"""
tests/test_valuation_comparator.py — Tests for valuation_comparator.py.
Standard 85% coverage. English-First (P5-A).
"""
from __future__ import annotations

import pytest
from investscan.valuation_comparator import (
    ValuationResult,
    compare_valuation,
    format_yoy_growth,
    format_foreign_flow,
    DISCOUNT_THRESHOLD,
    PREMIUM_THRESHOLD,
)


class TestCompareValuation:
    def test_undervalued_discount(self):
        result = compare_valuation("005930", per_current=10.2, per_sector_avg=14.2)
        assert result.valuation_label == "undervalued"
        assert result.discount_pct > 0  # positive = discount

    def test_overvalued_premium(self):
        result = compare_valuation("035420", per_current=28.4, per_sector_avg=22.1)
        assert result.valuation_label in ("overvalued", "fairly_valued")

    def test_fairly_valued(self):
        result = compare_valuation("000660", per_current=14.5, per_sector_avg=15.0)
        assert result.valuation_label == "fairly_valued"

    def test_none_per_current_returns_unavailable(self):
        result = compare_valuation("005930", per_current=None, per_sector_avg=14.2)
        assert result.valuation_label == "unavailable"

    def test_none_per_sector_returns_unavailable(self):
        result = compare_valuation("005930", per_current=10.2, per_sector_avg=None)
        assert result.valuation_label == "unavailable"

    def test_zero_sector_avg_returns_unavailable(self):
        result = compare_valuation("005930", per_current=10.2, per_sector_avg=0.0)
        assert result.valuation_label == "unavailable"

    def test_formatted_summary_discount(self):
        result = compare_valuation("005930", per_current=10.2, per_sector_avg=14.2)
        assert "discount" in result.formatted_summary
        assert "10.2x" in result.formatted_summary

    def test_formatted_summary_premium(self):
        result = compare_valuation("035420", per_current=30.0, per_sector_avg=20.0)
        assert "premium" in result.formatted_summary

    def test_unavailable_summary_text(self):
        result = compare_valuation("005930", per_current=None, per_sector_avg=None)
        assert "unavailable" in result.formatted_summary.lower()

    def test_discount_threshold_constant(self):
        assert DISCOUNT_THRESHOLD == pytest.approx(0.10)

    def test_premium_threshold_constant(self):
        assert PREMIUM_THRESHOLD == pytest.approx(0.15)


class TestFormatYoyGrowth:
    def test_both_metrics_with_quarter(self):
        result = format_yoy_growth(0.083, 0.342, "2025Q4")
        assert "8.3%" in result
        assert "34.2%" in result
        assert "2025Q4" in result

    def test_positive_sign_shown(self):
        result = format_yoy_growth(0.05, 0.10, "2025Q3")
        assert "+" in result

    def test_negative_growth(self):
        result = format_yoy_growth(-0.05, -0.10)
        assert "-5.0%" in result or "-5%" in result

    def test_none_both_returns_unavailable(self):
        result = format_yoy_growth(None, None)
        assert "unavailable" in result.lower()

    def test_only_revenue_provided(self):
        result = format_yoy_growth(0.083, None)
        assert "8.3%" in result
        assert "Op.Income" not in result

    def test_no_quarter_label(self):
        result = format_yoy_growth(0.05, 0.08)
        assert "Q" not in result or "N/A" not in result


class TestFormatForeignFlow:
    def test_positive_flow_buy(self):
        result = format_foreign_flow(380.0)
        assert "buy" in result
        assert "+$380M" in result

    def test_negative_flow_sell(self):
        result = format_foreign_flow(-45.0)
        assert "sell" in result
        assert "$45M" in result

    def test_zero_flow_buy(self):
        result = format_foreign_flow(0.0)
        assert "buy" in result

    def test_none_returns_unavailable(self):
        result = format_foreign_flow(None)
        assert "unavailable" in result.lower()
