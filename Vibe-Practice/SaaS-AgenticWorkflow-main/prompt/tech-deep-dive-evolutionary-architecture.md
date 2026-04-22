# SaaS Auto-Builder: Evolutionary Architecture Design Report

**Research Subject**: SaaS Auto-Builder — AI agentic workflow automation system (local CLI via Claude Code)
**Architecture Selection**: Modular Monolith (4/4 consensus from Round 1)
**Date**: 2026-03-12
**Perspective**: Architect who designs systems that evolve over time

---

## 0. Guiding Philosophy

> "Start simple, evolve as needed. Premature optimization is the root of all evil." — Donald Knuth

This report designs a **living architecture** — one that begins as the simplest thing that works and transforms only when real signals (not hypothetical scaling concerns) demand it. The approach is grounded in three precedents:

1. **Shopify**: Started as a monolithic Ruby on Rails app, evolved into a modular monolith serving 30TB/minute during Black Friday. They extracted payment processing and identity into microservices only when specific demands around scale, security, or isolation made it necessary — and these cases were "carefully considered and relatively rare."

2. **Strangler Fig Pattern**: Each evolutionary step is atomic and reversible. You never rewrite; you incrementally replace. The legacy application is the tree, the new architecture is the fig that gradually takes over.

3. **Solo Founder Reality**: The median indie project earns $500/month. Over-engineering kills more startups than under-engineering. "You can spend 3 weeks setting up a perfect monorepo, Docker compose file, and CI/CD pipeline — or you can ship an MVP in 2 days and get your first paying user."

The SaaS Auto-Builder has specific constraints that shape every architectural decision:

- **Local-first**: No cloud database, no server, no containers in V1
- **Solo founder**: Complexity is the enemy; every abstraction must earn its place
- **500K+ token problem**: Full 7-document workflow cannot fit in a single LLM context window
- **7-document SOT chain**: Documents must cross-reference each other with integrity
- **26 weeks total**: 24 productive weeks + 2 weeks buffer — zero room for architectural exploration

---

## 1. Initial MVP Architecture (Month 1-2)

### 1.1 The Simplest Possible Architecture

The Month 1-2 architecture answers one question: **Can a user go from zero to 7 generated documents?**

Everything else — templates, licensing, validation — is noise at this stage.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Entry Point                          │
│                    (bin/sab.ts)                               │
│                                                              │
│  $ sab init          → starts conversation                   │
│  $ sab generate      → runs document pipeline                │
│  $ sab status        → shows project state                   │
└───────────┬──────────────────────────────┬──────────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐   ┌──────────────────────────────┐
│  Conversation Engine  │   │    Document Pipeline          │
│  (core/conversation/) │   │    (core/pipeline/)           │
│                       │   │                               │
│  - Question flow      │   │  SaaSContext                  │
│  - Context extraction │   │    │                          │
│  - Session state      │   │    ├→ PRD Generator           │
│  - Domain detection   │   │    ├→ User Journey Generator  │
│                       │   │    ├→ TRD Generator           │
│  Output:              │   │    ├→ Code Guidelines Gen.    │
│    saas-context.json  │   │    ├→ UI Guidelines Gen.      │
│                       │   │    ├→ IA Generator            │
│                       │   │    └→ Tasks Generator         │
└───────────┬───────────┘   │                               │
            │               │  Output: 7 .md files          │
            └──────────────→│  + pipeline-state.json        │
                            └──────────────────────────────┘
                                         │
                                         ▼
                            ┌──────────────────────────┐
                            │     LLM Adapter           │
                            │     (shared/llm.ts)       │
                            │                           │
                            │  - Single function:       │
                            │    generate(prompt, opts)  │
                            │  - Claude-only in V1      │
                            │  - Streaming support      │
                            │  - Token counting         │
                            │  - Retry with backoff     │
                            └──────────────────────────┘
```

### 1.2 What Is NOT Abstracted Yet

| Component | Month 1-2 Approach | Why No Abstraction |
|-----------|-------------------|-------------------|
| LLM calls | Single `generate()` function, Claude hardcoded | Only one LLM provider. Interface costs 0 extra days but full adapter pattern is premature. |
| Template engine | Does not exist | F3 is Month 3-4 scope |
| Licensing | Does not exist | F6 is Month 3-4 scope |
| Cross-validation | Does not exist | F8 is Month 5-6 scope |
| Context propagation | Does not exist | F4 is Month 3-4 scope |
| State management | Single JSON file on disk | In-memory state is overhead for a CLI tool that runs, generates, and exits |

### 1.3 Module Communication: Direct Function Calls

At this stage, modules communicate through **direct function imports**. No event bus, no message queue, no pub/sub.

```typescript
// bin/sab.ts — the entire orchestration
import { runConversation } from '../core/conversation/index.ts';
import { runPipeline } from '../core/pipeline/index.ts';

const context = await runConversation();       // → saas-context.json
const docs = await runPipeline(context);       // → 7 markdown files
```

This is the right level of coupling for Month 1-2. The conversation engine produces a `SaaSContext` object. The pipeline consumes it. That boundary is the only module boundary that matters.

### 1.4 Data Flow: Conversation → Documents

```
User Input (interactive CLI)
  │
  ▼
┌──────────────────────────────┐
│  Question 1: "What SaaS?"   │──→ Domain detection (e-commerce? marketplace? dashboard?)
│  Question 2: "Target user?" │──→ User persona extraction
│  Question 3: "Core feature?"│──→ Feature set definition
│  Question 4: "Tech stack?"  │──→ Technical constraint capture
│  Question 5: "Revenue?"     │──→ Business model detection
│  Question 6-7: (conditional)│──→ Domain-specific deep-dives
└──────────────┬───────────────┘
               │
               ▼
         saas-context.json    ← SOT for this project
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  Document Pipeline (Sequential)               │
│                                                               │
│  saas-context.json                                            │
│    │                                                          │
│    ├─→ [1] PRD Generator      → outputs/prd.md                │
│    │     │                                                    │
│    │     ├─→ [2] User Journey → outputs/user-journey.md       │
│    │     │                                                    │
│    │     ├─→ [3] TRD          → outputs/trd.md                │
│    │     │     │                                              │
│    │     │     ├─→ [4] Code Guidelines → outputs/code-guide.md│
│    │     │     │                                              │
│    │     │     └─→ [5] UI Guidelines   → outputs/ui-guide.md  │
│    │     │                                                    │
│    │     └─→ [6] Info Architecture → outputs/ia.md            │
│    │                                                          │
│    └─→ [7] Tasks             → outputs/tasks.md               │
│                                                               │
│  Each generator receives: saas-context + all prior documents  │
│  Each generator outputs: markdown + metadata JSON sidecar     │
└──────────────────────────────────────────────────────────────┘
```

### 1.5 Solving the Context Window Problem (Month 1-2)

The full 7-document pipeline exceeds 500K tokens if naively loaded into a single context. The Month 1-2 solution is **sequential generation with selective context loading**:

```
For each document D[i]:
  context_for_llm = {
    saas_context,                    // ~2K tokens (always)
    document_schema[i],              // ~1K tokens (template/format)
    summary_of(D[1..i-1]),           // ~3-5K tokens (compressed summaries)
    full_text(D[i-1]),               // ~5-10K tokens (immediate predecessor)
    relevant_sections(D[1..i-2])     // ~2-5K tokens (cherry-picked cross-refs)
  }
  // Total per call: ~15-25K tokens — well within 200K window
```

This is a **parent-child chunking strategy** applied to document generation: small "child" summaries for broad context, full "parent" text for the immediately relevant predecessor. This approach is validated by current RAG best practices where "the retriever finds the best child chunk, then returns its parent chunk to the LLM, providing rich context for generation."

Each generator produces two files:
- `outputs/prd.md` — full document (human-readable)
- `outputs/.meta/prd.json` — structured metadata (key decisions, entities, cross-reference anchors)

The `.meta/` JSON files are what downstream generators actually consume for cross-referencing — not the full markdown. This keeps context windows manageable while maintaining SOT chain integrity.

### 1.6 Technology Choices (Month 1-2)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | TypeScript | Type safety prevents logic bugs in document pipeline. Solo founder ecosystem: Next.js template (F3) is TypeScript. One language across CLI + template. |
| **Runtime** | Node.js 20+ | Stable LTS. Native `fetch` for API calls. `fs/promises` for file ops. No external dependencies for core I/O. |
| **CLI Framework** | `commander` + `inquirer` | Mature, minimal, zero-config. Handles interactive Q&A (conversation engine) and command routing. ~50KB total. |
| **LLM Client** | Anthropic SDK (`@anthropic-ai/sdk`) | Direct SDK, no LangChain. LangChain abstractions add complexity with no value when supporting one provider. |
| **State Storage** | JSON files on disk | `saas-context.json` for conversation state. `pipeline-state.json` for generation progress. `outputs/.meta/*.json` for document metadata. No database. No SQLite. Files are inspectable, diffable, debuggable. |
| **Build** | `tsup` (esbuild-based) | Fast, zero-config TypeScript bundling. Produces a single `dist/` for `npm install -g`. |
| **Package Manager** | `pnpm` | Fast, disk-efficient. Strict by default (prevents phantom dependencies). |
| **Testing** | `vitest` | Fast, TypeScript-native, compatible with Node.js test runner patterns. |
| **Linting** | `biome` | Replaces ESLint + Prettier with a single, fast tool. Zero-config for TypeScript. |

### 1.7 File Structure (Month 1-2 Reality)

```
saas-auto-builder/
├── package.json
├── tsconfig.json
├── bin/
│   └── sab.ts                      ← CLI entry point
├── src/
│   ├── core/
│   │   ├── conversation/
│   │   │   ├── index.ts             ← runConversation()
│   │   │   ├── questions.ts         ← Question definitions + branching logic
│   │   │   ├── context-builder.ts   ← Builds SaaSContext from answers
│   │   │   └── domain-detector.ts   ← Detects SaaS domain (e-commerce, etc.)
│   │   └── pipeline/
│   │       ├── index.ts             ← runPipeline() — sequential orchestrator
│   │       ├── generator.ts         ← Base generator: prompt assembly + LLM call
│   │       └── summarizer.ts        ← Compresses prior docs for context window
│   ├── generators/
│   │   ├── prd.ts                   ← PRD prompt template + post-processing
│   │   ├── user-journey.ts
│   │   ├── trd.ts
│   │   ├── code-guidelines.ts
│   │   ├── ui-guidelines.ts
│   │   ├── information-architecture.ts
│   │   └── tasks.ts
│   ├── shared/
│   │   ├── llm.ts                   ← generate() function — Claude API wrapper
│   │   ├── types.ts                 ← SaaSContext, GeneratorInput, GeneratorOutput
│   │   ├── config.ts                ← API key loading, user prefs
│   │   └── fs-utils.ts              ← Atomic file writes, path helpers
│   └── __tests__/
│       ├── conversation.test.ts
│       ├── pipeline.test.ts
│       └── generators/
│           └── prd.test.ts          ← At least PRD generator tested
├── dist/                            ← Build output (gitignored)
└── .github/
    └── workflows/
        └── ci.yml                   ← Lint + type-check + test
```

**Total file count**: ~25 files. **Lines of code estimate**: ~2,500-3,500 (excluding tests).

This is a flat, scannable structure. No `interfaces/`, no `abstractions/`, no `factories/`. Every file does one thing and is findable by name.

---

## 2. Growth Phase Architecture (Month 3-4)

### 2.1 What Changes and Why

Month 3-4 introduces F3 (Template), F4 (Context Propagation), F5 (Editable Docs), and F6 (Licensing). Each addition creates a specific architectural pressure:

| Feature | Architectural Pressure | Response |
|---------|----------------------|----------|
| F3: Template | Code generation is fundamentally different from document generation. Templates need a rendering engine, variable substitution, file scaffolding. | Extract `templates/` as a separate module with its own pipeline. |
| F4: Context Propagation | Documents now have explicit dependency edges. Changing PRD must cascade to TRD, Code Guidelines, Tasks. | Add a dependency graph to `pipeline-state.json`. Forward-propagation-only in V1. |
| F5: Editable Docs | Users can modify generated documents and re-trigger downstream regeneration. | Pipeline must support partial re-runs from any document node. |
| F6: Licensing | Feature gating requires a cross-cutting concern (checking license before premium operations). | Simple middleware pattern — a `checkLicense()` guard before premium functions. |

### 2.2 Evolved Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI Layer (thin)                             │
│  $ sab init / generate / edit <doc> / template / status / license   │
└────────┬────────────────┬──────────────┬────────────────┬───────────┘
         │                │              │                │
         ▼                ▼              ▼                ▼
┌──────────────┐ ┌────────────────┐ ┌──────────┐ ┌───────────────┐
│ Conversation │ │   Document     │ │ Template │ │   License     │
│ Engine       │ │   Pipeline     │ │ Engine   │ │   Manager     │
│              │ │                │ │          │ │               │
│ (unchanged)  │ │ + Dep Graph    │ │ NEW      │ │ NEW           │
│              │ │ + Partial      │ │          │ │               │
│              │ │   Re-run       │ │ render() │ │ check()       │
│              │ │ + Forward      │ │ scaffold │ │ activate()    │
│              │ │   Propagation  │ │ validate │ │ projectCount()│
└──────┬───────┘ └───────┬────────┘ └────┬─────┘ └───────────────┘
       │                 │               │
       │         ┌───────┴───────┐       │
       │         │               │       │
       ▼         ▼               ▼       ▼
  ┌──────────────────────────────────────────────┐
  │              Shared Layer                      │
  │                                                │
  │  llm.ts → LLMAdapter interface (Month 3)       │
  │  types.ts → + TemplateContext, LicenseState     │
  │  config.ts → + license key storage              │
  │  fs-utils.ts → + atomic directory scaffolding   │
  │  dep-graph.ts → NEW: document dependency edges  │
  └────────────────────────────────────────────────┘
```

### 2.3 The LLM Adapter Abstraction (Month 3)

In Month 1-2, `llm.ts` is a single function wrapping the Anthropic SDK. In Month 3, we extract an interface — not because we need multiple providers, but because the Template Engine needs different LLM call patterns (code generation vs document generation):

```typescript
// shared/llm.ts — Month 3 evolution

interface LLMAdapter {
  generate(prompt: string, options: GenerateOptions): Promise<string>;
  generateStreaming(prompt: string, options: GenerateOptions): AsyncIterable<string>;
  countTokens(text: string): number;
}

interface GenerateOptions {
  maxTokens: number;
  temperature: number;       // 0.3 for documents, 0.1 for code
  systemPrompt?: string;
  stopSequences?: string[];
}

// V1: Only ClaudeAdapter exists
class ClaudeAdapter implements LLMAdapter { ... }

// V2: GPTAdapter, GeminiAdapter would implement the same interface
```

The trigger for this extraction is **not** "we might need GPT someday." The trigger is: **document generation and code generation require different LLM call configurations**, and a single `generate()` function is becoming a bag of conditional parameters.

### 2.4 Document Dependency Graph (F4 Implementation)

Forward-propagation-only means a directed acyclic graph (DAG):

```
saas-context.json
  │
  ├──→ PRD ──┬──→ User Journey
  │          ├──→ TRD ──┬──→ Code Guidelines
  │          │          └──→ UI Guidelines
  │          └──→ Information Architecture
  │
  └──→ Tasks (depends on: PRD + TRD)
```

Implementation: a simple adjacency list in `pipeline-state.json`:

```json
{
  "dependencies": {
    "prd": ["saas-context"],
    "user-journey": ["saas-context", "prd"],
    "trd": ["saas-context", "prd"],
    "code-guidelines": ["saas-context", "prd", "trd"],
    "ui-guidelines": ["saas-context", "prd", "trd"],
    "information-architecture": ["saas-context", "prd"],
    "tasks": ["saas-context", "prd", "trd"]
  },
  "lastGenerated": {
    "prd": "2026-04-15T10:30:00Z",
    "trd": "2026-04-15T10:32:00Z"
  },
  "dirty": ["code-guidelines", "ui-guidelines"]
}
```

When a user edits `prd.md` (F5), the system marks all downstream dependents as "dirty" and offers to regenerate:

```
$ sab edit prd
[Editor opens prd.md]
[User saves changes]

Detected changes in PRD. The following documents depend on PRD:
  - TRD (generated 2h ago)
  - User Journey (generated 2h ago)
  - Code Guidelines (generated 2h ago, depends via TRD)
  - UI Guidelines (generated 2h ago, depends via TRD)
  - Tasks (generated 2h ago)

Regenerate affected documents? [all / select / skip]
```

This is **not** bidirectional propagation. Changes flow downward only. If TRD has inconsistencies with PRD, the user must edit PRD and regenerate. Bidirectional (detecting TRD contradictions and suggesting PRD fixes) is V2 scope, per Tech perspective agreement.

### 2.5 Template Engine (F3 Architecture)

The template engine is the first module that justifies a **registry pattern** because V2 plans a marketplace:

```
templates/
├── registry.ts               ← Template discovery + metadata
├── engine.ts                  ← Variable substitution + file scaffolding
├── validator.ts               ← Validates generated code (lint, type-check)
└── nextjs-supabase-stripe/    ← V1: the only template
    ├── template.json          ← Metadata: name, variables, files
    ├── scaffolds/             ← File templates with {{ variable }} placeholders
    │   ├── app/
    │   ├── lib/
    │   ├── components/
    │   └── ...
    └── tests/                 ← Template self-tests (run after scaffolding)
```

The registry scans `templates/*/template.json` on startup. V1 finds one template. V2 marketplace adds a `RemoteRegistry` that fetches from a URL. The `engine.ts` rendering pipeline is unchanged — it only sees a `Template` object regardless of source.

### 2.6 Performance Considerations at ~100 Users

At 100 users, performance bottlenecks are **not** server-side (there is no server). They manifest as:

| Bottleneck | Symptom | Solution |
|-----------|---------|----------|
| LLM API latency | 7 sequential document generations take 5-10 minutes total | Parallelism where dependencies allow: PRD first, then User Journey + TRD + IA in parallel, then Code Guidelines + UI Guidelines + Tasks in parallel. Reduces to ~3-4 minutes. |
| Token cost per user | ~50K-80K tokens per full pipeline run ($1-4 at Claude pricing) | BYOK model means this is the user's cost. Optimization: cache document summaries to avoid re-summarizing unchanged documents. |
| Disk I/O | Negligible | Local SSD. No concern at any realistic scale. |
| npm install size | Package size with templates could exceed 50MB | Ship templates as lazy downloads (first-run fetches from GitHub releases, not bundled). |

The architectural response in Month 3-4 is introducing **parallel generation** where the DAG permits:

```
Phase 1: [PRD]                          ← sequential (no dependencies)
Phase 2: [User Journey] [TRD] [IA]     ← parallel (all depend only on PRD)
Phase 3: [Code Guide] [UI Guide]        ← parallel (depend on PRD + TRD)
Phase 4: [Tasks]                         ← sequential (depends on PRD + TRD)
```

This cuts wall-clock time by ~40% with zero architecture changes beyond `Promise.all()` in the pipeline orchestrator.

---

## 3. Maturity Phase Architecture (Month 5-6+)

### 3.1 Month 5-6: Cross-Validation Engine (F8)

The cross-validation engine is the first module that benefits from a **plugin architecture**:

```
core/
└── cross-validation/
    ├── engine.ts              ← Rule runner: loads validators, executes, reports
    ├── types.ts               ← ValidationRule, ValidationResult, Severity
    └── rules/
        ├── prd-trd-coverage.ts       ← Does TRD address all PRD features?
        ├── trd-tasks-coverage.ts     ← Do Tasks cover all TRD requirements?
        ├── ui-ia-consistency.ts      ← Are UI Guidelines aligned with IA?
        ├── code-guide-trd-sync.ts    ← Do Code Guidelines match TRD decisions?
        └── index.ts                  ← Exports all rules (V2: dynamic loading)
```

Each rule is a pure function:

```typescript
interface ValidationRule {
  id: string;
  name: string;
  description: string;
  documents: [string, string];  // pair of documents to cross-validate
  validate(docA: Document, docB: Document): ValidationResult[];
}

interface ValidationResult {
  ruleId: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  locationA?: { document: string; section: string; line?: number };
  locationB?: { document: string; section: string; line?: number };
  suggestion?: string;
}
```

V1 ships with 4-5 basic rules. V2 adds pluggable validators loaded from user-defined rule files. The engine is a simple `for (const rule of rules) { results.push(...rule.validate(docA, docB)); }` loop.

### 3.2 V2 Web GUI — The Biggest Architectural Evolution

If CLI adoption is below 500 users at Month 6, the V2 Web GUI becomes critical. The Month 1-6 architecture prepares for this by enforcing one absolute rule:

> **Zero business logic in the CLI layer.**

The CLI is a thin adapter that:
1. Reads user input (via `inquirer`)
2. Calls domain functions (from `core/`)
3. Displays output (formatted markdown/JSON)

A Web GUI would:
1. Read user input (via HTML forms/chat interface)
2. Call the **same** domain functions (from `core/`)
3. Display output (rendered in browser)

```
Month 1-6 Architecture:

  CLI (bin/sab.ts)
       │
       └──→ core/* + generators/* + templates/* + shared/*

Month 9-12 Architecture (if Web GUI needed):

  CLI (bin/sab.ts)         Web (web/server.ts)
       │                        │
       └────────┬───────────────┘
                │
                ▼
  core/* + generators/* + templates/* + shared/*
```

The migration cost is **building the web layer only** — not refactoring any business logic. This is the Shopify lesson: "the modular monolith kept all domain logic in one place, allowing different presentation layers to consume it."

Potential web stack for V2:
- **Hono** or **Fastify** for API server (lightweight, TypeScript-native)
- **htmx** + server-rendered templates for UI (minimal JS, progressive enhancement)
- Or **Tauri** for desktop app (reuses web UI, runs locally, no Electron bloat)

### 3.3 Template Marketplace — Registry Evolution

```
V1 Registry (Month 3-4):
  LocalRegistry → scans templates/ directory → returns Template[]

V2 Registry (Month 7-8):
  RegistryInterface
    ├── LocalRegistry   → scans templates/ directory
    └── RemoteRegistry  → fetches from marketplace API
                           → caches locally
                           → validates signatures
                           → handles payment (Stripe Connect)
```

The Strangler Fig in action: `LocalRegistry` is never rewritten. `RemoteRegistry` is added alongside it. The pipeline calls `registry.getTemplate(name)` and does not know or care whether the template is local or remote.

### 3.4 Multi-LLM Support — Adapter Evolution

```
V1 (Month 1-6):
  LLMAdapter
    └── ClaudeAdapter

V2 (Month 11-12):
  LLMAdapter
    ├── ClaudeAdapter
    ├── GPTAdapter
    └── GeminiAdapter

  + QualityNormalizer
    → Runs the same prompt through multiple providers
    → Scores output quality (via a judge LLM or heuristic)
    → Selects best output
    → Falls back on provider failure
```

The key insight: Multi-LLM is **not** about "swap Claude for GPT." It is about **quality normalization** — different LLMs produce different output styles, and the document pipeline expects a specific structure. The `QualityNormalizer` is the actual engineering challenge, not the adapter pattern.

### 3.5 Event System — When Does It Become Necessary?

In V1 (Month 1-6), there is no event system. Module calls are direct:

```typescript
// V1: Direct call
const prd = await generatePRD(context);
const trd = await generateTRD(context, prd);
```

An event system becomes necessary when:

1. **Multiple consumers need to react to a single event** — e.g., "document generated" triggers both cross-validation AND template regeneration AND progress tracking AND analytics.
2. **Long-running operations need progress reporting** — e.g., streaming generation progress to a Web GUI.
3. **Plugins/extensions need hook points** — e.g., community-built validators that run after each document generation.

**Estimated trigger point**: Month 9-10, when Web GUI and template marketplace create multiple consumers.

V2 event system (simple, not Kafka):

```typescript
// shared/events.ts
type EventType = 'document:generated' | 'document:edited' | 'validation:complete' | 'template:rendered';

class EventBus {
  private listeners = new Map<EventType, Function[]>();

  on(event: EventType, handler: Function): void { ... }
  emit(event: EventType, data: unknown): void { ... }
}

// Single instance, injected where needed
export const events = new EventBus();
```

This is an in-process event bus — not a message queue, not Redis pub/sub. For a local CLI tool, even at V2 scale, an in-process event bus handles all coordination needs.

---

## 4. Evolution Cost Analysis

### 4.1 Development Cost by Phase

| Phase | Productive Weeks | Architecture Overhead | Net Feature Work | Approach |
|-------|-----------------|----------------------|-------------------|----------|
| Month 1-2 (MVP) | 7 weeks | ~0.5 weeks (project setup, CI) | 6.5 weeks | Simplest thing that works |
| Month 3-4 (Growth) | 9 weeks | ~1.5 weeks (LLM adapter interface, dep graph, template registry) | 7.5 weeks | Extract boundaries where real pressure exists |
| Month 5-6 (Maturity) | 5 weeks + 3 weeks buffer | ~1 week (validation plugin system) | 4 weeks + buffer | Polish, harden, prepare V2 seams |
| **Total V1** | **24 weeks** | **~3 weeks** | **~18 weeks** | |

Architecture overhead is **12.5%** of total development time. The remaining 87.5% is feature work.

### 4.2 Refactoring Cost at Each Phase Transition

| Transition | What Changes | Estimated Cost | Risk |
|-----------|-------------|----------------|------|
| Month 2 → Month 3 | `generate()` function → `LLMAdapter` interface. Add `dep-graph.ts`. | 2-3 days | Low — straightforward interface extraction |
| Month 4 → Month 5 | Add cross-validation plugin system. Parallel pipeline execution. | 3-4 days | Low — additive, not destructive |
| Month 6 → Month 9 (V2 GUI) | Add web server layer. Expose domain functions as API. | 2-3 weeks | Medium — new deployment mode, but zero domain changes |
| Month 6 → Month 7 (V2 Marketplace) | Add `RemoteRegistry` alongside `LocalRegistry`. | 1-2 weeks | Low — additive |
| Month 6 → Month 11 (V2 Multi-LLM) | Implement new adapters + quality normalizer. | 2-3 weeks | Medium — quality normalization is non-trivial |

### 4.3 Evolutionary vs Big Bang Comparison

| Dimension | Evolutionary (This Plan) | Big Bang (Build Full Architecture Day 1) |
|-----------|------------------------|---------------------------------------|
| Month 1 productive output | Working conversation engine + 2-3 generators | Configuration files, interfaces, adapters, no user-facing features |
| Month 2 productive output | Full 7-doc pipeline, private alpha | Possibly first generator working, still building infrastructure |
| Time to first user feedback | Week 6-8 | Week 12-16 |
| Total architecture time (6 months) | ~3 weeks (12.5%) | ~6-8 weeks (25-33%) |
| Tech debt at Month 6 | Moderate — known, localized | Low — but features are fewer |
| Risk of unused abstractions | Near zero (only build what's needed) | High (built for scenarios that may never happen) |
| Ability to pivot | High (minimal sunk cost in architecture) | Low (significant investment in specific architecture) |
| **Net feature output at Month 6** | **8 features shipped** | **5-6 features shipped** |

The evolutionary approach delivers **2-3 more features** in the same timeframe by deferring architecture work until real signals demand it.

### 4.4 When Does "Evolutionary" Become "Spaghetti"?

The risk of spaghetti code in evolutionary architecture is real. Here are the specific guardrails:

**Hard Rules (enforce from Day 1)**:
1. **Each module has exactly one public entry point** (`index.ts` exports). Internal files are never imported from outside.
2. **Shared state is always in files on disk, never in module-level variables.** A CLI tool starts, runs, and exits. There is no persistent process state.
3. **Every function that calls the LLM goes through `shared/llm.ts`**. No direct Anthropic SDK usage in feature code.
4. **Module dependencies are one-directional**: `cli/` → `core/` → `generators/` → `shared/`. Never upward.

**Spaghetti Warning Signs** (monitor weekly):
- A single file exceeds 400 lines → split it
- A module imports from more than 3 other modules → dependency is too broad
- A change in `generators/` requires a change in `cli/` → coupling leak
- `shared/types.ts` exceeds 200 lines → types are becoming a god object

**Circuit Breaker**: If at any milestone review, more than 30% of development time was spent on "fixing interactions between modules" rather than "building features," stop and invest one week in boundary clarification.

---

## 5. Specific Design Decisions

### 5.1 File-Based State vs In-Memory State

**Decision: File-based state for everything.**

Rationale:
- A CLI tool has no long-running process. It starts, does work, exits. In-memory state dies with the process.
- File-based state is inspectable: `cat saas-context.json` shows exactly what the system knows.
- File-based state is debuggable: when document generation goes wrong, the developer can inspect every intermediate state file.
- File-based state survives crashes: if generation fails at document 5, the first 4 are already on disk. The user runs `sab generate --resume` and picks up where it left off.
- File-based state enables `sab edit`: the user opens `outputs/prd.md` in any editor, saves it, and `sab propagate` picks up the changes.

State files:

```
my-saas-project/
├── .sab/
│   ├── saas-context.json       ← SOT: conversation output
│   ├── pipeline-state.json     ← Generation progress, dep graph, dirty flags
│   ├── license.json            ← License key + tier (encrypted at rest)
│   └── meta/
│       ├── prd.json            ← PRD metadata (cross-ref anchors, key decisions)
│       ├── trd.json
│       └── ...
├── outputs/
│   ├── prd.md
│   ├── user-journey.md
│   ├── trd.md
│   ├── code-guidelines.md
│   ├── ui-guidelines.md
│   ├── information-architecture.md
│   └── tasks.md
└── generated/                  ← F3: scaffolded code (when template is applied)
    └── nextjs-app/
        ├── package.json
        ├── app/
        └── ...
```

The `.sab/` directory is the project's internal state. `outputs/` is the human-facing document output. `generated/` is the code output. Clear separation.

### 5.2 SOT Chain Between Documents

The SOT chain is implemented through **cross-reference anchors** — structured identifiers embedded in document metadata:

```json
// .sab/meta/prd.json
{
  "version": "1.0.0",
  "generatedAt": "2026-04-15T10:30:00Z",
  "anchors": {
    "features": [
      { "id": "F-001", "name": "User Authentication", "section": "3.1" },
      { "id": "F-002", "name": "Payment Processing", "section": "3.2" },
      { "id": "F-003", "name": "Dashboard", "section": "3.3" }
    ],
    "userTypes": [
      { "id": "U-001", "name": "Admin", "section": "2.1" },
      { "id": "U-002", "name": "Customer", "section": "2.2" }
    ],
    "decisions": [
      { "id": "D-001", "text": "Use Supabase for auth + DB", "section": "4.1" }
    ]
  }
}

// .sab/meta/trd.json
{
  "version": "1.0.0",
  "generatedAt": "2026-04-15T10:32:00Z",
  "references": {
    "prd": {
      "version": "1.0.0",
      "anchorsUsed": ["F-001", "F-002", "F-003", "D-001"]
    }
  },
  "anchors": {
    "components": [
      { "id": "C-001", "name": "AuthModule", "implementsFeature": "F-001" },
      { "id": "C-002", "name": "PaymentService", "implementsFeature": "F-002" }
    ],
    "apis": [
      { "id": "A-001", "name": "/api/auth/*", "component": "C-001" }
    ]
  }
}
```

Cross-validation (F8) then checks: "Does every `F-xxx` in PRD have at least one `implementsFeature: F-xxx` in TRD?" This is deterministic, not LLM-based. Pure JSON traversal.

### 5.3 LLM Call Orchestration: Sequential → Parallel

Month 1-2: **Sequential** (simplest)
```
PRD → User Journey → TRD → Code Guidelines → UI Guidelines → IA → Tasks
Total: 7 sequential LLM calls (~7-10 minutes)
```

Month 3+: **DAG-Parallel** (optimized)
```
Phase 1: PRD                                    (~60-90s)
Phase 2: [User Journey | TRD | IA] in parallel  (~60-90s)
Phase 3: [Code Guidelines | UI Guidelines]       (~60-90s)
Phase 4: Tasks                                   (~60-90s)
Total: 4 phases (~4-6 minutes, ~40% improvement)
```

Implementation is a simple topological sort of the dependency graph + `Promise.all()` for nodes at the same depth level. No complex scheduler needed.

### 5.4 Error Recovery: Mid-Pipeline Failure

When document generation fails at document 5 (UI Guidelines):

```
pipeline-state.json:
{
  "status": "failed",
  "completedSteps": ["prd", "user-journey", "trd", "code-guidelines"],
  "failedStep": "ui-guidelines",
  "error": { "type": "LLM_API_ERROR", "message": "Rate limit exceeded", "retryable": true },
  "resumable": true
}
```

Recovery:
```
$ sab generate --resume
Resuming pipeline from: ui-guidelines
Previous documents loaded from cache.
Generating UI Guidelines... ✓
Generating Information Architecture... ✓
Generating Tasks... ✓
Pipeline complete. 7/7 documents generated.
```

The pipeline orchestrator checks `pipeline-state.json` on startup. If `resumable: true`, it skips completed steps and retries from the failed step. Completed documents are already on disk — no regeneration needed.

For non-retryable errors (e.g., malformed LLM output that fails schema validation), the system offers:
```
$ sab generate --resume --retry-step ui-guidelines
Retrying UI Guidelines generation with fresh context...
```

### 5.5 Reusing Existing AgenticWorkflow Infrastructure

The parent AgenticWorkflow codebase contains significant infrastructure that the child SaaS Auto-Builder can inherit:

| AgenticWorkflow Component | Reuse in SaaS Auto-Builder | Estimated Savings |
|--------------------------|---------------------------|-------------------|
| `_context_lib.py` — Transcript parsing, token estimation, atomic file writes | Port the atomic file write pattern and token counting to TypeScript. The token estimation logic (2.5 chars/token for mixed content) is directly applicable. | 1-2 days |
| `query_workflow.py` — SOT schema validation, pACS score extraction | The SOT validation pattern (validate before any query) applies directly to `pipeline-state.json` validation. | 1 day |
| `output_secret_filter.py` — 25+ pattern secret detection | Port as a pre-publish hook: before outputting generated code, scan for accidentally embedded secrets (API keys in templates, etc.). | 1-2 days |
| `block_destructive_commands.py` — Dangerous command blocking | Relevant when the template engine executes `npm install` or `npx create-next-app`. Block `rm -rf /`, `sudo`, network exfiltration. | 0.5 days |
| Context Preservation pattern (save/restore) | The `saas-context.json` + `pipeline-state.json` file-based state model is a direct descendant of AgenticWorkflow's context snapshot pattern. | Architectural pattern (no code port, but design savings ~1 week) |
| 4-layer quality gates (L0→L1→L1.5→L2) | Map to document pipeline: L0 = schema validation (does output match expected JSON structure), L1 = completeness check (does PRD cover all conversation topics), L1.5 = self-rating (LLM rates its own output quality), L2 = cross-validation (F8). | Design pattern savings ~3-5 days |
| SOT single-writer principle | Directly inherited: only the pipeline orchestrator writes to `pipeline-state.json`. Generators write to their own output files only. | Architectural principle (no code) |
| **Estimated total savings** | | **2.5-4 weeks** |

This validates the Round 1 estimate of "7-11 weeks savings from existing infrastructure" — the conservative end (~4 weeks of direct savings) plus indirect design pattern benefits.

**DNA Inheritance**: Per `soul.md`, the SaaS Auto-Builder inherits the parent's full genome. Specifically:
- **Absolute Standard 1 (Quality)**: Document quality > generation speed. Always.
- **Absolute Standard 2 (SOT)**: `saas-context.json` is the single source of truth. Pipeline orchestrator is the single writer.
- **Absolute Standard 3 (CCP)**: Before modifying any generator prompt, analyze impact on all downstream documents.
- **4-Layer Quality Gates**: Mapped to L0 (JSON schema), L1 (completeness), L1.5 (self-rating), L2 (cross-validation).

---

## 6. Conclusion

### Is the Evolutionary Approach Right for Us?

**YES — with high confidence.**

The reasoning chain:

1. **Solo founder** — every hour spent on premature abstraction is an hour not spent on features that users evaluate. The evolutionary approach maximizes feature output per unit time.

2. **Unknown product-market fit** — the product may pivot (from full pipeline to PRD-only, from CLI to GUI, from developer tool to consulting accelerator). Evolutionary architecture minimizes sunk cost in any particular architectural direction.

3. **Local-first CLI** — there is no scaling crisis to prevent. The tool runs on the user's machine. Architectural scaling concerns (load balancing, database sharding, service discovery) literally do not apply.

4. **Proven by precedent** — Shopify's modular monolith serves millions of merchants and 30TB/minute. Our tool serves one user at a time on their local machine. If Shopify can scale a modular monolith to that level, our tool will never outgrow it.

5. **Clear evolution triggers** — we know exactly when to evolve (see below), so the risk of premature or delayed evolution is minimized.

### First 6 Months Development Time

| Phase | Duration | Key Output |
|-------|----------|-----------|
| Month 1-2 | 8 weeks (7 productive + 1 buffer) | Conversation engine + 7-doc pipeline + private alpha |
| Month 3-4 | 10 weeks (9 productive + 1 buffer) | Template + context propagation + editing + licensing + public beta |
| Month 5-6 | 8 weeks (5 productive + 3 buffer/polish) | Cross-validation + quality hardening + Pro launch |
| **Total** | **26 weeks** | **8 features, production-ready** |

### Expected Tech Debt

| Category | Severity | Location | Payoff Timeline |
|----------|----------|----------|----------------|
| Forward-propagation-only (no bidirectional) | Medium | `core/pipeline/dep-graph.ts` | V2 Month 7 |
| Single LLM provider (no quality normalization) | Low | `shared/llm.ts` | V2 Month 11-12 |
| No event system (direct function calls) | Low | Throughout `core/` | V2 Month 9-10 |
| Simple license check (no DRM, no server validation) | Low | `licensing/` | V2 or never (BYOK means DRM is low-value) |
| No i18n in CLI prompts | Low | `bin/sab.ts`, `core/conversation/` | V2 if international demand emerges |
| Templates bundled locally (no lazy download) | Low | `templates/` | V2 Month 7-8 with marketplace |

**Characterization**: This tech debt is **strategic** — each item is a conscious decision to defer complexity until a real signal demands it. None of it is "accidental complexity" from poor engineering. Every item has a known payoff timeline and a known trigger for resolution.

### Key Evolution Trigger Points

These are the signals that tell us to evolve — not dates on a calendar, but observable conditions:

| Signal | What It Means | Architectural Response |
|--------|--------------|----------------------|
| Template engine needs code generation with different LLM configs than doc generation | `generate()` function has too many conditional parameters | Extract `LLMAdapter` interface (Month 3) |
| User edits a document and asks "what else changed?" | Forward-propagation insufficient | Begin bidirectional propagation R&D (V2) |
| Multiple validation rules have copy-pasted setup code | Rule registration is ad-hoc | Extract validation plugin system (Month 5) |
| CLI adoption < 500 users at Month 6 | CLI is too niche | Begin Web GUI layer (V2 Month 9) |
| Community members ask to submit templates | Template marketplace has demand | Add `RemoteRegistry` (V2 Month 7) |
| Anthropic pricing increases > 50% OR Claude Code shows deprecation signs | Single-provider dependency is existential risk | Implement Multi-LLM adapters (V2 Month 11) |
| Document generation event needs to trigger 3+ different actions | Direct function calls create coupling | Add in-process event bus (V2 Month 9) |
| A single source file exceeds 400 lines | Module is doing too much | Split into smaller focused files (immediately) |
| > 30% of dev time spent on inter-module debugging | Boundaries are leaking | Stop feature work, invest 1 week in boundary clarification |

### Final Architecture Evolution Timeline (Visual)

```
Month:  1     2     3     4     5     6     7     8     9    10    11    12
        ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
        │           │           │           │                               │
        │  MVP      │  Growth   │ Maturity  │         V2 Evolution          │
        │           │           │           │                               │
Core:   │ [Conv] [Pipeline───] │           │                               │
        │ Direct fn calls      │           │                               │
        │           │           │           │                               │
Adapt:  │ generate()│→ LLMAdapter interface │           │→ Multi-LLM       │
        │           │           │           │                               │
Data:   │ JSON files│→ + Dep Graph         │           │→ + Event Bus      │
        │           │→ + Meta anchors      │           │                   │
        │           │           │           │                               │
F3:     │           │ [Template Engine─────]│           │→ Marketplace      │
        │           │ LocalRegistry         │           │  + RemoteRegistry │
        │           │           │           │                               │
F4:     │           │ [Forward Propagation─]│           │→ Bidirectional    │
        │           │           │           │                               │
F8:     │           │           │ [Cross-Validation────]│→ Plugin System    │
        │           │           │           │                               │
CLI:    │ [Thin CLI layer──────────────────]│           │                   │
GUI:    │           │           │           │           │→ [Web GUI?]       │
        │           │           │           │                               │
Debt:   │ None      │ Low       │ Moderate  │ Payoff begins                 │
        ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
```

The architecture starts as ~25 files with direct function calls and grows organically into a modular monolith with clear boundaries, an adapter layer, a dependency graph, and a plugin system — all driven by real user signals, not speculative planning.

This is how software that survives gets built.

---

## Sources

- [Shopify: Deconstructing the Monolith](https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity)
- [Is the Modular Monolith Shopify's Best-kept Secret to Scaling?](https://www.educative.io/newsletter/system-design/shopify)
- [How Shopify Handles 30TB of Data Every Minute with a Monolithic Architecture](https://newsletter.systemdesign.one/p/modular-monolith)
- [Evolutionary Architecture by Example (GitHub)](https://github.com/evolutionary-architecture/evolutionary-architecture-by-example)
- [The Death of Microservices Hype: When Modular Monoliths Win](https://www.javacodegeeks.com/2026/02/the-death-of-microservices-hype-when-modular-monoliths-win.html)
- [Why Monolithic Architecture Reigns Supreme for New Projects in 2025](https://leapcell.io/blog/why-monolithic-architecture-reigns-supreme-for-new-projects-in-2025)
- [Startup MVP Architecture: Why Over-Engineering Kills Growth](https://www.swarnendu.de/videos/startup-mvp-architecture/)
- [2025 Year in Review: Lessons from Solo SaaS Development](https://dev.to/pipipi-dev/2025-year-in-review-lessons-from-solo-saas-development-3i08)
- [Strangler Fig Pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-decomposing-monoliths/strangler-fig.html)
- [Strangler Fig Application Pattern: Incremental Modernization](https://microservices.io/post/refactoring/2023/06/21/strangler-fig-application-pattern-incremental-modernization-to-services.md.html)
- [Developer's Guide to Multi-Agent Patterns in ADK — Google](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/)
- [AI Agent Orchestration Patterns — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [A Practical Guide for Designing Agentic AI Workflows (arXiv)](https://arxiv.org/html/2512.08769v1)
- [Context Window Management for LLM Apps — Redis](https://redis.io/blog/context-window-management-llm-apps-developer-guide/)
- [Chunking Strategies for RAG — Weaviate](https://weaviate.io/blog/chunking-strategies-for-rag)
- [Sam Newman: Monolith to Microservices (O'Reilly)](https://www.amazon.com/Monolith-Microservices-Evolutionary-Patterns-Transform/dp/1492047848)
- [How to Break a Monolith into Microservices — Martin Fowler](https://martinfowler.com/articles/break-monolith-into-microservices.html)
- [Store State on Filesystem in Node.js CLIs with Conf](https://egghead.io/lessons/javascript-store-state-on-filesystem-in-node-js-clis-with-conf)
