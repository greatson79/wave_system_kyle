# Quality Gates

Use these gates to decide what must be verified before an AI-assisted change is
complete.

## Gate 0: Harness-Only Change

Applies to documentation, checklists, and agent process files.

Required:

- Files are scoped to harness or documentation paths.
- No application behavior is changed.
- Harness check script passes if available.

## Gate 1: Local Behavior Change

Applies to a small bug fix or isolated UI/API behavior.

Required:

- A focused test, characterization check, or manual reproduction note.
- Relevant lint/typecheck if the project has one.
- No unrelated files changed.

## Gate 2: Shared Contract Change

Applies to shared libraries, API contracts, data models, routing, build config,
or cross-module behavior.

Required:

- Focused tests for the changed contract.
- Relevant integration or build check.
- Callers or consumers reviewed.
- Migration or compatibility note if needed.

## Gate 3: High-Risk Change

Applies to auth, secrets, payments, deletion, production infra, migrations, or
privacy-sensitive behavior.

Required:

- Explicit user approval or risk acceptance.
- Tests or dry-run evidence.
- Rollback or recovery note.
- No hidden dependency or credential changes.

