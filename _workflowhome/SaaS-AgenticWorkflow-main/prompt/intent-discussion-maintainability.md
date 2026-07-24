# Maintainability-First Discussion: Intent Understanding & SaaS Generation System

**Phase 2 of 4 — Moderator Perspective: Code Quality & Long-Term Maintainability**
**Scope**: LOCAL CLI tool (Claude Code) generating full-stack SaaS, 9 Service Engines
**Date**: 2026-03-12

---

## Opening Position

Before evaluating any architectural choice, a maintainability moderator must ask a single clarifying question: "Who maintains this system at 2 years, not 2 weeks?"

Phase 1 produced 10 branches spanning aggressive and conservative poles across five dimensions. Each branch optimized for a different primary value. This discussion synthesizes all 10 through the lens of **long-term health** — the ability for a team (which may not be the original team) to extend, debug, and evolve the system without fear.

The answer is not the most sophisticated architecture. It is the most *readable* one.

---

## 1. The Maintainability Architecture

### Why Day-1 Interfaces + Formal Contracts Is the Best Combination

Branch 2.1 (Evolutionary Architecture) correctly identifies that premature evolution is wasteful. Branch 2.2 (Big Bang Architecture) correctly identifies that ambiguous contracts become compounding debt. The apparent tension between them dissolves when you distinguish what must be decided on Day 1 versus what can evolve.

**What must be fixed on Day 1**: the shape of data flowing between engines.
**What can evolve**: the internal implementation of each engine.

This is the core insight from Parnas (1972) that Branch 5.2 (Classical Theory) names explicitly: *information hiding*. An engine's internal prompts, retry logic, and model selection are private. Its input/output schema is public. A developer touching the Auth Engine should never need to understand how the Schema Engine works internally.

Day-1 interface commitment, therefore, does not mean implementing everything. It means signing the contract. Branch 2.2's "~8,500 LOC from Day 1" is over-engineering. Branch 2.1's "interfaces enable swap without rewriting" is the correct posture.

The recommended combination:

- **Day 1**: Define TypeScript interfaces for every inter-engine data structure. These are the public contracts. Nothing can flow between engines without passing through a typed interface.
- **Day 1**: Define preconditions and postconditions for every engine (Design by Contract, Meyer 1986 — Branch 5.2).
- **Day 2+**: Implement engines one at a time, behind the interfaces already agreed upon.

This approach passes the "new team member test": a developer joining in month 6 can read the interface files and understand what every engine expects and produces, without needing to trace prompt internals.

### Information Hiding Applied to 9 Engines

Each of the 9 Service Engines encapsulates a distinct class of complexity:

| Engine | Hidden Complexity | Public Interface |
|---|---|---|
| 1. Intent Parser | NLP ambiguity, multi-turn clarification | `ParsedIntent` object |
| 2. Schema Generator | DB normalization, relation inference | `DataSchema` object |
| 3. API Planner | REST conventions, OpenAPI generation | `APIContract` object |
| 4. Auth Engine | OAuth flows, JWT strategy selection | `AuthConfig` object |
| 5. UI Generator | Component hierarchy, Tailwind decisions | `UISpec` object |
| 6. Business Logic | Domain rules, validation chains | `LogicLayer` object |
| 7. Test Generator | Coverage strategy, mock generation | `TestSuite` object |
| 8. Infrastructure Planner | Deployment topology, service selection | `InfraSpec` object |
| 9. Documentation Engine | Content generation, API doc formatting | `DocBundle` object |

A developer responsible for the Auth Engine should never need to read the UI Generator's code. The only shared artifact is the typed interface that connects them.

This is not theoretical. Branch 3.2 (Robust Dev Workflow) observes that without explicit boundaries, a 7-state FSM becomes impossible to reason about unless each state corresponds to exactly one engine. The FSM is maintainable precisely because each transition maps to a single engine's contract fulfillment.

### Separation of Concerns: Why 9 Engines, Not 3 or 30

The number 9 is not arbitrary. Each engine maps to a *distinct decision class* — a category of choices that requires different domain knowledge, different testing strategies, and different evolution patterns.

Merging the Schema Generator and API Planner into one engine saves a file today and creates coupling that costs weeks in 18 months. Splitting the Auth Engine into "OAuth Engine" and "JWT Engine" creates fragmentation that makes it impossible to reason about security holistically.

The 9-engine decomposition is stable because it matches how senior developers already mentally partition a full-stack system. It is not a novel abstraction; it is a codification of existing engineering consensus. Stable decompositions come from matching the system's structure to the structure of the problem domain.

### Design by Contract for Inter-Engine Communication

Every engine's public API must declare:

```typescript
interface EngineContract<TInput, TOutput> {
  preconditions: (input: TInput) => ValidationResult;
  execute: (input: TInput) => Promise<TOutput>;
  postconditions: (output: TOutput) => ValidationResult;
}
```

This is not overhead. This is the mechanism by which "Engine X gave Engine Y bad data" becomes a *diagnosable* failure rather than a mysterious hallucination.

Branch 3.2's Zod validation fits exactly here: preconditions and postconditions are Zod schemas at runtime. TypeScript interfaces are their compile-time counterpart. The two layers together eliminate an entire class of runtime bugs that would otherwise surface only in production.

### The "Specification Compiler" Metaphor as a Maintainability Framework

Branch 5.2 introduces the metaphor: the system is a *specification compiler*. A user writes a natural-language specification ("a SaaS for team task management with billing"). The system compiles it into a runnable application.

This metaphor is not decorative. It has direct maintainability implications:

1. **Compilers have well-defined intermediate representations (IRs)**. The pipeline must have the same. Each engine's output is an IR. No engine skips stages. No engine passes raw text to the next engine.

2. **Compilers produce deterministic output from identical input**. The pipeline must be reproducible. Given the same `ParsedIntent`, the pipeline must produce the same application. This requires prompt versioning (Branch 4.1) and cassette-pattern recording (Branch 3.2) to be first-class, not afterthoughts.

3. **Compiler errors identify the failing pass**. When something goes wrong, the error message must name the engine and the contract violation, not emit a generic "generation failed."

The specification compiler metaphor converts maintainability from a vague aspiration into a set of engineering requirements.

---

## 2. Prompt Maintainability: The Unique AI Challenge

### Prompts Are the New Source Code

In a traditional system, source code is version-controlled, reviewed, tested, and documented. A prompt that drives an engine's core behavior is equally determinative of the system's output — yet it is frequently treated as configuration rather than code.

This is the root cause of what may be called *prompt spaghetti*: prompts that reference other prompts implicitly, contain undocumented assumptions about the model's version, grow through accretion without refactoring, and become impossible to test in isolation.

Branch 4.1 (Tech Debt Minimized) names prompt versioning as a first-class requirement. Branch 3.2 (Robust Dev Workflow) names the cassette pattern for deterministic replay. Branch 5.2 (Classical Theory) names "prompts as programs." These three branches are pointing at the same underlying principle: **prompts require the same engineering discipline as code**.

### Prompt Versioning Strategy

Every prompt must carry:

```typescript
interface VersionedPrompt {
  id: string;             // "schema-generator-v2"
  version: SemVer;        // "2.1.0"
  model: string;          // "claude-opus-4-5"
  inputs: ZodSchema;      // what this prompt expects
  outputs: ZodSchema;     // what this prompt guarantees to produce
  assumptions: string[];  // explicit list of model behavior assumptions
  changelog: ChangeEntry[];
}
```

Semantic versioning rules for prompts mirror those for APIs:
- **Patch** (2.1.0 → 2.1.1): Wording improvement that does not change output structure.
- **Minor** (2.1.0 → 2.2.0): New optional output field added.
- **Major** (2.1.0 → 3.0.0): Output schema changed; downstream engines must be updated.

This makes prompt upgrades a controlled, auditable process rather than a "let me just tweak this" change that silently breaks downstream engines.

### Prompt Testing: Regression Tests, Golden Outputs, Cassette Pattern

Branch 3.2 introduces the cassette pattern: record the actual LLM response for a given input, store it, and replay it in tests. This eliminates non-determinism from the test suite while preserving the ability to detect regressions when prompts change.

A complete prompt test suite requires three layers:

**Layer 1 — Unit (Cassette Pattern)**
For each prompt, record 5-10 representative input/output pairs. Tests run against cassettes, not live LLM calls. CI passes in under 60 seconds.

**Layer 2 — Contract (Schema Validation)**
Every recorded output is validated against the engine's postcondition schema. A prompt that produces structurally invalid output fails contract tests even if the cassette exists.

**Layer 3 — Regression (Golden Output Comparison)**
For critical paths (Intent Parser, Schema Generator), maintain "golden" outputs for known inputs. When a prompt is modified, golden tests flag any behavioral change — even if the new behavior is technically valid. The developer must consciously approve the change.

Without Layer 3, a well-intentioned prompt improvement that subtly changes Schema Generator output silently degrades the quality of generated applications. With Layer 3, the change is visible and the decision to accept it is explicit.

### Prompt Documentation

Every prompt file must include a header comment that answers four questions:

```
# Purpose: What decision does this prompt make?
# Input: What data does this prompt receive?
# Output: What structure does this prompt guarantee to produce?
# Assumptions: What model behaviors does this prompt rely on?
```

A new developer reading this header should understand the prompt's role in the pipeline without reading the prompt body. The body is an implementation detail. The header is the contract.

### Preventing Prompt Spaghetti

Prompt spaghetti occurs when:
- One prompt references another prompt's internal structure ("as you defined in the previous step...")
- Prompts accumulate context by string concatenation without structure
- Prompt logic branches on undocumented conditions
- The same concept is defined differently in multiple prompts

Prevention requires one architectural rule: **each prompt receives only its typed input and produces only its typed output**. Prompts do not share state through global context objects. They do not reference other prompts by name. The pipeline is responsible for assembling the inputs; the prompt is responsible only for its transformation.

This is Separation of Concerns applied at the prompt level.

---

## 3. Pipeline Maintainability

### Typed Contracts Between Stages

The pipeline is a sequence of engine invocations. Each invocation transforms a typed input into a typed output. The entire pipeline can be represented as:

```typescript
ParsedIntent
  → [Schema Generator] → DataSchema
  → [API Planner]      → APIContract
  → [Auth Engine]      → AuthConfig
  → [UI Generator]     → UISpec
  → [Business Logic]   → LogicLayer
  → [Test Generator]   → TestSuite
  → [Infra Planner]    → InfraSpec
  → [Doc Engine]       → DocBundle
  → [Assembler]        → GeneratedSaaS
```

Each arrow is a typed interface. Each bracket is an engine with a documented contract. This diagram is the system's architecture. If the code does not match this diagram, the code is wrong.

TypeScript interfaces provide compile-time enforcement. Zod schemas provide runtime enforcement. Both are required. A runtime validation failure that could have been a compile-time type error represents avoidable debugging time.

### Each Stage Independently Testable and Replaceable

The test for whether a stage is truly independent: can you replace it with a stub that returns a valid `DataSchema`, run the rest of the pipeline, and get a valid application? If yes, the stage is independent. If the rest of the pipeline breaks because it depended on something the `DataSchema` interface does not declare, the abstraction is leaking.

Branch 2.1's "each stage independently stable" and Branch 3.2's "contract testing between pipeline stages" converge on this principle. Contract testing verifies that the consumer (API Planner) correctly handles everything the producer (Schema Generator) can emit. It does not require both to be implemented simultaneously.

### Registry-Driven SOT (Source of Truth)

Branch 1.1 introduces 6 JSON registries for cross-document consistency. This is the correct approach to a recurring problem in document-generating systems: the same concept (e.g., "User entity") appears in the schema, the API contract, the UI spec, and the documentation. If each engine generates its own representation, they drift. If all engines reference the same registry entry, they stay consistent.

The registry pattern converts "Engine X and Engine Y disagree about the User entity" from a runtime inconsistency into a compile-time impossibility. Both engines read from the same registry. If the registry is wrong, it is wrong in one place, and fixing it fixes all engines.

Registry schema evolution must be additive by default. New fields are optional. Removing a field requires a deprecation cycle. This is the same discipline applied to public APIs.

### Error Handling: Stage-Aware Error Messages

Every error in the pipeline must include:
- The engine that produced it (e.g., `SchemaGeneratorError`)
- The input that triggered it (the `ParsedIntent` that led to this execution)
- The specific contract violation (e.g., `postcondition.DataSchema.tables must be non-empty`)
- The suggested recovery action

Generic errors like "generation failed" are unmaintainable. They require reading source code to locate the failure point. Stage-aware errors are self-diagnosing.

---

## 4. Multi-Agent Maintainability

### Agent Responsibilities Must Be Clear

The distinction between a "pipeline stage" and an "agent" requires precision. In this system:
- A **pipeline stage** is a deterministic function that transforms typed input to typed output (may invoke LLM internally).
- An **agent** is an autonomous entity that can observe state, make decisions, and invoke tools.

Not everything needs to be an agent. The Schema Generator does not need to observe the file system, make user-facing decisions, or invoke multiple tools. It is a pipeline stage. Calling it an agent adds the overhead of agent coordination without the benefit.

Agents are appropriate for the Orchestrator (coordinates the pipeline, handles user approval gates) and the Clarification Agent (manages multi-turn intent clarification before the pipeline starts). The 9 Service Engines are pipeline stages, not agents.

This distinction is not semantic pedantry. Agents that should be pipeline stages add non-determinism, debugging complexity, and failure modes that a deterministic function would not have.

### Agent Communication Protocol

For the agents that exist (Orchestrator, Clarification Agent), their communication must be typed and logged. No agent-to-agent communication through unstructured natural language. Every message has:

```typescript
interface AgentMessage {
  from: AgentId;
  to: AgentId;
  type: MessageType;     // "request" | "response" | "error"
  payload: ZodValidated; // typed payload for each MessageType
  traceId: string;       // for end-to-end trace correlation
}
```

This is the Actor Model principle from Branch 5.2 applied practically: agents communicate through typed messages, not shared mutable state.

### Debugging Agent Interactions

Branch 5.2's Actor Model enables fault isolation. When Agent X gives Agent Y bad data, the trace log shows:
1. What X sent (the exact `AgentMessage`)
2. What Y received (post-validation result)
3. Whether Y's precondition check passed

Without typed messages and trace IDs, debugging inter-agent failures requires reproducing the exact sequence of events. With them, the log is the reproduction.

### Supervision Hierarchy

The Orchestrator is the supervisor. It monitors pipeline stage completion, handles user approval gates, and retries failed stages within policy (Branch 1.2's hybrid 80/20 approach: deterministic retry logic, LLM invocation only for generation). If the Orchestrator itself fails, the CLI exits with a structured error report that includes the last successful stage and the input that triggered the failure.

No orphaned agents. No background processes that outlive the CLI invocation. LOCAL CLI constraint (주의2) enforces this: the process tree is clean, the exit code is meaningful, and the output is deterministic.

---

## 5. Long-Term Evolution Strategy

### Adding a 10th Engine: Drop-In Addition

The test of a good architecture is whether adding a 10th engine requires modifying the existing 9 engines. In the recommended architecture, it does not. Adding an "Analytics Engine" requires:
1. Defining the `AnalyticsSpec` interface.
2. Implementing `AnalyticsEngine` behind that interface.
3. Adding it to the pipeline sequence (one line in the Orchestrator).
4. Adding its inputs to the relevant upstream engine's output schema (additive change).

No existing engine's internals are touched. This is the "drop-in" property that Branch 2.1 identifies as the goal of evolutionary architecture.

### Changing LLM Provider: Swap LLMAdapter

Branch 1.1's multi-model routing and Branch 1.2's "clear separation: deterministic routing + LLM generation" both point to the same pattern: the LLM is behind an adapter.

```typescript
interface LLMAdapter {
  complete(prompt: VersionedPrompt, input: unknown): Promise<string>;
}
```

Every engine calls `LLMAdapter.complete()`. No engine calls the Anthropic SDK directly. When the provider changes (or when a specific engine needs to route to a different model for cost or quality reasons), only the adapter implementation changes. All 9 engines are unaffected.

This is the single most important structural decision for long-term maintainability of an AI-driven system. Without it, a provider migration touches every file in the codebase.

### Upgrading Document Schemas: Migration Strategy

When the `DataSchema` interface gains a new required field, all existing cassette recordings become invalid. This is a predictable migration scenario that must be handled systematically:

1. **Additive first**: New fields are optional for one minor version, then required in the next major version.
2. **Migration scripts**: When a major version bump is unavoidable, a migration script transforms old-format outputs to new-format outputs. Cassettes are re-recorded using the migration script.
3. **Schema version in the output**: Every engine output includes a `schemaVersion` field. Downstream engines check this version and reject inputs from incompatible upstream versions with a clear error.

### Supporting New SaaS Types: Template vs. Generative Approach

Branch 1.2's Handlebars/EJS templates (14-year track record) provide the maintainability anchor. Branch 1.1's generative approach provides flexibility. The correct long-term strategy is:

- **Templates for known patterns**: Authentication flows, CRUD endpoints, standard UI components. These are well-understood, high-confidence, and should not consume LLM tokens.
- **Generative for novel patterns**: Business logic that is specific to the described SaaS type, custom UI components, non-standard API shapes.

The boundary between template and generative is itself a versioned configuration, not a hardcoded condition. As new SaaS types are added, the template library grows, and the generative layer's scope narrows. This is the correct direction of travel.

### New Team Member Onboarding: 1-Day Understanding Target

The 1-day target is achievable if and only if:
1. The 9-engine pipeline diagram exists and is accurate (kept as code, not documentation).
2. Each engine's contract is readable from its interface definition alone.
3. The Registry-Driven SOT means a developer can search for any concept and find one canonical location.
4. Prompt headers answer "what does this prompt do?" without reading the prompt body.
5. Error messages name the failing engine and the violated postcondition.

If any of these five conditions is not met, onboarding takes weeks. Each condition is a specific engineering requirement, not a documentation aspiration.

---

## 6. Readability Over Cleverness

### Simple Code > Clever Abstractions

Branch 1.2 (Conservative Tech) makes the most important point in Phase 1: Handlebars has 14 years of community knowledge. JHipster has generated 200,000+ applications. These are not limitations; they are evidence that the abstractions are stable.

A custom meta-template system that generates template-generating templates is clever. It is also unmaintainable by anyone who did not write it. When it breaks at 2am, the developer who is on call is reading novel abstraction, not familiar code.

The rule is: use the simplest mechanism that achieves the requirement. If a Handlebars template achieves the requirement, do not use a generative prompt. If a typed function achieves the requirement, do not create an agent. If a Zod schema validates the requirement, do not write custom validation logic.

Branch 4.2 (Practical Tech Debt) names this "Debt Firewall": the infrastructure (CLI framework, template engine, schema validation) uses proven, boring technology. The LLM "magic" is confined to content generation, where it is irreplaceable.

### Explicit > Implicit

The single most common source of maintainability failures in complex systems is implicit behavior: "the system assumes X because we always did X." Over time, assumptions accumulate. New team members violate them without knowing. Systems break in mysterious ways.

Every assumption must be:
1. Declared as a precondition (for engine inputs).
2. Named in the prompt header (for model behavior assumptions).
3. Validated at runtime (for data shape assumptions).

No implicit conventions. No "everyone knows" rules. If it is not written down, it does not exist.

### Reserve LLM "Magic" for Where It Is Truly Necessary

The LLM is the most powerful component in this system and the most unpredictable. Expanding its scope beyond content generation trades short-term flexibility for long-term unreliability.

LLM scope should be limited to:
- Parsing ambiguous natural-language intent (where deterministic parsing fails)
- Generating application-specific business logic (where templates are insufficient)
- Generating documentation prose (where templates produce unreadable output)

LLM scope should explicitly exclude:
- Routing decisions (use typed conditions)
- Validation logic (use Zod schemas)
- File assembly (use deterministic Assembler)
- Error message generation (use typed error classes)

Branch 1.2's "80% rule-based, 20% LLM" is not a conservative compromise. It is the correct answer for a system where determinism, debuggability, and reproducibility are primary values.

---

## 7. Maintainability Scorecards Per Engine

Each engine is scored on five dimensions: Interface Clarity (IC), Testability (T), Replaceability (R), Error Diagnosability (ED), and Prompt Readability (PR). Scale: 1-5.

| Engine | IC | T | R | ED | PR | Total | Key Risk |
|---|---|---|---|---|---|---|---|
| 1. Intent Parser | 4 | 3 | 4 | 3 | 3 | 17/25 | Multi-turn ambiguity hard to test deterministically |
| 2. Schema Generator | 5 | 4 | 5 | 4 | 4 | 22/25 | Well-defined inputs; highest ROI for cassette testing |
| 3. API Planner | 5 | 5 | 5 | 5 | 4 | 24/25 | OpenAPI as output format eliminates ambiguity |
| 4. Auth Engine | 4 | 4 | 4 | 4 | 3 | 19/25 | Security decisions require human-readable rationale |
| 5. UI Generator | 3 | 3 | 4 | 3 | 3 | 16/25 | Highest LLM surface area; most prone to drift |
| 6. Business Logic | 3 | 3 | 3 | 3 | 2 | 14/25 | Most domain-specific; prompt readability is highest risk |
| 7. Test Generator | 4 | 5 | 5 | 4 | 4 | 22/25 | Meta-testing: generated tests validate the generator |
| 8. Infra Planner | 5 | 4 | 5 | 5 | 4 | 23/25 | Topology is well-typed; deployment decisions are auditable |
| 9. Doc Engine | 4 | 4 | 5 | 4 | 5 | 22/25 | Output is prose; quality subjective but schema valid |

**Engines requiring highest maintainability investment**: Business Logic Engine (14/25) and UI Generator (16/25). These have the highest LLM surface area, the most domain-specific prompts, and the greatest risk of prompt spaghetti. Both require dedicated golden-output regression tests, detailed prompt headers, and explicit scope constraints in their contracts.

**Engines with strongest baseline maintainability**: API Planner (24/25) and Infra Planner (23/25). Both benefit from industry-standard output formats (OpenAPI, infrastructure-as-code schemas) that serve as natural contracts and are independently validatable.

---

## 8. Conclusion: Maintainability-First Recommended Approach

### Architecture Choices Optimized for Long-Term Health

The recommended architecture is the combination of:
- **Branch 2.1's Day-1 interfaces** (evolution without rewrites)
- **Branch 2.2's formal contracts** (preconditions/postconditions for every inter-engine communication)
- **Branch 5.2's classical principles** (Information Hiding, Separation of Concerns, Design by Contract)
- **Branch 1.2's boring infrastructure** (Handlebars/EJS templates for deterministic generation)
- **Branch 4.2's Debt Firewall** (LLM magic contained to content generation)

This is not the most innovative architecture in Phase 1. It is the most *navigable* one.

### Testing Strategy for Sustained Quality

Three-layer testing pyramid:
1. **Unit (Cassette Pattern)**: Every engine's prompt tested against recorded responses. CI completes in < 60 seconds. Branch 3.2.
2. **Contract (Schema Validation)**: Every inter-engine handoff validated by Zod. Catches interface drift before it reaches integration. Branch 3.2.
3. **End-to-End (Golden Output)**: 5-10 representative full-pipeline runs with known-good golden outputs. Run before any major release. Branch 3.2.

Property-based testing (fast-check, Branch 3.2) for the deterministic components (Assembler, Registry lookups). This catches edge cases that hand-written tests miss.

Branch 4.1's 200+ test target is achievable and necessary. It is not overhead; it is the mechanism by which prompt changes, schema migrations, and engine replacements are made safely.

### Prompt Management as First-Class Engineering Discipline

The single most common failure mode in AI systems is treating prompts as disposable configuration. The recommended approach elevates prompts to the same status as production code:
- Version-controlled with semantic versioning
- Reviewed before merging (same process as code review)
- Tested with cassettes and golden outputs
- Documented with purpose, inputs, outputs, and assumptions
- Migrated with explicit scripts when major versions change

This is not bureaucracy. It is the mechanism by which a 2-person team's prompt library remains understandable to a 10-person team 18 months later.

### What We Sacrifice

**Initial development speed**: The interface-first, contract-heavy approach adds approximately 30-40% to initial implementation time compared to Branch 3.1's hot-reload rapid development. The first engine takes longer to ship.

**Exploratory flexibility**: When the "right" output schema for the Schema Generator is unclear, being forced to commit to a TypeScript interface before implementation is constraining. This constraint is a feature, not a bug — but it feels like friction early on.

**Cutting-edge model capabilities**: Branch 1.1's multi-model routing and Branch 5.1's Constitutional AI self-correction are more powerful in isolation. Constraining LLM scope to 20% of the pipeline means some capabilities are deliberately unused.

### What We Gain

**Team scalability**: A team of 10 can work on 10 different engines simultaneously because the interfaces are agreed upon. Without interfaces, two developers working on adjacent engines create integration debt that a later developer pays.

**Debuggability**: When the generated SaaS is wrong, the trace log names the failing engine, the violated contract, and the input that triggered the failure. Debugging time drops from hours to minutes.

**Evolution capacity**: Adding a 10th engine is a drop-in. Changing LLM providers touches one file. Upgrading document schemas follows a known migration path. These are not hoped-for properties; they are structural guarantees of the interface-first design.

**New developer confidence**: A developer who joins month 12 reads the 9-engine pipeline diagram, understands the system architecture in an hour, picks an engine with a 14/25 maintainability score, reads its prompt headers, and begins contributing before the end of day 1. This is not aspirational; it is the concrete outcome of the five onboarding conditions described in Section 5.

### The Non-Negotiable

There is one requirement that supersedes all tradeoffs: **the system must be correct before it is fast**. A SaaS generator that produces broken applications quickly is worse than one that produces correct applications slowly.

The maintainability-first architecture ensures that "correctness" is measurable (through contract validation and golden-output tests), that regressions are detectable (through cassette testing), and that failures are diagnosable (through stage-aware error messages).

Speed can be improved after correctness is established. The reverse is not true.

Branch 3.1's < 30-second cycle time is a valid optimization target once the system is correct. Branch 1.1's multi-model routing is a valid performance optimization once the LLMAdapter interface is in place. Branch 4.2's phased 30%→20%→10% debt reduction is a valid maintenance strategy once the Debt Firewall is established.

Maintainability is not the enemy of these optimizations. It is the prerequisite.

---

## Summary Table: Branch Contributions to Maintainability

| Branch | Core Contribution | Adoption |
|---|---|---|
| 1.1 Core Tech Aggressive | LLMAdapter abstraction, Registry-Driven SOT | Full — adapter + registries |
| 1.2 Core Tech Conservative | Boring infrastructure, 80/20 deterministic/LLM split | Full — foundational principle |
| 2.1 Arch Evolutionary | Day-1 interfaces, signal-based triggers | Full — interface-first |
| 2.2 Arch Big Bang | Formal contracts, engine-level specification | Partial — contracts yes, 8500 LOC no |
| 3.1 Dev Workflow Rapid | Hot-reload cycle | Partial — dev tooling only |
| 3.2 Dev Workflow Robust | Cassette pattern, FSM, contract testing | Full — testing backbone |
| 4.1 Tech Debt Minimized | Prompt versioning, hexagonal architecture | Full — prompt discipline |
| 4.2 Tech Debt Practical | Debt Firewall, generator vs tooling distinction | Full — scope containment |
| 5.1 Theory Modern | Constitutional AI self-correction | Partial — for Intent Parser only |
| 5.2 Theory Classical | Information Hiding, Separation of Concerns, Design by Contract | Full — architectural foundation |

---

*Discussion Moderator: Code Quality & Long-Term Maintainability*
*Phase 2 of 4 — Pre-work for PRD.md*
*Word count: ~3,800*
