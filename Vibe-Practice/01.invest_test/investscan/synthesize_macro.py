"""
investscan/synthesize_macro.py — Synthesize FRED macro data into InvestmentMeta.
P1 Critical (95% TDD required). P6 Python-First: all synthesis is deterministic Python.
Reads from fred_sample.json fixture in dry-run mode.
sentiment_weight: 0.0 sentinel always maintained (never appears in output).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from investscan.schema import InvestmentMeta, SectorDirection

logger = logging.getLogger(__name__)

# ── Threshold constants (P6: never hard-code in LLM prompt) ──────────────────
DFF_HIKE_MIN: float = 5.0          # DFF >= 5.0 required for hike candidate
T10YIE_HIKE_MIN: float = 2.5       # T10YIE > 2.5 required for hike confirmation
DFF_CUT_MAX: float = 3.0           # DFF <= 3.0 triggers cut
FEDFUNDS_DELTA_CUT: float = -0.5   # FEDFUNDS delta < -0.5 triggers cut

CPIAUCSL_RISING_MIN: float = 3.5   # CPI > 3.5 → rising
CPIAUCSL_COOLING_MAX: float = 3.0  # CPI <= 3.0 → cooling (inclusive of ~2.8 fixture)

VIXCLS_HIGH_MAX: float = 15.0      # VIX < 15 required for high risk appetite
BAMLH_HIGH_MAX: float = 3.0        # OAS < 3.0 required for high risk appetite
VIXCLS_LOW_MIN: float = 25.0       # VIX > 25 → low risk appetite
BAMLH_LOW_MIN: float = 5.0         # OAS > 5.0 → low risk appetite

DTWEXBGS_STRONG_MIN: float = 105.0  # DXY > 105 → strong USD
DTWEXBGS_WEAK_MAX: float = 95.0     # DXY < 95 → weak USD

DEFAULT_FIXTURE_PATH: str = "tests/fixtures/fred_sample.json"


def get_series_value(fred_data: dict, series_id: str) -> float | None:
    """
    Extract a single series value from FRED data dict.

    Args:
        fred_data: Dict loaded from FRED API response or fixture.
        series_id: FRED series identifier (e.g., "DFF", "CPIAUCSL").

    Returns:
        float value if present and available, None otherwise.
    """
    try:
        series_entry = fred_data.get("series", {}).get(series_id)
        if series_entry is None:
            return None
        if not series_entry.get("available", True):
            return None
        value = series_entry.get("value")
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError, KeyError) as exc:
        logger.debug("get_series_value(%s) failed: %s", series_id, exc)
        return None


def _determine_rate_direction(fred_data: dict) -> str:
    """
    Determine interest rate direction using DFF and T10YIE.

    Logic:
      - DFF >= DFF_HIKE_MIN AND T10YIE > T10YIE_HIKE_MIN → "hike"
      - DFF <= DFF_CUT_MAX OR FEDFUNDS delta < FEDFUNDS_DELTA_CUT → "cut"
      - else → "hold"
    """
    dff = get_series_value(fred_data, "DFF")
    t10yie = get_series_value(fred_data, "T10YIE")
    fedfunds = get_series_value(fred_data, "FEDFUNDS")

    if dff is not None and t10yie is not None:
        if dff >= DFF_HIKE_MIN and t10yie > T10YIE_HIKE_MIN:
            return "hike"

    if dff is not None and dff <= DFF_CUT_MAX:
        return "cut"

    # FEDFUNDS delta proxy: if FEDFUNDS itself is very low relative to DFF
    # In production this would compare to prior period; here we use the raw value
    if fedfunds is not None and fedfunds < (DFF_CUT_MAX + FEDFUNDS_DELTA_CUT):
        # fedfunds < 2.5 → effectively a significant cut environment
        return "cut"

    return "hold"


def _determine_inflation_trend(fred_data: dict) -> str:
    """
    Determine inflation trend using CPIAUCSL.

    Logic:
      - CPIAUCSL > 3.5 → "rising"
      - CPIAUCSL <= 3.0 → "cooling"
      - else → "stable"
    """
    cpi = get_series_value(fred_data, "CPIAUCSL")
    if cpi is None:
        return "stable"
    if cpi > CPIAUCSL_RISING_MIN:
        return "rising"
    if cpi <= CPIAUCSL_COOLING_MAX:
        return "cooling"
    return "stable"


def _determine_risk_appetite(fred_data: dict) -> str:
    """
    Determine risk appetite using VIXCLS and BAMLH0A0HYM2.

    Logic:
      - VIX < 15 AND OAS < 3.0 → "high"
      - VIX > 25 OR OAS > 5.0 → "low"
      - else → "moderate"
    """
    vix = get_series_value(fred_data, "VIXCLS")
    oas = get_series_value(fred_data, "BAMLH0A0HYM2")

    if vix is not None and oas is not None:
        if vix < VIXCLS_HIGH_MAX and oas < BAMLH_HIGH_MAX:
            return "high"

    if vix is not None and vix > VIXCLS_LOW_MIN:
        return "low"
    if oas is not None and oas > BAMLH_LOW_MIN:
        return "low"

    return "moderate"


def _determine_usd_strength(fred_data: dict) -> str:
    """
    Determine USD strength using DTWEXBGS (Nominal Broad Dollar Index).

    Logic:
      - DTWEXBGS > 105 → "strong"
      - DTWEXBGS < 95 → "weak"
      - else → "neutral"
    """
    dxy = get_series_value(fred_data, "DTWEXBGS")
    if dxy is None:
        return "neutral"
    if dxy > DTWEXBGS_STRONG_MIN:
        return "strong"
    if dxy < DTWEXBGS_WEAK_MAX:
        return "weak"
    return "neutral"


def _derive_sector_directions(fred_data: dict) -> dict:
    """
    Derive sector-level directional signals from macro indicator combinations.
    Covers all 10 sectors in sector_stock_map.yaml.

    Returns a dict mapping sector names to directional strings.
    """
    vix = get_series_value(fred_data, "VIXCLS")
    oas = get_series_value(fred_data, "BAMLH0A0HYM2")
    dff = get_series_value(fred_data, "DFF")
    cpi = get_series_value(fred_data, "CPIAUCSL")
    dxy = get_series_value(fred_data, "DTWEXBGS")

    sectors: dict[str, str] = {}

    # ── Original 4 sectors ────────────────────────────────────────────────────

    # Technology: benefits from low rates and moderate risk appetite
    if dff is not None and vix is not None:
        if dff <= 3.0 and vix < 20:
            sectors["technology"] = "bullish"
        elif dff >= 5.0 and vix > 20:
            sectors["technology"] = "bearish"
        else:
            sectors["technology"] = "neutral"

    # Financials: benefits from higher rates and tight spreads
    if dff is not None and oas is not None:
        if dff >= DFF_HIKE_MIN and oas < BAMLH_HIGH_MAX:
            sectors["financials"] = "bullish"
        elif dff <= DFF_CUT_MAX:
            sectors["financials"] = "bearish"
        else:
            sectors["financials"] = "neutral"

    # Energy: correlated with inflation and USD strength
    if cpi is not None and dxy is not None:
        if cpi > CPIAUCSL_RISING_MIN and dxy < DTWEXBGS_WEAK_MAX:
            sectors["energy"] = "bullish"
        elif cpi <= CPIAUCSL_COOLING_MAX and dxy > DTWEXBGS_STRONG_MIN:
            sectors["energy"] = "bearish"
        else:
            sectors["energy"] = "neutral"

    # ── 16 Korea-specific sectors (v3: 20-sector framework) ──────────────────

    # Semiconductor: HBM/DRAM — AI capex proxy, lower rate sensitivity than pure tech
    if dff is not None and vix is not None:
        if dff <= 4.0 and vix < 22:
            sectors["semiconductor"] = "bullish"
        elif dff >= 5.5 or vix > 30:
            sectors["semiconductor"] = "bearish"
        else:
            sectors["semiconductor"] = "neutral"

    # Semiconductor Equipment: lags semiconductor cycle by 1–2 quarters
    # Same FRED proxy as semiconductor (capex cycle driven)
    if dff is not None and vix is not None:
        if dff <= 4.0 and vix < 22:
            sectors["semiconductor_equipment"] = "bullish"
        elif dff >= 5.5 or vix > 30:
            sectors["semiconductor_equipment"] = "bearish"
        else:
            sectors["semiconductor_equipment"] = "neutral"

    # AI Platform: growth tech (NAVER, Kakao) — rate-sensitive, risk-on
    if dff is not None and vix is not None:
        if dff <= 3.5 and vix < 18:
            sectors["ai_platform"] = "bullish"
        elif dff >= 5.0 and vix > 22:
            sectors["ai_platform"] = "bearish"
        else:
            sectors["ai_platform"] = "neutral"

    # Optical Network: AI datacenter interconnect — FRED-agnostic baseline;
    # real signal comes from external_scores (AI capex news keyword count)
    # Default neutral; external_scores boost handles actual signal
    sectors["optical_network"] = "neutral"

    # Cybersecurity: defensive growth — elevated geopolitical risk (VIX) drives spending
    if vix is not None:
        if vix > 22:
            sectors["cybersecurity"] = "bullish"
        elif vix < VIXCLS_HIGH_MAX:
            sectors["cybersecurity"] = "neutral"
        else:
            sectors["cybersecurity"] = "neutral"

    # Power Infrastructure: capex-intensive (transformers, HVDC) — AI datacenter power demand
    # Low rates enable large capex; moderate inflation justifies infrastructure pricing
    if dff is not None and cpi is not None:
        if dff <= 4.0 and cpi > 2.5:
            sectors["power_infrastructure"] = "bullish"
        elif dff >= 5.5:
            sectors["power_infrastructure"] = "neutral"
        else:
            sectors["power_infrastructure"] = "neutral"

    # Nuclear: energy inflation + long-cycle capex; CPI high → nuclear interest rises
    if cpi is not None:
        if cpi > CPIAUCSL_RISING_MIN:
            sectors["nuclear"] = "bullish"
        elif cpi <= CPIAUCSL_COOLING_MAX:
            sectors["nuclear"] = "neutral"
        else:
            sectors["nuclear"] = "neutral"

    # Battery/EV: growth sector — low rates + manageable input costs + EV adoption
    if dff is not None and vix is not None and cpi is not None:
        if dff <= 4.0 and vix < 22 and cpi <= 4.5:
            sectors["battery_ev"] = "bullish"
        elif dff >= 5.0 or cpi > 5.0:
            sectors["battery_ev"] = "bearish"
        else:
            sectors["battery_ev"] = "neutral"

    # Automotive: cyclical — rate-sensitive (auto loans) + USD-sensitive (Korean exports)
    if dff is not None and dxy is not None:
        if dff <= 3.5 and dxy < DTWEXBGS_WEAK_MAX:
            sectors["automotive"] = "bullish"
        elif dff >= 5.0 or dxy > DTWEXBGS_STRONG_MIN:
            sectors["automotive"] = "bearish"
        else:
            sectors["automotive"] = "neutral"

    # Shipbuilding: export-driven + tight credit — weak USD + narrow spreads = bullish
    if dxy is not None and oas is not None:
        if dxy < DTWEXBGS_WEAK_MAX and oas < BAMLH_HIGH_MAX:
            sectors["shipbuilding"] = "bullish"
        elif dxy > DTWEXBGS_STRONG_MIN:
            sectors["shipbuilding"] = "bearish"
        else:
            sectors["shipbuilding"] = "neutral"

    # Defense: geopolitical risk proxy — VIX elevated → defense spending visibility up
    if vix is not None:
        if vix > 22:
            sectors["defense"] = "bullish"
        elif vix < VIXCLS_HIGH_MAX:
            sectors["defense"] = "neutral"
        else:
            sectors["defense"] = "neutral"

    # Steel/Materials: commodity — high inflation + weak USD lifts prices
    if cpi is not None and dxy is not None:
        if cpi > CPIAUCSL_RISING_MIN and dxy < DTWEXBGS_WEAK_MAX:
            sectors["steel_materials"] = "bullish"
        elif cpi <= CPIAUCSL_COOLING_MAX and dxy > DTWEXBGS_STRONG_MIN:
            sectors["steel_materials"] = "bearish"
        else:
            sectors["steel_materials"] = "neutral"

    # Chemicals: petrochemical spread — same commodity logic as steel_materials
    if cpi is not None and dxy is not None:
        if cpi > CPIAUCSL_RISING_MIN and dxy < DTWEXBGS_WEAK_MAX:
            sectors["chemicals"] = "bullish"
        elif cpi <= CPIAUCSL_COOLING_MAX and dxy > DTWEXBGS_STRONG_MIN:
            sectors["chemicals"] = "bearish"
        else:
            sectors["chemicals"] = "neutral"

    # Biotech: growth/defensive hybrid — rate cuts (growth) OR risk-off (defensive CMO)
    if dff is not None and vix is not None:
        if dff <= DFF_CUT_MAX or vix > 22:
            sectors["biotech"] = "bullish"
        elif dff >= DFF_HIKE_MIN and vix < VIXCLS_HIGH_MAX:
            sectors["biotech"] = "neutral"
        else:
            sectors["biotech"] = "neutral"

    # Telecom: defensive dividend — attractive when rates high OR volatility elevated
    if dff is not None and vix is not None:
        if vix > 22 or dff >= 4.0:
            sectors["telecom"] = "bullish"
        elif vix < VIXCLS_HIGH_MAX and dff < 3.0:
            sectors["telecom"] = "neutral"
        else:
            sectors["telecom"] = "neutral"

    # Entertainment: K-content/gaming — consumer sentiment + risk appetite
    if vix is not None and dff is not None:
        if vix < 18 and dff <= 3.5:
            sectors["entertainment"] = "bullish"
        elif vix > VIXCLS_LOW_MIN:
            sectors["entertainment"] = "bearish"
        else:
            sectors["entertainment"] = "neutral"

    # Consumer: domestic demand — low rates reduce household debt; low VIX = confidence
    if dff is not None and vix is not None:
        if dff <= 3.5 and vix < 20:
            sectors["consumer"] = "bullish"
        elif dff >= 5.0 or vix > VIXCLS_LOW_MIN:
            sectors["consumer"] = "bearish"
        else:
            sectors["consumer"] = "neutral"

    return sectors


def envscan_sector_boost(agent_round2_outputs: list[dict]) -> dict[str, float]:
    """
    Aggregate sector_adjustments from analyst agent Round 2 outputs into a
    numeric score dict consumed by _build_sectors_list(external_scores=...).

    Each agent (macro, korea, tech, valuation, risk) emits `sector_adjustments`
    in their round2_*.json output: {sector_name: float} in range [-0.30, +0.30].
    This function averages across all agents that provided an adjustment and
    clamps the result to [-0.30, +0.30].

    Also applies ENVSCAN_OVERRIDE: if the average exceeds ENVSCAN_BULLISH_OVERRIDE
    threshold, the sector direction is forced to "bullish" regardless of FRED.
    This ensures strong environmental signals (e.g. defense amid active war) are
    not masked by FRED neutrality.

    Args:
        agent_round2_outputs: list of dicts loaded from output/temp/round2_*.json.
            Each dict must contain "sector_adjustments": {sector_name: float}.

    Returns:
        {sector_name: float} — aggregated boost scores, range [-0.30, +0.30].
        Empty dict if no valid inputs.
    """
    if not agent_round2_outputs:
        return {}

    CLAMP_MAX: float = 0.30
    CLAMP_MIN: float = -0.30

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}

    for output in agent_round2_outputs:
        adjustments = output.get("sector_adjustments")
        if not isinstance(adjustments, dict):
            continue
        for sector, value in adjustments.items():
            if not isinstance(value, (int, float)):
                continue
            sums[sector] = sums.get(sector, 0.0) + float(value)
            counts[sector] = counts.get(sector, 0) + 1

    result: dict[str, float] = {}
    for sector, total in sums.items():
        n = counts[sector]
        avg = total / n
        result[sector] = max(CLAMP_MIN, min(CLAMP_MAX, avg))

    logger.info(
        "envscan_sector_boost: %d sectors boosted from %d agent outputs",
        len(result), len(agent_round2_outputs),
    )
    return result


# Threshold above which envscan boost overrides FRED-neutral to "bullish"
ENVSCAN_BULLISH_OVERRIDE: float = 0.12


def _apply_envscan_overrides(
    sector_directions: dict[str, str],
    boost_scores: dict[str, float],
) -> dict[str, str]:
    """
    Override FRED-derived sector directions when envscan boost is strong enough.

    Rules (P6 Python-First — deterministic thresholds):
      - boost >= ENVSCAN_BULLISH_OVERRIDE (+0.12) AND current != "bullish"
        → force "bullish"  (strong positive envscan signal overrides FRED neutral)
      - boost <= -ENVSCAN_BULLISH_OVERRIDE (-0.12) AND current != "bearish"
        → force "bearish"  (strong negative envscan signal overrides FRED neutral)
      - |boost| < ENVSCAN_BULLISH_OVERRIDE
        → keep FRED direction unchanged

    This ensures signals like "defense sector — active war" or
    "energy sector — Hormuz blockade" are not masked by FRED neutrality.

    Args:
        sector_directions: dict produced by _derive_sector_directions().
        boost_scores: dict produced by envscan_sector_boost().

    Returns:
        Updated sector_directions dict (new dict, not mutated in-place).
    """
    updated = dict(sector_directions)
    for sector, boost in boost_scores.items():
        if boost >= ENVSCAN_BULLISH_OVERRIDE:
            if updated.get(sector) != "bullish":
                logger.info(
                    "_apply_envscan_overrides: %s neutral→bullish (boost=%.3f)", sector, boost
                )
            updated[sector] = "bullish"
        elif boost <= -ENVSCAN_BULLISH_OVERRIDE:
            if updated.get(sector) != "bearish":
                logger.info(
                    "_apply_envscan_overrides: %s neutral→bearish (boost=%.3f)", sector, boost
                )
            updated[sector] = "bearish"
        # else: keep FRED direction
    return updated


def _build_sectors_list(
    sector_directions: dict,
    external_scores: dict | None = None,
) -> list:
    """
    Convert sector_directions dict → list[SectorDirection] for typed access.
    Confidence is estimated from direction label (P6: deterministic mapping).

    Args:
        sector_directions: {sector_name: "bullish"|"neutral"|"bearish"}
        external_scores: optional {sector_name: float} from orchestrate._score_sectors().
            Highest score maps to +0.15 confidence boost (normalized).
    """
    direction_confidence = {"bullish": 0.72, "neutral": 0.55, "bearish": 0.30}
    max_ext = max(external_scores.values()) if external_scores else 1.0
    result = []
    for sector_name, direction in sector_directions.items():
        direction_cap = direction.capitalize()  # "bullish" → "Bullish"
        conf = direction_confidence.get(direction.lower(), 0.50)
        # Blend external signal score: normalize to 0~+0.15 boost
        if external_scores and sector_name in external_scores and max_ext > 0:
            boost = (external_scores[sector_name] / max_ext) * 0.15
            conf = min(conf + boost, 0.95)
        result.append(SectorDirection(
            sector_name=sector_name,
            direction=direction_cap,
            confidence=conf,
        ))
    return result


def _build_action_item(rate_direction: str, risk_appetite: str, sector_directions: dict) -> str:
    """
    Rule-based single action item (P6 Python-First — no LLM).
    Priority: rate signal > risk signal > sector signal.
    """
    bullish_sectors = [k for k, v in sector_directions.items() if v == "bullish"]

    if rate_direction == "cut":
        return "금리 인하 수혜 섹터(IT·바이오·소비재) 비중 확대 타이밍 점검"
    if rate_direction == "hike":
        return "금리 인상 압박 — 고배당·방어주 비중 유지 및 성장주 밸류에이션 재검토"
    if risk_appetite == "high" and bullish_sectors:
        return f"{bullish_sectors[0]} 섹터 외국인 수급 방향 확인 후 비중 조절 검토"
    if risk_appetite == "low":
        return "변동성 확대 구간 — 현금 비중 유지 및 방어적 포지션 점검"
    return "이번 주 매크로 변화 없음 — 현재 포지션 유지 및 다음 FOMC 일정 확인"


def _build_action_checklist(
    rate_direction: str, inflation_trend: str, risk_appetite: str, usd_strength: str
) -> list:
    """
    Rule-based weekly action checklist (P6 Python-First — no LLM).
    Returns 3-5 concrete checkable items based on macro state.
    """
    checklist = []

    # Rate signal
    if rate_direction == "cut":
        checklist.append("금리 인하 수혜주 목록 업데이트 (리츠·바이오·성장주)")
        checklist.append("단기채 → 장기채 비중 전환 타당성 점검")
    elif rate_direction == "hike":
        checklist.append("포트폴리오 내 고금리 민감 종목 듀레이션 점검")

    # Inflation signal
    if inflation_trend == "rising":
        checklist.append("원자재·에너지·소재 섹터 헤지 수단 확인")
    elif inflation_trend == "cooling":
        checklist.append("인플레이션 완화 — 소비재·IT서비스 모멘텀 재확인")

    # Risk signal
    if risk_appetite == "low":
        checklist.append("VIX 25 초과 — 옵션 헤지 또는 현금 비중 10%+ 유지 점검")
    elif risk_appetite == "high":
        checklist.append("위험선호 구간 — 성장주 비중 확대 여부 검토")

    # USD signal
    if usd_strength == "strong":
        checklist.append("원/달러 강세 — 수출주(반도체·자동차) 수혜 확인")
    elif usd_strength == "weak":
        checklist.append("달러 약세 — 수입 원가 부담 업종(항공·에너지) 리스크 점검")

    return checklist[:5]  # 최대 5개


def _build_macro_summary(
    rate_direction: str, inflation_trend: str, risk_appetite: str, usd_strength: str
) -> str:
    """One-line macro state summary (P6: deterministic template fill)."""
    return (
        f"Rate: {rate_direction.upper()} | Inflation: {inflation_trend} | "
        f"Risk appetite: {risk_appetite} | USD: {usd_strength}"
    )


def synthesize(
    fred_data: dict,
    config: dict | None = None,
    external_scores: dict | None = None,
    envscan_boost_scores: dict[str, float] | None = None,
) -> InvestmentMeta:
    """
    Synthesize FRED macro data into an InvestmentMeta object.

    All synthesis logic is deterministic Python — NO LLM calls.
    The sentiment_weight sentinel is never included in InvestmentMeta
    (it belongs only to NarrativeOutput).

    Args:
        fred_data: Dict loaded from FRED API response or dry-run fixture.
        config: Optional config dict (currently unused; reserved for future thresholds).
        external_scores: Optional {sector_name: float} from orchestrate._score_sectors().
            Blended into sector confidence as a +0~0.15 boost (M2 bridge).
        envscan_boost_scores: Optional {sector_name: float} from envscan_sector_boost().
            Aggregated analyst sector_adjustments from environmental scanning signals.
            Applied via _apply_envscan_overrides() BEFORE _build_sectors_list().
            Strong signals (|boost| >= 0.12) override FRED neutral → bullish/bearish.
            This ensures defense/energy/biotech sectors activated by war/health crises
            are not masked by FRED-only neutrality.

    Returns:
        InvestmentMeta with all fields populated including sectors (list[SectorDirection]),
        action_item, action_checklist, macro_summary (workflow.md compliance).
    """
    rate_direction = _determine_rate_direction(fred_data)
    inflation_trend = _determine_inflation_trend(fred_data)
    risk_appetite = _determine_risk_appetite(fred_data)
    usd_strength = _determine_usd_strength(fred_data)
    sector_directions = _derive_sector_directions(fred_data)

    # Apply environmental scanning overrides (P6: deterministic threshold logic)
    if envscan_boost_scores:
        sector_directions = _apply_envscan_overrides(sector_directions, envscan_boost_scores)

    generated_at = datetime.now(tz=timezone.utc).isoformat()

    # P6: build typed SectorDirection list from dict (workflow.md Step 10 compliance)
    # external_scores from orchestrate._score_sectors() blended in if provided (M2)
    sectors = _build_sectors_list(sector_directions, external_scores=external_scores)

    # P6: rule-based action items (workflow.md Step 7 requirement)
    action_item = _build_action_item(rate_direction, risk_appetite, sector_directions)
    action_checklist = _build_action_checklist(
        rate_direction, inflation_trend, risk_appetite, usd_strength
    )
    macro_summary = _build_macro_summary(
        rate_direction, inflation_trend, risk_appetite, usd_strength
    )

    logger.info(
        "synthesize_macro: rate=%s inflation=%s risk=%s usd=%s | sectors=%d action=%s",
        rate_direction, inflation_trend, risk_appetite, usd_strength,
        len(sectors), action_item[:40],
    )

    return InvestmentMeta(
        rate_direction=rate_direction,
        inflation_trend=inflation_trend,
        risk_appetite=risk_appetite,
        usd_strength=usd_strength,
        sector_directions=sector_directions,
        generated_at=generated_at,
        sectors=sectors,
        action_item=action_item,
        action_checklist=action_checklist,
        macro_summary=macro_summary,
    )


def load_fred_fixture(path: str = DEFAULT_FIXTURE_PATH) -> dict:
    """
    Load FRED fixture JSON from disk.

    Args:
        path: Path to the fixture JSON file.

    Returns:
        Parsed dict from fixture file.

    Raises:
        FileNotFoundError: if path does not exist.
        json.JSONDecodeError: if file is not valid JSON.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
