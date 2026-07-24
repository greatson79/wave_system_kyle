"""
investscan/agent_context.py — Robust agent-context selection & normalization.

Fixes two latent bugs that affected ALL analyst agents:

  BUG A — Selection by string sort.  `sorted(glob('agent_context_*.json'))[-1]`
          picks the wrong file when filenames mix formats: a no-dash name like
          `agent_context_20260515.json` sorts AFTER dashed `agent_context_2026-05-27.json`
          because '-' (0x2D) < '0' (0x30).  Agents could read a stale context.
          Fix: select by the file's internal `run_date` (authoritative), not by name.

  BUG B — Schema drift.  Most context files key signals as `category`, but some
          legacy files use `steeps_category`.  A category-based filter returns 0
          on the legacy schema.  Fix: normalize so `category` always exists.

All agents should read context via load_latest_context() instead of globbing.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TEMP_DIR = Path("output/temp")


def _run_date_key(path: Path) -> tuple:
    """Sort key: prefer the file's internal run_date, fall back to mtime.

    Returns a comparable tuple so max() yields the freshest context regardless
    of filename format (dashed vs no-dash).
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rd = str(data.get("run_date", "")).strip()
        # Normalize YYYYMMDD → YYYY-MM-DD so string compare is chronological.
        if rd and "-" not in rd and len(rd) == 8 and rd.isdigit():
            rd = f"{rd[:4]}-{rd[4:6]}-{rd[6:]}"
        if rd:
            return (rd, path.stat().st_mtime)
    except Exception as exc:
        logger.debug("run_date parse failed for %s: %s", path, exc)
    return ("", path.stat().st_mtime)


def latest_context_path(temp_dir: Path | str = DEFAULT_TEMP_DIR) -> Path | None:
    """Return the agent_context file with the freshest run_date, or None."""
    temp = Path(temp_dir)
    candidates = list(temp.glob("agent_context_*.json"))
    if not candidates:
        return None
    return max(candidates, key=_run_date_key)


def _normalize_signals(ctx: dict) -> dict:
    """Ensure every signal has a `category` key (BUG B).

    Legacy files store the STEEPs tag under `steeps_category`.  Copy it to
    `category` so downstream filters (which use `category`) work uniformly.
    Mutates and returns ctx.
    """
    signals = ctx.get("envscan", {}).get("signals", [])
    if not isinstance(signals, list):
        return ctx
    for s in signals:
        if isinstance(s, dict) and "category" not in s and "steeps_category" in s:
            s["category"] = s["steeps_category"]
    return ctx


def load_latest_context(temp_dir: Path | str = DEFAULT_TEMP_DIR) -> dict:
    """Load the freshest agent context, with signals normalized.

    Raises FileNotFoundError if no context file exists — callers should fail
    loudly rather than silently analyze nothing.
    """
    path = latest_context_path(temp_dir)
    if path is None:
        raise FileNotFoundError(f"No agent_context_*.json found in {temp_dir}")
    ctx = json.loads(path.read_text(encoding="utf-8"))
    ctx = _normalize_signals(ctx)
    logger.info("Loaded context %s (run_date=%s)", path.name, ctx.get("run_date"))
    return ctx


def load_context_for_date(run_date: str, temp_dir: Path | str = DEFAULT_TEMP_DIR) -> dict:
    """Load the context whose internal run_date matches `run_date` exactly.

    Falls back to load_latest_context() if no exact match is found.
    """
    temp = Path(temp_dir)
    for path in temp.glob("agent_context_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rd = str(data.get("run_date", "")).strip()
        if rd and "-" not in rd and len(rd) == 8 and rd.isdigit():
            rd = f"{rd[:4]}-{rd[4:6]}-{rd[6:]}"
        if rd == run_date:
            return _normalize_signals(data)
    logger.warning("No context for run_date=%s — using latest", run_date)
    return load_latest_context(temp_dir)
