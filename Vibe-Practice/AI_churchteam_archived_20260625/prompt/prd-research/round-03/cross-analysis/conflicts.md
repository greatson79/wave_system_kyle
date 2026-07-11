# Round-03 Cross-Analysis — Conflicts

- **차수/축**: 3차 / 코딩·구현
- **생성**: 2026-04-29

## 1. 내부 불일치 (5팀 사이)

| # | 충돌 | t-축 | 본 차수 결론 |
|---|---|---|---|
| C1 | 선언적 단독 vs 절차적 단독 | t1 | 혼합 (상위 절차 + 노드 선언). 단독 후보는 모두 기각. |
| C2 | 중앙 vs 분산 | t2 | Centralized + readonly fanout. 분산 단독은 절대 기준 2 위반 위험 → 기각, LOCAL-PARTIAL. |
| C3 | 범용 vs 특화 | t3 | 레이어 분리. 단독은 모두 기각. |
| C4 | Strict vs Selective 검증 | t4 | L0/L1 전면 + L2 핀포인트. Strict 단독 기각(토큰·UX 비용). |
| C5 | 파일 vs 상태머신 | t5 | File-state + 얇은 phase enum. 풀 HSM 기각(과도). |

## 2. 차수 간 경계 중복 (1·2차 vs 3차)

### 경계 중복 #1 — 오케스트레이션
- **2차 t3 Orchestration Engineer**: *이론* 레벨에서 "고도 오케스트레이션" 우위 결론.
- **3차 t2 Agent Orchestration Coder**: *코드 레벨* 에서 "Centralized + readonly fanout" 결론.
- **해결**: 층위 차이 명시. 2차는 *어떤 이론 패턴이 적합한가*, 3차는 *그 패턴을 코드로 어떻게 안전하게 강제하는가*. 둘은 **수직 관계** 이며 충돌이 아님. PRD §System Architecture 에 두 층위 모두 반영.

### 경계 중복 #2 — 검증
- **2차 t1 Platform Capability**, **t5 Theory Foundation** 이 검증 원칙 일부 다룸 (이론).
- **3차 t4 Verification & Quality Coder**: 코드 레벨로 L0/L1/L2 매핑.
- **해결**: PRD §Quality Gates 는 3차 t4 결론을 1차 자료로, 2차 결과를 *원칙 근거* 로 인용.

### 경계 중복 #3 — 상태 관리
- **2차 t2 Configuration Architect** 가 설정 파일 구조를 다루나, *워크플로우 상태* 가 아닌 *설정* 중심.
- **3차 t5** 는 워크플로우 상태(`_state.json`).
- 충돌 아님. 영역 분리.

## 3. 식별자 정책 (`_index.md` 와의 정합)

- `_index.md` 의 "Teammate 식별자 고정" 표는 round-01 4축 기준. round-02 가 5팀(축 변경) 으로 차수별 재구성을 선례로 만듦.
- round-03 는 round-02 선례를 따라 코딩 5축에 맞춰 t1~t5 를 재정의.
- **이 변경은 `_index.md` 표를 수정하지 않는다** (round-01 의 기준 보존). 차수별 teammate 정의는 각 round 의 `_round-meta.md` 에서 권위적으로 관리.
- 임의 규칙 변경 아님. 기존 선례 준수.

## 4. 미해결 충돌 (PRD 단계로 이관)

- **U1**: 4.5 게이트 잠금 후 4단계 추가 갱신 시도 시의 정책. 현 권고는 "잠금 후 sermon-context.md immutable" 이지만, 운영 중 목사가 본문을 변경하는 경우 *재계획* 메커니즘을 PRD 가 정해야 함.
- **U2**: NotebookLM MCP 인증 갱신 실패 시 워크플로우 차단/우회 정책 (2차에서도 PARTIAL).
- 둘 다 parking-lot.md 로 이관.
