#!/usr/bin/env python3
"""
TDD Tests for sot_manager.py

Tests the ONLY authorized SOT write path. Covers:
  - --init: creates state.yaml with correct schema
  - --update-step: atomically writes output + current_step
  - --set-status: validates against VALID_STATUSES
  - --add-translation: records step-N-ko entry
  - --set-team / --add-team-result / --finalize-team: team lifecycle
  - --update-pacs: pACS score recording
  - Error handling: missing SOT, invalid args, duplicate init

P1 Compliance: Tests run in isolated tmp directory — no real SOT touched.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOT_MANAGER = os.path.join(SCRIPT_DIR, "sot_manager.py")


def _run(args, project_dir):
    """Run sot_manager.py with given args. Returns (exit_code, parsed_json)."""
    cmd = [sys.executable, SOT_MANAGER, "--project-dir", project_dir] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, data


def _read_sot(project_dir):
    """Read and parse the SOT file."""
    import yaml

    sot_path = os.path.join(project_dir, ".claude", "state.yaml")
    with open(sot_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestInit(unittest.TestCase):
    """Tests for --init command."""

    def test_init_creates_sot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run(["--init"], tmpdir)
            self.assertEqual(code, 0)
            self.assertTrue(data["success"])
            sot_path = os.path.join(tmpdir, ".claude", "state.yaml")
            self.assertTrue(os.path.exists(sot_path))

    def test_init_correct_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            sot = _read_sot(tmpdir)
            wf = sot["workflow"]
            self.assertEqual(wf["current_step"], 0)
            self.assertEqual(wf["status"], "running")
            self.assertEqual(wf["total_steps"], 12)
            self.assertFalse(wf["autopilot"]["enabled"])
            self.assertIsInstance(wf["outputs"], dict)
            self.assertEqual(len(wf["outputs"]), 0)

    def test_init_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(["--init"], tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["success"])
            self.assertTrue(any("already exists" in w for w in data["warnings"]))


class TestUpdateStep(unittest.TestCase):
    """Tests for --update-step command."""

    def test_update_step_records_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(
                ["--update-step", "1", "--output", "prompt/research/step1.md"], tmpdir
            )
            self.assertEqual(code, 0)
            self.assertTrue(data["success"])
            sot = _read_sot(tmpdir)
            self.assertEqual(
                sot["workflow"]["outputs"]["step-1"],
                "prompt/research/step1.md",
            )

    def test_update_step_advances_current_step(self):
        """S4 atomicity: output + current_step in same write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            _run(["--update-step", "1", "--output", "out1.md"], tmpdir)
            sot = _read_sot(tmpdir)
            self.assertEqual(sot["workflow"]["current_step"], 1)

    def test_update_step_requires_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(["--update-step", "1"], tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["success"])

    def test_update_multiple_steps(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            _run(["--update-step", "1", "--output", "out1.md"], tmpdir)
            _run(["--update-step", "2", "--output", "out2.md"], tmpdir)
            _run(["--update-step", "3", "--output", "out3.md"], tmpdir)
            sot = _read_sot(tmpdir)
            self.assertEqual(sot["workflow"]["current_step"], 3)
            self.assertEqual(len(sot["workflow"]["outputs"]), 3)


class TestSetStatus(unittest.TestCase):
    """Tests for --set-status command."""

    def test_set_valid_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            for status in ["running", "completed", "error", "paused"]:
                code, data = _run(["--set-status", status], tmpdir)
                self.assertEqual(code, 0, f"Failed for status: {status}")

    def test_set_invalid_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(["--set-status", "in_progress"], tmpdir)
            self.assertEqual(code, 1)
            self.assertFalse(data["success"])


class TestAddTranslation(unittest.TestCase):
    """Tests for --add-translation command."""

    def test_add_translation_records_ko(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            _run(["--update-step", "1", "--output", "out1.md"], tmpdir)
            code, data = _run(
                ["--add-translation", "1", "--ko-path", "out1.ko.md"], tmpdir
            )
            self.assertEqual(code, 0)
            sot = _read_sot(tmpdir)
            self.assertEqual(sot["workflow"]["outputs"]["step-1-ko"], "out1.ko.md")


class TestTeamLifecycle(unittest.TestCase):
    """Tests for team commands: --set-team, --add-team-result, --finalize-team."""

    def test_team_full_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)

            # Set team
            code, data = _run(
                ["--set-team", "prd-analysis-team", "--team-status", "partial"],
                tmpdir,
            )
            self.assertEqual(code, 0)
            sot = _read_sot(tmpdir)
            self.assertEqual(
                sot["workflow"]["active_team"]["name"], "prd-analysis-team"
            )
            self.assertEqual(sot["workflow"]["active_team"]["status"], "partial")

            # Add team result
            code, data = _run(
                [
                    "--add-team-result",
                    "task-1",
                    "--output",
                    "prompt/research/analysis1.md",
                ],
                tmpdir,
            )
            self.assertEqual(code, 0)
            sot = _read_sot(tmpdir)
            self.assertIn("task-1", sot["workflow"]["active_team"]["tasks_completed"])

            # Finalize team
            code, data = _run(["--finalize-team"], tmpdir)
            self.assertEqual(code, 0)
            sot = _read_sot(tmpdir)
            self.assertNotIn("active_team", sot["workflow"])
            self.assertEqual(len(sot["workflow"]["completed_teams"]), 1)

    def test_set_team_invalid_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(
                ["--set-team", "test-team", "--team-status", "invalid"], tmpdir
            )
            self.assertEqual(code, 1)

    def test_finalize_without_active_team(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(["--finalize-team"], tmpdir)
            self.assertEqual(code, 1)


class TestUpdatePacs(unittest.TestCase):
    """Tests for --update-pacs command."""

    def test_update_pacs_records_score(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(
                ["--update-pacs", "1", "--pacs-score", "85", "--weak-dim", "F"],
                tmpdir,
            )
            self.assertEqual(code, 0)
            sot = _read_sot(tmpdir)
            self.assertEqual(sot["workflow"]["pacs"]["current_step_score"], 85)
            self.assertEqual(sot["workflow"]["pacs"]["weak_dimension"], "F")
            self.assertEqual(sot["workflow"]["pacs"]["history"]["step-1"]["score"], 85)

    def test_update_pacs_out_of_range(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(
                ["--update-pacs", "1", "--pacs-score", "101"], tmpdir
            )
            self.assertEqual(code, 1)

    def test_update_pacs_invalid_weak_dim(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(
                ["--update-pacs", "1", "--pacs-score", "70", "--weak-dim", "X"],
                tmpdir,
            )
            self.assertEqual(code, 1)

    def test_update_pacs_requires_score(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["--init"], tmpdir)
            code, data = _run(["--update-pacs", "1"], tmpdir)
            self.assertEqual(code, 1)


class TestNoSotFile(unittest.TestCase):
    """Tests for operations without SOT file."""

    def test_update_step_no_sot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run(
                ["--update-step", "1", "--output", "out.md"], tmpdir
            )
            self.assertEqual(code, 2)

    def test_set_status_no_sot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, data = _run(["--set-status", "running"], tmpdir)
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
