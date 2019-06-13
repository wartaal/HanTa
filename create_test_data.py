import codecs
import re
from collections import Counter



def read_tiger_words(tiger_corpus_file):
    data = []
    sentnr = 1
    with codecs.open(tiger_corpus_file,'r','utf8') as f:
        for line in f:
            columns = line.split()
            if len(columns) == 15:
                word,lemma,pos,featstring =  columns[1], columns[2], columns[4], columns[6]
                if featstring == '_':
                    features = []
                else:
                    features = featstring.split('|')
                data.append((sentnr,word,lemma,pos,features))
            else:
                sentnr+= 1   
    return data
    
    
def read_dereko_words(dereko_file):
    data = []
    with codecs.open(dereko_file,'r','utf8') as f:
        for line in f:
            columns = line.split()
            if len(columns) == 4:
                word,lemma,pos =  columns[0].strip(), columns[1].strip(), columns[2].strip()
                if pos[0] == 'V' and lemma != 'UNKNOWN' and lemma != 'unknown' and '|' not in lemma:
                    data.append((-1,word,lemma,pos,[]))  
    return data


tagtable = {"VVFIN":("VV","SUF_FIN"),
            "VVINF":("VV","SUF_INF"),
            "VVIZU":("VV","SUF_INF"),
            "VVPP":("VV","SUF_PP"),
            "VVIMP":("VV","SUF_IMP"),
            "VAFIN":("VA","SUF_FIN"),
            "VAINF":("VA","SUF_INF"),
            "VAPP":("VA","SUF_PP"),
            "VAIMP":("VA","SUF_IMP"),
            "VMFIN":("VM","SUF_FIN"),
            "VMINF":("VM","SUF_INF"),
            "VMPP":("VM","SUF_PP"),
            "VMIMP":("VM","SUF_IMP"),
            "ADJA":("ADJ","A"),
            "ADJD":("ADJ","D")
           }

analyzable_classes = {"VV","VA","VM","ADJ","NE","NN","PPOSAT","TRUNC"}

suffixtable = {"SUF_FIN":"(?:t|e|st|n|en|et|est)?",
               "SUF_INF":"en|n",
               "SUF_IMP":"(?:t|et|e)?",
               "SUF_PP":"t|et|n|en",
               "SUF_NN":"(?:er|ern|en|n|s|es|e)?",
               "SUF_NE":"(?:s|es)?",
               "SUF_ADJ":"(?:er|es|en|em|e)?"
              }

verbpref = 'ver|be|ent|er|zer|miss|hinter|über'


def lemma_to_stem(word,lemma,pos):
    stem = lemma
    mapping = ()
    
    if pos.startswith("V"): # and lemma != 'sein':
        if lemma[-2:] == "en":
            stem = lemma[:-2]
        elif lemma[-1:] == "n":
            stem = lemma[:-1]
    elif lemma.endswith("er") and pos == 'NN' and 'er' not in word[-4:]: #Beamte/Beamter gelöst; Beamter/Beamter nicht! Beachte Vaters/Vater usw.
        stem = lemma[:-2]
    elif lemma.endswith("um") and pos == 'NN' and 'um' not in word[-4:]:  
        stem = lemma[:-2]
        mapping = (pos,stem,lemma)
    elif lemma[-1] in "ao" and pos == 'NN' and word.endswith('en'):  #TODO ? pos --> NN_VAR???
        stem = lemma[:-1]
        mapping = (pos,stem,lemma)
    elif lemma.endswith("el") and not word.startswith(lemma) and pos == 'ADJ':
        stem = lemma[:-2] + 'l'
        mapping = (pos,lemma[:-2] + 'l',lemma)
    elif lemma.endswith("er") and not word.startswith(lemma) and pos == 'ADJ' :
        stem = lemma[:-2]
        mapping = (pos,lemma[:-2],lemma)
    elif lemma == 'anderer' and pos == 'ADJ' :
        stem = lemma[:-2]
        mapping = (pos,lemma[:-2],lemma)
    
    return stem,mapping

def splittag(tag):
    pos,feat = tagtable.get(tag,(tag,""))
    return pos,feat






def findstem(word,stem,pos,feat):
    if word.startswith(stem):
        split = len(stem)
    else:
        split = -1

    return split 
    
    
def split_izu(word,stem,pos):
    morphemes =  []
    pattern = '^(.+?'+stem[-1]+'?)('+suffixtable['SUF_INF']+')$'
    match = re.match(pattern,word)
    word = match[1]
    suffix = match[2]
    for match in re.finditer('zu',word):
        start = match.start()
        end = match.end()
        if word[:start]+word[end:] == stem and start > 1:
            ptkl = word[:start]
            root = word[end:]
            stem_tag = pos
            morphemes =  [(ptkl,"PTKVZ"),("zu","PTKZU"),(root,stem_tag),(suffix,"SUF_IZU")]
            break
    
    
    return morphemes, ()
    
   
    
def split_ptkl_pp(word,stem,pos):
    mapping = ()
    pattern = '^(.+?'+stem[-1]+'?)('+suffixtable['SUF_PP']+')$'
    match = re.match(pattern,word)
    if not match:
        return [],()
    word = match[1]
    suffix = match[2]  
    matched = False
    for match in re.finditer('ge',word):
        start = match.start()
        end = match.end()
        if word[:start]+word[end:] == stem and re.match('.*[aeouiäöü].*',word[:end]):
            ptkl = word[:start]
            root = word[end:]
            stem_tag = pos
            matched = True
            break
    if not matched:# and 'ge' not in stem:
        for match in re.finditer('ge',word):
            start = match.start()
            end = match.end()
            ptkl = word[:start]
            if stem.startswith(ptkl) and re.match('.*[aeouiäöü].*',word[:end]):
                root = word[end:]
                stem_tag = pos+"_VAR_PP"
                mapping = (stem_tag,root,stem[len(ptkl):])
                matched = True
    if matched:
        morphemes = [(ptkl,"PTKVZ"),("ge","PREF_PP"),(root,stem_tag),(suffix,"SUF_PP")]
    else:
        morphemes = []
    return morphemes, mapping

def split_ptkl_pp_pref(word,stem,pos):
    mapping = ()
    morphemes =[]
    
    match = re.match('^(.*[aoueiüöä].*)('+ verbpref +')(.+)$',stem)
    if match:
        ptkl = match[1]
        prefix = match[2]
        stem_sub = match[3]
    
        pattern = '^'+ ptkl + prefix + '(.+)('+suffixtable['SUF_PP']+')$'
        match = re.match(pattern,word)
        if match:
            tag = pos
            root = match[1]
            suffix = match[2]
            if root != stem_sub:
                tag = pos+"_VAR_PP"
                mapping = (tag,root,stem_sub)
            morphemes = [(ptkl,"PTKVZ"),(prefix,"PREF_V"),(root,tag),(suffix,"SUF_PP")]
        
    return morphemes, mapping


def split_pp(word,stem,pos):
    mapping = ()
    pattern = '^ge'+stem+'('+suffixtable['SUF_PP']+')$'
    match = re.match(pattern,word)
    if match:
        root = stem
        suffix = match[1]
        tag = pos
    else:
        pattern = '^ge(.*?'+stem[-1]+'?)('+suffixtable['SUF_PP']+')$'
        match = re.match(pattern,word)
        if match:
            root = match[1]
            suffix = match[2]
            tag = pos+"_VAR_PP"
            mapping = (tag,root,stem)
    if match: 
        morphemes = [("ge","PREF_PP"),(root,tag),(suffix,"SUF_PP")]
    else:
        morphemes = []
    return morphemes,mapping

def split_pp_pref(word,stem,pos):
    mapping = ()
    morphemes = []
    
    match = re.match('^('+ verbpref +')(.*)$',stem)
    if match:
        prefix = match[1]
        stem_sub = match[2]
    
        pattern = '^'+ prefix +'(.+?)('+suffixtable['SUF_PP']+')$'
        match = re.match(pattern,word)
        if match:  
            root = match[1]
            suffix = match[2]
            tag = pos
            if root != stem_sub:
                tag = pos+"_VAR_PP"
                mapping = (tag,root,stem_sub)
            morphemes = [(prefix,"PREF_V"),(root,tag),(suffix,"SUF_PP")]

    return morphemes,mapping


def split_adj(word,stem,feat):
    mapping = ()
    suftag = 'SUF_ADJ'
    suffix = ""
    
    if 'degree=sup' in feat:
        degree = 2
    elif 'degree=comp' in feat:
        degree = 1
    else:
        degree = 0
    
    if degree == 2:
        suffixpattern = '(e?st)('+suffixtable[suftag] +')$'
        degreetag = "ADJ_SUP"
    elif degree == 1:
        suffixpattern = '(er)('+suffixtable[suftag] +')$'
        degreetag = "ADJ_COMP"
    else:
        suffixpattern = '('+suffixtable[suftag] +')$'
       
    pattern = '^' +stem+suffixpattern
    match = re.match(pattern,word)
                 
    if match:
        match = re.match(pattern,word)
        if match:
            mapping = ()
            tag = "ADJ"
            root = stem
            if degree == 0:
                suffix = match[1]
                degreesuff = ''
            else:
                degreesuffix = match[1]
                suffix = match[2]      
    else:
        pattern = '^(.*?'+stem[-1]+'?)'+suffixpattern
        match = re.match(pattern,word)
        if match:
            mapping = ("ADJ_VAR",match[1],stem)
            root = match[1]
            tag = "ADJ_VAR"
            if degree == 0:
                suffix = match[2]
                degreesuff = ''
            else:
                degreesuffix = match[2]
                suffix = match[3] 
               
    if match:   
        morphemes = [(root,tag)]
        if degree > 0:
            morphemes.append((degreesuffix,degreetag))
        if len(suffix) > 0:
            morphemes.append((suffix,suftag))
    else:
        root = word
        if root[0] == stem[0] and root[-1] == stem[-1] and degree == 0:
            tag = "ADJ_VAR"
        else:
            tag = "ADJ_IRR"
        morphemes = [(root,tag)]
        mapping = (tag,root,stem) 


    return morphemes,mapping




def split_word(word,stem,pos,feat):
    mapping = ()
    if pos[0] == 'V':
        suftag = feat
    else:
        suftag = 'SUF_'+pos
    suffix = ""
    if suftag in suffixtable:
        suffixpattern = suffixtable[suftag] 
    else:
        suffixpattern = '.*'
    pattern = stem+'('+suffixpattern+')$'
    match = re.match(pattern,word)
                 
    if match:
        root = stem
        suffix = match[1]
        tag = pos
      
    if not match:
        pattern = stem + '(.*)'
        match = re.match(pattern,word)
        if match:
            root = stem
            suffix = match[1]
            tag = pos
        
    if not match:
        pattern = '^(.*?'+stem[-1]+'?)('+suffixpattern+')$'
        match = re.match(pattern,word)
        if match:
            root = match[1]
            suffix = match[2]
            if feat == 'SUF_PP':
                tag = pos+"_VAR_PP"
            else:
                tag = pos+"_VAR"
            mapping = (tag,root,stem)
        
    if not match:
        root = word
        if root[0] == stem[0] and root[-1] == stem[-1]:
            if feat == 'SUF_PP':
                tag = pos+"_VAR_PP"
            else:
                tag = pos+"_VAR"
        else:
            tag = pos+"_IRR"
        morphemes = [(root,tag)]
        mapping = (tag,root,stem)

       
    if tag == 'TRUNC':
        tag = 'NN' 
         
    morphemes = [(root,tag)]
    
    if suffix  != '':
        if feat != '' and pos not in ['VV','VA','VM']:
             suftag = feat
        elif pos == 'TRUNC':
            if suffix.endswith('-'):
                if len(suffix) > 1:
                     morphemes.append((suffix[:-1],"FUGE"))
                suffix = '-'
                suftag = 'HYPHEN'
        
    
    if len(suffix) > 0:
        morphemes.append((suffix,suftag))
    return morphemes,mapping



def find_morphemes(word,lemma,tag,feat):
    morphemes = []
    mapping = ()
    
    pos,base_feat = splittag(tag)
    
    word = word.lower()
    lemma = lemma.lower()
    stem,mapping_stem = lemma_to_stem(word,lemma,pos)
        
    if lemma == '--' or pos not in analyzable_classes:
        morphemes = [(word,pos)]
    elif lemma == 'sein' and pos == 'VA':
        if word == 'sein':
            morphemes = [(word,'VA'),('n','SUF_INF')] 
        else:
            morphemes = [(word,'VA_IRR')] 
            mapping = ('VA_IRR',word,'sei')
    elif tag == "VVIZU":
        morphemes,mapping  =  split_izu(word,stem,'VV')
    elif tag == "VVPP" or tag == "VAPP" or tag == "VMPP":
        morphemes,mapping  =  split_pp(word,stem,pos)
        if len(morphemes) == 0:
             morphemes,mapping  =  split_pp_pref(word,stem,pos) 
        if len(morphemes) == 0:
             morphemes,mapping  =  split_ptkl_pp(word,stem,pos) 
        if len(morphemes) == 0:
             morphemes,mapping  =  split_ptkl_pp_pref(word,stem,pos) 
    elif tag == "ADJA" or tag == "ADJD":
        morphemes, mapping = split_adj(word,stem,feat)

    if len(morphemes) == 0:    
        morphemes, mapping = split_word(word,stem,pos,base_feat)
        
    if len(mapping) == 0:
        mapping = mapping_stem
        
    if len(morphemes) > 0:       
        morphemes.append(('','END_'+tag))

    return morphemes, mapping


#Some methods to split morphemes into smaller ones. These splittings have to be done in a second cycle, since it requires knowledge about possible stems.
#some derivational morphology in this part  



def splitcompound(nounset,nounvarset,noun):
    for i in range(3,len(noun)-3):
        n1 = noun[:i]
        #if n1 in nounset:
        if nounset.get(n1,0) > 4: 
            n2 = noun[i:]
            sc_n2 = splitcompound(nounset,nounvarset,n2)
            if len(sc_n2) > 0:
                return [(n1,'NN')] + sc_n2
            elif noun[i] == 's' or noun[i] == 'n' or noun[i] == '-':
                glue = noun[i]
                n2 = noun[i+1:]
                sc_n2 = splitcompound(nounset,nounvarset,n2)
                if len(sc_n2) > 0:
                    return [(n1,'NN'),(glue,'FUGE')] + sc_n2
            elif noun[i:i+2] == 'es' or noun[i:i+2] == 'en':
                glue = noun[i:i+2]
                n2 = noun[i+2:]
                sc_n2 = splitcompound(nounset,nounvarset,n2)
                if len(sc_n2) > 0:
                    return [(n1,'NN'),(glue,'FUGE')] + sc_n2
    if nounset.get(noun,0) > 4 and noun[0] != '-':
        return [(noun,'NN')]
    elif nounvarset.get(noun,0) > 4 and noun[0] != '-':
        return [(noun,'NN_VAR')]
    else:
        return []
    
def splitptklvb(ptklset,verbset,verb,alt):
    for i in range(len(verb)-2,1,-1):
        if verb[:i] in ptklset and verb[i:] in verbset:
        #if ptklcount[verb[:i]] > 5 and verbcount[verb[i:]] > 2:
            return (verb[:i],verb[i:])
        elif alt and verb[:i] in ptklset and alt[i:] in verbset:
        #elif alt and ptklcount[verb[:i]] > 5 and verbcount[alt[i:]] > 2:
            return (verb[:i],verb[i:])
    return []


def split_verb(stem,tag,subst):
    result = []
    if len(subst) == 3 and subst[2] == stem:
        altstem = subst[2]
    else:
        altstem = None
    parts = splitptklvb([p for p in partikel if partikel[p] > 10],verbstems,stem,altstem)
    if len(parts) == 2:
        result = [(parts[0],'PTKVZ'),(parts[1],tag)] 
        if len(subst) == 3:
            start_stem = len(parts[0])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    else:
        nonsepprefs = verbpref.split('|')
        parts = splitptklvb(nonsepprefs,verbstems,stem,altstem)
        if len(parts) == 2:
            result = [(parts[0],'PREF_V'),(parts[1],tag)] 
            if len(subst) == 3:
                start_stem = len(parts[0])
                subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
        else:        
            result = [(stem,tag)]
        
    return result,subst




def split_noun(stem,tag,subst): 
    result = []                
    if stem not in NEstems:
        result = splitcompound(nounstems,nounvarstems,stem)        
    else: 
        result = []
    if len(result) > 0:
        if len(subst) == 3 and len(result) > 1 :
            start_stem = sum([len(noun) for noun,_ in result[:-1]])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    else:
        result = [(stem,tag)]
        
    return result,subst
    
def split_adj_lemma(stem,tag,subst): 
    result = [(stem,tag)] 
    
    if stem.endswith('er') and stem != 'ander':
        stem = stem[:-2] 
        if stem in adjstems:
            result = [(stem,'ADJ'),('er','SUF_ADJ')] 
        elif stem in NEstems:
            result = [(stem,'NE'),('er','SUF_ADJ')]
  
    return result,subst
   
def split_adj_participle(stem,tag,mapping): 
    morphemes = [] 
    if stem.endswith('end'):
        if stem[:-3] in verbstems:
            morphemes = [(stem[:-3],'VV'),('end','PRESPART')]
    else:
        partikelpattern = '|'.join([p for p in partikel if partikel[p] > 10])
        
        pattern = '^('+partikelpattern+')?(ge|'+verbpref+')(.*[aeouiüäö].*)(' + suffixtable['SUF_PP'] +')$'
        match = re.match(pattern,stem)
        if match and match[3] in verbstems:
            ptkl = match[1]
            prefix = match[2]
            root = match[3]
            suffix = match[4]
            if prefix == "ge":
                preftag = "PREF_PP"
            else:
                preftag = "PREF_V"
            if ptkl:
                morphemes = [(ptkl,"PTKVZ"),(prefix,preftag),(root,"VV"),(suffix,"SUF_PP")]
            else:
                morphemes = [(prefix,preftag),(root,"VV"),(suffix,"SUF_PP")]
      

    if len(morphemes) == 0:
        morphemes = [(stem,tag)] 
            
    return morphemes,mapping



def postprocess_morphemes(morphlist):  
    data = []
   
    for entry in morphlist:
        if len(entry) != 6:
            data.append(entry)
            continue
        sentnr,word,lemma,tag, morphemes, subst = entry
        morph_new = []
        for i in range(len(morphemes)):
            m = morphemes[i]

            if m[1] == 'VV' or m[1] == 'VV_VAR':
                splitted,subst  = split_verb(m[0],m[1],subst)
                morph_new.extend(splitted) 
            elif m[1] == 'NN' or m[1] == 'NN_VAR':
                splitted,subst  = split_noun(m[0],m[1],subst)
                morph_new.extend(splitted) 
            elif m[1] == 'ADJ':
                splitted,subst  = split_adj_lemma(m[0],m[1],subst)
                if len(splitted) == 1:
                    splitted,subst  = split_adj_participle(m[0],m[1],subst)
                morph_new.extend(splitted) 
                
            else: 
                morph_new.append(m)
        data.append((sentnr,word,lemma,tag,morph_new,subst))

    return data    
 
def collect_morphemes(morphlist):
    global nounstems 
    global nounvarstems
    global verbstems 
    global adjstems 
    global NEstems 
    global partikel
    
    partikel = Counter() 
    nounstems = Counter()
    nounvarstems = Counter()
    verbstems = Counter()
    adjstems = Counter()
    NEstems = Counter()
 
    for entry in morphlist:
        _,_,_,tag, morphemes, subst = entry
        for i in range(len(morphemes)):
            m = morphemes[i]
            if m[1] == 'NN':
                nounstems.update([m[0]])
            if m[1] == 'NN_VAR':
                nounvarstems.update([m[0]])
            elif m[1] == 'VV' or m[1] == 'VV_VAR':
                verbstems.update([m[0]])
            elif m[1] == 'PTKVZ':
                partikel.update([m[0]])
            elif m[1] == 'NE':
                NEstems.update([m[0]])
            elif m[1] == 'ADJ':
                adjstems.update([m[0]])

             

    for n in list(nounstems):
        if len(splitcompound(nounstems,nounvarstems,n)) > 1: ##Unschön, das wird jetzt doppelt aufgerufen
            nounstems[n] = 0
            
            

def erroneous(morphemes,word,tag):
    error = False

    if tag == 'TRUNC' and morphemes[-2][1] != 'HYPHEN':
        error = True
    
    return error
    
def process_words(wordlist):
    data = []
    for sentnr,word,lemma,tag,feats in wordlist:
        morphemes,stemsub = find_morphemes(word,lemma,tag,feats)
        if not erroneous(morphemes,word,tag):
            data.append((sentnr,word,lemma,tag,morphemes,stemsub))
    return data




def make_morphem_patterns(wordlist):
    data = []
   
    data = process_words(wordlist)            
    collect_morphemes(data)
    data = postprocess_morphemes(data)   
          
    return data





Data = read_tiger_words(r'tiger.16012013.conll09')
Data += read_dereko_words(r'DeReKo-2014-II-MainArchive-STT.100000.freq')


morphdata = make_morphem_patterns(Data)

fout = codecs.open("labeledmorph_ger.csv", "w","utf-8")

for word in morphdata:
    print(*word,sep='\t',end='\n',file=fout)
fout.close() 




