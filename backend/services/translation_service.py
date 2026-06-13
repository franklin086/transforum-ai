from config import GEMINI_API_KEY, GEMINI_TRANSLATION_MODEL


def _mock_translate_zh_to_en(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        return ""
    return "[Mock EN] Hello everyone, welcome to the meeting."


def _build_translation_prompt(text: str) -> str:
    return (
        "Translate Chinese meeting subtitles into natural English.\n"
        "Keep the translation concise.\n"
        "Do not add explanations.\n"
        "Do not include quotation marks.\n\n"
        f"Chinese subtitle:\n{text}"
    )


def _translate_with_gemini(text: str) -> str:
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_TRANSLATION_MODEL,
        contents=_build_translation_prompt(text),
    )
    translated = (getattr(response, "text", "") or "").strip()
    if not translated:
        raise ValueError("Gemini returned an empty translation.")
    return translated.strip('"').strip("'").strip()


def translate_zh_to_en(text: str) -> dict:
    """Translate Chinese meeting subtitles to English with Gemini fallback."""
    normalized = text.strip()
    if not normalized:
        return {
            "success": True,
            "provider": "mock" if not GEMINI_API_KEY else "gemini",
            "source_text": "",
            "translated_text": "",
        }

    if not GEMINI_API_KEY:
        return {
            "success": True,
            "provider": "mock",
            "source_text": normalized,
            "translated_text": _mock_translate_zh_to_en(normalized),
        }

    try:
        return {
            "success": True,
            "provider": "gemini",
            "source_text": normalized,
            "translated_text": _translate_with_gemini(normalized),
        }
    except Exception as error:
        return {
            "success": False,
            "provider": "gemini",
            "source_text": normalized,
            "error": str(error),
            "fallback_text": _mock_translate_zh_to_en(normalized),
        }
