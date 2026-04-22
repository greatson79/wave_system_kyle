# Branch 1.1 & 1.2: External Financial Data Source Integration Analysis

> **TWO Data Source Integration Experts**
> **Date**: 2026-03-28
> **Context**: InvestScan Scenario B (BALANCED) -- LOCAL AI investment macro intelligence on MacBook M5 Max 64GB
> **Critical Constraint**: 100% LOCAL execution. No paid API subscriptions. Free/open data sources only.
> **Existing Assets**: EnvironmentScan (116+ sources, STEEPs) + GlobalNews-Crawling (8-stage NLP, 56 techniques)
> **Gap**: No actual market price data, no sector performance data, no macro economic indicators

---

## THE FUNDAMENTAL QUESTION

InvestScan currently processes 500+ macro signals per week from EnvironmentScan and GlobalNews-Crawling. These signals tell us WHAT is happening in the world (new regulations, tech breakthroughs, geopolitical shifts). But they do NOT tell us:

1. **How the market is already pricing these signals** -- Has the AI boom already inflated semiconductor stocks by 40%?
2. **Which Korean sectors are moving** -- Is the KOSPI Chemical sector up or down this week?
3. **What macro conditions frame the environment** -- Is the Korean won weakening? Is the Fed cutting rates?

Without this data, InvestScan's investment direction calls are untethered from market reality. Branch 1.1 (Comprehensive) argues we need all of it. Branch 1.2 (Minimal) argues we need just enough to be credible.

---

## BRANCH 1.1: COMPREHENSIVE Data Integration (Aggressive)

### A. Korean Market Data

---

#### A1. FinanceDataReader (Primary Recommendation)

| Property | Value |
|----------|-------|
| **Library** | `finance-datareader` |
| **Source** | [github.com/FinanceData/FinanceDataReader](https://github.com/FinanceData/FinanceDataReader) |
| **PyPI** | [pypi.org/project/finance-datareader](https://pypi.org/project/finance-datareader/) |
| **License** | MIT |
| **Stars** | 1,400+ |
| **Install** | `pip install finance-datareader` |
| **Python** | 3.7+ |
| **Dependencies** | pandas, requests |
| **Last Active** | March 2024 (201 commits) |
| **Rate Limits** | Not documented; relies on KRX/Naver/Yahoo backends |
| **Reliability** | HIGH -- 8+ years of community use, battle-tested |

**What it provides**:
- KOSPI index (KS11), KOSDAQ index (KQ11) -- daily OHLCV
- Individual stock prices: all KRX-listed stocks (2,663+) with OHLCV
- KRX stock listings with Sector and Industry columns
- Exchange rates: USD/KRW, EUR/KRW, CNY/KRW, JPY/KRW
- US Treasury yields: 5Y, 10Y, 30Y
- Commodities: Oil (WTI, Brent), Gold, Silver, Copper
- Cryptocurrency: BTC/USD, ETH/KRW
- ETF listings: Korean ETFs
- US indices: DJI, S&P500 (US500), NASDAQ (IXIC)
- Financial statements via Naver (SnapDataReader)

**Concrete Python code for InvestScan**:

```python
"""
investscan/data/korean_market.py
Fetch Korean market data using FinanceDataReader
"""
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta


def fetch_kospi_kosdaq_indices(start_date: str, end_date: str = None) -> dict[str, pd.DataFrame]:
    """Fetch KOSPI and KOSDAQ daily index data.

    Args:
        start_date: "YYYY-MM-DD" format
        end_date: "YYYY-MM-DD" format (default: today)

    Returns:
        Dict with 'kospi' and 'kosdaq' DataFrames (columns: Open, High, Low, Close, Volume)
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "kospi": fdr.DataReader("KS11", start_date, end_date),   # KOSPI Index
        "kosdaq": fdr.DataReader("KQ11", start_date, end_date),   # KOSDAQ Index
    }


def fetch_exchange_rates(start_date: str, end_date: str = None) -> dict[str, pd.DataFrame]:
    """Fetch key exchange rates relevant to Korean market analysis."""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "usd_krw": fdr.DataReader("USD/KRW", start_date, end_date),
        "eur_krw": fdr.DataReader("EUR/KRW", start_date, end_date),
        "jpy_krw": fdr.DataReader("JPY/KRW", start_date, end_date),
        "cny_krw": fdr.DataReader("CNY/KRW", start_date, end_date),
    }


def fetch_global_indices(start_date: str, end_date: str = None) -> dict[str, pd.DataFrame]:
    """Fetch major global indices for cross-market context."""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "sp500": fdr.DataReader("US500", start_date, end_date),    # S&P 500
        "nasdaq": fdr.DataReader("IXIC", start_date, end_date),    # NASDAQ Composite
        "dow": fdr.DataReader("DJI", start_date, end_date),        # Dow Jones
        "nikkei": fdr.DataReader("N225", start_date, end_date),    # Nikkei 225
    }


def fetch_commodities(start_date: str, end_date: str = None) -> dict[str, pd.DataFrame]:
    """Fetch commodity prices for macro analysis."""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "wti_oil": fdr.DataReader("CL=F", start_date, end_date),  # WTI Crude Oil
        "gold": fdr.DataReader("GC=F", start_date, end_date),     # Gold Futures
        "copper": fdr.DataReader("HG=F", start_date, end_date),   # Copper Futures
    }


def fetch_us_treasury_yields(start_date: str, end_date: str = None) -> dict[str, pd.DataFrame]:
    """Fetch US Treasury yields -- key for global rate environment."""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "us_5y": fdr.DataReader("US5YT=X", start_date, end_date),
        "us_10y": fdr.DataReader("US10YT=X", start_date, end_date),
        "us_30y": fdr.DataReader("US30YT=X", start_date, end_date),
    }


def fetch_krx_stock_listing() -> pd.DataFrame:
    """Get full KRX stock listing with Sector and Industry columns.

    Returns:
        DataFrame with columns: Symbol, Market, Name, Sector, Industry, ListingDate, ...
        This is the key mapping for STEEPs -> Korean sector direction.
    """
    return fdr.StockListing("KRX")  # ~2,663 stocks with Sector/Industry


def fetch_korean_etfs() -> pd.DataFrame:
    """Get Korean ETF listing for sector ETF mapping."""
    return fdr.StockListing("ETF/KR")
```

**LOC estimate**: ~90 LOC (data fetching module)

**Data format**: All returns are pandas DataFrames with DatetimeIndex. OHLCV columns: Open, High, Low, Close, Volume (or Adj Close for some sources).

**Update frequency**: Daily (end-of-day data). Data available after market close ~15:30 KST.

**Key limitation**: FinanceDataReader does NOT provide KRX sector-level indices directly (e.g., KOSPI Chemical Index, KOSPI Electronics Index). It provides the KOSPI composite and individual stock prices. For sector indices, we need pykrx.

---

#### A2. pykrx (Sector Index Specialist)

| Property | Value |
|----------|-------|
| **Library** | `pykrx` |
| **Source** | [github.com/sharebook-kr/pykrx](https://github.com/sharebook-kr/pykrx) |
| **PyPI** | [pypi.org/project/pykrx](https://pypi.org/project/pykrx/) |
| **License** | MIT |
| **Install** | `pip install pykrx` |
| **Python** | 3.10+ (tested on 3.10-3.14) |
| **Dependencies** | pandas, requests |
| **Mechanism** | Web scraping from KRX/Naver Finance |
| **Rate Limits** | Undocumented; library warns "refrain from indiscriminate API calls" |
| **Reliability** | MEDIUM-HIGH -- active maintenance, but scraping can break if KRX changes HTML |
| **Last Active** | January 2026 (recent issues/commits) |

**Critical advantage over FinanceDataReader**: pykrx provides **sector/industry index data** via `get_index_ohlcv()` and `get_index_ticker_list()`. This is what InvestScan needs to map STEEPs signals to actual Korean sector performance.

**KOSPI Sector Index Codes** (via `stock.get_index_ticker_list("KOSPI")`):

| Code | Sector Name (Korean) | Sector Name (English) |
|------|----------------------|----------------------|
| 1001 | 코스피 | KOSPI Composite |
| 1002 | 코스피 대형주 | KOSPI Large Cap |
| 1003 | 코스피 중형주 | KOSPI Mid Cap |
| 1004 | 코스피 소형주 | KOSPI Small Cap |
| 1005 | 음식료품 | Food & Beverage |
| 1006 | 섬유의복 | Textiles & Apparel |
| 1007 | 종이목재 | Paper & Wood |
| 1008 | 화학 | Chemicals |
| 1009 | 의약품 | Pharmaceuticals |
| 1010 | 비금속광물 | Non-Metallic Minerals |
| 1011 | 철강금속 | Iron & Steel |
| 1012 | 기계 | Machinery |
| 1013 | 전기전자 | Electronics |
| 1014 | 의료정밀 | Medical Instruments |
| 1015 | 운수장비 | Transport Equipment |
| 1016 | 유통업 | Retail/Distribution |
| 1017 | 전기가스업 | Electric & Gas |
| 1018 | 건설업 | Construction |
| 1019 | 운수창고업 | Transportation & Storage |
| 1020 | 통신업 | Telecommunications |
| 1021 | 금융업 | Finance |
| 1022 | 은행 | Banking |
| 1024 | 증권 | Securities |
| 1025 | 보험 | Insurance |
| 1026 | 서비스업 | Services |
| 1027 | 제조업 | Manufacturing |
| 1028 | 코스피200 | KOSPI 200 |

**Concrete Python code for InvestScan**:

```python
"""
investscan/data/korean_sectors.py
Fetch Korean sector index data using pykrx
"""
from pykrx import stock as pkstock
import pandas as pd
from datetime import datetime
import time


# KOSPI Sector Index Codes -- InvestScan's primary mapping target
KOSPI_SECTOR_INDICES = {
    "1005": "Food & Beverage",
    "1006": "Textiles & Apparel",
    "1007": "Paper & Wood",
    "1008": "Chemicals",
    "1009": "Pharmaceuticals",
    "1010": "Non-Metallic Minerals",
    "1011": "Iron & Steel",
    "1012": "Machinery",
    "1013": "Electronics",
    "1014": "Medical Instruments",
    "1015": "Transport Equipment",
    "1016": "Retail/Distribution",
    "1017": "Electric & Gas",
    "1018": "Construction",
    "1019": "Transportation & Storage",
    "1020": "Telecommunications",
    "1021": "Finance",
    "1022": "Banking",
    "1024": "Securities",
    "1025": "Insurance",
    "1026": "Services",
    "1027": "Manufacturing",
}


def fetch_all_sector_indices(
    start_date: str, end_date: str, freq: str = "d"
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV for all KOSPI sector indices.

    Args:
        start_date: "YYYYMMDD" format (pykrx convention)
        end_date: "YYYYMMDD" format
        freq: "d" (daily), "m" (monthly), "y" (yearly)

    Returns:
        Dict mapping sector code -> DataFrame with Open, High, Low, Close, Volume
    """
    results = {}
    for code, name in KOSPI_SECTOR_INDICES.items():
        try:
            df = pkstock.get_index_ohlcv(start_date, end_date, code, freq)
            df.attrs["sector_name"] = name
            df.attrs["sector_code"] = code
            results[code] = df
            time.sleep(0.3)  # Rate limit courtesy: 0.3s between requests
        except Exception as e:
            print(f"[WARN] Failed to fetch sector {code} ({name}): {e}")
            continue
    return results


def fetch_sector_performance_summary(
    start_date: str, end_date: str
) -> pd.DataFrame:
    """Compute sector performance summary for the period.

    Returns:
        DataFrame with columns: sector_code, sector_name, start_close,
        end_close, return_pct, avg_volume
    """
    sector_data = fetch_all_sector_indices(start_date, end_date)
    rows = []
    for code, df in sector_data.items():
        if len(df) < 2:
            continue
        start_close = df["종가"].iloc[0]
        end_close = df["종가"].iloc[-1]
        return_pct = ((end_close - start_close) / start_close) * 100 if start_close > 0 else 0
        avg_volume = df["거래량"].mean()
        rows.append({
            "sector_code": code,
            "sector_name": KOSPI_SECTOR_INDICES[code],
            "start_close": start_close,
            "end_close": end_close,
            "return_pct": round(return_pct, 2),
            "avg_volume": int(avg_volume),
        })
    return pd.DataFrame(rows).sort_values("return_pct", ascending=False)


def fetch_sector_fundamentals(date: str) -> pd.DataFrame:
    """Get PER, PBR, dividend yield for the KOSPI market on a given date.

    Args:
        date: "YYYYMMDD" format

    Returns:
        DataFrame with fundamental metrics for all stocks on that date
    """
    return pkstock.get_market_fundamental(date)


def fetch_investor_trading(
    start_date: str, end_date: str, ticker: str
) -> pd.DataFrame:
    """Get trading value by investor type (institutions, foreigners, retail).

    Args:
        ticker: Stock ticker (e.g., "005930" for Samsung Electronics)

    Returns:
        DataFrame with investor-type trading breakdown
    """
    return pkstock.get_market_trading_value_by_date(start_date, end_date, ticker)


def get_index_ticker_map(market: str = "KOSPI") -> dict[str, str]:
    """Get mapping of index ticker codes to names.

    Args:
        market: "KOSPI", "KOSDAQ", or "KRX"

    Returns:
        Dict of {ticker_code: korean_name}
    """
    tickers = pkstock.get_index_ticker_list(market=market)
    return {t: pkstock.get_index_ticker_name(t) for t in tickers}
```

**LOC estimate**: ~110 LOC (sector data module)

**Performance note**: pykrx uses web scraping, so fetching all 22 sector indices takes ~8-10 seconds (with 0.3s courtesy delay between requests). For a weekly batch pipeline, this is acceptable.

---

#### A3. KRX Open API (한국거래소 공식 API)

| Property | Value |
|----------|-------|
| **URL** | [openapi.krx.co.kr](https://openapi.krx.co.kr/) |
| **Type** | Official REST API |
| **Authentication** | Registration required (회원가입) |
| **Cost** | Free tier available; premium tiers for real-time data |
| **Data** | Market data, short selling, investment analysis (SMILE) |
| **Rate Limits** | Varies by subscription tier |
| **Reliability** | HIGHEST -- official exchange data |

**Also available via data.go.kr** (공공데이터포털):
- `금융위원회_KRX상장종목정보` -- Listed stock info (free, API key from data.go.kr)
- `금융위원회_주식시세정보` -- Stock price info (free, T+1 business day after 13:00)

**Assessment**: The official KRX API is the most reliable source but requires registration and has slower data availability (T+1). For InvestScan's **weekly** batch pipeline, T+1 is perfectly acceptable. However, FinanceDataReader and pykrx already wrap this data with much simpler Python interfaces.

**Recommendation**: Do NOT use KRX Open API directly. Use FinanceDataReader + pykrx which provide cleaner Python interfaces to the same underlying data. Only fallback to KRX direct API if the libraries break.

---

#### A4. Naver Finance Crawling

| Property | Value |
|----------|-------|
| **URL** | `finance.naver.com` |
| **Method** | HTTP requests to `siseJson.naver` endpoint |
| **Authentication** | None |
| **Legal Status** | Grey area -- publicly accessible data, but scraping may violate ToS |
| **Rate Limits** | Aggressive blocking if too many requests |
| **Reliability** | LOW-MEDIUM -- endpoints change without notice |

**Assessment**: FinanceDataReader already uses Naver Finance as one of its backends. Using Naver directly adds maintenance burden (HTML/JSON endpoint changes) with no data advantage. **Not recommended as a direct source.** Let FinanceDataReader handle the Naver backend abstraction.

---

#### A5. FinanceDataReader vs pykrx: HEAD-TO-HEAD COMPARISON

| Feature | FinanceDataReader | pykrx |
|---------|-------------------|-------|
| **KOSPI/KOSDAQ composite index** | YES (KS11, KQ11) | YES |
| **Individual stock OHLCV** | YES | YES |
| **KRX sector indices (업종별)** | NO | **YES** (critical differentiator) |
| **Investor trading by type** | NO | **YES** (foreign/institutional/retail) |
| **Market fundamentals (PER/PBR)** | YES (via Naver) | **YES** (native) |
| **Exchange rates** | **YES** (multiple pairs) | NO |
| **US/Global indices** | **YES** (DJI, S&P500, N225) | NO |
| **Commodities** | **YES** (Oil, Gold, Copper) | NO |
| **US Treasury yields** | **YES** | NO |
| **ETF listings** | **YES** | NO |
| **Financial statements** | YES (via Naver) | NO |
| **Bond data** | NO | **YES** |
| **API style** | Unified `DataReader()` | Function-based `stock.*()` |
| **Data backend** | Multiple (KRX, Naver, Yahoo, FRED) | KRX + Naver scraping |
| **Date format** | "YYYY-MM-DD" | "YYYYMMDD" |
| **Speed** | Fast | Slower (scraping) |

**Verdict**: InvestScan needs BOTH libraries. They are complementary, not competing:
- **FinanceDataReader** = broad market context (indices, FX, commodities, global)
- **pykrx** = deep Korean sector data (sector indices, investor flows, fundamentals)

---

### B. Macro Economic Data

---

#### B1. FRED (Federal Reserve Economic Data)

| Property | Value |
|----------|-------|
| **Library** | `fredapi` |
| **Source** | [github.com/mortada/fredapi](https://github.com/mortada/fredapi) |
| **PyPI** | [pypi.org/project/fredapi](https://pypi.org/project/fredapi/) |
| **Install** | `pip install fredapi` |
| **API Key** | Free -- register at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| **Rate Limit** | **120 requests/minute** (generous) |
| **Database Size** | 816,000+ time series |
| **Data Format** | pandas Series with DatetimeIndex |
| **Reliability** | HIGHEST -- maintained by Federal Reserve Bank of St. Louis |
| **Update Frequency** | Series-dependent: daily, weekly, monthly, quarterly, annual |

**Key FRED Series for InvestScan**:

| Series ID | Name | Frequency | Why InvestScan Needs It |
|-----------|------|-----------|------------------------|
| **DFF** | Federal Funds Effective Rate | Daily | US monetary policy -- drives global capital flows |
| **DFEDTARU** | Fed Funds Target Rate Upper | Per FOMC meeting | Rate decision signaling |
| **DGS2** | 2-Year Treasury Yield | Daily | Short-term rate expectations |
| **DGS10** | 10-Year Treasury Yield | Daily | Long-term rate environment, yield curve |
| **T10Y2Y** | 10Y-2Y Treasury Spread | Daily | Yield curve inversion = recession signal |
| **DEXKOUS** | USD/KRW Exchange Rate | Daily | Korean won strength, capital flow proxy |
| **CPIAUCSL** | Consumer Price Index (All Items) | Monthly | US inflation -- Fed reaction function |
| **GDP** | Real GDP | Quarterly | US economic growth |
| **UNRATE** | Unemployment Rate | Monthly | Labor market health |
| **INTDSRKRM193N** | Korea Discount Rate | Monthly | Korean monetary policy proxy |
| **VIXCLS** | CBOE Volatility Index (VIX) | Daily | Market fear gauge |
| **DCOILWTICO** | WTI Crude Oil Price | Daily | Energy sector, inflation input |
| **GOLDAMGBD228NLBM** | Gold Price (London AM Fix) | Daily | Safe haven demand |
| **M2SL** | M2 Money Stock | Monthly | Liquidity environment |

**Concrete Python code for InvestScan**:

```python
"""
investscan/data/macro_fred.py
Fetch US & global macro data from FRED
"""
import os
from fredapi import Fred
import pandas as pd
from datetime import datetime


# Core series InvestScan tracks weekly
INVESTSCAN_FRED_SERIES = {
    # --- Interest Rates & Monetary Policy ---
    "DFF": "Fed Funds Effective Rate",
    "DFEDTARU": "Fed Funds Target Upper",
    "DGS2": "2-Year Treasury Yield",
    "DGS10": "10-Year Treasury Yield",
    "T10Y2Y": "10Y-2Y Spread (Yield Curve)",
    # --- Exchange Rates ---
    "DEXKOUS": "USD/KRW Exchange Rate",
    # --- Inflation ---
    "CPIAUCSL": "CPI All Items",
    # --- Growth & Employment ---
    "GDP": "Real GDP",
    "UNRATE": "Unemployment Rate",
    # --- Korea-specific ---
    "INTDSRKRM193N": "Korea Discount Rate",
    # --- Volatility & Risk ---
    "VIXCLS": "VIX (CBOE Volatility)",
    # --- Commodities ---
    "DCOILWTICO": "WTI Crude Oil",
    "GOLDAMGBD228NLBM": "Gold Price (London)",
    # --- Liquidity ---
    "M2SL": "M2 Money Stock",
}


def get_fred_client() -> Fred:
    """Initialize FRED client. API key from env var or config."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        config_path = os.path.expanduser("~/.investscan/fred_api_key.txt")
        if os.path.exists(config_path):
            with open(config_path) as f:
                api_key = f.read().strip()
    if not api_key:
        raise ValueError(
            "FRED API key not found. Set FRED_API_KEY env var or "
            "save key to ~/.investscan/fred_api_key.txt"
        )
    return Fred(api_key=api_key)


def fetch_all_macro_indicators(
    start_date: str = "2020-01-01",
    end_date: str = None,
) -> dict[str, pd.Series]:
    """Fetch all InvestScan-tracked FRED series.

    Args:
        start_date: "YYYY-MM-DD"
        end_date: "YYYY-MM-DD" (default: today)

    Returns:
        Dict mapping series_id -> pandas Series
    """
    fred = get_fred_client()
    results = {}

    for series_id, name in INVESTSCAN_FRED_SERIES.items():
        try:
            data = fred.get_series(series_id, start_date, end_date)
            data.name = name
            results[series_id] = data
        except Exception as e:
            print(f"[WARN] Failed to fetch FRED/{series_id} ({name}): {e}")
            continue

    return results


def fetch_macro_snapshot(lookback_days: int = 30) -> pd.DataFrame:
    """Get latest values and recent changes for all macro indicators.

    Returns:
        DataFrame with columns: series_id, name, latest_value, latest_date,
        change_1w, change_1m
    """
    fred = get_fred_client()
    start_date = (
        datetime.now() - pd.Timedelta(days=max(lookback_days * 2, 90))
    ).strftime("%Y-%m-%d")

    rows = []
    for series_id, name in INVESTSCAN_FRED_SERIES.items():
        try:
            data = fred.get_series(series_id, start_date).dropna()
            if len(data) == 0:
                continue

            latest = data.iloc[-1]
            latest_date = data.index[-1]

            # 1-week change
            week_ago_idx = data.index[data.index <= latest_date - pd.Timedelta(days=5)]
            change_1w = (
                ((latest - data.loc[week_ago_idx[-1]]) / data.loc[week_ago_idx[-1]] * 100)
                if len(week_ago_idx) > 0 and data.loc[week_ago_idx[-1]] != 0
                else None
            )

            # 1-month change
            month_ago_idx = data.index[data.index <= latest_date - pd.Timedelta(days=25)]
            change_1m = (
                ((latest - data.loc[month_ago_idx[-1]]) / data.loc[month_ago_idx[-1]] * 100)
                if len(month_ago_idx) > 0 and data.loc[month_ago_idx[-1]] != 0
                else None
            )

            rows.append({
                "series_id": series_id,
                "name": name,
                "latest_value": round(latest, 4),
                "latest_date": latest_date.strftime("%Y-%m-%d"),
                "change_1w_pct": round(change_1w, 2) if change_1w is not None else None,
                "change_1m_pct": round(change_1m, 2) if change_1m is not None else None,
            })
        except Exception as e:
            print(f"[WARN] Snapshot failed for {series_id}: {e}")
            continue

    return pd.DataFrame(rows)
```

**LOC estimate**: ~110 LOC

**Setup cost**: 5 minutes to register for free FRED API key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html). Instant approval.

---

#### B2. BOK (한국은행 경제통계시스템 ECOS)

| Property | Value |
|----------|-------|
| **Library** | `PublicDataReader` |
| **Source** | [github.com/WooilJeong/PublicDataReader](https://github.com/WooilJeong/PublicDataReader) |
| **Install** | `pip install PublicDataReader` |
| **API Key** | Free -- register at [ecos.bok.or.kr/api](https://ecos.bok.or.kr/api/). Auto-issued on signup. Active within 1 day. |
| **Rate Limits** | Not explicitly documented; "avoid excessive calls" |
| **Data Format** | pandas DataFrame |
| **Reliability** | HIGH -- official Bank of Korea data |
| **Update Frequency** | Indicator-dependent: daily, monthly, quarterly |

**Key ECOS Statistical Tables (SNAP codes) for InvestScan**:

| SNAP Code | Category | Indicators |
|-----------|----------|-----------|
| **ECOS/SNAP/523** | Short-term rates | Base rate (기준금리), call rate, KORIBOR, CD yield |
| **ECOS/SNAP/512** | Long-term rates | Monetary stabilization bonds, government bonds, corporate bonds |
| **ECOS/SNAP/529** | Exchange rates | KRW/USD, KRW/JPY |
| **ECOS/SNAP/530** | Exchange rates | KRW/EUR, KRW/CNY |
| **ECOS/SNAP/531** | Equity markets | KOSPI index, KOSDAQ index |
| **ECOS/SNAP/532** | Market activity | KOSPI trading volume, investor deposits |
| **ECOS/SNAP/527** | Money supply | M1, M2 aggregates |
| **ECOS/SNAP/528** | Liquidity | Broad financial institution liquidity |
| **ECOS/SNAP/517-1** | Credit | Household credit |
| **ECOS/SNAP/517-2** | Delinquency | Household loan delinquency ratio |
| **ECOS/SNAP/861** | Bank rates | Deposit/lending rates |
| **ECOS/SNAP/1184-1211** | Real economy | GDP, production, employment, inflation, trade |
| **ECOS/SNAP/1186** | Real estate | Housing prices |
| **ECOS/SNAP/1511** | Commodities | Crude oil, gold prices |

**Concrete Python code for InvestScan**:

```python
"""
investscan/data/macro_bok.py
Fetch Korean macro economic data from Bank of Korea ECOS
"""
import os
from PublicDataReader import Ecos
import pandas as pd


# Key BOK statistical table codes for InvestScan
BOK_TABLES = {
    "722Y001": {
        "name": "Korean Base Rate (한국은행 기준금리)",
        "period": "D",  # Daily
        "item_code": "0101000",
    },
    "731Y003": {
        "name": "Treasury Bond Yields (국고채 수익률)",
        "period": "D",
        "item_code": "010200000",  # 3-year
    },
    "036Y001": {
        "name": "USD/KRW Exchange Rate",
        "period": "D",
        "item_code": "USD",
    },
    "200Y001": {
        "name": "GDP and Major Economic Indicators",
        "period": "A",  # Annual
        "item_code": None,  # Multiple sub-items
    },
    "901Y009": {
        "name": "Consumer Price Index",
        "period": "M",  # Monthly
        "item_code": "0",
    },
}


def get_ecos_client() -> Ecos:
    """Initialize ECOS API client."""
    api_key = os.environ.get("BOK_API_KEY")
    if not api_key:
        config_path = os.path.expanduser("~/.investscan/bok_api_key.txt")
        if os.path.exists(config_path):
            with open(config_path) as f:
                api_key = f.read().strip()
    if not api_key:
        raise ValueError(
            "BOK API key not found. Set BOK_API_KEY env var or "
            "save key to ~/.investscan/bok_api_key.txt. "
            "Register free at https://ecos.bok.or.kr/api/"
        )
    return Ecos(api_key)


def fetch_key_indicators(start_year: str = "2023", end_year: str = "2026") -> pd.DataFrame:
    """Fetch Bank of Korea key economic indicators (100대 주요 지표).

    Returns:
        DataFrame with top 100 BOK indicators and their latest values.
    """
    api = get_ecos_client()
    return api.get_key_statistic_list()


def fetch_base_rate_history(start_date: str = "2020", end_date: str = "2026") -> pd.DataFrame:
    """Fetch Korean base rate (기준금리) history.

    Args:
        start_date: "YYYY" or "YYYYMM" depending on period
        end_date: "YYYY" or "YYYYMM"
    """
    api = get_ecos_client()
    return api.get_statistic_search(
        통계표코드="722Y001",
        주기="M",  # Monthly
        검색시작일자=start_date,
        검색종료일자=end_date,
    )


def fetch_consumer_price_index(start_date: str = "202001", end_date: str = "202612") -> pd.DataFrame:
    """Fetch Korean CPI data."""
    api = get_ecos_client()
    return api.get_statistic_search(
        통계표코드="901Y009",
        주기="M",
        검색시작일자=start_date,
        검색종료일자=end_date,
    )


def search_available_tables(keyword: str = "") -> pd.DataFrame:
    """Search available statistical tables by keyword."""
    api = get_ecos_client()
    return api.get_statistic_table_list()
```

**LOC estimate**: ~80 LOC

**Setup cost**: 10-15 minutes to register at ECOS portal. API key auto-issued within 1 business day.

**FRED vs BOK overlap analysis**: For InvestScan, use FRED as primary for US/global macro data, BOK as primary for Korean-specific data. Some overlap exists (USD/KRW available in both), but BOK provides Korean-specific indicators unavailable in FRED (Korean base rate, CPI by category, household credit, real estate prices).

---

#### B3. OECD Data API

| Property | Value |
|----------|-------|
| **URL** | [data.oecd.org/api](https://data.oecd.org/api/) |
| **Library** | `pandasdmx` or `oecddatabuilder` |
| **Install** | `pip install pandasdmx` |
| **API Key** | **NOT required** -- free public access |
| **Rate Limits** | Not documented; reasonable use expected |
| **Format** | JSON and XML (SDMX standard) |
| **Reliability** | HIGH -- OECD institutional data |
| **Coverage** | 38 OECD member countries including Korea |

**Key OECD Indicators for InvestScan**:
- CLI (Composite Leading Indicator) -- forward-looking economic signal
- CPI across OECD countries -- global inflation comparison
- GDP growth rates -- comparative economic health
- Unemployment rates -- labor market comparison
- Trade balance data -- import/export trends

**Concrete Python code**:

```python
"""
investscan/data/macro_oecd.py
Fetch OECD economic data (no API key required)
"""
import requests
import pandas as pd


OECD_BASE_URL = "https://sdmx.oecd.org/public/rest"


def fetch_oecd_indicator(
    dataset: str,
    country: str = "KOR",
    frequency: str = "M",
    start_period: str = "2023-01",
    end_period: str = "2026-12",
) -> pd.DataFrame:
    """Fetch OECD data via SDMX REST API.

    Args:
        dataset: OECD dataset ID (e.g., "MEI_CLI" for Leading Indicators)
        country: ISO3 country code (KOR, USA, JPN, etc.)
        frequency: M (monthly), Q (quarterly), A (annual)

    Returns:
        pandas DataFrame with time series data
    """
    url = f"{OECD_BASE_URL}/data/{dataset}/{country}.{frequency}"
    params = {
        "startPeriod": start_period,
        "endPeriod": end_period,
        "format": "jsondata",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    # Parse SDMX JSON response into DataFrame
    data = response.json()
    # SDMX parsing is complex; use pandasdmx for production
    return data


def fetch_korea_leading_indicator() -> pd.DataFrame:
    """Fetch Korea's Composite Leading Indicator (CLI).
    CLI > 100 = expansion; CLI < 100 = contraction.
    """
    return fetch_oecd_indicator("MEI_CLI", "KOR", "M")


def fetch_comparative_gdp_growth() -> pd.DataFrame:
    """Fetch GDP growth rates for Korea + major economies."""
    countries = ["KOR", "USA", "JPN", "CHN", "DEU"]
    results = {}
    for country in countries:
        results[country] = fetch_oecd_indicator("QNA", country, "Q")
    return results
```

**LOC estimate**: ~50 LOC

**Assessment for InvestScan**: OECD data is SUPPLEMENTARY. The SDMX format is complex to parse, update frequency is slow (monthly/quarterly), and most indicators are available faster from FRED or BOK. **Recommended: defer to Month 3+**. The CLI (Composite Leading Indicator) is the one unique value-add.

---

#### B4. World Bank API

| Property | Value |
|----------|-------|
| **Library** | `wbgapi` |
| **Source** | [github.com/tgherzog/wbgapi](https://github.com/tgherzog/wbgapi) |
| **Install** | `pip install wbgapi` |
| **API Key** | **NOT required** |
| **Rate Limits** | Not documented; auto-chunking for large requests |
| **Database** | 63+ databases, 17,517+ indicators |
| **Reliability** | HIGH |
| **Update Frequency** | Annual/quarterly (slow) |

**Concrete Python code**:

```python
"""
investscan/data/macro_worldbank.py
Fetch World Bank development indicators
"""
import wbgapi as wb
import pandas as pd


def fetch_korea_development_indicators() -> pd.DataFrame:
    """Fetch key World Bank indicators for Korea.

    Key indicators:
    - NY.GDP.MKTP.KD.ZG: GDP growth (annual %)
    - FP.CPI.TOTL.ZG: Inflation (annual %)
    - BN.CAB.XOKA.GD.ZS: Current account balance (% of GDP)
    - NE.EXP.GNFS.ZS: Exports of goods/services (% of GDP)
    """
    indicators = [
        "NY.GDP.MKTP.KD.ZG",   # GDP growth
        "FP.CPI.TOTL.ZG",      # Inflation
        "BN.CAB.XOKA.GD.ZS",   # Current account
        "NE.EXP.GNFS.ZS",      # Exports % GDP
    ]
    return wb.data.DataFrame(
        indicators,
        economy="KOR",
        time=range(2020, 2027),
    )
```

**LOC estimate**: ~25 LOC

**Assessment**: World Bank data is ANNUAL, making it nearly useless for weekly investment direction. Good for long-term structural context but NOT for short-term sector calls. **Recommend: defer to Month 6+ or skip entirely.**

---

### C. Sector & Industry Mapping

---

#### C1. STEEPs-to-Korean-Sector Mapping

This is the CORE intellectual challenge of InvestScan -- connecting macro signals (categorized by STEEPs: Social, Technological, Economic, Environmental, Political, Values) to actual Korean stock market sectors.

**Two classification systems coexist in Korea**:

1. **KRX Traditional Classification** (22 sectors for KOSPI, 33 for KOSDAQ)
   - Used by pykrx sector indices
   - Industry-oriented (Chemicals, Electronics, Banking, etc.)

2. **WICS (Wise Industry Classification Standard)** by FnGuide
   - 10 major sectors, 26 mid-level, 100+ sub-categories
   - Adapted from GICS (Global Industry Classification Standard)
   - Used by ETF products and institutional investors

3. **GICS** (adopted by KRX for KOSPI 200 in 2017)
   - 11 Sectors, 25 Industry Groups, 74 Industries, 163 Sub-Industries
   - International standard

**Programmatic STEEPs -> Sector mapping**:

```python
"""
investscan/mapping/steeps_sector_map.py
Map STEEPs signal categories to Korean market sectors
"""

# STEEPs -> Affected KRX Sector Codes (pykrx codes)
# Each STEEPs category affects multiple sectors with varying weights (0.0-1.0)
STEEPS_SECTOR_MATRIX = {
    "T_Technological": {
        "1013": 0.95,  # Electronics -- direct
        "1020": 0.80,  # Telecommunications
        "1026": 0.60,  # Services (IT services)
        "1012": 0.50,  # Machinery (automation)
        "1015": 0.50,  # Transport Equipment (EV, autonomous)
        "1009": 0.40,  # Pharmaceuticals (biotech)
        "1014": 0.40,  # Medical Instruments
    },
    "E_Economic": {
        "1021": 0.90,  # Finance -- direct
        "1022": 0.85,  # Banking
        "1024": 0.80,  # Securities
        "1025": 0.75,  # Insurance
        "1018": 0.65,  # Construction (rates-sensitive)
        "1016": 0.60,  # Retail/Distribution (consumer spending)
        "1005": 0.50,  # Food & Beverage (inflation)
    },
    "P_Political": {
        "1018": 0.80,  # Construction (government spending)
        "1017": 0.75,  # Electric & Gas (regulation)
        "1021": 0.70,  # Finance (regulatory)
        "1008": 0.65,  # Chemicals (trade policy)
        "1011": 0.60,  # Iron & Steel (tariffs)
        "1015": 0.55,  # Transport Equipment (trade)
    },
    "S_Social": {
        "1009": 0.85,  # Pharmaceuticals (aging, healthcare)
        "1014": 0.80,  # Medical Instruments
        "1005": 0.70,  # Food & Beverage (consumption trends)
        "1016": 0.65,  # Retail/Distribution (consumer behavior)
        "1026": 0.55,  # Services
        "1006": 0.40,  # Textiles & Apparel (fashion trends)
    },
    "E_Environmental": {
        "1017": 0.90,  # Electric & Gas (energy transition)
        "1008": 0.80,  # Chemicals (green chemistry)
        "1015": 0.75,  # Transport Equipment (EV mandate)
        "1010": 0.60,  # Non-Metallic Minerals (solar panels)
        "1018": 0.55,  # Construction (green buildings)
        "1011": 0.50,  # Iron & Steel (carbon regulations)
    },
    "s_Values": {
        "1026": 0.70,  # Services (ESG consulting)
        "1021": 0.65,  # Finance (ESG investing)
        "1016": 0.60,  # Retail/Distribution (ethical consumption)
        "1005": 0.50,  # Food & Beverage (organic, sustainability)
    },
}


def map_signal_to_sectors(
    steeps_category: str,
    signal_strength: float = 1.0,
) -> list[dict]:
    """Map a STEEPs signal to affected Korean sectors with impact weights.

    Args:
        steeps_category: "T_Technological", "E_Economic", etc.
        signal_strength: pSST score normalized to 0-1 range

    Returns:
        List of {sector_code, sector_name, impact_weight} sorted by impact
    """
    from investscan.data.korean_sectors import KOSPI_SECTOR_INDICES

    mapping = STEEPS_SECTOR_MATRIX.get(steeps_category, {})
    results = []
    for code, base_weight in mapping.items():
        results.append({
            "sector_code": code,
            "sector_name": KOSPI_SECTOR_INDICES.get(code, "Unknown"),
            "impact_weight": round(base_weight * signal_strength, 3),
        })
    return sorted(results, key=lambda x: x["impact_weight"], reverse=True)


def aggregate_sector_signals(
    signals: list[dict],
) -> dict[str, float]:
    """Aggregate multiple signal impacts into per-sector conviction scores.

    Args:
        signals: List of dicts with 'steeps_category', 'strength', 'direction'
                 where direction is +1 (bullish) or -1 (bearish)

    Returns:
        Dict of {sector_code: net_conviction_score}
    """
    sector_scores: dict[str, float] = {}

    for signal in signals:
        sector_impacts = map_signal_to_sectors(
            signal["steeps_category"],
            signal.get("strength", 0.5),
        )
        direction = signal.get("direction", 0)  # +1 bull, -1 bear, 0 neutral

        for impact in sector_impacts:
            code = impact["sector_code"]
            weighted = impact["impact_weight"] * direction
            sector_scores[code] = sector_scores.get(code, 0.0) + weighted

    return sector_scores
```

**LOC estimate**: ~80 LOC

---

### D. Alternative Data (Free)

---

#### D1. Google Trends (pytrends / pytrends-modern)

| Property | Value |
|----------|-------|
| **Library** | `pytrends-modern` (successor to archived `pytrends`) |
| **Source** | [github.com/yiromo/pytrends-modern](https://github.com/yiromo/pytrends-modern) |
| **Install** | `pip install pytrends-modern` |
| **API Key** | NOT required (Google cookies only) |
| **Rate Limits** | ~1,400 requests before throttling; 60s sleep between requests recommended |
| **Status** | Original `pytrends` archived April 2025; Google launched official Trends API (alpha) July 2025 |
| **Reliability** | LOW-MEDIUM -- unofficial scraping, frequently breaks |

**InvestScan use case**: Search interest for Korean investment-relevant terms as a retail sentiment proxy.

```python
"""
investscan/data/alt_google_trends.py
Google Trends as sentiment proxy
"""
from pytrends.request import TrendReq
import pandas as pd
import time


# Korean investment sentiment keywords
INVESTSCAN_KEYWORDS = {
    "반도체": "Semiconductors",
    "AI 투자": "AI Investment",
    "금리 인하": "Rate Cut",
    "부동산": "Real Estate",
    "코스피": "KOSPI",
}


def fetch_search_trends(
    keywords: list[str] = None,
    timeframe: str = "today 3-m",
    geo: str = "KR",
) -> pd.DataFrame:
    """Fetch Google Trends interest over time for keywords.

    Args:
        keywords: List of search terms (max 5 per request)
        timeframe: "today 3-m", "today 12-m", "2024-01-01 2024-12-31"
        geo: Country code ("KR" for Korea, "" for worldwide)

    Returns:
        DataFrame with columns for each keyword, values 0-100 (relative interest)
    """
    if keywords is None:
        keywords = list(INVESTSCAN_KEYWORDS.keys())[:5]

    pytrends = TrendReq(hl="ko", tz=540)  # Korean, KST timezone
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)

    time.sleep(2)  # Rate limit courtesy
    return pytrends.interest_over_time()
```

**LOC estimate**: ~35 LOC

**Assessment**: Google Trends is a WEAK signal source. The data is relative (0-100 scale), not absolute. It can supplement sector conviction when search interest spikes align with STEEPs signals (e.g., "반도체" search interest surging + Technology STEEPs signals = reinforced Electronics conviction). **Recommend: Month 4+ enrichment, not Day 1.**

---

#### D2. Reddit / Social Sentiment

| Property | Value |
|----------|-------|
| **Library** | `praw` (Python Reddit API Wrapper) |
| **API** | Reddit Official API |
| **Cost** | Free tier for non-commercial use |
| **Rate Limits** | 100 requests/min (OAuth), 10 req/min (unauthenticated) |
| **Status (2025-2026)** | Pre-approval now required; Pushshift shut down |
| **Korean Coverage** | MINIMAL -- Reddit is not a major platform in Korea |
| **Reliability** | LOW -- API changes frequently, Korean content sparse |

**Assessment**: Reddit is NOT a useful data source for Korean market sentiment. Korean investors use Naver Cafe, DCInside Stock Gallery, and KakaoTalk communities. Crawling these Korean platforms raises significant legal and ethical issues. **Recommend: SKIP entirely.**

---

#### D3. KIPRIS (Korean Patent Information)

| Property | Value |
|----------|-------|
| **URL** | [plus.kipris.or.kr](https://plus.kipris.or.kr/) |
| **API** | REST API |
| **Cost** | Free: 1,000 calls/month |
| **Data** | Korean patents, utility models, designs, trademarks |
| **Reliability** | HIGH -- government data |

**Assessment**: Patent data is a LEADING indicator for technology sectors. Companies filing AI/semiconductor/biotech patents signal future innovation directions. However, 1,000 calls/month is tight, and translating patent filings to investment signals requires sophisticated NLP. **Recommend: Month 6+ research project, not core pipeline.**

---

#### D4. UN Comtrade (Trade Data)

| Property | Value |
|----------|-------|
| **Library** | `comtradeapicall` |
| **Source** | [github.com/uncomtrade/comtradeapicall](https://github.com/uncomtrade/comtradeapicall) |
| **API Key** | Free registration required (approval may take days) |
| **Rate Limits** | 500 calls/day, 100,000 records/call |
| **Data** | International trade flows by country and commodity |
| **Reliability** | HIGH |
| **Update** | Monthly (2-3 month lag) |

**Assessment**: Trade data reveals structural shifts (Korea's semiconductor exports to China declining = bearish Electronics). The 2-3 month data lag makes it unsuitable for weekly tactical calls but excellent for medium-term (1-6 month) structural views. **Recommend: Month 3+ for medium-term synthesis layer.**

---

## BRANCH 1.2: MINIMAL Data Integration (Conservative)

### The Minimal Stack

Branch 1.2 argues: InvestScan's PRIMARY value is signal processing from EnvironmentScan and GlobalNews-Crawling. Market price data is supplementary context, not the core product. A minimal stack should:

1. Confirm signals are not already priced in (basic market sanity check)
2. Provide one anchoring macro datapoint (US rates / KRW direction)
3. Add zero maintenance burden

**Minimal Stack: 2 libraries, ~80 LOC total**

```python
"""
investscan/data/minimal_data.py
MINIMAL external data -- just enough to be credible
"""
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta


def fetch_minimal_market_context(lookback_days: int = 30) -> dict:
    """Fetch the absolute minimum external data for investment context.

    Returns:
        Dict with:
        - kospi_return: KOSPI % return over lookback period
        - kosdaq_return: KOSDAQ % return over lookback period
        - usd_krw_current: Latest USD/KRW rate
        - usd_krw_change: USD/KRW % change over lookback period
        - us_10y_yield: Latest 10-year Treasury yield
    """
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    result = {}

    # KOSPI return
    try:
        kospi = fdr.DataReader("KS11", start, end)
        if len(kospi) >= 2:
            result["kospi_close"] = kospi["Close"].iloc[-1]
            result["kospi_return_pct"] = round(
                (kospi["Close"].iloc[-1] / kospi["Close"].iloc[0] - 1) * 100, 2
            )
    except Exception:
        result["kospi_close"] = None
        result["kospi_return_pct"] = None

    # KOSDAQ return
    try:
        kosdaq = fdr.DataReader("KQ11", start, end)
        if len(kosdaq) >= 2:
            result["kosdaq_close"] = kosdaq["Close"].iloc[-1]
            result["kosdaq_return_pct"] = round(
                (kosdaq["Close"].iloc[-1] / kosdaq["Close"].iloc[0] - 1) * 100, 2
            )
    except Exception:
        result["kosdaq_close"] = None
        result["kosdaq_return_pct"] = None

    # USD/KRW
    try:
        fx = fdr.DataReader("USD/KRW", start, end)
        if len(fx) >= 2:
            result["usd_krw_current"] = round(fx["Close"].iloc[-1], 2)
            result["usd_krw_change_pct"] = round(
                (fx["Close"].iloc[-1] / fx["Close"].iloc[0] - 1) * 100, 2
            )
    except Exception:
        result["usd_krw_current"] = None
        result["usd_krw_change_pct"] = None

    return result


# FRED: only US 10-year yield and Fed Funds rate
# Using FinanceDataReader's built-in FRED access (no fredapi needed!)
def fetch_minimal_macro() -> dict:
    """Fetch 2 macro datapoints via FinanceDataReader (no FRED API key needed)."""
    start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    result = {}

    try:
        # US 10-Year Treasury Yield via FDR
        us10y = fdr.DataReader("US10YT=X", start)
        if len(us10y) > 0:
            result["us_10y_yield"] = round(us10y["Close"].iloc[-1], 2)
    except Exception:
        result["us_10y_yield"] = None

    return result
```

**LOC estimate**: ~65 LOC

**Dependencies**: Only `finance-datareader` (which InvestScan already needs for stock listings)

**API keys needed**: ZERO

**Maintenance burden**: NEAR-ZERO (one library, mainstream endpoints only)

---

### Is Minimal Data SUFFICIENT?

**Branch 1.2 Expert's argument FOR sufficiency**:

1. **InvestScan is NOT a trading system.** It generates weekly "investment direction" reports for a pastor who invests 2-4 hours/week. The user does not need tick-by-tick sector performance.

2. **The signals ARE the product.** EnvScan's 500+ signals + GlobalNews's 56-technique NLP pipeline already provide differentiated insight. Adding market prices does not improve signal quality -- it only contextualizes them.

3. **Sector-level price data creates false precision.** Saying "KOSPI Electronics was up 2.3% this week" implies a connection between the signal and the price movement that may not exist. Correlation is not causation.

4. **Minimal data is maximally maintainable.** One library, no API keys, zero registration. This can run for 2 years without touching it.

**Branch 1.1 Expert's counter-argument for WHY minimal is INSUFFICIENT**:

1. **Without sector performance data, investment "direction" calls are unverifiable.** If InvestScan says "bullish on Electronics due to AI signal surge," but the user has no way to check whether Electronics actually went up or down, the report lacks credibility.

2. **The FRED macro data is essential framing.** Saying "AI regulation signals detected (P_Political)" without knowing if the Fed just raised rates by 50bps means the report misses the dominant market force. Rate hikes crush growth stocks regardless of sector-level signals.

3. **The KRW/USD direction is THE single most important variable for Korean equity returns.** Academic literature consistently shows that KRW weakness = foreign capital outflow = KOSPI decline, regardless of underlying fundamentals. InvestScan MUST track this.

4. **Sector performance is the validation loop.** Without knowing what sectors actually did, InvestScan cannot improve its signal-to-sector mapping over time. It becomes an unfalsifiable opinion generator.

---

## COMPARISON TABLE: All Data Sources

| Data Source | Library | API Key | Value for InvestScan | LOC | Maintenance | Reliability | Legal Risk | Priority |
|------------|---------|---------|---------------------|-----|-------------|-------------|------------|----------|
| **FinanceDataReader** | finance-datareader | None | **CRITICAL** -- KOSPI/KOSDAQ index, FX, global indices, stock listings with sectors | ~90 | LOW | HIGH (8yr+) | LOW (MIT) | **Day 1** |
| **pykrx** | pykrx | None | **HIGH** -- KOSPI sector indices (22 sectors), investor flows, fundamentals | ~110 | MEDIUM (scraping) | MEDIUM-HIGH | LOW (MIT) | **Day 1** |
| **FRED** | fredapi | Free (instant) | **HIGH** -- US rates, VIX, Korea discount rate, CPI, GDP, oil, gold | ~110 | LOW | HIGHEST | NONE | **Day 1** |
| **BOK ECOS** | PublicDataReader | Free (1 day) | **MEDIUM-HIGH** -- Korean base rate, CPI, M2, household credit | ~80 | LOW | HIGH | NONE | **Week 2** |
| **OECD** | pandasdmx | None | **LOW-MEDIUM** -- CLI leading indicator, cross-country comparison | ~50 | MEDIUM (SDMX parsing) | HIGH | NONE | Month 3+ |
| **World Bank** | wbgapi | None | **LOW** -- annual data only, too slow for weekly pipeline | ~25 | LOW | HIGH | NONE | Month 6+ or skip |
| **Google Trends** | pytrends-modern | None | **LOW** -- retail sentiment proxy, unreliable, breaks often | ~35 | HIGH (scraping) | LOW-MEDIUM | MEDIUM | Month 4+ |
| **Reddit** | praw | Free | **NEGLIGIBLE** -- no Korean market coverage | ~0 | N/A | LOW | MEDIUM | **SKIP** |
| **KIPRIS Patents** | requests | Free (1K/mo) | **LOW** -- leading indicator but hard to translate to sector | ~40 | LOW | HIGH | NONE | Month 6+ |
| **UN Comtrade** | comtradeapicall | Free (days) | **MEDIUM** -- trade flow structural shifts, 2-3 month lag | ~40 | LOW | HIGH | NONE | Month 3+ |

---

## RECOMMENDED IMPLEMENTATION STRATEGY

### Phase 1 (Day 1 -- Core, ~310 LOC)

| Component | Library | LOC | Setup Time |
|-----------|---------|-----|------------|
| Korean market data | FinanceDataReader | 90 | 0 min (pip install) |
| Korean sector indices | pykrx | 110 | 0 min (pip install) |
| US/Global macro | fredapi | 110 | 5 min (free API key) |
| **Total** | **3 libraries** | **310** | **5 minutes** |

This gives InvestScan:
- KOSPI/KOSDAQ daily closes and returns
- 22 KOSPI sector index performance (THE key differentiator)
- USD/KRW, EUR/KRW, JPY/KRW exchange rates
- Fed Funds rate, 10Y Treasury yield, yield curve
- VIX, oil, gold prices
- Korean discount rate (via FRED)
- STEEPs -> sector mapping matrix

### Phase 2 (Week 2 -- Korean Depth, +80 LOC)

| Component | Library | LOC | Setup Time |
|-----------|---------|-----|------------|
| Korean macro (BOK) | PublicDataReader | 80 | 15 min (registration) |

Adds: Korean base rate history, CPI, M2 money supply, household credit, real estate prices.

### Phase 3 (Month 3+ -- Enrichment, +90 LOC)

| Component | Library | LOC | Setup Time |
|-----------|---------|-----|------------|
| OECD leading indicator | pandasdmx | 50 | 0 min |
| UN Comtrade trade flows | comtradeapicall | 40 | 10 min (registration) |

### Phase 4 (Month 6+ -- Experimental)

Google Trends sentiment, KIPRIS patents. Only if core pipeline is stable and producing value.

---

## FINAL VERDICT: Branch 1.1 vs 1.2

**The answer is neither pure 1.1 nor pure 1.2. It is Phase 1 above.**

- Branch 1.2 (Minimal) is **too thin** -- without sector indices and macro rates, InvestScan produces unfalsifiable opinions, not investment intelligence.
- Branch 1.1 (Full Comprehensive) is **too wide for Day 1** -- Google Trends, Reddit, KIPRIS, World Bank, UN Comtrade add maintenance burden with marginal value for a weekly report.
- **Phase 1 (FinanceDataReader + pykrx + FRED)** is the sweet spot: 3 libraries, 310 LOC, 5 minutes setup, zero paid subscriptions, and it provides the ESSENTIAL data trifecta:
  1. **What are Korean sectors actually doing?** (pykrx sector indices)
  2. **What is the macro environment?** (FRED rates, VIX, commodities)
  3. **What is the cross-market context?** (FDR global indices, FX)

This enables InvestScan to say: "AI regulation signals (P_Political, 3 sources) detected. Meanwhile, KOSPI Electronics sector was DOWN 1.8% this week, the Fed held rates steady, and USD/KRW strengthened to 1,340. **Direction: cautious on Electronics short-term, structurally bullish medium-term as regulation creates moats for incumbents.**"

THAT is a credible investment direction call. It requires all three data sources. It requires none of the Phase 3-4 sources.

---

## DEPENDENCY SUMMARY

```
pip install finance-datareader pykrx fredapi
```

**Total new dependencies**: 3 packages (+ their transitive deps: pandas, requests, which are already in the project)

**API keys needed**:
- FRED: Free, instant approval, save to `~/.investscan/fred_api_key.txt`
- BOK ECOS: Free, auto-issued on signup, 1 business day activation (Phase 2)

**Storage per weekly run**: ~2-5 MB (sector indices + macro snapshots as JSON/Parquet)

**Network calls per weekly run**: ~40-50 HTTP requests total (22 sector indices @ 0.3s each + 14 FRED series + FDR indices/FX/commodities)

**Execution time per weekly run**: ~15-25 seconds (dominated by pykrx scraping delays)
