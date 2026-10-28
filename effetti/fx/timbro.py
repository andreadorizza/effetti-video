"""timbro (reject-stamp): Un grosso timbro rosso cala sullo schermo.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('timbro', en='reject-stamp', alias=('reject-stamp', 'respinto', 'stamp'),
         desc='Un grosso timbro rosso cala sullo schermo')
def fx_reject_stamp(c, e):
    word = e.o.get('text', tr('RESPINTO', 'REJECTED')).upper()
    y = clamp(float(e.o['y']) * c.H if 'y' in e.o else c.fy + c.fw * 2.7, 0, c.H * 0.85)
    # stamped straight on the video: a theme's danger that would vanish there falls back to what reads
    col = cached(e, 'col', lambda: rgb(e.o.get('color'), P.c('danger', (214, 40, 40), on=footage(c, c.W * 0.2, y - c.W * 0.12, c.W * 0.8, y + c.W * 0.12))))
    def build():
        t = fit_text(word, c.W * 0.62, 'bold', 200, fill=col); pad = int(t.height * 0.12)
        im = Image.new('RGBA', (t.width + 4 * pad, t.height + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([3, 3, im.width - 4, im.height - 4], P.r(18), outline=col + (255,), width=max(6, pad // 2))
        im.alpha_composite(t, (2 * pad, pad))
        a = np.asarray(im.split()[3], np.float32) * np.clip(np.random.default_rng(3).uniform(0.55, 1.6, (im.height, im.width)), 0, 1)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        return im
    st = cached(e, 's', build)
    k = clamp(c.lt / 0.16); sc = 2.3 - 1.3 * k * k
    if 0.16 < c.lt < 0.45:
        a = (0.45 - c.lt) / 0.29 * c.W * 0.012; rnd = np.random.default_rng(int(c.t * 30))
        M = np.float32([[1, 0, rnd.uniform(-a, a)], [0, 1, rnd.uniform(-a, a)]])
        c.img = cv2.warpAffine(c.img, M, (c.W, c.H), borderMode=cv2.BORDER_REFLECT)
    place(c, st, c.W / 2, y, sc, float(e.o.get('angle', 12)), k * clamp((e.d - c.lt) / 0.2), guard=True)
