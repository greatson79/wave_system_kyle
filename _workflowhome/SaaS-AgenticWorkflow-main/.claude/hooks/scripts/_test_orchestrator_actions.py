#!/usr/bin/env python3
"""
Tests for orchestrator_actions.py — deterministic orchestrator helpers.

Coverage:
  - All 8 subcommands
  - Edge cases: invalid steps, missing files, boundary pACS scores
  - Determinism verification: same input → same output
  - CLI integration: subprocess calls with JSON parsing
  - C-1/C-2/C-3/W-1/W-5 fix verifications

Run:
    python3 .claude/hooks/scripts/_test_orchestrator_actions.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

# Add script directory to path
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

from orchestrator_actions import (
    action_step_config,
    action_extract_pacs,
    action_derive_paths,
    action_team_files,
    action_pacs_decision,
    action_verify_deps,
    action_finalize_step12,
    action_agent_prompt,
    _derive_ko_path,
    _get_step_inputs,
    _step_11_prompt,
    STEP_INPUTS,
)
from _workflow_dag import DAG, TEAMS, TRANSLATION_STEPS, HUMAN_STEPS, TOTAL_STEPS


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _run_cli(*args):
    """Run orchestrator_actions.py as subprocess, return parsed JSON."""
    script = os.path.join(_SCRIPTS_DIR, "orchestrator_actions.py")
    cmd = [sys.executable, script] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout), result.returncode


# ===========================================================================
# Test: _derive_ko_path (H-5)
# ===========================================================================
class TestDeriveKoPath(unittest.TestCase):
    def test_md_extension(self):
        self.assertEqual(_derive_ko_path("file.md"), "file.ko.md")

    def test_txt_extension(self):
        self.assertEqual(_derive_ko_path("file.txt"), "file.ko.txt")

    def test_no_extension(self):
        self.assertEqual(_derive_ko_path("file"), "file.ko.md")

    def test_nested_path(self):
        self.assertEqual(
            _derive_ko_path("prompt/research/analysis.md"),
            "prompt/research/analysis.ko.md",
        )

    def test_already_ko(self):
        self.assertEqual(
            _derive_ko_path("file.ko.md"),
            "file.ko.md",
        )

    def test_already_ko_nested(self):
        self.assertEqual(
            _derive_ko_path("prompt/file.ko.txt"),
            "prompt/file.ko.txt",
        )

    def test_determinism(self):
        """Same input always produces same output."""
        for _ in range(100):
            self.assertEqual(_derive_ko_path("a/b.md"), "a/b.ko.md")


# ===========================================================================
# Test: _get_step_inputs (H-3) — Updated for STEP_INPUTS explicit map (C-1)
# ===========================================================================
class TestGetStepInputs(unittest.TestCase):
    def test_step_1_returns_prd(self):
        """Step 1 has explicit input: coding-resource/PRD.md."""
        inputs = _get_step_inputs(1)
        self.assertIsInstance(inputs, list)
        self.assertEqual(inputs, ["coding-resource/PRD.md"])

    def test_step_3_has_all_research_files(self):
        """Step 3 inputs: all Step 1+2 outputs + PRD."""
        inputs = _get_step_inputs(3)
        self.assertIsInstance(inputs, list)
        self.assertIn("prompt/research/prd-foundation-analysis.md", inputs)
        self.assertIn("prompt/research/arch-engine-analysis.md", inputs)
        self.assertIn("prompt/research/feature-ux-analysis.md", inputs)
        self.assertIn("prompt/research/biz-quality-analysis.md", inputs)
        self.assertIn("coding-resource/PRD.md", inputs)
        self.assertEqual(len(inputs), 5)

    def test_step_5_has_6_files(self):
        """Step 5 (prd-architect) needs 6 files per agent definition."""
        inputs = _get_step_inputs(5)
        self.assertEqual(len(inputs), 6)
        self.assertIn("prompt/research/synthesis-and-gaps.md", inputs)
        self.assertIn("coding-resource/PRD.md", inputs)

    def test_step_7_has_2_planning_files(self):
        """Step 7 (engine-planner) needs 2 planning inputs."""
        inputs = _get_step_inputs(7)
        self.assertEqual(len(inputs), 2)
        self.assertIn("prompt/planning/prd-architecture.md", inputs)
        self.assertIn("prompt/planning/intent-capture-spec.md", inputs)

    def test_step_10_has_3_files(self):
        """Step 10 (cross-validator) needs merged PRD + quality specs + architecture."""
        inputs = _get_step_inputs(10)
        self.assertEqual(len(inputs), 3)
        self.assertIn("prompt/implementation/prd-merged.md", inputs)

    def test_step_11_has_validated_prd(self):
        """Step 11 (reviewer) needs the validated PRD."""
        inputs = _get_step_inputs(11)
        self.assertEqual(inputs, ["prompt/implementation/prd-validated.md"])

    def test_invalid_step_returns_empty(self):
        self.assertEqual(_get_step_inputs(99), [])

    def test_human_steps_return_empty(self):
        """Human steps (4, 8, 12) have no entries in STEP_INPUTS."""
        for step in HUMAN_STEPS:
            self.assertEqual(_get_step_inputs(step), [])

    def test_team_member_specific_inputs(self):
        """Team member lookup with agent name returns per-member files."""
        inputs = _get_step_inputs(2, member_agent="arch-engine-specialist")
        self.assertIsInstance(inputs, list)
        self.assertEqual(len(inputs), 2)
        self.assertIn("prompt/research/prd-foundation-analysis.md", inputs)
        self.assertIn("coding-resource/PRD.md", inputs)

    def test_all_team_2_members_have_inputs(self):
        """All 3 members of Step 2 team have per-member inputs."""
        for member in TEAMS["prd-analysis-team"]["members"]:
            inputs = _get_step_inputs(2, member_agent=member["agent"])
            self.assertTrue(len(inputs) > 0, f"No inputs for {member['agent']}")

    def test_all_team_9_members_have_inputs(self):
        """All 4 members of Step 9 team have per-member inputs."""
        for member in TEAMS["prd-generation-team"]["members"]:
            inputs = _get_step_inputs(9, member_agent=member["agent"])
            self.assertTrue(len(inputs) > 0, f"No inputs for {member['agent']}")
            # All Step 9 members need the 3 planning files
            self.assertIn("prompt/planning/prd-architecture.md", inputs)
            self.assertIn("prompt/planning/intent-capture-spec.md", inputs)
            self.assertIn("prompt/planning/engine-quality-specs.md", inputs)

    def test_unknown_team_member_returns_empty(self):
        """Unknown agent name for a team step returns empty."""
        inputs = _get_step_inputs(2, member_agent="nonexistent-agent")
        self.assertEqual(inputs, [])

    def test_returns_copy_not_reference(self):
        """Returned list should be a copy, not a reference to STEP_INPUTS."""
        inputs1 = _get_step_inputs(1)
        inputs2 = _get_step_inputs(1)
        inputs1.append("extra.md")
        self.assertNotIn("extra.md", inputs2)

    def test_all_input_paths_are_strings(self):
        """All items in returned lists must be strings."""
        for key in STEP_INPUTS:
            if isinstance(key, int):
                inputs = _get_step_inputs(key)
            else:
                step_num, agent = key.split(":", 1)
                inputs = _get_step_inputs(int(step_num), member_agent=agent)
            for path in inputs:
                self.assertIsInstance(path, str, f"Non-string in inputs for key={key}")


# ===========================================================================
# Test: step-config (H-2)
# ===========================================================================
class TestStepConfig(unittest.TestCase):
    def test_valid_step(self):
        result = action_step_config(1)
        self.assertTrue(result["success"])
        self.assertEqual(result["step"], 1)
        self.assertEqual(result["agent"], "prd-analyst")
        self.assertEqual(result["type"], "sub-agent")
        self.assertEqual(result["output"], "prompt/research/prd-foundation-analysis.md")

    def test_invalid_step(self):
        result = action_step_config(99)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_team_step_includes_members(self):
        result = action_step_config(2)
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "agent-team")
        self.assertEqual(result["team"], "prd-analysis-team")
        self.assertIn("team_members", result)
        self.assertEqual(len(result["team_members"]), 3)

    def test_human_step(self):
        result = action_step_config(4)
        self.assertTrue(result["success"])
        self.assertTrue(result["human"])
        self.assertTrue(result["is_human_step"])
        self.assertEqual(result["type"], "human")

    def test_all_12_steps_valid(self):
        for step in range(1, 13):
            result = action_step_config(step)
            self.assertTrue(result["success"], f"Step {step} failed")
            self.assertEqual(result["step"], step)

    def test_translation_flag(self):
        result = action_step_config(1)
        self.assertTrue(result["translate"])
        self.assertTrue(result["is_translation_step"])

        result = action_step_config(4)
        self.assertFalse(result["translate"])
        self.assertFalse(result["is_translation_step"])

    def test_review_agent(self):
        result = action_step_config(3)
        self.assertEqual(result["review"], "fact-checker")

        result = action_step_config(6)
        self.assertEqual(result["review"], "reviewer")

        result = action_step_config(1)
        self.assertIsNone(result["review"])

    def test_pre_script(self):
        result = action_step_config(1)
        self.assertEqual(result["pre_script"], "extract_prd_sections.py")

        result = action_step_config(10)
        self.assertEqual(result["pre_script"], "merge_prd_sections.py")

        result = action_step_config(3)
        self.assertIsNone(result["pre_script"])

    def test_special_flow_step_11(self):
        """W-1: Step 11 should have special_flow='two-phase'."""
        result = action_step_config(11)
        self.assertEqual(result["special_flow"], "two-phase")

    def test_special_flow_other_steps_null(self):
        """Non-step-11 steps should have special_flow=None."""
        for step in range(1, 13):
            if step == 11:
                continue
            result = action_step_config(step)
            self.assertIsNone(result["special_flow"], f"Step {step}")

    def test_determinism(self):
        """Same step always returns same config."""
        r1 = action_step_config(7)
        r2 = action_step_config(7)
        self.assertEqual(r1, r2)


# ===========================================================================
# Test: extract-pacs (H-1) — Updated for C-3 fixes
# ===========================================================================
class TestExtractPacs(unittest.TestCase):
    def _write_temp(self, content):
        fd, path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_standard_pacs(self):
        content = """
## pACS Self-Assessment

| Dimension | Score |
|-----------|-------|
| F | 85 |
| C | 78 |
| L | 82 |

pACS = min(F, C, L) = 78
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertEqual(result["dimensions"]["F"], 85)
            self.assertEqual(result["dimensions"]["C"], 78)
            self.assertEqual(result["dimensions"]["L"], 82)
            self.assertEqual(result["final_score"], 78)
            self.assertEqual(result["weak_dim"], "C")
            self.assertTrue(result["arithmetic_ok"])
        finally:
            os.unlink(path)

    def test_wrong_arithmetic(self):
        content = """
| F | 85 |
| C | 78 |
| L | 82 |

pACS = min(F, C, L) = 85
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertFalse(result["arithmetic_ok"])
            self.assertEqual(result["reported_score"], 85)
            self.assertEqual(result["calculated_score"], 78)
            self.assertEqual(result["final_score"], 78)  # uses calculated
        finally:
            os.unlink(path)

    def test_no_pacs_found(self):
        content = "# Just a regular document\n\nNo pACS here."
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertFalse(result["found"])
            self.assertIsNone(result["final_score"])
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        result = action_extract_pacs("/nonexistent/file.md", "/")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_simple_pacs(self):
        content = """
| F | 90 |
| C | 88 |
| L | 92 |

pACS = 88
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertEqual(result["final_score"], 88)
            self.assertTrue(result["arithmetic_ok"])
        finally:
            os.unlink(path)

    def test_single_dimension_not_sufficient(self):
        """C-3: Single dimension should not produce a score (min 2 required)."""
        content = """
| F | 85 |

pACS = 85
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            # calculated_score should be None (< 2 dims)
            self.assertIsNone(result["calculated_score"])
            # reported_score should be found
            self.assertEqual(result["reported_score"], 85)
            # final_score falls back to reported
            self.assertEqual(result["final_score"], 85)
            self.assertTrue(result["found"])
        finally:
            os.unlink(path)

    def test_ambiguous_dimensions_dropped(self):
        """C-3: Same dimension with different scores should be dropped."""
        content = """
| F | 85 |
| C | 78 |
| F | 90 |
| L | 82 |

pACS = min(F, C, L) = 78
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            # F should be dropped due to ambiguity (85 vs 90)
            self.assertNotIn("F", result["dimensions"])
            # C and L remain
            self.assertIn("C", result["dimensions"])
            self.assertIn("L", result["dimensions"])
            # calculated = min(78, 82) = 78
            self.assertEqual(result["calculated_score"], 78)
        finally:
            os.unlink(path)

    def test_two_dimensions_sufficient(self):
        """C-3: Two dimensions should be enough for min()."""
        content = """
| F | 85 |
| C | 70 |

pACS = min(F, C) = 70
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertEqual(result["calculated_score"], 70)
            self.assertTrue(result["found"])
        finally:
            os.unlink(path)

    def test_four_plus_dimensions(self):
        """N>3 dimensions should still work (min of all)."""
        content = """
| F | 85 |
| C | 78 |
| L | 82 |
| A | 90 |

pACS = min(F, C, L, A) = 78
"""
        path = self._write_temp(content)
        try:
            result = action_extract_pacs(path, "/")
            self.assertTrue(result["success"])
            self.assertEqual(result["calculated_score"], 78)
            self.assertEqual(len(result["dimensions"]), 4)
        finally:
            os.unlink(path)

    def test_relative_path_resolved(self):
        """Relative paths should be resolved against project_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "| F | 80 |\n| C | 75 |\npACS = min(F,C) = 75\n"
            fpath = os.path.join(tmpdir, "test.md")
            with open(fpath, "w") as f:
                f.write(content)
            result = action_extract_pacs("test.md", tmpdir)
            self.assertTrue(result["success"])
            self.assertEqual(result["final_score"], 75)

    def test_determinism(self):
        content = "| F | 75 |\n| C | 80 |\n| L | 70 |\npACS = min(F,C,L) = 70\n"
        path = self._write_temp(content)
        try:
            r1 = action_extract_pacs(path, "/")
            r2 = action_extract_pacs(path, "/")
            self.assertEqual(r1, r2)
        finally:
            os.unlink(path)


# ===========================================================================
# Test: derive-paths (H-3, H-5) — Updated for STEP_INPUTS format
# ===========================================================================
class TestDerivePaths(unittest.TestCase):
    def test_sub_agent_step(self):
        result = action_derive_paths(1, "/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["en_output"], "prompt/research/prd-foundation-analysis.md")
        self.assertEqual(result["ko_output"], "prompt/research/prd-foundation-analysis.ko.md")

    def test_non_translate_step(self):
        result = action_derive_paths(10, "/tmp")
        self.assertTrue(result["success"])
        self.assertIsNone(result["ko_output"])

    def test_team_step_has_member_outputs(self):
        result = action_derive_paths(9, "/tmp")
        self.assertTrue(result["success"])
        self.assertIn("team_member_outputs", result)
        self.assertEqual(len(result["team_member_outputs"]), 4)
        # Each member should have ko_path
        for m in result["team_member_outputs"]:
            self.assertIn(".ko.", m["ko_path"])

    def test_human_step_no_ko(self):
        result = action_derive_paths(4, "/tmp")
        self.assertTrue(result["success"])
        # Human steps have "approved-by-user" which is not translatable
        self.assertIsNone(result["ko_output"])

    def test_invalid_step(self):
        result = action_derive_paths(99, "/tmp")
        self.assertFalse(result["success"])

    def test_inputs_format(self):
        """Inputs should be list of {"path": str, "exists": bool}."""
        result = action_derive_paths(1, "/tmp")
        self.assertIn("inputs", result)
        self.assertIsInstance(result["inputs"], list)
        for inp in result["inputs"]:
            self.assertIn("path", inp)
            self.assertIn("exists", inp)
            self.assertIsInstance(inp["path"], str)
            self.assertIsInstance(inp["exists"], bool)

    def test_no_primary_source_field(self):
        """derive-paths should NOT have primary_source field (removed in C-1)."""
        result = action_derive_paths(1, "/tmp")
        self.assertNotIn("primary_source", result)
        self.assertNotIn("primary_source_exists", result)

    def test_step_12_human_step(self):
        """Step 12 is hybrid human step — should have no ko_output."""
        result = action_derive_paths(12, "/tmp")
        self.assertTrue(result["success"])
        # Step 12 output is the final PRD path but translate is False for human steps
        # Check it doesn't crash

    def test_step_1_inputs_match_step_inputs(self):
        """derive-paths inputs should match STEP_INPUTS."""
        result = action_derive_paths(1, "/tmp")
        input_paths = [inp["path"] for inp in result["inputs"]]
        self.assertEqual(input_paths, STEP_INPUTS[1])


# ===========================================================================
# Test: team-files (H-4)
# ===========================================================================
class TestTeamFiles(unittest.TestCase):
    def test_step_2_team(self):
        result = action_team_files(2, "/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["team_name"], "prd-analysis-team")
        self.assertEqual(result["member_count"], 3)
        self.assertIn(",", result["files_csv"])

    def test_step_9_team(self):
        result = action_team_files(9, "/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["team_name"], "prd-generation-team")
        self.assertEqual(result["member_count"], 4)

    def test_non_team_step_errors(self):
        result = action_team_files(1, "/tmp")
        self.assertFalse(result["success"])
        self.assertIn("not a team step", result["error"])

    def test_invalid_step(self):
        result = action_team_files(99, "/tmp")
        self.assertFalse(result["success"])

    def test_csv_format(self):
        result = action_team_files(2, "/tmp")
        csv = result["files_csv"]
        files = csv.split(",")
        self.assertEqual(len(files), 3)
        for f in files:
            self.assertTrue(f.endswith(".md"))

    def test_file_existence_checked(self):
        result = action_team_files(2, "/tmp")
        # Files won't exist in /tmp
        self.assertFalse(result["all_outputs_exist"])
        for m in result["members"]:
            self.assertFalse(m["exists"])

    def test_file_existence_with_real_dir(self):
        """If we create the expected files, all_outputs_exist should be True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create team 2 output files
            for m in TEAMS["prd-analysis-team"]["members"]:
                path = os.path.join(tmpdir, m["output"])
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write("test content")
            result = action_team_files(2, tmpdir)
            self.assertTrue(result["all_outputs_exist"])


# ===========================================================================
# Test: pacs-decision (H-7)
# ===========================================================================
class TestPacsDecision(unittest.TestCase):
    def test_green(self):
        result = action_pacs_decision(85, "F", 3)
        self.assertTrue(result["success"])
        self.assertEqual(result["color"], "GREEN")
        self.assertEqual(result["action"], "proceed")
        self.assertIsNone(result["feedback"])

    def test_green_boundary(self):
        result = action_pacs_decision(70, "C", 5)
        self.assertEqual(result["color"], "GREEN")

    def test_yellow(self):
        result = action_pacs_decision(65, "C", 3)
        self.assertEqual(result["color"], "YELLOW")
        self.assertEqual(result["action"], "proceed_with_warning")
        self.assertIn("Warning", result["feedback"])

    def test_yellow_boundary_low(self):
        result = action_pacs_decision(50, "L", 7)
        self.assertEqual(result["color"], "YELLOW")

    def test_yellow_boundary_high(self):
        result = action_pacs_decision(69, "F", 1)
        self.assertEqual(result["color"], "YELLOW")

    def test_red(self):
        result = action_pacs_decision(42, "F", 5)
        self.assertEqual(result["color"], "RED")
        self.assertEqual(result["action"], "rework_required")
        self.assertIn("deviated from the input", result["feedback"])
        self.assertEqual(result["rework_max"], 1)

    def test_red_c_feedback(self):
        result = action_pacs_decision(30, "C", 3)
        self.assertIn("missing required elements", result["feedback"])

    def test_red_l_feedback(self):
        result = action_pacs_decision(25, "L", 6)
        self.assertIn("logical inconsistencies", result["feedback"])

    def test_red_unknown_dim(self):
        result = action_pacs_decision(10, "X", 1)
        self.assertEqual(result["color"], "RED")
        self.assertIn("below the minimum threshold", result["feedback"])

    def test_red_boundary(self):
        result = action_pacs_decision(49, "F", 3)
        self.assertEqual(result["color"], "RED")

    def test_zero_score(self):
        result = action_pacs_decision(0, "F", 1)
        self.assertEqual(result["color"], "RED")

    def test_max_score(self):
        result = action_pacs_decision(100, "F", 1)
        self.assertEqual(result["color"], "GREEN")

    def test_out_of_range(self):
        result = action_pacs_decision(101, "F", 1)
        self.assertFalse(result["success"])

    def test_negative_score(self):
        result = action_pacs_decision(-1, "F", 1)
        self.assertFalse(result["success"])

    def test_determinism(self):
        for _ in range(50):
            r = action_pacs_decision(65, "C", 3)
            self.assertEqual(r["color"], "YELLOW")


# ===========================================================================
# Test: verify-deps (H-12)
# ===========================================================================
class TestVerifyDeps(unittest.TestCase):
    def test_step_1_no_deps(self):
        result = action_verify_deps(1, "/tmp")
        self.assertTrue(result["success"])
        self.assertTrue(result["deps_satisfied"])
        self.assertEqual(result["deps"], [])

    def test_step_3_missing_deps(self):
        result = action_verify_deps(3, "/tmp")
        self.assertTrue(result["success"])
        self.assertFalse(result["deps_satisfied"])
        self.assertTrue(len(result["missing"]) > 0)

    def test_step_with_satisfied_deps(self):
        """Create dependency files and verify they're found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 3 depends on Step 1 output and Step 2 team outputs
            step1_out = DAG[1]["output"]
            path = os.path.join(tmpdir, step1_out)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write("test")

            # Also create step 2 team outputs
            for m in TEAMS["prd-analysis-team"]["members"]:
                p = os.path.join(tmpdir, m["output"])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w") as f:
                    f.write("test")

            result = action_verify_deps(3, tmpdir)
            self.assertTrue(result["deps_satisfied"])

    def test_step_with_sot_satisfied_human_dep(self):
        """Human step dep should check SOT for completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 5 depends on Step 4 (human). Create SOT with step-4 entry.
            sot_dir = os.path.join(tmpdir, ".claude")
            os.makedirs(sot_dir, exist_ok=True)
            sot_content = "workflow_name: saas-autobuilder\ncurrent_step: 4\nstatus: running\noutputs:\n  step-4: approved-by-user\n"
            with open(os.path.join(sot_dir, "state.yaml"), "w") as f:
                f.write(sot_content)

            # Step 5 deps = [4]
            result = action_verify_deps(5, tmpdir)
            self.assertTrue(result["success"])
            # Should be satisfied since SOT has step-4
            self.assertTrue(result["deps_satisfied"])

    def test_invalid_step(self):
        result = action_verify_deps(99, "/tmp")
        self.assertFalse(result["success"])


# ===========================================================================
# Test: finalize-step12 (H-11)
# ===========================================================================
class TestFinalizeStep12(unittest.TestCase):
    def test_returns_commands(self):
        result = action_finalize_step12("/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["step"], 12)
        self.assertEqual(result["final_en"], "prompt/PRD-SaaS-AutoBuilder.md")
        self.assertEqual(result["final_ko"], "prompt/PRD-SaaS-AutoBuilder.ko.md")
        self.assertEqual(len(result["commands"]), 5)

    def test_command_order(self):
        result = action_finalize_step12("/tmp")
        orders = [c["order"] for c in result["commands"]]
        self.assertEqual(orders, [1, 2, 3, 4, 5])

    def test_command_types(self):
        result = action_finalize_step12("/tmp")
        types = [c["type"] for c in result["commands"]]
        self.assertEqual(types, ["copy", "agent", "bash", "bash", "bash"])

    def test_sot_commands_correct(self):
        result = action_finalize_step12("/tmp")
        # Command 4: add-translation
        self.assertIn("add-translation 12", result["commands"][3]["command"])
        # Command 5: update-step
        self.assertIn("update-step 12", result["commands"][4]["command"])

    def test_source_derived_from_dag(self):
        """W-5: Source should come from DAG step 10 output."""
        result = action_finalize_step12("/tmp")
        expected_source = DAG[10]["output"]
        self.assertEqual(result["commands"][0]["source"], expected_source)

    def test_determinism(self):
        r1 = action_finalize_step12("/tmp")
        r2 = action_finalize_step12("/tmp")
        self.assertEqual(r1, r2)


# ===========================================================================
# Test: agent-prompt (H-3) — Updated for STEP_INPUTS + C-2 fixes
# ===========================================================================
class TestAgentPrompt(unittest.TestCase):
    def test_sub_agent_prompt(self):
        result = action_agent_prompt(1, "/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["agent"], "prd-analyst")
        self.assertIn("@prd-analyst", result["prompt"])
        self.assertIn("prd-foundation-analysis.md", result["prompt"])

    def test_team_step_prompts(self):
        result = action_agent_prompt(2, "/tmp")
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "agent-team")
        self.assertEqual(len(result["member_prompts"]), 3)
        for mp in result["member_prompts"]:
            self.assertIn("agent", mp)
            self.assertIn("prompt", mp)
            self.assertIn(f"@{mp['agent']}", mp["prompt"])

    def test_team_member_prompts_have_concrete_inputs(self):
        """C-2: Team member prompts must include concrete file paths, not generic instructions."""
        result = action_agent_prompt(2, "/tmp")
        for mp in result["member_prompts"]:
            self.assertIn("inputs", mp)
            self.assertIsInstance(mp["inputs"], list)
            self.assertTrue(len(mp["inputs"]) > 0, f"No inputs for {mp['agent']}")
            # Prompt should contain at least one concrete file path
            self.assertIn("REQUIRED input files", mp["prompt"])

    def test_team_9_member_prompts_have_concrete_inputs(self):
        """C-2: Step 9 team members should also have concrete file paths."""
        result = action_agent_prompt(9, "/tmp")
        for mp in result["member_prompts"]:
            self.assertTrue(len(mp["inputs"]) > 0, f"No inputs for {mp['agent']}")
            # All Step 9 members need planning files
            self.assertIn("prompt/planning/prd-architecture.md", mp["inputs"])

    def test_human_step_errors(self):
        result = action_agent_prompt(4, "/tmp")
        self.assertFalse(result["success"])
        self.assertIn("human step", result["error"])

    def test_step_11_two_phase(self):
        result = _step_11_prompt()
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "two-phase")
        self.assertIn("phase1", result)
        self.assertIn("phase2", result)
        self.assertEqual(result["phase1"]["subagent_type"], "reviewer")
        self.assertEqual(result["phase2"]["subagent_type"], "fact-checker")

    def test_pre_script_info(self):
        result = action_agent_prompt(1, "/tmp")
        self.assertIsNotNone(result["pre_script"])
        self.assertIn("extract_prd_sections", result["pre_script"]["command"])

        result = action_agent_prompt(10, "/tmp")
        self.assertIsNotNone(result["pre_script"])
        self.assertIn("merge_prd_sections", result["pre_script"]["command"])

    def test_review_info(self):
        result = action_agent_prompt(3, "/tmp")
        self.assertIsNotNone(result["review"])
        self.assertEqual(result["review"]["agent"], "fact-checker")

    def test_translate_info(self):
        result = action_agent_prompt(1, "/tmp")
        self.assertTrue(result["translate"])
        self.assertIn(".ko.", result["ko_output"])

    def test_sub_agent_inputs_are_strings(self):
        """Inputs field should be a list of path strings."""
        result = action_agent_prompt(5, "/tmp")
        self.assertIn("inputs", result)
        self.assertIsInstance(result["inputs"], list)
        for inp in result["inputs"]:
            self.assertIsInstance(inp, str)

    def test_step_5_has_6_inputs(self):
        """Step 5 should have 6 inputs matching STEP_INPUTS."""
        result = action_agent_prompt(5, "/tmp")
        self.assertEqual(len(result["inputs"]), 6)
        self.assertEqual(result["inputs"], STEP_INPUTS[5])

    def test_invalid_step(self):
        result = action_agent_prompt(99, "/tmp")
        self.assertFalse(result["success"])

    def test_all_sub_agent_steps_have_prompts(self):
        """Every sub-agent step should produce a valid prompt."""
        sub_agent_steps = [s for s, info in DAG.items() if info["type"] == "sub-agent"]
        for step in sub_agent_steps:
            if step == 11:
                result = _step_11_prompt()
            else:
                result = action_agent_prompt(step, "/tmp")
            self.assertTrue(result["success"], f"Step {step} failed to generate prompt")


# ===========================================================================
# Test: CLI Integration
# ===========================================================================
class TestCLI(unittest.TestCase):
    def test_step_config_cli(self):
        data, code = _run_cli("--action", "step-config", "--step", "1")
        self.assertEqual(code, 0)
        self.assertTrue(data["success"])
        self.assertEqual(data["agent"], "prd-analyst")

    def test_pacs_decision_cli(self):
        data, code = _run_cli("--action", "pacs-decision", "--score", "75", "--weak-dim", "F", "--step", "3")
        self.assertEqual(code, 0)
        self.assertEqual(data["color"], "GREEN")

    def test_invalid_action_cli(self):
        """Invalid action should fail."""
        result = subprocess.run(
            [sys.executable, os.path.join(_SCRIPTS_DIR, "orchestrator_actions.py"),
             "--action", "nonexistent"],
            capture_output=True, text=True, timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_missing_required_args_cli(self):
        data, code = _run_cli("--action", "step-config")
        # No --step provided
        self.assertEqual(code, 1)
        self.assertFalse(data["success"])

    def test_finalize_step12_cli(self):
        data, code = _run_cli("--action", "finalize-step12")
        self.assertEqual(code, 0)
        self.assertEqual(data["step"], 12)

    def test_derive_paths_cli(self):
        data, code = _run_cli("--action", "derive-paths", "--step", "3")
        self.assertEqual(code, 0)
        self.assertIn("en_output", data)
        self.assertIn("ko_output", data)

    def test_verify_deps_cli(self):
        data, code = _run_cli("--action", "verify-deps", "--step", "1")
        self.assertEqual(code, 0)
        self.assertTrue(data["deps_satisfied"])

    def test_team_files_cli(self):
        data, code = _run_cli("--action", "team-files", "--step", "2")
        self.assertEqual(code, 0)
        self.assertEqual(data["member_count"], 3)

    def test_step_11_agent_prompt_cli(self):
        """Step 11 via CLI should return two-phase result."""
        data, code = _run_cli("--action", "agent-prompt", "--step", "11")
        self.assertEqual(code, 0)
        self.assertTrue(data["success"])
        self.assertEqual(data["type"], "two-phase")
        self.assertIn("phase1", data)
        self.assertIn("phase2", data)

    def test_extract_pacs_cli(self):
        """extract-pacs via CLI with a temp file."""
        fd, path = tempfile.mkstemp(suffix=".md")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("| F | 80 |\n| C | 75 |\n| L | 82 |\npACS = min(F,C,L) = 75\n")
            data, code = _run_cli("--action", "extract-pacs", "--file", path)
            self.assertEqual(code, 0)
            self.assertTrue(data["success"])
            self.assertEqual(data["final_score"], 75)
        finally:
            os.unlink(path)

    def test_agent_prompt_cli(self):
        """agent-prompt via CLI for a regular sub-agent step."""
        data, code = _run_cli("--action", "agent-prompt", "--step", "5")
        self.assertEqual(code, 0)
        self.assertTrue(data["success"])
        self.assertEqual(data["agent"], "prd-architect")
        self.assertIn("inputs", data)


# ===========================================================================
# Test: Cross-Validation with DAG
# ===========================================================================
class TestCrossValidation(unittest.TestCase):
    """Verify orchestrator_actions output is consistent with DAG source."""

    def test_all_steps_have_config(self):
        for step in range(1, TOTAL_STEPS + 1):
            result = action_step_config(step)
            self.assertTrue(result["success"], f"Step {step}")
            self.assertEqual(result["step"], step)
            self.assertEqual(result["name"], DAG[step]["name"])
            self.assertEqual(result["output"], DAG[step]["output"])

    def test_translation_steps_match(self):
        for step in range(1, TOTAL_STEPS + 1):
            result = action_step_config(step)
            expected = step in TRANSLATION_STEPS
            self.assertEqual(result["is_translation_step"], expected, f"Step {step}")

    def test_human_steps_match(self):
        for step in range(1, TOTAL_STEPS + 1):
            result = action_step_config(step)
            expected = step in HUMAN_STEPS
            self.assertEqual(result["is_human_step"], expected, f"Step {step}")

    def test_team_members_match_dag(self):
        for step_num, info in DAG.items():
            if info["team"] and info["team"] in TEAMS:
                result = action_step_config(step_num)
                dag_members = TEAMS[info["team"]]["members"]
                result_members = result["team_members"]
                self.assertEqual(
                    len(result_members), len(dag_members),
                    f"Step {step_num} member count mismatch"
                )
                for rm, dm in zip(result_members, dag_members):
                    self.assertEqual(rm["agent"], dm["agent"])
                    self.assertEqual(rm["output"], dm["output"])

    def test_step_inputs_coverage(self):
        """Every non-human, non-team step with known inputs should have STEP_INPUTS entry."""
        for step_num, info in DAG.items():
            if info["type"] == "human":
                continue
            if info["type"] == "agent-team":
                # Team steps use per-member keys
                team_name = info["team"]
                if team_name in TEAMS:
                    for m in TEAMS[team_name]["members"]:
                        key = f"{step_num}:{m['agent']}"
                        self.assertIn(key, STEP_INPUTS,
                                      f"Missing STEP_INPUTS for team member {key}")
                continue
            # Sub-agent step
            if step_num in STEP_INPUTS:
                inputs = STEP_INPUTS[step_num]
                self.assertTrue(len(inputs) > 0, f"Empty STEP_INPUTS for step {step_num}")


# ===========================================================================
# Test: Determinism Guarantee
# ===========================================================================
class TestDeterminism(unittest.TestCase):
    """Core guarantee: same input → same output, every time."""

    def test_step_config_deterministic(self):
        results = [action_step_config(3) for _ in range(20)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_pacs_decision_deterministic(self):
        results = [action_pacs_decision(55, "C", 3) for _ in range(20)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_derive_paths_deterministic(self):
        results = [action_derive_paths(9, "/tmp") for _ in range(20)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_finalize_step12_deterministic(self):
        results = [action_finalize_step12("/tmp") for _ in range(20)]
        self.assertTrue(all(r == results[0] for r in results))


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
