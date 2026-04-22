#!/usr/bin/env python3
"""TDD Tests for merge_prd_sections.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merge_prd_sections.py")


def _run(input_dir, output_path):
    cmd = [sys.executable, SCRIPT, "--input-dir", input_dir, "--output", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw": result.stdout, "err": result.stderr}
    return result.returncode, data


def _create_section_files(tmpdir):
    """Create mock section files."""
    files = {
        "prd-sections-1-5.md": "## 1. Exec Summary\nContent 1\n\n## 2. Problem\nContent 2\n",
        "prd-sections-6-8.md": "## 6. Core Features\nContent 6\n",
        "prd-sections-9-12.md": "## 9. Data Sources\nContent 9\n",
        "prd-sections-13-16.md": "## 13. Business\nContent 13\n",
    }
    for name, content in files.items():
        with open(os.path.join(tmpdir, name), "w") as f:
            f.write(content)


class TestMerge(unittest.TestCase):
    def test_merges_all_4_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_section_files(tmpdir)
            output = os.path.join(tmpdir, "merged.md")
            code, data = _run(tmpdir, output)
            self.assertEqual(code, 0)
            self.assertEqual(data["sections_merged"], 4)
            self.assertEqual(data["missing_inputs"], [])
            self.assertTrue(os.path.exists(output))

    def test_merged_content_contains_all_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_section_files(tmpdir)
            output = os.path.join(tmpdir, "merged.md")
            _run(tmpdir, output)
            with open(output, "r") as f:
                content = f.read()
            self.assertIn("Exec Summary", content)
            self.assertIn("Core Features", content)
            self.assertIn("Business", content)

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Only create 2 of 4 files
            with open(os.path.join(tmpdir, "prd-sections-1-5.md"), "w") as f:
                f.write("content")
            with open(os.path.join(tmpdir, "prd-sections-6-8.md"), "w") as f:
                f.write("content")
            output = os.path.join(tmpdir, "merged.md")
            code, data = _run(tmpdir, output)
            self.assertEqual(code, 1)
            self.assertEqual(len(data["missing_inputs"]), 2)


class TestOutputStructure(unittest.TestCase):
    def test_json_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_section_files(tmpdir)
            output = os.path.join(tmpdir, "merged.md")
            code, data = _run(tmpdir, output)
            self.assertIn("output_path", data)
            self.assertIn("total_lines", data)
            self.assertIn("total_bytes", data)
            self.assertIn("sections_merged", data)
            self.assertGreater(data["total_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
