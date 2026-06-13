from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.audio import router as audio_router
from api.meeting import router as meeting_router
from api.minutes import router as minutes_router
from api.realtime import router as realtime_router
from api.transcription import router as transcription_router
from database.connection import init_db

app = FastAPI(title="TransForum AI", version="Alpha 1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "project": "TransForum AI",
        "version": "Alpha 1.1",
    }


@app.on_event("startup")
def startup():
    init_db()


app.include_router(meeting_router, prefix="/api/meeting", tags=["meeting"])
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])
app.include_router(transcription_router, prefix="/api/transcription", tags=["transcription"])
app.include_router(realtime_router, prefix="/api/realtime", tags=["realtime"])
app.include_router(minutes_router, prefix="/api/minutes", tags=["minutes"])
