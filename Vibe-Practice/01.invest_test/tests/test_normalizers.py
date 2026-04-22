"""
tests/test_normalizers.py — Unit tests for investscan.normalizers module.
Core Pipeline coverage target: 90%.
All test code and messages in English (P5-A).
"""
from __future__ import annotations

import json
import logging
import os

import pytest

from investscan.normalizers import load_envscan_file, normalize_envscan
from investscan.schema import UnifiedSignal

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
_ENVSCAN_FIXTURE = os.path.join(_FIXTURE_DIR, "envscan_sample.json")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def envscan_data() -> dict:
    """Return the parsed envscan_sample.json dict."""
    return load_envscan_file(_ENVSCAN_FIXTURE)


# ---------------------------------------------------------------------------
# test_normalize_envscan_full_fixture
# ---------------------------------------------------------------------------

def test_normalize_envscan_full_fixture(envscan_data):
    """normalize_envscan() on the 6-entry fixture must return exactly 6 UnifiedSignals."""
    signals = normalize_envscan(envscan_data)
    assert len(signals) == 6, f"Expected 6 signals, got {len(signals)}"


# ---------------------------------------------------------------------------
# test_normalize_sets_correct_steeps
# ---------------------------------------------------------------------------

def test_normalize_sets_correct_steeps(envscan_data):
    """Each UnifiedSignal must carry the steeps_category from the source entry."""
    signals = normalize_envscan(envscan_data)
    expected_categories = {"T", "E_env", "S", "s", "P", "E"}
    actual_categories = {s.steeps_category for s in signals}
    assert actual_categories == expected_categories, (
        f"Expected categories {expected_categories}, got {actual_categories}"
    )


# ---------------------------------------------------------------------------
# test_normalize_psst_score_in_range
# ---------------------------------------------------------------------------

def test_normalize_psst_score_in_range(envscan_data):
    """All psst_score values must be in the [0, 100] range."""
    signals = normalize_envscan(envscan_data)
    for sig in signals:
        assert 0.0 <= sig.psst_score <= 100.0, (
            f"psst_score out of range for {sig.steeps_category}: {sig.psst_score}"
        )


# ---------------------------------------------------------------------------
# test_normalize_skips_invalid_entry
# ---------------------------------------------------------------------------

def test_normalize_skips_invalid_entry(caplog):
    """An entry missing the psst_field must be skipped with a WARNING log."""
    data = {
        "entries": [
            {
                "steeps_category": "T",
                # pSST is intentionally missing
                "summary": "AI semiconductor demand.",
                "sector": "technology",
                "confidence": 0.85,
                "date": "2026-03-28",
            }
        ],
        "schema": {
            "steeps_field": "steeps_category",
            "psst_field": "pSST",
            "summary_field": "summary",
        },
    }
    with caplog.at_level(logging.WARNING, logger="investscan.normalizers"):
        signals = normalize_envscan(data)

    assert len(signals) == 0, "Skipped entry should result in empty list"
    assert any("pSST" in record.message or "missing" in record.message.lower()
               for record in caplog.records), "Expected a WARNING about missing psst field"


# ---------------------------------------------------------------------------
# test_load_envscan_file_success
# ---------------------------------------------------------------------------

def test_load_envscan_file_success():
    """load_envscan_file() must return a dict for the sample fixture."""
    data = load_envscan_file(_ENVSCAN_FIXTURE)
    assert isinstance(data, dict), f"Expected dict, got {type(data).__name__}"
    assert "entries" in data, "Expected 'entries' key in loaded data"


# ---------------------------------------------------------------------------
# test_load_envscan_file_not_found
# ---------------------------------------------------------------------------

def test_load_envscan_file_not_found():
    """load_envscan_file() must raise FileNotFoundError for a non-existent path."""
    with pytest.raises(FileNotFoundError):
        load_envscan_file("/nonexistent/path/does_not_exist.json")


# ---------------------------------------------------------------------------
# test_normalize_empty_entries
# ---------------------------------------------------------------------------

def test_normalize_empty_entries():
    """normalize_envscan() with an empty entries list must return an empty list."""
    data: dict = {"entries": [], "schema": {}}
    signals = normalize_envscan(data)
    assert signals == [], f"Expected empty list, got {signals}"


# ---------------------------------------------------------------------------
# test_normalize_uses_schema_hints
# ---------------------------------------------------------------------------

def test_normalize_uses_schema_hints():
    """Caller-supplied schema_hints must override field name mapping."""
    data = {
        "entries": [
            {
                "category_code": "T",
                "score": 80.0,
                "text": "AI chip demand rising.",
                "sector": "technology",
                "confidence": 0.9,
                "date": "2026-03-28",
            }
        ]
        # No "schema" block — all mapping comes from schema_hints
    }
    hints = {
        "steeps_field": "category_code",
        "psst_field": "score",
        "summary_field": "text",
        "score_scale": "0-100",
    }
    signals = normalize_envscan(data, schema_hints=hints)
    assert len(signals) == 1
    assert signals[0].steeps_category == "T"
    assert signals[0].psst_score == 80.0
    assert signals[0].summary == "AI chip demand rising."


# ---------------------------------------------------------------------------
# test_unified_signal_fields
# ---------------------------------------------------------------------------

def test_unified_signal_fields(envscan_data):
    """Every UnifiedSignal must have all required fields populated."""
    signals = normalize_envscan(envscan_data)
    required_attrs = ("steeps_category", "psst_score", "summary", "sector", "confidence", "date", "source")
    for sig in signals:
        for attr in required_attrs:
            value = getattr(sig, attr)
            assert value is not None, f"Field '{attr}' is None for signal: {sig}"


# ---------------------------------------------------------------------------
# Additional edge-case tests for coverage completeness
# ---------------------------------------------------------------------------

def test_normalize_missing_steeps_field_skips(caplog):
    """An entry missing steeps_category must be skipped with a WARNING."""
    data = {
        "entries": [
            {
                # steeps_category is missing
                "pSST": 55.0,
                "summary": "Some text.",
                "sector": "finance",
                "confidence": 0.7,
                "date": "2026-03-28",
            }
        ]
    }
    with caplog.at_level(logging.WARNING, logger="investscan.normalizers"):
        signals = normalize_envscan(data)
    assert len(signals) == 0


def test_normalize_missing_summary_field_skips(caplog):
    """An entry missing the summary field must be skipped with a WARNING."""
    data = {
        "entries": [
            {
                "steeps_category": "E",
                "pSST": 55.0,
                # summary is missing
                "sector": "finance",
                "confidence": 0.7,
                "date": "2026-03-28",
            }
        ]
    }
    with caplog.at_level(logging.WARNING, logger="investscan.normalizers"):
        signals = normalize_envscan(data)
    assert len(signals) == 0


def test_normalize_invalid_json_raises(tmp_path):
    """load_envscan_file() raises ValueError for non-JSON content."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json {{{{")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_envscan_file(str(bad_file))


def test_normalize_score_scale_0_1():
    """Score on 0-1 scale must be multiplied by 100."""
    data = {
        "entries": [
            {
                "steeps_category": "T",
                "pSST": 0.72,
                "summary": "AI chip.",
                "sector": "technology",
                "confidence": 0.85,
                "date": "2026-03-28",
            }
        ],
        "schema": {
            "steeps_field": "steeps_category",
            "psst_field": "pSST",
            "summary_field": "summary",
            "score_scale": "0-1",
        },
    }
    signals = normalize_envscan(data)
    assert len(signals) == 1
    assert abs(signals[0].psst_score - 72.0) < 0.01
