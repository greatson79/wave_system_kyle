"""
investscan/watchdog.py — Watchdog for pipeline health monitoring.
Monitors SOT state, detects stale runs, alerts on anomalies.
English-First (P5-A).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Thresholds
MAX_STALE_HOURS: int = 25           # Report older than 25h is considered stale
MAX_PIPELINE_FAIL_COUNT: int = 3    # Alert after 3 consecutive failures
ONBOARDING_WEEKS: int = 4           # Auto-transition from onboarding after 4 weeks


def check_state_freshness(
    state_path: str = ".claude/state.yaml",
    max_stale_hours: int = MAX_STALE_HOURS,
) -> dict:
    """
    Check if state.yaml was updated recently.

    Returns:
        {fresh: bool, hours_since_update: float | None, last_updated: str}
    """
    path = Path(state_path)
    if not path.exists():
        return {"fresh": False, "hours_since_update": None, "last_updated": "never"}

    try:
        state = yaml.safe_load(path.read_text()) or {}
        last_updated = state.get("workflow", {}).get("last_updated", "")
        if not last_updated:
            return {"fresh": False, "hours_since_update": None, "last_updated": "unknown"}

        last_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_elapsed = (now - last_dt).total_seconds() / 3600

        return {
            "fresh": hours_elapsed <= max_stale_hours,
            "hours_since_update": round(hours_elapsed, 1),
            "last_updated": last_updated,
        }
    except Exception as e:
        logger.warning("Watchdog: state freshness check failed: %s", e)
        return {"fresh": False, "hours_since_update": None, "last_updated": "error"}


def check_tdd_status(state_path: str = ".claude/state.yaml") -> dict[str, str]:
    """
    Read tdd_status from state.yaml.
    Returns dict of {module: status} where status is "pending" | "passing" | "failing".
    """
    path = Path(state_path)
    if not path.exists():
        return {}
    try:
        state = yaml.safe_load(path.read_text()) or {}
        return state.get("tdd_status", {})
    except Exception:
        return {}


def get_failing_modules(state_path: str = ".claude/state.yaml") -> list[str]:
    """Return list of modules with status == "failing"."""
    tdd = check_tdd_status(state_path)
    return [module for module, status in tdd.items() if status == "failing"]


def get_watchdog_report(state_path: str = ".claude/state.yaml") -> dict:
    """
    Comprehensive watchdog report combining all health checks.

    Returns:
        {fresh, failing_modules, tdd_summary, overall_healthy}
    """
    freshness = check_state_freshness(state_path)
    failing = get_failing_modules(state_path)
    tdd = check_tdd_status(state_path)

    passing = [m for m, s in tdd.items() if s == "passing"]
    pending = [m for m, s in tdd.items() if s == "pending"]

    overall_healthy = freshness["fresh"] and len(failing) == 0

    return {
        "fresh": freshness["fresh"],
        "hours_since_update": freshness["hours_since_update"],
        "failing_modules": failing,
        "passing_modules": passing,
        "pending_modules": pending,
        "overall_healthy": overall_healthy,
    }


def is_paused_week(pause_weeks: list[str]) -> bool:
    """
    Return True if today is in the user-configured pause_weeks list.
    pause_weeks: list of "YYYY-MM-DD" date strings.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return today in pause_weeks


def check_onboarding_transition(
    state_path: str = ".claude/state.yaml",
    onboarding_mode: bool = True,
) -> bool:
    """
    Return True if onboarding period (4 weeks) has elapsed and auto-transition is needed.
    Reads system.installed_at from state.yaml to calculate weeks_since_install.
    """
    if not onboarding_mode:
        return False

    path = Path(state_path)
    if not path.exists():
        return False

    try:
        state = yaml.safe_load(path.read_text()) or {}
        installed_at_str = state.get("system", {}).get("installed_at", "")
        if not installed_at_str:
            return False
        installed_at = datetime.fromisoformat(str(installed_at_str))
        weeks_since_install = (datetime.now() - installed_at).days // 7
        return weeks_since_install >= ONBOARDING_WEEKS
    except Exception as e:
        logger.warning("check_onboarding_transition failed: %s", e)
        return False


def monday_morning_check(
    last_run_path: str = "logs/last_successful_run.txt",
    state_path: str = ".claude/state.yaml",
) -> str:
    """
    Check if Stage 1 ran this past Sunday. Returns status string:
      "ok"          — last run was this Sunday or later
      "missed"      — last Sunday's run was missed
      "no_run_log"  — no run log file exists yet
    """
    run_log = Path(last_run_path)
    if not run_log.exists():
        logger.warning("Monday check: no run log found at %s", last_run_path)
        return "no_run_log"

    try:
        last_run = datetime.fromisoformat(run_log.read_text().strip())
        # Normalize to naive for consistent date comparison
        # (run_log may contain timezone-aware ISO strings)
        if last_run.tzinfo is not None:
            last_run = last_run.replace(tzinfo=None)
        today = datetime.now()
        days_since_monday = today.weekday()  # 0=Mon, 6=Sun
        last_sunday = today - timedelta(days=days_since_monday + 1)

        if last_run.date() >= last_sunday.date():
            logger.info("Monday check: Stage 1 ran on %s (OK)", last_run.date())
            return "ok"
        else:
            logger.warning(
                "Monday check: Stage 1 last ran %s, missed Sunday %s",
                last_run.date(), last_sunday.date(),
            )
            return "missed"
    except Exception as e:
        logger.warning("Monday check failed: %s", e)
        return "no_run_log"
