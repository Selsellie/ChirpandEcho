"""Dashboard diagnostics use isolated logs, status files and database."""
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

from webapp import app as dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, LOG_DIR=str(self.root), STATUS_DIR=str(self.root), MIN_FREE_MB='1024')
        self.env.start()
        self.settings = patch.multiple(dashboard, DB_PATH=str(self.root / 'archive.db'),
                                       DETECTIONS_DIR=str(self.root))
        self.settings.start()
        self.client = dashboard.app.test_client()

    def tearDown(self):
        self.settings.stop()
        self.env.stop()
        self.temp.cleanup()

    def test_navigation_and_unavailable_health(self):
        for path, title in [('/', 'Night watch.'), ('/logs', 'Log summaries'), ('/status', 'System health'), ('/species', 'Batlas.')]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(title.encode(), response.data)
            self.assertIn(b'Appearance', response.data)
        self.assertIn(b'Attention needed', self.client.get('/status').data)
        with dashboard.app.test_request_context():
            from flask import url_for
            self.assertEqual(url_for('index'), '/')

    def test_species_collection_matches_exact_labels_and_keeps_groups_unresolved(self):
        from webapp.species import SPECIES
        self.assertEqual(len(SPECIES), 24)
        self.assertEqual(sum(item['supported'] for item in SPECIES), 17)
        conn = sqlite3.connect(dashboard.DB_PATH)
        try:
            conn.execute('CREATE TABLE detections(species TEXT, detected_at TEXT, confidence REAL)')
            conn.executemany('INSERT INTO detections VALUES (?,?,?)', [
                ('Pipistrellus pipistrellus', '2026-11-01T20:00:00+00:00', .8),
                ('Common pipistrelle', '2026-11-02T20:00:00+00:00', .95),
                ('Barbastellus barbastellus', '2026-11-03T20:00:00+00:00', .9),
                ('Myotis sp.', '2026-11-03T20:00:00+00:00', .9),
                ('Pipistrellus pipistrellus / pygmaeus', '2026-11-03T20:00:00+00:00', .9),
                ('Unknown bat', '2026-11-03T20:00:00+00:00', .9),
            ])
            conn.commit()
        finally:
            conn.close()
        body = self.client.get('/species?collection=recorded').data
        self.assertIn(b'Common pipistrelle', body)
        self.assertIn(b'2 calls recorded', body)
        self.assertIn(b'95.0%', body)
        self.assertIn(b'Barbastelle', body)
        self.assertNotIn(b'<h2>Soprano pipistrelle</h2>', body)
        self.assertIn(b'3 detections have labels outside', body)
        self.assertIn(b'q=Pipistrellus+pipistrellus', body)
        self.assertNotIn(b'<h2>Common pipistrelle</h2>', self.client.get('/species?collection=undiscovered').data)
        self.assertIn(b'No species match', self.client.get('/species?q=does-not-exist').data)
        self.assertIn(b'Pond bat', self.client.get('/species?q=dasycneme').data)
        self.assertEqual(self.client.get('/species?collection=invalid').status_code, 400)

    def test_log_summary_and_html_escaping(self):
        (self.root / 'recorder.log').write_text(
            '2026-11-07 12:00:00,000 INFO recorder capture healthy: 12 chunks checked, 1 retained, 2 cooldown skips in last minute\n'
            '2026-11-07 12:00:01,000 WARNING recorder <script>alert(1)</script>\n')
        (self.root / 'detector.log').write_text(
            '2026-11-07 12:00:02,000 INFO detector test.wav: 3 raw detections, 0 above confidence threshold (0.50)\n')
        summary = dashboard.log_summary()
        self.assertEqual(summary['totals'], dict(checked=12, saved=1, cooldown=2, processed=1, raw=3, accepted=0))
        self.assertEqual(summary['warnings'], 1)
        response = self.client.get('/logs')
        self.assertIn(b'Sound recorded, no qualifying bat calls.', response.data)
        self.assertNotIn(b'<script>alert(1)</script>', response.data)
        self.assertIn(b'&lt;script&gt;', response.data)

    def test_health_fresh_stale_and_malformed(self):
        status = self.root / 'recorder.json'
        for content in ['null', '[]', '{bad', '{"updated_at":"invalid"}']:
            status.write_text(content)
            self.assertFalse(dashboard.pipeline_status('recorder')['fresh'])
        status.write_text(json.dumps(dict(updated_at=time.time(), state='listening')))
        self.assertTrue(dashboard.pipeline_status('recorder')['fresh'])
        status.write_text(json.dumps(dict(updated_at=time.time()-31, state='listening')))
        self.assertFalse(dashboard.pipeline_status('recorder')['fresh'])
        with sqlite3.connect(dashboard.DB_PATH) as conn:
            conn.execute('CREATE TABLE image_archive(id TEXT)')
        fresh = dict(fresh=True, state='ready')
        storage = dict(free_bytes=2*1024**3, free_gb=2, used_percent=50, high_water=85)
        self.assertTrue(all(check['ok'] for check in dashboard.health_checks(fresh, fresh, storage)))
        storage['free_bytes'] = 0
        self.assertFalse(dashboard.health_checks(fresh, fresh, storage)[-1]['ok'])


if __name__ == '__main__':
    unittest.main()
