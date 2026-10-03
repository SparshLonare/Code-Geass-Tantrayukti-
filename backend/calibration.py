from dataclasses import dataclass

import numpy as np

import config as C
from metrics import angle_diff


@dataclass
class Baseline:
    """One person's normal face. Thresholds are derived from it, not fixed."""
    ear_open: float = 0.30
    blink_open: float = 0.10
    jaw_closed: float = 0.05
    pitch_base: float = 0.0
    pitch_std: float = 3.0
    calibrated: bool = False

    @property
    def ear_close_thr(self):
        return self.ear_open * C.EAR_CLOSE_RATIO

    @property
    def blink_close_thr(self):
        return min(0.7, max(0.30, self.blink_open + 0.30))

    @property
    def jaw_open_thr(self):
        return max(0.35, self.jaw_closed + 0.30)

    @property
    def nod_deg(self):
        return min(25.0, max(12.0, 4.0 * self.pitch_std))


class Calibrator:
    def __init__(self):
        self.active = False
        self.failed = False
        self.message = ""
        self.samples = []
        self.start_t = 0.0

    def start(self, t):
        self.active, self.failed, self.samples, self.start_t = True, False, [], t
        self.message = "Look at the camera, keep your eyes open and blink normally."

    def progress(self, t):
        return min(1.0, (t - self.start_t) / C.CALIBRATION_S) if self.active else 0.0

    def add(self, t, face):
        """Feed one frame. Returns a new Baseline when calibration finishes."""
        if not self.active:
            return None
        if face.face_found and face.blink < 0.5:    # skip blink frames
            self.samples.append((face.ear, face.blink, face.jaw, face.pitch))
        if t - self.start_t < C.CALIBRATION_S:
            return None

        self.active = False
        if len(self.samples) < C.CALIBRATION_MIN_SAMPLES:
            self.failed = True
            self.message = "Face not seen long enough. Face the camera and try again."
            return None

        a = np.array(self.samples)
        rad = np.radians(a[:, 3])
        pitch_base = float(np.degrees(np.arctan2(np.sin(rad).mean(), np.cos(rad).mean())))
        spread = np.array([angle_diff(p, pitch_base) for p in a[:, 3]])
        self.message = "Calibrated for this face."
        return Baseline(float(np.median(a[:, 0])), float(np.median(a[:, 1])),
                        float(np.median(a[:, 2])), pitch_base, float(spread.std()), True)
