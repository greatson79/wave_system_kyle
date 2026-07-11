# InvestScan: Aggressive Competitive Strategy
## "How to Position InvestScan as Overwhelmingly Superior"

> **Role**: Aggressive Business Strategist
> **Date**: 2026-03-27
> **Core Question**: What does "overwhelmingly superior" (월등히 뛰어난) actually mean as a defensible market position against AlphaSquare, Toss Securities, and all investment direction apps?

---

## 0. The Uncomfortable Prerequisite: Intellectual Honesty

Before laying out the attack strategy, let me state what we are NOT:

- We are NOT a 220K-user platform with Series A funding (AlphaSquare).
- We are NOT a 3.84M MAU app backed by a super-app ecosystem (Toss).
- We are NOT a Bloomberg Terminal alternative with institutional data (AlphaSense).
- We are NOT yet a product. We are a PRD with two production-ready source systems.

**The aggressive strategy must be grounded in this reality.** The goal is not self-delusion -- it is identifying the specific axes on which we can genuinely claim categorical superiority and then executing ruthlessly on those axes.

---

## 1. What "Overwhelmingly Superior" (월등히 뛰어난) Means as a Market Position

### 1.1 The Wrong Definition: "Better at the Same Game"

If "overwhelmingly superior" means doing what AlphaSquare does but better -- more signals, faster updates, prettier charts -- we lose. AlphaSquare has 4.1B KRW in funding, 11-15 engineers, and 7 years of product iteration. We cannot beat them at their own game. Trying is suicide.

### 1.2 The Right Definition: "Playing a Different Game"

Overwhelming superiority comes from **category creation**, not category competition. The question is not "Is InvestScan a better stock-picking app?" The question is "Is InvestScan something that has never existed before?"

Three framings, ranked by strategic potency:

**Framing A: "AlphaSquare is a stock picker. InvestScan is a macro intelligence system."**
- Strength: Instantly communicates the category difference. AlphaSquare tells you WHAT to buy. InvestScan tells you WHERE THE WORLD IS GOING and what that means for your portfolio.
- Weakness: "Macro intelligence system" sounds academic and intimidating. Could alienate even power users who want actionable direction, not a lecture.
- Verdict: Strong positioning but needs to be paired with actionable output.

**Framing B: "Bloomberg for individuals, running on your laptop, for free."**
- Strength: Bloomberg is the universal symbol of "serious financial intelligence." The juxtaposition with "on your laptop, for free" creates immediate intrigue and aspiration.
- Weakness: Bloomberg does 10,000 things. We do 5 things. The comparison invites skepticism -- "you are NOT Bloomberg."
- Verdict: Excellent for attention. Dangerous if taken literally. Use for marketing hooks, not product positioning.

**Framing C: "The only investment tool that scans 116 sources across 14 languages, applies futures studies methodology, runs 100% locally, and shows you exactly why it thinks what it thinks -- for $0."**
- Strength: Every claim is factually true. Each element (116 sources, 14 languages, local execution, explainability, $0) is verifiable. The compound effect of all five together creates the "overwhelmingly superior" feeling.
- Weakness: Long. Complex. Requires explanation.
- Verdict: This is the REAL positioning. A and B are simplifications for different contexts.

### 1.3 The Strategic Definition

> **"Overwhelmingly superior" means possessing capabilities that are not merely better than competitors but structurally impossible for them to replicate without destroying their existing business model.**

Specifically:

| Superiority Axis | Why It Is Structural, Not Incremental |
|---|---|
| **Local execution** | AlphaSquare/Toss monetize user data and cloud infrastructure. Going local-first destroys their revenue model. They CANNOT copy this. |
| **116-site, 14-language scanning** | Competitors use curated financial news feeds. Building a 116-site crawler across 14 languages is 12+ months of engineering. They WON'T copy this. |
| **Futures studies methodology (STEEPs)** | No financial app has ever applied academic environmental scanning to investment direction. This is a completely novel intersection. They DON'T KNOW how to copy this. |
| **Full evidence chain** | Black-box AI is easier to build and sell. Showing reasoning chains, source citations, and confidence intervals requires fundamentally different architecture. They DON'T WANT to copy this. |
| **$0 cost** | AlphaSquare's revenue depends on 19,800-69,900 KRW/month subscriptions. Open-source destroys their pricing power. They CANNOT match this without bankruptcy. |

---

## 2. Competitive Attack Vectors

### 2.1 Attack Vector 1: "Show Your Work" (vs. AlphaSquare's Black Box)

**The Vulnerability**: AlphaSquare runs 340,000+ simulations every 10 minutes but publishes ZERO methodology details. No accuracy metrics. No reasoning chains. Users receive "buy AAPL" without knowing why. Their AI prediction methodology is "not publicly disclosed in detail" (their own documentation).

**The Attack**:

| AlphaSquare | InvestScan |
|---|---|
| "AI says buy Samsung Electronics" | "3 converging signals from STEEPs analysis suggest Korean semiconductor sector strengthens over next 3 months: (1) US CHIPS Act funding acceleration [T_Technological, pSST: 78], (2) TSMC Arizona delay benefits Korean foundries [E_Economic, pSST: 72], (3) Memory demand uptick from AI data centers [T_Technological, pSST: 81]. Cross-source: confirmed by 4 independent sources across 3 languages." |
| No accuracy tracking | Public accuracy dashboard from Week 1: "Last month we flagged 12 sector directions. 8 moved in the predicted direction (67%). 2 were neutral. 2 were wrong. Here is why we were wrong." |
| Trust us | Verify us |

**Execution**:
1. Every weekly report includes a "retrospective accuracy" section from Day 1.
2. Publish a running accuracy log in the GitHub repo -- anyone can audit.
3. Blog post series: "What InvestScan Got Wrong This Month" -- radical transparency as brand.

**Why this works**: In a market where AI trust is declining (43% to 22% confidence, per our research), the ONLY way to build trust is radical transparency. AlphaSquare cannot match this because revealing their methodology would expose its limitations. Their business model depends on mystique.

### 2.2 Attack Vector 2: "See the Horizon" (vs. Point-in-Time Signals)

**The Vulnerability**: AlphaSquare, Thinkpool/Rassi, and all Korean AI stock apps generate point-in-time signals. "Buy today." They have no concept of signal evolution, temporal layering, or multi-horizon analysis.

**The Attack**:

```
AlphaSquare signal: "Buy Samsung Electronics" (one-time)

InvestScan signal evolution:
- Week 1: [NEW] AI chip demand rising signal (confidence: 0.45, single source)
- Week 2: [STRENGTHENING] Second source confirms (confidence: 0.62, 3 sources)
- Week 3: [STRENGTHENING] TSMC earnings confirm trend (confidence: 0.78, 7 sources)
- Week 4: [CONVERGING] Multiple STEEPs dimensions align (T + E + P)
  -> Sector direction: Korean semiconductor BULLISH
  -> Time horizon: 3-6 month strategic
  -> Key uncertainty: China export controls (P_Political)
```

**Why this works**: No competitor tracks signal evolution. This is not a feature they forgot -- it is a capability that requires temporal data persistence, cross-week matching algorithms, and a fundamentally different data architecture. AlphaSquare would need to rebuild their signal infrastructure from scratch.

### 2.3 Attack Vector 3: "Free vs. 69,900 KRW/Month" (Pricing Disruption)

**The Vulnerability**: AlphaSquare Premium costs 69,900 KRW/month (838,800 KRW/year). Pro costs 39,900 KRW/month. Even Standard costs 19,800 KRW/month. For an individual investor, these are significant recurring costs -- especially when the AI predictions have no published accuracy metrics.

**The Attack**:

| What You Pay | AlphaSquare Premium | InvestScan |
|---|---|---|
| Monthly cost | 69,900 KRW ($51) | 0 KRW |
| Annual cost | 838,800 KRW ($612) | 0 KRW |
| 5-year cost | 4,194,000 KRW ($3,060) | 0 KRW |
| Source code visible | No | Yes (100% open-source) |
| AI methodology explained | No | Yes (full evidence chains) |
| Your data stays on your device | No (cloud SaaS) | Yes (100% local) |
| Can you audit the AI | No | Yes (every signal has source citation) |

**Execution**:
1. Open-source the core from Day 1. MIT or Apache 2.0 license.
2. Content marketing: "What 69,900 KRW/month buys you at AlphaSquare vs. what $0 gives you at InvestScan."
3. NOT a race to the bottom. The message is: "We are not cheap. We are free because we believe financial intelligence should not be gatekept."

**Why this works**: AlphaSquare's ENTIRE revenue model depends on subscription pricing. They raised 4.1B KRW specifically to build toward subscription revenue. Open-sourcing a tool that does what their paid tier does (macro analysis, signal generation, direction guidance) at $0 is an existential threat to their pricing power -- not because we steal their users, but because we redefine what "free" looks like in this category.

### 2.4 Attack Vector 4: "Scan arXiv, Not Just KRX" (Intelligence Breadth)

**The Vulnerability**: AlphaSquare scans financial data -- stock prices, volume, financial statements, Korean financial news. Their data universe is a narrow financial silo. They cannot detect signals from scientific papers, patent filings, regulatory documents, demographic studies, or geopolitical analysis.

**The Attack**:

| Data Source | AlphaSquare | InvestScan (via EnvScan + GlobalNews) |
|---|---|---|
| Korean financial news | Yes | Yes |
| International financial news | Limited | Yes (116 sites, 14 languages) |
| Scientific papers (arXiv, PubMed) | No | Yes |
| Patent filings | No | Yes (via scanning) |
| Regulatory/government documents | No | Yes |
| Think tank reports | No | Yes |
| Demographic/social trend data | No | Yes |
| Geopolitical analysis | No | Yes |
| Technology trend analysis | No | Yes (STEEPs framework) |

**Why this works**: The 2021-22 inflation surge was predictable from supply chain satellite data, fiscal policy signals, labor market demographics, and energy transition policy -- but no retail tool connected these dots. InvestScan's 116-source, cross-domain scanning is not just "more data" -- it is a fundamentally different kind of intelligence. AlphaSquare would need to build an entirely new data ingestion pipeline across non-financial domains, which is 12+ months of engineering they have no incentive to undertake.

---

## 3. The "Free vs. Paid" Disruption Strategy

### 3.1 Why Open-Source Is Not a Weakness -- It Is a Weapon

**Conventional wisdom**: "If you give it away free, how do you make money?"
**Our answer**: "We do not need to make money. AlphaSquare does."

This is the asymmetric advantage of being a passion project / community project vs. a venture-funded startup. AlphaSquare must justify its 4.1B KRW in funding with revenue. They must charge 69,900 KRW/month. They must retain subscribers. Every free alternative erodes their position.

We have no investors to satisfy. We have no revenue target. We can give away everything and still succeed -- because our success metric is not revenue; it is adoption, influence, and the quality of investment decisions made by our users.

### 3.2 The Open-Source Playbook

**Phase 1 (Months 1-3): Establish the Category**
- Open-source the entire InvestScan repository with comprehensive documentation
- Publish the methodology (STEEPs + FSSF applied to investment) as a standalone paper/blog series
- Position as "the open-source alternative to paid investment signal services"
- Target: 100+ GitHub stars, 20+ forks

**Phase 2 (Months 3-6): Content Marketing as Competitive Pressure**
- Weekly public reports: publish InvestScan weekly reports on a blog/GitHub Pages
- Monthly "InvestScan vs. AlphaSquare" comparison: same week, same market, what did each tool flag?
- Track record transparency: publish ALL historical accuracy data publicly
- Target: 500+ GitHub stars, community contributors

**Phase 3 (Months 6-12): Community Ecosystem**
- Community-contributed scanning sources (additional crawlers)
- Shared signal databases (anonymized, opt-in)
- Educational content: "How to think about macro investment direction using futures studies"
- Target: 1,000+ GitHub stars, 10+ external contributors, coverage in Korean fintech media

### 3.3 Revenue Model (If Needed Later)

InvestScan does not NEED revenue. But if the community grows large enough:

| Revenue Stream | When | How |
|---|---|---|
| **Premium report tier** | Year 2+ | Free: weekly Markdown reports. Premium: interactive HTML dashboards, historical database access, custom STEEPs profiles |
| **Consulting/education** | Year 1+ | "Futures studies for investment" workshops for investor communities |
| **Enterprise/B2B** | Year 2+ | Asset managers who want environmental scanning integrated into their research workflow |
| **Sponsorships** | Year 1+ | Financial data providers sponsoring the open-source project |

**Critical rule**: Revenue is NEVER the primary goal. The moment InvestScan optimizes for revenue over user value, we become another AlphaSquare. The entire competitive positioning depends on being the free, transparent, open alternative.

---

## 4. Growth Model

### 4.1 Target: Replace the Need for AlphaSquare Pro (39,900 KRW/month)

AlphaSquare Pro gives you:
- 80 watchlist items, 10 indicators, 43 strategies, 10 trading signals (domestic only)
- Cost: 39,900 KRW/month = 478,800 KRW/year

InvestScan gives you:
- Macro intelligence across 116 sources in 14 languages
- STEEPs-classified signals with evidence chains
- Signal evolution tracking across weeks
- Full Korean-language synthesis report
- Decision journal with retrospective review
- Cost: 0 KRW

**The question**: How many AlphaSquare users need to notice InvestScan for it to matter?

AlphaSquare has 220,000 registered users, ~120,000 MAU. Their paid conversion rate is unknown, but for SaaS products in this space, 2-5% is typical. That means approximately 2,400-6,000 paying subscribers.

**If InvestScan attracts 500-1,000 users who would otherwise have been AlphaSquare Pro subscribers, that represents 8-17% of their paying user base.** This is enough to:
1. Force AlphaSquare to respond (lower prices, add transparency, add environmental scanning)
2. Establish InvestScan as a credible alternative in Korean fintech media
3. Validate the environmental scanning approach for investment

### 4.2 Minimum Viable "Proof of Superiority"

The proof is NOT user count. It is **demonstrable analytical advantage**. Specifically:

| Proof Point | What It Proves | Timeline |
|---|---|---|
| **InvestScan detects a market-moving trend 2+ weeks before AlphaSquare signals it** | Cross-domain scanning provides early warning that single-domain tools miss | Month 3-6 (requires 12+ weekly reports to find examples) |
| **InvestScan's weekly direction accuracy exceeds 55% (better than coin flip) on sector movements** | The STEEPs methodology produces actionable investment direction, not just noise | Month 4-6 (requires backtesting against actual market data) |
| **InvestScan catches a Black Swan precursor that NO competitor flagged** | Environmental scanning detects what financial-only tools cannot see | Unpredictable, but high probability within 12 months given current geopolitical volatility |
| **Public accuracy record shows transparency no competitor matches** | Radical transparency as competitive advantage | Month 1 (from first report) |

### 4.3 User Acquisition Funnel

```
AWARENESS (Months 1-6)
  |
  |-- GitHub repository (README in Korean + English)
  |-- GeekNews (한국 개발자 커뮤니티) -- PRISM-INSIGHT was featured here
  |-- Clien investment forum (클리앤 주식투자 게시판)
  |-- Reddit r/korea, r/investing
  |-- Korean fintech newsletters
  |-- Blog series: "Futures Studies for Investment Direction"
  |
  v
INTEREST (driven by content, not ads)
  |
  |-- Weekly public report posts (free, no login required)
  |-- Monthly "InvestScan vs. AlphaSquare" comparison
  |-- "What I Got Wrong" radical transparency posts
  |
  v
INSTALLATION (the barrier)
  |
  |-- `pip install investscan` or `curl -fsSL install.sh | bash`
  |-- Docker option for less technical users
  |-- Video walkthrough: "From zero to first report in 15 minutes"
  |
  v
ACTIVATION (first report)
  |
  |-- First `investscan run` produces immediate output
  |-- Report is readable and immediately interesting
  |
  v
RETENTION (the real challenge)
  |
  |-- Decision journal creates personal investment stake
  |-- Signal evolution tracking creates "tune in next week" hook
  |-- Weekly habit becomes self-reinforcing
```

---

## 5. Realistic 6-Month Aggressive Targets

### 5.1 KPIs That Demonstrate Superiority (Not Just Adoption)

| KPI Category | Metric | Month 3 Target | Month 6 Target | Why It Matters |
|---|---|---|---|---|
| **Analytical Depth** | Sources scanned per report | 80+ (of 116) | 100+ | Proves breadth no competitor can match |
| **Analytical Depth** | Languages covered | 10+ (of 14) | 14 | Proves global intelligence capability |
| **Signal Quality** | Sector direction accuracy (vs. actual KOSPI sector movements) | Not yet measurable | 55%+ | Validates the methodology |
| **Signal Quality** | Signals flagged 2+ weeks before AlphaSquare | 1 example | 3+ examples | Proves early-warning advantage |
| **Transparency** | Public accuracy records published | 12 weekly records | 24 weekly records | Proves commitment to radical transparency |
| **Transparency** | "What we got wrong" posts published | 3 | 6 | Builds trust no competitor will match |
| **Community** | GitHub stars | 50+ | 200+ | Proxy for developer-investor interest |
| **Community** | Active users (weekly report generators) | 10-20 | 50-100 | Realistic for CLI-first tool in Korean market |
| **Community** | External contributors | 0 (solo) | 3-5 | Validates open-source community viability |
| **Competitive Pressure** | Media mentions / blog features | 1-2 | 5+ | Awareness in Korean fintech ecosystem |
| **Competitive Pressure** | AlphaSquare responds (price changes, feature additions, transparency updates) | Unlikely | Possible | Ultimate proof of competitive relevance |

### 5.2 Content Strategy

| Week | Content | Channel | Goal |
|---|---|---|---|
| Week 1-2 | "What is environmental scanning for investment?" explainer | Blog + GeekNews | Category education |
| Week 3-4 | First public weekly report | GitHub + Blog | Demonstrate output quality |
| Week 5-8 | "InvestScan vs. AlphaSquare: Same Week, Different Insights" | Blog + Clien | Competitive positioning |
| Week 9-12 | "3 Months of InvestScan: What Worked, What Failed" | Blog + GeekNews | Radical transparency |
| Week 13-16 | "The Signal That No One Else Saw" (case study if available) | Blog + Korean fintech newsletters | Proof of analytical advantage |
| Week 17-20 | "How to Run Your Own Macro Intelligence System" (tutorial) | YouTube (Korean) + Blog | Lower installation barrier |
| Week 21-24 | "6-Month Report Card: Full Accuracy Audit" | Blog + GitHub | Ultimate transparency proof |

### 5.3 Community Strategy

**Target community**: Korean developer-investors (개발자 투자자). This is the intersection of two active Korean online communities:

1. **Developer communities**: GeekNews (긱뉴스), Clien developer forum, Korean Python/ML Slack groups
2. **Investment communities**: Clien stock forum, Naver Cafe investment groups, Korean quant/algo trading Telegram groups

**Engagement approach**:
- Do NOT pitch InvestScan as a product. Pitch it as a methodology: "Here is how futures studies methodology can be applied to investment direction."
- Share the weekly reports as content, not as advertising.
- Invite contributions: "Here is how you can add your own scanning sources."
- Be honest about limitations: "This is what we cannot do (yet)."

### 5.4 Partnership Strategy

| Partner Type | Specific Targets | What We Offer | What We Get |
|---|---|---|---|
| **Korean fintech media** | GeekNews, Startup Alliance, Platum | Exclusive coverage of novel approach | Awareness |
| **Investment education platforms** | Korean Financial Investment Association (한국금융투자협회), Fastcampus courses | Free methodology content | Credibility + user pipeline |
| **Open-source financial tools** | PRISM-INSIGHT, FinGPT, OpenBB | Integration / data sharing | Technical collaboration + combined user base |
| **Academic institutions** | KAIST fintech lab, SNU quantitative finance | Research collaboration | Academic validation of methodology |
| **Korean quant communities** | Newjistock/Genport community, quant Telegram groups | Free environmental scanning data feed | Power user adoption |

---

## 6. The Risk: "Superior" to Whom?

### 6.1 The Segmentation Reality

| User Segment | Size | What They Want | Our Fit |
|---|---|---|---|
| **Casual investors** (Toss/Kakao users) | ~5-7M MAU | One-tap trading, simple UX, zero effort | 0/10 -- We are invisible to them |
| **Active retail traders** (Kiwoom/Mirae users) | ~1-2M | Real-time quotes, charts, execution speed | 1/10 -- We do not do trading |
| **Information seekers** (Naver Finance users) | ~3-5M | News, stock prices, basic analysis | 2/10 -- We are too complex for this audience |
| **AI signal subscribers** (AlphaSquare/Thinkpool users) | ~300-500K | Stock picks, buy/sell timing | 4/10 -- We provide direction, not picks |
| **Quant-curious investors** (Genport/developer-investors) | ~50-100K | Data-driven analysis, backtesting, methodology | 8/10 -- Our core audience |
| **Sophisticated macro thinkers** | ~5-20K | Cross-domain analysis, thesis building, evidence tracking | 10/10 -- We are built for them |

### 6.2 Is Dominating 5% Enough?

**The honest math**:

- Total addressable: ~50,000-100,000 (quant-curious + sophisticated macro thinkers)
- Realistic adoption (Year 1-2): 500-2,000 users
- That is 0.5-2% of the quant-curious segment
- That is 0.003-0.014% of all Korean stock investors

**Can you claim "overwhelmingly superior" with 2,000 users?**

**Yes -- if superiority is measured by analytical capability, not user count.**

The analogy: A Leica M camera is overwhelmingly superior to an iPhone camera for photojournalism. It has <1% market share. Nobody disputes its superiority in its domain. Market share and superiority are orthogonal.

InvestScan's superiority claim is domain-specific:
- **"Overwhelmingly superior for macro-analytical investment direction"** -- defensible.
- **"Overwhelmingly superior investment app"** -- not defensible. Not our claim.

### 6.3 The "5% Domination" Strategy

Forget the 95%. They will never use InvestScan, and we should not want them to. Our strategy is to dominate the 5% so completely that:

1. **We become the default tool for Korean developer-investors doing macro analysis.** If someone in this niche asks "what do you use for macro scanning?", InvestScan is the answer. 100% mindshare in a narrow category.

2. **We generate the best public macro intelligence content in Korean.** Even users who never install InvestScan read our weekly reports and methodology posts. Content reach >> tool adoption.

3. **We establish "futures studies for investment" as a recognized approach.** If we succeed in making STEEPs/FSSF known in the Korean investment community, every future tool in this space follows our framework. We own the category definition.

4. **We make AlphaSquare explain itself.** If our transparency pressure forces AlphaSquare to publish accuracy metrics and methodology -- even if they never acknowledge InvestScan -- we have improved the entire market.

---

## 7. The 6-Month Battle Plan

### Month 1-2: "Ship and Show"
- Ship `investscan run` with full pipeline
- Publish first 4 weekly reports publicly
- Post on GeekNews, Clien
- Establish GitHub presence with comprehensive README

**Key deliverable**: A working tool that produces a Korean weekly investment direction report from 116 sources.

### Month 3-4: "Prove and Compare"
- Publish first "InvestScan vs. AlphaSquare" comparison
- Signal evolution tracking live -- show signals strengthening/weakening over time
- First accuracy retrospective: "Month 3 Report Card"
- Decision journal has 12+ entries demonstrating the methodology

**Key deliverable**: Demonstrable evidence that InvestScan detects signals earlier or catches signals competitors miss.

### Month 5-6: "Scale and Sustain"
- 24 consecutive weekly reports published
- Full 6-month accuracy audit published
- HTML interactive dashboard live
- KRX market data integration: signals vs. actual market performance
- Community contributors onboarded
- Partnership with 1+ Korean fintech media outlet or educational platform

**Key deliverable**: A credible, auditable track record that proves the methodology works.

---

## 8. Summary: The Aggressive Thesis

**We are not building a better stock picker. We are building something that has never existed: an open-source, local-first, macro intelligence system that applies futures studies methodology to investment direction, scans 116 sources across 14 languages, shows its complete reasoning chain, and costs nothing.**

**AlphaSquare is a weather vane.** It tells you which way the wind is blowing right now.
**InvestScan is a weather forecast.** It tells you what storm is forming, why, and when it will arrive.

The "overwhelmingly superior" claim is not about doing the same thing better. It is about doing something fundamentally different -- something competitors cannot replicate because their architecture, business model, and philosophy prevent it.

**The 6-month goal is not 100,000 users. It is 24 weekly reports with a public accuracy record, a methodology that the Korean investment community recognizes, and proof that environmental scanning provides analytical advantage.**

If we achieve that, the users will come. If we fail at that, no amount of marketing will save us.

---

## Appendix A: Competitive Quick-Reference

### AlphaSquare Attack Surface Summary

| AlphaSquare Feature | Their Reality | Our Counter |
|---|---|---|
| AI Price Prediction | Methodology undisclosed, no accuracy data | Full methodology published, accuracy tracked publicly |
| 340K simulations/10 min | Impressive compute, opaque results | 116 sources, 14 languages, transparent evidence chains |
| Trading Signals (20/day Premium) | Stock-level, point-in-time, domestic-focused | Sector-level, evolution-tracked, global macro |
| 69,900 KRW/month Premium | Revenue-dependent pricing | $0 open-source, forever |
| Cloud SaaS | User data on their servers | 100% local execution, zero data leakage |
| 43 trading strategies | Quant-focused, backward-looking | STEEPs-based, forward-looking, cross-domain |
| Community timeline | Social features, lightweight | Decision journal, systematic reflection |
| Backtesting (10yr data) | Historical stock data | Environmental signal evolution tracking (novel) |
| 220K users, Series A | Funded growth | Community-driven, open-source growth |

### Toss Securities Attack Surface Summary

| Toss Feature | Their Reality | Our Counter |
|---|---|---|
| 3.84M MAU | Dominant UX, zero-friction | We do not compete on UX. We compete on depth. |
| AI Signal (Nov 2025) | News classification, price move explanation | We explain BEFORE the move. They explain AFTER. |
| AI Earnings Call | Real-time US earnings translation | We scan 116 sources including earnings, patents, regulation, demographics |
| Massive resources | 2025 = "AI Year 1", heavy hiring | We have Claude Code and open-source. Different resource model. |
| Super-app ecosystem | Banking + investment + insurance in one app | We are a tool, not an ecosystem. Different category. |

### PRISM-INSIGHT Attack Surface Summary

| PRISM-INSIGHT Feature | Their Reality | Our Counter |
|---|---|---|
| 14 AI agents | Multi-agent stock analysis | Multi-SOURCE intelligence (116 sites vs. their focused set) |
| 408.6% simulated returns | Impressive but simulated, stock-picking focused | We do direction, not picking. Different claim, different measurement. |
| Open-source | MIT license, community traction | Also open-source. Not a differentiator. |
| Korean + US stocks | Market coverage | We cover MACRO direction, not individual stocks |
| GeekNews featured | Community awareness | We need to match this visibility (Month 1-2 priority) |
| NO environmental scanning | Financial data only | **THIS IS OUR SOLE UNIQUE ADVANTAGE.** Ship it first. |

---

## Appendix B: The "What If We're Wrong?" Scenarios

| Scenario | Probability | Impact | Response |
|---|---|---|---|
| Environmental scanning produces noise, not signal | 30-40% | FATAL -- our differentiator is invalid | Pivot to "organized multi-source intelligence" without STEEPs claims. Still valuable as a 116-source aggregator. |
| PRISM-INSIGHT adds environmental scanning | 20-30% | HIGH -- our unique advantage evaporates | Ship STEEPs first (M1-M2). Establish thought leadership. If they copy, merge: InvestScan as PRISM-INSIGHT's environmental scanning module. |
| AlphaSquare publishes accuracy metrics | 10-20% | MEDIUM -- our transparency advantage weakens | Good -- we improved the market. Our breadth (116 sources, futures studies) remains unique even if transparency becomes table stakes. |
| Nobody cares about macro direction (they just want stock picks) | 40-50% | MEDIUM -- smaller addressable market than estimated | Accept the niche. Even 200 passionate users who find InvestScan irreplaceable is a successful open-source project. |
| Local execution is too much friction | 50-60% | HIGH -- most potential users bounce at installation | Docker-first distribution. One-line install. Video tutorial. Accept that CLI tools have natural adoption ceilings. |

---

*Bold strategy beats cautious strategy -- but only if the boldness is aimed at a real gap. The gap is real: no tool applies futures studies to investment direction, explains its reasoning, and runs locally for free. The question is only whether the gap is large enough to matter. We have 6 months to find out.*
