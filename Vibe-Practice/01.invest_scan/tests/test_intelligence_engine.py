"""
tests/test_intelligence_engine.py — Tests for intelligence_engine.py.
Core Pipeline 90% coverage. English-First (P5-A).
LLM calls are mocked via monkeypatch — no real API calls in tests.
"""
from __future__ import annotations

import dataclasses
import pytest
from unittest.mock import patch, MagicMock

from investscan.intelligence_engine import (
    generate,
    build_prompt,
    _mock_narrative,
    _build_user_prompt,
    CATEGORY_A_SYSTEM_PROMPT,
    CATEGORY_B_SYSTEM_PROMPT,
)
from investscan.schema import NarrativeOutput


DRY_RUN_CONFIG = {"mode": "dry-run"}

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
    "sector_directions": {"technology": "bullish", "semiconductor": "bullish", "financials": "neutral"},
    "macro_summary": "Rate hold with moderate risk appetite; USD strong; tech bullish",
    "action_item": "semiconductor sector foreign flow direction check before adjusting allocation",
    "action_checklist": ["Check FOMC minutes", "Monitor VIX below 20"],
    "top_signals": ["AI semiconductor demand surge (score=85)", "Fed patience on rate cuts (score=72)"],
}

CONTEXT_B = {
    "category": "B",
    "stock_code": "035420",
    "stock_name": "NAVER",
    "analysis_date": "2026-03-29",
    "rate_direction": "hold",
    "inflation_trend": "cooling",
    "risk_appetite": "moderate",
    "usd_strength": "strong",
    "sector_directions": {"technology": "bullish", "communication": "neutral"},
    "macro_summary": "Rate hold; tech theme intact",
    "action_item": "technology sector foreign flow direction check before adjusting allocation",
    "action_checklist": ["Confirm AI theme momentum continuity"],
    "top_signals": ["AI commerce theme (score=80)", "HyperCLOVA X integration (score=68)"],
}


class TestGenerateDryRun:
    def test_dry_run_returns_narrative_output(self):
        result = generate(CONTEXT_A, config=DRY_RUN_CONFIG)
        assert isinstance(result, NarrativeOutput)

    def test_dry_run_category_a(self):
        result = generate(CONTEXT_A, config=DRY_RUN_CONFIG)
        assert result.category == "A"

    def test_dry_run_category_b(self):
        result = generate(CONTEXT_B, config=DRY_RUN_CONFIG)
        assert result.category == "B"

    def test_dry_run_sentinel_is_zero(self):
        result = generate(CONTEXT_A, config=DRY_RUN_CONFIG)
        assert result.sentiment_weight == 0.0

    def test_dry_run_text_length_over_1000_bytes(self):
        result = generate(CONTEXT_A, config=DRY_RUN_CONFIG)
        assert len(result.text.encode("utf-8")) >= 1000, f"Text too short: {len(result.text.encode())} bytes"

    def test_dry_run_a_has_required_fields(self):
        result = generate(CONTEXT_A, config=DRY_RUN_CONFIG)
        assert result.yoy_growth != ""
        assert result.per_vs_sector != ""
        assert result.foreign_flow_direction != ""
        assert result.downside_risk != ""
        assert result.direction in (
            "Positive momentum maintained",
            "Neutral — monitor and wait",
            "Risk zone",
        )

    def test_dry_run_b_has_required_fields(self):
        result = generate(CONTEXT_B, config=DRY_RUN_CONFIG)
        assert result.market_size != ""
        assert result.stock_positioning != ""
        assert result.catalyst != ""
        assert result.theme_duration != ""
        assert result.dissolution_risk != ""
        assert result.disclaimer != ""

    def test_dry_run_with_failure_context(self):
        failure_ctx = ["A1: Missing YoY revenue figure", "A3: Missing PER reference"]
        result = generate(CONTEXT_A, failure_context=failure_ctx, config=DRY_RUN_CONFIG)
        assert isinstance(result, NarrativeOutput)


class TestBuildPrompt:
    def test_returns_string(self):
        prompt = build_prompt(CONTEXT_A)
        assert isinstance(prompt, str)

    def test_contains_stock_info(self):
        prompt = build_prompt(CONTEXT_A)
        assert "Samsung Electronics" in prompt
        assert "005930" in prompt

    def test_contains_failure_context(self):
        failures = ["Missing PER reference", "Text too short"]
        prompt = build_prompt(CONTEXT_A, failure_context=failures)
        assert "Missing PER reference" in prompt

    def test_english_only(self):
        prompt = build_prompt(CONTEXT_A)
        # Should not contain Korean characters (Korean is for user output only)
        import re
        korean_chars = re.findall(r'[\uAC00-\uD7A3]', prompt)
        assert len(korean_chars) == 0, f"Korean chars in prompt: {korean_chars}"

    def test_contains_sector_directions(self):
        ctx = {**CONTEXT_A, "sector_directions": {"technology": "bullish", "energy": "bearish"}}
        prompt = build_prompt(ctx)
        assert "Sector Directions" in prompt
        assert "technology: bullish" in prompt
        assert "energy: bearish" in prompt

    def test_action_item_not_in_prompt(self):
        # action_item is Korean user-facing text — must NOT appear in English LLM prompt (P5-A)
        ctx = {**CONTEXT_A, "action_item": "금리 인하 수혜 섹터 비중 확대"}
        prompt = build_prompt(ctx)
        assert "금리" not in prompt
        assert "Action:" not in prompt

    def test_action_checklist_not_in_prompt(self):
        # action_checklist is Korean user-facing — must NOT appear in English LLM prompt (P5-A)
        ctx = {**CONTEXT_A, "action_checklist": ["금리 인하 수혜주 목록 업데이트"]}
        prompt = build_prompt(ctx)
        assert "금리" not in prompt
        assert "Checklist:" not in prompt

    def test_contains_macro_summary(self):
        ctx = {**CONTEXT_A, "macro_summary": "Rate hold, moderate risk appetite, USD strong"}
        prompt = build_prompt(ctx)
        assert "Macro Summary:" in prompt
        assert "Rate hold" in prompt

    def test_empty_sector_directions_skipped(self):
        ctx = {**CONTEXT_A, "sector_directions": {}}
        prompt = build_prompt(ctx)
        assert "Sector Directions" not in prompt

    def test_empty_sector_directions_no_section(self):
        # Redundant with test_empty_sector_directions_skipped — verifies no stray header
        ctx = {**CONTEXT_A, "sector_directions": {}}
        prompt = build_prompt(ctx)
        assert "## Sector Directions" not in prompt


class TestMockNarrative:
    def test_mock_a_sentinel(self):
        result = _mock_narrative({"category": "A"})
        assert result.sentiment_weight == 0.0

    def test_mock_b_sentinel(self):
        result = _mock_narrative({"category": "B"})
        assert result.sentiment_weight == 0.0

    def test_mock_a_text_long_enough(self):
        result = _mock_narrative({"category": "A"})
        assert len(result.text.encode("utf-8")) >= 1000

    def test_mock_b_text_long_enough(self):
        result = _mock_narrative({"category": "B"})
        assert len(result.text.encode("utf-8")) >= 1000

    def test_mock_default_category_is_a(self):
        result = _mock_narrative({})
        assert result.category == "A"


class TestSystemPrompts:
    def test_category_a_prompt_english(self):
        assert "sentiment_weight" in CATEGORY_A_SYSTEM_PROMPT
        assert "0.0" in CATEGORY_A_SYSTEM_PROMPT

    def test_category_b_prompt_english(self):
        assert "sentiment_weight" in CATEGORY_B_SYSTEM_PROMPT
        assert "0.0" in CATEGORY_B_SYSTEM_PROMPT

    def test_category_a_prompt_has_5_fields(self):
        # 5 required fields for Category A
        for field in ["yoy_growth", "per_vs_sector", "foreign_flow", "downside_risk", "direction"]:
            assert field.replace("_", "") in CATEGORY_A_SYSTEM_PROMPT.replace("_", "").lower()

    def test_category_b_prompt_has_6_fields(self):
        for keyword in ["market_size", "stock_positioning", "catalyst", "theme_duration", "dissolution_risk", "disclaimer"]:
            assert keyword.replace("_", "") in CATEGORY_B_SYSTEM_PROMPT.replace("_", "").lower()

    def test_prohibited_expressions_in_a_prompt(self):
        assert "buy recommendation" in CATEGORY_A_SYSTEM_PROMPT.lower() or "prohibited" in CATEGORY_A_SYSTEM_PROMPT.lower()
