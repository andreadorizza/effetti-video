"""Two passes over the video: first find you (face + person mask), then draw the effects frame by frame.

By Vibha Ramprakash (MIT), from claude-video-effects; ported to effetti-video."""
import json, math, os, subprocess
import numpy as np
import cv2
from PIL import Image

from . import fx  # noqa: F401  (registers every effect)
from .i18n import EFFECTS
from .tracking import pick


def probe(path):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate:format=duration',
                                   '-of', 'json', path], capture_output=True, text=True, check=True).stdout)
    fr = j['streams'][0]['r_frame_rate']; num, den = fr.split('/'); fps = float(num) / float(den or 1)
    png = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True, check=True).stdout
    h, w = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR).shape[:2]
    return (fr if fps <= 30.5 else '30'), min(fps, 30.0), float(j['format']['duration']), w, h


def read_frames(path, W, H, fr):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={fr},scale={W}:{H}:flags=bicubic,format=rgb24', '-f', 'rawvideo', '-'],
                         stdout=subprocess.PIPE, bufsize=10 ** 8)
    n = W * H * 3
    try:
        while True:
            b = p.stdout.read(n)
            if len(b) < n: break
            yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    finally:
        if p.poll() is None: p.kill()
        p.stdout.close(); p.wait()


def smooth(vals, fps, tau=0.18):
    idx = [i for i, v in enumerate(vals) if v is not None]
    if not idx: return None
    arr = np.array([vals[i] if vals[i] is not None else (np.nan,) * 3 for i in range(len(vals))], np.float64)
    for k in range(3):
        col = arr[:, k]; good = ~np.isnan(col); col[~good] = np.interp(np.where(~good)[0], np.where(good)[0], col[good]); arr[:, k] = col
    a = 1 - math.exp(-1 / (fps * tau))  # forward then backward pass, so the smoothing has no lag
    for i in range(1, len(arr)): arr[i] = arr[i - 1] + a * (arr[i] - arr[i - 1])
    for i in range(len(arr) - 2, -1, -1): arr[i] = arr[i + 1] + a * (arr[i] - arr[i + 1])
    return arr


class Ctx: pass


class Fx:
    def __init__(self, d):
        self.name = d['fx']; self.start = float(d['start']); self.end = float(d['end']); self.d = max(0.05, self.end - self.start)
        self.o = {k: v for k, v in d.items() if k not in ('fx', 'start', 'end')}; self.state = {}; self.cards = []


def load_cards(folder, thumbs):
    out = []
    if folder and os.path.isdir(folder):
        for n in sorted(os.listdir(folder)):
            p = os.path.join(folder, n); ext = n.lower().rsplit('.', 1)[-1]
            if ext in ('jpg', 'jpeg', 'png', 'webp'): out.append(Image.open(p).convert('RGB'))
            elif ext in ('mp4', 'mov', 'm4v', 'webm'):
                cap = cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_MSEC, 1000); ok, fr = cap.read(); cap.release()
                if ok: out.append(Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
    return out or thumbs


def render(plan, src, dst, stills=None, width=1080, tracking='auto'):
    """plan: a list of {'fx': it name, 'start', 'end', **options}. stills: seconds to save as PNG instead of a video."""
    fr, fps, dur, sw, sh = probe(src)
    for d in plan: d['end'] = min(float(d['end']), dur)
    if sw <= sh: W = width; H = int(round(width * sh / sw / 2)) * 2
    else: H = width; W = int(round(width * sw / sh / 2)) * 2
    aw = 540 if sw <= sh else int(round(540 * sw / sh / 2)) * 2; ah = int(round(aw * sh / sw / 2)) * 2
    fxs = [Fx(d) for d in plan]
    if os.path.dirname(os.path.abspath(dst)): os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    inwin = lambda t: any(f.start - 0.5 <= t < f.end + 0.5 for f in fxs)
    Tracker = pick(tracking)
    print(f'Passo 1: ti cerco nel video ({Tracker.name}, {len(fxs)} effett{"i" if len(fxs) > 1 else "o"})...', flush=True)
    trk = Tracker(aw, ah); masks, faces, thumbs = {}, [], []
    n_thumb = 10; thumb_at = {int(dur * fps * (j + 0.5) / n_thumb) for j in range(n_thumb)}
    try:
        for i, fr_ in enumerate(read_frames(src, aw, ah, fr)):
            t = i / fps
            if i in thumb_at: thumbs.append(Image.fromarray(fr_.copy()))
            if inwin(t):
                m, f = trk(fr_, int(t * 1000)); masks[i] = m; faces.append(f)
            else:
                faces.append(None); trk.reset()
    finally:
        trk.close()
    sm = smooth(faces, fps)
    if sm is None: sm = np.tile([aw / 2, ah * 0.33, aw * 0.15], (len(faces), 1))
    for f in fxs:
        if EFFECTS[f.name]['cards']: f.cards = load_cards(f.o.get('images'), thumbs)
    stills = sorted({int(round(float(s) * fps)) for s in stills}) if stills else None
    enc = None
    if not stills:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fr), '-i', '-',
                                '-i', src, '-map', '0:v', '-map', '1:a:0?',
                                '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709',
                                '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
                                '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                                '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    print('Passo 2: aggiungo gli effetti...', flush=True)
    sc = W / aw; saved = []
    for i, frame in enumerate(read_frames(src, W, H, fr)):
        t = i / fps
        act = [f for f in fxs if f.start <= t < f.end]
        if stills is not None and i not in stills:
            if i > stills[-1]: break
            continue
        if act:
            c = Ctx(); c.W, c.H, c.t, c.fps = W, H, t, fps
            c.img = frame.astype(np.float32) / 255.0
            m = masks.get(i)
            c.m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0 if m is not None else np.zeros((H, W), np.float32)
            fx_, fy_, fw_ = sm[min(i, len(sm) - 1)]; c.fx, c.fy, c.fw = fx_ * sc, fy_ * sc, max(fw_ * sc, W * 0.05)
            for f in act:
                c.lt = t - f.start; EFFECTS[f.name]['fn'](c, f)
            frame = (np.clip(c.img, 0, 1) * 255 + 0.5).astype(np.uint8)
        if stills is not None:
            out = dst if len(stills) == 1 else dst.replace('.png', f'_{t:.2f}.png')
            if not cv2.imwrite(out, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)): raise SystemExit(f'Non riesco a salvare {out}')
            saved.append(out); print('salvato', out)
        else:
            enc.stdin.write(frame.tobytes())
            if i % int(fps * 5) == 0: print(f'  {t:5.1f}s / {dur:.1f}s', flush=True)
    if enc: enc.stdin.close(); enc.wait(); print('Fatto:', dst)
    return saved
