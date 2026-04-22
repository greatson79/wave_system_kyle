# Branch 3.2: Robust SaaS Development Process
## Quality-First Practices for AI-Generated SaaS Projects

**Perspective**: Quality-First Development Process Expert
**Focus**: Generated SaaS projects (Next.js + Supabase + Stripe), NOT the CLI tool itself
**Core Thesis**: AI-generated code has 1.7x more issues (CodeRabbit data). The system must embed quality gates, security posture, and observability into every generated project from line zero.
**Date**: 2026-03-12

---

## Executive Summary

When a developer runs `sab generate`, they receive a Next.js + Supabase + Stripe project scaffold. That scaffold will handle real user data, real payments, and real authentication within days of generation. The quality practices embedded in that scaffold are not optional polish — they are the minimum acceptable standard for any software that processes personal data and financial transactions.

The central problem: AI-generated code systematically skips error handling, produces shallow input validation, and generates security patterns that look correct but have subtle flaws. CodeRabbit's 2025 analysis across 100M+ AI-assisted code reviews found 1.7x more issues per 1000 lines compared to human-written code, with authentication logic and input validation being the highest-failure categories.

This report answers: **what quality infrastructure must the system embed into every generated project, and how should that infrastructure be structured to be maintained by a solo developer who did not write the code?**

---

## 1. Quality-First Project Scaffold Structure

### 1.1 What Gets Generated (The Full Project Shell)

The generated project must arrive with quality infrastructure pre-installed and pre-configured. A developer should not need to add testing, linting, or CI configuration — it must exist from the first `git clone`.

```
generated-saas/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              ← PR checks (type, lint, test, build, security)
│   │   ├── deploy.yml          ← Production deploy (after manual gate)
│   │   └── scheduled.yml       ← Weekly security scans + DB migration checks
│   └── CODEOWNERS              ← Auto-assign reviewers
├── src/
│   ├── app/                    ← Next.js App Router pages
│   │   ├── (auth)/             ← Route group: signup, login, forgot-password
│   │   ├── (dashboard)/        ← Route group: protected app pages
│   │   ├── api/                ← API routes
│   │   │   ├── webhooks/stripe/ ← Stripe webhook handler
│   │   │   └── health/         ← Health check endpoint
│   │   └── layout.tsx          ← Root layout with error boundary
│   ├── components/
│   │   ├── ui/                 ← shadcn/ui components (pre-installed)
│   │   └── shared/             ← App-specific shared components
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts       ← Browser Supabase client
│   │   │   └── server.ts       ← Server Supabase client (cookies)
│   │   ├── stripe/
│   │   │   ├── client.ts       ← Stripe client (server-side only)
│   │   │   └── webhooks.ts     ← Webhook signature verification
│   │   ├── validations/        ← Zod schemas for all inputs
│   │   ├── errors.ts           ← Typed error classes
│   │   └── logger.ts           ← Pino structured logger
│   ├── types/
│   │   └── database.ts         ← Supabase generated types
│   └── middleware.ts            ← Auth middleware (route protection)
├── tests/
│   ├── unit/                   ← Business logic, validators, utilities
│   ├── integration/            ← API routes with real test database
│   ├── e2e/                    ← Playwright: critical user flows
│   └── security/               ← Auth bypass, authorization checks
├── supabase/
│   ├── migrations/             ← Database migrations (versioned)
│   ├── seed.sql                ← Development seed data
│   └── config.toml             ← Local Supabase configuration
├── .env.example                ← All required variables documented
├── .env.test                   ← Test environment (committed, no secrets)
├── biome.json                  ← Lint + format (replaces ESLint + Prettier)
├── vitest.config.ts            ← Test configuration
├── playwright.config.ts        ← E2E test configuration
└── docker-compose.yml          ← Local development: Supabase + test DB
```

### 1.2 The Generated Development Environment

**Docker Compose for full local reproduction.** The generated `docker-compose.yml` spins up a complete local environment including the Supabase stack (PostgreSQL + Auth + Storage + Edge Functions emulator), an isolated test database instance, and a local Stripe webhook relay via the Stripe CLI. A developer running `docker compose up -d && pnpm dev` has a fully functional environment in under 5 minutes with zero external dependencies.

```yaml
# docker-compose.yml (generated)
services:
  db:
    image: supabase/postgres:15.8.1.060
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - ./supabase/migrations:/docker-entrypoint-initdb.d
      - pgdata:/var/lib/postgresql/data

  db-test:
    image: supabase/postgres:15.8.1.060
    ports: ["5433:5432"]
    environment:
      POSTGRES_PASSWORD: postgres_test
    tmpfs: /var/lib/postgresql/data  # Ephemeral: tests start clean

  supabase-auth:
    image: supabase/gotrue:v2.168.0
    depends_on: [db]
    environment:
      GOTRUE_DB_DATABASE_URL: postgres://postgres:postgres@db:5432/postgres
      GOTRUE_JWT_SECRET: ${SUPABASE_JWT_SECRET}

  stripe-webhook-relay:
    image: stripe/stripe-cli:latest
    command: listen --forward-to host.docker.internal:3000/api/webhooks/stripe
    environment:
      STRIPE_API_KEY: ${STRIPE_SECRET_KEY}

volumes:
  pgdata:
```

**Setup time realistic assessment.** First-time environment setup: 8-12 minutes (Docker image pulls + database initialization). Subsequent starts: under 60 seconds. This is a meaningful investment that pays for itself the first time a developer catches a row-level security regression locally instead of in production.

### 1.3 Pre-Configured Toolchain

The generated project arrives with four toolchain components pre-configured and integrated:

**Biome** for linting and formatting with SaaS-security rules activated. The generated `biome.json` enables all security-relevant lint rules including detection of `eval()` usage, non-literal regular expressions, and prototype pollution patterns. Cyclomatic complexity limit is set to 15 per function.

**TypeScript strict mode** with additional safety flags. The generated `tsconfig.json` includes `strict: true`, `noUncheckedIndexedAccess: true`, `noUnusedLocals: true`, and `exactOptionalPropertyTypes: true`. These settings catch entire categories of SaaS-specific bugs: null reference errors in database query results, type mismatches in API responses, and missing error handling branches.

**simple-git-hooks + lint-staged** for pre-commit validation. The generated hook runs Biome formatting (auto-fix on staged files) and TypeScript type checking on changed files. This runs in under 8 seconds for typical changes and prevents type errors from entering version control.

**IDE configuration** via `.vscode/settings.json` and `.vscode/extensions.json`. The generated settings configure Biome as the default formatter, activate TypeScript's strict checking in the editor, and recommend the Supabase, Stripe, and Tailwind CSS extensions. A developer opening the project in VS Code receives a complete environment without manual configuration.

---

## 2. Security from Generation

### 2.1 OWASP Top 10 Prevention Built Into Generated Code

Generated code must address the OWASP Top 10 structurally, not as a checklist applied after writing. Each vulnerability requires a specific architectural pattern embedded at generation time.

**A01 — Broken Access Control**

Every API route in the generated project follows a mandatory guard pattern. The system generates route handlers that fail closed: if the authorization check does not explicitly return `true`, the request is rejected.

```typescript
// src/lib/auth/guard.ts (generated)
export async function requireAuth(request: Request): Promise<User> {
  const supabase = createServerClient(cookies());
  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user) {
    throw new UnauthorizedError('Authentication required');
  }
  return user;
}

export async function requireOwnership(
  userId: string,
  resourceId: string,
  table: 'projects' | 'documents' | 'settings'
): Promise<void> {
  const supabase = createServerClient(cookies());
  const { data, error } = await supabase
    .from(table)
    .select('user_id')
    .eq('id', resourceId)
    .single();

  if (error || !data || data.user_id !== userId) {
    throw new ForbiddenError('Resource access denied');
  }
}
```

Additionally, **Row Level Security (RLS) is enabled by default** on every generated Supabase table. Generated migrations include RLS policies as non-negotiable SQL:

```sql
-- Generated migration: 002_enable_rls.sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_projects"
  ON projects
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**A02 — Cryptographic Failures**

The generated project enforces HTTPS-only patterns. Authentication cookies are generated with `httpOnly: true`, `secure: true`, and `sameSite: 'lax'`. Supabase JWT secrets are never exposed to the client. The generated middleware validates that all requests to protected routes arrive over HTTPS (enforced at Vercel deployment level, not in application code).

**A03 — Injection**

Drizzle ORM is the generated database layer. All queries use parameterized statements by construction — Drizzle's API does not have a string interpolation escape hatch. Raw SQL is generated only for migrations (which are reviewed before execution) and complex aggregations wrapped in Zod-validated functions.

**A04 — Insecure Design**

The generated subscription architecture does not trust client-supplied plan data. Plan entitlements are always fetched from the database based on the verified Stripe subscription status, never from query parameters or request bodies. The generated `useSubscription` hook on the client side fetches plan data from a server action that queries Supabase, not from session storage or cookies that a user could modify.

**A05 — Security Misconfiguration**

The generated `next.config.ts` includes a Content Security Policy (CSP) header configuration as a starting point, defaulting to a restrictive policy that allows only same-origin scripts, Supabase's CDN for auth scripts, and Stripe.js for payments. The generated middleware adds security headers on every response:

```typescript
// src/middleware.ts (generated security headers)
const securityHeaders = {
  'X-DNS-Prefetch-Control': 'on',
  'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
  'X-Frame-Options': 'SAMEORIGIN',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};
```

**A07 — Authentication Failures**

Rate limiting is embedded at the middleware level for all authentication routes. The generated project uses Upstash Redis (or in-memory rate limiter for development) to enforce: 5 login attempts per 15-minute window per IP, 3 password reset requests per hour per email address, and 10 API calls per second per authenticated user for general routes.

**A09 — Security Logging and Monitoring Failures**

Every authentication event, authorization failure, and data mutation is logged with structured fields including `userId`, `action`, `resource`, `ip`, `userAgent`, and `result`. These logs are written to Pino and forwarded to the configured logging provider (generated with Sentry integration by default).

### 2.2 Secrets Management

The generated `.env.example` documents every required environment variable with descriptions, expected format, and instructions for obtaining the value. The file is committed. The `.env.local` file is gitignored and never committed.

The generated `src/lib/env.ts` validates environment variables at startup using Zod. A missing or malformed environment variable causes the application to fail fast with a clear error message rather than failing silently at runtime when the variable is first accessed:

```typescript
// src/lib/env.ts (generated)
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  STRIPE_WEBHOOK_SECRET: z.string().startsWith('whsec_'),
  STRIPE_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
  DATABASE_URL: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

### 2.3 Dependency Vulnerability Scanning

The generated `package.json` includes `npm audit` in the CI pipeline with a threshold of zero high/critical vulnerabilities. The generated `.github/workflows/scheduled.yml` runs a weekly `npm audit` job that opens a GitHub issue if new vulnerabilities are detected, enabling proactive rather than reactive patching.

---

## 3. The 5-Layer Test Pyramid for Generated SaaS

### 3.1 Layer Structure and Coverage Targets

```
                        /\
                       /E2E\              4 critical user flows
                      /─────\
                     /Security\           Auth bypass + authorization
                    /──────────\
                   / Integration \        API routes + webhooks + DB
                  /──────────────\
                 /   Component    \       React components (user-facing)
                /─────────────────\
               /     Unit Tests    \     Business logic + validators
              /─────────────────────\
```

**Coverage targets for generated projects**: 70% overall is the realistic and defensible floor. Aiming for 90% on generated code has diminishing returns because much of the uncovered surface area is error handling branches that require complex mocking to reach. The coverage investment should be concentrated where it matters:

| Layer | Coverage Target | Rationale |
|-------|----------------|-----------|
| Business logic (pricing, entitlements) | 95% | Money touches this code |
| Input validation (Zod schemas) | 90% | Every public entry point |
| API route handlers | 80% | Mix of logic and I/O |
| React components | 60% | Happy path + accessibility |
| Utility functions | 85% | Deterministic, cheap to test |
| Stripe webhook handlers | 90% | Financial events, idempotency critical |

### 3.2 Unit Tests: Business Logic and Validation

Generated unit tests cover three critical SaaS-specific domains:

**Subscription entitlement logic**: Every plan boundary is tested. If the Free plan allows 5 projects and the Pro plan allows unlimited, there are tests for: exactly 5 projects on Free, attempt to create a 6th on Free (should fail), exactly 5 on Pro (should succeed), 50 on Pro (should succeed), and expired Pro subscription (should fail at the limit).

**Input validation (Zod schemas)**: Every schema generated has a corresponding test suite that covers valid inputs, boundary values, missing required fields, invalid formats, and injection attempt strings. The generated test helper includes a library of malicious input strings (XSS payloads, SQL injection patterns, oversized strings) that are run against every text input schema.

**Stripe price and billing calculations**: Proration calculations, trial period logic, and coupon application are tested with known inputs and expected outputs. These calculations cannot be trusted to be "approximately correct."

### 3.3 Integration Tests: API Routes with Real Database

Integration tests run against the ephemeral test database (the `db-test` Docker Compose service). The generated test setup creates a fresh database state before each test suite using Supabase's migration runner, eliminating test pollution.

**SaaS-specific integration test scenarios the system generates:**

```typescript
// tests/integration/subscription.test.ts (generated pattern)
describe('Subscription Lifecycle', () => {
  it('creates checkout session for new subscriber', async () => {
    const user = await createTestUser();
    const response = await POST('/api/stripe/checkout', {
      priceId: PRICE_IDS.PRO_MONTHLY,
    }, { authAs: user });

    expect(response.status).toBe(200);
    expect(response.body.url).toMatch(/^https:\/\/checkout\.stripe\.com/);
  });

  it('handles successful payment webhook and activates subscription', async () => {
    const user = await createTestUser();
    const event = createStripeEvent('checkout.session.completed', {
      customer: user.stripeCustomerId,
      subscription: 'sub_test_123',
    });

    const response = await POST('/api/webhooks/stripe', event.rawBody, {
      headers: { 'stripe-signature': event.signature },
    });

    expect(response.status).toBe(200);
    const subscription = await getSubscription(user.id);
    expect(subscription.status).toBe('active');
    expect(subscription.plan).toBe('pro');
  });

  it('handles failed payment and downgrades to free tier', async () => {
    const user = await createProUser();
    const event = createStripeEvent('invoice.payment_failed', {
      customer: user.stripeCustomerId,
    });

    await POST('/api/webhooks/stripe', event.rawBody, {
      headers: { 'stripe-signature': event.signature },
    });

    const subscription = await getSubscription(user.id);
    expect(subscription.status).toBe('past_due');
    // Feature access should be restricted after grace period
  });
});
```

**Multi-tenancy isolation tests**: For each generated SaaS with multi-tenant data, the integration suite includes explicit data isolation verification. User A cannot read, write, or infer the existence of User B's data. These tests are generated for every resource type in the application.

### 3.4 Component Tests: User-Facing UI

React components are tested with `@testing-library/react`. The generated component tests focus on:
- Form submission with valid and invalid data
- Error state display (API errors, validation errors)
- Loading state indicators (skeletons, spinners)
- Accessibility: keyboard navigation, ARIA labels, focus management
- Responsive behavior at three breakpoints (mobile, tablet, desktop)

The generated Playwright accessibility configuration includes `axe-core` integration that runs on every E2E test page load and fails tests when WCAG 2.1 AA violations are detected.

### 3.5 E2E Tests: Critical User Flows

The system generates Playwright tests for exactly four critical flows, which are the flows whose failure causes immediate user loss:

**1. Signup → Email Verification → Onboarding**
```typescript
test('new user completes signup flow', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('[name="email"]', testEmail);
  await page.fill('[name="password"]', 'SecureP@ss123');
  await page.click('[type="submit"]');

  // Verify redirect to email confirmation page
  await expect(page).toHaveURL('/signup/confirm');

  // Simulate email confirmation via Supabase test helper
  await confirmEmail(testEmail);
  await page.goto('/dashboard');

  await expect(page).toHaveURL('/onboarding');
  await expect(page.locator('h1')).toContainText('Welcome');
});
```

**2. Login → Access Protected Resource → Logout**

**3. Subscribe (Stripe Checkout) → Access Premium Feature**

**4. Cancel Subscription → Lose Premium Access After Period**

These four flows cover the complete subscription lifecycle. If any of them breaks, the SaaS loses revenue. The tests run in CI against a Stripe test-mode environment with test clocks to simulate time passage for subscription expiration.

### 3.6 Security Tests: Authorization Checks

The generated security test suite is minimal but targeted. It covers the scenarios that most developers miss:

```typescript
// tests/security/authorization.test.ts (generated)
describe('Horizontal Privilege Escalation Prevention', () => {
  it('user cannot access another user\'s project by ID', async () => {
    const userA = await createTestUser();
    const userB = await createTestUser();
    const projectB = await createProject(userB.id);

    const response = await GET(`/api/projects/${projectB.id}`, {
      authAs: userA,
    });

    expect(response.status).toBe(404); // Not 403: do not confirm existence
  });

  it('unauthenticated request to protected resource returns 401', async () => {
    const response = await GET('/api/projects');
    expect(response.status).toBe(401);
  });

  it('expired token does not grant access', async () => {
    const expiredToken = generateExpiredToken();
    const response = await GET('/api/projects', {
      headers: { Authorization: `Bearer ${expiredToken}` },
    });
    expect(response.status).toBe(401);
  });
});
```

---

## 4. CI/CD Pipeline for Generated SaaS

### 4.1 The Complete Generated CI Workflow

```yaml
# .github/workflows/ci.yml (generated)
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # Step 1: Type checking
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm tsc --noEmit

  # Step 2: Linting
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm biome check .

  # Step 3: Unit + Integration tests
  test:
    runs-on: ubuntu-latest
    needs: [typecheck, lint]
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres_test
          POSTGRES_DB: test_db
        ports: ["5433:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm supabase db push --db-url $TEST_DB_URL
        env:
          TEST_DB_URL: postgresql://postgres:postgres_test@localhost:5433/test_db
      - run: pnpm vitest run --coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres_test@localhost:5433/test_db
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.TEST_SUPABASE_SERVICE_ROLE_KEY }}
      - uses: davelosert/vitest-coverage-report-action@v2
        with:
          min-lines-coverage: 70
          min-branches-coverage: 65

  # Step 4: Build verification
  build:
    runs-on: ubuntu-latest
    needs: [typecheck]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
        env:
          NEXT_PUBLIC_SUPABASE_URL: https://placeholder.supabase.co
          NEXT_PUBLIC_SUPABASE_ANON_KEY: placeholder_anon_key
          STRIPE_PUBLISHABLE_KEY: pk_test_placeholder

  # Step 5: E2E tests (on PR to main only)
  e2e:
    runs-on: ubuntu-latest
    needs: [test, build]
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm playwright install chromium
      - run: pnpm playwright test
        env:
          BASE_URL: ${{ steps.deploy-preview.outputs.url }}
          STRIPE_TEST_KEY: ${{ secrets.STRIPE_TEST_KEY }}
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/

  # Step 6: Security scan
  security:
    runs-on: ubuntu-latest
    needs: [lint]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm audit --audit-level=high
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  # Step 7: Preview deployment (Vercel, on PR)
  preview-deploy:
    runs-on: ubuntu-latest
    needs: [build]
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  # Step 8: Production deployment (manual gate — merge to main only)
  production-deploy:
    runs-on: ubuntu-latest
    needs: [test, build, security]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production   # GitHub environment: requires manual approval
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: --prod
```

**Pipeline timing**: Type check (45s) and lint (20s) run in parallel. Tests (90s with PostgreSQL spinup) gate the build (60s). E2E (180s) and security (60s) run in parallel after tests pass. Total critical path: approximately 6 minutes, which is fast enough to feel responsive without cutting corners.

### 4.2 Scheduled Security and Database Verification Workflow

```yaml
# .github/workflows/scheduled.yml (generated)
name: Scheduled Checks

on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday 8 AM UTC

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm audit --json > audit-report.json
      - name: Fail on high/critical vulnerabilities
        run: |
          HIGH=$(cat audit-report.json | jq '.metadata.vulnerabilities.high')
          CRITICAL=$(cat audit-report.json | jq '.metadata.vulnerabilities.critical')
          if [ "$HIGH" -gt 0 ] || [ "$CRITICAL" -gt 0 ]; then
            echo "Found $HIGH high and $CRITICAL critical vulnerabilities"
            exit 1
          fi

  migration-check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_PASSWORD: postgres }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - name: Verify all migrations apply cleanly
        run: |
          pnpm supabase db reset --db-url postgresql://postgres:postgres@localhost:5432/postgres
          pnpm supabase db push --db-url postgresql://postgres:postgres@localhost:5432/postgres
          echo "All migrations applied successfully"
```

---

## 5. Error Handling and Monitoring

### 5.1 Generated Error Handling Patterns

The generated project uses a typed error hierarchy. Every error has a code, a user-facing message (safe to display), and a developer message (for logs only). API routes catch errors and serialize them consistently:

```typescript
// src/lib/errors.ts (generated)
export class AppError extends Error {
  constructor(
    public readonly code: string,
    public readonly userMessage: string,
    public readonly statusCode: number,
    message?: string,
  ) {
    super(message ?? userMessage);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') {
    super('UNAUTHORIZED', 'Please sign in to continue', 401, message);
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Access denied') {
    super('FORBIDDEN', 'You do not have permission to perform this action', 403, message);
  }
}

export class ValidationError extends AppError {
  constructor(
    public readonly fields: Record<string, string[]>,
    message = 'Validation failed',
  ) {
    super('VALIDATION_ERROR', 'Please check your input and try again', 422, message);
  }
}

export class PaymentError extends AppError {
  constructor(message: string) {
    super('PAYMENT_ERROR', 'Payment could not be processed. Please try again.', 402, message);
  }
}
```

Generated API routes use a wrapper function that catches all errors, logs them with full context, and returns a consistent JSON error response:

```typescript
// src/lib/api-handler.ts (generated)
export function withErrorHandling<T>(
  handler: (request: Request) => Promise<NextResponse<T>>
) {
  return async (request: Request): Promise<NextResponse<T | ApiError>> => {
    try {
      return await handler(request);
    } catch (error) {
      if (error instanceof AppError) {
        logger.warn({ code: error.code, message: error.message }, 'Application error');
        return NextResponse.json(
          { error: { code: error.code, message: error.userMessage } },
          { status: error.statusCode }
        );
      }

      // Unexpected errors: log full details, return generic response
      logger.error({ error, stack: error instanceof Error ? error.stack : undefined },
        'Unexpected error in API route');
      captureException(error); // Sentry

      return NextResponse.json(
        { error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' } },
        { status: 500 }
      );
    }
  };
}
```

### 5.2 Observability from Day 1

**Health check endpoint** (`/api/health`): Returns database connectivity status, Stripe API reachability, and application version. Used by uptime monitoring services and deployment verification scripts.

**Structured logging** with Pino: Every request generates a log entry with `requestId` (correlation ID generated at middleware level), `method`, `path`, `statusCode`, `duration`, `userId` (if authenticated), and `userAgent`. These fields enable query-based debugging without string parsing.

**Sentry integration**: The generated `sentry.client.config.ts` and `sentry.server.config.ts` capture unhandled errors with session replay enabled for authenticated users. The generated Sentry configuration includes `beforeSend` hooks that strip personally identifiable information (email addresses, phone numbers, payment card fragments) from error reports before transmission.

**Web Vitals tracking**: The generated `src/app/layout.tsx` includes a `useReportWebVitals` hook that reports Core Web Vitals (LCP, CLS, FID/INP) to the configured analytics provider. A SaaS with slow LCP loses users before they can sign up.

---

## 6. Code Quality Standards

### 6.1 TypeScript Standards

The generated project enforces TypeScript standards that prevent the most common AI-generated code deficiencies:

- No `any` types (enforced by `@typescript-eslint/no-explicit-any` rule — zero warnings permitted in CI)
- No non-null assertions (`!`) on values that could legitimately be null or undefined
- All async functions return typed Promises, not inferred `Promise<any>`
- Database query results are typed against the Supabase-generated `Database` type, not manually typed interfaces that drift

**The `any` problem in AI-generated code**: CodeRabbit's 2025 data shows that AI models have a systematic tendency to use `any` to resolve type conflicts quickly rather than expressing the actual type. The generated ESLint/Biome configuration treats `any` as an error, not a warning, because a single `any` can propagate through an entire codebase invalidating type safety.

### 6.2 Input Validation Architecture

Every mutation endpoint validates its input using a Zod schema before any business logic executes. The generated validation pattern separates schema definition (in `src/lib/validations/`) from usage (in route handlers), enabling the same schema to be used for both server-side validation and client-side form validation:

```typescript
// src/lib/validations/project.ts (generated)
export const createProjectSchema = z.object({
  name: z.string()
    .min(1, 'Project name is required')
    .max(100, 'Project name must be under 100 characters')
    .trim(),
  description: z.string()
    .max(500, 'Description must be under 500 characters')
    .trim()
    .optional(),
  visibility: z.enum(['private', 'public']).default('private'),
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>;
```

### 6.3 Documentation Standards

Generated code includes three levels of documentation, applied proportionally to complexity:

**JSDoc on public APIs**: Every exported function and type has a JSDoc comment explaining its purpose, parameters, and return value. This is not optional boilerplate — it is the interface contract that enables type-safe usage without reading the implementation.

**Module README**: Each `src/lib/` subdirectory includes a `README.md` that explains the module's responsibility, its relationship to other modules, and any non-obvious design decisions. This is especially important for the Stripe and Supabase integration modules, which have configuration subtleties.

**Inline comments for non-obvious logic**: The generated Stripe webhook handler includes explanatory comments for idempotency key handling and retry behavior, because these patterns are not self-evident and are the source of most production payment bugs.

---

## 7. Real Examples: Quality Engineering Practices to Embed

### 7.1 Linear — Reliability Through Simplicity

Linear processes millions of tasks for engineering teams globally. Their engineering culture prioritizes:

**No defensive coding theater**: Linear does not add try/catch blocks "just in case." Every error handler is written with a specific failure mode in mind. Generated code should follow this principle: every `try/catch` must have a comment explaining what specific failure it handles and why the error is recoverable.

**Predictable data mutations**: Linear uses optimistic updates with rollback rather than loading states for most user actions. The generated UI pattern for mutations uses React Query's `useMutation` with `onMutate`/`onError`/`onSettled` lifecycle hooks to provide instant feedback with guaranteed consistency.

**Performance as a feature**: Linear's sub-50ms response times are a product feature, not an engineering goal. The generated project includes performance budgets in the build configuration: a Lighthouse CI check in the preview deployment pipeline that fails if performance score drops below 80.

### 7.2 Vercel — Deployment Reliability

Vercel's deployment platform has 99.99% uptime because of practices embedded in their deployment architecture:

**Atomic deployments**: Every deployment is a complete, immutable snapshot. Rollback is instantaneous. The generated project uses Vercel's deployment model where each merge to main creates a new deployment; the previous deployment remains live until the new one passes health checks.

**Preview environments as quality gates**: Every pull request gets a unique preview URL with its own environment variables pointing to the test Supabase project and Stripe test mode. The generated CI pipeline posts the preview URL as a PR comment, making manual testing trivial.

**Environment variable validation at build time**: Vercel fails builds when required environment variables are missing. The generated `next.config.ts` validates environment variables during the build step, not only at runtime, so a missing secret fails fast in CI rather than producing a deployed application that crashes on first use.

### 7.3 Supabase — Open-Source Quality Standards

Supabase's database, authentication, and storage platform is built entirely in open source. Their quality practices that apply to generated SaaS projects:

**Migration versioning**: Supabase uses sequential, timestamped migration files. The generated project follows this pattern: `supabase/migrations/20260101000000_initial_schema.sql`. Migrations are forward-only; rollback is a new migration, not file deletion. This makes database state reproducible and auditable.

**Row Level Security as the primary authorization layer**: Supabase's own products enable RLS on every table without exception. The generated project follows this: application-level authorization (`requireOwnership()`) is a defense-in-depth supplement, not the primary control. If the application layer has a bug, RLS prevents data leakage.

**Type generation**: Supabase generates TypeScript types directly from the database schema (`supabase gen types typescript`). The generated project includes this as a `pnpm db:types` script that regenerates the `src/types/database.ts` file whenever the schema changes. Database changes that break TypeScript types are caught at compile time.

---

## 8. Risks of Quality-First for Generated Code

### 8.1 Slower Initial Deployment

**The real cost**: A developer who runs `sab generate` on Monday and wants to ship their SaaS to the first user on Tuesday will find the quality infrastructure adds approximately 2 hours to the setup process: 30 minutes to understand the test suite structure, 45 minutes to configure CI secrets (Vercel, Supabase, Stripe, Snyk), and 45 minutes to run the E2E suite locally for the first time.

**The mitigation**: The generated `SETUP.md` walks through this process step by step, with copy-paste commands for every step. The 2-hour investment front-loads work that would otherwise occur repeatedly as production incidents.

**The alternative cost**: A SaaS that ships without RLS enabled on its database tables will expose all user data to any authenticated user who knows (or guesses) another user's resource IDs. This is not a theoretical risk — it is the most common SaaS security failure mode and it takes minutes to exploit.

### 8.2 Over-Testing Generated Code

**Real risk**: It is genuinely possible to over-specify tests in generated code, particularly for snapshot tests that freeze implementation details and make refactoring painful.

**The constraint**: Generated tests should test behavior, not implementation. The generated Vitest configuration uses `@testing-library/user-event` for component tests (user behavior) rather than testing React state directly. Snapshot tests are generated only for stable, user-visible outputs (email templates, error messages), not for internal data structures.

**The coverage floor, not ceiling rule**: The generated `vitest.config.ts` enforces 70% as a floor. It does not enforce a ceiling. A developer who achieves 85% coverage in their business logic is not penalized. A developer who lets coverage drop to 55% is blocked in CI.

### 8.3 When Quality Gates Block Legitimate Speed

**The escape hatch**: The generated project includes a `skip-ci` commit message convention that bypasses the E2E test suite for trivial changes (documentation, dependency version bumps). This is documented in the generated `CONTRIBUTING.md` and is intentionally narrow: it skips only E2E tests, never unit tests, type checking, or security scans.

**The override policy**: If a developer needs to ship a hotfix that does not pass the full CI suite, the generated `HOTFIX.md` documents the manual deployment procedure and requires a post-deployment fix within 48 hours. The quality gate is not a wall — it is a standard with a documented exception process.

### 8.4 Minimum Viable Quality vs Enterprise Quality

For the generated SaaS target (solo developer or small team launching), the minimum viable quality gates are:

| Gate | MVQ | Enterprise |
|------|-----|------------|
| TypeScript strict | Required | Required |
| Unit test coverage | 70% | 85%+ |
| Integration tests | Critical paths only | Comprehensive |
| E2E tests | 4 core flows | All user journeys |
| Security scan | npm audit + Snyk | Penetration testing |
| Monitoring | Sentry + basic analytics | Full APM + alerting |
| RLS on all tables | Required | Required |
| Rate limiting | Auth routes only | All routes |
| Accessibility | WCAG 2.1 AA on auth pages | Full site |

The generated project is calibrated to the MVQ column. Enterprise quality requires additional investment that a 3-person team should make consciously, not through generated defaults.

---

## 9. Development Cycle Summary

### From Idea to Production (Quality-First Timeline)

```
Day 0:  sab generate → project scaffold with full quality infrastructure
Day 1:  Configure CI secrets (Vercel, Supabase, Stripe, Snyk) — ~2 hours
        First CI run passes — confirms environment is correct
Day 2:  Add first business feature — all quality gates enforce from day 1
Day 5:  First PR with preview deployment and E2E tests
Day 7:  First production deployment (requires passing all CI gates + manual approval)
```

**Realistic development cycle per feature**: 3-5 days including tests. This is approximately 1.5x slower than a quality-free approach but produces features that do not generate support tickets or security incidents.

**Features in 6 months**: A quality-first generated SaaS can ship 8-10 solid features in 6 months. Each feature ships with tests, is covered by CI, and does not accumulate hidden debt that slows the next feature.

### Recommended Minimum Quality Gates

The non-negotiable quality gates for any generated SaaS are:

1. TypeScript strict mode — no `any`, no implicit nulls
2. RLS enabled on every Supabase table
3. Environment variable validation at startup
4. Rate limiting on all authentication routes
5. Stripe webhook signature verification
6. Security headers on every response
7. Automated dependency vulnerability scanning (weekly)
8. Unit tests for subscription entitlement logic (95% coverage)
9. Integration tests for Stripe webhook handlers
10. E2E test for the subscription purchase flow

These ten gates take approximately 4 hours to configure in a generated project and protect against the failure modes that end SaaS businesses: data breaches, payment fraud, and billing logic errors.

---

## Sources

- [CodeRabbit: AI Code Review Insights 2025 — 1.7x More Issues in AI-Generated Code](https://www.coderabbit.ai/blog/2025-state-of-code-review)
- [OWASP Top 10 2025](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [Supabase Row Level Security Guide](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase TypeScript Type Generation](https://supabase.com/docs/guides/api/rest/generating-types)
- [Supabase Local Development with Docker](https://supabase.com/docs/guides/local-development)
- [Stripe Webhook Signature Verification](https://docs.stripe.com/webhooks/signatures)
- [Stripe Test Clocks for Subscription Testing](https://docs.stripe.com/billing/testing/test-clocks)
- [Stripe Security Best Practices](https://docs.stripe.com/security)
- [Next.js Security Headers](https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy)
- [Next.js Environment Variables Validation](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [Drizzle ORM vs Raw SQL: Parameterized Queries](https://orm.drizzle.team/docs/security)
- [Playwright Testing for Next.js](https://playwright.dev/docs/test-introduction)
- [Testing Library: Guiding Principles](https://testing-library.com/docs/guiding-principles)
- [Zod: TypeScript-First Schema Validation](https://zod.dev/)
- [Pino: Fast Node.js Logger](https://getpino.io/)
- [Sentry Next.js Integration](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Upstash Redis Rate Limiting for Next.js](https://upstash.com/docs/redis/sdks/ratelimit-ts/overview)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel GitHub Actions Integration](https://vercel.com/guides/how-can-i-use-github-actions-with-vercel)
- [Linear Engineering Blog: How Linear Builds Product](https://linear.app/blog/how-linear-builds-product)
- [Snyk: Dependency Vulnerability Scanning for Node.js](https://docs.snyk.io/supported-languages-package-managers-and-frameworks/javascript)
- [GitHub Actions: Manual Approval with Environments](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment)
- [Lighthouse CI GitHub Actions](https://github.com/GoogleChrome/lighthouse-ci)
- [axe-core: Accessibility Testing](https://github.com/dequelabs/axe-core)
- [Vitest Coverage Thresholds](https://vitest.dev/config/#coverage-thresholds)
- [davelosert/vitest-coverage-report-action](https://github.com/davelosert/vitest-coverage-report-action)
- [Biome: Security Lint Rules](https://biomejs.dev/linter/rules/#security)
- [Content Security Policy: A Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [WCAG 2.1 AA Requirements](https://www.w3.org/WAI/WCAG21/Understanding/)
