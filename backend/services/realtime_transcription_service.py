import asyncio
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess

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
from websocket.connection_manager import manager


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"
CHUNK_ERROR_LOG = CHUNKS_DIR / "invalid_chunk_errors.log"
MIN_CHUNK_SIZE_BYTES = 10 * 1024
VALID_CHUNK_EXTENSIONS = {".webm", ".wav"}
ROLLING_WINDOW_CHUNK_COUNT = 3
REALTIME_CHUNK_SECONDS = 8

MODEL_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": "MODEL_NOT_FOUND",
    "message": "Local Whisper model not found.",
}


def _safe_meeting_name(meeting_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", meeting_id)
    return cleaned if cleaned.startswith("meeting_") else f"meeting_{cleaned}"


def _format_chunk_timestamp(chunk_index: int) -> str:
    total_seconds = max(chunk_index, 1) * REALTIME_CHUNK_SECONDS
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def _realtime_transcript_path(meeting_id: str) -> Path:
    return TRANSCRIPTS_DIR / f"{_safe_meeting_name(meeting_id)}_realtime_transcript.txt"


def _broadcast_subtitle_update(
    meeting_id: str,
    chinese: str,
    english: str,
    provider: str,
    latency_ms: int,
) -> None:
    message = {
        "type": "subtitle_update",
        "meeting_id": meeting_id,
        "chinese": chinese,
        "english": english,
        "provider": provider,
        "translation_latency_ms": latency_ms,
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
    }
    try:
        asyncio.run(manager.broadcast(meeting_id, message))
    except Exception as error:
        print(f"WebSocket subtitle broadcast failed: {error}")


def _broadcast_chunk_status(
    meeting_id: str,
    chunk_index: int,
    error_code: str,
    message: str,
) -> None:
    status_message = {
        "type": "chunk_status",
        "meeting_id": meeting_id,
        "chunk_index": chunk_index,
        "error": error_code,
        "message": message,
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
    }
    try:
        asyncio.run(manager.broadcast(meeting_id, status_message))
    except Exception as error:
        print(f"WebSocket chunk status broadcast failed: {error}")


def _record_invalid_chunk(
    meeting_id: str,
    chunk_index: int,
    chunk_path: Path,
    error_code: str,
    message: str,
    detail: str = "",
) -> None:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    log_line = (
        f"{datetime.utcnow().replace(microsecond=0).isoformat()} "
        f"meeting_id={meeting_id} chunk_index={chunk_index} "
        f"error={error_code} file={chunk_path} message={message}"
    )
    if detail:
        log_line = f"{log_line} detail={detail}"
    with CHUNK_ERROR_LOG.open("a", encoding="utf-8") as output:
        output.write(f"{log_line}\n")


def _is_audio_decodable(chunk_path: Path) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=codec_type",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(chunk_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as error:
        return False, str(error)

    if completed.returncode != 0:
        return False, (completed.stderr or completed.stdout).strip()

    return "audio" in completed.stdout.lower(), completed.stderr.strip()


def _chunk_index_from_path(chunk_path: Path) -> int:
    match = re.search(r"_chunk_(\d+)", chunk_path.stem)
    return int(match.group(1)) if match else 0


def _recent_chunk_paths(meeting_id: str) -> list[Path]:
    safe_name = _safe_meeting_name(meeting_id)
    paths = [
        path
        for path in CHUNKS_DIR.glob(f"{safe_name}_chunk_*.webm")
        if path.exists()
        and not path.stem.endswith("_window")
        and path.suffix.lower() in VALID_CHUNK_EXTENSIONS
        and path.stat().st_size >= MIN_CHUNK_SIZE_BYTES
    ]
    return sorted(paths, key=_chunk_index_from_path)[-ROLLING_WINDOW_CHUNK_COUNT:]


def _concat_list_path(meeting_id: str, chunk_index: int) -> Path:
    return CHUNKS_DIR / f"{_safe_meeting_name(meeting_id)}_chunk_{chunk_index}_window.txt"


def _audio_window_path(meeting_id: str, chunk_index: int) -> Path:
    return CHUNKS_DIR / f"{_safe_meeting_name(meeting_id)}_chunk_{chunk_index}_window.webm"


def _write_concat_list(list_path: Path, chunk_paths: list[Path]) -> None:
    def escape_path(path: Path) -> str:
        return path.resolve().as_posix().replace("'", "'\\''")

    lines = [f"file '{escape_path(path)}'" for path in chunk_paths]
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _combine_audio_window(
    meeting_id: str,
    chunk_index: int,
    chunk_paths: list[Path],
) -> tuple[Path | None, str]:
    if len(chunk_paths) < 2:
        return (chunk_paths[0], "") if chunk_paths else (None, "No chunk files available.")

    list_path = _concat_list_path(meeting_id, chunk_index)
    output_path = _audio_window_path(meeting_id, chunk_index)
    _write_concat_list(list_path, chunk_paths)

    try:
        completed = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as error:
        return None, str(error)

    if completed.returncode != 0 or not output_path.exists():
        return None, (completed.stderr or completed.stdout).strip()

    return output_path, ""


def _basic_chunk_error(
    meeting_id: str,
    chunk_index: int,
    chunk_path: Path,
) -> dict | None:
    if not chunk_path.exists():
        return _invalid_chunk_response(
            meeting_id,
            chunk_index,
            chunk_path,
            "CHUNK_NOT_FOUND",
            "Audio chunk file was not found.",
        )

    if chunk_path.suffix.lower() not in VALID_CHUNK_EXTENSIONS:
        return _invalid_chunk_response(
            meeting_id,
            chunk_index,
            chunk_path,
            "INVALID_CHUNK_EXTENSION",
            "Audio chunk extension is not supported.",
        )

    chunk_size = chunk_path.stat().st_size
    if chunk_size < MIN_CHUNK_SIZE_BYTES:
        return _invalid_chunk_response(
            meeting_id,
            chunk_index,
            chunk_path,
            "CHUNK_TOO_SMALL",
            "Audio chunk is too small, skipped.",
            f"size={chunk_size}",
        )

    return None


def _recognition_audio_path(
    meeting_id: str,
    chunk_index: int,
    current_chunk_path: Path,
) -> tuple[Path | None, dict | None]:
    basic_error = _basic_chunk_error(meeting_id, chunk_index, current_chunk_path)
    if basic_error is not None:
        return None, basic_error

    recent_paths = _recent_chunk_paths(meeting_id)
    if current_chunk_path not in recent_paths:
        recent_paths.append(current_chunk_path)
        recent_paths = sorted(recent_paths, key=_chunk_index_from_path)[
            -ROLLING_WINDOW_CHUNK_COUNT:
        ]

    window_path, combine_detail = _combine_audio_window(
        meeting_id,
        chunk_index,
        recent_paths,
    )
    if window_path is not None:
        is_decodable, detail = _is_audio_decodable(window_path)
        if is_decodable:
            return window_path, None
        combine_detail = detail or combine_detail

    current_detail = ""
    if window_path != current_chunk_path:
        current_is_decodable, current_detail = _is_audio_decodable(current_chunk_path)
        if current_is_decodable:
            return current_chunk_path, None

    detail = combine_detail or current_detail
    return None, _invalid_chunk_response(
        meeting_id,
        chunk_index,
        current_chunk_path,
        "INVALID_AUDIO_CHUNK",
        "Audio chunk is invalid or not decodable.",
        detail,
    )


def _invalid_chunk_response(
    meeting_id: str,
    chunk_index: int,
    chunk_path: Path,
    error_code: str,
    message: str,
    detail: str = "",
) -> dict:
    _record_invalid_chunk(
        meeting_id,
        chunk_index,
        chunk_path,
        error_code,
        message,
        detail,
    )
    _broadcast_chunk_status(meeting_id, chunk_index, error_code, message)
    return {
        "success": False,
        "error": error_code,
        "message": message,
        "chunk_index": chunk_index,
    }


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

    recognition_path, invalid_chunk = _recognition_audio_path(
        meeting_id,
        chunk_index,
        chunk_path,
    )
    if invalid_chunk is not None:
        return invalid_chunk

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            str(get_whisper_model_dir()),
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            local_files_only=True,
        )
        segments, _info = model.transcribe(
            str(recognition_path),
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
            _broadcast_subtitle_update(
                meeting_id,
                text,
                english_text,
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
            "recognition_file": str(recognition_path).replace("\\", "/"),
            "transcript_file": str(transcript_path).replace("\\", "/"),
        }
    except Exception as error:
        error_message = str(error)
        if "Invalid data found when processing input" in error_message:
            return _invalid_chunk_response(
                meeting_id,
                chunk_index,
                chunk_path,
                "INVALID_AUDIO_CHUNK",
                "Audio chunk is invalid or not decodable.",
                error_message,
            )
        return {
            "success": False,
            "error": "TRANSCRIPTION_FAILED",
            "message": error_message,
            "chunk_index": chunk_index,
        }
