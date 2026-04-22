"""Google Drive API 클라이언트 — 인증, 다운로드, 업로드."""

import io
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from src.config import CREDENTIALS_FILE, SCOPES, TEMP_DIR, TOKEN_FILE
from src.utils.constants import FOLDER_MIME, GSHEET_MIME, XLSX_MIME
from src.utils.error_handler import Severity, log_error


class DriveClient:
    def __init__(self) -> None:
        if not CREDENTIALS_FILE.exists():
            msg = (
                f"credentials.json 파일이 없습니다: {CREDENTIALS_FILE}\n"
                "Google Cloud Console에서 OAuth2 클라이언트 ID를 다운로드하여 "
                f"{CREDENTIALS_FILE} 경로에 저장하세요."
            )
            log_error(Severity.CRITICAL, "DriveClient", msg)
            raise FileNotFoundError(msg)

        creds = self._load_or_refresh_credentials()
        self._service = build("drive", "v3", credentials=creds)
        TEMP_DIR.mkdir(exist_ok=True)

    def _load_or_refresh_credentials(self) -> Credentials:
        creds: Credentials | None = None

        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
            TOKEN_FILE.parent.mkdir(exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

        return creds

    def find_folder(self, name: str) -> str | None:
        query = (
            f"name = '{name}' and mimeType = '{FOLDER_MIME}' and trashed = false"
        )
        result = (
            self._service.files()
            .list(q=query, fields="files(id, name)", pageSize=1)
            .execute()
        )
        files = result.get("files", [])
        return files[0]["id"] if files else None

    def list_files(self, folder_id: str) -> list[dict]:
        results: list[dict] = []
        page_token: str | None = None

        while True:
            params: dict = {
                "q": f"'{folder_id}' in parents and trashed = false",
                "fields": "nextPageToken, files(id, name, mimeType)",
                "pageSize": 100,
            }
            if page_token:
                params["pageToken"] = page_token

            response = self._service.files().list(**params).execute()
            results.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return results

    def download_as_xlsx(self, file_id: str, dest_path: Path) -> Path:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        file_meta = (
            self._service.files().get(fileId=file_id, fields="mimeType").execute()
        )
        mime = file_meta.get("mimeType", "")

        if mime == GSHEET_MIME:
            request = self._service.files().export_media(
                fileId=file_id, mimeType=XLSX_MIME
            )
        else:
            request = self._service.files().get_media(fileId=file_id)

        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        dest_path.write_bytes(buffer.getvalue())
        return dest_path

    def upload_file(self, local_path: Path, folder_id: str, name: str) -> str:
        file_metadata = {"name": name, "parents": [folder_id]}
        media = MediaFileUpload(str(local_path), resumable=True)
        uploaded = (
            self._service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return uploaded["id"]

    def find_or_create_folder(self, path: str) -> str:
        parts = [p for p in path.split("/") if p]
        parent_id = "root"

        for part in parts:
            query = (
                f"name = '{part}' and mimeType = '{FOLDER_MIME}' "
                f"and '{parent_id}' in parents and trashed = false"
            )
            result = (
                self._service.files()
                .list(q=query, fields="files(id)", pageSize=1)
                .execute()
            )
            files = result.get("files", [])
            if files:
                parent_id = files[0]["id"]
            else:
                folder = (
                    self._service.files()
                    .create(
                        body={
                            "name": part,
                            "mimeType": FOLDER_MIME,
                            "parents": [parent_id],
                        },
                        fields="id",
                    )
                    .execute()
                )
                parent_id = folder["id"]

        return parent_id
