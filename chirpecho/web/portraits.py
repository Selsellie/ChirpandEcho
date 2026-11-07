"""Local, stylised field-guide portraits; no external image requests."""
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS, LABELS, normalize_label


def profile(label, bird=False):
    entries = BIRDS if bird else BATS
    key = normalize_label(label)
    entry = next((item for item in entries if key in (normalize_label(item['name']), normalize_label(item['scientific']), normalize_label(item['scientific'] + '_' + item['name']))), None)
    if not entry and not bird:
        entry = next((item for item in entries if item['number'] == LABELS.get(key)), None)
    result = dict(entry) if entry else dict(name=label, scientific='', number=None, group='Bird' if bird else 'Bat', note='This prediction is outside the starter field guide. Explore its spectrogram and review the identification.', habitat='Not available in the starter guide.')
    result['artwork'] = 'Stylised species portrait'
    result['portrait'] = ('bird' if bird else 'bat') + '-%03d' % result['number'] if result['number'] else None
    return result
