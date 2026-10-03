import asyncio
import json
import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from pipeline import SAMPLES_DIR, VIDEO_EXT, Pipeline

pipe = Pipeline()


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=pipe.run, daemon=True).start()
    yield
    pipe.stop()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class SourceBody(BaseModel):
    source: str


async def mjpeg():
    last = -1
    while True:
        jpg, fid = pipe.latest_jpeg, pipe.frame_id
        if jpg and fid != last:
            last = fid
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        await asyncio.sleep(0.03)


@app.get("/video")
async def video():
    return StreamingResponse(mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame",
                             headers={"Cache-Control": "no-cache"})


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    try:
        while True:
            await sock.send_text(json.dumps(pipe.snapshot()))
            await asyncio.sleep(0.1)
    except (WebSocketDisconnect, RuntimeError):
        pass


@app.post("/calibrate/start")
def calibrate():
    pipe.start_calibration()
    return {"ok": True}


@app.post("/label/{name}")
def label(name: str):
    try:
        pipe.set_label(name)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"label": name}


@app.get("/sources")
def sources():
    files = sorted(f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith(VIDEO_EXT)) \
        if os.path.isdir(SAMPLES_DIR) else []
    return {"sources": ["webcam"] + files}


@app.post("/source")
def source(body: SourceBody):
    try:
        pipe.set_source(body.source)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"source": body.source}


@app.get("/report")
def report():
    return pipe.report()


@app.post("/report/reset")
def report_reset():
    pipe.reset_report()
    return {"ok": True}
