from datetime import datetime
from pathlib import Path
import re
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.meeting_repository import get_meeting, update_meeting_audio

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"


def _safe_extension(file_name: str | None, content_type: str | None) -> str:
    suffix = Path(file_name or "").suffix.lower().lstrip(".")
    if suffix in {"webm", "wav"}:
        return suffix
    if content_type == "audio/wav":
        return "wav"
    return "webm"


def _safe_meeting_name(meeting_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", meeting_id)
    return cleaned if cleaned.startswith("meeting_") else f"meeting_{cleaned}"


@router.post("/upload")
def upload_audio(
    meeting_id: str = Form(...),
    audio: UploadFile = File(...),
    duration: int = Form(0),
):
    meeting = get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    extension = _safe_extension(audio.filename, audio.content_type)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{_safe_meeting_name(meeting_id)}_{timestamp}.{extension}"
    file_path = AUDIO_DIR / file_name

    with file_path.open("wb") as output:
        shutil.copyfileobj(audio.file, output)

    audio.file.close()
    update_meeting_audio(meeting_id, str(file_path), max(duration, 0))

    return {
        "success": True,
        "file_name": file_name,
        "duration": max(duration, 0),
    }
