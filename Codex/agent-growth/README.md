# Agent Growth

`agent-growth/` is a local, Hermes-inspired growth layer for this Codex
workspace. It turns experience notes into durable project memory, skill drafts,
curation metadata, and tick reports.

It is deliberately small and safe:

- no server
- no dependency install
- no external API calls
- no credential changes
- no automatic deletion

## Quick Start

Check structure:

```bash
python3 scripts/growth-tick.py --check
```

Run one local growth tick:

```bash
python3 scripts/growth-tick.py
```

Add a new experience note:

```text
agent-growth/inbox/YYYY-MM-DD-short-topic.md
```

Use these prefixes inside the note:

```text
Memory: Something future agents should remember.
Lesson: A failure mode and the fix.
Preference: A user preference to preserve.
Skill: a-new-skill-name
```

## Outputs

- `agent-growth/memory/MEMORY.md`: durable project memory.
- `agent-growth/skills/*/SKILL.md`: reusable procedures.
- `agent-growth/skills/.usage.json`: skill curation metadata.
- `agent-growth/reports/tick-*.md`: human-readable tick reports.
- `agent-growth/runs/ledger.jsonl`: machine-readable tick ledger.
- `agent-growth/state/state.json`: processed note hashes and tick counters.
