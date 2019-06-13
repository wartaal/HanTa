from collections import Counter, namedtuple
import math
from numpy import logaddexp
import pickle
import gzip
import ast
import pprint

State = namedtuple("State", ["p2", "p1"])


class HanoverTagger:

    def __init__(self, filename, model=None):
        if filename:
            file = gzip.GzipFile(filename, 'rb')
            model = pickle.load(file)
            file.close()
            self.strict = False
        else:
            self.strict = True
        self._debug = False
        if model:
            self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t, self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.cache = model

    def lp_m_t(self, m, t,wlen):
        lp = -math.inf
        if t in self.LP_m_t and m in self.LP_m_t[t]:
            lp = self.LP_m_t[t][m]
        #elif not self.strict and m not in self.N_m and t in self.LP_len_t and t in self.LP_s_t and t in self.LP_hapax_t:
        elif not self.strict and t in self.LP_len_t and t in self.LP_s_t and t in self.LP_hapax_t and (wlen < 4 or len(m) > 2): 
            if len(m) > 3 and m[-3:] in self.LP_s_t[t]:
                lp_suf = self.LP_s_t[t][m[-3:]]
            elif len(m) > 2 and m[-2:] in self.LP_s_t[t]:
                lp_suf = self.LP_s_t[t][m[-2:]]
            elif len(m) > 2 and m[-1:] in self.LP_s_t[t]:
                lp_suf = self.LP_s_t[t][m[-1:]]
            else:
                lp_suf = self.LP_s_t[t]['']
            lp = self.Int_t + self.LP_hapax_t[t] + self.LP_len_t[t][min(len(m), 24)] + lp_suf

        return lp

    def lp_trans(self, state, final=False):
        if state in self.LP_trans:
            if final:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if tag.startswith('END_')]
            else:
                following = [(tag, lp) for (tag, lp) in self.LP_trans[state].items() if not tag.startswith('END_')]
        else:
            following = []
        return following

    def analyze_forward(self, word): 
        lowerbound = -1e6
        table = []
        for i in range(len(word) + 2):
            table.append({})
        table[0][State(p2=None, p1='START')] = 0
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
                    morpheme = word[i:j]
                    for tag1, lpt in followup:
                        lp1 = lp + lpt + self.lp_m_t(morpheme, tag1,len(word))
                        if lp1 > lowerbound:
                            tag2 = state.p1
                            newstate = State(p2=tag2, p1=tag1)
                            if newstate in table[j]:
                                table[j][newstate] = logaddexp(lp1, table[j][newstate])
                            else:
                                table[j][newstate] = lp1

        for state in table[-2]:
            lp = table[-2][state]
            for tag1, lpt in self.lp_trans(state, final=True):
                lp1 = lp + lpt
                if lp1 > lowerbound:
                    tag2 = state.p1
                    newstate = State(p2=tag2, p1=tag1)
                    if newstate in table[-1]:
                        table[-1][newstate] = logaddexp(lp1, table[-1][newstate])
                    else:
                        table[-1][newstate] = lp1

        if self._debug:
            pprint.pprint(table)
        results = {}
        for state in table[-1]:
            lp = table[-1][state]
            if lp == -math.inf:
                continue
            pos = state.p1[4:]
            if pos in results:
                results[pos] = logaddexp(results[pos], lp)
            else:
                results[pos] = lp
        results = list(results.items())
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results

    def analyze_viterbi(self, word, pos):
        lowerbound = -1e6
        table = []
        backpointer = []
        for i in range(len(word) + 2):
            table.append({})
            backpointer.append({})
        table[0][State(p2=None, p1='START')] = 0
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
                    morpheme = word[i:j]
                    for tag1, lpt in followup:
                        lp1 = lp + lpt + self.lp_m_t(morpheme, tag1, len(word))
                        tag2 = state.p1
                        newstate = State(p2=tag2, p1=tag1)
                        if lp1 > table[j].get(newstate, lowerbound):
                            table[j][newstate] = lp1
                            backpointer[j][newstate] = (state, i)

        for state in table[-2]:
            lp = table[-2][state]
            for tag1, lpt in self.lp_trans(state, final=True):
                lp1 = lp + lpt
                tag2 = state.p1
                newstate = State(p2=tag2, p1=tag1)
                if lp1 > table[-1].get(newstate, lowerbound):
                    table[-1][newstate] = lp1
                    backpointer[-1][newstate] = (state, len(word))

        if self._debug:
            pprint.pprint(table)
            
        pmax = -math.inf
        beststate = ""
        for state in table[-1]:
            lp = table[-1][state]
            if lp > pmax and (pos == None or pos == state.p1):
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
        states = [(beststate, i)]
        state = beststate
        while i > 0:
            state, i = backpointer[i][state]
            states.append((state, i))
        states = states[:-1]

        return [(state.p1, i) for (state, i) in states[::-1]]

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
            wprobs = dict(self.tag_word(w,casesensitive=cs))
            row = {}
            backpointer.append({})
            if i == 0:
                prevrow = {State(p2=None, p1='<Start>'): 0.0}
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
                lp_t = self.LP_trans_word[prev].items()
                for c, lp_tc in lp_t:
                    if c not in wprobs:
                        continue
                    lpwc = wprobs[c]
                    lp = lp0 + lp_tc + lpwc
                    c2 = prev.p1
                    newstate = State(p2=c2, p1=c)
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
            lp = lp0 + lp_t.get('<END>', -math.inf)
            if lp > row.get('<END>', -math.inf):
                row['<END>'] = lp
                backpointer[-1]['<END>'] = prev
        table.append(row)

        if self._debug:
            pprint.pprint(table)

        tags = []
        state = '<END>'
        for i in range(len(backpointer) - 1, 0, -1):
            state = backpointer[i][state]
            if state.p1 != '<Upcase>':
                tags.append(state.p1)

        return tags[::-1]
        
    def makelemma(self,stem_morphemes,pos):
        lemma = ''.join(stem_morphemes)
        if pos[0] == 'V':
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
        elif pos == 'NN' or pos == 'NE':
           lemma = lemma[0].upper() + lemma[1:]
        elif pos[0] == '$':
           lemma = '--'
        return lemma
    
    def relevant_morpheme(self,mtag,pos):
        #verb suffixs belong to lemma in case a participle was turnes into an adjective!
        if pos == 'ADJA' or pos == 'ADJD':
            if mtag not in ['SUF_ADJ','ADJ_COMP','ADJ_SUP']:
               return True
            else:
               return False
        elif pos == 'PTKZU':
            return True
        else:
            if not mtag.startswith('SUF') and  mtag not in ['PREF_PP','PTKZU']:
               return True
            else:
               return False
    

    def analyze(self, word, pos=None, taglevel=1):
        word = word.lower()
        if pos:
            pos = 'END_' + pos
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
                if not tag.startswith('END'):
                    morpheme = word[start:end]
                    morphlist.append((morpheme, tag))
                    if start < end and self.relevant_morpheme(tag,pos): #not tag.startswith('SUF') and  tag not in ['PREF_PP','ADJ_COMP','ADJ_SUP']:                     
                        if tag in self.stemdict:
                            morpheme = self.stemdict[tag].get(morpheme, morpheme)
                        lemma.append(morpheme)
                start = end
            lemma = ''.join(lemma)
            return lemma, morphlist, pos

            return morphemes, pos

        
    def tag_word(self, word, cutoff=5,casesensitive = True):
        if casesensitive and word[0].isupper():
            upcase = True
        else:
            upcase = False
        word = word.lower()
        if word in self.cache:
            p_tags = self.cache[word]
            cached = True
        else:
            p_tags = self.analyze_forward(word)
            cached = False
         
        p_w_tags = []
        for tag,p in p_tags:
            if casesensitive:
               p += self.LP_case_t[tag][upcase]
            p -= self.LP_wtag[tag]
            p_w_tags.append((tag,p))
            
        p_w_tags.sort(key=lambda x: x[1], reverse=True)

        if not cached:
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


    def load(self, fin):
        sent = []
        lastsentnr = 1
        for line in fin:
            (sentnr, word, lemma, tag, morphemes, stemsub) = line.split('\t')
            morphemes = ast.literal_eval(morphemes)
            self.morphdata.append(morphemes)
            if int(sentnr) >= 0:
                if sentnr != lastsentnr:
                    self.sentdata.append(sent)
                    sent = []
                    lastsentnr = sentnr                   
                sent.append((word,tag))
            if len(stemsub) > 5:
                alttag, altstem, stem = ast.literal_eval(stemsub)
                sd_tag = self.stemdict.get(alttag, {})
                sd_tag[altstem] = stem
                self.stemdict[alttag] = sd_tag
            #wclset = self.wordclasses.get(word.lower(), set())
            #wclset.add(tag)
            #self.wordclasses[word.lower()] = wclset


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
                    if self.N_m[morph] < 10 and len(morph) > len_s and not self.endswith_one_of(morph, exclude):
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
                if self.N_m[m] < 10 and not t.endswith('_IRR'):
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
        for t in ['NN','NE','ADJ','ADV','CARD','FM']: #count:
            dist = Counter(count[t].values())
            if dist[1] > 0:
                p_hapax_t[t] = math.log(dist[1] / self.N_t[t])
            # else: #implicit
            #    p_hapax_t[t] = -math.inf
        return p_hapax_t

    def transprob(self):
        p_trans = {}
        for word in self.morphdata:
            posseq = ['START'] + [t for m, t in word]
            p = posseq[1]
            p_1 = posseq[0]
            prev = State(p2=None, p1=p_1)
            n_prev = p_trans.get(prev, {})
            n_prev[p] = 1 + n_prev.get(p, 0)
            p_trans[prev] = n_prev
            for i in range(2, len(posseq)):
                p = posseq[i]
                p_1 = posseq[i - 1]
                p_2 = posseq[i - 2]
                prev = State(p2=p_2, p1=p_1)
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
            
        p_t['<END>'] = len(self.sentdata)
        total += p_t['<END>']
        for p in p_t:
            p_t[p] = p_t[p] / total
            
        return lp_t, p_t

    def transprob_word_2(self):
        p_trans = {}
        for sent in self.sentdata:
            posseq = ['<Start>'] + [tag for (word,tag) in sent] + ['<END>']
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
            posseq = ['<Start>'] + [tag for (word,tag) in sent] + ['<END>']
            p = posseq[1]
            p_1 = posseq[0]
            prev = State(p2=None, p1=p_1)
            n_prev = p_trans.get(prev, {})
            n_prev[p] = 1 + n_prev.get(p, 0)
            p_trans[prev] = n_prev
            for i in range(2, len(posseq)):
                p = posseq[i]
                p_1 = posseq[i - 1]
                p_2 = posseq[i - 2]
                prev = State(p2=p_2, p1=p_1)
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
        for p in list(self.P_wtag.keys()) + [None, '<Start>']:
            if p == '<END>':
                continue
            for q in list(self.P_wtag.keys()) + ['<Start>']:
                if q == '<END>':
                    continue
                pq = State(p2=p, p1=q)
                t_pq = {}
                for r in list(self.P_wtag.keys()):
                    t_pq[r] = round(math.log(
                        weights[2] * self.P_trans_word_3.get(pq, {}).get(r, 0) + weights[1] * self.P_trans_word_2.get(q, {}).get(r, 0) + weights[0] * math.exp(self.P_wtag[r])), 4)

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
    
    def precompute_observed(self, tagger, nr):
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
            if f < 10:
               break
            observed = []
            for tag in lp_w_c:
               if w in lp_w_c[tag]:
                  p = lp_w_c[tag][w]
                  observed.append((tag,round(p, 4)))
            if len(observed) > 0:
               observed.sort(key=lambda x: x[1], reverse=True)
               cache[w] = observed
        #for w, f in words.most_common(2 * nr)[nr:]:
        #    computed = tagger.analyze_forward(w) 
        #    error = 0
        #    for (t,p) in computed:
        #       if w in lp_w_c[t]:
        #          print(w,t,round(p,2),round(lp_w_c[t][w],2), sep = '\t')
        return cache

    def train_morph_model(self):
        self.N_t = Counter([t for morphemes in self.morphdata for (morph, t) in morphemes])
        self.N_m, self.LP_t_m = self.collect_tag_freqs()
        self.LP_s_t = self.suffixprobs()
        self.LP_len_t = self.lenprobs()
        self.LP_hapax_t = self.hapaxprobs()
        self.Int_t = self.intercept()
        self.LP_trans = self.transprob()
        self.LP_m_t = self.morphprobs()
        self.LP_case_t = self.caseprobs()

    def train_sent_model(self):
        self.LP_wtag, self.P_wtag = self.tagprobs_word()
        self.P_trans_word_2 = self.transprob_word_2()
        self.P_trans_word_3 = self.transprob_word_3()
        self.LP_trans_word = self.mixture([0.01,0.04,0.95])

        
        
    def train_model(self):
        self.train_morph_model()
        self.train_sent_model()
        model = (
        self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, {})
        tagger = HanoverTagger(None, model)
        self.cache = self.precompute(tagger, 2000)

    def write_model(self, filename):
        model = (
        self.LP_s_t, self.LP_len_t, self.Int_t, self.LP_hapax_t, self.LP_trans, self.LP_m_t,
        self.stemdict, self.LP_trans_word, self.LP_wtag, self.LP_case_t, self.cache)

        file = gzip.GzipFile(filename, 'wb')
        pickle.dump(model, file)
        file.close()
