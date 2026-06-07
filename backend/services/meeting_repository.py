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
                transcript_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            SELECT id, name, source_language, target_language, status, created_at, started_at, ended_at, audio_file, audio_duration, transcript_file, transcript_text, transcript_status
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
            SELECT id, name, source_language, target_language, status, created_at, started_at, ended_at, audio_file, audio_duration, transcript_file, transcript_text, transcript_status
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
