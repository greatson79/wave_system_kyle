#!/usr/bin/env python3
"""
TDD Tests for validate_sot_write.py

Tests SOT write blocking:
  - Write to .claude/state.yaml → blocked (exit 2)
  - Write to .claude/state.yml → blocked
  - Write to .claude/state.json → blocked
  - Write to other files → allowed (exit 0)
  - Empty/malformed input → allowed (exit 0)

P1 Compliance: Tests run with mock stdin — no real SOT affected.
"""

import json
import os
import subprocess
import sys
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATE_SOT_WRITE = os.path.join(SCRIPT_DIR, "validate_sot_write.py")


def _run_hook(tool_input_dict):
    """Run validate_sot_write.py with simulated PreToolUse payload."""
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": tool_input_dict,
    })
    result = subprocess.run(
        [sys.executable, VALIDATE_SOT_WRITE],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.returncode, result.stderr


class TestSotBlocking(unittest.TestCase):
    def test_blocks_state_yaml(self):
        code, stderr = _run_hook({"file_path": "/project/.claude/state.yaml"})
        self.assertEqual(code, 2)
        self.assertIn("SOT WRITE BLOCKED", stderr)

    def test_blocks_state_yml(self):
        code, stderr = _run_hook({"file_path": "/project/.claude/state.yml"})
        self.assertEqual(code, 2)

    def test_blocks_state_json(self):
        code, stderr = _run_hook({"file_path": "/project/.claude/state.json"})
        self.assertEqual(code, 2)

    def test_blocks_nested_path(self):
        code, _ = _run_hook({
            "file_path": "/Users/dev/project/.claude/state.yaml"
        })
        self.assertEqual(code, 2)

    def test_blocks_backslash_path(self):
        code, _ = _run_hook({
            "file_path": "C:\\project\\.claude\\state.yaml"
        })
        self.assertEqual(code, 2)


class TestAllowedFiles(unittest.TestCase):
    def test_allows_regular_file(self):
        code, _ = _run_hook({"file_path": "src/main.py"})
        self.assertEqual(code, 0)

    def test_allows_other_yaml(self):
        code, _ = _run_hook({"file_path": ".claude/settings.yaml"})
        self.assertEqual(code, 0)

    def test_allows_state_in_other_dir(self):
        code, _ = _run_hook({"file_path": "config/state.yaml"})
        self.assertEqual(code, 0)

    def test_allows_sot_manager(self):
        code, _ = _run_hook({
            "file_path": ".claude/hooks/scripts/sot_manager.py"
        })
        self.assertEqual(code, 0)


class TestEdgeCases(unittest.TestCase):
    def test_empty_stdin(self):
        result = subprocess.run(
            [sys.executable, VALIDATE_SOT_WRITE],
            input="",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)

    def test_malformed_json(self):
        result = subprocess.run(
            [sys.executable, VALIDATE_SOT_WRITE],
            input="not json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)

    def test_missing_file_path(self):
        code, _ = _run_hook({})
        self.assertEqual(code, 0)

    def test_empty_file_path(self):
        code, _ = _run_hook({"file_path": ""})
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
