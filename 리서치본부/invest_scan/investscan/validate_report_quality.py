"""
investscan/validate_report_quality.py — Python-first quality validation for reports.
H-4 (v3.4): 8-criterion Python regex 1st pass BEFORE LLM @reviewer call.
P6 Python-First: python_validate_first() is pure Python — no LLM.
LLM @reviewer is only called AFTER Python pass succeeds.
English-First (P5-A).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from investscan.schema import NarrativeOutput

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of python_validate_first() quality check."""

    passed: bool
    details: list[str] = field(default_factory=list)
    criteria_checked: int = 8


# Minimum text length (bytes)
MIN_TEXT_BYTES: int = 1000

# Required structural patterns by category (Python regex)
CATEGORY_A_REQUIRED: list[tuple[str, str]] = [
    (r"\d+\.?\d*\s*%", "A1: At least one percentage figure in text"),
    (r"(?:YoY|year[-\s]over[-\s]year|quarterly)", "A2: YoY or quarterly reference"),
    (r"(?:PER|P/E|price[-\s]to[-\s]earnings)", "A3: Valuation metric reference"),
    (r"(?:foreign|institutional|net\s+buy|net\s+sell)", "A4: Foreign flow reference"),
    (r"(?:risk|downside|headwind)", "A5: Risk disclosure present"),
]

CATEGORY_B_REQUIRED: list[tuple[str, str]] = [
    (r"\$\s*\d+[\.,]?\d*\s*(?:bn|billion|M|million)", "B1: Market size with dollar figure"),
    (r"(?:CAGR|compound\s+annual|growth\s+rate)", "B2: Growth rate reference"),
    (r"(?:catalyst|trigger|event|launch)", "B3: Catalyst event mentioned"),
    (r"(?:week|month|quarter)s?\s+(?:momentum|outlook|expected)", "B4: Theme duration reference"),
    (r"(?:risk|dissolution|disruption|competition)", "B5: Risk disclosure present"),
    (r"(?:disclaimer|not\s+constitute|investment\s+advice|past\s+performance)", "B6: Disclaimer present"),
]

COMMON_CHECKS: list[tuple[str, str]] = [
    (r"\S{50,}", "C1: Text is not trivially short"),
]


def python_validate_first(narrative: NarrativeOutput) -> ValidationResult:
    """
    Run 8-criterion Python regex 1st pass on NarrativeOutput.
    Must PASS before LLM @reviewer is called (P6: Python is the judge).

    Criteria checked:
      - Category A: A1-A5 (5 structural checks)
      - Category B: B1-B6 (6 structural checks)
      - Common: text length (>= 1000 bytes), sentiment_weight sentinel

    Args:
        narrative: NarrativeOutput dataclass instance

    Returns:
        ValidationResult with passed=True if all applicable criteria met.
    """
    failures = []

    # Sentinel check (absolute — cannot bypass)
    if narrative.sentiment_weight != 0.0:
        failures.append(f"SENTINEL VIOLATION: sentiment_weight={narrative.sentiment_weight} (must be 0.0)")

    # Text length check
    text_bytes = len(narrative.text.encode("utf-8"))
    if text_bytes < MIN_TEXT_BYTES:
        failures.append(f"C1: Text too short ({text_bytes} bytes, minimum {MIN_TEXT_BYTES})")

    # Category-specific structural checks
    if narrative.category == "A":
        required_patterns = CATEGORY_A_REQUIRED
    elif narrative.category == "B":
        required_patterns = CATEGORY_B_REQUIRED
    else:
        failures.append(f"Unknown category: {narrative.category}")
        required_patterns = []

    for pattern, description in required_patterns:
        if not re.search(pattern, narrative.text, re.IGNORECASE):
            failures.append(f"Missing: {description}")

    # Mandatory fields check (category-specific, mirrors content_gate A1-A5 / B1-B6)
    if narrative.category == "A":
        if not narrative.yoy_growth:
            failures.append("A-field: yoy_growth is empty")
        if not narrative.per_vs_sector:
            failures.append("A-field: per_vs_sector is empty")
        if not narrative.foreign_flow_direction:
            failures.append("A-field: foreign_flow_direction is empty")
        if not narrative.downside_risk:
            failures.append("A-field: downside_risk is empty")
        if not narrative.direction:
            failures.append("A-field: direction is empty")
    elif narrative.category == "B":
        if not narrative.market_size:
            failures.append("B-field: market_size is empty")
        if not narrative.stock_positioning:
            failures.append("B-field: stock_positioning is empty")
        if not narrative.catalyst:
            failures.append("B-field: catalyst is empty")
        if not narrative.theme_duration:
            failures.append("B-field: theme_duration is empty")
        if not narrative.dissolution_risk:
            failures.append("B-field: dissolution_risk is empty")
        if not narrative.disclaimer:
            failures.append("B-field: disclaimer is empty")

    passed = len(failures) == 0
    if not passed:
        logger.info("Python validation failed: %d criteria unmet", len(failures))
    return ValidationResult(passed=passed, details=failures)


def validate_bear_case_position(report_text: str) -> bool:
    """
    v3.6 I-12: Validate Bear Case section is at bottom of report (above disclaimer).
    Returns True if Bear Case is correctly positioned.
    """
    bear_idx = report_text.find("⚠️")
    disclaimer_idx = report_text.rfind("disclaimer", 0, len(report_text))

    if bear_idx == -1:
        return True  # No Bear Case section — acceptable

    if disclaimer_idx == -1:
        return True  # No disclaimer found — can't validate position

    # Bear Case should appear BEFORE disclaimer
    return bear_idx < disclaimer_idx
