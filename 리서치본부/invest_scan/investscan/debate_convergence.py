"""
investscan/debate_convergence.py — Multi-round debate convergence judge.

P6 Python-First: the decision to continue or stop the agent debate is made by
deterministic Python, NOT by an LLM.  Called by invest-analysis between debate
rounds to decide whether another round is warranted.

Responsibilities:
  1. Convergence — if agents' sector_adjustments barely moved between rounds,
     further debate adds cost without insight → stop.
  2. Hard cap — never exceed MAX_ROUNDS (bounds cost; debate is N², not infinite).
  3. Divergence guard — if positions are oscillating (delta growing round over
     round), stop and write damped per-agent files (average of last two rounds)
     so agent_consensus uses a stable value instead of a swinging one.
  4. Conflict detection — surface sectors where two agents disagree strongly
     (>= CONFLICT_THRESHOLD), for the report's "의견 불일치" section.

Outputs:
  - debate_status_{DATE}.json — decision + per-round deltas + conflicts
  - round_final_{agent}_{DATE}.json — ONLY when damping is applied (divergence)

CLI (used by invest-analysis Phase 4):
    python3 -m investscan.debate_convergence --date 2026-05-27 --current-round 2
    # prints exactly one decision token to stdout: CONVERGED | CONTINUE | DIVERGED
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

TEMP_DIR = Path("output/temp")

# Sector-adjustment movement below this (max over all agents/sectors) means the
# debate has converged — another round would not change the outcome.
CONVERGENCE_THRESHOLD: float = 0.03

# Two agents whose adjustment for the SAME sector differ by at least this much
# are flagged as an unresolved conflict for the report.
CONFLICT_THRESHOLD: float = 0.15

# Hard cap on debate rounds (R1 independent + R2 + R3).  Bounds N² cost.
MAX_ROUNDS: int = 3

# Agent short-names whose round files participate in the debate.
# Mirrors agent_consensus.AGENT_WEIGHTS keys (9-agent roster).
DEBATE_AGENTS: list[str] = [
    "tech", "korea", "valuation", "macro", "risk",
    "energy", "defense", "biotech", "consumer",
]

# Decision tokens (printed to stdout for the orchestration branch).
CONVERGED = "CONVERGED"
CONTINUE = "CONTINUE"
DIVERGED = "DIVERGED"


def _load_round(agent: str, run_date: str, rnd: int) -> dict | None:
    """Load round{rnd}_{agent}_{date}.json, or None if absent/unreadable."""
    path = TEMP_DIR / f"round{rnd}_{agent}_{run_date}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return None


def _adjustments(data: dict | None) -> dict[str, float]:
    """Extract sector_adjustments dict, tolerating missing/malformed input."""
    if not data:
        return {}
    raw = data.get("sector_adjustments", {})
    if not isinstance(raw, dict):
        return {}
    out: dict[str, float] = {}
    for sector, val in raw.items():
        try:
            out[sector] = float(val)
        except (TypeError, ValueError):
            continue
    return out


def round_delta(run_date: str, rnd: int) -> tuple[float, int]:
    """
    Max absolute per-sector adjustment change between round `rnd` and `rnd-1`,
    taken across all agents.

    Returns (max_delta, agents_compared).  If an agent is missing in either
    round it is skipped (cannot compute its delta).
    """
    if rnd < 2:
        return 0.0, 0
    max_delta = 0.0
    compared = 0
    for agent in DEBATE_AGENTS:
        cur = _adjustments(_load_round(agent, run_date, rnd))
        prev = _adjustments(_load_round(agent, run_date, rnd - 1))
        if not cur or not prev:
            continue
        compared += 1
        sectors = set(cur) | set(prev)
        for s in sectors:
            d = abs(cur.get(s, 0.0) - prev.get(s, 0.0))
            if d > max_delta:
                max_delta = d
    return max_delta, compared


def detect_conflicts(run_date: str, rnd: int) -> list[dict]:
    """
    Find sectors where two agents' round-`rnd` adjustments differ by at least
    CONFLICT_THRESHOLD.  Returns a list of conflict records for the report.
    """
    per_sector: dict[str, list[tuple[str, float]]] = {}
    for agent in DEBATE_AGENTS:
        adj = _adjustments(_load_round(agent, run_date, rnd))
        for sector, val in adj.items():
            if val != 0.0:
                per_sector.setdefault(sector, []).append((agent, val))

    conflicts: list[dict] = []
    for sector, entries in per_sector.items():
        if len(entries) < 2:
            continue
        hi = max(entries, key=lambda e: e[1])
        lo = min(entries, key=lambda e: e[1])
        spread = hi[1] - lo[1]
        if spread >= CONFLICT_THRESHOLD:
            conflicts.append({
                "sector": sector,
                "spread": round(spread, 4),
                "bull": {"agent": hi[0], "adjustment": round(hi[1], 4)},
                "bear": {"agent": lo[0], "adjustment": round(lo[1], 4)},
            })
    conflicts.sort(key=lambda c: c["spread"], reverse=True)
    return conflicts


def _write_damped_finals(run_date: str, rnd: int) -> list[str]:
    """
    Oscillation damping: write round_final_{agent} = element-wise average of
    round `rnd` and round `rnd-1` sector_adjustments.  agent_consensus loads
    round_final preferentially, so the swinging value is replaced by a stable
    midpoint.  Returns the list of agents damped.
    """
    damped: list[str] = []
    for agent in DEBATE_AGENTS:
        cur_data = _load_round(agent, run_date, rnd)
        prev_data = _load_round(agent, run_date, rnd - 1)
        cur = _adjustments(cur_data)
        prev = _adjustments(prev_data)
        if not cur or not prev:
            continue
        sectors = set(cur) | set(prev)
        averaged = {
            s: round((cur.get(s, 0.0) + prev.get(s, 0.0)) / 2.0, 4)
            for s in sectors
        }
        # Preserve the rest of the latest round's payload; override adjustments.
        base = dict(cur_data) if isinstance(cur_data, dict) else {}
        base["sector_adjustments"] = averaged
        base["_damped"] = {"from_rounds": [rnd - 1, rnd], "reason": "oscillation"}
        out = TEMP_DIR / f"round_final_{agent}_{run_date}.json"
        out.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
        damped.append(agent)
    return damped


def evaluate(run_date: str, current_round: int) -> dict:
    """
    Decide whether the debate should continue after `current_round`.

    Logic:
      - current_round >= MAX_ROUNDS         → CONVERGED (hard cap reached)
      - delta(current vs prev) < threshold  → CONVERGED (positions stable)
      - delta increased vs the previous gap → DIVERGED  (oscillation → damp)
      - otherwise                           → CONTINUE  (run another round)

    Returns a status dict (also written to debate_status_{DATE}.json).
    """
    cur_delta, compared = round_delta(run_date, current_round)
    prev_delta, _ = round_delta(run_date, current_round - 1)
    conflicts = detect_conflicts(run_date, current_round)

    decision = CONTINUE
    damped: list[str] = []

    if compared == 0:
        # Cannot compare (round files missing) — do not loop forever.
        decision = CONVERGED
    elif current_round >= 3 and prev_delta > 0.0 and cur_delta > prev_delta:
        # Oscillation check before the hard cap so diverging finals are written
        # even when current_round == MAX_ROUNDS.
        decision = DIVERGED
        damped = _write_damped_finals(run_date, current_round)
    elif current_round >= MAX_ROUNDS:
        decision = CONVERGED
    elif cur_delta < CONVERGENCE_THRESHOLD:
        decision = CONVERGED

    status = {
        "date": run_date,
        "current_round": current_round,
        "max_rounds": MAX_ROUNDS,
        "current_delta": round(cur_delta, 4),
        "previous_delta": round(prev_delta, 4),
        "convergence_threshold": CONVERGENCE_THRESHOLD,
        "agents_compared": compared,
        "decision": decision,
        "damped_agents": damped,
        "unresolved_conflicts": conflicts,
    }
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    (TEMP_DIR / f"debate_status_{run_date}.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        "debate round %d: delta=%.4f (prev=%.4f) compared=%d → %s%s",
        current_round, cur_delta, prev_delta, compared, decision,
        f" (damped {len(damped)})" if damped else "",
    )
    return status


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    parser = argparse.ArgumentParser(description="Multi-round debate convergence judge")
    parser.add_argument("--date", help="Run date YYYY-MM-DD (default: today)")
    parser.add_argument(
        "--current-round", type=int, required=True,
        help="The round that just completed (2 or 3)",
    )
    parser.add_argument("--json", action="store_true", help="Print full status JSON")
    args = parser.parse_args()

    run_date = args.date or date.today().isoformat()
    status = evaluate(run_date, args.current_round)

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        # Single decision token for the orchestration branch.
        print(status["decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
