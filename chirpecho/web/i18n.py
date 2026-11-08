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
'Wildlife mode: birds or bats':'Diergroep: vogels of vleermuizen',
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
'Identification model':'Identificatiemodel','Sample rate':'Bemonsteringsfrequentie','Call duration':'Roepduur','Source recording':'Bronopname','Stored at':'Opgeslagen op',
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
'WAV recordings are kept without a time limit. The oldest recordings and spectrograms are cleared when storage runs low. Detection metadata stays in your archive.':'WAV-opnamen worden zonder tijdslimiet bewaard. Bij weinig opslagruimte worden de oudste opnamen en spectrogrammen opgeruimd. Waarnemingsgegevens blijven bewaard.',
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
TEXT.update({'Calendar': 'Kalender',
 'Milestones': 'Mijlpalen',
 'Weekly report': 'Weekverslag',
 'A week of wildlife, from the morning chorus to the night shift.': 'Een week vol dierenleven, van het '
                                                                    'ochtendkoor tot de nachtdienst.',
 'Birds and bats together. Choose a day to explore its timeline.': 'Vogels en vleermuizen samen. Kies een '
                                                                   'dag om de tijdlijn te bekijken.',
 'Previous week': 'Vorige week',
 'Next week': 'Volgende week',
 'This week': 'Deze week',
 'Jump to week': 'Ga naar week',
 'Show week': 'Toon week',
 'Weeks start on Monday': 'Weken beginnen op maandag',
 'Predictions saved': 'Opgeslagen voorspellingen',
 'Species this week': 'Soorten deze week',
 'Across both collections': 'Uit beide collecties',
 'New discoveries': 'Nieuwe ontdekkingen',
 'First records in your retained archive': 'Eerste waarnemingen in je bewaarde archief',
 'Active days': 'Actieve dagen',
 'Busiest day:': 'Drukste dag:',
 'Choose a day': 'Kies een dag',
 'New this week': 'Nieuw deze week',
 'Most heard this week': 'Meest gehoord deze week',
 'No first-time species recorded this week.': 'Deze week zijn geen nieuwe soorten waargenomen.',
 'No predictions saved this week. Browse another week or return after recording activity.': 'Deze week zijn '
                                                                                            'geen '
                                                                                            'voorspellingen '
                                                                                            'opgeslagen. '
                                                                                            'Bekijk een '
                                                                                            'andere week of '
                                                                                            'kom terug na '
                                                                                            'nieuwe opnamen.',
 'Day and night timeline': 'Dag- en nachttijdlijn',
 'Predictions by local hour. Repeated hours during the autumn clock change are combined.': 'Voorspellingen '
                                                                                           'per lokaal uur. '
                                                                                           'Dubbele uren bij '
                                                                                           'de overgang naar '
                                                                                           'wintertijd '
                                                                                           'worden '
                                                                                           'samengevoegd.',
 'View hourly counts as a table': 'Bekijk de aantallen per uur in een tabel',
 'Hour': 'Uur',
 'Recent encounters': 'Recente waarnemingen',
 'Up to 30 recent predictions for this day.': 'Maximaal 30 recente voorspellingen voor deze dag.',
 'No encounters recorded on this day.': 'Geen waarnemingen opgeslagen op deze dag.',
 'Reports use retained automatic predictions, not confirmed sightings or individual animal counts. Deleted observations are excluded. A quiet day may also mean the recorder was offline.': 'Verslagen '
                                                                                                                                                                                            'gebruiken '
                                                                                                                                                                                            'bewaarde '
                                                                                                                                                                                            'automatische '
                                                                                                                                                                                            'voorspellingen, '
                                                                                                                                                                                            'geen '
                                                                                                                                                                                            'bevestigde '
                                                                                                                                                                                            'waarnemingen '
                                                                                                                                                                                            'of '
                                                                                                                                                                                            'aantallen '
                                                                                                                                                                                            'dieren. '
                                                                                                                                                                                            'Verwijderde '
                                                                                                                                                                                            'waarnemingen '
                                                                                                                                                                                            'tellen '
                                                                                                                                                                                            'niet '
                                                                                                                                                                                            'mee. '
                                                                                                                                                                                            'Op '
                                                                                                                                                                                            'een '
                                                                                                                                                                                            'stille '
                                                                                                                                                                                            'dag '
                                                                                                                                                                                            'kan '
                                                                                                                                                                                            'de '
                                                                                                                                                                                            'recorder '
                                                                                                                                                                                            'ook '
                                                                                                                                                                                            'uit '
                                                                                                                                                                                            'hebben '
                                                                                                                                                                                            'gestaan.',
 'Your growing collection': 'Je groeiende collectie',
 'Little signals. Memorable firsts. A collection that grows with you.': 'Kleine signalen. Bijzondere '
                                                                        'primeurs. Een collectie die met je '
                                                                        'meegroeit.',
 'Explore the calendar →': 'Bekijk de kalender →',
 'Collection achievements': 'Collectieprestaties',
 'unlocked': 'ontgrendeld',
 'Unlocked': 'Ontgrendeld',
 'In progress': 'In uitvoering',
 'Birds and bats share the adventure. Every retained prediction counts.': 'Vogels en vleermuizen delen het '
                                                                          'avontuur. Elke bewaarde '
                                                                          'voorspelling telt.',
 'Collection progress': 'Collectievoortgang',
 'Species collected': 'Verzamelde soorten',
 'Birds and bats combined': 'Vogels en vleermuizen samen',
 'Days with retained predictions': 'Dagen met bewaarde voorspellingen',
 'Longest streak': 'Langste reeks',
 'days': 'dagen',
 'Consecutive days with activity': 'Opeenvolgende dagen met activiteit',
 'Achievements unlocked': 'Ontgrendelde prestaties',
 'More discoveries ahead': 'Er valt nog meer te ontdekken',
 'First signal': 'Eerste signaal',
 'Save your first wildlife prediction.': 'Sla je eerste diervoorspelling op.',
 'Bird beginnings': 'Eerste vogel',
 'Record your first bird species.': 'Leg je eerste vogelsoort vast.',
 'Night visitor': 'Nachtbezoeker',
 'Record your first bat species.': 'Leg je eerste vleermuissoort vast.',
 'Growing collection': 'Groeiende collectie',
 'Record 10 different species across both collections.': 'Leg 10 verschillende soorten vast uit beide '
                                                         'collecties.',
 'Field guide explorer': 'Veldgidsverkenner',
 'Record 25 species from the bird and bat catalogues.': 'Leg 25 soorten uit de vogel- en vleermuiscatalogus '
                                                        'vast.',
 'Busy garden': 'Drukke tuin',
 'Record 10 different species on one local calendar day.': 'Leg 10 verschillende soorten vast op één lokale '
                                                           'kalenderdag.',
 'Day and night': 'Dag en nacht',
 'Record birds and bats on the same local calendar day.': 'Leg vogels en vleermuizen vast op dezelfde lokale '
                                                          'kalenderdag.',
 'A week of listening': 'Een week luisteren',
 'Record activity on 7 consecutive local calendar days.': 'Leg activiteit vast op 7 opeenvolgende lokale '
                                                          'kalenderdagen.',
 'A month of discovery': 'Een maand ontdekken',
 'Record activity on 30 different local calendar days.': 'Leg activiteit vast op 30 verschillende lokale '
                                                         'kalenderdagen.',
 'One thousand signals': 'Duizend signalen',
 'Save 1,000 wildlife predictions.': 'Sla 1.000 diervoorspellingen op.',
 'Milestones are calculated from your retained archive and update as predictions arrive. Deleting observations can change progress. They celebrate automatic predictions, not verified species records. Dates use': 'Mijlpalen '
                                                                                                                                                                                                                    'worden '
                                                                                                                                                                                                                    'berekend '
                                                                                                                                                                                                                    'uit '
                                                                                                                                                                                                                    'je '
                                                                                                                                                                                                                    'bewaarde '
                                                                                                                                                                                                                    'archief '
                                                                                                                                                                                                                    'en '
                                                                                                                                                                                                                    'bijgewerkt '
                                                                                                                                                                                                                    'bij '
                                                                                                                                                                                                                    'nieuwe '
                                                                                                                                                                                                                    'voorspellingen. '
                                                                                                                                                                                                                    'Het '
                                                                                                                                                                                                                    'verwijderen '
                                                                                                                                                                                                                    'van '
                                                                                                                                                                                                                    'waarnemingen '
                                                                                                                                                                                                                    'kan '
                                                                                                                                                                                                                    'de '
                                                                                                                                                                                                                    'voortgang '
                                                                                                                                                                                                                    'veranderen. '
                                                                                                                                                                                                                    'Ze '
                                                                                                                                                                                                                    'vieren '
                                                                                                                                                                                                                    'automatische '
                                                                                                                                                                                                                    'voorspellingen, '
                                                                                                                                                                                                                    'geen '
                                                                                                                                                                                                                    'bevestigde '
                                                                                                                                                                                                                    'soortwaarnemingen. '
                                                                                                                                                                                                                    'Datums '
                                                                                                                                                                                                                    'gebruiken',
 'Not in catalogue': 'Niet in de catalogus',
 'Bird': 'Vogel',
 'Bat': 'Vleermuis'})
TEXT.update({'Collect familiar faces. Complete a set. Discover your next favourite.': 'Verzamel bekende gezichten. Maak '
                                                                          'een set compleet. Ontdek je '
                                                                          'volgende favoriet.',
 'A little closer with every discovery': 'Met elke ontdekking een stapje dichterbij',
 'Bird collecting sets': 'Vogelverzamelingen',
 'Listening adventures': 'Luisteravonturen',
 'A few feathered friends that belong together. Open a checklist to see who is still missing.': 'Gevleugelde '
                                                                                                'vrienden '
                                                                                                'die bij '
                                                                                                'elkaar '
                                                                                                'horen. Open '
                                                                                                'een lijstje '
                                                                                                'en zie '
                                                                                                'welke '
                                                                                                'soorten je '
                                                                                                'nog mist.',
 '✓ Unlocked': '✓ Behaald',
 'Completed': 'Compleet',
 'See the species': 'Bekijk de soorten',
 'Not recorded yet': 'Nog niet waargenomen',
 'Collecting sets are playful themes from the catalogue. Each species counts once, even if it has been recorded many times. Milestones use retained automatic predictions; deleting observations can change progress.': 'De '
                                                                                                                                                                                                                        'verzamelingen '
                                                                                                                                                                                                                        'zijn '
                                                                                                                                                                                                                        'speelse '
                                                                                                                                                                                                                        'thema’s '
                                                                                                                                                                                                                        'uit '
                                                                                                                                                                                                                        'de '
                                                                                                                                                                                                                        'catalogus. '
                                                                                                                                                                                                                        'Elke '
                                                                                                                                                                                                                        'soort '
                                                                                                                                                                                                                        'telt '
                                                                                                                                                                                                                        'één '
                                                                                                                                                                                                                        'keer, '
                                                                                                                                                                                                                        'ook '
                                                                                                                                                                                                                        'als '
                                                                                                                                                                                                                        'je '
                                                                                                                                                                                                                        'die '
                                                                                                                                                                                                                        'vaak '
                                                                                                                                                                                                                        'hebt '
                                                                                                                                                                                                                        'gehoord. '
                                                                                                                                                                                                                        'Mijlpalen '
                                                                                                                                                                                                                        'gebruiken '
                                                                                                                                                                                                                        'bewaarde '
                                                                                                                                                                                                                        'automatische '
                                                                                                                                                                                                                        'voorspellingen; '
                                                                                                                                                                                                                        'verwijderde '
                                                                                                                                                                                                                        'waarnemingen '
                                                                                                                                                                                                                        'kunnen '
                                                                                                                                                                                                                        'de '
                                                                                                                                                                                                                        'voortgang '
                                                                                                                                                                                                                        'veranderen.',
 'The tit club': 'De mezenclub',
 'Collect all five tits in this set, including the long-tailed tit.': 'Verzamel alle vijf mezen uit deze '
                                                                      'set, inclusief de staartmees.',
 'Goose parade': 'Ganzenparade',
 'Collect the greylag, Canada and greater white-fronted goose.': 'Verzamel de grauwe gans, Canadese gans en '
                                                                 'kolgans.',
 'Owl patrol': 'Uilenpatrouille',
 'Collect the tawny, little, long-eared and barn owl.': 'Verzamel de bosuil, steenuil, ransuil en kerkuil.',
 'The crow crew': 'De kraaienbende',
 'Collect the magpie, jackdaw, carrion crow, rook and jay.': 'Verzamel de ekster, kauw, zwarte kraai, roek '
                                                             'en gaai.',
 'Knock knock!': 'Klop, klop!',
 'Collect the great spotted and green woodpecker.': 'Verzamel de grote bonte specht en groene specht.',
 'Finch party': 'Vinkenfeest',
 'Collect the chaffinch, greenfinch, goldfinch, bullfinch, hawfinch and linnet.': 'Verzamel de vink, '
                                                                                  'groenling, putter, '
                                                                                  'goudvink, appelvink en '
                                                                                  'kneu.',
 'The thrush choir': 'Het lijsterkoor',
 'Collect the blackbird, song thrush, mistle thrush, redwing and fieldfare.': 'Verzamel de merel, '
                                                                              'zanglijster, grote lijster, '
                                                                              'koperwiek en kramsvogel.',
 'Lords of the sky': 'Heersers van de lucht',
 'Collect all six daytime birds of prey in this set.': 'Verzamel alle zes roofvogels uit deze set.',
 'Pigeon post': 'Duivenpost',
 'Collect the wood pigeon, rock pigeon, stock dove and collared dove.': 'Verzamel de houtduif, stadsduif, '
                                                                        'holenduif en Turkse tortel.',
 'Sparrow pals': 'Mussenmaatjes',
 'Collect the house sparrow and tree sparrow.': 'Verzamel de huismus en ringmus.',
 'By the water': 'Aan de waterkant',
 'Collect the mallard, heron, moorhen, coot, swan, stork and kingfisher.': 'Verzamel de wilde eend, blauwe '
                                                                           'reiger, waterhoen, meerkoet, '
                                                                           'knobbelzwaan, ooievaar en '
                                                                           'ijsvogel.',
 'Sky acrobats': 'Luchtacrobaten',
 'Collect the swift, barn swallow, house martin and common tern.': 'Verzamel de gierzwaluw, boerenzwaluw, '
                                                                   'huiszwaluw en visdief.',
 'A whole chorus': 'Een heel koor',
 'Record 10 different bird species.': 'Leg 10 verschillende vogelsoorten vast.',
 'The night club': 'De nachtclub',
 'Record 5 different bat species.': 'Leg 5 verschillende vleermuissoorten vast.',
 'An observatory of your own': 'Je eigen observatorium',
 'Save 10,000 wildlife predictions.': 'Sla 10.000 diervoorspellingen op.',
 'The complete bird atlas': 'De complete vogelatlas',
 'Record every bird in the starter catalogue.': 'Leg elke vogel uit de startcatalogus vast.',
 'Choose a day. See what you heard.': 'Kies een dag. Bekijk wat je hebt gehoord.',
 "This week's listening": 'Deze luisterweek',
 'Choose another week': 'Kies een andere week',
 'Choose a date': 'Kies een datum',
 'predictions': 'voorspellingen',
 'Selected day': 'Gekozen dag',
 'From the morning chorus to the night shift.': 'Van het ochtendkoor tot de nachtdienst.',
 'Activity on this day': 'Activiteit op deze dag',
 'Hourly bird and bat activity; exact counts in the table below': 'Vogel- en vleermuisactiviteit per uur; '
                                                                  'exacte aantallen in de tabel hieronder',
 'View hourly counts': 'Bekijk aantallen per uur',
 'Repeated hours during the autumn clock change are combined.': 'Dubbele uren bij de overgang naar '
                                                                'wintertijd worden samengevoegd.',
 'Encounters on this day': 'Waarnemingen op deze dag',
 'Latest': 'Laatste',
 'shown': 'getoond',
 'A quiet page in your diary': 'Een stille bladzijde in je dagboek',
 'No encounters recorded on this day. Choose another day above.': 'Op deze dag zijn geen waarnemingen '
                                                                  'opgeslagen. Kies hierboven een andere '
                                                                  'dag.',
 'new discoveries': 'nieuwe ontdekkingen',
 "Open this week's highlights": 'Open de hoogtepunten van deze week',
 'No predictions saved this week.': 'Deze week zijn geen voorspellingen opgeslagen.',
 'Reports use retained automatic predictions, not individual animal counts. A quiet day may also mean the recorder was offline. Dates use': 'Verslagen '
                                                                                                                                            'gebruiken '
                                                                                                                                            'bewaarde '
                                                                                                                                            'automatische '
                                                                                                                                            'voorspellingen, '
                                                                                                                                            'geen '
                                                                                                                                            'aantallen '
                                                                                                                                            'dieren. '
                                                                                                                                            'Op '
                                                                                                                                            'een '
                                                                                                                                            'stille '
                                                                                                                                            'dag '
                                                                                                                                            'kan '
                                                                                                                                            'de '
                                                                                                                                            'recorder '
                                                                                                                                            'ook '
                                                                                                                                            'uit '
                                                                                                                                            'hebben '
                                                                                                                                            'gestaan. '
                                                                                                                                            'Datums '
                                                                                                                                            'gebruiken',
 'Not in catalogue — needs to be added': 'Niet in de catalogus — moet nog worden toegevoegd',
 'View detections for': 'Bekijk waarnemingen van'})
TEXT.update({'Birds and bats · Your listening diary': 'Vogels en vleermuizen · Je luisterdagboek',
 'Birds and bats · Observatory status': 'Vogels en vleermuizen · Status van het observatorium',
 'Birds and bats · Your growing collection': 'Vogels en vleermuizen · Je groeiende collectie',
 'Bat collecting sets': 'Vleermuisverzamelingen',
 'Bird listening adventures': 'Luisteravonturen met vogels',
 'Bat listening adventures': 'Luisteravonturen met vleermuizen',
 'Meet the night shift. Open a checklist to see which bats are still missing.': 'Maak kennis met de '
                                                                                'nachtdienst. Open een '
                                                                                'lijstje en zie welke '
                                                                                'vleermuizen je nog mist.',
 'The pipistrelle trio': 'Het dwergvleermuistrio',
 'Collect the common, soprano and Nathusius’ pipistrelle.': 'Verzamel de gewone, kleine en ruige '
                                                            'dwergvleermuis.',
 'Above the treetops': 'Boven de boomtoppen',
 'Collect the noctule, Leisler’s bat and serotine.': 'Verzamel de rosse vleermuis, bosvleermuis en '
                                                     'laatvlieger.',
 'The Myotis club': 'De Myotisclub',
 'Collect all six supported mouse-eared bats in this set.': 'Verzamel alle zes door het model ondersteunde '
                                                            'Myotis-soorten uit deze set.',
 'All ears': 'Eén en al oor',
 'Collect the brown and grey long-eared bat.': 'Verzamel de gewone en grijze grootoorvleermuis.',
 'Lucky horseshoes': 'Gelukshoefijzers',
 'Collect the greater and lesser horseshoe bat.': 'Verzamel de grote en kleine hoefijzerneus.',
 'Save your first bird prediction.': 'Sla je eerste vogelvoorspelling op.',
 'Save your first bat prediction.': 'Sla je eerste vleermuisvoorspelling op.',
 'Record 25 birds from the catalogue.': 'Leg 25 vogelsoorten uit de catalogus vast.',
 'Record 10 supported bats from the catalogue.': 'Leg 10 door het model ondersteunde vleermuissoorten uit de '
                                                 'catalogus vast.',
 'A busy night shift': 'Een drukke nachtdienst',
 'Record 10 different bird species on one local calendar day.': 'Leg 10 verschillende vogelsoorten vast op '
                                                                'één lokale kalenderdag.',
 'Record 3 different bat species on one local calendar day.': 'Leg 3 verschillende vleermuissoorten vast op '
                                                              'één lokale kalenderdag.',
 'Save 1,000 bird predictions.': 'Sla 1.000 vogelvoorspellingen op.',
 'Save 1,000 bat predictions.': 'Sla 1.000 vleermuisvoorspellingen op.',
 'Save 10,000 bird predictions.': 'Sla 10.000 vogelvoorspellingen op.',
 'Save 10,000 bat predictions.': 'Sla 10.000 vleermuisvoorspellingen op.',
 'Batlas explorer': 'Batlasverkenner',
 'Record all 17 bat species supported by the bundled classifier.': 'Leg alle 17 vleermuissoorten vast die '
                                                                   'het meegeleverde model kan herkennen.'})
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
