"""ventaglio (phone-fan): Le tue reel si aprono a ventaglio come una mano di telefoni, sotto un titolo.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('ventaglio', en='phone-fan', alias=('fan', 'phone-fan', 'telefoni'),
         desc='Le tue reel si aprono a ventaglio come una mano di telefoni, sotto un titolo', schede=True)
def fx_phone_fan(c, e):
    W, H = c.W, c.H; al = fade(c, e)
    lines = e.o.get('text', '22 effects.|zero editing apps.').split('|')
    S = cached(e, 'sz', lambda: lines_fit(lines, W * 0.84, 'uib', int(W * 0.08)))
    y = max(H * 0.06, c.fy - c.fw * 1.3 - S * 1.3 * len(lines))
    for j, ln in enumerate(lines):
        kj = clamp((c.lt - 0.05 - 0.1 * j) / 0.18); last = j == len(lines) - 1
        t = cached(e, ('t', j), lambda: text_img(ln, S, 'uib', (16, 16, 18) if last else (255, 255, 255), shadow=0 if last else 9))
        if last: comp(c, rrect(t.width - S * 0.15, S * 1.22, S * 0.08, (255, 255, 255, 255)), W / 2 - (t.width - S * 0.15) / 2, y, al * kj, guard=True)
        place(c, t, W / 2, y + S * 0.6, 1, 0, al * kj, guard=True); y += S * 1.3
    pw = int(W * 0.23); ph = int(pw * 2.0)
    def phone(i):
        im = rrect(pw, ph, pw * 0.16, (14, 14, 16, 255))
        scr = card(vary(e.cards[i % len(e.cards)], i) if e.o.get('images') is None else e.cards[i % len(e.cards)], pw - 10)
        inner = scr.crop(((scr.width - (pw - 10)) // 2, (scr.height - (ph - 10)) // 2 - 6, (scr.width + pw - 10) // 2, (scr.height + ph - 10) // 2 - 6))
        im.alpha_composite(inner, (5, 5))
        ImageDraw.Draw(im).rounded_rectangle([pw * 0.36, ph * 0.025, pw * 0.64, ph * 0.045], pw * 0.03, fill=(0, 0, 0, 255))
        return shadowed(im, 14, 8, 120)
    ph_ = cached(e, 'ph', lambda: [phone(i) for i in range(4)])
    cx = W / 2 * 0.5 + c.fx * 0.5; cy = max(c.fy + c.fw * 1.1 + ph / 2, H * 0.62)
    cy = min(cy, H - ph * 0.42)
    for i, o in enumerate((-1.5, -0.5, 0.5, 1.5)):
        q = ease_back((c.lt - 0.2 - 0.06 * i) / 0.4)
        place(c, ph_[i], cx + o * W * 0.19 * q, cy + o * o * W * 0.025 * q, 0.9, -o * 11 * q, al * clamp((c.lt - 0.2) / 0.1), guard=True)
