"""muro-profilo (profile-wall): La griglia delle tue reel riempie il muro dietro di te mentre un contatore sale.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('muro-profilo', en='profile-wall', alias=('profile-wall', 'wall'),
         desc='La griglia delle tue reel riempie il muro dietro di te mentre un contatore sale', schede=True)
def fx_profile_wall(c, e):
    W, H = c.W, c.H; al = fade(c, e)
    def wall():
        pw = int(W * 0.92); ph = int(H * 0.36); im = rrect(pw, ph, W * 0.035, P.c('dark', (16, 16, 18), 240)); d = ImageDraw.Draw(im)
        tabs = (tr('Post', 'Posts'), tr('Reel', 'Reels'), tr('Taggati', 'Tagged')); f = font('uim', W * 0.032)
        for j, tb in enumerate(tabs):
            x = pw * (0.2 + 0.3 * j); d.text((x, ph * 0.06), tb, font=f, fill=(P.c('on-dark', (255, 255, 255), 255) if j == 1 else P.c('muted', (130, 130, 136), 255)), anchor='mm')
            if j == 1: d.rectangle([x - pw * 0.08, ph * 0.1, x + pw * 0.08, ph * 0.1 + 4], fill=P.c('on-dark', (255, 255, 255), 255))
        gr = thumb_grid(e.cards, 4, 2, int(pw * 0.225), int(pw * 0.012), look=False)
        im.alpha_composite(gr, ((pw - gr.width) // 2, int(ph * 0.14))); return shadowed(im, 20, 10, 110)
    wl = cached(e, 'wall', wall)
    place(c, wl, W / 2, H * 0.04 + wl.height / 2, 0.94 + 0.06 * ease_out(c.lt / 0.35), 0, al * clamp(c.lt / 0.15), behind=True)
    cw, chh = W * 0.76, W * 0.25; cy = min(H * 0.86, c.fy + c.fw * 2.6)
    # a dark glass card; a theme without glass gets glass()'s flat surface card, so the type on it is on-surface
    g = glass(c, cw, chh, chh * 0.18, W / 2, cy, amt=0.5, tint=(12, 12, 14)); d = ImageDraw.Draw(g)
    target = int(e.o.get('count', 197000)); n = int(target * ease_out((c.lt - 0.2) / 0.8))
    swap = clamp((c.lt - 1.15) / 0.2); ink = on_glass((255, 255, 255))
    if swap < 1: d.text((cw / 2, chh * 0.33), num(f'{n:,}'), font=font('uib', chh * 0.3), fill=ink + (int(255 * (1 - swap)),), anchor='mm')
    if swap > 0:
        lab = e.o.get('label', tr('visualizzazioni', 'views')); fl = fontfor('uib', chh * 0.3, lab)
        if fl.getlength(lab) > cw * 0.92: fl = fontfor('uib', chh * 0.3 * cw * 0.92 / fl.getlength(lab), lab)  # a longer word still fits the card
        d.text((cw / 2, chh * 0.33), lab, font=fl, fill=ink + (int(255 * swap),), anchor='mm')
    av = face_chip(c, e, chh * 0.3); g.alpha_composite(av, (int(chh * 0.14), int(chh * 0.58)))
    name = e.o.get('name', tr('il.tuo.profilo', 'vibha.in.progress')); sub = e.o.get('sub', tr('reel più vista', 'top reel'))
    d.text((chh * 0.52, chh * 0.68), name, font=fontfor('uib', chh * 0.09, name), fill=ink + (255,), anchor='lm')
    d.text((chh * 0.52, chh * 0.8), sub, font=fontfor('uim', chh * 0.075, sub), fill=P.c('muted', (170, 170, 176), 255), anchor='lm')
    on = c.lt >= e.d * 0.7
    d.rounded_rectangle([cw - chh * 0.95, chh * 0.62, cw - chh * 0.14, chh * 0.86], P.r(chh * 0.12), fill=(P.c('line', (60, 60, 66), 255) if on else P.c('accent', (255, 255, 255), 255)))
    d.text((cw - chh * 0.545, chh * 0.74), tr('Segui già', 'Following') if on else tr('Segui', 'Follow'), font=font('uib', chh * 0.08),
           fill=(on_glass((255, 255, 255), 255) if on else P.c('on-accent', (16, 16, 18), 255)), anchor='mm')
    place(c, g, W / 2, cy + (1 - ease_out((c.lt - 0.05) / 0.3)) * H * 0.1, 1, 0, al * clamp((c.lt - 0.05) / 0.12), guard=True)
