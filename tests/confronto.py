"""Regression check: the port must draw exactly what the original draws.

Renders every effect with Vibha's original fx.py and with effetti-video (neutral theme, English texts,
MediaPipe tracking), on the same clip, at the same instants, and compares the frames pixel by pixel.

    .venv/bin/python tests/confronto.py <claude-video-effects folder> <clip.mp4> <work folder> [effect ...]

The clip should be at least 45 x 2.8 s long. Prints one line per effect: OK when every pixel matches.
"""
import json, os, subprocess, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from effetti import fx  # noqa: F401,E402
from effetti.i18n import EFFECTS  # noqa: E402

ORIG, CLIP, WORK = sys.argv[1:4]
ONLY = set(sys.argv[4:])
SLOT, AT = 2.8, (0.5, 0.92)
os.makedirs(WORK, exist_ok=True)
names = [(it, v['en']) for it, v in EFFECTS.items() if not ONLY or it in ONLY or v['en'] in ONLY]
plan_en, plan_it, stills = [], [], []
for i, (it, en) in enumerate(names):
    s = round(i * SLOT, 3)
    plan_en.append({'fx': en, 'start': s, 'end': s + SLOT})
    plan_it.append({'fx': it, 'start': s, 'end': s + SLOT})
    stills += [round(s + SLOT * a, 3) for a in AT]
json.dump({'effects': plan_en}, open(os.path.join(WORK, 'plan_en.json'), 'w'))
json.dump({'effetti': plan_it}, open(os.path.join(WORK, 'plan_it.json'), 'w'))
st = ','.join(str(x) for x in stills)
py = sys.executable
for tag, cmd in (('orig', [py, os.path.join(ORIG, 'scripts', 'fx.py'), '--plan', os.path.join(WORK, 'plan_en.json')]),
                 ('port', [py, os.path.join(HERE, 'scripts', 'effetti.py'), '--piano', os.path.join(WORK, 'plan_it.json'),
                           '--lingua', 'en', '--tracciamento', 'mediapipe'])):
    os.makedirs(os.path.join(WORK, tag), exist_ok=True)
    subprocess.run(cmd + [CLIP, os.path.join(WORK, tag, 'f.png'), '--still', st, '--width', '540'], check=True,
                   stdout=subprocess.DEVNULL)

bad = 0
for i, (it, en) in enumerate(names):
    worst = 0
    for t in stills[2 * i:2 * i + 2]:
        fps = 30.0
        tt = round(t * fps) / fps
        a = cv2.imread(os.path.join(WORK, 'orig', f'f_{tt:.2f}.png')); b = cv2.imread(os.path.join(WORK, 'port', f'f_{tt:.2f}.png'))
        if a is None or b is None: worst = 999; continue
        worst = max(worst, int(np.abs(a.astype(int) - b.astype(int)).max()))
    bad += worst > 0
    print(f"{'OK ' if worst == 0 else 'DIFF'} {it:20s} ({en}) max diff {worst}")
print(f'\n{len(names) - bad}/{len(names)} identical')
