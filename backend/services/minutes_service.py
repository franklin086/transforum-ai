from models.meeting import Meeting
from services.meeting_repository import append_english_transcript, get_meeting, update_meeting_minutes
from services.translation_service import translate_zh_to_en


def _clean_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.replace("\r\n", "\n").split("\n")
        if line.strip() and not line.strip().lower().startswith("[" + "mock en" + "]")
    ]


def _split_sentences(text: str) -> list[str]:
    normalized = (
        text.replace("\r\n", "\n")
        .replace("。", "。\n")
        .replace("；", "；\n")
        .replace(";", ";\n")
        .replace(".", ".\n")
    )
    return _clean_lines(normalized)



def _strip_timestamp(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("[") and "]" in stripped[:12]:
        return stripped.split("]", 1)[1].strip()
    return stripped


def _caption_text_for_translation(realtime_transcript: str) -> str:
    return "\n".join(
        _strip_timestamp(line)
        for line in _clean_lines(realtime_transcript)
        if _strip_timestamp(line)
    ).strip()

def _needs_translation_backfill(meeting: Meeting) -> bool:
    has_caption = bool((meeting.realtime_transcript_text or "").strip())
    has_english = bool(_clean_lines(meeting.english_transcript_text or ""))
    provider_waiting = (meeting.translation_provider or "waiting") == "waiting"
    return has_caption and (not has_english or provider_waiting)


def _backfill_missing_translation(meeting: Meeting) -> Meeting:
    if not _needs_translation_backfill(meeting):
        return meeting

    caption_text = _caption_text_for_translation(meeting.realtime_transcript_text or "")
    if not caption_text:
        return meeting

    translation_result = translate_zh_to_en(caption_text)
    provider = translation_result.get("provider", "mock")
    status = translation_result.get("translation_status") or (
        "translated" if provider == "gemini" else "fallback"
    )
    fallback_reason = translation_result.get("fallback_reason")
    if not fallback_reason and provider == "mock":
        fallback_reason = translation_result.get("error")
    if provider == "waiting":
        provider = "error"
        status = "error"
        fallback_reason = fallback_reason or "MINUTES_TRANSLATION_BACKFILL_RETURNED_WAITING"

    updated = append_english_transcript(
        meeting.id,
        translation_result.get("translated_text", ""),
        provider,
        int(translation_result.get("latency_ms", 0)),
        status,
        fallback_reason,
    )
    print(
        "[REALTIME_TRACE] minutes_backfill="
        f"meeting_id={meeting.id} provider={provider} status={status} "
        f"fallback_reason={fallback_reason or ''} saved={str(updated is not None).lower()}",
        flush=True,
    )
    return updated or meeting

def _source_text_for_minutes(meeting_id: str) -> str:
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return ""

    parts = [
        meeting.realtime_transcript_text or "",
        meeting.transcript_text or "",
        meeting.english_transcript_text or "",
    ]
    return "\n".join(part for part in parts if part.strip())


def generate_minutes(meeting_id: str) -> dict | None:
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return None

    meeting = _backfill_missing_translation(meeting)
    source_text = _source_text_for_minutes(meeting_id)
    sentences = _split_sentences(source_text)

    if sentences:
        summary = (
            f"This meeting archive for {meeting.name} was generated from the "
            "available transcript, realtime captions, and English translation."
        )
        key_points = sentences[:3]
    else:
        summary = (
            f"Meeting {meeting.name} has ended, but no usable transcript or "
            "realtime caption content is available yet."
        )
        key_points = ["No extractable key points yet."]

    action_items = [
        "Review the archived Chinese captions and English translation.",
        "Add owners and due dates after confirming the meeting content.",
    ]
    next_steps = [
        "Verify the meeting archive before sharing it.",
        "Use the field test notes to improve realtime recognition and minutes quality.",
    ]

    update_meeting_minutes(
        meeting_id,
        summary,
        "\n".join(key_points),
        "\n".join(action_items),
        "\n".join(next_steps),
    )

    return {
        "success": True,
        "meeting_id": meeting_id,
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
        "next_steps": next_steps,
    }
