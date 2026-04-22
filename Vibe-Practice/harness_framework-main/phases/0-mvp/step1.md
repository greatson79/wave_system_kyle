# Step 1: Utils Layer

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 데이터 모델, ColumnMapper 매핑 테이블, Boolean 정규화 테이블, BatchRunner 패턴, 에러 처리 아키텍처
- `/docs/ADR.md` — ADR-006(헤더 기반 매핑), ADR-009(LockService), ADR-014(불린 정규화)
- `/gas/src/` — step0에서 생성된 파일 구조 확인

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 1-1. Constants.js

ARCHITECTURE.md의 분류 체계와 _config 키 목록을 상수로 정의하라.

```javascript
// 시그니처
const CONSTANTS = {
  CATEGORIES: [...],        // 교회강의, Wave Academy, 자격증과정, 외부강의
  CLASS_LEVELS: [...],      // Class #1, Class #2, Class #3
  TARGETS: [...],           // 목회자, 일반
  GRADE: { PASS: 'Pass', FAIL: 'Fail', IN_PROGRESS: '진행중' },
  SHEETS: { MASTER: '수강생_마스터', ASSIGNMENT_DEF: '과제_정의', ... },
  CONFIG_KEYS: { SCAN_FOLDER_IDS: 'SCAN_FOLDER_IDS', ... },
  CACHE_TTL: { DASHBOARD: 300, STUDENTS: 300, ASSIGNMENTS: 600, CONFIG: 1800 },
  BATCH_LIMIT_MS: 270000,  // 4.5분
  SEVERITY: { CRITICAL: 'CRITICAL', HIGH: 'HIGH', MEDIUM: 'MEDIUM', LOW: 'LOW' }
};
```

### 1-2. ErrorHandler.js

ARCHITECTURE.md의 에러 처리 아키텍처(4단계 심각도)를 구현하라.

```javascript
// 시그니처
const ErrorHandler = {
  log(severity, module, message, details) { ... },  // _log 시트에 기록
  wrap(fn, module) { ... },   // try-catch 래퍼, 에러 시 log 후 rethrow/skip
  getRecentLogs(limit) { ... } // 최근 로그 조회
};
```

핵심 규칙:
- CRITICAL/HIGH → 에러를 다시 throw하여 호출자에게 전파
- MEDIUM → 로그 기록 후 null 반환 (스킵)
- LOW → 로그만 기록, 정상 진행
- _log 시트가 없으면 Logger.log 폴백

### 1-3. ColumnMapper.js

ARCHITECTURE.md의 ColumnMapper 필드 매핑 테이블을 구현하라. 헤더 텍스트에 키워드가 포함되어 있는지 검사하여 필드명으로 매핑.

```javascript
// 시그니처
const ColumnMapper = {
  buildMap(headers) { ... },          // headers 배열 → { fieldName: columnIndex } 맵
  mapRow(row, columnMap) { ... },     // 단일 행 → { fieldName: value } 객체
  FIELD_KEYWORDS: { ... }             // ADR-006 매핑 테이블
};
```

핵심 규칙:
- 매핑은 contains + case-insensitive
- 동일 키워드가 여러 컬럼에 매칭되면 첫 번째 사용
- 필수 필드(email, name) 매핑 실패 시 HIGH 에러 로그

### 1-4. ResponseNormalizer.js

ADR-014의 Boolean 정규화 매핑 테이블을 구현하라.

```javascript
// 시그니처
const ResponseNormalizer = {
  normalizeBoolean(value) { ... },    // 다양한 예/아니오 → true/false
  normalizePhone(value) { ... },      // 공백/하이픈 정규화
  normalizeEmail(value) { ... },      // trim + lowercase
  normalizeRow(row) { ... }           // 전체 행 정규화
};
```

### 1-5. BatchRunner.js

ARCHITECTURE.md의 BatchRunner 패턴을 구현하라.

```javascript
// 시그니처
const BatchRunner = {
  run(items, processFn, options) { ... },  // 배치 실행, 4.5분 체크포인트
  saveCheckpoint(key, data) { ... },       // PropertiesService에 체크포인트 저장
  loadCheckpoint(key) { ... },             // 체크포인트 로드
  clearCheckpoint(key) { ... }             // 완료 후 정리
};
```

핵심 규칙:
- Date.now() 기준으로 4.5분(270,000ms) 초과 시 중단
- 체크포인트는 ScriptProperties에 JSON으로 저장
- 재개 시 체크포인트에서 이어서 처리

### 1-6. CacheHelper.js

ADR-012의 CacheService 전략을 래퍼로 구현하라.

```javascript
// 시그니처
const CacheHelper = {
  get(key) { ... },                   // JSON 파싱 포함
  set(key, value, ttl) { ... },       // JSON 직렬화 포함
  invalidate(key) { ... },            // 단일 키 무효화
  invalidatePrefix(prefix) { ... }    // 접두사 기반 무효화
};
```

핵심 규칙:
- CacheService.getScriptCache() 사용
- 100KB 초과 시 데이터를 분할하지 마라. 이유: 복잡도 대비 효용 낮음. 대신 캐시 스킵.

### 1-7. Jest 단위 테스트

`test/` 디렉토리에 아래 테스트를 작성하라:

- `ColumnMapper.test.js` — buildMap, mapRow (정상 매핑, 키워드 없는 헤더, 중복 키워드)
- `ResponseNormalizer.test.js` — normalizeBoolean (예/아니오/빈값 모든 변형), normalizePhone, normalizeEmail
- `GradeCalculator.test.js` — 빈 파일로 생성 (step5에서 구현)
- `FileNameParser.test.js` — 빈 파일로 생성 (step3에서 구현)

GAS 전역 객체(CacheService, PropertiesService, SpreadsheetApp 등)는 jest.fn()으로 mock하라.

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # ColumnMapper, ResponseNormalizer 테스트 전부 PASS
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

- SpreadsheetApp, DriveApp 등 GAS 전역 객체를 직접 import하지 마라. 이유: Jest에서 실행 불가. 전역 스코프에서 접근.
- 외부 npm 패키지를 추가하지 마라. 이유: clasp push 시 node_modules는 포함되지 않음.
- 다른 모듈(Scanner, Manager 등)의 로직을 이 step에서 구현하지 마라.
