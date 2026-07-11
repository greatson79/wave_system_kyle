# PHASE 2: Consolidated Four-Perspective Discussion

> **Supreme Moderator**: Synthesizing all 8 Phase 1 branches into unified direction
> **Date**: 2026-03-27
> **Status**: Complete

---

## Preamble: What Phase 1 Established

Eight parallel research branches produced a rich but contradictory evidence base. The core tension:

**Optimistic branches** say InvestScan occupies an empty quadrant (macro scanning + local + evidence chains + cross-domain synthesis) that constitutes a category-defining product. No competitor can replicate this without destroying their business model.

**Cautious branches** say InvestScan wins on 6 analytical dimensions but loses on 11 product dimensions against AlphaSquare. The TAM is 20K-50K users. 99% of Korean investors will never use a CLI tool. The "overwhelmingly superior" claim conflates analytical depth with product superiority.

**The key insight both sides agree on**: "AlphaSquare answers 'which stock should I buy?' InvestScan answers 'what is happening in the world and what does it mean for my portfolio?'" This is a CATEGORY difference, not a QUALITY difference.

---

## DISCUSSION A: MARKET PRIORITY

### Question A1: Is "overwhelmingly superior" the right positioning or "category creator"?

**Verdict: CATEGORY CREATOR.**

The evidence is unambiguous. The Cautious Superiority Challenge document demonstrated that InvestScan wins on 6 dimensions (all analytical) while AlphaSquare wins on 11 dimensions (all product/experience). Claiming "overwhelmingly superior" against a product that beats you on 11 out of 17 dimensions is factually indefensible and strategically dangerous.

However, the Aggressive Competitive Strategy correctly identifies that "overwhelmingly superior" can be domain-qualified: **"overwhelmingly superior for macro-analytical investment direction"** is defensible. The Leica-vs-iPhone analogy holds: a Leica is overwhelmingly superior for photojournalism despite having <1% of the camera market.

**Resolved positioning**: InvestScan is not a better investment app. It is a new category -- "local macro intelligence for investment direction" -- that answers a question no existing product addresses.

### Question A2: What features capture the "empty quadrant"?

The empty quadrant is defined by four intersecting capabilities no competitor occupies simultaneously:

1. **Macro environmental scanning** (STEEPs across 6 domains) -- not just financial data
2. **Evidence chain transparency** -- full reasoning from source to direction, not black-box
3. **Signal evolution tracking** -- temporal narrative, not point-in-time snapshots
4. **Local execution with data sovereignty** -- structurally impossible for SaaS competitors

The first three create the analytical advantage. The fourth creates the structural moat.

**Features that capture this quadrant (in priority order)**:
1. Multi-source signal normalization (the technical foundation)
2. STEEPs classification applied to investment (the sole unique differentiator)
3. Weekly synthesis report in Korean (the primary output)
4. Signal evolution tracking (the compounding advantage)
5. Decision journal (the habit-forming mechanism)

### Question A3: How to position vs. AlphaSquare without a losing comparison?

**Never compare on the same dimensions.** The Cautious branch proved that head-to-head comparison loses on 11 of 17 dimensions. The correct positioning:

- AlphaSquare = **microscope** (detailed view of individual stocks, real-time, actionable)
- InvestScan = **telescope** (broad view of macro forces, weekly, directional)

The messaging frame: "InvestScan is not an alternative to AlphaSquare. It is a complement. AlphaSquare tells you WHAT to trade today. InvestScan tells you WHERE THE WORLD IS GOING and what that means for your portfolio over the next 3-12 months."

This sidesteps the losing comparison entirely. Nobody asks whether a telescope is better than a microscope.

---

## DISCUSSION B: USER PRIORITY

### Question B1: Edge Case (3 personas) vs. Mainstream (Kim Minsu) -- who defines the product?

**Verdict: Edge Case personas define Phase 1. Mainstream defines Phase 2+.**

The Cautious User analysis is devastating: 99% of Korean investors will never use a CLI tool. The installation funnel drops 80% of interested users. The realistic SOM is 500-2,000 users in Year 1-2.

But the Optimistic User Edge Case analysis identifies 3 power personas who ALL want the same 7 features:

| Persona | Description | Key Need |
|---------|-------------|----------|
| **Jeonup Investor (전업투자자)** | Full-time investor, 100M+ KRW portfolio | Macro intelligence depth, evidence chains |
| **Content Creator** | Investment blogger/YouTuber | Unique insights, data-backed narratives |
| **Systematic Investor (체계적 투자자)** | Developer-investor, process-oriented | Decision audit trail, methodology rigor |

All three want: (1) Macro cascade, (2) Global pipeline, (3) Signal evolution, (4) Evidence chains, (5) Devil's advocate, (6) Decision audit, (7) Local+open+free.

**Design for the edge case personas first.** If InvestScan is irreplaceable for 500 serious macro-thinkers, that is success. If it is "okay" for 5,000 casual users, that is failure.

### Question B2: What is the minimum feature set ALL edge case personas agree on?

Cross-referencing the 3 power personas' needs with the Green/Yellow/Red zone analysis:

**Unanimous minimum (must-have for all 3 personas)**:
1. One-command pipeline execution
2. Weekly Korean synthesis report with STEEPs breakdown
3. Multi-source signal normalization
4. Signal evidence trails (which sources, what confidence, why)
5. Decision journal for personal accountability

**Strongly desired (2/3 personas demand it)**:
6. Signal evolution tracking (Jeonup Investor + Systematic Investor)
7. HTML dashboard report (Content Creator + Jeonup Investor)

**Nice-to-have (1/3 personas wants it)**:
8. KRX market data integration (Systematic Investor)
9. Devil's advocate counter-analysis (Content Creator)

### Question B3: Layer strategy -- which layers are Phase 1 vs. Phase 2?

| Layer | Content | Phase | Rationale |
|-------|---------|-------|-----------|
| **Layer 0: Pipeline** | One-command execution, health check | Phase 1 (M1) | No product without this |
| **Layer 1: Report** | Weekly Korean synthesis + STEEPs | Phase 1 (M1-M2) | Primary value delivery |
| **Layer 2: Intelligence** | Signal normalization + evidence chains | Phase 1 (M1-M2) | Enables cross-source synthesis |
| **Layer 3: Temporal** | Signal evolution tracking | Phase 1 (M2-M3) | The compounding differentiator |
| **Layer 4: Accountability** | Decision journal | Phase 1 (M2-M3) | Habit formation mechanism |
| **Layer 5: Visualization** | HTML interactive report | Phase 1 Stretch | Lowers consumption barrier |
| **Layer 6: Validation** | KRX market data + signal-vs-market | Phase 2 | Requires 3+ months of data first |
| **Layer 7: Community** | Public reports, GitHub, GeekNews | Phase 2 | Requires working product first |
| **Layer 8: Web Dashboard** | Streamlit/local web UI | Phase 2+ | Only if 12+ weeks of usage validated |

---

## DISCUSSION C: TECH PRIORITY

### Question C1: What is buildable in 6 months given ~5,300 LOC budget?

The Tech Architect (Fast-Ship) estimated ~5,300 LOC on the ~59,000 LOC existing base. The Balanced Scenario PRD scoped this at ~3,200 LOC with 60-80 dev hours. The Aggressive PRD scoped ~4,850 LOC with 75-80 dev hours.

**Realistic assessment at 3-4 hours/week for 24 weeks = 72-96 dev hours**:

| Feature | LOC | Dev Hours | Verdict |
|---------|-----|-----------|---------|
| CLI + orchestrator + config | 400 | 10 | BUILD |
| Signal normalization + dedup | 800 | 20 | BUILD |
| STEEPs classifier (for GNC signals) | 400 | 8 | BUILD |
| Weekly report generator (Korean MD) | 500 | 12 | BUILD |
| Signal evolution tracker | 500 | 12 | BUILD |
| Decision journal | 400 | 8 | BUILD |
| HTML interactive report | 600 | 15 | STRETCH |
| KRX market data adapter | 350 | 8 | DEFER |
| Tests + infrastructure | 500 | 10 | BUILD |
| **TOTAL (without stretch)** | **~3,500** | **~80** | **FEASIBLE** |
| **TOTAL (with stretch)** | **~4,450** | **~103** | **TIGHT** |

**The 3,500 LOC core is buildable.** The HTML report is the decision point: include it only if M1-M2 ship on schedule.

### Question C2: What PROVES superiority (not just claims it)?

The Tech Scalable branch raised the critical insight: **accuracy is unvalidatable for 7+ months**. You cannot prove direction accuracy without historical data to backtest against. The compounding advantage (Month 24 = uncatchable) requires TIME that Month 1 does not have.

**What can be proven in Phase 1 (Months 1-6)**:

| Proof Point | Timeline | How Measured |
|-------------|----------|--------------|
| **Breadth**: 150+ sources in 14+ languages | M1 | Source count in report metadata |
| **Transparency**: Full evidence chain for every direction call | M1 | Report structure includes citations |
| **Uniqueness**: STEEPs applied to investment (no competitor does this) | M1 | Feature comparison with PRISM-INSIGHT, AlphaSquare |
| **Temporal depth**: Signal evolution across 12+ weeks | M3 | Evolution tracker showing STRENGTHENING/FADING patterns |
| **Early warning**: At least 1 signal detected 2+ weeks before mainstream | M3-M6 | Public record comparison |
| **Habit value**: User runs tool weekly for 12+ consecutive weeks | M6 | Usage log |

**What CANNOT be proven in Phase 1**:
- Direction accuracy (55%+ target requires 6+ months of market data comparison)
- That more signals = better decisions (behavioral research says otherwise)
- That STEEPs methodology produces investment alpha

**Honest conclusion**: Phase 1 proves CAPABILITY (breadth, depth, transparency, uniqueness). Phase 2 proves VALUE (accuracy, decision quality, alpha generation). Do not conflate the two.

### Question C3: Architecture -- Monolithic integration + what new modules?

**Architecture: Monolithic Sequential Pipeline with File-Based IPC** (all perspectives agreed).

```
investscan/
  __init__.py
  cli.py                    # Click-based CLI (300 LOC)
  config.py                 # YAML config loader (100 LOC)
  orchestrator.py            # Pipeline phases + checkpointing (300 LOC)
  schema.py                  # UnifiedSignal dataclass (150 LOC)
  normalize_signals.py       # Schema harmonization + dedup (500 LOC)
  steeps_classifier.py       # STEEPs for GNC signals (250 LOC)
  sector_mapper.py           # Signal -> Korean sectors (200 LOC)
  synthesize_investment.py   # Direction + conviction (300 LOC)
  evolution_tracker.py       # Cross-week signal matching (350 LOC)
  generate_report.py         # Korean Markdown report (400 LOC)
  generate_html_report.py    # HTML with Plotly (STRETCH) (500 LOC)
  journal.py                 # Decision journal (250 LOC)
  health_check.py            # System validation (150 LOC)
  utils.py                   # Shared utilities (150 LOC)
```

**New modules**: 7 core + 1 stretch + 3 infrastructure = 11 files total.
**Zero changes to upstream systems** (EnvironmentScan, GlobalNews-Crawling).

---

## DISCUSSION D: BUSINESS PRIORITY

### Question D1: "Category creator" vs. "AlphaSquare killer" -- which strategy?

**Verdict: CATEGORY CREATOR, unambiguously.**

The Aggressive Competitive Strategy document itself reaches this conclusion: "We are not building a better stock picker. We are building something that has never existed." The "AlphaSquare killer" framing requires winning on 11 dimensions where we score 0/10 (trading, mobile, real-time, community, gamification, etc.). This is suicide.

**Category creator strategy**:
1. Define a new category: "Macro Environmental Intelligence for Investment Direction"
2. Be the sole (and therefore best) product in that category
3. Let the category grow organically through content and methodology sharing
4. Never compare head-to-head with AlphaSquare on their dimensions

The Aggressive Business Strategist's "5% Domination" strategy is correct: dominate the quant-curious + macro-thinker segment (50K-100K people) so completely that InvestScan is the default answer to "what do you use for macro scanning?"

### Question D2: Decision Journal as THE critical feature -- agree or disagree?

**AGREE (4/4 perspectives).**

This is the rare unanimous verdict. The Conservative PRD was built around this insight: "The tool is not the lasting value. Your decision history is." The Aggressive PRD included it as Stretch B but pulled it into Phase 1. The Balanced PRD made it a core feature.

**Why the Decision Journal matters more than any analytical feature**:

1. **It is the habit engine.** Without the journal, InvestScan is a report you read. With the journal, it is a system you participate in. Reading is passive. Journaling is active. Active engagement creates habits.

2. **It creates irreplaceable data.** After 6 months, the user has 24+ decision entries with rationale, confidence levels, and outcomes. This personal investment history cannot be recreated elsewhere. It creates organic switching costs -- not through lock-in, but through accumulated value.

3. **It enables future validation.** The journal entries become the training data for Phase 2 backtesting. Without decisions recorded against signals, there is no way to measure whether InvestScan improved investment decision quality.

4. **It is trivially simple to build.** ~250-400 LOC. No ML. No complex engineering. Maximum value per line of code.

### Question D3: Sustainability -- personal tool first, community second?

**Verdict: Personal tool first. Community is a Phase 2 concern.**

The Conservative PRD makes the strongest case: "Build the habit first. Build the product later." If the developer-user does not run InvestScan every week for 12 consecutive weeks, no amount of community features will save the project.

**Phase 1 = Personal tool**:
- Build for one user (the developer)
- Validate the weekly habit loop: run -> read -> journal -> review
- Success criterion: "Would you miss InvestScan if it stopped working?"

**Phase 2 = Selective sharing** (only after 12+ weeks of personal use):
- Publish weekly reports on GitHub Pages / blog
- Post on GeekNews (PRISM-INSIGHT was featured here successfully)
- Open-source the repository
- Accept the 500-2,000 SOM ceiling gracefully

**Phase 3 = Community** (only after demonstrable analytical advantage):
- "InvestScan vs. AlphaSquare: Same Week, Different Insights" comparisons
- Radical transparency: monthly accuracy audits
- Community contributors for additional crawl adapters

---

## FINAL OUTPUT: Unified Feature Comparison Table

| # | Feature | Market PRD | User PRD | Tech PRD | Business PRD | Consensus |
|---|---------|-----------|----------|----------|-------------|-----------|
| 1 | **One-command execution** (`investscan run`) | Essential | Essential | Essential | Essential | **GREEN (4/4)** |
| 2 | **Weekly Korean synthesis report** | Essential | Essential | Essential | Essential | **GREEN (4/4)** |
| 3 | **Multi-source signal normalization** | Essential | Essential | Essential | Essential | **GREEN (4/4)** |
| 4 | **Decision Journal** | Important | Important | Easy build | **Critical** | **GREEN (4/4)** |
| 5 | **STEEPs classification** | Sole differentiator | Desired by 3/3 personas | Buildable (400 LOC) | Moat feature | **GREEN (4/4)** |
| 6 | **Signal evolution tracking** | Compounding advantage | Desired by 2/3 personas | Buildable (500 LOC) | Phase 1 if time | **YELLOW (3/4)** |
| 7 | **Evidence chain in reports** | Core value prop | Essential for trust | Implicit in normalization | Transparency weapon | **GREEN (4/4)** |
| 8 | **HTML interactive report** | Expands reach | Content Creator needs | 600 LOC stretch | Nice-to-have | **YELLOW (2.5/4)** |
| 9 | **KRX market data snapshot** | Validates signals | Systematic Investor wants | 350 LOC, API risk | Phase 2 | **RED (1.5/4)** |
| 10 | **Devil's advocate agent** | Differentiation | Content Creator wants | Complex, Phase 2 | Defer | **RED (1/4)** |
| 11 | **Web dashboard (Streamlit)** | Market expansion | Mainstream gateway | Scope creep | Phase 2+ only | **RED (1/4)** |
| 12 | **Backtesting engine** | Proves accuracy | Systematic Investor wants | Requires 6+ months data | Phase 2+ | **RED (0.5/4)** |
| 13 | **Mobile app** | Would expand TAM | Mainstream users need | Out of scope | Never (solo dev) | **RED (0/4)** |
| 14 | **Community/social features** | Network effects | Social proof | Out of scope | Phase 3+ | **RED (0/4)** |
| 15 | **Trading integration** | Would close action gap | Users want it | Impossible (solo dev) | Never | **RED (0/4)** |

### Zone Summary

**GREEN ZONE (Phase 1 Must-Build, 4/4 agree):**
1. One-command execution
2. Weekly Korean synthesis report
3. Multi-source signal normalization
4. Decision Journal
5. STEEPs classification
6. Evidence chains in reports

**YELLOW ZONE (Phase 1 if schedule permits, 3/4 agree):**
7. Signal evolution tracking
8. HTML interactive report

**RED ZONE (Phase 2+ or Never, <=2/4 agree):**
9-15. KRX data, Devil's advocate, web dashboard, backtesting, mobile, community, trading

---

## RESOLVED OUTPUTS

### 1. Resolved Positioning Statement

> **InvestScan is a local, open-source macro intelligence system that applies futures studies methodology (STEEPs) to investment direction -- scanning 150+ sources across 14 languages, showing complete evidence chains, tracking signal evolution over time, and running 100% on the user's machine at zero cost. It does not pick stocks; it reveals the forces reshaping markets and what they mean for Korean sector allocation.**

### 2. Resolved Feature Priority (Ranked)

| Priority | Feature | LOC | Phase |
|----------|---------|-----|-------|
| P0 | One-command pipeline execution | 400 | M1 |
| P0 | Multi-source signal normalization + dedup | 800 | M1 |
| P0 | STEEPs classification (for GNC signals) | 400 | M1 |
| P0 | Weekly Korean synthesis report with evidence chains | 500 | M1-M2 |
| P1 | Decision Journal (add/review/list) | 400 | M2 |
| P1 | Signal evolution tracking | 500 | M2-M3 |
| P2 | HTML interactive report | 600 | M3 (stretch) |
| P3 | KRX market data snapshot | 350 | Phase 2 |
| P3 | Devil's advocate analysis | -- | Phase 2 |
| P4 | Web dashboard | -- | Phase 2+ (trigger-based) |
| **TOTAL Phase 1** | | **~3,000-3,600** | **6 months** |

### 3. Resolved Definition of "Overwhelmingly Superior" (월등히 뛰어난)

**"Overwhelmingly superior" does NOT mean**:
- Better than AlphaSquare as a product (we lose on 11/17 dimensions)
- Better UX, faster insights, more users, or easier setup
- Producing higher investment returns
- Replacing any existing tool

**"Overwhelmingly superior" DOES mean**:
- **Category-defining capability**: The ONLY tool that applies futures studies environmental scanning (STEEPs + Three Horizons + signal evolution) to investment direction in the Korean market
- **Structural moat**: Capabilities that competitors CANNOT, WILL NOT, or DON'T KNOW HOW TO replicate because doing so would destroy their business model, expose their IP, or require a ground-up architectural rebuild
- **Transparency monopoly**: The only investment direction tool with complete evidence chains, public accuracy records, and fully auditable reasoning -- in a market where every competitor is a black box
- **Compounding advantage**: After 6+ months of accumulated signal evolution data, the temporal intelligence depth becomes uniquely valuable and cannot be retroactively created by competitors

**The one-sentence definition**: "InvestScan is overwhelmingly superior in the specific domain of macro-analytical investment direction intelligence -- not because it does what others do better, but because it does something no one else does at all."

### 4. Key Disagreements That the User Must Decide

#### Decision 1: Balanced vs. Aggressive Scope

| Option | LOC | Dev Hours | Risk | Differentiator Strength |
|--------|-----|-----------|------|------------------------|
| **Balanced** (Green + selective Yellow) | ~3,200 | 60-80 hrs | LOW | Medium -- STEEPs + report, no evolution tracking |
| **Aggressive** (Green + all Yellow + stretch) | ~4,850 | 75-100 hrs | MEDIUM-HIGH | HIGH -- full differentiator set in Phase 1 |

**Moderator recommendation**: Balanced with a conditional promotion. Start with Balanced scope. If M1 (pipeline + normalization + STEEPs + report) ships by Week 8, promote signal evolution tracking and Decision Journal into Phase 1. If M1 is late, hold at Balanced scope.

#### Decision 2: HTML Report -- Phase 1 Stretch or Phase 2?

- **For Phase 1**: Content Creator persona needs it. Expands report accessibility beyond CLI users. Plotly charts are impressive for GeekNews/community sharing.
- **For Phase 2**: 600 LOC and 2.5 weeks is significant for a solo dev. Markdown reports work fine for the personal tool phase. HTML adds engineering complexity (Jinja2 templates, Plotly configs, inline CSS/JS).

**Moderator recommendation**: Phase 2. The Markdown report is sufficient for the personal tool phase. HTML becomes important only when sharing publicly (Phase 2+).

#### Decision 3: Is 3-4 hrs/week realistic for 6 months?

The Conservative PRD raises the most uncomfortable question: "I am not sure I will use this tool every week. Let me find out with minimum investment."

- **If YES (3-4 hrs/week is firm)**: Balanced scope is the right choice. ~60-80 dev hours fits comfortably.
- **If UNCERTAIN**: Conservative scope (~30-40 hrs, 1,200-1,600 LOC) is the safer bet. It delivers a working pipeline + report + journal, validates the habit, and preserves 60-70% of the time budget as buffer.
- **If time is VARIABLE (some weeks 6 hrs, some weeks 0)**: Balanced with checkpointing. The orchestrator's `--resume` capability means you can work in bursts without losing progress.

**Moderator recommendation**: Start Balanced. The conditional promotion mechanism (M1 gate at Week 8) provides an automatic scope adjustment. If the habit does not form by Week 12, the Conservative scenario's wisdom applies: "If you would not miss InvestScan, stop building."

#### Decision 4: Open-Source Timing

- **Option A**: Open-source from Day 1 (Aggressive strategy -- "free as a weapon")
- **Option B**: Open-source after 12 weeks of personal validation (Balanced strategy)
- **Option C**: Keep private indefinitely, personal tool only (Conservative strategy)

**Moderator recommendation**: Option B. Open-sourcing before the tool works reliably risks the credibility destruction the Cautious branch warns about. Open-sourcing after 12 weeks of validated use means the first public impression is a working, battle-tested tool with 12+ weekly reports as evidence.

---

## Summary for PHASE 3

This Phase 2 analysis resolves the 8-branch cacophony into clear direction:

1. **Positioning**: Category creator, not AlphaSquare killer
2. **Target user**: Edge case power personas first (전업투자자, Content Creator, 체계적 투자자)
3. **Core features**: 6 Green Zone features (pipeline, normalization, STEEPs, report, evidence chains, decision journal)
4. **Differentiator**: STEEPs environmental scanning applied to investment -- the sole feature no competitor offers
5. **Scope**: Balanced (~3,200 LOC) with conditional promotion to Aggressive if M1 ships on time
6. **"월등히 뛰어난" definition**: Category-defining capability in macro-analytical investment direction, not general product superiority
7. **Critical success metric**: 12 consecutive weeks of weekly usage (run + read + journal)

Phase 3 should produce 3 scenario PRDs (Conservative, Balanced, Aggressive) with the resolved positioning, feature priority, and definition of superiority from this Phase 2 analysis baked in.

---

*The telescope does not need to be better than the microscope. It needs to be the best telescope in the room. There is only one other tool even attempting to be a telescope (PRISM-INSIGHT), and they do not have environmental scanning. Ship STEEPs first. Own the category definition. Let the user decide if the category matters.*
