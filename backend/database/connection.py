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
                transcript_status TEXT NOT NULL DEFAULT 'pending'
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
        if "transcript_status" not in columns:
            connection.execute(
                "ALTER TABLE meetings ADD COLUMN transcript_status TEXT NOT NULL DEFAULT 'pending'"
            )
        connection.commit()
