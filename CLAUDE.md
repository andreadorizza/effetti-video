# effetti-video

Libreria pubblica (MIT): 45 effetti video con nomi italiani. Il look di default è neutro, identico all'originale di Vibha; le regole della casa di ~/Projects/video-making (palette Dori, Matrix Sans, effetti ritirati) qui non valgono, e `temi/dori` è solo un tema d'esempio.

## L'API che usa video-making: cambiarla rompe quel repo
`tools/effects.py` e `tools/hf_build.py` di ~/Projects/video-making usano:
- `effetti.engine`: `Fx(d)` (`name start end d o state cards`), `Ctx` (`W H t fps lt img m fx fy fw`), `load_cards`
- `effetti.cli.normalise`; `effetti.i18n`: `EFFECTS` (`fn`, `cards`), `set_lang`, `option`, `LOOKS`
- `effetti.theme`: `Theme` e i suoi campi, `P`, `GROUPS`, `hexrgb`; `effetti.draw.camera`, che video-making sostituisce in ogni modulo fx che la importa
- un effetto è `fn(c, e)` registrato con `@effetto('nome', en=..., alias=(...))` ad argomenti letterali: hf_build.py li legge con `ast.literal_eval`, carica `i18n.py` dal suo percorso (che quindi importa solo la libreria standard) e tratta come effetto di camera ogni file che chiama `face_cam(` o `camera(`
- copie da tenere allineate: lo zoom di default di ogni effetto di camera (`CAMERA` in hf_build.py), `FACE_W, FACE_DY` di `tracking/apple_vision.py` (in tools/effects.py), `theme.deepen` (in tools/logo.py)

## Le prove
- `.venv/bin/python tests/lint.py`, meno di un secondo: colori dal tema e testi con `tr()`, le regole di `docs/nuovo-effetto.md`
- `.venv/bin/python tests/fumo.py`, 20-40 secondi, serve solo ffmpeg: ogni effetto col tema neutro e con `temi/dori`, più un secondo di video coi tag bt709
- `git config core.hooksPath .githooks`, una volta per clone: il pre-commit lancia il lint sempre e la prova di fumo quando cambiano `effetti/` o `temi/`. La CI (`.github/workflows/prove.yml`) le lancia tutte e due
- `tests/confronto.py` resta manuale (6 minuti, il repo di Vibha e una clip di 2 minuti): l'identità al pixel con l'originale
