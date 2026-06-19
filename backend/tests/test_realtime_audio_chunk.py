import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from database import connection as db_connection
from database.connection import init_db
from services import meeting_repository
from services import realtime_transcription_service


class RealtimeAudioChunkTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(
            dir="C:\\tmp",
            ignore_cleanup_errors=True,
        )
        self.root = Path(self.temp_dir.name)
        data_dir = self.root / "data"
        self.data_dir_patch = patch.object(db_connection, "DATA_DIR", data_dir)
        self.db_path_patch = patch.object(
            db_connection, "DATABASE_PATH", data_dir / "transforum.db"
        )
        self.chunks_dir_patch = patch.object(
            realtime_transcription_service, "CHUNKS_DIR", data_dir / "chunks"
        )
        self.transcripts_dir_patch = patch.object(
            realtime_transcription_service,
            "TRANSCRIPTS_DIR",
            data_dir / "transcripts",
        )
        self.chunk_error_log_patch = patch.object(
            realtime_transcription_service,
            "CHUNK_ERROR_LOG",
            data_dir / "chunks" / "invalid_chunk_errors.log",
        )
        self.data_dir_patch.start()
        self.db_path_patch.start()
        self.chunks_dir_patch.start()
        self.transcripts_dir_patch.start()
        self.chunk_error_log_patch.start()
        init_db()
        self.insert_meeting("meeting_realtime")

    def tearDown(self):
        self.chunk_error_log_patch.stop()
        self.transcripts_dir_patch.stop()
        self.chunks_dir_patch.stop()
        self.db_path_patch.stop()
        self.data_dir_patch.stop()
        self.temp_dir.cleanup()

    def insert_meeting(self, meeting_id):
        with db_connection.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO meetings (
                    id, name, source_language, target_language, status, created_at,
                    transcript_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meeting_id,
                    "Realtime Meeting",
                    "zh",
                    "en",
                    "created",
                    "2026-06-09T00:00:00",
                    "pending",
                ),
            )
            connection.commit()

    def chunk_path(self, name="meeting_realtime_chunk_1.webm"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def installed_model_patch(self):
        model_dir = self.root / "models" / "whisper" / "tiny"
        model_dir.mkdir(parents=True)
        return patch.multiple(
            realtime_transcription_service,
            get_whisper_model_status=lambda: {
                "installed": True,
                "model": "tiny",
                "path": str(model_dir.parent),
                "model_path": str(model_dir),
                "message": "Ready",
            },
            get_whisper_model_dir=lambda: model_dir,
            _broadcast_chunk_status=lambda *args, **kwargs: None,
            _broadcast_subtitle_update=lambda *args, **kwargs: None,
        )

    def test_empty_chunk_is_skipped(self):
        path = self.chunk_path()
        path.write_bytes(b"")

        with self.installed_model_patch():
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 1, path
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "CHUNK_TOO_SMALL")
        self.assertEqual(result["message"], "Audio chunk is too small, skipped.")
        self.assertIn("CHUNK_TOO_SMALL", realtime_transcription_service.CHUNK_ERROR_LOG.read_text())

    def test_small_chunk_is_skipped(self):
        path = self.chunk_path()
        path.write_bytes(b"a" * 1024)

        with self.installed_model_patch():
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 2, path
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "CHUNK_TOO_SMALL")
        self.assertEqual(result["chunk_index"], 2)

    def test_invalid_webm_chunk_is_skipped(self):
        path = self.chunk_path()
        path.write_bytes(b"not a webm file" * 1024)

        with self.installed_model_patch(), patch.object(
            realtime_transcription_service,
            "_is_audio_decodable",
            return_value=(False, "Invalid data found when processing input"),
        ):
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 3, path
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "INVALID_AUDIO_CHUNK")
        self.assertEqual(result["message"], "Audio chunk is invalid or not decodable.")

    def test_whisper_invalid_data_error_is_protected(self):
        path = self.chunk_path()
        path.write_bytes(b"valid enough" * 1024)

        class FakeWhisperModel:
            def __init__(self, *_args, **_kwargs):
                pass

            def transcribe(self, *_args, **_kwargs):
                raise RuntimeError("Invalid data found when processing input")

        fake_module = types.SimpleNamespace(WhisperModel=FakeWhisperModel)

        with self.installed_model_patch(), patch.object(
            realtime_transcription_service,
            "_is_audio_decodable",
            return_value=(True, ""),
        ), patch.dict(sys.modules, {"faster_whisper": fake_module}):
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 4, path
            )

        meeting = meeting_repository.get_meeting("meeting_realtime")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "INVALID_AUDIO_CHUNK")
        self.assertEqual(meeting.status, "created")
        self.assertIsNone(meeting.realtime_transcript_text)

    def test_valid_chunk_after_invalid_chunk_still_updates_transcript(self):
        invalid_path = self.chunk_path("meeting_realtime_chunk_5.webm")
        valid_path = self.chunk_path("meeting_realtime_chunk_6.webm")
        invalid_path.write_bytes(b"bad chunk" * 2048)
        valid_path.write_bytes(b"valid chunk" * 2048)

        class FakeSegment:
            def __init__(self, text):
                self.text = text

        class FakeWhisperModel:
            def __init__(self, *_args, **_kwargs):
                pass

            def transcribe(self, *_args, **_kwargs):
                return [FakeSegment("hello realtime")], object()

        fake_module = types.SimpleNamespace(WhisperModel=FakeWhisperModel)

        with self.installed_model_patch(), patch.object(
            realtime_transcription_service,
            "_is_audio_decodable",
            side_effect=[(False, "Invalid data"), (True, "")],
        ), patch.dict(sys.modules, {"faster_whisper": fake_module}), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            return_value={
                "success": True,
                "provider": "gemini",
                "source_text": "hello realtime",
                "translated_text": "hello realtime translated",
                "latency_ms": 12,
                "error": None,
            },
        ):
            invalid_result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 5, invalid_path
            )
            valid_result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 6, valid_path
            )

        meeting = meeting_repository.get_meeting("meeting_realtime")
        self.assertFalse(invalid_result["success"])
        self.assertEqual(invalid_result["error"], "INVALID_AUDIO_CHUNK")
        self.assertTrue(valid_result["success"])
        self.assertEqual(valid_result["text"], "hello realtime")
        self.assertIn("hello realtime", meeting.realtime_transcript_text)
        self.assertIn("hello realtime translated", meeting.english_transcript_text)
        self.assertEqual(meeting.translation_provider, "gemini")


if __name__ == "__main__":
    unittest.main()
