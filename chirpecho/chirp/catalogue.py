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
]
from urllib.parse import quote

SPECIES = tuple(dict(number=i,name=name,scientific=scientific,group='Western European birds',
                     note='BirdNET predicts this species from three-second analysis windows. Review predictions before treating them as confirmed records.',
                     habitat='See the species profile for its habitat and range.',
                     supported=True,source='https://www.gbif.org/species/search?q='+quote(scientific))
                for i,(scientific,name) in enumerate(_ROWS,1))
