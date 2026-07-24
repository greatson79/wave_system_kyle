#!/usr/bin/env python3
"""
PreToolUse Hook — SOT Write Blocker (validate_sot_write.py)

Blocks direct Write tool access to SOT files (.claude/state.yaml|yml|json).
All SOT mutations MUST go through sot_manager.py.

Triggered by: PreToolUse with matcher "Write"
Exit codes:
    0 — file is NOT a SOT file, allow write
    2 — file IS a SOT file, BLOCK write (Claude self-corrects)

Part of 3-layer SOT write protection:
  Layer 1: THIS SCRIPT — blocks Write tool → state.yaml
  Layer 2: block_destructive_commands.py — blocks Bash redirect → state.yaml
  Layer 3: Architectural invariant — hooks are SOT read-only

P1 Compliance: Deterministic path matching. No AI judgment.
"""

import json
import os
import re
import sys


# SOT file patterns to block
SOT_PATTERNS = [
    re.compile(r"\.claude[/\\]state\.(yaml|yml|json)$"),
]


def is_sot_file(file_path):
    """Check if a file path targets a SOT file.

    Returns True if the path matches any SOT file pattern.
    """
    if not file_path:
        return False

    # Normalize path
    normalized = file_path.replace("\\", "/")

    for pattern in SOT_PATTERNS:
        if pattern.search(normalized):
            return True
    return False


def main():
    """Read PreToolUse JSON from stdin, block Write to SOT files."""
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        payload = json.loads(stdin_data)
        file_path = payload.get("tool_input", {}).get("file_path", "")

        if not file_path:
            sys.exit(0)

    except (json.JSONDecodeError, KeyError, TypeError):
        # Malformed input — don't block, exit cleanly
        sys.exit(0)

    if is_sot_file(file_path):
        print(
            "SOT WRITE BLOCKED: Direct Write to SOT file is not allowed.\n"
            "Use sot_manager.py for all SOT mutations:\n"
            "  python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step N --output PATH\n"
            "  python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-status STATUS\n"
            f"Attempted target: {file_path}",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Safety-first: never block Claude on unexpected internal errors
        sys.exit(0)
