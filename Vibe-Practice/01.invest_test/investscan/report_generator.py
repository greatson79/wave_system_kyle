"""
investscan/report_generator.py — Generate weekly investment report from NarrativeOutput.
English template (P5-A). Uses Jinja2 with templates/weekly-report.md.j2.
Output: output/reports/weekly-report-{date}.md (English original).
Korean translation: handled by @translator SubAgent.
"""
from __future__ import annotations

import dataclasses
import logging
from datetime import date
from pathlib import Path

from investscan.schema import NarrativeOutput

logger = logging.getLogger(__name__)

TEMPLATE_PATH: str = "templates/weekly-report.md.j2"
OUTPUT_DIR: str = "output/reports"


def generate_report(
    narrative: NarrativeOutput,
    stock_code: str,
    stock_name: str,
    meta_context: dict | None = None,
    portfolio_context: dict | None = None,
    bear_case: str = "",
    onboarding_mode: bool = True,
    version: str = "1.0.0",
) -> str:
    """
    Generate English weekly report from NarrativeOutput using Jinja2 template.

    Args:
        narrative: NarrativeOutput from intelligence_engine (English)
        stock_code: KRX stock code
        stock_name: Stock display name
        meta_context: InvestmentMeta fields as dict (macro environment)
        portfolio_context: Portfolio holdings for comparison (v3.6 I-11)
        bear_case: Bear Case text (positioned at bottom — v3.6 I-12)
        onboarding_mode: If True, adds Bear Case explanation prefix (v3.6 I-12)
        version: InvestScan version string

    Returns:
        Rendered Markdown string (English).
    """
    today = date.today().isoformat()
    week_label = _get_week_label()

    # Build template context
    context = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "category": narrative.category,
        "week_label": week_label,
        "narrative": dataclasses.asdict(narrative),
        "meta": meta_context or _default_meta(),
        "portfolio_context": portfolio_context,
        "bear_case": bear_case,
        "onboarding_mode": onboarding_mode,
        "version": version,
        "generated_at": today,
    }

    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(
            loader=FileSystemLoader("."),
            autoescape=False,
        )
        template = env.get_template(TEMPLATE_PATH)
        rendered = template.render(**context)
        return rendered
    except ImportError:
        logger.warning("jinja2 not installed — using simple string template")
        return _simple_render(context)


def save_report(
    content: str,
    stock_code: str,
    report_date: str | None = None,
) -> Path:
    """
    Save report to output/reports/weekly-report-{date}.md (atomic write).

    Returns:
        Path to saved report file.
    """
    report_date = report_date or date.today().isoformat()
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"weekly-report-{report_date}.md"
    filepath = output_dir / filename

    # Atomic write: tmp → rename
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(filepath)

    logger.info("Report saved: %s", filepath)
    return filepath


def _get_week_label() -> str:
    """Return ISO week label like '2026-W13'."""
    today = date.today()
    iso = today.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _default_meta() -> dict:
    """Default macro meta for dry-run/missing context."""
    return {
        "rate_direction": "hold",
        "inflation_trend": "cooling",
        "risk_appetite": "moderate",
        "usd_strength": "strong",
    }


def _simple_render(context: dict) -> str:
    """
    Fallback template renderer (no Jinja2).
    Used when jinja2 is not installed.
    """
    narrative = context["narrative"]
    lines = [
        f"# Weekly Investment Signal Report",
        f"**{context['stock_name']} ({context['stock_code']})** | "
        f"Week: {context['week_label']} | Category: {context['category']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        narrative.get("text", ""),
        "",
        "---",
        "",
    ]

    if context["category"] == "A":
        lines += [
            "## Financial Snapshot",
            "",
            f"- **YoY Growth**: {narrative.get('yoy_growth', 'N/A')}",
            f"- **Valuation**: {narrative.get('per_vs_sector', 'N/A')}",
            f"- **Foreign Flow**: {narrative.get('foreign_flow_direction', 'N/A')}",
            f"- **Downside Risk**: {narrative.get('downside_risk', 'N/A')}",
            "",
            "## Signal Direction",
            "",
            f"> **{narrative.get('direction', 'N/A')}**",
            "",
        ]
    elif context["category"] == "B":
        lines += [
            "## Theme Analysis",
            "",
            f"- **Market Size**: {narrative.get('market_size', 'N/A')}",
            f"- **Positioning**: {narrative.get('stock_positioning', 'N/A')}",
            f"- **Catalyst**: {narrative.get('catalyst', 'N/A')}",
            f"- **Theme Duration**: {narrative.get('theme_duration', 'N/A')}",
            f"- **Dissolution Risk**: {narrative.get('dissolution_risk', 'N/A')}",
            "",
        ]

    if context.get("bear_case"):
        lines += [
            "## ⚠️ Scenarios Where This Signal Could Be Wrong (Reference Only)",
            "",
            context["bear_case"],
            "",
        ]

    disclaimer = narrative.get("disclaimer") or (
        "This analysis is based on publicly available information and does not "
        "constitute investment advice. Investment decisions are solely the reader's responsibility."
    )
    lines += [
        "---",
        "",
        f"*{disclaimer}*",
        "",
        f"*Generated by InvestScan v{context['version']} | {context['generated_at']}*",
    ]

    return "\n".join(lines)
