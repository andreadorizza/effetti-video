"""effetti-video: 45 effetti per i tuoi video, da Claude.

Un effetto:      python scripts/effetti.py orbita video.mp4 uscita.mp4 --inizio 3.2 --fine 6
Più effetti:     python scripts/effetti.py --piano piano.json video.mp4 uscita.mp4
Prova veloce:    python scripts/effetti.py --piano piano.json video.mp4 prova.png --fermo 4.5,15.2
Con un tema:     ... --tema temi/dori
Elenco:          python scripts/effetti.py --elenco
"""
import argparse, json, sys

from . import fx, theme  # noqa: F401  (fx registers every effect)
from .i18n import EFFECTS, LOOKS, option, ordered, resolve, set_lang


def normalise(d):
    """One plan entry, with Italian or English keys, -> {'fx': it name, 'start', 'end', **options}."""
    out = {}
    for k, v in d.items():
        k, v = option(k, v)
        out[k] = v
    if 'fx' not in out: sys.exit(f'Manca il nome dell\'effetto in {d}')
    name, look = resolve(out['fx'])
    if not name or name not in EFFECTS:
        sys.exit(f"Effetto sconosciuto: '{out['fx']}'. Lancia --elenco per vederli tutti e {len(EFFECTS)}.")
    out['fx'] = name
    if look: out.setdefault('look', look)
    out.setdefault('start', 0.0); out.setdefault('end', 1e9)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('args', nargs='*', help='[effetto] video.mp4 uscita.mp4')
    ap.add_argument('--piano', '--plan', dest='plan', help='un piano JSON con più effetti')
    ap.add_argument('--inizio', '--start', dest='start', type=float, help='secondo di inizio')
    ap.add_argument('--fine', '--end', dest='end', type=float, help='secondo di fine')
    ap.add_argument('--testo', '--text', dest='text')
    ap.add_argument('--immagini', '--images', dest='images', help='una cartella di screenshot o clip')
    ap.add_argument('--opt', action='append', default=[], help='chiave=valore (si può ripetere)')
    ap.add_argument('--fermo', '--still', dest='still', help='secondi separati da virgole: salva fotogrammi PNG invece del video')
    ap.add_argument('--larghezza', '--width', dest='width', type=int, default=1080, help='lato corto del video (1080, o 2160 per il 4K)')
    ap.add_argument('--tema', '--theme', dest='theme', help='neutro (default), un file tema, una cartella o un tokens.json di un design system')
    ap.add_argument('--variante', '--variant', dest='variant', help='quale tema del design system (es. dark)')
    ap.add_argument('--lingua', '--lang', dest='lang', default=None, help='it (default) o en, per i testi predefiniti')
    ap.add_argument('--tracciamento', '--tracking', dest='tracking', default='auto', help='auto (default), vision o mediapipe')
    ap.add_argument('--elenco', '--list', dest='list', action='store_true', help='elenca gli effetti')
    a = ap.parse_args(argv)

    if a.list:
        for i, (k, v) in enumerate(ordered()): print(f"{i + 1:2d}. {k:20s} {v['desc']}  ({v['en']})")
        print('\nStili con nome: ' + ', '.join(f'{k} = {v[0]} stile={v[1]}' for k, v in LOOKS.items() if k.endswith('glitter')))
        return
    top = {}
    if a.plan:
        if len(a.args) != 2: sys.exit('Con --piano servono due file: video.mp4 uscita.mp4')
        src, dst = a.args
        raw = json.load(open(a.plan))
        if isinstance(raw, dict):
            top = raw; raw = raw.get('effetti', raw.get('effects', []))
        plan = [normalise(d) for d in raw]
    else:
        if len(a.args) != 3: sys.exit('Uso: effetti.py <effetto> video.mp4 uscita.mp4  (oppure --piano, oppure --elenco)')
        name, src, dst = a.args
        d = {'fx': name, 'start': a.start or 0.0, 'end': a.end if a.end is not None else 1e9}
        if a.text: d['text'] = a.text
        if a.images: d['images'] = a.images
        for kv in a.opt:
            if '=' not in kv: sys.exit(f'--opt vuole chiave=valore, non {kv}')
            k, v = kv.split('=', 1); d[k] = v
        plan = [normalise(d)]
    set_lang(a.lang or top.get('lingua') or top.get('lang') or 'it')
    theme.use(a.theme or top.get('tema') or top.get('theme'), a.variant or top.get('variante') or top.get('variant'))
    if theme.P.name != 'neutro': print(f'Tema: {theme.P.name}', flush=True)
    from .engine import render
    render(plan, src, dst, stills=a.still.split(',') if a.still else None, width=a.width,
           tracking=a.tracking or top.get('tracciamento', 'auto'))


if __name__ == '__main__':
    main()
