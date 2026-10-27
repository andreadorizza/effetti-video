"""passaggi (checklist): Una lista di passaggi di Claude sotto il mento: ogni passo gira, poi si spunta in verde.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('passaggi', en='checklist', alias=('checklist', 'tasks'),
         desc='Una lista di passaggi di Claude sotto il mento: ogni passo gira, poi si spunta in verde')
def fx_checklist(c, e):
    W, H = c.W, c.H; u = W / 1080; al = fade(c, e)
    rows = [x.split('::') for x in e.o.get('text', 'Found your face::every frame|Cut you out of the room::AI mask|Put the text behind you::depth|'
                                        'Graded the colour::warm|Rendered in 4K::2160p').split('|')]
    n = len(rows); cw = W * 0.9; rh = 104 * u; hh = 120 * u; chh = hh + rh * n + 26 * u
    y0 = min(max(c.fy + c.fw * 1.35, H * 0.42), H * 0.93 - chh); cy = y0 + chh / 2 + (1 - ease_out(c.lt / 0.35)) * H * 0.12
    span = max(0.4, e.d - 0.55); done_at = [0.3 + span * (i + 1) / n for i in range(n)]
    g = glass(c, cw, chh, 40 * u, W / 2, cy, amt=0.78, tint=(14, 13, 16), blur=int(30 * u)); d = ImageDraw.Draw(g)
    sx, sy = 44 * u, hh / 2
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        d.line([(sx, sy), (sx + 18 * u * math.cos(ang), sy + 18 * u * math.sin(ang))], fill=(217, 119, 87, 255), width=int(7 * u))
        d.line([(sx, sy), (sx + 18 * u * math.cos(ang + math.pi / 4), sy + 18 * u * math.sin(ang + math.pi / 4))], fill=(217, 119, 87, 255), width=int(5 * u))
    d.text((80 * u, hh / 2), e.o.get('title', 'Claude is editing your clip'), font=font('uib', 42 * u), fill=(255, 255, 255, 255), anchor='lm')
    nd = sum(c.lt >= t for t in done_at)
    d.text((cw - 36 * u, hh / 2), f'{nd} of {n}', font=font('uim', 28 * u), fill=(170, 170, 176, 255), anchor='rm')
    d.line([(30 * u, hh), (cw - 30 * u, hh)], fill=(255, 255, 255, 30), width=max(1, int(2 * u)))
    for i, (txt, meta) in enumerate([(r + [''])[:2] for r in rows]):
        y = hh + 13 * u + rh * i + rh / 2; x = 56 * u; r_ = 24 * u
        start = done_at[i - 1] if i else 0.3
        if c.lt >= done_at[i]:
            q = ease_back((c.lt - done_at[i]) / 0.25); rr = r_ * (0.6 + 0.4 * q)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(52, 199, 89, 255)); tick(d, x - rr * 0.5, y - rr * 0.45, rr, w=int(5 * u))
            fc, mc = (255, 255, 255, 255), (52, 199, 89, 255)
        elif c.lt >= start:
            a0 = (c.lt * 540) % 360; d.ellipse([x - r_, y - r_, x + r_, y + r_], outline=(255, 255, 255, 50), width=int(5 * u))
            d.arc([x - r_, y - r_, x + r_, y + r_], a0, a0 + 100, fill=(217, 119, 87, 255), width=int(5 * u)); fc, mc = (255, 255, 255, 255), (170, 170, 176, 255)
        else:
            d.ellipse([x - r_, y - r_, x + r_, y + r_], outline=(255, 255, 255, 60), width=int(4 * u)); fc, mc = (255, 255, 255, 110), (170, 170, 176, 90)
        d.text((x + 48 * u, y), txt, font=font('uib', 40 * u), fill=fc, anchor='lm')
        d.text((cw - 36 * u, y), meta, font=font('mono', 28 * u), fill=mc, anchor='rm')
    place(c, shadowed(g, 24, 12, 120), W / 2, cy, 1, 0, al * clamp(c.lt / 0.12), guard=True)
