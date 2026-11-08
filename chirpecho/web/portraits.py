"""Local, stylised field-guide portraits; no external image requests."""
import json
from pathlib import Path
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS, LABELS, normalize_label

_MANIFEST = Path(__file__).parent / 'static/species/artwork-manifest.json'
_VERSIONS = {key: value['sha256'][:12] for key, value in json.loads(_MANIFEST.read_text()).items()}


def profile(label, bird=False):
    entries = BIRDS if bird else BATS
    key = normalize_label(label)
    entry = next((item for item in entries if key in (normalize_label(item['name']), normalize_label(item['scientific']), normalize_label(item['scientific'] + '_' + item['name']))), None)
    if not entry and bird and '_' in label:
        scientific = normalize_label(label.partition('_')[0])
        entry = next((item for item in entries if scientific == normalize_label(item['scientific'])), None)
    if not entry and not bird:
        entry = next((item for item in entries if item['number'] == LABELS.get(key)), None)
    result = dict(entry) if entry else dict(name=label, scientific='', number=None, group='Bird' if bird else 'Bat', note='This prediction is outside the starter field guide. Explore its spectrogram and review the identification.', habitat='Not available in the starter guide.')
    result['in_catalogue'] = entry is not None
    if bird and not entry:
        scientific, separator, common = label.partition('_')
        if separator:
            result.update(name=common, scientific=scientific)
        result['note'] = 'BirdNET prediction outside the Bird Atlas. Review the identification and add this bird to the catalogue.'
    result['artwork'] = 'Stylised species portrait'
    result['portrait'] = ('bird' if bird else 'bat') + '-%03d' % result['number'] if result['number'] else None
    result['portrait_version'] = _VERSIONS.get(result['portrait'], '')
    if 'rarity' not in result:
        from chirpecho.common.rarity import rarity_for
        result['rarity'] = rarity_for('bird' if bird else 'bat')
    return result
