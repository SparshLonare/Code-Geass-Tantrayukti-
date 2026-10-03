import cv2
import numpy as np

import config as C

_clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))


def enhance_if_dark(frame):
    """Returns (frame_for_detection, was_enhanced)."""
    if cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean() / 255.0 >= C.DARK_ENHANCE_BELOW:
        return frame, False
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = _clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR), True


def _crop_gray(frame, pts):
    h, w = frame.shape[:2]
    x0, y0 = np.clip(pts.min(axis=0).astype(int), 0, [w - 1, h - 1])
    x1, y1 = np.clip(pts.max(axis=0).astype(int), 0, [w - 1, h - 1])
    if x1 - x0 < 10 or y1 - y0 < 10:
        return None
    return cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)


def face_lighting(original, processed, pts):
    """Returns (face_brightness 0-1 on the original frame, light_ok judged after enhancement)."""
    g0 = _crop_gray(original, pts)
    g1 = _crop_gray(processed, pts)
    if g0 is None or g1 is None:
        return 0.0, False
    ok = C.BRIGHT_MIN <= g1.mean() / 255.0 <= C.BRIGHT_MAX and g1.std() / 255.0 >= C.MIN_CONTRAST
    return float(g0.mean() / 255.0), bool(ok)


def frame_brightness(frame):
    return float(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean() / 255.0)
