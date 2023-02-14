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
                    if pos == 'VVINF':
                        match = re.fullmatch(r'(.+)zu(.+)',word)
                        if match and lemma == match[1]+match[2]:
                            pos = 'VVIZU'
                       
                    
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
            

tagtable = {"VV(FIN)":("VV","SUF_FIN"),
            "VV(INF)":("VV","SUF_INF"),
            "VV(IZU)":("VV","SUF_INF"),
            "VV(PP)":("VV","SUF_PP"),
            "VV(IMP)":("VV","SUF_IMP"),
            "VA(FIN)":("VA","SUF_FIN"),
            "VA(INF)":("VA","SUF_INF"),
            "VA(PP)":("VA","SUF_PP"),
            "VA(IMP)":("VA","SUF_IMP"),
            "VM(FIN)":("VM","SUF_FIN"),
            "VM(INF)":("VM","SUF_INF"),
            "VM(PP)":("VM","SUF_PP"),
            "VM(IMP)":("VM","SUF_IMP"),
            "NNI":("VV","SUF_INF"),
            "NNA":("NNA","SUF_ADJ"),
            "ADJ(A)":("ADJ","A"),
            "ADJ(D)":("ADJ","D")
           }
           
tagdict = {"VVFIN":"VV(FIN)",
            "VVINF":"VV(INF)",
            "VVIZU":"VV(IZU)",
            "VVPP":"VV(PP)",
            "VVIMP":"VV(IMP)",
            "VAFIN":"VA(FIN)",
            "VAINF":"VA(INF)",
            "VAPP":"VA(PP)",
            "VAIMP":"VA(IMP)",
            "VMFIN":"VM(FIN)",
            "VMINF":"VM(INF)",
            "VMPP":"VM(PP)",
            "VMIMP":"VM(IMP)",
            "ADJA":"ADJ(A)",
            "ADJD":"ADJ(D)"
           }

analyzable_classes = {"VV","VA","VM","ADJ","NE","NN","NNA","NNI","PPOSAT","PDAT","PIS","PIAT","TRUNC"}

suffixtable = {"SUF_FIN":"(?:t|e|st|n|en|et|est)?",
               "SUF_INF":"en|n",
               "SUF_IMP":"(?:t|et|e)?",
               "SUF_PP":"t|et|n|en",
               "SUF_NN":"(?:er|ern|en|n|s|es|e)?",
               "SUF_NE":"(?:s|es)?",
               "SUF_ADJ":"(?:er|es|en|em|e)?",
               "SUF_PPOSAT":"(?:er|es|en|em|e)?",
               "SUF_PRELS":"(?:er|es|en|em|e)?",
               "SUF_PRELAT":"(?:er|es|en|em|e)?",
               "SUF_PDAT":"(?:r|s|n|m|er|es|en|em|e)?",
               "SUF_PIS":"(?:r|s|n|m|er|es|en|em|e)?",
               "SUF_PIAT":"(?:r|s|n|m|er|es|en|em|e)?"
              }   

verbpref = 'ver|be|ent|er|zer|miss|hinter|über|wider|ge'



noncompound = ['abm', 'all', 'auf', 'aus', 'aus', 'bar', 'des', 'ei', 'ein', 'einzel', 'ente', 'fort', 'gesell', 'groß', 'gut', 'hau', 'hin', 'hoch', 'hypo', 'in', 'inn', 'innen', 'ion', 'kap', 'kombi', 'kommen', 'kont', 'lade', 'lan', 'lieb', 'los', 'miß', 'neu', 'ober', 'pro', 'rück', 'sau', 'saus', 'schaft', 'sein', 'selbst', 'ser', 'sfr', 'sol', 'sozial', 'spitz', 'super', 'super', 'tele', 'verb', 'vor', 'voraus', 'wohn', 'über','zustande']
# Wohnhaus, Wohn- und Geschäftshaus, Wanderurlaub, etc. V-NN Komposita lösen

#some nouns that can loose their final 'e' in a compund
noun_elis = ['kontroll','miet','straf','grenz','lehr','schul','hochschul','kron','erd','buß','woll','sprach','stimm','eck','kirch','farb','ehr','filial','wochenend','end','münz']

not_nominalized = ['wunde','junge','tiefe','weite','weiche','spitze','note']

noverbstems = ['statt','sonder','sonn','weih','wett']

unsplitable = ["frustration","potentat","potentaten","uniform","kontakt","generation","werkstatt","werkstätt","schienbein","wegweiser"]

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

    

def lemma_to_stem(word,lemma,pos,tag):
    stem = lemma
    mapping = ()
    
    if tag == "NNA":
        if lemma[-1:] == "e":
            stem = lemma[:-1]
    
    if pos.startswith("V"): # and lemma != 'sein':
        if lemma[-2:] == "en":
            stem = lemma[:-2]
        elif lemma[-1:] == "n":
            stem = lemma[:-1]
        if pos.startswith("VV") and nonsplitprefix(lemma) and not pos.startswith("NNvp"):
            pos = "VVnp"+ pos[2:]
    elif lemma.endswith("um") and pos == 'NN' and 'um' not in word[-5:] and 'üm' not in word[-5:]:  
        #pos = 'NN_VAR' #CW 20220617
        stem = lemma[:-2]
        #mapping = (pos,lemma[:-2],lemma)
    elif lemma[-1] in "ao" and lemma[-2:] != "ao" and pos == 'NN' and word.endswith('en'):  #Firma, Konto #TODO ? pos --> NN_VAR??? 
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
    elif lemma.endswith("auer") and  word.startswith(lemma[:-4]+'aur') and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-4]+'aur'
        mapping = (pos,lemma[:-4]+'aur',lemma)
    elif lemma.endswith("ster") and  word.startswith(lemma[:-4]+'str') and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-4]+'str'
        mapping = (pos,lemma[:-4]+'str',lemma)
    elif lemma.endswith("ger") and  word.startswith(lemma[:-3]+'gr') and pos == 'ADJ' :
        pos = 'ADJ_VAR'
        stem = lemma[:-3]+'gr'
        mapping = (pos,lemma[:-3]+'gr',lemma)
    elif lemma == 'eher' and word == 'ehesten':
        pos = 'ADJ_VAR'
        stem = 'ehe'  
        mapping = (pos,'ehe','eher')        
    elif lemma.endswith("er") and not word.startswith(lemma) and pos in ['ADJ','PIS','PIAT'] :
        #pos = 'ADJ_VAR'
        stem = lemma[:-2]
        #mapping = (pos,lemma[:-2],lemma)
    elif lemma == 'anderer' and pos in ['ADJ','PIS','PIAT'] :
        #pos = 'ADJ_VAR'
        stem = lemma[:-2]
        #mapping = (pos,lemma[:-2],lemma)
    
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
        if word[:start]+word[end:] == stem and re.match('.*[aeouiäöüy].*',word[:end]):
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
            if stem.startswith(ptkl) and re.match('.*[aeouiäöüy].*',word[:end]):
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
    root = word 
    
    if pos == 'NNA':
        tag = 'ADJ'
    else:
        tag = pos
    
    if 'degree=sup' in feat:
        degree = 2
    elif 'degree=comp' in feat:
        degree = 1
    else:
        degree = 0
    
    if degree == 2:
        suffixpattern = '(e?st)('+suffixtable[suftag] +')'
        degreetag = "ADJ_SUP"
    elif degree == 1:
        suffixpattern = '(er)('+suffixtable[suftag] +')'
        degreetag = "ADJ_COMP"
    else:
        suffixpattern = '('+suffixtable[suftag] +')'
       
    pattern = stem+suffixpattern
    match = re.fullmatch(pattern,word)
                 
    if match:
        match = re.fullmatch(pattern,word)
        if match:
            mapping = () 
            root = stem
            if degree == 0:
                suffix = match[1]
                degreesuff = ''
            else:
                degreesuffix = match[1]
                suffix = match[2]    
    elif pos == 'NNA':
        pattern = stem+'(e?st|er)('+suffixtable[suftag] +')'
        match = re.fullmatch(pattern,word)
        if match:
            mapping = ()
            root = stem
            degreesuffix = match[1]
            suffix = match[2] 
            if degreesuffix[-1] == 'r':
               degreetag = "ADJ_COMP"
               degree = 1
            else:
               degreetag = "ADJ_SUP"
               degree = 2       
    
    if not match:
        pattern = '(.*?'+stem[-1]+'?)'+suffixpattern
        match = re.fullmatch(pattern,word)
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
        
    morphemes = []
    if word.startswith('un') and not word.startswith('unter') and not word.startswith('univ') and not word.startswith('ungari'):
        morphemes = [('un','PREF_NEG')]  
        root = root[2:]  
        stem = stem[2:]         
         
    if match:   
        morphemes.append((root,tag))
        if degree > 0:
            morphemes.append((degreesuffix,degreetag))
        if len(suffix) > 0:
            morphemes.append((suffix,suftag))
    else:
              
        if root[0] == stem[0] and root[-1] == stem[-1] and degree == 0:
            tag = "ADJ_VAR"
        else:
            tag = "ADJ_IRR"
        morphemes.append((root,tag))
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
    match = re.fullmatch(pattern,word)
                 
    if match:
        root = stem
        tag = 'TRUNC'
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


def split_word(word,word_cased,stem,pos,feat):
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
        pattern = '(.*?'+stem[-1]+'?)('+suffixpattern+')'
        match = re.fullmatch(pattern,word)
        if match:
            root = match[1]
            suffix = match[2]
            if feat == 'SUF_PP':
                tag = tag+"_VAR_PP"
                mapping = (tag,root,stem)
            elif len(suffix) == 0 or not stem.endswith(suffix):
                if suffix == 'ern' and stem.endswith('ere'): #repair wrong split of Innern
                    root +='er'
                    suffix = 'n'
                if tag[:-4] != '_VAR':
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
            elif tag[:-4] != '_VAR':
                tag = tag+"_VAR"
        else:
            tag = tag+"_IRR"
        morphemes = [(root,tag)]
        mapping = (tag,root,stem)


    if tag == 'NN' and len(word) < 5 and (word_cased.isupper() or re.fullmatch(r'[^aeouiäöüy\-][^aeouiäöüy]*[^aeouiäöüyy\-]',word)) :
        tag = 'ACR_NN'
    if tag == 'NE' and 1 < len(word) < 5 and (word_cased.isupper() or re.fullmatch(r'[^aeouiäöüy\-][^aeouiäöüy]*[^aeouiäöü\-]',word)) :
        tag = 'ACR_NE'

    morphemes = [(root,tag)]
    
        
    if len(suffix) > 0:
        morphemes.append((suffix,suftag))
        
       
        
    return morphemes,mapping


def find_morphemes(word,lemma,tag,feat):
    morphemes = []
    mapping = ()
    
    pos,base_feat = splittag(tag)
    
    word_cased = word
    word = word.lower()
    lemma = lemma.lower()
    
    if pos == "PTKVZ":
        morphemes = [(word,partikel2tag(lemma))]
    elif pos not in analyzable_classes:
        morphemes = [(word.lower(),pos)]
        if not lemma.startswith(word.lower()):
            mapping = (pos,word.lower(),lemma)
        return lemma, morphemes, mapping 
    elif lemma == '--'  or lemma == '-':
        morphemes = [(word.lower(),pos)]
        return lemma, morphemes, mapping

    pos,stem,mapping_stem = lemma_to_stem(word,lemma,pos,tag)
    
    if lemma == 'sein' and pos == 'VA':
        if word == 'sein':
            morphemes = [('sei','VA'),('n','SUF_INF')] 
        elif word == 'sei':
            morphemes = [('sei','VA')] 
        else:
            morphemes = [(word,'VA_IRR')] 
            mapping = ('VA_IRR',word,'sei')
    elif tag == "VVIZU" or tag == "VV(IZU)":
        morphemes,mapping  =  split_izu(word,stem,'VV')
    elif tag == "VVPP" or tag == "VAPP" or tag == "VMPP" or tag == "VV(PP)" or tag == "VA(PP)" or tag == "VM(PP)" :
        morphemes,mapping  =  split_pp(word,stem,pos)
        if len(morphemes) == 0:
             morphemes,mapping  =  split_pp_nopref(word,stem,pos) 
        if len(morphemes) == 0:
             morphemes,mapping  =  split_ptkl_pp(word,stem,pos) 
    elif tag == "ADJ(A)" and word == stem  and re.fullmatch(r'[0-9]+\.',word):
        morphemes =  [(word,'ORD_ABR')]
    elif tag == "ADJ(A)" and word == stem:
        morphemes = [(word,'ADJ_INVAR')]
    elif tag == "ADJA" or tag == "ADJD" or tag == "ADJ(A)" or tag == "ADJ(D)" or tag == "NNA":
        morphemes, mapping = split_adj(word,stem,pos,feat)
    elif tag == "TRUNC":
        morphemes, mapping = split_trunc(word,stem,base_feat) 
    elif tag == 'NN' and len(word) == 1:
        morphemes = [(word,'SYMB')]
    elif word.startswith("http://") or  word.startswith("https://") :
        morphemes = [(word,'URL')]
    
        
    if len(morphemes) == 0:    
        try:
            morphemes, mapping = split_word(word,word_cased,stem,pos,base_feat)
        except:
            print(word,stem,pos,base_feat)
           
        
    if len(mapping) == 0:
        mapping = mapping_stem

        
    #if len(morphemes) > 0:       
    #    morphemes.append(('','END_'+tag))

    return stem, morphemes, mapping


#Some methods to split morphemes into smaller ones. These splittings have to be done in a second cycle, since it requires knowledge about possible stems.
#some derivational morphology in this part  



def acronym(lemma,word):
    if len(word) > 4:
        return False
    elif re.fullmatch(r'[^aeouiäöüy\-][^aeouiäöüy]*[^aeouiäöüy\-]',word):
        return True
    elif word.upper() in lemma:
        return True
    else:
        return False

#TODO Landbewirtschaftung, Buchprüfer, Hungerauflage, Ausweiskontrolle, Wohnraumversorgung 
#TODO Abgeordnetenhaus
def splitcompound(nounset,nounvarset,propernounset,lemma,noun,startlen = 2,letterbefore=False):
    if noun not in unsplitable:
       for i in range(startlen,len(noun)-2):
           n1 = noun[:i]
           n1_noun = False
           n1_nounvar = False
           n1_propernoun = False
           n1_acro = False
           n1_nounelis = False
           n1_card = False
           n1_nominalized = False
           if (n1 in verbstems or n1 in verbnpstems) and noun[i:].startswith('ende'):
               continue
           if nounset.get(n1,0) > 2 and n1 not in noncompound:
               n1_noun = True
           elif nounvarset.get(n1,0) > 5 and n1 not in noncompound:
               n1_nounvar = True
           elif noun[i] != 'e' and n1 in noun_elis:
               n1_nounelis = True
           elif noun[i] == '-' and re.fullmatch(r'[0-9]*',n1):
               n1_card = True    
           elif noun[i] == '-' and propernounset.get(n1,0) > 0 :
               n1_propernoun = True
           elif noun[i] == '-' and acronym(lemma,n1) and not letterbefore:
               n1_acro = True
           elif nominalized.get(n1,0) > 2:
               n1_nominalized = True
               
           if (len(n1) > 2 or n1 in ['öl'] or noun[2] == '-') and (n1_noun or n1_nounvar or n1_propernoun or n1_nounelis or n1_card  or n1_acro or n1_nominalized):
               n2 = noun[i:]
               if n1_noun: #nounvar requires Fuge (or plural) between compound parts 
                  if(n1 == 'verhör'):
                      print(pos,lemma,n2)
                  sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3, True)
                  if len(sc_n2) > 0:
                      return [(n1,'NN')] + sc_n2
               if n1_nounelis: 
                  sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3, True)
                  if len(sc_n2) > 0:
                      return [(n1,'NN_VAR_EL')] + sc_n2         
               if noun[i] == '-':
                   n2 = noun[i+1:]
                   sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3, False)
                   if n1_card:
                       ntag = 'CARD'
                   elif n1_acro:
                       if n1 in mostcommontag and mostcommontag[n1] == 'ACR_NN':
                           ntag = 'ACR_NN'
                       else:
                          ntag = 'ACR_NE'
                   elif n1_propernoun:
                       ntag = 'NE'
                   elif n1_noun:
                       ntag = 'NN'
                   elif n1_nounelis:
                       ntag = 'NN_VAR_EL'
                   elif n1_nominalized: #TODO adj-nn woanders behandeln
                        ntag = 'ADJ'
                        #print(noun)
                   else:
                       ntag = 'NN_VAR'
                   if len(sc_n2) > 0:
                       return [(n1,ntag),('-','HYPHEN')] + sc_n2
                   else:
                       return [(n1,ntag),('-','HYPHEN'),(n2,'NN')] 
               if n1_nominalized and noun[i:i+2] == 'en':
                   morph_adj,_  = split_adj_lemma(n1,'ADJ',())
                   n2 = noun[i+2:]
                   sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3, True)
                   if len(sc_n2) > 0:
                      return morph_adj + [('en','SUF_ADJ_NN')] + sc_n2
               #if (noun[i] == 's' or (noun[i] == 'n' and noun[i-1] in "er")) and not n1_nounelis and nounset.get(noun[:i+1],0) < 5 :
               if (noun[i] == 's' or (noun[i] == 'n' and noun[i-1] in "er")) and (n1_noun or n1_nounvar ) and nounset.get(noun[:i+1],0) < 5 :
                   glue = noun[i]
                   if noun[i+1] == '-': # Das ist echter Raketen-Wissenschaft!
                       n2 = noun[i+2:]
                       hyphen = [('-','HYPHEN')]
                   else:
                       n2 = noun[i+1:]
                       hyphen = []
                   sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3,True)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                       else:
                           ntag = 'NN_VAR'
                       return [(n1,ntag),(glue,'FUGE')] + hyphen + sc_n2
               
               if (noun[i:i+2] == 'es' or noun[i:i+2] == 'en' or noun[i:i+2] == 'er') and noun[i-1] not in "ie" and nounset.get(noun[:i+2],0) < 5 and ( n1_noun or n1_nounvar or n1_nominalized): #Trotzdem Falschzerlegung von Handwerkerszene
                   glue = noun[i:i+2]
                   if noun[i+2] == '-': # Das ist echter Raketen-Wissenschaft!
                       n2 = noun[i+3:]
                       hyphen = [('-','HYPHEN')]
                   else:
                       n2 = noun[i+2:]
                       hyphen = []
                   sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3,True)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                           gluetag = 'FUGE'
                       elif n1_nominalized:
                           ntag = 'ADJ'
                           gluetag = 'SUF_ADJ_NN'
                       else: # n1_nounvar:
                           ntag = 'NN_VAR'
                           gluetag = 'FUGE'

                       return [(n1,ntag),(glue,gluetag)] + hyphen + sc_n2
                    
               if noun[i] == 'e' and nounset.get(noun[:i+1],0) < 3 and (n1_noun or n1_nounvar):
                   glue = noun[i]
                   if noun[i+1] == '-': # Das ist echter Raketen-Wissenschaft!
                       n2 = noun[i+2:]
                       hyphen = [('-','HYPHEN')]
                   else:
                       n2 = noun[i+1:]
                       hyphen = []
                   sc_n2 = splitcompound(nounset,nounvarset,{},lemma,n2,3,True)
                   if len(sc_n2) > 0:
                       if n1_noun:
                           ntag = 'NN'
                       else: # n1_nounvar:
                           ntag = 'NN_VAR'

                       return [(n1,ntag),(glue,'FUGE')] + hyphen + sc_n2                 
                    
                    
    if nounset.get(noun,0) > 2  and noun[0] != '-' and noun not in noncompound :
        return [(noun,'NN')]
    elif nounvarset.get(noun,0) > 0 and noun[0] != '-':
        return [(noun,'NN_VAR')]
    elif mostcommontag.get(noun,'') == 'ACR_NN' and not letterbefore:
        return [(noun,'ACR_NN')]
    elif mostcommontag.get(noun,'') == 'ACR_NE' and not letterbefore:
        return [(noun,'ACR_NE')]
    elif noun[-1] == 'e' and noun[:-1] in nominalized:
        return [(noun[:-1],'ADJ'),('e','SUF_ADJ')]
    elif noun[-2:] in ['es','er','em','en'] and noun[:-2] in nominalized:
        return [(noun[:-2],'ADJ'),(noun[-2:],'SUF_ADJ')]
    else:
        return []
        
    
#TODO n1 darf kein Substantiv sein    
def splitverbnouncompound(verbset,verbnpset,nounset,nounvarset,noun,startlen = 4):
    if noun not in unsplitable:
       for i in range(startlen,len(noun)-2):
           n1 = noun[:i]
           n2 = noun[i:]
           n1_verb = False
           if verbset.get(n1,0) > 5:
               n1_verb = True
               vvtag =  'VV'
           elif verbnpset.get(n1,0) > 5:
               n1_verb = True
               vvtag =  'VVnp'
           
           if n1_verb and n1 not in noverbstems and n1 not in adjstems and n1 not in nounstems and n1 not in nounvarstems:
               sc_n2 = splitcompound(nounset,nounvarset,{},n2,n2,3,True)
               if len(sc_n2) > 1:
                   return [(n1,vvtag)]+sc_n2
               elif n2 in nounset:
                   return [(n1,vvtag),(n2,'NN')]
               elif n2 in nounvarset:
                   return [(n1,vvtag),(n2,'NN_VAR')]
    return []
           

def split_compound_nna(noun,tag,subst): 

    sc_n1 = []
    fuge = []
    head = noun
      
    for i in range(len(noun)-3,3,-1):
        n2 = noun[i:]
                    
        if nominalized.get(n2,0) > 2:
            hyphen = False
            if noun[i-1] == '-':
               n1 = noun[:i-1]
               hyphen = True
            else:
               n1 = noun[:i]
            sc_n1 = splitcompound(nounstems,nounvarstems,{},n1,n1,3,True)
            if len(sc_n1) > 0:
                head = n2
                if hyphen:
                    sc_n1 += [('-','HYPHEN')]
                break
            elif hyphen:
               head = n2
               n1tag = mostcommontag.get(n1,'NN')
               sc_n1 = [(n1,n1tag),('-','HYPHEN')] 
                
            if noun[i-1] in "sn":
               n1 = noun[:i-1]
               sc_n1 = splitcompound(nounstems,nounvarstems,{},n1,n1,3,True)
               if len(sc_n1) > 0:
                  head = n2
                  fuge = [(noun[i-1],'FUGE')]
                  break
            if noun[i-2:i] == "en":
               n1 = noun[:i-2]
               sc_n1 = splitcompound(nounstems,nounvarstems,{},n1,n1,3,True)
               if len(sc_n1) > 0:
                  head = n2
                  fuge = [('en','FUGE')]
                  break
  
                
    sc_n2,subst  = split_adj_lemma(head,tag,subst)       
    
    return sc_n1 + fuge + sc_n2, subst
   
    
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



def deriv_noun(stem,tag,subst): 

    if stem.endswith('chen') and stem[:-4] in nounvarstems :
        return [(stem[:-4],'NN_VAR'),('chen','SUF_DIM')], subst
    elif stem.endswith('chen') and  stem[:-4] in nounstems  and stem not in ['pochen','groschen','erlöschen']:
        return [(stem[:-4],'NN'),('chen','SUF_DIM')], subst
    elif stem.endswith('in') and len(stem) > 5 and stem[-3] != 'e' and stem[:-2] in nounstems:
        return [(stem[:-2],'NN'),('in','SUF_FEM')], subst
    elif stem.endswith('in') and len(stem) > 5 and stem[-3] != 'e' and stem[:-2] in nounvarstems:
        return [(stem[:-2],'NN_VAR'),('in','SUF_FEM')], subst
    elif stem.endswith('in') and len(stem) > 5 and stem[-3] != 'e' and stem[:-2]+'e' in nounstems:
        return [(stem[:-2],'NN_VAR'),('in','SUF_FEM')], ('NN_VAR',stem[:-2],stem[:-2]+'e' )

    return [(stem,tag)], subst

    
def split_noun(stem,tag,subst,lemma): 
    morphemes = [] 
    
    if stem not in NEstems and stem not in unsplitable and len(stem) > 3:
        morphemes = splitcompound(nounstems,nounvarstems,NEstems,lemma,stem)         
        if len(morphemes) <= 1:
            morphemes = splitverbnouncompound(verbstems,verbnpstems,nounstems,nounvarstems,stem)   
        if  len(morphemes) <= 1 and '-' in stem:
            parts = stem.split('-')
            morphemes = []
            for p in parts[:-1]:
                if len(p) > 1 and p in mostcommontag:
                   morphemes += [(p,mostcommontag[p]),('-','HYPHEN')]
            if len(morphemes) == 2 * (len(parts)-1) and len(parts[-1]) > 2:
                morphemes += [(parts[-1],tag)]
            else:
                morphemes = []
    if len(morphemes) > 1:
        if len(subst) == 3:
            start_stem = sum([len(noun) for noun,_ in morphemes[:-1]])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
            morphemes = morphemes[:-1] + [(morphemes[-1][0],subst[0])] #changes NN to NN_VAR if necessarry
    else:
        morphemes = [(stem,tag)]
      
    result = []
    for m in morphemes:
        morphemes_sub, subst = deriv_noun(m[0],m[1],subst)
        if len(morphemes_sub) > 1:
            for ms in morphemes_sub:
               if ms[1] in ['NN','NN_VAR']:
                   subcomp = splitcompound(nounstems,nounvarstems,NEstems,lemma,ms[0])  
                   if len(subcomp) > 1:
                       result.extend(subcomp)
                   else:
                       result.append(ms)
               else:
                   result.append(ms)
        else:
            result.extend(morphemes_sub)
    
    return result,subst
    
def split_adj_lemma(stem,tag,subst): 
    result = [] 
    suffix = []
    stemtag = tag
    
    if "-" in stem:
        parts = stem.split('-',1)
        if parts[0] in adjstems and parts[1] in adjstems or (len(parts[0]) > 5 and len(parts[1]) > 5 and parts[0][-3:] == parts[1][-3:]):
            result = [(parts[0],'ADJ'),('-','HYPHEN')] 
            stem = parts[1]
            if len(subst) == 3 and len(result) > 1 :
                start_stem = len(parts[0])+1
                if subst[1][start_stem:] != subst[2][start_stem:]:
                    subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
                else:
                    subst = ()
    elif stem.endswith('er') and stem not in ['ander','leer','inner','teuer','propper','lauter','sauer','illuster','leger','sinister','bieder',]:
        if stem[:-2]  in NEstems:
            stem = stem[:-2] 
            stemtag = 'NE'
            suffix = [('er','SUF_DERIV_ADJ')]
            subst = () #TODO will work in almost all cases. Evt. adjust the mapping
        elif stem[:-2]  in adjstems:
            stem = stem[:-2] 
            suffix = [('er','ADJ_COMP')]
            subst = () 
    elif stem.endswith('st') and stem[:-2] in adjstems and stem[:-2] not in ['drei']:
        stem = stem[:-2] 
        suffix = [('st','ADJ_SUP')]
        subst = () 
  
    if stemtag == 'NE':
        stem_morphemes = [(stem,stemtag)]
    else:
        stem_morphemes,subst  = split_adj_participle(stem,stemtag,subst)
        if len(stem_morphemes) == 1:
            stem_morphemes,subst = deriv_adj(stem,stemtag,subst) 
        
    return result+stem_morphemes+suffix,subst
   

def deriv_adj(stem,tag,mapping): 
    morphemes = [(stem,tag)] 
    
    if stem.endswith('bar') and verbstems.get(stem[:-3],0) > 2:
        morphemes = [(stem[:-3],'VV'),('bar','SUF_DERIV_VV_ADJ')]
        mapping = ()
    elif stem.endswith('bar') and verbnpstems.get(stem[:-3],0) > 2:
        morphemes = [(stem[:-3],'VVnp'),('bar','SUF_DERIV_VV_ADJ')]
        mapping = ()
    
    return morphemes, mapping
    
def split_adj_participle(stem,tag,mapping): 
    morphemes = [] 
    if stem.endswith('end'):
        if stem[:-3] in verbstems:
            morphemes = [(stem[:-3],'VV'),('end','PRESPART')]
        elif stem[:-3] in verbnpstems:
            morphemes = [(stem[:-3],'VVnp'),('end','PRESPART')]
    elif stem.endswith('nd'):
        if stem[:-2] in verbstems:
            morphemes = [(stem[:-2],'VV'),('nd','PRESPART')]
        elif stem[:-2] in verbnpstems:
            morphemes = [(stem[:-2],'VVnp'),('nd','PRESPART')]
    else:
        partikelpattern = '|'.join([p for p in partikel if partikel[p] > 10])
        
        pattern = '('+partikelpattern+')?(ge)?(.*?[aeouiüäöy].*?)(' + suffixtable['SUF_PP'] +')'
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

    if len(morphemes) > 1:
        mapping == ()
    elif len(morphemes) == 0:
        morphemes = [(stem,tag)] 
            
    return morphemes,mapping
   
    
def postprocess_morphemes(morphlist):  
    data = []
   
    for entry in morphlist:
        if len(entry) != 7:
            data.append(entry)
            continue
        sentnr,word,lemma,stem, tag, morphemes, subst = entry      
            
        morph_new = []
        for i in range(len(morphemes)):
            m = morphemes[i]

            if m[1] == 'VV' or m[1] == 'VV_VAR':
                splitted,subst  = split_verb(m[0],m[1],subst)
                morph_new.extend(splitted) 
            elif m[1] == 'NN' or m[1] == 'NN_VAR' or m[1] == 'NNA' and len(m[0]) > 2:
                splitted,subst  = split_noun(m[0],m[1],subst,lemma)
                morph_new.extend(splitted) 
            elif (m[1] == 'ADJ' or m[1] == 'ADJ_VAR') and tag == 'NNA': # and adjstems.get(m[0],0) > 2:
                splitted, subst  = split_compound_nna(m[0],m[1],subst)
                morph_new.extend(splitted) 
            elif (m[1] == 'ADJ' or m[1] == 'ADJ_VAR'):
                splitted,subst  = split_adj_lemma(m[0],m[1],subst)          
                morph_new.extend(splitted)    
            elif m[1] == 'TRUNC':
                for fuge in ['','n','s','en','es']:
                    if m[0].endswith(fuge):
                         if fuge == '':
                             trunc = m[0]
                         else:
                             trunc = m[0][:-len(fuge)]
                         compoundmorphemes = splitcompound(nounstems,nounvarstems,NEstems,lemma,trunc)  
                         if len(compoundmorphemes) > 0:
                            break
                if len(compoundmorphemes) > 0:
                    morph_new.extend(compoundmorphemes)
                    if len(fuge) > 0:
                        morph_new.append((fuge,'FUGE'))
                else:  
                    if re.fullmatch('[0-9]+',m[0]):
                        mtag = 'CARD'
                    elif m[0] in mostcommontag:
                        mtag = mostcommontag[m[0]]
                    elif m[0] in noun_elis:
                        mtag = 'NN_VAR_ELIS'
                        subst = ('NN_VAR_ELIS',m[0],m[0]+'e')
                    else:
                        mtag = 'TRUNC'
                    morph_new.append((m[0],mtag))
            else: 
                morph_new.append(m)
            
        #tagged in training data as NN but should be NNA
        #tag changed below        
        if tag == 'NN' and len(morph_new) > 1 and morph_new[-1][1] == 'SUF_ADJ' and morph_new[-2][0] not in ['frei', 'schlicht']:
            tag = 'NNA'
            morph_adj,subst  = split_adj_lemma(*morph_new[-2],subst)
            morph_new = morph_new[:-2] + morph_adj + [morph_new[-1]] 
        elif tag == 'NN' and  len(morph_new) > 2 and morph_new[-2][1] == 'SUF_ADJ' and morph_new[-3][0] not in ['frei','schlicht']:
            tag = 'NNA'
            morph_adj, subst  = split_adj_lemma(*morph_new[-3],subst)
            morph_new = morph_new[:-3] + morph_adj  + [(morph_new[-2][0]+morph_new[-1][0],'SUF_ADJ')]   

        
        data.append((sentnr,word,lemma,stem,tag,morph_new,subst))

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
    global nominalized
    global mostcommontag
    
    partikel = Counter() 
    nounstems = Counter()
    nounvarstems = Counter()
    verbstems = Counter()
    verbnpstems = Counter()
    adjstems = Counter()
    NEstems = Counter()
    verb2tag = {}
    mostcommontag = {}
    nominalized = Counter()
 
    for entry in morphlist:
        sentnr,_,_,stem,tag, morphemes, subst = entry
        if sentnr == -1:
            weight = 5
        else:
            weight = 1
        if tag == 'TRUNC':
            continue
        if tag == 'NNA':
            nominalized.update([stem])
        for i in range(len(morphemes)):
            m = morphemes[i]
            if len(m[0]) < 2:
                continue
            if m[1] == 'NN':
                nounstems.update(weight*[m[0]])
            if m[1] == 'NN_VAR':
                nounvarstems.update(weight*[m[0]])
                if m[0] == 'beamt':
                    print(sentnr,morphemes)
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
            tagcnt = mostcommontag.get(m[0],Counter()) 
            tagcnt.update([m[1]])  
            mostcommontag[m[0]] = tagcnt          

    mostcommontag = {w:mostcommontag[w].most_common(1)[0][0] for w in mostcommontag }

    for n in list(nounstems):
        if n not in unsplitable and len(splitcompound(nounstems,nounvarstems,NEstems,n,n)) > 1: ##Unschön, das wird jetzt doppelt aufgerufen
            nounstems[n] = 0
            
            

def erroneous(morphemes,word,tag):
    error = False

    if tag == 'TRUNC' and morphemes[-1][1] != 'HYPHEN':
        error = True
    
    return error
  
    
def process_words(wordlist):
    data = []
    for sentnr,word,lemma,tag,feats in wordlist:
        tag = tagdict.get(tag,tag)
        stem,morphemes,stemsub = find_morphemes(word,lemma,tag,feats)
        if not erroneous(morphemes,word,tag):
            data.append((sentnr,word,lemma,stem,tag,morphemes,stemsub))
    return data

def make_morphem_patterns(wordlist):
    data = process_words(wordlist) 
    print('collecting morphemes')    
    collect_morphemes(data) 
    print('Post processing')   
    data = postprocess_morphemes(data)  
    print('collecting morphemes (2nd round)')       
    collect_morphemes(data) 
    print('Post processing (2nd round)')  
    data = postprocess_morphemes(data)   
          
    return data


#Download the following files from University of Stuttgart and ISD Mannheim
#Repair some errors in the tiger corpus by first running repair_tiger.py
Data = read_tiger_words(r'tiger.16012013.conll09c')
Data += read_dereko_words(r'DeReKo-2014-II-MainArchive-STT.100000.freq')
Data += read_nounlist(r'substantive.txt')
# http://www.deutschonline.de/Deutsch/Grammatik/Plural.htm

morphdata = make_morphem_patterns(Data)

fout = codecs.open("labeledmorph_ger.csv", "w","utf-8")

for word in morphdata:
    if len(word[-1]) == 3:
       print(*word,sep='\t',end='\n',file=fout)
    else:
       print(*word[:-1],sep='\t',end='\n',file=fout)
fout.close() 

