import codecs



def correctlemma(nr,word,lemma,pos,features):
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
    elif word == 'beharrlich' and features == 'degree=sup':
         features = 'degree=pos' 
    elif pos[:3] == 'ADJ' and lemma == 'drittbester' and features[-3:] == 'sup':
         features = features[:-3]+'pos'
    elif pos[:3] == 'ADJ' and lemma == 'achthöchster' and features[-3:] == 'sup':
         features = features[:-3]+'pos'
    elif word == 'dass' and lemma == 'daß':
        lemma = 'dass'
    elif word == 'DDR-Autoren' and lemma == 'Autor':
        lemma = 'DDR-Autor' 
    elif word == 'destabilisieren' and lemma == 'handeln':
        lemma = 'destabilisieren' 
    elif word == 'Interessierten' and lemma == 'interessierter' and pos == 'ADJA':
        lemma = 'interessierte' 
        pos = 'NN'
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
    elif word == 'Mondgötting':
        word = 'Mondgöttin'
    elif word == 'Joruba-Priesterin':
        lemma = 'Joruba-Priesterin'
    elif word == 'Ministerpräsidentin':
        lemma = 'Ministerpräsidentin'
    elif word == 'Vorgängerin':
        lemma = 'Vorgängerin'
    elif word == 'werfen' and lemma == 'werfen' and pos == 'VAINF':
        word = 'werden'
        lemma = 'werden'
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
    elif word == 'inner-' and pos == 'TRUNC':
        lemma = 'inner'
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
    elif lemma == 'rechter' and pos == 'ADJA':
        lemma = 'recht'
    elif lemma == 'LKA' and pos == 'NN':
        pos = 'NE'
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
    elif lemma == 'Prellerband':
        lemma = 'Prellerbande'
    elif lemma == 'Gesamtkunstwerk' and word == 'werk':
        lemma = 'Werk'
    elif lemma == 'Stadtbaukunst' and word == 'Stattbaukunst':
        word = 'Stadtbaukunst'
    elif lemma == 'Aufenthaltserlaubni' and word == 'Aufenthaltserlaubnis':
        lemma = 'Aufenthaltserlaubnis'
    elif lemma == 'Gewerkschafsfunktionär' and word == 'Gewerkschafsfunktionär':
        lemma = 'Gewerkschaftsfunktionär'
        lemma = 'Gewerkschaftsfunktionär'
    elif lemma == 'Startramp':
        lemma = 'Startrampe'
    elif lemma == 'Aktivisten':
        lemma = 'Aktivist'
    elif lemma == 'vorgekegt':
         lemma = 'vorgelegt'
    elif lemma == 'ausgehebelen':
         lemma = 'aushebeln'
    elif lemma == 'auslgeöst':
         lemma = 'ausgelöst'   
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
    elif word == 'folgen' and lemma == 'folen':
         lemma = 'folgen' 
    elif word == 'Funktionärinnen':
         lemma = 'Funktionärin' 
    elif word == 'Top-Funktionärinnen':
         lemma = 'Top-Funktionärin' 
    elif word == 'PKK-Funktionärinnen':
         lemma = 'PKK-Funktionärin' 
    elif word == 'Parteiabweichlern':
         lemma = 'Parteiabweichler' 
    elif word == 'Hungrigen' and pos == 'NN':
         lemma = 'hungriger' 
    elif lemma == '-' or lemma == "--" or lemma == "---":
        lemma =  word
    elif word == "--" and lemma != '--':
        word =  lemma
    elif lemma == 'bekennen' and pos == 'VMFIN':
        pos =  'VVFIN'
    elif lemma == 'bedürfen' and pos == 'VMFIN':
        pos =  'VVFIN'
    elif lemma == 'mehrere' and word == 'mehr' and pos == 'PIAT':
        lemma =  'mehr'
    elif lemma[-2:] == 'er'  and pos == 'PIAT':
        lemma =  lemma[:-2]
    elif lemma == 'zuvieler' and pos == 'PIS':
        lemma = 'zuviel'
    elif lemma == 'ein' and pos == 'PIS':
        lemma = 'einer'
    elif lemma == 'einen' and pos == 'PIS':
        lemma = 'einer'          
    elif word.lower() == 'uns' and lemma == 'sich'  and pos == 'PPER':
        lemma =  'uns'
    elif word.lower() == 'was' and lemma == 'wer'  and pos == 'PWS':
        lemma =  'was'
    elif word.lower() == 'am' and lemma == 'an'  and pos == 'PTKA':
        lemma =  'am'
    elif pos == 'PRELAT':
        lemma =  'der'
    elif pos == 'PWS':
        lemma =  word.lower()
    elif word == 'KARLSRUHE' and  lemma == 'Karlruhe':
        lemma = 'Karlsruhe'
    elif word == "Debis'" and lemma == '17':
        lemma = 'Debis'
    elif word == "c't" and lemma == '17':
        lemma = "c't" 
    elif word == 'FRANKFURT' and lemma == 'Frankfrut':
        lemma = 'Frankfurt'
    elif word == 'DÜSSELDORF' and lemma == 'Düsselsdorf':
        lemma = 'Düsseldorf'
    elif word == 'WASHINGTON' and lemma == 'Wahington':
        lemma = 'Washington'
    elif word == 'SARAJEVO' and lemma == 'Sarjevo':
        lemma = 'Sarajevo'
    elif word == 'Stuttgarter' and lemma == 'stuttgarter' and pos == 'NN':
        lemma = 'Stuttgarter'
    elif word == 'Düsseldorfer' and lemma == 'düsseldorfer' and pos == 'NN':
        lemma = 'Düsseldorfer'
    elif lemma == 'niedersachse' and pos == 'NN':
        lemma = 'Niedersachse'
    elif word == 'de' and lemma == 'da' and pos == 'NE':
        lemma = 'de'
    elif word == 'Pidgin' and lemma == 'Pigdin':
        lemma = 'Pidgin'
    elif word == 'Hamburger' and lemma == 'hamburger' and pos == 'NN':
        lemma = 'Hamburger'
    elif word == 'Pilsner' and lemma == 'Pilsener' and pos == 'ADJA':
        lemma = 'Pilsner'
    elif word == 'erzwungenem' and lemma == 'erzwingen' and pos == 'ADJA':
        lemma = 'erzwungen'
    elif word == 'geschmolzenen' and lemma == 'schmelzen' and pos == 'ADJA':
        lemma = 'geschmolzen'
    elif word == 'erweiterten' and lemma == 'erweitern' and pos == 'ADJA':
        lemma = 'erweitert'
    elif word == 'abgewiesenen' and lemma == 'abweisen' and pos == 'ADJA':
        lemma = 'abgewiesen'
    elif word == 'hinzugekommenen' and lemma == 'hinzukommen' and pos == 'ADJA':
        lemma = 'hinzugekommen'
    elif word == 'aufgegebenes' and lemma == 'aufgeben' and pos == 'ADJA':
        lemma = 'aufgegeben'
    elif word == 'zuerkannte' and lemma == 'zuerkennen' and pos == 'ADJA':
        lemma = 'zuerkannt'
    elif word == 'orientierter' and lemma == 'orientierent' and pos == 'ADJA':
        lemma = 'orientiert'
    elif word == 'bekanntgegebenen' and lemma == 'bekanntgeben' and pos == 'ADJA':
        lemma = 'bekanntgegeben'
    elif word == 'durchgeführte' and lemma == 'durchführen' and pos == 'ADJA':
        lemma = 'durchgeführt'
    elif word == 'geknüpften' and lemma == 'knüpfen' and pos == 'ADJA':
        lemma = 'geknüpft'
    elif word == 'verwendete' and lemma == 'verwenden' and pos == 'ADJA':
        lemma = 'verwendet'
    elif word == 'Erhöhte' and lemma == 'erhöhen' and pos == 'ADJA':
        lemma = 'erhöht'
    elif word == 'klingende' and lemma == 'klingen' and pos == 'ADJA':
        lemma = 'klingend'
    elif word == 'entscheidene' and lemma == 'entscheidend' and pos == 'ADJA':
        word = 'entscheidende'
    elif word == 'geprellten' and lemma == 'prellen' and pos == 'ADJA':
        lemma = 'geprellt'
    elif word == 'erschienenes' and lemma == 'erscheinen' and pos == 'ADJA':
        lemma = 'erschienen'
    elif word == 'verbissenen' and lemma == 'verbeißen' and pos == 'ADJA':
        lemma = 'verbissen'
    elif word == 'abgerechneten' and lemma == 'abrechnen' and pos == 'ADJA':
        lemma = 'abgerechnet'
    elif word == 'gekennzeichneter' and lemma == 'kennzeichnen' and pos == 'ADJA':
        lemma = 'gekennzeichnet'
    elif word == 'ausgelieferten' and lemma == 'ausliefern' and pos == 'ADJA':
        lemma = 'ausgeliefert'
    elif word == 'versicherten' and lemma == 'versichern' and pos == 'ADJA':
        lemma = 'versichert'
    elif word == 'vergriffener' and lemma == 'vergreifen' and pos == 'ADJA': 
        lemma = 'vergriffen'
    elif word == 'anfeuernden' and lemma == 'anfeuern' and pos == 'ADJA': 
        lemma = 'anfeuernd'
    elif word == 'ungeregelt' and lemma == 'ungeregelen' and pos == 'VVPP': 
        lemma = 'ungeregelt'
        pos = 'ADJD'
    elif word == 'Städtekombinationsreise': 
        lemma = 'Städtekombinationsreise'
    elif word == 'Kleinen' and lemma ==  'klein' and pos == 'NN':
        lemma = 'kleine'
        #Rollen, Liegen, Angeln
    elif 'number=pl' in features and word in ['Unterlassen','Begehren','Verschleudern','Drängen','Ordern','Treffen','Heizen', 'Lüften','Erreichen','Verwechseln','Wehklagen','Halten','Herstellen','Schleudern','Aufwärmen','Klingen',]:
        features = features.replace('number=pl','number=sg')
        features = features.replace('gender=fem','gender=neut')
        features = features.replace('gender=masc','gender=neut')
    elif word == 'Weiterleben' and lemma == 'Weiterleben' and pos == 'NN':
        lemma = 'weiterleben'
    elif word == 'Freien' and lemma == 'Freie' and pos == 'NN':
        lemma = 'freie'
    elif word == 'Gleichwertiges' and lemma == 'gleichwertig' and pos == 'NN':
        lemma = 'gleichwertige'
    elif word == 'möchte' and pos == 'VVFIN':
        pos = 'VMFIN'  
    elif word == 'mußte' and pos == 'VVFIN':
        pos = 'VMFIN'   
    elif word == 'würde' and pos == 'VVFIN':
        pos = 'VAFIN'   
    elif word.endswith('-Jobs') and lemma == word:
        lemma = lemma[:-1]
    elif word == 'Fernseh-' and pos == 'TRUNC':
        lemma = 'Fernseh'
    elif word == 'Kranken-' and pos == 'TRUNC':
        lemma = 'Kranke'
    elif lemma.endswith('aktivisten') and pos == 'NN':
        lemma = lemma[:-2]
    elif lemma == 'Dinosaurier-Hits':
        lemma = 'Dinosaurier-Hit'
    elif lemma == 'DGB-landesvorsitzend':
        lemma = 'DGB-Landesvorsitzende'
    elif lemma.endswith('-vorsitzend') and pos == 'NN':
        lemma = lemma[:-11] + '-Vorsitzende'
    elif lemma.endswith('-ratsvorsitzend') and pos == 'NN':
        lemma = lemma[:-15] + '-Ratsvorsitzende'
    elif word == 'Begünstigten' and lemma == 'begünstigter'	and pos == 'ADJA':
        pos = 'NN'
        lemma = 'begünstigte'
    elif word == 'Mitgefangener' and lemma == 'Mitgefangener'	and pos == 'NN':
        lemma = 'mitgefangene'
    elif lemma.lower() == 'erster'	and pos == 'NN':
        lemma = 'erste'
    elif lemma.lower() == 'zweiter'	and pos == 'NN':
        lemma = 'zweite'
    elif lemma.lower() == 'dritter'	and pos == 'NN':
        lemma  = 'dritte'
    elif lemma.lower() == 'branchendritter'	and pos == 'NN':
        lemma = 'branchendritte'
    elif lemma.lower() == 'ranglisten-zweiter'	and pos == 'NN':
        lemma = 'ranglisten-zweite'
    elif lemma == 'seite' and pos == 'NN':
        lemma = 'Seite'
    elif lemma == 'farbig' and pos == 'NN':
        lemma = 'farbige'
    elif word == 'volksverbunden' and lemma == 'volksverbund':
        lemma = 'volksverbunden'
    elif word == 'uneingeladen' and lemma == 'uneingelad':
        lemma = 'uneingeladen'
    elif word == 'nahe' and lemma == 'nah' and pos == 'ADJD':
        lemma = 'nahe'
    elif word == 'dünne' and lemma == 'dünn' and pos == 'ADJD': #????
        lemma = 'dünne'
    elif word == 'rapide' and lemma == 'rapid' and pos == 'ADJD':
        lemma = 'rapide'
    elif word == 'spitze' and lemma == 'spitz' and pos == 'ADJD':
        lemma = 'spitze'
    elif word.lower() == 'sachte' and lemma == 'sacht'  and pos == 'ADJD':
        lemma = 'sachte'
    elif word.lower() == 'später' and lemma == 'spät' and pos == 'ADJD' and 'degree=pos' in features:
        features = features.replace('degree=pos','degree=comp')
    elif nr == '24052_22' and word == 'temporär' and pos == 'ADJA':
        pos = 'ADJD'
    elif nr == '18067_20' and word == 'enger' and pos == 'ADJD':
        pos = 'ADJA'
    elif word == 'schlechter' and lemma == 'schlecht' and pos == 'ADJD' and 'degree=pos' in features:
        pos = 'ADJA'
    elif word == 'zäher' and lemma == 'zäh' and pos == 'ADJD' and 'degree=pos' in features:
        pos = 'ADJA'
        features = 'case=dat|number=sg|gender=fem|degree=pos'
    elif word == 'vorsichtiger' and lemma == 'vorsichtig' and pos == 'ADJD' and 'degree=pos' in features:
        pos = 'ADJA'
        features = 'case=dat|number=sg|gender=neut|degree=pos'
    elif word == 'dauerhafter' and lemma == 'dauerhaft' and pos == 'ADJD' and 'degree=pos' in features:
        pos = 'ADJA'
        features = 'case=dat|number=sg|gender=fem|degree=pos'
    elif word == 'langem' and lemma == 'lang' and pos == 'ADJD' and 'degree=pos' in features:
        pos = 'ADJA'
        features = 'case=dat|number=sg|gender=fem|degree=pos'
    elif word == 'volltoniger' and lemma == 'volltonig' and pos == 'ADJD' and 'degree=pos' in features:
        features = features.replace('degree=pos','degree=comp')
    elif word == 'weiter' and lemma == 'weit' and pos == 'ADJD' and 'degree=pos' in features:
        features = features.replace('degree=pos','degree=comp')
    elif word == 'täglich' and lemma == 'täglich' and pos == 'ADJD' and 'degree=comp' in features:
        features = features.replace('degree=comp','degree=pos')
    elif pos == 'ADJD' and word == 'jüngst' and lemma == 'jung' and 'degree=sup' in features:
        lemma = 'jüngst'
        pos = 'ADV'
        features = ''

      

    if pos == 'ADJD' and word.lower() != lemma.lower() and word[-1] in ['t','n']  and lemma[-2:] in ['en','rn']:
        lemma = word.lower()
           
    
    if pos == 'ADJA' and lemma.lower() in ['nächster','zweiter','bismarckscher','drittgrößter','zweitgrößter','sogenannter','nächstbester','vorletzter','achter','allerhöchster','dritter','vierter','mittlerer','besonderer','linker','diverser','zweitbester','etlicher','fünfter','sechster','siebter','einiger','einziger','vorletzter','innerer','zweitbester','vorpommerscher','ultrarechter','gewerkschaftseigener','liebgewonnener','anderer', 'hinterer','selber','schröderscher','zehnter','unterer','habermasscher','hallescher','hannoverscher','lisztscher','äußerer','dreizehnter','dritter','elfter','weltgrößter','zehnter','zwanzigster','zweiter','zweitwichtigster','vierter','viertgrößter','vorderer','fünfter','dreizehnter','elfter','erster','nächster','oberer','unterer','meister','erhardscher','zweitstärkster','drittstärkster','zweithöchster','achthöchster','neuntgrößter', 'neunter','drittbester','neunter','allerjugendlichster','dienstältester','allergrößter','jedweder']:
        lemma = lemma[:-2]
    elif pos == 'ADJA' and word[-1] in "sn" and lemma == word[:-1]+'r':
        lemma = lemma[:-2]
    elif pos == 'ADJD' and lemma == 'allerwenigster':
        lemma = 'allerwenigst'
    elif pos == 'ADJD' and lemma == 'vierter':
        lemma = 'viert'
    elif pos == 'ADJD' and lemma == 'nächster':
        lemma = 'nächst'
    

#TODO Hungrigen

    if lemma[0].islower() and word[0].isupper and pos == 'NN':    
       if lemma.endswith('nd'):
           lemma = lemma[0].upper() + lemma[1:] + 'e'
           pos = 'NNA'
       elif lemma.endswith('er') and not word.endswith('er'): # or 'number=pl' not  in features):
           lemma = lemma[0].upper() + lemma[1:-1]
           pos = 'NNA'
       elif lemma.endswith('er') and word.endswith('er') and lemma.lower().endswith(('abgeordneter','angeklagter','angestellter','beauftragter','bediensteter','behinderter','beigeordneter','benachteiligter','beschäftigter','betroffener','delegierter','enttäuschter','ertappter','erwachsener','gefangener','gelehrter','geschädigter','mitbeteiligter','verblendeter','verbündeter','vertriebener','vorgesetzter')):
           lemma = lemma[0].upper() + lemma[1:-1]
           pos = 'NNA'
       elif lemma.endswith('e'):
           if not lemma.startswith('adidas'):
               pos = 'NNA'
               lemma = lemma[0].upper() + lemma[1:]
       elif lemma.endswith('n') and 'number=sg|gender=neut' in features:
           pos = 'NNI'
           lemma = lemma[0].upper() + lemma[1:]
    elif lemma.endswith('er') and pos == 'NN' and not word.startswith(lemma) and word.startswith(lemma[:-1]):
           pos = 'NNA'
           lemma = lemma[:-1]
    elif lemma.lower().endswith(('beamter','beauftragter','vorsitzender','abgeordneter','angestellter','heiliger','gelehrter','reisender','kommandierender','angehöriger','versicherter','erster','jähriger')) and pos == 'NN':
           pos = 'NNA'
           lemma = lemma[:-1]
    elif lemma.lower().endswith('beamte') and pos == 'NN':
           pos = 'NNA'
        
    
   
    return word,lemma,pos,features
  

fin = codecs.open("tiger.16012013.conll09", "r","utf-8")
fout = codecs.open("tiger.16012013.conll09c", "w","utf-8")
    
for line in fin:
    columns = line.split()
    if len(columns) == 15:
        #word,lemma,pos =  columns[1], columns[2], columns[4]
        word, lemma, pos, features = correctlemma(columns[0], columns[1], columns[2], columns[4],columns[6])
        print(columns[0],word,lemma,columns[3],pos,columns[5],features, *columns[7:], sep='\t',end='\n',file=fout)
    else:
        print(line,end='',file=fout)
fout.close() 
fin.close()


    