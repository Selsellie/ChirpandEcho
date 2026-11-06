import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from collections import namedtuple
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import storage

Disk = namedtuple('Disk', 'total used free')


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('CREATE TABLE detections (id TEXT, png_path TEXT, detected_at TEXT)')
        storage.init_archive_schema(self.conn)
        self.environment = patch.dict(os.environ, MIN_FREE_MB='0', RETENTION_DAYS='0',
                                       STORAGE_HIGH_WATER_PERCENT='85', STORAGE_LOW_WATER_PERCENT='80')
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.conn.close()
        self.temp.cleanup()

    def image(self, ident, date):
        path = self.directory / f'{ident}.png'
        path.write_bytes(b'image')
        self.conn.execute('INSERT INTO detections VALUES (?,?,?)', (ident, str(path), date))
        self.conn.commit()
        return path

    def test_oldest_png_removed_but_all_metadata_kept(self):
        old = self.image('old', '2020-01-01')
        new = self.image('new', '2026-01-01')
        def disk(_):
            return Disk(100, 90, 10) if old.exists() else Disk(100, 70, 30)
        with patch.object(storage.shutil, 'disk_usage', side_effect=disk):
            storage.manage_archive(self.conn, self.directory)
        self.assertFalse(old.exists())
        self.assertTrue(new.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 2)
        self.assertEqual(self.conn.execute('SELECT detection_id,reason FROM image_archive').fetchone(), ('old', 'disk pressure'))

    def test_failed_delete_is_journaled_and_retried(self):
        image = self.image('old', '2000-01-01')
        storage.queue_image(self.conn, ('old', str(image)), 'disk pressure')
        with patch.object(Path, 'unlink', side_effect=PermissionError('simulated')):
            storage.drain_queue(self.conn, self.directory)
        self.assertTrue(image.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM image_cleanup_queue').fetchone()[0], 1)
        storage.drain_queue(self.conn, self.directory)
        self.assertFalse(image.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM image_cleanup_queue').fetchone()[0], 0)

    def test_recover_after_unlink_before_database_commit(self):
        image = self.image('old', '2000-01-01')
        storage.queue_image(self.conn, ('old', str(image)), 'disk pressure')
        image.unlink()
        storage.drain_queue(self.conn, self.directory)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM image_archive').fetchone()[0], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 1)

    def test_normal_disk_preserves_png(self):
        image = self.image('old', '2000-01-01')
        with patch.object(storage.shutil, 'disk_usage', return_value=Disk(100, 40, 60)):
            storage.manage_archive(self.conn, self.directory)
        self.assertTrue(image.exists())
