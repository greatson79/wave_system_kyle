#!/usr/bin/env python3
"""
PostToolUse Hook — Task Completion Validator (validate_task_completion.py)

When a TaskUpdate sets status="completed", validates that the task's
associated output file exists and meets minimum size requirements.

This is a WARNING-only hook (exit 0) — it does NOT block task completion.
It provides feedback to the orchestrator to catch missing outputs early.

Triggered by: PostToolUse with matcher "TaskUpdate"
Exit codes:
    0 — always (warning only, never blocks)

P1 Compliance: Deterministic file existence check.
SOT Compliance: Read-only — checks files, does not modify SOT.
"""

import json
import os
import sys

# Minimum file size for a valid output
MIN_OUTPUT_SIZE = 100


def main():
    """Read PostToolUse JSON from stdin, warn if completed task has no output."""
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        payload = json.loads(stdin_data)

        # PostToolUse payload format:
        # {"tool_name": "TaskUpdate", "tool_input": {...}, "tool_result": {...}}
        tool_input = payload.get("tool_input", {})

        # Only check when status is being set to "completed"
        new_status = tool_input.get("status", "")
        if new_status != "completed":
            sys.exit(0)

        # Extract task description for output path hints
        task_id = tool_input.get("taskId", "unknown")
        description = tool_input.get("description", "")

        # Look for file paths in the task description or metadata
        metadata = tool_input.get("metadata", {})
        output_path = metadata.get("output_path", "") if isinstance(metadata, dict) else ""

        if output_path:
            if not os.path.exists(output_path):
                print(
                    f"WARNING: Task #{task_id} marked completed but output "
                    f"file not found: {output_path}",
                    file=sys.stderr,
                )
            elif os.path.getsize(output_path) < MIN_OUTPUT_SIZE:
                size = os.path.getsize(output_path)
                print(
                    f"WARNING: Task #{task_id} output file too small "
                    f"({size} bytes, min {MIN_OUTPUT_SIZE}): {output_path}",
                    file=sys.stderr,
                )

    except (json.JSONDecodeError, KeyError, TypeError):
        # Malformed input — silently continue
        pass
    except Exception:
        # Safety-first: never fail on unexpected errors
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
