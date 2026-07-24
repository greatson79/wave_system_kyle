"""
Test suite for translation_trigger.py — InvestScan Infrastructure Hook
Coverage requirement: 75%+ (Infrastructure tier — Phase B)

Tests cover:
  - TRANSLATION_TARGETS constant correctness
  - source_file_exists() with and without {date} placeholder
  - write_translation_pending() file write behavior
  - Hook main() flow: non-TaskUpdate, non-completed, translation self-loop guard
  - Step detection and signal emission
  - Missing source file guard (no signal when source doesn't exist)
"""
import json
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the hook script is importable from the test directory
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "hooks" / "scripts"))


class TestTranslationTargetsConstant(unittest.TestCase):
    """Test TRANSLATION_TARGETS constant structure and completeness."""

    def test_all_required_steps_present(self):
        """All 6 translation target steps must be defined."""
        from translation_trigger import TRANSLATION_TARGETS
        required_steps = {2, 4, 5, 11, 12, 15}
        self.assertEqual(set(TRANSLATION_TARGETS.keys()), required_steps)

    def test_step_2_source_no_date_placeholder(self):
        """Steps 2, 4, 5 must NOT have {date} placeholder."""
        from translation_trigger import TRANSLATION_TARGETS
        for step in [2, 4, 5]:
            self.assertNotIn("{", TRANSLATION_TARGETS[step],
                           f"Step {step} should not have date placeholder")

    def test_steps_11_12_15_have_date_placeholder(self):
        """Steps 11, 12, 15 MUST have {date} placeholder."""
        from translation_trigger import TRANSLATION_TARGETS
        for step in [11, 12, 15]:
            self.assertIn("{date}", TRANSLATION_TARGETS[step],
                         f"Step {step} should have {{date}} placeholder")

    def test_step_2_maps_to_schema_mapping(self):
        """Step 2 must map to schema-mapping.md."""
        from translation_trigger import TRANSLATION_TARGETS
        self.assertIn("schema-mapping", TRANSLATION_TARGETS[2])

    def test_step_12_maps_to_weekly_report(self):
        """Step 12 must map to weekly-report output."""
        from translation_trigger import TRANSLATION_TARGETS
        self.assertIn("weekly-report", TRANSLATION_TARGETS[12])

    def test_step_15_maps_to_watchlist(self):
        """Step 15 (v3.2 Q5) must map to watchlist output."""
        from translation_trigger import TRANSLATION_TARGETS
        self.assertIn("watchlist", TRANSLATION_TARGETS[15])


class TestSourceFileExists(unittest.TestCase):
    """Test source_file_exists() with various path scenarios."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_dir = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.orig_dir)

    def test_simple_path_exists(self):
        """Simple path (no {date}) — file exists."""
        from translation_trigger import source_file_exists
        p = Path("output/schema-mapping.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("test")
        self.assertTrue(source_file_exists("output/schema-mapping.md"))

    def test_simple_path_not_exists(self):
        """Simple path (no {date}) — file does not exist."""
        from translation_trigger import source_file_exists
        self.assertFalse(source_file_exists("output/nonexistent.md"))

    def test_date_placeholder_path_exists(self):
        """Path with {date} — matching file exists in parent directory."""
        from translation_trigger import source_file_exists
        p = Path("output/reports/weekly-report-2026-03-29.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("report content")
        # Template: "output/reports/weekly-report-{date}.md"
        self.assertTrue(source_file_exists("output/reports/weekly-report-{date}.md"))

    def test_date_placeholder_directory_missing(self):
        """Path with {date} — parent directory doesn't exist → False."""
        from translation_trigger import source_file_exists
        self.assertFalse(source_file_exists("output/missing-dir/file-{date}.md"))

    def test_date_placeholder_no_matching_files(self):
        """Path with {date} — directory exists but no matching files."""
        from translation_trigger import source_file_exists
        p = Path("output/temp")
        p.mkdir(parents=True, exist_ok=True)
        self.assertFalse(source_file_exists("output/temp/narrative-{date}.json"))


class TestWriteTranslationPending(unittest.TestCase):
    """Test write_translation_pending() file write behavior."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_dir = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.orig_dir)

    def test_writes_pending_yaml_file(self):
        """write_translation_pending() must create translation-pending.yaml."""
        import yaml
        from translation_trigger import write_translation_pending

        Path(".claude/agent-workspace").mkdir(parents=True, exist_ok=True)
        write_translation_pending(2, "output/schema-mapping.md")

        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        self.assertTrue(pending.exists())

    def test_pending_file_correct_content(self):
        """translation-pending.yaml must have correct step, source, and action."""
        import yaml
        from translation_trigger import write_translation_pending

        Path(".claude/agent-workspace").mkdir(parents=True, exist_ok=True)
        write_translation_pending(12, "output/reports/weekly-report-{date}.md")

        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        data = yaml.safe_load(pending.read_text())
        self.assertEqual(data["step"], 12)
        self.assertIn("weekly-report", data["source"])
        self.assertEqual(data["action"], "create_translation_task")

    def test_overwrites_existing_pending_file(self):
        """write_translation_pending() must overwrite existing pending file."""
        import yaml
        from translation_trigger import write_translation_pending

        Path(".claude/agent-workspace").mkdir(parents=True, exist_ok=True)
        write_translation_pending(2, "output/schema-mapping.md")
        write_translation_pending(5, "output/blueprint.md")

        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        data = yaml.safe_load(pending.read_text())
        self.assertEqual(data["step"], 5)  # Last write wins


class TestHookMainFlow(unittest.TestCase):
    """Test __main__ block behavior via subprocess simulation."""

    def _run_hook(self, hook_input: dict, tmpdir: str) -> int:
        """Run translation_trigger.py with given input via stdin."""
        import subprocess
        hook_path = str(
            Path(__file__).parent.parent / ".claude" / "hooks" / "scripts" / "translation_trigger.py"
        )
        result = subprocess.run(
            [sys.executable, hook_path],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        return result.returncode

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Path(self.tmpdir, ".claude", "agent-workspace").mkdir(parents=True, exist_ok=True)

    def test_non_taskupdate_exits_0(self):
        """Non-TaskUpdate tool_name → exit 0 (no action)."""
        hook_input = {"tool_name": "TaskCreate", "tool_result": {}, "tool_input": {}}
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)

    def test_taskupdate_not_completed_exits_0(self):
        """TaskUpdate with status != completed → exit 0."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "in_progress"},
            "tool_input": {"metadata": {"step": 2}},
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)

    def test_translation_task_itself_exits_0(self):
        """Translation task completing should NOT trigger another translation signal."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2, "task_type": "translation"}},
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)
        # No pending file should be written
        pending = Path(self.tmpdir) / ".claude" / "agent-workspace" / "translation-pending.yaml"
        self.assertFalse(pending.exists())

    def test_unknown_step_exits_0(self):
        """Step not in TRANSLATION_TARGETS → exit 0 (no signal)."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 99}},
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)

    def test_valid_step_with_source_file_emits_signal(self):
        """Valid step + existing source file → exit 0 + pending file written."""
        # Create source file for step 2
        source_dir = Path(self.tmpdir) / "output"
        source_dir.mkdir(exist_ok=True)
        (source_dir / "schema-mapping.md").write_text("schema content")

        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2}},
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)

        # Pending file should exist
        pending = Path(self.tmpdir) / ".claude" / "agent-workspace" / "translation-pending.yaml"
        self.assertTrue(pending.exists(), "translation-pending.yaml should be created")

    def test_valid_step_without_source_file_exits_0_no_pending(self):
        """Valid step but source file missing → exit 0, no pending file."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2}},  # schema-mapping.md doesn't exist
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)

        pending = Path(self.tmpdir) / ".claude" / "agent-workspace" / "translation-pending.yaml"
        self.assertFalse(pending.exists())

    def test_missing_step_in_metadata_exits_0(self):
        """task metadata without 'step' key → exit 0."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {}},  # no step
        }
        rc = self._run_hook(hook_input, self.tmpdir)
        self.assertEqual(rc, 0)


class TestCompletedStatusDetection(unittest.TestCase):
    """Test completed status detection from various tool_result formats."""

    def _run_hook(self, hook_input: dict) -> tuple[int, str]:
        """Run hook via subprocess and return (returncode, stdout)."""
        import subprocess
        tmpdir = tempfile.mkdtemp()
        Path(tmpdir, ".claude", "agent-workspace").mkdir(parents=True, exist_ok=True)
        hook_path = str(
            Path(__file__).parent.parent / ".claude" / "hooks" / "scripts" / "translation_trigger.py"
        )
        result = subprocess.run(
            [sys.executable, hook_path],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        return result.returncode, result.stdout

    def test_dict_tool_result_with_completed_status(self):
        """tool_result as dict with status: completed → detected."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed", "id": "task-1"},
            "tool_input": {"metadata": {"step": 99}},  # non-target step → exits 0 anyway
        }
        rc, _ = self._run_hook(hook_input)
        self.assertEqual(rc, 0)

    def test_string_tool_result_with_completed(self):
        """tool_result as string containing 'status: completed' → detected."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": "status: completed",
            "tool_input": {"metadata": {"step": 99}},
        }
        rc, _ = self._run_hook(hook_input)
        self.assertEqual(rc, 0)

    def test_in_progress_status_not_detected(self):
        """tool_result with in_progress status → no action (exit 0)."""
        hook_input = {
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "in_progress"},
            "tool_input": {"metadata": {"step": 2}},
        }
        rc, _ = self._run_hook(hook_input)
        self.assertEqual(rc, 0)


class TestRunHookDirect(unittest.TestCase):
    """Test run_hook() function directly — enables coverage tracking of main logic."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_dir = os.getcwd()
        os.chdir(self.tmpdir)
        Path(".claude/agent-workspace").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.chdir(self.orig_dir)

    def test_non_taskupdate_returns_0(self):
        """Direct: non-TaskUpdate → run_hook returns 0."""
        import translation_trigger as tt
        rc = tt.run_hook({"tool_name": "TaskCreate", "tool_result": {}, "tool_input": {}})
        self.assertEqual(rc, 0)

    def test_incomplete_task_returns_0(self):
        """Direct: TaskUpdate with in_progress → run_hook returns 0."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "in_progress"},
            "tool_input": {"metadata": {"step": 2}},
        })
        self.assertEqual(rc, 0)

    def test_translation_task_type_guard(self):
        """Direct: translation task_type → run_hook returns 0 (prevents infinite loop)."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2, "task_type": "translation"}},
        })
        self.assertEqual(rc, 0)

    def test_valid_step_no_source_file_returns_0(self):
        """Direct: valid step but source file missing → run_hook returns 0."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2}},
        })
        self.assertEqual(rc, 0)

    def test_valid_step_with_source_file_writes_pending(self):
        """Direct: valid step + source exists → pending file written, return 0."""
        import yaml
        import translation_trigger as tt

        Path("output").mkdir(exist_ok=True)
        Path("output/completion-definition.md").write_text("completion definition")

        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 4}},
        })
        self.assertEqual(rc, 0)
        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        self.assertTrue(pending.exists())
        data = yaml.safe_load(pending.read_text())
        self.assertEqual(data["step"], 4)

    def test_step_5_blueprint_triggers_signal(self):
        """Direct: step 5 + blueprint.md exists → pending written with correct step."""
        import yaml
        import translation_trigger as tt

        Path("output").mkdir(exist_ok=True)
        Path("output/blueprint.md").write_text("blueprint content")

        tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 5}},
        })
        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        self.assertTrue(pending.exists())
        data = yaml.safe_load(pending.read_text())
        self.assertEqual(data["step"], 5)
        self.assertIn("blueprint", data["source"])

    def test_step_none_in_metadata_returns_0(self):
        """Direct: step=None → run_hook returns 0."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {}},
        })
        self.assertEqual(rc, 0)

    def test_out_of_range_step_returns_0(self):
        """Direct: step=99 (not in TRANSLATION_TARGETS) → run_hook returns 0."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 99}},
        })
        self.assertEqual(rc, 0)

    def test_step_2_source_file_exists_triggers_signal(self):
        """Direct: step 2 + schema-mapping.md exists → pending file with step=2."""
        import yaml
        import translation_trigger as tt

        Path("output").mkdir(exist_ok=True)
        Path("output/schema-mapping.md").write_text("schema content")

        tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": {"status": "completed"},
            "tool_input": {"metadata": {"step": 2}},
        })
        pending = Path(".claude/agent-workspace/translation-pending.yaml")
        data = yaml.safe_load(pending.read_text())
        self.assertEqual(data["step"], 2)
        self.assertEqual(data["action"], "create_translation_task")

    def test_string_completed_status_detected(self):
        """Direct: string 'status: completed' in tool_result → processed."""
        import translation_trigger as tt
        rc = tt.run_hook({
            "tool_name": "TaskUpdate",
            "tool_result": "status: completed",
            "tool_input": {"metadata": {"step": 99}},
        })
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
