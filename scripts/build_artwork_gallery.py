"""Build review sheets and preserve the bookmark for the bilingual /artwork page."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.echo.catalogue import SPECIES as BATS

root = Path(__file__).resolve().parents[1] / 'chirpecho/web/static'
assets = root / 'species'
manifest_path = assets / 'artwork-manifest.json'
manifest = json.loads(manifest_path.read_text())
for number in (17, 44):
    key = f'bird-{number:03d}'
    destination = assets / (key + '-pokemon.webp')
    shutil.copyfile(assets / (key + '-preview.webp'), destination)
    with Image.open(destination) as image:
        manifest[key] = dict(file=destination.name, approved_preview=True,
                             width=image.width, height=image.height,
                             sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

items = [(f'{kind}-{item["number"]:03d}', item)
         for kind, catalogue in [('bird', BIRDS), ('bat', BATS)] for item in catalogue]
for start in range(0, len(items), 16):
    sheet = Image.new('RGB', (1000, 760), '#f3f4ed')
    draw = ImageDraw.Draw(sheet)
    for index, (key, item) in enumerate(items[start:start+16]):
        with Image.open(assets / (key + '-pokemon.webp')) as original:
            image = original.convert('RGBA')
        image.thumbnail((240, 155))
        x, y = index % 4 * 250, index // 4 * 190
        sheet.paste(image, (x + (250-image.width)//2, y), image)
        draw.text((x+8, y+158), item['name'], fill='#183138')
    sheet.save(f'/tmp/art-collection-{start//16}.jpg')

(root / 'artwork-preview.html').write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/artwork"><title>Artwork · Chirp &amp; Echo</title></head>
<body><p>The collection is now on the <a href="/artwork">Artwork page</a>.</p></body></html>
''')
print(f'Review sheets built for {len(items)} species. Public gallery: /artwork')
