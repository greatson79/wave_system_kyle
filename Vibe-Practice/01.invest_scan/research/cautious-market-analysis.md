# InvestScan: Cautious Market Analysis

> **Analyst Role**: Cautious Market Researcher
> **Core Assumption**: "This market may be smaller than expected or already saturated"
> **Date**: 2026-03-27

---

## 1. Market Size: Conservative Estimate

### 1.1 The Denominator Problem — How Many Korean Investors Actually Exist?

Let us start with the uncomfortable truth about the "14 million Korean stock investors" headline number.

**Raw Account Numbers vs. Active Investors:**
- Total securities accounts in Korea: estimated 70-80 million (many individuals hold 4-5 accounts each)
- Estimated unique individual investors: ~14 million people
- But **active** investors who trade more than once per quarter: significantly fewer — industry estimates suggest 5-7 million
- Retail investors account for ~64% of annual transaction amounts on Korean exchanges ([Korea Times, 2023](https://www.koreatimes.co.kr/economy/20231114/retail-investors-take-up-64-of-korean-stock-market))

**The MZ Generation Exodus — A Critical Warning:**
The "donghakaemi" (동학개미) wave is not just fading — it is actively reversing among the youngest cohorts:
- 20s investors: peaked at 2.04 million (2021) → dropped to 1.80 million (2022) → lost another 250,000 in 2023 ([Investing.com Korea](https://kr.investing.com/analysis/article-200447152))
- The decline expanded to the 40s age group by 2023
- Young investors who left Korean markets did not stop investing — they migrated to US stocks, crypto, and other high-volatility assets ([Investing.com Korea](https://kr.investing.com/analysis/article-200451449))
- The remaining Korean market participants skew older and less tech-adventurous

**The 2025-2026 Rally Complicates This**: KOSPI surged 76% in 2025 (world's #1 performing index) and has added another 25% YTD in 2026, breaching 6,000 ([Korea Herald](https://www.koreaherald.com/article/10646103); [CNBC](https://www.cnbc.com/2026/03/06/kospi-south-koreas-stock-market-volatility.html)). Retail investors earned 32% returns on domestic stocks in 2025 ([KED Global](https://www.kedglobal.com/korean-stock-market/newsView/ked202512230002)). This rally **may** bring some investors back — but it also means most are making money with existing simple tools, reducing the felt need for complex local AI systems.

### 1.2 The Real Question: Who Wants LOCAL AI Tools?

Now let us narrow the funnel ruthlessly:

| Funnel Stage | Population | Reasoning |
|---|---|---|
| Korean stock investors (unique) | ~14 million | KRX / KOFIA estimates |
| Active traders (quarterly+) | ~5-7 million | Industry estimates, many accounts are dormant |
| Investors who use ANY analysis tool beyond their broker app | ~1-2 million | Most use Toss/Kakao MTS and consider it sufficient |
| Investors technically capable of running local Python/AI pipelines | ~100,000-300,000 | Requires Python, terminal comfort, hardware |
| Investors willing to SET UP AND MAINTAIN a local AI system | ~20,000-50,000 | Time cost, update burden, troubleshooting |
| Investors who would PAY for such a system | ~5,000-15,000 | Free alternatives exist (TradingView, OpenBB, PRISM-INSIGHT) |

**Conservative TAM (Total Addressable Market): 20,000-50,000 users**
**Conservative SAM (Serviceable Addressable Market): 5,000-15,000 users**
**Conservative SOM (Serviceable Obtainable Market in Year 1-2): 500-2,000 users**

### 1.3 Revenue Implications

If this is a local tool (not SaaS), monetization is inherently harder:
- One-time license: 50,000-200,000 KRW ($35-$145) per user
- Year 1-2 realistic revenue: **25 million - 290 million KRW** ($18K-$210K)
- This is a **hobby project revenue range**, not a venture-scale business

**Annual Growth Rate (Conservative)**: 15-20% — driven by general AI adoption, but constrained by the local-deployment barrier. The robo-advisor market globally grows at ~30% CAGR ([GlobeNewsWire](https://www.globenewswire.com/news-release/2026/02/13/3237929/28124/en/Robo-Advisory-Market-Analysis-Report-2026-54-74-Bn-Market-Opportunities-Trends-Competitive-Landscape-Strategies-and-Forecasts-2020-2025-2025-2030F-2035F.html)), but that is cloud SaaS — local tools will grow much slower.

### 1.4 Honest Assessment

**Is "local AI investment analysis" a real market or a niche fantasy?**

It is a **real niche** — not a fantasy, but emphatically not a mass market. The intersection of "sophisticated enough to want deep analysis" AND "technical enough to run local AI" AND "privacy-conscious enough to reject cloud solutions" is a very small Venn diagram overlap. This is more comparable to the audience for quantitative finance libraries (QuantConnect, Zipline) than for consumer fintech apps.

---

## 2. Competitive Landscape: Competitor Strengths (Honest Assessment)

### 2.1 Tier 1: Billion-Dollar Incumbents (We Cannot Beat Them on Data)

| Competitor | Strengths | Why They Are Formidable |
|---|---|---|
| **Bloomberg Terminal** | 30+ years of data, real-time feeds from every exchange globally, BloombergGPT, 350,000+ subscribers | $24K/year but institutional clients do not blink. Data moat is insurmountable. |
| **AlphaSense** | AI-powered search across millions of filings, transcripts, expert calls. Forbes Top 50 AI company. CNBC Disruptor 50 (#8, 2025) | They have the document corpus we will never have. ([AlphaSense](https://www.alpha-sense.com/compare/alphasense-vs-bloomberg/)) |
| **Kensho (S&P Global)** | Event-driven impact analysis, connects geopolitical events to market outcomes, backed by S&P Global's data | Exactly the macro-to-market signal mapping we claim to do — but with orders of magnitude more data ([Analytics Insight](https://www.analyticsinsight.net/artificial-intelligence/which-ai-tools-are-best-for-financial-analysis-in-2026)) |
| **FactSet** | Deep proprietary datasets, portfolio analytics, multi-asset class coverage | Institutional standard alongside Bloomberg |
| **Refinitiv (LSEG)** | Eikon terminal, real-time market data, alternative data integration | Another terminal giant with global coverage |

**Honest verdict**: We have zero chance of competing with these on data breadth, real-time feeds, or institutional credibility. Our only angle is "free / local / Korean-market-focused."

### 2.2 Tier 2: Mobile Apps (We Cannot Beat Them on UX)

| Competitor | Strengths | Why They Are Formidable |
|---|---|---|
| **Toss Securities (토스증권)** | MAU 2.2 million (community alone), part of 24.8M MAU Toss ecosystem. One-tap trading. | The UX gap between a Python CLI and Toss is an ocean. ([Namu Wiki](https://namu.wiki/w/%ED%86%A0%EC%8A%A4%EC%A6%9D%EA%B6%8C)) |
| **Kakao Pay Securities** | Integrated into KakaoTalk ecosystem (50M+ users). Friction-free entry. | They do not need users to "set up" anything. |
| **Kiwoom Securities (키움증권)** | #1 MTS for active traders, HTS for power users, lowest fees | Already serves the "serious retail trader" segment we target |
| **Samsung Securities / Mirae Asset** | Full-service brokers with AI-powered analysis features built into their apps | They are embedding AI INTO existing flows, not asking users to install new tools |

**Honest verdict**: The Korean mobile trading app ecosystem is world-class. The trend is overwhelmingly toward SIMPLICITY, not complexity. InvestScan asks users to swim against this current.

### 2.3 Tier 3: Free/Low-Cost Analysis Tools (We Cannot Beat Them on Price)

| Competitor | Strengths | Why They Are Formidable |
|---|---|---|
| **TradingView** | 100M+ global users, Korean localization, free tier with advanced charting, massive community ([TradingView Korea](https://kr.tradingview.com/)) | "Good enough" for 95% of retail investors. Free. |
| **Google Finance / Naver Finance** | Completely free, zero setup, accessible on any device | The default "analysis tool" for casual investors |
| **OpenBB** | Open-source, 25,000+ GitHub stars, 50+ data sources, evolving from CLI to enterprise workspace. SOC 2 Type II certified. ([OpenBB](https://openbb.co/)) | The most direct competitor — and they are 3+ years ahead with institutional adoption |
| **PRISM-INSIGHT** | Korean-built, 14 AI agents, Korean + US stocks, open-source, free. Season 1 simulation: 408.6% cumulative return ([GitHub](https://github.com/dragon1086/prism-insight)) | **This is almost exactly what InvestScan would be** — and it already exists, is free, and has community traction |
| **Thinkpool (씽크풀)** | Korean AI stock analysis, established user base, web-based ([Thinkpool](https://www.thinkpool.com/)) | No installation required, Korean-native |

### 2.4 Tier 4: Korean Robo-Advisors (They Already Have the Users)

| Competitor | AUM / Scale | Positioning |
|---|---|---|
| **Fint (핀트)** | 31.2 billion KRW AUM, AI algorithm "ISAAC" ([Fint](https://www.fint.co.kr/)) | Fully managed AI investing — user does nothing |
| **AIM (에임)** | 409.7 billion KRW AUM (#2 in Korea) | Higher minimum (3M KRW) but fully automated |
| **Newjistock / Genport (뉴지스탁/젠포트)** | Quant analysis + robo-advisor, iM Financial Group subsidiary ([Newjistock](https://intro.newsystock.com/)) | Already has the "quant for retail" positioning |
| **Quantit (퀀팃)** | AI fintech, B2B + B2C solutions ([Quantit](https://www.quantit.io/)) | Enterprise-grade AI for finance |

**Honest verdict on differentiation**: The claimed differentiators of InvestScan — environmental scanning, news crawling, signal classification — overlap heavily with what Kensho does (at institutional scale), what PRISM-INSIGHT does (at the open-source level), and what broker apps increasingly bundle for free.

### 2.5 What Genuinely Differentiates InvestScan?

Being brutally honest, there are only a few genuine differentiators:

1. **116-site global news crawling at zero API cost** — this is technically impressive but PRISM-INSIGHT and others are catching up
2. **STEEPs + Three Horizons + Tipping Point framework** — unique in the Korean market, borrowed from futures studies. This is the strongest differentiator because no competitor offers environmental scanning methodology applied to investment
3. **Complete data sovereignty** — everything stays on the user's machine. Post-privacy-regulation, this matters to some
4. **Bilingual EN/KR with academic rigor** — most competitors are either English-only (Bloomberg) or Korean-only (broker apps)

**Can we really compete with billion-dollar tools?** No. But we can serve a niche they ignore: the technically capable Korean investor who wants deep, methodology-driven analysis with full data ownership. The question is whether this niche is large enough to matter.

---

## 3. Entry Timing: Challenge — Is It Already Too Late?

### 3.1 What New Ground Remains?

**AI investment tools already exist in abundance.** Let us map what is already covered:

| Capability | Already Available? | Covered By |
|---|---|---|
| AI stock screening | Yes | PRISM-INSIGHT, Thinkpool, broker apps |
| News sentiment analysis | Yes | Kensho, AlphaSense, RavenPack |
| Portfolio optimization | Yes | Fint, AIM, robo-advisors |
| Technical analysis | Yes | TradingView (world-class) |
| Fundamental analysis | Yes | OpenBB, FactSet, broker HTS |
| Macro event impact | Yes | Kensho (S&P Global) |
| Korean market focus | Yes | PRISM-INSIGHT, Thinkpool, Newjistock |
| Local/self-hosted | Partially | OpenBB (limited), FinRobot, Ghostfolio |
| Environmental scanning for investment | **No** | **This is the gap** |

The only genuinely uncovered ground is applying **futures studies methodology** (environmental scanning, weak signal detection, FSSF classification, Three Horizons) to investment decision-making in a local, automated system. This is academically interesting but commercially unproven.

### 3.2 Directional Trend: Simplicity vs. Complexity

The evidence is overwhelming — individual investors are moving TOWARD simplicity:

**Evidence for simplicity trend:**
- Toss Securities grew from zero to 2.2M MAU community by making investing "as easy as sending money"
- Mobile trading (MTS) has completely displaced desktop HTS for most retail investors
- Korean fintech platforms compete on "fewer taps to trade," not "deeper analysis"
- Robo-advisors (Fint, AIM) sell the promise of "let AI do everything, you do nothing"
- The most successful recent innovation: fractional shares (소수점 매매) — making investing simpler, not smarter

**Evidence for complexity trend (weak):**
- Quant community (Newjistock Genport) has a loyal niche following
- Developer-investors (mainly in tech sector) experimenting with AI agents
- The 2025-2026 KOSPI rally has renewed interest in Korean market analysis
- Growing local LLM capabilities (Ollama, etc.) lower the barrier slightly

**Verdict**: The mainstream is moving toward simplicity. The complexity-seeking segment exists but is small and shrinking as AI makes "automated simple" more capable.

### 3.3 Is the "Donghakaemi" (동학개미) Wave Fading?

**Yes, substantially.** The data is clear:

- 20s investors: -10% from peak (2021 → 2022), another -250K in 2023
- 30s investors: declining since 2022
- 40s investors: started declining in 2023
- The Korean market now has an **aging investor base** — those who remain are "고인물" (stagnant veterans)
- Young investors who left went to US stocks and crypto, not to "better analysis tools"

**However**: The KOSPI's 76% surge in 2025 and continued rally to 6,000+ in 2026 may partially reverse this. If young investors return to the Korean market, there could be renewed demand for analysis tools. But they would likely use mobile apps, not local AI pipelines.

### 3.4 Technical Barriers: Can Average Investors Run Local AI Pipelines?

**No.** The honest assessment:

**Requirements to run InvestScan (based on the existing systems):**
- Python 3.12+
- macOS (Apple Silicon) or Linux
- 5GB+ disk space (ML models)
- Playwright browser automation
- spaCy NLP models
- Multiple pip packages (44+ dependencies)
- Terminal/CLI comfort
- Ability to troubleshoot dependency conflicts
- Understanding of Parquet, SQLite, data pipeline concepts

**Research confirms this barrier**: "For a non-technical user, a single swipe or click is often faster and less cognitively demanding than drafting a complex prompt" ([ArXiv](https://arxiv.org/html/2505.17767)). Current LLM agents are "predominantly deployed in specialized, high-effort domains where users are already domain experts."

**The user who can set up GlobalNews-Crawling's 171 Python modules is not the same person who uses Toss Securities.** We are targeting a very specific intersection: financially sophisticated AND technically capable AND interested in Korean markets AND willing to maintain a local system. This is perhaps 20,000-50,000 people in all of South Korea.

---

## 4. Conclusions

### 4.1 Realistic Market Size

| Metric | Conservative Estimate |
|---|---|
| TAM (technically capable Korean investors interested in AI analysis) | 20,000-50,000 users |
| SAM (willing to set up and maintain local system) | 5,000-15,000 users |
| SOM (achievable in Year 1-2) | 500-2,000 users |
| Revenue potential (Year 1-2, one-time license model) | 25M-290M KRW ($18K-$210K) |
| Revenue potential (subscription model, 5K-10K KRW/month) | 30M-240M KRW/year ($22K-$175K/year) |
| Market growth rate | 15-20% annually (constrained by local-deployment barrier) |

**This is not a venture-scale market as a local tool.** It is a viable passion project or niche open-source community project that could generate supplementary income.

### 4.2 Top 3 MUST-HAVE Features (Defensive Perspective)

These are not "nice-to-haves" — without them, the project has no reason to exist given the competitive landscape:

**1. One-Command Installation & Auto-Update (Survival Feature)**

Why it is critical: The #1 reason local tools fail is installation friction. If setup takes more than 10 minutes or requires troubleshooting, 80%+ of potential users will abandon. Every competitor is either cloud-based (zero setup) or one-click mobile (zero setup). The technical barrier is the single largest threat to adoption.

- Must work: `curl -fsSL install.sh | bash` or `brew install investscan`
- Auto-update pipeline models, crawling adapters, and dependencies
- Built-in health check and self-diagnosis
- Docker option for isolation

**2. Environmental Scanning Signal-to-Investment Bridge (Unique Value)**

Why it is critical: This is the ONLY feature that genuinely differentiates InvestScan from every competitor. No one else applies futures studies methodology (STEEPs, FSSF 8-type classification, Three Horizons, Tipping Point detection) to generate actionable investment signals. Without this, InvestScan is just a worse version of PRISM-INSIGHT or OpenBB.

- Automated: scan → classify signals → map to investment implications → generate short/mid/long-term direction
- Must produce output that is demonstrably superior to what Toss/Kakao AI features provide
- Korean market-specific context (KRX sectors, Korean policy impacts, chaebol dynamics)

**3. Plain-Language Dashboard with Zero-CLI Operation Mode (Market Expansion)**

Why it is critical: To expand beyond the 5,000-person "developer-investor" core, InvestScan MUST offer a mode where users never touch a terminal. A local Streamlit/web dashboard that auto-launches, presents findings in Korean natural language, and allows drill-down with clicks — not commands.

- Daily briefing: "Here is what changed overnight and what it means for your portfolio direction"
- Risk alerts in plain Korean
- One-click report generation (PDF/DOCX)
- Mobile-responsive local web UI (access from phone on same network)

### 4.3 Major Risks (3 Serious Ones)

**Risk 1: PRISM-INSIGHT and Similar Open-Source Projects Make InvestScan Redundant (Probability: HIGH)**

PRISM-INSIGHT already offers 14 AI agents analyzing Korean + US stocks, is fully open-source, free, and has demonstrated 408.6% simulated returns. It has community traction on GeekNews and GitHub. If PRISM-INSIGHT adds environmental scanning or macro analysis capabilities — which is entirely plausible — InvestScan's unique value proposition evaporates. The open-source AI finance space is moving fast; by the time InvestScan launches, 2-3 more competitors may emerge.

Mitigation: Ship the environmental-scanning-to-investment bridge FAST and make it the definitive implementation. Establish thought leadership in "futures studies for investment" before others occupy this niche.

**Risk 2: Broker Apps Embed "Good Enough" AI Analysis, Eliminating the Need for Separate Tools (Probability: HIGH)**

Samsung Securities, Mirae Asset, and especially Toss are aggressively embedding AI features into their platforms. When Toss Securities adds "AI market outlook" or "personalized signal alerts" (which is inevitable given their AI investment), the value proposition of running a separate local tool diminishes catastrophically. Users will ask: "Why would I maintain a Python pipeline when Toss gives me 80% of the insight with zero effort?"

Mitigation: Emphasize depth and methodology that broker apps cannot replicate. Position as "the last 20% of insight that matters for serious allocations." This is a hard sell.

**Risk 3: Technical Maintenance Burden Causes User Churn (Probability: VERY HIGH)**

Local tools require ongoing maintenance: Python version updates break dependencies, website layout changes break crawlers, ML model updates require re-downloads, macOS updates cause compatibility issues. The GlobalNews-Crawling system has 171 Python modules and 44+ pip dependencies — this is a maintenance nightmare for individual users. Every broken crawl adapter, every `pip install` conflict, every "it worked yesterday" moment pushes users toward the zero-maintenance cloud alternatives.

Mitigation: Invest heavily in containerization (Docker), automated testing of crawl adapters, graceful degradation (if 10 of 116 sites break, the system still works), and a dead-simple update mechanism. This is unglamorous work but existential for user retention.

---

## Appendix: Summary Verdict

**The honest bottom line**: InvestScan as a local AI tool is targeting a real but very small niche — perhaps 5,000-15,000 potential users in Korea. It has one genuinely unique angle (environmental scanning methodology applied to investment), but faces overwhelming competition from simpler tools (mobile apps), cheaper tools (free open-source), and more powerful tools (institutional platforms). The local-deployment requirement shrinks the addressable market by 10-50x compared to an equivalent SaaS offering.

**Recommendation from the cautious perspective**: If the goal is commercial viability, strongly consider a hybrid model — local processing for sensitive data + lightweight cloud sync for convenience features. If the goal is open-source community building and personal use, the project is well-conceived and the environmental scanning differentiator is genuinely novel. But do not expect mass-market adoption.

The most honest framing: **InvestScan is a power tool for a power-user niche. It will never be Toss. The question is whether it can be the "Bloomberg Terminal for Korean individual quants" — and whether that audience is large enough to sustain development.**

---

Sources:
- [Retail investors take up 64% of Korean stock market - Korea Times](https://www.koreatimes.co.kr/economy/20231114/retail-investors-take-up-64-of-korean-stock-market)
- [Korean retail investors earn 32% on domestic stocks in 2025 - KED Global](https://www.kedglobal.com/korean-stock-market/newsView/ked202512230002)
- [Kospi tops global markets with world's strongest gains in 2025 - Korea Herald](https://www.koreaherald.com/article/10646103)
- [Why the world's top-performing stock market in 2025 is seeing historic volatility - CNBC](https://www.cnbc.com/2026/03/06/kospi-south-koreas-stock-market-volatility.html)
- [KOSPI bull run likely to hit 5,000 in 2026 - KED Global](https://www.kedglobal.com/korean-stock-market/newsView/ked202512120005)
- [MZ세대 주식투자자 수 감소 - Investing.com Korea](https://kr.investing.com/analysis/article-200447152)
- [젊은 투자자는 모두 떠나고 고인물만 남아 - Investing.com Korea](https://kr.investing.com/analysis/article-200451449)
- [Robo Advisory Market $54.74B Report 2026 - GlobeNewsWire](https://www.globenewswire.com/news-release/2026/02/13/3237929/28124/en/Robo-Advisory-Market-Analysis-Report-2026-54-74-Bn-Market-Opportunities-Trends-Competitive-Landscape-Strategies-and-Forecasts-2020-2025-2025-2030F-2035F.html)
- [Robo Advisor Market to Reach $3.2T by 2033 - PR Newswire](https://www.prnewswire.com/news-releases/robo-advisor-market-projected-to-reach-usd-3-2-trillion-by-2033--growing-at-a-strong-cagr-of-10-5-during-20262033---market-research-intellect-302565838.html)
- [AlphaSense vs Bloomberg - AlphaSense](https://www.alpha-sense.com/compare/alphasense-vs-bloomberg/)
- [AI Tools for Financial Analysis 2026 - Analytics Insight](https://www.analyticsinsight.net/artificial-intelligence/which-ai-tools-are-best-for-financial-analysis-in-2026)
- [OpenBB - The AI Workspace for Finance](https://openbb.co/)
- [OpenBB Challenges Bloomberg's Monopoly - Dynamic Business](https://dynamicbusiness.com/ai-tools/openbb-financial-research-platform-challenges-bloombergs-monopoly.html)
- [PRISM-INSIGHT - GeekNews](https://news.hada.io/topic?id=26302)
- [PRISM-INSIGHT GitHub](https://github.com/dragon1086/prism-insight)
- [TradingView Korea](https://kr.tradingview.com/)
- [Fint AI Investment](https://www.fint.co.kr/)
- [Quantit AI Fintech](https://www.quantit.io/)
- [Newjistock](https://intro.newsystock.com/)
- [December & Company](https://www.dco.com/)
- [The Real Barrier to LLM Agent Usability - ArXiv](https://arxiv.org/html/2505.17767)
- [한국 로보어드바이저 시장 30조 전망 - 한국경제](https://www.hankyung.com/economy/article/2018051758476)
- [Thinkpool AI Analysis](https://www.thinkpool.com/)
- [KOSPI sustain record performance 2026 Part 1 - FXStreet](https://www.fxstreet.com/news/can-the-kospi-index-sustain-its-record-breaking-performance-in-2026-part-one-202603091205)
- [20대 젊은 동학개미 저물고 - eDaily](https://marketin.edaily.co.kr/News/ReadE?newsId=01810566642336856)
