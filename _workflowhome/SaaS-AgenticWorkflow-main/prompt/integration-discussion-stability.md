# Phase 2 Discussion — Branch 2.B: Stability First (External Integrations)
## "Can We Build the Most Reliable External Integration Layer for the SaaS Auto-Builder?"

**Role**: Discussion Moderator — Stability and Proven Reliability Priority
**Phase**: Phase 2 of Round 5 — External Integrations
**System**: LOCAL CLI tool (Claude Code) that generates full-stack SaaS
**Date**: 2026-03-12
**Source Material**: All 10 Round 5 Phase 1 Branches (1.1 Aggressive, 1.2 Conservative, 2.1 Evolutionary, 2.2 Big Bang, 3.1 Rapid, 3.2 Robust, 4.1 Debt Minimized, 4.2 Debt Practical, 5.1 Modern Theory, 5.2 Classical Theory)

---

## Moderator's Opening Position: Reliability Is Not Negotiable When You Are a Code Generator

External integrations are not created equal. This is the first principle of any stability-first analysis, and it is the principle most often violated by engineering teams who treat a Stripe webhook handler with the same care they give an internal logging utility. They are not the same. When your logging utility fails, your observability degrades. When your Stripe webhook handler fails — silently, intermittently, in a way that passes 90% of your test cases — your users lose revenue, your subscription state becomes inconsistent, and you have created the kind of trust-destroying event that no amount of feature development can repair.

But this system is not simply a system that calls integrations. It is a **code generator**. The distinction is not rhetorical — it is architecturally decisive. Every integration pattern this system implements becomes a template that is replicated N times across every SaaS it generates. A bug in this system's Stripe integration is not one bug. It is a factory for that same bug, pre-installed in every project that every user ever generates. One missing idempotency key becomes N missing idempotency keys across N production applications, affecting M users per application. This is Branch 4.1's D×N×M blast radius equation made concrete.

The stability-first thesis is this: **for a code generator, defensive engineering is the primary product feature.** Not the LLM orchestration. Not the multi-model consensus. Not the MCP readiness. The fundamental value promise — "the code we generate will not lose your users' money, expose their data, or fail silently in production" — is only achievable through a stability architecture that applies known reliability patterns without exception.

This discussion is structured around a central classification: Branch 4.2's Debt Firewall. Every integration in this system belongs to one of two categories:

**Generator Output Integrations**: The patterns the system embeds in generated SaaS code. These run in users' production environments against real money, real data, and real users. Blast radius: D×N×M. Debt tolerance: 0%.

**Internal Tooling Integrations**: The CLI subprocess orchestration and supporting tools the developer uses to run the generation pipeline. These run on the developer's local machine. Failures affect only the developer. Blast radius: 1. Debt tolerance: up to 30%.

Branch 1.2's CLI reliability scores — Gemini CLI at 5/10, ChatGPT CLI at 3/10 — are the numbers this entire analysis is built on. Every architectural recommendation that follows derives from taking those scores seriously and engineering defensively around them.

---

## 1. The Multiplicative Reliability Problem: Why CLI Integration Is Categorically Worse Than API Integration

### 1.1 The Three-Dimensional Failure Space

The reliability problem in this system is not simply that external services can fail. Every distributed system engineer knows that external services fail. The problem here has three compounding dimensions that together create a categorically more dangerous situation than typical API integration:

**Dimension 1 — CLI reliability baseline**: Gemini CLI at 5/10 and ChatGPT CLI at 3/10 are not API reliability scores. API reliability scores for mature services cluster at 9.5/10 to 9.9/10 (Stripe SLA: 99.99%; Supabase SLA: 99.9%). CLI subscription tools have no SLA. They have no versioned API contract. They were designed for interactive human use, not programmatic orchestration. The 5/10 and 3/10 scores reflect a genuine structural gap between "this tool works when a human uses it" and "this tool works when a machine invokes it repeatedly in a pipeline."

**Dimension 2 — Pipeline multiplication**: A SaaS generation run invokes the LLM pipeline multiple times across 7-9 document generation stages. If Gemini CLI is called at 4 stages and has a 5/10 per-call reliability, the probability of completing all 4 stages without failure is 0.5^4 = 6.25%. This is not an exaggerated scenario. This is the direct mathematical consequence of using a 5/10 reliability component in a serial pipeline.

Even assuming the 5/10 score includes error handling and represents "produces usable output" rather than raw availability, and even using a more generous reading of "one transient failure per 3 calls" (67% per-call success rate), a 4-stage pipeline has 0.67^4 = 20% success probability without fallback logic. **This means 80% of multi-LLM generation runs will encounter at least one Gemini CLI failure.**

**Dimension 3 — Generated project multiplication**: This is the dimension that distinguishes a code generator from every other system in the reliability literature. When the generator produces flawed integration patterns, those patterns are deployed to N user projects. The developer cannot patch generated projects centrally. Every user who has generated a SaaS carries the bug independently, in their own codebase, in their own production environment. Branch 4.1's blast radius equation:

```
D × N × M

D = defect severity (0-1, where Stripe double-charge = 1.0)
N = number of generated projects using the pattern
M = affected operations per project (transactions, auth sessions, emails)

Example:
  D = 0.8 (missing Stripe idempotency key — charges duplicated under retries)
  N = 50 generated projects after 3 months of use
  M = 200 payment operations per project per month

  Blast radius = 0.8 × 50 × 200 = 8,000 affected transactions/month
```

This is not a hypothetical. It is the direct consequence of a single template defect replicated at scale. The stability architecture must prevent this class of event from occurring at all.

### 1.2 Why CLI Unreliability Is Categorically Worse Than API Unreliability

Branch 5.2's classical IPC theory establishes why the CLI subprocess model is structurally more fragile than the HTTP API model:

**No contract versioning.** When Stripe releases API version 2024-12-18, they publish a migration guide, provide a dated compatibility layer, and guarantee that old versions continue working for 12+ months. When Google releases Gemini CLI 2.0, they are under no obligation to maintain any parsing contract with existing subprocess callers. An output format change that is invisible to humans ("the response now starts with a brief intro paragraph") is catastrophic to a regex parser that expects the JSON block to start on line 1.

**No structured error taxonomy.** Stripe returns `{"error": {"type": "card_error", "code": "insufficient_funds", "message": "..."}}`. Gemini CLI returns "Sorry, I can't help with that right now." or "Rate limit exceeded, please try again." in natural language that varies between CLI versions. The subprocess caller must parse error messages designed for human reading, not for programmatic handling. Branch 1.2 identifies three known failure modes — authentication expiry, rate limiting, output format changes — but acknowledges that the exact text of these errors is not documented and may change.

**No transactional guarantees.** If an HTTP request to Stripe fails after the charge is authorized but before the response is received, Stripe's idempotency system allows safe retry. If a Gemini CLI subprocess fails mid-output (process killed, network disconnect), the partial output on stdout cannot be recovered. There is no resume-from-checkpoint semantics in a subprocess pipe.

**No rate limit documentation.** Stripe's rate limits are published: 100 requests per second, burst to 1,000. Gemini Advanced subscription rate limits are not published. Anecdotal evidence suggests ~60 requests per minute under normal conditions, with harder limits on long-context requests. But these limits are not contractually guaranteed and Google reserves the right to change them without notice. A generation pipeline that runs fine for 3 months can break overnight if Google adjusts subscription rate limits.

**Combined reliability impact calculation (Branch 1.2 methodology):**

If we model three independent failure modes per CLI call:
- Authentication expiry: 3% per session (conservative)
- Rate limit hit: 7% per session at machine-speed invocation
- Output format unparseable: 4% per call (model behavior drift)

P(at least one failure in a given call) = 1 - (0.97 × 0.93 × 0.96) = 1 - 0.866 = **13.4%**

This is consistent with Branch 1.2's 5/10 reliability score for Gemini CLI. For a 4-call pipeline, expected total failure rate exceeds **44%** without circuit breaker or fallback logic. The stability architecture is not optional complexity. It is the engineering response to a mathematically certain failure rate.

### 1.3 ChatGPT CLI: An Honest Assessment That Branch 1.1 Underfunds

Branch 1.1 describes ChatGPT CLI as a "$0 marginal cost" component with "stable authentication via ChatGPT Plus". Branch 1.2 rates it at 3/10. This discrepancy is not a matter of optimism versus pessimism — it is a difference in what failure mode analysis the analyst performed.

The 3/10 score reflects a specific structural problem: there is no official, programmatically reliable way to access ChatGPT Plus via CLI without API keys. The landscape of options (reviewed in Branch 1.2 exhaustively) reduces to:

- Official OpenAI CLI tools require API keys — incompatible with the subscription constraint
- Third-party CLIs claiming subscription support use session cookies that expire every 30-90 days
- Browser automation (Playwright) violates OpenAI's TOS explicitly and is actively blocked by Cloudflare challenge pages
- ChatGPT Desktop app has no programmatic CLI interface

The 3/10 score is accurate and may be generous. A 3/10 reliability system has no place in any automated pipeline. The stability-first verdict is categorical: **ChatGPT CLI does not enter the system in V1, V2, or any version until OpenAI releases an official CLI with documented programmatic support.** No amount of retry logic, circuit breaker configuration, or fallback engineering can make a TOS-violating browser automation acceptable production infrastructure.

---

## 2. For Each Major Integration Domain: Assessment, Concessions, and Hard Lines

### 2.1 Multi-LLM Orchestration Layer

**Stability assessment**: This is the highest-risk integration in the entire system. Not because it is the most complex, but because it uniquely combines: (a) no official programmatic API contract, (b) interactive authentication designed for humans, (c) unstructured output requiring fragile parsing, and (d) placement in the critical path of every generation run.

**Where conservative patterns are NON-NEGOTIABLE**:

*Circuit Breaker is mandatory, not optional.* Without it, a Gemini CLI that starts producing authentication errors will cause 3-retry delays on every of the remaining 3-5 pipeline calls — adding 6-15 minutes of retry latency to a 20-30 minute generation run. With Circuit Breaker, after 2 consecutive failures, the circuit opens, Gemini is removed from the pipeline for the current session, and the run continues in Claude-only mode. Total latency impact: 10-30 seconds.

```
Circuit Breaker Configuration (Gemini CLI):
  CLOSED → OPEN:  2 failures within 3 consecutive calls
  OPEN duration:  300 seconds (5 minutes)
  HALF-OPEN probe: 1 test call after OPEN duration
  HALF-OPEN → CLOSED: 1 successful probe
  HALF-OPEN → OPEN: 1 failed probe → extend OPEN by 300s
```

*Anti-Corruption Layer is mandatory, not optional.* No raw Gemini CLI output enters the domain model. Every CLI response passes through a dedicated `GeminiOutputParser` that validates the response against the expected schema before any downstream use. If validation fails, the call is counted as a failure for Circuit Breaker purposes.

*Timeout is mandatory and must kill the subprocess.* 30-second hard timeout per Gemini call, 60-second for large-context calls. Process must be killed with `SIGKILL` on timeout, not `SIGTERM` (some CLI tools catch SIGTERM and keep running). Zombie subprocess accumulation is a real failure mode in long-running pipeline sessions.

**Where concessions to aggressive approaches are acceptable**:

Branch 1.1's Gemini CLI integration architecture (OAuth2, LLMAdapter, subprocess spawning) is structurally correct. The subprocess model with spawn + stdout capture is the right approach. The LLMAdapter interface pattern (Branch 2.1's `LLMProvider` interface) is the right abstraction. The concession this discussion makes: Gemini CLI is acceptable in V1.1 (not V1.0) in a non-critical path role with full defensive instrumentation in place.

The specific V1.1 use case: **quality comparison on completed generations**. After the full Claude pipeline has generated all 7 documents, an optional (feature-flagged, clearly labeled Beta) Gemini pass can provide an independent review. If Gemini CLI fails at this stage, the user already has a complete generation output. The Gemini review is enhancement, not prerequisite.

**Specific stability patterns**:
- Retry: max 2 retries, 3s base delay, 2x backoff, full jitter
- Health check: `gemini --version` before session start (fast, non-quota)
- Version pin: `@google/gemini-cli@1.x.x` (exact minor version) in documentation
- Output validation: JSON extraction + Zod schema parse; on failure = ACL rejection

### 2.2 Stripe (Generated SaaS Layer)

**Stability assessment: 9.5/10 when implemented correctly; 4/10 when implemented with shortcuts.**

This score gap is the key finding. Stripe's API is genuinely stable — 12 years of backward compatibility, comprehensive documentation, SLA of 99.99%. The instability risk is entirely in the generated integration quality, not in Stripe itself.

**Where conservative patterns are NON-NEGOTIABLE**:

*Idempotency keys are the Stripe contract, not a recommendation.* Branch 2.2 identifies this correctly. The Stripe API was designed around idempotency because network failures are inevitable and retrying a payment without idempotency creates double charges. The generated code must implement deterministic idempotency keys for every state-mutating Stripe operation:

```typescript
// Correct: deterministic idempotency key
const idempotencyKey = `${userId}-${priceId}-${requestId}`;
const subscription = await stripe.subscriptions.create(params, {
  idempotencyKey,
});

// Defective: no idempotency key
const subscription = await stripe.subscriptions.create(params);
```

The generated template must enforce this pattern. No shortcut version ships.

*Webhook signature verification is a non-negotiable security boundary.* An unsigned webhook endpoint is an unauthenticated state mutation endpoint. Any process that can reach the URL can trigger arbitrary payment state changes. The generated handler must verify `stripe.webhooks.constructEvent()` before processing any event, with the raw body (not the parsed JSON body) as the verification input.

*Idempotent handler execution is a delivery contract requirement.* Stripe delivers webhooks "at least once" — the same event may arrive multiple times. A `checkout.session.completed` handler that creates a subscription record without checking existence first will create duplicate records on re-delivery. Every generated webhook handler must include a database lookup before state mutation.

**Where concessions to aggressive approaches are acceptable**:

Branch 1.1's LemonSqueezy as an alternative to Stripe is a reasonable V2 consideration for lower-friction merchant onboarding. It is not a V1 decision — the system must prove the Stripe integration is correct before expanding to a second payment provider. The stability concession: document the payment abstraction interface (Branch 2.1's `PaymentProvider`) from Day 1, so LemonSqueezy can be added without restructuring the generated code.

Branch 5.1's MCP-based Stripe validation (using stripe-mcp to verify generated code against the live Stripe API during generation) is a genuinely valuable future capability. MCP readiness 3/5 is acceptable for optional validation tooling. The concession: include an optional `--validate-stripe` flag in V2 that uses MCP to run the generated Stripe code against a test environment before delivery. Not in the critical generation path; not required for generation to succeed.

**Stability scoring for compliant generated Stripe integration: 9.5/10**

### 2.3 Supabase Auth (Generated SaaS Layer)

**Stability assessment: 9/10 when using the correct patterns; the risk is exclusively in pattern selection.**

Supabase Auth is genuinely mature — PostgreSQL-backed, comprehensive documentation, active security response. Branch 1.2's 9/10 rating is accurate. The stability concern is not Supabase itself but the specific patterns the generator selects.

**Where conservative patterns are NON-NEGOTIABLE**:

*`getUser()` over `getSession()` in server-side contexts.* This is the most common class of Supabase Auth bug in AI-generated code, and it is well-documented by Supabase. `getSession()` reads from local storage without server validation — a compromised or expired token can be passed and accepted. `getUser()` validates the token against the Supabase Auth server on every call. In server-side contexts (Next.js Server Components, API routes, middleware), `getUser()` is the only safe option.

*RLS policies must be generated for every table, not left as optional.* A table without RLS policies is accessible to any authenticated user with the anon key — or, if the anon key is exposed (which it always is in a browser-side application), to unauthenticated requests. Every generated table definition must include matching RLS policies derived from the data model specification.

*PKCE OAuth flow for all OAuth providers.* Implicit OAuth flow was deprecated by the OAuth 2.0 specification (RFC 6749, Section 10.16) for public clients. The PKCE extension (RFC 7636) must be used for all browser-based OAuth. Supabase supports this out of the box, but the generated authentication setup must configure it explicitly.

**Where concessions to aggressive approaches are acceptable**:

Branch 5.1's schema-aware code generation via Supabase MCP is a legitimately valuable future capability at readiness 3/5. The concession: document the Supabase MCP server configuration as an optional enhancement in V2 documentation, so developers who want schema validation during generation can enable it. The MCP integration does not block generation if unavailable; it enhances quality when available.

Branch 2.1's signal-based auth adapter interface is architecturally sound. The generated code should implement a `AuthProvider` interface from Day 1 so that future alternative providers (Clerk, Auth.js) can be supported without rewriting the application logic.

**Stability scoring for compliant generated Supabase Auth integration: 9/10**

### 2.4 Email Integration (Generated SaaS Layer)

**Stability assessment: 8.5/10 for Resend, with specific risks in the generated delivery guarantees.**

Email delivery is lower blast-radius than payment processing (no direct financial loss from a missed email), but the failure modes have real user impact: missed password resets lock users out of accounts; missed subscription confirmations create support burden; bounce loops get domains flagged as spam.

**Where conservative patterns are NON-NEGOTIABLE**:

*No fire-and-forget email dispatch.* Every transactional email dispatch must log the Resend message ID to the database. If dispatch fails (rate limit, API error), the failure must be persisted as a retriable record, not silently dropped. A password reset flow that swallows email dispatch errors and returns success to the user is a user-locking defect.

*Bounce and complaint webhook handlers must be generated.* Resend provides `email.bounced` and `email.complained` webhook events. The generated code must include handlers that update the user's email status in the database and suppress future sends to flagged addresses. An application that continuously sends email to bounced addresses will get its domain blacklisted on major email providers — a catastrophic outcome that affects all users of the generated app.

**Where concessions to aggressive approaches are acceptable**:

Branch 1.1's Resend over Sendgrid/Postmark recommendation is correct on developer experience grounds. The aggressive choice here happens to be the stable choice. Resend's React Email integration and developer-oriented documentation reduce the probability of generated integration errors. Concede this one fully.

Branch 2.1's deferred email integration (add in Month 3-4, not Day 1) is reasonable for the *generator's own operations* but is not acceptable for *generated SaaS output*. The generated SaaS must have email integration from its first generated version, because password reset and email verification are core auth user flows. The distinction: the CLI tool does not need to send emails; the generated SaaS does.

### 2.5 Deployment (Vercel, Generated SaaS Layer)

**Stability assessment: 9/10 for standard Node.js deployments; 6/10 for edge function deployments.**

The score gap reflects a genuine reliability risk in generated edge function code. Vercel's platform is mature. The instability is in the edge runtime compatibility surface.

**Where conservative patterns are NON-NEGOTIABLE**:

*Generate edge functions only for operations documented as edge-compatible.* The Vercel Edge Runtime does not support all Node.js APIs. Operations that work in Node.js but fail in edge: `net.createServer()`, `child_process`, synchronous file system operations, most Node.js crypto methods. Generated code that assumes full Node.js compatibility and targets edge functions will produce runtime errors that are invisible in development but catastrophic in production.

*Scope rule for generated edge functions*: static response headers, simple redirects, geolocation-based routing, lightweight JWT verification. Everything else — auth flows, database operations, payment processing, email dispatch — generates as standard Next.js API routes in the Node.js runtime.

**Where concessions to aggressive approaches are acceptable**:

Branch 5.1's edge function advocacy for session validation and bot protection is valid within the scoped definition above. JWT validation at the edge (without database lookup) is a well-established pattern that does work in the V8 isolate model. The concession: include edge-based JWT validation for simple read-only route protection as a generated option. Include explicit documentation of the edge/node boundary in the generated README.

### 2.6 Analytics and Monitoring (Generated SaaS Layer)

**Stability assessment: 8.5/10 for Sentry; 8/10 for PostHog. Lower blast radius than payment/auth.**

Branch 1.1 recommends PostHog + Sentry as the monitoring pair. This is the correct choice. The stability concern is scope: analytics and monitoring integrations that fail gracefully are acceptable in a way that payment integrations that fail gracefully are not.

**Where conservative patterns are acceptable by design**:

Analytics calls are fire-and-forget by definition. A missed PostHog event is a gap in analytics, not a user-facing failure. The generated PostHog integration should use PostHog's `capture()` in a fire-and-forget pattern (no await, no error handling that blocks the user request). This is the correct, documented PostHog usage pattern.

Sentry error reporting is higher stakes because it captures crash evidence. The generated Sentry integration must be initialized before any application code runs (at the top of `_app.tsx`/`layout.tsx`) and must include an error boundary component that captures unhandled React errors.

**Where concessions to aggressive approaches are acceptable**:

Branch 1.1's OpenTelemetry aspiration is V3+ but architecturally sound. The concession: generate Sentry with the OpenTelemetry exporter enabled from Day 1, even if no other OTel tooling is in the stack. This is forward-compatible without adding complexity.

---

## 3. Anti-Corruption Layer Architecture: Protecting the Domain Model From CLI Volatility

### 3.1 The ACL in Classical Theory

Evans's Anti-Corruption Layer (Domain-Driven Design, 2003) was designed for a specific problem: when integrating with a legacy system or external service whose domain model is fundamentally different from your own, you need a translation layer that prevents the external model's concepts from polluting your internal model. Without the ACL, your code starts thinking in the external system's terms — and when the external system changes, your entire codebase changes with it.

Branch 5.2 applies this directly to LLM CLI orchestration. The Gemini CLI's output model — conversational Markdown text with varying structure, preamble text, code blocks, inline explanations — is categorically different from the SaaS Auto-Builder's internal domain model: structured documents with typed sections, validated schemas, deterministic file structures. The ACL is the boundary that ensures the internal model never sees the external model's format.

### 3.2 The Five-Layer ACL for CLI Integration

The SaaS Auto-Builder requires five layers of protection between the CLI subprocess output and the internal domain model:

**Layer 1 — Subprocess isolation**: The CLI process runs in a sandboxed subprocess with a hard timeout. Its stdout is captured as a raw byte stream, not interpreted. Its exit code is recorded. Process termination is forced if the timeout is exceeded.

```typescript
// Layer 1: subprocess isolation contract
interface CLIInvocationResult {
  exitCode: number;
  stdout: Buffer;
  stderr: Buffer;
  timedOut: boolean;
  durationMs: number;
}
```

**Layer 2 — Raw output validation**: Before any parsing, the raw stdout is validated against basic sanity checks: non-empty, within expected length range, no binary content, valid UTF-8 encoding. Failures at this layer indicate a subprocess communication problem, not a content problem.

**Layer 3 — Format extraction**: Provider-specific parsing rules extract the "intended" content from the raw output. For Gemini CLI, this means stripping conversational preamble (lines before the first structured content marker), extracting code blocks, and normalizing whitespace. This layer is the most fragile and is explicitly versioned.

```typescript
// Layer 3: format extraction — versioned per CLI tool
class GeminiOutputParser_v1 implements CLIOutputParser {
  readonly version = '1.0.0';
  readonly cliTool = 'gemini-cli';

  extract(rawOutput: string): ExtractedContent {
    // Strip preamble: everything before first ``` or first {
    const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
    const codeMatch = rawOutput.match(/```[\s\S]*?```/g);
    return {
      json: jsonMatch?.[0] ?? null,
      codeBlocks: codeMatch ?? [],
      plainText: rawOutput.replace(/```[\s\S]*?```/g, '').trim(),
    };
  }
}
```

**Layer 4 — Schema validation**: The extracted content is validated against the expected Zod schema for the specific task type. A PRD review task expects a different schema than a code generation task. Validation failure is a schema mismatch error, not a CLI error — it means the CLI produced valid output in the wrong format.

**Layer 5 — Domain translation**: The validated, schema-conformant data is translated into the internal domain model type. This is the only place where the CLI's vocabulary (which may use different field names, different granularity, different enumeration values) is mapped to the internal model's vocabulary.

### 3.3 Why the ACL Must Be Versioned

Every layer of the ACL except Layer 1 (subprocess isolation) is specific to the current behavior of the CLI tool. When Gemini CLI changes its output format (which it has done multiple times since 2024, per Branch 1.2), only Layer 3 needs to change. When the expected schema changes because a new task type is added, only Layer 4 needs to change. When the domain model changes, only Layer 5 needs to change.

The ACL version number (`GeminiOutputParser_v1`) must be logged with every invocation. When a parsing failure occurs in production, the version number identifies exactly which layer of the ACL needs to be updated.

### 3.4 ACL Testing Requirements

The ACL must be the most heavily tested component in the CLI integration layer:

- 50 fixture-based tests covering known Gemini output formats (Layer 3 coverage)
- 20 schema validation tests covering expected and malformed outputs (Layer 4 coverage)
- 10 domain translation tests covering each task type (Layer 5 coverage)
- Record-replay test infrastructure (Branch 3.1's MSW + record-replay pattern applied to subprocess outputs)

When a new Gemini CLI version is released, the first engineering task is running the ACL fixture tests against the new version's output. This is the minimum change-detection mechanism.

---

## 4. Graceful Degradation Strategy: When CLI Components Fail

### 4.1 The Degradation Mode Map

The system must define its behavior in each degradation scenario before a single line of integration code is written. Ad-hoc degradation — "fall back to something reasonable" — produces inconsistent user experience and debuggability nightmares.

**Degradation Mode 1: Gemini CLI Authentication Expired**

Detection: `GeminiOutputParser` identifies `UNAUTHENTICATED` in stderr; or exit code 1 with specific text match.

User experience: "Gemini CLI authentication has expired. Generation continuing with Claude only. Run `gemini auth login` to restore multi-model validation."

System behavior: Circuit Breaker immediately moves to OPEN state for Gemini. All remaining pipeline steps use Claude-only mode. Generation completes. Log entry records: timestamp, failure mode, number of pipeline steps affected, generation ID.

Recovery: User runs `gemini auth login` manually. Circuit Breaker tests with probe call on next generation run.

**Degradation Mode 2: Gemini CLI Rate Limit**

Detection: stderr contains rate limit message; or exit code 1 with delay hint in output.

User experience: "Gemini CLI rate limit reached. Generation continuing with Claude only. Gemini will be available again in approximately 60 seconds."

System behavior: Circuit Breaker moves to OPEN state with 60-second timer. If current run has remaining stages where Gemini was scheduled, skip and continue with Claude. After 60-second timer, move to HALF-OPEN and attempt probe on next use.

**Degradation Mode 3: Gemini CLI Output Unparseable**

Detection: ACL Layer 3 or 4 returns validation failure.

User experience: "Gemini returned an unexpected format for this task. Using Claude's analysis only."

System behavior: Count as failure for Circuit Breaker. Log full raw output to `.debug/gemini-parse-failure-{timestamp}.txt` for debugging. Continue with Claude result for this pipeline step.

**Degradation Mode 4: Claude API Slow (>30s Response)**

Detection: Timeout guard on Claude API call.

User experience: "Claude is responding slowly. Generation may take longer than usual."

System behavior: Extend timeout to 90 seconds for next attempt. Log latency warning. Do NOT fall back — there is no fallback for the primary generation model. If 90-second timeout also expires, save checkpoint to `.debug/generation-checkpoint-{timestamp}.json` and exit with recovery instructions.

**Degradation Mode 5: Gemini CLI Not Installed**

Detection: `which gemini` fails, or spawn throws ENOENT.

User experience: "Gemini CLI is not installed. Generation will use Claude only. To enable multi-model validation, install Gemini CLI: `npm install -g @google/gemini-cli && gemini auth login`"

System behavior: Disable all Gemini integration for this session. This is not an error — it is a valid configuration state. Claude-only generation proceeds normally.

### 4.2 The Principle of Non-Blocking Degradation

Every degradation mode for Internal Tooling integrations (CLI subprocesses) must be non-blocking. The user must never be unable to complete a SaaS generation because Gemini CLI is unavailable. This principle drives every Circuit Breaker threshold, every fallback handler, and every timeout configuration.

The corollary: Generator Output integrations (Stripe, Supabase Auth, email) do not have non-blocking degradation. If the generated Stripe integration cannot be generated correctly (for any reason), the system must fail explicitly rather than generate a defective Stripe integration. Explicit failure that requires user intervention is preferable to silent generation of broken payment code.

### 4.3 Checkpoint Architecture for Long-Running Failures

A generation run that fails at Stage 5 of 7 has produced 4 completed documents. Without checkpoint persistence, these 4 documents are lost when the process exits, and the next run starts from Stage 1, incurring the full generation latency again.

The stability architecture requires checkpoint persistence:

```
.debug/
  generation-checkpoint-{id}.json  ← stage completion state
  gemini-failures-{session}.log    ← CLI failure log
  circuit-breaker-state.json       ← persistent CB state across sessions
  generation-history.json          ← past generation audit log
```

When a generation fails at Stage N with a transient error (timeout, CLI failure), the checkpoint allows resumption from Stage N rather than Stage 1. This makes the degradation experience tolerable: a Gemini failure that interrupts Stage 5 adds 10 seconds of fallback logic, not 20 minutes of re-generation.

---

## 5. Testing Requirements: Minimum Standards for Each Integration Tier

### 5.1 Testing Philosophy: Failure Mode Coverage, Not Coverage Metrics

Branch 3.2's 50-case test matrix and 7-gate validator establish the right testing philosophy: the goal is not line coverage, it is failure mode coverage. Every cell in Branch 3.2's failure taxonomy table must have at least one test case. An integration test suite that achieves 95% line coverage but does not test the rate limit path, the authentication expiry path, and the output format drift path is not a reliability test suite — it is a happy-path test suite.

### 5.2 Internal Tooling Integration Testing (CLI Layer)

**Gemini CLI integration tests (minimum 30 test cases)**:

| Test Category | Test Cases | Testing Method |
|--------------|------------|----------------|
| Nominal invocation | 5 cases (different prompt types) | Record-replay with fixture outputs |
| Authentication expiry | 3 cases (expired token, revoked, account locked) | Subprocess mock with simulated exit codes |
| Rate limit | 3 cases (429 equivalent, delay hint, silent drop) | Subprocess mock with stderr fixtures |
| Output format drift | 5 cases (preamble variants, JSON position variants, no-JSON response) | ACL fixture tests |
| Timeout | 3 cases (30s timeout, 60s timeout, partial output on kill) | Process mock with delayed response |
| Circuit breaker state transitions | 5 cases (CLOSED→OPEN, OPEN→HALF-OPEN, probe success, probe failure) | State machine unit tests |
| Process spawn failure | 3 cases (ENOENT, permission denied, PATH issue) | OS mock |
| Concurrent invocations | 3 cases (2 simultaneous, rate limit on concurrent) | Process concurrency tests |

**ChatGPT CLI integration tests: not applicable.** ChatGPT CLI is not implemented in V1. If implemented in V3+, it requires the same test matrix as Gemini CLI plus additional TOS-compliance documentation.

### 5.3 Generator Output Integration Testing (Template Layer)

**Stripe template tests (minimum 40 test cases, 0% skippable)**:

| Test Category | Test Cases | Required |
|--------------|------------|----------|
| Payment intent creation with idempotency key | 3 cases | Mandatory |
| Duplicate payment intent (same key) | 2 cases | Mandatory |
| Webhook signature verification | 5 cases (valid, invalid, missing, tampered, replay) | Mandatory |
| Webhook re-delivery idempotency | 4 cases (first delivery, second delivery, N-th delivery) | Mandatory |
| Subscription creation and lifecycle | 5 cases | Mandatory |
| Payment failure handling (insufficient funds, card decline) | 4 cases | Mandatory |
| Refund creation with idempotency | 2 cases | Mandatory |
| Stripe API timeout handling | 3 cases | Mandatory |
| API version compatibility | 2 cases | Mandatory |
| Customer creation and retrieval | 3 cases | Mandatory |
| Webhook error response codes | 3 cases (400, 500, 200) | Mandatory |
| Rate limit handling in generated code | 2 cases | Mandatory |

Branch 3.2's attack simulation testing must be applied: attempt to trigger double-charges, attempt to submit unsigned webhooks, attempt to replay stale webhook events. These are not optional. They are the functional equivalents of penetration testing for the generated payment code.

**Supabase Auth template tests (minimum 25 test cases)**:

| Test Category | Test Cases |
|--------------|------------|
| `getUser()` vs `getSession()` enforcement | 5 cases (server contexts) |
| RLS policy enforcement | 8 cases (authenticated, unauthenticated, cross-user) |
| OAuth PKCE flow | 3 cases |
| Token expiry handling | 3 cases |
| Sign-out session invalidation | 2 cases |
| JWT secret rotation | 2 cases |
| Auth callback URL handling | 2 cases |

### 5.4 Record-Replay Testing for CLI Integration

Branch 3.1 identifies MSW + record-replay as the testing approach for mocked subprocess behavior. This is the correct approach, adapted for subprocess calls rather than HTTP calls:

1. **Record phase**: Run the real Gemini CLI against representative prompts. Capture stdout, stderr, exit code, and duration. Store as fixtures in `test/fixtures/gemini/`.
2. **Replay phase**: Subprocess mock intercepts `spawn('gemini', ...)` calls and returns the matching fixture output instead of invoking the real CLI.
3. **Drift detection**: When Gemini CLI is updated to a new version, run the real CLI against the same prompts and compare outputs. Diff indicates what the ACL Layer 3 parser must handle for the new version.

This approach provides: fast test execution (no real CLI calls), deterministic results, and a concrete mechanism for detecting CLI output format drift.

---

## 6. Non-Negotiable Stability Requirements: The Hard Lines

### 6.1 Hard Lines for Internal Tooling Integrations

1. **Circuit Breaker is non-negotiable for all CLI integrations.** No CLI subprocess is called more than 2 consecutive times without Circuit Breaker evaluation. This is a code review gate, not a guideline.

2. **Hard timeout on every subprocess call.** 30 seconds for standard calls, 90 seconds for large-context calls. No exceptions. Process kill (SIGKILL, not SIGTERM) on timeout.

3. **Anti-Corruption Layer for all CLI output.** No raw CLI output enters the domain model. Every response is validated against a schema before use. Schema validation failure counts as a CLI failure for Circuit Breaker purposes.

4. **Claude-only fallback is always available.** The system must be able to complete any generation run with Claude as the sole LLM. If Gemini is unavailable for any reason, generation proceeds in Claude-only mode without user-facing failure.

5. **No ChatGPT CLI in any production pipeline.** The constraint is categorical, not a matter of implementation quality. ChatGPT CLI's 3/10 stability score and TOS ambiguity make it unsuitable for any automated workflow.

6. **Version pinning for CLI tools.** `@google/gemini-cli` must be pinned to an exact minor version in system documentation. Users must be warned before upgrading.

7. **Failure artifacts must survive process exit.** All Circuit Breaker state, CLI failure logs, and generation checkpoints are written to disk before process exit. An integration failure that leaves no local artifact is a failure that cannot be debugged.

### 6.2 Hard Lines for Generator Output Integrations

1. **Zero tolerance for Stripe integration shortcuts.** Idempotency keys, webhook signature verification, and idempotent handler execution are non-negotiable in every generated Stripe integration. No exceptions, no "good enough for MVP" compromises.

2. **`getUser()` over `getSession()` is enforced in code review, not documentation.** The generated code uses the correct Supabase Auth pattern. This is verified by automated linting rule in the generated SaaS codebase, not left to the developer's discretion.

3. **RLS policies are generated for every table, not optional.** A generated data model without matching RLS policies is an incomplete generation. The generation pipeline does not mark a table as complete until its RLS policies are generated.

4. **No generated edge function code for complex auth flows or database transactions.** Scope limit is enforced by the generation template. Prohibited edge function patterns trigger a generation-time warning and automatic conversion to Node.js server functions.

5. **Email dispatch failures are logged, never silently swallowed.** The generated email integration includes structured error logging to the database for every failed dispatch. No fire-and-forget without exception handling.

---

## 7. Where This Discussion Agrees with Modern / Aggressive Approaches

The "Stability First" position is not reflexive conservatism. It is evidence-based caution applied where the evidence supports caution. Where the evidence supports modern or aggressive approaches, this discussion concedes those points explicitly.

### 7.1 Gemini CLI Architecture: Concede the Core Approach (Branch 1.1)

Branch 1.1's Gemini CLI integration architecture — OAuth2, `@google/gemini-cli`, subprocess spawning, LLMAdapter pattern — is structurally correct. The aggressive analyst correctly identifies that Google's first-party CLI is the right substrate for subscription-based Gemini access. The concession from stability is about timing and risk tier, not architecture: Gemini CLI belongs in the non-critical path with Circuit Breaker protection, not in the critical path without it.

The aggressive integration architecture is adopted wholesale for V1.1; the aggressive timing (Day 1, critical path) is not.

### 7.2 LLMProvider Interface Abstraction: Concede (Branch 2.1)

Branch 2.1's Day-1 interface definition for `LLMProvider` is correct. Define the interface before implementing the first provider. This costs nothing and prevents major refactoring when Gemini is added in V1.1. The stability concern with deferring interfaces is higher than the cost of defining them upfront.

### 7.3 Resend Over Traditional Email Providers: Concede (Branch 1.1)

Branch 1.1's Resend recommendation over Sendgrid or Postmark is adopted. Resend's React Email native integration and developer-oriented API reduce the probability of generated integration errors relative to older providers with more complex SDKs. This is the case where the aggressive choice and the stable choice coincide.

### 7.4 Two-Domain Model for Integration Architecture: Concede (Branch 2.2)

Branch 2.2's Two-Domain Model — explicit separation between Host CLI Tool integrations and Generated SaaS integrations — is the correct architectural framing. This is not conservative or aggressive; it is analytically correct. This discussion uses it as the primary classification framework (Section 2 above).

### 7.5 PostHog + Sentry Monitoring Pair: Concede (Branch 1.1)

Branch 1.1's PostHog + Sentry recommendation for the generated SaaS monitoring stack is adopted. Both tools have years of production validation. PostHog's self-hosted option provides future data sovereignty. Sentry's source map integration with Next.js is first-class. This is not a stability compromise — it is the correct choice for both aggressive and conservative analysts.

### 7.6 MCP as Future Enhancement Path: Concede in Principle (Branch 5.1)

Branch 5.1's MCP vision is directionally correct. An MCP server wrapping Stripe, Supabase, or Gemini would provide richer integration than raw subprocess calls. The concession from this stability position: MCP is the architectural target for V3+, and the integration interfaces defined in V1 should be designed to be MCP-compatible without requiring structural changes. The specific concession: the `LLMProvider.generate()` interface signature should be compatible with a future MCP tool call interface.

### 7.7 Debt Firewall as Governance Model: Adopt (Branch 4.2)

Branch 4.2's Debt Firewall is adopted without reservation. It is the clearest expression of the stability-first framework applied to technical debt. The binary classification — Generator Output (0% debt) vs. Internal Tooling (up to 30% debt) — eliminates the ambiguity that leads to "acceptable" shortcuts in the wrong places.

---

## 8. Final Recommendation: The Stability-First Integration Stack

### 8.1 V1.0 Integration Stack (Month 1-2)

**System Layer (Internal Tooling)**:

| Integration | Decision | Rationale |
|-------------|----------|-----------|
| Claude (Anthropic SDK) | Primary, critical path | Official SDK, versioned, 8.5/10 |
| Gemini CLI | Not yet integrated | Critical path only if stability verified |
| ChatGPT CLI | Not implemented | 3/10 stability, TOS ambiguity |
| MCP servers | Not implemented | Protocol immaturity, readiness 2-3/5 |

**Generator Output Layer**:

| Integration | Decision | Non-Negotiables |
|-------------|----------|-----------------|
| Stripe (v13 SDK) | V1 mandatory | Idempotency, signature verification, idempotent handlers |
| Supabase Auth (v2 SDK) | V1 mandatory | getUser(), RLS on all tables, PKCE OAuth |
| Supabase Database | V1 mandatory | Connection pooling, query timeout, RLS |
| Resend (v3 SDK) | V1 mandatory | Dispatch logging, bounce handler, retry queue |
| Vercel | V1 mandatory | Edge scope limits enforced by generation rules |
| Sentry | V1 mandatory | Initialized before app code, error boundary |
| PostHog | V1 mandatory | Fire-and-forget capture, no blocking analytics calls |

**Overall V1.0 stability score: 9.2/10**

### 8.2 V1.1 Integration Stack (Month 3-4: Gemini Addition)

Prerequisites before Gemini enters production use:
- ACL implementation complete and tested (minimum 30 test cases)
- Circuit Breaker implementation complete and tested (state machine unit tests)
- Checkpoint persistence implemented
- Feature flag `--multi-llm` implemented (off by default)
- User documentation includes explicit stability caveat (Beta, 5/10, not for production-critical use)

When prerequisites are met:
- Gemini CLI added to non-critical path (quality comparison only)
- Full Circuit Breaker + ACL + timeout + fallback implemented
- V1.1 overall stability score: 9.0/10 (marginal reduction for Beta Gemini path)

### 8.3 The Non-Technical Non-Negotiable

Every integration in this system will eventually fail in production, in ways this document did not predict. The stability architecture's goal is not to prevent all failures — it is to ensure that failures produce:

1. A clear user-visible message explaining what failed and what the system did about it
2. A local file artifact (log, checkpoint, debug output) that allows the developer to diagnose the failure
3. A system state that the user can recover from without starting over

An integration failure that produces any of these three outcomes is a handled failure. An integration failure that produces none of them is a trust-destroying event. The entire defensive architecture — Circuit Breaker, ACL, retry, checkpoint — exists to ensure every failure is a handled failure.

### 8.4 Final Stability Assessment by Category

| Category | Stability Score | Confidence |
|----------|----------------|------------|
| V1.0 Generator Output integrations | 9.2/10 | High |
| V1.1 Gemini CLI (non-critical path) | 5.5/10 (with CB+ACL) | Medium |
| ChatGPT CLI | 3/10 | High (not implemented) |
| MCP integration (V3+) | 4/10 projected | Low |
| Overall V1.0 system reliability | **9.0/10** | High |

The 1.0 gap from perfect reflects three residual risks: Claude API dependency on Anthropic's infrastructure (unavoidable; managed by checkpoint + graceful exit), inherent non-determinism of LLM-generated code quality across diverse user specifications, and the fundamental uncertainty of generating code to run in production environments the system cannot observe. All three are managed, not eliminated. That distinction — known risk, managed risk, honestly communicated risk — is the operational definition of the stability-first philosophy.

---

*Discussion Branch 2.B — Stability First (External Integrations)*
*Synthesizes: Branch 1.1 (Aggressive), 1.2 (Conservative), 2.1 (Evolutionary), 2.2 (Big Bang), 3.1 (Rapid), 3.2 (Robust), 4.1 (Debt Minimized), 4.2 (Debt Practical), 5.1 (Modern Theory), 5.2 (Classical Theory)*
*Word count: ~5,800*
*Prepared for: PRD.md pre-work (Phase 3 input)*
