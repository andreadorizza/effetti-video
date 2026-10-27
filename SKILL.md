---
name: effetti
description: Aggiunge uno dei 45 effetti video a un video parlato (orbita, riflettore, widget di vetro, timeline, checklist, muro di titoli, commento Instagram, ventaglio di telefoni, grafico di vetro liquido, rassegna stampa, interruttori iPhone, insegna LED, zoom alla spalla, notifiche iMessage, griglia profilo e altri), in italiano e con il tema del tuo design system. Gli effetti seguono il viso e possono stare dietro la testa. Usalo quando l'utente scrive /effetti, nomina uno degli effetti (anche col nome inglese originale, es. orbit, spotlight, glass-widgets), chiede di aggiungere un effetto, uno zoom, un colore, un adesivo o un'animazione al suo video, o vuole gli effetti con i colori e i caratteri del suo design system.
---

# Effetti: 45 effetti video per Claude, in italiano

Porting di [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects) di Vibha Ramprakash (MIT), con nomi e testi in italiano, temi da design system e Apple Vision sul Mac.

Chi lo usa di solito non è tecnico. Rispondi breve e in italiano, fai tu il lavoro, non chiedere mai di lanciare comandi.

Tutti i percorsi qui sotto partono dalla cartella di questa skill (quella che contiene questo SKILL.md). Nei comandi usa il percorso assoluto.

## 1. Primo avvio: preparazione (una volta)
Lancia `bash scripts/setup.sh`. Quando ha finito stampa `PRONTO` (la prima volta ci mette da 1 a 3 minuti).
- `SERVE_FFMPEG`: installalo tu. Sul Mac `brew install ffmpeg` (se manca `brew`, chiedi di installare Homebrew da brew.sh). Su Windows `winget install ffmpeg`.
- `SERVE_PYTHON`: installa Python 3.12 (Mac `brew install python@3.12`, Windows `winget install Python.Python.3.12`), poi rilancia.
- Su Windows il Python è in `.venv\Scripts\python.exe` invece di `.venv/bin/python`.

Il tracciamento (chi trova il viso e ti ritaglia) si sceglie da solo: **Apple Vision** sul Mac, se ci sono gli strumenti Xcode (`xcode-select --install`), altrimenti **MediaPipe**. Si forza con `--tracciamento vision` o `--tracciamento mediapipe`.

## 2. Il video e l'effetto
- Video: l'utente lo trascina nella chat o dà un percorso. Meglio un video verticale dal telefono.
- Effetto: da `/effetti <nome>`, o da come lo descrive. Confronta le sue parole con la tabella. Se hai dubbi, mostragli l'elenco (`.venv/bin/python scripts/effetti.py --elenco`).
- I nomi inglesi originali funzionano sempre (`orbit` = `orbita`).

## 3. I tempi
- Se dice "sulla parola X" o "quando dico ...", lancia `.venv/bin/python scripts/parole.py <video>` e usa quei tempi (italiano di default; `--lingua en` o `--lingua auto` per altre lingue).
- Se non dà tempi, applica l'effetto a tutto il video, o chiedi quale parte (una domanda breve).
- Le finestre brevi rendono meglio: da 1,5 a 4 secondi per effetto.

## 4. Bozza, controllo, video
1. Scrivi il piano accanto al video come `<nome-video>_effetti.json`:
   ```json
   {"effetti": [
     {"effetto": "orbita", "inizio": 3.2, "fine": 6.0},
     {"effetto": "parola-dietro", "inizio": 14.0, "fine": 16.3, "testo": "CLAUDE"}
   ]}
   ```
   Le chiavi vanno bene in italiano o in inglese (`effetto`/`fx`, `inizio`/`start`, `fine`/`end`, `testo`/`text`). In cima al piano puoi mettere `"tema"` e `"variante"`.
2. Prima controlla qualche fotogramma (è veloce): `.venv/bin/python scripts/effetti.py --piano <piano.json> <video> <cartella>/prova.png --fermo 4.5,15.2`, a metà di ogni effetto. Guarda tu i PNG. Se qualcosa non va (copre il viso, esce dal bordo, non si legge), correggi testo, tempi o opzioni.
3. Il video: `.venv/bin/python scripts/effetti.py --piano <piano.json> <video> <nome-video>_effetti.mp4`. L'audio resta quello originale. Esce a 1080p; `--larghezza 2160` per il 4K (più lento).
4. Digli dove trova il file. Ricordagli in una riga di guardarlo prima di pubblicarlo: tu fai la bozza, lui approva.

Un effetto solo non ha bisogno del piano: `.venv/bin/python scripts/effetti.py orbita <video> <uscita.mp4> --inizio 3 --fine 6 --testo "..." --opt chiave=valore`.

## 5. Il tema: colori e caratteri del suo design system
Senza tema gli effetti hanno il look originale (`neutro`). Con `--tema` prendono i colori, i caratteri e lo stile di un design system. Funziona con qualsiasi design system di Claude (tipo *Design System* su claude.ai) o con un suo `tokens.json`. Come è fatto un tema: `docs/design-system.md`. Un esempio completo: `temi/dori/`.

Se l'utente vuole i suoi colori:
1. **Prendi il design system.** Se ti dà un link claude.ai, leggi con lo strumento degli artifact `project/README.md`, `project/tokens.json`, i file dei caratteri che `tokens.json` elenca in `type.fonts[].file` e le loro licenze. Altrimenti chiedigli il `tokens.json` (o la cartella del design system). Salva tutto in `temi/<nome>/`: `tokens.json`, `fonts/`, `licenses/`.
2. **Scrivi `temi/<nome>/tema.json`.** Dai a ogni ruolo il token giusto (tabella dei ruoli in `docs/design-system.md`), scegli un carattere per gruppo (`display`, `ui`, `serif`, `mono`, `hand`) e imposta `stile` seguendo le regole del suo README: angoli vivi → `"raggio": 0`; niente ombre, vetro, bagliori o sfumature → `false` per ognuno. Se il design system ha più temi (chiaro/scuro, o varianti), usa `colori_tema` e `caratteri_tema` per le differenze.
3. **Controlla.** Un fotogramma di prova con `--tema temi/<nome>` (e `--variante <tema>` se serve) su un effetto per famiglia: una scheda (`da-fare`), un'interfaccia (`commento`), una parola dietro (`parola-dietro`), una stanza (`parola-pastello`). Il testo deve leggersi; se un colore stona, cambia la mappa, non gli effetti.

Le schermate vere restano dei loro colori: il tema cambia la grafica, non le reel o le pagine che ci metti dentro.

## I 45 effetti
| # | Nome | Cosa fa | Opzioni (tutte facoltative) | Originale |
|---|---|---|---|---|
| 1 | `rumore` | Le tue reel si accumulano dietro la testa, una ogni quarto di secondo | `immagini` (cartella di screenshot o clip), `dimensione` | `noise` |
| 2 | `in-fila` | Tessere numerate si aprono ad arco sopra la testa | `testo` (nomi delle tessere separati da `\|`) | `lineup` |
| 3 | `agganciato` | Quattro angoli si agganciano al viso, la camera ti segue | `zoom` (1.35), `testo` (etichetta) | `locked-on` |
| 4 | `orbita` | Le tue reel ti girano intorno alla testa: davanti in basso, dietro in alto | `immagini`, `quanti`, `velocita`, `dimensione` | `orbit` |
| 5 | `zoom-lampo` | Uno zoom veloce su una parola | `zoom` (1.45, massimo 2), `velocita` | `lean-in` |
| 6 | `parola-dietro` | Una parola gigante cade dietro di te | `testo`, `colore` (hex), `carattere` (`grassetto` o `corsivo`) | `backdrop-word` |
| 7 | `riflettore` | Le luci si spengono, resti illuminato solo tu | `testo` (parola luminosa dietro di te), `colore`, `spinta` | `spotlight` |
| 8 | `scontrino` | Le istruzioni escono stampate come uno scontrino, nel muro sopra la testa | `testo` (righe con `\|`) | `the-bill` |
| 9 | `atmosfera` | Una correzione colore cupa | `tono` (`cupo`, `bn`, `caldo`, `freddo`, `vivido`) | `moody` |
| 10 | `prima-dopo` | Un cursore prima/dopo che ti attraversa | `tono` (il look del "dopo") | `swipe` |
| 11 | `da-fare` | Una lista accanto alla testa che si spunta mentre parli | `testo` (voci con `\|`), `spunte` (secondi del video con `\|`), `titolo` | `todo` |
| 12 | `commento` | Il pannello commenti di Instagram scrive la tua parola, la pubblica, riceve un cuore e la tua risposta | `testo` (default EFFETTI), `profilo`; `stile=barra` per la barra semplice | `comment-box` |
| 13 | `segui` | Compare un pulsante Segui che diventa Segui già | `quando` (secondo del video), `x`, `y` (da 0 a 1), `colore` | `tap` |
| 14 | `fermo-immagine` | L'immagine si blocca e una freccia disegnata a mano ti indica | `testo` (etichetta), `colore`, `etichetta_x` | `pause-point` |
| 15 | `disinstalla` | Una barra di disinstallazione glitchata spacca l'immagine | `testo` | `uninstall` |
| 16 | `cornice-reel` | Il video si rimpicciolisce dentro una scheda reel di Instagram | `testo` (profilo) | `reel-frame` |
| 17 | `pioggia-tasti` | Tasti della tastiera piovono dietro di te | `testo` (tasti con `\|`), `quanti` | `shortcut-rain` |
| 18 | `timbro` | Un grosso timbro cala sullo schermo | `testo`, `colore`, `angolo`, `y` | `reject-stamp` |
| 19 | `conto-alla-rovescia` | Un orologio a palette con 3, 2, 1 sopra la testa | `da` | `countdown-flip` |
| 20 | `tunnel` | L'immagine sprofonda in sé stessa, girando | `rapporto`, `velocita`, `rotazione` | `rabbit-hole` |
| 21 | `copertina` | Diventi la copertina di una rivista, col titolo dietro la testa | `testo` (testata), `righe` (con `\|`), `uscita`, `colore` | `cover-star` |
| 22 | `scarabocchi` | Scarabocchi a pennarello si disegnano da soli intorno a te | `testo` (etichetta), `colore` | `scribble` |
| 23 | `widget-vetro` | Widget di vetro e mini artefatti fluttuano intorno alla testa | `testo` (numero grande), `nome`, `profilo`, `stile` (`semplice` per la versione a 3 widget) | `glass-widgets` |
| 24 | `collage-rosso` | Tu in bianco e nero, una parola rossa gigante dietro, tre righe che entrano di colpo | `testo` (parola), `righe` (con `\|`), `targhetta` | `red-collage` |
| 25 | `titolo-diviso` | Una scheda col titolo scende dall'alto e ti spinge nella metà bassa | `testo` (righe con `\|`), `evidenzia` (parola evidenziata), `pillola` | `split-headline` |
| 26 | `parola-pastello` | Stanza lilla, parola gigante dietro di te, una scheda profilo riceve un Segui | `testo`, `nome`, `profilo` | `pastel-word` |
| 27 | `pillole` | Stanza a quadretti, le tue reel appese dietro di te, un cursore clicca le pillole | `testo` (pillole con `\|`), `immagini` | `check-pills` |
| 28 | `timeline` | Look da film rosso scuro, timeline di montaggio, timecode REC e testina luminosa | `testo` (titolo), `sottotitolo`, `timecode` | `timeline` |
| 29 | `titolo-box` | Uno zoom con un titolo su due righe, la seconda in un riquadro | `testo` (righe con `\|`), `zoom` | `headline-box` |
| 30 | `muro-profilo` | La griglia delle tue reel riempie il muro dietro di te, un contatore sale | `immagini`, `quanti`, `etichetta` | `profile-wall` |
| 31 | `classifica` | Arriva una tier list e Claude vola in fascia S | `titolo`, `elemento`, `altri` | `tier-list` |
| 32 | `broll-diviso` | B-roll sopra con un'etichetta prezzo, tu sotto | `immagini`, `testo` (etichetta) | `broll-split` |
| 33 | `ventaglio` | Le tue reel si aprono come una mano di telefoni, sotto un titolo | `immagini`, `testo` (righe con `\|`) | `phone-fan` |
| 34 | `puntini` | L'inquadratura si compone di puntini luminosi, poi torna nitida | `colore`, `cella` | `dot-reveal` |
| 35 | `muro-titoli` | I tuoi titoli si accumulano dietro la testa, poi davanti compare un totale | `testo` (`titolo::meta\|...`), `totale`, `etichetta` | `headline-wall` |
| 36 | `passaggi` | Una lista di passaggi di Claude sotto il mento: ogni passo gira, poi si spunta | `testo` (`passo::meta\|...`), `titolo` | `checklist` |
| 37 | `grafico-vetro` | Una scheda di vetro liquido: un grafico sale mentre il numero conta | `testo` (etichetta), `da`, `a` (es. `197K`, `59%`), `colore` | `liquid-glass-graph` |
| 38 | `giostra` | Le tue reel ti girano intorno in una giostra 3D, poi si fermano | `immagini`, `quanti`, `dimensione`, `giri` | `carousel-spin` |
| 39 | `rassegna-stampa` | Pagine di giornale che cambiano su una parola, ferma in un riquadro dietro la testa | `testo` (la parola, default Claude), `colore` | `match-cut` |
| 40 | `interruttori` | Una scheda Impostazioni dell'iPhone accende gli interruttori, una riga alla volta | `testo` (righe con `\|`), `spunte` (secondi con `\|`), `colore`, `posizione` (`sotto` per la scheda sotto il mento), `sovrapposizione`, `zoom` | `apple-toggles` |
| 41 | `insegna-led` | Le luci calano e un'insegna LED si scrive da sola dietro di te | `testo` (righe con `\|`), `colore`, `spinta` | `led-sign` |
| 42 | `carrellata` | Una lenta spinta cinematografica sul viso, la stanza va fuori fuoco | `zoom` (1.6), `sfocatura` | `slow-push` |
| 43 | `zoom-spalla` | La camera entra in un angolo in alto, un grafico di vetro compare accanto alla testa, poi l'altro angolo con un secondo grafico | `testo` (due etichette con `\|`), `a` (due numeri con `\|`, es. `197K\|672K`), `zoom` (2.0) | `over-the-shoulder-zoom` |
| 44 | `messaggi` | Notifiche di iMessage compaiono una dopo l'altra | `testo` (messaggi con `\|`), `titolo` (default Messaggi), `y` | `messages` |
| 45 | `griglia-profilo` | Ti rimpicciolisci nella casella centrale della tua griglia 3x3, le reel compaiono intorno con le visualizzazioni | `immagini` (cartella delle tue reel o copertine), `visualizzazioni` (9 numeri con `\|`, il 9° è il tuo) | `place-in-grid` |

**Stili con nome** (stesso effetto, un look più ricco; non contano come effetti nuovi):
- `riflettore-glitter` = `riflettore` con `stile=glitter`: la stanza si spegne, raggi dorati da dietro la testa, una grande parola d'oro con un riflesso, scintille. `testo`, `colore`, `spinta`.
- `copertina` con `stile=editoriale`: un look da pellicola calda, testata serif classica dietro la testa, uscita e righe di copertina eleganti. `testo`, `uscita`, `righe` (3 righe con `\|`), `destra` (righe con `\|`), `colore`, `accento`, `righe_y`, `destra_y`.
- `grafico-vetro` con `stile=bento`: il grafico va su uno schermo di vetro fumé dietro la testa, con tessere di vetro davanti (una ciambella, un KPI, delle barre). `testo`, `da`, `a`, `ciambella` (`29%::etichetta`), `kpi` (`672K::etichetta`), `barre` (`197\|140\|124::etichetta`).

## Regole
- Mai coprire il viso. Ogni elemento sta dietro la persona o evita il viso da solo; se un fotogramma di prova mostra testo sul viso, spostalo (`x`, `y`) o accorcia il testo.
- Gli effetti si applicano nell'ordine del piano. Metti prima gli effetti di camera (`agganciato`, `zoom-lampo`, `riflettore`) quando si sovrappongono ad altri.
- Lo zoom non supera mai 2x, così il video resta nitido.
- Questa skill aggiunge solo la grafica. Effetti sonori e sottotitoli li aggiunge l'utente (CapCut va bene).
- Sono versioni di partenza. Se l'utente le confronta con una reel che ha visto, dillo con onestà.
- Testi in italiano di default; `--lingua en` rimette i testi originali in inglese.
