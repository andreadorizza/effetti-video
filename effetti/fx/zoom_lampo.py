"""zoom-lampo (lean-in): Uno zoom veloce su una parola.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('zoom-lampo', en='lean-in', alias=('lean-in',),
         desc='Uno zoom veloce su una parola')
def fx_lean_in(c, e):
    z = float(e.o.get('zoom', 1.45))
    face_cam(c, 1 + (z - 1) * ease_out(c.lt / float(e.o.get('speed', 0.18))), 0.42)
