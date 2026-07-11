# Safe Development Protocol

This protocol is the minimum harness for AI agents working in this repository.
It is intentionally conservative and should be followed before and during every
engineering task.

## 1. Orientation

Before editing code, the agent should establish:

- Repository root.
- Main project type and package manager.
- Existing test commands.
- Existing lint, typecheck, build, or format commands.
- Git status and uncommitted files.
- Any user-provided files or instructions relevant to the task.

Record findings in the working notes or final response. Do not assume a command
exists just because it is common for the ecosystem.

If intent, data source, success criteria, or ownership is ambiguous, stop and
ask. Do not fill gaps by guessing.

## 2. Risk Scan

Classify the task using `AGENTS.md` change classes. Then scan whether the task
touches any of these high-risk areas:

- Authentication or authorization.
- Secrets, tokens, keys, or environment files.
- Payments, subscriptions, billing, or accounting.
- Data deletion, migrations, backup, restore, or irreversible writes.
- Production deployment, CI release, or infrastructure.
- User privacy, permissions, or external integrations.

If any high-risk area is involved, pause and create an explicit risk note before
implementation.

## 3. Plan

For non-trivial work, create a short plan with:

- Goal.
- Files or modules likely to change.
- Verification strategy.
- Known risks or assumptions.

Update the plan as facts change. A plan is not a substitute for inspection.
Prefer the simplest plan that can satisfy the goal. Do not introduce new
abstractions, frameworks, or speculative extension points unless the requested
behavior requires them.

## 4. Tests First When Practical

For bug fixes and behavior changes:

- Add or identify a failing test before implementation when practical.
- If tests are not available, create a characterization check or document the
  current behavior manually.
- Keep tests focused on the requested behavior.

For harness-only work, validate structure and scripts instead of adding app
behavior tests.

## 5. Edits

Make minimal, local edits. Prefer established project conventions. Avoid broad
renames, formatting churn, dependency changes, and unrelated refactors.

Agents should use patch-style edits for manual changes and should not rewrite
large files unless necessary.

Treat edits as surgical. Do not change working functions, comments, whitespace,
or nearby code for cleanup. If you notice an improvement outside the task, report
it separately before editing it.

## 6. Verification

Run the narrowest reliable checks first, then broader checks if the risk
justifies them:

- Unit or characterization tests for changed behavior.
- Lint or typecheck for changed language.
- Build or integration checks for shared contracts.
- Harness checks for agent safety files.

If a command fails, report the exact command and a concise explanation. Do not
claim completion without verification evidence.

When a reproduction test, characterization check, or acceptance criterion is
available, use it as the goal line. Iterate and re-run the relevant check until
it passes or until a concrete blocker is identified.

## 7. Handoff

At the end, summarize:

- Files changed.
- Behavioral impact.
- Commands run and outcomes.
- Known limitations.
- Recommended next safe step.
