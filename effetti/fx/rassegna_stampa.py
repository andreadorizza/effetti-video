"""rassegna-stampa (match-cut): Pagine di giornale che cambiano su una parola, ferma in un riquadro rosso dietro la testa.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


MATCH_TXT = ('one clip went in and every cut came back before lunch while editors once spent whole weeks rebuilding the same '
             'timeline by hand early users called it unsettling then impossible to ignore the dead air was gone the captions '
             'matched and the colour finally looked like the room it was shot in nobody opened an editing app all week').split()
# The same article in Italian: the words the pages are set in when the texts are Italian.
MATCH_TXT_IT = ('è entrata una sola clip e ogni taglio è tornato indietro prima di pranzo mentre i montatori passavano '
                'settimane intere a rifare a mano la stessa timeline i primi utenti lo hanno definito inquietante poi '
                'impossibile da ignorare i tempi morti erano spariti i sottotitoli tornavano e il colore finalmente '
                'somigliava alla stanza in cui era stato girato nessuno ha aperto un programma di montaggio per tutta '
                'la settimana').split()


def match_page(c, e, j, wx, wy):
    """One article page, with the key word in a red box locked at (wx, wy)."""
    W, H = c.W, c.H; rnd = random.Random(31 + j)
    paper = P.c('paper', [(246, 243, 236), (236, 229, 212), (251, 251, 250), (241, 236, 228), (232, 232, 230), (248, 240, 228)][j % 6])
    kind = ['serif', 'mont', 'ui', 'serif', 'anton', 'monts'][j % 6]
    size = W * [0.085, 0.07, 0.072, 0.095, 0.08, 0.068][j % 6]; f = font(kind, size); lh = size * 1.22
    word = e.o.get('text', 'Claude'); red = rgb(e.o.get('color'), P.c('accent', (214, 40, 40)))
    im = Image.new('RGB', (W, H), paper); d = ImageDraw.Draw(im); ink = P.c('on-surface', (40, 38, 36))
    words = tr(MATCH_TXT_IT, MATCH_TXT)
    base = f.getbbox('Ag'); asc = -base[1]
    ww = f.getlength(word); bx0 = wx - ww / 2
    def run(x, y, direction):
        while (x < W + size if direction > 0 else x > -size * 6):
            w_ = rnd.choice(words) + ' '
            if direction < 0: x -= f.getlength(w_)
            d.text((x, y), w_, font=f, fill=ink)
            if direction > 0: x += f.getlength(w_)
    off = rnd.uniform(0, size * 3)
    ys = wy - asc - lh * math.ceil((wy - asc) / lh + 1)
    y = ys
    while y < H + lh:
        if abs(y - (wy - asc)) < 1: pass
        else: run(-off - rnd.uniform(0, size * 4), y, 1)
        y += lh
    ky = wy - asc
    d.rectangle([0, ky - lh * 0.1, W, ky + lh * 0.95], fill=paper)
    run(bx0 - size * 0.45, ky, -1); run(bx0 + ww + size * 0.45, ky, 1)
    a = np.asarray(im, np.float32) / 255
    bl = cv2.GaussianBlur(a, (0, 0), W * 0.006)
    yy, xx = np.ogrid[0:H, 0:W]
    dd = np.clip((((xx - wx) / (W * 0.62)) ** 2 + ((yy - wy) / (H * 0.32)) ** 2) - 0.15, 0, 1)[..., None]
    a = a * (1 - dd) + bl * dd
    a *= (1 - 0.18 * np.clip(dd * 1.4, 0, 1))
    pg = Image.fromarray((a * 255).astype(np.uint8)).convert('RGBA')
    bf = font(kind, size); bb = bf.getbbox(word); padx, pady = size * 0.22, size * 0.12
    box = rrect(ww + 2 * padx, (bb[3] - bb[1]) + 2 * pady + size * 0.08, size * 0.08, red + (255,))
    ImageDraw.Draw(box).text((padx, pady - bb[1]), word, font=bf, fill=P.c('on-accent', (255, 255, 255), 255))
    pg.alpha_composite(box, (int(bx0 - padx), int(wy - asc + bb[1] - pady)))
    return np.asarray(pg.convert('RGB'), np.uint8)


@effetto('rassegna-stampa', en='match-cut', alias=('giornali', 'match', 'match-cut'),
         desc='Pagine di giornale che cambiano su una parola, ferma in un riquadro rosso dietro la testa')
def fx_match_cut(c, e):
    k = clamp(c.lt / 0.06) * fade(c, e, 0.12)
    face_cam(c, 1 + 0.06 * ease_out(c.lt / e.d), 0.44)
    wx, wy = cached(e, 'anchor', lambda: (c.W / 2, max(c.H * 0.1, c.fy - c.fw * 1.55)))
    durs = [0.15, 0.15, 0.17, 0.19, 0.22, 0.26, 0.3, 0.45]; t, j = c.lt, 0
    while j < len(durs) - 1 and t > durs[j]: t -= durs[j]; j += 1
    pg = cached(e, ('pg', j), lambda: match_page(c, e, j, wx, wy)).astype(np.float32) / 255
    m = c.m[..., None]
    c.img = c.img * (1 - k) + (pg * (1 - m) + c.img * m) * k
