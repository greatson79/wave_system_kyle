"""
investscan/signal_bridge.py — Route STEEPs signals to investment sectors.
DG-11: E_env → industrials/materials; lowercase 's' → sector-specific routing.
English-First (P5-A). Python-First (P6): routing table is static Python dict.
"""
from __future__ import annotations

from investscan.schema import UnifiedSignal

# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------
STEEPS_TO_SECTOR: dict[str, list[str]] = {
    "S": ["healthcare", "consumer"],
    "T": ["technology", "semiconductor"],
    "E": ["financials", "real_estate"],
    "E_env": ["industrials", "materials", "energy"],  # DG-11: E_env distinct from E
    "P": ["defense", "technology", "energy"],
    "s": [],  # sector-specific: uses UnifiedSignal.sector field directly
}


def route(signal: UnifiedSignal) -> list[str]:
    """
    Return the target investment sectors for a single UnifiedSignal.

    Routing rules:
    - "s" (lowercase) → [signal.sector]  (sector-specific override, DG-11)
    - Known STEEPS category → STEEPS_TO_SECTOR[category]
    - Unknown category → []

    Args:
        signal: A normalised UnifiedSignal instance.

    Returns:
        List of sector strings the signal should be routed to.
    """
    category = signal.steeps_category
    if category == "s":
        return [signal.sector] if signal.sector else []
    return list(STEEPS_TO_SECTOR.get(category, []))


def route_batch(
    signals: list[UnifiedSignal],
) -> dict[str, list[UnifiedSignal]]:
    """
    Route a batch of signals and group them by sector.

    Args:
        signals: List of UnifiedSignal instances.

    Returns:
        Dict mapping sector name → list of signals that route to that sector.
    """
    result: dict[str, list[UnifiedSignal]] = {}
    for signal in signals:
        for sector in route(signal):
            result.setdefault(sector, []).append(signal)
    return result


def filter_by_confidence(
    signals: list[UnifiedSignal],
    threshold: float = 0.6,
) -> list[UnifiedSignal]:
    """
    Remove signals whose confidence score is strictly below *threshold*.

    Args:
        signals:   List of UnifiedSignal instances.
        threshold: Minimum confidence required (inclusive).  Default 0.6.

    Returns:
        Filtered list containing only signals with confidence >= threshold.
    """
    return [s for s in signals if s.confidence >= threshold]
