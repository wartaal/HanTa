import codecs
import re
import ast
from collections import Counter

def read_sonar_words(sonar_csv_file):
    data = []

    with codecs.open(sonar_csv_file,'r','utf8') as f:
        for line in f:
            columns = line.split()
            data.append(columns)
    return data
    
#sentnr,nr,word,lemma,root,pos,postag    

def read_freq_words(freq_csv_file):
    data = []

    with codecs.open(freq_csv_file,'r','utf8') as f:
        for line in f:
            word,lemma,_,postag = line.strip().split('\t')
            if postag != 'XXX' and not postag.startswith('SPEC'):
                data.append(['-1','1',word,lemma,lemma,'-',postag])
    return data
    
    
analyzable_classes = {"N","ADJ","WW","SPEC(symb)"}
              
consonant = {'s':'(?:z|s)','f':'(?:f|v)'}

def makesuftag(suffix,pos,features):
    tag = 'SUF_'+pos
    
    if pos == 'ADJ':
        if suffix == 'e':
            tag = 'SUF_ADJ_E'
        elif suffix == 'en':
            tag = 'SUF_ADJ_EN'
        elif suffix == 's':
            tag = 'SUF_ADJ_S'
        else:
            tag = 'SUF_ADJ'
    elif pos == 'N':
        if suffix[-1] == 'e':
            tag = 'SUF_N_E'
        elif suffix[-1] == 'n':
            tag = 'SUF_N_N'
        elif suffix[-1] == 's':
            tag = 'SUF_N_S'
        else:
            tag = 'SUF_N'
    elif pos == 'WW':
        if features[0] in ['od','vd']:
            tag = 'SUF_ADJ'
        elif features[0] == 'pv':
            if features[1] == 'verl' and suffix[0] in ['t','d']:
                tag = 'SUF_WW('+','.join(features[1:])+')'
            else:
                tag = 'SUF_WW('+','.join(features[2:])+')'
        elif features[0] == 'inf':
            tag = 'SUF_WW(inf)'
    return tag

def makederivtag(suffix,pos,features):
    tag = 'SUF_'+pos
    
    if pos == 'WW' and features[0] == 'od':
        tag = 'SUF_OD'
    elif pos == 'WW' and features[0] == 'vd':
        if len(suffix) > 0 and suffix[-1] == 'n':
            tag = 'SUF_VD_EN'
        else:
            tag = 'SUF_VD'
    elif pos == 'ADJ' and features[1] == 'comp':
        tag = 'SUF_COMP'
    elif pos == 'ADJ' and features[1] == 'sup':
        tag = 'SUF_SUP'
    elif pos == 'N' and features[2] == 'dim':
        tag = 'SUF_DIM'
    return tag
    
def conspat(c):
    return consonant.get(c,c)

def split_word(word,lemma,root,pos,features):
    lemmalc =  lemma.lower()
    mapping = ()
    morphemes  = []
    
    #suftag = 'SUF_'+pos    
    prefpattern = '()'
    preftag = ''
    derivpattern = ''
    derivtag = ''
    
    if word == 'kan' and lemmalc == 'kunnen':
        return 'kunn', [('kan', 'WW_VAR')],('WW_VAR', 'kan', 'kunn')

    if pos == "WW":
        if lemmalc[-2:] in ['en','ën']  and lemmalc[-4:] not in ['doen','zien']:
            stem = lemmalc[:-2]
        elif lemma[-1:] == 'n':
            stem = lemmalc[:-1]
        else:
            stem = lemmalc
            
        if  features[0] == 'vd':
            if word.startswith('tegenge'):
                prefpattern = '(?:(tegen)ge)?'
            elif 'geluk' in lemmalc or 'gezel' in lemmalc:
                prefpattern = '()'
            elif lemmalc.startswith('ge') and not word.startswith('gege'):
                prefpattern = '(?:(.{3,})ge)?'
            else:
                prefpattern = '(?:(.*?)ge)?'
            preftag = 'PREF_VD'
            if lemmalc[-1] in ['d','t']:
                derivpattern = '(?:en)?'
            else:
                derivpattern = '(?:n|en|d|t)?'
        elif features[0] == 'od':
            derivpattern = '(?:e?nd)'
    #elif pos == 'ADJ':
    #    derivpattern = '(?:er|st)?'
    elif pos == 'ADJ' and 'comp' in features :
        derivpattern = 'd?er'
        stem = lemmalc
    elif pos == 'ADJ' and 'sup' in features :
        derivpattern = 'st'
        stem = lemmalc
    elif pos == 'N' and 'dim' in features:
        derivpattern = '(?:je|tje|etje|pje|ke)?'
        stem = lemmalc
    else:
        stem = lemmalc
  
    suffix = ""
    if pos == 'WW' and  features[0] == 'vd':
        suffixpattern = "(?:e|en)?"
    elif pos == 'ADJ':
        suffixpattern = "(?:e|s|en)?"
    elif pos == 'N':
        suffixpattern = "(?:en|ën|n|es|'s|s|e)?"
    elif pos == 'WW':
        suffixpattern = "(?:t|n|en|ën|de|den|ten|te|e)?"
    else:
        suffixpattern = '.*'       
        
 
    stempatterns = []
    stempatterns.append(stem[:-1] + conspat(stem[-1]))
    
    if pos == 'WW' and features[0] == 'vd':
        stempatterns.append('.*?' + stem[-2] + conspat(stem[-1]))
        stempatterns.append('.{2,}?' + conspat(stem[-1]))
        stempatterns.append('.{3,}?')
    else:
        #stempatterns.append(lemma[0] + '.*?')
        stempatterns.append(stem[:2] + '.*?' + conspat(stem[-1]))
        stempatterns.append(stem[0] + '.*?' + conspat(stem[-1]))
        stempatterns.append(stem[0] + '.*?')
        stempatterns.append('.*?')
    
    
    for stempattern in stempatterns:
        pattern = '^('+prefpattern+')('+stempattern+')('+derivpattern+')('+suffixpattern+')$'
        match = re.match(pattern,word)
        partikel = ''
        if match:
            prefix = match[1]
            if len(prefix) > 0:
                if match[2] and len(match[2]) > 0:
                    partikel = match[2]
                    morphemes.append((partikel,'PTK'))
                    morphemes.append((prefix[len(partikel):],preftag))
                else:
                    morphemes.append((prefix,preftag))
            p = match[3]
            if  partikel+p != stem: 
                tag = pos+'_VAR'
                if partikel+p != stem[:-1] and partikel+p != stem[:-1]+stem[-2:]:
                    if 'verl' in features:
                        tag = tag + '(verl)'
                    elif 'vd' in features:
                        tag = tag + '(vd)'
                morphemes.append((p,tag))
                mapping= (tag,p,stem[len(partikel):])
            elif 'vd' in features and match[4]  == 'en': #gelopen
                tag = pos + '_VAR(vd)'
                morphemes.append((p,tag))
            else:
                morphemes.append((p,pos))
                                  
            deriv = match[4] 
            if len(deriv) > 0:
                derivtag = makederivtag(deriv,pos,features)
                morphemes.append((deriv,derivtag))        
            suffix = match[5]
            if len(suffix) > 0:
                suftag = makesuftag(suffix,pos,features)
                morphemes.append((suffix,suftag))
            break
        
      
    if not match:
        morphemes = [(word,pos)]
        if word != stem:
            mapping = (pos,word,stem)
    
        
    return stem,morphemes,mapping

def find_morphemes(word,lemma,root,pos,features):
    morphemes = []
    mapping = ()
    
    word = word.lower()
    #lemma = lemma.lower()
    root = root.lower()
    
    tag = pos+'('+','.join(features)+')'

    if pos not in analyzable_classes: 
        morphemes = [(word,tag)]
        stem = lemma.lower()
        if word != stem:
            mapping = (tag,word,stem)
    else:
        if '+' in word or '*' in word or '(' in word or ')' in word:
            word = word.replace('+','').replace('(','').replace(')','').replace('*','')
            lemma = lemma.replace('+','').replace('(','').replace(')','').replace('*','')
            root = root.replace('+','').replace('(','').replace(')','').replace('*','')
        stem, morphemes, mapping = split_word(word,lemma,root,pos,features)


    return lemma, stem,morphemes, mapping
    
def cons(l):
    if l in 'aeoui':
        return False
    else:
        return True
    
def splitcompound(noun,lastvar,depth = 0):
    nsuf = ['oor','schap','aard','heid','schapp','graaf','aar','nis','niss','ar','ring','ster','er','el']

    for i in range(3,len(noun)-2):
        n1 = noun[:i]
        #if n1 in nounset:
        if (purenounstems.get(n1,0) > 4 or (len(n1) > 5 and purenounstems.get(n1,0) > 0)) and (depth == 0 or n1 not in nsuf): 
            n2 = noun[i:]
            sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
            if len(sc_n2) > 0:
                return [(n1,'N')] + sc_n2
            
            glue = noun[i]
            if glue in ['s','n','-'] or (glue == 'e' and cons(noun[i-1]) and cons(noun[i+1])): 
                n2 = noun[i+1:]
                sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
                if len(sc_n2) > 0:
                    if glue == '-':
                        li = 'LI(symb)'
                    else:
                        li = 'LI'
                    return [(n1,'N'),(glue,li)] + sc_n2
            
            glue = noun[i:i+2]
            if glue in ['es','en'] and cons(noun[i-1]):
                n2 = noun[i+2:]
                sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
                if len(sc_n2) > 0:
                    return [(n1,'N'),(glue,'LI')] + sc_n2
        if (len(n1) > 2 and purenounvarstems.get(n1,0) > 5 or len(n1) > 5 and purenounvarstems.get(n1,0) > 0) and (depth == 0 or n1 not in nsuf) : 
            #N_VAR as first part of a compound only allowed if a 'e' is following, or if the N_VAR is one of kinder, blader, eier, etx
            if len(n1) > 3 and n1[-2:] == 'er':
                n2 = noun[i:]
                sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
                if len(sc_n2) > 0:
                    return [(n1,'N_VAR')] + sc_n2
            
            glue = noun[i]
            if glue == 'e' and cons(noun[i-1]) and cons(noun[i+1]): 
                n2 = noun[i+1:]
                sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
                if len(sc_n2) > 0:
                    return [(n1,'N_VAR'),(glue,'LI')] + sc_n2
            glue = noun[i:i+2]
            if glue in ['es','en'] and cons(noun[i-1]) :
                n2 = noun[i+2:]
                sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
                if len(sc_n2) > 0:
                    return [(n1,'N_VAR'),(glue,'LI')] + sc_n2
        if depth == 0 and len(n1) > 3 and wwstems.get(n1,0) > 5:
            n2 = noun[i:]
            sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
            if len(sc_n2) > 0:
                return [(n1,'WW')] + sc_n2
        if depth == 0 and len(n1) > 3 and wwvarstems.get(n1,0) > 5:
            n2 = noun[i:]
            sc_n2 = splitcompound(n2,lastvar,depth = depth +1)
            if len(sc_n2) > 0:
                return [(n1,'WW_VAR')] + sc_n2
    if (nounstems.get(noun,0) > 4  or (len(noun) > 5 and nounstems.get(noun,0) > 0)) and noun not in nsuf and not lastvar:
        return [(noun,'N')]
    elif nounvarstems.get(noun,0) > 2 and lastvar and noun not in nsuf:
        return [(noun,'N_VAR')]
    elif len(noun) > 4 and nounvarstems.get(noun,0) > 0 and lastvar and noun not in nsuf:
        return [(noun,'N_VAR')]
    else:
        return []
        

def tag2featurelist(tag):
    pos,fstr = tag.split('(')
    features = fstr.strip(')').split(',')
    return pos, features
   
def collect_morphemes(morphlist):
    global nounstems 
    global nounvarstems
    global purenounstems 
    global purenounvarstems
    global adjstems
    global wwstems
    global wwvarstems
    global vzstems
    global ptk_sep
    global ptk_nonsep

    adjstems = Counter()
    wwstems = Counter()
    wwvarstems = Counter()
    vzstems = Counter()
    nounstems = Counter()
    nounvarstems = Counter()
    ptk_sep = Counter()
    ptk_nonsep = Counter()
 
    for entry in morphlist:

        _,_,_,_,_,tag, morphemes, subst = entry
        pos,features = tag2featurelist(tag)
        if pos == 'N' and features[0] == 'soort':
            for m in morphemes:
                if m[1] == 'N':
                    nounstems.update([m[0]])
                if m[1] == 'N_VAR':
                    nounvarstems.update([m[0]])
            if len(subst) == 3 and subst[0][:5] == 'N_VAR':
                nounstems.update([subst[2]])
        elif pos == 'ADJ':
            for m in morphemes:
                if m[1] == 'ADJ' or  m[1] == 'ADJ_VAR':
                    adjstems.update([m[0]])
        elif pos == 'WW':
            for m in morphemes:
                if m[1] == 'WW' :
                    wwstems.update([m[0]])
                elif  m[1] == 'WW_VAR' :
                    wwvarstems.update([m[0]])
                elif m[1] == 'PTK':
                    ptk_sep.update([m[0]])
            if len(subst) == 3 and subst[0][:6] == 'WW_VAR':
                wwstems.update([subst[2]])
        elif pos == 'VZ':
            for m in morphemes:
                if m[1] == 'VZ':
                    vzstems.update([m[0]])
                    
    nounstems['hersen'] = 5
    nounstems['waard'] = 0
    nounstems['el'] = 0
    nounstems['mol'] = 0
    nounvarstems['provinci'] = 0
    nounvarstems['viss'] = 0
    nounvarstems['getijd'] = 0
    nounvarstems['er'] = 0
    nounvarstems['moll'] = 0
    wwstems['over'] = 0
    wwstems['opper'] = 0
    wwstems['neder'] = 0
    wwstems['wet'] = 0
    wwstems['schar'] = 0
    wwstems['har'] = 0
    wwvarstems['groot'] = 0
    wwstems['hoog'] = 0
    wwvarstems['spar'] = 0
    wwvarstems['geloof'] = 0
    wwstems['dubbel'] = 0
    wwstems['lijk'] = 0

    
    for n in list(nounstems):
        if vzstems.get(n,0) > nounstems[n]:
            nounstems[n] = 0
            
    purenounstems = {n:nounstems[n] for n in nounstems if adjstems.get(n,0) < nounstems[n] and wwstems.get(n,0) < nounstems[n] and wwvarstems.get(n,0) < nounstems[n]}
    purenounvarstems = {n:nounvarstems[n] for n in nounvarstems if adjstems.get(n,0) < nounvarstems[n] and wwstems.get(n,0) < nounvarstems[n] and wwvarstems.get(n,0) < nounvarstems[n]}
             
    for n in list(nounstems):
        if len(splitcompound(n,True)) > 1: 
            nounstems[n] = 0
    
    ptk_sep = [x for x in  ptk_sep if ptk_sep[x] > 5]
    ptk_nonsep = [x for x in  ptk_sep if ptk_nonsep[x] > 5]
    ptk_sep.sort(key=lambda x:len(x),reverse = True)
    ptk_nonsep.sort(key=lambda x:len(x),reverse = True)
       

def split_noun(stem,tag,subst): 

    unsplittable = ['ballon','plankton','diefstal','automaat','automat','architectuur','standaard','kartel','oorsprong','oordeel','karton','metropool']
    if len(subst) == 3:
        lastvar = True
    else:
        lastvar = False
     
    if stem not in unsplittable:
        result = splitcompound(stem,lastvar)  
    else:
        result = []

    if len(result) > 1:
        if len(subst) == 3:
            start_stem = sum([len(noun) for noun,_ in result[:-1]])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    else:
        result = [(stem,tag)]
        
    return result,subst  

def splitnounstem(stem,tag,subst): 
    if tag == 'N' and stem[-4:] == 'heid' and adjstems.get(stem[:-4],0) > 1:
        return [(stem[:-4],'ADJ'),(stem[-4:],'SUF_SUBST')],subst
    elif tag == 'N_VAR' and stem[-3:] == 'hed' and adjstems.get(stem[:-3],0) > 1:
        return [(stem[:-3],'ADJ'),(stem[-3:],'SUF_A_SUBST')],('SUF_A_SUBST','hed','heid')
    elif tag == 'N' and stem[-3:] == 'ing' and wwstems.get(stem[:-3],0) > 1:
        return [(stem[:-3],'WW'),(stem[-3:],'SUF_WW_SUBST')],subst
    else:
        return [(stem,tag)],subst
    
def splitadjstem(stem,tag,subst): 
    if stem.startswith('on'):
        if stem[2:] in adjstems:
            if len(subst) == 3:
                subst = (subst[0],subst[1][2:],subst[2][2:])
            adjmorphemes, subst = splitadjstem(stem[2:],tag,subst)
            return [(stem[:2],'PREF_NEG')] + adjmorphemes, subst
        else:
            if len(subst) == 3:
                subst1 = (subst[0],subst[1][2:],subst[2][2:])
            else:
                subst1 = subst
            adjmorphemes, subst2 = splitadjstem(stem[2:],tag,subst1)
            if len(adjmorphemes) > 1:
                return [(stem[:2],'PREF_NEG')] + adjmorphemes, subst2
    
    if stem.startswith('niet-') and stem[5:] in adjstems:
        if len(subst) == 3:
            subst = (subst[0],subst[1][5:],subst[2][5:])
        adjmorphemes, subst = splitadjstem(stem[5:],tag,subst)
        return [(stem[:4],'PREF_NEG'),('-','LI(symb)')] + adjmorphemes, subst
    
    if '-' in stem:
        adjs = stem.split('-')
        if len(adjs) == 2: #andere gevallen: mond-aan-mond laag-bij-de-gronds niet-nieuwe-orde rood-wit-blauw
            a1,a2 = adjs 
            if a1 in adjstems and a2 in adjstems:
                if len(subst) == 3:
                    s_a2 = 1 + len(a1)
                    subst = (subst[0],subst[1][s_a2:],subst[2][s_a2:])
                    tag2 = subst[0]
                else:
                    tag2 = 'ADJ'
                return [(a1,'ADJ'),('-','LI(symb)'),(a2,tag2)], subst
    
    adjsuffix = ['bar','baar','aardig']
    exclude = ['rationel','rationeel','matig']
    wwexclude = ['open'] #openbaar

    for i in range(3,len(stem)-2):
        noun = stem[:i]
        adj = stem[i:]
        if adj in adjsuffix or (adj in adjstems and adj not in exclude):
            if adj in adjsuffix:
                tag2 = 'SUF_WW_ADJ'
            elif len(subst) == 3:
                tag2 = 'ADJ_VAR'
            else:
                tag2 = 'ADJ'
            if len(subst) == 3:
                subst1 = (tag2,subst[1][i:],subst[2][i:])
            else:
                subst1 = subst
            if i > 3 and adj in adjsuffix and noun in wwstems and noun not in wwexclude:
                verbmorphlist,_ = splitverbstem([(noun,'WW')],'',())
                return verbmorphlist+[(adj,tag2)],subst1
            elif i > 3 and adj in adjsuffix and noun in wwvarstems and noun not in wwexclude:
                verbmorphlist,_ = splitverbstem([(noun,'WW_VAR')],'',())
                return verbmorphlist+[(adj,tag2)],subst1
            elif noun in nounstems:
                return [(noun,'N'),(adj,tag2)],subst1
            elif noun in nounvarstems:
                return [(noun,'N_VAR'),(adj,tag2)], subst1
    
    return [(stem,tag)], subst

def splitverbstem(morphemelist,root,subst):
    prefix = ['be','ont','her','mis','ver','er','ge']
    unsplitable = ['generer','genereer','gelijk','beter','gemakkelijk','gewis','gewiss','erger','opereer','operer','openbar','openbaar']

    morpheme = morphemelist[0]
    
    if morpheme[1] == 'PTK' or morpheme[1] == 'PREF_VD' or morpheme[1] == 'PREF_WW':
        return morphemelist,subst
    
    sublist = []

    parts = root.split('_') 
    if len(parts) > 1:
        ptk = parts[-1]
        if morpheme[0].startswith(ptk):
            if ptk in prefix:
                tag = 'PREF_WW'
                wwtagparts = morpheme[1].split('(')
                if len(wwtagparts) == 1:
                    wwtag = 'WW_KERN'
                else:
                    wwtag = 'WW_KERN('+wwtagparts[1]
            else:
                tag = 'PTK'
                wwtag = morpheme[1]
            sublist = [(ptk,tag),(morpheme[0][len(ptk):],wwtag)]
            if len(subst) == 3:
                subst = (wwtag,subst[1][len(ptk):],subst[2][len(ptk):])
        
    if len(sublist) == 0 and morpheme[0] not in unsplitable:    
        for ptk in ptk_sep:
            if  morpheme[0].startswith(ptk) and len(morpheme[0]) > 2 + len(ptk):
                sublist = [(ptk,'PTK'),(morpheme[0][len(ptk):],morpheme[1])]
                if len(subst) == 3:
                    subst = (subst[0],subst[1][len(ptk):],subst[2][len(ptk):])
                break           
       
    if len(sublist) > 0 and morpheme[0] not in unsplitable:
        morpheme = sublist[1]
        for ptk in prefix:
            if morpheme[0].startswith(ptk) and len(morpheme[0]) > 2 + len(ptk) :
                wwtagparts = morpheme[1].split('(')
                if len(wwtagparts) == 1:
                    wwtag = 'WW_KERN'
                else:
                    wwtag = 'WW_KERN('+wwtagparts[1]
                subsublist = [(ptk,'PREF_WW'),(morpheme[0][len(ptk):],wwtag)]
                if len(subst) == 3:
                    subst = (wwtag,subst[1][len(ptk):],subst[2][len(ptk):])
                sublist = sublist[:1]+subsublist
    elif  morpheme[0] not in unsplitable and morpheme[1] != 'PREF_WW':
        for ptk in prefix:
            if morpheme[0].startswith(ptk) and len(morpheme[0]) > 2 + len(ptk):
                wwtagparts = morpheme[1].split('(')
                if len(wwtagparts) == 1:
                    wwtag = 'WW_KERN'
                else:
                    wwtag = 'WW_KERN('+wwtagparts[1]
                sublist = [(ptk,'PREF_WW'),(morpheme[0][len(ptk):],wwtag)]
                if len(subst) == 3:
                    subst = (wwtag,subst[1][len(ptk):],subst[2][len(ptk):])
                break           
    
    if len(sublist) >  0: 
        morphemelist = sublist+morphemelist[1:]    
        
    return morphemelist,subst

def splitspec(morphlist):
    m = morphlist[0]
    morphlist_new = []
    parts = re.findall(r'([^\.:\\/@]+)|([\.:\\/@]+)([^\.:\\/@]*)',m[0])
    for p in parts:
        if len(p[0]) > 0:
            morphlist_new.append((p[0],'SYMB_NAME'))
        if len(p[1]) > 0:
            morphlist_new.append((p[1],'SYMB_SEP'))
        if len(p[2]) > 0:
            morphlist_new.append((p[2],'SYMB_NAME'))
    morphlist_new.extend(morphlist[1:])
    return morphlist_new

def postprocess_morphemes(morphlist):  
    data1 = []
    data2 = []
    splittednouns = {}
   
    for entry in morphlist:
        sentnr,word,lemma,stem,root,tag, morphemes, subst = entry
        pos,features = tag2featurelist(tag)
        if pos == 'N' and features[0] == 'soort':
            morph_new = []
            for i in range(len(morphemes)):
                m = morphemes[i]
                if m[1] == 'N' or m[1] == 'N_VAR':
                    if m[0] in splittednouns:
                        splitted,subst = splittednouns[m[0]]
                    else:
                        splitted,subst  = split_noun(m[0],m[1],subst)
                        if len(splitted) > 1:
                            splittednouns[m[0]] = (splitted,subst)
                    morph_new.extend(splitted) 
                else: 
                    morph_new.append(m)
            data1.append((sentnr,word,lemma,stem,root,tag,morph_new,subst))
        elif pos == 'WW':
            morphemes, subst = splitverbstem(morphemes,root,subst)
            data1.append((sentnr,word,lemma,stem,root,tag,morphemes,subst))
        elif pos == 'ADJ':
            newmorph,subst = splitadjstem(*morphemes[0],subst)
            if len(newmorph) > 1:
                morphemes = newmorph + morphemes[1:]
            data1.append((sentnr,word,lemma,stem,root,tag,morphemes,subst))
        elif pos == 'SPEC' and features == ['symb']:
            morphemes = splitspec(morphemes)
            data1.append((sentnr,word,lemma,stem,root,tag,morphemes,subst))
        else:
            data1.append((sentnr,word,lemma,stem,root,tag,morphemes,subst)) 
            
    #iterate again over all entries to make sure that all nouns are replaced
    for entry in data1:
        sentnr,word,lemma,stem,root,tag, morphemes, subst = entry
        pos,features = tag2featurelist(tag)
        if pos == 'N' and features[0] == 'soort':
            morph_new = []
            for i in range(len(morphemes)):
                m = morphemes[i]
                if (m[1] == 'N' or m[1] == 'N_VAR') and  m[0] in splittednouns:
                    splitted,subst = splittednouns[m[0]]
                    morph_new.extend(splitted) 
                else: 
                    morph_new.append(m)

            morph_new2 = []
            for i in range(len(morph_new)):
                m = morph_new[i]
                if m[1] == 'N' or m[1] == 'N_VAR':
                    splitted,subst  = splitnounstem(m[0],m[1],subst)
                    firstpart = splitted[0]
                    if firstpart[1] == 'WW' or firstpart[1] == 'WW_VAR':
                        subsplitted,_ = splitverbstem([firstpart],'',())
                        if len(subsplitted) > 1:
                            splitted = subsplitted +splitted[1:]
                    elif firstpart[1] == 'ADJ' or firstpart[1] == 'ADJ_VAR':
                        subsplitted,_ = splitadjstem(*firstpart,())
                        if len(subsplitted) > 1:
                            splitted = subsplitted +splitted[1:]
                    morph_new2.extend(splitted) 
                else: 
                    morph_new2.append(m)
        
            data2.append((sentnr,word,lemma,stem,root,tag,morph_new2,subst))
        else:
            data2.append(entry)

    return data2    

def process_words(wordlist):
    data = []
    for  tuple in wordlist:
        if len(tuple) != 7:
            continue
        sentnr,wordnr,word,lemma,root,_,postag = tuple
        if '(' in lemma:
            continue
        pos,features = tag2featurelist(postag)
        lemma, stem, morphemes,stemsub = find_morphemes(word,lemma,root,pos,features)
        data.append((sentnr,word,lemma,stem,root,postag,morphemes,stemsub))
    return data


def missing_features(morphlist):
    data = []
   
    for entry in morphlist:
        sentnr,word,lemma,stem,root,tag, morphemes, subst = entry   
        pos,features = tag2featurelist(tag)
        if pos == 'N':
            morph = morphemes[-1]
            if '(' in morph[1]:
                mpos,mfeat = tag2featurelist(morph[1])
            else:
                mpos,mfeat = morph[1],[]
            if mpos in ['N','N_VAR'] and 'mv' in features: #plural but no suffix
                tag_new = mpos+'('+ ','.join(mfeat+['mv']) +')'
                morphemes_new = morphemes[:-1] + [(morph[0],tag_new)] # + morphemes[-1:]
                if len(subst) == 3 and subst[0] == morph[1] and subst[1] == morph[0]:
                    subst_new = (tag_new ,subst[1] ,subst[2] )
                else:
                    subst_new = subst
                entry = sentnr,word,lemma,stem,root,tag, morphemes_new, subst_new
        elif pos == 'WW' and word.endswith('ware') and 'conj' in features:
            morph = morphemes[-2]
            if '(' in morph[1]:
                mpos,mfeat = tag2featurelist(morph[1])
            else:
                mpos,mfeat = morph[1],[]
            if mpos == 'WW_VAR':
                tag_new = mpos+'('+ ','.join(mfeat+['verl']) +')'
                morphemes_new = morphemes[:-1] + [(morph[0],tag_new)] # + morphemes[-1:]
                if len(subst) == 3 and subst[0] == morph[1] and subst[1] == morph[0]:
                    subst_new = (tag_new ,subst[1] ,subst[2] )
                else:
                    subst_new = subst
                entry = sentnr,word,lemma,stem,root,tag, morphemes_new, subst_new
            
        data.append(entry)
        
    return data 

def guessgenus(word,noundict):
    genus = None
    for i in range(len(word)-2,2,-1):
        if word[-i:] in noundict:
            genus = noundict[word[-i:]]
            break
    return genus
    
def addgenus(morphlist):
    nouns = {}
    var2n = {}
    data = []
   
    for entry in morphlist:
        sentnr,word,lemma,stem,root,tag, morphemes, subst = entry
        laststem = ''
        pos,features = tag2featurelist(tag)

        if pos == 'N' and len(features) > 3 and features[0] == 'soort':
            genus = features[3]
            basenoun = False
            if morphemes[-1][1] in ['N'] :
                laststem = morphemes[-1][0]
                if len(morphemes) == 1:
                    basenoun = True
            elif len(morphemes) > 1 and morphemes[-2][1] in ['N']  and morphemes[-1][1] != 'SUF_DIM':
                laststem = morphemes[-2][0]
                if len(morphemes) == 2:
                    basenoun = True
            if genus in ['onz','zijd'] and (laststem not in nouns or basenoun):
                nouns[laststem] = genus
                
        if pos == 'N' and len(subst) == 3 and subst[0] == 'N_VAR':
            var2n[subst[1]] = subst[2]
            #n2var[subst[2]] = subst[1]
     
    nouns['bal'] = 'zijd'
    nouns['gevoelen'] = 'onz'

    for v,n in var2n.items():
        if n  in nouns and v not in nouns:
            nouns[v] = nouns[n]
        elif v  in nouns and n not in nouns:
            nouns[n] = nouns[v]
                
    for entry in morphlist:
        sentnr,word,lemma,stem,root,tag, morphemes, subst = entry

        pos,features = tag2featurelist(tag)
        if pos == 'N':
            morphemes_new = []
            subst_new = subst
            ntype = features[0]
            if len(features) > 3:
                maingenus = features[3]
            else:
                maingenus = ''
            for morpheme in morphemes:
                if morpheme[1] in ['N','N_VAR']:
                    genus = ''
                    if maingenus and  morpheme == morphemes[-1]: 
                        genus = maingenus
                    elif morpheme[1] == 'N_VAR' and morpheme[0] in var2n and var2n[morpheme[0]] in nouns:
                        genus = nouns[var2n[morpheme[0]]]
                    elif morpheme[0] in nouns:
                        genus = nouns[morpheme[0]]
                    
                    if genus:
                        feat = '('+ntype+','+genus+')'
                        morphemes_new.append((morpheme[0],morpheme[1]+feat))
                        if len(subst) == 3 and subst[0] == morpheme[1]:
                            subst_new = (morpheme[1]+feat,subst[1],subst[2])
                    else:
                        if morpheme[0] == 'N_VAR':
                            w = var2n[morpheme[0]]
                        else:
                            w = morpheme[0]
                        genus = guessgenus(w,nouns)
                        if genus:
                            feat = '('+ntype+','+genus+')'
                        elif ('mv' in features and w[-1] == 'a' and w == word) or w in ['media']:
                            feat = '('+ntype+',onz)'
                        else:
                            feat = '('+ntype+',zijd)'
                        morphemes_new.append((morpheme[0],morpheme[1]+feat))
                        if len(subst) == 3 and subst[0] == morpheme[1]:
                            subst_new = (morpheme[1]+feat,subst[1],subst[2])
                else:
                    morphemes_new.append(morpheme)
            data.append((sentnr,word,lemma,stem,root,tag, morphemes_new, subst_new) )
        else:
            data.append(entry)
            
    return data   

wordlist = read_sonar_words(r'../nl/sonar_modified.csv')
wordlist += read_freq_words(r'subtlfreq.csv')

data = process_words(wordlist)  
collect_morphemes(data)
data1 = postprocess_morphemes(data)
collect_morphemes(data1)
data2 = postprocess_morphemes(data1)    
data3 = addgenus(data2)
data4 = missing_features(data3)
morphdata = data4

fout = codecs.open("labeledmorph_dutch.csv", "w","utf-8")

for entry in morphdata:
    sentnr,word,lemma,stem,root,tag, morphemes, subst = entry
    entry1 = sentnr,word,lemma,stem,tag, morphemes, subst
    if len(subst) == 3:
        print(*entry1,sep='\t',end='\n',file=fout)
    else:
        print(*entry1[:-1],sep='\t',end='\n',file=fout)
fout.close()
