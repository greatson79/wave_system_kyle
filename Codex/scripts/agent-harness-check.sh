#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
cd "$ROOT_DIR"

fail() {
  printf '%s\n' "agent-harness-check: $1" >&2
  exit 1
}

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_file "AGENTS.md"
require_file ".codex/harness/safe-development-protocol.md"
require_file ".codex/harness/quality-gates.md"
require_file ".codex/harness/agent-checklist.md"
require_file ".codex/harness/change-report-template.md"
require_file ".codex/harness/repo-orientation-template.md"
require_file ".codex/harness/allowed-commands.md"
require_file ".codex/harness/harness-manifest.json"
require_file "ARCHITECTURE.md"
require_file "agent-growth/README.md"
require_file "agent-growth/loop-spec.md"
require_file "agent-growth/config.json"
require_file "agent-growth/state/state.json"
require_file "agent-growth/memory/MEMORY.md"
require_file "scripts/growth-tick.py"

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/growth-tick.py --check >/dev/null
else
  fail "python3 is required for growth tick validation"
fi

if command -v git >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git status --short --untracked-files=no -- "$(pwd -P)" >/dev/null
  fi
fi

printf '%s\n' "agent-harness-check: ok"
