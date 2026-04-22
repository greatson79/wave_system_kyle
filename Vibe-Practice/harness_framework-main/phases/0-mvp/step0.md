# Step 0: Project Setup

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

## 작업

### 0-1. clasp 프로젝트 생성

```bash
mkdir -p gas
cd gas
clasp create --type webapp --title "Wave Academy 수강관리"
```

생성된 `.clasp.json`과 `appsscript.json`을 확인하라.

### 0-2. appsscript.json 설정

```json
{
  "timeZone": "Asia/Seoul",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "webapp": {
    "executeAs": "USER_DEPLOYING",
    "access": "ANYONE"
  }
}
```

### 0-3. 디렉토리 구조 생성

ARCHITECTURE.md의 디렉토리 구조를 그대로 따라 빈 파일들을 생성하라:

```
gas/
├── src/
│   ├── Code.js
│   ├── Router.js
│   ├── Auth.js
│   ├── Setup.js
│   ├── scanners/
│   │   ├── DriveScanner.js
│   │   └── SheetReader.js
│   ├── parsers/
│   │   ├── FileNameParser.js
│   │   └── ResponseNormalizer.js
│   ├── managers/
│   │   ├── StudentManager.js
│   │   ├── AssignmentManager.js
│   │   └── GradeCalculator.js
│   ├── exporters/
│   │   └── CsvExporter.js
│   ├── utils/
│   │   ├── ColumnMapper.js
│   │   ├── BatchRunner.js
│   │   ├── ErrorHandler.js
│   │   ├── CacheHelper.js
│   │   └── Constants.js
│   ├── triggers/
│   │   └── TimeTrigger.js
│   └── html/
│       ├── index.html
│       ├── dashboard.html
│       ├── student-detail.html
│       ├── assignment.html
│       ├── setup.html
│       ├── css/
│       │   └── style.html
│       └── js/
│           ├── app.html
│           └── api.html
├── test/
│   ├── FileNameParser.test.js
│   ├── ColumnMapper.test.js
│   ├── GradeCalculator.test.js
│   └── ResponseNormalizer.test.js
├── .clasp.json
├── appsscript.json
├── package.json
└── jest.config.js
```

각 `.js` 파일에는 모듈 헤더 주석만 넣어라. 예:
```javascript
// DriveScanner.js — Google Drive 폴더 스캔
```

### 0-4. package.json

```json
{
  "name": "wave-academy",
  "version": "0.1.0",
  "scripts": {
    "test": "jest",
    "push": "clasp push",
    "pull": "clasp pull",
    "open": "clasp open"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

### 0-5. jest.config.js

Jest가 `test/` 디렉토리의 `.test.js` 파일만 실행하도록 설정하라. GAS 전역 객체(`SpreadsheetApp`, `DriveApp` 등)는 테스트에서 mock 처리할 것이므로 별도 setup 파일은 아직 불필요.

### 0-6. .clasp.json rootDir 설정

clasp push가 `gas/src/` 디렉토리를 루트로 사용하도록 `.clasp.json`에 `"rootDir": "src"` 추가.

### 0-7. npm install

```bash
cd gas && npm install
```

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -3   # "No tests found" 또는 테스트 스위트 0 — 에러 없음
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

- 이 step에서 비즈니스 로직을 구현하지 마라. 이유: 다음 step에서 구현.
- `gas/src/` 외부에 소스 파일을 만들지 마라. 이유: clasp push 범위 밖.
- `.clasp.json`의 scriptId를 하드코딩하지 마라. 이유: clasp create가 자동 생성.
