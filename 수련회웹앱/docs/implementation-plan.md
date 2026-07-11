# 구현 실행 계획

## 1. 목적

이 문서는 `docs/requirement.md`부터 페이지별 `plan.md`까지 작성된 기획 문서를 실제 웹앱 구현 순서로 정리한다. MVP는 서버, 로그인, 외부 데이터베이스 없이 Vite + React + TypeScript 기반 단일 브라우저 웹앱으로 구현한다.

## 2. 구현 전제

- 기술 스택: Vite + React + TypeScript
- 상태 관리: React Context + `useReducer`
- 저장 방식: `localStorage` 단일 키 `retreat-game:v1:state`
- 결과 다운로드: 이미지 다운로드 우선
- PDF 다운로드, 관리자 화면, 로그인, 서버 저장, 실시간 동기화는 MVP 이후로 분리한다.
- 모든 화면은 모바일 브라우저 우선으로 구현한다.

## 3. 문서 참조 순서

구현자는 아래 순서로 문서를 읽는다.

1. `docs/requirement.md`
2. `docs/prd.md`
3. `docs/userflow.md`
4. `docs/database.md`
5. `docs/common-modules.md`
6. `docs/usecases/*/spec.md`
7. `docs/pages/*/plan.md`

## 4. 구현 단계

### 4.1 프로젝트 초기화

- Vite + React + TypeScript 프로젝트를 생성한다.
- 기본 라우팅 또는 단계 기반 화면 전환 구조를 만든다.
- 테스트 도구는 최소 단위 테스트와 브라우저 확인이 가능한 수준으로 준비한다.
- 앱 이름과 문서 기준 경로를 README에 정리한다.

### 4.2 공통 모듈 선구현

`docs/common-modules.md`를 기준으로 페이지에 의존하지 않는 모듈을 먼저 만든다.

- 타입 정의
- 기본 콘텐츠 설정
- validation 유틸
- storage 모듈
- stageManager
- teamBuilder
- itemMatcher
- missionEngine
- reflectionManager
- exporter

이 단계가 끝나야 페이지 개발 중 공통 로직 중복과 충돌을 줄일 수 있다.

### 4.3 전역 상태 구현

- Context + `useReducer` 기반 전역 상태를 만든다.
- `docs/database.md`의 상태 스키마를 TypeScript 타입으로 옮긴다.
- 상태 변경 시 `localStorage`에 저장한다.
- 앱 시작 시 저장 상태를 검증하고 복구한다.
- 손상된 저장 데이터는 새 게임 시작 흐름으로 처리한다.

### 4.4 페이지 구현 순서

페이지는 아래 순서로 구현한다.

1. `docs/pages/009-session-recovery/plan.md`
2. `docs/pages/001-setup/plan.md`
3. `docs/pages/002-team-prep/plan.md`
4. `docs/pages/003-personality-stage/plan.md`
5. `docs/pages/004-item-stage/plan.md`
6. `docs/pages/005-bible-mission-stage/plan.md`
7. `docs/pages/006-final-mission-stage/plan.md`
8. `docs/pages/007-reflection/plan.md`
9. `docs/pages/008-result-export/plan.md`

세션 복구는 독립 화면이라기보다 앱 시작 게이트와 저장 계층에 가깝기 때문에 가장 먼저 구현한다.

### 4.5 콘텐츠 연결

- 기본 주제는 `공동체`로 둔다.
- 기본 대상은 중고등부로 둔다.
- 성향 질문 5개, 아이템 6개, 3단계 퀴즈 5개, 4단계 최종 미션 1개를 콘텐츠 설정 파일에 분리한다.
- 화면 컴포넌트는 콘텐츠 내용을 직접 하드코딩하지 않고 설정 데이터를 참조한다.

### 4.6 결과 이미지 다운로드

- `docs/usecases/008-result-export/spec.md`를 기준으로 결과 미리보기 영역을 만든다.
- 팀 이름, 주제 키워드, 미션 요약, 팀별 소감을 포함한다.
- 긴 텍스트가 이미지에서 잘리지 않도록 미리보기 레이아웃을 고정 폭과 자동 높이 중심으로 설계한다.
- 이미지 변환 실패 시 재시도할 수 있게 한다.

## 5. 테스트 계획

### 5.1 단위 테스트

- 설정값 검증
- 팀 이름 검증
- 성향 점수 계산
- 팀 자동 배정
- 아이템 랜덤 배정
- 미션 완료 판정
- 소감 필수값 검증
- 저장 상태 복구 검증

### 5.2 브라우저 수동 QA

- 새 게임 시작
- 새로고침 후 이어하기
- 잘못된 참가자 수와 팀 수 입력
- 팀 이름 누락 또는 중복
- 성향 응답 누락
- 2단계 아이템 배정 결과 확인
- 3단계와 4단계 미션 답변 저장
- 소감 작성
- 이미지 다운로드
- 저장 데이터 삭제 후 새 게임 시작

### 5.3 반응형 QA

- 모바일 세로 화면
- 태블릿 화면
- 데스크톱 화면
- 버튼, 입력창, 단계 표시 영역의 줄바꿈과 겹침 여부 확인

## 6. 완료 기준

- `npm run build`가 성공한다.
- 주요 단위 테스트가 통과한다.
- 로컬 브라우저에서 1단계부터 결과 다운로드까지 끝까지 진행된다.
- 새로고침 후 진행 상태가 복구된다.
- 개인정보 전용 입력 필드가 없다.
- 이미지 결과물이 다운로드된다.

## 7. MVP 이후 작업

- PDF 다운로드
- 진행자용 콘텐츠 편집 화면
- 팀 배정 수동 조정
- 점수판
- QR 공유
- 다중 기기 실시간 동기화

