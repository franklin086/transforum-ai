from services.meeting_repository import get_meeting, update_meeting_minutes


def _clean_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.replace("\r\n", "\n").split("\n")
        if line.strip()
    ]


def _split_sentences(text: str) -> list[str]:
    normalized = (
        text.replace("\r\n", "\n")
        .replace("。", "。\n")
        .replace("！", "！\n")
        .replace("？", "？\n")
        .replace(".", ".\n")
    )
    return _clean_lines(normalized)


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

    source_text = _source_text_for_minutes(meeting_id)
    sentences = _split_sentences(source_text)

    if sentences:
        summary = f"本次会议围绕 {meeting.name} 展开，系统已归档会议音频、实时字幕和逐字稿内容。"
        key_points = sentences[:3]
    else:
        summary = f"本次会议 {meeting.name} 已结束，但暂未发现可用于生成纪要的转写内容。"
        key_points = ["暂无可提取的核心观点。"]

    action_items = [
        "确认会议字幕和逐字稿内容是否完整。",
        "根据会议内容补充责任人和截止时间。",
    ]
    next_steps = [
        "复核会议归档内容。",
        "在后续版本中接入更高质量的 AI 纪要生成。",
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
