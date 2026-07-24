# Step 1: Drive Client

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — Google Drive API 인증, 데이터 흐름
- `/docs/ADR.md` — ADR-002(Drive API)
- `/src/` — step0에서 생성된 파일 구조

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 1-1. config.py

프로젝트 설정 상수를 정의하라.

```python
# 시그니처
SCOPES: list[str]  # Drive API 스코프
CREDENTIALS_DIR: Path  # credentials/ 경로
TOKEN_FILE: Path  # token.json 경로
CREDENTIALS_FILE: Path  # credentials.json 경로
SCAN_FOLDER_NAME: str = "wave_수강신청"
OUTPUT_FOLDER_PATH: str = "Wave/행정/수강관리"
TEMP_DIR: Path  # 임시 다운로드 디렉토리
PASS_THRESHOLD: float = 80.0
CURRENT_YEAR: int = 2026
```

### 1-2. src/utils/constants.py

분류 체계, 시트 이름 등 상수 정의.

```python
CATEGORIES: list[str]  # 교회강의, Wave Academy, 자격증과정, 외부강의
CLASS_LEVELS: list[str]  # Class #1, Class #2, Class #3
TARGETS: list[str]  # 목회자, 일반
REGIONS: list[str]  # 본부, 부산, 충남, 꿈별
GRADE_PASS = "Pass"
GRADE_FAIL = "Fail"
GRADE_IN_PROGRESS = "진행중"
SHEET_MASTER = "수강생_마스터"
SHEET_ASSIGNMENT_DEF = "과제_정의"
SHEET_ASSIGNMENT_STATUS = "과제_현황"
```

### 1-3. src/utils/error_handler.py

에러 분류 및 로깅 모듈.

```python
# 시그니처
class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

def log_error(severity: Severity, module: str, message: str, details: str | None = None) -> None: ...
def wrap(fn: Callable, module: str, severity: Severity = Severity.HIGH) -> Callable: ...
```

핵심 규칙:
- Python logging 모듈 사용 (stdout + 파일)
- CRITICAL/HIGH → 예외 re-raise
- MEDIUM → 로그 후 None 반환
- LOW → 로그만

### 1-4. src/drive/client.py

Google Drive API 인증 및 파일 조작 클라이언트.

```python
# 시그니처
class DriveClient:
    def __init__(self) -> None: ...  # OAuth2 인증 (credentials.json → token.json)
    def find_folder(self, name: str) -> str | None: ...  # 폴더 이름 → ID
    def list_files(self, folder_id: str) -> list[dict]: ...  # 폴더 내 파일 목록
    def download_as_xlsx(self, file_id: str, dest_path: Path) -> Path: ...  # .gsheet → .xlsx export 또는 .xlsx 직접 다운로드
    def upload_file(self, local_path: Path, folder_id: str, name: str) -> str: ...  # 파일 업로드
    def find_or_create_folder(self, path: str) -> str: ...  # 경로 기반 폴더 탐색/생성
```

핵심 규칙:
- credentials.json이 없으면 CRITICAL 에러 + 안내 메시지 출력 후 중단
- token.json이 없으면 브라우저 인증 플로우 자동 실행
- .gsheet 파일은 `export(mimeType=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)`로 다운로드
- .xlsx 파일은 `get_media()`로 직접 다운로드

### 1-5. src/drive/scanner.py

wave_수강신청 폴더를 스캔하여 파일 목록을 반환.

```python
# 시그니처
class DriveScanner:
    def __init__(self, client: DriveClient) -> None: ...
    def scan(self) -> list[dict]: ...
    # 반환: [{ file_id, file_name, mime_type, local_path }]
    # 1. find_folder("wave_수강신청")
    # 2. list_files()
    # 3. .gsheet 또는 .xlsx만 필터
    # 4. 각 파일을 temp 디렉토리에 .xlsx로 다운로드
```

핵심 규칙:
- CRITICAL: 원본 파일은 읽기 전용. 다운로드만 하고 원본 수정 금지.
- 파일명에 "(응답)" 포함된 것만 대상
- 개별 파일 다운로드 실패 시 스킵 + MEDIUM 에러 로그

## Acceptance Criteria

```bash
source .venv/bin/activate && pytest --collect-only 2>&1 | tail -5   # 테스트 수집 에러 없음
python -c "from src.drive.client import DriveClient; from src.drive.scanner import DriveScanner; print('OK')"
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- credentials.json을 코드에 하드코딩하지 마라. 이유: 보안.
- Google Drive의 원본 파일을 수정/삭제하지 마라. 이유: CLAUDE.md CRITICAL.
- Drive API 외의 방법(gdown, 직접 URL 등)으로 파일을 다운로드하지 마라. 이유: 인증 우회.
