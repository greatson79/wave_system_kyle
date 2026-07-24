# SaaS Auto-Builder: CUTTING EDGE Technology Scenario

**Scenario**: CUTTING EDGE (Maximum Innovation)
**Philosophy**: "The best technology makes us strongest."
**Risk Profile**: HIGH — offset by highest ceiling on quality and competitive differentiation
**Date**: 2026-03-12
**Context**: Solo founder, 6-month (26-week) timeline, 8 features, local CLI tool on Claude Code

---

## Executive Summary

This scenario maximizes innovation by adopting technologies released or significantly updated within the last 1-2 years (2024-2026) at every layer of the stack. The thesis: a solo founder building an AI-native product should use AI-native tooling. Every technology in this scenario has crossed the "production-proven" threshold — not experimental, but aggressively modern. The combined stack delivers 90%+ cost savings on LLM operations, 56x faster linting, 356x faster HMR, and 100% schema-guaranteed document generation.

The trade-off is real: higher learning curve, thinner community resources for edge cases, and more frequent breaking changes. This scenario is for a founder who views learning new tools as investment rather than overhead, and who believes that technical excellence in the generator directly translates to excellence in the generated output.

**Core bet**: The convergence of Claude Structured Outputs (100% schema compliance), Prompt Caching (90% cost reduction), Agent SDK (production-grade orchestration), and Rust-powered build tooling (Turbopack + Biome) creates a window where a solo founder can build a system that was simply impossible 18 months ago.

---

## 1. Complete Technology Stack

### 1.1 Technology Stack Table

| Layer | Technology | Version/Spec | Released/Updated | Why This Over Alternatives |
|-------|-----------|-------------|-----------------|---------------------------|
| **Runtime** | Node.js | 22 LTS | Oct 2024 | Native ESM, `--experimental-strip-types`, performance baseline |
| **Language** | TypeScript | 5.x (strict: true, all sub-flags) | 2024-2025 | Single language across CLI + pipeline + generated code |
| **LLM (Primary)** | Claude Sonnet 4.6 | 200K context, $3/$15 per M tokens | 2026 | SWE-bench 77.2%, cost-optimal for code generation |
| **LLM (Validation)** | Claude Opus 4.6 | 200K context, effort parameter | 2026 | 15% higher on Terminal-Bench, used for cross-validation only |
| **LLM Feature** | Structured Outputs | GA late 2025 | 2025 | 100% schema compliance — zero JSON parse errors |
| **LLM Feature** | Prompt Caching | Auto, 5-min TTL | 2025 | 90% cost savings, 85% latency reduction on cached prompts |
| **LLM Feature** | Batch API | 50% discount, async | 2025 | Combined with caching: 95%+ total cost reduction |
| **Orchestration** | Claude Agent SDK | TypeScript, pre-1.0 | Sep 2025 | Subagent isolation, MCP integration, powers Claude Code itself |
| **Protocol** | MCP (Model Context Protocol) | 97M+ monthly SDK downloads | 2025 | Universal standard (Anthropic + OpenAI + Google + Microsoft) |
| **Schema** | Zod + zodToJsonSchema | Zod 3.x | 2024-2025 | Triple duty: TypeScript types + runtime validation + LLM schema |
| **CLI Framework** | Commander.js (V1) / Ink (V2) | Commander 12.x | Stable | 180KB, 0 deps, near-invisible overhead |
| **CLI Prompts** | Inquirer.js (V1) / Ink @inkjs/ui (V2) | Inquirer 9.x | 2024 | Proven for conversational CLI flows |
| **Bundler** | tsup (library) + tsx (dev) | tsup 8.x | 2024 | esbuild-powered, zero-config TypeScript compilation |
| **Package Manager** | pnpm | 9.x | 2024 | 2x faster than npm, strict node_modules, workspace support |
| **Linter/Formatter** | Biome (primary) + ESLint (boundary) | Biome 2.x | Mar 2025 | 56x faster than ESLint, 423+ rules, single binary |
| **Test** | Vitest | 2.x | 2024-2025 | Native ESM, TypeScript-first, Vite-powered, same ecosystem |
| **Test (LLM)** | Golden-file mocking + LLM-as-judge | Custom | — | Deterministic daily tests, non-deterministic weekly validation |
| **CI/CD** | GitHub Actions + semantic-release | — | Stable | npm OIDC publishing, automated changelogs |
| **State** | File-based JSON/YAML on disk | — | — | Zero infrastructure, user owns all data |
| **Distribution** | npm registry | — | — | Universal Node.js distribution |
| **Generated: Framework** | Next.js 15+ (App Router + Turbopack) | 15.x / 16.x | Oct 2025 | RSC, Server Actions, 700x faster HMR |
| **Generated: UI** | shadcn/ui + Tailwind CSS v4 + Framer Motion | shadcn Jan 2026 | Jan 2026 | 65K+ stars, copy-paste, <10KB production CSS |
| **Generated: State** | Zustand | 5.x | 2024 | 1KB, TypeScript-native, no boilerplate |
| **Generated: ORM** | Drizzle ORM | 0.3x+ | 2024-2025 | 7KB bundle, SQL-native, zero binary deps |
| **Generated: Auth** | Supabase Auth + SSR | Latest | 2025-2026 | Row-Level Security, SSR support, zero vendor lock-in |
| **Generated: Payments** | Stripe via Supabase Stripe Sync Engine | Jan 2026 | Jan 2026 | One-click sync replaces weeks of webhook code |
| **Generated: Backend** | Supabase (Postgres + Edge Functions + Realtime) | Latest | 2025-2026 | Full backend-as-a-service, SQL queryable |

### 1.2 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER (Terminal)                           │
│  $ saas-builder create "My marketplace idea"                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                      CLI Layer (V1)                               │
│  Commander.js + Inquirer.js                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐     │
│  │ Onboarding  │  │   Commands   │  │  Editor Integration │     │
│  │ (F7: 15min) │  │ create|edit  │  │  (F5: edit docs)   │     │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘     │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
┌─────────▼────────────────▼─────────────────────▼────────────────┐
│                      CORE ENGINE                                 │
│                                                                  │
│  ┌───────────────────┐    ┌──────────────────────────────┐      │
│  │  Conversation     │    │  Document Pipeline (F2)       │      │
│  │  Engine (F1)      │    │                               │      │
│  │  5-7 Smart Q&A    │───▶│  PRD ──▶ User Journey ──▶ TRD│      │
│  │  + Smart Defaults │    │   │         │            │    │      │
│  └───────────────────┘    │   ▼         ▼            ▼    │      │
│                           │  Code    UI Guide    IA  ──▶ │      │
│  ┌───────────────────┐    │  Guidelines            Tasks  │      │
│  │  Context          │    │                               │      │
│  │  Propagation (F4) │◀──▶│  Zod Schema → JSON Schema    │      │
│  │  (SOT chain)      │    │  → Claude Structured Outputs  │      │
│  └───────────────────┘    └──────────────────────────────┘      │
│                                                                  │
│  ┌───────────────────┐    ┌──────────────────────────────┐      │
│  │  Cross-Validation │    │  Licensing / Tier Manager     │      │
│  │  Engine (F8)      │    │  (F6: Free/Paid boundary)    │      │
│  │  Sonnet→generate  │    │  3 projects free             │      │
│  │  Opus→validate    │    │                               │      │
│  └───────────────────┘    └──────────────────────────────┘      │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                      LLM ADAPTER LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  interface LLMAdapter {                                  │    │
│  │    generateStructured<T>(schema: ZodSchema<T>): T       │    │
│  │    generateText(prompt: string): string                  │    │
│  │    batch(requests: LLMRequest[]): LLMResponse[]         │    │
│  │  }                                                       │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  ClaudeAdapter (V1) ──── implements LLMAdapter           │    │
│  │  + Structured Outputs (100% schema compliance)           │    │
│  │  + Prompt Caching (automatic, 5-min TTL)                 │    │
│  │  + Batch API (async, 50% discount)                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                AGENT ORCHESTRATION LAYER                          │
│  Claude Agent SDK (selective use — orchestration shell)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │PRD Agent │ │TRD Agent │ │UI Agent  │ │Task Agent│  ...       │
│  │(subagent)│ │(subagent)│ │(subagent)│ │(subagent)│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│  Each subagent: own context window, restricted tools, isolated   │
│  MCP: file system access, template registry queries              │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│              TEMPLATE LAYER (Generated Output)                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  TemplateRegistry {                                      │    │
│  │    register(template: SaaSTemplate): void                │    │
│  │    get(id: string): SaaSTemplate                         │    │
│  │    scaffold(template, documents): ProjectFiles           │    │
│  │  }                                                       │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  V1: nextjs-supabase-stripe (F3)                         │    │
│  │  Next.js 15+ | Supabase | Stripe | shadcn/ui | Drizzle  │    │
│  │  + Tailwind v4 | Zustand | Framer Motion                │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

Dependency Direction: CLI → Core → Generators → Shared
                       ↓
                   LLM Adapter (shared, no upward deps)
```

### 1.3 Key Interface Contracts

```typescript
// LLMAdapter — the single most important abstraction for V2 multi-LLM
interface LLMAdapter {
  generateStructured<T extends z.ZodType>(
    schema: T,
    prompt: string,
    options?: { cache?: boolean; effort?: 'low' | 'medium' | 'high' }
  ): Promise<z.infer<T>>;

  generateText(prompt: string, options?: { cache?: boolean }): Promise<string>;

  batch<T extends z.ZodType>(
    requests: Array<{ schema: T; prompt: string }>
  ): Promise<Array<z.infer<T>>>;
}

// TemplateRegistry — the extension point for V2 marketplace
interface TemplateRegistry {
  register(template: SaaSTemplate): void;
  list(): SaaSTemplate[];
  get(id: string): SaaSTemplate;
  scaffold(templateId: string, documents: DocumentSet): Promise<ProjectFiles>;
}

// DocumentPipeline — the core value chain
interface DocumentPipeline {
  generate(stage: DocumentStage, context: PipelineContext): Promise<Document>;
  validate(document: Document, schema: z.ZodType): ValidationResult;
  propagate(source: Document, targets: DocumentStage[]): Promise<Document[]>;
}
```

---

## 2. Development Environment and Process

### 2.1 Setup and Developer Experience

| Aspect | Specification | Time |
|--------|--------------|------|
| **Initial setup** | `pnpm install` → ready to develop | < 2 minutes |
| **Dev server** | `tsx watch src/index.ts` — instant TypeScript execution | < 1 second |
| **Lint + format** | `biome check .` — single command, single config | < 1 second (10K files in 0.8s) |
| **Test** | `vitest` — watch mode with instant feedback | < 3 seconds for full suite |
| **Build** | `tsup src/index.ts --format esm,cjs` — dual-format output | < 5 seconds |
| **CI pipeline** | Push → lint → test → build → semantic-release → npm publish | < 3 minutes |

**Dev cycle**: Edit → save → tsx auto-restarts → test in ~2 seconds. No compilation step, no build step during development. The feedback loop is sub-second.

### 2.2 Testing Strategy

| Test Type | Tool | Coverage Target | Frequency | Purpose |
|-----------|------|----------------|-----------|---------|
| **Unit tests** | Vitest | 80%+ on core/ and generators/ | Every commit | Logic correctness, schema validation |
| **Golden-file tests** | Vitest + snapshots | All 7 document types | Every commit | Detect unintended output regressions |
| **Integration tests** | Vitest | CLI → pipeline → output | Every PR | End-to-end flow verification |
| **LLM-as-judge** | Custom + Opus 4.6 | All document types | Weekly (Batch API) | Quality assessment of generated documents |
| **Template tests** | Vitest + `next build` | Template compiles + passes lint | Every PR | Generated code is valid |
| **Security audit** | `npm audit` + Biome security rules | Zero high/critical | Every release | Supply chain + generated code safety |

**Golden-file strategy**: Record known-good LLM outputs as `.golden` files. Unit tests compare against these snapshots. This provides deterministic, fast tests for a non-deterministic system. Golden files are regenerated monthly or after model updates.

**LLM-as-judge strategy**: Weekly Batch API job sends generated documents to Opus 4.6 with evaluation rubrics (completeness, consistency, actionability). Results logged to `quality-reports/`. This catches gradual quality drift that golden files miss.

### 2.3 Quality Gates

| Gate | Trigger | Blocks | Tool |
|------|---------|--------|------|
| **G1: Type check** | Pre-commit | Merge | `tsc --noEmit` |
| **G2: Lint + format** | Pre-commit | Merge | `biome check` |
| **G3: Unit + golden** | CI | Merge | `vitest run` |
| **G4: Integration** | CI | Release | `vitest run --project integration` |
| **G5: Template build** | CI | Release | `cd template && next build` |
| **G6: Security audit** | CI | Release | `npm audit --audit-level=high` |
| **G7: LLM quality** | Weekly cron | Advisory (not blocking) | Custom Batch API evaluator |

---

## 3. Realistic Assessment

### 3.1 Development Difficulty: HIGH

**Justification**:
- Simultaneous learning of Agent SDK (pre-1.0, limited docs), Structured Outputs (new API surface), and Prompt Caching (cache key management) in the LLM layer
- Designing 7 Zod schemas that are strict enough for validation but flexible enough for LLM generation
- Building cross-document context propagation that maintains SOT consistency
- Template engineering: generating code that compiles, lints, and follows generated guidelines
- All of this on a solo-founder timeline of 26 weeks

**Mitigating factors**:
- The existing AgenticWorkflow codebase provides 7-11 weeks of head start (hooks, context system, quality gates)
- TypeScript everywhere means one language to master, not four
- Commander.js + Inquirer.js (V1) defers the Ink learning curve to V2
- The Agent SDK is optional — can be replaced by direct Claude API calls if it creates friction

### 3.2 Learning Curve

| Technology | Weeks to Productivity | Prior Knowledge Required |
|-----------|----------------------|------------------------|
| Claude API + Structured Outputs | 1 week | Basic LLM API usage |
| Prompt Caching + Batch API | 0.5 weeks | Claude API basics |
| Agent SDK (selective) | 2 weeks | Claude API + MCP concepts |
| Zod + zodToJsonSchema | 1 week | TypeScript generics |
| Biome | 0.5 weeks | Any linter/formatter experience |
| Vitest | 0.5 weeks | Any test framework (Jest, Mocha) |
| Next.js 15 App Router | 2 weeks | React + Next.js Pages Router |
| Drizzle ORM | 1 week | SQL + any TypeScript ORM |
| Supabase (Auth + Edge) | 1 week | Any BaaS or Firebase experience |
| Supabase Stripe Sync | 0.5 weeks | Basic Stripe knowledge |
| **Total sequential** | **~10.5 weeks** | |
| **Realistic (parallel learning)** | **~5-6 weeks** | Technologies learned during feature implementation |

### 3.3 Expected Bugs

| Bug Category | Likelihood | Severity | Root Cause |
|-------------|-----------|----------|-----------|
| Schema mismatch (LLM output vs Zod) | Medium | Medium | Edge cases where Structured Outputs hits schema ambiguity |
| Prompt cache misses | High | Low | Cache key instability from dynamic system prompts |
| Cross-document reference broken | High | High | Entity renaming in upstream doc not propagated downstream |
| Agent SDK version breaks | Medium | High | Pre-1.0 API surface changes |
| Generated template fails `next build` | High | Medium | AI-generated code with subtle type errors or import issues |
| Biome-ESLint rule conflicts | Low | Low | Different rule semantics for edge cases |
| Context window overflow | Medium | Medium | 7 documents + conversation history exceeds 200K tokens |

### 3.4 Expected Development Period

| Phase | Weeks | Features | Confidence |
|-------|-------|----------|-----------|
| Foundation + F1 (Conversation Engine) | 3 | F1 | 95% |
| Document Pipeline (F2) | 5 | F2 | 85% |
| Template (F3) | 4 | F3 | 80% |
| Context Propagation (F4) | 3 | F4 | 75% |
| Editable Documents (F5) | 2 | F5 | 85% |
| Free/Paid Boundary (F6) | 2 | F6 | 90% |
| 15-min First Experience (F7) | 2 | F7 | 80% |
| Cross-Validation (F8) | 3 | F8 | 70% |
| **Total production weeks** | **24** | **8 features** | |
| **Buffer** | **2 weeks (7.7%)** | — | |
| **Total timeline** | **26 weeks** | | |

**Buffer assessment**: 2 weeks is thin. This is the primary risk of the cutting-edge scenario. The Balanced scenario allocates 3 weeks (11.5%) and the Conservative scenario allocates 30%+. At 7.7%, one significant unexpected issue (Agent SDK breaking change, Claude API behavioral shift, personal emergency) could cascade into missed deadlines.

---

## 4. Risk and Mitigation

### 4.1 Risk Matrix

| # | Risk | Probability | Impact | Severity | Mitigation | Fallback if Mitigation Fails |
|---|------|------------|--------|----------|-----------|------------------------------|
| R1 | **Agent SDK breaking changes** (pre-1.0 API) | 40% | HIGH | CRITICAL | Use Agent SDK for orchestration shell only. Core logic in direct Claude API calls. Pin version, test against canary. | Drop Agent SDK entirely; replace with custom orchestration using raw Claude API. Cost: 2-3 weeks refactoring. |
| R2 | **Structured Outputs edge cases** (schema compilation failures) | 25% | HIGH | HIGH | Extensive Zod schema testing. Maintain fallback to prompt-based JSON + Zod validation. Design schemas to avoid deep nesting (>5 levels). | Fall back to prompt-based JSON generation with Zod `safeParse()` + retry loop (adds 5-10% latency, ~2% failure rate). |
| R3 | **Claude API pricing change** (cost model shift) | 20% | HIGH | HIGH | LLMAdapter interface abstracts all Claude-specific calls. BYOK model means user bears costs. Monitor Anthropic announcements. | LLMAdapter enables swap to OpenAI/Gemini. Migration effort: 2-4 weeks for adapter implementation + prompt tuning. |
| R4 | **Solo founder burnout** (26 weeks, cutting-edge tech, 7.7% buffer) | 35-45% | HIGH | HIGH | Strict 50-hour/week cap. F8 (Cross-Validation) as the first cut candidate if behind. Weekly "energy audit" — if two consecutive red weeks, switch to Conservative plan. | Cut F8 and F7 (save 5 weeks). Ship 6-feature product with 7-week buffer (27%). Quality over scope. |
| R5 | **Template code quality** (generated Next.js code fails in production) | 30-40% | MEDIUM | MEDIUM | Automated `next build` + `biome check` in CI for every generated template variant. Human curation of template base. Golden-file tests for template output. | Reduce template ambition: generate project structure + routing + data models only, leave component logic to user + Cursor/Copilot. |

### 4.2 Technology-Specific Failure Contingencies

**If Agent SDK fails**: The entire system can run on direct Claude API calls + custom async orchestration. The Agent SDK adds convenience (subagent isolation, automatic context management) but is not architecturally essential. The `LLMAdapter` interface means zero coupling between core logic and the SDK.

**If Structured Outputs fails for complex schemas**: Degrade gracefully to prompt-based JSON generation → Zod `safeParse()` → retry on failure. This was the standard approach before Structured Outputs and works at ~95-98% reliability (vs 100% with Structured Outputs). The schema validation layer catches all malformed outputs regardless.

**If Drizzle ORM proves too immature**: Swap to Prisma 7 in the generated template. Both are TypeScript ORMs with similar APIs. The template layer is isolated from the core pipeline — this swap affects only the `templates/nextjs-supabase-stripe/` directory.

**If Biome lacks critical rules**: Already planned: Biome handles 95% of checks, `next lint` covers the remaining 5% of Next.js-specific rules. If Biome has more gaps than expected, shift to Biome for formatting only + ESLint for linting. Slower, but functional.

**If Prompt Caching underperforms** (low cache hit rates in practice): System still functions — just costs more and is slower. The BYOK model means the cost impact falls on the user. Optimize by stabilizing cache keys: use deterministic system prompts, version template content, separate dynamic (conversation) from static (schema + instructions) context blocks.

---

## 5. 6-Month Milestone Plan

### M1: Month 1-2 (Weeks 1-8) — "Document Engine Alpha"

**Delivered**:
- F1: Conversational SaaS Definition Engine (5-7 smart questions with smart defaults)
- F2: 7-Document Pipeline (PRD, User Journey, TRD, Code Guidelines, UI Guidelines, IA, Tasks)
- LLMAdapter interface with ClaudeAdapter implementation
- Zod schemas for all 7 document types
- Structured Outputs integration (100% schema compliance)
- Prompt Caching integration (90% cost savings on repeat calls)
- File-based session persistence (close laptop, reopen later)
- Unit tests + golden-file tests for all document types

**Release**: Private Alpha (10-15 hand-picked users)

**Success criteria**:
- A user can go from "I want to build X" to 7 structured documents in under 10 minutes
- All generated documents pass Zod schema validation
- Prompt caching achieves >80% cache hit rate on multi-turn conversations
- 0 JSON parse errors (Structured Outputs guarantee)

**Week-by-week**:

| Week | Focus | Deliverable |
|------|-------|-------------|
| W1 | Project setup + CLI scaffold | pnpm monorepo, Commander.js, tsup, Vitest, Biome config |
| W2 | Claude API integration + LLMAdapter | `ClaudeAdapter` with Structured Outputs + Prompt Caching |
| W3 | Conversation Engine (F1) | 5-7 smart questions, domain detection, smart defaults |
| W4 | PRD + User Journey generators | Zod schemas, generation prompts, golden-file tests |
| W5 | TRD + Code Guidelines generators | Architecture decisions, tech stack selection logic |
| W6 | UI Guidelines + IA generators | Design system generation, navigation structure |
| W7 | Tasks generator + pipeline integration | Full pipeline: conversation → 7 documents |
| W8 | Alpha testing + bug fixes | Private alpha release, feedback collection |

### M2: Month 3-4 (Weeks 9-18) — "Template + Intelligence"

**Delivered**:
- F3: Next.js + Supabase + Stripe template (scaffolded from documents)
- F4: Cross-document context propagation (unidirectional V1)
- F5: Editable intermediate documents with re-propagation
- F6: Free/Paid boundary (3 projects free, Pro at $19/month)
- Agent SDK integration for subagent-based document generation
- Incremental regeneration (only regenerate downstream docs on change)

**Release**: Public Beta + Product Hunt launch

**Success criteria**:
- Generated Next.js project passes `next build` + `biome check`
- Editing a PRD feature automatically updates TRD and Tasks
- Free-to-paid boundary is functional (Stripe integration for Pro tier)
- Public Beta has 40-90 active users

**Week-by-week**:

| Week | Focus | Deliverable |
|------|-------|-------------|
| W9 | Template engine foundation | `TemplateRegistry` interface, scaffold system |
| W10 | Next.js template: project structure + routing | App Router setup, layout generation |
| W11 | Next.js template: Supabase Auth + DB | Auth flow, RLS policies, Drizzle schema from TRD |
| W12 | Next.js template: Stripe + shadcn/ui | Supabase Stripe Sync, payment pages, UI components |
| W13 | Context propagation (F4) | Document dependency graph, change detection |
| W14 | Context propagation: incremental regen | Only regenerate affected downstream docs |
| W15 | Editable documents (F5) | Markdown editor integration, diff detection |
| W16 | Free/Paid boundary (F6) | Project counter, license check, Stripe subscription |
| W17 | Agent SDK integration | Subagent-per-document, context isolation |
| W18 | Public Beta prep + Product Hunt | Documentation, onboarding, launch |

### M3: Month 5-6 (Weeks 19-26) — "Quality + Launch"

**Delivered**:
- F7: 15-minute first experience (guided onboarding)
- F8: Basic cross-validation engine (Sonnet generates, Opus validates)
- LLM-as-judge weekly quality pipeline
- Performance optimization (caching, latency)
- Documentation site
- Pro tier launch with pricing

**Release**: General Availability (GA) + Pro tier live

**Success criteria**:
- New user completes first project (idea → 7 docs) in under 15 minutes
- Cross-validation catches >50% of inconsistencies between documents
- 220-350 cumulative users, 40-80 paid subscribers
- $760-$1,520 MRR
- NPS > +40

**Week-by-week**:

| Week | Focus | Deliverable |
|------|-------|-------------|
| W19 | 15-min experience (F7) | Guided walkthrough, progress indicators, help text |
| W20 | 15-min experience: optimization | Reduce friction points identified in beta feedback |
| W21 | Cross-validation engine (F8) | Sonnet→generate, Opus→validate architecture |
| W22 | Cross-validation: consistency rules | PRD↔TRD, TRD↔Code Guidelines, etc. |
| W23 | Cross-validation: reporting | Inconsistency report with suggested fixes |
| W24 | Quality hardening + perf optimization | Cache hit rate optimization, latency reduction |
| W25-26 | **Buffer** | Bug fixes, edge cases, documentation, GA prep |

### Milestone Timeline Visualization

```
Month 1          Month 2          Month 3          Month 4          Month 5          Month 6
W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11 W12 W13 W14 W15 W16 W17 W18 W19 W20 W21 W22 W23 W24 W25 W26
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│◀─── F1: Conversation ───▶│                                                                           │
│       │◀────── F2: 7-Doc Pipeline ──────▶│                                                           │
│                           │◀──── F3: Template ────▶│                                                 │
│                                         │◀── F4: Context Propagation ──▶│                            │
│                                                    │◀─ F5 ─▶│                                       │
│                                                           │◀─ F6 ─▶│                                │
│                                                                     │◀─ F7 ─▶│                      │
│                                                                              │◀── F8: CrossVal ──▶│ │
│                                                                                                 │BUF│
│                           ▲                                   ▲                                 ▲   │
│                     Private Alpha                        Public Beta                           GA    │
│                      (10-15 users)                      + ProductHunt                      + Pro $19 │
```

---

## 6. V2 Readiness Assessment

### 6.1 Architecture Preparedness

| V2 Feature | Readiness | Architecture Support | Migration Effort |
|-----------|-----------|---------------------|-----------------|
| **Template Marketplace** | HIGH | `TemplateRegistry` interface designed for extensibility. Community templates register via standard interface. | 3-4 weeks: marketplace UI, template validation pipeline, revenue sharing logic |
| **Multi-Framework** (Svelte, Nuxt, Astro) | HIGH | Template layer is fully decoupled from core. Each framework is a new `SaaSTemplate` implementation. Document pipeline is framework-agnostic. | 4-6 weeks per framework: template creation + testing |
| **Web GUI** | MEDIUM | Core engine is CLI-independent (all logic in `core/`). GUI would be a new frontend consuming the same `DocumentPipeline` and `TemplateRegistry` interfaces. | 6-8 weeks: Next.js dashboard, WebSocket for real-time generation, session management |
| **Multi-LLM** (OpenAI, Gemini, local models) | HIGH | `LLMAdapter` interface abstracts all LLM operations. New adapters implement the same interface. | 2-4 weeks per LLM: adapter implementation + prompt tuning. Structured Outputs parity is the risk — not all LLMs guarantee schema compliance. |
| **One-Click Deploy** (Vercel, Netlify, Railway) | MEDIUM | Generated template is already a standard Next.js project. Deploy commands are additions to CLI. | 3-4 weeks: deployment provider abstractions, credential management, DNS setup |
| **RAG-Powered Learning** (learn from past projects) | MEDIUM-HIGH | Supabase Vector Buckets (already in generated stack) enable vector storage. MCP protocol enables agent access to vector search. | 4-6 weeks: embedding pipeline, similarity search, context injection into document generation |

### 6.2 Technical Debt Position for V2

The cutting-edge scenario accumulates moderate technical debt, but it is *intentional* debt in well-understood areas:

- **Agent SDK coupling** (if used): Pre-1.0 API may change. Debt is contained behind `LLMAdapter`.
- **Single-template limitation**: Only Next.js+Supabase+Stripe in V1. Debt is contained behind `TemplateRegistry`.
- **Unidirectional propagation**: V1 context propagation is one-way (upstream → downstream). Bidirectional propagation (editing Tasks affects TRD) is V2.
- **No Web GUI**: CLI-only in V1. The `core/` layer is GUI-agnostic, so no architectural debt — just missing functionality.

**No deep structural debt**: The key interfaces (`LLMAdapter`, `TemplateRegistry`, `DocumentPipeline`) are designed for extension. V2 features are additive, not refactoring-dependent.

---

## 7. Team Signatures

### Frontend Lead Assessment

**Rating: Challenging** (leaning Realistic)

*Rationale*: The generated template stack (Next.js 15 + shadcn/ui + Tailwind v4 + Drizzle + Supabase) is the most popular modern stack for SaaS — any competent React developer can work with it. The risk is in the *generation* of correct Next.js code by the LLM, not in the stack itself. App Router + Server Components + Server Actions have a non-trivial learning curve, and generating correct RSC patterns requires deep understanding of the client/server boundary. Turbopack's bundle size regression (+211KB) is acceptable for SaaS but should be monitored. The decision to defer Ink to V2 and use Inquirer.js in V1 is wise — it removes a significant learning surface from the critical path.

*Key concern*: shadcn/ui v4 (January 2026 update) may have undiscovered edge cases in generated code. Recommendation: pin shadcn component versions in the template.

### Backend Lead Assessment

**Rating: Challenging**

*Rationale*: The LLM integration layer is where the true complexity lives. Claude Structured Outputs is production-ready, but schema design for 7 document types is non-trivial — schemas must be strict enough to validate but flexible enough for LLM generation. The Zod → JSON Schema → Claude pipeline has known edge cases with discriminated unions and recursive types. Prompt Caching requires careful cache key management (any change in system prompt invalidates cache). The Agent SDK adds a powerful abstraction but is pre-1.0 — expect at least one breaking change during the 6-month window.

*Key concern*: Context window management across 7 documents + conversation history. A fully elaborated project could exceed 200K tokens. Recommendation: implement document summarization for context injection — feed summaries of upstream documents, not full text, into downstream generators.

### DevOps Lead Assessment

**Rating: Realistic**

*Rationale*: The infrastructure story is deliberately simple. File-based state (no database to manage), npm distribution (no container orchestration), GitHub Actions CI (no custom infrastructure). Biome + Vitest + tsup is a clean, fast toolchain with minimal configuration. The only operational complexity is the weekly LLM-as-judge pipeline (Batch API), which is a cron job, not a service. The BYOK model means we do not operate LLM infrastructure. semantic-release + npm OIDC is a well-trodden path.

*Key concern*: Monitoring LLM costs and cache hit rates for users. Recommendation: add telemetry (opt-in) for cache hit rates and token usage to identify optimization opportunities.

### CTO Assessment

**Rating: Challenging** (with high conviction)

*Rationale*: This is the right technology bet for an AI-native product. The cutting-edge stack is not cutting-edge for the sake of novelty — each choice has a concrete, measurable justification:

- Structured Outputs: eliminates an entire class of bugs (JSON parsing)
- Prompt Caching: transforms the economics (90% cost reduction)
- Agent SDK: provides the orchestration model that powers the most successful AI coding tool (Claude Code itself)
- Biome: 56x faster linting enables tighter feedback loops
- Drizzle: 7KB vs 1.6MB is material for serverless SaaS templates

The 7.7% buffer is the weakest point. If I were advising this founder, I would recommend cutting F8 (Cross-Validation) to a "basic" version — check for entity name consistency across documents rather than full semantic validation. This saves 1-2 weeks of buffer without losing the feature entirely.

The single-vendor dependency on Anthropic is real but manageable. The `LLMAdapter` interface is the insurance policy. MCP adoption by all major LLM providers (OpenAI, Google, Microsoft) means the orchestration layer is portable even if we switch LLM providers.

*Verdict*: Proceed with this stack. The technical risk is acceptable for the competitive advantage gained. The worst-case scenario (Agent SDK breaks, must refactor to raw API calls) costs 2-3 weeks — within recoverable range if F8 is descoped first.

---

## 8. Conclusion

### Recommendation Strength: 7.5/10

This is a strong recommendation tempered by the acknowledgment that the thin buffer (7.7%) makes it a high-wire act. The technology choices themselves are individually sound — each has production adoption, measurable benchmarks, and clear justification. The risk is cumulative: learning Agent SDK + designing 7 Zod schemas + building context propagation + engineering a template that generates compilable code, all in 24 production weeks with a 2-week buffer.

**The 2.5 points deducted are for**:
1. **Buffer risk** (1.0 point): 7.7% buffer is insufficient for a scenario with this many cutting-edge technologies. One significant unexpected issue cascades into missed deadlines.
2. **Agent SDK pre-1.0 risk** (0.5 points): Real possibility of breaking changes during the 6-month window.
3. **Cumulative learning curve** (0.5 points): ~5-6 weeks of parallel learning on top of 24 weeks of production work. Manageable but cognitively demanding for a solo founder.
4. **Solo founder concentration risk** (0.5 points): No redundancy. If the founder is out for 2 weeks (illness, personal), the thin buffer evaporates entirely.

### Who Should Choose This Scenario

- A solo founder with **3+ years of TypeScript/React experience** and comfort with rapid technology adoption
- Someone who has **previously used Claude API** (or any LLM API) and understands prompt engineering fundamentals
- A founder who views **learning new tools as energizing rather than draining** — cutting-edge requires intellectual curiosity
- Someone whose **competitive thesis depends on technical excellence** — the argument that "a better generator produces better SaaS" requires the generator itself to be state-of-the-art
- A founder with **personal financial runway of 12+ months** (the 6-month timeline may extend to 8 months)

### Who Should NOT Choose This Scenario

- A founder with **less than 2 years of TypeScript experience** — the learning curve will dominate the timeline
- Someone who **prioritizes predictability over performance** — the Balanced scenario (11.5% buffer) or Conservative scenario (30%+ buffer) are more appropriate
- A founder who **cannot tolerate 2-3 weeks of refactoring** if a technology bet fails (Agent SDK, Drizzle, Biome) — the fallback paths exist but take time
- Someone with **external deadlines or investor commitments** — the thin buffer means delivery date is probabilistic, not guaranteed
- A founder who is **also doing significant marketing/sales** in the same 6 months — the 50-hour/week budget assumes 50% development time, but cutting-edge tech demands closer to 60% development time in months 1-3

### Comparative Position

| Dimension | Cutting Edge (This) | Balanced | Conservative |
|-----------|-------------------|----------|-------------|
| Features | 8 | 8 | 4 |
| Buffer | 2 weeks (7.7%) | 3 weeks (11.5%) | 30%+ |
| Failure probability | 20-25% | 10-15% | 5% |
| Generated output quality | Highest | High | Medium |
| V2 readiness | Highest | High | Medium |
| Learning investment | 5-6 weeks | 3-4 weeks | 1-2 weeks |
| Tech debt | Low-Medium (intentional) | Medium | Very Low |
| Competitive differentiation | Strongest | Strong | Adequate |
| MRR target (Month 6) | $760-$1,520 | $760-$1,520 | $285-$760 |

### Final Verdict

The Cutting Edge scenario is the **maximum-conviction bet** on the thesis that AI-native tooling, applied to the problem of SaaS generation, creates a differentiated product that justifies the risk. Every technology choice — from Structured Outputs eliminating JSON parsing bugs to Prompt Caching transforming the cost structure to the Agent SDK providing production-grade orchestration — is in service of one goal: making the generated output so good that users cannot achieve the same quality with any competitor.

The trade-off is real: higher risk of timeline slippage, dependency on pre-1.0 tooling, and a solo founder working near maximum capacity for 6 months. But the upside is equally real: if executed, this stack produces the most technically sophisticated document-driven SaaS generator on the market, with clear extension paths to marketplace, multi-framework, and multi-LLM in V2.

**The recommendation**: Choose this scenario if you are a technically strong founder who believes that the window for spec-driven, local-first SaaS generation is narrow (14 weeks before competitors adapt) and that only the most capable technology stack will produce output good enough to compete. Choose Balanced if you want the same 8 features with more safety margin.

---

## Appendix A: Cost Model

### Per-Project LLM Cost (BYOK)

| Operation | Tokens | Cost (Sonnet 4.6) | With Caching (90%) | With Batch (50%) |
|-----------|--------|-------------------|--------------------|--------------------|
| Conversation (5-7 turns) | ~15K in / ~5K out | $0.12 | $0.02 | $0.01 |
| 7 Document Generation | ~100K in / ~50K out | $1.05 | $0.14 | $0.07 |
| Cross-Validation (Opus) | ~50K in / ~10K out | $0.90 | $0.12 | $0.06 |
| Template Scaffolding | ~30K in / ~20K out | $0.39 | $0.05 | $0.03 |
| **Total per project** | | **$2.46** | **$0.33** | **$0.17** |

**User-facing cost**: $0.17-$2.46 per project depending on caching efficiency. At scale (repeat usage), approaches $0.17 per project. This is dramatically cheaper than any cloud-based competitor (Lovable: $20-100/month for credits; Bolt.new: reports of $1,000+ per complex project).

### Monthly Operating Cost (Founder)

| Item | Monthly Cost |
|------|-------------|
| Claude API (development + testing) | $300-$800 |
| Domain + docs hosting (Vercel free tier) | $20-$50 |
| GitHub (free tier sufficient) | $0 |
| npm publishing (free) | $0 |
| Tooling (Linear free tier, analytics) | $0-$50 |
| **Total** | **$320-$900** |

---

## Appendix B: Technology Version Pinning Strategy

```json
{
  "engines": { "node": ">=22.0.0" },
  "dependencies": {
    "@anthropic-ai/sdk": "^0.35.x",
    "commander": "^12.x",
    "inquirer": "^9.x",
    "zod": "^3.23.x",
    "zod-to-json-schema": "^3.x"
  },
  "devDependencies": {
    "@biomejs/biome": "^2.x",
    "tsup": "^8.x",
    "tsx": "^4.x",
    "vitest": "^2.x",
    "typescript": "^5.x"
  }
}
```

**Pinning philosophy**: Use `^` (caret) for stable dependencies (Commander, Zod, Vitest). Use exact versions for pre-1.0 dependencies (Agent SDK) to prevent unexpected breaks. Run `pnpm update --interactive` monthly to audit and selectively update.

---

## Sources

### LLM & AI Infrastructure
- [Claude Model Specifications — Anthropic Docs](https://docs.anthropic.com/en/docs/about-claude/models)
- [Claude Structured Outputs — Anthropic Docs](https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs)
- [Prompt Caching — Anthropic Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Message Batches — Anthropic Docs](https://docs.anthropic.com/en/docs/build-with-claude/message-batches)
- [Claude Agent SDK — Anthropic](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
- [MCP Specification — Model Context Protocol](https://modelcontextprotocol.io)
- [Claude Code $2.5B Run-Rate — Uncover Alpha](https://www.uncoveralpha.com/p/anthropics-claude-code-is-having)
- [16 Claude Agents Write C Compiler — Anthropic](https://claude.com/blog/claude-agents-c-compiler)

### Framework & Build Tools
- [Next.js 15 Release — Vercel](https://nextjs.org/blog/next-15)
- [Turbopack Performance Benchmarks — Vercel](https://turbo.build/pack/docs/benchmarks)
- [Biome 2.0 Release — Biome](https://biomejs.dev/blog/biome-v2/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS v4 — Tailwind Labs](https://tailwindcss.com/blog/tailwindcss-v4)

### Backend & Integration
- [Supabase Stripe Sync Engine — Supabase Blog](https://supabase.com/blog/stripe-sync-engine)
- [Supabase Vector Buckets — Supabase Blog](https://supabase.com/blog/vector-buckets)
- [Vercel Next.js Subscription Payments Template](https://github.com/vercel/nextjs-subscription-payments)
- [Zod Documentation](https://zod.dev/)
- [zodToJsonSchema — npm](https://www.npmjs.com/package/zod-to-json-schema)

### Quality & Testing
- [AI Code Creates 1.7x More Issues — CodeRabbit](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- [45% AI Code Fails Security Tests — Veracode](https://www.veracode.com/resources/state-of-software-security)
- [Vitest Documentation](https://vitest.dev/)

### Market Context
- [Cursor $2B+ ARR — Fortune](https://fortune.com/2025/12/11/cursor-ipo-1-billion-revenue-brainstorm-ai/)
- [Lovable $300M ARR — Sacra](https://sacra.com/c/lovable/)
- [Spec-Driven Development — ThoughtWorks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
- [Solo Founders +340% YoY — Indie Hackers](https://www.indiehackers.com/post/2026-saas-market-report-key-insights-95423fc66b)
