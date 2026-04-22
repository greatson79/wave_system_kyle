"""
investscan/compliance_filter.py — Python regex compliance filter for investment text.
P1 Critical (95% TDD required). P6 Python-First: NO LLM in scan() or filter_report().
H-1: PROHIBITION_PATTERNS contains all 10 prohibited expression patterns.
sentiment_weight parameter is accepted but NEVER modifies output (sentinel enforcement).
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# H-1: Exactly 10 prohibited expression patterns
# ---------------------------------------------------------------------------
PROHIBITION_PATTERNS: list[tuple[str, str]] = [
    (r"매수\s*추천", "buy recommendation"),
    (r"목표가\s*\d+", "price target with number"),
    (r"확실한\s*상승", "guaranteed rise"),
    (r"매도\s*권고", "sell recommendation"),
    (r"강력\s*매수", "strong buy"),
    (r"손절\s*라인", "stop-loss line advisory"),
    (r"급등\s*예상", "expected surge"),
    (r"\d+%\s*수익\s*보장", "guaranteed return percentage"),
    (r"must\s+buy", "must buy (English)"),
    (r"guaranteed\s+return", "guaranteed return (English)"),
]

# Pre-compile patterns for performance
_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(pattern, re.IGNORECASE | re.UNICODE), description)
    for pattern, description in PROHIBITION_PATTERNS
]


def scan(text: str) -> list[tuple[str, str]]:
    """
    Scan *text* for prohibited investment advisory expressions.

    Pure Python regex implementation — zero LLM calls.
    Case-insensitive matching via re.IGNORECASE.

    Args:
        text: The investment report or advisory text to scan.

    Returns:
        List of (matched_text, description) tuples for each violation found.
        Empty list if no violations or if text is empty.
    """
    if not text:
        return []

    violations: list[tuple[str, str]] = []
    for compiled_pattern, description in _COMPILED_PATTERNS:
        for match in compiled_pattern.finditer(text):
            violations.append((match.group(0), description))
    return violations


def filter_report(
    text: str,
    sentiment_weight: float,  # ACCEPTED but IGNORED — sentinel must be 0.0
) -> tuple[bool, list[tuple[str, str]]]:
    """
    Evaluate whether *text* is compliant with investment advisory regulations.

    sentinel_weight is accepted in the function signature for schema compatibility
    but is NEVER used to modify output.  The caller is responsible for ensuring
    sentiment_weight == 0.0 per the NarrativeOutput sentinel rule.

    Args:
        text:             The text to evaluate.
        sentiment_weight: Accepted for interface compatibility; IGNORED entirely.

    Returns:
        Tuple of (is_compliant, violations) where:
            is_compliant: True if no prohibited patterns were found.
            violations:   List of (matched_text, description) tuples.
    """
    # sentiment_weight is intentionally not referenced here (sentinel enforcement)
    violations = scan(text)
    is_compliant = len(violations) == 0
    return is_compliant, violations
