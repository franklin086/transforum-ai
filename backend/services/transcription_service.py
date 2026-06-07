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
MODEL_NOT_FOUND_MESSAGE = "MODEL_NOT_FOUND: Whisper model not found in local path."


def _transcript_file_name(meeting_id: str) -> str:
    safe_id = "".join(
        character if character.isalnum() or character in {"_", "-"} else "_"
        for character in meeting_id
    )
    if not safe_id.startswith("meeting_"):
        safe_id = f"meeting_{safe_id}"
    return f"{safe_id}_transcript.txt"


def transcribe_meeting_audio(meeting_id: str) -> None:
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return

    if not meeting.audio_file:
        update_transcript_status(meeting_id, "failed")
        return

    audio_path = Path(meeting.audio_file)
    if not audio_path.exists():
        update_transcript_status(meeting_id, "failed")
        return

    update_transcript_status(meeting_id, "processing")

    try:
        from faster_whisper import WhisperModel

        model_status = get_whisper_model_status()
        if not model_status["installed"]:
            update_meeting_transcript(meeting_id, "", MODEL_NOT_FOUND_MESSAGE, "failed")
            return

        model = WhisperModel(
            str(get_whisper_model_dir()),
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            local_files_only=True,
        )
        segments, _info = model.transcribe(
            str(audio_path),
            language="zh",
            vad_filter=False,
        )
        transcript_text = "".join(segment.text for segment in segments).strip()

        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        transcript_path = TRANSCRIPTS_DIR / _transcript_file_name(meeting_id)
        transcript_path.write_text(transcript_text, encoding="utf-8")

        update_meeting_transcript(
            meeting_id,
            str(transcript_path),
            transcript_text,
            "completed",
        )
    except Exception as error:
        update_meeting_transcript(meeting_id, "", str(error), "failed")
