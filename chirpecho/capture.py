#!/usr/bin/env python3
"""One microphone capture feeding independent Chirp and Echo audio queues."""
import datetime as dt
import os
from pathlib import Path
import queue
import signal
import threading
import time

from chirpecho.common.runtime import ROOT, configure_logging, write_status
from chirpecho.echo.gate import CHUNK_SECONDS, SAMPLE_RATE, Cooldown, build_filter, process_chunk
import numpy as np
import sounddevice as sd

log = configure_logging('recorder')


def _parse_device(raw):
    if not raw:
        return None
    return int(raw) if raw.strip().lstrip('-').isdigit() else raw


DEVICE = _parse_device(os.environ.get('DEVICE', 'Vleermic'))


def capture(chunks, stop, frames):
    """Keep reading while the main thread filters and writes previous chunks."""
    while not stop.is_set():
        try:
            sd.check_input_settings(device=DEVICE, channels=1, dtype='float32',
                                    samplerate=SAMPLE_RATE)
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                                device=DEVICE, blocksize=4096, latency=0.2) as stream:
                log.info('microphone opened: %r at %d Hz', DEVICE, SAMPLE_RATE)
                assembled = np.empty((frames, 1), dtype=np.float32)
                offset = 0
                while not stop.is_set():
                    count = min(4096, frames - offset)
                    block, overflowed = stream.read(count)
                    if overflowed:
                        log.warning('Microphone overflow; dropping discontinuous chunk')
                        offset = 0
                        continue
                    if offset == 0:
                        # Estimate capture start, accounting for unread buffered frames.
                        started_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(
                            seconds=(count + stream.read_available) / SAMPLE_RATE)
                        captured_at = time.monotonic() - (count + stream.read_available) / SAMPLE_RATE
                    assembled[offset:offset + count] = block
                    offset += count
                    if offset < frames:
                        continue
                    try:
                        chunks.put_nowait((assembled, started_at, captured_at))
                    except queue.Full:
                        log.warning('Processing queue full; dropping newest chunk')
                    assembled = np.empty((frames, 1), dtype=np.float32)
                    offset = 0
        except Exception:
            log.exception('Microphone unavailable; retrying in 5 seconds')
            stop.wait(5)


def main():
    sos = build_filter()
    cooldown = Cooldown(float(os.environ.get('COOLDOWN_SECONDS', '10')),
                        Path(os.environ.get('COOLDOWN_STATE', str(ROOT / 'data/.cooldown'))))
    frames = int(SAMPLE_RATE * CHUNK_SECONDS)
    if frames < 32:
        raise ValueError('Chunk must contain at least 32 frames')
    capacity = int(os.environ.get('CAPTURE_QUEUE_CHUNKS', '3'))
    if not 1 <= capacity <= 16:
        raise ValueError('CAPTURE_QUEUE_CHUNKS must be between 1 and 16')
    chunks = queue.Queue(maxsize=capacity)
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    worker = threading.Thread(target=capture, args=(chunks, stop, frames), daemon=True)
    worker.start()
    bird_capture = None
    if os.environ.get('BIRD_ENABLED', '0') == '1':
        from chirpecho.chirp.audio import BirdCapture
        bird_capture = BirdCapture(SAMPLE_RATE)
    checked = retained = skipped = 0
    next_report = time.monotonic() + 60
    try:
        while not stop.is_set():
            try:
                chunk, started_at, captured_at = chunks.get(timeout=0.5)
            except queue.Empty:
                continue
            # Feed Chirp before Echo's gate/cooldown, while keeping microphone ownership singular.
            if bird_capture is not None:
                try:
                    bird_capture.process(chunk, started_at)
                except Exception:
                    log.exception('Chirp capture failed; Echo capture continues')
                    write_status('chirp_recorder', state='error')
            result = process_chunk(chunk, started_at, captured_at, sos, cooldown)
            if result == 'cooldown':
                skipped += 1
            elif result == 'saved':
                retained += 1
            checked += 1
            write_status('recorder', state='listening', retained=retained,
                         cooldown_seconds=cooldown.seconds, cooldown_skips=skipped,
                         sample_rate=SAMPLE_RATE, device=DEVICE)
            if time.monotonic() >= next_report:
                log.info('capture healthy: %d chunks checked, %d retained, %d cooldown skips in last minute',
                         checked, retained, skipped)
                checked = retained = skipped = 0
                next_report = time.monotonic() + 60
    finally:
        stop.set()
        worker.join(timeout=CHUNK_SECONDS + 2)


if __name__ == '__main__':
    main()
