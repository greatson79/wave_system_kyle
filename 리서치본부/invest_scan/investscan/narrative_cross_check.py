"""
investscan/narrative_cross_check.py — Numeric Backstop (NBS).
Hallucination 원천봉쇄: cross-verify LLM-generated financial numbers against input data.

P6 Python-First: pure Python regex + arithmetic — zero LLM calls.
English-First (P5-A).

Called in build_narrative_with_retry() as Step 2.5 (after python_validate_first,
before compliance_filter). Raises RetryableError on mismatch.

Design principle: "LLM narrates, Python judges."
The judge must now verify the LLM's numbers match the ground truth inputs.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from investscan.schema import NarrativeOutput

logger = logging.getLogger(__name__)

# Sentinel value written to context_data when a data source was unavailable.
# NBS skips cross-check for unavailable fields (no ground truth to check against).
DATA_UNAVAILABLE: str = "DATA_UNAVAILABLE"

# 5% relative tolerance — accounts for formatting rounding (8.27% written as "8.3%")
DEFAULT_TOLERANCE: float = 0.05

# Numeric extraction: matches integers and decimals, bounded by non-digit boundaries.
# Captures: 8.3, 34.2, 10.2, 380, 1000 — does NOT capture substrings of larger numbers.
_FLOAT_PATTERN: re.Pattern = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)(?!\d)")


def cross_check_narrative_numbers(
    narrative: "NarrativeOutput",
    context_data: dict,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[str]:
    """
    Cross-verify LLM-generated narrative fields against ground-truth context_data values.

    Checks 4 critical Category A fields:
      NBS-01:  yoy_growth (revenue)   ← context_data["yoy_revenue_growth"]
      NBS-01b: yoy_growth (op.income) ← context_data["yoy_op_income_growth"]
      NBS-02:  per_vs_sector          ← context_data["per_current"]
      NBS-03:  foreign_flow_direction ← context_data["foreign_flow_4w"]

    NBS-01 and NBS-01b both anchor on yoy_growth because that field contains
    both revenue and operating income figures. Without NBS-01b, the LLM can
    fabricate op.income while keeping revenue correct, silently passing NBS-01.

    Category B fields (market_size, catalyst, theme_duration) are qualitative —
    no numeric ground truth available in context_data, so skipped.

    Args:
        narrative:     NarrativeOutput from intelligence_engine
        context_data:  dict from _build_context_data() (ground truth values)
        tolerance:     relative tolerance for numeric comparison (default 5%)

    Returns:
        list[str]: error descriptions. Empty list = all checks passed.

    Raises:
        Nothing — caller (build_narrative_with_retry) decides whether to retry.
    """
    errors: list[str] = []

    # Skip cross-check for Category B — no deterministic numeric ground truth
    if narrative.category == "B":
        logger.debug("NBS: Category B — numeric cross-check skipped (qualitative fields)")
        return []

    # NBS-01: YoY revenue growth
    raw_yoy = context_data.get("yoy_revenue_growth")
    if _is_available(raw_yoy) and narrative.yoy_growth:
        expected_pct = float(raw_yoy) * 100  # decimal → percentage: 0.083 → 8.3
        found = _extract_floats(narrative.yoy_growth)
        if found and not _any_within_tolerance(expected_pct, found, tolerance):
            errors.append(
                f"NBS-01: yoy_growth mismatch — "
                f"input={expected_pct:.1f}%, "
                f"narrative numbers={_fmt(found)} — "
                f"LLM may have fabricated revenue growth figure"
            )

    # NBS-01b: YoY operating income growth (same field, second anchor)
    # yoy_growth field contains BOTH revenue and op.income figures.
    # NBS-01 anchors on revenue; NBS-01b anchors on op.income independently.
    # Without this check, "Revenue +8.3% YoY, Op.Income +99.9%" passes NBS-01 (8.3 found).
    raw_op_income = context_data.get("yoy_op_income_growth")
    if _is_available(raw_op_income) and narrative.yoy_growth:
        expected_pct = float(raw_op_income) * 100  # decimal → percentage: 0.342 → 34.2
        found = _extract_floats(narrative.yoy_growth)
        if found and not _any_within_tolerance(expected_pct, found, tolerance):
            errors.append(
                f"NBS-01b: yoy_growth op.income mismatch — "
                f"input={expected_pct:.1f}%, "
                f"narrative numbers={_fmt(found)} — "
                f"LLM may have fabricated op.income growth figure"
            )

    # NBS-02: PER vs sector average
    raw_per = context_data.get("per_current")
    if _is_available(raw_per) and narrative.per_vs_sector:
        expected_per = float(raw_per)  # already in x form: 10.2
        found = _extract_floats(narrative.per_vs_sector)
        if found and not _any_within_tolerance(expected_per, found, tolerance):
            errors.append(
                f"NBS-02: per_vs_sector mismatch — "
                f"input={expected_per:.1f}x, "
                f"narrative numbers={_fmt(found)} — "
                f"LLM may have fabricated PER figure"
            )

    # NBS-03: Foreign investor 4-week flow
    raw_flow = context_data.get("foreign_flow_4w")
    if _is_available(raw_flow) and narrative.foreign_flow_direction:
        # Use absolute value — narrative may say "+$380M" or "-$380M" (direction is in text)
        expected_flow = abs(float(raw_flow))
        found = _extract_floats(narrative.foreign_flow_direction)
        if found and not _any_within_tolerance(expected_flow, found, tolerance):
            errors.append(
                f"NBS-03: foreign_flow mismatch — "
                f"input=±{expected_flow:.0f}M, "
                f"narrative numbers={_fmt(found)} — "
                f"LLM may have fabricated foreign flow figure"
            )

    if errors:
        logger.warning(
            "NBS: %d numeric mismatch(es) — hallucination suspected in %s",
            len(errors),
            [e.split(":")[0] for e in errors],
        )
    else:
        logger.debug("NBS: all critical numeric fields verified (tolerance=%.0f%%)", tolerance * 100)

    return errors


def _is_available(value) -> bool:
    """Return True if the value is real numeric data (not None or DATA_UNAVAILABLE)."""
    return value is not None and value != DATA_UNAVAILABLE


def _extract_floats(text: str) -> list[float]:
    """
    Extract all positive numeric values from text as floats.
    "Revenue +8.3% YoY, Op.Income +34.2%" → [8.3, 34.2]
    "10.2x, 28.4% discount vs. 14.2x" → [10.2, 28.4, 14.2]
    """
    matches = _FLOAT_PATTERN.findall(text)
    result = []
    for m in matches:
        try:
            v = float(m)
            if v > 0:  # ignore zeros — they appear as punctuation artifacts
                result.append(v)
        except ValueError:
            pass
    return result


def _any_within_tolerance(expected: float, candidates: list[float], tol: float) -> bool:
    """
    Return True if any candidate is within `tol` relative tolerance of `expected`.

    Uses relative tolerance: |candidate - expected| / |expected| <= tol

    Edge case: if expected ≈ 0, use absolute tolerance of 0.1.
    """
    if abs(expected) < 0.001:
        return any(abs(c) < 0.1 for c in candidates)

    for c in candidates:
        if abs(c - expected) / abs(expected) <= tol:
            return True
    return False


def _fmt(values: list[float]) -> str:
    """Format a list of floats for error message display."""
    return "[" + ", ".join(f"{v:.2f}" for v in values[:5]) + "]"
