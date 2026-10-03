import os
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from scipy.spatial.transform import Rotation

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")

# 6 points per eye: outer corner, 2 upper lid, inner corner, 2 lower lid
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]
# left corner, right corner, upper inner lip, lower inner lip
MOUTH = [78, 308, 13, 14]


@dataclass
class FaceResult:
    face_found: bool = False
    ear: float = 0.0      # eye aspect ratio (landmarks)
    blink: float = 0.0    # eyeBlink blendshape, 0 open .. 1 closed
    jaw: float = 0.0      # jawOpen blendshape
    mar: float = 0.0      # mouth aspect ratio (display only)
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    points: Optional[np.ndarray] = None   # (478, 2) pixel coordinates


def _ear(p, i):
    d = lambda a, b: float(np.linalg.norm(p[i[a]] - p[i[b]]))
    return (d(1, 5) + d(2, 4)) / (2.0 * d(0, 3) + 1e-6)


class Detector:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        opts = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
        )
        self.lm = vision.FaceLandmarker.create_from_options(opts)
        self._last_ts = 0

    def detect(self, frame_bgr, ts_ms) -> FaceResult:
        ts_ms = max(int(ts_ms), self._last_ts + 1)   # timestamps must strictly increase
        self._last_ts = ts_ms
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = self.lm.detect_for_video(img, ts_ms)
        if not res.face_landmarks:
            return FaceResult()

        h, w = frame_bgr.shape[:2]
        pts = np.array([[l.x * w, l.y * h] for l in res.face_landmarks[0]], dtype=np.float32)
        shapes = {}
        if res.face_blendshapes:
            shapes = {c.category_name: c.score for c in res.face_blendshapes[0]}
        blink = (shapes.get("eyeBlinkLeft", 0.0) + shapes.get("eyeBlinkRight", 0.0)) / 2.0

        ear = (_ear(pts, LEFT_EYE) + _ear(pts, RIGHT_EYE)) / 2.0
        mar = float(np.linalg.norm(pts[13] - pts[14]) / (np.linalg.norm(pts[78] - pts[308]) + 1e-6))

        pitch = yaw = roll = 0.0
        if res.facial_transformation_matrixes:
            m = np.array(res.facial_transformation_matrixes[0])
            r = m[:3, :3]
            r = r / (np.linalg.norm(r, axis=0) + 1e-9)   # remove scale
            pitch, yaw, roll = Rotation.from_matrix(r).as_euler("xyz", degrees=True)

        return FaceResult(True, ear, blink, shapes.get("jawOpen", 0.0), mar,
                          float(pitch), float(yaw), float(roll), pts)
