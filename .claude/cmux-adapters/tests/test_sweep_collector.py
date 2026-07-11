"""Contract tests for the one-shot cmux sweep collector."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ADAPTER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER_DIR))

from sweep_collector import (  # noqa: E402
    CollectorBusyError,
    CollectorPaths,
    DEFAULT_THRESHOLDS,
    collect_once,
    is_tick_due,
    should_defer_tick,
    resolve_cmux_bin,
    run_tick,
    tick_lock,
)


TREE = {
    "windows": [
        {
            "workspaces": [
                {
                    "ref": "workspace:4",
                    "title": "개발본부",
                    "panes": [
                        {
                            "surfaces": [
                                {
                                    "ref": "surface:9",
                                    "title": "✳ 수집기 구현",
                                    "tty": "ttys009",
                                    "type": "terminal",
                                }
                            ]
                        }
                    ],
                }
            ]
        }
    ]
}

VM_STAT = (
    "Mach Virtual Memory Statistics: (page size of 16384 bytes)\n"
    "Pages free:                               64000.\n"
    "Pages active:                            100000.\n"
)
UPTIME = "12:00  up 5 days,  3:21, 2 users, load averages: 22.48 23.89 39.83\n"
OLLAMA_PS = json.dumps({"models": [{"name": "gemma3:12b"}]})


def make_run_command(
    tree: dict,
    *,
    screen: str = "idle prompt\n",
    vm_stat: str = VM_STAT,
    uptime: str = UPTIME,
    ollama: str = OLLAMA_PS,
    probe_error: bool = False,
):
    def run_command(argv: list[str]) -> str:
        if argv[1:4] == ["tree", "--all", "--json"]:
            return json.dumps(tree)
        if argv[1:2] == ["read-screen"]:
            return screen
        if argv[0] == "ps":
            return "4321 4321\n"
        if argv[0] == "pgrep":
            return ""
        if argv[0] in ("vm_stat", "uptime", "curl"):
            if probe_error:
                raise RuntimeError(f"probe failed: {argv[0]}")
            return {"vm_stat": vm_stat, "uptime": uptime, "curl": ollama}[argv[0]]
        raise AssertionError(f"unexpected command: {argv}")

    return run_command


class SweepCollectorTests(unittest.TestCase):
    def test_due_early_tolerance_is_a_configurable_five_second_guard(self) -> None:
        self.assertEqual(DEFAULT_THRESHOLDS["due_early_tolerance_seconds"], 5)

    def test_resolve_cmux_bin_uses_explicit_environment_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            binary = Path(temp_dir) / "cmux"
            binary.touch()
            binary.chmod(0o755)

            resolved = resolve_cmux_bin({"CMUX_BIN": str(binary)})

        self.assertEqual(resolved, str(binary))

    def test_run_tick_skips_before_next_due_without_calling_cmux(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = CollectorPaths.for_root(Path(temp_dir))
            paths.state_path.parent.mkdir(parents=True)
            paths.state_path.write_text(
                json.dumps({"sequence": 7, "panes": {}, "next_due_at": "2026-07-10T12:01:00Z"}),
                encoding="utf-8",
            )

            result = run_tick(
                paths,
                run_command=lambda argv: (_ for _ in ()).throw(AssertionError(argv)),
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
                cmux_bin="/unused/cmux",
            )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["next_due_at"], "2026-07-10T12:01:00Z")

    def test_run_tick_refuses_a_second_concurrent_tick(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = CollectorPaths.for_root(Path(temp_dir))
            with tick_lock(paths):
                with self.assertRaises(CollectorBusyError):
                    run_tick(
                        paths,
                        run_command=lambda argv: (_ for _ in ()).throw(AssertionError(argv)),
                        now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
                        cmux_bin="/unused/cmux",
                    )

    def test_tick_is_due_within_explicit_early_tolerance(self) -> None:
        due_at = datetime(2026, 7, 10, 12, 1, tzinfo=timezone.utc)

        self.assertTrue(
            is_tick_due(
                due_at,
                now=datetime(2026, 7, 10, 12, 0, 59, tzinfo=timezone.utc),
                early_tolerance_seconds=2,
            )
        )

    def test_working_pane_never_defers_a_launchd_tick(self) -> None:
        state = {"panes": {"workspace:1/surface:4": {"state": "working"}}}
        next_due_at = datetime(2026, 7, 10, 12, 5, tzinfo=timezone.utc)

        self.assertFalse(
            should_defer_tick(
                state,
                next_due_at=next_due_at,
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
                early_tolerance_seconds=5,
            )
        )

    def test_collect_once_writes_atomic_snapshot_with_ref_role_and_task_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(
                json.dumps({"AI-Tech 본부장": "surface:9"}), encoding="utf-8"
            )
            paths.thresholds_path.write_text(
                json.dumps(
                    {
                        "screen_unchanged_seconds": 300,
                        "context_threshold_percent": 60,
                        "proc_count_high": 20,
                        "working_interval_seconds": 30,
                        "idle_interval_seconds": 300,
                    }
                ),
                encoding="utf-8",
            )

            def run_command(argv: list[str]) -> str:
                if argv[1:4] == ["tree", "--all", "--json"]:
                    return json.dumps(TREE)
                if argv[1:2] == ["read-screen"]:
                    return "secret screen text\nCtx 61%\n"
                if argv[0] == "ps":
                    return "4321 4321\n"
                if argv[0] == "pgrep":
                    return "4322\n"
                if argv[0] == "uptime":
                    return "load averages: 0.10 0.20 0.30\n"
                if argv[0] == "vm_stat":
                    return VM_STAT
                if argv[0] == "curl":
                    return OLLAMA_PS
                raise AssertionError(f"unexpected command: {argv}")

            snapshot = collect_once(
                paths,
                run_command=run_command,
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
            )

            saved = json.loads(paths.snapshot_path.read_text(encoding="utf-8"))
            self.assertEqual(snapshot, saved)
            self.assertTrue(saved["generation_id"].startswith("20260710T120000Z-"))
            self.assertEqual(saved["panes"][0]["workspace_ref"], "workspace:4")
            self.assertEqual(saved["panes"][0]["workspace_name"], "개발본부")
            self.assertEqual(saved["panes"][0]["surface_ref"], "surface:9")
            self.assertEqual(saved["panes"][0]["role"], "AI-Tech 본부장")
            self.assertEqual(saved["panes"][0]["current_task"], "✳ 수집기 구현")
            self.assertEqual(saved["panes"][0]["current_task_basis"], "pane_title")
            self.assertEqual(saved["panes"][0]["owner_pid"], 4321)
            self.assertEqual(saved["panes"][0]["owner_pgid"], 4321)
            self.assertIn("context.threshold", saved["panes"][0]["alerts"])
            self.assertNotIn("secret screen text", json.dumps(saved, ensure_ascii=False))

    def test_collect_once_uses_overlay_task_when_title_is_the_fixed_role(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(json.dumps({"CSO": "surface:9"}), encoding="utf-8")
            paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
            paths.overlay_path.parent.mkdir(parents=True, exist_ok=True)
            paths.overlay_path.write_text(
                json.dumps(
                    {
                        "panes": {
                            "workspace:4/surface:9": {
                                "current_task": "CSO 수기 작업",
                                "observed_at": "2026-07-10T11:59:00Z",
                                "next_expected_event": "12:30 보고",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            tree = json.loads(json.dumps(TREE))
            tree["windows"][0]["workspaces"][0]["panes"][0]["surfaces"][0]["title"] = "CSO"

            def run_command(argv: list[str]) -> str:
                if argv[1:4] == ["tree", "--all", "--json"]:
                    return json.dumps(tree)
                if argv[1:2] == ["read-screen"]:
                    return "idle prompt\n"
                if argv[0] == "ps":
                    return "99 99\n"
                if argv[0] == "pgrep":
                    return ""
                if argv[0] == "uptime":
                    return "load averages: 0.10 0.20 0.30\n"
                if argv[0] == "vm_stat":
                    return VM_STAT
                if argv[0] == "curl":
                    return OLLAMA_PS
                raise AssertionError(f"unexpected command: {argv}")

            snapshot = collect_once(
                paths,
                run_command=run_command,
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["current_task"], "CSO 수기 작업")
            self.assertEqual(pane["current_task_basis"], "cso_overlay")
            self.assertEqual(pane["next_expected_event"], "12:30 보고")

    def test_collect_once_uses_only_explicit_todo_fallback_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(json.dumps({"CSO": "surface:9"}), encoding="utf-8")
            paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
            todo_path = root / "CSO_TODO.md"
            todo_path.write_text("- [x] previous\n- [ ] explicit next action\n", encoding="utf-8")
            paths.todo_map_path.write_text(json.dumps({"CSO": str(todo_path)}), encoding="utf-8")
            tree = json.loads(json.dumps(TREE))
            tree["windows"][0]["workspaces"][0]["panes"][0]["surfaces"][0]["title"] = "CSO"

            def run_command(argv: list[str]) -> str:
                if argv[1:4] == ["tree", "--all", "--json"]:
                    return json.dumps(tree)
                if argv[1:2] == ["read-screen"]:
                    return "idle prompt\n"
                if argv[0] == "ps":
                    return "99 99\n"
                if argv[0] == "pgrep":
                    return ""
                if argv[0] == "uptime":
                    return "load averages: 0.10 0.20 0.30\n"
                if argv[0] == "vm_stat":
                    return VM_STAT
                if argv[0] == "curl":
                    return OLLAMA_PS
                raise AssertionError(f"unexpected command: {argv}")

            snapshot = collect_once(
                paths,
                run_command=run_command,
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["current_task"], "explicit next action")
            self.assertEqual(pane["current_task_basis"], "todo_fallback")

    def test_collect_once_does_not_guess_a_todo_file_without_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(json.dumps({"CSO": "surface:9"}), encoding="utf-8")
            paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
            (root / "CSO_TODO.md").write_text("- [ ] must not be discovered\n", encoding="utf-8")
            tree = json.loads(json.dumps(TREE))
            tree["windows"][0]["workspaces"][0]["panes"][0]["surfaces"][0]["title"] = "CSO"

            def run_command(argv: list[str]) -> str:
                if argv[1:4] == ["tree", "--all", "--json"]:
                    return json.dumps(tree)
                if argv[1:2] == ["read-screen"]:
                    return "idle prompt\n"
                if argv[0] == "ps":
                    return "99 99\n"
                if argv[0] == "pgrep":
                    return ""
                if argv[0] == "uptime":
                    return "load averages: 0.10 0.20 0.30\n"
                if argv[0] == "vm_stat":
                    return VM_STAT
                if argv[0] == "curl":
                    return OLLAMA_PS
                raise AssertionError(f"unexpected command: {argv}")

            snapshot = collect_once(
                paths,
                run_command=run_command,
                now=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
            )

            pane = snapshot["panes"][0]
            self.assertIsNone(pane["current_task"])
            self.assertEqual(pane["current_task_basis"], "none")


class SystemStatusTests(unittest.TestCase):
    """v2 [A]: generation-level system_status collected only by the collector."""

    def _make_paths(self, root: Path) -> CollectorPaths:
        paths = CollectorPaths.for_root(root)
        paths.roster_path.parent.mkdir(parents=True)
        paths.roster_path.write_text(json.dumps({"AI-Tech 본부장": "surface:9"}), encoding="utf-8")
        paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
        return paths

    def test_system_status_records_local_probes_and_gemma_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self._make_paths(root)
            gemma_dir = root / "wave-gemma-triage"
            for sub, count in (("sources", 2), ("entities", 1), ("concepts", 0)):
                (gemma_dir / "staging" / sub).mkdir(parents=True)
                for index in range(count):
                    (gemma_dir / "staging" / sub / f"item{index}.md").write_text("x", encoding="utf-8")
            (gemma_dir / "heartbeat.json").write_text(
                json.dumps({"last_run": "2026-07-11T00:00:00Z", "exit_code": 0}), encoding="utf-8"
            )

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=gemma_dir,
            )

            status = snapshot["system_status"]
            self.assertEqual(status["system_resources"]["mem_free_mb"], 64000 * 16384 // (1024 * 1024))
            self.assertEqual(status["system_resources"]["load_1m"], 22.48)
            self.assertEqual(status["system_resources"]["load_5m"], 23.89)
            self.assertEqual(status["system_resources"]["load_15m"], 39.83)
            self.assertEqual(status["system_resources"]["ollama_loaded_models"], ["gemma3:12b"])
            self.assertEqual(status["gemma_triage"]["staged_count"], 3)
            self.assertEqual(status["gemma_triage"]["last_run_at"], "2026-07-11T00:00:00Z")
            self.assertTrue(status["gemma_triage"]["last_run_ok"])

    def test_claude_usage_starts_honest_unavailable_never_fake_precision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir))

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            usage = snapshot["system_status"]["claude_usage"]
            self.assertIsNone(usage["approx_pct"])
            self.assertEqual(usage["basis"], "unavailable")
            self.assertEqual(usage["gate_percent"], 92)

    def test_system_status_fails_closed_to_nulls_when_probes_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir))

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, probe_error=True),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            resources = snapshot["system_status"]["system_resources"]
            self.assertIsNone(resources["mem_free_mb"])
            self.assertIsNone(resources["load_1m"])
            self.assertIsNone(resources["ollama_loaded_models"])
            triage = snapshot["system_status"]["gemma_triage"]
            self.assertIsNone(triage["staged_count"])
            self.assertIsNone(triage["last_run_at"])
            self.assertIsNone(triage["last_run_ok"])
            self.assertTrue(snapshot["collector_meta"]["run_ok"])


class DrilldownFieldTests(unittest.TestCase):
    """v2 [B]: alert history ring buffer and always-on TODO side channel."""

    def test_alert_history_appends_with_timestamp_and_caps_at_ten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(json.dumps({"AI-Tech 본부장": "surface:9"}), encoding="utf-8")
            paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
            old_events = [
                {"condition": f"old.alert.{index}", "observed_at": "2026-07-11T00:00:00Z"}
                for index in range(10)
            ]
            paths.state_path.parent.mkdir(parents=True, exist_ok=True)
            paths.state_path.write_text(
                json.dumps(
                    {
                        "sequence": 3,
                        "panes": {
                            "workspace:4/surface:9": {
                                "screen_hash": "stale",
                                "last_io_at": "2026-07-11T00:00:00Z",
                                "state": "working",
                                "alert_history": old_events,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, screen="busy\nCtx 61%\n"),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=root / "missing-gemma",
            )

            history = snapshot["panes"][0]["alert_history"]
            self.assertEqual(len(history), 10)
            self.assertEqual(history[-1]["condition"], "context.threshold")
            self.assertEqual(history[-1]["observed_at"], "2026-07-11T01:00:00Z")
            self.assertNotIn("old.alert.0", [event["condition"] for event in history])
            persisted = json.loads(paths.state_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["panes"]["workspace:4/surface:9"]["alert_history"], history)

    def test_todo_latest_item_is_kept_even_when_basis_is_pane_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = CollectorPaths.for_root(root)
            paths.roster_path.parent.mkdir(parents=True)
            paths.roster_path.write_text(json.dumps({"AI-Tech 본부장": "surface:9"}), encoding="utf-8")
            paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
            todo_path = root / "AITECH_TODO.md"
            todo_path.write_text("- [x] done\n- [ ] drilldown TODO item\n", encoding="utf-8")
            paths.todo_map_path.write_text(json.dumps({"AI-Tech 본부장": str(todo_path)}), encoding="utf-8")

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=root / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["current_task_basis"], "pane_title")
            self.assertEqual(pane["todo_latest_item"], "drilldown TODO item")
            self.assertIsNotNone(pane["todo_latest_item_observed_at"])


class EngineModelTests(unittest.TestCase):
    """v2 [C]: engine badge — roster static wins, then status-line parse, else unknown."""

    def _make_paths(self, root: Path, roster: dict) -> CollectorPaths:
        paths = CollectorPaths.for_root(root)
        paths.roster_path.parent.mkdir(parents=True)
        paths.roster_path.write_text(json.dumps(roster, ensure_ascii=False), encoding="utf-8")
        paths.thresholds_path.write_text(json.dumps({}), encoding="utf-8")
        return paths

    def test_extended_roster_entry_resolves_role_and_static_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(
                Path(temp_dir),
                {"AI-Tech 본부장": {"surface": "surface:9", "engine": "claude-sonnet-5"}},
            )

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["role"], "AI-Tech 본부장")
            self.assertEqual(pane["engine_model"], "claude-sonnet-5")
            self.assertEqual(pane["engine_model_basis"], "roster_static")

    def test_status_line_parse_extracts_badge_without_storing_screen(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir), {"AI-Tech 본부장": "surface:9"})
            screen = "secret raw screen line\nModel: claude-opus-4-8 · Ctx 12%\n"

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, screen=screen),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["engine_model"], "claude-opus-4-8")
            self.assertEqual(pane["engine_model_basis"], "status_line_parse")
            self.assertNotIn("secret raw screen line", json.dumps(snapshot, ensure_ascii=False))
            # C-ENGINE-1: 캐시 폴백 금지 — 파싱 결과를 state에 이월 저장하지 않는다.
            persisted = json.loads(paths.state_path.read_text(encoding="utf-8"))
            self.assertNotIn("engine_model", persisted["panes"]["workspace:4/surface:9"])

    def test_codex_status_line_pattern_is_recognized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir), {"Ai_works(codex 워커)": "surface:9"})

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, screen="workdir ~/x\nmodel gpt-5.6-terra\n"),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertEqual(pane["engine_model"], "gpt-5.6-terra")
            self.assertEqual(pane["engine_model_basis"], "status_line_parse")

    def test_gpt_token_in_conversation_body_is_not_misattributed_as_engine(self) -> None:
        """C-ENGINE-1 회귀: 모델표기는 마지막 상태줄 영역에서만 인정 — 대화 본문 언급은 무시."""
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir), {"COO": "surface:9"})
            screen = (
                "[COO->CEO] 이번 코드검수는 gpt-5.6-terra 워커에게 맡겼다\n"
                "Model: claude-opus-4-8 언급도 본문에 있으면 무시해야 한다\n"
                + "본문 스크롤백 줄\n" * 10
                + "plain idle prompt\n"
            )

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, screen=screen),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertIsNone(pane["engine_model"])
            self.assertEqual(pane["engine_model_basis"], "unknown")

    def test_engine_model_stays_unknown_when_screen_is_not_captured_this_tick(self) -> None:
        """C-ENGINE-1: 미관측 tick에서 이전 파싱값 재사용 금지 — null/unknown으로 떨어뜨린다."""
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir), {"AI-Tech 본부장": "surface:9"})
            paths.state_path.parent.mkdir(parents=True, exist_ok=True)
            paths.state_path.write_text(
                json.dumps(
                    {
                        "sequence": 5,
                        "panes": {
                            "workspace:4/surface:9": {
                                "screen_hash": "unchanged",
                                "last_io_at": "2026-07-11T00:00:00Z",
                                "state": "idle",
                                "engine_model": "gpt-5.6-terra",
                                "engine_model_basis": "status_line_parse",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            tree = json.loads(json.dumps(TREE))
            tree["windows"][0]["workspaces"][0]["panes"][0]["surfaces"][0]["title"] = "AI-Tech 본부장"

            def run_command(argv: list[str]) -> str:
                if argv[1:2] == ["read-screen"]:
                    raise AssertionError("idle pane must not trigger read-screen")
                return make_run_command(tree)(argv)

            snapshot = collect_once(
                paths,
                run_command=run_command,
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertIsNone(pane["engine_model"])
            self.assertEqual(pane["engine_model_basis"], "unknown")

    def test_engine_model_is_null_unknown_when_no_source_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._make_paths(Path(temp_dir), {"AI-Tech 본부장": "surface:9"})

            snapshot = collect_once(
                paths,
                run_command=make_run_command(TREE, screen="plain shell prompt\n"),
                now=datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc),
                gemma_dir=Path(temp_dir) / "missing-gemma",
            )

            pane = snapshot["panes"][0]
            self.assertIsNone(pane["engine_model"])
            self.assertEqual(pane["engine_model_basis"], "unknown")


if __name__ == "__main__":
    unittest.main()
