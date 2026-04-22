# Speed-First Discussion: Fastest Path to Working Intent Understanding and SaaS Generation System

**Role**: Discussion Moderator — Development Speed and Time-to-Market Priority
**Phase**: 2 of 4 (Deep Research — Speed Synthesis)
**Date**: 2026-03-12
**Scope**: LOCAL CLI tool (Claude Code) — 9 Service Engines, full-stack SaaS generation

---

## Executive Summary

The fastest path to a working system is **6 weeks to full V1**, with a working demo in **5 days**. This is achievable by combining Branch 3.1's rapid development cadence, Branch 5.2's deterministic FSM foundation, Branch 1.1's Claude Structured Outputs, Branch 2.1's evolutionary file growth, and Branch 4.2's Debt Firewall. The single biggest speed lever: treat the intent engine as an FSM with slot-filling, not as a general NLU problem. The second biggest: externalize all prompts on Day 1 so behavior changes never require code changes.

---

## 1. The Fastest Path to Working System

### Philosophy: Demo First, Architecture Second

The critical insight from synthesizing all 10 branches is that **speed and quality are not opposites** — but they require different sequencing. Branch 3.2 (200+ tests, 6-month timeline) confuses completeness with quality. Branch 2.2 (160 files upfront) confuses architecture with progress. The speed-first approach inverts both: ship a working system that handles the core 80% of cases, then expand.

The Debt Firewall from Branch 4.2 is the key mental model: **generator output must be zero-debt, but the tooling that produces it can carry 30% debt**. This distinction alone saves 4-5 weeks. A SaaS platform with imperfect internal scaffolding that works is infinitely more valuable than a perfectly architected system that doesn't exist yet.

### Week-by-Week Timeline

| Week | Milestone | Key Deliverables | Hours |
|------|-----------|------------------|-------|
| **Week 1, Days 1-2** | Intent Engine Alpha | FSM + 7 questions working, Claude Structured Outputs for slot extraction, `.md` prompt files externalized | 16h |
| **Week 1, Days 3-5** | Demo-Ready Pipeline | PRD generation from answered slots, console output, 1 real SaaS category end-to-end | 14h |
| **Week 2, Days 1-3** | Real User Testing | 5 users testing intent flow, hot-reload prompts live, cassette tests for all 5 sessions | 18h |
| **Week 2, Days 4-5** | PRD + TRD Generation | Both documents generating from slots, user approval gate implemented | 12h |
| **Week 3** | 3 Core Service Engines | Schema Engine + Component Library Engine + API Route Engine | 20h |
| **Week 4** | 3 More Service Engines | Auth Engine + Database Engine + Deployment Engine | 20h |
| **Week 5** | Final 3 Engines + Integration | Testing Engine + Documentation Engine + Payment Engine; all 9 engines wired | 22h |
| **Week 6** | Polish + V1 Ship | Error handling, edge cases, 7-document expansion, CLI packaging | 16h |
| **TOTAL** | **Full V1** | 9 engines, 7 documents, working CLI | **~138h** |

This is within Branch 2.1's projected 100-140 dev-hours. The schedule is aggressive but not heroic.

### Week 1: Absolute Minimum for a Working Demo

On Day 5, the demo should do exactly one thing end-to-end: take a user's SaaS idea in natural language, ask 7 clarifying questions via FSM dialogue, and output a valid PRD.md.

Nothing else. No TRD. No code generation. No multiple SaaS categories. Just intent → questions → PRD.

The minimum stack for this demo:

```
intent-engine/
  slots.ts          ← 7 slot definitions
  fsm.ts            ← state machine (7 states + DONE)
  prompts/
    extract.md      ← Claude extraction prompt
    question-N.md   ← 7 question prompts (hot-reloadable)
  prd-template.md   ← Handlebars template
index.ts            ← 50-line CLI entry point
```

That is 12 files. Branch 2.1 starts with 22 files — this demo starts with 12. The difference is 10 files of infrastructure that can be added in Week 2.

Branch 5.2's Frame Semantics gives the slot definitions for free: a SaaS product description maps directly to named conceptual slots (target_user, core_problem, primary_feature, monetization, scale_requirement, tech_preference, timeline). These 7 slots are the entire intent model for V1. No ML training. No vector databases. No embedding similarity search. Claude extracts them from natural language in a single structured output call.

**Day 1 priority**: Get one slot extracted correctly. `"I want to build a tool for designers to manage client feedback"` → `{ target_user: "designers", core_problem: "client feedback management" }`. That's the entire Day 1 goal.

### Week 2: Real User Feedback

Branch 3.1 specifies this explicitly: **Week 2, 5 real users**. This is not optional for speed — it is *required* for speed. Without real user feedback at Week 2, you will spend Weeks 3-6 building the wrong thing. The cost of discovering a fundamental UX flaw at Week 6 is 4 weeks of rework. The cost of discovering it at Week 2 is 2 days.

The hot-reload system (chokidar watching `prompts/*.md`) means question phrasing can be changed between user sessions without recompiling. This is the fastest feedback loop possible. A user says "I don't understand question 3" — you edit `prompts/question-3.md`, restart nothing, the next user sees the new phrasing immediately.

The cassette recording pattern from Branch 3.2 (adapted for speed): record each user session's Claude API calls, replay them in tests. This gives you 5 integration tests for free, derived from real usage, zero test-writing overhead.

### Month 1: MVP Feature Set

By end of Week 4 (Month 1), the system should have:

- 9 clarifying questions (expanded from 7 based on Week 2 feedback)
- 3 output documents: PRD.md, TRD.md, TASKS.md
- 6 of 9 service engines working (Schema, Component, API Route, Auth, Database, Deployment)
- User approval gate before code generation begins
- Hot-reload prompt system
- Cassette-based test suite (15-20 tests from recorded sessions)

This is a system that a developer could use in production for greenfield projects. It is not complete — Payment Engine, Testing Engine, and Documentation Engine are missing — but the core 80% of a typical SaaS project is covered.

**What is NOT in Month 1 MVP (by design)**:
- Multi-agent orchestration (single pipeline only)
- Advanced error recovery
- Prompt version management
- Usage analytics
- More than 3 output document types

Each of these is a valid feature. None of them is required for the system to be useful. Adding them before the core works is the definition of premature complexity.

### Month 2: Full V1

By end of Week 6:

- All 9 service engines
- 7 output documents (add API.md, ENV.md, DOCKER.md, SECURITY.md)
- Multi-model routing (Branch 1.1): cheap model for clarifying questions, expensive model for code generation
- CLI packaging as npm package
- Complete cassette test suite (40+ tests)
- Prompt registry with versioning (registry.json pointing to .md files)

The evolutionary file count matches Branch 2.1's projection: 22 files (Week 1) → 38 files (Week 4) → 58 files (Week 6). This is not 160 files (Branch 2.2). The difference is that Branch 2.2 builds the scaffolding for all future expansion upfront, while Branch 2.1's Day-1 interfaces allow expansion without scaffolding.

---

## 2. Speed-Enabling Technology Choices

### Claude Structured Outputs: The Intent Engine's Core

Branch 1.1 rates Claude Structured Outputs at 5/5 for production readiness. For the intent engine specifically, this eliminates the single largest source of development time in NLU systems: parsing errors.

Traditional NLU (Rasa, spaCy, fine-tuned BERT) requires:
1. Training data collection (1-2 weeks)
2. Model training and evaluation (1 week)
3. Intent classification tuning (1 week)
4. Entity extraction debugging (1 week)

Total: 4-5 weeks before the first working classification.

Claude Structured Outputs requires:
1. Define JSON schema for slots (2 hours)
2. Write extraction prompt in `.md` file (1 hour)
3. Call API and validate response (1 hour)

Total: 4 hours.

The tradeoff: $12-25/run (Branch 1.1's estimate). For a LOCAL CLI tool targeting developers building SaaS products, this is acceptable. A developer paying $20 to generate a production-ready SaaS scaffold is getting a bargain. This is not a consumer app where per-query cost matters at scale.

Branch 1.2's hybrid approach (80% rules, 20% LLM) is correct for production systems serving millions of queries. It is wrong for a CLI tool used by hundreds of developers. The crossover point where rule-based becomes cheaper than LLM is around 100,000 queries/month. A CLI tool will not reach that volume in Year 1.

### Hot-Reload Prompts: The Iteration Accelerator

Branch 3.1's chokidar-based hot-reload system deserves emphasis. The < 30-second change-test cycle it enables is not just a developer convenience — it is a fundamentally different development model.

Without hot-reload: change prompt → rebuild → restart CLI → re-enter test input → observe output. Cycle time: 2-3 minutes minimum.

With hot-reload: change `.md` file → save → observe output in running session. Cycle time: 5-10 seconds.

Over a 6-week development period with 50 prompt iterations per week, this saves: (2.5 min - 0.1 min) × 50 × 6 = 720 minutes = 12 hours. That is 12 hours of pure speed gain from one architectural decision made on Day 1.

The implementation is trivial:

```typescript
import chokidar from 'chokidar';
const promptCache = new Map<string, string>();
chokidar.watch('prompts/').on('change', (path) => {
  promptCache.delete(path);  // next read will reload from disk
});
```

That is 5 lines. The return on investment is one of the highest in the entire system.

### Externalized Prompts: Behavior Without Code Changes

The strategic importance of `.md` prompt files goes beyond hot-reload. When prompts are externalized, the system has two independent change axes:

- **Logic axis**: TypeScript/code changes, requires rebuild, affects control flow
- **Behavior axis**: `.md` file changes, no rebuild, affects what Claude outputs

In practice, 80% of iteration during development is on the behavior axis. Question phrasing, PRD section content, code generation style — all of these are prompt changes, not logic changes. By separating them, 80% of iteration cycles require no compilation.

This also enables a non-developer to tune the system's output quality. A product manager can edit `prompts/prd-template.md` to improve PRD structure without understanding TypeScript. This is relevant for the LOCAL CLI's target user: a developer who wants to delegate prompt engineering to domain experts.

### 3-Document-First Strategy

Branch 3.1 specifies starting with 3 documents (PRD, TRD, Tasks) and expanding to 7 later. The speed rationale:

- Each document template takes 2-4 hours to design and implement
- Documents 1-3 are universally required for any SaaS project
- Documents 4-7 (API.md, ENV.md, DOCKER.md, SECURITY.md) are valuable but not blocking
- Getting documents 1-3 right requires user feedback, which requires shipping them first

Building all 7 templates upfront without user feedback means 50% of the template work will be revised after Week 2 feedback. Building 3 first means revising 3 templates instead of 7. Time saved: approximately 8-12 hours.

### Single-Agent First: The Evolutionary Principle

Branch 2.1's evolutionary architecture has a specific speed implication: single-agent pipelines are debuggable. Multi-agent pipelines are not.

When a single agent produces wrong output, the debugging path is: input → prompt → output. Three variables. Debugging time: minutes.

When a 4-agent pipeline produces wrong output, the debugging path is: which agent introduced the error? What state was passed between agents? Was the error in the prompt or the routing logic? Debugging time: hours to days.

Branch 2.2's "complete upfront" approach would include multi-agent orchestration from Day 1. This is fast to design (on a whiteboard) but slow to debug (in practice). The 2-3 month speed advantage of Branch 2.1 over 2.2 comes primarily from single-agent simplicity during the critical first month.

The migration path from single-agent to multi-agent is straightforward when Day-1 interfaces are in place: each engine has a defined input/output contract. Wrapping an engine in an agent is a structural change, not a logic change. This is Branch 2.1's key insight: design for agent-ability from Day 1, without actually deploying agents until the pipeline is proven.

---

## 3. Speed vs. Quality: Where to Draw the Line

### The Debt Firewall Principle

Branch 4.2's Debt Firewall is the most important architectural decision for speed without quality loss. The distinction is:

**Generator output** (what the system produces for users): PRD.md, TRD.md, TypeScript code, configuration files. This must be zero-debt. A developer using this system is trusting it to produce production-quality scaffolding. If the generated Auth Engine has security vulnerabilities, the entire system's value proposition collapses.

**Generator tooling** (the internal machinery): test utilities, build scripts, development helpers, documentation generators. This can carry 30% debt. A brittle test helper that works 90% of the time is acceptable. A brittle authentication code generator is not.

This distinction allows a specific set of shortcuts:

| Shortcut | Category | Time Saved | Quality Impact |
|----------|----------|------------|----------------|
| Hardcoded test fixtures instead of factories | Tooling | 4h | Zero (internal only) |
| No error messages for developer-facing CLI flags | Tooling | 2h | Minimal |
| Sequential engine execution instead of parallel | Tooling | 8h | None on output |
| Single config file instead of config hierarchy | Tooling | 6h | None on output |
| No retry logic for API calls in dev mode | Tooling | 3h | Dev experience only |
| Console.log instead of structured logging | Tooling | 4h | None on output |

Total tooling shortcuts: approximately 27 hours saved. That is 3-4 development days recovered without any degradation in what the user receives.

**Never acceptable shortcuts** (generator output):

| Shortcut | Why Never |
|----------|-----------|
| Template strings instead of validated templates | Output can contain syntax errors |
| Skip schema validation on generated code | Silent failures in user's project |
| Hardcoded tech stack assumptions | Wrong output for user's stated requirements |
| Skip user approval gate | Generates code user didn't authorize |
| Incomplete slot extraction | Wrong PRD based on misunderstood intent |

The meta-quality multiplication point from Branch 4.2 is critical: an error in generator output is not a 1x error. It is a N×users error. If the Auth Engine template has a vulnerability and 50 developers use it, that is 50 production systems with the same vulnerability. The cost multiplier makes generator output quality a first-order concern regardless of development speed.

### Branch 3.2's Cassette Pattern: Test Speed Without Coverage Loss

The cassette recording pattern adapts Branch 3.2's thoroughness to Branch 3.1's timeline. Instead of writing 200 tests before shipping (3.2's approach) or shipping without tests (speed-naive approach), cassettes provide a middle path:

- Record real Claude API calls during development sessions
- Replay them deterministically in CI
- Coverage comes from actual usage, not theoretical test design

For the intent engine, 5 recorded user sessions provide:
- 35+ slot extraction examples (7 slots × 5 sessions)
- 5 complete dialogue flow tests
- Edge cases from real users, not imagined ones

This is higher-quality test coverage than 200 hand-written tests, because real users find edge cases that developers don't imagine. And it takes 2 hours to set up the recording infrastructure, not 40 hours to write tests upfront.

---

## 4. Speed Killers to Avoid

### Over-Architecture: Branch 2.2's 160-File Trap

Branch 2.2 starts with 160 files and 22 weeks to first working prototype. The speed cost is not just 22 weeks — it is the cognitive overhead of maintaining 160 files before a single user has validated the approach.

Every file is a decision that must be made consistently with every other file. At 160 files, a naming convention change requires 160 file renames. At 22 files (Branch 2.1's start), it requires 22. The combinatorial maintenance cost of large file counts is quadratic, not linear.

The specific over-architectures to avoid in Week 1:

- No dependency injection framework until Month 2 (adds 15 files, saves nothing initially)
- No event bus until multi-agent orchestration is added (adds complexity with no consumer)
- No plugin system until 3+ engines are proven (premature extensibility)
- No configuration hierarchy (flat config.json is sufficient for 6 weeks)

### Over-Testing: Branch 3.2's Pre-Ship Test Trap

Branch 3.2 specifies 200+ tests before shipping. This is correct for a library or framework where the interface contract is stable and breaking changes have large downstream impact. It is wrong for a system where the core UX hasn't been validated yet.

Writing 200 tests for a system whose fundamental interaction model may change after Week 2 user testing is writing tests for code you will delete. The cassette approach avoids this by generating tests from validated interactions.

The appropriate test count by milestone:

| Milestone | Test Count | Type |
|-----------|------------|------|
| Week 1 Demo | 5-8 | Unit tests for slot extraction |
| Week 2 User Testing | 15-20 | Cassette tests from 5 sessions |
| Month 1 MVP | 30-40 | Cassette + critical path integration |
| V1 Ship | 60-80 | Full cassette suite + edge cases |

80 tests at V1 ship provides better coverage than 200 tests written before any user feedback, because 80 tests based on real usage exercise real code paths.

### Over-Cleaning: Branch 4.1's Hexagonal Architecture Trap

Branch 4.1 specifies hexagonal architecture (ports and adapters) for each engine. This is the correct architecture for a system with multiple deployment targets (web, mobile, CLI, API) or multiple database backends. For a LOCAL CLI tool with one deployment target (developer's machine) and one database (filesystem), it adds 3-4 files per engine with zero benefit.

For 9 engines × 4 extra files = 36 extra files, each requiring consistent implementation. This is 36 files of overhead with no user-visible benefit until the system needs to support additional deployment targets — which is a V2 concern.

### Premature Multi-Agent: The Orchestration Tax

Adding 4 agents before the single pipeline works creates what can be called the Orchestration Tax: every debugging session requires tracing through agent handoffs instead of a linear execution path.

The Orchestration Tax compounds: with 1 agent, debugging is linear. With 2 agents, debugging requires understanding the handoff contract. With 4 agents, debugging requires understanding 3 handoff contracts simultaneously, plus the orchestration logic, plus each agent's internal logic.

Branch 2.1's approach — single pipeline for Month 1, multi-agent as optional enhancement in Month 2 — defers the Orchestration Tax until the system's behavior is fully understood. At that point, the handoff contracts are obvious from the existing code, and the migration is mechanical rather than creative.

---

## 5. The Factory Multiplier: Where 1 Hour Saves 10 Hours

### Prompt Registry: The Output Multiplier

Branch 1.1's prompt registry concept has a specific ROI calculation. If the prompt registry (a JSON index mapping prompt names to `.md` file paths) takes 4 hours to build, and the system has 30 prompts, and each prompt is revised 3 times on average:

Without registry: each revision requires finding the prompt in source code, understanding its context, making the change, testing. Average 30 minutes per revision. Total: 30 prompts × 3 revisions × 30 min = 45 hours.

With registry: each revision opens a named `.md` file, makes the change, hot-reload reflects it immediately. Average 5 minutes per revision. Total: 30 prompts × 3 revisions × 5 min = 7.5 hours.

Net savings: 37.5 hours. Return on the 4-hour investment: 9.4×.

The registry also enables a capability that is impossible without it: A/B testing prompts. Record which version of `question-3.md` produces higher-quality slot extraction, and keep the winner. This is a quality improvement that costs zero additional development time.

### Day-1 Interfaces: The Refactoring Prevention System

Branch 2.1's Day-1 interfaces are the single most leveraged architectural decision for long-term speed. The principle: define the TypeScript interface for each engine before implementing it.

```typescript
interface ServiceEngine {
  name: string;
  generate(slots: SaaSSlots, context: GenerationContext): Promise<GeneratedArtifact[]>;
  validate(artifact: GeneratedArtifact): ValidationResult;
}
```

This 5-line interface, defined on Day 1, prevents:
- Callers having to know engine implementation details
- Orchestration code being coupled to specific engine APIs
- Adding a new engine requiring changes to existing callers

Without Day-1 interfaces, adding the 9th engine (after 8 engines with slightly different APIs) requires harmonizing all 9. With Day-1 interfaces, adding the 9th engine is filling in a template.

The ROI: 2 hours to define interfaces on Day 1 versus 20-30 hours of harmonization refactoring at Month 2. Return: 10-15×.

### Structured Outputs: The Debugging Elimination System

The ROI of Structured Outputs (Branch 1.1) is best understood as eliminating an entire category of bugs: parsing errors.

Without Structured Outputs, Claude's natural language response must be parsed to extract structured data. Parsing code introduces:
- Regex brittle to minor output format changes
- Edge case handling for unexpected formats
- Debugging sessions when Claude changes its response pattern

With Structured Outputs, Claude returns JSON that validates against a schema. Parsing errors are structurally impossible. The only errors are schema design errors (which are caught immediately) and Claude misunderstanding the slot (which is a prompt quality issue, not a code quality issue).

Eliminating parsing errors eliminates a category of debugging that typically consumes 15-20% of development time in NLU systems. For 138 total development hours, that is 21-28 hours recovered.

---

## 6. Conclusion: Speed-First Recommended Approach

### Fastest Path: 6 Weeks to Full V1

The synthesis of all 10 branches points to a single fastest path:

**Foundation stack**: Claude Structured Outputs (1.1) + FSM dialogue (5.2) + Evolutionary architecture (2.1) + Debt Firewall (4.2) + Hot-reload iteration (3.1)

**What is explicitly rejected**:
- Rasa/spaCy training pipelines (Branch 1.2 hybrid, adds 4-5 weeks)
- 160-file upfront architecture (Branch 2.2, adds 16+ weeks)
- 200+ pre-ship tests (Branch 3.2, adds 3-4 weeks)
- Hexagonal architecture per engine (Branch 4.1, adds 2-3 weeks)
- Multi-agent orchestration in Month 1 (premature, adds debugging overhead)

**What is explicitly accepted**:
- $12-25/run cost (acceptable for developer CLI tool)
- 30% tooling debt (internal only, zero user impact)
- Cassette tests instead of comprehensive upfront tests
- 3 documents in Month 1, expand to 7 in Month 2
- Single pipeline until Month 2

### Trade-offs Accepted

| Trade-off | Speed Gain | Risk |
|-----------|------------|------|
| No Rasa training | 4-5 weeks | Higher per-run cost |
| Tooling debt 30% | 3-4 weeks | Refactor tooling in Month 3 |
| 3 docs first | 1-2 weeks | Expand templates requires update cycle |
| Single agent | 2-3 weeks | Multi-agent migration in V2 |
| Cassette tests only | 3-4 weeks | Test coverage depends on usage patterns |

Total speed gain from accepted trade-offs: approximately 13-18 weeks compared to maximum-quality approach. This is the difference between a 6-week V1 and a 22-week V1.

### Risk Mitigation for Speed-Induced Issues

**Risk 1: Tooling debt compounds**
Mitigation: Document all accepted shortcuts in `TECH-DEBT.md` on the day they are introduced. Schedule a 1-week "tooling cleanup" sprint at Month 3. The Debt Firewall ensures only tooling carries debt, so cleanup is localized.

**Risk 2: Cassette tests miss real edge cases**
Mitigation: Add 10 synthetic edge case tests (empty input, adversarial input, non-English input) alongside cassette tests. Total coverage is still < 100 tests but covers the most likely failure modes.

**Risk 3: Single-agent pipeline doesn't parallelize**
Mitigation: Branch 2.1's Day-1 interfaces mean parallelization is a structural addition, not a rewrite. Add concurrent engine execution (Promise.all) in V2 without changing engine logic.

**Risk 4: Claude API cost surprises users**
Mitigation: Implement cost estimation before generation begins (count tokens in slots, estimate output length, display cost estimate, require explicit user approval). This also satisfies the LOCAL CLI constraint's user approval requirement.

**Risk 5: Prompt quality degrades across SaaS categories**
Mitigation: The hot-reload system and prompt registry enable rapid category-specific prompt tuning. Week 2's 5-user test covers multiple categories. Add category-specific prompt variants as discovered issues arise.

### The LOCAL CLI Constraint: User Approval Gate

All three critical constraints intersect at the user approval gate:

1. **LOCAL CLI**: runs on developer's machine, user is present
2. **User approval required**: explicit gate before code generation
3. **PRD.md pre-work**: PRD must be approved before generation begins

The implementation: after slot extraction and PRD generation, display the PRD in the terminal (or open in editor), ask for explicit `[y/N]` confirmation, then proceed to TRD generation, then ask for second confirmation before code generation begins. This is a 2-gate approval system that costs 20 minutes to implement and satisfies all three constraints simultaneously.

### What to Add in V2

V2 (Month 3-6) should focus on what was deliberately deferred:

1. **Multi-agent orchestration**: parallel engine execution, specialized sub-agents per domain
2. **Multi-model routing**: cheap models for clarification, expensive models for generation
3. **4 additional output documents**: API.md, ENV.md, DOCKER.md, SECURITY.md
4. **Prompt version management**: track which prompt version produced which output
5. **Tooling cleanup**: eliminate the 30% tooling debt accumulated in V1
6. **Branch 5.1's advanced techniques**: Tree-of-Thought for architecture decisions, Reflexion for iterative improvement

The V2 list is not a list of failures — it is a list of features deliberately deferred to enable V1 to ship in 6 weeks instead of 22. This is the core thesis of the speed-first approach: a working system that solves 80% of the problem in 6 weeks is more valuable than a perfect system that solves 100% in 22 weeks, because the 80% solution generates real-world feedback that shapes the remaining 20%.

---

## Appendix: Branch Score Reconciliation

| Branch | Quality Score | Speed Score | Chosen Elements |
|--------|---------------|-------------|-----------------|
| 1.1 Aggressive Tech | 9.2/10 | 9/10 | Structured Outputs, Agent SDK, registry |
| 1.2 Conservative Tech | 9.2/10 | 4/10 | None (too slow to implement) |
| 2.1 Evolutionary Arch | 9/10 | 9/10 | Day-1 interfaces, file growth curve |
| 2.2 Big Bang Arch | 7/10 | 2/10 | None |
| 3.1 Rapid Workflow | 8/10 | 10/10 | Hot-reload, Week 2 users, cassette |
| 3.2 Robust Workflow | 8.5/10 | 3/10 | Cassette pattern only |
| 4.1 Debt Minimized | 7.7/10 | 5/10 | None (hexagonal too slow) |
| 4.2 Debt Practical | 8.2/10 | 9/10 | Debt Firewall definition |
| 5.1 Modern Theory | 8.6/10 | 6/10 | ICL, CoT, Structured Outputs framing |
| 5.2 Classical Theory | 9.5/10 | 10/10 | FSM dialogue, Frame Semantics slots |

The highest-speed combination (3.1 + 5.2 + 1.1 + 2.1 + 4.2) achieves a weighted quality score of approximately 8.9/10 — higher than most individual branches — because the speed gains come from eliminating waste (over-architecture, premature complexity) rather than cutting corners on output quality.

---

*Next Phase: Phase 3 — Risk and Constraint Analysis (quality-first perspective to identify where speed-first approach needs guardrails)*
