"""Reclaim PNG files while retaining every detection row and a durable audit trail."""
import datetime as dt
import logging
import os
from pathlib import Path
import shutil

log = logging.getLogger('storage')


def init_archive_schema(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS image_archive '
                 '(detection_id TEXT PRIMARY KEY, removed_at TEXT NOT NULL, reason TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS image_cleanup_queue '
                 '(detection_id TEXT PRIMARY KEY, png_path TEXT NOT NULL, reason TEXT NOT NULL)')
    conn.commit()


def pressure(directory, target=False):
    disk = shutil.disk_usage(directory)
    high = float(os.environ.get('STORAGE_HIGH_WATER_PERCENT', '85'))
    low = float(os.environ.get('STORAGE_LOW_WATER_PERCENT', '80'))
    if not 0 < low < high < 100:
        raise ValueError('Storage watermarks must satisfy 0 < low < high < 100')
    minimum = int(os.environ.get('MIN_FREE_MB', '1024')) * 1024 ** 2
    limit = low if target else high
    return disk.used / disk.total * 100 >= limit or disk.free < minimum


def queue_image(conn, row, reason):
    conn.execute('INSERT OR IGNORE INTO image_cleanup_queue VALUES (?, ?, ?)',
                 (row[0], row[1], reason))
    conn.commit()


def drain_queue(conn, directory):
    directory = Path(directory).resolve()
    count = 0
    for ident, filename, reason in conn.execute('SELECT * FROM image_cleanup_queue').fetchall():
        path = Path(filename).resolve()
        if path.parent != directory:
            log.error('Refusing image cleanup outside %s: %s', directory, path)
            continue
        try:
            path.unlink(missing_ok=True)
        except OSError:
            log.exception('Image cleanup will retry: %s', path)
            continue
        conn.execute('INSERT OR REPLACE INTO image_archive VALUES (?, ?, ?)',
                     (ident, dt.datetime.now(dt.timezone.utc).isoformat(), reason))
        conn.execute('DELETE FROM image_cleanup_queue WHERE detection_id=?', (ident,))
        conn.commit()
        count += 1
    return count


def manage_archive(conn, directory):
    """Retry journaled deletions, optional image expiry, then oldest-first pressure cleanup."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    removed = drain_queue(conn, directory)
    days = int(os.environ.get('RETENTION_DAYS', '0'))
    if days > 0:
        rows = conn.execute("SELECT d.id, d.png_path FROM detections d LEFT JOIN image_archive a "
                            "ON a.detection_id=d.id WHERE a.detection_id IS NULL AND "
                            "julianday(d.detected_at)<julianday('now', ?) LIMIT 100",
                            (f'-{days} days',)).fetchall()
        for row in rows:
            queue_image(conn, row, 'age')
        removed += drain_queue(conn, directory)
    if pressure(directory):
        # Batch selection bounds memory. Stop when no more deletions can make progress.
        while pressure(directory, target=True):
            rows = conn.execute('SELECT d.id,d.png_path FROM detections d '
                                'LEFT JOIN image_archive a ON a.detection_id=d.id '
                                'LEFT JOIN image_cleanup_queue q ON q.detection_id=d.id '
                                'WHERE a.detection_id IS NULL AND q.detection_id IS NULL '
                                'ORDER BY julianday(d.detected_at), d.id LIMIT 100').fetchall()
            if not rows:
                log.warning('Disk pressure remains; all detection metadata is preserved')
                break
            for row in rows:
                if not pressure(directory, target=True):
                    break
                queue_image(conn, row, 'disk pressure')
                removed += drain_queue(conn, directory)
    if removed:
        log.info('Reclaimed %d PNGs; detection metadata retained', removed)
    return removed
