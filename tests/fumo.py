"""Smoke test: every effect draws a frame, in the neutral theme and in temi/dori, and a video comes out tagged bt709.

    .venv/bin/python tests/fumo.py

Needs nothing but ffmpeg. It makes its own synthetic 1080x1920 clip (no face: the effects run on the engine's
fallback face) and works from a temporary folder, as a user does from their own:
1. one still per effect at 540 wide, through the CLI and --fermo, neutral and with --tema temi/dori. Each effect
   gets its own one-second window of a 5 fps clip, and a tracker that finds no one stands in for the real one,
   which would take minutes here;
2. one second of one effect encoded by scripts/effetti.py in its own process, tracked by MediaPipe (the same on
   every OS), then its four colour tags read back with ffprobe.
Exits 1 and names each effect that failed; the temporary folder is kept then.
"""
import contextlib, io, json, os, shutil, subprocess, sys, tempfile, time, traceback
import numpy as np
import cv2

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from effetti import cli, engine  # noqa: E402
from effetti.i18n import EFFECTS, ordered  # noqa: E402

FPS, SLOT, AT = 5, 1.0, 0.62      # each effect gets SLOT seconds; its still is at AT of the window
TEMI = [('neutro', None), ('dori', 'temi/dori')]
TAG = {'color_range': 'tv', 'color_space': 'bt709', 'color_primaries': 'bt709', 'color_transfer': 'bt709'}
errori = []                       # (theme, effect, what went wrong)
ora = {'tema': None}


class Nessuno:
    """A tracker that finds no one: no face, an empty person mask."""
    name = 'nessuno'

    def __init__(self, aw, ah): self.shape = (ah, aw)
    def reset(self): pass
    def __call__(self, rgb, ms): return np.zeros(self.shape, np.uint8), None
    def close(self): pass


def sorvegliato(nome, fn):
    """The effect, with its exception recorded under its name instead of stopping the render."""
    def g(c, e):
        try:
            fn(c, e)
        except Exception:
            errori.append((ora['tema'], nome, traceback.format_exc(limit=-2).strip()))
    return g


def clip(path, secondi, fps):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'testsrc2=size=1080x1920:rate={fps}:duration={secondi}',
                    '-f', 'lavfi', '-i', f'sine=frequency=440:duration={secondi}', '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', path], check=True)


def main():
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix='fumo-')
    os.chdir(tmp)
    nomi = [k for k, _ in ordered()]
    clip('clip.mp4', len(nomi) * SLOT, FPS)
    clip('uno.mp4', 1, 30)
    piano = [{'effetto': n, 'inizio': i * SLOT, 'fine': (i + 1) * SLOT} for i, n in enumerate(nomi)]
    fermi = [round((i + AT) * SLOT * FPS) / FPS for i in range(len(nomi))]
    with open('piano.json', 'w') as f: json.dump({'effetti': piano}, f)

    # 1. one still per effect, in each theme
    engine.pick = lambda name: Nessuno
    for k, v in EFFECTS.items(): v['fn'] = sorvegliato(k, v['fn'])
    for etichetta, tema in TEMI:
        ora['tema'] = etichetta
        args = ['--piano', 'piano.json', 'clip.mp4', f'{etichetta}/f.png', '--fermo', ','.join(f'{t:.2f}' for t in fermi),
                '--larghezza', '540'] + (['--tema', tema] if tema else [])
        try:
            with contextlib.redirect_stdout(io.StringIO()): cli.main(args)
        except (Exception, SystemExit) as ex:
            errori.append((etichetta, 'motore', f'{type(ex).__name__}: {ex}'))
            continue
        for n, t in zip(nomi, fermi):
            im = cv2.imread(f'{etichetta}/f_{t:.2f}.png')
            if im is None or im.shape != (960, 540, 3):
                errori.append((etichetta, n, f'il fotogramma a {t:.2f} s manca o non è 540x960'))

    # 2. one second encoded by the CLI in its own process, then its colour tags
    r = subprocess.run([sys.executable, os.path.join(HERE, 'scripts', 'effetti.py'), 'timbro', 'uno.mp4', 'uno_effetti.mp4',
                        '--fine', '1', '--larghezza', '540', '--tracciamento', 'mediapipe'], capture_output=True, text=True)
    if r.returncode:
        errori.append(('neutro', 'timbro', 'video: ' + r.stderr.strip()[-2000:]))
    else:
        out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=' + ','.join(TAG),
                              '-of', 'default=noprint_wrappers=1', 'uno_effetti.mp4'], capture_output=True, text=True).stdout
        got = dict(l.split('=', 1) for l in out.split() if '=' in l)
        bad = {k: got.get(k) for k, v in TAG.items() if got.get(k) != v}
        if bad: errori.append(('neutro', 'timbro', f'tag del colore sbagliati nel video: {bad}'))

    os.chdir(HERE)
    for tema, nome, cosa in errori:
        print(f'ERRORE {nome} ({tema})\n  ' + cosa.replace('\n', '\n  '))
    if errori:
        print(f'\n{len(errori)} errori. La cartella resta: {tmp}')
        sys.exit(1)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'OK: {len(nomi)} effetti in {len(TEMI)} temi, video bt709, in {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
