#!/usr/bin/env python3
"""
Shared archive worker for Echo (BatDetect2) and Chirp (BirdNET).

Can be run once as a scheduled task or continuously with ``--watch``. Each scan:
  1. Scans INCOMING_DIR for finished WAV chunks (written atomically by the
     recorder, so any .wav file found here is complete).
  2. Runs BatDetect2 on each one.
  3. For every detection above CONFIDENCE_THRESHOLD: generates a small
     compact spectrogram of just that call (with padding) and writes a row to
     SQLite (timestamp, species, confidence, frequency range, png path).
  4. Deletes the original WAV after successful processing. Failed files are
     restored for a later retry.

Environment variables:
    INCOMING_DIR       - where the recorder drops WAV chunks (default <project>/data/incoming)
    DETECTIONS_DIR      - where compact spectrograms are written (default <project>/data/detections)
    DB_PATH             - SQLite database file (default <project>/data/db/detections.sqlite3)
    CONFIDENCE_THRESHOLD- minimum class_prob to keep a detection (default 0.5)
    SPECTROGRAM_PADDING_SECONDS - padding around each call for the spectrogram (default 0.5)
    SCAN_INTERVAL_SECONDS - delay between scans in watch mode (default 10)
    LOG_LEVEL           - default INFO
"""

import os
import sys
import glob
import argparse
import uuid
import sqlite3
import logging
import datetime as dt
import re
import signal as os_signal
import time
import hashlib
import fcntl
import shutil
from pathlib import Path

from chirpecho.common.runtime import ROOT, DEFAULT_AUDIO_DIR, configure_logging, write_status as publish_status
from chirpecho.common.storage import init_archive_schema, manage_archive
from chirpecho.common.notifications import init_notifications, queue_discovery, deliver_pending
from chirpecho.common.spectrograms import save_audio_spectrum, migrate_legacy, restore_legacy_axes
from chirpecho.common.audio_archive import retain_detection_audio, prune_audio

# Set limits before importing numerical libraries and PyTorch.
os.environ.setdefault('OMP_NUM_THREADS', os.environ.get('DETECTOR_THREADS', '2'))
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')

import numpy as np
import soundfile as sf

ENGINE = os.environ.get('DETECTOR_ENGINE', 'bat')
COMPONENT = 'chirp_detector' if ENGINE == 'bird' else 'detector'
if ENGINE == 'bird':
    from chirpecho.chirp.model import BirdAPI
    model_api = None
elif ENGINE == 'bat':
    from chirpecho.echo import model as model_api
else:
    raise ValueError('DETECTOR_ENGINE must be bat or bird')


def write_status(component, **details):
    publish_status(COMPONENT, **details)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_DIR = str(ROOT)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
INCOMING_DIR = os.environ.get("INCOMING_DIR", str(DEFAULT_AUDIO_DIR))
DETECTIONS_DIR = os.environ.get("DETECTIONS_DIR", os.path.join(DATA_DIR, "detections"))
AUDIO_ARCHIVE_DIR = os.environ.get('AUDIO_ARCHIVE_DIR', os.path.join(DETECTIONS_DIR, 'audio'))
DB_PATH = os.environ.get("DB_PATH", os.path.join(DATA_DIR, "db", "detections.sqlite3"))
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))
DETECTION_THRESHOLD = float(os.environ.get('DETECTION_THRESHOLD', '0.3'))
SPECTROGRAM_PADDING_SECONDS = float(os.environ.get("SPECTROGRAM_PADDING_SECONDS", "0.5"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
SCAN_INTERVAL_SECONDS = float(os.environ.get("SCAN_INTERVAL_SECONDS", "10"))

log = configure_logging(COMPONENT)

# Recorder writes files named like: 20260716T214752_c319cfb3.wav
_FILENAME_TS_RE = re.compile(r"^(\d{8}T\d{6})_")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def init_db():
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS detections (
            id TEXT PRIMARY KEY,
            detected_at TEXT NOT NULL,       -- absolute ISO8601 timestamp of the call
            species TEXT NOT NULL,
            confidence REAL NOT NULL,        -- class_prob
            det_prob REAL NOT NULL,          -- probability it's a call at all
            low_freq_hz INTEGER NOT NULL,
            high_freq_hz INTEGER NOT NULL,
            png_path TEXT NOT NULL,
            source_file TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_detections_detected_at "
        "ON detections(detected_at DESC)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_detections_species "
        "ON detections(species)"
    )
    conn.execute('CREATE TABLE IF NOT EXISTS processed_files '
                 '(source_file TEXT PRIMARY KEY, processed_at TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS failed_files '
                 '(source_file TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
    conn.commit()
    init_archive_schema(conn)
    init_notifications(conn, ENGINE)
    return conn


def insert_detection(conn, row: dict):
    conn.execute(
        """
        INSERT INTO detections
            (id, detected_at, species, confidence, det_prob,
             low_freq_hz, high_freq_hz, png_path, source_file, created_at)
        VALUES
            (:id, :detected_at, :species, :confidence, :det_prob,
             :low_freq_hz, :high_freq_hz, :png_path, :source_file, :created_at)
        """,
        row,
    )
    queue_discovery(conn, row, ENGINE)


# ---------------------------------------------------------------------------
# Timestamp handling
# ---------------------------------------------------------------------------

def chunk_start_time(filepath: str) -> dt.datetime:
    """Parse the recording start time from the filename. Falls back to the
    file's mtime if the name doesn't match the expected pattern (e.g. a
    manually-created test file)."""
    basename = os.path.basename(filepath)
    modern = re.match(r'^(\d{8}T\d{12}Z)_', basename)
    if modern:
        return dt.datetime.strptime(modern.group(1), '%Y%m%dT%H%M%S%fZ').replace(
            tzinfo=dt.timezone.utc)
    m = _FILENAME_TS_RE.match(basename)
    if m:
        return dt.datetime.strptime(m.group(1), "%Y%m%dT%H%M%S").astimezone()
    log.warning("filename %s doesn't match expected pattern, using file mtime", basename)
    return dt.datetime.fromtimestamp(os.path.getmtime(filepath)).astimezone()


# ---------------------------------------------------------------------------
# Spectrogram generation
# ---------------------------------------------------------------------------

def save_spectrogram_data(audio, fs, out_path, start_time, end_time, window_start_at=None):
    return save_audio_spectrum(audio, fs, out_path, start_time, end_time,
                               float(os.environ.get('SPECTROGRAM_MAX_HZ', '120000')), window_start_at)


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

def process_file(filepath: str, conn: sqlite3.Connection) -> bool:
    """Process one claimed WAV file.

    Return True only when processing completed and the source audio may be
    deleted. A False result lets the caller restore the file for a later retry.
    """
    log.info("processing %s", filepath)
    source_file = os.path.basename(filepath).removesuffix('.processing')
    if conn.execute('SELECT 1 FROM processed_files WHERE source_file=?',
                    (source_file,)).fetchone():
        Path(filepath).unlink(missing_ok=True)
        return True
    # Pause before generating spectrograms when the disk reserve is exhausted.
    if shutil.disk_usage(DETECTIONS_DIR).free < int(os.environ.get('MIN_FREE_MB', '1024')) * 1024 ** 2:
        raise OSError('Disk reserve reached; detector paused')
    started = time.monotonic()
    write_status('detector', state='processing', source_file=source_file)

    try:
        result = model_api.process_file(filepath, config=model_api.get_config(
            detection_threshold=DETECTION_THRESHOLD))
    except Exception as e:
        log.exception("Classification failed on %s: %s", filepath, e)
        return False

    if not isinstance(result, dict):
        log.error("Classifier returned an unexpected result for %s", filepath)
        return False
    annotations = result.get("pred_dict", {}).get("annotation", []) or []
    kept = [
        annotation for annotation in annotations
        if float(annotation.get("class_prob") or 0.0) >= CONFIDENCE_THRESHOLD
    ]

    log.info(
        "%s: %d raw detections, %d above confidence threshold (%.2f)",
        os.path.basename(filepath), len(annotations), len(kept), CONFIDENCE_THRESHOLD,
    )

    if kept:
        chunk_start = chunk_start_time(filepath)
        try:
            audio, fs = sf.read(filepath, dtype="float32", always_2d=False)
        except Exception as e:
            log.error("failed to read %s: %s", filepath, e)
            return False

        # Unexpected multi-channel input is mixed down so scipy receives a
        # one-dimensional signal and spectrogram slicing stays predictable.
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        duration = len(audio) / fs

        os.makedirs(DETECTIONS_DIR, exist_ok=True)

        created_spectra = []
        saved_detection = False
        try:
            for ann in kept:
                call_start = max(0.0, float(ann["start_time"]))
                call_end = min(duration, float(ann["end_time"]))
                if call_end <= call_start:
                    log.warning("ignoring invalid detection interval %r", ann)
                    continue

                seg_start = max(0.0, call_start - SPECTROGRAM_PADDING_SECONDS)
                seg_end = min(duration, call_end + SPECTROGRAM_PADDING_SECONDS)
                i0, i1 = int(seg_start * fs), int(seg_end * fs)
                segment = audio[i0:i1]
                if segment.size < 2:
                    log.warning("ignoring empty detection interval %r", ann)
                    continue

                # Stable IDs make an interrupted transaction safe to replay.
                detection_id = hashlib.sha256(
                    f'{source_file}:{ann["start_time"]}:{ann["end_time"]}:{ann.get("class")}'.encode()
                ).hexdigest()[:32]
                png_path = os.path.join(DETECTIONS_DIR, f"{detection_id}.spec")

                created_spectra.append(png_path)
                save_spectrogram_data(
                    segment, fs, png_path,
                    start_time=call_start - seg_start,
                    end_time=call_end - seg_start,
                    window_start_at=(chunk_start + dt.timedelta(seconds=seg_start)).isoformat(),
                )

                detected_at = chunk_start + dt.timedelta(seconds=call_start)

                insert_detection(conn, {
                    "id": detection_id,
                    "detected_at": detected_at.isoformat(),
                    "species": ann.get("class") or "unknown",
                    "confidence": float(ann.get("class_prob", 0.0)),
                    "det_prob": float(ann.get("det_prob", 0.0)),
                    "low_freq_hz": int(ann.get("low_freq") or 0),
                    "high_freq_hz": int(ann.get("high_freq") or 0),
                    "png_path": png_path,
                    "source_file": os.path.basename(filepath).removesuffix(".processing"),
                    "created_at": dt.datetime.now().astimezone().isoformat(),
                })
                saved_detection = True
                log.info(
                    "  -> detection: %s conf=%.2f at %s",
                    ann.get("class", "unknown"), ann.get("class_prob", 0.0), detected_at.isoformat(),
                )
        except Exception as e:
            conn.rollback()
            for png_path in created_spectra:
                try:
                    os.remove(png_path)
                except OSError:
                    pass
            log.exception("failed to store detections for %s: %s", filepath, e)
            if isinstance(e, OSError):
                raise
            return False

    # Commit the completion marker together with ALL detection rows.
    conn.execute('INSERT INTO processed_files VALUES (?, ?)',
                 (source_file, dt.datetime.now(dt.timezone.utc).isoformat()))
    conn.execute('DELETE FROM failed_files WHERE source_file=?', (source_file,))
    conn.commit()
    log.info('processed %s in %.2fs', source_file, time.monotonic() - started)
    write_status('detector', state='ready', last_processing_seconds=round(time.monotonic() - started, 2))
    # Preserve a detected source recording for review, then remove the RAM copy.
    if kept and saved_detection:
        retain_detection_audio(filepath, AUDIO_ARCHIVE_DIR, source_file)
    try:
        os.remove(filepath)
    except OSError as e:
        log.error("failed to delete %s: %s", filepath, e)
        # The database transaction already committed. Do not restore and
        # classify the audio again, which would create duplicate detections.
        return True
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def scan_once(conn: sqlite3.Connection, stopping=lambda: False):
    """Claim and process every completed WAV currently in the inbox."""
    deliver_pending(conn)
    prune_audio(AUDIO_ARCHIVE_DIR)
    converted, _ = migrate_legacy(conn, DETECTIONS_DIR)
    if converted:
        restore_legacy_axes(conn, DETECTIONS_DIR, ENGINE)
    manage_archive(conn, DETECTIONS_DIR)
    ttl = int(os.environ.get('AUDIO_BUFFER_TTL_SECONDS', '600'))
    for path in Path(INCOMING_DIR).rglob('*'):
        try:
            if path.is_file() and ('.wav' in path.name or path.name.endswith('.tmp')):
                if time.time() - path.stat().st_mtime > ttl:
                    path.unlink(missing_ok=True)
                    log.warning('Discarded expired temporary audio buffer %s', path.name)
        except FileNotFoundError:
            pass
    pending = sorted(glob.glob(os.path.join(INCOMING_DIR, "*.wav")))
    write_status('detector', state='ready', pending=len(pending))
    log.info("found %d pending file(s)", len(pending))

    for filepath in pending:
        if stopping():
            break
        processing_path = filepath + ".processing"
        try:
            os.rename(filepath, processing_path)
        except OSError:
            log.warning("could not claim %s (already being processed?), skipping", filepath)
            continue

        try:
            success = process_file(processing_path, conn)
        except OSError:
            conn.rollback()
            Path(processing_path).replace(filepath)
            log.exception('Storage unavailable; pausing this scan')
            break
        except Exception:
            conn.rollback()
            log.exception('Unexpected processing failure')
            success = False
        if not success:
            conn.execute('INSERT INTO failed_files VALUES (?, 1) ON CONFLICT(source_file) '
                         'DO UPDATE SET attempts=attempts+1', (os.path.basename(filepath),))
            attempts = conn.execute('SELECT attempts FROM failed_files WHERE source_file=?',
                                    (os.path.basename(filepath),)).fetchone()[0]
            conn.commit()
            try:
                if attempts >= int(os.environ.get('MAX_RETRIES', '3')):
                    quarantine = Path(INCOMING_DIR) / 'failed'
                    quarantine.mkdir(exist_ok=True)
                    Path(processing_path).replace(quarantine / Path(filepath).name)
                    log.error('Quarantined %s after %d failures', filepath, attempts)
                    continue
                os.rename(processing_path, filepath)
                log.warning("restored %s for a later retry", filepath)
            except OSError as e:
                log.error("could not restore failed file %s: %s", processing_path, e)


def expire_detections(conn):
    """Compatibility wrapper: retention now removes images, never metadata."""
    return manage_archive(conn, DETECTIONS_DIR)


def recover_interrupted():
    """Caller must hold the inbox lock before restoring unfinished claims."""
    for claimed in Path(INCOMING_DIR).glob('*.wav.processing'):
        original = claimed.with_suffix('')
        if not original.exists():
            claimed.replace(original)
            log.warning('Recovered interrupted file %s', original.name)


def main(argv=None):
    global model_api
    parser = argparse.ArgumentParser(description="Classify completed wildlife recordings")
    parser.add_argument("--watch", action="store_true", help="keep scanning instead of exiting")
    parser.add_argument(
        "--interval", type=float, default=SCAN_INTERVAL_SECONDS,
        help="seconds between scans in watch mode (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    if args.interval <= 0:
        parser.error("--interval must be greater than zero")
    if not 0.0 <= CONFIDENCE_THRESHOLD <= 1.0:
        parser.error("CONFIDENCE_THRESHOLD must be between 0 and 1")
    if not 0.0 <= DETECTION_THRESHOLD <= 1.0:
        parser.error('DETECTION_THRESHOLD must be between 0 and 1')
    if SPECTROGRAM_PADDING_SECONDS < 0:
        parser.error("SPECTROGRAM_PADDING_SECONDS cannot be negative")

    log.info(
        "starting detector run: incoming_dir=%s detections_dir=%s db_path=%s "
        "confidence_threshold=%.2f",
        INCOMING_DIR, DETECTIONS_DIR, DB_PATH, CONFIDENCE_THRESHOLD,
    )

    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(DETECTIONS_DIR, exist_ok=True)
    # A process-wide advisory lock also makes interrupted-file recovery safe.
    lock = open(os.path.join(INCOMING_DIR, '.detector.lock'), 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('Another detector already owns this inbox')
    conn = init_db()
    restore_legacy_axes(conn, DETECTIONS_DIR, ENGINE)
    if ENGINE == 'bird':
        write_status(COMPONENT, state='loading_model')
        model_api = BirdAPI()
        log.info('BirdNET 2.4 ready: %d Western European bird species', len(model_api.allowed))
    recover_interrupted()

    stopping = False
    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True
        log.info("received signal %s; stopping after the current file", signum)

    os_signal.signal(os_signal.SIGTERM, request_stop)
    os_signal.signal(os_signal.SIGINT, request_stop)
    try:
        while not stopping:
            scan_once(conn, lambda: stopping)
            if not args.watch:
                break
            # Short waits make stop.sh responsive without busy-waiting.
            deadline = time.monotonic() + args.interval
            while not stopping and time.monotonic() < deadline:
                time.sleep(max(0, min(0.5, deadline - time.monotonic())))
    finally:
        conn.close()
    log.info("detector run complete")


if __name__ == "__main__":
    sys.exit(main() or 0)
