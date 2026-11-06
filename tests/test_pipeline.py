"""Regression tests use temporary files; never touch live recordings."""
import datetime as dt
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import queue
import threading
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
workspace = tempfile.TemporaryDirectory()
os.environ['LOG_DIR'] = workspace.name
os.environ['MIN_FREE_MB'] = '0'
os.environ['STATUS_DIR'] = workspace.name + '/status'
import numpy as np
import soundfile as sf
from recorder import recorder as recorder
from detector import detector as detector
from webapp import app as dashboard
from runtime import storage_available


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.incoming = self.root / 'incoming'
        self.pngs = self.root / 'pngs'
        self.incoming.mkdir()
        self.pngs.mkdir()
        self.settings = patch.multiple(detector, INCOMING_DIR=str(self.incoming),
                                       DETECTIONS_DIR=str(self.pngs),
                                       DB_PATH=str(self.root / 'db.sqlite3'))
        self.settings.start()
        self.conn = detector.init_db()
        self.audio = self.incoming / '20261106T180000123456Z_test.wav'
        sf.write(self.audio, np.zeros(38400, dtype=np.float32), 384000)

    def tearDown(self):
        self.conn.close()
        self.settings.stop()
        self.temp.cleanup()

    def annotation(self):
        return dict(start_time=0.01, end_time=0.02, class_prob=.9,
                    det_prob=.95, low_freq=20000, high_freq=50000,
                    **{'class': 'Test bat'})

    def test_timestamp_and_gate(self):
        value = detector.chunk_start_time(str(self.audio))
        self.assertEqual(value, dt.datetime(2026, 11, 6, 18, 0, 0, 123456,
                                           tzinfo=dt.timezone.utc))
        sos = recorder.build_filter()
        t = np.arange(38400) / 384000
        self.assertFalse(recorder.is_active(np.zeros(38400), sos))
        self.assertTrue(recorder.is_active(.1 * np.sin(2*np.pi*40000*t), sos))
        self.assertFalse(recorder.is_active(.1 * np.sin(2*np.pi*1000*t), sos))

    def test_completion_marker_prevents_replay(self):
        original = self.audio.read_bytes()
        with patch.object(detector.bd_api, 'process_file', return_value={'pred_dict': {'annotation': []}}) as model:
            detector.scan_once(self.conn)
            self.assertFalse(self.audio.exists())
            self.audio.write_bytes(original)  # Simulate crash after commit before unlink.
            detector.scan_once(self.conn)
            self.assertEqual(model.call_count, 1)
            self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM processed_files').fetchone()[0], 1)

    def test_transaction_rollback_preserves_audio(self):
        annotation = self.annotation()
        def fail(*args, **kwargs):
            raise RuntimeError('simulated renderer failure')
        with patch.object(detector.bd_api, 'process_file', return_value={'pred_dict': {'annotation': [annotation]}}), patch.object(detector, 'save_spectrogram_png', side_effect=fail):
            detector.scan_once(self.conn)
        self.assertTrue(self.audio.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 0)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM processed_files').fetchone()[0], 0)

    def test_partial_batch_rollback(self):
        annotations = [self.annotation(), dict(self.annotation(), start_time=.03, end_time=.04)]
        real_insert = detector.insert_detection
        inserted = []
        def insert(conn, row):
            if inserted:
                raise RuntimeError('simulated second-row failure')
            real_insert(conn, row)
            inserted.append(row)
        with patch.object(detector.bd_api, 'process_file', return_value={'pred_dict': {'annotation': annotations}}), patch.object(detector, 'insert_detection', side_effect=insert):
            detector.scan_once(self.conn)
        self.assertTrue(self.audio.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 0)
        self.assertEqual(list(self.pngs.glob('*.png')), [])

    def test_interrupted_claim_recovery(self):
        claimed = self.audio.with_name(self.audio.name + '.processing')
        self.audio.replace(claimed)
        detector.recover_interrupted()
        self.assertTrue(self.audio.exists())
        self.assertFalse(claimed.exists())

    def test_capture_queue_does_not_block(self):
        stop = threading.Event()
        chunks = queue.Queue(maxsize=1)
        class Stream:
            read_available = 0
            calls = 0
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, frames):
                self.calls += 1
                if self.calls == 3:
                    stop.set()
                return np.zeros((frames, 1), dtype=np.float32), False
        stream = Stream()
        with patch.object(recorder.sd, 'check_input_settings'), patch.object(recorder.sd, 'InputStream', return_value=stream):
            recorder.capture(chunks, stop, 32)
        self.assertEqual(stream.calls, 3)
        self.assertEqual(chunks.qsize(), 1)

    def test_poison_file_quarantine(self):
        with patch.object(detector.bd_api, 'process_file', side_effect=ValueError('bad WAV')):
            for _ in range(3):
                detector.scan_once(self.conn)
        self.assertTrue((self.incoming / 'failed' / self.audio.name).exists())
        self.assertFalse(self.audio.exists())

    def test_real_png_and_dashboard(self):
        with patch.object(detector.bd_api, 'process_file', return_value={'pred_dict': {'annotation': [self.annotation()]}}):
            detector.scan_once(self.conn)
        png = next(self.pngs.glob('*.png'))
        self.assertEqual(png.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
        with patch.multiple(dashboard, DB_PATH=detector.DB_PATH, DETECTIONS_DIR=str(self.pngs)):
            response = dashboard.app.test_client().get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'BatsDropping', response.data)
            self.assertIn(b'Test bat', response.data)
            ident = self.conn.execute('SELECT id FROM detections').fetchone()[0]
            image_response = dashboard.app.test_client().get(f'/spectrogram/{ident}.png')
            self.assertEqual(image_response.status_code, 200)
            self.assertEqual(image_response.mimetype, 'image/png')
            self.assertEqual(dashboard.app.test_client().get('/health').status_code, 200)
            self.assertIn(b'batsdropping_detections_total 1', dashboard.app.test_client().get('/metrics').data)

    def test_storage_failure_does_not_quarantine_valid_audio(self):
        with patch.object(detector.bd_api, 'process_file', return_value={'pred_dict': {'annotation': [self.annotation()]}}), patch.object(detector, 'save_spectrogram_png', side_effect=OSError(28, 'disk full')):
            for _ in range(3):
                detector.scan_once(self.conn)
        self.assertTrue(self.audio.exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM failed_files').fetchone()[0], 0)

    def test_archived_image_keeps_dashboard_metadata(self):
        self.conn.execute('INSERT INTO detections VALUES (?,?,?,?,?,?,?,?,?,?)',
            ('archived', '2026-11-06T18:00:00+00:00', 'Archived bat', .9, .9, 20000, 50000,
             str(self.pngs / 'gone.png'), 'original.wav', '2026-11-06'))
        self.conn.execute('INSERT INTO image_archive VALUES (?,?,?)', ('archived', '2026-11-06', 'disk pressure'))
        self.conn.commit()
        with patch.multiple(dashboard, DB_PATH=detector.DB_PATH, DETECTIONS_DIR=str(self.pngs)):
            response = dashboard.app.test_client().get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Archived bat', response.data)
            self.assertIn(b'Image cleared', response.data)
            self.assertIn(b'19:00:00', response.data)
            self.assertEqual(dashboard.app.test_client().get('/spectrogram/archived.png').status_code, 404)

    def test_gallery_pagination_and_invalid_filters(self):
        for number in range(25):
            self.conn.execute('INSERT INTO detections VALUES (?,?,?,?,?,?,?,?,?,?)',
                (f'row-{number}', '2026-11-06T18:00:00+00:00', 'Paged bat', .9, .9, 20000, 50000,
                 str(self.pngs / f'{number}.png'), 'source.wav', '2026-11-06'))
        self.conn.commit()
        with patch.multiple(dashboard, DB_PATH=detector.DB_PATH, DETECTIONS_DIR=str(self.pngs)):
            client = dashboard.app.test_client()
            self.assertIn(b'Page 1 of 2', client.get('/').data)
            self.assertIn(b'Page 2 of 2', client.get('/?page=2').data)
            self.assertIn(b'No matching encounters', client.get('/?q=nonexistent').data)
            self.assertEqual(client.get('/?confidence=nan').status_code, 400)

    def test_retention_only_removes_expired(self):
        self.conn.execute('INSERT INTO detections VALUES (?,?,?,?,?,?,?,?,?,?)',
            ('old', '2000-01-01T00:00:00+00:00', 'Old bat', .9, .9, 1, 2,
             str(self.pngs / 'old.png'), 'old.wav', '2000-01-01'))
        self.conn.commit()
        (self.pngs / 'old.png').write_bytes(b'old')
        with patch.dict(os.environ, RETENTION_DAYS='90'):
            detector.expire_detections(self.conn)
        self.assertFalse((self.pngs / 'old.png').exists())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0], 1)
        self.assertTrue(self.audio.exists())

    def test_storage_cap_counts_quarantine(self):
        quarantine = self.incoming / 'failed'
        quarantine.mkdir()
        with (quarantine / 'failed.wav').open('wb') as output:
            output.truncate(1024 * 1024)
        with patch.dict(os.environ, MAX_AUDIO_MB='1'):
            self.assertFalse(storage_available(self.incoming, 1))


if __name__ == '__main__':
    unittest.main()
