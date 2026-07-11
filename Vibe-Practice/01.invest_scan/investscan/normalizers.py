"""
investscan/normalizers.py — Normalize EnvironmentScan output to UnifiedSignal schema.
Reads actual field names from state.yaml discovered_schema (or uses fixture defaults).
English-First (P5-A). Python-First (P6): all transformations are deterministic Python.

Supports three EnvScan formats:
  WF1 (fixture):   {"entries": [...], "schema": {...}} — PRD expected format
  WF4 (actual):    {"signals": [...]} — real database.json from EnvironmentScan v4
  WF_ACTUAL (v4+): raw JSON array [...] — actual WF*.json output files (EnvironmentScan v4+)
"""
from __future__ import annotations

import json
import logging
from typing import Any

from investscan.schema import UnifiedSignal

logger = logging.getLogger(__name__)

# Default field name mapping (matches envscan_sample.json schema block)
_DEFAULT_SCHEMA_HINTS: dict[str, str] = {
    "steeps_field": "steeps_category",
    "psst_field": "pSST",
    "summary_field": "summary",
    "score_scale": "0-100",
}

# UnifiedSignal optional fields that may be present in raw entries
_OPTIONAL_FIELDS = ("sector", "confidence", "date", "source")

# WF4 schema hints for actual database.json (EnvironmentScan v4)
# psst_default: "50.0" — 585/686 records lack analysis block; use midpoint instead of skip
WF4_SCHEMA_HINTS: dict[str, str] = {
    "steeps_field": "preliminary_category",
    "psst_field": "analysis.priority_score",
    "summary_field": "content.abstract",
    "score_scale": "0-5",
    "date_field": "collected_at",
    "source_field": "source.name",
    "entries_key": "signals",
    "psst_default": "50.0",  # use midpoint when analysis block absent
}

# WF_ACTUAL schema hints for actual WF*.json output files (EnvironmentScan v4+)
# These are raw JSON arrays: [{id, title, url, source{...}, published_date, preliminary_category, summary}]
# No score field exists — use 50.0 midpoint for all records.
ENVSCAN_WF_ACTUAL_HINTS: dict[str, str] = {
    "steeps_field":  "preliminary_category",
    "psst_field":    "__none__",      # no score in WF* files
    "summary_field": "summary",       # direct "summary" field (not content.abstract)
    "score_scale":   "0-100",
    "date_field":    "published_date",
    "source_field":  "source.name",   # nested: source → name
    "entries_key":   "signals",       # used after wrapping: {"__format__": "wf_actual", "signals": [...]}
    "psst_default":  "50.0",
}

_FORMAT_WF_ACTUAL = "wf_actual"   # marker injected by load_envscan_file

# Map real database.json category codes → UnifiedSignal steeps_category values
_STEEPS_ALIAS: dict[str, str] = {
    "E_Environmental": "E_env",   # WF4 uses full name; schema uses short code
}


def _get_nested(entry: dict, dotted_path: str) -> Any:
    """
    Extract a value from a nested dict using dot notation.
    "content.abstract" → entry["content"]["abstract"]
    Falls back to None if any key is missing.
    """
    parts = dotted_path.split(".")
    current: Any = entry
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _resolve_hints(data: dict, schema_hints: dict | None) -> dict[str, str]:
    """
    Merge schema hints in priority order:
      1. Caller-supplied schema_hints (highest)
      2. data["schema"] block embedded in the JSON file
      3. _DEFAULT_SCHEMA_HINTS (fallback)
    """
    merged: dict[str, str] = dict(_DEFAULT_SCHEMA_HINTS)

    # Layer 2: embedded schema block
    embedded = data.get("schema", {})
    if isinstance(embedded, dict):
        merged.update(embedded)

    # Layer 1: caller-supplied hints (highest priority)
    if schema_hints:
        merged.update(schema_hints)

    return merged


def _normalize_score(raw_value: Any, score_scale: str) -> float:
    """
    Convert *raw_value* to a 0-100 float.

    Handles three scale formats:
      "0-100"  — value is already in range, clamp only.
      "0-1"    — multiply by 100.
      "0-5"    — WF4 priority_score (0-5) → multiply by 20.
      "0-10"   — WF4 alternative scale → multiply by 10.
    """
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Cannot convert psst score to float: {raw_value!r}") from exc

    if score_scale == "0-1":
        value = value * 100.0
    elif score_scale == "0-5":
        value = value * 20.0   # 0-5 → 0-100
    elif score_scale == "0-10":
        value = value * 10.0   # 0-10 → 0-100

    # Clamp to [0, 100]
    return max(0.0, min(100.0, value))


def normalize_envscan(
    data: dict,
    schema_hints: dict | None = None,
) -> list[UnifiedSignal]:
    """
    Normalize a loaded EnvironmentScan JSON dict into a list of UnifiedSignal objects.

    Supports two formats automatically:
      WF1 (fixture/PRD): top-level "entries" key, flat fields
      WF4 (actual v4):   top-level "signals" key, nested fields ("content.abstract" etc.)

    Parameters
    ----------
    data:
        Parsed JSON content from the EnvironmentScan output file.
    schema_hints:
        Optional field-name overrides.  Keys: steeps_field, psst_field, summary_field,
        score_scale, date_field, source_field, entries_key.
        Merged on top of any embedded data["schema"] block.

    Returns
    -------
    list[UnifiedSignal]
        Successfully normalized entries.  Invalid entries are skipped with a WARNING log.
    """
    hints = _resolve_hints(data, schema_hints)

    steeps_field: str = hints["steeps_field"]
    psst_field: str = hints["psst_field"]
    summary_field: str = hints["summary_field"]
    score_scale: str = hints.get("score_scale", "0-100")
    date_field: str = hints.get("date_field", "date")
    source_field: str = hints.get("source_field", "source")

    # Format detection: wf_actual (raw array, wrapped by load_envscan_file)
    is_wf_actual = data.get("__format__") == _FORMAT_WF_ACTUAL
    if is_wf_actual and schema_hints is None:
        hints = _resolve_hints(data, ENVSCAN_WF_ACTUAL_HINTS)
        steeps_field  = hints["steeps_field"]
        psst_field    = hints["psst_field"]
        summary_field = hints["summary_field"]
        score_scale   = hints.get("score_scale", "0-100")
        date_field    = hints.get("date_field", "published_date")
        source_field  = hints.get("source_field", "source.name")

    # Auto-detect entries key: prefer explicit hint, then "entries", then "signals"
    entries_key: str = hints.get("entries_key", "")
    if not entries_key:
        entries_key = "entries" if "entries" in data else "signals"
    entries: list[dict] = data.get(entries_key, [])

    # WF4 auto-detection: if "signals" key and no embedded schema, apply WF4 hints
    is_wf4 = (
        entries_key == "signals"
        and "schema" not in data
        and schema_hints is None
        and not is_wf_actual   # don't override wf_actual detection
    )
    if is_wf4:
        hints = _resolve_hints(data, WF4_SCHEMA_HINTS)
        steeps_field = hints["steeps_field"]
        psst_field = hints["psst_field"]
        summary_field = hints["summary_field"]
        score_scale = hints.get("score_scale", "0-5")
        date_field = hints.get("date_field", "collected_at")
        source_field = hints.get("source_field", "source.name")

    results: list[UnifiedSignal] = []

    for idx, entry in enumerate(entries):
        # ── Mandatory fields (support dotted path for nested access) ──────────
        steeps_value = _get_nested(entry, steeps_field) if "." in steeps_field else entry.get(steeps_field)
        summary_raw = _get_nested(entry, summary_field) if "." in summary_field else entry.get(summary_field)

        # psst: supports dotted path; "__none__" means no score field in this format
        if psst_field == "__none__":
            psst_raw = None
        elif "." in psst_field:
            psst_raw = _get_nested(entry, psst_field)
        else:
            psst_raw = entry.get(psst_field)

        if steeps_value is None:
            logger.warning("Entry[%d]: missing field '%s' — skipping", idx, steeps_field)
            continue
        if summary_raw is None:
            logger.warning("Entry[%d]: missing field '%s' — skipping", idx, summary_field)
            continue

        # psst_raw may be None when analysis block is absent
        # If psst_default is set in hints, use it; otherwise skip the entry
        if psst_raw is None:
            psst_default_str = hints.get("psst_default")
            if psst_default_str is not None:
                psst_score = float(psst_default_str)
                logger.debug("Entry[%d]: psst field '%s' absent — using default %.1f", idx, psst_field, psst_score)
            else:
                logger.warning("Entry[%d]: missing field '%s' — skipping", idx, psst_field)
                continue
        else:
            try:
                psst_score = _normalize_score(psst_raw, score_scale)
            except ValueError as exc:
                logger.warning("Entry[%d]: invalid psst score (%s) — skipping: %s", idx, psst_raw, exc)
                continue

        # ── STEEPs category alias mapping (E_Environmental → E_env) ──────────
        steeps_str = str(steeps_value)
        steeps_str = _STEEPS_ALIAS.get(steeps_str, steeps_str)

        # ── Truncate summary to 200 chars (content.abstract can be very long) ─
        summary_value = str(summary_raw)[:200]

        # ── Optional fields with sensible defaults ─────────────────────────────
        sector = str(entry.get("sector", "unknown"))
        confidence_raw = entry.get("confidence", 0.5)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.5

        # Date field: dotted path or direct
        if "." in date_field:
            date_raw = _get_nested(entry, date_field)
        else:
            date_raw = entry.get(date_field) or entry.get("date") or ""
        date_value = str(date_raw or "")[:10]  # keep YYYY-MM-DD prefix only

        # Source field: dotted path (e.g., "source.name") or direct string
        if "." in source_field:
            source_raw = _get_nested(entry, source_field)
        else:
            source_raw = entry.get(source_field)
        if isinstance(source_raw, dict):
            source_raw = source_raw.get("name", "envscan")
        source = str(source_raw or "envscan")

        signal = UnifiedSignal(
            steeps_category=steeps_str,
            psst_score=psst_score,
            summary=summary_value,
            sector=sector,
            confidence=confidence,
            date=date_value,
            source=source,
        )
        results.append(signal)

    logger.debug(
        "normalize_envscan: %d entries processed, %d valid signals produced",
        len(entries),
        len(results),
    )
    return results


def load_envscan_file(path: str) -> dict:
    """
    Read and parse a JSON file from *path*.

    Supports three top-level formats:
      dict with "entries" or "signals" key — fixture / WF4 database.json
      list (raw array)                     — actual WF*.json output (wrapped automatically)

    Returns a dict.
    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the file content is not valid JSON.
    """
    with open(path, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in file '{path}': {exc}") from exc

    # Actual EnvironmentScan WF*.json files are raw arrays — wrap them
    if isinstance(data, list):
        logger.debug(
            "load_envscan_file: raw array detected in '%s' (%d entries) — wrapping as wf_actual",
            path, len(data),
        )
        return {"__format__": _FORMAT_WF_ACTUAL, "signals": data}

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected JSON type in '{path}': {type(data).__name__}")

    logger.debug("load_envscan_file: loaded '%s'", path)
    return data
