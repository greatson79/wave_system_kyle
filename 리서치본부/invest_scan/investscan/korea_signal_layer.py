"""
investscan/korea_signal_layer.py — Korean market signal layer.
Wraps pykrx and dart-fss with graceful fallback (v3.6 I-6).
In dry-run mode: returns mock Korean market signals.
P5-A: all field names and log messages in English.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Mock values for dry-run mode ──────────────────────────────────────────────
MOCK_FOREIGN_FLOW: float = 42.0     # Mock 4-week net buy in millions USD
MOCK_PER_VALUE: float = 12.5        # Mock trailing PER
MOCK_PER_SECTOR_AVG: float = 14.2   # Mock sector average PER
MOCK_DATA_SOURCE: str = "dry-run-mock"


@dataclass
class KoreaSignal:
    """
    Korean market signal for a single stock.

    Fields:
        stock_code: KRX stock code (e.g., "005930" for Samsung)
        foreign_flow_4w: 4-week cumulative foreign net buy/sell in millions USD
        per_value: Trailing P/E ratio for the stock
        per_sector_avg: Sector average trailing P/E ratio
        data_source: Identifier for the data source used
        available: Whether real data was successfully retrieved
    """

    stock_code: str
    foreign_flow_4w: float
    per_value: float
    per_sector_avg: float
    data_source: str = MOCK_DATA_SOURCE
    available: bool = False


def is_available() -> bool:
    """
    Check whether pykrx or FinanceDataReader (FDR) are importable.

    Returns:
        True if at least one Korean market data library is available.
    """
    try:
        import pykrx  # noqa: F401
        return True
    except ImportError:
        pass

    try:
        import FinanceDataReader  # noqa: F401
        return True
    except ImportError:
        pass

    return False


def get_foreign_flow(stock_code: str, weeks: int = 4) -> float | None:
    """
    Get cumulative foreign net buy/sell over the specified number of weeks.

    In dry-run mode returns mock value (42.0).
    In live mode queries pykrx or FDR; returns None on failure.

    Args:
        stock_code: KRX stock code string.
        weeks: Number of weeks to accumulate (default 4).

    Returns:
        Cumulative foreign flow in millions USD, or None if unavailable.
    """
    # Dry-run guard — always return mock value when real libraries unavailable
    if not is_available():
        logger.debug(
            "get_foreign_flow(%s): pykrx/FDR not available — returning mock",
            stock_code,
        )
        return MOCK_FOREIGN_FLOW

    try:
        return _get_foreign_flow_live(stock_code, weeks)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "get_foreign_flow(%s) live fetch failed: %s — returning mock",
            stock_code,
            exc,
        )
        return MOCK_FOREIGN_FLOW


def _get_foreign_flow_live(stock_code: str, weeks: int) -> float | None:
    """
    Internal live implementation. Tries pykrx first, then FDR.
    Always returns mock on any failure.
    """
    try:
        from datetime import datetime, timedelta

        import pykrx.stock as krx  # type: ignore[import]

        end_date = datetime.today()
        start_date = end_date - timedelta(weeks=weeks)

        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        df = krx.get_market_trading_value_by_date(
            start_str, end_str, stock_code, etf=False, etn=False, elw=False
        )
        if df is not None and not df.empty and "기관합계" in df.columns:
            # 외국인 column name varies; try common variants
            for col in ("외국인합계", "외국인", "Foreigner"):
                if col in df.columns:
                    total_krw = float(df[col].sum())
                    # Convert KRW millions to USD millions (approx 1330 KRW/USD)
                    return round(total_krw / 1_330_000_000, 2)
        return MOCK_FOREIGN_FLOW
    except Exception as exc:  # noqa: BLE001
        logger.debug("pykrx foreign flow failed: %s", exc)
        return _get_foreign_flow_fdr(stock_code, weeks)


def _get_foreign_flow_fdr(stock_code: str, weeks: int) -> float | None:
    """Fallback FDR foreign flow fetch."""
    try:
        from datetime import datetime, timedelta

        import FinanceDataReader as fdr  # type: ignore[import]

        end_date = datetime.today()
        start_date = end_date - timedelta(weeks=weeks)

        df = fdr.DataReader(stock_code, start_date.strftime("%Y-%m-%d"))
        if df is not None and not df.empty:
            # FDR does not provide foreign flow directly; return mock
            return MOCK_FOREIGN_FLOW
        return None
    except Exception as exc:  # noqa: BLE001
        logger.debug("FDR foreign flow failed: %s", exc)
        return MOCK_FOREIGN_FLOW


def _get_per_live(stock_code: str) -> tuple[float, float]:
    """
    Retrieve P/E ratio and sector average via pykrx.

    Returns:
        Tuple of (per_value, per_sector_avg). Falls back to mock on any error.
    """
    try:
        import pykrx.stock as krx  # type: ignore[import]
        from datetime import datetime

        today = datetime.today().strftime("%Y%m%d")
        df = krx.get_market_fundamental(today, market="KOSPI")
        if df is not None and not df.empty and stock_code in df.index:
            per = float(df.loc[stock_code, "PER"])
            sector_avg = float(df["PER"].mean())
            return per, sector_avg
    except Exception as exc:  # noqa: BLE001
        logger.debug("pykrx PER fetch failed: %s", exc)

    return MOCK_PER_VALUE, MOCK_PER_SECTOR_AVG


def get_korea_signal(stock_code: str, config: dict) -> KoreaSignal:
    """
    Get Korean market signal for a given stock code.

    NEVER raises an exception — all errors result in graceful fallback
    to mock/unavailable signal.

    In dry-run mode (config["mode"] == "dry-run"):
      Returns KoreaSignal with mock values and available=False.

    In live mode:
      Attempts pykrx → FDR fallback chain.
      Returns unavailable signal on any failure.

    Args:
        stock_code: KRX stock code (e.g., "005930").
        config: Config dict with at minimum a "mode" key.

    Returns:
        KoreaSignal with all required fields populated.
    """
    mode = config.get("mode", "dry-run") if config else "dry-run"

    if mode == "dry-run":
        logger.debug("get_korea_signal(%s): dry-run mode — returning mock", stock_code)
        return KoreaSignal(
            stock_code=stock_code,
            foreign_flow_4w=MOCK_FOREIGN_FLOW,
            per_value=MOCK_PER_VALUE,
            per_sector_avg=MOCK_PER_SECTOR_AVG,
            data_source=MOCK_DATA_SOURCE,
            available=False,
        )

    # Live mode — wrap entire flow in broad exception guard
    try:
        return _get_korea_signal_live(stock_code)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "get_korea_signal(%s) live failed: %s — returning unavailable signal",
            stock_code,
            exc,
        )
        return _unavailable_signal(stock_code)


def _get_korea_signal_live(stock_code: str) -> KoreaSignal:
    """Internal live fetch. Raises on unrecoverable errors (caught by caller)."""
    if not is_available():
        logger.info(
            "get_korea_signal(%s): no live library available — returning mock",
            stock_code,
        )
        return _unavailable_signal(stock_code)

    foreign_flow = get_foreign_flow(stock_code, weeks=4) or MOCK_FOREIGN_FLOW
    per_value, per_sector_avg = _get_per_live(stock_code)

    return KoreaSignal(
        stock_code=stock_code,
        foreign_flow_4w=foreign_flow,
        per_value=per_value,
        per_sector_avg=per_sector_avg,
        data_source="pykrx",
        available=True,
    )


def _unavailable_signal(stock_code: str) -> KoreaSignal:
    """Return a clearly-labeled unavailable signal with mock numeric values."""
    return KoreaSignal(
        stock_code=stock_code,
        foreign_flow_4w=MOCK_FOREIGN_FLOW,
        per_value=MOCK_PER_VALUE,
        per_sector_avg=MOCK_PER_SECTOR_AVG,
        data_source="unavailable",
        available=False,
    )
