# Step 8: Frontend Pages

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/UI_GUIDE.md` — 대시보드 와이어프레임, 수강생 상세 와이어프레임, 컴포넌트 스펙
- `/docs/ARCHITECTURE.md` — Router.js 라우팅 테이블 (19개 API 엔드포인트)
- `/docs/PRD.md` — F1~F9 전체 기능 명세, 엣지케이스
- `/gas/src/html/` — step7 산출물 (index.html, style.html, api.html, app.html)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 8-1. dashboard.html

UI_GUIDE.md의 대시보드 와이어프레임을 구현하라.

구성요소:
1. **카테고리 탭**: 교회강의 / Wave Academy / 자격증과정 / 외부강의 (+ 전체)
2. **클래스 카드**: 각 카테고리 내 Class#1/2/3별 요약 카드
   - 수강 인원, 이수 인원, 이수율 (%)
   - 이수율에 따른 상단 바 색상 (green >= 70%, yellow >= 40%, red < 40%)
3. **수강생 테이블**: 이름 | 클래스 | 과제완료율 | 이수 | 상세 →
   - 필터: 카테고리, 클래스, 대상, 지역, 기수, 이수상태
   - 검색: 이름/이메일/교회명
   - 페이지네이션
4. **액션 버튼**: [스캔 실행] [내보내기] (admin only)

```javascript
function loadDashboard() {
  // 1. API.call('getDashboard') → 통계 데이터
  // 2. API.call('getStudents', filters) → 수강생 목록
  // 3. HTML 렌더링
}
```

### 8-2. student-detail.html

UI_GUIDE.md의 수강생 상세 와이어프레임을 구현하라.

구성요소:
1. **기본 정보**: 이름, 소속, 클래스, 직분, 연락처(마스킹 가능)
2. **상태**: 입금 ✅/❌, 수강완료 ✅/❌, 이수 Pass/Fail/진행중
3. **과제 현황**: 체크리스트 형태 (☑/☐ + 과제명 + 제출일)
4. **수정 폼**: admin만 표시 — 입금여부, 수강완료, 과제 체크 토글

```javascript
function loadStudentDetail(studentId) {
  // 1. API.call('getStudent', { id: studentId })
  // 2. API.call('getAssignments', { studentId })  // 해당 학생의 과제 현황
  // 3. HTML 렌더링
}
```

### 8-3. assignment.html

과제 관리 페이지 (admin only).

구성요소:
1. **과제 정의 목록**: 카테고리/클래스별 필터, 과제명, 주차, 배점, 마감일
2. **과제 추가/수정 폼**: 모달 또는 인라인
3. **일괄 체크**: 특정 과제에 대해 다수 수강생 일괄 완료 처리

### 8-4. setup.html

초기 설정 페이지 (admin only).

구성요소:
1. **스캔 폴더 설정**: 폴더 ID 입력/수정
2. **관리자/열람자 이메일 설정**
3. **이수 기준 설정**: PASS_THRESHOLD
4. **자동 스캔 설정**: 활성화 토글 + 주기
5. **기수 관리**: 현재 기수 선택
6. **로그 뷰어**: 최근 에러/경고 로그 표시

### 8-5. 검색/필터 공통 컴포넌트

app.html에 검색/필터 공통 함수 추가:

```javascript
// 필터 UI 생성 (드롭다운)
function createFilterBar(containerId, options) { ... }
// options: [{ key, label, values }]

// 검색 바
function createSearchBar(containerId, onSearch) { ... }

// 페이지네이션
function createPagination(containerId, { total, page, limit, onChange }) { ... }
```

핵심 규칙:
- 모든 사용자 입력은 textContent 또는 이스케이프 처리 (XSS 방지)
- admin 전용 기능은 role 체크 후 표시/숨김
- 빈 데이터 상태 처리 (수강생 0명, 과제 0개 등)
- 로딩 상태 표시 (API 호출 중)
- 에러 상태 표시 (API 실패 시 toast)

## Acceptance Criteria

```bash
cd gas && clasp push --force 2>&1 | tail -5   # 배포 에러 없음
```

추가 수동 검증: 웹앱 URL 접속 후:
1. 대시보드에 카테고리 탭 + 클래스 카드 표시
2. 수강생 테이블에 필터/검색/페이지네이션 동작
3. 수강생 클릭 → 상세 페이지 이동
4. admin으로 접속 시 스캔/내보내기/과제관리/설정 접근 가능

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
   - UI_GUIDE.md 색상/레이아웃을 따르는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 외부 CSS 프레임워크(Bootstrap, Tailwind 등)를 사용하지 마라. 이유: iframe 샌드박스 내 CDN 로드 불가, 번들 사이즈 증가.
- innerHTML에 사용자 입력값을 직접 넣지 마라. 이유: XSS 취약점. 반드시 이스케이프 함수 사용.
- 페이지별로 별도 google.script.run 호출을 만들지 마라. 이유: api.html의 API.call() 단일 인터페이스 사용.
