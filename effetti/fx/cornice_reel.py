"""cornice-reel (reel-frame): Il video si rimpicciolisce dentro una scheda reel di Instagram.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def reel_icons(size):
    s = int(size); im = Image.new('RGBA', (s, int(s * 3.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(3, s // 12)
    h = heart(s * 0.8, (255, 255, 255)); im.alpha_composite(h, (int(s * 0.1), 0))
    d.text((s / 2, s * 0.95), '26.9K', font=font('ui', s * 0.24), fill=(255, 255, 255, 255), anchor='mm')
    d.ellipse([s * 0.15, s * 1.25, s * 0.85, s * 1.95], outline=(255, 255, 255, 255), width=w)
    d.text((s / 2, s * 2.15), '412', font=font('ui', s * 0.24), fill=(255, 255, 255, 255), anchor='mm')
    d.polygon([(s * 0.12, s * 2.75), (s * 0.9, s * 2.45), (s * 0.55, s * 3.25), (s * 0.45, s * 2.88)], outline=(255, 255, 255, 255), width=w)
    return im


@effetto('cornice-reel', en='reel-frame', alias=('cornice', 'reel-frame'),
         desc='Il video si rimpicciolisce dentro una scheda reel di Instagram')
def fx_reel_frame(c, e):
    k = ease_out(c.lt / 0.35) * clamp((e.d - c.lt) / 0.3)
    if k <= 0: return
    s = 1 - 0.2 * k
    small = cv2.resize(c.img, (c.W // 16, c.H // 16), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(cv2.resize(small, (c.W, c.H), interpolation=cv2.INTER_LINEAR), (0, 0), 12) * (1 - 0.45 * k)
    iw, ih = int(c.W * s), int(c.H * s)
    inset = cv2.resize(c.img, (iw, ih), interpolation=cv2.INTER_AREA)
    m = to_np(rrect(iw, ih, c.W * 0.05 * k + 1, (255, 255, 255, 255)))[..., 3:4]
    x0, y0 = (c.W - iw) // 2, int((c.H - ih) * 0.42)
    out = bg.copy(); reg = out[y0:y0 + ih, x0:x0 + iw]; reg[:] = reg * (1 - m) + inset * m
    c.img = out
    mm = np.zeros_like(c.m); mm[y0:y0 + ih, x0:x0 + iw] = cv2.resize(c.m, (iw, ih)); c.m = mm
    c.fx, c.fy, c.fw = x0 + c.fx * s, y0 + c.fy * s, c.fw * s
    ic = cached(e, 'ic', lambda: shadowed(reel_icons(c.W * 0.075), 6, 2, 120))
    comp(c, ic, x0 + iw - ic.width - c.W * 0.01, y0 + ih * 0.52, k)
    hdl = text_img(e.o.get('text', '@your.handle'), c.W * 0.032, 'ui', (255, 255, 255), shadow=4)
    comp(c, hdl, x0 + c.W * 0.03, y0 + ih - hdl.height - c.W * 0.04, k)
