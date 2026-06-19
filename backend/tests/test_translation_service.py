import unittest
from unittest.mock import patch

from api import translation as translation_api
from services import translation_service


class TranslationServiceTest(unittest.TestCase):
    def test_translates_chinese_meeting_welcome_with_gemini(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "test-key"), patch.object(
            translation_service,
            "_translate_with_gemini",
            return_value="Hello everyone, welcome to the TransForum AI test meeting.",
        ):
            result = translation_service.translate_zh_to_en(
                "大家好，欢迎参加 TransForum AI 测试会议。"
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(
            result["translated_text"],
            "Hello everyone, welcome to the TransForum AI test meeting.",
        )
        self.assertIsNone(result["error"])
        self.assertGreaterEqual(result["latency_ms"], 0)

    def test_translates_incomplete_chinese_subtitle_naturally(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "test-key"), patch.object(
            translation_service,
            "_translate_with_gemini",
            return_value="We will move to the Q&A session shortly.",
        ):
            result = translation_service.translate_zh_to_en("我们稍后进入问答环节。")

        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(
            result["translated_text"],
            "We will move to the Q&A session shortly.",
        )

    def test_preserves_proper_names_and_acronyms(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "test-key"), patch.object(
            translation_service,
            "_translate_with_gemini",
            return_value="The APEC Youth Forum now begins.",
        ):
            result = translation_service.translate_zh_to_en("APEC 青年论坛现在开始。")

        self.assertEqual(result["provider"], "gemini")
        self.assertIn("APEC", result["translated_text"])
        self.assertEqual(result["translated_text"], "The APEC Youth Forum now begins.")

    def test_missing_gemini_key_falls_back_to_mock(self):
        with patch.object(translation_service, "GEMINI_API_KEY", None):
            result = translation_service.translate_zh_to_en(
                "今天我们讨论人工智能在国际会议中的应用。"
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["provider"], "mock")
        self.assertEqual(result["error"], "GEMINI_API_KEY_MISSING")
        self.assertTrue(result["translated_text"].startswith("[Mock EN]"))
        self.assertEqual(result["fallback_reason"], "GEMINI_API_KEY_MISSING")
        self.assertEqual(result["latency_ms"], 0)

    def test_removes_translation_prefix(self):
        self.assertEqual(
            translation_service.remove_translation_noise(
                "Translation: Hello everyone, welcome to today's meeting."
            ),
            "Hello everyone, welcome to today's meeting.",
        )

    def test_removes_quotes_and_markdown(self):
        self.assertEqual(
            translation_service.remove_translation_noise(
                '```English\n"Hello everyone, welcome to today\'s meeting."\n```'
            ),
            "Hello everyone, welcome to today's meeting.",
        )

    def test_api_error_falls_back_to_mock(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "test-key"), patch.object(
            translation_service,
            "_translate_with_gemini",
            side_effect=RuntimeError("internal API failure"),
        ):
            result = translation_service.translate_zh_to_en(
                "大家好，欢迎参加 TransForum AI 测试会议。"
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["provider"], "mock")
        self.assertEqual(result["error"], "GEMINI_API_ERROR")
        self.assertEqual(result["fallback_reason"], "GEMINI_REQUEST_FAILED: GEMINI_API_ERROR")
        self.assertTrue(result["translated_text"].startswith("[Mock EN]"))

    def test_rate_limit_retries_once_then_fallback(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "test-key"), patch.object(
            translation_service,
            "_translate_with_gemini",
            side_effect=RuntimeError("429 rate limit"),
        ) as translate_mock, patch.object(translation_service.time, "sleep") as sleep_mock:
            result = translation_service.translate_zh_to_en(
                "大家好，欢迎参加 TransForum AI 测试会议。"
            )

        self.assertEqual(translate_mock.call_count, 2)
        sleep_mock.assert_called_once_with(0.5)
        self.assertFalse(result["success"])
        self.assertEqual(result["provider"], "mock")
        self.assertEqual(result["error"], "GEMINI_RATE_LIMIT")
        self.assertEqual(result["fallback_reason"], "GEMINI_REQUEST_FAILED: GEMINI_RATE_LIMIT")


    def test_empty_text_returns_waiting_without_mock_fallback(self):
        result = translation_service.translate_zh_to_en("   ")

        self.assertTrue(result["success"])
        self.assertEqual(result["provider"], "waiting")
        self.assertEqual(result["translated_text"], "")
        self.assertIsNone(result["fallback_reason"])


    def test_translation_status_reports_gemini_without_exposing_key(self):
        with patch.object(translation_service, "GEMINI_API_KEY", "secret-key"), patch.object(
            translation_service,
            "GEMINI_TRANSLATION_MODEL",
            "gemini-3.5-flash",
        ):
            result = translation_service.get_translation_status()

        self.assertEqual(
            result,
            {
                "gemini_api_key_configured": True,
                "provider": "gemini",
                "model": "gemini-3.5-flash",
            },
        )
        self.assertNotIn("secret-key", str(result))

    def test_translation_status_reports_mock_without_key(self):
        with patch.object(translation_service, "GEMINI_API_KEY", None):
            result = translation_service.get_translation_status()

        self.assertEqual(
            result,
            {
                "gemini_api_key_configured": False,
                "provider": "mock",
                "model": None,
            },
        )


    def test_translation_status_endpoint_returns_status_payload(self):
        expected = {
            "gemini_api_key_configured": True,
            "provider": "gemini",
            "model": "gemini-3.5-flash",
        }
        with patch.object(translation_api, "get_translation_status", return_value=expected):
            self.assertEqual(translation_api.translation_status(), expected)


if __name__ == "__main__":
    unittest.main()
