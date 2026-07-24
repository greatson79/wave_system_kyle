# SaaS Auto-Builder: PROVEN STACK Implementation Scenario

**Scenario**: PROVEN STACK — "Every technology choice must have 5+ years of production validation, or be the minimum viable LLM usage required."
**Philosophy**: We accept slower development and less "magic" in exchange for predictability, debuggability, and zero surprises.
**Risk Profile**: LOW — lowest of the three scenarios. Residual risk is market timing and UX quality, not technical failure.
**Date**: 2026-03-12
**Analyst**: Technology Leader (Maximum Reliability Priority)
**Data Basis**: Phase 1-2 Research Synthesis (10 branches, 4 discussion perspectives) + Conservative Technology Stack Analysis + Classical Theoretical Foundations Report
**System Context**: LOCAL CLI tool (Claude Code) that generates full-stack SaaS from user descriptions via 14-question conversation → 7 specification documents → code scaffolding.

---

## Preface: Why "Proven" Is an Engineering Requirement, Not a Preference

Before a single technology choice appears in this document, the argument for conservatism must be made precisely, because it is frequently misunderstood as timidity rather than rigor.

**The multiplicative blast radius argument (Branch 4.1)**: When a solo developer writes code with a cutting-edge library and hits a bug, the blast radius is one project. When a code generator writes that same code and ships it to 1,000 users, the blast radius is 1,000 identical bugs across 1,000 projects — each user debugging code they did not write, using tooling they do not fully understand, in a framework they adopted because a generator recommended it. A 0.1% defect rate in hand-written code becomes a 100% reproducibility rate in generated code. This asymmetry changes the risk calculus entirely.

**The local CLI constraint (주의2)**: This system runs on the user's machine. There is no distributed tracing, no error aggregation service, no automatic rollback orchestration. When something goes wrong at 11pm, the user needs to understand why from local log files and standard tools. FSM state transition logs, Zod validation errors, and Handlebars template failures are debuggable this way. LLM "reasoning failures" are not.

**The user approval requirement (주의3)**: Every generated document requires explicit user approval before the next stage begins. This constraint is not a limitation — it is the highest-value quality gate in the system. Designing around it means designing for legibility: the system must explain itself at each stage in terms the user can evaluate. Template-structured documents with predictable sections satisfy this requirement. Fully-generative outputs do not.

**The PRD pre-work framing (주의1)**: This system does not build a SaaS. It produces PRD.md and 6 companion specification documents as pre-work for implementation. The generated documents are the product. Every architectural decision must be evaluated against this scope.

The proven stack philosophy translates these four constraints into a single engineering directive: **minimize the surface area of non-determinism, and make every non-deterministic component observable, bounded, and replaceable**.

---

## 1. Architecture: Sequential Pipeline with Deterministic Gates

### 1.1 Core Design Principle

The architecture is the simplest pipeline that satisfies the requirements. One sentence: a CLI collects user intent through a FSM-governed 14-question conversation, builds a validated context object, passes it sequentially through 7 document generators (each requiring user approval before the next starts), and writes specification documents to disk.

No parallel processing. No multi-agent orchestration. No autonomous decision-making. Every stage has a defined input schema, a defined output schema, and a deterministic gate that must be cleared before the next stage begins.

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Terminal)                                 │
│    $ saas-builder create "I want to build a team invoicing tool"            │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                    ENGINE 1: NLU / INTENT (Stage 1)                         │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Layer 1: Rule-based classifier (keyword tables × domain taxonomy)    │   │
│  │          Confidence ≥ 0.60 → proceed directly to FSM dialog          │   │
│  │          Confidence < 0.60 → LLM fallback (Claude Haiku, Structured  │   │
│  │                              Output, closed 12-domain taxonomy)      │   │
│  │ Layer 2: User confirmation gate — "I understand you want to build ... │   │
│  │          Is that correct? [yes/no/correct-it]"                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                ↓ ParsedIntent (Zod-validated)               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                  ENGINE 1 CONTINUED: FSM DIALOG (Stage 2)                   │
│                                                                             │
│  TypeScript FSM: 10 named states, explicit transition table                 │
│  Frame Semantics slot-filling: 14 questions, dependency DAG                 │
│  Session serialized to saas-session.json after every state transition       │
│  LLM role: extract slot values from natural-language answers only           │
│                                                                             │
│  States: initial → domain_confirmed → scale_captured → features_listed     │
│          → tech_prefs_collected → constraints_gathered → summary_shown      │
│          → approved → document_gen_in_progress → complete                  │
│                                ↓ SaaSContext (Zod-validated, 14 slots full) │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                   ENGINE 2: AI PM IDEATION (Stage 3)                        │
│                                                                             │
│  Pre-built SaaS ideation frameworks (per-domain templates: 12 domains)      │
│  LLM fills content within template structure — does not invent structure    │
│  Output: ProductIdea object (name, tagline, 3 differentiators, scope note)  │
│  User approval gate: "Here is the product concept. Proceed? [yes/refine]"  │
│                                ↓ ProductIdea (Zod-validated)                │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 3: TOOL/TEMPLATE SELECTION (Stage 4)                    │
│                                                                             │
│  Decision matrix: user tech level × project complexity → template catalog   │
│  Rule-based matching: NO LLM involved                                       │
│  Output: TemplateSelection (stack, files list, feature flags)               │
│  Deterministic: same context object → same template selection, always       │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 4: FEATURE EXTRACTION (Stage 5)                         │
│                                                                             │
│  Pre-built feature taxonomy (50+ common SaaS features, organized by domain) │
│  Checkbox menu for known features + LLM extraction from free-text additions │
│  Zod validation: all extracted features must be in known taxonomy           │
│  Output: FeatureSet (selected features, priorities, constraints)            │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 5: USER RESEARCH (Stage 6)                              │
│                                                                             │
│  Template personas: 5-7 archetypes per SaaS domain (pre-built)             │
│  LLM customizes template with user's specific context (not fully generative)│
│  Output: PersonaSet (2-3 validated personas with pain points + goals)       │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 6: DOCUMENT PIPELINE (Stage 7)                          │
│                                                                             │
│  Sequential generation ONLY — no parallelism (predictability > speed)       │
│  Handlebars templates define structure. LLM fills content sections only.    │
│  Zod schema validation BEFORE passing to LLM (input) and AFTER (output)    │
│  Cross-document validation: schema-based foreign keys between documents     │
│                                                                             │
│  PRD.md → [user approval] → UserJourney.md → [user approval]               │
│         → TRD.md → [user approval] → CodeGuidelines.md → [user approval]   │
│         → UIGuidelines.md → [user approval] → IA.md → [user approval]      │
│         → Tasks.md → [user approval]                                        │
│                                ↓ 7 approved .md files                      │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 8: CODE GENERATION (Stage 8)                            │
│                                                                             │
│  Yeoman/Plop.js scaffolding — template-based, deterministic structure       │
│  Handlebars templates per file type (Next.js pages, API routes, Prisma)     │
│  Conditional compilation: user choices → template variables → generated code│
│  LLM ONLY for: custom business logic sections that cannot be templated      │
│  Generated code MUST PASS: lint (ESLint), typecheck (tsc), build (Next.js) │
│  Failure = abort + show error to user (not silent, not auto-fix)            │
│                                ↓ Generated project directory                │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│              ENGINE 9: META-PROGRAMMING (Stage 9)                           │
│                                                                             │
│  Static AGENTS.md / CLAUDE.md templates — NOT LLM-generated                 │
│  Variable substitution for project-specific values (project name, features) │
│  Human-reviewed reference templates: reviewed before each release           │
│                                ↓ Complete output package                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 State Machine: 10 Named States

```typescript
enum DialogState {
  INITIAL              = "initial",
  DOMAIN_CONFIRMED     = "domain_confirmed",
  SCALE_CAPTURED       = "scale_captured",
  FEATURES_LISTED      = "features_listed",
  TECH_PREFS_COLLECTED = "tech_prefs_collected",
  CONSTRAINTS_GATHERED = "constraints_gathered",
  SUMMARY_SHOWN        = "summary_shown",
  APPROVED             = "approved",
  DOCUMENTS_IN_PROGRESS = "documents_in_progress",
  COMPLETE             = "complete"
}
```

Every transition is a deterministic function: `transition(state: DialogState, event: UserEvent): DialogState`. The transition table has 47 entries, each independently unit-testable. Every invalid transition throws a typed `InvalidTransitionError` with the current state and attempted event. No "recovery by inference." No "the system guessed based on context."

### 1.4 File Count: ~25-30 Files (V1)

```
saas-builder/
├── src/
│   ├── cli.ts                    ← Commander.js entry point
│   ├── engines/
│   │   ├── intent/
│   │   │   ├── classifier.ts     ← Rule-based keyword classifier
│   │   │   ├── fsm.ts            ← FSM with 10 states, transition table
│   │   │   ├── slot-filler.ts    ← Frame semantics slot extraction
│   │   │   └── domain-frames/    ← 12 domain frame definitions (JSON)
│   │   ├── ideation.ts           ← Template-based PM ideation
│   │   ├── tool-selector.ts      ← Decision matrix (no LLM)
│   │   ├── feature-extractor.ts  ← Taxonomy + LLM for free-text
│   │   ├── user-researcher.ts    ← Template personas + LLM customization
│   │   ├── document-pipeline.ts  ← Sequential 7-doc orchestrator
│   │   ├── code-generator.ts     ← Yeoman/Plop scaffolding + LLM business logic
│   │   └── meta-programmer.ts    ← Static template substitution
│   ├── schemas/
│   │   ├── saas-context.schema.ts   ← Zod: 14 slots
│   │   ├── prd.schema.ts
│   │   ├── user-journey.schema.ts
│   │   ├── trd.schema.ts
│   │   ├── code-guidelines.schema.ts
│   │   ├── ui-guidelines.schema.ts
│   │   ├── ia.schema.ts
│   │   └── tasks.schema.ts
│   ├── llm/
│   │   └── adapter.ts            ← LLMAdapter interface + Anthropic SDK impl
│   └── templates/                ← Handlebars + Yeoman templates
├── tests/
│   ├── intent/
│   │   ├── classifier.test.ts    ← 200+ rule-based cases
│   │   └── fsm.test.ts           ← 500+ FSM transition cases
│   ├── pipeline/
│   │   └── golden-outputs/       ← Golden file tests per document type
│   └── cassettes/                ← Recorded LLM responses (non-deterministic)
└── package.json
```

---

## 2. Per-Engine Technology Decisions

### Engine 1 — NLU / Intent Understanding

**Primary strategy**: Rule-based keyword classifier handles 80% of inputs deterministically. LLM fallback for the 20% where rule-based confidence < 0.60.

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Primary classifier | Keyword tables × domain taxonomy (TypeScript) | Rule-based systems: 30+ years of NLP production history. No API dependency. O(n) performance. Fully unit-testable. | ZERO |
| Confidence threshold | 0.60 (never guess below this) | Calibrated to actual SaaS domain input distribution. 80%+ of inputs contain domain-specific vocabulary. | — |
| Fallback classifier | Claude Haiku + Structured Output + closed 12-domain taxonomy | When rule-based fails, LLM provides contextual understanding that no rule can replicate. Constrained to closed taxonomy prevents hallucination. | YES — bounded |
| Confirmation gate | CLI prompt: "Is that correct? [yes/no/correct-it]" | Human-in-loop is the highest-quality gate in the system. Catches 80%+ of classification errors before they propagate. | ZERO |
| Slot filling | Frame semantics (Fillmore 1976) + dependency DAG | 50-year theoretical foundation. Each domain activates a semantic frame with declared slot dependencies. Rollback is deterministic: invalidate dependents, not the full session. | YES — extraction only |
| Session persistence | JSON checkpoint to disk after every state transition | LOCAL CLI constraint. No network. No database. Plain JSON is readable with any text editor. Recovery = load checkpoint, resume from last state. | ZERO |

**Why not LLM-primary intent?** Branch 1.2 identifies the failure mode precisely: LLM conversation management lacks a formal model of slot dependencies. When a user changes their domain at question 8, an LLM cannot reliably determine which of the previous 7 answers are now invalid. An FSM with an explicit dependency DAG resolves this in O(k) where k is the number of dependent slots. The LLM "might" get this right; the FSM always does.

**Stability score: 9.4/10** (Branch 2.B assessment confirmed across all 10 branches)

### Engine 2 — AI PM Ideation

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Ideation framework | Pre-built templates: 12 SaaS domain × 3 complexity tiers = 36 idea frameworks | Templates encode domain knowledge accumulated from 12+ years of SaaS patterns. They do not hallucinate market positions or invent non-existent categories. | ZERO |
| Creative expansion | Claude Sonnet — fills content within template structure | LLM is genuinely irreplaceable here. No template can generate creative, user-specific product positioning. Constrained: LLM fills 5 defined fields, does not invent structure. | YES — bounded |
| Output validation | Zod: `ProductIdea` schema (name, tagline, 3 differentiators, scope note) | LLM output passes or fails schema. No partial accepts. Failure = retry once, then show user the raw attempt for manual correction. | ZERO |

### Engine 3 — Tool / Template Selection

**Zero LLM involvement.** This is the engine where the system's determinism is most visible and most valuable.

| Component | Technology | Stability Rationale |
|-----------|-----------|---------------------|
| Decision matrix | TypeScript lookup table: user_tech_level × project_complexity × domain → TemplateSelection | 3×3×12 = 108 entries. Every entry manually reviewed. Every entry testable. Zero probability of "creative" selection that produces an inappropriate stack for a non-technical user. |
| Template catalog | Handlebars/Yeoman templates: 12 domains × 3 complexity tiers | 12+ years for Yeoman (released 2012, 200K+ apps generated), 14+ years for Handlebars (released 2010, 23M+ weekly npm downloads). Failure modes are fully documented. |
| Tech level assessment | Derived from FSM slot `user_tech_level` (one of: beginner/intermediate/advanced) | Captured explicitly in dialog, not inferred. No ambiguity. |

**Why no LLM?** The question "which template should I use?" has a deterministic answer given the user's tech level, project complexity, and domain. An LLM that "reasons" about template selection introduces non-determinism into a decision that has no business being non-deterministic. Two identical users asking for identical projects must receive identical template selections.

### Engine 4 — Feature Extraction

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Known feature menu | Pre-built taxonomy: 50+ features organized by domain (JSON) | Checkbox selection from known features. No hallucination possible. User picks from items that the generator has templates for. | ZERO |
| Free-text extraction | Claude Haiku + Structured Output constrained to taxonomy IDs | When user writes "I also want the ability to schedule recurring invoices," LLM maps this to `feature:invoice_scheduling` in the taxonomy. Returns taxonomy ID, not free text. | YES — bounded |
| Taxonomy validation | Zod: all extracted features must be in known taxonomy | If LLM returns an ID not in taxonomy: reject, ask user to rephrase, or offer closest match. Never generate code for features outside the known taxonomy in V1. | ZERO |

**Why taxonomy-constrained?** This is the Proven Stack's most explicit trade-off vs. Cutting Edge. The Cutting Edge scenario can generate any feature the user describes. Proven Stack generates only features with validated templates. The cost: less customization. The benefit: generated code always has templates tested against lint, typecheck, and build. No user receives generated code for a feature the system has never validated.

### Engine 5 — User Research

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Persona archetypes | Pre-built: 5-7 archetypes per SaaS domain (JSON templates) | Domain-specific archetypes encode 12+ years of SaaS product management knowledge. They prevent the LLM from generating personas that bear no relationship to actual SaaS users in that domain. | ZERO |
| Customization | Claude Sonnet — fills archetype details with user's specific context | The LLM provides genuine value here: adapting generic archetypes to a specific product context ("your primary user is a freelance graphic designer billing clients in Europe, not a generic 'small business owner'"). | YES — template-guided |
| Output validation | Zod: `PersonaSet` schema (2-3 personas, each with role, pain points array, goals array, technical comfort level) | Prevents LLM from generating personas that are structurally invalid (e.g., missing pain points, which would make the user research section of the PRD empty). | ZERO |

### Engine 6 — Document Pipeline

This is the engine where the Proven Stack's architecture most clearly separates from alternatives. The philosophy: **the LLM writes words; the system controls structure, sequence, and validation**.

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Document structure | Handlebars templates: one template per document type × domain | Handlebars (2010, 23M+ weekly downloads): battle-tested, zero dependencies on LLM, failure modes documented for 14 years. Each template has exactly N sections. The LLM fills section content. It does not invent sections. | ZERO |
| Content generation | Claude Sonnet — fills section content within template | LLM is irreplaceable for specification prose. A PRD without coherent language is not useful. Template structure ensures completeness; LLM ensures quality of prose within that structure. | YES — central use |
| Input validation | Zod: validates `SaaSContext` + `FeatureSet` + `PersonaSet` before passing to LLM | Bad input to LLM = bad output. Zod validation catches malformed context objects before they produce malformed documents. | ZERO |
| Output validation | Zod: validates document JSON before converting to Markdown | Every section required by the schema must be present. Cross-document consistency check: features in PRD must appear in TRD. Foreign key constraint enforced by deterministic code, not LLM self-check. | ZERO |
| Stage sequencing | Sequential with explicit approval contracts: document N requires user [yes] before N+1 begins | Sequential contracts from Branch 2.B: deterministic code checks approval, not LLM evaluation of user "seeming satisfied." | ZERO |
| Cross-document validation | TypeScript: `features_in_prd ⊆ features_in_trd` check | 20-line script. Not an LLM self-check (Branch 2.B §4.2: "self-referential LLM validation is zero-value validation"). | ZERO |

**Sequential ONLY, no parallel**: The Cutting Edge and Balanced-Tech scenarios parallelize independent document pairs to reduce latency. Proven Stack does not. Rationale: the 30% latency saving is real, but the debugging surface area is not. In a sequential pipeline, if document 4 fails validation, the cause is unambiguous: document 4's generation step. In a parallel pipeline, a failure in document 4 may be caused by a race condition in document 3's approval gate. The debugging complexity is not worth the latency saving for V1.

### Engine 7 — Multi-Agent Orchestration

**This engine does not exist in V1.**

The Proven Stack defers multi-agent entirely. V1 is a single orchestrator that calls the LLM with different system prompts at different pipeline stages. This is not an architectural compromise — it is the correct choice for the validation period.

Rationale from Branch 2.D: "The system must be correct before it is fast." Multi-agent in V1 means: two LLM calls that can produce conflicting outputs with no deterministic arbiter, race conditions in shared state, and debugging complexity that requires distributed tracing tooling that cannot exist in a local CLI. Sequential orchestration eliminates all three risks. V2 multi-agent is enabled by the `LLMAdapter` interface (Section 5 — Upgrade Path).

### Engine 8 — Code Generation

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| Scaffold generation | Yeoman + Plop.js + Handlebars templates | Yeoman: released 2012, 200K+ applications generated, 9K+ community generators. JHipster (Branch 1.2): 12+ years, enterprise Java → TypeScript patterns. Handlebars: 14+ years, structural guarantees for every generated file. | ZERO |
| Conditional compilation | Template variables from `TemplateSelection` object | User choices (auth: JWT vs. OAuth, DB: Postgres vs. SQLite, payment: yes/no) directly map to template conditionals. Same input → same files. Deterministic. | ZERO |
| Custom business logic | Claude Sonnet — fills marked `{{BUSINESS_LOGIC}}` sections in templates | The irreplaceable LLM use: a billing portal's invoice calculation logic cannot be templated without understanding the user's specific billing model. LLM fills this section within the structural constraints defined by the surrounding template. | YES — bounded |
| Syntax validation | TypeScript compiler: `tsc --noEmit` | Deterministic formal grammar validation. If `tsc` rejects the output, the generation fails. Not "probably fine." Non-negotiable. | ZERO |
| Lint validation | ESLint with project ruleset | Style and common error patterns. Catches issues `tsc` misses (unused variables, unreachable code). | ZERO |
| Schema validation | Prisma validate (for database schema files) | Deterministic schema validation. Prisma has 6+ years of production history. | ZERO |
| Build verification | `next build` (dry-run) | Structural correctness at the application level. If the build fails, the user is shown the error and the generation session is checkpointed. The user can re-run from the last successful stage. | ZERO |

**The non-negotiable**: Generated code MUST pass lint + typecheck + build before being written to disk. A generated project that fails `next build` out of the box is worse than no generated project. The user has no way to know if the failure is in their business logic or in the generator's template. This is why the Proven Stack accepts slower generation (validation adds 30-60 seconds per run) in exchange for this guarantee.

### Engine 9 — Meta-Programming

| Component | Technology | Stability Rationale | LLM Involvement |
|-----------|-----------|---------------------|-----------------|
| AGENTS.md / CLAUDE.md | Static templates with variable substitution | LLM-generated meta-programming instructions are unpredictable and untestable. Static, human-reviewed templates are reproducible. Variable substitution (project name, feature list, tech stack) is deterministic. | ZERO |
| Reference templates | Maintained in `templates/meta/` directory, reviewed before each release | Human review before release = highest quality gate for meta-programming artifacts. These files govern how Claude Code will interact with the generated project. Getting them wrong is architecturally significant. | ZERO |

---

## 3. Development Timeline

### 3.1 Month-by-Month Milestones

The Proven Stack accepts a longer timeline because each stage is validated thoroughly before moving forward. This is not slowness — it is the debt firewall applied to the development process itself.

| Month | Focus | Deliverables | Success Criteria |
|-------|-------|-------------|------------------|
| **Month 1** | Engine 1 (NLU/Intent) + FSM foundation | Rule-based classifier (200+ test cases passing), 10-state FSM (500+ transition tests), session checkpoint/restore, CLI scaffolding | Intent classification accuracy > 99% on test suite; FSM state corruption: zero |
| **Month 2** | Engine 4 (Feature Extraction) + Engine 3 (Tool Selection) + Schema layer | Feature taxonomy (50+ features), decision matrix, all 8 Zod schemas, LLMAdapter interface | Taxonomy-constrained extraction: 100% (no hallucinated features); tool selection: deterministic on 108 matrix entries |
| **Month 3** | Engine 6 (Document Pipeline) — PRD + User Journey + TRD | 3 Handlebars templates, golden-file tests for each, cross-document validation, first end-to-end demo | 3 documents pass Zod validation 100%; golden-file diff < 5% from baseline on 20 test cases |
| **Month 4** | Engine 6 continued — Code Guidelines + UI Guidelines + IA + Tasks | 4 remaining Handlebars templates, full 7-document pipeline, user approval gates, cassette test suite | Full pipeline run end-to-end: all 7 documents generated and validated; 200+ cassette tests passing |
| **Month 5** | Engine 2 (Ideation) + Engine 5 (User Research) + Engine 8 (Code Generation — scaffold only) | Ideation templates (36 frameworks), persona templates (12 domains), Yeoman scaffold for 3 SaaS types | Scaffold generation: lint + typecheck + build pass 100% of test runs; 70% code coverage gate met |
| **Month 6** | Engine 8 (Code Generation — LLM business logic) + Engine 9 (Meta) + Polish | Business logic slot filling, AGENTS.md templates, error messages, edge cases, documentation | Generated code build pass rate ≥ 99%; end-to-end run success rate ≥ 98%; V1 ship |

### 3.2 When is V1 Ready?

V1 ships when:
1. All 200+ rule-based intent classifier tests pass
2. All 500+ FSM transition tests pass
3. All 7 document types pass Zod schema validation on 100% of test inputs
4. All 3 supported SaaS scaffolds pass `lint + tsc + next build` on 100% of test runs
5. End-to-end run success rate ≥ 98% on 100 diverse test inputs (measured with cassette replay)
6. Code coverage ≥ 70% on deterministic components (non-LLM code)

Not shipped until all six gates pass. No exceptions.

### 3.3 When is V2 Ready?

V2 (Multi-Agent + Expanded Domain) begins 4-6 weeks after V1 ship, contingent on:
- V1 running ≥ 500 sessions without a regression-class bug
- Cassette suite expanded to 300+ cases covering V1 production inputs
- `LLMAdapter` interface proven stable (no breaking changes in V1)

V2 scope: multi-agent orchestration for document pipeline, 6 additional SaaS domains, expanded feature taxonomy (100+ features), parallel document generation for independent pairs.

---

## 4. Quality Strategy

### 4.1 Test Architecture

The Proven Stack achieves high confidence through maximal testing of deterministic components and minimal (but carefully bounded) testing of non-deterministic LLM components.

**Layer 1 — Unit Tests (Deterministic components)**

| Component | Test Count | Coverage | Time to Run |
|-----------|-----------|----------|-------------|
| Rule-based intent classifier | 200+ cases | All keyword tables, edge cases, ambiguous inputs | < 2 seconds |
| FSM transitions | 500+ cases | All 47 transitions, all invalid transitions, rollback cases | < 1 second |
| Zod schema validation | 150+ cases | Valid inputs, boundary cases, invalid inputs per schema | < 1 second |
| Template rendering (Handlebars) | 100+ cases | All 7 document templates × representative SaaSContext objects | < 3 seconds |
| Decision matrix (Engine 3) | 108+ cases | All 108 matrix entries + boundary conditions | < 1 second |
| Feature taxonomy matching | 80+ cases | Exact matches, partial matches, out-of-taxonomy rejections | < 1 second |

**Total deterministic test suite: ~1,140 tests. Runs in < 10 seconds. No LLM API calls. Runs on every commit.**

**Layer 2 — Cassette Tests (LLM components)**

Cassette pattern (Branch 3.2): record actual LLM responses to representative inputs, store as JSON files, replay deterministically in CI. LLM calls in CI are zero (cassette playback only). LLM calls outside CI update the cassette library (run weekly or on prompt changes).

| Component | Cassette Count | Trigger for Re-recording |
|-----------|---------------|--------------------------|
| Intent classification (fallback) | 50 cassettes | Prompt version bump or model version bump |
| Slot extraction | 60 cassettes | Prompt version bump |
| Ideation content generation | 36 cassettes | One per domain-complexity combination |
| User research customization | 36 cassettes | One per domain archetype |
| Document content generation | 140 cassettes | 20 per document type |
| Business logic slot filling | 30 cassettes | Per SaaS scaffold type |

**Total cassette library: ~352 cassettes. CI runs deterministically in < 30 seconds.**

**Layer 3 — Golden File Tests**

For each of the 7 document types, maintain golden output files for 3 representative SaaS inputs per domain (3 inputs × 12 domains × 7 documents = 252 golden files). Any code change that causes a golden file diff > 5% requires explicit review before merge.

**Layer 4 — Build Verification Tests**

For each of the 3 supported scaffold types (SaaS Web App, API-only, Admin Dashboard), run the full generation → lint → typecheck → build pipeline on each CI run. Failure = broken scaffold template. Non-negotiable gate.

### 4.2 Coverage Target

- Deterministic components: 70%+ line coverage (target for V1 ship)
- LLM adapter: 100% interface coverage via cassette tests
- Template rendering: 100% (all conditional branches tested)
- Schema validation: 100% (all required fields, all rejection cases)

### 4.3 Regression Detection

When model behavior drifts (API version change, model behavior update): run cassette suite, compare outputs against stored cassettes. > 5% diff rate triggers investigation before deployment. This is the primary mechanism for detecting the non-deterministic risk that cannot be eliminated.

---

## 5. Cost Analysis

### 5.1 Token Cost Per Run

The Proven Stack's most significant cost advantage over alternatives: 80% of classification is rule-based (zero tokens), all validation is Zod (zero tokens), all scaffolding is Handlebars (zero tokens). LLM involvement is limited to: fallback classification, content generation (7 documents), business logic slot filling.

| Stage | Model | Estimated Tokens (Input + Output) | Cost per Run (Sonnet pricing: $3/$15 per M) |
|-------|-------|----------------------------------|---------------------------------------------|
| Intent fallback classification (20% of runs) | Haiku ($0.25/$1.25 per M) | ~500 input + ~100 output | ~$0.0001 |
| Ideation content fill | Sonnet | ~2,000 input + ~800 output | ~$0.018 |
| User research customization | Sonnet | ~3,000 input + ~1,200 output | ~$0.027 |
| 7 document content sections | Sonnet | ~5,000 input + ~15,000 output | ~$0.24 |
| Business logic slot filling | Sonnet | ~3,000 input + ~5,000 output | ~$0.084 |
| **Total (typical run)** | Mixed | **~29,000 tokens** | **~$0.37/run** |

**Compared with alternatives:**
- Cutting Edge scenario: ~$12-25/run (Branch 1.1: 800K-1.2M tokens, multi-agent + full parallel pipeline)
- Balanced-Tech scenario: ~$3-6/run (Branch 2.2 estimate: moderate parallelism + Structured Outputs)
- **Proven Stack: ~$0.37/run** — approximately 95% cheaper than Cutting Edge, 90% cheaper than Balanced

**Why such a large difference?** The gap is almost entirely explained by three choices:
1. Sequential pipeline (no redundant context re-injection across parallel agents)
2. No multi-agent (eliminates agent-coordination token overhead)
3. Template-based structure (LLM generates content, not scaffold — 70% reduction in output tokens)

### 5.2 Development Cost

The Proven Stack requires more developer hours than alternatives:
- Keyword classifier maintenance: ~4 hours per new domain (vs. zero for LLM-primary)
- Template development: ~8 hours per document template (vs. zero for fully generative)
- Feature taxonomy curation: ~2 hours per 10 new features (vs. zero for free-text extraction)

Over a 6-month timeline, this represents approximately 60-80 additional development hours versus the Cutting Edge scenario. However, the Proven Stack saves approximately 80-120 hours of LLM debugging time (debugging non-deterministic failures, chasing hallucinations, diagnosing prompt sensitivity). Net developer cost: roughly equivalent, with the Proven Stack delivering predictable output throughout the 6 months and the Cutting Edge delivering variable output with concentrated debugging periods.

---

## 6. Risk Matrix

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation | Residual Risk |
|------|-------------|--------|------------|---------------|
| **API unavailability** (Claude API down) | Low-Medium (2-3× per year, < 4h each) | Medium — session cannot complete | Graceful exit with clear message; session checkpoint preserved; retry when available | Low |
| **Intent misclassification** (rule-based + LLM + confirmation fails) | Very Low (< 1% with hybrid 3-layer stack) | High — wrong domain = wrong everything | User confirmation gate catches 80%+ of errors before propagation | Very Low |
| **Document schema violation** (LLM generates invalid structure) | Minimal (Zod pre-validation + output validation) | High — invalid document cannot be used | Pre-validation of LLM inputs; post-validation of LLM outputs; failure = retry once then surface to user | Minimal |
| **Code generation syntax error** (generated TypeScript fails tsc) | Minimal (tsc validation gate) | Medium — user receives broken scaffold | tsc validation before write to disk; failure = abort + show error; user can request regeneration | Minimal |
| **Template regression** (template change breaks generated code) | Low (templates are versioned, golden-file tests catch regressions) | Medium — affects all users until patched | Golden-file tests + build verification tests catch regressions in CI before release | Low |
| **Model behavior drift** (LLM output quality changes post-API update) | Low-Medium (3-4× per year with model updates) | Medium — document quality degrades | Cassette suite with 352 recordings; > 5% diff = flag for review | Low |
| **Session corruption** (power failure, crash mid-pipeline) | Low | Medium — user loses progress | JSON checkpoint after every state transition; resume from last approved stage | Low |
| **API pricing change** | Medium (historical: annual pricing adjustments) | Low-Medium (at $0.37/run, even 3× cost increase = $1.11/run — still cheap) | Tiered model routing (Haiku for classification, Sonnet for generation); budget tracking | Low |

**Overall technical risk profile: LOW.** This is the lowest-risk technical stack achievable while still using Claude API for content quality.

### 6.2 Strategic Risks (Where Proven Stack Is Vulnerable)

These risks are not mitigated by the technical stack. They are the honest costs of the Proven Stack philosophy.

| Risk | Probability | Impact | Notes |
|------|-------------|--------|-------|
| **Market timing** | Medium | High | If Cutting Edge scenario ships in 6 weeks (Branch 2.C: Speed discussion), and Proven Stack ships in 6 months, a competitor occupies the market. The Proven Stack bets that quality matters more than speed-to-market. This bet may be wrong. |
| **UX quality gap** | High | Medium | FSM-governed conversation is less "magical" than LLM-native conversation. Users who have experienced ChatGPT-quality UX may find the structured Q&A experience inferior. This is a real competitive disadvantage. |
| **Domain coverage limitation** | High | Medium | V1 supports 12 SaaS domains. Cutting Edge supports arbitrary domains via fully-generative approach. Users with non-standard SaaS ideas may be unable to use Proven Stack V1. |
| **Feature scope limitation** | High | Medium | 50-feature taxonomy in V1. Users who need custom features outside the taxonomy receive an honest "not supported" rather than a hallucinated template. This is correct behavior but may be perceived as inferior to alternatives. |
| **Innovation perception** | Medium | Low | "No magic" is not a compelling marketing story. Competitors who promise (and sometimes deliver) more advanced features may win mindshare even if Proven Stack wins reliability. |

---

## 7. Honest Limitations Assessment

The Proven Stack is the right choice for some situations and clearly wrong for others. This section is honest about what it cannot do.

### 7.1 What Proven Stack Cannot Do (That Cutting Edge Can)

**Arbitrary domain support**: The Cutting Edge scenario handles any SaaS idea the user can describe. Proven Stack handles 12 pre-defined domains in V1. A user who wants to build an AI-powered legal contract generator, a marketplace for freelance underwater welders, or a SaaS for managing community-supported agriculture subscriptions will be told "not supported in V1." This is not a failure mode — it is a design choice — but it limits total addressable market.

**Proactive suggestions**: The Cutting Edge scenario (via multi-agent and agentic loops) can proactively suggest features the user has not considered, identify competitive gaps in the user's described market, and recommend architecture patterns based on scale requirements. Proven Stack does none of this. It responds to what the user says; it does not contribute to what the user should consider.

**Conversation naturalness**: The FSM dialog is structured. The user is asked specific questions in a specific order. An LLM-native conversation manager can pick up on things the user said earlier, ask follow-up questions based on context, and skip questions that have already been answered. Proven Stack's FSM will ask all 14 questions in dependency order, even if the user's initial description already answered 6 of them.

**Creative document generation**: Documents generated by Proven Stack are well-structured and technically complete. They are also recognizably template-shaped. Users who generate multiple projects will notice the structural similarity between documents. Cutting Edge produces more varied, stylistically distinct documents. For specification documents, structural consistency is arguably a feature (easier to review, compare, and understand); for business documents, it may feel generic.

**Multi-agent parallelism**: The Cutting Edge scenario generates several documents simultaneously through parallel agents, significantly reducing run time. Proven Stack's sequential pipeline is approximately 2-3× slower per run. For users who value speed over cost, this is a meaningful disadvantage.

**Self-healing generation**: Cutting Edge agents can detect that a generated document is logically inconsistent with an earlier document and automatically correct it. Proven Stack surfaces this inconsistency to the user (via cross-document validation) and asks them to resolve it. This is more transparent, but it requires more user effort.

### 7.2 Why Someone Might NOT Choose Proven Stack

Despite its lowest-risk profile, a rational user might reject Proven Stack for these reasons:

1. **They are in a competitive market where speed-to-market matters more than reliability.** If the primary goal is "ship a prototype SaaS in 2 weeks," the Cutting Edge scenario's LLM-heavy, fast-failure-fast-learning approach may be superior even with its higher defect rate.

2. **Their SaaS idea does not fit a standard domain.** If the user is building something genuinely novel — not just a variation on an established SaaS category — the 12-domain constraint is a blocker, not a limitation.

3. **They prioritize UX over correctness.** For users who care more about how the generation experience feels than about whether the generated code passes `tsc`, the more conversational Cutting Edge experience is preferable.

4. **They are technically sophisticated and can debug LLM failures.** The value of Proven Stack's debuggability accrues most to non-technical users who cannot diagnose hallucinations or template failures. Technical users may prefer the Cutting Edge scenario's higher ceiling even if it means more debugging.

5. **They are willing to pay $12-25/run for better output quality.** Proven Stack's cost advantage is a feature if money is a constraint. If the user has a budget and wants the best possible output, the cost differential may be worth it.

---

## 8. Upgrade Path to Balanced-Tech

### 8.1 Why the Upgrade Path Works

The Proven Stack is architecturally designed for upgrade, not replacement. Every LLM dependency is behind a typed interface (`LLMAdapter`). Every document structure is in a separate template file. Every schema is a standalone Zod definition. This means upgrading specific components does not require touching surrounding code.

Branch 2.1's "Day-1 interfaces enable swap without rewrite" is precisely what makes this upgrade path viable. The 4-hour investment in defining clean interfaces in Month 1 creates a clear migration path to Balanced-Tech in Month 7.

### 8.2 Component-by-Component Upgrade Priority

**Priority 1 — Upgrade Intent Engine to Balanced-Tech (Estimated: 2-3 days)**

What changes: replace the pure FSM confirmation gate with Claude Structured Outputs + confidence-scored classification. The FSM remains as the state management layer; the LLM replaces only the slot extraction and fallback classification components.

What stays: FSM transitions (unchanged), session checkpoint (unchanged), dependency DAG (unchanged).

What enables: more natural conversation flow, better handling of implicit answers ("I want to target small businesses" simultaneously answers domain, scale, and user persona questions).

**Priority 2 — Upgrade Document Pipeline to Prompt Caching (Estimated: 1-2 days)**

What changes: add `cache_control` headers to the Anthropic SDK calls in `LLMAdapter`. The Handlebars templates and Zod validation layers are unchanged.

What enables: 76-90% cost reduction on cached prefixes. The system prompt and SaaSContext object, sent at the start of each document generation call, become cached after the first document. Documents 2-7 cost 10% of document 1.

Cost impact: Proven Stack's $0.37/run drops to approximately $0.12-0.15/run with caching enabled.

**Priority 3 — Add Parallel Document Generation for Independent Pairs (Estimated: 1 week)**

What changes: introduce the Petri net model from Branch 2.B §1.3 for the 4 independent document pairs (CodeGuidelines + UIGuidelines can be parallel; IA + UserJourney can be parallel after PRD is approved). The `document-pipeline.ts` orchestrator gains a parallel execution path with explicit dependency checking.

What stays: all Zod validation, all Handlebars templates, all cross-document validation.

What enables: approximately 30% latency reduction per run (Branch 5.2 Petri net estimate).

**Priority 4 — Expand Feature Taxonomy to Free-Text Extraction (Estimated: 2 weeks)**

What changes: the Zod taxonomy constraint is relaxed to allow LLM-generated features with a "needs template" flag. The template generation process begins (LLM generates a new Handlebars template for the requested feature, which is then validated against the build pipeline before being added to the catalog).

What stays: existing taxonomy entries (unchanged, still preferred), build validation (non-negotiable), code generation structure.

What enables: unlimited feature scope. Users can request any feature; the system generates a template for it and adds it to the catalog for future users.

**Priority 5 — Multi-Agent for Document Pipeline V2 (Estimated: 3 weeks)**

What changes: `document-pipeline.ts` orchestrator is replaced by a multi-agent orchestrator using the Claude Agent SDK. Individual document generators become sub-agents with typed communication contracts.

Prerequisite: `LLMAdapter` interface must already be stable (Proven Stack V1 ensures this). All agents communicate through typed `AgentMessage` objects, not through unstructured natural language.

What stays: all Zod schemas, all Handlebars templates, all cross-document validation. The multi-agent layer sits above all of these.

What enables: concurrent document generation, agent-level retry isolation (a failure in the TRD agent does not restart the PRD agent), agent specialization for different document types.

### 8.3 Total Upgrade Effort: Proven → Balanced

| Upgrade | Effort | Risk | When to Prioritize |
|---------|--------|------|-------------------|
| Prompt caching | 1-2 days | Very low | Immediately post-V1 ship (pure cost saving, zero risk) |
| Intent conversation upgrade | 2-3 days | Low | After 200 V1 sessions (validate that the FSM is the actual UX bottleneck) |
| Parallel document pairs | 1 week | Low | After prompt caching proves stable |
| Free-text feature expansion | 2 weeks | Medium | After V1 taxonomy covers 80%+ of user requests |
| Multi-agent pipeline | 3 weeks | Medium | After 500 V1 sessions with zero state corruption incidents |

**Total estimated effort: 5-6 weeks of focused development to reach full Balanced-Tech capability from Proven Stack V1.**

The migration is incremental, validated at each step, and does not require a rewrite of any major component. This is the structural benefit of the Proven Stack's interface-first architecture.

---

## 9. Comparison with Other Scenarios

| Dimension | Proven Stack | Balanced-Tech | Cutting Edge |
|-----------|-------------|--------------|-------------|
| **V1 timeline** | 6 months | 4-5 months | 2-3 months (demo) / 6 months (production) |
| **Cost per run** | ~$0.37 | ~$3-6 | ~$12-25 |
| **Intent accuracy** | 99%+ (hybrid 3-layer) | 97-99% (LLM-primary + validation) | 95-99% (LLM-primary, higher variance) |
| **Domain support (V1)** | 12 domains | 12-20 domains | Unlimited |
| **Feature coverage (V1)** | 50 features (taxonomy-bound) | 80-100 features (taxonomy + LLM) | Unlimited (fully generative) |
| **Generated code quality** | Guaranteed: lint + tsc + build pass | Guaranteed: lint + tsc + build pass | High (but higher variance: 95% pass rate) |
| **UX conversational quality** | Structured (FSM) | Hybrid (FSM + LLM natural) | Natural (LLM-primary) |
| **Debuggability** | Maximum | High | Medium |
| **Upgrade complexity** | Low (interface-first) | Medium | High |
| **Multi-agent** | V2 only | V2 optional | V1 (Agent SDK) |
| **Risk profile** | LOW | MEDIUM | HIGH |
| **Score** | **8.8/10** | **9.1/10** | **8.2/10** |

---

## 10. Final Assessment

### 10.1 Score Breakdown

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|---------|
| Technical reliability (build pass rate, schema validity) | 25% | 9.8/10 | 2.45 |
| Implementation feasibility (6-month solo timeline) | 20% | 9.2/10 | 1.84 |
| Cost efficiency (per-run cost) | 15% | 9.5/10 | 1.43 |
| Debuggability and maintainability | 15% | 9.4/10 | 1.41 |
| User experience quality | 10% | 6.5/10 | 0.65 |
| Domain + feature coverage | 10% | 6.0/10 | 0.60 |
| Competitive differentiation | 5% | 5.5/10 | 0.28 |
| **Total** | **100%** | — | **8.66/10 → rounded 8.7/10** |

**Final Score: 8.7/10**

The Proven Stack does not win on any single dimension where the user experience, coverage breadth, or competitive differentiation is the primary criterion. It wins decisively on the dimensions that matter most for a code generator: reliability of output, cost per run, and debuggability of failures.

The score gap between Proven Stack (8.7) and Balanced-Tech (9.1) is primarily explained by coverage limitations (12 domains vs. broader), UX naturalness, and the absence of proactive suggestions. These are not permanent limitations — the upgrade path closes the gap in 5-6 weeks of post-V1 development — but they are real limitations in V1.

### 10.2 Who Should Choose This Scenario

**Choose Proven Stack if:**
- You are building for users who are not deeply technical (the reliability and debuggability benefits are most valuable to non-technical users)
- You are in a domain where trust matters more than novelty (B2B enterprise tooling, compliance-adjacent SaaS, regulated industries)
- You are a solo founder who needs to ship something reliable in a known timeline, not something impressive in an optimistic timeline
- You are building a long-lived product where maintainability in year 2-3 matters as much as the launch

**Do not choose Proven Stack if:**
- Speed to market is existentially important (a competitor could preempt you in 3 months)
- Your target SaaS types are outside the 12 supported domains
- You expect users to compare your UX against ChatGPT-class conversational experiences and find FSM-structured dialogs inferior
- You have sufficient budget and tolerance for debugging non-deterministic failures

### 10.3 The Proven Stack Promise

Not magic. Not "wow" on first demo. Not unlimited customization. Not the fastest time-to-market.

**What it delivers instead**: A system that generates specification documents and code scaffolding that a user can trust, debug, and build on. A $0.37 run cost that makes per-user economics work at any scale. A 99%+ intent accuracy rate that means 499 out of 500 users never experience a misclassification. A `lint + tsc + build` guarantee that means the generated project works on the user's machine the first time, without the user needing to understand why a particular TypeScript compilation error appeared.

And crucially: an upgrade path that turns every hour invested in the Proven Stack into a foundation for Balanced-Tech capability, not a sunk cost.

The guarantee is not magic. It is reliability. In a product category where the alternative is "impressive demo, unpredictable production," reliability is the competitive advantage.

---

## Appendix: Technology Selection Summary Table

| Engine | Core Technology | LLM Usage | Years in Production | Key Decision |
|--------|----------------|-----------|---------------------|-------------|
| Engine 1 NLU/Intent | TypeScript FSM + keyword classifier | Fallback only (< 20%) | FSM: 60+ years; keyword NLP: 30+ years | Rule-based primary; LLM fallback; user confirmation final gate |
| Engine 1 Dialog | Frame semantics slot filling + dependency DAG | Slot extraction only | Fillmore 1976: 50 years | Explicit dependency graph; deterministic rollback |
| Engine 2 Ideation | Pre-built domain templates (36) | Content fill (bounded) | Template patterns: 12+ years | Template structure; LLM fills content sections only |
| Engine 3 Selection | Decision matrix (TypeScript lookup table) | ZERO | Lookup tables: fundamental CS | Fully deterministic; same input → same selection |
| Engine 4 Features | Feature taxonomy (50+ items) | Free-text extraction (bounded) | Taxonomy design: 20+ years | All extracted features must be in taxonomy; no hallucination possible |
| Engine 5 Research | Template personas (5-7 per domain) | Template customization | Template patterns: 12+ years | Template archetypes; LLM personalizes within template |
| Engine 6 Documents | Handlebars templates + Zod validation | Content generation (primary) | Handlebars: 14 years; Zod: 4 years | Template controls structure; LLM fills content; Zod validates both ends |
| Engine 7 Orchestration | Sequential pipeline (single orchestrator) | N/A (deferred to V2) | Sequential pipelines: 50+ years | No multi-agent in V1; V2 when V1 pipeline proven stable |
| Engine 8 Code Gen | Yeoman/Plop + Handlebars + tsc + ESLint | Business logic fill (bounded) | Yeoman: 12 years; Handlebars: 14 years | Template scaffold; LLM fills `{{BUSINESS_LOGIC}}` sections; tsc gate |
| Engine 9 Meta | Static templates + variable substitution | ZERO | Variable substitution: 50+ years | Human-reviewed templates only; no LLM meta-programming |

---

*Document prepared as pre-work for PRD.md companion documents.*
*Scenario C of 3: Proven Stack (Conservative Maximum Reliability)*
*Counterpart documents: Cutting Edge (Scenario A), Balanced-Tech (Scenario B)*
*Synthesizes: Branch 1.2, 2.1, 2.B, 2.D, 3.2, 4.2, 5.2 (primary) + all 10 Phase 1 branches + 4 Phase 2 discussions*
*Word count: ~7,200*
