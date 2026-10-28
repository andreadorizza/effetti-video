"""Builds assets/anteprima.jpg: all 45 effects on one clip, and one effect in every theme.

    .venv/bin/python tests/anteprima.py <clip.mp4> <work folder> [--effetto da-fare]

The clip should be at least 45 x --slot seconds long (each effect gets its own window). Each tile is the frame
at `PEAK` of its window, where most effects are fully in; tweak PEAK per effect if one looks early.
"""
import argparse, json, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from effetti import fx  # noqa: F401,E402
from effetti.i18n import ordered  # noqa: E402

SLOT = 2.8
PEAK = {'default': 0.62, 'scontrino': 0.85, 'da-fare': 0.8, 'passaggi': 0.85, 'commento': 0.9, 'segui': 0.85,
        'griglia-profilo': 0.9, 'interruttori': 0.85, 'messaggi': 0.85, 'muro-titoli': 0.9, 'grafico-vetro': 0.85,
        'zoom-spalla': 0.4, 'classifica': 0.9, 'conto-alla-rovescia': 0.5, 'puntini': 0.35, 'muro-profilo': 0.85}
THEMES = [('neutro', None, None), ('dori · screen', 'temi/dori', 'screen'), ('dori · raster', 'temi/dori', 'raster'),
          ('dori · video', 'temi/dori', 'video')]

ap = argparse.ArgumentParser()
ap.add_argument('clip'); ap.add_argument('work'); ap.add_argument('--effetto', default='da-fare')
ap.add_argument('--slot', type=float, default=2.8, help='seconds per effect (45 x slot must fit in the clip)')
a = ap.parse_args()
SLOT = a.slot
os.makedirs(a.work, exist_ok=True)
py = sys.executable
names = [k for k, _ in ordered()]


def run(plan, stills, out, *extra):
    p = os.path.join(a.work, os.path.basename(out) + '.json'); json.dump({'effetti': plan}, open(p, 'w'))
    subprocess.run([py, os.path.join(HERE, 'scripts', 'effetti.py'), '--piano', p, a.clip, out, '--fermo',
                    ','.join(f'{s:.3f}' for s in stills), '--larghezza', '540', *extra], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def frame_name(out, t):
    t = round(t * 30) / 30
    return out.replace('.png', f'_{t:.2f}.png')


# 1. every effect in its own window
plan, stills = [], []
for i, n in enumerate(names):
    s = i * SLOT; plan.append({'effetto': n, 'inizio': s, 'fine': s + SLOT})
    stills.append(s + SLOT * PEAK.get(n, PEAK['default']))
grid_out = os.path.join(a.work, 'g.png')
run(plan, stills, grid_out)

F = ImageFont.truetype(os.path.join(HERE, 'fonts', 'Inter.ttf'), 24)
F.set_variation_by_axes([32, 760])
tw, th, cols = 270, 480, 9


def tile(path, label):
    im = Image.open(path).convert('RGB').resize((tw, th), Image.LANCZOS)
    d = ImageDraw.Draw(im, 'RGBA')
    w = F.getlength(label)
    d.rounded_rectangle([8, th - 42, 8 + w + 18, th - 8], 8, fill=(0, 0, 0, 170))
    d.text((17, th - 39), label, font=F, fill=(255, 255, 255))
    return im


tiles = [tile(frame_name(grid_out, t), f'{i + 1} {n}') for i, (n, t) in enumerate(zip(names, stills))]
rows = (len(tiles) + cols - 1) // cols
gap = 6
grid = Image.new('RGB', (cols * tw + (cols + 1) * gap, rows * th + (rows + 1) * gap), (16, 16, 18))
for k, t in enumerate(tiles):
    grid.paste(t, (gap + (k % cols) * (tw + gap), gap + (k // cols) * (th + gap)))

# 2. one effect in every theme
strip_t = 1.0 + SLOT * PEAK.get(a.effetto, PEAK['default'])
row = []
for label, theme, variant in THEMES:
    out = os.path.join(a.work, f't_{variant or "neutro"}.png')
    extra = ['--tema', theme, '--variante', variant] if theme else []
    run([{'effetto': a.effetto, 'inizio': 1.0, 'fine': 1.0 + SLOT}], [strip_t], out, *extra)
    row.append(tile(out, label))
strip = Image.new('RGB', (grid.width, th + 2 * gap), (16, 16, 18))
x0 = (grid.width - (len(row) * tw + (len(row) - 1) * gap)) // 2
for k, t in enumerate(row): strip.paste(t, (x0 + k * (tw + gap), gap))

full = Image.new('RGB', (grid.width, grid.height + strip.height + 16), (16, 16, 18))
full.paste(grid, (0, 0)); full.paste(strip, (0, grid.height + 16))
full = full.resize((full.width // 2 * 2 * 3 // 4, full.height // 2 * 2 * 3 // 4), Image.LANCZOS)
dst = os.path.join(HERE, 'assets', 'anteprima.jpg')
full.save(dst, quality=82, optimize=True, progressive=True)
print(dst, full.size, os.path.getsize(dst) // 1024, 'KB')
