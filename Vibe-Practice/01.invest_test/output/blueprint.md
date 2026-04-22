# InvestScan System Blueprint
**Step 5 Output** | Generated: 2026-03-29 | Language: English (P5-A)

---

## System Architecture

```
User (Korean) ←→ Claude Code Session (Orchestrator)
                        │
          ┌─────────────┼─────────────┐
          │             │             │
   Research Fork    Module Forks   Translation
   (Stage 1)        (Stage 2)      Fork (@translator)
          │             │             │
   ┌──────┼──────┐  ┌───┼───┐     Korean .ko.md
   │      │      │  │   │   │     pACS logs
 FRED  EnvScan GNews Fork Fork Fork
              │    A   B   C
              └─────────────── Fork D → Fork E
```

### Agent Swarm: 3+5+2+1

| Role | Count | Agents |
|------|-------|--------|
| Research | 3 | envscan-agent, fred-agent, gnews-agent |
| Implementation | 5 | builder-a/b/c/d/e |
| Review | 2 | code-reviewer, fact-checker |
| Translation | 1 | @translator |

---

## Data Flow

```
EnvironmentScan DB → normalizers.py → UnifiedSignal[]
                                            │
FRED API ──────────→ synthesize_macro.py → InvestmentMeta
                                            │
GlobalNews Parquet → signal_bridge.py ──→ {sector: signals[]}
                           │
                     dedup.py (content-hash)
                           │
                   steeps_classifier.py (keyword lookup)
                           │
KRX/DART ──────────→ korea_signal_layer.py → KoreaSignal
                           │
                   stock_selector.py (numeric thresholds)
                    category A or B
                           │
                   synthesize_stock.py → context_data dict
                           │
                   intelligence_engine.py (LLM)
                    → NarrativeOutput (English)
                           │
              ┌────────────┼────────────┐
              │            │            │
    validate_report   compliance_   citation_
    _quality.py       filter.py     validator.py
    (Python 8-criteria) (10 patterns) (Python)
              │
    report_generator.py → weekly-report-{date}.md
              │
         @translator → weekly-report-{date}.ko.md
              │
    accuracy_tracker.py → PredictionRecord
              │
    Telegram (Korean 5-line summary)
```

---

## Module Responsibilities (P6: Python-First)

| Module | Decision Type | LLM Involved? |
|--------|--------------|---------------|
| steeps_classifier.py | Keyword classification | NO |
| compliance_filter.py | Regex prohibition check | NO |
| stock_selector.py | Numeric category threshold | NO |
| synthesize_macro.py | Rule-based macro synthesis | NO |
| citation_validator.py | Number cross-validation | NO |
| validate_report_quality.py | Regex 8-criteria (1st pass) | 2nd pass only |
| intelligence_engine.py | Text generation | YES (narrative only) |
| @translator | Korean translation | YES (text only) |

---

## SOT Hierarchy (D1)

```
Tier 0: .claude/state.yaml          ← Orchestrator-only write
  └── Tier 1: .claude/state/phase-*.yaml  ← Phase Lead write
        └── Tier 2: .claude/agent-workspace/*.yaml  ← SubAgent self-write only
```

All writes: atomic `tmp → rename` pattern. All keys/values: English (P5-A).

---

## Dry-Run Mode

When `investscan.yaml` mode = `dry-run`:
- API keys: MOCK_ prefixed dummy values
- Data paths: `tests/fixtures/` instead of live APIs
- LLM calls: can be monkeypatched in tests
- Telegram: print to stdout instead of sending
- `run_m05.py --dry-run` verifies DG-01~08 without any external connections

This allows full pipeline verification without real API keys.

---

## Accuracy Tracking (v3.6 I-3)

| Window | Purpose | KS-1 Basis |
|--------|---------|-----------|
| 4-week | Preliminary reading | No |
| 8-week | Final measurement | YES |

KS-1 label: "Month 3 data basis" (measurement lag accounted — v3.6 I-5).
Naive Baselines: Always-Bullish + Momentum + Random (v3.6 I-13).

---

## Bear Case UX (v3.6 I-12)

Bear Case section position: **bottom of report** (above disclaimer only).
This prevents decision paralysis for onboarding users.
Telegram 5-line summary: Bear Case NOT included (brevity principle).

---

*This blueprint is the canonical system design reference. Architectural deviations require ADR documentation.*
