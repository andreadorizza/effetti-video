"""commento (comment-box): Il pannello commenti di Instagram sopra la testa scrive la tua parola, la pubblica, riceve un cuore e la tua risposta.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
from ..draw import *


def comment_bar(c, e):
    word = e.o.get('text', 'EFFECTS')
    bw, bh = int(c.W * 0.9), int(c.W * 0.11)
    slide = ease_out(c.lt / 0.3); y = c.H * 0.8 + (1 - slide) * c.H * 0.25
    type_t, post_t = 0.35, 0.35 + 0.08 * len(word) + 0.25
    typed = word[:int(clamp((c.lt - type_t) / (0.08 * len(word))) * len(word) + 0.001)] if c.lt < post_t else ''
    im = rrect(bw, bh, bh / 2, (255, 255, 255, 245)); d = ImageDraw.Draw(im)
    r = bh * 0.32; d.ellipse([bh * 0.2, bh / 2 - r, bh * 0.2 + 2 * r, bh / 2 + r], fill=(214, 41, 118, 255))
    f = font('ui', bh * 0.3)
    if typed: d.text((bh * 0.95, bh / 2), typed + ('|' if int(c.lt * 4) % 2 else ''), font=f, fill=INK + (255,), anchor='lm')
    elif c.lt < post_t: d.text((bh * 0.95, bh / 2), 'Add a comment...', font=f, fill=(150, 150, 150, 255), anchor='lm')
    d.text((bw - bh * 0.4, bh / 2), 'Post', font=f, fill=((0, 149, 246, 255) if typed else (180, 210, 240, 255)), anchor='rm')
    al = clamp((e.d - c.lt) / 0.2)
    place(c, shadowed(im, 14, 6, 100), c.W / 2, y, alpha=al, guard=True)
    if c.lt >= post_t:
        k = ease_back((c.lt - post_t) / 0.3)
        b = rrect(int(c.W * 0.52), int(bh * 0.85), bh * 0.3, (255, 255, 255, 240)); bd = ImageDraw.Draw(b)
        bd.text((bh * 0.3, b.height * 0.32), 'you', font=font('ui', bh * 0.2), fill=(120, 120, 120, 255), anchor='lm')
        bd.text((bh * 0.3, b.height * 0.66), word, font=font('ui', bh * 0.3), fill=INK + (255,), anchor='lm')
        hk = ease_back((c.lt - post_t - 0.3) / 0.3)
        if hk > 0:
            hh = heart(bh * 0.4 * hk); b.alpha_composite(hh, (int(b.width - bh * 0.3 - hh.width), int(b.height / 2 - hh.height / 2)))
        place(c, shadowed(b, 12, 5, 90), c.W * 0.07 + b.width / 2, y - bh * 1.05, 0.7 + 0.3 * k, 0, al * clamp((c.lt - post_t) / 0.1), guard=True)


_emoji = {}


def emoji(ch, size):
    """A colour emoji as an RGBA image (Apple Color Emoji on a Mac). Returns None where the font is missing."""
    k = (ch, int(size))
    if k not in _emoji:
        try:
            f = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 160)
            im = Image.new('RGBA', (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(im).text((20, 10), ch, font=f, embedded_color=True)
            im = im.crop(im.getbbox()); _emoji[k] = im.resize((int(size), int(size * im.height / im.width)), Image.LANCZOS)
        except Exception:
            _emoji[k] = None
    return _emoji[k]


def comment_sheet(c, e):
    """Reels 1021 + VOX look: an Instagram Comments sheet above your head (your hair in front). The word types in, posts,
    gets a heart, then your reply drops in with a link chip."""
    W, H = c.W, c.H; u = W / 1080; al = fade(c, e)
    word = e.o.get('text', 'EFFECTS'); handle = e.o.get('handle', 'vibha.in.progress')
    reply = e.o.get('reply', 'Sent you the pack'); chip = e.o.get('chip', '22 effects')
    sw, sh = 740 * u, 450 * u
    t_post = 0.3 + 0.06 * len(word) + 0.1; t_heart, t_rep = t_post + 0.25, t_post + 0.4
    sheet = rrect(sw, sh, 30 * u, (38, 38, 40, 248)); d = ImageDraw.Draw(sheet)
    white, grey, blue = (245, 245, 245, 255), (160, 160, 166, 255), (0, 149, 246, 255)
    d.rounded_rectangle([sw / 2 - 32 * u, 14 * u, sw / 2 + 32 * u, 20 * u], 3 * u, fill=(110, 110, 116, 255))
    d.text((sw / 2, 50 * u), 'Comments', font=font('uib', 26 * u), fill=white, anchor='mm')
    d.line([(0, 80 * u), (sw, 80 * u)], fill=(60, 60, 64, 255), width=max(1, int(2 * u)))
    def avatar(sz):
        a = Image.new('RGBA', (int(sz), int(sz)), (0, 0, 0, 0)); ad = ImageDraw.Draw(a)
        ad.ellipse([0, 0, sz - 1, sz - 1], fill=(233, 90, 140, 255)); ad.text((sz / 2, sz / 2), 'V', font=font('uib', sz * 0.5), fill=(255, 255, 255, 255), anchor='mm')
        return a
    if c.lt < t_post:
        d.text((sw / 2, 190 * u), 'Start the conversation.', font=font('uim', 21 * u), fill=grey, anchor='mm')
    else:
        q = ease_out((c.lt - t_post) / 0.25); oy = (1 - q) * -20 * u; a8 = int(255 * clamp(q * 1.5))
        av = avatar(46 * u); av.putalpha(av.split()[3].point(lambda v: v * a8 // 255)); sheet.alpha_composite(av, (int(26 * u), int(100 * u + oy)))
        d.text((88 * u, 108 * u + oy), 'you', font=font('uib', 19 * u), fill=white[:3] + (a8,), anchor='lm')
        d.text((88 * u + font('uib', 19 * u).getlength('you ') + 4 * u, 108 * u + oy), 'now', font=font('uim', 18 * u), fill=grey[:3] + (a8,), anchor='lm')
        d.text((86 * u, 128 * u + oy), word, font=font('uib', 50 * u), fill=white[:3] + (a8,))
        d.text((88 * u, 196 * u + oy), 'Reply', font=font('uim', 17 * u), fill=grey[:3] + (a8,), anchor='lm')
        hk = ease_back((c.lt - t_heart) / 0.3)
        if hk > 0:
            hh = heart(30 * u * hk, (255, 48, 64)); sheet.alpha_composite(hh, (int(sw - 46 * u - hh.width / 2), int(130 * u - hh.height / 2)))
        rk = ease_out((c.lt - t_rep) / 0.25)
        if rk > 0:
            ra = int(255 * clamp(rk * 1.5)); ry = 226 * u + (1 - rk) * 16 * u; rx = 88 * u
            fc = face_chip(c, e, 34 * u); fc.putalpha(fc.split()[3].point(lambda v: v * ra // 255)); sheet.alpha_composite(fc, (int(rx), int(ry)))
            d.text((rx + 46 * u, ry + 8 * u), handle, font=font('uib', 18 * u), fill=white[:3] + (ra,), anchor='lm')
            d.text((rx + 46 * u + font('uib', 18 * u).getlength(handle) + 10 * u, ry + 8 * u), 'Author', font=font('uim', 16 * u), fill=grey[:3] + (ra,), anchor='lm')
            d.text((rx + 46 * u, ry + 36 * u), reply, font=font('uim', 22 * u), fill=white[:3] + (ra,), anchor='lm')
            gift = emoji('🎁', 24 * u)
            if gift is not None:
                g2 = gift.copy(); g2.putalpha(g2.split()[3].point(lambda v: v * ra // 255))
                sheet.alpha_composite(g2, (int(rx + 52 * u + font('uim', 22 * u).getlength(reply)), int(ry + 36 * u - g2.height / 2)))
            ck = ease_back((c.lt - t_rep - 0.12) / 0.3)
            if ck > 0:
                ct = text_img(chip, 19 * u, 'uib', (20, 20, 22)); lk = emoji('🔗', 20 * u)
                cw_ = ct.width + (lk.width + 4 * u if lk is not None else 0) + 10 * u
                cp = rrect(cw_, ct.height * 0.9, ct.height * 0.45, (255, 214, 10, 255))
                x0 = 6 * u
                if lk is not None: cp.alpha_composite(lk, (int(x0 + 4 * u), int((cp.height - lk.height) / 2))); x0 += lk.width + 4 * u
                cp.alpha_composite(ct, (int(x0), int((cp.height - ct.height) / 2)))
                cp = cp.resize((max(1, int(cp.width * (0.6 + 0.4 * ck))), max(1, int(cp.height * (0.6 + 0.4 * ck)))))
                sheet.alpha_composite(cp, (int(rx + 46 * u), int(ry + 56 * u)))
    ey = sh - 140 * u
    chars = ['❤️', '🙌', '🔥', '👏', '😢', '😍', '😮', '😂']
    for j, ch in enumerate(chars):
        im = emoji(ch, 36 * u)
        if im is not None: sheet.alpha_composite(im, (int(36 * u + j * (sw - 72 * u - 36 * u) / 7), int(ey)))
    iy = sh - 78 * u
    sheet.alpha_composite(avatar(48 * u), (int(22 * u), int(iy)))
    d.rounded_rectangle([82 * u, iy, sw - 22 * u, iy + 48 * u], 24 * u, fill=(54, 54, 58, 255))
    typed = word[:int(clamp((c.lt - 0.3) / (0.06 * len(word))) * len(word) + 1e-3)] if c.lt < t_post else ''
    if typed:
        d.text((104 * u, iy + 24 * u), typed, font=font('uib', 26 * u), fill=white, anchor='lm')
        if int(c.lt * 4) % 2: d.rectangle([104 * u + font('uib', 26 * u).getlength(typed) + 3 * u, iy + 10 * u, 106 * u + font('uib', 26 * u).getlength(typed) + 3 * u, iy + 38 * u], fill=(0, 149, 246, 255))
    else:
        d.text((104 * u, iy + 24 * u), f'Add a comment for {handle}', font=font('uim', 20 * u), fill=grey, anchor='lm')
    pressed = t_post - 0.08 <= c.lt < t_post
    d.text((sw - 44 * u, iy + 24 * u), 'Post', font=font('uib', 23 * u), fill=(blue if typed else (70, 110, 160, 255)) if not pressed else (140, 200, 255, 255), anchor='rm')
    sheet = shadowed(sheet, 22, 10, 120)
    bottom = c.fy - c.fw * 0.5; top = bottom - sheet.height
    s = 1.0
    if top < H * 0.02: s = max(0.6, (bottom - H * 0.02) / sheet.height)
    cy = bottom - sheet.height * s / 2 + 3 * u * math.sin(c.lt * 3.2)
    place(c, sheet, W / 2 * 0.5 + c.fx * 0.5, cy, s * (0.85 + 0.15 * ease_back(c.lt / 0.3)), 1.2, al * clamp(c.lt / 0.1), behind=True)


@effetto('commento', en='comment-box', alias=('comment', 'comment-box', 'commenti'),
         desc='Il pannello commenti di Instagram sopra la testa scrive la tua parola, la pubblica, riceve un cuore e la tua risposta')
def fx_comment_box(c, e):
    (comment_bar if e.o.get('look') == 'bar' else comment_sheet)(c, e)
