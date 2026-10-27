"""Who finds your face and cuts you out. `auto` picks the best one for this computer:
Apple Vision on a Mac (when Swift is installed), MediaPipe + YuNet everywhere else."""
import sys


def pick(name='auto'):
    name = (name or 'auto').lower()
    if name in ('vision', 'apple', 'apple-vision'):
        from . import apple_vision
        if not apple_vision.available():
            raise SystemExit('Apple Vision non è disponibile: serve un Mac con gli strumenti Xcode (xcode-select --install).')
        return apple_vision.Tracker
    if name in ('mediapipe', 'mp'):
        from . import mediapipe_yunet
        return mediapipe_yunet.Tracker
    if sys.platform == 'darwin':
        from . import apple_vision
        if apple_vision.available(): return apple_vision.Tracker
    from . import mediapipe_yunet
    return mediapipe_yunet.Tracker
