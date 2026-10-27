"""timeline (timeline): Look da film rosso scuro con una timeline di montaggio, un timecode REC e una testina luminosa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def red_timeline(c, e):
    W, H = c.W, c.H; k = ramp(c, e, 0.2, 0); m = c.m[..., None]; al = fade(c, e)
    lum = (c.img @ np.float32([0.299, 0.587, 0.114]))[..., None]
    bg = np.clip(lum * np.float32([1.05, 0.3, 0.27]) * 0.85, 0, 1)
    you = np.clip(c.img * np.float32([1.04, 0.86, 0.82]), 0, 1)
    c.img = c.img * (1 - k) + (you * m + bg * (1 - m)) * k; vignette(c, 0.5 * k)
    red = rgb(e.o.get('color'), (255, 52, 44))
    sl = (1 - ease_out(c.lt / 0.35)) * W * 0.08; tb = clamp(c.lt / 0.15) * al
    secs = 21 + int(c.lt * 3)
    rec = text_img(f"{e.o.get('tc', 'REC')} 00:{secs:02d}", W * 0.032, 'mono', red)
    dot = Image.new('RGBA', (int(rec.height * 0.36),) * 2, (0, 0, 0, 0)); ImageDraw.Draw(dot).ellipse([0, 0, dot.width - 1, dot.width - 1], fill=red + (255,))
    comp(c, dot, W * 0.065 - sl, H * 0.075 + (rec.height - dot.height) / 2, tb * (1.0 if int(c.lt * 2.5) % 2 == 0 else 0.35), guard=True)
    comp(c, rec, W * 0.065 + dot.width * 1.4 - sl, H * 0.075, tb, guard=True)
    ti = cached(e, 'ti', lambda: text_img(e.o.get('text', 'AUTO-EDIT'), W * 0.13, 'uib', (255, 255, 255), shadow=10))
    comp(c, ti, W * 0.055 - sl, H * 0.075 + rec.height * 0.85, tb, guard=True)
    su = cached(e, 'su', lambda: text_img(e.o.get('sub', 'timeline by Claude'), W * 0.037, 'uim', red))
    comp(c, su, W * 0.065 - sl, H * 0.075 + rec.height * 0.85 + ti.height * 0.88, tb, guard=True)
    pw, phh = int(W * 0.9), int(H * 0.19); py = H * 0.755 + (1 - ease_out((c.lt - 0.1) / 0.35)) * H * 0.3
    lay = rrect(pw, phh, W * 0.03, (14, 10, 10, 215), (255, 70, 60, 90), 2); d = ImageDraw.Draw(lay)
    for j in range(4): d.text((pw * (0.05 + 0.3 * j), phh * 0.12), f'00:0{j}', font=font('mono', W * 0.022), fill=(170, 170, 175, 255), anchor='lm')
    clips = cached(e, 'cl', lambda: [(r, a, b) for r, segs in enumerate([[(0.04, 0.24), (0.26, 0.5), (0.53, 0.76), (0.79, 0.96)],
                                                                            [(0.04, 0.3), (0.33, 0.45), (0.48, 0.7)], [(0.04, 0.55), (0.6, 0.96)]]) for a, b in segs])
    p = 0.04 + 0.92 * clamp(c.lt / (e.d * 0.95)); ph_x = pw * p
    glow = Image.new('RGBA', (pw, phh), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for r, a, b in clips:
        y0 = phh * (0.27 + 0.235 * r); x0, x1 = pw * a, pw * b; on = pw * a < ph_x
        fill = red + (255,) if on else (120, 30, 28, 255)
        d.rounded_rectangle([x0, y0, x1, y0 + phh * 0.17], phh * 0.04, fill=fill)
        if on: gd.rounded_rectangle([x0, y0, x1, y0 + phh * 0.17], phh * 0.04, fill=red + (200,))
    d.line([(ph_x, phh * 0.2), (ph_x, phh * 0.97)], fill=(255, 255, 255, 255), width=max(3, W // 300))
    gd.line([(ph_x, phh * 0.2), (ph_x, phh * 0.97)], fill=(255, 255, 255, 255), width=max(8, W // 100))
    lay = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(W // 90)), lay)
    comp(c, lay, (W - pw) / 2, py, al, guard=True)


@effetto('timeline', en='timeline', alias=('auto-edit', 'montaggio', 'timeline'),
         desc='Look da film rosso scuro con una timeline di montaggio, un timecode REC e una testina luminosa', schede=True)
def fx_timeline(c, e):
    studio = globals().get('studio_timeline')
    (studio if studio and e.o.get('look') != 'red' else red_timeline)(c, e)
