from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.audio import router as audio_router
from api.meeting import router as meeting_router
from api.transcription import router as transcription_router
from database.connection import init_db

app = FastAPI(title="TransForum AI", version="Alpha 0.4.2")

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
        "version": "Alpha 0.4.2",
    }


@app.on_event("startup")
def startup():
    init_db()


app.include_router(meeting_router, prefix="/api/meeting", tags=["meeting"])
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])
app.include_router(transcription_router, prefix="/api/transcription", tags=["transcription"])
