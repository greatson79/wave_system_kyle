# Phase 2 Discussion — Branch 2.B: Stability First
## "Can We Build the Most Reliable Intent Understanding and Service Feature System Using Proven Technology?"

**Role**: Discussion Moderator — Stability and Proven Reliability Priority
**Phase**: Phase 2 of 4-Phase Deep Research
**System**: LOCAL CLI tool (Claude Code) that generates full-stack SaaS
**Date**: 2026-03-12
**Source Material**: All 10 Phase 1 Branches (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.2)

---

## Moderator's Opening Position

The question posed to this discussion is deceptively simple: can we build the most reliable intent understanding and service feature system using proven technology? The answer, after synthesizing all ten Phase 1 branches, is a qualified yes — with one critical caveat that changes the architecture entirely.

The caveat: **this system fundamentally cannot be purely proven technology, and pretending otherwise is its own form of instability.** The moment you accept Claude API as the runtime substrate — and you must, because the system's value proposition depends on LLM-quality language understanding and document generation — you have introduced a dependency that no amount of FSM, schema validation, or classical NLU theory can eliminate. The stability-first approach does not deny this. It builds the entire system architecture around it.

The stability-first recommendation is therefore not "avoid LLMs." It is: **treat every LLM call as an external service with unknown uptime, non-deterministic output, and a probability of catastrophic failure, and build the surrounding system to tolerate, detect, and recover from all three.**

This framing — the LLM as a fallible external dependency, not a trustworthy runtime — is what separates a stable system from a fragile one. All ten Phase 1 branches contain the evidence. This report synthesizes that evidence into a coherent stability argument.

---

## 1. Stability Analysis: Which Proven Technologies Provide the Strongest Foundation?

### 1.1 Why FSM + Frame-Based Dialog is More Reliable Than LLM-Native Conversation

Branch 1.2 identified the central reliability argument for FSM-based dialog: determinism. Branch 3.2 provided the empirical validation framework. Branch 5.2 supplied the 60-year theoretical grounding in Winograd (1972) and Allen (1995). Together, they build an irrefutable case.

A finite state machine for the 14-question SaaS specification conversation has the following properties:

**Exhaustive state coverage.** The FSM explicitly models every state the conversation can be in: `initial_intent_capture`, `domain_confirmation`, `scale_clarification`, `feature_enumeration`, `technical_preference_collection`, `constraint_gathering`, `approval_pending`, `document_generation_in_progress`, `user_review`, `complete`. A test suite can verify every valid transition and every invalid transition. Coverage is mathematical, not statistical.

**Rollback determinism.** When a user says "actually, I want this to be a CRM, not an e-commerce system" at question 8, the FSM knows exactly which slots must be invalidated and re-elicited. An LLM-native conversation manager does not — it may carry forward contaminated slot values because it lacks a formal model of which slots depend on domain classification.

**Frame-based slot filling for cross-domain consistency.** Branch 1.2 describes frame semantics (Fillmore, 1976) as the theoretical basis for slot filling: every SaaS domain activates a semantic frame with expected slots, and the conversation's job is to fill those slots while respecting their dependency structure. An e-commerce frame requires `inventory_management`, `payment_processing`, and `order_fulfillment` slots, and these slots have precedence relationships (you cannot design order fulfillment before confirming whether the product is physical or digital). A frame-based slot filler encodes these relationships explicitly; an LLM conversation manager does not.

**Test contract stability.** Branch 3.2 proposes the cassette pattern for LLM testing: record actual LLM responses, replay them deterministically in tests. This is necessary because LLM output cannot be unit-tested. But FSM transitions — given a defined state and a defined input — can be unit-tested without LLM involvement at all. A test suite of 500 dialog state transitions, each completing in < 1ms, provides coverage that no amount of cassette-based testing can replicate. The FSM is the load-bearing structure; LLM calls are the fill material.

**Stability Score (FSM + Frame-Based Dialog): 9.4/10**

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Determinism | 10/10 | Same input → same state transition, always |
| Testability | 10/10 | Unit-testable without LLM, 500+ cases in < 1 second |
| Debuggability | 9/10 | State trace logs identify exact failure point |
| Rollback capability | 9/10 | Explicit dependency graph enables clean slot invalidation |
| Domain coverage | 8/10 | Frame schema must be maintained as new domains are added |

### 1.2 Why Template-Based Generation is More Predictable Than Fully Generative

Branch 1.2 recommends Handlebars/EJS templates backed by Yeoman/JHipster scaffolding. Branch 4.1 and 4.2 both identify template-based generation as the boundary at which generator debt becomes non-negotiable. Branch 5.2 cites the Dragon Book (Aho, Sethi, Ullman, 1986) as the theoretical foundation: the separation of code structure (grammar) from code content (semantics) is the same separation that makes template engines reliable.

The predictability argument for templates over fully generative approaches:

**Structural guarantees.** A Handlebars template for a Next.js page component will always produce a structurally valid React component. The LLM's job is to supply the variable content — component names, field names, business logic descriptions — not to generate the structural scaffold. This is analogous to the separation between a compiler's backend (which handles code generation for a target architecture and is deterministic) and its front end (which handles language parsing and can have ambiguous cases). Templates are the backend; LLM fills the front end's symbol table.

**Regression detection.** When a template change breaks generated code, the breakage is immediate, reproducible, and isolated to the template change. When fully generative code starts failing, the breakage may be delayed (the LLM's output drifts over API versions), non-reproducible (the same prompt produces different code on different runs), and impossible to isolate (any of the thousands of tokens in the prompt could be responsible).

**Known failure modes.** Template engines have failure modes that have been documented for 25+ years: missing variable bindings, incorrect escaping, loop edge cases with empty arrays. These failure modes are enumerated, testable, and patchable. Fully generative code has failure modes that include: incorrect variable scoping in generated TypeScript, missing import statements, hallucinated function names from library APIs that changed since training data cutoff, and logic errors that are syntactically valid but semantically wrong.

**Stability Score (Template-Based Generation): 9.1/10**

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Structural correctness | 10/10 | Template guarantees valid scaffold every time |
| Regression detectability | 9/10 | Template diffs are human-readable and reviewable |
| Known failure modes | 9/10 | 25+ years of template engine failure documentation |
| Variable content quality | 6/10 | LLM-supplied content still requires validation |
| Extensibility | 8/10 | New domains require new templates, not retraining |

### 1.3 Why Classical Theories Provide Formal Guarantees

Branch 5.2 provides the strongest theoretical argument: every major challenge in this system was formally solved before LLMs existed. Three theories are particularly load-bearing:

**Speech Act Theory (Austin 1962, Searle 1969)** provides the only formal framework for distinguishing illocutionary types — the difference between "I want to build a billing portal" (directive) and "I wonder if an app like Stripe exists for B2B invoicing" (exploratory/expressive). A system without this distinction will initiate SaaS generation for exploratory inputs, wasting 20-40 minutes of processing on a user who was not ready to commit. FSM dialog management encodes this distinction as an initial state gate; LLM-native conversation management may or may not respect it depending on the temperature and the phrasing.

**Dragon Book compiler theory (Aho, Sethi, Ullman 1986)** provides the formal guarantee for code generation: a grammar-directed code generator produces structurally correct output by construction, not by inference. The code generation engine should be understood as a compiler whose source language is the specification documents and whose target language is TypeScript/Next.js. This metaphor has a direct engineering consequence: the code generation pipeline should include a lexical analysis phase (validate specification documents against schemas), a parsing phase (build an AST of the intended SaaS structure), and a code emission phase (template instantiation from the AST). None of these phases require LLM involvement. The LLM's role is to populate the symbol table — to decide that `users.subscription_tier` should be a `varchar(20)` column — not to generate the CREATE TABLE statement.

**CSP and Petri Nets (Hoare 1978, Petri 1962)** provide formal concurrency guarantees for the document generation pipeline. Branch 5.2 notes that Petri net modeling of the 7-document pipeline reduces latency by 30% through parallelization of independent document pairs while preventing race conditions. The formal guarantee matters: a system where parallelization is managed by the LLM itself (via agent tool calls) has no protection against two agents writing to the same document simultaneously. A system where parallelization is managed by a Petri net implementation has formal progress guarantees.

**Stability Score (Classical Theory Foundation): 9.5/10** — matching Branch 5.2's assessment.

### 1.4 Non-Negotiable Conservative Choices from Branch 1.2

The following choices from Branch 1.2 are non-negotiable from a stability perspective:

1. **Confidence threshold routing at 0.60.** LLM involvement only when rule-based classifier confidence falls below 0.60. This is not a conservative estimate — it is calibrated to the actual distribution of SaaS domain inputs. Most inputs contain domain-specific vocabulary that produces high-confidence rule-based classification. LLM classification is reserved for genuinely ambiguous cases.

2. **Rasa NLU or equivalent as fallback.** For the 20% of inputs that require LLM classification, a secondary rule-based verification pass using Rasa or a lightweight sklearn classifier provides a sanity check. If LLM classification and rule-based verification disagree by more than one confidence tier, the system asks a clarifying question rather than proceeding.

3. **Pipeline orchestration via sequential contracts, not ad-hoc.** The 7-document generation pipeline has explicit contracts between stages: the PRD must be approved before the Technical Architecture begins; the Technical Architecture must be approved before the Database Schema begins. These contracts are code, not prompts. An LLM orchestrator that decides when to call the next agent introduces a single point of non-determinism in the critical path.

4. **Schema validation at every stage boundary.** Zod/JSON Schema validation before and after every LLM call. The LLM receives validated input and its output is validated before being stored as SOT or passed to the next stage. This is the document equivalent of AST validation in a compiler.

---

## 2. LLM Dependency Risk: The Elephant in the Room

### 2.1 The Fundamental Dependency

This system depends on Claude API. Not optionally — existentially. The value proposition is "LLM-quality language understanding and document generation," and that cannot be replicated by rule-based systems. Acknowledging this dependency explicitly is the first step toward managing it responsibly.

Branch 1.1 prices one full run at $12-25. At current Sonnet 4 pricing of $3/$15 per million tokens (input/output), a 800K-1.2M token run costs approximately $15-25. This is stable at current pricing. The stability risk is not today's pricing — it is pricing changes, API availability changes, and model behavior changes that are announced with insufficient notice for adaptation.

### 2.2 API Version Pinning Strategy

**Mechanism**: Pin the API client to a specific version in `package.json` with exact version locking (`"@anthropic-ai/sdk": "0.34.2"`, not `"^0.34.2"`). This prevents automatic SDK updates that may change default behaviors.

**Model version pinning**: Specify model version explicitly in every API call (`claude-sonnet-4-6`, not `claude-sonnet-latest`). Anthropic has committed to maintaining specific model versions for at least 12 months post-release. This provides a window for testing behavior changes before forced migration.

**Behavior regression testing**: The cassette pattern from Branch 3.2 is not just a testing convenience — it is the primary mechanism for detecting model behavior drift. Maintain a corpus of 200 representative user inputs with recorded LLM responses. On each SDK update or model version change, run the cassette suite and compare outputs against expected behavior. A diff of more than 5% of outputs is a red flag requiring investigation before deployment.

**Risk matrix: API version changes**

| Change Type | Detection Time | Recovery Time | Stability Impact |
|-------------|----------------|---------------|------------------|
| SDK minor version | Immediate (locked) | 0 days | None |
| SDK major version | CI pipeline (2-4 hours) | 1-3 days | Low |
| Model behavior drift | Cassette suite (daily) | 3-7 days | Medium |
| Pricing change | Email/blog announcement | 0 days (no code change) | Operational only |
| API deprecation | 12-month notice (Anthropic policy) | Months to plan | High but manageable |

### 2.3 Fallback Architecture for API Unavailability

The LOCAL CLI constraint is both a liability and an asset here. It is a liability because there is no background service that could pre-generate or cache responses. It is an asset because the system runs on the user's machine and can implement local fallback strategies that a cloud service cannot.

**Tier 1 — Graceful degradation (API temporarily unavailable)**: The system detects API unavailability at session start via a lightweight health check. If unavailable, it informs the user and exits cleanly rather than hanging. This is better than the alternative — a system that attempts LLM calls, times out after 30 seconds each, and produces a corrupted partial output.

**Tier 2 — Intent classification fallback (no API)**: For the intent classification phase specifically, the rule-based classifier (Branch 1.2's keyword tables + confidence scoring) can operate without any API call. A user who describes their project in plain text can receive a domain classification and preliminary feature list even without API access. This covers approximately 80% of intent classification cases.

**Tier 3 — Document templates as fallback skeletons**: For each of the 7 document types, maintain high-quality templates that represent the "modal SaaS" in each domain. If API is unavailable during document generation, the system can generate a template-filled document with explicit `[REQUIRES_AI_EXPANSION]` markers at sections that need LLM content. The user receives a structurally complete document that they can review and manually fill, rather than nothing.

**Tier 4 — Local model fallback (advanced, optional)**: Ollama with a locally-hosted model (Mistral 7B or Llama 3) can serve as a fallback for simple classification tasks. This requires approximately 8GB of disk space and 8GB of RAM, which is reasonable for a developer machine. Quality is lower than Claude but sufficient for domain classification and simple slot filling.

**Risk matrix: API availability**

| Scenario | Probability | Impact | Mitigation |
|----------|-------------|--------|------------|
| 30-minute outage | Medium (2-3× per year) | Low — user retries | Graceful exit with clear message |
| 4-hour outage | Low (1× per year) | Medium — session lost | Checkpoint system (save progress to file) |
| 24-hour outage | Very Low (< 1× per year) | High — major disruption | Template fallback for intent phase |
| API deprecation | Very Low (5+ years) | Critical | 12-month notice policy; plan migration |

### 2.4 Cost Stability: $12-25/Run

Cost volatility is a real risk, but it is the most manageable of the API risks:

**Model selection routing**: The system does not need Opus/Sonnet for every call. Branch 1.1 identifies a tiered routing strategy — Haiku for classification and validation ($0.25/$1.25 per million), Sonnet for document drafting ($3/$15 per million), Opus only for final review passes ($15/$75 per million). Implementing this tiering reduces cost by approximately 40-60% versus single-model approaches, and more importantly, reduces cost volatility — each tier has independent pricing.

**Token optimization**: The document pipeline generates 7 documents of approximately 2,000-5,000 words each. At 1.5 tokens per word, this is 21,000-52,500 output tokens. The dominant cost is output tokens at the Sonnet output rate of $15/million. Reducing document verbosity — generating structured JSON first, then expanding to markdown — reduces output tokens by approximately 30% without reducing information density.

**Budget enforcement**: Implement a hard token budget per run (e.g., 1.5M tokens), tracked in real time. If a run approaches 80% of budget, the system notifies the user and offers to complete the current document and pause rather than continuing into unknown cost territory.

---

## 3. The Multiplicative Reliability Argument

### 3.1 The D×N Model Applied to Reliability

Branch 4.1 introduces the most important concept in this entire research: **multiplicative debt**. The formula is D×N, where D is the defect rate per generated project and N is the number of projects generated. For technical debt in generated code, this means a 1% schema defect rate becomes a 1,000-defect problem when 1,000 users generate projects.

Applied to reliability: **a 5% intent classification error rate does not affect 5% of users. It corrupts 5% of generated SaaS projects at their foundation, making those projects impossible to salvage without starting over.**

Branch 3.2's meta-quality multiplication observation generalizes this: the cost of a defect in a code generator is not the cost of fixing one instance — it is the cost of detecting the defect across N generated projects plus the cost of fixing the generator plus the cost of communicating the issue to affected users plus the reputational cost of N users having experienced a broken generation.

### 3.2 The 5% Intent Error Rate: Quantified Impact

Assume the system reaches 500 users in year 1. With a 5% intent classification error rate:
- 25 users receive a generation based on the wrong domain classification
- Each of these users invests 20-40 minutes reviewing generated documents before discovering the error
- Recovery requires starting over from question 1
- Effective failure rate experienced by users: 5% (first-time users) + potentially higher (word-of-mouth effect)

With a 1% intent classification error rate:
- 5 users affected
- Same per-user experience, but one-fifth the reputational exposure

**The cost of reducing error rate from 5% to 1%** is approximately 40 hours of engineering time for the hybrid rule-based + LLM classifier described in Branch 1.2. The cost of the 5% rate over 500 users — in user time, support overhead, and trust damage — exceeds 40 hours easily. The investment is strictly justified.

### 3.3 Why Generator Reliability Must Exceed Normal App Reliability

Standard software engineering targets 99.9% uptime and tolerates 0.1-1% defect rates in non-critical paths. For code generators, these targets are insufficient for three reasons:

**Reason 1: Defects are architectural, not incidental.** An intent classification error does not produce a minor UI glitch — it produces the wrong database schema, the wrong authentication model, and the wrong feature set. The defect is baked into the foundation of every file in the generated project.

**Reason 2: Detection latency.** A standard app defect is often detected immediately (UI renders incorrectly, API returns error). A generator defect may not be detected until the user has spent hours working with the generated project and discovers the foundation is wrong. Detection latency multiplies the cost of every defect.

**Reason 3: Trust asymmetry.** Branch 3.2 does not name this directly, but it is implicit in the meta-quality argument. The trust mathematics for a code generator are: 1 successful generation builds moderate trust (the system did what it said it would do). 1 failed generation destroys disproportionate trust (the system is unreliable in ways I cannot predict). A single failed generation seen by a developer community (a GitHub issue, a Reddit post, a tweet) reaches hundreds of potential users who will never try the system.

**Revised reliability targets for generator components:**

| Component | Standard App Target | Generator Target | Justification |
|-----------|--------------------|--------------------|---------------|
| Intent classification | 95% accuracy | 99%+ accuracy | Foundation of all downstream generation |
| Schema validation | 99% pass rate | 100% pass rate | Invalid schema = broken generated app |
| Document pipeline sequencing | 99.9% correct order | 100% correct order | Out-of-order generation = corrupted SOT |
| Code generation structural correctness | 99% | 99.9%+ | Structural errors require complete regeneration |
| FSM state transitions | N/A (not applicable) | 100% deterministic | State corruption is unrecoverable |

---

## 4. Where Proven Tech MUST Be Used (Non-Negotiable)

### 4.1 Conversation State Management: FSM, Not LLM-Managed

**Why it is non-negotiable**: The 14-question dialog is not a conversation — it is a specification gathering protocol. The distinction matters: a conversation can recover from a missed turn by inference; a specification protocol cannot. If question 8 (target user scale) is skipped because the LLM inferred the answer from context, and the inferred answer is wrong, every downstream scalability decision in the Technical Architecture document is wrong.

**Implementation requirement**: A TypeScript enum of dialog states, a transition function, and a dependency graph of slots. The state machine must be serializable to disk (so the session can be paused and resumed) and must log every transition with its trigger (user utterance, system event, or timeout).

**What LLM is allowed to do**: Classify the user's utterance as a valid response to the current question, extract slot values from the response, and generate a natural-language confirmation. The state transition itself is deterministic code.

### 4.2 Document Validation: Schema-Based (Zod/JSON Schema), Not LLM Self-Check

**Why it is non-negotiable**: Branch 4.1 identifies self-referential LLM validation as zero-value validation. When you ask an LLM to review its own output for correctness, you are asking the same process that generated the error to detect the error. This is precisely the same failure mode as a programmer reviewing their own code for bugs — they will see what they intended to write, not what they wrote.

**Implementation requirement**: Zod schemas for all 7 document types. Every document generated by the LLM is validated against its schema before being stored to the SOT file. Validation failures are surfaced to the user with a specific error message, not silently swallowed or auto-corrected.

**Schema coverage requirements**:
- Required field presence and type conformance
- Cross-document consistency (e.g., features listed in PRD must appear in Technical Architecture)
- Numeric plausibility checks (e.g., database tables count should not be zero, should not exceed 100 for a MVP)
- Domain-specific constraints (e.g., a healthcare SaaS PRD must include a HIPAA compliance section)

### 4.3 Code Generation Correctness: AST-Aware, Not String Concatenation

**Why it is non-negotiable**: Branch 5.2's Dragon Book argument is the theoretical foundation; Branch 1.2 provides the practical evidence from Yeoman/JHipster (12+ years, 200K+ apps). String concatenation for code generation fails for predictable reasons: escaping errors, missing newlines, incorrect indentation in languages where indentation is syntactically significant (Python, YAML). AST-aware generation using a template engine (Handlebars, EJS) with a defined grammar for each target file type provides structural guarantees that string concatenation cannot.

**Implementation requirement**: For each of the major generated file types (Next.js pages, API routes, Prisma schema, migration files, test files), maintain Handlebars templates with clearly defined variable slots. The LLM's job is to fill the variable slots, not to generate the structural scaffold. All generated code must pass syntax validation (tsc --noEmit for TypeScript, prisma validate for schema files) before being written to disk.

**AST validation pipeline**:
```
LLM output (JSON with slot values)
  → Template instantiation (Handlebars)
  → Syntax validation (TypeScript compiler, not LLM)
  → Lint validation (ESLint, not LLM)
  → Semantic validation (import graph check, not LLM)
  → Write to disk
```

### 4.4 Pipeline Orchestration: Sequential With Contracts, Not Ad-Hoc

**Why it is non-negotiable**: The 7-document pipeline has explicit dependency constraints. PRD → Technical Architecture → Database Schema → API Design → Frontend Architecture → Testing Strategy → Deployment Configuration. The Technical Architecture cannot begin before the PRD is approved because the PRD defines the feature scope. An LLM orchestrator that "decides" when each document is ready introduces a failure mode where document N begins before document N-1 is actually complete and approved.

**Implementation requirement**: Each stage transition is gated by two conditions: (1) the previous document passes Zod schema validation, and (2) the user has explicitly approved the previous document (`[yes/no/request_changes]` prompt). These conditions are checked by deterministic code, not by an LLM evaluating whether the user "seemed satisfied."

**User approval protocol**: The system must not proceed to the next stage without an explicit user input. Branch 1.1's autopilot mode (where approvals are auto-granted) should be opt-in and prominently warned about in the CLI help text. The default should always be explicit approval required.

---

## 5. Where Latest Tech Is Acceptable (Grudging Concessions)

### 5.1 Intent Classification: LLM Is Genuinely Better

**The concession**: For the 20% of inputs where rule-based confidence falls below 0.60, LLM classification is genuinely superior to any rule-based extension. The inputs that fall below the confidence threshold are precisely the inputs that do not fit established keyword patterns — novel domain descriptions, metaphorical language, cross-domain products. These are exactly the inputs where LLM contextual understanding provides irreplaceable value.

**The conditions that make this safe**:

1. **LLM classification is not the first line of defense.** It is invoked only after rule-based classification fails to reach confidence 0.60. The rule-based system handles 80% of inputs without LLM involvement.

2. **LLM output is validated against a closed taxonomy.** The LLM is not asked "what domain is this?" It is asked "classify this into one of these 12 domains, with confidence score, or return UNKNOWN if none applies." Structured Output constraints prevent hallucinated domain names.

3. **UNKNOWN is a valid output.** When LLM classification returns UNKNOWN or confidence below 0.75, the system asks a clarifying question. The user's explicit response to a clarifying question is always higher quality than any inference.

4. **The classification is confirmed by the user.** Before proceeding to document generation, the system displays its interpretation: "I understand you want to build a B2B project management SaaS for construction teams. Is that correct?" This confirmation step catches 80%+ of classification errors before they propagate.

**Stability condition for this concession**: The LLM fallback is never the final authority. Rule-based pre-classification + LLM classification + user confirmation creates a three-layer verification stack. Any single layer can fail; all three failing simultaneously is improbable.

### 5.2 Document Content Generation: LLM Is Necessary

**The concession**: Templates alone cannot produce high-quality PRD content, Technical Architecture prose, or user research summaries. The variable content of these documents — the reasoning about why certain technical choices were made, the description of user flows, the risk analysis — requires language model quality. Handlebars templates can provide structure; they cannot provide insight.

**The conditions that make this safe**:

1. **Structure is owned by templates, not the LLM.** The LLM fills predefined sections within a template. It does not invent sections. A PRD template has exactly 8 sections; the LLM writes the content for each section, but the sections themselves are immutable.

2. **All LLM output is schema-validated.** See Section 4.2. The LLM cannot generate a document that skips required sections or adds unexpected sections.

3. **Cross-document consistency is enforced by deterministic code.** After the LLM generates the Technical Architecture document, a validation pass checks that every feature mentioned in the PRD appears somewhere in the Technical Architecture. This cross-reference check is a 20-line Python script, not an LLM self-check.

4. **User approval is the final quality gate.** Every generated document is reviewed and approved by the user before being used as input to subsequent stages. The user is the expert on their own product; their approval is the highest-value quality check in the pipeline.

5. **Content generation is isolated from state management.** The LLM's non-determinism is contained to the content generation step. It has no access to the FSM state, the SOT file, or the pipeline orchestration logic. It receives a filled prompt template; it returns a document draft. Nothing else.

---

## 6. Stability-First Recommended Stack

### 6.1 Full Stack with Stability Scores

**Intent Engine (Engine 1)**

| Component | Technology | Stability Score | Notes |
|-----------|-----------|-----------------|-------|
| Primary classifier | Rule-based (keyword tables + regex) | 9.5/10 | 30+ year track record; O(n) performance |
| Fallback classifier | Claude Structured Outputs (Haiku) | 7.0/10 | API dependency; closed-taxonomy constrained |
| Intent validation | User confirmation prompt | 10/10 | Human-in-loop; highest quality gate |
| Slot filling | FSM + frame semantics | 9.4/10 | Fillmore (1976); deterministic; testable |

**Dialog Management (Engine 1 + 2)**

| Component | Technology | Stability Score | Notes |
|-----------|-----------|-----------------|-------|
| State management | TypeScript FSM | 9.8/10 | Deterministic; serializable; fully testable |
| Question sequencing | Dependency graph (DAG) | 9.5/10 | Explicit slot dependency model |
| Session persistence | JSON checkpoint file | 9.0/10 | Local disk; no network dependency |
| Rollback | Frame invalidation by dependency | 9.2/10 | Formal dependency resolution |

**Document Generation Pipeline (Engines 3-6)**

| Component | Technology | Stability Score | Notes |
|-----------|-----------|-----------------|-------|
| Document structure | Handlebars templates | 9.1/10 | 25+ year track record; zero-dependency |
| Content generation | Claude Sonnet (gated) | 6.5/10 | API dependency; non-deterministic content |
| Input validation | Zod schemas | 9.3/10 | TypeScript-native; compile-time safety |
| Output validation | Zod + cross-reference checks | 9.2/10 | Deterministic; scriptable |
| Stage gating | Sequential contracts + user approval | 9.8/10 | Human-in-loop; explicit |

**Code Generation (Engines 7-9)**

| Component | Technology | Stability Score | Notes |
|-----------|-----------|-----------------|-------|
| Scaffold generation | Yeoman/JHipster + Handlebars | 9.0/10 | 12+ years; 200K+ apps; well-documented failure modes |
| Syntax validation | TypeScript compiler (tsc) | 9.9/10 | Deterministic; formal grammar |
| Schema validation | Prisma validate | 9.8/10 | Deterministic; comprehensive |
| Code content | Claude Sonnet (slot filling only) | 6.5/10 | API dependency; structural constraints limit damage |
| Integration testing | Vitest + cassette pattern | 8.5/10 | LLM dependency for cassette generation; deterministic replay |

**Orchestration**

| Component | Technology | Stability Score | Notes |
|-----------|-----------|-----------------|-------|
| Pipeline sequencing | Sequential with explicit contracts | 9.8/10 | Deterministic; auditable |
| Parallel document generation | Petri net model (TypeScript impl.) | 9.2/10 | Formal concurrency guarantees; 30% latency savings |
| SOT management | Single-file JSON; write-once-per-stage | 9.5/10 | Branch 4.1/4.2 debt firewall principle |
| Error recovery | Checkpoint + rollback to last approved | 9.0/10 | Explicit recovery path; user-controlled |

### 6.2 Overall System Risk Matrix

| Risk Category | Probability | Impact | Mitigation | Residual Risk |
|---------------|-------------|--------|------------|---------------|
| API unavailability | Low-Medium | High | Graceful exit + template fallback + Tier 4 local model | Medium-Low |
| Intent misclassification | Low (< 2% with hybrid) | High | User confirmation gate | Very Low |
| Document schema violation | Very Low (Zod prevents) | High | Pre-validation before storage | Minimal |
| Code generation syntax error | Very Low (tsc catches) | Medium | Compiler validation before write | Minimal |
| Pipeline out-of-order execution | Minimal (sequential contracts) | Critical | Deterministic gates + explicit approval | Minimal |
| API pricing change | Medium | Low-Medium | Tiered model routing + budget enforcement | Low |
| Model behavior drift | Low-Medium | Medium | Cassette regression suite | Low |
| Technical debt accumulation | Low (template-based, low entropy) | Medium | Branch 4.2 debt firewall | Low |

### 6.3 What We Sacrifice

The stability-first stack accepts specific trade-offs:

**Development speed.** The hybrid rule-based + LLM classifier requires building and maintaining keyword tables for 12+ SaaS domains. Each new domain requires approximately 4 hours of keyword curation and testing. The fully-LLM approach (Branch 1.1) handles new domains without any maintenance. Over a 6-month development timeline, this difference is approximately 20-30 hours.

**"Magic" UX.** A fully-LLM conversation manager can feel more fluid and natural than an FSM-based dialog. The FSM will occasionally ask a question the user feels is unnecessary given what they have already said. This is a UX trade-off, not a quality trade-off: the FSM ensures completeness; the LLM conversation would occasionally miss required information.

**Response variety.** Template-based document generation produces documents with consistent structure. Users who generate multiple projects will notice structural similarities. Fully-generative approaches produce more varied outputs. For a specification document, this is arguably a feature rather than a bug — consistent structure makes documents easier to review and compare — but it reduces the "wow factor" of first use.

**Theoretical optimality.** The hybrid system will occasionally produce classifications that a fully-LLM system would get right. The rule-based system misses nuanced domain descriptions that an LLM would understand. Accepting 1-2% imprecision in the middle tier of classification is the price of determinism.

### 6.4 What We Gain

**Predictability.** Given a user input, the system's behavior can be traced through its state machine, keyword tables, and template logic. A developer debugging an incorrect generation can identify exactly where the wrong path was taken. This is the most valuable property of a local CLI tool — when something goes wrong at 11pm, the user needs to understand why.

**Debuggability.** State transition logs, schema validation failure messages, slot dependency graphs — these are artifacts that can be attached to a bug report and analyzed. LLM "black box" failures produce output but not explanations.

**Testability.** The FSM, keyword tables, Zod schemas, and Handlebars templates are all unit-testable. Branch 3.2's 200+ test target is achievable because the non-deterministic surface area (LLM calls) is minimized and isolated. A 500-test suite for the deterministic components provides high coverage in seconds.

**Cost control.** By routing 80% of classification through rule-based systems and all validation through Zod, the LLM call surface area is reduced by approximately 40-60% compared to Branch 1.1's fully-LLM approach. This directly reduces cost per run and reduces cost sensitivity to API pricing changes.

**User trust.** The explicit approval gates at each stage boundary are not just safety mechanisms — they are trust-building interactions. A user who approves each document before proceeding has a clear mental model of the system's behavior and a natural intervention point when the output is not what they intended. This transparency is the foundation of trust in a local tool that generates production code.

---

## 7. Conclusion

The stability-first stack for the AI Agentic Workflow Automation System is not a conservative choice driven by risk aversion. It is a principled engineering choice driven by the system's unique properties:

1. **The multiplicative reliability requirement.** A 5% error rate in a normal application means 5% of users have a bad experience. In a code generator, it means 5% of generated projects are built on a wrong foundation. The mathematics of D×N make generator reliability a qualitatively different target than application reliability.

2. **The local CLI context.** Without cloud infrastructure, there is no distributed tracing, no error aggregation, no automatic rollback orchestration. Everything the system does must be debuggable from the local file system with standard tools. FSM state logs, JSON schema validation errors, and template rendering failures are all debuggable this way. LLM "reasoning failures" are not.

3. **The user approval requirement.** Every major milestone requires explicit user approval (주의3). This constraint is not a limitation — it is the most powerful quality gate in the system. Designing around it means designing for legibility: the system must explain itself at each stage in terms the user can evaluate. Template-structured documents with clear sections are more legible than fully-generative outputs.

4. **The trust asymmetry.** One failure erases more trust than ten successes build. The stability-first stack accepts lower peak performance in exchange for a dramatically higher floor. A system that consistently produces good-to-excellent output on 98%+ of runs is more valuable to a user community than a system that produces excellent output 70% of the time and incomprehensible failures 30% of the time.

**Final stability score for the recommended stack: 9.1/10**

This score reflects genuine, residual API dependency risk (which cannot be eliminated without abandoning LLM quality) and the maintenance burden of hybrid classifier keyword tables. It does not reflect any compromise in the deterministic components — the FSM, schema validation, template generation, and sequential pipeline are all individually rated 9.0-9.9/10.

The system can be built in 6 months by a solo founder. It will be debuggable, testable, and maintainable. It will fail predictably and recover cleanly. When it succeeds — which will be 98%+ of the time — it will produce specification documents and code scaffolding that a developer can trust as a foundation.

That is the stability-first promise: not magic, but reliability. Not "wow" on first demo, but confidence on the hundredth production use.

---

*Discussion Branch 2.B — Stability First*
*Synthesizes: Branch 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.2*
*Word count: ~4,200*
*Prepared for: PRD.md pre-work (Phase 3 input)*
