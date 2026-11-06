import datetime as dt
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recorder import recorder as recorder


class CooldownTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / '.cooldown'
        self.cooldown = recorder.Cooldown(10, self.path)

    def tearDown(self):
        self.temp.cleanup()

    def arm(self):
        with patch.object(recorder.time, 'monotonic', return_value=100), patch.object(recorder.time, 'time', return_value=1000):
            self.cooldown.saved()

    def test_ten_second_boundary(self):
        self.arm()
        self.assertFalse(self.cooldown.ready(109.999))
        self.assertTrue(self.cooldown.ready(110))

    def test_short_ultrasonic_pulse_passes_gate(self):
        import numpy as np
        audio = np.zeros(recorder.SAMPLE_RATE * 5, dtype=np.float32)
        samples = int(recorder.SAMPLE_RATE * .01)
        t = np.arange(samples) / recorder.SAMPLE_RATE
        audio[recorder.SAMPLE_RATE:recorder.SAMPLE_RATE + samples] = .1 * np.sin(2*np.pi*40000*t)
        self.assertTrue(recorder.is_active(audio, recorder.build_filter()))

    def test_stale_capture_is_not_accepted_later(self):
        self.arm()
        with patch.object(recorder.time, 'monotonic', return_value=120), patch.object(recorder, 'is_active') as gate, patch.object(recorder, 'write_chunk') as writer:
            result = recorder.process_chunk(None, None, 105, None, self.cooldown)
        self.assertEqual(result, 'cooldown')
        gate.assert_not_called()
        writer.assert_not_called()

    def test_quiet_and_failed_writes_do_not_arm(self):
        with patch.object(recorder, 'is_active', return_value=False), patch.object(recorder, 'write_chunk') as writer:
            self.assertEqual(recorder.process_chunk(None, None, 100, None, self.cooldown), 'discarded')
            writer.assert_not_called()
        with patch.object(recorder, 'is_active', return_value=True), patch.object(recorder, 'write_chunk', return_value=False):
            self.assertEqual(recorder.process_chunk(None, None, 100, None, self.cooldown), 'discarded')
        self.assertFalse(self.path.exists())
        self.assertTrue(self.cooldown.ready(100))

    def test_successful_activity_arms_cooldown(self):
        with patch.object(recorder, 'is_active', return_value=True), patch.object(recorder, 'write_chunk', return_value=True), patch.object(recorder.time, 'monotonic', return_value=100):
            self.assertEqual(recorder.process_chunk(None, None, 99, None, self.cooldown), 'saved')
        self.assertFalse(self.cooldown.ready(109))
        self.assertTrue(self.path.exists())

    def test_restart_preserves_remaining_time(self):
        self.arm()
        with patch.object(recorder.time, 'monotonic', return_value=200), patch.object(recorder.time, 'time', return_value=1004):
            restarted = recorder.Cooldown(10, self.path)
        self.assertFalse(restarted.ready(205.999))
        self.assertTrue(restarted.ready(206))

    def test_disabled_and_invalid_settings(self):
        disabled = recorder.Cooldown(0, self.path)
        disabled.saved()
        self.assertTrue(disabled.ready(0))
        for value in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                recorder.Cooldown(value, self.path)


if __name__ == '__main__':
    unittest.main()
