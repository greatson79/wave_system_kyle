# Agent Growth Context

This directory stores the local growing-agent layer for the Codex workspace.
Treat it as project context and process state, not application code.

## Rules

- Do not delete inbox notes, reports, memory, or skills as part of routine work.
- Do not enable archival or destructive curation without explicit user approval.
- Keep growth loop changes file based and auditable.
- Use `python3 scripts/growth-tick.py --check` from the workspace root before
  claiming this layer is healthy.
- Use `python3 scripts/growth-tick.py` only when intentionally processing
  `agent-growth/inbox/*.md` into persistent state.

## Note Format

Write reusable lessons into `agent-growth/inbox/*.md` with simple prefixes:

```text
Memory: Durable fact, convention, or workaround to remember.
Lesson: A repeated failure mode and the fix.
Preference: User preference that should shape future work.
Skill: name-of-skill-to-create-or-keep
```
