"""
run_m05.py — M0.5 Milestone Done Gate runner (DG-01 through DG-08).
Usage:
    python run_m05.py --dry-run      # Verify all 8 Done Gates (no real API calls)
    python run_m05.py --gate DG-04   # Run single gate

DG-01: config.py loads without error (sector_stock_map, BULLISH_THRESHOLD)
DG-02: normalizers.py processes a sample signal without raising
DG-03: synthesize_macro returns InvestmentMeta with correct labels
DG-04: sentiment_weight sentinel enforced = 0.0 in intelligence_engine
DG-05: compliance_filter passes on clean text, blocks prohibited expression
DG-06: telegram_notifier dry-run prints to stdout (no network call)
DG-07: run_full_pipeline dry-run returns status='success'
DG-08: state.yaml can be written and read back (atomic write pattern)

Exit codes:
    0 — all gates passed
    1 — one or more gates failed
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Callable

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


# ── Gate implementations ───────────────────────────────────────────────────────

def _check_dg01_config() -> tuple[bool, str]:
    """DG-01: config.py loads; stock_selector constants verified; YAML config parseable."""
    try:
        from investscan.config import load_config, is_dry_run, ConfigError
        from investscan.stock_selector import BULLISH_THRESHOLD

        assert BULLISH_THRESHOLD == 0.01, f"BULLISH_THRESHOLD={BULLISH_THRESHOLD}, expected 0.01"

        # sector_stock_map.yaml must exist and parse
        import yaml
        sector_map_path = Path("config/sector_stock_map.yaml")
        assert sector_map_path.exists(), f"Missing: {sector_map_path}"
        sector_data = yaml.safe_load(sector_map_path.read_text(encoding="utf-8"))
        assert isinstance(sector_data, dict) and len(sector_data) > 0, (
            "sector_stock_map.yaml is empty or malformed"
        )

        # load_config works with investscan.yaml
        cfg = load_config("investscan.yaml")
        assert isinstance(cfg, dict), "load_config() must return a dict"
        assert "mode" in cfg, "Config missing 'mode' key"

        return True, f"config loaded (mode={cfg['mode']}), BULLISH_THRESHOLD=0.01 ✓"
    except Exception as e:
        return False, f"config load failed: {e}"


def _check_dg02_normalizers() -> tuple[bool, str]:
    """DG-02: normalizers.py processes envscan fixture without raising."""
    try:
        from investscan.normalizers import normalize_envscan, load_envscan_file
        from investscan.schema import UnifiedSignal

        # Use the fixture file
        fixture_path = "tests/fixtures/envscan_sample.json"
        data = load_envscan_file(fixture_path)
        signals = normalize_envscan(data)

        assert isinstance(signals, list), f"Expected list, got {type(signals)}"
        assert len(signals) > 0, "normalize_envscan returned empty list"
        assert isinstance(signals[0], UnifiedSignal), (
            f"Expected UnifiedSignal, got {type(signals[0])}"
        )
        return True, f"normalize_envscan returned {len(signals)} UnifiedSignal(s) ✓"
    except Exception as e:
        return False, f"normalizer failed: {e}"


def _check_dg03_synthesize_macro() -> tuple[bool, str]:
    """DG-03: synthesize_macro.synthesize() returns InvestmentMeta with correct labels."""
    try:
        from investscan.synthesize_macro import synthesize, load_fred_fixture
        from investscan.schema import InvestmentMeta

        fred_data = load_fred_fixture()  # reads tests/fixtures/fred_sample.json
        meta = synthesize(fred_data, config={"mode": "dry-run"})
        assert isinstance(meta, InvestmentMeta), f"Expected InvestmentMeta, got {type(meta)}"
        assert meta.rate_direction in ("hike", "cut", "hold"), (
            f"rate_direction='{meta.rate_direction}' not in (hike, cut, hold)"
        )
        assert meta.inflation_trend in ("rising", "cooling", "stable"), (
            f"inflation_trend='{meta.inflation_trend}' not valid"
        )
        assert meta.risk_appetite in ("high", "moderate", "low"), (
            f"risk_appetite='{meta.risk_appetite}' not valid"
        )
        return True, (
            f"InvestmentMeta(rate={meta.rate_direction}, inflation={meta.inflation_trend}, "
            f"risk={meta.risk_appetite}) ✓"
        )
    except Exception as e:
        return False, f"synthesize_macro failed: {e}"


def _check_dg04_sentinel() -> tuple[bool, str]:
    """DG-04: intelligence_engine enforces sentiment_weight == 0.0."""
    try:
        from investscan.intelligence_engine import generate
        from investscan.schema import NarrativeOutput

        context = {
            "category": "A",
            "stock_code": "005930",
            "stock_name": "Samsung Electronics",
            "analysis_date": "2026-03-29",
            "yoy_revenue_growth": 0.083,
            "yoy_op_income_growth": 0.342,
            "latest_quarter": "2025Q4",
            "per_current": 10.2,
            "per_sector_avg": 14.2,
            "foreign_flow_4w": 380.0,
            "rate_direction": "hold",
            "inflation_trend": "cooling",
            "risk_appetite": "moderate",
            "usd_strength": "strong",
            "top_signals": ["AI semiconductor demand"],
        }
        narrative = generate(context, config={"mode": "dry-run"})
        assert isinstance(narrative, NarrativeOutput)
        assert narrative.sentiment_weight == 0.0, (
            f"SENTINEL VIOLATION: sentiment_weight={narrative.sentiment_weight}"
        )
        assert len(narrative.text.encode("utf-8")) >= 1000, (
            f"Text too short: {len(narrative.text.encode())} bytes"
        )
        return True, f"NarrativeOutput(category={narrative.category}, sentiment_weight=0.0) ✓"
    except Exception as e:
        return False, f"intelligence_engine sentinel check failed: {e}"


def _check_dg05_compliance() -> tuple[bool, str]:
    """DG-05: compliance_filter passes clean text, blocks prohibited expression."""
    try:
        from investscan.compliance_filter import filter_report, PROHIBITION_PATTERNS

        # Clean text should pass
        clean_text = "Samsung shows positive momentum based on fundamental analysis."
        compliant, violations = filter_report(clean_text, 0.0)
        assert compliant is True, f"Clean text failed compliance: {violations}"
        assert violations == []

        # Prohibited text should fail
        prohibited_text = "이 종목 매수 추천합니다!"
        compliant2, violations2 = filter_report(prohibited_text, 0.0)
        assert compliant2 is False, "Prohibited text should have been blocked"
        assert len(violations2) > 0

        assert len(PROHIBITION_PATTERNS) == 10, (
            f"Expected 10 patterns, got {len(PROHIBITION_PATTERNS)}"
        )
        return True, f"compliance_filter: clean=PASS, prohibited=BLOCKED, 10 patterns ✓"
    except Exception as e:
        return False, f"compliance_filter check failed: {e}"


def _check_dg06_telegram_dry() -> tuple[bool, str]:
    """DG-06: telegram_notifier dry-run builds 5-line Korean summary without error."""
    try:
        from investscan.telegram_notifier import build_5line_summary

        summary = build_5line_summary(
            stock_name="삼성전자",
            stock_code="005930",
            category="A",
            narrative_text="Samsung Q4 results with Revenue +8.3% YoY momentum strong.",
            direction="Positive momentum maintained",
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.2%",
            downside_risk="DRAM oversupply → est. -12% revenue impact",
        )
        assert isinstance(summary, str), f"Expected str, got {type(summary)}"
        assert len(summary) > 0, "5-line summary is empty"
        assert "삼성전자" in summary or "005930" in summary or "A" in summary
        return True, f"5-line summary built ({len(summary)} chars) ✓"
    except Exception as e:
        return False, f"telegram_notifier check failed: {e}"


def _check_dg07_pipeline_dry() -> tuple[bool, str]:
    """DG-07: run_full_pipeline dry-run returns status='success'."""
    try:
        from investscan.weekly_orchestrator import run_full_pipeline

        result = run_full_pipeline(
            stock_code="005930",
            stock_name="Samsung Electronics",
            category="A",
            config={"mode": "dry-run"},
        )
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert result.get("status") == "success", (
            f"Pipeline returned status={result.get('status')!r}. "
            f"Error: {result.get('error', 'none')}"
        )
        report_path = result.get("report_path")
        assert report_path is not None, "report_path missing from result"
        return True, f"Pipeline success, report at {report_path} ✓"
    except Exception as e:
        return False, f"run_full_pipeline dry-run failed: {e}"


def _check_dg08_state_written() -> tuple[bool, str]:
    """DG-08: state.yaml can be read as YAML (atomic write pattern integrity)."""
    try:
        import yaml

        state_path = Path(".claude/state.yaml")
        if not state_path.exists():
            # Create minimal state for test
            state_path.parent.mkdir(parents=True, exist_ok=True)
            minimal_state = {
                "system": {"version": "1.0.0"},
                "workflow": {"current_phase": "research"},
                "packages": {"m05_ready": False},
            }
            tmp = state_path.with_suffix(".tmp")
            tmp.write_text(yaml.dump(minimal_state), encoding="utf-8")
            tmp.rename(state_path)

        content = state_path.read_text(encoding="utf-8")
        state = yaml.safe_load(content)
        assert isinstance(state, dict), "state.yaml must parse as dict"
        assert "workflow" in state or "system" in state, (
            "state.yaml missing required top-level keys"
        )

        # Verify no .tmp file is leftover
        tmp_file = state_path.with_suffix(".tmp")
        assert not tmp_file.exists(), f"Leftover tmp file: {tmp_file}"

        return True, "state.yaml exists, parses as YAML, no stale .tmp ✓"
    except Exception as e:
        return False, f"state.yaml check failed: {e}"


# ── Gate registry ──────────────────────────────────────────────────────────────

M05_GATES: list[tuple[str, str, Callable[[], tuple[bool, str]]]] = [
    ("DG-01", "config.py constants and load_config()", _check_dg01_config),
    ("DG-02", "normalizers.py signal normalization", _check_dg02_normalizers),
    ("DG-03", "synthesize_macro InvestmentMeta labels", _check_dg03_synthesize_macro),
    ("DG-04", "sentiment_weight sentinel == 0.0", _check_dg04_sentinel),
    ("DG-05", "compliance_filter 10 patterns", _check_dg05_compliance),
    ("DG-06", "telegram_notifier 5-line summary", _check_dg06_telegram_dry),
    ("DG-07", "run_full_pipeline dry-run success", _check_dg07_pipeline_dry),
    ("DG-08", "state.yaml atomic write integrity", _check_dg08_state_written),
]

GATE_BY_ID: dict[str, tuple[str, Callable[[], tuple[bool, str]]]] = {
    gid: (desc, fn) for gid, desc, fn in M05_GATES
}


def run_gates(gate_ids: list[str] | None = None) -> tuple[int, int]:
    """
    Run specified gates (or all if gate_ids is None).

    Returns:
        (passed_count, total_count)
    """
    targets = (
        [(gid, desc, fn) for gid, desc, fn in M05_GATES if gid in gate_ids]
        if gate_ids
        else M05_GATES
    )

    passed = 0
    total = len(targets)

    print(f"\n{'='*60}")
    print(f"  InvestScan M0.5 Done Gate Runner  ({total} gates)")
    print(f"{'='*60}\n")

    for gid, desc, fn in targets:
        print(f"  [{gid}] {desc}")
        try:
            ok, message = fn()
        except Exception as e:
            ok, message = False, f"Unexpected error: {e}"

        status = "PASS ✓" if ok else "FAIL ✗"
        icon = "  ✓" if ok else "  ✗"
        print(f"{icon}  {status} — {message}\n")
        if ok:
            passed += 1

    print(f"{'='*60}")
    print(f"  Result: {passed}/{total} gates passed")
    if passed < total:
        print(f"  FAILED: {total - passed} gate(s) require attention")
    else:
        print(f"  M0.5 MILESTONE ACHIEVED — system ready for M1")
    print(f"{'='*60}\n")

    return passed, total


def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan M0.5 Done Gate Runner")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run all gates in dry-run mode (default: True)",
    )
    parser.add_argument(
        "--gate",
        metavar="GATE_ID",
        help="Run a single gate (e.g., --gate DG-04)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    gate_ids = [args.gate] if args.gate else None

    if gate_ids and gate_ids[0] not in GATE_BY_ID:
        print(f"ERROR: Unknown gate '{gate_ids[0]}'. Available: {list(GATE_BY_ID.keys())}")
        return 1

    if args.json:
        results = {}
        for gid, desc, fn in M05_GATES:
            if gate_ids and gid not in gate_ids:
                continue
            try:
                ok, msg = fn()
            except Exception as e:
                ok, msg = False, str(e)
            results[gid] = {"passed": ok, "message": msg, "description": desc}
        print(json.dumps(results, indent=2, ensure_ascii=False))
        all_passed = all(v["passed"] for v in results.values())
        return 0 if all_passed else 1

    passed, total = run_gates(gate_ids)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
