"""Regression checks for browsing sections, native types and collecting goals.

Run with: python -m unittest discover -s tests -v
"""
import datetime as dt
import unittest
from collections import Counter
from unittest.mock import patch

from flask import template_rendered
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS
from chirpecho.web import app as web
from chirpecho.web.artwork import artwork_group, artwork_sort_key
from chirpecho.web.collection import collection_history, milestone_report
from chirpecho.web.i18n import TEXT
from chirpecho.web.milestones import BIRD_COLLECTIONS, BAT_COLLECTIONS
from chirpecho.web.portraits import profile


class SpeciesGroupsTests(unittest.TestCase):
    def test_native_types_and_aliases_are_preserved(self):
        for catalogue, bird in ((BIRDS, True), (BATS, False)):
            for item in catalogue:
                for label in (item['name'], item['scientific'],
                              item['scientific'] + '_' + item['name']):
                    resolved = profile(label, bird)
                    self.assertEqual(resolved['number'], item['number'])
                    self.assertEqual(resolved['group'], item['group'])
                self.assertIn(item['group'], TEXT)
        self.assertEqual(profile('Sturnus vulgaris', True)['group'], 'Starlings')
        self.assertEqual(profile('Fringilla coelebs', True)['group'], 'Finches')
        self.assertEqual(profile('Sylvia communis', True)['scientific'], 'Curruca communis')

    def test_specific_corvid_and_wagtail_types(self):
        expected = {
            'Corvus corone': 'Crows',
            'Pica pica': 'Magpies',
            'Garrulus glandarius': 'Jays',
            'Nucifraga caryocatactes': 'Nutcrackers',
            'Motacilla alba': 'Wagtails',
            'Motacilla flava': 'Wagtails',
            'Anthus pratensis': 'Pipits',
        }
        for scientific, group in expected.items():
            with self.subTest(scientific=scientific):
                self.assertEqual(profile(scientific, True)['group'], group)
                self.assertIn(group, TEXT)

    def test_complete_catalogue_sections(self):
        expected = {
            'Birds of prey and owls': 12, 'Crows, jays and starlings': 7,
            'Pigeons and doves': 4, 'Ducks, geese and swans': 13,
            'Herons, storks, cranes and lapwings': 7, 'Rails and coots': 2,
            'Gulls, terns and cormorants': 4,
            'Woodpeckers, nuthatches and treecreepers': 5,
            'Swifts, swallows and nightjars': 4,
            'Cuckoos, kingfishers, rollers and bee-eaters': 4,
            'Tits, long-tailed tits and crests': 7,
            'Finches, sparrows and buntings': 9, 'Thrushes and flycatchers': 8,
            'Warblers, wrens and accentors': 7, 'Wagtails, pipits and larks': 6,
        }
        self.assertEqual(Counter(artwork_group(dict(b, kind='bird')) for b in BIRDS), expected)
        bats = Counter(artwork_group(dict(b, kind='bat')) for b in BATS)
        self.assertEqual(sorted(bats.values()), [3, 3, 4, 5, 9])
        for group in expected.keys() | bats.keys():
            self.assertIn(group, TEXT)

    def test_species_filters_match_artwork_and_keep_native_card_types(self):
        web.app.config['TESTING'] = True
        client = web.app.test_client()
        contexts = []
        def capture(sender, template, context, **extra):
            contexts.append(context)
        with template_rendered.connected_to(capture, web.app), patch.object(web, 'query', return_value=[]):
            for kind, catalogue, path in (('bird', BIRDS, '/chirp/species'), ('bat', BATS, '/species')):
                for lang in ('en', 'nl'):
                    response = client.get(path, query_string={'lang': lang})
                    self.assertEqual(response.status_code, 200)
                    display = (lambda value: TEXT.get(value, value)) if lang == 'nl' else str
                    cards = contexts[-1]['catalogue']
                    keys = [artwork_sort_key(dict(item, kind=kind), display) for item in cards]
                    self.assertEqual(keys, sorted(keys))
                    options = contexts[-1]['group_options']
                    labels = list(options.values())
                    self.assertEqual(labels, sorted(labels, key=lambda g: (TEXT[g] if lang == 'nl' else g).casefold()))
                    expected = {artwork_group(dict(b, kind=kind)) for b in catalogue}
                    self.assertEqual(set(labels), expected)
                    for slug, group in options.items():
                        response = client.get(path, query_string={'group': slug, 'lang': lang})
                        self.assertEqual(response.status_code, 200)
                        context = contexts[-1]
                        wanted = {b['number'] for b in catalogue if artwork_group(dict(b, kind=kind)) == group}
                        self.assertEqual({b['number'] for b in context['catalogue']}, wanted)
                        self.assertEqual(context['group_options'], options)
                        for item in context['catalogue']:
                            self.assertEqual(item['group'], catalogue[item['number'] - 1]['group'])
                        client.get(path, query_string={'group': slug, 'lang': lang, 'q': 'no-matching-species-xyz'})
                        self.assertEqual(contexts[-1]['catalogue'], [])
                        self.assertEqual(contexts[-1]['group_options'], options)
                    client.get('/artwork', query_string={'kind': kind, 'lang': lang})
                    self.assertEqual(set(contexts[-1]['artwork_groups']), expected)
                    for cards in contexts[-1]['artwork_groups'].values():
                        keys = [artwork_sort_key(item, display) for item in cards]
                        self.assertEqual(keys, sorted(keys))
            response = client.get('/chirp/species', query_string={'q': 'Sturnus vulgaris', 'lang': 'nl'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual([b['group'] for b in contexts[-1]['catalogue']], ['Starlings'])
            self.assertIn('>Spreeuwen<', response.get_data(as_text=True))


class MilestoneTests(unittest.TestCase):
    @staticmethod
    def history(kind, names):
        return dict(daily=[dict(kind=kind, day=dt.date(2026, 11, 10), calls=1,
                               key=(kind, name)) for name in names])

    def test_all_collecting_sets_membership_completion_and_translations(self):
        for kind, catalogue, sets in (('bird', BIRDS, BIRD_COLLECTIONS), ('bat', BATS, BAT_COLLECTIONS)):
            known = {b['scientific']: b for b in catalogue}
            self.assertEqual(len({s[0] for s in sets}), len(sets))
            for ident, title, description, members in sets:
                self.assertEqual(len(set(members)), len(members))
                self.assertIn(title, TEXT)
                self.assertIn(description, TEXT)
                for name in members:
                    self.assertIn(name, known)
                    self.assertTrue(known[name]['supported'])
                    self.assertIsNotNone(profile(name, kind == 'bird')['portrait'])
                for names, complete in (((), False), (members[:-1], False), (members, True)):
                    report = milestone_report(self.history(kind, names), kind)
                    card = next(c for c in report['cards'] if c['id'] == ident)
                    self.assertEqual(card['target'], len(members))
                    self.assertEqual(card['value'], len(names))
                    self.assertEqual(card['unlocked'], complete)
                    self.assertEqual([m['profile']['scientific'] for m in card['members']], list(members))
                    self.assertEqual(sum(m['recorded'] for m in card['members']), len(names))

    def test_atlas_targets_and_alias_collection(self):
        for kind, catalogue, target in (('bird', BIRDS, 99), ('bat', BATS, 17)):
            names = tuple(b['scientific'] for b in catalogue if b['supported'])
            for recorded, complete in ((names[:-1], False), (names, True)):
                report = milestone_report(self.history(kind, recorded), kind)
                atlas = next(c for c in report['cards'] if c['id'] == kind + '-atlas')
                self.assertEqual(atlas['target'], target)
                self.assertEqual(atlas['unlocked'], complete)
            for item in catalogue:
                rows = [dict(day='2026-11-10', species=item['scientific'], calls=1, best=.9),
                        dict(day='2026-11-10', species=item['name'], calls=1, best=.9)]
                history = collection_history(lambda *args, **kwargs: rows, {kind: 'unused'})
                self.assertEqual(len(history['profiles']), 1)
                self.assertEqual(milestone_report(history, kind)['species'], 1)
        combined = milestone_report(dict(daily=[]))
        self.assertEqual(combined['total'], 43)
        self.assertEqual(len({c['id'] for c in combined['cards']}), 43)
        for card in combined['cards']:
            self.assertIn(card['title'], TEXT)
            self.assertIn(card['description'], TEXT)


if __name__ == '__main__':
    unittest.main()
