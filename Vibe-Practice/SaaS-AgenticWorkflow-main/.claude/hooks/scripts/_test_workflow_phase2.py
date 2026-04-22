#!/usr/bin/env python3
"""
Tests for Phase 2 Workflow Infrastructure.

Coverage:
  - _workflow_dag_phase2.py: DAG structure, constants, STEP_INPUTS
  - _workflow_registry.py: polymorphic loading, phase detection, helpers
  - orchestrator_actions.py: --workflow phase2 integration
  - quality_gate_runner.py: gate_profile routing, L3 gate
  - sot_manager.py: --workflow phase2 init
  - Phase 1 regression: all existing behavior preserved

Run:
    python3 .claude/hooks/scripts/_test_workflow_phase2.py
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

from _workflow_dag_phase2 import (
    DAG as DAG_P2,
    TEAMS as TEAMS_P2,
    TOTAL_STEPS as TOTAL_P2,
    HUMAN_STEPS as HUMAN_P2,
    TRANSLATION_STEPS as TRANS_P2,
    PACS_DIMENSIONS,
    GATE_PROFILES,
    L3_STEPS,
    STEP_INPUTS as STEP_INPUTS_P2,
)
from _workflow_dag import (
    DAG as DAG_P1,
    TEAMS as TEAMS_P1,
    TOTAL_STEPS as TOTAL_P1,
    HUMAN_STEPS as HUMAN_P1,
    TRANSLATION_STEPS as TRANS_P1,
)
from _workflow_registry import (
    get_workflow,
    detect_phase_from_sot,
    get_step_inputs,
    get_pacs_dimensions,
    get_gate_profile,
    VALID_PHASES,
    DEFAULT_PHASE,
)
from orchestrator_actions import (
    action_step_config,
    action_team_files,
    action_agent_prompt,
    action_pacs_decision,
    action_verify_deps,
    action_finalize_step12,
    action_derive_paths,
    _get_step_inputs,
)


def _run_cli(script, *args):
    """Run a script as subprocess, return parsed JSON."""
    script_path = os.path.join(_SCRIPTS_DIR, script)
    cmd = [sys.executable, script_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout), result.returncode


# ===========================================================================
# Phase 2 DAG Structure
# ===========================================================================
class TestPhase2DAG(unittest.TestCase):
    """Verify Phase 2 DAG structure and constants."""

    def test_total_steps(self):
        self.assertEqual(TOTAL_P2, 16)

    def test_dag_has_all_steps(self):
        for step in range(1, 17):
            self.assertIn(step, DAG_P2, f"Step {step} missing from Phase 2 DAG")

    def test_human_steps(self):
        self.assertEqual(sorted(HUMAN_P2), [3, 12, 16])

    def test_translation_steps(self):
        self.assertEqual(TRANS_P2, [15])

    def test_pacs_dimensions_4d(self):
        self.assertEqual(PACS_DIMENSIONS, ["F", "C", "L", "T"])

    def test_l3_steps(self):
        self.assertEqual(L3_STEPS, [13])

    def test_gate_profiles_defined_for_all_steps(self):
        for step_num in DAG_P2:
            self.assertIn(step_num, GATE_PROFILES)

    def test_code_steps_have_code_profile(self):
        code_steps = [4, 5, 6, 7, 8, 9, 10, 11, 13, 14]
        for step in code_steps:
            self.assertEqual(
                GATE_PROFILES[step], "code",
                f"Step {step} should have 'code' gate_profile",
            )

    def test_document_steps_have_document_profile(self):
        doc_steps = [1, 2, 15]
        for step in doc_steps:
            self.assertEqual(
                GATE_PROFILES[step], "document",
                f"Step {step} should have 'document' gate_profile",
            )

    def test_human_steps_have_none_profile(self):
        for step in HUMAN_P2:
            self.assertIsNone(
                GATE_PROFILES[step],
                f"Human step {step} should have None gate_profile",
            )

    def test_dag_fields_complete(self):
        """Every step has all required fields."""
        required = {"name", "deps", "type", "agent", "team", "human",
                     "pre_script", "review", "translate", "output", "gate_profile"}
        for step_num, info in DAG_P2.items():
            for field in required:
                self.assertIn(
                    field, info,
                    f"Step {step_num} missing field: {field}",
                )

    def test_teams_exist_for_team_steps(self):
        for step_num, info in DAG_P2.items():
            if info["type"] == "agent-team":
                self.assertIsNotNone(info["team"])
                self.assertIn(info["team"], TEAMS_P2,
                              f"Step {step_num} team '{info['team']}' not in TEAMS")

    def test_four_teams(self):
        self.assertEqual(len(TEAMS_P2), 4)
        expected = {"architecture-design-team", "engine-frontend-team",
                    "engine-analysis-team", "code-generation-team"}
        self.assertEqual(set(TEAMS_P2.keys()), expected)

    def test_each_team_has_three_members(self):
        for team_name, team in TEAMS_P2.items():
            self.assertEqual(
                len(team["members"]), 3,
                f"Team '{team_name}' should have 3 members",
            )

    def test_step_inputs_has_entries(self):
        self.assertGreater(len(STEP_INPUTS_P2), 0)

    def test_step_inputs_per_member_keys(self):
        """Per-member keys like '6:engine-impl-e1' should exist."""
        self.assertIn("6:engine-impl-e1", STEP_INPUTS_P2)
        self.assertIn("2:engine-architect", STEP_INPUTS_P2)
        self.assertIn("8:engine-impl-e7", STEP_INPUTS_P2)


# ===========================================================================
# Workflow Registry
# ===========================================================================
class TestWorkflowRegistry(unittest.TestCase):
    """Verify polymorphic workflow loading."""

    def test_valid_phases(self):
        self.assertEqual(VALID_PHASES, frozenset({"phase1", "phase2"}))

    def test_default_phase(self):
        self.assertEqual(DEFAULT_PHASE, "phase1")

    def test_load_phase1(self):
        wf = get_workflow("phase1")
        self.assertEqual(wf.TOTAL_STEPS, 12)
        self.assertIn(1, wf.DAG)

    def test_load_phase2(self):
        wf = get_workflow("phase2")
        self.assertEqual(wf.TOTAL_STEPS, 16)
        self.assertIn(16, wf.DAG)

    def test_default_loads_phase1(self):
        wf = get_workflow()
        self.assertEqual(wf.TOTAL_STEPS, 12)

    def test_invalid_phase_raises(self):
        with self.assertRaises(ValueError):
            get_workflow("phase3")

    def test_caching(self):
        wf1 = get_workflow("phase1")
        wf2 = get_workflow("phase1")
        self.assertIs(wf1, wf2)

    def test_get_pacs_dimensions_phase1(self):
        dims = get_pacs_dimensions("phase1")
        self.assertEqual(dims, ["F", "C", "L"])

    def test_get_pacs_dimensions_phase2(self):
        dims = get_pacs_dimensions("phase2")
        self.assertEqual(dims, ["F", "C", "L", "T"])

    def test_get_gate_profile_phase1(self):
        # Phase 1 non-human step → "document"
        self.assertEqual(get_gate_profile("phase1", 1), "document")

    def test_get_gate_profile_phase1_human(self):
        self.assertIsNone(get_gate_profile("phase1", 4))

    def test_get_gate_profile_phase2_code(self):
        self.assertEqual(get_gate_profile("phase2", 5), "code")

    def test_get_gate_profile_phase2_document(self):
        self.assertEqual(get_gate_profile("phase2", 1), "document")

    def test_get_step_inputs_phase1(self):
        inputs = get_step_inputs("phase1")
        # Phase 1 STEP_INPUTS co-located with DAG (same pattern as Phase 2)
        self.assertIn(1, inputs)
        self.assertEqual(inputs[1], ["coding-resource/PRD.md"])

    def test_get_step_inputs_phase2(self):
        inputs = get_step_inputs("phase2")
        self.assertIn(1, inputs)
        self.assertIn("6:engine-impl-e1", inputs)

    def test_detect_phase_no_sot(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(detect_phase_from_sot(td), DEFAULT_PHASE)


# ===========================================================================
# Orchestrator Actions — Phase 2 Integration
# ===========================================================================
class TestStepConfigPhase2(unittest.TestCase):
    """Verify step-config action with Phase 2 workflow."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_step_1_config(self):
        result = action_step_config(1, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["name"], "PRD Technical Extraction")
        self.assertEqual(result["agent"], "prd-tech-analyst")
        self.assertEqual(result["gate_profile"], "document")

    def test_step_5_code_profile(self):
        result = action_step_config(5, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["gate_profile"], "code")

    def test_step_3_human(self):
        result = action_step_config(3, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertTrue(result["is_human_step"])
        self.assertIsNone(result["gate_profile"])

    def test_step_6_team_members(self):
        result = action_step_config(6, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "agent-team")
        self.assertEqual(result["team"], "engine-frontend-team")
        self.assertEqual(len(result["team_members"]), 3)

    def test_no_special_flow(self):
        """Phase 2 should never have special_flow."""
        for step in range(1, 17):
            result = action_step_config(step, wf=self.wf)
            self.assertIsNone(result.get("special_flow"),
                              f"Step {step} should have no special_flow in Phase 2")

    def test_step_16_is_last(self):
        result = action_step_config(16, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertTrue(result["is_human_step"])
        self.assertEqual(result["name"], "Release Approval")

    def test_invalid_step_17(self):
        result = action_step_config(17, wf=self.wf)
        self.assertFalse(result["success"])


class TestTeamFilesPhase2(unittest.TestCase):
    """Verify team-files action with Phase 2 teams."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_engine_frontend_team(self):
        result = action_team_files(6, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["team_name"], "engine-frontend-team")
        self.assertEqual(result["member_count"], 3)
        agents = [m["agent"] for m in result["members"]]
        self.assertIn("engine-impl-e1", agents)
        self.assertIn("engine-impl-e2", agents)
        self.assertIn("engine-impl-e3", agents)

    def test_code_generation_team(self):
        result = action_team_files(8, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["team_name"], "code-generation-team")

    def test_non_team_step_errors(self):
        result = action_team_files(5, ".", wf=self.wf)
        self.assertFalse(result["success"])


class TestAgentPromptPhase2(unittest.TestCase):
    """Verify agent-prompt action with Phase 2 STEP_INPUTS."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_step_1_inputs(self):
        result = action_agent_prompt(1, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["agent"], "prd-tech-analyst")
        self.assertIn("prompt/PRD-SaaS-AutoBuilder.md", result["inputs"])

    def test_team_step_per_member_inputs(self):
        result = action_agent_prompt(6, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "agent-team")
        # Check first member has per-member inputs
        e1 = result["member_prompts"][0]
        self.assertEqual(e1["agent"], "engine-impl-e1")
        self.assertIn("dev/engine-context/e1-context.md", e1["inputs"])

    def test_human_step_errors(self):
        result = action_agent_prompt(3, ".", wf=self.wf)
        self.assertFalse(result["success"])


class TestStepInputsPhase2(unittest.TestCase):
    """Verify _get_step_inputs with Phase 2 workflow."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_step_1_inputs(self):
        inputs = _get_step_inputs(1, wf=self.wf)
        self.assertEqual(inputs, ["prompt/PRD-SaaS-AutoBuilder.md"])

    def test_per_member_inputs(self):
        inputs = _get_step_inputs(6, member_agent="engine-impl-e1", wf=self.wf)
        self.assertIn("dev/engine-context/e1-context.md", inputs)
        self.assertIn("dev/architecture/system-architecture.md", inputs)

    def test_missing_step_returns_empty(self):
        inputs = _get_step_inputs(99, wf=self.wf)
        self.assertEqual(inputs, [])


class TestPacsDecisionT(unittest.TestCase):
    """Verify pACS decision includes T (Testability) feedback."""

    def test_red_t_dimension(self):
        result = action_pacs_decision(40, "T", 7)
        self.assertTrue(result["success"])
        self.assertEqual(result["color"], "RED")
        self.assertIn("testability", result["feedback"].lower())

    def test_green_t_dimension(self):
        result = action_pacs_decision(80, "T", 7)
        self.assertEqual(result["action"], "proceed")


class TestFinalizeStep12Phase2(unittest.TestCase):
    """Verify finalize-step12 rejects Phase 2."""

    def test_rejects_phase2(self):
        wf = get_workflow("phase2")
        result = action_finalize_step12(".", wf=wf)
        self.assertFalse(result["success"])
        self.assertIn("Phase 1-specific", result["error"])

    def test_accepts_phase1(self):
        wf = get_workflow("phase1")
        result = action_finalize_step12(".", wf=wf)
        self.assertTrue(result["success"])


class TestVerifyDepsPhase2(unittest.TestCase):
    """Verify dependency checking with Phase 2 DAG."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_step_1_no_deps(self):
        result = action_verify_deps(1, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertTrue(result["deps_satisfied"])

    def test_step_9_deps_on_6_7_8(self):
        result = action_verify_deps(9, ".", wf=self.wf)
        self.assertTrue(result["success"])
        # deps not satisfied (files don't exist)
        self.assertFalse(result["deps_satisfied"])
        # Should have missing entries for steps 6, 7, 8
        missing_steps = [m["step"] for m in result["missing"]]
        self.assertIn(6, missing_steps)
        self.assertIn(7, missing_steps)
        self.assertIn(8, missing_steps)


class TestDerivePathsPhase2(unittest.TestCase):
    """Verify path derivation for Phase 2."""

    def setUp(self):
        self.wf = get_workflow("phase2")

    def test_code_step_no_ko(self):
        """Code steps (translate=False) should have ko_output=None."""
        result = action_derive_paths(5, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertIsNone(result["ko_output"])

    def test_doc_step_has_ko(self):
        """Step 15 (translate=True) should have ko_output."""
        result = action_derive_paths(15, ".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["ko_output"])
        self.assertIn(".ko.", result["ko_output"])


# ===========================================================================
# CLI Integration — --workflow flag
# ===========================================================================
class TestCLIWorkflowFlag(unittest.TestCase):
    """Verify --workflow flag works via CLI subprocess."""

    def test_phase1_default(self):
        result, rc = _run_cli("orchestrator_actions.py",
                              "--action", "step-config", "--step", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(result["name"], "PRD Foundation Extraction")

    def test_phase2_explicit(self):
        result, rc = _run_cli("orchestrator_actions.py",
                              "--action", "step-config", "--step", "1",
                              "--workflow", "phase2")
        self.assertEqual(rc, 0)
        self.assertEqual(result["name"], "PRD Technical Extraction")

    def test_phase2_step_16(self):
        result, rc = _run_cli("orchestrator_actions.py",
                              "--action", "step-config", "--step", "16",
                              "--workflow", "phase2")
        self.assertEqual(rc, 0)
        self.assertEqual(result["name"], "Release Approval")

    def test_phase1_step_16_invalid(self):
        result, rc = _run_cli("orchestrator_actions.py",
                              "--action", "step-config", "--step", "16",
                              "--workflow", "phase1")
        self.assertEqual(rc, 1)
        self.assertFalse(result["success"])

    def test_phase2_team_files(self):
        result, rc = _run_cli("orchestrator_actions.py",
                              "--action", "team-files", "--step", "6",
                              "--workflow", "phase2", "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["team_name"], "engine-frontend-team")

    def test_quality_gate_phase2(self):
        """Quality gate runner with --workflow phase2."""
        # Use an existing file to pass L0
        result, rc = _run_cli("quality_gate_runner.py",
                              "--step", "5", "--workflow", "phase2",
                              "--project-dir", ".",
                              "--output-path", "coding-resource/PRD.md",
                              "--skip-review", "--skip-translation")
        self.assertEqual(rc, 0)
        # Should have L1 as code gate (skipped — no tsconfig)
        self.assertIn("L1-code", result["gates"]["L1"]["details"])
        # Should have L3 skipped (not an L3 step)
        self.assertIn("L3", result["gates"])


# ===========================================================================
# Phase 1 Regression
# ===========================================================================
class TestPhase1Regression(unittest.TestCase):
    """Verify Phase 1 behavior is completely preserved."""

    def setUp(self):
        self.wf = get_workflow("phase1")

    def test_step_config_unchanged(self):
        result = action_step_config(1, wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["name"], "PRD Foundation Extraction")
        self.assertEqual(result["agent"], "prd-analyst")
        # Phase 1 has no gate_profile field in DAG → returns None
        self.assertIsNone(result["gate_profile"])

    def test_step_11_special_flow(self):
        result = action_step_config(11, wf=self.wf)
        self.assertEqual(result["special_flow"], "two-phase")

    def test_step_12_total(self):
        self.assertEqual(self.wf.TOTAL_STEPS, 12)

    def test_human_steps(self):
        self.assertEqual(sorted(self.wf.HUMAN_STEPS), [4, 8, 12])

    def test_phase1_dag_untouched(self):
        """Phase 1 DAG module should be the original _workflow_dag."""
        self.assertEqual(len(self.wf.DAG), 12)
        self.assertIn("prd-analysis-team", self.wf.TEAMS)
        self.assertIn("prd-generation-team", self.wf.TEAMS)

    def test_step_inputs_fallback(self):
        """Phase 1 _get_step_inputs should use module-level STEP_INPUTS."""
        inputs = _get_step_inputs(1, wf=self.wf)
        self.assertEqual(inputs, ["coding-resource/PRD.md"])

    def test_finalize_step12_works(self):
        result = action_finalize_step12(".", wf=self.wf)
        self.assertTrue(result["success"])
        self.assertEqual(result["step"], 12)

    def test_no_l3_in_phase1(self):
        """Phase 1 should not have L3_STEPS."""
        self.assertFalse(hasattr(self.wf, "L3_STEPS"))


# ===========================================================================
# SOT Manager Phase 2 Init (dry run)
# ===========================================================================
class TestSOTManagerPhase2(unittest.TestCase):
    """Verify sot_manager.py --workflow phase2 --init."""

    def test_phase2_init(self):
        """Phase 2 init should create a 16-step SOT with 4D pACS."""
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            result = subprocess.run(
                [sys.executable, os.path.join(_SCRIPTS_DIR, "sot_manager.py"),
                 "--project-dir", td, "--init", "--workflow", "phase2"],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            # Read and verify
            sot_path = os.path.join(claude_dir, "state.yaml")
            self.assertTrue(os.path.exists(sot_path))
            import yaml
            with open(sot_path) as f:
                sot = yaml.safe_load(f)
            wf = sot["workflow"]
            self.assertEqual(wf["total_steps"], 16)
            self.assertEqual(sorted(wf["pacs"]["dimensions"].keys()), ["C", "F", "L", "T"])
            self.assertIn("parent_genome", wf)

    def test_phase1_init_unchanged(self):
        """Phase 1 init should create a 12-step SOT with 3D pACS."""
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            result = subprocess.run(
                [sys.executable, os.path.join(_SCRIPTS_DIR, "sot_manager.py"),
                 "--project-dir", td, "--init"],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            import yaml
            sot_path = os.path.join(claude_dir, "state.yaml")
            with open(sot_path) as f:
                sot = yaml.safe_load(f)
            wf = sot["workflow"]
            self.assertEqual(wf["total_steps"], 12)
            self.assertEqual(sorted(wf["pacs"]["dimensions"].keys()), ["C", "F", "L"])
            self.assertNotIn("T", wf["pacs"]["dimensions"])


# ===========================================================================
# Task DAG Init — Phase 2
# ===========================================================================
class TestTaskDagInitPhase2(unittest.TestCase):
    """Verify task_dag_init.py with --workflow flag."""

    def test_phase1_default(self):
        result, rc = _run_cli("task_dag_init.py", "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["total_steps"], 12)
        self.assertEqual(len(result["teams"]), 2)

    def test_phase2_explicit(self):
        result, rc = _run_cli("task_dag_init.py", "--workflow", "phase2",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["total_steps"], 16)
        self.assertEqual(len(result["teams"]), 4)

    def test_phase2_gate_profiles(self):
        result, rc = _run_cli("task_dag_init.py", "--workflow", "phase2",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        # Step 5 (index 4) should be "code" gate_profile
        step5 = [s for s in result["steps"] if s["step_number"] == 5][0]
        self.assertEqual(step5["gate_profile"], "code")

    def test_phase1_no_gate_profile(self):
        result, rc = _run_cli("task_dag_init.py", "--project-dir", ".")
        self.assertEqual(rc, 0)
        # Phase 1 steps should not have gate_profile key
        step1 = result["steps"][0]
        self.assertNotIn("gate_profile", step1)

    def test_phase2_translation_steps(self):
        result, rc = _run_cli("task_dag_init.py", "--workflow", "phase2",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["translation_steps"], [15])


# ===========================================================================
# Workflow Router — Phase 2
# ===========================================================================
class TestWorkflowRouterPhase2(unittest.TestCase):
    """Verify workflow_router.py with --workflow flag."""

    def test_phase1_start(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "0",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["next_steps"], [1])

    def test_phase1_complete(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "12",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["next_steps"], [])
        self.assertIn("12 steps", result["reason"])

    def test_phase2_start(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "0",
                              "--workflow", "phase2", "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["next_steps"], [1])

    def test_phase2_complete(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "16",
                              "--workflow", "phase2", "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertEqual(result["next_steps"], [])
        self.assertIn("16 steps", result["reason"])

    def test_phase2_invalid_step_17(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "17",
                              "--workflow", "phase2", "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertIn("Invalid step 17", result["reason"])

    def test_phase1_step_13_invalid(self):
        result, rc = _run_cli("workflow_router.py", "--current-step", "13",
                              "--project-dir", ".")
        self.assertEqual(rc, 0)
        self.assertIn("Invalid step 13", result["reason"])


# ===========================================================================
# Manifest Generator — Phase 2
# ===========================================================================
class TestManifestGeneratorPhase2(unittest.TestCase):
    """Verify manifest_generator.py with --workflow flag."""

    def test_phase1_invalid_step(self):
        result, rc = _run_cli("manifest_generator.py", "--step", "99",
                              "--project-dir", ".", "--files", "x.md")
        self.assertEqual(rc, 1)
        self.assertFalse(result["valid"])
        self.assertIn("Step 99 not found in DAG", result["errors"])

    def test_phase2_invalid_step(self):
        result, rc = _run_cli("manifest_generator.py", "--step", "99",
                              "--workflow", "phase2",
                              "--project-dir", ".", "--files", "x.md")
        self.assertEqual(rc, 1)
        self.assertFalse(result["valid"])

    def test_phase2_valid_step_missing_file(self):
        result, rc = _run_cli("manifest_generator.py", "--step", "6",
                              "--workflow", "phase2",
                              "--project-dir", ".", "--files", "nonexistent.md")
        self.assertEqual(rc, 1)
        self.assertFalse(result["valid"])
        self.assertIn("File not found: nonexistent.md", result["errors"])

    def test_phase2_step_6_accepted(self):
        """Phase 2 step 6 (team step) should be recognized."""
        result, rc = _run_cli("manifest_generator.py", "--step", "6",
                              "--workflow", "phase2",
                              "--project-dir", ".",
                              "--files", "coding-resource/PRD.md")
        # Should accept the step even if the file path doesn't match output_dir
        self.assertEqual(rc, 0)
        self.assertTrue(result["valid"])


# ===========================================================================
# Context Memory — CM-1 (Design Decisions) and CM-2 (Workflow Phase)
# ===========================================================================
class TestContextMemoryCM1(unittest.TestCase):
    """CM-1: Verify design decision extraction for SessionStart surfacing."""

    def test_extract_design_decisions(self):
        from restore_context import _extract_recent_design_decisions
        sessions = [
            {"design_decisions": ["Use polymorphic registry", "[intent] minor fix"]},
            {"design_decisions": ["L3 gate at Step 13 only"]},
        ]
        result = _extract_recent_design_decisions(sessions)
        self.assertEqual(len(result), 2)
        self.assertIn("L3 gate at Step 13 only", result)
        self.assertIn("Use polymorphic registry", result)
        # [intent] should be filtered
        self.assertNotIn("[intent] minor fix", result)

    def test_extract_empty_sessions(self):
        from restore_context import _extract_recent_design_decisions
        result = _extract_recent_design_decisions([])
        self.assertEqual(result, [])

    def test_extract_no_decisions(self):
        from restore_context import _extract_recent_design_decisions
        sessions = [{"error_patterns": []}]
        result = _extract_recent_design_decisions(sessions)
        self.assertEqual(result, [])

    def test_max_three(self):
        from restore_context import _extract_recent_design_decisions
        sessions = [
            {"design_decisions": ["D1", "D2", "D3", "D4", "D5"]},
        ]
        result = _extract_recent_design_decisions(sessions)
        self.assertEqual(len(result), 3)


class TestContextMemoryCM2(unittest.TestCase):
    """CM-2: Verify workflow Phase detection for context recovery."""

    def test_detect_phase1(self):
        from restore_context import _detect_workflow_phase
        import yaml
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            sot_data = {
                "workflow": {
                    "name": "SaaS Auto-Builder PRD Generation",
                    "current_step": 5,
                    "total_steps": 12,
                    "status": "running",
                }
            }
            with open(os.path.join(claude_dir, "state.yaml"), "w") as f:
                yaml.dump(sot_data, f)
            result = _detect_workflow_phase(td)
            self.assertIn("Phase 1", result)
            self.assertIn("Step 5/12", result)
            self.assertIn("running", result)

    def test_detect_phase2(self):
        from restore_context import _detect_workflow_phase
        import yaml
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            sot_data = {
                "workflow": {
                    "name": "SaaS Fullstack Development",
                    "current_step": 10,
                    "total_steps": 16,
                    "status": "running",
                }
            }
            with open(os.path.join(claude_dir, "state.yaml"), "w") as f:
                yaml.dump(sot_data, f)
            result = _detect_workflow_phase(td)
            self.assertIn("Phase 2", result)
            self.assertIn("Step 10/16", result)

    def test_no_sot(self):
        from restore_context import _detect_workflow_phase
        with tempfile.TemporaryDirectory() as td:
            result = _detect_workflow_phase(td)
            self.assertIsNone(result)


# ===========================================================================
# P1: L1 Document Gate (validate_l1_document.py)
# ===========================================================================
class TestL1DocumentGate(unittest.TestCase):
    """P1: Verify structural L1 gate for document outputs."""

    def test_prd_fails_d5_no_pacs(self):
        """PRD.md is a source file — no pACS section → D5 fails."""
        from validate_l1_document import validate_l1_document
        result = validate_l1_document(
            "coding-resource/PRD.md", ".", 1
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["D5_pacs_section"]["passed"])

    def test_prd_passes_d1_sections(self):
        """PRD.md has many sections → D1 passes."""
        from validate_l1_document import validate_l1_document
        result = validate_l1_document(
            "coding-resource/PRD.md", ".", 1
        )
        self.assertTrue(result["checks"]["D1_sections"]["passed"])
        self.assertGreater(result["checks"]["D1_sections"]["found"], 3)

    def test_prd_passes_d2_content_depth(self):
        """PRD.md has substantial content → D2 passes."""
        from validate_l1_document import validate_l1_document
        result = validate_l1_document(
            "coding-resource/PRD.md", ".", 1
        )
        self.assertTrue(result["checks"]["D2_content_depth"]["passed"])

    def test_nonexistent_file(self):
        from validate_l1_document import validate_l1_document
        result = validate_l1_document(
            "nonexistent.md", ".", 1
        )
        self.assertFalse(result["passed"])
        self.assertIn("not found", result["warnings"][0])

    def test_small_file_fails_d2(self):
        """A tiny document should fail D2 (content depth)."""
        from validate_l1_document import validate_l1_document
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Title\n\nShort.\n\n## Section 2\n\nBrief.\n\n## Section 3\n\nMinimal.\n")
            f.flush()
            result = validate_l1_document(f.name, ".", 1)
        os.unlink(f.name)
        self.assertFalse(result["checks"]["D2_content_depth"]["passed"])

    def test_cli_phase2(self):
        """CLI with --workflow phase2 should work."""
        result, rc = _run_cli(
            "validate_l1_document.py",
            "--step", "1", "--workflow", "phase2",
            "--project-dir", ".",
            "--output-path", "coding-resource/PRD.md",
        )
        # Should fail D5 (no pACS) but run without errors
        self.assertEqual(rc, 1)
        self.assertIn("D5_pacs_section", result["checks"])

    def test_d4_skipped_for_step_1(self):
        """Step 1 has no deps → D4 should be skipped (passed=True)."""
        from validate_l1_document import validate_l1_document
        result = validate_l1_document(
            "coding-resource/PRD.md", ".", 1
        )
        self.assertTrue(result["checks"]["D4_trace_markers"]["passed"])


# ===========================================================================
# P2+P5: Step Progression Guard (validate_step_progression.py)
# ===========================================================================
class TestStepProgressionGuard(unittest.TestCase):
    """P2+P5: Verify step progression validation."""

    def test_no_sot_blocks(self):
        """No SOT → cannot verify progression → block."""
        from validate_step_progression import validate_progression
        with tempfile.TemporaryDirectory() as td:
            result = validate_progression(1, td)
            self.assertFalse(result["can_progress"])
            self.assertTrue(any("SOT" in b for b in result["blockers"]))

    def test_complete_step_passes(self):
        """Step with all obligations met should pass."""
        from validate_step_progression import validate_progression
        import yaml
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            # Create SOT with output, pACS, and translation (Step 1 has translate=true)
            sot = {
                "workflow": {
                    "name": "test",
                    "total_steps": 12,
                    "current_step": 1,
                    "status": "running",
                    "outputs": {
                        "step-1": "prompt/research/test.md",
                        "step-1-ko": "prompt/research/test.ko.md",
                    },
                    "pacs": {
                        "history": {
                            "step-1": {"score": 75, "action_taken": "proceed"},
                        },
                    },
                },
            }
            with open(os.path.join(claude_dir, "state.yaml"), "w") as f:
                yaml.dump(sot, f)
            # Create the output file + translation
            out_dir = os.path.join(td, "prompt", "research")
            os.makedirs(out_dir)
            with open(os.path.join(out_dir, "test.md"), "w") as f:
                f.write("x" * 200)
            with open(os.path.join(out_dir, "test.ko.md"), "w") as f:
                f.write("x" * 200)

            result = validate_progression(1, td)
            self.assertTrue(result["can_progress"])
            self.assertEqual(result["blockers"], [])

    def test_red_pacs_without_rework_blocks(self):
        """RED pACS with action_taken=proceed should block (SP3)."""
        from validate_step_progression import validate_progression
        import yaml
        with tempfile.TemporaryDirectory() as td:
            claude_dir = os.path.join(td, ".claude")
            os.makedirs(claude_dir)
            sot = {
                "workflow": {
                    "outputs": {"step-1": "test.md"},
                    "pacs": {
                        "history": {
                            "step-1": {
                                "score": 40,
                                "decision_action": "rework_required",
                                "action_taken": "proceed",
                            },
                        },
                    },
                },
            }
            with open(os.path.join(claude_dir, "state.yaml"), "w") as f:
                yaml.dump(sot, f)
            with open(os.path.join(td, "test.md"), "w") as f:
                f.write("x" * 200)

            result = validate_progression(1, td)
            self.assertFalse(result["can_progress"])
            self.assertTrue(any("SP3" in b for b in result["blockers"]))

    def test_missing_translation_blocks(self):
        """translate=true but no .ko output → blocks (SP4)."""
        from validate_step_progression import validate_progression
        import yaml
        wf = get_workflow("phase1")
        # Find a step with translate=true
        trans_steps = [s for s, info in wf.DAG.items() if info.get("translate")]
        if trans_steps:
            step = trans_steps[0]
            with tempfile.TemporaryDirectory() as td:
                claude_dir = os.path.join(td, ".claude")
                os.makedirs(claude_dir)
                sot = {
                    "workflow": {
                        "outputs": {f"step-{step}": "test.md"},
                        "pacs": {
                            "history": {
                                f"step-{step}": {"score": 80},
                            },
                        },
                    },
                }
                with open(os.path.join(claude_dir, "state.yaml"), "w") as f:
                    yaml.dump(sot, f)
                with open(os.path.join(td, "test.md"), "w") as f:
                    f.write("x" * 200)

                result = validate_progression(step, td, wf=wf)
                self.assertFalse(result["can_progress"])
                self.assertTrue(any("SP4" in b for b in result["blockers"]))

    def test_human_step_only_checks_sot(self):
        """Human steps should only check SOT output registration."""
        from validate_step_progression import validate_progression
        result = validate_progression(4, ".")  # Step 4 is human
        # Should have SP1 check but NOT SP2-SP6
        self.assertIn("SP1_sot_output", result["checks"])
        self.assertNotIn("SP2_pacs_recorded", result["checks"])

    def test_invalid_step(self):
        from validate_step_progression import validate_progression
        result = validate_progression(99, ".")
        self.assertFalse(result["can_progress"])

    def test_cli_interface(self):
        """CLI should return valid JSON."""
        result, rc = _run_cli(
            "validate_step_progression.py",
            "--step", "1", "--project-dir", ".",
        )
        self.assertEqual(rc, 1)  # No SOT → fails
        self.assertIn("blockers", result)


# ===========================================================================
# P3: pACS Cross-Validation
# ===========================================================================
class TestPacsCrossValidation(unittest.TestCase):
    """P3: Verify structural cross-validation in extract-pacs."""

    def test_cross_validation_present(self):
        """extract-pacs should include cross_validation field."""
        result = _run_cli(
            "orchestrator_actions.py",
            "--action", "extract-pacs",
            "--file", "coding-resource/PRD.md",
            "--project-dir", ".",
        )[0]
        self.assertIn("cross_validation", result)
        self.assertIn("metrics", result["cross_validation"])
        self.assertIn("warnings", result["cross_validation"])

    def test_cross_validation_metrics(self):
        """Metrics should include section_count and file_references."""
        result = _run_cli(
            "orchestrator_actions.py",
            "--action", "extract-pacs",
            "--file", "coding-resource/PRD.md",
            "--project-dir", ".",
        )[0]
        metrics = result["cross_validation"]["metrics"]
        self.assertIn("section_count", metrics)
        self.assertIn("file_references", metrics)
        self.assertIn("avg_paragraph_bytes", metrics)

    def test_optimistic_f_flagged(self):
        """High F score with few file refs should trigger warning."""
        from orchestrator_actions import _cross_validate_pacs
        content = "## Section\nSome content with no file references at all.\n" * 10
        dims = {"F": 90, "C": 85, "L": 80}
        result = _cross_validate_pacs(content, dims, "/tmp/test.md")
        self.assertTrue(result["has_warnings"])
        self.assertTrue(any("F cross-check" in w for w in result["warnings"]))

    def test_no_warnings_for_good_output(self):
        """Well-structured doc with modest scores should have no warnings."""
        from orchestrator_actions import _cross_validate_pacs
        content = (
            "## Analysis\n\n"
            + "Reference to source.md and data.json and config.yaml.\n" * 20
            + "\n## Details\n\n"
            + "Detailed paragraph with substantial content. " * 20
            + "\n## Methodology\n\n"
            + "Another substantial section. " * 20
            + "\n## Conclusion\n\n"
            + "Final section. " * 20
        )
        dims = {"F": 65, "C": 60, "L": 55}
        result = _cross_validate_pacs(content, dims, "/tmp/test.md")
        self.assertFalse(result["has_warnings"])


# ===========================================================================
# P4: Extended L1 Code Gate
# ===========================================================================
class TestL1CodeGateExtended(unittest.TestCase):
    """P4: Verify extended L1 code gate (tsc + eslint + test check)."""

    def test_no_tsconfig_skips(self):
        """No tsconfig.json → skip all checks."""
        from quality_gate_runner import gate_l1_code
        with tempfile.TemporaryDirectory() as td:
            passed, details = gate_l1_code(td)
            self.assertTrue(passed)
            self.assertIn("skipped", details)

    def test_l1_code_via_quality_runner(self):
        """Quality gate runner should use extended L1 for code steps."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "5", "--workflow", "phase2",
            "--project-dir", ".",
            "--output-path", "coding-resource/PRD.md",
            "--skip-review", "--skip-translation",
        )
        self.assertEqual(rc, 0)
        self.assertIn("L1", result["gates"])
        # Should be L1-code (skipped — no tsconfig)
        self.assertIn("skipped", result["gates"]["L1"]["details"])


# ===========================================================================
# Integration: L1 Document Gate via Quality Gate Runner
# ===========================================================================
class TestL1DocumentIntegration(unittest.TestCase):
    """Verify L1 document gate integration in quality_gate_runner."""

    def test_document_step_runs_structural_check(self):
        """Phase 1 document step should run D1-D5, not auto-pass."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "1",
            "--project-dir", ".",
            "--output-path", "coding-resource/PRD.md",
            "--skip-review", "--skip-translation",
        )
        # L1 should NOT say "performed by orchestrator LLM" anymore
        l1 = result["gates"]["L1"]
        self.assertNotIn("orchestrator LLM", l1.get("details", ""))
        # Should mention D1-D5 or L1-doc
        self.assertTrue(
            "L1-doc" in l1.get("details", "") or
            "D5" in l1.get("details", ""),
            f"Expected structural L1 check, got: {l1}",
        )


# ===========================================================================
# 4th Reflection Fixes (F-1 ~ F-5)
# ===========================================================================
class TestHumanStepEarlyReturn(unittest.TestCase):
    """F-1: Human steps should be skipped by run_gates()."""

    def test_phase1_human_step_skipped(self):
        """Phase 1 human step (4) with approved-by-user returns skip."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "4",
            "--project-dir", ".",
            "--output-path", "approved-by-user",
            "--skip-review", "--skip-translation",
        )
        self.assertTrue(result["all_passed"])
        self.assertIn("skipped", result)
        self.assertIn("Human", result["skipped"])
        self.assertEqual(rc, 0)

    def test_phase2_human_step_skipped(self):
        """Phase 2 human step (3) with approved-by-user returns skip."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "3",
            "--workflow", "phase2",
            "--project-dir", ".",
            "--output-path", "approved-by-user",
            "--skip-review", "--skip-translation",
        )
        self.assertTrue(result["all_passed"])
        self.assertIn("skipped", result)
        self.assertEqual(rc, 0)

    def test_hybrid_human_step_runs_gates(self):
        """Phase 1 Step 12 (hybrid) with real output runs gates, not skip."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "12",
            "--project-dir", ".",
            "--output-path", "prompt/PRD-SaaS-AutoBuilder.md",
            "--skip-review", "--skip-translation",
        )
        # Should run gates (not skipped) — hybrid step with real output
        self.assertNotIn("skipped", result)
        self.assertIn("gates", result)
        # L0 may pass or fail depending on file existence, but gates should run
        self.assertIn("L0", result["gates"])

    def test_phase1_agent_step_not_skipped(self):
        """Phase 1 agent step (1) should NOT be skipped — should run gates."""
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "1",
            "--project-dir", ".",
            "--output-path", "coding-resource/PRD.md",
            "--skip-review", "--skip-translation",
        )
        # Should have gates (not skipped)
        self.assertIn("gates", result)
        self.assertIn("L0", result["gates"])
        self.assertNotIn("skipped", result)


class TestPhaseNameAttribute(unittest.TestCase):
    """F-2: Workflow DAG modules have PHASE_NAME attribute."""

    def test_phase1_has_phase_name(self):
        from _workflow_dag import PHASE_NAME
        self.assertEqual(PHASE_NAME, "phase1")

    def test_phase2_has_phase_name(self):
        from _workflow_dag_phase2 import PHASE_NAME
        self.assertEqual(PHASE_NAME, "phase2")

    def test_registry_exposes_phase_name(self):
        wf1 = get_workflow("phase1")
        wf2 = get_workflow("phase2")
        self.assertEqual(wf1.PHASE_NAME, "phase1")
        self.assertEqual(wf2.PHASE_NAME, "phase2")


class TestGateProfileFallback(unittest.TestCase):
    """F-1 cont: Phase 1 agent steps get gate_profile="document" fallback."""

    def test_phase1_step1_gets_document_profile(self):
        """Phase 1 step 1 has no gate_profile in DAG — should fall back to document."""
        # Phase 1 DAG does not have gate_profile field
        step_info = DAG_P1[1]
        self.assertNotIn("gate_profile", step_info)
        # Registry helper handles this correctly
        profile = get_gate_profile("phase1", 1)
        self.assertEqual(profile, "document")

    def test_phase1_human_gets_none_profile(self):
        """Phase 1 human step 4 — registry returns None."""
        profile = get_gate_profile("phase1", 4)
        self.assertIsNone(profile)

    def test_phase2_code_step_explicit(self):
        """Phase 2 code step has explicit gate_profile."""
        step_info = DAG_P2[4]
        self.assertEqual(step_info["gate_profile"], "code")

    def test_phase2_document_step_explicit(self):
        """Phase 2 document step has explicit gate_profile."""
        step_info = DAG_P2[1]
        self.assertEqual(step_info["gate_profile"], "document")


class TestCrossValidateNoPrivateImport(unittest.TestCase):
    """F-5: _cross_validate_pacs uses module-level re, not import re as _re."""

    def test_no_private_re_import(self):
        """Verify _cross_validate_pacs function body has no 'import re as _re'."""
        import inspect
        from orchestrator_actions import _cross_validate_pacs
        source = inspect.getsource(_cross_validate_pacs)
        self.assertNotIn("import re as _re", source)
        self.assertNotIn("_re.", source)

    def test_cross_validate_still_works(self):
        """Verify _cross_validate_pacs runs without error after import cleanup."""
        from orchestrator_actions import _cross_validate_pacs
        content = "# Test\n## Section 1\nSome content here.\n## Section 2\nMore content.\n"
        dims = {"F": 90, "C": 85, "L": 80}
        result = _cross_validate_pacs(content, dims, "/tmp/nonexistent.md")
        self.assertIn("warnings", result)
        self.assertIn("metrics", result)
        self.assertIsInstance(result["warnings"], list)


class TestPhaseDetectionInL1Document(unittest.TestCase):
    """F-3: gate_l1_document uses PHASE_NAME instead of PACS_DIMENSIONS heuristic."""

    def test_phase1_passes_correct_workflow_arg(self):
        """Phase 1 workflow should pass --workflow phase1 to validator."""
        # Run quality gate on a real file to verify phase routing
        result, rc = _run_cli(
            "quality_gate_runner.py",
            "--step", "1",
            "--workflow", "phase1",
            "--project-dir", ".",
            "--output-path", "coding-resource/PRD.md",
            "--skip-review", "--skip-translation",
        )
        l1 = result["gates"].get("L1", {})
        # Should run L1-doc (not L1-code)
        self.assertTrue(
            "L1-doc" in l1.get("details", "") or
            "D1" in l1.get("details", "") or
            "D5" in l1.get("details", ""),
            f"Expected structural L1 check for phase1, got: {l1}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
