import sys
import shutil
import types
import unittest
from uuid import uuid4
from pathlib import Path
from unittest.mock import patch

from database import connection as db_connection
from database.connection import init_db
from services import meeting_repository
from services import realtime_transcription_service


class RealtimeAudioChunkTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1] / ".test-tmp" / uuid4().hex
        self.root.mkdir(parents=True, exist_ok=True)
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
        realtime_transcription_service.MEETING_TEXT_STATE.clear()
        init_db()
        self.insert_meeting("meeting_realtime")

    def tearDown(self):
        self.chunk_error_log_patch.stop()
        self.transcripts_dir_patch.stop()
        self.chunks_dir_patch.stop()
        self.db_path_patch.stop()
        self.data_dir_patch.stop()
        shutil.rmtree(self.root, ignore_errors=True)

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

    def fake_whisper_module(self, texts):
        class FakeSegment:
            def __init__(self, text):
                self.text = text

        class FakeWhisperModel:
            queued_texts = list(texts)

            def __init__(self, *_args, **_kwargs):
                pass

            def transcribe(self, *_args, **_kwargs):
                text = self.queued_texts.pop(0) if self.queued_texts else ""
                return [FakeSegment(text)], object()

        return types.SimpleNamespace(WhisperModel=FakeWhisperModel)

    def bypass_audio_validation_patch(self):
        return patch.object(
            realtime_transcription_service,
            "_recognition_audio_path",
            side_effect=lambda _meeting_id, _chunk_index, chunk_path: (chunk_path, None),
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


    def test_uses_recent_three_chunk_window_for_recognition(self):
        paths = [
            realtime_transcription_service.CHUNKS_DIR / f"meeting_realtime_chunk_{index}.webm"
            for index in (7, 8, 9)
        ]
        realtime_transcription_service.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        for path in paths:
            path.write_bytes(b"valid chunk" * 2048)
        window_path = realtime_transcription_service.CHUNKS_DIR / "meeting_realtime_chunk_9_window.webm"
        window_path.parent.mkdir(parents=True, exist_ok=True)
        window_path.write_bytes(b"combined audio")
        captured = {}

        class FakeSegment:
            def __init__(self, text):
                self.text = text

        class FakeWhisperModel:
            def __init__(self, *_args, **_kwargs):
                pass

            def transcribe(self, audio_file, **_kwargs):
                captured["audio_file"] = audio_file
                return [FakeSegment("rolling window text")], object()

        fake_module = types.SimpleNamespace(WhisperModel=FakeWhisperModel)

        with self.installed_model_patch(), patch.object(
            realtime_transcription_service,
            "_combine_audio_window",
            return_value=(window_path, ""),
        ) as combine_mock, patch.object(
            realtime_transcription_service,
            "_is_audio_decodable",
            return_value=(True, ""),
        ), patch.dict(sys.modules, {"faster_whisper": fake_module}), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            return_value={
                "success": True,
                "provider": "gemini",
                "source_text": "rolling window text",
                "translated_text": "rolling window translated",
                "latency_ms": 8,
                "error": None,
            },
        ):
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 9, paths[-1]
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["recognition_file"], str(window_path).replace("\\", "/"))
        self.assertEqual(captured["audio_file"], str(window_path))
        combined_paths = combine_mock.call_args.args[2]
        self.assertEqual([path.name for path in combined_paths], [path.name for path in paths])

    def test_empty_whisper_text_does_not_trigger_translation(self):
        path = self.chunk_path("meeting_realtime_chunk_10.webm")
        path.write_bytes(b"valid chunk" * 2048)
        fake_module = self.fake_whisper_module(["   "])

        with self.installed_model_patch(), self.bypass_audio_validation_patch(), patch.dict(
            sys.modules, {"faster_whisper": fake_module}
        ), patch.object(realtime_transcription_service, "translate_zh_to_en") as translate_mock:
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 10, path
            )

        meeting = meeting_repository.get_meeting("meeting_realtime")
        self.assertTrue(result["success"])
        self.assertEqual(result["text"], "")
        self.assertEqual(result["translation_provider"], "waiting")
        translate_mock.assert_not_called()
        self.assertIsNone(meeting.realtime_transcript_text)
        self.assertIsNone(meeting.english_transcript_text)

    def test_duplicate_whisper_text_is_not_written_twice(self):
        paths = [
            self.chunk_path("meeting_realtime_chunk_11.webm"),
            self.chunk_path("meeting_realtime_chunk_12.webm"),
        ]
        for path in paths:
            path.write_bytes(b"valid chunk" * 2048)
        fake_module = self.fake_whisper_module(["hello realtime", "hello realtime"])

        with self.installed_model_patch(), self.bypass_audio_validation_patch(), patch.dict(
            sys.modules, {"faster_whisper": fake_module}
        ), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            return_value={
                "success": True,
                "provider": "gemini",
                "source_text": "hello realtime",
                "translated_text": "hello realtime translated",
                "latency_ms": 15,
                "error": None,
                "fallback_reason": None,
            },
        ) as translate_mock:
            first = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 11, paths[0]
            )
            second = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 12, paths[1]
            )

        meeting = meeting_repository.get_meeting("meeting_realtime")
        self.assertEqual(first["text"], "hello realtime")
        self.assertEqual(second["text"], "")
        self.assertEqual(second["translation_provider"], "waiting")
        self.assertEqual(translate_mock.call_count, 1)
        self.assertEqual(meeting.realtime_transcript_text.count("hello realtime"), 1)

    def test_rolling_window_longer_text_only_appends_new_suffix(self):
        paths = [
            self.chunk_path("meeting_realtime_chunk_13.webm"),
            self.chunk_path("meeting_realtime_chunk_14.webm"),
        ]
        for path in paths:
            path.write_bytes(b"valid chunk" * 2048)
        fake_module = self.fake_whisper_module(["hello", "hello welcome"])

        with self.installed_model_patch(), self.bypass_audio_validation_patch(), patch.dict(
            sys.modules, {"faster_whisper": fake_module}
        ), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            side_effect=[
                {
                    "success": True,
                    "provider": "gemini",
                    "source_text": "hello",
                    "translated_text": "hello translated",
                    "latency_ms": 8,
                    "error": None,
                    "fallback_reason": None,
                },
                {
                    "success": True,
                    "provider": "gemini",
                    "source_text": "welcome",
                    "translated_text": "welcome translated",
                    "latency_ms": 9,
                    "error": None,
                    "fallback_reason": None,
                },
            ],
        ) as translate_mock:
            first = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 13, paths[0]
            )
            second = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 14, paths[1]
            )

        meeting = meeting_repository.get_meeting("meeting_realtime")
        self.assertEqual(first["text"], "hello")
        self.assertEqual(second["text"], "welcome")
        self.assertEqual([call.args[0] for call in translate_mock.call_args_list], ["hello", "welcome"])
        self.assertIn("[00:01:44] hello", meeting.realtime_transcript_text)
        self.assertIn("[00:01:52] welcome", meeting.realtime_transcript_text)
        self.assertNotIn("hello welcome", meeting.realtime_transcript_text)

    def test_realtime_translation_payload_uses_gemini_provider(self):
        path = self.chunk_path("meeting_realtime_chunk_15.webm")
        path.write_bytes(b"valid chunk" * 2048)
        fake_module = self.fake_whisper_module(["new chinese text"])

        with self.installed_model_patch(), self.bypass_audio_validation_patch(), patch.dict(
            sys.modules, {"faster_whisper": fake_module}
        ), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            return_value={
                "success": True,
                "provider": "gemini",
                "source_text": "new chinese text",
                "translated_text": "new English text",
                "latency_ms": 22,
                "error": None,
                "fallback_reason": None,
            },
        ) as translate_mock:
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 15, path
            )

        translate_mock.assert_called_once_with("new chinese text")
        self.assertEqual(result["translation_provider"], "gemini")
        self.assertEqual(result["translation_text"], "new English text")
        self.assertEqual(result["translation_latency_ms"], 22)
        self.assertIsNone(result["translation_fallback_reason"])

    def test_gemini_failure_returns_mock_fallback_reason(self):
        path = self.chunk_path("meeting_realtime_chunk_16.webm")
        path.write_bytes(b"valid chunk" * 2048)
        fake_module = self.fake_whisper_module(["fallback text"])

        with self.installed_model_patch(), self.bypass_audio_validation_patch(), patch.dict(
            sys.modules, {"faster_whisper": fake_module}
        ), patch.object(
            realtime_transcription_service,
            "translate_zh_to_en",
            return_value={
                "success": False,
                "provider": "mock",
                "source_text": "fallback text",
                "translated_text": "[Mock EN] fallback",
                "latency_ms": 30,
                "error": "GEMINI_API_ERROR",
                "fallback_reason": "GEMINI_REQUEST_FAILED: GEMINI_API_ERROR",
            },
        ):
            result = realtime_transcription_service.transcribe_realtime_chunk(
                "meeting_realtime", 16, path
            )

        self.assertEqual(result["translation_provider"], "mock")
        self.assertEqual(result["translation_text"], "[Mock EN] fallback")
        self.assertEqual(
            result["translation_fallback_reason"],
            "GEMINI_REQUEST_FAILED: GEMINI_API_ERROR",
        )


if __name__ == "__main__":
    unittest.main()
