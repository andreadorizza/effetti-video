#!/usr/bin/env bash
# Preparazione, una volta sola. Si può rilanciare: stampa PRONTO quando è tutto a posto.
set -e
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "SERVE_FFMPEG: installa ffmpeg (Mac: brew install ffmpeg, Windows: winget install ffmpeg)"; exit 1
fi
if [ -x .venv/bin/python ] && .venv/bin/python -c "import mediapipe, cv2, PIL, numpy" 2>/dev/null; then
  .venv/bin/python -c "from effetti.tracking import pick; print('Tracciamento:', pick('auto').name)"; echo PRONTO; exit 0
fi

PY=""
for v in python3.12 python3.11 python3.10 python3; do
  if command -v "$v" >/dev/null 2>&1 && "$v" -c 'import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)' 2>/dev/null; then PY="$v"; break; fi
done

if [ -n "$PY" ]; then
  "$PY" -m venv .venv
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r requirements.txt
elif command -v uv >/dev/null 2>&1; then
  uv venv -q -p 3.12 .venv
  uv pip install -q -p .venv/bin/python -r requirements.txt
else
  echo "SERVE_PYTHON: installa Python 3.12 (python.org/downloads), poi rilancia questo script"; exit 1
fi

# On a Mac, build the Apple Vision helper now, so the first video doesn't wait for it.
.venv/bin/python -c "from effetti.tracking import pick; print('Tracciamento:', pick('auto').name)"
.venv/bin/python -c "import mediapipe, cv2, PIL, numpy; print('PRONTO')"
