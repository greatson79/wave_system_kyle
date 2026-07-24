"""
investscan/schema.py — Single Source of Truth for all InvestScan dataclasses.

This is the ONLY place where data contracts are defined.
All modules must import types from here — never define local dataclass duplicates.

DO NOT add or rename fields without updating:
  - content_gate() in weekly_orchestrator.py
  - CATEGORY_A/B_SYSTEM_PROMPT in intelligence_engine.py
  - templates/weekly-report.md.j2
  - test_intelligence_engine.py

P5-A: All fields and comments in English.
P6: sentiment_weight == 0.0 is an absolute sentinel — never modify.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal


# ── STEEPs Category enum (P6: type system enforces lowercase s vs S) ─────────

class SteepsCategory(StrEnum):
    """
    Six STEEPs signal categories.
    StrEnum: values are plain strings — existing code using "T", "E", etc. is compatible.
    CRITICAL: lowercase 's' (security/legal) is DISTINCT from uppercase 'S' (society).
    """
    T     = "T"       # Technology
    E     = "E"       # Economic / Financial
    P     = "P"       # Political / Regulatory
    S     = "S"       # Social / Demographic
    E_env = "E_env"   # Environmental / Climate
    s     = "s"       # security / Legal risk (lowercase — intentional)


# ── Core signal types ─────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class NarrativeOutput:
    """
    English-original JSON output produced by intelligence_engine.py.
    content_gate(), report_generator.py, and @translator consume this directly.

    Sentinel rule: sentiment_weight MUST equal 0.0. Any deviation is a bug.
    Text rule: text must be >= 1000 bytes (UTF-8 encoded).
    """

    # ── Common fields (mandatory for both Category A and B) ──────────────────
    category: Literal["A", "B"]
    text: str                               # Full narrative body (English, >= 1000 bytes)
    sentiment_weight: float = 0.0           # ABSOLUTE SENTINEL — never modify

    # ── Category A fields (5 mandatory elements) ─────────────────────────────
    yoy_growth: str = ""
    # Example: "Revenue +12.3% YoY, Op.Income +8.7% (2025Q3)"

    per_vs_sector: str = ""
    # Example: "12.3x, 15.2% discount vs. sector avg 14.5x"

    foreign_flow_direction: str = ""
    # Example: "4-week net buy: +$42M (cumulative)"

    downside_risk: str = ""
    # Example: "Supply chain disruption → est. -8% revenue impact"

    direction: Literal[
        "Positive momentum maintained",
        "Neutral — monitor and wait",
        "Risk zone",
        "",
    ] = ""

    # ── Category B fields (6 mandatory elements) ─────────────────────────────
    market_size: str = ""
    # Example: "Global AI infra market: $180bn, CAGR 28%"

    stock_positioning: str = ""
    # Example: "Tier-1 DRAM supplier for LLM training clusters"

    catalyst: str = ""
    # Example: "Q2 2026 hyperscaler datacenter capex cycle"

    theme_duration: str = ""
    # Example: "12-24 week momentum expected"

    dissolution_risk: str = ""
    # Example: "Chinese DRAM entry by 2027H1"

    disclaimer: str = ""
    # Example: "This analysis is based on publicly available information..."


@dataclass(frozen=True, slots=True)
class UnifiedSignal:
    """
    Normalized signal produced by normalizers.py from EnvironmentScan output.
    Single schema for all downstream processing (steeps_classifier, signal_bridge, etc.).
    """

    steeps_category: str    # SteepsCategory value: "S"|"T"|"E"|"E_env"|"P"|"s"
    psst_score: float       # 0-100 scale
    summary: str            # English summary text
    sector: str             # e.g., "technology", "healthcare"
    confidence: float       # 0.0-1.0
    date: str               # "YYYY-MM-DD"
    source: str = "envscan" # data source identifier
    # Extended fields (optional — backward compatible)
    id: str = ""            # unique signal identifier (e.g., "envscan-abc123")
    title: str = ""         # headline / title text (used by dedup hash)
    signal_date: str = ""   # alias for date (workflow.md ContextContract compatibility)
    steeps_tags: list = field(default_factory=list)   # multi-label categories
    schema_version: str = "signal-v1"


@dataclass(frozen=True, slots=True)
class SectorDirection:
    """
    Per-sector synthesis result produced by synthesize_macro.py.
    Typed replacement for the plain-dict sector_directions field.
    """

    sector_name: str        # e.g., "technology", "healthcare"
    direction: str          # "Bullish" | "Neutral" | "Bearish"
    confidence: float       # 0.0-1.0 (mean weighted score of constituent signals)
    signal_count: int = 0   # number of UnifiedSignals mapped to this sector
    signal_ids: list = field(default_factory=list)  # constituent signal ids


@dataclass(frozen=True, slots=True)
class InvestmentMeta:
    """
    Synthesized macro context produced by synthesize_macro.py.
    Used by intelligence_engine.py as context_data input.
    """

    rate_direction: Literal["cut", "hold", "hike"]
    inflation_trend: Literal["rising", "cooling", "stable"]
    risk_appetite: Literal["low", "moderate", "high"]
    usd_strength: Literal["weak", "neutral", "strong"]
    sector_directions: dict = field(default_factory=dict)
    # Example: {"technology": "bullish", "healthcare": "neutral"}
    generated_at: str = ""
    # Extended fields (optional — backward compatible, added for workflow.md compliance)
    sectors: list = field(default_factory=list)        # list[SectorDirection] — typed sector analysis
    top_signals: list = field(default_factory=list)    # list[UnifiedSignal] — top signals this week
    macro_summary: str = ""                            # one-line macro state description
    action_item: str = ""                              # "이번 주 행동 1가지" (rule-based, P6)
    action_checklist: list = field(default_factory=list)  # checklist items (rule-based, P6)
    schema_version: str = "investmeta-v1"


@dataclass(frozen=True, slots=True)
class PredictionRecord:
    """
    Single prediction entry for accuracy_tracker.py.
    Stored in data/accuracy/ as JSONL.
    """

    week_label: str         # e.g., "2026-W13"
    stock_code: str         # e.g., "005930"
    direction: str          # "Positive momentum maintained" | "Neutral..." | "Risk zone"
    actual_return_4w: float | None = None   # 4-week actual return (preliminary window)
    actual_return_8w: float | None = None   # 8-week actual return (final KS-1 window)
    recorded_at: str = ""


@dataclass(frozen=True, slots=True)
class CitationValidationResult:
    """
    Result of citation_validator.validate_citations().
    Non-blocking: unmatched numbers are flagged, not rejected.
    """

    validated: bool
    unmatched_numbers: list = field(default_factory=list)
    matched_count: int = 0
    total_numbers_found: int = 0


@dataclass
class ContextContract:
    """
    Stage 1 → Stage 2 interface contract.
    Stage 1 (launchd headless weekly_orchestrator.py) produces this file.
    Stage 2 (Claude Code interactive / M1 API intelligence_engine.py) consumes it.

    Schema version mismatch between stages triggers a compatibility warning.
    Saved as: output/context/context_{date}.json

    P6: All fields deterministically populated by Python — no LLM inference.
    """

    report_date: str                            # ISO date "YYYY-MM-DD"
    runtime_mode: str                           # "full" | "envscan_only" | "independent"
    meta: dict                                  # InvestmentMeta serialized
    cat_a_contexts: list                        # list[StockFinancials] — Category A tickers
    cat_b_contexts: list                        # list[StockFinancials] — Category B tickers
    stock_contexts: list                        # cat_a + cat_b combined (for _verify_metrics_consistency)
    signals_summary: list                       # top-5 UnifiedSignal summaries
    fred_snapshot: dict                         # {series_id: {"value": float, "date": str}}
    created_at: str                             # ISO datetime
    schema_version: str = "context-v1"         # version guard — mismatch triggers warning
