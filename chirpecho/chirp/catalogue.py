"""A deliberately limited Western European bird list for the garden monitor.

Names are matched to the bundled BirdNET label file at startup. This is a
starter selection, not a complete checklist or a geographic occurrence model.
"""
_ROWS = [
('Turdus merula','Eurasian Blackbird'),('Erithacus rubecula','European Robin'),
('Parus major','Great Tit'),('Cyanistes caeruleus','Eurasian Blue Tit'),
('Passer domesticus','House Sparrow'),('Passer montanus','Eurasian Tree Sparrow'),
('Fringilla coelebs','Common Chaffinch'),('Chloris chloris','European Greenfinch'),
('Carduelis carduelis','European Goldfinch'),('Prunella modularis','Dunnock'),
('Troglodytes troglodytes','Eurasian Wren'),('Sturnus vulgaris','European Starling'),
('Pica pica','Eurasian Magpie'),('Corvus monedula','Eurasian Jackdaw'),
('Corvus corone','Carrion Crow'),('Corvus frugilegus','Rook'),
('Garrulus glandarius','Eurasian Jay'),('Columba palumbus','Common Wood Pigeon'),
('Columba livia','Rock Pigeon'),('Streptopelia decaocto','Eurasian Collared Dove'),
('Dendrocopos major','Great Spotted Woodpecker'),('Picus viridis','European Green Woodpecker'),
('Sitta europaea','Eurasian Nuthatch'),('Certhia brachydactyla','Short-toed Treecreeper'),
('Aegithalos caudatus','Long-tailed Tit'),('Periparus ater','Coal Tit'),
('Poecile palustris','Marsh Tit'),('Regulus regulus','Goldcrest'),
('Turdus philomelos','Song Thrush'),('Turdus viscivorus','Mistle Thrush'),
('Turdus iliacus','Redwing'),('Turdus pilaris','Fieldfare'),
('Sylvia atricapilla','Eurasian Blackcap'),('Phylloscopus collybita','Common Chiffchaff'),
('Phylloscopus trochilus','Willow Warbler'),('Cuculus canorus','Common Cuckoo'),
('Apus apus','Common Swift'),('Hirundo rustica','Barn Swallow'),
('Delichon urbicum','Common House Martin'),('Motacilla alba','White Wagtail'),
('Alauda arvensis','Eurasian Skylark'),('Buteo buteo','Common Buzzard'),
('Falco tinnunculus','Common Kestrel'),('Strix aluco','Tawny Owl'),
('Athene noctua','Little Owl'),('Asio otus','Long-eared Owl'),
('Tyto alba','Barn Owl'),('Anas platyrhynchos','Mallard'),
('Ardea cinerea','Grey Heron'),('Gallinula chloropus','Common Moorhen'),
('Fulica atra','Eurasian Coot'),('Larus argentatus','European Herring Gull'),
('Chroicocephalus ridibundus','Black-headed Gull'),('Anser anser','Greylag Goose'),
('Branta canadensis','Canada Goose'),('Cygnus olor','Mute Swan'),
('Accipiter nisus', 'Eurasian Sparrowhawk'),
('Pyrrhula pyrrhula', 'Eurasian Bullfinch'),
('Emberiza citrinella', 'Yellowhammer'),
('Coccothraustes coccothraustes', 'Hawfinch'),
('Ciconia ciconia', 'White Stork'),
('Motacilla flava', 'Western Yellow Wagtail'),
('Linaria cannabina', 'Common Linnet'),
('Columba oenas', 'Stock Dove'),
('Haliaeetus albicilla', 'White-tailed Eagle'),
('Alcedo atthis', 'Common Kingfisher'),
('Sterna hirundo', 'Common Tern'),
('Pernis apivorus', 'European Honey-buzzard'),
('Circus aeruginosus', 'Western Marsh Harrier'),
]

# eBird species codes from the Cornell Lab's eBird taxonomy (v2026).
# A few accepted scientific names differ from BirdNET's training labels;
# these codes were matched by scientific-name aliases where needed.
_EBIRD_CODES = {
    'Turdus merula':'eurbla','Erithacus rubecula':'eurrob1',
    'Parus major':'gretit1','Cyanistes caeruleus':'blutit',
    'Passer domesticus':'houspa','Passer montanus':'eutspa',
    'Fringilla coelebs':'comcha','Chloris chloris':'eurgre1',
    'Carduelis carduelis':'eurgol','Prunella modularis':'dunnoc1',
    'Troglodytes troglodytes':'winwre4','Sturnus vulgaris':'eursta',
    'Pica pica':'eurmag1','Corvus monedula':'eurjac',
    'Corvus corone':'carcro1','Corvus frugilegus':'rook1',
    'Garrulus glandarius':'eurjay1','Columba palumbus':'cowpig1',
    'Columba livia':'rocpig','Streptopelia decaocto':'eucdov',
    'Dendrocopos major':'grswoo','Picus viridis':'eugwoo2',
    'Sitta europaea':'eurnut2','Certhia brachydactyla':'shttre1',
    'Aegithalos caudatus':'lottit1','Periparus ater':'coatit2',
    'Poecile palustris':'martit2','Regulus regulus':'goldcr1',
    'Turdus philomelos':'sonthr1','Turdus viscivorus':'misthr1',
    'Turdus iliacus':'redwin','Turdus pilaris':'fieldf',
    'Sylvia atricapilla':'blackc1','Phylloscopus collybita':'comchi1',
    'Phylloscopus trochilus':'wlwwar','Cuculus canorus':'comcuc',
    'Apus apus':'comswi','Hirundo rustica':'barswa',
    'Delichon urbicum':'comhom1','Motacilla alba':'whiwag',
    'Alauda arvensis':'skylar','Buteo buteo':'combuz1',
    'Falco tinnunculus':'eurkes','Strix aluco':'tawowl1',
    'Athene noctua':'litowl1','Asio otus':'loeowl','Tyto alba':'webowl1',
    'Anas platyrhynchos':'mallar3','Ardea cinerea':'graher1',
    'Gallinula chloropus':'commoo3','Fulica atra':'eurcoo',
    'Larus argentatus':'euhgul1','Chroicocephalus ridibundus':'bkhgul',
    'Anser anser':'gragoo','Branta canadensis':'cangoo','Cygnus olor':'mutswa',
}
_EBIRD_CODES.update({'Accipiter nisus': 'eurspa1', 'Pyrrhula pyrrhula': 'eurbul', 'Emberiza citrinella': 'yellow2', 'Coccothraustes coccothraustes': 'hawfin', 'Ciconia ciconia': 'whisto1', 'Motacilla flava': 'eaywag1', 'Linaria cannabina': 'eurlin1', 'Columba oenas': 'stodov1'})
_EBIRD_CODES.update({'Haliaeetus albicilla': 'whteag', 'Alcedo atthis': 'comkin1', 'Sterna hirundo': 'comter', 'Pernis apivorus': 'euhbuz1', 'Circus aeruginosus': 'wemhar1'})
assert len(_EBIRD_CODES) == len(_ROWS)
from urllib.parse import quote
from chirpecho.common.field_art import BIRD_ART

SPECIES = tuple(dict(number=i,name=name,scientific=scientific,group='Western European birds',
                     note=BIRD_ART[i-1][6],
                     habitat='See the species profile for its habitat and range.',
                     supported=True,source='https://www.gbif.org/species/search?q='+quote(scientific),
                     ebird_code=_EBIRD_CODES[scientific],
                     ebird_url='https://ebird.org/species/'+_EBIRD_CODES[scientific]+'?continue')
                for i,(scientific,name) in enumerate(_ROWS,1))

# Collection rarity is a game mechanic, not a biological assessment.
from chirpecho.common.rarity import rarity_for
SPECIES = tuple(dict(item, rarity=rarity_for('bird', item['number'])) for item in SPECIES)
