"""parola-pastello (pastel-word): Stanza lilla, una parola gigante dietro di te, una scheda profilo che riceve un Segui.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *

_grad = {}


@effetto('parola-pastello', en='pastel-word', alias=('pastel', 'pastel-word', 'pastello'),
         desc='Stanza lilla, una parola gigante dietro di te, una scheda profilo che riceve un Segui')
def fx_pastel_word(c, e):
    W, H = c.W, c.H; k = ramp(c, e, 0.2, 0); m = c.m[..., None]; al = fade(c, e)
    key = (W, H, P.get('ground'), P.gradients)   # the lavender room, or the theme's ground (flat without gradients)
    if key not in _grad:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); t = np.clip((yy / H) * 0.8 + (xx / W) * 0.2, 0, 1)[..., None]
        top, bot = P.f('ground', [0.70, 0.67, 0.97]), P.f('ground', [0.93, 0.90, 1.0])
        if not P.gradients: bot = top
        _grad[key] = top * (1 - t) + bot * t
    lum = (c.img @ np.float32([0.299, 0.587, 0.114]))[..., None]
    bg = _grad[key] * (0.86 + 0.22 * lum)
    you = np.clip(c.img * 0.93 + 0.05, 0, 1)
    c.img = c.img * (1 - k) + (you * m + bg * (1 - m)) * k
    word = cached(e, 'w', lambda: fit_text(e.o.get('text', tr('REEL', 'REELS')).upper(), W * 0.96, 'uib', 700, fill=P.c('on-surface', (255, 255, 255))))
    dk = ease_out(c.lt / 0.45)
    place(c, shadowed(word, 24, 12, 60), W / 2, max(word.height * 0.45, c.fy - c.fw * 1.2) - (1 - dk) * H * 0.06, 1, 0, al * clamp(c.lt / 0.15), behind=True)
    cw, chh = W * 0.86, W * 0.15; cy = H * 0.865 + (1 - ease_out((c.lt - 0.15) / 0.35)) * H * 0.2
    fill = P.c('surface', (255, 255, 255)); edge = P.c('line', (255, 255, 255), 255) if fill == P.c('ground', (178, 171, 247)) else None  # a card the room's colour gets an edge
    card_ = rrect(cw, chh, chh * 0.3, fill + (248,), edge, max(2, int(W / 540)) if edge else 0); d = ImageDraw.Draw(card_)
    av = face_chip(c, e, chh * 0.64); card_.alpha_composite(av, (int(chh * 0.18), int((chh - av.height) / 2)))
    d.text((chh * 0.98, chh * 0.38), e.o.get('name', tr('Il tuo nome', 'Vibha')), font=font('uib', chh * 0.22), fill=P.c('on-surface', (20, 20, 22), 255), anchor='lm')
    h1 = e.o.get('handle', tr('@il.tuo.profilo  ·  ', '@vibha.in.progress  ·  ')); f = font('uim', chh * 0.15)
    d.text((chh * 0.98, chh * 0.66), h1, font=f, fill=P.c('muted', (140, 140, 150), 255), anchor='lm')
    d.text((chh * 0.98 + f.getlength(h1), chh * 0.66), e.o.get('role', 'creator'), font=f, fill=P.c('accent', PURPLE, 255), anchor='lm')
    at = e.d * 0.6; on = c.lt >= at
    bx = cw - chh * 0.22
    d.text((bx, chh / 2), tr('Segui già', 'Following') if on else tr('Segui', 'Follow'), font=font('uib', chh * 0.2), fill=(P.c('muted', (140, 140, 150), 255) if on else P.c('accent', PURPLE, 255)), anchor='rm')
    sq = 1 - 0.06 * math.sin(math.pi * clamp((c.lt - at) / 0.25)) if on else 1
    place(c, shadowed(card_, 18, 8, 90), W / 2, cy, sq, 0, al * clamp((c.lt - 0.15) / 0.12), guard=True)
    cu = cached(e, 'cur', lambda: cursor(W * 0.06))
    ck = ease_inout((c.lt - 0.25) / max(0.2, at - 0.3))
    tx, ty = W / 2 + cw / 2 - chh * 0.55, cy + chh * 0.12
    sx, sy = W * 1.02, H * 1.02
    place(c, cu, sx + (tx - sx) * ck + cu.width / 2, sy + (ty - sy) * ck + cu.height / 2, 0.85 if on and c.lt - at < 0.15 else 1, 0, al * clamp((c.lt - 0.25) / 0.1))
