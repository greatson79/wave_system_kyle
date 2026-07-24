# InvestScan PRD: Conservative Scenario

> **Scenario Philosophy**: "Start small, validate deeply, build only what's proven valuable."
> **Decision Maker**: Conservative Convergence Branch
> **Date**: 2026-03-27

---

## 0. Executive Summary

This PRD defines the **minimum credible product** for InvestScan -- a weekly investment signal synthesis tool that combines outputs from two existing, production-ready systems (EnvironmentScan and GlobalNews-Crawling) into a single actionable Korean-language report.

The Conservative Scenario includes **only the 3 Green Zone features** that all four analysis perspectives (Market, User, Tech, Business) unanimously agreed upon, plus one critical addition from Business Priority: a **Decision Journal**. Everything else is explicitly deferred to Phase 2 or later, with documented re-evaluation triggers.

**Core belief**: The tool is not the lasting value. Your decision history is. Build the habit first.

**Total new code**: ~1,200-1,600 LOC
**Dev time budget**: ~30-40 hours over 6 months (leaving 60-70% buffer from the 50-100 hour budget)
**First useful output**: Week 4 (Month 1)

---

## 1. Absolute Minimum Features (Green Zone Only)

### Feature 1: One-Command Execution (`investscan run`)

**What it does**: A single CLI command that sequentially runs EnvironmentScan, then GlobalNews-Crawling, then produces a unified output directory with both systems' results organized by date.

**What it does NOT do**: No signal normalization. No cross-source correlation. No investment scoring. It literally orchestrates two existing systems and collects their outputs in one place.

**Implementation**:

```
investscan run --date 2026-03-27

  Step 1: Run EnvironmentScan quad scan
  Step 2: Run GlobalNews crawl + analyze
  Step 3: Copy/symlink outputs to output/{date}/
  Step 4: Print summary (signal counts, run time, errors)
```

**Technical scope**:
- `main.py` -- CLI entry point with argparse (~100 LOC)
- `config.py` -- Paths to both source systems (~50 LOC)
- `runner.py` -- Sequential subprocess execution with exit code checking, timeout, basic retry (~200 LOC)
- `collector.py` -- Gather outputs from both systems into unified directory (~150 LOC)

**Estimated LOC**: ~500
**Estimated dev time**: 8-10 hours

**Why this is enough**: Both source systems already produce excellent analysis independently. The user's actual bottleneck is not "I need better analysis" -- it's "I forget to run both systems, and when I do, outputs are scattered." One command, one directory, done.

### Feature 2: Weekly Synthesis Report (Korean Markdown)

**What it does**: A Python script that reads the week's outputs from both systems, extracts key signals, and generates a structured Korean-language Markdown report summarizing the week's investment-relevant findings.

**What it does NOT do**: No automated sector mapping. No conviction scoring. No GICS classification. No cross-source deduplication via embeddings. The synthesis is **template-based** -- it organizes signals by source and date, not by sophisticated analysis.

**Report structure**:

```markdown
# 주간 투자 환경 브리핑 (2026-03-24 ~ 2026-03-28)

## 이번 주 핵심 시그널 (Top 10)
<!-- Sorted by pSST score (EnvScan) or confidence (GlobalNews) -->

## EnvironmentScan 요약
### 기술 (Technological)
### 경제 (Economic)
### 사회 (Social)
### 환경 (Environmental)
### 정치 (Political)

## GlobalNews 요약
### 고관심 토픽 (Burst Score > 0.7)
### 신규 등장 토픽 (Novelty Score > 0.5)

## 결정 기록 (Decision Journal)
<!-- User fills in after reading -->
- 이 시그널을 보고 내가 한 결정:
- 왜 그렇게 결정했는가:
- 다음 주 확인할 것:
```

**Implementation**:
- `weekly_report.py` -- Read both systems' outputs, extract top signals, fill template (~400 LOC)
- `templates/weekly_report_template.md` -- Jinja2 or f-string template (~50 lines)

**Estimated LOC**: ~450
**Estimated dev time**: 10-12 hours

**Why this is enough**: A human reading a well-organized summary once a week is more valuable than an automated system that scores signals without validation data. For the first 3-6 months, signal quality is unvalidatable (Tech's critical insight). So organize, don't analyze.

### Feature 3: Multi-Source Integration (Pipeline Orchestration)

**What it does**: The configuration and glue code that makes Feature 1 work with both source systems. Validates that both systems are installed, their virtual environments exist, and their output directories are accessible.

**What it does NOT do**: No schema harmonization. No unified signal format. Each system's outputs remain in their native format (JSON for EnvScan, Parquet for GlobalNews). The weekly report reads both formats directly.

**Implementation**:
- `health_check.py` -- Verify both source systems are present and functional (~150 LOC)
- `config.py` additions -- Source system paths, expected output locations (~50 LOC)

**Estimated LOC**: ~200
**Estimated dev time**: 4-5 hours

### Feature 4: Decision Journal (Business Priority's #1 Recommendation)

**What it does**: A structured append-only Markdown file where the user records investment decisions made in response to signals. Each entry is timestamped and linked to the weekly report that prompted it.

**Why it is included (even though it is not a Green Zone feature from the four-perspective vote)**: Because Business Priority's analysis was unambiguous -- "The tool is not the lasting value. Your decision history is." The Decision Journal is the **single highest-ROI feature** in the entire system: zero engineering complexity, enormous long-term value.

**Implementation**:

```
investscan journal --add

  Prompts:
  - Date: [auto-filled]
  - Weekly report reference: [auto-linked to latest]
  - Signal that prompted this: [free text]
  - Decision made: [free text]
  - Rationale: [free text]
  - Review date: [user picks: 1 week / 1 month / 3 months]
  - Confidence: [low / medium / high]
```

```
investscan journal --review

  Shows all entries whose review date has passed.
  "You made this decision 4 weeks ago. What happened?"
```

**Implementation**:
- `journal.py` -- CLI for add/review/list, append to `journal/decisions.md` (~250 LOC)
- `journal/decisions.md` -- Append-only Markdown file (runtime)

**Estimated LOC**: ~250
**Estimated dev time**: 5-6 hours

**Why this matters more than signal scoring**: After 6 months, you will have 24+ weekly reports and 50+ decision entries. That decision history -- what you noticed, what you decided, whether you were right -- is genuinely irreplaceable. The signal pipeline can always be improved. Your decision history can only be captured in real time.

---

## 2. What We Explicitly DO NOT Build (And Why That Is Good)

### Deferred to Phase 2 (Yellow Zone -- 3/4 agreed)

| Feature | Why Deferred | Re-evaluation Trigger |
|---------|-------------|----------------------|
| **STEEPs classification engine** | Business called it optional. EnvScan already classifies signals. Duplicating that logic adds complexity without clear value until we know what signals matter for investment. | After 12 weeks of weekly reports, if the user consistently wishes signals were classified differently for investment purposes. |
| **Signal evolution tracking** | Tech and Business both said Phase 2. Requires 3-6 months of data to validate whether tracking evolution improves decisions. | After 3 months of accumulated data, if the user manually notices "I wish I could see how this signal changed over time." |
| **Cross-source signal correlation** | Merging EnvScan JSON + GlobalNews Parquet into a unified schema is the single most complex engineering task (~800 LOC, 3-4 weeks). It creates the LEAST investment value (Business Sustainable's critical insight). | After 3 months, if the weekly report consistently surfaces duplicate signals that confuse the user. |
| **Sector mapping (STEEPs to GICS)** | Rule-based mapping is 80% accuracy at best (Tech's estimate). Without backtesting data, we cannot validate whether better mapping leads to better decisions. | After accumulating 6 months of decision journal entries that could serve as training data. |
| **Investment conviction scoring** | Signal quality is unvalidatable for 3-6 months (Tech's critical insight). A number that looks precise but is actually random is worse than no number at all. | After backtesting becomes possible (6+ months of data). |

### Permanently Deferred (Red Zone -- all agreed to defer)

| Feature | Why Never | Honest Reason |
|---------|-----------|---------------|
| **Web dashboard** | Solo developer, CLI user, local tool | The user works in Claude Code terminal. A web dashboard serves no one. |
| **Backtesting engine** | Requires 6+ months of signal data that does not yet exist | Cannot validate what does not exist yet. |
| **Mobile app** | Requires server infrastructure, app store deployment | Absurdly out of scope for a personal tool. |
| **Plugin system** | Two source systems exist. A third is not planned. | The adapter abstraction pays for itself only with 3+ sources. Two sources = direct integration. |
| **Community features** | Single user tool | There is no community. |
| **Korean sentiment analysis (KoELECTRA)** | Both source systems already perform sentiment analysis | Duplicating NLP capabilities that already exist in upstream systems. |
| **HTML interactive reports** | Markdown is the native format for a Claude Code user | Over-engineering output format for an audience of one. |
| **Self-improvement engine** | Requires months of signal quality feedback data | Cannot self-improve without a baseline to improve from. |

### Why NOT Building Is Good

1. **Developer availability is the #1 risk** (HIGH probability, per Tech analysis). Every feature NOT built is time NOT competing with church responsibilities, thesis work, and other projects.

2. **At 2-4 hours/week of available dev time**, the Conservative Scenario's ~30-40 total dev hours fit comfortably in 6 months. The Balanced Scenario's ~80-100 hours would consume the entire budget with zero buffer. The Aggressive Scenario's 150+ hours is physically impossible.

3. **The part requiring the most engineering creates the LEAST investment value** (Business Sustainable). Signal normalization, schema harmonization, sector mapping, conviction scoring -- these are intellectually satisfying engineering challenges that produce numbers the user cannot validate for months.

4. **Building the habit of weekly review is the actual goal**. If the user runs `investscan run` once a week, reads the report, and writes a journal entry for 3 months straight, the system has succeeded -- regardless of how sophisticated the underlying analysis is.

---

## 3. Technical Architecture (Simplest Possible)

### 3.1 Even Simpler Than Monolithic

The Monolithic Architecture analysis proposed ~2,800 LOC with 8 Python modules, schema harmonization, sector mapping, and investment synthesis. The Conservative Scenario strips this to ~1,200-1,600 LOC with 6 modules and **no analysis layer at all**.

```
01.invest_test/
  investscan/
    __init__.py
    main.py              ← CLI entry point (argparse)
    config.py            ← Source system paths + thresholds
    runner.py            ← Run both source systems sequentially
    collector.py         ← Gather outputs into output/{date}/
    weekly_report.py     ← Read outputs, generate Korean MD report
    journal.py           ← Decision journal add/review/list
    health_check.py      ← Verify source systems are functional
  templates/
    weekly_report.md     ← Report template
  config/
    investscan.yaml      ← Master config (paths, schedule prefs)
  journal/
    decisions.md         ← Append-only decision journal (runtime)
  output/
    {date}/              ← Daily run outputs (runtime)
    weekly/              ← Weekly synthesis reports (runtime)
```

### 3.2 Data Flow

```
EnvironmentScan                    GlobalNews-Crawling
  (existing, unchanged)              (existing, unchanged)
       |                                    |
       |  signals/database.json             |  data/output/signals.parquet
       |  output/WF*_signals_*.json         |  data/output/analysis.parquet
       |                                    |
       +------------------------------------+
                        |
                  collector.py
             (copy/symlink outputs)
                        |
                  output/{date}/
              envscan/   globalnews/
                        |
                  weekly_report.py
             (read both, extract top signals,
              fill Korean report template)
                        |
              output/weekly/
         weekly-{date}.md (Korean)
                        |
                  journal.py
          (user manually records decisions)
                        |
              journal/decisions.md
```

### 3.3 Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **No unified signal schema** | Both systems' output formats are stable. Reading JSON + Parquet directly is simpler than harmonizing into a third format. |
| **No analysis layer** | Both source systems already perform analysis. We organize their outputs, we do not re-analyze them. |
| **Subprocess execution, not Python imports** | Both source systems have their own venvs and dependencies. Subprocess isolation prevents dependency conflicts. |
| **Markdown output only** | User works in terminal. Markdown is native. |
| **Append-only journal** | Simplest possible persistence. No database. No migration. `git log` on the file provides history. |
| **No scheduled execution (cron)** | Manual weekly run builds the habit better than automated background execution. The user should consciously choose to run the tool. |

### 3.4 Dependencies

```
# requirements.txt
# For the Conservative Scenario, we need almost nothing.

pyyaml>=6.0        # Config parsing
jinja2>=3.1        # Report template rendering (optional -- f-strings work too)
pyarrow>=14.0      # Read GlobalNews Parquet output
```

Three dependencies. That is it. No ML models, no SBERT, no spaCy, no PyTorch. Both source systems handle their own dependencies in their own virtual environments.

---

## 4. Risk Profile

### 4.1 Risks in the Conservative Scenario

| Risk | Probability | Impact | Mitigation | Recovery |
|------|-------------|--------|------------|----------|
| **Developer abandons after Month 2** | MEDIUM (30%) | LOW -- Even a partial tool (just the runner + collector) is useful | The Conservative Scenario is designed so that each month's deliverable is independently useful | Nothing to recover from. Each piece works alone. |
| **EnvScan or GlobalNews output format changes** | MEDIUM (30%) | LOW -- Only the collector and report reader need updating | Defensive parsing (`.get()` with defaults). Health check validates expected output structure on every run. | ~2-4 hours of fix-up work. |
| **Weekly report is not useful enough** | MEDIUM (35%) | LOW -- The decision journal is still independently valuable | Iterate on the report template. Add/remove sections based on what the user actually reads. | Template change, not architecture change. |
| **User does not form the weekly habit** | MEDIUM (40%) | HIGH -- This is the only scenario where Conservative fails | `investscan journal --review` reminds about past decisions. Calendar reminder integration. | If the habit fails after 3 months, re-evaluate whether InvestScan serves a real need at all. |

### 4.2 Risks NOT Present in Conservative (That Other Scenarios Have)

| Risk | Scenario That Has It | Why Conservative Avoids It |
|------|---------------------|---------------------------|
| **Signal scoring produces misleading numbers** | Balanced, Aggressive | Conservative has no scoring. Humans read signals directly. |
| **Over-engineering consumes dev budget** | Aggressive | 1,200 LOC. No abstraction layers. No plugin system. |
| **Schema harmonization bugs** | Balanced, Aggressive | Conservative reads both formats natively. No unified schema. |
| **Analysis layer produces hallucinated investment signals** | Aggressive | Conservative does not generate investment signals. It organizes existing ones. |
| **6-month project fails to ship** | Aggressive | Conservative ships a usable tool in Month 1. |

### 4.3 Easy Recovery Paths

**If Conservative is too simple after 3 months**: Upgrade to Balanced Scenario. The runner, collector, and report infrastructure carry forward. You add the analysis layer on top. Nothing is thrown away.

**If the user stops using it**: You spent 30-40 hours, not 150 hours. The decision journal entries from the weeks you DID use it remain valuable.

**If a source system breaks**: The runner continues with one source. The weekly report gracefully degrades to show only available data.

---

## 5. 6-Month Milestones

### M1: Functioning Pipeline (Months 1-2)

**Deliverables**:
- `investscan run` executes both source systems and collects outputs (**Feature 1**)
- `investscan health` validates both source systems are available (**Feature 3**)
- Output directory structure: `output/{date}/envscan/` + `output/{date}/globalnews/`
- Basic error handling: timeout, retry, partial success reporting

**Success criterion**: The user runs `investscan run` at least 4 times in Month 2 (once per week).

**Dev time estimate**: 12-15 hours

**Milestone test**: Run the command. Both systems execute. Outputs appear in the expected directory. The user can find last Tuesday's signals without searching through two separate project directories.

### M2: Weekly Intelligence (Months 3-4)

**Deliverables**:
- `investscan report --week` generates a Korean-language weekly synthesis (**Feature 2**)
- `investscan journal --add` records a decision entry (**Feature 4**)
- `investscan journal --review` surfaces past decisions due for review
- Report template refined based on 4-8 weeks of actual usage from M1

**Success criterion**: The user reads the weekly report AND writes at least one journal entry per week for 4 consecutive weeks.

**Dev time estimate**: 15-18 hours

**Milestone test**: Open the weekly report. Can the user identify the 3 most important signals of the week within 2 minutes of reading? Does the journal entry prompt feel natural, not burdensome?

### M3: Habit Validation (Months 5-6)

**Deliverables**:
- Report template v2 (refined from 8-12 weeks of user feedback)
- Decision journal has 12+ entries with review cycles
- `investscan stats` shows usage summary (weeks run, decisions recorded, reviews completed)
- Documentation: setup guide, weekly workflow guide
- Buffer for bug fixes and quality-of-life improvements

**Success criterion**:
- 8+ consecutive weeks of usage (run + read + journal)
- 3+ decision entries have completed at least one review cycle
- The user can articulate "what InvestScan does for me" in one sentence

**Dev time estimate**: 5-10 hours (mostly template refinement and bug fixes)

**Milestone test**: Ask the user: "Would you miss InvestScan if it stopped working?" If yes, the Conservative Scenario has succeeded and Phase 2 planning begins. If no, we saved 100+ hours by not building the Balanced/Aggressive versions.

---

## 6. Success Metrics (Business Priority KPIs)

### Primary Metrics (Habit Formation)

| Metric | Target (M1-M2) | Target (M3) | Target (M3+) | Measurement |
|--------|----------------|-------------|---------------|-------------|
| **Consecutive weeks of use** | 4 weeks | 8 weeks | 12+ weeks | `investscan stats` |
| **Weekly report read rate** | 75% (3/4 weeks) | 85% (7/8 weeks) | 90%+ | Self-reported or file access time |
| **Decision journal entries per month** | 2+ | 4+ | 4+ | `journal/decisions.md` entry count |
| **Decision review completion rate** | N/A (too early) | 50%+ | 70%+ | Entries with completed reviews / entries due |

### Secondary Metrics (Utility Validation)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time saved per week** | 30+ minutes vs. manually checking both systems | User estimate after 4 weeks |
| **Signal discovery** | 1+ signal per month the user would have missed without InvestScan | Journal entries referencing signals as decision triggers |
| **Run reliability** | 90%+ successful runs (both systems complete without manual intervention) | `investscan stats` |
| **Setup-to-first-run time** | < 30 minutes | Timed during M1 |

### Anti-Metrics (Things We Deliberately Do Not Measure)

| Anti-Metric | Why We Ignore It |
|-------------|-----------------|
| **Signal accuracy** | Cannot be validated without 6+ months of backtesting data. Measuring it now produces false precision. |
| **Number of signals processed** | More signals is not better. The user reads 10 signals per week. Processing 10,000 is irrelevant. |
| **Pipeline execution time** | Whether the run takes 3 hours or 5 hours does not matter for a weekly batch tool. |
| **Code coverage percentage** | 1,200 LOC does not need enterprise testing infrastructure. Manual testing suffices. |

### The Only Metric That Actually Matters

> **After 3 months, does the user run InvestScan every week without being reminded?**

If yes: the habit is formed. Phase 2 begins.
If no: InvestScan does not solve a real problem. Stop building.

---

## 7. When to Choose This Scenario

### Choose Conservative If:

1. **You have less than 4 hours/week for development.** The Conservative Scenario requires ~30-40 total hours. At 2 hours/week, that is 15-20 weeks -- fitting comfortably in 6 months with massive buffer.

2. **You are unsure whether you will actually use InvestScan.** Conservative is the cheapest way to find out. If you stop after Month 2, you have lost 15 hours, not 100.

3. **You want to validate the habit before building the product.** The Business Priority perspective was clear: "Stop building infrastructure for 6 months. USE the system." Conservative enforces this.

4. **You are busy with church, thesis, and other projects.** Conservative acknowledges that InvestScan is one of many priorities, not the main one.

5. **You believe that organized information + human judgment beats automated analysis.** Conservative trusts the user to interpret signals. It does not try to replace human judgment with conviction scores.

### Do NOT Choose Conservative If:

1. **You have a clear 20+ hours/week for InvestScan development.** In that case, the Balanced Scenario's engineering investment pays off faster.

2. **You want InvestScan to produce actionable buy/sell recommendations.** Conservative produces organized information, not recommendations.

3. **You already have the weekly habit and want more depth.** If you have been manually running both systems weekly for 3+ months, you have already validated the habit. Skip to Balanced.

4. **You plan to share InvestScan with others.** Conservative is a personal tool. It requires manual setup, has no documentation beyond a setup guide, and assumes one user.

### The Conservative Scenario Is Right When:

> You can honestly say: "I am not sure I will use this tool every week. Let me find out with minimum investment."

If that sentence resonates, Conservative is your scenario. Build the habit first. Build the product later.

---

## 8. Phase 2 Trigger Conditions

The Conservative Scenario is designed to be a **decision gateway**, not a final state. Here are the specific, measurable conditions that trigger Phase 2 planning:

| Trigger | Threshold | What It Unlocks |
|---------|-----------|-----------------|
| **12 consecutive weeks of use** | Run + read + journal for 12 weeks | Full Phase 2 planning (Balanced Scenario features) |
| **"I keep noticing the same signal in both systems"** | 3+ instances in journal entries | Cross-source signal correlation |
| **"I wish signals were grouped by sector"** | User requests this 3+ times | Sector mapping (STEEPs to GICS) |
| **"I want to know if my past signals were accurate"** | 6 months of accumulated data | Backtesting framework |
| **"Running this manually is annoying"** | After 12+ successful manual runs | Cron/launchd scheduled execution |
| **20+ hours/week become available** | Life circumstances change | Aggressive Scenario features |

**Critical rule**: No Phase 2 feature is built until its trigger condition is met. Anticipated need is not the same as demonstrated need.

---

## Appendix A: Comparison with Other Scenarios

| Dimension | Conservative | Balanced | Aggressive |
|-----------|-------------|----------|------------|
| **Total LOC** | ~1,200-1,600 | ~2,800-3,500 | ~4,000-6,000 |
| **Dev hours** | ~30-40 | ~80-100 | ~150-200 |
| **Time to first useful output** | Week 4 | Week 8 | Week 12 |
| **Analysis sophistication** | None (human reads signals) | Medium (sector mapping, scoring) | High (ML classification, backtesting) |
| **Risk of abandonment** | LOW | MEDIUM | HIGH |
| **Risk of over-engineering** | NONE | MEDIUM | HIGH |
| **Value if user stops at Month 3** | High (habit + journal) | Medium (partial pipeline) | Low (unfinished system) |
| **Dependencies** | 3 packages | ~15 packages | ~30 packages |
| **Addresses "habit" problem** | YES (primary focus) | Partially | No (assumes habit exists) |

## Appendix B: Weekly Workflow (User Perspective)

```
Monday morning:

1. Open terminal
2. Run: investscan run
3. Wait ~4 hours (do other work)
4. Run: investscan report --week
5. Read the weekly report (10-15 minutes)
6. Run: investscan journal --add
7. Record 1-3 decisions or observations (5 minutes)

Total active time: ~20 minutes/week

Monthly:

8. Run: investscan journal --review
9. Review past decisions whose review dates have arrived (15 minutes)

Total active time: ~15 minutes/month
```

**This is the product.** Twenty minutes of focused reading and reflection per week, supported by two powerful analysis systems running in the background. No dashboards. No scores. No ML models. Just organized information, human judgment, and a written record of decisions.

## Appendix C: What "Success" Looks Like at Month 6

The user opens `journal/decisions.md` and sees 24 entries spanning 6 months. Some decisions were right. Some were wrong. All have rationale recorded. The user can answer:

- "When did I first notice the AI regulation trend? What did I do about it?"
- "How many of my 'high confidence' decisions actually played out?"
- "What kind of signals do I consistently overreact to? Underreact to?"

This self-knowledge -- built from structured reflection on real decisions -- is worth more than any automated scoring system. It is the foundation on which every future InvestScan feature will be judged: "Does this feature help me make better decisions, or does it just produce more numbers?"

---

*Build the habit, not the product. The product will follow the habit.*
