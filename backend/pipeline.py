import os
import threading
import time
from collections import deque

import cv2

import config as C
from alert_engine import AlertEngine
from calibration import Baseline, Calibrator
from detector import LEFT_EYE, MOUTH, RIGHT_EYE, Detector
from evaluation import LABELS, Evaluation
from lighting import enhance_if_dark, face_lighting, frame_brightness
from metrics import Tracker

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
VIDEO_EXT = (".mp4", ".avi", ".mov", ".mkv", ".webm")
COLORS = {  # BGR
    "OK": (94, 197, 34), "WARNING": (11, 158, 245), "ALARM": (68, 68, 239),
    "LOW_CONFIDENCE": (184, 163, 148), "CALIBRATING": (246, 130, 59),
}


class Pipeline:
    """Owns the camera. One background thread: frame -> detect -> metrics -> alert -> JPEG."""

    def __init__(self, detector=None):
        self.detector = detector
        self.tracker, self.base = Tracker(), Baseline()
        self.calib, self.engine, self.evalr = Calibrator(), AlertEngine(), Evaluation()
        self.label, self.source, self._source_changed = "none", "webcam", True
        self.latest_jpeg, self.frame_id = None, 0
        self.error, self._fps, self._last_t = "", 0.0, None
        self._found = deque(maxlen=100)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._snap = {"state": "LOW_CONFIDENCE", "error": "Starting..."}

    # ---- control (called from API threads) ----
    def start_calibration(self):
        self.calib.start(time.monotonic())
        self.tracker.reset()

    def set_label(self, name):
        if name not in LABELS:
            raise ValueError(f"unknown label: {name}")
        self.label = name

    def set_source(self, source):
        if source != "webcam":
            path = os.path.join(SAMPLES_DIR, os.path.basename(source))
            if not os.path.isfile(path):
                raise ValueError(f"no such sample video: {source}")
            source = os.path.basename(source)
        self.source, self._source_changed = source, True

    def snapshot(self):
        with self._lock:
            return dict(self._snap)

    def report(self):
        return self.evalr.report()

    def reset_report(self):
        self.evalr.reset()

    def stop(self):
        self._stop.set()

    # ---- capture loop ----
    def _open(self):
        if self.source == "webcam":
            return cv2.VideoCapture(0, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(0)
        return cv2.VideoCapture(os.path.join(SAMPLES_DIR, self.source))

    def run(self):
        try:
            if self.detector is None:
                self.detector = Detector()
        except Exception as e:  # missing model etc.
            self.error = f"Model load failed: {e}"
            print(self.error)
            self._publish_error()
            return

        cap, interval = None, 0.0
        while not self._stop.is_set():
            if cap is None or self._source_changed:
                if cap is not None:
                    cap.release()
                self._source_changed = False
                self.tracker.reset()
                self.engine = AlertEngine()
                cap = self._open()
                if not cap.isOpened():
                    self.error = "Cannot open " + ("the webcam" if self.source == "webcam" else self.source)
                    self._publish_error()
                    cap.release()
                    cap = None
                    time.sleep(1.0)
                    self._source_changed = True
                    continue
                self.error = ""
                fps = cap.get(cv2.CAP_PROP_FPS)
                interval = 0.0 if self.source == "webcam" else 1.0 / (fps if fps and fps > 1 else 30.0)

            t0 = time.monotonic()
            ok, frame = cap.read()
            if not ok:
                if self.source != "webcam":
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)   # loop the clip
                else:
                    self.error = "Camera read failed"
                    self._publish_error()
                time.sleep(0.1)
                continue

            self._process(frame, t0)
            if interval:                                   # play clips at real speed
                time.sleep(max(0.0, interval - (time.monotonic() - t0)))
        if cap is not None:
            cap.release()

    def _publish_error(self):
        with self._lock:
            self._snap = {"state": "LOW_CONFIDENCE", "error": self.error, "label": self.label,
                          "source": self.source}

    # ---- one frame ----
    def _process(self, frame, t):
        h, w = frame.shape[:2]
        if w != C.FRAME_WIDTH:
            frame = cv2.resize(frame, (C.FRAME_WIDTH, int(h * C.FRAME_WIDTH / w)))
        if self.source == "webcam":
            frame = cv2.flip(frame, 1)

        proc, dark = enhance_if_dark(frame)
        face = self.detector.detect(proc, t * 1000.0)

        if face.face_found:
            bright, light_ok = face_lighting(frame, proc, face.points)
        else:
            bright, light_ok = frame_brightness(frame), True

        new_base = self.calib.add(t, face)
        if new_base is not None:
            self.base = new_base
            self.tracker.reset()

        if face.face_found and not self.calib.active:
            sig = self.tracker.update(t, face, self.base)
        else:
            if not face.face_found:
                self.tracker.lost()
            sig = Tracker.empty()

        state = self.engine.update(t, sig["score"], face.face_found, light_ok, self.calib.active)
        self.evalr.update(t, self.label, state, face.face_found)
        self._found.append(face.face_found)

        if self._last_t is not None and t > self._last_t:
            self._fps = 0.9 * self._fps + 0.1 / (t - self._last_t) if self._fps else 1.0 / (t - self._last_t)
        self._last_t = t

        self._draw(frame, face, state, sig, t)
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, C.JPEG_QUALITY])

        snap = {
            "t": time.time(), "state": state, "reason": self.engine.reason,
            "face_found": face.face_found, "fatigue_score": round(sig["score"], 3),
            "blink": round(face.blink, 3), "ear": round(face.ear, 3), "jaw": round(face.jaw, 3),
            "mar": round(face.mar, 3), "perclos": round(sig["perclos"], 3),
            "pitch": round(face.pitch, 1), "yaw": round(face.yaw, 1),
            "pitch_delta": round(sig["pitch_delta"], 1),
            "closure_s": round(sig["closure_s"], 2), "head_down_s": round(sig["head_down_s"], 2),
            "yawns": sig["yawns"], "nods": sig["nods"], "components": sig["components"],
            "brightness": round(bright, 3), "dark_mode": dark, "fps": round(self._fps),
            "detect_rate": round(sum(self._found) / len(self._found), 3) if self._found else 0,
            "calibration": {"done": self.base.calibrated, "active": self.calib.active,
                            "progress": round(self.calib.progress(t), 3), "failed": self.calib.failed,
                            "message": self.calib.message,
                            "baseline_ear": round(self.base.ear_open, 3),
                            "baseline_blink": round(self.base.blink_open, 3)},
            "label": self.label, "source": self.source, "error": self.error,
        }
        with self._lock:
            if ok:
                self.latest_jpeg = buf.tobytes()
                self.frame_id += 1
            self._snap = snap

    def _draw(self, frame, face, state, sig, t):
        h, w = frame.shape[:2]
        color = COLORS[state]
        if face.points is not None:
            for i in LEFT_EYE + RIGHT_EYE + MOUTH:
                cv2.circle(frame, tuple(face.points[i].astype(int)), 1, (0, 255, 255), -1)
        cv2.rectangle(frame, (0, 0), (w, 32), color, -1)
        cv2.putText(frame, state.replace("_", " "), (10, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        note = self.engine.reason
        if self.calib.active:
            note = f"Look at the camera... {int(self.calib.progress(t) * 100)}%"
        if note:
            cv2.putText(frame, note, (170, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if state == "ALARM":
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), color, 8)
