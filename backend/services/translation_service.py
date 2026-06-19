import re
import time

from config import GEMINI_API_KEY, GEMINI_TRANSLATION_MODEL


RATE_LIMIT_PATTERNS = ("rate limit", "quota", "429", "resource exhausted")
NETWORK_PATTERNS = ("timeout", "timed out", "connection", "network", "dns")


def _mock_translate_zh_to_en(text: str) -> str:
    return "" if text.strip() else ""


def remove_translation_noise(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:\w+)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    cleaned = re.sub(
        r"^(translation|english|translated text|the translation is)\s*:\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = cleaned.strip(" \t\r\n\"'“”‘’")
    cleaned = re.sub(r"[*_`#>]+", "", cleaned)
    cleaned = re.sub(r"\s*\n+\s*", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


def _build_translation_prompt(text: str) -> str:
    return (
        "You are a professional conference interpreter.\n\n"
        "Task:\n"
        "Translate Chinese live meeting subtitles into concise, natural English subtitles.\n\n"
        "Rules:\n"
        "1. Keep the translation concise.\n"
        "2. Preserve the speaker's meaning.\n"
        "3. Do not add explanations.\n"
        "4. Do not add quotation marks.\n"
        "5. Do not output markdown.\n"
        "6. Do not say \"Translation:\".\n"
        "7. If the Chinese sentence is incomplete, translate naturally without over-explaining.\n"
        "8. Keep names, organizations, and acronyms accurate.\n"
        "9. Use formal but natural conference English.\n"
        "10. Output English only.\n\n"
        "Input example:\n"
        "大家好，欢迎参加今天的论坛。\n\n"
        "Output example:\n"
        "Good morning, everyone. Welcome to today's forum.\n\n"
        f"Chinese subtitle:\n{text}"
    )


def _classify_gemini_error(error: Exception) -> str:
    message = str(error).lower()
    if any(pattern in message for pattern in RATE_LIMIT_PATTERNS):
        return "GEMINI_RATE_LIMIT"
    if any(pattern in message for pattern in NETWORK_PATTERNS):
        return "GEMINI_NETWORK_ERROR"
    return "GEMINI_API_ERROR"


def _translate_with_gemini(text: str) -> str:
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_TRANSLATION_MODEL,
        contents=_build_translation_prompt(text),
    )
    translated = remove_translation_noise(getattr(response, "text", "") or "")
    if not translated:
        raise ValueError("Gemini returned an empty translation.")
    return translated


def _fallback_result(source_text: str, error_code: str, latency_ms: int = 0) -> dict:
    fallback_reason = error_code
    if error_code != "GEMINI_API_KEY_MISSING":
        fallback_reason = f"GEMINI_REQUEST_FAILED: {error_code}"
    return {
        "success": False,
        "provider": "mock",
        "translation_status": "fallback",
        "source_text": source_text,
        "translated_text": _mock_translate_zh_to_en(source_text),
        "latency_ms": latency_ms,
        "error": error_code,
        "fallback_reason": fallback_reason,
        "gemini_configured": bool(GEMINI_API_KEY),
    }


def get_translation_status() -> dict:
    configured = bool(GEMINI_API_KEY)
    return {
        "gemini_api_key_configured": configured,
        "provider": "gemini" if configured else "mock",
        "model": GEMINI_TRANSLATION_MODEL if configured else None,
    }


def translate_zh_to_en(text: str) -> dict:
    """Translate Chinese meeting subtitles to English with Gemini fallback."""
    normalized = text.strip()
    if not normalized:
        return {
            "success": True,
            "provider": "waiting",
            "translation_status": "waiting",
            "source_text": "",
            "translated_text": "",
            "latency_ms": 0,
            "error": None,
            "fallback_reason": None,
            "gemini_configured": bool(GEMINI_API_KEY),
        }

    if not GEMINI_API_KEY:
        return _fallback_result(normalized, "GEMINI_API_KEY_MISSING")

    started = time.perf_counter()
    last_error_code = "GEMINI_API_ERROR"

    for attempt in range(2):
        try:
            translated = _translate_with_gemini(normalized)
            latency_ms = int((time.perf_counter() - started) * 1000)
            print(f"Gemini translation latency: {latency_ms} ms")
            return {
                "success": True,
                "provider": "gemini",
                "translation_status": "translated",
                "source_text": normalized,
                "translated_text": translated,
                "latency_ms": latency_ms,
                "error": None,
                "fallback_reason": None,
                "gemini_configured": True,
            }
        except Exception as error:
            last_error_code = _classify_gemini_error(error)
            print(f"Gemini translation error: {last_error_code}: {error}")
            if last_error_code == "GEMINI_RATE_LIMIT" and attempt == 0:
                time.sleep(0.5)
                continue
            break

    latency_ms = int((time.perf_counter() - started) * 1000)
    print(f"Gemini translation latency: {latency_ms} ms")
    return _fallback_result(normalized, last_error_code, latency_ms)
