"""titolo-box (headline-box): Uno zoom con un titolo su due righe, la seconda in un riquadro bianco.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('titolo-box', en='headline-box', alias=('headline', 'headline-box', 'titolo'),
         desc='Uno zoom con un titolo su due righe, la seconda in un riquadro bianco')
def fx_headline_box(c, e):
    face_cam(c, 1 + (float(e.o.get('zoom', 1.2)) - 1) * ease_out(c.lt / 0.22), 0.45)
    W = c.W; al = fade(c, e); lines = e.o.get('text', 'How I got Claude|to edit my reels.').split('|')
    S = cached(e, 'sz', lambda: lines_fit(lines, W * 0.84, 'uib', int(W * 0.085)))
    y = max(c.H * 0.06, c.fy - c.fw * 1.3 - S * 1.3 * len(lines))
    for j, ln in enumerate(lines):
        kj = clamp((c.lt - 0.1 - 0.12 * j) / 0.18)
        if kj <= 0: y += S * 1.3; continue
        boxed = j == len(lines) - 1
        t = cached(e, ('t', j), lambda: text_img(ln, S, 'uib', (16, 16, 18) if boxed else (255, 255, 255), shadow=0 if boxed else 9))
        if boxed:
            bx = rrect(t.width - S * 0.15, S * 1.22, S * 0.08, (255, 255, 255, 255))
            wk = ease_out(kj); bx = bx.crop((0, 0, max(1, int(bx.width * wk)), bx.height))
            comp(c, bx, W / 2 - (t.width - S * 0.15) / 2, y, al, guard=True)
        place(c, t, W / 2, y + S * 0.6, 0.92 + 0.08 * ease_out(kj), 0, al * kj, guard=True)
        y += S * 1.3
