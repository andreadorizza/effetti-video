"""broll-diviso (broll-split): B-roll sopra con un'etichetta prezzo, tu sotto.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('broll-diviso', en='broll-split', alias=('b-roll', 'broll', 'broll-split'),
         desc="B-roll sopra con un'etichetta prezzo, tu sotto", schede=True)
def fx_broll_split(c, e):
    W, H = c.W, c.H; k = ease_out(c.lt / 0.3) * clamp((e.d - c.lt) / 0.2); al = fade(c, e)
    shift(c, (H * 0.72 - c.fy) * k)
    sh = int(H * 0.5 * k)
    if sh > 2:
        src = e.cards[int(e.o.get('pick', 0)) % len(e.cards)].convert('RGB')
        z = 1.0 + 0.06 * clamp(c.lt / e.d); tw, th = int(W * z), int(H * 0.5 * z)
        s = max(tw / src.width, th / src.height); im = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.BILINEAR)
        l, t = (im.width - W) // 2, int((im.height - H * 0.5) * 0.35); im = im.crop((l, t, l + W, t + int(H * 0.5)))
        top = np.asarray(im, np.float32) / 255
        c.img[:sh] = top[int(H * 0.5) - sh:]; c.m[:sh] = 0
        c.img[max(0, sh - 3):sh + 3] = P.f('over', [1.0, 1.0, 1.0])  # the white seam
    tag = cached(e, 'tag', lambda: text_img(e.o.get('text', tr('4 ore  →  4 min', '4 hrs  →  4 min')), W * 0.06, 'uib', P.c('on-surface', (16, 16, 18))))
    tw, th = int(tag.width + W * 0.11), int(tag.height * 1.25)
    st = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(st); n = th * 0.5
    d.polygon([(0, th / 2), (n, 0), (tw, 0), (tw, th), (n, th)], fill=P.c('surface', (255, 255, 255), 255))
    d.ellipse([n * 0.55, th / 2 - n * 0.16, n * 0.87, th / 2 + n * 0.16], fill=P.c('line', (200, 200, 205), 255))
    st.alpha_composite(tag, (int(n * 1.05), (th - tag.height) // 2))
    place(c, shadowed(st, 12, 6, 110), W * 0.66, H * 0.39 * k + H * 0.0, 0.5 + 0.5 * pop(c, 0.3), 8, al * clamp((c.lt - 0.3) / 0.08))
