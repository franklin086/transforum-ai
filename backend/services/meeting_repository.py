from datetime import datetime
from uuid import uuid4

from database.connection import get_connection, init_db
from models.meeting import Meeting, MeetingCreateRequest


def _row_to_meeting(row) -> Meeting:
    return Meeting(
        id=row["id"],
        name=row["name"],
        source_language=row["source_language"],
        target_language=row["target_language"],
        status=row["status"],
        created_at=row["created_at"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        audio_file=row["audio_file"],
        audio_duration=row["audio_duration"],
        transcript_file=row["transcript_file"],
        transcript_text=row["transcript_text"],
        realtime_transcript_text=row["realtime_transcript_text"],
        english_transcript_text=row["english_transcript_text"],
        translation_provider=row["translation_provider"],
        minutes_summary=row["minutes_summary"],
        minutes_key_points=row["minutes_key_points"],
        minutes_action_items=row["minutes_action_items"],
        minutes_next_steps=row["minutes_next_steps"],
        transcript_status=row["transcript_status"],
    )


def create_meeting(request: MeetingCreateRequest) -> Meeting:
    init_db()
    meeting = Meeting(
        id=f"meeting_{uuid4().hex[:12]}",
        name=request.name.strip(),
        source_language=request.source_language,
        target_language=request.target_language,
        status="created",
        created_at=datetime.utcnow().replace(microsecond=0).isoformat(),
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO meetings (
                id,
                name,
                source_language,
                target_language,
                status,
                created_at,
                started_at,
                ended_at,
                audio_file,
                audio_duration,
                transcript_file,
                transcript_text,
                realtime_transcript_text,
                english_transcript_text,
                translation_provider,
                minutes_summary,
                minutes_key_points,
                minutes_action_items,
                minutes_next_steps,
                transcript_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meeting.id,
                meeting.name,
                meeting.source_language,
                meeting.target_language,
                meeting.status,
                meeting.created_at,
                meeting.started_at,
                meeting.ended_at,
                meeting.audio_file,
                meeting.audio_duration,
                meeting.transcript_file,
                meeting.transcript_text,
                meeting.realtime_transcript_text,
                meeting.english_transcript_text,
                meeting.translation_provider,
                meeting.minutes_summary,
                meeting.minutes_key_points,
                meeting.minutes_action_items,
                meeting.minutes_next_steps,
                meeting.transcript_status,
            ),
        )
        connection.commit()

    return meeting


def get_meeting(meeting_id: str) -> Meeting | None:
    init_db()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, source_language, target_language, status, created_at, started_at, ended_at, audio_file, audio_duration, transcript_file, transcript_text, realtime_transcript_text, english_transcript_text, translation_provider, minutes_summary, minutes_key_points, minutes_action_items, minutes_next_steps, transcript_status
            FROM meetings
            WHERE id = ?
            """,
            (meeting_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_meeting(row)


def list_recent_meetings(limit: int = 50) -> list[Meeting]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, source_language, target_language, status, created_at, started_at, ended_at, audio_file, audio_duration, transcript_file, transcript_text, realtime_transcript_text, english_transcript_text, translation_provider, minutes_summary, minutes_key_points, minutes_action_items, minutes_next_steps, transcript_status
            FROM meetings
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [_row_to_meeting(row) for row in rows]


def update_meeting_audio(
    meeting_id: str, audio_file: str, audio_duration: int
) -> Meeting | None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET audio_file = ?, audio_duration = ?
            WHERE id = ?
            """,
            (audio_file, audio_duration, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)


def update_transcript_status(meeting_id: str, status: str) -> Meeting | None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET transcript_status = ?
            WHERE id = ?
            """,
            (status, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)


def update_meeting_transcript(
    meeting_id: str, transcript_file: str, transcript_text: str, status: str
) -> Meeting | None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET transcript_file = ?, transcript_text = ?, transcript_status = ?
            WHERE id = ?
            """,
            (transcript_file, transcript_text, status, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)


def append_realtime_transcript(meeting_id: str, text: str) -> Meeting | None:
    init_db()
    current = get_meeting(meeting_id)
    if current is None:
        return None

    existing_text = current.realtime_transcript_text or ""
    next_text = f"{existing_text}\n{text}".strip() if existing_text else text.strip()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET realtime_transcript_text = ?
            WHERE id = ?
            """,
            (next_text, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)


def append_english_transcript(
    meeting_id: str, text: str, provider: str = "mock"
) -> Meeting | None:
    init_db()
    current = get_meeting(meeting_id)
    if current is None:
        return None

    existing_text = current.english_transcript_text or ""
    next_text = f"{existing_text}\n{text}".strip() if existing_text else text.strip()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET english_transcript_text = ?,
                translation_provider = ?
            WHERE id = ?
            """,
            (next_text, provider, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)


def end_meeting(meeting_id: str) -> Meeting | None:
    init_db()
    ended_at = datetime.utcnow().replace(microsecond=0).isoformat()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET status = ?, ended_at = ?
            WHERE id = ?
            """,
            ("ended", ended_at, meeting_id),
        )
        connection.commit()

    meeting = get_meeting(meeting_id)
    if meeting is None:
        return None

    archive_meeting(meeting)
    return meeting


def archive_meeting(meeting: Meeting) -> None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO meeting_archive (
                meeting_id,
                meeting_name,
                source_language,
                target_language,
                created_time,
                audio_file,
                transcript_text,
                english_transcript_text,
                realtime_transcript_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(meeting_id) DO UPDATE SET
                meeting_name = excluded.meeting_name,
                source_language = excluded.source_language,
                target_language = excluded.target_language,
                created_time = excluded.created_time,
                audio_file = excluded.audio_file,
                transcript_text = excluded.transcript_text,
                english_transcript_text = excluded.english_transcript_text,
                realtime_transcript_text = excluded.realtime_transcript_text
            """,
            (
                meeting.id,
                meeting.name,
                meeting.source_language,
                meeting.target_language,
                meeting.created_at,
                meeting.audio_file,
                meeting.transcript_text,
                meeting.english_transcript_text,
                meeting.realtime_transcript_text,
            ),
        )
        connection.commit()


def update_meeting_minutes(
    meeting_id: str,
    summary: str,
    key_points: str,
    action_items: str,
    next_steps: str,
) -> Meeting | None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE meetings
            SET minutes_summary = ?,
                minutes_key_points = ?,
                minutes_action_items = ?,
                minutes_next_steps = ?
            WHERE id = ?
            """,
            (summary, key_points, action_items, next_steps, meeting_id),
        )
        connection.commit()

    return get_meeting(meeting_id)
