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
    select_stocks,
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


# ═══════════════════════════════════════════════════════════════════════════════
# select_stocks() — P1 Critical RED tests
# Tests for: (1) 3-tuple return with conditional_cat_a, (2) YAML path fix,
#            (3) direction gate fix, (4) per-sector min-1 guarantee
# ═══════════════════════════════════════════════════════════════════════════════

def _make_meta(sectors_spec: list[tuple[str, str, float]]):
    """Build a minimal InvestmentMeta for select_stocks() testing.

    sectors_spec: list of (sector_name, direction, confidence)
    direction: "Bullish" | "Neutral" | "Bearish"  (capitalized, schema convention)
    """
    from investscan.schema import InvestmentMeta, SectorDirection
    sectors = [
        SectorDirection(sector_name=name, direction=direction, confidence=conf)
        for name, direction, conf in sectors_spec
    ]
    sector_directions = {name: direction for name, direction, _ in sectors_spec}
    return InvestmentMeta(
        rate_direction="hold",
        inflation_trend="stable",
        risk_appetite="moderate",
        usd_strength="neutral",
        sector_directions=sector_directions,
        sectors=sectors,
    )


_TELECOM_A_CODES     = {"017670", "030200", "032640"}
_FINANCIALS_A_CODES  = {"105560", "055550", "086790", "316140", "032830"}


class TestSelectStocksReturnShape:
    """select_stocks() must return a 3-tuple: (cat_a, cat_b, conditional_cat_a)."""

    def test_returns_three_element_tuple(self):
        """select_stocks() must return a 3-element tuple after fix."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        result = select_stocks(meta)
        assert isinstance(result, tuple), "select_stocks must return a tuple"
        assert len(result) == 3, (
            f"select_stocks must return (cat_a, cat_b, conditional_cat_a). Got len={len(result)}"
        )

    def test_all_three_elements_are_lists(self):
        """Each element of the 3-tuple must be a list of strings."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        cat_a, cat_b, conditional_cat_a = select_stocks(meta)
        assert isinstance(cat_a, list)
        assert isinstance(cat_b, list)
        assert isinstance(conditional_cat_a, list)


class TestSelectStocksYamlPathFix:
    """Bullish + high-confidence sectors must produce actual stock codes from YAML."""

    def test_bullish_high_confidence_produces_cat_a_stocks(self):
        """telecom=Bullish/0.70 must yield hint=A codes in cat_a, not empty list."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        cat_a, _, _ = select_stocks(meta)
        assert len(cat_a) >= 1, (
            "YAML path bug: cat_a is empty for bullish telecom. Expected >= 1 code."
        )
        assert any(code in _TELECOM_A_CODES for code in cat_a), (
            f"Expected telecom codes, got {cat_a}"
        )


class TestSelectStocksConditionalCatA:
    """Neutral sectors with confidence >= 0.65 must go to conditional_cat_a, not be discarded."""

    def test_neutral_high_confidence_sector_not_silently_dropped(self):
        """financials=Neutral/0.66 must appear in conditional_cat_a, not nowhere."""
        meta = _make_meta([
            ("telecom", "Bullish", 0.70),
            ("financials", "Neutral", 0.66),
        ])
        cat_a, cat_b, conditional_cat_a = select_stocks(meta)
        assert any(code in _FINANCIALS_A_CODES for code in conditional_cat_a), (
            "Neutral sector with confidence>=0.65 must appear in conditional_cat_a. "
            f"Got conditional_cat_a={conditional_cat_a}"
        )

    def test_neutral_high_confidence_not_in_cat_a(self):
        """Neutral sectors must NOT appear in cat_a (they go to conditional_cat_a)."""
        meta = _make_meta([
            ("telecom", "Bullish", 0.70),
            ("financials", "Neutral", 0.66),
        ])
        cat_a, _, conditional_cat_a = select_stocks(meta)
        for code in conditional_cat_a:
            assert code not in cat_a, (
                f"Code {code} from conditional_cat_a must not appear in cat_a"
            )

    def test_neutral_low_confidence_not_in_conditional_cat_a(self):
        """Neutral sector with confidence < 0.65 must NOT enter conditional_cat_a."""
        meta = _make_meta([("financials", "Neutral", 0.55)])
        _, _, conditional_cat_a = select_stocks(meta)
        for code in _FINANCIALS_A_CODES:
            assert code not in conditional_cat_a, (
                f"Low-confidence neutral sector stock {code} must not appear in conditional_cat_a"
            )


class TestSelectStocksMinimumGuarantee:
    """Per-sector min-1 guarantee in select_stocks (mirrors agent_consensus fix)."""

    def test_multiple_bullish_sectors_each_get_stock(self):
        """Two bullish sectors must each contribute >= 1 stock to cat_a."""
        meta = _make_meta([
            ("telecom", "Bullish", 0.75),
            ("financials", "Bullish", 0.66),
        ])
        cat_a, _, _ = select_stocks(meta)
        assert any(c in _TELECOM_A_CODES for c in cat_a),     "telecom missing from cat_a"
        assert any(c in _FINANCIALS_A_CODES for c in cat_a),  "financials missing from cat_a"

    def test_cat_a_does_not_exceed_five(self):
        """cat_a must never exceed 5 stocks."""
        meta = _make_meta([
            ("telecom", "Bullish", 0.75),
            ("financials", "Bullish", 0.70),
            ("semiconductor", "Bullish", 0.66),
        ])
        cat_a, _, _ = select_stocks(meta)
        assert len(cat_a) <= 5, f"cat_a={cat_a} exceeds max 5"


class TestSelectStocksThemeSectors:
    """Bullish sectors with confidence < 0.65 go to cat_b (theme signals)."""

    def test_bullish_low_confidence_goes_to_cat_b(self):
        """Bullish but confidence < 0.65 produces cat_b stocks."""
        meta = _make_meta([("telecom", "Bullish", 0.50)])
        _, cat_b, conditional_cat_a = select_stocks(meta)
        assert len(cat_b) >= 1, "Bullish + low-conf sector must produce cat_b stocks"
        # Must not appear in conditional_cat_a (reserved for non-bullish + high-conf)
        for code in cat_b:
            assert code not in conditional_cat_a

    def test_theme_sectors_capped_at_three(self):
        """cat_b must not exceed 3 stocks even with many theme sectors."""
        meta = _make_meta([
            ("telecom", "Bullish", 0.50),
            ("semiconductor", "Bullish", 0.45),
            ("financials", "Bullish", 0.40),
        ])
        _, cat_b, _ = select_stocks(meta)
        assert len(cat_b) <= 3


class TestSelectStocksLegacyPath:
    """Legacy dict path: investment_meta.sectors empty, sector_directions used."""

    def test_legacy_dict_bullish_sectors_used(self):
        """When sectors list is empty, sector_directions dict drives selection."""
        from investscan.schema import InvestmentMeta
        meta = InvestmentMeta(
            rate_direction="hold",
            inflation_trend="stable",
            risk_appetite="moderate",
            usd_strength="neutral",
            sector_directions={"telecom": "Bullish"},
            sectors=[],  # empty → triggers legacy path
        )
        cat_a, _, _ = select_stocks(meta)
        # Legacy path only checks direction, no confidence gate → telecom stocks in cat_a
        # telecom has hint=A stocks: 017670, 030200, 032640
        assert len(cat_a) >= 1


class TestSelectStocksWatchlistOverride:
    """watchlist_override inserts tickers at the front of cat_a."""

    def test_override_tickers_in_cat_a(self):
        """Override tickers appear in cat_a after override is applied."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        override = ["TEST_A", "TEST_B"]
        cat_a, _, _ = select_stocks(meta, watchlist_override=override)
        # Override tickers must be present in cat_a
        assert "TEST_A" in cat_a
        assert "TEST_B" in cat_a

    def test_override_tickers_at_front(self):
        """Override tickers appear at the start of cat_a."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        override = ["OVERRIDE_1"]
        cat_a, _, _ = select_stocks(meta, watchlist_override=override)
        assert cat_a[0] == "OVERRIDE_1"

    def test_override_capped_at_five(self):
        """cat_a with override never exceeds 5 tickers."""
        meta = _make_meta([("telecom", "Bullish", 0.70)])
        override = ["T1", "T2", "T3", "T4", "T5", "T6"]
        cat_a, _, _ = select_stocks(meta, watchlist_override=override)
        assert len(cat_a) <= 5


class TestSelectStocksConditionalCap:
    """conditional_cat_a cap is enforced at 5."""

    def test_conditional_cat_a_capped_at_five(self):
        """conditional_cat_a must not exceed 5 stocks even with many qualifying sectors."""
        meta = _make_meta([
            ("telecom",           "Neutral", 0.70),
            ("financials",        "Neutral", 0.68),
            ("semiconductor",     "Neutral", 0.67),
            ("power_infrastructure", "Neutral", 0.66),
            ("defense",           "Neutral", 0.66),
            ("biotech",           "Neutral", 0.66),
        ])
        _, _, conditional_cat_a = select_stocks(meta)
        assert len(conditional_cat_a) <= 5


class TestHasValidFinancialsTypeGuards:
    """Type-guard branches in _has_valid_financials (lines 60, 68, 70)."""

    def test_weeks_tracked_non_numeric_returns_unknown(self):
        """weeks_tracked that is a string (not int/float) → unknown category."""
        result = classify_category(
            "TEST",
            financial_history={"weeks_tracked": "four", "abs_count": 1, "yoy_revenue": 0.1},
            theme_data=None,
        )
        assert result == "unknown"

    def test_abs_count_non_numeric_returns_unknown(self):
        """abs_count that is a string → unknown category."""
        result = classify_category(
            "TEST",
            financial_history={"weeks_tracked": 4, "abs_count": "one", "yoy_revenue": 0.1},
            theme_data=None,
        )
        assert result == "unknown"

    def test_abs_count_zero_returns_unknown(self):
        """abs_count == 0 (< MIN_ABS_COUNT=1) → unknown category."""
        result = classify_category(
            "TEST",
            financial_history={"weeks_tracked": 4, "abs_count": 0, "yoy_revenue": 0.1},
            theme_data=None,
        )
        assert result == "unknown"


class TestHasValidThemeTypeGuards:
    """Type-guard branches in _has_valid_theme (lines 99, 106, 113, 115)."""

    def test_theme_weeks_non_numeric_returns_unknown(self):
        """theme_weeks that is a string → unknown category."""
        result = classify_category(
            "TEST",
            financial_history=None,
            theme_data={
                "theme_weeks": "four", "abs_count": 2,
                "avg_count": 1.5, "market_size": "1B",
            },
        )
        assert result == "unknown"

    def test_theme_abs_count_non_numeric_returns_unknown(self):
        """abs_count string in theme_data → unknown category."""
        result = classify_category(
            "TEST",
            financial_history=None,
            theme_data={
                "theme_weeks": 4, "abs_count": "two",
                "avg_count": 1.5, "market_size": "1B",
            },
        )
        assert result == "unknown"

    def test_theme_avg_count_non_numeric_returns_unknown(self):
        """avg_count string in theme_data → unknown category."""
        result = classify_category(
            "TEST",
            financial_history=None,
            theme_data={
                "theme_weeks": 4, "abs_count": 2,
                "avg_count": "one-point-five", "market_size": "1B",
            },
        )
        assert result == "unknown"

    def test_theme_avg_count_negative_returns_unknown(self):
        """avg_count < 0 in theme_data → unknown category."""
        result = classify_category(
            "TEST",
            financial_history=None,
            theme_data={
                "theme_weeks": 4, "abs_count": 2,
                "avg_count": -1.0, "market_size": "1B",
            },
        )
        assert result == "unknown"


class TestSelectStocksEmptySectorName:
    """SectorDirection with empty sector_name must be silently skipped."""

    def test_empty_sector_name_skipped(self):
        """A SectorDirection with no sector_name does not crash or pollute results."""
        from investscan.schema import InvestmentMeta, SectorDirection
        meta = InvestmentMeta(
            rate_direction="hold",
            inflation_trend="stable",
            risk_appetite="moderate",
            usd_strength="neutral",
            sectors=[
                SectorDirection(sector_name="", direction="Bullish", confidence=0.80),
                SectorDirection(sector_name="telecom", direction="Bullish", confidence=0.70),
            ],
        )
        cat_a, cat_b, conditional_cat_a = select_stocks(meta)
        # Should not crash; telecom stocks should appear
        assert isinstance(cat_a, list)
        assert len(cat_a) >= 1


class TestSelectStocksSourceHygiene:
    """select_stocks must comply with P6 Python-First: no LLM imports."""

    def test_no_llm_imports_in_select_stocks(self):
        """select_stocks must not import anthropic, openai, or langchain."""
        import importlib, inspect
        module = importlib.import_module("investscan.stock_selector")
        source = inspect.getsource(module)
        forbidden = ["import anthropic", "import openai", "import langchain"]
        for pattern in forbidden:
            assert pattern not in source, (
                f"P6 violation: '{pattern}' found in stock_selector.py"
            )
