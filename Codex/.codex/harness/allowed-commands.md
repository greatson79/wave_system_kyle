# Allowed Command Policy

This file documents command intent. It does not grant shell permissions by
itself; agents must still follow the active sandbox and approval rules.

## Usually Safe Read-Only Commands

- `git status --short`
- `git diff --stat`
- `git diff`
- `rg --files`
- `rg <pattern>`
- `find . -maxdepth <n> -type f`
- Package-manager script listing commands, when read-only.

## Commands That Need Context

- Test commands.
- Lint commands.
- Typecheck commands.
- Build commands.
- Dev servers.
- Formatters.

Run these only after identifying the project conventions and expected side
effects.

## Commands Requiring Explicit Approval

- Dependency installation or upgrade.
- Network access not already approved by the user.
- Writes outside the workspace.
- Production deployment or release commands.
- Database migrations against non-local targets.
- Credential or secret management.
- Destructive commands such as deleting broad paths, `git reset --hard`, or
  `git clean`.

