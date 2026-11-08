"""Compact display spectra, with verified, restart-safe migration of old PNGs.

The historical SQLite column is still named png_path for compatibility. It can
now point to a .spec file: gzip JSON plus an 8-bit, high-frequency-first matrix.
Scientific dependencies are loaded only by writers, never by the web server.
"""
import base64
import datetime as dt
import re
import gzip
import hashlib
import json
import logging
import os
import zlib
from pathlib import Path

log = logging.getLogger('spectrograms')
MAX_ROWS = 160
MAX_COLUMNS = 384


def sync_directory(path):
    descriptor = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_spectrum(path):
    with gzip.open(path, 'rb') as stream:
        payload = json.loads(stream.read(512 * 1024))
    raw = base64.b64decode(payload['data'], validate=True)
    if (payload.get('version') != 1 or not 1 <= payload['width'] <= MAX_COLUMNS
            or not 1 <= payload['height'] <= MAX_ROWS
            or len(raw) != payload['width'] * payload['height']
            or hashlib.sha256(raw).hexdigest() != payload['sha256']):
        raise ValueError('Invalid spectrogram matrix')
    return payload


def write_spectrum(path, matrix, **metadata):
    """Validate the replacement on disk before making it visible."""
    path = Path(path)
    raw = matrix.astype('uint8').tobytes()
    payload = dict(metadata, version=1, width=int(matrix.shape[1]), height=int(matrix.shape[0]),
                   encoding='base64-u8', data=base64.b64encode(raw).decode('ascii'),
                   sha256=hashlib.sha256(raw).hexdigest())
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        with temporary.open('wb') as stream:
            stream.write(gzip.compress(json.dumps(payload, separators=(',', ':'), allow_nan=False).encode(), compresslevel=6, mtime=0))
            stream.flush()
            os.fsync(stream.fileno())
        read_spectrum(temporary)
        temporary.replace(path)
        sync_directory(path)
    finally:
        temporary.unlink(missing_ok=True)
    return payload


def reduce_matrix(matrix):
    """Peak-pool oversized dimensions to keep short, narrow calls visible."""
    import numpy as np
    for axis, limit in [(0, MAX_ROWS), (1, MAX_COLUMNS)]:
        if matrix.shape[axis] > limit:
            edges = np.linspace(0, matrix.shape[axis], limit + 1).astype(int)
            matrix = np.maximum.reduceat(matrix, edges[:-1], axis=axis)
    return matrix


def save_audio_spectrum(audio, sample_rate, path, start_time, end_time, max_frequency_hz, window_start_at=None):
    import numpy as np
    from scipy import signal
    frequencies, _, power = signal.spectrogram(
        audio, fs=sample_rate, nperseg=min(512, len(audio)),
        noverlap=min(256, len(audio) // 2), scaling='spectrum')
    upper = min(float(max_frequency_hz), sample_rate / 2)
    selected = frequencies <= upper
    db = 10 * np.log10(power[selected] + 1e-12)
    ceiling = float(db.max())
    floor = min(ceiling - 1, max(float(db.min()), ceiling - 80))
    matrix = np.rint(np.clip((db - floor) / (ceiling - floor), 0, 1) * 255).astype('uint8')
    matrix = reduce_matrix(matrix)[::-1]
    return write_spectrum(path, matrix, source='audio', duration_seconds=len(audio) / sample_rate,
                          frequency_min_hz=float(frequencies[selected][0]), frequency_max_hz=float(frequencies[selected][-1]),
                          db_min=floor, db_max=ceiling,
                          highlight=[max(0, start_time), min(len(audio) / sample_rate, end_time)],
                          window_start_at=window_start_at)


def convert_png(source, destination):
    """Recover display intensity from the old magma-colour plot, not raw power.

    Axis ranges were never archived numerically. Legacy files therefore use
    relative time/frequency axes rather than claiming reconstructed measurements.
    """
    import numpy as np
    from PIL import Image
    from matplotlib import colormaps
    from scipy.spatial import cKDTree
    source = Path(source)
    with Image.open(source) as image:
        rgb = np.asarray(image.convert('RGB'))
    # The chart is coloured; its surrounding axes, text and margins are grey.
    spread = np.ptp(rgb.astype('int16'), axis=2)
    ys, xs = np.where(spread > 16)
    if not len(xs):
        raise ValueError('No coloured spectrogram plot found')
    left, right, top, bottom = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    if right-left < 32 or bottom-top < 16 or (right-left)*(bottom-top) < rgb.shape[0]*rgb.shape[1]*.2:
        raise ValueError('Spectrogram plot bounds could not be verified')
    plot = rgb[top:bottom, left:right]
    palette = (colormaps['magma'](np.linspace(0, 1, 256))[:, :3] * 255).round()
    _, indices = cKDTree(palette).query(plot.reshape(-1, 3).astype(float))
    matrix = reduce_matrix(indices.reshape(plot.shape[:2]).astype('uint8'))
    return write_spectrum(destination, matrix, source='legacy_png', duration_seconds=None,
                          frequency_min_hz=None, frequency_max_hz=None, db_min=None, db_max=None,
                          highlight=None, original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                          original_size_bytes=source.stat().st_size)


def migrate_legacy(conn, directory, limit=2):
    """Convert a bounded batch; commit the new path before deleting any PNG.

    Call under the detector's existing inbox lock. Unreadable or uncertain PNGs
    remain usable through the legacy route; a failed conversion never deletes one.
    """
    directory = Path(directory).resolve()
    # Only legacy PNGs need migration work. The filename is the detection ID,
    # allowing an indexed lookup without scanning every modern spectrum row.
    rows = []
    for png in directory.glob('*.png'):
        if len(rows) >= limit:
            break
        row = conn.execute('SELECT d.id, d.png_path FROM detections d '
                           'LEFT JOIN image_archive a ON a.detection_id=d.id '
                           'LEFT JOIN image_cleanup_queue q ON q.detection_id=d.id '
                           'WHERE d.id=? AND a.detection_id IS NULL AND q.detection_id IS NULL',
                           (png.stem,)).fetchone()
        if row and Path(row[1]).resolve() in (png.resolve(), png.with_suffix('.spec').resolve()):
            rows.append(row)
    converted = saved = attempted = 0
    for ident, filename in rows:
        stored = Path(filename).resolve()
        if stored.parent != directory:
            continue
        png = stored.with_suffix('.png')
        spec = stored.with_suffix('.spec')
        if not png.is_file():
            continue
        if attempted >= limit:
            break
        attempted += 1
        try:
            original_digest = hashlib.sha256(png.read_bytes()).hexdigest()
            if spec.is_file():
                payload = read_spectrum(spec)
                if payload.get('original_sha256') != original_digest:
                    raise ValueError('Existing spectrum does not match the PNG')
            else:
                payload = convert_png(png, spec)
            # A larger replacement is no space-saving migration; keep the PNG.
            if spec.stat().st_size >= png.stat().st_size:
                if stored.suffix == '.png':
                    spec.unlink()
                continue
            sync_directory(spec)
            if stored.suffix == '.png':
                updated = conn.execute('UPDATE detections SET png_path=? WHERE id=? AND png_path=?',
                                       (str(spec), ident, filename)).rowcount
                if updated != 1:
                    raise ValueError('Detection changed during migration')
                conn.commit()
            # Re-read after the committed pointer change. A crash before unlink
            # leaves both files; the next scan resumes here and verifies the pair.
            verified = read_spectrum(spec)
            if verified.get('original_sha256') != hashlib.sha256(png.read_bytes()).hexdigest():
                raise ValueError('PNG changed during migration')
            difference = png.stat().st_size - spec.stat().st_size
            png.unlink()
            saved += difference
            converted += 1
        except (OSError, ValueError, KeyError, TypeError, EOFError, zlib.error):
            conn.rollback()
            log.warning('PNG conversion deferred for %s; original retained', ident)
    if converted:
        log.info('Converted %d PNGs to compact spectra; saved %d bytes', converted, saved)
    return converted, saved


def restore_legacy_axes(conn, directory, engine):
    """Restore known BirdNET window geometry from saved source timestamps.

    Only accept standard timestamped captures and the configured three-second
    analysis-window positions. Intensity remains explicitly image-derived.
    """
    if engine != 'bird':
        return 0
    import numpy as np
    directory = Path(directory).resolve()
    chunk = float(os.environ.get('CHUNK_SECONDS', '5'))
    padding = float(os.environ.get('SPECTROGRAM_PADDING_SECONDS', '.5'))
    if chunk < 3 or padding < 0:
        return 0
    positions = list(range(0, int(chunk - 3) + 1, 3))
    if abs(positions[-1] + 3 - chunk) > .001:
        positions.append(chunk - 3)
    restored = 0
    rows = conn.execute("SELECT png_path, source_file, detected_at, low_freq_hz, high_freq_hz FROM detections WHERE png_path LIKE '%.spec'")
    for filename, source, detected, low, high in rows:
        path = Path(filename).resolve()
        if path.parent != directory or not path.is_file() or (low, high) != (0, 15000):
            continue
        data = read_spectrum(path)
        if data['source'] != 'legacy_png' or data['duration_seconds'] is not None:
            continue
        stamp = re.match(r'^(\d{8}T\d{12}Z)_', source)
        if not stamp:
            continue
        started = dt.datetime.strptime(stamp[1], '%Y%m%dT%H%M%S%fZ').replace(tzinfo=dt.timezone.utc)
        offset = (dt.datetime.fromisoformat(detected) - started).total_seconds()
        if not any(abs(offset - position) < .001 for position in positions):
            continue
        begin = max(0, offset - padding)
        end = min(chunk, offset + 3 + padding)
        metadata = {key:value for key,value in data.items() if key not in ('version','width','height','encoding','data','sha256')}
        metadata.update(duration_seconds=end-begin, frequency_min_hz=0,
                        frequency_max_hz=min(24000, float(os.environ.get('SPECTROGRAM_MAX_HZ','15000'))),
                        window_start_at=(started+dt.timedelta(seconds=begin)).isoformat(),
                        highlight=[offset-begin, offset+3-begin], axis_provenance='recording_settings')
        matrix = np.frombuffer(base64.b64decode(data['data']), dtype='uint8').reshape(data['height'], data['width'])
        write_spectrum(path, matrix, **metadata)
        restored += 1
    if restored:
        log.info('Restored physical axes for %d legacy BirdNET spectra from recording settings', restored)
    return restored
