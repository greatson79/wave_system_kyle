"""
tests/test_dedup.py — Tests for investscan/dedup.py
Standard 85% coverage. English-First (P5-A).
DG-09: verifies source field is included in hash computation.
"""
import pytest

from investscan.dedup import (
    DeduplicationResult,
    compute_hash,
    dedup_signals,
    dedup_with_stats,
)


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_deterministic():
    """Same text + source must always produce the same hash."""
    h1 = compute_hash("Fed raises rates by 50bps", "reuters")
    h2 = compute_hash("Fed raises rates by 50bps", "reuters")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest length


def test_compute_hash_includes_source():
    """Same text with different sources must produce different hashes (DG-09)."""
    h_reuters = compute_hash("Oil prices surge", "reuters")
    h_bloomberg = compute_hash("Oil prices surge", "bloomberg")
    assert h_reuters != h_bloomberg


def test_compute_hash_empty_source():
    """Empty source is a valid case and must not raise."""
    h = compute_hash("Some headline", "")
    assert isinstance(h, str)
    assert len(h) == 64


# ---------------------------------------------------------------------------
# dedup_signals
# ---------------------------------------------------------------------------

def test_dedup_removes_exact_duplicates():
    """3 signals where 2 share the same headline+source → 2 returned."""
    signals = [
        {"headline": "Samsung Q1 beats estimates", "source": "reuters"},
        {"headline": "Samsung Q1 beats estimates", "source": "reuters"},  # duplicate
        {"headline": "Hyundai EV sales jump", "source": "bloomberg"},
    ]
    result = dedup_signals(signals)
    assert len(result) == 2


def test_dedup_preserves_first_occurrence():
    """When a duplicate exists, the first occurrence must be kept."""
    signals = [
        {"headline": "KOSPI rises 1%", "source": "yonhap", "rank": 1},
        {"headline": "KOSPI rises 1%", "source": "yonhap", "rank": 2},
    ]
    result = dedup_signals(signals)
    assert len(result) == 1
    assert result[0]["rank"] == 1


def test_dedup_empty_list():
    """Empty input must return empty list without error."""
    assert dedup_signals([]) == []


def test_dedup_no_duplicates():
    """All-unique signals must return a list of the same count."""
    signals = [
        {"headline": f"Story number {i}", "source": "reuters"}
        for i in range(5)
    ]
    result = dedup_signals(signals)
    assert len(result) == 5


def test_dedup_source_field_in_hash():
    """Same headline but different source must NOT be deduped (DG-09)."""
    signals = [
        {"headline": "Rate cut imminent", "source": "reuters"},
        {"headline": "Rate cut imminent", "source": "bloomberg"},
    ]
    result = dedup_signals(signals)
    assert len(result) == 2


def test_dedup_fallback_to_summary_field():
    """When 'headline' is absent, 'summary' field should be used for hashing."""
    signals = [
        {"summary": "Inflation cooling down", "source": "fred"},
        {"summary": "Inflation cooling down", "source": "fred"},  # duplicate
        {"summary": "GDP growth stable", "source": "fred"},
    ]
    result = dedup_signals(signals)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# dedup_with_stats
# ---------------------------------------------------------------------------

def test_dedup_with_stats_counts_correct():
    """removed_count must equal original_count - deduplicated_count."""
    signals = [
        {"headline": "Signal A", "source": "src1"},
        {"headline": "Signal A", "source": "src1"},  # duplicate
        {"headline": "Signal B", "source": "src1"},
        {"headline": "Signal B", "source": "src1"},  # duplicate
        {"headline": "Signal C", "source": "src1"},
    ]
    result = dedup_with_stats(signals)
    assert isinstance(result, DeduplicationResult)
    assert result.original_count == 5
    assert result.deduplicated_count == 3
    assert result.removed_count == 2
    assert result.removed_count == result.original_count - result.deduplicated_count


def test_dedup_with_stats_no_removals():
    """All unique signals must report removed_count == 0."""
    signals = [
        {"headline": f"Unique story {i}", "source": "reuters"}
        for i in range(3)
    ]
    stats = dedup_with_stats(signals)
    assert stats.original_count == 3
    assert stats.deduplicated_count == 3
    assert stats.removed_count == 0
