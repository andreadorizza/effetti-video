"""puntini (dot-reveal): L'inquadratura si compone di puntini luminosi, poi torna nitida.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('puntini', en='dot-reveal', alias=('dot-reveal', 'dots'),
         desc="L'inquadratura si compone di puntini luminosi, poi torna nitida")
def fx_dot_reveal(c, e):
    p = clamp(c.lt / e.d); W, H = c.W, c.H
    cell = max(6, int(W * float(e.o.get('cell', 0.017)))); gh, gw = H // cell + 1, W // cell + 1
    def geo():
        yy, xx = np.mgrid[0:gh * cell, 0:gw * cell].astype(np.float32)
        dist = np.sqrt((xx % cell - cell / 2 + 0.5) ** 2 + (yy % cell - cell / 2 + 0.5) ** 2)[:H, :W]
        return dist, np.random.default_rng(5).random((gh, gw)).astype(np.float32)
    dist, thr = cached(e, 'geo', geo)
    pad = np.pad(c.img, ((0, gh * cell - H), (0, gw * cell - W), (0, 0)), mode='edge')
    small = cv2.resize(pad, (gw, gh), interpolation=cv2.INTER_AREA)
    lum = small @ np.float32([0.299, 0.587, 0.114])
    on = np.clip((p * 1.7 - thr * 0.95) / 0.3, 0, 1)
    col = rgb(e.o.get('color'), P.c('accent', (255, 128, 80)))
    bgc = np.float32(rgb(e.o.get('bg'), P.c('ground', (20, 20, 22)))) / 255
    # dots lighter than the ground grow with the light; darker dots (on a light theme ground) grow with the shadows
    lw = np.float32([0.299, 0.587, 0.114]); tone = lum if float(np.float32(col) / 255 @ lw) >= float(bgc @ lw) else 1 - lum
    r = (0.18 + 0.32 * np.sqrt(np.clip(tone, 0, 1))) * cell * on
    q2 = clamp((p - 0.3) / 0.35)
    if P.glow:  # luminous dots that twinkle
        sparkle = 0.75 + 0.25 * np.sin(thr * 40 + c.lt * 18)
        dc = np.float32(col) / 255 * (0.55 + 0.6 * lum[..., None]) * sparkle[..., None] * (1 - q2) + np.clip(small * 1.15, 0, 1) * q2
    else:  # flat halftone dots in one colour
        dc = np.float32(col) / 255 * np.ones_like(lum)[..., None] * (1 - q2) + np.clip(small * 1.15, 0, 1) * q2
    R = np.repeat(np.repeat(r, cell, 0), cell, 1)[:H, :W]
    DC = np.repeat(np.repeat(dc, cell, 0), cell, 1)[:H, :W]
    dm = np.clip(R - dist + 0.5, 0, 1)[..., None]
    dots = bgc * (1 - dm) + DC * dm
    q = ease_inout((p - 0.6) / 0.4)
    c.img = dots * (1 - q) + c.img * q
