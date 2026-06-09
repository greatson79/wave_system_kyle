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
# 9-agent roster: 5 cross-cutting (tech/korea/valuation/macro/risk) +
# 4 sector specialists (energy/defense/biotech/consumer). Matches tech_cycle.
AGENT_WEIGHTS: dict[str, float] = {
    "tech":      0.28,
    "korea":     0.18,
    "valuation": 0.18,
    "macro":     0.12,
    "risk":      0.05,
    "energy":    0.07,
    "defense":   0.03,
    "biotech":   0.05,
    "consumer":  0.04,
}

# ── Regime-specific agent weight tables (dynamic — P6: Python-determined) ─────
# Each table sums to 1.0 (verified).  Selected by detect_market_regime() from
# FRED meta + orchestrate sector scores.  9-agent roster: 5 cross-cutting +
# 4 sector specialists (energy/defense/biotech/consumer).
REGIME_WEIGHTS: dict[str, dict[str, float]] = {
    "tech_cycle": {
        # Semiconductor / AI-led market
        "tech":      0.28,
        "korea":     0.18,
        "valuation": 0.18,
        "macro":     0.12,
        "risk":      0.05,
        "energy":    0.07,
        "defense":   0.03,
        "biotech":   0.05,
        "consumer":  0.04,
    },
    "macro_cycle": {
        # Rate-hike / inflation regime — macro & valuation authority rises
        "macro":     0.28,
        "valuation": 0.22,
        "korea":     0.15,
        "energy":    0.12,
        "consumer":  0.10,
        "tech":      0.06,
        "defense":   0.04,
        "biotech":   0.02,
        "risk":      0.01,
    },
    "geopolitical": {
        # Defense / energy surge — risk & defense lead
        # tech NOT excluded: semiconductor supply-chain is inseparable from
        # geopolitical risk (export controls, Taiwan strait, etc.)
        "risk":      0.22,
        "defense":   0.20,
        "macro":     0.18,
        "energy":    0.15,
        "tech":      0.10,
        "korea":     0.08,
        "valuation": 0.05,
        "consumer":  0.01,
        "biotech":   0.01,
    },
    "risk_off": {
        # Bear market / broad selloff — risk & macro dominate; defensives favored
        "risk":      0.32,
        "macro":     0.25,
        "valuation": 0.18,
        "defense":   0.08,
        "biotech":   0.06,
        "korea":     0.05,
        "consumer":  0.03,
        "energy":    0.02,
        "tech":      0.01,
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

# Stock-count caps per category.
CAT_A_CAP: int = 5
CAT_B_CAP: int = 5   # raised from 3 — 9-agent roster surfaces more Cat B sectors

# Quorum: minimum fraction of weighted agents that must produce output.
# Below this, the result is flagged low-confidence but NOT renormalized —
# renormalizing would let a single surviving agent wield full authority.
# Missing agents simply contribute 0.0, biasing the result conservative
# (toward FRED neutral base), which is the safe direction.
QUORUM_FRACTION: float = 0.60

# Loaded from sector_stock_map.yaml at import time.
# To add/remove a sector, edit config/sector_stock_map.yaml — no code change needed.
ALL_SECTORS: list[str] = _load_sectors_from_yaml()

TEMP_DIR = Path("output/temp")


def load_agent_latest(agent: str, run_date: str) -> dict | None:
    """Load the latest authoritative debate round for an agent.

    Priority: round_final > round3 > round2 > round1.
      - round_final exists only when debate_convergence.py applied oscillation
        damping (average of last two rounds) — it is authoritative when present.
      - Otherwise the highest completed round wins.  Multi-round debate may stop
        early (convergence), so round3 may be absent; per-agent latest is used.
    Returns None if no round file exists.
    """
    candidates = [
        ("final", TEMP_DIR / f"round_final_{agent}_{run_date}.json"),
        (3, TEMP_DIR / f"round3_{agent}_{run_date}.json"),
        (2, TEMP_DIR / f"round2_{agent}_{run_date}.json"),
        (1, TEMP_DIR / f"round1_{agent}_{run_date}.json"),
    ]
    for tag, path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if tag != 3:
                    logger.info("%s: using round '%s'", agent, tag)
                return data
            except Exception as exc:
                logger.warning("Skipping unreadable %s: %s — trying next round", path, exc)
                continue
    logger.warning("Agent output not found: %s (final/3/2/1)", agent)
    return None


# Backwards-compatible alias.
load_agent_round2 = load_agent_latest


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
        (weighted_adjustments, rationale_map, quorum_info)
        weighted_adjustments: {sector: float} — final weighted delta (NOT renormalized
            when agents are missing — see QUORUM_FRACTION rationale)
        rationale_map: {sector: str} — aggregated rationale strings
        quorum_info: {loaded, total, loaded_weight, quorum_ok} — diagnostics
    """
    effective_weights = weights if weights is not None else AGENT_WEIGHTS
    weighted: dict[str, float] = {s: 0.0 for s in ALL_SECTORS}
    rationales: dict[str, list[str]] = {s: [] for s in ALL_SECTORS}
    agents_loaded = 0
    loaded_weight = 0.0

    for agent, weight in effective_weights.items():
        data = load_agent_latest(agent, run_date)
        if data is None:
            continue

        adjustments = extract_sector_adjustments(data, agent)
        rationale_text = data.get("sector_adjustment_rationale", "")
        agents_loaded += 1
        loaded_weight += weight

        for sector in ALL_SECTORS:
            delta = adjustments[sector]
            # No renormalization: a missing agent contributes 0.0, biasing the
            # result toward FRED neutral base (conservative = safe direction).
            weighted[sector] += delta * weight
            if delta != 0.0:
                rationales[sector].append(
                    f"{agent}({weight:.0%}): {delta:+.2f} — {rationale_text[:60]}"
                )

    quorum_ok = loaded_weight >= QUORUM_FRACTION
    if not quorum_ok:
        logger.warning(
            "QUORUM NOT MET: loaded %d/%d agents (weight %.2f < %.2f) for %s — "
            "result is low-confidence, biased toward FRED base",
            agents_loaded, len(effective_weights), loaded_weight,
            QUORUM_FRACTION, run_date,
        )
    logger.info(
        "aggregate_adjustments: loaded %d/%d agents (weight %.2f) for %s",
        agents_loaded, len(effective_weights), loaded_weight, run_date,
    )

    # Build rationale strings
    rationale_map = {
        sector: "; ".join(items) if items else "no signal"
        for sector, items in rationales.items()
    }
    quorum_info = {
        "loaded": agents_loaded,
        "total": len(effective_weights),
        "loaded_weight": round(loaded_weight, 4),
        "quorum_ok": quorum_ok,
    }
    return weighted, rationale_map, quorum_info


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

    cat_a: sectors with final_confidence >= CONSENSUS_CAT_A_THRESHOLD (0.65),
           ONLY stocks with category_hint == 'A'.  P6: Python confirms the
           main recommendations, so they must be the vetted large-caps (hint=A),
           not small-cap theme names (hint=B) that happen to share the sector.
    cat_b: sectors with CONSENSUS_CAT_B_THRESHOLD <= conf < CAT_A (all hints) +
           hint=B stocks DEMOTED from cat_a sectors that lacked any hint=A name.

    Returns:
        (cat_a_tickers, cat_b_tickers) — deduplicated, capped at CAT_A_CAP / CAT_B_CAP
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
    # hint=B stocks from cat_a sectors are demoted to the cat_b pool (lowest priority).
    demoted_to_cat_b: list[str] = []

    # When qualifying sectors exceed the cap, only top-CAT_A_CAP (by confidence)
    # receive a min-1 guarantee.  Excess sectors are logged so nothing is silent.
    sectors_with_guarantee = cat_a_sectors[:CAT_A_CAP]
    excess_sectors = cat_a_sectors[CAT_A_CAP:]
    if excess_sectors:
        logger.warning(
            "select_confirmed_stocks: %d qualifying sectors exceed CAT_A_CAP=%d "
            "— sectors with no min-1 guarantee (confidence-dropped): %s",
            len(cat_a_sectors), CAT_A_CAP, excess_sectors,
        )

    # Pass 1: guarantee at least 1 hint=A stock per sector (confidence desc order).
    # All hint=B stocks encountered here are demoted immediately.
    for sector in sectors_with_guarantee:
        added_one = False
        for stock in sectors_yaml.get(sector, {}).get("sample_stocks", []):
            code = str(stock.get("code", "")).strip()
            if not code or code in seen:
                continue
            hint = str(stock.get("category_hint", "")).strip().upper()
            if hint == "A":
                if not added_one:
                    seen.add(code)
                    cat_a.append(code)
                    added_one = True
                # Remaining hint=A codes for this sector handled in pass 2
            else:
                # hint=B in a cat_a sector → demote, never confirm as Cat A
                if code not in demoted_to_cat_b:
                    demoted_to_cat_b.append(code)

    # Pass 2: fill remaining slots up to CAT_A_CAP with additional hint=A codes,
    # iterating sectors in confidence-desc order (highest-confidence fills first).
    for sector in sectors_with_guarantee:
        if len(cat_a) >= CAT_A_CAP:
            break
        for stock in sectors_yaml.get(sector, {}).get("sample_stocks", []):
            if len(cat_a) >= CAT_A_CAP:
                break
            code = str(stock.get("code", "")).strip()
            if not code or code in seen:
                continue
            hint = str(stock.get("category_hint", "")).strip().upper()
            if hint == "A":
                seen.add(code)
                cat_a.append(code)

    # Log sectors that got only their min-1 slot (vs more) for transparency.
    for sector in sectors_with_guarantee:
        sec_codes = {
            str(s.get("code", "")).strip()
            for s in sectors_yaml.get(sector, {}).get("sample_stocks", [])
            if str(s.get("category_hint", "")).upper() == "A"
        }
        in_cat_a = [c for c in cat_a if c in sec_codes]
        if len(in_cat_a) == 1:
            logger.info(
                "select_confirmed_stocks: sector '%s' got only min-1 slot "
                "(cap filled by higher-confidence sectors) — stock: %s",
                sector, in_cat_a[0],
            )

    cat_b: list[str] = []
    # Priority within Cat B: regular Cat B sector stocks (by confidence desc) first,
    # then stocks demoted from Cat A sectors.
    for sector in cat_b_sectors:
        for stock in sectors_yaml.get(sector, {}).get("sample_stocks", []):
            code = str(stock.get("code", "")).strip()
            if code and code not in seen and len(cat_b) < CAT_B_CAP:
                seen.add(code)
                cat_b.append(code)
    for code in demoted_to_cat_b:
        if code not in seen and len(cat_b) < CAT_B_CAP:
            seen.add(code)
            cat_b.append(code)

    logger.info(
        "select_confirmed_stocks: cat_a=%s cat_b=%s (demoted=%d)",
        cat_a, cat_b, len(demoted_to_cat_b),
    )
    return cat_a, cat_b


# ── Regime sector groups (expanded to cover all cycle-sensitive sectors) ──────
# Used ONLY for regime detection via TOP-K signal comparison.
# biotech (defensive) and entertainment (discretionary) are intentionally
# unmapped — they do not signal a tech/geo/macro CYCLE regime.
_TECH_SECTORS  = ["semiconductor", "semiconductor_equipment", "ai_platform",
                  "technology", "optical_network"]
_GEO_SECTORS   = ["defense", "shipbuilding", "nuclear", "cybersecurity",
                  "steel_materials"]
_MACRO_SECTORS = ["financials", "energy", "power_infrastructure", "chemicals",
                  "battery_ev", "automotive", "telecom", "consumer"]

# Number of top-scoring sectors summed per group.  Using TOP-K instead of a
# raw SUM makes the comparison length-neutral: adding more sectors to a group
# no longer inflates its signal by mere membership count, and zero-score
# sectors cannot dilute a group (unlike a MEAN).  K=3 is robust to both biases.
_REGIME_TOP_K: int = 3


def _top_k_signal(sector_scores: dict[str, float], sectors: list[str]) -> float:
    """Sum of the top-K orchestrate scores within a sector group."""
    vals = sorted((sector_scores.get(s, 0.0) for s in sectors), reverse=True)
    return float(sum(vals[:_REGIME_TOP_K]))


def detect_market_regime(
    sector_scores: dict[str, float],
    meta,  # InvestmentMeta | None
) -> tuple[str, dict]:
    """
    Detect current market regime from FRED meta fields + orchestrate sector scores.

    Detection priority (highest → lowest):
      1. risk_off     — FRED risk_appetite == "low"              (FRED-authoritative)
      2. macro_cycle  — FRED rate hike + rising inflation         (FRED-authoritative)
      3. geopolitical — geo TOP-K dominates with deadband         (orchestrate-based)
      4. macro_cycle  — macro TOP-K dominates with deadband       (orchestrate fallback)
      5. tech_cycle   — default

    FRED fields are evaluated first so that orchestrate_scores (which also drive
    the ±0.10 adjustment boost in build_confirmed_watchlist) are not used for BOTH
    regime switching AND adjustment blending at the same time — separation of concerns.

    Signal comparison uses TOP-K (sum of top-3 scores per group), which is
    length- and dilution-neutral, so expanding the sector groups cannot flip the
    regime through membership-count artifacts.

    Returns:
        (regime_name, regime_signals_dict)
        regime_name: "tech_cycle" | "macro_cycle" | "geopolitical" | "risk_off"
        regime_signals_dict: diagnostic snapshot included in confirmed_watchlist.json
    """
    tech_signal  = _top_k_signal(sector_scores, _TECH_SECTORS)
    geo_signal   = _top_k_signal(sector_scores, _GEO_SECTORS)
    macro_signal = _top_k_signal(sector_scores, _MACRO_SECTORS)

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
    weighted_adjustments, rationale_map, quorum_info = aggregate_adjustments(
        today, weights=dynamic_weights
    )

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
        "quorum": quorum_info,
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
