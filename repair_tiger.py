import codecs


def correctlemma(word,lemma,pos,features):
    if pos == 'NNE':
        pos = 'NE'
    elif word == 'propperen' and features.strip() == 'case=gen|number=sg|gender=neut|degree=comp':
        features = 'case=gen|number=sg|gender=neut|degree=pos'
    elif pos[:3] == 'ADJ' and lemma == 'erster':
        lemma = 'erst'
    elif pos[:3] == 'ADJ' and lemma == 'letzter':
        lemma = 'letzt'
    elif pos == 'ADJD' and word == 'ausgebremst':
        lemma = 'ausbremsen'
        pos = 'VVPP'
        features = "_"
    elif pos == 'ADJD' and word == 'ehesten' and lemma == 'ehesten':
        lemma = 'eher'
    elif pos[:3] == 'ADJ' and word[:7] == 'nächste':
        lemma = 'nächster'
        if features[-3:] == 'sup':
            features = features[:-3]+'pos'
    elif pos[:3] == 'ADJ' and lemma == 'drittbester' and features[-3:] == 'sup':
         features = features[:-3]+'pos'
    elif pos[:3] == 'ADJ' and lemma == 'achthöchster' and features[-3:] == 'sup':
         features = features[:-3]+'pos'
    elif word == 'dass' and lemma == 'daß':
        lemma = 'dass'
    elif word == 'destabilisieren' and lemma == 'handeln':
        lemma = 'destabilisieren' 
    elif word == 'bedeuteten' and pos == 'VVINF':
        word = 'bedeuten'
    elif word == 'anorden' and lemma == 'anordnen':
        word = 'anordnen'
    elif word == 'tolerien' and lemma == 'landespolitisch':
        word = 'tolerieren'   
        lemma = 'tolerieren'   
    elif word == 'aushebeln' and lemma == 'gewaltlosem': 
        lemma = 'aushebeln'  
    elif word == 'rapen' and lemma == 'rappen': 
        word = 'rappen' 
    elif lemma  == 'Wirtschafts-':
        lemma = 'Wirtschaft'
    elif lemma == 'Verkaufs-':
        lemma = 'Verkauf'
    elif lemma == 'Staats-':
        lemma = 'Staat'
    elif lemma == 'Maschinen-':
        lemma = 'Maschine'
    elif lemma[-1] == '-' and pos == 'TRUNC':
        lemma = lemma[:-1]
    elif lemma == 'nom.sg.masc' and word == 'Werbespot':
        lemma = 'Werbespot'
    elif word.lower().startswith('unser') and pos == 'PPOSAT':
        lemma = 'unser'
    elif word.lower().startswith('eu') and pos == 'PPOSAT':
        lemma = 'euer'
    elif lemma.lower().endswith('innen') and pos == 'NN' and len(lemma) > 10:
        lemma = lemma[:-3]
    elif lemma == 'losgelöst' and pos == 'VVPP':
        lemma = 'loslösen'
    elif lemma == 'angewiesem' and pos == 'VVPP':
        lemma = 'anweisen'
    elif lemma == 'losgelöst' and pos == 'VVPP':
        lemma = 'loslösen'
    elif lemma == 'uraufgeführen' and pos == 'VVPP':
        lemma = 'uraufführen'
    elif lemma == 'angemaßen' and pos == 'VVPP':
        lemma = 'anmaßen'
    elif lemma == 'angewiesen' and pos == 'VVPP':
        lemma = 'anweisen'
    elif lemma == 'hevorgegangen' and pos == 'VVPP':
        lemma = 'hervorgehen'
    elif lemma == 'abgespalten' and pos == 'VVPP':
        lemma = 'abspalten'
    elif lemma == 'losgeworden' and pos == 'VVPP':
        lemma = 'loswerden'
    elif lemma == 'anvisiert' and word == 'avisierte':
        lemma = 'avisiert'
    elif lemma == 'Importeuer':
        lemma = 'Importeur'
    elif lemma == 'unnbekannte':
        lemma = 'unbekannte'
    elif lemma == 'Museumsqualitaet':
        lemma = 'Museumsqualität'
    elif lemma == 'Pepräsentant':
        lemma = 'Repräsentant'
    elif lemma == 'Lösug':
        lemma = 'Lösung'
    elif lemma == 'Faktum' and word == 'Fakten':
        lemma = 'Fakt'
    elif lemma == 'Kellerzelle' and word == 'Killerzellen':
        lemma = 'Killerzelle'
    elif lemma == 'Deutsche_Mark' and word == 'DM':
        lemma = 'DM'
    elif lemma == 'Gesamtkunstwerk' and word == 'werk':
        lemma = 'Werk'
    elif lemma == 'Stadtbaukunst' and word == 'Stattbaukunst':
        word = 'Stadtbaukunst'
    elif lemma == 'Verkauf' and word == 'Staats-':
        lemma = 'Staat'
    elif word == 'Fraktionsvorsitzene':
        word = 'Fraktionsvorsitzende'
    elif word == 'Abs.':
         lemma = 'Abs.'
    elif word == 'Art.':
         lemma = 'Art.'
    elif word == '%' and pos == 'NN':
         lemma = '%'
    elif lemma == 'nirgenswo':
         lemma = 'nirgendswo'
    elif word == 'Themenwechseln' and lemma == 'Themawechsel':
         lemma = 'Themenwechsel'
    elif word == 'unakzeptbalen' and lemma == 'unakzeptabel':
         word = 'unakzeptablen' 
    elif lemma == "--" or lemma == "---":
        lemma =  word
   
    return word,lemma,pos,features
    
    
fin = codecs.open("tiger.16012013.conll09", "r","utf-8")
fout = codecs.open("tiger.16012013.conll09c", "w","utf-8")
    
for line in fin:
    columns = line.split()
    if len(columns) == 15:
        #word,lemma,pos =  columns[1], columns[2], columns[4]
        word, lemma, pos, features = correctlemma(columns[1], columns[2], columns[4],columns[6])
        print(columns[0],word,lemma,columns[3],pos,columns[5],features, *columns[7:], sep='\t',end='\n',file=fout)
    else:
        print(line,end='',file=fout)
fout.close() 
fin.close()