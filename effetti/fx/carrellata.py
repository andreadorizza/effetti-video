"""carrellata (slow-push): Una lenta spinta cinematografica sul viso mentre la stanza va fuori fuoco.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('carrellata', en='slow-push', alias=('push', 'push-in', 'slow-push'),
         desc='Una lenta spinta cinematografica sul viso mentre la stanza va fuori fuoco')
def fx_slow_push(c, e):
    p = ease_inout(c.lt / e.d)
    face_cam(c, 1 + (float(e.o.get('zoom', 1.6)) - 1) * p, 0.4)
    s = c.W * float(e.o.get('blur', 0.006)) * p
    if s > 0.6:
        bl = cv2.GaussianBlur(c.img, (0, 0), s); m = c.m[..., None]
        c.img = c.img * m + bl * (1 - m)
    vignette(c, 0.25 * p)
