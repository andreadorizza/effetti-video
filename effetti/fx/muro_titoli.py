"""muro-titoli (headline-wall): I tuoi titoli si accumulano dietro la testa, poi davanti compare un totale.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


@effetto('muro-titoli', en='headline-wall', alias=('headline-wall', 'headlines'),
         desc='I tuoi titoli si accumulano dietro la testa, poi davanti compare un totale')
def fx_headline_wall(c, e):
    W, H = c.W, c.H; u = W / 1080; al = fade(c, e)
    items = [x.split('::') for x in e.o.get('text', tr(
        'Proteggi i tuoi dati personali con ChatGPT Agent Mode::197K visualizzazioni|Siti con animazioni allo scroll, senza codice::124K visualizzazioni|'
        'Un curriculum impossibile da scartare con Claude::83K visualizzazioni|Stesso prompt: Claude Fable 5 vs ChatGPT 5.6 Sol::50K visualizzazioni|'
        'Jev, il nuovo modello AI più veloce ed economico di Claude::40K visualizzazioni|Scraping di LinkedIn in automatico::38K visualizzazioni|'
        'Proteggi i tuoi dati personali su internet::140K visualizzazioni',
        'Protect your personal data with ChatGPT Agent Mode::197K views|Easiest no-code scroll animation websites::124K views|'
        'How to make your resume un-rejectable using Claude::83K views|Same prompt: Claude Fable 5 vs ChatGPT 5.6 Sol::50K views|'
        'Jev, the new AI model faster and cheaper than Claude::40K views|Scrape LinkedIn automatically::38K views|'
        'Protect your personal data on the internet::140K views')).split('|')]
    looks = [(P.c('surface', (255, 255, 255)), P.c('on-surface', (20, 20, 22))), (P.c('dark', (22, 20, 24)), P.c('on-dark', (255, 255, 255))),
             (P.c('paper', (246, 238, 226)), P.c('on-surface', (30, 24, 20))), (P.c('accent2', (255, 214, 10)), P.c('on-accent', (20, 20, 22)))]
    handle = tr('@il.tuo.profilo', '@vibha.in.progress')
    def hcard(i):
        title, meta = (items[i % len(items)] + [''])[:2]; bg, fg = looks[i % len(looks)]
        cw = int(W * 0.5); f = font('uib', cw * 0.085); words = title.split(' '); lines, cur = [], ''
        for w_ in words:
            tst = (cur + ' ' + w_).strip()
            if f.getlength(tst) > cw * 0.84 and cur: lines.append(cur); cur = w_
            else: cur = tst
        lines.append(cur); lh = cw * 0.1
        chh = int(cw * 0.1 + lh * len(lines) + cw * 0.16)
        im = rrect(cw, chh, cw * 0.04, bg + (255,)); d = ImageDraw.Draw(im)
        for j, ln in enumerate(lines): d.text((cw * 0.08, cw * 0.07 + j * lh), ln, font=f, fill=fg + (255,))
        my = chh - cw * 0.085; s = cw * 0.04
        play = P.c('danger', (255, 48, 64)); play = fg if play == bg else play   # the play mark must show on its card
        d.polygon([(cw * 0.08, my - s / 2), (cw * 0.08, my + s / 2), (cw * 0.08 + s * 0.9, my)], fill=play + (255,))
        mt = (handle + '  ·  ' + meta) if meta else handle
        ms = lines_fit([mt], cw * 0.86 - s * 1.5, 'uim', cw * 0.045)   # shrinks only when a wider theme font would overflow
        d.text((cw * 0.08 + s * 1.5, my), mt, font=font('uim', ms), fill=fg + (170,), anchor='lm')
        return shadowed(im, 14, 8, 110)
    N = int(e.o.get('count', 13))
    cards = cached(e, 'cards', lambda: [hcard(i) for i in range(N)])
    pos = cached(e, 'pos', lambda: [(random.Random(i * 7 + 1).uniform(0.2, 0.8), random.Random(i * 7 + 2).uniform(0.07, 0.42), random.Random(i * 7 + 3).uniform(-9, 9)) for i in range(N)])
    gap = float(e.o.get('gap', 0.09))
    for i in range(N):
        t0 = i * gap
        if c.lt < t0: break
        x, y, r = pos[i]; kk = ease_back((c.lt - t0) / 0.22)
        place(c, cards[i], x * W, y * H, 0.55 + 0.45 * kk, r, al * clamp((c.lt - t0) / 0.06), behind=True)
    t1 = N * gap + 0.1
    if c.lt > t1:
        tot = e.o.get('total', '672K'); lab = e.o.get('label', tr('visualizzazioni in 7 reel', 'views from 7 reels'))
        a = text_img(tot, 96 * u, 'anton', P.c('on-accent', (255, 255, 255))); b = text_img(lab, 34 * u, 'uib', P.c('on-accent', (255, 255, 255)))
        pw = int(a.width + b.width + 30 * u); ph = int(max(a.height, b.height) + 10 * u)
        pill = rrect(pw, ph, ph * 0.28, P.c('accent', (217, 119, 87), 245)); pill.alpha_composite(a, (int(8 * u), (ph - a.height) // 2)); pill.alpha_composite(b, (int(a.width + 8 * u), (ph - b.height) // 2))
        place(c, shadowed(pill, 18, 8, 110), W / 2, max(c.fy + c.fw * 1.8, H * 0.6), 0.6 + 0.4 * pop(c, t1, 0.3), -3, al * clamp((c.lt - t1) / 0.08), guard=True)
