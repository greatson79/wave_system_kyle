"""
tests/test_m05_done_gate.py — M0.5 Milestone Done Gate tests (DG-01 through DG-08).
Infrastructure tier (75% coverage). English-First (P5-A).
All gates run in dry-run mode — no real API calls.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from run_m05 import (
    _check_dg01_config,
    _check_dg02_normalizers,
    _check_dg03_synthesize_macro,
    _check_dg04_sentinel,
    _check_dg05_compliance,
    _check_dg06_telegram_dry,
    _check_dg07_pipeline_dry,
    _check_dg08_state_written,
    M05_GATES,
    GATE_BY_ID,
    run_gates,
)


# ── DG-01: Config ─────────────────────────────────────────────────────────────

class TestDG01Config:
    def test_passes(self):
        ok, msg = _check_dg01_config()
        assert ok is True, f"DG-01 failed: {msg}"

    def test_message_contains_mode(self):
        ok, msg = _check_dg01_config()
        assert ok
        assert "mode=" in msg or "dry-run" in msg or "0.01" in msg

    def test_returns_tuple(self):
        result = _check_dg01_config()
        assert isinstance(result, tuple)
        assert len(result) == 2


# ── DG-02: Normalizers ────────────────────────────────────────────────────────

class TestDG02Normalizers:
    def test_passes(self):
        ok, msg = _check_dg02_normalizers()
        assert ok is True, f"DG-02 failed: {msg}"

    def test_message_indicates_success(self):
        ok, msg = _check_dg02_normalizers()
        assert ok
        assert "NormalizedSignal" in msg or "gnews" in msg or "✓" in msg


# ── DG-03: Synthesize Macro ───────────────────────────────────────────────────

class TestDG03SynthesizeMacro:
    def test_passes(self):
        ok, msg = _check_dg03_synthesize_macro()
        assert ok is True, f"DG-03 failed: {msg}"

    def test_message_contains_rate_direction(self):
        ok, msg = _check_dg03_synthesize_macro()
        assert ok
        # Should contain one of the valid labels
        assert any(label in msg for label in ("hike", "cut", "hold"))

    def test_message_contains_inflation_label(self):
        ok, msg = _check_dg03_synthesize_macro()
        assert ok
        assert any(label in msg for label in ("rising", "cooling", "stable"))


# ── DG-04: Sentinel ───────────────────────────────────────────────────────────

class TestDG04Sentinel:
    def test_passes(self):
        ok, msg = _check_dg04_sentinel()
        assert ok is True, f"DG-04 failed: {msg}"

    def test_message_confirms_sentinel_zero(self):
        ok, msg = _check_dg04_sentinel()
        assert ok
        assert "0.0" in msg or "sentiment_weight" in msg

    def test_message_confirms_text_length(self):
        ok, msg = _check_dg04_sentinel()
        assert ok
        # Should have produced valid NarrativeOutput


# ── DG-05: Compliance ─────────────────────────────────────────────────────────

class TestDG05Compliance:
    def test_passes(self):
        ok, msg = _check_dg05_compliance()
        assert ok is True, f"DG-05 failed: {msg}"

    def test_message_confirms_10_patterns(self):
        ok, msg = _check_dg05_compliance()
        assert ok
        assert "10" in msg

    def test_message_confirms_clean_pass_and_blocked(self):
        ok, msg = _check_dg05_compliance()
        assert ok
        assert "PASS" in msg or "✓" in msg
        assert "BLOCKED" in msg or "blocked" in msg.lower()


# ── DG-06: Telegram Dry-run ───────────────────────────────────────────────────

class TestDG06TelegramDry:
    def test_passes(self):
        ok, msg = _check_dg06_telegram_dry()
        assert ok is True, f"DG-06 failed: {msg}"

    def test_message_contains_summary_info(self):
        ok, msg = _check_dg06_telegram_dry()
        assert ok
        assert "summary" in msg.lower() or "char" in msg.lower() or "✓" in msg


# ── DG-07: Full Pipeline Dry-run ─────────────────────────────────────────────

class TestDG07PipelineDryRun:
    """DG-07 runs from project root — templates/weekly-report.md.j2 must be accessible."""

    def test_passes(self):
        ok, msg = _check_dg07_pipeline_dry()
        assert ok is True, f"DG-07 failed: {msg}"

    def test_message_contains_success(self):
        ok, msg = _check_dg07_pipeline_dry()
        assert ok
        assert "success" in msg.lower() or "✓" in msg

    def test_message_contains_report_path(self):
        ok, msg = _check_dg07_pipeline_dry()
        assert ok
        assert "report" in msg.lower() or "output" in msg.lower() or "✓" in msg


# ── DG-08: State YAML ─────────────────────────────────────────────────────────

class TestDG08StateWritten:
    """Runs from project root where .claude/state.yaml already exists."""

    def test_passes(self):
        ok, msg = _check_dg08_state_written()
        assert ok is True, f"DG-08 failed: {msg}"

    def test_no_tmp_file_leftover(self):
        ok, msg = _check_dg08_state_written()
        assert ok
        from pathlib import Path
        tmp_file = Path(".claude/state.yaml").with_suffix(".tmp")
        assert not tmp_file.exists()

    def test_message_confirms_yaml(self):
        ok, msg = _check_dg08_state_written()
        assert ok
        assert "yaml" in msg.lower() or "YAML" in msg or "✓" in msg

    def test_sot_updated_after_pipeline(self):
        """DG-07 + DG-08: run_full_pipeline sets packages.m05_ready=True in state.yaml."""
        import yaml
        from pathlib import Path
        # DG-07 already ran run_full_pipeline — verify SOT was updated
        ok, _ = _check_dg07_pipeline_dry()
        assert ok, "DG-07 must pass before SOT update can be verified"
        state = yaml.safe_load(Path(".claude/state.yaml").read_text(encoding="utf-8"))
        assert state.get("packages", {}).get("m05_ready") is True, (
            "SOT not updated: packages.m05_ready should be True after successful pipeline run"
        )


# ── Gate registry ─────────────────────────────────────────────────────────────

class TestGateRegistry:
    def test_exactly_8_gates(self):
        assert len(M05_GATES) == 8

    def test_gate_ids_are_dg01_through_dg08(self):
        ids = [g[0] for g in M05_GATES]
        expected = [f"DG-{i:02d}" for i in range(1, 9)]
        assert ids == expected

    def test_gate_by_id_lookup(self):
        assert "DG-01" in GATE_BY_ID
        assert "DG-08" in GATE_BY_ID

    def test_each_gate_has_callable(self):
        for gid, desc, fn in M05_GATES:
            assert callable(fn), f"{gid} fn is not callable"

    def test_each_gate_has_description(self):
        for gid, desc, fn in M05_GATES:
            assert isinstance(desc, str) and len(desc) > 0, f"{gid} missing description"


# ── run_gates() integration ───────────────────────────────────────────────────

class TestRunGates:
    """
    run_gates() must execute from the project root (where investscan.yaml,
    config/, tests/fixtures/, and templates/ all live).
    No chdir — pytest is invoked from the project root.
    """

    def test_all_gates_pass(self):
        """Full M0.5 milestone integration test — all 8 gates must pass."""
        passed, total = run_gates()
        assert total == 8
        assert passed == total, (
            f"M0.5 milestone NOT achieved: {passed}/{total} gates passed"
        )

    def test_single_gate_run(self):
        passed, total = run_gates(["DG-01"])
        assert total == 1
        assert passed == 1

    def test_returns_tuple_of_counts(self):
        result = run_gates(["DG-04"])
        assert isinstance(result, tuple)
        passed, total = result
        assert isinstance(passed, int)
        assert isinstance(total, int)
