"""copertina (cover-star): Diventi la copertina di una rivista, col titolo dietro la testa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def tracked(s, size, kind, fill, spacing, colors=None):
    """Letter-spaced text. colors: optional per-character fill list."""
    f = font(kind, size); w = sum(f.getlength(ch) for ch in s) + spacing * max(0, len(s) - 1)
    bb = f.getbbox('Ag'); im = Image.new('RGBA', (int(w) + 8, int(bb[3] - bb[1] + size * 0.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    for i, ch in enumerate(s):
        d.text((x, -bb[1] + size * 0.2), ch, font=f, fill=(colors[i] if colors else fill) + (255,)); x += f.getlength(ch) + spacing
    return im


def cover_editorial(c, e):
    k = ease_out(c.lt / 0.35); al = fade(c, e); W, H = c.W, c.H
    lum = (c.img @ np.float32([0.299, 0.587, 0.114]))[..., None]
    soft = (c.img * 0.82 + lum * 0.18) * 0.9 + np.float32((252, 238, 228)) / 255 * 0.1
    if P.glow:  # the highlights bloom
        q = 4; bl = cv2.resize(np.clip(c.img[::q, ::q] - 0.62, 0, 1), (W, H), interpolation=cv2.INTER_LINEAR)
        bloom = cv2.GaussianBlur(bl, (0, 0), W * 0.012)
        soft = soft + bloom * 0.55
    c.img = c.img * (1 - k) + np.clip(soft, 0, 1) * k
    ink, rose = rgb(e.o.get('color'), P.c('over', (26, 20, 22))), rgb(e.o.get('accent'), P.c('accent', (168, 70, 94)))
    cream = P.c('paper', (252, 244, 236))
    title = e.o.get('text', tr('EFFETTI', 'EFFECTS')).upper()
    def mast():
        size = int(H * 0.16)
        while size > 20 and font('didoneb', size).getlength(title) + size * 0.04 * len(title) > W * 0.92: size = int(size * 0.95)
        return tracked(title, size, 'didoneb', ink, size * 0.04)
    m = cached(e, 'm', mast)
    s = 1.05 - 0.05 * ease_out(c.lt / 0.5)
    place(c, m, W / 2, H * 0.085 + m.height / 2, s, 0, al * k, behind=True)
    iss = cached(e, 'i', lambda: tracked(e.o.get('issue', tr('SPECIALE UNA CLIP  ·  N. 42  ·  OTTOBRE 2026', 'THE ONE-CLIP ISSUE  ·  NO. 42  ·  OCTOBER 2026')), int(W * 0.022), 'ui', ink, W * 0.006))
    place(c, iss, W / 2, H * 0.075, alpha=al * k, behind=True)
    rule = cached(e, 'r', lambda: rrect(W * 0.86, max(3, W // 600), 1, ink + (255,)))
    place(c, rule, W / 2, H * 0.087 + m.height, alpha=al * k * 0.8, behind=True)
    lines = e.o.get('lines', tr('Una clip,|42 stili.|ZERO EDITOR  ·  ZERO APP', 'One clip,|42 looks.|NO EDITOR  ·  NO APPS')).split('|')
    styles = [('didonei', 0.085, ink), ('didoneb', 0.105, rose), ('ui', 0.03, ink)]
    y = H * float(e.o.get('lines_y', 0.575))
    for j, ln in enumerate(lines):
        kind, sz, col = styles[min(j, 2)]
        im = cached(e, ('l', j), lambda: (tracked(ln, int(W * sz), kind, col, W * 0.006) if kind == 'ui' else text_img(ln, W * sz, kind, col, glow=(cream, W * 0.012))))
        kj = ease_out((c.lt - 0.2 - 0.1 * j) / 0.35)
        comp(c, im, W * 0.05 - (1 - kj) * W * 0.03, y, al * kj); y += im.height * (0.82 if kind != 'ui' else 1.6)
    right = e.o.get('right', tr("l'arte del|montaggio facile", 'the art of the|effortless edit')).split('|')
    y = H * float(e.o.get('right_y', 0.715))
    for j, ln in enumerate(right):
        im = cached(e, ('r', j), lambda: text_img(ln, W * 0.058, 'didonei', ink, glow=(cream, W * 0.01)))
        kj = ease_out((c.lt - 0.45 - 0.1 * j) / 0.35)
        comp(c, im, W * 0.95 - im.width + (1 - kj) * W * 0.03, y, al * kj); y += im.height * 0.78


@effetto('copertina', en='cover-star', alias=('cover', 'cover-star', 'rivista'),
         desc='Diventi la copertina di una rivista, col titolo dietro la testa')
def fx_cover_star(c, e):
    if e.o.get('look') == 'editorial': return cover_editorial(c, e)
    k = ease_out(c.lt / 0.35); al = clamp((e.d - c.lt) / 0.2)
    c.img = c.img * (1 - 0.6 * k) + grade(c.img, 'pop') * 0.6 * k
    title = e.o.get('text', 'VIBE').upper(); col = rgb(e.o.get('color'), P.c('over', (232, 36, 52)))
    mast = cached(e, 'm', lambda: fit_text(title, c.W * 0.92, 'bold', 600, fill=col))
    mast_h = min(mast.height, c.H * 0.24)
    place(c, mast, c.W / 2, c.H * 0.035 + mast_h / 2 - (1 - k) * mast_h, mast_h / mast.height, 0, al * k, behind=True)
    iss = cached(e, 'i', lambda: text_img(e.o.get('issue', tr('SPECIALE AI  ·  2026', 'THE AI ISSUE  ·  2026')), c.W * 0.025, 'mono', P.c('over', (255, 255, 255)), shadow=3))
    place(c, iss, c.W / 2, c.H * 0.03, alpha=al * k, behind=True)
    lines = e.o.get('lines', tr('22 effetti|da rubare|senza|montatore', '22 effects|you can steal|no editor|needed')).split('|')
    y = c.H * 0.5
    for j, ln in enumerate(lines):
        big = j == 0
        im = cached(e, ('l', j), lambda: text_img(ln, c.W * (0.085 if big else 0.045), 'serif' if big else 'bold', P.c('over', YELLOW) if big else P.c('over', (255, 255, 255)), shadow=5))
        kj = ease_out((c.lt - 0.15 - 0.08 * j) / 0.3)
        comp(c, im, c.W * 0.05 - (1 - kj) * 60, y, al * kj, guard=True); y += im.height * 0.86
    def barcode():
        rnd = random.Random(1); bw, bh = int(c.W * 0.16), int(c.W * 0.09)
        im = Image.new('RGBA', (bw, bh), P.c('surface', (255, 255, 255), 255)); d = ImageDraw.Draw(im); x = 8
        while x < bw - 8:
            w = rnd.choice((2, 2, 3, 5)); d.rectangle([x, 6, x + w - 1, bh - 18], fill=P.c('on-surface', (0, 0, 0), 255)); x += w + rnd.choice((2, 3, 4))
        return im
    bc = cached(e, 'b', barcode)
    comp(c, bc, c.W * 0.95 - bc.width, c.H * 0.93 - bc.height, al * k, guard=True)
