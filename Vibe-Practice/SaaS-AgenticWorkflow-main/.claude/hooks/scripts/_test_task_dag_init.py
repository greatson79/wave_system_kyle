#!/usr/bin/env python3
"""
TDD Tests for task_dag_init.py

Tests DAG JSON output:
  - All 12 steps present with correct fields
  - Dependencies are valid step references
  - Team definitions match DAG team fields
  - Translation steps list is correct
  - Output is valid JSON

P1 Compliance: No I/O beyond subprocess — pure data validation.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DAG_INIT = os.path.join(SCRIPT_DIR, "task_dag_init.py")


def _run_dag_init(project_dir="."):
    """Run task_dag_init.py. Returns (exit_code, parsed_json)."""
    cmd = [sys.executable, TASK_DAG_INIT, "--project-dir", project_dir]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = None
    return result.returncode, data


class TestDagOutput(unittest.TestCase):
    def setUp(self):
        self.code, self.data = _run_dag_init()

    def test_exit_code_zero(self):
        self.assertEqual(self.code, 0)

    def test_valid_json(self):
        self.assertIsNotNone(self.data)

    def test_has_required_keys(self):
        self.assertIn("steps", self.data)
        self.assertIn("teams", self.data)
        self.assertIn("total_steps", self.data)
        self.assertIn("translation_steps", self.data)

    def test_twelve_steps(self):
        self.assertEqual(len(self.data["steps"]), 12)
        self.assertEqual(self.data["total_steps"], 12)

    def test_step_fields(self):
        required_fields = {
            "step_number",
            "name",
            "deps",
            "type",
            "team",
            "human",
            "pre_script",
            "review",
            "translate",
            "output",
            "agent",
        }
        for step in self.data["steps"]:
            for field in required_fields:
                self.assertIn(
                    field, step, f"Step {step.get('step_number', '?')} missing {field}"
                )

    def test_step_numbers_sequential(self):
        step_nums = [s["step_number"] for s in self.data["steps"]]
        self.assertEqual(step_nums, list(range(1, 13)))

    def test_deps_reference_valid_steps(self):
        valid_steps = set(range(1, 13))
        for step in self.data["steps"]:
            for dep in step["deps"]:
                self.assertIn(
                    dep,
                    valid_steps,
                    f"Step {step['step_number']} has invalid dep {dep}",
                )

    def test_deps_no_self_reference(self):
        for step in self.data["steps"]:
            self.assertNotIn(
                step["step_number"],
                step["deps"],
                f"Step {step['step_number']} depends on itself",
            )

    def test_deps_no_forward_reference(self):
        """Dependencies should only reference earlier steps (no cycles)."""
        for step in self.data["steps"]:
            for dep in step["deps"]:
                self.assertLess(
                    dep,
                    step["step_number"],
                    f"Step {step['step_number']} has forward dep {dep}",
                )

    def test_step_types_valid(self):
        valid_types = {"sub-agent", "agent-team", "human"}
        for step in self.data["steps"]:
            self.assertIn(
                step["type"],
                valid_types,
                f"Step {step['step_number']} has invalid type {step['type']}",
            )

    def test_human_steps(self):
        human_steps = [s for s in self.data["steps"] if s["human"]]
        human_nums = [s["step_number"] for s in human_steps]
        self.assertIn(4, human_nums)
        self.assertIn(8, human_nums)
        self.assertIn(12, human_nums)

    def test_team_steps_have_team_name(self):
        team_steps = [s for s in self.data["steps"] if s["type"] == "agent-team"]
        for step in team_steps:
            self.assertIsNotNone(
                step["team"],
                f"Team step {step['step_number']} has no team name",
            )

    def test_teams_defined(self):
        self.assertIn("prd-analysis-team", self.data["teams"])
        self.assertIn("prd-generation-team", self.data["teams"])

    def test_team_members_have_fields(self):
        for team_name, team_info in self.data["teams"].items():
            self.assertIn("members", team_info)
            for member in team_info["members"]:
                self.assertIn("agent", member)
                self.assertIn("task", member)
                self.assertIn("output", member)

    def test_prd_analysis_team_has_3_members(self):
        team = self.data["teams"]["prd-analysis-team"]
        self.assertEqual(len(team["members"]), 3)

    def test_prd_generation_team_has_4_members(self):
        team = self.data["teams"]["prd-generation-team"]
        self.assertEqual(len(team["members"]), 4)

    def test_translation_steps(self):
        expected = [1, 2, 3, 5, 6, 7, 9, 11, 12]
        self.assertEqual(self.data["translation_steps"], expected)

    def test_every_step_has_output_path(self):
        """BUG-3 fix: every step must have a deterministic output path."""
        for step in self.data["steps"]:
            self.assertIsNotNone(
                step.get("output"),
                f"Step {step['step_number']} missing output path",
            )
            self.assertTrue(
                len(step["output"]) > 0,
                f"Step {step['step_number']} has empty output path",
            )

    def test_sub_agent_steps_have_agent_name(self):
        """Sub-agent steps must specify which agent to spawn."""
        for step in self.data["steps"]:
            if step["type"] == "sub-agent":
                self.assertIsNotNone(
                    step.get("agent"),
                    f"Sub-agent step {step['step_number']} missing agent name",
                )


if __name__ == "__main__":
    unittest.main()
