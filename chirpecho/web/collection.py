"""Calendar reports and collection achievements from retained predictions."""
import datetime as dt
from collections import Counter

from chirpecho.web.portraits import profile
from chirpecho.web.milestones import BIRD_COLLECTIONS, BAT_COLLECTIONS, artwork
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS


def collection_history(query, databases):
    """Aggregate in SQLite; never load individual lifetime detections."""
    daily, profiles, first_seen = [], {}, {}
    for kind, database in databases.items():
        cache = {}
        for row in query('SELECT local_day(detected_at) AS day, species, COUNT(*) AS calls, '
                         'MAX(confidence) AS best FROM detections '
                         'WHERE local_day(detected_at) IS NOT NULL GROUP BY day, species', database=database):
            if row['species'] not in cache:
                creature = profile(row['species'], kind == 'bird')
                # Collapse catalogue aliases into one species, keep unknown labels distinct.
                key = (kind, creature['scientific'] or row['species'].casefold())
                cache[row['species']] = key
                profiles[key] = creature
            key = cache[row['species']]
            day = dt.date.fromisoformat(row['day'])
            daily.append(dict(row, day=day, kind=kind, key=key))
            first_seen[key] = min(day, first_seen.get(key, day))
    return dict(daily=daily, profiles=profiles, first_seen=first_seen)


def weekly_report(history, start, selected_day):
    end = start + dt.timedelta(days=7)
    rows = [row for row in history['daily'] if start <= row['day'] < end]
    totals, species_counts = Counter(), Counter()
    days = {start + dt.timedelta(days=i): dict(bird=0, bat=0, species=set()) for i in range(7)}
    for row in rows:
        totals[row['kind']] += row['calls']
        species_counts[row['key']] += row['calls']
        days[row['day']][row['kind']] += row['calls']
        days[row['day']]['species'].add(row['key'])
    cards = [dict(day=day, **value, total=value['bird'] + value['bat'],
                  selected=day == selected_day) for day, value in days.items()]
    newcomers = [dict(profile=history['profiles'][key], kind=key[0], day=day)
                 for key, day in history['first_seen'].items() if start <= day < end]
    newcomers.sort(key=lambda item: (item['day'], item['profile']['name']))
    busiest = max(cards, key=lambda day: day['total'])
    return dict(days=cards, birds=totals['bird'], bats=totals['bat'],
                total=sum(totals.values()), species_count=len(species_counts),
                active_days=sum(day['total'] > 0 for day in cards),
                busiest=busiest if busiest['total'] else None,
                newcomers=newcomers,
                leaders=[dict(profile=history['profiles'][key], kind=key[0], calls=calls)
                         for key, calls in species_counts.most_common(6)])


def milestone_report(history, kind=None):
    if kind is None:
        reports = [(name, milestone_report(history, name)) for name in ('bird', 'bat')]
        cards, categories = [], []
        for name, report in reports:
            for card in report['cards']:
                card['id'] = name + '-' + card['id']
            cards.extend(report['cards'])
            for category in report['categories']:
                title = category['title']
                if title == 'Listening adventures':
                    title = 'Bird listening adventures' if name == 'bird' else 'Bat listening adventures'
                categories.append(dict(category, title=title, kind=name))
        # Show the two collecting checklists first, then the listening goals.
        categories.sort(key=lambda category: category['title'].endswith('listening adventures'))
        days = sorted({row['day'] for row in history['daily']})
        streak = longest = 0
        previous = None
        for day in days:
            streak = streak + 1 if previous and day - previous == dt.timedelta(days=1) else 1
            longest = max(longest, streak)
            previous = day
        return dict(cards=cards, categories=categories, total=len(cards),
                    unlocked=sum(card['unlocked'] for card in cards),
                    species=sum(report['species'] for _, report in reports),
                    active_days=len(days), longest=longest)

    if kind not in ('bird', 'bat'):
        raise ValueError('Unknown milestone collection')
    bird = kind == 'bird'
    days, daily_species = Counter(), {}
    species = set()
    total = 0
    for row in history['daily']:
        if row['kind'] != kind:
            continue
        total += row['calls']
        days[row['day']] += row['calls']
        daily_species.setdefault(row['day'], set()).add(row['key'])
        species.add(row['key'])
    streak = longest = 0
    previous = None
    for day in sorted(days):
        streak = streak + 1 if previous and day - previous == dt.timedelta(days=1) else 1
        longest = max(longest, streak)
        previous = day
    best_day = max(map(len, daily_species.values()), default=0)
    catalogue = BIRDS if bird else tuple(item for item in BATS if item['supported'])
    catalogue_count = sum((kind, item['scientific']) in species for item in catalogue)
    cards = []

    def add(ident, title, description, value, target, portraits, category='Listening adventures', members=()):
        checklist = [dict(profile=profile(name, bird), recorded=(kind, name) in species) for name in members]
        cards.append(dict(id=ident, kind=kind, title=title, description=description, value=value, target=target,
                          unlocked=value >= target, percent=min(100, value / target * 100),
                          artwork=artwork(*portraits), category=category, members=checklist))

    robin = 'Erithacus rubecula' if bird else 'Pipistrellus pipistrellus'
    owl = 'Strix aluco' if bird else 'Plecotus auritus'
    jay = 'Garrulus glandarius' if bird else 'Nyctalus noctula'
    add('first-signal', 'First signal',
        'Save your first bird prediction.' if bird else 'Save your first bat prediction.', total, 1, (robin,))
    add('first-bird' if bird else 'first-bat', 'Bird beginnings' if bird else 'Night visitor',
        'Record your first bird species.' if bird else 'Record your first bat species.', len(species), 1,
        ('Parus major' if bird else 'Pipistrellus pygmaeus',))
    add('bird-chorus' if bird else 'bat-colony', 'A whole chorus' if bird else 'The night club',
        'Record 10 different bird species.' if bird else 'Record 5 different bat species.',
        len(species), 10 if bird else 5, (jay, robin))
    add('field-guide', 'Field guide explorer',
        'Record 25 birds from the catalogue.' if bird else 'Record 10 supported bats from the catalogue.',
        catalogue_count, 25 if bird else 10, (jay, owl))
    add('busy-garden', 'Busy garden' if bird else 'A busy night shift',
        'Record 10 different bird species on one local calendar day.' if bird else
        'Record 3 different bat species on one local calendar day.', best_day, 10 if bird else 3, (robin, jay, owl))
    add('week-streak', 'A week of listening', 'Record activity on 7 consecutive local calendar days.',
        longest, 7, (robin,))
    add('month-discovery', 'A month of discovery', 'Record activity on 30 different local calendar days.',
        len(days), 30, (owl,))
    add('thousand-signals', 'One thousand signals',
        'Save 1,000 bird predictions.' if bird else 'Save 1,000 bat predictions.', total, 1000, (jay,))
    add('ten-thousand', 'An observatory of your own',
        'Save 10,000 bird predictions.' if bird else 'Save 10,000 bat predictions.', total, 10000, (owl, jay))
    atlas = tuple(item['scientific'] for item in catalogue)
    add('bird-atlas' if bird else 'bat-atlas', 'The complete bird atlas' if bird else 'Batlas explorer',
        'Record every bird in the starter catalogue.' if bird else
        'Record all 17 bat species supported by the bundled classifier.',
        catalogue_count, len(atlas), (jay, owl, robin), members=atlas)
    set_category = 'Bird collecting sets' if bird else 'Bat collecting sets'
    for ident, title, description, members in (BIRD_COLLECTIONS if bird else BAT_COLLECTIONS):
        add(ident, title, description, sum((kind, name) in species for name in members),
            len(members), members[:3], category=set_category, members=members)
    categories = [dict(title=title, cards=[card for card in cards if card['category'] == title])
                  for title in (set_category, 'Listening adventures')]
    return dict(cards=cards, categories=categories, unlocked=sum(card['unlocked'] for card in cards),
                total=len(cards), species=len(species), active_days=len(days), longest=longest)
