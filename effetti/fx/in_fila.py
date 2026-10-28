"""in-fila (lineup): Tessere numerate si aprono ad arco sopra la testa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('in-fila', en='lineup', alias=('fila', 'lineup', 'the-lineup'),
         desc='Tessere numerate si aprono ad arco sopra la testa')
def fx_lineup(c, e):
    names = e.o.get('text', '|'.join(tr(NOMI, NAMES))).split('|')
    tw = int(c.W * 0.105)
    def tile(i, name):
        im = rrect(tw, int(tw * 1.25), tw * 0.16, P.c('dark', (24, 24, 28), 225), P.c('line', (255, 255, 255), 60), 2)
        d = ImageDraw.Draw(im)
        num = text_img(f'{i + 1:02d}', tw * 0.42, 'serif', P.c('on-dark', CREAM))
        im.alpha_composite(num, ((tw - num.width) // 2, int(tw * 0.04)))
        words = name.split(' ')
        lines = [' '.join(words[:len(words) // 2 or 1]), ' '.join(words[len(words) // 2 or 1:])] if len(name) > 10 else [name]
        lines = [l for l in lines if l]
        fs = tw * 0.15; f = fontfor('ui', fs, name); lim = tw * 0.84
        if max((f.getlength(l) for l in lines), default=0) > lim:  # longer names (the Italian ones): break where both lines fit best, then shrink
            if len(words) > 1:
                j = min(range(1, len(words)), key=lambda j: max(f.getlength(' '.join(words[:j])), f.getlength(' '.join(words[j:]))))
                lines = [' '.join(words[:j]), ' '.join(words[j:])]
            while fs > 6 and max((f.getlength(l) for l in lines), default=0) > lim: fs *= 0.94; f = fontfor('ui', fs, name)
        for j, ln in enumerate(lines):
            d.text((tw / 2, tw * (0.78 + 0.19 * j)), ln, font=f, fill=P.c('on-dark', (255, 255, 255), 235), anchor='mm')
        return shadowed(im, 8, 5, 90)
    tiles = cached(e, 'tiles', lambda: [tile(i, n) for i, n in enumerate(names)])
    n = len(tiles); outer = math.ceil(n / 2 + 0.5); inner = n - outer
    cx, cy = c.W / 2 * 0.6 + c.fx * 0.4, c.fy + c.fw * 0.3
    slots = []
    for row, cnt, R in ((0, outer, c.W * 0.47), (1, inner, c.W * 0.33)):
        for k in range(cnt):
            a = math.pi * (0.94 - 0.88 * k / max(1, cnt - 1))
            slots.append((cx + R * math.cos(a), cy - R * math.sin(a) * 1.05, math.degrees(a - math.pi / 2) * 0.3))
    out = clamp((e.d - c.lt) / 0.2)
    for i, (x, y, r) in enumerate(slots[:n]):
        t0 = 0.035 * i
        if c.lt < t0: continue
        k = ease_back((c.lt - t0) / 0.3)
        place(c, tiles[i], x, y + (1 - k) * 40, 0.5 + 0.5 * k, r, clamp((c.lt - t0) / 0.1) * out, behind=True)
