import codecs
import re
import ast
from collections import Counter



analyzable_classes = {"N","ADJ"}

suffixtable = {"SUF_INF":"en|n",
               "SUF_ADJ":"(?:e|s|en)?",
               "SUF_N":"(?:eren|en|ën|n|es|'s|s)?"
              }
              
consonant = {'s':'(?:z|s)','f':'(?:f|v)'}


def read_sonar_words(sonar_csv_file):
    data = []

    with codecs.open(sonar_csv_file,'r','utf8') as f:
        for line in f:
            columns = line.split()
            data.append(columns)
    return data
    
#sentnr,nr,word,lemma,root,pos,postag    



def conspat(c):
    return consonant.get(c,c)

def split_word(word,lemma,stem,pos,postag):
    mapping = ()
    morphemes  = []


    ##Suffix Inflection
    suftag = 'SUF_'+pos
    suffix = ""
    if suftag in suffixtable:
        suffixpattern = suffixtable[suftag] 
    else:
        suffixpattern = '.*'
        
    #Suffix Derivation, only a few highly productive cases
    if pos == 'ADJ':
        derivpattern = '(?:er|st)?'
        derivtag = 'ADJ_COMP'
    else:
        derivpattern = ''
        derivtag = ''

    #Stem
    if '_' not in stem and len(lemma) < len(stem):
        #print(word,lemma,stem)
        stem = lemma
    
    stem_parts = stem.strip('_').split('_')
    if pos == 'N' and stem_parts[-1] == 'dim':
       stem_parts = stem_parts[:-1]
       derivpattern = '(?:je|tje|etje|pje)?'
       derivtag = 'N_DIM'
    
    #stempattern = '(' + ')(.*)('.join(stem_parts) + ')'
    if len(stem_parts) > 1:
        stempattern = '(' + ')(.*?)('.join(stem_parts[:-1]) + ')(.*?)'
    else:
        stempattern = ''
    mainstem = stem_parts[-1]
    
    
    stempatterns = []
    stempatterns.append((len(stem_parts),stempattern+'('+mainstem[:-1]+ conspat(mainstem[-1]) +')'))
    stempatterns.append((len(stem_parts),stempattern+'('+mainstem[:2]+'.*'+ conspat(mainstem[-1]) +')'))
    stempatterns.append((len(stem_parts),stempattern+'('+mainstem[0]+'.*'+ conspat(mainstem[-1]) +')'))
    stempatterns.append((1,'(' + lemma[:-1] + conspat(lemma[-1])  +')'))
    stempatterns.append((1,'(' + lemma[:2] + '.*' + conspat(lemma[-1])  +')'))
    stempatterns.append((1,'(' + lemma[0] + '.*' + conspat(lemma[-1])  +')'))
    stempatterns.append((len(stem_parts),stempattern+'('+mainstem[0]+'.*)'))
    stempatterns.append((1,'(' + lemma[0] + '.*)'))
    
    for nr_of_stem_parts, stempattern in stempatterns:
        pattern = '^'+stempattern+'('+derivpattern+')'+'('+suffixpattern+')$'
        match = re.match(pattern,word)
        if match:
            #print(stem,pattern)
            for i in range(1,2 * nr_of_stem_parts):
                 p = match[i]
                 if i%2 == 0:
                     if len(p) > 0:
                         morphemes.append((p,'LE'))  #Linking Element
                 elif i == 2 * nr_of_stem_parts - 1 and p != mainstem and p!= lemma:
                     tag = pos+'_VAR'
                     morphemes.append((p,tag))
                     if nr_of_stem_parts == 1:
                         mapping= (tag,p,lemma)
                     else:
                         mapping = (tag,p,mainstem)
                 else:
                     morphemes.append((p,pos))
                                  
            deriv = match[2 * nr_of_stem_parts] 
            if len(deriv) > 0:
                morphemes.append((deriv,derivtag))        
            suffix = match[2 * nr_of_stem_parts + 1]
            if len(suffix) > 0:
                morphemes.append((suffix,suftag))
            break
        
      
    if not match:
        #if pos == 'N':
        #    print(stem,pattern)
        morphemes = [('XXX',pos)]
    
        
    return morphemes,mapping

def find_morphemes(word,lemma,root,pos,postag):
    morphemes = []
    mapping = ()
    
    word = word.lower()
    lemma = lemma.lower()
    root = root.lower()
    

    if pos not in analyzable_classes or '+' in word or '*' in word or '(' in word or ')' in word:
        morphemes = [(word,pos)]
    else:
        morphemes, mapping = split_word(word,lemma,root,pos,postag)
        
    if len(morphemes) > 0:       
        morphemes.append(('','END_'+pos))


    return morphemes, mapping
 
def splitcompound(nounset,nounvarset,noun):
    for i in range(3,len(noun)-3):
        n1 = noun[:i]
        #if n1 in nounset:
        if nounset.get(n1,0) > 4: 
            n2 = noun[i:]
            sc_n2 = splitcompound(nounset,nounvarset,n2)
            if len(sc_n2) > 0:
                return [(n1,'N')] + sc_n2
            elif noun[i] == 's' or noun[i] == 'n' or noun[i] == '-' or noun[i] == 'e':
                glue = noun[i]
                n2 = noun[i+1:]
                sc_n2 = splitcompound(nounset,nounvarset,n2)
                if len(sc_n2) > 0:
                    return [(n1,'N'),(glue,'LI')] + sc_n2
            elif noun[i:i+2] == 'es' or noun[i:i+2] == 'en':
                glue = noun[i:i+2]
                n2 = noun[i+2:]
                sc_n2 = splitcompound(nounset,nounvarset,n2)
                if len(sc_n2) > 0:
                    return [(n1,'N'),(glue,'LI')] + sc_n2
    if nounset.get(noun,0) > 4 and noun[0] != '-':
        return [(noun,'N')]
    elif nounvarset.get(noun,0) > 4 and noun[0] != '-':
        return [(noun,'N_VAR')]
    else:
        return []
    
def collect_morphemes(morphlist):
    global nounstems 
    global nounvarstems

    nounstems = Counter()
    nounvarstems = Counter()
 
    for entry in morphlist:
        _,_,_,tag, morphemes, subst = entry
        features = tag.split('(')[1].strip(')').split(',')
        type = features[0]
        if type == 'soort':
           for m in morphemes:
               if m[1] == 'N':
                   nounstems.update([m[0]])
               if m[1] == 'N_VAR':
                   nounvarstems.update([m[0]])
                
    for n in list(nounstems):
        if len(splitcompound(nounstems,nounvarstems,n)) > 1: ##Unschön, das wird jetzt doppelt aufgerufen
            nounstems[n] = 0
       

       
def split_noun(stem,tag,subst): 
    #result = []                
    #if stem not in NEstems:
    result = splitcompound(nounstems,nounvarstems,stem)        
    #else: 
    #    result = []
    if len(result) > 0:
        if len(subst) == 3 and len(result) > 1 :
            start_stem = sum([len(noun) for noun,_ in result[:-1]])
            subst = (subst[0],subst[1][start_stem:],subst[2][start_stem:])
    else:
        result = [(stem,tag)]
        
    return result,subst                

def postprocess_morphemes(morphlist):  
    data = []
   
    for entry in morphlist:
        if len(entry) != 6:
            data.append(entry)
            continue
        sentnr,word,lemma,tag, morphemes, subst = entry
        pos = tag.split('(')[0]
        features = tag.split('(')[1].strip(')').split(',')
        if pos == 'N' and features[0] == 'soort':
           morph_new = []
           for i in range(len(morphemes)):
               m = morphemes[i]

               if m[1] == 'N' or m[1] == 'N_VAR':
                   splitted,subst  = split_noun(m[0],m[1],subst)
                   morph_new.extend(splitted) 
               else: 
                   morph_new.append(m)
           data.append((sentnr,word,lemma,tag,morph_new,subst))
           if morphemes != morph_new:
               print(morphemes,'===>',morph_new)
        else:
           data.append(entry) 

    return data    

def process_words(wordlist):
    data = []
    for  tuple in wordlist:
        if len(tuple) != 7:
            continue
        sentnr,wordnr,word,lemma,root,_,postag = tuple
        pos = postag.split('(')[0]
        morphemes,stemsub = find_morphemes(word,lemma,root,pos,postag)
        data.append((sentnr,word,lemma,postag,morphemes,stemsub))
        #print(sentnr,morphemes)
    return data


def make_morphem_patterns(wordlist):
    data = []
   
    data = process_words(wordlist)  
    #collect_morphemes(data)
    #data = postprocess_morphemes(data)    
  

          
    return data





Data = read_sonar_words(r'sonar.csv')


morphdata = make_morphem_patterns(Data)

fout = codecs.open("labeledmorph_dutch.csv", "w","utf-8")

for word in morphdata:
    print(*word,sep='\t',end='\n',file=fout)
fout.close() 


