#!/usr/bin/env python3
"""
TDD Tests for bilingual_validator.py

Tests EN+KO pair validation:
  - Both files present and valid → success
  - Missing EN file → failure
  - Missing KO file → failure
  - File too small → failure
  - No SOT entries → failure

P1 Compliance: Tests use mock SOT in temp directory.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BILINGUAL_VALIDATOR = os.path.join(SCRIPT_DIR, "bilingual_validator.py")
SOT_MANAGER = os.path.join(SCRIPT_DIR, "sot_manager.py")


def _run_validator(step, project_dir):
    """Run bilingual_validator.py. Returns (exit_code, parsed_json)."""
    cmd = [
        sys.executable,
        BILINGUAL_VALIDATOR,
        "--step",
        str(step),
        "--project-dir",
        project_dir,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, data


def _init_sot(project_dir):
    cmd = [sys.executable, SOT_MANAGER, "--project-dir", project_dir, "--init"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _register_step(project_dir, step, output):
    cmd = [
        sys.executable,
        SOT_MANAGER,
        "--project-dir",
        project_dir,
        "--update-step",
        str(step),
        "--output",
        output,
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _register_translation(project_dir, step, ko_path):
    cmd = [
        sys.executable,
        SOT_MANAGER,
        "--project-dir",
        project_dir,
        "--add-translation",
        str(step),
        "--ko-path",
        ko_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _create_file(project_dir, rel_path, content="x" * 200):
    abs_path = os.path.join(project_dir, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)


class TestBothPresent(unittest.TestCase):
    def test_valid_pair(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            en_path = "prompt/research/step1.md"
            ko_path = "prompt/research/step1.ko.md"
            _create_file(tmpdir, en_path, "English content " * 20)
            _create_file(tmpdir, ko_path, "한국어 콘텐츠 " * 20)
            _register_step(tmpdir, 1, en_path)
            _register_translation(tmpdir, 1, ko_path)

            code, data = _run_validator(1, tmpdir)
            self.assertEqual(code, 0)
            self.assertTrue(data["valid"])
            self.assertEqual(data["en_path"], en_path)
            self.assertEqual(data["ko_path"], ko_path)
            self.assertGreater(data["en_size"], 0)
            self.assertGreater(data["ko_size"], 0)


class TestMissingFiles(unittest.TestCase):
    def test_no_sot_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_validator(1, tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])

    def test_en_registered_but_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _register_step(tmpdir, 1, "nonexistent.md")
            code, data = _run_validator(1, tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])

    def test_en_present_ko_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            en_path = "step1.md"
            _create_file(tmpdir, en_path, "content " * 50)
            _register_step(tmpdir, 1, en_path)
            code, data = _run_validator(1, tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])


class TestFileSizeValidation(unittest.TestCase):
    def test_en_too_small(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            en_path = "step1.md"
            ko_path = "step1.ko.md"
            _create_file(tmpdir, en_path, "tiny")
            _create_file(tmpdir, ko_path, "한국어 " * 50)
            _register_step(tmpdir, 1, en_path)
            _register_translation(tmpdir, 1, ko_path)
            code, data = _run_validator(1, tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["valid"])


class TestOutputStructure(unittest.TestCase):
    def test_json_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_validator(1, tmpdir)
            self.assertIn("step", data)
            self.assertIn("valid", data)
            self.assertIn("en_path", data)
            self.assertIn("ko_path", data)
            self.assertIn("en_size", data)
            self.assertIn("ko_size", data)


if __name__ == "__main__":
    unittest.main()
