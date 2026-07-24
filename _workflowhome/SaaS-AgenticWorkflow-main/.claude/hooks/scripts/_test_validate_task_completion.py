#!/usr/bin/env python3
"""
TDD Tests for validate_task_completion.py

Tests task completion validation hook:
  - Status=completed with missing output → warning (exit 0)
  - Status=completed with valid output → no warning (exit 0)
  - Status=in_progress → no check (exit 0)
  - Empty/malformed input → exit 0

All cases exit 0 (warning-only hook, never blocks).

P1 Compliance: Tests use mock stdin and temp files.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATE_TASK = os.path.join(SCRIPT_DIR, "validate_task_completion.py")


def _run_hook(tool_input_dict):
    """Run validate_task_completion.py with simulated PostToolUse payload."""
    payload = json.dumps({
        "tool_name": "TaskUpdate",
        "tool_input": tool_input_dict,
    })
    result = subprocess.run(
        [sys.executable, VALIDATE_TASK],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.returncode, result.stderr


class TestCompletedTask(unittest.TestCase):
    def test_always_exit_0(self):
        """Hook should never block (exit 0 always)."""
        code, _ = _run_hook({
            "taskId": "1",
            "status": "completed",
            "metadata": {"output_path": "/nonexistent/file.md"},
        })
        self.assertEqual(code, 0)

    def test_warns_missing_output(self):
        code, stderr = _run_hook({
            "taskId": "1",
            "status": "completed",
            "metadata": {"output_path": "/nonexistent/file.md"},
        })
        self.assertEqual(code, 0)
        self.assertIn("WARNING", stderr)

    def test_no_warning_valid_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("x" * 200)
            tmp_path = f.name
        try:
            code, stderr = _run_hook({
                "taskId": "1",
                "status": "completed",
                "metadata": {"output_path": tmp_path},
            })
            self.assertEqual(code, 0)
            self.assertNotIn("WARNING", stderr)
        finally:
            os.unlink(tmp_path)

    def test_warns_small_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("tiny")
            tmp_path = f.name
        try:
            code, stderr = _run_hook({
                "taskId": "1",
                "status": "completed",
                "metadata": {"output_path": tmp_path},
            })
            self.assertEqual(code, 0)
            self.assertIn("WARNING", stderr)
        finally:
            os.unlink(tmp_path)


class TestNonCompletedStatus(unittest.TestCase):
    def test_in_progress_no_check(self):
        code, stderr = _run_hook({
            "taskId": "1",
            "status": "in_progress",
        })
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")

    def test_pending_no_check(self):
        code, stderr = _run_hook({
            "taskId": "1",
            "status": "pending",
        })
        self.assertEqual(code, 0)


class TestEdgeCases(unittest.TestCase):
    def test_empty_stdin(self):
        result = subprocess.run(
            [sys.executable, VALIDATE_TASK],
            input="",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)

    def test_malformed_json(self):
        result = subprocess.run(
            [sys.executable, VALIDATE_TASK],
            input="not json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)

    def test_no_metadata(self):
        """No metadata/output_path → no warning, just exit 0."""
        code, stderr = _run_hook({
            "taskId": "1",
            "status": "completed",
        })
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
