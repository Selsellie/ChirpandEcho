"""Shared logging and disk limits for the Pi services."""
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil
import json
import time

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIO_DIR = Path('/dev/shm') / f'chirp-echo-{os.getuid()}' / 'incoming'
STATUS_DIR = Path(os.environ.get('STATUS_DIR', ROOT / 'data/status'))


def write_status(component, **details):
    directory = Path(os.environ.get('STATUS_DIR', STATUS_DIR))
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{component}.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(dict(updated_at=time.time(), **details)))
    temporary.replace(path)


def configure_logging(name):
    directory = Path(os.environ.get('LOG_DIR', ROOT / 'logs'))
    directory.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handlers = [logging.StreamHandler(), RotatingFileHandler(
        directory / f'{name}.log', maxBytes=5 * 1024 * 1024, backupCount=3)]
    for handler in handlers:
        handler.setFormatter(formatter)
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'), handlers=handlers, force=True)
    return logging.getLogger(name)


def storage_available(incoming, required_bytes=0):
    """Stop accepting new audio rather than deleting unprocessed recordings."""
    directory = Path(incoming)
    directory.mkdir(parents=True, exist_ok=True)
    reserve = int(os.environ.get('MIN_FREE_MB', '1024')) * 1024 * 1024
    limit = int(os.environ.get('MAX_AUDIO_MB', '512')) * 1024 * 1024
    used = 0
    for path in directory.rglob('*'):
        try:
            if path.is_file() and ('.wav' in path.name or path.name.endswith('.tmp')):
                used += path.stat().st_size
        except FileNotFoundError:
            pass  # The detector may have just consumed a file.
    persistent = Path(os.environ.get('DB_PATH', ROOT / 'data/db/detections.sqlite3')).parent
    persistent.mkdir(parents=True, exist_ok=True)
    return (shutil.disk_usage(persistent).free >= reserve
            and shutil.disk_usage(directory).free - required_bytes >= 8 * 1024 ** 2
            and used + required_bytes <= limit)
