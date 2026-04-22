"""
tests/test_signal_bridge.py — Tests for investscan/signal_bridge.py
Standard 85% coverage. English-First (P5-A).
DG-11: verifies E_env and lowercase 's' routing correctness.
"""
import pytest

from investscan.schema import UnifiedSignal
from investscan.signal_bridge import (
    STEEPS_TO_SECTOR,
    filter_by_confidence,
    route,
    route_batch,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_signal(steeps: str, sector: str = "technology", confidence: float = 0.8) -> UnifiedSignal:
    return UnifiedSignal(
        steeps_category=steeps,
        psst_score=50.0,
        summary="Test signal summary",
        sector=sector,
        confidence=confidence,
        date="2026-03-29",
        source="envscan",
    )


# ---------------------------------------------------------------------------
# route()
# ---------------------------------------------------------------------------

def test_route_technology():
    """T category must route to technology and semiconductor."""
    signal = make_signal("T")
    result = route(signal)
    assert result == ["technology", "semiconductor"]


def test_route_e_env_not_e():
    """E_env must route to industrials and materials (DG-11)."""
    signal = make_signal("E_env")
    result = route(signal)
    assert "industrials" in result
    assert "materials" in result


def test_route_e_env_excludes_financials():
    """E_env must NOT route to financials — that belongs to E (DG-11)."""
    signal = make_signal("E_env")
    result = route(signal)
    assert "financials" not in result


def test_route_lowercase_s_uses_sector_field():
    """Lowercase 's' must return [signal.sector] directly."""
    signal = make_signal("s", sector="semiconductor")
    result = route(signal)
    assert result == ["semiconductor"]


def test_route_lowercase_s_empty_sector():
    """Lowercase 's' with empty sector must return []."""
    signal = make_signal("s", sector="")
    result = route(signal)
    assert result == []


def test_route_uppercase_S_social():
    """Uppercase 'S' (Social) must route to healthcare and consumer."""
    signal = make_signal("S")
    result = route(signal)
    assert result == ["healthcare", "consumer"]


def test_route_e_financials():
    """E (Economic/Financial) must route to financials and real_estate."""
    signal = make_signal("E")
    result = route(signal)
    assert "financials" in result
    assert "real_estate" in result


def test_route_p_defense():
    """P (Political) must route to defense."""
    signal = make_signal("P")
    result = route(signal)
    assert "defense" in result


def test_route_unknown_returns_empty():
    """An unknown STEEPS category must return an empty list."""
    signal = make_signal("X_unknown")
    result = route(signal)
    assert result == []


# ---------------------------------------------------------------------------
# route_batch()
# ---------------------------------------------------------------------------

def test_route_batch_groups_by_sector():
    """3 signals across different categories must produce a sector-keyed dict."""
    signals = [
        make_signal("T"),          # → technology, semiconductor
        make_signal("S"),          # → healthcare, consumer
        make_signal("E_env"),      # → industrials, materials, energy
    ]
    result = route_batch(signals)
    assert isinstance(result, dict)
    assert "technology" in result
    assert "semiconductor" in result
    assert "healthcare" in result
    assert "industrials" in result


def test_route_batch_values_are_signal_lists():
    """Each value in the route_batch dict must be a list of UnifiedSignal."""
    signals = [make_signal("T"), make_signal("T")]
    result = route_batch(signals)
    for sector, sig_list in result.items():
        assert isinstance(sig_list, list)
        for s in sig_list:
            assert isinstance(s, UnifiedSignal)


def test_route_batch_empty():
    """Empty input must return an empty dict."""
    assert route_batch([]) == {}


def test_route_batch_lowercase_s():
    """Lowercase 's' signals must be grouped under their specific sector."""
    signals = [
        make_signal("s", sector="semiconductor"),
        make_signal("s", sector="healthcare"),
    ]
    result = route_batch(signals)
    assert "semiconductor" in result
    assert "healthcare" in result


# ---------------------------------------------------------------------------
# filter_by_confidence()
# ---------------------------------------------------------------------------

def test_filter_by_confidence_threshold():
    """Signals with confidence < 0.6 must be removed."""
    signals = [
        make_signal("T", confidence=0.9),
        make_signal("S", confidence=0.3),   # below threshold
        make_signal("E", confidence=0.6),   # exactly at threshold — kept
        make_signal("P", confidence=0.59),  # just below — removed
    ]
    result = filter_by_confidence(signals, threshold=0.6)
    assert len(result) == 2
    for s in result:
        assert s.confidence >= 0.6


def test_filter_by_confidence_default_threshold():
    """Default threshold of 0.6 must be applied when none specified."""
    signals = [
        make_signal("T", confidence=0.7),
        make_signal("S", confidence=0.5),
    ]
    result = filter_by_confidence(signals)
    assert len(result) == 1
    assert result[0].confidence == 0.7


def test_filter_by_confidence_all_pass():
    """All signals above threshold must all be returned."""
    signals = [make_signal("T", confidence=0.8) for _ in range(4)]
    result = filter_by_confidence(signals, threshold=0.6)
    assert len(result) == 4


def test_filter_by_confidence_none_pass():
    """No signals meeting threshold must return empty list."""
    signals = [make_signal("T", confidence=0.3) for _ in range(3)]
    result = filter_by_confidence(signals, threshold=0.6)
    assert result == []
