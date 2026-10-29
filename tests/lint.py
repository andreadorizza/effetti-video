"""Lint: the prose rules of docs/nuovo-effetto.md, checked on every effect (effetti/fx/*.py).

    .venv/bin/python tests/lint.py

1. Every colour through the theme: no bare RGB tuple (three or four ints, 0-255) outside P.c(), P.f() and the
   helpers that theme it themselves (on_glass(), glass(tint=...)). Black and white, at any alpha, are fine.
2. Every default text through tr(): no string with a word in it outside tr() and num(), unless it is a docstring,
   a key, a comparison, the effect's registration or the library's own vocabulary (roles, fonts, option values).
What is legitimately literal sits in LECITI, with the reason. Prints file:line for each offender; exits 1 if any.
"""
import ast, glob, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from effetti.i18n import VALUES  # noqa: E402
from effetti.theme import FONT, ROLES  # noqa: E402

# (file, literal as written): why it stays literal
LECITI = {
    **{('classifica.py', t): 'a tier row, themed where it is drawn: P.c(surface, col)' for t in (
        '(255, 127, 127)', '(255, 191, 127)', '(255, 223, 127)', '(191, 255, 127)', '(127, 191, 255)', '(191, 127, 255)')},
    ('copertina.py', '(2, 2, 3, 5)'): 'barcode bar widths, not a colour',
    ('copertina.py', '(2, 3, 4)'): 'barcode gaps, not a colour',
    ('copertina.py', '(252, 238, 228)'): 'the warm wash of the editorial film look, a grade of the footage as draw.grade',
    ('classifica.py', "'Claude'"): 'a name', ('rassegna_stampa.py', "'Claude'"): 'a name',
    ('widget_vetro.py', "'Claude'"): 'a name', ('insegna_led.py', "'CLAUDE'"): 'a name',
    ('parola_dietro.py', "'CLAUDE'"): 'a name', ('riflettore.py', "'CLAUDE'"): 'a name',
    ('copertina.py', "'VIBE'"): 'the masthead, a name',
    ('timeline.py', "'REC'"): 'the camera label, the same in Italian',
    ('parola_pastello.py', "'creator'"): 'the same word in Italian',
    ('widget_vetro.py', "'render'"): 'the same word in Italian',
    ('classifica.py', "'BCDF'"): 'tier letters, the keys of the rows',
    ('copertina.py', "'Ag'"): 'measures the line height, never drawn',
    ('rassegna_stampa.py', "'Ag'"): 'measures the line height, never drawn',
    ('commento.py', "'/System/Library/Fonts/Apple Color Emoji.ttc'"): 'a path',
    ('zoom_spalla.py', "r'\\s*([\\d.,]+)\\s*(.*)'"): 'a regular expression',
    ('zoom_spalla.py', "'line'"): 'a graph kind', ('zoom_spalla.py', "'bars'"): 'a graph kind',
}
BLACK_WHITE = ((0, 0, 0), (255, 255, 255))
THEMED = {'c', 'f', 'on_glass'}                    # P.c, P.f, on_glass: what they return is the theme's
LOCALISED = {'tr', 'num', 'effetto'}               # translated, a number in the language's notation, the registration
VOCAB = set(ROLES) | set(FONT) | {v for d in VALUES.values() for v in d.values()} | {'RGB', 'RGBA'}
NOT_TEXT = {'anchor', 'joint', 'mode'}             # keyword arguments that never take text
WORD = re.compile(r'[^\W\d_]{2,}')


def called(n):
    f = n.func if isinstance(n, ast.Call) else None
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, 'id', None)


def check(path):
    src = open(path, encoding='utf-8').read(); tree = ast.parse(src); name = os.path.basename(path)
    up = {ch: p for p in ast.walk(tree) for ch in ast.iter_child_nodes(p)}

    def chain(n):                                  # (child, parent) pairs from n up to the module
        while n in up: yield n, up[n]; n = up[n]

    def key(ch, p):                                # ch is a key there, never drawn
        return ((called(p) == 'get' and p.args[:1] == [ch]) or (called(p) == 'cached' and p.args[1:2] == [ch])
                or (isinstance(p, ast.Subscript) and ch is p.slice) or (isinstance(p, ast.Dict) and ch in p.keys))
    via_tr = {a.id for n in ast.walk(tree) if called(n) == 'tr' for a in n.args if isinstance(a, ast.Name)}
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.Tuple, ast.List)) and 3 <= len(n.elts) <= 4 and all(
                isinstance(x, ast.Constant) and type(x.value) is int and 0 <= x.value <= 255 for x in n.elts):
            p = up.get(n)
            if tuple(x.value for x in n.elts[:3]) in BLACK_WHITE: continue
            if isinstance(p, ast.keyword) and p.arg == 'tint' and called(up.get(p)) == 'glass': continue
            if any(called(a) in THEMED for _, a in chain(n)): continue
            what = 'colore fuori dal tema'
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and WORD.search(n.value) and n.value not in VOCAB:
            p = up.get(n)
            if isinstance(p, (ast.Expr, ast.Compare)): continue                     # a docstring, a comparison
            if isinstance(p, ast.keyword) and p.arg in NOT_TEXT: continue
            if any(key(ch, a) or called(a) in LOCALISED for ch, a in chain(n)): continue
            if any(isinstance(a, ast.Assign) and {getattr(t, 'id', None) for t in a.targets} & via_tr for _, a in chain(n)):
                continue                                                             # a constant handed to tr()
            what = 'testo senza tr()'
        else:
            continue
        lit = ast.get_source_segment(src, n)
        if (name, lit) not in LECITI: out.append((n.lineno, f'{name}:{n.lineno}: {what} {lit}'))
    return [m for _, m in sorted(out)]


def main():
    bad = [m for p in sorted(glob.glob(os.path.join(HERE, 'effetti', 'fx', '*.py'))) for m in check(p)]
    for m in bad: print(m)
    if bad:
        print(f'\n{len(bad)} da sistemare: le regole sono in docs/nuovo-effetto.md; un valore davvero fisso va in LECITI (tests/lint.py)')
        sys.exit(1)
    print('OK: colori dal tema e testi con tr()')


if __name__ == '__main__':
    main()
