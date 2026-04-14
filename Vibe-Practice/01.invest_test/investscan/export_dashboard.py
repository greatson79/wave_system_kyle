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

from investscan.naver_finance import fetch_stocks, fetch_kospi_index

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
    date:                   str
    cat_a:                  list[str]
    cat_b:                  list[str]
    p6_not_passed:          list[str]
    agent_weights:          dict[str, float]
    base_sector_directions: dict[str, str]


class StockCard(TypedDict):
    ticker:     str
    name:       str
    current:    str   # "82,300" or "N/A"
    change_pct: str   # "+1.20%" or "N/A"
    direction:  str   # "up" | "down" | "flat" | "unknown"
    sector:     str
    confidence: str   # "0.74" or "N/A"
    target:     str   # always "N/A" in v1


class DashboardData(TypedDict):
    date:              str
    pipeline_version:  str
    kospi_current:     str
    kospi_change_pct:  str
    kospi_direction:   str
    kospi_forecast:    KospiForecast
    cat_a:             list[StockCard]
    cat_b:             list[StockCard]
    p6_not_passed:     list[StockCard]
    agent_weights:     dict[str, float]
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

    Returns KospiForecast with "N/A" values if parsing fails or file missing.
    """
    path = reports_dir / f"weekly-report-{date}.md"
    empty = KospiForecast(low="N/A", base="N/A", high="N/A")
    if not path.exists():
        return empty

    text = path.read_text(encoding="utf-8")

    # Match the corrected-value column (last bold cell) in the 2.3 forecast table.
    # Pattern: **Low** ... **<value>** (last bold on that row)
    low_m  = re.search(r"\*\*Low\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    base_m = re.search(r"\*\*Base\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    high_m = re.search(r"\*\*High\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)

    def _extract(m: re.Match | None) -> str:
        if not m:
            return "N/A"
        raw = m.group(1).strip()
        # Strip parenthetical suffix like " (-5.2% from 5,800)"
        raw = re.sub(r"\s*\(.*?\)", "", raw).strip()
        return raw if raw else "N/A"

    return KospiForecast(
        low=_extract(low_m),
        base=_extract(base_m),
        high=_extract(high_m),
    )


# ── stock card builder ─────────────────────────────────────────────────────────

def _make_stock_card(
    ticker: str,
    live_data: dict,
    sector: str = "N/A",
    confidence: str = "N/A",
) -> StockCard:
    """Build a StockCard from live price data dict (may be empty on failure)."""
    info = live_data.get(ticker, {})
    return StockCard(
        ticker=ticker,
        name=info.get("name", ticker),
        current=info.get("current_price", "N/A"),
        change_pct=info.get("change_pct", "N/A"),
        direction=info.get("direction", "unknown"),
        sector=sector,
        confidence=confidence,
        target="N/A",
    )


# ── data assembler ─────────────────────────────────────────────────────────────

def assemble_dashboard_data(
    date: str,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
    live: bool = True,
) -> DashboardData:
    """Load all data sources and assemble DashboardData.

    live=False skips all network calls (for testing / --no-live mode).
    """
    wl       = load_watchlist(date, temp_dir=temp_dir)
    forecast = load_kospi_forecast(date, reports_dir=reports_dir)

    live_tickers = wl["cat_a"] + wl["cat_b"]
    live_data: dict = {}
    kospi_index = None

    if live and live_tickers:
        try:
            live_data = fetch_stocks(live_tickers)
        except Exception as e:
            print(f"  ⚠  주가 조회 실패: {e}")
        try:
            kospi_index = fetch_kospi_index()
        except Exception as e:
            print(f"  ⚠  KOSPI 지수 조회 실패: {e}")

    cat_a_cards    = [_make_stock_card(t, live_data) for t in wl["cat_a"]]
    cat_b_cards    = [_make_stock_card(t, live_data) for t in wl["cat_b"]]
    p6_cards       = [_make_stock_card(t, {})        for t in wl["p6_not_passed"]]

    return DashboardData(
        date=date,
        pipeline_version="v4.0.0",
        kospi_current=kospi_index["current"]    if kospi_index else "N/A",
        kospi_change_pct=kospi_index["change_pct"] if kospi_index else "N/A",
        kospi_direction=kospi_index["direction"] if kospi_index else "unknown",
        kospi_forecast=forecast,
        cat_a=cat_a_cards,
        cat_b=cat_b_cards,
        p6_not_passed=p6_cards,
        agent_weights=wl["agent_weights"],
        sector_directions=wl["base_sector_directions"],
    )
