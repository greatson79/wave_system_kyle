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

    def test_returns_dashes_when_spans_empty(self):
        soup = MagicMock()
        soup.select.return_value = []
        soup.select_one.return_value = None
        with patch("investscan.naver_finance._fetch", return_value=soup):
            result = fetch_kospi_index()
        assert result is not None
        assert result["current"] == "N/A"
        assert result["direction"] == "flat"

    def test_flat_direction_when_em_missing(self):
        soup = self._make_soup("5,801.71", "70.63", "1.20%")
        soup.select_one.return_value = None
        with patch("investscan.naver_finance._fetch", return_value=soup):
            result = fetch_kospi_index()
        assert result["direction"] == "flat"


from investscan.export_dashboard import load_watchlist, load_kospi_forecast

# ── Fixtures ──────────────────────────────────────────────────────────────────

WATCHLIST_FIXTURE = {
    "date": "2026-04-09",
    "agent_weights": {"tech": 0.35, "korea": 0.25, "valuation": 0.2,
                      "macro": 0.15, "risk": 0.05},
    "base_sector_directions": {"technology": "neutral", "telecom": "bullish",
                                "energy": "bearish"},
    "cat_a": ["017670", "053800"],
    "cat_b": ["012450"],
    "rationale": {"p6_not_passed": ["009540"]},
}

REPORT_FIXTURE = """
### 2.3 KOSPI 4주 전망 (에이전트 합의 범위)

| 시나리오 | 에이전트 합의 (원본) | **실시간 기준 수정값** |
|---------|---------------|-------------------|
| **Low** | 2,725 (오류) | **5,500** (-5.2% from 5,800) |
| **Base** | 2,860~2,875 (오류) | **5,800~5,900** (현 수준 유지) |
| **High** | 3,000~3,050 (오류) | **6,200~6,350** (52주 최고 6,347 재도전) |

*현재가 기준: KOSPI 5,801.71 (2026-04-09) / 전일 종가 5,872.34 / 52주 범위 2,284~6,347*
"""


class TestLoadWatchlist:

    def test_parses_cat_a_and_cat_b(self, tmp_path):
        p = tmp_path / "confirmed_watchlist_2026-04-09.json"
        p.write_text(json.dumps(WATCHLIST_FIXTURE), encoding="utf-8")
        data = load_watchlist("2026-04-09", temp_dir=tmp_path)
        assert data["cat_a"] == ["017670", "053800"]
        assert data["cat_b"] == ["012450"]

    def test_parses_agent_weights(self, tmp_path):
        p = tmp_path / "confirmed_watchlist_2026-04-09.json"
        p.write_text(json.dumps(WATCHLIST_FIXTURE), encoding="utf-8")
        data = load_watchlist("2026-04-09", temp_dir=tmp_path)
        assert data["agent_weights"]["tech"] == 0.35

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_watchlist("2026-04-09", temp_dir=tmp_path)


class TestLoadKospiForecast:

    def test_parses_low_base_high(self, tmp_path):
        p = tmp_path / "weekly-report-2026-04-09.md"
        p.write_text(REPORT_FIXTURE, encoding="utf-8")
        forecast = load_kospi_forecast("2026-04-09", reports_dir=tmp_path)
        assert forecast["low"] == "5,500"
        assert "5,800" in forecast["base"]
        assert "6,200" in forecast["high"]

    def test_returns_na_on_parse_failure(self, tmp_path):
        p = tmp_path / "weekly-report-2026-04-09.md"
        p.write_text("no forecast section here", encoding="utf-8")
        forecast = load_kospi_forecast("2026-04-09", reports_dir=tmp_path)
        assert forecast["low"] == "N/A"
        assert forecast["base"] == "N/A"
        assert forecast["high"] == "N/A"

    def test_returns_na_on_missing_file(self, tmp_path):
        forecast = load_kospi_forecast("2026-04-09", reports_dir=tmp_path)
        assert forecast["low"] == "N/A"
