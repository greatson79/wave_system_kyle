"""
tests/test_accuracy_tracker.py — Tests for accuracy_tracker.py.
Infrastructure tier (75% coverage). English-First (P5-A).
KS-1 dual-window accuracy: 4-week preliminary + 8-week final.
All I/O uses tmp_path — no real data/accuracy directory touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from investscan.accuracy_tracker import (
    ACCURACY_WINDOW_FINAL,
    ACCURACY_WINDOW_PRELIMINARY,
    BULLISH_THRESHOLD,
    NEUTRAL_BAND,
    _compute_naive_baselines,
    _return_to_direction,
    compute_accuracy,
    load_all_records,
    record_prediction,
    update_actual_return,
)
from investscan.schema import PredictionRecord


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_preliminary_window_is_4(self):
        assert ACCURACY_WINDOW_PRELIMINARY == 4

    def test_final_window_is_8(self):
        assert ACCURACY_WINDOW_FINAL == 8

    def test_bullish_threshold_is_001(self):
        assert BULLISH_THRESHOLD == 0.01

    def test_neutral_band_is_003(self):
        assert NEUTRAL_BAND == 0.03


# ── _return_to_direction() — P6 deterministic classification ──────────────────

class TestReturnToDirection:
    def test_above_bullish_threshold_is_positive(self):
        result = _return_to_direction(0.05)
        assert result == "Positive momentum maintained"

    def test_exactly_bullish_threshold_is_positive(self):
        # Strictly above BULLISH_THRESHOLD=0.01
        result = _return_to_direction(0.011)
        assert result == "Positive momentum maintained"

    def test_at_threshold_boundary(self):
        # 0.01 is NOT > BULLISH_THRESHOLD(0.01) → falls to neutral check
        result = _return_to_direction(0.01)
        # abs(0.01) <= NEUTRAL_BAND(0.03) → Neutral
        assert result == "Neutral — monitor and wait"

    def test_within_neutral_band_positive(self):
        # 0.02 > BULLISH_THRESHOLD(0.01) → Positive momentum maintained
        result = _return_to_direction(0.02)
        assert result == "Positive momentum maintained"

    def test_within_neutral_band_negative(self):
        result = _return_to_direction(-0.02)
        assert result == "Neutral — monitor and wait"

    def test_zero_is_neutral(self):
        result = _return_to_direction(0.0)
        assert result == "Neutral — monitor and wait"

    def test_large_negative_is_risk_zone(self):
        result = _return_to_direction(-0.10)
        assert result == "Risk zone"

    def test_exactly_minus_neutral_band_is_neutral(self):
        # abs(-0.03) <= 0.03 → Neutral
        result = _return_to_direction(-0.03)
        assert result == "Neutral — monitor and wait"

    def test_just_outside_neutral_band_negative_is_risk(self):
        result = _return_to_direction(-0.031)
        assert result == "Risk zone"

    def test_returns_string(self):
        assert isinstance(_return_to_direction(0.05), str)


# ── record_prediction() ────────────────────────────────────────────────────────

class TestRecordPrediction:
    def test_returns_prediction_record(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record = record_prediction("005930", "Positive momentum maintained",
                                   week_label="2026-W13", config=cfg)
        assert isinstance(record, PredictionRecord)

    def test_record_fields_correct(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record = record_prediction("005930", "Positive momentum maintained",
                                   week_label="2026-W13", config=cfg)
        assert record.stock_code == "005930"
        assert record.week_label == "2026-W13"
        assert record.direction == "Positive momentum maintained"

    def test_actual_returns_none_on_creation(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record = record_prediction("005930", "Risk zone",
                                   week_label="2026-W13", config=cfg)
        assert record.actual_return_4w is None
        assert record.actual_return_8w is None

    def test_creates_jsonl_file(self, tmp_path):
        acc_dir = tmp_path / "accuracy"
        cfg = {"paths": {"accuracy_data": str(acc_dir)}}
        record_prediction("005930", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        assert (acc_dir / "005930.jsonl").exists()

    def test_auto_generates_week_label(self, tmp_path):
        import re
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record = record_prediction("005930", "Neutral — monitor and wait", config=cfg)
        assert re.match(r"\d{4}-W\d{2}", record.week_label)

    def test_recorded_at_is_set(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record = record_prediction("005930", "Risk zone",
                                   week_label="2026-W13", config=cfg)
        assert record.recorded_at != ""

    def test_multiple_stocks_separate_files(self, tmp_path):
        acc_dir = tmp_path / "accuracy"
        cfg = {"paths": {"accuracy_data": str(acc_dir)}}
        record_prediction("005930", "Risk zone", week_label="2026-W13", config=cfg)
        record_prediction("035420", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        assert (acc_dir / "005930.jsonl").exists()
        assert (acc_dir / "035420.jsonl").exists()


# ── load_all_records() ─────────────────────────────────────────────────────────

class TestLoadAllRecords:
    def test_returns_empty_list_when_no_file(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        records = load_all_records("999999", cfg)
        assert records == []

    def test_loads_written_records(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record_prediction("005930", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        records = load_all_records("005930", cfg)
        assert len(records) == 1
        assert records[0]["stock_code"] == "005930"

    def test_loads_multiple_records(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        for week in ["2026-W11", "2026-W12", "2026-W13"]:
            record_prediction("005930", "Risk zone", week_label=week, config=cfg)
        records = load_all_records("005930", cfg)
        assert len(records) == 3

    def test_returns_list_of_dicts(self, tmp_path):
        cfg = {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}
        record_prediction("005930", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        records = load_all_records("005930", cfg)
        assert isinstance(records, list)
        assert isinstance(records[0], dict)


# ── update_actual_return() ─────────────────────────────────────────────────────

class TestUpdateActualReturn:
    def _make_config(self, tmp_path):
        return {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}

    def test_returns_true_when_found(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        result = update_actual_return("005930", "2026-W13", 0.07,
                                      ACCURACY_WINDOW_FINAL, cfg)
        assert result is True

    def test_returns_false_when_not_found(self, tmp_path):
        cfg = self._make_config(tmp_path)
        result = update_actual_return("005930", "2026-W99", 0.07,
                                      ACCURACY_WINDOW_FINAL, cfg)
        assert result is False

    def test_updates_4w_window(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Risk zone", week_label="2026-W13", config=cfg)
        update_actual_return("005930", "2026-W13", 0.05,
                             ACCURACY_WINDOW_PRELIMINARY, cfg)
        records = load_all_records("005930", cfg)
        assert records[0]["actual_return_4w"] == 0.05
        assert records[0]["actual_return_8w"] is None

    def test_updates_8w_window(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Risk zone", week_label="2026-W13", config=cfg)
        update_actual_return("005930", "2026-W13", -0.04,
                             ACCURACY_WINDOW_FINAL, cfg)
        records = load_all_records("005930", cfg)
        assert records[0]["actual_return_8w"] == -0.04

    def test_atomic_write_no_tmp_leftover(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Risk zone", week_label="2026-W13", config=cfg)
        update_actual_return("005930", "2026-W13", 0.05,
                             ACCURACY_WINDOW_FINAL, cfg)
        acc_dir = tmp_path / "accuracy"
        tmp_file = acc_dir / "005930.tmp"
        assert not tmp_file.exists()


# ── compute_accuracy() ─────────────────────────────────────────────────────────

class TestComputeAccuracy:
    def _make_config(self, tmp_path):
        return {"paths": {"accuracy_data": str(tmp_path / "accuracy")}}

    def test_returns_dict(self, tmp_path):
        cfg = self._make_config(tmp_path)
        result = compute_accuracy("005930", config=cfg)
        assert isinstance(result, dict)

    def test_empty_when_no_records(self, tmp_path):
        cfg = self._make_config(tmp_path)
        result = compute_accuracy("005930", config=cfg)
        assert result["accuracy"] is None
        assert result["total"] == 0
        assert result["correct"] == 0

    def test_ks1_label_month_3(self, tmp_path):
        """v3.6 I-5: Must be 'Month 3 data basis', NOT 'Month 2'."""
        cfg = self._make_config(tmp_path)
        result = compute_accuracy("005930", config=cfg)
        assert result["ks1_label"] == "Month 3 data basis"

    def test_window_in_result(self, tmp_path):
        cfg = self._make_config(tmp_path)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_FINAL, config=cfg)
        assert result["window"] == ACCURACY_WINDOW_FINAL

    def test_perfect_accuracy_all_correct(self, tmp_path):
        cfg = self._make_config(tmp_path)
        # Record 3 predictions with "Positive momentum maintained"
        for week in ["2026-W11", "2026-W12", "2026-W13"]:
            record_prediction("005930", "Positive momentum maintained",
                              week_label=week, config=cfg)
        # Set actual returns all strongly positive (> BULLISH_THRESHOLD)
        for week in ["2026-W11", "2026-W12", "2026-W13"]:
            update_actual_return("005930", week, 0.08, ACCURACY_WINDOW_FINAL, cfg)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_FINAL, config=cfg)
        assert result["accuracy"] == 1.0
        assert result["total"] == 3
        assert result["correct"] == 3

    def test_zero_accuracy_all_wrong(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Positive momentum maintained",
                          week_label="2026-W13", config=cfg)
        # Actual return is strongly negative → Risk zone
        update_actual_return("005930", "2026-W13", -0.10, ACCURACY_WINDOW_FINAL, cfg)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_FINAL, config=cfg)
        assert result["accuracy"] == 0.0

    def test_partial_accuracy(self, tmp_path):
        cfg = self._make_config(tmp_path)
        for week in ["2026-W11", "2026-W12"]:
            record_prediction("005930", "Positive momentum maintained",
                              week_label=week, config=cfg)
        # First is correct (positive return), second is wrong (negative return)
        update_actual_return("005930", "2026-W11", 0.05, ACCURACY_WINDOW_FINAL, cfg)
        update_actual_return("005930", "2026-W12", -0.08, ACCURACY_WINDOW_FINAL, cfg)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_FINAL, config=cfg)
        assert result["accuracy"] == 0.5
        assert result["total"] == 2

    def test_preliminary_window_uses_4w_field(self, tmp_path):
        cfg = self._make_config(tmp_path)
        record_prediction("005930", "Risk zone", week_label="2026-W13", config=cfg)
        update_actual_return("005930", "2026-W13", -0.08, ACCURACY_WINDOW_PRELIMINARY, cfg)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_PRELIMINARY, config=cfg)
        assert result["window"] == ACCURACY_WINDOW_PRELIMINARY
        assert result["total"] == 1

    def test_unresolved_predictions_excluded(self, tmp_path):
        """Records without actual_return_8w are excluded from 8w accuracy."""
        cfg = self._make_config(tmp_path)
        for week in ["2026-W11", "2026-W12", "2026-W13"]:
            record_prediction("005930", "Positive momentum maintained",
                              week_label=week, config=cfg)
        # Only update one
        update_actual_return("005930", "2026-W11", 0.05, ACCURACY_WINDOW_FINAL, cfg)
        result = compute_accuracy("005930", window=ACCURACY_WINDOW_FINAL, config=cfg)
        assert result["total"] == 1  # Only 1 has 8w return

    def test_naive_baselines_in_result(self, tmp_path):
        cfg = self._make_config(tmp_path)
        result = compute_accuracy("005930", config=cfg)
        assert "naive_baselines" in result
        baselines = result["naive_baselines"]
        assert "always_bullish" in baselines
        assert "random" in baselines


# ── _compute_naive_baselines() ────────────────────────────────────────────────

class TestComputeNaiveBaselines:
    def test_empty_records_returns_none_accuracy(self):
        result = _compute_naive_baselines([], "actual_return_8w")
        assert result["always_bullish"] is None
        assert result["momentum"] is None

    def test_random_baseline_is_one_third(self):
        result = _compute_naive_baselines([], "actual_return_8w")
        # Code stores 1/3 as 0.333 literal
        assert abs(result["random"] - (1/3)) < 0.001

    def test_always_bullish_all_positive(self):
        records = [
            {"actual_return_8w": 0.05},
            {"actual_return_8w": 0.08},
            {"actual_return_8w": 0.03},
        ]
        result = _compute_naive_baselines(records, "actual_return_8w")
        # All positive momentum → always_bullish gets all 3 correct
        assert result["always_bullish"] == 1.0

    def test_always_bullish_none_positive(self):
        records = [
            {"actual_return_8w": -0.05},
            {"actual_return_8w": -0.08},
        ]
        result = _compute_naive_baselines(records, "actual_return_8w")
        assert result["always_bullish"] == 0.0

    def test_momentum_is_none(self):
        """Momentum baseline requires sequential context — computed externally."""
        records = [{"actual_return_8w": 0.05}]
        result = _compute_naive_baselines(records, "actual_return_8w")
        assert result["momentum"] is None
