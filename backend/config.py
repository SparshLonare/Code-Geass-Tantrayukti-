"""Every tunable number lives here. Edit, then restart the server."""

FRAME_WIDTH = 640
JPEG_QUALITY = 70

# Eye closure
EAR_CLOSE_RATIO = 0.55    # closed = below 55% of this person's own open-eye EAR
CLOSURE_ALARM_S = 1.5     # warning starts around 0.75 s; a normal blink is 0.1-0.4 s
PERCLOS_WINDOW_S = 15
PERCLOS_FLOOR = 0.08      # normal blinking already closes the eyes ~8% of the time
PERCLOS_ALARM = 0.30      # share of the window with eyes closed

# Yawn
YAWN_MIN_S = 1.5          # mouth held open this long counts as a yawn (talking is shorter)
YAWN_WINDOW_S = 60
YAWN_ALARM_COUNT = 3

# Head nod
PITCH_DOWN_SIGN = 1       # set to -1 if "pitch change" in the UI goes NEGATIVE when you nod down
HEAD_DOWN_ALARM_S = 2.0
NOD_MIN_S = 0.4
NOD_WINDOW_S = 30
NOD_ALARM_COUNT = 3

# Alert state machine (hysteresis: enter high, leave low)
WARN_ON, WARN_OFF = 0.50, 0.35
ALARM_ON, ALARM_OFF = 0.90, 0.60
ALARM_MIN_HOLD_S = 2.0
FACE_LOST_S = 1.0

# Lighting
BRIGHT_MIN, BRIGHT_MAX = 0.12, 0.93   # face brightness (0-1) outside this = low confidence
MIN_CONTRAST = 0.03
DARK_ENHANCE_BELOW = 0.35             # whole-frame brightness below this triggers CLAHE

# Calibration
CALIBRATION_S = 12
CALIBRATION_MIN_SAMPLES = 40
