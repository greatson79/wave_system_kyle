"""
tests/test_schema.py — Unit tests for investscan.schema module.
Verifies all dataclass definitions, field types, and constraints.
English-First (P5-A).
"""
from __future__ import annotations

import dataclasses
import pytest

from investscan.schema import (
    NarrativeOutput,
    UnifiedSignal,
    InvestmentMeta,
    PredictionRecord,
    CitationValidationResult,
)


# ─────────────────────────────────────────────────────────────────────────────
# NarrativeOutput
# ─────────────────────────────────────────────────────────────────────────────

class TestNarrativeOutput:

    def test_category_a_instantiation(self):
        """NarrativeOutput category A with mandatory fields instantiates cleanly."""
        n = NarrativeOutput(
            category="A",
            text="x" * 1000,
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)",
            per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x",
            foreign_flow_direction="4-week net buy: +$380M (cumulative)",
            downside_risk="DRAM oversupply → -12% revenue",
            direction="Positive momentum maintained",
        )
        assert n.category == "A"
        assert n.sentiment_weight == 0.0

    def test_category_b_instantiation(self):
        """NarrativeOutput category B with mandatory fields instantiates cleanly."""
        n = NarrativeOutput(
            category="B",
            text="y" * 1000,
            market_size="Global AI market: $180bn CAGR 28%",
            stock_positioning="Tier-1 HBM supplier",
            catalyst="Q2 2026 capex cycle",
            theme_duration="12-24 week momentum",
            dissolution_risk="Chinese DRAM entry",
            disclaimer="This analysis does not constitute investment advice.",
        )
        assert n.category == "B"
        assert n.sentiment_weight == 0.0

    def test_sentiment_weight_default_is_zero(self):
        """sentiment_weight must default to 0.0 — absolute sentinel."""
        n = NarrativeOutput(category="A", text="a" * 1000)
        assert n.sentiment_weight == 0.0

    def test_frozen_prevents_mutation(self):
        """NarrativeOutput is frozen — mutation must raise FrozenInstanceError."""
        n = NarrativeOutput(category="A", text="a" * 1000)
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            n.sentiment_weight = 0.5  # type: ignore[misc]

    def test_direction_valid_values(self):
        """Valid direction literals must be accepted."""
        for direction in ("Positive momentum maintained", "Neutral — monitor and wait", "Risk zone", ""):
            n = NarrativeOutput(category="A", text="a" * 1000, direction=direction)
            assert n.direction == direction

    def test_category_a_defaults(self):
        """Category A fields default to empty string when not provided."""
        n = NarrativeOutput(category="A", text="a" * 1000)
        assert n.yoy_growth == ""
        assert n.per_vs_sector == ""
        assert n.foreign_flow_direction == ""
        assert n.downside_risk == ""
        assert n.direction == ""

    def test_category_b_defaults(self):
        """Category B fields default to empty string when not provided."""
        n = NarrativeOutput(category="B", text="b" * 1000)
        assert n.market_size == ""
        assert n.stock_positioning == ""
        assert n.catalyst == ""
        assert n.theme_duration == ""
        assert n.dissolution_risk == ""
        assert n.disclaimer == ""

    def test_asdict_contains_all_fields(self):
        """dataclasses.asdict() must include all fields."""
        n = NarrativeOutput(category="A", text="a" * 1000)
        d = dataclasses.asdict(n)
        for field_name in ("category", "text", "sentiment_weight", "yoy_growth",
                           "per_vs_sector", "foreign_flow_direction", "downside_risk",
                           "direction", "market_size", "stock_positioning", "catalyst",
                           "theme_duration", "dissolution_risk", "disclaimer"):
            assert field_name in d, f"Field '{field_name}' missing from asdict output"

    def test_sentiment_weight_zero_is_sentinel(self):
        """Passing sentiment_weight=0.0 explicitly must succeed."""
        n = NarrativeOutput(category="A", text="a" * 1000, sentiment_weight=0.0)
        assert n.sentiment_weight == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# UnifiedSignal
# ─────────────────────────────────────────────────────────────────────────────

class TestUnifiedSignal:

    def test_basic_instantiation(self):
        """UnifiedSignal with required fields instantiates cleanly."""
        s = UnifiedSignal(
            steeps_category="T",
            psst_score=72.5,
            summary="AI semiconductor demand surge.",
            sector="technology",
            confidence=0.85,
            date="2026-03-28",
        )
        assert s.steeps_category == "T"
        assert s.source == "envscan"  # default

    def test_frozen_prevents_mutation(self):
        """UnifiedSignal is frozen."""
        s = UnifiedSignal(
            steeps_category="E",
            psst_score=50.0,
            summary="summary",
            sector="financials",
            confidence=0.7,
            date="2026-03-28",
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            s.psst_score = 99.0  # type: ignore[misc]

    def test_source_default(self):
        """source defaults to 'envscan'."""
        s = UnifiedSignal(
            steeps_category="P",
            psst_score=40.0,
            summary="Policy signal.",
            sector="defense",
            confidence=0.6,
            date="2026-03-28",
        )
        assert s.source == "envscan"

    def test_source_override(self):
        """source can be overridden."""
        s = UnifiedSignal(
            steeps_category="S",
            psst_score=60.0,
            summary="Social signal.",
            sector="healthcare",
            confidence=0.75,
            date="2026-03-28",
            source="gnews",
        )
        assert s.source == "gnews"

    def test_steeps_categories(self):
        """All 6 STEEPs categories are accepted."""
        for cat in ("S", "T", "E", "E_env", "P", "s"):
            s = UnifiedSignal(
                steeps_category=cat,
                psst_score=50.0,
                summary="test",
                sector="test",
                confidence=0.5,
                date="2026-03-28",
            )
            assert s.steeps_category == cat

    def test_psst_score_range(self):
        """psst_score accepts values in 0-100 range."""
        for score in (0.0, 50.0, 100.0):
            s = UnifiedSignal(
                steeps_category="T",
                psst_score=score,
                summary="test",
                sector="tech",
                confidence=0.5,
                date="2026-03-28",
            )
            assert s.psst_score == score


# ─────────────────────────────────────────────────────────────────────────────
# InvestmentMeta
# ─────────────────────────────────────────────────────────────────────────────

class TestInvestmentMeta:

    def test_basic_instantiation(self):
        """InvestmentMeta with required Literal fields instantiates."""
        m = InvestmentMeta(
            rate_direction="hold",
            inflation_trend="cooling",
            risk_appetite="moderate",
            usd_strength="strong",
        )
        assert m.rate_direction == "hold"
        assert m.sector_directions == {}

    def test_frozen(self):
        """InvestmentMeta is frozen."""
        m = InvestmentMeta(
            rate_direction="cut",
            inflation_trend="stable",
            risk_appetite="high",
            usd_strength="weak",
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            m.rate_direction = "hike"  # type: ignore[misc]

    def test_sector_directions_default(self):
        """sector_directions defaults to empty dict."""
        m = InvestmentMeta(
            rate_direction="hold",
            inflation_trend="stable",
            risk_appetite="low",
            usd_strength="neutral",
        )
        assert isinstance(m.sector_directions, dict)
        assert len(m.sector_directions) == 0


# ─────────────────────────────────────────────────────────────────────────────
# PredictionRecord
# ─────────────────────────────────────────────────────────────────────────────

class TestPredictionRecord:

    def test_basic_instantiation(self):
        """PredictionRecord with required fields instantiates."""
        p = PredictionRecord(
            week_label="2026-W13",
            stock_code="005930",
            direction="Positive momentum maintained",
        )
        assert p.week_label == "2026-W13"
        assert p.actual_return_4w is None
        assert p.actual_return_8w is None

    def test_with_returns(self):
        """PredictionRecord with actual returns set."""
        p = PredictionRecord(
            week_label="2026-W10",
            stock_code="000660",
            direction="Risk zone",
            actual_return_4w=-0.05,
            actual_return_8w=-0.08,
            recorded_at="2026-03-10",
        )
        assert p.actual_return_4w == pytest.approx(-0.05)
        assert p.actual_return_8w == pytest.approx(-0.08)

    def test_frozen(self):
        """PredictionRecord is frozen."""
        p = PredictionRecord(week_label="2026-W13", stock_code="005930", direction="Risk zone")
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            p.stock_code = "000660"  # type: ignore[misc]


# ─────────────────────────────────────────────────────────────────────────────
# CitationValidationResult
# ─────────────────────────────────────────────────────────────────────────────

class TestCitationValidationResult:

    def test_validated_true(self):
        """validated=True with matched counts."""
        r = CitationValidationResult(validated=True, matched_count=5, total_numbers_found=6)
        assert r.validated is True
        assert r.unmatched_numbers == []

    def test_validated_false(self):
        """validated=False with unmatched list."""
        r = CitationValidationResult(
            validated=False,
            unmatched_numbers=["$42bn", "19%"],
            matched_count=0,
            total_numbers_found=2,
        )
        assert r.validated is False
        assert len(r.unmatched_numbers) == 2

    def test_defaults(self):
        """Defaults: unmatched_numbers=[], counts=0."""
        r = CitationValidationResult(validated=True)
        assert r.unmatched_numbers == []
        assert r.matched_count == 0
        assert r.total_numbers_found == 0
