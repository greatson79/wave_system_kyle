"""
investscan/agent_consensus.py — Aggregate sector_adjustments from 5 analyst agents.

P6 Python-First: all aggregation is deterministic Python — NO LLM calls.
Reads round2_*.json outputs, applies agent weights, merges with InvestmentMeta
base confidence, applies threshold → confirmed_watchlist.json.

Usage:
    python3 -m investscan.agent_consensus --date 2026-04-06
    python3 -m investscan.agent_consensus  # defaults to today
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_SECTOR_MAP_PATH = Path(__file__).parent.parent / "config" / "sector_stock_map.yaml"


def _load_sectors_from_yaml() -> list[str]:
    """Load sector names from sector_stock_map.yaml.

    Returns the ordered list of sector keys from config.
    Falls back to the hardcoded list only if yaml is missing/unreadable,
    so adding a new sector to the yaml automatically propagates here.
    """
    try:
        import yaml  # pyyaml
        data = yaml.safe_load(_SECTOR_MAP_PATH.read_text(encoding="utf-8"))
        sectors = list(data.get("sectors", {}).keys())
        if sectors:
            return sectors
    except Exception as e:
        logger.warning("sector_stock_map.yaml 로드 실패 — fallback 사용: %s", e)
    # Fallback — mirrors sector_stock_map.yaml v3 (20 sectors)
    return [
        "semiconductor", "semiconductor_equipment", "ai_platform", "technology",
        "optical_network", "cybersecurity",
        "power_infrastructure", "nuclear", "energy",
        "battery_ev", "automotive", "shipbuilding", "defense",
        "steel_materials", "chemicals",
        "financials", "biotech", "telecom", "entertainment", "consumer",
    ]

# ── Static agent weights — tech_cycle baseline (legacy reference) ────────────
# Kept as fallback default for aggregate_adjustments().
# Active weights are selected dynamically via REGIME_WEIGHTS[regime].
AGENT_WEIGHTS: dict[str, float] = {
    "tech":      0.35,
    "korea":     0.25,
    "valuation": 0.20,
    "macro":     0.15,
    "risk":      0.05,
}

# ── Regime-specific agent weight tables (dynamic — P6: Python-determined) ─────
# Each table sums to 1.0.  Selected by detect_market_regime() from FRED meta
# + orchestrate sector scores.  Fixes the uniform-weight design flaw where
# tech(0.35) was applied to all 20 sectors regardless of market cycle.
REGIME_WEIGHTS: dict[str, dict[str, float]] = {
    "tech_cycle": {
        # Semiconductor / AI-led market — matches legacy AGENT_WEIGHTS
        "tech":      0.35,
        "korea":     0.25,
        "valuation": 0.20,
        "macro":     0.15,
        "risk":      0.05,
    },
    "macro_cycle": {
        # Rate-hike / inflation regime — macro & valuation authority rises
        "macro":     0.35,
        "valuation": 0.25,
        "korea":     0.20,
        "tech":      0.15,
        "risk":      0.05,
    },
    "geopolitical": {
        # Defense / energy / nuclear surge — risk & macro lead
        # tech NOT excluded: semiconductor supply-chain is inseparable from
        # geopolitical risk (export controls, Taiwan strait, etc.)
        "risk":      0.30,
        "macro":     0.25,
        "tech":      0.20,
        "korea":     0.15,
        "valuation": 0.10,
    },
    "risk_off": {
        # Bear market / broad selloff — risk & macro dominate; growth marginalised
        "risk":      0.40,
        "macro":     0.30,
        "valuation": 0.20,
        "korea":     0.08,
        "tech":      0.02,
    },
}

# Minimum lead margin required to switch away from tech_cycle.
# Prevents daily news-volume fluctuations from causing false regime flips.
REGIME_DEADBAND: float = 0.15

# ── Threshold constants (aligned with stock_selector.py) ──────────────────────
# Base confidence from synthesize_macro: bullish=0.72, neutral=0.55, bearish=0.30
# After agent consensus adjustment, sectors above this threshold enter cat_a/cat_b
CONSENSUS_CAT_A_THRESHOLD: float = 0.65   # cat_a: high conviction
CONSENSUS_CAT_B_THRESHOLD: float = 0.50   # cat_b: theme/emerging signal

# Loaded from sector_stock_map.yaml at import time.
# To add/remove a sector, edit config/sector_stock_map.yaml — no code change needed.
ALL_SECTORS: list[str] = _load_sectors_from_yaml()

TEMP_DIR = Path("output/temp")


def load_agent_round2(agent: str, run_date: str) -> dict | None:
    """Load round2_{agent}_{date}.json. Returns None if missing."""
    path = TEMP_DIR / f"round2_{agent}_{run_date}.json"
    if not path.exists():
        # Fallback to round1 if round2 not available
        path = TEMP_DIR / f"round1_{agent}_{run_date}.json"
        if not path.exists():
            logger.warning("Agent output not found: %s (round2 + round1)", agent)
            return None
        logger.info("round2 missing for %s — using round1 fallback", agent)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return None


def extract_sector_adjustments(agent_data: dict, agent_name: str) -> dict[str, float]:
    """
    Extract sector_adjustments from agent output.
    Returns {sector: float} with 0.0 defaults for missing sectors.
    Clamps values to [-0.30, +0.30] range.
    """
    raw = agent_data.get("sector_adjustments", {})
    if not isinstance(raw, dict):
        logger.warning("%s: sector_adjustments is not a dict — skipping", agent_name)
        return {s: 0.0 for s in ALL_SECTORS}

    result: dict[str, float] = {}
    for sector in ALL_SECTORS:
        try:
            val = float(raw.get(sector, 0.0))
            # Clamp to valid range
            result[sector] = max(-0.30, min(0.30, val))
        except (TypeError, ValueError):
            result[sector] = 0.0

    return result


def aggregate_adjustments(
    run_date: str,
    weights: dict[str, float] | None = None,
) -> tuple[dict[str, float], dict[str, str]]:
    """
    Load all 5 agents' round2 outputs and compute weighted sector adjustments.

    Args:
        run_date: Date string YYYY-MM-DD.
        weights:  Agent weight dict to apply.  Defaults to AGENT_WEIGHTS (tech_cycle).
                  Pass REGIME_WEIGHTS[regime] for dynamic regime-based weighting.

    Returns:
        (weighted_adjustments, rationale_map)
        weighted_adjustments: {sector: float} — final weighted delta
        rationale_map: {sector: str} — aggregated rationale strings
    """
    effective_weights = weights if weights is not None else AGENT_WEIGHTS
    weighted: dict[str, float] = {s: 0.0 for s in ALL_SECTORS}
    rationales: dict[str, list[str]] = {s: [] for s in ALL_SECTORS}
    agents_loaded = 0

    for agent, weight in effective_weights.items():
        data = load_agent_round2(agent, run_date)
        if data is None:
            continue

        adjustments = extract_sector_adjustments(data, agent)
        rationale_text = data.get("sector_adjustment_rationale", "")
        agents_loaded += 1

        for sector in ALL_SECTORS:
            delta = adjustments[sector]
            weighted[sector] += delta * weight
            if delta != 0.0:
                rationales[sector].append(
                    f"{agent}({weight:.0%}): {delta:+.2f} — {rationale_text[:60]}"
                )

    logger.info(
        "aggregate_adjustments: loaded %d/%d agents for %s",
        agents_loaded, len(effective_weights), run_date,
    )

    # Build rationale strings
    rationale_map = {
        sector: "; ".join(items) if items else "no signal"
        for sector, items in rationales.items()
    }
    return weighted, rationale_map


def merge_with_base_confidence(
    base_sector_directions: dict[str, str],
    weighted_adjustments: dict[str, float],
) -> dict[str, float]:
    """
    Merge FRED-derived base confidence with agent consensus adjustments.

    Base confidence (from synthesize_macro._build_sectors_list):
        bullish → 0.72, neutral → 0.55, bearish → 0.30

    Final confidence = base + weighted_adjustment, clamped to [0.0, 0.95].
    Sectors missing from base_sector_directions default to neutral (0.55).
    """
    base_map = {"bullish": 0.72, "neutral": 0.55, "bearish": 0.30}
    final: dict[str, float] = {}

    for sector in ALL_SECTORS:
        direction = base_sector_directions.get(sector, "neutral").lower()
        base_conf = base_map.get(direction, 0.55)
        adjustment = weighted_adjustments.get(sector, 0.0)
        final[sector] = max(0.0, min(0.95, base_conf + adjustment))

    return final


def select_confirmed_stocks(
    final_confidence: dict[str, float],
    sector_map_path: Path = Path("config/sector_stock_map.yaml"),
) -> tuple[list[str], list[str]]:
    """
    Apply confidence thresholds to select cat_a and cat_b stocks.

    cat_a: sectors with final_confidence >= CONSENSUS_CAT_A_THRESHOLD (0.65)
    cat_b: sectors with final_confidence >= CONSENSUS_CAT_B_THRESHOLD (0.50)
           and < CAT_A_THRESHOLD

    Returns:
        (cat_a_tickers, cat_b_tickers) — deduplicated, max 5 and 3 respectively
    """
    if not sector_map_path.exists():
        logger.error("sector_stock_map.yaml not found: %s", sector_map_path)
        return [], []

    try:
        import yaml
        data = yaml.safe_load(sector_map_path.read_text(encoding="utf-8"))
        sectors_yaml: dict = data.get("sectors", {})
    except Exception as exc:
        logger.error("Failed to load sector_stock_map.yaml: %s", exc)
        return [], []

    cat_a_sectors = sorted(
        [s for s, conf in final_confidence.items() if conf >= CONSENSUS_CAT_A_THRESHOLD],
        key=lambda s: final_confidence[s],
        reverse=True,
    )
    cat_b_sectors = sorted(
        [s for s, conf in final_confidence.items()
         if CONSENSUS_CAT_B_THRESHOLD <= conf < CONSENSUS_CAT_A_THRESHOLD],
        key=lambda s: final_confidence[s],
        reverse=True,
    )

    seen: set[str] = set()
    cat_a: list[str] = []
    for sector in cat_a_sectors:
        for stock in sectors_yaml.get(sector, {}).get("sample_stocks", []):
            code = str(stock.get("code", "")).strip()
            if code and code not in seen and len(cat_a) < 5:
                seen.add(code)
                cat_a.append(code)

    cat_b: list[str] = []
    for sector in cat_b_sectors:
        for stock in sectors_yaml.get(sector, {}).get("sample_stocks", []):
            code = str(stock.get("code", "")).strip()
            if code and code not in seen and len(cat_b) < 3:
                seen.add(code)
                cat_b.append(code)

    logger.info(
        "select_confirmed_stocks: cat_a=%s cat_b=%s",
        cat_a, cat_b,
    )
    return cat_a, cat_b


def detect_market_regime(
    sector_scores: dict[str, float],
    meta,  # InvestmentMeta | None
) -> tuple[str, dict]:
    """
    Detect current market regime from FRED meta fields + orchestrate sector scores.

    Detection priority (highest → lowest):
      1. risk_off     — FRED risk_appetite == "low"              (FRED-authoritative)
      2. macro_cycle  — FRED rate hike + rising inflation         (FRED-authoritative)
      3. geopolitical — geo sector scores dominate with deadband  (orchestrate-based)
      4. macro_cycle  — macro sector scores dominate with deadband (orchestrate fallback)
      5. tech_cycle   — default

    FRED fields are evaluated first so that orchestrate_scores (which also drive
    the ±0.10 adjustment boost in build_confirmed_watchlist) are not used for BOTH
    regime switching AND adjustment blending at the same time — separation of concerns.

    Returns:
        (regime_name, regime_signals_dict)
        regime_name: "tech_cycle" | "macro_cycle" | "geopolitical" | "risk_off"
        regime_signals_dict: diagnostic snapshot included in confirmed_watchlist.json
    """
    _TECH_SECTORS  = ["semiconductor", "ai_platform", "technology", "optical_network"]
    _GEO_SECTORS   = ["defense", "shipbuilding", "nuclear", "cybersecurity"]
    _MACRO_SECTORS = ["financials", "energy", "power_infrastructure", "chemicals"]

    tech_signal  = sum(sector_scores.get(s, 0.0) for s in _TECH_SECTORS)
    geo_signal   = sum(sector_scores.get(s, 0.0) for s in _GEO_SECTORS)
    macro_signal = sum(sector_scores.get(s, 0.0) for s in _MACRO_SECTORS)

    signals: dict = {
        "tech_signal":    round(tech_signal, 2),
        "geo_signal":     round(geo_signal, 2),
        "macro_signal":   round(macro_signal, 2),
        "risk_appetite":  getattr(meta, "risk_appetite",   "n/a") if meta else "n/a",
        "rate_direction": getattr(meta, "rate_direction",  "n/a") if meta else "n/a",
        "inflation_trend": getattr(meta, "inflation_trend", "n/a") if meta else "n/a",
    }

    # Guard: FRED unavailable
    if meta is None:
        logger.warning("detect_market_regime: meta=None — defaulting to tech_cycle")
        return "tech_cycle", signals

    # 1. risk_off: FRED risk appetite is low (bear market / broad selloff)
    if meta.risk_appetite == "low":
        return "risk_off", signals

    # 2. macro_cycle: Fed tightening + rising inflation — classic rate-hike regime
    if meta.rate_direction == "hike" and meta.inflation_trend == "rising":
        return "macro_cycle", signals

    # 3–4. Orchestrate-based regime: compare sector signal groups.
    #      REGIME_DEADBAND (15%) prevents daily score fluctuations from triggering
    #      false regime flips when signals are near-equal.
    if (geo_signal > tech_signal  * (1 + REGIME_DEADBAND)
            and geo_signal > macro_signal * (1 + REGIME_DEADBAND)):
        return "geopolitical", signals

    if macro_signal > tech_signal * (1 + REGIME_DEADBAND):
        return "macro_cycle", signals

    return "tech_cycle", signals


def build_confirmed_watchlist(run_date: str | None = None) -> dict:
    """
    Full pipeline: load agents → aggregate → merge with base → select stocks.
    Returns the confirmed watchlist dict (also written to output/temp/).

    This is the P6 Python judge — called between Phase 4 and Phase 5 of invest-analysis.
    """
    from investscan.synthesize_macro import synthesize, load_fred_fixture

    today = run_date or date.today().isoformat()

    # Load FRED base sector directions.
    # meta_obj is kept as explicit None when FRED fails so detect_market_regime
    # can handle it safely (Fix 2 — prevents NameError on unbound meta).
    meta_obj = None
    try:
        fred_data = load_fred_fixture()
        meta_obj = synthesize(fred_data)
        base_directions: dict[str, str] = meta_obj.sector_directions
    except Exception as exc:
        logger.warning("FRED base load failed (%s) — using all-neutral baseline", exc)
        base_directions = {s: "neutral" for s in ALL_SECTORS}

    # Load orchestrate sector_scores if available (M2 bridge)
    orchestrate_scores: dict[str, float] = {}
    ctx_files = sorted(TEMP_DIR.glob(f"agent_context_{today}.json"))
    if ctx_files:
        try:
            ctx = json.loads(ctx_files[-1].read_text(encoding="utf-8"))
            orchestrate_scores = ctx.get("sector_scores", {})
            if orchestrate_scores:
                logger.info(
                    "Loaded orchestrate sector_scores: %d sectors",
                    len(orchestrate_scores),
                )
        except Exception as exc:
            logger.debug("Could not load orchestrate sector_scores: %s", exc)

    # Detect market regime → select appropriate agent weights dynamically.
    # FRED fields (risk_appetite, rate_direction, inflation_trend) are the primary
    # signal; orchestrate_scores are used only for tech vs geo distinction.
    regime, regime_signals = detect_market_regime(orchestrate_scores, meta_obj)
    dynamic_weights = REGIME_WEIGHTS[regime]
    logger.info("Market regime: %s → weights: %s", regime, dynamic_weights)

    # Aggregate agent consensus adjustments using regime-specific weights
    weighted_adjustments, rationale_map = aggregate_adjustments(today, weights=dynamic_weights)

    # Optional: blend orchestrate signal scores (normalize to ±0.10 range)
    if orchestrate_scores:
        max_score = max(orchestrate_scores.values()) if orchestrate_scores else 1.0
        for sector in ALL_SECTORS:
            if sector in orchestrate_scores and max_score > 0:
                boost = (orchestrate_scores[sector] / max_score) * 0.10
                weighted_adjustments[sector] = weighted_adjustments.get(sector, 0.0) + boost

    # Merge with FRED base confidence
    final_confidence = merge_with_base_confidence(base_directions, weighted_adjustments)

    # Select stocks via threshold
    cat_a, cat_b = select_confirmed_stocks(final_confidence)

    watchlist = {
        "date": today,
        "method": "fred_base + envscan_signal + agent_consensus + dynamic_regime",
        "market_regime": regime,
        "regime_signals": regime_signals,
        "agent_weights": dynamic_weights,
        "base_sector_directions": base_directions,
        "weighted_adjustments": {k: round(v, 4) for k, v in weighted_adjustments.items()},
        "final_sector_confidence": {k: round(v, 4) for k, v in final_confidence.items()},
        "thresholds": {
            "cat_a": CONSENSUS_CAT_A_THRESHOLD,
            "cat_b": CONSENSUS_CAT_B_THRESHOLD,
        },
        "cat_a": cat_a,
        "cat_b": cat_b,
        "rationale": rationale_map,
    }

    # Write to output/temp/
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TEMP_DIR / f"confirmed_watchlist_{today}.json"
    out_path.write_text(
        json.dumps(watchlist, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Confirmed watchlist written: %s", out_path)

    # Print summary
    cat_a_sectors = [
        s for s, c in final_confidence.items() if c >= CONSENSUS_CAT_A_THRESHOLD
    ]
    cat_b_sectors = [
        s for s, c in final_confidence.items()
        if CONSENSUS_CAT_B_THRESHOLD <= c < CONSENSUS_CAT_A_THRESHOLD
    ]
    print(f"\n{'='*60}")
    print(f"  InvestScan Confirmed Watchlist — {today}")
    print(f"{'='*60}")
    print(f"  Market Regime: {regime} (signals: {regime_signals})")
    print(f"  Agent Weights: {dynamic_weights}")
    print(f"  Cat A sectors ({CONSENSUS_CAT_A_THRESHOLD}+): {cat_a_sectors}")
    print(f"  Cat B sectors ({CONSENSUS_CAT_B_THRESHOLD}+): {cat_b_sectors}")
    print(f"  Cat A stocks : {cat_a}")
    print(f"  Cat B stocks : {cat_b}")
    print(f"  Written      : {out_path}")
    print(f"{'='*60}\n")

    return watchlist


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    parser = argparse.ArgumentParser(
        description="Aggregate agent sector_adjustments → confirmed_watchlist.json"
    )
    parser.add_argument("--date", help="Run date YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", help="Print result JSON to stdout")
    args = parser.parse_args()

    result = build_confirmed_watchlist(run_date=args.date)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
