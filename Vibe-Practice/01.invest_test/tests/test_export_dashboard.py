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


from investscan.export_dashboard import load_watchlist, load_kospi_forecast, assemble_dashboard_data, render_html, DashboardData

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


MOCK_STOCK_INFO = {
    "017670": {
        "ticker": "017670", "name": "SK텔레콤",
        "current_price": "60,000", "change_pct": "+1.50%",
        "direction": "up", "change": "900",
        "prev_close": "", "open_price": "", "high": "", "low": "",
        "volume": "", "market_cap": "", "per": "", "eps": "",
        "foreign_ratio": "", "op_income_growth": "", "roe": "",
        "pbr": "", "revenue_100m": "", "fetched_at": "2026-04-09T10:00:00",
    },
    "053800": {
        "ticker": "053800", "name": "안랩",
        "current_price": "85,000", "change_pct": "-0.50%",
        "direction": "down", "change": "430",
        "prev_close": "", "open_price": "", "high": "", "low": "",
        "volume": "", "market_cap": "", "per": "", "eps": "",
        "foreign_ratio": "", "op_income_growth": "", "roe": "",
        "pbr": "", "revenue_100m": "", "fetched_at": "2026-04-09T10:00:00",
    },
    "012450": {
        "ticker": "012450", "name": "한화에어로스페이스",
        "current_price": "550,000", "change_pct": "-2.43%",
        "direction": "down", "change": "13700",
        "prev_close": "", "open_price": "", "high": "", "low": "",
        "volume": "", "market_cap": "", "per": "", "eps": "",
        "foreign_ratio": "", "op_income_growth": "", "roe": "",
        "pbr": "", "revenue_100m": "", "fetched_at": "2026-04-09T10:00:00",
    },
}

MOCK_KOSPI = {
    "current": "5,801.71", "change": "70.63",
    "change_pct": "1.20%", "direction": "down",
}


class TestAssembleDashboardData:

    def _write_fixtures(self, tmp_path):
        wl = tmp_path / "confirmed_watchlist_2026-04-09.json"
        wl.write_text(json.dumps(WATCHLIST_FIXTURE), encoding="utf-8")
        rpt = tmp_path / "weekly-report-2026-04-09.md"
        rpt.write_text(REPORT_FIXTURE, encoding="utf-8")

    def test_cat_a_cards_populated(self, tmp_path):
        self._write_fixtures(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks",
                   return_value=MOCK_STOCK_INFO), \
             patch("investscan.export_dashboard.fetch_kospi_index",
                   return_value=MOCK_KOSPI):
            data = assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path,
            )
        assert len(data["cat_a"]) == 2
        assert data["cat_a"][0]["ticker"] == "017670"
        assert data["cat_a"][0]["name"] == "SK텔레콤"
        assert data["cat_a"][0]["current"] == "60,000"
        assert data["cat_a"][0]["target"] == "N/A"

    def test_live_false_skips_network(self, tmp_path):
        self._write_fixtures(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks") as mock_fs, \
             patch("investscan.export_dashboard.fetch_kospi_index") as mock_ki:
            assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path, live=False,
            )
        mock_fs.assert_not_called()
        mock_ki.assert_not_called()

    def test_kospi_live_data_in_result(self, tmp_path):
        self._write_fixtures(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks",
                   return_value=MOCK_STOCK_INFO), \
             patch("investscan.export_dashboard.fetch_kospi_index",
                   return_value=MOCK_KOSPI):
            data = assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path,
            )
        assert data["kospi_current"] == "5,801.71"
        assert data["kospi_direction"] == "down"

    def test_p6_cards_have_na_prices(self, tmp_path):
        self._write_fixtures(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks",
                   return_value=MOCK_STOCK_INFO), \
             patch("investscan.export_dashboard.fetch_kospi_index",
                   return_value=MOCK_KOSPI):
            data = assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path,
            )
        assert len(data["p6_not_passed"]) == 1
        assert data["p6_not_passed"][0]["current"] == "N/A"

    def test_network_failure_returns_na_prices(self, tmp_path):
        self._write_fixtures(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks",
                   side_effect=Exception("network error")), \
             patch("investscan.export_dashboard.fetch_kospi_index",
                   side_effect=Exception("network error")):
            data = assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path,
            )
        # Should not raise — graceful degradation
        assert data["cat_a"][0]["current"] == "N/A"
        assert data["kospi_current"] == "N/A"


SAMPLE_DATA: DashboardData = {
    "date": "2026-04-09",
    "pipeline_version": "v4.0.0",
    "kospi_current": "5,801.71",
    "kospi_change_pct": "1.20%",
    "kospi_direction": "down",
    "kospi_forecast": {"low": "5,500", "base": "5,800~5,900", "high": "6,200~6,350"},
    "cat_a": [
        {"ticker": "017670", "name": "SK텔레콤", "current": "60,000",
         "change_pct": "+1.50%", "direction": "up",
         "sector": "통신", "confidence": "0.74", "target": "N/A"},
    ],
    "cat_b": [
        {"ticker": "012450", "name": "한화에어로스페이스", "current": "550,000",
         "change_pct": "-2.43%", "direction": "down",
         "sector": "방산", "confidence": "0.63", "target": "N/A"},
    ],
    "p6_not_passed": [
        {"ticker": "009540", "name": "009540", "current": "N/A",
         "change_pct": "N/A", "direction": "unknown",
         "sector": "조선", "confidence": "N/A", "target": "N/A"},
    ],
    "agent_weights": {"tech": 0.35, "korea": 0.25,
                      "valuation": 0.2, "macro": 0.15, "risk": 0.05},
    "sector_directions": {"telecom": "bullish", "energy": "bearish",
                          "technology": "neutral"},
}


class TestRenderHtml:

    def test_produces_valid_html_doctype(self):
        html = render_html(SAMPLE_DATA)
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_contains_stock_name(self):
        html = render_html(SAMPLE_DATA)
        assert "SK텔레콤" in html

    def test_contains_kospi_current(self):
        html = render_html(SAMPLE_DATA)
        assert "5,801.71" in html

    def test_contains_kospi_forecast_values(self):
        html = render_html(SAMPLE_DATA)
        assert "5,500" in html
        assert "5,800" in html
        assert "6,200" in html

    def test_contains_chartjs(self):
        html = render_html(SAMPLE_DATA)
        assert "chart.js" in html.lower()

    def test_contains_agent_weights(self):
        html = render_html(SAMPLE_DATA)
        assert "0.35" in html

    def test_sector_direction_telecom_present(self):
        html = render_html(SAMPLE_DATA)
        assert "telecom" in html.lower()

    def test_p6_not_passed_ticker_present(self):
        html = render_html(SAMPLE_DATA)
        assert "009540" in html

    def test_date_in_header(self):
        html = render_html(SAMPLE_DATA)
        assert "2026-04-09" in html

    def test_cat_b_stock_present(self):
        html = render_html(SAMPLE_DATA)
        assert "한화에어로스페이스" in html
