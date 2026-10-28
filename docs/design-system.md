# Temi: gli effetti con il tuo design system

Gli effetti non hanno colori fissi. Ogni colore è un **ruolo** ("la scheda chiara", "il testo sopra il video", "l'evidenziatore"), e un tema dice quale colore dare a ogni ruolo. Senza tema (`neutro`) ogni ruolo tiene il colore originale di Vibha, quindi il look di default è il suo, identico pixel per pixel.

```bash
python scripts/effetti.py da-fare video.mp4 uscita.mp4 --tema temi/dori
```

`--tema` accetta:
- `neutro` (default);
- un nome sotto `temi/` (`dori`);
- una cartella con `tema.json`, o con il solo `tokens.json` di un design system;
- un file `tema.json`, o un `tokens.json` direttamente.

`--variante` sceglie uno dei temi del design system (chiaro/scuro, o come li hai chiamati). Senza, si usa il tema scritto in `tema.json`, o il primo del design system.

## Da un design system di Claude

Un design system fatto su claude.ai (tipo *Design System*) tiene i suoi valori in `project/tokens.json`: colori per tema, caratteri, raggi, ombre. È proprio quello che serve qui. Basta chiedere a Claude "usa il mio design system per gli effetti" e dargli il link: la skill legge `tokens.json`, il README e i caratteri, li salva in `temi/<nome>/` e scrive la mappa. A mano funziona così:

```
temi/<nome>/
├── tokens.json      ← copiato com'è dal design system
├── fonts/           ← i file dei caratteri che tokens.json elenca
├── licenses/        ← le loro licenze
└── tema.json        ← la mappa: ruoli → token, caratteri, stile
```

Con il solo `tokens.json` (senza `tema.json`) i ruoli si mappano da soli sui nomi di token più comuni (`bg`, `fg`, `accent`, `on-accent`, `muted`, `dim`, `surface`, `primary`...). Funziona, ma la mappa scritta a mano è sempre meglio: sai tu quale colore è "la scheda" e quale "l'evidenziatore".

## tema.json

```json
{
  "nome": "Il mio brand",
  "design_system": "tokens.json",
  "tema": "light",
  "colori": {
    "surface": "bg", "on-surface": "fg",
    "dark": "fg", "on-dark": "bg",
    "over": "#ffffff",
    "accent": "accent", "on-accent": "on-accent", "accent2": "accent2",
    "success": "accent", "danger": "accent",
    "muted": "muted", "line": "dim", "paper": "bg", "ground": "bg"
  },
  "colori_tema": {"dark": {"over": "fg"}},
  "caratteri": {
    "display": "fonts/Brand-Black.ttf",
    "ui": {"file": "fonts/Brand-Variable.woff2", "assi": [600]},
    "serif": "fonts/Brand-Italic.ttf",
    "mono": "fonts/BrandMono.ttf",
    "hand": "fonts/Brand-Italic.ttf"
  },
  "caratteri_tema": {},
  "stile": {"raggio": 1, "ombre": true, "vetro": true, "bagliore": true, "sfumature": true}
}
```

- **`colori`**: ogni ruolo prende il nome di un token del design system, o un colore `#rrggbb`. Un ruolo che non scrivi resta neutro.
- **`colori_tema`**: differenze per una variante (qui: in `dark` il testo sopra il video usa `fg`).
- **`caratteri`**: un file per gruppo. Per un carattere variabile, `{"file": ..., "assi": [peso]}`. Un gruppo che non scrivi resta quello originale. `caratteri_tema` fa lo stesso per una variante.
- **`stile`**: `raggio` moltiplica gli angoli arrotondati (1 = originali, 0 = angoli vivi); `ombre`, `vetro`, `bagliore` e `sfumature` a `false` tolgono ombre morbide, pannelli di vetro (diventano schede piatte), aloni luminosi e sfumature.

## I ruoli

| Ruolo | Cos'è | Neutro (esempi) |
|---|---|---|
| `surface` | Schede chiare, pannelli, pillole, fumetti | bianco, crema |
| `on-surface` | Testo, linee e icone su una scheda chiara | quasi nero |
| `dark` | Schede, pannelli e barre scure | quasi nero |
| `on-dark` | Testo e icone su una scheda scura | bianco |
| `over` | Testo e segni disegnati direttamente sul video | bianco |
| `paper` | Carta stampata: lo scontrino, la rivista, il giornale | crema |
| `accent` | Il segnale: l'arancione di Claude, il blu di Instagram, la parola evidenziata | arancione, blu |
| `on-accent` | Testo su un riempimento `accent` | bianco |
| `accent2` | Un secondo evidenziatore | giallo, pesca, viola |
| `success` | Spunte, interruttori accesi, un grafico che sale | verde |
| `danger` | Il timbro, il pallino REC, il cuore, la barra d'errore | rosso |
| `muted` | Testo secondario: contatori, righe di dettaglio, segnaposto | grigio |
| `line` | Contorni, righe, caselle vuote, binari | grigio chiaro |
| `ground` | Una stanza che sostituisce la tua: lilla, carta a quadretti, un set scuro | lilla, quadretti |

Controlla il contrasto delle coppie che contano: `on-surface` su `surface`, `on-dark` su `dark`, `on-accent` su `accent`, e `over` sopra il tuo video.

## Cosa non cambia

- Le **schermate vere** (le tue reel, le pagine, le immagini che passi con `immagini`) restano dei loro colori.
- Le **correzioni colore** del video (`atmosfera`, il bianco e nero di `collage-rosso`) sono trattamenti della ripresa, non colori del brand.
- Gli **emoji** restano emoji.

## L'esempio: temi/dori

Il design system di Andrea Dorizza, esportato com'è da claude.ai. Ha un tema solo, `dori`: carta bianca, inchiostro, il verde salvia come accento e i suoi pastelli (lilla, rosa, foglia). La mappa dei ruoli sta nel design system stesso, un token `fx-*` per ruolo (`fx-surface`, `fx-on-surface`...), e `tema.json` li prende uno a uno. È un esempio di tema che cambia **solo i colori**: gli effetti tengono angoli, vetro, bagliori, ombre e sfumature originali. Le schede (`surface`) restano bianche col testo in inchiostro, quelle scure (`dark`) quasi nere col testo bianco, il testo sul video (`over`) bianco; il salvia va sugli accenti (`accent`), il lilla sul secondo evidenziatore (`accent2`), il rosa su timbri e cuori (`danger`). Matrix Sans Screen solo per le scritte grandi (`display`); il testo piccolo (`ui`) è in Schibsted Grotesk. Un colore pastello non regge un testo su una scheda bianca: dove serve, l'effetto passa all'inchiostro da solo (`P.c(..., on='surface')`). Guardalo per vedere una mappa completa.
