# InvestScan: Long-Term Scalability Architecture Analysis

**Role**: Long-Term Scalability Tech Architect
**Philosophy**: "Build solid foundations now, scale without pain later"
**Date**: 2026-03-27

---

## 1. Architecture Strategy

### 1.1 Extensibility Design: The "Spine + Rib" Pattern

After deep-diving into both codebases, I recommend a **Spine + Rib** architecture -- not microservices (overkill for single-user CLI), not a monolith (already proven painful in EnvironmentScan's 42-file `core/` directory).

**Spine** = The fixed pipeline skeleton: Collect -> Normalize -> Analyze -> Score -> Output
**Ribs** = Pluggable components that attach to spine stages

```
          SPINE (fixed)                    RIBS (pluggable)
     +-----------------+
     |   Data Ingest   | <--- EnvScan adapter, GlobalNews adapter, KRX adapter, ...
     +-----------------+
            |
     +-----------------+
     |   Normalize     | <--- Article normalizer, Signal normalizer, Price normalizer, ...
     +-----------------+
            |
     +-----------------+
     |   Analyze       | <--- STEEPs classifier, 5-Layer signal, pSST scorer, ...
     +-----------------+
            |
     +-----------------+
     |   Synthesize    | <--- Cross-source correlator, Investment direction mapper, ...
     +-----------------+
            |
     +-----------------+
     |   Output        | <--- Markdown report, JSON signals, Parquet archive, ...
     +-----------------+
```

**Why this works for InvestScan specifically:**
- Both source systems already have well-defined output contracts (GlobalNews: `RawArticle` dataclass with 14 fields; EnvironmentScan: JSON with `items[]` array + `agent_metadata`)
- Adding a new data source = writing one adapter class (a "rib"), not modifying the spine
- Adding a new analysis method = dropping a new analyzer into the Analyze stage
- Config-driven: YAML declarations, not code changes

### 1.2 Modular Pipeline Design: Each Stage Independently Replaceable

Taking the best lessons from both systems:

**From GlobalNews (KEEP):**
- 8-stage sequential pipeline with explicit dependency graph (`STAGE_DEPENDENCIES` dict mapping stage -> required Parquet files)
- Atomic stage execution: temp file + rename, failure doesn't corrupt prior outputs
- Checkpoint/resume from any stage
- Memory management with explicit `gc.collect()` between stages

**From EnvironmentScan (KEEP):**
- Task graph with `blockedBy`/`blocks` dependency chains
- Config-driven thresholds via `thresholds.yaml` and `workflow-registry.yaml`
- SOT Direct Reading pattern: "Python reads parameters, LLM makes judgments"
- Self-improvement engine for autonomous parameter tuning

**For InvestScan, each stage must satisfy:**
1. **Input contract**: Typed dataclass or schema-validated dict (inspired by GlobalNews `RawArticle`)
2. **Output contract**: Same -- schema-enforced
3. **Config isolation**: Own YAML section, no cross-stage config dependencies
4. **Statelessness**: Can be re-run independently given valid inputs
5. **Observable**: Emits structured logs + timing + memory metrics

### 1.3 Data Contracts Between Stages

This is where both existing systems diverge significantly and where InvestScan must get it right from day 1.

**EnvironmentScan's weakness**: Loosely typed JSON. The `items[]` array has no enforced schema -- each agent (arxiv, blog, policy) returns different field sets merged into a flat list. This works at 37 agents but will become painful for investment analysis where field mismatches cause silent calculation errors.

**GlobalNews's strength**: The `RawArticle` frozen dataclass is excellent -- 14 typed fields, `to_jsonl_dict()` serialization, `from_jsonl_dict()` deserialization, content hash for dedup. This is the right pattern.

**InvestScan data contracts (proposed):**

```python
# Stage boundaries -- frozen dataclasses with version tags
@dataclass(frozen=True)
class IngestRecord:
    """Contract: Ingest -> Normalize"""
    source_system: str        # "envscan" | "globalnews" | "krx" | ...
    source_id: str            # Unique ID within source
    raw_content: str          # Original text/data
    content_type: str         # "article" | "signal" | "price" | "report"
    language: str             # ISO 639-1
    collected_at: datetime
    metadata: dict            # Source-specific metadata (unstructured)
    schema_version: str       # "1.0.0" -- for forward compatibility

@dataclass(frozen=True)
class NormalizedItem:
    """Contract: Normalize -> Analyze"""
    item_id: str              # UUID
    source_system: str
    title: str
    body: str
    language: str
    published_at: datetime | None
    steeps_category: str | None
    geographic_scope: str | None
    content_hash: str
    schema_version: str

@dataclass(frozen=True)
class AnalyzedSignal:
    """Contract: Analyze -> Synthesize"""
    signal_id: str
    item_ids: list[str]       # Which items contributed
    signal_type: str          # FSSF type or 5-Layer classification
    confidence: float         # 0-1
    psst_score: float         # 0-100 (from EnvironmentScan's pSST)
    investment_relevance: float  # 0-1 (new for InvestScan)
    steeps_dimensions: dict[str, float]
    temporal_class: str       # "fad" | "short" | "mid" | "long" | "singularity"
    evidence: list[str]       # Key supporting quotes/data points
    schema_version: str

@dataclass(frozen=True)
class InvestmentDirection:
    """Contract: Synthesize -> Output"""
    direction_id: str
    title: str
    summary: str
    signal_ids: list[str]
    sector_impacts: dict[str, float]   # sector -> impact magnitude
    time_horizon: str                   # "1m" | "3m" | "6m" | "1y"
    confidence_level: str               # "high" | "medium" | "low"
    risk_factors: list[str]
    supporting_evidence_count: int
    schema_version: str
```

**Schema versioning** is critical. Both source systems lack it entirely. When EnvironmentScan added the `exploration_gate` fields, there was no schema migration -- just new optional fields. For investment analysis where signal accuracy matters, we need explicit `schema_version` fields so the system knows when it's reading data from an older pipeline version.

### 1.4 Plugin Architecture for Investment-Specific Analyzers

```yaml
# config/analyzers.yaml
analyzers:
  steeps_classifier:
    module: "analyzers.steeps"
    class: "SteepsClassifier"
    enabled: true
    priority: 1
    config:
      model: "all-MiniLM-L6-v2"
      threshold: 0.7

  sector_mapper:
    module: "analyzers.sector"
    class: "KoreanSectorMapper"
    enabled: true
    priority: 2
    config:
      sectors_file: "config/kr-sectors.yaml"
      gics_mapping: true

  sentiment_kr:
    module: "analyzers.sentiment_kr"
    class: "KoreanSentimentAnalyzer"
    enabled: true
    priority: 3
    config:
      model: "monologg/koelectra-base-finetuned-nsmc"
```

**Adding a new analyzer = 3 steps:**
1. Write a Python class implementing `BaseAnalyzer` interface
2. Add YAML entry in `config/analyzers.yaml`
3. Run pipeline -- new analyzer is auto-discovered and executed

**No code changes to the spine.** This is the config-driven behavior that both source systems aspire to but neither fully achieves. EnvironmentScan comes closest with its `workflow-registry.yaml` + `thresholds.yaml` pattern.

### 1.5 Config-Driven Behavior

The existing systems already demonstrate this well:
- **EnvironmentScan**: `workflow-registry.yaml` (53KB!) as the master config SOT, `thresholds.yaml` for scoring parameters, `domains.yaml` for STEEPs categories, `sources.yaml` for data sources
- **GlobalNews**: `sources.yaml` (116 sites with crawl methods, anti-block tiers), `pipeline.yaml` for stage configuration, `constants.py` for centralized magic numbers

**InvestScan config hierarchy (proposed):**
```
config/
  investscan.yaml          # Master config: pipeline stages, feature flags
  sources/
    envscan-adapter.yaml   # How to connect to EnvironmentScan outputs
    globalnews-adapter.yaml # How to connect to GlobalNews outputs
    kr-market.yaml         # Korean market data sources (new)
  analyzers.yaml           # Plugin registry (above)
  scoring/
    psst-weights.yaml      # pSST dimension weights
    investment-criteria.yaml # Investment relevance scoring rules
    sector-mapping.yaml    # Signal -> Korean sector mapping
  thresholds.yaml          # All numeric thresholds in one place
  output/
    report-templates.yaml  # Output format configurations
```

---

## 2. Technical Stack Recommendations

### 2.1 What to KEEP from Both Systems

| Component | Source System | Why Keep | InvestScan Role |
|-----------|-------------|----------|-----------------|
| `RawArticle` dataclass pattern | GlobalNews | Type-safe data contracts with serialization | Template for all stage contracts |
| `contracts.py` approach | GlobalNews | Explicit boundary definitions | Every stage boundary gets a contracts file |
| 8-stage pipeline orchestrator | GlobalNews | Proven sequential pipeline with checkpoint/resume | Spine architecture |
| pSST scoring (6 dimensions) | EnvironmentScan | Mature confidence scoring for signals | Core signal confidence metric |
| Signal evolution tracker | EnvironmentScan | Cross-day signal matching + temporal classification | Investment trend persistence tracking |
| Self-improvement engine | EnvironmentScan | Autonomous parameter tuning with safety classification | Auto-tuning investment thresholds |
| `thresholds.yaml` pattern | EnvironmentScan | All numeric parameters externalized | Single file for all scoring thresholds |
| SOT Direct Reading pattern | EnvironmentScan | "Python reads, LLM judges" -- hallucination prevention | Adapter config reading |
| `sot_manager.py` | GlobalNews | Deterministic state management with file locking | Pipeline state SOT |
| Structured logging (structlog) | GlobalNews | Grep-able JSON logs | Pipeline observability |
| `run_daily.sh` pattern | GlobalNews | Cron-ready daily runner with lock files, timeouts, health checks | Daily execution automation |
| Memory management (`gc.collect()` between stages) | GlobalNews | Critical for M2 Pro 16GB | Same hardware constraint |
| Multiprocessing orchestrator | EnvironmentScan | True parallel execution for independent sources | Parallel source ingestion |
| FSSF 8-type classification | EnvironmentScan | Mature signal classification taxonomy | Signal taxonomy base |
| 5-Layer signal hierarchy (L1-L5) | GlobalNews | Temporal persistence classification | Signal temporal depth |

### 2.2 What to REDESIGN

| Component | Problem in Source System | InvestScan Design |
|-----------|------------------------|-------------------|
| **EnvironmentScan's flat JSON output** | 42 core modules dump into loosely-typed `items[]` arrays. No enforced schema. Different agents return different fields. | **Frozen dataclasses with schema_version** at every stage boundary. Validation on read AND write. |
| **GlobalNews's monolithic stage files** | `stage6_cross_analysis.py` is 102KB, `pipeline.py` is 91KB. Single files doing too much. | **Max 500 lines per file.** Each stage is a directory with `__init__.py` (interface) + internal modules. |
| **EnvironmentScan's LLM-as-orchestrator** | The LLM orchestrator runs agents by passing CLI commands. Fragile -- depends on LLM understanding 53KB `workflow-registry.yaml`. | **Python orchestrator only.** LLM is used for analysis/judgment tasks via API calls, never for pipeline control flow. |
| **GlobalNews's hardcoded crawling pipeline** | `pipeline.py` (91KB) with all 116 sites hardcoded. Adding a site requires understanding deep internals. | **Adapter pattern.** Each source system has a thin adapter. Adding a source = one new adapter file + YAML config. |
| **EnvironmentScan's 4 separate workflows** | wf1-general, wf2-arxiv, wf3-naver, wf4-multiglobal -- each with duplicated infrastructure (signals/, analysis/, reports/). | **Single unified pipeline** with source adapters. No workflow duplication. |
| **Both systems' lack of data versioning** | Neither system versions its data schemas. Schema changes are implicit. | **Explicit schema_version field** on every data contract. Migration scripts for version transitions. |

### 2.3 Database: Should We Upgrade from JSON + Parquet?

**Honest answer: Not initially, but prepare for it.**

Current landscape:
- EnvironmentScan: Pure JSON files (`database.json`, `evolution-index.json`, per-scan JSON)
- GlobalNews: Parquet (ZSTD compressed) + SQLite (FTS5 + sqlite-vec) + JSONL

**Recommendation for InvestScan MVP:**

| Data Type | Storage | Why |
|-----------|---------|-----|
| **Daily ingest records** | JSONL per source per day | Same as GlobalNews `data/raw/YYYY-MM-DD/{source_id}.jsonl`. Append-only, debuggable, git-diffable for small volumes. |
| **Analyzed signals** | Parquet (ZSTD) | Columnar access for analytics. GlobalNews already proved this works well. ~3x compression ratio. |
| **Signal evolution index** | SQLite with FTS5 | EnvironmentScan's `evolution-index.json` hits performance limits with >10K signals. SQLite handles this natively. |
| **Investment directions** | SQLite + Markdown | Queryable history + human-readable reports. |
| **Pipeline state** | YAML (state.yaml) | Same `sot_manager.py` pattern from GlobalNews. |
| **Config** | YAML | Both systems use YAML. Proven pattern. |

**6-month evolution path:**
- Month 1-3: JSON + Parquet + SQLite (above)
- Month 4-6: If signal volume exceeds 100K records/month, evaluate DuckDB as the unified query layer (GlobalNews already has it as a dependency). DuckDB reads Parquet natively and provides SQL interface without a separate server.

**Do NOT:**
- Use PostgreSQL/MongoDB (server process overhead, single-user tool)
- Use Redis (not needed for local CLI)
- Use Elasticsearch (massive overkill)

### 2.4 Orchestration: workflow.md Alone or Task Queue?

**Neither. Use a Python-native orchestrator with a task graph.**

EnvironmentScan's `task_graph.json` pattern is the right starting point:
```json
{
  "tasks": [
    {"id": "ingest-envscan", "status": "pending", "blockedBy": [], "blocks": ["normalize"]},
    {"id": "ingest-globalnews", "status": "pending", "blockedBy": [], "blocks": ["normalize"]},
    {"id": "normalize", "status": "pending", "blockedBy": ["ingest-envscan", "ingest-globalnews"], "blocks": ["analyze"]},
    ...
  ]
}
```

But upgrade with:
1. **Persistent task state** in SQLite (not JSON -- file locking issues under parallel writes)
2. **Retry with backoff** (GlobalNews's `retry_manager.py` pattern)
3. **Stage-level checkpointing** (GlobalNews's approach: if stage 3 fails, resume from stage 3 input)

**Do NOT use:**
- Celery/RQ (requires Redis/RabbitMQ server -- overkill)
- Airflow/Prefect (cloud-oriented, massive overhead)
- Temporal (distributed systems solution)

The sweet spot is Python's `multiprocessing.Pool` (already proven in EnvironmentScan) + `concurrent.futures.ProcessPoolExecutor` for parallel ingest, combined with sequential execution for analysis stages (already proven in GlobalNews).

### 2.5 Monitoring: Pipeline Health Over Weeks/Months

**Borrow liberally from both systems:**

From GlobalNews:
- `run_metadata.json` per execution (timestamp, mode, exit code, elapsed time, per-stage metrics)
- `run_daily.sh` with lock files, timeout protection, structured log rotation

From EnvironmentScan:
- `workflow-status.json` per workflow
- `health/` directory with system health checks
- `self-improvement-config.yaml` for tracking metric trends

**InvestScan monitoring design:**

```
data/
  health/
    pipeline-runs.sqlite     # Historical run metadata (append-only)
    signal-quality.sqlite    # Signal accuracy tracking over time
    source-health.json       # Per-source availability/reliability
  logs/
    daily/
      2026-03-27-daily.log   # Structured JSON log per run
    errors.log               # Error aggregation
    alerts/                  # Threshold breach notifications
```

**Key metrics to track automatically:**
1. **Source health**: Success rate per source over trailing 7/30 days
2. **Signal volume**: Daily count by type, with anomaly detection
3. **Signal quality**: pSST score distribution drift
4. **Pipeline performance**: Per-stage timing and memory usage
5. **Investment direction accuracy**: Manual feedback loop (monthly review)

---

## 3. MVP Scope (6-month, with extensibility)

### 3.1 Features That MUST Have Clean Interfaces from Day 1

These are the "golden joints" -- places where a messy interface now creates permanent debt:

| Joint | Clean Interface Required | Why Critical | Extra Time Investment |
|-------|------------------------|-------------|----------------------|
| **Source adapter boundary** | `BaseAdapter` ABC with `ingest(date) -> list[IngestRecord]` | Every new data source connects here. A leaky abstraction here means rewriting every adapter when the spine changes. | +2 days over "just make it work" |
| **Data contracts (all 4 stage boundaries)** | Frozen dataclasses with `schema_version`, `to_dict()`/`from_dict()`, validation | Downstream consumers silently break when upstream schemas drift. Both source systems suffer from this. | +3 days total |
| **Analyzer plugin interface** | `BaseAnalyzer` ABC with `analyze(items: list[NormalizedItem]) -> list[AnalyzedSignal]` | This is the primary extensibility point. New analysis methods are the #1 feature request in research systems. | +1 day |
| **Signal scoring interface** | `BaseScorer` ABC with `score(signal: AnalyzedSignal) -> ScoredSignal` | Scoring criteria WILL change as the user learns what matters for Korean market investment. The pSST model has already evolved through 3 versions in EnvironmentScan. | +1 day |
| **Output formatter interface** | `BaseFormatter` ABC with `format(directions: list[InvestmentDirection]) -> Path` | Output formats multiply: Markdown, JSON, HTML, email digest, NotebookLM input, etc. | +0.5 days |

**Total clean-interface investment: ~7.5 developer-days upfront**
**Estimated debt-avoidance value: ~30 developer-days over 12 months** (based on observed refactoring effort in both source systems)

### 3.2 MVP Feature List with Time Estimates

**Phase 1: Foundation (Month 1-2) -- 8 weeks**

| Feature | Description | Time | Priority |
|---------|-------------|------|----------|
| **F1: Project skeleton** | Directory structure, config hierarchy, pyproject.toml, logging setup | 3 days | P0 |
| **F2: Data contracts** | All 4 stage boundary dataclasses with validation | 3 days | P0 |
| **F3: Pipeline orchestrator** | Task graph + sequential stage execution + checkpoint/resume | 5 days | P0 |
| **F4: EnvironmentScan adapter** | Read EnvScan's JSON outputs, normalize to `IngestRecord` | 3 days | P0 |
| **F5: GlobalNews adapter** | Read GlobalNews's Parquet/JSONL outputs, normalize to `IngestRecord` | 3 days | P0 |
| **F6: Basic normalizer** | Deduplicate, language detect, content hash, -> `NormalizedItem` | 4 days | P0 |
| **F7: Config system** | YAML config loading with validation, `thresholds.yaml` | 2 days | P0 |
| **F8: CLI entry point** | `python main.py --mode scan --date YYYY-MM-DD [--sources envscan,globalnews]` | 2 days | P0 |
| **F9: Basic output** | Markdown report generator (investment directions summary) | 3 days | P0 |
| | **Phase 1 subtotal** | **28 days** | |

**Phase 2: Analysis Core (Month 3-4) -- 8 weeks**

| Feature | Description | Time | Priority |
|---------|-------------|------|----------|
| **F10: STEEPs classifier** | Port from EnvironmentScan, adapted for investment context | 5 days | P0 |
| **F11: Signal classifier (5-Layer)** | Port from GlobalNews Stage 7, simplified for InvestScan | 5 days | P0 |
| **F12: pSST scorer** | Port from EnvironmentScan, add investment_relevance dimension | 4 days | P0 |
| **F13: Cross-source correlator** | Match signals across EnvScan + GlobalNews outputs | 5 days | P1 |
| **F14: Korean sector mapper** | Map signals to KOSPI/KOSDAQ sector classifications | 5 days | P1 |
| **F15: Investment direction synthesizer** | Aggregate signals into actionable investment directions | 7 days | P0 |
| **F16: Signal evolution tracker** | Port from EnvironmentScan, adapted for investment signal persistence | 4 days | P1 |
| **F17: Analyzer plugin system** | `BaseAnalyzer` ABC + YAML-driven discovery + registration | 3 days | P1 |
| | **Phase 2 subtotal** | **38 days** | |

**Phase 3: Robustness & Polish (Month 5-6) -- 8 weeks**

| Feature | Description | Time | Priority |
|---------|-------------|------|----------|
| **F18: Daily automation** | `run_daily.sh` with cron, lock files, timeout, log rotation | 3 days | P0 |
| **F19: Pipeline health monitoring** | `pipeline-runs.sqlite` + source health tracking | 4 days | P1 |
| **F20: Signal quality tracking** | pSST distribution drift detection + monthly report | 3 days | P1 |
| **F21: Self-improvement engine** | Port from EnvironmentScan, adapted for investment scoring | 5 days | P2 |
| **F22: HTML report generator** | Interactive dashboard (similar to EnvScan's `scan-report-*.html`) | 5 days | P1 |
| **F23: Historical backtest** | Run pipeline on historical data, compare signal quality | 5 days | P2 |
| **F24: SQLite signal database** | FTS5 search + evolution index + query CLI | 4 days | P1 |
| **F25: Test suite** | Unit tests for contracts, analyzers, scoring; integration tests for pipeline | 8 days | P0 |
| **F26: Error handling hardening** | Circuit breakers, graceful degradation, alerting | 3 days | P1 |
| | **Phase 3 subtotal** | **40 days** | |

**Total: ~106 developer-days across 6 months (achievable for a single developer working part-time with AI assistance)**

### 3.3 Critical Modular Boundaries

These are the boundaries that, if drawn wrong, cause the most refactoring pain:

1. **Source Adapters <-> Normalizer**: Each adapter outputs `list[IngestRecord]`. The normalizer never knows or cares about the source system's internals.

2. **Normalizer <-> Analyzers**: Analyzers receive `list[NormalizedItem]` -- fully deduplicated, language-tagged, hash-verified items. No raw source data leaks through.

3. **Analyzers <-> Synthesizer**: Individual analyzers return `list[AnalyzedSignal]` with independent confidence scores. The synthesizer merges/correlates these. An analyzer can fail without crashing the pipeline.

4. **Synthesizer <-> Output Formatters**: The synthesizer produces `list[InvestmentDirection]` -- formatter-agnostic. Adding a new output format never touches analysis logic.

---

## 4. Technical Debt Prevention

### 4.1 Where Debt Accumulates in Investment Analysis Systems

Based on concrete patterns observed in both source systems:

**Debt Source 1: Schema Drift (HIGHEST RISK)**
- EnvironmentScan: The `items[]` array schema varies by agent. `arxiv-agent` returns `papers_collected`, `blog-agent` returns `articles_collected`. No enforcement.
- GlobalNews: `RawArticle` is well-typed, but the analysis stages use loose dicts between stages.
- **Prevention**: Frozen dataclasses with `schema_version` at every boundary. Validation on read AND write. Reject unknown fields.

**Debt Source 2: Monolithic Analysis Files**
- GlobalNews: `stage6_cross_analysis.py` = 102KB, `stage4_aggregation.py` = 81KB, `stage7_signals.py` = 81KB
- **Prevention**: Max 500 lines per file. Each stage is a package (directory), not a file. Internal decomposition is encapsulated.

**Debt Source 3: Threshold Sprawl**
- EnvironmentScan: `thresholds.yaml` + `core-invariants.yaml` + `workflow-registry.yaml` (53KB!) + per-module hardcoded defaults.
- GlobalNews: `constants.py` (261 lines) centralizes well, but analysis stage files also have local constants.
- **Prevention**: Single `thresholds.yaml` for ALL numeric parameters. Module-level defaults reference it. `constants.py` for path definitions only.

**Debt Source 4: Implicit Dependencies Between Analyses**
- GlobalNews: Stage 7 (signals) requires outputs from stages 3, 4, 5, 6 -- but dependencies are implicit in import statements, not declared.
- EnvironmentScan: The `task_graph.json` declares dependencies, but Python code doesn't enforce them.
- **Prevention**: Explicit `STAGE_DEPENDENCIES` dict (GlobalNews pattern) + runtime validation that required files exist before stage execution.

**Debt Source 5: Testing Gaps in Scoring Accuracy**
- Both systems have infra tests but minimal accuracy tests for scoring/classification.
- **Prevention**: "Golden dataset" of 100+ manually-scored signals. Regression test: if pSST accuracy drops below threshold, test fails. Updated quarterly.

### 4.2 Clean Separation: Data Collection vs. Analysis vs. Presentation

```
investscan/
  adapters/           # DATA COLLECTION -- talks to external systems
    base.py           # BaseAdapter ABC
    envscan.py        # EnvironmentScan adapter
    globalnews.py     # GlobalNews adapter
    kr_market.py      # Korean market data adapter (future)

  pipeline/           # ORCHESTRATION -- connects stages
    orchestrator.py   # Task graph + stage execution
    contracts.py      # All stage boundary dataclasses
    state.py          # Pipeline state management (sot_manager pattern)

  analysis/           # ANALYSIS -- pure computation, no I/O in core
    normalize/        # Dedup, language detect, hash
    classify/         # STEEPs, FSSF, 5-Layer
    score/            # pSST, investment relevance
    correlate/        # Cross-source signal matching
    synthesize/       # Signal -> Investment direction
    evolve/           # Signal evolution tracking

  output/             # PRESENTATION -- formatting only
    markdown.py       # Markdown report
    html.py           # HTML dashboard
    json_export.py    # Machine-readable JSON
    parquet.py        # Archival Parquet

  config/             # All configuration
  data/               # All data (gitignored except schema files)
  tests/              # All tests
```

The key constraint: **analysis/ modules do ZERO file I/O.** They receive typed data and return typed data. All I/O happens in adapters/ (input) and output/ (output). The orchestrator handles the plumbing.

This directly borrows from EnvironmentScan's `PSSTCalculator` design principle: "This module is a PURE COMPUTATION module (no side effects, no I/O). All data loading/saving is handled by the calling agents."

### 4.3 Testing Strategy for Investment Signal Accuracy

**Layer 1: Unit Tests (automated, per-PR)**
- Contract validation: serialize/deserialize round-trip for all dataclasses
- Analyzer correctness: known input -> expected output for each analyzer
- Scorer boundary conditions: edge cases for pSST, investment relevance

**Layer 2: Golden Dataset Regression (automated, nightly)**
- 100+ manually labeled signals with expected classifications
- Track classification accuracy, pSST score distribution, investment relevance ranking
- **Fail threshold**: If F1 score drops >5% from baseline, alert and block deployment

**Layer 3: Temporal Consistency (automated, weekly)**
- Compare this week's signal distribution to trailing 4-week average
- Flag anomalies: sudden spike in "singularity" signals, collapse in source health
- Not a pass/fail -- a diagnostic dashboard

**Layer 4: Quarterly Human Review**
- Review 50 randomly sampled investment directions from past quarter
- Score quality 1-5 on: accuracy, timeliness, actionability
- Feed back into self-improvement engine parameters

### 4.4 Validating That Investment Direction Analysis Is Improving Over Time

This is the hardest problem. Both source systems punt on it.

**Proposed approach: "Signal Scorecard"**

```
data/health/signal-quality.sqlite

TABLE signal_reviews (
    review_id TEXT PRIMARY KEY,
    signal_id TEXT,
    review_date TEXT,
    reviewer TEXT,          -- "auto" or "human"
    accuracy_score REAL,    -- 0-1: Did this signal accurately reflect reality?
    timeliness_score REAL,  -- 0-1: Was the signal detected early enough?
    actionability_score REAL, -- 0-1: Could this be acted upon?
    notes TEXT
)
```

- Auto-reviews: Compare predicted signals against what actually happened (e.g., if a signal predicted tech sector weakness, did KOSPI tech index decline within the time horizon?)
- Human reviews: Monthly 15-minute review of top 20 signals

This creates a feedback loop: signal scorecard -> self-improvement engine -> adjusted thresholds -> better signals.

---

## 5. Technical Risks (Top 3)

### Risk 1: Over-Engineering (PROBABILITY: HIGH, IMPACT: HIGH)

**The honest tension**: InvestScan is a local, single-user CLI tool run on a MacBook. Building a fully pluggable, versioned, schema-validated, self-improving system is intellectually satisfying but potentially a 6-month yak shave that produces an over-architected system no one uses.

**Evidence from source systems:**
- EnvironmentScan's `workflow-registry.yaml` is 53KB of configuration for a system that runs once daily. The config is more complex than the data flow.
- GlobalNews has 32 validation scripts in `scripts/` -- more validation code than analysis code.

**Mitigation:**
1. **The "Would I Actually Change This?" test**: Before adding an abstraction layer, ask: "In the next 12 months, will I actually add a second implementation?" If no, don't abstract.
2. **Concrete ceiling**: No more than 3 source adapters in the first 6 months (EnvScan, GlobalNews, one Korean financial API). If that's the final set, the adapter abstraction was unnecessary -- but the cost was only 7 extra developer-days.
3. **Kill switch**: If after Month 3 the project hasn't produced a single useful investment direction report, stop architecture work and switch to a 500-line script that just combines outputs from both systems.

**Honest assessment**: The plugin architecture for analyzers is probably overkill for the MVP. A simpler approach -- direct function calls in a pipeline -- would work for 6 months. The plugin system pays off only if you plan to experiment with many different analysis approaches. Given that this is a research/investment tool, experimentation IS the point, so the investment is justified -- but barely.

### Risk 2: Complexity Tax (PROBABILITY: MEDIUM, IMPACT: HIGH)

**How much complexity is justified for a local single-user tool?**

Both source systems are VERY complex:
- EnvironmentScan: 36 Python core modules, 4 workflows, 37 agents, config totaling ~150KB of YAML
- GlobalNews: 8 analysis stages totaling ~500KB of Python, 32 scripts, 116 site configurations

The question is whether InvestScan inherits this complexity or simplifies.

**My recommendation: Simplified Inheritance**

| Source System Feature | Full Port? | InvestScan Approach |
|----------------------|-----------|-------------------|
| EnvironmentScan 4 workflows | No | Single unified pipeline |
| EnvironmentScan 37 agents | No | 2-3 source adapters |
| EnvironmentScan pSST 6 dimensions | Yes | Keep (well-designed, proven) |
| EnvironmentScan signal evolution | Simplified | Track only NEW/RECURRING/STRENGTHENING/FADING |
| GlobalNews 8-stage analysis | Simplified | 5 stages (Ingest->Normalize->Analyze->Synthesize->Output) |
| GlobalNews 56 NLP techniques | No | 8-12 core techniques, add more only when baseline works |
| GlobalNews anti-block crawling | No | InvestScan reads outputs, doesn't crawl |
| GlobalNews Parquet+SQLite+DuckDB | Parquet+SQLite only | DuckDB only if query needs emerge |

**Complexity budget**: InvestScan should be ~40% the code volume of either source system. If it exceeds that, we're over-engineering.

### Risk 3: Integration Risk Between Two Very Different Systems (PROBABILITY: MEDIUM, IMPACT: MEDIUM)

**The core challenge**: EnvironmentScan and GlobalNews have fundamentally different data models:

| Dimension | EnvironmentScan | GlobalNews |
|-----------|----------------|------------|
| Unit of data | "Signal" (already classified) | "Article" (raw news content) |
| Classification | FSSF 8-type | 5-Layer (L1-L5) |
| Confidence | pSST (0-100, 6 dimensions) | Per-technique scores (varied) |
| Temporal | Signal evolution states (6 types) | Time series analysis (STL, Prophet) |
| Scope | STEEPs categories | Topic model clusters |
| Format | JSON | Parquet + SQLite |

**Merging these is not trivial.** A signal from EnvironmentScan ("Weak Signal: AI regulation in EU") and a cluster of articles from GlobalNews about the same topic need to be recognized as related and merged into a single investment direction.

**Mitigation:**
1. **Normalization layer** is critical -- both systems' outputs must pass through a common `NormalizedItem` contract before analysis
2. **Cross-source correlation** should use content hashing + semantic similarity (both systems already have these capabilities: EnvironmentScan's `embedding_deduplicator.py`, GlobalNews's simhash/MinHash dedup)
3. **Accept imperfect matching**: Start with simple keyword + date overlap matching. Improve to semantic matching only after baseline works.

**Contingency**: If cross-source correlation proves too noisy (precision < 0.7), fall back to presenting each source's signals independently with a manual correlation step. This is less elegant but immediately useful.

---

## 6. Conclusions

### 6-Month Realistic MVP Feature List

**Must-have (P0):**
1. Source adapters for EnvironmentScan + GlobalNews outputs
2. Normalization pipeline with deduplication
3. STEEPs classification + 5-Layer signal classification
4. pSST confidence scoring with investment relevance dimension
5. Investment direction synthesis (signals -> actionable summaries)
6. Markdown report output
7. Daily cron automation with health checks
8. Test suite (contracts, scoring, integration)

**Should-have (P1):**
9. Cross-source signal correlation
10. Korean sector mapping (KOSPI/KOSDAQ)
11. Signal evolution tracking
12. HTML dashboard report
13. Pipeline health monitoring (SQLite)
14. Analyzer plugin system

**Nice-to-have (P2):**
15. Self-improvement engine (auto-tuning)
16. Historical backtest capability
17. Signal accuracy scorecard with feedback loop

### Architecture Principle

**"Typed Boundaries, Flexible Interiors"**

Every stage boundary is rigidly typed (frozen dataclasses with schema versions). Within a stage, implementation can be messy, experimental, and rapidly changed -- because the contracts ensure nothing leaks out.

This is the practical middle ground between EnvironmentScan's flexibility-first approach (loose JSON everywhere, fast to iterate, error-prone at scale) and GlobalNews's rigor-first approach (detailed schemas, slow to add features, reliable at scale).

### Initial Complexity Overhead

**MEDIUM** -- estimated at 7.5 developer-days of "architecture tax" above a naive implementation, concentrated in:
- Data contracts with validation (3 days)
- Adapter abstraction layer (2 days)
- Config system with YAML validation (1.5 days)
- Analyzer plugin interface (1 day)

This is justified by the expected iteration velocity: once the foundation is laid, adding a new source or analysis method should take hours, not days.

### 1-Year-Out Concrete Advantages

1. **Adding a Korean financial data source** (KRX API, DART filings): Write one adapter file (~200 lines) + one YAML config entry. No pipeline changes. Estimated: 1 day instead of 5 days.

2. **Experimenting with a new analysis technique** (e.g., LLM-based signal validation): Write one analyzer class implementing `BaseAnalyzer` + one YAML entry. Run pipeline. Compare results. Estimated: 2 hours instead of 2 days.

3. **Schema evolution** (adding fields to signals): Bump `schema_version`, add migration script. Old data still readable. No "rebuild everything from scratch" moments.

4. **Debugging pipeline failures**: Each stage has typed inputs/outputs. When Stage 3 fails, inspect Stage 2's output file directly -- it's a validated, self-describing Parquet file. No "which agent produced this malformed JSON?" debugging sessions.

5. **Reproducing a past analysis**: Checkpoint/resume from any stage. Re-run Stage 5 (synthesis) on last week's Stage 4 output with new thresholds. Takes 30 seconds, not a full pipeline re-run.

### The Honest Bottom Line

InvestScan should be **~2,500-4,000 lines of Python** at MVP (excluding tests). It should NOT try to be either source system. It should be a focused, well-boundaried pipeline that:
- Reads from two excellent upstream systems (that do the hard work of crawling and initial analysis)
- Adds a focused investment analysis layer on top
- Produces actionable Korean market investment direction reports

The biggest risk is building a third 10,000-line system when a 3,000-line system would serve the actual user need perfectly well. Stay disciplined. Ship a useful report in Month 2, then iterate.
