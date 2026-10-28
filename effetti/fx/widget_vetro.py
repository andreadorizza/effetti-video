"""widget-vetro (glass-widgets): Widget di vetro e mini artefatti fluttuano intorno alla testa, con la pillola Montato con Claude.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def glass_widgets_v1(c, e):
    k0 = ramp(c, e, 0.3, 0)
    if e.o.get('grade', 'warm') != 'none': c.img = c.img * (1 - 0.6 * k0) + grade(c.img, e.o.get('grade', 'warm')) * 0.6 * k0
    al = fade(c, e); W = c.W; mg = W * 0.055
    S = W * 0.31; y_top = c.H * 0.07
    gd = float(e.o.get('dark', 0.2))
    ink = 'on-dark' if gd >= 0.3 else 'on-surface'   # without glass, glass() draws a dark card from dark=0.3 up
    white = P.c(ink, (255, 255, 255))
    a = glass(c, S, S, S * 0.2, mg + S / 2, y_top + S / 2, amt=0.14, dark=gd); d = ImageDraw.Draw(a)
    d.ellipse([S * 0.1, S * 0.115, S * 0.1 + S * 0.06, S * 0.115 + S * 0.06], fill=P.c('accent', ORANGE) + (255,))
    d.text((S * 0.2, S * 0.145), e.o.get('title', 'Claude'), font=font('uim', S * 0.085), fill=white + (235,), anchor='lm')
    d.text((S * 0.08, S * 0.2), e.o.get('text', '22'), font=font('uib', S * 0.44), fill=white + (255,))
    for j, ln in enumerate(e.o.get('sub', tr('effetti|una clip', 'effects|one clip')).split('|')):
        d.text((S * 0.1, S * (0.7 + 0.11 * j)), ln, font=font('uim', S * 0.085), fill=white + (235,))
    place(c, a, mg + S / 2, y_top + S / 2, 0.6 + 0.4 * pop(c, 0.0), 0, al * clamp(c.lt / 0.1), behind=True)
    bw, bh = W * 0.37, W * 0.15; bx = W - mg - bw / 2
    b = glass(c, bw, bh, bh * 0.28, bx, y_top + bh / 2, amt=0.14, dark=gd); d = ImageDraw.Draw(b)
    d.ellipse([bh * 0.17, bh * 0.2, bh * 0.17 + bh * 0.11, bh * 0.31], fill=P.c('danger', (255, 69, 58), 255))
    d.text((bh * 0.36, bh * 0.255), tr('Esportazione', 'Rendering'), font=font('uim', bh * 0.19), fill=white + (240,), anchor='lm')
    p = ease_inout(c.lt / max(0.3, e.d * 0.85))
    d.rounded_rectangle([bh * 0.17, bh * 0.5, bw - bh * 0.17, bh * 0.6], P.r(bh * 0.05), fill=P.c('line', (255, 255, 255), 70))
    d.rounded_rectangle([bh * 0.17, bh * 0.5, bh * 0.17 + (bw - bh * 0.34) * max(0.04, p), bh * 0.6], P.r(bh * 0.05), fill=white + (245,))
    d.text((bh * 0.17, bh * 0.78), f"{e.o.get('label', tr('UI in vetro', 'glass UI'))}  ·  {int(p * 100)}%", font=font('uim', bh * 0.14), fill=white + (210,), anchor='lm')
    place(c, b, bx, y_top + bh / 2, 0.6 + 0.4 * pop(c, 0.12), 0, al * clamp((c.lt - 0.12) / 0.1), behind=True)
    cy2 = y_top + bh + mg * 0.45 + bh / 2
    g = glass(c, bw, bh, bh * 0.28, bx, cy2, amt=0.14, dark=gd); d = ImageDraw.Draw(g)
    av = face_chip(c, e, bh * 0.62); g.alpha_composite(av, (int(bw - bh * 0.19 - av.width), int((bh - av.height) / 2)))
    d.text((bh * 0.2, bh * 0.36), e.o.get('name', tr('Il tuo nome', 'Vibha')), font=font('uib', bh * 0.22), fill=white + (255,), anchor='lm')
    d.text((bh * 0.2, bh * 0.66), e.o.get('handle', tr('@il.tuo.profilo', '@vibha.in.progress')), font=font('uim', bh * 0.14), fill=white + (215,), anchor='lm')
    place(c, g, bx, cy2, 0.6 + 0.4 * pop(c, 0.24), 0, al * clamp((c.lt - 0.24) / 0.1), behind=True)
    f1, f2 = font('uim', W * 0.045), font('uib', W * 0.045)
    pill = e.o.get('pill', tr('Montato con |Claude', 'Edited by |Claude'))
    pre, hi = pill.split('|') if '|' in pill else (pill, '')
    tw = f1.getlength(pre) + f2.getlength(hi); ph = W * 0.105; pw = tw + ph * 0.9; py = c.H * 0.865
    q = glass(c, pw, ph, ph / 2, W / 2, py, amt=0.16, tint=(70, 70, 76)); d = ImageDraw.Draw(q)
    d.text(((pw - tw) / 2, ph / 2), pre, font=f1, fill=on_glass((255, 255, 255), 255), anchor='lm')
    d.text(((pw - tw) / 2 + f1.getlength(pre), ph / 2), hi, font=f2, fill=P.c('accent', (255, 176, 146), 255), anchor='lm')
    place(c, shadowed(q, 14, 6, 70), W / 2, py, 0.7 + 0.3 * pop(c, 0.4), 0, al * clamp((c.lt - 0.4) / 0.1), guard=True)


def glass_widgets_v2(c, e):
    """More widgets, artifact-style: stat tile, render bar, profile, a mini views artifact, now-playing, calendar, a 4K ring and the Edited by Claude pill."""
    W, H = c.W, c.H; u = W / 1080
    k0 = ramp(c, e, 0.3, 0)
    if e.o.get('grade', 'warm') != 'none': c.img = c.img * (1 - 0.6 * k0) + grade(c.img, e.o.get('grade', 'warm')) * 0.6 * k0
    al = fade(c, e); gd = float(e.o.get('dark', 0.22))
    white = P.c('on-dark', (255, 255, 255)) if gd >= 0.3 else on_glass((255, 255, 255))   # text and marks on the glass (a card without glass)
    track = P.c('line', (255, 255, 255))
    def bob(i): return 6 * u * math.sin(2 * math.pi * (c.lt * 0.55 + i * 0.17))
    def show(im, x, y, i, front=False):
        t0 = 0.07 * i
        if c.lt < t0: return
        place(c, im, x, y + bob(i), 0.6 + 0.4 * pop(c, t0, 0.32), 0, al * clamp((c.lt - t0) / 0.08), behind=not front, guard=front)
    G = lambda w, h, cx, cy, r=None: glass(c, w, h, r or min(w, h) * 0.2, cx, cy, amt=0.14, dark=gd)
    # 1 · stat tile
    S = 300 * u; ax, ay = 50 * u + S / 2, 118 * u + S / 2
    a = G(S, S, ax, ay); d = ImageDraw.Draw(a)
    d.ellipse([S * 0.1, S * 0.115, S * 0.16, S * 0.175], fill=P.c('accent', ORANGE) + (255,))
    d.text((S * 0.2, S * 0.145), e.o.get('title', 'Claude'), font=font('uim', S * 0.085), fill=white + (235,), anchor='lm')
    d.text((S * 0.08, S * 0.2), e.o.get('text', '38'), font=font('uib', S * 0.44), fill=white + (255,))
    for j, ln in enumerate(e.o.get('sub', tr('effetti|una clip', 'effects|one clip')).split('|')): d.text((S * 0.1, S * (0.7 + 0.11 * j)), ln, font=font('uim', S * 0.085), fill=white + (235,))
    show(a, ax, ay, 0)
    # 2 · render bar
    bw, bh = 400 * u, 150 * u; bx, by = W - 50 * u - bw / 2, 118 * u + bh / 2
    b = G(bw, bh, bx, by, bh * 0.28); d = ImageDraw.Draw(b); p = ease_inout(c.lt / max(0.3, e.d * 0.85))
    d.ellipse([bh * 0.17, bh * 0.2, bh * 0.28, bh * 0.31], fill=P.c('danger', (255, 69, 58), 255))
    d.text((bh * 0.36, bh * 0.255), tr('Esportazione', 'Rendering'), font=font('uim', bh * 0.19), fill=white + (240,), anchor='lm')
    d.rounded_rectangle([bh * 0.17, bh * 0.5, bw - bh * 0.17, bh * 0.6], P.r(bh * 0.05), fill=track + (70,))
    d.rounded_rectangle([bh * 0.17, bh * 0.5, bh * 0.17 + (bw - bh * 0.34) * max(0.04, p), bh * 0.6], P.r(bh * 0.05), fill=white + (245,))
    d.text((bh * 0.17, bh * 0.78), f"{tr('render 4K', '4K render')}  ·  {int(p * 100)}%", font=font('uim', bh * 0.14), fill=white + (210,), anchor='lm')
    show(b, bx, by, 1)
    # 3 · profile
    cy3 = by + bh / 2 + 22 * u + bh / 2
    g = G(bw, bh, bx, cy3, bh * 0.28); d = ImageDraw.Draw(g)
    av = face_chip(c, e, bh * 0.62); g.alpha_composite(av, (int(bw - bh * 0.19 - av.width), int((bh - av.height) / 2)))
    d.text((bh * 0.2, bh * 0.36), e.o.get('name', tr('Il tuo nome', 'Vibha')), font=font('uib', bh * 0.22), fill=white + (255,), anchor='lm')
    d.text((bh * 0.2, bh * 0.66), e.o.get('handle', tr('@il.tuo.profilo', '@vibha.in.progress')), font=font('uim', bh * 0.14), fill=white + (215,), anchor='lm')
    show(g, bx, cy3, 2)
    # 4 · views artifact (a mini page inside the glass)
    aw, ah = 330 * u, 330 * u; dx, dy = 50 * u + aw / 2, ay + S / 2 + 26 * u + ah / 2
    art = G(aw, ah, dx, dy, 44 * u); d = ImageDraw.Draw(art)
    d.text((24 * u, 30 * u), tr('artefatto · views.html', 'artifact · views.html'), font=font('mono', 15 * u), fill=white + (220,), anchor='lm')
    inn = rrect(aw - 36 * u, ah - 74 * u, 20 * u, P.c('surface', (250, 248, 244), 255),
                outline=None if P.glass else P.c('line', (255, 255, 255), 255), width=0 if P.glass else max(2, c.W // 540))
    di = ImageDraw.Draw(inn); iw, ih = inn.size
    for j in range(3): di.ellipse([14 * u + j * 16 * u, 14 * u, 24 * u + j * 16 * u, 24 * u], fill=(P.c('danger', (255, 95, 87)), P.c('accent2', (255, 189, 46)), P.c('success', (40, 200, 64)))[j] + (255,))
    di.text((16 * u, 40 * u), tr('Reel migliori', 'Top reels'), font=font('uib', 26 * u), fill=P.c('on-surface', (24, 22, 26), 255))
    di.text((16 * u, 72 * u), '197K', font=font('anton', 44 * u), fill=P.c('accent', (200, 85, 61), 255, on='surface'))
    vals = [197, 140, 124, 83, 50, 40, 38]; gx0, gx1, gy1 = 16 * u, iw - 16 * u, ih - 18 * u; bwid = (gx1 - gx0) / 7 * 0.66
    for j, v in enumerate(vals):
        q = ease_out((c.lt - 0.35 - 0.05 * j) / 0.4); hh = (ih * 0.42) * v / 197 * q; x0 = gx0 + (gx1 - gx0) * j / 7
        if hh > 1: di.rounded_rectangle([x0, gy1 - hh, x0 + bwid, gy1], P.r(5 * u), fill=(P.c('accent2', (242, 196, 109)) if j == 0 else P.c('accent', (200, 85, 61))) + (255,))
    art.alpha_composite(inn, (int(18 * u), int(56 * u)))
    show(art, dx, dy, 3)
    # 5 · now playing
    mw, mh = 360 * u, 220 * u; mx, my = W - 50 * u - mw / 2, cy3 + bh / 2 + 22 * u + mh / 2
    mu = G(mw, mh, mx, my, 40 * u); d = ImageDraw.Draw(mu); A = 96 * u
    t = np.linspace(0, 1, int(A), dtype=np.float32)[:, None, None]
    top, bot = P.c('accent', (255, 150, 110)), P.c('accent', (217, 90, 70))
    if not P.gradients: top = bot
    art2 = Image.fromarray(np.concatenate([(np.float32(top) * (1 - t) + np.float32(bot) * t) * np.ones((1, int(A), 1), np.float32), np.full((int(A), int(A), 1), 255, np.float32)], 2).astype(np.uint8), 'RGBA')
    am = Image.new('L', art2.size, 0); ImageDraw.Draw(am).rounded_rectangle([0, 0, art2.width - 1, art2.height - 1], P.r(16 * u), fill=255); art2.putalpha(am)
    ad = ImageDraw.Draw(art2)
    for k_ in range(6):
        ang = k_ * math.pi / 3; ad.line([(A / 2 - 26 * u * math.cos(ang), A / 2 - 26 * u * math.sin(ang)), (A / 2 + 26 * u * math.cos(ang), A / 2 + 26 * u * math.sin(ang))], fill=P.c('on-accent', (255, 255, 255), 255), width=int(7 * u))
    mu.alpha_composite(art2, (int(22 * u), int(22 * u)))
    d.text((134 * u, 44 * u), tr('IN MONTAGGIO', 'NOW EDITING'), font=font('mono', 15 * u), fill=white + (200,), anchor='lm')
    d.text((134 * u, 78 * u), e.o.get('song', tr('clic morbidi', 'soft UI pops')), font=font('uib', 28 * u), fill=white + (255,), anchor='lm')
    d.text((134 * u, 108 * u), 'sfx · 25.7s', font=font('uim', 20 * u), fill=white + (200,), anchor='lm')
    pp = clamp(c.lt / max(0.5, e.d)); d.rounded_rectangle([22 * u, 140 * u, mw - 22 * u, 146 * u], P.r(3 * u), fill=track + (70,))
    d.rounded_rectangle([22 * u, 140 * u, 22 * u + (mw - 44 * u) * pp, 146 * u], P.r(3 * u), fill=white + (240,))
    cxm, cym = mw / 2, 184 * u
    d.polygon([(cxm - 12 * u, cym - 16 * u), (cxm - 12 * u, cym + 16 * u), (cxm + 16 * u, cym)], fill=white + (255,))
    for sgn in (-1, 1):
        x = cxm + sgn * 80 * u
        d.polygon([(x - sgn * 10 * u, cym - 11 * u), (x - sgn * 10 * u, cym + 11 * u), (x + sgn * 6 * u, cym)], fill=white + (220,))
        d.polygon([(x + sgn * 4 * u, cym - 11 * u), (x + sgn * 4 * u, cym + 11 * u), (x + sgn * 20 * u, cym)], fill=white + (220,))
    show(mu, mx, my, 4)
    # 6 · calendar
    kw, kh = 330 * u, 190 * u; kx, ky = 50 * u + kw / 2, dy + ah / 2 + 26 * u + kh / 2
    ca = G(kw, kh, kx, ky, 40 * u); d = ImageDraw.Draw(ca)
    d.text((26 * u, 36 * u), e.o.get('day', tr('MER', 'WED')), font=font('uib', 22 * u), fill=P.c('accent', (255, 92, 82), 255), anchor='lm')
    d.text((26 * u, 82 * u), e.o.get('date', '21'), font=font('uib', 56 * u), fill=white + (255,), anchor='lm')
    d.rounded_rectangle([22 * u, 120 * u, kw - 22 * u, 168 * u], P.r(12 * u), fill=P.c('accent', (255, 92, 82), 210))
    d.text((36 * u, 144 * u), e.o.get('event', tr('Posta 2 reel · stasera', 'Post 2 reels · tonight')), font=font('uib', 22 * u), fill=P.c('on-accent', (255, 255, 255), 255), anchor='lm')
    show(ca, kx, ky, 5)
    # 7 · 4K ring
    R = 250 * u; rx, ry = W - 50 * u - R / 2, my + mh / 2 + 26 * u + R / 2
    rg = G(R, R, rx, ry, 56 * u); d = ImageDraw.Draw(rg); rp = ease_inout((c.lt - 0.4) / 1.0); rr = R * 0.34
    d.ellipse([R / 2 - rr, R / 2 - rr - 8 * u, R / 2 + rr, R / 2 + rr - 8 * u], outline=track + (60,), width=int(16 * u))
    if rp > 0: d.arc([R / 2 - rr, R / 2 - rr - 8 * u, R / 2 + rr, R / 2 + rr - 8 * u], -90, -90 + 360 * rp, fill=P.c('success', (52, 199, 89), 255), width=int(16 * u))
    d.text((R / 2, R / 2 - 8 * u), '4K', font=font('uib', 52 * u), fill=white + (255,), anchor='mm')
    d.text((R / 2, R - 26 * u), 'render', font=font('uim', 20 * u), fill=white + (210,), anchor='mm')
    show(rg, rx, ry, 6)
    # 8 · Edited by Claude pill (in front)
    f1, f2 = font('uim', W * 0.045), font('uib', W * 0.045); pre, hi = tr('Montato con ', 'Edited by '), 'Claude'
    tw = f1.getlength(pre) + f2.getlength(hi); ph = W * 0.105; pw = tw + ph * 0.9; py = H * 0.875
    q = glass(c, pw, ph, ph / 2, W / 2, py, amt=0.16, tint=(70, 70, 76)); d = ImageDraw.Draw(q)
    d.text(((pw - tw) / 2, ph / 2), pre, font=f1, fill=on_glass((255, 255, 255), 255), anchor='lm')
    d.text(((pw - tw) / 2 + f1.getlength(pre), ph / 2), hi, font=f2, fill=P.c('accent', (255, 176, 146), 255), anchor='lm')
    show(shadowed(q, 14, 6, 70), W / 2, py, 7, front=True)


@effetto('widget-vetro', en='glass-widgets', alias=('glass', 'glass-widgets', 'vetro', 'widget', 'widgets'),
         desc='Widget di vetro e mini artefatti fluttuano intorno alla testa, con la pillola Montato con Claude')
def fx_glass_widgets(c, e):
    (glass_widgets_v1 if e.o.get('look') == 'simple' else glass_widgets_v2)(c, e)
