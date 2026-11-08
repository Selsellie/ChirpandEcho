import datetime as dt
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from chirpecho.web import app as web
from chirpecho.web.collection import collection_history, milestone_report, weekly_report


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.birds = str(Path(self.temp.name) / 'birds.sqlite3')
        self.bats = str(Path(self.temp.name) / 'bats.sqlite3')
        for database in (self.birds, self.bats):
            with closing(sqlite3.connect(database)) as conn, conn:
                conn.execute('CREATE TABLE detections '
                             '(id TEXT, species TEXT, detected_at TEXT, confidence REAL)')
        self.patcher = patch.multiple(web, BIRD_DB_PATH=self.birds, DB_PATH=self.bats,
                                      ZONE=ZoneInfo('Europe/Amsterdam'))
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.addCleanup(self.temp.cleanup)
        self.client = web.app.test_client()

    def add(self, database, species, when, ident='test'):
        with closing(sqlite3.connect(database)) as conn, conn:
            conn.execute('INSERT INTO detections VALUES (?, ?, ?, ?)',
                         (ident, species, when, .95))

    def history(self):
        with web.app.test_request_context('/calendar'):
            return collection_history(web.query, web.collection_databases())

    def test_local_midnight_and_week_boundaries(self):
        # Sunday in UTC, Monday locally. Next Sunday night is next Monday locally.
        self.add(self.birds, 'Eurasian Blackbird', '2026-11-01T23:30:00+00:00')
        self.add(self.birds, 'European Robin', '2026-11-08T23:30:00+00:00')
        report = weekly_report(self.history(), dt.date(2026, 11, 2), dt.date(2026, 11, 2))
        self.assertEqual(report['total'], 1)
        self.assertEqual(report['days'][0]['bird'], 1)
        self.assertEqual(report['newcomers'][0]['profile']['name'], 'Eurasian Blackbird')

    def test_aliases_do_not_inflate_species_or_newcomers(self):
        self.add(self.birds, 'Turdus merula', '2026-10-01T12:00:00+02:00')
        self.add(self.birds, 'Eurasian Blackbird', '2026-11-03T12:00:00+01:00')
        self.add(self.birds, 'Turdus merula_Eurasian Blackbird', '2026-11-04T12:00:00+01:00')
        history = self.history()
        report = weekly_report(history, dt.date(2026, 11, 2), dt.date(2026, 11, 3))
        self.assertEqual(report['species_count'], 1)
        self.assertEqual(report['total'], 2)
        self.assertEqual(report['newcomers'], [])
        self.assertEqual(milestone_report(history)['species'], 1)

    def test_streak_combines_pipelines_without_counting_day_twice(self):
        for index in range(7):
            day = dt.date(2026, 11, 2) + dt.timedelta(days=index)
            self.add(self.birds if index % 2 else self.bats,
                     'Eurasian Blackbird' if index % 2 else 'Common Pipistrelle',
                     day.isoformat() + 'T12:00:00+01:00')
        self.add(self.birds, 'Eurasian Blackbird', '2026-11-02T09:00:00+01:00')
        report = milestone_report(self.history())
        self.assertEqual(report['longest'], 7)
        self.assertEqual(report['active_days'], 7)
        cards = {item['title']: item for item in report['cards']}
        self.assertFalse(cards['A week of listening']['unlocked'])
        self.assertFalse(cards['A whole chorus']['unlocked'])
        self.assertFalse(cards['The night club']['unlocked'])
        # Progress reflects explicit deletions, rather than awarding from stale counters.
        with closing(sqlite3.connect(self.bats)) as conn, conn:
            conn.execute("DELETE FROM detections WHERE detected_at LIKE '2026-11-04%'")
        self.assertEqual(milestone_report(self.history())['longest'], 4)

    def test_invalid_timestamps_are_excluded(self):
        self.add(self.birds, 'European Robin', 'broken date')
        self.assertEqual(milestone_report(self.history())['unlocked'], 0)

    def test_empty_pages_and_translations(self):
        for path in ('/calendar', '/milestones', '/calendar?lang=nl', '/milestones?lang=nl'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'/calendar', response.data)
                self.assertIn(b'/milestones', response.data)
        self.assertIn(b'Kalender.', self.client.get('/calendar?lang=nl').data)
        self.assertIn(b'Mijlpalen.', self.client.get('/milestones?lang=nl').data)
        self.assertIn(b'0 <span>/ 37</span>', self.client.get('/milestones?lang=en').data)

    def test_missing_databases(self):
        with patch.multiple(web, DB_PATH='/nonexistent/bats.sqlite3', BIRD_DB_PATH='/nonexistent/birds.sqlite3'):
            self.assertEqual(self.client.get('/calendar').status_code, 200)
            self.assertEqual(self.client.get('/milestones').status_code, 200)

    def test_date_validation_and_monday_normalization(self):
        for query in ('week=nope', 'week=0001-01-01', 'week=9999-12-31', 'day=nope'):
            self.assertEqual(self.client.get('/calendar?' + query).status_code, 400)
        page = self.client.get('/calendar?week=2026-11-05&day=2026-12-01').get_data(as_text=True)
        self.assertIn('02 Nov – 08 Nov 2026', page)
        self.assertIn('Monday · 02 November 2026', page)

    def test_day_timeline_and_repeated_dst_hour(self):
        self.add(self.birds, 'European Robin', '2026-10-25T00:30:00+00:00', 'early')
        self.add(self.birds, 'European Robin', '2026-10-25T01:30:00+00:00', 'late')
        self.add(self.bats, 'Common Pipistrelle', '2026-10-25T03:00:00+01:00')
        page = self.client.get('/calendar?week=2026-10-25&day=2026-10-25').get_data(as_text=True)
        self.assertIn('02:00 · 2 birds · 0 bats', page)
        self.assertIn('03:00 · 0 birds · 1 bats', page)
        self.assertIn('European Robin', page)
        self.assertIn('Common pipistrelle', page)
        self.assertIn('3</div><div class="stat-note">2 birds · 1 bats', page)

    def test_external_species_and_html_escaping(self):
        self.add(self.birds, 'Cardinalis cardinalis_Northern Cardinal', '2026-11-03T12:00:00+01:00')
        self.add(self.birds, '<script>alert(1)</script>', '2026-11-03T13:00:00+01:00')
        page = self.client.get('/calendar?week=2026-11-02&day=2026-11-03').get_data(as_text=True)
        self.assertIn('Northern Cardinal', page)
        self.assertIn('Not in catalogue', page)
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertEqual(milestone_report(self.history())['species'], 2)


    def test_bird_sets_count_species_once_and_only_in_the_correct_set(self):
        for label in ('Parus major', 'Great Tit', 'Parus major_Great Tit'):
            self.add(self.birds, label, '2026-11-03T12:00:00+01:00')
        self.add(self.birds, 'Anser anser_Greylag Goose', '2026-11-03T13:00:00+01:00')
        self.add(self.birds, 'Anser albifrons', '2026-11-03T14:00:00+01:00')
        self.add(self.birds, 'Unknown species_Some Tit', '2026-11-03T15:00:00+01:00')
        cards = {card['id']: card for card in milestone_report(self.history(), 'bird')['cards']}
        self.assertEqual(cards['tit-club']['value'], 1)
        self.assertEqual(cards['tit-club']['target'], 5)
        self.assertEqual(cards['goose-parade']['value'], 2)
        self.assertFalse(cards['goose-parade']['unlocked'])
        self.assertEqual(cards['owl-patrol']['value'], 0)
        self.assertEqual(sum(member['recorded'] for member in cards['tit-club']['members']), 1)
        self.add(self.birds, 'Branta canadensis', '2026-11-03T16:00:00+01:00')
        cards = {card['id']: card for card in milestone_report(self.history(), 'bird')['cards']}
        self.assertTrue(cards['goose-parade']['unlocked'])
        self.assertEqual(cards['goose-parade']['percent'], 100)
        self.assertTrue(all(member['recorded'] for member in cards['goose-parade']['members']))

    def test_every_milestone_has_existing_illustrations_and_valid_checklists(self):
        from chirpecho.chirp.catalogue import SPECIES as BIRDS
        from chirpecho.echo.catalogue import SPECIES as BATS
        catalogues = {'bird': {item['scientific'] for item in BIRDS},
                      'bat': {item['scientific'] for item in BATS if item['supported']}}
        report = milestone_report(self.history())
        self.assertEqual(report['total'], 37)
        self.assertEqual(len({card['id'] for card in report['cards']}), report['total'])
        for card in report['cards']:
            with self.subTest(card=card['id']):
                self.assertGreater(len(card['artwork']), 0)
                for portrait in card['artwork']:
                    self.assertTrue(portrait['portrait'])
                    self.assertTrue(portrait['portrait_version'])
                    self.assertTrue((Path(web.app.static_folder) / 'species' /
                                     (portrait['portrait'] + '-pokemon.webp')).is_file())
                if card['members']:
                    names = [member['profile']['scientific'] for member in card['members']]
                    self.assertEqual(len(names), card['target'])
                    self.assertEqual(len(names), len(set(names)))
                    self.assertTrue(set(names).issubset(catalogues[card['kind']]))

    def test_dutch_set_names_and_illustrated_cards(self):
        page = self.client.get('/milestones?lang=nl').get_data(as_text=True)
        for title in ('De mezenclub', 'Ganzenparade', 'Uilenpatrouille', 'Vinkenfeest'):
            self.assertIn(title, page)
        self.assertIn('Bekijk de soorten', page)
        self.assertEqual(page.count('class="card milestone-card locked"'), 37)
        self.assertNotIn('milestone-icon', page)
        self.assertIn('/static/species/bird-003-pokemon.webp', page)

    def test_calendar_links_to_each_pipelines_audio_and_spectrogram(self):
        audio_dir = Path(self.temp.name) / 'audio'
        images_dir = Path(self.temp.name) / 'images'
        audio_dir.mkdir()
        images_dir.mkdir()
        (audio_dir / 'bird.wav').write_bytes(b'fixture')
        image = images_dir / 'bird.spec'
        image.write_bytes(b'fixture')
        self.add(self.birds, 'Great Tit', '2026-11-03T12:00:00+01:00', 'bird-id')
        self.add(self.bats, 'Common Pipistrelle', '2026-11-03T20:00:00+01:00', 'bat-id')
        for database, filename in ((self.birds, 'bird.wav'), (self.bats, 'missing.wav')):
            with closing(sqlite3.connect(database)) as conn, conn:
                conn.execute('ALTER TABLE detections ADD COLUMN source_file TEXT')
                conn.execute('ALTER TABLE detections ADD COLUMN png_path TEXT')
                conn.execute('UPDATE detections SET source_file=?, png_path=?', (filename, str(image)))
        with patch.multiple(web, BIRD_AUDIO_ARCHIVE_DIR=str(audio_dir),
                            BIRD_DETECTIONS_DIR=str(images_dir),
                            ECHO_AUDIO_ARCHIVE_DIR=str(audio_dir), DETECTIONS_DIR=self.temp.name):
            page = self.client.get('/calendar?week=2026-11-02&day=2026-11-03').get_data(as_text=True)
        self.assertIn('/chirp/observation/bird-id/audio', page)
        self.assertIn('/chirp/spectrogram/bird-id', page)
        self.assertNotIn('/observation/bat-id/audio', page)
        self.assertIn('class="card detection encounter"', page)
        self.assertIn('class="card weekly-report"', page)
        self.assertNotIn('class="card weekly-report" open', page)


    def test_shared_pages_have_no_switch_and_do_have_shared_text(self):
        for path in ('/calendar', '/status', '/milestones'):
            for mode in ('chirp', 'echo'):
                self.client.set_cookie('wildlife-mode', mode)
                response = self.client.get(path + '?lang=nl')
                page = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('<nav class="mode-switch"', page)
                self.assertIn('Vogels en vleermuizen · ', page)
                self.assertNotIn('Vleermuizen · De nachtdienst', page)
                self.assertNotIn('Vogels · Het koor overdag', page)
        # The illustration page still has its working species selector.
        page = self.client.get('/artwork?kind=bird&lang=en').get_data(as_text=True)
        self.assertIn('<nav class="mode-switch"', page)

    def test_bat_goals_use_bat_observations_and_bat_artwork(self):
        from chirpecho.web.milestones import BAT_COLLECTIONS
        self.add(self.birds, 'Great Tit', '2026-11-03T12:00:00+01:00')
        history = self.history()
        bats = milestone_report(history, 'bat')
        self.assertEqual(bats['species'], 0)
        self.assertEqual(bats['unlocked'], 0)
        for scientific in BAT_COLLECTIONS[0][3]:
            self.add(self.bats, scientific, '2026-11-03T20:00:00+01:00')
        bats = milestone_report(self.history(), 'bat')
        cards = {card['id']: card for card in bats['cards']}
        self.assertTrue(cards['pipistrelle-trio']['unlocked'])
        self.assertEqual(cards['pipistrelle-trio']['value'], 3)
        self.assertFalse(cards['bat-colony']['unlocked'])
        self.assertEqual(cards['bat-atlas']['target'], 17)
        self.assertTrue(all(portrait['portrait'].startswith('bat-')
                            for card in bats['cards'] for portrait in card['artwork']))
        page = self.client.get('/milestones?lang=en').get_data(as_text=True)
        self.assertIn('The tit club', page)
        self.assertIn('The pipistrelle trio', page)
        self.assertIn('/species#bat-1', page)
        self.assertIn('/chirp/species#bat-3', page)


if __name__ == '__main__':
    unittest.main()
