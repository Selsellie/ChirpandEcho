"""Durable first-species Discord notifications, committed with detections."""
import datetime as dt
import json
import logging
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS, LABELS, normalize_label

log = logging.getLogger('notifications')


def webhook_url():
    filename = os.environ.get('DISCORD_WEBHOOK_URL_FILE', '')
    try:
        value = Path(filename).read_text().strip() if filename else os.environ.get('DISCORD_WEBHOOK_URL', '').strip()
    except OSError:
        log.warning('Discord webhook secret file is unavailable')
        return ''
    try:
        parsed = urllib.parse.urlsplit(value)
        valid = (parsed.scheme == 'https' and parsed.hostname in ('discord.com', 'discordapp.com')
                 and parsed.path.startswith('/api/webhooks/') and not parsed.username
                 and not parsed.password and parsed.port in (None, 443))
    except ValueError:
        valid = False
    if value and not valid:
        log.warning('Discord webhook configuration is invalid; notifications disabled')
        return ''
    return urllib.parse.urlunsplit(parsed._replace(netloc='discord.com')) if value else ''


def identity(label, engine):
    entries = BIRDS if engine == 'bird' else BATS
    key = normalize_label(label)
    for item in entries:
        aliases = (item['name'], item['scientific'], item['scientific'] + '_' + item['name'])
        if key in {normalize_label(value) for value in aliases} or (engine != 'bird' and LABELS.get(key) == item['number']):
            return item['scientific'], item['name']
    return key, label


def init_notifications(conn, engine):
    conn.execute('CREATE TABLE IF NOT EXISTS discovered_species '
                 '(species_key TEXT PRIMARY KEY, first_detection_id TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS notification_outbox '
                 '(id TEXT PRIMARY KEY, payload TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, '
                 'next_attempt REAL NOT NULL DEFAULT 0, delivered_at TEXT)')
    # Existing records establish a baseline; enabling notifications never floods
    # Discord with the archive. INSERT OR IGNORE also preserves queued retries.
    for label, ident in conn.execute('SELECT species, MIN(id) FROM detections GROUP BY species').fetchall():
        key, _ = identity(label, engine)
        conn.execute('INSERT OR IGNORE INTO discovered_species VALUES (?, ?)', (key, ident))
    conn.commit()


def queue_discovery(conn, row, engine):
    """Caller commits or rolls back this along with its detection transaction."""
    key, name = identity(row['species'], engine)
    if key in ('', 'unknown', 'unidentified', 'noise'):
        return
    inserted = conn.execute('INSERT OR IGNORE INTO discovered_species VALUES (?, ?)', (key, row['id'])).rowcount
    if not inserted or not webhook_url():
        return
    bird = engine == 'bird'
    from chirpecho.common.rarity import rarity_for
    entry = next((item for item in (BIRDS if bird else BATS) if item['scientific'] == key), None)
    rarity = entry['rarity'] if entry else rarity_for(engine)
    catalogue_note = '\nNot in catalogue — needs to be added. Review the identification.' if bird and entry is None else ''
    payload = {
        'allowed_mentions': {'parse': []},
        'embeds': [{
            'title': '🐦 New bird species discovered!' if bird else '🦇 New bat species discovered!',
            'description': f"**{name[:200]}**\n" + ('A new voice joins your bird collection!' if bird else 'A new night visitor joins your bat collection!') + catalogue_note,
            'color': int(rarity['color'][1:], 16),
            'fields': [
                {'name': 'Type', 'value': 'Bird · Chirp' if bird else 'Bat · Echo', 'inline': True},
                {'name': 'Rarity', 'value': rarity['stars'] + ' ' + rarity['label'], 'inline': True},
                {'name': 'Confidence', 'value': f"{row['confidence']:.1%}", 'inline': True},
            ],
            'timestamp': row['detected_at'],
            'footer': {'text': 'Chirp & Echo · First detection · Game rarity · Automatic prediction'},
        }],
    }
    conn.execute('INSERT INTO notification_outbox (id, payload) VALUES (?, ?)',
                 (row['id'], json.dumps(payload)))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def deliver_pending(conn, now=None):
    """Try one queued event per scan; never propagate delivery failure to audio."""
    url = webhook_url()
    if not url:
        return
    now = time.time() if now is None else now
    row = conn.execute('SELECT id, payload, attempts FROM notification_outbox '
                       'WHERE delivered_at IS NULL AND next_attempt<=? ORDER BY next_attempt, rowid LIMIT 1', (now,)).fetchone()
    if not row:
        return
    ident, payload, attempts = row
    # wait=true asks Discord to confirm message creation before marking delivery.
    parsed = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    query['wait'] = 'true'
    url = urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))
    request = urllib.request.Request(url, data=payload.encode(), headers={
        'Content-Type': 'application/json', 'User-Agent': 'ChirpEcho/1.0'}, method='POST')
    retry = min(3600, 30 * 2 ** min(attempts, 7))
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=3) as response:
            if not 200 <= response.status < 300:
                raise OSError('Unexpected webhook status')
        conn.execute('UPDATE notification_outbox SET delivered_at=? WHERE id=?',
                     (dt.datetime.now(dt.timezone.utc).isoformat(), ident))
        log.info('Discord discovery notification delivered')
    except urllib.error.HTTPError as error:
        if error.code == 429:
            try:
                retry = max(retry, min(86400, float(error.headers.get('Retry-After', retry))))
            except (ValueError, TypeError):
                pass
        conn.execute('UPDATE notification_outbox SET attempts=attempts+1, next_attempt=? WHERE id=?', (now + retry, ident))
        log.warning('Discord notification failed (HTTP %s); retry scheduled', error.code)
    except (OSError, ValueError):
        conn.execute('UPDATE notification_outbox SET attempts=attempts+1, next_attempt=? WHERE id=?', (now + retry, ident))
        # Exception strings can contain the secret URL: never log them.
        log.warning('Discord notification unavailable; retry scheduled')
    conn.commit()
