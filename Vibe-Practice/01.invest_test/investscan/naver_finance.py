"""
naver_finance.py — Real-time stock data scraper from Naver Finance.

Fetches current price, OHLCV, PER, market cap, foreign ownership,
institutional flow, and sector peer comparison from finance.naver.com.

No API key required. Uses requests + BeautifulSoup HTML parsing.

Usage:
    python3 -m investscan.naver_finance                    # default watchlist
    python3 -m investscan.naver_finance --ticker 005930 000660
    python3 -m investscan.naver_finance --ticker 005930 --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from typing import TypedDict

import requests
from bs4 import BeautifulSoup

# ── constants ──────────────────────────────────────────────────────────────────

_BASE_URL   = "https://finance.naver.com/item/main.naver"
_SISE_URL   = "https://finance.naver.com/item/sise.naver"
_FOREIGN_URL = "https://finance.naver.com/item/frgn.naver"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Referer": "https://finance.naver.com/",
}

DATA_DIR = Path("output/stock_data")

# Default watchlist
DEFAULT_TICKERS: dict[str, str] = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "042700": "한미반도체",
    "035420": "NAVER",
    "034020": "두산에너빌리티",
}


# ── type definitions ───────────────────────────────────────────────────────────

class StockInfo(TypedDict):
    ticker: str
    name: str
    current_price: str        # "179,700"
    change: str               # "+1,200" or "-400"
    change_pct: str           # "+0.67%" or "-0.22%"
    direction: str            # "up" | "down" | "flat"
    prev_close: str
    open_price: str
    high: str
    low: str
    volume: str               # "29,113,466"
    market_cap: str           # "1,063.8조"
    per: str                  # "27.38배"
    eps: str                  # "6,564원"
    foreign_ratio: str        # "48.90%"
    op_income_growth: str     # "65.00%" operating income growth rate
    roe: str                  # "10.85%"
    pbr: str                  # "2.81배"
    revenue_100m: str         # "938,374" 억원
    fetched_at: str           # ISO datetime


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


# ── HTML parsing helpers ───────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Remove extra whitespace and non-breaking spaces."""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def _fetch(url: str, params: dict) -> BeautifulSoup | None:
    """Fetch a URL and return BeautifulSoup, or None on failure."""
    try:
        r = requests.get(url, params=params, headers=_HEADERS, timeout=12)
        r.raise_for_status()
        # Pass raw bytes — lxml detects charset from <meta> tag (UTF-8 on Naver)
        return BeautifulSoup(r.content, "lxml")
    except Exception as e:
        print(f"  ⚠  네이버 증권 접속 실패 ({url}?code={params.get('code','')}): {e}")
        return None


def _parse_price_block(soup: BeautifulSoup) -> dict:
    """Parse current price, change, direction from rate_info block."""
    data: dict = {}

    # Current price — first .blind inside today block
    today = soup.select_one(".today")
    if today:
        blinds = today.select(".blind")
        if blinds:
            data["current_price"] = _clean(blinds[0].get_text())

    # Direction: em.no_up or em.no_down
    em = soup.select_one(".today em")
    if em:
        cls = em.get("class", [])
        if "no_up" in cls:
            data["direction"] = "up"
        elif "no_down" in cls:
            data["direction"] = "down"
        else:
            data["direction"] = "flat"
        blind_texts = [_clean(b.get_text()) for b in em.select(".blind")]
        if len(blind_texts) >= 1:
            data["current_price"] = blind_texts[0]

    # Change amount and percent from .change block
    rate_info = soup.select_one("div.rate_info")
    if rate_info:
        txt = _clean(rate_info.get_text())
        # Extract change amount: 숫자 + 숫자,숫자 pattern after 전일대비
        m = re.search(r"전일대비\s*(하락|상승|보합)?([\d,]+)", txt)
        if m:
            data["change"] = m.group(2)

    # Precise data via today's .blind spans (price, change, pct)
    today_blinds = []
    if today:
        today_blinds = [_clean(b.get_text()) for b in today.select(".blind")]

    if len(today_blinds) >= 3:
        data["current_price"] = today_blinds[0]
        raw_change = today_blinds[1]
        raw_pct    = today_blinds[2]
        sign = "+" if data.get("direction") == "up" else ("-" if data.get("direction") == "down" else "")
        data["change"]     = f"{sign}{raw_change}"
        data["change_pct"] = f"{sign}{raw_pct}%"

    return data


_SP_FIELD_MAP: dict[str, str] = {
    "sp_txt2":  "prev_close",   # 전일 종가
    "sp_txt3":  "open_price",   # 시가
    "sp_txt4":  "high",         # 고가
    "sp_txt5":  "low",          # 저가
    "sp_txt9":  "volume",       # 거래량
}


def _parse_ohlcv_table(soup: BeautifulSoup) -> dict:
    """Parse OHLCV table using CSS sprite class names (labels are images on Naver)."""
    data: dict = {}
    table = soup.select_one("table.no_info")
    if not table:
        return data

    for td in table.select("td"):
        span = td.select_one("span.sptxt")
        if not span:
            continue
        for css_cls in span.get("class", []):
            field = _SP_FIELD_MAP.get(css_cls)
            if field:
                blind = td.select_one("em .blind") or td.select_one(".blind")
                if blind:
                    data[field] = _clean(blind.get_text())
                break

    return data


def _parse_market_summary(soup: BeautifulSoup) -> dict:
    """Parse market cap, PER, EPS, foreign ratio."""
    data: dict = {}

    # PER and EPS — direct IDs
    per_el = soup.select_one("#_per")
    eps_el = soup.select_one("#_eps")
    if per_el:
        data["per"] = _clean(per_el.get_text()) + "배"
    if eps_el:
        data["eps"] = _clean(eps_el.get_text()) + "원"

    # Market cap + financial ratios from sector comparison table
    compare = soup.select_one("div.section.trade_compare")
    if compare:
        for row in compare.select("tr"):
            th = row.select_one("th")
            tds = row.select("td")
            if not th or not tds:
                continue
            label = _clean(th.get_text())
            val0  = _clean(tds[0].get_text())
            if "시가총액" in label:
                num_str = val0.replace(",", "")
                if num_str.isdigit():
                    jo = int(num_str) / 10_000
                    data["market_cap"] = f"{jo:,.1f}조"
                else:
                    data["market_cap"] = val0
            elif "외국인비율" in label:
                data["foreign_ratio"] = val0 + "%"
            elif "영업이익증가율" in label:
                data["op_income_growth"] = val0 + "%"
            elif "ROE" in label:
                data["roe"] = val0 + "%"
            elif "PBR" in label:
                data["pbr"] = val0 + "배"
            elif "매출액" in label and "억" in label:
                data["revenue_100m"] = val0

    return data


def _parse_stock_name(soup: BeautifulSoup, ticker: str) -> str:
    """Extract stock name from company header."""
    a = soup.select_one("div.wrap_company h2 a")
    if a:
        return _clean(a.get_text())
    return DEFAULT_TICKERS.get(ticker, ticker)


# ── public API ─────────────────────────────────────────────────────────────────

def fetch_stock(ticker: str, delay: float = 0.5) -> StockInfo | None:
    """
    Fetch real-time stock data for a single ticker from Naver Finance.
    Returns StockInfo dict or None on failure.
    """
    soup = _fetch(_BASE_URL, {"code": ticker})
    if soup is None:
        return None

    time.sleep(delay)  # polite crawling

    now = datetime.now().isoformat(timespec="seconds")
    name = _parse_stock_name(soup, ticker)

    price_data   = _parse_price_block(soup)
    ohlcv_data   = _parse_ohlcv_table(soup)
    summary_data = _parse_market_summary(soup)

    return StockInfo(
        ticker=ticker,
        name=name,
        current_price=price_data.get("current_price", "N/A"),
        change=price_data.get("change", "N/A"),
        change_pct=price_data.get("change_pct", "N/A"),
        direction=price_data.get("direction", "flat"),
        prev_close=ohlcv_data.get("prev_close", "N/A"),
        open_price=ohlcv_data.get("open_price", "N/A"),
        high=ohlcv_data.get("high", "N/A"),
        low=ohlcv_data.get("low", "N/A"),
        volume=ohlcv_data.get("volume", "N/A"),
        market_cap=summary_data.get("market_cap", "N/A"),
        per=summary_data.get("per", "N/A"),
        eps=summary_data.get("eps", "N/A"),
        foreign_ratio=summary_data.get("foreign_ratio", "N/A"),
        op_income_growth=summary_data.get("op_income_growth", "N/A"),
        roe=summary_data.get("roe", "N/A"),
        pbr=summary_data.get("pbr", "N/A"),
        revenue_100m=summary_data.get("revenue_100m", "N/A"),
        fetched_at=now,
    )


def fetch_stocks(
    tickers: dict[str, str] | None = None,
    delay: float = 0.8,
) -> dict[str, StockInfo]:
    """Fetch data for multiple tickers. Returns {ticker: StockInfo}."""
    watchlist = tickers or DEFAULT_TICKERS
    results: dict[str, StockInfo] = {}
    for ticker, name in watchlist.items():
        print(f"  [{ticker}] {name} 조회 중...", end=" ", flush=True)
        info = fetch_stock(ticker, delay)
        if info:
            results[ticker] = info
            dir_icon = "▲" if info["direction"] == "up" else ("▼" if info["direction"] == "down" else "─")
            print(f"{info['current_price']}원 {dir_icon}{info['change_pct']}")
        else:
            print("실패")
    return results


def save_stock_data(
    data: dict[str, StockInfo],
    report_date: str | None = None,
    out_dir: Path = DATA_DIR,
) -> Path:
    """Save fetched stock data as JSON. Returns output path."""
    rd = report_date or date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{rd}_stock_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


def format_stock_table(data: dict[str, StockInfo]) -> str:
    """Format stock data as a markdown table for report injection."""
    if not data:
        return ""
    lines = [
        "## 실시간 주요 종목 현황 (출처: 네이버 증권)",
        "",
        "| 종목 | 현재가 | 전일대비 | 거래량 | 시가총액 | PER |",
        "|------|--------|---------|--------|---------|-----|",
    ]
    for ticker, info in data.items():
        dir_icon = "▲" if info["direction"] == "up" else ("▼" if info["direction"] == "down" else "─")
        lines.append(
            f"| {info['name']} ({ticker}) "
            f"| {info['current_price']}원 "
            f"| {dir_icon} {info['change']} ({info['change_pct']}) "
            f"| {info['volume']} "
            f"| {info['market_cap']} "
            f"| {info['per']} |"
        )
    lines.append("")
    lines.append(f"> 조회 시각: {list(data.values())[0]['fetched_at'][:16] if data else 'N/A'}")
    lines.append("")
    return "\n".join(lines)


def format_stock_detail(info: StockInfo) -> str:
    """Format a single stock's detail as a markdown section."""
    dir_icon = "▲" if info["direction"] == "up" else ("▼" if info["direction"] == "down" else "─")
    return f"""### {info['name']} ({info['ticker']}) — 실시간 시세

| 항목 | 수치 |
|------|------|
| 현재가 | **{info['current_price']}원** |
| 전일 대비 | {dir_icon} {info['change']} ({info['change_pct']}) |
| 전일 종가 | {info['prev_close']}원 |
| 시초가 / 고가 / 저가 | {info['open_price']} / {info['high']} / {info['low']}원 |
| 거래량 | {info['volume']} |
| 시가총액 | {info['market_cap']} |
| PER / PBR | {info['per']} / {info['pbr']} |
| EPS | {info['eps']} |
| 외국인비율 | {info['foreign_ratio']} |
| 영업이익증가율 | {info['op_income_growth']} |
| ROE | {info['roe']} |
| 매출액 | {info['revenue_100m']}억원 |

"""


# ── mock data for dry-run ──────────────────────────────────────────────────────

def _mock_data() -> dict[str, StockInfo]:
    now = datetime.now().isoformat(timespec="seconds")
    return {
        "005930": StockInfo(
            ticker="005930", name="삼성전자",
            current_price="179,700", change="-400", change_pct="-0.22%",
            direction="down", prev_close="180,100",
            open_price="172,100", high="181,700", low="172,000",
            volume="29,113,466", market_cap="1,063.8조",
            per="27.38배", eps="6,564원", foreign_ratio="48.90%",
            op_income_growth="65.00%", roe="10.85%", pbr="2.81배",
            revenue_100m="938,374", fetched_at=now,
        ),
        "000660": StockInfo(
            ticker="000660", name="SK하이닉스",
            current_price="922,000", change="-11,000", change_pct="-1.18%",
            direction="down", prev_close="933,000",
            open_price="890,000", high="934,000", low="880,000",
            volume="4,520,842", market_cap="657.1조",
            per="15.64배", eps="58,955원", foreign_ratio="53.21%",
            op_income_growth="68.40%", roe="44.15%", pbr="5.28배",
            revenue_100m="328,267", fetched_at=now,
        ),
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="네이버 증권 실시간 데이터 수집")
    parser.add_argument("--ticker",  nargs="*", help="종목 코드 (기본: 워치리스트)")
    parser.add_argument("--dry-run", action="store_true", help="mock 데이터 사용")
    parser.add_argument("--save",    action="store_true", help="JSON 저장")
    parser.add_argument("--date",    help="저장 날짜 YYYY-MM-DD (기본: 오늘)")
    args = parser.parse_args()

    mode = "dry-run (오프라인)" if args.dry_run else "네이버 증권 실시간"
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
네이버 증권 데이터 수집 — {mode}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    if args.dry_run:
        tickers_param = None if not args.ticker else {t: DEFAULT_TICKERS.get(t, t) for t in args.ticker}
        data = _mock_data()
        if tickers_param:
            data = {k: v for k, v in data.items() if k in tickers_param}
    else:
        tickers_param = None
        if args.ticker:
            tickers_param = {t: DEFAULT_TICKERS.get(t, t) for t in args.ticker}
        data = fetch_stocks(tickers_param)

    print()
    print(format_stock_table(data))

    for ticker, info in data.items():
        print(format_stock_detail(info))

    if args.save and data:
        out_path = save_stock_data(data, report_date=args.date)
        print(f"  저장: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
