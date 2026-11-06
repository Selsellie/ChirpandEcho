#!/usr/bin/env python3
"""LAN dashboard for retained metadata and space-managed spectrograms."""
import datetime as dt
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import time
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import ROOT, configure_logging
configure_logging('webapp')
from flask import Flask, abort, jsonify, render_template, request, send_file

DB_PATH = os.environ.get('DB_PATH', str(ROOT / 'data/db/detections.sqlite3'))
DETECTIONS_DIR = os.environ.get('DETECTIONS_DIR', str(ROOT / 'data/detections'))
INCOMING_DIR = os.environ.get('INCOMING_DIR', str(ROOT / 'data/incoming'))
ZONE = ZoneInfo(os.environ.get('TZ', 'Europe/Amsterdam'))
app = Flask(__name__)


def local_time(value):
    try:
        value = dt.datetime.fromisoformat(value)
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZONE)
        return value.astimezone(ZONE)
    except (TypeError, ValueError):
        return None


def query(sql, parameters=()):
    if not Path(DB_PATH).exists():
        return []
    conn = sqlite3.connect(Path(DB_PATH).resolve().as_uri() + '?mode=ro', uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.create_function('local_hour', 1, lambda value: local_time(value).hour if local_time(value) else 0)
    try:
        return [dict(row) for row in conn.execute(sql, parameters).fetchall()]
    except sqlite3.OperationalError as error:
        if 'no such table' in str(error):
            return []
        raise
    finally:
        conn.close()


def image_path(filename):
    if not filename:
        return None
    path = Path(filename).resolve()
    return path if path.parent == Path(DETECTIONS_DIR).resolve() and path.is_file() else None


def pipeline_status(component):
    directory = Path(os.environ.get('STATUS_DIR', ROOT / 'data/status'))
    try:
        data = json.loads((directory / f'{component}.json').read_text())
        data['fresh'] = time.time() - data.get('updated_at', 0) < (30 if component == 'recorder' else 180)
        return data
    except (OSError, ValueError):
        return {'state': 'starting', 'fresh': False}


def storage_status():
    directory = Path(DETECTIONS_DIR)
    while not directory.exists():
        directory = directory.parent
    disk = shutil.disk_usage(directory)
    return dict(used_percent=round(disk.used / disk.total * 100, 1),
                free_gb=round(disk.free / 1024 ** 3, 1),
                high_water=int(os.environ.get('STORAGE_HIGH_WATER_PERCENT', '85')))


@app.template_filter('localdate')
def localdate(value, pattern='%d %b · %H:%M:%S'):
    date = local_time(value)
    return date.strftime(pattern) if date else 'Waiting for activity'


@app.get('/')
def index():
    search = request.args.get('q', '').strip()[:100]
    try:
        minimum = float(request.args.get('confidence', '0'))
        if not math.isfinite(minimum) or not 0 <= minimum <= 1:
            raise ValueError()
        page = max(1, int(request.args.get('page', '1')))
    except ValueError:
        abort(400)
    stats_rows = query('SELECT COUNT(*) AS total, COUNT(DISTINCT species) AS species_count, '
                       'AVG(confidence) AS avg_confidence, MAX(detected_at) AS last_heard, '
                       "SUM(datetime(detected_at)>=datetime('now','-1 day')) AS last_24h FROM detections")
    stats = stats_rows[0] if stats_rows else dict(total=0, species_count=0, avg_confidence=0, last_heard=None, last_24h=0)
    filtered = query('SELECT COUNT(*) AS total FROM detections WHERE species LIKE ? AND confidence>=?',
                     (f'%{search}%', minimum))
    matched = filtered[0]['total'] if filtered else 0
    pages = max(1, math.ceil(matched / 24))
    page = min(page, pages)
    detections = query('SELECT d.*, a.reason AS archive_reason FROM detections d '
                       'LEFT JOIN image_archive a ON a.detection_id=d.id '
                       'WHERE d.species LIKE ? AND d.confidence>=? '
                       'ORDER BY d.detected_at DESC LIMIT 24 OFFSET ?',
                       (f'%{search}%', minimum, (page - 1) * 24))
    for row in detections:
        row['has_image'] = image_path(row['png_path']) is not None
    species = query('SELECT species, COUNT(*) AS calls, AVG(confidence) AS confidence '
                    'FROM detections GROUP BY species ORDER BY calls DESC LIMIT 8')
    hourly_rows = query("SELECT local_hour(detected_at) AS hour, COUNT(*) AS calls FROM detections "
                        "WHERE datetime(detected_at)>=datetime('now','-1 day') GROUP BY hour")
    counts = {row['hour']: row['calls'] for row in hourly_rows}
    now = dt.datetime.now(ZONE)
    hourly = [dict(hour=(now.hour + 1 + index) % 24,
                   calls=counts.get((now.hour + 1 + index) % 24, 0)) for index in range(24)]
    peak = max((row['calls'] for row in hourly), default=0)
    archived = query('SELECT COUNT(*) AS total FROM image_archive')
    image_total = query('SELECT COUNT(*) AS total FROM detections d LEFT JOIN image_archive a '
                       'ON a.detection_id=d.id WHERE a.detection_id IS NULL')
    return render_template('index.html', stats=stats, detections=detections, species=species,
                           hourly=hourly, peak=max(peak, 1), storage=storage_status(),
                           recorder=pipeline_status('recorder'), detector=pipeline_status('detector'),
                           archived=archived[0]['total'] if archived else 0,
                           image_total=image_total[0]['total'] if image_total else 0,
                           search=search, minimum=minimum, page=page, pages=pages, matched=matched,
                           now=now, cooldown=os.environ.get('COOLDOWN_SECONDS', '10'))


@app.get('/spectrogram/<detection_id>.png')
def spectrogram(detection_id):
    rows = query('SELECT png_path FROM detections WHERE id=?', (detection_id,))
    path = image_path(rows[0]['png_path']) if rows else None
    if path is None:
        abort(404)
    return send_file(path, mimetype='image/png', conditional=True, max_age=3600)


@app.get('/health')
def health():
    ready = bool(query("SELECT name FROM sqlite_master WHERE name='image_archive'"))
    return jsonify(ready=ready), 200 if ready else 503


@app.get('/metrics')
def metrics():
    rows = query('SELECT COUNT(*) AS total FROM detections')
    archive = query('SELECT COUNT(*) AS total FROM image_archive')
    return ('# TYPE batsdropping_detections_total counter\n'
            f'batsdropping_detections_total {rows[0]["total"] if rows else 0}\n'
            '# TYPE batsdropping_archived_images_total counter\n'
            f'batsdropping_archived_images_total {archive[0]["total"] if archive else 0}\n'
            '# TYPE batsdropping_disk_used_ratio gauge\n'
            f'batsdropping_disk_used_ratio {storage_status()["used_percent"] / 100}\n',
            200, {'Content-Type': 'text/plain; version=0.0.4'})


if __name__ == '__main__':
    app.run(host=os.environ.get('WEB_HOST', '127.0.0.1'), port=int(os.environ.get('WEB_PORT', '8090')))
