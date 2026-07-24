# SaaS Auto-Builder: BALANCED-TECH Technology Scenario

**Scenario Philosophy**: "Good technology, but we must be able to execute."
**Perspective**: Technology leader who balances innovation with pragmatism
**Risk Profile**: Medium — cherry-picks cutting-edge where it provides unbridgeable advantage, conservative where stability matters more
**Date**: 2026-03-12
**Target**: Solo founder, 6 months (26 weeks), 8 features

---

## Executive Summary

The Balanced-Tech scenario is the product of aggressive cherry-picking across all four Phase 2 discussion perspectives (Latest, Stability, Speed, Maintainability). Rather than committing to a single philosophy, this scenario treats each technology layer as an independent decision point: where Phase 2 discussions achieved 3/4 or 4/4 consensus, we adopt without debate; where they diverged, we pick the choice that maximizes execution probability while preserving V2 optionality.

The result is a stack that is conservative at the CLI and state management layers (where stability prevents session-breaking bugs), aggressive at the document pipeline and LLM integration layers (where Structured Outputs and Prompt Caching provide unbridgeable advantages that cannot be replicated with older approaches), and deliberately minimal at the architecture layer (where evolutionary architecture with Day-1 interfaces delivers 2-3 more features than Big Bang in 26 weeks).

**Key numbers**: 23.5 weeks of development, 2.5 weeks of buffer, 87% confidence, $460-$840 total 6-month cost.

---

## 1. Complete Technology Stack (Cherry-Picked)

### 1.1 CLI Interface Layer

| Decision | Choice |
|----------|--------|
| **Framework** | **Commander.js v12 + Inquirer.js v12** |
| Why over alternatives | 4/4 Phase 2 consensus. Commander.js has 12+ years of stability, 26K+ GitHub stars, zero breaking API changes in major versions. Inquirer.js provides rich interactive prompts (list, checkbox, confirm, input) that map directly to the conversational Q&A flow. Alternatives considered: **Ink** (React-based terminal UI) was explicitly rejected by all 4 discussions for V1 — it adds React as a runtime dependency for terminal rendering, introduces JSX compilation step, and the learning curve consumes 1-2 weeks that produce zero user-facing value. Ink remains a strong V2 candidate for dashboard/progress UI. **Oclif** was considered but rejected: it imposes a plugin architecture that adds complexity without benefit for a single-binary CLI. |
| Phase 2 agreement | 4/4 (unanimous) |
| Risk level | **Low** — battle-tested, massive community, no surprises |
| Version pinning | `commander@^12.0.0`, `inquirer@^12.0.0` |

**Day-1 Interface**: `CLIAdapter` interface (2 hours to define). Abstracts prompt collection from rendering. Enables Ink migration in V2 without touching business logic.

### 1.2 LLM Integration Layer

| Decision | Choice |
|----------|--------|
| **SDK** | **Anthropic SDK v0.52+ (TypeScript)** |
| Why | Direct SDK provides full control over Prompt Caching, Structured Outputs, streaming, and error handling. The Claude Agent SDK was rejected by 3/4 discussions for V1 — it adds an abstraction layer that hides caching behavior, complicates structured output extraction, and couples the codebase to Anthropic's opinionated agent loop. Direct SDK + manual orchestration gives us exactly the control we need. |
| Phase 2 agreement | 3/4 (no Agent SDK); 4/4 (Anthropic SDK) |
| Risk level | **Low** — Anthropic SDK is the primary integration path, well-documented |

| Decision | Choice |
|----------|--------|
| **Prompt Caching** | **Built-in from Day 1** |
| Why | 76-90% cost reduction is not optional — it is the difference between $0.15/session and $0.60/session. Automatic via SDK `cache_control` parameter on system prompts and large context blocks. Phase 2 Speed discussion measured: first call to Claude at full price, subsequent calls at 90% discount on cached prefix. For a multi-turn conversation engine (Feature 1), this means turns 2-N cost 10% of turn 1. |
| Phase 2 agreement | 3.5/4 (near-unanimous) |
| Risk level | **Low** — built into SDK, zero additional infrastructure |

| Decision | Choice |
|----------|--------|
| **Structured Outputs** | **Native Claude Structured Outputs (JSON mode + tool_use)** |
| Why | 100% schema compliance eliminates retry logic entirely. Phase 2 data: zero parse failures across all test runs. Combined with Zod schemas, this creates a pipeline where the LLM output is guaranteed to match the TypeScript type. No `try/catch` JSON parsing, no "please format as JSON" prompt hacking, no retry loops. This is the single biggest productivity multiplier in the stack. |
| Phase 2 agreement | 4/4 (unanimous) |
| Risk level | **Low** — production-proven, deterministic behavior |

**Day-1 Interface**: `LLMAdapter` interface (1-2 hours to define). Methods: `generateStructured<T>(prompt, schema): Promise<T>`, `generateStream(prompt): AsyncIterable<string>`, `estimateCost(prompt): CostEstimate`. Enables Multi-LLM (GPT-4o, Gemini) in V2 with zero business logic changes.

### 1.3 Document Pipeline Layer (Schema, Validation, Generation)

| Decision | Choice |
|----------|--------|
| **Schema Definition** | **Zod v3.24+** |
| Why | Single source of truth: one Zod schema produces TypeScript types (via `z.infer`), runtime validation, and LLM JSON Schema (via `zodToJsonSchema`). Alternatives: **TypeBox** (faster validation but no ecosystem), **io-ts** (functional style, steeper learning curve), **raw JSON Schema** (no type inference, manual sync). Zod wins because it collapses three concerns into one definition. |
| Phase 2 agreement | 4/4 (unanimous) |
| Risk level | **Low** — 25K+ stars, standard in TypeScript ecosystem |

| Decision | Choice |
|----------|--------|
| **Document Types** | **7 Zod schemas: PRD, TRD, UserJourney, UIGuidelines, CodeGuidelines, InformationArchitecture, TaskList** |
| Why | Each document type gets a versioned Zod schema. Schema evolution via `z.union([v1Schema, v2Schema])` with migration functions. This is where Structured Outputs + Zod combine to create the "unbridgeable advantage": the LLM is constrained to produce exactly these schemas, validation is automatic, and TypeScript catches schema mismatches at compile time. |
| Phase 2 agreement | 4/4 (design); 3/4 (Zod specifically) |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Markdown Generation** | **Template literals + custom renderer** |
| Why | Document output is Markdown. A thin rendering layer (100-200 lines) converts Zod-validated objects to formatted Markdown. No template engine dependency needed — template literals with tagged templates handle this cleanly. Handlebars/EJS were considered but rejected: they add a dependency and a separate template language for what amounts to string interpolation. |
| Phase 2 agreement | 3/4 |
| Risk level | **Low** |

### 1.4 Code Scaffolding Layer (Template Rendering)

| Decision | Choice |
|----------|--------|
| **Template Engine** | **Handlebars v4.7 + file-based templates** |
| Why | For code generation (as opposed to document generation), Handlebars provides the right level of abstraction: partials for reusable components, helpers for conditional logic, and a clear separation between template and data. EJS was considered but its `<%= %>` syntax inside TypeScript/JSX templates creates escaping nightmares. Handlebars' `{{}}` syntax is visually distinct from generated code. |
| Phase 2 agreement | 3/4 |
| Risk level | **Low** — mature, stable, well-understood |

| Decision | Choice |
|----------|--------|
| **Template Registry Pattern** | **1.5-day investment on Day 1** |
| Why | A simple registry (`Map<string, TemplateConfig>`) that maps template IDs to file paths, metadata, and validation schemas. This is the V2 enabler for Template Marketplace. Without it, adding new templates requires code changes. With it, templates are data. Investment: 1.5 days. Return: marketplace-ready architecture from Day 1. |
| Phase 2 agreement | 3/4 (Speed discussion deferred it; other 3 agreed) |
| Risk level | **Low** — simple pattern, high optionality value |

### 1.5 Generated SaaS Template Stack

This is the technology stack that SaaS Auto-Builder generates for its users, not the stack it is built with.

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | **Next.js 15 (App Router)** | 4/4 consensus. Dominant React meta-framework, 150K+ GitHub stars. App Router is now stable and the recommended path. Server Components reduce client bundle. API routes eliminate separate backend for simple SaaS. |
| **Database** | **Supabase (PostgreSQL + Auth + Realtime)** | 4/4 consensus. Supabase is the default backend for AI app builders (Bolt.new, Lovable both generate Supabase backends). Free tier is generous. Auth, storage, and realtime subscriptions built-in. Eliminates 3-4 separate service integrations. |
| **ORM** | **Drizzle ORM** | 3/4 consensus. Type-safe, SQL-like API, zero runtime overhead. Generates migrations from schema. Prisma was the alternative: heavier runtime (query engine binary), slower cold starts, more opinionated. Drizzle's SQL-first approach produces more predictable queries for AI-generated code. |
| **Payments** | **Stripe (via @stripe/stripe-js + stripe)** | 4/4 consensus. No real alternative for SaaS billing. Checkout Sessions for quick integration, Customer Portal for subscription management. |
| **UI Components** | **shadcn/ui + Tailwind CSS v4** | 4/4 consensus. shadcn/ui is copy-paste components (not a package dependency), which means generated code owns its UI completely. Tailwind v4 is CSS-first (no PostCSS config), which simplifies the generated project's build pipeline. |
| **Email** | **Resend** | 3/4 consensus. Simple API, generous free tier (100 emails/day), React Email for templates. |

| Risk level | **Low** — this is the most popular "indie SaaS" stack in 2026 |

### 1.6 Build and Dev Tooling

| Decision | Choice |
|----------|--------|
| **Runtime** | **Node.js 22 LTS** |
| Why | LTS channel ensures 30 months of support. Native `--experimental-strip-types` flag enables running TypeScript directly without build step during development. ESM-first. |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **TypeScript** | **TypeScript 5.7+ (strict mode)** |
| Why | 4/4 unanimous. `strict: true` catches 40%+ of runtime errors at compile time. Combined with Zod, this creates a type-safe pipeline from LLM output to file system. |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Build** | **tsup v8 (esbuild-based)** |
| Why | Single-command build for CLI distribution. Produces CJS + ESM bundles. 100x faster than tsc for production builds. Handles shebang injection for CLI binary. |
| Phase 2 agreement | 3/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Package Manager** | **pnpm v9** |
| Why | 3x faster installs than npm, hard links save disk space, strict dependency resolution catches phantom dependencies. `pnpm` workspace support if we ever need monorepo. |
| Phase 2 agreement | 3/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Linting/Formatting** | **Biome v1.9 + minimal ESLint (boundary rules only)** |
| Why | This is the cherry-pick that defines Balanced-Tech. Biome handles 80% of linting + 100% of formatting at 56x the speed of ESLint+Prettier. For the ~20% of rules Biome misses (import boundaries, no-restricted-imports for architecture enforcement), we keep a minimal ESLint config with exactly those rules. Two tools, but each doing what it does best. Total config: ~30 lines of Biome config + ~15 lines of ESLint config. |
| Phase 2 agreement | 3/4 (Biome primary); 1/4 preferred ESLint-only |
| Risk level | **Medium** — two-tool setup requires clear documentation on which tool owns what |

### 1.7 Testing

| Decision | Choice |
|----------|--------|
| **Test Runner** | **Vitest v3** |
| Why | 4/4 unanimous. Native ESM support, TypeScript without config, Jest-compatible API, 5-10x faster than Jest. Watch mode with HMR. Built-in coverage via `@vitest/coverage-v8`. |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Coverage Targets** | **Unit: 80%, Integration: 60%, E2E: key flows only** |
| Why | Unit tests for Zod schemas, document pipeline, template rendering. Integration tests for CLI flow (Commander.js command → LLM call → file output). E2E tests for the 3 critical user journeys (new project, resume project, generate code). Coverage targets are floors, not ceilings. |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Snapshot Testing** | **Vitest snapshots for generated documents** |
| Why | Generated Markdown documents should not change unexpectedly. Snapshot tests catch regressions in document structure. Updated intentionally when schemas evolve. |
| Risk level | **Low** |

### 1.8 CI/CD

| Decision | Choice |
|----------|--------|
| **CI** | **GitHub Actions (free for OSS)** |
| Why | 4/4 consensus. 2000 free minutes/month for public repos. Matrix testing (Node 20, 22). Runs: lint → typecheck → test → build. |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **CD** | **npm publish via GitHub Actions on tag push** |
| Why | `npm publish` on `v*` tag push. Automated changelog via `changesets`. Simple, proven, no custom infrastructure. |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **Release Strategy** | **Semantic versioning + changesets** |
| Why | `@changesets/cli` manages version bumps and changelogs. Each PR includes a changeset file describing the change. On merge to main, a "Version Packages" PR is auto-created. Merging that PR triggers npm publish. |
| Risk level | **Low** |

### 1.9 Quality Enforcement

| Decision | Choice |
|----------|--------|
| **Pre-commit** | **lint-staged v15 + husky v9** |
| Why | Runs Biome format + ESLint boundary check + TypeScript typecheck on staged files only. Prevents broken code from entering the repository. Fast because it only checks changed files. |
| Risk level | **Low** |

| Decision | Choice |
|----------|--------|
| **PR Checks** | **Required: CI green + 1 self-review checklist** |
| Why | Solo founder cannot do peer review. Instead: a checklist in the PR template covering schema compatibility, test coverage delta, and breaking change assessment. CI must pass. No merge without green checks. |
| Risk level | **Low** |

### 1.10 State Management

| Decision | Choice |
|----------|--------|
| **Runtime State** | **File-based JSON state (single file per project)** |
| Why | 4/4 consensus. A SaaS Auto-Builder project stores its state in `~/.saas-auto-builder/projects/{id}/state.json`. This file contains: conversation history references, generated document paths, current phase, completion status. No database for V1 — the filesystem is the database. This aligns directly with Absolute Standard 2 (Single File SOT). |
| Phase 2 agreement | 4/4 |
| Risk level | **Low** — simplest possible persistence, zero dependencies |

| Decision | Choice |
|----------|--------|
| **State Schema** | **Zod schema with versioned migrations** |
| Why | `state.json` has a Zod schema. When the schema evolves (V1 → V1.1), a migration function transforms old state to new state on load. This prevents the "corrupted state file" failure mode. |
| Risk level | **Low** |

### 1.11 Architecture Pattern

| Decision | Choice |
|----------|--------|
| **Pattern** | **Evolutionary Architecture with Minimal Day-1 Interfaces** |
| Why | Phase 2 data: evolutionary architecture delivers 2-3 more features than Big Bang in 26 weeks. We define exactly 2 interfaces on Day 1: `LLMAdapter` (enables Multi-LLM V2) and `TemplateRegistry` (enables Marketplace V2). Everything else starts as direct implementation and is extracted to interfaces only when a second implementation appears. This follows the Rule of Three: abstract on the third use, not the first. |
| Phase 2 agreement | 4/4 (evolutionary); 3/4 (specific interfaces) |
| Risk level | **Medium** — requires discipline to add interfaces at the right time, not too early and not too late |

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Layer (Commander.js)                  │
│                    + Prompts (Inquirer.js)                   │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│   Conversation Engine   │   │      Project Manager          │
│   (multi-turn Q&A)      │   │   (state, resume, history)    │
└─────────────┬───────────┘   └───────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Document Pipeline                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Zod      │  │ LLM      │  │ Validator │  │ Renderer   │  │
│  │ Schemas  │→ │ Adapter  │→ │ (Zod)    │→ │ (Markdown) │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Code Scaffolding                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Template     │  │ Handlebars   │  │ File Writer      │  │
│  │ Registry     │→ │ Engine       │→ │ (project output) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Development Environment and Process

### 2.1 Setup Time Target

| Task | Time | Notes |
|------|------|-------|
| Repository init + TypeScript strict + tsup | 2 hours | Scripted via `pnpm create` |
| Biome + ESLint boundary config | 1 hour | ~45 lines total config |
| Vitest + coverage | 30 min | Zero config with `vitest.config.ts` |
| Commander.js CLI skeleton | 2 hours | 3 commands: `new`, `resume`, `generate` |
| Zod schemas (7 document types, draft) | 4 hours | Iterative — start minimal, expand |
| LLMAdapter interface + Claude implementation | 3 hours | Interface + one concrete impl |
| TemplateRegistry interface + file loader | 2 hours | Interface + filesystem impl |
| GitHub Actions CI pipeline | 1 hour | lint → typecheck → test → build |
| Husky + lint-staged | 30 min | Pre-commit hooks |
| **Total infrastructure setup** | **~2 working days** | Conservative estimate: 3 days with buffer |

### 2.2 Sprint Structure

**1-week sprints**. Rationale: solo founder needs fast feedback loops. Two-week sprints create too much WIP for one person. The week structure:

| Day | Activity |
|-----|----------|
| Monday | Sprint planning (30 min). Pick 1 feature slice or 2-3 smaller tasks. Write failing tests for the week's target. |
| Tue-Thu | Implementation. Commit early, commit often. Each commit should leave the project in a working state. |
| Friday | Integration testing, documentation update, sprint review (solo — write a brief "what shipped" note). Tag a release if the feature is complete. |

### 2.3 Release Cadence

- **Internal (npm `next` tag)**: Every Friday, if tests pass. Allows dogfooding over the weekend.
- **Stable (npm `latest` tag)**: Every 2 weeks, after a full feature is complete and integration-tested.
- **Major milestones**: Week 8 (Alpha — F1-F3), Week 16 (Beta — F1-F6), Week 24 (RC — F1-F8).

### 2.4 Testing Strategy and Coverage Targets

| Test Type | Target | What It Covers | When It Runs |
|-----------|--------|---------------|-------------|
| Unit | 80% line coverage | Zod schemas, document pipeline functions, template helpers, state management | Every commit (pre-commit hook for changed files, CI for all) |
| Integration | 60% line coverage | CLI command → LLM mock → file output end-to-end. State persistence round-trips. | CI on every PR |
| E2E | 3 critical flows | `new project` flow, `resume project` flow, `generate code` flow — with real (cached) LLM calls | Weekly, manually triggered CI job (to manage API costs) |
| Snapshot | All 7 document types | Generated Markdown structure stability | CI on every PR |

**LLM Test Strategy**: All unit/integration tests use **deterministic mocks** that return pre-recorded Structured Output responses. This eliminates API costs in CI and ensures test determinism. E2E tests use real API calls with Prompt Caching to minimize cost.

### 2.5 Quality Gates (What Blocks a Release)

| Gate | Blocks | Automated? |
|------|--------|-----------|
| TypeScript strict compilation errors | PR merge | Yes (CI) |
| Biome lint/format violations | PR merge | Yes (CI) |
| ESLint boundary violations | PR merge | Yes (CI) |
| Unit test failures | PR merge | Yes (CI) |
| Unit coverage below 80% | PR merge | Yes (CI) |
| Integration test failures | Stable release | Yes (CI) |
| Snapshot mismatches (unintentional) | PR merge | Yes (CI) |
| Generated SaaS template fails `pnpm build` | Stable release | Yes (CI, template validation job) |
| Security: `pnpm audit` high/critical | Stable release | Yes (CI) |

### 2.6 Documentation Strategy

- **README.md**: Installation, quick start, 60-second demo GIF. Updated every stable release.
- **Inline JSDoc**: All public functions and interfaces. TypeScript types are self-documenting; JSDoc adds "why" not "what."
- **Architecture Decision Records (ADRs)**: For decisions that were debated (e.g., "Why Biome + ESLint instead of just ESLint?"). Stored in `docs/adr/`. Brief — 1 page max.
- **Generated template docs**: The SaaS template itself includes a README explaining its structure, how to customize, and how to deploy.
- **No separate docs site for V1**: README + JSDoc + ADRs are sufficient. Docs site is a V2 investment.

---

## 3. Realistic Assessment

### 3.1 Development Difficulty

**Medium**. Here is the breakdown:

| Component | Difficulty | Why |
|-----------|-----------|-----|
| CLI skeleton (Commander.js + Inquirer.js) | Easy | Well-documented, no surprises |
| Zod schema design (7 document types) | Medium | Schema design is iterative — getting the PRD schema "right" takes experimentation |
| LLM integration (Structured Outputs) | Easy-Medium | SDK handles the hard parts; prompt engineering is the real work |
| Conversation engine (multi-turn Q&A) | Medium | State management across turns, branching logic, context window management |
| Code scaffolding (Handlebars templates) | Medium | Template authoring is tedious but not difficult. Getting the generated code to actually work requires careful testing. |
| Generated SaaS template (Next.js + Supabase) | Medium-Hard | The generated template must work out of the box. Auth, DB, payments, UI — all must integrate correctly. This is the hardest part of the project. |
| Quality infrastructure (tests, CI, linting) | Easy | One-time setup, then maintenance |

### 3.2 Learning Curve

| Technology | Learning Time | Notes |
|-----------|--------------|-------|
| Commander.js + Inquirer.js | 0 weeks | Assumed known or trivially learnable |
| Zod | 0.5 weeks | If not already familiar. Core API is small. |
| Anthropic SDK + Structured Outputs | 1 week | Prompt engineering iteration, not SDK complexity |
| Biome | 0 days | Drop-in replacement for ESLint+Prettier for most rules |
| Drizzle ORM (for generated template) | 0.5 weeks | SQL-first API is intuitive if you know SQL |
| Vitest | 0 days | Jest-compatible API |
| **Total learning overhead** | **~2 weeks** | Absorbed into Weeks 1-3 of development |

### 3.3 Expected Development Period

| Category | Weeks |
|----------|-------|
| Infrastructure + schemas | 2 |
| 8 features (detailed below) | 19.5 |
| Quality hardening + integration testing | 2 |
| **Subtotal** | **23.5** |
| **Buffer** | **2.5** |
| **Total** | **26** |

### 3.4 Confidence Level

**87%**. Rationale:
- Conservative CLI layer eliminates the "framework fighting" risk that Cutting Edge faces (Ink, Effect-TS).
- Structured Outputs eliminate retry/parsing logic that Proven Stack must build manually.
- 2.5 weeks of buffer absorbs 1 unexpected problem (e.g., Claude API behavior change, Zod edge case).
- The highest-risk item (generated SaaS template working out-of-box) has ample precedent from Bolt.new/Lovable templates.
- Solo founder risk: illness, burnout, life events. Buffer partially addresses this but cannot fully mitigate.

---

## 4. Detailed 6-Month Timeline

### Phase 0: Infrastructure (Weeks 1-2)

| Week | Task | Technology Focus | Deliverable | Hours |
|------|------|-----------------|-------------|-------|
| 1 | Repository setup, TypeScript strict, tsup build | Node.js 22, TS 5.7, tsup, pnpm | Working `npx saas-auto-builder --version` | 20 |
| 1 | Biome + ESLint config, Vitest, husky/lint-staged | Biome 1.9, ESLint 9, Vitest 3 | Green CI pipeline with lint → typecheck → test → build | 8 |
| 1 | Day-1 interfaces: LLMAdapter, TemplateRegistry | TypeScript interfaces + Zod | Two `.ts` files with interfaces, types, and JSDoc | 4 |
| 2 | Zod schemas for 7 document types (draft v0.1) | Zod 3.24 | 7 schema files, each with `z.infer` types and `zodToJsonSchema` export | 16 |
| 2 | File-based state management | Zod + fs/promises | `ProjectState` schema, load/save/migrate functions, unit tests | 12 |
| 2 | CLI skeleton with 3 commands | Commander.js 12 | `saas new`, `saas resume`, `saas generate` — stubs that print help | 8 |

**Week 2 Deliverable**: A publishable (but empty) CLI that installs from npm, passes CI, and has a typed schema foundation. Running `saas new` prints a placeholder message. All 7 Zod schemas exist in draft form.

### Phase 1: Core Engine (Weeks 3-8)

#### Feature 1: Conversation Engine (Weeks 3-5) — 3 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 3 | Implement `LLMAdapter` concrete class for Claude | Anthropic SDK, Prompt Caching | `ClaudeLLMAdapter` with `generateStructured()` and `generateStream()`. Unit tests with mock responses. |
| 3 | Design conversation flow state machine | TypeScript enums + state transitions | State machine: `GREETING → INDUSTRY_QA → FEATURE_QA → REVIEW → CONFIRM`. Typed transitions. |
| 4 | Implement multi-turn Q&A with Inquirer.js | Inquirer.js 12, ClaudeLLMAdapter | User answers questions → Claude analyzes → follow-up questions generated. 4-question maximum per round (P4 design rule). |
| 4 | Context management: conversation history + caching | Prompt Caching (`cache_control`) | System prompt cached. Conversation history grows with each turn. Cache hit rate target: >80% on turns 2+. |
| 5 | End-to-end integration: `saas new` triggers full Q&A flow | Commander.js → Inquirer.js → Claude → state.json | Complete conversational flow from `saas new "My SaaS Idea"` to populated state file. Integration tests. |

**Week 5 Deliverable**: `saas new "church management SaaS"` runs an interactive Q&A session, asks intelligent follow-up questions powered by Claude, and saves the conversation + extracted requirements to `state.json`.

#### Feature 2: PRD Generation (Weeks 6-7) — 2 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 6 | PRD prompt engineering + schema refinement | Zod PRD schema, Structured Outputs | Claude generates a complete PRD that validates against Zod schema. 100% schema compliance via Structured Outputs. |
| 6 | PRD Markdown renderer | Template literals, tagged templates | `renderPRD(prdData: PRDSchema): string` produces formatted Markdown. Snapshot tests. |
| 7 | Quality loop: self-critique + revision | Claude multi-turn | Generated PRD is fed back to Claude with "critique this PRD" prompt. Revisions are applied. 1-2 revision cycles. |
| 7 | `saas generate prd` command | Commander.js sub-command | End-to-end: reads state.json → generates PRD → validates → renders → writes `docs/PRD.md`. |

**Week 7 Deliverable**: `saas generate prd` produces a high-quality PRD document based on the conversation data. PRD includes: problem statement, target users, features (MoSCoW prioritized), technical constraints, success metrics.

#### Feature 3: TRD Generation (Week 8) — 1 week

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 8 | TRD prompt engineering + schema | Zod TRD schema, Structured Outputs | Claude generates a TRD that references the PRD. Schema: tech stack, architecture, database schema, API endpoints, deployment strategy. |
| 8 | TRD renderer + cross-reference validation | Renderer + Zod refinements | TRD references PRD sections. Validation ensures PRD features map to TRD components. |

**Week 8 Deliverable (ALPHA)**: Three working commands: `saas new`, `saas generate prd`, `saas generate trd`. A user can go from idea to PRD + TRD. Alpha release to npm `next` tag.

### Phase 2: Document Suite (Weeks 9-14)

#### Feature 4: User Journey + UI Guidelines (Weeks 9-11) — 3 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 9 | User Journey schema + prompt engineering | Zod, Structured Outputs | User Journey document: personas, flows, screens, edge cases. References PRD personas. |
| 10 | UI Guidelines schema + prompt engineering | Zod, Structured Outputs | UI Guidelines: color scheme, typography, component library (shadcn/ui), layout patterns. Generated based on industry + user journey. |
| 11 | Cross-document consistency validation | Zod refinements, custom validators | Automated check: every PRD feature has a User Journey flow; every User Journey screen has UI Guidelines coverage. |

**Week 11 Deliverable**: `saas generate journey` and `saas generate ui` produce cross-referenced documents.

#### Feature 5: Code Guidelines + Information Architecture (Weeks 12-13) — 2 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 12 | Code Guidelines schema + generation | Zod, Structured Outputs | Code Guidelines: project structure, naming conventions, error handling patterns, testing strategy. Based on TRD tech stack. |
| 13 | Information Architecture schema + generation | Zod, Structured Outputs | IA document: navigation structure, URL hierarchy, data relationships, page-component mapping. Based on User Journey flows. |

**Week 13 Deliverable**: Full document suite (6 of 7 documents) generated and cross-referenced.

#### Feature 6: Task List Generation (Week 14) — 1 week

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 14 | Task decomposition from all documents | Zod, Structured Outputs | Task list: epics (from PRD features) → stories (from User Journey) → tasks (from TRD + Code Guidelines). Dependency graph. Estimated hours. |

**Week 14 Deliverable**: `saas generate tasks` produces an implementation-ready task list. All 7 documents complete.

### Phase 3: Code Generation (Weeks 15-20)

#### Feature 7: SaaS Template Scaffolding (Weeks 15-18) — 4 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 15 | Next.js 15 base template + Handlebars integration | Handlebars, TemplateRegistry | Base template: `create-next-app` equivalent with App Router, TypeScript, Tailwind v4, shadcn/ui. Renders from Handlebars templates. |
| 16 | Supabase integration template | Supabase client, Drizzle ORM | Auth (email + OAuth), database schema from TRD, Row Level Security policies. Drizzle schema + migrations. |
| 17 | Stripe integration template | Stripe SDK, webhooks | Checkout Sessions, Customer Portal, webhook handler, subscription management. Pricing page component. |
| 18 | Template assembly + validation | TemplateRegistry, Vitest | `saas generate code` assembles all templates, runs `pnpm install && pnpm build` on the generated project to verify it compiles. |

**Week 18 Deliverable**: `saas generate code` produces a working Next.js 15 SaaS project with auth, database, and payments. The generated project passes `pnpm build`.

#### Feature 8: Project Resume + Polish (Weeks 19-20) — 2 weeks

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 19 | `saas resume` implementation | State management, CLI | Resume a previously started project. Load state, show progress, continue from where user left off. Regenerate individual documents. |
| 20 | Error handling hardening, help text, onboarding UX | Commander.js, Inquirer.js | Graceful error messages, `--help` for all commands, `--verbose` flag, progress indicators. First-run experience. |

### Phase 4: Hardening (Weeks 21-23.5)

| Week | Task | Technology Focus | Deliverable |
|------|------|-----------------|-------------|
| 21 | Integration test suite expansion | Vitest | Full integration tests for all 8 features. Coverage targets met. |
| 22 | E2E testing with real API calls | Vitest + Anthropic SDK | 3 complete user journeys tested end-to-end. Prompt Caching verified. Cost per session measured. |
| 23 | Documentation, README, demo GIF | - | README with quick start, demo GIF, architecture overview. |
| 23.5 | **RELEASE CANDIDATE** | npm `latest` | `saas-auto-builder@1.0.0-rc.1` published to npm. |

### Phase 5: Buffer (Weeks 23.5-26)

| Week | Task | Notes |
|------|------|-------|
| 23.5-26 | Bug fixes, community feedback, edge case handling | 2.5 weeks of buffer. If unused: invest in V2 prep (Ink prototype, multi-framework research). |
| 26 | **v1.0.0 STABLE RELEASE** | Published to npm `latest`. |

### Timeline Summary

```
Week  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
      ├──┤  ├─────────┤  ├──────┤  ├────────────────┤  ├──────────────────┤  ├──────┤  ├──────┤
      Infra  F1:Conv    F2:PRD  F3  F4:Journey+UI     F5:Code+IA  F6:Tasks  F7:Scaffold F8    Harden  Buffer
                               TRD
      ◆ Alpha (W8)                    ◆ Beta (W16)                          ◆ RC (W23.5) ◆ v1.0 (W26)
```

---

## 5. Risk Matrix

### Risk 1: Claude API Behavior Changes (Structured Outputs)

| Attribute | Assessment |
|-----------|-----------|
| **Probability** | 20% (Low-Medium) |
| **Impact** | High — schema compliance is the foundation of the entire document pipeline |
| **Mitigation** | Pin Anthropic SDK version. Comprehensive snapshot tests catch output regressions. Zod validation is a second safety net even if Structured Outputs degrade. The `LLMAdapter` interface enables emergency switch to OpenAI Structured Outputs (which has the same Zod→JSON Schema pattern). |
| **Detection** | Snapshot test failures in CI. E2E test failures in weekly runs. |
| **Recovery time** | 1-2 days (SDK pin or adapter swap) |

### Risk 2: Generated SaaS Template Doesn't Work Out-of-Box

| Attribute | Assessment |
|-----------|-----------|
| **Probability** | 40% (Medium-High) |
| **Impact** | High — this is the core value proposition. A generated project that fails `pnpm build` destroys trust. |
| **Mitigation** | CI job that generates a test project and runs `pnpm install && pnpm build && pnpm test` on every PR. Template components are tested individually. Supabase local dev via Docker for integration testing. Pin all generated dependency versions (no `^` ranges in generated `package.json`). |
| **Detection** | Template validation CI job (automated). Manual testing of generated project every 2 weeks. |
| **Recovery time** | 2-5 days depending on the issue (dependency conflict vs. template logic error) |

### Risk 3: Solo Founder Burnout / Context Switching

| Attribute | Assessment |
|-----------|-----------|
| **Probability** | 30% (Medium) |
| **Impact** | Medium-High — 1-2 weeks of lost productivity pushes into buffer; 3+ weeks jeopardizes the timeline |
| **Mitigation** | 1-week sprints with visible progress. Strict scope per week — no "while I'm here" side quests. 2.5-week buffer is explicitly allocated for this risk. Each feature is independently deployable — partial completion still ships value. |
| **Detection** | Self-monitoring: if a week ends with zero merged PRs, trigger a scope reduction. |
| **Recovery time** | N/A — prevention-focused |

### Risk 4: Prompt Engineering Iteration Takes Longer Than Expected

| Attribute | Assessment |
|-----------|-----------|
| **Probability** | 35% (Medium) |
| **Impact** | Medium — affects Weeks 3-14 (document generation features). Each document type requires 10-30 prompt iterations to achieve quality. |
| **Mitigation** | Start with the simplest document (PRD — most structured, most training data) to establish patterns. Reuse prompt patterns across document types. Prompt Caching reduces iteration cost by 76-90%. Budget 2-3 days of pure prompt engineering per document type. |
| **Detection** | If PRD prompt engineering exceeds 1 week (vs. budgeted 4 days), de-scope the quality loop (self-critique + revision) for later documents. |
| **Recovery time** | Scope reduction — ship documents without self-critique loop, add it in hardening phase |

### Risk 5: Biome + ESLint Two-Tool Friction

| Attribute | Assessment |
|-----------|-----------|
| **Probability** | 25% (Low-Medium) |
| **Impact** | Low — developer experience annoyance, not product-breaking. Rule conflicts or formatting disagreements between Biome and ESLint. |
| **Mitigation** | Clear ownership: Biome owns formatting + standard lint rules. ESLint owns only `no-restricted-imports` and `import/no-cycle`. No overlapping rules. Document in ADR. If friction persists after 2 weeks, drop ESLint entirely and enforce boundaries via code review convention. |
| **Detection** | Developer friction (self-report). CI failures from conflicting rules. |
| **Recovery time** | 2 hours (remove ESLint, accept the 20% rule gap) |

---

## 6. Cost Analysis

### 6.1 API Costs During Development

| Phase | Weeks | Calls/Day | Avg Cost/Call | Cache Savings | Daily Cost | Phase Cost |
|-------|-------|-----------|---------------|---------------|------------|------------|
| Infrastructure (no LLM) | 1-2 | 0 | - | - | $0 | $0 |
| Feature dev (prompt iteration) | 3-14 | 30-50 | $0.08 | 80% (avg) | $0.48-$0.80 | $29-$48 (12 weeks) |
| Code gen templates | 15-18 | 20-30 | $0.12 | 75% | $0.60-$0.90 | $12-$18 (4 weeks) |
| E2E testing | 21-23 | 10-15 | $0.10 | 85% | $0.15-$0.23 | $3-$5 (3 weeks) |
| **Total API development cost** | | | | | | **$44-$71** |

Assumptions: Claude 3.5 Sonnet pricing ($3/MTok input, $15/MTok output). Average prompt: 2K tokens input (system + conversation), 1.5K tokens output. Prompt Caching: 90% discount on cached input tokens.

### 6.2 API Costs Per User Session (Production)

| Metric | Value |
|--------|-------|
| Average conversation turns | 5-8 |
| Average document generations | 7 (full suite) |
| Average code generation | 1 |
| Total API calls per session | 13-16 |
| Cost per call (with caching) | $0.02-$0.05 |
| **Total cost per user session** | **$0.26-$0.80** |
| At $20/month subscription | **67-97% gross margin** |

Note: Users provide their own Anthropic API key in V1 (local CLI tool). The cost above is what the user pays Anthropic directly. SaaS Auto-Builder's revenue model is template/workflow sales, not API markup.

### 6.3 Infrastructure Costs

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| GitHub (public repo) | $0 | Free for OSS |
| GitHub Actions CI | $0 | 2000 min/month free for public repos |
| npm registry | $0 | Free for public packages |
| Domain + DNS | $1-2 | Cloudflare (free plan) + domain renewal |
| Documentation hosting | $0 | GitHub Pages or Vercel free tier |
| Supabase (for development/testing) | $0 | Free tier: 500MB DB, 1GB storage |
| **Total monthly infrastructure** | **$1-2** |

### 6.4 Total 6-Month Development Cost

| Category | Cost |
|----------|------|
| API costs (development) | $44-$71 |
| Infrastructure (6 months) | $6-$12 |
| Domain registration | $10-$15 |
| npm Pro (optional, for private packages during dev) | $0-$42 |
| Tools (Biome, Vitest, etc.) | $0 (all OSS) |
| Hardware/compute | $0 (local development) |
| Coffee | ~$400-$700 |
| **Total (excluding coffee)** | **$60-$140** |
| **Total (including coffee)** | **$460-$840** |

This is one of the lowest-cost technology startups possible. The local-first, CLI-based architecture eliminates hosting costs entirely. OSS tooling eliminates license costs. Prompt Caching eliminates the API cost problem that plagues cloud-based competitors.

---

## 7. V2 Readiness Assessment

### 7.1 Template Marketplace

| Attribute | Assessment |
|-----------|-----------|
| **V1 Preparation** | TemplateRegistry interface + file-based loader |
| **V2 Migration Effort** | 2-3 weeks |
| **What's Needed** | Remote registry (npm-style or custom), template packaging format, version management, community submission flow, revenue sharing infrastructure (Stripe Connect) |
| **Readiness Score** | **8/10** — the hard architectural decision (registry pattern) is already made. Remaining work is distribution infrastructure. |

### 7.2 Multi-Framework

| Attribute | Assessment |
|-----------|-----------|
| **V1 Preparation** | TemplateRegistry supports multiple template sets; Code Guidelines schema includes framework field |
| **V2 Migration Effort** | 3-4 weeks per framework (SvelteKit, Nuxt, Remix) |
| **What's Needed** | New Handlebars template sets per framework. Framework-specific Code Guidelines prompts. Template validation CI for each framework. |
| **Readiness Score** | **7/10** — TemplateRegistry makes adding frameworks a content problem, not an architecture problem. But each framework needs its own prompt engineering and template authoring. |

### 7.3 Web GUI

| Attribute | Assessment |
|-----------|-----------|
| **V1 Preparation** | CLIAdapter abstraction separates prompt logic from CLI rendering |
| **V2 Migration Effort** | 6-8 weeks |
| **What's Needed** | Web app (Next.js), WebSocket server for streaming, authentication, session management, hosted LLM proxy (users can't use their own API keys in a web context). This fundamentally changes the cost model — SaaS Auto-Builder would now pay API costs. |
| **Readiness Score** | **5/10** — the business logic is reusable, but the infrastructure change is substantial. The shift from "user pays API directly" to "we pay API and charge subscription" is a business model change, not just a technical one. |

### 7.4 One-Click Deploy

| Attribute | Assessment |
|-----------|-----------|
| **V1 Preparation** | Generated template includes deployment configs for Vercel (vercel.json) and Railway |
| **V2 Migration Effort** | 2-3 weeks |
| **What's Needed** | CLI integration with Vercel/Railway/Netlify APIs. OAuth flow for platform authentication. Supabase project auto-provisioning. Environment variable setup automation. |
| **Readiness Score** | **6/10** — the generated template is deployment-ready; the missing piece is automating the platform provisioning step. |

### 7.5 Multi-LLM

| Attribute | Assessment |
|-----------|-----------|
| **V1 Preparation** | `LLMAdapter` interface with `generateStructured()` and `generateStream()` |
| **V2 Migration Effort** | 1-2 weeks per model (GPT-4o, Gemini, Llama) |
| **What's Needed** | Concrete adapter implementations. OpenAI and Google both support Structured Outputs with JSON Schema, so Zod schemas are reusable. Prompt adjustments per model. Quality comparison testing. |
| **Readiness Score** | **9/10** — this is the highest-readiness V2 feature. The LLMAdapter interface was designed specifically for this. Zod→JSON Schema works across all major providers. Main work is prompt tuning per model. |

### V2 Readiness Summary

| Feature | Readiness | Migration Weeks | Risk |
|---------|-----------|----------------|------|
| Multi-LLM | 9/10 | 1-2 per model | Low |
| Template Marketplace | 8/10 | 2-3 | Low |
| Multi-Framework | 7/10 | 3-4 per framework | Medium |
| One-Click Deploy | 6/10 | 2-3 | Medium |
| Web GUI | 5/10 | 6-8 | High |

---

## 8. Team Signatures

As a cross-functional assessment of this scenario's feasibility for a solo founder delivering 8 features in 26 weeks:

### Frontend Lead Assessment: **Realistic**

The CLI is not a frontend challenge — Commander.js + Inquirer.js are straightforward. The real frontend work is in the generated SaaS template (Next.js 15 + shadcn/ui + Tailwind v4), which is a well-trodden path with extensive community examples. The Handlebars template authoring is tedious but mechanical. No custom React rendering in V1 (no Ink) eliminates the hardest frontend risk. Risk is low; execution is predictable.

### Backend Lead Assessment: **Realistic**

The "backend" is a Node.js CLI application with file-based state. No database, no server, no authentication, no horizontal scaling concerns. The Anthropic SDK handles the LLM communication complexity. Zod handles validation. The most complex backend concern is state management across sessions (resume functionality), which is a well-understood problem. The generated template's Supabase integration (auth, RLS, Drizzle ORM) is the hardest piece but has excellent documentation and community examples.

### DevOps Lead Assessment: **Realistic**

GitHub Actions CI/CD is standard. npm publishing is standard. No cloud infrastructure to manage (local CLI tool). The only interesting DevOps challenge is the template validation CI job (generating a test project and building it), which is creative but not complex. Total DevOps time: ~2 days of setup, ~1 hour/week of maintenance. Lowest-effort DevOps of any SaaS project imaginable.

### CTO Assessment: **Realistic**

This is the scenario I would greenlight. The technology choices are defensible: every selection has either unanimous consensus (4/4) or strong majority (3/4) from Phase 2 discussions. The two Day-1 interfaces (LLMAdapter, TemplateRegistry) cost 3-4 hours total and buy enormous V2 optionality. The 1-week sprint cadence prevents scope creep. The 2.5-week buffer is appropriate for a solo founder.

The primary concern is Feature 7 (SaaS Template Scaffolding, Weeks 15-18): getting a generated Next.js + Supabase + Stripe project to work out-of-box is the single hardest deliverable. If the project falls behind, this is where it will happen. Mitigation: start with a minimal template (auth + one CRUD entity + basic Stripe checkout) and expand incrementally rather than attempting a full-featured template from day one.

**Overall verdict: Realistic with disciplined execution.**

---

## 9. Why Balanced-Tech Is the Right Choice

### 9.1 What Balanced-Tech Has That Cutting Edge Doesn't: Lower Risk

Cutting Edge would adopt Ink for terminal UI, Effect-TS for error handling, and potentially the Claude Agent SDK for orchestration. Each of these adds 1-2 weeks of learning curve and introduces abstraction layers that provide elegance at the cost of predictability.

Balanced-Tech explicitly rejects these:

| Cutting Edge Choice | Balanced-Tech Choice | Risk Reduction |
|-------------------|---------------------|---------------|
| Ink (React terminal) | Inquirer.js | Eliminates React dependency, JSX compilation, 1-2 week learning curve |
| Effect-TS (functional errors) | Standard try/catch + Result type | Eliminates 2-week learning curve for a novel paradigm |
| Claude Agent SDK | Direct Anthropic SDK | Full control over caching, structured outputs, streaming |
| Full abstraction layers Day 1 | 2 minimal interfaces Day 1 | 3-4 hours vs. 2-3 weeks of architecture work |
| Bun runtime | Node.js 22 LTS | 30 months of guaranteed support vs. moving target |

**Net savings**: ~4-6 weeks of development time redirected from "learning the stack" to "building features."

### 9.2 What Balanced-Tech Has That Proven Stack Doesn't: More Capability

Proven Stack would use ESLint+Prettier (not Biome), raw JSON Schema (not Zod), manual JSON parsing (not Structured Outputs), and Jest (not Vitest). Each of these works. But each leaves capability on the table.

| Proven Stack Choice | Balanced-Tech Choice | Capability Gain |
|-------------------|---------------------|----------------|
| ESLint + Prettier | Biome + minimal ESLint | 56x faster linting, single config for 80% of rules |
| Raw JSON Schema | Zod | Single source of truth: types + validation + LLM schema |
| Manual JSON parsing + retry | Structured Outputs | 100% schema compliance, zero retry logic, zero parse failures |
| Jest | Vitest | 5-10x faster tests, native ESM, zero config |
| npm | pnpm | 3x faster installs, strict dependency resolution |
| `JSON.stringify` rendering | Tagged template literals | Type-safe document rendering with compile-time checks |

**Net gain**: ~2-3 weeks saved from eliminated retry logic, faster iteration cycles, and reduced configuration overhead. This time is reinvested into prompt engineering quality and generated template polish.

### 9.3 The Specific Advantages of Cherry-Picking

The power of Balanced-Tech is that it makes **independent, evidence-based decisions at each layer** rather than committing to a philosophy:

1. **CLI Layer** (Conservative): Commander.js + Inquirer.js — because the CLI is not the product differentiator. Users spend 5 minutes in the CLI and 5 months with the generated output. Don't over-engineer the input layer.

2. **LLM Layer** (Aggressive): Structured Outputs + Prompt Caching — because these provide **unbridgeable advantages**. There is no conservative alternative that achieves 100% schema compliance. There is no older approach that achieves 76-90% cost reduction. These are not "nice to have" — they are the foundation that makes the product economically viable and technically reliable.

3. **Document Pipeline** (Aggressive): Zod as single source of truth — because the alternative (maintaining separate TypeScript types, JSON Schemas, and validation logic) triples the surface area for bugs in the most critical part of the system.

4. **Code Scaffolding** (Conservative): Handlebars + file templates — because template rendering is solved. Sophisticated alternatives (AST manipulation, code generation DSLs) add complexity without proportional quality improvement for V1.

5. **Generated Template** (Mainstream): Next.js 15 + Supabase + Stripe + shadcn/ui — because this is what the target user expects. Deviating from the dominant indie SaaS stack would require justification, and there is none for V1.

6. **Architecture** (Minimal + Intentional): Two interfaces on Day 1, everything else direct — because premature abstraction is more expensive than late abstraction. The Phase 2 data is clear: evolutionary architecture delivers 2-3 more features than Big Bang in 26 weeks.

### 9.4 The Bottom Line

Balanced-Tech is not a compromise. It is the **optimal strategy for a solo founder who needs to ship 8 features in 26 weeks** while maintaining V2 optionality. It uses cutting-edge technology exactly where the data shows an unbridgeable advantage (Structured Outputs, Prompt Caching, Zod), and conservative technology exactly where stability matters more than capability (CLI framework, template engine, state management).

The 87% confidence level reflects this: high enough to commit, low enough to respect the inherent uncertainty of solo founder execution.

**Recommended next step**: Proceed to Phase 4 (Technology Roadmap Final Confirmation) with Balanced-Tech as the selected scenario.

---

## Appendix A: Full Stack Reference Table

| Layer | Technology | Version | Phase 2 Consensus | Risk |
|-------|-----------|---------|-------------------|------|
| Runtime | Node.js | 22 LTS | 4/4 | Low |
| Language | TypeScript | 5.7+ strict | 4/4 | Low |
| CLI Framework | Commander.js | 12 | 4/4 | Low |
| CLI Prompts | Inquirer.js | 12 | 4/4 | Low |
| LLM SDK | Anthropic SDK | 0.52+ | 4/4 | Low |
| LLM Optimization | Prompt Caching | Built-in | 3.5/4 | Low |
| LLM Output | Structured Outputs | Native | 4/4 | Low |
| Schema/Validation | Zod | 3.24+ | 4/4 | Low |
| Template Engine | Handlebars | 4.7 | 3/4 | Low |
| Build | tsup | 8 | 3/4 | Low |
| Package Manager | pnpm | 9 | 3/4 | Low |
| Linting | Biome + ESLint (minimal) | 1.9 + 9 | 3/4 | Medium |
| Testing | Vitest | 3 | 4/4 | Low |
| CI/CD | GitHub Actions | - | 4/4 | Low |
| Pre-commit | lint-staged + husky | 15 + 9 | 3/4 | Low |
| State | File-based JSON | - | 4/4 | Low |
| Generated: Framework | Next.js | 15 | 4/4 | Low |
| Generated: Backend | Supabase | Latest | 4/4 | Low |
| Generated: ORM | Drizzle | Latest | 3/4 | Low |
| Generated: Payments | Stripe | Latest | 4/4 | Low |
| Generated: UI | shadcn/ui + Tailwind CSS | Latest + v4 | 4/4 | Low |
| Generated: Email | Resend | Latest | 3/4 | Low |

## Appendix B: Decision Rationale Quick Reference

| Decision Point | Chosen | Rejected | One-Line Rationale |
|---------------|--------|----------|-------------------|
| Terminal UI | Inquirer.js | Ink | No React dependency for terminal output in V1 |
| Error handling | try/catch + Result | Effect-TS | 2-week learning curve for marginal benefit |
| Agent orchestration | Direct SDK | Claude Agent SDK | Full caching/streaming control needed |
| Formatter | Biome | Prettier | 56x faster, single tool for lint+format |
| Test runner | Vitest | Jest | Native ESM, 5-10x faster, zero config |
| ORM (generated) | Drizzle | Prisma | Lighter runtime, SQL-first for AI predictability |
| Package manager | pnpm | npm/yarn | 3x faster, strict resolution |
| Bundler | tsup | tsc/webpack | esbuild speed, CLI binary support |
| Architecture | Evolutionary | Big Bang | 2-3 more features in 26 weeks |
| Day-1 interfaces | 2 (LLM, Template) | 0 or 5+ | Minimal investment, maximum V2 optionality |
