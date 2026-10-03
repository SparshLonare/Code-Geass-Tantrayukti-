import config as C


class AlertEngine:
    """OK / WARNING / ALARM with hysteresis, plus LOW_CONFIDENCE and CALIBRATING."""

    def __init__(self):
        self.state = "OK"
        self.reason = ""
        self.alarm_since = None
        self.face_lost_since = None

    def _set(self, state, t=None):
        if state == "ALARM" and self.state != "ALARM":
            self.alarm_since = t
        self.state = state

    def update(self, t, score, face_found, light_ok, calibrating):
        if calibrating:
            self.reason = "calibrating"
            self.state = "CALIBRATING"
            return self.state

        if not face_found:
            if self.face_lost_since is None:
                self.face_lost_since = t
            if t - self.face_lost_since >= C.FACE_LOST_S:
                self.state, self.reason = "LOW_CONFIDENCE", "Face not visible"
            return self.state          # brief loss keeps the previous state
        self.face_lost_since = None

        if not light_ok:
            self.state, self.reason = "LOW_CONFIDENCE", "Lighting too poor to monitor"
            return self.state

        prev = "OK" if self.state in ("LOW_CONFIDENCE", "CALIBRATING") else self.state
        self.reason = ""
        if prev == "ALARM":
            held = self.alarm_since is not None and t - self.alarm_since < C.ALARM_MIN_HOLD_S
            if held or score >= C.ALARM_OFF:
                self.state = "ALARM"
            else:
                self.state = "WARNING" if score >= C.WARN_OFF else "OK"
        elif prev == "WARNING":
            if score >= C.ALARM_ON:
                self._set("ALARM", t)
            else:
                self.state = "WARNING" if score >= C.WARN_OFF else "OK"
        else:
            if score >= C.ALARM_ON:
                self._set("ALARM", t)
            else:
                self.state = "WARNING" if score >= C.WARN_ON else "OK"
        return self.state
