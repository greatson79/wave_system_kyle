# t1 Workflow Script Architect — Summary

- **차수/축**: 3차 / 코딩·구현
- **핵심 발견**: 선언적 단독은 하드 게이트(특히 4.5 → D·E fanout)를 구조적으로 강제하지 못하고, 절차적 단독은 인간 분기·운영 마찰을 흡수하지 못한다. **상위 절차적 + 노드 내부 선언적 혼합** 이 합의 좌표.
- **의사 결정 영향**:
  - PRD §Workflow Specification: 부록 스키마 의무 — `id, phase, agent, skill, inputs[], outputs[], validators[], retry_budget, depends_on, exit_criteria`.
  - PRD §System Architecture: phase enum 게이트가 DAG 구조 자체에 박힐 것.
- **태그**: 1.1 `[LOCAL-OK]`, 1.2 `[LOCAL-OK]`. Blocked·Partial 없음.
- **버려진 후보**: 선언적 단독, 절차적 단독.
- **반증 메모**: 운영 메모리에 "4.5 후 D·E 동시 소환" 이 *피드백* 으로 박혀야 했던 사실 = 선언적 단독의 약점 증거.
- **재현 가능 근거**: weekly-works/.claude/skills/team-leader/rules/workflow-dag.md 의 현 운영 패턴.
