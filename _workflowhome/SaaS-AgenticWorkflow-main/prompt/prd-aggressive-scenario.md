# SaaS Auto-Builder PRD: Aggressive Scenario

**Scenario**: AGGRESSIVE
**Philosophy**: "Now or never. Take the risk, capture the market before the window closes."
**Date**: 2026-03-12
**Status**: Phase 3 — Convergence Branch 3.A

---

## 1. Executive Summary

### Why Aggressive?

Three converging market signals create a window that closes in 14 weeks:

**Signal 1: The Spec-Driven Development vacuum is real and unfilled.**
ThoughtWorks identified spec-driven development as a key emerging practice in late 2025. Addy Osmani published influential guidance on writing specs for AI agents. Yet as of March 2026, zero products productize this workflow. Every competitor — Cursor ($2B+ ARR), Lovable ($300M ARR), Replit ($265M ARR), Bolt.new ($40M ARR) — starts at the code level. The structured document pipeline (PRD -> TRD -> Code Guidelines -> Tasks -> Code) has no direct competitor. This gap will not persist: any of these $4B+ funded competitors can build a basic document pipeline in a single engineering sprint. We have 14 weeks of first-mover advantage, not 14 months.

**Signal 2: The trust deficit is creating defector demand right now.**
Lovable exposed 18,000 users' data through 16 vulnerabilities (6 critical). Bolt.new users report $1,000+ token bills for single projects. Replit Agent deleted a company's live production database. Devin completes only 3 of 20 tasks. AI-generated code produces 1.7x more issues and 45% fail security tests (CodeRabbit Dec 2025, Veracode 2025). These failures are not anecdotal — they represent systemic quality gaps in code-first approaches. Users burned by these tools are actively seeking alternatives NOW, not in 6 months.

**Signal 3: The solo founder explosion demands a structured tool immediately.**
Solo founders using AI tools increased +340% YoY. MVP development time dropped to 3.2 weeks. The micro-SaaS market is projected to grow from $15.7B to $59.6B by 2030. These founders need exactly what we build: conversational guidance from idea to implementation. But they form tool loyalty quickly — once they adopt Cursor or Lovable as their workflow, switching costs compound monthly. Every week we delay, potential users become locked-in competitors' customers.

**The aggressive bet**: Sacrifice long-term code purity for maximum feature coverage in 14 weeks. Ship the full document pipeline AND working code generation AND cross-validation — not just the "safe" minimum. Accept that Month 7 will require significant refactoring. The alternative — shipping a minimal PRD-only tool — means entering a saturated market with a product that is half-differentiated and easily replicated.

**What makes this worth the risk**: Near-zero marginal cost (BYOK model), low burn rate ($700-$1,900/mo), and bounded downside. If the aggressive bet fails, the worst case is an open-source tool with 100-200 users and a founder with deep AI workflow expertise. If it succeeds, we capture first-mover position in an unoccupied category within a $40B+ combined market.

---

## 2. Feature Set (10 Features)

### Feature Matrix

| # | Feature | Priority | Dev Time | Risk | Business Justification |
|---|---------|----------|----------|------|----------------------|
| F1 | Conversational SaaS Definition Engine | P0 | 3 weeks | Low | **Acquisition + Conversion**: This IS the product. The quality of 5-7 smart questions determines everything downstream. 55% of trial cancellations happen on Day 0 — this is where users decide to stay or leave. |
| F2 | Full 7-Document Pipeline | P0 | 4 weeks | Medium | **Differentiation + Retention**: PRD + User Journey + TRD + Code Guidelines + UI Guidelines + IA + Tasks. No competitor generates ANY of these. This is the only true differentiator — shipping 3 docs instead of 7 is half-differentiated and easily replicated. |
| F3 | Cross-Document Validation Engine | P0 | 2.5 weeks | Medium | **Retention + Quality**: Bidirectional traceability between documents. If TRD references a feature not in PRD, flag it. If Tasks reference a non-existent API, flag it. This is what makes the pipeline a SYSTEM, not just 7 separate files. Without this, we are ChatGPT with a markdown template. |
| F4 | Context Propagation (Document Linkage) | P0 | 2 weeks | Medium | **Conversion**: Changes to PRD automatically cascade to TRD, Code Guidelines, and Tasks. This is the "magic moment" where users realize the documents are alive, not static. Phase 2 discussions rated this 3.5/4 consensus — near-universal agreement it matters. |
| F5 | Editable Intermediate Documents | P0 | 1.5 weeks | Low | **Retention + Trust**: Users can edit any generated document and re-propagate changes. This removes the "black box" anxiety that kills trust in AI tools. Cursor/Copilot users expect to modify AI output — if we lock documents, we lose this audience. |
| F6 | Next.js + Supabase + Stripe Template | P0 | 3 weeks | Low | **Conversion**: The proof that the pipeline produces real output. "Idea to running code in 30 minutes" is the viral story. Without working code, we are a document generator competing against ChatGPT. With code, we are the bridge from planning to implementation. |
| F7 | First-Run Experience (<15 min) | P1 | 2 weeks | Low | **Acquisition**: Install to first generated PRD in under 15 minutes. CLI setup, first question flow, output preview. If this takes 30+ minutes, we lose the "try it once" audience permanently. |
| F8 | Free/Paid Tier Boundary System | P1 | 1.5 weeks | High | **Revenue**: 3-project limit on free tier. Industry-specific templates, advanced code guidelines, multi-framework support behind paywall. This is THE business model. Getting the boundary wrong is fatal: too generous = zero revenue (45% probability per Business perspective), too restrictive = zero adoption. |
| F9 | Industry-Specific Template Packs (3 verticals) | P1 | 3 weeks | Medium | **Revenue**: E-commerce, marketplace, and project management SaaS templates with domain-specific questioning, compliance requirements, and architecture patterns. This is the "knowledge layer" that justifies $19/mo — the premium value that cannot be replicated with the free tier. |
| F10 | CLI Dashboard & Project Management | P2 | 2 weeks | Low | **Retention**: Project history, status tracking, multi-project overview. Prevents "one-and-done" churn. Users who build a second project have 3x higher LTV. |

### Total Development Time: 24.5 weeks

With 26 available production weeks in 6 months, this leaves 1.5 weeks of buffer — intentionally tight. The aggressive scenario accepts this constraint. Buffer is consumed by bug fixes and unforeseen integration issues.

### Feature Dependency Chain

```
F1 (Conversational Engine) ──→ F2 (7-Doc Pipeline) ──→ F3 (Cross-Validation)
         │                            │                        │
         │                            ├──→ F4 (Context Propagation)
         │                            │
         │                            ├──→ F5 (Editable Docs)
         │                            │
         │                            └──→ F6 (Next.js Template)
         │
         └──→ F7 (First-Run Experience)

F8 (Free/Paid Boundary) — independent, ships parallel to F2-F6
F9 (Industry Templates) — depends on F2 + F6 being stable
F10 (CLI Dashboard) — depends on F1, independent of F2-F6
```

---

## 3. Architecture Choices

### Tech Debt We Accept

| Area | Debt Accepted | Justification | Repayment Timeline |
|------|--------------|---------------|-------------------|
| **Monolithic CLI architecture** | All 7 document generators in a single Python package, no module boundaries | Faster iteration, simpler debugging, avoids premature abstraction. At <500 users, scaling is irrelevant. | Month 7-8: Extract generators into pluggable modules |
| **Template coupling** | Next.js template is hardcoded, not abstracted into a template engine | First template must be perfect; abstraction before validation is waste. | Month 5-6: Abstract template engine before adding second framework |
| **Cross-validation as post-hoc checks** | Validation runs after generation, not as inline constraints during generation | Building inline constraints doubles development time. Post-hoc catches 80% of issues at 30% of the dev cost. | Month 8-10: Move to constraint-based generation |
| **Single LLM dependency (Claude)** | No LLM abstraction layer. Directly calls Claude API. | Claude Code is our platform. Multi-LLM support triples testing surface area for marginal benefit. 90% of target users already use Claude. | Month 9-12: Abstract LLM layer only if Anthropic pricing changes threaten viability |
| **Minimal test coverage** | Unit tests for cross-validation and context propagation only. Integration tests deferred. | These two features are the highest-risk components. Testing everything else slows shipping by 3-4 weeks. | Month 4-6: Expand test coverage to 60%+ as features stabilize |
| **No telemetry infrastructure** | Opt-in CLI analytics via simple JSON logging, no backend analytics pipeline | Building analytics infrastructure is a 2-week project with zero user-facing value. JSON logs + manual analysis suffice for 350 users. | Month 6+: Implement proper telemetry when user base exceeds 500 |

### Shortcuts Justified

1. **BYOK only (no API key management)**: Users bring their own Claude API key. This is not a shortcut — it is a structural decision. Zero marginal cost per user, full data sovereignty, no API billing infrastructure.

2. **Markdown-only output**: All 7 documents generate as `.md` files. No PDF export, no web preview, no Notion integration. Markdown is the native format for developers. Adding export formats costs 2 weeks for <5% of user requests.

3. **No deployment pipeline**: We generate code; the user deploys it. Lovable/Bolt.new deploy in one click, but they also control the hosting. Our product philosophy is "you own everything." Deployment guidance in the TRD is sufficient for V1. Full deployment automation is a V2 feature that requires maintaining cloud provider integrations — a different business.

4. **No web GUI**: CLI-only. The Phase 2 business discussion confirmed: 12,000 GUI users in 6 months is fantasy for a bootstrapped product. Our target (power users, 10+ years experience) lives in the terminal. A web GUI is 8-12 weeks of development for a demographic we explicitly exclude from V1.

### Non-Negotiable Quality Standards (Even in Aggressive Mode)

These are NOT compromised regardless of timeline pressure:

| Standard | Reason | Enforcement |
|----------|--------|-------------|
| **Cross-validation correctness** | A single false-negative (missed inconsistency between PRD and TRD) destroys trust permanently. Users do not give AI tools a second chance after a quality failure. | Unit tests with 50+ test cases covering edge cases. Manual QA for every release. |
| **Context propagation integrity** | If editing a PRD feature name does not cascade to TRD and Tasks, the "living document" value proposition is a lie. | Integration tests for all propagation paths. Regression testing on every change. |
| **Generated code runs on first attempt** | If `npm install && npm run dev` fails, the user closes the terminal and never returns. Lovable gets away with broken code because they control the environment. We don't. | Template code is tested against clean Node.js 18/20 installs before every release. |
| **Conversational flow completes without confusion** | If a user abandons the questionnaire mid-flow, everything downstream is wasted. Target: 70%+ completion rate. | A/B testing question wording with first 50 users. Iterative refinement based on abandonment data. |
| **Security of generated code** | Competitors' 45% security failure rate is our #1 marketing differentiator. Our generated code MUST pass basic OWASP checks. | Security linting (eslint-plugin-security, Semgrep) built into template CI. |

---

## 4. Timeline (6 Months)

### Month 1-2 (M1): Foundation + Core Pipeline — "Idea to Documents in 10 Minutes"

**Goal**: Ship conversational engine + full 7-doc pipeline + editable documents. User can go from "I want to build X" to 7 professionally-structured documents in a single session.

| Week | Deliverable | Feature | Dev Weeks |
|------|-------------|---------|-----------|
| W1-W3 | Conversational SaaS Definition Engine | F1 | 3.0 |
| W3-W5 | PRD + TRD Generation (first 2 of 7 docs) | F2 (partial) | 2.0 |
| W5-W7 | User Journey + Code Guidelines + UI Guidelines | F2 (partial) | 2.0 |
| W7-W8 | IA + Task Generation (final 2 of 7 docs) | F2 (complete) | Overlap with above, net 0 additional |
| W7-W8.5 | Editable Intermediate Documents | F5 | 1.5 |
| W8-W9 | First-Run Experience Polish | F7 | Partial (1.0 of 2.0) |

**M1 Milestone**: A user can install the CLI, answer 5-7 questions, and receive 7 polished documents in under 15 minutes. Documents are editable. No code generation yet.

**M1 Dev Weeks Used**: 9.5 / 26 total

**Launch Event**: Private beta to 15-25 users sourced from Claude Code Discord, r/ClaudeAI, and personal network. Focus: conversational quality feedback and document quality assessment.

### Month 3-4 (M2): Code Generation + Validation — "Documents to Running Code"

**Goal**: Ship cross-validation, context propagation, and Next.js template. User can go from documents to working, deployable code. Free/paid boundary goes live.

| Week | Deliverable | Feature | Dev Weeks |
|------|-------------|---------|-----------|
| W9-W11.5 | Cross-Document Validation Engine | F3 | 2.5 |
| W11.5-W13.5 | Context Propagation (bidirectional) | F4 | 2.0 |
| W13.5-W16.5 | Next.js + Supabase + Stripe Template | F6 | 3.0 |
| W16-W17.5 | Free/Paid Tier System (license keys, 3-project limit) | F8 | 1.5 |
| W17-W18 | First-Run Experience Completion | F7 | 1.0 (remaining) |

**M2 Milestone**: Full pipeline works end-to-end. User answers questions -> gets 7 validated, cross-linked documents -> gets working Next.js+Supabase+Stripe code. Free tier limits enforced. Pro tier ($19/mo) available.

**M2 Dev Weeks Used**: 10.0 / 26 total (cumulative: 19.5)

**Launch Event**: Public beta on Product Hunt. Target: 80-120 total users. First paying customers. "Build a SaaS in 30 minutes" demo video.

### Month 5-6 (M3): Revenue Features + Polish — "From Tool to Business"

**Goal**: Ship industry templates, CLI dashboard, polish based on user feedback. Reach $10K MRR target.

| Week | Deliverable | Feature | Dev Weeks |
|------|-------------|---------|-----------|
| W19-W22 | Industry Template Packs (3 verticals) | F9 | 3.0 |
| W22-W24 | CLI Dashboard & Project Management | F10 | 2.0 |
| W24-W26 | Bug fixes, performance optimization, UX polish | Buffer | 1.5 |

**M3 Milestone**: Three industry templates live (e-commerce, marketplace, project management). Multi-project support. Stable product with 250-500 users and $10K+ MRR.

**M3 Dev Weeks Used**: 6.5 / 26 total (cumulative: 26.0 — fully consumed)

### Timeline Visualization

```
Month 1      Month 2      Month 3      Month 4      Month 5      Month 6
|------------|------------|------------|------------|------------|------------|
[F1: Conversational Engine (3w)]
   [F2: 7-Doc Pipeline (4w)                ]
              [F5: Editable Docs (1.5w)]
              [F7: First-Run (1w)]
                          [F3: Cross-Validation (2.5w)]
                             [F4: Context Propagation (2w)]
                                        [F6: Next.js Template (3w)]
                                        [F8: Free/Paid (1.5w)]
                                        [F7: First-Run completion (1w)]
                                                    [F9: Industry Templates (3w)]
                                                              [F10: CLI Dashboard (2w)]
                                                                         [Buffer (1.5w)]

PRIVATE BETA ─────────────────── PUBLIC BETA ─────────────── REVENUE GROWTH
(15-25 users)                    (80-120 users)                (250-500 users)
                                 Product Hunt launch            $10K MRR target
```

---

## 5. Revenue Targets (Aggressive)

### Pricing Model

| Tier | Price | What's Included |
|------|-------|-----------------|
| **Community (Free)** | $0 | Conversational engine + 7-doc pipeline (generic templates only) + basic Next.js template. **3-project limit.** |
| **Pro** | $29/mo or $249/year | Unlimited projects. Industry-specific templates (e-commerce, marketplace, PM). Advanced code guidelines (testing, CI/CD, monitoring). Priority support. |
| **Team** | $59/mo or $499/year | Everything in Pro. Shared template library. Custom template creation. Multi-agent orchestration configs. |
| **Enterprise** | $2,000-$10,000/engagement | Custom workflow design. On-site setup and training. Proprietary template creation. |

**Why $29/mo, not $19/mo**: The aggressive scenario prices higher because (a) we ship more value (10 features vs 5-7), (b) the 14-week window means we need fewer users to hit revenue targets, and (c) developer tools at $20/mo are commodity pricing — $29/mo signals premium quality. If conversion rate drops below 1.5% at $29, we can always drop to $19. Pricing down is easy; pricing up after launch is nearly impossible.

### Revenue Projections

| Month | Cumulative Users | Free Users | Pro Subs | Team Subs | Enterprise | MRR |
|-------|-----------------|------------|----------|-----------|------------|-----|
| 1 | 25 | 25 | 0 | 0 | 0 | $0 |
| 2 | 75 | 73 | 2 | 0 | 0 | $58 |
| 3 | 200 | 185 | 12 | 3 | 0 | $525 |
| 4 | 500 | 450 | 38 | 8 | 1 | $3,674 |
| 5 | 1,200 | 1,080 | 90 | 20 | 1 | $3,790* + enterprise |
| 6 | 2,500 | 2,225 | 200 | 50 | 2 | **$10,750** |

*Month 5-6 MRR includes: (200 Pro x $29) + (50 Team x $59) + (2 Enterprise at $2,500 avg) = $5,800 + $2,950 + $5,000 = $10,750 + recurring enterprise.

### Conversion Rate Assumptions

| Metric | Assumption | Benchmark Source |
|--------|-----------|-----------------|
| Free-to-Pro conversion | 4% by Month 6 | Dev tools median 2-5% (Lenny's); we target upper end due to aggressive free/paid boundary |
| Pro-to-Team upgrade | 20% of Pro convert within 3 months | SaaS upsell benchmarks: 15-25% |
| Monthly churn (Pro) | 5% | Small SaaS average: 3-5% |
| Monthly churn (Team) | 3% | Team accounts are stickier |
| Enterprise close rate | 1 per 200 Pro inquiries | Conservative for high-touch sales |

### What Makes $10K MRR Aggressive but Not Fantasy

The sustainable scenario targets $1,500-$3,000 MRR at Month 6 with 250-350 users. The aggressive scenario targets $10,750 MRR with 2,500 users. The gap requires:

1. **10x more users** (2,500 vs 250): Achieved through Product Hunt launch (target: 500 signups day 1), HN front page post, aggressive content marketing (weekly tutorial posts), and leveraging the "spec-driven development" narrative that ThoughtWorks legitimized. This requires at least one viral moment.

2. **Higher price point** ($29 vs $19): Justified by more features (10 vs 5-7) and the "premium alternative to broken AI builders" positioning.

3. **Higher conversion rate** (4% vs 2%): Justified by aggressive free/paid boundary (3-project limit) and industry templates that are genuinely impossible to replicate with the free tier.

4. **Enterprise revenue** ($5,000/mo from 2 engagements): The most uncertain component. Requires proactive outreach to companies already using Claude Code internally. If enterprise revenue is $0, MRR drops to $8,750 — still exceeding $8K.

### Revenue Sensitivity Analysis

| Scenario | Users | Conversion | Price | MRR (Month 6) |
|----------|-------|-----------|-------|---------------|
| Bull case | 3,500 | 5% | $29 | $15,225 |
| **Base case** | **2,500** | **4%** | **$29** | **$10,750** |
| Bear case | 1,200 | 2.5% | $29 | $4,350 |
| Worst case | 500 | 1.5% | $29 | $1,305 |

If worst case materializes at Month 4 (tracking toward $1,305), trigger the pivot to conservative — see Section 7.

---

## 6. Top 5 Risks with Contingency Plans

### Risk 1: Free Tier "Good Enough" — Nobody Converts

**Probability**: 45%
**Impact**: FATAL — business generates zero revenue
**Weighted Score**: CRITICAL

**Why this is the #1 risk**: The Phase 2 business discussion identified this as the highest-weighted threat. Open-source developer tools have notoriously low conversion rates (<1%). The free tier includes the full 7-doc pipeline — the core value proposition. If users can get 90% of the value for free, they will.

**Mitigation**:
- 3-project limit is the primary conversion lever. After 3 projects, the free user MUST subscribe. This creates a natural usage-based conversion trigger that activates only for engaged users.
- Industry templates require deep domain knowledge (healthcare compliance, marketplace escrow, financial regulations) that genuinely cannot be replicated by editing generic templates.
- Advanced code guidelines (testing strategies, CI/CD configuration, monitoring setup, security hardening) are premium-only. These are the features that separate a prototype from production.
- The free tier generates CODE from a basic template only. Pro templates generate code with auth, payments, email, admin dashboard — the features that take weeks to build manually.

**Trigger for pivot**: If free-to-paid conversion is <1.0% at Month 4 with 500+ free users, redesign the boundary. Options: (a) reduce free tier to 3-doc pipeline (PRD + TRD + Tasks only), (b) switch to usage-based pricing (pay per document generation after first project), (c) abandon freemium entirely and go trial-based (14-day free trial, then $29/mo).

### Risk 2: Competitors Add Document Pipelines Within 14 Weeks

**Probability**: 60-70%
**Impact**: HIGH — erosion of primary differentiator
**Weighted Score**: HIGH

**Why this is likely**: "Structured document pipeline" is not a technical moat — it is a workflow design. Cursor, Lovable, and Replit each have 100+ engineers who could build basic PRD generation in weeks. The spec-driven development trend is visible to everyone.

**Mitigation**:
- **Depth over breadth**: If Cursor adds basic PRD generation, our PRD must be 10x better through domain-specific questioning, cross-validation, and professional-grade output with architecture decision records.
- **Document linkage is the real moat**: Competitors can copy individual documents. Replicating the SOT chain (PRD -> TRD -> Code Guidelines -> Tasks with bidirectional traceability and automated cross-validation) requires fundamental architecture changes that take months, not weeks.
- **Community lock-in**: User-created templates, shared question sets, domain-specific workflows create switching costs that pure technology cannot.
- **Speed of iteration**: Ship weekly improvements to document quality. Every week, the AI's questioning becomes smarter based on user feedback. This creates a compounding advantage.

**Trigger for pivot**: If a direct competitor (specifically Cursor or Lovable) launches a document pipeline with >3 documents AND cross-validation by Month 3, accelerate timeline: skip F9 (industry templates) and F10 (dashboard), redirect 5 weeks to deepening document quality and building unique features competitors cannot easily copy (e.g., multi-agent implementation orchestration).

### Risk 3: CLI Adoption Too Niche — <500 Users at Month 6

**Probability**: 25-35%
**Impact**: FATAL — cannot sustain business at any conversion rate
**Weighted Score**: HIGH

**Why this is real**: No mass-market CLI developer tool has acquired 2,500 users in 6 months without corporate backing. Even experienced developers increasingly prefer GUI-based tools. The Phase 2 business discussion estimated realistic TAM at 90K-115K users total — capturing 2.8% of TAM in 6 months is aggressive.

**Evidence against this risk**: Claude Code itself proves CLI AI tools have a market. 58 of 99 surveyed developers use Claude Code. Power users are vocal evangelists — one popular HN post could drive 500+ signups in a day.

**Mitigation**:
- Target Claude Code's existing user base as initial community (they already use CLI, already have Claude API keys, already understand the value proposition).
- Plan V2 web GUI architecture from Day 1 but do NOT build it in V1.
- Invest heavily in video content showing the CLI in action (reduces perceived barrier).
- Partner with Claude Code community leaders for early access and testimonials.

**Trigger for pivot**: If <200 total users at Month 4, activate GUI acceleration: begin V2 web interface development immediately, targeting Month 8 launch. Redirect 50% of feature development to a lightweight web wrapper around the CLI engine.

### Risk 4: Anthropic Dependency (Claude Code Platform Risk)

**Probability**: 15-25%
**Impact**: EXISTENTIAL — product becomes uneconomical or unusable
**Weighted Score**: MEDIUM-HIGH

**Why this matters**: The product is built entirely on Claude Code CLI. Anthropic could:
- Raise API pricing (Claude 3 Opus costs 3x what Claude 3 Sonnet costs — a tier change doubles user costs)
- Deprecate or pivot Claude Code's architecture
- Launch their own SaaS builder (they already have Claude Artifacts)
- Impose rate limits that throttle our generation pipeline

**Mitigation**:
- Abstract the LLM interaction into a thin adapter layer from Day 1. This costs <1 week and enables future multi-LLM support without rewriting the core.
- Monitor Anthropic's pricing and product announcements weekly.
- Maintain a "Plan B" document specifying what it would take to port to OpenAI/Gemini (estimated: 2-3 weeks of adapter work).
- Build the product's value in the WORKFLOW, not the MODEL. If Claude is swapped for GPT-5, the conversational flow, document templates, cross-validation logic, and industry knowledge remain.

**Trigger for pivot**: If Anthropic announces >50% API price increase or Claude Code deprecation, immediately begin multi-LLM port. Budget: 3 weeks of emergency development.

### Risk 5: Quality of Generated Output is Not "10x Better"

**Probability**: 30-40%
**Impact**: HIGH — users try once and never return
**Weighted Score**: HIGH

**Why this is dangerous**: The aggressive scenario's marketing message is "production-quality alternative to broken AI builders." If our PRDs are generic, our TRDs are boilerplate, and our generated code has the same 45% security failure rate as competitors, the positioning collapses. We promised premium; we delivered commodity.

**Mitigation**:
- Spend 60% of M1 development time on conversational question quality. The questions determine everything downstream.
- Benchmark every generated document against manually-written equivalents from senior PMs/architects. If an experienced user says "I would have written the same thing," we win. If they say "this is a template with my product name inserted," we fail.
- Security linting is non-negotiable: generated code MUST pass eslint-plugin-security and Semgrep basic checks.
- Early beta users (15-25) provide feedback before public launch. Iterate question flow 3-5 times based on real usage.

**Trigger for pivot**: If NPS is below +20 at Month 3 after 80+ users, the product quality is insufficient. Pause all feature development. Redirect 100% of effort to improving conversational flow and document generation quality for 4 weeks.

---

## 7. Success Criteria

### WIN at Month 6

All of the following must be true:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Monthly Recurring Revenue | >= $10,000 | Stripe dashboard |
| Cumulative Users | >= 2,000 | CLI install + activation count |
| Free-to-Paid Conversion | >= 3.5% | Paid subscribers / total registered |
| 30-Day Retention (Free) | >= 45% | % of users who run CLI again within 30 days |
| Net Promoter Score | >= +35 | Monthly survey (minimum 50 responses) |
| Conversation Completion Rate | >= 70% | % of users who complete full Q&A flow |
| Deployed SaaS Products | >= 150 | Projects that produce runnable code |
| Zero critical security vulnerabilities in generated code | 0 critical, <3 high | Automated security scan of template output |

**What this WIN means**: The product has demonstrated product-market fit in a defensible niche. Revenue covers burn rate with margin. User growth is organic. The spec-driven development category exists and we own it. Month 7+ is about scaling, not survival.

### LOSS at Month 6

Any TWO of the following constitute a LOSS:

| Criterion | Threshold | Interpretation |
|-----------|-----------|---------------|
| MRR < $3,000 | Well below aggressive target | Revenue model is broken; free tier too generous or value proposition insufficient |
| Users < 500 | 80% below target | CLI niche is too small; need GUI or platform pivot |
| Conversion < 1.5% | Below industry floor | Premium value is not compelling; users see no reason to pay |
| NPS < +15 | Users are dissatisfied | Product quality is insufficient; generated output is not good enough |
| Retention < 25% | Users try once and leave | The tool solves a one-time problem, not a recurring need |
| 0 enterprise inquiries | No high-value segment interest | Product is hobbyist-only; no path to sustainable revenue |

**What this LOSS means**: The aggressive bet did not pay off. The market is either too small, the product is insufficiently differentiated, or the timing was wrong.

### Kill Criteria: When to Abandon Aggressive and Switch to Conservative

**Month 3 Early Warning Assessment** (mandatory review):

| Signal | Threshold | Action |
|--------|-----------|--------|
| Users < 80 | Tracking 4x below M6 target | Pause feature development. Diagnose: is it awareness (marketing) or product quality? 2-week sprint focused on whichever is failing. |
| Conversion < 0.8% | Structurally broken | Redesign free/paid boundary immediately. Consider: remove free tier entirely, switch to 14-day trial model. |
| NPS < +10 | Product is actively bad | Stop all feature development. Redirect 100% effort to improving core experience for 4 weeks. |
| Completion rate < 40% | Conversational flow is broken | Emergency UX redesign of question flow. User interviews with all 80 users. |

**Month 4 Go/No-Go Decision** (hard deadline):

If 3+ of 4 Month 3 signals are in "action" territory:
- **SWITCH TO CONSERVATIVE**: Abandon F9 (industry templates), F10 (dashboard), and F8 (paid tier). Make the entire product free and open-source. Focus remaining 2 months on polishing core pipeline quality. Pivot business model to consulting + sponsored templates.
- **Reasoning**: Aggressive failed at 4 months means the market signal was misread. Doubling down wastes runway. Conservative preserves the codebase, community, and optionality.

---

## 8. Team Signatures (Simulated)

### Market Perspective

**Verdict**: AGREE

> The aggressive scenario correctly identifies the 14-week window as real and closing. The spec-driven development category is genuinely unoccupied. No competitor — not even Cursor at $29.3B valuation — offers a structured document pipeline with cross-validation. The risk of being too late outweighs the risk of being too early.
>
> **One concern**: The 2,500 user target requires at least one viral moment (Product Hunt, HN front page). Organic growth alone cannot reach this number in 6 months for a CLI tool. If viral distribution fails, the revenue target collapses to bear case ($4,350 MRR). This is still viable but not "aggressive."
>
> **What I'm signing off on**: The feature set correctly maximizes market opportunity capture. The 7-doc pipeline + cross-validation + industry templates is the strongest possible competitive position in 14 weeks.

### User Perspective

**Verdict**: ACCEPT (with concern)

> The feature set covers what power users need. The conversational engine, editable documents, and context propagation address the core user journey. The 15-minute first-run experience is ambitious but necessary.
>
> **Primary concern**: 10 features in 26 weeks means each feature gets minimal UX polish. The conversational flow (F1) determines the entire user experience — and it gets only 3 weeks. Competitors with $300M ARR spent months refining their onboarding. If the questions feel robotic or generic, users will abandon within the first minute.
>
> **What I need to see**: At least 5 iteration cycles of the conversational flow with real users during the private beta (Month 1-2). The question quality must improve weekly, not be "done" in Week 3.
>
> **What I'm signing off on**: The feature priorities are correct. F1 (conversational engine) and F7 (first-run experience) are appropriately P0/P1. I accept the timeline risk with the condition that user testing drives iterative improvement throughout all 6 months, not just in M1.

### Tech Perspective

**Verdict**: ACCEPT (with concern)

> 24.5 weeks of development in a 26-week timeline is technically feasible for a solo developer who knows the stack. The feature dependency chain is well-ordered. The tech debt decisions are pragmatic — monolithic architecture, single LLM, minimal tests — these are correct trade-offs for a product that may need to pivot at Month 4.
>
> **Primary concern**: Cross-validation (F3) and context propagation (F4) are the two highest-risk features, estimated at 4.5 weeks combined. If either takes 50% longer than estimated (which happens frequently with novel AI-driven features), the timeline breaks. There is only 1.5 weeks of buffer.
>
> **My honest estimate**: 30% chance the timeline slips by 2-3 weeks. F9 (industry templates) or F10 (dashboard) gets cut or ships at reduced scope. This is acceptable if F1-F6 ship on time.
>
> **What I refuse to compromise on**: Cross-validation correctness and template code quality. If these ship broken, the product is actively harmful — generating inconsistent documents and non-running code is worse than generating nothing.
>
> **What I'm signing off on**: The architecture choices are sound. Monolithic CLI, single LLM, BYOK, markdown-only — all correct for V1. The non-negotiable quality standards are the right ones. I accept the timeline risk with the understanding that F9 or F10 may be sacrificed.

### Business Perspective

**Verdict**: ACCEPT (with strong concern)

> The pricing model ($29/mo Pro, $59/mo Team) is defensible. BYOK eliminates marginal cost. LTV:CAC ratio of 2.5-10x is healthy. The free/paid boundary with 3-project limit is the right mechanism.
>
> **Strong concern**: The $10K MRR target at Month 6 requires 2,500 users with 4% conversion. The median indie project earns $500/mo (IndieMarkerAnalytics, 326 projects). Only 10% of indie projects break $10K/mo. We are betting we are in the top 10% — and we have no data to support this yet.
>
> **The math that worries me**: $10K MRR requires ~275 paid subscribers (200 Pro + 50 Team + enterprise). At 4% conversion from 2,500 free users. No bootstrapped CLI tool in history has reached 2,500 users in 6 months without corporate backing. The business discussion estimated that $29K MRR at $19/mo required 51,000-76,000 free users, which was called "fantasy." At $29/mo, we need fewer users but the conversion rate must be higher.
>
> **What makes me sign off anyway**: The downside is bounded. Low burn rate ($700-$1,900/mo) means even total revenue failure doesn't kill us. The kill criteria at Month 4 prevent us from burning runway on a proven failure. And if the bear case materializes ($4,350 MRR), that is STILL in the top 30% of indie projects and above the sustainable scenario's target.
>
> **What I'm signing off on**: The aggressive scenario with the explicit understanding that Month 4 is a hard Go/No-Go gate. If we are tracking toward worst case at Month 4, we switch to conservative immediately. No emotional attachment to the aggressive numbers.

---

## Appendix A: Comparison with Other Scenarios

| Dimension | Aggressive (This) | Balanced | Conservative |
|-----------|-------------------|----------|-------------|
| Features at Month 6 | 10 | 6-8 | 3-4 |
| Dev weeks used | 24.5 / 26 | 18-20 / 26 | 12-14 / 26 |
| Buffer weeks | 1.5 | 6-8 | 12-14 |
| MRR target (Month 6) | $10,750 | $3,000-$5,000 | $1,500-$3,000 |
| User target (Month 6) | 2,500 | 500-800 | 250-350 |
| Conversion rate needed | 4% | 2.5-3% | 2% |
| Tech debt | Very High | Medium | Low |
| Refactoring needed | Month 7-8 (mandatory) | Month 9-12 | Minimal |
| Risk of total failure | 25-35% | 10-15% | 5% |
| Upside if it works | Category creator, $100K+ ARR trajectory | Solid niche tool, $60K+ ARR trajectory | Sustainable indie tool, $18-45K ARR |
| Recovery if it fails | Open-source + consulting pivot | Open-source + iterate | No recovery needed (always viable) |

## Appendix B: Data Sources

All market data, competitor metrics, and benchmarks in this document are sourced from the Phase 1 research reports:
- `prompt/market-research-optimistic.md` — Optimistic market analysis with sourced data
- `prompt/market-research-cautious-report.md` — Conservative market analysis with sourced data
- `prompt/strategy-report-sustainable-growth.md` — Sustainable business strategy with benchmarks
- `prompt/discussion-business-sustainability.md` — Business sustainability discussion with conversion rate analysis

Key data citations:
- AI-generated code 1.7x more issues: CodeRabbit, Dec 2025, 470 GitHub PRs
- 45% security failure rate: Veracode 2025
- Solo founders +340% YoY: Multiple 2025-2026 reports
- Lovable 18K user breach: The Register, Feb 2026
- Median indie project $500/mo: IndieMarkerAnalytics, 326 projects
- Dev tools conversion 2-5%: Lenny's Newsletter + Monetizely
- 55% trial cancellations on Day 0: RevenueCat 2026
