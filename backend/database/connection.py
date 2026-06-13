from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "transforum.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                source_language TEXT NOT NULL DEFAULT 'zh',
                target_language TEXT NOT NULL DEFAULT 'en',
                status TEXT NOT NULL DEFAULT 'created',
                created_at TEXT NOT NULL,
                started_at TEXT,
                ended_at TEXT,
                audio_file TEXT,
                audio_duration INTEGER,
                transcript_file TEXT,
                transcript_text TEXT,
                realtime_transcript_text TEXT,
                english_transcript_text TEXT,
                translation_provider TEXT NOT NULL DEFAULT 'mock',
                minutes_summary TEXT,
                minutes_key_points TEXT,
                minutes_action_items TEXT,
                minutes_next_steps TEXT,
                transcript_status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS meeting_archive (
                meeting_id TEXT PRIMARY KEY,
                meeting_name TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                created_time TEXT NOT NULL,
                audio_file TEXT,
                transcript_text TEXT,
                english_transcript_text TEXT,
                realtime_transcript_text TEXT
            )
            """
        )
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(meetings)").fetchall()
        }
        if "audio_file" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN audio_file TEXT")
        if "audio_duration" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN audio_duration INTEGER")
        if "transcript_file" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN transcript_file TEXT")
        if "transcript_text" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN transcript_text TEXT")
        if "realtime_transcript_text" not in columns:
            connection.execute(
                "ALTER TABLE meetings ADD COLUMN realtime_transcript_text TEXT"
            )
        if "english_transcript_text" not in columns:
            connection.execute(
                "ALTER TABLE meetings ADD COLUMN english_transcript_text TEXT"
            )
        if "translation_provider" not in columns:
            connection.execute(
                "ALTER TABLE meetings ADD COLUMN translation_provider TEXT NOT NULL DEFAULT 'mock'"
            )
        if "minutes_summary" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN minutes_summary TEXT")
        if "minutes_key_points" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN minutes_key_points TEXT")
        if "minutes_action_items" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN minutes_action_items TEXT")
        if "minutes_next_steps" not in columns:
            connection.execute("ALTER TABLE meetings ADD COLUMN minutes_next_steps TEXT")
        if "transcript_status" not in columns:
            connection.execute(
                "ALTER TABLE meetings ADD COLUMN transcript_status TEXT NOT NULL DEFAULT 'pending'"
            )
        connection.commit()
