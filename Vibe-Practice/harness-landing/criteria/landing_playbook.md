# Landing Page Playbook — shared standards for all three agents

This file is the **single source of truth** for what a good Next.js landing page must be.
The Planner specs against it, the Generator builds against it, the Evaluator grades against
it. It is bundled inside the harness on purpose: spawned agents run with `--bare`/`--add-dir`
scoping, so the user's global web rules (`~/.claude/rules/web/*`) do **not** reach them. The
essentials live here instead, so quality is independent of auth mode.

Read this fully before proposing a spec, building a sprint, or grading one.

---

## 1. What "landing page" means here

A landing page is **one focused page** (occasionally with a thank-you/legal sub-route) whose
job is to convert a visitor toward a single primary action. It is NOT a multi-feature app.

- **One primary CTA**, repeated where it makes sense (hero, mid-page, footer).
- **No backend or database by default.** Lead forms post to a Next.js Route Handler that
  validates and returns a result, or to a third-party endpoint the spec names. Add a DB only
  if the spec explicitly requires one.
- **No AI feature unless the spec asks for one.** Marketing pages rarely need the Claude API.
  If the brief asks for it (e.g. an interactive demo), wire it real, never stubbed.

## 2. Tech stack (default — the spec may narrow it)

- **Framework:** Next.js (App Router) + TypeScript.
- **Styling:** Tailwind CSS, **customized** to the spec's design language — never raw library
  defaults. Define design tokens (see §6).
- **Output:** static export (`output: 'export'`) when there is no server logic — the default.
  **`output: 'export'` is incompatible with Route Handlers** (`app/api/*` needs a server), so
  if the brief requires a server-side form, run a **standard Next server** (no `output:
  'export'`) and put the form handler under `app/api/`. Never combine the two.
- **Dev server:** `npm run dev` on `http://localhost:3000` (Next's default — NOT Vite's 5173).
- **Images:** `next/image` with explicit `width`/`height`. **Fonts:** `next/font` (self-hosted,
  `display: swap`). **Metadata:** the App Router `metadata` export (see §7).

## 3. Required page sections (typical — adapt to the brief)

1. **Hero** — value proposition headline, supporting line, primary CTA, hero visual. Must
   communicate what this is and why it matters *above the fold*.
2. **Social proof** — logos, testimonials, ratings, or usage stats.
3. **Features / benefits** — benefit-led, not feature-dump. Scannable.
4. **How it works / details** — process, demo, or deeper explanation.
5. **Pricing or offer** (if relevant).
6. **FAQ** — accessible accordion.
7. **Final CTA + footer** — repeat the conversion action; footer with nav/legal/contact.

## 4. Core Web Vitals — hard targets (Craft dimension)

| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| INP | < 200ms |
| CLS | < 0.1 |
| FCP | < 1.5s |
| TBT | < 200ms |

**Bundle budget (gzipped):** JS < 150kb, CSS < 30kb for the landing page.

Loading discipline:
- Hero image: `priority` / `fetchpriority="high"`. Below-the-fold media: `loading="lazy"`.
- Every image has explicit `width`/`height` — **no layout shift**.
- Preload only the truly critical font weight. `font-display: swap`. Max two families.
- Dynamically import anything heavy (carousels, 3D, animation libs).
- No render-blocking third-party scripts; load them `async`/`defer`, only when needed.

## 5. Responsive — test every breakpoint

Design and verify at **320, 375, 768, 1024, 1440, 1920**. At each:
- No horizontal overflow, no clipped text, no overlapping elements.
- Tap targets ≥ 44px; mobile nav works; hero stays legible.
- Images/grids reflow intentionally (not just shrink).

## 6. Anti-template design quality (Design Quality + Originality dimensions)

The page must look **intentional and specific**, not like a generic template.

**Banned (these tank the Originality score):**
- Centered-headline + gradient-blob + generic CTA stock hero.
- Purple-gradient-on-white-card AI-slop aesthetics.
- Uniform radius / shadow / spacing across every component.
- Default Tailwind or shadcn look shipped unmodified.
- Safe gray-on-white with one decorative accent and no hierarchy.

**Required — demonstrate at least four:**
1. Clear hierarchy through real scale contrast.
2. Intentional spacing rhythm (not uniform padding everywhere).
3. Depth/layering via overlap, surfaces, shadow, or motion.
4. Typography with character and a real pairing strategy.
5. Color used semantically, not just decoratively.
6. Designed hover/focus/active states.
7. Editorial / bento / grid-breaking composition where it fits.
8. Texture, grain, or atmosphere when it suits the direction.

**Design tokens:** define palette, type scale, spacing, radii, durations, easing as CSS
custom properties (or Tailwind theme extension). Do not hardcode the same hex/size repeatedly.
Use `clamp()` for fluid type and section spacing. **No raw `hex`/`rgb`/`hsl`/`rgba` color
literals in component `.tsx`/`.jsx` files** — every color must reference a token.

**Alpha / translucent colors from tokens (important — avoids the most common token trap).**
You often need a semi-transparent version of a brand color (shadows, borders, overlays,
glows). Do NOT drop to `rgba(201,138,43,0.25)`. Instead make the alpha *from the token*:

```css
/* preferred — works with any token color, any color space */
box-shadow: 0 32px 64px -16px color-mix(in oklch, var(--color-primary) 50%, transparent),
            0 0 0 1px color-mix(in oklch, var(--color-accent) 25%, transparent);

/* or define dedicated shadow tokens once, reuse everywhere */
:root { --shadow-elevated: 0 32px 64px -16px color-mix(in oklch, var(--color-primary) 50%, transparent); }
```

If you must keep raw channels for a one-off, store the channels in a token
(`--accent-rgb: 201 138 43;`) and use `rgb(var(--accent-rgb) / 0.25)` — still token-driven,
no literal in the component. This keeps the "no raw color literals" criterion satisfiable
rather than a trap.

## 7. Accessibility (Craft dimension — non-negotiable)

- **Semantic HTML:** `header`/`nav`/`main`/`section`/`footer`, one `h1`, ordered headings.
  No `div` soup where a semantic element exists.
- Color contrast meets **WCAG AA** (4.5:1 text, 3:1 large text/UI).
- Full keyboard operability; visible focus states; logical tab order.
- All images have meaningful `alt` (or empty `alt` for decorative).
- Forms: labels tied to inputs, inline validation, errors announced.
- Honor `prefers-reduced-motion` — gate non-essential motion behind it.

## 8. Motion

- Animate **compositor-friendly properties only**: `transform`, `opacity`, `clip-path`,
  sparingly `filter`. Never animate `width`/`height`/`top`/`left`/`margin`/`font-size`.
- Use `IntersectionObserver` (or a well-behaved lib) for scroll reveals — no scroll-handler
  churn. Add `will-change` narrowly and remove it when done.
- Motion should clarify flow, not distract. All of it respects reduced-motion.

## 9. SEO & sharing

- Unique `<title>` and meta description via the App Router `metadata` export.
- Open Graph + Twitter card tags; a real OG image.
- Semantic headings; descriptive link text. `robots`/`sitemap` if multi-route.
- Relevant structured data (JSON-LD) when it fits (Organization, Product, FAQ).

## 10. Security headers (when a server/host config exists)

Set in `next.config` headers or host config: `Strict-Transport-Security`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`,
a `Content-Security-Policy` (avoid `unsafe-inline` for scripts), `frame-src 'none'`.
Never inject unsanitized HTML; avoid `dangerouslySetInnerHTML` unless sanitized.

---

### Quick verdict checklist (Evaluator)

- [ ] Hero communicates value above the fold; primary CTA is obvious and works.
- [ ] Every CTA/link resolves; every form validates and submits (valid AND invalid input).
- [ ] No overflow/overlap at 320/768/1024/1440.
- [ ] CWV targets met (LCP/CLS/INP); images have dimensions; no layout shift.
- [ ] Looks intentional, not templated (≥4 required qualities; no banned patterns).
- [ ] Keyboard-operable, AA contrast, reduced-motion honored.
- [ ] Title/description/OG present.
