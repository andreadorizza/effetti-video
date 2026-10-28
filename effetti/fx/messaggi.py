"""messaggi (messages): Notifiche di iMessage compaiono una dopo l'altra, vetro color crema con un leggero bagliore.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def msg_bubble(c, y, title, body, a):
    """One creamy glass iMessage notification with a soft white halo, centred at height y."""
    u = c.W / 2160; w, h = int(1880 * u), int(330 * u); x0 = (c.W - w) // 2; y0 = int(y - h / 2)
    if a <= 0 or y0 + h < 0 or y0 > c.H: return
    s = 0.82 + 0.18 * ease_back(a); ww, hh = int(w * s), int(h * s); xs, ys = (c.W - ww) // 2, int(y - hh / 2)
    if P.glow:   # the soft halo
        halo = Image.new('RGBA', (ww + int(240 * u), hh + int(240 * u)), (0, 0, 0, 0)); p = int(120 * u)
        ImageDraw.Draw(halo).rounded_rectangle([p - 30 * u, p - 30 * u, p + ww + 30 * u, p + hh + 30 * u], int(P.r(100 * u)), fill=P.c('surface', (255, 250, 240), int(215 * clamp(a * 2))))
        comp(c, halo.filter(ImageFilter.GaussianBlur(56 * u)), xs - p, ys - p)
    gx0, gy0, gx1, gy1 = max(0, xs), max(0, ys), min(c.W, xs + ww), min(c.H, ys + hh)
    if gx1 <= gx0 or gy1 <= gy0: return
    tint = np.float32(P.c('surface', (252, 246, 238))) / 255   # cream glass (a flat cream card without glass)
    if P.glass:
        reg = cv2.GaussianBlur(c.img[gy0:gy1, gx0:gx1], (0, 0), 20 * u)
        yy = np.linspace(0, 1, gy1 - gy0, dtype=np.float32)[:, None, None]
        reg = reg * (1 - 0.78) + tint * 0.78 + ((1 - yy) * 0.08 if P.gradients else 0)
    else:
        reg = np.broadcast_to(tint, (gy1 - gy0, gx1 - gx0, 3))
    mk = Image.new('L', (ww, hh), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, ww - 1, hh - 1], int(P.r(70 * u * s)), fill=255)
    mk = np.asarray(mk, np.float32)[gy0 - ys:gy1 - ys, gx0 - xs:gx1 - xs, None] / 255 * clamp(a * 2.5)
    dst = c.img[gy0:gy1, gx0:gx1]; dst[:] = dst * (1 - mk) + np.clip(reg, 0, 1) * mk
    lay = Image.new('RGBA', (ww, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); v = s * u; al = int(255 * clamp(a * 2.5))
    d.rounded_rectangle([1, 1, ww - 2, hh - 2], int(P.r(70 * v)), outline=P.c('line', (255, 255, 255), int(170 * clamp(a * 2.5))), width=max(1, int(3 * v)))
    ic = np.linspace(0, 1, int(160 * v), dtype=np.float32)[:, None]
    t0, t1 = P.c('success', (110, 232, 120)), P.c('success', (46, 181, 69))   # the green app icon, top to bottom
    if not P.gradients: t0 = t1
    icon = np.dstack([t0[0] - ic * (t0[0] - t1[0]), t0[1] - ic * (t0[1] - t1[1]), t0[2] - ic * (t0[2] - t1[2]), np.full_like(ic, 255)]).repeat(int(160 * v), 1).astype(np.uint8)
    icon = Image.fromarray(icon, 'RGBA'); im_ = Image.new('L', icon.size, 0); ImageDraw.Draw(im_).rounded_rectangle([0, 0, icon.width - 1, icon.height - 1], int(P.r(40 * v)), fill=al); icon.putalpha(im_)
    bub = P.c('on-accent', (255, 255, 255), al)
    ImageDraw.Draw(icon).ellipse([30 * v, 34 * v, 130 * v, 114 * v], fill=bub); ImageDraw.Draw(icon).polygon([(44 * v, 102 * v), (36 * v, 130 * v), (72 * v, 110 * v)], fill=bub)
    lay.alpha_composite(icon, (int(56 * v), int(70 * v)))
    d.text((262 * v, 76 * v), title, font=fontfor('uib', 72 * v, title), fill=P.c('on-surface', (28, 28, 30), al)); d.text((262 * v, 170 * v), body, font=fontfor('uim', 76 * v, body), fill=P.c('on-surface', (44, 44, 46), al))
    comp(c, lay, xs, ys)


@effetto('messaggi', en='messages', alias=('imessage', 'messages', 'notifications', 'notifiche', 'texts'),
         desc="Notifiche di iMessage compaiono una dopo l'altra, vetro color crema con un leggero bagliore")
def fx_messages(c, e):
    msgs = (e.o.get('text') or tr("ma come l'hai montato??|aspetta, che app è questa|mandami gli effetti pls|EFFETTI",
                                  'how did you edit this??|wait, which app is this|send me the effects pls|EFFECTS')).split('|')
    title = e.o.get('title', tr('Messaggi', 'Messages')); n = len(msgs); u = c.W / 2160
    gap = min(0.4, e.d * 0.75 / max(1, n)); pops = [0.13 + i * gap for i in range(n)]
    bottom = c.H * float(e.o.get('y', 0.61)); out = fade(c, e, 0.2)
    for k in range(n):
        if c.lt < pops[k]: continue
        newer = sum(ease_out(clamp((c.lt - pops[j]) / 0.17)) for j in range(k + 1, n) if c.lt >= pops[j])
        msg_bubble(c, bottom - 165 * u - newer * 365 * u, title, msgs[k], clamp((c.lt - pops[k]) / 0.17) * out)
