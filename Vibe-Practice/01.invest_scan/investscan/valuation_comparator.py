"""
investscan/valuation_comparator.py — Compute valuation metrics for Category A stocks.
Compares PER to sector average, computes discount/premium.
English-First (P5-A). Python-First (P6): all computations are deterministic Python.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Valuation thresholds (P6: numeric constants, never LLM judgment)
DISCOUNT_THRESHOLD: float = 0.10    # 10%+ discount vs sector → "undervalued"
PREMIUM_THRESHOLD: float = 0.15     # 15%+ premium vs sector → "overvalued"


@dataclass(frozen=True, slots=True)
class ValuationResult:
    """Valuation comparison result for a single stock."""

    stock_code: str
    per_current: float | None
    per_sector_avg: float | None
    discount_pct: float | None          # positive = discount, negative = premium
    valuation_label: str                # "undervalued" | "fairly_valued" | "overvalued" | "unavailable"
    formatted_summary: str              # Ready for NarrativeOutput.per_vs_sector field


def compare_valuation(
    stock_code: str,
    per_current: float | None,
    per_sector_avg: float | None,
) -> ValuationResult:
    """
    Compare stock PER to sector average and produce formatted summary.

    Args:
        stock_code: KRX stock code
        per_current: Current stock PER (trailing twelve months)
        per_sector_avg: Sector average PER for comparison

    Returns:
        ValuationResult with discount_pct and formatted summary string.
    """
    if per_current is None or per_sector_avg is None or per_sector_avg == 0:
        return ValuationResult(
            stock_code=stock_code,
            per_current=per_current,
            per_sector_avg=per_sector_avg,
            discount_pct=None,
            valuation_label="unavailable",
            formatted_summary="PER data unavailable",
        )

    # Positive = discount (stock cheaper than sector), negative = premium
    discount_pct = (per_sector_avg - per_current) / per_sector_avg

    if discount_pct >= DISCOUNT_THRESHOLD:
        label = "undervalued"
    elif discount_pct <= -PREMIUM_THRESHOLD:
        label = "overvalued"
    else:
        label = "fairly_valued"

    # Format for NarrativeOutput.per_vs_sector field
    direction = "discount" if discount_pct >= 0 else "premium"
    formatted = (
        f"{per_current:.1f}x, {abs(discount_pct) * 100:.1f}% {direction} "
        f"vs. sector avg {per_sector_avg:.1f}x"
    )

    return ValuationResult(
        stock_code=stock_code,
        per_current=per_current,
        per_sector_avg=per_sector_avg,
        discount_pct=discount_pct,
        valuation_label=label,
        formatted_summary=formatted,
    )


def format_yoy_growth(
    revenue_growth: float | None,
    op_income_growth: float | None,
    quarter: str = "",
) -> str:
    """
    Format YoY growth figures for NarrativeOutput.yoy_growth field.

    Args:
        revenue_growth: decimal (0.083 = 8.3% growth)
        op_income_growth: decimal
        quarter: latest quarter label e.g. "2025Q4"

    Returns:
        Formatted string like "Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)"
    """
    if revenue_growth is None and op_income_growth is None:
        return "Financial data unavailable"

    parts = []
    if revenue_growth is not None:
        sign = "+" if revenue_growth >= 0 else ""
        parts.append(f"Revenue {sign}{revenue_growth * 100:.1f}% YoY")
    if op_income_growth is not None:
        sign = "+" if op_income_growth >= 0 else ""
        parts.append(f"Op.Income {sign}{op_income_growth * 100:.1f}%")

    result = ", ".join(parts)
    if quarter:
        result += f" ({quarter})"
    return result


def format_foreign_flow(flow_4w_usd_millions: float | None) -> str:
    """
    Format 4-week foreign flow for NarrativeOutput.foreign_flow_direction field.

    Args:
        flow_4w_usd_millions: cumulative 4-week net foreign buy in millions USD

    Returns:
        Formatted string like "4-week net buy: +$380M (cumulative)"
    """
    if flow_4w_usd_millions is None:
        return "Foreign flow data unavailable"

    direction = "buy" if flow_4w_usd_millions >= 0 else "sell"
    sign = "+" if flow_4w_usd_millions >= 0 else ""
    return f"4-week net {direction}: {sign}${abs(flow_4w_usd_millions):.0f}M (cumulative)"
