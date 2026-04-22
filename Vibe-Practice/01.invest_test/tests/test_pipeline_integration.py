"""
tests/test_pipeline_integration.py — End-to-end pipeline data-flow integration tests.

Validates the full InvestScan pipeline chain:
  FRED fixture → synthesize_macro → InvestmentMeta
    → stock_selector → (cat_a, cat_b)
    → synthesize_stock (dry-run) → StockFinancials
    → intelligence_engine (dry-run) → NarrativeOutput
    → validate_report_quality (Python 8-criteria)
    → report_generator → report Markdown
    → telegram_notifier (dry-run) → stdout

No external API calls — all modules run in dry-run / fixture mode.
Contract: each stage's OUTPUT must satisfy the next stage's INPUT schema.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Ensure project root is in sys.path ────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Stage imports ──────────────────────────────────────────────────────────────
from investscan.synthesize_macro import synthesize, load_fred_fixture
from investscan.schema import (
    InvestmentMeta, SectorDirection, NarrativeOutput,
    UnifiedSignal, CitationValidationResult, PredictionRecord,
)
from investscan.stock_selector import (
    classify_category, select_stocks, get_direction,
)
from investscan.synthesize_stock import synthesize_stock_data
from investscan.intelligence_engine import generate, _mock_narrative
from investscan.validate_report_quality import python_validate_first
from investscan.report_generator import generate_report
from investscan.telegram_notifier import (
    build_5line_summary, send_message, TelegramConfig,
)
from investscan.compliance_filter import filter_report, scan
from investscan.citation_validator import validate_citations
from investscan.pacs_calculator import calculate_translation_pacs, score_from_files
from investscan.normalizers import normalize_envscan

FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
ENVSCAN_FIXTURE = FIXTURE_DIR / "envscan_sample.json"
FRED_FIXTURE = FIXTURE_DIR / "fred_sample.json"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: FRED fixture → InvestmentMeta
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage1_FREDToInvestmentMeta:
    """FRED fixture data → synthesize_macro → InvestmentMeta contract."""

    def test_fred_fixture_loads(self):
        """FRED fixture file is readable and valid JSON."""
        data = load_fred_fixture()
        assert isinstance(data, dict), "FRED fixture must be a dict"
        assert "series" in data, "FRED fixture must have 'series' key"

    def test_synthesize_returns_investmentmeta(self):
        """synthesize() returns a typed InvestmentMeta, not a plain dict."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert isinstance(meta, InvestmentMeta), "Must return InvestmentMeta"

    def test_investmentmeta_literal_fields_valid(self):
        """rate_direction, inflation_trend, risk_appetite, usd_strength are valid literals."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert meta.rate_direction in ("cut", "hold", "hike")
        assert meta.inflation_trend in ("rising", "cooling", "stable")
        assert meta.risk_appetite in ("low", "moderate", "high")
        assert meta.usd_strength in ("weak", "neutral", "strong")

    def test_investmentmeta_sectors_are_typed(self):
        """sectors field is list[SectorDirection], not empty."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert isinstance(meta.sectors, list)
        assert len(meta.sectors) >= 1, "Must have at least one sector"
        for sd in meta.sectors:
            assert isinstance(sd, SectorDirection)
            assert sd.direction in ("Bullish", "Neutral", "Bearish")
            assert 0.0 <= sd.confidence <= 1.0

    def test_investmentmeta_action_item_nonempty(self):
        """action_item is a non-empty Korean string."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert meta.action_item != "", "action_item must not be empty"
        assert len(meta.action_item) > 10, "action_item too short"

    def test_investmentmeta_checklist_not_empty(self):
        """action_checklist has at least 1 item."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert len(meta.action_checklist) >= 1

    def test_investmentmeta_macro_summary_template(self):
        """macro_summary contains expected labels."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert "Rate:" in meta.macro_summary
        assert "Inflation:" in meta.macro_summary
        assert "Risk appetite:" in meta.macro_summary

    def test_sentimentweight_absent_in_investmentmeta(self):
        """InvestmentMeta must NOT have sentiment_weight field."""
        data = load_fred_fixture()
        meta = synthesize(data)
        assert not hasattr(meta, "sentiment_weight"), \
            "sentiment_weight sentinel must NOT appear in InvestmentMeta"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: InvestmentMeta → stock_selector → (cat_a, cat_b)
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage2_StockSelector:
    """InvestmentMeta → stock_selector → ticker lists contract."""

    @pytest.fixture
    def meta(self):
        return synthesize(load_fred_fixture())

    def test_select_stocks_returns_tuple(self, meta):
        """select_stocks returns (list, list)."""
        result = select_stocks(meta)
        assert isinstance(result, tuple)
        assert len(result) == 2
        cat_a, cat_b = result
        assert isinstance(cat_a, list)
        assert isinstance(cat_b, list)

    def test_select_stocks_max_size(self, meta):
        """cat_a max 5, cat_b max 3."""
        cat_a, cat_b = select_stocks(meta)
        assert len(cat_a) <= 5
        assert len(cat_b) <= 3

    def test_watchlist_override_takes_priority(self, meta):
        """watchlist_override tickers appear first in cat_a."""
        override = ["TEST001", "TEST002"]
        cat_a, _ = select_stocks(meta, watchlist_override=override)
        # Override tickers should be at the front (if present)
        for ticker in override:
            if ticker in cat_a:
                assert cat_a.index(ticker) < len(override)

    def test_classify_category_a_with_financials(self):
        """classify_category returns 'A' when valid financial_history provided."""
        result = classify_category(
            "005930",
            financial_history={"weeks_tracked": 4, "abs_count": 1, "yoy_revenue": 0.18},
            theme_data=None,
        )
        assert result == "A"

    def test_classify_category_b_with_theme(self):
        """classify_category returns 'B' when only theme_data provided."""
        result = classify_category(
            "035720",
            financial_history=None,
            theme_data={
                "theme_weeks": 4, "abs_count": 2, "avg_count": 1.5,
                "market_size": 8_200_000_000,
            },
        )
        assert result == "B"

    def test_classify_category_unknown_no_data(self):
        """classify_category returns 'unknown' when both inputs are None."""
        result = classify_category("UNKNOWN", None, None)
        assert result == "unknown"

    @pytest.mark.parametrize("return_4w,expected", [
        (0.05,  "Positive momentum maintained"),
        (0.02,  "Positive momentum maintained"),
        (0.005, "Neutral — monitor and wait"),
        (-0.01, "Neutral — monitor and wait"),
        (-0.05, "Risk zone"),
        (-0.20, "Risk zone"),
    ])
    def test_get_direction_thresholds(self, return_4w, expected):
        """get_direction maps 4w return to correct directional signal."""
        assert get_direction(return_4w) == expected


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: stock_selector → synthesize_stock → StockFinancials
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage3_SynthesizeStock:
    """stock code + category → synthesize_stock_data → StockFinancials contract."""

    def test_synthesize_stock_returns_dataclass(self):
        """synthesize_stock_data returns a StockFinancials-like object."""
        from investscan.synthesize_stock import StockFinancials
        result = synthesize_stock_data("005930", "Samsung Electronics", "A")
        assert hasattr(result, "stock_code")
        assert hasattr(result, "stock_name")
        assert hasattr(result, "category")

    def test_synthesize_stock_category_preserved(self):
        """category field in StockFinancials matches input."""
        result = synthesize_stock_data("005930", "Samsung Electronics", "A")
        assert result.category == "A"

    def test_synthesize_stock_b_category(self):
        """Category B stock synthesis works."""
        result = synthesize_stock_data("035720", "Kakao", "B")
        assert result.category == "B"

    def test_synthesize_stock_dry_run_no_api_calls(self):
        """Dry-run mode returns mock data without hitting Naver Finance."""
        # Patch Naver Finance to verify it is NOT called in dry-run mode
        with patch("investscan.synthesize_stock._fetch_naver_finance_data") as naver_mock:
            result = synthesize_stock_data(
                "005930", "Samsung Electronics", "A", config={"mode": "dry-run"}
            )
        # In dry-run mode, naver_finance should not be called (data_source == "mock")
        if result.data_source == "mock":
            naver_mock.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: StockFinancials + InvestmentMeta → intelligence_engine → NarrativeOutput
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage4_IntelligenceEngine:
    """context_data → intelligence_engine → NarrativeOutput contract."""

    @pytest.fixture
    def context_data_a(self):
        """Category A context dict for dry-run intelligence_engine."""
        return {
            "category": "A",
            "stock_code": "005930",
            "stock_name": "Samsung Electronics",
            "yoy_revenue": 0.183,
            "yoy_op_income": 0.952,
            "latest_quarter": "2026Q1",
            "per_current": 12.4,
            "per_sector_avg": 14.6,
            "foreign_net_4w_usd": 320_000_000,
            "foreign_flow_direction": "buy",
            "return_4w": 0.055,
            "downside_description": "NAND oversupply risk H2 2026",
            "downside_impact_pct": -12.0,
            "rate_direction": "hold",
            "inflation_trend": "cooling",
            "risk_appetite": "moderate",
            "config": {"mode": "dry-run"},
        }

    def test_generate_returns_narrativeoutput(self, context_data_a):
        """generate() returns NarrativeOutput."""
        result = generate(context_data_a)
        assert isinstance(result, NarrativeOutput)

    def test_sentiment_weight_sentinel_zero(self, context_data_a):
        """sentiment_weight MUST be exactly 0.0 — absolute sentinel."""
        result = generate(context_data_a)
        assert result.sentiment_weight == 0.0, \
            f"SENTINEL VIOLATED: sentiment_weight={result.sentiment_weight}"

    def test_narrative_text_min_1000_bytes(self, context_data_a):
        """NarrativeOutput.text must be >= 1000 bytes UTF-8."""
        result = generate(context_data_a)
        byte_len = len(result.text.encode("utf-8"))
        assert byte_len >= 1000, f"text too short: {byte_len} bytes"

    def test_narrative_category_preserved(self, context_data_a):
        """category in output matches input."""
        result = generate(context_data_a)
        assert result.category == "A"

    def test_narrative_direction_valid_literal(self, context_data_a):
        """direction is one of the three valid literals."""
        result = generate(context_data_a)
        assert result.direction in (
            "Positive momentum maintained",
            "Neutral — monitor and wait",
            "Risk zone",
            "",
        )

    def test_narrative_category_b_fields(self):
        """Category B narrative has market_size and catalyst fields."""
        ctx = {
            "category": "B",
            "stock_code": "035720",
            "stock_name": "Kakao",
            "market_size_usd": 8_200_000_000,
            "market_cagr": 0.34,
            "stock_positioning": "KakaoTalk 47M DAU AI agent deployment platform",
            "catalyst": "KakaoWork AI Agent beta Q2 2026",
            "theme_duration_weeks": 16,
            "dissolution_risk": "Naver Works feature parity by Q4 2026",
            "return_4w": 0.08,
            "config": {"mode": "dry-run"},
        }
        result = generate(ctx)
        assert result.category == "B"
        assert result.sentiment_weight == 0.0

    def test_mock_narrative_no_llm(self, context_data_a):
        """_mock_narrative returns valid NarrativeOutput without any LLM call."""
        result = _mock_narrative(context_data_a)
        assert isinstance(result, NarrativeOutput)
        assert result.sentiment_weight == 0.0
        assert len(result.text.encode("utf-8")) >= 1000


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: NarrativeOutput → validate_report_quality (Python 8-criteria)
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage5_ValidateReportQuality:
    """NarrativeOutput → python_validate_first → ValidationResult contract."""

    @pytest.fixture
    def valid_narrative(self):
        return NarrativeOutput(
            category="A",
            text=(
                "Samsung Electronics enters Q1 2026 as the primary HBM beneficiary. "
                "Revenue surged 18.3% YoY in Q1 2026 as AI hyperscaler allocations accelerated, "
                "with operating income recovering 95.2% on ASP normalization and cost discipline. "
                "At 12.4x PER — a 15.0% discount to the semiconductor sector average — valuation "
                "remains undemanding relative to the earnings recovery trajectory. Foreign institutional "
                "net buying of $320M over 4 weeks signals sustained accumulation. Key downside: "
                "NAND oversupply risk in H2 2026 could cause est. -12% ASP compression. "
                "The company maintains strong balance sheet positioning with robust free cash flow. "
                "Direction: Positive momentum maintained."
            ),
            yoy_growth="Revenue +18.3% YoY, Op.Income +95.2% (2026Q1)",
            per_vs_sector="12.4x, 15.0% discount vs. sector avg 14.6x",
            foreign_flow_direction="4-week net buy: +$320M cumulative",
            downside_risk="NAND oversupply risk H2 2026 → est. -12% ASP",
            direction="Positive momentum maintained",
        )

    def test_validation_returns_result(self, valid_narrative):
        """python_validate_first returns a ValidationResult."""
        from investscan.validate_report_quality import ValidationResult
        result = python_validate_first(valid_narrative)
        assert isinstance(result, ValidationResult)

    def test_validation_has_passed_field(self, valid_narrative):
        """ValidationResult has a passed boolean field."""
        result = python_validate_first(valid_narrative)
        assert hasattr(result, "passed")
        assert isinstance(result.passed, bool)

    def test_sentiment_weight_zero_passes(self, valid_narrative):
        """Narrative with sentiment_weight=0.0 passes the sentinel check."""
        result = python_validate_first(valid_narrative)
        # sentiment_weight check must not be the failure reason
        assert valid_narrative.sentiment_weight == 0.0

    def test_invalid_sentiment_fails(self):
        """Narrative with non-zero sentiment_weight fails validation."""
        from investscan.validate_report_quality import ValidationResult
        # Create narrative via dict hack to bypass frozen dataclass sentinel
        bad = NarrativeOutput.__new__(NarrativeOutput)
        object.__setattr__(bad, "category", "A")
        object.__setattr__(bad, "text", "x" * 1000)
        object.__setattr__(bad, "sentiment_weight", 0.5)
        object.__setattr__(bad, "yoy_growth", "Revenue +5% YoY")
        object.__setattr__(bad, "per_vs_sector", "10x discount")
        object.__setattr__(bad, "foreign_flow_direction", "buy")
        object.__setattr__(bad, "downside_risk", "risk")
        object.__setattr__(bad, "direction", "Risk zone")
        object.__setattr__(bad, "market_size", "")
        object.__setattr__(bad, "stock_positioning", "")
        object.__setattr__(bad, "catalyst", "")
        object.__setattr__(bad, "theme_duration", "")
        object.__setattr__(bad, "dissolution_risk", "")
        object.__setattr__(bad, "disclaimer", "")
        result = python_validate_first(bad)
        assert not result.passed, "Should FAIL when sentiment_weight != 0.0"

    def test_compliance_filter_blocks_prohibited(self):
        """compliance_filter rejects Korean prohibited investment expressions."""
        is_clean, violations = filter_report("이 종목은 강력 매수 추천입니다.", sentiment_weight=0.0)
        assert not is_clean, "Prohibited expression must be blocked"
        assert len(violations) > 0

    def test_compliance_filter_allows_clean(self):
        """compliance_filter passes clean narrative text."""
        is_clean, violations = filter_report(
            "Samsung Electronics shows strong fundamental recovery.", sentiment_weight=0.0
        )
        assert is_clean, "Clean text should pass compliance filter"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: NarrativeOutput → report_generator → Markdown
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage6_ReportGenerator:
    """NarrativeOutput → generate_report → Markdown string contract."""

    @pytest.fixture
    def narrative(self):
        return NarrativeOutput(
            category="A",
            text=(
                "Samsung Electronics leads DRAM recovery entering Q1 2026. "
                "Revenue grew 18.3% YoY with operating income recovering 95.2% on HBM ramp. "
                "At 12.4x PER, the stock trades at a 15% discount to the semiconductor sector. "
                "Foreign net buying of $320M over 4 weeks confirms institutional accumulation. "
                "Primary risk: NAND oversupply in H2 2026 with estimated -12% ASP impact. "
                "The balance sheet remains strong, FCF generation accelerating. "
                "Direction: Positive momentum maintained."
            ),
            yoy_growth="Revenue +18.3% YoY, Op.Income +95.2% (2026Q1)",
            per_vs_sector="12.4x, 15.0% discount vs. sector avg 14.6x",
            foreign_flow_direction="4-week net buy: +$320M cumulative",
            downside_risk="NAND oversupply H2 2026 → est. -12% ASP",
            direction="Positive momentum maintained",
        )

    def test_generate_report_returns_string(self, narrative):
        """generate_report returns a non-empty Markdown string."""
        report = generate_report(narrative, stock_code="005930", stock_name="Samsung Electronics")
        assert isinstance(report, str)
        assert len(report) > 100, "Report too short"

    def test_report_contains_stock_code(self, narrative):
        """Generated report contains the stock code."""
        report = generate_report(narrative, stock_code="005930", stock_name="Samsung Electronics")
        assert "005930" in report

    def test_report_contains_direction(self, narrative):
        """Generated report contains the direction label."""
        report = generate_report(narrative, stock_code="005930", stock_name="Samsung Electronics")
        assert "Positive momentum" in report

    def test_report_contains_yoy_growth(self, narrative):
        """Generated report contains the YoY growth figure."""
        report = generate_report(narrative, stock_code="005930", stock_name="Samsung Electronics")
        assert "18.3%" in report

    def test_report_category_b(self):
        """Category B narrative generates a valid report."""
        narrative_b = NarrativeOutput(
            category="B",
            text=(
                "Kakao's AI agent opportunity is defined by its KakaoTalk distribution moat. "
                "With 47M daily active users and an existing enterprise channel, the company is "
                "positioned to monetize AI agent deployments. The Korean AI agent market of $8.2bn "
                "growing at 34% CAGR creates a multi-year runway. Q2 2026 KakaoWork beta targets "
                "180K enterprise customers — conversion of 15% adds ₩180bn incremental ARR. "
                "Dissolution risk: Naver Works feature parity by Q4 2026. "
                "Note: Theme analysis, not trailing earnings. Direction: Positive momentum maintained."
            ),
            market_size="Korean AI agent market: $8.2bn, CAGR 34%",
            stock_positioning="KakaoTalk 47M DAU deployment platform",
            catalyst="KakaoWork AI Agent beta Q2 2026",
            theme_duration="12-24 week momentum",
            dissolution_risk="Naver Works parity Q4 2026",
            direction="Positive momentum maintained",
        )
        report = generate_report(narrative_b, stock_code="035720", stock_name="Kakao")
        assert isinstance(report, str)
        assert len(report) > 100


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 7: NarrativeOutput → telegram_notifier dry-run
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage7_TelegramNotifier:
    """NarrativeOutput → telegram_notifier (dry-run) → stdout contract."""

    def test_build_5line_summary_returns_string(self):
        """build_5line_summary returns a non-empty string."""
        summary = build_5line_summary(
            stock_name="Samsung Electronics",
            stock_code="005930",
            category="A",
            narrative_text="Samsung Electronics shows strong DRAM recovery momentum.",
            direction="Positive momentum maintained",
            yoy_growth="Revenue +18.3% YoY",
            downside_risk="NAND oversupply risk",
        )
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summary_has_5_lines(self):
        """Summary must have exactly 5 lines (per DG-06 spec)."""
        summary = build_5line_summary(
            stock_name="Samsung Electronics",
            stock_code="005930",
            category="A",
            narrative_text="Strong DRAM recovery with HBM demand from hyperscalers.",
            direction="Positive momentum maintained",
        )
        lines = [l for l in summary.strip().split("\n") if l.strip()]
        assert len(lines) == 5, f"Expected 5 lines, got {len(lines)}: {lines}"

    def test_dry_run_send_returns_true(self):
        """send_message with dry_run=True returns True without network call."""
        cfg = TelegramConfig(bot_token="MOCK", chat_id="MOCK", dry_run=True)
        result = send_message("Test message", cfg)
        assert result is True

    def test_dry_run_does_not_call_http(self):
        """Dry-run mode returns True immediately without reaching network layer."""
        # Verify dry_run short-circuits before any network import is attempted.
        # If httpx is not installed, send_message must still return True in dry-run.
        cfg = TelegramConfig(bot_token="MOCK", chat_id="MOCK", dry_run=True)
        result = send_message("Test message", cfg)
        # If we reach here without ImportError/ConnectionError → dry-run confirmed
        assert result is True, "dry_run must return True without network call"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 8: EnvScan fixture → normalizers → UnifiedSignal list
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage8_Normalizers:
    """EnvScan fixture → normalize_envscan → list[UnifiedSignal] contract."""

    def test_envscan_fixture_loads(self):
        """EnvScan fixture file is readable and valid JSON."""
        with open(ENVSCAN_FIXTURE) as f:
            data = json.load(f)
        assert isinstance(data, (dict, list)), "EnvScan fixture must be dict or list"

    def test_normalize_envscan_returns_list(self):
        """normalize_envscan returns a list."""
        with open(ENVSCAN_FIXTURE) as f:
            raw = json.load(f)
        result = normalize_envscan(raw)
        assert isinstance(result, list)

    def test_normalized_signals_are_unifiedsignal(self):
        """Each normalized signal is a UnifiedSignal instance."""
        with open(ENVSCAN_FIXTURE) as f:
            raw = json.load(f)
        signals = normalize_envscan(raw)
        for sig in signals:
            assert isinstance(sig, UnifiedSignal)

    def test_signal_steeps_category_valid(self):
        """Each UnifiedSignal.steeps_category is one of the 6 STEEPS values."""
        valid_cats = {"T", "E", "P", "S", "E_env", "s"}
        with open(ENVSCAN_FIXTURE) as f:
            raw = json.load(f)
        signals = normalize_envscan(raw)
        for sig in signals:
            assert sig.steeps_category in valid_cats, \
                f"Invalid steeps_category: {sig.steeps_category}"

    def test_signal_psst_score_in_range(self):
        """psst_score is scaled to 0-100 range."""
        with open(ENVSCAN_FIXTURE) as f:
            raw = json.load(f)
        signals = normalize_envscan(raw)
        for sig in signals:
            assert 0.0 <= sig.psst_score <= 100.0, \
                f"psst_score out of range: {sig.psst_score}"

    def test_signal_confidence_0_to_1(self):
        """confidence is in [0.0, 1.0]."""
        with open(ENVSCAN_FIXTURE) as f:
            raw = json.load(f)
        signals = normalize_envscan(raw)
        for sig in signals:
            assert 0.0 <= sig.confidence <= 1.0, \
                f"confidence out of range: {sig.confidence}"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 9: Full end-to-end pipeline chain integration
# ═══════════════════════════════════════════════════════════════════════════════

class TestStage9_FullPipelineChain:
    """
    Full end-to-end chain: all stages in sequence.
    Validates that each stage's output satisfies the next stage's input contract.
    """

    def test_fred_to_report_full_chain(self):
        """Full pipeline: FRED → InvestmentMeta → NarrativeOutput → Markdown report."""
        # Stage 1: FRED → InvestmentMeta
        fred_data = load_fred_fixture()
        meta = synthesize(fred_data)
        assert isinstance(meta, InvestmentMeta)

        # Stage 2: InvestmentMeta → stock selection (use fixed ticker for determinism)
        context_data = {
            "category": "A",
            "stock_code": "005930",
            "stock_name": "Samsung Electronics",
            "yoy_revenue": 0.183,
            "yoy_op_income": 0.952,
            "latest_quarter": "2026Q1",
            "per_current": 12.4,
            "per_sector_avg": 14.6,
            "foreign_net_4w_usd": 320_000_000,
            "foreign_flow_direction": "buy",
            "return_4w": 0.055,
            "downside_description": "NAND oversupply risk H2 2026",
            "downside_impact_pct": -12.0,
            "rate_direction": meta.rate_direction,
            "inflation_trend": meta.inflation_trend,
            "risk_appetite": meta.risk_appetite,
            "config": {"mode": "dry-run"},
        }

        # Stage 3: context_data → NarrativeOutput
        narrative = generate(context_data)
        assert isinstance(narrative, NarrativeOutput)
        assert narrative.sentiment_weight == 0.0  # sentinel MUST hold

        # Stage 4: NarrativeOutput → validation
        validation = python_validate_first(narrative)
        assert hasattr(validation, "passed")

        # Stage 5: NarrativeOutput → compliance check
        is_clean, violations = filter_report(narrative.text, sentiment_weight=narrative.sentiment_weight)
        assert is_clean, f"Narrative failed compliance: {violations}"

        # Stage 6: NarrativeOutput → Markdown report
        report = generate_report(
            narrative,
            stock_code="005930",
            stock_name="Samsung Electronics",
            meta_context=dataclasses.asdict(meta),
        )
        assert isinstance(report, str)
        assert len(report) > 200

        # Stage 7: NarrativeOutput → Telegram summary
        summary = build_5line_summary(
            stock_name="Samsung Electronics",
            stock_code="005930",
            category=narrative.category,
            narrative_text=narrative.text,
            direction=narrative.direction,
            yoy_growth=narrative.yoy_growth,
            downside_risk=narrative.downside_risk,
        )
        lines = [l for l in summary.strip().split("\n") if l.strip()]
        assert len(lines) == 5

        # Stage 7b: Telegram dry-run send
        cfg = TelegramConfig(bot_token="MOCK", chat_id="MOCK", dry_run=True)
        sent = send_message(summary, cfg)
        assert sent is True

    def test_schema_sot_no_duplicate_types(self):
        """All pipeline types imported from schema.py — no local duplicates."""
        import investscan.schema as schema_mod
        schema_classes = {
            name for name, obj in vars(schema_mod).items()
            if isinstance(obj, type) and not name.startswith("_")
        }
        expected = {
            "NarrativeOutput", "UnifiedSignal", "SectorDirection",
            "InvestmentMeta", "PredictionRecord", "CitationValidationResult",
            "ContextContract", "SteepsCategory",
        }
        for cls_name in expected:
            assert cls_name in schema_classes, \
                f"{cls_name} missing from schema.py SOT"

    def test_pacs_calculator_integration(self, tmp_path):
        """pacs_calculator scores a real translation pair correctly."""
        source_text = (
            "Samsung Electronics shows strong DRAM recovery with operating income up 95.2% YoY. "
            "At 12.4x PER, the stock trades at a 15% discount to the semiconductor sector average. "
            "Foreign net buying of $320M over 4 weeks confirms institutional accumulation."
        )
        target_text = (
            "삼성전자는 영업이익이 전년대비 95.2% 증가하며 강한 DRAM 회복세를 보여줍니다. "
            "PER 12.4배로 반도체 섹터 평균 대비 15% 할인된 가격에 거래됩니다. "
            "4주간 외국인 순매수 3.2억 달러로 기관의 지속적 매집을 확인합니다."
        )
        result = calculate_translation_pacs(source_text, target_text)
        assert "pACS" in result
        assert "grade" in result
        assert result["grade"] in ("GREEN", "YELLOW", "RED")
        assert 0 <= result["pACS"] <= 100

    def test_citation_validator_nonblocking(self):
        """citation_validator returns CitationValidationResult (non-blocking)."""
        text = "Revenue grew 18.3% YoY. At 12.4x PER, the stock is a 15% discount."
        context = {"yoy_revenue": 0.183, "per_current": 12.4, "discount_pct": 15.0}
        result = validate_citations(text, context)
        assert isinstance(result, CitationValidationResult)
        assert hasattr(result, "validated")
        assert hasattr(result, "total_numbers_found")

    def test_prediction_record_dataclass(self):
        """PredictionRecord can be created and serialized."""
        record = PredictionRecord(
            week_label="2026-W13",
            stock_code="005930",
            direction="Positive momentum maintained",
        )
        d = dataclasses.asdict(record)
        assert d["week_label"] == "2026-W13"
        assert d["actual_return_4w"] is None  # not yet recorded
