# InvestScan -- Monolithic/Fast-Ship Architecture Analysis

**Architect Role**: Monolithic/Fast-Ship Tech Architect
**Date**: 2026-03-27
**Target**: Single MacBook M5 Max, 64GB RAM, 18 cores (6 Super + 12 Performance)

---

## 1. Architecture Strategy

### 1.1 Integration Approach: Sequential Pipeline with File-Based IPC

The two source systems are architecturally complementary, not overlapping:

| Dimension | EnvironmentScan (EnvScan) | GlobalNews-Crawling (GNC) |
|-----------|---------------------------|---------------------------|
| **Signal source** | arXiv, blogs, policy docs, patents, Naver News, 32+ global news sites | 116 international news sites, 14+ languages |
| **Processing** | Claude Code agents (LLM-driven analysis) | Local ML pipeline (SBERT, BERTopic, Prophet, PCMCI) |
| **Signal schema** | JSON: `{id, title, source, content, metadata, preliminary_category, pSST_score}` | Parquet: `{signal_id, signal_layer (L1-L5), burst_score, novelty_score, singularity_composite, confidence}` |
| **Classification** | STEEPs categories (S, T, E, E, P, s) + pSST 0-100 score | 5-Layer hierarchy (L1_fad to L5_singularity) + 56 quantitative techniques |
| **Output** | Markdown reports + JSON signals database (~833KB) | Parquet (ZSTD) + SQLite (FTS5+vec) + DuckDB |
| **API cost** | Moderate (Claude API calls for agent reasoning) | Zero (all local ML inference) |

**Proposed unified pipeline:**

```
Phase 1: Data Collection (parallel where possible)
  EnvScan WF1-WF4 (sequential, ~2hr) ──┐
                                         ├──> Phase 2: Signal Merge Layer
  GlobalNews crawl+analyze (~1.5hr)  ───┘
                                         │
Phase 3: Investment Signal Synthesis  <──┘
  ├── Cross-source signal correlation
  ├── Korean market investment direction mapping
  ├── Sector/asset class impact scoring
  └── Conviction level calculation

Phase 4: Report Generation
  ├── Investment direction report (EN + KO)
  ├── Sector heat map
  └── Risk/opportunity matrix
```

### 1.2 Data Flow Architecture

```
EnvScan Output:                        GlobalNews Output:
  signals/database.json                  data/output/signals.parquet
  output/WF*_signals_*.json              data/output/analysis.parquet
  integrated/analysis/*.json             data/output/index.sqlite
  integrated/reports/daily/*.md          data/output/topics.parquet
          │                                        │
          ▼                                        ▼
  ┌─────────────────────────────────────────────────┐
  │         Signal Normalization Layer (NEW)         │
  │  - Schema harmonization (JSON ←→ Parquet)        │
  │  - STEEPs ←→ L1-L5 cross-mapping                │
  │  - pSST ←→ confidence score normalization        │
  │  - Temporal alignment (same date window)         │
  │  - Cross-source deduplication (title similarity) │
  └─────────────────────┬───────────────────────────┘
                        ▼
  ┌─────────────────────────────────────────────────┐
  │      Investment Signal Synthesizer (NEW)         │
  │  - Sector classification (GICS or custom)        │
  │  - Asset class mapping                           │
  │  - Korean market relevance scoring               │
  │  - Directional conviction (bull/bear/neutral)    │
  │  - Convergence detection (multiple sources)      │
  └─────────────────────┬───────────────────────────┘
                        ▼
  ┌─────────────────────────────────────────────────┐
  │         Report Generator (NEW)                   │
  │  - Investment direction summary                  │
  │  - Sector heat map (matplotlib/plotly)           │
  │  - Risk/opportunity matrix                       │
  │  - Signal evidence trail                         │
  │  - KO translation (reuse EnvScan translator)     │
  └─────────────────────────────────────────────────┘
```

### 1.3 File-Based IPC: The Fast-Ship Choice

Instead of building a shared database or message queue, both systems write to their existing output directories. The new InvestScan layer reads from those directories:

```python
# investscan/config.py
ENVSCAN_ROOT = Path("../EnvironmentScan-system-main-v4-main")
GNEWS_ROOT = Path("../GlobalNews-Crawling-AgenticWorkflow")

ENVSCAN_SIGNALS = ENVSCAN_ROOT / "env-scanning/signals/database.json"
ENVSCAN_DAILY_OUTPUT = ENVSCAN_ROOT / "output/"
ENVSCAN_INTEGRATED = ENVSCAN_ROOT / "env-scanning/integrated/"

GNEWS_SIGNALS = GNEWS_ROOT / "data/output/signals.parquet"
GNEWS_ANALYSIS = GNEWS_ROOT / "data/output/analysis.parquet"
GNEWS_TOPICS = GNEWS_ROOT / "data/output/topics.parquet"
```

This is the fastest path to shipping. Zero changes to either source system.

---

## 2. Technical Feasibility

### 2.1 Machine Resources

**Hardware**: Apple M5 Max, 64GB unified memory, 18 CPU cores

| Resource | EnvScan Demand | GlobalNews Demand | Concurrent Peak | Available | Verdict |
|----------|---------------|-------------------|-----------------|-----------|---------|
| **RAM** | ~4-6 GB (Python + SBERT model) | ~10 GB peak (Stage 2: SBERT + PyTorch) | ~16 GB if sequential | 64 GB | VERY COMFORTABLE |
| **CPU** | Moderate (4 parallel scan agents) | Heavy (SBERT batch, BERTopic, Prophet) | 12-14 cores | 18 cores | COMFORTABLE |
| **Disk I/O** | Low (JSON reads/writes) | Moderate (Parquet I/O, ~500MB) | Sequential = fine | NVMe SSD | NO ISSUE |
| **GPU (MPS)** | Not used | PyTorch MPS for SBERT/BERTopic | Shared | M5 Max GPU | FINE |
| **Network** | Heavy (web scraping + Claude API) | Heavy (116 site crawling) | Bottleneck if parallel | Home internet | SEQUENTIAL PREFERRED |

**Memory analysis for concurrent execution (if desired later)**:
The original GlobalNews was designed for M2 Pro 16GB with a 10GB budget. On 64GB M5 Max, even concurrent execution is feasible. However, network I/O is the bottleneck for both systems (web scraping), so **sequential execution is optimal** for MVP -- there is no speed benefit to concurrent crawling because you would saturate the network connection and trigger more anti-bot measures.

### 2.2 Time Budget

| Phase | Duration | Notes |
|-------|----------|-------|
| EnvScan quad scan (WF1-WF4) | ~120 min | Sequential, Claude API dependent |
| GlobalNews crawl | ~53 min | 116 sites, rate-limited |
| GlobalNews analyze (8 stages) | ~45 min | CPU-bound, local ML |
| **Signal Normalization** (NEW) | ~2 min | JSON/Parquet reads, schema mapping |
| **Investment Synthesis** (NEW) | ~5-10 min | Classification + scoring, mostly rule-based |
| **Report Generation** (NEW) | ~3-5 min | Template fill + optional charts |
| **Total** | **~230-240 min (~4 hours)** | |

This is acceptable for a daily batch run. A scheduled 6:00 AM start finishes by 10:00 AM.

### 2.3 Claude Code workflow.md as Sole Orchestrator

The workflow.md will serve as the orchestration script, executed by Claude Code. This is feasible because:

1. **EnvScan already uses Claude Code slash commands** (`/env-scan:run`). The workflow.md can invoke these.
2. **GlobalNews has a clean CLI**: `python main.py --mode full --date YYYY-MM-DD`. Bash invocation from workflow.md.
3. **New modules** (normalization, synthesis, report gen) will be pure Python scripts, also invoked via Bash.

**Orchestration flow in workflow.md:**

```
Step 1: Run EnvironmentScan
  (bash) cd ../EnvironmentScan-system-main-v4-main && /env-scan:run --quad
  Wait for completion, check exit code

Step 2: Run GlobalNews
  (bash) cd ../GlobalNews-Crawling-AgenticWorkflow
  (bash) .venv/bin/python main.py --mode full --date $(date +%Y-%m-%d)
  Wait for completion, check exit code

Step 3: Signal Normalization
  (bash) cd ../01.invest_test
  (bash) python invest_pipeline/normalize_signals.py --date $(date +%Y-%m-%d)

Step 4: Investment Synthesis
  (bash) python invest_pipeline/synthesize_investment.py --date $(date +%Y-%m-%d)

Step 5: Report Generation
  (bash) python invest_pipeline/generate_report.py --date $(date +%Y-%m-%d)
  (Claude) Review and refine report narrative
  (Claude) Translate to Korean using @translator pattern
```

### 2.4 New Modules to Build

| Module | Purpose | Complexity | Estimated LOC |
|--------|---------|------------|---------------|
| `normalize_signals.py` | Read both signal formats, harmonize into unified schema | Medium | ~400 |
| `schema.py` | Unified signal data classes + Parquet schema | Low | ~150 |
| `synthesize_investment.py` | Map signals to sectors, score directions, compute conviction | High | ~800 |
| `sector_mapper.py` | STEEPs/L1-L5 to GICS sector mapping rules | Medium | ~300 |
| `korean_market_scorer.py` | Korea-specific market relevance scoring | Medium | ~400 |
| `generate_report.py` | Markdown report generation from synthesis output | Medium | ~500 |
| `config.py` | Path configs, thresholds, sector definitions | Low | ~100 |
| `utils.py` | Shared utilities (date handling, Parquet I/O) | Low | ~150 |
| **Total new code** | | | **~2,800 LOC** |

---

## 3. MVP Scope (6-Month Timeline)

### 3.1 Month-by-Month Development Plan

#### Month 1 (Weeks 1-4): Foundation + Pipeline Skeleton

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W1 | Project scaffolding, config, schema definitions, `config.py` + `schema.py` | 1 week |
| W2 | `normalize_signals.py` -- EnvScan JSON reader + parser | 1 week |
| W3 | `normalize_signals.py` -- GlobalNews Parquet reader + unified schema mapping | 1 week |
| W4 | End-to-end test: both systems run, normalization produces unified output | 1 week |

**Milestone**: Unified signal dataset from both systems (JSON file).

#### Month 2 (Weeks 5-8): Investment Signal Synthesis Core

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W5 | `sector_mapper.py` -- STEEPs category to GICS sector mapping | 1 week |
| W6 | `synthesize_investment.py` -- directional scoring (bull/bear/neutral) | 1 week |
| W7 | `korean_market_scorer.py` -- Korea relevance scoring + KOSPI/KOSDAQ sector weights | 1 week |
| W8 | Conviction level calculation + cross-source convergence detection | 1 week |

**Milestone**: Investment direction signals with sector assignments and conviction levels.

#### Month 3 (Weeks 9-12): Report Generation + Orchestration

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W9 | `generate_report.py` -- Markdown report template + data injection | 1 week |
| W10 | Report enrichment: sector heat map visualization (matplotlib) | 1 week |
| W11 | `workflow.md` -- Full orchestration script, end-to-end automation | 1 week |
| W12 | Korean translation integration (reuse EnvScan's @translator pattern) | 1 week |

**Milestone**: First fully automated daily run producing English + Korean investment reports.

#### Month 4 (Weeks 13-16): Quality + Signal Intelligence

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W13 | Cross-source deduplication (title similarity + entity overlap) | 1 week |
| W14 | Signal strength aggregation (pSST + GlobalNews confidence fusion) | 1 week |
| W15 | Historical signal tracking (investment direction evolution over time) | 1 week |
| W16 | Backtesting framework skeleton (compare past signals vs actual market moves) | 1 week |

**Milestone**: Production-quality signal merging with dedup and historical tracking.

#### Month 5 (Weeks 17-20): Advanced Analysis + Refinement

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W17 | Risk/opportunity matrix generation | 1 week |
| W18 | Sector rotation signal detection (cross-temporal pattern) | 1 week |
| W19 | Portfolio implication summaries (which sectors to overweight/underweight) | 1 week |
| W20 | Anomaly alerts (L5_singularity signals + pSST spikes) | 1 week |

**Milestone**: Advanced investment analytics beyond basic direction scanning.

#### Month 6 (Weeks 21-24): Hardening + Documentation

| Week | Deliverable | Dev Time |
|------|-------------|----------|
| W21 | Error handling, retry logic, graceful degradation | 1 week |
| W22 | Scheduled execution (cron/launchd for daily automated runs) | 1 week |
| W23 | User documentation + configuration guide | 1 week |
| W24 | Buffer week for bugs, edge cases, final polish | 1 week |

**Milestone**: Production-ready system running daily on schedule.

### 3.2 Feature Priority Matrix

| Feature | Priority | Month | Cut if Needed? |
|---------|----------|-------|----------------|
| Signal normalization (both sources) | P0 (must have) | 1 | NO |
| Sector mapping + direction scoring | P0 (must have) | 2 | NO |
| Basic report generation | P0 (must have) | 3 | NO |
| Full workflow.md orchestration | P0 (must have) | 3 | NO |
| Cross-source deduplication | P1 (should have) | 4 | Degrade to simple title match |
| Signal confidence fusion (pSST + GNC) | P1 (should have) | 4 | Use simple average |
| Historical signal tracking | P1 (should have) | 4 | Cut entirely |
| Korean translation | P1 (should have) | 3 | Delay to Month 5 |
| Backtesting framework | P2 (nice to have) | 4 | CUT FIRST |
| Risk/opportunity matrix | P2 (nice to have) | 5 | Cut if behind |
| Sector rotation detection | P2 (nice to have) | 5 | Cut if behind |
| Portfolio implications | P2 (nice to have) | 5 | Cut if behind |
| Anomaly alerts | P2 (nice to have) | 5 | Cut if behind |
| Scheduled execution (cron) | P1 (should have) | 6 | Manual daily run instead |
| Visualization (heat maps) | P2 (nice to have) | 3 | Text-only reports |

### 3.3 Parallel Development Opportunities

```
Month 1-2: Sequential (Foundation must come first)

Month 3 onward: Parallelizable tracks
  Track A: Report Generation + Visualization
  Track B: Orchestration + Automation
  Track C: Quality (dedup, confidence fusion)

If you recruit a second developer:
  Developer 1: Tracks A+B (pipeline + orchestration)
  Developer 2: Track C (signal quality + advanced analytics)
```

---

## 4. Technical Debt Assessment

### 4.1 Acceptable Shortcuts for Fast Shipping

| Shortcut | Why Acceptable | Debt Level |
|----------|---------------|------------|
| **File-based IPC** (JSON/Parquet files on disk) | Zero coupling to source systems. Works immediately. | LOW -- This is actually good architecture for batch processing |
| **Rule-based sector mapping** (hardcoded STEEPs-to-sector rules) | 80% accuracy is fine for v1. ML classification later. | MEDIUM -- Will need ML model eventually |
| **Simple averaging** for confidence fusion | pSST (0-100) and GNC confidence (0-1) use different scales. Linear normalization + average is good enough. | LOW -- Proper Bayesian fusion is over-engineered for MVP |
| **No shared database** -- each system keeps its own DB | Source systems are unchanged. InvestScan reads from both. | LOW -- Actually reduces coupling |
| **Sequential execution** (not parallel) | Network I/O is the bottleneck. Parallel crawling adds complexity + anti-bot risk. | LOW -- Correct for current constraints |
| **Markdown-only reports** (no web dashboard) | User is a Claude Code user who reads Markdown natively. | NONE -- This is the right choice |
| **No authentication/multi-user** | Single-user local system. | NONE -- Would be over-engineering |
| **Hardcoded Korean market focus** | User's primary market. Global expansion later. | LOW -- Easy to parameterize later |

### 4.2 Where Debt Will Accumulate

| Debt Area | When It Becomes Painful | Estimated Refactoring Cost |
|-----------|------------------------|---------------------------|
| **Sector mapper (rules to ML)** | When rule-based accuracy drops below 70% on novel signals | 2-3 weeks (train SetFit model, integrate) |
| **No backtesting validation** | When user asks "were past signals accurate?" | 3-4 weeks (historical data collection + comparison framework) |
| **No incremental processing** | When daily runs take >5 hours due to data growth | 1-2 weeks (add date-windowed processing, skip unchanged signals) |
| **No web UI/dashboard** | If user wants to share reports with others | 4-6 weeks (but NOT needed for solo user) |
| **Monolithic pipeline script** | When adding new signal sources or analysis types | 1-2 weeks (refactor to plugin architecture) |
| **EnvScan's Claude API dependency** | If API costs grow or rate limits tighten | 2-3 weeks (partial local ML migration) |

### 4.3 Total Debt Summary

**Debt Risk Level: LOW-MEDIUM**

The monolithic/file-based approach generates surprisingly little technical debt because:
1. Both source systems are already well-structured with clean interfaces
2. File-based IPC is the _correct_ architecture for daily batch processing
3. The new code (~2,800 LOC) is small enough to refactor entirely if needed
4. The 64GB machine eliminates memory-related shortcuts

---

## 5. Technical Risks (Top 3)

### Risk 1: EnvScan Claude API Reliability + Cost

**Assumption**: Claude API remains available, affordable, and fast enough for daily quad scans.

| Attribute | Assessment |
|-----------|------------|
| **Probability** | MEDIUM (25-35%) -- API outages, rate limits, cost increases are real |
| **Impact** | HIGH -- EnvScan produces ~60% of the signal diversity (arXiv, patents, policy, Naver, specialized blogs). Without it, GlobalNews alone provides only mass-market news coverage |
| **Mitigation** | 1. GlobalNews can run independently as fallback (still produces investment signals, just less diverse). 2. EnvScan has existing retry logic. 3. Build the synthesis layer to produce useful output even with only one source system's data. 4. Long-term: migrate EnvScan's LLM-dependent analysis to local models (Mistral/Llama via Ollama) |
| **Mitigation cost** | Low (graceful degradation in synthesis layer is ~1 day of work) |

### Risk 2: Signal Schema Drift Between Source Systems

**Assumption**: Both systems' output schemas remain stable during InvestScan development.

| Attribute | Assessment |
|-----------|------------|
| **Probability** | MEDIUM (30%) -- Both systems are actively developed |
| **Impact** | MEDIUM -- Schema changes break normalization layer, but are detectable and fixable |
| **Mitigation** | 1. `normalize_signals.py` validates schema on every run (fail-fast with clear error). 2. Use defensive parsing (`.get()` with defaults, not direct key access). 3. Pin source system versions in documentation. 4. Add schema version detection that warns about unexpected fields |
| **Mitigation cost** | Low (good engineering practice, included in Month 1 work) |

### Risk 3: Investment Signal Quality is Unvalidatable Without Backtesting

**Assumption**: Rule-based sector mapping and conviction scoring produces actionable investment directions.

| Attribute | Assessment |
|-----------|------------|
| **Probability** | HIGH (50-60%) -- Rule-based NLP-to-investment mapping has inherent accuracy limits |
| **Impact** | HIGH -- If output signals are not meaningfully correlated with actual market movements, the entire system's value proposition collapses |
| **Mitigation** | 1. Start with conservative conviction levels (never output "strong conviction" without multi-source convergence). 2. Include explicit uncertainty bands in all reports. 3. Prioritize Month 4's backtesting framework to validate against KOSPI sector data. 4. Human-in-the-loop: user reviews every report before acting |
| **Mitigation cost** | Medium (backtesting framework is 3-4 weeks but provides existential validation) |

### Risk Matrix Summary

```
           HIGH Impact      │
                             │
    Risk 3 ●                 │  Risk 1 ●
    (Signal Quality)         │  (API Reliability)
                             │
                             │  Risk 2 ●
                             │  (Schema Drift)
           LOW Impact        │
    ─────────────────────────┼─────────────────────
           LOW Probability        HIGH Probability
```

---

## 6. Conclusions

### 6.1 6-Month Realistic MVP Feature List

**Guaranteed (P0, Months 1-3)**:
- Unified signal ingestion from EnvironmentScan (4 workflows) + GlobalNews (116 sites)
- Signal normalization: STEEPs + pSST + L1-L5 + GNC confidence into unified schema
- Sector mapping (STEEPs/signals to Korean market sectors)
- Investment direction scoring (bull/bear/neutral with conviction levels)
- Automated Markdown report generation (EN + KO)
- Full workflow.md orchestration (one-command daily run)

**Likely (P1, Months 4-5)**:
- Cross-source deduplication
- Signal confidence fusion (pSST + GNC confidence)
- Historical signal tracking and evolution
- Scheduled daily execution (cron/launchd)

**Stretch (P2, Month 5-6)**:
- Sector heat map visualization
- Risk/opportunity matrix
- Backtesting framework (signal accuracy validation)
- Anomaly alerts for L5_singularity events

### 6.2 Architecture Recommendation

**MONOLITHIC SEQUENTIAL PIPELINE with FILE-BASED IPC.**

Specific structure:

```
01.invest_test/
├── CLAUDE.md
├── workflow.md                       ← Claude Code orchestration script
├── invest_pipeline/
│   ├── __init__.py
│   ├── config.py                     ← Paths, thresholds, sector definitions
│   ├── schema.py                     ← Unified signal data classes
│   ├── normalize_signals.py          ← Read + harmonize both signal formats
│   ├── sector_mapper.py              ← STEEPs/L1-L5 → GICS sector mapping
│   ├── korean_market_scorer.py       ← Korea-specific relevance scoring
│   ├── synthesize_investment.py      ← Direction scoring + conviction
│   ├── generate_report.py            ← Markdown report + heat map
│   └── utils.py                      ← Shared utilities
├── config/
│   ├── sectors.yaml                  ← Sector definitions + keywords
│   ├── korean_market.yaml            ← KOSPI/KOSDAQ sector weights
│   └── thresholds.yaml               ← Scoring thresholds
├── output/
│   └── {date}/
│       ├── unified_signals.json
│       ├── investment_synthesis.json
│       ├── invest-report-{date}.md
│       └── invest-report-{date}-ko.md
└── tests/
    ├── test_normalize.py
    ├── test_sector_mapper.py
    └── test_synthesize.py
```

### 6.3 Tech Debt Risk: LOW-MEDIUM

The monolithic approach is actually the _right_ architecture for this use case:
- Daily batch processing (not real-time)
- Single user on a single machine
- Well-defined input boundaries (both source systems have stable output formats)
- Small new codebase (~2,800 LOC) that is easy to refactor

### 6.4 Refactoring Plan

| Trigger | Action | Timeline | Estimated Effort |
|---------|--------|----------|-----------------|
| **Month 7+**: Signal accuracy below 60% in backtests | Replace rule-based sector mapper with ML (SetFit few-shot) | 2-3 weeks | Medium |
| **Month 9+**: Daily run exceeds 5 hours | Add incremental processing (skip unchanged signals) | 1-2 weeks | Low |
| **Month 12+**: New signal sources needed (Reddit, Twitter, etc.) | Refactor normalization into plugin architecture | 2 weeks | Medium |
| **IF needed**: Multi-user access required | Add Flask/FastAPI web layer + auth | 4-6 weeks | High |

### 6.5 Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **Sequential, not parallel execution** | Network I/O bottleneck. Parallel crawling triggers more anti-bot measures. No speed gain. |
| **File-based IPC, not shared database** | Zero changes to source systems. Correct for daily batch. Simplest possible integration. |
| **Rule-based mapping, not ML** | 80% accuracy for v1. ML requires training data we don't have yet. |
| **Markdown reports, not web dashboard** | User works in Claude Code terminal. Markdown is the native format. |
| **Korean market focus, not global** | User's primary market. Global expansion is a v2 feature. |
| **Claude Code workflow.md orchestration** | User's existing tool. Both source systems already integrate with Claude Code. |

---

## Appendix A: Signal Schema Harmonization Design

### EnvScan Signal (JSON)
```json
{
  "id": "TC-20260325-001",
  "title": "With $3.5B in fresh capital, Kleiner Perkins is going all in on AI",
  "source": {"name": "TechCrunch", "type": "blog", "tier": "base"},
  "published_date": "2026-03-25T00:47:20Z",
  "preliminary_category": "T_Technological",
  "summary": "..."
}
```

### GlobalNews Signal (Parquet)
```
signal_id:                 UUID string
signal_layer:              L1_fad | L2_short | L3_mid | L4_long | L5_singularity
signal_label:              Human-readable topic label
detected_at:               Timestamp (UTC)
topic_ids:                 List[int32]
article_ids:               List[string]
burst_score:               float32 (0-1)
changepoint_significance:  float32 (0-1)
novelty_score:             float32 (0-1)
singularity_composite:     float32 (0-1)
evidence_summary:          string
confidence:                float32 (0-1)
```

### Unified InvestScan Signal (proposed)
```json
{
  "signal_id": "IS-20260327-001",
  "source_system": "envscan|gnews",
  "source_signal_id": "TC-20260325-001",
  "title": "...",
  "summary": "...",
  "detected_at": "2026-03-27T10:00:00Z",

  "steeps_category": "T_Technological",
  "signal_layer": "L3_mid",
  "confidence": 0.78,
  "psst_score": 72,

  "investment": {
    "sectors": ["IT", "Financials"],
    "direction": "bullish",
    "conviction": 0.65,
    "korea_relevance": 0.80,
    "kospi_sectors": ["삼성전자", "카카오", "네이버"],
    "rationale": "..."
  },

  "evidence": {
    "source_count": 3,
    "sources": ["TechCrunch", "Wired", "Bloomberg"],
    "burst_score": 0.45,
    "novelty_score": 0.62
  }
}
```

## Appendix B: Execution Timeline for Daily Run

```
06:00  Start
06:00  Phase 1a: EnvScan WF1 (General)          [~30 min]
06:30  Phase 1b: EnvScan WF2 (arXiv)            [~30 min]
07:00  Phase 1c: EnvScan WF3 (Naver)            [~30 min]
07:30  Phase 1d: EnvScan WF4 (MultiGlobal)      [~30 min]
08:00  Phase 2a: GlobalNews Crawl                [~53 min]
08:53  Phase 2b: GlobalNews Analyze (8 stages)   [~45 min]
09:38  Phase 3:  Signal Normalization            [~2 min]
09:40  Phase 4:  Investment Synthesis            [~10 min]
09:50  Phase 5:  Report Generation               [~5 min]
09:55  Phase 6:  Korean Translation             [~5 min]
10:00  DONE -- Reports available in output/
```

Total wall time: ~4 hours. Fits a "before market open" (09:00 KST) schedule if started at 05:00 KST, or a "morning briefing" schedule if started at 06:00 KST.
