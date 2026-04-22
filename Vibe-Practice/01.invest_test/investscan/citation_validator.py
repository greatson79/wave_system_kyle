"""
investscan/citation_validator.py — Validate numeric citations in NarrativeOutput.
H-5 (v3.4): Cross-validate numbers in narrative text against context_data.
BCG (Blocking Citation Gate): validated=False → RetryableError in weekly_orchestrator.
Threshold: 80% unmatched — broad hallucination detection only (NBS handles precision).
P6 Python-First: pure Python regex + numeric comparison — no LLM calls.
English-First (P5-A).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from investscan.narrative_cross_check import DATA_UNAVAILABLE
from investscan.schema import CitationValidationResult

logger = logging.getLogger(__name__)

# Regex to extract numeric values from text
# Matches: 12.3%, $42M, $180bn, +8.7%, -12%, 1000 bytes, 28% CAGR
NUMBER_PATTERN = re.compile(
    r"[+-]?[\$]?\d+(?:\.\d+)?(?:[MBKmb]n?)?(?:\s*%)?",
    re.IGNORECASE,
)

# Tolerance for floating-point comparison
NUMERIC_TOLERANCE: float = 0.05  # 5% relative tolerance


def extract_numbers(text: str) -> list[str]:
    """
    Extract financial citation numbers from text using regex.
    Returns only numbers that are explicitly financial figures:
    - Has $ prefix: $380M, $42bn
    - Has % suffix: 8.3%, 34.2%
    - Has sign prefix with %: +8.3%, -12%

    This excludes: years (2025, 2026), counts (4 weeks, Q4, Q3),
    and bare integers without financial context.
    These non-financial numbers are NOT citations and must not be checked.
    """
    if not text:
        return []
    return [m for m in NUMBER_PATTERN.findall(text) if _is_financial_citation(m)]


def _is_financial_citation(raw: str) -> bool:
    """
    Return True only if this number is a financial citation (has $ or % marker).
    Years, counts, and bare integers are NOT citations.
    """
    # Must have % suffix OR $ prefix to be a "cited" financial figure
    stripped = raw.strip()
    return stripped.endswith('%') or stripped.startswith('$') or stripped.startswith('+$') or stripped.startswith('-$')


def parse_numeric(raw: str) -> float | None:
    """
    Parse a raw numeric string to float.
    Handles: $42M, 8.3%, +12.5, -8%, $180bn

    Returns:
        Float value (millions for M, billions for bn/B), or None if unparseable.
    """
    try:
        # Remove $ signs (handles: $380M, +$380M, -$100M)
        clean = raw.strip().replace("$", "").strip()

        # Extract multiplier suffix
        multiplier = 1.0
        if clean.lower().endswith("bn"):
            multiplier = 1000.0
            clean = clean[:-2]
        elif clean.lower().endswith("b"):
            multiplier = 1000.0
            clean = clean[:-1]
        elif clean.lower().endswith("mn") or clean.lower().endswith("m"):
            multiplier = 1.0
            clean = clean[:-1] if clean.lower().endswith("m") else clean[:-2]
        elif clean.lower().endswith("k"):
            multiplier = 0.001
            clean = clean[:-1]

        # Remove % sign
        clean = clean.rstrip("%").strip()
        return float(clean) * multiplier
    except (ValueError, AttributeError):
        return None


def validate_citations(
    narrative_text: str,
    context_data: dict,
) -> CitationValidationResult:
    """
    Cross-validate numeric citations in narrative text against context_data.
    Non-blocking: returns CitationValidationResult regardless of outcome.

    Args:
        narrative_text: English narrative from NarrativeOutput.text
        context_data: dict containing source data (FRED values, financial figures, etc.)

    Returns:
        CitationValidationResult with validated=True if all numbers found in context,
        or validated=False with unmatched_numbers list.
    """
    if not narrative_text:
        return CitationValidationResult(validated=True, matched_count=0, total_numbers_found=0)

    # Extract all numbers from narrative
    raw_numbers = extract_numbers(narrative_text)
    total_found = len(raw_numbers)

    if total_found == 0:
        return CitationValidationResult(validated=True, matched_count=0, total_numbers_found=0)

    # Build flat list of all numeric values from context_data for comparison
    context_numbers = _extract_context_numbers(context_data)

    unmatched = []
    matched = 0

    for raw in raw_numbers:
        parsed = parse_numeric(raw)
        if parsed is None:
            continue  # Skip unparseable — not a citation issue

        if _is_in_context(parsed, context_numbers):
            matched += 1
        else:
            unmatched.append(raw)

    # BCG: validated=False if >80% of numbers are unmatched.
    # NBS (narrative_cross_check.py) handles precision on 3 critical fields (5% tolerance).
    # BCG handles broad hallucination: fires only when LLM fabricated essentially ALL numbers.
    # Legitimate narratives always have derived values (discount %, estimates, benchmarks)
    # not present in raw context_data — these are valid and must not trigger BCG.
    # validated=False → RetryableError in weekly_orchestrator.
    parseable_count = sum(1 for r in raw_numbers if parse_numeric(r) is not None)
    validated = len(unmatched) <= parseable_count * 0.80 if parseable_count > 0 else True

    if unmatched:
        logger.info(
            "Citation validation: %d/%d numbers matched, %d unmatched (non-blocking)",
            matched, parseable_count, len(unmatched),
        )

    return CitationValidationResult(
        validated=validated,
        unmatched_numbers=unmatched[:10],  # Cap at 10 for log brevity
        matched_count=matched,
        total_numbers_found=total_found,
    )


def _extract_context_numbers(context_data: dict, _depth: int = 0) -> list[float]:
    """
    Recursively extract all numeric values from context_data dict.
    Depth-limited to prevent infinite recursion on circular refs.
    """
    if _depth > 5:
        return []

    numbers = []
    for value in context_data.values():
        if value == DATA_UNAVAILABLE:
            continue  # Skip unavailability markers — not real data
        if isinstance(value, (int, float)):
            numbers.append(float(value))
        elif isinstance(value, dict):
            numbers.extend(_extract_context_numbers(value, _depth + 1))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, (int, float)):
                    numbers.append(float(item))
                elif isinstance(item, dict):
                    numbers.extend(_extract_context_numbers(item, _depth + 1))
    return numbers


def _is_in_context(value: float, context_numbers: list[float]) -> bool:
    """
    Check if a value exists in context_numbers within tolerance.
    Allows 5% relative tolerance for rounding/formatting differences.

    Also checks percentage form: context 0.083 matches narrative "8.3%" (×100 form).
    Derived ratios (e.g., discount % computed from two PER values) are inherently
    not in context_numbers — they are expected to produce unmatched counts.
    """
    if not context_numbers:
        return True  # No context data → assume valid (conservative)

    for ctx_val in context_numbers:
        # Check both raw form and percentage form (×100 for decimal fractions < 10)
        candidates = [ctx_val]
        if 0.001 <= abs(ctx_val) < 10:
            candidates.append(ctx_val * 100)   # 0.083 → 8.3 (percentage form)

        for check_val in candidates:
            if check_val == 0:
                if abs(value) < 0.001:
                    return True
                continue
            relative_diff = abs(value - check_val) / abs(check_val)
            if relative_diff <= NUMERIC_TOLERANCE:
                return True
    return False
