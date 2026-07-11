"""
investscan/dedup.py — Content-hash deduplication for signal data.
DG-09: source field included in hash computation.
English-First (P5-A). Python-First (P6): deterministic hash logic only.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


def compute_hash(text: str, source: str = "") -> str:
    """
    Compute SHA-256 hash over the concatenation of text and source.

    DG-09 compliance: source is always included so that identical text
    from different sources produces distinct hashes.

    Args:
        text:   The primary content string (e.g., headline or summary).
        source: The originating data source identifier.

    Returns:
        Hex-encoded SHA-256 digest string.
    """
    raw = f"{text}\x00{source}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dedup_signals(signals: list[dict]) -> list[dict]:
    """
    Remove duplicate signals based on content hash.

    Hash is computed over the "headline" field (falling back to "summary")
    combined with the "source" field per DG-09.  The first occurrence of
    each unique hash is kept; subsequent duplicates are discarded.

    Args:
        signals: List of raw signal dicts.

    Returns:
        Deduplicated list preserving insertion order of first occurrences.
    """
    seen: set[str] = set()
    result: list[dict] = []
    for signal in signals:
        text = signal.get("headline") or signal.get("summary") or ""
        source = signal.get("source") or ""
        h = compute_hash(text, source)
        if h not in seen:
            seen.add(h)
            result.append(signal)
    return result


@dataclass
class DeduplicationResult:
    """Summary statistics produced by dedup_with_stats()."""

    original_count: int
    deduplicated_count: int
    removed_count: int


def dedup_with_stats(signals: list[dict]) -> DeduplicationResult:
    """
    Deduplicate signals and return counts.

    Args:
        signals: List of raw signal dicts.

    Returns:
        DeduplicationResult with original, deduplicated, and removed counts.
    """
    deduped = dedup_signals(signals)
    original = len(signals)
    deduped_count = len(deduped)
    return DeduplicationResult(
        original_count=original,
        deduplicated_count=deduped_count,
        removed_count=original - deduped_count,
    )
