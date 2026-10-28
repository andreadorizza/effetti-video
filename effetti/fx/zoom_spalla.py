"""zoom-spalla (over-the-shoulder-zoom): La camera entra in un angolo in alto e accanto alla testa compare un grafico di vetro liquido, poi l'altro angolo con un secondo grafico.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *
from ..i18n import num as num_text


def liquid_glass(c, box, r=None, blur=None):
    """Liquid glass panel on c.img, after liquid-glass-js (MIT, dashersw): rounded-rect SDF, edge + rim refraction
    along the normal, a light blur so the room still shows through, a faint top-to-bottom tint, a specular rim lit
    from the top-left, plus a red/blue fringe at the edge (after React Bits' GlassSurface)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]; w, h = x1 - x0, y1 - y0
    if w < 8 or h < 8: return
    u = c.W / 2160; r = r or 72 * u; M = int(140 * u)
    if not P.glass:   # a theme without glass: a flat card in its own colours, as glass() draws it (a light one, like glass() below dark=0.3)
        comp(c, rrect(w, h, r, P.c('surface', (255, 255, 255), 240), outline=P.c('line', (255, 255, 255), 255), width=max(2, c.W // 540)), x0, y0)
        return
    X0, Y0, X1, Y1 = max(0, x0 - M), max(0, y0 - M), min(c.W, x1 + M), min(c.H, y1 + M)
    tex = cv2.GaussianBlur(c.img[Y0:Y1, X0:X1], (0, 0), blur or 7 * u)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    q = np.stack([np.abs(xx - w / 2) - (w / 2 - r), np.abs(yy - h / 2) - (h / 2 - r)], -1)
    sdf = np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.maximum(q[..., 0], q[..., 1]), 0) - r
    d = np.maximum(-sdf, 0) / u
    nx, ny = xx - w / 2, yy - h / 2; nl = np.sqrt(nx * nx + ny * ny) + 1e-3; nx, ny = nx / nl, ny / nl
    k = (70 * np.exp(-d / 14) + 34 * np.exp(-d / 70) + 10 * np.exp(-d / 260)) * u
    out = np.zeros((h, w, 3), np.float32)
    for ch, fr in enumerate((1.10, 1.0, 0.90)):
        mx = (xx + x0 - X0 + nx * k * fr).astype(np.float32); my = (yy + y0 - Y0 + ny * k * fr).astype(np.float32)
        out[..., ch] = cv2.remap(tex[..., ch], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    out = out * 0.86 + 0.06 * (1.0 - 0.30 * (yy / h))[..., None] - 0.05
    spec = np.exp(-d / 5) * np.clip(0.55 - 0.45 * (nx * 0.6 + ny * 0.8), 0, 1)
    out = np.clip(out + (spec * 0.85 + np.exp(-d / 30) * 0.10)[..., None], 0, 1)
    a = np.clip(0.5 - sdf, 0, 1)[..., None]
    gx0, gy0, gx1, gy1 = max(0, x0), max(0, y0), min(c.W, x1), min(c.H, y1)
    sl = (slice(gy0 - y0, gy1 - y0), slice(gx0 - x0, gx1 - x0))
    dst = c.img[gy0:gy1, gx0:gx1]; dst[:] = dst * (1 - a[sl]) + out[sl] * a[sl]


def split_num(s):
    """'197K' -> (197.0, 'K', 0 decimals); '82%' -> (82.0, '%', 0); '1.2M' -> (1.2, 'M', 1)."""
    import re as _re
    m = _re.match(r'\s*([\d.,]+)\s*(.*)', str(s)); n = decimal_comma(m.group(1)) if m else '0'
    return float(n), (m.group(2) if m else ''), (len(n.split('.')[1]) if '.' in n else 0)


def glass_graph(c, cx, cy, k, prog, label, value, kind, scale=1.0):
    """A see-through glass stat card: spaced-caps label, a number that counts up, a glowing line or bar chart."""
    if k <= 0: return
    u = c.W / 2160 * scale; sc = 0.82 + 0.18 * ease_back(k)
    w, h = 1760 * u * sc, 1056 * u * sc; lift = 40 * u * (1 - k)
    x0, y0 = cx - w / 2, cy - h / 2 + lift
    liquid_glass(c, (x0, y0, x0 + w, y0 + h))
    v = w / 1500
    lay = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = 20
    lab, big = fontfor('uim', 44 * v, label.upper()), font('uib', 170 * v)
    num, suf, dec = split_num(value); txt = num_text(f'{num * ease_out(prog):.{dec}f}') + suf
    xx = o + 64 * v
    ink = P.c('on-surface', (255, 255, 255))   # on the glass (a surface card without glass)
    for chh in label.upper(): d.text((xx, o + 64 * v), chh, font=lab, fill=ink + (235,)); xx += lab.getlength(chh) + 9 * v
    d.text((o + w - 70 * v - big.getlength(txt), o + 40 * v), txt, font=big, fill=ink + (255,))
    gx0, gx1, gy0, gy1 = o + 64 * v, o + w - 64 * v, o + 290 * v, o + h - 80 * v
    for j in range(3): d.line([gx0, gy0 + (gy1 - gy0) * j / 2, gx1, gy0 + (gy1 - gy0) * j / 2], fill=P.c('line', (255, 255, 255), 70), width=max(1, int(3 * v)))
    halo = Image.new('RGBA', lay.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(halo)
    xx = o + 64 * v
    for chh in label.upper(): hd.text((xx, o + 64 * v), chh, font=lab, fill=(0, 0, 0, 150)); xx += lab.getlength(chh) + 9 * v
    hd.text((o + w - 70 * v - big.getlength(txt), o + 40 * v), txt, font=big, fill=(0, 0, 0, 150))
    base = halo.filter(ImageFilter.GaussianBlur(10 * v)) if P.shadows else Image.new('RGBA', lay.size, (0, 0, 0, 0))   # the soft shadow behind the text
    chart = Image.new('RGBA', lay.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(chart); green = P.c('success', GREEN)
    if kind == 'line':
        ys = [0.04, 0.07, 0.10, 0.16, 0.22, 0.35, 0.52, 0.74, 1.0]; n = max(0.02, (len(ys) - 1) * ease_out(prog)); pts = []
        for i in range(int(n) + 1):
            t = min(i, n); i0 = min(int(t), len(ys) - 2); f = t - i0; yv = ys[i0] + (ys[i0 + 1] - ys[i0]) * f
            pts.append((gx0 + (gx1 - gx0) * t / (len(ys) - 1), gy1 - (gy1 - gy0) * yv))
        if len(pts) > 1:
            cd.polygon(pts + [(pts[-1][0], gy1), (pts[0][0], gy1)], fill=green + (70,))
            if P.glow:
                gl = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts, fill=green + (255,), width=int(60 * v), joint='curve')
                chart.alpha_composite(gl.filter(ImageFilter.GaussianBlur(26 * v)))
            cd = ImageDraw.Draw(chart); cd.line(pts, fill=green + (255,), width=max(2, int(20 * v)), joint='curve')
            ex, ey = pts[-1]
            cd.ellipse([ex - 30 * v, ey - 30 * v, ex + 30 * v, ey + 30 * v], fill=green + (90,)); cd.ellipse([ex - 15 * v, ey - 15 * v, ex + 15 * v, ey + 15 * v], fill=P.c('surface', (235, 255, 240), 255))
    else:
        vals = [1.0, 0.71, 0.63, 0.42, 0.25, 0.20, 0.19]; bw = (gx1 - gx0) / len(vals)
        for i, val in enumerate(vals):
            g = ease_out(clamp(prog * 1.6 - i * 0.1)); top = gy1 - (gy1 - gy0) * val * g; bx = gx0 + i * bw + bw * 0.16
            if i == 0 and P.glow:
                gl = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle([bx, top, bx + bw * 0.68, gy1], int(P.r(18 * v)), fill=green + (230,))
                chart.alpha_composite(gl.filter(ImageFilter.GaussianBlur(22 * v))); cd = ImageDraw.Draw(chart)
            cd.rounded_rectangle([bx, top, bx + bw * 0.68, gy1], int(P.r(18 * v)), fill=green + (230 if i == 0 else 120,))
    base.alpha_composite(chart); base.alpha_composite(lay)
    comp(c, base, x0 - o, y0 - o)


@effetto('zoom-spalla', en='over-the-shoulder-zoom', alias=('angolo', 'corner-zoom', 'ots', 'over-the-shoulder-zoom', 'shoulder-zoom'),
         desc="La camera entra in un angolo in alto e accanto alla testa compare un grafico di vetro liquido, poi l'altro angolo con un secondo grafico")
def fx_over_the_shoulder_zoom(c, e):
    p = clamp(c.lt / e.d); z0 = float(e.o.get('zoom', 2.0))
    lx, rx = c.fx - c.W * 0.17, c.fx + c.W * 0.19
    keys = [(0, 1.0, c.fx, c.fy), (0.30, 1.04, c.fx, c.fy), (0.46, z0, lx, c.fy), (0.66, z0 + 0.04, lx, c.fy), (0.76, 1.05, c.fx, c.fy), (0.87, z0, rx, c.fy), (1.0, z0 + 0.04, rx, c.fy)]
    for (pa, za, xa, ya), (pb, zb, xb, yb) in zip(keys, keys[1:]):
        if pa <= p <= pb: q = ease_inout((p - pa) / (pb - pa)); z, x, y = za + (zb - za) * q, xa + (xb - xa) * q, ya + (yb - ya) * q; break
    camera(c, z, x, y)
    k1 = clamp((p - 0.42) / 0.065) * (1 - clamp((p - 0.66) / 0.055)); k2 = clamp((p - 0.84) / 0.065)
    if k1 <= 0 and k2 <= 0: return
    me, m = c.img.copy(), c.m[..., None]
    a, b = (e.o.get('text') or tr('Visualizzazioni del reel|Top reel · totale', 'Views · this reel|Top reels · total')).split('|')[:2]
    va, vb = (str(e.o.get('to') or '197K|672K')).split('|')[:2]
    glass_graph(c, c.W * 0.43, c.H * 0.255, k1, clamp((p - 0.45) / 0.17), a, va, 'line')
    glass_graph(c, c.W * 0.57, c.H * 0.255, k2, clamp((p - 0.86) / 0.14), b, vb, 'bars')
    c.img = c.img * (1 - m) + me * m   # your head stays in front of the cards
