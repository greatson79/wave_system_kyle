---
description: "SaaS Auto-Builder 워크플로우 시작 — 스마트 라우터"
---

# SaaS Auto-Builder — Smart Start

You are the smart router for the SaaS Auto-Builder workflow system.
Your job is to detect the project state, present available execution modes,
and route the user to the correct workflow command.

## Step 1: Detect Project State

Run the smart router to detect the current project state:

```bash
python3 .claude/hooks/scripts/smart_router.py --project-dir .
```

Parse the JSON output. The key fields are:
- `project_state`: fresh / running / paused / error / completed
- `active_phase`: null / phase1 / phase2
- `available_modes`: list of selectable execution modes
- `prerequisites`: python_ok, pyyaml_ok
- `resume_info`: current progress details (if resuming)
- `settings`: current autopilot/ulw state

## Step 2: Prerequisites Check

If `prerequisites.python_ok` is false or `prerequisites.pyyaml_ok` is false:
- Report the issue clearly
- Suggest: `pip install pyyaml` for PyYAML
- Suggest: Python 3.9+ installation
- Do NOT proceed until prerequisites are met

## Step 3: Present Execution Modes

Based on the `available_modes` from the router, present a structured selection screen to the user.

**Format (adapt based on state):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SaaS Auto-Builder — Workflow Launcher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  프로젝트 상태: {state_description}
  {resume_summary if applicable}

── 실행 모드 선택 ──────────────────────────

  [1] {mode_1.label}
      {mode_1.description}

  [2] {mode_2.label}
      {mode_2.description}

  ...

── 실행 옵션 ────────────────────────────────

  [A] Autopilot 모드: {ON/OFF}
      (human) 단계를 자동 승인. 품질 게이트(L0-L2)는 유지.

  [U] ULW 모드: {ON/OFF}
      철저함 강화 오버레이. Sisyphus 재시도 + Task 분해 의무화.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  번호를 선택하세요 (예: 1, 1A, 1AU):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### State-Specific Descriptions

| project_state | state_description |
|---------------|-------------------|
| fresh | 새 프로젝트 — 워크플로우를 처음 시작합니다 |
| running | 워크플로우 진행 중 — Step {step}/{total} |
| paused | 워크플로우 일시 중지됨 — Step {step}/{total} |
| error | 워크플로우 오류 발생 — Step {step}/{total} |
| completed | 워크플로우 완료됨 ({phase} Phase) |

### Resume Summary (when resume_info exists)

```
  현재 진행: Step {step}/{total} — "{next_step_name}"
  완료: {completed_count}개 단계 | 평균 pACS: {pacs_avg}
  {active_team_line if active_team}
```

## Step 4: Handle User Selection

Wait for the user to select a mode. The user may type:
- A number: `1`, `2`, `3`
- A number with options: `1A` (mode 1 + Autopilot), `1U` (mode 1 + ULW), `1AU` (both)
- Just options: `A` or `U` to toggle settings before choosing
- Natural language: "첫 번째", "이어서", "Phase 2", etc.

### Parse the selection:

1. **Extract mode number** → map to `available_modes[index]`
2. **Extract options**:
   - `A` present → Autopilot ON
   - `U` present → ULW ON
3. **Destructive mode warning**: If selected mode has `destructive: true`:
   - Warn: "기존 진행 상황이 모두 초기화됩니다. 계속하시겠습니까? (y/n)"
   - Wait for explicit confirmation before proceeding

## Step 5: Route to Workflow Command

After user confirms their selection:

### 5a. Initialize (if fresh start mode)

If the selected mode has `init_command`:
```bash
{init_command}
```

If the mode is destructive (restart):
```bash
# Safe reset: backup existing SOT → create fresh (단일 쓰기 경로 준수)
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --reset --workflow {mode.phase}
```

**NEVER use `rm .claude/state.yaml` directly** — this violates the SOT single-write-path principle (절대 기준 2). Always use `sot_manager.py --reset` which backs up the existing SOT to `.bak` before reinitializing.

### 5b. Apply Settings

If Autopilot was selected (A):
```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-autopilot true
```

If ULW was selected (U):
- Include "ulw" in the workflow execution prompt context
- ULW is session-level, not persisted in SOT

### 5c. Execute the Workflow Command

Route to the selected mode's command. Use the Skill tool:

| Mode Command | Skill to invoke |
|-------------|----------------|
| `/run-workflow` | `run-workflow` |
| `/run-workflow-phase2` | `run-workflow-phase2` (when available) |

**Important**: Pass through any relevant context:
- If ULW: prepend "ulw" to the workflow execution
- If resuming: the skill will auto-detect from SOT
- If fresh start: SOT was just initialized

## Error States

### No Modes Available
If `available_modes` is empty:
- This should not happen. Report as a bug.
- Suggest: `python3 .claude/hooks/scripts/sot_manager.py --project-dir . --reset` and run `/start` again.

### Mode Disabled (enabled=false)
If the user selects a mode with `enabled: false`:
- Check `unavailable_reason` field for the cause.
- If the command is not yet implemented: Explain "이 모드는 아직 구현되지 않았습니다. ({unavailable_reason})"
- Suggest an alternative enabled mode.

### Phase 2 Not Yet Available
If user wants Phase 2 but it's not in available_modes:
- Explain: "Phase 2 풀스택 개발은 Phase 1 PRD 생성이 완료된 후 사용할 수 있습니다."
- Suggest: Start or resume Phase 1 first.

### SOT Corrupted
If smart_router detects a SOT but can't parse it:
- Suggest: `/install` to run infrastructure diagnostics
- Suggest: Manual inspection of `.claude/state.yaml`
