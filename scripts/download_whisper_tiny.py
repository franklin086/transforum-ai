from pathlib import Path
import sys

from huggingface_hub import snapshot_download


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = PROJECT_ROOT / "models" / "whisper" / "tiny"
REPO_ID = "Systran/faster-whisper-tiny"


def main() -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {REPO_ID}")
    print(f"Target: {TARGET_DIR}")

    try:
        snapshot_download(
            repo_id=REPO_ID,
            local_dir=TARGET_DIR,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
    except Exception as error:
        print("DOWNLOAD_FAILED")
        print(f"{type(error).__name__}: {error}")
        existing_files = [path for path in TARGET_DIR.rglob("*") if path.is_file()]
        print(f"Partial files: {len(existing_files)}")
        for path in existing_files[:30]:
            print(path.relative_to(TARGET_DIR))
        return 1

    files = [path for path in TARGET_DIR.rglob("*") if path.is_file()]
    print("DOWNLOAD_SUCCESS")
    print(f"Files: {len(files)}")
    for path in files:
        print(path.relative_to(TARGET_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
