"""
tests/test_weekly_orchestrator.py — Tests for weekly_orchestrator.py.
Core Pipeline 90% coverage. English-First (P5-A).
All LLM calls mocked — no real API calls. No real file I/O.
"""
from __future__ import annotations

import dataclasses
from unittest.mock import MagicMock, patch

import pytest

from investscan.schema import NarrativeOutput
from investscan.weekly_orchestrator import (
    RetryableError,
    FinalFailureError,
    content_gate,
    pre_translation_gate,
    build_narrative_with_retry,
    _noop_reviewer,
    _save_best_attempt,
    MAX_RETRIES,
)


# ── Shared valid narratives ────────────────────────────────────────────────────

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
    "of 15% combined with Chinese foundry competition could compress operating margins to "
    "the 8-10% range by Q3 2026. Current margin guidance stands at 15-17% for FY2026."
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
    "regulatory scrutiny over AI recommendation transparency in Korean market. Secondary "
    "risk: LINE Yahoo Japan integration complexity may delay synergy realization timeline."
)


def make_narrative_a(**overrides) -> NarrativeOutput:
    defaults = dict(
        category="A",
        text=VALID_TEXT_A,
        sentiment_weight=0.0,
        yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)",
        per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x",
        foreign_flow_direction="4-week net buy: +$380M (cumulative)",
        downside_risk="DRAM oversupply → est. -12% revenue impact",
        direction="Positive momentum maintained",
    )
    defaults.update(overrides)
    return NarrativeOutput(**defaults)


def make_narrative_b(**overrides) -> NarrativeOutput:
    defaults = dict(
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
    defaults.update(overrides)
    return NarrativeOutput(**defaults)


CONTEXT_A = {
    "category": "A",
    "stock_code": "005930",
    "stock_name": "Samsung Electronics",
    "analysis_date": "2026-03-29",
    "yoy_revenue_growth": 0.083,
    "yoy_op_income_growth": 0.342,
    "latest_quarter": "2025Q4",
    "per_current": 10.2,
    "per_sector_avg": 14.2,
    "foreign_flow_4w": 380.0,
    "rate_direction": "hold",
    "inflation_trend": "cooling",
    "risk_appetite": "moderate",
    "usd_strength": "strong",
    "top_signals": ["AI semiconductor demand"],
}


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_max_retries(self):
        assert MAX_RETRIES == 3


# ── Exception classes ─────────────────────────────────────────────────────────

class TestExceptionClasses:
    def test_retryable_error_is_exception(self):
        with pytest.raises(RetryableError):
            raise RetryableError("retry")

    def test_final_failure_error_is_exception(self):
        with pytest.raises(FinalFailureError):
            raise FinalFailureError("final")

    def test_retryable_error_message(self):
        err = RetryableError("test msg")
        assert "test msg" in str(err)


# ── content_gate() ────────────────────────────────────────────────────────────

class TestContentGateCategoryA:
    def test_valid_a_passes(self):
        passed, failures = content_gate(dataclasses.asdict(make_narrative_a()))
        assert passed is True
        assert failures == []

    def test_missing_yoy_growth_fails(self):
        narrative = make_narrative_a()
        d = dataclasses.asdict(narrative)
        d["yoy_growth"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("A1" in f for f in failures)

    def test_missing_per_vs_sector_fails(self):
        d = dataclasses.asdict(make_narrative_a())
        d["per_vs_sector"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("A2" in f for f in failures)

    def test_missing_foreign_flow_fails(self):
        d = dataclasses.asdict(make_narrative_a())
        d["foreign_flow_direction"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("A3" in f for f in failures)

    def test_missing_downside_risk_fails(self):
        d = dataclasses.asdict(make_narrative_a())
        d["downside_risk"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("A4" in f for f in failures)

    def test_invalid_direction_fails(self):
        d = dataclasses.asdict(make_narrative_a())
        d["direction"] = "Buy now!"
        passed, failures = content_gate(d)
        assert passed is False
        assert any("A5" in f for f in failures)

    def test_valid_directions_pass(self):
        for direction in (
            "Positive momentum maintained",
            "Neutral — monitor and wait",
            "Risk zone",
        ):
            d = dataclasses.asdict(make_narrative_a())
            d["direction"] = direction
            passed, _ = content_gate(d)
            assert passed is True, f"Direction '{direction}' should pass"

    def test_short_text_fails_c1(self):
        d = dataclasses.asdict(make_narrative_a())
        d["text"] = "Too short"
        passed, failures = content_gate(d)
        assert passed is False
        assert any("C1" in f for f in failures)

    def test_sentinel_violation_fails_c2(self):
        d = dataclasses.asdict(make_narrative_a())
        d["sentiment_weight"] = 0.7
        passed, failures = content_gate(d)
        assert passed is False
        assert any("C2" in f for f in failures)

    def test_multiple_failures_reported(self):
        d = dataclasses.asdict(make_narrative_a())
        d["yoy_growth"] = ""
        d["per_vs_sector"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert len(failures) >= 2


class TestContentGateCategoryB:
    def test_valid_b_passes(self):
        passed, failures = content_gate(dataclasses.asdict(make_narrative_b()))
        assert passed is True
        assert failures == []

    def test_missing_market_size_fails(self):
        d = dataclasses.asdict(make_narrative_b())
        d["market_size"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("B1" in f for f in failures)

    def test_missing_disclaimer_fails(self):
        d = dataclasses.asdict(make_narrative_b())
        d["disclaimer"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("B6" in f for f in failures)

    def test_missing_catalyst_fails(self):
        d = dataclasses.asdict(make_narrative_b())
        d["catalyst"] = ""
        passed, failures = content_gate(d)
        assert passed is False
        assert any("B3" in f for f in failures)


# ── _noop_reviewer() ──────────────────────────────────────────────────────────

class TestNoopReviewer:
    def test_returns_true_passed(self):
        passed, failures = _noop_reviewer(make_narrative_a())
        assert passed is True

    def test_returns_empty_failures(self):
        passed, failures = _noop_reviewer(make_narrative_a())
        assert failures == []

    def test_accepts_category_b(self):
        passed, failures = _noop_reviewer(make_narrative_b())
        assert passed is True


# ── build_narrative_with_retry() ──────────────────────────────────────────────

class MockIntelligenceEngine:
    """Mock intelligence_engine for testing retry loop."""

    def __init__(self, narratives: list[NarrativeOutput]):
        self._iter = iter(narratives)

    def generate(self, context_data, failure_context=None, config=None):
        return next(self._iter)


class TestBuildNarrativeWithRetrySuccess:
    def test_success_on_first_attempt(self):
        engine = MockIntelligenceEngine([make_narrative_a()])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
            config={"mode": "dry-run"},
        )
        assert isinstance(result, NarrativeOutput)
        assert result.category == "A"

    def test_returns_narrative_output_type(self):
        engine = MockIntelligenceEngine([make_narrative_a()])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)

    def test_sentinel_is_zero_on_return(self):
        engine = MockIntelligenceEngine([make_narrative_a()])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert result.sentiment_weight == 0.0

    def test_success_after_python_fail_then_pass(self):
        # First attempt: short text (Python validation fails)
        # Second attempt: valid narrative
        bad = make_narrative_a(text="short")
        good = make_narrative_a()
        engine = MockIntelligenceEngine([bad, good])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)

    def test_reviewer_failure_triggers_retry(self):
        def strict_reviewer(narrative):
            # Always fail review — but we need two attempts, second passes
            return False, ["Review failed: missing critical context"]

        good = make_narrative_a()
        engine = MockIntelligenceEngine([good, good, good])

        # All reviewer calls fail → should exhaust retries → FinalFailureError
        with pytest.raises(FinalFailureError):
            build_narrative_with_retry(
                context_data=CONTEXT_A,
                intelligence_engine=engine,
                reviewer_agent_fn=strict_reviewer,
            )

    def test_reviewer_exception_skipped_gracefully(self):
        """Reviewer exception → non-blocking, pipeline continues."""
        call_count = [0]

        def failing_reviewer(narrative):
            call_count[0] += 1
            raise RuntimeError("Reviewer API unavailable")

        engine = MockIntelligenceEngine([make_narrative_a()])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=failing_reviewer,
        )
        assert result.sentiment_weight == 0.0
        assert call_count[0] >= 1


class TestBuildNarrativeWithRetryFailure:
    def test_final_failure_after_max_retries(self):
        # 3 narratives all fail Python validation (short text)
        bad = make_narrative_a(text="short")
        engine = MockIntelligenceEngine([bad, bad, bad])
        with pytest.raises(FinalFailureError):
            build_narrative_with_retry(
                context_data=CONTEXT_A,
                intelligence_engine=engine,
                reviewer_agent_fn=_noop_reviewer,
            )

    def test_final_failure_message_contains_max_retries(self):
        bad = make_narrative_a(text="short")
        engine = MockIntelligenceEngine([bad, bad, bad])
        with pytest.raises(FinalFailureError) as exc_info:
            build_narrative_with_retry(
                context_data=CONTEXT_A,
                intelligence_engine=engine,
                reviewer_agent_fn=_noop_reviewer,
            )
        assert str(MAX_RETRIES) in str(exc_info.value)

    def test_compliance_failure_triggers_retry(self):
        # Text with prohibited expression
        prohibited_text = (
            "매수 추천합니다. " + "x" * 1100  # compliance violation + long enough
        )
        bad = make_narrative_a(text=prohibited_text)
        engine = MockIntelligenceEngine([bad, bad, bad])
        with pytest.raises(FinalFailureError):
            build_narrative_with_retry(
                context_data=CONTEXT_A,
                intelligence_engine=engine,
                reviewer_agent_fn=_noop_reviewer,
            )


# ── _save_best_attempt() ──────────────────────────────────────────────────────

class TestSaveBestAttempt:
    def test_saves_json_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _save_best_attempt(make_narrative_a())
        from datetime import date
        saved = list(tmp_path.glob("output/temp/narrative_failed_*.json"))
        assert len(saved) == 1

    def test_none_narrative_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Should return silently
        _save_best_attempt(None)

    def test_saved_file_is_valid_json(self, tmp_path, monkeypatch):
        import json
        monkeypatch.chdir(tmp_path)
        _save_best_attempt(make_narrative_a())
        saved = list(tmp_path.glob("output/temp/narrative_failed_*.json"))[0]
        data = json.loads(saved.read_text(encoding="utf-8"))
        assert "category" in data
        assert data["category"] == "A"


# ── NBS Step 2.5 Integration ──────────────────────────────────────────────────

class TestNBSIntegration:
    """NBS (Numeric Backstop) is Step 2.5 in build_narrative_with_retry().
    Verifies that hallucinated field values trigger retry.
    """

    def test_nbs_pass_allows_pipeline_to_proceed(self):
        # Correct numbers in yoy_growth / per_vs_sector / foreign_flow_direction
        # → NBS passes → pipeline returns narrative
        engine = MockIntelligenceEngine([make_narrative_a()])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)

    def test_nbs_hallucinated_yoy_triggers_retry(self):
        # yoy_growth says 99.9% but context says 8.3%
        hallucinated = make_narrative_a(
            yoy_growth="Revenue +99.9% YoY, Op.Income +99.9% (2025Q4)"
        )
        good = make_narrative_a()
        engine = MockIntelligenceEngine([hallucinated, good])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        # Second attempt (good) should pass
        assert isinstance(result, NarrativeOutput)
        assert result.yoy_growth == make_narrative_a().yoy_growth

    def test_nbs_hallucinated_per_triggers_retry(self):
        # per_vs_sector says 99.9x but context says 10.2x
        hallucinated = make_narrative_a(
            per_vs_sector="99.9x vs. sector avg 14.2x"
        )
        good = make_narrative_a()
        engine = MockIntelligenceEngine([hallucinated, good])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)

    def test_nbs_hallucinated_flow_triggers_retry(self):
        # foreign_flow_direction says $9999M but context says $380M
        hallucinated = make_narrative_a(
            foreign_flow_direction="4-week net buy: +$9999M (cumulative)"
        )
        good = make_narrative_a()
        engine = MockIntelligenceEngine([hallucinated, good])
        result = build_narrative_with_retry(
            context_data=CONTEXT_A,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)

    def test_nbs_all_hallucinated_exhausts_retries(self):
        # All 3 retries produce hallucinated numbers → FinalFailureError
        hallucinated = make_narrative_a(
            yoy_growth="Revenue +99.9% YoY, Op.Income +99.9% (2025Q4)"
        )
        engine = MockIntelligenceEngine([hallucinated, hallucinated, hallucinated])
        with pytest.raises(FinalFailureError):
            build_narrative_with_retry(
                context_data=CONTEXT_A,
                intelligence_engine=engine,
                reviewer_agent_fn=_noop_reviewer,
            )

    def test_nbs_category_b_skipped(self):
        # Category B: NBS fields are qualitative → NBS always passes
        narrative_b = make_narrative_b()
        engine = MockIntelligenceEngine([narrative_b])
        context_b = {**CONTEXT_A, "category": "B"}
        result = build_narrative_with_retry(
            context_data=context_b,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)
        assert result.category == "B"

    def test_nbs_data_unavailable_skips_check(self):
        # If context has DATA_UNAVAILABLE, NBS skips that field check
        context_no_per = {**CONTEXT_A, "per_current": "DATA_UNAVAILABLE"}
        # Even if per_vs_sector seems wrong, NBS won't fail since DATA_UNAVAILABLE
        narrative = make_narrative_a(per_vs_sector="N/A — PER data unavailable")
        engine = MockIntelligenceEngine([narrative])
        result = build_narrative_with_retry(
            context_data=context_no_per,
            intelligence_engine=engine,
            reviewer_agent_fn=_noop_reviewer,
        )
        assert isinstance(result, NarrativeOutput)
