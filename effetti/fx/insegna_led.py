"""insegna-led (led-sign): Le luci calano e un'insegna LED si scrive da sola dietro di te.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('insegna-led', en='led-sign', alias=('insegna', 'led', 'led-sign'),
         desc="Le luci calano e un'insegna LED si scrive da sola dietro di te")
def fx_led_sign(c, e):
    k = ramp(c, e, 0.2, 0.2)
    face_cam(c, 1 + (float(e.o.get('push', 1.08)) - 1) * ease_inout(c.lt / e.d), 0.42)
    lines = e.o.get('text', 'CLAUDE').upper().split('|'); col = np.float32(rgb(e.o.get('color'), (255, 146, 48))) / 255
    def setup():
        mats = []
        for s in lines:
            f = font('uib', 40); w = int(f.getlength(s)) + 8
            im = Image.new('L', (w, 56), 0); ImageDraw.Draw(im).text((4, 2), s, font=f, fill=255)
            bb = im.getbbox() or (0, 0, w, 56); im = im.crop(bb)
            rows = 11; cols = max(1, round(im.width / im.height * rows))
            mats.append(np.asarray(im.resize((cols, rows), Image.BOX), np.float32) / 255 > 0.42)
        cols = max(m.shape[1] for m in mats) + 2
        cell = int(min(c.W * 0.96 / cols, c.H * 0.3 / (len(mats) * 12)))
        L = np.zeros((len(mats) * 12 - 1, cols), np.float32)
        for i, m in enumerate(mats): o = (cols - m.shape[1]) // 2; L[i * 12:i * 12 + 11, o:o + m.shape[1]] = m
        yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32); rr = np.hypot(xx - cell / 2 + 0.5, yy - cell / 2 + 0.5)
        dot = np.clip(cell * 0.36 - rr + 0.5, 0, 1)
        return L, cell, dot, np.random.default_rng(3).random(L.shape).astype(np.float32)
    L, cell, dot, rnd = cached(e, 'm', setup)
    rows, cols = L.shape
    sweep = clamp((c.lt - 0.15) / 0.75) * (cols + 4)
    lit = L * np.clip((sweep - np.arange(cols)[None, :]) / 3, 0, 1)
    flick = 0.82 + 0.18 * np.sin(rnd * 50 + c.lt * 30)
    b = np.maximum(lit * flick, 0.09)
    pan = np.kron(b, dot)[..., None] * col
    glow = cv2.GaussianBlur(pan, (0, 0), cell * 0.9)
    pan = np.clip(pan + glow * 1.6, 0, 1)
    ph, pw = pan.shape[:2]; x0 = int(c.W / 2 - pw / 2)
    y0 = int(max(c.H * 0.03, c.fy - c.fw * 0.75 - ph))
    xx, yy = grid(c)
    d = ((xx - c.fx) / (c.W * 0.6)) ** 2 + ((yy - (c.fy + c.H * 0.25)) / (c.H * 0.55)) ** 2
    bright = 1 - k * (0.84 - 0.3 * np.clip(1 - d, 0, 1))
    c.img *= (bright * (1 - c.m) + c.m * (1 - 0.18 * k))[..., None]
    xa, xb = max(0, x0), min(c.W, x0 + pw); ya, yb = max(0, y0), min(c.H, y0 + ph)
    if xb > xa and yb > ya:
        sub = pan[ya - y0:yb - y0, xa - x0:xb - x0] * k * (1 - c.m[ya:yb, xa:xb, None])
        c.img[ya:yb, xa:xb] = np.clip(c.img[ya:yb, xa:xb] + sub, 0, 1)
