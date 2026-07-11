"""
tests/test_validate_report_quality.py — Tests for validate_report_quality.py.
Core Pipeline 90% coverage. English-First (P5-A).
P6: python_validate_first() is pure Python — no LLM calls.
"""
from __future__ import annotations

import pytest
from investscan.schema import NarrativeOutput
from investscan.validate_report_quality import (
    ValidationResult,
    python_validate_first,
    validate_bear_case_position,
    CATEGORY_A_REQUIRED,
    CATEGORY_B_REQUIRED,
    MIN_TEXT_BYTES,
)


# Fixtures — valid narratives for testing (must be >= 1000 bytes UTF-8)
VALID_TEXT_A = (
    "Samsung Electronics delivers strong Q4 2025 results with Revenue +8.3% YoY, "
    "Operating Income +34.2%. The current PER of 10.2x represents a 28.4% discount "
    "to the sector average of 14.2x. Foreign institutional net buy: +$380M over 4 weeks. "
    "Primary downside risk: DRAM oversupply resurgence → est. -12% revenue impact. "
    "The 4-week net foreign buy pattern and improving year-over-year quarterly results "
    "support a positive fundamental outlook. Risk appetite remains moderate per VIX levels. "
    "Memory semiconductor demand driven by AI training infrastructure investment continues "
    "to provide a structural tailwind. NAND pricing has stabilized following two quarters "
    "of inventory correction, and HBM (High Bandwidth Memory) allocation for leading AI "
    "chip customers remains sold out through H1 2026. Foundry utilization rates at 78% "
    "suggest capacity normalization. Capital allocation policy remains disciplined, with "
    "a 50% total shareholder return ratio maintained. Downside scenario: DRAM ASP decline "
    "of 15% combined with Chinese foundry competition could compress margins to 8-10%."
)

VALID_TEXT_B = (
    "NAVER's AI commerce integration drives category B growth thesis. The global AI "
    "commerce market reaches $42bn with CAGR 19% through 2028. Stock positioning: "
    "dominant search-to-commerce funnel with 78% Korean search market share. "
    "Catalyst: Q2 2026 AI shopping assistant launch. Theme duration: 18-30 week momentum "
    "expected. Theme dissolution risk: Google AI Mode entry by Q4 2026. "
    "This analysis is based on publicly available information and does not constitute "
    "investment advice. Past performance does not guarantee future results. "
    "HyperCLOVA X model integration into NAVER Shopping enables personalized product "
    "recommendations with conversion rate uplift of 12-18% versus control groups. "
    "The advertising revenue per search query has increased 9.2% QoQ as AI-assisted "
    "query expansion broadens ad inventory. Webtoon and fintech subsidiaries represent "
    "option value not fully reflected in current consensus estimates. Operating leverage "
    "is expected to improve as AI infrastructure costs plateau in H2 2026. Key risk: "
    "regulatory scrutiny over AI recommendation transparency in the Korean market."
)


def make_valid_narrative_a() -> NarrativeOutput:
    return NarrativeOutput(
        category="A",
        text=VALID_TEXT_A,
        sentiment_weight=0.0,
        yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)",
        per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x",
        foreign_flow_direction="4-week net buy: +$380M (cumulative)",
        downside_risk="DRAM oversupply → est. -12% revenue impact",
        direction="Positive momentum maintained",
    )


def make_valid_narrative_b() -> NarrativeOutput:
    return NarrativeOutput(
        category="B",
        text=VALID_TEXT_B,
        sentiment_weight=0.0,
        market_size="Korean AI commerce market: $42bn, CAGR 19%",
        stock_positioning="Dominant search funnel — 78% market share",
        catalyst="Q2 2026 AI shopping assistant launch",
        theme_duration="18-30 week momentum expected",
        dissolution_risk="Google AI Mode entry by Q4 2026",
        disclaimer="This analysis does not constitute investment advice.",
    )


class TestPythonValidateFirstCategoryA:
    def test_valid_narrative_a_passes(self):
        narrative = make_valid_narrative_a()
        result = python_validate_first(narrative)
        assert result.passed is True

    def test_empty_per_vs_sector_fails(self):
        narrative = NarrativeOutput(
            category="A",
            text=VALID_TEXT_A,
            sentiment_weight=0.0,
            yoy_growth="Rev +8%",
            per_vs_sector="",  # Empty — should fail
            foreign_flow_direction="Net buy",
            downside_risk="Risk",
            direction="Positive momentum maintained",
        )
        result = python_validate_first(narrative)
        assert result.passed is False
        assert any("per_vs_sector" in d for d in result.details)

    def test_sentinel_violation_fails(self):
        data = {
            "category": "A",
            "text": VALID_TEXT_A,
            "sentiment_weight": 0.7,  # VIOLATION
            "yoy_growth": "Rev +8%",
            "per_vs_sector": "10x vs 14x",
            "foreign_flow_direction": "Net buy",
            "downside_risk": "Risk",
            "direction": "Positive momentum maintained",
        }
        narrative = NarrativeOutput(**data)
        result = python_validate_first(narrative)
        assert result.passed is False
        assert any("SENTINEL" in d for d in result.details)

    def test_short_text_fails(self):
        narrative = NarrativeOutput(
            category="A",
            text="Too short",
            sentiment_weight=0.0,
            yoy_growth="Rev +8%",
            per_vs_sector="10x",
            foreign_flow_direction="Net buy",
            downside_risk="Risk",
            direction="Positive momentum maintained",
        )
        result = python_validate_first(narrative)
        assert result.passed is False

    def test_empty_yoy_growth_fails(self):
        narrative = NarrativeOutput(
            category="A",
            text=VALID_TEXT_A,
            sentiment_weight=0.0,
            yoy_growth="",  # Empty
            per_vs_sector="10.2x",
            foreign_flow_direction="Net buy",
            downside_risk="Risk",
            direction="Positive momentum maintained",
        )
        result = python_validate_first(narrative)
        assert result.passed is False

    def test_empty_direction_fails(self):
        narrative = NarrativeOutput(
            category="A",
            text=VALID_TEXT_A,
            sentiment_weight=0.0,
            yoy_growth="Rev +8%",
            per_vs_sector="10x",
            foreign_flow_direction="Net buy",
            downside_risk="Risk",
            direction="",  # Empty
        )
        result = python_validate_first(narrative)
        assert result.passed is False

    def test_result_has_details_on_failure(self):
        narrative = NarrativeOutput(
            category="A",
            text="Short",
            sentiment_weight=0.0,
        )
        result = python_validate_first(narrative)
        assert isinstance(result.details, list)
        assert len(result.details) > 0


class TestPythonValidateFirstCategoryB:
    def test_valid_narrative_b_passes(self):
        narrative = make_valid_narrative_b()
        result = python_validate_first(narrative)
        assert result.passed is True

    def test_empty_market_size_fails(self):
        narrative = NarrativeOutput(
            category="B",
            text=VALID_TEXT_B,
            sentiment_weight=0.0,
            market_size="",  # Empty
            stock_positioning="Dominant funnel",
            catalyst="Q2 2026 launch",
            theme_duration="18 weeks",
            dissolution_risk="Google entry risk",
            disclaimer="Not investment advice",
        )
        result = python_validate_first(narrative)
        assert result.passed is False

    def test_empty_theme_duration_fails(self):
        narrative = NarrativeOutput(
            category="B",
            text=VALID_TEXT_B,
            sentiment_weight=0.0,
            market_size="$42bn CAGR 19%",
            stock_positioning="Dominant funnel",
            catalyst="Q2 2026 launch",
            theme_duration="",  # Empty — should fail
            dissolution_risk="Google entry risk",
            disclaimer="Not investment advice",
        )
        result = python_validate_first(narrative)
        assert result.passed is False
        assert any("theme_duration" in d for d in result.details)

    def test_empty_disclaimer_fails(self):
        narrative = NarrativeOutput(
            category="B",
            text=VALID_TEXT_B,
            sentiment_weight=0.0,
            market_size="$42bn CAGR 19%",
            stock_positioning="Dominant funnel",
            catalyst="Q2 2026 launch",
            theme_duration="18 weeks",
            dissolution_risk="Google entry risk",
            disclaimer="",  # Empty
        )
        result = python_validate_first(narrative)
        assert result.passed is False


class TestConstants:
    def test_min_text_bytes(self):
        assert MIN_TEXT_BYTES == 1000

    def test_category_a_patterns_count(self):
        assert len(CATEGORY_A_REQUIRED) == 5

    def test_category_b_patterns_count(self):
        assert len(CATEGORY_B_REQUIRED) == 6


class TestValidationResult:
    def test_passed_true(self):
        result = ValidationResult(passed=True)
        assert result.passed is True
        assert result.details == []

    def test_criteria_checked_default(self):
        result = ValidationResult(passed=True)
        assert result.criteria_checked == 8


class TestBearCasePosition:
    def test_bear_case_before_disclaimer_passes(self):
        report = "Content\n\n⚠️ Bear case\n\nsome disclaimer text here"
        assert validate_bear_case_position(report) is True

    def test_no_bear_case_passes(self):
        report = "Content with no bear case section"
        assert validate_bear_case_position(report) is True

    def test_no_disclaimer_passes(self):
        report = "Content\n\n⚠️ Bear case"
        assert validate_bear_case_position(report) is True
