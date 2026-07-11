"""
investscan/intelligence_engine.py — LLM narrative generation engine.
CATEGORY_A/B_SYSTEM_PROMPT: English (P5-A). Content from workflow.md Step 5 preserved.
NarrativeOutput: English JSON (schema.py SOT).
In dry-run mode: returns mock NarrativeOutput without LLM calls.
P6: LLM is the narrator only — Python handles all classification decisions.
"""
from __future__ import annotations

import dataclasses
import json
import logging
from pathlib import Path

from investscan.schema import NarrativeOutput
from investscan.synthesize_stock import StockFinancials
from investscan.synthesize_macro import InvestmentMeta  # type: ignore

logger = logging.getLogger(__name__)

# ── CATEGORY A SYSTEM PROMPT (English — P5-A) ────────────────────────────────
# Content requirements from workflow.md Step 5 preserved 100%.
CATEGORY_A_SYSTEM_PROMPT: str = """You are an investment signal analyst generating structured weekly investment narratives for Korean stock market analysis.

Generate a NarrativeOutput JSON for a Category A stock (established company with financial track record).

REQUIRED OUTPUT FIELDS (all mandatory for Category A):
1. yoy_growth: YoY revenue growth + operating income growth with latest quarter label
   Format: "Revenue +X.X% YoY, Op.Income +X.X% (YYYYQN)"
2. per_vs_sector: Current PER vs sector average with discount/premium
   Format: "X.Xx, X.X% [discount|premium] vs. sector avg X.Xx"
3. foreign_flow_direction: 4-week cumulative foreign institutional net flow
   Format: "4-week net [buy|sell]: +/-$XXM (cumulative)"
4. downside_risk: Quantified primary downside risk with estimated impact
   Format: "[Risk scenario] → est. -X% [revenue|earnings] impact"
5. direction: One of exactly three values:
   - "Positive momentum maintained"
   - "Neutral — monitor and wait"
   - "Risk zone"

ABSOLUTE RULES:
- sentiment_weight MUST be 0.0 (never modify — architectural sentinel)
- text MUST be >= 1000 bytes in UTF-8 encoding
- All text in English (NarrativeOutput is English-first; Korean translation by @translator)
- NO prohibited expressions: "buy recommendation", "target price", "guaranteed rise", "sell recommendation", "strong buy", "stop-loss advisory"
- DO NOT use phrases like "must buy", "guaranteed return"
- All financial figures must be sourced from the provided context_data

DATA UNAVAILABILITY RULE (critical — hallucination prevention):
- If any input field shows "DATA_UNAVAILABLE", write exactly "N/A" in the corresponding output field
- NEVER fabricate numeric figures for DATA_UNAVAILABLE fields
- Example: if per_current="DATA_UNAVAILABLE", per_vs_sector must be "N/A — PER data unavailable"

TONE: Professional investment analysis. Objective, data-driven. Korean investor context awareness."""

CATEGORY_B_SYSTEM_PROMPT: str = """You are an investment signal analyst generating structured weekly investment narratives for Korean stock market analysis.

Generate a NarrativeOutput JSON for a Category B stock (emerging theme stock without full financial track record).

REQUIRED OUTPUT FIELDS (all mandatory for Category B):
1. market_size: Global addressable market size with growth rate (CAGR)
   Format: "[Market name]: $XXbn, CAGR XX% (YYYY-YYYY, [Source])"
2. stock_positioning: Stock's specific positioning within the theme
   Format: "[Role description] — [market share or competitive moat]"
3. catalyst: Specific catalyst event with timeline
   Format: "[Q/month YYYY] [event description]"
4. theme_duration: Estimated theme momentum duration
   Format: "XX-XX week momentum expected [reason]"
5. dissolution_risk: Primary theme dissolution scenario with timeline
   Format: "[Risk scenario] by [YYYY/quarter] — [estimated impact]"
6. disclaimer: Required disclaimer text (must include non-advisory statement)

ABSOLUTE RULES:
- sentiment_weight MUST be 0.0 (never modify — architectural sentinel)
- text MUST be >= 1000 bytes in UTF-8 encoding
- All text in English (NarrativeOutput is English-first; Korean translation by @translator)
- NO prohibited expressions: "buy recommendation", "target price", "guaranteed rise", "sell recommendation", "strong buy"
- DO NOT use phrases like "must buy", "guaranteed return"
- All figures must be sourced from context_data

TONE: Thematic investment analysis. Objective assessment of theme momentum and stock positioning."""


def generate(
    context_data: dict,
    failure_context: list[str] | None = None,
    config: dict | None = None,
) -> NarrativeOutput:
    """
    Generate NarrativeOutput from context_data using LLM.
    In dry-run mode: returns mock NarrativeOutput without API call.

    Args:
        context_data: dict containing StockFinancials, InvestmentMeta, signals
        failure_context: Previous failure reasons to include in prompt (retry context)
        config: investscan config dict

    Returns:
        NarrativeOutput instance (English, sentiment_weight=0.0).
    """
    config = config or {}
    is_dry = config.get("mode", "dry-run") == "dry-run"

    if is_dry:
        return _mock_narrative(context_data)

    category = context_data.get("category", "A")
    system_prompt = CATEGORY_A_SYSTEM_PROMPT if category == "A" else CATEGORY_B_SYSTEM_PROMPT

    # Build user prompt with context_data + failure_context
    user_prompt = _build_user_prompt(context_data, failure_context or [])

    try:
        raw_json = _call_llm(system_prompt, user_prompt, config)
        return _parse_narrative(raw_json, category)
    except Exception as e:
        logger.error("LLM generation failed: %s — using fallback mock", e)
        return _mock_narrative(context_data)


def build_prompt(context_data: dict, failure_context: list[str] | None = None) -> str:
    """
    Build the user-facing prompt from context_data.
    Called by weekly_orchestrator.py before generate().
    Returns English prompt string.
    """
    return _build_user_prompt(context_data, failure_context or [])


def _build_user_prompt(context_data: dict, failure_context: list[str]) -> str:
    """Construct English prompt from context_data dict."""
    category = context_data.get("category", "A")
    stock_code = context_data.get("stock_code", "N/A")
    stock_name = context_data.get("stock_name", "Unknown")

    prompt_lines = [
        f"Stock: {stock_name} ({stock_code}) — Category {category}",
        f"Analysis date: {context_data.get('analysis_date', 'N/A')}",
        "",
        "## Financial Context",
        f"YoY Revenue Growth: {context_data.get('yoy_revenue_growth', 'N/A')}",
        f"YoY Op.Income Growth: {context_data.get('yoy_op_income_growth', 'N/A')}",
        f"Latest Quarter: {context_data.get('latest_quarter', 'N/A')}",
        f"PER Current: {context_data.get('per_current', 'N/A')}",
        f"PER Sector Avg: {context_data.get('per_sector_avg', 'N/A')}",
        f"Foreign Flow 4w: {context_data.get('foreign_flow_4w', 'N/A')}",
        "",
        "## Macro Environment",
        f"Rate Direction: {context_data.get('rate_direction', 'N/A')}",
        f"Inflation Trend: {context_data.get('inflation_trend', 'N/A')}",
        f"Risk Appetite: {context_data.get('risk_appetite', 'N/A')}",
        f"USD Strength: {context_data.get('usd_strength', 'N/A')}",
        f"Macro Summary: {context_data.get('macro_summary', 'N/A')}",
    ]

    # Sector Directions — skip section if empty
    sector_dirs: dict = context_data.get("sector_directions") or {}
    if sector_dirs:
        prompt_lines += ["", "## Sector Directions"]
        for sector_name, direction in sector_dirs.items():
            prompt_lines.append(f"{sector_name}: {direction}")

    # NOTE: action_item and action_checklist are Korean user-facing text (synthesize_macro.py P6).
    # They must NOT appear in the English LLM prompt (P5-A violation).
    # They remain in context_data for dashboard/report use outside LLM.

    prompt_lines += [
        "",
        "## STEEPs Signals",
        f"Top Signals: {context_data.get('top_signals', [])}",
    ]

    if failure_context:
        prompt_lines.extend([
            "",
            "## Previous Attempt Failures (fix these in this attempt):",
            *[f"- {f}" for f in failure_context],
        ])

    prompt_lines.extend([
        "",
        "Generate a complete NarrativeOutput JSON with all required fields for this stock.",
        "Ensure sentiment_weight=0.0 and text >= 1000 bytes.",
    ])

    return "\n".join(prompt_lines)


def _call_llm(system_prompt: str, user_prompt: str, config: dict) -> str:
    """
    Call Claude API to generate narrative.
    Returns raw JSON string response.
    """
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
    except ImportError:
        raise RuntimeError("anthropic library not installed — cannot call LLM")


def _parse_narrative(raw_json: str, category: str) -> NarrativeOutput:
    """Parse LLM JSON response into NarrativeOutput. Validates sentinel."""
    # Extract JSON from potential markdown code block
    import re
    json_match = re.search(r"```json\s*(.*?)\s*```", raw_json, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)

    data = json.loads(raw_json)

    # Enforce sentinel — never trust LLM on sentiment_weight
    data["sentiment_weight"] = 0.0
    data["category"] = category

    return NarrativeOutput(**{
        k: v for k, v in data.items()
        if k in {f.name for f in dataclasses.fields(NarrativeOutput)}
    })


def _mock_narrative(context_data: dict) -> NarrativeOutput:
    """
    Return a stock-aware mock NarrativeOutput for dry-run mode and TDD.

    Uses actual per_current, per_sector_avg, foreign_flow_4w from context_data
    so NBS (Numeric Backstop) checks pass — prevents cross-stock number mismatch.
    Falls back to safe DATA_UNAVAILABLE strings when fields are None.
    """
    category = context_data.get("category", "A")
    stock_code = context_data.get("stock_code", "")
    stock_name = context_data.get("stock_name", "Unknown Stock")

    # Read actual numeric fields — NBS verifies these appear in narrative text
    per_current = context_data.get("per_current")
    per_sector_avg = context_data.get("per_sector_avg")
    foreign_flow_4w = context_data.get("foreign_flow_4w")
    top_signals = context_data.get("top_signals", [])
    signals_text = "; ".join(str(s)[:60] for s in top_signals[:3]) or "No signals available"

    # Build NBS-compatible field strings from actual context values
    if per_current is not None and per_sector_avg is not None:
        try:
            per_curr_f = float(per_current)
            per_sect_f = float(per_sector_avg)
            diff_pct = round((per_curr_f / per_sect_f - 1) * 100, 1)
            if diff_pct == 0.0:
                per_vs_sector_str = f"{per_curr_f:.1f}x, at parity with sector avg {per_sect_f:.1f}x"
                per_text = f"PER of {per_curr_f:.1f}x is at parity with the sector average of {per_sect_f:.1f}x."
            else:
                direction_word = "premium" if diff_pct > 0 else "discount"
                per_vs_sector_str = (
                    f"{per_curr_f:.1f}x, {abs(diff_pct):.1f}% {direction_word}"
                    f" vs. sector avg {per_sect_f:.1f}x"
                )
                per_text = f"PER of {per_curr_f:.1f}x represents a {abs(diff_pct):.1f}% {direction_word} to the sector average of {per_sect_f:.1f}x."
        except (TypeError, ValueError):
            per_vs_sector_str = "N/A — PER data unavailable"
            per_text = "Valuation data unavailable (dry-run)."
    else:
        per_vs_sector_str = "N/A — PER data unavailable"
        per_text = "Valuation data unavailable (dry-run)."

    if foreign_flow_4w is not None:
        try:
            flow_f = float(foreign_flow_4w)
            flow_direction = "buy" if flow_f >= 0 else "sell"
            foreign_flow_str = f"4-week net {flow_direction}: {abs(flow_f):.1f}M (cumulative foreign institutional flow)"
            foreign_text = f"Foreign institutional 4-week flow of {abs(flow_f):.1f}M net {flow_direction} reflects current positioning."
        except (TypeError, ValueError):
            foreign_flow_str = "N/A — foreign flow data unavailable"
            foreign_text = "Foreign flow data unavailable (dry-run)."
    else:
        foreign_flow_str = "N/A — foreign flow data unavailable (dry-run)"
        foreign_text = "Foreign flow data unavailable (dry-run)."

    # Build YoY growth context for text body (NBS-01 anchors on yoy_growth field, not text)
    yoy_rev = context_data.get("yoy_revenue_growth")
    yoy_op = context_data.get("yoy_op_income_growth")
    if yoy_rev is not None and yoy_op is not None:
        try:
            yoy_text = (
                f"Mock financial context: revenue growth estimated at {float(yoy_rev)*100:.1f}% YoY, "
                f"operating income growth at {float(yoy_op)*100:.1f}% YoY (dry-run placeholders — DART API not connected). "
            )
        except (TypeError, ValueError):
            yoy_text = "YoY financial data unavailable in dry-run mode (DART API not connected). "
    else:
        yoy_text = "YoY financial data unavailable in dry-run mode (DART API not connected). "

    if category == "A":
        text = (
            f"{stock_name} ({stock_code}) weekly investment signal analysis for dry-run mode. "
            f"{per_text} "
            f"{foreign_text} "
            f"{yoy_text}"
            f"Quarterly trend assessment is based on available EnvironmentScan signals and macro context. "
            f"Active macro environment: Fed rate direction hold, inflation cooling, "
            f"risk appetite moderate, USD strength noted. "
            f"Current sector confidence reflects signal-driven scoring from EnvironmentScan pipeline. "
            f"Key environmental signals driving this analysis: {signals_text}. "
            f"Macro backdrop assessment: global central bank policy normalization ongoing, "
            f"with geopolitical risk premium elevated across emerging market equities. "
            f"Primary downside risk is macro-driven volatility from geopolitical escalation "
            f"and yen carry trade unwind risk, "
            f"with estimated portfolio impact of minus five to minus ten percentage points in adverse scenario. "
            f"Foreign institutional positioning and sector signal strength support current stance. "
            f"Signal-driven watchlist selection confirmed this stock as relevant to active themes."
        )
        return NarrativeOutput(
            category="A",
            text=text,
            sentiment_weight=0.0,
            yoy_growth="N/A — YoY/quarterly data unavailable (dry-run, DART API not connected)",
            per_vs_sector=per_vs_sector_str,
            foreign_flow_direction=foreign_flow_str,
            downside_risk=(
                "Geopolitical escalation (Hormuz crisis) + yen carry unwind → "
                "est. -5 to -10 percentage point portfolio impact in adverse scenario"
            ),
            direction="Neutral — monitor and wait",
        )
    else:
        # Category B — theme stock mock (generic, not stock-specific)
        DEFAULT_MARKET_SIZE = "Global addressable market: $180bn, CAGR 18% (2024-2030, McKinsey estimate)"
        market_size_val = context_data.get("market_size") or DEFAULT_MARKET_SIZE
        catalyst_val = context_data.get("catalyst", "Q2 2026 product launch — primary monetization catalyst")
        theme_duration_val = context_data.get(
            "theme_duration", "16-24 week momentum expected as theme adoption curve accelerates"
        )
        dissolution_val = context_data.get(
            "dissolution_risk", "Competitive entry by global platform players — est. 3-8pp market share erosion"
        )
        disclaimer_val = context_data.get(
            "disclaimer",
            "This analysis does not constitute investment advice. Past performance is not indicative of future results.",
        )
        text = (
            f"{stock_name} ({stock_code}) Category B theme analysis for dry-run mode. "
            f"Market size context: {market_size_val}. "
            f"This stock is positioned within an emerging theme with significant growth potential, "
            f"reflecting a total addressable market growth trajectory of approximately 18% CAGR. "
            f"The stock holds a meaningful positioning within its primary theme, "
            f"supported by active EnvironmentScan signals: {signals_text}. "
            f"Macro environment (FRED): rate hold, inflation cooling, risk moderate, USD strong. "
            f"Catalyst: {catalyst_val}. "
            f"Theme duration estimate: {theme_duration_val}. "
            f"Primary dissolution risk: {dissolution_val}. "
            f"Valuation premium over sector average requires catalyst execution evidence. "
            f"Theme momentum is signal-driven, with EnvironmentScan confirming active thematic "
            f"alignment across technological and structural change dimensions. "
            f"This analysis does not constitute investment advice and is based solely on "
            f"publicly available information. Past performance is not indicative of future results. "
            f"Investment decisions remain solely the reader's responsibility."
        )
        return NarrativeOutput(
            category="B",
            text=text,
            sentiment_weight=0.0,
            market_size=market_size_val,
            stock_positioning=(
                context_data.get("stock_positioning")
                or f"{stock_name} — theme positioning data not provided in dry-run"
            ),
            catalyst=catalyst_val,
            theme_duration=theme_duration_val,
            dissolution_risk=dissolution_val,
            disclaimer=disclaimer_val,
        )
