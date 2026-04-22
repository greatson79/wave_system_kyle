# 아키텍처: Wave Academy 수강관리 시스템

## 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| 런타임 | Google Apps Script (V8) | 6분/실행 제한, 동시 실행 30 |
| 프론트엔드 | HTML Service (iframe sandbox) | google.script.run으로 서버 통신 |
| 데이터 저장 | Google Spreadsheet | 마스터 시트 + 과제 시트 분리 |
| 호스팅 | Google Apps Script 웹앱 | 자동 HTTPS, 배포 URL 고정 |
| 인증 | Google 계정 (exec as me, access by allow-list) | 이메일 기반 역할(admin/viewer) |
| 개발도구 | clasp CLI | 로컬 .js → push 배포 |
| 테스트 | Jest + GAS 테스트 함수 | 순수 로직 Jest, 통합 GAS |

## 디렉토리 구조

```
gas/
├── src/
│   ├── Code.js              # 진입점: doGet(), include()
│   ├── Router.js             # API 라우터: route(action, params)
│   ├── Auth.js               # 인증/인가: withAuth(), getRole()
│   ├── Setup.js              # 초기 설정: initConfig(), createSheets()
│   ├── scanners/
│   │   ├── DriveScanner.js   # 구글드라이브 폴더 스캔
│   │   └── SheetReader.js    # 스프레드시트 데이터 읽기
│   ├── parsers/
│   │   ├── FileNameParser.js # 파일명 패턴 파싱 (6 패턴 A-F)
│   │   └── ResponseNormalizer.js # 폼 응답 정규화 (불린, 공백 등)
│   ├── managers/
│   │   ├── StudentManager.js # 수강생 CRUD (soft delete)
│   │   ├── AssignmentManager.js # 과제 정의/현황 관리
│   │   └── GradeCalculator.js   # 학점/이수 계산
│   ├── exporters/
│   │   └── CsvExporter.js    # NotebookLM용 CSV/JSON 내보내기
│   ├── utils/
│   │   ├── ColumnMapper.js   # 헤더 텍스트 기반 컬럼 매핑
│   │   ├── BatchRunner.js    # 6분 타임아웃 대응 배치 처리
│   │   ├── ErrorHandler.js   # 에러 분류/로깅
│   │   ├── CacheHelper.js    # CacheService 래퍼
│   │   └── Constants.js      # 상수 정의
│   ├── triggers/
│   │   └── TimeTrigger.js    # 자동 스캔 트리거
│   └── html/
│       ├── index.html        # SPA 셸
│       ├── dashboard.html    # 대시보드 뷰
│       ├── student-detail.html # 수강생 상세 뷰
│       ├── assignment.html   # 과제 관리 뷰
│       ├── setup.html        # 초기 설정 뷰
│       ├── css/
│       │   └── style.html    # CSS (include용 html)
│       └── js/
│           ├── app.html      # SPA 라우팅 + 공통 로직
│           └── api.html      # google.script.run Promise 래퍼
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

## 데이터 모델

### 수강생_마스터 (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | String | ✅ | UUID v4 |
| timestamp | DateTime | ✅ | 원본 폼 제출 시각 |
| email | String | ✅ | 이메일 주소 |
| name | String | ✅ | 성함 |
| phone | String | ✅ | 연락처 |
| church | String | ✅ | 교회/기관명 |
| position | String | ⬜ | 직분 |
| category | String | ✅ | 교회강의/Wave Academy/자격증과정/외부강의 |
| class_level | String | ✅ | Class #1 / Class #2 / Class #3 |
| target | String | ✅ | 목회자/일반 |
| region | String | ⬜ | 부산/충남/꿈별 등 |
| cohort | String | ✅ | 기수 (예: 2026-03) |
| prerequisite_check | Boolean | ⬜ | 선수학습 확인 |
| ai_usage_freq | String | ⬜ | AI 사용 빈도 |
| goal | String | ⬜ | 수강 목표 |
| payment_status | Boolean | ✅ | 입금 여부 |
| payment_name | String | ⬜ | 입금자명 |
| openchat_joined | Boolean | ⬜ | 오픈채팅방 참여 |
| privacy_agreed | Boolean | ✅ | 개인정보 동의 |
| course_completed | Boolean | ✅ | 수강완료 여부 |
| grade | String | ✅ | Pass/Fail/진행중 |
| assignment_completion_rate | Number | ✅ | 과제 완료율 (0~100) |
| source_file | String | ✅ | 원본 파일명 |
| source_sheet_id | String | ✅ | 원본 시트 ID |
| is_active | Boolean | ✅ | 활성 여부 (soft delete) |
| created_at | DateTime | ✅ | 레코드 생성 시각 |
| updated_at | DateTime | ✅ | 최종 수정 시각 |

### 과제_정의 (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | String | ✅ | 과제 고유 ID |
| category | String | ✅ | 카테고리 |
| class_level | String | ✅ | 대상 클래스 |
| week | Number | ✅ | 주차 |
| title | String | ✅ | 과제 제목 |
| description | String | ⬜ | 과제 설명 |
| due_date | Date | ⬜ | 마감일 |
| weight | Number | ✅ | 배점 비중 (%) |
| is_active | Boolean | ✅ | 활성 여부 |

### 과제_현황 (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | String | ✅ | 고유 ID |
| student_id | String | ✅ | 수강생 ID (FK) |
| assignment_id | String | ✅ | 과제 ID (FK) |
| status | String | ✅ | 완료/미완료/지각 |
| submitted_at | DateTime | ⬜ | 제출 시각 |
| checked_by | String | ⬜ | 확인자 이메일 |
| note | String | ⬜ | 비고 |

### _config (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| key | String | ✅ | 설정 키 |
| value | String | ✅ | 설정 값 |
| description | String | ⬜ | 설명 |

**Config keys:**

| 키 | 설명 | 기본값 |
|----|------|--------|
| SCAN_FOLDER_IDS | 스캔 대상 구글드라이브 폴더 ID 목록 (JSON 배열) | `[]` |
| ADMIN_EMAILS | 관리자 이메일 목록 (JSON 배열) | `["waveainetworks@gmail.com"]` |
| VIEWER_EMAILS | 열람자 이메일 목록 (JSON 배열) | `[]` |
| PASS_THRESHOLD | 이수 기준 과제 완료율 (%) | `60` |
| MASTER_SHEET_ID | 마스터 스프레드시트 ID | 자동 생성 |
| AUTO_SCAN_ENABLED | 자동 스캔 활성화 여부 | `true` |
| AUTO_SCAN_INTERVAL_HOURS | 자동 스캔 주기 (시간) | `24` |
| CURRENT_COHORT | 현재 기수 | `2026-03` |
| CATEGORIES | 카테고리 목록 (JSON 배열) | `["교회강의","Wave Academy","자격증과정","외부강의"]` |
| CLASS_LEVELS | 클래스 레벨 목록 (JSON 배열) | `["Class#1","Class#2","Class#3"]` |
| TARGETS | 대상 목록 (JSON 배열) | `["목회자","일반","교회(성도)"]` |
| REGIONS | 지역 목록 (JSON 배열) | `["본부","부산","충남","꿈별"]` |

### _scan_history (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | String | ✅ | 스캔 ID |
| started_at | DateTime | ✅ | 시작 시각 |
| completed_at | DateTime | ⬜ | 완료 시각 |
| files_found | Number | ✅ | 발견 파일 수 |
| new_students | Number | ✅ | 신규 수강생 수 |
| updated_students | Number | ✅ | 업데이트 수강생 수 |
| skipped | Number | ✅ | 스킵 수 |
| errors | Number | ✅ | 에러 수 |
| status | String | ✅ | success/partial/failed |
| error_details | String | ⬜ | 에러 상세 |

### _log (시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| timestamp | DateTime | ✅ | 로그 시각 |
| severity | String | ✅ | CRITICAL/HIGH/MEDIUM/LOW |
| module | String | ✅ | 모듈명 |
| message | String | ✅ | 로그 메시지 |
| details | String | ⬜ | 상세 JSON |

## 데이터 흐름

### 흐름 1: 스캔 (Google Drive → 마스터 시트)

```
[DriveScanner: 폴더 스캔]
    │ .gsheet 파일 목록
    ▼
[FileNameParser: 파일명 파싱]
    │ category, class_level, target, region 추출
    ▼
[SheetReader: 시트 데이터 읽기]
    │ 원본 헤더 + 행 데이터
    ▼
[ColumnMapper: 헤더→필드 매핑]
    │ 정규화된 데이터 배열
    ▼
[ResponseNormalizer: 불린/공백 정규화]
    │ 클린 데이터
    ▼
[StudentManager: 중복 체크 + upsert]
    │ email+class_level+cohort 기준
    ▼
[마스터 시트 기록]
```

### 흐름 2: 과제 체크

```
[AssignmentManager: 과제 정의 조회]
    │ category+class_level 기준
    ▼
[과제_현황: 제출 상태 기록]
    │ student_id + assignment_id
    ▼
[GradeCalculator: 완료율 재계산]
    │ weight 기반 가중 평균
    ▼
[수강생_마스터: assignment_completion_rate 업데이트]
```

### 흐름 3: 학점 계산

```
[GradeCalculator: 이수 판정]
    │ assignment_completion_rate >= PASS_THRESHOLD?
    │ AND course_completed == true?
    │ AND payment_status == true?
    ▼
[수강생_마스터: grade 업데이트]
    │ Pass / Fail / 진행중
```

## ColumnMapper 필드 매핑

원본 폼마다 헤더 텍스트가 다를 수 있으므로 키워드 기반 매핑을 사용한다.

| 필드명 | 매칭 키워드 (contains, case-insensitive) |
|--------|----------------------------------------|
| timestamp | 타임스탬프, timestamp |
| email | 이메일, email |
| name | 성함, 이름, name |
| phone | 연락처, 전화, phone |
| church | 교회, 기관, church |
| position | 직분, position |
| class_level | 클래스, class, 희망 |
| prerequisite_check | 선수, prerequisite |
| ai_usage_freq | AI, 사용빈도 |
| goal | 목표, goal |
| payment_status | 입금여부, payment |
| payment_name | 입금자, payer |
| openchat_joined | 오픈채팅, openchat |
| privacy_agreed | 개인정보, privacy |

**매칭 우선순위:** 정확 일치 > contains 일치 > 첫 번째 매칭
**매칭 실패 시:** 해당 필드 null + 로그 기록 (경고, 에러 아님)

## 접근 제어

| 기능 | admin | viewer |
|------|-------|--------|
| 대시보드 조회 | ✅ | ✅ |
| 수강생 목록 조회 | ✅ | ✅ (마스킹) |
| 수강생 상세 조회 | ✅ | ✅ (마스킹) |
| 수강생 추가/수정 | ✅ | ❌ |
| 수강생 삭제 (soft) | ✅ | ❌ |
| 과제 정의 CRUD | ✅ | ❌ |
| 과제 현황 체크 | ✅ | ❌ |
| 스캔 실행 | ✅ | ❌ |
| 내보내기 | ✅ | ❌ |
| 설정 변경 | ✅ | ❌ |
| 로그 조회 | ✅ | ✅ |

**마스킹 규칙 (viewer):**
- phone: `010-****-1234` (중간 4자리 마스킹)
- email: `gre***@gmail.com` (로컬 파트 3자 이후 마스킹)

### 권한 체크 미들웨어 패턴

```javascript
function withAuth(requiredRole, handler) {
  return function() {
    var email = Session.getActiveUser().getEmail();
    var role = getUserRole(email);

    if (role === 'none') {
      return { error: 'ACCESS_DENIED', message: '접근 권한이 없습니다' };
    }
    if (requiredRole === 'admin' && role !== 'admin') {
      return { error: 'ADMIN_REQUIRED', message: '관리자 권한이 필요합니다' };
    }

    return handler.apply(this, arguments);
  };
}
```

## 에러 처리 아키텍처

모든 `.js` 파일의 public 함수는 try-catch로 감싸고 `ErrorHandler`를 호출한다.

| 심각도 | 처리 | 예시 |
|--------|------|------|
| CRITICAL | 즉시 중단 + _log 기록 + UI 알림 | 마스터 시트 접근 불가, 인증 실패 |
| HIGH | 해당 작업 중단 + _log 기록 | 개별 파일 읽기 실패, 데이터 무결성 위반 |
| MEDIUM | 항목 스킵 + 경고 로그 | 파일명 파싱 실패, 컬럼 매핑 불일치 |
| LOW | 로그만 기록 | 선택 필드 누락, 캐시 미스 |

**핵심 원칙:** 개별 파일/항목 실패가 전체 프로세스를 중단시키면 안 된다. HIGH 이하 에러는 해당 항목만 스킵하고 나머지를 계속 처리한다.

## 제한사항 대응

| 제한 | 값 | 대응 |
|------|-----|------|
| 실행 시간 | 6분/실행 | BatchRunner: 4.5분 체크포인트 → 트리거 체인 |
| 동시 실행 | 30개 | LockService로 쓰기 직렬화 |
| 셀 수 | 1000만/스프레드시트 | 기수별 시트 분리 고려 |
| 일일 트리거 | 20개/사용자 | 트리거 수 최소화 (1개 자동스캔) |
| URL Fetch | 20,000/일 | 해당 없음 (외부 API 미사용) |
| 캐시 | 100KB/항목, 25MB/전체 | 데이터 분할 캐싱 |

### BatchRunner 패턴

```javascript
function batchProcess(items, processFn) {
  const START = Date.now();
  const LIMIT_MS = 4.5 * 60 * 1000; // 4.5분
  let processed = 0;
  
  for (const item of items) {
    if (Date.now() - START > LIMIT_MS) {
      // 체크포인트 저장 후 트리거 체인
      saveCheckpoint(items.slice(processed));
      ScriptApp.newTrigger('resumeBatch')
        .timeBased().after(1000).create();
      return { status: 'continuing', processed };
    }
    processFn(item);
    processed++;
  }
  return { status: 'complete', processed };
}
```

## Router.js 라우팅 테이블

| action | 메서드 | 핸들러 | 권한 |
|--------|--------|--------|------|
| getDashboard | GET | DashboardController.get | all |
| getStudents | GET | StudentManager.list | all |
| getStudent | GET | StudentManager.get | all |
| addStudent | POST | StudentManager.add | admin |
| updateStudent | POST | StudentManager.update | admin |
| deleteStudent | POST | StudentManager.softDelete | admin |
| getAssignments | GET | AssignmentManager.listDefs | all |
| addAssignment | POST | AssignmentManager.addDef | admin |
| updateAssignment | POST | AssignmentManager.updateDef | admin |
| checkAssignment | POST | AssignmentManager.check | admin |
| calculateGrades | POST | GradeCalculator.calcAll | admin |
| runScan | POST | DriveScanner.scan | admin |
| exportData | GET | CsvExporter.export | admin |
| getConfig | GET | Setup.getConfig | admin |
| updateConfig | POST | Setup.updateConfig | admin |
| getLogs | GET | LogViewer.get | all |
| getFilterOptions | GET | FilterController.options | all |
| searchStudents | GET | StudentManager.search | all |
| getCohorts | GET | CohortManager.list | all |

## SPA 라우팅 패턴

```javascript
// html/js/app.html
const routes = {
  '#dashboard': 'dashboard',
  '#students': 'student-list',
  '#student/:id': 'student-detail',
  '#assignments': 'assignment',
  '#setup': 'setup',
  '#logs': 'logs'
};

function navigate(hash) {
  const view = routes[hash] || 'dashboard';
  google.script.run
    .withSuccessHandler(html => {
      document.getElementById('app').innerHTML = html;
    })
    .getView(view);
}
```

### google.script.run Promise 래퍼

```javascript
// html/js/api.html
function callServer(functionName, ...args) {
  return new Promise(function(resolve, reject) {
    google.script.run
      .withSuccessHandler(resolve)
      .withFailureHandler(reject)
      [functionName](...args);
  });
}
```

## CacheService 전략

`CacheService.getScriptCache()`를 이용한 서버 사이드 캐시.

| 데이터 | TTL | 무효화 시점 |
|--------|-----|------------|
| 대시보드 통계 | 5분 | 스캔 완료, 학점 계산 후 |
| 수강생 목록 | 5분 | CRUD 작업 후 |
| 과제 정의 | 10분 | 과제 CRUD 후 |
| 설정값 | 30분 | 설정 변경 후 |

**캐시 키 패턴:** `{데이터타입}_{필터해시}` (예: `dashboard_all`, `students_WA_C1_p1`)

## Boolean 정규화

| 입력값 | 정규화 결과 |
|--------|------------|
| "예", "네", "Yes", "yes", "Y", "TRUE", "true", "1", "O", "o", "확인" | true |
| "아니오", "아니요", "No", "no", "N", "FALSE", "false", "0", "X", "x" | false |
| "", null, undefined | false |

## 초기 설정 흐름

```
[Setup.html: 관리자 접속]
    │
    ▼ 마스터 시트 존재 확인
[없음] → createSheets() → 6개 시트 생성
    │
    ▼ _config 초기값 세팅
[SCAN_FOLDER_IDS 입력]
    │
    ▼ ADMIN_EMAILS 설정
[첫 스캔 실행]
    │
    ▼ 완료
[대시보드로 이동]
```

## 배포 구조

```
[로컬 개발 환경]
    │
    ▼ clasp push
[Google Apps Script 프로젝트]
    │
    ▼ 배포 (Deploy as web app)
[웹앱 URL]
    │
    ▼ 구글 계정 인증
[관리자/열람자 접근]
```

**배포 설정:**
- Execute as: 스크립트 소유자 (waveainetworks@gmail.com)
- Who has access: 특정 사용자 (ADMIN_EMAILS + VIEWER_EMAILS)
