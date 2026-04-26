from lemmatize import lemmatize

CLAWS7_TO_BNC = {

    # ===== Articles/Determiners =====
    'AT':   'AT0',  # article (the, no)
    'AT1':  'AT0',  # singular article (a, an, every)
    'AT2':  'AT0',  # plural article (all) — collapsed in BNC
    'DD':   'DT0',  # general determiner
    'DD1':  'DT0',  # singular determiner
    'DD2':  'DT0',  # plural determiner
    'DDQ':  'DTQ',  # wh-determiner
    'DDQGE':'DTQ',  # genitive wh-determiner (whose)
    'DDQV':'DTQ', #whatever
    

    # ===== Existential =====
    'EX':   'EX0',  # existential there

    # ===== Conjunctions =====
    'CC':   'CJC',
    'CCB':  'CJC',  # coordinated but
    'CS':   'CJS',
    'CSA':  'CJS',  # 'as' as conjunction
    'CSN':  'CJS',  # 'than' as conjunction
    'CST':  'CJT',  # 'that' as conjunction
    'CSW':  'CJS',  # 'whether' as conjunction
    'BCS':  'CJS',  # before-conjunction (maps to general subordinating)

    # ===== Determiners/Subtypes =====
    'DA':   'DT0',  # after-determiner (former)
    'DA1':  'DT0',
    'DA2':  'DT0',
    'DAR':  'DT0',
    'DAT':  'DT0',

    # ===== Pre-/Post-Determiners =====
    'DB':   'DT0',  # pre-determiner
    'DB2':  'DT0',

    # ===== Pronouns =====
    'PN':   'PNI',  # indefinite pronoun neutral
    'PN1':  'PNI',
    'PNQO': 'PNQ',
    'PNQS': 'PNQ',
    'PNQV': 'PNQ',
    'PNX1': 'PNP',  # reflexive pronoun collapsed

    # Personal pronouns (mapped to single CLAWS5 PNP)
    'PPH1': 'PNP', 'PPHO1': 'PNP', 'PPHO2': 'PNP',
    'PPHS1': 'PNP', 'PPHS2': 'PNP',
    'PPIO1': 'PNP', 'PPIO2': 'PNP',
    'PPIS1': 'PNP', 'PPIS2': 'PNP',
    'PPX1': 'PNP','PPX2': 'PNP','PPY': 'PNP',
    'PPGE':'PNP',  # possessive personal pronoun

    # ===== Nouns =====
    'ND1':  'NN1',  # singular noun of direction
    'NN':   'NN0',  # common noun, neutral for number 
    'NN1':  'NN1',
    'NN2':  'NN2',
    'NNB':  'NP0',  # noun before title → treat as proper noun
    'NNJ':  'NN1',  # human organization noun
    'NNJ2': 'NN2',  # plural human org noun
    'NNT1': 'NN1',
    'NNT2': 'NN2',
    'NNU': 'NN0',
    'NNU1': 'NN1',
    'NNU2': 'NN2',
    'NNL':  'NN1',  'NNL1':'NN1', 'NNL2':'NN2',
    'NNO':  'CRD', 'NNO2':'CRD',
    'NNSA':'NN1',  # noun of style/title → common noun
    'NPM1':'NP0',  # month nouns 
    'NPD1':'NP0', 'NPD2':'NP0',  # weekday nouns
    'NNA':'NP0',
    'NP':'NP0',
    

    # ===== Adjectives =====
    'JJ':   'AJ0',
    'JJR':  'AJC',
    'JJT':  'AJS',
    'JK':   'AJ0',

    # ===== Verbs (auxiliaries and lexical) =====
    'VV0':  'VVB',  # base lexical verb
    'VVD':  'VVD',
    'VVG':  'VVG',
    'VVGK':  'VVG',
    'VVI':  'VVI',
    'VVN':  'VVN',
    'VVNK':  'VVN',
    'VVZ':  'VVZ',

    # Auxiliary BE
    'VB0':  'VBB',
    'VBR':  'VBB',
    'VBDR':  'VBD',
    'VBDZ':'VBD',
    'VBG':'VBG',
    'VBI':'VBI',
    'VBN':'VBN',
    'VBZ':'VBZ',
    'VBM':'VBB',

    # Auxiliary DO
    'VD0':  'VDB','VDD':'VDD','VDG':'VDG','VDI':'VDI','VDN':'VDN','VDZ':'VDZ',

    # Auxiliary HAVE
    'VH0':  'VHB','VHD':'VHD','VHG':'VHG','VHI':'VHI','VHN':'VHN','VHZ':'VHZ',

    # Modals
    'VM':  'VM0',
    'VMK':  'VM0',

    # ===== Adverbs =====
    'RR':   'AV0','RRQ':'AVQ','RRQV':'AVQ','RRT':'AV0','RGR':'AV0','RGT':'AV0',
    'RRR':   'AV0',
    'RRT':   'AV0',
    'RG':   'AV0','RGQ':'AVQ','RGQV':'AVQ',
    'RL':   'AV0','RT':'AV0','RA':'AV0','REX':'AV0','RP':'AVP','RPK':'AVP',

    # ===== Numbers =====
    'MC':   'CRD','MC1':'CRD','MC2':'CRD',
    'MD':   'ORD','MF':'CRD','MCMC':'CRD',

    # ===== Misc =====
    'EX':   'EX0',
    'FO':   'UNC',  # formula/unclassified
    'FW':   'UNC',  # foreign word becomes UNC
    'FU':  'UNC',  #  unclassified
    'GE':   'POS',  # genitive marker becomes POS in BNC
    'NP1': 'NP0',   # proper noun singular
    'NP2': 'NP0',
    'II': 'PRP',     # preposition (collapsed)
    'IO': 'PRF',     # preposition (collapsed)
    'IF': 'PRP',     # preposition (collapsed)
    'IW': 'PRP',     # preposition (collapsed)
    'APPGE': 'DPS', # possessive determiner (his/her)
    'UH': 'ITJ', 
    'ZZ1': 'ZZ0',
    'ZZ2': 'ZZ0',

    # ===== Infinitive marker =====
    'TO':   'TO0',

    # ===== Negation =====
    'XX':   'XX0',

    # ===== Punctuation —— direct mapping in BNC =====
    'YCOM': 'PUN', 'YSTP':'PUN', 'YQUO':'PUQ',
    'YCOL':'PUN', 'YSCOL':'PUN', 'YHYP':'PUN',
    'YQUE':'PUN', 'YEX':'PUN',
    'YBL':'PUL', 'YBR':'PUR', 
     'YDSH':'PUN', 'YLIP':'PUN'
}


def map_claws7_to_claws5(tag):
    return CLAWS7_TO_BNC.get(tag, 'UNMATCHED: '+tag)



def repair(word,pos,prev_word,next_word):
    if word.lower() == 'meantime' and prev_word.lower() != 'the':
        pos = 'AV0'
    elif word.lower() == 'counter' and prev_word.lower() != 'the' and next_word.lower() == 'to':    
        pos = 'AV0'
    elif word == 'disabled' and prev_word != 'seriously' and next_word== 'person':    
        pos = 'AJ0'
    elif word == 'market' and prev_word == 'US':    
        pos = 'NN1'
    elif word == 'helps' and prev_word == 'that' and next_word== 'people':    
        pos = 'VVZ'
    elif word == 'Economy' and pos == 'AJ0':    
        pos = 'NN1'
    elif word == 'conpired' :    
        word = 'conspired'
    return word, pos

def convert_bnc_sampler_to_claws5(sentences):
    """Apply BNC ADOPT-specific adjustments to the extracted sentences.

    Args:
        sentences: List of sentences, where each sentence is a list of (word, pos, lemma) tuples
    Returns:
        Adjusted list of sentences  """
    adjusted_sentences = []

    prev_word = ''
    for sent in sentences:
        adjusted_sent = []
        for i in range(len(sent)) :
            word, pos, lemma, altpos = sent[i]
            next_word = ''
            if i < len(sent)-1:
                next_word = sent[i+1][0]
            prev_word = ''  
            if i > 0:
                prev_word = sent[i-1][0]
            word = word.replace('[mdash ]','—')
            word = word.replace('[ndash ]','—')
            word = word.replace('[hellip]','...')
            word = word.replace('[oelig ]','œ')

            if pos:
                pos = map_claws7_to_claws5(pos)
            else:
                pos = altpos
            word,pos = repair(word,pos,prev_word,next_word)
            if pos.startswith("PU"):
                lemma = word
            elif word == "an" and pos == "AT0":
                lemma = "a"
            elif word == "used" and pos == "VM0": # Error in BNC. 
                lemma = "use"
            elif word == "my" and pos == "DPS" and lemma == "i": 
                lemma = "my"
            elif word == "your" and pos == "DPS" and lemma == "you": 
                lemma = "your"
            elif word == "his" and pos == "DPS" and lemma == "he": 
                lemma = "his"
            elif word == "her" and pos == "DPS" and lemma == "she": 
                lemma = "her"
            elif word == "its" and pos == "DPS" and lemma == "it": 
                lemma = "its"
            elif word == "our" and pos == "DPS" and lemma == "we": 
                lemma = "our"
            elif word == "their" and pos == "DPS" and lemma == "they": 
                lemma = "their"
            elif word == "thine" and pos == "DPS" and lemma == "thou":
                lemma = "thine"
            elif lemma.endswith("creat") and pos == altpos: # Error in BNC. 
                lemma += "e"
            elif len(lemma) == 0 or pos != altpos or "/" in lemma:
                lemma = lemmatize(word, pos)
            elif word.startswith("co-o") and lemma.startswith("coo"):
                lemma = "co-"+lemma[3:]
            adjusted_sent.append((word, pos, lemma))
            
        adjusted_sentences.append(adjusted_sent)

 
    return adjusted_sentences 