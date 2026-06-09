"""
investscan/stock_selector.py — Deterministic stock category classification.
P1 Critical (95% TDD required). P6 Python-First: classify_category() uses ONLY
numeric thresholds from config. NO LLM calls anywhere in this module.
P6 principle: "Python is the judge, LLM is the narrator."

Category A: established stocks with financial track record (YoY growth measurable)
Category B: emerging theme stocks (theme market size + positioning)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Numeric threshold constants (P6: never hard-code in LLM prompt) ──────────
BULLISH_THRESHOLD: float = 0.01      # +1% (v3.6 I-4 correction — was 0.02)
NEUTRAL_BAND: float = 0.03           # ±3%
MIN_WEEKS_TRACKED: int = 4           # v3.6 I-7: Category B zero-guard
MIN_ABS_COUNT: int = 1               # absolute safety net
CATEGORY_B_MIN_THEME_WEEKS: int = 4  # minimum trackable weeks for Category B


@dataclass
class StockClassification:
    """
    Result of classify_category() for a single stock.

    Fields:
        stock_code: KRX or ticker identifier.
        category: "A", "B", or "unknown".
        confidence: 0.0–1.0 numeric confidence score.
        classified_by: Human-readable explanation of the rule that decided the category.
    """

    stock_code: str
    category: str
    confidence: float
    classified_by: str


def _has_valid_financials(financial_history: dict | None) -> bool:
    """
    Check whether financial_history contains usable YoY revenue data.

    Validation requirements (triple guard — v3.6 I-7):
      1. financial_history is not None and not empty
      2. weeks_tracked >= MIN_WEEKS_TRACKED
      3. yoy_revenue key is present (non-None)

    Returns:
        True only when all three conditions are satisfied.
    """
    if not financial_history:
        return False

    weeks_tracked = financial_history.get("weeks_tracked", 0)
    if not isinstance(weeks_tracked, (int, float)):
        return False
    # Guard 1: minimum weeks tracked
    if weeks_tracked < MIN_WEEKS_TRACKED:
        return False

    # Guard 2: absolute count safety net
    abs_count = financial_history.get("abs_count", 0)
    if not isinstance(abs_count, (int, float)):
        return False
    if abs_count < MIN_ABS_COUNT:
        return False

    # Guard 3: YoY revenue must be present
    yoy_revenue = financial_history.get("yoy_revenue")
    if yoy_revenue is None:
        return False

    return True


def _has_valid_theme(theme_data: dict | None) -> bool:
    """
    Check whether theme_data contains usable theme market data.

    Validation requirements (triple guard — v3.6 I-7):
      1. theme_data is not None and not empty
      2. theme_weeks >= CATEGORY_B_MIN_THEME_WEEKS
      3. abs_count >= MIN_ABS_COUNT (absolute safety net — NO 'or 1' pattern)
      4. market_size is present

    Returns:
        True only when all four conditions are satisfied.
    """
    if not theme_data:
        return False

    # Guard 1: minimum theme weeks
    theme_weeks = theme_data.get("theme_weeks", 0)
    if not isinstance(theme_weeks, (int, float)):
        return False
    if theme_weeks < CATEGORY_B_MIN_THEME_WEEKS:
        return False

    # Guard 2: absolute count — NEVER use 'or 1' pattern (v3.6 I-7 bug fix)
    abs_count = theme_data.get("abs_count", 0)
    if not isinstance(abs_count, (int, float)):
        return False
    if abs_count < MIN_ABS_COUNT:
        return False

    # Guard 3: avg_count sanity check
    avg_count = theme_data.get("avg_count", 0)
    if not isinstance(avg_count, (int, float)):
        return False
    if avg_count < 0:
        return False

    # Guard 4: market_size must be present
    market_size = theme_data.get("market_size")
    if market_size is None:
        return False

    return True


def classify_category(
    stock_code: str,
    financial_history: dict | None,
    theme_data: dict | None,
) -> str:
    """
    Classify a stock as Category A, B, or unknown using deterministic thresholds.

    Rules (evaluated in priority order):
      - Has BOTH valid financial_history AND valid theme_data → "A" (financials take precedence)
      - Has valid financial_history only → "A"
      - Has valid theme_data only → "B"
      - Neither valid → "unknown"

    v3.6 I-7: triple zero-guard applied to both financial and theme validation.
    NO 'or 1' pattern is used anywhere in this function.

    Args:
        stock_code: Stock identifier (used only for logging).
        financial_history: Dict with keys: weeks_tracked, abs_count, yoy_revenue.
        theme_data: Dict with keys: theme_weeks, abs_count, avg_count, market_size.

    Returns:
        "A", "B", or "unknown".
    """
    valid_financials = _has_valid_financials(financial_history)
    valid_theme = _has_valid_theme(theme_data)

    if valid_financials:
        # Category A takes precedence even if theme data is also present
        logger.debug("classify_category(%s): → A (financials)", stock_code)
        return "A"

    if valid_theme:
        logger.debug("classify_category(%s): → B (theme)", stock_code)
        return "B"

    logger.debug("classify_category(%s): → unknown (insufficient data)", stock_code)
    return "unknown"


_CAT_A_CAP: int = 5   # mirrors agent_consensus.CAT_A_CAP
_CAT_B_CAP: int = 3
_CONDITIONAL_CAT_A_THRESHOLD: float = 0.65   # confidence gate for non-bullish sectors


def select_stocks(
    investment_meta,
    watchlist_override: list | None = None,
) -> tuple[list, list, list]:
    """
    Select Category A, Category B, and conditional-Cat-A tickers from InvestmentMeta.
    Implements workflow.md Step 10 select_stocks() specification.

    P6 Python-First: selection is deterministic threshold logic — no LLM.
    Bridges InvestmentMeta.sectors (list[SectorDirection]) and legacy
    InvestmentMeta.sector_directions (dict) — works with both.

    Args:
        investment_meta: InvestmentMeta produced by synthesize_macro.py.
        watchlist_override: Optional list of ticker strings to prioritize in Cat A.

    Returns:
        (cat_a, cat_b, conditional_cat_a): Three lists of ticker strings.
        - cat_a:            bullish direction AND confidence >= 0.65 (max 5).
        - cat_b:            bullish but confidence < 0.65 (max 3).
        - conditional_cat_a: high-confidence (>= 0.65) but non-bullish direction
                             (neutral/bearish) — preserved as user-confirmation
                             candidates rather than silently discarded (max 5).
        Tickers come from config/sector_stock_map.yaml mapping.
    """
    from pathlib import Path

    # Load sector → stock mapping (fix: navigate the 'sectors' top-level key)
    stock_map_path = Path("config/sector_stock_map.yaml")
    sectors_data: dict = {}
    if stock_map_path.exists():
        try:
            import yaml
            raw = yaml.safe_load(stock_map_path.read_text()) or {}
            sectors_data = raw.get("sectors", {})
        except Exception:
            pass

    def _get_codes(sector: str) -> list[str]:
        """Return stock codes for a sector from the YAML mapping."""
        stocks = sectors_data.get(sector, {}).get("sample_stocks", [])
        return [str(s.get("code", "")).strip() for s in stocks if s.get("code")]

    # Classify sectors into three tracks
    bullish_sectors:      list[str] = []   # direction==bullish AND conf>=0.65 → cat_a
    conditional_sectors:  list[str] = []   # conf>=0.65 but NOT bullish → conditional_cat_a
    theme_sectors:        list[str] = []   # direction==bullish but conf<0.65 → cat_b

    if investment_meta.sectors:
        # Typed path: list[SectorDirection]
        for sd in investment_meta.sectors:
            direction = (sd.direction.lower() if hasattr(sd, "direction") else "")
            confidence = (sd.confidence if hasattr(sd, "confidence") else 0.0)
            sector_name = (sd.sector_name if hasattr(sd, "sector_name") else "")
            if not sector_name:
                continue
            if direction == "bullish" and confidence >= _CONDITIONAL_CAT_A_THRESHOLD:
                bullish_sectors.append(sector_name)
            elif confidence >= _CONDITIONAL_CAT_A_THRESHOLD:
                # Non-bullish but high confidence → preserve as conditional candidate
                conditional_sectors.append(sector_name)
            elif direction == "bullish":
                theme_sectors.append(sector_name)
    else:
        # Legacy dict path: {"technology": "bullish", ...}
        for sector_name, direction in investment_meta.sector_directions.items():
            if direction.lower() == "bullish":
                bullish_sectors.append(sector_name)

    # ── Build Cat A: bullish + high-confidence (per-sector min-1 guarantee) ────
    seen: set[str] = set()
    cat_a: list[str] = []

    # Pass 1: guarantee at least 1 code per bullish sector (confidence order preserved
    # by the order sectors appear in investment_meta.sectors).
    for sector in bullish_sectors:
        for code in _get_codes(sector):
            if code and code not in seen:
                seen.add(code)
                cat_a.append(code)
                break  # one per sector in pass 1

    # Pass 2: fill remaining slots up to _CAT_A_CAP
    for sector in bullish_sectors:
        if len(cat_a) >= _CAT_A_CAP:
            break
        for code in _get_codes(sector):
            if len(cat_a) >= _CAT_A_CAP:
                break
            if code and code not in seen:
                seen.add(code)
                cat_a.append(code)

    # Apply watchlist_override — HITL-1 manual inserts take priority
    if watchlist_override:
        override_tickers = list(watchlist_override)[:_CAT_A_CAP]
        remaining = [t for t in cat_a if t not in override_tickers]
        cat_a = (override_tickers + remaining)[:_CAT_A_CAP]

    # ── Build Conditional Cat A: high-confidence non-bullish sectors ────────────
    conditional_cat_a: list[str] = []
    for sector in conditional_sectors:
        if len(conditional_cat_a) >= _CAT_A_CAP:
            break
        for code in _get_codes(sector):
            if len(conditional_cat_a) >= _CAT_A_CAP:
                break
            if code and code not in seen:
                seen.add(code)
                conditional_cat_a.append(code)

    # ── Build Cat B: lower-confidence bullish (theme signals) ───────────────────
    cat_b: list[str] = []
    for sector in theme_sectors:
        for code in _get_codes(sector):
            if len(cat_b) >= _CAT_B_CAP:
                break
            if code and code not in seen:
                seen.add(code)
                cat_b.append(code)

    logger.info(
        "select_stocks: bullish=%s conditional=%s → "
        "cat_a=%d cat_b=%d conditional_cat_a=%d tickers",
        bullish_sectors, conditional_sectors,
        len(cat_a), len(cat_b), len(conditional_cat_a),
    )
    return cat_a, cat_b, conditional_cat_a


def get_direction(return_4w: float) -> str:
    """
    Convert a 4-week return float into a directional signal string.

    Thresholds:
      - return_4w > BULLISH_THRESHOLD (+1%) → "Positive momentum maintained"
      - abs(return_4w) <= NEUTRAL_BAND (±3%) → "Neutral — monitor and wait"
      - return_4w < -NEUTRAL_BAND → "Risk zone"

    Note: The neutral band check is applied AFTER the bullish check, so values
    in (BULLISH_THRESHOLD, NEUTRAL_BAND] that are positive are caught by bullish first.
    Values in [-NEUTRAL_BAND, BULLISH_THRESHOLD] that are small-positive or negative-small
    fall into neutral.

    Args:
        return_4w: 4-week total return as a decimal (e.g., 0.05 = +5%).

    Returns:
        Direction string matching NarrativeOutput.direction literals.
    """
    if return_4w > BULLISH_THRESHOLD:
        return "Positive momentum maintained"
    if abs(return_4w) <= NEUTRAL_BAND:
        return "Neutral — monitor and wait"
    return "Risk zone"
