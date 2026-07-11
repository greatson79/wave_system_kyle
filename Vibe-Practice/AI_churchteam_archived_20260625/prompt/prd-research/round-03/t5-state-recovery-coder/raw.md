# t5 State & Recovery Coder — Raw

- **차수/축**: 3차 / 코딩·구현 / **Teammate**: t5
- **생성**: 2026-04-29
- **원본 질문**: 워크플로우 상태를 파일 기반 단순 구조로 둘 것인가, 구조화된 상태머신으로 둘 것인가. PreCompact/SessionEnd hook 과 어떻게 정합시킬 것인가.
- **근거 출처**: AgenticWorkflow Context Preservation System(`save_context.py`, `restore_context.py`, `generate_context_summary.py`), weekly-works `output/{월}/{주차}/status.md` 구조.

---

## Branch 5.1 — File-Based State

### 패턴 (구조 예시)

```
output/{월}/{주차}/
  ├─ status.md      ← 인간 가독 (마크다운 표)
  ├─ _state.json    ← 머신 가독
  ├─ 설교/
  │   └─ sermon-context.md  ← 4.5 잠금 후 immutable
  ├─ 매일묵상/
  ├─ 수요기도회/
  ├─ 소그룹나눔지/
  ├─ 카드뉴스/
  └─ 보고서/
```

`_state.json` 스키마(예):
```json
{
  "week_id": "2026-04-W4",
  "phase": "P1_INTERACTIVE",
  "nodes": {
    "sermon-1": {"status":"done", "outputs":["설교/draft-step1.md"], "validated":["L0","L1"]},
    "sermon-4_5": {"status":"running"},
    "small-group": {"status":"pending"}
  },
  "title_locked": false,
  "checkpoint_at": "2026-04-29T10:31:00+09:00"
}
```

쓰기 순서(원자성):
1. 임시 파일 `_state.json.tmp` write
2. fsync + rename → `_state.json` 원자 교체
3. status.md 재생성 (read `_state.json` → render markdown)
4. git add 두 파일

### 전제
- 단일 쓰기자 (team-leader). t2 결과와 결합.
- PreCompact 시 진실은 `_state.json`. status.md 는 파생물.

### 트레이드오프
- (+) 투명·grep 가능. 디버깅 쉬움.
- (+) 부모 Context Preservation System 과 정합 (스냅샷에 자연스럽게 포함).
- (−) 동시성 보장 약함 (단일 쓰기자 전제 위배 시 즉시 깨짐).
- (−) `_state.json` 과 status.md 사이 crash 시 파생물 재생성 필요.

### 한계
- PreCompact 가 status.md 갱신 *중간* 에 발화하면 status.md 는 깨질 수 있음. 정책: status.md 는 항상 `_state.json` 에서 재생성 가능 → 파생물로 취급, crash 후 재생성.

### 반증
- 부모 Context Preservation 이 이미 파일 기반 → 정합 우위.

### `[LOCAL-OK]`

### 🅿️ 파킹 로트
- PreCompact 동시성 (parking-lot #4).

---

## Branch 5.2 — Structured State Machine

### 패턴 (구조 예시)

```python
# phase enum
PHASES = [
  "P0_INIT",
  "P1_AUTO",
  "P1_INTERACTIVE",
  "P1_5_TITLE_LOCKED",
  "P2_PARALLEL",
  "P3_REPORT",
  "DONE"
]
ALLOWED = {
  "P0_INIT": ["P1_AUTO"],
  "P1_AUTO": ["P1_INTERACTIVE"],
  "P1_INTERACTIVE": ["P1_5_TITLE_LOCKED"],
  "P1_5_TITLE_LOCKED": ["P2_PARALLEL"],
  "P2_PARALLEL": ["P3_REPORT"],
  "P3_REPORT": ["DONE"],
}
def transition(cur, nxt):
    if nxt not in ALLOWED[cur]: raise IllegalTransition
```

추가로 hierarchical state machine (HSM): P2_PARALLEL 안에 small-group/sns-cardnews 의 부분 동시 상태.

### 전제
- 상태 수 < ~30. churchTeam 은 phase 7개 + 노드 7개 = 충분히 적음.
- 상태 무결성 검사가 코드로 강제됨.

### 트레이드오프
- (+) 잘못된 전이 차단 (예: P1_INTERACTIVE → P2 직접 점프 차단 = 4.5 게이트 강제).
- (+) 예측 가능성 최상.
- (−) 새 산출 추가 시 enum + 표 동시 수정.
- (−) HSM 도입 시 구현 복잡도 급증.

### 한계
- 단일 enum 으로 P2 의 small-group/sns-cardnews 부분 동시 상태 표현 불가 → HSM 또는 노드별 sub-status 가 필요.

### 반증
- 풀 HSM 은 churchTeam 규모에 과도. 얇은 phase enum + 노드별 sub-status (file-based 와 결합) 가 현실 좌표.

### `[LOCAL-OK]`

### 🅿️ 파킹 로트
- HSM 채택 시 시각화 도구 — 본 축 범위 밖.

---

## 최종 정리 (Branch 5.1 vs 5.2)

| 기준 | 5.1 파일 | 5.2 상태머신 |
|---|---|---|
| 디버깅 | 쉬움 | 보통 |
| 잘못된 전이 차단 | 약함 | 강함 |
| 부모 정합 | 강 | 보통 |
| 추가 비용 | 낮음 | 중간(HSM 시 큼) |

**권고 좌표**: **File-Based + 얇은 phase enum guard**
- `_state.json` 의 `phase` 필드에 enum 적용, transition 함수로만 변경.
- 노드별 진행은 `_state.json.nodes` 에 sub-status (pending/running/done/failed).
- 4.5 게이트 = `phase==P1_INTERACTIVE && all(sermon-1..4 done) && sermon-4_5 done` → `transition("P1_5_TITLE_LOCKED")` → sermon-context.md immutable lock.
- `[LOCAL-OK]`.
