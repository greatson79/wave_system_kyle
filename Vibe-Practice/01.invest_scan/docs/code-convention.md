# InvestScan Code Convention

> Version: v3.6 | English-First (P5) compliant

## P5: English-First Code Authorship Principle

All internal logic, data structures, and system messages use English. User-facing delivery channels (Telegram, HITL prompts) may use Korean.

| Context | Language | Examples |
|---------|----------|---------|
| Variable / function / class names | English | `classify_category()`, `StockScore` |
| Comments and docstrings | English | `# compute weighted pSST score` |
| Log messages | English | `logger.info("Step 4 synthesis complete")` |
| Exception messages | English | `raise ValueError("pSST out of range [0, 100]")` |
| Config file keys and values | English | `rate_direction: hold` |
| Agent prompts and intermediate outputs | English | All `.claude/agents/*.md` prompts |
| User delivery (Telegram, HITL) | Korean allowed | `"이번 주 투자 인사이트입니다"` |

## CATEGORY_A/B_SYSTEM_PROMPT Language Principle (P5-A)

- `intelligence_engine.py` implements CATEGORY_A/B_SYSTEM_PROMPT in **English**
- All 5 required content items from workflow.md Step 5 must be preserved verbatim — **only the language changes to English**
- `NarrativeOutput.text` is generated in English
- Final Korean report is produced exclusively by `@translator` SubAgent

## P6: Python-First Decision Architecture

All classification, validation, and threshold judgments use deterministic Python code. LLM role is limited to text generation (`NarrativeOutput.text`).

| Module | Decision owner | LLM role |
|--------|---------------|----------|
| `steeps_classifier.py` | `keyword_lookup` table + `classify()` | None |
| `stock_selector.py` | Numeric threshold constants + `classify_category()` | None |
| `compliance_filter.py` | `PROHIBITION_PATTERNS` regex array + `scan()` | None |
| `validate_report_quality.py` | 8-criterion Python regex (1st pass) | Scoring only (2nd pass) |
| `citation_validator.py` | Python cross-validation vs `context_data` | None |
| `intelligence_engine.py` | N/A | `NarrativeOutput.text` generation |
| `@translator` | N/A | Korean translation |

**Principle**: "Python is the judge, LLM is the narrator."

## General Rules

| Category | Rule |
|----------|------|
| Python version | 3.11+ |
| Type hints | Required on all functions |
| Style | PEP 8 + Black, line length 100 |
| Shared dataclasses | `frozen=True, slots=True` |
| Sentiment weight | `sentiment_weight = 0.0` (immutable — never modified by code) |
| API keys | Never in plain text — environment variables only |
| SOT writes | Orchestrator only, atomic `tmp → rename` pattern |

## InvestScan-Specific Constants (centralized in `config.py`)

```python
# Threshold constants — Python-First (P6)
BULLISH_THRESHOLD = 0.01        # +1% (I-4: relaxed from +2%)
NEUTRAL_BAND = 0.03             # ±3%
MIN_WEEKS_TRACKED = 4           # I-7: Category B zero-guard
MIN_ABS_COUNT = 1               # I-7: absolute safety net
ACCURACY_WINDOW_PRELIMINARY = 4  # weeks (I-3)
ACCURACY_WINDOW_FINAL = 8        # weeks, KS-1 basis (I-3)

# Compliance — DO NOT modify without legal review
PROHIBITION_PATTERNS = [...]    # See compliance_filter.py H-1
```

## SOT Write Protocol

```python
# Correct: atomic write to state.yaml (Orchestrator only)
tmp = Path(".claude/state.yaml.tmp")
tmp.write_text(yaml.dump(data, allow_unicode=True))
tmp.rename(Path(".claude/state.yaml"))

# Forbidden: direct write from SubAgent
Path(".claude/state.yaml").write_text(...)  # BLOCKED by sot_write_guard.py
```
