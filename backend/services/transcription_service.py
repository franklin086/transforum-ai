from pathlib import Path

from config import (
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    get_whisper_model_dir,
    get_whisper_model_status,
)
from services.meeting_repository import (
    get_meeting,
    update_meeting_transcript,
    update_transcript_status,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"
AUDIO_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": "AUDIO_NOT_FOUND",
    "message": "Audio file not found for this meeting.",
    "status": "failed",
}
MODEL_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": "MODEL_NOT_FOUND",
    "message": "Local Whisper model not found.",
    "status": "failed",
}


def _transcript_file_name(meeting_id: str) -> str:
    safe_id = "".join(
        character if character.isalnum() or character in {"_", "-"} else "_"
        for character in meeting_id
    )
    if not safe_id.startswith("meeting_"):
        safe_id = f"meeting_{safe_id}"
    return f"{safe_id}_transcript.txt"


def transcribe_meeting_audio(meeting_id: str) -> dict:
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return {
            "success": False,
            "error": "MEETING_NOT_FOUND",
            "message": "Meeting not found.",
            "status": "failed",
        }

    if not meeting.audio_file:
        update_transcript_status(meeting_id, "failed")
        return AUDIO_NOT_FOUND_RESPONSE

    audio_path = Path(meeting.audio_file)
    if not audio_path.exists():
        update_transcript_status(meeting_id, "failed")
        return AUDIO_NOT_FOUND_RESPONSE

    update_transcript_status(meeting_id, "processing")

    try:
        model_status = get_whisper_model_status()
        if not model_status["installed"]:
            update_transcript_status(meeting_id, "failed")
            return MODEL_NOT_FOUND_RESPONSE

        from faster_whisper import WhisperModel

        model = WhisperModel(
            str(get_whisper_model_dir()),
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            local_files_only=True,
        )
        segments, _info = model.transcribe(
            str(audio_path),
            language="zh",
            task="transcribe",
            vad_filter=False,
        )
        transcript_text = "".join(segment.text for segment in segments).strip()

        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        transcript_path = TRANSCRIPTS_DIR / _transcript_file_name(meeting_id)
        transcript_path.write_text(transcript_text, encoding="utf-8")
        transcript_file = str(transcript_path).replace("\\", "/")

        update_meeting_transcript(
            meeting_id,
            transcript_file,
            transcript_text,
            "completed",
        )
        return {
            "success": True,
            "status": "completed",
            "transcript": transcript_text,
            "transcript_file": transcript_file,
        }
    except Exception as error:
        update_transcript_status(meeting_id, "failed")
        return {
            "success": False,
            "error": "TRANSCRIPTION_FAILED",
            "message": str(error),
            "status": "failed",
        }
