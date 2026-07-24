# Step 4: Exporter

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 마스터 스프레드시트 구조, 시트별 스키마
- `/docs/ADR.md` — ADR-003(NotebookLM 범위 밖)
- `/src/processors/` — step3 산출물
- `/src/utils/constants.py` — 시트 이름 상수

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 4-1. src/exporters/excel_exporter.py

마스터 스프레드시트(.xlsx) 생성 모듈.

```python
# 시그니처
class ExcelExporter:
    def export(
        self,
        master_df: pd.DataFrame,
        assignment_defs: pd.DataFrame,
        assignment_status: pd.DataFrame,
        output_path: Path
    ) -> Path: ...
    # 3개 시트를 가진 .xlsx 파일 생성:
    # 1. 수강생_마스터 — master_df
    # 2. 과제_정의 — assignment_defs
    # 3. 과제_현황 — assignment_status

    def _style_sheet(self, ws, df: pd.DataFrame) -> None: ...
    # 헤더 스타일링: 굵은 글씨, 배경색, 자동 열 너비
    # 조건부 서식: grade=Pass → 초록, Fail → 빨강, 진행중 → 노랑

    def _add_summary_sheet(self, wb, master_df: pd.DataFrame) -> None: ...
    # 요약 시트 추가:
    # - 카테고리별 수강생 수
    # - 클래스별 이수율
    # - 기수별 현황
```

핵심 규칙:
- openpyxl로 서식 적용 (pandas to_excel은 데이터만, 서식은 openpyxl로)
- 파일명: `wave-academy-master-{cohort}-{timestamp}.xlsx`
- 한글 호환 (UTF-8)
- 기존 마스터 파일이 있으면 덮어쓰기 (새 파일로 생성)

## Acceptance Criteria

```bash
source .venv/bin/activate && python -c "
from src.exporters.excel_exporter import ExcelExporter
import pandas as pd
from pathlib import Path
e = ExcelExporter()
df = pd.DataFrame({'name': ['테스트'], 'grade': ['Pass']})
p = e.export(df, pd.DataFrame(), pd.DataFrame(), Path('/tmp/test-export.xlsx'))
print('OK:', p.exists())
"
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

- NotebookLM에 직접 업로드하지 마라. 이유: ADR-003 — 범위 밖.
- xlsxwriter를 사용하지 마라. 이유: openpyxl로 통일 (읽기+쓰기 모두 가능).
- 원본 수강신청 파일을 수정하지 마라. 이유: CLAUDE.md CRITICAL.
