"""
investscan/adapters/envscan_adapter.py

Bridge adapter for EnvironmentScan (standalone system).
Reads WF*.json output files WITHOUT modifying EnvironmentScan in any way.

EnvironmentScan output format (actual WF* files):
  - Top-level: JSON array  [{"id":..., "title":..., "preliminary_category":..., "summary":...}, ...]
  - Fields: id, title, url, source{name,type,tier}, published_date, preliminary_category, summary

Usage (standalone):
    python3 -m investscan.adapters.envscan_adapter
    python3 -m investscan.adapters.envscan_adapter --base-dir /path/to/EnvironmentScan/output
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from investscan.schema import UnifiedSignal

logger = logging.getLogger(__name__)

# Default EnvironmentScan output directory
DEFAULT_ENVSCAN_DIR = Path(
    "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
    "/EnvironmentScan-system-main-v4-main/output"
)

# WF file priority order: WF1(base) → WF1(expansion) → WF3(naver) → WF2(arxiv)
# WF3(Naver Korean news) is especially relevant for Korean equity analysis
_WF_PRIORITY = ["WF3", "WF1_base", "WF1_expansion", "WF1", "WF2"]

# EnvironmentScan actual field mapping (WF* format)
_ENVSCAN_FIELD_MAP = {
    "steeps_field":   "preliminary_category",
    "summary_field":  "summary",
    "date_field":     "published_date",
    "source_field":   "source.name",   # nested: source.name
    "url_field":      "url",
    "title_field":    "title",
    "score_scale":    "0-100",         # no score in WF* → default 50
}

# preliminary_category → STEEPS mapping
_CATEGORY_MAP: dict[str, str] = {
    "T_Technological":  "T",
    "T":                "T",
    "E_Environmental":  "E_env",
    "E_Economic":       "E",
    "E":                "E",
    "P_Political":      "P",
    "P":                "P",
    "S_Social":         "S",
    "S":                "S",
    "s_Security":       "s",
    "s":                "s",
}

# STEEPS → investment sector routing
_STEEPS_SECTOR_MAP: dict[str, str] = {
    "T":     "technology",
    "E":     "financials",
    "E_env": "energy",
    "P":     "financials",
    "S":     "consumer",
    "s":     "technology",
}


def find_latest_files(base_dir: Path = DEFAULT_ENVSCAN_DIR) -> list[Path]:
    """
    Find all WF*.json files in base_dir, sorted by priority then date (newest first).
    Returns empty list if directory doesn't exist or has no matching files.
    """
    if not base_dir.exists():
        logger.warning("EnvironmentScan output directory not found: %s", base_dir)
        return []

    files = list(base_dir.glob("WF*.json"))
    if not files:
        logger.warning("No WF*.json files found in %s", base_dir)
        return []

    # Sort: newest date first, then by WF priority
    def _sort_key(p: Path) -> tuple[str, int]:
        # Extract date from filename e.g. WF1_base_signals_20260325.json
        m = re.search(r"(\d{8})", p.stem)
        date_str = m.group(1) if m else "00000000"
        # Priority by WF prefix
        name = p.stem
        for i, prefix in enumerate(_WF_PRIORITY):
            if prefix.lower() in name.lower():
                return (date_str, -i)
        return (date_str, -99)

    return sorted(files, key=_sort_key, reverse=True)


def _get_nested(entry: dict, dotted: str) -> str | None:
    """Extract nested field using dot notation."""
    parts = dotted.split(".")
    val = entry
    for part in parts:
        if not isinstance(val, dict):
            return None
        val = val.get(part)
        if val is None:
            return None
    return str(val) if val is not None else None


def _map_steeps(raw: str | None) -> str:
    """Map preliminary_category string to normalized STEEPS single char."""
    if not raw:
        return "T"
    # Try exact match first
    mapped = _CATEGORY_MAP.get(raw)
    if mapped:
        return mapped
    # Prefix match
    raw_upper = raw.upper()
    for key, val in _CATEGORY_MAP.items():
        if raw_upper.startswith(key.upper()):
            return val
    return "T"  # default: Technological


def load_signals(
    base_dir: Path = DEFAULT_ENVSCAN_DIR,
    max_per_file: int = 50,
    wf_filter: list[str] | None = None,
) -> list[dict]:
    """
    Load and merge signals from all WF*.json files.

    Args:
        base_dir: EnvironmentScan output directory.
        max_per_file: Max signals to load per file (avoid context overload).
        wf_filter: Optional list of WF prefixes to include e.g. ["WF1", "WF3"].
                   None = load all.

    Returns:
        List of normalized signal dicts with keys:
        steeps_category, psst_score, summary, sector, confidence, date, source, url, title
    """
    files = find_latest_files(base_dir)
    if not files:
        return []

    seen_urls: set[str] = set()
    all_signals: list[dict] = []
    loaded_files: list[str] = []

    for path in files:
        # Apply WF filter
        if wf_filter:
            if not any(f.lower() in path.stem.lower() for f in wf_filter):
                continue

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to load %s: %s", path.name, e)
            continue

        # EnvironmentScan outputs are raw JSON arrays
        entries: list[dict] = raw if isinstance(raw, list) else raw.get("signals", raw.get("entries", []))
        count = 0

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if count >= max_per_file:
                break

            url = entry.get("url", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            steeps_raw = entry.get("preliminary_category")
            summary = entry.get("summary") or entry.get("title", "")
            if not summary:
                continue

            steeps = _map_steeps(steeps_raw)
            source_raw = entry.get("source")
            source = (
                source_raw.get("name", "envscan") if isinstance(source_raw, dict)
                else str(source_raw or "envscan")
            )
            date_raw = entry.get("published_date", "")
            date_str = date_raw[:10] if date_raw else datetime.now().date().isoformat()

            all_signals.append({
                "steeps_category": steeps,
                "psst_score":      50.0,   # WF* files have no priority score
                "summary":         summary[:200],
                "sector":          _STEEPS_SECTOR_MAP.get(steeps, "technology"),
                "confidence":      0.6,
                "date":            date_str,
                "source":          source,
                "url":             url,
                "title":           entry.get("title", ""),
            })
            count += 1

        if count:
            loaded_files.append(f"{path.name}({count}건)")

    if loaded_files:
        logger.info("EnvironmentScan signals loaded: %s", ", ".join(loaded_files))
    else:
        logger.warning("No signals loaded from EnvironmentScan output.")

    return all_signals


def to_unified_signals(signals: list[dict]) -> list:
    """Convert raw signal dicts to UnifiedSignal objects."""
    from investscan.schema import UnifiedSignal
    result = []
    for s in signals:
        try:
            result.append(UnifiedSignal(
                steeps_category=s["steeps_category"],
                psst_score=s["psst_score"],
                summary=s["summary"],
                sector=s["sector"],
                confidence=s["confidence"],
                date=s["date"],
                source=s["source"],
            ))
        except Exception as e:
            logger.debug("UnifiedSignal conversion failed: %s", e)
    return result


def get_top_topics(
    base_dir: Path = DEFAULT_ENVSCAN_DIR,
    top_n: int = 10,
) -> dict[str, list[str]]:
    """
    Extract top topics per STEEPS category from EnvironmentScan output.
    Used as input topic guidance for GlobalNews crawling.

    Returns:
        {"T": ["topic1", "topic2", ...], "E": [...], ...}
    """
    signals = load_signals(base_dir, max_per_file=100)
    topics: dict[str, list[str]] = {}

    for sig in signals:
        cat = sig["steeps_category"]
        title = sig.get("title") or sig["summary"][:80]
        if cat not in topics:
            topics[cat] = []
        if len(topics[cat]) < top_n:
            topics[cat].append(title)

    return topics


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="EnvironmentScan → InvestScan 어댑터")
    parser.add_argument("--base-dir", default=str(DEFAULT_ENVSCAN_DIR))
    parser.add_argument("--wf-filter", nargs="*", help="WF 필터 예: WF1 WF3")
    parser.add_argument("--top-topics", action="store_true", help="STEEPS별 상위 토픽 출력")
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    files = find_latest_files(base_dir)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EnvironmentScan 어댑터 — {base_dir.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    if not files:
        print("  ⚠  WF*.json 파일 없음")
        return 1

    print(f"  발견된 파일 ({len(files)}개):")
    for f in files:
        size = f.stat().st_size
        print(f"    {f.name}  ({size:,} bytes)")

    signals = load_signals(base_dir, wf_filter=args.wf_filter)
    print(f"\n  로드된 신호: {len(signals)}건")

    # STEEPS 분포
    steeps_count: dict[str, int] = {}
    for s in signals:
        cat = s["steeps_category"]
        steeps_count[cat] = steeps_count.get(cat, 0) + 1
    print("\n  STEEPS 분포:")
    for cat, cnt in sorted(steeps_count.items()):
        sector = _STEEPS_SECTOR_MAP.get(cat, "?")
        print(f"    {cat:8s} → {sector:15s}  {cnt}건")

    if args.top_topics:
        topics = get_top_topics(base_dir)
        print("\n  STEEPS별 상위 토픽 (GlobalNews 크롤링 참고용):")
        for cat, titles in topics.items():
            print(f"\n  [{cat}]")
            for t in titles[:5]:
                print(f"    · {t[:80]}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
