import codecs
import nltk
from nltk.corpus import wordnet as wn
from collections import Counter


lemmatizer = nltk.WordNetLemmatizer()

def wntag(pttag):
    if pttag in ['JJ', 'JJR', 'JJS','JJT']:
        return wn.ADJ
    elif pttag[:2] in ['NN', 'NP']:
        return wn.NOUN
    elif pttag in ['RB', 'RBR', 'RBS','RBT','QL']:
        return wn.ADV
    elif pttag[:2] in ['VB', 'DO','HV','BE','MD']:
        return wn.VERB
    return None

def lemmatize(word,pos):
    wnt = wntag(pos)
    if pos[-1] == 'G' and word.endswith("n'"):
        word = word[:-1]+'g'
    
    if word == 'an':
        return 'a'
    elif word == "n't":
        return 'not'
    elif word == 'ca' and pos == 'MD':
        return 'can'
    elif word == "'s'" and pos == "BEZ":
        return 'is'
    elif word == 'men' and pos == 'NNS':
        return 'man'
    elif word == 'uses' and pos == 'NNS':
        return 'use'
    elif word == 'rated' and pos == 'VBN':
        return 'rate'
    elif word == 'rates' and pos == 'VBZ':
        return 'rate'
    elif word == 'rating' and pos == 'VBG':
        return 'rate'
    elif word == 'fastest':
        return 'fast'
    elif wnt == None:
        return word
    else:
        return lemmatizer.lemmatize(word,wnt)


def make_morphpattern(word,pos):
    word = word.lower()
    lemma = lemmatize(word,pos)
    morphemes = []
    mapping = ()
    

        
    if lemma == word:
        stem = word
        suffix = ''
    elif word == 'an' and lemma == 'a':
        stem = word
        suffix = ''
    elif word.startswith(lemma+lemma[-1]):
        stem = lemma+lemma[-1]
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
    elif lemma[-1] == 'f' and word.startswith(lemma[:-1]+'v'):
        stem = lemma[:-1]+'v'
        suffix = word[len(stem):]
    else:
        stem = word
        suffix = ''
        
        
    if pos == 'VBZ':
        mtag = 'VB'
        stag = 'SUF_VB_S'
    elif pos == 'VBD': 
        mtag = 'VB'
        stag = 'SUF_VB_D'
    elif pos == 'VBN': 
        mtag = 'VB'
        stag = 'SUF_VB_N'
    elif pos == 'VBG':
        mtag = 'VB'
        stag = 'SUF_ING'
    elif pos == 'NNS':
        mtag = 'NN'
        stag = 'SUF_NN_S'
    elif pos == 'NPS':
        mtag = 'NP'
        stag = 'SUF_NN_S'
    elif pos == 'JJR' or (pos == 'RBR' and suffix.endswith('er')):
        mtag = 'JJ'
        stag = 'SUF_JJ_R'
    elif pos == 'JJT' or (pos == 'RBT' and suffix.endswith('st')):
        mtag = 'JJ'
        stag = 'SUF_JJ_T'
    else:
        mtag = pos
        stag = 'SUF_'+pos
        

    if stem != lemma:
        if len(suffix) == 0 and pos in ['VBD','VBN']:
            mtag = mtag+'_VAR_'+pos
        else:
            mtag = mtag+'_VAR'
        mapping = (mtag,stem,lemma)
        
        
    morphemes.append((stem,mtag))
    
    if len(suffix) > 0:
        morphemes.append((suffix,stag))

 
    #morphemes.append(('','END_'+pos))
        
    return lemma,morphemes,mapping

def read_brown():
    data = []
    sentnr = 0
    for sent in nltk.corpus.brown.tagged_sents():
        sent1 = []
        debug = False
        problematic = False
        
        for (word,tag) in sent:
            tagparts = tag.split('-')
            tag = tagparts[0]
            if len(tagparts) == 2:
                TL = True
            else:
                TL = False
                
            
            if len(tag) == 0 and word == '--':
                sent1.append(('--','--',False)) 
            elif tag == '*':
                sent1.append((word,'RB',TL)) 
            elif tag[-1] == '*' and word.endswith("n't"):
                sent1.append((word[:-3],tag[:-1],TL)) 
                sent1.append(("n't",'RB',False)) 
            elif tag == 'MD*' and word[-3:] == "not":
                sent1.append((word[:-3],'MD',TL)) 
                sent1.append(('not','RB',False)) 
            elif word.endswith("'s") and tag[-1] == '$':
                sent1.append((word[:-2],tag[:-1],TL)) 
                sent1.append(("'s",'POS',False)) 
            elif "'" in word[1:] and '+' in tag:
            #elif len(word.split("'")) == 2 and len(tag.split('+')) == 2:
                w1,w2 = word.split("'")
                t1,t2 = tag.split('+')
                sent1.append((w1,t1,TL))
                sent1.append(("'"+w2,t2,TL))
            elif word == 'gonna' and tag == 'VBG+TO':
                sent1.append(('gon','VBG',TL))
                sent1.append(('na','TO',False))
            elif word == 'gotta' and tag == 'VBG+TO':
                sent1.append(('got','VBN',TL))
                sent1.append(('ta','TO',False))
            elif word[-1] == "'" and tag[-1] == '$':
                sent1.append((word[:-1],tag[:-1],TL))
                sent1.append(("'",'POS',False))
            elif '+' in tag:
                problematic = True
            elif 'NIL' == tag:
                problematic = True
            else:
                sent1.append((word,tag,TL))
                
        
        if problematic:
            continue
            
        for (word,postag,TL) in sent1:

            lemma,morphemes,stemsub = make_morphpattern(word,postag)
            stem = lemma
            if TL:
                lemma = lemma[0].upper()+lemma[1:]
            if len(word) and len(lemma) > 0:
                data.append((sentnr,word,lemma,stem,postag,morphemes,stemsub))
        sentnr += 1    
 
    return data


def collect_morphemes(morphlist):

    global adjstems 
    global verbstems
    global vbn2morphemes

    adjstems = Counter()
    verbstems = Counter()
    vbn2morphemes = {}
 
    for entry in morphlist:
        sentnr,word,lemma,stem, tag, morphemes, subst = entry
        if tag == 'VBN':
            vbn2morphemes[word.lower()] = morphemes[:-1]
        for i in range(len(morphemes)):
            m = morphemes[i]
            if len(m[0]) < 2:
                continue
            elif m[1] == 'JJ' or m[1] == 'JJS':
                adjstems.update([m[0]])
            elif m[1] == 'VB':
                verbstems.update([m[0]])
            elif m[1] == 'VB_VAR':
                verbstems.update([subst[2]])

def split_adv(morphemes):
    morphemes_new = []
    mapping = ()
    for (word,tag) in morphemes:
        if tag in ["RB","QL"] and word[-2:] == 'ly' and (adjstems.get(word[:-2],0) > 1 or word[:-2] in vbn2morphemes):  #honestly
            morphemes_new.append((word[:-2],'JJ'))
            morphemes_new.append(('ly','SUF_RB'))
        elif tag in ["RB","QL"]  and word[-3:] == 'ily' and adjstems.get(word[:-3]+'y',0) > 1: #easily
            morphemes_new.append((word[:-3]+'i','JJ_VAR'))
            morphemes_new.append(('ly','SUF_RB'))
            mapping = ('JJ_VAR',word[:-3]+'i',word[:-3]+'y')
        elif tag in ["RB","QL"]  and word[-2:] == 'ly' and adjstems.get(word[:-1]+'e',0) > 1: #terribly
            morphemes_new.append((word[:-1],'JJ_VAR'))
            morphemes_new.append(('y','SUF_RB'))
            mapping = ('JJ_VAR',word[:-1],word[:-1]+'e')
        else:
            morphemes_new.append((word,tag))
            
    return morphemes_new,mapping


def split_noun(morphemes):
    morphemes_new = []
    mapping = ()
    for (word,tag) in morphemes:
        if len(word) < 8:
            morphemes_new.append((word,tag))
        elif tag == 'NN' and word[-4:] == 'ness' and adjstems.get(word[:-4],0) > 5:  
            morphemes_new.append((word[:-4],'JJ'))
            morphemes_new.append(('ness','SUF_JJN'))
        elif tag == 'NN' and word[-5:] == 'iness' and adjstems.get(word[:-5]+'y',0) > 5: 
            morphemes_new.append((word[:-5]+'i','JJ_VAR'))
            morphemes_new.append(('ness','SUF_JJN'))
            mapping = ('JJ_VAR',word[:-5]+'i',word[:-5]+'y')
        elif tag == 'NN'  and word[-3:] == 'ity' and adjstems.get(word[:-3],0) > 5: 
            morphemes_new.append((word[:-3],'JJ'))
            morphemes_new.append(('ity','SUF_JJN'))
        elif tag == 'NN_VAR'  and word[-3:] == 'iti' and adjstems.get(word[:-3],0) > 5: 
            morphemes_new.append((word[:-3],'JJ'))
            morphemes_new.append(('iti','SUF_JJN_VAR'))
            mapping = ('SUF_JJN_VAR','iti','ity')
        elif tag == 'NN'  and word[-3:] == 'ity' and adjstems.get(word[:-3]+'e',0) > 5: 
            morphemes_new.append((word[:-3],'JJ_VAR'))
            morphemes_new.append(('ity','SUF_JJN'))
            mapping = ('JJ_VAR',word[:-3],word[:-3]+'e')
        elif tag == 'NN_VAR'  and word[-3:] == 'iti' and adjstems.get(word[:-3]+'e',0) > 5: 
            morphemes_new.append((word[:-3],'JJ_VAR'))
            morphemes_new.append(('iti','SUF_JJN_VAR'))
            mapping = ('SUF_JJN_VAR','iti','ity')
            #mapping = ('JJ_VAR',word[:-3],word[:-3]+'e')
        else:
            morphemes_new.append((word,tag))
            
    return morphemes_new,mapping


def split_adj(morphemes):
    morphemes_new = []
    mapping = ()
    
    word,tag = morphemes[0]
    if word.startswith('un') and  (adjstems.get(word[2:],0) > 0 or (not word.startswith('under') and not word.startswith('uni') and not word.startswith('unanim')  )):
        morphemes = [('un','PREF_NEG'),(word[2:],tag)] + morphemes[1:]
        #print(morphemes)
    
    for (word,tag) in morphemes:
        if tag == 'JJ' and word.endswith('ing') and verbstems.get(word[:-3],0) > 1:  
            morphemes_new.append((word[:-3],'VB'))
            morphemes_new.append(('ing','SUF_ING'))
        elif tag == 'JJ' and word.endswith('ing') and verbstems.get(word[:-3]+'e',0) > 1:  
            morphemes_new.append((word[:-3]+'e','VB'))
            morphemes_new.append(('ing','SUF_ING'))
            mapping = ('VB_VAR',word[:-3],word[:-3]+'e') 
        elif tag == 'JJ' and word in vbn2morphemes:
            morphemes_new.extend(vbn2morphemes[word])
        elif len(word) < 8:
            morphemes_new.append((word,tag))
        elif tag == 'JJ' and word[-4:] == 'able' and verbstems.get(word[:-4],0) > 5:  
            morphemes_new.append((word[:-4],'VB'))
            morphemes_new.append(('able','SUF_VBJJ'))
        elif tag == 'JJ' and word[-4:] == 'able' and verbstems.get(word[:-4]+'e',0) > 5:  
            morphemes_new.append((word[:-4],'VB_VAR'))
            morphemes_new.append(('able','SUF_VBJJ'))
        elif tag == 'JJ' and word[-5:] == 'iable' and verbstems.get(word[:-5]+'y',0) > 5:  
            morphemes_new.append((word[:-5]+'i','VB_VAR'))
            morphemes_new.append(('able','SUF_VBJJ'))
        elif tag == 'JJ_VAR' and word[-3:] == 'abl' and verbstems.get(word[:-3],0) > 5:  
            morphemes_new.append((word[:-3],'VB'))
            morphemes_new.append(('abl','SUF_VBJJ'))
        elif tag == 'JJ+VAR' and word[-3:] == 'able' and verbstems.get(word[:-3]+'e',0) > 5:  
            morphemes_new.append((word[:-3],'VB_VAR'))
            morphemes_new.append(('abl','SUF_VBJJ'))
        elif tag == 'JJ_VAR' and word[-3:] == 'iabl' and verbstems.get(word[:-4]+'y',0) > 5:  
            morphemes_new.append((word[:-3]+'i','VB_VAR'))
            morphemes_new.append(('able','SUF_VBJJ'))

        else:
            morphemes_new.append((word,tag))
            
    return morphemes_new,mapping

def postprocess_morphemes(morphlist):
    data = []
    
    for entry in morphlist:
        if len(entry) != 7:
            data.append(entry)
            continue
        sentnr,word,lemma,stem, tag, morphemes, subst = entry
        if tag in ["RB","QL"]:
            morphemes_new, subst_new = split_adv(morphemes)
            if len(subst_new) >= len(subst):
                subst = subst_new
            morphemes_new, _ = split_adj(morphemes_new)
            #morphemes_new, subst_new = split_adj(morphemes_new)
            #if len(subst_new) > len(subst):
            #    subst = subst_new
        elif tag in ["NNS","NN"]:    
            morphemes_new, subst_new = split_noun(morphemes)
            if len(subst_new) >= len(subst):
                subst = subst_new
        elif tag == 'JJ':    
            morphemes_new, subst_new = split_adj(morphemes)
            if len(subst_new) >= len(subst):
                subst = subst_new
        else:
            morphemes_new = morphemes
        data.append((sentnr,word,lemma,stem, tag, morphemes_new, subst))
        
    return data

Data = read_brown()

collect_morphemes(Data)
Data = postprocess_morphemes(Data) 

fout = codecs.open("labeledmorph_en.csv", "w","utf-8")

for word in Data:
    if len(word[-1]) == 3:
       print(*word,sep='\t',end='\n',file=fout)
    else:
       print(*word[:-1],sep='\t',end='\n',file=fout)
fout.close() 



##https://gist.github.com/nschneid/6476715
#http://korpus.uib.no/icame/manuals/BROWN/INDEX.HTM#bc6

