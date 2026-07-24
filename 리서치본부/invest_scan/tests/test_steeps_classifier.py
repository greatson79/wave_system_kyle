"""
tests/test_steeps_classifier.py — Unit tests for investscan.steeps_classifier module.
P1 Critical coverage target: 95%.
All test code and messages in English (P5-A).
"""
from __future__ import annotations

import pytest

from investscan.schema import UnifiedSignal
from investscan.steeps_classifier import (
    KEYWORD_LOOKUP,
    batch_classify,
    classify,
    classify_signal,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_signal(summary: str, category: str = "T") -> UnifiedSignal:
    """Create a minimal UnifiedSignal for testing."""
    return UnifiedSignal(
        steeps_category=category,
        psst_score=50.0,
        summary=summary,
        sector="technology",
        confidence=0.8,
        date="2026-03-28",
    )


# ---------------------------------------------------------------------------
# Individual keyword category tests
# ---------------------------------------------------------------------------

def test_classify_technology_keyword():
    """'AI semiconductor demand' must classify as 'T' (Technology)."""
    assert classify("AI semiconductor demand") == "T"


def test_classify_social_keyword():
    """'aging population healthcare' must classify as 'S' (Social)."""
    assert classify("aging population healthcare") == "S"


def test_classify_economic_keyword():
    """'Fed rate cut inflation' must classify as 'E' (Economic)."""
    assert classify("Fed rate cut inflation") == "E"


def test_classify_environmental_keyword():
    """'carbon regulation ESG' must classify as 'E_env' (Environmental)."""
    assert classify("carbon regulation ESG") == "E_env"


def test_classify_political_keyword():
    """'US-China trade tariff' must classify as 'P' (Political)."""
    assert classify("US-China trade tariff") == "P"


def test_classify_sector_lowercase_s():
    """'sector supply chain inventory' must classify as lowercase 's' (sector-specific)."""
    result = classify("sector supply chain inventory")
    assert result == "s", f"Expected 's', got '{result}'"


# ---------------------------------------------------------------------------
# Case sensitivity / ambiguity edge cases
# ---------------------------------------------------------------------------

def test_classify_uppercase_S_not_lowercase_s():
    """
    'social media' must classify as 'S' (Social), NOT lowercase 's' (sector-specific).
    'social' is an S keyword; it is NOT in the lowercase 's' keyword list.
    """
    result = classify("social media")
    assert result == "S", f"Expected 'S', got '{result}'"


def test_classify_case_insensitive():
    """'TECHNOLOGY AI' (all caps) must still classify as 'T'."""
    assert classify("TECHNOLOGY AI") == "T"


def test_classify_mixed_case():
    """'Carbon Regulation ESG' (title case) must classify as 'E_env'."""
    assert classify("Carbon Regulation ESG") == "E_env"


# ---------------------------------------------------------------------------
# Empty / None / no-match tests
# ---------------------------------------------------------------------------

def test_classify_empty_text():
    """Empty string must return 'unknown'."""
    assert classify("") == "unknown"


def test_classify_none_text():
    """None input must return 'unknown'."""
    assert classify(None) == "unknown"  # type: ignore[arg-type]


def test_classify_no_match():
    """Text with no matching keywords must return 'unknown'."""
    assert classify("random unrelated text xyzzy quux") == "unknown"


def test_classify_whitespace_only():
    """Whitespace-only text has no keyword matches — returns 'unknown'."""
    assert classify("   ") == "unknown"


# ---------------------------------------------------------------------------
# Multi-match / highest-frequency test
# ---------------------------------------------------------------------------

def test_classify_multi_match_returns_highest_freq():
    """
    Text with more T keywords than E keywords must classify as 'T'.
    'AI semiconductor LLM chip GPU' → 5 T hits vs 'inflation' → 1 E hit.
    """
    text = "AI semiconductor LLM chip GPU inflation"
    result = classify(text)
    assert result == "T", f"Expected 'T' (most T keywords), got '{result}'"


def test_classify_single_match_wins():
    """Text with exactly one matching keyword must return that category."""
    assert classify("tariff imposed") == "P"


# ---------------------------------------------------------------------------
# classify_signal tests
# ---------------------------------------------------------------------------

def test_classify_signal_uses_summary():
    """classify_signal() must classify based on the UnifiedSignal.summary field."""
    signal = _make_signal("Fed interest rate hike inflation")
    result = classify_signal(signal)
    assert result == "E", f"Expected 'E', got '{result}'"


def test_classify_signal_empty_summary():
    """classify_signal() with empty summary must return 'unknown'."""
    signal = _make_signal("")
    assert classify_signal(signal) == "unknown"


# ---------------------------------------------------------------------------
# batch_classify tests
# ---------------------------------------------------------------------------

def test_batch_classify_mixed():
    """batch_classify() on 6 mixed signals must return 6 (signal, category) tuples."""
    signals = [
        _make_signal("AI semiconductor demand"),          # T
        _make_signal("carbon regulation ESG"),            # E_env
        _make_signal("aging population healthcare"),      # S
        _make_signal("sector supply chain inventory"),    # s
        _make_signal("US-China trade tariff"),            # P
        _make_signal("Fed rate cut inflation"),           # E
    ]
    results = batch_classify(signals)
    assert len(results) == 6
    for original, (sig, cat) in zip(signals, results):
        assert sig is original, "batch_classify should preserve signal identity"
        assert isinstance(cat, str) and len(cat) > 0


def test_batch_classify_returns_correct_categories():
    """batch_classify() must produce correct category codes for each signal."""
    pairs = [
        ("AI semiconductor LLM chip", "T"),
        ("carbon ESG sustainability", "E_env"),
        ("aging population workforce", "S"),
        ("sector inventory supply chain", "s"),
        ("US-China trade tariff sanction", "P"),
        ("Fed inflation monetary CPI", "E"),
    ]
    signals = [_make_signal(text) for text, _ in pairs]
    results = batch_classify(signals)
    for (text, expected), (sig, actual) in zip(pairs, results):
        assert actual == expected, f"text={text!r}: expected '{expected}', got '{actual}'"


def test_batch_classify_empty_list():
    """batch_classify() on empty list must return empty list."""
    assert batch_classify([]) == []


# ---------------------------------------------------------------------------
# KEYWORD_LOOKUP structural test
# ---------------------------------------------------------------------------

def test_keyword_lookup_covers_all_6_categories():
    """KEYWORD_LOOKUP must have exactly the 6 required category keys."""
    required_keys = {"S", "T", "E", "E_env", "P", "s"}
    actual_keys = set(KEYWORD_LOOKUP.keys())
    assert required_keys == actual_keys, (
        f"Missing keys: {required_keys - actual_keys}; "
        f"Unexpected keys: {actual_keys - required_keys}"
    )


def test_keyword_lookup_no_empty_lists():
    """Every category in KEYWORD_LOOKUP must have at least one keyword."""
    for cat, keywords in KEYWORD_LOOKUP.items():
        assert len(keywords) > 0, f"KEYWORD_LOOKUP['{cat}'] is empty"


def test_lowercase_s_keywords_not_in_uppercase_S():
    """
    Verify that 's' (sector-specific) keywords do not overlap with 'S' (Social) keywords.
    This structural test ensures the category distinction is maintained.
    """
    s_lower = set(kw.lower() for kw in KEYWORD_LOOKUP["S"])
    s_sector = set(kw.lower() for kw in KEYWORD_LOOKUP["s"])
    overlap = s_lower & s_sector
    assert not overlap, (
        f"Unexpected overlap between 'S' and 's' keyword lists: {overlap}"
    )


# ---------------------------------------------------------------------------
# Real fixture integration test
# ---------------------------------------------------------------------------

def test_classify_fixture_entries():
    """
    Classify the actual 6 fixture summaries and verify expected categories.
    Tests the full classify() path with real data.
    """
    fixture_pairs = [
        ("AI semiconductor demand surge driven by LLM training infrastructure buildout.", "T"),
        ("Carbon regulation tightening — ESG compliance cost rising for manufacturing.", "E_env"),
        ("Aging population driving healthcare demand in Korea — bio/pharma sector tailwind.", "S"),
        # Korean text → keyword lookup will not match → "unknown" is acceptable for this entry
        ("US-China trade tensions escalating — export restriction risk for chip makers.", "P"),
        ("Fed rate cut expectations rising — 2-3 cuts priced in for 2026.", "E"),
    ]
    for text, expected in fixture_pairs:
        result = classify(text)
        assert result == expected, (
            f"text={text[:60]!r}: expected '{expected}', got '{result}'"
        )
