# InvestScan: Long-Term Superiority Architecture

**Role**: Long-Term Superiority Tech Architect
**Core Question**: What makes InvestScan's advantage LASTING, not just initial?
**Date**: 2026-03-27

---

## 0. The Strategic Reality

AlphaSquare has 15 engineers, Series A funding (2B KRW from Korea Economic TV), 220K registered users, and a 4.6-star app rating. If InvestScan shows a good approach, what prevents AlphaSquare from copying it in 6 months?

**The honest answer**: Most features can be copied. The question is not "what features are unique" but "what structural properties make copying self-destructive for the copier?"

This document identifies five categories of advantage: (1) things AlphaSquare can copy trivially, (2) things they could copy but won't because it would hurt them, (3) things that require a ground-up rebuild they cannot justify, (4) things that compound over time and cannot be copied retroactively, and (5) the specific technical architecture that activates all four.

---

## 1. Copyability Analysis: Can vs. Cannot vs. Won't

### 1.1 What AlphaSquare CAN Copy (6-12 months)

These provide zero lasting advantage. Build them, but do not rely on them as differentiators.

| Feature | Copy Difficulty | Copy Time | Why Easy |
|---------|----------------|-----------|----------|
| Report format / template design | Trivial | 2 weeks | UI/UX design is visible and replicable |
| STEEPs category labels on signals | Easy | 1 month | Taxonomy is public knowledge (futures studies literature) |
| Sector heat map visualization | Easy | 2 weeks | Standard data visualization |
| Multi-timeframe signal grouping | Easy | 1 month | UI re-organization of existing data |
| Korean-language investment summary | Easy | 1 month | They already have Korean content |
| Basic AI-generated market narrative | Easy | 2 months | LLM API call with financial prompt |

**Lesson**: Do not confuse "features" with "advantages." Every visible feature is copyable. The advantage must be structural.

### 1.2 What AlphaSquare COULD Copy but WON'T (Business Model Incompatibility)

These are the most powerful advantages because they require the competitor to damage their own business to replicate them.

#### 1.2.1 Local Execution (Structural Barrier: Revenue Model Destruction)

**Why they cannot copy it**: AlphaSquare is a cloud SaaS platform. Their entire revenue model -- subscriptions (19,800-69,900 KRW/month), virtual currency (seeds), trading commissions (0.015%), B2B data licensing -- depends on users being connected to their servers. Moving to local execution would:

1. **Eliminate subscription justification**: If the software runs locally, what justifies monthly payments? Users would expect a one-time purchase.
2. **Destroy data licensing revenue**: Their B2B data sales depend on aggregated user behavior data. Local execution = no behavioral data collection.
3. **Break real-time features**: Their 340,000 simulations every 10 minutes for trading signals requires cloud compute. Moving this locally would require users to have high-end machines.
4. **Kill cross-device sync**: Their key UX advantage (web + mobile + tablet seamlessly) requires cloud state. Local execution breaks this entirely.
5. **Undermine the Chart Game**: The gamification/social features (friend battles, investment leagues, rankings) require a central server.

**Quantified impact**: AlphaSquare's 2024 revenue target was 1B KRW/year. Pivoting to local would eliminate approximately 70-80% of this revenue stream (subscriptions + data licensing + commission flow), leaving only one-time software sales in a market of 5,000-15,000 potential buyers.

**InvestScan architecture implication**: Every core analysis function MUST run without network connectivity. Network is used only for data collection (crawling), never for analysis or report generation. This is not just a privacy feature -- it is the structural moat.

#### 1.2.2 Open Workflow Transparency (Structural Barrier: IP Exposure)

**Why they cannot copy it**: AlphaSquare's value proposition rests on proprietary algorithms -- "AI prediction," "340K simulations," "43 trading strategies." Their competitive position depends on users NOT knowing how these work. Full transparency would:

1. **Commoditize their paid tier**: If users can see exactly how AI predictions are generated, the premium tier (69,900 KRW/month) loses its mystique. Users would replicate the logic in Python.
2. **Expose accuracy weaknesses**: AlphaSquare publishes NO accuracy metrics for their AI predictions. Transparency would require publishing these, potentially revealing that their predictions are mediocre.
3. **Enable competitor replication**: Their algorithms are their moat. Publishing them hands competitors the blueprints.

**InvestScan architecture implication**: Every analysis step must produce an auditable reasoning chain. The `generate_report.py` module must include: (a) which signals contributed to each direction call, (b) the confidence calculation breakdown, (c) which sources corroborated each other, (d) explicit counter-evidence that was considered. This transparency is the feature; the opacity is the competitor's structural constraint.

#### 1.2.3 User-Owned Data (Structural Barrier: Asset Model Contradiction)

**Why they cannot copy it**: For AlphaSquare, user data IS the product. They monetize it through:
- B2B data licensing (trading patterns, user behavior)
- AI model training (user interactions improve their predictions)
- Feature personalization (requires centralized user profiles)
- Regulatory compliance (KRX/FSS require centralized audit trails)

Giving users full data ownership would:
1. Remove the training data that improves their AI models
2. Eliminate B2B data licensing revenue
3. Require rebuilding their entire data pipeline for exportability
4. Create compliance complications (user-controlled data is harder to audit)

**InvestScan architecture implication**: All data must be stored in open, standard formats (JSON, Parquet, SQLite). No proprietary encoding. No data lock-in. The `output/` directory structure must be self-documenting -- any technically competent person should be able to read it without InvestScan installed.

### 1.3 What AlphaSquare CANNOT Copy (Architectural Impossibility)

These require a ground-up rebuild that contradicts their technical architecture.

#### 1.3.1 Environmental Scanning Depth (116 Sites + arXiv + STEEPs)

**Why it is structurally uncopyable**:

AlphaSquare processes financial data: stock prices, financial statements, news headlines about specific companies. Their data pipeline is optimized for this.

InvestScan processes *civilization-level change vectors*: arXiv research papers, government policy documents, patent filings, multi-language global news across 116 sites in 14+ languages, social trend signals, environmental regulation changes. This requires:

1. **Entirely different crawling infrastructure**: 116-site multi-language crawling with anti-bot evasion (Playwright automation, rate limiting, adaptive scraping strategies). AlphaSquare crawls financial data APIs, not the open web.
2. **Different NLP pipeline**: SBERT for multilingual semantic similarity, BERTopic for topic modeling, Prophet for time-series trend detection, PCMCI for causal inference. AlphaSquare's NLP is financial-text focused.
3. **Different classification framework**: STEEPs (Social, Technological, Economic, Environmental, Political, Security) is a futures studies framework, not a financial analytics framework. Implementing it requires domain expertise in strategic foresight, not quantitative finance.
4. **Different data volume**: 116 sites producing thousands of articles daily in 14 languages, plus arXiv papers, plus Naver News. This is 10-100x the data volume of financial news feeds.

**Estimated effort for AlphaSquare to replicate**: 6-12 months of dedicated engineering (3-5 engineers), plus hiring a futures studies domain expert. With 15 total employees and a burn rate that demands revenue growth, this investment is extremely unlikely.

**InvestScan architecture implication**: The environmental scanning depth is not a feature -- it is the foundation. The two upstream systems (EnvironmentScan ~23,400 LOC + GlobalNews-Crawling ~25,400 LOC) represent ~48,800 lines of production-tested code. This is the inheritance that makes InvestScan possible and competitors cannot retroactively acquire.

#### 1.3.2 Cross-Domain Signal Synthesis (STEEP+G to Investment Direction)

**Why it is structurally uncopyable**:

No existing investment app maps multi-domain environmental forces to investment directions. This is not because the idea is novel -- it is because the pipeline is uniquely complex:

1. It requires signals from DIFFERENT domains (social trends, technology shifts, economic indicators, environmental regulation, political events) to be classified on the same framework.
2. It requires a synthesis layer that can say "Aging population (Social) + AI healthcare innovation (Technological) + Medicare expansion (Political) = Healthcare sector bullish, 6-12 month horizon."
3. It requires temporal classification: distinguishing a 2-week news cycle from a 5-year structural shift.

Financial apps analyze within a single domain (financial data). Environmental scanning apps scan across domains but do not produce investment directions. InvestScan is in the empty quadrant: cross-domain scanning + investment direction synthesis.

**InvestScan architecture implication**: The `synthesize_investment.py` module is the crown jewel. Its logic -- mapping STEEPs signals + 5-Layer temporal classifications to KOSPI/KOSDAQ sector directions -- is the intellectual property that cannot be reproduced by copying visible features.

### 1.4 What Cannot Be Copied RETROACTIVELY (Time-Dependent Compounding)

This is the most important category. Even if a competitor started building the exact same system today, they cannot catch up on accumulated data.

#### 1.4.1 Signal Evolution Database

Every week InvestScan runs, it records which signals appeared, strengthened, weakened, converged, or disappeared. After 6 months, this database contains:

- ~600-1,200 unique signals with temporal trajectories
- Cross-source corroboration patterns (which signal combinations tend to co-occur)
- Signal-to-market-outcome correlations (did "semiconductor bullish" signals precede actual KOSPI IT sector gains?)
- False positive patterns (which signal types consistently fail to predict)

**Why this is uncopyable retroactively**: AlphaSquare cannot build this database by starting today. The signals from January 2026, March 2026, June 2026 are gone -- the web pages have changed, the news cycles have moved on, the arXiv papers have been superseded. Historical environmental scanning data does not exist in any purchasable dataset.

**Compounding formula**:
- Month 1: Raw signals, no history, no validation
- Month 6: 6 months of signal trajectories, early pattern detection
- Month 12: Seasonal patterns visible, false positive filtering, signal combination scoring
- Month 24: Two full years of cross-domain signal evolution, statistically significant accuracy metrics, personalized to the user's market focus

**InvestScan architecture implication**: Signal persistence must be a first-class concern from day 1. Every signal must be stored with: (a) first detection date, (b) weekly status updates (NEW/RECURRING/STRENGTHENING/WEAKENING/FADING), (c) linked investment direction calls, (d) eventual market outcome. The `evolution_tracker.py` module (conditional in the Balanced PRD) should be elevated to P0 for the long-term superiority strategy.

#### 1.4.2 Decision Journal (Personal Investment Reasoning Corpus)

Each time the user acts on InvestScan's report, the decision journal records:
- Which signals informed the decision
- The user's reasoning (in their own words)
- The confidence level at decision time
- The outcome check date
- The actual outcome

After 12 months, this creates a personal corpus that answers: "What kinds of environmental signals do I consistently misinterpret?" and "Which STEEPs dimensions am I best at translating into investment decisions?"

**Why this is uncopyable**: This is personal data generated by the interaction between the system's signals and the user's judgment. No competitor can replicate another user's decision history. It is the user's own intellectual property, stored on their own machine.

**Compounding formula**:
- Month 3: First 10-20 decisions logged, too few for patterns
- Month 6: 30-50 decisions, first patterns emerging (e.g., "I am 70% accurate on T_Technological signals but only 40% on P_Political")
- Month 12: 80-120 decisions, statistically meaningful accuracy rates per STEEPs dimension, personal blind spots identified
- Month 24: 200+ decisions, a comprehensive personal investment reasoning corpus that no AI tool can replicate because it reflects this specific user's judgment evolution

**InvestScan architecture implication**: The decision journal must be dead-simple to use (append-only YAML) but richly queryable (SQLite index on top). Monthly and quarterly review scripts should auto-generate accuracy reports by STEEPs dimension, time horizon, and confidence level.

#### 1.4.3 Signal Accuracy Calibration Database

Over time, InvestScan can measure:
- Which STEEPs dimensions produce the most accurate investment directions for the Korean market
- Which time horizons (1m, 3m, 6m, 1y) the system is most accurate at
- Which source combinations (EnvScan only, GlobalNews only, both converging) produce the highest accuracy
- Seasonal accuracy patterns (does the system perform better in Q1 vs Q3?)

**Why this matters for superiority**: After 12 months, InvestScan can say: "Our Technology + Economic convergence signals have a 73% accuracy rate for 3-month semiconductor sector direction, based on 47 historical instances." No competitor can make this claim without the same 12 months of data.

**InvestScan architecture implication**: The `signal_accuracy.sqlite` database must be designed from the start with outcome tracking fields. Even before automated backtesting exists, manual outcome annotation builds the foundation.

---

## 2. Architecture Principles for Lasting Superiority

### Principle 1: Data Moat by Default

Every pipeline run accumulates data that makes future runs more valuable. This is not optional -- it is baked into the architecture.

```
investscan/
  data/
    signals/
      raw/                          # Every signal ever detected (append-only)
        2026-03-27.jsonl
        2026-04-03.jsonl
        ...
      evolution/                    # Signal trajectory tracking
        evolution-index.sqlite      # Signal lifecycle: NEW -> RECURRING -> FADING
        cross-source-links.sqlite   # Which signals appeared in both systems
      accuracy/                     # Outcome tracking
        signal-outcomes.sqlite      # Signal -> market outcome correlation
        accuracy-by-steeps.json     # Aggregated accuracy per STEEPs dimension
        accuracy-by-horizon.json    # Aggregated accuracy per time horizon
    decisions/                      # Personal decision journal
      journal.yaml                  # Append-only decision log
      reviews/                      # Quarterly review reports
        2026-Q1-review.md
        2026-Q2-review.md
    calibration/                    # System self-improvement data
      threshold-history.yaml        # How scoring thresholds evolved over time
      false-positive-log.jsonl      # Signals that were wrong -- learning material
      source-reliability.json       # Per-source accuracy rates over trailing 90 days
```

**Key design constraint**: All data files are append-only or versioned. Never overwrite historical data. The history IS the moat.

### Principle 2: Customization Moat Through Configuration Evolution

Each user's `config/` directory becomes unique over time:

```yaml
# config/thresholds.yaml -- evolves with usage
# Initial (generic)
conviction:
  high_threshold: 0.75
  multi_source_bonus: 0.15
  min_signals_for_direction: 3

# After 6 months (calibrated to this user's market and judgment)
conviction:
  high_threshold: 0.68          # Lowered because user found 0.75 too conservative
  multi_source_bonus: 0.20      # Increased because cross-source convergence proved very reliable
  min_signals_for_direction: 2  # Lowered because 2-signal convergence was sufficient for this user

# config/sectors.yaml -- evolves with market knowledge
sectors:
  semiconductor:
    keywords_v1: ["반도체", "semiconductor", "chip", "AI 칩"]          # Initial
    keywords_v6: ["반도체", "semiconductor", "chip", "AI 칩", "HBM",  # After 6 months
                   "TSMC", "파운드리", "패키징", "CoWoS", "GAA",
                   "NAND", "DRAM", "EUV", "삼성전자 DS", "SK하이닉스"]
    weight_adjustment: 1.15     # User learned Korean semiconductor signals deserve higher weight
```

**Why this is uncopyable**: AlphaSquare gives every user the same algorithm. InvestScan gives each user a system that has been tuned to their specific judgment patterns, market focus, and accuracy history. After 12 months, two InvestScan users running the same upstream data will produce different reports because their configs have diverged based on their individual usage patterns.

**InvestScan architecture implication**: The `config/` directory must be git-tracked separately from code. Users can version their configs, revert changes, and see how their thresholds evolved. The self-improvement engine (EnvironmentScan's proven pattern) can suggest threshold adjustments, but the user always approves.

### Principle 3: Methodology Moat Through STEEPs Expertise Deepening

The STEEPs framework is not a static taxonomy -- it deepens with use:

**Month 1**: STEEPs is a keyword-based classifier (70-80% accuracy)
- "semiconductor" -> T_Technological
- "oil price" -> E_Economic
- "aging population" -> S_Social

**Month 6**: STEEPs classifier learns from the signal evolution database
- Signals that were initially classified as T_Technological but correlated with E_Economic outcomes get reclassified
- New sub-categories emerge: T_AI, T_Biotech, T_Energy (more specific than generic T_Technological)
- Cross-dimension patterns detected: "T_AI + E_Economic convergence precedes semiconductor sector moves"

**Month 12**: STEEPs becomes a predictive framework
- Historical data reveals which STEEPs dimension combinations are most predictive for which sectors
- Seasonal patterns: P_Political signals spike before elections and trade negotiations, creating predictable investment windows
- "Meta-signals": when 3+ STEEPs dimensions converge on the same sector, accuracy jumps from ~55% to ~75%

**Month 24**: STEEPs expertise is deep enough to publish
- The accumulated data can support academic-quality analysis: "Cross-Domain Environmental Signal Convergence as a Predictor of Korean Market Sector Rotation: A 24-Month Empirical Study"
- This published methodology becomes a thought leadership moat -- InvestScan is not just a tool but the reference implementation of a validated approach

**InvestScan architecture implication**: The STEEPs classifier must be designed for evolution. Version 1 is keyword-based. Version 2 (month 4+) adds feedback from the accuracy database. Version 3 (month 8+) uses embedding-based classification trained on the accumulated signal corpus. The interface stays the same; the internals improve.

### Principle 4: Integration Moat Through Upstream System Maturity

InvestScan inherits 48,800+ lines of production-tested code from two upstream systems:

| System | LOC | What It Provides | Replication Cost |
|--------|-----|-----------------|-----------------|
| EnvironmentScan v4 | ~23,400 | STEEPs classification, pSST scoring, signal evolution, arXiv scanning, policy document analysis, Naver News scanning, multi-global news scanning | 6-9 months for a team of 3 |
| GlobalNews-Crawling | ~25,400 | 116-site multi-language crawling, 8-stage NLP pipeline, 56 quantitative techniques, SBERT embeddings, BERTopic topic modeling, Prophet time series, PCMCI causal inference | 9-12 months for a team of 3-4 |
| **Combined** | **~48,800** | **Complete environmental scanning + global news intelligence pipeline** | **12-18 months, 6+ engineers, $500K+** |

**Why this is a moat**: AlphaSquare would need to build or acquire equivalent functionality. They cannot buy it (no vendor sells a combined environmental scanning + multi-language news intelligence pipeline). They would need to build it from scratch, which means 12-18 months and 6+ engineers -- half their team, diverted from revenue-generating features.

**InvestScan architecture implication**: Treat upstream systems as stable dependencies. Do not fork them. Do not modify them. Read their outputs via file-based IPC. This zero-coupling approach means upstream systems can evolve independently, and InvestScan benefits from their improvements without integration work.

---

## 3. The Compounding Advantage Design

### 3.1 The Superiority Curve

```
Superiority
  |
  |                                              * Year 2: Uncatchable
  |                                           *    - 2 years of signal evolution data
  |                                        *       - Validated accuracy metrics
  |                                     *          - Deep STEEPs expertise
  |                                  *             - Personal decision corpus
  |                               *                - Publishable methodology
  |                            *
  |                         * Year 1: Clearly Better
  |                      *     - 12 months of signal tracking
  |                   *        - Calibrated thresholds
  |                *           - First accuracy measurements
  |             *              - Cross-domain patterns visible
  |          *
  |       * Month 6: Promising
  |     *    - 6 months of raw signal data
  |   *      - Initial evolution tracking
  |  *       - User's config customized
  | * Month 1: Baseline
  |*   - Generic thresholds
  +---------------------------------------------------> Time
```

### 3.2 What Makes Each Phase Increasingly Superior

**Month 1 Output (Baseline)**:
- Generic STEEPs classification, rule-based sector mapping
- Reports are useful but not dramatically better than reading both upstream systems' outputs manually
- Value: convenience (one command, one report) + STEEPs lens (unique framing)
- Superiority over AlphaSquare: Limited to "environmental scanning exists" and "local execution"

**Month 6 Output (Promising)**:
- 6 months of signal evolution data enables trajectory tracking
- User's thresholds calibrated to their judgment
- Cross-source convergence patterns emerging (which EnvScan + GlobalNews overlaps matter)
- First manual accuracy checks establish baseline
- Superiority over AlphaSquare: Signal trajectory tracking (they have nothing equivalent), personalized thresholds, partial accuracy validation

**Month 12 Output (Clearly Better)**:
- 12 months of signal-to-market outcome data
- STEEPs classifier v2 with feedback-trained accuracy
- Seasonal patterns detected (quarterly political cycle, annual budget effects)
- Decision journal with 80-120 entries revealing personal judgment patterns
- Source reliability scores (which of the 116 GlobalNews sites are most predictive?)
- Superiority over AlphaSquare: Demonstrated accuracy metrics (they still publish none), personal decision analytics, deep STEEPs expertise, a year of compounded data they cannot retroactively acquire

**Month 24 Output (Uncatchable)**:
- 2 full years of cross-domain signal evolution
- STEEPs classifier v3 with embedding-based classification
- Publishable methodology with empirical backing
- Decision journal with 200+ entries: personal investment reasoning corpus
- Accuracy by STEEPs dimension, time horizon, sector, source -- all statistically significant
- The system has essentially become a personalized, validated, transparent environmental scanning-to-investment pipeline that no cloud app can replicate
- Superiority over AlphaSquare: Structural, demonstrated, personal, validated, transparent -- on every dimension that matters for investment quality

### 3.3 The Self-Reinforcing Feedback Loop

```
    +---> Better Signals ---> Better Decisions ---> Better Outcomes
    |                                                      |
    |                                                      v
    +--- Calibrated Thresholds <--- Outcome Tracking <---+
    |                                                      |
    |                                                      v
    +--- Improved STEEPs Classifier <--- Accuracy Data <--+
    |                                                      |
    |                                                      v
    +--- Source Reliability Scores <--- False Positive Log +
```

Each cycle through this loop:
1. Improves the signal-to-noise ratio (better signals)
2. Calibrates the user's decision-making (better decisions)
3. Validates the methodology (provable outcomes)
4. Tightens the scoring thresholds (fewer false positives)
5. Sharpens the STEEPs classifier (more precise classification)

AlphaSquare has no equivalent feedback loop because they have no accuracy tracking, no outcome correlation, and no transparent methodology to improve.

---

## 4. Feature Roadmap for Sustained Superiority

### Phase 1: Foundation + First Superiority Proof Points (Months 1-6)

**Goal**: Ship a working pipeline that produces useful weekly reports AND begins accumulating the data that creates long-term advantage.

| Feature | Month | Purpose for Superiority | Priority |
|---------|-------|------------------------|----------|
| One-command execution (`investscan run`) | M1 | Table stakes | P0 |
| Signal normalization (EnvScan + GlobalNews) | M1 | Foundation for cross-source analysis | P0 |
| STEEPs classification for all signals | M1 | **Primary differentiator** -- no competitor has this | P0 |
| Weekly Korean markdown report | M1 | The visible product | P0 |
| **Signal persistence database** (append-only) | M1 | **Compounding data moat starts here** | P0 |
| Cross-source convergence detection | M2 | Higher confidence when both systems agree | P1 |
| **Signal evolution tracker** (NEW/RECURRING/FADING) | M2 | **Time-dependent moat begins accumulating** | P0-elevated |
| Sector mapper (KOSPI/KOSDAQ) | M2 | Korean market-specific value | P1 |
| Confidence scoring with pSST + GlobalNews fusion | M3 | More calibrated direction calls | P1 |
| **Decision journal** (append-only YAML + SQLite index) | M3 | **Personal reasoning corpus starts** | P1-elevated |
| Graceful degradation (single-source fallback) | M3 | Pipeline reliability | P1 |
| `investscan health` diagnostic | M4 | Maintenance burden reduction | P1 |
| **Outcome annotation CLI** (`investscan annotate`) | M4 | **Accuracy tracking begins** | P1 |
| Scheduled execution (launchd) | M5 | Automation (reduces abandonment risk) | P1 |
| **First quarterly accuracy review** | M6 | **First proof of superiority: real accuracy data** | P0 |

**Phase 1 Superiority Milestone**: By month 6, InvestScan should be able to state: "We have 6 months of environmental signal tracking across X STEEPs dimensions. We detected Y signals, Z% of which were confirmed by both upstream systems. Our directional calls had W% accuracy against actual KOSPI sector performance." No competitor, including AlphaSquare, can make any equivalent statement.

### Phase 2: Accumulated Data Advantage Becomes Visible (Months 7-12)

**Goal**: The data accumulated in Phase 1 begins producing measurably better outputs. The gap widens.

| Feature | Month | Purpose for Superiority | Priority |
|---------|-------|------------------------|----------|
| STEEPs classifier v2 (feedback-trained) | M7 | **Methodology deepens**: classifier improves based on accuracy data | P1 |
| Signal combination scoring | M7 | Which multi-STEEPs patterns predict best? | P1 |
| **Source reliability scoring** | M8 | **Data moat deepens**: which of 116 sources are most predictive? | P1 |
| Threshold auto-suggestion (self-improvement engine) | M8 | Config evolves based on accumulated accuracy data | P2 |
| Seasonal pattern detection | M9 | "Q1 Political signals historically precede Q2 market moves" | P2 |
| **Decision journal quarterly analytics** | M9 | **Personal moat deepens**: accuracy by STEEPs dimension, personal blind spots | P1 |
| False positive analysis | M10 | Which signal types consistently mislead? Filter them. | P1 |
| Cross-domain convergence scoring | M10 | Quantify: how much does multi-STEEPs agreement increase accuracy? | P1 |
| **Semi-automated backtesting** | M11 | Compare past signals against actual KOSPI sector performance (automated) | P1 |
| **12-month accuracy report** | M12 | **Major proof point**: publish accuracy metrics by dimension, horizon, sector | P0 |

**Phase 2 Superiority Milestone**: By month 12, InvestScan can publish: "12-month empirical accuracy: Technology signals 68% accurate at 3-month horizon, Economic + Political convergence 74% accurate for sector rotation, Social signals 52% (below threshold, requires methodology revision)." This is radical transparency that no competitor will match.

### Phase 3: Uncatchable Lead in Methodology + Data + Customization (Months 13-24)

**Goal**: The accumulated advantages become insurmountable. Even a well-funded competitor starting from scratch cannot catch up in less than 18 months.

| Feature | Month | Purpose for Superiority | Priority |
|---------|-------|------------------------|----------|
| STEEPs classifier v3 (embedding-based, trained on local corpus) | M13-14 | **Methodology moat**: classifier trained on 12 months of InvestScan-specific data | P1 |
| Predictive signal scoring | M15 | Not just "signal exists" but "this signal pattern historically precedes sector moves" | P1 |
| **Investment thesis builder** | M16 | Structured hypothesis management with evidence accumulation | P2 |
| Cross-year comparative analysis | M17 | "March 2027 signal landscape vs March 2026: what changed?" | P2 |
| **Publishable methodology paper** | M18 | **Thought leadership moat**: publish "STEEPs as Investment Direction Predictor" | P2 |
| Portfolio alignment scoring | M19 | "How well does your portfolio align with current high-conviction signals?" | P2 |
| Multi-user comparative calibration (opt-in) | M20 | If multiple users adopt, compare anonymized accuracy data | P3 |
| Scenario generation with probability estimates | M21 | "Based on current STEEPs convergence, 3 possible scenarios for Q3..." | P2 |
| **24-month comprehensive accuracy audit** | M24 | **Definitive proof**: 2-year empirical validation of methodology | P0 |

**Phase 3 Superiority Milestone**: By month 24, InvestScan represents:
- 2 years of irreproducible signal evolution data
- An empirically validated methodology with published accuracy metrics
- A personal decision corpus that no AI can replicate
- Configuration that reflects 24 months of calibration to one user's judgment
- A thought leadership position in "futures studies for investment"

---

## 5. Technical Validation Strategy: PROVE Superiority, Don't Just Claim It

### 5.1 Why Validation Is the Ultimate Moat

AlphaSquare publishes zero accuracy metrics for their AI predictions. Thinkpool/Rassi self-reports "75% hit rate" with no independent verification. No Korean investment AI app provides transparent, auditable accuracy tracking.

**This is the single biggest trust gap in the market** (identified in the competitive landscape map, Gap 3).

InvestScan's validation strategy converts this gap into an insurmountable advantage: by publicly tracking accuracy (including failures), InvestScan builds trust that black-box competitors structurally cannot match.

### 5.2 Signal Accuracy Tracking System

```python
# investscan/accuracy_tracker.py

@dataclass
class SignalOutcome:
    signal_id: str
    direction_call: str           # "bullish" | "bearish" | "neutral"
    sector: str                   # KOSPI sector
    time_horizon: str             # "1m" | "3m" | "6m" | "1y"
    call_date: datetime
    check_date: datetime

    # Outcome (filled in at check_date)
    actual_sector_return: float | None   # Actual sector index return
    direction_correct: bool | None       # Did our call match reality?
    magnitude_accuracy: float | None     # How close was our conviction to actual magnitude?

    # Context
    steeps_dimensions: list[str]         # Which STEEPs categories contributed
    source_count: int                    # How many sources corroborated
    conviction_at_call: float            # Our confidence when the call was made

    # Meta
    annotation_method: str               # "auto" | "manual"
    notes: str                           # User's notes on why this was right/wrong
```

### 5.3 Three-Tier Validation Approach

**Tier 1: Automated Market Outcome Comparison (Monthly)**

```
For each investment direction call made 1 month ago:
  1. Fetch actual KOSPI sector index performance for the period
  2. Compare direction (bullish/bearish/neutral) with actual return sign
  3. Score: Direction correct = +1, Wrong = 0, Magnitude within 50% = bonus
  4. Aggregate by: STEEPs dimension, sector, time horizon, source count
```

Implementation: A `investscan annotate --auto --lookback 30d` command that:
- Reads past direction calls from `output/*/synthesis.json`
- Fetches KOSPI sector index data (KRX API or manual CSV)
- Computes accuracy metrics
- Appends to `data/accuracy/signal-outcomes.sqlite`

Estimated LOC: ~400 (including KRX data fetcher + comparison logic)

**Tier 2: Manual Decision Outcome Review (Quarterly)**

The user reviews their decision journal and annotates outcomes:

```bash
investscan review --quarter 2026-Q1

# Displays each decision with its signal context and asks:
# "Decision: Increased semiconductor ETF 5% based on IS-20260127-003"
# "Signal: T_Technological convergence, conviction 0.72"
# "Actual outcome (3-month check): semiconductor index +8.3%"
# "Was this a good decision? [yes/no/partial]: "
```

This builds the personal decision corpus and creates the data for the self-reinforcing feedback loop.

Estimated LOC: ~250 (CLI review tool + journal query + annotation)

**Tier 3: Public Accuracy Dashboard (Month 12+)**

After 12 months of data, generate a public accuracy report:

```markdown
# InvestScan 12-Month Accuracy Report
## Period: March 2026 - March 2027

### Overall Accuracy
- Direction calls: 347 total
- Correct direction: 62.2% (216/347)
- Correct within 1 month: 58.1%
- Correct within 3 months: 66.4%
- Correct within 6 months: 71.3%

### Accuracy by STEEPs Dimension
| Dimension | Calls | Accuracy | Best Sector |
|-----------|-------|----------|-------------|
| T (Technological) | 128 | 68.0% | Semiconductor |
| E (Economic) | 89 | 64.0% | Banking |
| P (Political) | 47 | 57.4% | Defense |
| S (Social) | 42 | 54.8% | Healthcare |
| E (Environmental) | 28 | 60.7% | Energy |
| s (Security) | 13 | 46.2% | Cybersecurity |

### Accuracy by Conviction Level
| Conviction | Calls | Accuracy | Interpretation |
|------------|-------|----------|----------------|
| High (>0.75) | 52 | 73.1% | Well-calibrated |
| Medium (0.5-0.75) | 168 | 63.1% | Slightly overconfident |
| Low (<0.5) | 127 | 52.0% | Noise territory |

### Honest Failures
- [List of the most notable wrong calls, with analysis of why]
- "IS-20260615-012: Called bearish on auto sector due to US tariff signals.
   Actual: Auto sector +12% as tariffs were negotiated away.
   Lesson: Political signals with diplomatic counter-evidence should be weighted lower."
```

**Why this is the ultimate superiority move**: AlphaSquare will never publish this. They cannot afford to show their failures. InvestScan can, because transparency IS the value proposition. Every published failure analysis increases trust (counterintuitively) and demonstrates the kind of intellectual honesty that black-box AI apps structurally cannot match.

### 5.4 Decision Outcome Correlation

The most powerful validation is not "were signals accurate?" but "did acting on signals produce better outcomes than not acting?"

After 12 months with a decision journal, compute:

```
Decisions informed by InvestScan signals: N
  - Average return: X%
  - vs. KOSPI benchmark: +/- Y%

Decisions NOT informed by InvestScan signals: M
  - Average return: A%
  - vs. KOSPI benchmark: +/- B%

Difference: (X - A)% = InvestScan's marginal contribution
```

This is the definitive superiority metric. If InvestScan-informed decisions consistently outperform non-InvestScan decisions by even 2-3% annually, the system has demonstrated concrete investment value.

---

## 6. Why Each Advantage Is Structural and Uncopyable: Summary Matrix

| Advantage | Type | Copy Time | Copy Cost | Self-Destructive to Copy? | Compounds Over Time? |
|-----------|------|-----------|-----------|--------------------------|---------------------|
| Local execution | Business model incompatibility | N/A | N/A | YES: kills SaaS revenue | No |
| Open workflow transparency | Business model incompatibility | N/A | N/A | YES: exposes IP, commoditizes premium tier | No |
| User-owned data | Business model incompatibility | N/A | N/A | YES: destroys data licensing revenue | No |
| 116-site crawling + arXiv + STEEPs | Architectural impossibility | 12-18 months | $500K+ | No, but prohibitively expensive | Slightly (source reliability improves) |
| Cross-domain signal synthesis | Architectural impossibility | 6-12 months | $200K+ | No, but requires futures studies expertise | Yes (methodology deepens) |
| Signal evolution database | Time-dependent accumulation | Cannot be copied retroactively | Infinite | N/A -- time cannot be purchased | YES: every week adds value |
| Decision journal | Time-dependent accumulation | Cannot be copied (personal data) | N/A | N/A -- unique to each user | YES: personal corpus grows |
| Accuracy calibration database | Time-dependent accumulation | Cannot be copied retroactively | Infinite | N/A -- past signals are gone | YES: statistical significance increases |
| Customized config/thresholds | Time-dependent personalization | Cannot be copied (unique to user) | N/A | N/A | YES: calibration improves |
| Published accuracy metrics | Trust through transparency | Could be copied in theory | Low | YES for black-box competitors | YES: longer track record = more trust |

---

## 7. Architectural Decisions That Activate Long-Term Superiority

### 7.1 Decision: Signal Persistence as P0 Requirement

**From the Balanced PRD**: Signal evolution tracking was listed as "Conditional Feature A" with a trigger: "User manually tracks signal evolution for 4+ consecutive weeks."

**Superiority override**: Elevate to P0. Signal persistence is not a feature -- it is the foundation of every compounding advantage. Without it, the signal evolution database never starts accumulating, the accuracy calibration database has no historical data, and the customization moat has no feedback loop.

**Implementation change**: Add `data/signals/raw/{date}.jsonl` append-only storage from day 1 of the pipeline. Every normalized signal is persisted, even before evolution tracking logic exists. The data accumulation begins at first run.

### 7.2 Decision: Decision Journal in M1, Not M3

**From the Balanced PRD**: Decision journal was listed as "Conditional Feature B" with a trigger: "User makes 3+ investment decisions citing report signals within first 2 months."

**Superiority override**: Include a minimal journal template in M1 reports. The report already has the section:

```markdown
## 결정 기록 (Decision Journal)
- 이 시그널을 보고 내가 한 결정:
- 왜 그렇게 결정했는가:
- 다음 주 확인할 것:
```

This costs zero additional code -- it is a report template section. The user fills it in manually. The structured journal CLI (`investscan journal add`) can wait until M3, but the habit starts in M1.

### 7.3 Decision: Outcome Annotation Infrastructure in M4, Not Phase 2

**From the Long-Term Architecture**: Outcome tracking was Phase 3 / P2.

**Superiority override**: `investscan annotate --auto` requires only a KOSPI sector index data source and comparison logic (~400 LOC). This should be M4 priority so that by M6, the first quarterly accuracy report exists. Without this, the Phase 1 superiority milestone ("we can state our accuracy") is unachievable.

### 7.4 Decision: Never Delete Signal Data

**Architectural constraint**: No InvestScan operation may delete or overwrite data in `data/signals/`, `data/decisions/`, or `data/accuracy/`. These directories are append-only by design. Even if a signal is later determined to be a false positive, the original detection record remains -- annotated, not deleted.

**Rationale**: Every piece of historical data contributes to the compounding advantage. Deleting a false positive removes the learning signal that prevents future false positives.

### 7.5 Decision: Accuracy Metrics in Every Report from M6

**Architectural constraint**: From month 6 onward, every weekly report must include a "System Accuracy" section:

```markdown
## 시스템 정확도 (System Accuracy)
- 지난 4주 방향 적중률: 63.2% (12/19 calls)
- STEEPs별 최고 정확도: T_Technological 71.4%
- STEEPs별 최저 정확도: P_Political 42.9%
- 이번 주 교차검증 시그널: 5건 (두 시스템 모두 포착)
```

**Rationale**: This is the visible proof of superiority that no competitor will include (because they do not track accuracy). It is also a forcing function: if accuracy is poor, the user sees it immediately and the system must improve.

---

## 8. The Honest Bottom Line

### What InvestScan Is

InvestScan is a local, automated, transparent investment direction scanning system that:
1. Runs entirely on one MacBook with zero cloud dependency for analysis
2. Scans 116+ sources across 14 languages through two production-tested upstream systems
3. Classifies signals on a cross-domain STEEPs framework that no competitor uses
4. Accumulates signal evolution data that cannot be retroactively replicated
5. Tracks its own accuracy with radical transparency, including publishing failures
6. Creates a personal decision reasoning corpus unique to each user
7. Deepens its methodology through a self-reinforcing feedback loop

### What InvestScan Is NOT

InvestScan is not:
- A mass-market app (target: 5,000-15,000 technically capable Korean investors)
- A real-time trading tool (weekly/daily batch, not second-by-second)
- A stock picker (direction and sector level, not individual tickers)
- A replacement for professional judgment (it informs decisions, not makes them)
- A SaaS product (local, local, local)

### Why AlphaSquare Cannot Catch Up

Even if AlphaSquare's CEO reads this document tomorrow and decides to replicate every feature:

1. **They cannot go local** without destroying 70-80% of their revenue.
2. **They cannot be transparent** without exposing that their AI predictions lack accuracy metrics.
3. **They cannot build 48,800 LOC of environmental scanning infrastructure** with 15 employees while maintaining their existing product.
4. **They cannot retroactively create** the signal evolution database that InvestScan accumulates from day 1.
5. **They cannot replicate** any individual user's decision journal, customized configuration, or accuracy calibration.

The window to establish this advantage is NOW -- before other open-source projects (PRISM-INSIGHT, FinRobot) add environmental scanning capabilities. The upstream systems are built. The architecture is designed. The compounding clock starts when the first pipeline runs.

---

## Appendix: Priority Adjustments from Balanced PRD

| Feature | Balanced PRD Priority | Superiority-Adjusted Priority | Rationale |
|---------|----------------------|------------------------------|-----------|
| Signal persistence (append-only storage) | Not explicitly listed | **P0/M1** | Foundation of all compounding advantages |
| Signal evolution tracker | Conditional/M3 | **P0/M2** | Time-dependent moat must start early |
| Decision journal template in reports | Conditional/M3 | **P0/M1** (template only) | Zero code cost, habit formation |
| Decision journal CLI | P2/M3 | **P1/M3** | Personal reasoning corpus |
| Outcome annotation (`investscan annotate`) | Phase 2 | **P1/M4** | Required for M6 accuracy report |
| Accuracy section in weekly reports | Not listed | **P0/M6** | Visible proof of superiority |
| Source reliability scoring | Phase 2 | **P1/M8** | Data moat deepening |
| STEEPs classifier v2 (feedback-trained) | Phase 2 | **P1/M7** | Methodology moat deepening |
| Public accuracy report | Phase 3 | **P1/M12** | Trust moat establishment |

All other priorities from the Balanced PRD remain unchanged. The adjustments above add approximately 15-20 additional developer-hours to the 6-month budget (from ~60-80 to ~75-100 hours), primarily in signal persistence infrastructure and outcome annotation tooling. This is within the Aggressive scenario's budget range while maintaining the Balanced scenario's "build for yourself" philosophy.
