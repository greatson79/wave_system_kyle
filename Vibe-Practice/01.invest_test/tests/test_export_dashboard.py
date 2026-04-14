"""
tests/test_export_dashboard.py — Tests for export_dashboard + fetch_kospi_index.
English-First (P5-A).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from investscan.naver_finance import fetch_kospi_index


class TestFetchKospiIndex:

    def _make_soup(self, price: str, change: str, pct: str, direction: str = "down") -> MagicMock:
        """Build a minimal BeautifulSoup mock matching Naver Finance sise_index HTML."""
        soup = MagicMock()
        # .num_e spans: [price, change, pct]
        spans = [MagicMock(), MagicMock(), MagicMock()]
        spans[0].get_text.return_value = price
        spans[1].get_text.return_value = change
        spans[2].get_text.return_value = pct
        soup.select.return_value = spans
        # direction class
        em = MagicMock()
        em.get.return_value = [f"no_{direction}"]
        soup.select_one.return_value = em
        return soup

    def test_returns_dict_with_expected_keys(self):
        soup = self._make_soup("5,801.71", "70.63", "1.20%")
        with patch("investscan.naver_finance._fetch", return_value=soup):
            result = fetch_kospi_index()
        assert result is not None
        assert result["current"] == "5,801.71"
        assert result["change"] == "70.63"
        assert result["change_pct"] == "1.20%"
        assert result["direction"] == "down"

    def test_returns_none_on_network_failure(self):
        with patch("investscan.naver_finance._fetch", return_value=None):
            result = fetch_kospi_index()
        assert result is None
