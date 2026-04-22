"""설정 — 폴더 ID, 분류 체계 등 전역 설정값."""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

CREDENTIALS_DIR: Path = BASE_DIR / "credentials"
TOKEN_FILE: Path = CREDENTIALS_DIR / "token.json"
CREDENTIALS_FILE: Path = CREDENTIALS_DIR / "credentials.json"

SCAN_FOLDER_NAME: str = "wave_수강신청"
OUTPUT_FOLDER_PATH: str = "Wave/행정/수강관리"

TEMP_DIR: Path = BASE_DIR / "temp"

PASS_THRESHOLD: float = 80.0
CURRENT_YEAR: int = 2026
