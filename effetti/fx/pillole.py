"""pillole (check-pills): Stanza a quadretti, le tue reel appese dietro di te, un cursore clicca pillole blu.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *

_gp = {}


@effetto('pillole', en='check-pills', alias=('check-pills', 'pills'),
         desc='Stanza a quadretti, le tue reel appese dietro di te, un cursore clicca pillole blu', schede=True)
def fx_check_pills(c, e):
    W, H = c.W, c.H; k = ramp(c, e, 0.15, 0); m = c.m[..., None]; al = fade(c, e)
    if (W, H) not in _gp:
        g = np.ones((H, W, 3), np.float32) * np.float32([0.935, 0.945, 0.96]); st = max(20, W // 20); lw = max(1, W // 700)
        for x in range(0, W, st): g[:, x:x + lw] = np.float32([0.86, 0.875, 0.9])
        for y in range(0, H, st): g[y:y + lw] = np.float32([0.86, 0.875, 0.9])
        _gp[(W, H)] = g
    c.img = c.img * (1 - k) + (c.img * m + _gp[(W, H)] * (1 - m)) * k
    def board(i, title):
        bw = int(W * 0.44); im = rrect(bw, int(bw * 1.12), bw * 0.07, (255, 255, 255, 255)); d = ImageDraw.Draw(im)
        d.ellipse([bw * 0.06, bw * 0.055, bw * 0.06 + bw * 0.09, bw * 0.145], fill=(255, 160, 140, 255))
        d.text((bw * 0.19, bw * 0.1), title, font=font('uib', bw * 0.06), fill=(20, 20, 22, 255), anchor='lm')
        gr = thumb_grid(e.cards, 3, 3, int(bw * 0.28), int(bw * 0.025), i0=i * 3)
        im.alpha_composite(gr, ((bw - gr.width) // 2, int(bw * 0.2))); return shadowed(im, 16, 8, 70)
    b1 = cached(e, 'b1', lambda: board(0, e.o.get('handle', '@vibha.in.progress')))
    b2 = cached(e, 'b2', lambda: board(1, e.o.get('board', 'Reels  ·  22 effects')))
    by = max(H * 0.17, c.fy - c.fw * 0.9)
    place(c, b1, W * 0.25, by, 0.6 + 0.4 * pop(c, 0.0), 8, al * clamp(c.lt / 0.1), behind=True)
    place(c, b2, W * 0.76, by - W * 0.02, 0.6 + 0.4 * pop(c, 0.1), -8, al * clamp((c.lt - 0.1) / 0.1), behind=True)
    names = e.o.get('text', 'Hook|Captions|Cuts|B-roll').split('|')
    spots = [(-0.95, 2.35), (0.55, 2.0), (-0.35, 2.95), (0.95, 2.75), (0.1, 3.45), (-1.1, 3.3)]
    ph = W * 0.078; cu = cached(e, 'cur', lambda: cursor(W * 0.055))
    pos = []
    for i, n in enumerate(names):
        sx, sy = spots[i % len(spots)]
        x = clamp(c.fx + sx * c.fw * 1.6, W * 0.16, W * 0.84); y = clamp(c.fy + sy * c.fw, H * 0.3, H * 0.9)
        t0 = 0.22 + 0.2 * i; pos.append((x, y, t0))
        if c.lt < t0: continue
        clicked = c.lt >= t0 + 0.12
        t = text_img(n, ph * 0.42, 'uib', (255, 255, 255)); pw = int(t.width + ph * (0.75 if clicked else 0.35))
        pill = rrect(pw, ph, ph / 2, BLUE + (255,)); pill.alpha_composite(t, (int(ph * 0.18), int((ph - t.height) / 2)))
        if clicked: tick(ImageDraw.Draw(pill), pw - ph * 0.55, ph * 0.33, ph * 0.33)
        sq = 1 - 0.1 * math.sin(math.pi * clamp((c.lt - t0 - 0.12) / 0.2))
        place(c, shadowed(pill, 10, 5, 90), x, y, (0.5 + 0.5 * pop(c, t0, 0.25)) * sq, 0, al, guard=True)
    if pos and c.lt > pos[0][2] - 0.1:
        seg = [p for p in pos if p[2] <= c.lt + 0.1]; tx, ty, t0 = seg[-1]
        px, py = (pos[len(seg) - 2][0], pos[len(seg) - 2][1]) if len(seg) > 1 else (W * 0.9, H * 0.95)
        q = ease_inout((c.lt - (t0 - 0.12)) / 0.2)
        place(c, cu, px + (tx - px) * q + ph * 0.3 + cu.width / 2, py + (ty - py) * q + ph * 0.1 + cu.height / 2, 1, 0, al)
