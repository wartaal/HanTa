from collections import Counter, namedtuple
import math
from numpy import logaddexp
from operator import itemgetter
import pickle
import gzip
import ast
import pprint
import re
import os

#State = namedtuple("State", ["p2", "p1"])

cdef class HanoverTagger:
    cdef:
        bint strict
        bint _debug
        dict LP_s_t
        dict LP_len_t
        double Int_t
        LP_hapax_t
        LP_trans
        dict LP_m_t
        dict stemdict
        dict LP_trans_word
        dict LP_wtag
        dict LP_case_t
        dict cache
        object re_qmark
        
        
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
            self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t, self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.cache = model

    cdef inline lp_m_t(self, str m, char *t,int wlen):
        cdef: 
            double lp
            int mlen
            
        lp = -math.inf
        if t in self.LP_m_t and m in self.LP_m_t[t]:
            lp = self.LP_m_t[t][m]
        #elif not self.strict and m not in self.N_m and t in self.LP_len_t and t in self.LP_s_t and t in self.LP_hapax_t:
        else:
            mlen = len(m)
            if not self.strict and t in self.LP_len_t and t in self.LP_s_t and t in self.LP_hapax_t and (wlen < 4 or mlen > 2): 
                if mlen > 3 and m[-3:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-3:]]
                elif mlen > 2 and m[-2:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-2:]]
                elif mlen > 2 and m[-1:] in self.LP_s_t[t]:
                    lp_suf = self.LP_s_t[t][m[-1:]]
                else:
                    lp_suf = self.LP_s_t[t]['']
                lp = self.Int_t + self.LP_hapax_t[t] + self.LP_len_t[t][min(mlen, 24)] + lp_suf

        return lp

    cdef inline lp_trans(self, (char *,char *) state, bint final=False):
        cdef:
            list following
            
        if state in self.LP_trans:
            if final:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if tag[:4] == b'END_']
            else:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if not tag[:4] == b'END_']
        else:
            following = []
        return following

    cdef analyze_forward(self, str word): 
        cdef:
            double lowerbound
            double rowbound
            double lp1
            double lp
            double lpt
            list table
            dict row
            int i
            int wlen
            double pmax
            (char*,char*) state
            (char*,char*) beststate
            dict results
            list result_list
    
        lowerbound = -1e6
        table = []
        wlen = len(word)
        for i in range(wlen + 2):
            table.append({})
        table[0][(b'', b'START')] = 0
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
                for j in range(i + 1, len(word) + 1):
                    #morpheme = word[i:j]
                    for tag1, lpt in followup:
                        #lp1 = lp + lpt + self.lp_m_t(morpheme, tag1,len(word))
                        lp1 = lp + lpt + self.lp_m_t(word[i:j], tag1,len(word))
                        if lp1 > lowerbound:
                            tag2 = state[1]
                            newstate = (tag2, tag1)
                            if newstate not in table[j] or lp1 > table[j][newstate]:
                                 table[j][newstate] = lp1
                            #if newstate in table[j]:
                            #    table[j][newstate] = logaddexp(lp1, table[j][newstate])
                            #else:
                            #    table[j][newstate] = lp1

        for state in table[-2]:
            lp = table[-2][state]
            for tag1, lpt in self.lp_trans(state, final=True):
                lp1 = lp + lpt
                if lp1 > lowerbound:
                    tag2 = state[1]
                    newstate = (tag2, tag1)
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
            pos = state[1][4:]
            if pos in results:
                results[pos] = logaddexp(results[pos], lp) # TODO Maximum!!!
            else:
                results[pos] = lp
        result_list = list(results.items())
        #result_list.sort(key=lambda x: x[1], reverse=True)
        result_list.sort(key=itemgetter(1), reverse=True)
        if len(result_list) == 0: #Occurs only in very very rare and strage cases, eg analyzing the empty string as word, or unknownwords with strict == True; Maybe better throw an exception...
            result_list = [(b'UNKNOWN',0)]
        
        return result_list

    cdef analyze_viterbi(self, str word, char *pos):
    
        cdef:
            double lowerbound
            double rowbound
            double lp1
            double lp
            double lpt
            list table
            dict row
            list backpointer
            int i
            int j
            double pmax
            #char *morpheme
            (char*,char*) state
            (char*,char*) beststate
            #char *tag1
            #char *tag2
        
        lowerbound = -1e6
        table = []
        backpointer = []
        

        for i in range(len(word) + 2):
            table.append({})
            backpointer.append({})
        table[0][(b'',b'START')] = 0
        for i in range(len(word) + 1):
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
                for j in range(i + 1, len(word) + 1):
                    #morpheme = word[i:j]
                    for tag1, lpt in followup:
                        #lp1 = lp + lpt + self.lp_m_t(morpheme, tag1, len(word))
                        lp1 = lp + lpt + self.lp_m_t(word[i:j], tag1, len(word))
                        tag2 = state[1]
                        newstate = (tag2, tag1)
                        if lp1 > table[j].get(newstate, lowerbound):
                            table[j][newstate] = lp1
                            backpointer[j][newstate] = (state, i)

        for state in table[-2]:
            lp = table[-2][state]
            for tag1, lpt in self.lp_trans(state, final=True):
                lp1 = lp + lpt
                tag2 = state[1]
                newstate = (tag2, tag1)
                if lp1 > table[-1].get(newstate, lowerbound):
                    table[-1][newstate] = lp1
                    backpointer[-1][newstate] = (state, len(word))

        #if self._debug:
        #pprint.pprint(table)
            
        pmax = -math.inf
        beststate = (b'',b'')
        for state in table[-1]:
            lp = table[-1][state]
            if lp > pmax and (pos == b'' or pos == state[1]):
                pmax = lp
                beststate = state
        #if pos not in the table...        
        if pmax == -math.inf:
            for state in table[-1]:
               lp = table[-1][state]
               if lp > pmax:
                  pmax = lp
                  beststate = state
        

        i = len(backpointer) - 1
        if beststate == (b'',b''):
            states = [((b'UNKNOWN', b'END_UNKNOWN'), i), ((b'START', b'UNKNOWN'), i-1)]
        else:       
            states = [(beststate, i)]
            state = beststate
            while i > 0:
                state, i = backpointer[i][state]
                states.append((state, i))
            states = states[:-1]
      
        return [(state[1], i) for (state, i) in states[::-1]]

    cdef tag_sent_viterbi(self, list sent, bint casesensitive = True):
        cdef:
            double lowerbound
            double rowbound
            double lp
            double lp0
            double lp_tc
            double lpwc
            list table
            dict row
            dict prevrow
            list backpointer
            bint cs
            int i
            dict wprobs
            dict lp_t
            #char *c
            #char *c2
            list tags

        
        
        lowerbound = -1e6
        table = []
        backpointer = []

        for i in range(len(sent)):
            w = sent[i]

            if i == 0:
               cs = False
            elif casesensitive:
               cs = True
            wprobs = dict(self.tag_word(w,cutoff = 5, casesensitive=cs,conditional=True))
            if len(wprobs) == 1 and b'UNKNOWN' in wprobs: #This should not occur but can result from erong settings
               wprobs = {}
            row = {}
            backpointer.append({})
            if i == 0:
                prevrow = {(b'', b'<Start>'): 0.0}
            else:
                prevrow = table[i - 1]
            # Only continue with 5 top states
            if len(prevrow) > 5:
                rowbound = sorted(prevrow.values(), reverse=True)[5] - 1
            else:
                rowbound = lowerbound
            for prev in prevrow:
                lp0 = prevrow[prev]
                if lp0 < rowbound:
                    continue
                lp_t = self.LP_trans_word[prev] #.items()
                for c, lp_tc in lp_t.items():
                    if c not in wprobs and len(wprobs) > 0:
                        continue
                    if c == b'<END>': #2020-11-11 We are not in the last row, so adding state <END> makes no sense
                        continue
                    if len(wprobs) ==  0: #If the word is unknown anything goes
                        lpwc = 0
                    else:
                        lpwc = wprobs[c]
                    lp = lp0 + lp_tc + lpwc
                    c2 = prev[1]
                    newstate = (c2, c)
                    if lp > row.get(newstate, lowerbound):
                        row[newstate] = lp
                        backpointer[i][newstate] = prev
            table.append(row)
        # last row
        prevrow = table[-1]
        row = {}
        backpointer.append({})
        for prev in prevrow:
            lp0 = prevrow[prev]
            lp_t = dict(self.LP_trans_word[prev])
            lp = lp0 + lp_t.get(b'<END>', -math.inf)
            if lp > row.get(b'<END>', -math.inf):
                row[b'<END>'] = lp
                backpointer[-1][b'<END>'] = prev
        table.append(row)

        if self._debug:
            pprint.pprint(table)

        tags = []
        state = b'<END>'
        for i in range(len(backpointer) - 1, 0, -1):
            state = backpointer[i][state]
            tags.append(state[1])

        return tags[::-1]
        
    cdef makelemma(self,list stem_morphemes,char *pos):
        lemma = ''.join(stem_morphemes)
        if pos[0] == b'V'[0]:
           #if lemma[-1] in 'aeo':
           #     lemma = lemma + 'n'
           #el
           ## Betonung muss berücksichtigt werden: beschwerEn !
           if lemma.endswith('tu') or lemma.endswith('sei'):
                lemma = lemma + 'n'
           elif (lemma.endswith('el') or lemma.endswith('er')) and lemma[-3] not in 'ui':
                lemma = lemma + 'n'
           else:
                lemma = lemma + 'en'
        elif pos == b'NN' or pos == b'NE':
           lemma = lemma[0].upper() + lemma[1:]
        elif pos[0] == b'$'[0]:
           lemma = '--'
        return lemma
    
    cdef relevant_morpheme(self,char *mtag,char *pos):
        #verb suffixs belong to lemma in case a participle was turned into an adjective!
        if pos == b'ADJA' or pos == b'ADJD':
            if mtag not in [b'SUF_ADJ',b'ADJ_COMP',b'ADJ_SUP']:
               return True
            else:
               return False
        elif pos == b'PTKZU':
            return True
        else:
            if not mtag[:3] == b'SUF' and  mtag not in [b'PREF_PP',b'PTKZU']:
               return True
            else:
               return False
    

    cpdef analyze(self, word, pos='', taglevel=1):
        
        word = word.lower()
        if pos:
            if type(pos) == str: 
               pos = pos.encode('utf8')
            pos = b'END_' + pos
        else:
            pos = b''
        morphemes = self.analyze_viterbi(word, pos)
        pos = morphemes[-1][0][4:]

        if taglevel == 0:
            return pos
        elif taglevel == 1 or taglevel == 2:
            start = 0
            lemma = []
            for (tag, end) in morphemes:
                if start < end and self.relevant_morpheme(tag,pos): #not tag.startswith('SUF') and  tag not in ['PREF_PP','ADJ_COMP','ADJ_SUP']:
                    morpheme = word[start:end]
                    if tag in self.stemdict:
                        morpheme = self.stemdict[tag].get(morpheme, morpheme)
                    if len(morpheme) > 0:
                        lemma.append(morpheme)
                start = end
            if taglevel == 1:
                lemma = self.makelemma(lemma,pos)
            elif taglevel == 2:
                lemma = '+'.join(lemma)
            return lemma, pos
        else:
            start = 0
            morphlist = []
            lemma = []
            for (tag, end) in morphemes:
                if not tag[:3] == b'END':
                    morpheme = word[start:end]
                    morphlist.append((morpheme, tag))
                    if start < end and self.relevant_morpheme(tag,pos): #not tag.startswith('SUF') and  tag not in ['PREF_PP','ADJ_COMP','ADJ_SUP']:                     
                        if tag in self.stemdict:
                            morpheme = self.stemdict[tag].get(morpheme, morpheme)
                        lemma.append(morpheme)
                start = end
            lemma = ''.join(lemma)
            return lemma, morphlist, pos


    cdef inline normalize(self,str w):
        #if re.match(r'^(`|``|´|´´|\'|\'\')$',w):
        if self.re_qmark.match(w):
           return '"'
        else:
           return w.lower()
        
    cpdef tag_word(self, str word, int cutoff=5,bint casesensitive = True, bint conditional = False):
        cdef:
            list p_w_tags
            double p
            bint upcase
            bint cached
            
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
            if tag != b'UNKNOWN':
               if casesensitive:
                  p += self.LP_case_t[tag][upcase]
               if conditional:
                  p -= self.LP_wtag[tag] 
            p_w_tags.append((tag,p))
            
        #p_w_tags.sort(key=lambda x: x[1], reverse=True)
        p_w_tags.sort(key=itemgetter(1), reverse=True)

        if not cached and len(p_w_tags) > 0:
           if cutoff == 0:
               p_w_tags = [p_w_tags[0]]
           else:
               limit = p_w_tags[0][1] - cutoff
               p_w_tags = [(tag,p) for (tag,p) in  p_w_tags if p >= limit]
           

        return p_w_tags

    def tag_sent(self, sent, taglevel=1, casesensitive = True):
        tags = self.tag_sent_viterbi(sent,casesensitive)
        if taglevel == 0:
            return tags
        elif taglevel == 1:
            return [(sent[i], self.analyze(sent[i], tags[i], taglevel=1)[0], tags[i]) for i in range(len(sent))]
        elif taglevel == 2:
            return [(sent[i], self.analyze(sent[i], tags[i], taglevel=2)[0], tags[i]) for i in range(len(sent))]
        else:
            return [(sent[i], *self.analyze(sent[i], tags[i], taglevel=3)) for i in range(len(sent))]


class TrainHanoverTagger:

    def __init__(self):
        self.morphdata = []
        self.sentdata = []
        self.stemdict = {}

    def normalize_w(self,w):
        if re.match(r'^(`|``|´|´´|\'|\'\')$',w):
           return '"'
        else:
           return w
           
    def normalize_m(self,morphemes): 
        result = []
        for (m,t) in morphemes:
            result.append((self.normalize_w(m),t.encode('utf8')))
        return result
         

    def load(self, fin):
        sent = []
        lastsentnr = 1
        for line in fin:
            (sentnr, word, lemma, tag, morphemes, stemsub) = line.split('\t')
            morphemes = ast.literal_eval(morphemes)
            word = self.normalize_w(word)
            morphemes = self.normalize_m(morphemes)
            self.morphdata.append(morphemes)
            if int(sentnr) >= 0:
                if sentnr != lastsentnr:
                    self.sentdata.append(sent)
                    sent = []
                    lastsentnr = sentnr   
                sent.append((word,tag.encode('utf8')))
            if len(stemsub) > 5:
                alttag, altstem, stem = ast.literal_eval(stemsub)
                sd_tag = self.stemdict.get(alttag.encode('utf8'), {})
                sd_tag[altstem] = stem
                self.stemdict[alttag.encode('utf8')] = sd_tag



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
                if self.N_m[m] < 50 and not (len(t) > 4 and t[-4:] == '_IRR'):
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

    def hapaxprobs(self):
        count = {}
        for morphemes in self.morphdata:
            for m, t in morphemes:
                count_t = count.get(t, Counter())
                count_t.update([m])
                count[t] = count_t
        p_hapax_t = {}
        for t in [b'NN',b'NE',b'ADJ',b'ADV',b'CARD',b'FM',b'VV']: #count:
            dist = Counter(count[t].values())
            if dist[1] > 0:
                p_hapax_t[t] = math.log(dist[1] / self.N_t[t])
        return p_hapax_t

    def transprob(self):
        p_trans = {}
        for word in self.morphdata:
            posseq = [b'START'] + [t for m, t in word]
            p = posseq[1]
            p_1 = posseq[0]
            prev = (b'', p_1)
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
        for tag in lp_case_t:
            total = 2 + lp_case_t[tag][True] + lp_case_t[tag][False] 
            lp_case_t[tag][True]  = math.log((1+lp_case_t[tag][True])/total)
            lp_case_t[tag][False]  = math.log((1+lp_case_t[tag][False])/total)
            
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
        return -4.6 + min(0, min_observed - max_unknown)

        

    def tagprobs_word(self):
        lp_t = {}
        p_t = Counter([pos for sent in self.sentdata for (word,pos) in sent])
        total = sum(p_t.values())
        for p in p_t:
            lp_t[p] = math.log(p_t[p] / total)
            
        p_t[b'<END>'] = len(self.sentdata)
        total += p_t[b'<END>']
        for p in p_t:
            p_t[p] = p_t[p] / total
            
        return lp_t, p_t

    def transprob_word_2(self):
        p_trans = {}
        for sent in self.sentdata:
            posseq = [b'<Start>'] + [tag for (word,tag) in sent] + [b'<END>']
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
            posseq = [b'<Start>'] + [tag for (word,tag) in sent] + [b'<END>']
            p = posseq[1]
            p_1 = posseq[0]
            prev = (b'', p_1)
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
        for p in list(self.P_wtag.keys()) + [b'', b'<Start>']:
            if p == b'<END>':
                continue
            for q in list(self.P_wtag.keys()) + [b'<Start>']:
                if q == b'<END>':
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
    
    def precompute_observed(self):
        words = Counter()
        lp_w_c = {}
        for c in self.LP_wtag:
           lp_w_c[c] = Counter()
           
        for sent in self.sentdata:
           for (w,c) in sent:
               lp_w_c[c].update([w.lower()])
               words.update([w.lower()])
        for c in lp_w_c:
           lp_w = lp_w_c[c]
           total = sum(lp_w.values())
           for w in lp_w:
               lp_w[w] = math.log(lp_w[w]/total)
           lp_w_c[c] = dict(lp_w)
        cache = {}
        n = 0
        for w, f in words.most_common(): #(nr):
            if f < 3:
               break
            observed = []
            for tag in lp_w_c:
               if w in lp_w_c[tag]:
                  p = lp_w_c[tag][w] + self.LP_wtag[tag] 
                  observed.append((tag,round(p, 4)))
            if len(observed) > 0:
               #observed.sort(key=lambda x: x[1], reverse=True)
               observed.sort(key=itemgetter(1), reverse=True)
               cache[w] = observed
        return cache

    def train_morph_model(self):
        self.N_t = Counter([t for morphemes in self.morphdata for (morph, t) in morphemes])
        self.N_m, self.LP_t_m = self.collect_tag_freqs()
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
        self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, {})
        tagger = HanoverTagger(None, model)
        if observed_values:
            self.cache = self.precompute_observed()
        else:
            self.cache = self.precompute(tagger,2000)

    def write_model(self, filename):
        model = (
        self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.cache)

        file = gzip.GzipFile(filename, 'wb')
        pickle.dump(model, file)
        file.close()
