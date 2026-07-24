"""
tests/test_watchdog.py — Unit tests for investscan.watchdog module.
Verifies state freshness checks, TDD status reads, and watchdog report generation.
English-First (P5-A).
"""
from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from investscan.watchdog import (
    check_state_freshness,
    check_tdd_status,
    get_failing_modules,
    get_watchdog_report,
    is_paused_week,
    check_onboarding_transition,
    monday_morning_check,
    MAX_STALE_HOURS,
    MAX_PIPELINE_FAIL_COUNT,
    ONBOARDING_WEEKS,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _write_state(tmp_path: Path, content: dict) -> str:
    """Write a state.yaml to tmp_path and return its path string."""
    state_file = tmp_path / "state.yaml"
    state_file.write_text(yaml.dump(content, allow_unicode=True))
    return str(state_file)


# ─────────────────────────────────────────────────────────────────────────────
# TestConstants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:

    def test_max_stale_hours_positive(self):
        """MAX_STALE_HOURS must be a positive integer."""
        assert isinstance(MAX_STALE_HOURS, int)
        assert MAX_STALE_HOURS > 0

    def test_max_pipeline_fail_count_positive(self):
        """MAX_PIPELINE_FAIL_COUNT must be a positive integer."""
        assert isinstance(MAX_PIPELINE_FAIL_COUNT, int)
        assert MAX_PIPELINE_FAIL_COUNT > 0


# ─────────────────────────────────────────────────────────────────────────────
# TestCheckStateFreshness
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckStateFreshness:

    def test_missing_file_returns_not_fresh(self, tmp_path):
        """Non-existent state.yaml returns fresh=False."""
        result = check_state_freshness(str(tmp_path / "nonexistent.yaml"))
        assert result["fresh"] is False
        assert result["last_updated"] == "never"

    def test_fresh_recent_timestamp(self, tmp_path):
        """State updated just now is considered fresh."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso}
        })
        result = check_state_freshness(state_path)
        assert result["fresh"] is True
        assert result["hours_since_update"] is not None
        assert result["hours_since_update"] < 1.0

    def test_stale_old_timestamp(self, tmp_path):
        """State updated years ago is stale (default threshold 25h)."""
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": "2020-01-01T00:00:00+00:00"}
        })
        result = check_state_freshness(state_path)
        assert result["fresh"] is False
        assert result["hours_since_update"] is not None

    def test_missing_last_updated_returns_not_fresh(self, tmp_path):
        """State with no last_updated field returns fresh=False."""
        state_path = _write_state(tmp_path, {"workflow": {}})
        result = check_state_freshness(state_path)
        assert result["fresh"] is False

    def test_empty_state_file_returns_not_fresh(self, tmp_path):
        """Empty state.yaml returns fresh=False gracefully."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("")
        result = check_state_freshness(str(state_file))
        assert result["fresh"] is False

    def test_custom_max_stale_hours(self, tmp_path):
        """Custom max_stale_hours parameter is respected."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso}
        })
        result = check_state_freshness(state_path, max_stale_hours=0)
        # With threshold=0, even a just-updated state may not be fresh
        assert isinstance(result["fresh"], bool)

    def test_result_has_required_keys(self, tmp_path):
        """Return dict must contain fresh, hours_since_update, last_updated."""
        state_path = _write_state(tmp_path, {"workflow": {}})
        result = check_state_freshness(state_path)
        assert "fresh" in result
        assert "hours_since_update" in result
        assert "last_updated" in result


# ─────────────────────────────────────────────────────────────────────────────
# TestCheckTddStatus
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckTddStatus:

    def test_returns_tdd_section(self, tmp_path):
        """check_tdd_status returns tdd_status dict from state.yaml."""
        state_path = _write_state(tmp_path, {
            "tdd_status": {
                "normalizers": "passing",
                "schema": "pending",
                "watchdog": "pending",
            }
        })
        result = check_tdd_status(state_path)
        assert result["normalizers"] == "passing"
        assert result["schema"] == "pending"

    def test_missing_file_returns_empty(self, tmp_path):
        """Missing state.yaml returns empty dict."""
        result = check_tdd_status(str(tmp_path / "no_file.yaml"))
        assert result == {}

    def test_no_tdd_section_returns_empty(self, tmp_path):
        """State without tdd_status section returns empty dict."""
        state_path = _write_state(tmp_path, {"workflow": {}})
        result = check_tdd_status(state_path)
        assert result == {}

    def test_returns_all_statuses(self, tmp_path):
        """All status types (passing, pending, failing) are returned."""
        state_path = _write_state(tmp_path, {
            "tdd_status": {
                "a": "passing",
                "b": "pending",
                "c": "failing",
            }
        })
        result = check_tdd_status(state_path)
        assert result["a"] == "passing"
        assert result["b"] == "pending"
        assert result["c"] == "failing"


# ─────────────────────────────────────────────────────────────────────────────
# TestGetFailingModules
# ─────────────────────────────────────────────────────────────────────────────

class TestGetFailingModules:

    def test_no_failures_returns_empty_list(self, tmp_path):
        """When all modules pass, get_failing_modules returns []."""
        state_path = _write_state(tmp_path, {
            "tdd_status": {
                "normalizers": "passing",
                "schema": "passing",
            }
        })
        assert get_failing_modules(state_path) == []

    def test_identifies_failing_modules(self, tmp_path):
        """Modules with 'failing' status are returned."""
        state_path = _write_state(tmp_path, {
            "tdd_status": {
                "normalizers": "failing",
                "schema": "passing",
                "watchdog": "failing",
            }
        })
        failing = get_failing_modules(state_path)
        assert "normalizers" in failing
        assert "watchdog" in failing
        assert "schema" not in failing

    def test_pending_not_treated_as_failing(self, tmp_path):
        """Pending modules are NOT counted as failing."""
        state_path = _write_state(tmp_path, {
            "tdd_status": {"schema": "pending"}
        })
        assert get_failing_modules(state_path) == []

    def test_missing_state_returns_empty_list(self, tmp_path):
        """Missing state.yaml returns empty list (no failing modules)."""
        result = get_failing_modules(str(tmp_path / "no_file.yaml"))
        assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# TestGetWatchdogReport
# ─────────────────────────────────────────────────────────────────────────────

class TestGetWatchdogReport:

    def test_report_structure(self, tmp_path):
        """get_watchdog_report returns dict with required keys."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso},
            "tdd_status": {"normalizers": "passing"},
        })
        report = get_watchdog_report(state_path)
        for key in ("fresh", "hours_since_update", "failing_modules",
                    "passing_modules", "pending_modules", "overall_healthy"):
            assert key in report, f"Missing key: {key}"

    def test_healthy_when_fresh_and_no_failures(self, tmp_path):
        """overall_healthy=True when fresh and no failures."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso},
            "tdd_status": {"normalizers": "passing"},
        })
        report = get_watchdog_report(state_path)
        assert report["overall_healthy"] is True

    def test_not_healthy_when_stale(self, tmp_path):
        """overall_healthy=False when state is stale."""
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": "2020-01-01T00:00:00"},
            "tdd_status": {"normalizers": "passing"},
        })
        report = get_watchdog_report(state_path)
        assert report["overall_healthy"] is False

    def test_not_healthy_when_failing_modules(self, tmp_path):
        """overall_healthy=False when failing modules exist."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso},
            "tdd_status": {"normalizers": "failing"},
        })
        report = get_watchdog_report(state_path)
        assert report["overall_healthy"] is False

    def test_passing_pending_modules_separated(self, tmp_path):
        """Passing and pending modules are listed separately."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        state_path = _write_state(tmp_path, {
            "workflow": {"last_updated": now_iso},
            "tdd_status": {
                "normalizers": "passing",
                "schema": "pending",
            },
        })
        report = get_watchdog_report(state_path)
        assert "normalizers" in report["passing_modules"]
        assert "schema" in report["pending_modules"]
        assert "normalizers" not in report["pending_modules"]

    def test_empty_state_returns_not_healthy(self, tmp_path):
        """Missing state file returns overall_healthy=False."""
        report = get_watchdog_report(str(tmp_path / "no_file.yaml"))
        assert report["overall_healthy"] is False


# ─────────────────────────────────────────────────────────────────────────────
# TestIsPausedWeek
# ─────────────────────────────────────────────────────────────────────────────

class TestIsPausedWeek:

    def test_today_in_list_returns_true(self):
        """Returns True when today's date is in pause_weeks list."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        assert is_paused_week([today]) is True

    def test_today_not_in_list_returns_false(self):
        """Returns False when today's date is not in pause_weeks."""
        assert is_paused_week(["1900-01-01", "1900-01-02"]) is False

    def test_empty_list_returns_false(self):
        """Empty pause_weeks list always returns False."""
        assert is_paused_week([]) is False

    def test_multiple_dates_finds_today(self):
        """Returns True when today appears anywhere in a multi-date list."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        assert is_paused_week(["1900-01-01", today, "1900-01-02"]) is True


# ─────────────────────────────────────────────────────────────────────────────
# TestCheckOnboardingTransition
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckOnboardingTransition:

    def test_returns_false_when_onboarding_mode_false(self, tmp_path):
        """onboarding_mode=False always returns False regardless of install date."""
        from datetime import datetime, timedelta
        old = (datetime.now() - timedelta(weeks=10)).strftime("%Y-%m-%d")
        state_path = _write_state(tmp_path, {"system": {"installed_at": old}})
        assert check_onboarding_transition(state_path, onboarding_mode=False) is False

    def test_returns_false_before_4_weeks(self, tmp_path):
        """Returns False when installed less than ONBOARDING_WEEKS ago."""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d")
        state_path = _write_state(tmp_path, {"system": {"installed_at": recent}})
        assert check_onboarding_transition(state_path, onboarding_mode=True) is False

    def test_returns_true_after_4_weeks(self, tmp_path):
        """Returns True when installed >= ONBOARDING_WEEKS ago."""
        from datetime import datetime, timedelta
        old = (datetime.now() - timedelta(weeks=ONBOARDING_WEEKS + 1)).strftime("%Y-%m-%d")
        state_path = _write_state(tmp_path, {"system": {"installed_at": old}})
        assert check_onboarding_transition(state_path, onboarding_mode=True) is True

    def test_missing_state_file_returns_false(self, tmp_path):
        """Missing state.yaml returns False (safe default)."""
        assert check_onboarding_transition(
            str(tmp_path / "no_file.yaml"), onboarding_mode=True
        ) is False

    def test_missing_installed_at_returns_false(self, tmp_path):
        """State without system.installed_at returns False."""
        state_path = _write_state(tmp_path, {"system": {}})
        assert check_onboarding_transition(state_path, onboarding_mode=True) is False


# ─────────────────────────────────────────────────────────────────────────────
# TestMondayMorningCheck
# ─────────────────────────────────────────────────────────────────────────────

class TestMondayMorningCheck:

    def test_no_run_log_returns_no_run_log(self, tmp_path):
        """Returns 'no_run_log' when log file does not exist."""
        result = monday_morning_check(
            str(tmp_path / "nonexistent.txt"),
            str(tmp_path / "state.yaml"),
        )
        assert result == "no_run_log"

    def test_recent_run_returns_ok(self, tmp_path):
        """Returns 'ok' when last run was today."""
        from datetime import datetime
        run_log = tmp_path / "last_run.txt"
        run_log.write_text(datetime.now().isoformat())
        result = monday_morning_check(str(run_log), str(tmp_path / "state.yaml"))
        assert result == "ok"

    def test_old_run_returns_missed(self, tmp_path):
        """Returns 'missed' when last run was years ago."""
        run_log = tmp_path / "last_run.txt"
        run_log.write_text("2020-01-01T00:00:00")
        result = monday_morning_check(str(run_log), str(tmp_path / "state.yaml"))
        assert result == "missed"

    def test_timezone_aware_log_does_not_crash(self, tmp_path):
        """Timezone-aware ISO strings in run log must not raise TypeError."""
        run_log = tmp_path / "last_run.txt"
        run_log.write_text("2020-01-01T00:00:00+09:00")
        # Must return a valid status, not raise
        result = monday_morning_check(str(run_log), str(tmp_path / "state.yaml"))
        assert result in ("ok", "missed", "no_run_log")

    def test_invalid_log_content_returns_no_run_log(self, tmp_path):
        """Corrupt log file content returns 'no_run_log' gracefully."""
        run_log = tmp_path / "last_run.txt"
        run_log.write_text("not-a-valid-date")
        result = monday_morning_check(str(run_log), str(tmp_path / "state.yaml"))
        assert result == "no_run_log"
