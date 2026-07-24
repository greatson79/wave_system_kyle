"""
tests/test_agent_consensus.py — P1 Critical TDD suite for agent_consensus.py.

Focus: select_confirmed_stocks() per-sector minimum-1 guarantee.
Production bug: CAT_A_CAP=5 exhausted by telecom(3)+power_infra(2) before
financials can contribute any stocks, despite financials qualifying (conf >= 0.65).

Target coverage: 95%.
All test names, assertions, and comments in English (P5-A).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from investscan.agent_consensus import (
    CAT_A_CAP,
    CAT_B_CAP,
    CONSENSUS_CAT_A_THRESHOLD,
    CONSENSUS_CAT_B_THRESHOLD,
    select_confirmed_stocks,
)

SECTOR_MAP = Path("config/sector_stock_map.yaml")

# Known codes from sector_stock_map.yaml (verified 2026-06-10)
_TELECOM_A_CODES      = {"017670", "030200", "032640"}                         # 3 hint=A
_POWER_INFRA_A_CODES  = {"267260", "298040", "010120"}                         # 3 hint=A
_POWER_INFRA_B_CODES  = {"103590", "011690"}                                   # 2 hint=B
_FINANCIALS_A_CODES   = {"105560", "055550", "086790", "316140", "032830"}     # 5 hint=A


def _conf(**kwargs: float) -> dict[str, float]:
    """Build a final_confidence dict. Unlisted sectors default to 0.0."""
    from investscan.agent_consensus import ALL_SECTORS
    base: dict[str, float] = {s: 0.0 for s in ALL_SECTORS}
    base.update(kwargs)
    return base


# ═══════════════════════════════════════════════════════════════════════════════
# Production bug regression: financials cap exhaustion
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapExhaustionRegression:
    """
    Regression suite for the production bug where telecom(3) + power_infra(2)
    filled CAT_A_CAP=5 before financials could add any stocks.
    """

    def test_financials_gets_at_least_one_stock_when_cap_would_fill(self):
        """
        BUG SCENARIO: telecom(0.759) + power_infra(0.708) together have 5+ hint=A
        stocks and previously exhausted CAT_A_CAP before financials(0.660) could enter.

        GUARANTEE: with per-sector min-1 logic, at least one financials code must
        appear in cat_a.
        """
        confidence = _conf(
            telecom=0.759,
            power_infrastructure=0.708,
            financials=0.660,
        )
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert any(code in _FINANCIALS_A_CODES for code in cat_a), (
            f"financials must have >= 1 stock in cat_a after fix. Got cat_a={cat_a}"
        )

    def test_all_three_qualifying_sectors_represented(self):
        """Each of the 3 qualifying sectors must contribute at least 1 stock to cat_a."""
        confidence = _conf(
            telecom=0.759,
            power_infrastructure=0.708,
            financials=0.660,
        )
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert any(c in _TELECOM_A_CODES for c in cat_a),       "telecom: 0 stocks in cat_a"
        assert any(c in _POWER_INFRA_A_CODES for c in cat_a),   "power_infra: 0 stocks in cat_a"
        assert any(c in _FINANCIALS_A_CODES for c in cat_a),    "financials: 0 stocks in cat_a"

    def test_cap_still_respected_with_three_sectors(self):
        """Total cat_a stocks must not exceed CAT_A_CAP regardless of sector count."""
        confidence = _conf(
            telecom=0.759,
            power_infrastructure=0.708,
            financials=0.660,
        )
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_a) <= CAT_A_CAP, (
            f"cat_a length {len(cat_a)} exceeds CAT_A_CAP={CAT_A_CAP}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Per-sector minimum-1 guarantee (general cases)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerSectorMinimumGuarantee:
    """General per-sector min-1 guarantee tests for select_confirmed_stocks."""

    def test_single_qualifying_sector_gets_stocks(self):
        """Single cat_a sector receives its stocks (up to cap)."""
        confidence = _conf(telecom=0.760)
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_a) >= 1, "Single qualifying sector must produce >= 1 cat_a stock"
        assert all(c in _TELECOM_A_CODES for c in cat_a), (
            f"Expected only telecom codes, got {cat_a}"
        )

    def test_two_qualifying_sectors_both_represented(self):
        """Two cat_a sectors must each have >= 1 stock."""
        confidence = _conf(telecom=0.760, financials=0.660)
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert any(c in _TELECOM_A_CODES for c in cat_a),    "telecom missing from cat_a"
        assert any(c in _FINANCIALS_A_CODES for c in cat_a), "financials missing from cat_a"

    def test_highest_confidence_sector_fills_extra_slots(self):
        """After min-1 pass, remaining slots go to highest-confidence sector first."""
        confidence = _conf(telecom=0.760, financials=0.660)
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        # telecom has higher confidence → should dominate the extra slots
        telecom_count = sum(1 for c in cat_a if c in _TELECOM_A_CODES)
        financials_count = sum(1 for c in cat_a if c in _FINANCIALS_A_CODES)
        assert telecom_count >= financials_count, (
            f"Higher-confidence telecom should fill more slots. "
            f"Got telecom={telecom_count}, financials={financials_count}"
        )

    def test_excess_qualifying_sectors_respect_cap(self):
        """More qualifying sectors than CAT_A_CAP still respects the cap."""
        confidence = _conf(
            telecom=0.80,
            financials=0.76,
            power_infrastructure=0.74,
            semiconductor=0.72,
            defense=0.70,
            biotech=0.68,
            cybersecurity=0.67,
        )
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_a) <= CAT_A_CAP


# ═══════════════════════════════════════════════════════════════════════════════
# hint=B stocks must not enter cat_a
# ═══════════════════════════════════════════════════════════════════════════════

class TestHintBNeverInCatA:
    """hint=B stocks from cat_a sectors must be demoted to cat_b, never cat_a."""

    def test_power_infra_hint_b_stocks_not_in_cat_a(self):
        """power_infrastructure hint=B stocks (103590, 011690) must not appear in cat_a."""
        confidence = _conf(power_infrastructure=0.760)
        cat_a, cat_b = select_confirmed_stocks(confidence, SECTOR_MAP)
        for code in _POWER_INFRA_B_CODES:
            assert code not in cat_a, (
                f"hint=B code {code} must not appear in cat_a. Got cat_a={cat_a}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Deduplication
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeduplication:
    """No code should appear in both cat_a and cat_b, and no duplicates within each."""

    def test_no_duplicate_codes_in_cat_a(self):
        confidence = _conf(telecom=0.760, power_infrastructure=0.710, financials=0.660)
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_a) == len(set(cat_a)), f"Duplicates in cat_a: {cat_a}"

    def test_no_duplicate_codes_in_cat_b(self):
        confidence = _conf(semiconductor=0.58, cybersecurity=0.55)
        _, cat_b = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_b) == len(set(cat_b)), f"Duplicates in cat_b: {cat_b}"

    def test_no_overlap_between_cat_a_and_cat_b(self):
        confidence = _conf(
            telecom=0.760,
            financials=0.660,
            semiconductor=0.58,
        )
        cat_a, cat_b = select_confirmed_stocks(confidence, SECTOR_MAP)
        overlap = set(cat_a) & set(cat_b)
        assert not overlap, f"Overlap between cat_a and cat_b: {overlap}"


# ═══════════════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases: empty input, no qualifying sectors, missing YAML."""

    def test_empty_confidence_returns_empty_lists(self):
        cat_a, cat_b = select_confirmed_stocks({}, SECTOR_MAP)
        assert cat_a == []
        assert cat_b == []

    def test_no_sectors_above_cat_a_threshold(self):
        confidence = _conf(telecom=0.50, financials=0.55)
        cat_a, _ = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert cat_a == []

    def test_missing_yaml_returns_empty_lists(self, tmp_path):
        missing = tmp_path / "nonexistent.yaml"
        cat_a, cat_b = select_confirmed_stocks({"telecom": 0.80}, missing)
        assert cat_a == []
        assert cat_b == []

    def test_cat_b_sectors_populated(self):
        """Sectors in [0.50, 0.65) range produce cat_b stocks."""
        confidence = _conf(semiconductor=0.58, cybersecurity=0.55)
        _, cat_b = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_b) >= 1, "cat_b should have stocks from sectors in [0.50, 0.65)"

    def test_cat_b_does_not_exceed_cap(self):
        confidence = _conf(
            semiconductor=0.62,
            cybersecurity=0.60,
            defense=0.58,
            biotech=0.55,
            shipbuilding=0.52,
        )
        _, cat_b = select_confirmed_stocks(confidence, SECTOR_MAP)
        assert len(cat_b) <= CAT_B_CAP


# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_cat_a_threshold(self):
        assert CONSENSUS_CAT_A_THRESHOLD == 0.65

    def test_cat_b_threshold(self):
        assert CONSENSUS_CAT_B_THRESHOLD == 0.50

    def test_cat_a_cap(self):
        assert CAT_A_CAP == 5

    def test_cat_b_cap(self):
        assert CAT_B_CAP == 5
