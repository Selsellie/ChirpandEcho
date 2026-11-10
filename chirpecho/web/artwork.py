"""Shared browsing sections; native catalogue species types remain unchanged.

Always resolve membership from the full catalogue type, never filtered results.
Milestone collecting sets have independent, explicit scientific-name checklists.
"""

_BIRD_SECTIONS = {
    'Birds of prey': 'Birds of prey and owls',
    'Owls': 'Birds of prey and owls',
    'Crows': 'Crows, jays and starlings',
    'Magpies': 'Crows, jays and starlings',
    'Jays': 'Crows, jays and starlings',
    'Nutcrackers': 'Crows, jays and starlings',
    'Starlings': 'Crows, jays and starlings',
    'Pigeons and doves': 'Pigeons and doves',
    'Ducks': 'Ducks, geese and swans',
    'Geese': 'Ducks, geese and swans',
    'Swans': 'Ducks, geese and swans',
    'Herons': 'Herons, storks, cranes and lapwings',
    'Storks': 'Herons, storks, cranes and lapwings',
    'Cranes': 'Herons, storks, cranes and lapwings',
    'Lapwings': 'Herons, storks, cranes and lapwings',
    'Rails and coots': 'Rails and coots',
    'Gulls': 'Gulls, terns and cormorants',
    'Terns': 'Gulls, terns and cormorants',
    'Cormorants': 'Gulls, terns and cormorants',
    'Woodpeckers': 'Woodpeckers, nuthatches and treecreepers',
    'Nuthatches': 'Woodpeckers, nuthatches and treecreepers',
    'Treecreepers': 'Woodpeckers, nuthatches and treecreepers',
    'Swifts': 'Swifts, swallows and nightjars',
    'Swallows': 'Swifts, swallows and nightjars',
    'Nightjars': 'Swifts, swallows and nightjars',
    'Cuckoos': 'Cuckoos, kingfishers, rollers and bee-eaters',
    'Kingfishers': 'Cuckoos, kingfishers, rollers and bee-eaters',
    'Rollers': 'Cuckoos, kingfishers, rollers and bee-eaters',
    'Bee-eaters': 'Cuckoos, kingfishers, rollers and bee-eaters',
    'Tits': 'Tits, long-tailed tits and crests',
    'Long-tailed tits': 'Tits, long-tailed tits and crests',
    'Crests': 'Tits, long-tailed tits and crests',
    'Finches': 'Finches, sparrows and buntings',
    'Sparrows': 'Finches, sparrows and buntings',
    'Buntings': 'Finches, sparrows and buntings',
    'Thrushes': 'Thrushes and flycatchers',
    'Flycatchers': 'Thrushes and flycatchers',
    'Warblers': 'Warblers, wrens and accentors',
    'Wrens': 'Warblers, wrens and accentors',
    'Accentors': 'Warblers, wrens and accentors',
    'Wagtails': 'Wagtails, pipits and larks',
    'Pipits': 'Wagtails, pipits and larks',
    'Larks': 'Wagtails, pipits and larks',
}
_BAT_SECTIONS = {
    'Pipistrelles': 'Pipistrelles',
    'Open-air hunters': 'Open-air hunters',
    'Mouse-eared bats': 'Mouse-eared bats',
    'Long-eared bats': 'Long-eared bats and barbastelles',
    'Woodland specialists': 'Long-eared bats and barbastelles',
    'Horseshoe bats': 'Horseshoe and bent-winged bats',
    'Cave specialists': 'Horseshoe and bent-winged bats',
}


def artwork_group(item):
    sections = _BIRD_SECTIONS if item['kind'] == 'bird' else _BAT_SECTIONS
    return sections.get(item['group'], item['group'])


def artwork_sort_key(item, display_name=str):
    """Keep native types together within each translated browsing section."""
    section = artwork_group(item)
    return (section == 'Others', display_name(section).casefold(),
            display_name(item['group']).casefold(),
            display_name(item['name']).casefold())
