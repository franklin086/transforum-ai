import json
import os
from urllib import error, request


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("TRANSFORUM_GEMINI_MODEL", "gemini-1.5-flash")


def _mock_translate_zh_to_en(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        return ""
    return "[Mock EN] Hello everyone, welcome to the meeting."


def _translate_with_gemini(text: str) -> str:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Translate the following Chinese live caption into "
                            "natural English. Return only the English translation.\n\n"
                            f"{text}"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        endpoint,
        data=encoded_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=12) as response:
        body = json.loads(response.read().decode("utf-8"))

    candidates = body.get("candidates") or []
    if not candidates:
        return _mock_translate_zh_to_en(text)

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )
    translated = "".join(part.get("text", "") for part in parts).strip()
    return translated or _mock_translate_zh_to_en(text)


def translate_zh_to_en(text: str) -> str:
    """Translate Chinese live caption text to English.

    Gemini is used when an API key is configured. Mock output keeps the realtime
    subtitle chain usable in offline or unconfigured local environments.
    """
    normalized = text.strip()
    if not normalized:
        return ""
    if not GEMINI_API_KEY:
        return _mock_translate_zh_to_en(normalized)

    try:
        return _translate_with_gemini(normalized)
    except (error.URLError, TimeoutError, ValueError, KeyError, OSError):
        return _mock_translate_zh_to_en(normalized)
