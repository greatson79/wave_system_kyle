#!/usr/bin/env python3
"""
TDD Tests for manifest_generator.py

Tests manifest file generation for team steps:
  - Manifest created with correct format
  - File verification (existence, minimum size)
  - Missing files cause failure
  - JSON output structure
  - Manifest content includes file stats

P1 Compliance: Tests use temp directory — no real project files touched.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_GEN = os.path.join(SCRIPT_DIR, "manifest_generator.py")


def _run_manifest(step, project_dir, files):
    """Run manifest_generator.py. Returns (exit_code, parsed_json)."""
    cmd = [
        sys.executable,
        MANIFEST_GEN,
        "--step",
        str(step),
        "--project-dir",
        project_dir,
        "--files",
        files,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, data


def _create_file(project_dir, rel_path, content="x" * 200):
    abs_path = os.path.join(project_dir, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)


class TestManifestCreation(unittest.TestCase):
    def test_creates_manifest_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            _create_file(tmpdir, "b.md", "content " * 50)
            code, data = _run_manifest(2, tmpdir, "a.md,b.md")
            self.assertEqual(code, 0)
            self.assertTrue(data["valid"])
            manifest_path = os.path.join(tmpdir, data["manifest_path"])
            self.assertTrue(os.path.exists(manifest_path))

    def test_manifest_content_has_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            code, data = _run_manifest(2, tmpdir, "a.md")
            manifest_path = os.path.join(tmpdir, data["manifest_path"])
            with open(manifest_path, "r") as f:
                content = f.read()
            self.assertIn("Step 2 Manifest", content)
            self.assertIn("Sub-outputs", content)
            self.assertIn("Summary", content)

    def test_manifest_lists_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            _create_file(tmpdir, "b.md", "content " * 50)
            code, data = _run_manifest(2, tmpdir, "a.md,b.md")
            manifest_path = os.path.join(tmpdir, data["manifest_path"])
            with open(manifest_path, "r") as f:
                content = f.read()
            self.assertIn("a.md", content)
            self.assertIn("b.md", content)


class TestFileVerification(unittest.TestCase):
    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run_manifest(2, tmpdir, "nonexistent.md")
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])
            self.assertTrue(any("not found" in e.lower() for e in data.get("errors", [])))

    def test_small_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "tiny.md", "hi")
            code, data = _run_manifest(2, tmpdir, "tiny.md")
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])

    def test_empty_files_list_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run_manifest(2, tmpdir, "")
            self.assertEqual(code, 1)


class TestOutputStructure(unittest.TestCase):
    def test_json_has_required_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            code, data = _run_manifest(2, tmpdir, "a.md")
            self.assertIn("manifest_path", data)
            self.assertIn("valid", data)
            self.assertIn("files_verified", data)
            self.assertIn("total_bytes", data)

    def test_files_verified_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            _create_file(tmpdir, "b.md", "content " * 60)
            _create_file(tmpdir, "c.md", "content " * 70)
            code, data = _run_manifest(9, tmpdir, "a.md,b.md,c.md")
            self.assertEqual(data["files_verified"], 3)
            self.assertGreater(data["total_bytes"], 0)


class TestInvalidStep(unittest.TestCase):
    def test_step_99_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_file(tmpdir, "a.md", "content " * 50)
            code, data = _run_manifest(99, tmpdir, "a.md")
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])


if __name__ == "__main__":
    unittest.main()
