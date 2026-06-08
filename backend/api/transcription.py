from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import get_whisper_model_status
from services.meeting_repository import get_meeting
from services.transcription_service import transcribe_meeting_audio

router = APIRouter()


class TranscriptionStartRequest(BaseModel):
    meeting_id: str


@router.get("/model-status")
def get_model_status():
    return get_whisper_model_status()


@router.post("/start")
def start_transcription(request: TranscriptionStartRequest):
    meeting = get_meeting(request.meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return transcribe_meeting_audio(request.meeting_id)


@router.get("/{meeting_id}")
def get_transcription(meeting_id: str):
    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return {
        "success": True,
        "status": meeting.transcript_status,
        "transcript": meeting.transcript_text or "",
        "transcript_file": meeting.transcript_file,
    }
