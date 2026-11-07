"""Echo's ultrasonic activity gate, bounded WAV writes, and recording cooldown."""
import datetime as dt
import logging
import math
import os
from pathlib import Path
import time
import uuid
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt
from chirpecho.common.runtime import DEFAULT_AUDIO_DIR, storage_available

log = logging.getLogger('recorder')
SAMPLE_RATE = int(os.environ.get('SAMPLE_RATE', '384000'))
CHUNK_SECONDS = float(os.environ.get('CHUNK_SECONDS', '5'))
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', str(DEFAULT_AUDIO_DIR))
GATE_LOW_HZ = float(os.environ.get('GATE_LOW_HZ', '15000'))
GATE_HIGH_HZ = float(os.environ.get('GATE_HIGH_HZ', '100000'))
GATE_RMS_THRESHOLD = float(os.environ.get('GATE_RMS_THRESHOLD', '0.01'))


class Cooldown:
    """Limit saved recordings, including across recorder restarts."""
    def __init__(self, seconds, state_path):
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError('COOLDOWN_SECONDS must be finite and nonnegative')
        self.seconds = seconds
        self.path = Path(state_path)
        self.until = 0
        try:
            saved = float(self.path.read_text())
            if not math.isfinite(saved):
                raise ValueError('invalid cooldown timestamp')
            remaining = max(0, min(seconds, saved + seconds - time.time()))
            self.until = time.monotonic() + remaining
        except FileNotFoundError:
            pass
        except ValueError:
            # A damaged state file should not disable rate limiting on restart.
            self.until = time.monotonic() + seconds
            log.warning('Invalid cooldown state; waiting one cooldown interval')

    def ready(self, captured_at):
        return self.seconds == 0 or captured_at >= self.until

    def saved(self):
        self.until = time.monotonic() + self.seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + '.tmp')
        temporary.write_text(str(time.time()))
        temporary.replace(self.path)
        log.info('Recording saved; cooldown for %.0f seconds', self.seconds)


def build_filter():
    if SAMPLE_RATE <= 0 or CHUNK_SECONDS <= 0:
        raise ValueError('SAMPLE_RATE and CHUNK_SECONDS must be positive')
    if not 0 < GATE_LOW_HZ < GATE_HIGH_HZ < SAMPLE_RATE / 2:
        raise ValueError('Gate frequencies must satisfy 0 < low < high < Nyquist')
    if not np.isfinite(GATE_RMS_THRESHOLD) or GATE_RMS_THRESHOLD < 0:
        raise ValueError('GATE_RMS_THRESHOLD must be finite and nonnegative')
    return butter(4, [GATE_LOW_HZ, GATE_HIGH_HZ], fs=SAMPLE_RATE,
                  btype='bandpass', output='sos')


def is_active(chunk, sos):
    filtered = sosfiltfilt(sos, chunk, axis=0)
    # Peak 20 ms RMS over 10 ms hops preserves brief calls within a 5 s chunk.
    power = np.square(filtered.reshape(-1))
    hop = max(1, int(SAMPLE_RATE * .01))
    count = len(power) // hop
    if count >= 2:
        bins = power[:count * hop].reshape(count, hop).mean(axis=1)
        peak = float(np.max((bins[:-1] + bins[1:]) / 2))
        if len(power) % hop:
            peak = max(peak, float(power[count * hop:].mean()))
    else:
        peak = float(power.mean())
    rms = float(np.sqrt(peak))
    log.debug('peak 20 ms gate RMS = %.5f', rms)
    return rms >= GATE_RMS_THRESHOLD


def write_chunk(chunk, started_at):
    if not storage_available(OUTPUT_DIR, chunk.size * 2 + 4096):
        log.warning('Audio storage limit reached; dropping new chunk, preserving pending files')
        return False
    directory = Path(OUTPUT_DIR)
    name = started_at.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    final = directory / f'{name}_{uuid.uuid4().hex[:8]}.wav'
    temporary = final.with_name('.' + final.name + '.tmp')
    try:
        sf.write(temporary, chunk, SAMPLE_RATE, subtype='PCM_16', format='WAV')
        temporary.replace(final)
    finally:
        temporary.unlink(missing_ok=True)
    log.info('wrote %s', final.name)
    return True


def process_chunk(chunk, started_at, captured_at, sos, cooldown):
    if not cooldown.ready(captured_at):
        return 'cooldown'
    if is_active(chunk, sos) and write_chunk(chunk, started_at):
        cooldown.saved()
        return 'saved'
    return 'discarded'

