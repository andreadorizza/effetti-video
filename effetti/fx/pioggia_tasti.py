"""pioggia-tasti (shortcut-rain): Tasti della tastiera piovono dietro di te.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('pioggia-tasti', en='shortcut-rain', alias=('rain', 'shortcut-rain', 'tasti'),
         desc='Tasti della tastiera piovono dietro di te')
def fx_shortcut_rain(c, e):
    # the Italian Mac keyboard: tab, shift and return are symbols, option is alt
    keys = e.o.get('text', tr('cmd|/|C|V|Z|esc|⇥|⇧|↩|alt', 'cmd|/|C|V|Z|esc|tab|shift|enter|opt')).split('|')
    ks = int(c.W * 0.1)
    def cap(k):
        f = fontfor('mono' if covers(FONT['mono'], k) else 'ui', ks * 0.36, k)  # the mono face has no ⇧ ⇥ ↩ ⌘: those come from the ui face
        w = max(ks, int(f.getlength(k) + ks * 0.5))
        im = rrect(w, ks, ks * 0.18, P.c('line', (190, 190, 198), 255)); top = rrect(w - 8, ks - 14, ks * 0.16, P.c('surface', (246, 246, 248), 255))
        im.alpha_composite(top, (4, 3)); ImageDraw.Draw(im).text((w / 2, ks * 0.44), k, font=f, fill=P.c('on-surface', INK, 255), anchor='mm')
        return shadowed(im, 8, 6, 100)
    caps = cached(e, 'caps', lambda: [cap(k) for k in keys])
    parts = cached(e, 'p', lambda: [(random.Random(i).random(), random.Random(i + 99).random() * max(0.1, e.d - 0.8),
                                     0.45 + 0.4 * random.Random(i + 7).random(), random.Random(i + 3).uniform(-25, 25),
                                     random.Random(i + 5).uniform(-60, 60)) for i in range(int(e.o.get('count', 26)))])
    for i, (x, t0, v, r0, w) in enumerate(parts):
        if c.lt < t0: continue
        y = -ks + (c.lt - t0) * v * c.H
        place(c, caps[i % len(caps)], c.W * (0.04 + 0.92 * x), y, 0.75 + 0.35 * v, r0 + w * (c.lt - t0), clamp((e.d - c.lt) / 0.2), behind=True)
