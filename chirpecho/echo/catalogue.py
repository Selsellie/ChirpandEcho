"""Curated Western European field guide, not an exhaustive regional checklist.

Short original summaries; each record links to its conservation source.
Model support reflects the bundled BatDetect2 Net2DFast_UK_same model.
"""
import re

BCT = 'https://www.bats.org.uk/about-bats/what-are-bats/uk-bats/'
PNA = 'https://plan-actions-chiropteres.fr/les-chauves-souris/les-especes/'
# Common name, scientific name, group, habitat, field note, source slug.
_ROWS = [
    ('Common pipistrelle', 'Pipistrellus pipistrellus', 'Pipistrelles', 'Gardens, woodland edges and towns', 'A tiny bat often encountered around buildings. Its calls overlap with those of other pipistrelles.', 'common-pipistrelle'),
    ('Soprano pipistrelle', 'Pipistrellus pygmaeus', 'Pipistrelles', 'Wetlands, rivers and woodland', 'A small pipistrelle associated with water. Its calls are generally higher pitched than those of the common pipistrelle.', 'soprano-pipistrelle'),
    ("Nathusius’ pipistrelle", 'Pipistrellus nathusii', 'Pipistrelles', 'Lakes, wetlands and woodland edges', 'A migratory pipistrelle. Water-rich landscapes are important feeding areas.', 'nathusius-pipistrelle'),
    ('Noctule', 'Nyctalus noctula', 'Open-air hunters', 'Open skies, parks and mature trees', 'Long, narrow wings support fast flight above the treetops. Tree holes provide important roosts.', 'noctule'),
    ("Leisler’s bat", 'Nyctalus leisleri', 'Open-air hunters', 'Woodland, parkland and open skies', 'A smaller relative of the noctule, with a fast flight and a strong association with tree roosts.', 'leislers-bat'),
    ('Serotine', 'Eptesicus serotinus', 'Open-air hunters', 'Pasture, woodland edges and settlements', 'A large bat that often roosts in buildings and feeds over pasture and along woodland edges.', 'serotine'),
    ("Daubenton’s bat", 'Myotis daubentonii', 'Mouse-eared bats', 'Still water, rivers and canals', 'Often hunts low over smooth water, taking insects from the surface with its feet or tail membrane.', 'daubentons-bat'),
    ("Natterer’s bat", 'Myotis nattereri', 'Mouse-eared bats', 'Woodland, hedgerows and pasture', 'An agile hunter that can pick prey from vegetation. A fringe of stiff hairs lines its tail membrane.', 'natterers-bat'),
    ('Whiskered bat', 'Myotis mystacinus', 'Mouse-eared bats', 'Woodland edges, gardens and hedgerows', 'A small bat closely resembling Brandt’s bat. Sound alone may not separate these species reliably.', 'whiskered-bat'),
    ("Brandt’s bat", 'Myotis brandtii', 'Mouse-eared bats', 'Woodland and landscapes near water', 'Very similar to the whiskered bat. A predicted label needs careful review rather than visual certainty.', 'brandts-bat-2'),
    ('Alcathoe bat', 'Myotis alcathoe', 'Mouse-eared bats', 'Mature deciduous woodland near water', 'A tiny woodland bat recognised as a separate species in 2001. It resembles other small Myotis bats.', 'alcathoe-bat'),
    ("Bechstein’s bat", 'Myotis bechsteinii', 'Mouse-eared bats', 'Mature deciduous woodland', 'Large ears help this woodland specialist listen for prey. Its quiet calls make acoustic detection difficult.', 'bechsteins'),
    ('Brown long-eared bat', 'Plecotus auritus', 'Long-eared bats', 'Woodland, gardens and parkland', 'Huge ears and quiet calls suit slow flight among foliage, where it can pick insects from leaves and bark.', 'brown-long-eared-bat'),
    ('Grey long-eared bat', 'Plecotus austriacus', 'Long-eared bats', 'Grasslands and rural landscapes', 'A long-eared species that can be confused with the brown long-eared bat. Acoustic labels need particular caution.', PNA + 'oreillard-gris/'),
    ('Barbastelle', 'Barbastella barbastellus', 'Woodland specialists', 'Woodland, wet meadows and river corridors', 'Broad ears meet across its head. Small moths form an important part of its diet.', 'barbastelle'),
    ('Greater horseshoe bat', 'Rhinolophus ferrumequinum', 'Horseshoe bats', 'Pasture, hedgerows and woodland edges', 'A horseshoe-shaped noseleaf directs its calls. Buildings and underground sites provide roosts.', 'greater-horseshoe'),
    ('Lesser horseshoe bat', 'Rhinolophus hipposideros', 'Horseshoe bats', 'Sheltered woodland edges and hedgerows', 'A small horseshoe bat that wraps its wings around its body at rest. Its high calls can be difficult to capture.', 'lesser-horseshoe'),
    ('Greater mouse-eared bat', 'Myotis myotis', 'Mouse-eared bats', 'Open woodland and grassland', 'A large Myotis bat that hunts prey close to the ground. Included as a mainland European guide species.', 'greater-mouse-eared-bat'),
    ('Pond bat', 'Myotis dasycneme', 'Mouse-eared bats', 'Large lakes, rivers and canals', 'A water hunter with large feet used to scoop prey from the surface. Particularly relevant to Dutch waterways.', 'https://www.zodion.nl/zoogdiersoorten/meervleermuis'),
    ('Parti-coloured bat', 'Vespertilio murinus', 'Open-air hunters', 'Open landscapes and buildings', 'Its dark back has distinctive silver-tipped hairs. It is a very rare species in the Netherlands.', 'https://www.zodion.nl/zoogdiersoorten/tweekleurige-vleermuis'),
    ("Geoffroy’s bat", 'Myotis emarginatus', 'Mouse-eared bats', 'Woodland, orchards and agricultural mosaics', 'A notch in the outer ear and woolly fur are useful field features. Summer colonies may occupy quiet roof spaces.', PNA + 'murin-a-oreilles-echancrees/'),
    ("Kuhl’s pipistrelle", 'Pipistrellus kuhlii', 'Pipistrelles', 'Towns, open spaces and wetland edges', 'A pale wing margin is a characteristic feature. In France its range has expanded northwards.', PNA + 'pipistrelle-de-kuhl/'),
    ("Savi’s pipistrelle", 'Hypsugo savii', 'Pipistrelles', 'Cliffs, rocky landscapes and settlements', 'A southern species found in parts of France, roosting in rock and wall crevices.', PNA + 'vespere-de-savi/'),
    ("Schreibers’ bent-winged bat", 'Miniopterus schreibersii', 'Cave specialists', 'Caves and varied surrounding landscapes', 'Long, narrow wings suit fast flight. Underground roosts are central to its life cycle.', PNA + 'minioptere-de-schreibers/'),
]


def normalize_label(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


SPECIES = tuple(dict(number=index, name=row[0], scientific=row[1], group=row[2],
                     habitat=row[3], note=row[4], source=row[5] if row[5].startswith('https://') else BCT + row[5],
                     supported=index <= 17)
                for index, row in enumerate(_ROWS, 1))
LABELS = {}
for entry in SPECIES:
    for label in (entry['name'], entry['scientific']):
        LABELS[normalize_label(label)] = entry['number']
# The bundled model contains this spelling; retain the accepted genus on cards.
LABELS[normalize_label('Barbastellus barbastellus')] = 15
LABELS[normalize_label('Common noctule')] = 4

# Collection rarity is a game mechanic, not a biological assessment.
from chirpecho.common.rarity import rarity_for
SPECIES = tuple(dict(item, rarity=rarity_for('bat', item['number'])) for item in SPECIES)
