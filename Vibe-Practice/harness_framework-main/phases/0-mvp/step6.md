# Step 6: Exporter & Trigger

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — CsvExporter, TimeTrigger 관련 섹션
- `/docs/PRD.md` — F5(내보내기), F9(기수 관리)
- `/docs/ADR.md` — ADR-003(NotebookLM 범위 밖), ADR-013(기수=월)
- `/gas/src/` — step0~5 전체 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 6-1. CsvExporter.js

NotebookLM용 데이터 내보내기 모듈. CSV 또는 JSON 형식으로 Google Drive에 파일 생성.

```javascript
// 시그니처
const CsvExporter = {
  export(options) { ... },
  // options: { format: 'csv'|'json', filters: {...}, includeAssignments: boolean }
  // 1. StudentManager.list() + AssignmentManager.getStudentAssignments()
  // 2. 데이터 정제 (개인정보 포함 — admin 전용 기능)
  // 3. CSV/JSON 문자열 생성
  // 4. DriveApp.createFile()로 Google Drive에 저장
  // 반환: { fileId, fileName, url, recordCount }

  _toCsv(data) { ... },
  _toJson(data) { ... },
  _sanitizeForExport(students) { ... }  // 내보내기용 데이터 정제
};
```

핵심 규칙:
- admin only (Auth.withAuth 적용)
- 내보내기 파일은 `Wave/행정/수강관리/exports/` 폴더에 저장
- 파일명: `wave-academy-export-{cohort}-{timestamp}.{csv|json}`
- is_active=false인 레코드는 기본 제외 (옵션으로 포함 가능)
- CSV는 BOM(UTF-8 BOM) 포함하여 한글 Excel 호환

### 6-2. TimeTrigger.js

자동 스캔 트리거 관리 모듈.

```javascript
// 시그니처
const TimeTrigger = {
  enable() { ... },
  // _config의 AUTO_SCAN_INTERVAL_HOURS 기반으로 시간 트리거 생성
  // 기존 트리거가 있으면 삭제 후 재생성

  disable() { ... },
  // 자동 스캔 트리거 삭제

  isEnabled() { ... },
  // 현재 트리거 활성화 여부

  onTrigger() { ... }
  // 트리거 실행 시 호출되는 함수: runFullScan() 래핑
};
```

핵심 규칙:
- 일일 트리거 20개 제한 → 트리거는 1개만 사용
- enable/disable 시 _config의 AUTO_SCAN_ENABLED 동기화
- 트리거 실행 실패 시 ErrorHandler로 CRITICAL 로그

### 6-3. CohortManager (Setup.js에 추가)

기수(cohort) 관리 기능을 Setup.js에 추가.

```javascript
// Setup.js에 추가할 시그니처
const CohortManager = {
  list() { ... },           // 존재하는 기수 목록 (수강생_마스터에서 distinct cohort)
  getCurrent() { ... },     // _config의 CURRENT_COHORT
  setCurrent(cohort) { ... } // CURRENT_COHORT 변경 (admin)
};
```

### 6-4. Router.js 라우트 추가

- exportData → CsvExporter.export (admin)
- getCohorts → CohortManager.list

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # 기존 테스트 PASS 유지
cd gas && clasp push --force 2>&1 | tail -5   # 배포 에러 없음
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

- NotebookLM API를 직접 호출하지 마라. 이유: ADR-003 — 범위 밖. CSV/JSON 파일 생성까지만.
- 트리거를 2개 이상 만들지 마라. 이유: GAS 일일 트리거 20개 제한, 최소화 원칙.
- 내보내기 파일을 원본 응답 폴더에 저장하지 마라. 이유: 스캔 시 혼동 위험.
