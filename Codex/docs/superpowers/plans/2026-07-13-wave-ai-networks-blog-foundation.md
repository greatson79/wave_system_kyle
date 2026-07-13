# WAVE AI Networks Blog Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and privately deploy the first working WAVE AI Networks multi-route blog on Sites, with the four approved categories and a content structure ready for the later approval workflow.

**Architecture:** This first plan deliberately covers only the public blog foundation. Article data is isolated behind one content module so the second plan can replace seeded records with D1-backed approved posts without rewriting pages. Approval/authentication and Codex scheduling remain separate, independently testable plans because they introduce durable writes, identity, and external execution.

**Tech Stack:** Sites vinext starter, React server components, CSS, Node built-in test runner, Sites private hosting

---

## Scope split

This implementation is Phase 1 of three:

1. **This plan:** public blog foundation, category routes, article routes, responsive styling, accessibility, build, private Sites deployment.
2. **Next plan:** D1 content persistence, protected approval queue, immutable version approval, publish gate.
3. **Final plan:** Tuesday/Friday Codex automations, on-demand topic intake, five-stage content pipeline, notification and recovery.

Phase 1 must not pretend that sample articles are approved production articles. All seeded articles carry `status: "preview"` and the private deployment is for review only.

## File map

- Create project directory: `wave-ai-networks-blog/`
- Create: `wave-ai-networks-blog/lib/content.mjs` — categories, preview articles, lookup functions.
- Create: `wave-ai-networks-blog/tests/content.test.mjs` — content-contract tests.
- Create: `wave-ai-networks-blog/app/components/site-header.tsx` — shared navigation.
- Create: `wave-ai-networks-blog/app/components/article-card.tsx` — article preview card.
- Modify: `wave-ai-networks-blog/app/page.tsx` — home page.
- Create: `wave-ai-networks-blog/app/categories/[slug]/page.tsx` — category listing.
- Create: `wave-ai-networks-blog/app/articles/[slug]/page.tsx` — article detail.
- Create: `wave-ai-networks-blog/app/about/page.tsx` — mission and editorial principles.
- Modify: `wave-ai-networks-blog/app/layout.tsx` — site metadata and shared shell.
- Modify: `wave-ai-networks-blog/app/globals.css` — complete responsive visual system.
- Modify: `wave-ai-networks-blog/package.json` — content test command only if absent.
- Modify: `wave-ai-networks-blog/.openai/hosting.json` — retain generated project metadata; no D1/R2 binding in Phase 1.

### Task 1: Initialize the Sites project

**Files:**
- Create: `wave-ai-networks-blog/` through the Sites initializer

- [ ] **Step 1: Confirm the target does not already contain a project**

Run: `test ! -e wave-ai-networks-blog/package.json`

Expected: exit 0. If the file exists, stop and inspect instead of running a second initializer.

- [ ] **Step 2: Initialize once with the Sites bundled initializer**

Run from the repository root:

```bash
/Users/kylechoi/.codex/plugins/cache/openai-bundled/sites/0.1.27/scripts/init-site.sh "$PWD/wave-ai-networks-blog"
```

Expected: dependency installation completes and the generated project contains `app/page.tsx`, `app/layout.tsx`, `app/globals.css`, `package.json`, and `.openai/hosting.json`.

- [ ] **Step 3: Start the retained development preview**

Run: `npm run dev`

Working directory: `wave-ai-networks-blog/`

Expected: a healthy Local URL is printed. Open that exact URL once in Codex and keep the process alive until private hosting completes.

- [ ] **Step 4: Inspect only the generated product entry points**

Read `app/page.tsx`, `app/layout.tsx`, `app/globals.css`, `package.json`, and `.openai/hosting.json`. Record any path or script difference in this plan before continuing.

- [ ] **Step 5: Commit the generated foundation**

```bash
git add Codex/wave-ai-networks-blog
git commit -m "chore: initialize WAVE blog site"
```

### Task 2: Define and test the content contract

**Files:**
- Create: `wave-ai-networks-blog/lib/content.mjs`
- Create: `wave-ai-networks-blog/tests/content.test.mjs`
- Modify: `wave-ai-networks-blog/package.json`

- [ ] **Step 1: Write the failing contract test**

```js
// tests/content.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { articles, categories, getArticle, getCategoryArticles } from "../lib/content.mjs";

test("defines the four approved categories in editorial order", () => {
  assert.deepEqual(categories.map(({ slug }) => slug), [
    "ai-automation",
    "church-ministry",
    "era-analysis",
    "youth-identity",
  ]);
});

test("keeps preview articles out of the approved state", () => {
  assert.ok(articles.length >= 4);
  assert.ok(articles.every((article) => article.status === "preview"));
  assert.ok(articles.every((article) => article.sources.length > 0));
});

test("looks up articles without leaking another category", () => {
  const article = getArticle(articles[0].slug);
  assert.equal(article?.slug, articles[0].slug);
  assert.ok(getCategoryArticles(article.category).every((item) => item.category === article.category));
});
```

- [ ] **Step 2: Run the test and verify the missing module failure**

Run: `node --test tests/content.test.mjs`

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `lib/content.mjs`.

- [ ] **Step 3: Add the minimal content module**

Create `lib/content.mjs` with this public contract and four clearly labelled preview records:

```js
export const categories = [
  { slug: "ai-automation", name: "AI 자동화", description: "사람을 소외시키지 않는 실제 업무 자동화" },
  { slug: "church-ministry", name: "교회 사역", description: "복음과 공동체를 섬기는 기술과 실천" },
  { slug: "era-analysis", name: "시대 분석", description: "사실과 해석을 구분해 읽는 변화의 흐름" },
  { slug: "youth-identity", name: "청소년 인성·정체성 교육", description: "다음 세대가 자신과 이웃을 이해하도록 돕는 교육" },
];

export const articles = categories.map((category, index) => ({
  slug: `${category.slug}-preview`,
  category: category.slug,
  status: "preview",
  title: `${category.name}, 무엇부터 질문해야 하는가`,
  summary: "공식 발행 전 정보 구조와 읽기 경험을 검토하기 위한 미리보기 글입니다.",
  audience: index === 3 ? "학부모·교사" : "교회 리더·일반 독자",
  readingMinutes: 5,
  publishedAt: "2026-07-13",
  sections: [
    { heading: "문제보다 먼저 볼 것", body: "좋은 변화는 도구보다 사람과 목적을 먼저 살피는 데서 시작합니다." },
    { heading: "WAVE의 관점", body: "사실과 해석을 구분하고, 공동체가 실제로 적용할 수 있는 질문을 제안합니다." },
  ],
  sources: [{ label: "설계 검토용 내부 미리보기", url: "/about" }],
}));

export const getArticle = (slug) => articles.find((article) => article.slug === slug);
export const getCategory = (slug) => categories.find((category) => category.slug === slug);
export const getCategoryArticles = (slug) => articles.filter((article) => article.category === slug);
```

- [ ] **Step 4: Add a test script without changing other scripts**

Add only this key under `scripts` in `package.json`:

```json
"test:content": "node --test tests/content.test.mjs"
```

- [ ] **Step 5: Run the content contract**

Run: `npm run test:content`

Expected: 3 tests pass, 0 fail.

- [ ] **Step 6: Commit the content contract**

```bash
git add Codex/wave-ai-networks-blog/lib/content.mjs Codex/wave-ai-networks-blog/tests/content.test.mjs Codex/wave-ai-networks-blog/package.json
git commit -m "feat: define WAVE blog content contract"
```

### Task 3: Build the shared shell and home page

**Files:**
- Create: `wave-ai-networks-blog/app/components/site-header.tsx`
- Create: `wave-ai-networks-blog/app/components/article-card.tsx`
- Modify: `wave-ai-networks-blog/app/page.tsx`

- [ ] **Step 1: Implement accessible shared navigation**

`site-header.tsx` must render a skip link, the WAVE AI Networks wordmark, links for 홈 and 소개, and a labelled category navigation sourced from `categories`. The current route may be styled through `aria-current="page"`; no client state is required.

- [ ] **Step 2: Implement the reusable article card**

The component contract is:

```tsx
type ArticleCardProps = {
  article: {
    slug: string;
    title: string;
    summary: string;
    audience: string;
    readingMinutes: number;
    category: string;
    status: string;
  };
};
```

It must link to `/articles/${article.slug}`, display the category name, audience, reading time, title, summary, and a visible `미리보기` badge when `status === "preview"`.

- [ ] **Step 3: Replace the starter home page**

The home page must contain, in order:

1. A hero headed `사람과 공동체를 위한 변화의 해석`.
2. A one-sentence WAVE AI Networks editorial promise.
3. Four category links with their descriptions.
4. A latest-articles grid using all preview records.
5. A visible private-review notice stating that preview copy is not published editorial content.

Remove all imports of `app/_sites-preview` from the product page.

- [ ] **Step 4: Verify compilation continuously**

Run: `npm run build`

Expected: PASS with the home route included and no missing import.

- [ ] **Step 5: Commit the shared shell and home page**

```bash
git add Codex/wave-ai-networks-blog/app
git commit -m "feat: build WAVE blog home page"
```

### Task 4: Add category, article, and about routes

**Files:**
- Create: `wave-ai-networks-blog/app/categories/[slug]/page.tsx`
- Create: `wave-ai-networks-blog/app/articles/[slug]/page.tsx`
- Create: `wave-ai-networks-blog/app/about/page.tsx`

- [ ] **Step 1: Add category pages**

Use `getCategory(slug)` and `getCategoryArticles(slug)`. Unknown slugs must call the framework `notFound()` helper. Each valid page renders the category name, description, article count, and `ArticleCard` list.

- [ ] **Step 2: Add article pages**

Use `getArticle(slug)` and call `notFound()` when absent. Render title, summary, audience, reading time, preview badge, sections, and a numbered sources list. Do not render source URLs as plain text; use labelled links.

- [ ] **Step 3: Add the about page**

The page must state the four editorial rules: people before tools, primary sources before summaries, fact separated from interpretation, and publication only after owner approval. Do not claim that the automated approval system exists in Phase 1.

- [ ] **Step 4: Build all routes**

Run: `npm run build`

Expected: PASS with home, about, four category paths, and four article paths available.

- [ ] **Step 5: Commit the routes**

```bash
git add Codex/wave-ai-networks-blog/app/categories Codex/wave-ai-networks-blog/app/articles Codex/wave-ai-networks-blog/app/about
git commit -m "feat: add WAVE blog reading routes"
```

### Task 5: Apply the visual system and metadata

**Files:**
- Modify: `wave-ai-networks-blog/app/globals.css`
- Modify: `wave-ai-networks-blog/app/layout.tsx`
- Remove: `wave-ai-networks-blog/app/_sites-preview/` after imports are gone
- Create: `wave-ai-networks-blog/public/og.png` only after the finished visual direction is stable and the generated card passes inspection

- [ ] **Step 1: Implement one coherent responsive visual system**

Use a warm editorial direction: paper background, near-black text, deep blue primary, restrained amber accent, generous reading width, clear Korean typography fallback, 44px minimum touch targets, visible keyboard focus, and reduced-motion support. Define values once in `:root` custom properties and do not add decorative SVG illustrations.

- [ ] **Step 2: Replace starter metadata**

Set the title to `WAVE AI Networks` and description to `AI 자동화, 교회 사역, 시대 분석, 청소년 인성·정체성 교육을 연결하는 공식 블로그`. Remove any starter `codex-preview` marker.

- [ ] **Step 3: Create and inspect one social preview image**

Generate exactly one landscape social card reflecting the finished site's headline, palette, and editorial motif. Inspect it for invented or malformed Korean text. Retry once only if unusable. Save a passing image as `public/og.png`; otherwise omit image metadata.

- [ ] **Step 4: Remove starter-only preview code and dependency**

Remove `app/_sites-preview` once no product import remains. If `react-loading-skeleton` has no remaining consumer, remove only that dependency and refresh the existing lockfile.

- [ ] **Step 5: Run accessibility-oriented static checks**

Run:

```bash
rg -n "outline:\s*none|user-scalable=no|maximum-scale=1|<img(?![^>]*alt=)" app --pcre2
```

Expected: no matches.

- [ ] **Step 6: Run the complete local verification**

Run:

```bash
npm run test:content
npm run build
```

Expected: all content tests pass and the production build succeeds.

- [ ] **Step 7: Commit visual and metadata completion**

```bash
git add Codex/wave-ai-networks-blog
git commit -m "feat: finish WAVE blog visual system"
```

### Task 6: Validate and privately publish Phase 1

**Files:**
- Modify: `wave-ai-networks-blog/.openai/hosting.json` only with the Sites project id and null unused bindings

- [ ] **Step 1: Confirm the deployment boundary**

Verify `.openai/hosting.json` contains no credentials and leaves unused `d1` and `r2` bindings null. Confirm every article still has `status: "preview"`.

- [ ] **Step 2: Reuse the successful build**

Do not rebuild if source has not changed since Task 5. Package the validated output with the Sites bundled packaging helper.

- [ ] **Step 3: Create and deploy a private Sites version**

Create the site once, persist only its project id, save the exact validated version, deploy privately, and poll until the status is `succeeded` or a terminal failure is returned. Do not request public deployment in this phase.

- [ ] **Step 4: Open the successful private URL**

Open the exact deployed URL in Codex only after deployment reports success.

- [ ] **Step 5: Record the Phase 1 handoff**

Report the private URL, routes present, content-test result, build result, and the explicit limitation that approval/authentication and scheduled generation are Phase 2 and Phase 3.

## Plan self-review

- Spec coverage: Phase 1 covers public information architecture, four categories, audience-aware previews, responsive reading, source display, private validation, and Sites hosting. Durable approval and scheduling are explicitly assigned to later plans rather than silently omitted.
- Placeholder scan: every code-writing step contains a concrete contract, content, command, or expected result.
- Type consistency: category and article fields used by cards and routes match the `content.mjs` contract.
- Risk boundary: no authentication, public deployment, credentials, D1 mutation, or external publishing is introduced in Phase 1.
