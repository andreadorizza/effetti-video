"""parola-dietro (backdrop-word): Una parola gigante cade dietro di te.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('parola-dietro', en='backdrop-word', alias=('backdrop', 'backdrop-word'),
         desc='Una parola gigante cade dietro di te')
def fx_backdrop_word(c, e):
    word = e.o.get('text', 'CLAUDE')
    im = cached(e, 'w', lambda: fit_text(word, c.W * 0.94, e.o.get('font', 'bold'), fill=rgb(e.o.get('color'), P.c('over', CREAM)), shadow=10))
    k = ease_back(c.lt / 0.42)
    y_end = c.fy - c.fw * 1.05
    y = -im.height + (y_end + im.height) * k
    place(c, im, c.W / 2 * 0.6 + c.fx * 0.4, y, alpha=clamp((e.d - c.lt) / 0.2), behind=True)
