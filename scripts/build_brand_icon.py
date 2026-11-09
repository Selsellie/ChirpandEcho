"""Rasterize the existing brand mark for iOS home-screen shortcuts (Pillow only)."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / 'chirpecho/web/static'
svg = ET.parse(ROOT / 'brand.svg').getroot()
scale = 180 * 4 / 64
image = Image.new('RGB', (720, 720), '#172e35')
draw = ImageDraw.Draw(image)

for path in svg.findall('{http://www.w3.org/2000/svg}path'):
    tokens = re.findall(r'[a-zA-Z]|-?\d+(?:\.\d+)?', path.attrib['d'])
    points, subpaths, current, start = [], [], (0., 0.), (0., 0.)
    index = 0
    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
        relative = command.islower()
        op = command.upper()
        if op == 'Z':
            points.append(start)
            current = start
            continue
        count = {'M': 2, 'L': 2, 'H': 1, 'C': 6}[op]
        values = list(map(float, tokens[index:index + count]))
        index += count
        def point(x, y):
            return (x + current[0], y + current[1]) if relative else (x, y)
        if op == 'C':
            a, b, end = (point(*values[i:i + 2]) for i in (0, 2, 4))
            for step in range(1, 41):
                t = step / 40
                points.append(tuple((1-t)**3*current[d] + 3*(1-t)**2*t*a[d]
                                    + 3*(1-t)*t*t*b[d] + t**3*end[d] for d in (0, 1)))
            current = end
        else:
            current = ((values[0] + current[0] if relative else values[0]), current[1]) if op == 'H' else point(*values)
            if op == 'M':
                if points:
                    subpaths.append(points)
                    points = []
                start = current
                command = 'l' if relative else 'L'
            points.append(current)
    for points in subpaths + [points]:
        pixels = [(x * scale, y * scale) for x, y in points]
        if 'fill' in path.attrib:
            draw.polygon(pixels, fill=path.attrib['fill'])
        if 'stroke' in path.attrib:
            width = float(path.attrib.get('stroke-width', 1)) * scale
            draw.line(pixels, fill=path.attrib['stroke'], width=round(width))
            for x, y in (pixels[0], pixels[-1]):
                draw.ellipse((x-width/2, y-width/2, x+width/2, y+width/2), fill=path.attrib['stroke'])

# iOS applies the corner mask itself; keep the exported square fully opaque.
image.resize((180, 180), Image.Resampling.LANCZOS).save(ROOT / 'apple-touch-icon.png')
