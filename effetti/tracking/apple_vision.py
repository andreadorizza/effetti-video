"""Tracking on a Mac: Apple Vision finds your face and cuts you out, on the Neural Engine.

Cleaner edges than MediaPipe on hair, glasses and dark rooms. Needs the Xcode Command Line Tools
(`xcode-select --install`): vision_stream.swift is compiled once into .build/ on first use.
"""
import os, shutil, struct, subprocess, sys
import numpy as np
import cv2

from .common import guided, face_from_mask

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SWIFT = os.path.join(HERE, 'vision_stream.swift')
BIN = os.path.join(ROOT, '.build', 'vision_stream')
# Vision's face box is taller and a little wider than YuNet's, which the effects were placed against:
# scale its width and lift its centre so every effect lands where it does with MediaPipe.
FACE_W, FACE_DY = 1.0, 0.0


def binary():
    """The compiled helper, built on first use. None when this is not a Mac or Swift is missing."""
    if sys.platform != 'darwin': return None
    if os.path.exists(BIN) and os.path.getmtime(BIN) >= os.path.getmtime(SWIFT): return BIN
    if not shutil.which('swiftc'): return None
    os.makedirs(os.path.dirname(BIN), exist_ok=True)
    print('Preparo Apple Vision (solo la prima volta, circa 30 secondi)...', flush=True)
    r = subprocess.run(['swiftc', '-O', SWIFT, '-o', BIN], capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-2000:]); return None
    return BIN


def available():
    try: return binary() is not None
    except Exception: return False


class Tracker:
    name = 'vision'

    def __init__(self, aw, ah):
        self.aw, self.ah = aw, ah
        self.p = subprocess.Popen([binary(), str(aw), str(ah)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)

    def reset(self):
        pass

    def _read(self, n):
        b = bytearray()
        while len(b) < n:
            chunk = self.p.stdout.read(n - len(b))
            if not chunk: raise RuntimeError('Apple Vision si è fermato')
            b += chunk
        return bytes(b)

    def __call__(self, rgb, ms):
        self.p.stdin.write(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGRA).tobytes())
        cx, cy, fw, conf = struct.unpack('4f', self._read(16))
        mw, mh = struct.unpack('2i', self._read(8))
        if mw and mh:
            m = np.frombuffer(self._read(mw * mh), np.uint8).reshape(mh, mw).astype(np.float32) / 255
            m = cv2.resize(m, (self.aw, self.ah), interpolation=cv2.INTER_LINEAR)
            m = guided(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255, m)
            m = np.clip((m - 0.5) * 1.6 + 0.5, 0, 1)
        else:
            m = np.zeros((self.ah, self.aw), np.float32)
        face = (cx, cy + fw * FACE_DY, fw * FACE_W) if conf > 0 else face_from_mask(m)
        return (m * 255).astype(np.uint8), face

    def close(self):
        try:
            self.p.stdin.close(); self.p.wait(timeout=5)
        except Exception:
            self.p.kill()
