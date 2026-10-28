"""da-fare (todo): Una lista accanto alla testa che si spunta mentre parli.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('da-fare', en='todo', alias=('lista', 'the-to-do', 'the-todo', 'to-do', 'todo'),
         desc='Una lista accanto alla testa che si spunta mentre parli')
def fx_todo(c, e):
    items = e.o.get('text', tr('trascina il video in Claude|installa la skill|scrivi /effetti',
                               'drop your video into Claude|install the skill|type /effects')).split('|')
    # ticks = video seconds when each item gets ticked (e.g. when you say it); default is evenly spaced
    ticks = [float(t) - e.start for t in str(e.o['ticks']).split('|')] if e.o.get('ticks') else [e.d * (i + 1) / (len(items) + 1) for i in range(len(items))]
    cw = int(c.W * 0.5); lh = int(cw * 0.13); pad = int(cw * 0.07)
    im = rrect(cw, pad * 2 + lh * (len(items) + 1), cw * 0.07, P.c('surface', (250, 248, 242), 235)); d = ImageDraw.Draw(im)
    done = sum(c.lt >= t for t in ticks)
    title = e.o.get('title', tr('DA FARE', 'TO DO')).upper(); count = tr(f'{done} di {len(items)}', f'{done} of {len(items)}')
    d.text((pad, pad), title, font=fontfor('ui', lh * 0.42, title), fill=P.c('accent2', (200, 140, 20), 255))
    d.text((cw - pad, pad), count, font=font('ui', lh * 0.36), fill=P.c('muted', (120, 120, 120), 255), anchor='ra')
    ink = P.c('on-surface', INK) + (255,)
    for i, it in enumerate(items):
        f = fontfor('ui', lh * 0.4, it)
        y = pad + lh * (i + 1); bx = lh * 0.42
        d.rounded_rectangle([pad, y + lh * 0.12, pad + bx, y + lh * 0.12 + bx], P.r(6), outline=P.c('line', (160, 160, 160), 255), width=3)
        d.text((pad + bx * 1.5, y + lh * 0.1), it, font=f, fill=ink)
        if c.lt >= ticks[i]:
            k = ease_out((c.lt - ticks[i]) / 0.25)
            d.rounded_rectangle([pad, y + lh * 0.12, pad + bx, y + lh * 0.12 + bx], P.r(6), fill=P.c('success', (52, 199, 89), 255))
            d.line([(pad + bx * .22, y + lh * .12 + bx * .52), (pad + bx * .42, y + lh * .12 + bx * .74), (pad + bx * .8, y + lh * .12 + bx * .28)], fill=P.c('on-accent', (255, 255, 255), 255), width=4)
            tw = f.getlength(it) * k
            d.line([(pad + bx * 1.5, y + lh * 0.36), (pad + bx * 1.5 + tw, y + lh * 0.36)], fill=ink, width=3)
    left = c.fx > c.W / 2
    x = c.W * 0.05 + cw / 2 if left else c.W * 0.95 - cw / 2
    pop = ease_back(c.lt / 0.3)
    place(c, shadowed(im, 14, 8, 90), x, max(im.height / 2 + c.H * 0.06, c.fy - c.fw * 1.4), 0.8 + 0.2 * pop, 0, clamp(c.lt / 0.12) * clamp((e.d - c.lt) / 0.2), behind=True)
