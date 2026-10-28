"""disinstalla (uninstall): Una barra di disinstallazione glitchata spacca l'immagine.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('disinstalla', en='uninstall', alias=('uninstall',),
         desc="Una barra di disinstallazione glitchata spacca l'immagine")
def fx_uninstall(c, e):
    p = clamp(c.lt / e.d); g = p ** 1.6
    rnd = np.random.default_rng(int(c.t * 30))
    sh = int(g * c.W * 0.025)
    if sh: c.img = np.stack([np.roll(c.img[..., 0], sh, 1), c.img[..., 1], np.roll(c.img[..., 2], -sh, 1)], -1)
    for _ in range(int(2 + g * 10)):
        y0 = int(rnd.uniform(0, c.H)); hh = int(rnd.uniform(8, 60)); off = int(rnd.uniform(-1, 1) * g * c.W * 0.08)
        c.img[y0:y0 + hh] = np.roll(c.img[y0:y0 + hh], off, 1)
    if p > 0.82:
        q = (p - 0.82) / 0.18; f = 1 + int(q * 40)
        small = cv2.resize(c.img, (max(1, c.W // f), max(1, c.H // f)), interpolation=cv2.INTER_AREA)
        c.img = cv2.resize(small, (c.W, c.H), interpolation=cv2.INTER_NEAREST) * (1 - 0.6 * q)
    bw, bh = int(c.W * 0.7), int(c.W * 0.2)
    im = rrect(bw, bh, 22, P.c('surface', (245, 245, 247), 240)); d = ImageDraw.Draw(im)
    txt = e.o.get('text', tr('Disinstallazione...', 'Uninstalling...'))
    d.text((bw * 0.06, bh * 0.28), txt, font=fontfor('ui', bh * 0.18, txt), fill=P.c('on-surface', INK) + (255,), anchor='lm')
    d.rounded_rectangle([bw * 0.06, bh * 0.56, bw * 0.94, bh * 0.7], P.r(8), fill=P.c('line', (215, 215, 220), 255))
    d.rounded_rectangle([bw * 0.06, bh * 0.56, bw * 0.06 + bw * 0.88 * max(0.03, ease_inout(p)), bh * 0.7], P.r(8), fill=P.c('accent', (0, 122, 255), 255))
    d.text((bw * 0.94, bh * 0.85), f'{int(ease_inout(p) * 100)}%', font=font('ui', bh * 0.13), fill=P.c('muted', (110, 110, 110), 255), anchor='rm')
    place(c, shadowed(im, 16, 8, 120), c.W / 2, c.H * 0.16, 0.8 + 0.2 * ease_back(c.lt / 0.3), 0, clamp(c.lt / 0.1))
