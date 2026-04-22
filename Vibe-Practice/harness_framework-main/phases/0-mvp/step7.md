# Step 7: Frontend Shell

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — SPA 라우팅 패턴, google.script.run Promise 래퍼, Router.js 라우팅 테이블
- `/docs/UI_GUIDE.md` — 색상, 레이아웃, 컴포넌트 스펙
- `/docs/ADR.md` — ADR-011(SPA 시뮬레이션)
- `/gas/src/Router.js` — 서버 사이드 라우팅 (step4~6 산출물)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 7-1. Code.js (진입점)

```javascript
// 시그니처
function doGet(e) { ... }
// HtmlService.createHtmlOutputFromFile('index')
// .setTitle('Wave Academy 수강관리')
// .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)

function include(filename) { ... }
// HtmlService.createHtmlOutputFromFile(filename).getContent()
// CSS, JS 파일을 index.html에 인라인 포함하기 위한 헬퍼

function processRequest(action, params) { ... }
// 프론트엔드에서 google.script.run.processRequest()로 호출
// Router.route(action, params) 위임
```

### 7-2. index.html (SPA 셸)

```html
<!-- 구조 -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wave Academy 수강관리</title>
  <?!= include('css/style') ?>
</head>
<body>
  <header id="app-header">
    <!-- Wave Academy 수강관리 로고/타이틀 -->
    <!-- 네비게이션: 대시보드 | 수강생 | 과제 | 설정 -->
  </header>
  <main id="app">
    <!-- SPA 콘텐츠 영역 — 해시 라우팅으로 교체 -->
  </main>
  <div id="loading" class="hidden">로딩중...</div>
  <div id="toast" class="hidden"></div>
  <?!= include('js/api') ?>
  <?!= include('js/app') ?>
</body>
</html>
```

### 7-3. css/style.html

UI_GUIDE.md의 색상/컴포넌트 스펙을 CSS로 구현하라.

핵심 규칙:
- CSS Custom Properties로 디자인 토큰 정의 (UI_GUIDE.md 색상 테이블 기반)
- 모바일 대응: 320px 이상 반응형
- 테이블 헤더: 굵은 글씨, 배경 #f1f3f4
- 행 hover: 배경 #e8f0fe
- 버튼 Primary: #1a73e8 배경, white 텍스트
- 카드: white 배경, #dadce0 테두리, rounded 8px

```css
:root {
  --color-primary: #1a73e8;
  --color-success: #34a853;
  --color-danger: #ea4335;
  --color-warning: #fbbc04;
  --color-bg: #fafafa;
  --color-card: #ffffff;
  --color-text: #202124;
  --color-text-secondary: #5f6368;
  --color-border: #dadce0;
}
```

### 7-4. js/api.html

google.script.run을 Promise로 래핑하는 API 헬퍼.

```javascript
// 시그니처
const API = {
  call(action, params) { ... }
  // 반환: Promise
  // 내부: google.script.run
  //   .withSuccessHandler(resolve)
  //   .withFailureHandler(reject)
  //   .processRequest(action, params)
};
```

### 7-5. js/app.html

SPA 라우팅 + 공통 UI 로직.

```javascript
// 시그니처
const App = {
  init() { ... },            // hashchange 리스너 등록, 초기 라우팅
  navigate(hash) { ... },    // 해시 변경 → 뷰 로드
  showLoading() { ... },
  hideLoading() { ... },
  showToast(message, type) { ... },  // type: success/error/info
  render(containerId, html) { ... }  // innerHTML 교체
};

// 라우트 정의
const ROUTES = {
  '#dashboard': loadDashboard,
  '#students': loadStudentList,
  '#student': loadStudentDetail,    // #student?id=xxx
  '#assignments': loadAssignments,
  '#setup': loadSetup
};
```

각 load 함수는 이 step에서 stub으로 구현 (API.call → placeholder HTML 표시).
실제 페이지 구현은 step8에서 진행.

## Acceptance Criteria

```bash
cd gas && clasp push --force 2>&1 | tail -5   # 배포 에러 없음
```

추가 수동 검증: clasp push 후 웹앱 URL 접속 시 헤더 + 빈 대시보드 셸이 표시되어야 한다.

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

- 외부 CDN에서 CSS/JS 라이브러리를 로드하지 마라. 이유: iframe 샌드박스 CSP 제한.
- index.html에서 직접 google.script.run을 호출하지 마라. 이유: api.html의 Promise 래퍼를 통해서만 호출.
- innerHTML에 사용자 입력을 직접 삽입하지 마라. 이유: XSS 방지. textContent 사용하거나 이스케이프.
