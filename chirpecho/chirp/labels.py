"""BirdNET 2.4 bird labels, including birds outside the starter catalogue."""
from chirpecho.chirp.catalogue import SPECIES

# Non-avian genera in the fixed 2.4 model. Source:
# https://github.com/tphakala/birdnet-go/blob/main/doc/wiki/non-bird-species.md
# Revisit this exclusion list when upgrading the model.
NON_BIRD_GENERA = frozenset("""
Anaxyrus Incilius Eleutherodactylus Acris Dryophytes Pseudacris Gastrophryne
Lithobates Scaphiopus Spea Apis Gryllus Miogryllus Oecanthus Amblycorypha
Atlanticus Conocephalus Microcentrum Neoconocephalus Orchelimum Pterophylla
Scudderia Allonemobius Anaxipha Cyrtoxipha Eunemobius Neonemobius Phyllopalpus
Odocoileus Canis Alouatta Sciurus Tamias Tamiasciurus
""".split())
SOUNDS = frozenset(('Dog', 'Engine', 'Environmental', 'Fireworks', 'Gun',
                   'Human non-vocal', 'Human vocal', 'Human whistle', 'Noise',
                   'Power tools', 'Siren'))


def bird_labels(labels):
    names = {entry['scientific']: entry['name'] for entry in SPECIES}
    accepted = {}
    for index, label in enumerate(labels):
        scientific, separator, common = label.partition('_')
        # Sound labels can contain underscores within the category itself.
        if (not scientific.strip() or not separator or not common or scientific.split()[0] in NON_BIRD_GENERA
                or scientific in SOUNDS or common in SOUNDS
                or scientific.startswith('Human')):
            continue
        accepted[index] = names.get(scientific, label)
    return accepted
