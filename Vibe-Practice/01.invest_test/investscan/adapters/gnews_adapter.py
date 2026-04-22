"""
investscan/adapters/gnews_adapter.py

Bridge adapter for GlobalNews Crawling (standalone system).
Reads data/output/{date}/signals.parquet WITHOUT modifying GlobalNews in any way.

GlobalNews output format (signals.parquet columns):
  - Standard: id, title, url, published_date, source, category, summary, signal_layer, confidence, ...

Graceful degradation: returns empty list if GlobalNews hasn't been run or Parquet is absent.

Usage (standalone):
    python3 -m investscan.adapters.gnews_adapter
    python3 -m investscan.adapters.gnews_adapter --base-dir /path/to/GlobalNews/data/output
"""
from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_GNEWS_DIR = Path(
    "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
    "/GlobalNews-Crawling-AgenticWorkflow/data/output"
)

# GlobalNews signal_layer → investment relevance score (0-100)
_LAYER_SCORE: dict[str, float] = {
    "Singularity":  95.0,
    "Long-term":    80.0,
    "Mid-term":     65.0,
    "Short-term":   45.0,
    "Fad":          20.0,
}

# Keyword → STEEPS category (for GlobalNews articles without category field)
_KEYWORD_STEEPS: list[tuple[str, str]] = [
    ("semiconductor", "T"), ("AI", "T"), ("chip", "T"), ("robot", "T"),
    ("interest rate", "E"), ("inflation", "E"), ("GDP", "E"), ("fed", "E"),
    ("climate", "E_env"), ("energy", "E_env"), ("solar", "E_env"),
    ("regulation", "P"), ("sanction", "P"), ("election", "P"),
    ("labor", "S"), ("consumer", "S"), ("demographic", "S"),
    ("cyber", "s"), ("security", "s"), ("hack", "s"),
]

_STEEPS_SECTOR_MAP: dict[str, str] = {
    "T":     "technology",
    "E":     "financials",
    "E_env": "energy",
    "P":     "financials",
    "S":     "consumer",
    "s":     "technology",
}


import re


def find_latest_dir(base_dir: Path = DEFAULT_GNEWS_DIR) -> Path | None:
    """Find the most recent date subdirectory in GlobalNews output (legacy).

    GlobalNews stores signals directly in base_dir (no date subdirectory),
    so this returns base_dir itself if it exists and contains Parquet files.
    Falls back to scanning date subdirectories for older GlobalNews layouts.
    """
    if not base_dir.exists():
        return None
    # Primary: flat layout — signals.parquet / analysis.parquet directly in base_dir
    if (base_dir / "signals.parquet").exists() or (base_dir / "analysis.parquet").exists():
        return base_dir
    # Fallback: legacy date-subdirectory layout
    date_dirs = sorted(
        (d for d in base_dir.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)),
        reverse=True,
    )
    return date_dirs[0] if date_dirs else None


def _infer_steeps(text: str) -> str:
    """Infer STEEPS category from article text using keyword matching."""
    text_lower = text.lower()
    for keyword, cat in _KEYWORD_STEEPS:
        if keyword.lower() in text_lower:
            return cat
    return "T"


def _load_from_analysis_join(
    latest_dir: Path,
    base_dir: Path,
    max_signals: int,
) -> list[dict]:
    """
    Fallback: derive signals by joining analysis.parquet + articles.parquet.
    Used when signals.parquet exists but is empty (Stage 7 produced no signals).

    analysis.parquet  → steeps_category, importance_score, sentiment_label, keywords
    articles.parquet  → url, title, body, source, published_at
    Join key: article_id
    """
    import pandas as pd

    analysis_path = latest_dir / "analysis.parquet"
    if not analysis_path.exists():
        return []

    # articles.parquet lives in data/processed/{date}/
    date_name = latest_dir.name if latest_dir != base_dir else ""
    processed_dir = base_dir.parent / "processed"
    articles_path = (processed_dir / date_name / "articles.parquet"
                     if date_name else processed_dir / "articles.parquet")

    try:
        analysis_df = pd.read_parquet(analysis_path)
        if len(analysis_df) == 0:
            return []
    except Exception as e:
        logger.warning("Failed to read analysis.parquet: %s", e)
        return []

    # Merge with articles if available
    try:
        articles_df = pd.read_parquet(articles_path)[
            ["article_id", "url", "title", "body", "source", "published_at"]
        ]
        df = analysis_df.merge(articles_df, on="article_id", how="left")
    except Exception:
        df = analysis_df
        df["url"]          = ""
        df["title"]        = df.get("article_id", "")
        df["body"]         = ""
        df["source"]       = "gnews"
        df["published_at"] = ""

    results: list[dict] = []
    seen_urls: set[str] = set()

    for _, row in df.head(max_signals).iterrows():
        url = str(row.get("url", ""))
        if url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        title   = str(row.get("title", ""))
        body    = str(row.get("body", "") or "")
        summary = body[:200] if body else title

        steeps = str(row.get("steeps_category", "") or "").strip()
        if not steeps:
            steeps = _infer_steeps(title + " " + summary)

        importance = float(row.get("importance_score", 50) or 50)
        psst_score = min(importance, 100.0)

        sentiment = str(row.get("sentiment_label", "neutral") or "neutral")
        confidence = 0.7 if sentiment != "neutral" else 0.5

        date_raw = row.get("published_at", "")
        try:
            date_str = str(date_raw)[:10]
        except Exception:
            date_str = datetime.now().date().isoformat()

        source = str(row.get("source", "gnews") or "gnews")

        results.append({
            "steeps_category": steeps,
            "psst_score":      psst_score,
            "summary":         summary,
            "sector":          _STEEPS_SECTOR_MAP.get(steeps, "technology"),
            "confidence":      confidence,
            "date":            date_str,
            "source":          source,
            "url":             url,
            "title":           title,
        })

    logger.info(
        "GlobalNews analysis-join fallback: %d signals from %s",
        len(results), latest_dir.name if latest_dir != base_dir else base_dir.name,
    )
    return results


def load_signals(
    base_dir: Path = DEFAULT_GNEWS_DIR,
    max_signals: int = 100,
) -> list[dict]:
    """
    Load signals from GlobalNews Parquet output.
    Returns empty list (graceful) if no Parquet files found.

    Priority:
      1. signals.parquet (non-empty) — Stage 7 output
      2. analysis.parquet + articles.parquet join — Stage 7 empty fallback
      3. Empty list (graceful degradation)

    Args:
        base_dir: GlobalNews data/output directory.
        max_signals: Maximum signals to return.

    Returns:
        List of normalized signal dicts (same schema as envscan_adapter.load_signals).
    """
    latest_dir = find_latest_dir(base_dir)
    if latest_dir is None:
        logger.info("GlobalNews output directory not found or empty — skipping")
        return []

    signals_parquet = latest_dir / "signals.parquet"
    analysis_parquet = latest_dir / "analysis.parquet"

    # Prefer signals.parquet; fall back to analysis.parquet
    parquet_path = signals_parquet if signals_parquet.exists() else (
        analysis_parquet if analysis_parquet.exists() else None
    )

    if parquet_path is None:
        logger.info("No Parquet files in %s — GlobalNews not yet run", latest_dir)
        return []

    try:
        import pandas as pd
    except ImportError:
        logger.warning("pandas not installed — cannot read GlobalNews Parquet")
        return []

    try:
        df = pd.read_parquet(parquet_path)
    except Exception as e:
        logger.warning("Failed to read %s: %s", parquet_path, e)
        return []

    # signals.parquet is empty (Stage 7 produced no signals) → analysis join fallback
    if len(df) == 0 and parquet_path == signals_parquet:
        logger.info("signals.parquet is empty — trying analysis.parquet join fallback")
        return _load_from_analysis_join(latest_dir, base_dir, max_signals)

    results: list[dict] = []
    seen_urls: set[str] = set()

    for _, row in df.head(max_signals).iterrows():
        url = str(row.get("url", ""))
        if url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        title   = str(row.get("title", ""))
        summary = str(row.get("summary", "") or row.get("content", "") or title)
        if not summary:
            continue

        # Infer STEEPS
        category_raw = str(row.get("category", "") or row.get("steeps_category", ""))
        if category_raw:
            steeps = category_raw[0].upper() if category_raw else "T"
        else:
            steeps = _infer_steeps(title + " " + summary[:200])

        # Score from signal_layer
        layer = str(row.get("signal_layer", "") or row.get("layer", ""))
        score = _LAYER_SCORE.get(layer, 50.0)

        # Confidence
        conf_raw = row.get("confidence", row.get("relevance_score", 0.6))
        try:
            confidence = float(conf_raw)
            if confidence > 1.0:
                confidence /= 100.0
        except (TypeError, ValueError):
            confidence = 0.6

        # Date
        date_raw = row.get("published_date", row.get("collected_at", ""))
        try:
            date_str = str(date_raw)[:10]
        except Exception:
            date_str = datetime.now().date().isoformat()

        source = str(row.get("source", "") or row.get("publisher", "gnews"))

        results.append({
            "steeps_category": steeps,
            "psst_score":      score,
            "summary":         summary[:200],
            "sector":          _STEEPS_SECTOR_MAP.get(steeps, "technology"),
            "confidence":      confidence,
            "date":            date_str,
            "source":          source,
            "url":             url,
            "title":           title,
        })

    logger.info(
        "GlobalNews signals loaded: %d from %s (%s)",
        len(results), parquet_path.name, latest_dir.name,
    )
    return results


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


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="GlobalNews → InvestScan 어댑터")
    parser.add_argument("--base-dir", default=str(DEFAULT_GNEWS_DIR))
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    latest = find_latest_dir(base_dir)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GlobalNews 어댑터 — {base_dir.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    if latest is None:
        print("  ⚠  GlobalNews 출력 디렉터리 없음 또는 Parquet 파일 없음")
        print("  → GlobalNews를 먼저 실행하세요: python3 main.py --mode full")
        print(f"  → 기대 경로: {base_dir / 'signals.parquet'}")
        return 0  # graceful — not an error

    label = "base_dir (flat layout)" if latest == base_dir else latest.name
    print(f"  Parquet 위치: {label}")
    for f in sorted(latest.iterdir()):
        if f.suffix in (".parquet", ".json"):
            print(f"    {f.name}  ({f.stat().st_size:,} bytes)")

    signals = load_signals(base_dir)
    if not signals:
        print("\n  ⚠  Parquet 파일 없음 — GlobalNews 아직 미실행")
        print("  → GlobalNews를 실행하면 자동으로 연동됩니다")
        return 0

    print(f"\n  로드된 신호: {len(signals)}건")
    steeps_count: dict[str, int] = {}
    for s in signals:
        cat = s["steeps_category"]
        steeps_count[cat] = steeps_count.get(cat, 0) + 1

    print("\n  STEEPS 분포:")
    for cat, cnt in sorted(steeps_count.items()):
        sector = _STEEPS_SECTOR_MAP.get(cat, "?")
        print(f"    {cat:8s} → {sector:15s}  {cnt}건")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
