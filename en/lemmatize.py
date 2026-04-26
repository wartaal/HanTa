from nltk.corpus import wordnet as wn
import nltk



def wntag(c5tag):
    if c5tag.startswith('AJ'):
        return wn.ADJ
    elif c5tag.startswith('NN'):
        return wn.NOUN
    elif c5tag.startswith('AV') or c5tag.startswith('RR'):
        return wn.ADV
    elif c5tag.startswith('V'):
        return wn.VERB
    return None



def lemmatize(word: str, pos: str) -> str:  
    lemmatizer = nltk.WordNetLemmatizer()
    wnt = wntag(pos)

    if pos != 'NP0':
        word = word.lower()

    split = None
    if "-" in word:
        split = word.split("-")
        word = split[-1]
        split = split[:-1]
    

    if word == 'an':
        lemma = 'a'     
    elif word == "n't":
        lemma = 'not'
    elif word == "'s'" and pos == "VBZ":
        lemma = 'be'
    elif word == "'s" and pos == "VBZ":
        lemma = 'be'
    elif word == "'s" and pos == "VHZ":
        lemma = 'have'
    elif word == "would" and pos == "VM0":
        lemma = 'will'
    elif word == "should" and pos == "VM0":
        lemma = 'shall'
    elif word == "could" and pos == "VM0":
        lemma = 'can'
    elif word == "'d" and pos == "VM0":
        lemma = 'will'
    elif word == "wo" and pos == "VM0":
        lemma = 'will'
    elif word == "'ve" and pos == "VHB":
        lemma = 'have'
    elif word == "'d" and pos == "VHD":
        lemma = 'have'
    elif word == "'ll" and pos == "VM0":
        lemma = 'will'
    elif word == "'m" and pos == "VBB":
        lemma = 'be'
    elif word == "'re" and pos == "VBB":
        lemma = 'be'
    elif word == "ca" and pos == "VM0":
        lemma = 'can'
    elif word == "'em" and pos == "PNP":
        lemma = 'they'
    elif word == "best" and pos == "AJS":
        lemma = 'good'
    elif word == 'men' and pos == 'NN2':
        lemma = 'man'
    elif word == 'uses' and pos == 'NN2':
        lemma = 'use'
    elif word == 'others' and pos == 'NN2':
        lemma = 'other'
    elif word == 'rated' and pos in ['VVD', 'VVN']:
        lemma = 'rate'
    elif word == 'felt' and pos in ['VVD', 'VVN']:
        lemma = 'feel'
    elif word == 'fell' and pos in ['VVD', 'VVN']:
        lemma = 'fall'
    elif word == 'waged' and pos in ['VVD', 'VVN']:
        lemma = 'wage'
    elif word == 'lay' and pos in ['VVD', 'VVN']:
        lemma = 'lie'
    elif word == 'rates' and pos == 'VVZ':
        lemma = 'rate'
    elif word == 'rating' and pos == 'VVG':
        lemma = 'rate'
    elif word == 'saw' and pos == 'VVD':
        lemma = 'see'
    elif word == 'further' and pos == 'AJC':
        lemma = 'far'
    elif word == 'farthest' and pos == 'AJS':
        lemma = 'far'
    elif word == 'fastest':
        lemma = 'fast'
    elif word == 'my' and pos == 'DPS':
        lemma = 'my'
    elif word == 'your' and pos == 'DPS':
        lemma = 'your'
    elif word == 'his' and pos == 'DPS':
        lemma = 'his'
    elif word == 'her' and pos == 'DPS':
        lemma = 'her'
    elif word == 'its' and pos == 'DPS':
        lemma = 'its'
    elif word == 'our' and pos == 'DPS':
        lemma = 'our'
    elif word == 'their' and pos == 'DPS':
        lemma = 'their'
    elif word == 'thy' and pos == 'DPS':
        lemma = 'thy'
    elif word == 'me' and pos == 'PNP':
        lemma = 'i'
    elif word == 'him' and pos == 'PNP':
        lemma = 'he'
    elif word == 'her' and pos == 'PNP':
        lemma = 'she'
    elif word == 'us' and pos == 'PNP':
        lemma = 'we'
    elif word == 'them' and pos == 'PNP':
        lemma = 'they'
    elif word == 'thee' and pos == 'PNP':
        lemma = 'thou'
    elif word == 'aides' and pos == 'NN2':
        lemma = 'aid'
    elif  pos == 'NN2' and word.lower() in ['senses', 'vases', 'motives','graves','soles', ]:
        lemma = word.lower()[:-1]
    elif word == 'reemerged' and pos == 'VVD':
        lemma = 'reemerge'
    elif word in ['unlinked','preceeded'] and pos in ['VVD', 'VVN']:
        lemma = word[:-2]
    elif wnt == None:
        lemma = word
    elif pos == 'NN2' and word.endswith('aires'):
        lemma = word[:-1]
    elif pos in ['NN0','NN1','NP','PRP','AJ0','VVI','VVB']:
        lemma = word
    elif pos == 'NN2' and word.endswith('teeth'):
        lemma = 'tooth'
    elif pos == 'VVG' and word.endswith("in'"):
        lemma = word[:-3]
    else:
        lemma = lemmatizer.lemmatize(word,wnt)
    
    #NB slated is ambiguous between slat and slate. 
    if pos.startswith('V') and lemma in ['hop', 'star', 'hat', 'fin','slat','twin','cop','agitat','din','grop','rag','rid','shin','spar','stag','rap']:
        lemma+='e'
    elif pos == 'NN2' and lemma == word and lemma.endswith('men'):
        lemma = lemma[:-3] + 'man'
    elif pos.startswith('V') and lemma == 'instal':
        lemma = 'install'   


    if pos == "NN2" and lemma.lower() == word.lower() and lemma[-1] == 's':
        if lemma not in ['clothes','thanks','surroundings','odds']:
            if lemma.endswith('ies'):
                lemma = lemma[:-3] + 'y'
            elif lemma.endswith("'s"):
                lemma = lemma[:-2]
            else:
                lemma = lemma[:-1]
    elif pos == 'VVG' and lemma.lower() == word.lower() and lemma.endswith("ing"):
        lemma = lemma[:-3]


    if split:
        lemma = '-'.join(split+ [lemma])

    return lemma