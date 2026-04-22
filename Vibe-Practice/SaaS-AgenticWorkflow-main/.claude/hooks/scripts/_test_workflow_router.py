#!/usr/bin/env python3
"""
TDD Tests for workflow_router.py

Tests DAG-based step routing:
  - Step 0 (not started) → [1]
  - Step 1 complete → [2]
  - Step 2 complete (with 1 already) → [3]
  - Step 3 complete → [4] (human checkpoint)
  - Step 4 (human) complete → [5, 6] (parallel)
  - Steps 5+6 complete → [7]
  - Step 7 complete → [8] (human)
  - Step 12 → workflow complete
  - Invalid step numbers

P1 Compliance: Tests run in isolated tmp directory with mock SOT.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_ROUTER = os.path.join(SCRIPT_DIR, "workflow_router.py")
SOT_MANAGER = os.path.join(SCRIPT_DIR, "sot_manager.py")


def _run_router(current_step, project_dir):
    """Run workflow_router.py. Returns (exit_code, parsed_json)."""
    cmd = [
        sys.executable,
        WORKFLOW_ROUTER,
        "--current-step",
        str(current_step),
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
    """Initialize SOT file."""
    cmd = [sys.executable, SOT_MANAGER, "--project-dir", project_dir, "--init"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _update_step(project_dir, step, output="dummy.md"):
    """Record a step output in SOT."""
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


class TestWorkflowStart(unittest.TestCase):
    def test_step_0_returns_step_1(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_router(0, tmpdir)
            self.assertEqual(code, 0)
            self.assertEqual(data["next_steps"], [1])
            self.assertFalse(data["human_checkpoint"])


class TestLinearProgression(unittest.TestCase):
    def test_step_1_to_step_2(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _update_step(tmpdir, 1)
            code, data = _run_router(1, tmpdir)
            self.assertEqual(code, 0)
            self.assertIn(2, data["next_steps"])

    def test_step_2_to_step_3(self):
        """Step 3 requires both 1 AND 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _update_step(tmpdir, 1)
            _update_step(tmpdir, 2)
            code, data = _run_router(2, tmpdir)
            self.assertEqual(code, 0)
            self.assertIn(3, data["next_steps"])

    def test_step_3_to_step_4_human(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _update_step(tmpdir, 1)
            _update_step(tmpdir, 2)
            _update_step(tmpdir, 3)
            code, data = _run_router(3, tmpdir)
            self.assertEqual(code, 0)
            self.assertIn(4, data["next_steps"])
            self.assertTrue(data["human_checkpoint"])


class TestParallelSteps(unittest.TestCase):
    def test_step_4_to_steps_5_and_6(self):
        """Step 4 (human) completed → steps 5 AND 6 can run in parallel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _update_step(tmpdir, 1)
            _update_step(tmpdir, 2)
            _update_step(tmpdir, 3)
            _update_step(tmpdir, 4)  # human step
            code, data = _run_router(4, tmpdir)
            self.assertEqual(code, 0)
            self.assertIn(5, data["next_steps"])
            self.assertIn(6, data["next_steps"])
            self.assertEqual(len(data["next_steps"]), 2)

    def test_step_7_requires_both_5_and_6(self):
        """Step 7 deps: [5, 6]. Only 5 done → step 7 NOT available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            _update_step(tmpdir, 1)
            _update_step(tmpdir, 2)
            _update_step(tmpdir, 3)
            _update_step(tmpdir, 4)
            _update_step(tmpdir, 5)
            code, data = _run_router(5, tmpdir)
            self.assertEqual(code, 0)
            # Step 7 should NOT be in next_steps (step 6 not done)
            # But step 6 might be there if it hasn't run yet
            self.assertNotIn(7, data["next_steps"])


class TestWorkflowComplete(unittest.TestCase):
    def test_step_12_ends_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_router(12, tmpdir)
            self.assertEqual(code, 0)
            self.assertEqual(data["next_steps"], [])
            self.assertIn("complete", data["reason"].lower())


class TestEdgeCases(unittest.TestCase):
    def test_negative_step(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_router(-1, tmpdir)
            self.assertEqual(code, 0)
            self.assertEqual(data["next_steps"], [])

    def test_step_beyond_total(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _init_sot(tmpdir)
            code, data = _run_router(13, tmpdir)
            self.assertEqual(code, 0)
            self.assertEqual(data["next_steps"], [])


if __name__ == "__main__":
    unittest.main()
