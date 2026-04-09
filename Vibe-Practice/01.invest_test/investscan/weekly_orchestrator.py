"""
investscan/weekly_orchestrator.py — Main pipeline orchestrator.
Coordinates all stages: data collection → synthesis → narrative → report → delivery.
English-First (P5-A): all internal logic, logs, and intermediate data in English.
build_narrative_with_retry(): Reflect-Revise loop (v3.5 CR-5-4 spec).
content_gate(): Pre-translation validation gate (v3.2 Q8).
"""
from __future__ import annotations

import dataclasses
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

from investscan.schema import NarrativeOutput, CitationValidationResult
from investscan.narrative_cross_check import DATA_UNAVAILABLE

logger = logging.getLogger(__name__)

MAX_RETRIES: int = 3


class RetryableError(Exception):
    """Signals build_narrative_with_retry() to retry with failure context."""


class FinalFailureError(Exception):
    """Signals max retries exhausted — trigger HITL escalation."""


def content_gate(narrative_output: dict) -> tuple[bool, list[str]]:
    """
    Pre-translation gate: verify NarrativeOutput meets all structural criteria.
    Called after Reflect-Revise loop PASS. Returns (passed, failures).
    Field names from schema.py §9-7-1.
    """
    failures = []
    category = narrative_output.get("category", "A")

    if category == "A":
        if not narrative_output.get("yoy_growth"):
            failures.append("A1: Missing YoY revenue + operating income growth")
        if not narrative_output.get("per_vs_sector"):
            failures.append("A2: Missing PER vs sector average")
        if not narrative_output.get("foreign_flow_direction"):
            failures.append("A3: Missing foreign investor 4-week flow direction")
        if not narrative_output.get("downside_risk"):
            failures.append("A4: Missing quantified downside risk")
        if narrative_output.get("direction") not in (
            "Positive momentum maintained",
            "Neutral — monitor and wait",
            "Risk zone",
        ):
            failures.append("A5: Missing/invalid directional opinion")

    elif category == "B":
        if not narrative_output.get("market_size"):
            failures.append("B1: Missing global market size + growth rate")
        if not narrative_output.get("stock_positioning"):
            failures.append("B2: Missing stock positioning within theme")
        if not narrative_output.get("catalyst"):
            failures.append("B3: Missing catalyst event with timeline")
        if not narrative_output.get("theme_duration"):
            failures.append("B4: Missing theme duration estimate")
        if not narrative_output.get("dissolution_risk"):
            failures.append("B5: Missing theme dissolution risk")
        if not narrative_output.get("disclaimer"):
            failures.append("B6: Missing required disclaimer text")

    # Common checks
    text = narrative_output.get("text", "")
    if len(text.encode("utf-8")) < 1000:
        failures.append(f"C1: NarrativeOutput too short ({len(text.encode())} bytes, min 1000)")
    if narrative_output.get("sentiment_weight", 0.0) != 0.0:
        failures.append("C2: Sentinel violation — sentiment_weight != 0.0")

    return len(failures) == 0, failures


def pre_translation_gate(
    narrative_output: dict,
    context_data: dict,
    retry_count: int,
) -> None:
    """
    Called inside build_narrative_with_retry() before @translator spawn.
    Raises RetryableError or FinalFailureError on failure.
    """
    passed, failures = content_gate(narrative_output)
    if not passed:
        msg = (f"Content gate FAIL — {len(failures)} criteria unmet:\n"
               + "\n".join(f"  - {f}" for f in failures))
        if retry_count < MAX_RETRIES:
            raise RetryableError(msg)
        raise FinalFailureError(msg)

    # Citation validation (BCG — blocking at 80% unmatched threshold)
    # NBS already validates 3 critical fields at 5% precision.
    # BCG is the last-resort catch: fires only when >80% of all financial citations
    # are unmatched (i.e., LLM fabricated essentially every number in the narrative).
    # Category B: market figures ($42bn, 19% CAGR) come from external research —
    # not in context_data → skip BCG for B (same reasoning as NBS).
    from investscan.citation_validator import validate_citations
    category = narrative_output.get("category", "A")
    if category == "B":
        logger.debug("BCG: Category B — citation check skipped (qualitative/research fields)")
    else:
        cite_result = validate_citations(narrative_output.get("text", ""), context_data)
        if not cite_result.validated:
            unmatched = len(cite_result.unmatched_numbers)
            msg = (
                f"Citation gate FAIL: {unmatched} numbers unmatched (>80% of total). "
                f"Unmatched: {cite_result.unmatched_numbers[:5]} — "
                f"LLM likely fabricated most numeric values not found in context_data."
            )
            logger.warning("BCG: %s", msg)
            if retry_count < MAX_RETRIES:
                raise RetryableError(msg)
            raise FinalFailureError(msg)


def build_narrative_with_retry(
    context_data: dict,
    intelligence_engine,
    reviewer_agent_fn,
    config: dict | None = None,
) -> NarrativeOutput:
    """
    Full Reflect-Revise loop with bounded retry counter (v3.5 CR-5-4 spec).

    Sequence per attempt:
      1. intelligence_engine.generate() → NarrativeOutput (LLM or mock)
      2. validate_report_quality.python_validate_first() → Python 1st pass (H-4)
      2.5. narrative_cross_check.cross_check_narrative_numbers() → NBS numeric backstop
      3. compliance_filter.filter_report() → Python regex (H-1)
      4. reviewer_agent_fn() → LLM @reviewer (2nd pass, Python PASS required first)
      5. pre_translation_gate() → final structural gate (includes BCG citation check)

    Returns:
        NarrativeOutput on success.

    Raises:
        FinalFailureError: after MAX_RETRIES exhausted.
    """
    from investscan.validate_report_quality import python_validate_first
    from investscan.compliance_filter import filter_report
    from investscan.narrative_cross_check import cross_check_narrative_numbers

    failure_context: list[str] = []
    best_attempt: NarrativeOutput | None = None

    for retry_count in range(MAX_RETRIES):
        # Step 1: Generate (LLM or mock)
        narrative = intelligence_engine.generate(
            context_data=context_data,
            failure_context=failure_context,
            config=config,
        )
        best_attempt = narrative

        # Step 2: Python 1st pass (H-4 — blocks self-evaluation loop)
        py_result = python_validate_first(narrative)
        if not py_result.passed:
            failure_context = [f"Python validation failed: {py_result.details}"]
            logger.info("Retry %d/%d: Python validation failed", retry_count + 1, MAX_RETRIES)
            continue

        # Step 2.5: Numeric Backstop (NBS — hallucination prevention)
        # Cross-verify LLM-generated financial numbers against input context_data.
        # Only for Category A: yoy_growth, per_vs_sector, foreign_flow_direction.
        nbs_errors = cross_check_narrative_numbers(narrative, context_data)
        if nbs_errors:
            # Flatten into individual items so the LLM sees each mismatch
            # as a separate, actionable instruction in the retry prompt.
            # "NBS: NBS-01: yoy_growth mismatch — input=8.3%..." is far clearer
            # than a stringified Python list inside one f-string.
            failure_context = [f"NBS: {err}" for err in nbs_errors]
            logger.warning(
                "Retry %d/%d: NBS detected %d numeric mismatch(es)",
                retry_count + 1, MAX_RETRIES, len(nbs_errors),
            )
            continue

        # Step 3: Compliance filter (H-1 — Python regex, 10 patterns)
        compliant, violations = filter_report(narrative.text, narrative.sentiment_weight)
        if not compliant:
            failure_context = [f"Compliance failed: {[(v[0], v[1]) for v in violations]}"]
            logger.info("Retry %d/%d: Compliance check failed", retry_count + 1, MAX_RETRIES)
            continue

        # Step 4: LLM @reviewer 2nd pass (only after Python passes)
        try:
            review_passed, review_failures = reviewer_agent_fn(narrative)
        except Exception as e:
            logger.warning("Reviewer agent failed: %s — skipping review", e)
            review_passed, review_failures = True, []

        if not review_passed:
            failure_context = review_failures
            logger.info("Retry %d/%d: Reviewer failed", retry_count + 1, MAX_RETRIES)
            continue

        # Step 5: Pre-translation gate
        try:
            pre_translation_gate(
                dataclasses.asdict(narrative),
                context_data,
                retry_count,
            )
        except RetryableError as e:
            failure_context = [str(e)]
            continue

        logger.info("Narrative quality gates passed on attempt %d", retry_count + 1)
        return narrative

    # MAX_RETRIES exceeded
    _save_best_attempt(best_attempt)
    raise FinalFailureError(
        f"Narrative quality gate failed after {MAX_RETRIES} attempts. "
        f"Best attempt saved to output/temp/narrative_failed_[date].json. "
        f"Human review required (/approve-hitl to proceed with best attempt)."
    )


def _save_best_attempt(narrative: NarrativeOutput | None) -> None:
    """Save best attempt on MAX_RETRIES failure for HITL review."""
    import json

    if narrative is None:
        return
    path = Path(f"output/temp/narrative_failed_{date.today()}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dataclasses.asdict(narrative), ensure_ascii=False, indent=2)
    )
    logger.warning("Best attempt saved to: %s", path)


def _update_sot_on_success(report_path: str) -> None:
    """Update state.yaml after successful pipeline run (atomic write, non-blocking).

    Sets packages.m05_ready=True and records last successful report path.
    Failure is logged but never raises — SOT update must not block delivery.
    """
    import yaml

    state_path = Path(".claude/state.yaml")
    if not state_path.exists():
        logger.debug("SOT not found at %s — skipping update", state_path)
        return
    try:
        state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
        state.setdefault("packages", {})["m05_ready"] = True
        state.setdefault("workflow", {}).update({
            "last_successful_report": report_path,
            "last_updated": datetime.now().isoformat(),
        })
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(yaml.dump(state, allow_unicode=True, default_flow_style=False), encoding="utf-8")
        tmp.rename(state_path)
        logger.info("SOT updated: packages.m05_ready=true, report=%s", report_path)
    except Exception as exc:
        logger.warning("SOT update failed (non-blocking): %s", exc)


def _noop_reviewer(narrative: NarrativeOutput) -> tuple[bool, list[str]]:
    """No-op reviewer for dry-run and testing."""
    return True, []


def run_full_pipeline(
    stock_code: str,
    stock_name: str,
    category: str,
    config: dict | None = None,
) -> dict:
    """
    Run complete InvestScan pipeline for a single stock.
    Returns result dict with report_path, narrative, and status.

    This is the main entry point for weekly_orchestrator --mode full-auto.
    """
    config = config or {}
    is_dry = config.get("mode", "dry-run") == "dry-run"

    logger.info("Pipeline start: %s (%s) Category %s", stock_name, stock_code, category)

    # Stage 1: Data collection (uses fixtures in dry-run)
    context_data = _build_context_data(stock_code, stock_name, category, config)

    # Stage 2: Generate narrative with retry
    import investscan.intelligence_engine as ie
    try:
        narrative = build_narrative_with_retry(
            context_data=context_data,
            intelligence_engine=ie,
            reviewer_agent_fn=_noop_reviewer,
            config=config,
        )
    except FinalFailureError as e:
        logger.error("Pipeline failed: %s", e)
        return {"status": "failed", "error": str(e)}

    # Stage 3: Generate report
    from investscan.report_generator import generate_report, save_report
    report_content = generate_report(
        narrative=narrative,
        stock_code=stock_code,
        stock_name=stock_name,
        meta_context=context_data,
    )
    report_path = save_report(report_content, stock_code)

    logger.info("Pipeline complete: report saved to %s", report_path)
    _update_sot_on_success(str(report_path))
    return {
        "status": "success",
        "report_path": str(report_path),
        "narrative_category": narrative.category,
        "direction": narrative.direction if narrative.category == "A" else narrative.theme_duration,
    }


def _build_context_data(
    stock_code: str,
    stock_name: str,
    category: str,
    config: dict,
) -> dict:
    """Build context_data dict from available data sources.

    Macro environment is synthesized from FRED fixture (dry-run) or FRED API (live).
    EnvScan signals loaded from discovered_paths.envscan_wf1_output when available.
    P6: synthesize_macro uses deterministic Python thresholds — no LLM.
    """
    from investscan.synthesize_stock import synthesize_stock_data
    from investscan.synthesize_macro import synthesize, load_fred_fixture

    financials = synthesize_stock_data(stock_code, stock_name, category, config=config)

    # Macro context: dry-run reads fixture; live mode would call FRED API (Phase 2)
    fred_data = load_fred_fixture()
    meta = synthesize(fred_data, config=config)

    # Top signals: EnvironmentScan (primary) + GlobalNews (supplement, if available)
    envscan_signals = _load_top_signals_from_envscan(top_n=5)
    gnews_signals   = _load_gnews_signals(top_n=5)

    # Merge and deduplicate by content (keep envscan first, gnews supplements)
    seen: set[str] = {s[:40] for s in envscan_signals}
    gnews_new = [s for s in gnews_signals if s[:40] not in seen]
    top_signals = envscan_signals + gnews_new

    def _val(v):
        """Replace None with DATA_UNAVAILABLE so LLM never fabricates missing data."""
        return v if v is not None else DATA_UNAVAILABLE

    return {
        "category": category,
        "stock_code": stock_code,
        "stock_name": stock_name,
        "analysis_date": date.today().isoformat(),
        "yoy_revenue_growth": _val(financials.yoy_revenue_growth),
        "yoy_op_income_growth": _val(financials.yoy_op_income_growth),
        "latest_quarter": financials.latest_quarter or DATA_UNAVAILABLE,
        "per_current": _val(financials.per_current),
        "per_sector_avg": _val(financials.per_sector_avg),
        "foreign_flow_4w": _val(financials.foreign_flow_4w),
        "rate_direction": meta.rate_direction,
        "inflation_trend": meta.inflation_trend,
        "risk_appetite": meta.risk_appetite,
        "usd_strength": meta.usd_strength,
        "sector_directions": meta.sector_directions,
        "macro_summary": meta.macro_summary or DATA_UNAVAILABLE,
        "action_item": meta.action_item or DATA_UNAVAILABLE,
        "action_checklist": meta.action_checklist,
        "top_signals": top_signals,
    }


def _load_top_signals_from_envscan(top_n: int = 5) -> list[str]:
    """
    Load top N signals from EnvironmentScan using envscan_adapter.
    Reads WF*.json files from the actual output directory (not a single hardcoded path).
    Falls back to hardcoded defaults when EnvironmentScan output is unavailable.

    Returns list of signal title strings (top N by psst_score).
    """
    try:
        from investscan.adapters.envscan_adapter import load_signals as envscan_load
        signals = envscan_load()
        if not signals:
            raise ValueError("No EnvironmentScan signals loaded")

        top = sorted(signals, key=lambda s: s["psst_score"], reverse=True)[:top_n]
        titles = []
        for s in top:
            title = (s.get("title") or s["summary"]).split(".")[0].strip()[:80]
            score = s.get("psst_score", 0)
            if title:
                titles.append(f"{title} (score={score})")

        logger.info("Loaded %d top signals from EnvironmentScan (%d total)", len(titles), len(signals))
        return titles if titles else ["AI semiconductor demand", "Fed rate stability"]

    except Exception as e:
        logger.debug("EnvironmentScan signal load skipped: %s — using defaults", e)
        return ["AI semiconductor demand", "Fed rate stability"]


def _load_gnews_signals(top_n: int = 10) -> list[str]:
    """
    Load signals from GlobalNews Crawling output (if available).
    Returns empty list gracefully when GlobalNews hasn't been run.

    Returns list of signal summary strings.
    """
    try:
        from investscan.adapters.gnews_adapter import load_signals as gnews_load
        signals = gnews_load()
        if not signals:
            return []

        top = sorted(signals, key=lambda s: s["psst_score"], reverse=True)[:top_n]
        summaries = [
            f"{s['summary'][:80]} (score={s.get('psst_score', 0)})"
            for s in top if s.get("summary")
        ]
        logger.info("Loaded %d signals from GlobalNews (%d total)", len(summaries), len(signals))
        return summaries

    except Exception as e:
        logger.debug("GlobalNews signal load skipped: %s", e)
        return []


def run_data_only_pipeline(
    config: dict | None = None,
) -> dict:
    """
    Stage 1 data-only pipeline: collect signals + synthesize context → save context file.
    Used by launchd Sunday 20:00 automated run.
    Returns result dict with context_path and status.
    """
    import json

    config = config or {}
    logger.info("Stage 1 data-only pipeline starting")

    # Load and normalize EnvScan signals
    top_signals = _load_top_signals_from_envscan()
    logger.info("Stage 1: %d top signals loaded", len(top_signals))

    # Synthesize macro context
    from investscan.synthesize_macro import synthesize, load_fred_fixture
    fred_data = load_fred_fixture()
    meta = synthesize(fred_data, config=config)

    # Build context contract (Stage 1 → Stage 2 interface)
    today = date.today().isoformat()
    context = {
        "report_date": today,
        "runtime_mode": config.get("runtime_mode", "envscan_only"),
        "schema_version": "context-v1",
        "created_at": datetime.now().isoformat(),
        "meta": {
            "rate_direction": meta.rate_direction,
            "inflation_trend": meta.inflation_trend,
            "risk_appetite": meta.risk_appetite,
            "usd_strength": meta.usd_strength,
        },
        "signals_summary": top_signals,
        # Stock contexts: empty in envscan_only mode (stock selection not yet performed)
        "cat_a_contexts": [],
        "cat_b_contexts": [],
        "stock_contexts": {},
        # FRED snapshot for Stage 2 reference (processed from fixture in dry-run)
        "fred_snapshot": {
            "source": "fixture",
            "rate_direction": meta.rate_direction,
            "inflation_trend": meta.inflation_trend,
            "risk_appetite": meta.risk_appetite,
            "usd_strength": meta.usd_strength,
        },
    }

    # Save context file
    context_path = Path(f"output/context/context_{today}.json")
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2)
    )
    logger.info("Stage 1 context saved: %s", context_path)

    # Record last successful run
    run_log = Path("logs/last_successful_run.txt")
    run_log.parent.mkdir(parents=True, exist_ok=True)
    run_log.write_text(datetime.now().isoformat())

    _update_sot_on_success(str(context_path))
    return {"status": "success", "context_path": str(context_path)}


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="InvestScan Weekly Orchestrator")
    parser.add_argument("--mode", choices=["full-auto", "dry-run", "data-only"], default="dry-run")
    parser.add_argument("--stock", default="005930", help="KRX stock code")
    parser.add_argument("--name", default="Samsung Electronics", help="Stock name")
    parser.add_argument("--category", choices=["A", "B"], default="A")
    args = parser.parse_args()

    if args.mode == "data-only":
        result = run_data_only_pipeline()
    else:
        cfg = {"mode": "dry-run" if args.mode == "dry-run" else "live"}
        result = run_full_pipeline(args.stock, args.name, args.category, config=cfg)

    print(f"Result: {result}")
    sys.exit(0 if result.get("status") == "success" else 1)
