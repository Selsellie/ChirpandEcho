#!/usr/bin/env python3
"""LAN dashboard for retained metadata and space-managed spectrograms."""
import datetime as dt
import json
import math
import os
import re
from pathlib import Path
import shutil
import sqlite3
import time
from zoneinfo import ZoneInfo

from chirpecho.common.runtime import ROOT, configure_logging
configure_logging('webapp')
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for
from chirpecho.echo.catalogue import SPECIES, LABELS, normalize_label
from chirpecho.chirp.catalogue import SPECIES as BIRD_SPECIES
from chirpecho.web.portraits import profile
from chirpecho.web.collection import collection_history, weekly_report, milestone_report
from chirpecho.common.rarity import TIERS
from chirpecho.web.i18n import language, language_return_url, localize_html, safe_return_url, translate


DB_PATH = os.environ.get('DB_PATH', str(ROOT / 'data/db/detections.sqlite3'))
DETECTIONS_DIR = os.environ.get('DETECTIONS_DIR', str(ROOT / 'data/detections'))
INCOMING_DIR = os.environ.get('INCOMING_DIR', str(ROOT / 'data/incoming'))
BIRD_DB_PATH = os.environ.get('BIRD_DB_PATH', str(Path(DB_PATH).parent.parent / 'chirp/db/detections.sqlite3'))
BIRD_DETECTIONS_DIR = os.environ.get('BIRD_DETECTIONS_DIR', str(Path(DB_PATH).parent.parent / 'chirp/detections'))
ECHO_AUDIO_ARCHIVE_DIR = os.environ.get('AUDIO_ARCHIVE_DIR', str(Path(DETECTIONS_DIR) / 'audio'))
BIRD_AUDIO_ARCHIVE_DIR = os.environ.get('BIRD_AUDIO_ARCHIVE_DIR', str(Path(BIRD_DETECTIONS_DIR) / 'audio'))
ZONE = ZoneInfo(os.environ.get('TZ', 'Europe/Amsterdam'))
app = Flask(__name__)
app.jinja_env.globals['creature_profile'] = profile
RARITY_OPTIONS = {key: value for key, value in TIERS.items() if key != 'unranked'}
app.jinja_env.globals['rarity_options'] = RARITY_OPTIONS


def observation_feed(where):
    """Keep the newest matching record in each species' two-minute burst."""
    return ("WITH ranked AS (SELECT d.*, LAG(unixepoch(detected_at)) OVER ("
            "PARTITION BY species_key(species) ORDER BY detected_at DESC, id DESC) AS newer_at "
            "FROM detections d WHERE " + where + "), "
            "visible AS (SELECT * FROM ranked WHERE newer_at IS NULL "
            "OR newer_at - unixepoch(detected_at) > 120) ")


def selected_rarity():
    value = request.args.get('rarity', 'all')
    if value != 'all' and value not in RARITY_OPTIONS:
        abort(400)
    return value


def selected_collection_kind():
    default = 'bat' if request.cookies.get('wildlife-mode') == 'echo' else 'bird'
    kind = request.args.get('kind', default)
    if kind == 'all':
        kind = default
    if kind not in ('bird', 'bat'):
        abort(400)
    return kind


@app.context_processor
def listening_mode():
    bird = request.path == '/chirp' or request.path.startswith('/chirp/')
    shared = request.path in ('/status', '/artwork', '/calendar', '/milestones')
    selected_bird = bird or (shared and request.cookies.get('wildlife-mode') == 'chirp')
    if request.path == '/artwork':
        selected_bird = selected_collection_kind() == 'bird'
    tail = request.path.rstrip('/').split('/')[-1]
    section = tail if tail in ('species', 'logs') else ''
    paths = dict(overview='/', species='/species', artwork='/artwork', logs='/logs', health='/status', calendar='/calendar', milestones='/milestones')
    chirp_url = '/chirp' + ('/' + section if section else '')
    echo_url = '/' + section
    if request.path == '/artwork':
        filters = {key: request.args[key] for key in ('q', 'lang') if key in request.args}
        endpoint = 'artwork'
        chirp_url = url_for(endpoint, kind='bird', **filters)
        echo_url = url_for(endpoint, kind='bat', **filters)
    return dict(active_wildlife_mode='chirp' if selected_bird else 'echo',
                mode='shared' if shared else 'chirp' if bird else 'echo',
                bird=bird, timezone=ZONE.key, language=language(), language_return=language_return_url(),
                mode_name='System' if shared else 'Chirp' if bird else 'Echo',
                navigation={key: '/chirp' + (value if value != '/' else '') if selected_bird and key in ('overview', 'species', 'logs') else value
                            for key, value in paths.items()},
                chirp_url=chirp_url, echo_url=echo_url)


@app.post('/language')
def set_language():
    selected = request.form.get('lang', 'en')
    if selected not in ('en', 'nl'):
        abort(400)
    response = redirect(safe_return_url(request.form.get('next', '/')), code=303)
    response.set_cookie('chirpecho-language', selected, max_age=365*24*3600, httponly=True, samesite='Lax')
    return response


@app.after_request
def translate_page(response):
    if response.mimetype == 'text/html':
        selected = language()
        if selected == 'nl':
            response.set_data(localize_html(response.get_data(as_text=True)))
        response.headers['Content-Language'] = selected
        response.vary.add('Cookie')
        if request.args.get('lang') in ('en', 'nl'):
            response.set_cookie('chirpecho-language', selected, max_age=365*24*3600, httponly=True, samesite='Lax')
    return response


@app.after_request
def remember_wildlife_mode(response):
    if request.path == '/artwork' and response.status_code == 200:
        response.set_cookie('wildlife-mode', 'chirp' if selected_collection_kind() == 'bird' else 'echo',
                            max_age=365 * 24 * 3600, httponly=True, samesite='Lax')
    if request.path in ('/', '/species', '/chirp', '/chirp/species', '/logs', '/chirp/logs') and response.status_code == 200:
        response.set_cookie('wildlife-mode', 'chirp' if request.path.startswith('/chirp') else 'echo',
                            max_age=365 * 24 * 3600, httponly=True, samesite='Lax')
    return response


@app.get('/chirp')
@app.get('/chirp/species', endpoint='chirp_species')
@app.get('/chirp/logs', endpoint='chirp_logs')
@app.get('/chirp/status', endpoint='chirp_status')
def chirp():
    if request.path == '/chirp/status':
        return redirect('/' + request.path.rsplit('/', 1)[-1])
    return species_guide() if request.path.endswith('/species') else index()


def local_time(value):
    try:
        value = dt.datetime.fromisoformat(value)
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZONE)
        return value.astimezone(ZONE)
    except (TypeError, ValueError):
        return None


def query(sql, parameters=(), database=None):
    database = database or (BIRD_DB_PATH if request.path.startswith('/chirp') else DB_PATH)
    if not Path(database).exists():
        return []
    conn = sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.create_function('local_day', 1, lambda value: local_time(value).date().isoformat() if local_time(value) else None)
    conn.create_function('local_hour', 1, lambda value: local_time(value).hour if local_time(value) else 0)
    bird = request.path.startswith('/chirp')
    def species_key(label):
        creature = profile(label, bird)
        return creature['scientific'] or creature['name']
    conn.create_function('species_key', 1, species_key, deterministic=True)
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
    return path if path.parent == Path(BIRD_DETECTIONS_DIR if request.path.startswith('/chirp') else DETECTIONS_DIR).resolve() and path.is_file() else None


def pipeline_status(component):
    directory = Path(os.environ.get('STATUS_DIR', ROOT / 'data/status'))
    try:
        data = json.loads((directory / f'{component}.json').read_text())
        age = time.time() - float(data.get('updated_at', 0))
        data['fresh'] = 0 <= age < (30 if component == 'recorder' else 180)
        data['updated_label'] = dt.datetime.fromtimestamp(float(data.get('updated_at', 0)), ZONE).strftime('%d %b · %H:%M:%S')
        return data
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        return {'state': 'starting', 'fresh': False}


def storage_status():
    directory = Path(DETECTIONS_DIR)
    while not directory.exists():
        directory = directory.parent
    disk = shutil.disk_usage(directory)
    return dict(used_percent=round(disk.used / disk.total * 100, 1),
                free_bytes=disk.free,
                free_gb=round(disk.free / 1024 ** 3, 1),
                high_water=int(os.environ.get('STORAGE_HIGH_WATER_PERCENT', '85')))


def log_summary(bird=False):
    """Read a bounded tail only; never load an unbounded log into a request."""
    directory = Path(os.environ.get('LOG_DIR', ROOT / 'data/logs'))
    totals = dict(checked=0, saved=0, cooldown=0, processed=0, raw=0, accepted=0)
    events, periods = [], []
    warnings = 0
    for component in (('chirp_recorder', 'chirp_detector') if bird else ('recorder', 'detector')):
        try:
            with (directory / f'{component}.log').open('rb') as handle:
                handle.seek(0, 2)
                start = max(0, handle.tell() - 512 * 1024)
                handle.seek(start)
                if start:
                    handle.readline()
                lines = handle.read().decode('utf-8', errors='replace').splitlines()
        except OSError:
            continue
        if lines:
            periods.append(f'{component}: {lines[0][:19]} – {lines[-1][:19]}')
        for line in lines:
            match = re.search(r'(\d+) chunks checked, (\d+) retained, (\d+) cooldown skips', line)
            if match:
                for key, value in zip(('checked', 'saved', 'cooldown'), match.groups()):
                    totals[key] += int(value)
            if bird and component == 'chirp_recorder' and ' wrote ' in line:
                totals['saved'] += 1
            result = re.search(r'(\d+) raw detections, (\d+) above confidence threshold', line)
            if result:
                totals['processed'] += 1
                totals['raw'] += int(result[1])
                totals['accepted'] += int(result[2])
            warning = ' WARNING ' in line or ' ERROR ' in line or ' CRITICAL ' in line
            warnings += int(warning)
            if warning or result or ' wrote ' in line:
                message = ('Sound recorded; waiting for classification.' if ' wrote ' in line else
                           ('Sound recorded, no qualifying bird predictions.' if bird else 'Sound recorded, no qualifying bat calls.') if result and int(result[2]) == 0 else
                           f'{result[2]} qualifying {"bird predictions" if bird else "bat calls"} found.' if result else line[24:])
                events.append(dict(time=line[:23], component=component, warning=warning,
                                   message=message, detail=line[:2000]))
    return dict(totals=totals, warnings=warnings, periods=periods,
                events=sorted(events, key=lambda item: item['time'], reverse=True)[:40])


def health_checks(recorder, detector, storage):
    try:
        database = bool(query("SELECT name FROM sqlite_master WHERE name='image_archive'"))
    except sqlite3.Error:
        database = False
    reserve = int(os.environ.get('MIN_FREE_MB', '1024')) * 1024 ** 2
    return [dict(name='Microphone capture', ok=recorder['fresh'],
                 detail='Audio chunks are arriving. This does not confirm bat activity.' if recorder['fresh'] else 'No recent recorder heartbeat. Check the recorder and microphone.'),
            dict(name='Bat classifier', ok=detector['fresh'],
                 detail=f"Detector is {detector.get('state', 'unknown')}. Zero detections can be normal." if detector['fresh'] else 'No recent detector heartbeat. Check the detector logs.'),
            dict(name='Detection database', ok=database,
                 detail='The archive is readable.' if database else 'The archive is unavailable or not initialized.'),
            dict(name='Storage reserve', ok=storage['free_bytes'] >= reserve and storage['used_percent'] < storage['high_water'],
                 detail=f"{storage['free_gb']} GB free · {storage['used_percent']}% used. Cleanup starts at {storage['high_water']}%.")]


@app.template_filter('localdate')
def localdate(value, pattern='%d %b · %H:%M:%S'):
    date = local_time(value)
    return date.strftime(pattern) if date else 'Waiting for activity'


@app.get('/')
@app.get('/logs', endpoint='logs')
@app.get('/status', endpoint='status')
def index():
    tab = 'logs' if request.path.endswith('/logs') else 'health' if request.path == '/status' else 'overview'
    if tab != 'overview':
        recorder, detector, storage = pipeline_status('recorder'), pipeline_status('detector'), storage_status()
        bird_recorder, bird_detector = pipeline_status('chirp_recorder'), pipeline_status('chirp_detector')
        checks = health_checks(recorder, detector, storage) if tab == 'health' else []
        if tab == 'health':
            try:
                bird_database = bool(query("SELECT name FROM sqlite_master WHERE name='image_archive'", database=BIRD_DB_PATH))
            except sqlite3.Error:
                bird_database = False
            checks += [dict(name='Chirp · Audio capture', ok=bird_recorder['fresh'] and bird_recorder.get('state') not in ('error','buffer_full'), detail='Audible audio from the shared microphone. State: '+bird_recorder.get('state','starting')),
                       dict(name='Chirp · BirdNET classifier', ok=bird_detector['fresh'] and bird_detector.get('state') in ('ready','processing'), detail='BirdNET 2.4 local inference. State: '+bird_detector.get('state','starting')),
                       dict(name='Chirp · Bird database', ok=bird_database, detail='Bird records are stored separately from Echo records.')]

        bird = request.path.startswith('/chirp')
        return render_template('index.html', tab=tab, logs=log_summary(bird=bird) if tab == 'logs' else None,
                               checks=checks, storage=storage, healthy=all(check['ok'] for check in checks),
                               recorder=bird_recorder if bird and tab == 'logs' else recorder,
                               detector=bird_detector if bird and tab == 'logs' else detector,
                               bird_recorder=bird_recorder, bird_detector=bird_detector, now=dt.datetime.now(ZONE))
    search = request.args.get('q', '').strip()[:100]
    rarity_filter = selected_rarity()
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
    bird = request.path.startswith('/chirp')
    where = 'species LIKE ? AND confidence>=?'
    parameters = [f'%{search}%', minimum]
    known_labels = query('SELECT DISTINCT species FROM detections') if search or rarity_filter != 'all' else []
    if search:
        localized = [row['species'] for row in known_labels if search.casefold() in translate(profile(row['species'], bird)['name']).casefold()]
        if localized:
            where = '(species LIKE ? OR species IN (' + ','.join('?' for _ in localized) + ')) AND confidence>=?'
            parameters = [f'%{search}%', *localized, minimum]
    if rarity_filter != 'all':
        # Match actual stored labels, including scientific and legacy aliases,
        # before applying LIMIT so counts and pagination stay accurate.
        matching = [row['species'] for row in known_labels
                    if profile(row['species'], bird)['rarity']['key'] == rarity_filter]
        if matching:
            where += ' AND species IN (' + ','.join('?' for _ in matching) + ')'
            parameters.extend(matching)
        else:
            where += ' AND 0'
    feed = observation_feed(where)
    filtered = query(feed + 'SELECT COUNT(*) AS total FROM visible', parameters)
    matched = filtered[0]['total'] if filtered else 0
    pages = max(1, math.ceil(matched / 24))
    page = min(page, pages)
    detections = query(feed + 'SELECT d.*, a.reason AS archive_reason FROM visible d '
                       'LEFT JOIN image_archive a ON a.detection_id=d.id '
                       ' ORDER BY d.detected_at DESC LIMIT 24 OFFSET ?',
                       (*parameters, (page - 1) * 24))
    for row in detections:
        row['has_image'] = image_path(row['png_path']) is not None
        row['has_spectrum_data'] = row['has_image'] and row['png_path'].endswith('.spec')
        audio_dir = BIRD_AUDIO_ARCHIVE_DIR if bird else ECHO_AUDIO_ARCHIVE_DIR
        audio_name = Path(row.get('source_file') or '').name
        row['audio_available'] = bool(audio_name and (Path(audio_dir) / audio_name).is_file())
    # Resolve historical model labels against the current catalogue before
    # ranking visitors, so adding a species also updates existing records.
    visitors = {}
    for row in query('SELECT species, COUNT(*) AS calls, AVG(confidence) AS confidence '
                     'FROM detections GROUP BY species'):
        creature = profile(row['species'], bird)
        key = creature['scientific'] or creature['name']
        visitor = visitors.setdefault(key, dict(species=creature['name'], calls=0, confidence=0))
        visitor['calls'] += row['calls']
        visitor['confidence'] += (row['confidence'] or 0) * row['calls']
    for visitor in visitors.values():
        visitor['confidence'] /= visitor['calls']
    species = sorted(visitors.values(), key=lambda item: (-item['calls'], item['species']))[:8]
    stats['species_count'] = len(visitors)
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
    bird = request.path.startswith('/chirp')
    recorder, detector, storage = pipeline_status('chirp_recorder' if bird else 'recorder'), pipeline_status('chirp_detector' if bird else 'detector'), storage_status()
    return render_template('index.html', tab=tab,
                           stats=stats, detections=detections, species=species,
                           hourly=hourly, peak=max(peak, 1), storage=storage,
                           recorder=recorder, detector=detector,
                           archived=archived[0]['total'] if archived else 0,
                           image_total=image_total[0]['total'] if image_total else 0,
                           search=search, minimum=minimum, page=page, pages=pages, matched=matched, rarity_filter=rarity_filter,
                           now=now, cooldown=os.environ.get('COOLDOWN_SECONDS', '10'))


def spectrum_record(detection_id):
    rows = query('SELECT * FROM detections WHERE id=?', (detection_id,))
    path = image_path(rows[0]['png_path']) if rows else None
    if path is None:
        abort(404)
    return rows[0], path


def archive_audio_path(row, bird):
    filename = Path(row.get('source_file') or '').name
    directory = Path(BIRD_AUDIO_ARCHIVE_DIR if bird else ECHO_AUDIO_ARCHIVE_DIR).resolve()
    path = (directory / filename).resolve()
    return path if filename and path.parent == directory and path.suffix.lower() == '.wav' else None


@app.get('/observation/<detection_id>/delete')
@app.get('/chirp/observation/<detection_id>/delete', endpoint='chirp_delete_confirmation')
def delete_confirmation(detection_id):
    rows = query('SELECT id,species,detected_at FROM detections WHERE id=?', (detection_id,))
    if not rows:
        abort(404)
    return render_template('delete_observation.html', detection=rows[0], bird=request.path.startswith('/chirp'))


@app.post('/observation/<detection_id>/delete')
@app.post('/chirp/observation/<detection_id>/delete', endpoint='chirp_delete_observation')
def delete_observation(detection_id):
    if request.form.get('confirm') != 'delete':
        abort(400)
    bird = request.path.startswith('/chirp')
    database = BIRD_DB_PATH if bird else DB_PATH
    detections_dir = Path(BIRD_DETECTIONS_DIR if bird else DETECTIONS_DIR).resolve()
    conn = sqlite3.connect(database, timeout=10)
    conn.row_factory = sqlite3.Row
    spectrum = audio = None
    try:
        row = conn.execute('SELECT * FROM detections WHERE id=?', (detection_id,)).fetchone()
        if row is None:
            abort(404)
        spectrum = Path(row['png_path']).resolve()
        if spectrum.parent != detections_dir:
            spectrum = None
        conn.execute('BEGIN IMMEDIATE')
        conn.execute('DELETE FROM detections WHERE id=?', (detection_id,))
        conn.execute('DELETE FROM image_archive WHERE detection_id=?', (detection_id,))
        conn.execute('DELETE FROM image_cleanup_queue WHERE detection_id=?', (detection_id,))
        still_referenced = conn.execute('SELECT 1 FROM detections WHERE source_file=? LIMIT 1',
                                        (row['source_file'],)).fetchone()
        if not still_referenced:
            audio = archive_audio_path(dict(row), bird)
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
    for path in (spectrum, audio):
        if path is not None:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                app.logger.exception('Could not remove media for deleted observation')
    return redirect(('/chirp' if bird else '/') + '#archive', code=303)


@app.get('/observation/<detection_id>/audio')
@app.get('/chirp/observation/<detection_id>/audio', endpoint='chirp_observation_audio')
def observation_audio(detection_id):
    bird = request.path.startswith('/chirp')
    rows = query('SELECT * FROM detections WHERE id=?', (detection_id,))
    path = archive_audio_path(rows[0], bird) if rows else None
    if path is None or not path.is_file():
        abort(404)
    return send_file(path, mimetype='audio/wav', conditional=True, max_age=0)


@app.get('/spectrogram/<detection_id>')
@app.get('/chirp/spectrogram/<detection_id>', endpoint='chirp_spectrogram')
def spectrogram(detection_id):
    detection, path = spectrum_record(detection_id)
    return render_template('spectrogram.html', detection=detection, compact=path.suffix == '.spec')


@app.get('/spectrogram/<detection_id>/data')
@app.get('/chirp/spectrogram/<detection_id>/data', endpoint='chirp_spectrogram_data')
def spectrogram_data(detection_id):
    _, path = spectrum_record(detection_id)
    if path.suffix != '.spec':
        abort(404)
    response = send_file(path, mimetype='application/json', conditional=True, max_age=3600)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@app.get('/spectrogram/<detection_id>.png')
@app.get('/chirp/spectrogram/<detection_id>.png', endpoint='chirp_legacy_spectrogram')
def legacy_spectrogram(detection_id):
    _, path = spectrum_record(detection_id)
    if path.suffix == '.spec':
        return redirect(url_for('chirp_spectrogram' if request.path.startswith('/chirp') else 'spectrogram', detection_id=detection_id))
    return send_file(path, mimetype='image/png', conditional=True, max_age=3600)


@app.get('/species')
def species_guide():
    search = request.args.get('q', '').strip()[:100]
    rarity_filter = selected_rarity()
    collection = request.args.get('collection', 'all')
    if collection not in ('all', 'recorded', 'undiscovered'):
        abort(400)
    bird = request.path.startswith('/chirp')
    catalogue = BIRD_SPECIES if bird else SPECIES
    from chirpecho.web.artwork import artwork_group
    kind = 'bird' if bird else 'bat'
    species_types = {item['number']: artwork_group(dict(item, kind=kind)) for item in catalogue}
    group_options = {group.lower().replace(' ', '-'): group for group in species_types.values()}
    group_options = dict(sorted(group_options.items(),
                                key=lambda pair: (pair[1] == 'Others',
                                                  (translate(pair[1]) if language() == 'nl' else pair[1]).casefold())))
    species_group = request.args.get('group', 'all')
    if species_group != 'all' and species_group not in group_options:
        abort(400)
    labels = {normalize_label(value):item['number'] for item in catalogue for value in (item['name'], item['scientific'], item['scientific'] + '_' + item['name'])} if bird else LABELS
    entries = {item['number']: dict(item, calls=0, first=None, last=None, best=0, labels=[]) for item in catalogue}
    rows = query('SELECT species, COUNT(*) AS calls, MIN(detected_at) AS first, '
                 'MAX(detected_at) AS last, MAX(confidence) AS best FROM detections GROUP BY species')
    unmatched = 0
    pending_species = []
    for row in rows:
        number = profile(row['species'], True)['number'] if bird else labels.get(normalize_label(row['species']))
        if number is None:
            unmatched += row['calls']
            if bird:
                pending_species.append(dict(row, profile=profile(row['species'], True)))
            continue
        item = entries[number]
        item['calls'] += row['calls']
        item['best'] = max(item['best'], row['best'])
        item['labels'].append(row['species'])
        if item['first'] is None or local_time(row['first']) < local_time(item['first']):
            item['first'] = row['first']
        if item['last'] is None or local_time(row['last']) > local_time(item['last']):
            item['last'] = row['last']
    recorded = sum(item['calls'] > 0 for item in entries.values())
    visible = [item for item in entries.values()
               if (not search or search.casefold() in ' '.join((item['name'], item['scientific'], item['group'], species_types[item['number']], item['habitat'], translate(item['name']), translate(item['group']), translate(species_types[item['number']]), translate(item['habitat']))).casefold())
               and (species_group == 'all' or species_types[item['number']] == group_options[species_group])
               and (collection == 'all' or (item['calls'] > 0) == (collection == 'recorded'))
               and (rarity_filter == 'all' or item['rarity']['key'] == rarity_filter)]
    return render_template('index.html', tab='species', catalogue=visible, catalogue_total=len(catalogue),
                           recorded=recorded, unmatched=unmatched, pending_species=pending_species, search=search, collection=collection, rarity_filter=rarity_filter,
                           species_group=species_group, group_options=group_options,
                           recorder=pipeline_status('chirp_recorder' if bird else 'recorder'), detector=pipeline_status('chirp_detector' if bird else 'detector'),
                           now=dt.datetime.now(ZONE))


@app.get('/artwork')
def artwork():
    search = request.args.get('q', '').strip()[:100]
    kind = selected_collection_kind()
    entries = []
    for group, catalogue in [('bird', BIRD_SPECIES), ('bat', SPECIES)]:
        for item in catalogue:
            if kind != 'all' and kind != group:
                continue
            if search and search.casefold() not in ' '.join((item['name'], translate(item['name']), item['scientific'])).casefold():
                continue
            entries.append(dict(item, kind=group, creature=profile(item['name'], group == 'bird')))
    display_name = translate if language() == 'nl' else str
    from chirpecho.web.artwork import artwork_group
    entries.sort(key=lambda item: (artwork_group(item) == 'Others',
                                   display_name(artwork_group(item)).casefold(),
                                   display_name(item['name']).casefold()))
    artwork_groups = {}
    for item in entries:
        artwork_groups.setdefault(artwork_group(item), []).append(item)
    return render_template('index.html', tab='artwork', artwork_entries=entries,
                           artwork_groups=artwork_groups,
                           artwork_total=len(BIRD_SPECIES if kind == 'bird' else SPECIES), search=search, artwork_kind=kind,
                           recorder=pipeline_status('recorder'), detector=pipeline_status('detector'),
                           now=dt.datetime.now(ZONE))


@app.get('/static/artwork-preview.html')
def artwork_preview_bookmark():
    filters = {key: request.args[key] for key in ('lang', 'kind', 'q') if key in request.args}
    return redirect(url_for('artwork', **filters))


@app.get('/health')
def health():
    ready = bool(query("SELECT name FROM sqlite_master WHERE name='image_archive'"))
    if os.environ.get('BIRD_ENABLED') == '1':
        ready = ready and bool(query("SELECT name FROM sqlite_master WHERE name='image_archive'", database=BIRD_DB_PATH))
    return jsonify(ready=ready), 200 if ready else 503


@app.get('/metrics')
def metrics():
    rows = query('SELECT COUNT(*) AS total FROM detections')
    archive = query('SELECT COUNT(*) AS total FROM image_archive')
    bird_rows = query('SELECT COUNT(*) AS total FROM detections', database=BIRD_DB_PATH)
    return ('# TYPE batsdropping_detections_total counter\n'
            f'batsdropping_detections_total {rows[0]["total"] if rows else 0}\n'
            '# TYPE chirp_detections_total counter\n'
            f'chirp_detections_total {bird_rows[0]["total"] if bird_rows else 0}\n'
            '# TYPE batsdropping_archived_images_total counter\n'
            f'batsdropping_archived_images_total {archive[0]["total"] if archive else 0}\n'
            '# TYPE batsdropping_disk_used_ratio gauge\n'
            f'batsdropping_disk_used_ratio {storage_status()["used_percent"] / 100}\n',
            200, {'Content-Type': 'text/plain; version=0.0.4'})



def collection_databases():
    return {'bird': BIRD_DB_PATH, 'bat': DB_PATH}


@app.get('/calendar')
def calendar():
    now = dt.datetime.now(ZONE)
    try:
        requested = dt.date.fromisoformat(request.args.get('week', now.date().isoformat()))
        start = requested - dt.timedelta(days=requested.weekday())
        # Keep navigation dates inside the supported date range.
        previous, following = start - dt.timedelta(days=7), start + dt.timedelta(days=7)
        selected_day = dt.date.fromisoformat(request.args.get('day', requested.isoformat()))
        if not start <= selected_day < following:
            selected_day = start
    except (ValueError, OverflowError):
        abort(400)
    history = collection_history(query, collection_databases())
    report = weekly_report(history, start, selected_day)
    hourly, events = {'bird': [0] * 24, 'bat': [0] * 24}, []
    for kind, database in collection_databases().items():
        for row in query('SELECT local_hour(detected_at) AS hour, COUNT(*) AS calls FROM detections '
                         'WHERE local_day(detected_at)=? GROUP BY hour',
                         (selected_day.isoformat(),), database=database):
            hourly[kind][row['hour']] = row['calls']
        for row in query('SELECT * FROM detections '
                         'WHERE local_day(detected_at)=? ORDER BY julianday(detected_at) DESC LIMIT 30',
                         (selected_day.isoformat(),), database=database):
            audio = archive_audio_path(row, kind == 'bird')
            spectrum = Path(row['png_path']).resolve() if row.get('png_path') else None
            directory = Path(BIRD_DETECTIONS_DIR if kind == 'bird' else DETECTIONS_DIR).resolve()
            events.append(dict(row, kind=kind, profile=profile(row['species'], kind == 'bird'),
                               instant=local_time(row['detected_at']).timestamp(),
                               audio_available=bool(audio and audio.is_file()),
                               has_image=bool(spectrum and spectrum.parent == directory and spectrum.is_file())))
    events.sort(key=lambda row: row['instant'], reverse=True)
    peak = max(1, *hourly['bird'], *hourly['bat'])
    return render_template('index.html', tab='calendar', report=report, start=start,
                           week_end=following - dt.timedelta(days=1), previous=previous,
                           following=following, selected_day=selected_day, hourly=hourly,
                           timeline_peak=peak, events=events[:30], now=now,
                           recorder=pipeline_status('recorder'), detector=pipeline_status('detector'))


@app.get('/milestones')
def milestones():
    history = collection_history(query, collection_databases())
    return render_template('index.html', tab='milestones', achievements=milestone_report(history),
                           now=dt.datetime.now(ZONE), recorder=pipeline_status('recorder'),
                           detector=pipeline_status('detector'))


if __name__ == '__main__':
    app.run(host=os.environ.get('WEB_HOST', '127.0.0.1'), port=int(os.environ.get('WEB_PORT', '8090')))
