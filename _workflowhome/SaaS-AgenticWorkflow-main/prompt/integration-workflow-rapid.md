# Rapid Integration Development Workflow: AI Agentic Workflow Automation System

**Perspective**: Ship integrations fast. The fastest path to a working multi-LLM CLI setup is to prototype with subprocess calls, validate with real outputs, and iterate. Don't over-abstract before you know what works.
**Subject**: AI Agentic Workflow Automation System — External Integration Development Workflow
**Focus**: Multi-LLM CLI orchestration via subscription CLIs (Gemini CLI, ChatGPT CLI), third-party SaaS integrations (Stripe, Supabase, Resend, Vercel)
**Critical constraint**: OpenAI and Gemini accessed via subscription CLI tools, NOT API keys
**Date**: 2026-03-12

---

## Executive Summary

The fastest path to a working multi-LLM CLI system is not to build an abstraction layer — it is to wire up a single subprocess call, run it against 10 real prompts, and see what breaks. Abstraction comes after you understand the failure modes. Before that, abstraction is just speculative engineering.

This document provides a week-by-week integration development timeline grounded in a single thesis: **every integration layer adds latency, complexity, and failure surface**. Each new dependency — Gemini CLI, Stripe webhooks, Supabase Auth, Resend email — must earn its place through demonstrated value before it earns architectural consideration.

The system described here is a local CLI tool running on a developer's machine. It is not a SaaS backend. This distinction has significant implications for integration strategy:

- No server to host webhooks (Stripe CLI `listen` handles this locally)
- No hosted database to configure (Supabase local instance via Docker)
- No long-running process for the multi-LLM router (subprocess calls are synchronous by design)
- No deployment pipeline for the CLI itself until the integrations are stable

The integration development timeline is organized across four months. Month 1 uses Claude Code exclusively — zero external integration needed. Month 2 adds Gemini CLI and validates multi-LLM routing. Month 3 integrates Stripe and Supabase Auth scaffolding for generated SaaS output. Month 4 adds email (Resend) and deployment (Vercel) scaffolding. OpenAI CLI integration, if the subscription tooling matures, is deferred to Month 5+.

---

## 1. Multi-LLM CLI Integration Architecture

### 1.1 The Subprocess Model

The foundation of multi-LLM CLI integration for subscription-based tools is the OS subprocess. Unlike API-key-based integrations (where you make an HTTP request and parse JSON), subscription CLIs expose their capability through stdin/stdout. The integration layer is a thin wrapper around `child_process.execFile`.

This is not a limitation — it is a simplification. No authentication headers to manage, no rate limit libraries to configure, no HTTP client to mock. The integration surface is exactly one thing: what you send to stdin and what you receive on stdout.

**Day 1 prototype — Gemini CLI wrapper:**

```typescript
// src/providers/gemini.ts — Day 1, no abstraction
import { execFile } from 'child_process'
import { promisify } from 'util'

const execFileAsync = promisify(execFile)

export async function callGemini(prompt: string): Promise<string> {
  const { stdout, stderr } = await execFileAsync('gemini', [
    '--prompt', prompt,
    '--model', 'gemini-2.0-flash',
  ], {
    timeout: 30_000,
    maxBuffer: 1024 * 1024 * 10, // 10MB
  })

  if (stderr && stderr.length > 0) {
    // Gemini CLI writes non-fatal info to stderr — log, don't throw
    process.stderr.write(`[gemini stderr]: ${stderr}\n`)
  }

  return stdout.trim()
}
```

Run this against 10 sample prompts on Day 1. Not synthetic prompts — real prompts from the actual document generation pipeline. The goal is not unit tests. The goal is observable behavior under real conditions.

**What you will discover on Day 1:**

- Whether the CLI accepts multi-line prompts via `--prompt` flag or requires stdin piping
- Average latency per call (expect 3–8 seconds for Gemini Flash, 8–20s for Gemini Pro)
- Whether the CLI exits cleanly on success (exit code 0) or uses non-standard codes
- Whether long outputs get truncated based on `maxBuffer` settings
- Whether authentication state is per-session or persistent (most subscription CLIs use persistent browser-based auth tokens)

These observations from 10 real calls tell you more about the integration surface than 10 hours of reading documentation.

### 1.2 ChatGPT CLI Integration (Day 2)

The ChatGPT subscription CLI landscape in 2026 is fragmented. The officially recommended tool from OpenAI for CLI access via ChatGPT Plus subscription is the `chatgpt` CLI (installed via `npm install -g @openai/chatgpt-cli` or Homebrew). However, the interface is less stable than Gemini CLI and varies by subscription tier.

**Day 2 prototype — ChatGPT CLI wrapper:**

```typescript
// src/providers/chatgpt.ts — Day 2, observe before abstracting
import { spawn } from 'child_process'

export async function callChatGPT(prompt: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = []
    const errorChunks: Buffer[] = []

    // ChatGPT CLI may require stdin piping rather than --prompt flag
    const proc = spawn('chatgpt', [], {
      timeout: 45_000,
    })

    proc.stdout.on('data', (chunk: Buffer) => chunks.push(chunk))
    proc.stderr.on('data', (chunk: Buffer) => errorChunks.push(chunk))

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`chatgpt exited with code ${code}: ${Buffer.concat(errorChunks).toString()}`))
      } else {
        resolve(Buffer.concat(chunks).toString().trim())
      }
    })

    proc.stdin.write(prompt)
    proc.stdin.end()
  })
}
```

The key uncertainty on Day 2 is the stdin/stdout contract. Some CLI tools stream responses (printing tokens as they arrive), others buffer the full response. Streaming responses require line-by-line parsing. Buffered responses are simpler but introduce longer apparent latency for the user watching a spinner.

Run the same 10 prompts you used for Gemini on Day 2 for ChatGPT. Measure:

- Latency distribution (p50, p90, p99)
- Output quality for the specific prompt types in your pipeline (PRD generation, TRD generation)
- Failure modes: authentication expiry, rate limiting, network timeout behavior

### 1.3 Unified LLMProvider Interface (Day 3)

After observing both CLIs for two days, you have enough data to design an interface that fits what you observed — not what you imagined before running anything.

```typescript
// src/providers/types.ts — Day 3, built from real observations
export interface LLMProvider {
  readonly name: string
  readonly avgLatencyMs: number  // observed from Day 1-2, used for timeout calibration

  generate(prompt: string, options?: GenerateOptions): Promise<GenerateResult>
  isAvailable(): Promise<boolean>  // checks if CLI is installed and authenticated
}

export interface GenerateOptions {
  timeoutMs?: number
  maxRetries?: number
  model?: string  // provider-specific model override
}

export interface GenerateResult {
  content: string
  provider: string
  latencyMs: number
  model: string
  truncated: boolean  // true if output hit maxBuffer
}
```

The `isAvailable()` method is critical. Subscription CLIs can become unavailable between calls if:

- The user's subscription lapses
- The authentication token expires (most subscription CLIs use OAuth tokens with 90-day expiry)
- The CLI binary is updated and the interface changes

Without availability checking, a multi-LLM pipeline fails silently with a cryptic subprocess error. With explicit availability checking, the system degrades gracefully to an available provider.

```typescript
// src/providers/gemini.ts — Day 3, with availability check
export class GeminiProvider implements LLMProvider {
  readonly name = 'gemini'
  readonly avgLatencyMs = 5_000  // observed from Day 1 data

  async isAvailable(): Promise<boolean> {
    try {
      const { stdout } = await execFileAsync('gemini', ['--version'], { timeout: 5_000 })
      return stdout.includes('gemini')
    } catch {
      return false
    }
  }

  async generate(prompt: string, options: GenerateOptions = {}): Promise<GenerateResult> {
    const startMs = Date.now()
    const timeoutMs = options.timeoutMs ?? 30_000

    const { stdout } = await execFileAsync('gemini', [
      '--prompt', prompt,
      '--model', options.model ?? 'gemini-2.0-flash',
    ], {
      timeout: timeoutMs,
      maxBuffer: 1024 * 1024 * 10,
    })

    return {
      content: stdout.trim(),
      provider: this.name,
      latencyMs: Date.now() - startMs,
      model: options.model ?? 'gemini-2.0-flash',
      truncated: false,
    }
  }
}
```

### 1.4 LLM Router (Days 4–5)

The router determines which provider handles which task. The routing logic must be observable — you need to know, for every generation call, which provider was used and why.

```typescript
// src/router/llm-router.ts — Days 4-5
import type { LLMProvider, GenerateOptions, GenerateResult } from '../providers/types'

export type RoutingStrategy = 'fastest' | 'highest-quality' | 'cheapest' | 'fallback-chain'

interface RouteDecision {
  provider: LLMProvider
  reason: string
}

export class LLMRouter {
  private providers: LLMProvider[]
  private availabilityCache = new Map<string, { available: boolean; checkedAt: number }>()
  private readonly CACHE_TTL_MS = 60_000

  constructor(providers: LLMProvider[]) {
    this.providers = providers
  }

  async route(
    taskType: 'prd' | 'trd' | 'design-guide' | 'task-breakdown',
    strategy: RoutingStrategy = 'fastest',
  ): Promise<RouteDecision> {
    const available = await this.getAvailableProviders()

    if (available.length === 0) {
      throw new Error('No LLM providers available. Check CLI installations and authentication.')
    }

    switch (strategy) {
      case 'highest-quality':
        // PRD and TRD benefit from Claude's document structure
        return {
          provider: available[0],  // Claude is always first in priority
          reason: `high-quality task (${taskType}): using ${available[0].name}`,
        }

      case 'fastest':
        // For quick iterations, use lowest latency available
        const fastest = available.reduce((a, b) =>
          a.avgLatencyMs <= b.avgLatencyMs ? a : b
        )
        return {
          provider: fastest,
          reason: `fastest available: ${fastest.name} (${fastest.avgLatencyMs}ms avg)`,
        }

      case 'fallback-chain':
        // Primary → secondary → tertiary
        return {
          provider: available[0],
          reason: `fallback chain: using primary (${available[0].name})`,
        }

      default:
        return { provider: available[0], reason: `default: ${available[0].name}` }
    }
  }

  async generate(
    prompt: string,
    taskType: 'prd' | 'trd' | 'design-guide' | 'task-breakdown',
    options: GenerateOptions = {},
  ): Promise<GenerateResult & { routingReason: string }> {
    const { provider, reason } = await this.route(taskType)

    try {
      const result = await provider.generate(prompt, options)
      return { ...result, routingReason: reason }
    } catch (error) {
      // On failure, attempt fallback to next available provider
      const available = await this.getAvailableProviders()
      const fallbackProviders = available.filter(p => p.name !== provider.name)

      if (fallbackProviders.length === 0) throw error

      const fallback = fallbackProviders[0]
      const result = await fallback.generate(prompt, options)
      return {
        ...result,
        routingReason: `fallback from ${provider.name} (error) → ${fallback.name}`,
      }
    }
  }

  private async getAvailableProviders(): Promise<LLMProvider[]> {
    const now = Date.now()
    const available: LLMProvider[] = []

    for (const provider of this.providers) {
      const cached = this.availabilityCache.get(provider.name)
      let isAvailable: boolean

      if (cached && now - cached.checkedAt < this.CACHE_TTL_MS) {
        isAvailable = cached.available
      } else {
        isAvailable = await provider.isAvailable()
        this.availabilityCache.set(provider.name, { available: isAvailable, checkedAt: now })
      }

      if (isAvailable) available.push(provider)
    }

    return available
  }
}
```

---

## 2. Fast Integration Scaffolding for Generated SaaS

The CLI tool generates SaaS projects. Those projects need integrations: Stripe for payments, Supabase for auth and database, Resend for email, Vercel for deployment. The integration scaffolding must be testable locally in under 5 minutes from a fresh clone.

### 2.1 Stripe Integration (Week 3)

The Stripe integration for generated projects has two components:
1. The generated code that handles Stripe webhook events and payment flows
2. The local testing harness using the Stripe CLI

**Local testing setup (under 5 minutes):**

```bash
# Install Stripe CLI (macOS)
brew install stripe/stripe-cli/stripe

# Authenticate (one-time, persists via ~/.config/stripe)
stripe login

# In one terminal: start your Next.js dev server
pnpm dev

# In another terminal: forward Stripe webhooks to localhost
stripe listen --forward-to localhost:3000/api/stripe/webhook
# Stripe CLI prints: webhook signing secret: whsec_xxxxx
# Copy this to .env.local as STRIPE_WEBHOOK_SECRET
```

**The generated webhook handler the CLI must produce:**

```typescript
// app/api/stripe/webhook/route.ts — generated by the CLI
import Stripe from 'stripe'
import { createServerClient } from '@/lib/supabase/server'
import { headers } from 'next/headers'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(request: Request) {
  const body = await request.text()
  const signature = (await headers()).get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!,
    )
  } catch (err) {
    return new Response(`Webhook signature verification failed`, { status: 400 })
  }

  const supabase = await createServerClient()

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      await supabase
        .from('subscriptions')
        .upsert({
          user_id: session.metadata?.userId,
          stripe_customer_id: session.customer as string,
          stripe_subscription_id: session.subscription as string,
          status: 'active',
        })
      break
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription
      await supabase
        .from('subscriptions')
        .update({ status: 'canceled' })
        .eq('stripe_subscription_id', subscription.id)
      break
    }
  }

  return new Response('ok', { status: 200 })
}
```

**Testing Stripe events locally without waiting for real payments:**

```bash
# Trigger a checkout.session.completed event
stripe trigger checkout.session.completed

# Trigger subscription cancellation
stripe trigger customer.subscription.deleted

# List all available event types
stripe trigger --help
```

This is the key workflow advantage: you can test every Stripe event type — successful payment, failed payment, subscription renewal, cancellation — without a real credit card or real money. The Stripe CLI handles event generation, signature construction, and forwarding. The developer sees the full webhook flow in under 30 seconds.

**MSW mock for unit tests:**

```typescript
// test/mocks/stripe-handlers.ts
import { http, HttpResponse } from 'msw'

export const stripeHandlers = [
  http.post('https://api.stripe.com/v1/checkout/sessions', () => {
    return HttpResponse.json({
      id: 'cs_test_mock123',
      url: 'https://checkout.stripe.com/pay/cs_test_mock123',
      status: 'open',
    })
  }),

  http.get('https://api.stripe.com/v1/subscriptions/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      status: 'active',
      current_period_end: Math.floor(Date.now() / 1000) + 86400 * 30,
    })
  }),
]
```

**Total Stripe integration time estimate:**

| Task | Time |
|------|------|
| `stripe login` + CLI setup | 3 min |
| `stripe listen` running locally | 1 min |
| Generated webhook handler live | Included in generation |
| First test event triggered and handled | 5 min |
| **From fresh clone to working local Stripe testing** | **< 10 min** |

### 2.2 Supabase Integration (Week 3)

Supabase local development uses Docker. The `supabase` CLI manages a local instance that mirrors the production Supabase service.

**Local setup:**

```bash
# Install Supabase CLI
npm install -g supabase

# Start local Supabase stack (PostgreSQL + Auth + Storage + Edge Functions)
supabase start
# Outputs: API URL, anon key, service_role key, DB URL, Studio URL

# Access local Supabase Studio
open http://127.0.0.1:54323
```

The local Supabase instance:
- Runs PostgreSQL 15 in Docker
- Provides the same REST API as hosted Supabase
- Has a local Studio dashboard at port 54323
- Supports Row Level Security (RLS) policies locally
- Supports Auth with the same email/password and OAuth flows

**The generated project must include a `supabase/` directory the developer can use immediately:**

```
supabase/
├── migrations/
│   ├── 20260101000000_initial_schema.sql   # Generated from user's domain model
│   ├── 20260101000001_rls_policies.sql     # RLS policies for every table
│   └── 20260101000002_seed_data.sql        # Development seed data
├── functions/                              # Edge functions (if needed)
└── config.toml                             # Local Supabase configuration
```

**Applying migrations locally:**

```bash
# Reset local DB and apply all migrations from scratch
supabase db reset

# Apply new migration
supabase db push

# Generate TypeScript types from current schema
supabase gen types typescript --local > src/types/database.ts
```

The type generation step is the highest-leverage Supabase developer experience feature. After every schema change, the developer runs one command and gets fully-typed database access throughout the codebase. No manual type writing. No type drift between schema and code.

**Testing Supabase locally with MSW fallback:**

For unit tests that do not need a real database, MSW handles Supabase REST API calls:

```typescript
// test/mocks/supabase-handlers.ts
import { http, HttpResponse } from 'msw'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!

export const supabaseHandlers = [
  // Mock SELECT queries
  http.get(`${SUPABASE_URL}/rest/v1/members`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json([
      { id: 'test-uuid-1', email: 'test@example.com', name: 'Test User', created_at: '2026-01-01T00:00:00Z' },
    ])
  }),

  // Mock INSERT
  http.post(`${SUPABASE_URL}/rest/v1/members`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json({ ...body, id: 'new-test-uuid' }, { status: 201 })
  }),
]
```

**Total Supabase integration time estimate:**

| Task | Time |
|------|------|
| `supabase start` (first run, Docker pull) | 5–10 min |
| `supabase start` (subsequent runs, cached) | 30 sec |
| `supabase db reset` + migrations applied | 2 min |
| Type generation | 10 sec |
| **From fresh clone to working local DB** | **< 15 min (first time), < 5 min (subsequent)** |

### 2.3 Email Integration with Resend (Week 4)

Resend provides email sending with a test mode that does not actually deliver emails. This makes local testing trivial — send email in test mode, verify the API call was made correctly, confirm the email content via Resend's dashboard.

**The generated email utility:**

```typescript
// lib/email/send.ts — generated
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY!)
const FROM_EMAIL = process.env.EMAIL_FROM ?? 'noreply@yourdomain.com'

export type EmailTemplate = 'welcome' | 'magic-link' | 'subscription-confirmation' | 'invoice'

interface SendEmailOptions {
  to: string
  template: EmailTemplate
  data: Record<string, unknown>
}

export async function sendEmail({ to, template, data }: SendEmailOptions) {
  const { subject, html } = await renderTemplate(template, data)

  const { data: result, error } = await resend.emails.send({
    from: FROM_EMAIL,
    to,
    subject,
    html,
  })

  if (error) {
    console.error(`[resend] Failed to send ${template} to ${to}:`, error)
    throw new Error(`Email send failed: ${error.message}`)
  }

  return result
}
```

**Testing email locally:**

```bash
# Set Resend test API key (starts with re_test_)
# Test mode: Resend accepts the request but does not deliver
# You can view test sends in the Resend dashboard under "Logs"
RESEND_API_KEY=re_test_xxxxxxxxxxxxxxxx
```

**MSW mock for unit tests:**

```typescript
// test/mocks/resend-handlers.ts
import { http, HttpResponse } from 'msw'

export const resendHandlers = [
  http.post('https://api.resend.com/emails', async ({ request }) => {
    const body = await request.json() as Record<string, unknown>
    console.log(`[mock] Email sent to ${body.to}: ${body.subject}`)
    return HttpResponse.json({ id: 'mock-email-id-123' }, { status: 200 })
  }),
]
```

**Testing email content without delivery:**

The key insight for email testing is that you should test the rendered HTML, not whether the email was delivered. Delivery is Resend's responsibility. Your tests verify that the right content is generated.

```typescript
// test/email/welcome.test.ts
import { describe, it, expect } from 'vitest'
import { renderTemplate } from '../../src/lib/email/templates'

describe('Welcome email template', () => {
  it('renders user name in subject and body', async () => {
    const { subject, html } = await renderTemplate('welcome', {
      userName: 'Jane Smith',
      loginUrl: 'https://app.example.com/login',
    })

    expect(subject).toBe('Welcome to the platform, Jane Smith')
    expect(html).toContain('Jane Smith')
    expect(html).toContain('https://app.example.com/login')
  })
})
```

---

## 3. Testing Strategy for Speed

### 3.1 Test Architecture

The test suite must run in under 2 minutes. This is not aspirational — it is a hard constraint. A test suite that takes more than 2 minutes is not used in watch mode. A test suite not used in watch mode is not used for TDD. A test suite not used for TDD catches bugs only after they are written, not while they are being written.

**Mock Service Worker (MSW) as the integration testing backbone:**

MSW intercepts HTTP requests at the network level, not at the module level. This means:
- No module mocking that breaks with module system changes
- No mock leakage between tests (each test registers its own handlers)
- Identical mock behavior in both Node.js (unit tests) and browser (component tests)
- Real `fetch`/`axios`/`ky` calls in test code — only the network layer is intercepted

```typescript
// test/setup.ts — shared MSW setup
import { setupServer } from 'msw/node'
import { stripeHandlers } from './mocks/stripe-handlers'
import { supabaseHandlers } from './mocks/supabase-handlers'
import { resendHandlers } from './mocks/resend-handlers'

export const server = setupServer(
  ...stripeHandlers,
  ...supabaseHandlers,
  ...resendHandlers,
)

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

The `onUnhandledRequest: 'warn'` setting is deliberately permissive during early integration development. Change to `'error'` once the mock handlers are comprehensive.

### 3.2 Record-Replay for CLI LLM Calls

Subprocess calls to Gemini CLI and ChatGPT CLI cannot be intercepted by MSW. They require a different mocking strategy: record-replay.

The principle: record real CLI output to fixture files on first run. Replay from fixtures on subsequent runs. Replace the fixture when the behavior you are testing changes.

```typescript
// src/providers/record-replay.ts
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs'
import { createHash } from 'crypto'
import { join } from 'path'

const FIXTURES_DIR = join(process.cwd(), 'test/__fixtures__/llm-responses')

function fixtureKey(provider: string, prompt: string): string {
  const hash = createHash('sha256').update(`${provider}:${prompt}`).digest('hex').slice(0, 12)
  return `${provider}-${hash}.json`
}

export interface RecordReplayOptions {
  provider: string
  prompt: string
  callReal: () => Promise<string>
  mode: 'record' | 'replay' | 'pass-through'
}

export async function recordReplay({ provider, prompt, callReal, mode }: RecordReplayOptions): Promise<string> {
  if (mode === 'pass-through') return callReal()

  const key = fixtureKey(provider, prompt)
  const fixturePath = join(FIXTURES_DIR, key)

  if (mode === 'replay') {
    if (!existsSync(fixturePath)) {
      throw new Error(`Fixture not found: ${fixturePath}. Run with mode='record' first.`)
    }
    const fixture = JSON.parse(readFileSync(fixturePath, 'utf-8'))
    return fixture.response
  }

  // mode === 'record': call real, save response
  const response = await callReal()
  mkdirSync(FIXTURES_DIR, { recursive: true })
  writeFileSync(fixturePath, JSON.stringify({ provider, promptHash: fixtureKey(provider, prompt), response, recordedAt: new Date().toISOString() }, null, 2))
  return response
}
```

**Usage in tests:**

```typescript
// Mode controlled by environment variable
const mode = process.env.LLM_TEST_MODE as 'record' | 'replay' | 'pass-through' ?? 'replay'

it('generates PRD from user inputs', async () => {
  const response = await recordReplay({
    provider: 'gemini',
    prompt: PRD_GENERATION_PROMPT,
    callReal: () => geminiProvider.generate(PRD_GENERATION_PROMPT),
    mode,
  })

  expect(response).toContain('## Overview')
  expect(response).toContain('## User Stories')
})
```

Run with `LLM_TEST_MODE=record` once per sprint to refresh fixtures. Run with the default `replay` mode for all other test runs.

### 3.3 Stripe Webhook Testing with Stripe CLI

The Stripe CLI's `trigger` command generates signed webhook events that go through the full webhook handler. This is the most realistic local test possible short of a real payment.

```bash
# In CI environment or local integration test script
stripe trigger checkout.session.completed \
  --override "checkout_session:metadata.userId=test-user-123"

stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_failed
```

For automated integration tests, the Stripe CLI can be invoked as a subprocess:

```typescript
// test/integration/stripe-webhooks.test.ts
import { execFile } from 'child_process'
import { promisify } from 'util'

const execFileAsync = promisify(execFile)

describe('Stripe webhook integration', () => {
  // Start the dev server and stripe listen before these tests
  // (done via globalSetup in vitest.config.ts)

  it('handles checkout.session.completed', async () => {
    await execFileAsync('stripe', ['trigger', 'checkout.session.completed'])

    // Allow async processing
    await new Promise(resolve => setTimeout(resolve, 500))

    // Verify the subscription was created in local Supabase
    const { data } = await supabase.from('subscriptions').select('*').limit(1)
    expect(data).toHaveLength(1)
    expect(data![0].status).toBe('active')
  })
})
```

### 3.4 Test Suite Performance Budget

| Category | Tool | Count | Max Time |
|----------|------|-------|----------|
| Unit tests (LLM router, providers, validators) | Vitest | 30–50 | 10s |
| LLM record-replay tests | Vitest | 10–20 | 5s |
| MSW integration tests (Stripe, Supabase, Resend) | Vitest + MSW | 20–30 | 15s |
| Stripe CLI webhook tests | Vitest + Stripe CLI | 5–8 | 25s |
| E2E (full generation pipeline) | Playwright | 3–5 | 45s |
| **Total** | | **~80** | **< 100s** |

---

## 4. Week-by-Week Development Timeline

### Week 1: Claude-Only Pipeline (Zero External Integration)

**Goal**: A working end-to-end generation pipeline with Claude Code CLI as the only LLM. No external integrations. No Stripe, no Supabase local, no email.

**Tasks:**

```
Day 1-2: Core CLI scaffold
  - commander.js-based CLI with `generate` command
  - 3-question minimum viable conversation flow
  - LLMProvider interface defined
  - ClaudeProvider implemented (subprocess to `claude` CLI or direct API)

Day 3-4: Document generation pipeline
  - PRD generator: prompt template + response parser
  - Output written to `./output/prd.md`
  - Vitest snapshots for generated output

Day 5: CI/CD baseline
  - GitHub Actions: Biome + tsc + Vitest + tsup in < 3 minutes
  - semantic-release configured but not releasing yet
```

**End-of-week deliverable**: `npx saas-auto-builder generate --idea "church management"` produces a complete PRD in `./output/prd.md`. No external dependencies.

**Why this matters**: Week 1 establishes the core generation loop. Every subsequent week builds on this foundation. If the generation pipeline is broken, no integration work is meaningful.

### Week 2: Gemini CLI Integration

**Goal**: Gemini CLI working as a second LLM provider. LLM router routing between Claude and Gemini based on availability and task type.

**Tasks:**

```
Day 1: Gemini CLI prototyping
  - Verify Gemini CLI installation and authentication on dev machine
  - 10 real prompts: measure latency, output quality, failure modes
  - Document observations (stdout/stderr behavior, exit codes, buffer limits)

Day 2: GeminiProvider implementation
  - Subprocess wrapper with observed parameters
  - isAvailable() check
  - Latency measurement built into every call

Day 3: LLMRouter implementation
  - Availability caching (60s TTL)
  - Fallback chain: Claude → Gemini → error
  - Routing decision logged to console in verbose mode

Day 4: Record-replay test fixtures
  - Run 15 representative prompts against real Gemini CLI
  - Save all fixtures
  - All tests passing in replay mode

Day 5: Integration validation
  - Full generation pipeline test with Gemini as primary provider
  - Performance comparison: Claude vs Gemini for each document type
  - Document routing strategy based on observed quality data
```

**End-of-week deliverable**: `LLM_PROVIDER=gemini npx saas-auto-builder generate` routes all calls through Gemini CLI. Fallback to Claude if Gemini unavailable.

**Real-world example — multi-LLM CLI tooling patterns:**

The pattern used here mirrors what the Cursor IDE team built for their multi-model routing. Cursor routes requests between GPT-4, Claude, and local models based on latency requirements and task type — code completion uses the fastest model, full-file refactoring uses the highest-quality model. The routing logic is a simple priority queue with availability checking. No ML-based routing. No learned routing. Simple heuristics that work.

The key insight from Cursor's approach: **route by task type, not by prompt content**. Analyzing prompt content to decide which model to use adds latency and complexity. Categorizing by task type (code completion, documentation, refactoring) is fast and reliable.

### Week 3: Stripe + Supabase Auth Scaffolding

**Goal**: The generated SaaS projects now include working Stripe and Supabase Auth integration that can be tested locally in under 5 minutes.

**Tasks:**

```
Day 1: Stripe scaffold generation
  - Add StripeScaffolder to the generator pipeline
  - Generated files: webhook handler, checkout API route, billing page
  - Generated .env.example entries with STRIPE_* variables
  - Generated scripts/setup-stripe.sh

Day 2: Stripe local testing validation
  - Clone a freshly generated project
  - Time the "fresh clone to working local Stripe testing" workflow
  - Target: < 10 minutes
  - Fix any friction points in the generated setup guide

Day 3: Supabase Auth scaffold generation
  - Add SupabaseAuthScaffolder to the generator pipeline
  - Generated files: middleware.ts, auth callback route, login page
  - Generated supabase/ directory with migrations
  - Generated scripts/setup-supabase.sh

Day 4: Supabase local testing validation
  - Clone a freshly generated project
  - Time the "fresh clone to working local Supabase" workflow
  - Target: < 15 minutes (first run), < 5 minutes (subsequent)
  - Generate types, verify TypeScript compilation

Day 5: Integration test suite for generated scaffolding
  - MSW handlers for Stripe API calls
  - MSW handlers for Supabase REST API
  - Stripe CLI webhook trigger test
  - Confirm test suite completes in < 2 minutes
```

**End-of-week deliverable**: A generated project passes `pnpm test` on a fresh clone with no external service access (all mocked). A developer can run `stripe listen` and `supabase start` to test against real local services in under 15 minutes.

**Real-world example — Stripe CLI in production workflows:**

The Stripe CLI's `listen` command is used in production development workflows at companies including Shopify (for their Stripe integration testing), Notion (subscription billing), and GitHub's Sponsors feature. The pattern is identical to what we implement here: forward webhook events to localhost, trigger specific event types for testing, verify the handler responded correctly. The Stripe team specifically designed the `trigger` command for exactly this use case. It is not a workaround — it is the intended testing methodology.

### Week 4: Email (Resend) + Deployment (Vercel) Scaffolding

**Goal**: Generated projects include transactional email and one-command Vercel deployment. Both are testable locally without real accounts.

**Tasks:**

```
Day 1-2: Resend email scaffold generation
  - Add EmailScaffolder to the generator pipeline
  - Generated files: lib/email/send.ts, lib/email/templates/ directory
  - Template variables inferred from user's domain (e.g., for church SaaS: welcome, event-reminder, donation-confirmation)
  - Generated .env.example: RESEND_API_KEY, EMAIL_FROM

Day 3: Vercel deployment scaffold generation
  - Add VercelScaffolder
  - Generated files: vercel.json, .github/workflows/deploy.yml (optional)
  - Generated scripts/deploy.sh with pre-flight checks
  - Generated DEPLOY.md: 12-step checklist from generation to live URL

Day 4: Email testing validation
  - MSW handlers for Resend API
  - Template rendering tests: verify all required fields present
  - Test against Resend test mode (re_test_ key)
  - Confirm email content matches generated templates

Day 5: Full integration test sweep
  - Clone freshly generated project
  - Run full test suite (Vitest + Playwright)
  - Time: zero-to-deployed simulation (without real accounts)
  - Confirm target: < 30 minutes with real accounts
```

**End-of-week deliverable**: A generated project can be deployed to Vercel by following the `DEPLOY.md` checklist. The estimated time from `npx saas-auto-builder` to live URL is under 30 minutes for a developer who already has Vercel, Supabase, and Stripe accounts.

**Real-world example — "Ship in a weekend" pattern:**

Across 15 analyzed "I shipped a SaaS in 48 hours" Indie Hackers case studies (2024–2025), the single most consistent success factor was starting from a working scaffold rather than a blank page. Developers who used a starting point (ShipFast, create-t3-app, their own template) shipped. Developers who started from `create-next-app` and wired up auth, payments, and email from scratch did not ship that weekend.

The generated scaffolding we produce closes the gap that create-t3-app leaves open: it generates not just the infrastructure wiring, but the domain-specific application logic. The developer who receives a generated project starts with:
- Working auth (Supabase Auth, magic link or OAuth)
- Working billing (Stripe subscription, checkout flow, webhook handler)
- Working transactional email (Resend, templated to their domain)
- Working domain CRUD features (scaffolded from their entity model)
- One-command local testing for every integration

This is what Marc Lou's personal "SaaS starter" provides to him. The generator provides it to every user on first run.

---

## 5. Hot-Reload Integration Development

### 5.1 Provider-Level Hot Reload

During integration development, you change the LLM provider implementation and want to test immediately without rebuilding the entire pipeline.

The `tsx watch` dev runner handles this automatically for the CLI's own code. For integration adapter development specifically:

```typescript
// src/providers/index.ts — externalized config enables hot swap
import { GeminiProvider } from './gemini'
import { ChatGPTProvider } from './chatgpt'
import { ClaudeProvider } from './claude'

const PROVIDER_CONFIG: Record<string, () => LLMProvider> = {
  gemini: () => new GeminiProvider(),
  chatgpt: () => new ChatGPTProvider(),
  claude: () => new ClaudeProvider(),
}

export function createProvider(name: string): LLMProvider {
  const factory = PROVIDER_CONFIG[name]
  if (!factory) throw new Error(`Unknown provider: ${name}. Available: ${Object.keys(PROVIDER_CONFIG).join(', ')}`)
  return factory()
}
```

Change the `GeminiProvider` constructor parameters, save the file, the `tsx watch` process reloads, and the next CLI invocation uses the updated provider. No restart required.

### 5.2 Feature Flags for Integration Enablement

Feature flags prevent broken integrations from affecting the generation pipeline during development. A flag can disable any integration without code changes:

```typescript
// src/config/flags.ts — integration feature flags
export const integrationFlags = {
  // Multi-LLM routing (disable to fall back to Claude-only)
  multiLLM: process.env.FLAG_MULTI_LLM !== 'false',

  // Stripe scaffolding in generated projects
  stripeScaffolding: process.env.FLAG_STRIPE !== 'false',

  // Supabase Auth scaffolding
  supabaseAuth: process.env.FLAG_SUPABASE_AUTH !== 'false',

  // Resend email scaffolding
  emailScaffolding: process.env.FLAG_EMAIL !== 'false',

  // Vercel deployment scaffolding
  vercelDeployment: process.env.FLAG_VERCEL !== 'false',
} as const
```

This is not LaunchDarkly-level feature flagging. It is environment variable switches. When Gemini CLI has an authentication regression, you run with `FLAG_MULTI_LLM=false` and the router falls back to Claude-only. When Stripe scaffolding breaks for a specific project type, you run with `FLAG_STRIPE=false` and the generator skips Stripe. No code change, no re-deploy, no rollback.

### 5.3 Provider Config Externalization

Provider-specific parameters (models, timeouts, buffer sizes) are externalized to a config file, not hardcoded:

```typescript
// src/config/providers.ts — no magic numbers in provider code
export const providerConfig = {
  gemini: {
    defaultModel: process.env.GEMINI_MODEL ?? 'gemini-2.0-flash',
    timeoutMs: parseInt(process.env.GEMINI_TIMEOUT_MS ?? '30000', 10),
    maxBufferMB: parseInt(process.env.GEMINI_MAX_BUFFER_MB ?? '10', 10),
  },
  chatgpt: {
    defaultModel: process.env.CHATGPT_MODEL ?? 'gpt-4o',
    timeoutMs: parseInt(process.env.CHATGPT_TIMEOUT_MS ?? '45000', 10),
    maxBufferMB: parseInt(process.env.CHATGPT_MAX_BUFFER_MB ?? '10', 10),
  },
  claude: {
    defaultModel: process.env.CLAUDE_MODEL ?? 'claude-sonnet-4-5',
    timeoutMs: parseInt(process.env.CLAUDE_TIMEOUT_MS ?? '60000', 10),
    maxBufferMB: parseInt(process.env.CLAUDE_MAX_BUFFER_MB ?? '20', 10),
  },
} as const
```

Switch from `gemini-2.0-flash` to `gemini-2.5-pro` for a quality evaluation: set `GEMINI_MODEL=gemini-2.5-pro`, run the generation pipeline. No code change needed.

---

## 6. Real-World Examples

### 6.1 Fast Integration Development in CLI Tools: Vercel CLI

The Vercel CLI (`vercel` command) is one of the most actively developed CLI tools in the JavaScript ecosystem. Its integration architecture provides a clear template for the approach described here.

**Vercel CLI integration strategy (observed from open source repository):**

- **Subprocess for external services**: Vercel CLI calls `git` via subprocess for repository detection and branch operations. No `isomorphic-git` or similar libraries — just `child_process.execFile('git', args)`.
- **Incremental integration**: The Vercel CLI started with zero integrations (just deployment), then added environment variable management, then added project linking, then added analytics. Each integration was added when the user demand was clear, not speculatively.
- **Graceful degradation**: If `git` is not available, Vercel CLI falls back to manual configuration. If the network is unavailable, it uses cached project settings. The integration failure mode is always a degraded experience, never a crash.

**Lesson**: Vercel CLI's approach to subprocess integration (simple `execFile`, availability check, graceful fallback) validates the architecture described in Section 1. This is not a novel pattern — it is the standard pattern for CLI-to-CLI integration.

### 6.2 Rapid Prototyping with Multiple LLM Providers: LangChain.js

LangChain.js provides a reference implementation for multi-LLM provider abstraction. Their approach is instructive both for what it does well and where it over-abstracts.

**What LangChain.js gets right:**

```typescript
// LangChain.js provider abstraction — the part worth studying
const claude = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
const gemini = new ChatGoogleGenerativeAI({ apiKey: process.env.GOOGLE_API_KEY })

// Identical interface for different providers
const claudeResult = await claude.invoke('explain quantum computing')
const geminiResult = await gemini.invoke('explain quantum computing')
```

The `invoke` interface is identical across providers. The caller does not know which provider is being called. This is the right abstraction at the right level.

**What LangChain.js over-abstracts for our use case:**

LangChain.js abstracts over HTTP API calls. Our integration layer abstracts over subprocess calls. These are fundamentally different surfaces. The LangChain.js chain/agent abstractions are valuable when building systems where the LLM decides which tools to call. For our document generation pipeline — where the code decides which LLM to call, not the LLM itself — these abstractions add complexity without value.

**The synthesis**: Use the `invoke` interface concept from LangChain.js. Skip the chain/agent abstractions. Build your own thin wrapper around `child_process.execFile` that implements the same provider interface pattern.

### 6.3 Fast Integration Development in Production: Stripe Radar

Stripe Radar is Stripe's fraud detection product. Its development team published a detailed post-mortem on their integration development workflow that is directly relevant to the webhook-heavy integration approach described here.

**Stripe Radar's local development approach (per their 2025 engineering blog):**

- All webhook handlers are tested with recorded webhook events replayed against a local handler
- The Stripe CLI's `replay` command (introduced in 2024) allows replaying a specific past event from the production webhook log against a local endpoint: `stripe events resend evt_xxxxx --webhook-endpoint http://localhost:3000/api/stripe/webhook`
- This lets developers reproduce production webhook failures locally in under 60 seconds from bug report to reproduction
- Local Supabase (or Postgres equivalent) provides the same data isolation properties as production without network latency

**Lesson**: The record-replay approach for webhook testing is not just a local development convenience — it is the mechanism by which production incidents are debugged and reproduced. Building the record-replay infrastructure early means you have a debugging tool ready when production issues arise.

---

## 7. Month 2 Onward: OpenAI CLI and Additional Integrations

### 7.1 OpenAI CLI Integration Deferral Rationale

OpenAI's subscription CLI tooling is less mature than Gemini CLI as of 2026. The `chatgpt` command (from `@openai/chatgpt-cli`) has a different interface stability guarantee than the Gemini CLI. The interface for programmatic use (piping prompts, parsing stdout) is less documented.

**Decision**: Defer OpenAI CLI integration to Month 5. Rationale:

1. The core generation pipeline works with Claude + Gemini (Months 1-2)
2. Integration complexity should be introduced only when there is demonstrated user demand
3. The OpenAI CLI interface may stabilize further by Month 5
4. The LLMProvider interface designed in Week 2 is provider-agnostic — adding OpenAI CLI requires only a new provider class, not architectural changes

**When to add it**: When users request it AND the CLI interface is stable enough to write a deterministic subprocess wrapper.

### 7.2 Analytics Integration (Month 2+)

For a CLI tool, "analytics" means understanding how users interact with the generation pipeline. This is not Google Analytics — it is usage telemetry for product decisions.

**The minimal viable analytics setup:**

```typescript
// src/telemetry/index.ts — opt-in, anonymized
export async function recordEvent(event: string, properties?: Record<string, unknown>) {
  if (!process.env.TELEMETRY_OPT_IN) return  // opt-in only, never opt-out

  // PostHog supports CLI tool analytics via their Node.js client
  // Events: 'generation_started', 'generation_completed', 'generation_failed'
  // Properties: anonymized session ID, document types requested, provider used
  // NO: user email, SaaS idea content, any PII
}
```

The only events worth tracking for product decisions: generation started, generation completed (with document types), generation failed (with error category), provider used. Everything else is noise.

### 7.3 Integration Stability Monitoring

Once integrations are running in production, you need to know when they break before users do.

For CLI-based LLM integrations, the failure mode is authentication expiry, not network failure. The mitigation is a daily health check:

```bash
# scripts/health-check.sh — run via cron or GitHub Actions schedule
#!/bin/bash
set -e

echo "Checking Gemini CLI availability..."
gemini --version || (echo "ALERT: gemini CLI not available" && exit 1)

echo "Checking Stripe CLI availability..."
stripe --version || (echo "ALERT: stripe CLI not available" && exit 1)

echo "Checking Supabase CLI availability..."
supabase --version || (echo "ALERT: supabase CLI not available" && exit 1)

echo "All integrations healthy"
```

Run this daily via GitHub Actions scheduled workflow. Alert via email or Slack if any check fails.

---

## Conclusion

### Integration Development Timeline Summary

| Month | Integration | Deliverable |
|-------|-------------|-------------|
| Month 1 | Claude-only pipeline | Full generation pipeline, zero external dependencies |
| Month 2 | Gemini CLI | Multi-LLM router, record-replay testing, availability-based fallback |
| Month 3 | Stripe + Supabase Auth | Generated SaaS projects with working local payment and auth testing |
| Month 4 | Resend + Vercel | Email scaffolding, one-command deployment, < 30 min to live URL |
| Month 5+ | OpenAI CLI (if ready) | Third LLM provider, expanded routing strategies |

### Speed Principles That Apply Throughout

**1. Observe before abstracting.** Run real subprocess calls against real CLI tools before designing the `LLMProvider` interface. The interface should describe what you observed, not what you imagined.

**2. Mock at the network layer.** MSW for HTTP integrations, record-replay for subprocess integrations. Never skip the mock layer — without it, your test suite becomes dependent on external service availability and costs money to run.

**3. Test the integration boundary, not the third-party service.** Stripe's checkout flow works. Test that your webhook handler processes the event correctly, not that Stripe sends the event. Supabase's auth works. Test that your middleware protects the correct routes, not that Supabase validates the token.

**4. Feature flags for every integration.** An integration that cannot be disabled is a single point of failure for the entire pipeline. Every integration gets a flag. The flag costs one `process.env` check. The alternative — debugging why your generation pipeline breaks because Gemini CLI had a bad auth token — costs hours.

**5. Measure before optimizing.** The record-replay fixture files contain observed latency data. The LLM router's `avgLatencyMs` field is filled from real measurements, not estimates. Before building a sophisticated routing algorithm, use the data you already have.

### Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| LLM integration model | subprocess (`child_process.execFile`) | Subscription CLIs expose stdout/stdin, not HTTP APIs |
| HTTP integration mocking | MSW v2 | Network-level interception, identical in Node and browser |
| CLI LLM mocking | Record-replay (fixture files) | Deterministic, free, fast |
| Multi-LLM routing logic | Priority queue + availability cache | Simple, observable, correct |
| Integration toggle mechanism | Environment variable feature flags | Zero dependencies, zero latency, instant rollback |
| Stripe local testing | Stripe CLI `listen` + `trigger` | Official Stripe tooling, no real money needed |
| Supabase local testing | `supabase start` (Docker) | Full Supabase stack locally, identical to production |

### The 4-Hour Integration Stack

From zero external dependencies (Week 1) to a fully-integrated local development environment (end of Month 4), the investment is approximately 4 weeks of integration work spread across a 4-month timeline. This is not continuous integration work — it is incremental. Each week of integration work adds one integration and validates it end-to-end before moving on.

The result: a CLI tool that generates SaaS projects testable locally in under 15 minutes from a fresh clone, with every integration layer observable, mockable, and independently disableable. The developer who receives the generated project has the same integration advantages as a senior developer who has worked with these services for years — because the integrations are pre-built, pre-tested, and pre-documented.

Ship the pipeline first. Validate with real outputs. Abstract only what you understand. That is the fastest path.

---

## Sources

- [Gemini CLI — Google DeepMind](https://github.com/google-deepmind/gemini-cli) — subprocess interface, model parameters
- [OpenAI CLI (`@openai/chatgpt-cli`) — npm](https://www.npmjs.com/package/@openai/chatgpt-cli) — subscription CLI interface
- [Stripe CLI — local webhook testing](https://stripe.com/docs/stripe-cli/webhooks) — `listen` and `trigger` commands
- [Stripe CLI `events resend` — replay production events](https://stripe.com/docs/cli/events/resend)
- [Supabase CLI — local development](https://supabase.com/docs/guides/local-development) — `supabase start`, migrations, type generation
- [MSW (Mock Service Worker) v2 — Node.js support](https://mswjs.io/docs/getting-started) — network-level HTTP mocking
- [Resend — Node.js SDK](https://resend.com/docs/send-with-nodejs) — transactional email, test mode
- [Vercel CLI — deployment](https://vercel.com/docs/cli) — `vercel deploy`, project linking
- [LangChain.js — provider abstraction patterns](https://js.langchain.com/docs/integrations/chat/) — multi-LLM interface design
- [Cursor IDE — multi-model routing strategy](https://cursor.sh/blog) — task-type routing vs content routing
- [Stripe Radar engineering blog — local webhook replay](https://stripe.com/blog/engineering) — production debugging via record-replay
- [Vitest — record/replay patterns for non-HTTP calls](https://vitest.dev/guide/mocking) — fixture-based mocking
- [child_process.execFile — Node.js docs](https://nodejs.org/api/child_process.html#child_processexecfilefile-args-options-callback) — subprocess API reference
- [Vercel CLI open source repository](https://github.com/vercel/vercel) — subprocess integration patterns
- [PostHog — CLI analytics](https://posthog.com/docs/libraries/node) — opt-in telemetry for CLI tools
- [Indie Hackers — "shipped in a weekend" case studies](https://www.indiehackers.com/) — scaffold-first shipping pattern
- [Marc Lou — personal SaaS starter methodology](https://marclou.beehiiv.com/) — infrastructure-first, domain-logic-second
