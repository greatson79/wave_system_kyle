# HTML Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a self-contained interactive HTML dashboard alongside TXT/PDF reports via `python3 -m investscan.export_report --formats html`.

**Architecture:** `export_dashboard.py` owns all dashboard logic (data loading + HTML rendering); `naver_finance.py` gains `fetch_kospi_index()`; `export_report.py` calls `export_dashboard.generate()` when `html` is in the formats list. The dashboard reads `confirmed_watchlist_{DATE}.json` for portfolio/sector data, regex-parses `weekly-report-{DATE}.md` for KOSPI forecasts, and fetches live prices via `naver_finance`.

**Tech Stack:** Python 3.12, Chart.js CDN (v4), pytest, requests + BeautifulSoup (existing), TypedDict

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `investscan/naver_finance.py` | Add `fetch_kospi_index() -> KospiIndex \| None` |
| Create | `investscan/export_dashboard.py` | `DashboardData` TypedDict, data loaders, `render_html()`, `generate()` |
| Modify | `investscan/export_report.py` | Add `html` branch in `export()`, `--no-live` CLI flag |
| Create | `tests/test_export_dashboard.py` | Full test suite for export_dashboard + kospi_index |

---

## Task 1: `fetch_kospi_index()` in naver_finance.py

**Files:**
- Modify: `investscan/naver_finance.py`
- Test: `tests/test_export_dashboard.py`

- [ ] **Step 1: Write the failing test**

Add at top of new file `tests/test_export_dashboard.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test
python -m pytest tests/test_export_dashboard.py::TestFetchKospiIndex -v
```

Expected: `ImportError: cannot import name 'fetch_kospi_index'`

- [ ] **Step 3: Add `KospiIndex` TypedDict and `fetch_kospi_index()` to naver_finance.py**

Add after the `StockInfo` TypedDict (line ~78):

```python
class KospiIndex(TypedDict):
    current: str      # "5,801.71"
    change: str       # "70.63"
    change_pct: str   # "1.20%"
    direction: str    # "up" | "down" | "flat"


_KOSPI_URL = "https://finance.naver.com/sise/sise_index.naver"


def fetch_kospi_index() -> KospiIndex | None:
    """Fetch current KOSPI index price and change from Naver Finance.

    Returns KospiIndex dict or None on network/parse failure.
    """
    soup = _fetch(_KOSPI_URL, {"code": "KOSPI"})
    if soup is None:
        return None
    try:
        spans = soup.select(".num_e")
        current = _clean(spans[0].get_text()) if len(spans) > 0 else "—"
        change  = _clean(spans[1].get_text()) if len(spans) > 1 else "—"
        pct     = _clean(spans[2].get_text()) if len(spans) > 2 else "—"

        em = soup.select_one(".point_flag em")
        direction = "flat"
        if em:
            cls = em.get("class", [])
            if any("up" in c for c in cls):
                direction = "up"
            elif any("down" in c for c in cls):
                direction = "down"

        return KospiIndex(current=current, change=change,
                          change_pct=pct, direction=direction)
    except Exception:
        return None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_export_dashboard.py::TestFetchKospiIndex -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add investscan/naver_finance.py tests/test_export_dashboard.py
git commit -m "feat: add fetch_kospi_index() to naver_finance + tests"
```

---

## Task 2: `DashboardData` TypedDict + Data Loaders

**Files:**
- Create: `investscan/export_dashboard.py`
- Modify: `tests/test_export_dashboard.py`

- [ ] **Step 1: Write failing tests for `load_watchlist` and `load_kospi_forecast`**

Append to `tests/test_export_dashboard.py`:

```python
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

    def test_returns_empty_strings_on_parse_failure(self, tmp_path):
        p = tmp_path / "weekly-report-2026-04-09.md"
        p.write_text("no forecast section here", encoding="utf-8")
        forecast = load_kospi_forecast("2026-04-09", reports_dir=tmp_path)
        assert forecast["low"] == "—"
        assert forecast["base"] == "—"
        assert forecast["high"] == "—"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_export_dashboard.py::TestLoadWatchlist tests/test_export_dashboard.py::TestLoadKospiForecast -v
```

Expected: `ImportError: cannot import name 'load_watchlist'`

- [ ] **Step 3: Create `investscan/export_dashboard.py` with TypedDict + loaders**

```python
"""
export_dashboard.py — InvestScan HTML dashboard generator.

Reads confirmed_watchlist_{DATE}.json + weekly-report-{DATE}.md,
fetches live prices via naver_finance, renders a self-contained HTML file.

Usage (via export_report):
    python3 -m investscan.export_report --date 2026-04-09 --formats html
    python3 -m investscan.export_report --date 2026-04-09 --formats html --no-live

Saves to:
    ~/Desktop/Ai_works/output/투자분析제안/{DATE}_주간투자분析_대시보드.html
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict

# ── paths ──────────────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parent.parent
TEMP_DIR      = _PROJECT_ROOT / "output" / "temp"
REPORTS_DIR   = _PROJECT_ROOT / "output" / "reports"
OUTPUT_DIR    = Path.home() / "Desktop" / "Ai_works" / "output" / "투자분析제안"


# ── TypedDicts ─────────────────────────────────────────────────────────────────

class KospiForecast(TypedDict):
    low:  str   # "5,500"
    base: str   # "5,800~5,900"
    high: str   # "6,200~6,350"


class WatchlistData(TypedDict):
    date:                  str
    cat_a:                 list[str]
    cat_b:                 list[str]
    p6_not_passed:         list[str]
    agent_weights:         dict[str, float]
    base_sector_directions: dict[str, str]


class StockCard(TypedDict):
    ticker:      str
    name:        str
    current:     str   # "82,300" or "—"
    change_pct:  str   # "+1.20%" or "—"
    direction:   str   # "up" | "down" | "flat" | "unknown"
    sector:      str
    confidence:  str   # "0.74" or "—"
    target:      str   # always "—" in v1


class DashboardData(TypedDict):
    date:             str
    pipeline_version: str
    kospi_current:    str
    kospi_change_pct: str
    kospi_direction:  str
    kospi_forecast:   KospiForecast
    cat_a:            list[StockCard]
    cat_b:            list[StockCard]
    p6_not_passed:    list[StockCard]
    agent_weights:    dict[str, float]
    sector_directions: dict[str, str]


# ── data loaders ───────────────────────────────────────────────────────────────

def load_watchlist(
    date: str,
    temp_dir: Path = TEMP_DIR,
) -> WatchlistData:
    """Load confirmed_watchlist_{date}.json. Raises FileNotFoundError if missing."""
    path = temp_dir / f"confirmed_watchlist_{date}.json"
    if not path.exists():
        raise FileNotFoundError(f"Watchlist not found: {path}")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    p6_not_passed: list[str] = []
    rationale = raw.get("rationale", {})
    if isinstance(rationale, dict):
        p6_not_passed = rationale.get("p6_not_passed", [])

    return WatchlistData(
        date=raw.get("date", date),
        cat_a=raw.get("cat_a", []),
        cat_b=raw.get("cat_b", []),
        p6_not_passed=p6_not_passed,
        agent_weights=raw.get("agent_weights", {}),
        base_sector_directions=raw.get("base_sector_directions", {}),
    )


def load_kospi_forecast(
    date: str,
    reports_dir: Path = REPORTS_DIR,
) -> KospiForecast:
    """Parse KOSPI Low/Base/High from section 2.3 of the weekly report MD.

    Returns KospiForecast with "—" values if parsing fails.
    """
    path = reports_dir / f"weekly-report-{date}.md"
    empty = KospiForecast(low="—", base="—", high="—")
    if not path.exists():
        return empty

    text = path.read_text(encoding="utf-8")

    # Match the corrected-value column (last bold cell) in the 2.3 forecast table
    low_m  = re.search(r"\*\*Low\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    base_m = re.search(r"\*\*Base\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    high_m = re.search(r"\*\*High\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)

    def _extract(m: re.Match | None) -> str:
        if not m:
            return "—"
        raw = m.group(1).strip()
        # Strip parenthetical suffix like " (-5.2% from 5,800)"
        raw = re.sub(r"\s*\(.*?\)", "", raw).strip()
        return raw if raw else "—"

    return KospiForecast(
        low=_extract(low_m),
        base=_extract(base_m),
        high=_extract(high_m),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_export_dashboard.py::TestLoadWatchlist tests/test_export_dashboard.py::TestLoadKospiForecast -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add investscan/export_dashboard.py tests/test_export_dashboard.py
git commit -m "feat: add export_dashboard skeleton — TypedDicts + data loaders"
```

---

## Task 3: `fetch_stock_prices()` + `assemble_dashboard_data()`

**Files:**
- Modify: `investscan/export_dashboard.py`
- Modify: `tests/test_export_dashboard.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_export_dashboard.py`:

```python
from investscan.export_dashboard import assemble_dashboard_data

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

    def _patch_all(self, tmp_path):
        """Write fixture files and return patch context."""
        wl = tmp_path / "confirmed_watchlist_2026-04-09.json"
        wl.write_text(json.dumps(WATCHLIST_FIXTURE), encoding="utf-8")
        rpt = tmp_path / "weekly-report-2026-04-09.md"
        rpt.write_text(REPORT_FIXTURE, encoding="utf-8")
        return tmp_path

    def test_cat_a_cards_populated(self, tmp_path):
        self._patch_all(tmp_path)
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
        assert data["cat_a"][0]["target"] == "—"

    def test_live_false_skips_network(self, tmp_path):
        self._patch_all(tmp_path)
        with patch("investscan.export_dashboard.fetch_stocks") as mock_fs, \
             patch("investscan.export_dashboard.fetch_kospi_index") as mock_ki:
            assemble_dashboard_data(
                "2026-04-09",
                temp_dir=tmp_path, reports_dir=tmp_path, live=False,
            )
        mock_fs.assert_not_called()
        mock_ki.assert_not_called()

    def test_kospi_live_data_in_result(self, tmp_path):
        self._patch_all(tmp_path)
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_export_dashboard.py::TestAssembleDashboardData -v
```

Expected: `ImportError: cannot import name 'assemble_dashboard_data'`

- [ ] **Step 3: Add imports + `_make_stock_card()` + `assemble_dashboard_data()` to export_dashboard.py**

Add at the top of `investscan/export_dashboard.py` after existing imports:

```python
from investscan.naver_finance import fetch_stocks, fetch_kospi_index, KospiIndex
```

Add these functions after `load_kospi_forecast()`:

```python
# Sector confidence comes from confirmed_watchlist final_sector_confidence
_TICKER_SECTOR: dict[str, str] = {}  # populated by assemble_dashboard_data


def _make_stock_card(
    ticker: str,
    live_data: dict,          # naver StockInfo dict, may be {}
    sector: str = "—",
    confidence: str = "—",
) -> StockCard:
    info = live_data.get(ticker, {})
    return StockCard(
        ticker=ticker,
        name=info.get("name", ticker),
        current=info.get("current_price", "—"),
        change_pct=info.get("change_pct", "—"),
        direction=info.get("direction", "unknown"),
        sector=sector,
        confidence=confidence,
        target="—",
    )


def assemble_dashboard_data(
    date: str,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
    live: bool = True,
) -> DashboardData:
    """Load all data sources and assemble DashboardData.

    live=False skips network calls (for testing / --no-live mode).
    """
    wl       = load_watchlist(date, temp_dir=temp_dir)
    forecast = load_kospi_forecast(date, reports_dir=reports_dir)

    # Sector confidence map from watchlist
    all_tickers = wl["cat_a"] + wl["cat_b"] + wl["p6_not_passed"]

    # Live price fetch — Cat A + Cat B only (P6미통과 shown without price)
    live_tickers = wl["cat_a"] + wl["cat_b"]
    live_data: dict = {}
    kospi_index: KospiIndex | None = None

    if live and live_tickers:
        try:
            live_data = fetch_stocks(live_tickers)
        except Exception:
            live_data = {}
        try:
            kospi_index = fetch_kospi_index()
        except Exception:
            kospi_index = None

    # Build sector confidence lookup from watchlist
    final_conf: dict[str, float] = {}
    # Sector mapping per ticker — infer from base_sector_directions + cat assignment
    # Stored flat in watchlist; we use a best-effort approach
    sector_conf_raw = {}  # will be filled if key exists in watchlist json

    def _sector_for(ticker: str) -> str:
        return "—"  # v1: sector lookup not yet structured; shown as "—"

    def _conf_for(ticker: str) -> str:
        return "—"  # v1: per-ticker confidence not yet extracted

    cat_a_cards = [_make_stock_card(t, live_data, _sector_for(t), _conf_for(t))
                   for t in wl["cat_a"]]
    cat_b_cards = [_make_stock_card(t, live_data, _sector_for(t), _conf_for(t))
                   for t in wl["cat_b"]]
    p6_cards    = [_make_stock_card(t, {}, _sector_for(t), _conf_for(t))
                   for t in wl["p6_not_passed"]]

    return DashboardData(
        date=date,
        pipeline_version="v4.0.0",
        kospi_current=kospi_index["current"] if kospi_index else "—",
        kospi_change_pct=kospi_index["change_pct"] if kospi_index else "—",
        kospi_direction=kospi_index["direction"] if kospi_index else "unknown",
        kospi_forecast=forecast,
        cat_a=cat_a_cards,
        cat_b=cat_b_cards,
        p6_not_passed=p6_cards,
        agent_weights=wl["agent_weights"],
        sector_directions=wl["base_sector_directions"],
    )
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_export_dashboard.py::TestAssembleDashboardData -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add investscan/export_dashboard.py tests/test_export_dashboard.py
git commit -m "feat: add assemble_dashboard_data() with live price + KOSPI fetch"
```

---

## Task 4: `render_html()` — HTML 생성

**Files:**
- Modify: `investscan/export_dashboard.py`
- Modify: `tests/test_export_dashboard.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_export_dashboard.py`:

```python
from investscan.export_dashboard import render_html

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
         "sector": "통신", "confidence": "0.74", "target": "—"},
    ],
    "cat_b": [
        {"ticker": "012450", "name": "한화에어로스페이스", "current": "550,000",
         "change_pct": "-2.43%", "direction": "down",
         "sector": "방산", "confidence": "0.63", "target": "—"},
    ],
    "p6_not_passed": [
        {"ticker": "009540", "name": "009540", "current": "—",
         "change_pct": "—", "direction": "unknown",
         "sector": "조선", "confidence": "—", "target": "—"},
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
        assert "0.35" in html  # tech weight

    def test_sector_direction_bullish_rendered(self):
        html = render_html(SAMPLE_DATA)
        assert "bullish" in html.lower() or "telecom" in html.lower()

    def test_p6_not_passed_ticker_present(self):
        html = render_html(SAMPLE_DATA)
        assert "009540" in html

    def test_date_in_header(self):
        html = render_html(SAMPLE_DATA)
        assert "2026-04-09" in html
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_export_dashboard.py::TestRenderHtml -v
```

Expected: `ImportError: cannot import name 'render_html'`

- [ ] **Step 3: Add `render_html()` to export_dashboard.py**

Append to `investscan/export_dashboard.py`:

```python
# ── HTML renderer ──────────────────────────────────────────────────────────────

def _direction_arrow(direction: str) -> str:
    return {"up": "▲", "down": "▼", "flat": "–"}.get(direction, "–")


def _direction_color(direction: str) -> str:
    return {"up": "var(--green)", "down": "var(--red)", "flat": "var(--text-dim)"}.get(
        direction, "var(--text-dim)"
    )


def _sector_badge(direction: str) -> str:
    colors = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#64748b"}
    labels = {"bullish": "BULL", "bearish": "BEAR", "neutral": "—"}
    color = colors.get(direction, "#64748b")
    label = labels.get(direction, direction.upper()[:4])
    return f'<span style="color:{color};font-weight:600;font-size:11px">{label}</span>'


def _stock_cards_html(cards: list[StockCard]) -> str:
    if not cards:
        return '<p style="color:var(--text-dim);padding:16px">해당 없음</p>'
    rows = []
    for c in cards:
        arrow = _direction_arrow(c["direction"])
        color = _direction_color(c["direction"])
        rows.append(f"""
        <div class="stock-card">
          <div class="sc-header">
            <span class="sc-name">{c['name']}</span>
            <span class="sc-ticker">{c['ticker']}</span>
          </div>
          <div class="sc-price" style="color:{color}">
            {c['current']} <span class="sc-arrow">{arrow}</span>
            <span class="sc-pct">{c['change_pct']}</span>
          </div>
          <div class="sc-meta">
            섹터 {c['sector']} &nbsp;|&nbsp; 신뢰도 {c['confidence']}
            &nbsp;|&nbsp; 목표가 <span style="color:var(--text-dim)">{c['target']}</span>
          </div>
        </div>""")
    return "\n".join(rows)


def _weights_js(weights: dict[str, float]) -> str:
    labels = [f"'{k}'" for k in weights]
    values = list(weights.values())
    colors = ["'#f5c518'", "'#60a5fa'", "'#22c55e'", "'#f59e0b'", "'#ef4444'"]
    return (f"labels:[{','.join(labels)}],"
            f"data:[{','.join(str(v) for v in values)}],"
            f"backgroundColor:[{','.join(colors[:len(values)])}]")


def _sector_grid_html(directions: dict[str, str]) -> str:
    cells = []
    for sector, direction in sorted(directions.items()):
        badge = _sector_badge(direction)
        cells.append(
            f'<div class="sector-cell"><span class="sector-name">{sector}</span>'
            f'<span class="sector-dir">{badge}</span></div>'
        )
    return "\n".join(cells)


def render_html(data: DashboardData) -> str:
    """Render DashboardData into a self-contained HTML string."""
    cat_a_html    = _stock_cards_html(data["cat_a"])
    cat_b_html    = _stock_cards_html(data["cat_b"])
    p6_html       = _stock_cards_html(data["p6_not_passed"])
    sector_html   = _sector_grid_html(data["sector_directions"])
    weights_js    = _weights_js(data["agent_weights"])
    forecast      = data["kospi_forecast"]
    kospi_arrow   = _direction_arrow(data["kospi_direction"])
    kospi_color   = _direction_color(data["kospi_direction"])

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InvestScan 대시보드 — {data['date']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg:#06090f;--bg-2:#0c1220;--bg-3:#111827;
  --border:rgba(255,255,255,0.07);--border-hi:rgba(245,197,24,0.35);
  --gold:#f5c518;--gold-dim:#b38e10;
  --green:#22c55e;--red:#ef4444;--amber:#f59e0b;--blue:#60a5fa;
  --text:#e2e8f0;--text-dim:#64748b;--text-mid:#94a3b8;
  --mono:'DM Mono',monospace;--display:'Bebas Neue',sans-serif;--body:'Outfit',sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:var(--body);font-size:14px;line-height:1.6;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");pointer-events:none;z-index:0;opacity:0.6}}
.wrap{{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 32px 80px}}
/* TICKER */
.ticker{{background:var(--gold);color:#000;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.05em;padding:5px 0;overflow:hidden;white-space:nowrap;position:sticky;top:0;z-index:100}}
.ticker-inner{{display:inline-block;animation:ticker-scroll 24s linear infinite}}
.ticker-inner span{{margin:0 40px}}
@keyframes ticker-scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
/* HEADER */
.header{{padding:48px 0 32px;border-bottom:1px solid var(--border)}}
.header h1{{font-family:var(--display);font-size:48px;letter-spacing:.05em;color:var(--gold);line-height:1}}
.header .sub{{color:var(--text-mid);font-size:13px;margin-top:8px;font-family:var(--mono)}}
/* GRID */
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}}
.grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin-top:24px}}
/* CARDS */
.card{{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:24px}}
.card-title{{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:16px}}
/* TABS */
.tab-bar{{display:flex;gap:4px;margin-bottom:16px}}
.tab{{padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text-dim);font-family:var(--mono)}}
.tab.active{{background:var(--gold);color:#000;border-color:var(--gold);font-weight:600}}
.tab-content{{display:none}}.tab-content.active{{display:block}}
/* STOCK CARD */
.stock-card{{background:var(--bg-3);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:10px}}
.sc-header{{display:flex;justify-content:space-between;margin-bottom:6px}}
.sc-name{{font-weight:600;font-size:14px}}
.sc-ticker{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.sc-price{{font-size:20px;font-weight:600;font-family:var(--mono);margin-bottom:4px}}
.sc-pct{{font-size:13px;margin-left:8px}}
.sc-meta{{font-size:11px;color:var(--text-dim)}}
/* SECTOR GRID */
.sector-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}}
.sector-cell{{background:var(--bg-3);border:1px solid var(--border);border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}}
.sector-name{{font-size:12px;color:var(--text-mid);text-transform:capitalize}}
/* FORECAST */
.forecast-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}}
.forecast-row:last-child{{border-bottom:none}}
.forecast-label{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.forecast-val{{font-family:var(--mono);font-size:14px;font-weight:600}}
</style>
</head>
<body>

<!-- TICKER BAR -->
<div class="ticker">
  <div class="ticker-inner">
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
  </div>
</div>

<div class="wrap">

  <!-- HEADER -->
  <div class="header">
    <h1>INVESTSCAN</h1>
    <div class="sub">주간 투자 분析 대시보드 &nbsp;|&nbsp; {data['date']} &nbsp;|&nbsp; {data['pipeline_version']}</div>
  </div>

  <!-- ROW 1: Portfolio + KOSPI Forecast -->
  <div class="grid-2">

    <!-- P6 Portfolio -->
    <div class="card">
      <div class="card-title">P6 포트폴리오</div>
      <div class="tab-bar">
        <button class="tab active" onclick="showTab(event,'tab-a')">Cat A ({len(data['cat_a'])})</button>
        <button class="tab" onclick="showTab(event,'tab-b')">Cat B ({len(data['cat_b'])})</button>
        <button class="tab" onclick="showTab(event,'tab-p6')">P6미통과 ({len(data['p6_not_passed'])})</button>
      </div>
      <div id="tab-a" class="tab-content active">{cat_a_html}</div>
      <div id="tab-b" class="tab-content">{cat_b_html}</div>
      <div id="tab-p6" class="tab-content">{p6_html}</div>
    </div>

    <!-- KOSPI Forecast -->
    <div class="card">
      <div class="card-title">KOSPI 4주 전망</div>
      <div style="font-family:var(--mono);font-size:32px;font-weight:600;color:{kospi_color};margin-bottom:24px">
        {data['kospi_current']} <span style="font-size:16px">{kospi_arrow} {data['kospi_change_pct']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">HIGH</span>
        <span class="forecast-val" style="color:var(--green)">{forecast['high']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">BASE</span>
        <span class="forecast-val" style="color:var(--gold)">{forecast['base']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">LOW</span>
        <span class="forecast-val" style="color:var(--red)">{forecast['low']}</span>
      </div>
      <canvas id="kospiChart" style="margin-top:24px;max-height:120px"></canvas>
    </div>

  </div>

  <!-- ROW 2: Agent Weights + Sector Grid -->
  <div class="grid-2" style="margin-top:24px">

    <!-- Agent Weights Donut -->
    <div class="card">
      <div class="card-title">에이전트 가중치</div>
      <canvas id="weightsChart" style="max-height:200px"></canvas>
    </div>

    <!-- Sector Directions -->
    <div class="card">
      <div class="card-title">섹터 방향</div>
      <div class="sector-grid">{sector_html}</div>
    </div>

  </div>

</div><!-- /wrap -->

<script>
// ── Tab switching ──────────────────────────────────────────────────────────
function showTab(e, id) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

// ── Agent Weights Donut ────────────────────────────────────────────────────
new Chart(document.getElementById('weightsChart'), {{
  type: 'doughnut',
  data: {{
    {weights_js}
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ labels: {{ color: '#e2e8f0', font: {{ family: 'Outfit' }} }} }}
    }}
  }}
}});

// ── KOSPI Forecast Bar ─────────────────────────────────────────────────────
new Chart(document.getElementById('kospiChart'), {{
  type: 'bar',
  data: {{
    labels: ['LOW', 'BASE (상단)', 'HIGH'],
    datasets: [{{
      data: [
        parseFloat('{forecast['low']}'.replace(/,/g,'')),
        parseFloat('{forecast['base']}'.split('~').pop().replace(/,/g,'')),
        parseFloat('{forecast['high']}'.split('~').pop().replace(/,/g,''))
      ],
      backgroundColor: ['#ef4444aa', '#f5c518aa', '#22c55eaa'],
      borderRadius: 4
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }}
    }}
  }}
}});
</script>
</body>
</html>"""
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_export_dashboard.py::TestRenderHtml -v
```

Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add investscan/export_dashboard.py tests/test_export_dashboard.py
git commit -m "feat: add render_html() — Chart.js dark dashboard template"
```

---

## Task 5: `generate()` entry point + `export_report.py` integration

**Files:**
- Modify: `investscan/export_dashboard.py`
- Modify: `investscan/export_report.py`
- Modify: `tests/test_export_dashboard.py`

- [ ] **Step 1: Write failing test for `generate()`**

Append to `tests/test_export_dashboard.py`:

```python
from investscan.export_dashboard import generate

class TestGenerate:

    def test_writes_html_file(self, tmp_path):
        with patch("investscan.export_dashboard.assemble_dashboard_data",
                   return_value=SAMPLE_DATA), \
             patch("investscan.export_dashboard.render_html",
                   return_value="<!DOCTYPE html><html></html>"):
            out = generate(
                "2026-04-09",
                out_dir=tmp_path,
                temp_dir=tmp_path,
                reports_dir=tmp_path,
                live=False,
            )
        assert out.exists()
        assert out.name == "2026-04-09_주간투자분析_대시보드.html"
        assert "<!DOCTYPE html>" in out.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_export_dashboard.py::TestGenerate -v
```

Expected: `ImportError: cannot import name 'generate'`

- [ ] **Step 3: Add `generate()` to export_dashboard.py**

Append to `investscan/export_dashboard.py`:

```python
# ── public entry point ─────────────────────────────────────────────────────────

def generate(
    date: str,
    out_dir: Path = OUTPUT_DIR,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
    live: bool = True,
) -> Path:
    """Assemble data, render HTML, write file. Returns output Path."""
    data     = assemble_dashboard_data(date, temp_dir=temp_dir,
                                       reports_dir=reports_dir, live=live)
    html     = render_html(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date}_주간투자분析_대시보드.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
```

- [ ] **Step 4: Run test**

```bash
python -m pytest tests/test_export_dashboard.py::TestGenerate -v
```

Expected: `1 passed`

- [ ] **Step 5: Add `html` branch and `--no-live` flag to export_report.py**

In `investscan/export_report.py`:

**5a.** Add import at top (after existing imports):

```python
from investscan import export_dashboard as _dashboard
```

**5b.** In the `export()` function, add after the MD copy block (after line ~718):

```python
    if "html" in formats:
        try:
            html_path = _dashboard.generate(
                report_date,
                out_dir=out_dir,
                live=not dry_run,
            )
            results["html"] = html_path
            print(f"  ✅ HTML → {html_path}")
        except FileNotFoundError as e:
            print(f"  ⚠️  HTML 생략 — {e}")
        except Exception as e:
            print(f"  ⚠️  HTML 생성 실패 — {e}")
```

**5c.** In `main()`, update the `--formats` help string and add `--no-live`:

```python
    parser.add_argument("--formats", default="txt,pdf",
                        help="형식 선택: txt,pdf,md,html (기본: txt,pdf)")
    parser.add_argument("--no-live", action="store_true",
                        help="실시간 주가 조회 생략 (HTML 대시보드 테스트용)")
```

**5d.** Pass `--no-live` to `export()` call. Change the `dry_run` to also cover `--no-live`:

```python
    results = export(md_path, report_date, formats, out_dir,
                     enrich=args.enrich, dry_run=args.dry_run or args.no_live)
```

- [ ] **Step 6: Run full test suite to confirm no regressions**

```bash
python -m pytest tests/ -q
```

Expected: all previously passing tests still pass, new tests pass.

- [ ] **Step 7: Smoke test with real data**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test
python3 -m investscan.export_report --date 2026-04-09 --formats html --no-live
```

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
리포트 내보내기 — 2026-04-09
...
  ✅ HTML → /Users/kylechoi/Desktop/Ai_works/output/투자분析제안/2026-04-09_주간투자분析_대시보드.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- [ ] **Step 8: Open in browser and verify**

```bash
open ~/Desktop/Ai_works/output/투자분析제안/2026-04-09_주간투자분析_대시보드.html
```

Verify: ticker bar visible, Cat A tab shows stocks, KOSPI forecast values render, donut chart renders, sector grid renders.

- [ ] **Step 9: Run with live data**

```bash
python3 -m investscan.export_report --date 2026-04-09 --formats html
```

Verify: live KOSPI price shown in ticker bar and header.

- [ ] **Step 10: Commit**

```bash
git add investscan/export_dashboard.py investscan/export_report.py tests/test_export_dashboard.py
git commit -m "feat: wire HTML dashboard into export_report — --formats html + --no-live flag"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Architecture: export_dashboard.py + export_report.py integration (Tasks 1–5)
- ✅ `fetch_kospi_index()` in naver_finance.py (Task 1)
- ✅ `load_watchlist()` — confirmed_watchlist_{D}.json (Task 2)
- ✅ `load_kospi_forecast()` — regex on weekly-report.md (Task 2)
- ✅ Live stock prices via naver_finance (Task 3)
- ✅ `--no-live` flag (Task 5)
- ✅ `--formats html` CLI (Task 5)
- ✅ Output path: `output/투자분析제안/{DATE}_주간투자분析_대시보드.html` (Task 5)
- ✅ Error handling: FileNotFoundError → skip with warning (Task 5), live failure → `—` (Task 3)
- ✅ Dark mode + gold palette + Chart.js (Task 4)
- ✅ Cat A / Cat B / P6미통과 tabs (Task 4)
- ✅ KOSPI forecast Low/Base/High (Task 4)
- ✅ Agent weights donut (Task 4)
- ✅ Sector directions grid (Task 4)
- ✅ Target price shows `—` (spec: v1 deferred) (Task 3)

**Type consistency:**
- `DashboardData` defined in Task 2, used in Task 3 (`assemble_dashboard_data` return), Task 4 (`render_html` param), Task 5 (`generate` internally)
- `WatchlistData` defined in Task 2, returned by `load_watchlist()`
- `KospiForecast` defined in Task 2, returned by `load_kospi_forecast()`, nested in `DashboardData`
- `StockCard` defined in Task 2, used in `_make_stock_card()` Task 3 and `_stock_cards_html()` Task 4
- `fetch_stocks` / `fetch_kospi_index` imported from `naver_finance` in Task 3 — both defined (Task 1 adds `fetch_kospi_index`)
- `generate()` signature in Task 5 test matches implementation: `(date, out_dir, temp_dir, reports_dir, live)` ✅
