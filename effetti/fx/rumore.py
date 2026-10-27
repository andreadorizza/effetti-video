"""rumore (noise): Le tue reel si accumulano dietro la testa, una ogni quarto di secondo.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('rumore', en='noise', alias=('caos', 'noise', 'the-noise'),
         desc='Le tue reel si accumulano dietro la testa, una ogni quarto di secondo', schede=True)
def fx_noise(c, e):
    cw = int(c.W * float(e.o.get('size', 0.34)))
    def setup():
        rnd = random.Random(7); n = min(16, max(4, int(e.d / 0.22)))
        return [(rnd.uniform(0.14, 0.86), rnd.uniform(0.12, 0.52), rnd.uniform(-7, 7)) for _ in range(n)]
    pos = cached(e, 'pos', setup)
    cards = cached(e, 'cards', lambda: [card(vary(im, i) if e.o.get('images') is None else im, cw) for i, im in enumerate(e.cards)])
    out = clamp((e.d - c.lt) / 0.2)
    for i, (x, y, r) in enumerate(pos):
        t0 = i * 0.22
        if c.lt < t0: break
        k = ease_back((c.lt - t0) / 0.25)
        place(c, cards[i % len(cards)], x * c.W, y * c.H, 0.6 + 0.4 * k, r, clamp((c.lt - t0) / 0.08) * out, behind=True)
