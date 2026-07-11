# PRD Research Index

## 목적
churchTeamPRD.md를 위한 teammate 심층조사 결과 저장소.
각 round의 조사 결과를 축별로 분리 저장하여 종합 단계에서 재조합 가능하게 조직화.

---

## 조사 Round 현황

| Round | 날짜 | 조사 축 | 상태 | 메타 파일 |
|-------|------|---------|------|----------|
| round-01 | 2026-04-29 | 일반 축 — Claude Code 단독 완결 vs 외부 도구(MCP·스크립트) 연동 | 완료 | round-01/_round-meta.md |
| round-02 | 2026-04-29 | 기술·이론 축 — Platform/Config/Orchestration/Integration/Theory (5 Teammate × 2 Branch) | 완료 | round-02/_round-meta.md |
| round-03 | 2026-04-29 | 코딩·구현 축 — WorkflowScript/Orchestration/Skills&Hooks/Verification/State (5 Teammate × 2 Branch + 4 토론 + 3 시나리오) | 완료 | round-03/_round-meta.md |

---

## 확장 규칙

### 새 조사 Round 추가 시
1. `round-NN/` 폴더 생성 (NN = 02, 03 ...)
2. `round-NN/_round-meta.md` 에 차수 메타데이터 기록
3. 각 teammate 폴더: `t1-workflow-architect/`, `t2-scenario-explorer/`, `t3-operator-analyst/`, `t4-sustainability-strategist/`
4. 각 폴더 안에 `raw.md` + `summary.md` 분리 저장
5. `cross-analysis/` 에 교집합·충돌·파킹 로트 기록
6. `_index.md` (이 파일) Round 현황 테이블 업데이트

### 파일명 규칙
- 원본 산출: `raw.md`
- 정제 요약: `summary.md`
- 교차 분석: `cross-analysis/intersections.md`, `conflicts.md`, `parking-lot.md`
- 방향 조언: `cross-analysis/prd-direction-advice.md`

### 종합 단계 진입 조건
- round-01 ~ round-N 전부 완료 후 `synthesis/` 폴더 신규 생성
- `synthesis/final-prd-input.md` 에 전 round 핵심 발견 통합
- `synthesis/open-questions.md` 에 미해결 질문 목록 유지

---

## Teammate 식별자 고정

| ID | 이름 | 담당 축 |
|----|------|---------|
| t1 | Workflow Architect | 구조·파이프라인 설계 |
| t2 | Scenario Explorer | 사용 시나리오 지형 |
| t3 | Operator Analyst | 사용자 행동·마찰 |
| t4 | Sustainability Strategist | 지속 가능성·확장 |
