# Branch 2: Multi-Model CLI Integration Analysis for InvestScan

**Branch 2.1**: MULTI-MODEL Orchestration (Claude + Gemini + OpenAI)
**Branch 2.2**: SINGLE-MODEL Primary (Claude only, others as fallback)
**Date**: 2026-03-28
**Context**: Solo dev, MacBook M5 Max 64GB, existing CLI subscription accounts (no API keys)

---

## CRITICAL CONSTRAINT VALIDATION

> "OpenAI, Gemini를 사용해야 한다면, API 연결방식을 사용하지 말라. 이미 2개 모델은 '구독 계정'을 가지고 있다."

### Live Verification Results (tested 2026-03-28)

| CLI Tool | Installed | Version | Auth Method | Auth Mode | Working |
|----------|-----------|---------|-------------|-----------|---------|
| **Claude Code** | `/Users/kylechoi/.local/bin/claude` | Current | Anthropic subscription | Claude Max | YES |
| **Gemini CLI** | `@google/gemini-cli@0.35.1` (npm global) | 0.35.1 | Google OAuth (Personal) | `oauth-personal` | YES |
| **OpenAI Codex CLI** | `@openai/codex@0.116.0` (npm global) | 0.116.0 | ChatGPT subscription | `auth_mode: "chatgpt"` | YES |

**Confirmed**: All three CLIs authenticate via subscription accounts. Zero API keys required.

Authentication evidence:
- Gemini: `~/.gemini/settings.json` shows `"selectedType": "oauth-personal"`, `~/.gemini/oauth_creds.json` exists
- Codex: `~/.codex/auth.json` shows `"auth_mode": "chatgpt"`, ChatGPT Plus/Pro subscription auth
- Claude: Already running as the primary environment

---

## Part A: HOW Each CLI Works (Technical Deep-Dive)

### A.1 Gemini CLI

**Authentication Flow:**
1. First run: `gemini` opens browser for Google OAuth consent
2. Tokens cached in `~/.gemini/oauth_creds.json`
3. Subsequent runs: "Loaded cached credentials." (no browser needed)
4. Subscription tier detected automatically from Google account

**Non-Interactive (Headless) Mode:**
```bash
# Basic text output
gemini -p "Your prompt here" -o text

# Structured JSON output (includes response + stats + token usage)
gemini -p "Your prompt here" -o json

# Streaming JSON output (JSONL events)
gemini -p "Your prompt here" -o stream-json

# Model selection
gemini -p "prompt" -m gemini-2.5-pro -o text

# File reference with @ syntax
gemini -p "Analyze @/path/to/file.json" -o json

# Pipe stdin as context
cat data.csv | gemini -p "Summarize this data" -o text
```

**JSON Output Structure:**
```json
{
  "session_id": "uuid",
  "response": "The model's text response",
  "stats": {
    "models": {
      "gemini-2.5-pro": {
        "api": { "totalRequests": 1, "totalErrors": 0, "totalLatencyMs": 3061 },
        "tokens": { "input": 47119, "prompt": 47119, "candidates": 58, "total": 47558, "cached": 0, "thoughts": 381 }
      }
    }
  }
}
```

**Available Models (via subscription):**
- `gemini-2.5-pro` -- Best reasoning, long context
- `gemini-2.5-flash` -- Fast, efficient
- `gemini-2.5-flash-lite` -- Fastest, cheapest (default for routing)
- `gemini-3-flash-preview` -- Latest preview model

**Subscription Quotas:**
| Tier | Requests/Day |
|------|-------------|
| Free (individual) | 1,000 |
| Google AI Pro | 1,500 |
| Google AI Ultra | 2,000 |

**Exit Codes:** 0=success, 1=error, 42=input error, 53=turn limit exceeded

---

### A.2 OpenAI Codex CLI

**Authentication Flow:**
1. First run: `codex login` or just `codex` opens browser for ChatGPT OAuth device code flow
2. Tokens cached in `~/.codex/auth.json` with `auth_mode: "chatgpt"`
3. Subsequent runs: reuses saved credentials automatically
4. ChatGPT Plus/Pro/Business/Edu/Enterprise plans all work

**Non-Interactive (Exec) Mode:**
```bash
# Basic execution (final response to stdout, progress to stderr)
codex exec "Your prompt here"
# Short form
codex e "Your prompt here"

# JSON Lines streaming (structured events)
codex exec --json "Your prompt here"

# Save final response to file
codex exec -o /path/output.txt "Your prompt here"

# Structured output with JSON Schema validation
codex exec --output-schema schema.json "Your prompt here"

# Model selection
codex exec -m gpt-5.4 "Your prompt here"

# Pipe from stdin
echo "data" | codex exec -

# Ephemeral mode (no session persistence)
codex exec --ephemeral "Your prompt here"

# Full auto mode (allows edits, no approval)
codex exec --full-auto "Your prompt here"
```

**JSON Lines Output Structure:**
```jsonl
{"type":"thread.started","thread_id":"uuid"}
{"type":"turn.started"}
{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"response text"}}
{"type":"turn.completed","usage":{"input_tokens":19321,"cached_input_tokens":19200,"output_tokens":16}}
```

**Available Models (via ChatGPT subscription):**
- `gpt-5.4` -- Latest, most capable (default)
- `gpt-5.3-codex` -- Previous generation
- Others accessible via `-m` flag

**MCP Server Mode:**
```bash
# Start Codex as an MCP server (stdio protocol)
codex mcp-server

# Exposes two tools:
#   "codex" -- Run a new Codex session
#   "codex-reply" -- Continue an existing conversation
```

---

### A.3 Claude Code (The Orchestrator)

Claude Code is already the running environment. It can:
1. Execute Bash commands (subprocess calls to Gemini/Codex CLIs)
2. Run Python scripts that call other CLIs
3. Connect to MCP servers (Codex as MCP server)
4. Read/write files to pass data between models

---

## Part B: Integration Approaches (3 Methods)

### Method 1: Python Subprocess (PROVEN -- RECOMMENDED)

Direct subprocess calls from Python scripts. Tested and working.

```python
#!/usr/bin/env python3
"""
InvestScan Multi-Model Orchestrator
Uses CLI subscription auth -- NO API keys required.
"""
import subprocess
import json
import time
from pathlib import Path
from typing import Optional

class GeminiCLI:
    """Wrapper for Gemini CLI using Google OAuth subscription."""

    def __init__(self, model: str = "gemini-2.5-pro"):
        self.model = model

    def query(self, prompt: str, output_format: str = "json") -> dict:
        """Call Gemini CLI and return parsed response."""
        cmd = ["gemini", "-p", prompt, "-o", output_format]
        if self.model:
            cmd.extend(["-m", self.model])

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr[:500]}

        if output_format == "json":
            data = json.loads(result.stdout)
            return {
                "success": True,
                "response": data["response"],
                "models_used": list(data["stats"]["models"].keys()),
                "total_tokens": sum(
                    m["tokens"]["total"]
                    for m in data["stats"]["models"].values()
                )
            }
        else:
            return {"success": True, "response": result.stdout.strip()}

    def analyze_file(self, filepath: str, prompt: str) -> dict:
        """Analyze a file using Gemini's @ syntax."""
        return self.query(f"{prompt} @{filepath}")


class CodexCLI:
    """Wrapper for OpenAI Codex CLI using ChatGPT subscription."""

    def __init__(self, model: str = "gpt-5.4"):
        self.model = model

    def query(self, prompt: str, json_mode: bool = True) -> dict:
        """Call Codex CLI exec and return parsed response."""
        cmd = ["npx", "@openai/codex", "exec"]
        if json_mode:
            cmd.append("--json")
        if self.model:
            cmd.extend(["-m", self.model])
        cmd.append(prompt)

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr[:500]}

        if json_mode:
            responses = []
            usage = {}
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                event = json.loads(line)
                if (event.get('type') == 'item.completed' and
                    event.get('item', {}).get('type') == 'agent_message'):
                    responses.append(event['item']['text'])
                elif event.get('type') == 'turn.completed':
                    usage = event.get('usage', {})
            return {
                "success": True,
                "response": "\n".join(responses),
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0)
            }
        else:
            return {"success": True, "response": result.stdout.strip()}

    def structured_query(self, prompt: str, schema_path: str, output_path: str) -> dict:
        """Call Codex with JSON Schema output validation."""
        cmd = [
            "npx", "@openai/codex", "exec",
            "--output-schema", schema_path,
            "-o", output_path,
            prompt
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0 and Path(output_path).exists():
            with open(output_path) as f:
                return {"success": True, "response": json.load(f)}
        return {"success": False, "error": result.stderr[:500]}


class MultiModelOrchestrator:
    """
    Orchestrator that uses Claude (self) + Gemini CLI + Codex CLI.
    All three use subscription authentication -- zero API keys.
    """

    def __init__(self):
        self.gemini = GeminiCLI(model="gemini-2.5-pro")
        self.codex = CodexCLI(model="gpt-5.4")

    def investment_analysis(self, ticker: str, data: dict) -> dict:
        """
        Multi-model investment analysis pipeline.

        Gemini: Long-context historical analysis (1M token window)
        Codex/GPT: Structured classification (JSON mode)
        Claude: Synthesis and final recommendation (orchestrator)
        """
        context = json.dumps(data, indent=2)

        # Step 1: Gemini -- Historical context & fact verification
        gemini_result = self.gemini.query(
            f"You are an investment analyst. Analyze {ticker} with this data:\n"
            f"{context}\n"
            f"Provide historical PE ratio context and growth trajectory analysis. "
            f"Compare to sector averages. 3-4 sentences."
        )

        # Step 2: Codex/GPT -- Structured classification
        codex_result = self.codex.query(
            f"You are an investment analyst. For {ticker} with data:\n"
            f"{context}\n"
            f"Classify as overvalued/fairly_valued/undervalued. "
            f"Reply with ONLY a JSON object: "
            f'{{"verdict":"...","confidence":0.0-1.0,"key_factors":["...","..."]}}'
        )

        # Step 3: Claude (this process) would synthesize both
        return {
            "ticker": ticker,
            "gemini_analysis": gemini_result,
            "gpt_classification": codex_result,
            "synthesis_prompt": (
                f"Synthesize these two analyses for {ticker}:\n"
                f"1. Historical context (Gemini): {gemini_result.get('response', 'N/A')}\n"
                f"2. Classification (GPT): {codex_result.get('response', 'N/A')}\n"
                f"Provide a final investment recommendation."
            )
        }


# Usage example
if __name__ == "__main__":
    orch = MultiModelOrchestrator()
    result = orch.investment_analysis("AAPL", {
        "ticker": "AAPL",
        "price": 185.50,
        "pe_ratio": 28.5,
        "revenue_growth": 0.08,
        "sector": "Technology"
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**Measured Performance (2026-03-28):**
| Operation | Latency |
|-----------|---------|
| Gemini simple query (text) | ~11s |
| Gemini simple query (json) | ~12s |
| Gemini complex analysis (gemini-2.5-pro) | ~28s |
| Codex simple query (exec) | ~2.5s |
| Codex complex analysis (gpt-5.4) | ~3.3s |

---

### Method 2: MCP Server Integration

Codex CLI can run as an MCP server, allowing Claude Code to call it as a tool.

**Configuration for Claude Code** (add to `.claude/settings.json`):
```json
{
  "mcpServers": {
    "codex": {
      "command": "npx",
      "args": ["@openai/codex", "mcp-server"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/opt/homebrew/bin"
      }
    }
  }
}
```

**Codex MCP Tools Exposed:**
| Tool | Description |
|------|-------------|
| `codex` | Run a new Codex session with full configuration |
| `codex-reply` | Continue an existing conversation by thread ID |

**Pros:**
- Native tool integration within Claude Code
- Conversation continuity via thread IDs
- Claude Code handles the MCP protocol automatically

**Cons:**
- Only Codex has official MCP server mode
- Gemini CLI has no equivalent `gemini mcp-server` command (it can _consume_ MCP, not _serve_ it)
- Additional process running in background
- Less control over output parsing

**NOTE on Gemini MCP:** Third-party MCP servers exist (e.g., `gemini-mcp`, `RLabs-Inc/gemini-mcp`) but they ALL require Gemini API keys. None use OAuth/subscription auth. The only way to use Gemini with subscription auth is the subprocess approach (Method 1).

---

### Method 3: Bash Script Orchestration

For simpler workflows, pure shell scripts can coordinate the CLIs.

```bash
#!/usr/bin/env bash
# investscan-multi-model.sh -- Multi-model analysis using subscription CLIs
set -euo pipefail

TICKER="$1"
DATA_FILE="$2"
OUTPUT_DIR="$3"
mkdir -p "$OUTPUT_DIR"

echo "[1/3] Gemini: Historical analysis..."
gemini -p "Analyze investment data for $TICKER from @$DATA_FILE. \
  Provide historical PE context and growth trajectory. 3 sentences." \
  -m gemini-2.5-pro -o json > "$OUTPUT_DIR/gemini_analysis.json"

echo "[2/3] Codex: Structured classification..."
npx @openai/codex exec --json \
  "Classify $TICKER as overvalued/fairly_valued/undervalued based on: $(cat $DATA_FILE). \
   Reply with ONLY JSON: {\"verdict\":\"...\",\"confidence\":0.0-1.0}" \
  > "$OUTPUT_DIR/codex_classification.jsonl"

echo "[3/3] Claude: Synthesis..."
# Claude Code is the orchestrator -- it reads both outputs and synthesizes
GEMINI_RESPONSE=$(cat "$OUTPUT_DIR/gemini_analysis.json" | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])")
CODEX_RESPONSE=$(cat "$OUTPUT_DIR/codex_classification.jsonl" | python3 -c "
import sys,json
for line in sys.stdin:
    e=json.loads(line)
    if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message':
        print(e['item']['text'])
")

echo "Gemini says: $GEMINI_RESPONSE"
echo "Codex says: $CODEX_RESPONSE"
echo "Claude synthesizes these in the main workflow."
```

---

## Part C: Multi-Model Task Allocation Strategy

### Which Model for Which Task?

| Task Category | Best Model | Why | InvestScan Use Case |
|---------------|-----------|-----|-------------------|
| **Orchestration & Reasoning** | Claude (Opus/Sonnet) | Best at planning, multi-step reasoning, synthesis | Main pipeline controller, final recommendations |
| **Long-Context Analysis** | Gemini 2.5 Pro | 1M+ token context window | Analyzing full 10-K filings, quarterly reports, multi-year data |
| **Fact Verification** | Gemini 2.5 Pro | Grounded in Google Search data | Cross-checking financial claims against public data |
| **Structured Output** | GPT-5.4 (Codex) | Native JSON mode, schema validation | Stock classifications, risk scores, structured ratings |
| **Fast Classification** | GPT-5.4 (Codex) | Lowest latency (~2.5s) | Real-time sentiment classification, news categorization |
| **Code Generation** | Claude or Codex | Both excellent; Codex has sandbox | Data pipeline scripts, analysis modules |
| **Translation** | Claude | Best Korean language quality | Korean market reports, user-facing content |
| **Document Synthesis** | Claude | Best at coherent long-form writing | Final investment reports, weekly summaries |

### Proposed Multi-Model Pipeline for InvestScan

```
                    ┌─────────────────────────────────┐
                    │      Claude Code (Orchestrator)  │
                    │  - Pipeline control              │
                    │  - Final synthesis               │
                    │  - Korean translation            │
                    └─────┬───────────┬───────────┬───┘
                          │           │           │
              ┌───────────▼──┐  ┌─────▼──────┐  ┌▼──────────────┐
              │  Gemini CLI  │  │ Codex CLI   │  │ Claude Code   │
              │  (subprocess)│  │ (subprocess)│  │ (self/native) │
              ├──────────────┤  ├─────────────┤  ├───────────────┤
              │ Long-context │  │ Structured  │  │ Synthesis     │
              │ analysis     │  │ JSON output │  │ & reasoning   │
              │ Fact-check   │  │ Fast classif│  │ Translation   │
              │ 10-K parsing │  │ Risk scores │  │ Report gen    │
              └──────────────┘  └─────────────┘  └───────────────┘
                  OAuth             ChatGPT          Subscription
                (Google)            (OpenAI)         (Anthropic)
              NO API KEYS         NO API KEYS       NO API KEYS
```

### Output Combination Pattern

```python
def combine_multi_model_outputs(gemini_result, codex_result):
    """
    Combine outputs from Gemini and Codex for Claude synthesis.
    Claude Code (the orchestrator) reads both and produces the final output.
    """
    synthesis_context = f"""
## Multi-Model Analysis Results

### Source 1: Gemini (Historical Context & Fact Verification)
{gemini_result.get('response', 'N/A')}

### Source 2: GPT-5.4 (Structured Classification)
{codex_result.get('response', 'N/A')}

### Instructions for Synthesis
1. Cross-validate: Where do the models agree/disagree?
2. Resolve conflicts using factual evidence
3. Produce a single coherent recommendation
4. Rate confidence (0-1) based on model agreement
"""
    return synthesis_context
```

---

## Part D: Branch 2.1 -- MULTI-MODEL Orchestration (Detailed)

### Architecture

```
InvestScan Multi-Model Architecture
====================================

User (Cron Schedule)
  │
  ▼
[Claude Code CLI] ◄── Primary orchestrator
  │
  ├──[Phase 1: Data Collection]
  │    └── Python scripts (requests, BeautifulSoup, etc.)
  │
  ├──[Phase 2: Multi-Model Analysis]
  │    │
  │    ├── subprocess: gemini -p "..." -o json
  │    │     └── Google OAuth (subscription)
  │    │     └── gemini-2.5-pro for long documents
  │    │     └── Returns: JSON with response + token stats
  │    │
  │    ├── subprocess: codex exec --json "..."
  │    │     └── ChatGPT subscription auth
  │    │     └── gpt-5.4 for structured output
  │    │     └── Returns: JSONL events
  │    │
  │    └── Claude (native): synthesis + reasoning
  │          └── Claude subscription (already active)
  │          └── Best reasoning, Korean language
  │
  ├──[Phase 3: Report Generation]
  │    └── Claude: coherent report writing
  │    └── Claude: Korean translation
  │
  └──[Phase 4: Distribution]
       └── Email, Notion, etc.
```

### Implementation Complexity

| Component | LOC (Python) | LOC (Bash) | Effort |
|-----------|-------------|-----------|--------|
| GeminiCLI wrapper | ~50 | N/A | 1 hour |
| CodexCLI wrapper | ~60 | N/A | 1 hour |
| MultiModelOrchestrator | ~80 | N/A | 2 hours |
| Output parsers | ~40 | ~30 | 1 hour |
| Error handling + retry | ~60 | ~20 | 2 hours |
| Configuration | ~30 | ~10 | 30 min |
| **Total** | **~320** | **~60** | **~7.5 hours** |

### Cost Analysis

| Model | Auth Method | Monthly Cost | Requests/Day |
|-------|-----------|-------------|-------------|
| Claude Code | Subscription | Already paying | Unlimited (within plan) |
| Gemini CLI | Google OAuth | Already paying (Google AI Pro/Ultra) | 1,500-2,000/day |
| Codex CLI | ChatGPT subscription | Already paying (ChatGPT Plus/Pro) | Included in plan |
| **Total Additional Cost** | | **$0** | |

### Error Handling

```python
import time
from functools import wraps

def retry_cli(max_retries=3, backoff_factor=2):
    """Retry decorator for CLI subprocess calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                result = func(*args, **kwargs)
                if result.get("success"):
                    return result
                if attempt < max_retries - 1:
                    wait = backoff_factor ** attempt
                    time.sleep(wait)
            return result  # Return last failed result
        return wrapper
    return decorator

class RobustGeminiCLI(GeminiCLI):
    @retry_cli(max_retries=3)
    def query(self, prompt, output_format="json"):
        return super().query(prompt, output_format)

class RobustCodexCLI(CodexCLI):
    @retry_cli(max_retries=3)
    def query(self, prompt, json_mode=True):
        return super().query(prompt, json_mode)
```

### Known Limitations

1. **Gemini CLI latency**: ~11-28s per call (includes CLI startup + model inference). Not suitable for real-time.
2. **Codex CLI latency**: ~2.5-3.5s per call. Fast enough for batch processing.
3. **No parallel execution guarantee**: Each subprocess is sequential unless you use `concurrent.futures`.
4. **Gemini CLI subprocess auth issue**: There is a known issue where Gemini CLI in subprocess/non-TTY mode may prompt for re-authentication in ACP mode. Workaround: ensure `~/.gemini/oauth_creds.json` exists and is valid.
5. **Rate limits**: Google AI Pro gives 1,500 requests/day. For a daily scan of ~50-100 stocks, this is ample.
6. **No Gemini MCP server using subscription auth**: All existing Gemini MCP servers require API keys. Subprocess is the only subscription-auth path.

---

## Part E: Branch 2.2 -- SINGLE-MODEL Primary (Claude Only)

### Architecture

```
InvestScan Single-Model Architecture
=====================================

User (Cron Schedule)
  │
  ▼
[Claude Code CLI] ◄── Does everything
  │
  ├──[Phase 1: Data Collection]
  │    └── Python scripts
  │
  ├──[Phase 2: Analysis]
  │    └── Claude: all reasoning, classification, synthesis
  │    └── No external CLI calls needed
  │
  ├──[Phase 3: Report Generation]
  │    └── Claude: writing + Korean translation
  │
  └──[Phase 4: Distribution]
       └── Email, Notion, etc.
```

### When Multi-Model is NOT Worth It

1. **Simple daily scans**: If analyzing <20 stocks with standard metrics, Claude alone is sufficient.
2. **No long documents**: If not parsing full 10-K filings (>100 pages), Gemini's 1M context is unnecessary.
3. **No structured output requirement**: If reports are free-form text, GPT's JSON schema mode adds no value.
4. **Speed is critical**: Removing CLI subprocess overhead (11-28s for Gemini) makes the pipeline faster.
5. **Maintenance burden**: One model = one failure mode. Three models = three failure modes.

### Implementation Complexity

| Component | LOC (Python) | Effort |
|-----------|-------------|--------|
| Claude-only analysis | ~100 | 3 hours |
| Report generation | ~50 | 1 hour |
| Error handling | ~30 | 1 hour |
| **Total** | **~180** | **~5 hours** |

### Fallback Strategy

Use Gemini/Codex only when Claude fails or for specific verification:
```python
def analyze_with_fallback(prompt, data):
    """Claude-first with multi-model fallback."""
    # Primary: Claude handles it (native -- no subprocess needed)
    claude_result = analyze_with_claude(prompt, data)

    if claude_result["confidence"] > 0.8:
        return claude_result

    # Fallback: Cross-validate with Gemini if confidence is low
    gemini = GeminiCLI(model="gemini-2.5-pro")
    gemini_result = gemini.query(f"Verify this analysis: {claude_result['response']}")

    # Fallback: Get structured classification from GPT if needed
    codex = CodexCLI(model="gpt-5.4")
    codex_result = codex.query(f"Classify: {json.dumps(data)}")

    return {
        "primary": claude_result,
        "verification": gemini_result,
        "classification": codex_result
    }
```

---

## Part F: COMPARISON -- Multi-Model vs Single-Model

### Decision Matrix

| Criterion | Multi-Model (2.1) | Single-Model (2.2) | Winner |
|-----------|-------------------|-------------------|--------|
| **Setup complexity** | 7.5 hours, ~320 LOC | 5 hours, ~180 LOC | Single |
| **Maintenance** | 3 CLIs to keep updated | 1 CLI | Single |
| **Failure modes** | 3x (auth expiry, version breaks, rate limits) | 1x | Single |
| **Long document analysis** | Gemini 1M tokens | Claude 200K tokens | Multi |
| **Structured output** | GPT schema validation | Claude JSON (good but no schema) | Multi |
| **Classification speed** | GPT: 2.5s | Claude: varies | Multi |
| **Report quality** | Multi-perspective synthesis | Single perspective | Multi |
| **Fact verification** | Cross-model validation | Self-validation only | Multi |
| **Additional cost** | $0 (all subscription) | $0 | Tie |
| **Korean language** | Claude best | Claude (native) | Tie |
| **10-K/Annual report parsing** | Gemini excels (1M context) | Claude limited (200K) | Multi |
| **Daily batch feasibility** | Yes (1500+ requests/day) | Yes (unlimited) | Tie |

### What Each Model UNIQUELY Offers

| Model | Unique Capability | Justifies Integration? |
|-------|------------------|----------------------|
| **Gemini 2.5 Pro** | 1M token context window for full 10-K filing analysis | **YES** -- if parsing SEC filings |
| **Gemini 2.5 Pro** | Google Search grounding for fact verification | **YES** -- for verifying financial claims |
| **GPT-5.4 (Codex)** | `--output-schema` JSON Schema validation | **MODERATE** -- useful but Claude can output JSON too |
| **GPT-5.4 (Codex)** | 2.5s latency for fast classification | **MODERATE** -- matters for real-time, not batch |
| **GPT-5.4 (Codex)** | Web search integration (`--search` flag) | **YES** -- for current market data |
| **Claude** | Best reasoning and synthesis | **YES** -- orchestrator role |
| **Claude** | Best Korean language capability | **YES** -- Korean market reports |

### Recommendation

**Start with Branch 2.2 (Single-Model), graduate to Branch 2.1 (Multi-Model) for specific tasks.**

**Phase 1 (Month 1-2)**: Claude-only pipeline. Simple, reliable, fast to build.

**Phase 2 (Month 3+)**: Add Gemini CLI for:
- 10-K filing analysis (when context exceeds 200K tokens)
- Fact verification of financial claims
- Cross-model validation of high-stakes recommendations

**Phase 3 (Month 4+)**: Add Codex CLI for:
- Structured classification outputs with schema validation
- Current market data via web search
- Speed-critical classification tasks

### The Pragmatic Answer

> Multi-model is worth it when: (a) you are parsing documents >200K tokens (10-K filings), OR (b) you need cross-model validation for high-confidence recommendations, OR (c) you need current web data that Claude cannot access.
>
> Multi-model is NOT worth it when: you are doing standard financial metric analysis on <100 stocks with readily available data. Claude alone handles this perfectly.

---

## Part G: Integration with workflow.md

### For Multi-Model Workflow Steps

```yaml
# In workflow.md, a step using multi-model:
- id: analyze-stock
  name: "Multi-Model Stock Analysis"
  type: script
  script: |
    python3 scripts/multi_model_analyzer.py \
      --ticker $TICKER \
      --data-file $DATA_FILE \
      --output-dir $OUTPUT_DIR
  models:
    gemini: "gemini-2.5-pro"   # Historical context (OAuth subscription)
    codex: "gpt-5.4"           # Structured classification (ChatGPT subscription)
    claude: "orchestrator"      # Synthesis (current session)
  auth: "subscription-only"     # NO API keys
```

### For Claude Code Hook Integration

The multi-model calls can be integrated into the existing hook system:
```python
# In a Claude Code hook or script:
import subprocess, json

def get_gemini_analysis(prompt):
    """Called from Claude Code hook -- uses Gemini subscription."""
    result = subprocess.run(
        ["gemini", "-p", prompt, "-o", "json", "-m", "gemini-2.5-pro"],
        capture_output=True, text=True, timeout=60
    )
    return json.loads(result.stdout)["response"] if result.returncode == 0 else None

def get_codex_classification(prompt):
    """Called from Claude Code hook -- uses ChatGPT subscription."""
    result = subprocess.run(
        ["npx", "@openai/codex", "exec", prompt],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout.strip() if result.returncode == 0 else None
```

---

## Appendix: Verified Test Results (2026-03-28)

### Test 1: Gemini CLI Subprocess (Python)
```
Input:  "Analyze S&P 500 at 5800. Historical context in 2 sentences."
Model:  gemini-2.5-pro (routed through gemini-2.5-flash-lite + gemini-3-flash-preview)
Auth:   OAuth (Google subscription, oauth-personal)
Time:   28.4s
Output: "Nominally, 5800 is an all-time historical high... current multiples
         significantly exceed long-term mean price-to-earnings ratios."
```

### Test 2: Codex CLI Subprocess (Python)
```
Input:  "Analyze S&P 500 at 5800. Historical context in 2 sentences."
Model:  gpt-5.4
Auth:   ChatGPT subscription (auth_mode: chatgpt)
Time:   3.3s
Output: "Historically, 5,800 is high... far above pre-2024 norms and only
         modestly below the S&P 500's 2025 record highs of 6,173."
Bonus:  Codex performed live web search and cited actual 2025 market data!
```

### Test 3: Multi-Model Orchestration
```
Pipeline: Gemini (historical) → Codex (classification) → Claude (synthesis)
Total time: ~32s for complete 3-model analysis
All auth: subscription-only, zero API keys
Result: Successfully combined perspectives from all three models
```

### Test 4: Gemini File Analysis
```
Input:  @/tmp/test_stock_data.json (AAPL data)
Auth:   OAuth subscription
Result: Successfully read and analyzed JSON file content
```

### Test 5: Codex Structured Output
```
Input:  "Classify AAPL" with structured prompt
Output: {"verdict":"fairly_valued","confidence":0.65,"key_factor":"..."}
Auth:   ChatGPT subscription
```

### Test 6: Codex MCP Server Protocol
```
Command: codex mcp-server
Protocol: JSON-RPC 2.0, MCP protocol version 2024-11-05
Tools exposed: "codex" (new session), "codex-reply" (continue conversation)
Auth: Inherits ChatGPT subscription from parent process
```
