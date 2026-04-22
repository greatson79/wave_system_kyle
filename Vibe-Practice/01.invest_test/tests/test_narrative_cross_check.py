"""
tests/test_narrative_cross_check.py — Tests for narrative_cross_check.py (NBS).
Numeric Backstop: cross-verify LLM-generated financial numbers against input data.
P6 Python-First: all tests deterministic — no LLM calls.
English-First (P5-A).
"""
from __future__ import annotations

import pytest

from investscan.narrative_cross_check import (
    cross_check_narrative_numbers,
    DATA_UNAVAILABLE,
    DEFAULT_TOLERANCE,
    _is_available,
    _extract_floats,
    _any_within_tolerance,
    _fmt,
)
from investscan.schema import NarrativeOutput


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_narrative_a(**overrides) -> NarrativeOutput:
    defaults = dict(
        category="A",
        text="Samsung Electronics Q4 2025 investment analysis narrative.",
        sentiment_weight=0.0,
        yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)",
        per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x",
        foreign_flow_direction="4-week net buy: +$380M (cumulative)",
        downside_risk="DRAM oversupply → est. -12% revenue impact",
        direction="Positive momentum maintained",
    )
    defaults.update(overrides)
    return NarrativeOutput(**defaults)


def make_context_a(**overrides) -> dict:
    defaults = {
        "category": "A",
        "stock_code": "005930",
        "stock_name": "Samsung Electronics",
        "yoy_revenue_growth": 0.083,      # 8.3%
        "yoy_op_income_growth": 0.342,    # 34.2%
        "per_current": 10.2,
        "per_sector_avg": 14.2,
        "foreign_flow_4w": 380.0,
    }
    defaults.update(overrides)
    return defaults


def make_narrative_b(**overrides) -> NarrativeOutput:
    defaults = dict(
        category="B",
        text="NAVER AI commerce theme analysis.",
        sentiment_weight=0.0,
        market_size="Korean AI commerce market: $42bn, CAGR 19% (2025-2028)",
        stock_positioning="78% Korean search market share",
        catalyst="Q2 2026 AI shopping assistant launch",
        theme_duration="18-30 week momentum expected",
        dissolution_risk="Google AI Mode entry by Q4 2026",
        disclaimer="This does not constitute investment advice.",
    )
    defaults.update(overrides)
    return NarrativeOutput(**defaults)


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_data_unavailable_sentinel(self):
        assert DATA_UNAVAILABLE == "DATA_UNAVAILABLE"

    def test_default_tolerance_is_5_percent(self):
        assert DEFAULT_TOLERANCE == pytest.approx(0.05)


# ── _is_available() ───────────────────────────────────────────────────────────

class TestIsAvailable:
    def test_real_number_is_available(self):
        assert _is_available(8.3) is True

    def test_zero_is_available(self):
        assert _is_available(0.0) is True

    def test_none_is_not_available(self):
        assert _is_available(None) is False

    def test_data_unavailable_string_is_not_available(self):
        assert _is_available(DATA_UNAVAILABLE) is False

    def test_other_string_is_available(self):
        # Non-sentinel strings are technically "available" (caller decides interpretation)
        assert _is_available("some_value") is True

    def test_integer_is_available(self):
        assert _is_available(10) is True


# ── _extract_floats() ─────────────────────────────────────────────────────────

class TestExtractFloats:
    def test_extracts_percentage(self):
        result = _extract_floats("Revenue +8.3% YoY")
        assert 8.3 in result

    def test_extracts_multiple_numbers(self):
        result = _extract_floats("10.2x, 28.4% discount vs. 14.2x")
        assert 10.2 in result
        assert 28.4 in result
        assert 14.2 in result

    def test_extracts_integers(self):
        result = _extract_floats("net buy: +$380M (cumulative)")
        assert 380.0 in result

    def test_excludes_zeros(self):
        # Zeros are filtered (appear as punctuation artifacts)
        result = _extract_floats("year 2025, Q0 data")
        assert 0 not in result
        assert 0.0 not in result

    def test_empty_string_returns_empty(self):
        assert _extract_floats("") == []

    def test_no_numbers_returns_empty(self):
        assert _extract_floats("no numeric content here") == []

    def test_bounded_pattern_no_substring_extraction(self):
        # "10.2x" should extract 10.2 but not "0.2" as substring
        result = _extract_floats("10.2x")
        # Should contain 10.2, not include 0.2 as a standalone match
        assert 10.2 in result
        assert 0.2 not in result

    def test_negative_numbers_excluded(self):
        # Pattern only extracts positive values ((?<!\d)(\d+...))
        result = _extract_floats("-8.3%")
        assert all(v > 0 for v in result)


# ── _any_within_tolerance() ───────────────────────────────────────────────────

class TestAnyWithinTolerance:
    def test_exact_match(self):
        assert _any_within_tolerance(8.3, [8.3], 0.05) is True

    def test_within_5_percent(self):
        # 8.27 is within 5% of 8.3
        assert _any_within_tolerance(8.3, [8.27], 0.05) is True

    def test_just_outside_5_percent(self):
        # 7.8 is 6% below 8.3 — outside tolerance
        assert _any_within_tolerance(8.3, [7.8], 0.05) is False

    def test_multiple_candidates_one_matches(self):
        assert _any_within_tolerance(8.3, [1.0, 8.31, 100.0], 0.05) is True

    def test_no_candidates_match(self):
        assert _any_within_tolerance(8.3, [1.0, 50.0, 200.0], 0.05) is False

    def test_expected_near_zero_uses_absolute_tolerance(self):
        # Expected ≈ 0 → use absolute tolerance of 0.1
        assert _any_within_tolerance(0.0, [0.05], 0.05) is True
        assert _any_within_tolerance(0.0, [0.5], 0.05) is False

    def test_empty_candidates(self):
        assert _any_within_tolerance(8.3, [], 0.05) is False

    def test_large_value_tolerance(self):
        # 380M ± 5% = 361-399
        assert _any_within_tolerance(380.0, [379.9], 0.05) is True
        assert _any_within_tolerance(380.0, [300.0], 0.05) is False


# ── _fmt() ────────────────────────────────────────────────────────────────────

class TestFmt:
    def test_formats_floats(self):
        result = _fmt([8.3, 34.2, 380.0])
        assert "8.30" in result
        assert "34.20" in result
        assert "380.00" in result

    def test_caps_at_5_values(self):
        result = _fmt([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
        # Only first 5 appear
        assert "6.00" not in result

    def test_empty_list(self):
        result = _fmt([])
        assert result == "[]"


# ── cross_check_narrative_numbers() — Category B skip ─────────────────────────

class TestCategoryBSkipped:
    def test_category_b_returns_empty_errors(self):
        narrative = make_narrative_b()
        context = {"per_current": 10.2, "yoy_revenue_growth": 0.083}
        errors = cross_check_narrative_numbers(narrative, context)
        assert errors == []

    def test_category_b_no_check_even_with_wrong_values(self):
        # Category B has qualitative fields — never checked
        narrative = make_narrative_b(
            market_size="$999bn CAGR 99%"  # wildly wrong but B is skipped
        )
        context = {"some_data": 1.0}
        errors = cross_check_narrative_numbers(narrative, context)
        assert errors == []


# ── cross_check_narrative_numbers() — NBS-01 (yoy_growth) ────────────────────

class TestNBS01YoyGrowth:
    def test_correct_yoy_growth_passes(self):
        # Default make_narrative_a() has both revenue +8.3% AND Op.Income +34.2%
        # → both NBS-01 and NBS-01b pass
        narrative = make_narrative_a()
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01:" in e for e in errors)

    def test_mismatched_yoy_growth_fails(self):
        # narrative says 8.3%, context says 25% — NBS-01 fires
        # Include op.income (34.2%) to prevent NBS-01b from also firing
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.25)  # 25%, not 8.3%
        errors = cross_check_narrative_numbers(narrative, context)
        assert any("NBS-01:" in e for e in errors)

    def test_yoy_growth_within_tolerance_passes(self):
        # 8.27% is within 5% of 8.3%; include op.income so NBS-01b also satisfied
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.27% YoY, Op.Income +34.2% (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.083)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01:" in e for e in errors)

    def test_data_unavailable_yoy_skipped(self):
        # Both revenue AND op.income unavailable → both NBS-01 and NBS-01b skip
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY (2025Q4)"
        )
        context = make_context_a(
            yoy_revenue_growth=DATA_UNAVAILABLE,
            yoy_op_income_growth=DATA_UNAVAILABLE,
        )
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01" in e for e in errors)

    def test_none_yoy_skipped(self):
        # Both revenue AND op.income None → both checks skip
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=None, yoy_op_income_growth=None)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01" in e for e in errors)

    def test_empty_yoy_growth_field_skipped(self):
        # Empty field → neither NBS-01 nor NBS-01b run
        narrative = make_narrative_a(yoy_growth="")
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01" in e for e in errors)

    def test_yoy_decimal_to_percent_conversion(self):
        # context has 0.083 → 8.3%, 0.342 → 34.2%; narrative includes both
        # Tests that decimal-to-percent conversion (×100) works for both anchors
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.083, yoy_op_income_growth=0.342)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01" in e for e in errors)


# ── cross_check_narrative_numbers() — NBS-01b (yoy_op_income) ────────────────

class TestNBS01bOpIncomeGrowth:
    def test_correct_op_income_passes(self):
        narrative = make_narrative_a()  # "Op.Income +34.2% (2025Q4)"
        context = make_context_a()     # yoy_op_income_growth=0.342 → 34.2%
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01b" in e for e in errors)

    def test_hallucinated_op_income_caught(self):
        # Revenue correct (8.3%), but op.income hallucinated (99.9%)
        # NBS-01 passes (8.3 found), NBS-01b catches (34.2 not found)
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +99.9% (2025Q4)"
        )
        context = make_context_a()  # yoy_op_income_growth=0.342 → 34.2%
        errors = cross_check_narrative_numbers(narrative, context)
        assert any("NBS-01b" in e for e in errors)

    def test_nbs01_passes_while_nbs01b_fails(self):
        # Confirms independence: NBS-01 PASS + NBS-01b FAIL can coexist
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +99.9% (2025Q4)"
        )
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01:" in e for e in errors)   # revenue ok
        assert any("NBS-01b" in e for e in errors)       # op.income caught

    def test_op_income_within_tolerance_passes(self):
        # 34.0% is within 5% of 34.2%
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.0% (2025Q4)"
        )
        context = make_context_a(yoy_op_income_growth=0.342)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01b" in e for e in errors)

    def test_data_unavailable_op_income_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(yoy_op_income_growth=DATA_UNAVAILABLE)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01b" in e for e in errors)

    def test_none_op_income_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(yoy_op_income_growth=None)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-01b" in e for e in errors)


# ── cross_check_narrative_numbers() — NBS-02 (per_vs_sector) ─────────────────

class TestNBS02PerVsSector:
    def test_correct_per_passes(self):
        narrative = make_narrative_a()
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-02" in e for e in errors)

    def test_mismatched_per_fails(self):
        narrative = make_narrative_a(
            per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x"
        )
        context = make_context_a(per_current=25.0)  # 25x, not 10.2x
        errors = cross_check_narrative_numbers(narrative, context)
        assert any("NBS-02" in e for e in errors)

    def test_per_within_tolerance_passes(self):
        # 10.18x is within 5% of 10.2x
        narrative = make_narrative_a(
            per_vs_sector="10.18x, discount vs. sector avg"
        )
        context = make_context_a(per_current=10.2)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-02" in e for e in errors)

    def test_data_unavailable_per_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(per_current=DATA_UNAVAILABLE)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-02" in e for e in errors)

    def test_none_per_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(per_current=None)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-02" in e for e in errors)


# ── cross_check_narrative_numbers() — NBS-03 (foreign_flow) ──────────────────

class TestNBS03ForeignFlow:
    def test_correct_flow_passes(self):
        narrative = make_narrative_a()
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-03" in e for e in errors)

    def test_mismatched_flow_fails(self):
        narrative = make_narrative_a(
            foreign_flow_direction="4-week net buy: +$380M (cumulative)"
        )
        context = make_context_a(foreign_flow_4w=50.0)  # 50M, not 380M
        errors = cross_check_narrative_numbers(narrative, context)
        assert any("NBS-03" in e for e in errors)

    def test_negative_flow_absolute_comparison(self):
        # context=-380.0 (net sell), narrative says "380" → abs comparison → match
        narrative = make_narrative_a(
            foreign_flow_direction="4-week net sell: 380M (cumulative)"
        )
        context = make_context_a(foreign_flow_4w=-380.0)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-03" in e for e in errors)

    def test_data_unavailable_flow_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(foreign_flow_4w=DATA_UNAVAILABLE)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-03" in e for e in errors)

    def test_none_flow_skipped(self):
        narrative = make_narrative_a()
        context = make_context_a(foreign_flow_4w=None)
        errors = cross_check_narrative_numbers(narrative, context)
        assert not any("NBS-03" in e for e in errors)


# ── cross_check_narrative_numbers() — full pass/fail integration ──────────────

class TestCrossCheckIntegration:
    def test_all_fields_match_returns_empty_errors(self):
        narrative = make_narrative_a()
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        assert errors == []

    def test_returns_list(self):
        narrative = make_narrative_a()
        context = make_context_a()
        result = cross_check_narrative_numbers(narrative, context)
        assert isinstance(result, list)

    def test_error_messages_contain_field_id(self):
        # Revenue wrong (50% vs 8.3%), op.income correct → only NBS-01 fires
        narrative = make_narrative_a(
            yoy_growth="Revenue +50.0% YoY, Op.Income +34.2% (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.083, yoy_op_income_growth=0.342)
        errors = cross_check_narrative_numbers(narrative, context)
        assert len(errors) == 1
        assert "NBS-01:" in errors[0]  # colon to distinguish from NBS-01b

    def test_multiple_mismatches_returns_multiple_errors(self):
        # Revenue wrong + per wrong → NBS-01 + NBS-02 fire; op.income wrong → NBS-01b too
        narrative = make_narrative_a(
            yoy_growth="Revenue +50.0% YoY, Op.Income +50.0% (2025Q4)",
            per_vs_sector="99.9x vs. sector",
        )
        context = make_context_a(
            yoy_revenue_growth=0.083,
            yoy_op_income_growth=0.342,
            per_current=10.2,
        )
        errors = cross_check_narrative_numbers(narrative, context)
        assert len(errors) >= 2

    def test_nbs01b_independent_from_nbs01(self):
        # Revenue correct → NBS-01 passes; op.income hallucinated → NBS-01b fires
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.3% YoY, Op.Income +99.9% (2025Q4)"
        )
        context = make_context_a()
        errors = cross_check_narrative_numbers(narrative, context)
        nbs01_ids = [e for e in errors if "NBS-01:" in e]   # colon: exact match
        nbs01b_ids = [e for e in errors if "NBS-01b" in e]
        assert len(nbs01_ids) == 0   # revenue was correct
        assert len(nbs01b_ids) == 1  # op.income was hallucinated

    def test_custom_tolerance_accepted(self):
        # At 1% tolerance, 8.27% (0.36% off) and 34.0% (0.58% off) both pass
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.27% YoY, Op.Income +34.0% (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.083, yoy_op_income_growth=0.342)
        errors = cross_check_narrative_numbers(narrative, context, tolerance=0.01)
        assert not any("NBS-01" in e for e in errors)

    def test_zero_tolerance_strict(self):
        # At 0% tolerance, 8.27 vs 8.3 fails NBS-01
        # Disable op.income to isolate NBS-01 failure
        narrative = make_narrative_a(
            yoy_growth="Revenue +8.27% YoY (2025Q4)"
        )
        context = make_context_a(yoy_revenue_growth=0.083, yoy_op_income_growth=None)
        errors = cross_check_narrative_numbers(narrative, context, tolerance=0.0)
        assert any("NBS-01:" in e for e in errors)

    def test_does_not_raise_exceptions(self):
        # NBS must not raise — caller decides retry logic
        try:
            cross_check_narrative_numbers(make_narrative_a(), make_context_a())
        except Exception as e:
            pytest.fail(f"cross_check_narrative_numbers raised: {e}")

    def test_empty_context_passes_all(self):
        # No context → no ground truth → no errors
        narrative = make_narrative_a()
        errors = cross_check_narrative_numbers(narrative, {})
        assert errors == []
