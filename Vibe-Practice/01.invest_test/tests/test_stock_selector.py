"""
tests/test_stock_selector.py — P1 Critical TDD suite for stock_selector.py.
Target coverage: 95%.
All test names, assertions, and comments in English (P5-A).
"""
from __future__ import annotations

import inspect

import pytest

from investscan.stock_selector import (
    BULLISH_THRESHOLD,
    CATEGORY_B_MIN_THEME_WEEKS,
    MIN_ABS_COUNT,
    MIN_WEEKS_TRACKED,
    NEUTRAL_BAND,
    StockClassification,
    classify_category,
    get_direction,
)

# ── Helper factories ─────────────────────────────────────────────────────────

def _make_financials(
    weeks_tracked: int = 4,
    abs_count: int = 1,
    yoy_revenue: float = 0.12,
) -> dict:
    return {
        "weeks_tracked": weeks_tracked,
        "abs_count": abs_count,
        "yoy_revenue": yoy_revenue,
    }


def _make_theme(
    theme_weeks: int = 4,
    abs_count: int = 2,
    avg_count: float = 1.5,
    market_size: str = "Global AI infra: $180bn",
) -> dict:
    return {
        "theme_weeks": theme_weeks,
        "abs_count": abs_count,
        "avg_count": avg_count,
        "market_size": market_size,
    }


# ── classify_category() — Category A ─────────────────────────────────────────

class TestClassifyCategoryA:
    def test_classify_category_a_with_financials(self):
        """financial_history with weeks_tracked >= 4 → 'A'."""
        result = classify_category("005930", _make_financials(weeks_tracked=4), None)
        assert result == "A"

    def test_classify_category_a_with_large_weeks(self):
        """financial_history with weeks_tracked=52 → 'A'."""
        result = classify_category("005930", _make_financials(weeks_tracked=52), None)
        assert result == "A"

    def test_classify_prefers_a_when_both(self):
        """When both financial_history AND theme_data are valid → 'A' (financials take precedence)."""
        result = classify_category(
            "005930",
            _make_financials(weeks_tracked=8),
            _make_theme(theme_weeks=8),
        )
        assert result == "A"

    def test_classify_a_requires_yoy_revenue(self):
        """financial_history without yoy_revenue → NOT 'A'."""
        fin = {"weeks_tracked": 8, "abs_count": 2, "yoy_revenue": None}
        result = classify_category("005930", fin, None)
        # yoy_revenue is None → invalid financials → should not be "A"
        assert result != "A"


# ── classify_category() — Category B ─────────────────────────────────────────

class TestClassifyCategoryB:
    def test_classify_category_b_with_theme(self):
        """theme_data with theme_weeks >= 4 → 'B'."""
        result = classify_category("themed_stock", None, _make_theme(theme_weeks=4))
        assert result == "B"

    def test_classify_category_b_large_theme_weeks(self):
        """theme_data with theme_weeks=24 → 'B'."""
        result = classify_category("themed_stock", None, _make_theme(theme_weeks=24))
        assert result == "B"

    def test_classify_category_b_min_weeks_threshold(self):
        """theme_weeks < 4 → NOT 'B' (insufficient theme tracking)."""
        result = classify_category("themed_stock", None, _make_theme(theme_weeks=3))
        assert result != "B"

    def test_classify_category_b_zero_guard_weeks_tracked(self):
        """theme_weeks=0 → NOT 'B' (v3.6 I-7 zero guard)."""
        result = classify_category("themed_stock", None, _make_theme(theme_weeks=0))
        assert result != "B"

    def test_classify_category_b_zero_guard_abs_count(self):
        """abs_count=0 in theme_data → NOT 'B' (v3.6 I-7 absolute safety net)."""
        theme = _make_theme(theme_weeks=8, abs_count=0)
        result = classify_category("themed_stock", None, theme)
        assert result != "B"

    def test_classify_category_b_requires_market_size(self):
        """theme_data without market_size → NOT 'B'."""
        theme = {"theme_weeks": 8, "abs_count": 2, "avg_count": 1.5, "market_size": None}
        result = classify_category("themed_stock", None, theme)
        assert result != "B"


# ── classify_category() — unknown ────────────────────────────────────────────

class TestClassifyUnknown:
    def test_classify_unknown_when_neither(self):
        """No financial_history AND no theme_data → 'unknown'."""
        result = classify_category("unknown_stock", None, None)
        assert result == "unknown"

    def test_classify_unknown_empty_dicts(self):
        """Empty dicts for both financial_history and theme_data → 'unknown'."""
        result = classify_category("unknown_stock", {}, {})
        assert result == "unknown"

    def test_classify_unknown_insufficient_financials(self):
        """financial_history with weeks_tracked < 4 and no valid theme → 'unknown'."""
        fin = _make_financials(weeks_tracked=2)
        result = classify_category("stock", fin, None)
        assert result == "unknown"

    def test_classify_unknown_financials_insufficient_weeks_no_theme(self):
        """weeks_tracked=1 with no theme → 'unknown'."""
        fin = _make_financials(weeks_tracked=1)
        result = classify_category("stock", fin, None)
        assert result == "unknown"


# ── get_direction() tests ─────────────────────────────────────────────────────

class TestGetDirection:
    def test_get_direction_bullish(self):
        """return_4w=0.05 (+5%) > BULLISH_THRESHOLD (+1%) → 'Positive momentum maintained'."""
        result = get_direction(0.05)
        assert result == "Positive momentum maintained"

    def test_get_direction_neutral(self):
        """return_4w=0.005 (within ±3% neutral band) → 'Neutral — monitor and wait'."""
        result = get_direction(0.005)
        assert result == "Neutral — monitor and wait"

    def test_get_direction_risk_zone(self):
        """return_4w=-0.05 (-5%) < -NEUTRAL_BAND → 'Risk zone'."""
        result = get_direction(-0.05)
        assert result == "Risk zone"

    def test_get_direction_at_bullish_threshold(self):
        """return_4w exactly at BULLISH_THRESHOLD (0.01) is NOT > threshold → neutral."""
        result = get_direction(BULLISH_THRESHOLD)
        # 0.01 is NOT > 0.01, and abs(0.01) <= 0.03 → neutral
        assert result == "Neutral — monitor and wait"

    def test_get_direction_just_above_bullish(self):
        """return_4w=0.011 (just above +1%) → 'Positive momentum maintained'."""
        result = get_direction(0.011)
        assert result == "Positive momentum maintained"

    def test_get_direction_neutral_negative_small(self):
        """return_4w=-0.01 (within neutral band) → 'Neutral — monitor and wait'."""
        result = get_direction(-0.01)
        assert result == "Neutral — monitor and wait"

    def test_get_direction_neutral_zero(self):
        """return_4w=0.0 → 'Neutral — monitor and wait'."""
        result = get_direction(0.0)
        assert result == "Neutral — monitor and wait"

    def test_get_direction_risk_zone_at_boundary(self):
        """return_4w exactly at -NEUTRAL_BAND (-0.03) is abs() == 0.03 → neutral (not risk zone)."""
        result = get_direction(-NEUTRAL_BAND)
        # abs(-0.03) == 0.03 <= 0.03 → "Neutral — monitor and wait"
        assert result == "Neutral — monitor and wait"

    def test_get_direction_just_below_negative_band(self):
        """return_4w=-0.031 → 'Risk zone'."""
        result = get_direction(-0.031)
        assert result == "Risk zone"


# ── Constant value verification ───────────────────────────────────────────────

class TestConstants:
    def test_bullish_threshold_is_one_percent(self):
        """BULLISH_THRESHOLD must be exactly 0.01 (v3.6 I-4 correction — was 0.02)."""
        assert BULLISH_THRESHOLD == 0.01

    def test_constants_values(self):
        """Verify all threshold constants match specification."""
        assert BULLISH_THRESHOLD == 0.01
        assert NEUTRAL_BAND == 0.03
        assert MIN_WEEKS_TRACKED == 4

    def test_category_b_min_theme_weeks_constant(self):
        """CATEGORY_B_MIN_THEME_WEEKS must be 4."""
        assert CATEGORY_B_MIN_THEME_WEEKS == 4

    def test_min_abs_count_constant(self):
        """MIN_ABS_COUNT must be 1."""
        assert MIN_ABS_COUNT == 1


# ── Source code hygiene tests ─────────────────────────────────────────────────

class TestSourceHygiene:
    def test_no_or_1_pattern_in_source(self):
        """
        Verify that the 'or 1' anti-pattern is absent from classify_category source.
        This was the v3.6 I-7 bug that caused zero-guard bypass.
        """
        import investscan.stock_selector as module
        source = inspect.getsource(module)
        # Check that " or 1" does not appear in classify_category or its helpers
        classify_src = inspect.getsource(classify_category)
        assert " or 1" not in classify_src, (
            "classify_category must NOT use 'or 1' pattern — use explicit MIN_ABS_COUNT guard instead"
        )

    def test_no_lm_calls_in_module(self):
        """Verify that no LLM/OpenAI/Anthropic imports exist in stock_selector.
        Checks only import statements to avoid false positives from docstring mentions.
        """
        import investscan.stock_selector as module
        source = inspect.getsource(module)
        # Only scan import lines — docstrings legitimately say "no LLM calls"
        import_lines = [
            line.strip().lower()
            for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        disallowed = ["openai", "anthropic", "langchain", "gpt"]
        for term in disallowed:
            for line in import_lines:
                assert term not in line, (
                    f"stock_selector must not import LLM libraries, found: {term!r} in: {line!r}"
                )


# ── StockClassification dataclass tests ──────────────────────────────────────

class TestStockClassificationDataclass:
    def test_stock_classification_dataclass(self):
        """StockClassification has stock_code, category, and confidence fields."""
        sc = StockClassification(
            stock_code="005930",
            category="A",
            confidence=0.9,
            classified_by="financial_history",
        )
        assert sc.stock_code == "005930"
        assert sc.category == "A"
        assert sc.confidence == 0.9

    def test_stock_classification_all_fields(self):
        """StockClassification exposes stock_code, category, confidence, classified_by."""
        sc = StockClassification(
            stock_code="000660",
            category="B",
            confidence=0.75,
            classified_by="theme_data",
        )
        assert hasattr(sc, "stock_code")
        assert hasattr(sc, "category")
        assert hasattr(sc, "confidence")
        assert hasattr(sc, "classified_by")

    def test_stock_classification_unknown_category(self):
        """StockClassification can hold 'unknown' category."""
        sc = StockClassification(
            stock_code="TEST",
            category="unknown",
            confidence=0.0,
            classified_by="no_data",
        )
        assert sc.category == "unknown"
        assert sc.confidence == 0.0
