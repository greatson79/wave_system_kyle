#!/usr/bin/env python3
"""TDD Tests for extract_prd_sections.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_prd_sections.py")
PRD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "coding-resource", "PRD.md")


def _run(input_path, output_dir):
    cmd = [sys.executable, SCRIPT, "--input", input_path, "--output-dir", output_dir]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw": result.stdout, "err": result.stderr}
    return result.returncode, data


class TestWithRealPRD(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(PRD_PATH):
            self.skipTest("PRD.md not found")
        self.tmpdir = tempfile.mkdtemp()
        self.code, self.data = _run(PRD_PATH, self.tmpdir)

    def test_exit_code_0(self):
        self.assertEqual(self.code, 0)

    def test_finds_16_sections(self):
        self.assertEqual(self.data["total_sections"], 16)

    def test_section_files_created(self):
        for section in self.data["sections"]:
            self.assertTrue(os.path.exists(section["path"]), f"Missing: {section['path']}")

    def test_section_numbers_sequential(self):
        nums = [s["number"] for s in self.data["sections"]]
        self.assertEqual(nums, list(range(1, 17)))

    def test_code_blocks_counted(self):
        self.assertGreater(self.data["code_blocks"], 0)

    def test_full_reference_created(self):
        self.assertTrue(os.path.exists(self.data["full_reference"]))


class TestWithMockPRD(unittest.TestCase):
    def test_extracts_3_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_prd = os.path.join(tmpdir, "mock.md")
            with open(mock_prd, "w") as f:
                f.write("# Title\n\n## 1. First\nContent A\n\n## 2. Second\nContent B\n\n## 3. Third\nContent C\n")
            outdir = os.path.join(tmpdir, "out")
            code, data = _run(mock_prd, outdir)
            self.assertEqual(code, 0)
            self.assertEqual(data["total_sections"], 3)

    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run("/nonexistent.md", tmpdir)
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
