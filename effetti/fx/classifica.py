"""classifica (tier-list): Arriva una tier list e Claude vola in fascia S.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('classifica', en='tier-list', alias=('tier', 'tier-list', 'tiers'),
         desc='Arriva una tier list e Claude vola in fascia S')
def fx_tier_list(c, e):
    W, H = c.W, c.H; al = fade(c, e)
    ttl = cached(e, 'ttl', lambda: fit_text(e.o.get('title', 'best way to edit a reel?'), W * 0.88, 'serif', int(W * 0.11), fill=YELLOW, shadow=8))
    place(c, ttl, W / 2, max(ttl.height * 0.6, c.fy - c.fw * 1.65), 0.9 + 0.1 * ease_out(c.lt / 0.3), 0, al * clamp(c.lt / 0.15), behind=True)
    tiers = [('S', (255, 127, 127)), ('A', (255, 191, 127)), ('B', (255, 223, 127)), ('C', (191, 255, 127)), ('D', (127, 191, 255)), ('F', (191, 127, 255))]
    cw = int(W * 0.66); rh = int(W * 0.082); pad = int(W * 0.015); chh = pad * 2 + rh * 6 + pad * 5
    fill = dict(zip('BCDF', e.o.get('others', 'templates|timelines|apps|doing it by hand').split('|')))
    def board():
        im = rrect(cw, chh, W * 0.025, (22, 22, 26, 240)); d = ImageDraw.Draw(im)
        for i, (lab, col) in enumerate(tiers):
            y = pad + i * (rh + pad)
            d.rounded_rectangle([pad, y, pad + rh, y + rh], rh * 0.14, fill=col + (255,))
            d.text((pad + rh / 2, y + rh / 2), lab, font=font('uib', rh * 0.5), fill=(20, 20, 22, 255), anchor='mm')
            d.rounded_rectangle([pad * 2 + rh, y, cw - pad, y + rh], rh * 0.14, fill=(40, 40, 46, 255))
            if lab in fill:
                f = font('uim', rh * 0.3); tw = f.getlength(fill[lab]) + rh * 0.4
                d.rounded_rectangle([pad * 3 + rh, y + rh * 0.15, pad * 3 + rh + tw, y + rh * 0.85], rh * 0.12, fill=(78, 78, 86, 255))
                d.text((pad * 3 + rh + rh * 0.2, y + rh / 2), fill[lab], font=f, fill=(225, 225, 230, 255), anchor='lm')
        return shadowed(im, 18, 10, 120)
    bd = cached(e, 'bd', board)
    top = min(H * 0.95 - bd.height, max(c.fy + c.fw * 1.4, H * 0.45))
    k = ease_back(c.lt / 0.35); bx, by = W / 2, top + bd.height / 2 + (1 - k) * H * 0.15
    place(c, bd, bx, by, 1, 0, al * clamp(c.lt / 0.12), guard=True)
    tile = cached(e, 'tile', lambda: shadowed(rrect(int(rh * 2.6), int(rh * 0.8), rh * 0.16, ORANGE + (255,)), 8, 4, 100))
    tx = cached(e, 'tx', lambda: text_img(e.o.get('item', 'Claude'), rh * 0.36, 'uib', (255, 255, 255)))
    tl = tile.copy(); tl.alpha_composite(tx, ((tl.width - tx.width) // 2, (tl.height - tx.height) // 2 - 3))
    sx, sy = W * 0.86, c.fy + c.fw * 0.4
    ex = bx - bd.width / 2 + 18 + pad * 3 + rh + tile.width / 2 - 10; ey = by - bd.height / 2 + 18 + pad + rh / 2
    q = ease_back((c.lt - 0.45) / 0.4)
    if c.lt > 0.4: place(c, tl, sx + (ex - sx) * q, sy + (ey - sy) * q, 1.25 - 0.25 * clamp(q), 18 * (1 - clamp(q)), al, guard=True)
