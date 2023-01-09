import codecs
from collections import Counter

def read_sonar_words(sonar_csv_file):
    data = []

    with codecs.open(sonar_csv_file,'r','utf8') as f:
        for line in f:
            columns = line.split()
            data.append(columns)
    return data

def repair(lines):
    repaired = []
    
    prevword = ''
    for  tuple in lines:
        if len(tuple) != 7:
            #print(tuple)
            continue
        sentnr,wordnr,word,lemma,root,upos,postag = tuple
        
        if lemma == 'FOUT!!' and word == 'Verenigde':
            lemma = 'Verenigd'
        elif word == 'gedronkem' and lemma == 'drinken':
            word = 'gedronken'
        elif word == 'gewond' and lemma == 'verwonden':
            postag = 'ADJ(vrij,basis,zonder)'
            lemma = 'gewond'
        elif word == 'politi' and lemma == 'politi':
            word = 'politie' 
            lemma = 'politie'
        elif word == 'kasplantje' and lemma == 'kasplantje':
            lemma = 'kasplant'
        elif word == 'vrije' and lemma == 'vrijetijdskleding':
            lemma = 'vrij'
        elif word == 'tijdskleding' and lemma == 'vrijetijdskleding':
            lemma = 'tijdskleding' 
        elif word  == 'name' and lemma == 'met':
            lemma = 'naam'
        elif word == 'Start' and lemma == 'starten' and postag == 'N(eigen,ev,basis,genus,stan)':
            lemma = 'Start'
            postag = 'N(eigen,ev,basis,zijd,stan)'
        elif word == 'voetballen' and lemma == 'voetbal' and postag == 'N(soort,ev,basis,zijd,stan)':
            postag = 'N(soort,mv,basis)'
        elif word == 'zaak-Houins' and postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)'
        elif word == 'onderzoeken'  and lemma ==  'onderzoeken' and postag == 'N(soort,mv,basis)':
            lemma = 'onderzoek'
        elif word == 'huisregels'  and lemma ==  'huisregels' and postag == 'N(soort,mv,basis)':
            lemma = 'huisregel'
        elif word == 'testen'  and lemma ==  'testen' and postag == 'N(soort,mv,basis)':
            lemma = 'test'
        elif word == 'verder' and (postag == 'ADJ(vrij,comp,zonder)' or postag == 'ADJ(vrij,basis,zonder)'):
            lemma = 'ver'
            postag = 'ADJ(vrij,comp,zonder)'
        elif word == 'vroeger' and lemma == 'vroeger' and postag[:3] == 'ADJ':
            lemma = 'vroeg'
        elif word == 'sterkste'  and lemma ==  'sterk' and postag == 'ADJ(nom,basis,met-e,zonder-n,stan)':
            postag = 'ADJ(nom,sup,met-e,zonder-n,stan)'
        elif word == 'vaste'  and lemma ==  'aanstaande':
            lemma = 'vast'
            postag = 'ADJ(prenom,basis,met-e,stan)'
        elif word == 'verkoopcijfers'  and lemma ==  'verkoopcijfers' and postag == 'N(soort,mv,basis)':
            lemma = 'verkoopcijfer'
        elif word == 'adresgegevens'  and lemma ==  'adresgegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'adresgegeven'
        elif word == 'bevolkingsgegevens'  and lemma ==  'bevolkingsgegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'bevolkingsgegeven'
        elif word == 'informaticagegevens'  and lemma ==  'informaticagegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'informaticagegeven'
        elif word == 'prikklokgegevens'  and lemma ==  'prikklokgegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'prikklokgegeven'
        elif word == 'inkomensgegevens'  and lemma ==  'inkomensgegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'inkomensgegeven'
        elif word == 'Oudergegevens'  and lemma ==  'oudergegevens' and postag == 'N(soort,mv,basis)':
            lemma = 'oudergegeven'
        elif word == 'bestaand'  and postag == 'WW(vd,vrij,zonder)':
            postag = 'WW(od,vrij,zonder)'
        elif word == 'beëindigend'  and postag == 'WW(vd,vrij,zonder)':
            postag = 'WW(od,vrij,zonder)'
        elif word == 'stigmatiserend'  and postag == 'WW(vd,vrij,zonder)':
            postag = 'WW(od,vrij,zonder)'
        elif word == 'passende'  and postag == 'WW(vd,prenom,met-e)':
            postag = 'WW(od,prenom,met-e)'
        elif word == 'grievende'  and postag == 'WW(vd,prenom,met-e)':
            postag = 'WW(od,prenom,met-e)'
        elif word == 'aangekomen'  and postag == 'WW(inf,vrij,zonder)':
            postag = 'WW(vd,vrij,zonder)'
        elif word  == 'gilden' and lemma == 'gild':
            lemma = 'gilde'
        elif word  == 'waarden' and lemma == 'waard': #De waard uit de kroeg komt in de Data niet voor
            lemma = 'waarde'
        elif word  == 'quota' and lemma == 'quota':
            lemma = 'quotum'
        elif word  == 'tariefquota' and lemma == 'tariefquota':
            lemma = 'tariefquotum'
        elif word  == 'importquota' and lemma == 'importquota':
            lemma = 'importquotum'
        elif word  == 'lagen' and lemma == 'liggen' and postag == 'N(soort,mv,basis)':
            lemma = 'laag'
        elif word  == 'gewonnen' and lemma == 'gewinnen' and postag[:5] == 'WW(vd':
            lemma = 'winnen'
        elif lemma == 'tassen' and postag[:2] == 'WW':
            lemma = 'tasten'
        elif word == 'onstonden' and lemma == 'onstaan':
            word = 'ontstonden'
            lemma = 'ontstaan'
        elif word == 'onstaat' and lemma == 'onstaan':
            word = 'ontstaat'
        elif word == 'onstaan' and lemma == 'onstaan':
            word = 'ontstaan'
        elif word == 'uigeprocedeerde':
            word = 'uitgeprocedeerde'
        elif word == 'zwakken' and lemma == 'afzwakken':
            lemma = 'zwakken'
        elif word == 'beïnvloed' and lemma == 'beïvloeden':
            lemma = 'beïnvloeden'
        elif word == 'taalontwikkingsstoornissen' and lemma == 'taalontwikkingsstoornis':
            word = 'taalontwikkelingsstoornissen'
            lemma = 'taalontwikkelingsstoornis'  
        elif word == 'zakenavocaten' and lemma == 'zakenavocaat':
            word = 'zakenadvocaten'
            lemma = 'zakenadvocaat'  
        elif word == 'corpulentere' and postag == 'ADJ(prenom,basis,met-e,stan)':
            postag == 'ADJ(prenom,comp,met-e,stan)'
        elif word == 'sensationeelste' and postag == 'ADJ(prenom,basis,met-e,stan)':
            postag == 'ADJ(prenom,sup,met-e,stan)'  
        elif word == 'Taalwetwijzer' and postag == 'ADJ(vrij,basis,zonder)':
            lemma == 'Taalwetwijzer' 
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'plezantst' and lemma == 'plezant' and postag == 'ADJ(vrij,comp,zonder)':    
            postag = 'ADJ(vrij,sup,zonder)' 
        elif word == 'uitgebreider' and lemma == 'uitbreiden' and postag == 'ADJ(vrij,comp,zonder)':
            lemma = 'uitgebreid'
            postag = 'ADJ(vrij,comp,zonder)'
        elif word == 'voorste' and lemma == 'voor' and postag == 'ADJ(prenom,basis,met-e,stan)':    
            lemma = 'voorst' 
        elif word == 'smalst' and lemma == 'smal' and postag == 'ADJ(vrij,comp,zonder)':
            postag = 'ADJ(vrij,sup,zonder)' 
        elif word == 'wegheeft' and lemma == 'hebben' :    
            lemma = 'weghebben' 
        elif word == 'wegheeft' and lemma == 'hebben' :    
            lemma = 'weghebben' 
        elif word == 'inhangt' and lemma == 'hangen' :    
            lemma = 'inhangen' 
        elif word == 'geleidden' and lemma == 'leiden' :    
            lemma = 'geleiden' 
        elif word == 'gedragen' and lemma == 'dragen' and postag == 'WW(inf,vrij,zonder)':    
            postag = 'WW(vd,vrij,zonder)'
        elif word == 'gebeurd' and lemma == 'beuren' and postag == 'WW(pv,tgw,met-t)':    
            lemma = 'gebeuren'
            word = 'gebeurt'
        elif word == 'onbegrijpelijk' and lemma == 'begrijpelijk':    
            lemma = 'onbegrijpelijk'
        elif word == 'enqutecommissie' and lemma == 'enqutecommissie':    
            lemma = 'enquetecommissie'
            word = 'enquetecommissie'
        elif word == 'opleit' and lemma == 'pleiten':    
            word = 'pleit'
        elif word == 'hervormingsvoorstellen' and lemma == 'y':    
            lemma = 'hervormingsvoorstel'
        elif word == 'geleidt' and lemma == 'leiden' and postag == 'WW(vd,vrij,zonder)':    
            word = 'geleid'
        elif word == 'bekleedt' and lemma == 'bekleden' and postag == 'WW(vd,vrij,zonder)':    
            word = 'bekleed'
        elif word == 'kan' and lemma == 'kan' and postag == 'WW(pv,tgw,ev)':
            lemma = 'kunnen'
        elif word == 'kon' and lemma == 'kon' and postag == 'WW(pv,verl,ev)':
            lemma = 'kunnen'
        elif word == 'toon' and lemma == 'toon' and postag == 'WW(pv,tgw,ev)':
            lemma = 'tonen'
        elif word == 'MOETEN' and lemma == 'moeten' and postag == 'WW(pv,tgw,ev)':
            postag = 'WW(pv,tgw,mv)'
        elif word == 'begonnen' and lemma == 'beginnen' and postag == 'WW(pv,tgw,met-t)':
            postag = 'WW(pv,verl,mv)'
        elif word == 'verlopen' and lemma == 'verlopen' and postag == 'WW(pv,tgw,met-t)':
            postag = 'WW(pv,tgw,mv)'
        elif word == 'bewogen' and lemma == 'bewegen' and postag == 'WW(pv,verl,ev)':
            postag = 'WW(pv,verl,mv)'
        elif word == 'kan' and lemma == 'kunnen' and postag == 'N(soort,ev,basis,zijd,stan)':
            postag = 'WW(pv,tgw,ev)'
        elif word == 'factoren' and lemma == 'factoor':
            lemma = 'factor'
        elif word == 'leen' and lemma == 'leen' and postag == 'WW(inf,vrij,zonder)':
            lemma = 'lenen'
        elif word == 'ontginnging' and lemma == 'ontginnging':
            lemma = 'ontginning'
            word = 'ontginning'
        elif word == 'komt' and lemma == 'binnenkomen':
            lemma = 'komen'
        elif word == 'allereerst' and lemma == 'één':
            lemma = 'allereerst'
        elif word == 'allereerste' and lemma == 'één':
            lemma = 'allereerst'
        elif word == 'PvdA-partijvoorzitter' and lemma == 'PvdA-voorzitter':
            lemma = 'PvdA-partijvoorzitter'
        elif word == 'overgangsjaren' and lemma == 'overgangsjaren' and postag == 'N(soort,mv,basis)':
            lemma = 'overgangsjaar'  
        elif word == 'boekdelen' and lemma == 'boekdelen':
            lemma = 'boekdeel' 
        elif word == 'condoleances' and lemma == 'condoleances':
            lemma = 'condoleance'   
        elif word == 'natuurwetenschappen' and lemma == 'natuurwetenschappen':
            lemma = 'natuurwetenschap' 
        elif word == 'menswetenschappen' and lemma == 'menswetenschappen':
            lemma = 'menswetenschap' 
        elif word == 'loonlasten' and lemma == 'loonlasten':
            lemma = 'loonlast' 
        elif word == 'kleerscheuren' and lemma == 'kleerscheuren':
            lemma = 'kleerscheur' 
        elif word == 'lijken' and lemma == 'lijken' and postag == 'N(soort,mv,basis)':
            lemma = 'lijk' 
        elif word == 'Vlaams-Blok-brochures' and lemma == 'Vlaams-Blok-brochures':
            lemma = 'Vlaams-Blok-brochure' 
        elif word == 'bierrecensies' and lemma == 'bierrecensies':
            lemma = 'bierrecensie' 
        elif word == 'autopapieren' and lemma == 'autopapieren':
            lemma = 'autopapier' 
        elif word == 'identiteitspapieren' and lemma == 'identiteitspapieren':
            lemma = 'identiteitspapier' 
        elif lemma == 'kostbaarheden':
            lemma = 'kostbaarheid'
        elif lemma == 'benodigdheden':
            lemma = 'benodigdheid' 
        elif word == 'burgerdoelen' and lemma == 'burgerdoelen':
            lemma = 'burgerdoel' 
        elif lemma == 'handelsbetrekkingen':
            lemma = 'handelsbetrekking' 
        elif lemma == 'levensomstandigheden':
            lemma = 'levensomstandigheid' 
        elif lemma == 'weerssomstandigheden':
            lemma = 'weersomstandigheid' 
        elif lemma == 'toekomstmogelijkheden':
            lemma = 'toekomstmogelijkheid' 
        elif word == 'Vergisten' and lemma == 'vergisten' and postag == 'N(soort,mv,basis)':
            postag = 'WW(inf,vrij,zonder)'
        elif word == 'kolen' and lemma == 'kolen':
            lemma = 'kool' 
        elif word == 'Polen' and lemma == 'Polen' and  postag == 'N(soort,mv,basis)':
            lemma = 'Pool' 
        elif word == 'roofvliegen' and lemma == 'roofvliegen':
            lemma = 'roofvlieg' 
        elif word == 'verkoopcijfers' and lemma == 'verkoopcijfers':
            lemma = 'verkoopcijfer' 
        elif word == 'mensachtigen' and lemma == 'mensachtigen':
            lemma = 'mensachtige' 
        elif word == 'luchtstrijdkrachten' and lemma == 'luchtstrijdkrachten':
            lemma = 'luchtstrijdkracht' 
        elif word == 'werkzaamheden' and lemma == 'werkzaamheden':
            lemma = 'werkzaamheid' 
        elif word == 'NGO-campagnes' and lemma == 'NGO-campagnes':
            lemma = 'NGO-campagne' 
        elif word == 'douaneformaliteiten' and lemma == 'douaneformaliteiten':
            lemma = 'douaneformaliteit' 
        elif word == 'douaneprocedures' and lemma == 'douaneprocedures':
            lemma = 'douaneprocedure' 
        elif word == 'EHBO-verenigingen' and lemma == 'EHBO-verenigingen':
            lemma = 'EHBO-vereniging' 
        elif word == 'huisregels' and lemma == 'huisregels':
            lemma = 'huisregel' 
        elif word == 'onthoudingsverschijnselen' and lemma == 'onthoudingsverschijnselen':
            lemma = 'onthoudingsverschijnsel' 
        elif word == 'A3-vergrotingen' and lemma == 'A3-vergrotingen':
            lemma = 'A3-vergroting' 
        elif word == 'verdragstaten' and lemma == 'verdragstaten':
            lemma = 'verdragstaat' 
        elif word == 'pianorecitals' and lemma == 'pianorecitals':
            lemma = 'pianorecital' 
        elif word == 'gammastralen' and lemma == 'gammastralen':
            lemma = 'gammastraal' 
        elif word == 'alfastralen' and lemma == 'alfastralen':
            lemma = 'alfastraal' 
        elif word == 'alarmroepen' and lemma == 'alarmroepen':
            lemma = 'alarmroep' 
        elif word == 'leermoeilijkheden' and lemma == 'leermoeilijkheden':
            lemma = 'leermoeilijkheid' 
        elif word == 'glycerolen' and lemma == 'glycerolen':
            lemma = 'glycerol' 
        elif word == 'papieren' and lemma == 'papieren':
            lemma = 'papier' 
        elif word == 'dopvruchten' and lemma == 'dopvruchten':
            lemma = 'dopvrucht' 
        elif word == 'noten' and lemma == 'noten':
            lemma = 'noot' 
        elif word == 'wegenwerken' and lemma == 'wegenwerken':
            lemma = 'wegenwerk' 
        elif word == 'HR-ketels' and lemma == 'HR-ketels':
            lemma = 'HR-ketel' 
        elif lemma == 'parcours' and postag == 'N(soort,mv,basis)':
            postag == 'N(soort,ev,basis,onz,stan)'
        elif lemma == 'reisadvies' and postag == 'N(soort,mv,basis)':
            postag == 'N(soort,ev,basis,onz,stan)'
        elif lemma == 'pluimvee' and postag == 'N(soort,mv,basis)':
            postag == 'N(soort,ev,basis,onz,stan)'
        elif word == 'onderzoeken' and lemma == 'onderzoeken' and  postag == 'N(soort,mv,basis)':
            lemma = 'onderzoek' 
        elif word == 'testen' and lemma == 'testen' and  postag == 'N(soort,mv,basis)':
            lemma = 'test' 
        elif word == 'verkoopcijfers' and lemma == 'verkoopcijfers':
            lemma = 'verkoopcijfer'
        elif word == 'collegegelden' and lemma == 'collegegelden':
            lemma = 'collegegeld' 
        elif word == 'collegelden' and lemma == 'collegelden':
            lemma = 'collegegeld' 
            word = 'collegegelden' 
        elif word == 'mannenbroeders' and lemma == 'mannenbroeders':
            lemma = 'mannenbroeder' 
        elif word == 'argusogen' and lemma == 'argusogen':
            lemma = 'argusoog'
        elif lemma == 'kuren' and postag == 'N(soort,mv,basis)':
            lemma = 'kuur'
        elif word == 'getuigen' and lemma == 'getuigen' and  postag == 'N(soort,mv,basis)':
            lemma = 'getuige' 
        elif word == 'verkoopsvoorwaarden' and lemma == 'verkoopsvoorwaarden':
            lemma = 'verkoopsvoorwaarde' 
        elif word == 'logies' and lemma == 'logie':
            lemma = 'logies'
        elif word == '3D-beelden' and lemma == '3D-beelden':
            lemma = '3D-beeld' 
        elif word == 'horeca-vakbeurs' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'geitenvlees' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'pluimveevlees' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'theejongen' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)'
        elif word == 'isbn' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'afstemmingsproces' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == 'coördinatievermogen' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,onz,stan)' 
        elif word == 'medebeschuldigde' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)'
        elif word == 'buitengrens' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'gevelsteen' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'berenmuts' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'nijlbaars' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'mecanicien' and  postag == 'N(soort,mv,basis)':
            lemma = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'dagbladpers' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'triomfwagen' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'pantserwagen' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'zinsgrens' and  postag == 'N(soort,mv,basis)':
            postag = 'N(soort,ev,basis,zijd,stan)' 
        elif word == 'aanvalsstrategie' and postag == 'N(soort,ev,dim,onz,stan)':
            postag = 'N(soort,ev,basis,zijd,stan)'
        elif word == 'Hoofdlijnenakkoord' and postag == 'N(soort,ev,dim,onz,stan)':
            postag = 'N(soort,ev,basis,onz,stan)'   
        elif word == 'gevaarte' and postag == 'N(soort,ev,dim,onz,stan)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word == lemma and postag == 'N(soort,ev,dim,onz,stan)':
            postag = 'N(soort,ev,basis,onz,stan)'
        elif word[:-1] == lemma and word[-1] == 's'   and postag == 'N(soort,mv,dim)':
            postag = 'N(soort,mv,basis)'
        elif word == 'tropen' and lemma == 'troop' and prevword == 'Duitse':
            lemma = 'troep' 
            word = 'troepen'
        elif word == 'tropen' and lemma == 'troop':
            lemma = 'tropen' 
        elif word == 'veel' and lemma == 'teveel':
            lemma = 'veel' 
            root = 'veel'
        elif word == 'is' and lemma == 'in':
            word = 'in'
        elif lemma == 'vraag' and postag[:2] == 'WW':
            lemma = 'vragen'
        elif word.lower() == 'gevoelens' and lemma == 'gevoel' and postag == 'N(soort,mv,basis)':
            lemma = 'gevoelen'
        elif word.lower() == 'haatgevoelens' and lemma == 'haatgevoel' and postag == 'N(soort,mv,basis)':
            lemma = 'haatgevoelen'
        elif lemma == 'gevoelen' and postag[:2] == 'WW':
            lemma = 'voelen'
        elif word == 'kosten' and lemma == 'kost' and postag == 'N(soort,mv,basis)':
            lemma = 'kosten'
        elif word == 'telefoonkosten' and lemma == 'telefoonkost':
            lemma = 'telefoonkosten'
        elif word == 'verzekeringskosten' and lemma == 'verzekeringskost':
            lemma = 'verzekeringskosten'
        elif  lemma == 'mix-producten':
            lemma = 'mix-product'
        elif word == 'mij' and lemma == 'me':
            lemma = 'mij' 
        elif word == 'ons' and postag == 'VNW(pr,pron,obl,vol,1,mv)' and upos == 'det':
            postag = 'VNW(bez,det,stan,vol,1,mv,prenom,zonder,evon)'
        elif lemma == 'het' and postag == 'LID(bep,stan,evon)' and (int(sentnr),int(wordnr)) in [(11,0),(168,0),(2609,0),(4536,4),(4842,6),(4958,3),(4958,21),(5083,3),(6964,0),(7557,0),(8485,8),(48021,8),(50304,15)]:
            postag = 'VNW(pers,pron,stan,red,3,ev,onz)'
        elif word == 'die' and postag == 'VNW(aanw,det,stan,prenom,zonder,rest)' and int(sentnr) in [24,547,2948,6204]:
            postag = 'VNW(betr,pron,stan,vol,persoon,getal)'
        elif word == 'Namen' and int(sentnr) in [7145,10972,12531,12546,12570,12595,12631,12744,12957,12960,12965,14248,14662,14675,14683,14685,14686,14687,14688,14690,14693,18929,19125,51835,]:
            lemma = 'Namen'
            postag = 'N(eigen,ev,basis,onz,stan)'
        elif postag == 'ADJ(vrij,sup,zonder)' and word.lower() in  ['allereerst']:
            postag = 'BW()'
        elif postag == 'ADJ(vrij,basis,zonder)' and word.lower()  in  ['natuurlijk','bijelkaar','quasi','pal','tamelijk','dadelijk']: #natuurlijk niet allemaal, maar wel bijn allemaal
            postag = 'BW()'
        elif postag.startswith('ADJ') and word.lower()  in  ['vaak','vaker','vaakst']:
            postag = 'BW()'
        elif postag == 'BW()' and word.lower()  in ['louter','eventueel','bijtijds','landinwaarts','onverwachts']:
            postag = 'ADJ(vrij,basis,zonder)' 
        elif word == 'vol' and postag.startswith('ADJ') and int(sentnr) in [174,208,1922,4238,5289,6025,8268,10779,23273,24875,25201,27516,34917,38103,40932,41069,41771,45462,45785,47082,49924,50250,50803,51243,]:
            postag = 'ADJ(postnom,basis,zonder)' 
        elif word.startswith('http://') and postag.startswith('N(soort'):
            postag = 'SPEC(symb)'
        elif word == 'Smelten' and postag == 'N(soort,mv,basis)':
            postag = 'WW(inf,vrij,zonder)'
            lemma = 'smelten'
        elif word == 'geworden' and lemma == 'geworden' and postag == 'WW(vd,vrij,zonder)':
            lemma = 'worden'
        elif word == 'voldaan' and lemma == 'voldaan' and postag == 'WW(vd,vrij,zonder)':
            lemma = 'voldoen'
        elif word == 'maakt' and lemma == 'maakt':
            lemma = 'maken'
        elif word == 'hielden' and lemma == 'hielen':
            lemma = 'houden'
        elif word == 'overvallen' and sentnr == '15468':
            lemma = 'overval'
            postag = 'N(soort,mv,basis)'
        elif lemma == 'voldoend' and postag.startswith('ADJ'):
            lemma = 'voldoende'
        elif lemma == 'onvoldoend' and postag.startswith('ADJ'):
            lemma = 'onvoldoende'
        #elif word == 'gemiddelde' and postag == 'N(soort,ev,basis,onz,stan)':
        #    lemma = 'gemiddeld'
        #    postag = 'ADJ(nom,basis,met-e,zonder-n,stan)'
        #elif word == 'gewonde' and postag == 'N(soort,ev,basis,onz,stan)':
        #    lemma = 'gewond'
        #    postag = 'ADJ(nom,basis,met-e,zonder-n,stan)'
        #elif word == 'gewonden' and postag == 'N(soort,mv,basis)':
        #    lemma = 'gewond'
        #    postag = 'ADJ(nom,basis,met-e,mv-n)'
        elif lemma in ['verslaafde','leidinggevende','jarige','vermiste','schuldige','illegale','genodigde','geleerde','gelovige','gehandicapte','actieve','gemiddelde','gewonde','schuldige','ondergrondse','reactionaire','verpleegkundige','heilige','mensachtige']:
            lemma = lemma[:-1]
            if postag == 'N(soort,ev,basis,onz,stan)':
                postag = 'ADJ(nom,basis,met-e,zonder-n,stan)'
            elif postag == 'N(soort,mv,basis)':
                postag = 'ADJ(nom,basis,met-e,mv-n)'
            
            

            
        repaired.append((sentnr,wordnr,word,lemma,root,upos,postag))
        prevword = word
    return repaired


def remove_foreign(wordlist): #remove all sentences with more than 50% foreign words
    reduced = []
    
    sentence = []
    lastsentnr = -1
    nrForeign = 0
    
    for row in wordlist:
        if len(row) != 7:
            continue
        sentnr,wordnr,word,lemma,root,upos,postag = row
        if sentnr != lastsentnr:
            if sentence != [] and nrForeign <= len(sentence)/2:
                reduced.extend(sentence)
            sentence = [] 
            lastsentnr = sentnr
            nrForeign = 0
        sentence.append(row)
        if postag == 'SPEC(vreemd)':
            nrForeign+=1
    if sentence != [] and nrForeign <= len(sentence)/2:
        reduced.extend(sentence)    
    return reduced


def resolve_named_entities(wordlist):
    repaired = []
    
    words = {}
    for row in wordlist:
        sentnr,wordnr,word,lemma,root,upos,postag = row
        if not postag.startswith('SPEC') and not postag.startswith('WW'):
            w = word.lower()
            poscnt = words.get(w,Counter())
            poscnt.update([(postag,lemma)])
            words[w] = poscnt
       
    prevword = ''
    prevpos = ''
    #prevprevpos = ''
    for row in wordlist:
        sentnr,wordnr,word,lemma,root,upos,postag = row
        if postag == 'SPEC(deeleigen)':
            w = word.lower()
            if prevpos == 'name' and prevword.lower() in ['de','der','den','van','ter']:
                postag = 'N(eigen,ev,basis,zijd,stan)'
                #print(prevword,word)
            elif word in ['Piet']:
                postag = 'N(eigen,ev,basis,zijd,stan)'
            elif w in words:
                postag = words[w].most_common(1)[0][0][0]
                lemma = words[w].most_common(1)[0][0][1]
                #if lemma.lower() == lemma1.lower():
                #    pass
                #elif lemma.isupper():
                #    lemma = lemma1.upper()
                #elif lemma[0].isupper():
                #    lemma = lemma1[0].upper() + lemma1[1:]
                #else:
                #    lemma = lemma1
            else:
                if len(word) == 2 and word[1]=='.':
                    postag = 'SPEC(symb)'
                else:
                    postag = 'N(eigen,ev,basis,zijd,stan)'
        repaired.append((sentnr,wordnr,word,lemma,root,upos,postag))
        prevword = word
        prevpos = upos
        #prevprevpos = prevpos
    return repaired





wordlist = read_sonar_words(r'sonar.csv')
wordlist = repair(wordlist)
wordlist = remove_foreign(wordlist)
wordlist = resolve_named_entities(wordlist)

with codecs.open('sonar_modified.csv','w','utf8') as fout:
    for entry in wordlist:
        print(*entry,sep='\t',end='\n',file=fout)