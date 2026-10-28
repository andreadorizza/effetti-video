"""fermo-immagine (pause-point): L'immagine si blocca e una freccia disegnata a mano ti indica.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('fermo-immagine', en='pause-point', alias=('freccia', 'pause', 'pause-and-point', 'pause-point'),
         desc="L'immagine si blocca e una freccia disegnata a mano ti indica")
def fx_pause_point(c, e):
    if 'f' not in e.state: e.state['f'] = (c.img.copy(), c.m.copy(), c.fx, c.fy, c.fw)
    img, m, c.fx, c.fy, c.fw = e.state['f']; c.img, c.m = img.copy(), m
    face_cam(c, 1 + 0.06 * ease_out(c.lt / e.d), 0.4)
    c.img = c.img * 0.92 + grade(c.img, 'bw') * 0.08
    col = cached(e, 'col', lambda: rgb(e.o.get('color'), P.c('accent2', YELLOW, on=footage(c)))) + (255,)  # a marker straight on the footage: falls back to what reads there
    lay = Image.new('RGBA', (c.W, c.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([c.W * 0.05, c.H * 0.06, c.W * 0.05 + c.W * 0.1, c.H * 0.06 + c.W * 0.1], P.r(16), fill=P.c('dark', (0, 0, 0), 150))
    for bx in (0.075, 0.11): d.rectangle([c.W * bx, c.H * 0.06 + c.W * 0.025, c.W * (bx + 0.017), c.H * 0.06 + c.W * 0.075], fill=P.c('on-dark', (255, 255, 255), 230))
    tx, ty = c.W * float(e.o.get('label_x', 0.72)), c.fy - c.fw * 2.2
    pts = arrow_pts(tx - c.W * 0.05, ty + c.W * 0.06, c.fx + c.fw * 0.75, c.fy - c.fw * 0.35, 0.3)
    k = ease_out((c.lt - 0.15) / 0.4)
    hand_path(d, pts, col, max(6, c.W // 140), k)
    if k >= 0.99: arrow_head(d, pts, col, max(6, c.W // 140), c.W * 0.04)
    comp(c, to_np(lay), 0, 0)
    lab = text_img(e.o.get('text', tr('guarda qui', 'look here')), c.W * 0.07, 'hand', col[:3], shadow=6)
    place(c, lab, tx, ty - lab.height * 0.2, 0.7 + 0.3 * ease_back(c.lt / 0.3), -6, clamp(c.lt / 0.1), guard=True)
