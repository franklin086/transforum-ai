import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from database import connection as db_connection
from database.connection import init_db
from services import meeting_repository
from services import transcription_service


class TranscriptionServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)
        data_dir = self.root / "data"
        self.data_dir_patch = patch.object(db_connection, "DATA_DIR", data_dir)
        self.db_path_patch = patch.object(
            db_connection, "DATABASE_PATH", data_dir / "transforum.db"
        )
        self.data_dir_patch.start()
        self.db_path_patch.start()
        init_db()

    def tearDown(self):
        self.db_path_patch.stop()
        self.data_dir_patch.stop()
        self.temp_dir.cleanup()

    def insert_meeting(self, meeting_id, audio_file=None, transcript_status="pending"):
        with db_connection.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO meetings (
                    id, name, source_language, target_language, status, created_at,
                    audio_file, transcript_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meeting_id,
                    "Test Meeting",
                    "zh",
                    "en",
                    "created",
                    "2026-06-08T00:00:00",
                    audio_file,
                    transcript_status,
                ),
            )
            connection.commit()

    def test_returns_audio_not_found_when_audio_missing(self):
        self.insert_meeting("meeting_missing_audio")

        result = transcription_service.transcribe_meeting_audio(
            "meeting_missing_audio"
        )

        meeting = meeting_repository.get_meeting("meeting_missing_audio")
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "AUDIO_NOT_FOUND",
                "message": "Audio file not found for this meeting.",
                "status": "failed",
            },
        )
        self.assertEqual(meeting.transcript_status, "failed")
        self.assertIsNone(meeting.audio_file)

    def test_returns_model_not_found_without_local_model(self):
        audio_path = self.root / "meeting.webm"
        audio_path.write_bytes(b"audio")
        self.insert_meeting("meeting_missing_model", str(audio_path))

        with patch.object(
            transcription_service,
            "get_whisper_model_status",
            return_value={
                "installed": False,
                "model": "tiny",
                "path": str(self.root / "models"),
                "model_path": str(self.root / "models" / "tiny"),
                "message": "Model not found",
            },
        ):
            result = transcription_service.transcribe_meeting_audio(
                "meeting_missing_model"
            )

        meeting = meeting_repository.get_meeting("meeting_missing_model")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "MODEL_NOT_FOUND")
        self.assertEqual(result["message"], "Local Whisper model not found.")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(meeting.transcript_status, "failed")
        self.assertEqual(meeting.audio_file, str(audio_path))

    def test_saves_txt_and_updates_database(self):
        audio_path = self.root / "meeting.webm"
        audio_path.write_bytes(b"audio")
        model_dir = self.root / "models" / "whisper" / "tiny"
        model_dir.mkdir(parents=True)
        transcripts_dir = self.root / "transcripts"
        self.insert_meeting("meeting_success", str(audio_path))
        captured = {}

        class FakeSegment:
            def __init__(self, text):
                self.text = text

        class FakeWhisperModel:
            def __init__(self, model_path, **kwargs):
                captured["model_path"] = model_path
                captured["kwargs"] = kwargs

            def transcribe(self, audio_file, **kwargs):
                captured["audio_file"] = audio_file
                captured["transcribe_kwargs"] = kwargs
                return [
                    FakeSegment("大家好，"),
                    FakeSegment("欢迎参加测试会议。"),
                ], object()

        fake_module = types.SimpleNamespace(WhisperModel=FakeWhisperModel)

        with patch.dict(sys.modules, {"faster_whisper": fake_module}), patch.object(
            transcription_service, "TRANSCRIPTS_DIR", transcripts_dir
        ), patch.object(
            transcription_service,
            "get_whisper_model_status",
            return_value={
                "installed": True,
                "model": "tiny",
                "path": str(model_dir.parent),
                "model_path": str(model_dir),
                "message": "Ready",
            },
        ), patch.object(
            transcription_service, "get_whisper_model_dir", return_value=model_dir
        ):
            result = transcription_service.transcribe_meeting_audio("meeting_success")

        transcript_path = transcripts_dir / "meeting_success_transcript.txt"
        transcript_file = str(transcript_path).replace("\\", "/")
        meeting = meeting_repository.get_meeting("meeting_success")
        self.assertEqual(
            result,
            {
                "success": True,
                "status": "completed",
                "transcript": "大家好，欢迎参加测试会议。",
                "transcript_file": transcript_file,
            },
        )
        self.assertEqual(
            transcript_path.read_text(encoding="utf-8"),
            "大家好，欢迎参加测试会议。",
        )
        self.assertEqual(meeting.transcript_status, "completed")
        self.assertEqual(meeting.transcript_file, transcript_file)
        self.assertEqual(meeting.transcript_text, "大家好，欢迎参加测试会议。")
        self.assertEqual(captured["model_path"], str(model_dir))
        self.assertTrue(captured["kwargs"]["local_files_only"])
        self.assertEqual(captured["transcribe_kwargs"]["language"], "zh")
        self.assertEqual(captured["transcribe_kwargs"]["task"], "transcribe")


if __name__ == "__main__":
    unittest.main()
