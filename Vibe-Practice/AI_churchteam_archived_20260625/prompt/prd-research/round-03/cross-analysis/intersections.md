# Round-03 Cross-Analysis — Intersections (5팀 합의 항목)

- **차수/축**: 3차 / 코딩·구현
- **생성**: 2026-04-29

## 4관점(표현력/안정성/속도/유지보수) 토론 결과 압축

| 합의 패턴 | 표현력 | 안정성 | 속도 | 유지보수 | LOCAL |
|---|---|---|---|---|---|
| 상위 절차적 + 노드 내부 선언적 DAG (t1) | ✓ | ✓ | ✓ | ✓ | OK |
| Centralized + readonly fanout (t2) | ✓ | ✓ | ✓ | ✓ | OK |
| Layered Skills (`val/*` 범용 + `skill/*` 특화) (t3) | ✓ | ✓ | ✓ | ✓ | OK |
| L0+L1 전면 / L2 핀포인트 + SOT-pin 의무 (t4) | ✓ | ✓ | ✓ | ✓ | OK |
| File-state + phase enum guard (t5) | ✓ | ✓ | ✓ | ✓ | OK |

**5/5 합의**: 위 5축이 코딩·구현 axis 의 합의 좌표.

## 5팀이 동의하는 운영 불변

1. team-leader 만 status.md / `_state.json` write. 그 외는 자기 출력 폴더만 write.
2. 4.5 단계 = phase enum hard gate. 잠금 후 sermon-context.md immutable.
3. SOT-pin checker 는 모든 설교 노드에 의무. sermon-plan-2026.json 을 AI 기억으로 재구성하지 않는다.
4. L0(빈 산출 차단) 은 모든 노드에 박힌다.
5. workflow.md 포맷 스키마(부록): `id, phase, agent, skill, inputs[], outputs[], validators[], retry_budget, depends_on, exit_criteria`.

## 1·2차 결과와의 정합

- **1차 일반 축** "Claude Code 단독 완결 우위" → 본 차 권고 모두 LOCAL-OK 로 정합.
- **2차 기술·이론 축** "정밀 설정 + 적극 연동(MCP) + 검증된 원칙" → 본 차의 hook 권한 강제, validator 레이어, file-state 가 모두 정합.
- 충돌 없음. 단, 2차 t3(이론) 와 3차 t2(코드) 의 **층위 차이** 는 conflicts.md 에서 명시.
