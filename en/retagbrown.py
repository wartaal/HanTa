#####################################################################################
##
## Tag the Brown corpus with claws5 tags and generate a lemma for each word
## Idea:
## 1. Change each sentence  to British spelling
## 2. Tag the corpus with a tagger trained on BNC
## 3. Use the original (correct) Brown Tag and the proposed Claws5 tag to find the correct Claws5 tag 
## 4. Use Wordnet tagger and some heuristics to find correct lemma
#####################################################################################
import nltk
from lemmatize import lemmatize
import uwotm8 
from HanTa import  HanoverTagger as ht 

tagger = ht.HanoverTagger(r'..\morphmodel_en_gb.pgz')


def convert_american_to_british_spelling(word):
    if word.lower() == 'connection':
        return 'connection'
    elif word.lower() == 'connections':
        return 'connections'
    elif word.lower() == 'infection':
        return 'infection'
    elif word.lower() == 'inflections':
        return 'infections'
    elif word.lower() == 'airplane':
        return 'airplane'
    elif word.lower() == 'airplanes':
        return 'airplanes'
    else:
        return uwotm8.convert_american_to_british_spelling(word)


def convert_british_to_american_spelling(word):
    if word == 'defence':
        return 'defense'
    elif word == 'offence':
        return 'offense'
    elif word == 'licence':
        return 'license'
    elif word == 'pretence':
        return 'pretense'
    elif word == 'analyse':
        return 'analyze'
    elif word == 'paralyse':
        return 'paralyze'
    elif word == 'programme':
        return 'program'
    elif word == 'catalogue':
        return 'catalog'
    elif word == 'dialogue':
        return 'dialog' 
    elif word == 'monologue':
        return 'monolog'    
    elif word == 'traveller':
        return 'traveler'   
    elif word == 'practize':
        return 'practice'
    elif word in ['fibre', 'centre', 'theatre']:
        return word[:-2] + 'er'    
    elif 'favour' in word:
        return word.replace('favour', 'favor')
    elif 'neighbour' in word:
        return word.replace('neighbour', 'neighbor')
    elif 'rumour' in word:
        return word.replace('rumour', 'rumor')
    elif 'colour' in word:
        return word.replace('colour', 'color')
    elif 'humour' in word:
        return word.replace('humour', 'humor')
    elif 'flavour' in word:
        return word.replace('flavour', 'flavor')
    elif 'honour' in word:
        return word.replace('honour', 'honor')
    elif word.endswith('ise'):
        return word[:-3] + 'ize'
    elif word.endswith('yse'):
        return word[:-3] + 'yze'
    elif word.endswith('ised'):
        return word[:-3] + 'ized'
    elif word.endswith('ysed'):
        return word[:-3] + 'yzed'
    elif word.endswith('ising'):
        return word[:-3] + 'izing'
    elif word.endswith('ysing'):
        return word[:-3] + 'yzing'
    elif word.endswith('isation'):
        return word[:-7] + 'ization'
    elif word.endswith('ysation'):
        return word[:-7] + 'yzation' 


    else:
        return word

def read_brown():
    data = []

    for sent in nltk.corpus.brown.tagged_sents():
        sent1 = []
        problematic = False
        
        for (word,tag) in sent:
            tagparts = tag.split('-')
            tag = tagparts[0]

            if len(tag) == 0 and word == '--':
                sent1.append(('--','--')) 
            elif tag == '*':
                sent1.append((word,'RB')) 
            elif tag[-1] == '*' and '+' in tag :
                problematic = True
            elif tag[-1] == '*' and word.endswith("n't"):
                sent1.append((word[:-3],tag[:-1])) 
                sent1.append(("n't",'RB')) 
            elif tag == 'MD*' and word[-3:] == "not":
                sent1.append((word[:-3],'MD')) 
                sent1.append(('not','RB')) 
            elif word.endswith("'s") and tag[-1] == '$':
                sent1.append((word[:-2],tag[:-1])) 
                sent1.append(("'s",'POS')) 
            elif "'" in word[1:] and '+' in tag and len(word.split("'")) == 2 and len(tag.split('+')) == 2:
                w1,w2 = word.split("'")
                t1,t2 = tag.split('+')
                sent1.append((w1,t1))
                sent1.append(("'"+w2,t2))
            elif '+' in tag:
                problematic = True  
            elif '*' in tag:
                problematic = True
            elif word == 'gonna' and tag == 'VBG+TO':
                sent1.append(('gon','VBG'))
                sent1.append(('na','TO'))
            elif word == 'gotta' and tag == 'VBG+TO':
                sent1.append(('got','VBN'))
                sent1.append(('ta','TO'))
            elif word[-1] == "'" and tag[-1] == '$':
                sent1.append((word[:-1],tag[:-1]))
                sent1.append(("'",'POS'))
            else:
                sent1.append((word,tag))
                
        
        if not problematic:            
            data.append(sent1)
        
    return data

penn2claws = {'PRP$': ['DPS'],
 'AT': ['AT0', 'DT0'],
 'CS': ['CJS','CJT'],             
 'CC': ['CJC'],
 'IN': ['AVP', 'CJS', 'PRF', 'PRP'],
 'PDT': ['DT0'],
 'ABN': ['DT0'],
 'WDT': ['DTQ'],
 'DTI': ['DT0'],  
 'DT': ['DT0'],  
 'DTS': ['DT0'],  
 'DTX': ['DT0'], 
 'ABX': ['DT0'], 
 'ABL': ['DT0'], 
 'PPS': ['PNP'],             
 'WP$': ['DTQ'],
 'EX': ['EX0'],
 'FW': ['UNC'],
 'NIL': ['UNC'],
 'POS': ['POS'],
 'JJ': ['AJ0'],
 'JJS': ['AJ0'],
 'JJR': ['AJC'],
 'JJT': ['AJS'],
 'CD': ['CRD'],
 'OD': ['ORD'],
 'NNS': ['NN2', 'NN0', 'CRD'],
 'NN': ['NN0', 'NN1','ZZ0' ,'PNI'],
 'NN$': ['NN0', 'NN1'],
 'NP': ['NP0'],
 'NP$': ['NP0'],
 'NPS': ['NN2'],
 'NR': ['NP0','AV0'],
 'NRS': ['NN2'], #NN2 is plural of NP0 and of NN1!!!
 'WP': ['PNQ'],
 'WPS': ['PNQ'],             
 'PRP': ['PNP'],
 'PPSS': ['PNP'],
 'PPO': ['PNP'],
 'PPL': ['PNP'],
 'PPLS': ['PNP'],
 'PN': ['PNI'],  
 'WPO': ['PNQ','CJT','DTQ'],  #CJT accordiong to tagging manual from BNC Corpus!!!!
 'PP$': ['DPS'], 
 'PP$$': ['PNP'], #mine, ours
 'RB': ['AV0', 'XX0', 'AVP', 'ORD','ITJ'],
 'RBT': ['AV0'],
 'WRB': ['AVQ'],
 'RBR': ['AV0'],
 'RBS': ['AV0'],
 'RN': ['AV0'],
 'AP': ['AV0'],
 'QL': ['AV0'],
 'QLP': ['AV0'],
 'WQL': ['AV0'],
 'RP': ['AVP'],  #AV0??
 'TO': ['TO0'],
 'UH': ['ITJ'],
 'VBD': ['VVD'],
 'VBG': ['VVG','AJ0','NN1','VDG'],
 'VB': ['VVB','VVI'],
 'VBN': ['VVN','AJ0','VDN'],
 'VBZ': ['VVZ'],
 'HVZ': ['VHZ'], 
 'HVD': ['VHD'],   
 'HVG': ['VHG'], 
 'HVN': ['VHN'], 
 'HV': ['VHB','VHI'], 
 'BEDZ': ['VBD'], 
 'BE': ['VBI'], 
 'BEN': ['VBN'], 
 'BEM': ['VBB'],
 'BED': ['VBD'],
 'BER': ['VBB'],
 'BEG': ['VBG'], 
 'BEZ': ['VBZ'], 
 'MD': ['VM0'],
 'DO': ['VDB','VDI'],
 'DOZ': ['VDZ'],
 'DOD': ['VDD'],
 '.': ['PUN'],
 ',': ['PUN'],
 ':': ['PUN'],
 '--': ['PUN'],
 '``': ['PUQ'],
 "''": ['PUQ'],
 "'": ['PUQ'],             
 "(": ['PUL'], 
 ")": ['PUR'],
    }



def retag(sentence):
    #print(sentence, end = '\r')
    words = [w for  w,_ in sentence]
    words_uk = [convert_american_to_british_spelling(w) for w in words]
    tags_proposed = tagger.tag_sent(words_uk,taglevel = 1)
    tags_old = [t for _,t in sentence]
    tags_new = []
    success = True

    for i in range(len(words)):
        t_p = tags_proposed[i][2]
        t_o = tags_old[i]
        w = words[i]
        w_uk = words_uk[i]
        t_n = None
        try:
            t_possible = penn2claws[t_o]
        except:
            print(w, t_o, t_p)
            t_possible = []

        #  Repair special cases first
        if w ==  'living' and  tags_old[i+1] in ['NN', 'NNS'] and words[i+1] in ['room','rooms','cost','costs','space','spaces','expense','expenses'] :
           t_n = "NN1"
        elif t_o == 'NN'  and t_p == 'NN2' and w in ['people','police','folk', 'cattle']:
           t_n = "NN2"
        elif len(t_possible) == 1:
            t_n = t_possible[0]
        elif t_p in t_possible:
            t_n = t_p
        else:
            for t_x,_ in tagger.tag_word(w_uk,cutoff=10):
                if t_x in t_possible:
                    t_n = t_x
                    break
        if not t_n:
            if t_o == "NNS" and w.lower() == 'people':
                t_n = "NN0" 
            elif t_o[0] == "N" and t_p == "NP0" and w[0].isupper():
                t_n = "NP0" 
            elif t_o == "IN" and w.lower() == 'thru':
                t_n = "PRP" 
            elif t_o == "CS" and w.lower() == 'altho':
                t_n = "CJS" 
            elif t_o == "RB" and w.lower() == 'yes':
                t_n = "ITJ" 
            elif t_o == "IN" and w in [":","-","/"]:
                t_n = "PUN" 
            elif t_o == "RB" and w.lower() == 'because': # because of!
                t_n = "CJS" 
            elif t_o == "NNS" and w.lower() == 'lots':
                if words[i+1].lower() in ["of","and","o'","more"] : 
                    t_n = "PNI" 
                else:
                    t_n = "NN2" 
            elif t_o == "IN" and w.lower() == 'rather':
                t_n = "AV0"  
            elif t_o == "IN" and t_p == "VVG" :
                t_n = "VVG"  
            elif t_o == "RB" and t_p == "VVG" and w == 'according':
                t_n = "VVG"  
            elif t_o == "IN" and t_p == "VVI" and w == "considerin'":
                t_n = "VVG"  
            elif t_o == "NNS" and t_p == "VVZ"  and w.lower() == 'employes':
                t_n = "VVG" 
                w = 'employees'
            elif t_o == "VBN" and w.lower() == 'froze':
                t_n = "VVN" 
                w = 'frozen'
            elif t_o == "VBN" and w.lower() == 'showed':
                t_n = "VVN" 
                w = 'shown'
            elif t_o == "NNS":
                t_n = "NN2" 
            elif t_o == "NN" and t_p == "AJ0"  and "-" in w: #long-term, high-speed, long-term  BUT: 19-century
                t_n = "AJ0" 
            elif t_o == "NR" and w.lower() == 'downtown':
                if tags_old[i+1].startswith('N'):
                    t_n = "AJ0"
                else:
                    t_n = "AV0"
            elif t_o == "NN" and t_p == "PRP"  and w.lower() == 'for':
                t_n = "PRP"
            elif t_o == "NN" and t_p == "CRD":
                t_n = "CRD"
            elif t_o == "NN" :
                t_n = "NN1"
            elif t_o == "IN" and w.lower() in ['pursuant','due']:
                t_n = "AJ0"
            elif t_o == "NR" and t_p == "NN1":
                t_n = "NN1"
            elif t_o == "IN" and t_p == "ORD"  and w.lower() == 'next':
                t_n = "ORD"
            elif t_o == "RB" and t_p == "CJS"  and w.lower() == 'except':
                t_n = "CJS"
            # adjectives used as secondar predicates and othe cases that seem to be tagged inccorectly    
            elif t_o == "RB" and w.lower() in ['present','asleep','due','parallel','afloat','awake','ablaze','underwater','widespread','usual','outboard','crosswise','normal','true','large','strong','lively','bodily','prone','previous','nice','subsequent']:
                t_n = "AJ0"
            # direction adverbs, flat advers, etc. Correctly tagged in Brown but unknonw to the tagger trained on BNC Sampler
            elif t_o == "RB" and w.lower() in ['verbatim','downwind','abreast','meantime','westerly','plain','cool','smart','cowardly', 'balance-wise','counter','homeward','daytime','perforce','hereabouts','thereabouts','inasmuch','overland','upland','uptown','world-wide','aloof','false','soft','half-time','piecemeal','backstairs','broadside','adrift','cheap','aforesaid','gratis']:
                t_n = "AV0"
            elif t_o == "VB" and w.lower() == "better" and tags_old[i+1] in ['BE','VBN'] :
                t_n = "AV0"
            elif t_o == "VB" and w.lower() == "best":
                t_n = "AV0"
            elif w.lower() == "even":
                t_n = "AV0"
            elif w.lower() == "clerk":
                t_n = "NN1"
            elif w.lower() == "insofar":
                t_n = "AV0"
            elif t_o == "RB" and w.lower() == "wherefore":
                t_n = "AVQ"
            elif t_o == "RB" and w.lower() == "whatsoever":
                t_n = "DTQ"
            elif t_o == "VB" and w.lower() == "program" and (tags_old[i-1] in ['NNS','``']  or tags_proposed[i-1] in ['NN2','PUQ']):
                t_n = "NN1"
            elif w.lower() == "party" and words[i+1].lower() == "leaders":
                t_n = "NN1"
            elif w.lower() == "group" and words[i-1].lower() == "electronics":
                t_n = "NN1"
            elif w.lower() == "group" and words[i+1].lower() == "O":
                t_n = "NN1"
            elif w.lower() == "guy" and t_o == "VB":
                t_n = "NN1"
            elif w.lower() == "a.d." and t_o == "RB":
                t_n = "NN1"
            elif w.lower() == "upside" and words[i+1].lower() == "down":
                t_n = "NN1"
            elif w.lower() == "vice" and words[i+1].lower() == "versa":
                t_n = "AV0"
            elif w.lower() == "versa" and words[i-1].lower() == "vice":
                t_n = "AV0"
            elif w.lower() == "durin'" and t_o == "IN":
                t_n = "PRP"     
            elif w == 'Plus': # plus is probleamtic in BNC Sampler all instances of plus that should be conjunction are tagged as preposition
                t_n = 'NN1'
            elif w.lower() == 'times' and t_o == 'IN': 
                t_n = 'NN2'
            elif w.lower() == 'against' and t_o == 'RB': 
                t_n = 'PRP'
            elif w.lower() in ['versus','v.','vs.','v','vs']:
                t_n = "PRP"
            elif t_o == 'IN' and w.lower() in ['anti','pro','2']:
                t_n = "IN"
            elif w == 'whatever':
                t_n = 'DTQ'
            elif w.lower() == 'with':
                t_n = 'PRP'
            # 3 instances of atop remain. Each is a preposition
            elif w.lower() == 'atop':
                t_n = 'PRP'
            elif w == 'dost':
                t_n = 'VDB'
            elif t_o == "VB": #VVB or VVI!!
                words_uk2 = words_uk
                #words_uk2[i] = 'drive' 
                words_uk2[i] = 'obey'
                tags_proposed2 = tagger.tag_sent(words_uk2,taglevel = 0)
                tagi = tags_proposed2[i]
                if tagi == "VVI":
                    t_n = "VVI"
                    #print(w,"VVI",' '.join(words[max(0,i-8):min(len(words)-1,i+4)]),sep="\t")
                elif tagi == "VVB":
                    t_n = "VVB"
                    #print(w,"VVB",' '.join(words[max(0,i-8):min(len(words)-1,i+4)]),sep="\t")
                else:
                    t_n = "VVI"
                    #print(w,"VVI",' '.join(words[max(0,i-8):min(len(words)-1,i+4)]),sep="\t")
            elif t_o == "VBN" and t_p == "VVD":
                t_n = "VVN"
                #print(w,' '.join(words[max(0,i-8):min(len(words)-1,i+4)]),sep="\t")
            elif t_o == "VBN" and t_p[:2] == "NN":
                t_n = "VVN"
                #print(w,' '.join(words[max(0,i-8):min(len(words)-1,i+4)]),sep="\t")
                
        if not t_n:
            t_n = "!!!"
            #print(w,t_o,t_p)
            success = False

       
        #if t_n == "NP0":
        #        lemma = w
        #elif t_n in ['NN0','NN1','NP','PRP','AJ0','VVI','VVB']:
        #    lemma = w.lower()
        #elif t_p == t_n:
        #    if w_uk == tags_proposed[i][1]: # word is lemma in the british spelling, so it will be the lemma in the american spelling as well
        #        lemma = w
        #    elif w == w_uk: # no spelling differences, we can safely take the proposed lemma
        #        lemma = tags_proposed[i][1]
        #        if lemma.endswith("ie") and t_n == "NN2" and w.endswith("ies"):
        #            lemma = lemma[:-2]+'y'
        #        if lemma == 'cloth' and t_n == "NN2" and w == 'clothes':
        #           lemma = 'clothes'
        #    else:
        #        lemma = convert_british_to_american_spelling(tags_proposed[i][1])   
        #else:

        lemma = lemmatize(w,t_n)
        

        tags_new.append((w,t_n, lemma))


    return tags_new, success


sentences = read_brown()
fout = open('BrownC5.txt','w',encoding = 'utf8')
sentnr = 0

for s in sentences:
    s1, rc = retag(s)
    if rc:
        sentnr += 1
    for w,t,l in s1:
        print(sentnr,w,t,l,sep="\t",file= fout)

fout.close()