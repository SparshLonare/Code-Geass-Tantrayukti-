"""Reliability report from labelled scenarios.

Press a scenario button (normal / closure / yawn / nod), act it out, press 'none' when done.
A positive scenario counts as detected if a new WARNING/ALARM starts while it is running.
An alert that starts during 'normal' is a false alarm.
"""

POSITIVE = ("closure", "yawn", "nod")
LABELS = ("none", "normal") + POSITIVE


class Evaluation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.segments = []
        self.cur = None
        self.prev_alert = False
        self.frames = self.face_frames = self.low_conf_frames = 0

    def update(self, t, label, state, face_found):
        if state == "CALIBRATING":
            return
        self.frames += 1
        self.face_frames += 1 if face_found else 0
        self.low_conf_frames += 1 if state == "LOW_CONFIDENCE" else 0

        alert = state in ("WARNING", "ALARM")
        onset = alert and not self.prev_alert
        self.prev_alert = alert

        if label == "none":
            self.cur = None
            return
        if self.cur is None or self.cur["label"] != label:
            self.cur = {"label": label, "start": t, "end": t, "first_alert": None, "onsets": 0}
            self.segments.append(self.cur)
        self.cur["end"] = t
        if onset:
            self.cur["onsets"] += 1
            if self.cur["first_alert"] is None:
                self.cur["first_alert"] = t - self.cur["start"]

    def report(self):
        pos = [s for s in self.segments if s["label"] in POSITIVE]
        neg = [s for s in self.segments if s["label"] == "normal"]
        detected = sum(1 for s in pos if s["first_alert"] is not None)
        true_on = sum(s["onsets"] for s in pos)
        false_on = sum(s["onsets"] for s in neg)
        normal_min = sum(s["end"] - s["start"] for s in neg) / 60.0

        recall = detected / len(pos) if pos else None
        precision = true_on / (true_on + false_on) if (true_on + false_on) else None
        f1 = (2 * precision * recall / (precision + recall)
              if precision and recall else (0.0 if precision is not None and recall is not None else None))

        scenarios = []
        for label in ("normal",) + POSITIVE:
            segs = [s for s in self.segments if s["label"] == label]
            lat = [s["first_alert"] for s in segs if s["first_alert"] is not None]
            scenarios.append({
                "label": label,
                "segments": len(segs),
                "detected": sum(1 for s in segs if s["first_alert"] is not None) if label != "normal" else None,
                "mean_latency_s": sum(lat) / len(lat) if lat and label != "normal" else None,
                "alerts": sum(s["onsets"] for s in segs),
                "seconds": sum(s["end"] - s["start"] for s in segs),
            })
        return {
            "summary": {
                "recall": recall, "precision": precision, "f1": f1,
                "false_alarms_per_min": (false_on / normal_min) if normal_min > 0 else None,
                "face_detect_rate": self.face_frames / self.frames if self.frames else None,
                "low_confidence_share": self.low_conf_frames / self.frames if self.frames else None,
                "positive_segments": len(pos), "detected_segments": detected,
                "normal_minutes": normal_min, "frames": self.frames,
            },
            "scenarios": scenarios,
        }
