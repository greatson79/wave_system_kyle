"""
tests/test_synthesize_macro.py — P1 Critical TDD suite for synthesize_macro.py.
Target coverage: 95%.
All test names, assertions, and comments in English (P5-A).
"""
from __future__ import annotations

import os
import pytest

from investscan.schema import InvestmentMeta
from investscan.synthesize_macro import (
    get_series_value,
    load_fred_fixture,
    synthesize,
)

# ── Fixture path helper ───────────────────────────────────────────────────────
FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "fred_sample.json"
)


def _make_fred(overrides: dict | None = None) -> dict:
    """Build a minimal FRED data dict, optionally overriding series values."""
    base = {
        "series": {
            "DFF": {"value": 5.25, "available": True},
            "FEDFUNDS": {"value": 5.25, "available": True},
            "T10YIE": {"value": 2.31, "available": True},
            "CPIAUCSL": {"value": 2.8, "available": True},
            "VIXCLS": {"value": 18.42, "available": True},
            "BAMLH0A0HYM2": {"value": 3.21, "available": True},
            "DTWEXBGS": {"value": 106.8, "available": True},
        }
    }
    if overrides:
        for series_id, value in overrides.items():
            if series_id in base["series"]:
                base["series"][series_id]["value"] = value
            else:
                base["series"][series_id] = {"value": value, "available": True}
    return base


# ── synthesize() integration tests ───────────────────────────────────────────

class TestSynthesizeFromFixture:
    """Load the real fred_sample.json fixture and verify InvestmentMeta fields."""

    def test_synthesize_from_fixture(self):
        """synthesize() with real fixture → valid InvestmentMeta with expected values."""
        fred_data = load_fred_fixture(FIXTURE_PATH)
        result = synthesize(fred_data)

        assert isinstance(result, InvestmentMeta)
        assert result.rate_direction in ("cut", "hold", "hike")
        assert result.inflation_trend in ("rising", "cooling", "stable")
        assert result.risk_appetite in ("low", "moderate", "high")
        assert result.usd_strength in ("weak", "neutral", "strong")
        assert isinstance(result.sector_directions, dict)
        assert result.generated_at != ""

    def test_synthesize_returns_investment_meta_type(self):
        """synthesize() must return an InvestmentMeta instance."""
        fred_data = load_fred_fixture(FIXTURE_PATH)
        result = synthesize(fred_data)
        assert isinstance(result, InvestmentMeta)

    def test_sentiment_weight_not_in_output(self):
        """InvestmentMeta must not have a sentiment_weight field (sentinel belongs to NarrativeOutput)."""
        fred_data = load_fred_fixture(FIXTURE_PATH)
        result = synthesize(fred_data)
        assert not hasattr(result, "sentiment_weight"), (
            "InvestmentMeta must not carry sentiment_weight — it belongs to NarrativeOutput only"
        )


# ── rate_direction tests ──────────────────────────────────────────────────────

class TestRateDirection:
    def test_rate_direction_hold(self):
        """DFF=5.25 with T10YIE=2.31 (below 2.5) → 'hold'."""
        fred_data = _make_fred({"DFF": 5.25, "T10YIE": 2.31})
        result = synthesize(fred_data)
        assert result.rate_direction == "hold"

    def test_rate_direction_cut(self):
        """DFF=2.5 (below 3.0 threshold) → 'cut'."""
        fred_data = _make_fred({"DFF": 2.5, "T10YIE": 2.0})
        result = synthesize(fred_data)
        assert result.rate_direction == "cut"

    def test_rate_direction_hike(self):
        """DFF=5.5 AND T10YIE=3.0 (both above hike thresholds) → 'hike'."""
        fred_data = _make_fred({"DFF": 5.5, "T10YIE": 3.0})
        result = synthesize(fred_data)
        assert result.rate_direction == "hike"

    def test_rate_direction_cut_at_exactly_3(self):
        """DFF exactly at 3.0 → 'cut' (boundary: <= 3.0)."""
        fred_data = _make_fred({"DFF": 3.0, "T10YIE": 2.0})
        result = synthesize(fred_data)
        assert result.rate_direction == "cut"

    def test_rate_direction_hike_requires_both_conditions(self):
        """DFF=5.5 but T10YIE=2.3 (below 2.5) → NOT 'hike' (hold)."""
        fred_data = _make_fred({"DFF": 5.5, "T10YIE": 2.3})
        result = synthesize(fred_data)
        assert result.rate_direction == "hold"


# ── inflation_trend tests ─────────────────────────────────────────────────────

class TestInflationTrend:
    def test_inflation_cooling(self):
        """CPIAUCSL=2.8 (fixture value, <= 3.0) → 'cooling'."""
        fred_data = _make_fred({"CPIAUCSL": 2.8})
        result = synthesize(fred_data)
        assert result.inflation_trend == "cooling"

    def test_inflation_rising(self):
        """CPIAUCSL=4.0 (above 3.5) → 'rising'."""
        fred_data = _make_fred({"CPIAUCSL": 4.0})
        result = synthesize(fred_data)
        assert result.inflation_trend == "rising"

    def test_inflation_stable(self):
        """CPIAUCSL=3.0 is at boundary (<= 3.0) so goes cooling; 3.2 → 'stable'."""
        fred_data = _make_fred({"CPIAUCSL": 3.2})
        result = synthesize(fred_data)
        assert result.inflation_trend == "stable"

    def test_inflation_stable_mid_range(self):
        """CPIAUCSL=3.2 is between cooling threshold (3.0) and rising threshold (3.5) → 'stable'."""
        fred_data = _make_fred({"CPIAUCSL": 3.2})
        result = synthesize(fred_data)
        assert result.inflation_trend == "stable"

    def test_inflation_cooling_boundary(self):
        """CPIAUCSL exactly at 3.0 boundary → 'cooling' (inclusive)."""
        fred_data = _make_fred({"CPIAUCSL": 3.0})
        result = synthesize(fred_data)
        assert result.inflation_trend == "cooling"

    def test_inflation_rising_boundary(self):
        """CPIAUCSL just above 3.5 → 'rising'."""
        fred_data = _make_fred({"CPIAUCSL": 3.51})
        result = synthesize(fred_data)
        assert result.inflation_trend == "rising"


# ── risk_appetite tests ───────────────────────────────────────────────────────

class TestRiskAppetite:
    def test_risk_appetite_moderate(self):
        """VIX=18.42, OAS=3.21 (fixture values) → 'moderate'."""
        fred_data = _make_fred({"VIXCLS": 18.42, "BAMLH0A0HYM2": 3.21})
        result = synthesize(fred_data)
        assert result.risk_appetite == "moderate"

    def test_risk_appetite_high(self):
        """VIX=12.0 (< 15) AND OAS=2.5 (< 3.0) → 'high'."""
        fred_data = _make_fred({"VIXCLS": 12.0, "BAMLH0A0HYM2": 2.5})
        result = synthesize(fred_data)
        assert result.risk_appetite == "high"

    def test_risk_appetite_low_vix(self):
        """VIX=30.0 (> 25) → 'low'."""
        fred_data = _make_fred({"VIXCLS": 30.0, "BAMLH0A0HYM2": 3.5})
        result = synthesize(fred_data)
        assert result.risk_appetite == "low"

    def test_risk_appetite_low_oas(self):
        """OAS=6.0 (> 5.0) → 'low' regardless of VIX."""
        fred_data = _make_fred({"VIXCLS": 20.0, "BAMLH0A0HYM2": 6.0})
        result = synthesize(fred_data)
        assert result.risk_appetite == "low"

    def test_risk_appetite_high_requires_both_vix_and_oas(self):
        """VIX=12.0 (< 15) but OAS=4.0 (>= 3.0) → NOT 'high' (moderate)."""
        fred_data = _make_fred({"VIXCLS": 12.0, "BAMLH0A0HYM2": 4.0})
        result = synthesize(fred_data)
        assert result.risk_appetite == "moderate"


# ── usd_strength tests ────────────────────────────────────────────────────────

class TestUsdStrength:
    def test_usd_strong(self):
        """DTWEXBGS=106.8 (fixture value, > 105) → 'strong'."""
        fred_data = _make_fred({"DTWEXBGS": 106.8})
        result = synthesize(fred_data)
        assert result.usd_strength == "strong"

    def test_usd_weak(self):
        """DTWEXBGS=90.0 (< 95) → 'weak'."""
        fred_data = _make_fred({"DTWEXBGS": 90.0})
        result = synthesize(fred_data)
        assert result.usd_strength == "weak"

    def test_usd_neutral(self):
        """DTWEXBGS=100.0 (between 95 and 105) → 'neutral'."""
        fred_data = _make_fred({"DTWEXBGS": 100.0})
        result = synthesize(fred_data)
        assert result.usd_strength == "neutral"

    def test_usd_strong_boundary(self):
        """DTWEXBGS just above 105 → 'strong'."""
        fred_data = _make_fred({"DTWEXBGS": 105.1})
        result = synthesize(fred_data)
        assert result.usd_strength == "strong"

    def test_usd_weak_boundary(self):
        """DTWEXBGS just below 95 → 'weak'."""
        fred_data = _make_fred({"DTWEXBGS": 94.9})
        result = synthesize(fred_data)
        assert result.usd_strength == "weak"


# ── get_series_value() tests ──────────────────────────────────────────────────

class TestGetSeriesValue:
    def test_get_series_value_exists(self):
        """Extracts correct float value for an existing series."""
        fred_data = {"series": {"DFF": {"value": 5.25, "available": True}}}
        result = get_series_value(fred_data, "DFF")
        assert result == 5.25
        assert isinstance(result, float)

    def test_get_series_value_missing(self):
        """Returns None when series_id is not in fred_data."""
        fred_data = {"series": {}}
        result = get_series_value(fred_data, "NONEXISTENT")
        assert result is None

    def test_get_series_value_unavailable(self):
        """Returns None when series exists but available=False."""
        fred_data = {"series": {"DFF": {"value": 5.25, "available": False}}}
        result = get_series_value(fred_data, "DFF")
        assert result is None

    def test_get_series_value_no_series_key(self):
        """Returns None when fred_data has no 'series' key."""
        result = get_series_value({}, "DFF")
        assert result is None

    def test_get_series_value_null_value(self):
        """Returns None when value is explicitly None in fixture."""
        fred_data = {"series": {"DFF": {"value": None, "available": True}}}
        result = get_series_value(fred_data, "DFF")
        assert result is None

    def test_get_series_value_integer_converted_to_float(self):
        """Integer values are correctly cast to float."""
        fred_data = {"series": {"DFF": {"value": 5, "available": True}}}
        result = get_series_value(fred_data, "DFF")
        assert result == 5.0
        assert isinstance(result, float)
