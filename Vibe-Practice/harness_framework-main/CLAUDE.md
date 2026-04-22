# 프로젝트: Wave Academy 수강관리 시스템

## 기술 스택
- Google Apps Script (V8 런타임, 6분/실행 제한)
- HTML Service (웹앱 프론트엔드, iframe 샌드박스)
- Google Spreadsheet (마스터 데이터 저장소)
- Google Drive API — DriveApp (폴더 스캔, 파일 탐색)
- clasp CLI (로컬 개발 → push 배포)
- Jest (순수 로직 단위 테스트)

## 아키텍처 규칙
- CRITICAL: 원본 `.gsheet` 응답 파일은 **읽기 전용**. 절대 수정하지 않는다.
- CRITICAL: 모든 데이터 원천은 구글드라이브 스프레드시트. AI가 데이터를 "기억"으로 생성하지 않는다.
- CRITICAL: NotebookLM 연동은 이 시스템 범위 밖. 정제 스프레드시트 생성까지가 범위.
- CRITICAL: 삭제는 soft delete (`is_active = false`). 물리적 삭제 금지.
- CRITICAL: 마스터 시트 쓰기 시 반드시 `LockService.getScriptLock()` 사용.
- 컬럼 매핑은 인덱스가 아닌 **헤더 텍스트 키워드** 기반.
- 6분 실행 제한 → 대량 작업은 `BatchRunner.js`로 분할.
- 에러 처리는 `ErrorHandler.js` 중앙 처리. 개별 파일 실패가 전체를 중단시키면 안 됨.
- 로컬 파일 확장자: `.js` (clasp 기본, IDE 지원)

## 데이터 원천
- 구글드라이브 계정: `waveainetworks@gmail.com`
- 수강신청 응답: `내 드라이브/Wave_class 수강신청/` (월별·클래스별 `.gsheet`)
- 통합신청서 응답: `내 드라이브/` 루트
- 파일명 패턴: `({월} {대상} Class#{N}) {강의명}(응답).gsheet` (변형 6종 — ADR-005)
- NotebookLM 계정: 별도 (Claude Code MCP로 연동)
- 마스터 시트 위치: `Wave/행정/수강관리/` 하위

## 분류 체계
- 카테고리: 교회강의 / Wave Academy / 자격증과정 / 외부강의
- 클래스: Class#1(파운데이션) / Class#2(심화) / Class#3(활용)
- 대상: 목회자 / 일반 / 교회(성도)
- 지역: 본부 / 부산 / 충남 / 꿈별 등

## 개발 프로세스
- CRITICAL: 코드 변경 전 의도 파악 → 영향 범위 분석 → 변경 설계 3단계 수행
- clasp CLI로 로컬 개발 → `clasp push` 배포
- 커밋 메시지: conventional commits (feat:, fix:, docs:, refactor:)

## 명령어
```bash
# 배포
clasp push

# 테스트
npm test

# 원격 코드 가져오기
clasp pull

# 스크립트 에디터 열기
clasp open
```

## 참조 문서
| 문서 | 경로 | 내용 |
|------|------|------|
| PRD | `docs/PRD.md` | 9개 기능 명세, 38개 엣지케이스, 에러 핸들링 |
| 아키텍처 | `docs/ARCHITECTURE.md` | 파일 구조, 데이터 흐름, 스키마, 19개 API, 캐싱 전략 |
| ADR | `docs/ADR.md` | 14개 아키텍처 결정 기록 |
| UI 가이드 | `docs/UI_GUIDE.md` | 색상, 레이아웃, 컴포넌트 |
