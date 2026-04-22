# ULW (Ultrawork) Mode

> This document is the detailed specification for ULW mode.
> Separated from CLAUDE.md — reference when ULW is active.

## Overview

When a prompt includes `ulw`, **Ultrawork mode** is activated. ULW is a **thoroughness intensity overlay that is orthogonal to Autopilot**.

- **Autopilot** = automation axis (HOW) — skips `(human)` approvals
- **ULW** = thoroughness axis (HOW THOROUGHLY) — completes everything exhaustively, including error resolution

The two axes are independent, so any combination is valid:

|  | **ULW OFF** (normal) | **ULW ON** (maximum thoroughness) |
|---|---|---|
| **Autopilot OFF** | Standard conversational | Conversational + Sisyphus Persistence (3 retries) + mandatory task decomposition |
| **Autopilot ON** | Standard automated workflow | Automated workflow + Sisyphus reinforcement (3 retries) + team thoroughness |

## Two-Axis Comparison

| Axis | Concern | Activation | Deactivation | Scope |
|----|--------|--------|---------|----------|
| **Autopilot** | Automation (HOW) | SOT `autopilot.enabled: true` | SOT change | Workflow steps |
| **ULW** | Thoroughness (HOW THOROUGHLY) | `ulw` in prompt | Implicit (no `ulw` in new session = deactivated) | All tasks (conversational + workflow) |

## Activation Patterns

| User Command | Behavior |
|-----------|------|
| "ulw do this", "ulw refactor this" | Detect `ulw` in transcript → activate ULW mode |
| Prompt without `ulw` in a new session | ULW inactive (implicit deactivation — no explicit deactivation needed) |

## 3 Intensifier Rules

When ULW is activated, the following 3 intensifier rules are **overlaid onto the current context**:

| Intensifier | Description | Conversational Effect | Combined with Autopilot |
|----------|------|-----------|-------------------|
| **I-1. Sisyphus Persistence** | Up to 3 retries, each with a different approach. Report 100% completion or reason for impossibility. | On error, attempt up to 3 alternatives | Quality gate (Verification/pACS) retry limit: 10 → 15 |
| **I-2. Mandatory Task Decomposition** | TaskCreate → TaskUpdate → TaskList required | Force task decomposition for non-trivial work | No change (Autopilot already uses SOT-based tracking) |
| **I-3. Bounded Retry Escalation** | No more than 3 consecutive retries on the same target (quality gates use separate budget) — escalate to user if exceeded | Prevents infinite loops | Always respect Safety Hook blocks |

## Runtime Reinforcement Mechanisms

| Layer | Mechanism | Reinforcement |
|------|---------|----------|
| **Hook** (deterministic) | `_context_lib.py` — `detect_ulw_mode()` | Detect `ulw` via transcript regex |
| **Hook** (deterministic) | `generate_snapshot_md()` — snapshot | Preserve ULW state section at IMMORTAL priority |
| **Hook** (deterministic) | `extract_session_facts()` — Knowledge Archive | Tag `ulw_active: true` → queryable via RLM |
| **Hook** (deterministic) | `restore_context.py` — SessionStart | Inject 3 intensifier rules into context when ULW active (startup source excluded — implicit deactivation) |
| **Hook** (deterministic) | `_context_lib.py` — `check_ulw_compliance()` | Deterministically verify compliance with 3 intensifier rules → include warnings in snapshot IMMORTAL |
| **Hook** (deterministic) | `generate_context_summary.py` — Stop | ULW compliance safety net — stderr warning on violation |

## NEVER DO
- Do not retry the same target more than 3 consecutive times (quality gates use separate budget) — I-3 violation, escalate to user
- Do not override Safety Hook (`(hook)` exit code 2) blocks in the name of ULW
- Do not leave a Task as "partially complete" and stop while ULW is active — I-1 violation
- Do not give up on an error without attempting alternatives — I-1 violation
- Do not proceed implicitly without TaskCreate for non-trivial work — I-2 violation
