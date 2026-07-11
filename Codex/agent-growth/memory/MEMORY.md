# Growth Memory

This is the local project memory for the Codex workspace growth loop.

Use it for durable facts, conventions, repeated failure modes, tool quirks, and
completed work that should influence future runs in this folder. Keep entries
short and source-backed. Do not put secrets here.

## Tick 2026-07-04T08:45:40Z
- Memory: This Codex folder uses a harness-first workflow. Agents should read AGENTS.md, ARCHITECTURE.md, and agent-growth/loop-spec.md before behavior changes. (source: agent-growth/inbox/2026-07-04-bootstrap.md)
- Memory: The Hermes-inspired growth loop in this folder is local and file based. It does not start servers or install dependencies by default. (source: agent-growth/inbox/2026-07-04-bootstrap.md)
- Lesson: When this folder is nested under a larger git worktree, scope git status checks to the Codex folder path to avoid slow full-tree scans. (source: agent-growth/inbox/2026-07-04-bootstrap.md)

## Tick 2026-07-04T10:48:56Z
- Preference: Core work in this Codex folder must follow thinking before coding, simplicity first, surgical changes, and goal-driven execution. (source: agent-growth/inbox/2026-07-04-four-operating-principles.md)
- Preference: If intent, source of truth, or success criteria are ambiguous, stop and ask instead of guessing. (source: agent-growth/inbox/2026-07-04-four-operating-principles.md)
- Preference: Avoid speculative extensibility, unnecessary abstraction, and broad frameworks; choose the smallest clear solution. (source: agent-growth/inbox/2026-07-04-four-operating-principles.md)
- Preference: Keep edits surgical and do not touch working functions, comments, formatting, or nearby code for cleanup without reporting the improvement first. (source: agent-growth/inbox/2026-07-04-four-operating-principles.md)
- Preference: When success criteria, a reproduction test, or a characterization check exists, iterate and re-run verification until it passes or a concrete blocker is found. (source: agent-growth/inbox/2026-07-04-four-operating-principles.md)

## Tick 2026-07-04T11:14:14Z
- Memory: The Reformed gospel-centered sermon system is implemented as six skills: reformed-sermon-workflow, biblical-text-research, cmt-fcf-hp-builder, christ-centered-sermon-arc, sermon-manuscript-builder, and sermon-theology-reviewer. (source: agent-growth/inbox/2026-07-04-reformed-sermon-skills.md)
- Memory: Shared sermon references live under reformed-sermon-workflow/references and are read by the narrower sermon skills through relative paths. (source: agent-growth/inbox/2026-07-04-reformed-sermon-skills.md)
- Preference: For sermon tasks, do not force the full workflow when the user asks for only one stage such as CMT, FCF, HP, manuscript, or review. (source: agent-growth/inbox/2026-07-04-reformed-sermon-skills.md)
- Lesson: Keep CMT/FCF/HP rules in a dedicated reference because that engine has highest priority in the source GPT prompt. (source: agent-growth/inbox/2026-07-04-reformed-sermon-skills.md)
