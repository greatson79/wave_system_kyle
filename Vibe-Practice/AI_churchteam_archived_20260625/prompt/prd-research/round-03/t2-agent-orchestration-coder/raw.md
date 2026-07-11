# t2 Agent Orchestration Coder — Raw

- **차수/축**: 3차 / 코딩·구현 / **Teammate**: t2
- **생성**: 2026-04-29
- **원본 질문**: orchestrator/sub-agent/swarm 을 코드 수준에서 어떻게 분배할 것인가. SOT 단일 쓰기 원칙(절대 기준 2)을 코드로 강제할 수 있는가.
- **근거 출처**: `Claude_skills/weekly-works/.claude/skills/team-leader/rules/agent-registry.md`, AgenticWorkflow `AGENTS.md §SOT`, 부모 hook `block_test_file_edit.py` 패턴(쓰기 권한 차단), 2차 t3 결과(이론 우선 결론) 와의 코드 레벨 차이.

---

## Branch 2.1 — Centralized Orchestration

### 패턴 (구조 예시)

```
team-leader_SKILL.md  ← orchestrator
  ├─ writes: output/{월}/{주차}/status.md, _state.json
  ├─ reads: workflow.md, agent-registry.md, sermon-plan-2026.json
  └─ delegates → sub-skills (read-only inputs, write-own-folder only)

sub-skills (sermon, weekly-devotion, prayer-doc, small-group, sns-cardnews, insert-images, ...)
  ├─ writes: output/{월}/{주차}/{자기영역}/* 만
  └─ NO write to status.md (PreToolUse hook 으로 차단)
```

PreToolUse hook 예 (의사 코드, 부모의 `block_test_file_edit.py` 변형):
```python
# block_status_write_by_subskill.py
if tool == "Write|Edit" and target.endswith("status.md"):
    if caller_skill not in ["team-leader"]:
        sys.exit(2)  # 차단
```

### 전제
- agent-registry.md 의 `writes` 필드가 코드로 강제됨 (위 hook).
- team-leader 컨텍스트에 7산출물 메타가 동시에 적재 가능 (Claude Code 1M 컨텍스트 가정).

### 트레이드오프
- (+) SOT 단일 쓰기 자동 강제 → 절대 기준 2 정합.
- (+) 추적·롤백 쉬움. status.md 에 단일 history.
- (−) team-leader 컨텍스트 폭발 위험 (묵상 15 HTML + 검증 로그 누적).
- (−) team-leader 가 단일 장애점.

### 한계
- 1M 컨텍스트라도 turn 30+ 에서 PreCompact 압박. 압축 중 status.md 동시 갱신이 발생하면 일관성 깨질 수 있음 (t5 와 결합 필요).

### 반증
- weekly-works `insert-images` 가 이미 캡쳐까지 부분 자율 — 완전 중앙은 과거 실용을 뒤집는다. 따라서 *절대 중앙* 은 비현실, **읽기는 다중·쓰기는 단일** 이 현실 좌표.

### `[LOCAL-OK]`
- 모든 호출이 로컬 Claude Code 내부.

### 🅿️ 파킹 로트
- team-leader 가 컨텍스트 폭발 시 sub-orchestrator 로 위임할 패턴 — 본 축 범위 밖.

---

## Branch 2.2 — Distributed Orchestration (Skill Swarm)

### 패턴 (구조 예시)

```
sermon-skill ──hand-off──> small-group-skill (직접 핸드오프)
                       └──> sns-cardnews-skill
team-leader 는 phase 전이 게이트만 검사. status.md 갱신은 swarm 합의 후 어느 skill 이 commit?
```

### 전제
- 산출 디렉토리 구조와 파일명이 *프로토콜* 수준으로 동결.
- 각 skill 이 멱등 + 자가 재시도.

### 트레이드오프
- (+) team-leader 컨텍스트 부담 분산.
- (+) skill 단위 독립 개발·테스트.
- (−) status.md 쓰기 권한 분산 → SOT 단일 쓰기 원칙(절대 기준 2) 위반 위험.
- (−) read-modify-write race (특히 4.5 → D·E fanout 진행 중 4단계 추가 갱신 시도).

### 한계
- Claude Code 에 분산 트랜잭션 없음. OS 수준 파일락만 가능 → race 부분 완화는 되나 일관성 보장 부족.
- 한 skill 실패 시 누가 재시도하는가? 책임 모호.

### 반증
- 부모 게놈 `AGENTS.md` 의 절대 기준 2가 본 분산을 사실상 금지. SOT 위반은 품질 1순위 위반으로 직결.

### `[LOCAL-PARTIAL]`
- 로컬 실행 자체는 가능하나, *분산 트랜잭션 부재* 가 부분 한계. PRD 단계에서 채택 시 LOCAL-PARTIAL 명시 필요.

### 🅿️ 파킹 로트
- 분산 채택 시 합의 알고리즘(Paxos lite, lease) — 본 축 범위 밖, 사실상 over-engineering.

---

## 최종 정리 (Branch 2.1 vs 2.2)

| 기준 | 2.1 중앙 | 2.2 분산 |
|---|---|---|
| SOT 단일 쓰기 강제 | 자동 | 위반 위험 |
| 컨텍스트 부담 | team-leader 집중 | 분산 |
| race 가능성 | 낮음 | 높음 (특히 4.5 fanout) |
| 디버깅 | 쉬움 | 어려움 |
| Claude Code 호환 | 자연스러움 | 인위적 |

**권고 좌표**: **Centralized-with-readonly-fanout**
- team-leader 만 status.md / _state.json write
- sub-skill 은 *자기 출력 폴더* write + 다른 모든 입력 read-only
- PreToolUse hook 으로 권한 코드 강제 (위 의사코드)
- `[LOCAL-OK]`
