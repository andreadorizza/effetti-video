"""Il tema: colori, caratteri e stile di tutti gli effetti.

Senza tema gli effetti hanno il look originale (`neutro`). Un tema non riscrive gli effetti:
dà un valore ai **ruoli** che gli effetti usano. Ogni colore negli effetti è scritto così:

    P.c('accent', (217, 119, 87))

cioè "il ruolo accent, che nel look neutro vale (217, 119, 87)". Il tema neutro restituisce
il valore scritto; un tema restituisce il colore che ha dato a quel ruolo. Un ruolo che il
tema non definisce resta neutro.

Un tema è un file JSON (vedi docs/design-system.md e temi/):

    {"nome": "Dori",
     "design_system": "tokens.json", "tema": "dori",
     "colori": {"surface": "fx-surface", "on-surface": "fx-on-surface", "accent": "fx-accent", ...},
     "caratteri": {"display": "fonts/MatrixSansScreen-Regular.ttf", ...},
     "stile": {"raggio": 0, "ombre": true, "vetro": false, "bagliore": false, "sfumature": false}}

`colori` dà a ogni ruolo un token del design system (per nome) o un colore esadecimale.
Con un design system e senza `colori`, i ruoli si mappano da soli sui nomi di token più comuni.
"""
import colorsys, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The roles every effect draws with. The neutral value of each one is written at the call site.
ROLES = {
    'surface': 'light cards, panels, pills and bubbles',
    'on-surface': 'text, lines and icons on a surface',
    'dark': 'dark cards, panels and bars',
    'on-dark': 'text and icons on a dark card',
    'over': 'type and marks drawn straight over the footage',
    'paper': 'printed paper: the receipt, the magazine, the newspaper',
    'accent': 'the one signal: the Claude orange, the Instagram blue, the highlighted word',
    'on-accent': 'text on an accent fill',
    'accent2': 'a second highlight: yellow, peach, purple',
    'success': 'ticks, toggles switched on, a graph that climbs',
    'danger': 'the stamp, the REC dot, the heart, the error bar',
    'muted': 'secondary text: counters, meta lines, placeholders',
    'line': 'outlines, rules, empty checkboxes, tracks',
    'ground': 'a full-frame room that replaces yours: lavender, grid paper, a dark set',
}

# Where a role reads its value when a design system is given without an explicit "colori" map.
AUTO = {
    'surface': ['surface', 'surface-100', 'bg', 'background', 'paper', 'white'],
    'on-surface': ['on-surface', 'fg', 'ink', 'text', 'foreground'],
    'dark': ['inverse', 'surface-inverse', 'fg', 'ink', 'foreground'],
    'on-dark': ['on-inverse', 'bg', 'background', 'paper'],
    'over': ['on-footage', 'over', 'on-video', 'white', 'bg'],
    'paper': ['paper', 'surface', 'bg', 'background'],
    'accent': ['accent', 'primary', 'brand', 'signal'],
    'on-accent': ['on-accent', 'on-primary', 'on-brand'],
    'accent2': ['accent2', 'accent-2', 'secondary', 'accent'],
    'success': ['success', 'positive', 'ok', 'green', 'accent'],
    'danger': ['danger', 'error', 'negative', 'red', 'accent'],
    'muted': ['muted', 'text-muted', 'secondary-text', 'fg'],
    'line': ['dim', 'line', 'border', 'rule', 'muted'],
    'ground': ['ground', 'bg', 'background'],
}

# Her 14 font kinds fall into five groups; a theme replaces a group (or a single kind).
GROUPS = {'display': ('bold', 'anton'), 'serif': ('serif', 'didone', 'didoneb', 'didonei'),
          'mono': ('mono',), 'hand': ('hand',), 'ui': ('ui', 'uim', 'uib', 'mont', 'monts', 'montb')}
FONT = {k: os.path.join(ROOT, 'fonts', v) for k, v in {
    'bold': 'ArchivoBlack-Regular.ttf', 'serif': 'InstrumentSerif-Italic.ttf', 'mono': 'SpaceMono-Bold.ttf',
    'hand': 'PermanentMarker-Regular.ttf', 'ui': 'Inter.ttf', 'uim': 'Inter.ttf', 'uib': 'Inter.ttf',
    'anton': 'Anton-Regular.ttf', 'mont': 'Montserrat.ttf', 'monts': 'Montserrat.ttf', 'montb': 'Montserrat.ttf',
    'didone': 'PlayfairDisplay.ttf', 'didoneb': 'PlayfairDisplay.ttf', 'didonei': 'PlayfairDisplay-Italic.ttf'}.items()}
# Variable-font axes of the neutral fonts: Inter (optical size, weight), Montserrat and Playfair (weight)
WGHT = {'ui': (24, 640), 'uim': (24, 540), 'uib': (32, 860), 'mont': (700,), 'monts': (600,), 'montb': (800,),
        'didone': (500,), 'didoneb': (800,), 'didonei': (500,)}


# The text colour of each ground, for P.c(..., on=ground)
ON = {'dark': 'on-dark', 'surface': 'on-surface', 'paper': 'on-surface', 'ground': 'on-surface', 'accent': 'on-accent'}


def contrast(a, b):
    """WCAG contrast ratio between two RGB colours (1 to 21)."""
    def lum(c):
        c = [x / 255 for x in c[:3]]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def deepen(col, ground, target=3.0):
    """`col` in the same hue, darker on a light ground or lighter on a dark one, until it reads at `target`
    against `ground`; None when no shade of that hue gets there (a grey keeps the old fallback)."""
    h, l, sat = colorsys.rgb_to_hls(*(x / 255 for x in col[:3]))
    if sat < 0.15:
        return None
    dark_ground = contrast(ground, (0, 0, 0)) < contrast(ground, (255, 255, 255))
    for step in range(1, 41):
        l2 = min(1.0, l + step * 0.02) if dark_ground else max(0.0, l - step * 0.02)
        c = tuple(int(round(x * 255)) for x in colorsys.hls_to_rgb(h, l2, min(1.0, sat + step * 0.01)))
        if contrast(c, ground) >= target:
            return c
    return None


def hexrgb(v):
    """'#rgb', '#rrggbb' or '#rrggbbaa' (or a list) -> (r, g, b)."""
    if isinstance(v, (list, tuple)): return tuple(int(x) for x in v[:3])
    v = str(v).strip().lstrip('#')
    if len(v) in (3, 4): v = ''.join(ch * 2 for ch in v[:3])
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


class Theme:
    def __init__(self):
        self.name = 'neutro'
        self.roles = {}            # role -> (r, g, b)
        self.fonts = {}            # kind -> path
        self.font_axes = {}        # kind -> variable-font axes, e.g. [800] for the weight
        self.radius = 1.0          # 1 = the original corners, 0 = square
        self.shadows = True
        self.glass = True
        self.glow = True
        self.gradients = True
        self.tints = []            # (r, g, b) a theme's palette of hues, e.g. pastels: see _tint()
        self.tint_roles = set()    # the roles whose colours keep their meaning by hue

    @property
    def neutral(self): return not self.roles

    def c(self, role, rgb, a=None, on=None):
        """The colour of `role`, or `rgb` (its neutral value) when the theme leaves the role alone.
        With `a`, an RGBA tuple. `on` names the role of what it is drawn on ('dark', 'surface', 'accent'...):
        when the theme makes the two too alike to tell apart (under 3:1), the colour falls back to the text
        colour of that ground (on-dark, on-surface...). A two-colour theme can have accent = dark, for example."""
        col = self._tint(role, rgb) or self.roles.get(role, tuple(rgb[:3]))
        if on is not None and role in self.roles:
            ground = self.roles.get(on) if isinstance(on, str) else tuple(on[:3])
            if ground is not None and contrast(col, ground) < 3:
                # first the same hue, deeper (or lighter on a dark ground), so a colour keeps its meaning and a
                # logo stays recognisable (a pastel green icon on a white card turns deep green, not ink)
                shade = deepen(col, ground)
                if shade is not None:
                    col = shade
                elif isinstance(on, str):
                    col = self.roles.get(ON.get(on, 'on-surface'), col)
                else:  # an actual colour: the theme colour that reads best on it
                    col = max(self.roles.values(), key=lambda v: contrast(v, on))
        if a is None: a = rgb[3] if len(rgb) > 3 else None
        return tuple(col) + ((int(a),) if a is not None else ())

    def _tint(self, role, rgb):
        """With tints, a colour keeps its meaning: an effect's saturated original (the stamp's red, Claude's
        orange, Instagram's blue) becomes the theme's tint nearest to it in hue. Greys and dark or washed-out
        originals are left to the role. None when nothing applies."""
        if not self.tints or role not in self.tint_roles:
            return None
        h, sat, val = colorsys.rgb_to_hsv(*(x / 255 for x in rgb[:3]))
        if sat < 0.3 or val < 0.25:
            return None
        def dist(t):
            d = abs(colorsys.rgb_to_hsv(*(x / 255 for x in t))[0] - h)
            return min(d, 1 - d)
        return min(self.tints, key=dist)

    def r(self, px):
        """A corner radius, scaled by the theme (0 for square corners)."""
        return px if self.radius == 1 else px * self.radius

    def get(self, role):
        """The theme's colour for `role`, or None when the theme leaves it neutral."""
        return self.roles.get(role)

    def f(self, role, neutral):
        """A colour as float32 0..1 for numpy maths: the theme's, or `neutral` (already 0..1) untouched."""
        import numpy as np
        v = self._tint(role, [int(round(x * 255)) for x in list(neutral)[:3]]) or self.roles.get(role)
        return np.float32(neutral) if v is None else np.float32(v) / 255

    def font_path(self, kind):
        return self.fonts.get(kind, FONT[kind])

    def axes(self, kind):
        return WGHT.get(kind) if kind not in self.fonts else self.font_axes.get(kind)


P = Theme()


def _tokens(path, theme_id):
    """Colour tokens of a Claude design system (tokens.json) as {name: (r, g, b)} for one theme,
    plus the font files it lists by family."""
    ds = json.load(open(path))
    color = ds.get('color', {})
    themes = [t['id'] for t in color.get('themes', [])]
    tid = theme_id or (themes[0] if themes else None)
    if theme_id and themes and theme_id not in themes:
        raise SystemExit(f"Il design system non ha il tema '{theme_id}'. Temi: {', '.join(themes)}")
    raw = {}
    for t in color.get('tokens', []):
        v = t.get('value')
        if isinstance(v, dict): v = v.get(tid, v.get(themes[0]) if themes else None)
        if isinstance(v, str): raw[t['name']] = v
    out = {}
    def resolve(name, depth=0):
        v = raw.get(name)
        if v is None or depth > 8: return None
        if v.startswith('{') and v.endswith('}'): return resolve(v[1:-1], depth + 1)
        if v.startswith('#'): return hexrgb(v)
        if v.startswith('rgb'):
            nums = [float(x) for x in v[v.index('(') + 1:v.index(')')].replace('/', ',').split(',')[:3]]
            return tuple(int(round(x)) for x in nums)
        return None
    for name in raw:
        rgb = resolve(name)
        if rgb: out[name] = rgb
    base = os.path.dirname(os.path.abspath(path))
    fonts = {f['family']: os.path.join(base, f['file']) for f in ds.get('type', {}).get('fonts', []) if f.get('file')}
    return out, fonts, tid


def use(spec=None, theme_id=None):
    """Load a theme: None or 'neutro' for the original look, a theme file (.json), a folder that holds
    tema.json, a name under temi/, or a design system's tokens.json."""
    global P
    t = Theme()
    if not spec or spec == 'neutro':
        P.__dict__.update(t.__dict__); return P
    path = spec
    if not os.path.exists(path):
        for cand in (os.path.join(ROOT, spec), os.path.join(ROOT, 'temi', spec), os.path.join(ROOT, 'temi', spec + '.json')):
            if os.path.exists(cand): path = cand; break
        else:
            raise SystemExit(f"Tema non trovato: {spec}")
    if os.path.isdir(path):
        path = os.path.join(path, 'tema.json') if os.path.exists(os.path.join(path, 'tema.json')) else os.path.join(path, 'tokens.json')
    cfg = json.load(open(path))
    base = os.path.dirname(os.path.abspath(path))
    if 'color' in cfg and 'tema' not in cfg and 'colori' not in cfg:   # a bare tokens.json
        cfg = {'design_system': os.path.basename(path), 'tema': theme_id}
    tokens, ds_fonts, tid = {}, {}, None
    if cfg.get('design_system'):
        tokens, ds_fonts, tid = _tokens(os.path.join(base, cfg['design_system']), theme_id or cfg.get('tema'))
    t.name = cfg.get('nome') or os.path.splitext(os.path.basename(path))[0] + (f' · {tid}' if tid else '')
    colori = cfg.get('colori')
    if colori is None and tokens:
        colori = {role: next((n for n in names if n in tokens), None) for role, names in AUTO.items()}
    for role, v in (colori or {}).items():
        if role not in ROLES: raise SystemExit(f"Ruolo sconosciuto nel tema: '{role}'. Ruoli: {', '.join(ROLES)}")
        if v is None: continue
        t.roles[role] = tokens[v] if v in tokens else hexrgb(v)
    # a per-theme override of the colours, e.g. {"colori_tema": {"dark": {"over": "fg"}}}
    for role, v in cfg.get('colori_tema', {}).get(tid, {}).items():
        t.roles[role] = tokens[v] if v in tokens else hexrgb(v)
    car = dict(cfg.get('caratteri', {}))
    car.update(cfg.get('caratteri_tema', {}).get(tid, {}))
    for key, f in car.items():   # "ui": "fonts/X.ttf", or {"file": "fonts/X.ttf", "assi": [800]} for a variable font
        spec = f if isinstance(f, dict) else {'file': f}
        p = ds_fonts.get(spec['file']) or os.path.join(base, spec['file'])
        if not os.path.exists(p): raise SystemExit(f"Carattere non trovato per '{key}': {spec['file']}")
        for kind in GROUPS.get(key, (key,)):
            t.fonts[kind] = p
            if spec.get('assi'): t.font_axes[kind] = tuple(spec['assi'])
    # tints: a palette of hues ("tinte": token names or #hex); the roles in "tinte_ruoli" keep each effect's
    # colour meaning by snapping its original to the nearest tint (default: the signal roles)
    t.tints = [tokens[v] if v in tokens else hexrgb(v) for v in cfg.get('tinte', [])]
    t.tint_roles = set(cfg.get('tinte_ruoli', ['accent', 'accent2', 'success', 'danger']))
    st = cfg.get('stile', {})
    t.radius = float(st.get('raggio', 1.0))
    t.shadows = bool(st.get('ombre', True)); t.glass = bool(st.get('vetro', True))
    t.glow = bool(st.get('bagliore', True)); t.gradients = bool(st.get('sfumature', True))
    P.__dict__.update(t.__dict__)
    return P


_cmaps = {}


def covers(path, s):
    """True when the font at `path` has a glyph for every character of `s` (True if we cannot tell)."""
    if path not in _cmaps:
        try:
            from fontTools.ttLib import TTFont
            _cmaps[path] = set(TTFont(path, fontNumber=0).getBestCmap())
        except Exception:
            _cmaps[path] = None
    cm = _cmaps[path]
    return cm is None or all(ord(ch) in cm or ch in '\n\t\ufe0f' for ch in s)
