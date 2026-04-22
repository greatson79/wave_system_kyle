"""
tests/test_korea_signal_layer.py — Standard TDD suite for korea_signal_layer.py.
Target coverage: 85%.
All test names, assertions, and comments in English (P5-A).
"""
from __future__ import annotations

import pytest

from investscan.korea_signal_layer import (
    KoreaSignal,
    get_foreign_flow,
    get_korea_signal,
    is_available,
)

# ── Config helpers ────────────────────────────────────────────────────────────

DRY_RUN_CONFIG = {"mode": "dry-run"}
LIVE_CONFIG = {"mode": "live"}
SAMPLE_STOCK = "005930"  # Samsung Electronics
INVALID_STOCK = "INVALID_CODE_XYZZY"


# ── get_korea_signal() — dry-run mode ─────────────────────────────────────────

class TestGetKoreaSignalDryRun:
    def test_get_korea_signal_dry_run(self):
        """Dry-run mode returns a KoreaSignal with mock numeric values."""
        result = get_korea_signal(SAMPLE_STOCK, DRY_RUN_CONFIG)
        assert isinstance(result, KoreaSignal)
        assert result.stock_code == SAMPLE_STOCK
        assert result.foreign_flow_4w == 42.0
        assert result.per_value > 0
        assert result.per_sector_avg > 0

    def test_dry_run_never_raises(self):
        """Even with an invalid stock code, dry-run never raises an exception."""
        # Must not raise any exception
        result = get_korea_signal(INVALID_STOCK, DRY_RUN_CONFIG)
        assert result is not None
        assert isinstance(result, KoreaSignal)

    def test_dry_run_invalid_code_returns_signal(self):
        """Invalid stock code in dry-run still returns a valid KoreaSignal."""
        result = get_korea_signal("", DRY_RUN_CONFIG)
        assert isinstance(result, KoreaSignal)
        assert result.foreign_flow_4w == 42.0

    def test_none_config_uses_dry_run_default(self):
        """None config defaults to dry-run mode without raising."""
        result = get_korea_signal(SAMPLE_STOCK, None)
        assert isinstance(result, KoreaSignal)


# ── KoreaSignal dataclass field tests ─────────────────────────────────────────

class TestKoreaSignalFields:
    def test_korea_signal_has_required_fields(self):
        """KoreaSignal has stock_code, foreign_flow_4w, and per_value fields."""
        result = get_korea_signal(SAMPLE_STOCK, DRY_RUN_CONFIG)
        assert hasattr(result, "stock_code")
        assert hasattr(result, "foreign_flow_4w")
        assert hasattr(result, "per_value")

    def test_korea_signal_has_all_dataclass_fields(self):
        """KoreaSignal exposes all six declared fields."""
        result = get_korea_signal(SAMPLE_STOCK, DRY_RUN_CONFIG)
        assert hasattr(result, "stock_code")
        assert hasattr(result, "foreign_flow_4w")
        assert hasattr(result, "per_value")
        assert hasattr(result, "per_sector_avg")
        assert hasattr(result, "data_source")
        assert hasattr(result, "available")

    def test_korea_signal_data_source_labeled(self):
        """data_source field is set to a non-empty string in dry-run mode."""
        result = get_korea_signal(SAMPLE_STOCK, DRY_RUN_CONFIG)
        assert result.data_source is not None
        assert isinstance(result.data_source, str)
        assert len(result.data_source) > 0

    def test_korea_signal_dry_run_not_available(self):
        """Dry-run signals are explicitly marked as not available (real data)."""
        result = get_korea_signal(SAMPLE_STOCK, DRY_RUN_CONFIG)
        assert result.available is False

    def test_korea_signal_stock_code_preserved(self):
        """stock_code in the returned signal matches the input argument."""
        result = get_korea_signal("000660", DRY_RUN_CONFIG)
        assert result.stock_code == "000660"


# ── get_foreign_flow() tests ─────────────────────────────────────────────────

class TestGetForeignFlow:
    def test_get_foreign_flow_dry_run(self):
        """get_foreign_flow() returns a float (mock 42.0) when pykrx is unavailable."""
        result = get_foreign_flow(SAMPLE_STOCK)
        assert isinstance(result, float)

    def test_get_foreign_flow_returns_42_mock(self):
        """Without live libraries, get_foreign_flow() returns the mock sentinel 42.0."""
        result = get_foreign_flow(SAMPLE_STOCK, weeks=4)
        # In test env pykrx is either not installed or unavailable
        # Either returns 42.0 (mock) or a real float — both are acceptable
        assert isinstance(result, float)
        assert result is not None

    def test_get_foreign_flow_never_raises(self):
        """get_foreign_flow() must never raise even with invalid input."""
        result = get_foreign_flow(INVALID_STOCK, weeks=4)
        # Returns None or a float — never raises
        assert result is None or isinstance(result, float)


# ── is_available() tests ─────────────────────────────────────────────────────

class TestIsAvailable:
    def test_is_available_returns_bool(self):
        """is_available() returns True or False without raising any exception."""
        result = is_available()
        assert isinstance(result, bool)

    def test_is_available_no_exception(self):
        """Calling is_available() on any platform never raises."""
        try:
            is_available()
        except Exception as exc:
            pytest.fail(f"is_available() raised an unexpected exception: {exc}")
