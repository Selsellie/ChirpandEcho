"""Apply the same optical scale to bird and bat portraits without redrawing them.

Match visible silhouette area, capped by a safe extent for long wings and tails.
Portraits already carrying this framing policy are skipped on subsequent runs.
"""
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'chirpecho/web/static/species'
MANIFEST = ASSETS / 'artwork-manifest.json'
CANVAS = 1200
MAX_EXTENT = 1104
TARGET_AREA = 0.24 * CANVAS ** 2
POLICY = 'Shared bird/bat optical scale: 24% silhouette area; 1104px maximum extent; centred on 1200px square'


def normalize():
    manifest = json.loads(MANIFEST.read_text())
    changed = 0
    for key, entry in manifest.items():
        if not key.startswith(('bird-', 'bat-')):
            continue
        if entry.get('framing') == POLICY:
            continue
        destination = ASSETS / entry['file']
        image = Image.open(destination).convert('RGBA')
        alpha = image.getchannel('A')
        # Ignore faint generation specks when finding the actual animal.
        bounds = alpha.point(lambda value: 255 if value >= 32 else 0).getbbox()
        if bounds is None:
            raise ValueError(f'Empty artwork: {key}')
        crop = image.crop(bounds)
        coverage = sum(value * count for value, count in
                       enumerate(crop.getchannel('A').histogram())) / 255
        scale = min(math.sqrt(TARGET_AREA / coverage),
                    MAX_EXTENT / max(crop.size))
        size = tuple(max(1, round(edge * scale)) for edge in crop.size)
        crop = crop.resize(size, Image.Resampling.LANCZOS)
        result = Image.new('RGBA', (CANVAS, CANVAS))
        result.alpha_composite(crop, ((CANVAS-size[0])//2, (CANVAS-size[1])//2))
        result.save(destination, 'WEBP', lossless=True)
        changed += 1
        entry.update(width=CANVAS, height=CANVAS,
                     sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                     framing=POLICY,
                     approved_preview=False)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Applied shared optical framing to {changed} portraits.')


if __name__ == '__main__':
    normalize()
