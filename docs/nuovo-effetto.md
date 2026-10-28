# Aggiungere un effetto

Ogni effetto è un file in `effetti/fx/`. Aggiungerne uno vuol dire aggiungere un file: si registra da solo.

```python
"""bolla (bubble): Una bolla di testo che segue la tua testa."""
from ..draw import *


@effetto('bolla', en='bubble', alias=('fumetto',),
         desc='Una bolla di testo che segue la tua testa')
def fx_bolla(c, e):
    k = ease_back(c.lt / 0.3) * fade(c, e)                       # entra con un rimbalzo, esce in dissolvenza
    testo = e.o.get('text', tr('Ciao!', 'Hi!'))
    t = text_img(testo, c.W * 0.06, 'uib', P.c('on-surface', INK))
    bolla = rrect(t.width + c.W * 0.06, t.height * 1.4, t.height * 0.7, P.c('surface', (255, 255, 255), 240))
    bolla.alpha_composite(t, (int(c.W * 0.03), int(t.height * 0.2)))
    x = clamp(c.fx + c.fw * 1.1, bolla.width * 0.6, c.W - bolla.width * 0.6)  # resta dentro l'inquadratura
    place(c, shadowed(bolla, 12, 6, 90), x, c.fy - c.fw * 0.9, 0.6 + 0.4 * k, 0, k, guard=True)
```

Poi `python scripts/effetti.py bolla video.mp4 prova.png --fermo 1` e guarda il fotogramma.

## Cosa hai a disposizione

Un effetto è una funzione `(c, e)` chiamata una volta per fotogramma, finché l'effetto è attivo.

- `c.img`: il fotogramma, float32 RGB da 0 a 1 (`H × W × 3`). Disegnaci sopra.
- `c.m`: la maschera della persona, da 0 a 1 (1 dove ci sei tu).
- `c.fx`, `c.fy`, `c.fw`: centro e larghezza del viso, in pixel, già smussati nel tempo.
- `c.lt`: secondi dall'inizio dell'effetto. `e.d`: quanto dura. `c.W`, `c.H`: dimensioni.
- `e.o`: le opzioni (`e.o.get('text', ...)`). `e.state`: un dizionario per la cache (`cached(e, 'chiave', funzione)`). `e.cards`: le reel dell'utente, se registri l'effetto con `schede=True`.

Da `draw.py`:
- **Disegnare:** `text_img`, `fit_text`, `rrect`, `card`, `shadowed`, `glass`, `heart`, `cursor`, `tick`, `face_chip`.
- **Comporre:** `place(c, img, cx, cy, scale, rot, alpha, behind=True)` mette un'immagine *dietro* di te (dove c'è la persona sparisce); `guard=True` la tiene lontana solo dal viso. `comp` fa lo stesso dato l'angolo in alto a sinistra.
- **Camera:** `camera`, `face_cam` (zoom sul viso, massimo 2x), `shift`.
- **Tempo:** `ease_out`, `ease_inout`, `ease_back`, `ramp`, `pop`, `fade`, `clamp`.
- **Colore della ripresa:** `grade`, `vignette`.

## Tre regole per stare nel tema e in italiano

1. **Ogni colore passa dal tema:** `P.c('ruolo', (r, g, b))`, con `(r, g, b)` il colore del look neutro. I ruoli sono in `docs/design-system.md`. Mai una tupla RGB nuda per qualcosa che si vede (le ombre nere e il trasparente vanno bene). Se disegni un segnale su una scheda scura, aggiungi `on='dark'` (o `on='surface'`, o il colore vero del fondo): in un tema a due colori l'accento può essere uguale alla scheda, e così ripiega sul colore del testo di quella scheda invece di sparire.
2. **Ogni angolo passa dal tema:** `P.r(raggio)` nei `rounded_rectangle` che scrivi tu (`rrect` e `card` lo fanno già). Vetro, aloni e sfumature disegnati a mano: controlla `P.glass`, `P.glow`, `P.gradients`, `P.shadows`.
3. **Ogni testo predefinito si traduce:** `tr('italiano', 'english')`.

Se aggiungi un effetto visto altrove, scrivi da dove viene nel docstring del file, e controlla la licenza prima di copiare codice.

## Controllare

```bash
# il tuo effetto, neutro e con un tema
.venv/bin/python scripts/effetti.py bolla video.mp4 neutro.png --fermo 1
.venv/bin/python scripts/effetti.py bolla video.mp4 dori.png --fermo 1 --tema temi/dori --variante raster

# i 45 originali disegnano ancora esattamente come quelli di Vibha (serve il suo repo e una clip di almeno 2 minuti)
.venv/bin/python tests/confronto.py ../claude-video-effects clip.mp4 /tmp/confronto
```
