# InvestScan: Aggressive Scenario PRD

> **Role**: Aggressive Scenario Decision-Maker
> **Philosophy**: "Seize the market opportunity now. Risk is manageable."
> **Date**: 2026-03-27

---

## Executive Summary

The Aggressive scenario builds ALL Green Zone + ALL Yellow Zone features into Phase 1, then pulls 2-3 Red Zone features forward as stretch goals. It accepts higher technical debt and tighter timelines in exchange for a faster, more feature-complete product that can establish InvestScan as the definitive "futures studies for investment" tool before competitors fill the gap.

**Core bet**: The 20,000-50,000 TAM of technically capable Korean investors is enough -- if we ship a compelling, differentiated product FAST. PRISM-INSIGHT (14 AI agents, 408.6% simulated returns, already on GeekNews) is the existential threat. Every month we delay, the window narrows.

---

## 1. Core Features (Green + Yellow = 5 Features)

### Feature 1: One-Command Execution (`investscan run`) -- GREEN ZONE

**Scope**: Single CLI command triggers the entire pipeline: EnvScan quad scan -> GlobalNews crawl+analyze -> Signal normalization -> Investment synthesis -> Report generation -> Korean translation.

**Aggressive interpretation**: Not just `investscan run`, but also `investscan install` with zero-touch setup. The installation experience IS the product's first impression.

| Component | Specification |
|-----------|---------------|
| Entry point | `investscan run --date YYYY-MM-DD` (default: today) |
| Installation | `pip install investscan` or `curl -fsSL install.sh \| bash` |
| Auto-detection | Finds EnvScan/GlobalNews directories automatically via `~/.investscan/config.yaml` |
| Health check | `investscan doctor` validates both source systems, Python version, disk space, dependencies |
| Progress display | Rich terminal progress bar (8 pipeline stages, ETA per stage) |
| Fail-safe | If one source system fails, generate partial report from the other |
| Scheduling | Built-in `investscan schedule` using launchd (macOS) -- runs at 05:00 KST daily |
| Total execution time | ~4 hours (sequential, network-bound) |

**New code**: ~300 LOC (CLI entry point + orchestrator wrapper)
**Dev time**: 1.5 weeks

---

### Feature 2: Weekly Synthesis Report (Korean Markdown) -- GREEN ZONE

**Scope**: The primary output artifact. A comprehensive Korean-language investment direction report that synthesizes signals from both source systems into actionable sector-level guidance.

**Aggressive interpretation**: Not just a data dump -- a structured, narrative investment briefing that a professional analyst would find useful. Include visualizations.

**Report structure**:

```markdown
# 주간 투자 방향 스캐닝 리포트 (2026-03-24 ~ 2026-03-28)

## 요약 (Executive Summary)
- 핵심 투자 방향 3가지 (bullet points)
- 주간 컨빅션 변화 (상승/하락/유지)

## 섹터별 분석
### IT/테크
- 방향: 강세 (conviction: 0.78)
- 핵심 신호: [3-5개 신호 요약 + 출처]
- KOSPI 관련: 삼성전자, SK하이닉스, 네이버, 카카오
- STEEPs 분류: T_Technological (3), E_Economic (2)

### 에너지/소재
...

## 신호 진화 추적 (Signal Evolution)
- 강화되는 신호 (Strengthening): [목록]
- 약화되는 신호 (Fading): [목록]
- 새로 출현한 신호 (Emerging): [목록]

## 리스크/기회 매트릭스
[Text-based matrix in Phase 1, matplotlib heatmap by M2]

## 데이터 품질 메타데이터
- EnvScan: 4 workflows, N signals processed
- GlobalNews: M sites crawled, P articles analyzed
- Cross-source overlap: X%
- Signal confidence distribution: [histogram]
```

**New code**: ~500 LOC (report generator + Korean template)
**Dev time**: 2 weeks (including matplotlib sector heatmap)

---

### Feature 3: Multi-Source Integration (EnvScan + GlobalNews Pipeline) -- GREEN ZONE

**Scope**: The Signal Normalization Layer -- the technical heart of InvestScan. Harmonizes two fundamentally different data models into a unified investment signal format.

**Aggressive interpretation**: Build the normalization layer AND the cross-source deduplication from day 1. Don't defer dedup to Month 4 -- noisy duplicate signals in early reports will destroy credibility.

| Component | From | To | Logic |
|-----------|------|----|-------|
| Schema mapping | EnvScan JSON + GNC Parquet | Unified `InvestSignal` JSON | Field-by-field mapping with defensive parsing |
| Category harmonization | STEEPs (6 types) + L1-L5 (5 layers) | Combined `steeps_category` + `temporal_class` | Cross-mapping table (30 combinations) |
| Confidence fusion | pSST (0-100) + GNC confidence (0-1) | Unified confidence (0-1) | Weighted average: `(pSST/100 * 0.5) + (gnc_conf * 0.5)` |
| Deduplication | Title + content from both systems | Deduplicated signal set | Cosine similarity on TF-IDF vectors, threshold 0.85 |
| Temporal alignment | EnvScan dates + GNC timestamps | Same date window (weekly) | UTC normalization + weekly windowing |
| Sector mapping | Raw signals | GICS-aligned Korean market sectors | Rule-based keyword mapping (v1) -> SetFit ML (v2) |

**Unified signal schema** (from Tech Architect analysis):

```python
@dataclass
class InvestSignal:
    signal_id: str              # "IS-20260327-001"
    source_system: str          # "envscan" | "gnews"
    source_signal_id: str       # Original ID
    title: str
    summary: str
    detected_at: datetime
    steeps_category: str        # "T_Technological" etc.
    signal_layer: str           # "L1_fad" to "L5_singularity"
    confidence: float           # 0-1 unified
    psst_score: float           # 0-100 (EnvScan native)
    investment: InvestmentMeta  # sectors, direction, conviction, korea_relevance
    evidence: EvidenceMeta      # source_count, sources, burst/novelty scores
    schema_version: str         # "1.0.0"
```

**New code**: ~800 LOC (normalize_signals.py + schema.py + dedup logic)
**Dev time**: 3 weeks

---

### Feature 4: STEEPs Classification -- YELLOW ZONE (pulled into Phase 1)

**Scope**: Full futures studies methodology applied to investment signals. This is the ONLY genuine differentiator vs. PRISM-INSIGHT, OpenBB, and every other competitor.

**Why Aggressive pulls this in**: Without STEEPs, InvestScan is "just another news aggregator with a CLI." The cautious market analysis is clear -- environmental scanning methodology is the sole defensible moat. Deferring it is unacceptable.

**Implementation**:

| Component | Specification |
|-----------|---------------|
| STEEPs dimensions | S (Social), T (Technological), E (Economic), E (Environmental), P (Political), s (security) |
| Classification source | EnvScan already does this. For GlobalNews signals, add rule-based + keyword STEEPs assignment |
| Cross-dimensional scoring | Each signal gets a 6-dimension STEEPs vector (0-1 per dimension) |
| Investment mapping | STEEPs dimension -> Korean market sector mapping table |
| Report integration | Sector analysis organized BY STEEPs dimension in addition to by sector |
| FSSF 8-type integration | Merge EnvironmentScan's FSSF types (Weak Signal, Wild Card, Megatrend, etc.) with investment horizon |

**STEEPs -> Sector mapping example**:

| STEEPs | Primary Korean Sectors | Example Signal |
|--------|----------------------|----------------|
| T_Technological | IT, Bio/Healthcare | "AI chip export controls tightening" -> SK Hynix, Samsung |
| E_Economic | Financials, Real Estate | "BOK rate decision" -> KB Financial, Shinhan |
| P_Political | Defense, Construction | "Korean peninsula diplomatic shift" -> Hanwha Aerospace, Korea Aerospace |
| E_Environmental | Energy, Chemicals | "EU carbon border tax expansion" -> POSCO, LG Chem |
| S_Social | Consumer, Healthcare | "Aging population acceleration" -> Samsung Biologics, Celltrion |
| s_security | Defense, Cyber | "Cyber warfare escalation" -> Hancom, AhnLab |

**New code**: ~400 LOC (steeps_classifier.py + steeps_sector_mapper.py)
**Dev time**: 1.5 weeks (leveraging EnvScan's existing classification logic)

---

### Feature 5: Signal Evolution Tracking -- YELLOW ZONE (pulled into Phase 1)

**Scope**: Track how signals change over time across weekly runs. A signal detected 3 weeks ago may strengthen, fade, or transform. This temporal dimension is what separates InvestScan from point-in-time news analysis tools.

**Why Aggressive pulls this in**: The Cautious Market Analysis identified that the only users who will actually USE a local CLI investment tool are sophisticated, detail-oriented investors. These users will DEMAND temporal persistence. "What changed since last week?" is the first question any serious analyst asks. Without evolution tracking, the weekly report is just a snapshot -- not a trend monitor.

**Implementation**:

| Component | Specification |
|-----------|---------------|
| Signal matching | Cross-week signal matching via title similarity + entity overlap |
| Evolution states | NEW, STRENGTHENING, STABLE, WEAKENING, FADING, TRANSFORMED, MERGED |
| Persistence score | How many consecutive weeks a signal has appeared (1-52) |
| Direction change detection | If a signal's sector impact direction flips (bullish -> bearish), flag prominently |
| Evolution index | SQLite database (`evolution_index.sqlite`) with FTS5 for search |
| Weekly delta report | "3 new signals, 2 strengthened, 1 faded, 1 transformed" summary |

**EnvironmentScan already has signal evolution tracking** (`signal_evolution_tracker.py`). The aggressive approach ports this directly, adapting it for the unified InvestSignal schema rather than rebuilding from scratch.

**New code**: ~500 LOC (evolution_tracker.py + sqlite schema + weekly_delta.py)
**Dev time**: 2 weeks

---

## 2. Stretch Features (Pulled from Red Zone into Phase 1)

### Stretch A: Interactive HTML Dashboard Report

**Red Zone -> Phase 1 justification**: The Cautious Market Analysis hammered the point that the target audience is 20K-50K users. To reach even the upper end of that range, we need an output format that isn't exclusively terminal-native. An HTML report that auto-opens in the browser after `investscan run` dramatically lowers the consumption barrier. The user doesn't need to install anything -- they already have a browser.

**Scope**: NOT a web app. NOT a server. A single self-contained HTML file (inline CSS/JS) generated at the end of each pipeline run. Opens in Safari/Chrome.

| Component | Specification |
|-----------|---------------|
| Format | Single HTML file with inline Plotly.js charts |
| Size | <5MB per report (all assets embedded) |
| Charts | Sector heatmap, signal evolution timeline, confidence distribution, STEEPs radar chart |
| Interactivity | Click on sector -> drill down to individual signals. Hover for details. Filter by STEEPs dimension. |
| Korean | Full Korean UI with bilingual toggle (KO/EN) |
| Auto-open | `investscan run` auto-opens the HTML report after completion |
| Archive | Previous reports browsable via `investscan reports` (lists dates, opens selected) |

**New code**: ~600 LOC (html_report_generator.py + Jinja2 template + Plotly chart configs)
**Dev time**: 2.5 weeks

**Risk**: Adds 2.5 weeks to timeline. Contingency: if behind schedule by M4, ship Markdown-only and add HTML in M5.

---

### Stretch B: Decision Journal with Signal Retrospective

**Red Zone -> Phase 1 justification**: The Business Strategist was emphatic -- "build the habit, not the product." The decision journal is what transforms InvestScan from "a report I read" into "a system that improves my investment thinking." It also generates the data needed for future backtesting (Red Zone) without building the backtesting engine itself.

**Scope**: A structured log where the user records their investment decisions alongside the signals that informed them. After the market moves, they can review whether signals were accurate.

| Component | Specification |
|-----------|---------------|
| Entry format | `investscan journal add --signal IS-20260327-001 --action "Overweight IT sector" --confidence high` |
| Weekly prompt | After `investscan run`, prompt: "Record any investment decisions based on this week's signals?" |
| Retrospective | `investscan journal review --period 4w` shows past decisions with actual market outcomes |
| Storage | SQLite (`decision_journal.sqlite`) with FTS5 |
| Report integration | Weekly report includes "Your Decisions This Week" section if journal entries exist |
| Export | `investscan journal export --format csv` for external analysis |

**New code**: ~400 LOC (journal.py + cli_commands.py + sqlite schema)
**Dev time**: 1.5 weeks

**Risk**: Low technical risk. Mainly a UX challenge -- making journal entry frictionless enough that the user actually does it. Contingency: if user doesn't use it after M3, deprioritize further development.

---

### Stretch C: KRX Market Data Snapshot Integration

**Red Zone -> Phase 1 justification (AGGRESSIVE PUSH)**: Currently InvestScan generates investment "direction" signals but has no connection to actual market data. Adding a lightweight Korean market data snapshot (KOSPI/KOSDAQ index levels, sector ETF performance, top movers) makes the report dramatically more actionable. The user can see "Signal says IT sector bullish" alongside "KODEX IT ETF: +3.2% this week."

**Scope**: Read-only market data snapshot. NOT a trading system. NOT real-time. Weekly snapshot of major Korean market indices and sector performance.

| Component | Specification |
|-----------|---------------|
| Data source | KRX Open API (free, registration required) + pykrx library |
| Indices | KOSPI, KOSDAQ, KOSPI 200, sector sub-indices (IT, Healthcare, Finance, etc.) |
| Sector ETFs | Top 10 sector ETFs (KODEX series) -- weekly performance |
| Frequency | Weekly snapshot (Friday close) |
| Storage | Parquet file per week in `data/market/` |
| Report integration | "Market Context" section in weekly report showing actual performance alongside signals |
| Signal validation | Auto-compare: "Signal predicted IT bullish -> KODEX IT ETF actual: +3.2%" |

**New code**: ~350 LOC (krx_adapter.py + market_snapshot.py)
**Dev time**: 1.5 weeks

**Risk**: MEDIUM. KRX API availability and rate limits. pykrx library stability. Contingency: if KRX API proves unreliable, use Yahoo Finance Korea as fallback (less data but more stable).

---

## 3. Technical Debt Accepted

The Aggressive scenario explicitly accepts the following shortcuts in exchange for speed:

| Shortcut | What It Means | Debt Level | When It Hurts | Payoff Deadline |
|----------|--------------|------------|---------------|-----------------|
| **Rule-based sector mapping (no ML)** | Hardcoded keyword -> sector rules instead of trained classifier | MEDIUM | When novel signals don't match any keyword rules (~70-80% accuracy) | Month 7: evaluate SetFit few-shot if accuracy <70% |
| **Simple confidence averaging** | `(pSST/100 * 0.5) + (gnc_conf * 0.5)` instead of Bayesian fusion | LOW | Rarely -- simple averaging is surprisingly robust for this use case | Month 9: add Bayesian fusion only if signal quality reviews demand it |
| **Monolithic codebase (no plugins)** | Direct function calls, not BaseAnalyzer/BaseAdapter abstractions | MEDIUM | When adding 3rd data source or 3rd analysis method | Month 8: refactor to plugin architecture IF extensibility is actually needed |
| **Minimal test coverage (M1-M3)** | Integration tests only, no unit tests for individual modules | HIGH | When a subtle bug in normalization corrupts signal scores silently | Month 4: add comprehensive unit tests during quality hardening |
| **No schema versioning** | Data contracts exist but without migration framework | MEDIUM | When schema changes require reprocessing historical data | Month 6: add schema_version field to all data contracts |
| **HTML report without accessibility** | Interactive charts, no screen reader support, no keyboard navigation | LOW | If the tool gains users with accessibility needs | Month 9+: only if user feedback demands it |
| **No graceful degradation for KRX** | If KRX API fails, market data section is simply empty | LOW | Every time KRX API is down (infrequent) | Month 5: add Yahoo Finance fallback |

**Total estimated debt payoff**: ~4-6 weeks of refactoring work in Months 7-9, which fits naturally into a "maintenance phase" after the initial 6-month push.

**Debt that is NOT acceptable** (even in Aggressive):
- Skipping deduplication -- duplicate signals make the system look broken
- Skipping Korean translation -- primary user reads Korean
- Skipping error handling for source system failures -- both systems WILL fail occasionally
- Hardcoding file paths -- must be configurable via YAML

---

## 4. Risk Profile

### Risk 1: Timeline Overrun (Probability: HIGH, 60-70%)

**What goes wrong**: The Aggressive scope is ~5,850 LOC of new code across 8 features + 3 stretch features. At 2-4 hours/week, this requires ~65-80 dev hours. Even with AI assistance (Claude Code), complex integration work (cross-source dedup, evolution tracking, KRX API) will encounter unexpected issues.

**Impact**: M3 milestone delayed by 2-4 weeks. Stretch features don't ship. User loses momentum.

**Contingency (ordered cuts)**:
1. Cut Stretch C (KRX Market Data) first -- saves 1.5 weeks, least critical
2. Cut Stretch A (HTML Dashboard) -- saves 2.5 weeks, Markdown reports still work
3. Defer Feature 5 (Signal Evolution) to M4 -- saves 2 weeks, weekly reports still function
4. NEVER cut: Features 1-3 (core pipeline) or Feature 4 (STEEPs -- the differentiator)

### Risk 2: Signal Quality Produces Noise, Not Insight (Probability: MEDIUM-HIGH, 40-50%)

**What goes wrong**: The rule-based sector mapping + simple confidence averaging produces investment directions that don't correlate with actual Korean market movements. The user reads the first few reports, finds them generic or inaccurate, and stops using InvestScan.

**Impact**: Existential -- if the output isn't useful, the product has no reason to exist.

**Contingency**:
1. Month 2 reality check: generate 4 weekly reports, manually evaluate quality. If <3/4 reports contain at least one genuinely useful insight, STOP and recalibrate.
2. Stretch B (Decision Journal) provides the feedback loop: user marks which signals were useful, which weren't. Use this to tune scoring.
3. Add explicit uncertainty bands: never claim "strong conviction" for single-source signals.
4. Include raw evidence trails in every report so the user can verify signal quality.

### Risk 3: PRISM-INSIGHT Ships Environmental Scanning (Probability: LOW-MEDIUM, 20-30%)

**What goes wrong**: PRISM-INSIGHT (already on GeekNews, 14 AI agents, open-source) adds STEEPs-like environmental scanning to its feature set, eliminating InvestScan's sole differentiator.

**Impact**: HIGH. If PRISM-INSIGHT has environmental scanning + stock-level analysis + community traction, InvestScan becomes redundant for most users.

**Contingency**:
1. Ship STEEPs classification in M1-M2, not M3-M4. First-mover advantage in this niche.
2. Publish methodology (futures studies for investment) as a blog post/article. Establish thought leadership.
3. If PRISM-INSIGHT adds this, pivot InvestScan to be a "PRISM-INSIGHT enhancer" that adds environmental scanning as an upstream data source.

### Risk 4: Source System Schema Drift (Probability: MEDIUM, 30%)

**What goes wrong**: EnvironmentScan or GlobalNews updates their output format, breaking the normalization layer.

**Impact**: Pipeline failure until adapter is updated. If both break simultaneously, total downtime.

**Contingency**:
1. Defensive parsing (`.get()` with defaults) in all adapters -- handles missing fields gracefully
2. Schema validation on every run -- fail-fast with clear error message identifying which field changed
3. Pin source system versions in config: `envscan_version: "2.5.0"`, `globalnews_version: "1.0.0"`
4. Monthly compatibility check: `investscan doctor` verifies source system output formats

### Risk 5: Solo Developer Burnout (Probability: MEDIUM, 35%)

**What goes wrong**: Part-time development (2-4 hrs/week) on an aggressive feature set across 6 months leads to motivation fatigue, especially if early reports don't demonstrate clear value.

**Impact**: Project stalls at M2-M3 with a half-built system.

**Contingency**:
1. M1 delivers a WORKING (if basic) report within 4-6 weeks. Seeing output sustains motivation.
2. AI-assisted development (Claude Code) reduces boilerplate writing by ~40-50%.
3. Hard rule: if no working report by Week 8, switch to Conservative scenario (bare minimum integration).

---

## 5. 6-Month Milestones

### M1: Working Pipeline (Weeks 1-8, Target: Month 2 End)

**Deliverables**:
- `investscan run` executes full pipeline (EnvScan -> GlobalNews -> Normalize -> Synthesize -> Report)
- Signal normalization with cross-source deduplication
- STEEPs classification on all signals (ported from EnvScan + rule-based for GlobalNews)
- Basic Korean Markdown weekly report with sector-level direction
- `investscan doctor` health check
- Config via `~/.investscan/config.yaml`

**Success gate**: Run the pipeline on real data. Produce a report. Read it. Is there at least ONE insight you wouldn't have found manually? If yes, proceed. If no, recalibrate scoring.

**LOC milestone**: ~2,000 of ~5,850 total
**Dev hours**: ~25-30 hours

### M2: Quality + Intelligence (Weeks 9-16, Target: Month 4 End)

**Deliverables**:
- Signal evolution tracking (NEW/STRENGTHENING/FADING/etc.)
- Weekly delta report ("What changed since last week?")
- Sector heatmap visualization (matplotlib in Markdown or HTML)
- Cross-source convergence detection (signals appearing in BOTH EnvScan and GlobalNews scored higher)
- Korean market sector mapping refined based on 8+ weeks of actual data
- Decision journal (Stretch B) -- `investscan journal add/review`
- HTML interactive report (Stretch A) -- auto-opens in browser

**Success gate**: Run 8 consecutive weekly reports. Review signal evolution accuracy. At least 60% of "STRENGTHENING" signals should still be relevant the following week. Decision journal has >5 entries.

**LOC milestone**: ~4,500 of ~5,850 total
**Dev hours**: ~25-30 hours

### M3: Production Hardening + Market Context (Weeks 17-24, Target: Month 6 End)

**Deliverables**:
- KRX market data snapshot integration (Stretch C)
- Signal-vs-market validation in reports ("Signal said bullish IT -> KODEX IT actual: +X%")
- `investscan schedule` for automated daily/weekly runs (launchd)
- Error handling hardening (retry logic, graceful degradation, source system failure tolerance)
- Comprehensive unit + integration test suite
- User documentation (README + config guide)
- 24 weekly reports in archive, browsable via `investscan reports`

**Success gate**: System runs for 4 consecutive weeks without manual intervention. Signal-to-market correlation is >0.3 (weak but positive correlation). User documentation is sufficient for a new user to set up from scratch.

**LOC milestone**: ~5,850 total (complete)
**Dev hours**: ~20-25 hours

### Milestone Timeline Visualization

```
Month 1    Month 2    Month 3    Month 4    Month 5    Month 6
|----------|----------|----------|----------|----------|----------|
  M1: Working Pipeline  M2: Quality + Intelligence   M3: Hardening
  [F1][F3][F4]          [F5][StrA][StrB]              [StrC][Tests]
  [normalize][steeps]   [evolution][HTML]              [KRX][cron]
  [report v1]           [journal][convergence]         [docs][polish]

  *** First report ***  *** Signal evolution ***       *** Fully automated ***
  (Week 6)              (Week 12)                      (Week 22)
```

---

## 6. Success Metrics (Aggressive Targets)

### Product Metrics

| Metric | M1 Target | M2 Target | M3 Target | Measurement |
|--------|-----------|-----------|-----------|-------------|
| **Weekly reports generated** | 4 (manual trigger) | 12 cumulative (auto) | 24 cumulative | Count of reports in `output/` |
| **Signals per report** | >20 normalized | >30 with evolution | >40 with market context | Count in unified_signals.json |
| **STEEPs coverage** | 4/6 dimensions per report | 6/6 dimensions | 6/6 + sector mapping | Check report sections |
| **Cross-source overlap** | Any overlap detected | >15% signal overlap | >20% with convergence scoring | Dedup statistics |
| **Report read time** | <10 min | <15 min (more content) | <20 min (full report) | Estimated from word count |
| **Pipeline reliability** | 70% success rate | 85% success rate | 95% success rate | Success/total runs |
| **Pipeline runtime** | <5 hours | <4.5 hours | <4 hours | Wall clock time |

### Signal Quality Metrics (the metrics that actually matter)

| Metric | M1 Target | M2 Target | M3 Target | How Measured |
|--------|-----------|-----------|-----------|-------------|
| **Useful insight rate** | 1+ per report | 2+ per report | 3+ per report | User self-assessment |
| **Direction accuracy** | Not measurable yet | 55%+ (better than coin flip) | 60%+ | Signal direction vs actual market move |
| **Signal persistence** | N/A | 60%+ STRENGTHENING signals still relevant next week | 65%+ | Evolution tracking accuracy |
| **Sector mapping accuracy** | 70%+ (rule-based) | 75%+ (refined rules) | 80%+ (human-validated) | Manual review of 20 signals/month |
| **Decision journal entries** | N/A | 5+ entries | 15+ entries | Journal database count |

### Developer Productivity Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Dev hours to M1** | <35 hours | If M1 takes >35 hours, scope is too ambitious |
| **LOC per dev hour** | 15-25 LOC/hr (with AI assist) | Below 10 LOC/hr = over-engineering. Above 30 = under-testing |
| **Test coverage by M3** | >60% line coverage | Below 50% = fragile system. Above 80% = over-testing for solo dev |
| **Bugs per weekly run by M3** | <1 blocking bug/month | More = insufficient error handling |

---

## 7. When to Choose This Scenario

The Aggressive scenario is the RIGHT choice when ALL of the following conditions are true:

### Condition 1: Developer Commitment is Firm
The developer can reliably commit 3-4 hours/week for 6 months (total ~75-80 hours). If available time is <2 hours/week, choose Conservative. The Aggressive scope WILL fail at <2 hrs/week.

### Condition 2: Both Source Systems Are Stable
EnvironmentScan v2.5.0 and GlobalNews v1.0 are feature-frozen (no major schema changes planned). If either system is undergoing active restructuring, the normalization layer will be constantly breaking. Choose Balanced instead.

### Condition 3: The Developer Values Differentiation Over Simplicity
If the goal is "I just want a combined report from both systems," the Conservative scenario (bare pipeline, no STEEPs, no evolution tracking) delivers that in 3 months. If the goal is "I want a tool that NO ONE ELSE offers -- futures studies methodology applied to Korean market investment direction," then Aggressive is the only path that builds that differentiation into Phase 1.

### Condition 4: First-Mover Urgency Is Real
If PRISM-INSIGHT or similar projects are likely to add environmental scanning capabilities within 6 months, delaying STEEPs and signal evolution tracking to Phase 2 means shipping a commodity product. The Aggressive scenario ensures the differentiating features ship FIRST.

### Condition 5: Tolerance for Technical Debt
The developer accepts that the Aggressive codebase will need ~4-6 weeks of refactoring in Months 7-9 (rule-based -> ML sector mapping, adding schema versioning, expanding test coverage). If "clean architecture from day 1" is a hard requirement, choose Balanced.

### When NOT to Choose Aggressive

- Available dev time is <2 hours/week
- Either source system is undergoing major refactoring
- The developer wants a "quiet, reliable tool" rather than a "feature-rich, fast-moving project"
- There is no perceived competitive threat (no urgency to ship differentiating features first)
- The developer is burned out from building EnvScan and GlobalNews and needs a lighter project

---

## 8. Total Scope Summary

### Feature Budget

| Category | Feature | New LOC | Dev Weeks | Priority |
|----------|---------|---------|-----------|----------|
| **GREEN** | F1: One-command execution | 300 | 1.5 | P0 |
| **GREEN** | F2: Weekly synthesis report (KO) | 500 | 2.0 | P0 |
| **GREEN** | F3: Multi-source integration + dedup | 800 | 3.0 | P0 |
| **YELLOW** | F4: STEEPs classification | 400 | 1.5 | P0 |
| **YELLOW** | F5: Signal evolution tracking | 500 | 2.0 | P1 |
| **STRETCH** | SA: HTML interactive report | 600 | 2.5 | P1 |
| **STRETCH** | SB: Decision journal | 400 | 1.5 | P1 |
| **STRETCH** | SC: KRX market data snapshot | 350 | 1.5 | P2 |
| **INFRA** | Config, utils, CLI, tests | 1,000 | 4.0 | P0 |
| | **TOTAL** | **~4,850** | **~20 weeks** | |

At 2-4 hours/week over 24 weeks = 48-96 dev hours available.
Estimated total effort with AI assistance: ~75-80 dev hours.

**This is tight but feasible at the upper end of the commitment range (4 hrs/week).** At 2 hrs/week, cut all stretch features.

### Architecture Choice

**Monolithic Sequential Pipeline with File-Based IPC** (per Tech Architect recommendation).

```
01.invest_test/
├── investscan/
│   ├── __init__.py
│   ├── cli.py                      # Click-based CLI entry point
│   ├── config.py                   # YAML config loader
│   ├── schema.py                   # InvestSignal + all data contracts
│   ├── normalize_signals.py        # Schema harmonization + dedup
│   ├── steeps_classifier.py        # STEEPs classification for GNC signals
│   ├── sector_mapper.py            # Signal -> Korean market sector
│   ├── korean_market_scorer.py     # Korea relevance scoring
│   ├── synthesize_investment.py    # Direction scoring + conviction
│   ├── evolution_tracker.py        # Cross-week signal matching
│   ├── generate_report.py          # Markdown report + matplotlib
│   ├── generate_html_report.py     # Interactive HTML (Stretch A)
│   ├── journal.py                  # Decision journal (Stretch B)
│   ├── krx_adapter.py              # KRX market data (Stretch C)
│   └── utils.py                    # Shared utilities
├── config/
│   ├── investscan.yaml             # Master config
│   ├── sectors.yaml                # Korean sector definitions
│   ├── steeps_mapping.yaml         # STEEPs -> sector mapping rules
│   └── thresholds.yaml             # All scoring thresholds
├── data/
│   ├── signals/                    # Normalized signal archives (Parquet)
│   ├── evolution/                  # Evolution index (SQLite)
│   ├── journal/                    # Decision journal (SQLite)
│   ├── market/                     # KRX snapshots (Parquet)
│   └── reports/                    # Generated reports archive
├── output/
│   └── {date}/
│       ├── unified_signals.json
│       ├── investment_synthesis.json
│       ├── invest-report-{date}-ko.md
│       └── invest-report-{date}-ko.html
├── tests/
│   ├── test_normalize.py
│   ├── test_steeps.py
│   ├── test_sector_mapper.py
│   ├── test_synthesize.py
│   └── test_evolution.py
├── workflow.md                     # Claude Code orchestration
├── pyproject.toml
└── README.md
```

---

## 9. The Aggressive Bet, Stated Plainly

We are betting that:

1. **20,000-50,000 technically capable Korean investors is a large enough niche** to justify 6 months of development.

2. **Futures studies methodology (STEEPs, FSSF, Three Horizons) applied to investment is a genuine moat** that competitors won't replicate quickly because they don't have two production-ready source systems (EnvScan + GlobalNews) feeding the pipeline.

3. **A CLI tool that produces a high-quality Korean weekly investment briefing will generate a habit loop**: run on Monday morning -> read report over coffee -> make allocation decisions -> record in journal -> review accuracy next week.

4. **"Good enough" signal quality (60%+ directional accuracy) is sufficient** for the target user, because they're using InvestScan for discovery and framing, not for algorithmic trading.

5. **First-mover advantage matters in this niche** -- if we establish InvestScan as "the futures studies investment scanner" before PRISM-INSIGHT or others occupy the space, we own the category definition.

If any of these bets are wrong, the Conservative scenario (3 months, 3 features, 2,000 LOC) would have been the right call. But if they're right, the Aggressive scenario delivers a genuinely unique tool that the ~3,000-8,000 realistic users in our target market would find irreplaceable.

**The worst outcome is not failure -- it's shipping a mediocre tool that's indistinguishable from existing options.** The Aggressive scenario is designed to prevent that by shipping the differentiating features FIRST.
