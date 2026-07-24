# Step 3: Processors

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 수강생_마스터 스키마, 과제 스키마, 데이터 흐름
- `/docs/ADR.md` — ADR-004(동적 과제), ADR-007(soft delete)
- `/src/parsers/` — step2 산출물
- `/src/utils/`, `/src/config.py` — step1 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 3-1. src/processors/student_processor.py

수강생 데이터 통합: 여러 파일에서 읽은 데이터를 하나의 마스터 DataFrame으로 병합.

```python
# 시그니처
class StudentProcessor:
    def __init__(self) -> None: ...  # 빈 마스터 DataFrame 초기화

    def load_existing(self, master_path: Path | None) -> None: ...
    # 기존 마스터 Excel이 있으면 로드

    def process_file(self, local_path: Path, parsed_filename: ParsedFileName) -> int: ...
    # 1. openpyxl로 Excel 읽기
    # 2. column_mapper로 헤더 매핑
    # 3. normalizer로 정규화
    # 4. parsed_filename에서 category/class_level/target/region/cohort 병합
    # 5. upsert (email + class_level + cohort 기준 중복 제거)
    # 반환: 처리된 행 수

    def get_master(self) -> pd.DataFrame: ...
    # 현재 마스터 DataFrame 반환

    def get_stats(self) -> dict: ...
    # { total, new, updated, skipped, errors }
```

핵심 규칙:
- upsert 중복 기준: email + class_level + cohort
- 기존 레코드 → updated_at 갱신, 변경 필드만 업데이트
- 신규 레코드 → UUID 생성, created_at 설정, is_active=True
- CRITICAL: 원본 파일 수정 금지. DataFrame으로만 작업.
- 개별 행 처리 실패 시 스킵 + MEDIUM 에러 (전체 중단 안 함)

### 3-2. src/processors/assignment_manager.py

과제 정의 및 현황 관리.

```python
# 시그니처
class AssignmentManager:
    def __init__(self) -> None: ...

    def load_definitions(self, master_path: Path | None) -> None: ...
    # 기존 마스터 Excel의 과제_정의 시트에서 로드

    def load_status(self, master_path: Path | None) -> None: ...
    # 기존 마스터 Excel의 과제_현황 시트에서 로드

    def get_completion_rate(self, student_id: str) -> float: ...
    # weight 기반 가중 완료율 계산

    def get_definitions(self) -> pd.DataFrame: ...
    def get_status(self) -> pd.DataFrame: ...
```

핵심 규칙:
- 과제_정의 시트가 없으면 빈 DataFrame으로 시작 (사용자가 마스터 Excel에서 직접 추가)
- weight 합이 100%가 아니어도 비례 계산

### 3-3. src/processors/grade_calculator.py

이수 판정 로직.

```python
# 시그니처
def calculate_grade(
    completion_rate: float,
    course_completed: bool,
    payment_status: bool,
    threshold: float = 80.0
) -> tuple[str, str]: ...
# 반환: (grade, reason)
# Pass: completion_rate >= threshold AND course_completed AND payment_status
# Fail: course_completed AND (rate < threshold OR not payment)
# 진행중: not course_completed

def calculate_all(master_df: pd.DataFrame, threshold: float = 80.0) -> pd.DataFrame: ...
# 전체 수강생 학점 일괄 계산, grade 컬럼 업데이트
```

### 3-4. pytest 테스트

`tests/test_grade_calculator.py`:
- Pass (rate>=80, completed, paid)
- Fail (rate<80, completed)
- 진행중 (not completed)
- 경계값 (rate=80 정확히)

`tests/test_student_processor.py`:
- 중복 제거 (같은 email+class+cohort)
- 신규 추가
- 빈 파일 처리

## Acceptance Criteria

```bash
source .venv/bin/activate && pytest tests/ -v 2>&1 | tail -20   # 전부 PASS
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

- 학점을 자동으로 Fail로 변경하지 마라 (과정 진행 중). 이유: 과제 제출 기회가 남아있을 수 있음.
- pandas DataFrame을 inplace 수정하지 마라. 이유: 불변성 원칙. 새 DataFrame 반환.
- StudentProcessor에서 Google Drive에 직접 접근하지 마라. 이유: 로컬 파일만 처리. Drive 연동은 main.py에서.
