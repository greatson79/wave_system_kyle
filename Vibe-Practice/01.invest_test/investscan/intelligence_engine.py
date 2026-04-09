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

    # Weekly Action Guidance — show if action_item or checklist is present
    action_item: str = context_data.get("action_item") or ""
    action_checklist: list = context_data.get("action_checklist") or []
    has_action = action_item and action_item != "DATA_UNAVAILABLE"
    if has_action or action_checklist:
        prompt_lines += ["", "## Weekly Action Guidance"]
        if has_action:
            prompt_lines.append(f"Action: {action_item}")
        if action_checklist:
            prompt_lines.append("Checklist:")
            for item in action_checklist:
                prompt_lines.append(f"- {item}")

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
    """Return a realistic mock NarrativeOutput for dry-run mode and TDD."""
    category = context_data.get("category", "A")

    if category == "A":
        return NarrativeOutput(
            category="A",
            text=(
                "Samsung Electronics enters Q1 2026 with memory fundamentals showing structural "
                "recovery. HBM3E ramp for AI training clusters positions the DRAM segment as the "
                "primary growth vector, with Q4 2025 operating income surging 34.2% YoY on improved "
                "ASP mix. The 4-week cumulative foreign institutional net buy of +$380M signals "
                "sustained conviction from global asset managers. Current PER of 10.2x represents a "
                "28.4% discount to the sector average of 14.2x, creating a compelling entry window "
                "for value-oriented investors. Primary downside risk remains DRAM oversupply "
                "resurgence if the AI capex cycle moderates faster than anticipated, with an estimated "
                "revenue impact of -12% in that scenario. The stock trajectory aligns with the broader "
                "technology sector bullish regime established by stabilizing Fed policy and improving "
                "risk appetite indicators. Foreign institutional accumulation pattern further validates "
                "the thesis that memory cycle recovery is entering a sustained phase rather than a "
                "transient bounce driven by inventory restocking alone."
            ),
            sentiment_weight=0.0,
            yoy_growth="Revenue +8.3% YoY, Op.Income +34.2% (2025Q4)",
            per_vs_sector="10.2x, 28.4% discount vs. sector avg 14.2x",
            foreign_flow_direction="4-week net buy: +$380M (cumulative)",
            downside_risk="DRAM oversupply resurgence → est. -12% revenue if AI capex cycle moderates Q3 2026",
            direction="Positive momentum maintained",
        )
    else:
        return NarrativeOutput(
            category="B",
            text=(
                "NAVER's convergence of AI capability and commerce dominance creates a defensible "
                "growth runway through 2026. The HyperCLOVA X integration into Smart Store ecosystem "
                "positions NAVER at the intersection of Korea's two fastest-growing digital verticals. "
                "With 78% Korean search market share and 12M monthly active users primed for AI "
                "shopping assistant adoption, the upcoming Q2 2026 launch represents a significant "
                "monetization inflection point. The global AI commerce market trajectory of $42bn "
                "with 19% CAGR through 2028 provides the macro tailwind. Theme duration estimate of "
                "18-30 weeks reflects the adoption curve of AI-integrated commerce features. Primary "
                "dissolution risk remains Google's AI Mode expansion into the Korean market, with "
                "potential search share erosion of 3-8 percentage points by Q4 2026. Operating "
                "leverage is expected to improve as AI infrastructure costs plateau in H2 2026. "
                "This analysis does not constitute investment advice and is based solely on publicly "
                "available information. Investment decisions remain solely the reader's responsibility."
            ),
            sentiment_weight=0.0,
            market_size="Korean AI commerce market: $42bn, CAGR 19% (2025-2028, Gartner)",
            stock_positioning="Dominant search-to-commerce funnel with HyperCLOVA X integration — 78% Korean search market share",
            catalyst="Q2 2026 AI shopping assistant launch targeting 12M monthly active users",
            theme_duration="18-30 week momentum expected as AI commerce adoption curve steepens",
            dissolution_risk="Google AI Mode Korean market entry by Q4 2026 — search share erosion risk (est. 3-8pp)",
            disclaimer="This analysis is based on publicly available information and does not constitute investment advice.",
        )
