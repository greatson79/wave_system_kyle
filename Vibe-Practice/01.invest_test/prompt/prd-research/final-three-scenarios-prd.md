# InvestScan: Final Three-Scenario PRD with Comparison and Recommendation

> **Author**: Final Scenario Architect
> **Date**: 2026-03-27
> **Status**: PHASE 3 Deliverable -- Converged from 8 research branches, 4-perspective discussion, and 3 independent scenario PRDs
> **Positioning**: Category Creator -- "What is happening in the world and what does it mean for my portfolio?"

---

## 0. Context Summary

**InvestScan** integrates two production-ready source systems:

| System | LOC | Capabilities |
|--------|-----|-------------|
| **EnvironmentScan** | ~25,500 | 4 workflows, STEEPs classification, 37 agents, LLM-driven analysis, 17+ sources, pSST scoring |
| **GlobalNews-Crawling** | ~25,400 | 116 sites, 8-stage NLP pipeline, 56 analysis techniques, 5-Layer signal hierarchy (L1-L5), BERTopic, Granger causality |
| **Combined** | **~50,900** | Production-ready, battle-tested, zero changes needed |

**Developer profile**: Solo, part-time (2-4 hrs/week = 48-96 dev hours over 6 months). Pastor with primary duties elsewhere. MacBook M5 Max 64GB.

**Strategic consensus** (from Phase 2 four-perspective discussion):
- InvestScan is a **category creator**, not an AlphaSquare competitor
- "Telescope vs. microscope" -- complementary, not rival
- The empty quadrant: macro scanning + local execution + evidence chains + signal evolution
- STEEPs classification applied to investment is the **sole defensible differentiator**
- Edge case personas (full-time investor, content creator, systematic investor) define Phase 1

**GREEN ZONE** (4/4 consensus): One-command execution, Weekly Korean synthesis report, Multi-source signal normalization, Decision Journal, STEEPs classification, Evidence chains in reports

**YELLOW ZONE** (3/4 consensus): Signal evolution tracking, HTML interactive report

---

## SCENARIO A: AGGRESSIVE

> **Philosophy**: "Seize the opportunity. Ship the differentiating features FIRST."
> **Risk Profile**: HIGH
> **Core Bet**: First-mover advantage in the "futures studies for investment" niche matters, and PRISM-INSIGHT (14 AI agents, 408.6% simulated returns, already on GeekNews) is an existential threat.

### A1. Feature List with LOC Estimates

| # | Feature | Zone | LOC | Dev Hours | Priority |
|---|---------|------|-----|-----------|----------|
| F1 | One-command execution (`investscan run`) with Rich progress bar, auto-detection, `investscan doctor`, `investscan schedule` (launchd) | GREEN | 300 | 12 | P0 |
| F2 | Weekly Korean synthesis report with sector heatmap (matplotlib), narrative briefing, STEEPs table, risk/opportunity matrix | GREEN | 500 | 16 | P0 |
| F3 | Multi-source integration: unified InvestSignal schema, cross-source dedup (TF-IDF cosine similarity 0.85), confidence fusion, temporal alignment | GREEN | 800 | 24 | P0 |
| F4 | STEEPs classification: 6-dimension scoring for all signals, STEEPs-to-GICS sector mapping, FSSF 8-type integration | YELLOW->P0 | 400 | 12 | P0 |
| F5 | Signal evolution tracking: SQLite FTS5, 7 evolution states (NEW/STRENGTHENING/STABLE/WEAKENING/FADING/TRANSFORMED/MERGED), persistence scoring | YELLOW->P1 | 500 | 16 | P1 |
| F6 | Decision journal with signal retrospective: SQLite, CLI add/review/export, weekly prompt integration | STRETCH | 400 | 12 | P1 |
| F7 | HTML interactive report: single self-contained HTML with inline Plotly.js, sector heatmap, STEEPs radar, signal timeline, KO/EN toggle | STRETCH | 600 | 20 | P1 |
| F8 | KRX market data snapshot: pykrx, KOSPI/KOSDAQ indices, sector ETFs, signal-vs-market auto-compare | STRETCH | 350 | 12 | P2 |
| -- | Infrastructure: config, utils, CLI (Click), tests, YAML configs | INFRA | 1,000 | 32 | P0 |
| | **TOTAL** | | **~4,850** | **~156** | |

**Effective LOC with AI assistance**: ~4,850 new LOC
**Dev hours required**: ~75-80 hours (with Claude Code ~40-50% boilerplate reduction)
**Hours per week needed**: **4+ hrs/week consistently** (upper bound of commitment range)

### A2. Six-Month Milestones

**M1: Working Pipeline (Months 1-2, ~30 hrs)**
- `investscan run` executes full pipeline: EnvScan -> GlobalNews -> Normalize -> Synthesize -> Report
- Signal normalization with cross-source deduplication (TF-IDF)
- STEEPs classification on all signals (ported from EnvScan + rule-based for GlobalNews)
- Basic Korean Markdown weekly report with sector-level direction + evidence chains
- `investscan doctor` health check
- Config via `~/.investscan/config.yaml`
- **LOC at M1**: ~2,000
- **Gate**: Produce a report. Is there at least ONE insight you would not have found manually?

**M2: Quality + Intelligence (Months 3-4, ~30 hrs)**
- Signal evolution tracking (7 states, weekly delta report)
- Cross-source convergence detection (signals in BOTH systems scored higher)
- Decision journal (`investscan journal add/review`)
- HTML interactive report (auto-opens in browser)
- Sector mapping refinement from 8+ weeks of real data
- **LOC at M2**: ~4,500
- **Gate**: 60%+ of STRENGTHENING signals still relevant next week. Decision journal has 5+ entries.

**M3: Production Hardening + Market Context (Months 5-6, ~25 hrs)**
- KRX market data snapshot integration
- Signal-vs-market validation in reports
- `investscan schedule` for automated runs
- Comprehensive test suite (60%+ coverage)
- User documentation sufficient for new user setup
- 24 weekly reports archived and browsable
- **LOC at M3**: ~4,850 (complete)
- **Gate**: 4 consecutive weeks without manual intervention. Signal-to-market correlation > 0.3.

### A3. Success Metrics

| Metric | M1 | M2 | M3 |
|--------|----|----|-----|
| Weekly reports generated | 4 | 12 cumulative | 24 cumulative |
| Signals per report | 20+ | 30+ | 40+ |
| STEEPs coverage | 4/6 dimensions | 6/6 | 6/6 + sector mapping validated |
| Pipeline reliability | 70% | 85% | 95% |
| Useful insight rate | 1+/report | 2+/report | 3+/report |
| Direction accuracy | Not measured | 55%+ | 60%+ |
| Decision journal entries | N/A | 5+ | 15+ |
| Open-source readiness | No | No | **Month 3** (README + setup guide) |

### A4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Timeline overrun** | HIGH (60-70%) | M3 delayed 2-4 weeks | Ordered cuts: KRX first, HTML second, evolution third. NEVER cut F1-F4. |
| **Signal quality = noise** | MEDIUM-HIGH (40-50%) | Existential | Month 2 reality check: if <3/4 reports have useful insight, STOP and recalibrate. |
| **Developer burnout** | MEDIUM (35%) | Project stalls at M2-M3 | If no working report by Week 8, switch to Conservative. |
| **Source schema drift** | MEDIUM (30%) | Pipeline breaks | Defensive parsing, schema validation, version pinning. |
| **PRISM-INSIGHT ships scanning** | LOW-MEDIUM (20-30%) | Differentiator eliminated | Ship STEEPs in M1 (not M3). Publish methodology for thought leadership. |

**Accepted technical debt**: Rule-based sector mapping (70-80% accuracy), simple confidence averaging, monolithic codebase, minimal test coverage until M3. Debt payoff: ~4-6 weeks in Months 7-9.

### A5. "월등히 뛰어난" Credibility Assessment

**Can Scenario A support the claim?** **YES, domain-qualified.**

"월등히 뛰어난" for macro-analytical investment direction is defensible because:
- Full STEEPs 6-dimension scanning (no competitor offers this)
- Signal evolution across weeks (point-in-time competitors cannot match)
- Evidence chain transparency (vs. AlphaSquare's black-box AI)
- Local execution with data sovereignty (structurally impossible for SaaS)
- Cross-source convergence from two independent analysis systems
- Decision journal creating irreproducible personal investment history
- KRX market data enables signal-vs-reality validation

**However**: Claims "월등" against AlphaSquare as a *product* (not analytical tool) remain indefensible. AlphaSquare wins on 11 of 17 product dimensions. The claim holds only within the "local macro intelligence for investment direction" category.

**Risk to credibility**: If signal quality is poor (40-50% probability), the "월등" claim collapses entirely. Analytical depth without accuracy is noise.

---

## SCENARIO B: BALANCED

> **Philosophy**: "Build for yourself first. Ship useful, iterate from real usage."
> **Risk Profile**: MEDIUM
> **Core Bet**: The developer-user's personal value comes first. If InvestScan is irreplaceable for one serious macro-thinker, it is a success. STEEPs is the differentiator, but everything else is conditional on demonstrated need.

### B1. Feature List with LOC Estimates

| # | Feature | Zone | LOC | Dev Hours | Priority |
|---|---------|------|-----|-----------|----------|
| F1 | One-command execution with checkpointing (`--resume`), state.yaml tracking, graceful degradation | GREEN | 400 | 12 | P0/M1 |
| F2 | Weekly Korean synthesis report: STEEPs table, cross-source convergence, risk radar, weak signal watch, evidence chains | GREEN | 500 | 14 | P0/M1 |
| F3 | Multi-source integration: UnifiedSignal dataclass, JSON+Parquet readers, content-hash dedup, cross-mapping enrichment | GREEN | 600 | 16 | P0/M1 |
| F4 | STEEPs classification for GlobalNews signals: keyword-based assignment, 70-80% accuracy acceptable for v1 | GREEN* | 300 | 8 | P0/M1 |
| F5 | Sector mapping: rule-based signal-to-KOSPI/KOSDAQ sector mapping, direction scoring, conviction computation | GREEN | 350 | 10 | P0/M1 |
| F6 | Investment synthesis: direction scoring by time horizon (short/mid/long), Korea relevance scoring, multi-source convergence boost | GREEN | 500 | 14 | P0/M1 |
| -- | Infrastructure: CLI, config, schema, utils, YAML configs | INFRA | 400 | 10 | P0/M1 |
| | **M1 Subtotal** | | **~3,050** | **~84** | |
| C1 | Signal evolution tracking (conditional -- include if user manually tracks for 4+ weeks) | YELLOW | +400 | 10 | P2/M3 |
| C2 | Decision journal (conditional -- include if 3+ investment decisions cite report signals in 2 months) | YELLOW | +150 | 5 | P2/M3 |
| C3 | Scheduled execution via launchd (conditional -- include if manual runs 3+/week for 4 weeks) | YELLOW | +200 | 5 | P2/M3 |
| -- | M2 quality: cross-source convergence refinement, health diagnostic, graceful degradation | POLISH | +550 | 15 | P1/M2 |
| -- | M3: tests, documentation, conditional features | HARDEN | +500 | 12 | P1/M3 |
| | **TOTAL (if all conditionals triggered)** | | **~4,850** | **~131** | |
| | **TOTAL (base without conditionals)** | | **~3,600** | **~99** | |

**Effective LOC**: ~3,050-3,600 (M1-M2), up to ~4,850 if all conditionals triggered
**Dev hours required**: ~60-80 hours
**Hours per week needed**: **~3 hrs/week** (sustainable mid-range)

### B2. Six-Month Milestones

**M1: Working Pipeline (Months 1-2, ~25-30 hrs)**

| Week | Task | Hours |
|------|------|-------|
| W1 | Project scaffolding: package structure, config.py, schema.py, CLI entry point | 4 |
| W2 | normalize_signals.py: Read EnvScan JSON, parse into UnifiedSignal | 5 |
| W3 | normalize_signals.py: Read GlobalNews Parquet, parse + basic dedup | 5 |
| W4 | orchestrator.py: Sequential phase execution with checkpointing | 4 |
| W5 | synthesize_investment.py: Rule-based sector mapping + direction scoring | 6 |
| W6 | generate_report.py: Korean markdown template + report generation | 4 |
| W7 | End-to-end test: Full pipeline on real data, fix issues, first real report | 4 |
| W8 | steeps_classifier.py: Assign STEEPs to GlobalNews signals (keyword-based) | 3 |

- **Gate**: User reads the M1 report. "Would I run this again next week?" If YES, proceed.

**M2: Quality + Polish (Months 3-4, ~20-25 hrs)**

| Week | Task | Hours |
|------|------|-------|
| W9 | Cross-source convergence detection (title similarity + STEEPs overlap) | 5 |
| W10 | Confidence scoring calibration (fuse pSST + GlobalNews confidence) | 4 |
| W11 | Sector mapper refinement (Korean market-specific rules, chaebol mapping) | 4 |
| W12 | Report enrichment: risk radar, weak signal watch | 4 |
| W13 | `investscan health` diagnostic command | 3 |
| W14 | Error handling: graceful degradation when one system fails | 3 |
| W15-16 | Buffer for bug fixes, threshold tuning, report iteration | 4 |

- **Gate**: "Has this report told me something that changed how I think about my investment positions?" If YES even once, proceed.

**M3: Hardening + Conditional Features (Months 5-6, ~15-20 hrs)**

| Week | Task | Hours |
|------|------|-------|
| W17 | Evaluate conditional features against actual usage data | 2 |
| W18-19 | Implement 1-2 conditional features that passed triggers | 6 |
| W20 | Scheduled execution (launchd) if triggered | 3 |
| W21 | Test suite: contract validation, sector mapping, synthesis correctness | 4 |
| W22 | Historical report archive: index of all past reports, searchable | 3 |
| W23 | User documentation: config guide, troubleshooting, report interpretation | 2 |
| W24 | Final polish, edge cases | 2 |

- **Gate**: "What did InvestScan tell me this quarter that I would not have known otherwise?" with specific examples.

### B3. Success Metrics

| Metric | Month 2 | Month 4 | Month 6 |
|--------|---------|---------|---------|
| Pipeline runs/month | >= 2 | >= 4 | >= 8 (weekly+) |
| Reports actually read | 100% | 100% | 100% |
| Pipeline success rate | > 60% | > 80% | > 90% |
| Signals per report | >= 20 | >= 30 | >= 40 |
| Cross-source convergent signals | N/A | >= 2/week | >= 3/week |
| Sector direction calls with rationale | >= 3 | >= 5 | >= 7 |
| "New insight" rate | >= 1/report | >= 2/report | >= 2/report |
| Direction accuracy | Not measured | Baseline | > 50% |
| Open-source readiness | No | **Month 4** (after personal validation) | Ready |

**The only metric that actually matters**: Does the developer-user run InvestScan voluntarily, without obligation, because the reports genuinely inform investment thinking?

### B4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Signal quality unvalidatable** | HIGH (50%) | HIGH but recoverable | Months 1-3: frame as "scanning synthesis" not "advice." Month 4+: manual retrospective. Month 6+: if correlation < 40%, rethink synthesis. |
| **EnvScan API reliability/cost** | MEDIUM (30%) | Pipeline half-broken | Graceful degradation: GlobalNews-only report. 1 day of engineering. |
| **Maintenance burden -> abandonment** | HIGH (40%) | FATAL | Graceful degradation everywhere. Minimal dependencies. `investscan health` self-diagnosis. |
| **Over-engineering** | MEDIUM (25%) | Medium | "Would I Actually Change This?" test. Kill switch at Month 2 if no useful report produced. |
| **Source schema drift** | MEDIUM (30%) | Pipeline breaks temporarily | Defensive parsing. Schema validation on every run. ~2-4 hours fix-up. |

**No accepted technical debt in M1**: The Balanced scenario ships clean code at each milestone. Conditionals are feature-gated, not quality-gated.

### B5. "월등히 뛰어난" Credibility Assessment

**Can Scenario B support the claim?** **YES, but only after Month 4.**

Month 1-3: The system is a well-organized multi-source report. It is *useful* but not yet "overwhelmingly superior" to manually reading both systems' outputs. The "월등" claim is premature.

Month 4+: With STEEPs-organized sector direction, cross-source convergence, evidence chains, and 12+ weeks of accumulated reports, the system demonstrates capabilities no free tool offers:
- Multi-dimensional macro force analysis (STEEPs)
- Two independent source systems cross-validating each other
- Evidence transparency (vs. AlphaSquare's black box)
- Local execution (vs. all SaaS competitors)

The conditional features, if triggered, add compounding advantages:
- Signal evolution (temporal narrative no competitor provides)
- Decision journal (irreproducible personal investment history)

**Credibility gap vs. Aggressive**: No HTML interactive report means the output looks less impressive to external observers. No KRX market data means no signal-vs-reality validation. The "월등" claim is defensible but harder to demonstrate visually.

---

## SCENARIO C: CONSERVATIVE

> **Philosophy**: "Build the habit, prove the value. The product will follow the habit."
> **Risk Profile**: LOW
> **Core Bet**: The actual bottleneck is not "I need better analysis" -- it is "I forget to run both systems, and outputs are scattered." Building the habit of weekly review is worth more than any analysis engine.

### C1. Feature List with LOC Estimates

| # | Feature | Zone | LOC | Dev Hours | Priority |
|---|---------|------|-----|-----------|----------|
| F1 | One-command execution: argparse CLI, sequential subprocess, output collection, basic retry | GREEN | 500 | 12 | P0/M1 |
| F2 | Weekly Korean synthesis report: template-based (Jinja2), organize by source+date, top 10 signals by score, STEEPs sections from EnvScan native output | GREEN | 450 | 14 | P0/M2 |
| F3 | Multi-source integration: health check, path configuration, output directory unification. **No schema harmonization.** Each system's native format read directly. | GREEN | 200 | 6 | P0/M1 |
| F4 | Decision journal: append-only Markdown, CLI add/review/list, timestamped entries linked to weekly reports, review-date reminders | GREEN | 250 | 8 | P0/M2 |
| -- | Infrastructure: config (YAML), main.py, health_check.py | INFRA | 100 | 3 | P0/M1 |
| | **TOTAL** | | **~1,500** | **~43** | |

**What is explicitly NOT built**:
- No unified signal schema (read both formats natively)
- No analysis layer (both systems already analyze; we organize, not re-analyze)
- No STEEPs re-classification (use EnvScan's native STEEPs)
- No cross-source deduplication
- No sector mapping
- No conviction scoring
- No signal evolution tracking
- No HTML report
- No scheduled execution (manual builds the habit better)

**Effective LOC**: ~1,500
**Dev hours required**: ~30-43 hours
**Hours per week needed**: **~2 hrs/week** (comfortable lower range)
**Dependencies**: 3 packages (pyyaml, jinja2, pyarrow)

### C2. Six-Month Milestones

**M1: Functioning Pipeline (Months 1-2, ~15 hrs)**
- `investscan run` executes both source systems, collects outputs in `output/{date}/`
- `investscan health` validates both systems are available
- Output directory structure: `output/{date}/envscan/` + `output/{date}/globalnews/`
- Basic error handling: timeout, retry, partial success reporting
- **Gate**: User runs `investscan run` at least 4 times in Month 2 (once per week).

**M2: Weekly Intelligence (Months 3-4, ~18 hrs)**
- `investscan report --week` generates Korean weekly synthesis
- `investscan journal --add` records decision entries
- `investscan journal --review` surfaces past decisions due for review
- Report template refined from 4-8 weeks of actual usage
- **Gate**: User reads the weekly report AND writes at least one journal entry per week for 4 consecutive weeks.

**M3: Habit Validation (Months 5-6, ~10 hrs)**
- Report template v2 (refined from 12+ weeks of feedback)
- Decision journal has 12+ entries with review cycles
- `investscan stats` usage summary
- Documentation: setup guide, weekly workflow guide
- Buffer for bug fixes and quality-of-life improvements
- **Gate**: "Would you miss InvestScan if it stopped working?"

### C3. Success Metrics

| Metric | M1-M2 Target | M3 Target | M3+ Target |
|--------|-------------|-----------|------------|
| Consecutive weeks of use | 4 weeks | 8 weeks | 12+ weeks |
| Weekly report read rate | 75% | 85% | 90%+ |
| Decision journal entries/month | 2+ | 4+ | 4+ |
| Decision review completion | N/A | 50%+ | 70%+ |
| Time saved/week | 30+ min vs. manual | 30+ min | 30+ min |
| Run reliability | 80%+ | 90%+ | 90%+ |

**Anti-metrics** (deliberately not measured): Signal accuracy (unvalidatable), number of signals processed (irrelevant), pipeline execution time (irrelevant for weekly batch), code coverage (1,500 LOC does not need enterprise testing).

**The only metric**: After 3 months, does the user run InvestScan every week without being reminded?

### C4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Developer abandons after Month 2** | MEDIUM (30%) | LOW -- each month's deliverable works independently | Conservative is designed so partial completion is still useful |
| **Report is not useful enough** | MEDIUM (35%) | LOW -- decision journal remains independently valuable | Template iteration. Change sections based on what user actually reads. |
| **User does not form weekly habit** | MEDIUM (40%) | HIGH -- this is the only scenario where Conservative fails | `investscan journal --review` prompts. Calendar reminders. |
| **Source format changes** | MEDIUM (30%) | LOW -- ~2-4 hrs fix-up | Defensive parsing with defaults. Health check validates output structure. |

**Risks NOT present** (that other scenarios have): Signal scoring misleading numbers, over-engineering consuming budget, schema harmonization bugs, analysis layer hallucinating signals, 6-month project failing to ship.

### C5. "월등히 뛰어난" Credibility Assessment

**Can Scenario C support the claim?** **NO. Not in Phase 1.**

Conservative deliberately does not build the features that constitute "overwhelming superiority":
- No STEEPs re-classification (uses EnvScan native, which is partial)
- No cross-source convergence analysis
- No sector-level direction calls
- No signal evolution
- No evidence chain construction beyond what source systems already provide

The Conservative scenario produces an **organized summary**, not an **analytical synthesis**. It is a useful personal tool. It is NOT a "category creator." It is a better way to read outputs from two existing systems.

**However**: Conservative is the **foundation** on which "월등" credibility is later built. If the habit forms (12+ weeks of consistent use), the developer has:
1. Proven the workflow is worth investing in
2. Accumulated data for signal evolution tracking
3. Built decision journal entries for backtesting
4. Understood which parts of the report are actually useful

The upgrade path to Balanced (adding STEEPs classification, sector mapping, synthesis) is straightforward. Nothing is thrown away.

**Honest framing**: Conservative answers "Is this workflow worth my time?" Balanced/Aggressive answer "Can I build something no one else offers?" Conservative must come first, logically, even if it is not built first chronologically.

---

## COMPARISON TABLE

| Dimension | A: AGGRESSIVE | B: BALANCED | C: CONSERVATIVE |
|-----------|--------------|-------------|-----------------|
| **Features** | 6 GREEN + 2 YELLOW + 3 STRETCH = 11 | 6 GREEN + 3 conditional YELLOW = 6-9 | 4 GREEN (subset) = 4 |
| **Total LOC** | ~4,850 | ~3,050-4,850 | ~1,500 |
| **Dev hours** | ~75-80 | ~60-80 | ~30-43 |
| **Hours/week needed** | 4+ consistently | ~3 sustainable | ~2 comfortable |
| **Time to first useful output** | Week 6 | Week 7-8 | Week 4 |
| **Analysis sophistication** | High (STEEPs + evolution + KRX + dedup) | Medium (STEEPs + sector mapping + convergence) | None (organize, not analyze) |
| **Risk level** | HIGH | MEDIUM | LOW |
| **Risk of not shipping** | MEDIUM-HIGH | LOW | VERY LOW |
| **Risk of over-engineering** | HIGH | MEDIUM | NONE |
| **Success probability (Month 6)** | 40-50% (ships complete) | 70-80% (ships core) | 90%+ (ships easily) |
| **Value if abandoned at Month 3** | Low (half-built pipeline) | Medium (working report) | High (habit + journal) |
| **"월등" credibility** | YES (domain-qualified, if quality holds) | YES (after Month 4, if quality holds) | NO (not in Phase 1) |
| **Open-source readiness** | Month 3 | Month 4 (after validation) | Month 6, maybe |
| **Phase 2 readiness** | Overlaps with Phase 2 already | Strong foundation, clear triggers | Clean foundation, needs significant addition |
| **Dependencies** | ~15+ packages + SQLite + Plotly.js | ~8 packages | 3 packages |
| **Signal quality validation** | KRX auto-compare (M3) | Manual retrospective (M4+) | Not addressed |
| **HTML report** | YES (Plotly.js, interactive) | NO | NO |
| **Signal evolution** | YES (SQLite FTS5, 7 states) | CONDITIONAL (trigger-gated) | NO |
| **Decision journal** | YES (SQLite, CLI, retrospective) | CONDITIONAL (trigger-gated) | YES (Markdown, simple) |
| **Market data integration** | YES (KRX, pykrx) | NO | NO |
| **Persona fit** | Content Creator + Systematic Investor | Developer-user (self-first) | Anyone unsure if they will use it |
| **Buffer for life** | NONE (fully loaded schedule) | ~20-30% | ~50-60% |

---

## RECOMMENDATION

### Choose Scenario B: BALANCED

**Justification, point by point:**

**1. The developer is a pastor with primary duties elsewhere.**

This single fact eliminates Scenario A. The Aggressive scenario requires 4+ hours/week consistently for 6 months with zero buffer. A pastor managing church responsibilities, thesis work, and multiple projects cannot guarantee this. The 60-70% probability of timeline overrun in Scenario A becomes near-certainty for a part-time developer with competing priorities.

Scenario C is safe but does not build the differentiator. If the goal is merely "organize outputs from two systems," a 50-line shell script would suffice. The user explicitly wants something "overwhelmingly superior" -- Conservative cannot deliver that claim.

Scenario B at ~3 hrs/week fits within the 2-4 hr/week budget with buffer for weeks when church duties take priority. The 20-30% schedule buffer is not luxury; it is realism for a part-time developer.

**2. "월등히 뛰어난" requires STEEPs, and STEEPs requires a normalization layer.**

The Phase 2 discussion established unanimous consensus: STEEPs classification applied to investment is the sole defensible differentiator. Without it, InvestScan is "a better way to read two systems' outputs" (useful but not exceptional). With it, InvestScan does something no free tool offers: multi-dimensional macro force analysis mapped to Korean market sectors.

Scenario C defers STEEPs re-classification entirely. Scenario B includes it in M1 (keyword-based, 70-80% accuracy). This is the minimum viable version of the differentiator.

Scenario A includes STEEPs plus ML-enhanced classification and FSSF integration. This is better but unnecessary for Phase 1. Keyword-based STEEPs at 70-80% accuracy is sufficient to validate whether the approach has value. Investing in ML classification before knowing if anyone reads the reports is premature optimization.

**3. Conditional features are the correct model for a solo developer.**

Balanced's "include if" triggers for signal evolution, decision journal depth, and scheduled execution respect a critical principle: **anticipated need is not demonstrated need**.

The Aggressive scenario builds signal evolution tracking (500 LOC, 16 hours) before anyone has used the system for a single week. If signal persistence in Korean markets is low (which is plausible in volatile 2025-2026 conditions), this is 16 wasted hours.

Balanced builds it only when the user manually tracks signals for 4+ weeks and finds it painful. This is proof of value before investment of effort.

**4. The upgrade path is preserved.**

Conservative -> Balanced is a clean upgrade (add normalization layer + STEEPs + synthesis). Balanced -> Aggressive is a clean upgrade (add evolution tracking + HTML + KRX). Nothing built in Balanced is thrown away if Aggressive becomes warranted later.

The reverse is not true: Aggressive technical debt (rule-based mappings, minimal tests, monolithic architecture) creates cleanup work that competes with feature development in Months 7-9.

**5. "Build for yourself, share as byproduct" is the correct strategy for a solo developer.**

Balanced explicitly builds for the developer-user first. Reports assume domain knowledge, use financial terminology without explanation, and optimize for information density over accessibility. This is correct for a personal tool.

Open-sourcing at Month 4 (after 8+ weeks of personal validation) ensures the public release demonstrates actual value, not theoretical capability. Aggressive's Month 3 open-source risks releasing an impressive-looking but unvalidated system.

**6. The kill switch.**

Balanced includes explicit kill conditions: if no useful report by Month 2, stop architecture work and write a simple concatenation script. This intellectual honesty -- "maybe this does not solve a real problem" -- is the most valuable feature of the Balanced scenario. It limits maximum downside to ~30 hours while preserving maximum upside.

### The Decisive Factor

The user wants "월등히 뛰어난." Conservative cannot deliver it. Aggressive can deliver it but probably will not ship. Balanced delivers the minimum credible version of "월등" (STEEPs + multi-source convergence + evidence chains + local execution) with the highest probability of actually being completed and used.

**The worst outcome is not building too little -- it is building something impressive that sits unused.** Balanced is optimized for the outcome where the developer actually runs InvestScan every week for 6 months, finds it valuable, and THEN decides whether Aggressive features are worth building.

### Summary Decision

> **Scenario B: BALANCED** -- Ship the differentiator (STEEPs), validate with real usage, gate everything else on demonstrated need. Build the habit AND the product simultaneously.

**Next step**: Generate `workflow.md` for Scenario B implementation, starting with M1 deliverables (Weeks 1-8).

---

## Appendix: Phase 2 Trigger Conditions (Post-Balanced M3)

If Balanced succeeds (12+ weeks of weekly use, reports informing investment thinking), these triggers determine what comes next:

| Trigger | Threshold | Unlocks |
|---------|-----------|---------|
| "I keep noticing the same signal across weeks" | User manually tracks 4+ weeks | Signal evolution tracking |
| "I want to see this in a browser, not terminal" | External sharing need or visual preference | HTML interactive report |
| "I want to know if my signals were right" | 6 months of accumulated decision journal | KRX market data + backtesting framework |
| "Installation is too hard for others" | Decision to open-source seriously | `investscan install` zero-touch setup |
| "I need this on my phone" | Never (for Phase 2) | Permanently deferred |
| 20+ hours/week become available | Life circumstances change | Aggressive scenario features |

**Critical rule**: No Phase 2 feature is built until its trigger condition is met with data. Anticipated need is not demonstrated need.
