"""Bounded, short-lived copies of recordings that produced detections."""
import logging
import os
from pathlib import Path
import shutil
import time
import uuid

log = logging.getLogger(__name__)


def prune_audio(directory, now=None):
    """Expire recordings after 24 hours and enforce a per-pipeline size cap."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    now = time.time() if now is None else now
    ttl = max(0, int(os.environ.get('AUDIO_ARCHIVE_TTL_SECONDS', '86400')))
    limit = max(0, int(os.environ.get('AUDIO_ARCHIVE_MAX_MB', '512'))) * 1024 * 1024
    files = []
    for path in directory.glob('*.wav'):
        try:
            stat = path.stat()
            if now - stat.st_mtime >= ttl:
                path.unlink(missing_ok=True)
            else:
                files.append((stat.st_mtime, path, stat.st_size))
        except FileNotFoundError:
            continue
    total = sum(size for _, _, size in files)
    for _, path, size in sorted(files):
        if total <= limit:
            break
        path.unlink(missing_ok=True)
        total -= size


def retain_detection_audio(source, directory, filename=None):
    """Keep one atomic copy per source recording, returning its path or None."""
    source = Path(source)
    filename = filename or source.name.removesuffix('.processing')
    directory = Path(directory)
    try:
        prune_audio(directory)
        size = source.stat().st_size
        limit = max(0, int(os.environ.get('AUDIO_ARCHIVE_MAX_MB', '512'))) * 1024 * 1024
        if size > limit:
            log.warning('Recording exceeds the short-term audio archive limit; not retained')
            return None
        existing = directory / Path(filename).name
        if existing.is_file():
            return existing
        temporary = directory / ('.' + existing.name + '.' + uuid.uuid4().hex + '.tmp')
        try:
            shutil.copyfile(source, temporary)
            os.replace(temporary, existing)
        finally:
            temporary.unlink(missing_ok=True)
        prune_audio(directory)
        return existing if existing.is_file() else None
    except OSError:
        log.exception('Could not retain detection audio for 24 hours')
        return None
