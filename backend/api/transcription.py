from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from config import get_whisper_model_status
from services.meeting_repository import get_meeting, update_transcript_status
from services.transcription_service import transcribe_meeting_audio

router = APIRouter()


class TranscriptionStartRequest(BaseModel):
    meeting_id: str


@router.get("/model-status")
def get_model_status():
    return get_whisper_model_status()


@router.post("/start")
def start_transcription(
    request: TranscriptionStartRequest, background_tasks: BackgroundTasks
):
    meeting = get_meeting(request.meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if not meeting.audio_file:
        raise HTTPException(status_code=400, detail="Meeting has no audio file")
    model_status = get_whisper_model_status()
    if not model_status["installed"]:
        update_transcript_status(request.meeting_id, "failed")
        return {
            "success": False,
            "error": "MODEL_NOT_FOUND",
            "message": "Whisper model not found in local path.",
            "status": "failed",
            "model": model_status["model"],
            "path": model_status["path"],
        }

    update_transcript_status(request.meeting_id, "processing")
    background_tasks.add_task(transcribe_meeting_audio, request.meeting_id)

    return {
        "success": True,
        "status": "processing",
    }


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
