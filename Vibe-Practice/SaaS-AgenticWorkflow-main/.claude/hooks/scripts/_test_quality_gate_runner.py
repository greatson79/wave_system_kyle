#!/usr/bin/env python3
"""
TDD Tests for quality_gate_runner.py

Tests the L0→L1.5→L2→Translation gate sequence:
  - L0: file existence and minimum size
  - Skip flags work correctly
  - Invalid step number handling
  - Gate sequence respects L0 failure (fatal)
  - JSON output structure

P1 Compliance: Tests use mock SOT + mock files in temp directory.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUALITY_GATE_RUNNER = os.path.join(SCRIPT_DIR, "quality_gate_runner.py")
SOT_MANAGER = os.path.join(SCRIPT_DIR, "sot_manager.py")


def _run_gates(step, project_dir, output_path, skip_review=False, skip_translation=False):
    """Run quality_gate_runner.py. Returns (exit_code, parsed_json)."""
    cmd = [
        sys.executable,
        QUALITY_GATE_RUNNER,
        "--step",
        str(step),
        "--project-dir",
        project_dir,
        "--output-path",
        output_path,
    ]
    if skip_review:
        cmd.append("--skip-review")
    if skip_translation:
        cmd.append("--skip-translation")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, data


def _init_sot(project_dir):
    cmd = [sys.executable, SOT_MANAGER, "--project-dir", project_dir, "--init"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _register_step(project_dir, step, output_path):
    cmd = [
        sys.executable,
        SOT_MANAGER,
        "--project-dir",
        project_dir,
        "--update-step",
        str(step),
        "--output",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _create_output_file(project_dir, rel_path, content="x" * 200):
    """Create a mock output file."""
    abs_path = os.path.join(project_dir, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)


class TestInvalidStep(unittest.TestCase):
    def test_step_99_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_gates(99, tmpdir, "nonexistent.md")
            self.assertEqual(code, 1)
            self.assertFalse(data["all_passed"])
            self.assertIn("error", data)


class TestL0Gate(unittest.TestCase):
    def test_l0_fails_nonexistent_file(self):
        """L0 fails when output file doesn't exist — no SOT dependency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_gates(
                1, tmpdir, "nonexistent.md",
                skip_review=True, skip_translation=True,
            )
            self.assertEqual(code, 1)
            self.assertFalse(data["all_passed"])
            self.assertFalse(data["gates"]["L0"]["passed"])

    def test_l0_fails_file_too_small(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "tiny")
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            self.assertEqual(code, 1)
            self.assertFalse(data["gates"]["L0"]["passed"])

    def test_l0_passes_valid_file_without_sot_registration(self):
        """BUG-1 fix: L0 passes with valid file even if NOT registered in SOT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "# Step 1\n" + "content " * 50)
            # NOTE: NOT calling _register_step — this is the BUG-1 fix test
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            self.assertTrue(data["gates"]["L0"]["passed"])

    def test_l0_passes_valid_file_with_sot_registration(self):
        """L0 passes with valid file when also registered in SOT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "# Step 1\n" + "content " * 50)
            _register_step(tmpdir, 1, output_path)
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            self.assertTrue(data["gates"]["L0"]["passed"])

    def test_l0_failure_stops_subsequent_gates(self):
        """L0 failure is fatal — no L1.5, L2, or translation should run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_gates(1, tmpdir, "nonexistent.md")
            gates = data.get("gates", {})
            self.assertIn("L0", gates)
            self.assertNotIn("L1.5", gates)


class TestSkipFlags(unittest.TestCase):
    def test_skip_review(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "content " * 100)
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            if "L2" in data.get("gates", {}):
                self.assertTrue(data["gates"]["L2"].get("skipped", False))

    def test_skip_translation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "content " * 100)
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            if "translation" in data.get("gates", {}):
                self.assertTrue(data["gates"]["translation"].get("skipped", False))


class TestOutputStructure(unittest.TestCase):
    def test_output_has_required_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            output_path = "prompt/research/step1.md"
            _create_output_file(tmpdir, output_path, "content " * 100)
            code, data = _run_gates(
                1, tmpdir, output_path,
                skip_review=True, skip_translation=True,
            )
            self.assertIn("step", data)
            self.assertIn("all_passed", data)
            self.assertIn("gates", data)
            self.assertEqual(data["step"], 1)


if __name__ == "__main__":
    unittest.main()
