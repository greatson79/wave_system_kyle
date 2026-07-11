"""Contract tests for the read-only situation-room dashboard."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ADAPTER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER_DIR))

from situation_dashboard import build_world, dashboard_html, load_world  # noqa: E402


NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def snapshot(*, generated_at: datetime, next_due_at: datetime) -> dict:
    return {
        "generation_id": "generation-1",
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "tree_observed_at": generated_at.isoformat().replace("+00:00", "Z"),
        "panes": [
            {
                "workspace_ref": "workspace:1",
                "workspace_name": "경영본부",
                "surface_ref": "surface:4",
                "role": "CEO 관제타워",
                "state": "working",
                "observed_at": generated_at.isoformat().replace("+00:00", "Z"),
                "current_task": "canary 보고 교신 중",
                "current_task_basis": "cso_overlay",
                "current_task_observed_at": generated_at.isoformat().replace("+00:00", "Z"),
            },
            {
                "workspace_ref": "workspace:1",
                "workspace_name": "경영본부",
                "surface_ref": "surface:6",
                "role": "CSO",
                "state": "idle",
                "observed_at": generated_at.isoformat().replace("+00:00", "Z"),
                "current_task": None,
                "current_task_basis": "none",
                "current_task_observed_at": None,
            },
        ],
        "alerts_summary": [],
        "collector_meta": {
            "run_ok": True,
            "next_due_at": next_due_at.isoformat().replace("+00:00", "Z"),
        },
    }


class SituationDashboardTests(unittest.TestCase):
    def test_build_world_exposes_three_activity_states_and_coverage(self) -> None:
        world = build_world(snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30)), now=NOW)

        department = world["departments"][0]
        self.assertEqual(department["name"], "경영본부")
        self.assertEqual(department["snapshot_coverage"], {"recorded": 2, "total": 2})
        self.assertEqual(department["workers"][0]["activity"], "working")
        self.assertEqual(department["workers"][0]["activity_label"], "가동중")
        self.assertEqual(department["workers"][0]["current_task"], "canary 보고 교신 중")
        self.assertEqual(department["workers"][1]["activity"], "idle")
        self.assertEqual(department["workers"][1]["activity_label"], "대기")

    def test_stale_snapshot_downgrades_working_and_idle_to_unknown(self) -> None:
        old = NOW - timedelta(minutes=10)
        world = build_world(snapshot(generated_at=old, next_due_at=old + timedelta(seconds=30)), now=NOW)

        self.assertTrue(world["snapshot_stale"])
        self.assertEqual([row["activity"] for row in world["departments"][0]["workers"]], ["unknown", "unknown"])
        self.assertEqual(world["departments"][0]["workers"][0]["basis"], "snapshot_stale")

    def test_unmapped_surface_is_visible_as_unassigned_not_dropped(self) -> None:
        payload = snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30))
        payload["panes"].append(
            {
                "workspace_ref": "workspace:1",
                "workspace_name": "경영본부",
                "surface_ref": "surface:99",
                "role": None,
                "state": "idle",
                "observed_at": NOW.isoformat().replace("+00:00", "Z"),
                "current_task": None,
                "current_task_basis": "none",
                "current_task_observed_at": None,
            }
        )

        world = build_world(payload, now=NOW)

        workers = world["departments"][0]["workers"]
        self.assertEqual(len(workers), 3)
        self.assertEqual(workers[-1]["surface_ref"], "surface:99")
        self.assertEqual(workers[-1]["role"], "미배정 surface")

    def test_load_world_fails_closed_to_format_error_for_invalid_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "SweepSnapshot.json"
            path.write_text("{ invalid", encoding="utf-8")

            world = load_world(path, now=NOW)

        self.assertEqual(world["state"], "snapshot_error")
        self.assertTrue(world["snapshot_stale"])


class DashboardV2Tests(unittest.TestCase):
    def test_system_status_is_passed_through_from_the_snapshot(self) -> None:
        payload = snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30))
        payload["system_status"] = {
            "system_resources": {
                "mem_free_mb": 1000,
                "load_1m": 22.48,
                "load_5m": 23.89,
                "load_15m": 39.83,
                "ollama_loaded_models": ["gemma3:12b"],
            },
            "claude_usage": {"approx_pct": None, "basis": "unavailable", "gate_percent": 92, "note": "n"},
            "gemma_triage": {"staged_count": 3, "last_run_at": "2026-07-11T00:00:00Z", "last_run_ok": True},
        }

        world = build_world(payload, now=NOW)

        self.assertEqual(world["system_status"], payload["system_status"])

    def test_missing_system_status_fails_closed_to_honest_nulls(self) -> None:
        world = build_world(snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30)), now=NOW)

        status = world["system_status"]
        self.assertIsNone(status["system_resources"]["mem_free_mb"])
        self.assertIsNone(status["claude_usage"]["approx_pct"])
        self.assertEqual(status["claude_usage"]["basis"], "unavailable")
        self.assertIsNone(status["gemma_triage"]["staged_count"])

    def test_worker_rows_carry_drilldown_and_engine_badge_fields(self) -> None:
        payload = snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30))
        payload["panes"][0].update(
            {
                "owner_pid": 4321,
                "owner_pgid": 4321,
                "last_io_at": NOW.isoformat().replace("+00:00", "Z"),
                "todo_latest_item": "다음 미완 항목",
                "todo_latest_item_observed_at": NOW.isoformat().replace("+00:00", "Z"),
                "alert_history": [{"condition": "context.threshold", "observed_at": "2026-07-11T00:00:00Z"}],
                "engine_model": "claude-sonnet-5",
                "engine_model_basis": "roster_static",
            }
        )

        world = build_world(payload, now=NOW)

        worker = world["departments"][0]["workers"][0]
        self.assertEqual(worker["owner_pid"], 4321)
        self.assertEqual(worker["owner_pgid"], 4321)
        self.assertEqual(worker["todo_latest_item"], "다음 미완 항목")
        self.assertEqual(worker["alert_history"][0]["condition"], "context.threshold")
        self.assertEqual(worker["engine_model"], "claude-sonnet-5")
        self.assertEqual(worker["engine_model_basis"], "roster_static")

    def test_worker_rows_default_v2_fields_when_snapshot_is_v1(self) -> None:
        world = build_world(snapshot(generated_at=NOW, next_due_at=NOW + timedelta(seconds=30)), now=NOW)

        worker = world["departments"][0]["workers"][0]
        self.assertIsNone(worker["engine_model"])
        self.assertEqual(worker["engine_model_basis"], "unknown")
        self.assertEqual(worker["alert_history"], [])
        self.assertIsNone(worker["todo_latest_item"])

    def test_dashboard_html_always_shows_unreviewed_preview_banner_statically(self) -> None:
        html = dashboard_html()

        self.assertIn("미검수 프리뷰", html)
        self.assertIn("codex 코드검수 전", html)
        # 정적 마크업이어야 한다 — stale 배너처럼 JS 렌더에 의존하면 fetch 실패 시 사라진다.
        static_part = html.split("<script>")[0]
        self.assertIn('class="preview-banner"', static_part)
        self.assertIn("미검수 프리뷰", static_part)

    def test_dashboard_html_ships_strip_drilldown_and_badge_hooks(self) -> None:
        html = dashboard_html()

        self.assertIn('id="strip"', html)
        self.assertIn("system_status", html)
        self.assertIn("drilldown", html)
        self.assertIn("engine_model", html)


if __name__ == "__main__":
    unittest.main()
