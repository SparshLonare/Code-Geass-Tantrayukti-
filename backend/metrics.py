from collections import deque

import config as C


def angle_diff(a, b):
    """Signed difference a-b in degrees, wrapped to [-180, 180)."""
    return (a - b + 180.0) % 360.0 - 180.0


def _prune(dq, t, window):
    while dq and t - dq[0] > window:
        dq.popleft()


class Tracker:
    """Turns per-frame face values into durations, counts and one 0-1 fatigue score."""

    def __init__(self):
        self.closed_hist = deque()    # (t, closed)
        self.yawn_times = deque()
        self.nod_times = deque()
        self.reset()

    def reset(self):
        self.closed_hist.clear()
        self.yawn_times.clear()
        self.nod_times.clear()
        self.lost()

    def lost(self):
        """Face missing: drop running timers so stale durations never trigger alarms."""
        self.closed_since = None
        self.mouth_since = None
        self.yawn_counted = False
        self.down_since = None

    @staticmethod
    def empty():
        return {"closed": False, "closure_s": 0.0, "perclos": 0.0, "mouth_open_s": 0.0,
                "yawns": 0, "head_down_s": 0.0, "nods": 0, "pitch_delta": 0.0,
                "components": {"closure": 0.0, "perclos": 0.0, "yawn": 0.0, "head": 0.0},
                "score": 0.0}

    def update(self, t, face, base):
        # Eyes: closed only if the landmark ratio AND the blendshape agree
        closed = face.ear < base.ear_close_thr and face.blink > base.blink_close_thr
        if closed:
            self.closed_since = self.closed_since if self.closed_since is not None else t
            closure = t - self.closed_since
        else:
            self.closed_since, closure = None, 0.0

        self.closed_hist.append((t, closed))
        while self.closed_hist and t - self.closed_hist[0][0] > C.PERCLOS_WINDOW_S:
            self.closed_hist.popleft()
        span = t - self.closed_hist[0][0]
        perclos = (sum(1 for _, c in self.closed_hist if c) / len(self.closed_hist)) if span >= 5 else 0.0

        # Yawn: mouth held open long enough, counted once per yawn
        if face.jaw > base.jaw_open_thr:
            if self.mouth_since is None:
                self.mouth_since, self.yawn_counted = t, False
            mouth_s = t - self.mouth_since
            if mouth_s >= C.YAWN_MIN_S and not self.yawn_counted:
                self.yawn_times.append(t)
                self.yawn_counted = True
        else:
            self.mouth_since, mouth_s = None, 0.0
        _prune(self.yawn_times, t, C.YAWN_WINDOW_S)

        # Head: pitch change from this person's calibrated neutral pose
        delta = angle_diff(face.pitch, base.pitch_base)
        if C.PITCH_DOWN_SIGN * delta > base.nod_deg:
            self.down_since = self.down_since if self.down_since is not None else t
            down_s = t - self.down_since
        else:
            if self.down_since is not None and t - self.down_since >= C.NOD_MIN_S:
                self.nod_times.append(t)
            self.down_since, down_s = None, 0.0
        _prune(self.nod_times, t, C.NOD_WINDOW_S)

        comp = {
            "closure": min(closure / C.CLOSURE_ALARM_S, 1.0),
            "perclos": min(max(perclos - C.PERCLOS_FLOOR, 0.0) / (C.PERCLOS_ALARM - C.PERCLOS_FLOOR), 1.0),
            "yawn": max(0.5 if mouth_s >= C.YAWN_MIN_S else 0.0,
                        min(len(self.yawn_times) / C.YAWN_ALARM_COUNT, 1.0)),
            "head": max(min(down_s / C.HEAD_DOWN_ALARM_S, 1.0),
                        min(len(self.nod_times) / C.NOD_ALARM_COUNT, 1.0)),
        }
        return {"closed": closed, "closure_s": closure, "perclos": perclos,
                "mouth_open_s": mouth_s, "yawns": len(self.yawn_times),
                "head_down_s": down_s, "nods": len(self.nod_times), "pitch_delta": delta,
                "components": comp, "score": max(comp.values())}
