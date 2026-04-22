# InvestScan: PHASE 2 + 3 + 4 -- Implementation Discussion, Scenarios, and Final Guide

> **Supreme Implementation Moderator**
> **Date**: 2026-03-28
> **Input**: 10 coding branches (5 branches x 2 coders each), Phase 1 consolidated results
> **Output**: Four-perspective discussion, three coding scenarios, final implementation guide
> **Status**: COMPLETE

---

## PHASE 2: Four Implementation Perspectives

The question is no longer "what to build" (decided in Round 3) but "how to code it." Ten coding branches produced concrete Python code, shell scripts, templates, and test suites. This phase evaluates those implementations from four angles.

---

### 2.A: CODE QUALITY PRIORITY

> "Which coding patterns from Branch 1-5 produce the most maintainable code?"

#### Verdict: Aggressive Schema + Conservative Parsers + Big Bang CLI

**The strongest quality patterns from each branch:**

**Branch 1 (Schema)**: The frozen dataclass with `slots=True` is unambiguously correct. Immutable data objects eliminate an entire class of bugs (accidental mutation during pipeline stages). The `StrEnum` for STEEPs/EvolutionState/SourceSystem provides compile-time-like safety at zero runtime cost. The `content_hash` on `UnifiedSignal` makes deduplication deterministic and testable. This is the highest-quality code in all 10 branches.

**Branch 1 (Parsers)**: The structural pattern matching for STEEPs normalization (`match raw.strip(): case "T" | "T_Technological":`) is both the most readable and the most maintainable pattern for the 6-format parsing problem. The auto-scale detection for pSST (`if score > 10: assume 0-100`) is pragmatic but carries a subtle risk: a score of exactly 10.0 is ambiguous. The defensive `.get()` with fallbacks throughout the parsers is the correct defensive posture for external data.

**Branch 2 (Orchestration)**: The Big Bang CLI's `PipelineState` dataclass with JSON checkpoint serialization is the single most important quality decision across all branches. Without checkpoint/resume, a failure at step 4 (report generation) forces re-running steps 1-3 (3.5 hours of EnvScan + GlobalNews). This is not a quality luxury; it is a correctness requirement. The `StepResult` with explicit status enum (`PENDING/RUNNING/COMPLETED/FAILED/SKIPPED`) prevents the ambiguous states that shell scripts suffer from.

**Branch 3 (Report)**: The frozen dataclass DTOs (`SignalView`, `SectorView`, `EvidenceChainView`) between synthesis and template rendering create a clean separation of concerns. The template does not touch raw data. The renderer does not know about Jinja2. This is textbook Model-View separation and the correct pattern for a system where the report format will evolve significantly over the first 12 weeks.

**Branch 4 (Testing)**: The 10 contract tests guarding schema parsing are the highest-value tests possible. They protect the system boundary where external data enters. The philosophy "crash loud on contract violation, graceful degradation everywhere else" is the correct testing posture for a solo-dev financial tool.

**Branch 5 (Integration)**: The Simple integration approach (shell orchestrator calling Python modules) has one quality advantage: separation of orchestration from business logic. The Python modules are testable independently of how they are invoked.

**Quality Anti-Patterns Found:**

1. **Branch 2.1 (Evolutionary shell)**: Hardcoded paths in shell script. Config management via env vars is fragile. This is acceptable for Week 1 prototyping but becomes technical debt by Week 4.
2. **Branch 3.2 (Comprehensive report)**: The `signal_retrospective` section adds ~150 LOC for a feature whose value is unproven. Quality code is code that exists for a reason.
3. **Branch 5.1 (Deep workflow.md)**: 460 LOC of workflow orchestration duplicates what the Python CLI already does. Two orchestration layers creates ambiguity about which is the SOT.

---

### 2.B: SHIPPING SPEED PRIORITY

> "What is the fastest path to first useful report?"

#### Verdict: Shell Orchestrator Week 1, Python Modules Week 2-7, CLI Migration Week 8

**Fastest path analysis:**

| Week | Action | Output |
|------|--------|--------|
| W1 | Copy Branch 2.1 shell script (`run.sh`), hardcode paths to real EnvScan + GlobalNews directories | Manual pipeline execution with real data |
| W2 | Implement Branch 1.1 schema (`schema.py` + `normalizers.py`) for WF4 database.json ONLY (the richest format) | 1 of 6 parsers working |
| W3 | Implement WF1 database.json parser + basic dedup (content_hash) | 2 of 6 parsers, signal dedup functional |
| W4 | Implement Branch 3.1 minimal report (`generate_report.py` + Jinja2 template) with hardcoded sector mapping | **FIRST USEFUL REPORT** |
| W5 | Add remaining 4 parsers (WF1 output, WF4 priority-ranked, WF4 evolution, GlobalNews Parquet) | All 6 formats normalized |
| W6 | Implement `synthesize_investment.py` (rule-based sector mapping + direction scoring) | Synthesis replaces hardcoded mapping |
| W7 | End-to-end integration test on real data, fix bugs | Reliable pipeline |
| W8 | Migrate shell to Big Bang CLI (Branch 2.2) with checkpoint/resume | Production-grade orchestration |

**First useful report: Week 4** (28 days from start, ~16 dev hours invested).

This is achieved by a critical shortcut: the Week 4 report uses only WF4 database.json signals (the richest format, 200+ signals) with hardcoded sector mapping. It is not complete, but it answers the fundamental question: "Is a synthesized, sector-organized report of macro signals useful to me?"

**Speed Anti-Patterns to Avoid:**

1. **Do NOT start with the CLI framework.** Click, YAML config, subcommands -- all can wait until Week 8. The shell script gets you to Week 4's first report faster.
2. **Do NOT implement all 6 parsers before generating a report.** WF4 database.json alone has enough signals for a useful report.
3. **Do NOT write tests before Week 7.** The first 6 weeks are about discovering whether the pipeline produces useful output. Testing code that might be rewritten is wasted effort.
4. **Do NOT implement the decision journal before Week 8.** The journal is a Phase 1 feature, but it has zero dependency on pipeline correctness. Build it after the report works.

---

### 2.C: FINANCIAL SAFETY PRIORITY

> "Where must code be bulletproof because errors = money lost?"

#### Verdict: Three Critical Code Paths, Everything Else Can Crash

InvestScan does not execute trades. It does not manage portfolios. It produces directional intelligence reports that inform human investment decisions. The financial risk is indirect: a misleading report could cause a bad investment decision. The damage path is:

```
Wrong signal normalization -> Wrong direction scoring -> Misleading sector direction in report -> User makes bad investment decision
```

**Critical Path 1: pSST Score Normalization**

The most dangerous code in the entire system is `_normalize_psst_score()`. The source data uses THREE different scales:

- WF4 database.json: 0-100 (integer)
- WF4 priority-ranked: 0-10 (float)
- GlobalNews: 0-1 (float)

If the auto-detection fails (a pSST score of 10 could be 10/100 = 0.10 OR 10/10 = 1.0), a low-confidence signal becomes high-confidence or vice versa. This directly affects direction scoring.

**Required safeguard**: Never use auto-detection in production. Each parser explicitly passes the scale parameter: `_normalize_psst_score(raw.get("psst_score"), scale="0-100")`. The auto-detection exists only as a fallback for unknown formats. Branch 1.1's code already does this correctly for WF4 database (`scale="0-100"`), but the auto-detection default is still dangerous.

**Critical Path 2: Cross-Source Deduplication Threshold**

If the dedup threshold (content hash or title similarity) is too aggressive (e.g., 0.70), distinct signals about related topics get merged, reducing signal diversity. If too conservative (e.g., 0.95), duplicate signals inflate conviction scores by appearing to have multi-source convergence when they are actually the same signal reported twice.

**Required safeguard**: Content hash dedup (exact match on normalized title + abstract) for certain dedup. Title similarity dedup (cosine > 0.85) only for cross-source dedup with logging. Every dedup decision must be recorded in the pipeline log so the user can audit why signals were merged.

**Critical Path 3: Direction Conviction Scoring**

The synthesis module assigns direction (bullish/bearish/neutral) and conviction (0-1) per sector. If confidence averaging is naive (mean of all signal confidences), a single high-confidence signal can dominate 20 low-confidence signals, producing a misleading conviction score.

**Required safeguard**: Weighted median, not mean. Weight by source diversity (multi-source convergence increases weight) and signal layer (L3+ signals weighted higher than L1-L2). Report conviction with explicit uncertainty: "Bullish (60% conviction, based on 3 independent sources)" not just "Bullish."

**Everything Else Can Crash:**

- Report generation failure: No financial impact. Re-run after fix.
- Journal failure: No financial impact. Manual entry as fallback.
- CLI failure: No financial impact. Run modules manually.
- Health check failure: No financial impact. Warns user, does not produce misleading data.

**The financial safety rule**: Code that transforms numerical scores or produces directional calls must be tested. Code that formats, presents, or orchestrates does not need the same rigor.

---

### 2.D: LONG-TERM SUSTAINABILITY PRIORITY

> "What keeps this running for 2+ years with minimal maintenance?"

#### Verdict: Schema Versioning + Defensive Parsing + Zero ML Dependencies in Core

**The #1 sustainability risk is upstream schema drift.** EnvScan and GlobalNews are actively developed. Their output schemas WILL change. Every format they have today was not the format they had 3 months ago (WF4 was added recently; GlobalNews Parquet output is not yet production).

**Sustainability Pattern 1: Parser Registry with Version Detection**

```python
# Instead of: if "steeps" in raw -> WF4 format
# Do: explicit format version detection

def detect_format(data: dict) -> str:
    """Detect which of the 6 known formats this data matches."""
    if "steeps" in data and "psst_score" in data:
        return "envscan_wf4_database"
    if "preliminary_category" in data and "content" in data:
        return "envscan_wf1_database"
    if "preliminary_category" in data and "summary" in data:
        return "envscan_wf1_output"
    # ... etc
    raise ValueError(f"Unknown signal format: keys={list(data.keys())[:5]}")
```

When a new format appears, the `detect_format` function fails loudly with the unknown keys, telling the developer exactly what changed.

**Sustainability Pattern 2: Defensive Parsing with Explicit Defaults**

Every `.get()` call in the parsers should have a documented default with a rationale:

```python
confidence_score=_normalize_psst_score(
    raw.get("psst_score"),  # Missing in WF1 database format
    scale="0-100"
) if "psst_score" in raw else 0.5,  # 0.5 = "unknown" (not 0.0 = "zero confidence")
```

The default `0.5` (mid-confidence) instead of `0.0` (zero confidence) is a sustainability decision: it prevents signals from being silently filtered out when a field disappears from upstream.

**Sustainability Pattern 3: Zero ML in the Core Pipeline**

Branch 1.1's structural pattern matching for STEEPs classification and rule-based sector mapping are dramatically more sustainable than any ML-based approach. A rule-based mapper breaks visibly (wrong sector) and fixes in 5 minutes (add a rule). An ML classifier degrades silently (gradually worse predictions) and fixes in 5 hours (retrain, evaluate, deploy).

For a 2-4 hr/week solo developer, the maintenance budget for ML models is zero. Keep ML in the upstream systems (EnvScan, GlobalNews) where it is already maintained. InvestScan's core pipeline should be pure Python with explicit rules.

**Sustainability Pattern 4: JSONL Journal Over SQLite**

Branch 3's JSONL decision journal is more sustainable than SQLite because:
- No migration scripts when schema evolves
- Append-only (no UPDATE/DELETE corruption risk)
- Human-readable with `cat` / `grep` (debuggable without tools)
- Git-diffable (version history for free)
- No driver dependency (json is stdlib; sqlite3 is stdlib too, but schema management is not)

**Sustainability Anti-Patterns:**

1. **SQLite FTS5 for signal evolution tracking**: Requires schema migrations, index maintenance, and database file management. JSONL with in-memory filtering is sufficient for <10,000 signals.
2. **Plotly.js for HTML reports**: Plotly CDN dependency or 3MB inline JS. matplotlib static images are sustainable; interactive charts are a maintenance burden.
3. **Click CLI with 5+ subcommands in Month 1**: Overcommits the CLI interface before usage patterns are known. Start with 2 commands (`run` and `status`), add more when demonstrated need.

---

### UNIFIED COMPARISON TABLE

| Pattern / Decision | Quality (A) | Speed (B) | Safety (C) | Sustainability (D) | Zone |
|---|---|---|---|---|---|
| **Frozen dataclass schema** | Essential | Neutral | Essential | Essential | **GREEN (4/4)** |
| **StrEnum for categories** | Essential | Neutral | Improves | Essential | **GREEN (4/4)** |
| **Content-hash dedup** | Good | Fast to implement | Essential | Essential | **GREEN (4/4)** |
| **Explicit pSST scale per parser** | Good | Neutral | Essential | Essential | **GREEN (4/4)** |
| **Defensive `.get()` with documented defaults** | Good | Neutral | Improves | Essential | **GREEN (4/4)** |
| **Jinja2 Markdown report** | Good | Fast to implement | Neutral | Essential | **GREEN (4/4)** |
| **JSONL decision journal** | Good | Fast to implement | Neutral | Essential | **GREEN (4/4)** |
| **JSON checkpoint for pipeline state** | Essential | +1 week delay | Improves | Essential | **GREEN (4/4)** |
| **10 contract tests on parsers** | Essential | -4 hrs first month | Essential | Essential | **GREEN (4/4)** |
| **Frozen DTOs for report rendering** | Good | Neutral | Neutral | Good | **GREEN (4/4)** |
| **Big Bang CLI (Click)** | Good | -1 week vs shell | Neutral | Good | **YELLOW (3/4)** |
| **Rule-based sector mapping** | Acceptable | Fast | Acceptable | Essential | **YELLOW (3/4)** |
| **Shell script for Week 1-3** | Poor | Essential | Neutral | Poor | **YELLOW (3/4)** |
| **Structural pattern matching** | Essential | Neutral | Good | Neutral (Python 3.10+ only) | **YELLOW (3/4)** |
| **15 sector mapping tests** | Good | -4 hrs | Good | Good | **YELLOW (3/4)** |
| **Signal evolution tracking** | Good | -16 hrs | Neutral | Maintenance burden | **YELLOW (2.5/4)** |
| **SQLite for journal** | Good | Neutral | Neutral | Maintenance burden | **RED (2/4)** |
| **HTML interactive report** | Neutral | -20 hrs | Neutral | Maintenance burden | **RED (1.5/4)** |
| **ML-based STEEPs classifier** | Neutral | -12 hrs | Risk | Anti-sustainable | **RED (1/4)** |
| **Auto-scale pSST detection** | Poor | Fast | Dangerous | Fragile | **RED (1/4)** |
| **50+ tests in Month 1** | Premature | -20 hrs | Marginal gain | Neutral | **RED (1.5/4)** |

**Zone Summary:**

- **GREEN (10 items)**: Implement in every scenario. These are unanimous best practices.
- **YELLOW (5 items)**: Implement with timing flexibility. Good patterns that may need sequencing.
- **RED (5 items)**: Avoid or defer. These add cost without proportional value in Phase 1.

---

## PHASE 3: Three Coding Scenarios

### SCENARIO 3.A: MAXIMUM QUALITY

> Full Big Bang CLI from Day 1, all frozen dataclasses, comprehensive testing, complete error handling, signal evolution tracking.

#### Module List with LOC and Dev Hours

| # | Module | File | LOC | Dev Hours | Month |
|---|--------|------|-----|-----------|-------|
| 1 | Schema + Enums | `investscan/schema.py` | 120 | 3 | M1-W1 |
| 2 | Config Loader | `investscan/config.py` | 80 | 2 | M1-W1 |
| 3 | CLI Framework | `investscan/cli.py` | 200 | 5 | M1-W1 |
| 4 | Pipeline Orchestrator | `investscan/orchestrator.py` | 350 | 8 | M1-W2 |
| 5 | WF1 Database Parser | `investscan/parsers/envscan_wf1_db.py` | 80 | 2 | M1-W2 |
| 6 | WF1 Output Parser | `investscan/parsers/envscan_wf1_out.py` | 70 | 2 | M1-W3 |
| 7 | WF4 Database Parser | `investscan/parsers/envscan_wf4_db.py` | 90 | 2 | M1-W3 |
| 8 | WF4 Priority Parser | `investscan/parsers/envscan_wf4_priority.py` | 60 | 1 | M1-W3 |
| 9 | WF4 Evolution Parser | `investscan/parsers/envscan_wf4_evo.py` | 70 | 1 | M1-W3 |
| 10 | GlobalNews Parser | `investscan/parsers/gnews_parquet.py` | 90 | 3 | M1-W4 |
| 11 | Parser Registry | `investscan/parsers/__init__.py` | 60 | 1 | M1-W4 |
| 12 | Signal Normalizer | `investscan/normalize.py` | 180 | 4 | M1-W4 |
| 13 | Content Deduplicator | `investscan/dedup.py` | 120 | 3 | M1-W5 |
| 14 | STEEPs Classifier | `investscan/steeps_classifier.py` | 150 | 4 | M1-W5 |
| 15 | Sector Mapper | `investscan/sector_mapper.py` | 200 | 5 | M2-W6 |
| 16 | Investment Synthesizer | `investscan/synthesize.py` | 300 | 8 | M2-W6-W7 |
| 17 | Report DTOs | `investscan/report_models.py` | 80 | 2 | M2-W7 |
| 18 | Report Generator | `investscan/generate_report.py` | 200 | 5 | M2-W8 |
| 19 | Jinja2 Template | `investscan/templates/weekly-report.md.j2` | 120 | 3 | M2-W8 |
| 20 | Decision Journal | `investscan/journal.py` | 200 | 5 | M2-W9 |
| 21 | Signal Evolution Tracker | `investscan/evolution.py` | 350 | 10 | M3-W10-W11 |
| 22 | Health Check | `investscan/health_check.py` | 120 | 3 | M3-W12 |
| 23 | Utilities | `investscan/utils.py` | 100 | 2 | M1-M3 |
| 24 | Contract Tests (Schema) | `tests/test_parsers.py` | 200 | 5 | M2-W7 |
| 25 | Sector Mapping Tests | `tests/test_sector_mapper.py` | 150 | 4 | M2-W8 |
| 26 | Synthesis Tests | `tests/test_synthesize.py` | 120 | 3 | M3-W11 |
| 27 | Evolution Tests | `tests/test_evolution.py` | 100 | 3 | M3-W12 |
| 28 | Report Tests | `tests/test_report.py` | 80 | 2 | M3-W12 |
| 29 | Integration Tests | `tests/test_pipeline_e2e.py` | 100 | 3 | M3-W13 |
| 30 | Conftest + Fixtures | `tests/conftest.py` | 80 | 2 | M2-W7 |
| | **TOTAL** | | **~3,920** | **~105** | |

**Test count**: ~50 tests across 7 test files.

#### Timeline

- **First useful report**: Week 8 (Month 2). The CLI + all parsers + synthesizer + report must all work before any report is produced.
- **Feature complete**: Week 13 (Month 3.5).
- **All tests passing**: Week 14 (Month 3.5).

#### Risk Assessment

| Risk | Probability | Impact |
|------|-------------|--------|
| Never produces first report (scope paralysis) | 30% | FATAL |
| CLI framework consumes Month 1 without value | 40% | HIGH -- delays all downstream |
| 50 tests require maintenance when schemas evolve | 25% | MEDIUM -- 2-4 hrs per schema change |
| Signal evolution tracker unused after building | 35% | MEDIUM -- 10 hrs wasted |
| Total dev hours exceed budget (105 > 96 available) | 50% | HIGH -- feature cut required |

**Scenario 3.A assessment**: This is the "enterprise quality for a solo developer" approach. The code will be beautiful, well-tested, and properly structured. The risk is that it takes 3.5 months to produce the first useful report, by which point motivation may have evaporated. Appropriate only if the developer has consistent 4+ hr/week availability and high tolerance for delayed gratification.

---

### SCENARIO 3.B: BALANCED IMPLEMENTATION

> Big Bang CLI for orchestration, aggressive schema (frozen dataclasses, StrEnum), minimal but targeted testing, JSONL journal, shell bootstrap for Week 1-3.

#### Module List with LOC and Dev Hours

| # | Module | File | LOC | Dev Hours | Month |
|---|--------|------|-----|-----------|-------|
| 1 | Shell Bootstrap | `run.sh` | 140 | 3 | M1-W1 |
| 2 | Schema + Enums | `investscan/schema.py` | 110 | 3 | M1-W1 |
| 3 | All Parsers (unified) | `investscan/normalizers.py` | 350 | 8 | M1-W2-W3 |
| 4 | Content Dedup | `investscan/dedup.py` | 80 | 2 | M1-W3 |
| 5 | STEEPs Classifier | `investscan/steeps_classifier.py` | 120 | 3 | M1-W4 |
| 6 | Sector Mapper | `investscan/sector_mapper.py` | 160 | 4 | M1-W4 |
| 7 | Investment Synthesizer | `investscan/synthesize.py` | 250 | 6 | M1-W5 |
| 8 | Report Generator | `investscan/generate_report.py` | 180 | 4 | M1-W6 |
| 9 | Jinja2 Template | `investscan/templates/weekly-report.md.j2` | 110 | 3 | M1-W6 |
| 10 | Config Loader | `investscan/config.py` | 60 | 1 | M2-W7 |
| 11 | CLI (Click) | `investscan/cli.py` | 160 | 4 | M2-W7 |
| 12 | Pipeline Orchestrator | `investscan/orchestrator.py` | 280 | 6 | M2-W8 |
| 13 | Decision Journal | `investscan/journal.py` | 150 | 4 | M2-W9 |
| 14 | Health Check | `investscan/health_check.py` | 100 | 2 | M2-W10 |
| 15 | Utilities | `investscan/utils.py` | 80 | 2 | M1-M2 |
| 16 | Contract Tests (10) | `tests/test_normalizers.py` | 160 | 4 | M2-W9 |
| 17 | Sector Tests (15) | `tests/test_sector_mapper.py` | 120 | 3 | M2-W10 |
| 18 | Conftest + Fixtures | `tests/conftest.py` | 60 | 1 | M2-W9 |
| 19 | Config YAML | `config/investscan.yaml` | 30 | 0.5 | M2-W7 |
| 20 | Package Init | `investscan/__init__.py` | 10 | 0.5 | M1-W1 |
| | **TOTAL** | | **~2,710** | **~64** | |

**Test count**: 25 tests across 2 test files + conftest.

#### Timeline

| Week | Deliverable | Cumulative Hours |
|------|-------------|-----------------|
| W1 | `run.sh` + `schema.py` -- shell runs, schema defined | 6 |
| W2 | `normalizers.py` (WF4 db + WF1 db) -- 2 of 6 parsers | 12 |
| W3 | `normalizers.py` (remaining 4 parsers) + `dedup.py` | 22 |
| W4 | `steeps_classifier.py` + `sector_mapper.py` | 29 |
| W5 | `synthesize.py` -- rule-based direction scoring | 35 |
| W6 | `generate_report.py` + Jinja2 template -- **FIRST REPORT** | 42 |
| W7 | `config.py` + `cli.py` -- Click CLI replaces `run.sh` | 47 |
| W8 | `orchestrator.py` -- checkpoint/resume | 53 |
| W9 | `journal.py` + 10 contract tests | 58 |
| W10 | `health_check.py` + 15 sector tests | 63 |
| W11-12 | Buffer: bug fixes, threshold tuning, report iteration | 68 |
| W13-24 | Maintenance: weekly runs, iterative improvements, conditional features | 72-80 |

- **First useful report**: Week 6 (42 dev hours, ~1.5 months at 3 hrs/week).
- **CLI with checkpoint/resume**: Week 8.
- **Full test suite**: Week 10.
- **Feature complete**: Week 10 (63 dev hours).
- **Remaining 14 weeks**: Maintenance, iteration, conditional feature evaluation.

#### Risk Assessment

| Risk | Probability | Impact |
|------|-------------|--------|
| Shell-to-CLI migration friction | 15% | LOW -- shell is temporary scaffolding |
| Report not useful (signals = noise) | 35% | HIGH but discovered at Week 6, not Week 14 |
| Parsers break on schema drift | 30% | LOW -- 2-4 hrs fix with contract tests catching it |
| 25 tests insufficient coverage | 20% | LOW -- tests cover the money paths |
| Dev hours slightly exceed budget | 15% | LOW -- 14-week buffer absorbs overrun |

**Scenario 3.B assessment**: This is the "right tool for a solo pastor-developer" approach. It produces a useful report by Week 6, has production-grade orchestration by Week 8, and leaves 14 weeks of buffer for real-world iteration. The shell-to-CLI migration adds 3 hours of "throwaway" work, but it buys 4 weeks of faster iteration during the discovery phase. The 25 targeted tests cover the two critical code paths (parsing and sector mapping) without the maintenance burden of comprehensive coverage.

---

### SCENARIO 3.C: MINIMUM VIABLE CODE

> Shell script orchestration throughout, conservative dicts (no frozen dataclasses), 15 tests on critical paths only, Markdown report without Jinja2 templating.

#### Module List with LOC and Dev Hours

| # | Module | File | LOC | Dev Hours | Month |
|---|--------|------|-----|-----------|-------|
| 1 | Shell Orchestrator | `run.sh` | 180 | 4 | M1-W1 |
| 2 | Signal Reader | `investscan/read_signals.py` | 200 | 5 | M1-W2 |
| 3 | Simple Normalizer | `investscan/normalize.py` | 150 | 4 | M1-W3 |
| 4 | Sector Mapper | `investscan/sector_mapper.py` | 120 | 3 | M1-W3 |
| 5 | Direction Scorer | `investscan/score_direction.py` | 150 | 4 | M1-W4 |
| 6 | Report Writer | `investscan/write_report.py` | 200 | 5 | M1-W4 |
| 7 | Decision Journal | `investscan/journal.py` | 100 | 3 | M2-W5 |
| 8 | Health Check | `investscan/health_check.py` | 80 | 2 | M2-W6 |
| 9 | Config (flat YAML) | `config/investscan.yaml` | 20 | 0.5 | M1-W1 |
| 10 | Utilities | `investscan/utils.py` | 60 | 1.5 | M1-M2 |
| 11 | Parsing Tests (10) | `tests/test_normalize.py` | 120 | 3 | M2-W7 |
| 12 | Mapping Tests (5) | `tests/test_sector_mapper.py` | 60 | 2 | M2-W7 |
| 13 | Package Init | `investscan/__init__.py` | 5 | 0.5 | M1-W1 |
| | **TOTAL** | | **~1,445** | **~37.5** | |

**Test count**: 15 tests across 2 test files.

**Key architectural differences from 3.B:**

- **No frozen dataclasses**: Signals are plain dicts throughout. Easier to write, harder to debug when a typo creates a wrong key.
- **No Click CLI**: Shell script is the permanent orchestrator. No checkpoint/resume. No `--resume` flag.
- **No Jinja2**: Report is assembled via f-strings in Python. Template changes require code changes.
- **No STEEPs classifier module**: Uses EnvScan's native STEEPs directly. GlobalNews signals get `steeps_category = "UNKNOWN"`.
- **No parser registry**: Single `read_signals.py` with if/elif chains for each format.

#### Timeline

| Week | Deliverable | Cumulative Hours |
|------|-------------|-----------------|
| W1 | `run.sh` + `config.yaml` | 4.5 |
| W2 | `read_signals.py` -- reads WF4 + WF1 formats | 9.5 |
| W3 | `normalize.py` + `sector_mapper.py` | 16.5 |
| W4 | `score_direction.py` + `write_report.py` -- **FIRST REPORT** | 25.5 |
| W5 | `journal.py` -- decision journal | 28.5 |
| W6 | `health_check.py` | 30.5 |
| W7 | 15 tests | 35.5 |
| W8-24 | Maintenance, iteration | 38-45 |

- **First useful report**: Week 4 (25.5 hours, ~1 month at 3 hrs/week).
- **Feature complete**: Week 7 (35.5 hours).
- **Remaining 17 weeks**: Pure maintenance and iteration.

#### Risk Assessment

| Risk | Probability | Impact |
|------|-------------|--------|
| Shell script breaks on path changes | 40% | LOW -- 30 min fix |
| Dict typos cause silent wrong data | 25% | HIGH -- wrong investment direction |
| No checkpoint/resume: 3.5hr re-runs | 50% | HIGH -- painful but not dangerous |
| No STEEPs on GlobalNews: incomplete analysis | 40% | MEDIUM -- weaker differentiation |
| Cannot evolve to Balanced without rewrite | 60% | HIGH -- migration requires new schema layer |

**Scenario 3.C assessment**: This is the "validate the habit before investing in code quality" approach. It produces a report 2 weeks faster than 3.B at the cost of significant technical debt. The critical weakness is the dict-based signal representation: without frozen dataclasses, there is no compile-time safety against typos that silently corrupt data. The lack of checkpoint/resume means every pipeline failure costs 3.5 hours. And the upgrade path to Balanced requires essentially rewriting the core (adding schema.py, normalizers.py, cli.py). The 17-week buffer is large but largely consumed by re-running failed pipelines.

---

### SCENARIO COMPARISON

| Dimension | 3.A Maximum | 3.B Balanced | 3.C Minimum |
|---|---|---|---|
| **Total LOC** | ~3,920 | ~2,710 | ~1,445 |
| **Dev Hours** | ~105 | ~64 | ~37.5 |
| **First Report** | Week 8 | **Week 6** | **Week 4** |
| **Tests** | 50 (7 files) | 25 (2 files) | 15 (2 files) |
| **Orchestration** | Click CLI from Day 1 | Shell W1-6, Click W7+ | Shell permanently |
| **Schema** | Frozen dataclass + slots | Frozen dataclass | Plain dicts |
| **STEEPs Classifier** | Dedicated module | Dedicated module | None (uses upstream) |
| **Signal Evolution** | YES (350 LOC) | NO (conditional M3+) | NO |
| **Decision Journal** | SQLite + CLI | JSONL + CLI | JSONL + CLI |
| **Checkpoint/Resume** | YES (from W2) | YES (from W8) | NO |
| **Schedule Buffer** | 0% (105/96 hrs = overbudget) | 30% (64/96 hrs) | 60% (37.5/96 hrs) |
| **Upgrade Path** | N/A (already maximum) | Clean (+evolution, +HTML) | Partial rewrite needed |
| **Financial Safety** | Comprehensive | Targeted (money paths) | Minimal |
| **Silent Data Corruption Risk** | Very Low | Low | Medium |
| **Sustainability (2+ years)** | High (but maintenance burden) | High | Medium (dict fragility) |

---

## PHASE 4: Final Implementation Guide

### 1. RECOMMENDED SCENARIO: 3.B (BALANCED IMPLEMENTATION)

**Justification, condensed:**

| Factor | Why 3.B Wins |
|--------|-------------|
| **Dev hours** | 64 hrs fits within 96 hr budget with 33% buffer |
| **First report** | Week 6 -- fast enough to validate before burnout |
| **Safety** | Frozen dataclasses prevent the silent data corruption that 3.C risks |
| **Sustainability** | StrEnum + typed parsers survive upstream schema drift |
| **Upgrade path** | Clean path to signal evolution + HTML if triggered |
| **Schedule realism** | 33% buffer absorbs pastoral duty weeks with zero coding |
| **Testing** | 25 tests on money paths -- enough to catch contract violations, not so many to become maintenance burden |

**3.A is rejected** because it exceeds the dev-hour budget (105 > 96) and delays the first report to Week 8. For a solo developer validating whether a tool is worth building, 8 weeks without output is too long.

**3.C is rejected** because plain dicts are the wrong choice for a financial intelligence tool. A dict typo (`"confience"` instead of `"confidence"`) silently produces zero-confidence scores that eliminate signals from the report. Frozen dataclasses catch this at construction time. The 2-week speed advantage of 3.C is not worth the silent corruption risk.

---

### 2. COMPLETE MODULE LIST WITH LOC PER FILE

```
investscan/                          # Python package
  __init__.py                    10  # Version, package metadata
  schema.py                     110  # UnifiedSignal frozen dataclass, StrEnums
  normalizers.py                350  # 6 format parsers + helpers
  dedup.py                       80  # Content-hash dedup + title-similarity dedup
  steeps_classifier.py          120  # Keyword-based STEEPs for GlobalNews signals
  sector_mapper.py              160  # Signal -> KOSPI/KOSDAQ sector mapping
  synthesize.py                 250  # Direction scoring + conviction computation
  generate_report.py            180  # Synthesis -> Jinja2 -> Markdown
  journal.py                    150  # JSONL append-only decision journal
  health_check.py               100  # Source freshness, schema, disk, writability
  orchestrator.py               280  # PipelineState + checkpoint/resume + step execution
  cli.py                        160  # Click CLI: run, status, report, journal, health
  config.py                      60  # YAML config loader with defaults
  utils.py                       80  # Shared I/O, date parsing, logging setup
  templates/
    weekly-report.md.j2         110  # Jinja2 Markdown report template

config/
  investscan.yaml                30  # Paths, thresholds, sector definitions

tests/
  conftest.py                    60  # Shared fixtures (sample signals, temp dirs)
  test_normalizers.py           160  # 10 contract tests on schema parsing
  test_sector_mapper.py         120  # 15 sector mapping tests

run.sh                          140  # Week 1-6 bootstrap (replaced by cli.py Week 7+)

TOTAL                         ~2,710 LOC
```

---

### 3. IMPLEMENTATION ORDER

The order is driven by one principle: **produce a working report as fast as possible, then harden.**

```
PHASE A: Foundation (Week 1-3, ~22 hrs)
  Step 1: schema.py + __init__.py           [3 hrs]   -- The data contract
  Step 2: run.sh                            [3 hrs]   -- Bootstrap orchestration
  Step 3: normalizers.py (WF4 db first)     [4 hrs]   -- Richest format first
  Step 4: normalizers.py (remaining 5)      [4 hrs]   -- All formats
  Step 5: dedup.py                          [2 hrs]   -- Remove duplicates
  Step 6: steeps_classifier.py              [3 hrs]   -- STEEPs for GlobalNews
  Step 7: sector_mapper.py                  [3 hrs]   -- Signal-to-sector

PHASE B: First Report (Week 4-6, ~13 hrs)
  Step 8: synthesize.py                     [6 hrs]   -- Direction + conviction
  Step 9: templates/weekly-report.md.j2     [3 hrs]   -- Report template
  Step 10: generate_report.py               [4 hrs]   -- Template rendering
  >>> FIRST USEFUL REPORT <<<

PHASE C: Production Grade (Week 7-10, ~18 hrs)
  Step 11: config.py + investscan.yaml      [1.5 hrs] -- Externalize config
  Step 12: cli.py                           [4 hrs]   -- Click CLI
  Step 13: orchestrator.py                  [6 hrs]   -- Checkpoint/resume
  Step 14: health_check.py                  [2 hrs]   -- System validation
  Step 15: journal.py                       [4 hrs]   -- Decision journal
  (run.sh retired, cli.py takes over)

PHASE D: Test & Harden (Week 9-12, ~8 hrs)
  Step 16: conftest.py                      [1 hrs]   -- Test fixtures
  Step 17: test_normalizers.py              [4 hrs]   -- 10 contract tests
  Step 18: test_sector_mapper.py            [3 hrs]   -- 15 mapping tests

PHASE E: Iterate (Week 13-24, ~8-15 hrs)
  Step 19: Weekly pipeline runs             [0.5 hr/week]
  Step 20: Report template refinement       [as needed]
  Step 21: Threshold calibration            [as needed]
  Step 22: Conditional feature evaluation   [Week 16+]
```

**Why this order:**

- `schema.py` first because every other module depends on `UnifiedSignal`.
- `run.sh` second because it provides immediate pipeline execution capability.
- Parsers before synthesis because you need real signals to test synthesis.
- `synthesize.py` before report because the report renders synthesis output.
- CLI after first report because the shell script works fine for the discovery phase.
- Tests after first report because testing code that might be rewritten is waste.
- Journal after CLI because the journal's CLI commands depend on Click.

---

### 4. MONTH-BY-MONTH CODING PLAN

#### Month 1 (Weeks 1-4): Foundation + First Signals
**Target: 16 hrs (4 hrs/week)**

| Week | Hours | What to Build | What to Validate |
|------|-------|---------------|------------------|
| W1 | 4 | `schema.py` + `run.sh` + project scaffolding | `run.sh` executes without errors. `UnifiedSignal` instantiates from sample data. |
| W2 | 4 | `normalizers.py` (WF4 db + WF1 db parsers) | Parse real EnvScan JSON files. Print signal count + sample fields. |
| W3 | 4 | `normalizers.py` (4 remaining parsers) + `dedup.py` | Parse all 6 formats. Dedup reduces signal count by 10-30%. |
| W4 | 4 | `steeps_classifier.py` + `sector_mapper.py` | All signals have STEEPs. 70%+ map to a Korean sector. |

**Month 1 output**: Unified signal file (`unified_signals.json`) with 200+ deduplicated, classified, sector-mapped signals from real data.

**Month 1 gate**: Open the unified signal file. Are the STEEPs distributions reasonable? Do the sector mappings make sense? If YES, proceed. If signal quality is garbage, stop and diagnose before investing in synthesis.

#### Month 2 (Weeks 5-8): First Report + CLI Migration
**Target: 16 hrs (4 hrs/week)**

| Week | Hours | What to Build | What to Validate |
|------|-------|---------------|------------------|
| W5 | 4 | `synthesize.py` (rule-based direction scoring) | Direction calls for 5+ sectors with conviction scores. |
| W6 | 4 | `generate_report.py` + `weekly-report.md.j2` | **FIRST WEEKLY REPORT**. Read it. Is there one insight you would not have found manually? |
| W7 | 4 | `config.py` + `cli.py` | `python -m investscan run --date 2026-05-01` works end-to-end. |
| W8 | 4 | `orchestrator.py` (checkpoint/resume) | Kill pipeline mid-run. `python -m investscan run --resume` picks up from the failed step. |

**Month 2 output**: Weekly Korean investment direction report generated by `investscan run`. Click CLI with checkpoint/resume.

**Month 2 gate**: Read the Week 6 and Week 8 reports. "Would I run this again next week?" If NO, stop building new features and diagnose. If YES, proceed.

#### Month 3 (Weeks 9-12): Journal + Tests + Hardening
**Target: 12 hrs (3 hrs/week)**

| Week | Hours | What to Build | What to Validate |
|------|-------|---------------|------------------|
| W9 | 3 | `journal.py` + `conftest.py` + 5 contract tests | `investscan journal add` creates JSONL entry. 5 tests pass. |
| W10 | 3 | `health_check.py` + 5 more contract tests + 8 sector tests | `investscan health` reports all green. 18 tests pass. |
| W11 | 3 | 7 remaining sector tests + report template refinement | 25 tests pass. Report has been iterated based on 4+ weeks of reading. |
| W12 | 3 | Buffer: fix bugs, calibrate thresholds, handle edge cases | Pipeline has run 6+ times on real data without manual intervention. |

**Month 3 output**: Decision journal with 4+ entries. 25 passing tests. Health check command. Battle-tested report template.

**Month 3 gate**: Review the 4-6 weekly reports. "Has any report changed how I think about my investment positions?" If YES, the tool has demonstrated value. If NO, the analytical approach may not work -- consider whether to continue.

#### Month 4-6 (Weeks 13-24): Maintenance + Conditional Features
**Target: 8-12 hrs total (1-2 hrs/week)**

| Activity | Hours | Trigger Condition |
|----------|-------|-------------------|
| Weekly pipeline runs | 6 (0.5/week) | Always |
| Report template iteration | 2-4 | Every time you read a report and want a different section |
| Sector mapping refinement | 2 | When a sector direction seems wrong due to mapping |
| Threshold calibration | 2 | When conviction scores seem too high or low |
| Signal evolution tracker | 10 | IF you manually track signals across 4+ weeks and find it painful |
| HTML report | 15 | IF you need to share reports externally |

**Month 4-6 output**: 12+ consecutive weekly reports. 12+ journal entries. Calibrated thresholds based on real data.

**Month 6 gate**: "Would I miss InvestScan if it stopped working?" This is the only question that matters.

---

### 5. CRITICAL CODE PATTERNS TO FOLLOW EVERYWHERE

#### Pattern 1: Frozen Dataclasses for All Data Objects

```python
@dataclass(frozen=True, slots=True)
class UnifiedSignal:
    signal_id: str
    source_system: SourceSystem
    confidence_score: float
    # ... all fields
```

**Why**: Immutability prevents accidental mutation during pipeline stages. `slots=True` reduces memory 30-40% for large signal collections. A signal created in the normalization stage must be identical when read by the report generator.

**Exception**: `PipelineState` is mutable (it tracks step completion).

#### Pattern 2: StrEnum for All Categorical Values

```python
class STEEPsCategory(StrEnum):
    S = "Social"
    T = "Technological"
    E_ECONOMIC = "Economic"
    E_ENVIRONMENTAL = "Environmental"
    P = "Political"
    SMALL_S = "sSecurity"
```

**Why**: Prevents typo-based bugs (`"Technoloigcal"` would fail at enum construction, not silently propagate). Serializes cleanly to JSON (because StrEnum IS a string).

#### Pattern 3: Explicit Scale Parameters, Never Auto-Detection

```python
# WRONG:
confidence = normalize_score(raw.get("psst_score"))  # What scale?

# RIGHT:
confidence = normalize_score(raw.get("psst_score"), scale="0-100")
```

**Why**: A pSST score of 10 is ambiguous (10/100 = 0.10 or 10/10 = 1.0). Each parser knows its source format and must declare the scale explicitly. Auto-detection exists only as a last-resort fallback with a logged warning.

#### Pattern 4: Defensive `.get()` with Documented Defaults

```python
confidence_score = _normalize_psst_score(
    raw.get("psst_score"),  # Missing in WF1 format
    scale="0-100",
) if "psst_score" in raw else 0.5  # 0.5 = "unknown confidence" (NOT 0.0)
```

**Why**: Default `0.0` eliminates a signal from synthesis (zero confidence = discard). Default `0.5` keeps it in play as "uncertain." Every default must be documented with its rationale.

#### Pattern 5: Crash Loud on Contract Violations, Graceful on Everything Else

```python
# Contract violation (upstream changed): CRASH
if "id" not in raw_signal:
    raise ValueError(f"Signal missing required 'id' field: {list(raw_signal.keys())[:5]}")

# Operational issue (network, disk): GRACEFUL
try:
    signals = parse_envscan_wf4_database(path)
except FileNotFoundError:
    logger.warning("WF4 database not found at %s, skipping", path)
    signals = []
```

**Why**: Contract violations mean upstream schemas changed -- the developer needs to know immediately. Operational issues are transient -- the pipeline should continue with reduced data.

#### Pattern 6: JSON Checkpoint for Pipeline State

```python
# After each step completes:
state.steps[step_name] = {"status": "completed", "elapsed_seconds": 42.3}
state.save(output_dir / "pipeline_state.json")
```

**Why**: If the pipeline crashes at step 4, `investscan run --resume` reads `pipeline_state.json` and skips steps 1-3. Without this, a report generation bug costs 3.5 hours of re-running upstream systems.

#### Pattern 7: Direction with Explicit Uncertainty

```python
@dataclass(frozen=True)
class SectorDirection:
    sector: str
    direction: str           # "bullish" | "bearish" | "neutral"
    conviction: float        # 0.0 - 1.0
    source_count: int        # How many independent sources
    uncertainty_reason: str  # "single source" | "conflicting signals" | ""
```

**Why**: A "bullish" direction with conviction 0.9 from 5 sources is fundamentally different from "bullish" with conviction 0.6 from 1 source. The report must present this distinction. The user's investment decision depends on it.

---

### 6. ANTI-PATTERNS TO AVOID EVERYWHERE

#### Anti-Pattern 1: Dict-Based Signal Passing

```python
# NEVER DO THIS:
signal = {"title": "AI Boom", "confience": 0.8}  # Typo: "confience"
# Downstream code reads signal["confidence"] -> KeyError (if lucky)
# or signal.get("confidence", 0.0) -> Silent zero (if unlucky)
```

**Why this is dangerous**: In a financial tool, a silent zero-confidence score eliminates a signal from the report. The user never sees it. A direction call that should have been "bullish with high conviction" becomes "neutral" because the strongest signal was silently dropped.

#### Anti-Pattern 2: Averaging Confidence Scores Without Weighting

```python
# NEVER DO THIS:
sector_conviction = sum(s.confidence for s in signals) / len(signals)
# 1 high-confidence signal + 19 low-confidence = mediocre average
```

**Why**: Naive averaging drowns strong signals in noise. Use weighted median or require minimum source diversity for high-conviction calls.

#### Anti-Pattern 3: ML Dependencies in the Core Pipeline

```python
# NEVER DO THIS for STEEPs classification:
from transformers import pipeline
classifier = pipeline("zero-shot-classification")
steeps = classifier(signal.title, candidate_labels=["Social", "Technological", ...])
```

**Why**: GPU/CPU inference adds 30+ seconds per run, requires model downloads, version pinning, and silent degradation when model weights drift. Keyword-based classification at 70-80% accuracy is dramatically more maintainable for a solo developer. Keep ML in the upstream systems where it is already maintained.

#### Anti-Pattern 4: Premature Optimization of Report Format

```python
# NEVER DO THIS in Month 1:
# - Interactive Plotly charts
# - CSS-styled HTML with inline JavaScript
# - PDF generation with WeasyPrint
# - Multiple report formats (MD + HTML + PDF)
```

**Why**: The report format will change significantly based on usage feedback. Building a complex rendering pipeline before knowing what sections the user actually reads is wasted effort. Start with Markdown. Add HTML if and when external sharing becomes a need.

#### Anti-Pattern 5: Building Signal Evolution Before Weekly Reports Work

```python
# NEVER DO THIS:
# Week 3: "Let me build the SQLite FTS5 evolution tracker..."
# Week 6: "...still haven't generated a single report."
```

**Why**: Signal evolution tracking is a compounding feature that provides value only after 4+ weeks of accumulated data. Building it before the basic pipeline produces useful reports is a classic premature investment. The evolution tracker cannot even be tested without 4 weeks of real signal data.

#### Anti-Pattern 6: Modifying Upstream Systems

```python
# NEVER DO THIS:
# "Let me add an InvestScan-compatible output format to GlobalNews-Crawling"
# "Let me modify EnvScan's database.json to include sector mappings"
```

**Why**: InvestScan reads upstream outputs; it does not modify upstream systems. Modifying EnvScan or GlobalNews creates coupling that makes both systems harder to maintain independently. The normalization layer exists precisely to absorb upstream format differences.

---

### 7. THE ONE THING TO GET RIGHT ABOVE ALL ELSE

**`normalizers.py` -- the 6-format parsing module.**

Everything else in InvestScan can be wrong and fixed quickly. A bad report template takes 30 minutes to fix. A wrong sector mapping takes 1 hour. A broken CLI takes 2 hours.

But if `normalizers.py` is wrong -- if it silently drops fields, miscategorizes STEEPs, misscales confidence scores, or fails to detect format changes -- then **every downstream module produces wrong results**. The synthesis scores wrong directions. The report shows wrong sectors. The journal records wrong rationale. And the user makes investment decisions based on corrupted data.

**What "getting it right" means concretely:**

1. **Every parser function must handle the exact field names found in real data** (not theoretical schemas). The six formats discovered in Branch 1's analysis are the ground truth:
   - WF1 `database.json`: nested `source/content`, `preliminary_category` (short codes: "T", "E")
   - WF1 output JSON: flat `source`, `preliminary_category` (long codes: "T_Technological")
   - WF4 `database.json`: flat, `steeps` (short), `psst_score` 0-100, `evolution_state`
   - WF4 `priority-ranked`: `psst_score` 0-10 scale (!), `impact_score`, `rank`
   - WF4 `evolution-map`: `thread_id`, `metrics.velocity`, `state`
   - GlobalNews Parquet: `signal_id`, `signal_layer` (L1-L5), `confidence` 0-1

2. **Every confidence score must use explicit scale parameters.** The three scales (0-100, 0-10, 0-1) in the source data are the most dangerous data quality issue in the entire system.

3. **Every parser must be covered by contract tests.** The 10 contract tests in `test_normalizers.py` are non-negotiable. They are the early warning system for upstream schema drift.

4. **Every parsing failure must crash loud** (not silently return defaults). A missing required field is not a "graceful degradation" opportunity -- it is a signal that upstream changed. The developer needs to know immediately.

If `normalizers.py` is correct and well-tested, everything downstream has a solid foundation. If it is wrong, nothing downstream can compensate.

**Build `normalizers.py` first. Test it against real data. Verify every field mapping manually. Only then build anything else.**

---

## Appendix A: Dependency List

```
# requirements.txt for Scenario 3.B
click>=8.0          # CLI framework
pyyaml>=6.0         # Config loading
jinja2>=3.0         # Report templating
pyarrow>=14.0       # GlobalNews Parquet reading

# Dev dependencies
pytest>=7.0         # Testing

# Already available (stdlib)
# json, dataclasses, enum, pathlib, hashlib, logging, datetime, subprocess
```

**Total external dependencies**: 4 runtime + 1 dev = 5 packages.

---

## Appendix B: Project Scaffold Command

```bash
# Run this once to create the project structure:
mkdir -p investscan/templates config tests
touch investscan/__init__.py
touch investscan/{schema,normalizers,dedup,steeps_classifier,sector_mapper}.py
touch investscan/{synthesize,generate_report,journal,health_check}.py
touch investscan/{orchestrator,cli,config,utils}.py
touch tests/__init__.py tests/{conftest,test_normalizers,test_sector_mapper}.py
touch config/investscan.yaml run.sh
chmod +x run.sh
```

---

## Appendix C: Conditional Feature Triggers (Month 4+)

| Feature | Trigger Condition | Evidence Required | LOC | Hours |
|---------|-------------------|-------------------|-----|-------|
| Signal Evolution Tracker | User manually notes "same signal appearing again" for 4+ consecutive weeks | 4+ journal entries referencing signal persistence | +350 | +10 |
| HTML Interactive Report | User needs to share report with someone who won't read Markdown | Specific sharing event occurred | +400 | +12 |
| KRX Market Data | 6+ months of decision journal entries ready for backtesting | 24+ journal entries with sector direction predictions | +300 | +8 |
| Scheduled Execution (launchd) | User runs pipeline manually 3+/week for 4 consecutive weeks | Usage log shows 12+ manual runs in 4 weeks | +100 | +3 |

**Rule**: No conditional feature is built until its trigger condition is met with evidence. The trigger evidence is a journal entry or usage log, not a feeling.

---

*The telescope is now designed. The lens grinding begins at Week 1, Step 1: `schema.py`. Sixteen lines of StrEnum that define the entire vocabulary of the system. Get those right, and the rest follows. Get those wrong, and nothing downstream can compensate.*
