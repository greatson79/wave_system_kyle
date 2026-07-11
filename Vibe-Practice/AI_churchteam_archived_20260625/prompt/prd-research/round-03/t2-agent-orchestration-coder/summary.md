# t2 Agent Orchestration Coder — Summary

- **차수/축**: 3차 / 코딩·구현
- **핵심 발견**: SOT 단일 쓰기 원칙은 **PreToolUse hook 으로 권한 코드 강제** 하는 것이 가장 견고. 분산은 race·일관성 위험으로 LOCAL-PARTIAL.
- **권고 좌표**: **Centralized-with-readonly-fanout** — team-leader 만 status.md/_state.json write, sub-skill 은 자기 출력 폴더만 write.
- **태그**: 2.1 `[LOCAL-OK]`, 2.2 `[LOCAL-PARTIAL]` (분산 트랜잭션 부재).
- **버려진 후보**: Skill Swarm 단독.
- **반증 메모**: insert-images 가 이미 부분 자율 → "절대 중앙" 은 비현실. 읽기 분산·쓰기 단일이 현실 좌표.
- **재현 가능 근거**: agent-registry.md `writes` 필드 + hook 강제 패턴.
