"""giostra (carousel-spin): Le tue reel ti girano intorno in una giostra 3D, poi rallentano fino a fermarsi.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('giostra', en='carousel-spin', alias=('carousel', 'carousel-spin'),
         desc='Le tue reel ti girano intorno in una giostra 3D, poi rallentano fino a fermarsi', schede=True)
def fx_carousel_spin(c, e):
    K = int(e.o.get('count', max(6, min(12, len(e.cards))))); cw = int(c.W * float(e.o.get('size', 0.3)))
    def mk():
        out = []
        for i, im in enumerate(e.cards):
            f = card(vary(im, i) if e.o.get('images') is None else im, cw)
            dk = f.copy(); a = np.asarray(dk).copy(); a[..., :3] = (a[..., :3] * 0.55).astype(np.uint8); out.append((f, Image.fromarray(a, 'RGBA')))
        return out
    cards = cached(e, 'cards', mk)
    k = ramp(c, e, 0.3, 0.25); xx, yy = grid(c)
    d = ((xx - c.fx) / (c.W * 0.55)) ** 2 + ((yy - (c.fy + c.H * 0.15)) / (c.H * 0.5)) ** 2
    dim = 1 - k * 0.5 * np.clip(d, 0, 1) - k * 0.12
    c.img *= (dim * (1 - c.m) + c.m)[..., None]
    p = clamp(c.lt / e.d); spin = float(e.o.get('turns', 1.1)) * 2 * math.pi * (1 - (1 - p) ** 2.4)
    intro, out = ease_out(c.lt / 0.45), fade(c, e, 0.25)
    R, ry = c.W * 0.56 * intro, c.H * 0.07
    cy = c.fy + c.fw * 1.8
    items = sorted((math.cos(i * 2 * math.pi / K + spin), i * 2 * math.pi / K + spin, i) for i in range(K))
    for depth, th, i in items:
        n = len(cards); f, dk = cards[(i * (3 if n % 3 else 2)) % n]; src = f if depth >= 0 else dk  # spread similar covers apart
        sx = max(0.06, abs(math.cos(th)) ** 0.6)
        s = (0.72 + 0.34 * (depth + 1) / 2) * (0.5 + 0.5 * intro)
        w2, h2 = max(2, int(src.width * s * sx)), max(2, int(src.height * s))
        place(c, src.resize((w2, h2), Image.BILINEAR), c.fx + R * math.sin(th), cy + ry * depth, 1.0, 0,
              out * clamp(c.lt / 0.12) * (0.85 + 0.15 * depth), behind=depth < 0, guard=depth >= 0)
