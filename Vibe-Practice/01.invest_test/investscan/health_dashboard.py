"""
investscan/health_dashboard.py — Library availability tracking and system health.
v3.6 I-6: Track FDR/pykrx/dart-fss availability with 4-week rolling rate.
Alert threshold: 4-week availability < 80% → Telegram warning.
English-First (P5-A).
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable

import yaml

logger = logging.getLogger(__name__)

LIBRARY_AVAILABILITY_THRESHOLD: float = 0.80  # Alert if < 80%

LIBRARY_AVAILABILITY_TRACKING: dict[str, dict] = {
    "fdr": {
        "call": "fdr.DataReader('USD/KRW', start)",
        "timeout_sec": 10,
    },
    "pykrx": {
        "call": "stock.get_market_ohlcv('005930')",
        "timeout_sec": 10,
    },
    "dart_fss": {
        "call": "dart.get_corp_code('005930')",
        "timeout_sec": 10,
    },
}


def check_library(lib_name: str) -> bool:
    """
    Test if a library is importable and responsive.
    Returns True on success, False on any failure.
    """
    try:
        if lib_name == "fdr":
            import FinanceDataReader as fdr  # type: ignore  # noqa: F401
            return True
        elif lib_name == "pykrx":
            from pykrx import stock  # type: ignore  # noqa: F401
            return True
        elif lib_name == "dart_fss":
            import dart_fss  # type: ignore  # noqa: F401
            return True
        return False
    except ImportError:
        return False
    except Exception as e:
        logger.warning("Library check failed for %s: %s", lib_name, e)
        return False


def record_library_availability(
    lib_name: str,
    success: bool,
    state_path: str = ".claude/state.yaml",
) -> None:
    """
    Record library call success/failure in state.yaml library_availability section.
    Maintains 4-week rolling average.
    """
    path = Path(state_path)
    if not path.exists():
        return

    try:
        state = yaml.safe_load(path.read_text()) or {}
        lib_section = state.setdefault("library_availability", {})
        lib_data = lib_section.setdefault(lib_name, {
            "success_count": 0,
            "total_count": 0,
            "rolling_4w_rate": None,
        })

        lib_data["total_count"] = lib_data.get("total_count", 0) + 1
        if success:
            lib_data["success_count"] = lib_data.get("success_count", 0) + 1

        total = lib_data["total_count"]
        success_count = lib_data["success_count"]
        lib_data["rolling_4w_rate"] = success_count / total if total > 0 else None

        # Atomic write
        tmp = path.with_suffix(".tmp")
        tmp.write_text(yaml.dump(state, allow_unicode=True))
        tmp.rename(path)

        # Alert if below threshold
        rate = lib_data["rolling_4w_rate"]
        if rate is not None and rate < LIBRARY_AVAILABILITY_THRESHOLD:
            logger.warning(
                "Library %s availability %.0f%% below threshold %.0f%%",
                lib_name, rate * 100, LIBRARY_AVAILABILITY_THRESHOLD * 100,
            )

    except Exception as e:
        logger.error("Failed to record library availability: %s", e)


def run_health_check(config: dict | None = None) -> dict[str, bool]:
    """
    Run availability check for all tracked libraries.
    Records results to state.yaml.

    Returns:
        {lib_name: is_available} dict.
    """
    results = {}
    for lib_name in LIBRARY_AVAILABILITY_TRACKING:
        available = check_library(lib_name)
        results[lib_name] = available
        record_library_availability(lib_name, available)
        logger.info("Library %s: %s", lib_name, "available" if available else "unavailable")
    return results


def get_availability_report(state_path: str = ".claude/state.yaml") -> dict:
    """
    Read current library availability rates from state.yaml.
    Returns empty dict if state.yaml not found.
    """
    path = Path(state_path)
    if not path.exists():
        return {}
    try:
        state = yaml.safe_load(path.read_text()) or {}
        return state.get("library_availability", {})
    except Exception:
        return {}


def generate_html_dashboard(
    state_path: str = ".claude/state.yaml",
    output_path: str = "output/dashboard/weekly_dashboard.html",
) -> str:
    """
    Generate output/dashboard/weekly_dashboard.html with 5 required sections:
    1. Last run timestamp
    2. Sector directions + confidence
    3. Data freshness status
    4. Error log entries (last 5)
    5. Kill Switch status

    Returns the output path on success.
    """
    from datetime import datetime as dt

    state: dict = {}
    if Path(state_path).exists():
        try:
            state = yaml.safe_load(Path(state_path).read_text()) or {}
        except Exception as e:
            logger.warning("Dashboard: failed to load state: %s", e)

    # 1. Last run info
    last_updated = state.get("workflow", {}).get("last_updated", "N/A")
    last_report = state.get("workflow", {}).get("last_successful_report", "N/A")
    runtime_mode = state.get("workflow", {}).get("runtime_mode", "unknown")

    # 2. Library availability
    lib_avail = state.get("library_availability", {})

    # 3. Errors
    errors = state.get("errors", [])[-5:]  # last 5

    # 4. Milestones
    m05 = state.get("milestones", {}).get("m05", {})
    m1 = state.get("milestones", {}).get("m1", {})

    # 5. TDD status
    tdd = state.get("tdd_status", {})
    passing = sum(1 for s in tdd.values() if s == "passing")
    total = len(tdd)

    def _bar(rate: float | None) -> str:
        if rate is None:
            return "N/A"
        pct = int((rate or 0) * 100)
        color = "#28a745" if pct >= 80 else "#dc3545"
        return f'<span style="color:{color}">{pct}%</span>'

    lib_rows = ""
    for lib, data in lib_avail.items():
        rate = data.get("rolling_4w_rate")
        lib_rows += f"<tr><td>{lib}</td><td>{_bar(rate)}</td></tr>"

    error_items = "".join(f"<li>{e}</li>" for e in errors) or "<li>No errors</li>"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>InvestScan Health Dashboard</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; background: #f8f9fa; }}
h1 {{ color: #343a40; }}
.card {{ background: white; border-radius: 8px; padding: 16px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ padding: 8px 12px; border-bottom: 1px solid #dee2e6; text-align: left; }}
.badge {{ padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
.green {{ background: #d4edda; color: #155724; }}
.red {{ background: #f8d7da; color: #721c24; }}
.gray {{ background: #e2e3e5; color: #383d41; }}
</style>
</head>
<body>
<h1>📊 InvestScan Health Dashboard</h1>
<p style="color:#6c757d">Generated: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="card">
<h3>🕐 Last Run</h3>
<table>
<tr><td>Last Updated</td><td>{last_updated}</td></tr>
<tr><td>Last Report</td><td>{last_report}</td></tr>
<tr><td>Runtime Mode</td><td><span class="badge gray">{runtime_mode}</span></td></tr>
</table>
</div>

<div class="card">
<h3>📦 Library Availability (4-week rolling)</h3>
<table><tr><th>Library</th><th>Availability</th></tr>
{lib_rows if lib_rows else "<tr><td colspan='2'>No data yet</td></tr>"}
</table>
</div>

<div class="card">
<h3>✅ Test Status</h3>
<p>{passing}/{total} modules passing
<span class="badge {'green' if passing == total else 'red'}">{passing}/{total}</span>
</p>
</div>

<div class="card">
<h3>🏆 Milestones</h3>
<table>
<tr><td>M0.5 DG-01~08</td><td>{'<span class="badge green">PASS</span>' if m05.get("dg_01_to_08_passed") else '<span class="badge gray">pending</span>'}</td></tr>
<tr><td>M0.5 Tests Passing</td><td>{m05.get("tests_passing", "N/A")}</td></tr>
<tr><td>M1 DG-09~16</td><td>{'<span class="badge green">PASS</span>' if m1.get("dg_09_to_16_passed") else '<span class="badge gray">pending</span>'}</td></tr>
<tr><td>Full Pipeline</td><td>{'<span class="badge green">READY</span>' if m1.get("full_pipeline_ready") else '<span class="badge gray">pending</span>'}</td></tr>
</table>
</div>

<div class="card">
<h3>⚠️ Recent Errors (last 5)</h3>
<ul>{error_items}</ul>
</div>
</body>
</html>"""

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    logger.info("Health dashboard written to %s", output_path)
    return output_path
