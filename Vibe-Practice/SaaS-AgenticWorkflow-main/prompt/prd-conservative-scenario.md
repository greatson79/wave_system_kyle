# SaaS Auto-Builder: Conservative Scenario PRD

**Scenario**: CONSERVATIVE — "Start small, go deep. Survive first, grow later."
**Philosophy**: If we do 3 things perfectly, that is better than 10 things mediocrely.
**Date**: 2026-03-12
**Data Basis**: Phase 1 (8 research branches) + Phase 2 (4 discussion perspectives: Market, User, Tech, Business)

---

## 1. Executive Summary

### Why Conservative?

The AI developer tools market in 2026 is a $7.37B arena dominated by players with a combined $4B+ in funding. Cursor ($29.3B valuation, $2B+ ARR), Lovable ($6.6B valuation, $300M ARR), and Replit ($9B valuation, $265M ARR) have already captured the mainstream. Entering this market with a bootstrapped, CLI-only tool against billion-dollar incumbents demands intellectual honesty about what is achievable.

**Four uncertainties justify extreme caution:**

1. **Unvalidated core assumption.** The structured document pipeline (PRD to TRD to Code) is the product's sole true differentiator — yet zero market data confirms that developers will pay for AI-generated planning documents. Lovable's $300M ARR proves users want "prompt to app," not "prompt to documents to app." We are betting that a minority of developers prefer our approach, and we do not yet know how large that minority is.

2. **Replicability risk.** The document pipeline is a workflow design, not a technical moat. Any well-funded competitor could add similar capabilities in a single engineering sprint (the Business discussion estimated 60-70% probability of competitor replication). Our defense must be execution depth, not feature novelty.

3. **CLI adoption ceiling.** The fastest-growing tools in this space (Lovable, Bolt.new, Replit) are all cloud-based with browser interfaces. CLI tools serve a narrow audience: experienced developers who are also the most price-resistant and most capable of building their own solutions. The Cautious Market Report estimated our total realistic TAM at 90,000-115,000 users — a viable niche, but one with no margin for error.

4. **Solo founder resource constraint.** With approximately $1,500-$1,900/month burn rate, no external funding, and 50 hours/week of founder time, every feature decision is a zero-sum tradeoff against quality. Spreading thin across 10 features guarantees none of them are excellent.

### The "Worst Case Is Still OK" Argument

The conservative scenario's greatest strength is its bounded downside. At its worst:

- **The open-source core** continues to exist and serve 100-200 free users regardless of monetization success.
- **The founder's expertise** in AI-driven SaaS workflow generation is itself a marketable skill worth $150-$300/hr in consulting.
- **The template and workflow knowledge** is reusable in courses ($99-$299 each), consulting ($2,000-$10,000/engagement), or a different product.
- **Community relationships** transfer to whatever comes next.
- **Total sunk cost** at Month 6: approximately $9,000-$11,400 (6 months x $1,500-$1,900). This is not a catastrophic loss for a founder with 18+ months of personal runway.

The worst realistic outcome: a well-maintained open-source tool with a small but grateful user base, zero revenue, and a soft pivot to consulting. That is a career detour, not a career-ending crash.

---

## 2. Feature Set (4 Features — All P0)

The conservative scenario includes ONLY features that achieved 4/4 consensus across all research perspectives AND form the absolute minimum chain for a viable product. Every feature has a 30%+ timeline buffer built into its estimate.

### Feature 1: Conversational SaaS Definition Engine

**Description**: An intelligent, domain-aware questioning system (3-7 questions per topic area) that extracts a founder's SaaS idea with sufficient depth to generate production-quality documents — functioning as an AI product manager.

**Priority**: P0 — This IS the product. Without this, everything downstream fails.

**Dev Time**: 5 weeks (base 3.5 weeks + 43% buffer)

**Risk Level**: Low — The technical implementation (structured prompt chains with Claude Code) is well-understood. The risk is in question quality, which is iteratively improvable.

**Quality Standard — What "Excellent" Looks Like**:
- Users report "the tool asked questions I hadn't considered" in post-session feedback
- Conversation completion rate exceeds 70% (users do not abandon the Q&A flow)
- The median session produces a complete enough input to generate a PRD without follow-up clarification
- Questions adapt to the user's domain (a marketplace SaaS gets different questions than a project management tool)
- Time from first question to completed input: under 10 minutes
- At least 5 domain-specific question paths (e-commerce, marketplace, SaaS dashboard, content platform, productivity tool)

**What This Is NOT**: A generic chatbot. The questioning system must demonstrate genuine product management expertise — surfacing edge cases, forcing prioritization, and identifying implicit assumptions the founder has not articulated.

### Feature 2: PRD + TRD Generation with Bidirectional Context Propagation

**Description**: From the conversational input, automatically generate a production-grade Product Requirements Document and Technical Requirements Document where every TRD decision traces back to a PRD requirement, and changes to either document propagate to the other.

**Priority**: P0 — This is the ONLY true differentiator versus all competitors. No existing tool links planning documents with bidirectional traceability.

**Dev Time**: 7 weeks (base 5 weeks + 40% buffer)

**Risk Level**: Low — Document generation is within Claude's proven capabilities. Context propagation requires careful architecture but no novel technology.

**Quality Standard — What "Excellent" Looks Like**:
- Generated PRD is usable without editing by a senior PM (covers user personas, feature prioritization, constraints, success metrics, and out-of-scope items)
- Generated TRD includes defensible architecture decisions with explicit trade-off reasoning (not boilerplate)
- Every TRD component references the specific PRD requirement it satisfies (traceability matrix)
- Cross-validation catches at least 80% of consistency errors between documents (e.g., a feature listed in PRD but missing from TRD)
- A developer reading only the TRD can understand what to build, why, and how
- Document quality passes a blind review against human-written equivalents with a "comparable or better" rating from 3 out of 5 experienced PMs/architects

**What This Is NOT**: Two independent documents generated separately. The bidirectional linkage — where a TRD architectural constraint can flag a PRD requirement as infeasible — is what makes this a pipeline rather than two separate generators.

### Feature 3: One Production-Quality Code Template (Next.js + Supabase + Stripe)

**Description**: A single, battle-tested, production-ready code template that translates TRD specifications into a runnable Next.js application with Supabase (database + auth) and Stripe (payments) pre-integrated.

**Priority**: P0 — This is the proof that the document pipeline produces real, working output. Without this, we are just another document generator.

**Dev Time**: 6 weeks (base 4.5 weeks + 33% buffer)

**Risk Level**: Low — Next.js + Supabase + Stripe is the most common indie SaaS stack in 2026 and covers approximately 60%+ of the target market's needs. The template itself uses proven technologies with massive community support.

**Quality Standard — What "Excellent" Looks Like**:
- Generated code passes ESLint with zero errors, TypeScript strict mode with zero errors
- Includes proper error handling (not just happy path)
- Includes basic test coverage (unit tests for core logic, integration test for auth flow)
- Auth (email/password + OAuth), database schema, and Stripe subscription flow work out of the box
- Code follows the generated Code Guidelines document (not generic boilerplate)
- A mid-level developer can read, understand, and extend the generated codebase without documentation beyond the generated TRD
- Security: passes OWASP Top 10 basic checks (no exposed API keys, proper CORS, input validation, parameterized queries)
- Time from TRD to runnable code: under 20 minutes

**What This Is NOT**: A full auto-implementation system. The template generates the structural skeleton and core integrations. Feature-specific business logic (e.g., a marketplace's escrow system) requires developer implementation guided by the generated Task Breakdown.

### Feature 4: First-Run Experience (Install to First PRD in Under 15 Minutes)

**Description**: A frictionless onboarding path where a developer goes from `npm install` (or equivalent) to holding a generated PRD in their hands within 15 minutes, including the conversational flow.

**Priority**: P0 — 55% of trial cancellations happen on Day 0 (RevenueCat 2026). If the first experience is confusing, slow, or underwhelming, the user never returns.

**Dev Time**: 3 weeks (base 2 weeks + 50% buffer)

**Risk Level**: Low — This is UX polish and CLI design, not novel technology. The high buffer accounts for the iteration cycles needed to get onboarding right (user testing with 10+ subjects).

**Quality Standard — What "Excellent" Looks Like**:
- Installation requires 3 or fewer commands
- BYOK (Bring Your Own Key) setup for Claude API key takes under 2 minutes with clear instructions
- First conversational session starts within 60 seconds of installation
- No confusing error messages — every failure mode has a human-readable explanation and suggested fix
- The generated PRD from the first session is impressive enough that the user's immediate reaction is "this saved me days of work"
- End-to-end time (install to PRD) median: 12 minutes or less
- Documentation covers 100% of installation scenarios (macOS, Linux, WSL on Windows)

**What This Is NOT**: A web-based setup wizard. This is a CLI-first experience designed for developers who are comfortable with terminals. The goal is not zero-friction (that requires a GUI) but minimum-friction-for-the-target-audience.

---

## 3. Architecture Choices

### What Gets Built with Maximum Quality

**Modular Monolith with Clean Module Boundaries** — 4/4 consensus across all research perspectives.

The architecture follows the evolutionary approach (Branch 2.1 from Tech Deep-Dive): start simple, design for future separation.

```
saas-auto-builder/
├── core/                          # Core engine (the soul)
│   ├── conversation-engine/       # Q&A flow management + domain detection
│   ├── document-generator/        # PRD, TRD generation + cross-validation
│   ├── context-propagation/       # Bidirectional document linkage (SOT chain)
│   └── template-engine/           # Code generation from TRD specs
├── templates/
│   └── nextjs-supabase-stripe/    # The ONE production template
├── cli/                           # CLI interface layer (thin)
├── config/                        # User config, API key management
└── tests/                         # Unit, integration, E2E
```

**Key Architectural Decisions:**

1. **Each module communicates through defined interfaces (no direct imports between modules).** This means `conversation-engine` produces a standardized `ConversationOutput` that `document-generator` consumes. If we later need to add a GUI or API layer, we replace only the `cli/` module — the core engine remains untouched.

2. **Document format is structured JSON internally, rendered to Markdown for users.** This enables machine-readable cross-validation between documents while preserving human-readable output. The JSON schema IS the contract between modules.

3. **Template engine uses a declarative specification layer.** Templates are not hardcoded; they consume a `TemplateSpec` derived from the TRD. Adding a new template (SvelteKit, Nuxt) in V2 means adding a new template directory that conforms to the `TemplateSpec` interface — zero changes to the core engine.

4. **BYOK architecture: API key is injected at the CLI layer, never stored in the core engine.** The core engine accepts an `LLMClient` interface. In V1, the only implementation is Claude. In V2, GPT/Gemini implementations can be added without touching the core engine.

### No Tech Debt Policy — What This Means Concretely

"No tech debt" does not mean "no shortcuts." It means:

1. **Every shortcut is documented.** If we hardcode a value that should be configurable, a `// DEBT: Extract to config` comment marks it. A `TECH-DEBT.md` file tracks all debts with estimated remediation time.

2. **20% of development time is allocated to debt reduction.** Every fifth week is dedicated to refactoring, test coverage, and documentation. By Month 6, the codebase remains clean and extensible.

3. **No module boundary violations.** The modular monolith pattern only works if module boundaries are enforced. A linting rule prevents direct imports across module boundaries. This is the one rule that is never broken, even under time pressure.

4. **All generated code follows the same Code Guidelines the product generates for users.** We eat our own dog food. If the product generates TypeScript strict mode code, our codebase uses TypeScript strict mode.

### How This Scales to V2 Without Refactoring

| V2 Feature | Architecture Ready? | What Changes |
|---|---|---|
| Additional templates (Svelte, Nuxt) | Yes | Add new template directory conforming to `TemplateSpec` |
| Web GUI | Yes | Add `web/` module consuming the same core engine interfaces |
| Multi-LLM support | Yes | Add new `LLMClient` implementation (GPT, Gemini) |
| Template marketplace | Yes | Add `marketplace/` module; templates already follow standard spec |
| Full 7-doc pipeline | Yes | Add generators to `document-generator/` module; `context-propagation` already handles N documents |
| Task generation | Yes | Add `task-generator/` module consuming TRD output |

The critical insight: V2 features ADD modules. They do not MODIFY existing modules. This is the payoff of investing in clean interfaces upfront.

### Testing Strategy

**Target Coverage**: 85%+ line coverage, 90%+ branch coverage for core modules.

| Layer | Testing Approach | Coverage Target |
|---|---|---|
| Conversation Engine | Unit tests for question flow logic; integration tests with mock LLM responses | 85% |
| Document Generator | Unit tests for template rendering; snapshot tests for output format; property-based tests for cross-validation | 90% |
| Context Propagation | Integration tests verifying bidirectional linkage; regression tests for known edge cases | 90% |
| Template Engine | E2E tests: generated code must lint, typecheck, and pass basic runtime tests | 85% |
| CLI | Integration tests for all user-facing commands; manual testing for UX flows | 75% |

**Testing philosophy**: We test the contract (inputs and outputs of each module) exhaustively. We test internal implementation selectively. We never ship a feature without its corresponding test. We run the full test suite before every release.

---

## 4. Timeline (6 Months)

### Month 1-3 (Milestone 1): Build Core Engine to Excellence

| Week | Focus | Deliverable | Quality Gate |
|---|---|---|---|
| 1-2 | Architecture setup + CI/CD | Project scaffolding, module boundaries, linting rules, test infrastructure, GitHub Actions pipeline | All linting passes, CI green, module boundary enforcement active |
| 3-5 | Conversation Engine | Domain-aware questioning system with 5 paths, 3-7 questions each | 70%+ completion rate in internal testing (founder + 3 beta testers) |
| 5-7 | Onboarding (First-Run) | Install flow, BYOK setup, CLI interface | Install-to-first-question in under 3 minutes |
| 6-10 | Document Generator (PRD) | PRD generation from conversation output, cross-validation engine foundation | Generated PRDs pass blind review by 2 experienced PMs |
| 8-12 | Document Generator (TRD) + Context Propagation | TRD generation with bidirectional PRD linkage | Every TRD component traces to a PRD requirement; cross-validation catches 80%+ consistency errors |
| 10-13 | Template Engine + Next.js Template | Code generation from TRD, one production template | Generated code lints, typechecks, runs, passes auth/payment flow test |

**M1 Quality Gate (Week 13)**: End-to-end flow works: conversation to PRD to TRD to running code in under 30 minutes. Internal test with 5 users. Fix all critical bugs before proceeding.

### Month 4-5 (Milestone 2): Polish, Test, Beta

| Week | Focus | Deliverable | Quality Gate |
|---|---|---|---|
| 14-15 | Bug fixing + polish from M1 testing | Stable end-to-end flow | Zero critical bugs, <5 medium bugs |
| 16-17 | Private beta (20-30 users) | Real user testing, feedback collection | 70%+ completion rate, <15min first-run, NPS 25+ |
| 18-19 | Iteration on beta feedback | Improved question quality, document quality, template quality | Measurable improvement on all M1 metrics |
| 20-21 | Documentation + tutorials | Installation guide, "Build X in Y minutes" tutorial (2 versions), API key setup guide, FAQ | 100% of installation scenarios covered; 2 end-to-end tutorials published |
| 21-22 | Free/paid boundary implementation | License key validation, 3-project limit on free tier, Pro tier ($19/mo) with Stripe integration | Payment flow works; free/paid boundary is clear and fair |

**M2 Quality Gate (Week 22)**: 20+ beta users have completed the full flow. Conversion intent signal from at least 3 users ("I would pay for this"). NPS 30+. All documentation complete.

### Month 6 (Milestone 3): Launch with Confidence

| Week | Focus | Deliverable | Quality Gate |
|---|---|---|---|
| 23 | Public beta preparation | ProductHunt page, launch blog post, Indie Hackers post, Reddit strategy | All launch materials reviewed and ready |
| 24 | Public launch | ProductHunt launch, Indie Hackers post, r/SideProject + r/ClaudeAI posts | Launch day goes smoothly; no critical bugs |
| 25-26 | Post-launch support + iteration | Bug fixes, user support, feedback-driven improvements, community seeding (Discord) | Response to all user issues within 24 hours |

**M3 Quality Gate (Week 26 — Month 6 Review)**: Evaluate against success criteria (Section 8). Make GO/NO-GO decision on continuing investment.

### What Fills the Remaining Time

The generous buffer (30%+) on each feature means some weeks will have available capacity. This capacity is pre-allocated:

1. **Testing depth** (40% of buffer time): Additional edge case tests, security testing, performance testing
2. **Documentation** (30% of buffer time): Internal architecture docs, contributor guide (for future open-source contributors), user-facing FAQ expansion
3. **Community groundwork** (20% of buffer time): Build-in-public posts (1/week), engage in Claude Code / AI coding communities, seed Discord server
4. **Tech debt reduction** (10% of buffer time): Refactor any shortcuts taken under time pressure

---

## 5. Revenue Targets (Conservative)

### Pricing Model

| Tier | Price | Includes |
|---|---|---|
| Community (Free) | $0 | Core conversation + PRD + TRD generation. Basic Next.js template. 3-project limit. |
| Pro | $19/month ($149/year) | Unlimited projects. Industry-specific question paths. Advanced Code Guidelines (testing, CI/CD, monitoring). Priority template updates. |
| Enterprise Consulting | $2,000-$10,000/engagement | Custom workflow design. Template creation for proprietary stacks. |

**Note**: Team tier ($49/mo) is explicitly deferred to V2. The conservative scenario avoids multi-tier complexity at launch.

### Revenue Projections

| Metric | Month 3 | Month 6 | Month 12 |
|---|---|---|---|
| Cumulative Free Users | 50-80 | 200-300 | 800-1,500 |
| Pro Subscribers | 0-3 | 15-40 | 60-120 |
| Conversion Rate | N/A (beta) | 1-1.5% | 1.5-2% |
| MRR | $0 | $285-$760 | $1,140-$2,280 |
| Enterprise Engagements (cumulative) | 0 | 0-1 | 2-4 |
| Enterprise Revenue (cumulative) | $0 | $0-$3,000 | $4,000-$20,000 |
| **Total Year 1 Revenue** | | | **$10,000-$30,000** |

**Why these numbers are lower than the Business discussion's estimates**: The Business discussion assumed $1,500-$3,000 MRR at Month 6 with 2-3% conversion. The conservative scenario uses 1-1.5% conversion (the low end of CLI tool benchmarks) and projects slower user acquisition (200-300 cumulative vs 250-350). We plan for the floor, not the ceiling.

### Conservative Conversion Rate Assumption: 1-1.5%

**Justification**: Open-source SaaS tools convert at 0.3-3% (Monetizely benchmark). CLI-specific tools have no direct benchmark data, but CLI users are simultaneously higher-intent (they chose a power tool) and more price-resistant (they can build alternatives themselves). Taking the conservative middle of the 0.3-3% range at 1-1.5% accounts for the possibility that the free tier is "good enough" for most users — the #1 business risk identified in the Business discussion (40-50% probability).

### What If Revenue Is $0 for 6 Months?

This is the scenario we must survive. Here is why it is still acceptable:

| Factor | Assessment |
|---|---|
| Total cost incurred | $9,000-$11,400 (6 months x $1,500-$1,900 burn rate) |
| Founder personal runway remaining | 12+ months (assuming 18-month initial runway) |
| Open-source asset value | A working, documented, tested tool with 100-200 users |
| Consulting pivot viability | The tool itself is a demonstration of AI workflow expertise; $150-$300/hr consulting rate is realistic |
| Skills acquired | Deep expertise in AI-driven product development, CLI tool design, open-source community building |
| Community value | Even 50 active users who find the tool useful create referral and testimonial value |
| Sunk cost vs option value | $10K sunk cost buys 12+ months of option value on a potentially viable product |

**The honest math**: A bootstrapped founder with $30,000 in savings and $1,500/month burn has 20 months of runway with zero revenue. If by Month 6 the product has 200+ free users but $0 revenue, the correct move is not shutdown but pivoting the monetization approach (consulting-first, different paywall boundary, or enterprise focus). The $10K spent buys the right to make that decision with real data.

---

## 6. What Is Explicitly EXCLUDED from V1 and Why

### Excluded Feature 1: Full 7-Document Pipeline (User Journey, UI Guidelines, IA)

**Why excluded**: The minimum viable document chain is Conversation to PRD to TRD to Code. The remaining 4 documents (User Journey, UI Guidelines, Information Architecture, Task Breakdown with acceptance criteria) add completeness but do not drive conversion or initial retention. Building 7 generators to "good" quality is worse than building 3 generators to "excellent" quality (Absolute Standard 1: quality is the only criterion).

**What we lose**: Completeness of the planning process. Users who want full documentation will need to write User Journey, UI Guidelines, and IA manually (or use the PRD/TRD as a starting point). This reduces the "wow factor" of the full pipeline.

**When it enters V2**: Trigger condition — PRD and TRD generation achieve 85%+ user satisfaction score (measured by document edit rate: <30% of users make significant edits). Once the core documents are excellent, expanding the pipeline adds genuine value rather than diluting quality.

**Estimated V2 timeline**: Month 7-10 (4 documents x 2-3 weeks each, with buffer).

### Excluded Feature 2: Task Generation with Acceptance Criteria

**Why excluded**: Task generation is valuable but sits at the end of the pipeline. Its quality depends entirely on PRD/TRD quality. Building task generation before PRD/TRD are excellent produces garbage-in-garbage-out. Additionally, experienced developers (our V1 target) can derive tasks from a TRD manually — this is not a blocker for them.

**What we lose**: The "bridge from documents to implementation" that makes the tool feel complete. Users must manually translate TRD into actionable development tasks, which adds friction to the "idea to code" journey.

**When it enters V2**: Trigger condition — TRD generation is stable (no critical bugs for 4 consecutive weeks) AND at least 10 users have requested task generation in feedback. Demand-validated before building.

**Estimated V2 timeline**: Month 8-9 (3 weeks base + buffer).

### Excluded Feature 3: Multi-Framework Support (SvelteKit, Nuxt, etc.)

**Why excluded**: Each additional framework template requires 4-6 weeks of development and ongoing maintenance. Next.js covers approximately 60%+ of the target market. Adding a second framework in V1 halves the quality investment in the primary template for a 15-20% increase in addressable users. The math does not work in a quality-first strategy.

**What we lose**: Users who prefer SvelteKit or Nuxt must either use the Next.js template or only use the document pipeline (no code generation). This is a real limitation that may cost 20-30% of potential users.

**When it enters V2**: Trigger condition — Next.js template achieves 90%+ user satisfaction AND at least 20 users have specifically requested an alternative framework. The second framework choice should be data-driven (which framework do users actually request?), not assumption-driven.

**Estimated V2 timeline**: Month 9-12 (6 weeks per framework with buffer).

### Excluded Feature 4: Web GUI / Browser Interface

**Why excluded**: 8-12 weeks of development for a demographic (mainstream/non-technical users) that we explicitly decided NOT to target in V1. Building a GUI before the core engine is excellent is premature optimization of distribution before the product is ready. The Business discussion confirmed: "Plan V2 GUI architecture from Day 1 but do NOT build it in V1."

**What we lose**: The entire non-CLI-comfortable user base. This is significant — the fastest-growing competitors are all browser-based. We are accepting a smaller total addressable market in exchange for deeper quality within our niche.

**When it enters V2**: Trigger condition — CLI product achieves product-market fit signals (NPS 40+, 30-day retention 50%+, organic word-of-mouth detectable) AND revenue supports hiring a frontend developer. Building a GUI on a shaky core engine produces a shaky GUI.

**Estimated V2 timeline**: Month 10-14 (8-12 weeks, ideally with a dedicated frontend hire).

### Excluded Feature 5: One-Click Deployment

**Why excluded**: Deployment infrastructure (cloud provider integrations, CI/CD pipeline management, SSL/CDN configuration) is a hosting business, not a document pipeline business. Maintaining deployment for even 2-3 providers (Vercel, Netlify, Railway) requires ongoing operational work that exceeds a solo founder's capacity. The Cautious Market Report identified this as a "MUST-HAVE," but the Business discussion correctly counter-argued: "Let Vercel/Netlify handle deployment."

**What we lose**: The "idea to deployed SaaS" narrative. Users generate code but must deploy it themselves. This is the single biggest sacrifice in the conservative scenario — competitors like Lovable deploy in one click. Our response is that the generated code includes a deployment guide in the TRD, and users who can handle a CLI tool can handle `vercel deploy`.

**When it enters V2**: Trigger condition — at least 30% of users cite "deployment difficulty" as a pain point in feedback surveys. If our users (experienced developers) do not struggle with deployment, this feature never needs to exist.

**Estimated V2 timeline**: Month 12-16 (8-10 weeks, high complexity).

### Excluded Feature 6: Multi-LLM Support (GPT, Gemini, Local Models)

**Why excluded**: Supporting multiple LLMs creates a massive testing surface area (every feature must work across 3-5 models with different capabilities, rate limits, and output formats). Output quality varies significantly across models, making quality guarantees impossible. Claude Code is our platform; optimizing for one LLM produces far better results than mediocre support for five.

**What we lose**: Users who do not have or want a Claude API key cannot use the product. This creates a single-vendor dependency (Anthropic) that the Cautious Market Report rated as CRITICAL severity.

**When it enters V2**: Trigger condition — Anthropic makes a pricing or policy change that materially affects user economics OR at least 25% of potential users cite Claude-only as a blocker. The `LLMClient` interface in the architecture allows adding new providers without core changes — the abstraction exists from Day 1 even though only one implementation ships.

**Estimated V2 timeline**: Month 10-14 (4-6 weeks per additional LLM provider).

### Excluded Feature 7: Template Marketplace

**Why excluded**: A marketplace requires (a) critical mass of templates, (b) critical mass of users, and (c) payment/commission infrastructure. None of these exist at launch. Building marketplace infrastructure before having 500+ users is premature optimization. The Business discussion confirmed this as "P3 — plan now, ship later."

**What we lose**: A potential revenue diversification stream (30% commission model) and community-driven content creation that would reduce the founder's template-building burden.

**When it enters V2**: Trigger condition — 500+ active users AND at least 5 community members have expressed interest in creating and selling templates. Architecture supports it from Day 1 (templates follow `TemplateSpec` interface), but the marketplace UI/payment system is deferred.

**Estimated V2 timeline**: Month 12-18 (8-12 weeks for marketplace infrastructure).

---

## 7. Top 3 Risks (Even in Conservative Mode)

### Risk 1: Free Tier "Good Enough" — Zero Conversion

**Probability**: 40-50%
**Impact**: FATAL — business generates zero revenue, forcing pivot or shutdown
**Weighted Score**: CRITICAL

**Why this risk persists in conservative mode**: The conservative scenario's free tier includes the core value proposition (conversation to PRD to TRD to code for 3 projects). If 3 free projects satisfy most users' needs (they only build 1-2 SaaS products), there is no conversion trigger. The 3-project limit may be too generous for the actual usage pattern.

**Evidence**: Open-source developer tools have notoriously low conversion rates (<1% for most). Developers are the most price-resistant user segment (5% median conversion vs 10% for non-dev products per Lenny's Newsletter). AI-powered apps churn 30% faster than non-AI apps (RevenueCat 2026).

**Mitigation plan**:
1. **Design the free/paid boundary with surgical precision BEFORE launch.** Free: generic question paths + basic template. Pro: industry-specific question paths, advanced Code Guidelines (testing strategy, CI/CD, monitoring, security hardening), template customization.
2. **A/B test the project limit.** Start at 3 projects free; if conversion is below 1% at Month 4, reduce to 1 project free with 7-day unlimited trial.
3. **Instrument conversion intent signals.** Track when free users attempt Pro-only features (which tells us what they actually want). Use this data to optimize the paywall boundary.
4. **Accept the consulting fallback.** If conversion structurally fails, pivot to consulting-led model where the free tool drives leads and enterprise engagements ($2K-$10K each) provide revenue.

### Risk 2: Competitors Replicate the Document Pipeline

**Probability**: 60-70%
**Impact**: HIGH — erosion of sole differentiator, but not immediately fatal if execution quality is superior
**Weighted Score**: HIGH

**Why this risk persists in conservative mode**: The document pipeline is a workflow design, not a defensible technology. Lovable, Cursor, or Replit could add "generate PRD before coding" in a single sprint. If Cursor (with its $2B+ ARR and massive engineering team) adds even basic document generation, our differentiation collapses.

**Evidence**: "Structured document pipeline" is not a technical moat. AI prompting strategies for PRD/TRD generation are not defensible IP. Competitors have 10-100x more engineering capacity.

**Mitigation plan**:
1. **Build depth, not breadth.** If Cursor adds basic PRD generation, our PRD must be demonstrably better through domain-specific questioning, multi-layer cross-validation, and professional-grade output. "10x better on one thing" beats "1x on many things."
2. **Bidirectional context propagation IS the moat.** Competitors can copy individual document generators. Replicating the full SOT chain (PRD to TRD to Code Guidelines with bidirectional traceability and change propagation) requires fundamental architecture changes that would take months, not sprints.
3. **Community knowledge as a moat.** Domain-specific question paths, user-contributed best practices, and a library of high-quality example outputs create switching costs that pure technology cannot.
4. **Accept partial overlap.** If Cursor adds document generation, position SaaS Auto-Builder as "the document pipeline for developers who want depth and local control." Not everyone wants their planning documents in a cloud IDE.

### Risk 3: CLI Adoption Too Niche (Under 200 Users by Month 6)

**Probability**: 25-35%
**Impact**: HIGH — insufficient user base to validate product-market fit or generate meaningful revenue
**Weighted Score**: HIGH

**Why this risk persists in conservative mode**: Even conservative user projections (200-300 at Month 6) require consistent organic growth from a narrow channel mix (Indie Hackers, Reddit, Claude Code communities). If none of these channels convert at expected rates, the user base may plateau below the minimum viable threshold for feedback, iteration, and revenue.

**Evidence**: No mass-market CLI developer tool has acquired significant users without corporate backing. Even experienced developers increasingly prefer GUI-based tools. The target audience (10+ year experienced developers who prefer CLI and want structured workflows) may be smaller than the estimated 90K-115K TAM suggests.

**Mitigation plan**:
1. **Validate earlier.** Do not wait until Month 6 to assess adoption. Set a Month 3 checkpoint: if fewer than 30 cumulative users, the distribution strategy is failing. Pivot to video-first content (YouTube tutorials showing the CLI in action reduce perceived CLI barrier).
2. **Leverage Claude Code's existing user base.** Claude Code users already operate in CLI. Target them specifically through r/ClaudeAI, Anthropic community forums, and Claude Code-specific content.
3. **Plan V2 GUI from Day 1.** The modular architecture explicitly supports adding a web interface without changing the core engine. If CLI adoption is below threshold at Month 6, accelerate GUI development for Month 9-10.
4. **Redefine "success" threshold.** If we have 100 highly engaged users (NPS 50+, 60%+ retention) but not 200, that may still indicate product-market fit within an ultra-niche. Quality of user engagement matters more than raw count at this stage.

---

## 8. Success Criteria

### WIN at Month 6: Conservative Success

| Metric | Target | Meaning |
|---|---|---|
| Cumulative Users | 200+ | The product has found its audience |
| 30-Day Retention | 50%+ | Users come back — the product delivers lasting value |
| Conversation Completion Rate | 70%+ | The Q&A flow is engaging and useful |
| NPS | 40+ | Users would actively recommend the tool |
| Pro Subscribers | 15+ | Someone is willing to pay — product-market fit signal |
| MRR | $285+ | Revenue exists, even if modest |
| Deployed SaaS from Tool | 10+ | The end-to-end pipeline actually works in production |
| Critical Bugs | 0 | Stability breeds trust |

**What "WIN" means**: The product has demonstrated organic demand, user satisfaction, and initial monetization. The foundation is solid enough to invest in V2 features (full 7-doc pipeline, additional templates, task generation). Growth is slow but real. The founder can confidently commit another 6 months.

### ACCEPTABLE at Month 6: Minimum Viable

| Metric | Target | Meaning |
|---|---|---|
| Cumulative Users | 100+ | Small but real audience |
| 30-Day Retention | 35%+ | Retention is below SaaS average (39%) but shows some stickiness |
| Conversation Completion Rate | 55%+ | Flow needs work but is functional |
| NPS | 25+ | Users are lukewarm but not hostile |
| Pro Subscribers | 3+ | At least someone paid — a signal worth investigating |
| MRR | $57+ | Technically non-zero revenue |

**What "ACCEPTABLE" means**: The product works but has not found product-market fit. The next 3 months (Month 7-9) should focus on user research: why are users not converting? Why is retention below target? The product is worth continuing but needs strategic adjustment, not just more features.

### FAIL at Month 6: Pivot or Wind Down

| Metric | Trigger |
|---|---|
| Cumulative Users | <50 |
| 30-Day Retention | <20% |
| Conversation Completion Rate | <40% |
| NPS | <+10 |
| Pro Subscribers | 0 |

**What "FAIL" means**: The product has not found an audience. Options:
1. **Pivot to consulting-first model**: Use the tool as a demonstration of expertise, sell consulting services
2. **Open-source everything**: Remove all monetization, maintain as a community project, build founder's reputation
3. **Graceful wind-down**: Archive the project, extract learnings, move on

### When to Accelerate: Signals for Shifting to Balanced Scenario

The conservative scenario should shift to the balanced scenario when ALL of the following are true:

1. **Product-market fit confirmed**: NPS consistently 40+ for 8+ weeks AND 30-day retention consistently 50%+ for 8+ weeks
2. **Monetization validated**: Conversion rate stable at 2%+ for 4+ weeks AND MRR shows month-over-month growth for 3 consecutive months
3. **Organic growth visible**: Weekly new users trending upward without paid acquisition AND organic mentions (Reddit, X, HN) average 3+/week
4. **Core quality bar met**: PRD/TRD document edit rate below 30% (users accept generated docs without major changes) AND template code passes all quality gates
5. **Founder capacity available**: Current workload is sustainable (no burnout signs) AND revenue trajectory suggests ability to hire first team member within 3 months

When these signals align, the response is: accelerate content production, launch the full 7-doc pipeline, begin V2 feature development (task generation, second template), and consider a ProductHunt re-launch or HN Show post for a growth push.

---

## 9. The "Boring but Alive" Argument

### Why 200 Happy Users Beats 2,000 Frustrated Users

The AI developer tools market in 2026 is defined by a paradox: explosive adoption and equally explosive disillusionment. Lovable has 25M+ projects created, but its code has been found with 16 critical vulnerabilities exposing 18,000+ users' data. Bolt.new users report spending $1,000+ on tokens for single projects. Replit Agent deleted a company's live production database. Devin completes only 3 out of 20 tasks. AI-generated code produces 1.7x more issues and fails 45% of security tests.

The market is screaming for something that actually works.

**A perfectly executed document pipeline with 200 happy users is better than a buggy auto-builder with 2,000 frustrated users because:**

**1. Trust compounds, hype decays.** The 200 users who trust your output become your marketing team. Every "I built my SaaS with this tool and it actually works in production" tweet is worth more than 1,000 ProductHunt upvotes. Developer trust is the hardest moat to build and the hardest to lose. Lovable's growth is impressive, but every security breach erodes the trust they have not yet fully built. We can build trust from Day 1 by shipping less but shipping right.

**2. Word-of-mouth has a quality threshold.** Users do not recommend tools that sort-of work. They recommend tools that surprise them. A PRD so good that a founder says "this understood my idea better than I could explain it" gets shared in Slack channels, Discord servers, and Twitter threads. A PRD that is "okay but I had to rewrite half of it" gets forgotten. The difference between 7/10 quality and 9/10 quality is the difference between zero virality and organic virality. We cannot afford paid marketing; organic recommendation is our only viable channel.

**3. Retention is cheaper than acquisition.** Acquiring a new CLI tool user through organic content costs an estimated $30-$80 in founder time (writing posts, engaging in communities, creating tutorials). Retaining an existing user costs approximately $0 (the product just needs to keep working well). A 200-user base with 60% retention has 120 active users next month. A 2,000-user base with 20% retention has 400 active users next month — but required 10x the acquisition effort and produces 10x the support burden, bugs, and negative word-of-mouth from the 1,600 who left.

**4. Quality data beats quantity data.** 200 engaged users who complete the full flow (conversation to PRD to TRD to code) and provide detailed feedback generate better product insight than 2,000 users who try the tool once and bounce. Each completed workflow tells us which questions work, which document sections need improvement, and which template patterns produce the best code. This feedback loop is the engine of product improvement.

**5. The "boring" business is the one that survives.** The indie hacker graveyard is filled with products that launched big, grew fast, and died when the founder burned out supporting a scale the product was not ready for. The products that survive are the ones that grow at a pace the founder and the product can sustain. 200 users at Month 6, growing 20% monthly, becomes 3,700 users by Month 18. That is the growth curve of a product that actually works, growing at a rate the founder can support.

**The conservative scenario does not aim for obscurity. It aims for inevitability.** A small, fiercely loyal user base that organically grows because the product genuinely delivers is not a failure of ambition — it is the foundation of every durable company. Stripe launched with 7 beta users. Basecamp launched with a few hundred. They grew because each individual user had an excellent experience, not because they chased vanity metrics.

We will not have 25 million projects. We will have 200 projects where the founder looked at the generated PRD and said: "This is better than what I would have written myself." That is the signal that matters.

---

## 10. Team Signatures (Simulated)

### Market Perspective

**Verdict**: CONCERN (Accept with reservations)

**Reasoning**: The conservative scenario correctly identifies the narrow but defensible niche. However, I have two material concerns:

1. **The 14-week competitive window is real.** By the time the conservative scenario completes Month 6 (launch), it will be September 2026. Cursor, Lovable, or Vercel may have already added document generation features. The conservative timeline's generosity with buffers may cost us first-mover advantage in the only niche we can win. I would prefer compressing M1 to 10 weeks and launching a public beta at Month 4 instead of Month 5.

2. **Excluding one-click deployment is the riskiest exclusion.** The Cautious Market Report identified this as a MUST-HAVE. Users who can generate code but cannot deploy it will generate code in SaaS Auto-Builder and then deploy with Lovable — making us a free planning tool for a competitor's deployment business. The conservative scenario's counter-argument ("our users can handle `vercel deploy`") may be true but underestimates the value of a seamless end-to-end experience.

**What would change my mind**: Evidence from the private beta (Month 4-5) that deployment is NOT a significant pain point. If beta users are deploying successfully without tool assistance, the exclusion is validated.

**Signature**: Market Perspective — Conditionally Accepts

---

### User Perspective

**Verdict**: ACCEPT

**Reasoning**: The conservative scenario aligns precisely with what power users need: fewer features, higher quality. Three specific endorsements:

1. **The quality standards are specific and measurable.** "Generated PRD is usable without editing by a senior PM" is a concrete bar, not a vague aspiration. This is the kind of quality commitment that earns user trust.

2. **First-run experience as P0 is correct.** Too many developer tools neglect onboarding because "our users are technical." Technical users still abandon tools with confusing setup processes. The 15-minute bar is achievable and meaningful.

3. **The exclusion list is honest.** Listing what is NOT included, with specific reasons and re-entry conditions, shows respect for the user's intelligence. Users distrust products that promise everything. Users trust products that promise less and deliver more.

**One suggestion**: Add an explicit feedback mechanism in the CLI (e.g., `saas-builder feedback` command) that makes it trivially easy for users to report issues and request features. The 200-user base is small enough for the founder to personally respond to every piece of feedback, which builds extraordinary loyalty.

**Signature**: User Perspective — Accepts

---

### Tech Perspective

**Verdict**: AGREE

**Reasoning**: The conservative scenario is the technically sound choice. Four specific agreements:

1. **Modular monolith with clean interfaces is the correct architecture.** The temptation is to over-engineer (microservices, event sourcing, etc.) for a product that does not yet have users. The modular monolith delivers simplicity now with a credible migration path to more complex architectures if/when scale demands it. The module boundary enforcement (linting rule preventing cross-module imports) is the critical discipline that makes this work.

2. **85%+ test coverage is ambitious but achievable for a focused feature set.** With only 4 features, the testing surface is manageable. 85% coverage on 4 features is dramatically more valuable than 40% coverage on 10 features.

3. **One template is the right call.** Next.js + Supabase + Stripe is the most common indie SaaS stack and has the largest community for troubleshooting. Supporting one template means we can make that template genuinely production-quality: proper error handling, security best practices, accessibility basics, and tested auth/payment flows. A second template at this stage would halve our quality investment.

4. **The `LLMClient` abstraction is architecturally wise.** Even though V1 only ships Claude, having the interface layer from Day 1 means multi-LLM support in V2 is an additive change, not a refactoring project. This is the right level of future-proofing: plan the interface, defer the implementation.

**One technical concern**: The 7-week estimate for PRD + TRD generation with bidirectional context propagation may be optimistic even with 40% buffer. Cross-document validation and bidirectional change propagation are architecturally non-trivial. I recommend a Week 8 technical review specifically for this component, with an explicit option to simplify (unidirectional propagation only) if bidirectional proves too complex within the timeline.

**Signature**: Tech Perspective — Agrees

---

### Business Perspective

**Verdict**: ACCEPT (with one non-negotiable condition)

**Reasoning**: The conservative scenario's financial model is the most survivable option. Three endorsements:

1. **$10,000-$30,000 Year 1 revenue is honest.** Most indie products earn less than this. Setting this as the target (rather than the Business discussion's $18K-$45K) means we are less likely to be disappointed and more likely to make sound decisions when actual data arrives.

2. **The bounded downside argument is the strongest case for proceeding.** $9,000-$11,400 total cost at Month 6, with residual value in the open-source asset, founder expertise, and community relationships, means the worst case is a modest loss and a career asset. This passes the "regret minimization" test: at Month 6, will the founder regret having tried? Almost certainly not.

3. **BYOK as a business model feature (not a limitation) is correct framing.** "Your data never touches our servers" and "You control your AI costs" are genuine selling points in a market where Bolt.new users report $1,000+ surprise bills. Near-zero marginal cost per user means profitability at remarkably low scale (~80 Pro subscribers).

**Non-negotiable condition**: The free/paid boundary MUST be designed and tested BEFORE public launch (Month 6). This is not a feature — it is the business model. The 3-project limit and industry template paywall must be validated with at least 10 beta users to ensure the boundary feels fair (not punitive) while creating genuine conversion motivation. Launching with the wrong boundary means either (a) zero revenue or (b) community backlash, both of which are business-killing for a bootstrapped product.

**Signature**: Business Perspective — Conditionally Accepts

---

## Appendix: Data Sources Cross-Referenced

All projections in this PRD are grounded in data from Phase 1 (8 research branches) and Phase 2 (4 discussion perspectives), specifically:

- **Market size**: Cautious Market Report TAM of 90K-115K users, $22M-$69M ARR ceiling
- **Conversion rates**: Monetizely open-source SaaS benchmark (0.3-3%), Lenny's Newsletter developer tools median (5% including GUI tools), conservative CLI estimate (1-1.5%)
- **Competitor data**: Cursor $2B+ ARR, Lovable $300M ARR, Replit $265M ARR, combined funding $4B+ (all from Cautious Market Report with sourced citations)
- **Revenue benchmarks**: IndieMarkerAnalytics 2024-2025 (326 projects, median $500/mo), Business Discussion analysis
- **Risk probabilities**: Business Discussion weighted risk matrix
- **Technical estimates**: Phase 2 Tech Discussion Green Zone assessment (26 production weeks, 7 Green Zone features)
- **Quality benchmarks**: AI code generates 1.7x more issues (CodeRabbit Dec 2025), 45% fail security tests (Veracode 2025)
- **Retention/churn benchmarks**: SaaS average 39% 30-day retention (Pendo 2025), SMB developer tool churn 3-5%/month
- **LTV/CAC**: Business Discussion blended LTV $203-$297, blended CAC $30-$80, ratio 2.5-10x
