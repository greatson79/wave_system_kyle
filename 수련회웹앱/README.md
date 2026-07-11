# 수련회 팀빌딩 성경 미션 웹앱

교회 수련회, 성경학교, 여름행사에서 사용할 수 있는 팀빌딩형 웹앱 게임입니다. MVP는 로그인, 서버 저장, 개인정보 입력 없이 한 기기에서 진행자가 조작하는 흐름으로 구현합니다.

## 주요 기능

- 전체 인원 수와 팀 수 설정
- 팀 이름 입력과 참가자 번호 자동 생성
- 간이 성향 질문 기반 팀 자동 구성
- 직접 입력/선택한 힌트를 사다리타기 게임으로 팀별 배정
- 성경 기반 협업 미션
- 최종 공동체 실천 약속 작성
- 팀별 소감 작성
- 결과 카드 이미지 다운로드
- `localStorage` 기반 새로고침 복구

## 실행

```bash
npm install
npm run dev
```


## 검증

```bash
npm run lint
npm test
npm run build
```

## 문서

- 요구사항: `docs/requirement.md`
- PRD: `docs/prd.md`
- 유저 플로우: `docs/userflow.md`
- 데이터 설계: `docs/database.md`
- 공통 모듈 계획: `docs/common-modules.md`
- 구현 계획: `docs/implementation-plan.md`
- 유스케이스: `docs/usecases/*/spec.md`
- 페이지 계획: `docs/pages/*/plan.md`
