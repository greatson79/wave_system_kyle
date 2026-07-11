# t5 State & Recovery Coder — Summary

- **차수/축**: 3차 / 코딩·구현
- **핵심 발견**: **File-Based + 얇은 phase enum guard**. 풀 HSM 은 churchTeam 규모에 과도. `_state.json` 이 진실, status.md 는 파생물.
- **태그**: 5.1 `[LOCAL-OK]`, 5.2 `[LOCAL-OK]`.
- **원자 쓰기 규칙**: tmp write → fsync+rename → status.md 재생성 → git add. 단일 쓰기자(team-leader) 전제.
- **4.5 게이트 코드 표현**: `transition("P1_5_TITLE_LOCKED")` 후 sermon-context.md immutable lock.
- **버려진 후보**: 풀 HSM, 단일 enum 단독.
- **파킹 로트**: PreCompact 와 status.md 동시성 (parking-lot #4).
- **재현 가능 근거**: AgenticWorkflow Context Preservation System.
