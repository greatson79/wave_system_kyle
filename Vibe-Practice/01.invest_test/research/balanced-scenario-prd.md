# InvestScan: Balanced Scenario PRD

> **Decision-Maker Role**: Balanced Scenario Architect
> **Philosophy**: "Realistic yet ambitious. Ship useful, iterate from real usage."
> **Date**: 2026-03-27
> **Guiding Principle**: Build for yourself first. If it helps others, that is a bonus -- not the goal.

---

## 0. Executive Summary

InvestScan is a **local, automated investment direction scanning system** that merges output from two production-ready upstream systems (EnvironmentScan ~23,400 LOC + GlobalNews-Crawling ~25,400 LOC) into a weekly Korean market investment direction report. It runs entirely on a single MacBook, costs zero in infrastructure, and produces a synthesis that neither upstream system can produce alone.

**The Balanced Scenario** accepts the cautious market analysis (5K-15K SAM, niche product) while investing in the one genuine differentiator (STEEPs environmental scanning applied to investment). It does not build for hypothetical users -- it builds for the developer-user first, then opens the door for sharing.

**Scope**: ~3,200 LOC of new Python code. 6 months. One developer, part-time (~60-80 dev hours total). No web dashboard. No SaaS. No mobile. Markdown in, Markdown out.

---

## 1. Core Features (Green Zone + Selective Yellow Zone)

### Feature 1: One-Command Execution (`investscan run`)

**Zone**: GREEN (4/4 agreed)
**Why it exists**: Without this, there is no product. Just two separate systems the user runs manually and cross-references in their head.

**Specification**:

```bash
# The only command a user needs to remember
python -m investscan run --date 2026-03-27

# Or with shorthand for "today"
python -m investscan run

# Resume from failure (checkpoint-based)
python -m investscan run --resume
```

**What it does**:
1. Runs EnvironmentScan quad-scan (WF1-WF4) sequentially (~120 min)
2. Runs GlobalNews crawl + 8-stage analysis (~98 min)
3. Normalizes both signal sets into unified schema (~2 min)
4. Synthesizes investment directions (~5-10 min)
5. Generates weekly synthesis report (~3-5 min)
6. Total: ~4 hours, suitable for 05:00 KST cron start

**Critical engineering requirement**: Checkpointing. The 4-hour pipeline WILL fail partway through. The system must detect which phase completed, store intermediate state, and resume from the last successful checkpoint. This is not a nice-to-have; it is the difference between a usable tool and a frustrating one.

**Implementation approach**: Python orchestrator script (not workflow.md as sole orchestrator). Claude Code workflow.md calls the Python orchestrator. The orchestrator manages state via a simple `state.yaml` file tracking phase completion timestamps and exit codes.

```python
# investscan/orchestrator.py (core logic)
PHASES = [
    Phase("envscan", cmd="cd {envscan_root} && ..."),
    Phase("globalnews", cmd="cd {gnews_root} && ..."),
    Phase("normalize", func=normalize_signals),
    Phase("synthesize", func=synthesize_investment),
    Phase("report", func=generate_report),
]

def run(date: str, resume: bool = False):
    state = load_state(date)
    for phase in PHASES:
        if resume and state.is_completed(phase.name):
            log.info(f"Skipping completed phase: {phase.name}")
            continue
        result = phase.execute(date)
        state.mark(phase.name, result)
        if not result.success:
            state.save()
            raise PipelineError(f"Phase {phase.name} failed. Run with --resume to continue.")
    state.save()
```

**Estimated LOC**: ~400 (orchestrator + state management + CLI entry point)

---

### Feature 2: Weekly Synthesis Report (Korean Markdown)

**Zone**: GREEN (4/4 agreed)
**Why it exists**: The entire point. A report that synthesizes signals from both systems into actionable Korean market investment direction insights.

**Report structure**:

```markdown
# InvestScan 주간 투자 방향 스캐닝 리포트
> 기간: 2026-03-21 ~ 2026-03-27
> 생성: 2026-03-27 10:00 KST
> 소스: EnvironmentScan (4개 워크플로우) + GlobalNews (116개 사이트)

## 1. 핵심 투자 방향 요약
### 단기 (1-3개월)
- [방향] 반도체 섹터 강세 지속 — 확신도: ●●●●○ (높음)
  - 근거: AI 투자 가속 (EnvScan WF1 3건 + GlobalNews 12건 수렴)
  - 관련 종목군: 삼성전자, SK하이닉스, 한미반도체

### 중기 (3-6개월)
- ...

### 장기 (6-12개월)
- ...

## 2. STEEPs 차원별 시그널 분석
| 차원 | 이번 주 시그널 수 | 주요 테마 | 투자 시사점 |
|------|-----------------|----------|------------|
| S (사회) | 12 | 고령화 가속, MZ 소비 변화 | 헬스케어 +, 소비재 중립 |
| T (기술) | 28 | AI 인프라 투자, 양자컴퓨팅 | 반도체 ++, 소프트웨어 + |
| E (경제) | 15 | 금리 동결 전망, 원화 강세 | 수출주 중립, 내수주 + |
| E (환경) | 8 | 탄소중립 규제 강화 | 신재생에너지 +, 정유 - |
| P (정치) | 6 | 한미 통상 협상 | 자동차 중립, 방산 + |
| s (안보) | 3 | 사이버 보안 이슈 | 보안 섹터 + |

## 3. 시그널 수렴 분석 (Cross-Source Convergence)
[두 시스템에서 독립적으로 포착된 동일 주제 시그널 = 높은 확신]
...

## 4. 위험 요인 (Risk Radar)
...

## 5. 이번 주 특이 시그널 (Weak Signal Watch)
[pSST 점수 높거나 L4_long/L5_singularity 시그널 중 주목할 것들]
...

## 6. 데이터 소스 요약
- EnvScan: 스캔 X건, 시그널 Y건 (pSST 평균 Z점)
- GlobalNews: 기사 A건, 시그널 B건 (L1: C, L2: D, L3: E, L4: F, L5: G)
- 교차 검증 시그널: H건
```

**Language**: Korean throughout. This is a personal decision tool for a Korean market investor. No English version needed for the report itself.

**Format**: Single `.md` file per week, stored in `output/{date}/invest-report-{date}.md`. The report is the product. Everything else is plumbing.

**Estimated LOC**: ~500 (report generation + template + Korean formatting)

---

### Feature 3: Multi-Source Integration (Signal Normalization Layer)

**Zone**: GREEN (4/4 agreed)
**Why it exists**: This is the technical foundation that makes the synthesis possible. Without normalizing two radically different signal schemas into one, there is no cross-source analysis.

**The normalization challenge**:

| Dimension | EnvironmentScan | GlobalNews | Unified |
|-----------|----------------|------------|---------|
| ID format | `TC-20260325-001` | UUID | `IS-{date}-{seq}` |
| Signal format | JSON | Parquet | JSON (internal) |
| Classification | STEEPs (S,T,E,E,P,s) | 5-Layer (L1-L5) | Both preserved + cross-mapped |
| Confidence | pSST 0-100 | confidence 0-1 | Normalized 0-1 scale |
| Temporal | Signal evolution states | Time series | Unified temporal class |
| Dedup | Title similarity | simhash/MinHash | Content hash + title similarity |

**Cross-mapping rules (STEEPs to L-Layer)**:

This is not a 1:1 mapping. STEEPs classifies the *domain* of a signal; L-Layer classifies its *temporal persistence*. A single signal has both dimensions:

```python
# A signal can be simultaneously:
#   STEEPs: T_Technological
#   L-Layer: L3_mid (medium-term technological shift)
#
# Cross-mapping enrichment:
# - EnvScan signals get L-Layer assigned based on pSST temporal indicators
# - GlobalNews signals get STEEPs assigned based on topic keywords + sector mapping
```

**Unified signal schema** (simplified from the Long-Term Architecture's proposal -- we do not need frozen dataclasses and schema versioning for a solo-developer MVP):

```python
@dataclass
class UnifiedSignal:
    signal_id: str
    source_system: str          # "envscan" | "globalnews"
    source_signal_id: str
    title: str
    summary: str
    detected_at: datetime

    # Dual classification
    steeps_category: str | None     # S, T, E_economic, E_environmental, P, s
    signal_layer: str | None        # L1_fad, L2_short, L3_mid, L4_long, L5_singularity
    confidence: float               # Normalized 0-1

    # Investment mapping (populated in synthesis phase)
    sectors: list[str] | None
    direction: str | None           # "bullish" | "bearish" | "neutral"
    korea_relevance: float | None   # 0-1

    # Evidence
    source_count: int
    evidence_summary: str
    content_hash: str
```

**File-based IPC (correct for this use case)**:
- InvestScan reads from EnvScan's output directories and GlobalNews's Parquet files
- Zero changes to either upstream system
- The normalization layer is a pure reader/transformer -- it never writes back to source systems

**Estimated LOC**: ~600 (normalize_signals.py + schema.py + utils.py)

---

### Feature 4: STEEPs Investment Classification (Selective Yellow Zone)

**Zone**: YELLOW (3/4 agreed -- Business called it optional)
**Decision**: INCLUDE. This is the only genuine differentiator.

**Why include despite Business objection**: Business Priority branch's core insight was "the tool is not the value; the decision history is the value." But to generate decision-worthy signals, those signals must be *classified in a way no competitor offers*. STEEPs classification applied to investment is what makes InvestScan not-just-another-PRISM-INSIGHT. Without it, we are building a worse version of something that already exists.

**What STEEPs adds to investment analysis**:

Competitors analyze news by *topic* (semiconductor, oil, currency). InvestScan analyzes by *force dimension*:

| Dimension | Investment Implication | Example |
|-----------|----------------------|---------|
| **S** (Social) | Demographic shifts = sector rotation signals | Aging population -> healthcare long, consumer discretionary short |
| **T** (Technological) | Innovation waves = growth sector identification | AI infrastructure boom -> semiconductor + datacenter REIT |
| **E** (Economic) | Macro conditions = market regime detection | Rate cuts -> growth stocks, strong won -> exporters neutral |
| **E** (Environmental) | Regulatory + climate = policy-driven sectors | Carbon pricing -> green energy long, coal short |
| **P** (Political) | Geopolitical risk = defense + trade-sensitive sectors | US-China tension -> defense +, China-exposed - |
| **s** (Security) | Stability risk = safe haven + cyber sectors | Cyber attacks -> cybersecurity +, general risk-off |

**This multi-dimensional scanning is what no free tool offers.** TradingView gives you price charts. PRISM-INSIGHT gives you AI stock picks. OpenBB gives you financial data. None of them give you "Here is what social, technological, economic, environmental, political, and security forces are converging to suggest about Korean market sectors over the next 3-12 months."

**Implementation**: Leveraged from EnvironmentScan's existing STEEPs classifier. For GlobalNews signals that lack STEEPs classification, apply keyword-based STEEPs assignment using the sector mapping rules (a new ~300 LOC module). Accept 70-80% accuracy for v1 -- it is better to have approximate STEEPs than no STEEPs.

**Estimated LOC**: ~300 (steeps_classifier.py for GlobalNews signal enrichment)

---

## 2. Conditional Features (Yellow Zone with "Include If" Criteria)

### Conditional Feature A: Signal Evolution Tracking

**Zone**: YELLOW (Tech + Business say Phase 2 possible)

**Include if**: By Month 3, the weekly reports consistently reference "this signal appeared 3 weeks ago and has strengthened" -- manually. When the user finds themselves repeatedly scrolling back through old reports to track signal trajectories, the manual pain justifies automation.

**Exclude if**: By Month 3, most signals are one-off events that do not recur. In a volatile market (which KOSPI has been in 2025-2026), signals may be high-frequency / low-persistence, making evolution tracking less valuable.

**What it would be**:
- Track signal recurrence across weeks (same STEEPs category + similar title/content)
- Assign evolution state: NEW, RECURRING, STRENGTHENING, WEAKENING, FADING
- Weekly report gains a "Signal Trajectory" section showing how this week's directions compare to last 4 weeks

**Estimated LOC if built**: ~400 (evolution_tracker.py + SQLite signal history)
**Trigger for inclusion**: User manually tracks signal evolution for 4+ consecutive weeks

---

### Conditional Feature B: Decision Journal + Outcome Tracking

**Zone**: Not formally zoned, but Business Priority branch identified this as "the real value"

**Include if**: The user actually makes investment decisions based on the reports (not just reading them for intellectual interest). When the user starts annotating reports with "I acted on this signal" or "I should have acted on this," the decision journal becomes essential.

**Exclude if**: The user treats reports as background reading rather than decision inputs. If no investment action is taken based on the reports for 2+ months, the journal is overhead.

**What it would be**:
- Simple append-only YAML/JSON log:
  ```yaml
  - date: 2026-03-27
    signal_id: IS-20260327-003
    decision: "Increased semiconductor ETF position by 5%"
    confidence: "medium"
    outcome_check_date: 2026-06-27
    outcome: null  # filled in later
  ```
- Quarterly review: compare decisions against actual market outcomes
- No automation -- purely a structured note-taking format

**Estimated LOC if built**: ~150 (decision_journal.py -- mostly I/O scaffolding)
**Trigger for inclusion**: User makes 3+ investment decisions citing report signals within first 2 months

---

### Conditional Feature C: Scheduled Daily Execution (cron/launchd)

**Zone**: YELLOW (consensus as "should have")

**Include if**: The user runs `investscan run` manually at least 3 times per week for 4+ weeks. The manual habit proves the report is valuable enough to automate.

**Exclude if**: The user runs it sporadically (once a week or less). Automation overhead is not justified for occasional use.

**What it would be**:
- `launchd` plist for macOS (not cron -- launchd handles sleep/wake correctly)
- Run at 05:00 KST daily or weekly (configurable)
- Lock file to prevent concurrent runs
- Simple log rotation (keep last 30 runs)
- Notification on completion (macOS `osascript` alert)

**Estimated LOC if built**: ~200 (run_daily.sh + launchd config + notification)
**Trigger for inclusion**: 4 consecutive weeks of manual daily/weekly execution

---

## 3. Technical Architecture

### 3.1 Architecture Decision: Monolithic Sequential Pipeline

**Chosen**: Monolithic with file-based IPC, per the Fast-Ship Tech Architect's recommendation.

**Not chosen**: Spine + Rib plugin architecture (Long-Term Architect). Reason: For a solo developer building a personal tool, plugin abstractions add ~7.5 developer-days of overhead for extensibility that may never be exercised. If signal source diversity expands beyond 3 sources, refactor then. YAGNI wins for the Balanced scenario.

**Not chosen**: Claude Code workflow.md as sole orchestrator. Reason: A 4-hour pipeline needs programmatic error handling, state management, and retry logic that workflow.md cannot provide robustly. workflow.md invokes the Python orchestrator; the orchestrator manages the pipeline.

### 3.2 Directory Structure

```
01.invest_test/
├── CLAUDE.md                           ← Project instructions
├── workflow.md                         ← Claude Code entry point (invokes orchestrator)
├── investscan/
│   ├── __init__.py
│   ├── __main__.py                     ← CLI: python -m investscan run [--date] [--resume]
│   ├── config.py                       ← Paths to upstream systems, thresholds, sector defs
│   ├── orchestrator.py                 ← Pipeline phases, checkpointing, error handling
│   ├── schema.py                       ← UnifiedSignal dataclass
│   ├── normalize_signals.py            ← Read both formats -> UnifiedSignal list
│   ├── steeps_classifier.py            ← Assign STEEPs to GlobalNews signals
│   ├── sector_mapper.py                ← Signal -> Korean market sector mapping
│   ├── synthesize_investment.py        ← Direction scoring, conviction, cross-source
│   ├── generate_report.py              ← Korean markdown report generation
│   └── utils.py                        ← Date handling, Parquet I/O, logging
├── config/
│   ├── sectors.yaml                    ← KOSPI/KOSDAQ sector definitions + keywords
│   └── thresholds.yaml                 ← Scoring thresholds (conviction, relevance)
├── output/
│   └── {date}/
│       ├── unified_signals.json        ← Normalized signal dump (debug + audit)
│       ├── synthesis.json              ← Investment direction synthesis
│       └── invest-report-{date}.md     ← The actual product
├── research/                           ← Prior analysis (this file, market analysis, etc.)
└── tests/
    ├── test_normalize.py
    ├── test_sector_mapper.py
    └── test_synthesize.py
```

### 3.3 Data Flow

```
EnvironmentScan                        GlobalNews-Crawling
  signals/database.json                  data/output/signals.parquet
  output/WF*_signals_*.json              data/output/analysis.parquet
  integrated/analysis/*.json             data/output/topics.parquet
          |                                        |
          v                                        v
  +--------------------------------------------------+
  |          normalize_signals.py                      |
  |  - Read EnvScan JSON -> list[UnifiedSignal]        |
  |  - Read GlobalNews Parquet -> list[UnifiedSignal]  |
  |  - Deduplicate by content_hash + title similarity  |
  |  - Assign missing STEEPs (steeps_classifier.py)    |
  +---------------------------+------------------------+
                              |
                              v
  +--------------------------------------------------+
  |        synthesize_investment.py                     |
  |  - Map signals to KOSPI/KOSDAQ sectors             |
  |  - Score direction (bullish/bearish/neutral)       |
  |  - Compute conviction (multi-source = higher)      |
  |  - Compute Korea relevance (0-1)                   |
  |  - Group by time horizon (short/mid/long)          |
  +---------------------------+------------------------+
                              |
                              v
  +--------------------------------------------------+
  |          generate_report.py                        |
  |  - Fill Korean markdown template                   |
  |  - STEEPs dimension summary table                  |
  |  - Cross-source convergence highlights             |
  |  - Risk radar                                      |
  |  - Weak signal watch                               |
  +--------------------------------------------------+
                              |
                              v
              output/{date}/invest-report-{date}.md
```

### 3.4 Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Sequential execution** | Network I/O bottleneck. Parallel crawling triggers anti-bot and does not save time. |
| **File-based IPC** | Zero coupling to upstream systems. Correct for daily batch. Simplest integration. |
| **Rule-based sector mapping** | 80% accuracy for v1. ML needs training data we do not have. Ship now, improve later. |
| **JSON for intermediate data** | Debuggable. `jq` queryable. Parquet only for reading GlobalNews output. |
| **Markdown reports, no web UI** | User works in terminal + editor. Markdown IS the native format. |
| **Korean-only reports** | Personal tool for Korean market. English translation adds complexity for zero value. |
| **Python orchestrator, not workflow.md** | 4-hour pipeline needs programmatic checkpointing and error handling. |
| **No database for v1** | Signal volume is ~100-500 per week. JSON files suffice. SQLite when history tracking is added. |

### 3.5 Upstream System Dependencies

| System | Version | Output Contract | Risk |
|--------|---------|-----------------|------|
| **EnvironmentScan v4** | Pinned at current | `signals/database.json` (JSON array) | MEDIUM: Active development may change schema |
| **GlobalNews-Crawling** | Pinned at current | `data/output/signals.parquet` (Parquet schema) | LOW: Stable schema with defined columns |

**Mitigation**: Defensive parsing (`.get()` with defaults). Schema validation on every run with clear error messages when fields are missing or unexpected.

---

## 4. Risk Profile

### Risk 1: Signal Quality Unvalidatable (PROBABILITY: HIGH, IMPACT: HIGH)

**The problem**: How do we know if "InvestScan says semiconductors bullish" is any good? Without backtesting against actual KOSPI sector performance, we are flying blind on accuracy.

**Balanced mitigation** (not full backtesting framework, not ignoring it):
- **Month 1-3**: Accept that signal quality is unproven. Frame reports as "environmental scanning synthesis" not "investment advice." Include explicit uncertainty language in every direction call.
- **Month 4+**: Manually review past reports against actual market moves. Keep a simple spreadsheet: "Report said X, market did Y." This is Business Priority's "decision history" insight applied as a validation tool.
- **Month 6+**: If the manual tracking shows signal-to-outcome correlation > 60%, consider building automated backtesting. If < 40%, fundamentally rethink the synthesis algorithm.

**Recovery path**: Even if directional signals are poor, the STEEPs-organized environmental scan itself has value as a research tool. "What forces are shaping markets" is useful regardless of whether the specific direction calls are accurate.

### Risk 2: EnvScan Claude API Reliability + Cost (PROBABILITY: MEDIUM, IMPACT: HIGH)

**The problem**: EnvironmentScan's quad-scan uses Claude API for agent reasoning. API outages, rate limits, or cost increases can break half the pipeline.

**Balanced mitigation**:
- **Graceful degradation**: If EnvScan fails, still produce a report from GlobalNews data alone. Mark it as "partial scan -- EnvScan data unavailable." This is ~1 day of engineering.
- **Cost monitoring**: Track Claude API usage per run. If monthly cost exceeds a threshold (e.g., 50,000 KRW), alert and consider reducing scan frequency.

**Recovery path**: GlobalNews runs entirely locally (zero API cost). The system always has a baseline even when EnvScan is down.

### Risk 3: Maintenance Burden Causes Abandonment (PROBABILITY: HIGH, IMPACT: FATAL)

**The problem**: The cautious market analysis identified this as the #1 risk for local tools. When crawlers break, Python dependencies conflict, or macOS updates cause issues, the user stops using the tool.

**Balanced mitigation**:
- **Graceful degradation everywhere**: If 10 of 116 GlobalNews sites break, the pipeline still runs. If 1 of 4 EnvScan workflows fails, the report still generates. Every failure is logged but non-fatal unless all sources fail.
- **Dependency minimization**: InvestScan itself has minimal dependencies (Python stdlib + JSON + Parquet reader). The upstream systems carry the heavy dependency burden.
- **Self-diagnosis**: `investscan health` command that checks upstream system availability, output freshness, and dependency status. 30 seconds, runs before each full pipeline.

**Recovery path**: If maintenance burden becomes too high, scale back to running GlobalNews only (zero API cost, battle-tested crawling system) and produce a simplified report.

### Risk 4: Over-Engineering (PROBABILITY: MEDIUM, IMPACT: MEDIUM)

**The problem**: The Long-Term Architect's proposal has 17 features across 3 phases with plugin architectures, frozen dataclasses with schema versioning, 5 abstract base classes, and 106 developer-days of work. For a solo developer building a personal tool, this is a trap.

**Balanced mitigation**:
- **The "Would I Actually Change This?" test**: Before adding an abstraction, ask: "In the next 6 months, will I add a second implementation?" If no, use a direct function call.
- **Concrete ceiling**: Maximum 3 source adapters (EnvScan, GlobalNews, possibly KRX API later). If that is the final set, adapter abstraction was unnecessary -- but the cost was only a few extra hours.
- **Kill switch**: If after Month 2 no useful investment direction report has been produced, stop all architecture work and write a 500-line script that concatenates both systems' outputs with basic formatting.

---

## 5. Six-Month Milestones

### M1: Working Pipeline (Month 1-2, ~25-30 dev hours)

**Deliverable**: `investscan run` produces a basic Korean markdown report from both upstream systems.

| Week | Task | Hours |
|------|------|-------|
| W1 | Project scaffolding: `investscan/` package, config.py, schema.py, CLI entry point | 4h |
| W2 | normalize_signals.py: Read EnvScan JSON, parse into UnifiedSignal | 5h |
| W3 | normalize_signals.py: Read GlobalNews Parquet, parse + basic dedup | 5h |
| W4 | orchestrator.py: Sequential phase execution with checkpointing | 4h |
| W5 | synthesize_investment.py: Rule-based sector mapping + direction scoring | 6h |
| W6 | generate_report.py: Korean markdown template + basic report generation | 4h |
| W7 | End-to-end test: Run full pipeline, fix issues, produce first real report | 4h |
| W8 | steeps_classifier.py: Assign STEEPs to GlobalNews signals (keyword-based) | 3h |

**M1 success criteria**:
- [ ] `python -m investscan run` completes without manual intervention
- [ ] Output report contains signals from BOTH upstream systems
- [ ] STEEPs dimension table is populated
- [ ] At least 3 sector-level direction calls with rationale
- [ ] User (developer) reads the report and finds at least 2 insights they did not already know

**M1 exit gate**: The user reads the M1 report and answers: "Would I run this again next week?" If YES, proceed to M2. If NO, diagnose why and fix before moving on.

---

### M2: Quality + Polish (Month 3-4, ~20-25 dev hours)

**Deliverable**: Reports are useful enough to inform actual investment thinking. Cross-source convergence works. Confidence scoring is calibrated.

| Week | Task | Hours |
|------|------|-------|
| W9 | Cross-source convergence detection (title similarity + STEEPs overlap) | 5h |
| W10 | Confidence scoring calibration (fuse pSST + GlobalNews confidence) | 4h |
| W11 | Sector mapper refinement (add Korean market-specific rules, chaebol mapping) | 4h |
| W12 | Report enrichment: risk radar section, weak signal watch section | 4h |
| W13 | `investscan health` diagnostic command | 3h |
| W14 | Error handling: graceful degradation when one system fails | 3h |
| W15-16 | Buffer for bug fixes, report format iteration, threshold tuning | 4h |

**M2 success criteria**:
- [ ] Cross-source convergence section identifies at least 2 signals confirmed by both systems per week
- [ ] Confidence levels feel calibrated (high confidence signals are actually more reliable than low)
- [ ] Pipeline runs end-to-end 4 out of 5 times without manual intervention
- [ ] User has run the pipeline at least 4 times and read every report

**M2 exit gate**: The user answers: "Has this report told me something that changed how I think about my investment positions?" If YES even once, the product is working.

---

### M3: Hardening + Conditional Features (Month 5-6, ~15-20 dev hours)

**Deliverable**: Production-quality daily tool. Conditional features added based on actual usage patterns.

| Week | Task | Hours |
|------|------|-------|
| W17 | Evaluate conditional features based on M1-M2 usage data | 2h |
| W18-19 | Implement 1-2 conditional features that passed "include if" triggers | 6h |
| W20 | Scheduled execution setup (launchd) if triggered | 3h |
| W21 | Test suite: contract validation, sector mapping, synthesis correctness | 4h |
| W22 | Historical report archive: index of all past reports, searchable | 3h |
| W23 | User documentation: config guide, troubleshooting, report interpretation | 2h |
| W24 | Buffer for final polish, edge cases, M3 report quality iteration | 2h |

**M3 success criteria**:
- [ ] System has run for 8+ weeks producing usable reports
- [ ] No more than 1 pipeline failure per month requiring manual intervention
- [ ] If scheduled execution is activated, it runs 5 out of 7 days without intervention
- [ ] All conditional feature triggers have been evaluated with data
- [ ] The user can answer: "What did InvestScan tell me this quarter that I would not have known otherwise?" with specific examples

**M3 exit gate**: The system is either a useful personal tool (success) or an interesting experiment that taught something about signal synthesis (acceptable failure). Either outcome is fine.

---

## 6. Success Metrics

### 6.1 Usage Metrics (The User IS the Developer)

| Metric | Month 2 Target | Month 4 Target | Month 6 Target |
|--------|---------------|----------------|----------------|
| Pipeline runs per month | >= 2 | >= 4 | >= 8 (weekly+) |
| Reports actually read (not just generated) | 100% | 100% | 100% |
| Time to read report | < 15 min | < 10 min | < 10 min |
| Pipeline success rate | > 60% | > 80% | > 90% |
| Manual intervention per run | <= 2 | <= 1 | 0 |

### 6.2 Quality Metrics

| Metric | Month 2 Target | Month 4 Target | Month 6 Target |
|--------|---------------|----------------|----------------|
| Signals per report (both sources) | >= 20 | >= 30 | >= 40 |
| Cross-source convergent signals | N/A | >= 2/week | >= 3/week |
| Sector direction calls with rationale | >= 3 | >= 5 | >= 7 |
| "New insight" rate (user self-assessment) | >= 1/report | >= 2/report | >= 2/report |
| Direction accuracy (manual retrospective) | Not measured | Baseline established | > 50% |

### 6.3 The Only Metric That Actually Matters

> **Does the developer-user run InvestScan voluntarily, without feeling obligated to, because the reports genuinely inform their investment thinking?**

If YES at Month 6 -- the project succeeded.
If NO at Month 3 -- trigger the kill switch. Stop building architecture. Write a simple script or abandon.

---

## 7. When to Choose This Scenario

### Choose Balanced if:

1. **You are building this for yourself first.** The Business Priority branch said "build for yourself, share as byproduct." The Balanced scenario takes this literally. Every feature is evaluated against "Does the developer-user need this?" not "Would 5,000 hypothetical users want this?"

2. **You have 60-80 hours of part-time dev capacity over 6 months.** Not 100+ hours (Aggressive assumes), not 30 hours (Conservative assumes). You can dedicate 2-4 focused hours per week.

3. **You want STEEPs as the differentiator but do not need a plugin architecture to support it.** STEEPs classification is included because it is the one thing that makes InvestScan worth building over just reading both systems' outputs separately. But it is implemented as a direct function call, not a pluggable analyzer.

4. **You accept that signal accuracy is an open question.** The Balanced scenario does not pretend that rule-based sector mapping will be highly accurate from day one. It builds the pipeline, produces reports, and uses real usage data to decide what to improve.

5. **You are comfortable with "good enough" over "perfect."** 80% sector mapping accuracy, 70% STEEPs assignment accuracy, reports that sometimes have noisy signals -- all acceptable. The alternative is spending 6 months building an architecture and never producing a report.

### Do NOT choose Balanced if:

1. **You want to share this with other users immediately.** Balanced assumes a single developer-user. Installation docs, onboarding, and UX are minimal. Choose Aggressive if sharing is a near-term goal.

2. **You need validated investment signals.** Balanced does not include backtesting. If you need proven accuracy before acting on signals, add the backtesting framework (Aggressive territory) or use a different approach entirely.

3. **You only have 20-30 hours total.** Choose Conservative -- just build the normalization layer and a basic report, skip STEEPs and cross-source convergence.

---

## 8. What "Build for Yourself, Share as Byproduct" Means Concretely

The Business Priority branch's most important insight shapes every decision in this PRD:

**Feature decisions**: Every feature passes through "Does the developer-user need this?" before "Would other users want this?" This is why we include STEEPs (the developer-user is interested in environmental scanning methodology) but exclude one-click installation (the developer-user can run Python commands) and web dashboard (the developer-user reads Markdown).

**Quality decisions**: Report quality is measured by "Did I learn something?" not "Would 1,000 users understand this?" The reports can be information-dense, assume domain knowledge, and use financial terminology without explanation.

**Architecture decisions**: No need for multi-user auth, horizontal scaling, API endpoints, or cloud deployment. The architecture serves one user on one machine. If sharing happens, it happens by open-sourcing the repo -- not by building a platform.

**Timeline decisions**: No launch deadline. No marketing milestones. No user acquisition targets. The only timeline pressure is "Am I personally finding this useful?" If the answer is "no" after Month 3, pivot or stop. If "yes," keep going at whatever pace feels sustainable.

**Investment decision tracking is the exit strategy**: If InvestScan works well for the developer-user, the accumulated decision journal (tracking signals -> decisions -> outcomes) becomes the most valuable artifact -- more valuable than the code. This history of "what signals preceded what market moves" is unique, personal, and irreproducible by any competitor. It is the moat that builds over time.

---

## Appendix A: LOC Budget

| Module | Estimated LOC | Priority |
|--------|--------------|----------|
| `__main__.py` (CLI) | 80 | P0/M1 |
| `config.py` | 120 | P0/M1 |
| `schema.py` | 100 | P0/M1 |
| `orchestrator.py` | 300 | P0/M1 |
| `normalize_signals.py` | 400 | P0/M1 |
| `steeps_classifier.py` | 300 | P0/M1 |
| `sector_mapper.py` | 350 | P0/M1 |
| `synthesize_investment.py` | 500 | P0/M1 |
| `generate_report.py` | 500 | P0/M1 |
| `utils.py` | 150 | P0/M1 |
| `config/sectors.yaml` | 200 | P0/M1 |
| `config/thresholds.yaml` | 50 | P0/M1 |
| **M1 Subtotal** | **~3,050** | |
| Cross-source convergence (in synthesize) | +200 | P1/M2 |
| Health diagnostic | +150 | P1/M2 |
| Graceful degradation logic | +200 | P1/M2 |
| **M2 Subtotal** | **~3,600** | |
| Signal evolution tracker (conditional) | +400 | P2/M3 |
| Decision journal (conditional) | +150 | P2/M3 |
| Scheduled execution (conditional) | +200 | P2/M3 |
| Tests | +500 | P1/M3 |
| **M3 Maximum** | **~4,850** | |

**Complexity budget**: InvestScan should never exceed ~5,000 LOC (excluding tests). If it approaches that, something is over-engineered.

---

## Appendix B: Comparison with Other Scenarios

| Dimension | Conservative | **Balanced (This)** | Aggressive |
|-----------|-------------|---------------------|------------|
| Dev hours (6 months) | ~30-40 | **~60-80** | ~100+ |
| New LOC | ~1,500-2,000 | **~3,000-4,000** | ~5,000-7,000 |
| STEEPs classification | Deferred | **Included (keyword-based)** | Included (ML-enhanced) |
| Signal evolution | No | **Conditional** | Yes |
| Cross-source convergence | Basic | **Implemented** | Implemented + semantic |
| Backtesting | No | **Manual only** | Automated framework |
| Web UI | No | **No** | Streamlit dashboard |
| Scheduled execution | Manual only | **Conditional** | Yes (launchd + monitoring) |
| Plugin architecture | No | **No** | Yes (BaseAnalyzer ABC) |
| Test suite | Minimal | **Core paths** | Comprehensive + golden dataset |
| Risk of not shipping | Very low | **Low** | Medium-High |
| Risk of under-delivering | Medium | **Low** | Very low (if shipped) |
| "Would I use this?" confidence | 60% | **80%** | 95% (but might not finish) |

---

## Appendix C: Non-Goals (Explicitly Out of Scope)

These are not being deferred -- they are being rejected for the Balanced scenario:

1. **Web dashboard / Streamlit UI**: The user reads Markdown. A web UI adds maintenance burden for zero personal value.
2. **Mobile access**: Reports are read at a desk. Mobile-responsive anything is wasted effort.
3. **Multi-user support**: One user. One machine. No auth, no permissions, no sharing infrastructure.
4. **Real-time alerts**: This is a weekly batch analysis tool, not a trading terminal.
5. **Plugin architecture**: YAGNI for 2 source systems. Refactor if/when a 3rd source is added.
6. **English translation of reports**: Personal tool, Korean market, Korean user. English is overhead.
7. **Backtesting framework**: Requires historical market data pipeline + comparison logic. Manual retrospective suffices for the Balanced scenario.
8. **Community features**: No forums, no shared signal feeds, no social anything.
9. **Deployment packaging**: No Docker, no brew formula, no installer script. The developer runs Python directly.
10. **SaaS of any kind**: Local. Local. Local.
