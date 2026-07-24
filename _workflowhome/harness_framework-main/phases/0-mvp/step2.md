# Step 2: Parsers

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — ColumnMapper 매핑 테이블, Boolean 정규화 테이블, 파일명 패턴
- `/docs/ADR.md` — ADR-005(파일명 패턴), ADR-006(헤더 매핑), ADR-009(기수=월), ADR-010(불린 정규화)
- `/src/utils/constants.py`, `/src/config.py` — step1 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 2-1. src/parsers/filename_parser.py

ADR-005의 6가지 파일명 패턴(A-F)을 파싱.

```python
# 시그니처
@dataclass(frozen=True)
class ParsedFileName:
    month: int | None
    category: str | None
    target: str | None
    class_levels: list[int]
    region: str | None
    raw: str
    parse_error: bool = False

def parse_filename(filename: str) -> ParsedFileName: ...
```

패턴 상세:
- **A**: `(4월 목회자 통합신청서)(응답)` → month=4, target=목회자
- **B**: `(4월 일반 Class #1 & 3통합신청서)(응답)` → month=4, target=일반, class_levels=[1,3]
- **C**: `(3월 교회강의 목회자 Class#1 수강신청)(응답)` → month=3, category=교회강의, target=목회자, class_levels=[1]
- **D**: `(3월 교회강의 일반 Class #1 수강신청)(응답)` → month=3, category=교회강의, target=일반, class_levels=[1]
- **E**: `(4월 꿈별 교회강의 신청서)(응답)` → month=4, region=꿈별, category=교회강의
- **F**: `(4월 부산 교회강의 Class#1 수강신청서)(응답)` → month=4, region=부산, category=교회강의, class_levels=[1]

핵심 규칙:
- Class 번호 앞의 `#`과 공백은 있을 수도 없을 수도 있음
- `&` 구분으로 멀티 클래스 지원
- 파싱 실패 시 parse_error=True 반환 (전체 중단 안 함)
- month를 config.CURRENT_YEAR과 합쳐 cohort 생성 (예: month=3 → "2026-03")

### 2-2. src/parsers/column_mapper.py

ARCHITECTURE.md의 ColumnMapper 매핑 테이블 구현.

```python
# 시그니처
FIELD_KEYWORDS: dict[str, list[str]]  # { field_name: [keyword1, keyword2, ...] }

def build_column_map(headers: list[str]) -> dict[str, int]: ...
# headers → { field_name: column_index }

def map_row(row: list, column_map: dict[str, int]) -> dict[str, Any]: ...
# 단일 행 → { field_name: value }
```

핵심 규칙:
- contains + case-insensitive 매칭
- 필수 필드(email, name) 매핑 실패 시 에러 로그

### 2-3. src/parsers/normalizer.py

ADR-010의 Boolean 정규화 + 전화번호/이메일 정규화.

```python
# 시그니처
def normalize_boolean(value: Any) -> bool: ...
def normalize_phone(value: Any) -> str: ...
def normalize_email(value: Any) -> str: ...
def normalize_row(row: dict[str, Any]) -> dict[str, Any]: ...
```

### 2-4. pytest 테스트 작성

`tests/test_filename_parser.py`:
- 6개 패턴 A-F 각각 정상 파싱
- Class 번호 변형 (Class#1, Class #1)
- 멀티 클래스 (Class #1 & 3)
- 파싱 실패 케이스
- 빈 문자열, None

`tests/test_column_mapper.py`:
- 정상 매핑, 키워드 없는 헤더, 필수 필드 누락

`tests/test_normalizer.py`:
- Boolean 전체 매핑 테이블, 전화번호, 이메일

## Acceptance Criteria

```bash
source .venv/bin/activate && pytest tests/test_filename_parser.py tests/test_column_mapper.py tests/test_normalizer.py -v 2>&1 | tail -20   # 전부 PASS
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

- 정규식을 하나의 거대한 패턴으로 만들지 마라. 이유: 유지보수 불가. 패턴별 개별 매칭.
- 외부 NLP 라이브러리를 사용하지 마라. 이유: 의존성 최소화. 키워드 매칭으로 충분.
- 테스트에서 실제 Google Drive 파일을 사용하지 마라. 이유: 단위 테스트는 로컬 데이터만.
