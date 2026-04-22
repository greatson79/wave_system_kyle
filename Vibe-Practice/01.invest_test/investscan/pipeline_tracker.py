"""
investscan/pipeline_tracker.py — Pipeline execution state tracker.

Writes phase status to output/temp/pipeline_status.json (atomic write).
All writes are non-blocking — exceptions are silently ignored.
English-First (P5-A).

CLI:
    python3 -m investscan.pipeline_tracker --phase PHASE --status STATUS [--agent NAME]
    python3 -m investscan.pipeline_tracker --reset   # start a new run

Phase values:
    phase_0 | phase_1_envscan | phase_1_gnews | phase_2 |
    phase_3 | phase_4 | phase_5 | phase_6

Status values:
    pending | running | completed | failed | skipped

Agent names (phase_3 / phase_4 only):
    macro | tech | korea | valuation | risk
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

STATUS_FILE = Path("output/temp/pipeline_status.json")

PHASES_ORDERED = [
    "phase_0",
    "phase_1_envscan",
    "phase_1_gnews",
    "phase_2",
    "phase_3",
    "phase_4",
    "phase_5",
    "phase_6",
]

AGENT_NAMES = ["macro", "tech", "korea", "valuation", "risk"]

VALID_STATUSES = ["pending", "running", "completed", "failed", "skipped"]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _empty_phase(phase_name: str) -> dict:
    base: dict = {
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "duration_sec": None,
    }
    if phase_name in ("phase_3", "phase_4"):
        base["agents"] = {a: "pending" for a in AGENT_NAMES}
    return base


def _empty_status() -> dict:
    now = datetime.now().isoformat()
    return {
        "run_id": now,
        "started_at": now,
        "last_updated": now,
        "current_phase": "phase_0",
        "phases": {p: _empty_phase(p) for p in PHASES_ORDERED},
    }


def _load() -> dict:
    """Load existing pipeline_status.json or return empty skeleton."""
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return _empty_status()


def _save(state: dict) -> None:
    """Atomic write: write to .tmp then rename."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    tmp = STATUS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(STATUS_FILE)


# ── Public API ────────────────────────────────────────────────────────────────

def update_phase(phase: str, status: str, agent: Optional[str] = None) -> None:
    """
    Update phase (or agent within phase_3/phase_4) status.
    Non-blocking: all exceptions are silently ignored.
    """
    try:
        state = _load()
        now = datetime.now().isoformat()
        phases = state.setdefault("phases", {})

        if phase not in phases:
            phases[phase] = _empty_phase(phase)

        p = phases[phase]

        if agent and phase in ("phase_3", "phase_4"):
            # Agent-level update
            p.setdefault("agents", {a: "pending" for a in AGENT_NAMES})[agent] = status
            agent_vals = list(p["agents"].values())
            if all(s == "completed" for s in agent_vals):
                p["status"] = "completed"
                p["completed_at"] = now
                if p.get("started_at"):
                    try:
                        start = datetime.fromisoformat(p["started_at"])
                        p["duration_sec"] = round(
                            (datetime.now() - start).total_seconds()
                        )
                    except Exception:
                        pass
            elif any(s == "running" for s in agent_vals):
                if p.get("status") != "running":
                    p["status"] = "running"
                    if not p.get("started_at"):
                        p["started_at"] = now
                        state["current_phase"] = phase
            elif any(s == "failed" for s in agent_vals):
                p["status"] = "partial_failed"
        else:
            # Phase-level update
            old_status = p.get("status", "pending")
            p["status"] = status

            if status == "running" and old_status != "running":
                p["started_at"] = now
                state["current_phase"] = phase

            elif status in ("completed", "failed", "skipped"):
                p["completed_at"] = now
                if p.get("started_at"):
                    try:
                        start = datetime.fromisoformat(p["started_at"])
                        p["duration_sec"] = round(
                            (datetime.now() - start).total_seconds()
                        )
                    except Exception:
                        pass

        _save(state)
    except Exception:
        pass  # Never raise — tracking must not interrupt the pipeline


def reset(run_id: Optional[str] = None) -> None:
    """Reset pipeline_status.json to a fresh state (new pipeline run)."""
    try:
        state = _empty_status()
        if run_id:
            state["run_id"] = run_id
        _save(state)
    except Exception:
        pass


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="InvestScan pipeline phase tracker"
    )
    parser.add_argument(
        "--phase",
        choices=PHASES_ORDERED,
        help="Phase name to update",
    )
    parser.add_argument(
        "--status",
        choices=VALID_STATUSES,
        help="New status value",
    )
    parser.add_argument(
        "--agent",
        choices=AGENT_NAMES,
        default=None,
        help="Agent name (phase_3 / phase_4 only)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset to a fresh run before applying update",
    )
    args = parser.parse_args()

    if args.reset:
        reset()

    if args.phase and args.status:
        update_phase(args.phase, args.status, agent=args.agent)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
