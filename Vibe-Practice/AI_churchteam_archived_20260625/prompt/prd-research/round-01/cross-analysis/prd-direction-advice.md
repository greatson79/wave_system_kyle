# PRD 제작 방향 조언 (Round-01)

## 메타데이터
- 조사 차수: 1 / 생성일: 2026-04-29
- 성격: 방향 조언 (PRD 본문 아님)

---

## 조언 1: 선결 질문 2개를 PRD 첫 섹션에 명시하라

1. **weekly-works(didim)와의 관계 정의**
   - 이 시스템은 didim을 대체하는가, 보완하는가, 완전히 독립적인가?
   - 이 답에 따라 파이프라인 범위가 전부 달라진다

2. **Theology Filter 구현 방식**
   - LLM 판단(프롬프트 기반) vs Python 규칙(Hook 기반)
   - 트레이드오프를 PRD에 명시하고 선택 이유 기록 필수

## 조언 2: Phase 구조로 범위를 쪼개라

- **Phase 1 (MVP)**: Orchestrator + Sermon Pipeline + 슬래시 커맨드 + state.yaml
- **Phase 2**: Discipleship + Operations Automation
- **Phase 3**: Strategy Intelligence + 고도화

## 조언 3: 신학 제약을 ABSOLUTE ANCHOR로 격상하라

- RULES.md의 내용을 PRD 최상위 제약으로 위치
- Theology Filter가 이를 강제하는 메커니즘을 기술

## 조언 4: 사용자 모델을 한 명으로 고정하라

- Phase 1: 담임목사 1인, 슬래시 커맨드 단독 운용
- 스태프 확장은 Phase 2

## 조언 5: 각 에이전트에 로컬 실행 가능성 명시란을 만들어라

- 기능별 "로컬 실행 가능 여부" + "외부 의존성 목록" 표
- 원어 분석처럼 외부 DB 필요 기능은 로컬 설치 방법 기술

---

## 조사 품질 검증

### 1층위 (사실 확인) — 미조사 항목
- 원어 성경 로컬 DB 실제 옵션 미비교

### 2층위 (구조 분석) — 가장 먼저 무너지는 지점
- didim 중복 미해결 상태에서 PRD 작성 시 범위가 두 번 흔들림

### 3층위 (역방향 점검) — 다루지 않은 것

| 미조사 축 | PRD 결정 영향 |
|----------|--------------|
| 원어 데이터 실제 옵션 | Exegesis Agent 설계 전체 |
| Theology Filter 회귀 테스트 | 프롬프트 버전 관리 |
| didim 실제 기능 비교 | 설교 파이프라인 범위 |
| 한국어 신학 용어 처리 (CMT, FCF) | 에이전트 프롬프트 설계 |
| 산출물 형식 결정 | 출력 설계 |
