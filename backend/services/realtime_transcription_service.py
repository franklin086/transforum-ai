from pathlib import Path
import re
import shutil

from fastapi import UploadFile

from config import (
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    get_whisper_model_dir,
    get_whisper_model_status,
)
from services.meeting_repository import (
    append_english_transcript,
    append_realtime_transcript,
    get_meeting,
)
from services.translation_service import translate_zh_to_en


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"

MODEL_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": "MODEL_NOT_FOUND",
    "message": "Local Whisper model not found.",
}


def _safe_meeting_name(meeting_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", meeting_id)
    return cleaned if cleaned.startswith("meeting_") else f"meeting_{cleaned}"


def _format_chunk_timestamp(chunk_index: int) -> str:
    total_seconds = max(chunk_index, 1) * 3
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def _realtime_transcript_path(meeting_id: str) -> Path:
    return TRANSCRIPTS_DIR / f"{_safe_meeting_name(meeting_id)}_realtime_transcript.txt"


def save_realtime_chunk(audio: UploadFile, meeting_id: str, chunk_index: int) -> Path:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    chunk_path = (
        CHUNKS_DIR / f"{_safe_meeting_name(meeting_id)}_chunk_{chunk_index}.webm"
    )

    with chunk_path.open("wb") as output:
        shutil.copyfileobj(audio.file, output)

    audio.file.close()
    return chunk_path


def transcribe_realtime_chunk(
    meeting_id: str,
    chunk_index: int,
    chunk_path: Path,
) -> dict:
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return {
            "success": False,
            "error": "MEETING_NOT_FOUND",
            "message": "Meeting not found.",
        }

    model_status = get_whisper_model_status()
    if not model_status["installed"]:
        return MODEL_NOT_FOUND_RESPONSE

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            str(get_whisper_model_dir()),
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            local_files_only=True,
        )
        segments, _info = model.transcribe(
            str(chunk_path),
            language="zh",
            task="transcribe",
            vad_filter=False,
        )
        text = "".join(segment.text for segment in segments).strip()

        if text:
            timestamp = _format_chunk_timestamp(chunk_index)
            transcript_line = f"{timestamp} {text}"
            translation_result = translate_zh_to_en(text)
            english_text = translation_result.get("translated_text", "")
            translation_provider = translation_result.get("provider", "mock")
            translation_latency_ms = int(translation_result.get("latency_ms", 0))
            english_line = f"{timestamp} {english_text}" if english_text else ""
            TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            transcript_path = _realtime_transcript_path(meeting_id)
            with transcript_path.open("a", encoding="utf-8") as output:
                output.write(f"{transcript_line}\n")
            append_realtime_transcript(meeting_id, transcript_line)
            if english_line:
                append_english_transcript(
                    meeting_id,
                    english_line,
                    translation_provider,
                    translation_latency_ms,
                )
        else:
            english_text = ""
            translation_result = {
                "success": True,
                "provider": "mock",
                "source_text": "",
                "translated_text": "",
                "latency_ms": 0,
                "error": None,
            }
            translation_provider = "mock"
            translation_latency_ms = 0
            transcript_path = _realtime_transcript_path(meeting_id)

        return {
            "success": True,
            "text": text,
            "english_text": english_text,
            "translation_provider": translation_provider,
            "translation_latency_ms": translation_latency_ms,
            "translation": translation_result,
            "chunk_index": chunk_index,
            "chunk_file": str(chunk_path).replace("\\", "/"),
            "transcript_file": str(transcript_path).replace("\\", "/"),
        }
    except Exception as error:
        return {
            "success": False,
            "error": "TRANSCRIPTION_FAILED",
            "message": str(error),
            "chunk_index": chunk_index,
        }
