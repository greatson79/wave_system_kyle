# INVESTSCAN — Project Memory (Agent Onboarding)

> Single-file SOT for agent onboarding. Read this first — enables full context in <2 minutes.
> Last updated: 2026-03-29 | M0.5 ACHIEVED (437 tests passing, all 8 DG gates green)

---

## 1. Purpose

InvestScan is a weekly Korean stock analysis pipeline that:
1. Collects environmental signals (FRED macro, GNews sentiment, EnvironmentScan)
2. Synthesizes macro context + selects stocks (Category A: fundamentals, B: growth themes)
3. Generates structured narrative (NarrativeOutput) via Reflect-Revise loop
4. Validates narrative deterministically (Python-First, P6)
5. Renders weekly report → translates to Korean → delivers via Telegram

**NOT a recommendation engine.** Purely analytical with explicit disclaimer enforcement.

---

## 2. Absolute Constraints (P1–P6)

| ID | Name | Rule |
|----|------|------|
| P1 | Data Refinement | Python cleans/validates data before LLM sees it |
| P2 | Expert Delegation | Orchestrator coordinates; modules own their domain |
| P3 | Resource Accuracy | No placeholder URLs/paths — exact paths only |
| P4 | Question Design | Max 4 questions, 3 options each |
| P5-A | English-First | Internal logic/prompts in English; user output in Korean |
| P6 | Python-First | Python is the judge, LLM is the narrator |

**BULLISH_THRESHOLD = 0.01** (+1%, v3.6 I-4) — from `investscan/stock_selector.py`
**sentiment_weight = 0.0** — ABSOLUTE SENTINEL. Any non-zero value = pipeline halt.

---

## 3. Module Map (23 modules)

```
investscan/
├── schema.py              # NarrativeOutput, PredictionRecord, NormalizedSignal (frozen dataclasses)
├── config.py              # YAML config loader — investscan.yaml
├── weekly_orchestrator.py # 🎯 MAIN PIPELINE — run_full_pipeline(), build_narrative_with_retry()
│
├── [Data Collection]
│   ├── normalizers.py     # normalize_envscan(), load_envscan_file() → NormalizedSignal
│   ├── signal_bridge.py   # Bridge EnvironmentScan → UnifiedSignal
│   ├── korea_signal_layer.py  # Korean market signals (KOSPI, foreign flow)
│   └── dedup.py           # Signal deduplication
│
├── [Synthesis]
│   ├── synthesize_macro.py    # synthesize() + load_fred_fixture() → macro context dict
│   ├── synthesize_stock.py    # Per-stock fundamental synthesis
│   ├── steeps_classifier.py   # STEEPS category classification
│   └── stock_selector.py      # BULLISH_THRESHOLD=0.01, select_stocks()
│
├── [Narrative & Validation]
│   ├── intelligence_engine.py # LLM narrative generation (mock in dry-run)
│   ├── validate_report_quality.py  # python_validate_first() — P6 gate
│   ├── compliance_filter.py   # 10-pattern compliance check (BLOCKED/PASS)
│   ├── citation_validator.py  # Citation accuracy validation
│   └── valuation_comparator.py  # PER/PBR vs sector comparison
│
├── [Report & Delivery]
│   ├── report_generator.py    # generate_report(), save_report(), _simple_render()
│   ├── telegram_notifier.py   # build_5line_summary(), send (dry-run in M0.5)
│   └── health_dashboard.py    # System health metrics
│
├── [Tracking]
│   ├── accuracy_tracker.py    # KS-1 dual-window (4-week prelim, 8-week final)
│   ├── watchdog.py            # Pipeline anomaly detection
│   └── personalizer.py        # User portfolio context
```

---

## 4. Pipeline Flow (run_full_pipeline)

```
Step 1: load config (investscan.yaml)
Step 2: normalize_envscan() → NormalizedSignal           [P1: Python validates]
Step 3: synthesize_macro() → {rate_direction, inflation_trend, risk_appetite, usd_strength}
Step 4: synthesize_stock() → per-stock fundamentals
Step 5: stock_selector.select_stocks() → Category A or B
Step 6: build_narrative_with_retry() → NarrativeOutput   [Reflect-Revise, MAX_RETRIES=3]
  └─ python_validate_first() → P6 gate
  └─ compliance_filter() → 10-pattern check
  └─ content_gate() → pre-translation structural validation
Step 7: generate_report() → Markdown string
Step 8: save_report() → output/reports/weekly-report-{date}.md  [atomic write]
Step 9: build_5line_summary() → Telegram dry-run
Step 10: _update_sot_on_success() → state.yaml atomic write
```

**content_gate() checks:**
- Category A: A1(text≥1000B), A2(per_vs_sector), A3(foreign_flow), A4(downside), A5(direction)
- Category B: B1(text≥1000B), B2(market_size), B3(catalyst), B4(theme_duration), B5(dissolution), B6(disclaimer)
- Common: C1(sentiment_weight==0.0), C2(category in {A,B})

---

## 5. SOT Hierarchy (3 Tiers)

| Tier | File | Owner | Purpose |
|------|------|-------|---------|
| 0 | `.claude/state.yaml` | Orchestrator only | Global milestone + tdd_status + translations |
| 1 | `.claude/state/phase-*.yaml` | Phase lead | Per-phase progress |
| 2 | `.claude/agent-workspace/*.yaml` | Individual agents | Agent-local state |

**Atomic write pattern**: write to `.yaml.tmp` → `tmp.rename(target)` — all SOT writes.
**Parallel agents**: never write to the same file simultaneously.

---

## 6. M0.5 Status — ACHIEVED ✅

| Gate | Description | Status |
|------|-------------|--------|
| DG-01 | Config loads, BULLISH_THRESHOLD=0.01 | ✅ PASS |
| DG-02 | normalize_envscan() produces NormalizedSignal | ✅ PASS |
| DG-03 | synthesize_macro() returns valid labels | ✅ PASS |
| DG-04 | NarrativeOutput sentinel=0.0, text≥1000B | ✅ PASS |
| DG-05 | compliance_filter() 10 patterns: PASS+BLOCKED | ✅ PASS |
| DG-06 | build_5line_summary() dry-run | ✅ PASS |
| DG-07 | run_full_pipeline() dry-run succeeds | ✅ PASS |
| DG-08 | state.yaml written atomically, m05_ready=True | ✅ PASS |

Translation Done Gates (TDG-01~06): ✅ All passing
- blueprint.ko.md (pACS 88), completion-definition.ko.md (pACS 85), schema-mapping.ko.md (pACS 90)

**Test count**: 437 passing, 0 failing (run: `python -m pytest tests/ -q`)

---

## 7. TDD Status

| Module | Tests | Status |
|--------|-------|--------|
| citation_validator | test_citation_validator.py | ✅ passing |
| compliance_filter | test_compliance_filter.py | ✅ passing |
| config | test_config.py | ✅ passing |
| dedup | test_dedup.py | ✅ passing |
| intelligence_engine | test_intelligence_engine.py | ✅ passing |
| korea_signal_layer | test_korea_signal_layer.py | ✅ passing |
| normalizers | test_normalizers.py | ✅ passing |
| report_generator | test_report_generator.py | ✅ passing |
| signal_bridge | test_signal_bridge.py | ✅ passing |
| steeps_classifier | test_steeps_classifier.py | ✅ passing |
| stock_selector | test_stock_selector.py | ✅ passing |
| synthesize_macro | test_synthesize_macro.py | ✅ passing |
| synthesize_stock | test_synthesize_stock.py | ✅ passing |
| validate_report_quality | test_validate_report_quality.py | ✅ passing |
| valuation_comparator | test_valuation_comparator.py | ✅ passing |
| weekly_orchestrator | test_weekly_orchestrator.py | ✅ passing |
| **accuracy_tracker** | ❌ MISSING | pending |
| **schema** | ❌ MISSING | pending |
| **watchdog** | ❌ MISSING | pending |

---

## 8. Key Files for New Agents

| Task | Read First |
|------|-----------|
| Pipeline change | `investscan/weekly_orchestrator.py` |
| Schema change | `investscan/schema.py` |
| Add validation rule | `investscan/validate_report_quality.py` + `investscan/compliance_filter.py` |
| Report template | `templates/weekly-report.md.j2` |
| Config reference | `investscan.yaml` + `config/sector_stock_map.yaml` |
| Accuracy tracking | `investscan/accuracy_tracker.py` |
| SOT inspection | `.claude/state.yaml` |
| M0.5 gate runner | `run_m05.py` (CLI: `python run_m05.py --dry-run`) |

---

## 9. Critical Identifiers (Must NOT be translated)

- `NarrativeOutput` — core output schema
- `sentiment_weight` — absolute sentinel field (must be 0.0)
- `DG-01` through `DG-16` — done gate IDs
- `TDG-01` through `TDG-06` — translation done gate IDs
- `M0.5`, `M1` — milestone identifiers
- `BULLISH_THRESHOLD` — stock selection threshold constant
- `UnifiedSignal`, `NormalizedSignal` — data pipeline types
- `steeps_category`, `pSST` — EnvironmentScan schema fields
- `KS-1` — accuracy measurement standard

---

## 10. Agent Swarm Architecture (3+5+2+1)

```
Research Swarm (3):
  ├── envscan-subagent    → .claude/agents/envscan-subagent.md
  ├── fred-subagent       → .claude/agents/fred-subagent.md
  └── gnews-subagent      → .claude/agents/gnews-subagent.md

Implementation Swarm (5 Forks A-E):
  ├── Fork A: data pipeline (normalizers, signal_bridge)
  ├── Fork B: synthesis (synthesize_macro, synthesize_stock)
  ├── Fork C: narrative (intelligence_engine, validate_report_quality)
  ├── Fork D: report (report_generator, templates)
  └── Fork E: delivery (telegram_notifier, accuracy_tracker)

Review Swarm (2):
  ├── reviewer            → .claude/agents/reviewer.md (adversarial, pACS)
  └── fact-checker        → .claude/agents/fact-checker.md

Translation (1):
  └── translator          → .claude/agents/translator.md (glossary: translations/glossary.yaml)
```

Orchestrator: `.claude/agents/investscan-orchestrator.md`

---

## 11. M1 Milestone (Next Target)

DG-09~16 cover: full HITL flow, live API integration, portfolio comparison, accuracy baseline,
agent team parallel execution, phase sequencing, HITL-2 approval, production delivery.

**Prerequisite**: HITL-1 (user provides API keys + sector confirmation via `/approve-hitl`).
