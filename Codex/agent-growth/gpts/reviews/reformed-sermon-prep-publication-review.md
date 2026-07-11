# Skill Publication Review

## Source

- GPT name: ReformedGospelCenteredSermonSystem_Project_v1.3
- Raw path: `agent-growth/gpts/raw/reformed-gospel-centered-sermon-system-v1.3.xml`
- Normalized path: `agent-growth/gpts/normalized/reformed-gospel-centered-sermon-system-v1.3.json`
- Candidate skills: `reformed-sermon-workflow`, `biblical-text-research`, `cmt-fcf-hp-builder`, `christ-centered-sermon-arc`, `sermon-manuscript-builder`, `sermon-theology-reviewer`

## Decision

- Status: publish
- Publish target: `.agents/skills/`
- Reviewer: Codex
- Reviewed at: 2026-07-04

## Checks

- [x] Raw source preserved.
- [x] No secrets or credentials included.
- [x] Global rules were not duplicated into every skill body.
- [x] Skill frontmatter has clear `name` and `description`.
- [x] Long source material is moved to shared `references/`.
- [x] No live scripts or external APIs are introduced.
- [x] Conflicts with `AGENTS.md` are resolved by using scope discipline and 확인 필요 marking.
- [x] Verification command is documented.

## Notes

The six-skill split is approved because sermon preparation has distinct stages, but each skill remains small. Shared references live under `reformed-sermon-workflow/references/`; other sermon skills read those files through relative paths.
