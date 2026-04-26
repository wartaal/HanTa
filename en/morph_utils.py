from collections import Counter
from typing import List, Tuple
import re



def repair(word: str, pos: str, lemma: str) -> Tuple[str, str, str]:
    if pos == 'UNC':
        if word == 'per':
            pos = 'PRP'
        elif word == 'cent':
            pos = 'NN0'
        elif word[0:1].isupper() and word[1:].islower() and word.isalpha():
            pos = 'NP0'
            lemma = word
    elif word == "'s" :
        if pos == "VHZ":
            lemma = 'have'
        elif pos == "VBZ":
            lemma = 'be'
    elif lemma == "would" and pos == "VM0":
        lemma = 'will'
    elif lemma == "should" and pos == "VM0":
        lemma = 'shall'
    elif lemma == "could" and pos == "VM0":
        lemma = 'can'

    if len(lemma) == 0:
        lemma = word

    return word, pos, lemma

def make_morphpattern(word: str, pos: str, lemma: str):
    if pos not in ['NP0','UNC']:
        word = word.lower()
    morphemes = []
    mapping = ()

    if lemma == word:
        stem = word
        suffix = ''
    elif lemma.lower() == word.lower() and pos == 'NP0':
        stem = word
        suffix = ''
    elif word == 'an' and lemma == 'a':
        stem = word
        suffix = ''
    #elif len(lemma) == 0:
    #    print(lemma, word, pos)
    elif word.startswith(lemma + lemma[-1]):
        stem = lemma + lemma[-1]
        suffix = word[len(stem):]
    elif word.startswith(lemma):
        suffix = word[len(lemma):]
        stem = lemma
    elif lemma[-1] == 'e' and word.startswith(lemma[:-1]):
        stem = lemma[:-1]
        suffix = word[len(stem):]
    elif word[:-3] == lemma[:-1] and lemma[-1] == 'y':
        stem = word[:-2]
        suffix = word[-2:]
    elif word[:-2] == lemma[:-1] and lemma[-2:] == 'ay':
        stem = word[:-1] 
        suffix = word[-1:]
    elif lemma[-1] == 'f' and word.startswith(lemma[:-1] + 'v'):
        stem = lemma[:-1] + 'v'
        suffix = word[len(stem):]
    else:
        stem = word
        suffix = ''

    if pos == 'VBB':
        mtag = 'VB'
        stag = ''
    elif pos == 'VBD':
        mtag = 'VB'
        stag = 'SUF_ED'
    elif pos == 'VBG':
        mtag = 'VB'
        stag = 'SUF_ING'
    elif pos == 'VBI':
        mtag = 'VB'
        stag = ''
    elif pos == 'VBN':
        mtag = 'VB'
        stag = 'SUF_EN '
    elif pos == 'VBZ':
        mtag = 'VB'
        stag = ''
    elif pos == 'VDB':
        mtag = 'VD'
        stag = ''
    elif pos == 'VDD':
        mtag = 'VD'
        stag = 'SUF_ED'
    elif pos == 'VDG':
        mtag = 'VD'
        stag = 'SUF_ING'
    elif pos == 'VDI':
        mtag = 'VD'
        stag = ''
    elif pos == 'VDN':
        mtag = 'VD'
        stag = 'SUF_EN '
    elif pos == 'VDZ':
        mtag = 'VD'
        stag = 'SUF_3S'
    elif pos == 'VHB':
        mtag = 'VH'
        stag = ''
    elif pos == 'VHD':
        mtag = 'VH'
        stag = 'SUF_ED'
    elif pos == 'VHG':
        mtag = 'VH'
        stag = 'SUF_ING'
    elif pos == 'VHI':
        mtag = 'VH'
        stag = ''
    elif pos == 'VHN':
        mtag = 'VH'
        stag = 'SUF_EN '
    elif pos == 'VHZ':
        mtag = 'VH'
        stag = 'SUF_3S'
    elif pos == 'VM0':
        mtag = 'VM'
        stag = ''
    elif pos == 'VVB':
        mtag = 'VV'
        stag = ''
    elif pos == 'VVD':
        mtag = 'VV'
        stag = 'SUF_ED'
    elif pos == 'VVG':
        mtag = 'VV'
        stag = 'SUF_ING'
    elif pos == 'VVI':
        mtag = 'VV'
        stag = ''
    elif pos == 'VVN':
        mtag = 'VV'
        stag = 'SUF_EN '
    elif pos == 'VVZ':
        mtag = 'VV'
        stag = 'SUF_3S'
    elif pos == 'NN0':
        mtag = 'NNst'
        stag = ''
    elif pos == 'NN1':
        mtag = 'NN'
        stag = ''
    elif pos == 'NN2' and word == lemma:
        mtag = 'NNpt'
        stag = ''
    elif pos == 'NN2':
        mtag = 'NN'
        stag = 'SUF_NN_S'
    elif pos == 'AJC':
        mtag = 'AJ'
        stag = 'SUF_AJ_C'
    elif pos == 'AJS':
        mtag = 'AJ'
        stag = 'SUF_AJ_S'
    elif pos == 'AVC':
        mtag = 'AV'
        stag = 'SUF_AV_C'
    elif pos == 'AVS':
        mtag = 'AV'
        stag = 'SUF_AV_S'
    else:
        if pos and pos[-1] in ['0', '1', '2']:
            mtag = pos[:-1]
        else:
            mtag = pos
        stag = 'SUF_' + mtag

    if stem.lower() != lemma.lower():
        if len(suffix) == 0 and pos in ['VVD', 'VVN']:
            mtag = mtag + '_VAR_' + pos
        else:
            mtag = mtag + '_VAR'
        mapping = (mtag, stem, lemma)

    morphemes.append((stem, mtag))

    if len(suffix) > 0:
        morphemes.append((suffix, stag))

    return lemma, morphemes, mapping


def make_morph_lists(sentences: List[List[Tuple[str, str, str]]]):
    data = []
    sentnr = 0
    for sent in sentences:
        sentnr += 1
        for (word, postag, lemma) in sent:
            word, postag, lemma = repair(word, postag, lemma)
            lemma, morphemes, stemsub = make_morphpattern(word, postag, lemma)
            stem = lemma
            data.append((sentnr, word, lemma, stem, postag, morphemes, stemsub))

    return data


class MorphemeAnalyzer:
    def __init__(self):
        self.adjstems = Counter()
        self.verbstems = Counter()
        self.verbvarstems = Counter()
        self.nounstems = Counter()
        self.vvn2morphemes = {}

    def collect_morphemes(self, morphlist):
        for entry in morphlist:
            sentnr, word, lemma, stem, tag, morphemes, subst = entry
            if tag == 'VVN':
                self.vvn2morphemes[word.lower()] = morphemes
            for i in range(len(morphemes)):
                m = morphemes[i]
                if len(m[0]) < 2:
                    continue
                elif m[1] == 'AJ':
                    self.adjstems.update([m[0]])
                elif m[1] == 'VV':
                    self.verbstems.update([m[0]])
                elif m[1] == 'VV_VAR':
                    # original used subst[2]
                    try:
                        self.verbvarstems.update([subst[1]])
                        self.verbstems.update([subst[2]])
                    except Exception:
                        pass
                elif m[1] == 'NN':
                    self.nounstems.update([m[0]])


    def split_adv(self, pos, morphemes):
        morphemes_new = []
        mapping = ()
        for (word, tag) in morphemes:
            if tag == 'AV' and word[-2:] == 'ly' and (
                self.adjstems.get(word[:-2], 0) > 1 or word[:-2] in self.vvn2morphemes
            ):
                morphemes_new.append((word[:-2], 'AJ'))
                morphemes_new.append(('ly', 'SUF_AV'))
            elif tag == 'AV' and word[-3:] == 'ily' and self.adjstems.get(word[:-3] + 'y', 0) > 1:
                morphemes_new.append((word[:-3] + 'i', 'AJ_VAR'))
                morphemes_new.append(('ly', 'SUF_AV'))
                mapping = ('AJ_VAR', word[:-3] + 'i', word[:-3] + 'y')
            elif tag == 'AV' and word[-2:] == 'ly' and self.adjstems.get(word[:-1] + 'e', 0) > 1:
                morphemes_new.append((word[:-1], 'AJ_VAR'))
                morphemes_new.append(('y', 'SUF_AV'))
                mapping = ('AJ_VAR', word[:-1], word[:-1] + 'e')
            else:
                morphemes_new.append((word, tag))

        return morphemes_new, mapping, pos

    ## TODO -ship,  (relationship, steamship)
    ##  combustibility
    def split_noun(self, pos, morphemes):
        morphemes_new = []
        mapping = ()


        word, tag = morphemes[0]
        if word.startswith('non-')  and self.nounstems.get(word[4:], 0) > 5:
            morphemes = [('non', 'PREF_NEG'), ('-', 'HYPHEN'), (word[4:], tag)] + morphemes[1:]
        if word.startswith('anti-')  and self.nounstems.get(word[5:], 0) > 5:
            morphemes = [('anti', 'PREF_NEG'), ('-', 'HYPHEN'), (word[5:], tag)] + morphemes[1:]


        for (word, tag) in morphemes:
            if tag in ["NNst", "NN"] and word[-3:] == 'ing' and self.verbstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'VV'))
                morphemes_new.append(('ing', 'SUF_ING'))
            elif tag in ["NNst", "NN"] and word.endswith('ing') and self.verbstems.get(word[:-3] + 'e', 0) > 5:
                morphemes_new.append((word[:-3], 'VV_VAR'))
                morphemes_new.append(('ing', 'SUF_ING'))
            elif len(word) < 8:
                morphemes_new.append((word, tag))
            elif tag in ["NNst", "NN"] and word[-4:] == 'ness' and self.adjstems.get(word[:-4], 0) > 5:
                morphemes_new.append((word[:-4], 'AJ0'))
                morphemes_new.append(('ness', 'SUF_JJN'))
            elif tag in ["NNst", "NN"] and word[-5:] == 'iness' and self.adjstems.get(word[:-5] + 'y', 0) > 5:
                morphemes_new.append((word[:-5] + 'i', 'AJ0_VAR'))
                morphemes_new.append(('ness', 'SUF_AJN'))
                mapping = ('AJ0_VAR', word[:-5] + 'i', word[:-5] + 'y')
            elif tag in ["NNst", "NN", "NN_VAR"] and re.fullmatch(r'[ai]bilit[iy]', word[-7:]):
                aj = word[:-6] + 'ble'
                ajmorphemes, mapping, _ = self.split_adj('AJ',[(word[:-3], 'AJ_VAR')])
                morphemes_new.extend(ajmorphemes)
                morphemes_new.append((word[-3:], 'SUF_AJN'))
                if len(ajmorphemes) == 1:
                    mapping = ('AJ_VAR', word[:-3], aj)
            elif tag in ["NNst", "NN"] and word[-3:] == 'ity' and self.adjstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'AJ'))
                morphemes_new.append(('ity', 'SUF_AJN'))
            elif tag == 'NN_VAR' and word[-3:] == 'iti' and self.adjstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'AJ'))
                morphemes_new.append(('iti', 'SUF_AJN_VAR'))
                mapping = ('SUF_AJN_VAR', 'iti', 'ity')
            elif tag in ["NNst", "NN"] and word[-3:] == 'ity' and self.adjstems.get(word[:-3] + 'e', 0) > 5:
                morphemes_new.append((word[:-3], 'AJ_VAR'))
                morphemes_new.append(('ity', 'SUF_AJN'))
                mapping = ('AJ_VAR', word[:-3], word[:-3] + 'e')
            elif tag == 'NN_VAR' and word[-3:] == 'iti' and self.adjstems.get(word[:-3] + 'e', 0) > 5:
                morphemes_new.append((word[:-3], 'AJ_VAR'))
                morphemes_new.append(('iti', 'SUF_AJN_VAR'))
                mapping = ('SUF_AJN_VAR', 'iti', 'ity')
            elif tag in ["NNst", "NN"] and word[-3:] == 'ion' and self.verbstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'VV'))
                morphemes_new.append(('ion', 'SUF_VN'))
            elif tag in ["NNst", "NN"]  and word[-3:] == 'ion' and self.verbstems.get(word[:-3] + 'e', 0) > 5:
                morphemes_new.append((word[:-3], 'VV_VAR'))
                morphemes_new.append(('ion', 'SUF_VN'))
                mapping = ('VV_VAR', word[:-3], word[:-3] + 'e')
            else:
                compound = False
                if len(word) >= 8:
                    for i in range(4, len(word)-4):
                        if self.nounstems.get(word[:i], 0) > 10 and\
                              self.nounstems.get(word[i:], 0) > 10 and\
                            word[:i] not in ['rein','counter'] and\
                            word[i:] not in ['ship','hood','ment','less','ness','nation']:

                            morphemes_new.append((word[:i], 'NN'))
                            morphemes_new.append((word[i:], tag))
                            compound = True
                            break

                if not compound:    
                    morphemes_new.append((word, tag))

        return morphemes_new, mapping, pos

    def split_adj(self, pos, morphemes):
        morphemes_new = []
        mapping = ()

        word, tag = morphemes[0]
        if word.startswith('un') and (
            self.adjstems.get(word[2:], 0) > 0
            or (not word.startswith('under') and not word.startswith('uni') and not word.startswith('unanim'))
        ):
            morphemes = [('un', 'PREF_NEG'), (word[2:], tag)] + morphemes[1:]
        elif word.startswith('non-')  and self.nounstems.get(word[4:], 0) > 5 and self.adjstems.get(word[4:], 0) < 3:
            morphemes = [(word, 'NN')] + morphemes[1:] ## Split and CORRECT!
            return self.split_noun('NN', morphemes)
        elif word.startswith('non-')  and (
            self.adjstems.get(word[4:], 0) > 0 or word.endswith('ing') or word.endswith('ent')
        ):
            morphemes = [('non', 'PREF_NEG'), ('-', 'HYPHEN'), (word[4:], tag)] + morphemes[1:]
        elif word.startswith('anti-')  and self.nounstems.get(word[5:], 0) > 8 and self.adjstems.get(word[:], 0) < 3\
            and not word.endswith('ing') and not word.endswith('ese') and not word.endswith('an'):
            morphemes = [(word, 'NN')] + morphemes[1:] ## Split and CORRECT!
            return self.split_noun('NN1', morphemes)
        elif word.startswith('anti-')  and (
            self.adjstems.get(word[5:], 0) > 0 or word.endswith('ing') or word.endswith('ent')
        ):
            morphemes = [('anti', 'PREF_NEG'), ('-', 'HYPHEN'), (word[5:], tag)] + morphemes[1:]


        for (word, tag) in morphemes:
            if tag == 'AJ' and word.endswith('ing') and self.verbstems.get(word[:-3], 0) > 1:
                vmorphemes, mapping, _ = self.split_verb('VVG', [(word[:-3], 'VV')])
                morphemes_new.extend(vmorphemes)
                morphemes_new.append(('ing', 'SUF_ING'))
            elif tag == 'AJ' and word.endswith('ing') and self.verbstems.get(word[:-3] + 'e', 0) > 1:
                vmorphemes, mapping, _ = self.split_verb('VVG', [(word[:-3], 'VV_VAR')])
                morphemes_new.extend(vmorphemes)
                morphemes_new.append(('ing', 'SUF_ING'))
                #mapping = ('VV_VAR', word[:-3], word[:-3] + 'e')
                mapping = ('VV_VAR', vmorphemes[-1][0], vmorphemes[-1][0] + 'e')
            elif tag == 'AJ' and word in self.vvn2morphemes:
                #morphemes_new.extend(self.vvn2morphemes[word])
                vmorphemes, mapping, _ = self.split_verb('VVN', self.vvn2morphemes[word])
                morphemes_new.extend(vmorphemes)
            elif len(word) < 6:
                morphemes_new.append((word, tag))
            elif tag == 'AJ' and word[-4:] == 'able' and self.verbstems.get(word[:-4], 0) > 5:
                morphemes_new.append((word[:-4], 'VV'))
                morphemes_new.append(('able', 'SUF_VVAJ'))
            elif tag == 'AJ' and word[-4:] == 'able' and self.verbstems.get(word[:-4] + 'e', 0) > 5:
                morphemes_new.append((word[:-4], 'VV_VAR'))
                morphemes_new.append(('able', 'SUF_VVAJ'))
                mapping = ('VV_VAR', word[:-4], word[:-4] + 'e')
            elif tag == 'AJ' and word[-5:] == 'iable' and self.verbstems.get(word[:-5] + 'y', 0) > 5:
                morphemes_new.append((word[:-5] + 'i', 'VV_VAR'))
                morphemes_new.append(('able', 'SUF_VV_AJ'))
                mapping = ('VV_VAR', word[:-5] + 'i', word[:-5] + 'y')
            elif tag == 'AJ_VAR' and word[-3:] == 'abl' and self.verbstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'VV'))
                morphemes_new.append(('abl', 'SUF_VVAJ'))
            elif tag == 'AJ_VAR' and word[-4:] == 'iabl' and self.verbstems.get(word[:-4] + 'y', 0) > 5:
                morphemes_new.append((word[:-4] + 'i', 'VV_VAR'))
                morphemes_new.append(('abl', 'SUF_VVAJ'))
                mapping = ('VV_VAR', word[:-4] + 'i', word[:-4] + 'y')
            elif tag == 'AJ_VAR' and re.match(r'[ia]bil',word[-4:]) and self.verbstems.get(word[:-4], 0) > 5:
                morphemes_new.append((word[:-4], 'VV'))
                morphemes_new.append((word[-4:], 'SUF_VVAJ_VAR'))
                mapping = ('SUF_VVAJ_VAR', word[-4:] , word[-4]+'ble')
            elif tag == 'AJ_VAR' and word[-5:] == 'iabil'  and self.verbstems.get(word[:-5] + 'y', 0) > 5:
                morphemes_new.append((word[:-5]+ 'y', 'VV_VAR'))
                morphemes_new.append(('abil', 'SUF_VVAJ_VAR'))
                mapping = ('VV_VAR', word[:-5]+ 'i' ,word[:-5]+ 'y') 
            elif tag == 'AJ' and word[-4:] == 'less' and self.nounstems.get(word[:-4], 0) > 5:
                morphemes_new.append((word[:-4], 'NN'))
                morphemes_new.append(('less', 'SUF_NNAJ'))
            elif tag == 'AJ' and word[-3:] == 'ful' and self.nounstems.get(word[:-3], 0) > 5:
                morphemes_new.append((word[:-3], 'NN'))
                morphemes_new.append(('ful', 'SUF_NNAJ'))
            elif tag == 'AJ' and word[-4:] == 'full' and self.nounstems.get(word[:-4], 0) > 5:
                morphemes_new.append((word[:-4], 'NN'))
                morphemes_new.append(('full', 'SUF_NNAJ'))
            elif tag == 'AJ' and '-' in word:
                parts = word.split('-')
                if (
                    len(parts) == 2
                    and self.nounstems.get(parts[0], 0) > 5
                    and self.adjstems.get(parts[1], 0) > 5
                    and self.adjstems.get(parts[0], 0) < 10
                    and self.nounstems.get(parts[1], 0) < 10
                    and len(parts[0]) > 2
                    and len(parts[1]) > 2
                    and parts[0] not in ['co', 'pre', 're', 'un', 'non', 'mid', 'anti', 'post', 'pro', 'well', 'sub','counter']
                ):
                    morphemes_new.append((parts[0].strip(), 'NN'))
                    morphemes_new.append(('-', 'HYPHEN'))
                    morphemes_new.append((parts[1].strip(), 'AJ'))
                else:
                    morphemes_new.append((word, tag))

            else:
                morphemes_new.append((word, tag))

        return morphemes_new, mapping, pos



#TODO remaining, remained etc. when analyed as AJ
    def split_verb(self, pos, morphemes):
   
        mapping = ()

        word, tag = morphemes[0]
        
        parts = word.split('-')
        if len(parts) > 1 and parts[0] in ['re','co','over','under','pre','cross'] :
            morphemes_new = []
            morphemes_new.append((parts[0].strip(), 'PREF_VV'))
            morphemes_new.append(('-', 'HYPHEN'))
            morphemes_new.append((''.join(parts[1:]), tag))
            morphemes = morphemes_new + morphemes[1:]
        elif word.startswith('re') and (self.verbstems.get(word[2:], 0) > 5 or self.verbvarstems.get(word[2:], 0) > 5):
            morphemes = [('re', 'PREF_VV'), (word[2:], tag)] + morphemes[1:]
        elif word.startswith('co') and (self.verbstems.get(word[2:], 0) > 5 or self.verbvarstems.get(word[2:], 0) > 5):
            morphemes = [('co', 'PREF_VV'), (word[2:], tag)] + morphemes[1:]
        elif word.startswith('over') and (self.verbstems.get(word[4:], 0) > 5 or self.verbvarstems.get(word[4:], 0) > 5):
            morphemes = [('over', 'PREF_VV'), (word[4:], tag)] + morphemes[1:]
        elif word.startswith('under') and (self.verbstems.get(word[5:], 0) > 5 or self.verbvarstems.get(word[5:], 0) > 5):
            morphemes = [('under', 'PREF_VV'), (word[5:], tag)] + morphemes[1:]
        elif word.startswith('pre') and (self.verbstems.get(word[3:], 0) > 5 or self.verbvarstems.get(word[3:], 0) > 5):
            morphemes = [('pre', 'PREF_VV'), (word[3:], tag)] + morphemes[1:]



        return morphemes, mapping, pos 

    def postprocess_morphemes(self, morphlist):
        data = []

        for entry in morphlist:
            if len(entry) != 7:
                data.append(entry)
                continue
            sentnr, word, lemma, stem, tag, morphemes, subst = entry
            if tag == "AV0":
                morphemes_new, subst_new, tag = self.split_adv(tag, morphemes)
                if len(subst_new) >= len(subst):
                    subst = subst_new
                morphemes_new, subst_new, tag = self.split_adj(tag, morphemes_new)
                if len(subst_new) >= len(subst):
                    subst = subst_new
            elif tag in ["NN0", "NN1", "NN2"]:
                morphemes_new, subst_new, tag = self.split_noun(tag, morphemes)
                if len(subst_new) >= len(subst):
                    subst = subst_new
            elif tag in ['AJ0','AJC','AJS']    :
                morphemes_new, subst_new, tag = self.split_adj(tag, morphemes)
                if len(subst_new) >= len(subst):
                    subst = subst_new
            elif tag.startswith('V'): 
                morphemes_new, subst_new, tag = self.split_verb(tag, morphemes)
                if len(subst) > 0 and len(morphemes_new) > len(morphemes):    
                    preflen = len(morphemes_new[0][0])
                    if morphemes_new[0][1] == "HYPHEN":
                        preflen+= 1
                    subst = (subst[0], subst[1][preflen:], subst[2][preflen:])  
            else:
                morphemes_new = morphemes
            data.append((sentnr, word, lemma, stem, tag, morphemes_new, subst))

        return data
