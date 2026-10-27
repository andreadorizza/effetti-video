"""atmosfera (moody): Una correzione colore cupa: più scura, più morbida, ombre verde acqua.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('atmosfera', en='moody', alias=('colore', 'moody'),
         desc='Una correzione colore cupa: più scura, più morbida, ombre verde acqua')
def fx_moody(c, e):
    k = ramp(c, e, 0.35, 0)
    c.img = c.img * (1 - k) + grade(c.img, e.o.get('grade', 'moody')) * k
    vignette(c, 0.4 * k)
