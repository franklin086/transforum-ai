from datetime import datetime
import re

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from services.meeting_repository import get_meeting
from services.realtime_transcription_service import (
    save_realtime_chunk,
    transcribe_realtime_chunk,
)
from websocket.connection_manager import manager

router = APIRouter()
websocket_router = APIRouter()


def _latest_text_from_transcript(transcript: str) -> str:
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    if not lines:
        return ""
    return re.sub(r"^\[\d{2}:\d{2}:\d{2}\]\s*", "", lines[-1]).strip()


def _is_mock_placeholder(text: str) -> bool:
    compact = (text or "").strip().lower()
    return compact.startswith("[" + "mock en" + "]")


def _safe_english_from_transcript(transcript: str) -> str:
    latest = _latest_text_from_transcript(transcript)
    return "" if _is_mock_placeholder(latest) else latest


def _safe_provider(provider: str | None, english: str, fallback_reason: str | None) -> str:
    if provider == "mock" and fallback_reason:
        return "mock"
    if english.strip():
        return provider or "waiting"
    return "waiting"


@router.post("/transcribe-chunk")
def transcribe_chunk(
    meeting_id: str = Form(...),
    chunk_index: int = Form(...),
    audio_mode: str = Form("pcm_wav"),
    chunk_duration_ms: int = Form(3000),
    audio: UploadFile = File(...),
):
    if chunk_index < 1:
        raise HTTPException(status_code=400, detail="chunk_index must be positive")

    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    chunk_path = save_realtime_chunk(audio, meeting_id, chunk_index, audio_mode)
    result = transcribe_realtime_chunk(
        meeting_id,
        chunk_index,
        chunk_path,
        audio_mode=audio_mode,
        chunk_duration_ms=chunk_duration_ms,
    )
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
    english = _safe_english_from_transcript(meeting.english_transcript_text or "")
    provider = _safe_provider(
        meeting.translation_provider,
        english,
        meeting.translation_fallback_reason,
    )
    return {
        "success": True,
        "meeting_id": meeting_id,
        "chinese": chinese,
        "english": english,
        "provider": provider,
        "translation_provider": provider,
        "translation_status": meeting.translation_status or ("translated" if provider == "gemini" else "fallback" if provider == "mock" else "waiting"),
        "translation_text": english,
        "fallback_reason": meeting.translation_fallback_reason,
        "translation_fallback_reason": meeting.translation_fallback_reason,
        "latency_ms": meeting.translation_latency_ms or 0,
        "updated_at": datetime.utcnow().replace(microsecond=0).isoformat(),
    }


@websocket_router.websocket("/ws/realtime/{meeting_id}")
async def websocket_realtime_subtitles(websocket: WebSocket, meeting_id: str):
    if get_meeting(meeting_id) is None:
        await websocket.close(code=1008)
        return

    await manager.connect(meeting_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(meeting_id, websocket)
    except Exception:
        manager.disconnect(meeting_id, websocket)
