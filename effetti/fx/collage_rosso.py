"""collage-rosso (red-collage): Tu in bianco e nero, una parola rossa gigante dietro, tre righe che entrano di colpo.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('collage-rosso', en='red-collage', alias=('collage', 'red-collage'),
         desc='Tu in bianco e nero, una parola rossa gigante dietro, tre righe che entrano di colpo')
def fx_red_collage(c, e):
    k = ramp(c, e, 0.15, 0); m = c.m[..., None]
    bw = grade(c.img, 'bw'); out = bw * m + bw * 0.62 * (1 - m)
    c.img = c.img * (1 - k) + out * k
    vignette(c, 0.45 * k)
    # the red is the accent on a darkened room: a theme accent that would vanish there falls back to what reads
    red = cached(e, 'red', lambda: rgb(e.o.get('color'), P.c('accent', RED, on=footage(c, 0, 0, c.W, c.H * 0.45)))); al = fade(c, e)
    w = cached(e, 'w', lambda: fit_text(e.o.get('text', tr('MONTA', 'EDIT')).upper(), c.W * 0.98, 'uib', 700, fill=red, glow=(red, 34)))
    s = 1.12 - 0.12 * ease_out(c.lt / 0.4)
    place(c, w, c.W / 2, max(w.height * 0.42, c.fy - c.fw * 1.05), s, 0, clamp(c.lt / 0.12) * al, behind=True)
    lines = e.o.get('lines', tr('UNA CLIP.|22 EFFETTI.|NIENTE APP.', 'ONE CLIP.|22 EFFECTS.|ZERO APPS.')).split('|')
    size = cached(e, 'sz', lambda: lines_fit(lines, c.W * 0.8, 'uib', int(c.W * 0.14)))
    y = max(c.H * 0.5, c.fy + c.fw * 1.55)
    for j, ln in enumerate(lines):
        im = cached(e, ('l', j), lambda: text_img(ln, size, 'uib', red if j == 1 else P.c('over', (255, 255, 255)), shadow=8))
        kk = clamp((c.lt - 0.18 - 0.13 * j) / 0.16)
        if kk > 0: place(c, im, c.W * 0.05 + im.width / 2, y + im.height / 2, 1.4 - 0.4 * ease_out(kk), 0, kk * al, guard=True)
        y += size * 1.0
    tag = cached(e, 'tag', lambda: text_img(e.o.get('tag', tr('REC  ·  COLLAGE ROSSO', 'REC  ·  RED COLLAGE')), c.W * 0.027, 'mono', red))
    dot = Image.new('RGBA', (int(tag.height * 0.4),) * 2, (0, 0, 0, 0)); ImageDraw.Draw(dot).ellipse([0, 0, dot.width - 1, dot.width - 1], fill=rgb(e.o.get('color'), P.c('danger', RED, on=footage(c, 0, c.H * 0.88, c.W * 0.3, c.H * 0.98))) + (255,))
    blink = 1.0 if int(c.lt * 2.5) % 2 == 0 else 0.35
    place(c, dot, c.W * 0.07, c.H * 0.93, alpha=al * k * blink, guard=True)
    place(c, tag, c.W * 0.07 + dot.width + tag.width / 2, c.H * 0.93, alpha=al * k, guard=True)
