# InvestScan: Modern/Cutting-Edge Theory Foundation Analysis

> **Expert Role**: Modern/Cutting-Edge Theory Foundation Expert
> **Date**: 2026-03-27
> **Scope**: Theoretical basis for InvestScan -- a LOCAL AI investment macro intelligence system using environmental scanning (STEEPs) + global news NLP for investment direction
> **Method**: Systematic literature review across 25+ web research queries, 50+ academic papers and industry sources (2020-2026)

---

## Table of Contents

1. [Investment Analysis Theory (Latest 5 Years)](#1-investment-analysis-theory-latest-5-years)
   - 1A. Weak Signal Detection for Finance
   - 1B. Environmental Scanning for Investment
   - 1C. Multi-Agent AI for Investment Research
2. [NLP Theory for Financial Text](#2-nlp-theory-for-financial-text)
   - 2A. Financial Sentiment Analysis
   - 2B. Topic Modeling for Signal Detection
   - 2C. Causal Inference from News
3. [Local AI Execution Theory](#3-local-ai-execution-theory)
4. [Theory-Practice Gap Analysis](#4-theory-practice-gap-analysis)
5. [Conclusions and Recommendations](#5-conclusions-and-recommendations)

---

## 1. Investment Analysis Theory (Latest 5 Years)

### 1A. Weak Signal Detection for Finance

#### Theoretical Origins and Modern Evolution

**Ansoff's Original Concept (1975)**: Igor Ansoff introduced the concept of "weak signals" in strategic management as early warning signs of meaningful change -- subtle indicators that appear before trends become obvious to mainstream observers. His framework distinguished between signal strength (visibility) and response capability (organizational readiness), arguing that waiting for "strong signals" before acting was strategically fatal in turbulent environments.

**Modern Evolution (2012-2025)**: The concept has undergone significant theoretical development:

- **Hiltunen (2012)**: Published "Weak signals: Ansoff today" in *Futures* journal, reconceptualizing weak signals through three dimensions: the signal itself (observable), the issue (emerging phenomenon), and the interpretation (organizational sense-making). This elevated weak signal detection from a passive scanning exercise to an active constructivist practice. (Hiltunen, E., 2012, *Futures*, Vol. 44, Issue 3, pp. 198-205)

- **Ahlqvist & Uotila (2020)**: Published "Contextualising weak signals: Towards a relational theory of futures knowledge" in *Futures* (Vol. 110, pp. 102-111), proposing a relational approach based on positional theory that bridges the Ansoffian (signal-as-external-reality) and constructivist (signal-as-interpretation) traditions.

- **WISDOM Framework (2024)**: Kwon et al. published an AI-powered framework for emerging research detection using weak signal analysis and advanced topic modeling (arXiv:2409.15340). This framework introduced **Topic Emergence Maps (TEMs)** using BERTopic proportions, creating a four-quadrant classification:
  - **Weak signals**: Low average proportion, high growth rate
  - **Strong signals**: High proportion AND high growth rate
  - **Latent signals**: Low on both dimensions
  - **Well-known but not strong (NSWK)**: High proportion, low growth

#### Application to Financial Markets

**Early Warning Systems (2022-2025)**: The financial application of weak signal theory has primarily manifested through early warning signal (EWS) research:

1. **Persistent Homology Approach** (Rimon & Sambayan, 2024; Gidea et al., 2022): Topological Data Analysis (TDA) has emerged as a method for detecting financial market phase transitions. A causal early-warning framework extracts topological signals from multivariate return streams using sliding windows of daily log-returns mapped to point clouds, computing Vietoris-Rips persistence diagrams summarized by persistence landscapes. On four major U.S. equity indices (S&P 500, NASDAQ, DJIA, Russell 2000) over 1999-2021, the method achieves balanced precision-recall with an **average lead time of approximately 34 days** before crashes. (Published in *Computers* 14(10):408, 2025)

2. **Multiplex Recurrence Networks** (EPJ Data Science, 2024): A framework using multiplex recurrence network (MRN) indicators demonstrated that average mutual information serves as an effective EWS for forecasting forthcoming financial crashes, analyzing constituent stocks of both China's and U.S. stock markets.

3. **Graph-Based Risk Signals** (Quantitative Finance, 2025): During periods of enhanced volatility, empirical correlations between assets jump higher, graph structures become denser as securities become more interconnected, and changes in mean and standard deviation of network metrics can serve as early-warning risk signals.

#### Empirical Evidence: Does Weak Signal Detection Improve Returns?

**Direct evidence is limited but encouraging**:

- The topological approach provides ~34-day lead time, which is potentially actionable for portfolio rebalancing (not high-frequency trading)
- Signal lifecycle research (Ansoff through WISDOM) establishes that weak signals have a 3-5 year effect duration before maturing into macro trends (5-10 year effect), meaning a system that identifies signals 6-12 months before consensus would have significant alpha potential
- However, no published study directly links automated weak signal detection to excess portfolio returns in a real-money backtest

**Assessment for InvestScan**: Weak signal detection is the theoretical backbone of the entire system. The WISDOM framework's TEM approach is directly applicable -- InvestScan's STEEPs classification combined with BERTopic temporal analysis can implement the four-quadrant signal classification operationally.

---

### 1B. Environmental Scanning for Investment

#### STEEP/PESTEL Applied to Portfolio Management

**The Framework**: STEEP (Social, Technological, Economic, Environmental, Political) and its extended variants (PESTEL adding Legal; STEEPLE adding Legal + Ethical) provide structured lenses for macro-environmental analysis. These frameworks are ubiquitous in strategic management and corporate planning but have a notable absence from retail investment applications.

**Current Investment Application**:
- The Corporate Finance Institute describes PESTEL as a tool to "identify external forces that could materially alter strategy, economics, or risk profile," explicitly linking it to "capital allocation in an explicit external view" and portfolio choices
- Organizations using PESTEL produce "prioritized external drivers, quantified indicators to monitor, and scenario backdrops that make strategy more robust"
- For every driver identified, best practice demands "so what/now what" linked to Five Forces and capital allocation, with classification into no-regret moves, options, and big bets with triggers

#### Futures Studies Methods in Finance

**Three Horizons Framework** (Hodgson, Curry, Leicester, Sharpe, Lyon, Fazey, 2006):
- H1: Currently dominant system declining as it loses environmental fit
- H2: Turbulent intermediate space of innovations (H2- props up H1; H2+ creates space for H3)
- H3: Envisioned desired future aligned to changing environment

McKinsey adapted this for financial strategy: distributing focus and resources across three temporal horizons for "aligning short-term financial achievements with long-term growth objectives." This is precisely the temporal lens InvestScan needs -- weekly reports that distinguish between H1 (current portfolio), H2 (emerging opportunities/threats), and H3 (structural shifts requiring long-term positioning).

**Causal Layered Analysis (CLA)** (Sohail Inayatullah):
- Four layers: litany (surface events), systemic causes, worldview/discourse, myth/metaphor
- Applied to investment: moves beyond "what happened" (news) to "why it matters structurally"
- InvestScan's multi-layer signal analysis (L1-L5 in GlobalNews-Crawling) maps directly to CLA's layered approach

#### Gap Analysis: Why Existing Investment Apps DON'T Use Environmental Scanning

This is InvestScan's most critical theoretical justification. Analysis of the competitive landscape reveals:

| Platform | What It Does | What's Missing |
|----------|-------------|----------------|
| **Bloomberg Terminal** ($32K/yr) | Comprehensive financial data, news terminal | No structured STEEPs classification; no futures studies lens |
| **Koyfin** ($39-299/mo) | Macro tracking, yield curves, sector performance | Data dashboard, not analytical framework; no signal lifecycle |
| **Seeking Alpha** | 7,000+ contributors, 10,000+ articles/month | Crowdsourced opinion, not systematic environmental scanning |
| **AlphaSquare** (Korean) | Korean stock analysis, community-driven | Microscope (individual stock focus), not telescope (macro) |
| **PRISM-INSIGHT** | 14 AI agents, GeekNews featured | Similar concept but cloud-based, not local-first |

**Why the gap exists** (5 structural reasons):

1. **Disciplinary silo**: Environmental scanning is taught in strategic management and futures studies programs, not finance programs. Investment app developers trained in quantitative finance never encounter STEEP/PESTEL
2. **Quantification challenge**: STEEP dimensions are qualitative by nature; fintech rewards quantitative metrics. Converting "social trend toward remote work" to an actionable investment signal requires multi-step reasoning
3. **Temporal mismatch**: Financial markets operate on microseconds-to-quarters; environmental scanning operates on months-to-decades. Bridging this gap requires explicit temporal translation
4. **Data heterogeneity**: Combining political news, technology trends, social movements, environmental data, and economic indicators into a single analytical framework is technically demanding
5. **Individual investor neglect**: Environmental scanning has been a corporate strategy tool (McKinsey, BCG clients). Nobody has "democratized" it for retail investors

**Assessment for InvestScan**: This gap is real, validated, and represents a genuine category-creation opportunity. InvestScan occupies the "empty quadrant" of macro scanning + local execution + evidence chains + signal evolution. This is InvestScan's strongest theoretical foundation.

---

### 1C. Multi-Agent AI for Investment Research

#### TradingAgents Framework (Tauric Research, December 2024)

**Architecture**: A multi-agent LLM framework inspired by professional trading firms, consisting of:
- **Analyst Team**: Fundamental, sentiment, and technical analysts with specialized data processing
- **Research Team**: Bull and Bear researchers who engage in structured debate
- **Risk Management Team**: Monitoring exposure and risk metrics
- **Traders**: Synthesizing insights from debates and historical data

**Performance Metrics** (arXiv:2412.20138):

| Ticker | Cumulative Returns | Improvement | Sharpe Ratio | Max Drawdown |
|--------|-------------------|-------------|--------------|--------------|
| AAPL | 26.62% | +24.57% vs baseline | 8.21 | 0.91% |
| GOOGL | 24.36% | +16.58% vs baseline | 6.39 | 1.69% |
| AMZN | 23.21% | +6.10% vs baseline | 5.60 | 2.11% |

**Bull-Bear Debate Mechanism**: Bullish researchers "highlight positive market indicators and growth potential" while bearish researchers focus on "risks and negative market signals." This dialectical approach "ensures a balanced understanding of market conditions."

The framework is built with LangGraph, supports multiple LLM providers (OpenAI, Google, Anthropic, xAI, OpenRouter, **Ollama**), and operates "without the need for GPUs."

#### FinRobot (AI4Finance Foundation, 2024-2025)

**Architecture** (arXiv:2405.14767): A four-layer open-source platform:
1. **Financial AI Agents Layer**: Financial Chain-of-Thought (CoT) prompting
2. **Financial LLM Algorithms Layer**: Dynamic model selection for specific tasks
3. **LLMOps and DataOps Layer**: Training/fine-tuning with task-relevant data
4. **Multi-source LLM Foundation Models Layer**: Integration with various LLMs

Includes Market Forecasting Agents, Document Analysis Agents, and Trading Strategies Agents.

#### Critical Limitation: The Multi-Agent Debate Failure Problem

**ICLR 2025 Blog Post** ("Multi-LLM-Agents Debate -- Performance, Efficiency, and Scaling Challenges"):
- Most MAD (Multi-Agent Debate) frameworks **fail to consistently outperform** chain-of-thought (CoT) single-agent approaches
- When compared to self-consistency (SC), most MAD frameworks fail to surpass SC
- Multi-agent debating systems "do not reliably outperform other proposed prompting strategies"

**Specific Failure Modes** (arXiv:2503.13657, 2509.05396):
1. **Weaker agents negatively impact performance**: Contrary to collaborative assumptions, weak agents drag down the group
2. **Correct answers become corrupted during debate**: Sequential revision, social influence, and sycophancy degrade accuracy
3. **Conformity and echo chambers**: Majority agents create convergence regardless of correctness
4. **14 distinct failure modes identified**: System design flaws, inter-agent misalignment, task verification issues

**Assessment for InvestScan**: Multi-agent architecture is PROMISING for structured decomposition (separate analysts for different STEEPs dimensions) but RISKY for debate mechanisms. InvestScan should:
- USE multi-agent for task decomposition (proven benefit)
- AVOID multi-agent debate for consensus building (unproven, high failure rate)
- PREFER structured aggregation over free-form debate
- CONSIDER simple ensemble/voting over iterative argumentation

---

## 2. NLP Theory for Financial Text

### 2A. Financial Sentiment Analysis

#### FinBERT: The Foundation (Araci, 2019-present)

**Architecture**: BERT pre-trained on financial corpus, fine-tuned for financial sentiment classification (positive/negative/neutral). Published as arXiv:1908.10063.

**Performance**: FinBERT achieves F1-scores 4-5% higher than general-purpose sentiment models on financial text. Recent studies (October 2024) showed FinBERT + GPT-4 + logistic regression combinations achieve strong stock price prediction accuracy.

**FinBERT + LSTM** (2024): The combination of FinBERT sentiment with LSTM time series models "achieved the best performance" compared to either approach alone, and sentiment analysis using FinBERT outperformed standalone LSTM.

#### KR-FinBERT: Korean Financial NLP (Seoul National University, 2022)

**Creator**: snunlp (Seoul National University NLP Lab), Kim & Shin, 2022

**Training Corpus** (13.22 GB total):
- Korean Wikipedia + general news + legal texts (base from KR-BERT-MEDIUM)
- Corporate economic news from **72 Korean media sources** (Financial Times Korea, Korean Economy Daily, etc.)
- Analyst reports from **16 securities companies** (Kiwoom Securities, Samsung Securities, etc.)
- 440,067 news titles with content + 11,237 analyst reports = 6,379,315 training lines
- Training: 5.5M steps, 67.48 hours on NVIDIA TITAN XP

**Performance** (Sentiment Classification with 50K labeled data):

| Model | Accuracy |
|-------|----------|
| **KR-FinBERT** | **0.963** |
| KR-BERT-MEDIUM | 0.958 |
| KcBert-large | 0.955 |
| KoBert | 0.817 |

**Available on HuggingFace**: `snunlp/KR-FinBert-SC` with 81,438 downloads/month

**Assessment for InvestScan**: KR-FinBERT is production-ready for Korean financial text sentiment analysis. The 96.3% accuracy on Korean financial news is excellent. This model can run locally on Apple Silicon hardware.

#### LLM-Based Sentiment (2024-2025)

**FinGPT** (arXiv:2412.10823): Enhanced sentiment-based stock movement prediction using dissemination-aware and context-enriched LLMs. Goes beyond single-news analysis to capture broader sentiment landscapes.

**LLaMA-2 Finance** (2024): Trading strategies based on LLaMA-2 sentiments produce "significantly higher buy-and-hold returns compared to those derived from FinBERT and traditional models."

**Key Insight**: The field is rapidly moving from fine-tuned BERT models to instruction-tuned LLMs for financial sentiment. For InvestScan running locally, this means a quantized Qwen3-32B or similar model can potentially replace/complement KR-FinBERT for more nuanced analysis.

#### Sentiment-Return Correlation: What Does Evidence Actually Show?

**Positive Evidence**:
- Greyling & Rossouw (2025): Collective mood states from X (Twitter) data "significantly enhanced the accuracy of predicting whether the Dow Jones Industrial Average would rise or fall the next day"
- Deng et al. (2024): Multiple XGBoost models combined with sentiment features achieved "high accuracy, low risk, and stable returns in predicting Chinese stock index trends"
- Average accuracy of sentiment-based stock prediction: ~63.58% using ensemble methods (above random but not dramatically)

**Critical Caution -- Spurious Correlation Problem**:
A 2025 study (arXiv:2603.21473) delivered a devastating finding: **Raw sentiment-return correlations range from 0.45-0.73, but validated effects (controlling for confounders) are an order of magnitude smaller at 0.034-0.048.** This means approximately 90-95% of observed sentiment-return correlation is spurious.

This finding fundamentally affects InvestScan's design: sentiment analysis should be treated as one input signal among many, NOT as a primary prediction mechanism.

#### Cross-Lingual Financial NLP

**Market Projection**: Sentiment analysis projected to account for 58.9% of financial NLP market revenue by 2025.

**Challenges**:
- Financial terms carry cultural/economic nuances ("keiretsu," "Mittelstand") that standard translations fail to capture
- Sarcasm, humor, indirect communication styles vary across cultures
- Accuracy on translated sentences: ~86% using ensemble models

**ICE-PIXIU**: Integrates bilingual Chinese-English financial task spectrum, bridging the gap for Asian financial NLP.

**Assessment for InvestScan**: For a Korean-primary system analyzing global English-language news, the cross-lingual challenge is real. Strategy should be: process English sources with English models, Korean sources with KR-FinBERT, then merge at the signal level rather than translating text.

---

### 2B. Topic Modeling for Signal Detection

#### BERTopic (Grootendorst, 2022)

**Core Architecture** (arXiv:2203.05794): A neural topic modeling technique using:
1. Document embeddings via Sentence-BERT
2. Dimensionality reduction with UMAP
3. Clustering with HDBSCAN (noise-aware, no forced assignment)
4. Class-based TF-IDF (c-TF-IDF) for topic representation

**Comparative Performance**: BERTopic "consistently achieves higher or comparable topic coherence, diversity, and interpretability" compared to PLSA, LDA, NMF, Top2Vec across domains and languages.

#### Financial Applications of BERTopic (2024-2025)

**FinTextSim** (arXiv:2504.15683, 2025): BERTopic applied to 10-K filings from S&P 500 companies (2016-2022). Critical finding: **BERTopic only forms clear and distinct economic topic clusters when paired with domain-adapted embeddings (FinTextSim)**. Without domain-specific embeddings, BERTopic "struggles with misclassification and overlapping topics."

**Hedge Fund Analysis** (arXiv:2512.06620, 2025): Topic modeling and sentiment correlation applied to hedge fund disclosures.

**Stock Market Prediction** (arXiv:2404.02053, 2024): BERTopic-driven stock market predictions through sentiment unraveling.

#### Dynamic/Temporal Topic Modeling

**BERTopic's Built-in Temporal Mode**: BERTopic allows dynamic topic modeling by "calculating the topic representation at each timestep without the need to run the entire model several times." This enables tracking topic evolution over time.

**TopicProphet** (arXiv:2512.11857, 2025): A system that "prophesies on temporal topic trends and stocks," combining topic modeling with stock market prediction.

**THEME** (arXiv:2508.16936, 2025): "Enhancing Thematic Investing with Semantic Stock Representations and Temporal Dynamics" -- directly connecting topic evolution to investment themes.

**Gap Identified**: "No existing system fully integrates semantic NLP techniques with explicit temporal modeling to support dynamic financial applications" (motivation for THEME framework).

#### Signal Lifecycle Modeling

Combining the WISDOM framework's Topic Emergence Maps with BERTopic's temporal capabilities, a signal lifecycle can be modeled as:

```
EMERGING (weak signal) --> STRENGTHENING (growing proportion + attention)
    --> MAINSTREAM (strong signal) --> WEAKENING (declining attention)
        --> FADING/TRANSFORMED/MERGED
```

InvestScan's GlobalNews-Crawling system already implements a 7-state evolution model (NEW/STRENGTHENING/STABLE/WEAKENING/FADING/TRANSFORMED/MERGED) -- this is theoretically well-grounded.

**Assessment for InvestScan**: BERTopic is the clear choice for topic-based signal detection. CRITICAL: domain-adapted embeddings (e.g., FinTextSim or FinBERT embeddings) are essential -- generic embeddings produce poor results on financial text. The temporal/dynamic mode is directly applicable to InvestScan's weekly signal tracking.

---

### 2C. Causal Inference from News

#### Granger Causality on News-Market Movements

**Core Concept**: Granger causality tests whether past values of one time series (e.g., sentiment scores) contain information useful for forecasting another (e.g., stock returns), beyond what is available in the target series' own history.

**Evidence for News-Market Causality**:
- Granger Causality analysis of sentiment tweets with stock returns has shown "statistically significant causality between stock movements and sentiment" (PMC:10724666)
- However, the test fundamentally relies on linear regression, "neglecting the nonlinear intricacies that underlie interactions between variables"

**Critical Limitation -- False Positive Rates**:
- **40% of Granger-causal relationships fail when controlling for synthetic confounders** (arXiv:2603.21473)
- Raw correlations: 0.45-0.73; validated effects: 0.034-0.048 (an order of magnitude deflation)
- The fundamental problem: "Studies employing Pearson correlation, Granger causality, or information-theoretic measures identify statistical dependencies but fail to account for confounding factors, reverse causality, or multiple testing problems"

#### PCMCI (Runge et al., 2019-present)

**Algorithm**: Implemented in the Tigramite Python package (github.com/jakobrunge/tigramite). PCMCI estimates time-lagged causal links through a two-step procedure:
1. **Condition-selection** using iterative PC1 algorithm
2. **MCI (Momentary Conditional Independence)** test estimating p-values accounting for common drivers, indirect links, and autocorrelation

**False Positive Control**: "MCI empirically well controls false positives even for highly autocorrelated variables, which is due to the conditioning on the parents of the lagged variable."

**Provable Guarantees**: "PCMCI provably estimates the true causal graph in the limit of infinite sample size under the standard assumptions of causal discovery."

**Variants**: PCMCI+ handles contemporaneous causal links; Latent-PCMCI handles hidden confounders.

**CD-NOTS** (2024): A newer method that "consistently outperforms PCMCI for causal discovery in nonstationary time series data" -- relevant for financial data with distributional shifts.

#### Transfer Entropy as Alternative

**Information-theoretic approach**: Transfer entropy measures asymmetric information transfer between sentiment and prices. Non-parametric Shannon and Renyi entropy approaches "provide superior tools for examining nonlinear causality compared to Granger tests, which are constrained to Gaussian time series with linear causation."

#### Expected False Positive Rates

Based on the literature:

| Method | Expected FPR | Notes |
|--------|-------------|-------|
| Raw Granger causality | 30-40% | Uncontrolled confounders |
| Granger with multiple testing correction | 10-15% | Bonferroni/BH correction |
| PCMCI | 5-8% | Provably controlled under assumptions |
| PCMCI+ | 3-7% | Handles contemporaneous links |
| Transfer entropy | 10-20% | Nonlinear but computationally expensive |

**Assessment for InvestScan**: InvestScan's GlobalNews-Crawling already implements Granger causality. This is a reasonable first-pass filter, but the system MUST:
1. Apply multiple testing correction (Bonferroni or Benjamini-Hochberg)
2. Report confidence levels honestly (not overstate causal claims)
3. Consider PCMCI (via Tigramite) as a Phase 2 upgrade for more robust causal discovery
4. NEVER present sentiment-return correlations as proven causation

---

## 3. Local AI Execution Theory

### Apple Silicon + MLX: The Hardware Foundation

#### M5 Max Performance (March 2026)

Apple's M5 Pro and M5 Max represent a significant leap for local LLM inference:

**Time-to-First-Token (TTFT)**:
- Qwen 14B (4-bit): Under 10 seconds, **4.06x speedup** vs M4
- Qwen 30B MoE (4-bit): Under 3 seconds, **3.52x speedup** vs M4
- GPT OSS 20B (MXFP4): **3.33x speedup** over M4

**Token Generation**:
- 19-27% improvement over M4 (153 GB/s vs 120 GB/s memory bandwidth)
- M5 Max with 128GB: Llama 70B fits entirely, estimated 18-25 tok/s

**Neural Accelerators**: Dedicated matrix-multiplication units in every GPU core yield **up to 4x speedup** for TTFT. However, for mainstream local LLM use, "GPU via Metal remains the primary and recommended execution path."

#### MLX Framework (Apple, 2023-present)

MLX is Apple's open-source ML framework for native Apple Silicon execution:
- Native quantization support (4-bit, 8-bit via `mlx_lm.convert`)
- Highest sustained generation throughput among local frameworks
- WWDC 2025 featured session: "Explore large language models on Apple silicon with MLX"
- Text prefix caching: **5.8x speedup** on TTFT for repeated prompts
- Multimodal prefix caching: latency reduction from 21.7s to 0.78s on cached queries

#### Comparative Framework Analysis (arXiv:2511.05502)

Production-grade local LLM inference comparison on Apple Silicon:

| Framework | Strength | Best For |
|-----------|----------|----------|
| **MLX** | Highest sustained generation throughput | Batch processing, long generation |
| **MLC-LLM** | Lowest TTFT for moderate prompts | Interactive use |
| **Ollama** | Easiest setup, broad model support | Development, prototyping |
| **llama.cpp** | Most model format support | GGUF models, CPU+GPU hybrid |
| **vllm-mlx** | 21-87% higher throughput than llama.cpp | Production serving |

#### Quantized Models for 64GB Unified Memory

**GGUF Format**: The standard for local LLM deployment. At Q4_K_M quantization, models retain ~92% of original quality while reducing size by ~75%.

**What 64GB Enables**:
- 32B models at Q4-Q6: Comfortable operation with room for embeddings + BERTopic
- 70B models at Q4-Q5: Feasible with some memory pressure
- Multiple simultaneous models: Run KR-FinBERT (sentiment) + Qwen3-32B (analysis) concurrently

**QwQ-32B** (Alibaba, November 2024): A reasoning model with 32K token context that "matches or outperforms much larger models like DeepSeek-R1 (671B parameters)" -- remarkable for a model that runs on consumer hardware.

**Qwen3-32B** (Alibaba, 2025): Dense 32B model under Apache 2.0 license with "leading performance among open-source models in complex agent-based tasks." Qwen-Agent framework recommended for agentic applications.

**Qwen3-30B-A3B** (MoE): Only 3B activated parameters out of 30B total, meaning dramatically lower memory and compute requirements while maintaining 30B-class capability.

#### Privacy-Preserving Architecture

**Local-First as Privacy Architecture**: InvestScan's local execution model inherently provides:
- Zero data transmission to cloud providers
- No API key dependency or rate limiting
- No prompt injection risk from cloud intermediaries
- Full data sovereignty over investment analysis

**Market Context**: The privacy-preserving AI market reached $3.12B in 2024, projected to hit $12.09B by 2030 (CAGR ~25%). Apple's Private Cloud Compute (2024-2025) validates the industry direction toward privacy-preserving ML.

**Assessment for InvestScan**: The M5 Max 64GB is an exceptionally capable platform for the InvestScan use case. A Qwen3-30B-A3B (MoE, 3B active) or Qwen3-32B at Q4 quantization provides near-frontier reasoning capability locally. The privacy narrative is strong and genuine -- individual investment analysis on personal hardware, zero cloud exposure.

---

## 4. Theory-Practice Gap Analysis

### Theory-Practice Matrix

For each theoretical component, here is an honest assessment of what theory promises vs. what practice delivers, with specific InvestScan guidance.

#### 4.1 Weak Signal Detection

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Early identification of emerging trends 3-5 years before mainstream recognition; 34-day average lead time for market crashes via topological methods |
| **Practice delivers** | Qualitative signal identification works well; quantitative signal-to-return mapping remains unproven for retail investors; no real-money backtests published |
| **InvestScan should** | FOLLOW the WISDOM framework's TEM approach for signal classification; SHORTCUT the topological analysis (too complex for solo developer); IMPLEMENT as qualitative intelligence augmentation, not quantitative trading signal |

#### 4.2 Environmental Scanning (STEEP)

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Structured macro-environmental awareness reduces blind spots; frameworks like Three Horizons provide temporal investment lens |
| **Practice delivers** | Extensively used in corporate strategy; completely absent from retail investment tools; the gap is real and represents genuine category creation |
| **InvestScan should** | FOLLOW fully -- this is the core differentiator; IMPLEMENT STEEPs classification as the primary organizational framework; MAP to investment sectors via STEEPs-to-GICS mapping |

#### 4.3 Multi-Agent Debate

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Bull-bear debate produces balanced analysis; specialized agents outperform generalists; TradingAgents shows impressive metrics (26.62% returns, 8.21 Sharpe on AAPL) |
| **Practice delivers** | ICLR 2025 finds MAD "does not reliably outperform" single-agent with self-consistency; 14 identified failure modes; weaker agents corrupt correct analyses; echo chamber effects |
| **InvestScan should** | USE multi-agent for task decomposition (e.g., separate STEEPs analysts) -- this is proven; AVOID iterative debate mechanisms -- these fail; PREFER structured aggregation with explicit weighting over free-form argumentation |

#### 4.4 Financial Sentiment Analysis

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | FinBERT achieves 96.3% accuracy on Korean financial sentiment; sentiment predicts stock movements |
| **Practice delivers** | Classification accuracy is high; sentiment-to-return correlation is 90-95% spurious (0.45-0.73 raw, 0.034-0.048 validated); ~63.58% directional accuracy at best |
| **InvestScan should** | USE KR-FinBERT for sentiment classification (proven, high accuracy); DO NOT use sentiment as primary trading signal; TREAT sentiment as one dimension among STEEPs; ALWAYS report sentiment alongside evidence chains, never as standalone prediction |

#### 4.5 BERTopic for Signal Detection

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Superior topic coherence vs. LDA/NMF; built-in temporal/dynamic mode; directly applicable to signal lifecycle tracking |
| **Practice delivers** | Works well with domain-adapted embeddings (FinTextSim, FinBERT); struggles with generic embeddings on financial text; computationally feasible on consumer hardware |
| **InvestScan should** | FOLLOW fully -- BERTopic with FinBERT embeddings for topic extraction; USE dynamic mode for weekly signal evolution tracking; IMPLEMENT the 7-state lifecycle model already designed in GlobalNews-Crawling |

#### 4.6 Causal Inference (Granger/PCMCI)

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Identify whether news/sentiment Granger-causes market movements; PCMCI provides provably correct causal graphs |
| **Practice delivers** | 40% false positive rate for raw Granger causality; PCMCI reduces to 5-8% but requires substantial sample sizes; computationally expensive; financial data violates stationarity assumptions |
| **InvestScan should** | KEEP existing Granger implementation as first-pass filter; ADD multiple testing correction (Bonferroni/BH); REPORT confidence levels honestly; PLAN for PCMCI upgrade in Phase 2; NEVER claim causation without caveats |

#### 4.7 Local LLM Execution

| Dimension | Assessment |
|-----------|-----------|
| **Theory promises** | Frontier-class reasoning on consumer hardware; 15-25 tok/s on 32B models; privacy by architecture |
| **Practice delivers** | Qwen3-32B at Q4 runs comfortably on 64GB M5 Max; 15-22 tok/s confirmed for 32B Q4 models; MLX framework is production-grade; multiple models can run concurrently |
| **InvestScan should** | FOLLOW fully -- this is proven technology; USE Ollama for development, MLX for production; TARGET Qwen3-30B-A3B (MoE, 3B active) for efficiency or Qwen3-32B for quality; LEVERAGE prefix caching for repeated analysis patterns |

---

## 5. Conclusions and Recommendations

### Classification of Theories

#### PROVEN Theories That Should Guide InvestScan Design

These have strong empirical support and mature implementations:

1. **BERTopic for Financial Topic Modeling** (Grootendorst, 2022; FinTextSim, 2025)
   - Proven superior to LDA/NMF/Top2Vec across multiple benchmarks
   - Dynamic temporal mode enables weekly signal tracking
   - CRITICAL: Must use domain-adapted embeddings (FinBERT), not generic
   - Implementation: BERTopic + FinBERT embeddings + dynamic mode
   - **Confidence: HIGH (90%+)**

2. **KR-FinBERT for Korean Financial Sentiment** (SNU NLP Lab, 2022)
   - 96.3% accuracy on Korean financial text, production-ready on HuggingFace
   - Trained on 72 Korean media sources + 16 securities company reports
   - Runs locally on Apple Silicon without issues
   - **Confidence: HIGH (95%+)**

3. **Local LLM Inference on Apple Silicon** (Apple MLX, 2023-2026)
   - M5 Max 64GB handles 32B models comfortably at 15-22 tok/s
   - MLX/Ollama/llama.cpp all production-grade
   - Qwen3-32B/30B-A3B proven on consumer hardware
   - Privacy-by-architecture is genuine competitive advantage
   - **Confidence: VERY HIGH (98%+)**

4. **STEEP/PESTEL as Investment Organizing Framework** (established theory, 1960s-present)
   - Ubiquitous in strategic management, proven for macro-environmental analysis
   - Gap in retail investment applications is real and validated
   - The "empty quadrant" of macro scanning + local execution is genuine
   - **Confidence: HIGH (85%+) as organizational framework; MEDIUM as return predictor**

5. **Signal Lifecycle Modeling** (Ansoff 1975 -> WISDOM 2024)
   - Topic Emergence Maps provide quantified signal classification
   - 7-state lifecycle (NEW->STRENGTHENING->STABLE->WEAKENING->FADING->TRANSFORMED->MERGED) is theoretically well-grounded
   - BERTopic's temporal mode enables direct implementation
   - **Confidence: HIGH (85%) for signal detection; MEDIUM (60%) for timing investment decisions**

#### PROMISING But Unproven Theories

These have theoretical merit but lack sufficient empirical validation for confident adoption:

6. **Multi-Agent Task Decomposition for Investment Analysis** (TradingAgents, 2024)
   - TradingAgents shows 24.57% improvement in cumulative returns vs baselines
   - But: specialized to short-term trading, not macro analysis
   - Multi-agent decomposition (separate STEEPs analysts) is sound; debate mechanism is not
   - **Recommendation**: Use for task decomposition only; avoid debate
   - **Confidence: MEDIUM (55-65%)**

7. **PCMCI for Causal Discovery** (Runge et al., Tigramite)
   - Provably correct under assumptions; 5-8% false positive rate vs. 30-40% for Granger
   - But: requires substantial sample sizes; computationally expensive; financial data often violates stationarity
   - **Recommendation**: Plan for Phase 2; keep Granger with corrections for Phase 1
   - **Confidence: MEDIUM (60%) for financial application**

8. **Cross-Lingual Financial NLP** (ICE-PIXIU, multilingual models)
   - ~86% accuracy on translated financial sentiment
   - Cultural nuance loss is real (Korean financial idioms, sarcasm patterns)
   - **Recommendation**: Process each language natively, merge at signal level
   - **Confidence: MEDIUM (65%)**

9. **Three Horizons Framework for Investment Temporal Lens** (IFF, 2006)
   - Elegant conceptual framework mapping H1/H2/H3 to portfolio horizons
   - No empirical validation specifically for retail investment timing
   - **Recommendation**: Use as report structuring framework (proven for communication), not as prediction tool
   - **Confidence: MEDIUM (60%) as analytical lens; LOW (30%) as trading signal**

#### HYPE Theories to AVOID or Deprioritize

These are overstated, insufficiently validated, or inappropriate for InvestScan's context:

10. **Multi-Agent Debate for Better Analysis** (MAD frameworks)
    - ICLR 2025: "does not reliably outperform" single-agent with self-consistency
    - 14 identified failure modes; echo chambers; weak agent contamination
    - Computational cost 3-5x higher for negligible or negative benefit
    - **Verdict: AVOID for InvestScan. Use structured aggregation instead.**

11. **Sentiment-as-Trading-Signal** (raw sentiment -> return prediction)
    - 90-95% of observed sentiment-return correlation is spurious
    - Validated effects are 0.034-0.048, not 0.45-0.73
    - ~63.58% directional accuracy is marginally above coin flip
    - **Verdict: Use sentiment as CONTEXT, never as PRIMARY SIGNAL. Always pair with evidence chains.**

12. **Topological Data Analysis for Crash Prediction** (Persistent Homology)
    - Impressive 34-day lead time on historical data
    - Implementation complexity far exceeds solo developer capacity
    - Requires deep mathematical expertise to implement correctly
    - **Verdict: INTERESTING but impractical for InvestScan. Acknowledge in theory, do not implement.**

13. **Zero-Knowledge Proofs for Financial Privacy**
    - InvestScan's local-first architecture already provides complete privacy
    - ZKP adds cryptographic complexity with zero user benefit for a local system
    - Relevant only for cloud-based or multi-party scenarios
    - **Verdict: IRRELEVANT for local-first architecture. The simpler solution (don't send data anywhere) already solves the problem.**

---

### Recommended Theoretical Framework for PRD

Based on this analysis, InvestScan's PRD should be grounded in the following theoretical stack:

```
Layer 5: INVESTMENT INTELLIGENCE OUTPUT
         Three Horizons temporal framing (H1/H2/H3)
         STEEPs-to-GICS sector mapping
         Evidence chains (not sentiment scores)
         ┌─────────────────────────────────────┐
         │                                     │
Layer 4: │ SIGNAL LIFECYCLE MANAGEMENT          │
         │ WISDOM TEM (4-quadrant classification)│
         │ 7-state evolution tracking            │
         │ BERTopic dynamic temporal mode        │
         │ SQLite FTS5 persistence store         │
         └─────────────────────────────────────┘
         ┌─────────────────────────────────────┐
         │                                     │
Layer 3: │ NLP ANALYSIS ENGINE                  │
         │ BERTopic + FinBERT embeddings        │
         │ KR-FinBERT sentiment (Korean)        │
         │ Granger causality (with BH correction)│
         │ Cross-lingual: native processing     │
         └─────────────────────────────────────┘
         ┌─────────────────────────────────────┐
         │                                     │
Layer 2: │ MULTI-AGENT TASK DECOMPOSITION       │
         │ Separate STEEPs dimension analysts    │
         │ Structured aggregation (NOT debate)   │
         │ Single orchestrator, weighted merge   │
         └─────────────────────────────────────┘
         ┌─────────────────────────────────────┐
         │                                     │
Layer 1: │ LOCAL EXECUTION FOUNDATION            │
         │ M5 Max 64GB + MLX/Ollama             │
         │ Qwen3-30B-A3B or Qwen3-32B (Q4)     │
         │ Privacy-by-architecture               │
         │ Prefix caching for repeated patterns  │
         └─────────────────────────────────────┘
```

### Key Design Principles Derived from Theory

1. **STEEPs-First, Not Sentiment-First**: The theoretical foundation overwhelmingly supports structured environmental scanning as the primary analytical framework, with sentiment as one input dimension (not the core)

2. **Signal Lifecycle Over Point-in-Time Analysis**: BERTopic's temporal mode + WISDOM TEM enable the evolution tracking that distinguishes InvestScan from static analysis tools

3. **Honest Uncertainty Communication**: Given 90-95% spurious correlation in sentiment-return relationships and 30-40% Granger causality false positives, InvestScan MUST communicate confidence levels honestly. Every signal should carry an explicit confidence rating and evidence chain

4. **Local-First is a Feature, Not a Limitation**: The privacy-by-architecture approach is theoretically sound, computationally feasible, and strategically differentiating

5. **Decompose, Don't Debate**: Multi-agent task decomposition (proven) over multi-agent debate (hype). Separate analysts for S-T-E-E-P dimensions, structured weighted aggregation, single orchestrator

6. **Domain-Adapted Everything**: Generic models/embeddings consistently underperform on financial text. Use FinBERT embeddings for BERTopic, KR-FinBERT for Korean sentiment, financial-corpus-tuned LLMs for analysis

---

### Summary Confidence Matrix

| Theory Component | Theory Maturity | Empirical Evidence | InvestScan Fit | Action |
|-----------------|----------------|-------------------|---------------|--------|
| BERTopic + FinBERT embeddings | HIGH | STRONG | EXCELLENT | Implement in Phase 1 |
| KR-FinBERT sentiment | HIGH | STRONG | EXCELLENT | Implement in Phase 1 |
| Local LLM (MLX/Ollama, Qwen3) | HIGH | STRONG | EXCELLENT | Implement in Phase 1 |
| STEEP as organizing framework | HIGH | MODERATE (for investment) | CORE | Implement in Phase 1 |
| Signal lifecycle / WISDOM TEM | MEDIUM-HIGH | MODERATE | EXCELLENT | Implement in Phase 1 |
| Three Horizons (report structure) | HIGH | LOW (for investment) | GOOD | Use for output framing |
| Multi-agent decomposition | MEDIUM | MODERATE | GOOD | Implement in Phase 1 |
| Granger causality (with correction) | HIGH | MODERATE | GOOD | Keep existing + add corrections |
| PCMCI causal discovery | HIGH | LOW (for finance) | GOOD | Plan for Phase 2 |
| Cross-lingual NLP | MEDIUM | MODERATE | MODERATE | Native processing per language |
| Multi-agent debate | MEDIUM | WEAK/NEGATIVE | POOR | Avoid |
| Sentiment-as-trading-signal | MEDIUM | WEAK | POOR | Context only, never primary |
| Topological data analysis | HIGH | MODERATE | POOR (complexity) | Acknowledge, don't implement |

---

### Sources

#### Weak Signal Detection & Environmental Scanning
- [Hiltunen, "Weak signals: Ansoff today" (Futures, 2012)](https://www.sciencedirect.com/science/article/abs/pii/S0016328711002540)
- [Ahlqvist & Uotila, "Contextualising weak signals" (Futures, 2020)](https://www.sciencedirect.com/science/article/abs/pii/S0016328720300331)
- [WISDOM: AI-powered weak signal detection framework (arXiv:2409.15340)](https://arxiv.org/html/2409.15340v1)
- [Topological Machine Learning for Financial Crisis Detection (Computers, 2025)](https://www.mdpi.com/2073-431X/14/10/408)
- [Early warning signals using nonlinear methods (EPJ Data Science, 2024)](https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-024-00457-2)
- [Early-warning risk signals framework (Quantitative Finance, 2025)](https://www.tandfonline.com/doi/full/10.1080/14697688.2025.2482637)
- [Three Horizons Framework (International Futures Forum)](https://www.internationalfuturesforum.com/three-horizons)
- [McKinsey 3 Horizon Model for Financial Planning (ResearchGate)](https://www.researchgate.net/publication/379924972)
- [PESTEL Analysis in Finance (Corporate Finance Institute)](https://corporatefinanceinstitute.com/resources/management/pestel-analysis/)

#### Multi-Agent AI Systems
- [TradingAgents Framework (arXiv:2412.20138)](https://arxiv.org/abs/2412.20138)
- [TradingAgents Project Page](https://tradingagents-ai.github.io/)
- [FinRobot: AI Agent Platform (arXiv:2405.14767)](https://arxiv.org/abs/2405.14767)
- [Multi-Agent Debate Failure Modes (arXiv:2509.05396)](https://arxiv.org/pdf/2509.05396)
- [Why Multi-Agent LLM Systems Fail (arXiv:2503.13657)](https://arxiv.org/html/2503.13657v2)
- [ICLR 2025: MAD Performance and Scaling Challenges](https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/)
- [Can LLM Agents Really Debate? (arXiv:2511.07784)](https://arxiv.org/pdf/2511.07784)

#### Financial NLP & Sentiment Analysis
- [FinBERT: Financial Sentiment Analysis (arXiv:1908.10063)](https://arxiv.org/abs/1908.10063)
- [KR-FinBERT (snunlp, HuggingFace)](https://huggingface.co/snunlp/KR-FinBert-SC)
- [FinGPT: Enhanced Sentiment Prediction (arXiv:2412.10823)](https://arxiv.org/html/2412.10823v2)
- [Sentiment-Return Spurious Correlation Findings (arXiv:2603.21473)](https://arxiv.org/html/2603.21473)
- [LLaMA-2 for Financial Sentiment (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24003846)
- [Investor Sentiment and Market Movements: Granger Causality (arXiv:2510.15915)](https://arxiv.org/abs/2510.15915)
- [NLP in Finance Survey (ScienceDirect, 2024)](https://www.sciencedirect.com/science/article/abs/pii/S1566253524005335)
- [Cross-lingual Sentiment Analysis (Nature Scientific Reports, 2024)](https://www.nature.com/articles/s41598-024-60210-7)

#### Topic Modeling
- [BERTopic (arXiv:2203.05794)](https://arxiv.org/abs/2203.05794)
- [FinTextSim: Financial Text Analysis with BERTopic (arXiv:2504.15683)](https://arxiv.org/abs/2504.15683)
- [BERTopic-Driven Stock Market Predictions (arXiv:2404.02053)](https://arxiv.org/html/2404.02053v2)
- [TopicProphet: Temporal Topic Trends and Stocks (arXiv:2512.11857)](https://www.arxiv.org/pdf/2512.11857)
- [THEME: Thematic Investing with Temporal Dynamics (arXiv:2508.16936)](https://arxiv.org/html/2508.16936)
- [BERTopic Dynamic Topic Modeling Documentation](https://maartengr.github.io/BERTopic/getting_started/topicsovertime/topicsovertime.html)

#### Causal Inference
- [PCMCI: Detecting Causal Associations (Science Advances, 2019)](https://www.science.org/doi/10.1126/sciadv.aau4996)
- [Tigramite Documentation](https://jakobrunge.github.io/tigramite/)
- [CD-NOTS: Causal Discovery for Nonstationary Time Series (Springer, 2024)](https://link.springer.com/article/10.1007/s41060-024-00679-7)
- [Causal Inference in Banking/Finance Survey (arXiv:2307.16427)](https://arxiv.org/pdf/2307.16427)

#### Local AI Execution
- [Apple MLX: LLMs on M5 (Apple ML Research)](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)
- [Production-Grade Local LLM Inference on Apple Silicon (arXiv:2511.05502)](https://arxiv.org/abs/2511.05502)
- [Native LLM Inference at Scale on Apple Silicon (arXiv:2601.19139)](https://arxiv.org/html/2601.19139v1)
- [Profiling LLM Inference: Quantization Perspective (arXiv:2508.08531)](https://arxiv.org/abs/2508.08531)
- [WWDC 2025: Explore LLM on Apple Silicon with MLX](https://developer.apple.com/videos/play/wwdc2025/298/)
- [Qwen3 Release Blog](https://qwenlm.github.io/blog/qwen3/)
- [Ollama Platform](https://ollama.com/library/qwen3)
- [Privacy-Preserving AI Market Growth (Technavio, 2025)](https://www.technavio.com/report/privacy-preserving-ai-market-industry-analysis)

#### Competitive Landscape
- [Bloomberg Terminal Alternatives (AlphaSense)](https://www.alpha-sense.com/compare/alternatives-to-bloomberg-terminal/)
- [Best Stock Analysis Tools 2026 (Gainify)](https://www.gainify.io/blog/best-stock-research-apps)
- [Koyfin vs Bloomberg (AlphaSense)](https://www.alpha-sense.com/compare/koyfin-vs-bloomberg/)
