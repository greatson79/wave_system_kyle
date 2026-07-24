# SaaS Auto-Builder PRD Generation — Orchestrator Command

You are the orchestrator for the SaaS Auto-Builder PRD Generation workflow. This command executes a 12-step, 3-phase workflow that produces a comprehensive PRD document.

**Absolute Rule**: Quality is the ONLY criterion. Speed and token cost are completely ignored.

**Anti-Hallucination Rule**: For all step configuration, path derivation, pACS scoring, and decision logic, use `orchestrator_actions.py` (deterministic Python) instead of interpreting prose. The Python helper is the single source of truth for orchestration data.

```
HELPER = "python3 .claude/hooks/scripts/orchestrator_actions.py"
SOT_MGR = "python3 .claude/hooks/scripts/sot_manager.py --project-dir ."
QUALITY = "python3 .claude/hooks/scripts/quality_gate_runner.py"
```

## Prerequisites Check

Before starting, verify:
1. `python3 --version` — Python 3.9+ required
2. `python3 -c "import yaml"` — PyYAML required
3. Verify helper: `python3 .claude/hooks/scripts/orchestrator_actions.py --action step-config --step 1`

## Phase 0: Initialize or Resume

### Fresh Start

```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --init
```

Create tasks for all 12 steps. For each step, get config from the helper:

```bash
# For N = 1 to 12:
python3 .claude/hooks/scripts/orchestrator_actions.py --action step-config --step {N}
```

Parse each JSON response and create tasks:
```
TaskCreate(subject="Step {step}: {name}", description="{type} step. Deps: {deps}. Output: {output}")
```

Set up dependency chains from the `deps` field in each step-config response.

### Resume (SOT exists)

Read `.claude/state.yaml` to determine `current_step` and `status`:
- `status == "completed"` → Report completion and exit
- `status == "error"` or `"paused"` → Report status, ask user to resume
- `status == "running"` → Continue from `current_step + 1`

If `active_team` exists with incomplete tasks → resume team coordination (see Team Step Protocol).

## Step Execution Loop

For each step from `current_step + 1` to 12:

### 1. Get Step Configuration (MANDATORY — replaces prose interpretation)

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action step-config --step {N}
```

Parse the JSON. Use the fields directly:
- `type` → determines execution path (human, sub-agent, agent-team)
- `agent` → agent to spawn
- `output` → expected output file path
- `pre_script` → script to run before agent (if not null)
- `review` → review agent (if not null)
- `translate` → whether to translate
- `is_human_step` → true for steps 4, 8, 12
- `special_flow` → "two-phase" for Step 11 (null for all others)

### 2. Verify Dependencies (MANDATORY — prevents skipping)

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action verify-deps --step {N} --project-dir .
```

Parse JSON. If `deps_satisfied` is false, STOP and report `missing` entries. Do NOT proceed with unsatisfied dependencies.

### 3. Execute by Step Type

---

#### HUMAN STEPS (type == "human")

| Step | Command | Gate |
|------|---------|------|
| 4 | `/review-research` | Research findings approval |
| 8 | `/review-planning` | Planning artifacts approval |
| 12 | `/review-final-prd` | Final PRD approval (hybrid — also produces deliverable) |

**Protocol**:
1. TaskUpdate(taskId=step_task, status="in_progress")
2. Invoke the review slash command
3. Wait for user approval
4. On approval:
   - TaskUpdate(taskId=step_task, status="completed")
   - `python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step {N} --output approved-by-user`
5. On rejection: Report feedback, pause workflow

**Step 12 Hybrid Protocol** (after user approval):

Get the exact command sequence from the helper:
```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action finalize-step12 --project-dir .
```

Parse JSON and execute the 5 commands in order:
1. Copy validated PRD to final location (source → destination from JSON)
2. Spawn @translator (agent/input/output/glossary from JSON)
3. Run bilingual validator (command from JSON)
4. Register translation in SOT (command from JSON)
5. Update SOT with final output (command from JSON)

---

#### SUB-AGENT STEPS (type == "sub-agent")

**Execution Sequence** (execute in this exact order):

**a. Mark in-progress**
```
TaskUpdate(taskId=step_task, status="in_progress")
```

**b. Get agent prompt and paths (MANDATORY — replaces prose templates)**

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action agent-prompt --step {N} --project-dir .
```

Parse JSON to get: `agent`, `output`, `prompt`, `pre_script`, `review`, `translate`, `ko_output`, `inputs`.

**c. Run pre-script** (if `pre_script` is not null in JSON)

Execute the `pre_script.command` value from the JSON response:
```bash
# Example for Step 1:
python3 scripts/extract_prd_sections.py --input coding-resource/PRD.md --output-dir prompt/research/sections/
# Example for Step 10:
python3 scripts/merge_prd_sections.py --input-dir prompt/implementation/ --output prompt/implementation/prd-merged.md
```

**d. Spawn agent**

Use the `agent` and `prompt` fields from the JSON. Check `special_flow` from step-config:

For **regular sub-agent steps** (`special_flow` is null):
```
Agent(
  description="Step {N}: {name}",
  prompt="{prompt}",
  mode="bypassPermissions"
)
```

For **Step 11** (`special_flow == "two-phase"`), the agent-prompt helper returns `type: "two-phase"` with `phase1` and `phase2` sub-objects. Spawn both in a single message for parallel execution:
```
# Phase 1 + Phase 2 (parallel — single message, two Agent() calls)
Agent(
  description="Step 11 Phase 1: Adversarial Review",
  subagent_type="{phase1.subagent_type}",
  isolation="worktree",
  prompt="{phase1.prompt}",
  mode="bypassPermissions"
)
Agent(
  description="Step 11 Phase 2: Fact Check",
  subagent_type="{phase2.subagent_type}",
  isolation="worktree",
  prompt="{phase2.prompt}",
  mode="bypassPermissions"
)

# After both complete, merge reports into the output path from JSON
```

**e. Verify output**

```bash
python3 .claude/hooks/scripts/quality_gate_runner.py --step {N} --project-dir . --output-path {output} --skip-review --skip-translation
```

Check `all_passed`. If L0 fails, retry the agent (max 2 retries with different approach each time per I-1 Sisyphus).

**f. Extract pACS score (MANDATORY — replaces LLM interpretation)**

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action extract-pacs --file {output} --project-dir .
```

Parse JSON: `final_score`, `weak_dim`, `arithmetic_ok`, `found`.
- If `found` is false → warn but proceed (agent did not include pACS section)
- If `arithmetic_ok` is false → flag discrepancy (reported vs calculated)

Record in SOT:
```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-pacs {N} --pacs-score {final_score} --weak-dim {weak_dim}
```

**g. pACS Decision (MANDATORY — replaces prose decision matrix)**

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action pacs-decision --score {final_score} --weak-dim {weak_dim} --step {N}
```

Parse JSON and follow the `action` field exactly:
- `action == "proceed"` → Continue to next phase
- `action == "proceed_with_warning"` → Log `feedback`, continue
- `action == "rework_required"` → Re-spawn agent with the `feedback` text as additional context. Max 1 pACS rework per step (`rework_max` from JSON). If still RED → escalate to user.

**h. L2 Adversarial Review** (if `review` field is not null in step-config)

Use the `review.agent` value from the agent-prompt JSON (may be "reviewer" or "fact-checker"):
```
Agent(
  description="Step {N} L2 Review",
  subagent_type="{review.agent}",
  isolation="worktree",
  prompt="Review step {N} output at {output}. Generator pACS = {final_score}.
          Context: This is '{name}'. Check fidelity against inputs, completeness, and logical coherence.
          Write your review report to stdout — do NOT create files.",
  mode="bypassPermissions"
)
```

If review verdict is FAIL with Critical issues → rework the step.

**i. Translation** (if `translate` is true in step-config)

Get paths:
```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action derive-paths --step {N} --project-dir .
```

Use `ko_output` from the JSON:
```
Agent(
  description="Step {N} Translation",
  subagent_type="translator",
  prompt="Translate {en_output} to Korean.
          Output: {ko_output}
          Use glossary at translations/glossary.yaml.
          Preserve all markdown structure, code blocks, and Mermaid diagrams untranslated.",
  mode="bypassPermissions"
)
```

After translation completes:
```bash
python3 .claude/hooks/scripts/bilingual_validator.py --step {N} --project-dir .
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --add-translation {N} --ko-path {ko_output}
```

**j. Full quality gate** (now with translation)

```bash
python3 .claude/hooks/scripts/quality_gate_runner.py --step {N} --project-dir . --output-path {output} --skip-review
```

**k. Update SOT**

```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step {N} --output {output}
```

**l. Mark complete**
```
TaskUpdate(taskId=step_task, status="completed")
```

---

#### AGENT-TEAM STEPS (type == "agent-team")

**a. Get team configuration (MANDATORY — replaces hardcoded tables)**

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action team-files --step {N} --project-dir .
```

Parse JSON: `team_name`, `members` (each with `agent`, `task`, `output`), `files_csv`, `manifest_path`.

**b. Mark in-progress and set team**
```
TaskUpdate(taskId=step_task, status="in_progress")
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-team {team_name} --team-status partial
```

**c. Get member prompts**

```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action agent-prompt --step {N} --project-dir .
```

Parse JSON: `member_prompts` array, each with `agent`, `task`, `output`, `prompt`.

**d. Spawn all team members**

Spawn all members in a **single message** with multiple parallel Agent() calls. This is the preferred concurrency pattern. If parallel execution fails, fall back to sequential.

```
# Parallel (preferred — single message, multiple Agent() calls):
Agent(
  description="Team {team_name}: {member_prompts[0].agent}",
  prompt="{member_prompts[0].prompt}",
  mode="bypassPermissions"
)
Agent(
  description="Team {team_name}: {member_prompts[1].agent}",
  prompt="{member_prompts[1].prompt}",
  mode="bypassPermissions"
)
# ... one Agent() call per team member, all in one message

# Sequential fallback (if parallel fails):
For each member in member_prompts:
  Agent(
    description="Team {team_name}: {member.agent}",
    prompt="{member.prompt}",
    mode="bypassPermissions"
  )
```

**e. Verify each member output and record in SOT**

For each member from the team-files JSON:
```bash
python3 .claude/hooks/scripts/quality_gate_runner.py --step {N} --project-dir . --output-path {member.output} --skip-review --skip-translation
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --add-team-result {member.agent} --output {member.output}
```

If any member output fails L0, retry that specific member (max 2 retries).

**f. Generate manifest**

Use `files_csv` from team-files JSON:
```bash
python3 .claude/hooks/scripts/manifest_generator.py --step {N} --project-dir . --files "{files_csv}"
```

**g. Translate each sub-output** (if step.translate is true)

Get paths for each member:
```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action derive-paths --step {N} --project-dir .
```

For each `team_member_outputs` entry:
```
Agent(
  description="Translate {member.agent} output",
  subagent_type="translator",
  prompt="Translate {en_path} to Korean.
          Output: {ko_path}
          Use glossary at translations/glossary.yaml.",
  mode="bypassPermissions"
)
```

Validate bilingual pairs:
```bash
python3 .claude/hooks/scripts/bilingual_validator.py --step {N} --project-dir .
```

**h. Finalize team and update SOT**

Use `manifest_path` from team-files JSON:
```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --finalize-team
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step {N} --output {manifest_path}
```

**i. Mark complete**
```
TaskUpdate(taskId=step_task, status="completed")
```

---

## Error Handling

### Step Failure
1. Set status: `python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-status error`
2. Report failure with diagnostics to user
3. User can resume by running `/run-workflow` again

### Agent Failure (I-1 Sisyphus Persistence)
- Retry up to 2 times with a different approach each attempt
- Attempt 1: Re-run with same prompt
- Attempt 2: Re-run with additional context ("Previous attempt failed because {reason}. Focus on {weak_area}.")
- After 2 retries: Escalate to user with failure details

### pACS RED Score (< 50)

Use the deterministic helper:
```bash
python3 .claude/hooks/scripts/orchestrator_actions.py --action pacs-decision --score {SCORE} --weak-dim {DIM} --step {N}
```

The `feedback` field contains the exact rework instructions. Pass it to the re-spawned agent. Max 1 pACS rework per step (`rework_max` from JSON). If still RED → escalate to user.

### Team Member Failure
- Retry the failing member only (do not restart the entire team)
- If retry fails, check if other members can compensate
- If not, escalate to user

## Compaction Recovery Protocol

If context is compressed mid-workflow:

1. **Read SOT**: Read `.claude/state.yaml` — extract `current_step`, `status`, `active_team`, `outputs`
2. **Read Tasks**: TaskList to see task status
3. **Active team check**: If `active_team` exists:
   - Get team files: `python3 .claude/hooks/scripts/orchestrator_actions.py --action team-files --step {TEAM_STEP} --project-dir .`
   - Check `members[].exists` in JSON for each member
   - Resume from the first member where `exists` is false
4. **No active team**: Resume from `current_step + 1`
5. **Verify prior outputs**: For steps 1 through current_step:
   ```bash
   python3 .claude/hooks/scripts/orchestrator_actions.py --action verify-deps --step {current_step + 1} --project-dir .
   ```
6. **Re-read step config**: `python3 .claude/hooks/scripts/orchestrator_actions.py --action step-config --step {N}` to restore step metadata

## Workflow Completion

After all 12 steps:
```bash
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-status completed
```

Report final outputs:
- EN: `prompt/PRD-SaaS-AutoBuilder.md`
- KO: `prompt/PRD-SaaS-AutoBuilder.ko.md`

Report final quality metrics:
- Total steps completed: 12
- pACS history: Read from SOT `pacs.history`
- Weakest step: Step with lowest pACS score
- L2 review results: Steps 3, 6, 7, 11 review verdicts

## Quality Standards

- **English-First**: All agent processing and outputs in English. @translator produces .ko.md pairs.
- **Quality over speed**: No time or token constraints. Only final output quality matters.
- **pACS Threshold**: Use `--action pacs-decision` for deterministic GREEN/YELLOW/RED branching.
- **L2 Review**: Steps with `review` field non-null have mandatory adversarial review.
- **4-Layer Quality Gate**: L0 (Anti-Skip) → L1 (Structural Verification) → L1.5 (pACS) → L2 (Adversarial Review)
- **Translation Protocol**: Steps with `translate: true` produce .ko.md pairs validated by bilingual_validator.
- **Deterministic Orchestration**: ALL step config, path derivation, pACS extraction, and decision logic via `orchestrator_actions.py`. NEVER interpret these from prose.
