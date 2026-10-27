"""Il tema: colori, caratteri e stile di tutti gli effetti.

Senza tema gli effetti hanno il look originale (`neutro`). Un tema non riscrive gli effetti:
dà un valore ai **ruoli** che gli effetti usano. Ogni colore negli effetti è scritto così:

    P.c('accent', (217, 119, 87))

cioè "il ruolo accent, che nel look neutro vale (217, 119, 87)". Il tema neutro restituisce
il valore scritto; un tema restituisce il colore che ha dato a quel ruolo. Un ruolo che il
tema non definisce resta neutro.

Un tema è un file JSON (vedi docs/design-system.md e temi/):

    {"nome": "Dori · screen",
     "design_system": "dori/tokens.json", "tema": "screen",
     "colori": {"surface": "bg", "on-surface": "fg", "accent": "accent", ...},
     "caratteri": {"display": "dori/fonts/MatrixSansScreen-Regular.ttf", ...},
     "stile": {"raggio": 0, "ombre": false, "vetro": false, "bagliore": false, "sfumature": false}}

`colori` dà a ogni ruolo un token del design system (per nome) o un colore esadecimale.
Con un design system e senza `colori`, i ruoli si mappano da soli sui nomi di token più comuni.
"""
import json, os

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
        self.radius = 1.0          # 1 = the original corners, 0 = square
        self.shadows = True
        self.glass = True
        self.glow = True
        self.gradients = True

    @property
    def neutral(self): return not self.roles

    def c(self, role, rgb, a=None):
        """The colour of `role`, or `rgb` (its neutral value) when the theme leaves the role alone.
        With `a`, an RGBA tuple."""
        col = self.roles.get(role, tuple(rgb[:3]))
        if a is None: a = rgb[3] if len(rgb) > 3 else None
        return tuple(col) + ((int(a),) if a is not None else ())

    def r(self, px):
        """A corner radius, scaled by the theme (0 for square corners)."""
        return px * self.radius

    def font_path(self, kind):
        return self.fonts.get(kind, FONT[kind])

    def axes(self, kind):
        return WGHT.get(kind) if kind not in self.fonts else None


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
        for cand in (os.path.join(ROOT, 'temi', spec), os.path.join(ROOT, 'temi', spec + '.json')):
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
    # a per-theme override of the colours, e.g. {"colori_tema": {"raster": {"accent": "#ffd08a"}}}
    for role, v in cfg.get('colori_tema', {}).get(tid, {}).items():
        t.roles[role] = tokens[v] if v in tokens else hexrgb(v)
    car = dict(cfg.get('caratteri', {}))
    car.update(cfg.get('caratteri_tema', {}).get(tid, {}))
    for key, f in car.items():
        p = ds_fonts.get(f) or os.path.join(base, f)
        if not os.path.exists(p): raise SystemExit(f"Carattere non trovato per '{key}': {f}")
        for kind in GROUPS.get(key, (key,)): t.fonts[kind] = p
    st = cfg.get('stile', {})
    t.radius = float(st.get('raggio', 1.0))
    t.shadows = bool(st.get('ombre', True)); t.glass = bool(st.get('vetro', True))
    t.glow = bool(st.get('bagliore', True)); t.gradients = bool(st.get('sfumature', True))
    P.__dict__.update(t.__dict__)
    return P
