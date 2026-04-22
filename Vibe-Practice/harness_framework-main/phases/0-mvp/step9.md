# Step 9: Integration Test

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/PRD.md` — 전체 기능 F1~F9, 38개 엣지케이스, 9개 에러 핸들링 테이블
- `/docs/ARCHITECTURE.md` — 전체 아키텍처
- `/gas/src/` — step0~8 전체 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 9-1. Jest 테스트 보강

기존 테스트 파일들의 커버리지를 확인하고 부족한 테스트를 추가하라:

- `test/FileNameParser.test.js` — 6패턴 A-F 정상 + 에지 케이스 (step3에서 작성됨, 누락 확인)
- `test/ColumnMapper.test.js` — 다양한 헤더 형식, 필수 필드 누락 케이스
- `test/ResponseNormalizer.test.js` — 전체 매핑 테이블 커버리지
- `test/GradeCalculator.test.js` — 경계값, 복합 조건

### 9-2. GAS 통합 테스트 함수

GAS 환경에서 실행하는 통합 테스트 함수들을 `gas/src/` 루트에 `TestRunner.js`로 생성:

```javascript
// 시그니처
function testSetup() { ... }
// Setup.createSheets() 실행 → 6개 시트 존재 확인 → _config 기본값 확인

function testScanFlow() { ... }
// DriveScanner.scan() → 파일 목록 확인 → SheetReader.readAndNormalize() → StudentManager.upsert()
// 실제 Google Drive 데이터로 전체 스캔 흐름 검증

function testAssignmentFlow() { ... }
// AssignmentManager.addDef() → check() → GradeCalculator.calculate()
// 과제 추가 → 완료 체크 → 학점 계산 전체 흐름

function testExportFlow() { ... }
// CsvExporter.export() → 파일 생성 확인

function testAuthFlow() { ... }
// Auth.withAuth() 권한 체크 — admin/viewer/unauthorized 각 케이스

function runAllTests() { ... }
// 위 모든 테스트 순차 실행, 결과 로그 출력
```

핵심 규칙:
- 통합 테스트는 실제 스프레드시트에서 실행 (GAS 환경)
- 테스트 전용 시트/데이터를 사용하고, 테스트 후 정리
- 각 테스트 함수는 독립적으로 실행 가능해야 함

### 9-3. 전체 빌드 검증

```bash
cd gas && npm test                    # Jest 단위 테스트 전체 PASS
cd gas && clasp push --force          # GAS 배포 성공
```

### 9-4. PRD 엣지케이스 매핑 확인

PRD.md의 38개 엣지케이스가 코드에서 처리되는지 체크리스트로 확인:

F1 엣지케이스 (14개):
- EC1-1: 빈 응답 시트 → SheetReader에서 빈 배열 반환
- EC1-2: 헤더만 있는 시트 → 빈 배열 반환
- EC1-3: 중복 수강생 → upsert 중복 체크
- ...각 EC에 대해 처리 코드 위치를 확인

처리되지 않는 엣지케이스가 있으면 해당 코드를 수정하라.

### 9-5. 코드 품질 검증

- 모든 파일이 800줄 이하인지 확인
- 함수가 50줄 이하인지 확인
- 하드코딩된 값이 없는지 확인 (Constants.js 사용)
- console.log가 남아있지 않은지 확인 (Logger.log 또는 ErrorHandler 사용)

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # 전체 Jest 테스트 PASS
cd gas && clasp push --force 2>&1 | tail -5   # 배포 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. PRD 엣지케이스 38개 전수 확인.
4. 결과에 따라 `phases/0-mvp/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 테스트를 통과시키기 위해 프로덕션 코드의 에러 처리를 제거하지 마라.
- 통합 테스트에서 마스터 시트의 실 데이터를 삭제하지 마라. 이유: 테스트 전용 데이터만 사용.
- 커버리지를 올리기 위해 의미 없는 테스트(항상 pass)를 추가하지 마라.
