# Growth Loop Spec

This spec defines the local closed learning loop for the Codex workspace.

## Inputs

- Root context: `AGENTS.md`, `ARCHITECTURE.md`, and harness docs.
- Inbox notes: `agent-growth/inbox/*.md`.
- Existing memory: `agent-growth/memory/MEMORY.md`.
- Existing skills: `agent-growth/skills/*/SKILL.md`.
- My GPTs import staging: `agent-growth/gpts/`.
- Config and state: `agent-growth/config.json` and
  `agent-growth/state/state.json`.

## Tick Contract

One tick must perform these steps in order:

1. Validate the required files and JSON state.
2. Read unprocessed inbox notes.
3. Extract durable memory lines from `Memory:`, `Lesson:`, and `Preference:`.
4. Create missing skill drafts for each `Skill:` line.
5. Refresh skill usage metadata.
6. Write one report under `agent-growth/reports/`.
7. Append one ledger entry under `agent-growth/runs/ledger.jsonl`.
8. Update `agent-growth/state/state.json`.

## Curation Policy

The curator records metadata every tick, but it does not archive or delete by
default. Archival requires all of the following:

- `archive_enabled` is true in `agent-growth/config.json`.
- The skill is not pinned.
- The skill exceeded `archive_after_days`.
- A report records the action.

## My GPTs Import Policy

My GPTs instructions must move through staging before they become active Codex
skills:

1. Raw text stays in `agent-growth/gpts/raw/`.
2. Structured extraction goes to `agent-growth/gpts/normalized/`.
3. Draft skills stay in `agent-growth/skills/`.
4. Publication reviews stay in `agent-growth/gpts/reviews/`.
5. Reviewed skills may be copied to `.agents/skills/`.

The tick may read staging metadata, but it must not publish or delete skills
without an explicit command.

## Non-Goals

- This is not a replacement for Codex memory.
- This is not a background daemon.
- This does not install Hermes.
- This does not run network, messaging, cron, or model-provider setup.

## Success Criteria

- `python3 scripts/growth-tick.py --check` exits 0.
- `sh scripts/agent-harness-check.sh` exits 0.
- A normal tick produces a report and ledger entry.
- Re-running the same tick does not duplicate already processed inbox memory.
