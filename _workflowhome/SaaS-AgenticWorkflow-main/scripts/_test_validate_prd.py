#!/usr/bin/env python3
"""TDD Tests for validate_prd_structure.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_prd_structure.py")
PRD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "coding-resource", "PRD.md")


def _run(input_path):
    cmd = [sys.executable, SCRIPT, "--input", input_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw": result.stdout, "err": result.stderr}
    return result.returncode, data


class TestWithRealPRD(unittest.TestCase):
    """Test against the actual PRD.md if available."""

    def setUp(self):
        if not os.path.exists(PRD_PATH):
            self.skipTest("PRD.md not found")
        self.code, self.data = _run(PRD_PATH)

    def test_finds_all_16_headings(self):
        checks = self.data.get("checks", {})
        headings = checks.get("headings", {})
        self.assertEqual(headings.get("found", 0), 16)
        self.assertEqual(headings.get("missing", [1]), [])

    def test_has_code_blocks(self):
        checks = self.data.get("checks", {})
        self.assertTrue(checks.get("code_blocks", {}).get("passed", False))

    def test_has_mermaid(self):
        checks = self.data.get("checks", {})
        self.assertTrue(checks.get("mermaid", {}).get("passed", False))


class TestWithMockContent(unittest.TestCase):
    def _write_mock(self, content):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_missing_headings_detected(self):
        content = "## 1. First\nContent\n## 3. Third\nContent\n"
        path = self._write_mock(content)
        try:
            code, data = _run(path)
            missing = data["checks"]["headings"]["missing"]
            self.assertIn(2, missing)  # section 2 is missing
        finally:
            os.unlink(path)

    def test_placeholder_detected(self):
        # Build content with all 16 headings + a TODO
        lines = []
        for i in range(1, 17):
            lines.append(f"## {i}. Section {i}\nContent for section {i}\n")
        lines.append("\nTODO: fix this\n")
        lines.append("```typescript\nconst x = 1;\n```\n")
        lines.append("```mermaid\ngraph TD\n```\n")
        content = "\n".join(lines) + "\n" * 2500
        path = self._write_mock(content)
        try:
            code, data = _run(path)
            self.assertFalse(data["checks"]["no_placeholders"]["passed"])
        finally:
            os.unlink(path)

    def test_min_lines_check(self):
        content = "## 1. First\nShort\n"
        path = self._write_mock(content)
        try:
            code, data = _run(path)
            self.assertFalse(data["checks"]["min_lines"]["passed"])
        finally:
            os.unlink(path)


class TestMissingInput(unittest.TestCase):
    def test_nonexistent_file(self):
        code, data = _run("/nonexistent/file.md")
        self.assertEqual(code, 1)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
