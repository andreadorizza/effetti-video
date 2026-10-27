import numpy as np
import cv2


def guided(I, p, r=8, eps=2e-3):
    """Guided filter: snaps a soft mask to the edges of the picture."""
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p); a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps); b = mp_ - a * mI
    return np.clip(box(a) * I + box(b), 0, 1)


def face_from_mask(m):
    """No face found: guess it from the top of the person mask."""
    rows = np.where((m > 0.5).sum(1) > m.shape[1] * 0.01)[0]
    if not len(rows): return None
    top = rows[0]; band = m[top:top + max(4, int(m.shape[0] * 0.06))] > 0.5; xs = np.where(band.any(0))[0]
    fw = max(8.0, (xs.max() - xs.min()) * 0.8)
    return (float(xs.mean()), top + fw * 0.7, fw)
