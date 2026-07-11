# Autopilot Execution Protocol

> This document is the detailed checklist for executing workflows in Autopilot mode.
> Separated from CLAUDE.md — reference only during workflow execution.

## Activation Patterns

| User Command | Behavior |
|-----------|------|
| "run in autopilot mode", "run workflow automatically", "fully automated execution" | Set SOT `autopilot.enabled: true` then start workflow |
| "disable autopilot", "switch to manual mode" | Set SOT `autopilot.enabled: false` — takes effect from the next `(human)` step |

## Checkpoint Behavior

| Checkpoint | Autopilot Behavior |
|-----------|---------------|
| `(human)` + Slash Command | Generate complete artifact → auto-approve with quality-maximizing defaults → record decision log |
| AskUserQuestion | Auto-select quality-maximizing option from choices → record decision log |
| `(hook)` exit code 2 | **No change** — block as-is, deliver feedback, rework |

## Decision Log

Auto-approved decisions are recorded in `autopilot-logs/step-N-decision.md`: step, options, selection rationale (based on Absolute Standard 1).
Decision Log standard template: `references/autopilot-decision-template.md`

## Runtime Reinforcement Mechanisms

| Layer | Mechanism | Reinforcement |
|------|---------|----------|
| **Hook** (deterministic) | `restore_context.py` — SessionStart | Inject 6 execution rules + prior step artifact validation results into context when Autopilot active |
| **Hook** (deterministic) | `generate_snapshot_md()` — snapshot | Preserve Autopilot state + Agent Team state sections at IMMORTAL priority |
| **Hook** (deterministic) | `generate_context_summary.py` — Stop | Detect missing Decision Log → supplement (safety net) |
| **Hook** (deterministic) | `update_work_log.py` — PostToolUse | Track step progression via `autopilot_step` field |
| **Prompt** (behavioral) | Execution Checklist (below) | Specify required actions at start/execution/completion of each step |

> The Hook layer accesses SOT in read-only mode (Absolute Standard 2 compliance); writes only to `context-snapshots/` and `autopilot-logs/`.

---

## Execution Checklist (MANDATORY)

When executing a workflow in Autopilot mode, **always** perform the following checklist at each step.

### Before Each Step Starts
- [ ] Check SOT `current_step`
- [ ] Confirm prior step artifact file exists and is non-empty
- [ ] Confirm prior step artifact path is recorded in SOT `outputs`
- [ ] Read the step's `Verification` criteria — recognize the definition of "100% complete" first (AGENTS.md §5.3)

### During Step Execution
- [ ] **Fully** execute all tasks in the step (no abbreviation — Absolute Standard 1)
- [ ] Generate artifacts at **complete quality**

### After Step Completion (Verification Gate — only for steps with a `Verification` field)
- [ ] Save artifact file to disk
- [ ] Self-verify artifact against each `Verification` criterion
- [ ] If any criterion fails:
  - [ ] Check + consume P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate verification --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** (see diagnosis subsection below) → re-execute based on diagnosis
  - [ ] `can_retry: false` → escalate to user (retry budget exhausted, do not increment counter)
- [ ] Confirm all criteria PASS
- [ ] Generate `verification-logs/step-N-verify.md`
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_verification.py --step N --project-dir .`
- [ ] Confirm P1 validation result `valid: true` (V1a-V1c all pass)

### After Step Completion (Cross-Step Traceability — only for steps where Verification includes "cross-step traceability" criteria)
- [ ] Confirm artifact contains at least 3 `[trace:step-N:section-id]` markers
- [ ] Confirm all markers reference only prior steps (no forward references)
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_traceability.py --step N --project-dir .`
- [ ] Confirm P1 validation result `valid: true` (CT1-CT5 all pass)
- [ ] If CT3 WARNING (section ID unresolved): re-verify marker accuracy

### After Step Completion (Domain Knowledge Structure — only for workflows using DKS pattern, optional)
- [ ] DKS construction step: Run P1 validation: `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir .`
- [ ] Confirm P1 validation result `valid: true` (DK1-DK5 all pass)
- [ ] DKS reference step (artifact contains `[dks:xxx]` markers): Run P1 cross-validation: `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir . --check-output --step N`
- [ ] Confirm P1 cross-validation result `valid: true` (including DK6-DK7)

### After Step Completion (pACS — perform after Verification Gate passes)
- [ ] Answer 3 Pre-mortem Protocol questions (AGENTS.md §5.4)
- [ ] Score F, C, L 3 dimensions → derive pACS = min(F, C, L)
- [ ] Generate `pacs-logs/step-N-pacs.md`
- [ ] Update SOT `pacs` field (current_step_score, dimensions, weak_dimension, history)
- [ ] If pACS RED (< 50):
  - [ ] Check + consume P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate pacs --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** (see diagnosis subsection below) → rework + re-score based on diagnosis
  - [ ] `can_retry: false` → escalate to user (retry budget exhausted, do not increment counter)
- [ ] If pACS YELLOW (50-69): record weak dimension in Decision Log then proceed
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_pacs.py --step N --check-l0 --project-dir .`
- [ ] Confirm P1 validation result `valid: true` (PA1-PA7 + L0 all pass)
- [ ] Record artifact path in SOT `outputs`
- [ ] Increment SOT `current_step` by +1
- [ ] `(human)` step: generate `autopilot-logs/step-N-decision.md`
- [ ] `(human)` step: add to SOT `auto_approved_steps`

### `(team)` Step Additional Checklist
- [ ] Immediately after `TeamCreate` → record SOT `active_team` (name, status, tasks_pending)
- [ ] Each Teammate self-verifies their Task against verification criteria before reporting (L1 — AGENTS.md §5.3)
- [ ] Each Teammate performs pACS self-rating after L1 pass (L1.5 — complete within session, include score in report message)
- [ ] When each Teammate completes → Team Lead performs comprehensive verification against step criteria (L2) + derives step pACS
- [ ] L2 FAIL or Teammate pACS RED → SendMessage with specific feedback + re-execution instruction
- [ ] When each Teammate completes → update SOT `active_team.tasks_completed` + `completed_summaries`
- [ ] When all Tasks complete → record SOT `outputs`, increment `current_step` by +1, set `active_team.status` → `all_completed`
- [ ] Immediately after `TeamDelete` → move SOT `active_team` → `completed_teams`
- [ ] Confirm Teammate artifacts include Decision Rationale + Cross-Reference Cues

### After Step Completion (Adversarial Review — only for steps with `Review: @reviewer|@fact-checker`)
- [ ] Call the agent specified in `Review:` field as a Sub-agent (recommended: `isolation: "worktree"` — protects Orchestrator context, details: `reviewer.md § Context Isolation`)
- [ ] Save review report to `review-logs/step-N-review.md`
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_review.py --step N --project-dir . --check-pacs-arithmetic`
- [ ] Confirm P1 validation result `valid: true` (R1-R5 all pass)
- [ ] Check Verdict:
  - [ ] PASS → proceed to next step (including Translation)
  - [ ] FAIL → Check + consume P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate review --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** (see diagnosis subsection below) → rework based on diagnosis
  - [ ] `can_retry: false` → escalate to user (retry budget exhausted, do not increment counter)
- [ ] If pACS Delta ≥ 15 → record in Decision Log + document recalibration rationale
- [ ] Do not execute Translation when Review is in FAIL state

### Quality Gate FAIL Diagnosis (Abductive Diagnosis — perform when retry is possible)
- [ ] Step A — P1 pre-evidence collection: `python3 .claude/hooks/scripts/diagnose_context.py --step N --gate {verification|pacs|review} --project-dir .`
- [ ] Check Fast-Path: `fast_path.eligible == true` → FP1/FP2: re-execute immediately, FP3: escalate to user
- [ ] If no Fast-Path match → Step B — LLM diagnosis: analyze root cause based on evidence bundle + hypothesis priority
- [ ] Generate diagnosis log: `diagnosis-logs/step-N-{gate}-{timestamp}.md`
- [ ] Step C — P1 post-validation: `python3 .claude/hooks/scripts/validate_diagnosis.py --step N --gate {verification|pacs|review} --project-dir .`
- [ ] Confirm P1 validation result `valid: true` (AD1-AD10 all pass)
- [ ] Execute rework based on selected hypothesis (H1/H2/H3/H4) from diagnosis

### After Step Completion (Translation — only for steps with `Translation: @translator`)
- [ ] Call `@translator` sub-agent (include reference to `translations/glossary.yaml`)
- [ ] Confirm translated file (`*.ko.md`) exists on disk
- [ ] Confirm translated file is non-empty
- [ ] Record translation path in SOT `outputs.step-N-ko`
- [ ] Confirm `translations/glossary.yaml` is updated
- [ ] Translation pACS scoring complete (Ft/Ct/Nt — `@translator` Step 4, AGENTS.md §5.4)
- [ ] Translation pACS log generated (`pacs-logs/step-N-translation-pacs.md`)
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_translation.py --step N --project-dir . --check-pacs --check-sequence`
- [ ] Confirm P1 validation result `valid: true` (T1-T9 + sequence all pass)

---

## NEVER DO

- Do not increment `current_step` by 2 or more at once
- Do not proceed to the next step without an artifact
- Do not abbreviate because "it's automated" — violation of Absolute Standard 1
- Do not ignore `(hook)` exit code 2 blocks
- Do not let `(team)` Teammates modify SOT directly — only Team Lead updates SOT
- Do not initialize `active_team` as empty object when restoring session — preserve existing `completed_summaries` (conservative resume protocol)
- Do not proceed to the next step while Verification criteria are FAIL — retry up to 10 times (15 when ULW active), then escalate to user
- Do not record "all PASS" for Verification criteria falsely — each criterion requires specific Evidence
- Do not skip Pre-mortem Protocol and assign only a pACS score — weakness recognition is the premise of the score
- Do not run pACS alone without a Verification Gate — L1 pass is the premise of L1.5
- Do not assign 90+ scores for all pACS dimensions — score must be consistent with weaknesses identified in Pre-mortem
- Do not execute Translation when Review is in FAIL state — Review PASS is the premise of Translation
- Do not process Review with 0 issues as PASS — P1 validation automatically rejects (R5 check)
- Do not score Reviewer pACS after referencing Generator pACS — independent scoring is required
- Do not retry a quality gate failure with the same approach without diagnosis — Abductive Diagnosis or Fast-Path is required
- Do not record only 1 hypothesis in the diagnosis log — minimum 2 hypotheses for comparison (AD8)
- Do not select the same hypothesis 3 consecutive times in diagnosis — FP3 escalation (I-3 integration)
