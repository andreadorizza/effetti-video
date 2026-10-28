"""grafico-vetro (liquid-glass-graph): Una scheda di vetro liquido sotto il mento: un grafico sale mentre il numero conta.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def num_parts(s):
    """'197K' -> (197.0, 'K', 0 decimals); '59%' -> (59.0, '%', 0); '4.8' -> (4.8, '', 1)."""
    s = str(s).strip(); i = len(s)
    while i and not (s[i - 1].isdigit()): i -= 1
    n = decimal_comma(s[:i]) or '0'   # '4,8' is read as 4.8, '197,000' as 197000
    return float(n), s[i:], (len(n.split('.')[1]) if '.' in n else 0)


def donut(size, pct, col, label, value):
    """A ring chart for a dark tile (its text is on-dark)."""
    S = int(size) * 2; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = int(S * 0.1); pad = int(S * 0.08)
    ink = P.c('on-dark', (255, 255, 255))
    d.arc([pad, pad, S - pad, S - pad], 0, 360, fill=P.c('line', (255, 255, 255), 46), width=w)
    if pct > 0.002: d.arc([pad, pad, S - pad, S - pad], -90, -90 + 360 * pct, fill=tuple(col) + (255,), width=w)
    f = font('uib', S * 0.2); d.text((S / 2, S / 2 - S * 0.02), value, font=f, fill=ink + (255,), anchor='mm')
    f2 = fontfor('mono', S * 0.065, label.upper()); d.text((S / 2, S / 2 + S * 0.15), label.upper(), font=f2, fill=ink + (170,), anchor='mm')
    return im.resize((int(size), int(size)), Image.LANCZOS)


def glass_bento(c, e):
    W, H = c.W, c.H; al = fade(c, e) * clamp(c.lt / 0.12)
    if al <= 0: return
    green = rgb(e.o.get('color'), P.c('success', (52, 211, 110), on='dark')); peach = P.c('accent2', (255, 160, 122), on='dark')
    ink = P.c('on-dark', (255, 255, 255))   # the panel and the tiles are dark glass (dark cards without glass)
    # 1. the big graph, on a smoked glass screen behind you
    q = ease_out(c.lt / 0.4); pw, ph = int(W * 0.9), int(H * 0.3); pcx, pcy = W / 2, H * 0.08 + ph / 2 + (1 - q) * H * 0.02
    pan = glass(c, pw, ph, W * 0.04, pcx, pcy, amt=0.06, dark=0.62, blur=max(10, W // 30))
    lay = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); pad = pw * 0.05
    g = ease_inout((c.lt - 0.2) / max(0.3, e.d * 0.75))
    lab = e.o.get('text', tr('VISUALIZZAZIONI', 'VIEWS')).upper()
    d.text((pad, pad * 0.8), lab, font=fontfor('mono', pw * 0.026, lab), fill=ink + (180,))
    a, _, _ = num_parts(e.o.get('from', '0')); b, suf, dp = num_parts(e.o.get('to', '197K')); s = num(f'{a + (b - a) * g:.{dp}f}') + suf
    f = font('uib', pw * 0.085); d.text((pw - pad - f.getlength(s), pad * 0.45), s, font=f, fill=ink + (255,))
    x0, x1, y0, y1 = pad, pw - pad, ph - pad * 0.8, ph * 0.3
    for j in range(1, 4): yy = y0 - (y0 - y1) * j / 3.3; d.line([(x0, yy), (x1, yy)], fill=P.c('line', (255, 255, 255), 34), width=max(1, W // 1000))
    n = 80; pts = [(x0 + (x1 - x0) * j / n, y0 - (y0 - y1) * ((j / n) ** 1.7) + math.sin(j / n * 17) * ph * 0.02 * (1 - j / n)) for j in range(int(n * g) + 1)]
    if len(pts) > 1:
        area = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); ImageDraw.Draw(area).polygon(pts + [(pts[-1][0], y0), (x0, y0)], fill=green + (60,)); lay.alpha_composite(area)
        lw = max(4, int(pw * 0.006)); gl = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts, fill=green + (255,), width=lw * 3, joint='curve')
        if P.glow: lay.alpha_composite(gl.filter(ImageFilter.GaussianBlur(lw * 2)))
        ImageDraw.Draw(lay).line(pts, fill=green + (255,), width=lw, joint='curve')
        hx, hy = pts[-1]; r = lw * 2; ImageDraw.Draw(lay).ellipse([hx - r, hy - r, hx + r, hy + r], fill=ink + (255,), outline=green + (255,), width=lw // 2)
    pan.alpha_composite(lay)
    place(c, pan, pcx, pcy, alpha=al * q, behind=True)
    # 2. the bento tiles in front of you
    def tile(i, cx, cy, tw, th, draw):
        k = pop(c, 0.15 + 0.12 * i, 0.4)
        if k <= 0: return
        t = glass(c, tw, th, W * 0.035, cx, cy, amt=0.08, dark=0.5, blur=max(10, W // 34))
        draw(t, ImageDraw.Draw(t), tw, th); place(c, shadowed(t, max(8, W // 80), W // 120, 90), cx, cy, 0.7 + 0.3 * k, 0, al * clamp(k * 2))
    dv, dl = (e.o.get('donut', tr('29%::quota ERASE', '29%::ERASE share')).split('::') + [''])[:2]; pct = num_parts(dv)[0] / 100
    def dr_donut(t, d, tw, th):
        p = ease_out((c.lt - 0.35) / 0.8) * pct
        dn = donut(tw * 0.86, p, peach, dl, f'{round(p * 100)}%'); t.alpha_composite(dn, (int((tw - dn.width) / 2), int((th - dn.height) / 2)))
    kv, kl = (e.o.get('kpi', tr('672K::views · top 7 reel', '672K::views · top 7 reels')).split('::') + [''])[:2]
    def dr_kpi(t, d, tw, th):
        b, suf, dp = num_parts(kv); v = b * ease_out((c.lt - 0.45) / 0.8)
        d.text((tw * 0.1, th * 0.18), num(f'{v:.{dp}f}') + suf, font=font('uib', th * 0.36), fill=ink + (255,))
        d.text((tw * 0.1, th * 0.7), kl.upper(), font=fontfor('mono', th * 0.1, kl.upper()), fill=ink + (170,))
    bv, bl = (e.o.get('bars', tr('197|140|124|83|50::top reel · K views', '197|140|124|83|50::top reels · K views')).split('::') + [''])[:2]; vals = [num_parts(v)[0] for v in bv.split('|')]
    def dr_bars(t, d, tw, th):
        d.text((tw * 0.1, th * 0.06), bl.upper(), font=fontfor('mono', tw * 0.055, bl.upper()), fill=ink + (170,))
        n = len(vals); bw = tw * 0.8 / n; top, base = th * 0.2, th * 0.88; mx = max(vals)
        for j, v in enumerate(vals):
            kk = ease_out((c.lt - 0.4 - 0.08 * j) / 0.5); hgt = (base - top) * v / mx * kk; x = tw * 0.1 + j * bw
            d.rounded_rectangle([x + bw * 0.14, base - hgt, x + bw * 0.86, base], int(P.r(bw * 0.18)), fill=(green if j == 0 else ink) + (255 if j == 0 else 150,))
            if kk > 0.6: d.text((x + bw / 2, base - hgt - tw * 0.02), num(f'{v:g}'), font=font('uib', tw * 0.06), fill=ink + (230,), anchor='md')
    tw = W * 0.25; gap = W * 0.02; ty = max(H * 0.5, c.fy + c.fw * 1.1)
    tile(0, W * 0.15, ty + tw * 0.5, tw, tw, dr_donut)
    tile(1, W * 0.15, ty + tw + gap + tw * 0.28, tw, tw * 0.56, dr_kpi)
    tile(2, W * 0.85, ty + tw * 0.65, tw, tw * 1.3, dr_bars)


@effetto('grafico-vetro', en='liquid-glass-graph', alias=('glass-graph', 'grafico', 'liquid-glass', 'liquid-glass-graph'),
         desc='Una scheda di vetro liquido sotto il mento: un grafico sale mentre il numero conta')
def fx_liquid_glass_graph(c, e):
    if e.o.get('look') == 'bento': return glass_bento(c, e)
    q = ease_out(c.lt / 0.4); al = fade(c, e) * clamp(c.lt / 0.12)
    if al <= 0: return
    W = c.W; cw, ch = int(W * 0.74), int(W * 0.46); sc = 0.88 + 0.12 * q
    cx = W / 2; cy = min(c.H - ch * 0.62, c.fy + c.fw * 2.7) + (1 - q) * W * 0.08
    gw, gh = int(cw * sc), int(ch * sc)
    im = glass(c, gw, gh, gh * 0.12, cx, cy, amt=0.16, blur=max(10, W // 30), dark=0.12)
    if P.glass and P.gradients:   # the sheen on the glass
        hi = cached(e, ('hi', gw, gh), lambda: Image.fromarray(np.dstack([np.full((gh, gw, 3), 255, np.uint8),
            (np.clip(1 - np.linspace(0, 1, gh) * 2.2, 0, 1)[:, None] * np.ones(gw) * 46).astype(np.uint8)]), 'RGBA'))
        hm = Image.new('L', (gw, gh), 0); ImageDraw.Draw(hm).rounded_rectangle([0, 0, gw - 1, gh - 1], int(P.r(gh * 0.12)), fill=255)
        hl = hi.copy(); hl.putalpha(Image.fromarray(np.minimum(np.asarray(hi)[..., 3], np.asarray(hm)))); im.alpha_composite(hl)
    ink = P.c('on-surface', (255, 255, 255))   # light glass (a light card without glass)
    lay = Image.new('RGBA', (gw, gh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); pad = gw * 0.07
    g = ease_inout((c.lt - 0.25) / max(0.3, e.d * 0.72))
    lab = e.o.get('text', tr('FIDELIZZAZIONE', 'RETENTION')).upper()
    d.text((pad, pad * 0.9), lab, font=fontfor('mono', gw * 0.04, lab), fill=ink + (190,))
    a, _, _ = num_parts(e.o.get('from', '0')); b, suf, dp = num_parts(e.o.get('to', '59%'))
    v = a + (b - a) * g; s = num(f'{v:.{dp}f}') + suf
    f = font('uib', gw * 0.12); d.text((gw - pad - f.getlength(s), pad * 0.55), s, font=f, fill=ink + (255,))
    x0, x1, y0, y1 = pad, gw - pad, gh - pad * 0.9, gh * 0.36
    def ycurve(u): return y0 - (y0 - y1) * (u ** 1.5) + math.sin(u * 13) * gh * 0.018 * (1 - u)
    n = 60; pts = [(x0 + (x1 - x0) * j / n, ycurve(j / n)) for j in range(int(n * g) + 1)]
    green = rgb(e.o.get('color'), P.c('success', (52, 211, 110)))
    if len(pts) > 1:
        area = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
        ImageDraw.Draw(area).polygon(pts + [(pts[-1][0], y0), (x0, y0)], fill=green + (55,)); lay.alpha_composite(area)
        glow = Image.new('RGBA', (gw, gh), (0, 0, 0, 0)); lw = max(4, int(gw * 0.011))
        ImageDraw.Draw(glow).line(pts, fill=green + (255,), width=lw * 3, joint='curve')
        if P.glow: lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(lw * 2)))
        ImageDraw.Draw(lay).line(pts, fill=green + (255,), width=lw, joint='curve')
        hx, hy = pts[-1]; r = lw * 1.9
        ImageDraw.Draw(lay).ellipse([hx - r, hy - r, hx + r, hy + r], fill=P.c('surface', (255, 255, 255), 255), outline=green + (255,), width=max(2, lw // 2))
    for j in range(1, 4):
        yy = y0 - (y0 - y1) * j / 3.4
        d.line([(x0, yy), (x1, yy)], fill=P.c('line', (255, 255, 255), 40), width=max(1, int(gw * 0.002)))
    im.alpha_composite(lay)
    place(c, shadowed(im, max(10, W // 70), W // 90, 90), cx, cy, alpha=al, guard=True)
