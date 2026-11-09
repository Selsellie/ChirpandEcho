"""Stable browsing sections for the artwork gallery, independent of filtering."""

from collections import Counter

from chirpecho.chirp.catalogue import SPECIES as BIRDS

_BIRD_COUNTS = Counter(species["group"] for species in BIRDS)

FINCHES = {7, 8, 9, 58, 60, 63}
TITS = {3, 4, 25, 26, 27, 90}

_BIRD_SECTIONS = {
    'Ducks': 'Ducks, geese and swans',
    'Geese and swans': 'Ducks, geese and swans',
}
_BAT_SECTIONS = {
    'Woodland specialists': 'Long-eared bats and woodland specialists',
    'Long-eared bats': 'Long-eared bats and woodland specialists',
    'Cave specialists': 'Horseshoe and cave bats',
    'Horseshoe bats': 'Horseshoe and cave bats',
}


def artwork_group(item):
    if item['kind'] == 'bird':
        if item['number'] in FINCHES:
            return 'Finches'
        if item['number'] in TITS:
            return 'Tits'
        if _BIRD_COUNTS[item['group']] == 1:
            return 'Others'
        return _BIRD_SECTIONS.get(item['group'], item['group'])
    return _BAT_SECTIONS.get(item['group'], item['group'])
