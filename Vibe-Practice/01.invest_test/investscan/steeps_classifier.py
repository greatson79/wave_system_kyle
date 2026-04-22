"""
investscan/steeps_classifier.py — Python keyword-based STEEPs classification.
P1 Critical (95% TDD required). P6 Python-First: NO LLM calls in classify().
keyword_lookup table is the single source of truth for classification logic.

STEEPs categories: S(Social), T(Technology), E(Economic), E_env(Environmental), P(Political), s(sector-specific)
IMPORTANT: lowercase 's' (sector-specific) is DISTINCT from uppercase 'S' (Social).
"""
from __future__ import annotations

import logging
from collections import Counter

from investscan.schema import UnifiedSignal

logger = logging.getLogger(__name__)

# Single source of truth for classification logic — NO LLM calls in classify()
KEYWORD_LOOKUP: dict[str, list[str]] = {
    "S": ["social", "aging", "population", "demographic", "healthcare demand", "consumer behavior", "workforce", "lifestyle"],
    "T": ["technology", "AI", "semiconductor", "LLM", "chip", "data center", "automation", "digital", "HBM", "GPU"],
    "E": ["economic", "GDP", "interest rate", "Fed", "inflation", "unemployment", "CPI", "yield", "credit", "monetary"],
    "E_env": ["environmental", "carbon", "ESG", "climate", "renewable", "emission", "regulation", "sustainability", "EV battery"],
    "P": ["political", "trade", "tariff", "geopolitical", "sanction", "export restriction", "policy", "election", "US-China"],
    "s": ["sector", "industry", "supply chain", "inventory", "market share", "earnings", "valuation", "M&A"],
}

# Pre-compute lowercase keyword lists for fast case-insensitive matching.
# Stored as: {category: [kw_lower, ...]}
_LOOKUP_LOWER: dict[str, list[str]] = {
    cat: [kw.lower() for kw in kws]
    for cat, kws in KEYWORD_LOOKUP.items()
}


def classify(text: str | None) -> str:
    """
    Classify *text* into one of the STEEPs category codes using keyword lookup.

    Rules
    -----
    - Case-insensitive matching against KEYWORD_LOOKUP.
    - Lowercase 's' (sector-specific) is only matched by keywords in KEYWORD_LOOKUP["s"]
      (e.g., "sector", "industry") — NOT by Social ("S") keywords.
    - If multiple categories match, return the one with the highest keyword-hit frequency.
    - Ties are broken by iteration order of KEYWORD_LOOKUP (stable in CPython 3.7+).
    - Empty string or None → "unknown".
    - No LLM calls — pure keyword matching.

    Parameters
    ----------
    text:
        Input text to classify.  May be None or empty.

    Returns
    -------
    str
        Category code: "S" | "T" | "E" | "E_env" | "P" | "s" | "unknown"
    """
    if not text:
        return "unknown"

    text_lower = text.lower()
    hit_counts: Counter[str] = Counter()

    for cat, keywords_lower in _LOOKUP_LOWER.items():
        for kw in keywords_lower:
            if kw in text_lower:
                hit_counts[cat] += 1

    if not hit_counts:
        return "unknown"

    # Return category with highest hit count (Counter.most_common preserves insertion order
    # for equal counts in Python 3.7+ because Counter is a dict subclass).
    best_category = hit_counts.most_common(1)[0][0]
    logger.debug("classify: text=%r → %s (hits=%s)", text[:60], best_category, dict(hit_counts))
    return best_category


def classify_signal(signal: UnifiedSignal) -> str:
    """
    Classify a UnifiedSignal by its summary text.

    Parameters
    ----------
    signal:
        A UnifiedSignal whose .summary field is used for classification.

    Returns
    -------
    str
        Category code or "unknown".
    """
    return classify(signal.summary)


def batch_classify(signals: list[UnifiedSignal]) -> list[tuple[UnifiedSignal, str]]:
    """
    Classify a list of UnifiedSignal objects.

    Parameters
    ----------
    signals:
        Iterable of UnifiedSignal instances.

    Returns
    -------
    list[tuple[UnifiedSignal, str]]
        Each tuple is (signal, category_code).
    """
    results: list[tuple[UnifiedSignal, str]] = []
    for signal in signals:
        category = classify_signal(signal)
        results.append((signal, category))
    logger.debug("batch_classify: %d signals processed", len(results))
    return results
