# Step 5: Main Pipeline

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 전체 파이프라인 데이터 흐름
- `/src/` — step0~4 전체 산출물. 모든 파일을 읽어라.

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 5-1. src/main.py

CLI 진입점. 전체 파이프라인을 연결하는 메인 함수.

```python
# 시그니처
def main() -> None: ...
# argparse로 CLI 옵션:
#   --scan-only     파일 스캔만 (다운로드까지)
#   --export-only   기존 마스터에서 내보내기만
#   --no-upload     Drive 업로드 스킵 (로컬 파일만 생성)
#   --master PATH   기존 마스터 Excel 경로 (업데이트 모드)
#   --output PATH   출력 파일 경로 (기본: output/)

# 전체 파이프라인:
# 1. DriveClient 초기화 (OAuth 인증)
# 2. DriveScanner로 wave_수강신청 폴더 스캔 + 다운로드
# 3. 각 파일에 대해:
#    a. filename_parser로 파일명 파싱
#    b. StudentProcessor.process_file()로 데이터 처리
# 4. GradeCalculator.calculate_all()로 학점 계산
# 5. ExcelExporter.export()로 마스터 Excel 생성
# 6. DriveClient.upload_file()로 Google Drive에 업로드 (--no-upload 아닌 경우)
# 7. 처리 결과 요약 출력
```

핵심 규칙:
- 각 단계 시작/완료 로그 출력
- 개별 파일 실패 시 스킵 + 다음 파일 계속 처리
- 전체 완료 후 요약 출력: 처리 파일 수, 신규/업데이트/스킵/에러 수

### 5-2. output/ 디렉토리

프로젝트 루트에 `output/` 디렉토리 생성. .gitignore에 `output/` 추가.

### 5-3. 전체 통합 테스트

Google Drive 연동 없이 로컬 Excel 파일로 전체 파이프라인을 검증하는 테스트:

```python
# tests/test_pipeline.py
def test_full_pipeline_local():
    # 1. 테스트용 .xlsx 파일 생성 (수강신청 응답 형식)
    # 2. StudentProcessor로 처리
    # 3. GradeCalculator로 학점 계산
    # 4. ExcelExporter로 내보내기
    # 5. 결과 Excel 검증 (시트 수, 행 수, 컬럼 확인)
```

### 5-4. README 업데이트

프로젝트 루트 README.md에 사용법 추가:

```markdown
## 사용법

### 사전 준비
1. Google Cloud Console에서 OAuth2 Client ID 생성 (Desktop)
2. credentials.json을 `credentials/` 디렉토리에 저장

### 실행
python src/main.py                  # 전체 파이프라인
python src/main.py --scan-only      # 스캔만
python src/main.py --no-upload      # 업로드 스킵
```

## Acceptance Criteria

```bash
source .venv/bin/activate && pytest tests/ -v 2>&1 | tail -20   # 전체 테스트 PASS
python -c "from src.main import main; print('import OK')"   # 임포트 성공
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

- main.py에서 비즈니스 로직을 직접 구현하지 마라. 이유: 각 모듈을 조합만 해야 함.
- Google Drive 인증 실패 시 자동 재시도하지 마라. 이유: 사용자가 credentials를 확인해야 함. blocked 처리.
- output/ 디렉토리의 기존 파일을 삭제하지 마라. 이유: 이전 결과물 보존.
