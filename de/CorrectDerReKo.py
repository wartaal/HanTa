import re
from HanTa import HanoverTagger as ht 
tagger = ht.HanoverTagger('morphmodel_ger.pgz')
tagger.strict = True


NEs = ['Hohle','Bollig','Machbare','Schimpf','Außen','Native','Football','Real','Null','Falsch','Oberstadt',
       'Beamter','Erwerbslos','Nobel','Trupp','Blankenburg','Hackenheim','Rockenhausen',
       'Beermann','Weidmann','Wildberger','Westenthaler','Laumann','Hohlmeier',
       'Kleinmann','Astor','Heidenreichstein','Kingston','Mühlhausen','Eisler',
       'Schillerplatz','Johanniskirche','Kleinfeld','Guckheim','Hammerstein','Mülheimer',
       'Stettiner','Eisenstadt','Friedrichssegen','Lori','Federer','Langenfeld','Wegerle',
      'Löhndorf','Marienfeld','Oberbayer', 'Mariendorf','Marienwerder','Friedrichstadt','Bonanza',
      'Odertal','Belgische','Kirchenbollenbach','Schönhausen','Ukrainische','Haldenstein','Holzendorf',
       'Hennegau','Rheinecker','Wallenstein','Rabenstein','Rheingau','Oberammergau','Flachgau','Dachstein',
      'Tennengau','Turngau','Einstein','Pechstein','Ehrenbreitstein','Torgau','Reichmann','Haselbach','Ölsburg','Reckermann', 
      'Moosmann','Stegmann','Fallmann','Vollmann','Lerchenfeld','Wellmann','Eisermann','Eisermann','Bandmann','Galle', 
       'Niedersachse', 'Bayer', 'Derby', 'Online', 'Klagenfurt', 'Greifswald', 'Braunschweiger', 'Springer', 'Christus', 
       'Bremer', 'First', 'Review', 'Schwede', 'Queen', 'Weinheim', 'Major', 'Turner', 'Volksbank', 'Hamas', 'Ostsee', 
       'Rheintal',  'Philippe', 'Vatikan', 'Trittin', 'Commerzbank', 'Friedhelm', 'Rösler', 'Modern', 'Mittelmeer', 
       'Baumeister', 'Porto',  'Walker', 'Napoleon', 'Special', 'Venus', 'Haller', 'Engel', 'Kreml', 'Sachse', 'Guide', 
       'Weltbank', 'Friedland', 'Binder',  'Jeans', 'Court', 'Studio', 'Warner', 'Polster', 'Sierra', 'Madeleine', 
       'Schwarzwald', 'Parker', 'England', 'Ulmer', 'Baker',  'Hisbollah', 'Bordeaux', 'Javier', 'Tagesspiegel', 
       'Hausen', 'Avenue', 'Berlinale', 'Board', 'Töpfer', 'Odenwald', 'Schweiger', 'Wächter', 'Ebner', 'Holland', 
       'Broadway', 'Marienkirche', 'Erzgebirge', 'Schwede', 'Merkur', 'Marshall', 'Eberswald', 'Rheinpfalz', 
       'Tagesschau', 'Brockhaus', 'Oberland', 'Memorial', 'Elfenbeinküste', 'Trumpf', 'Harm', 'Square', 'Postbank', 
       'Butler', 'Crash', 'Sauerland', 'Aristoteles', 'Tempelhof', 'Future', 'Schlegel', 'Figaro', 'Vesper', 'Gestapo', 
       'Burgtheater',  'Volkswagen', 'Eurosport', 'Pentagon', 'Alexanderplatz', 'Antarktis', 'Capitol', 'Schweinfurt', 
       'Atlantik', 'Trust', 'Bundesbahn', 'Fidel', 'Bohle', 'Stocker', 'Schwarzenegger','Buchenwald', 'Hiller', 
       'Rußland', 'Jaguar', 'Junker', 'Juso', 'Enterprise', 'Brunn', 'Hochtief', 'Flandern', 'Bundeskriminalamt', 
       'Portland', 'Präsent', 'Alpha', 'Bloch', 'Büttner', 'Baptist', 'Diamond', 'Wedel', 'Schuler', 'Lotus', 'Weingarten', 
       'Rubin', 'Banking', 'Reimer', 'Napoleon', 'Interfax', 'Bertrand', 'Lausitz', 'Nahost', 'Aston', 'Fuchs', 'Kaufhof', 
       'Schwarzkopf', 'Telegraph', 'Bayer', 'Mähre', 'Ferrari', 'Fischler', 'Kaschmir', 'Schirmer', 'Saarland', 'Center', 
       'Pazifik', 'Götze', 'Frauenkirche', 'Sager', 'Sattler',  'Schreiber', 'Schröter', 'Passat', 'Waldheim', 'Krenz', 
       'Hanse', 'Himmler', 'Television', 'Sylvester', 'Dschihad', 'Klinger', 'Hager', 'Ungar', 'Bergheim', 'Barmer', 
       'Waldeck', 'Stories', 'Attila', 'Wendland', 'Château', 'Anger', 'Nicolaus', 'Tribun', 'Schleicher', 'Mineral', 
       'Weißrußland', 'Heiligendamm', 'Kurfürstendamm', 'Weber', 'Neukirche', 'Deutschlandradio', 'Reiser', 'Rang', 
       'Salsa', 'Duden', 'Osmane', 'Sprengel', 'Train', 'Groove', 'Pollen', 'Zwickel', 'Flamenco', 'Freytag', 'Wattenmeer', 
       'Fechter', 'Hepatitis', 'Voltaire', 'Bundesverkehrsministerium', 'Water', 'Bubi', 'Stockhausen', 'Ernst', 
       'Automotiv', 'Bond', 'Erle', 'Camp', 'Seidler', 'Evergreen', 'Omega', 'Marge', 'Vatikan', 'Kreuzkirche', 
       'Investment', 'Mittelland', 'Tamil', 'Faßbinder', 'Bacon', 'Eurofighter', 'Pantheon', 'Hanser', 'Spindler', 
       'Saarland', 'Niederland', 'Renault', 'Hirsch', 'Kreuzer', 'Paulskirche', 'Progressive', 'Peugeot', 'Flach', 
       'Ruhrgas', 'Duma', 'Hagedorn', 'Bunte', 'Rheinpfalz', 'Mephisto', 'Knigge',  'Klagenfurt', 'Eurostat', 'Asmuße', 
       'Tagesschau', 'Schlemmer', 'Kühne', 'Delle', 'Furtwängler', 'Yard', 'Friedewald',  'Bundesrechnungshof', 
       'Bundesnachrichtendienst', 'Weissenberger', 'Trash', 'Fürstenwald', 'Tagesthema', 'Siebeck', 'Europarat',  
       'Ostwestfale', 'Vogtland', 'Marder', 'Baptist', 'Junker', 'Holde', 'Eldorado', 'Bonhoeffer', 'Braune', 
       'Ravensburger', 'Schliere', 'Hochheim', 'Point', 'Petersplatz', 'Sterling', 'Tannhaus', 'Royals', 'Allende', 
       'Transportation', 'Tran',  'Ostwald', 'Diamond', 'Weichsel', 'Lore', 'Rennweg', 'Sprint', 'Automation', 'Rambo', 
       'Lorenzen', 'Nordfriesland',  'Bregenzerwald', 'Ulysses', 'Wall', 'Better', 'Wildbad', 'Gesamtmetall', 
       'Nordkaukasus', 'Koppelin', 'Piller', 'Frauenkirche',  'Schwanensee', 'Mastershausen', 'Dietrich', 'Wismut', 
       'Ayatollah', 'Burgenland', 'Gazastreifen', 'Rheinmetall', 'Handling',  'Scheele',  'Bourgeois', 'Europol', 
       'Heldenplatz', 'Südwestfunk', 'Normanne', 'Port', 'Tümpel', 'Navigator',  'Ruhrgebiet', 'Grobe', 'Turner', 
       'Jamal', 'Nonnenmacher', 'Volksgarten', 'Mercedes', 'Schwarzenberger', 'Hoffer', 'Reimer', 'Grimm',  'Romani', 
       'Frankfurt', 'Magyar', 'Rheinberger', 'Trinkaus', 'Riff', 'Patton', 'Hagen', 'Barre', 'Burgtheater', 'Senger',  
       'Ostende', 'Ehrenhof', 'Food', 'Härter', 'Wehler', 'Stelzer', 'Future', 'Neckarwestheim', 'Baumeister', 'Kreml', 
       'Patte', 'Nissan', 'Holend', 'Guide', 'Weber', 'Diller', 'Galle', 'Tagesspiegel',  'Horst', 'Schartau', 'Maxhütte', 
       'Ripper', 'Himmler',  'Nordatlantik', 'Wall', 'Huster', 'Schüssler', 'Card', 'Malin', 'Fritze', 'Magyar', 'Court', 
       'Roderich', 'Justitia', 'Bouillon', 'Talabanus', 'Wiesehügel', 'Anger', 'Mittenwald', 'Reiher', 'Hutton', 'Hopp', 
       'Nordsee', 'Ostdeutschland', 'Küchler', 'Bolzen', 'Fleckenstein', 'Hoch', 'Metzmacher',  'Bolle', 'Garbe', 
       'Westjordanland', 'Forint', 'Plateau', 'Nordhesse', 'Nickel',   'Bernstein', 'Outback', 'Springer', 'Farin', 
       'Special', 'Marienbad', 'Heller', 'Hinterzarte', 'Henkel', 'Kaschmir', 'Götze', 'Mittelmeer', 'Schorfheide', 
       'Peninsula', 'Karatschi', 'Eurotunnel', 'Kleinwort', 'Höhler', 'Steinhausen', 'Morsleben', 'Setzer', 'Niesen', 
       'Vetter', 'Türkis', 'Apollo', 'Pierrot', 'Rheinebene', 'Mette', 'Handelsblatt', 'Telefunken', 'Leise', 'Port', 
       'Nirwana', 'Intershop', 'Sonderegger','Neuengamme','Kolosseum','Limes','Akademietheater','Andreaskirche']

def read_dereko_words(dereko_file):
    data = []
    with open(dereko_file,'r',encoding = 'utf8') as f:
        for line in f:
            columns = line.split()
            if len(columns) == 4:
                word,lemma,pos =  columns[0].strip(), columns[1].strip(), columns[2].strip()
                if pos[0] == 'V' and lemma != 'UNKNOWN' and lemma != 'unknown' and '|' not in lemma:
                    if pos == 'VVINF':
                        match = re.fullmatch(r'(.+)zu(.+)',word)
                        if match and lemma == match[1]+match[2]:
                            pos = 'VVIZU'   
                    data.append((word,lemma,pos)) 
                    
                #NN und NE werden zu häufig verwechselt in Dereko. Nicht ohne weiteres Nutzbar.                    
                elif pos == 'NN' and len(word) > 4 and lemma != 'UNKNOWN' and lemma != 'unknown' and re.fullmatch(r'\w+',word) and '|' not in lemma and lemma not in NEs: 
                    lemma1, pos1 = tagger.analyze(word)
                    #if pos1 != pos or lemma1 != lemma:
                    #    print(word,pos,lemma,pos1,lemma1)
                    if lemma[-1:] == 'ß':
                        continue
                    if pos1 == 'NNA' :
                        continue
                    if pos1 == 'NNI' :
                        continue
                    if pos1 == 'ADJ(A)':
                        continue
                    if pos1 == 'ADJ(D)' and lemma != 'Paradox':
                        continue
                    if lemma.endswith('straße'):
                        continue
                    if lemma.endswith('dorf'):
                        continue
                    if lemma.endswith('berg'):
                        continue
                    if lemma.endswith('feld'):
                        continue
                    if lemma.endswith('stadt'):
                        continue 
                    if lemma.endswith('mann'):
                        continue 
                    if lemma.endswith('bach'):
                        continue 
                    if lemma.endswith('burg'): 
                        continue 
                    if lemma.endswith('n') and word in ['Können','Könnens','Wirtschaften','Wirtschaftens','Vorgehen','Vorgehens','Leiden','Leidens','Gedenken','Gedenkens','Aufheben','Aufhebens','Bebens','Beben','Aussehen','Aussehens','Essens','Treiben','Treibens','Graben','Grabens','Ausscheiden','Ausscheidens','Reisens','Reisen','Treffens','Treffen','Rennens','Rennen','Wollen','Wollens','Taumeln','Taumelns','Scherzens','Scherzen','Parken','Parkens']:
                        pos = 'NNI'
                    data.append((word,lemma,pos)) 
                    #gleichaltrige --> NNA
                elif pos in ['ADJA','ADJD','ADV'] and len(word) > 4 and lemma != 'UNKNOWN' and lemma != 'unknown' and re.fullmatch(r'\w+',word) and '|' not in lemma:
                    lemma1, pos1 = tagger.analyze(word)
                    #if pos1 == 'ADJ(A)':
                    #    pos1 = 'ADJA'
                    #if pos1 == 'ADJ(D)':
                    #    pos1 = 'ADJD'
                    #if pos1 != pos or lemma1 != lemma:
                        #print(word,pos,lemma,pos1,lemma1)
                    if pos1 == 'VV(PP)' :
                        continue
                    if word in ['verwendete','Weblinks','Nobelpreisträger','postwendend','ebensoviel','einher','bezüglich','allabendlich','drüber','sattsam','allermeisten','grosser']: # Fehlerhafter Eintrag
                        continue
                    #routiniert, diskutiert
                    data.append((word,lemma,pos)) 
    return data

Data = read_dereko_words(r'DeReKo-2014-II-MainArchive-STT.100000.freq')


fout = open("DeReKo-2014-II_selected.tsv", "w", encoding = "utf-8")
    
for word, lemma, pos in Data:
    print(word,lemma,pos, sep='\t',end='\n',file=fout)
fout.close()





