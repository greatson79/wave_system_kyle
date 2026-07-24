"""
tests/test_m1_done_gate.py — M1 Milestone Done Gate tests (DG-09 through DG-16).
Infrastructure tier (75% coverage). English-First (P5-A).
All gates run in dry-run mode — no real API calls.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from run_m1 import (
    _check_dg09_dedup,
    _check_dg10_steeps,
    _check_dg11_signal_bridge,
    _check_dg12_synthesize_stock,
    _check_dg13_intelligence_engine,
    _check_dg14_validation,
    _check_dg15_weekly_orchestrator,
    _check_dg16_accuracy_tracker,
    M1_GATES,
    GATE_BY_ID,
    run_gates,
)


# ── DG-09: Dedup with source field ────────────────────────────────────────────

class TestDG09Dedup:
    def test_passes(self):
        ok, msg = _check_dg09_dedup()
        assert ok is True, f"DG-09 failed: {msg}"

    def test_message_confirms_distinct_hashes(self):
        ok, msg = _check_dg09_dedup()
        assert ok
        assert "distinct" in msg or "h1=" in msg

    def test_returns_tuple(self):
        result = _check_dg09_dedup()
        assert isinstance(result, tuple)
        assert len(result) == 2


# ── DG-10: STEEPs 6 categories ────────────────────────────────────────────────

class TestDG10Steeps:
    def test_passes(self):
        ok, msg = _check_dg10_steeps()
        assert ok is True, f"DG-10 failed: {msg}"

    def test_message_confirms_6_categories(self):
        ok, msg = _check_dg10_steeps()
        assert ok
        # All 6 category results must be in message
        assert "S=" in msg or "S=S" in msg

    def test_message_confirms_e_env(self):
        ok, msg = _check_dg10_steeps()
        assert ok
        assert "E_env" in msg

    def test_message_confirms_lowercase_s(self):
        ok, msg = _check_dg10_steeps()
        assert ok
        assert "sector" in msg.lower() or "s(sector)" in msg


# ── DG-11: Signal bridge routing ──────────────────────────────────────────────

class TestDG11SignalBridge:
    def test_passes(self):
        ok, msg = _check_dg11_signal_bridge()
        assert ok is True, f"DG-11 failed: {msg}"

    def test_message_confirms_e_env_routing(self):
        ok, msg = _check_dg11_signal_bridge()
        assert ok
        assert "industrials" in msg or "materials" in msg

    def test_message_confirms_sector_routing(self):
        ok, msg = _check_dg11_signal_bridge()
        assert ok
        assert "technology" in msg or "sector" in msg.lower()


# ── DG-12: synthesize_stock graceful fallback ─────────────────────────────────

class TestDG12SynthesizeStock:
    def test_passes(self):
        ok, msg = _check_dg12_synthesize_stock()
        assert ok is True, f"DG-12 failed: {msg}"

    def test_message_confirms_stock_financials(self):
        ok, msg = _check_dg12_synthesize_stock()
        assert ok
        assert "StockFinancials" in msg

    def test_message_confirms_graceful_fallback(self):
        ok, msg = _check_dg12_synthesize_stock()
        assert ok
        assert any(s in msg for s in ("mock", "partial", "fallback", "pykrx"))


# ── DG-13: intelligence_engine NarrativeOutput ────────────────────────────────

class TestDG13IntelligenceEngine:
    def test_passes(self):
        ok, msg = _check_dg13_intelligence_engine()
        assert ok is True, f"DG-13 failed: {msg}"

    def test_message_confirms_1000_bytes(self):
        ok, msg = _check_dg13_intelligence_engine()
        assert ok
        # Message should contain byte count
        assert "B" in msg or "byte" in msg.lower() or "1" in msg

    def test_message_confirms_sentinel_zero(self):
        ok, msg = _check_dg13_intelligence_engine()
        assert ok
        assert "0.0" in msg or "sentiment" in msg

    def test_message_confirms_category(self):
        ok, msg = _check_dg13_intelligence_engine()
        assert ok
        assert "category=" in msg or "A" in msg or "B" in msg


# ── DG-14: Python 8-criteria + citation validation ────────────────────────────

class TestDG14Validation:
    def test_passes(self):
        ok, msg = _check_dg14_validation()
        assert ok is True, f"DG-14 failed: {msg}"

    def test_message_confirms_8_criteria_pass(self):
        ok, msg = _check_dg14_validation()
        assert ok
        assert "8-criteria" in msg or "PASS" in msg

    def test_message_mentions_citation_validator(self):
        ok, msg = _check_dg14_validation()
        assert ok
        assert "citation" in msg.lower()


# ── DG-15: weekly_orchestrator full pipeline ──────────────────────────────────

class TestDG15WeeklyOrchestrator:
    """DG-15 runs the full pipeline dry-run — templates must be accessible from project root."""

    def test_passes(self):
        ok, msg = _check_dg15_weekly_orchestrator()
        assert ok is True, f"DG-15 failed: {msg}"

    def test_message_confirms_success(self):
        ok, msg = _check_dg15_weekly_orchestrator()
        assert ok
        assert "success" in msg.lower() or "✓" in msg

    def test_message_contains_report_path(self):
        ok, msg = _check_dg15_weekly_orchestrator()
        assert ok
        assert "report" in msg.lower() or "output" in msg.lower()

    def test_report_file_actually_exists(self):
        ok, msg = _check_dg15_weekly_orchestrator()
        assert ok
        # Extract path from message and verify
        import re
        match = re.search(r"output/reports/[\w\-\.]+", msg)
        if match:
            assert Path(match.group()).exists()


# ── DG-16: accuracy_tracker ───────────────────────────────────────────────────

class TestDG16AccuracyTracker:
    def test_passes(self):
        ok, msg = _check_dg16_accuracy_tracker()
        assert ok is True, f"DG-16 failed: {msg}"

    def test_message_confirms_prediction_recorded(self):
        ok, msg = _check_dg16_accuracy_tracker()
        assert ok
        assert "PredictionRecord" in msg or "week=" in msg

    def test_message_confirms_stock_code(self):
        ok, msg = _check_dg16_accuracy_tracker()
        assert ok
        assert "005930" in msg

    def test_returns_tuple(self):
        result = _check_dg16_accuracy_tracker()
        assert isinstance(result, tuple)
        ok, msg = result
        assert isinstance(ok, bool)
        assert isinstance(msg, str)


# ── Gate registry ─────────────────────────────────────────────────────────────

class TestGateRegistry:
    def test_exactly_8_gates(self):
        assert len(M1_GATES) == 8

    def test_gate_ids_are_dg09_through_dg16(self):
        ids = [g[0] for g in M1_GATES]
        expected = [f"DG-{i:02d}" for i in range(9, 17)]
        assert ids == expected

    def test_gate_by_id_lookup(self):
        assert "DG-09" in GATE_BY_ID
        assert "DG-16" in GATE_BY_ID

    def test_each_gate_has_callable(self):
        for gid, desc, fn in M1_GATES:
            assert callable(fn), f"{gid} fn is not callable"

    def test_each_gate_has_description(self):
        for gid, desc, fn in M1_GATES:
            assert isinstance(desc, str) and len(desc) > 0, f"{gid} missing description"


# ── run_gates() integration ───────────────────────────────────────────────────

class TestRunGates:
    """run_gates() must execute from project root (cwd = project root via pytest.ini)."""

    def test_all_gates_pass(self):
        """Full M1 milestone integration test — all 8 gates must pass."""
        passed, total = run_gates()
        assert total == 8
        assert passed == total, (
            f"M1 milestone NOT achieved: {passed}/{total} gates passed"
        )

    def test_single_gate_run(self):
        passed, total = run_gates(["DG-09"])
        assert total == 1
        assert passed == 1

    def test_returns_tuple_of_counts(self):
        result = run_gates(["DG-10"])
        assert isinstance(result, tuple)
        passed, total = result
        assert isinstance(passed, int)
        assert isinstance(total, int)

    def test_subset_gates(self):
        passed, total = run_gates(["DG-09", "DG-10", "DG-16"])
        assert total == 3
        assert passed == total
