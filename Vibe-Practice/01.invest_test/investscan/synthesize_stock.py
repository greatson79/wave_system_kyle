"""
investscan/synthesize_stock.py — Synthesize stock-level financial data.
Primary source: DART (official financial statements — YoY revenue/op-income growth).
Secondary source: Naver Finance (real-time price, PER, EPS, foreign ratio).
Fallback chain: dart → naver_finance → partial data (never raises on API failure).
English-First (P5-A). Python-First (P6): all synthesis decisions are deterministic.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class StockFinancials:
    """Synthesized stock financial data for intelligence_engine context."""

    stock_code: str
    stock_name: str
    category: str                           # "A" or "B" from stock_selector
    yoy_revenue_growth: float | None        # decimal (0.083 = 8.3%)
    yoy_op_income_growth: float | None
    latest_quarter: str                     # e.g., "2025Q4"
    per_current: float | None
    per_sector_avg: float | None
    foreign_flow_4w: float | None           # millions USD, net buy positive
    data_freshness_note: str = ""           # populated when data is partial
    data_source: str = "partial"            # "naver_finance" | "naver_finance+korea_signal" | "partial" | "mock"


def synthesize_stock_data(
    stock_code: str,
    stock_name: str,
    category: str,
    korea_signal: Any | None = None,
    config: dict | None = None,
) -> StockFinancials:
    """
    Synthesize all available stock data from DART, pykrx, and FDR.
    Never raises: all API failures result in partial data with data_freshness_note.

    Args:
        stock_code: KRX stock code (e.g., "005930")
        stock_name: Stock display name
        category: "A" or "B" from stock_selector
        korea_signal: KoreaSignal from korea_signal_layer (optional)
        config: investscan config dict (used to detect dry-run mode)

    Returns:
        StockFinancials with available data. Partial data noted in data_freshness_note.
    """
    config = config or {}
    is_dry = config.get("mode", "dry-run") == "dry-run"

    if is_dry:
        return _mock_stock_financials(stock_code, stock_name, category)

    # Live mode: attempt real data collection with fallback chain
    yoy_revenue = None
    yoy_op_income = None
    latest_quarter = ""
    per_current = None
    per_sector_avg = None
    foreign_flow = None
    sources_used = []
    notes = []

    # Source 1: DART official financial statements (YoY revenue + op-income growth)
    dart_result = _fetch_dart_financials(stock_code, config)
    if dart_result:
        yoy_revenue    = dart_result.get("yoy_revenue_growth")
        yoy_op_income  = dart_result.get("yoy_op_income_growth")
        latest_quarter = dart_result.get("latest_quarter", "")
        sources_used.append("dart")
    else:
        notes.append("dart unavailable")

    # Source 2: Naver Finance (real-time price + PER)
    try:
        naver_info = _fetch_naver_finance_data(stock_code)
        if naver_info:
            per_current = naver_info.get("per_float")
            # Use naver op_income_growth only if DART didn't provide it
            if yoy_op_income is None:
                op_growth_str = naver_info.get("op_income_growth", "")
                if op_growth_str and op_growth_str != "N/A":
                    try:
                        yoy_op_income = float(op_growth_str.rstrip("%")) / 100.0
                    except ValueError:
                        pass
            sources_used.append("naver_finance")
    except Exception as e:
        logger.warning("Naver Finance fetch failed for %s: %s", stock_code, e)
        notes.append("naver_finance unavailable")

    # Source 3: Foreign flow from korea_signal
    if korea_signal is not None:
        foreign_flow = getattr(korea_signal, "foreign_flow_4w", None)
        if foreign_flow is not None:
            sources_used.append("korea_signal")

    data_source = "+".join(sources_used) if sources_used else "partial"
    freshness_note = "; ".join(notes) if notes else ""

    return StockFinancials(
        stock_code=stock_code,
        stock_name=stock_name,
        category=category,
        yoy_revenue_growth=yoy_revenue,
        yoy_op_income_growth=yoy_op_income,
        latest_quarter=latest_quarter,
        per_current=per_current,
        per_sector_avg=per_sector_avg,
        foreign_flow_4w=foreign_flow,
        data_freshness_note=freshness_note,
        data_source=data_source,
    )


def _mock_stock_financials(stock_code: str, stock_name: str, category: str) -> StockFinancials:
    """Return realistic mock data for dry-run mode and TDD."""
    mock_data: dict[str, dict] = {
        "005930": {
            "yoy_revenue_growth": 0.083,
            "yoy_op_income_growth": 0.342,
            "latest_quarter": "2025Q4",
            "per_current": 10.2,
            "per_sector_avg": 14.2,
            "foreign_flow_4w": 380.0,
        },
        "000660": {
            "yoy_revenue_growth": 0.156,
            "yoy_op_income_growth": 0.891,
            "latest_quarter": "2025Q4",
            "per_current": 12.8,
            "per_sector_avg": 14.2,
            "foreign_flow_4w": 210.0,
        },
        "035420": {
            "yoy_revenue_growth": 0.042,
            "yoy_op_income_growth": 0.031,
            "latest_quarter": "2025Q3",
            "per_current": 28.4,
            "per_sector_avg": 22.1,
            "foreign_flow_4w": -45.0,
        },
    }
    d = mock_data.get(stock_code, {
        "yoy_revenue_growth": 0.05,
        "yoy_op_income_growth": 0.08,
        "latest_quarter": "2025Q3",
        "per_current": 15.0,
        "per_sector_avg": 15.0,
        "foreign_flow_4w": None,  # unknown stocks: no ground truth → NBS-03 skipped
    })
    return StockFinancials(
        stock_code=stock_code,
        stock_name=stock_name,
        category=category,
        yoy_revenue_growth=d["yoy_revenue_growth"],
        yoy_op_income_growth=d["yoy_op_income_growth"],
        latest_quarter=d["latest_quarter"],
        per_current=d["per_current"],
        per_sector_avg=d["per_sector_avg"],
        foreign_flow_4w=d["foreign_flow_4w"],
        data_freshness_note="",
        data_source="mock",
    )


def _fetch_dart_financials(stock_code: str, config: dict) -> dict | None:
    """
    Fetch YoY revenue and operating income growth from DART official filings.
    Resolves API key via get_api_key() (keyring in live mode).
    Returns dict with keys: yoy_revenue_growth, yoy_op_income_growth, latest_quarter.
    Returns None on any failure — caller falls back to Naver Finance.

    DART FinancialStatement structure (dart-fss >= 0.4.15):
      fs._statements['is'] — MultiIndex DataFrame
        column level-0: table title string
        column level-1: 'concept_id' | 'label_ko' | ... | '20240101-20241231' (date range)
      date-range columns have tuple values: ('연결재무제표',) sub-type
    """
    try:
        import dart_fss as dart
        from investscan.config import get_api_key, ConfigError

        try:
            api_key = get_api_key("dart_api_key", config)
        except ConfigError as e:
            logger.warning("DART API key unavailable: %s", e)
            return None

        dart.set_api_key(api_key)
        corp_list = dart.get_corp_list()

        corp = corp_list.find_by_stock_code(stock_code)
        if corp is None:
            logger.warning("DART: corp not found for stock_code=%s", stock_code)
            return None

        # Fetch last 2 full years (연결 우선, 별도 fallback)
        bgn_year = str(date.today().year - 2)
        fs = None
        for separate in (False, True):
            try:
                fs = corp.extract_fs(bgn_de=f"{bgn_year}0101", separate=separate)
                if fs is not None:
                    break
            except Exception as e:
                logger.debug("DART extract_fs separate=%s failed for %s: %s", separate, stock_code, e)

        if fs is None:
            return None

        # Income statement: 'is' first, fallback to 'cis' (포괄손익계산서)
        stmts = getattr(fs, "_statements", {})
        is_df = stmts.get("is")
        if is_df is None:
            is_df = stmts.get("cis")
        if is_df is None or is_df.empty:
            logger.warning("DART: no income statement for %s", stock_code)
            return None

        # Locate concept_id column (level-1 == 'concept_id')
        concept_col = next(
            (c for c in is_df.columns if c[1] == "concept_id"),
            None,
        )
        if concept_col is None:
            return None

        # Date-range columns: MultiIndex tuple (date_str, sub_label)
        # date_str format: '20240101-20241231', sub_label: ('연결재무제표',)
        date_cols = sorted(
            [c for c in is_df.columns if str(c[0]).startswith("20") and "-" in str(c[0])],
            key=lambda c: c[0],
            reverse=True,  # most recent first
        )
        if len(date_cols) < 2:
            logger.warning("DART: insufficient date columns for %s (%d)", stock_code, len(date_cols))
            return None

        cur_col, prev_col = date_cols[0], date_cols[1]
        latest_year = str(cur_col[0])[:4]  # '20240101-20241231' → '2024'

        # Concept IDs for revenue and operating income (IFRS / DART tags)
        _REVENUE_IDS = {"ifrs-full_Revenue", "ifrs-full_SalesRevenue", "dart_Revenue"}
        _OP_INCOME_IDS = {"dart_OperatingIncomeLoss", "ifrs-full_ProfitLossFromOperatingActivities"}

        def _extract_value(col) -> float | None:
            val = str(col).replace(",", "").strip()
            if val in ("", "None", "nan"):
                return None
            try:
                return float(val)
            except ValueError:
                return None

        def _yoy(row_mask) -> float | None:
            rows = is_df[row_mask]
            if rows.empty:
                return None
            row = rows.iloc[0]
            cur  = _extract_value(row[cur_col])
            prev = _extract_value(row[prev_col])
            if cur is None or prev is None or prev == 0:
                return None
            return round((cur - prev) / abs(prev), 4)

        rev_mask = is_df[concept_col].isin(_REVENUE_IDS)
        op_mask  = is_df[concept_col].isin(_OP_INCOME_IDS)

        return {
            "yoy_revenue_growth":   _yoy(rev_mask),
            "yoy_op_income_growth": _yoy(op_mask),
            "latest_quarter":       latest_year,
        }

    except Exception as e:
        logger.warning("DART fetch error for %s: %s", stock_code, e)
        return None


def _fetch_naver_finance_data(stock_code: str) -> dict | None:
    """
    Fetch real-time financial data from Naver Finance.
    Returns parsed dict or None on failure.
    """
    try:
        from investscan.naver_finance import fetch_stock
        info = fetch_stock(stock_code, delay=0.3)
        if info is None:
            return None

        # Parse PER float (strip 배 suffix)
        per_float = None
        per_str = info.get("per", "N/A")
        if per_str and per_str != "N/A":
            try:
                per_float = float(per_str.rstrip("배").replace(",", ""))
            except ValueError:
                pass

        return {
            "per_float": per_float,
            "op_income_growth": info.get("op_income_growth", "N/A"),
            "foreign_ratio": info.get("foreign_ratio", "N/A"),
            "market_cap": info.get("market_cap", "N/A"),
            "roe": info.get("roe", "N/A"),
        }
    except Exception as e:
        logger.warning("Naver Finance import/fetch failed for %s: %s", stock_code, e)
        return None
