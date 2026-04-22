# InvestScan Technology Deep-Dive: PHASE 2-3-4

> **Supreme Technical Moderator Report**
> **Date**: 2026-03-28
> **Input**: 10 completed PHASE 1 research branches (Core Tech, Architecture, Dev Workflow, Tech Debt, Modern Theory, Classical Theory)
> **Output**: Four-perspective discussion, three scenarios, final recommendation

---

## PHASE 2: Four Technical Perspective Discussions

Each perspective evaluates the same technology pool through a different lens. The goal is not to declare a winner among perspectives but to identify where they **agree** (Green Zone) and where they **conflict** (trade-offs that require explicit decisions).

---

### 2.A: Latest Tech Priority

**Advocate Position**: "Adopt the best available tools. The M5 Max 64GB hardware enables cutting-edge local AI. Choosing 5-year-old tools when superior alternatives exist at similar complexity is waste, not prudence."

#### Technologies Justified Despite Risks

**1. BGE-M3 Embeddings (UNANIMOUS across all perspectives)**

This is the single clearest upgrade in the entire technology evaluation. The evidence is overwhelming:
- Same `sentence-transformers` API as current MiniLM -- literal one-line model name change
- 12.5% quality improvement on MTEB benchmarks (56.0 to 63.0)
- 8192-token context vs 512-token -- eliminates truncation of full financial articles
- Hybrid dense+sparse+ColBERT retrieval in one model -- matches InvestScan's dual need for semantic similarity (cross-source dedup) AND keyword matching (financial terms)
- MIRACL cross-lingual benchmark SOTA -- directly relevant to English-Korean signal matching
- 2.2 GB RAM (3.4% of 64 GB) -- negligible on M5 Max
- Risk: VERY LOW. Fallback to MiniLM requires changing one line back.

**Verdict**: Adopt Day 1. No rational argument against this.

**2. DuckDB for Analytical Queries (STRONG CASE, TIMING DEBATABLE)**

DuckDB is the "SQLite of analytics" -- embedded, zero-config, file-based, queries Parquet files in-place. For InvestScan's evolution tracking queries (GROUP BY week, category, source across months of data), DuckDB is 10-100x faster than SQLite's row-oriented engine.

However, the Latest Tech advocate concedes: at <10K signals (first 6 months), SQLite returns results in <100ms anyway. The speed advantage is theoretical until data volume grows. The real argument for DuckDB is **developer ergonomics**: `SELECT * FROM 'signals/2026-03-*.parquet' WHERE steeps = 'T'` -- querying Parquet files directly without import is genuinely superior workflow.

**Verdict**: Strong candidate for Month 3-4 adoption when evolution queries begin. Zero migration cost (both read same Parquet files).

**3. Ollama + Qwen3-32B for Narrative Enhancement (CONDITIONAL)**

The M5 Max can run Qwen3-32B at Q4 quantization (~30-34 GB RAM) producing 15-22 tokens/second. For a weekly batch pipeline, 1-2 minutes for a 300-word executive summary is acceptable latency. The quality advantage over Jinja2 templates for narrative prose is real.

But the Latest Tech advocate acknowledges the strongest counter-argument: **determinism**. Financial reports that influence investment decisions must be reproducible. LLM output is inherently non-deterministic. The hybrid approach (Jinja2 for data tables + LLM for narrative only, clearly marked) partially addresses this, but the reproducibility violation remains.

**Verdict**: Month 5-6 experiment only. Executive summary section only. Clearly marked as AI-generated. Never touches data tables, evidence chains, or directional calls.

**4. SetFit Few-Shot Classification (STRONG CASE, BUT PREMATURE)**

SetFit achieves GPT-3-level classification with 8-32 labeled examples per class. For InvestScan's three classification tasks (STEEPs 6 classes, Signal Layer 5 classes, Direction 3 classes), the total labeling effort is 3-5 hours for 85-92% accuracy vs rule-based 70-80%.

The Latest Tech advocate's strongest argument: **the accuracy gap matters for investment decisions**. A 75% accurate STEEPs classifier misclassifies 1 in 4 signals. Over 200 signals/week, that is 50 misclassified signals flowing into the synthesis layer. If 10% of those misclassifications flip a sector's directional call, that is ~5 wrong sector-level assessments per week.

**Verdict**: Adopt when rule-based accuracy is measured below 70% on real data (trigger-based). The 8-10 hour investment in SetFit is justified only after proving rule-based is insufficient.

**5. KR-FinBERT for Korean Financial Sentiment (NICHE BUT VALUABLE)**

KR-FinBERT (Seoul National University) achieves 96.3% accuracy on Korean financial news sentiment. It is trained on 13.22 GB of Korean financial text from 72 media sources and 16 securities companies. This is the most domain-specific model available for InvestScan's exact use case.

However: sentiment-return correlation is largely spurious (90-95% per 2025 meta-analysis). Sentiment should be ONE input signal, not a primary prediction mechanism. The STEEPs-first approach (classify what the signal IS about, not how it FEELS) is theoretically superior.

**Verdict**: Not a Day 1 priority. Consider as Month 4+ enrichment for signals already classified by STEEPs. STEEPs classification is primary; sentiment is supplementary.

**6. Technologies NOT Justified**

| Technology | Why Rejected |
|-----------|-------------|
| E5-Mistral-7B embeddings | 14 GB RAM for embeddings alone; marginal improvement over BGE-M3 |
| Multi-agent debate (MAD) | ICLR 2025: fails to outperform single-agent CoT; high failure modes |
| Neo4j graph database | Server daemon for <1000 nodes; NetworkX or SQL JOINs suffice |
| InfluxDB / TimescaleDB | Server-based time-series DBs for 200 weekly signals is absurd |
| Airflow / Prefect | Enterprise orchestration for a 5-step linear pipeline |
| Topological Data Analysis | Fascinating but requires time-series price data InvestScan does not process |
| Full fine-tuning (1000+ labels) | 100x more labeling than SetFit for marginal accuracy gain |

---

### 2.B: Stability Priority

**Advocate Position**: "Every technology choice must survive 2+ years without the developer touching it. The stack must work when the developer returns after 3 months away. Battle-tested means battle-tested -- 5+ years of production use is the minimum."

#### Bedrock Technologies (Non-Negotiable Foundation)

**1. Python 3.12 Standard Library (subprocess, pathlib, dataclasses, json, logging)**

The standard library is the most stable dependency in the Python ecosystem. `subprocess` has been unchanged since Python 2.4 (2004, 22 years). `pathlib` since Python 3.4 (2014, 12 years). `dataclasses` since Python 3.7 (2018, 8 years). Every function call in these modules will work identically in Python 3.15.

**Verdict**: Foundation layer. Zero debate.

**2. Kiwi Korean Morphological Analyzer**

Active since 2018 (8+ years). Battle-tested in EnvironmentScan's 25,500 LOC across 37 agents. Processes Naver News financial articles daily without failures. Python bindings stable across 3.8-3.12. The Stability advocate firmly rejects eKoNLPy: adding a second NLP library doubles the dependency surface for a 5% improvement on financial terminology that can be handled by Kiwi's custom dictionary extension.

**Verdict**: Kiwi only. eKoNLPy is a Month 6+ consideration if specific financial terms repeatedly cause errors.

**3. BERTopic + HDBSCAN**

BERTopic: released 2022, 4+ years of widespread adoption, actively maintained by Maarten Grootendorst. HDBSCAN: original paper 2013, Python library stable since 2017 (9 years). The combination is the most-cited neural topic modeling stack in academic literature. GlobalNews-Crawling uses it for 56 analysis techniques across 116 sites.

The Stability advocate accepts the BERTopic representation model upgrade (KeyBERTInspired + MaximalMarginalRelevance) as a **configuration change within the same library**, not a new dependency. This is the one point where Stability and Latest Tech perspectives converge.

**Verdict**: Keep current BERTopic. Accept representation model upgrade as configuration.

**4. SQLite + Parquet + PyArrow**

SQLite: 25+ years, most-deployed database globally. Parquet: 12+ years, columnar storage standard. PyArrow: 8+ years, Apache Foundation backed. This combination has survived every technology cycle from Hadoop to Kubernetes to serverless.

The Stability advocate's strongest argument against DuckDB: DuckDB is 5 years old with rapid version churn. If a breaking change occurs in DuckDB 2.x and the developer is on a 3-month hiatus, the pipeline breaks. SQLite has had zero breaking changes in 25 years.

**Verdict**: SQLite + Parquet for storage. DuckDB is acceptable as an optional analytical overlay (queries only, not primary storage).

**5. Jinja2 Templates**

18+ years of stability. Powers Flask, Ansible, Kubernetes Helm. Version 3.1.x has had no breaking changes in years. A Jinja2 template written today will render identically in 2030.

The Stability advocate's strongest argument against LLM report generation: **LLM models are replaced every 6-12 months**. Qwen3-32B will be obsolete by late 2027. The prompts will need re-tuning for Qwen4 or whatever succeeds it. Jinja2 templates written once require zero maintenance.

**Verdict**: Jinja2 only for all deterministic report sections. LLM is acceptable only for optional, clearly-marked narrative enhancement.

**6. launchd (macOS) + subprocess for Orchestration**

launchd: 21 years, Apple-maintained. subprocess: 22 years, Python standard library. cron: 51 years. These tools orchestrate mission-critical systems at every bank, hospital, and government agency. A 5-step linear pipeline does not need Snakemake's DAG engine.

**Verdict**: subprocess + launchd. Snakemake is over-engineering for a linear pipeline.

---

### 2.C: Dev Speed Priority

**Advocate Position**: "Time-to-first-report is everything. Every technology that delays the first working weekly report costs 1-2 weeks of calendar time at 2-4 hrs/week. Ship a report in Week 3, iterate from reality."

#### Critical Path to First Report

The Dev Speed advocate identifies the **minimum viable pipeline** that produces a readable weekly investment direction report:

```
Week 1-2 (4-8 hours):
  normalize_signals.py    -- Read EnvScan JSON + GlobalNews Parquet, output unified JSON
  schema.py               -- @dataclass(frozen=True) for UnifiedSignal (from Branch 4 requirement)
  health_check.py         -- Verify source files exist and are recent

Week 3-4 (4-8 hours):
  synthesize_investment.py -- Rule-based STEEPs classification + simple averaging for direction
  generate_report.py       -- Jinja2 template rendering to Markdown

TOTAL: ~8-16 hours = FIRST REPORT by Week 4 at 2-4 hrs/week
```

#### Technology Choices Driven by Speed

| Decision | Speed-Optimized Choice | Reasoning |
|----------|----------------------|-----------|
| Embeddings | BGE-M3 (same API as MiniLM) | One-line change, no speed cost |
| Topic modeling | Keep current BERTopic config | Zero change = zero time |
| Classification | Rule-based keyword dict | 3-4 hours to build, works immediately |
| Sentiment | Skip entirely for V1 | STEEPs classification is more valuable; sentiment can wait |
| Storage | Parquet files only (no database) | Files are sufficient for Month 1-3; add SQLite when needed |
| Report | Jinja2 template | 2-3 hours to build a basic template |
| Orchestration | Single Python script | `python investscan_run.py` -- zero overhead |
| Testing | Manual only for Month 1-2 | Run pipeline, read report, iterate |

#### What the Dev Speed Advocate Defers

- **Formal tests**: Month 3 (after the pipeline shape stabilizes)
- **Signal evolution tracking**: Month 4 (requires 4+ weeks of accumulated data)
- **Decision Journal**: Month 5 (requires calibration data from 4+ months of reports)
- **DuckDB**: Month 4+ (when analytical queries become necessary)
- **SetFit classifiers**: Only if rule-based accuracy is provably insufficient
- **LLM narrative**: Month 5-6 (optional polish, not core value)

#### The Speed Advocate's Key Insight

> "Every feature you build before generating the first report is a feature you might throw away. The first report reveals which features actually matter. Build the minimum, see what the data looks like, then invest."

This aligns with Branch 2's finding that Evolutionary architecture (first report at Week 3-4, ~55-70 dev hours total) beats Big Bang architecture (first report at Week 7-8, ~80-100 dev hours total) on every metric except pipeline stability -- which is addressed by the two borrowed Big Bang elements (frozen dataclasses + health check).

---

### 2.D: Maintainability Priority

**Advocate Position**: "This system must run for 2+ years with a developer who works 2-4 hours per week and sometimes disappears for months. Every technology choice must be evaluated by: 'Can I debug this after 3 months away?'"

#### The 3-Month Hiatus Test

The Maintainability advocate applies a single decisive test to every technology: **If the developer returns after 3 months of zero engagement, how long does it take to understand what broke and fix it?**

| Technology | 3-Month Return Time | Why |
|-----------|-------------------|-----|
| Rule-based keyword classifier | 5 minutes | Open YAML file, read keywords, adjust |
| SetFit ML classifier | 2-5 hours | Diagnose model drift, retrain, validate |
| Jinja2 template | 10 minutes | Open template, read, modify |
| Ollama + LLM prompt | 1-2 hours | Model version changed, prompt needs re-tuning |
| SQLite queries | 15 minutes | Universal SQL, zero learning curve |
| DuckDB queries | 20 minutes | Same SQL, slightly different functions |
| subprocess orchestrator | 5 minutes | Read the 30-line Python script |
| Snakemake orchestrator | 30-60 minutes | Re-learn Snakefile syntax, wildcard patterns |

#### The Maintainability Stack

1. **Frozen dataclasses for all data contracts** (Branch 4): When returning after 3 months, type hints on frozen dataclasses tell the developer exactly what data flows between stages. This is self-documenting architecture.

2. **Constants and Enums (no magic strings)** (Branch 4): A `SteepsCategory.TECHNOLOGICAL` enum is searchable, refactorable, and self-documenting. A string `"T"` scattered across 8 files is a debugging nightmare.

3. **Every function < 50 lines** (Branch 4): Short functions with descriptive names are readable after months away. A 200-line `synthesize()` function requires re-reading the entire thing to find a bug.

4. **Type hints on every public function** (Branch 4): `def normalize_envscan_signal(raw: dict[str, Any]) -> UnifiedSignal` is comprehensible at a glance. An untyped function requires reading the implementation to understand what it does.

5. **File-based pipeline** (Branch 5.2 Unix Philosophy): Every intermediate artifact is a readable file. After 3 months away, `cat output/2026-03-28/unified_signals.json | jq . | head` instantly shows the developer what the normalizer produced. No database queries, no connection strings, no schema inspections.

6. **Single orchestrator script** (< 50 lines): The entire pipeline flow is visible in one screen. No DAG files, no configuration hierarchy, no workflow definitions to trace.

#### The Maintainability Advocate's Key Insight

> "The most maintainable code is code that does not exist. Every additional library, every ML model, every configuration layer is a future debugging session. Choose the simplest technology that achieves 80% of the capability, and invest the saved time in the features that create actual user value."

This aligns with Branch 3's Targeted Hybrid finding: test only schema parsing (10 tests) and sector mapping (15 tests), type-hint function signatures, and skip everything else. The testing investment targets the most financially-risky code paths where bugs produce wrong investment signals.

---

### UNIFIED FEATURE / TECHNOLOGY COMPARISON TABLE

Each technology is rated by all four perspectives: Latest Tech (LT), Stability (ST), Dev Speed (DS), Maintainability (MT). Approval = check, Rejection = cross.

#### GREEN ZONE (4/4 Agreement -- Adopt Without Debate)

| Technology | LT | ST | DS | MT | Rationale |
|-----------|:--:|:--:|:--:|:--:|-----------|
| **BGE-M3 embeddings** | Y | Y | Y | Y | One-line swap, 12.5% quality gain, same API, low risk. All four perspectives agree this is a no-regret decision. |
| **@dataclass(frozen=True) schema** | Y | Y | Y | Y | ~100 LOC investment prevents entire class of data mutation bugs. Self-documenting. Required by ETL idempotency principle (Branch 5.2). |
| **Health check (source validation)** | Y | Y | Y | Y | ~50 LOC that prevents running the pipeline on stale/missing data. 5-minute investment that saves hours of debugging. |
| **Kiwi Korean NLP (keep current)** | Y | Y | Y | Y | Battle-tested, production-proven, no alternative offers sufficient improvement to justify switching. |
| **BERTopic + HDBSCAN (keep current)** | Y | Y | Y | Y | SOTA topic modeling, already in GlobalNews stack, no upgrade justified. |
| **Jinja2 for data-driven report sections** | Y | Y | Y | Y | Deterministic, debuggable, 18+ years stable. All perspectives agree data tables and evidence chains must be template-rendered. |
| **File-based IPC (JSON/Parquet)** | Y | Y | Y | Y | Unix Philosophy validated over 57 years. Simplest integration pattern for solo developer. |
| **subprocess + launchd orchestration** | Y | Y | Y | Y | Linear 5-step pipeline needs no DAG engine. Standard library + OS scheduler = zero dependency. |
| **Rule-based classification (initial)** | Y | Y | Y | Y | 3-4 hours to build, 70-80% accuracy, instantly debuggable. All perspectives agree this is the correct starting point. |
| **Parquet for signal storage** | Y | Y | Y | Y | Already used by GlobalNews, columnar, compressed, schema-preserving. Universal agreement. |
| **Type hints on public functions** | Y | Y | Y | Y | Self-documenting, catches bugs at edit-time, zero runtime cost. |
| **Constants/Enums (no magic strings)** | Y | Y | Y | Y | Searchable, refactorable, prevents the single most common classification bug (string mismatch). |

#### YELLOW ZONE (3/4 Agreement -- Adopt with Conditions)

| Technology | LT | ST | DS | MT | Dissenter | Condition for Adoption |
|-----------|:--:|:--:|:--:|:--:|-----------|----------------------|
| **DuckDB analytical queries** | Y | N | Y | Y | Stability (5-yr track record concern) | Adopt at Month 3-4 when evolution queries begin. Use as query layer over Parquet; SQLite remains backup. |
| **BERTopic representation upgrade** | Y | Y | N | Y | Speed (zero-value change for V1) | Adopt at Month 3 when topic quality tuning begins. Configuration change, not new dependency. |
| **SetFit classification (trigger-based)** | Y | N | Y | N | Stability + Maintainability (ML complexity) | Adopt ONLY when rule-based accuracy measured < 70% on 4+ weeks of real data. Concrete trigger. |
| **SQLite FTS5 for text search** | N | Y | Y | Y | Latest Tech (DuckDB is superior) | Adopt at Month 2 for signal search. Upgrade to DuckDB later if needed. |
| **NetworkX graph analysis** | Y | N | Y | N | Stability + Maintainability (new paradigm) | Adopt ONLY when multi-hop relationship queries cannot be expressed as SQL JOINs. |
| **eKoNLPy financial dictionary** | Y | N | N | N | Stability + Speed + Maintainability | Adopt ONLY when specific financial terms repeatedly cause classification errors. |
| **Targeted tests (25 tests)** | N | Y | N | Y | Latest Tech + Speed (not enough tests / too many tests) | Adopt from Month 2. Schema parsing (10) + sector mapping (15) = the minimum viable test suite. |

#### RED ZONE (<=2/4 Agreement -- Do Not Adopt or Defer Significantly)

| Technology | LT | ST | DS | MT | Supporters | Rejection Rationale |
|-----------|:--:|:--:|:--:|:--:|-----------|---------------------|
| **Ollama + LLM narrative** | Y | N | N | N | Latest Tech only | Non-deterministic, 30 GB RAM, prompt maintenance burden, hallucination risk in financial context. Month 5-6 experiment at best. |
| **Snakemake orchestration** | Y | N | N | N | Latest Tech only | 5-step linear pipeline. DAG engine overhead exceeds benefit. Reconsider at 10+ steps. |
| **KR-FinBERT sentiment model** | Y | N | N | N | Latest Tech only | Sentiment-return correlation is 90-95% spurious. STEEPs-first approach is theoretically superior. Optional enrichment at Month 5+. |
| **KcELECTRA + SetFit sentiment** | Y | N | N | N | Latest Tech only | Same as above, plus ML training/maintenance complexity. |
| **Full fine-tuning (1000+ labels)** | N | N | N | N | None | Absurd for 3K LOC project. SetFit achieves comparable results with 48 labels. |
| **Neo4j graph database** | N | N | N | N | None | Server daemon for <1000 nodes. Universally rejected. |
| **InfluxDB / TimescaleDB** | N | N | N | N | None | Time-series servers for 200 weekly signals. Universally rejected. |
| **Airflow / Prefect** | N | N | N | N | None | Enterprise orchestration for 5 steps. Universally rejected. |
| **Multi-agent debate (MAD)** | N | N | N | N | None | ICLR 2025: fails to outperform single-agent. Universally rejected. |

---

## PHASE 3: Three Technology Scenarios

Each scenario is a complete, implementable technology stack with specific libraries, LOC estimates, dev hour budgets, risk assessments, and 6-month milestones.

---

### 3.A: CUTTING EDGE Scenario

**Philosophy**: "Maximize innovation. Use the best 2024-2026 tools from Day 1. Accept higher learning curve and debugging complexity in exchange for maximum capability ceiling."

#### Exact Tech Stack

| Layer | Technology | Version | RAM | Justification |
|-------|-----------|---------|-----|---------------|
| Korean NLP | Kiwi + eKoNLPy | Kiwi 0.17+, eKoNLPy latest | ~0.3 GB | Financial term coverage |
| Embeddings | **BGE-M3** | BAAI/bge-m3 (sentence-transformers) | ~2.2 GB | SOTA multilingual, hybrid retrieval |
| Topic Modeling | BERTopic + KeyBERTInspired + MMR | BERTopic 0.16+ | ~0.5 GB | Upgraded representation stack |
| Sentiment | **KcELECTRA + SetFit** | beomi/KcELECTRA-base-v2022 + SetFit 1.0+ | ~0.5 GB | Few-shot Korean financial sentiment |
| Classification | **SetFit few-shot** (3 classifiers) | SetFit 1.0+ | ~0.5 GB | 85-92% accuracy on STEEPs/Layer/Direction |
| Storage | **DuckDB + Parquet** | DuckDB 1.2+, PyArrow 17+ | ~0.1 GB | Columnar analytics, direct Parquet queries |
| Graph | **NetworkX** | NetworkX 3.4+ | ~0.1 GB | Cross-domain impact graph analysis |
| Report (data) | Jinja2 | Jinja2 3.1+ | ~0.01 GB | Deterministic data rendering |
| Report (narrative) | **Ollama + Qwen3-32B Q4** | Ollama 0.5+, Qwen3-32B-Q4_K_M | ~32 GB | AI-generated executive summary |
| Orchestration | **Snakemake** | Snakemake 8.0+ | ~0.1 GB | DAG-based pipeline management |
| Schema | @dataclass(frozen=True) | Python 3.12 stdlib | 0 | Immutable data contracts |
| Testing | pytest + hypothesis | pytest 8.0+, hypothesis 6.0+ | 0 | Property-based testing for classifiers |

**Total RAM at peak**: ~36 GB (comfortably within 64 GB, but leaves limited headroom for OS + other apps)

#### LOC Estimate

| Module | LOC | Month |
|--------|-----|-------|
| schema.py (frozen dataclasses + enums) | 150 | 1 |
| normalize_signals.py | 300 | 1-2 |
| steeps_classifier_setfit.py | 250 | 2 |
| sector_mapper.py | 200 | 2 |
| synthesize_investment.py | 500 | 3 |
| signal_store.py (DuckDB) | 200 | 3 |
| evolution_tracker.py | 250 | 4 |
| cross_domain_graph.py (NetworkX) | 200 | 4 |
| generate_report.py (Jinja2 + Ollama) | 350 | 5 |
| decision_journal.py | 250 | 5-6 |
| investscan_run.py (Snakemake) | 100 | 2 |
| health_check.py | 80 | 1 |
| config.yaml + constants.py | 120 | 1 |
| Tests (~60 tests) | 500 | 1-6 |
| **TOTAL** | **~3,450** | |

#### Dev Hours

| Activity | Hours | % |
|---------|-------|---|
| Feature development | 55 | 55% |
| ML model training + tuning (SetFit x3, sentiment) | 15 | 15% |
| Testing (writing + maintaining 60 tests) | 12 | 12% |
| Learning curve (Snakemake, DuckDB, SetFit, NetworkX, Ollama) | 12 | 12% |
| Debugging + maintenance | 6 | 6% |
| **TOTAL** | **~100** | |

At 2-4 hrs/week = **25-50 weeks = 6-12 months**. **Exceeds the 6-month budget by 0-100%.**

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| SetFit training produces poor classifiers | 25% | HIGH (entire classification layer fails) | Fall back to rule-based; labeled data is reusable |
| Ollama/Qwen3-32B produces inaccurate financial narrative | 40% | MEDIUM (report quality degrades, not data) | Jinja2 fallback for all sections |
| Snakemake version conflict with Python 3.12 | 15% | MEDIUM (pipeline does not run) | Replace with subprocess script (2 hours) |
| DuckDB breaking change during hiatus | 10% | LOW (queries only; data in Parquet is safe) | SQLite fallback |
| Total RAM exceeds 64 GB during pipeline run | 20% | HIGH (pipeline crashes) | Reduce Qwen3 to 14B or skip LLM narrative |
| Developer burns out from learning curve | 30% | CRITICAL (project abandoned) | -- |

**Aggregate Risk Level**: **HIGH**. The learning curve alone consumes 12% of the development budget. A solo developer at 2-4 hrs/week hitting a SetFit training problem could lose an entire month of progress.

#### 6-Month Milestones

| Month | Milestone | Deliverable |
|-------|----------|------------|
| M1 | Schema + Normalize + Health Check | unified_signals.json from both sources |
| M2 | SetFit classifiers + Snakemake | Classified signals with 85%+ accuracy |
| M3 | Synthesis + DuckDB store | First investment direction output |
| M4 | Evolution tracking + NetworkX graph | Signal evolution + cross-domain analysis |
| M5 | Report generation (Jinja2 + Ollama) | Complete weekly report with AI narrative |
| M6 | Decision Journal + calibration | Prediction tracking system |

**First usable report**: Month 3 (Week 10-12). **Delayed 6-8 weeks vs Balanced/Proven.**

---

### 3.B: BALANCED-TECH Scenario (Recommended)

**Philosophy**: "Conservative core with one aggressive bet (BGE-M3). Trigger-based upgrades. Build the minimum that produces value, then evolve based on measured deficiencies."

#### Exact Tech Stack

| Layer | Technology | Version | RAM | Justification |
|-------|-----------|---------|-----|---------------|
| Korean NLP | Kiwi (keep current) | Kiwi 0.17+ | ~0.2 GB | Battle-tested, 95%+ accuracy |
| Embeddings | **BGE-M3** | BAAI/bge-m3 (sentence-transformers) | ~2.2 GB | One-line upgrade, 12.5% quality gain |
| Topic Modeling | BERTopic + HDBSCAN (keep current) | BERTopic 0.16+, HDBSCAN 0.8.38+ | ~0.5 GB | Proven SOTA, no change needed |
| Sentiment | Rule-based keyword dict | Python stdlib + YAML | ~0 | 65-75% accuracy, 5-minute fixes |
| Classification | Rule-based keyword + regex | Python stdlib + YAML | ~0 | 70-80% accuracy, instantly debuggable |
| Storage | **Parquet** (M1-3) -> + SQLite FTS5 (M3+) -> + DuckDB optional (M4+) | PyArrow 17+, SQLite3 stdlib, DuckDB 1.2+ | ~0.1 GB | Incremental: start files-only, add DB when needed |
| Graph | SQL JOINs (M1-4) -> NetworkX optional (M5+) | Python stdlib -> NetworkX 3.4+ | ~0 | JOINs cover 90% of use cases |
| Report | Jinja2 templates only | Jinja2 3.1+ | ~0.01 GB | 100% deterministic, zero hallucination |
| Orchestration | subprocess + launchd | Python 3.12 stdlib | ~0 | 22+ year proven pattern |
| Schema | @dataclass(frozen=True) + Enums | Python 3.12 stdlib | ~0 | Immutable contracts, self-documenting |
| Testing | pytest (targeted: 25 tests) | pytest 8.0+ | ~0 | Schema parsing (10) + sector mapping (15) |

**Total RAM at peak**: ~3 GB. **Leaves 61 GB free for OS, development tools, and future upgrades.**

#### LOC Estimate

| Module | LOC | Month |
|--------|-----|-------|
| schema.py (frozen dataclasses + enums + constants) | 150 | 1 |
| normalize_signals.py | 250 | 1-2 |
| health_check.py | 60 | 1 |
| steeps_classifier.py (rule-based) | 120 | 2 |
| sector_mapper.py | 180 | 2 |
| synthesize_investment.py | 400 | 2-3 |
| generate_report.py (Jinja2) | 200 | 3 |
| investscan_run.py (subprocess) | 60 | 2 |
| Templates (weekly_report.md.j2 + partials) | 200 | 3 |
| signal_store.py (Parquet -> SQLite) | 150 | 3-4 |
| evolution_tracker.py | 200 | 4-5 |
| decision_journal.py | 200 | 5-6 |
| config.yaml | 50 | 2 |
| Tests (25 tests) | 250 | 2-4 |
| **TOTAL** | **~2,470** | |

**Within the ~3,000 LOC budget with 530 LOC headroom for iteration.**

#### Dev Hours

| Activity | Hours | % |
|---------|-------|---|
| Feature development | 45 | 64% |
| Targeted testing (25 tests) | 7 | 10% |
| Manual testing (weekly pipeline run) | 10 | 14% |
| Type hints + documentation | 3 | 4% |
| Debugging + maintenance | 4 | 6% |
| Git hygiene | 1 | 2% |
| **TOTAL** | **~70** | |

At 2-4 hrs/week = **18-35 weeks = 4.5-9 months**. **Fits comfortably within the 6-month target at average pace (2.7 hrs/week).**

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| BGE-M3 produces different similarity distributions than MiniLM | 15% | LOW (recalibrate dedup threshold, 1 hour) | Test with sample data before full switch |
| Rule-based classification accuracy insufficient (<70%) | 30% | MEDIUM (visible report quality issues) | SetFit upgrade path is pre-planned; trigger is measurable |
| EnvScan/GlobalNews schema drift breaks normalization | 20% | MEDIUM (pipeline fails visibly) | Frozen dataclass + 10 contract tests catch this immediately |
| Developer motivation drops due to slow progress | 10% | MEDIUM | First report at Week 3-4 provides early reward |
| Jinja2 reports feel "robotic" vs natural language | 40% | LOW (content matters more than prose) | Can add LLM narrative later; data quality is unaffected |

**Aggregate Risk Level**: **LOW-MEDIUM**. The highest-probability risk (robotic reports) has low impact. The highest-impact risks (schema drift, classification accuracy) have concrete mitigations with clear trigger points.

#### 6-Month Milestones

| Month | Milestone | Deliverable |
|-------|----------|------------|
| M1 | Schema + Normalize + Health Check | unified_signals.json validated from both sources |
| M2 | Classification + Sector Mapping + Orchestrator | Classified, mapped signals; pipeline runs end-to-end |
| **M2 (Week 3-4)** | **FIRST WEEKLY REPORT** | **Readable investment direction report in Markdown** |
| M3 | Synthesis refinement + Report polish | Improved direction scoring + template iteration |
| M4 | Signal store + evolution tracking begins | SQLite store; weekly delta comparisons |
| M5 | Evolution tracker + cross-domain analysis | 12+ weeks of signal history; convergence detection |
| M6 | Decision Journal + system calibration | Prediction tracking; retrospective accuracy measurement |

**First usable report**: **Week 3-4 (Month 2)**. This is the earliest achievable report across all three scenarios.

#### Trigger-Based Upgrade Path

| Trigger Condition | Measurement Method | Upgrade Action | Time Cost |
|-------------------|-------------------|----------------|-----------|
| Rule-based STEEPs accuracy < 70% | Manual spot-check 10 signals/week for 4 weeks | SetFit classifier (8-10 hrs) | 3-4 weeks |
| SQLite query > 1 second | `time` the longest analytical query | DuckDB analytical overlay (3-4 hrs) | 1 week |
| Pipeline grows to 10+ steps | Count steps in orchestrator | Snakemake migration (6-8 hrs) | 2-3 weeks |
| Multi-hop signal relationships needed | SQL JOINs exceed 4 tables | NetworkX graph (3-4 hrs) | 1-2 weeks |
| Financial terms cause repeated errors | Log misclassified signals for 4 weeks | eKoNLPy supplement (2-3 hrs) | 1 week |
| Report narrative deemed insufficient | User dissatisfaction after 12+ reports | Ollama narrative experiment (12-15 hrs) | 4-5 weeks |

---

### 3.C: PROVEN STACK Scenario

**Philosophy**: "Zero new technologies. Use only what exists in the current source systems or has been proven for 5+ years. Accept lower capability ceiling for maximum predictability."

#### Exact Tech Stack

| Layer | Technology | Version | RAM | Justification |
|-------|-----------|---------|-----|---------------|
| Korean NLP | Kiwi (keep current) | Kiwi 0.17+ | ~0.2 GB | Proven in EnvScan |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 (keep current) | sentence-transformers | ~0.5 GB | 5+ years, 100M+ downloads |
| Topic Modeling | BERTopic + HDBSCAN (keep current) | BERTopic 0.16+, HDBSCAN 0.8.38+ | ~0.5 GB | Proven in GlobalNews |
| Sentiment | Rule-based keyword dict | Python stdlib + YAML | ~0 | Decades-proven pattern |
| Classification | Rule-based keyword + regex | Python stdlib + YAML | ~0 | Decades-proven pattern |
| Storage | SQLite FTS5 + Parquet (ZSTD) | Python 3.12 stdlib (sqlite3), PyArrow 17+ | ~0.1 GB | 25+ years proven |
| Graph | SQL JOINs only | Python 3.12 stdlib (sqlite3) | ~0 | No new paradigm |
| Report | Jinja2 templates only | Jinja2 3.1+ | ~0.01 GB | 18+ years proven |
| Orchestration | subprocess + launchd | Python 3.12 stdlib | ~0 | 22+ years proven |
| Schema | @dataclass(frozen=True) + Enums | Python 3.12 stdlib | ~0 | Python stdlib |
| Testing | pytest (targeted: 25 tests) | pytest 8.0+ | ~0 | Minimal viable suite |

**Total RAM at peak**: ~1.3 GB. **The lightest possible stack.**

#### LOC Estimate

| Module | LOC | Month |
|--------|-----|-------|
| schema.py | 150 | 1 |
| normalize_signals.py | 250 | 1-2 |
| health_check.py | 60 | 1 |
| steeps_classifier.py (rule-based) | 120 | 2 |
| sector_mapper.py | 180 | 2 |
| synthesize_investment.py | 350 | 2-3 |
| generate_report.py (Jinja2) | 180 | 3 |
| investscan_run.py (subprocess) | 60 | 2 |
| Templates | 180 | 3 |
| signal_store.py (SQLite) | 130 | 3 |
| evolution_tracker.py | 180 | 4-5 |
| decision_journal.py | 180 | 5-6 |
| config.yaml | 40 | 2 |
| Tests (25 tests) | 250 | 2-4 |
| **TOTAL** | **~2,310** | |

**The smallest codebase. 690 LOC under budget.**

#### Dev Hours

| Activity | Hours | % |
|---------|-------|---|
| Feature development | 40 | 62% |
| Targeted testing (25 tests) | 7 | 11% |
| Manual testing (weekly pipeline run) | 10 | 15% |
| Type hints + documentation | 3 | 5% |
| Debugging + maintenance | 3 | 5% |
| Git hygiene | 1 | 2% |
| **TOTAL** | **~64** | |

At 2-4 hrs/week = **16-32 weeks = 4-8 months**. **The fastest to complete.**

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| MiniLM 512-token limit truncates financial articles | 35% | MEDIUM (reduced dedup quality) | Summarize before embedding (EnvScan already does this) |
| Rule-based accuracy ceiling (75%) limits report quality | 40% | MEDIUM | Upgrade to SetFit when measured; path is clear |
| Reports feel mechanical/template-like | 50% | LOW (content > prose) | Accept this trade-off; data quality is maintained |
| SQLite slow on analytical evolution queries (Year 2+) | 15% | LOW (add DuckDB layer when needed) | DuckDB migration is zero-cost (same Parquet files) |
| Missing cross-domain insights due to no graph analysis | 25% | MEDIUM | SQL JOINs capture most patterns; NetworkX is available |

**Aggregate Risk Level**: **LOW**. The highest-probability risk (mechanical reports) has low impact. The main capability risk (MiniLM truncation, rule-based ceiling) has clear upgrade paths.

#### 6-Month Milestones

| Month | Milestone | Deliverable |
|-------|----------|------------|
| M1 | Schema + Normalize + Health Check | unified_signals.json from both sources |
| M2 | Classification + Sector Mapping + Orchestrator | End-to-end pipeline |
| **M2 (Week 3-4)** | **FIRST WEEKLY REPORT** | **Basic investment direction report** |
| M3 | Synthesis + Report polish + SQLite store | Improved reports + persistent storage |
| M4 | Evolution tracking | Weekly signal deltas |
| M5 | Cross-domain analysis (SQL JOINs) + refinement | Convergence detection via relational queries |
| M6 | Decision Journal + calibration | Prediction tracking |

**First usable report**: **Week 3-4 (Month 2)**. Same as Balanced scenario.

---

### SCENARIO COMPARISON MATRIX

| Dimension | 3.A Cutting Edge | 3.B Balanced-Tech | 3.C Proven Stack |
|-----------|:----------------:|:-----------------:|:----------------:|
| **First report** | Week 10-12 | **Week 3-4** | **Week 3-4** |
| **Total LOC** | ~3,450 | ~2,470 | ~2,310 |
| **Dev hours** | ~100 | ~70 | ~64 |
| **New dependencies** | 8 (SetFit, DuckDB, NetworkX, Ollama, Snakemake, eKoNLPy, KcELECTRA, Qwen3) | 1 (BGE-M3 model swap) | 0 |
| **Peak RAM** | ~36 GB | ~3 GB | ~1.3 GB |
| **Classification accuracy** | 85-92% | 70-80% (upgradeable) | 70-80% |
| **Embedding quality (MTEB)** | 63.0 | 63.0 | 56.0 |
| **Report quality** | Highest (AI narrative) | Good (structured template) | Basic (template only) |
| **Determinism** | Partial (LLM sections non-deterministic) | **100%** | **100%** |
| **3-month hiatus recovery** | 4-8 hours | **30-60 minutes** | **30-60 minutes** |
| **Risk level** | HIGH | **LOW-MEDIUM** | LOW |
| **Upgrade headroom** | Low (already at ceiling) | **High (clear triggers)** | High (everything upgradeable) |
| **Fits 6-month / 2-4hr/wk** | NO (needs 6-12 months) | **YES** | **YES** |
| **Within 3,000 LOC budget** | NO (+450 over) | **YES** (530 headroom) | **YES** (690 headroom) |

---

## PHASE 4: Final Recommendation

---

### 1. SELECTED SCENARIO: 3.B Balanced-Tech

**Justification**:

The selection is driven by three decisive factors:

**Factor 1: The developer's time is the binding constraint, not technology capability.**

At 2-4 hrs/week, every hour of learning curve costs 1-2 weeks of calendar time. Scenario 3.A (Cutting Edge) consumes 12% of its budget on learning alone and exceeds both the 6-month timeline and the 3,000 LOC budget. Scenario 3.C (Proven Stack) fits the constraints but leaves quality improvement on the table unnecessarily -- specifically, the BGE-M3 embedding upgrade that costs zero learning time.

Scenario 3.B captures 95% of the Proven Stack's speed and predictability while adding the single most impactful technology upgrade (BGE-M3) that all four perspectives unanimously endorsed.

**Factor 2: Trigger-based upgrades preserve optionality without premature commitment.**

Scenario 3.B does not reject cutting-edge technologies -- it sequences them rationally. SetFit, DuckDB, NetworkX, and even Ollama narrative are all available as measured upgrades when specific, concrete triggers are met. This is the "evolutionary architecture + 2 Big Bang elements" pattern from Branch 2, validated by 6 independent research analyses.

**Factor 3: First report at Week 3-4 maximizes learning velocity.**

The first weekly report is the most important deliverable in the entire project. It reveals: (a) whether the source system data is suitable for investment direction synthesis, (b) which STEEPs categories have the most signal volume, (c) whether rule-based classification is adequate or insufficient, (d) what the developer actually needs from the system. Every week of delay before the first report is a week of building in the dark.

Scenarios 3.B and 3.C both achieve first-report at Week 3-4. Scenario 3.A delays to Week 10-12 -- **a 6-8 week delay that provides zero learning value**.

---

### 2. COMPLETE TECHNOLOGY STACK

#### Core Dependencies (requirements.txt)

```
# === CORE (Day 1) ===
sentence-transformers>=3.0.0        # BGE-M3 embeddings
pyarrow>=17.0.0                     # Parquet read/write
Jinja2>=3.1.4                       # Report template rendering
PyYAML>=6.0.2                       # Configuration files
kiwipiepy>=0.18.0                   # Korean morphological analysis

# === ALREADY IN SOURCE SYSTEMS (inherited, not new) ===
bertopic>=0.16.4                    # Topic modeling (from GlobalNews)
hdbscan>=0.8.38                     # Clustering (from GlobalNews)
umap-learn>=0.5.7                   # Dimensionality reduction (from GlobalNews)
scikit-learn>=1.5.0                 # ML utilities (from GlobalNews)
pandas>=2.2.0                       # DataFrame operations (from both)

# === DEVELOPMENT ===
pytest>=8.3.0                       # Testing framework
mypy>=1.12.0                        # Static type checking (optional, recommended)

# === PHASE 2 TRIGGERS (install when needed) ===
# duckdb>=1.2.0                     # When analytical queries > 1s on SQLite
# setfit>=1.0.0                     # When rule-based accuracy < 70%
# networkx>=3.4                     # When multi-hop queries needed
# ollama (system package)           # When narrative enhancement desired
```

#### Model Downloads

```bash
# Day 1: BGE-M3 embedding model (~2.2 GB, one-time download)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# Already cached from source systems:
# - BERTopic uses the embedding model
# - Kiwi models download automatically on first use
```

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INVESTSCAN PIPELINE                       │
│                                                                   │
│  ┌──────────────┐  ┌──────────────────┐                          │
│  │ EnvironmentScan│  │GlobalNews-Crawling│   SOURCE SYSTEMS        │
│  │  (25,500 LOC) │  │  (25,400 LOC)    │   (NOT modified)        │
│  └──────┬───────┘  └────────┬─────────┘                          │
│         │ JSON               │ Parquet                            │
│  ═══════╪═══════════════════╪═══════ FILE-BASED IPC BOUNDARY ══  │
│         │                    │                                     │
│  ┌──────▼────────────────────▼──────┐                            │
│  │      health_check.py             │  LAYER 0: VALIDATION       │
│  │  (verify files exist + recent)   │  (~60 LOC)                 │
│  └──────────────┬───────────────────┘                            │
│                 │                                                  │
│  ┌──────────────▼───────────────────┐                            │
│  │    normalize_signals.py          │  LAYER 1: NORMALIZATION    │
│  │  + schema.py (frozen dataclass)  │  (~400 LOC)               │
│  │  EnvScan JSON → UnifiedSignal    │                            │
│  │  GNews Parquet → UnifiedSignal   │                            │
│  └──────────────┬───────────────────┘                            │
│                 │ unified_signals.json                             │
│  ┌──────────────▼───────────────────┐                            │
│  │    steeps_classifier.py          │  LAYER 2: CLASSIFICATION   │
│  │    sector_mapper.py              │  (~300 LOC)               │
│  │  Rule-based + keyword YAML       │                            │
│  └──────────────┬───────────────────┘                            │
│                 │ classified_signals.json                          │
│  ┌──────────────▼───────────────────┐                            │
│  │    synthesize_investment.py      │  LAYER 3: SYNTHESIS        │
│  │  Direction scoring + convergence  │  (~400 LOC)               │
│  │  BGE-M3 dedup + BERTopic topics  │                            │
│  └──────────────┬───────────────────┘                            │
│                 │ investment_synthesis.json                        │
│  ┌──────────────▼───────────────────┐                            │
│  │    generate_report.py            │  LAYER 4: PRESENTATION     │
│  │  Jinja2 templates → Markdown     │  (~400 LOC)               │
│  │  weekly_report.md.j2             │                            │
│  └──────────────┬───────────────────┘                            │
│                 │ invest-report-{date}.md                          │
│  ┌──────────────▼───────────────────┐                            │
│  │    signal_store.py (M3+)         │  LAYER 5: PERSISTENCE     │
│  │    evolution_tracker.py (M4+)    │  (~350 LOC)               │
│  │    decision_journal.py (M5+)     │                            │
│  └──────────────────────────────────┘                            │
│                                                                   │
│  ORCHESTRATION: investscan_run.py (~60 LOC, subprocess + launchd)│
│  TESTING: 25 pytest tests (schema parse + sector mapping)        │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. SIX NON-NEGOTIABLE DESIGN PRINCIPLES

These principles are derived from Branch 5.2 (Classical/Foundational Theory) and represent 30-263 years of validated knowledge. They are constraints, not trade-offs.

**Principle 1: IDEMPOTENCY** (ETL Theory, 30+ years)
> Same input must produce same output. Every time. No exceptions.

`synthesize_investment.py` must be a pure function. Same `unified_signals.json` in, same `investment_synthesis.json` out. No hidden mutable state, no non-deterministic processing, no external API calls during synthesis. This is why Ollama narrative is explicitly excluded from the core synthesis path -- LLM output is non-deterministic by nature.

**Implementation**: Frozen dataclasses for all inter-stage data. No `datetime.now()` calls inside synthesis logic (pass date as parameter). No random seeds without explicit control.

**Principle 2: SEPARATION OF CONCERNS** (Dijkstra, 52 years)
> Collection, Analysis, and Presentation are architecturally separate. InvestScan never modifies source systems.

Three systems, three responsibilities: EnvironmentScan collects, InvestScan analyzes, the report generator presents. If EnvironmentScan rewrites its JSON format tomorrow, only `normalize_signals.py` changes -- synthesis, scoring, and reporting are untouched.

**Implementation**: File-based IPC is the permanent integration boundary. No shared databases, no shared code, no bidirectional data flow.

**Principle 3: EVIDENCE CHAIN TRACEABILITY** (ETL Lineage + Superforecasting)
> Every directional output must be traceable to its source signals with full reasoning chain.

When the report says "bullish on semiconductors, conviction 0.72," the user must be able to trace: which 15 source articles from which sources with which STEEPs classifications contributed to this call, what weights were applied, and what the individual signal strengths were.

**Implementation**: Every `InvestmentDirection` object contains a `signal_ids: list[str]` field linking to source `UnifiedSignal` objects. The report template renders this chain.

**Principle 4: DECISION JOURNAL** (Tetlock's Superforecasting, 21 years)
> Systematic recording and scoring of predictions is the primary mechanism for long-term value creation.

This is not a nice-to-have feature for Month 6. It is the single most strategically important feature in InvestScan. Tetlock's 20-year study provides definitive evidence: untracked predictions yield no improvement. The Decision Journal records: date, sector, direction, confidence, evidence (signal IDs), time horizon, and later, outcome + Brier score.

**Implementation**: `decision_journal.py` writes structured JSON entries. Monthly retrospective compares predictions against actual KOSPI sector performance. Brier score computation is automated.

**Principle 5: FILE-BASED PIPELINE ARCHITECTURE** (Unix Philosophy, 57 years)
> Every inter-stage artifact is a readable, inspectable file. No opaque database-only state.

After 3 months away, the developer opens `output/2026-06-15/unified_signals.json` and immediately sees what the normalizer produced. No database connections, no query tools, no schema inspections. Every intermediate artifact is human-readable.

**Implementation**: JSON for structured data, Parquet for columnar analytics, Markdown for reports. SQLite is used for search and aggregation only -- the source of truth is always the file.

**Principle 6: SCHEMA VALIDATION AT NORMALIZATION BOUNDARY** (ETL Schema-on-Write)
> Because output influences financial decisions, data integrity must be enforced at ingestion with typed, validated, frozen data structures.

The normalization layer is the single point where external data (variable, uncontrolled) becomes internal data (typed, validated, immutable). Every `UnifiedSignal` must pass: (a) all required fields present, (b) all types correct, (c) all values in valid ranges (confidence 0.0-1.0, STEEPs in enum, etc.). Signals that fail validation are logged and excluded, never silently passed through.

**Implementation**: `@dataclass(frozen=True)` with `__post_init__` validation. `SchemaValidationError` raised on invalid input. Validation failures logged with full context for debugging.

---

### 4. THEORETICAL FRAMEWORK FOR THE PRD

The PRD should be grounded in four theory clusters identified in Branch 5.2:

#### Cluster A: "Why InvestScan Can Work" (Justification)

| Theory | Core Insight | InvestScan Application |
|--------|-------------|----------------------|
| **EMH Processing Lags** (Fama 1970, augmented by Lo 2004) | Markets incorporate complex, cross-domain, multi-language information slowly -- weeks to months | InvestScan targets this lag: public signals, private synthesis |
| **Reflexivity** (Soros 1987) | News signals CREATE market movements, not just reflect them; feedback loops amplify convergent signals | Cross-domain convergence detection; super-linear weighting of multi-STEEPs signals |
| **Shannon Information Theory** (1948) | Not all sources carry equal information; novelty is inversely proportional to probability | Source-quality weighting; deduplication as compression; novelty scoring as information content |

**PRD Positioning**: InvestScan does not claim markets are inefficient. It claims markets are **slow** at incorporating complex, cross-domain, multi-language macro signals -- and 50+ years of empirical evidence supports this claim.

#### Cluster B: "How InvestScan Should Work" (Architecture)

| Theory | Core Insight | InvestScan Application |
|--------|-------------|----------------------|
| **Unix Philosophy** (Thompson & Ritchie, 1969) | Do one thing well; compose via standard interfaces | File-based modular pipeline; each component independently testable |
| **ETL Patterns** (Kimball 1996) | Idempotent transformations; schema validation; data lineage | Frozen dataclasses; evidence chains; reproducible synthesis |
| **Separation of Concerns** (Dijkstra 1974) | Decompose by distinct responsibilities | Collection/Analysis/Presentation separation; no source system modification |

#### Cluster C: "How to Know If InvestScan Works" (Evaluation)

| Theory | Core Insight | InvestScan Application |
|--------|-------------|----------------------|
| **Superforecasting** (Tetlock 2005) | Track predictions; calibrate confidence; learn from errors | Decision Journal; Brier score; monthly retrospective |
| **Bayesian Updating** (Bayes 1763) | Start with base rates; update incrementally with evidence | Signal evolution tracking; confidence as posterior probability |
| **Signal Detection Theory** (Green & Swets 1966) | ROC/AUC framework distinguishes real detection from noise | Month 7+ evaluation: are directional calls better than random? |

#### Cluster D: "Where InvestScan Creates Unique Value" (Positioning)

| Theory | Core Insight | InvestScan Application |
|--------|-------------|----------------------|
| **Bounded Rationality** (Simon 1956) | Humans cannot process 500 signals across 133 sources in 14 languages | InvestScan as "cognitive prosthesis" -- extends information acquisition, processing, and temporal memory |
| **Systems Thinking** (Meadows 1972/2008) | STEEPs dimensions are interconnected subsystems with feedback loops | Cross-domain convergence is the unique analytical edge; leverage point hierarchy maps to L1-L5 signal layers |
| **Value Investing** (Graham & Dodd 1934) | "Prospects" dimension of fundamental analysis requires systematic macro scanning | InvestScan fills the qualitative gap that MPT and quantitative analysis cannot address |

**The master framing for the PRD**:

> InvestScan is a **bounded rationality extension device** (Simon 1956) that exploits **documented market processing lags** (Fama/Lo) to synthesize **cross-domain macro signals** (Meadows/STEEPs) into **directional investment intelligence**, validated through **empirical calibration** (Tetlock/SDT). Its value proposition holds regardless of market efficiency: even in a perfectly efficient market, it prevents the investor from making cognitively bounded mistakes by structuring information acquisition, forcing explicit reasoning, and enabling calibrated self-assessment.

---

### 5. FOUR DECISIONS THE USER MUST MAKE

These are genuine unresolved tensions where the research provides evidence for multiple positions. The Supreme Technical Moderator presents the trade-offs; the user decides.

---

**DECISION 1: BGE-M3 Embedding Dimension -- 1024 Full or 768 Truncated?**

BGE-M3 outputs 1024-dimensional embeddings by default. This is higher dimensionality than MiniLM's 384-dim and consumes 2.7x more storage per signal. For InvestScan's expected volume (~10,000-30,000 signals over 2 years), this means:

| Dimension | Storage / 30K signals | MTEB Quality | Dedup Precision |
|-----------|---------------------|-------------|-----------------|
| 384 (MiniLM) | ~46 MB | 56.0 | Baseline |
| 768 (BGE-M3 truncated) | ~92 MB | ~61.5 | Better |
| 1024 (BGE-M3 full) | ~123 MB | 63.0 | Best |

Storage is negligible on modern hardware. The real question is: does 1024-dim improve dedup/similarity quality enough to justify the larger index? For <30K signals, the answer is almost certainly "use full 1024 -- storage is irrelevant."

**Moderator recommendation**: Use full 1024-dim. The storage cost is trivial and the quality improvement is measurable.

**But the user should confirm**: Are there downstream tools or processes that expect 384-dim embeddings? If any custom similarity functions are hardcoded to 384-dim, the switch requires updating them.

---

**DECISION 2: STEEPs-First vs Sentiment-First Signal Processing?**

Two legitimate approaches to signal classification:

| Approach | Philosophy | Accuracy on Direction | Theoretical Basis |
|----------|-----------|----------------------|-------------------|
| **STEEPs-first** | Classify WHAT the signal is about, THEN derive direction | Direction from structural analysis | Systems Thinking (Meadows); 90-95% of sentiment-return correlation is spurious |
| **Sentiment-first** | Classify HOW the signal FEELS, THEN categorize by domain | Direction from emotional valence | Financial sentiment analysis (FinBERT); intuitive for investors |

Branch 5.1 provides a devastating finding: raw sentiment-return correlations of 0.45-0.73 deflate to 0.034-0.048 after controlling for confounders. This means **sentiment is nearly useless as a standalone prediction mechanism**.

However, sentiment CAN be valuable as a **secondary enrichment** after STEEPs classification. "This Technology signal about semiconductor supply chains has bearish sentiment" adds nuance to a structurally classified signal.

**Moderator recommendation**: STEEPs-first (classify by domain), with optional sentiment enrichment added later. This aligns with Branch 5.1's "STEEPs-first, NOT sentiment-first" verdict.

**The user decides**: If the user's investment intuition is more sentiment-driven ("I want to know if the market feels bullish or bearish"), then sentiment should be elevated. If the user's investment intuition is more structural ("I want to know what forces are shaping each sector"), then STEEPs-first is correct.

---

**DECISION 3: Weekly Report Depth -- Comprehensive vs Actionable?**

Two report philosophies:

| Style | Length | Content | Reading Time | Theoretical Basis |
|-------|--------|---------|-------------|-------------------|
| **Comprehensive** | 3,000-5,000 words | Full signal list, all evidence chains, all STEEPs dimensions, all sectors, all time horizons | 30-45 minutes | Shannon (maximize information); Tetlock (comprehensive evidence) |
| **Actionable** | 500-1,000 words | Top 5 signals, 3 strongest directional calls, key convergences only | 5-10 minutes | Simon (bounded rationality); satisficing (enough to not miss anything big) |

The Comprehensive approach preserves maximum information but risks the "TL;DR" effect -- the developer may stop reading 5,000-word reports after month 2. The Actionable approach risks missing important signals but respects the developer's 2-4 hrs/week constraint.

**Moderator recommendation**: **Executive Summary (actionable, 500 words) + Full Appendix (comprehensive, 3,000 words)**. The developer reads the summary weekly; the appendix is available for deep-dives when a signal warrants investigation.

**The user decides**: The Jinja2 template structure. Does the developer want to read a single document top-to-bottom, or a summary-with-appendix structure?

---

**DECISION 4: Signal Evolution Window -- 4 Weeks or 12 Weeks?**

Signal evolution tracking requires defining the "lookback window" -- how far back should InvestScan track signal state changes?

| Window | Signals Tracked | Storage | Analytical Complexity | Theoretical Basis |
|--------|----------------|---------|----------------------|-------------------|
| **4 weeks** | ~400-1,200 | Minimal | Simple delta comparison | Short-term macro (L1-L2 signals) |
| **12 weeks** | ~1,200-3,600 | Moderate | Trend detection, lifecycle modeling | Medium-term macro (L3-L4 signals, WISDOM lifecycle) |
| **26 weeks** | ~2,600-7,800 | Larger | Full lifecycle + seasonal patterns | Long-term structural shifts (L4-L5 signals) |

The WISDOM framework (Branch 5.1) classifies signals along a lifecycle: Emerging -> Strengthening -> Mainstream -> Weakening -> Fading. Detecting this lifecycle requires at least 8-12 weeks of history. A 4-week window can only detect "strengthening" and "weakening" -- it cannot distinguish a true emerging signal from a temporary fluctuation.

**Moderator recommendation**: **12-week rolling window**. This captures one full quarter of signal history, aligns with the mid-term investment horizon (L3_mid: 1-6 months), and is sufficient for lifecycle detection without overwhelming storage.

**The user decides**: If the user's investment horizon is primarily short-term (1-4 weeks), a 4-week window is sufficient and simpler. If the user's investment horizon includes medium-to-long-term positioning (1-6+ months), the 12-week window is necessary.

---

### SUMMARY

| Dimension | Decision |
|-----------|---------|
| **Scenario** | 3.B Balanced-Tech |
| **Embedding** | BGE-M3 (one-line swap, Day 1) |
| **Classification** | Rule-based (start) -> SetFit (when <70% accuracy) |
| **Storage** | Parquet -> SQLite FTS5 -> DuckDB (progressive) |
| **Report** | Jinja2 only (deterministic) |
| **Orchestration** | subprocess + launchd |
| **LOC budget** | ~2,470 (530 headroom) |
| **Dev hours** | ~70 (fits 6 months at 2.7 hrs/week avg) |
| **First report** | Week 3-4 |
| **Risk** | LOW-MEDIUM |
| **Design principles** | Idempotency, Separation of Concerns, Evidence Traceability, Decision Journal, File-based Pipeline, Schema Validation |
| **Theoretical frame** | Bounded rationality cognitive prosthesis (Simon) exploiting EMH processing lags (Fama/Lo) via cross-domain synthesis (Meadows/STEEPs) with empirical calibration (Tetlock/SDT) |

---

*This analysis synthesizes findings from 10 PHASE 1 research branches: Core Tech (Branch 1), Architecture (Branch 2), Dev Workflow (Branch 3), Tech Debt (Branch 4), Modern Theory (Branch 5.1), and Classical Theory (Branch 5.2). Total research corpus: ~80,000 words across 6 analytical documents.*
