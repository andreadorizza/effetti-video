"""interruttori (apple-toggles): Una scheda Impostazioni dell'iPhone accende gli interruttori, una riga alla volta.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('interruttori', en='apple-toggles', alias=('apple-toggles', 'impostazioni', 'toggles'),
         desc="Una scheda Impostazioni dell'iPhone accende gli interruttori, una riga alla volta")
def fx_apple_toggles(c, e):
    rows = e.o.get('text', tr('Una clip|Scrivi /effetti|Niente montaggio', 'One clip|Type /effects|Zero editing apps')).split('|')
    if e.o.get('pos', 'above') != 'below': face_cam(c, 1 + (float(e.o.get('zoom', 1.12)) - 1) * ease_out(c.lt / 0.5), 0.56)
    W = c.W; cw = int(W * 0.72); rh = int(W * 0.125); ch = rh * len(rows); r = int(W * 0.055)
    tw, th = int(W * 0.135), int(W * 0.08); tx = cw - int(W * 0.05) - tw
    def base():
        im = rrect(cw, ch, r, P.c('surface', (255, 255, 255), 250)); d = ImageDraw.Draw(im)
        for i, s in enumerate(rows):
            d.text((W * 0.05, i * rh + rh / 2), s, font=fontfor('ui', W * 0.05, s), fill=P.c('on-surface', (18, 18, 20), 255), anchor='lm')
            if i: d.line([(W * 0.05, i * rh), (cw, i * rh)], fill=P.c('line', (222, 222, 226), 255), width=max(2, W // 900))
        pad = max(10, W // 60) * 2 + W // 90
        return shadowed(im, max(10, W // 60), W // 90, 110), pad
    sh, pad = cached(e, 'base', base)
    ts = [float(x) for x in e.o['ticks'].split('|')] if e.o.get('ticks') else [0.45 + 0.34 * i for i in range(len(rows))]
    im = sh.copy(); d = ImageDraw.Draw(im)
    off, on = np.float32(P.c('line', (233, 233, 235))), np.float32(rgb(e.o.get('color'), P.c('success', (52, 199, 89))))
    for i in range(len(rows)):
        u = ease_out((c.lt - ts[i]) / 0.2) if i < len(ts) else 0.0
        col = tuple(int(v) for v in off * (1 - u) + on * u) + (255,)
        x0, y0 = pad + tx, pad + i * rh + (rh - th) / 2
        d.rounded_rectangle([x0, y0, x0 + tw, y0 + th], P.r(th // 2), fill=col)
        kr = th / 2 - W * 0.006; kx = x0 + th / 2 + (tw - th) * u; ky = y0 + th / 2
        if P.shadows: d.ellipse([kx - kr, ky - kr + W * 0.002, kx + kr, ky + kr + W * 0.004], fill=(0, 0, 0, 40))
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=P.c('surface', (255, 255, 255), 255))
    q = pop(c, 0.0, 0.38); al = fade(c, e) * clamp(c.lt / 0.1)
    if e.o.get('pos', 'above') == 'below':
        place(c, im, c.W / 2, min(c.H - ch * 0.75, c.fy + c.fw * 2.5), 0.6 + 0.4 * q, 0, al, guard=True); return
    # above you, tucked behind your head: your hair overlaps only the bottom edge
    cy = max(c.H * 0.08 + ch / 2, c.fy - c.fw * 0.95 + c.fw * float(e.o.get('overlap', 0.08)) - ch / 2)
    place(c, im, c.W / 2, cy + (1 - q) * c.W * 0.04, 0.6 + 0.4 * q, 0, al, behind=True)
