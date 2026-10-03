# Wakeup SID!!

A real-time fatigue and drowsiness monitoring system for drivers or operators. The project uses a webcam or sample video feed, tracks the user’s face with MediaPipe and OpenCV, and estimates alertness based on eye closure, yawning, and head nod patterns.

The application has two parts:

- A Python backend that captures frames, runs the detection pipeline, and exposes a FastAPI API and websocket stream.
- A React + Vite frontend that displays the live camera feed, current fatigue state, calibration controls, and reliability reporting.

## Why this project exists

The system is designed to detect early signs of drowsiness and escalate to warning/alarm states when fatigue indicators become severe. It continuously evaluates:

- Eye closure duration and perclos (percentage of eye closure over time)
- Yawning based on mouth openness duration
- Head nods and pitch changes
- Face visibility and lighting quality
- A calibrated baseline per user

## Project architecture

### Backend
The backend lives under the `backend/` directory and includes:

- `server.py` — FastAPI server, websocket stream, video endpoint, calibration and source APIs
- `pipeline.py` — main camera loop and detection pipeline
- `detector.py` — face and landmark detection wrapper
- `metrics.py` — fatigue scoring logic from facial metrics
- `alert_engine.py` — state machine for OK / WARNING / ALARM / LOW_CONFIDENCE / CALIBRATING
- `calibration.py` — calibration routines for a user’s neutral pose
- `evaluation.py` — scenario-based reliability report
- `config.py` — all tunable thresholds and timings
- `lighting.py` — brightness and contrast handling

### Frontend
The frontend lives under the `ui/` directory and includes:

- `src/App.jsx` — main dashboard layout
- `src/useMetrics.js` — websocket connection and live metric updates
- `src/components/` — video panel, status badge, chart, controls, source picker, alarm toggle, report page

## Features

- Live webcam or sample-video input
- Face landmark tracking and drowsiness scoring
- Calibration to a person’s neutral eye and head position
- Alert states: `OK`, `WARNING`, `ALARM`, `LOW_CONFIDENCE`, `CALIBRATING`
- Alarm audio feedback when the alert state becomes critical
- Reliability report for labeled test scenarios such as normal, closure, yawn, and nod
- Source switching between webcam and local sample clips

## Tech stack

### Backend
- Python
- OpenCV
- MediaPipe
- NumPy
- SciPy
- FastAPI
- Uvicorn

### Frontend
- React
- Vite
- Recharts

## Repository structure

```text
.
├── README.md
├── RUN.md
├── backend/
│   ├── alert_engine.py
│   ├── calibration.py
│   ├── config.py
│   ├── detector.py
│   ├── evaluation.py
│   ├── face_landmarker.task
│   ├── lighting.py
│   ├── metrics.py
│   ├── pipeline.py
│   ├── requirements.txt
│   ├── samples/
│   └── server.py
├── ui/
│   ├── index.html
│   ├── package.json
│   ├── public/
│   └── src/
└── .gitignore (if present in your setup)
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A webcam for live use, or pre-recorded `.mp4/.avi/.mov/.mkv/.webm` clips in `backend/samples/`
- A browser with access to the webcam

## Quick start

### 1. Set up the backend

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the MediaPipe face landmark model once:

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" -OutFile "face_landmarker.task"
```

Start the API server:

```powershell
uvicorn server:app --port 8000
```

> Do not use `--reload` with this project because it can open the camera twice and create duplicate capture threads.

### 2. Set up the frontend

Open a second terminal and run:

```powershell
cd ui
npm install
npm run dev
```

Then open the local URL printed by Vite in the browser.

## How to use the app

1. Confirm the backend is running and connected.
2. Choose `webcam` or a sample video source from the UI.
3. Start calibration and look straight at the camera for the calibration window.
4. Watch the live status change from `OK` to `WARNING` or `ALARM` as fatigue indicators accumulate.
5. Use the scenario buttons to evaluate reliability for:
   - normal operation
   - eye closure
   - yawning
   - head nodding
6. Review the reliability report tab for summary metrics such as recall, precision, F1 score, false alarms, and face detection rate.

## Configuration and tuning

Most tuning parameters are defined in `backend/config.py`.

Examples:

- eye closure threshold
- drowsiness alarm timing
- head nod sensitivity
- confidence thresholds
- calibration duration
- brightness filtering

If the pitch direction feels inverted while nodding, check the setting:

```python
PITCH_DOWN_SIGN = 1
```

If the UI shows a negative pitch change when nodding down, switch it to:

```python
PITCH_DOWN_SIGN = -1
```

## Troubleshooting

### Backend not connecting
- Ensure `uvicorn server:app --port 8000` is running in the backend folder.
- Check that the model file `backend/face_landmarker.task` exists.
- Confirm that no other process is already using port 8000.

### Webcam not available
- Allow camera access in the browser.
- Verify the machine has a working webcam.
- Use a sample video source instead.

### Poor detection quality
- Improve lighting in the scene.
- Keep the face centrally aligned in the camera.
- Re-run calibration after adjusting the environment.
- Tune values in `backend/config.py`.

## Notes

This project is best suited for desktop testing and prototyping in a local environment. It is not a production-grade driver safety system, but it provides a solid real-time proof of concept for computer-vision-based fatigue detection.

## License

This project does not currently declare a license file. If you plan to distribute or reuse it publicly, add an appropriate license such as MIT or Apache 2.0.
