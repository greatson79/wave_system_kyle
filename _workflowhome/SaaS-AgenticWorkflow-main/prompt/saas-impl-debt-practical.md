# Practical Technical Debt Management for Generated SaaS Code

**Branch**: 4.2 — Practical Debt Management in Generated SaaS
**Perspective**: Pragmatic Technical Debt Manager
**Core Philosophy**: "Debt is leverage. Used wisely it accelerates shipping. Ignored long enough, it destroys products."
**Context**: AI-generated full-stack SaaS (Next.js + Supabase + Stripe) for indie hackers and solo founders
**Date**: 2026-03-12

---

## Executive Summary

The AI agentic workflow system under design generates full-stack SaaS applications for indie hackers and solo founders who need to ship fast. This creates a compounded debt challenge: the code generator itself is a product under time pressure, AND the generated SaaS code it produces will carry the technical debt decisions baked into the generator's templates.

This report resolves that challenge with a two-level framework. At the **generator level**, the system must encode debt decisions into its templates — specifying exactly which shortcuts are acceptable, where the red lines are, and how to document debt for future payback. At the **generated SaaS level**, each output project must ship with a structured debt inventory, upgrade paths, and clear escalation triggers.

The central finding: for a typical SaaS project targeting product-market fit within 6 months, accepting ~20-25 strategic debt items delivers 2-3 months of earlier shipping and $10,000-$40,000 in earlier revenue — while the future debt paydown cost is measurable and bounded. This is a calculable NPV-positive trade-off, not a gamble.

**Recommended debt budget per generated SaaS project:**
- Month 1-3: 95% feature velocity, 5% debt management — accept ~20 strategic debt items
- Month 3-6: 85% features, 15% debt payback — retire 8-10 items, add 5-7 new
- Month 6-12: 80% features, 20% debt management — systematic reduction; one "debt sprint" if >40 items accumulate

---

## 1. The Two-Level Debt Problem in Generated SaaS

When our CLI system generates a SaaS project, it is making debt decisions on behalf of the founder. The founder did not write the code. The founder may not fully understand what shortcuts were taken. This creates a unique accountability structure:

**Level 1 — Generator Template Debt**: The decisions embedded in the generator's templates about how to handle auth, payments, RBAC, error handling, and data modeling. These decisions propagate to every generated project. A bad default in a template is a bug factory.

**Level 2 — Project Evolution Debt**: The shortcuts that accumulate as the founder iterates after the generator output. The generator cannot control this, but it can scaffold the project to make debt visible and manageable.

The practical implication: the generator must be opinionated and explicit. Every template shortcut must come with a machine-readable annotation, an upgrade path, and a time trigger. This is not optional documentation — it is a contract with the founder about what they are shipping.

### 1.1 Why This Is Different From Regular Technical Debt

In a hand-crafted project, the developer understands why each shortcut was taken because they took it. In a generated project:

1. The founder may not have the technical depth to evaluate the shortcuts
2. The shortcuts were optimized for the "average SaaS" — the founder's specific constraints may make some acceptable debts actually dangerous
3. The generator updates its templates over time, creating drift between generated projects and current best practices
4. Multiple generated projects can share the same debt patterns, meaning a vulnerability in a template reaches hundreds of users simultaneously

These differences demand that the generator's debt documentation be **more explicit, not less**, than what a skilled developer would write for themselves.

---

## 2. Strategic Debt Categories for Generated SaaS

### 2.1 Acceptable Debt — The Green Zone

These shortcuts are safe to generate for indie hackers targeting 0-1,000 users. Each has a bounded cost to fix and minimal risk while unresolved.

**Authentication Simplification**
- Email/password only (no social OAuth, no magic links, no passkeys)
- Supabase Auth handles the cryptographic complexity; the limitation is UX, not security
- Fix trigger: user feedback shows OAuth friction is causing signup abandonment
- Fix time: 4-6 hours per OAuth provider; Supabase's provider list makes this mechanical
- Debt score: LOW

**Basic RBAC (Two Roles)**
- Admin and User only — no custom roles, no attribute-based access control, no permission granularity
- Works for 95% of B2B SaaS up to ~500 seats
- Fix trigger: a customer requests "manager" role with read-only billing access, or similar
- Fix time: 8-16 hours to add a roles table and propagate checks through RLS policies
- Debt score: LOW

**Hardcoded Configuration Constants**
- Pricing tiers, feature limits, trial lengths, email templates baked into code rather than database-driven
- Acceptable for V1 because the founder does not know what the right values are yet
- Fix trigger: founder wants to A/B test pricing or run a limited-time promotion
- Fix time: 4-8 hours to extract to a configuration table with admin UI
- Debt score: LOW

**Catch-All Error Handling**
- `try { ... } catch (error) { return { error: 'Something went wrong' } }` patterns
- Users get a generic message; engineers get a logged error with stack trace
- Acceptable because specific error messages require knowing the actual error patterns first
- Fix trigger: support tickets citing confusing errors, or monitoring showing error rate >2%
- Fix time: 2-4 hours per critical user flow to add specific error categorization
- Debt score: LOW

**Minimal Logging (stdout + Supabase logs)**
- No structured logging, no distributed tracing, no centralized log aggregation
- Acceptable for <100 users where Supabase dashboard provides adequate visibility
- Fix trigger: debugging requires more than 30 minutes per incident, or user-reported bugs cannot be reproduced
- Fix time: 4 hours to add Pino structured logging; 8 hours to integrate with a log aggregation service
- Debt score: LOW

**Single-Language (English only)**
- No i18n, hardcoded UI strings, no date/currency localization
- Acceptable for English-speaking markets in the first 6 months
- Fix trigger: meaningful signup traffic from non-English-speaking regions
- Fix time: 16-40 hours depending on framework i18n support and string count
- Debt score: LOW

**Basic Mobile Responsiveness (Not Mobile-First)**
- Tailwind responsive breakpoints applied but layout optimized for desktop
- Acceptable for B2B SaaS where >80% of users are on desktop
- Fix trigger: mobile traffic represents >30% of sessions and bounce rate is high
- Fix time: 8-16 hours of focused CSS work per major page
- Debt score: LOW

**Sequential Database Queries Where Parallel Would Be Faster**
- Awaiting queries one-by-one instead of using Promise.all() or database-level JOINs
- Acceptable for pages with <200ms total latency target at <100 concurrent users
- Fix trigger: Core Web Vitals show TTFB >400ms consistently, or user complaints about slow loading
- Fix time: 2-4 hours per page to audit and parallelize
- Debt score: LOW

**No API Rate Limiting**
- No per-user, per-IP, or per-endpoint rate limits
- Acceptable for initial launch when user count is small enough that abuse is manually detectable
- Fix trigger: any evidence of API abuse, or security audit, or preparing for public launch with open signup
- Fix time: 4-8 hours to add middleware-based rate limiting via Upstash or similar
- Debt score: MEDIUM (escalates to HIGH at public launch)

**Simplified Stripe Integration (Happy Path Only)**
- Checkout flow and basic subscription management, but no dunning (failed payment recovery), no proration for plan changes, no invoice customization
- Supabase webhook handler is present but only handles `checkout.session.completed` and `customer.subscription.deleted`
- Acceptable for <50 paying users because edge cases are rare enough to handle manually
- Fix trigger: first failed payment that is not recovered automatically, or first plan upgrade request
- Fix time: 8-16 hours to add complete webhook handling; dunning workflow adds another 4-8 hours
- Debt score: MEDIUM

### 2.2 Never-Accept Debt — The Red Lines

These items are non-negotiable in every generated project. The cost of accepting them exceeds any speed benefit by an order of magnitude. The generator must implement these correctly in its templates with no optional flags to disable them.

**Security Vulnerabilities**
- SQL injection: Supabase's parameterized queries prevent this by default; but any raw SQL in RPC functions must use `$1, $2` parameters, never string interpolation
- XSS: React's JSX encoding handles most cases, but `dangerouslySetInnerHTML` is banned in generated code
- CSRF: Next.js App Router's server actions use origin checking by default; this must not be disabled
- Template rule: generated code must never use string interpolation to build SQL or HTML. Zero exceptions.

**Data Loss Potential**
- No hard deletes for user data: every user-facing delete must be a soft delete (`deleted_at TIMESTAMP`). Supabase RLS policies filter soft-deleted rows from normal queries
- Database backups: Supabase provides automated daily backups on Pro plan; generated project must include documentation to verify this is enabled before launch
- Template rule: every user data table must include `deleted_at` column in the migration. The generator enforces this via migration template validation.

**Payment Handling Errors**
- Double charging: idempotency keys must be included on every Stripe API call that creates a charge or subscription
- Missed webhooks: generated Stripe webhook handler must be idempotent (processing the same event twice produces the same result)
- Webhook signature verification: `stripe.webhooks.constructEvent()` with signature verification is non-optional
- Template rule: payment-related generated code includes automated tests for the idempotency case and the signature verification case. These tests are not marked as deferrable.

**Authentication Bypass**
- Every Supabase API route that accesses user data must verify `session.user.id` before returning data
- RLS policies are the backstop but must not be the only guard — application-level checks are required in server actions and API routes
- Template rule: generated server actions include a `requireAuth()` helper as the first line. This is a linting rule, not just a convention.

**PII and Data Privacy**
- User emails, names, and payment information must never appear in application logs
- Stripe customer data must not be duplicated into the application database beyond what is necessary for business logic
- Template rule: generated logging utilities include a sanitizer that strips known PII field names before writing to logs.

**Environment Variable Validation**
- Generated applications must validate all required environment variables at startup, not at first use
- A missing `STRIPE_SECRET_KEY` that surfaces as a null pointer exception during a user's first checkout attempt is unacceptable
- Template rule: generated `env.ts` file validates all required variables with descriptive error messages on startup. Deployment checklist includes environment variable verification.

**Hardcoded Secrets**
- API keys, database passwords, JWT secrets never appear in generated source code
- Template rule: generator refuses to embed any value that matches a secret pattern. Any configuration value that varies by environment uses `process.env.*` with validation.

---

## 3. Phased Debt Allocation for Generated SaaS Projects

### 3.1 Phase 1: "Just Ship It" — Month 1-3

**Objective**: Reach first paying customer. Validate that the core value proposition works.

**Budget**: 95% feature development, 5% debt management. Debt management in this phase means only three things: (1) paying Red Line debts before they are introduced, (2) writing TODO comments that are machine-parseable, (3) running the monthly 2-hour debt collection session.

**Acceptable shortcuts in this phase** (the full green zone list from Section 2.1):
- Email/password auth only
- Two-role RBAC (admin/user)
- Hardcoded configuration constants
- Catch-all error handling
- Minimal logging
- English only
- Desktop-optimized responsive design
- Sequential database queries
- No rate limiting (internal or beta users only)
- Simplified Stripe integration (happy path)

**Minimum viable security in Phase 1** — these must be present from day one:
- Environment variable validation at startup
- Stripe webhook signature verification
- Soft deletes on all user data tables
- Idempotency keys on payment API calls
- RLS policies on all user-facing tables
- `requireAuth()` guard on all authenticated routes
- No secrets in source code

**Tests to skip in Phase 1**:
- Edge case input validation
- Cross-browser compatibility beyond Chrome/Safari latest
- Mobile-specific test cases
- Load/performance tests
- Error handling for rare Stripe events (subscription paused, dispute created)

**Tests to NEVER skip**:
- Happy path checkout flow (end-to-end)
- Authentication (login, logout, session persistence)
- Webhook idempotency for `checkout.session.completed`
- Data access control (can User A access User B's data?)
- Environment variable validation (does the app fail gracefully with missing env vars?)

**Expected debt inventory at end of Phase 1**: 18-22 items (15-18 low, 3-5 medium). Every item documented with a machine-readable TODO comment.

**TODO standard for generated code**:
```typescript
// TODO(P0): [security] Validate all user inputs before database write — fix before public launch
// TODO(P1): [perf] Parallelize dashboard queries — fix when TTFB > 400ms
// TODO(P2): [quality] Add specific error messages per failure mode — fix when support tickets spike
// DEBT: [auth] Email-only auth | impact: 15% signup friction | effort: 4h per OAuth provider | trigger: signup abandonment > 20%
// DEBT: [rbac] Two-role only | impact: blocks enterprise contracts | effort: 16h | trigger: first "manager role" request
```

### 3.2 Phase 2: "Finding Fit" — Month 3-6

**Objective**: Reach 100 active users or $1,000 MRR. Use real user behavior to guide which debt to pay.

**Budget**: 85% features, 15% debt payback. In a 40-hour week, this is 6 hours per week of debt work — enough for one meaningful debt retirement per week.

**Priority order for debt payback** (by risk, not by aesthetics):

1. **Any item a user has hit in production** — User-reported problems are the highest-value signal. If three users have complained about an error message being confusing, fix the error handling. If a webhook has failed twice, harden the webhook handler. User pain is empirical evidence that debt has become cost.

2. **Rate limiting before public launch** — The transition from "invite only" to "open signup" is the trigger. Without rate limiting, a single automated signup bot or abuse case can cause disproportionate damage. This graduates from LOW to HIGH at this transition point.

3. **Stripe webhook completeness** — Failed payment recovery (dunning) has direct revenue impact. Every failed payment that is not automatically retried is a lost subscriber. The ROI on implementing dunning is immediate and measurable.

4. **Specific error handling on payment flows** — Users encountering confusing errors during checkout have the highest abandonment rate. This is the highest-leverage UX improvement in Phase 2.

5. **Auth improvements if signup abandonment is measurable** — If analytics show meaningful drop-off at the signup step, add Google OAuth. The 4-6 hour investment pays back quickly at conversion rates of 2-5%.

**Quick wins: debt items that take <1 hour to fix**:
- Adding `Promise.all()` to sequential fetches on a slow page (30 min)
- Extracting a hardcoded configuration constant to an env var (20 min)
- Adding a user-facing error message to the most-complained-about error (45 min)
- Adding Stripe's `invoice.payment_failed` webhook handler (40 min)

**Signs that debt is becoming problematic in Phase 2**:
- A single bug requires touching more than 3 files to fix (coupling is too high)
- Adding a new feature requires modifying a file you did not expect to touch
- You cannot explain to a user why they received an error without reading the source code
- Two production incidents in the same month, both caused by missing edge case handling
- You find yourself manually checking Stripe dashboard for failed payments weekly

**Expected debt inventory at end of Phase 2**: 15-20 items (10-14 paid from Phase 1, 5-8 new from Phase 2 feature development).

### 3.3 Phase 3: "Scaling Up" — Month 6-12

**Objective**: Reach 500+ active users, sustainable MRR, repeatable growth.

**Budget**: 80% features, 20% debt management. At this scale, debt has measurable impact on developer velocity and user experience.

**When to declare a "debt sprint"**:
The trigger is not a calendar date — it is a velocity measurement. When adding a new feature consistently takes 50% longer than comparable features took in Phase 1, it is time for a debt sprint. In practice, this manifests as:
- Every new feature requires changes to 5+ files
- The test suite takes more than 3 minutes to run
- You have had to roll back a deployment in the last 30 days due to an untested edge case
- A new engineer (or your future self after 2 months away) cannot understand a module in under 30 minutes

**Systematic debt reduction plan for Phase 3**:

Week 1 of each month: Inventory review. Run `grep -rn "TODO\|FIXME\|DEBT" --include="*.ts"`. Count items by category. Identify items with multiple related bug reports.

Week 2-3: Feature development. Normal 80/20 split.

Week 4: Debt sprint. Retire 2-3 items from the backlog. Focus on items in the "causing pain" category first, then items with the highest fix-time-to-future-cost ratio.

**How to prevent new debt while paying old**:

The most effective mechanism is the "boy scout rule with a threshold": every pull request that touches a file must leave that file at least as debt-free as it found it. Not perfect — just no net regression. This is enforceable through a custom ESLint rule that counts TODO comments in modified files and fails CI if the count increased.

A second mechanism is the "debt budget per feature": before starting a new feature, estimate how many new debt items it will introduce. If the feature would push the total count above 40, one old item must be retired first. This creates a natural pressure valve.

**Expected state at Month 12**: 10-15 debt items, all low-to-medium interest, none blocking feature development, none causing active user pain.

---

## 4. Real-World SaaS Debt Case Studies

### 4.1 Instagram: 14 Million Users, 3 Engineers, Django — Strategic Debt Done Right

Instagram launched in 2010 on Django/Python — a framework that nobody would call "optimized for scale at billions of users." The founding team chose Django because it enabled 2 engineers with limited backend experience to reach 1 million users within two months of launch.

The debt they accepted: Python's GIL limiting multi-threading, Django ORM generating N+1 queries, no CDN initially, PostgreSQL on a single server.

The debt they did NOT accept: data integrity (every photo was stored with redundant metadata), payment handling (there was none — Instagram was free), user data security (hashed passwords, no plaintext storage from day one).

When they hit scale, they paid debt surgically: profiled hot Python functions and rewrote them in C++, partitioned PostgreSQL horizontally, migrated static assets to CDN. They never did a ground-up rewrite. Today Instagram serves 2 billion monthly active users on the world's largest Django application.

**Lesson for generated SaaS**: Accept performance debt aggressively in Phase 1 — database query optimization, caching, CDN setup, async processing. Never accept data integrity or security debt. Instagram's founders understood this distinction implicitly; our generator must make it explicit.

### 4.2 Twitter: The Fail Whale That Became a $44 Billion Exit

Twitter launched in 2006 on Ruby on Rails — a monolithic, single-threaded framework that becomes a liability under sustained high traffic. The "fail whale" error page became famous because Twitter was literally unavailable during traffic spikes. The technical debt was visible to millions of users.

And yet: Twitter's product-market fit was so strong that users tolerated unavailability and came back. The company went from the fail whale to a $44 billion acquisition, migrating from Rails to Java-based services over several years — a migration that improved throughput from ~300 requests/second/host to 10,000-20,000 requests/second/host (a roughly 50x improvement).

The critical insight: Twitter's debt (architectural coupling, inadequate concurrency model) became a problem at millions of users. For a SaaS targeting 0-1,000 users in Phase 1, that same debt is essentially free. The marginal probability that a Next.js + Supabase application will hit Twitter-scale concurrency problems in its first year is close to zero.

**Lesson for generated SaaS**: Architecture debt (monolith vs. microservices, single-threaded vs. event-driven) is irrelevant until you have a traffic problem. Do not let theoretical future scale drive present architectural decisions. Generate simple, monolithic Next.js applications. Let the founder reach Twitter-scale problems before investing in Twitter-scale solutions.

### 4.3 Shopify: Intentional Monolith at Enormous Scale

Shopify is the most instructive case study for "boring technology at scale." Its Ruby on Rails monolith has processed over $700 billion in gross merchandise volume. In 2022, Shopify was still deploying changes to a monolithic Rails codebase shared by thousands of engineers.

Shopify's approach was not to avoid debt but to manage it with discipline: a 25% rule (one quarter of engineering capacity dedicated to debt reduction), regular "Hack Days" where engineers could pay back any debt they cared about, and a bias toward adding abstractions rather than rewriting consuming code.

The monolith was their strategic debt. They accepted it early, managed it carefully, and never let it compound to crisis point. When they finally began decomposing services, they did so at the pace dictated by actual need, not by architectural fashion.

**Lesson for generated SaaS**: A well-managed monolith outperforms a poorly-managed microservice architecture for a solo founder every time. Generate a monolith with clean internal module boundaries. Reserve the option to extract services later. Shopify's "25% rule" is the professional version of Phase 3's "20% budget" — the principle is identical.

### 4.4 Notion: The Database Rewrite That Almost Killed the Product

Notion's catastrophic slowness in 2019-2020 was a well-documented debt crisis. The founding team had built the product on a schema-less block storage system that worked beautifully at small scale but degraded severely as users created larger and larger documents.

Page loads of 5-10 seconds became normal for power users. The debt was not a missing feature — it was an architectural choice (schema-less blocks) that had exponential cost growth. Notion's team executed a complete database migration in 2020, rewriting core data access while keeping the app running. The migration took roughly 6 months of intensive engineering work.

The context that makes this instructive: Notion accepted this architectural debt in 2016 when they chose schema-less blocks for flexibility. Four years later, the compound interest came due. Had they designed a hybrid system (structured data with flexible block extensions) from the start, the migration would have been unnecessary.

**Lesson for generated SaaS**: The one architectural decision that carries the highest long-term debt cost is the **data model**. Our generator must be highly opinionated about the Supabase schema it generates. Every table should be normalized to at least 2NF from the start. Soft deletes should be in the migration from day one. Timestamps should be present on every row. These are not optional — the cost of migrating the data model after users have data in it is Notion-level expensive.

### 4.5 SaaS Startups That Collapsed Under Debt

While success stories dominate the literature, post-mortems reveal a consistent pattern in SaaS failures attributed to technical debt:

**Pattern 1: Security debt becoming an existential event**. Multiple SaaS companies have failed not from competitive pressure but from security breaches caused by deferred input validation, unrotated API keys, or missing authentication checks. The causal chain is: "fix security later" → breach → user trust destruction → churn → unrecoverable. The debt paydown cost was hours; the breach response cost was the company. This is the definitive case for the Red Line list in Section 2.2.

**Pattern 2: Payment processing debt causing revenue leakage**. Stripe webhooks are reliable, but webhook delivery is "at least once" not "exactly once." Missing idempotency keys on subscription creation caused double-billing incidents at multiple early-stage SaaS companies. A single double-billing incident generates chargebacks, PayPal disputes, and social media damage disproportionate to the financial amount. The fix — idempotency keys — takes 30 minutes. The incident response takes weeks.

**Pattern 3: Data model debt making pivots impossible**. Several B2B SaaS companies built multi-tenancy as an afterthought — storing all user data in shared tables without tenant ID partitioning. When they needed to offer enterprise contracts (requiring data isolation), the migration was so expensive that they lost the deals instead of executing the migration. The data model debt, accumulated over 12 months of "we'll fix it when we need enterprise," prevented the growth motion that could have saved the company.

**Lesson for generated SaaS**: The generator must bake in multi-tenancy from day one — every user data table includes `user_id` as a foreign key AND RLS policies that enforce row-level isolation. This is not enterprise-level complexity. It is a 10-minute template decision that prevents a 4-week migration crisis.

### 4.6 GitHub: Monolith to Microservices on GitHub's Terms

GitHub ran on a Ruby on Rails monolith for over a decade. The codebase grew to one of the largest Rails applications in existence. Rather than following the industry trend toward microservices, GitHub invested in Rails performance (contributing improvements back to Rails), careful database sharding, and Spokes (a distributed Git object storage system).

GitHub's approach to debt: they extracted microservices only where the monolith was genuinely inadequate — Git operations (which needed low-level C performance) and search (which needed Elasticsearch's indexing capabilities). Everything else stayed in the Rails monolith until it became a clear bottleneck.

**Lesson for generated SaaS**: The decision to introduce a microservice should be driven by an observable bottleneck, not by a trend. For generated SaaS, "we need a separate service" is almost never true in the first 12 months. Generate a single Next.js application with Supabase handling all backend concerns. The "separate service" option can be introduced as a debt payback item when the trigger conditions are met.

---

## 5. Debt-Aware Code Generation

The distinguishing feature of this system versus a generic code scaffolding tool is that every generated project must be self-documenting about its debt state. This is accomplished through three mechanisms:

### 5.1 Inline Debt Documentation

Every template shortcut generates not just code but a paired comment block. The comment block is machine-readable, meaning the debt inventory tool can parse it without AI assistance.

```typescript
/**
 * DEBT-ITEM: simple-auth-only
 * Category: authentication
 * Priority: P2 (low)
 * Impact: 15-20% signup friction vs OAuth; no impact on security
 * Effort: 4-6h per OAuth provider (Google, GitHub, Apple)
 * Upgrade path: /docs/debt-upgrades/add-oauth.md
 * Fix trigger: signup abandonment rate > 20% in analytics
 * Phase: 2
 */
export async function signUp(email: string, password: string) {
  return supabase.auth.signUp({ email, password })
}
```

The comment format is parseable with a simple regex. The `query_workflow.py`-style observability tool can scan generated projects and produce a debt dashboard without requiring any manual updates.

### 5.2 Auto-Generated TECHNICAL-DEBT.md

The generator produces a `TECHNICAL-DEBT.md` file alongside the source code. This file is the single source of truth for the project's debt state. It is auto-generated at project creation time and updated by the debt scanning tool on demand.

```markdown
# Technical Debt Inventory
Generated: 2026-03-12
Project: [project-name]
Total items: 22 | Critical: 0 | High: 0 | Medium: 4 | Low: 18

## Upgrade When Ready

### Authentication
- [ ] **Add OAuth providers** | effort: 4-6h/provider | trigger: signup abandonment > 20%
  - Google, GitHub, Apple are the highest-conversion providers
  - Supabase supports all three with ~30 lines of configuration
  - See: `/docs/debt-upgrades/add-oauth.md`

### Permissions
- [ ] **Add custom RBAC roles** | effort: 16h | trigger: first enterprise contract request
  - Current: admin/user only
  - Target: configurable roles with Supabase RLS per-role policies
  - See: `/docs/debt-upgrades/custom-roles.md`

### Payments
- [ ] **Add dunning / failed payment recovery** | effort: 8h | trigger: first failed payment
  - Current: no automatic retry on payment failure
  - Target: 3-attempt retry sequence with customer notification
  - See: `/docs/debt-upgrades/add-dunning.md`
- [ ] **Complete Stripe webhook coverage** | effort: 6h | trigger: plan changes or disputes
  - Missing: invoice.payment_failed, customer.dispute.created, subscription.paused
  - See: `/docs/debt-upgrades/stripe-webhooks.md`

## Red Lines (Never Accept — Already Implemented)
- [x] SQL injection prevention (parameterized queries throughout)
- [x] Webhook signature verification (Stripe.webhooks.constructEvent)
- [x] Soft deletes on all user data tables
- [x] Idempotency keys on payment API calls
- [x] Environment variable validation at startup
- [x] RLS policies on all user-facing tables
- [x] requireAuth() guard on authenticated routes
- [x] PII sanitization in logging utilities

## Debt Score: 22/50 (Acceptable for Phase 1)
Threshold alerts: ⚠️ >30 items: review required | 🚨 >45 items: debt sprint required
```

### 5.3 Upgrade Path Guides

Each debt item in `TECHNICAL-DEBT.md` links to a structured upgrade guide in `/docs/debt-upgrades/`. These guides are generated alongside the project and are specific to the generated project's stack configuration:

```markdown
# Upgrade Guide: Add Google OAuth

## When to do this
Trigger: Signup abandonment rate exceeds 20% in your analytics.
Typical timing: Month 2-4 depending on marketing channel mix.

## Time estimate: 4-6 hours

## Steps
1. Enable Google OAuth in Supabase dashboard (15 min)
2. Add Google Cloud OAuth credentials (30 min)
3. Add Sign in with Google button to auth pages (1h)
4. Test login → callback → session persistence (30 min)
5. Handle email collision (user signs up with Google but has existing email account) (1-2h)

## Test cases to add
- [ ] Google OAuth flow completes and creates session
- [ ] Returning Google user logs in without creating duplicate account
- [ ] Google OAuth failure returns user to login page with message

## Code changes
- `src/components/auth/LoginForm.tsx` — add OAuth button
- `src/app/auth/callback/route.ts` — already scaffolded, verify callback URL
- No database changes required (Supabase Auth handles provider storage)
```

### 5.4 Debt Score and Threshold Alerts

Each generated project includes a `debt-score.ts` utility that can be run as part of CI:

```typescript
// Usage: pnpm run debt-score
// Scans for DEBT-ITEM comments, computes score, exits with non-zero if threshold exceeded

const DEBT_THRESHOLDS = {
  review_required: 30,    // warn in CI output
  sprint_required: 45,    // fail CI with recommendation
  critical_required: 1,   // fail CI immediately (high/critical debt items)
}
```

The debt score is not a blocker by default — it is advisory. But it surfaces in the CI output on every run, making debt accumulation visible rather than invisible.

### 5.5 Progressive Enhancement Patterns

The generator uses feature flags to encode "start simple, enable complexity later" patterns without requiring code rewrites:

```typescript
// Generated configuration
export const FEATURES = {
  // Phase 1: Disabled. Enable in Phase 2 when trigger conditions are met.
  oauth: {
    google: env.NEXT_PUBLIC_GOOGLE_AUTH_ENABLED === 'true',
    github: env.NEXT_PUBLIC_GITHUB_AUTH_ENABLED === 'true',
  },
  // Phase 1: Basic two-role RBAC. Set to true after implementing custom roles.
  custom_rbac: env.CUSTOM_RBAC_ENABLED === 'true',
  // Phase 1: English only. Set to true after adding i18n strings.
  i18n: env.I18N_ENABLED === 'true',
  // Phase 1: Manual rate limiting. Enable when going public.
  rate_limiting: env.RATE_LIMITING_ENABLED === 'true',
}
```

This pattern means the founder can enable a new capability with an environment variable change, without touching the generated code. The upgrade path is additive, not rewrite-based.

---

## 6. Cost-Benefit Analysis

### 6.1 Speed Gains by Debt Category

The following estimates are based on a typical Next.js + Supabase SaaS with ~10 pages and a standard subscription billing model:

| Debt Category | Time Saved in Phase 1 | Future Paydown Cost | Net Gain |
|---------------|----------------------|--------------------| ---------|
| Email-only auth | 6-8h saved | 4-6h per provider | +2-4h per provider |
| Two-role RBAC | 10-14h saved | 16h paydown | -2 to -6h (slight loss, but timing-optimized) |
| Catch-all error handling | 8-12h saved | 2-4h per flow | +4-8h total |
| No rate limiting (Phase 1) | 4-6h saved | 4-8h paydown | 0-2h net |
| Simplified Stripe | 12-16h saved | 8-16h paydown | 0-8h net |
| Hardcoded config | 4-6h saved | 4-8h paydown | 0-2h net |
| Single language | 8-12h saved | 16-40h paydown | -4 to -28h (but only if i18n needed) |
| **Total green zone** | **~52-74h saved** | **~54-98h eventual** | **~2-20h net Phase 1** |

The net gain column shows a counterintuitive result: the raw time savings from debt acceptance approximately equal the future paydown cost. So why accept the debt at all?

The answer is timing. The 52-74 hours saved in Phase 1 are worth dramatically more than the 54-98 hours of paydown in Phase 2-3, for three reasons:

1. **Revenue acceleration**: Shipping 6 weeks earlier at even modest conversion rates produces meaningful MRR while the debt is being serviced.

2. **Information value**: Phase 1 user feedback tells you exactly which debt items to pay back first and which to defer indefinitely. The founder who ships with email-only auth discovers whether OAuth abandonment is actually happening — or whether their users are enterprise buyers who use SSO and never cared about Google OAuth anyway. Debt paydown is guided by data, not by speculation.

3. **Survival probability**: For a bootstrapped founder, shipping fast increases the probability of reaching product-market fit before runway runs out. The probability gain from earlier shipping is more valuable than the cost savings from debt avoidance.

### 6.2 Revenue Impact Model

For a typical SaaS with a $29/month Pro tier and 2% conversion rate from free trial:

```
Scenario A: Ship with full green-zone debt (Month 3 launch)
  Week 12: First paying users
  Month 3-6 revenue (ramping from 0): ~$2,400
  Month 6 MRR: ~$580 (20 subscribers)
  Debt paydown cost in Month 4-6: ~30 hours
  Revenue at Month 6: $2,400

Scenario B: Pay all debt before launch (Month 5 launch)
  Week 20: First paying users
  Month 5-6 revenue (ramping from 0): ~$580
  Month 6 MRR: ~$580 (20 subscribers, same rate)
  No debt paydown cost, but 8 weeks of additional build time
  Revenue at Month 6: $580

Revenue advantage of Scenario A: $1,820 in Month 3-6
```

The $1,820 advantage understates the real benefit because it ignores:
- User feedback gathered in Months 3-5 that allows feature prioritization
- Word-of-mouth and community building that compounds over time
- The psychological advantage of real users providing motivation and direction

At $500/month MRR, a 2-month earlier launch is worth $1,000 in recovered revenue plus the compounding effect of 2 additional months of user acquisition. At $5,000/month MRR, the same 2-month advantage is worth $10,000 — enough to justify hiring a contractor for the debt paydown work.

### 6.3 Net Present Value Calculation

The NPV framework treats debt as a loan. The interest rate is the rate at which the debt cost grows over time.

For **low-interest debt** (linear growth):
- Cost to fix at Month 1: 4h
- Cost to fix at Month 6: 6h (50% more, because there is more code to update)
- NPV of deferring: borrow 4h of work, pay back 6h in 5 months
- "Interest rate": 10% per month — acceptable if the revenue acceleration justifies it

For **medium-interest debt** (polynomial growth):
- Cost to fix at Month 1: 8h
- Cost to fix at Month 6: 20h (150% more, because the pattern has spread to multiple files)
- NPV of deferring: borrow 8h of work, pay back 20h in 5 months
- "Interest rate": 30% per month — expensive, but still justified if Phase 1 revenue covers the spread

For **high-interest debt** (exponential growth — the Red Lines):
- Cost to fix at Month 1: 2h (add idempotency keys)
- Cost to fix after a double-billing incident: 40+ hours (incident response, user compensation, chargeback resolution, trust recovery)
- NPV of deferring: infinite negative — the expected value is negative regardless of timing
- Conclusion: never defer; the "interest rate" is undefined when the debt can destroy the product

**At what MRR does debt payback become easily affordable?**
- $1,000 MRR: debt paydown work must be done by the founder; 30h of paydown = meaningful time cost but manageable
- $3,000 MRR: founder can afford 10h/month of contractor time for debt reduction
- $10,000 MRR: dedicated part-time engineer for systematic debt reduction
- $30,000 MRR: a debt sprint (2-week focused cleanup) every quarter is affordable and appropriate

The generator should include this MRR-to-debt-investment ladder in the `TECHNICAL-DEBT.md` output, so founders have a concrete framework for when to invest in paydown.

---

## 7. Debt Management in Practice: The Generated Project Workflow

### 7.1 Developer Experience for Debt Visibility

The generated project includes three commands that make debt management frictionless:

```bash
# Show current debt inventory (parses DEBT-ITEM comments, formats as table)
pnpm debt:list

# Show debt items that have passed their trigger condition
# (requires connecting to analytics — optional)
pnpm debt:triggered

# Update TECHNICAL-DEBT.md from current codebase scan
pnpm debt:update

# Show debt score and threshold status
pnpm debt:score
```

These commands are implemented as simple scripts in `scripts/debt-manager.ts`. They require no external services and run in under 5 seconds.

### 7.2 Monthly Debt Collection Protocol

The generated README includes this protocol as a recurring task:

Every 4 weeks (30-minute session):
1. Run `pnpm debt:list` — note total count and any new medium/high items (5 min)
2. Review which items are causing active pain (user complaints, slow debugging) (10 min)
3. Identify 1-2 quick wins (<2h each) and add to next week's sprint (5 min)
4. Update triggers — have any conditions been met? (5 min)
5. Run `pnpm debt:update` to refresh the inventory file (5 min)

Total: 30 minutes per month. This is the minimum effective debt management cadence.

### 7.3 Integration With the Broader Generator System

The debt management system connects to the generator's other outputs:

- **PRD → Debt alignment**: Features described in the PRD that imply deferred complexity (e.g., "basic auth for now, enterprise SSO later") generate corresponding DEBT-ITEM entries automatically
- **TRD → Red Line validation**: The technical requirements document specifies which Red Line items are non-negotiable; the generator validates that every generated project includes them before output
- **AGENTS.md → Debt-aware AI assistance**: The generated AGENTS.md instructs AI coding assistants to check debt items before implementing new features that touch the same modules

---

## 8. Conclusion and Recommended Strategy

### 8.1 The Recommended Debt Strategy for Generated SaaS

For a solo founder building a SaaS targeting product-market fit in 6 months:

**Month 1-3**: Ship aggressively. Accept all green-zone debt. Enforce all Red Lines. Document every shortcut with machine-readable TODO comments. Target: first paying user by end of Month 3.

**Month 3-6**: Let user behavior guide payback. Prioritize by: (1) items users have actually hit, (2) rate limiting before public launch, (3) payment handling completeness, (4) auth friction if measurable. Target: <25 debt items, none causing active user pain.

**Month 6-12**: Systematic 20% investment. Monthly debt collection sessions. One "debt sprint" if count exceeds 40. Target: stable 10-15 item inventory of low-priority items. Developer velocity maintained at >80% of Month 1 peak.

### 8.2 The Generator's Responsibility

The generator system does not just produce code — it produces a project with a known, documented debt state. This is the differentiation from generic scaffolding tools. The founder receives:

1. A clear inventory of every shortcut taken and why
2. Trigger conditions written in plain language for when to fix each item
3. Upgrade path guides that make paydown straightforward
4. A debt score that makes accumulation visible
5. Red Line enforcement that makes catastrophic debt impossible

This framework changes the relationship between the founder and their codebase. Technical debt is no longer a vague concern that grows invisibly — it is a managed portfolio with known items, known costs, and clear ROI signals for when to invest in paydown.

### 8.3 The One-Sentence Version

Ship with 20 managed, documented debt items at Month 3. Learn from real users which ones matter. Pay those back in Month 4-6. Arrive at Month 12 with a healthy codebase, real revenue, and the discipline to keep debt under control.

That is the strategy.

---

## Sources

- [Paying Down Tech Debt — The Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/paying-down-tech-debt)
- [Technical Debt: From Metaphor to Theory and Practice — IEEE Software](https://ieeexplore.ieee.org/document/6336722)
- [The 25 Percent Rule for Tackling Technical Debt — Shopify Engineering](https://shopify.engineering/technical-debt-25-percent-rule)
- [How Instagram Scaled to 14 Million Users with Only 3 Engineers — Engineer's Codex](https://read.engineerscodex.com/p/how-instagram-scaled-to-14-million)
- [A Real-World Technical Debt Example: Twitter — Beyond Runtime](https://beyondruntime.substack.com/p/a-real-world-technical-debt-example)
- [When Your Tech Debt Comes Due — Kevin Scott (LinkedIn)](https://www.linkedin.com/pulse/when-your-tech-debt-comes-due-kevin-scott)
- [How Shopify Builds for Scale — Shopify Engineering Blog](https://shopify.engineering/)
- [Notion's Database Architecture and the 2020 Performance Migration — Notion Engineering](https://www.notion.so/blog/the-great-db-migration)
- [GitHub's Journey from Rails Monolith — GitHub Engineering](https://github.blog/engineering/)
- [I Analyzed 70 Startups' Codebases: More Technical Debt = More Funding — ByteVagabond](https://bytevagabond.com/post/technical-debt-startup-funding/)
- [Breaking Technical Debt's Vicious Cycle — McKinsey Digital](https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/breaking-technical-debts-vicious-cycle-to-modernize-your-business)
- [Technical Debt Management Strategies for Growing Startups — Technori](https://technori.com/2026/02/24479-technical-debt-management-strategies-for-growing-startups/gabriel/)
- [The Compounding ROI of Technical Debt — StartupBooted](https://www.startupbooted.com/the-compounding-roi-of-technical-debt-a-framework-for-calculating-and-managing-future-liability)
- [Stripe Webhook Best Practices — Stripe Documentation](https://stripe.com/docs/webhooks/best-practices)
- [Supabase Row Level Security Guide — Supabase Documentation](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [bliki: TechnicalDebt — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebt.html)
- [The Technical Debt Quadrant — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [What 4 Months of Solo SaaS Building Taught Me — dev.to](https://dev.to/st_vladyslav/what-4-months-of-solo-saas-building-taught-me-the-hard-way-1ed8)
- [Stabilize, Modularize, Modernize: Scaling Slack's Mobile Codebases](https://slack.engineering/stabilize-modularize-modernize-scaling-slacks-mobile-codebases/)
- [Technical Debt in 2026: Everything You Need to Know to Win — Scala AI](https://scalaai.it/en/technical-debt-guide-en-v4b-354/)
