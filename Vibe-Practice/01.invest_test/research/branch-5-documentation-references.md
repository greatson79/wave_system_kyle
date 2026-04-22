# Branch 5.1 & 5.2: Documentation & Implementation References for InvestScan PRD

> **TWO Documentation & Implementation Reference Experts**
> **Date**: 2026-03-28
> **Context**: InvestScan integrates EnvironmentScan + GlobalNews-Crawling + financial data + AI models to produce investment directions
> **Scope**: What existing documentation, patterns, and reference implementations should the PRD reference?

---

## BRANCH 5.1: MODERN References (Agentic Workflow Patterns, 2024-2026)

### Expert 1: Modern/Cutting-Edge Documentation Researcher

**Research Method**: 12 targeted web searches across agentic workflows, financial AI implementations, local-first architecture, and API integration patterns, cross-referenced with the user's existing AgenticWorkflow framework and 27 research documents already produced in Rounds 1-4.

---

### A. Agentic Workflow Documentation

#### A1. Claude Code workflow.md Best Practices (2025-2026)

The Claude Code ecosystem has converged on a clear set of documentation and workflow practices that InvestScan should both follow and reference:

**Boris Cherny's CLAUDE.md Golden Rule** (Anthropic, Creator of Claude Code):
The creator's own CLAUDE.md is only ~100 lines. His golden rule: "Anytime we see Claude do something incorrectly, we add it to CLAUDE.md so it doesn't repeat next time." This is a living document, not a one-time setup. InvestScan's PRD should adopt this principle for its configuration files -- `config/investscan.yaml` should be a living reference that evolves with actual pipeline failures.

**Architecture Pattern Convergence**:
All major Claude Code workflows converge on: **Research -> Plan -> Execute -> Review -> Ship**. The single biggest mistake is letting the agent jump straight into coding without a plan. InvestScan's pipeline (Collect -> Normalize -> Synthesize -> Report) is a domain-specific expression of this universal pattern. The PRD should explicitly map InvestScan pipeline stages to this canonical workflow structure.

**Context Management as First-Class Concern**:
Every file Claude reads, every command output, every message consumes context window capacity. When it fills, the agent starts forgetting earlier instructions. The fix: use subagents for research, start fresh sessions for new tasks, and avoid dumping information "just in case." For InvestScan, this means the workflow.md must document clear context boundaries between pipeline stages -- the normalizer does not need to understand the report template.

**Memory Continuity Pattern**:
A dedicated `memory.md` document captures current state and functions as a continuity layer across sessions. InvestScan's `.claude/state.yaml` (the SOT from AgenticWorkflow's DNA) serves this identical function. The PRD should document this as: "InvestScan inherits the SOT pattern from AgenticWorkflow. Pipeline state, step completion, output paths, and error history are tracked in `.claude/state.yaml`. Only the orchestrator writes."

**Source**: [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows), [claude-code-best-practice (GitHub)](https://github.com/shanraisshan/claude-code-best-practice), [Claude Code Ultimate Guide (GitHub)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide), [Claude Code Best Practices 2026 (eesel AI)](https://www.eesel.ai/blog/claude-code-best-practices), [Claude Code Creator Workflow (MindWiredAI)](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/)

#### A2. Multi-Agent Orchestration Patterns (2025-2026)

The agentic workflow landscape in 2025-2026 has crystallized around four primary orchestration patterns, each documented by major cloud providers and framework authors:

| Pattern | Description | InvestScan Applicability | Reference |
|---------|-------------|-------------------------|-----------|
| **Supervisor/Conductor** | A central orchestrator delegates to specialized sub-agents, collects results, and synthesizes | **HIGH** -- InvestScan's pipeline is inherently sequential with a single orchestrator | AWS Prescriptive Guidance, LangGraph |
| **Swarm** | Multiple agents with overlapping capabilities self-organize around tasks | LOW -- InvestScan's pipeline has clear stage boundaries | CrewAI documentation |
| **Pipeline** | Sequential stages where output of stage N becomes input of stage N+1 | **HIGH** -- This IS InvestScan's architecture (Collect -> Normalize -> Synthesize -> Report) | dbt Labs ETL patterns |
| **Adaptive Agent Network** | Dynamic routing based on task characteristics | MEDIUM -- Could apply to signal routing (route financial signals to financial synthesizer, tech signals to tech synthesizer) | Kore.ai, Vellum |

**AWS Prescriptive Guidance Pattern (2025)**: AWS documented "workflow orchestration agents" that "manage and coordinate multistep tasks across distributed systems. Rather than reasoning and acting in isolation, these agents delegate work to subagents or other systems, maintain execution context, and adapt based on intermediate results." This is precisely InvestScan's orchestration model. The PRD should reference this pattern: the CLI orchestrator maintains execution context (checkpoint/resume via `PipelineState` JSON), delegates to Python modules (normalizers, synthesizer, report generator), and adapts based on intermediate results (skip GlobalNews if its output is stale).

**AgenticWorkflow's Own Framework** (the user's parent system):
InvestScan inherits the complete AgenticWorkflow genome. Key patterns already documented in the parent framework that InvestScan's PRD should reference by inheritance, not re-document:

1. **3-Phase Structure**: Research -> Planning -> Implementation (maps to InvestScan's Collect -> Synthesize -> Report)
2. **SOT Pattern**: `.claude/state.yaml` -- single writer (Orchestrator only)
3. **4-Layer QA**: L0 Anti-Skip -> L1 Verification -> L1.5 pACS -> L2 Adversarial Review
4. **P1 Hallucination Prevention**: Deterministic validation scripts
5. **P2 Expert Delegation**: Specialized sub-agents for each task
6. **Context Preservation**: Snapshot + Knowledge Archive + RLM restoration

The workflow template (`workflow-template.md`) specifies: Overview, Inherited DNA (Parent Genome), Research Phase, Planning Phase, Implementation Phase, with each step containing Pre-processing, Agent, Verification, Task, Output, Translation, and Post-processing fields.

**Source**: [AWS Agentic AI Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/introduction.html), [LangChain Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [Agentic Workflows 2026 Guide (Vellum)](https://vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns), [CrewAI](https://crewai.com/)

#### A3. How Other Projects Structure Their workflow.md

From examination of the AgenticWorkflow ecosystem and open-source Claude Code projects:

**Standard workflow.md Structure** (from `workflow-template.md`):
```
1. Overview (Input, Output, Frequency, Autopilot mode, pACS)
2. Inherited DNA (Constitutional Principles, Domain-Specific Gene Expression)
3. Research Phase (data collection, validation)
4. Planning Phase (analysis, design decisions)
5. Implementation Phase (execution, quality gates)
6. Post-processing (cleanup, archival)
```

**InvestScan-Specific Adaptation** (from Branch 5.1 research):
The existing Branch 5 research already produced two workflow.md approaches:
- **Deep Integration** (5.1): Full workflow.md with Inherited DNA, Phase 1-4 pipeline stages, human checkpoints, and pACS ratings at each stage (~460 LOC of workflow orchestration)
- **Simple Integration** (5.2): Shell orchestrator calling Python modules, minimal workflow.md that is mostly a README

The Phase 2 discussion concluded that the Deep workflow.md approach "duplicates what the Python CLI already does" and creates "ambiguity about which is the SOT." The recommended pattern: **workflow.md as pipeline documentation** (what the pipeline does and why), **Python CLI as pipeline execution** (how the pipeline runs).

---

### B. Financial AI Implementation References

#### B1. FinGPT (AI4Finance Foundation)

**Architecture**: FinGPT is structured as a 4-layer stack: Data Source -> Data Engineering -> LLMs -> Applications. This maps almost 1:1 to InvestScan:

| FinGPT Layer | InvestScan Equivalent | Notes |
|-------------|----------------------|-------|
| Data Source | EnvScan + GlobalNews output directories | FinGPT crawls from scratch; InvestScan reads from existing production systems |
| Data Engineering | Signal Normalization Layer (`normalize_signals.py`) | FinGPT focuses on fine-tuning data prep; InvestScan focuses on schema harmonization |
| LLMs | Claude API (for EnvScan agent reasoning) + Local ML (SBERT, BERTopic for GlobalNews) | FinGPT fine-tunes open models; InvestScan uses pre-trained models |
| Applications | Weekly Investment Direction Report + Decision Journal | FinGPT targets robo-advising/algo trading; InvestScan targets human decision support |

**Key Pattern to Adopt**: FinGPT's data-centric approach -- "providing researchers and practitioners with accessible and transparent resources" -- aligns with InvestScan's evidence chain philosophy. The PRD should reference FinGPT's data pipeline architecture as a validated pattern: external data -> normalization -> model inference -> actionable output.

**Key Pattern to Reject**: FinGPT uses fine-tuned LLMs (llama2-7b/13b, chatglm2-6B) for financial reasoning. InvestScan should NOT fine-tune models. The system's value comes from data synthesis (cross-domain signal correlation), not model specialization. This is a deliberate architectural divergence that the PRD should document explicitly.

**Source**: [FinGPT GitHub](https://github.com/AI4Finance-Foundation/FinGPT), [FinGPT Paper (arXiv:2306.06031)](https://arxiv.org/abs/2306.06031), [AI4Finance Foundation](https://ai4finance.org/)

#### B2. TradingAgents (Tauric Research)

**Architecture**: TradingAgents mirrors a real-world trading firm with distinct roles: fundamental analysts, sentiment analysts, technical analysts, researchers (Bull and Bear), traders, and risk managers. Built on LangGraph with multi-provider LLM support (GPT-5.x, Gemini 3.x, Claude 4.x as of v0.2.2, March 2026).

**Patterns Relevant to InvestScan**:

| TradingAgents Pattern | InvestScan Application | Adopt/Reject |
|----------------------|----------------------|--------------|
| Bull vs Bear researcher debate | Signal convergence detection (signals appearing in BOTH EnvScan and GlobalNews scored higher) | **Adopt conceptually** -- not as agent debate, but as cross-source validation scoring |
| Multi-provider LLM support | Claude API for agent reasoning + local SBERT/BERTopic | **Adopt partially** -- InvestScan already uses this pattern via its source systems |
| Risk management as separate agent | Risk/Opportunity Matrix section in weekly report | **Adapt** -- not a separate agent, but a dedicated report section |
| Real-time trading execution | N/A -- InvestScan produces direction, not trades | **Reject** -- out of scope |

**Critical Lesson**: TradingAgents' architecture is designed for high-frequency, real-time decision-making. InvestScan's weekly batch cadence is fundamentally different. The PRD should explicitly state: "InvestScan is NOT a trading system. It produces weekly directional intelligence reports. Automated trade execution is out of scope permanently."

**Source**: [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents), [TradingAgents Documentation](https://tradingagents-ai.github.io/)

#### B3. PRISM-INSIGHT

**Architecture**: 13+ specialized AI agents analyze Korean (KOSPI/KOSDAQ) and US (NYSE/NASDAQ) stocks. Key capabilities: surge stock detection, analyst-grade reports, trading simulation via KIS API. Uses pykrx (KR) and yfinance (US) for market data.

**Patterns Relevant to InvestScan**:

| PRISM-INSIGHT Pattern | InvestScan Application | Adopt/Reject |
|----------------------|----------------------|--------------|
| pykrx + yfinance for KR/US market data | Phase 2 feature: KRX market data snapshot for signal-vs-market comparison | **Adopt** -- pykrx is battle-tested, PRISM-INSIGHT v2.4.0 demonstrates production viability |
| 13 specialized AI agents | InvestScan's simpler 4-module pipeline | **Reject** -- InvestScan's solo-dev constraint precludes 13-agent complexity |
| Firebase Bridge integration | Local-only architecture | **Reject** -- InvestScan is local-first by design |
| Direct API prefetch (replacing MCP tool calls) | Direct file reads from source system output directories | **Already aligned** -- InvestScan's file-based IPC is simpler than API calls |

**Critical Competitive Insight** (from Round 2 research): PRISM-INSIGHT, with its 14 AI agents and 408.6% simulated returns (already featured on GeekNews), is the closest competitive threat. But it operates in the "microscope" space (individual stock analysis), while InvestScan occupies the "telescope" space (macro signal synthesis). The PRD should reference this positioning: "PRISM-INSIGHT answers 'which stock?' InvestScan answers 'which direction and why?'"

**Source**: [PRISM-INSIGHT GitHub](https://github.com/dragon1086/prism-insight), [PRISM-INSIGHT Dashboard](https://analysis.stocksimulation.kr/)

#### B4. Signal-to-Direction Mapping Patterns Across Financial AI Projects

Across FinGPT, TradingAgents, and PRISM-INSIGHT, signal-to-direction mapping follows three distinct patterns:

| Pattern | Used By | Mechanism | Suitability for InvestScan |
|---------|---------|-----------|---------------------------|
| **LLM-based classification** | FinGPT | Fine-tuned model directly outputs sentiment/direction | LOW -- requires fine-tuning, InvestScan lacks training data |
| **Agent debate** | TradingAgents | Bull and Bear agents argue, trader synthesizes | MEDIUM -- philosophically appealing but operationally complex for solo dev |
| **Rule-based scoring with ML features** | PRISM-INSIGHT | Quantitative features (burst_score, novelty_score) fed to scoring rules | **HIGH** -- InvestScan already has these features from GlobalNews pipeline |

**Recommended InvestScan Pattern**: Hybrid rule-based + feature-weighted scoring. The synthesis module takes:
- `confidence` (normalized from pSST/signal_layer)
- `burst_score` (from GlobalNews or derived from frequency for EnvScan)
- `novelty_score` (from GlobalNews or derived from first-appearance for EnvScan)
- `cross_source_count` (number of source systems where similar signal appears)
- STEEPs-to-GICS mapping (rule-based)

And outputs: direction (bullish/bearish/neutral) + conviction (0.0-1.0) per sector. No LLM in the synthesis loop. Deterministic. Testable. Auditable.

---

### C. Local-First AI Application Patterns

#### C1. Architecture Principles (2025-2026)

The local-first AI movement has matured significantly. Key principles applicable to InvestScan:

**Principle 1: Device as Primary Source of Truth**
"Offline-first design flips the architecture: the local device becomes the primary source of truth, and the network becomes a background optimization." InvestScan is already aligned: all processing runs on MacBook M5 Max 64GB. EnvScan uses Claude API for agent reasoning (requires network), but GlobalNews is entirely local (SBERT, BERTopic, Prophet -- all local inference). The normalization, synthesis, and report generation layers are 100% local.

**Principle 2: Hybrid Architecture**
"The future isn't purely local or purely cloud. The best systems use local models for immediate response and privacy-sensitive tasks while opportunistically leveraging cloud capabilities when available." InvestScan's architecture is precisely this: Claude API for high-reasoning tasks (EnvScan agent analysis), local ML for high-throughput tasks (GlobalNews NLP pipeline), local Python for deterministic tasks (normalization, synthesis, report).

**Principle 3: Data Sovereignty**
InvestScan processes investment-sensitive data. No signal data, no synthesized directions, no investment decisions leave the local machine. The PRD should document this as a non-negotiable constraint: "All InvestScan data remains on the local machine. Cloud APIs are used only for LLM reasoning (via EnvScan's Claude API calls), never for data storage or signal transmission."

**Performance Benchmark**: Modern local-first AI applications achieve 100-600ms latency vs 800-3000ms cloud. For InvestScan's weekly batch pipeline (3.5+ hours total), latency per inference call is irrelevant. The batch nature eliminates the primary concern (latency) while preserving the primary benefit (data sovereignty).

**Source**: [Building Offline-First AI Applications 2026 (PracticalWebTools)](https://www.practicalwebtools.com/blog/building-offline-first-ai-applications-guide-2026), [Definitive Guide to Local-First AI (SitePoint)](https://www.sitepoint.com/definitive-guide-local-first-ai-2026/), [Local-First Software Patterns 2026 (Tech-Champion)](https://tech-champion.com/software-engineering/the-local-first-manifesto-why-the-cloud-is-losing-its-luster-in-2026/)

#### C2. External Data Integration for Local-First Apps

How do local-first applications handle external data integration?

| Pattern | Description | InvestScan Implementation |
|---------|-------------|--------------------------|
| **Sync-on-demand** | Fetch external data only when explicitly requested | `investscan run` triggers EnvScan + GlobalNews execution |
| **Cache-then-process** | Download data, cache locally, process from cache | File-based IPC: source systems write to their output dirs, InvestScan reads from cache |
| **Stale-data detection** | Check if cached data is fresh enough before processing | Pre-flight check in orchestrator: `if output_age > 7_days: warn("stale data")` |
| **Graceful degradation** | Function with partial data if some source is unavailable | If GlobalNews output missing: generate EnvScan-only report with reduced confidence |

---

### D. API Integration Best Practices Documentation

#### D1. External API Dependencies in a PRD

Based on research into PRD documentation standards for 2025-2026, an InvestScan PRD should document external dependencies in a structured format:

**Recommended PRD Section: External Dependencies Matrix**

| Dependency | Type | Required For | Failure Mode | Degradation Strategy | Rate Limit | Auth Method |
|-----------|------|-------------|--------------|---------------------|------------|-------------|
| Claude API | Cloud LLM | EnvScan agent reasoning | Pipeline continues with GlobalNews-only data | Reduced confidence scores, EnvScan-only report | Per-key rate limits | API key in `.env` |
| FRED API | REST API | Economic indicators (Phase 2) | Report omits macro economic section | Use cached last-known values | 120 req/min, 500K/day | API key |
| pykrx | Web scraping | KRX market data snapshot (Phase 2) | Report omits market comparison | Cache last-known KOSPI/KOSDAQ values | Implicit (web scraping) | None |
| yfinance | Web API | US market data (Phase 2) | Report omits US market context | Cache last-known S&P 500 data | Yahoo rate limits | None |
| ArXiv API | REST API | EnvScan WF1 signal collection | Fewer academic signals that week | Previous week's academic signals carried forward | None documented | None |
| Naver News | Web scraping | EnvScan Korean news signals | Fewer Korean-language signals | GlobalNews Korean sources as fallback | Implicit | None |

#### D2. API Degradation Handling Patterns

The PRD should document a **Degradation Matrix** showing system behavior when each dependency fails:

**Tier 1 (Pipeline continues normally)**:
- pykrx down -> market snapshot section shows "Data unavailable, using last cached values from {date}"
- yfinance down -> same degradation as pykrx
- FRED down -> economic indicators show cached values with staleness warning

**Tier 2 (Pipeline continues with reduced quality)**:
- ArXiv API down -> EnvScan produces fewer academic signals -> normalization layer marks report as "reduced academic coverage"
- Naver News down -> EnvScan produces fewer Korean signals -> report notes "reduced Korean signal coverage"

**Tier 3 (Pipeline partially blocked)**:
- Claude API down -> EnvScan cannot run -> InvestScan runs GlobalNews-only mode with explicit warning
- GlobalNews venv broken -> GlobalNews cannot run -> InvestScan runs EnvScan-only mode

**Tier 4 (Pipeline fully blocked)**:
- Both Claude API AND GlobalNews broken -> Pipeline aborts with clear error message

**Implementation Pattern**: Circuit breaker with exponential backoff. From research: "When an API is completely degraded, if you receive continuous 429s or 5xx errors, your system should 'trip' a circuit breaker." For InvestScan's weekly batch, the circuit breaker is simpler: try once, if fail, use cached data, log warning, continue.

**Source**: [API Rate Limiting at Scale (Gravitee)](https://www.gravitee.io/blog/rate-limiting-apis-scale-patterns-strategies), [Best Practices for API Rate Limits (Truto)](https://truto.one/blog/best-practices-for-handling-api-rate-limits-and-retries-across-multiple-third-party-apis), [FRED API Errors](https://fred.stlouisfed.org/docs/api/fred/errors.html)

#### D3. Rate Limiting and Retry Patterns for Financial Data

| API | Rate Limit | Retry Strategy | InvestScan Implementation |
|-----|-----------|----------------|--------------------------|
| Claude API | Per-key, tier-dependent | Exponential backoff (already in EnvScan) | Inherited from EnvScan -- no new code needed |
| FRED API | 120 requests/min, 500K requests/day | Not needed (InvestScan makes ~5 requests/week) | Simple try/except with cache fallback |
| pykrx | Implicit (KRX web scraping) | 1-second delay between requests | `time.sleep(1)` between calls |
| yfinance | Yahoo's undocumented limits | 2-second delay between ticker groups | `time.sleep(2)` between batch calls |

**Key Insight**: InvestScan's weekly batch cadence makes rate limiting a non-issue. The entire pipeline makes fewer than 200 external API calls per week. The PRD should document this explicitly: "Rate limiting is a non-concern for InvestScan's weekly execution cadence. Simple retry-once-with-cache-fallback is sufficient."

#### D4. Credential Management for Local Tools

Based on research into Python credential management best practices (2025):

| Approach | Security Level | Complexity | InvestScan Recommendation |
|----------|---------------|------------|--------------------------|
| `.env` file + python-dotenv | Medium | Low | **Phase 1 (Months 1-3)** -- simplest path |
| macOS Keychain via `keyring` library | High | Medium | **Phase 2 (Months 4-6)** -- upgrade when stable |
| HashiCorp Vault / AWS Secrets Manager | Very High | High | **Never** -- overkill for local solo tool |

**Recommended Implementation**:
```
Phase 1: .env file in project root (gitignored)
  CLAUDE_API_KEY=sk-ant-...
  FRED_API_KEY=...

Phase 2: keyring migration
  keyring.set_password("investscan", "claude_api", "sk-ant-...")
  keyring.get_password("investscan", "claude_api")
```

The PRD should document: "Credentials are stored in `.env` (Phase 1) with planned migration to macOS Keychain via `keyring` library (Phase 2). The `.env` file is gitignored. No credentials are hardcoded in source code. No credentials leave the local machine."

**Source**: [Python Secrets Management (GitGuardian)](https://blog.gitguardian.com/how-to-handle-secrets-in-python/), [Managing Secrets with .env (KDnuggets)](https://www.kdnuggets.com/managing-secrets-and-api-keys-in-python-projects-env-guide), [Python Keyring (Medium)](https://medium.com/@forsytheryan/securely-storing-credentials-in-python-with-keyring-d8972c3bd25f)

---

## BRANCH 5.2: CLASSICAL References (Proven Patterns, 5+ Years)

### Expert 2: Classical/Foundational Documentation Researcher

**Research Method**: Examination of established software engineering patterns, ETL documentation standards, Unix integration philosophy, and financial data integration approaches proven over 5+ years, cross-referenced with the project's existing classical theory analysis (Round 2).

---

### A. ETL Pipeline Documentation Standards

#### A1. How Traditional ETL Projects Document External Integrations

The ETL world has 20+ years of documentation standards that InvestScan should inherit. The core principle: **document the contract, not the implementation**.

**Standard ETL Documentation Sections** (relevant to InvestScan PRD):

1. **Source System Inventory**
   - For each source: name, owner, data format, refresh frequency, SLA, contact
   - InvestScan equivalent: EnvScan (JSON, ~weekly, Claude API-dependent) and GlobalNews (Parquet/SQLite, ~weekly, fully local)

2. **Data Contract Specification**
   - Schema definition for each source system's output
   - Field-level mapping from source to target
   - Data type conversions and validation rules
   - InvestScan equivalent: The 6 source formats documented in Branch 1 (WF1 database.json, WF1 output, WF4 database.json, WF4 priority-ranked, WF4 evolution, GlobalNews Parquet)

3. **Data Quality Rules**
   - Completeness rules (which fields are required vs optional)
   - Validity rules (allowed values, ranges, formats)
   - Consistency rules (cross-field validation)
   - InvestScan equivalent: The 10 contract tests in Branch 4.1 that guard schema parsing

4. **Error Handling Matrix**
   - For each source field: what happens when it's null, malformed, or unexpected
   - InvestScan equivalent: "crash loud on contract violation, graceful degradation everywhere else"

5. **Data Lineage Documentation**
   - Where does each field in the final output come from?
   - InvestScan equivalent: Evidence chain in the weekly report (which source signals contributed to each sector direction)

**Medallion Architecture (2025 Industry Standard)**:
68% of cloud-first enterprises have adopted the medallion architecture pattern (Bronze -> Silver -> Gold layers). InvestScan's pipeline follows an equivalent pattern:

| Medallion Layer | InvestScan Equivalent | Description |
|----------------|----------------------|-------------|
| **Bronze** (raw) | Source system output directories | Raw EnvScan JSON + GlobalNews Parquet, untouched |
| **Silver** (cleaned) | `UnifiedSignal` frozen dataclasses | Schema-normalized, validated, deduplicated signals |
| **Gold** (business) | Weekly Investment Direction Report | Synthesized, sector-mapped, direction-scored output |

The PRD should reference this mapping: "InvestScan follows the medallion architecture pattern. Source system outputs are Bronze (read-only). Normalized `UnifiedSignal` objects are Silver (validated, typed). The weekly report is Gold (business-ready)."

**Source**: [ETL Pipeline Data Lineage (Meegle)](https://www.meegle.com/en_us/topics/etl-pipeline/etl-pipeline-data-lineage), [Data Lineage in ETL (Secoda)](https://www.secoda.co/blog/data-lineage-in-etl-process), [Track Data Lineage in ETL (Airbyte)](https://airbyte.com/data-engineering-resources/track-data-lineage-etl-pipelines), [Data Lineage 2025 (Dagster)](https://dagster.io/learn/data-lineage)

#### A2. Data Lineage Tracking Patterns

InvestScan's evidence chain feature IS data lineage. The PRD should frame it this way:

**Forward Lineage** (source -> report):
- Signal `TC-20260325-001` from EnvScan WF1 -> normalized as `IS-20260325-0042` -> mapped to Technology sector -> contributed to "bullish Technology" direction at 72% conviction -> appears in weekly report Section 2 as supporting evidence

**Backward Lineage** (report -> source):
- Weekly report says "Bullish Technology, 72% conviction" -> click into evidence chain -> see `IS-20260325-0042` -> trace back to TechCrunch article about Kleiner Perkins AI investment

**Implementation Pattern**: Each `UnifiedSignal` carries `source_signal_id` (original ID from source system) and `source_system` (envscan/gnews). The report template includes evidence chains that link back to these IDs. This is sufficient lineage for a solo-dev weekly tool.

#### A3. Schema Versioning for External Data Sources

The most dangerous moment in InvestScan's lifecycle is when EnvScan or GlobalNews changes its output format. Classical ETL addresses this with:

**Schema Registry Pattern** (simplified for InvestScan):
```python
# investscan/schema.py
SCHEMA_VERSION = "1.0.0"

@dataclass(frozen=True)
class UnifiedSignal:
    schema_version: str  # Embedded in every signal object
    ...
```

**Contract Test Pattern** (already adopted in Branch 4):
The 10 schema contract tests are InvestScan's schema versioning mechanism. When EnvScan changes `preliminary_category` from `"T"` to `"T_Technological"` (both of which already exist), the contract test catches it. The PRD should document: "Schema compatibility is verified by 10 contract tests that run before every pipeline execution. If any test fails, the pipeline aborts with a clear error identifying which source system changed its format."

---

### B. Financial Data Integration Patterns

#### B1. Bloomberg Terminal Integration Patterns (Reference, Not Implementation)

Bloomberg's architecture provides a useful reference model even though InvestScan will never integrate with Bloomberg directly:

**Bloomberg's Key Pattern: Unified API Layer**
Bloomberg's BLPAPI provides a single standardized language for accessing all data -- market data, historical data, reference data, calculation tools. This "one API to rule them all" pattern maps to InvestScan's `UnifiedSignal` schema: regardless of whether a signal comes from EnvScan JSON or GlobalNews Parquet, the synthesis layer sees only `UnifiedSignal` objects.

**Bloomberg's Session/Event Model**:
Bloomberg structures data access as: Session (connection) -> Service (data type) -> Request (query) -> Event (response). InvestScan's pipeline follows an equivalent model: Pipeline execution (session) -> Module (service: normalizer/synthesizer/reporter) -> Function call (request) -> Return value (event).

The PRD should reference Bloomberg's unified API pattern as the inspiration for InvestScan's normalized schema: "Like Bloomberg's BLPAPI, which presents diverse data sources through a single standardized interface, InvestScan's `UnifiedSignal` schema presents diverse signal sources (EnvScan JSON, GlobalNews Parquet) through a single typed interface."

**Source**: [Bloomberg API Overview (Apidog)](https://apidog.com/blog/bloomberg-api/), [Bloomberg Server API](https://www.bloomberg.com/professional/products/data/data-connectivity/server-api/)

#### B2. QuantLib, Zipline, Backtrader: Established Financial Tool Integration

These libraries represent 10+ years of financial data integration experience:

**Zipline (Quantopian, 2012-present)**:
- Event-driven architecture for backtesting
- Data Bundles: standardized data ingest from multiple sources (Quandl, Yahoo Finance, custom CSVs)
- Key Pattern: **Data Bundle Registry** -- a catalog of available data sources with standardized ingest pipelines
- InvestScan application: The source system inventory (EnvScan + GlobalNews) is InvestScan's "data bundle registry"

**Backtrader (2015-present)**:
- Supports CSV, Pandas DataFrames, and real-time data feeds simultaneously
- Key Pattern: **Data Feed Abstraction** -- multiple data formats abstracted behind a uniform interface
- InvestScan application: The 6 normalizer functions (one per source format) are InvestScan's "data feed abstraction"

**QuantLib (2000-present)**:
- Modular architecture for quantitative finance
- Key Pattern: **Calculation Engine Separation** -- pricing models are separate from data access and instrument definitions
- InvestScan application: The synthesis module (direction scoring) is separate from normalization (data access) and reporting (presentation)

**Common Thread**: All three libraries follow the same architecture: **Data Ingest -> Normalization -> Calculation -> Output**. This is the canonical financial data processing pipeline, validated by 20+ years of production use. InvestScan's pipeline (Collect -> Normalize -> Synthesize -> Report) is a direct descendant.

**Source**: [Zipline (GitHub)](https://github.com/quantopian/zipline), [awesome-quant (GitHub)](https://github.com/wilsonfreitas/awesome-quant), [Python Trading Tools 2026 (Analyzing Alpha)](https://analyzingalpha.com/python-trading-tools)

#### B3. Batch vs Streaming Patterns for Market Data

| Pattern | Use Case | InvestScan Fit |
|---------|---------|---------------|
| **Batch (weekly)** | Weekly portfolio rebalancing, monthly reports | **PRIMARY** -- InvestScan's weekly execution cadence |
| **Micro-batch (daily)** | Daily risk monitoring | FUTURE -- if user wants daily signal alerts |
| **Streaming (real-time)** | Intraday trading, real-time risk | NEVER -- InvestScan is not a trading system |

The PRD should document: "InvestScan uses batch processing exclusively. The pipeline runs once per week (Sunday evening via `launchd`). There is no real-time component. This is a deliberate design choice: macro signal synthesis requires multi-day accumulation of data, and the target user (part-time investor) makes decisions on a weekly cadence."

---

### C. Unix Integration Patterns

#### C1. stdin/stdout Piping for Tool Integration

InvestScan's file-based IPC is a conscious choice to NOT use Unix pipe-based integration. The rationale:

| Approach | Pros | Cons | InvestScan Decision |
|----------|------|------|-------------------|
| **Unix pipes** (`envscan | normalize | synthesize | report`) | Zero disk overhead, streaming | No checkpoint/resume, no debugging, no partial re-run | **Rejected** |
| **File-based IPC** (EnvScan writes JSON/Parquet, InvestScan reads) | Checkpoint/resume, easy debugging, partial re-run | Disk overhead (~5MB/week) | **Adopted** |

**The Classical Argument FOR File-Based IPC** (from Doug McIlroy's Unix Philosophy):
"Write programs that do one thing and do it well. Write programs to work together." EnvScan does signal scanning well. GlobalNews does news analysis well. InvestScan does synthesis well. They work together via files -- the oldest, most debuggable, most universal integration mechanism.

#### C2. Configuration File Standards

| Format | Pros | Cons | InvestScan Decision |
|--------|------|------|-------------------|
| **YAML** | Human-readable, supports comments, hierarchical | Whitespace-sensitive, complex types | **Adopted** -- `config/investscan.yaml` |
| **TOML** | Clean syntax, typed values | Less familiar to most developers | Considered, rejected for familiarity |
| **INI** | Simplest possible format | No nesting, no typed values | Too simple for InvestScan config |
| **JSON** | Universal, machine-readable | No comments, verbose | Used for data, not config |

**InvestScan Configuration Hierarchy** (classical pattern):
1. Default values in code (`investscan/config.py`)
2. System-level config (`~/.investscan/config.yaml`)
3. Project-level config (`./config/investscan.yaml`)
4. Environment variables (`INVESTSCAN_ENVSCAN_ROOT`)
5. CLI arguments (`--date 2026-03-25`)

Higher numbers override lower numbers. This is the standard 5-tier configuration hierarchy used by virtually all Unix tools.

#### C3. launchd/Scheduling Service Patterns

For macOS batch scheduling, `launchd` is the correct choice (cron is deprecated since macOS 10.4):

**Key Design Decisions for PRD**:

1. **Agent, not Daemon**: InvestScan runs as the user, not as root. Config goes in `~/Library/LaunchAgents/`, not `/Library/LaunchDaemons/`.
2. **StartCalendarInterval**: Weekly execution (Sunday 21:00) via `<key>Weekday</key><integer>0</integer><key>Hour</key><integer>21</integer>`.
3. **Missed Execution Handling**: `launchd`'s key advantage over `cron`: if the Mac was asleep on Sunday 21:00, `launchd` will execute the pipeline when the Mac next wakes. This is critical for InvestScan because the user (a pastor) may not have the laptop open at the scheduled time.
4. **Working Directory**: Set `WorkingDirectory` to InvestScan project root.
5. **Log Capture**: `StandardOutPath` and `StandardErrorPath` to `~/Library/Logs/InvestScan/`.

**Source**: [Apple Scheduling Timed Jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html), [Cron and Launchd for ETL (Inner Join)](https://innerjoin.bit.io/cron-anacron-and-launchd-for-data-pipeline-scheduling-dd62bf11b6b7), [Scheduling Tasks on macOS (Serghei)](https://blog.serghei.pl/posts/scheduling-recurring-tasks-on-macos-using-launchd/)

---

### D. PRD Documentation for External Integrations

#### D1. What Sections Should a PRD Have for External Dependencies?

Based on classical PRD standards and modern PRD-for-AI-agents practices:

**Required PRD Sections for InvestScan's External Integrations**:

1. **System Context Diagram**
   - Visual showing InvestScan's position relative to EnvScan, GlobalNews, external APIs
   - Data flow arrows with format labels (JSON, Parquet, YAML)
   - Trust boundary markings (local vs. network)

2. **External Dependencies Inventory** (see Section D1 in Branch 5.1 above)
   - For each dependency: name, type, purpose, failure mode, degradation strategy

3. **Data Contract Specifications**
   - Input schema per source system (6 formats documented in Branch 1)
   - Output schema (weekly report structure, decision journal schema)
   - Schema version and compatibility guarantees

4. **Integration Testing Strategy**
   - Contract tests for source system boundaries (10 tests from Branch 4.1)
   - End-to-end test with real data from most recent pipeline run
   - Smoke test: `investscan doctor` that validates all prerequisites

5. **Degradation Matrix** (see Section D2 in Branch 5.1 above)
   - 4-tier degradation model for each external dependency

6. **Operational Runbook**
   - How to diagnose pipeline failures
   - How to re-run from a specific checkpoint
   - How to handle source system schema changes

#### D2. How to Document API Contracts in PRD Format

**Recommended Format** (per-API):

```markdown
### API: FRED (Federal Reserve Economic Data)

**Purpose**: Economic indicators for macro context (GDP, inflation, interest rates)
**Phase**: Phase 2 (Months 4-6)
**Base URL**: https://api.stlouisfed.org/fred/
**Auth**: API key (request at https://fred.stlouisfed.org/docs/api/api_key.html)
**Rate Limit**: 120 requests/minute, 500,000 requests/day

**Endpoints Used**:
| Endpoint | Purpose | Frequency | Cache TTL |
|----------|---------|-----------|-----------|
| `/series/observations` | GDP, CPI, Fed Funds Rate | Weekly | 7 days |

**Response Schema** (relevant fields only):
```json
{
  "observations": [
    {"date": "2026-03-01", "value": "28015.5"}
  ]
}
```

**Failure Handling**:
- HTTP 429 (rate limit): Wait Retry-After seconds, retry once
- HTTP 5xx (server error): Use cached value, log warning
- Network error: Use cached value, log warning
- Stale cache (>14 days): Flag in report as "economic data outdated"
```

#### D3. Integration Testing Strategy Documentation

**Three-Tier Testing Strategy** (adapted from classical ETL + modern PRD practices):

| Tier | What | When | How |
|------|------|------|-----|
| **T1: Contract Tests** | Verify source system output matches expected schema | Before every pipeline run | 10 pytest tests, auto-run by `investscan doctor` |
| **T2: Integration Tests** | Verify full pipeline produces valid report from real data | Weekly (after pipeline runs) | `investscan test` command, uses most recent output |
| **T3: Regression Tests** | Verify pipeline produces same output from same input | Monthly | Frozen test data in `tests/fixtures/`, `pytest tests/test_regression.py` |

The PRD should document: "InvestScan uses a 3-tier testing strategy. T1 contract tests (10 tests) run automatically before every pipeline execution. T2 integration tests run weekly. T3 regression tests run monthly. Total test budget: 25 tests, ~8 hours to write over 6 months."

---

## COMPARISON: Explicit Reference vs. Implicit Pattern Adoption

### Documents and Patterns the PRD Should EXPLICITLY Reference

These are patterns that the PRD should cite by name, with a brief explanation of why InvestScan adopts them:

| Reference | What to Reference | Why Explicit |
|-----------|-------------------|-------------|
| **AgenticWorkflow DNA** | Inherited genome (3-Phase, SOT, 4-Layer QA, CCP) | InvestScan IS a child of AgenticWorkflow -- the inheritance must be documented |
| **Medallion Architecture** | Bronze/Silver/Gold data layers | Establishes data quality progression for readers who know ETL |
| **Bloomberg BLPAPI Pattern** | Unified schema abstraction over diverse data sources | Justifies `UnifiedSignal` schema design -- this is how the industry leader does it |
| **EMH + Behavioral Finance** | Theoretical justification for why signal synthesis has value | Already documented in Round 2 classical-foundational-theory.md; PRD should cite specific mechanisms (attention scarcity, processing lags, geographic fragmentation) |
| **PRISM-INSIGHT Positioning** | "Microscope vs. Telescope" competitive positioning | Preempts the "why not just use PRISM-INSIGHT?" question |
| **Ansoff's Weak Signal Theory** | Theoretical backbone of STEEPs classification | Connects InvestScan to 50+ years of strategic foresight research |
| **launchd Scheduling** | macOS-native batch execution | Documents why cron is not used (deprecated) and why launchd is chosen |
| **Circuit Breaker Pattern** | API degradation handling | Provides a named, well-understood pattern for the degradation matrix |

### Patterns the PRD Should IMPLICITLY Follow (Not Cite)

These are patterns that shape InvestScan's architecture but do not need to be cited explicitly -- the reader should see them in the architecture without needing them named:

| Pattern | Where It Appears | Why Implicit |
|---------|-----------------|-------------|
| **Claude Code workflow conventions** | Pipeline structure, context boundaries, SOT | These are implementation conventions, not architectural decisions worth citing |
| **Supervisor orchestration pattern** | CLI orchestrator calling Python modules | Naming the pattern adds no value; the architecture speaks for itself |
| **Unix configuration hierarchy** | 5-tier config (code -> system -> project -> env -> CLI) | This is standard practice, not a noteworthy design choice |
| **FinGPT data-centric approach** | Emphasis on data quality over model sophistication | InvestScan's design already embodies this; citing FinGPT adds no credibility |
| **TradingAgents debate pattern** | Cross-source convergence scoring | InvestScan uses scoring, not agent debate; the pattern diverges too much to cite directly |
| **Frozen dataclass pattern** | `UnifiedSignal`, `InvestmentMeta`, `SignalView` | This is a Python best practice, not a design decision worth citing |
| **Event-driven architecture (Zipline)** | N/A -- InvestScan is batch, not event-driven | Explicitly NOT following this pattern; mentioning it would confuse readers |
| **Data Bundle Registry (Zipline)** | Source system inventory in config | The concept is adopted but the implementation is too different to warrant citation |
| **File-based IPC** | Source systems write output, InvestScan reads | The "why" is documented (fastest path, zero changes to source systems); the pattern name adds nothing |

### The Dividing Principle

**Cite explicitly when**: The reference provides legitimacy, establishes positioning, or explains a non-obvious architectural choice to the reader.

**Follow implicitly when**: The pattern is industry-standard practice that would be expected of any competent implementation, or when the InvestScan adaptation diverges significantly from the reference.

---

## Summary: Top 10 References the PRD Must Include

| # | Reference | PRD Section | Purpose |
|---|-----------|-------------|---------|
| 1 | **AgenticWorkflow DNA** (parent framework) | Architecture > Inherited Patterns | Establishes InvestScan as a legitimate child of a proven framework |
| 2 | **Ansoff Weak Signal Theory** + WISDOM Framework | Theoretical Foundation | Justifies the entire system's raison d'etre with 50+ years of academic backing |
| 3 | **EMH Processing Lag Evidence** | Theoretical Foundation | Answers "why would this work?" with specific mechanisms (attention scarcity, geographic fragmentation, processing lags) |
| 4 | **Medallion Architecture** (Bronze/Silver/Gold) | Data Architecture | Frames InvestScan's pipeline in industry-standard ETL terminology |
| 5 | **Bloomberg BLPAPI Unified Schema** | Schema Design Rationale | Justifies `UnifiedSignal` as following the industry leader's pattern |
| 6 | **PRISM-INSIGHT** (competitive positioning) | Market Positioning | "Telescope vs. Microscope" -- preempts competitive confusion |
| 7 | **Circuit Breaker + Degradation Matrix** | Reliability Architecture | Named patterns for handling external API failures |
| 8 | **launchd** (macOS scheduling) | Operational Architecture | Documents platform-native scheduling choice |
| 9 | **10 Contract Tests** (classical ETL boundary testing) | Quality Architecture | Bridges financial safety ("errors = money lost") with concrete test strategy |
| 10 | **Behavioral Finance Biases** (Kahneman, Shiller) | User Value Proposition | Even if EMH is correct, InvestScan provides cognitive structuring value |

---

## Sources

### Modern References (Branch 5.1)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
- [claude-code-best-practice (GitHub)](https://github.com/shanraisshan/claude-code-best-practice)
- [Claude Code Ultimate Guide (GitHub)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)
- [Claude Code Best Practices 2026 (eesel AI)](https://www.eesel.ai/blog/claude-code-best-practices)
- [Claude Code Creator Workflow (MindWiredAI)](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/)
- [AWS Agentic AI Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/introduction.html)
- [AWS Workflow Orchestration Agents](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-orchestration-agents.html)
- [LangChain Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Agentic Workflows 2026 Guide (Vellum)](https://vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns)
- [CrewAI Platform](https://crewai.com/)
- [FinGPT GitHub](https://github.com/AI4Finance-Foundation/FinGPT)
- [FinGPT Paper (arXiv:2306.06031)](https://arxiv.org/abs/2306.06031)
- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- [TradingAgents Documentation](https://tradingagents-ai.github.io/)
- [PRISM-INSIGHT GitHub](https://github.com/dragon1086/prism-insight)
- [PRISM-INSIGHT Dashboard](https://analysis.stocksimulation.kr/)
- [Building Offline-First AI Applications 2026](https://www.practicalwebtools.com/blog/building-offline-first-ai-applications-guide-2026)
- [Definitive Guide to Local-First AI (SitePoint)](https://www.sitepoint.com/definitive-guide-local-first-ai-2026/)
- [Local-First Software Patterns 2026](https://tech-champion.com/software-engineering/the-local-first-manifesto-why-the-cloud-is-losing-its-luster-in-2026/)
- [API Rate Limiting at Scale (Gravitee)](https://www.gravitee.io/blog/rate-limiting-apis-scale-patterns-strategies)
- [Best Practices for API Rate Limits (Truto)](https://truto.one/blog/best-practices-for-handling-api-rate-limits-and-retries-across-multiple-third-party-apis)
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/errors.html)
- [Python Secrets Management (GitGuardian)](https://blog.gitguardian.com/how-to-handle-secrets-in-python/)
- [Managing Secrets with .env (KDnuggets)](https://www.kdnuggets.com/managing-secrets-and-api-keys-in-python-projects-env-guide)
- [Python Keyring (Medium)](https://medium.com/@forsytheryan/securely-storing-credentials-in-python-with-keyring-d8972c3bd25f)
- [PRDs for AI Coding Agents (Medium)](https://medium.com/@haberlah/how-to-write-prds-for-ai-coding-agents-d60d72efb797)
- [PRD as Persistent Documentation (CodeSignal)](https://codesignal.com/learn/courses/foundations-of-spec-driven-development/lessons/prd-as-persistent-documentation)

### Classical References (Branch 5.2)
- [ETL Pipeline Data Lineage (Meegle)](https://www.meegle.com/en_us/topics/etl-pipeline/etl-pipeline-data-lineage)
- [Data Lineage in ETL (Secoda)](https://www.secoda.co/blog/data-lineage-in-etl-process)
- [Track Data Lineage in ETL (Airbyte)](https://airbyte.com/data-engineering-resources/track-data-lineage-etl-pipelines)
- [Data Lineage 2025 (Dagster)](https://dagster.io/learn/data-lineage)
- [Bloomberg API Overview (Apidog)](https://apidog.com/blog/bloomberg-api/)
- [Bloomberg Server API](https://www.bloomberg.com/professional/products/data/data-connectivity/server-api/)
- [Zipline (GitHub)](https://github.com/quantopian/zipline)
- [awesome-quant (GitHub)](https://github.com/wilsonfreitas/awesome-quant)
- [Python Trading Tools 2026 (Analyzing Alpha)](https://analyzingalpha.com/python-trading-tools)
- [pykrx GitHub](https://github.com/sharebook-kr/pykrx)
- [Apple Scheduling Timed Jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)
- [Cron and Launchd for ETL (Inner Join)](https://innerjoin.bit.io/cron-anacron-and-launchd-for-data-pipeline-scheduling-dd62bf11b6b7)
- [Scheduling Tasks on macOS (Serghei)](https://blog.serghei.pl/posts/scheduling-recurring-tasks-on-macos-using-launchd/)
