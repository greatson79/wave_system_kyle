"""
tests/test_citation_validator.py — Tests for citation_validator.py.
Core Pipeline 90% coverage. English-First (P5-A).
P6: all validation is Python-only, no LLM.
BCG: Blocking Citation Gate — financial citations only ($ or % marked).
"""
from __future__ import annotations

import pytest
from investscan.citation_validator import (
    extract_numbers,
    parse_numeric,
    validate_citations,
    _extract_context_numbers,
    _is_financial_citation,
    _is_in_context,
    NUMERIC_TOLERANCE,
)
from investscan.schema import CitationValidationResult


class TestIsFinancialCitation:
    """BCG filter: only $ or % marked numbers are financial citations."""

    def test_percentage_is_financial(self):
        assert _is_financial_citation("8.3%") is True

    def test_dollar_prefix_is_financial(self):
        assert _is_financial_citation("$380M") is True

    def test_positive_dollar_is_financial(self):
        assert _is_financial_citation("+$380M") is True

    def test_negative_dollar_is_financial(self):
        assert _is_financial_citation("-$100M") is True

    def test_negative_percentage_is_financial(self):
        assert _is_financial_citation("-12%") is True

    def test_positive_percentage_is_financial(self):
        assert _is_financial_citation("+8.3%") is True

    def test_bare_integer_not_financial(self):
        # Year, count, bare number → not a citation
        assert _is_financial_citation("2025") is False
        assert _is_financial_citation("4") is False
        assert _is_financial_citation("10") is False

    def test_year_not_financial(self):
        assert _is_financial_citation("2026") is False

    def test_bare_decimal_not_financial(self):
        assert _is_financial_citation("10.2") is False  # PER without x or %

    def test_multiplier_without_dollar_not_financial(self):
        assert _is_financial_citation("10.2x") is False  # No $ or %

    def test_empty_string_not_financial(self):
        assert _is_financial_citation("") is False


class TestExtractNumbers:
    def test_extracts_percentage(self):
        nums = extract_numbers("Revenue grew 8.3% YoY")
        assert "8.3%" in nums or any("8.3" in n for n in nums)

    def test_extracts_dollar_millions(self):
        nums = extract_numbers("Foreign flow: +$380M cumulative")
        assert any("380" in n for n in nums)

    def test_extracts_dollar_billions(self):
        nums = extract_numbers("Market size: $42bn CAGR")
        assert any("42" in n for n in nums)

    def test_empty_text(self):
        assert extract_numbers("") == []

    def test_no_numbers(self):
        result = extract_numbers("no numeric content here")
        assert isinstance(result, list)

    def test_multiple_numbers(self):
        text = "Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)"
        nums = extract_numbers(text)
        assert len(nums) >= 2

    def test_excludes_years(self):
        # Years like 2025, 2026 must NOT be extracted as financial citations
        nums = extract_numbers("Q4 2025 and Q1 2026 outlook")
        assert "2025" not in nums
        assert "2026" not in nums

    def test_excludes_bare_integers(self):
        # Bare integers without $ or % are not citations
        nums = extract_numbers("4 weeks, 12 months, Q3 results")
        assert all("%" in n or "$" in n for n in nums)

    def test_excludes_per_multiplier(self):
        # "10.2x" has no $ or % — not a financial citation
        nums = extract_numbers("Current PER of 10.2x")
        assert not any("10.2" in n for n in nums)


class TestParseNumeric:
    def test_parse_percentage(self):
        assert parse_numeric("8.3%") == pytest.approx(8.3)

    def test_parse_dollar_millions(self):
        result = parse_numeric("$380M")
        assert result == pytest.approx(380.0)

    def test_parse_dollar_billions(self):
        result = parse_numeric("$42bn")
        assert result == pytest.approx(42000.0)

    def test_parse_positive_sign(self):
        assert parse_numeric("+8.3") == pytest.approx(8.3)

    def test_parse_negative(self):
        result = parse_numeric("-12")
        assert result == pytest.approx(-12.0)

    def test_parse_plain_number(self):
        assert parse_numeric("34.2") == pytest.approx(34.2)

    def test_parse_unparseable_returns_none(self):
        assert parse_numeric("abc") is None

    def test_parse_empty_string_returns_none(self):
        assert parse_numeric("") is None

    def test_parse_positive_dollar_millions(self):
        # +$380M — sign before $ must be handled correctly
        result = parse_numeric("+$380M")
        assert result == pytest.approx(380.0)

    def test_parse_negative_dollar_millions(self):
        # -$100M — sign before $ must be handled correctly
        result = parse_numeric("-$100M")
        assert result == pytest.approx(-100.0)

    def test_parse_dollar_billions_bn(self):
        result = parse_numeric("$1bn")
        assert result == pytest.approx(1000.0)

    def test_parse_negative_percentage(self):
        assert parse_numeric("-12%") == pytest.approx(-12.0)

    def test_parse_thousands_k_suffix(self):
        result = parse_numeric("$500K")
        assert result == pytest.approx(0.5)


class TestValidateCitations:
    def test_empty_text_returns_validated_true(self):
        result = validate_citations("", {})
        assert result.validated is True

    def test_no_numbers_in_text(self):
        result = validate_citations("Samsung has strong fundamentals.", {"value": 100})
        assert result.validated is True

    def test_matched_numbers_validated(self):
        context = {"revenue_growth": 8.3, "op_income_growth": 34.2}
        text = "Revenue grew 8.3% and operating income grew 34.2%."
        result = validate_citations(text, context)
        assert isinstance(result, CitationValidationResult)
        assert result.total_numbers_found >= 2

    def test_returns_citation_validation_result(self):
        result = validate_citations("Test 5.0% value.", {"v": 5.0})
        assert hasattr(result, "validated")
        assert hasattr(result, "unmatched_numbers")
        assert hasattr(result, "matched_count")

    def test_non_blocking_even_when_unmatched(self):
        # Even with completely unrelated numbers, should not raise
        result = validate_citations("Random number 999.99%.", {"value": 1.0})
        assert isinstance(result, CitationValidationResult)

    def test_empty_context_is_conservative(self):
        # No context → assume valid (conservative approach)
        result = validate_citations("Revenue grew 8.3%.", {})
        assert result.validated is True

    def test_unmatched_numbers_capped_at_10(self):
        # Generate many unmatched numbers
        text = " ".join(f"{i * 100}.5%" for i in range(20))
        result = validate_citations(text, {"value": 0.001})
        assert len(result.unmatched_numbers) <= 10


class TestExtractContextNumbers:
    def test_flat_dict(self):
        nums = _extract_context_numbers({"a": 5.0, "b": 10.0})
        assert 5.0 in nums
        assert 10.0 in nums

    def test_nested_dict(self):
        nums = _extract_context_numbers({"outer": {"inner": 42.0}})
        assert 42.0 in nums

    def test_list_values(self):
        nums = _extract_context_numbers({"list": [1.0, 2.0, 3.0]})
        assert 1.0 in nums
        assert 3.0 in nums

    def test_non_numeric_skipped(self):
        nums = _extract_context_numbers({"text": "hello", "num": 5.0})
        assert "hello" not in nums
        assert 5.0 in nums


class TestIsInContext:
    def test_exact_match(self):
        assert _is_in_context(8.3, [8.3, 34.2, 10.2]) is True

    def test_within_tolerance(self):
        assert _is_in_context(8.3, [8.0]) is True  # 3.7% diff < 5% tolerance

    def test_outside_tolerance(self):
        assert _is_in_context(8.3, [50.0]) is False

    def test_empty_context_returns_true(self):
        assert _is_in_context(8.3, []) is True  # Conservative: assume valid

    def test_tolerance_constant(self):
        assert NUMERIC_TOLERANCE == pytest.approx(0.05)

    def test_percentage_form_conversion(self):
        # Context has 0.083 (decimal), narrative extracted 8.3 (percentage form)
        # 0.083 × 100 = 8.3 → should match
        assert _is_in_context(8.3, [0.083]) is True

    def test_percentage_form_for_small_values(self):
        # 0.001 ≤ |ctx_val| < 10 → also check ctx_val×100
        assert _is_in_context(34.2, [0.342]) is True

    def test_no_percentage_form_for_large_values(self):
        # Values ≥ 10 are not multiplied ×100
        # 380.0 in context → does NOT produce 38000 candidate
        assert _is_in_context(38000.0, [380.0]) is False

    def test_percentage_form_not_applied_below_threshold(self):
        # Values very close to 0 (< 0.001) are not ×100 expanded
        assert _is_in_context(100.0, [0.0001]) is False


class TestBCGBlockingBehavior:
    """BCG: validate_citations returns validated=False when >80% numbers unmatched."""

    def test_all_matched_is_valid(self):
        context = {"yoy": 8.3, "income": 34.2}
        text = "Revenue 8.3% and income 34.2%."
        result = validate_citations(text, context)
        assert result.validated is True

    def test_data_unavailable_skipped_in_context(self):
        # DATA_UNAVAILABLE strings should not be extracted as context numbers
        context = {"yoy": "DATA_UNAVAILABLE", "real": 8.3}
        text = "Revenue 8.3%."
        result = validate_citations(text, context)
        assert result.validated is True

    def test_bcg_threshold_80_percent(self):
        # BCG fires when >80% are unmatched
        # 10 financial numbers, all unmatched → 100% → fail
        context = {"value": 1.0}
        numbers = [f"{i * 111}.5%" for i in range(1, 11)]
        text = " ".join(numbers)
        result = validate_citations(text, context)
        # With all 10 unmatched: 10/10 = 100% > 80% → fail
        assert result.validated is False

    def test_bcg_passes_below_threshold(self):
        # 2 matched, 1 unmatched → 33% unmatched → passes at 80% threshold
        context = {"a": 8.3, "b": 34.2}
        text = "Revenue 8.3%, income 34.2%, and forward PE 999.9%."
        result = validate_citations(text, context)
        # 3 parseable, 1 unmatched = 33% < 80% → validated=True
        assert result.validated is True

    def test_non_financial_numbers_excluded_from_bcg(self):
        # Years and bare integers must NOT be counted
        context = {"value": 0.001}  # tiny value, nothing matches
        # Only bare integers and years — no financial citations
        text = "In Q4 2025, Samsung reported 4 weeks of positive 2026 guidance."
        result = validate_citations(text, context)
        # No financial citations extracted → validated=True (0 total)
        assert result.validated is True

    def test_result_has_matched_count(self):
        context = {"yoy": 8.3}
        text = "Revenue 8.3%."
        result = validate_citations(text, context)
        assert result.matched_count >= 0
        assert result.total_numbers_found >= 0
