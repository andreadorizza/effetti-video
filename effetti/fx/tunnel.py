"""tunnel (rabbit-hole): L'immagine sprofonda in sé stessa, girando.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *

_rect = {}


@effetto('tunnel', en='rabbit-hole', alias=('bianconiglio', 'rabbit-hole'),
         desc="L'immagine sprofonda in sé stessa, girando")
def fx_rabbit_hole(c, e):
    k = ease_out(c.lt / 0.4) * clamp((e.d - c.lt) / 0.3)
    if k <= 0: return
    if (c.W, c.H) not in _rect:
        a = np.ones((c.H, c.W), np.float32); b = np.zeros((c.H, c.W), np.float32); t = max(4, c.W // 120)
        b[:t] = b[-t:] = 1; b[:, :t] = b[:, -t:] = 1; _rect[(c.W, c.H)] = (a, b)
    ones, border = _rect[(c.W, c.H)]
    r = float(e.o.get('ratio', 0.62)); z = (c.lt * float(e.o.get('speed', 0.8))) % 1.0
    src = c.img; cx, cy = c.fx, c.fy
    out = None
    for lev in range(0, 7):
        s = r ** (lev - z * k) if lev else 1.0
        ang = (lev - z) * float(e.o.get('spin', 10)) * k if lev else 0
        if lev and s < 0.03: break
        M = cv2.getRotationMatrix2D((cx, cy), ang, s)
        if lev == 0:
            out = src.copy(); continue
        L = cv2.warpAffine(src, M, (c.W, c.H), flags=cv2.INTER_LINEAR)
        a = cv2.warpAffine(ones, M, (c.W, c.H))[..., None] * k
        bd = cv2.warpAffine(border, M, (c.W, c.H))[..., None] * k
        out = out * (1 - a) + L * a
        out = out * (1 - bd) + bd
    m = c.m[..., None] * k  # you stay in front while the room tunnels behind you
    c.img = out * (1 - m) + src * m
