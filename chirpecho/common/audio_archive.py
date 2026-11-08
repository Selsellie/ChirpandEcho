"""Persistent recordings, reclaimed oldest first when disk space runs low."""
import logging
import os
from pathlib import Path
import shutil
import uuid

log = logging.getLogger(__name__)


def prune_audio(directory, now=None):
    """Keep recordings indefinitely; reclaim oldest WAVs under disk pressure."""
    from chirpecho.common.storage import pressure

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if not pressure(directory):
        return
    files = []
    for path in directory.glob('*.wav'):
        try:
            files.append((path.stat().st_mtime, path))
        except FileNotFoundError:
            continue
    for _, path in sorted(files):
        if not pressure(directory, target=True):
            break
        path.unlink(missing_ok=True)


def retain_detection_audio(source, directory, filename=None):
    """Keep one atomic copy per source recording, returning its path or None."""
    source = Path(source)
    filename = filename or source.name.removesuffix('.processing')
    directory = Path(directory)
    try:
        prune_audio(directory)
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
        log.exception('Could not retain detection audio')
        return None
