# Run the drowsiness monitor

Unzip into your project root (it merges into `backend/` and `ui/src/`; overwrite `App.jsx`, `main.jsx`, `index.css`).

## 1. Backend (venv active)
    pip install -r backend/requirements.txt
    cd backend
    # download the model once (PowerShell):
    Invoke-WebRequest -Uri https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task -OutFile face_landmarker.task
    uvicorn server:app --port 8000        # do NOT use --reload (it would open the camera twice)

## 2. Frontend (second terminal)
    cd ui
    npm install recharts
    npm run dev                            # open the printed localhost URL

## 3. First checks (5 minutes)
1. Status shows "Alert", camera overlay shows yellow dots on eyes and mouth.
2. Click Start calibration, look at the camera 12 s.
3. Nod your head DOWN and watch "Pitch change". If it goes negative, set PITCH_DOWN_SIGN = -1 in backend/config.py and restart.
4. Close your eyes 2 s -> Wake up (ALARM). Blink normally -> stays Alert.
5. Hold your mouth open 2 s -> Getting drowsy.

## Tuning
Everything is in backend/config.py. Video fallback: put .mp4 clips in backend/samples and pick them in the Source menu.
