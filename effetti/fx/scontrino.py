"""scontrino (the-bill): Le istruzioni escono stampate come uno scontrino, nel muro sopra la testa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('scontrino', en='the-bill', alias=('bill', 'ricevuta', 'the-bill'),
         desc='Le istruzioni escono stampate come uno scontrino, nel muro sopra la testa')
def fx_bill(c, e):
    lines = e.o.get('text', tr('ORDINE N. 1021|1x orbita|1x riflettore|1x zoom-lampo|taglia i tempi morti|TOTALE: 1 prompt',
                                 'ORDER #1021|1x orbit|1x spotlight|1x lean-in|cut the dead air|TOTAL: 1 prompt')).split('|')
    def build():
        pw = int(c.W * 0.5); lh = int(pw * 0.085); pad = int(pw * 0.08)
        h = pad * 2 + lh * (len(lines) + 1)
        im = Image.new('RGBA', (pw, h), P.c('paper', CREAM, 255)); d = ImageDraw.Draw(im); ink = P.c('on-surface', INK)
        f = font('mono', lh * 0.62)
        for i, ln in enumerate(lines):
            y = pad + lh * i + (lh if i == len(lines) - 1 else 0)
            if i == len(lines) - 1:
                for x in range(pad, pw - pad, 14): d.line([(x, y - lh * 0.45), (x + 7, y - lh * 0.45)], fill=ink + (140,), width=2)
            d.text((pad, y), ln, font=f, fill=ink + (255,))
        return im
    rec = cached(e, 'r', build)
    slot_y, sw = c.H * 0.075, c.W * 0.62
    max_h = max(80, c.fy - c.fw * 1.3 - slot_y)
    s = min(1.0, max_h / rec.height)
    pr = ease_inout(c.lt / (e.d * 0.75)); L = int(rec.height * pr)
    al = clamp((e.d - c.lt) / 0.25)
    cx = c.W / 2
    if L > 2:
        paper = rec.crop((0, 0, rec.width, L))
        z = 14; jag = Image.new('RGBA', (rec.width, L + z), (0, 0, 0, 0)); jag.paste(paper, (0, 0))
        ImageDraw.Draw(jag).polygon([(x, L) for x in range(0, rec.width + 1, 2 * z)] + [(rec.width, L)] +
                                    [(x + z, L + z) for x in range(rec.width - 2 * z, -1, -2 * z)], fill=P.c('paper', CREAM, 255))
        paper = shadowed(jag, 10, 6, 90)
        if s < 1: paper = paper.resize((int(paper.width * s), int(paper.height * s)), Image.BILINEAR)
        comp(c, paper, cx - paper.width / 2, slot_y - 10 * s, al, behind=True)
    slot = rrect(sw, c.H * 0.03, c.H * 0.015, P.c('dark', (30, 30, 34), 255), P.c('line', (90, 90, 96), 255), 3)
    place(c, shadowed(slot, 10, 6, 140), cx, slot_y, alpha=al * clamp(c.lt / 0.15), behind=True)
