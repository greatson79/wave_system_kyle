---
name: harness-first-development
description: Use before engineering changes in this Codex workspace to preserve guardrails and growth-loop continuity.
---

# Harness First Development

## When to Use

Use this before changing code, process files, scripts, or agent-facing docs in
this workspace.

## Procedure

1. Read `AGENTS.md`.
2. Read `ARCHITECTURE.md`.
3. Read `.codex/harness/safe-development-protocol.md`.
4. Read `agent-growth/loop-spec.md`.
5. Inspect the requested scope and existing files.
6. Classify the change with the smallest fitting class.
7. Make a short plan before editing.
8. Keep edits scoped to named files and nearby process files.
9. Run `python3 scripts/growth-tick.py --check`.
10. Run `sh scripts/agent-harness-check.sh`.

## Pitfalls

- This folder is nested under a larger git worktree. Scope git checks to this
  folder when possible.
- Do not treat application deliverables as part of the growth layer unless the
  user explicitly names them.
- Do not enable destructive curation without explicit user approval.

## Verification

The growth layer is healthy when both commands exit 0:

```bash
python3 scripts/growth-tick.py --check
sh scripts/agent-harness-check.sh
```
