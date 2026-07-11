# T5 Theory Foundation Expert — 핵심 발견 요약 (Round-02)

## 메타데이터
- 조사 차수: 2 / Teammate: t5 / 조사 축: 기술·이론 축 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
최신 에이전틱 이론(ReAct, Multi-Agent)이 설계 언어를 제공하고 검증된 자동화 원칙(상태 머신, 실패 격리)이 구현 신뢰성을 보장하며, 둘 다 필요하고 충돌하지 않는다. 단, LLM 비결정성으로 인해 신학 검증은 목회자 최종 검토가 이론보다 우선한다.

## 핵심 이론 목록

| 이론 | 원저자 | 연도 | 적용 | 로컬 실행 |
|-----|------|-----|-----|---------|
| ReAct | Yao et al. | ICLR 2023 | Orchestrator 루프 설계 | LOCAL-OK |
| Multi-Agent | Li et al. / Park et al. | 2023 | 12 에이전트 역할 분화 | LOCAL-OK |
| Reflexion | Shinn et al. | NeurIPS 2023 | Theology Filter 자기 검토 | LOCAL-OK |
| Unix 철학 | Thompson/Ritchie | 1978~ | 에이전트 단일 책임 | LOCAL-OK |
| 상태 머신 | 제어공학 원칙 | 수십 년 | state.yaml SOT | LOCAL-OK |
| 실패 격리 | Bulkhead Pattern | 2010~  | Task tool 격리 | LOCAL-OK |

## 이론과 현실의 핵심 갭
1. ReAct 완전 자동 루프 → Claude Code는 사용자 개시 필수
2. Multi-Agent 실시간 공유 → 파일 기반 비동기만 가능
3. 멱등성 원칙 → LLM 비결정성으로 부분 적용만 가능

## PRD에 전달할 것
- "목회자 검토 단계는 이론적 자동화 설계보다 우선한다"를 설계 원칙으로 명시
- Orchestrator 설계에 ReAct 루프 + 상태 머신을 결합한 구조 채택
- 각 에이전트의 단일 책임 원칙(Unix 철학)을 역할 정의에 반영
