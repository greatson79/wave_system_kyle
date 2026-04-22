# Step 2: Auth & Config

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 접근 제어 매트릭스, _config 시트 스키마, 초기 설정 흐름
- `/docs/ADR.md` — ADR-007(soft delete), ADR-009(LockService), ADR-010(마스킹)
- `/gas/src/utils/Constants.js` — 상수 정의
- `/gas/src/utils/ErrorHandler.js` — 에러 처리

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 2-1. Auth.js

이메일 기반 역할 인증/인가 모듈.

```javascript
// 시그니처
const Auth = {
  getCurrentUser() { ... },           // Session.getActiveUser().getEmail()
  getRole(email) { ... },             // _config의 ADMIN_EMAILS/VIEWER_EMAILS 대조 → 'admin'/'viewer'/null
  isAdmin(email) { ... },
  isAuthorized(email) { ... },
  withAuth(requiredRole, fn) { ... }, // 고차함수: 권한 체크 후 fn 실행, 미인가 시 에러
  maskPhone(phone) { ... },           // 010-1234-5678 → 010-****-5678
  maskEmail(email) { ... }            // greatson79@gmail.com → gre***@gmail.com
};
```

핵심 규칙:
- `withAuth`는 ARCHITECTURE.md의 접근 제어 매트릭스를 강제하는 핵심 미들웨어
- viewer 역할에게 반환되는 데이터는 반드시 phone, email 마스킹 적용 (ADR-010)
- 인증 실패 시 CRITICAL 에러 로그

### 2-2. Setup.js

초기 설정 및 시트 생성 모듈.

```javascript
// 시그니처
const Setup = {
  initConfig() { ... },              // _config 시트 존재 확인 → 없으면 생성 + 기본값 세팅
  createSheets() { ... },            // 6개 시트 생성 (수강생_마스터, 과제_정의, 과제_현황, _config, _scan_history, _log)
  getConfig(key) { ... },            // _config에서 값 조회 (캐시 활용)
  updateConfig(key, value) { ... },  // _config 값 변경 (admin only)
  getConfigAll() { ... },            // 전체 설정 조회
  isInitialized() { ... }            // 초기 설정 완료 여부
};
```

핵심 규칙:
- createSheets()는 멱등(idempotent)해야 한다 — 이미 존재하는 시트는 스킵
- 각 시트 생성 시 헤더 행을 ARCHITECTURE.md 데이터 모델의 필드명으로 설정
- 마스터 시트 위치: _config의 MASTER_SHEET_ID로 지정된 스프레드시트
- CRITICAL: 마스터 시트 쓰기 시 반드시 LockService.getScriptLock() 사용 (ADR-009)
- getConfig()는 CacheHelper를 활용하여 캐싱 (TTL: 30분)

### 2-3. _config 기본값

Setup.initConfig()가 세팅하는 기본값:

| key | 기본값 | 설명 |
|-----|--------|------|
| SCAN_FOLDER_IDS | "" | 스캔 대상 폴더 ID (쉼표 구분) |
| ADMIN_EMAILS | (배포자 이메일) | 관리자 이메일 (쉼표 구분) |
| VIEWER_EMAILS | "" | 열람자 이메일 (쉼표 구분) |
| PASS_THRESHOLD | "80" | 이수 기준 완료율 (%) |
| MASTER_SHEET_ID | (현재 스프레드시트 ID) | 마스터 시트 ID |
| AUTO_SCAN_ENABLED | "false" | 자동 스캔 활성화 |
| AUTO_SCAN_INTERVAL_HOURS | "24" | 자동 스캔 주기 (시간) |
| CURRENT_COHORT | "2026-04" | 현재 기수 |
| CATEGORIES | "교회강의,Wave Academy,자격증과정,외부강의" | 카테고리 목록 |
| CLASS_LEVELS | "Class #1,Class #2,Class #3" | 클래스 목록 |
| TARGETS | "목회자,일반" | 대상 목록 |
| REGIONS | "본부,부산,충남,꿈별" | 지역 목록 |

## Acceptance Criteria

```bash
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

- _config에 비밀번호나 API 키를 저장하지 마라. 이유: 스프레드시트는 공유될 수 있음.
- createSheets()에서 기존 시트의 데이터를 삭제하지 마라. 이유: 멱등성 위반, 데이터 손실 위험.
- Auth.withAuth 없이 직접 Setup.updateConfig을 호출하지 마라. 이유: admin 권한 검증 누락.
