#!/usr/bin/env python3
"""Quando dici ogni parola, così un effetto può partire sulla parola giusta.

uso: python scripts/parole.py video.mp4 [--lingua it]   -> stampa righe "12.34  parola" e salva video.words.json

Sul Mac con mlx-whisper installato usa quello (veloce, sul chip). Altrove usa faster-whisper, che si installa
nel .venv al primo uso. Gira tutto sul tuo computer: niente costi, niente upload.
WHISPER_MODEL sceglie il modello di faster-whisper (default: small, buono per l'italiano).
By Vibha Ramprakash (MIT), from claude-video-effects; adapted for Italian.
"""
import argparse, json, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('video')
ap.add_argument('--lingua', '--lang', dest='lang', default='it', help="lingua del parlato (it di default; 'auto' per riconoscerla)")
a = ap.parse_args()
lang = None if a.lang == 'auto' else a.lang
out = os.path.splitext(a.video)[0] + '.words.json'
words = []
try:
    import mlx_whisper
    r = mlx_whisper.transcribe(a.video, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True, language=lang)
    words = [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)} for seg in r['segments'] for w in seg.get('words', [])]
except ImportError:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print('Installo la trascrizione (una volta sola, circa un minuto)...', flush=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'faster-whisper'], check=True)
        from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get('WHISPER_MODEL', 'small'), device='cpu', compute_type='int8')
    segs, _ = model.transcribe(a.video, word_timestamps=True, vad_filter=True, language=lang)
    words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or [])]

json.dump(words, open(out, 'w'), indent=0, ensure_ascii=False)
for w in words: print(f"{w['s']:7.2f}  {w['w']}")
print(f'\nSalvate {len(words)} parole in {out}')
