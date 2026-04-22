# InvestScan: Overwhelming Superiority Architecture

**Architect**: Fast-Ship Tech Architect
**Date**: 2026-03-27
**Objective**: Design InvestScan to be overwhelmingly superior to AlphaSquare
**Hardware**: MacBook M5 Max 64GB, 18 cores

---

## Part 1: Architecture for Superiority -- The Investment Intelligence Pipeline

### 1.1 Current Assets Inventory (What Actually Exists)

Before designing, let us precisely measure what we have:

**EnvironmentScan v2.5.0** (actual codebase audit):
- `env-scanning/core/`: 25,528 LOC across ~40 modules
- `env-scanning/scanners/`: 1,837 LOC (arXiv, RSS, Federal Register, local LLM classifier)
- Signal database: 509 signals from 17 sources (arXiv, TechCrunch, MIT Tech Review, Nature, IEEE Spectrum, Wired, Ars Technica, Hacker News, UN News, WHO, NASA, etc.)
- STEEPs categories: T=400, P=225, E=76, S=63, E_Environmental=25, s=7
- Daily reports: 12+ days of timeline maps, cross-evolution maps, integrated report statistics
- Output format: JSON signals + Markdown reports
- Orchestrator: Python multiprocessing, task graph-based dependency management
- 4 workflow tracks: WF1 (General), WF2 (arXiv), WF3 (Naver), WF4 (MultiGlobal)

**GlobalNews-Crawling** (actual codebase audit):
- `src/analysis/`: 15,772 LOC across 8 stages + pipeline
- `src/crawling/`: 15,699 LOC across 22 modules (stealth browser, UA manager, URL discovery)
- `scripts/`: 32 utility scripts (SOT manager, quality gates, site validation)
- Stage breakdown by LOC:
  - Stage 1 (Preprocessing): 1,449 LOC
  - Stage 2 (Features/SBERT): 1,563 LOC
  - Stage 3 (Article Analysis): 1,678 LOC (sentiment, emotion, STEEPS)
  - Stage 4 (Aggregation/BERTopic): 2,220 LOC
  - Stage 5 (Time Series): 2,147 LOC (Prophet, burst detection, changepoints)
  - Stage 6 (Cross Analysis): 2,617 LOC (Granger, PCMCI, knowledge graphs, frame analysis)
  - Stage 7 (Signal Classification): 2,177 LOC (L1-L5 hierarchy, novelty, singularity)
  - Stage 8 (Output): 810 LOC (Parquet merge, SQLite index, DuckDB verification)
- 56 analysis techniques including: LOF, Isolation Forest, z-score anomaly, entropy change, Zipf deviation, survival analysis, KL divergence, BERTrend weak signal detection, Granger causality, PCMCI causal inference, knowledge graphs, cross-lingual alignment, frame analysis, DTW temporal alignment, contradiction detection
- 5-Layer signal hierarchy: L1_fad through L5_singularity
- 4-level retry (90 attempts), Never-Abandon philosophy
- Output format: Parquet (ZSTD) + SQLite (FTS5 + sqlite-vec) + DuckDB

**Combined existing codebase**: ~59,000 LOC of production code

### 1.2 The Integration Architecture

```
                    InvestScan Unified Pipeline
    ================================================================

    LAYER 0: DATA ACQUISITION (existing -- zero changes)
    ┌───────────────────────┐  ┌───────────────────────────────────┐
    │  EnvironmentScan      │  │  GlobalNews-Crawling              │
    │  4 workflows, ~2hr    │  │  116 sites, 8 stages, ~1.5hr     │
    │  17+ specialized src  │  │  56 NLP techniques                │
    │  LLM-driven analysis  │  │  100% local ML inference          │
    │  Output: JSON + MD    │  │  Output: Parquet + SQLite         │
    └──────────┬────────────┘  └──────────────┬────────────────────┘
               │                              │
    ═══════════╪══════════════════════════════╪═════════════════════
               │                              │
    LAYER 1: SIGNAL NORMALIZATION (NEW)       │
    ┌──────────▼──────────────────────────────▼────────────────────┐
    │  normalize_signals.py                                        │
    │  - Read EnvScan JSON (509+ signals/run)                     │
    │  - Read GNews Parquet (signals.parquet, 12 columns)         │
    │  - STEEPs <-> L1-L5 cross-mapping                           │
    │  - pSST (0-100) <-> confidence (0-1) normalization          │
    │  - Cross-source deduplication (SBERT similarity > 0.85)     │
    │  - Temporal alignment (same date window)                     │
    │  Output: unified_signals.parquet (UnifiedSignal schema)      │
    └──────────────────────────┬───────────────────────────────────┘
                               │
    LAYER 2: INVESTMENT SYNTHESIS (NEW -- the superiority engine)
    ┌──────────────────────────▼───────────────────────────────────┐
    │  Module A: Cross-Domain Impact Matrix                        │
    │  - Map every signal to affected GICS sectors                │
    │  - Compute STEEPS-domain -> sector transmission vectors      │
    │  - Detect when signals in different domains converge         │
    │                                                              │
    │  Module B: Multi-Horizon Direction Synthesizer               │
    │  - Short-term (1-4 weeks): L1+L2 signals + burst scores    │
    │  - Mid-term (1-6 months): L3 signals + changepoint data     │
    │  - Long-term (6+ months): L4+L5 signals + trend strength   │
    │  - Per-sector directional conviction (bull/bear/neutral)     │
    │                                                              │
    │  Module C: Evidence Chain Builder                             │
    │  - For every directional call, link to source signals        │
    │  - Track: which sources -> which topics -> which direction   │
    │  - Compute evidence diversity score (source count + type)    │
    │  - Flag single-source calls vs. multi-corroborated           │
    │                                                              │
    │  Module D: Signal Lifecycle Tracker                           │
    │  - Track signals across daily runs (signal_id persistence)   │
    │  - Detect promotion: L1 -> L2 -> L3 over time               │
    │  - Detect demotion: L3 -> L2 (thesis weakening)              │
    │  - Generate "signal aging" metrics                            │
    │                                                              │
    │  Module E: Korean Market Mapper                              │
    │  - GICS sectors -> KOSPI/KOSDAQ sector indices              │
    │  - Global signal -> Korea impact scoring (trade dependency)  │
    │  - Korean-specific theme mapping (반도체, AI, 바이오, etc.)    │
    │                                                              │
    │  Output: investment_synthesis.json                            │
    └──────────────────────────┬───────────────────────────────────┘
                               │
    LAYER 3: REPORT + EVIDENCE PRESENTATION (NEW)
    ┌──────────────────────────▼───────────────────────────────────┐
    │  generate_report.py                                          │
    │  - Sector heat map (matplotlib/plotly static)               │
    │  - Risk/opportunity matrix                                   │
    │  - Evidence trail per sector (clickable to source)          │
    │  - Signal lifecycle dashboard (promotions/demotions)         │
    │  - Multi-horizon synthesis view (3 timeframe columns)        │
    │  - Conviction confidence bands with uncertainty              │
    │  Output: invest-report-{date}.md (EN) + -ko.md (KO)        │
    └─────────────────────────────────────────────────────────────┘
```

### 1.3 New Modules to Build -- Detailed Breakdown

| Module | File | Purpose | LOC | Complexity |
|--------|------|---------|-----|------------|
| Schema | `schema.py` | UnifiedSignal dataclass + Parquet schema | 200 | Low |
| Config | `config.py` | Paths, sector definitions, thresholds | 150 | Low |
| Normalizer | `normalize_signals.py` | Read both formats, harmonize, dedup | 600 | Medium |
| Cross-Domain Matrix | `cross_domain_matrix.py` | STEEPs -> sector transmission scoring | 500 | High |
| Direction Synthesizer | `direction_synthesizer.py` | Multi-horizon conviction scoring | 900 | High |
| Evidence Builder | `evidence_chain.py` | Link directions to source signals | 400 | Medium |
| Lifecycle Tracker | `signal_lifecycle.py` | Cross-run signal tracking + promotion | 600 | High |
| Korean Mapper | `korean_market_mapper.py` | GICS -> KOSPI/KOSDAQ mapping | 400 | Medium |
| Report Generator | `generate_report.py` | Markdown + charts from synthesis | 700 | Medium |
| Visualization | `visualizations.py` | Heat maps, matrices, lifecycle charts | 500 | Medium |
| Utilities | `utils.py` | Shared I/O, date handling | 200 | Low |
| CLI Entry | `cli.py` | argparse CLI for the pipeline | 150 | Low |
| **Total** | | | **5,300** | |

### 1.4 Schema Normalization Design

**The core challenge**: EnvScan signals are LLM-classified qualitative entries. GlobalNews signals are ML-computed quantitative entries. They measure different things at different granularities.

**Cross-mapping logic**:

```
EnvScan STEEPs -> GlobalNews L1-L5 mapping:
  Not a 1:1 map. STEEPs describes WHAT domain; L1-L5 describes PERSISTENCE.
  A single signal has BOTH dimensions:
    STEEPs category = WHAT domain (Social, Technological, Economic, etc.)
    Signal layer    = HOW PERSISTENT (Fad, Short, Mid, Long, Singularity)

EnvScan signals LACK the persistence layer.
GlobalNews signals LACK the STEEPs domain classification.

SOLUTION: Cross-enrichment, not simple mapping.
  1. EnvScan signals get a L-layer assignment from:
     - pSST score: 0-30 -> L1, 30-60 -> L2, 60-80 -> L3, 80-95 -> L4, 95+ -> L5
     - Recurrence across daily scans: appears 1 day -> L1, 3+ days -> L2, 7+ -> L3
  2. GlobalNews signals get a STEEPs assignment from:
     - Stage 3 article_analysis already includes STEEPS per article
     - Aggregate: topic's dominant STEEPS category from constituent articles
  3. Both get normalized scores:
     - confidence: 0.0-1.0 (EnvScan: pSST/100; GNews: native confidence field)
     - burst_score: 0.0-1.0 (EnvScan: derive from multi-day recurrence; GNews: native)
     - novelty_score: 0.0-1.0 (EnvScan: derive from source uniqueness; GNews: native)
```

**UnifiedSignal schema (final)**:

```python
@dataclass
class UnifiedSignal:
    signal_id: str              # IS-{date}-{seq}
    source_system: str          # "envscan" | "gnews"
    source_signal_id: str       # Original ID from source system
    title: str
    summary: str
    detected_at: datetime

    # Dual-axis classification
    steeps_category: str        # S, T, E, E_env, P, s
    signal_layer: str           # L1_fad through L5_singularity

    # Quantitative scores (all normalized 0.0-1.0)
    confidence: float
    burst_score: float
    novelty_score: float
    singularity_composite: float  # 0.0 for non-L5 signals

    # Provenance
    source_name: str            # "TechCrunch", "Reuters", "arXiv"
    source_type: str            # "academic", "news", "blog", "government"
    article_count: int          # How many articles back this signal
    source_diversity: int       # Distinct source outlets

    # Investment mapping (populated by Layer 2)
    gics_sectors: list[str]
    direction: str              # "bullish" | "bearish" | "neutral"
    conviction: float           # 0.0-1.0
    korea_relevance: float      # 0.0-1.0
    evidence_chain: list[str]   # List of source signal IDs supporting this
```

---

## Part 2: The Superiority Stack

### 2.1 What InvestScan Can Do That AlphaSquare Structurally Cannot

| Capability | InvestScan | AlphaSquare | Why AlphaSquare Cannot Replicate |
|-----------|------------|-------------|----------------------------------|
| **Multi-horizon synthesis** | 3 timeframes (short/mid/long) from signal persistence analysis across 116+ sources | Single prediction per stock | Their architecture is stock-centric. Building source-diverse multi-horizon requires fundamentally different data infrastructure. |
| **Evidence chain** | Every directional call links to specific signals, from specific sources, with specific detection dates | "AI says buy" with no provenance | They would need to expose their model internals, which proprietary ML systems never do. |
| **Cross-domain impact** | POLITICAL signal -> TECHNOLOGY stocks (via STEEPs-to-sector transmission matrix) | Stock-level features only | Their 340K simulations use price/volume/technical indicators. They have no macro signal ingestion pipeline. |
| **Signal lifecycle** | Track a weak signal from L1_fad through L3_mid over weeks | No concept of signal aging | Their signals are daily snapshots (buy/sell today). No temporal tracking architecture. |
| **116-site multilingual** | 14+ languages, academic + government + specialized sources | Korean financial news only | Building a 116-site crawler with 4-level retry and 56 NLP techniques is 2+ years of engineering (~31K LOC crawling+analysis). |
| **STEEPs framework** | Futures studies methodology (Social, Technological, Economic, Environmental, Political) | No macro framework | This is a methodological choice, not a feature. It requires domain expertise in futures studies. |
| **100% local** | $0 operating cost, zero data exfiltration | Cloud-dependent, subscription model | Their business model requires cloud. Local-first is architecturally incompatible with their revenue structure. |
| **Open pipeline** | User modifies workflow.md, adds sources, changes scoring | Closed black-box | Their competitive advantage is their black-box. Opening it would destroy their moat. |

### 2.2 Multi-Horizon Direction Synthesis (Detailed)

This is InvestScan's single most differentiated feature. Here is the exact algorithm:

```
INPUT: unified_signals.parquet (from Layer 1)

FOR EACH gics_sector:
  COLLECT all signals mapped to this sector

  SHORT-TERM DIRECTION (1-4 weeks):
    signals_short = filter(signal_layer IN [L1_fad, L2_short])
    bullish_signals = count(direction == "bullish" AND burst_score > 0.5)
    bearish_signals = count(direction == "bearish" AND burst_score > 0.5)
    short_direction = weighted_vote(bullish_signals, bearish_signals,
                                     weights=burst_score * confidence)
    short_conviction = evidence_diversity_factor * signal_strength_avg

  MID-TERM DIRECTION (1-6 months):
    signals_mid = filter(signal_layer == L3_mid)
    Use changepoint_significance as primary weight
    Require minimum 3 independent sources for "confident" call
    mid_direction = weighted_vote(...)
    mid_conviction = source_diversity_factor * changepoint_avg

  LONG-TERM DIRECTION (6+ months):
    signals_long = filter(signal_layer IN [L4_long, L5_singularity])
    Use trend_strength and signal persistence (days tracked) as weights
    long_direction = weighted_vote(...)
    long_conviction = persistence_factor * cross_domain_count

  SECTOR SYNTHESIS:
    alignment_score = how_aligned(short, mid, long)
    // alignment_score = 1.0 if all three agree, 0.33 if all disagree
    overall_conviction = max(short, mid, long) * alignment_score
    conflict_flag = TRUE if short != long
    // Conflict is INFORMATIVE, not an error: "short-term bearish but long-term bullish"

OUTPUT: per-sector direction card with 3 timeframes + alignment score
```

**Why this is superior to 340K simulations**: AlphaSquare's simulations operate on price/volume data for individual stocks within a single timeframe. They answer "which stock to pick today." InvestScan answers "which macro direction is forming, across what timeframe, based on what evidence from 133+ sources." These are categorically different questions. A retail investor who knows "semiconductor sector is short-term bearish (US export controls tightening) but long-term bullish (sovereign AI investment wave)" makes better decisions than one who gets "buy Samsung Electronics today."

### 2.3 Cross-Domain Impact Analysis

The cross-domain matrix maps how signals in one STEEPs domain affect investment sectors:

```
TRANSMISSION MATRIX (rules-based v1, ML v2):

                 IT    Health  Financials  Materials  Energy  Consumer  Utilities  Telecom
Political       0.7    0.3     0.6         0.4        0.8     0.3       0.5        0.3
Technological   0.9    0.6     0.4         0.3        0.4     0.5       0.3        0.7
Economic        0.6    0.3     0.9         0.7        0.6     0.8       0.4        0.3
Environmental   0.3    0.2     0.3         0.6        0.9     0.4       0.8        0.2
Social          0.4    0.7     0.3         0.2        0.2     0.9       0.3        0.3
Geopolitical    0.5    0.2     0.7         0.5        0.8     0.4       0.3        0.4

EXAMPLE:
  Signal: "EU AI Act enforcement begins" (Political, L3_mid, confidence 0.82)
  Transmission: IT=0.7, Financials=0.6 -> both sectors impacted
  Direction: bearish for IT (compliance costs), neutral-bullish for Financials (AI audit demand)
  Result: sector-level directional signal with cross-domain provenance
```

### 2.4 Signal Lifecycle Tracking

```
Day 1:  Signal "OpenAI releases new model" detected
        -> L1_fad (burst_score=0.9, from 5 sources)
        -> Status: NEW

Day 3:  Same signal cluster persists, 12 sources now
        -> Promoted to L2_short
        -> Status: PROMOTED (L1 -> L2)

Day 14: Related signals: "Google responds", "Meta pivots", "US regulation proposed"
        -> Signal cluster merges with 3 related clusters
        -> Promoted to L3_mid (changepoint_significance=0.7)
        -> Status: PROMOTED (L2 -> L3), MERGED with 3 clusters

Day 60: Signal cluster still active, appears in arXiv papers now
        -> Promoted to L4_long
        -> Status: PROMOTED (L3 -> L4)
        -> Investment implication: this is a structural shift, not a cycle

TRACKING DATA (signal_lifecycle.json):
{
  "cluster_id": "CL-20260301-007",
  "birth_date": "2026-03-01",
  "current_layer": "L4_long",
  "promotion_history": [
    {"date": "2026-03-01", "from": null, "to": "L1_fad"},
    {"date": "2026-03-03", "from": "L1_fad", "to": "L2_short"},
    {"date": "2026-03-14", "from": "L2_short", "to": "L3_mid"},
    {"date": "2026-05-01", "from": "L3_mid", "to": "L4_long"}
  ],
  "source_count_over_time": [5, 8, 12, 18, 24, 31],
  "merged_clusters": ["CL-20260305-012", "CL-20260308-003", "CL-20260312-019"],
  "investment_implication_shift": "initial: short-term trading opportunity -> current: long-term structural allocation shift"
}
```

AlphaSquare has no equivalent concept. Their signals are born and die in 10-minute windows. There is no persistent identity, no promotion history, no lifecycle narrative.

---

## Part 3: MVP Feature List with Time Estimates

### 3.1 Feature-Level Breakdown

| # | Feature | LOC | Dev Time | Dependencies | Priority |
|---|---------|-----|----------|-------------|----------|
| F1 | Project scaffold + config + CLI | 350 | 3 days | None | P0 |
| F2 | UnifiedSignal schema + Parquet definition | 200 | 2 days | F1 | P0 |
| F3 | EnvScan JSON reader/parser | 300 | 3 days | F2 | P0 |
| F4 | GlobalNews Parquet reader/parser | 250 | 2 days | F2 | P0 |
| F5 | STEEPs <-> L1-L5 cross-enrichment logic | 350 | 4 days | F3, F4 | P0 |
| F6 | Cross-source deduplication (SBERT cosine) | 250 | 3 days | F5 | P1 |
| F7 | Sector mapper (STEEPs -> GICS, rules-based) | 500 | 5 days | F5 | P0 |
| F8 | Cross-domain impact matrix (rules-based) | 400 | 4 days | F7 | P0 |
| F9 | Short-term direction scoring | 300 | 3 days | F8 | P0 |
| F10 | Mid-term direction scoring | 300 | 3 days | F8 | P0 |
| F11 | Long-term direction scoring | 300 | 3 days | F8 | P0 |
| F12 | Multi-horizon synthesis + alignment | 200 | 2 days | F9, F10, F11 | P0 |
| F13 | Evidence chain builder | 400 | 4 days | F12 | P0 |
| F14 | Korean market mapper (GICS -> KOSPI sectors) | 400 | 4 days | F7 | P0 |
| F15 | Basic Markdown report generation | 500 | 5 days | F12, F13, F14 | P0 |
| F16 | Sector heat map (matplotlib) | 250 | 3 days | F15 | P1 |
| F17 | workflow.md orchestration (full pipeline) | 200 | 3 days | F15 | P0 |
| F18 | Korean translation integration | 150 | 2 days | F15 | P1 |
| F19 | Signal lifecycle tracker (cross-run persistence) | 600 | 8 days | F5 | P1 |
| F20 | Risk/opportunity matrix visualization | 300 | 3 days | F12 | P2 |
| F21 | Backtesting skeleton (signal vs. actual prices) | 500 | 7 days | F12 | P2 |
| F22 | Anomaly alerts (L5_singularity + pSST spikes) | 200 | 2 days | F5 | P2 |
| F23 | Sector rotation detection | 350 | 5 days | F19 | P2 |
| F24 | Portfolio implication summary | 300 | 3 days | F12, F14 | P2 |
| F25 | Scheduled execution (launchd/cron) | 150 | 2 days | F17 | P1 |
| F26 | Error handling + graceful degradation | 300 | 3 days | F17 | P1 |
| F27 | Conviction confidence bands + uncertainty | 200 | 2 days | F12 | P1 |
| **TOTAL** | | **~7,500** | **~93 dev-days** | | |

### 3.2 Month-by-Month Plan (6 Months)

**Month 1: Foundation (F1-F5)**
- Week 1: F1 (scaffold) + F2 (schema)
- Week 2: F3 (EnvScan reader)
- Week 3: F4 (GNews reader)
- Week 4: F5 (cross-enrichment) + integration tests
- **Milestone**: Unified signal dataset from both systems
- **LOC delivered**: ~1,450

**Month 2: Investment Synthesis Core (F7-F12)**
- Week 5: F7 (sector mapper)
- Week 6: F8 (cross-domain matrix)
- Week 7: F9 + F10 (short + mid direction scoring)
- Week 8: F11 + F12 (long-term + synthesis)
- **Milestone**: Per-sector investment directions with 3 timeframes
- **LOC delivered**: ~2,000

**Month 3: Report + Orchestration (F13-F17)**
- Week 9: F13 (evidence chains)
- Week 10: F14 (Korean market mapper)
- Week 11: F15 (Markdown report generation)
- Week 12: F17 (workflow.md orchestration)
- **Milestone**: First fully automated daily run producing investment reports
- **LOC delivered**: ~1,700

**Month 4: Quality + Lifecycle (F6, F18, F19, F26, F27)**
- Week 13: F6 (deduplication)
- Week 14-15: F19 (signal lifecycle tracker -- 8 days)
- Week 16: F26 (error handling) + F27 (confidence bands)
- **Milestone**: Signal persistence across runs, production error handling
- **LOC delivered**: ~1,500

**Month 5: Advanced Analytics (F16, F20-F24)**
- Week 17: F16 (heat map) + F18 (Korean translation)
- Week 18: F20 (risk matrix) + F22 (anomaly alerts)
- Week 19: F23 (sector rotation)
- Week 20: F24 (portfolio implications)
- **Milestone**: Full analytics suite
- **LOC delivered**: ~1,550

**Month 6: Hardening (F21, F25 + buffer)**
- Week 21: F21 (backtesting skeleton)
- Week 22: F25 (scheduled execution)
- Week 23-24: Testing, edge cases, documentation, buffer
- **Milestone**: Production-ready system
- **LOC delivered**: ~650 + test code

### 3.3 What Makes It "Superior" vs. "Just Different"

**"Just different" features** (nice but not decisive):
- 100% local execution (privacy advantage, but users trade convenience for privacy rarely)
- Korean translation (AlphaSquare is already Korean-native)
- Markdown reports (different format, not better per se)

**Actually superior features** (structural advantages):
1. **Multi-horizon direction synthesis**: No Korean investment app provides short + mid + long term directional views from the same signal base. This is architecturally impossible for stock-picker apps.
2. **Evidence chains**: "This sector direction is bullish because of [3 signals from 7 sources over 14 days]" vs. "AI says buy." This is a trust architecture advantage.
3. **Signal lifecycle tracking**: Watching a weak signal grow from fad to megatrend over weeks is unique. No competitor tracks signal evolution.
4. **Cross-domain impact**: A POLITICAL signal affecting TECHNOLOGY stocks is invisible to apps that only parse financial data.
5. **Source diversity**: 133+ sources across 14+ languages vs. Korean financial news. This is a data moat.

---

## Part 4: Technical Risks to the Superiority Claim

### Risk 1: Can We Produce Better Investment Directions Than 340K Simulations?

**Honest assessment**: It depends on what "better" means.

| Dimension | AlphaSquare (340K simulations) | InvestScan (STEEPs + NLP synthesis) |
|-----------|-------------------------------|--------------------------------------|
| **What it answers** | "Which stock will go up/down today?" | "What macro forces are forming and what sectors will they impact?" |
| **Time horizon** | Very short (intraday to days) | Short to long (weeks to months) |
| **Data basis** | Price/volume/technical indicators | News, research, policy, social media across 133+ sources |
| **Backtestable** | Yes, immediately (historical price data exists) | Difficult (need historical signal-to-market-outcome data) |
| **Accuracy measurable** | Yes (predicted price vs actual price) | Partially (sector direction is measurable, conviction accuracy is not) |
| **User type** | Active trader (daily decisions) | Strategic allocator (sector/thesis-level decisions) |

**The truth**: These systems answer different questions. AlphaSquare is better at short-term stock picking. InvestScan is better at macro direction and thesis building. They do not compete on the same axis.

**Where InvestScan genuinely wins**: When a retail investor asks "Should I increase my semiconductor exposure given what is happening globally?" -- AlphaSquare cannot answer this. InvestScan can, with evidence from 133 sources across 14 languages.

**Where AlphaSquare genuinely wins**: When a trader asks "Which 3 stocks should I buy this morning?" -- InvestScan cannot answer this (no individual stock scoring). AlphaSquare can.

**Verdict**: InvestScan's superiority is real but only for macro-direction and thesis-level investing. For daily stock picking, AlphaSquare wins.

### Risk 2: Is STEEPs-Based Direction More Valuable Than Quantitative Backtesting?

**Honest assessment**: STEEPs is more valuable for CERTAIN decisions, not ALL decisions.

**Where STEEPs wins**:
- Black swan detection: STEEPs scans political and social domains that quantitative backtesting literally cannot see. COVID-19, Russia-Ukraine, SVB collapse -- these are STEEPs signals, not price/volume signals.
- Sector rotation: When a structural shift begins (e.g., sovereign AI investment wave), price data lags by months. Environmental scanning detects the POLICY signal before it shows up in EARNINGS.
- Confirmation bias prevention: STEEPs forces systematic scanning of domains the investor might ignore.

**Where backtesting wins**:
- Pattern validation: "This technical pattern has led to X% gains Y% of the time over 10 years" -- this is statistically grounded. STEEPs provides no equivalent validation.
- Risk management: Stop-loss levels, position sizing -- these require price data, not macro signals.
- Speed: Backtesting gives actionable signals in seconds. STEEPs-based analysis takes hours.

**Verdict**: STEEPs is strategically superior (WHY to invest) but tactically inferior (WHEN and HOW MUCH). The two are complementary, not competing.

### Risk 3: How Do We Validate That Our Output Is "Better"?

This is the existential risk. Three concrete validation approaches:

**Approach A: Forward-Looking Track Record (6 months)**
- Start recording all InvestScan directional calls from Day 1
- After 6 months, compare against actual sector performance (KOSPI sector indices)
- Metric: "Of sectors InvestScan called bullish with conviction > 0.6, what percentage outperformed the index?"
- Target: >55% accuracy (above random 50%)
- LOC to implement: ~500 (backtesting framework skeleton, F21)
- Timeline: Results available Month 7+

**Approach B: Historical Backfill (3 months of effort)**
- Replay EnvScan and GlobalNews against historical data from 2025
- Generate InvestScan directions for past dates
- Compare against actual KOSPI sector outcomes
- Problem: EnvScan's historical data only goes back to 2026-01-30. GlobalNews has no historical archive.
- Verdict: NOT feasible for v1 (insufficient historical data)

**Approach C: Expert Panel Review (immediate)**
- Produce weekly InvestScan reports
- Have 3-5 domain experts (or the user) score each report on: usefulness, accuracy of direction, quality of evidence
- Qualitative but immediate
- Cost: $0 (user is the domain expert)
- LOC: 0 (human review process)

**Recommended validation strategy**: Approach C immediately (human review from Week 12), transitioning to Approach A (quantitative tracking from Month 4 onward).

### Risk 4: Signal Normalization Quality

**Problem**: EnvScan signals (LLM-classified, qualitative) and GlobalNews signals (ML-computed, quantitative) may not be meaningfully comparable after normalization.

**Specific concern**: A pSST score of 72 from EnvScan and a confidence of 0.72 from GlobalNews DO NOT mean the same thing. pSST measures "preliminary sociotechnical significance" while confidence measures "statistical confidence in signal layer classification."

**Mitigation**:
- Never average pSST and GNews confidence directly
- Use them as independent inputs to the conviction formula: `conviction = f(psst_norm, gnews_confidence, source_diversity, cross_source_corroboration)`
- Display both raw scores in evidence chains so users can form their own judgment
- Treat normalization as "making comparable" not "making identical"

**LOC impact**: Adds ~100 LOC of careful fusion logic to `direction_synthesizer.py`

---

## Part 5: The Honest Answer -- Where Is Superiority Real vs. Marketing?

### REAL Superiority (Structural, Defensible)

| Advantage | Why It Is Real | Defensive Moat |
|-----------|---------------|----------------|
| **Source diversity (133+ sources, 14 languages)** | 31,000 LOC of crawling + analysis code. 2+ years of engineering. No competitor has this. | Extremely high. Building this from scratch takes 18-24 months minimum. |
| **Cross-domain impact analysis** | STEEPs framework + 56 NLP techniques detect signals across domains that stock-picker apps structurally cannot see. | High. Requires both the data infrastructure AND the analytical framework. |
| **Signal lifecycle tracking** | No Korean investment app tracks signal evolution over time. This is a genuinely novel capability. | Medium-high. The concept is copyable but requires persistent signal identity across daily runs. |
| **Evidence chains** | Full provenance from source article -> signal -> sector direction. AlphaSquare's black box cannot offer this. | Medium. Technically implementable by anyone, but requires fundamentally different architecture than ML-prediction apps. |
| **$0 cost, 100% local** | Zero API fees for the NLP pipeline. Zero cloud dependency. | Low. This is a deployment choice, not a technical advantage. Others can go local too. |

### MARKETING (Real But Not Decisive)

| Claim | Why It Is Marketing | Honest Assessment |
|-------|-------------------|-------------------|
| **"Better than 340K simulations"** | Different, not better. We answer different questions. | MISLEADING if stated as superiority. HONEST if stated as "complementary at a different level of analysis." |
| **"Academic paper scanning (arXiv)"** | Novel for consumer investment apps, but academic papers rarely generate short-term investment signals. | NICHE. Valuable for L4/L5 long-term technology thesis building, irrelevant for quarterly trading. |
| **"56 NLP techniques"** | Impressive count but many techniques contribute marginally. LOF + Isolation Forest might detect 95% of what all 56 together detect. | QUANTITY is not quality. The techniques that matter most: SBERT embedding, BERTopic, Prophet time series, Granger causality, and the 5-Layer classification. The rest are incremental. |
| **"14+ languages"** | Crawling 14 languages is impressive infrastructure, but the investment-relevant signal density in most languages for Korean market investors is low. | BROAD but SHALLOW for investment. English + Korean + Chinese + Japanese cover 90%+ of Korean-market-relevant signals. |
| **"Futures studies methodology (STEEPs)"** | Sounds academic and rigorous. But the actual implementation is keyword-based classification, not genuine futures studies. | OVERSTATED. The implementation is a rule-based classifier mapping articles to 6 categories. Real futures studies involves expert Delphi panels, scenarios, wildcards. |

### THE BOTTOM LINE

**Where InvestScan is genuinely, overwhelmingly superior**:
1. **Macro direction synthesis**: No Korean app turns 133-source environmental scanning into sector-level investment directions with 3 timeframes. This is a genuine empty quadrant.
2. **Evidence transparency**: "Here are the 7 signals from 12 sources that led to this bullish call on semiconductors" vs. "AI says buy." This is a trust revolution.
3. **Signal lifecycle**: Watching a weak signal evolve from fad to megatrend is something no competitor offers.

**Where InvestScan must be HONEST about limitations**:
1. It does NOT replace stock picking. It is a macro overlay, not a stock screener.
2. Its accuracy is UNVALIDATED until Month 7+ of forward-looking tracking.
3. The STEEPs classification is keyword-based, not genuine futures studies methodology.
4. 14 languages sounds impressive but only 4 matter for Korean market investing.

**The recommended positioning**:
> "InvestScan is not a stock picker. It is an investment direction intelligence system that tells you WHICH sectors to watch, WHY, and for HOW LONG -- with full evidence from 133+ sources across 14 languages. Use InvestScan to decide WHAT to invest in. Use your broker app to decide WHICH stocks to buy."

This positioning is honest, defensible, and targets the genuine gap in the Korean market that no competitor fills.

---

## Appendix A: Codebase Size Comparison

| System | Component | LOC | Status |
|--------|-----------|-----|--------|
| EnvironmentScan | Core modules | 25,528 | Production |
| EnvironmentScan | Scanners | 1,837 | Production |
| GlobalNews | Analysis pipeline (8 stages) | 15,772 | Production |
| GlobalNews | Crawling infrastructure | 15,699 | Production |
| GlobalNews | Utility scripts | ~8,000 | Production |
| **Existing total** | | **~67,000** | |
| InvestScan | New integration layer | 5,300 | To build |
| InvestScan | Tests + docs | ~2,000 | To build |
| **Grand total** | | **~74,000** | |

InvestScan adds ~10% new code on top of a massive existing base. This is the fastest path to overwhelming superiority: leverage 67K LOC of existing infrastructure, add 5-7K LOC of integration intelligence.

## Appendix B: Project Directory Structure

```
01.invest_test/
├── CLAUDE.md
├── workflow.md                         <- Claude Code orchestration
├── invest_pipeline/
│   ├── __init__.py
│   ├── cli.py                          <- argparse entry point
│   ├── config.py                       <- Paths, thresholds, constants
│   ├── schema.py                       <- UnifiedSignal + Parquet schema
│   ├── normalize_signals.py            <- Layer 1: read + harmonize
│   ├── cross_domain_matrix.py          <- Layer 2A: STEEPs -> sector transmission
│   ├── direction_synthesizer.py        <- Layer 2B: multi-horizon scoring
│   ├── evidence_chain.py              <- Layer 2C: provenance builder
│   ├── signal_lifecycle.py            <- Layer 2D: cross-run tracking
│   ├── korean_market_mapper.py        <- Layer 2E: GICS -> KOSPI/KOSDAQ
│   ├── generate_report.py            <- Layer 3: Markdown + charts
│   ├── visualizations.py             <- Layer 3: heat maps, matrices
│   └── utils.py                       <- Shared utilities
├── config/
│   ├── sectors.yaml                    <- GICS sector definitions + keywords
│   ├── korean_market.yaml             <- KOSPI/KOSDAQ sector weights
│   ├── cross_domain_weights.yaml      <- STEEPs -> sector transmission matrix
│   └── thresholds.yaml               <- Scoring thresholds
├── data/
│   ├── lifecycle/                      <- Signal lifecycle persistence
│   │   └── signal_clusters.json
│   └── validation/                     <- Forward-looking accuracy tracking
│       └── direction_log.json
├── output/
│   └── {date}/
│       ├── unified_signals.parquet
│       ├── investment_synthesis.json
│       ├── invest-report-{date}.md
│       ├── invest-report-{date}-ko.md
│       └── sector_heatmap.png
├── tests/
│   ├── test_normalize.py
│   ├── test_cross_domain.py
│   ├── test_direction_synthesizer.py
│   ├── test_evidence_chain.py
│   ├── test_lifecycle.py
│   └── test_korean_mapper.py
└── research/                           <- Existing research (this file)
```

## Appendix C: Dependency Summary

| Library | Purpose | Already Installed? |
|---------|---------|-------------------|
| pyarrow | Parquet I/O | Yes (GlobalNews) |
| pandas | Data manipulation | Yes (GlobalNews) |
| numpy | Numerical operations | Yes (GlobalNews) |
| matplotlib | Heat maps, charts | Likely yes |
| sentence-transformers | SBERT for dedup | Yes (GlobalNews) |
| pyyaml | Config files | Likely yes |
| Jinja2 | Report templates | Install needed (~2 min) |

All heavy ML dependencies are already in GlobalNews's `.venv`. InvestScan can share the same virtual environment for its analysis modules, adding only Jinja2 (optional, for report templating).
