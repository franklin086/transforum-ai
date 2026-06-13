from datetime import datetime
import re

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.meeting_repository import get_meeting
from services.realtime_transcription_service import (
    save_realtime_chunk,
    transcribe_realtime_chunk,
)

router = APIRouter()


def _latest_text_from_transcript(transcript: str) -> str:
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    if not lines:
        return ""
    return re.sub(r"^\[\d{2}:\d{2}:\d{2}\]\s*", "", lines[-1]).strip()


@router.post("/transcribe-chunk")
def transcribe_chunk(
    meeting_id: str = Form(...),
    chunk_index: int = Form(...),
    audio: UploadFile = File(...),
):
    if chunk_index < 1:
        raise HTTPException(status_code=400, detail="chunk_index must be positive")

    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    chunk_path = save_realtime_chunk(audio, meeting_id, chunk_index)
    result = transcribe_realtime_chunk(meeting_id, chunk_index, chunk_path)
    if not result["success"] and result.get("error") == "MEETING_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Meeting not found")

    return result


@router.get("/transcript/{meeting_id}")
def get_realtime_transcript(meeting_id: str):
    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    transcript = meeting.realtime_transcript_text or ""
    latest_text = _latest_text_from_transcript(transcript)
    response = {
        "success": True,
        "meeting_id": meeting_id,
        "transcript": transcript,
        "latest_text": latest_text,
    }
    if transcript:
        response["updated_at"] = datetime.utcnow().replace(microsecond=0).isoformat()
    else:
        response["message"] = "No realtime transcript yet."
    return response


@router.get("/bilingual/{meeting_id}")
def get_bilingual_realtime_transcript(meeting_id: str):
    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    chinese = _latest_text_from_transcript(meeting.realtime_transcript_text or "")
    english = _latest_text_from_transcript(meeting.english_transcript_text or "")
    return {
        "success": True,
        "meeting_id": meeting_id,
        "chinese": chinese,
        "english": english,
        "provider": meeting.translation_provider or "mock",
        "updated_at": datetime.utcnow().replace(microsecond=0).isoformat(),
    }
