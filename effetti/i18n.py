"""Lingua, nomi degli effetti e nomi delle opzioni.

Gli effetti si chiamano in italiano (`orbita`); il nome inglese originale funziona sempre come alias
(`orbit`). Anche le opzioni hanno un nome italiano (`testo`) accanto a quello inglese (`text`).
I testi predefiniti degli effetti sono scritti `tr('Segui', 'Follow')`: italiano di default,
`--lingua en` per i testi originali.
"""
LANG = {'v': 'it'}


def set_lang(v):
    LANG['v'] = 'en' if str(v).lower().startswith('en') else 'it'


def tr(it, en):
    return en if LANG['v'] == 'en' else it


EFFECTS = {}   # it name -> dict(fn, en, desc, cards)
ALIASES = {}   # any accepted name -> it name
# Named looks of another effect: name -> (effect, look)
LOOKS = {'riflettore-glitter': ('riflettore', 'sparkle'), 'glitter-spotlight': ('riflettore', 'sparkle'),
         'glitter': ('riflettore', 'sparkle')}


def effetto(name, en=None, alias=(), desc='', schede=False):
    """Register an effect. `name` is its Italian name, `en` the original English one, `alias` any other
    words that should find it. `schede=True` gives it e.cards (your reels, or stills from the video)."""
    def deco(fn):
        EFFECTS[name] = {'fn': fn, 'en': en, 'desc': desc, 'cards': schede}
        for a in (name, en, *alias):
            if a: ALIASES[a.lower()] = name
        return fn
    return deco


def resolve(name):
    """Any accepted name -> (it name, look or None). None when unknown."""
    n = str(name).lower().strip().lstrip('/').replace(' ', '-').replace('_', '-')
    if n in LOOKS: return LOOKS[n]
    if n in ALIASES: return ALIASES[n], None
    return None, None


# Italian option names -> the option the effect reads
OPTIONS = {
    'testo': 'text', 'colore': 'color', 'immagini': 'images', 'dimensione': 'size', 'grandezza': 'size',
    'velocita': 'speed', 'velocità': 'speed', 'quanti': 'count', 'carattere': 'font', 'tono': 'grade',
    'spunte': 'ticks', 'titolo': 'title', 'quando': 'at', 'etichetta': 'label', 'etichetta_x': 'label_x',
    'angolo': 'angle', 'da': 'from', 'a': 'to', 'rapporto': 'ratio', 'rotazione': 'spin', 'righe': 'lines',
    'uscita': 'issue', 'nome': 'name', 'profilo': 'handle', 'stile': 'look', 'targhetta': 'tag',
    'evidenzia': 'hl', 'pillola': 'pill', 'sottotitolo': 'sub', 'timecode': 'tc', 'elemento': 'item',
    'altri': 'others', 'cella': 'cell', 'totale': 'total', 'ciambella': 'donut', 'barre': 'bars',
    'giri': 'turns', 'visualizzazioni': 'views', 'spinta': 'push', 'sfocatura': 'blur', 'posizione': 'pos',
    'sovrapposizione': 'overlap', 'accento': 'accent', 'destra': 'right', 'righe_y': 'lines_y',
    'destra_y': 'right_y', 'inizio': 'start', 'fine': 'end', 'effetto': 'fx',
}
# Italian option values -> the value the effect reads, per option
VALUES = {
    'look': {'glitter': 'sparkle', 'scintille': 'sparkle', 'editoriale': 'editorial', 'semplice': 'simple',
             'barra': 'bar', 'rosso': 'red'},
    'grade': {'cupo': 'moody', 'bn': 'bw', 'bianconero': 'bw', 'bianco-e-nero': 'bw', 'caldo': 'warm',
              'freddo': 'cool', 'vivido': 'pop', 'acceso': 'pop'},
    'font': {'grassetto': 'bold', 'corsivo': 'serif', 'mano': 'hand', 'macchina': 'mono'},
    'pos': {'sotto': 'below', 'sopra': 'above'},
}


def option(k, v):
    k = OPTIONS.get(k, k)
    if isinstance(v, str): v = VALUES.get(k, {}).get(v.lower(), v)
    return k, v
