import asyncio
from collections import deque
from datetime import datetime
import time
import wave
from pathlib import Path
import hashlib
import re
import shutil
import subprocess

from fastapi import UploadFile

from config import (
    GEMINI_API_KEY,
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
VALID_CHUNK_EXTENSIONS = {".webm", ".wav", ".pcm"}
ROLLING_WINDOW_CHUNK_COUNT = 3
REALTIME_CHUNK_SECONDS = 3
RECENT_TEXT_HASH_LIMIT = 12
MEETING_TEXT_STATE = {}

MODEL_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": "MODEL_NOT_FOUND",
    "message": "Local Whisper model not found.",
}


def _safe_meeting_name(meeting_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", meeting_id)
    return cleaned if cleaned.startswith("meeting_") else f"meeting_{cleaned}"


def _format_chunk_timestamp(chunk_index: int, chunk_duration_ms: int | None = None) -> str:
    chunk_seconds = max(1, int((chunk_duration_ms or REALTIME_CHUNK_SECONDS * 1000) / 1000))
    total_seconds = max(chunk_index, 1) * chunk_seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def _realtime_transcript_path(meeting_id: str) -> Path:
    return TRANSCRIPTS_DIR / f"{_safe_meeting_name(meeting_id)}_realtime_transcript.txt"


def _text_without_timestamp(line: str) -> str:
    return re.sub(r"^\[\d{2}:\d{2}:\d{2}\]\s*", "", line or "").strip()


def _latest_text_from_transcript(transcript: str | None) -> str:
    lines = [line.strip() for line in (transcript or "").splitlines() if line.strip()]
    return _text_without_timestamp(lines[-1]) if lines else ""


def _compact_text(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").strip()).lower()


def _clean_recognized_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _is_meaningful_text(text: str) -> bool:
    compact = _compact_text(text)
    meaningful = re.sub(r"[\W_]+", "", compact)
    return bool(meaningful)


def _text_hash(text: str) -> str:
    return hashlib.sha256(_compact_text(text).encode("utf-8")).hexdigest()


def _get_text_state(meeting_id: str, meeting) -> dict:
    state = MEETING_TEXT_STATE.get(meeting_id)
    latest_transcript_text = _latest_text_from_transcript(
        getattr(meeting, "realtime_transcript_text", None)
    )
    if state is None:
        state = {
            "last_transcript_text": latest_transcript_text,
            "last_emitted_text": latest_transcript_text,
            "recent_text_hashes": deque(maxlen=RECENT_TEXT_HASH_LIMIT),
        }
        if latest_transcript_text:
            state["recent_text_hashes"].append(_text_hash(latest_transcript_text))
        MEETING_TEXT_STATE[meeting_id] = state
    elif latest_transcript_text and not state.get("last_emitted_text"):
        state["last_transcript_text"] = latest_transcript_text
        state["last_emitted_text"] = latest_transcript_text
        state["recent_text_hashes"].append(_text_hash(latest_transcript_text))
    return state


def _strip_leading_punctuation(text: str) -> str:
    return re.sub(r"^[^\w]+", "", text or "").strip()


def _derive_new_transcript_text(meeting_id: str, meeting, recognized_text: str) -> str:
    candidate = _clean_recognized_text(recognized_text)
    if not _is_meaningful_text(candidate):
        return ""

    state = _get_text_state(meeting_id, meeting)
    last_full = _clean_recognized_text(state.get("last_transcript_text", ""))
    last_emitted = _clean_recognized_text(state.get("last_emitted_text", ""))
    candidate_compact = _compact_text(candidate)
    last_full_compact = _compact_text(last_full)
    last_emitted_compact = _compact_text(last_emitted)

    new_text = candidate
    if last_full_compact and candidate_compact == last_full_compact:
        new_text = ""
    elif last_full_compact and candidate_compact.startswith(last_full_compact):
        new_text = _strip_leading_punctuation(candidate[len(last_full):])
    elif last_full_compact and last_full_compact.startswith(candidate_compact):
        new_text = ""
    elif last_emitted_compact and candidate_compact == last_emitted_compact:
        new_text = ""
    elif last_emitted_compact and last_emitted_compact in candidate_compact:
        repeated_prefix = candidate.find(last_emitted)
        if repeated_prefix >= 0:
            suffix_start = repeated_prefix + len(last_emitted)
            suffix = _strip_leading_punctuation(candidate[suffix_start:])
            new_text = suffix or ""

    if not _is_meaningful_text(new_text):
        state["last_transcript_text"] = candidate
        return ""

    emitted_hash = _text_hash(new_text)
    if emitted_hash in state["recent_text_hashes"]:
        state["last_transcript_text"] = candidate
        return ""

    state["last_transcript_text"] = candidate
    state["last_emitted_text"] = new_text
    state["recent_text_hashes"].append(emitted_hash)
    return new_text


def _waiting_translation_result() -> dict:
    return {
        "success": True,
        "provider": "waiting",
        "translation_status": "waiting",
        "source_text": "",
        "translated_text": "",
        "latency_ms": 0,
        "error": None,
        "fallback_reason": None,
        "gemini_configured": bool(GEMINI_API_KEY),
    }


def _print_realtime_trace(
    meeting_id: str,
    chunk_index: int,
    caption_text: str,
    accepted_caption: bool,
    translation_attempted: bool,
    translation_provider: str,
    translation_status: str,
    fallback_reason: str | None,
    saved_to_minutes: bool,
    audio_mode: str = "webm",
    chunk_duration_ms: int = REALTIME_CHUNK_SECONDS * 1000,
    audio_size_bytes: int = 0,
    asr_latency_ms: int = 0,
    translation_latency_ms: int = 0,
    end_to_end_latency_ms: int = 0,
) -> None:
    trace = {
        "meeting_id": meeting_id,
        "chunk_index": chunk_index,
        "audio_mode": audio_mode,
        "chunk_duration_ms": chunk_duration_ms,
        "audio_size_bytes": audio_size_bytes,
        "asr_latency_ms": asr_latency_ms,
        "caption_text": caption_text,
        "accepted_caption": str(accepted_caption).lower(),
        "translation_attempted": str(translation_attempted).lower(),
        "translation_provider": translation_provider,
        "translation_status": translation_status,
        "translation_latency_ms": translation_latency_ms,
        "end_to_end_latency_ms": end_to_end_latency_ms,
        "fallback_reason": fallback_reason or "",
        "saved_to_minutes": str(saved_to_minutes).lower(),
    }
    for key, value in trace.items():
        print(f"[REALTIME_TRACE] {key}={value}", flush=True)


def _broadcast_subtitle_update(
    meeting_id: str,
    chinese: str,
    english: str,
    provider: str,
    latency_ms: int,
    fallback_reason: str | None = None,
    translation_status: str = "waiting",
    audio_mode: str = "webm",
    chunk_duration_ms: int = REALTIME_CHUNK_SECONDS * 1000,
    asr_latency_ms: int = 0,
    end_to_end_latency_ms: int = 0,
) -> None:
    message = {
        "type": "subtitle_update",
        "meeting_id": meeting_id,
        "chinese": chinese,
        "english": english,
        "provider": provider,
        "translation_provider": provider,
        "translation_status": translation_status,
        "translation_text": english,
        "translation_latency_ms": latency_ms,
        "translation_fallback_reason": fallback_reason,
        "fallback_reason": fallback_reason,
        "gemini_configured": bool(GEMINI_API_KEY),
        "audio_mode": audio_mode,
        "chunk_duration_ms": chunk_duration_ms,
        "asr_latency_ms": asr_latency_ms,
        "end_to_end_latency_ms": end_to_end_latency_ms,
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
    audio_mode: str = "webm",
) -> tuple[Path | None, dict | None]:
    basic_error = _basic_chunk_error(meeting_id, chunk_index, current_chunk_path)
    if basic_error is not None:
        return None, basic_error

    normalized_mode = (audio_mode or "webm").lower()
    if normalized_mode in {"pcm_wav", "wav", "pcm"} or current_chunk_path.suffix.lower() in {".wav", ".pcm"}:
        recognition_path = _wrap_pcm_as_wav(current_chunk_path) if current_chunk_path.suffix.lower() == ".pcm" else current_chunk_path
        is_decodable, detail = _is_audio_decodable(recognition_path)
        if is_decodable:
            return recognition_path, None
        return None, _invalid_chunk_response(
            meeting_id,
            chunk_index,
            current_chunk_path,
            "INVALID_AUDIO_CHUNK",
            "Audio chunk is invalid or not decodable.",
            detail,
        )

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



def _audio_extension(upload: UploadFile, audio_mode: str) -> str:
    filename = (upload.filename or "").lower()
    content_type = (upload.content_type or "").lower()
    normalized_mode = (audio_mode or "webm").lower()
    if normalized_mode in {"pcm_wav", "wav"} or "wav" in content_type or filename.endswith(".wav"):
        return ".wav"
    if normalized_mode == "pcm" or "pcm" in content_type or filename.endswith(".pcm"):
        return ".pcm"
    return ".webm"


def _wrap_pcm_as_wav(pcm_path: Path) -> Path:
    wav_path = pcm_path.with_suffix(".wav")
    with pcm_path.open("rb") as source, wave.open(str(wav_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(source.read())
    return wav_path

def save_realtime_chunk(
    audio: UploadFile,
    meeting_id: str,
    chunk_index: int,
    audio_mode: str = "webm",
) -> Path:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    extension = _audio_extension(audio, audio_mode)
    chunk_path = CHUNKS_DIR / f"{_safe_meeting_name(meeting_id)}_chunk_{chunk_index}{extension}"

    with chunk_path.open("wb") as output:
        shutil.copyfileobj(audio.file, output)

    audio.file.close()
    return chunk_path


def transcribe_realtime_chunk(
    meeting_id: str,
    chunk_index: int,
    chunk_path: Path,
    audio_mode: str = "webm",
    chunk_duration_ms: int = REALTIME_CHUNK_SECONDS * 1000,
) -> dict:
    request_started = time.perf_counter()
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

    audio_size_bytes = chunk_path.stat().st_size if chunk_path.exists() else 0
    recognition_path, invalid_chunk = _recognition_audio_path(
        meeting_id,
        chunk_index,
        chunk_path,
        audio_mode,
    )
    if invalid_chunk is not None:
        end_to_end_latency_ms = int((time.perf_counter() - request_started) * 1000)
        invalid_chunk.update(
            {
                "audio_mode": audio_mode,
                "chunk_duration_ms": chunk_duration_ms,
                "audio_size_bytes": audio_size_bytes,
                "asr_latency_ms": 0,
                "translation_latency_ms": 0,
                "end_to_end_latency_ms": end_to_end_latency_ms,
                "fallback_reason": invalid_chunk.get("error"),
            }
        )
        _print_realtime_trace(
            meeting_id,
            chunk_index,
            "",
            False,
            False,
            "waiting",
            "waiting",
            invalid_chunk.get("error"),
            False,
            audio_mode,
            chunk_duration_ms,
            audio_size_bytes,
            0,
            0,
            end_to_end_latency_ms,
        )
        return invalid_chunk

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            str(get_whisper_model_dir()),
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            local_files_only=True,
        )
        asr_started = time.perf_counter()
        segments, _info = model.transcribe(
            str(recognition_path),
            language="zh",
            task="transcribe",
            vad_filter=False,
        )
        recognized_text = "".join(segment.text for segment in segments).strip()
        asr_latency_ms = int((time.perf_counter() - asr_started) * 1000)
        text = _derive_new_transcript_text(meeting_id, meeting, recognized_text)
        transcript_path = _realtime_transcript_path(meeting_id)

        accepted_caption = bool(text)
        translation_attempted = False
        saved_to_minutes = False
        if text:
            timestamp = _format_chunk_timestamp(chunk_index, chunk_duration_ms)
            transcript_line = f"{timestamp} {text}"
            translation_attempted = True
            translation_result = translate_zh_to_en(text)
            english_text = translation_result.get("translated_text", "")
            translation_provider = translation_result.get("provider", "mock")
            translation_latency_ms = int(translation_result.get("latency_ms", 0))
            translation_status = translation_result.get("translation_status") or (
                "translated" if translation_provider == "gemini" else "fallback"
            )
            translation_fallback_reason = translation_result.get("fallback_reason")
            if not translation_fallback_reason and translation_provider == "mock":
                translation_fallback_reason = translation_result.get("error")
            if translation_provider == "waiting":
                translation_provider = "error"
                translation_status = "error"
                translation_fallback_reason = (
                    translation_fallback_reason
                    or "TRANSLATION_PROVIDER_WAITING_AFTER_ACCEPTED_CAPTION"
                )
            english_line = f"{timestamp} {english_text}" if english_text else ""
            TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            with transcript_path.open("a", encoding="utf-8") as output:
                output.write(f"{transcript_line}\n")
            saved_caption = append_realtime_transcript(meeting_id, transcript_line) is not None
            saved_translation = append_english_transcript(
                meeting_id,
                english_line,
                translation_provider,
                translation_latency_ms,
                translation_status,
                translation_fallback_reason,
            ) is not None
            saved_to_minutes = saved_caption and saved_translation
            _broadcast_subtitle_update(
                meeting_id,
                text,
                english_text,
                translation_provider,
                translation_latency_ms,
                translation_fallback_reason,
                translation_status,
                audio_mode,
                chunk_duration_ms,
                asr_latency_ms,
                int((time.perf_counter() - request_started) * 1000),
            )
        else:
            english_text = ""
            translation_result = _waiting_translation_result()
            translation_provider = "waiting"
            translation_latency_ms = 0
            translation_status = "waiting"
            translation_fallback_reason = None
            _broadcast_chunk_status(
                meeting_id,
                chunk_index,
                "WAITING_FOR_VALID_SPEECH",
                "Waiting for valid speech input...",
            )

        end_to_end_latency_ms = int((time.perf_counter() - request_started) * 1000)
        _print_realtime_trace(
            meeting_id,
            chunk_index,
            text,
            accepted_caption,
            translation_attempted,
            translation_provider,
            translation_status,
            translation_fallback_reason,
            saved_to_minutes,
            audio_mode,
            chunk_duration_ms,
            audio_size_bytes,
            asr_latency_ms,
            translation_latency_ms,
            end_to_end_latency_ms,
        )

        return {
            "success": True,
            "text": text,
            "caption_text": text,
            "accepted_caption": accepted_caption,
            "translation_attempted": translation_attempted,
            "recognized_text": recognized_text,
            "english_text": english_text,
            "translation_text": english_text,
            "translation_provider": translation_provider,
            "translation_status": translation_status,
            "translation_latency_ms": translation_latency_ms,
            "latency_ms": translation_latency_ms,
            "translation_fallback_reason": translation_fallback_reason,
            "fallback_reason": translation_fallback_reason,
            "saved_to_minutes": saved_to_minutes,
            "audio_mode": audio_mode,
            "chunk_duration_ms": chunk_duration_ms,
            "audio_size_bytes": audio_size_bytes,
            "asr_latency_ms": asr_latency_ms,
            "end_to_end_latency_ms": end_to_end_latency_ms,
            "gemini_configured": bool(GEMINI_API_KEY),
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
