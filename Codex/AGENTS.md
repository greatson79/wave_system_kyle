# AI Agent Development Harness

This repository uses a harness-first workflow for AI-assisted engineering.
Agents must treat this file as the top-level operating contract before making
code changes.

## Prime Directive

Do not start application feature development until the harness checks, repo
orientation, and change-safety protocol have been followed.

## Core Operating Principles

These principles apply before any task-specific workflow.

1. **Thinking before coding** - Understand intent, constraints, and impact
   before editing. If the request or source of truth is ambiguous, stop and ask
   instead of guessing.
2. **Simplicity first** - Prefer the smallest clear solution. Do not add
   speculative extensibility, unnecessary abstraction, or broad frameworks. If a
   200-line solution can safely become 50 clear lines, choose the smaller shape.
3. **Surgical changes** - Touch only the files and lines required for the task.
   Do not modify working functions, comments, formatting, or nearby code for
   cleanup. Report optional improvements before changing them.
4. **Goal-driven execution** - Work against explicit success criteria. When a
   reproduction test, characterization check, or acceptance criterion is given,
   verify, iterate, and re-run checks until it passes or a real blocker is
   found.

## Required Workflow

1. Read `AGENTS.md`.
2. Read `.codex/harness/safe-development-protocol.md`.
3. Read `ARCHITECTURE.md` when changing process, harness, or agent behavior.
4. Clarify ambiguity before editing; do not invent missing requirements.
5. Inspect repository structure and current git status.
6. Create or update a short task plan before editing code.
7. Prefer tests or characterization checks before behavior changes.
8. Keep edits scoped to the requested task.
9. Run the relevant verification commands before claiming completion.
10. Report changed files, verification results, and any residual risk.

## Growing Agent Layer

This workspace has a local Hermes-inspired growth layer under `agent-growth/`.
It is file based and intentionally conservative: no background daemon, no
network calls, no dependency install, and no automatic deletion.

Use it this way:

- Read `ARCHITECTURE.md` and `agent-growth/loop-spec.md` before changing the
  growth loop.
- Add reusable lessons to `agent-growth/inbox/*.md` using `Memory:`,
  `Lesson:`, `Preference:`, or `Skill:` prefixes.
- Run `python3 scripts/growth-tick.py` to process one closed-loop tick.
- Run `python3 scripts/growth-tick.py --check` for a non-mutating health check.
- Keep curation non-destructive unless the user explicitly approves archival.

## Safety Rules

- Never overwrite or revert user changes unless the user explicitly requests it.
- Never run destructive commands such as `git reset --hard`, `git clean`, or
  broad deletes without explicit approval.
- Do not install dependencies, call external services, or modify credentials
  without user approval.
- Do not change production configuration, secrets, migrations, billing logic,
  authentication, or data deletion paths without an explicit risk review.
- Do not use application feature work to "clean up" unrelated code.
- If the repo is dirty, identify which changes are yours and which appear to
  preexist.

## Change Classes

Use the smallest class that fits the request:

- `docs`: documentation, harness, plans, checklists.
- `characterization`: tests or scripts that describe current behavior.
- `bugfix`: narrow correction to existing behavior.
- `feature`: new behavior requested by the user.
- `refactor`: structure change without intended behavior change.
- `infra`: build, CI, dependencies, deployment, or environment change.

Feature work should not begin until the harness is in place and the user asks
for feature development.

## Required Completion Report

Every engineering task should end with:

- What changed.
- Where it changed.
- What verification ran.
- What could not be verified.
- Any user decisions still needed.
