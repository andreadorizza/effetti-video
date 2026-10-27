"""segui (tap): Compare un pulsante Segui che diventa Segui già.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('segui', en='tap', alias=('follow', 'tap', 'the-tap'),
         desc='Compare un pulsante Segui che diventa Segui già')
def fx_tap(c, e):
    at = float(e.o['at']) - e.start if 'at' in e.o else e.d * 0.45  # 'at' = video second of the tap
    bw, bh = int(c.W * 0.3), int(c.W * 0.09)
    x = clamp(float(e.o['x']) * c.W if 'x' in e.o else c.fx + c.fw * 1.9, bw / 2 + 30, c.W - bw / 2 - 30)
    y = clamp(float(e.o['y']) * c.H if 'y' in e.o else c.fy + c.fw * 1.6, bh + 30, c.H - bh - 30)
    on = c.lt >= at
    col = rgb(e.o.get('color'), (124, 92, 255)) if on else (0, 149, 246)
    im = rrect(bw, bh, bh * 0.28, col + (255,)); d = ImageDraw.Draw(im)
    d.text((bw / 2, bh / 2), 'Following' if on else '+ Follow', font=font('ui', bh * 0.4), fill=(255, 255, 255, 255), anchor='mm')
    pop = ease_back(c.lt / 0.3)
    sq = 1.0
    if on: q = (c.lt - at) / 0.3; sq = 1 - 0.12 * math.sin(math.pi * clamp(q)) if q < 1 else 1
    place(c, shadowed(im, 12, 6, 110), x, y, (0.6 + 0.4 * pop) * sq, 0, clamp(c.lt / 0.1) * clamp((e.d - c.lt) / 0.2), guard=True)
    if on and c.lt - at < 0.4:
        q = (c.lt - at) / 0.4; r = int(bh * (0.3 + 0.9 * q)); ring = Image.new('RGBA', (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([4, 4, 2 * r + 4, 2 * r + 4], outline=(255, 255, 255, int(220 * (1 - q))), width=5)
        place(c, ring, x, y, guard=True)
