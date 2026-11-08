"""Offline English/Dutch presentation translation; scientific data stays intact."""
import html
from html.parser import HTMLParser
import re
from urllib.parse import urlencode, urlsplit
from flask import request
from chirpecho.common.dutch import BIRDS as DUTCH_BIRDS, BATS as DUTCH_BATS
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS

TEXT = {
'Artwork':'Illustraties','The wildlife artwork collection':'De collectie dierenillustraties',
'Browse the full collection. Open an illustration to see it at full size.':'Bekijk de volledige collectie. Open een illustratie om deze op volledig formaat te bekijken.',
'Birds and bats':'Vogels en vleermuizen',
'Signal ↗':'Signaal ↗','Listen':'Luisteren','Encounter actions':'Acties voor waarneming','Delete encounter...':'Waarneming verwijderen...',
'Use the bird/bat switch to choose the log pipeline.':'Kies met de vogel/vleermuis-schakelaar welk logboek je bekijkt.',
'Browse all artwork ↗':'Bekijk alle illustraties ↗',
'Detections':'Waarnemingen','Species':'Soorten','Logs':'Logboeken','Health':'Status',
'Appearance':'Weergave','System':'Systeem','Light':'Licht','Dark':'Donker',
'Local network only':'Alleen lokaal netwerk','Main navigation':'Hoofdnavigatie','Wildlife mode':'Diergroep',
'Language: English or Dutch':'Taal: Engels of Nederlands','Change language':'Taal wijzigen',
'One observatory. Two worlds.':'Eén observatorium. Twee werelden.',
'Birds · The daytime chorus':'Vogels · Het koor overdag','Bats · The night shift':'Vleermuizen · De nachtdienst',
'Birds':'Vogels','Bats':'Vleermuizen','Bird':'Vogel','Bat':'Vleermuis',
'Your bird observatory':'Je vogelobservatorium','Your bat observatory':'Je vleermuisobservatorium',
'Morning watch.':'Ochtendwacht.','Night watch.':'Nachtwacht.',
'A closer look at the calls around you.':'Een kijkje in de geluiden om je heen.',
'Among the treetops':'Tussen de boomtoppen','Out in the quiet':'In de stilte',
'Microphone listening':'Microfoon luistert','Checking microphone':'Microfoon controleren',
'Small songs.':'Kleine liedjes.','Small sounds.':'Kleine geluiden.','A bigger picture.':'Een groter verhaal.',
'BirdNET listens for birds in three-second analysis windows. Predictions become species insights and spectrograms.':'BirdNET luistert naar vogels in analysevensters van drie seconden. Voorspellingen worden soortinformatie en spectrogrammen.',
'Ultrasonic calls become species insights and spectrograms.':'Ultrasone roepen worden soortinformatie en spectrogrammen.',
'Bird activity':'Vogelactiviteit','Activity after dark':'Activiteit na zonsondergang','Last 24 hours':'Afgelopen 24 uur',
'prediction windows':'voorspellingsvensters','in your last 24 hours':'in de afgelopen 24 uur',
'Bird predictions':'Vogelvoorspellingen','Calls collected':'Roepen verzameld','Detection records kept':'Opgeslagen waarnemingen',
'Species identified':'Soorten herkend','Predicted by the classifier':'Voorspeld door het model',
'Average confidence':'Gemiddelde zekerheid','Across retained observations':'Over opgeslagen waarnemingen',
'Spectrogram archive':'Spectrogramarchief','Compact spectra':'Compacte spectra','cleared for space':'opgeruimd voor ruimte',
'The field notes':'De veldnotities','Recent encounters':'Recente ontmoetingen',
'Interactive spectrograms + lasting data':'Interactieve spectrogrammen + blijvende gegevens',
'Find a species…':'Zoek een soort…','Search species':'Soorten zoeken','Minimum confidence':'Minimale zekerheid',
'All confidence levels':'Alle zekerheidsniveaus','confidence and higher':'zekerheid of hoger',
'Apply filters':'Filters toepassen','Species rarity':'Zeldzaamheid van de soort','All rarities':'Alle zeldzaamheden',
'Common':'Gewoon','Uncommon':'Ongewoon','Rare':'Zeldzaam','Epic':'Episch','Legendary':'Legendarisch','Unranked':'Zonder klasse',
'Wild encounter':'Nieuwe ontmoeting','Prediction confidence':'Voorspellingszekerheid',
'Explore species card →':'Bekijk soortkaart →','Illustrative portrait · automatic prediction':'Gestileerde tekening · automatische voorspelling',
'Explore signal':'Signaal bekijken','Explore spectrogram':'Spectrogram bekijken',
'Open on eBird ↗':'Openen op eBird ↗',
'Recording kept for 24 hours after detection.':'De opname wordt 24 uur na de waarneming bewaard.',
'Delete observation...':'Waarneming verwijderen...',
'Are you sure?':'Weet je het zeker?','Delete this observation?':'Deze waarneming verwijderen?',
'This removes':'Dit verwijdert','from the archive. Its spectrogram is deleted too. Any saved WAV is deleted if no other observation uses it.':'uit het archief. Het spectrogram wordt ook verwijderd. De WAV-opname wordt verwijderd als geen andere waarneming deze gebruikt.',
'This cannot be undone.':'Dit kan niet ongedaan worden gemaakt.',
'Yes, delete observation':'Ja, verwijder waarneming','Cancel':'Annuleren',
'Legacy preview · conversion pending':'Oude weergave · omzetting volgt','Detection data safely retained':'Waarnemingsgegevens veilig bewaard',
'No matching encounters':'Geen passende waarnemingen','The chorus is still unfolding':'Het koor moet nog beginnen',
'The night is still unfolding':'De nacht moet nog beginnen',
'Try another species, rarity, or a lower confidence filter.':'Probeer een andere soort, zeldzaamheid of lagere zekerheid.',
'When BirdNET finds a qualifying bird prediction, its species, time, confidence and spectrogram will appear here.':'Wanneer BirdNET een passende vogelvoorspelling opslaat, verschijnen hier de soort, het tijdstip, de zekerheid en het spectrogram.',
'When a call is detected, its species, time, confidence and spectrogram will appear here. Quiet recordings are discarded.':'Bij een gedetecteerde roep verschijnen hier de soort, het tijdstip, de zekerheid en het spectrogram. Stille opnamen worden weggegooid.',
'← Newer':'← Nieuwer','Older →':'Ouder →','Page':'Pagina','of':'van','observations':'waarnemingen','observation':'waarneming',
'Detection ledger · all metadata for this page':'Waarnemingenregister · alle gegevens op deze pagina',
'Recorded':'Waargenomen','Undiscovered':'Nog niet ontdekt','Confidence':'Zekerheid','Call probability':'Roepkans',
'Analysis window':'Analysevenster','Frequency':'Frequentie','Spectrogram':'Spectrogram','Image':'Afbeelding',
'Unavailable':'Niet beschikbaar','unavailable':'niet beschikbaar','cleared':'opgeruimd','call probability':'roepkans',
'3-second analysis window':'Analysevenster van 3 seconden','3 seconds · 0–15 kHz model band':'3 seconden · modelbereik 0–15 kHz',
'Who’s been visiting?':'Wie kwam er op bezoek?','Species overview':'Soortenoverzicht',
'Your species summary will grow with each encounter.':'Je soortenoverzicht groeit bij elke ontmoeting.',
'Last heard:':'Voor het laatst gehoord:','A lighter footprint':'Een kleinere voetafdruk','GB free':'GB vrij',
'disk used':'schijfgebruik','Cleanup starts at':'Opruimen begint bij',
'Keep the story. Make room for the next call.':'Bewaar het verhaal. Maak ruimte voor de volgende roep.',
'The oldest spectrograms are cleared when storage runs low. Species, timestamps, confidence and frequency data stay in your archive. WAVs linked to detections are kept for 24 hours.':'Bij weinig opslagruimte worden de oudste spectrogrammen opgeruimd. Soorten, tijdstippen, zekerheid en frequenties blijven bewaard. WAV-opnamen bij waarnemingen blijven 24 uur bewaard.',
'The Western European bird collection':'De West-Europese vogelcollectie','The Western European collection':'De West-Europese collectie',
'Bird atlas.':'Vogelatlas.','Meet the voices around you.':'Ontmoet de stemmen om je heen.',
'Meet the neighbours of the night.':'Ontmoet de buren van de nacht.',
'Species field guide':'Soortengids','Discover · Record · Explore':'Ontdek · Luister · Verken',
'A little curiosity. A growing collection.':'Een beetje nieuwsgierigheid. Een groeiende collectie.',
'A curated selection of':'Een selectie van','occurring in Western Europe, from the British Isles and Benelux to France and neighbouring mainland regions.':'uit West-Europa, van de Britse eilanden en Benelux tot Frankrijk en de aangrenzende regio’s.',
'This is a starter field guide, not a complete checklist or a list of bats expected at your microphone.':'Dit is een startgids, geen complete soortenlijst of voorspelling van dieren bij je microfoon.',
'SPECIES RECORDED':'SOORTEN WAARGENOMEN','Search name, habitat or group…':'Zoek naam, leefgebied of groep…',
'Collection status':'Collectiestatus','All species':'Alle soorten','Explore':'Verkennen','species shown':'soorten getoond',
'Entry locked':'Nog vergrendeld','Detect this species to reveal its colours and field notes.':'Ontdek deze soort om de kleuren en veldnotities te zien.',
'In your collection':'In je collectie','Still to discover':'Nog te ontdekken','Open field notes':'Veldnotities openen',
'Where it hunts':'Waar hij jaagt','Your first record':'Je eerste waarneming','Last recorded':'Laatste waarneming',
'No record yet':'Nog niet waargenomen','Highest prediction confidence':'Hoogste voorspellingszekerheid',
'Automatic identification':'Automatische herkenning',
'Included in the bundled classifier. Predictions still need review.':'Inbegrepen in het model. Voorspellingen moeten nog gecontroleerd worden.',
'Field guide entry; not identified by the bundled classifier.':'Veldgidssoort; wordt niet door het meegeleverde model herkend.',
'View detections →':'Bekijk waarnemingen →','Species reference ↗':'Soortinformatie ↗',
'No species match this search':'Geen soorten gevonden',
'Try another name, rarity, or collection status. Your collection grows when qualifying predictions are saved.':'Probeer een andere naam, zeldzaamheid of collectiestatus. Je collectie groeit als passende voorspellingen worden opgeslagen.',
'Show all species →':'Toon alle soorten →',
'Collection game tier; not a measure of local rarity':'Spelklasse; geen maat voor plaatselijke zeldzaamheid',
'Western European birds':'West-Europese vogels','Pipistrelles':'Dwergvleermuizen','Open-air hunters':'Jagers in open lucht',
'Mouse-eared bats':'Myotis-vleermuizen','Long-eared bats':'Grootoorvleermuizen','Woodland specialists':'Bosspecialisten',
'Horseshoe bats':'Hoefijzerneuzen','Cave specialists':'Grottenspecialisten',
'Gardens, woodland edges and towns':'Tuinen, bosranden en steden','Wetlands, rivers and woodland':'Moerassen, rivieren en bossen',
'Lakes, wetlands and woodland edges':'Meren, moerassen en bosranden','Open skies, parks and mature trees':'Open lucht, parken en oude bomen',
'Woodland, parkland and open skies':'Bossen, parken en open lucht','Pasture, woodland edges and settlements':'Weilanden, bosranden en bebouwing',
'Still water, rivers and canals':'Stilstaand water, rivieren en kanalen','Woodland, hedgerows and pasture':'Bossen, hagen en weilanden',
'Woodland edges, gardens and hedgerows':'Bosranden, tuinen en hagen','Woodland and landscapes near water':'Bossen en landschappen bij water',
'Mature deciduous woodland near water':'Oud loofbos bij water','Mature deciduous woodland':'Oud loofbos',
'Woodland, gardens and parkland':'Bossen, tuinen en parken','Grasslands and rural landscapes':'Graslanden en landelijke gebieden',
'Woodland, wet meadows and river corridors':'Bossen, natte weilanden en rivierdalen','Pasture, hedgerows and woodland edges':'Weilanden, hagen en bosranden',
'Sheltered woodland edges and hedgerows':'Beschutte bosranden en hagen','Open woodland and grassland':'Open bos en grasland',
'Large lakes, rivers and canals':'Grote meren, rivieren en kanalen','Open landscapes and buildings':'Open landschappen en gebouwen',
'Woodland, orchards and agricultural mosaics':'Bossen, boomgaarden en gevarieerd boerenland','Towns, open spaces and wetland edges':'Steden, open terrein en moerasranden',
'Cliffs, rocky landscapes and settlements':'Kliffen, rotslandschappen en bebouwing','Caves and varied surrounding landscapes':'Grotten en gevarieerde omliggende landschappen',
'Small signals, lasting observations.':'Kleine signalen, blijvende waarnemingen.',
'capture listening':'opname luistert','capture status pending':'opnamestatus wordt opgehaald','Detector':'Detector',
'Refreshes every minute':'Vernieuwt elke minuut','listening':'luistert','ready':'gereed','processing':'bezig',
'Spectrogram detail':'Spectrogramdetails','Legacy spectrogram detail':'Oude spectrogramdetails','Close ✕':'Sluiten ✕',
'Quiet':'Zacht','Strong':'Sterk','← Back to encounters':'← Terug naar waarnemingen',
'prediction confidence':'voorspellingszekerheid','Loading spectrogram…':'Spectrogram laden…',
'Legacy PNG · waiting for verified conversion to a compact spectrogram.':'Oude PNG · wacht op gecontroleerde omzetting naar een compact spectrogram.',
'Log summaries':'Logoverzicht','System health':'Systeemstatus','Your acoustic observatory':'Je akoestische observatorium',
'Follow each sound through the pipeline.':'Volg ieder geluid door de verwerking.',
'Service checks, with a clear view of what is working.':'Servicecontroles die laten zien wat goed werkt.',
'Updated':'Bijgewerkt','Shared logs':'Gedeelde logboeken','Shared health':'Gedeelde status',
'Both pipelines are shown below. Birds and bats keep separate audio queues and archives.':'Beide verwerkingsketens staan hieronder. Vogels en vleermuizen hebben aparte audiowachtrijen en archieven.',
'Active service checks passing':'Actieve servicecontroles geslaagd','Attention needed':'Aandacht nodig','Healthy':'In orde','Check needed':'Controle nodig',
'Shared microphone capture, both classifiers, both archives, and storage checks are shown below. Service health does not confirm wildlife activity.':'Hieronder staan de gedeelde microfoon, beide modellen, beide archieven en de opslag. Een werkende service bewijst geen dierenactiviteit.',
'How these checks work':'Hoe deze controles werken','View log summaries →':'Bekijk logoverzicht →','Last heartbeat:':'Laatste teken van leven:',
'windows':'vensters','window':'venster','calls':'roepen','call':'roep','recorded':'waargenomen',
'Monday':'Maandag','Tuesday':'Dinsdag','Wednesday':'Woensdag','Thursday':'Donderdag','Friday':'Vrijdag','Saturday':'Zaterdag','Sunday':'Zondag',
'January':'januari','February':'februari','March':'maart','April':'april','May':'mei','June':'juni','July':'juli','August':'augustus','September':'september','October':'oktober','November':'november','December':'december',
}
TEXT.update({
'Explore spectrogram for':'Bekijk het spectrogram van','Spectrogram for':'Spectrogram van',
'Cartoon portrait of':'Cartoonportret van','Undiscovered silhouette of':'Nog niet ontdekt silhouet van',
'Detailed detection spectrogram':'Gedetailleerd spectrogram van de waarneming',
'Open legacy spectrogram for':'Bekijk oud spectrogram van','Legacy spectrogram for':'Oud spectrogram van',
'“Recorded” means at least one retained classifier prediction, not a confirmed identification.':'“Waargenomen” betekent minstens één opgeslagen modelvoorspelling, geen bevestigde herkenning.',
'Bird counts are qualifying three-second windows, not individual calls or birds. Adjacent windows may overlap.':'Vogeltellingen zijn passende vensters van drie seconden, geen afzonderlijke roepen of vogels. Aangrenzende vensters kunnen overlappen.',
'Call counts are detections, not individual bats.':'Roeptellingen zijn detecties, geen afzonderlijke vleermuizen.',
'Similar species can be confused; undiscovered does not mean absent.':'Vergelijkbare soorten kunnen worden verward; nog niet ontdekt betekent niet afwezig.',
'Cartoon portraits are stylised illustrations, not identification drawings; each guide species has its own artwork.':'Cartoonportretten zijn gestileerde illustraties, geen determinatietekeningen; elke gidssoort heeft een eigen tekening.',
'Rarity tiers are a collection game mechanic, not local occurrence or conservation ratings.':'Zeldzaamheidsklassen zijn een spelelement, geen maat voor plaatselijk voorkomen of beschermingsstatus.',
'Plumage represents an adult; sex, age and season can change its appearance.':'Het verenkleed stelt een volwassen dier voor; geslacht, leeftijd en seizoen kunnen het uiterlijk veranderen.',
'Starter list:':'Startlijst:','BirdNET 2.4 predicts from audio alone; inclusion here is not evidence that a species is present at your location.':'BirdNET 2.4 voorspelt op basis van geluid; opname in de gids bewijst niet dat de soort hier voorkomt.',
'BirdNET model source':'Bron van het BirdNET-model','Field notes adapted from the':'Veldnotities gebaseerd op informatie van',
'Each card links to its species source. Reviewed November 2026.':'Elke kaart verwijst naar soortinformatie. Nagekeken in november 2026.',
'They remain in':'Ze blijven zichtbaar bij','and do not unlock a card.':'en ontgrendelen geen kaart.',
'have labels outside this guide or unresolved species groups.':'hebben labels buiten deze gids of betreffen niet-onderscheiden soortgroepen.',
'The recorder must report within 30 seconds and the detector within 180 seconds. Storage needs the configured free-space reserve and usage below the cleanup threshold. This page refreshes every minute.':'De recorder moet binnen 30 seconden en de detector binnen 180 seconden een teken van leven geven. De opslag moet voldoende vrije ruimte hebben en onder de opruimgrens blijven. Deze pagina vernieuwt elke minuut.',
'See the species profile for its habitat and range.':'Bekijk het soortprofiel voor leefgebied en verspreiding.',
'Not available in the starter guide.':'Niet beschikbaar in deze startgids.',
'This prediction is outside the starter field guide. Explore its spectrogram and review the identification.':'Deze voorspelling valt buiten de startgids. Bekijk het spectrogram en controleer de herkenning.',
})
TEXT.update({
'birds':'vogels','bats':'vleermuizen','bird':'vogel','bat':'vleermuis',
'Pipeline summary':'Overzicht van de verwerking','Recordings saved':'Opgeslagen opnamen',
'Files classified':'Geclassificeerde bestanden','Raw predictions':'Ruwe voorspellingen',
'Qualifying predictions':'Passende voorspellingen','Available log window':'Beschikbare logperiode',
'Coverage':'Logbereik','recent events':'recente gebeurtenissen',
'Bounded tails of the current logs, up to 512 KiB per service; these are not lifetime totals.':'De laatste regels uit de huidige logs, maximaal 512 KiB per service; dit zijn geen totalen sinds de start.',
'warning/error entries.':'waarschuwingen of fouten.','Amsterdam time':'Amsterdamse tijd',
'No events available in this log window yet.':'Nog geen gebeurtenissen in deze logperiode.',
'Sound recorded; waiting for classification.':'Geluid opgenomen; wacht op classificatie.',
'Sound recorded, no qualifying bird predictions.':'Geluid opgenomen, geen passende vogelvoorspellingen.',
'Sound recorded, no qualifying bat calls.':'Geluid opgenomen, geen passende vleermuisroepen.',
'qualifying bird predictions found.':'passende vogelvoorspellingen gevonden.',
'qualifying bat calls found.':'passende vleermuisroepen gevonden.',
'Microphone capture':'Microfoonopname','Bat classifier':'Vleermuismodel','Storage reserve':'Opslagreserve',
'Audio chunks are arriving. This does not confirm bat activity.':'Audioblokken komen binnen. Dit bewijst geen vleermuisactiviteit.',
'No recent recorder heartbeat. Check the recorder and microphone.':'Geen recent teken van leven van de recorder. Controleer de recorder en microfoon.',
'No recent detector heartbeat. Check the detector logs.':'Geen recent teken van leven van de detector. Controleer de detectorlogs.',
'Zero detections can be normal.':'Geen detecties kan normaal zijn.','Detector is':'Detector is',
'Separate bird records are stored.':'Vogelgegevens worden apart opgeslagen.',
'Bird records are stored separately from Echo records.':'Vogelgegevens worden apart van vleermuisgegevens opgeslagen.',
'Audible audio from the shared microphone. State:':'Hoorbare audio van de gedeelde microfoon. Toestand:',
'BirdNET 2.4 local inference. State:':'BirdNET 2.4 verwerkt lokaal. Toestand:',
'Local BirdNET 2.4 inference. State:':'Lokale verwerking met BirdNET 2.4. Toestand:',
'BirdNET 2.4 local inference. State':'BirdNET 2.4 verwerkt lokaal. Toestand',
'State:':'Toestand:','Waiting for activity':'Wacht op activiteit','Starting':'Opstarten',
'Audio capture':'Audio-opname','BirdNET classifier':'BirdNET-model','Bird database':'Vogeldatabase',
'Shared':'Gedeeld','used.':'gebruikt.','Database':'Database','unknown':'onbekend',
})
for english, dutch in zip(BIRDS+BATS,DUTCH_BIRDS+DUTCH_BATS,strict=True):
    TEXT[english['name']]=dutch[0]
    TEXT[english['note']]=dutch[1]
PATTERN=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(key) for key in sorted(TEXT,key=len,reverse=True))+r')(?!\w)')


def language():
    value=request.args.get('lang', request.cookies.get('chirpecho-language','en'))
    return value if value in ('en','nl') else 'en'


def translate(value):
    value=re.sub(r'A ([\d.]+)-second pause keeps listening balanced\.',r'Een pauze van \1 seconden houdt het luisteren in balans.',value)
    return PATTERN.sub(lambda match:TEXT[match[0]],value)


def language_return_url():
    args=[(key,value) for key,value in request.args.items(multi=True) if key!='lang']
    return request.path+('?' + urlencode(args) if args else '')


class DutchHTML(HTMLParser):
    HUMAN_ATTRIBUTES={'alt','title','placeholder','aria-label','data-species'}
    RAW={'script','style','pre','code','kbd','samp'}
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts=[];self.raw=[]
    def start(self,tag,attrs,ending):
        values=[]
        for key,value in attrs:
            if value is not None and key in self.HUMAN_ATTRIBUTES:value=translate(value)
            values.append(key if value is None else key+'="'+html.escape(value,quote=True)+'"')
        self.parts.append('<'+tag+(' '+' '.join(values) if values else '')+ending)
    def handle_starttag(self,tag,attrs):
        self.start(tag,attrs,'>')
        if tag in self.RAW:self.raw.append(tag)
    def handle_startendtag(self,tag,attrs):self.start(tag,attrs,'/>')
    def handle_endtag(self,tag):
        self.parts.append('</'+tag+'>')
        if self.raw and self.raw[-1]==tag:self.raw.pop()
    def handle_data(self,value):self.parts.append(value if self.raw else html.escape(translate(value),quote=False))
    def handle_entityref(self,name):self.parts.append('&'+name+';')
    def handle_charref(self,name):self.parts.append('&#'+name+';')
    def handle_comment(self,data):self.parts.append('<!--'+data+'-->')
    def handle_decl(self,decl):self.parts.append('<!'+decl+'>')


def localize_html(value):
    parser=DutchHTML();parser.feed(value);parser.close()
    return ''.join(parser.parts)


def safe_return_url(value):
    try:
        parsed=urlsplit(value)
    except ValueError:
        return '/'
    return value if value.startswith('/') and not value.startswith('//') and '\\' not in value and not parsed.netloc and not parsed.scheme and not any(ord(c)<32 for c in value) else '/'
