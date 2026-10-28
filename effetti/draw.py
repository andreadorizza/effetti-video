"""The shared drawing kit every effect imports: easing, text, cards, compositing, camera moves, glass.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video, where every colour,
corner, shadow and glass panel goes through the theme (P, see theme.py) and every default text
through tr() (see i18n.py).

An effect is a function (c, e) called once per frame:
  c.img   the frame, float32 RGB 0..1, H x W x 3 (draw on it in place)
  c.m     the person mask, 0..1 (1 where you are)
  c.fx, c.fy, c.fw   your face: centre and width, in pixels
  c.lt    seconds since the effect started; c.t the video time; c.W, c.H the frame size
  e.o     the options; e.d the effect's length; e.start; e.state a dict for caches; e.cards your reels
"""
import math, os, random
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .theme import P, ROOT, FONT, WGHT, covers
from .i18n import tr, effetto, num, decimal_comma

# The neutral palette. Effects take colours through P.c(role, neutral), so a theme can replace them.
CREAM, INK, PEACH, YELLOW = (244, 233, 216), (22, 22, 24), (255, 183, 165), (255, 214, 10)
GREEN, BLUE, PURPLE, ORANGE, RED = (52, 211, 102), (10, 132, 255), (124, 92, 255), (217, 119, 87), (238, 34, 34)  # GREEN as the original renders it (it was rebound to this value further down)
NAMES = ['The Noise', 'The Lineup', 'Locked On', 'Orbit', 'Lean-In', 'Backdrop Word', 'Spotlight', 'The Bill',
         'Moody', 'Swipe', 'The To-Do', 'Comment Box', 'The Tap', 'Pause & Point', 'Uninstall', 'Reel Frame',
         'Shortcut Rain', 'Reject Stamp', 'Countdown Flip', 'Rabbit Hole', 'Cover Star', 'Scribble']
NOMI = ['Rumore', 'In fila', 'Agganciato', 'Orbita', 'Zoom lampo', 'Parola dietro', 'Riflettore', 'Scontrino',
        'Atmosfera', 'Prima e dopo', 'Da fare', 'Commento', 'Segui', 'Fermo immagine', 'Disinstalla', 'Cornice reel',
        'Pioggia di tasti', 'Timbro', 'Conto alla rovescia', 'Tunnel', 'Copertina', 'Scarabocchi']


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))


def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3


def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x


def ease_back(x): x = clamp(x); s = 1.7; x -= 1; return x * x * ((s + 1) * x + s) + 1


def ramp(c, e, t_in=0.25, t_out=0.2): return clamp(c.lt / t_in) * clamp((e.d - c.lt) / t_out) if t_out else clamp(c.lt / t_in)


def rgb(v, default):
    if v is None: return default
    if isinstance(v, (list, tuple)): return tuple(int(x) for x in v[:3])
    v = str(v).lstrip('#'); return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


_fc = {}


def font(kind, size):
    path, axes = P.font_path(kind), P.axes(kind)
    k = (path, axes, int(size))
    if k not in _fc:
        f = ImageFont.truetype(path, max(6, int(size)))
        if axes:
            try: f.set_variation_by_axes(list(axes))
            except Exception: pass
        _fc[k] = f
    return _fc[k]


def fontfor(kind, size, s):
    """font(), but falls back to the neutral font when the theme's font has no glyph for a character of s."""
    if kind in P.fonts and not covers(P.fonts[kind], s): return font_neutral(kind, size)
    return font(kind, size)


def font_neutral(kind, size):
    k = ('neutral', kind, int(size))
    if k not in _fc:
        f = ImageFont.truetype(FONT[kind], max(6, int(size)))
        if kind in WGHT:
            try: f.set_variation_by_axes(list(WGHT[kind]))
            except Exception: pass
        _fc[k] = f
    return _fc[k]


def text_img(s, size, kind='bold', fill=None, stroke=0, stroke_fill=None, shadow=0, glow=None):
    fill = P.c('over', (255, 255, 255)) if fill is None else fill
    stroke_fill = P.c('on-surface', INK) if stroke_fill is None else stroke_fill
    f = fontfor(kind, size, s)
    bb = f.getbbox(s, stroke_width=stroke)
    pad = int(size * 0.2 + shadow * 2.5 + (glow[1] * 2.5 if glow else 0)) + 4
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    pos = (pad - bb[0], pad - bb[1])
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow and P.shadows:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pos[0], pos[1] + shadow * 0.5), s, font=f, fill=(0, 0, 0, 160), stroke_width=stroke)
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(shadow)))
    if glow and P.glow:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).text(pos, s, font=f, fill=tuple(glow[0]) + (255,), stroke_width=int(size * 0.04))
        g = g.filter(ImageFilter.GaussianBlur(glow[1]))
        im = Image.alpha_composite(Image.alpha_composite(im, g), g)
    ImageDraw.Draw(im).text(pos, s, font=f, fill=tuple(fill) + (255,), stroke_width=stroke, stroke_fill=tuple(stroke_fill) + (255,))
    return im


def fit_text(s, max_w, kind='bold', start=400, **kw):
    size = start
    while size > 10 and fontfor(kind, size, s).getlength(s) > max_w: size = int(size * 0.92)
    return text_img(s, size, kind, **kw)


def rrect(w, h, r, fill, outline=None, width=0):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], int(P.r(r)), fill=fill, outline=outline, width=width)
    return im


def shadowed(im, blur=18, dy=10, alpha=120):
    pad = blur * 2 + abs(dy)
    out = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    if not P.shadows:  # same size, so everything lands where it would have
        out.alpha_composite(im, (pad, pad)); return out
    a = im.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 255)); sh.putalpha(a)
    out.paste(sh, (pad, pad + dy), sh)
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out


def to_np(im): return np.asarray(im.convert('RGBA'), dtype=np.float32) / 255.0


def comp(c, layer, x, y, alpha=1.0, behind=False, guard=False):
    """Alpha-composite an RGBA layer with its top-left at (x, y).
    behind=True hides it wherever the person is (so it sits behind you).
    guard=True only hides it where it would cover your face."""
    L = to_np(layer) if isinstance(layer, Image.Image) else layer
    h, w = L.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(c.W, x + w), min(c.H, y + h)
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    L = L[y0 - y:y1 - y, x0 - x:x1 - x]
    a = L[..., 3:4] * alpha
    m = c.m[y0:y1, x0:x1, None]
    if behind: a = a * (1 - m)
    elif guard:
        yy, xx = np.ogrid[y0:y1, x0:x1]
        e = ((xx - c.fx) / (c.fw * 0.95)) ** 2 + ((yy - c.fy) / (c.fw * 1.35)) ** 2
        a = a * (1 - np.clip((1.2 - e) / 0.3, 0, 1)[..., None] * m)
    dst = c.img[y0:y1, x0:x1]
    dst[:] = dst * (1 - a) + L[..., :3] * a


def place(c, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0, behind=False, guard=False):
    """Draw a PIL image centred on (cx, cy), scaled and rotated (degrees, counter-clockwise)."""
    if scale <= 0.01 or alpha <= 0: return
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05: im = im.rotate(rot, Image.BICUBIC, expand=True)
    comp(c, im, cx - im.width / 2, cy - im.height / 2, alpha, behind, guard)


def camera(c, zoom, cx, cy):
    """Zoom the whole frame (and the person mask) towards (cx, cy). Capped at 2x so it stays sharp."""
    zoom = min(zoom, 2.0)
    if zoom <= 1.002: return
    cw, ch = c.W / zoom, c.H / zoom
    x0 = clamp(cx - cw / 2, 0, c.W - cw); y0 = clamp(cy - ch / 2, 0, c.H - ch)
    M = np.float32([[zoom, 0, -x0 * zoom], [0, zoom, -y0 * zoom]])
    c.img = cv2.warpAffine(c.img, M, (c.W, c.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    c.m = cv2.warpAffine(c.m, M, (c.W, c.H), flags=cv2.INTER_LINEAR)
    c.fx, c.fy, c.fw = (c.fx - x0) * zoom, (c.fy - y0) * zoom, c.fw * zoom


def face_cam(c, zoom, head_at=0.40):
    """Zoom on the face, keeping it at `head_at` of the frame height."""
    z = min(zoom, 2.0)
    camera(c, z, c.fx, c.fy + (c.H / z) * (0.5 - head_at))


def grade(img, kind='moody'):
    lum = (img @ np.float32([0.299, 0.587, 0.114]))[..., None]
    if kind == 'bw':
        g = np.clip((lum - 0.5) * 1.25 + 0.5, 0, 1); return np.repeat(g, 3, axis=2)
    if kind == 'warm': return np.clip(img * np.float32([1.08, 1.0, 0.86]) + 0.02, 0, 1)
    if kind == 'cool': return np.clip(img * np.float32([0.9, 1.0, 1.1]), 0, 1)
    if kind == 'pop':
        o = lum + (img - lum) * 1.35; return np.clip((o - 0.5) * 1.12 + 0.5, 0, 1)
    # moody: a little darker, softer colour, teal shadows, warm highlights, gentle contrast
    o = lum + (img - lum) * 0.6
    o = np.power(np.clip(o, 0, 1), 1.3) * 0.88
    o = o + (1 - lum) * np.float32([-0.03, 0.035, 0.065]) + lum * np.float32([0.05, 0.015, -0.04])
    o = np.clip((o - 0.42) * 1.12 + 0.42, 0, 1)
    return o


_vig = {}


def vignette(c, strength=0.35):
    k = (c.W, c.H)
    if k not in _vig:
        yy, xx = np.ogrid[0:c.H, 0:c.W]
        d = ((xx - c.W / 2) / (c.W * 0.75)) ** 2 + ((yy - c.H / 2) / (c.H * 0.7)) ** 2
        _vig[k] = np.clip(d, 0, 1).astype(np.float32)
    c.img *= (1 - strength * _vig[k])[..., None]


def card(im, w, radius=0.07):
    """A reel-shaped (9:16) rounded card with a soft shadow."""
    h = int(w * 16 / 9)
    src = im.convert('RGB'); sw, sh = src.size
    s = max(w / sw, h / sh)
    src = src.resize((max(w, int(sw * s)), max(h, int(sh * s))), Image.LANCZOS)
    l, t = (src.width - w) // 2, (src.height - h) // 2
    src = src.crop((l, t, l + w, t + h)).convert('RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], int(P.r(w * radius)), fill=255)
    src.putalpha(m)
    ImageDraw.Draw(src).rounded_rectangle([0, 0, w - 1, h - 1], int(P.r(w * radius)), outline=(0, 0, 0, 70), width=2)
    return shadowed(src, blur=max(6, w // 16), dy=w // 22, alpha=150)


def vary(im, i):
    """Give each card its own look, so a pile of frames reads as different reels."""
    kind = ('pop', 'bw', 'warm', 'cool', 'moody')[i % 5]
    a = np.asarray(im.convert('RGB'), np.float32) / 255
    return Image.fromarray((grade(a, kind) * 255).astype(np.uint8))


def footage(c, x0=0, y0=0, x1=None, y1=None):
    """The mean colour of the frame inside a box, as 0..255 RGB. Pass it as P.c(role, neutral, on=footage(...))
    for a mark drawn straight on the video: a theme colour too close to what is underneath falls back to the
    theme colour that reads best there."""
    x0, y0 = int(clamp(x0, 0, c.W - 1)), int(clamp(y0, 0, c.H - 1))
    x1, y1 = int(clamp(c.W if x1 is None else x1, x0 + 1, c.W)), int(clamp(c.H if y1 is None else y1, y0 + 1, c.H))
    return tuple(int(v * 255) for v in c.img[y0:y1:4, x0:x1:4].reshape(-1, 3).mean(0))


def cached(e, key, fn):
    if key not in e.state: e.state[key] = fn()
    return e.state[key]


_grid = {}


def grid(c):
    if (c.W, c.H) not in _grid:
        yy, xx = np.mgrid[0:c.H, 0:c.W].astype(np.float32); _grid[(c.W, c.H)] = (xx, yy)
    return _grid[(c.W, c.H)]


def heart(size, color=None):
    color = P.c('danger', (255, 48, 64)) if color is None else color
    s = int(size); im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(s / 2 + s * 0.48 * (16 * math.sin(t) ** 3) / 16, s * 0.46 - s * 0.46 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
           for t in np.linspace(0, 2 * math.pi, 60)]
    d.polygon(pts, fill=color + (255,)); return im


def hand_path(d, pts, color, width, frac):
    n = max(2, int(len(pts) * clamp(frac)))
    if frac > 0: d.line(pts[:n], fill=color, width=width, joint='curve')
    return pts[n - 1]


def arrow_pts(x0, y0, x1, y1, bend=0.25, n=40):
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    return [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1) for t in np.linspace(0, 1, n)]


def arrow_head(d, pts, color, width, size):
    (xa, ya), (xb, yb) = pts[-4], pts[-1]; a = math.atan2(yb - ya, xb - xa)
    for s in (2.6, -2.6):
        d.line([(xb, yb), (xb + size * math.cos(a + s), yb + size * math.sin(a + s))], fill=color, width=width)


def pop(c, t0, dur=0.3): return ease_back((c.lt - t0) / dur) if c.lt > t0 else 0.0


def fade(c, e, t=0.2): return clamp((e.d - c.lt) / t)


def glass(c, w, h, r, cx, cy, amt=0.22, tint=(255, 255, 255), blur=None, alpha=240, dark=0.0, liquid=True):
    """A glass panel made from whatever sits behind it. liquid=True (default since 27 Oct 2026) is see-through liquid
    glass after liquid-glass-js (MIT, dashersw): light blur, refraction bending the room at the rim, a red/blue fringe
    (after React Bits' GlassSurface) and a specular edge lit from the top-left. liquid=False is the old frosted card."""
    w, h = int(w), int(h); blur = blur or max(8, c.W // 40); x0, y0 = int(cx - w / 2), int(cy - h / 2)
    if not P.glass:  # a theme without glass: a flat card in its own colours
        fill = P.c('dark', (20, 20, 22)) if dark >= 0.3 else P.c('surface', tint)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], int(P.r(r)), fill=fill + (alpha,),
                                             outline=P.c('line', (255, 255, 255), 255), width=max(2, c.W // 540))
        return im
    if not liquid:
        pad = blur * 2
        xs = np.clip(np.arange(x0 - pad, x0 + w + pad), 0, c.W - 1); ys = np.clip(np.arange(y0 - pad, y0 + h + pad), 0, c.H - 1)
        reg = cv2.GaussianBlur(np.ascontiguousarray(c.img[np.ix_(ys, xs)]), (0, 0), blur)[pad:pad + h, pad:pad + w]
        reg = reg * (1 - dark) * (1 - amt) + np.float32(tint) / 255 * amt
        im = Image.fromarray((np.clip(reg, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], int(r), fill=alpha); im.putalpha(m)
        ImageDraw.Draw(im).rounded_rectangle([1, 1, w - 2, h - 2], int(r), outline=(255, 255, 255, 120), width=max(2, c.W // 540))
        return im
    u = c.W / 2160; pad = int(140 * u) + 4
    xs = np.clip(np.arange(x0 - pad, x0 + w + pad), 0, c.W - 1); ys = np.clip(np.arange(y0 - pad, y0 + h + pad), 0, c.H - 1)
    tex = cv2.GaussianBlur(np.ascontiguousarray(c.img[np.ix_(ys, xs)]), (0, 0), max(3.0, blur * 0.3))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); r = max(2.0, float(r))
    q = np.stack([np.abs(xx - w / 2) - (w / 2 - r), np.abs(yy - h / 2) - (h / 2 - r)], -1)
    sdf = np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.maximum(q[..., 0], q[..., 1]), 0) - r
    d = np.maximum(-sdf, 0) / u
    nx, ny = xx - w / 2, yy - h / 2; nl = np.sqrt(nx * nx + ny * ny) + 1e-3; nx, ny = nx / nl, ny / nl
    k = (70 * np.exp(-d / 14) + 34 * np.exp(-d / 70) + 10 * np.exp(-d / 260)) * u
    out = np.zeros((h, w, 3), np.float32)
    for ch, fr in enumerate((1.10, 1.0, 0.90)):
        out[..., ch] = cv2.remap(tex[..., ch], (xx + pad + nx * k * fr).astype(np.float32), (yy + pad + ny * k * fr).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    out = out * (1 - dark * 0.3) * 0.9 + np.float32(tint) / 255 * amt * 0.25 + 0.05 * (1.0 - 0.30 * (yy / h))[..., None] - 0.04
    spec = np.exp(-d / 5) * np.clip(0.55 - 0.45 * (nx * 0.6 + ny * 0.8), 0, 1)
    out = np.clip(out + (spec * 0.85 + np.exp(-d / 30) * 0.10)[..., None], 0, 1)
    a = (np.clip(0.5 - sdf, 0, 1) * alpha).astype(np.uint8)
    im = Image.fromarray((out * 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray(a))
    return im


def face_chip(c, e, size):
    """A round avatar cut from your own face (grabbed once, at the start of the effect)."""
    def grab():
        r = c.fw * 0.9; x0, y0 = int(max(0, c.fx - r)), int(max(0, c.fy - r * 1.05))
        crop = c.img[y0:int(y0 + 2 * r), x0:int(x0 + 2 * r)]
        im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        return im
    src = cached(e, 'face', grab).resize((int(size), int(size)), Image.LANCZOS)
    m = Image.new('L', src.size, 0); ImageDraw.Draw(m).ellipse([0, 0, src.width - 1, src.height - 1], fill=255); src.putalpha(m)
    return src


def cursor(size):
    s = float(size); im = Image.new('RGBA', (int(s * 0.95), int(s * 1.45)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(3, 3), (3, s * 1.12), (s * 0.3, s * 0.87), (s * 0.5, s * 1.33), (s * 0.66, s * 1.26), (s * 0.46, s * 0.8), (s * 0.82, s * 0.8)]
    d.polygon(pts, fill=(255, 255, 255, 255)); d.line(pts + [pts[0]], fill=(0, 0, 0, 255), width=max(2, int(s / 14)), joint='curve')
    return shadowed(im, 6, 3, 110)


def tick(d, x, y, s, color=(255, 255, 255, 255), w=None):
    d.line([(x, y + s * 0.5), (x + s * 0.36, y + s * 0.85), (x + s, y + s * 0.1)], fill=color, width=w or max(3, int(s / 5)), joint='curve')


def lines_fit(lines, max_w, kind, start):
    size = start
    while size > 10 and max(font(kind, size).getlength(l) for l in lines) > max_w: size = int(size * 0.94)
    return size


def shift(c, dy):
    """Slide the whole picture (and you) down by dy pixels."""
    if abs(dy) < 0.5: return
    M = np.float32([[1, 0, 0], [0, 1, dy]])
    c.img = cv2.warpAffine(c.img, M, (c.W, c.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    c.m = cv2.warpAffine(c.m, M, (c.W, c.H), flags=cv2.INTER_LINEAR); c.fy += dy


def thumb_grid(cards, cols, rows, cell, gap, i0=0, look=True):
    im = Image.new('RGBA', (cols * cell + (cols - 1) * gap, rows * int(cell * 1.25) + (rows - 1) * gap), (0, 0, 0, 0))
    ch = int(cell * 1.25)
    for k in range(cols * rows):
        src = cards[(i0 + k) % len(cards)]; src = vary(src, i0 + k) if look else src.convert('RGB')
        sw, sh = src.size; s = max(cell / sw, ch / sh); t = src.resize((max(cell, int(sw * s)), max(ch, int(sh * s))), Image.LANCZOS)
        l, tp = (t.width - cell) // 2, int((t.height - ch) * 0.3); t = t.crop((l, tp, l + cell, tp + ch)).convert('RGBA')
        m = Image.new('L', t.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cell - 1, ch - 1], int(P.r(max(4, cell // 12))), fill=255); t.putalpha(m)
        im.alpha_composite(t, ((k % cols) * (cell + gap), (k // cols) * (ch + gap)))
    return im


def rich(parts, size, kind, base, accent, accent_kind=None, shadow=0):
    """One line of text where *starred* words take the accent colour (and optionally another font)."""
    segs = []
    for j, p in enumerate(parts.split('*')):
        if p: segs.append(text_img(p, size, accent_kind if (j % 2 and accent_kind) else kind, accent if j % 2 else base, shadow=shadow))
    pad = int(size * 0.2 + shadow * 2.5) + 4
    w = sum(s.width - 2 * pad for s in segs) + 2 * pad; h = max(s.height for s in segs)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for s in segs: im.alpha_composite(s, (x, (h - s.height) // 2)); x += s.width - 2 * pad
    return im


def np_thumb(c, w, h):
    """The current frame as a small PIL thumbnail (cropped to w:h around your face)."""
    ar = w / h; ch = c.H * 0.62; cw = ch * ar
    x0 = int(clamp(c.fx - cw / 2, 0, c.W - cw)); y0 = int(clamp(c.fy - ch * 0.4, 0, c.H - ch))
    crop = c.img[y0:int(y0 + ch), x0:int(x0 + cw)]
    return Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8)).resize((int(w), int(h)), Image.LANCZOS)


def glow_panel(w, h, r, top, bot, line, glow, gblur):
    """A rounded panel with a vertical gradient fill, a thin border and an outer glow."""
    w, h = int(w), int(h); pad = int(gblur * 2.2); r = P.r(r)
    if not P.gradients: top = bot
    if not P.glow: glow = (0, 0, 0, 0)
    out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    g = Image.new('RGBA', out.size, (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=glow)
    out.alpha_composite(g.filter(ImageFilter.GaussianBlur(gblur)))
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    fill = (np.float32(top) * (1 - t) + np.float32(bot) * t) * np.ones((1, w, 1), np.float32)
    body = Image.fromarray(np.concatenate([fill, np.full((h, w, 1), 255, np.float32)], 2).astype(np.uint8), 'RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); body.putalpha(m)
    ImageDraw.Draw(body).rounded_rectangle([1, 1, w - 2, h - 2], r, outline=line, width=max(2, int(w / 400)))
    out.alpha_composite(body, (pad, pad))
    return out, pad


def np_thumb_pil(im, w, h):
    src = im.convert('RGB'); s = max(w / src.width, h / src.height)
    t = src.resize((max(w, int(src.width * s) + 1), max(h, int(src.height * s) + 1)), Image.LANCZOS)
    l, tp = (t.width - w) // 2, int((t.height - h) * 0.3); t = t.crop((l, tp, l + w, tp + h)).convert('RGBA')
    m = Image.new('L', t.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], int(P.r(max(3, w // 10))), fill=255); t.putalpha(m)
    return t
