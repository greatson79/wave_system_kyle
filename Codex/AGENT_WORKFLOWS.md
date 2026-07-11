# Agent Workflows

This file defines how this workspace connects global rules, growth memory, and
published skills. It is intentionally small; detailed task logic belongs in
skills, references, scripts, and templates.

## Default Development Workflow

Use for feature work and behavior changes.

1. Load `AGENTS.md`, `ARCHITECTURE.md`, and this file.
2. Read relevant docs and source files.
3. Stop and ask if intent, source of truth, or success criteria are ambiguous.
4. Create or update an exec plan before editing.
5. Use requirement and design skills when scope is unclear or user-facing.
6. Choose the simplest implementation that satisfies the goal.
7. Use test-first implementation for feature and bugfix work.
8. Make surgical edits only; report optional cleanups before making them.
9. Run the narrowest reliable verification, then broader checks if needed.
10. Iterate until the reproduction test or success criterion passes, or report a
    concrete blocker.
11. Record reusable lessons in `agent-growth/inbox/`.
12. Report changed files, checks, residual risk, and decisions needed.

## My GPTs Import Workflow

Use when the user provides My GPTs instructions for conversion into Codex
skills or workflows.

1. Store the untouched source under `agent-growth/gpts/raw/`.
2. Normalize it into `agent-growth/gpts/normalized/<name>.json`.
3. Classify content into global rules, workflows, skill candidates, references,
   scripts, templates, and conflicts.
4. Keep drafts in `agent-growth/skills/` until reviewed.
5. Promote only reviewed skills to `.agents/skills/`.
6. Record the promotion decision in `agent-growth/gpts/reviews/`.
7. Run `python3 scripts/growth-tick.py --check` and
   `sh scripts/agent-harness-check.sh`.

## Reformed Sermon Workflow

Use for 개혁주의 복음 중심 설교 preparation.

1. Use `reformed-sermon-workflow` for full-process orchestration.
2. Use `biblical-text-research` for passage study and redemptive-historical notes.
3. Use `cmt-fcf-hp-builder` for Subject, Complement, CMT, FCF, and HP.
4. Use `christ-centered-sermon-arc` for Moral Principle, Human Effort Failure,
   Christ's person and work, Hermeneutical Points, and gospel application.
5. Use `sermon-manuscript-builder` for outlines, manuscripts, applications, and
   audience-facing sermon materials.
6. Use `sermon-theology-reviewer` before finalizing or when the user asks for
   review.
7. Do not run the whole workflow when the user asks for only one stage.

## Bugfix Workflow

1. Reproduce or characterize the bug.
2. Add a failing regression test when practical.
3. Apply the smallest fix.
4. Do not touch unrelated working code, comments, or formatting.
5. Run focused verification.
6. Iterate until the regression passes or a concrete blocker is identified.
7. Record any durable failure mode in `agent-growth/inbox/`.

## Drive Data Report Workflow

Use `drive-data-report-workflow` when a task starts from Google Drive, Google
Sheets, Excel, CSV, course application, survey, or feedback files and should end
with cleaned data, a report, PDF, or visualization.

1. Scope the source account, folder/query, file types, and output format.
2. Build a source manifest before analyzing contents.
3. Normalize spreadsheet rows before interpreting or comparing them.
4. Keep private respondent details out of public visuals by default.
5. Verify each created sheet, PDF, image, and final path before handoff.

## Docs And Harness Workflow

1. Treat the change as `docs` or `characterization`.
2. Do not require feature TDD or worktree setup unless code behavior changes.
3. Run growth and harness checks.
4. Report limitations plainly.
