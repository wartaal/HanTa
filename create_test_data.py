import codecs
import re
from collections import Counter

#einbrechen, wiederholt, modifizieren, 'ifizier', mißverstehen
#Bossen/Boß
#kann




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
                #NN und NE werden zu häufig verwechselt in Dereko. Nicht ohne weiteres Nutzbar.                    
                #elif pos == 'NN' and len(word) > 2 and lemma != 'UNKNOWN' and lemma != 'unknown' and '|' not in lemma:
                #    data.append((-1,word,lemma,pos,[]))  
    return data


def read_nounlist(nounfile):
     data  = [] 
     with codecs.open(nounfile,'r','utf8') as f:
        for line in f:
            columns = line.split()
            if len(columns) == 3:
                sg,_,pl = columns
                data.append((-1,sg,sg,'NN',[])) 
                if sg != pl:
                  data.append((-1,pl,sg,'NN',[])) 
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
               "SUF_ADJ":"(?:er|es|en|em|e)?",
               "SUF_PPOSAT":"(?:er|es|en|em|e)?"
              }   

verbpref = 'ver|be|ent|er|zer|miss|hinter|über|wider|ge'



noncompound = ['abm', 'all', 'auf', 'aus', 'aus', 'bar', 'des', 'ei', 'ein', 'einzel', 'ente', 'fort', 'gesell', 'groß', 'gut', 'hau', 'hin', 'hoch', 'hypo', 'in', 'inn', 'innen', 'ion', 'kap', 'kombi', 'kommen', 'kont', 'lade', 'lan', 'lieb', 'los', 'miß', 'neu', 'ober', 'pro', 'rück', 'sau', 'saus', 'schaft', 'sein', 'selbst', 'ser', 'sfr', 'sol', 'sozial', 'spitz', 'super', 'super', 'tele', 'verb', 'vor', 'voraus', 'wohn', 'über','zustande']
# Wohnhaus, Wohn- und Geschäftshaus, Wanderurlaub, etc. V-NN Komposita lösen

not_nominalzed = ['wunde','junge','tote','tiefe','weite','weiche','spitze','note']

unsplitable = ["frustration","potentat","potentaten","uniform","kontakt","generation","werkstatt","werkstätt"]

#verbs with nonsplitable prefix and other verbs that buil pp without ge- 
def nonsplitprefix(lemma):
    if lemma in ['geben','geb','geh','gehen','gelten','gelt','gehr','geiz']:
        return False
    if lemma.startswith('bereit') and len(lemma) > 8:
        return False
    if re.fullmatch('(' + verbpref +').*',lemma):
        return True
    if lemma.endswith('ieren') or lemma.endswith('ier'): #works for stem as well as for lemma
        return True
    return False
    
    
def partikel2tag(lemma):
    if lemma in ['um', 'über', 'durch', 'unter', 'wieder']:
        return "PTKVZ_DUBIUM" #sometime separable, sometimes not
    else:
        return "PTKVZ_SEP"

    

def lemma_to_stem(word,lemma,pos):
    stem = lemma
    mapping = ()
    
    if pos.startswith("V"): # and lemma != 'sein':
        if lemma[-2:] == "en":
            stem = lemma[:-2]
        elif lemma[-1:] == "n":
            stem = lemma[:-1]
        if pos.startswith("VV") and nonsplitprefix(lemma) and not pos.startswith("NNvp"):
            pos = "VVnp"+ pos[2:]
    elif lemma.endswith("um") and pos == 'NN' and 'um' not in word[-4:] and 'üm' not in word[-4:]:  
        pos = 'NN_VAR' #CW 20220617
        stem = lemma[:-2]
        mapping = (pos,stem,lemma)
    elif lemma[-1] in "ao" and pos == 'NN' and word.endswith('en'):  #TODO ? pos --> NN_VAR???
        pos = 'NN_VAR' #CW 20220617
        stem = lemma[:-1]
        mapping = (pos,stem,lemma)
    elif lemma.endswith("el") and not word.startswith(lemma) and pos == 'ADJ':
        pos = 'ADJ_VAR'
        stem = lemma[:-2] + 'l'
        mapping = (pos,lemma[:-2] + 'l',lemma)
    elif lemma.endswith("euer") and  word.startswith(lemma[:-4]+'eur') and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-4]+'eur'
        mapping = (pos,lemma[:-4]+'eur',lemma)
    elif lemma.endswith("er") and not word.startswith(lemma) and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-2]
        mapping = (pos,lemma[:-2],lemma)
    elif lemma == 'anderer' and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-2]
        mapping = (pos,lemma[:-2],lemma)
    
    return pos,stem,mapping

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
            if nonsplitprefix(root):
                stem_tag = 'VVnp'+stem_tag[2:]
            morphemes =  [(ptkl,partikel2tag(ptkl)),("zu","PTKZU"),(root,stem_tag),(suffix,"SUF_IZU")]
            break
    
    
    return morphemes, ()
    
   
    
def split_ptkl_pp(word,stem,pos):
    mapping = ()
    pattern = '(.+?'+stem[-1]+'?)('+suffixtable['SUF_PP']+')'
    match = re.fullmatch(pattern,word)
    if not match or nonsplitprefix(stem):
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
                break
    if matched:
        morphemes = [(ptkl,partikel2tag(ptkl)),("ge","PREF_PP"),(root,stem_tag),(suffix,"SUF_PP")]
    else:    
        morphemes = []
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
        pattern = '^ge('+stem[0]+'.*?'+stem[-1]+'?)('+suffixtable['SUF_PP']+')$'
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

def split_pp_nopref(word,stem,pos):
    mapping = ()
    morphemes = []
    
   
    pattern = '(.*?'+stem[-1]+'?)('+suffixtable['SUF_PP']+')'
    match = re.fullmatch(pattern,word)
    if match and pos.startswith('VV') and nonsplitprefix(stem):  
        root = match[1]
        suffix = match[2]

        if not pos.startswith('VVnp'):
            pos = "VVnp"+ pos[2:]
        tag = pos
                
        if root != stem:
            tag = tag+"_VAR_PP"
            mapping = (tag,root,stem)
        morphemes.append((root,tag))
        morphemes.append((suffix,"SUF_PP"))

    return morphemes,mapping


def split_adj(word,stem,pos,feat):
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
            tag = pos  #"ADJ" #CW 20220808
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




def split_trunc(word,stem,feat):
    mapping = ()

    suffixpattern = suffixtable['SUF_NN'] 
 
    if word[-1] == '-':
        hyphen = '-'
    else:
        hyphen = ''

    pattern = stem+'('+suffixpattern+')?'+hyphen+'$'
    match = re.match(pattern,word)
                 
    if match:
        root = stem
        tag = 'NN'
        suffix = match[1]
      
    if not match:
        pattern = stem + '(.*)'+hyphen+'$'
        match = re.match(pattern,word)
        if match:
            root = stem
            tag = 'NN'
            suffix = match[1]
        
    if not match and suffixpattern != '.*':
        pattern = '^(.*?'+stem[-1]+'?)('+suffixpattern+')?'+hyphen+'$'
        match = re.match(pattern,word)
        if match:
            root = match[1]
            suffix = match[2]
            tag = "NN_VAR"
            mapping = (tag,root,stem)
        
    if not match:
        root = word
        if root[0] == stem[0] and root[-1] == stem[-1]:
            tag = "NN_VAR"
        else:
            tag = "NN_IRR"
        morphemes = [(root,tag)]
        mapping = (tag,root,stem)


    morphemes = [(root,tag)]
    
        
    if len(suffix) > 0:
       morphemes.append((suffix,'FUGE'))

        
        
    if len(hyphen) > 0: 
        morphemes.append((hyphen,'HYPHEN'))
        
    return morphemes,mapping


def split_word(word,stem,pos,feat):
    mapping = ()
    if pos[0] == 'V':
        suftag = feat
        tag = pos
    else:
        suftag = 'SUF_'+pos
        if suftag == 'SUF_NN_VAR':
            suftag = 'SUF_NN'
        tag = pos
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
      
    if not match:
        pattern = stem + '(.*)'
        match = re.match(pattern,word)
        if match:
            root = stem
            suffix = match[1]
        
    if not match and suffixpattern != '.*':
        pattern = '^(.*?'+stem[-1]+'?)('+suffixpattern+')$'
        match = re.match(pattern,word)
        if match:
            root = match[1]
            suffix = match[2]
            if feat == 'SUF_PP':
                tag = tag+"_VAR_PP"
                mapping = (tag,root,stem)
            elif len(suffix) == 0 or not stem.endswith(suffix):
                tag = tag+"_VAR"
                mapping = (tag,root,stem)
            else:
                match = False
                suffix = ""
        
    if not match and word != stem:
        root = word
        if root[0] == stem[0] and root[-1] == stem[-1]:
            if feat == 'SUF_PP':
                tag = tag+"_VAR_PP"
            else:
                tag = tag+"_VAR"
        else:
            tag = tag+"_IRR"
        morphemes = [(root,tag)]
        mapping = (tag,root,stem)


    morphemes = [(root,tag)]
    
        
    if len(suffix) > 0:
        morphemes.append((suffix,suftag))
        
       
        
    return morphemes,mapping


def find_morphemes(word,lemma,tag,feat):
    morphemes = []
    mapping = ()
    
    pos,base_feat = splittag(tag)
    
    word = word.lower()
    lemma = lemma.lower()
    
    if pos == "PTKVZ":
        morphemes = [(word,partikel2tag(lemma)),('','END_'+pos)]
    elif lemma == '--' or pos not in analyzable_classes:
        morphemes = [(word,pos),('','END_'+pos)]

        return morphemes, mapping

    pos,stem,mapping_stem = lemma_to_stem(word,lemma,pos)
        
    
    if lemma == 'sein' and pos == 'VA':
        if word == 'sein':
            morphemes = [('sei','VA'),('n','SUF_INF')] 
        elif word == 'sei':
            morphemes = [('sei','VA')] 
        else:
            morphemes = [(word,'VA_IRR')] 
            mapping = ('VA_IRR',word,'sei')
    elif tag == "VVIZU":
        morphemes,mapping  =  split_izu(word,stem,'VV')
    elif tag == "VVPP" or tag == "VAPP" or tag == "VMPP":
        morphemes,mapping  =  split_pp(word,stem,pos)
        if len(morphemes) == 0:
             morphemes,mapping  =  split_pp_nopref(word,stem,pos) 
        if len(morphemes) == 0:
             morphemes,mapping  =  split_ptkl_pp(word,stem,pos) 
    elif tag == "ADJA" or tag == "ADJD":
        morphemes, mapping = split_adj(word,stem,pos,feat)
    elif tag == "TRUNC":
        morphemes, mapping = split_trunc(word,stem,base_feat) 
    if len(morphemes) == 0:    
        try:
            morphemes, mapping = split_word(word,stem,pos,base_feat)
        except:
            print(word,stem,pos,base_feat)
           
        
    if len(mapping) == 0:
        mapping = mapping_stem

        
    if len(morphemes) > 0:       
        morphemes.append(('','END_'+tag))

    return morphemes, mapping


#Some methods to split morphemes into smaller ones. These splittings have to be done in a second cycle, since it requires knowledge about possible stems.
#some derivational morphology in this part  


def splitcompound(nounset,nounvarset,noun,startlen = 2):
    if noun not in unsplitable:
       for i in range(startlen,len(noun)-2):
           n1 = noun[:i]
           n1_noun = False
           n1_nounvar = False
           if nounset.get(n1,0) > 2 and n1 not in noncompound:
               n1_noun = True
           elif nounvarset.get(n1,0) > 5 and n1 not in noncompound:
               n1_nounvar = True
               
           if (len(n1) > 2 or n1 in ['öl'] or noun[2] == '-') and (n1_noun or n1_nounvar):
               n2 = noun[i:]
               if n1_noun: #nounvar requires Fuge (or plural) between compound parts 
                  sc_n2 = splitcompound(nounset,nounvarset,n2,3)
                  if len(sc_n2) > 0:
                      return [(n1,'NN')] + sc_n2
               
               if (noun[i] == 's' or (noun[i] == 'n' and noun[i-1] in "er") or noun[i] == '-') and nounset.get(noun[:i+1],0) < 5 :
                   glue = noun[i]
                   n2 = noun[i+1:]
                   sc_n2 = splitcompound(nounset,nounvarset,n2,3)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                       else:
                           ntag = 'NN_VAR'
                       return [(n1,ntag),(glue,'FUGE')] + sc_n2
               
               if (noun[i:i+2] == 'es' or noun[i:i+2] == 'en' or noun[i:i+2] == 'er') and noun[i-1] not in "ie" and nounset.get(noun[:i+2],0) < 5: #Trotzdem Falschzerlegung von Handwerkerszene
                   glue = noun[i:i+2]
                   n2 = noun[i+2:]
                   sc_n2 = splitcompound(nounset,nounvarset,n2,3)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                       else:
                           ntag = 'NN_VAR'
                       return [(n1,ntag),(glue,'FUGE')] + sc_n2
                    
               if noun[i] == 'e' and nounset.get(noun[:i+1],0) < 3 :
                   glue = noun[i]
                   n2 = noun[i+1:]
                   sc_n2 = splitcompound(nounset,nounvarset,n2,3)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                       else:
                           ntag = 'NN_VAR'
                       return [(n1,ntag),(glue,'FUGE')] + sc_n2                 
                    
                    
    if nounset.get(noun,0) > 2  and noun[0] != '-' and noun not in noncompound :
        return [(noun,'NN')]
    elif nounvarset.get(noun,0) > 0 and noun[0] != '-':
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
    parts = splitptklvb([p for p in partikel if partikel[p] > 10],verbstems+verbnpstems,stem,altstem)
    if len(parts) == 2:
        vtag = tag
        if nonsplitprefix(parts[1]) and not tag.startswith('VVnp'):
            vtag = 'VVnp'+tag[2:]
        else:
            vtag = tag
        result = [(parts[0],partikel2tag(parts[0])),(parts[1],vtag)] 
        if len(subst) == 3:
            start_stem = len(parts[0])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    else:        
        result = [(stem,tag)]
        
    return result,subst


def split_noun(stem,tag,subst): 
    result = []                
    if stem not in NEstems and stem not in unsplitable:
        result = splitcompound(nounstems,nounvarstems,stem)        
    if len(result) > 1:
        if len(subst) == 3:
            start_stem = sum([len(noun) for noun,_ in result[:-1]])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
            result = result[:-1] + [(result[-1][0],subst[0])] #changes NN to NN_VAR if necessarry
    else:
        result = [(stem,tag)]
        
    return result,subst
    
def split_adj_lemma(stem,tag,subst): 
    result = [(stem,tag)] 
    
    if "-" in stem:
        parts = stem.split('-',1)
        if parts[0] in adjstems and parts[1] in adjstems or (len(parts[0]) > 5 and len(parts[1]) > 5 and parts[0][-3:] == parts[1][-3:]):
            result = [(parts[0],'ADJ'),('-','HYPHEN'),(parts[1],'ADJ')]
            if len(subst) == 3 and len(result) > 1 :
                start_stem = len(parts[0])+1
                subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    elif stem.endswith('er') and stem not in ['ander','leer','inner','teuer','propper']:
        stem = stem[:-2] 
        if stem in adjstems:
            result = [(stem,'ADJ'),('er','SUF_ADJ')] 
        elif stem in NEstems:
            result = [(stem,'NE'),('er','SUF_DERIV_ADJ')]
  
    return result,subst
   

def split_adj_participle(stem,tag,mapping): 
    morphemes = [] 
    if stem.endswith('end'):
        if stem[:-3] in verbstems:
            morphemes = [(stem[:-3],'VV'),('end','PRESPART')]
        elif stem[:-3] in verbnpstems:
            morphemes = [(stem[:-3],'VVnp'),('end','PRESPART')]
    else:
        partikelpattern = '|'.join([p for p in partikel if partikel[p] > 10])
        
        pattern = '('+partikelpattern+')?(ge)?(.*?[aeouiüäö].*?)(' + suffixtable['SUF_PP'] +')'
        match = re.fullmatch(pattern,stem)
        if match and (match[3] in verbstems or match[3] in verbnpstems): 
            ptkl = match[1]
            prefix = match[2]
            root = match[3]
            suffix = match[4]
            if prefix or nonsplitprefix(root):
                if ptkl:
                    morphemes.append((ptkl,partikel2tag(ptkl)))
                if prefix:
                    morphemes.append((prefix,"PREF_PP"))
                vtag = verb2tag.get(root,"VV")
                if nonsplitprefix(root) and not vtag.startswith('VVnp'):
                    vtag = 'VVnp'+vtag[2:]
                morphemes.append((root,vtag))
                morphemes.append((suffix,"SUF_PP"))   

    if len(morphemes) == 0:
        morphemes = [(stem,tag)] 
            
    return morphemes,mapping

#TODO include PP as well (Der Vertraute)
def nominalized_adj(morphemes):
    m_nn = morphemes[0]
    m_suf = morphemes[1]
    if m_nn[0] in not_nominalzed:
        return morphemes
    elif m_nn[1] == 'NN' and m_suf[1] == 'SUF_NN' and m_nn[0][-1] == 'e' and m_nn[0][:-1] in adjstems:
        return [(m_nn[0][:-1],'ADJ'),('e'+m_suf[0],'SUF_ADJ'),morphemes[2]]
    elif m_nn[1] == 'NN' and m_suf[1] == 'SUF_NN' and m_nn[0][-1] == 'e' and m_suf[0] == 'm':
        adjstems.update([m_nn[0][:-1]])
        return [(m_nn[0][:-1],'ADJ'),('em','SUF_ADJ'),morphemes[2]]
    else:
        return morphemes

def postprocess_morphemes(morphlist):  
    data = []
   
    for entry in morphlist:
        if len(entry) != 6:
            data.append(entry)
            continue
        sentnr,word,lemma,tag, morphemes, subst = entry
        
        if tag == 'NN' and len(morphemes) == 3:
            morphemes = nominalized_adj(morphemes)
            
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
    global verbnpstems 
    global adjstems 
    global NEstems 
    global partikel
    global verb2tag
    
    partikel = Counter() 
    nounstems = Counter()
    nounvarstems = Counter()
    verbstems = Counter()
    verbnpstems = Counter()
    adjstems = Counter()
    NEstems = Counter()
    verb2tag = {}
 
    for entry in morphlist:
        sentnr,_,_,tag, morphemes, subst = entry
        if sentnr == -1:
            weight = 5
        else:
            weight = 1
        for i in range(len(morphemes)):
            m = morphemes[i]
            if len(m[0]) < 2:
                continue
            if m[1] == 'NN':
                nounstems.update(weight*[m[0]])
            if m[1] == 'NN_VAR':
                nounvarstems.update(weight*[m[0]])
            elif m[1] == 'VV' or m[1] == 'VV_VAR' or m[1] == 'VV_VAR_PP':
                verbstems.update(weight*[m[0]])
                verb2tag[m[0]] = m[1]
            elif m[1] == 'VVnp' or m[1] == 'VVnp_VAR' or m[1] == 'VVnp_VAR_PP':
                verbnpstems.update(weight*[m[0]])
                verb2tag[m[0]] = m[1]
            elif m[1].startswith('PTKVZ'):
                partikel.update(weight*[m[0]])
            elif m[1] == 'NE':
                NEstems.update(weight*[m[0]])
            elif m[1] == 'ADJ':
                adjstems.update(weight*[m[0]])     

    for n in list(nounstems):
        if n not in unsplitable and len(splitcompound(nounstems,nounvarstems,n)) > 1: ##Unschön, das wird jetzt doppelt aufgerufen
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





Data = read_tiger_words(r'tiger.16012013.conll09c')
Data += read_dereko_words(r'DeReKo-2014-II-MainArchive-STT.100000.freq')
Data += read_nounlist(r'substantive.txt')
# http://www.deutschonline.de/Deutsch/Grammatik/Plural.htm

morphdata = make_morphem_patterns(Data)

fout = codecs.open("labeledmorph_ger.csv", "w","utf-8")

for word in morphdata:
    print(*word,sep='\t',end='\n',file=fout)
fout.close() 




