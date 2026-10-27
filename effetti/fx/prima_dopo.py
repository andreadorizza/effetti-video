"""prima-dopo (swipe): Un cursore prima/dopo che ti attraversa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('prima-dopo', en='swipe', alias=('swipe',),
         desc='Un cursore prima/dopo che ti attraversa')
def fx_swipe(c, e):
    after = grade(c.img, e.o.get('grade', 'moody'))
    p = c.lt / e.d
    sp = 1.05 - 0.95 * ease_inout(p / 0.5) if p < 0.5 else 0.1 + 0.4 * ease_inout((p - 0.5) / 0.4)
    xx, yy = grid(c)
    line = sp * c.W + 0.22 * (yy - c.H / 2)
    a = np.clip((xx - line) / 3 + 0.5, 0, 1)[..., None]
    c.img = c.img * (1 - a) + after * a
    hy = c.H * 0.62; hx = sp * c.W + 0.22 * (hy - c.H / 2)
    edge = np.clip(1 - np.abs(xx - line) / 3.5, 0, 1)[..., None]
    c.img = c.img * (1 - edge) + edge
    r = int(c.W * 0.035); h = Image.new('RGBA', (2 * r + 4, 2 * r + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(h)
    d.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(255, 255, 255, 255))
    d.text((r + 2, r + 2), '< >', font=font('mono', r * 0.7), fill=INK + (255,), anchor='mm')
    place(c, shadowed(h, 8, 4, 110), hx, hy)
    for lab, x in (('before', 0.14), ('after', 0.86)):
        t = text_img(lab, c.W * 0.03, 'serif', INK); pill = rrect(t.width + 16, t.height, t.height / 2, (255, 255, 255, 225))
        pill.alpha_composite(t, (8, 0)); place(c, pill, c.W * x, c.H * 0.88)
