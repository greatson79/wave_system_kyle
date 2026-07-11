# Agent Skill Index

This index separates draft growth-loop skills from Codex-published skills.

## Published Skills

Published skills live under `.agents/skills/` and are intended for Codex
auto-discovery.

- `reformed-sermon-workflow`: full sermon-preparation orchestration.
- `biblical-text-research`: passage study for sermon preparation.
- `cmt-fcf-hp-builder`: Subject, Complement, CMT, FCF, and HP engine.
- `christ-centered-sermon-arc`: gospel-centered sermon logic and application.
- `sermon-manuscript-builder`: sermon outline, manuscript, and applied material writing.
- `sermon-theology-reviewer`: theological and quality review.
- `drive-data-report-workflow`: Google Drive/Sheets/Excel data cleanup, reports, and visualization.

## Draft Skills

Draft or learning-loop skills live under `agent-growth/skills/`.

- `harness-first-development`: local guardrail workflow for this Codex folder.
- `reformed-sermon-workflow`
- `biblical-text-research`
- `cmt-fcf-hp-builder`
- `christ-centered-sermon-arc`
- `sermon-manuscript-builder`
- `sermon-theology-reviewer`
- `drive-data-report-workflow`

## Promotion Rules

A draft skill can be published when:

- Its frontmatter has clear `name` and `description` fields.
- The body is concise and operational.
- Long examples or source material are moved to `references/`.
- Scripts are executable or clearly marked as dry-run only.
- A review file exists under `agent-growth/gpts/reviews/` when derived from a
  My GPT.
- `python3 scripts/growth-tick.py --check` passes.
- `sh scripts/agent-harness-check.sh` passes.
