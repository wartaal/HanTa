from collections import Counter
import math
from numpy import logaddexp
from operator import itemgetter
import pickle
import gzip
import ast
import pprint
import re
import os
import bisect
import random


EMPTY = 0
START = 1
END = 2
UNKNOWN = 3
END_UNKNOWN = -3

class HanoverTagger:
     
    # For each final state colelct what states possibly can lead to this final state
    # If we run the viterbi algorithm and we know the desired outcome, this speeds up the computation
    # Since this is computed fast and used only for optimizing speed, this is not stored in the model
    def reachable(self):
        connections = []
        for (_,c), followers in self.LP_trans.items():
            for f in followers:
                connections.append((c,f)) 
        self.reachability = {} 

        for c in self.int2tag.keys():
            if c >= 0:
                continue
            states = []
            for (a,b) in connections:
                if b == c and a not in states:
                    states.append(a)
            i = 0
            end = len(states)
            while i < end:
                d = states[i]
                for (a,b) in connections:
                    if b == d and a not in states:
                        states.append(a)
                        end+=1
                i+=1
            self.reachability[c] = states   
        
    #Find classes that are not analyzable, i.e. classes that can only be reached from the start and only can be followed by an end node
    def atomic(self):
        self.atomic_class = [c for c in self.reachability if len(self.reachability[c]) == 2 and -c in self.reachability[c] ] 

 
        
    def __init__(self, filename, model=None):
        self.re_qmark = re.compile(r'^(`|``|´|´´|\'|\'\')$')
        if filename:
            if os.path.exists(filename):
               file = gzip.GzipFile(filename, 'rb')
            else :
               dir =  os.path.split(__file__)[0]
               filename = os.path.join(dir,filename)
               if os.path.exists(filename):
                  file = gzip.GzipFile(filename, 'rb')
               else:
                  raise Exception('File not found: {}.',format(filename))
            model = pickle.load(file)
            file.close()
            self.strict = False
        else:
            self.strict = True
        self._debug = False
        if model:
            self.tag2int, self.int2tag, self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t, self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.nonstemtags, self.lemmasuffixtable,  self.capitalizedlemmata, self.cache = model
        self.tag2int['EMPTY'] = EMPTY
        self.tag2int['END'] = END
        self.tag2int['UNKNOWN'] = UNKNOWN
        self.tag2int['END_UNKNOWN'] = END_UNKNOWN
        self.int2tag[EMPTY] = 'EMPTY'
        self.int2tag[END] = 'END'
        self.int2tag[UNKNOWN] = 'UNKNOWN'
        self.int2tag[END_UNKNOWN] = 'END_UNKNOWN'
        self.reachable()
        self.atomic()


    #log prob of a morpheme given a tag: p(m|t)
    def  lp_m_t(self, m, t,wlen,strict):
  
        #if t in self.LP_m_t:
        if m in self.LP_m_t[t]:
            return self.LP_m_t[t][m]
        elif not strict and t in self.LP_s_t and t in self.LP_hapax_t:
            mlen = len(m)
            if (wlen < 4 or mlen > 2): 
                if mlen > 3 and m[-3:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-3:]]
                elif mlen > 2 and m[-2:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-2:]]
                elif mlen > 2 and m[-1:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-1:]]
                else:
                    lp_suf = self.LP_s_t[t]['']
                lp = self.Int_t + self.LP_hapax_t[t] + self.LP_len_t[t][min(mlen, 24)] + lp_suf
                if wlen == mlen: #CW 20220616 penalize analysis that assumes the whole word is one large unknown morpheme
                    lp -= 4.6
            else:
                lp = -math.inf
        else:
           lp = -math.inf

        return lp

    #log prob of a transition
    #All values are stored in the model but here we return all possible following states (and their probabilities)
    #and already filter whether it should be a final state or not
    def  lp_trans(self, state, final=False):
            
        if state in self.LP_trans:
            if final:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if tag < 0]
            else:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if tag > 0]
        else:
            following = []
        return following
    

    #Run the forward algorithm over the HMM
    #In fact this is not the forward algorithm but the Viterbi algorithm
    #This method is intended to give the probability for each part of speech. Thus if there
    #are two possibilities to arrive at a certain (final) state,we should sum up the probabilities, i.e. 
    #use the forward algorithm. However, in almost all such cases the less likely path is a spurious 
    #one and the results get better if we take the maximum as in the Viterbi algorithm.
    #Nevertheless, in the end probabilities for each POS are given, no paths.
    def analyze_forward(self, word): 
    
        lowerbound = -1e6
        table = []
        wlen = len(word)
        for i in range(wlen + 2):
            table.append({})
        table[0][(EMPTY, START)] = 0
        for i in range(wlen + 1):
            row = table[i]
            # Only continue with 3 top states
            if len(row) > 3:
                rowbound = sorted(row.values(), reverse=True)[3] - 1
            else:
                rowbound = lowerbound
            for state in row:
                lp = row[state]
                if lp < rowbound:
                    continue
                followup = self.lp_trans(state, final=False)

                for j in range(i + 1, wlen + 1):
                    for tag1, lpt in followup:
                        #lp1 = self.lp_m_t(word[i:j], tag1)
                        #if not self.strict and lp1 == -math.inf:
                        #    lp1 = self.guess_lp_m_t(word[i:j], tag1,wlen)
                        #lp1 += lp + lpt
                        lp1 = lp + lpt + self.lp_m_t(word[i:j], tag1, wlen,self.strict)
                        if lp1 > lowerbound:
                            newstate = (state[1], tag1)
                            if newstate not in table[j]:
                                table[j][newstate] = lp1
                            elif lp1 > table[j][newstate]:   
                                table[j][newstate] = lp1
                            #if newstate in table[j]:
                            #    table[j][newstate] = logaddexp(lp1, table[j][newstate])
                            #else:
                            #    table[j][newstate] = lp1

        for state in table[-2]:
            lp = table[-2][state]
            followup = self.lp_trans(state, final=True)
                    
            for tag1, lpt in followup:
                lp1 = lp + lpt
                if lp1 > lowerbound:
                    newstate = (state[1], tag1)
                    if newstate not in table[-1] or lp1 > table[-1][newstate]:
                        table[-1][newstate] = lp1
                    #if newstate in table[-1]:
                    #    table[-1][newstate] = logaddexp(lp1, table[-1][newstate])
                    #else:
                    #    table[-1][newstate] = lp1

        if self._debug:
            pprint.pprint(table)
        results = {}
        for state in table[-1]:
            lp = table[-1][state]
            if lp == -math.inf:
                continue
            #pos = self.int2tag[-state[1]]
            pos = -state[1]
            if pos in results:
                results[pos] = logaddexp(results[pos], lp) # TODO Maximum!!!
            else:
                results[pos] = lp
        result_list = list(results.items())
        result_list.sort(key=itemgetter(1), reverse=True)
        if len(result_list) == 0: #Occurs only in rare cases, eg analyzing the empty string as word, or unknownwords with strict == True
            result_list = [(UNKNOWN,0)]
        
        return result_list


    #The following method is similar to the previous one, but assumes that the POS is already known. 
    #Thus, we use only states that can lead to this POS, reducing the size of the tables.
    #Now a backpointer is maintained and the most likely path fis returned.
    #This method can be called from outside to analyze a word, or it is called to generate a lemma
    #after POS Tagging of the sentence. In the first case the forward algorithm has to be run first to determin the
    #POS if that was not specified in the call.
    #In a first run we try to find a path without using unknown morphemes. If that is noct succesfull 
    #(or if forced globally) a second run without this restriction is done
    
    def analyze_viterbi(self, word, targetpos):
        wlen = len(word)
        lowerbound = -1e6
        
        for localstrict in [True,False]: 
            table = []
            backpointer = []   

            for i in range(wlen + 2):
                table.append({})
                backpointer.append({})
                
            table[0][(EMPTY,START)] = 0
            
            reachable_t = self.reachability.get(targetpos,[])   

            for i in range(wlen + 1):
                row = table[i]
                # Only continue with 3 top states
                if len(row) > 3:
                    rowbound = sorted(row.values(), reverse=True)[3] - 1
                else:
                    rowbound = lowerbound
                for state in row:
                    lp = row[state]
                    if lp < rowbound:
                        continue
                    followup = [(t,p) for (t,p) in self.lp_trans(state, final=False) if t in reachable_t]
                    for j in range(i + 1, wlen + 1):
                        for tag1, lpt in followup:
                            #lp1 = self.lp_m_t(word[i:j], tag1)
                            #if not localstrict and lp1 == -math.inf:
                            #    lp1 = self.guess_lp_m_t(word[i:j], tag1,wlen)
                            #lp1 += lp + lpt
                            lp1 = lp + lpt + self.lp_m_t(word[i:j], tag1, wlen,localstrict)
                            if lp1 > lowerbound :
                                newstate = (state[1], tag1)
                                if newstate not in table[j] or lp1 > table[j][newstate]:
                                   table[j][newstate] = lp1
                                   backpointer[j][newstate] = (state, i)
  
            for state in table[-2]:
                lp = table[-2][state]
                for tag1, lpt in self.lp_trans(state, final=True):
                    if tag1 == targetpos: 
                       lp1 = lp + lpt
                       if lp1 > lowerbound:
                           newstate = (state[1], tag1)
                           if newstate not in table[-1] or lp1 > table[-1][newstate]  :
                               table[-1][newstate] = lp1
                               backpointer[-1][newstate] = (state, wlen)

            if len(table[-1]) > 0:
                break #Only if the last row is empty we need a second try without restrictions
        if self._debug:
            pprint.pprint(table)    
            
        pmax = -math.inf
        beststate = (EMPTY,EMPTY)
        for state in table[-1]:
            lp = table[-1][state]
            if lp > pmax: 
                pmax = lp
                beststate = state

        i = len(backpointer) - 1
        if beststate == (EMPTY,EMPTY):
            states = [((UNKNOWN, END_UNKNOWN), i), ((START, UNKNOWN), i-1)]
        else:       
            states = [(beststate, i)]
            state = beststate
            while i > 0:
                state, i = backpointer[i][state]
                states.append((state, i))
            states = states[:-1]
      
        return [(state[1], i) for (state, i) in states[::-1]]


    #Viterbi algorith now running over a sentence instead of over morphemes.
    #This is much simpler since we have boundaries between the words.
    def tag_sent_viterbi(self, sent, casesensitive = True):

        lowerbound = -1e6
        table = []
        backpointer = []
        
        for i in range(len(sent)):
            w = sent[i]

            if i == 0:
               cs = False
            elif casesensitive:
               cs = True
            wprobs = dict(self._tag_word(w,cutoff = 5, casesensitive=cs,conditional=True))
            if len(wprobs) == 1 and UNKNOWN in wprobs: #This should not occur but can result from wrong settings
               wprobs = {}
            row = {}
            backpointer.append({})
            if i == 0:
                prevrow = {(EMPTY, START): 0.0}
            else:
                prevrow = table[i - 1]
            # Only continue with 5 top states
            if len(prevrow) > 5:
                rowbound = sorted(prevrow.values(), reverse=True)[5] - 1
            else:
                rowbound = lowerbound
            for state in prevrow:
                lp0 = prevrow[state]
                if lp0 < rowbound:
                    continue
                lp_t = self.LP_trans_word[state] #.items()
                for c, lp_tc in lp_t.items():
                    if c not in wprobs and len(wprobs) > 0:
                        continue
                    if c == END: #2020-11-11 We are not in the last row, so adding state <END> makes no sense
                        continue
                    if len(wprobs) ==  0: #If the word is unknown anything goes
                        lpwc = 0
                    else:
                        lpwc = wprobs[c]
                    lp = lp0 + lp_tc + lpwc
                    #c2 = prev[1]
                    if lp > lowerbound:
                        newstate = (state[1], c)
                        if newstate not in row or lp > row[newstate]:
                            row[newstate] = lp
                            backpointer[i][newstate] = state

            table.append(row)
        
        # last row
        finalstate = (END,EMPTY)
        prevrow = table[-1]
        row = {}
        backpointer.append({})
        for state in prevrow:
            lp0 = prevrow[state]
            lp_t = dict(self.LP_trans_word[state])
            lp = lp0 + lp_t.get(END, -math.inf)
            if lp > row.get(finalstate, -math.inf):
                row[finalstate] = lp
                backpointer[-1][finalstate] = state
        table.append(row)

        if self._debug:
            pprint.pprint(table)

        tags = []
        state = finalstate
        for i in range(len(backpointer) - 1, 0, -1):
            state = backpointer[i][state]
            tags.append(state[1])

        return tags[::-1]
        
    def makelemma(self,stem_morphemes,pos):
        mainpostag = pos.split('(')[0]
        lemma = ''.join(stem_morphemes)
        suffix = ''
        lemmasuffices = self.lemmasuffixtable.get(mainpostag,[])
        if len(lemmasuffices) > 0:
           longest = max([len(e) for e in lemmasuffices])
           if len(lemma) + 1 < longest:
               longest = len(lemma)
           for i in range(longest+1,0,-1):
               ending = ('#'+lemma)[-i:]
               if ending in lemmasuffices:
                   suffix = lemmasuffices[ending]
               #elif len(suffix) > 0:  
                   break
            
        if self.tag2int.get(pos,0) in self.capitalizedlemmata:
            lemma = lemma[0].upper()+lemma[1:]
        lemma += suffix

        return lemma

    #german verb suffix belong to lemma in case a participle was turned into an adjective!
    #Tells whether a morpheme is part of the stem or not
    def relevant_morpheme(self, mtag, pos):
        if pos != None:
            mainpostag = pos.split('(')[0]
            return not mtag in self.nonstemtags.get(mainpostag,[])
        else:  
            return True
            #return mtag in set().union(*self.stemtags.values())

    def analyze(self, word, pos='EMPTY', taglevel=1, casesensitive=True):
       if pos == 'EMPTY' or pos not in self.tag2int:
           tags = self._tag_word(word,cutoff=0,casesensitive=casesensitive)   
           postag = tags[0][0]
       else:
           postag = self.tag2int[pos]
       return self._analyze(word,postag,taglevel)   
    
    def _analyze(self, word,  pos, taglevel=1):

        word = word.lower()
        postag = -pos
        
        if postag in self.atomic_class:
            wlen = len(word)
            morphemes = [(pos,wlen),(postag,wlen+1)]
        else:        
            morphemes = self.analyze_viterbi(word, postag)
        
        postag = -morphemes[-1][0]
        str_postag  =  self.int2tag[postag] 

        if taglevel == 0:
            return str_postag
   
        start = 0
        morphlist = []
        for (tag, end) in morphemes:
            if tag > 0:
                morpheme = word[start:end]
                morphlist.append((morpheme, tag))
            start = end
               
        if taglevel == 2:
            roots = []
            for (m,t) in morphlist: 
                if t in self.stemdict:
                    m = self.stemdict[t].get(m,m)
                roots.append(m)
            lemma = '+'.join(roots)  
            return lemma, str_postag
          
        lemmacomponents = [(morpheme,tag) for (morpheme,tag) in morphlist if self.relevant_morpheme(tag,str_postag)]
        if len(lemmacomponents) == 0 : ## Should never occur...
            lemmacomponents = [(morpheme,tag) for (morpheme,tag) in morphlist if self.relevant_morpheme(tag,None)]
        if len(lemmacomponents) == 0 :
            lemmacomponents = morphlist
         
         
        lastmorpheme = lemmacomponents[-1][0]
        lasttag = lemmacomponents[-1][1]
        if lasttag in self.stemdict:
            lastmorpheme = self.stemdict[lasttag].get(lastmorpheme, lastmorpheme)
        lemmamorphemes = [m for m,_ in lemmacomponents[:-1]]+[lastmorpheme]
        
      
        if taglevel == 1:
            lemma = self.makelemma(lemmamorphemes,str_postag)  
            return lemma, str_postag
                     
        #taglevel 3
        morphlist = [(m,self.int2tag[t]) for m,t in morphlist]
        stem = ''.join(lemmamorphemes)
        return stem, morphlist, str_postag


    def  normalize(self, w):
        #if re.match(r'^(`|``|´|´´|\'|\'\')$',w):
        if self.re_qmark.match(w):
           return '"'
        else:
           return w.lower()

    def tag_word(self, word, cutoff=5, casesensitive = True):
        tags = self._tag_word(word, cutoff, casesensitive)   
        return [(self.int2tag[t],p) for (t,p) in tags]
         
      
    def _tag_word(self, word, cutoff=5, casesensitive = True, conditional = False):
            
        if casesensitive and word[0].isupper():
            upcase = True
        else:
            upcase = False
        word = self.normalize(word)
        if word in self.cache:
            p_tags = self.cache[word]
            cached = True
        else:
            p_tags = self.analyze_forward(word)
            cached = False
         
        p_w_tags = []
        for tag,p in p_tags:
            if tag != UNKNOWN:
               if casesensitive:
                  p += self.LP_case_t[tag][upcase]
               if conditional:
                  p -= self.LP_wtag[tag] 
            p_w_tags.append((tag,p))
            
        p_w_tags.sort(key=itemgetter(1), reverse=True)

        if not cached and len(p_w_tags) > 0:
           if cutoff == 0:
               p_w_tags = [p_w_tags[0]]
           else:
               limit = p_w_tags[0][1] - cutoff
               p_w_tags = [(tag,p) for (tag,p) in  p_w_tags if p >= limit]
           

        return p_w_tags

    def tag_sent(self, sent, taglevel=1, casesensitive = True):
        if len(sent) == 0:
            return []
        tags = self.tag_sent_viterbi(sent,casesensitive)
        if taglevel == 0:
            return [self.int2tag[t] for t in tags]
        elif taglevel == 1:
            return [(sent[i], self._analyze(sent[i], tags[i], taglevel=1)[0], self.int2tag[tags[i]]) for i in range(len(sent))]
        elif taglevel == 2:
            return [(sent[i], self._analyze(sent[i], tags[i], taglevel=2)[0], self.int2tag[tags[i]]) for i in range(len(sent))]
        else:
            return [(sent[i], *self._analyze(sent[i], tags[i], taglevel=3)) for i in range(len(sent))]
            
            
    def list_postags(self):
        examples = {}
        for w in self.cache:
            for pos,prob in self.cache[w]:
               posex = examples.get(pos,[])
               posex.append((w,prob))
               examples[pos] = posex
               
        for ptag in sorted([self.int2tag[-tag] for tag in  self.int2tag if tag < 0]):
            print(ptag,end='\t')
            pos = self.tag2int[ptag]
            posex = examples.get(pos,[])
            m = min(200,len(posex))
            words = [w for w,p in sorted(posex,key=lambda x:x[1],reverse = True)][:m]
            m = min(10,len(posex))
            words = random.sample(words,m)
            print(*words,sep=", ")
    
    
    def list_mtags(self):
        mtags = sorted([self.int2tag[tag] for tag in  self.int2tag if tag > 0 and -tag not in self.int2tag ])
        longest = 3 + max([len(m) for m in mtags])
        for mtag in mtags:
            tag = self.tag2int[mtag]
            if tag not in self.LP_m_t:
                continue
            print(mtag,end=(longest-len(mtag)) * ' ')
            mex = [m for m,p in self.LP_m_t[tag].most_common()]
            red = min(200,len(mex))
            mex = mex[:red]
            red = min(10,len(mex))
            mex = random.sample(mex,red)
            print(*mex,sep=', ')


class TrainHanoverTagger:

    def __init__(self):
        self.morphdata = []
        self.sentdata = []
        self.stemdict = {}
        self.tag2int = {}
        self.int2tag = {}
        self.nonstemtags = {}
        self.lemmasuffixtable = {}
        self.capitalizedlemmata = set()
        self.word_tags = set()
        self.tagnr = 10

    def normalize_w(self,w):
        if re.match(r'^(`|``|´|´´|\'|\'\')$',w):
           return '"'
        else:
           return w
           
    def normalize_m(self,morphemes): 
        result = []
        for (m,s_tag) in morphemes:
            tag = self.gettagnr(s_tag)
            result.append((self.normalize_w(m),tag))
        return result
         
    def gettagnr(self, tagstr):
        if tagstr in self.tag2int:
            return self.tag2int[tagstr]
        if tagstr.startswith('END_'):
            maintag = tagstr[4:]
            if maintag in self.tag2int:
                nr = -self.tag2int[maintag]
                self.int2tag[nr] = tagstr
                self.tag2int[tagstr] = nr
            else:
                self.tagnr += 1
                self.tag2int[maintag] = self.tagnr 
                self.int2tag[self.tagnr] = maintag
                nr = -self.tagnr 
                self.tag2int[tagstr] = nr
                self.int2tag[nr] = tagstr
            return nr
        self.tagnr += 1
        self.tag2int[tagstr] = self.tagnr
        self.int2tag[self.tagnr] = tagstr
        return self.tagnr
    
    #collect tags of morphemes that are part of the stem of a word
    def relevant_tags(self,stem,morphemes,stemsub):
       relevant = []
       irrelevant  = []
       
       stem = stem.strip().lower()
       
       morphemes_sub = []
       for m,t in morphemes[::-1]:   
           if len(m) == 0:
               continue
           if len(stemsub) == 3 and self.gettagnr(stemsub[0]) == t and stemsub[1] == m and stem.endswith(stemsub[2]): 
               m = stemsub[2]
           morphemes_sub = [(m,t)]+morphemes_sub

       morphemes = morphemes_sub
       
       matches = []
       for i in range(len(stem)+1):
           matches.append([]) 
           for i_m in range(len(morphemes)):
               m,t = morphemes[i_m]
               if len(m) > i:
                   continue
               b = i - len(m)
               if m == stem[b:i]:
                   if b == 0:
                       matches[i].append([i_m])
                   elif len(matches[b]) > 0:
                       for match in matches[b]:
                           prev = match[-1]
                           if prev < i_m:
                               matches[i].append(match+[i_m])
         
       end = len(stem)
       if len(matches[end]) > 0:
           match = matches[end][0]
           relevant = [morphemes[m][1] for m in match]

       irrelevant = [tag  for m,tag in morphemes if tag not in relevant]
       
       return relevant,irrelevant
       
    def collectlemmata(self,lemma,stem,tag,lemmasuffix):
       postag = tag.split('(')[0]     
               
       if lemma.lower().startswith(stem):
          s = lemma[len(stem):]
          suf_t = lemmasuffix.get(postag,{})
          words = suf_t.get(s,set())
          words.update(['#'+stem])
          suf_t[s] = words
          lemmasuffix[postag] = suf_t


    #Goal: From a dictionary of stems and suffixes to be added to each word to create a lemma
    #make a dictionary of endings of words and suffixes to be added.  
    #Here we have a list of words using a certain ending. We try to rduce the lists by removing the 
    #beginning of the words till conflicts arise    
    def reducelemmasuffix(self,lemmasuffix):
        
        for pos in lemmasuffix:
            for sf, wordlist in lemmasuffix[pos].items():
                if len(sf) == 0:
                   continue
                ws = [w for w in wordlist]
                for w in ws:
                    unique = True
                    for i in range(1,1+len(w)):
                        end = w[i:]
                        unique = True
                        for wl in lemmasuffix[pos].values():
                            if wl == wordlist:
                                continue
                            for v in wl:
                                if v.endswith(end):
                                    wordlist.remove(w)
                                    suffix = w[i-1:]
                                    wordlist.update([suffix])
                                    unique = False
                                    break
                            if not unique:
                                break
                        if not unique:      
                            break
                    if unique:
                        wordlist.remove(w)
                        wordlist.update([''])  
            
        return lemmasuffix
                
    def suffixtable(self,lemmasuffix):
       suftable = {}
       for POS in lemmasuffix:
           suffixes = {}
           for suf in lemmasuffix[POS]:
               if len(suf) > 0:
                  for ending in lemmasuffix[POS][suf]:
                     suffixes[ending] = suf
           suftable[POS] = suffixes
       return suftable

    def load(self, fin):
        sent = []
        lemmasuff = {}
        lastsentnr = 1
        upcasestat = {}
        cnt_lex_morph = {}
        
        for line in fin:
            columns = line.split('\t') 
            if len(columns) == 7:
                (sentnr, word, lemma, stem, s_tag, morphemes, stemsub) = columns # 2021-03-01 added stem
                stemsub = ast.literal_eval(stemsub)
            else:
               (sentnr, word, lemma, stem, s_tag, morphemes) = columns
               stemsub = ()
            
            word = self.normalize_w(word)
            tag = self.gettagnr(s_tag)
            self.word_tags.update([tag])
            morphemes = ast.literal_eval(morphemes)
            morphemes.append(('','END_'+s_tag))
            morphemes = self.normalize_m(morphemes)
            if len(morphemes) == 0: #2022-09-18 Should not happen...
                continue
            
            
            casecnt = upcasestat.get(tag,Counter())
            casecnt.update([lemma[0].isupper()])
            upcasestat[tag] = casecnt

            self.morphdata.append(morphemes)
            self.collectlemmata(lemma,stem,s_tag,lemmasuff)
            postag = s_tag.split('(')[0]            
            rel,irrel = self.relevant_tags(stem,morphemes,stemsub)
            cnt_lex_pos = cnt_lex_morph.get(postag,(Counter(),Counter()))
            cnt_lex_pos[0].update(rel)
            cnt_lex_pos[1].update(irrel)
            cnt_lex_morph[postag] = cnt_lex_pos
            
            
            if int(sentnr) >= 0:
                if sentnr != lastsentnr:
                    self.sentdata.append(sent)
                    sent = []
                    lastsentnr = sentnr   
                sent.append((word,tag))
            if len(stemsub) == 3:
                s_alttag, altstem, stem = stemsub #ast.literal_eval(stemsub)
                alttag = self.gettagnr(s_alttag)
                sd_tag = self.stemdict.get(alttag, {})
                sd_tag[altstem] = stem
                self.stemdict[alttag] = sd_tag

        for tag in upcasestat:
            if upcasestat[tag][True] > upcasestat[tag][False]:
                self.capitalizedlemmata.update([tag])
        lemmasuff = self.reducelemmasuffix(lemmasuff)
        self.lemmasuffixtable = self.suffixtable(lemmasuff)
        for p in cnt_lex_morph: #change 2023.02.24 Store tags to be removed,  not the ones to be kept (make keeping a morpheme the default)
            irrel_p = []
            (cnt_r, cnt_i) = cnt_lex_morph[p]
            #print(p,cnt_r, cnt_i)
            for t in cnt_i:
                if cnt_i[t] > cnt_r[t]:
                    irrel_p.append(t)
            self.nonstemtags[p] = irrel_p
            

    def collect_tag_freqs(self):
        p_t_m = {}
        n_m = {}
        for word in self.morphdata:
            for (m, t) in word:
                p_t = p_t_m.get(m, Counter())
                p_t.update([t])
                p_t_m[m] = p_t
        for m in p_t_m:
            p_t = p_t_m[m]
            n_m[m] = sum(p_t.values())
            for t in p_t:
                p_t[t] = math.log(p_t[t] / n_m[m])

        return n_m, p_t_m

    def endswith_one_of(self, w, suffixes):
        for s in suffixes:
            if w.endswith(s):
                return True
        return False

    def suffixprobs(self):
        exclude = []
        sufcount = Counter()
        n_suf_t = {}
        for len_s in range(3, -1, -1):
            for morphemes in self.morphdata:
                for morph, t in morphemes:
                    if t in self.LP_hapax_t and self.N_m[morph] < 20 and len(morph) > len_s and not self.endswith_one_of(morph, exclude):
                        if len_s > 0:
                            suf = morph[-len_s:]
                        else:
                            suf = ''
                        sufcount.update([suf])
                        n_suf = n_suf_t.get(t, Counter())
                        n_suf.update([suf])
                        n_suf_t[t] = n_suf
            exclude = [suf for suf in sufcount if sufcount[suf] > 50]

        p_suf_t = {}

        allsufs = [suf for suf in sufcount if sufcount[suf] > 50]
        for t in n_suf_t:
            p_suf = {}
            n_suf = n_suf_t[t]
            sum_t = sum([n_suf[s] for s in allsufs])
            for suf in allsufs:
                if n_suf[suf] > 0:
                    p_suf[suf] = math.log(n_suf[suf] / sum_t)
                else:
                    p_suf[suf] = -math.inf
            p_suf_t[t] = p_suf
        return p_suf_t

    def smooth(self, data):
        sdata = data[:2]
        for i in range(2, len(data) - 2):
            sdata.append(data[i - 2] + 0.2 * data[i - 1] + 0.4 * data[i] + 0.2 * data[i + 1] + 0.1 * data[i + 2])
        sdata.extend(data[-2:])
        return sdata

    def lenprobs(self):
        p_len_t = {}
        for morphemes in self.morphdata:
            for m, t in morphemes:
                t_name = self.int2tag[t]
                if self.N_m[m] < 50 and not (len(t_name) > 4 and t_name[-4:] == '_IRR'):
                    l = min(len(m), 25)
                    n_l = p_len_t.get(t, Counter())
                    n_l.update([l])
                    p_len_t[t] = n_l
        for t in p_len_t:
            p_l = p_len_t[t]
            p_l = [p_l.get(l, 0) for l in range(0, 26)]
            p_l = self.smooth(p_l)
            total = sum(p_l)
            for l in range(len(p_l)):
                if p_l[l] > 0:
                    p_l[l] = math.log(p_l[l] / total)
                else:
                    p_l[l] = -math.inf
            p_len_t[t] = p_l
        return p_len_t

    def find_openclass(self):
        N_mp = Counter([m for morphemes in self.morphdata for m in morphemes])
        N_t_hapax = Counter([t for (m,t) in N_mp  if N_mp[(m,t)] == 1])
        N_hapax = sum(N_t_hapax.values())
        P_t_hapax = Counter({t:N_t_hapax[t]/N_hapax for t in N_t_hapax })
        open_class = [t for t in P_t_hapax if P_t_hapax[t] > 0.005 and '_VAR' not in self.int2tag[t]]
        return  open_class

    def hapaxprobs(self):
        count = {}
        for morphemes in self.morphdata:
            for m, t in morphemes:
                count_t = count.get(t, Counter())
                count_t.update([m])
                count[t] = count_t
        p_hapax_t = {}
        #openclass = self.tag2int[t] for t in ['NN','NE','ADJ','ADV','CARD','FM','VV']]
        openclass = self.find_openclass()
        for t in openclass: #count:
            dist = Counter(count[t].values())
            if dist[1] > 0:
                p_hapax_t[t] = math.log(dist[1] / self.N_t[t])
        return p_hapax_t

    def transprob(self):
        p_trans = {}
        for word in self.morphdata:
            posseq = [START] + [t for m, t in word]
            p = posseq[1]
            p_1 = posseq[0]
            prev = (EMPTY, p_1)
            n_prev = p_trans.get(prev, {})
            n_prev[p] = 1 + n_prev.get(p, 0)
            p_trans[prev] = n_prev
            for i in range(2, len(posseq)):
                p = posseq[i]
                p_1 = posseq[i - 1]
                p_2 = posseq[i - 2]
                prev = (p_2, p_1)
                n_prev = p_trans.get(prev, {})
                n_prev[p] = 1 + n_prev.get(p, 0)
                p_trans[prev] = n_prev
        for prev in p_trans:
            total = sum(p_trans[prev].values())
            for p in p_trans[prev]:
                p_trans[prev][p] = round(math.log(p_trans[prev][p] / total),5)
        return p_trans

    def morphprobs(self):
        lp_m_t = {}
        for t in self.N_t:
            lp_m_t[t] = Counter()

        for word in self.morphdata:
            for (m, t) in word:
                lp_m_t[t].update([m])
        for t in lp_m_t:
            lp_m = lp_m_t[t]
            total = sum(lp_m.values())
            for m in lp_m:
                lp_m[m] = round(math.log(lp_m[m] / total), 5)

        return lp_m_t
  
    def caseprobs(self):
        lp_case_t = {}
        for sent in self.sentdata:
            for (word,tag) in sent[1:]:
                casecount = lp_case_t.get(tag,Counter())
                casecount.update([word[0].isupper()])
                lp_case_t[tag] = casecount
        for tag in self.word_tags:  # some tags might be present only in the additional data              
           if tag in lp_case_t: 
               total = 2 + lp_case_t[tag][True] + lp_case_t[tag][False] 
               lp_case_t[tag][True]  = math.log((1+lp_case_t[tag][True])/total)
               lp_case_t[tag][False]  = math.log((1+lp_case_t[tag][False])/total)
           else:
               lp_case_t[tag] = {True:math.log(0.5),False:math.log(0.5)}
            
        return lp_case_t
    

    def intercept(self):
        min_observed = math.log(1 / max(self.N_t.values()))  ##Problem. eg. verbs always need a suffix....
        max_unknown = -math.inf
        for t in self.N_t:
            if t in self.LP_hapax_t and t in self.LP_len_t and t in self.LP_s_t:
                unknown = self.LP_hapax_t[t] + max(self.LP_len_t[t]) + max(self.LP_s_t[t].values())
                if unknown > max_unknown:
                    max_unknown = unknown
        #return -2.3 + min(0, min_observed - max_unknown)
        #return -4.6 + min(0, min_observed - max_unknown)
        return -6.9 + min(0, min_observed - max_unknown)

        

    def tagprobs_word(self):
        lp_t = {}
        p_t = Counter([pos for sent in self.sentdata for (word,pos) in sent])
        additional = [pos for pos in self.word_tags if pos not in p_t]
        p_t.update(additional)
        total = sum(p_t.values())
        for p in p_t:
            lp_t[p] = math.log(p_t[p] / total)
            
        p_t[END] = len(self.sentdata)
        total += p_t[END]
        for p in p_t:
            p_t[p] = p_t[p] / total
            
        return lp_t, p_t

    def transprob_word_2(self):
        p_trans = {}
        for sent in self.sentdata:
            posseq = [START] + [tag for (word,tag) in sent] + [END]
            for i in range(len(posseq) - 1):
                p = posseq[i]
                q = posseq[i + 1]
                tc_p = p_trans.get(p, {})
                tc_p[q] = 1 + tc_p.get(q, 0)
                p_trans[p] = tc_p
        for p in p_trans:
            total = sum(p_trans[p].values())
            for q in p_trans[p]:
                p_trans[p][q] = p_trans[p][q] / total
        return p_trans

    def transprob_word_3(self):
        p_trans = {}
        for sent in self.sentdata:
            posseq = [START] + [tag for (word,tag) in sent] + [END]
            p = posseq[1]
            p_1 = posseq[0]
            prev = (EMPTY, p_1)
            n_prev = p_trans.get(prev, {})
            n_prev[p] = 1 + n_prev.get(p, 0)
            p_trans[prev] = n_prev
            for i in range(2, len(posseq)):
                p = posseq[i]
                p_1 = posseq[i - 1]
                p_2 = posseq[i - 2]
                prev = (p_2, p_1)
                n_prev = p_trans.get(prev, {})
                n_prev[p] = 1 + n_prev.get(p, 0)
                p_trans[prev] = n_prev

        for prev in p_trans:
            total = sum(p_trans[prev].values())
            for p in p_trans[prev]:
                p_trans[prev][p] = p_trans[prev][p] / total
                
        return p_trans  

    def mixture(self,weights):
        p_trans = {}
        for p in list(self.P_wtag.keys()) + [EMPTY, START]:
            if p == '<END>':
                continue
            for q in list(self.P_wtag.keys()) + [START]:
                if q == END:
                    continue 
                if q == START and p != EMPTY:
                    continue
                pq = (p, q)
                t_pq = {}
                for r in list(self.P_wtag.keys()):
                    t_pq[r] = round(math.log(
                        weights[2] * self.P_trans_word_3.get(pq, {}).get(r, 0) + weights[1] * self.P_trans_word_2.get(q, {}).get(r, 0) + weights[0] * self.P_wtag[r]), 4)

                p_trans[pq] = t_pq

        return p_trans 
    

    def precompute(self, tagger, nr):
        words = Counter()
        wordclasses = {}
        for sent in self.sentdata:
           for (w,c) in sent:
               words.update([w.lower()])
               wclset = wordclasses.get(w.lower(), set())
               wclset.add(c)
               wordclasses[w.lower()] = wclset
        
        cache = {}
        n = 0
        for w, f in words.most_common(nr):
            computed = tagger.analyze_forward(w) 
            filtered = []
            for tag, p in computed:
                if tag in wordclasses[w]:
                    filtered.append((tag, round(p, 2)))
            if len(filtered) > 0:
                cache[w] = filtered
        for w, f in words.most_common(2 * nr)[nr:]:
            computed = tagger.analyze_forward(w) 
            if len(computed) < 5:
                continue
            filtered = []
            for tag, p in computed:
                if tag in wordclasses[w]:
                    filtered.append((tag, round(p, 2)))
            if len(filtered) > 0:
                cache[w] = filtered
        return cache
    
    
    #TODO Include unobserved possibilities as well!
    # Die Laufenden, e.g. NNA possible but only ADJ observed
    def precompute_observed(self,tagger):
        words = Counter()
        lp_w_c = {}
        lowest = {}
        for c in self.LP_wtag:
           lp_w_c[c] = Counter()
           
        for sent in self.sentdata:
           for (w,c) in sent:
               lp_w_c[c].update([w.lower()])
               words.update([w.lower()])
        for c in lp_w_c:
           lp_w = lp_w_c[c]
           total = sum(lp_w.values())
           if total == 0: # can happen if a category/tag is only found in additional data and not in the sentence data
               continue
           lowest[c] = math.log(2/total)
           for w in lp_w:
               lp_w[w] = math.log(lp_w[w]/total)
           lp_w_c[c] = dict(lp_w)
        cache = {}
        n = 0
        for w, f in words.most_common(): #(nr):
            if f < 3:
               break
            observed = []
            if f < 10:
               computed = dict(tagger.analyze_forward(w))
            for tag in lp_w_c:
               if w in lp_w_c[tag]:
                  p = lp_w_c[tag][w] + self.LP_wtag[tag] 
                  observed.append((tag,round(p, 4)))
               elif f < 10 and tag in computed:
                  p = min(lowest[tag],computed[tag]) 
                  #p = computed[tag] 
                  #if p > lowest[tag]:
                     #print(w,tag,round(p, 4),sep='\t')
                  if p > -20: #Quite arbitrary
                     observed.append((tag,round(p, 4)))
                  #print(w,tag,round(p, 4),sep='\t')
            if len(observed) > 0:
               observed.sort(key=itemgetter(1), reverse=True)
               cache[w] = observed
        return cache
               

    def train_morph_model(self):
        self.N_t = Counter([t for morphemes in self.morphdata for (morph, t) in morphemes])
        self.N_m, self.LP_t_m = self.collect_tag_freqs() #TODO  self.LP_t_m is never used
        self.LP_hapax_t = self.hapaxprobs()
        self.LP_s_t = self.suffixprobs()
        self.LP_len_t = self.lenprobs()
        self.Int_t = self.intercept()
        self.LP_trans = self.transprob()
        self.LP_m_t = self.morphprobs()
        self.LP_case_t = self.caseprobs()

    def train_sent_model(self):
        self.LP_wtag, self.P_wtag = self.tagprobs_word()
        self.P_trans_word_2 = self.transprob_word_2()
        self.P_trans_word_3 = self.transprob_word_3()
        self.LP_trans_word = self.mixture([0.01,0.04,0.95])

        
        
    def train_model(self,observed_values=True):
        self.train_morph_model()
        self.train_sent_model()
        model = (
        self.tag2int, self.int2tag, self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.nonstemtags, self.lemmasuffixtable, self.capitalizedlemmata,{})
        tagger = HanoverTagger(None, model)
        if observed_values:
            self.cache = self.precompute_observed(tagger)
        else:
            self.cache = self.precompute(tagger,2000)

    def write_model(self, filename):
        model = (
        self.tag2int, self.int2tag, self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.nonstemtags, self.lemmasuffixtable, self.capitalizedlemmata, self.cache)

        file = gzip.GzipFile(filename, 'wb')
        pickle.dump(model, file)
        file.close()
