"""griglia-profilo (place-in-grid): Ti rimpicciolisci nella casella centrale della tua griglia 3x3 e le reel compaiono intorno a te con le visualizzazioni.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def views_icon(px):
    """The Instagram 'views' eye: an arc above a teardrop (traced from the IG app)."""
    paths = [[(325, 490), [(-43, -9, -73, -30, -97, -68), (-28, -46, -14, -53, 22, -10), (37, 45, 79, 62, 133, 55), (33, -4, 50, -14, 80, -48), (40, -44, 60, -46, 37, -3), (-29, 52, -112, 87, -175, 74)]],
             [(315, 405), [(-51, -50, -21, -115, 52, -115), (51, 0, 88, 65, 41, 72), (-14, 2, -29, 15, -38, 35), (-8, 18, -19, 33, -23, 33), (-4, 0, -19, -11, -32, -25)]]]
    k = px / 24 * 4; im = Image.new('L', (int(34 * k), int(24 * k)), 0); d = ImageDraw.Draw(im)
    tx = lambda x, y: ((0.1 * x - 19) * k, (80 - 0.1 * y - 29) * k)
    for (sx, sy), segs in paths:
        pts = [tx(sx, sy)]; cx, cy = sx, sy
        for s in segs:
            p0, p1, p2, p3 = (cx, cy), (cx + s[0], cy + s[1]), (cx + s[2], cy + s[3]), (cx + s[4], cy + s[5])
            for j in range(1, 13):
                t = j / 12; pts.append(tx(*[(1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * cc + t ** 3 * dd for a, b, cc, dd in zip(p0, p1, p2, p3)]))
            cx, cy = p3
        d.polygon(pts, fill=255)
    im = im.resize((int(34 * px / 24), px), Image.LANCZOS); out = Image.new('RGBA', im.size, (255, 255, 255, 0)); out.putalpha(im); return out


def grid_tile(im, w, h, views, r):
    t = im.convert('RGB'); s = max(w / t.width, h / t.height); t = t.resize((int(t.width * s) + 1, int(t.height * s) + 1), Image.LANCZOS)
    t = t.crop(((t.width - w) // 2, (t.height - h) // 2, (t.width - w) // 2 + w, (t.height - h) // 2 + h)).convert('RGBA')
    mk = Image.new('L', (w, h), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    if views:
        u = w / 660; fd = Image.linear_gradient('L').resize((w, int(h * 0.28))).point(lambda v: int(v * 0.75))
        sh = Image.new('RGBA', fd.size, (0, 0, 0, 0)); sh.putalpha(fd); t.alpha_composite(sh, (0, h - fd.height))
        ic = views_icon(int(56 * u)); x, y = int(34 * u), int(h - 92 * u); t.alpha_composite(ic, (x, y + int(2 * u)))
        ImageDraw.Draw(t).text((x + ic.width + 14 * u, y - 6 * u), views, font=font('uib', 58 * u), fill=(255, 255, 255, 255))
    t.putalpha(mk); ImageDraw.Draw(t).rounded_rectangle([1, 1, w - 2, h - 2], r, outline=(255, 255, 255, 150), width=max(1, int(4 * w / 660)))
    return t


@effetto('griglia-profilo', en='place-in-grid', alias=('grid', 'griglia', 'place-in-grid', 'profile-grid'),
         desc='Ti rimpicciolisci nella casella centrale della tua griglia 3x3 e le reel compaiono intorno a te con le visualizzazioni', schede=True)
def fx_place_in_grid(c, e):
    W, H = c.W, c.H; g, m = int(33 * W / 2160), int(68 * W / 2160)
    tw = (W - 2 * m - 2 * g) // 3; th = int(tw * 16 / 9); top = (H - (3 * th + 2 * g)) // 2; r = int(28 * W / 2160)
    rect = lambda i: (m + (i % 3) * (tw + g), top + (i // 3) * (th + g))
    views = (e.o.get('views') or '2.4M|847K|1.2M|312K|3.4M|596K|268K|1.8M|3.1M').split('|')
    tiles = cached(e, 'tiles', lambda: [grid_tile(vary(im, i) if e.o.get('images') is None else im, tw, th, views[i % len(views)], r) for i, im in enumerate((e.cards * 8)[:8])])
    me = c.img.copy(); p = ease_inout(clamp(c.lt / 0.45))
    fz = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (W // 8, H // 8)), (0, 0), 14), (W, H), interpolation=cv2.INTER_CUBIC)
    lum = (fz @ np.float32([0.299, 0.587, 0.114]))[..., None]; fz = np.clip(lum + (fz - lum) * 1.25, 0, 1)
    c.img = fz * (1 - 0.37) + np.float32([255, 248, 238]) / 255 * 0.37
    for j, slot in enumerate((1, 5, 7, 3, 2, 8, 6, 0)):
        a = clamp((c.lt - 0.47 - j / 30) / 0.1)
        if a > 0: x, y = rect(slot); place(c, tiles[j], x + tw / 2, y + th / 2, 0.82 + 0.18 * ease_back(a), 0, clamp(a * 2))
    cx, cy = rect(4); w2, h2 = int(W + (tw - W) * p), int(H + (th - H) * p)
    mine = Image.fromarray((np.clip(me, 0, 1) * 255).astype(np.uint8))
    tile = grid_tile(mine, w2, h2, views[8 % len(views)] if p > 0.9 else None, int(r * p))
    comp(c, tile, cx * p, cy * p)
    if p > 0.95: d = Image.new('RGBA', (tw + 8, th + 8), (0, 0, 0, 0)); ImageDraw.Draw(d).rounded_rectangle([2, 2, tw + 5, th + 5], r + 2, outline=(217, 119, 87, 255), width=8); comp(c, d, cx - 4, cy - 4)
