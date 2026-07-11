# Codex Growth Architecture

This workspace is a local Codex operating root with a safety harness and a
Hermes-inspired growth layer. The goal is not to install Hermes inside this
folder. The goal is to adapt its closed learning loop into files that Codex can
read, run, audit, and improve over time.

## Current Shape

- `AGENTS.md` is the top-level operating contract for agents.
- `.codex/harness/` contains the existing safety harness docs.
- `scripts/agent-harness-check.sh` validates the agent-facing guardrails.
- `bible-quiz-app/` and `ai_basic_03_claude_projects_cards/` are existing
  deliverable areas and are outside this setup unless a task names them.
- `agent-growth/` is the new growing-agent layer.
- `.agents/skills/` is the publication target for reviewed Codex skills.

## Hermes Pattern Adapted Here

Hermes describes a built-in learning loop made of context files, durable
session storage, persistent memory, skill creation, skill curation, automation,
and auditable background reviews. This folder mirrors that pattern with a
conservative local loop:

1. Observe local context and inbox notes.
2. Reflect on reusable lessons.
3. Distill durable project memory.
4. Create or preserve skill drafts.
5. Curate skill metadata without deleting by default.
6. Persist a tick report and machine-readable ledger entry.

The loop is intentionally file based. It starts no server, installs no
dependency, calls no external API, and makes no hidden credential changes.

## Growth Layer

```text
agent-growth/
  README.md
  loop-spec.md
  config.json
  AGENTS.md
  inbox/
  memory/
    MEMORY.md
  skills/
    harness-first-development/
      SKILL.md
  state/
    state.json
  reports/
  runs/
  templates/
    skill/
      SKILL.md
  gpts/
    raw/
    normalized/
    reviews/
    publication-queue/
.agents/
  skills/
```

## My GPTs Merge Path

My GPTs instructions are imported through a staging path instead of being pasted
directly into the operating contract:

1. Preserve the raw instructions in `agent-growth/gpts/raw/`.
2. Normalize them into structured JSON under `agent-growth/gpts/normalized/`.
3. Create draft skills under `agent-growth/skills/`.
4. Review risks and conflicts under `agent-growth/gpts/reviews/`.
5. Promote only reviewed skills to `.agents/skills/`.
6. Record lessons in `agent-growth/inbox/` so the growth tick can update memory.

## One Tick

Run a deterministic tick with:

```bash
python3 scripts/growth-tick.py
```

Run a non-mutating structure check with:

```bash
python3 scripts/growth-tick.py --check
```

The harness check calls the non-mutating check. A mutating tick is a deliberate
operation that processes `agent-growth/inbox/*.md` into memory entries, skill
drafts, usage metadata, a report, and a ledger record.

## Risk Model

- Default change class: `docs` or `characterization`.
- High-risk areas are out of scope unless the user explicitly asks for them.
- The curator does not archive or delete skills unless `archive_enabled` is
  turned on in `agent-growth/config.json`.
- Inbox notes are never deleted by the tick. Processed note hashes are recorded
  in `agent-growth/state/state.json`.
