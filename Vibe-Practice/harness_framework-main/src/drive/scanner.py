"""wave_수강신청 폴더 스캔, 파일 목록 반환."""

from pathlib import Path

from src.config import SCAN_FOLDER_NAME, TEMP_DIR
from src.drive.client import DriveClient
from src.utils.constants import GSHEET_MIME, XLSX_MIME
from src.utils.error_handler import Severity, log_error


class DriveScanner:
    def __init__(self, client: DriveClient) -> None:
        self._client = client

    def scan(self) -> list[dict]:
        folder_id = self._client.find_folder(SCAN_FOLDER_NAME)
        if not folder_id:
            log_error(
                Severity.HIGH,
                "DriveScanner",
                f"폴더를 찾을 수 없습니다: {SCAN_FOLDER_NAME}",
            )
            return []

        all_files = self._client.list_files(folder_id)
        target_files = [
            f
            for f in all_files
            if "(응답)" in f["name"]
            and f["mimeType"] in (GSHEET_MIME, XLSX_MIME)
        ]

        results: list[dict] = []
        for file in target_files:
            dest = TEMP_DIR / f"{file['id']}.xlsx"
            try:
                local_path = self._client.download_as_xlsx(file["id"], dest)
                results.append(
                    {
                        "file_id": file["id"],
                        "file_name": file["name"],
                        "mime_type": file["mimeType"],
                        "local_path": local_path,
                    }
                )
            except Exception as exc:
                log_error(
                    Severity.MEDIUM,
                    "DriveScanner",
                    f"파일 다운로드 실패: {file['name']}",
                    details=str(exc),
                    exc=exc,
                )

        return results
