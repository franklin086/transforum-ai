from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env_file() -> None:
    if not ENV_PATH.exists():
        return

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

WHISPER_MODEL = os.getenv("TRANSFORUM_WHISPER_MODEL", "tiny")
WHISPER_MODEL_PATH = Path(
    os.getenv(
        "TRANSFORUM_WHISPER_MODEL_PATH",
        str(PROJECT_ROOT / "models" / "whisper"),
    )
)
WHISPER_DEVICE = os.getenv("TRANSFORUM_WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("TRANSFORUM_WHISPER_COMPUTE_TYPE", "int8")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_TRANSLATION_MODEL = os.getenv(
    "GEMINI_TRANSLATION_MODEL",
    os.getenv("TRANSFORUM_GEMINI_MODEL", "gemini-3.5-flash"),
)


def get_whisper_model_dir() -> Path:
    return WHISPER_MODEL_PATH / WHISPER_MODEL


def get_whisper_model_status() -> dict:
    model_dir = get_whisper_model_dir()
    installed = model_dir.exists() and any(model_dir.iterdir())
    available_model_names = ["tiny", "base", "small"]
    available_models = {
        name: {
            "installed": (WHISPER_MODEL_PATH / name).exists()
            and any((WHISPER_MODEL_PATH / name).iterdir()),
            "path": str(WHISPER_MODEL_PATH / name).replace("\\", "/"),
        }
        for name in available_model_names
    }

    return {
        "installed": installed,
        "model": WHISPER_MODEL,
        "current_model": WHISPER_MODEL,
        "path": str(WHISPER_MODEL_PATH).replace("\\", "/"),
        "model_path": str(model_dir).replace("\\", "/"),
        "active_model_path": str(model_dir).replace("\\", "/"),
        "available_models": available_models,
        "recommended_for_field_test": "base",
        "message": "Ready" if installed else "Model not found",
    }
