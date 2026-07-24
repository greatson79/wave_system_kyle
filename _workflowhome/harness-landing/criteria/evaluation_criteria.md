# Evaluation Criteria — Harness Grading Rubric (Landing-Page Edition)

Used by **both** the Generator (for honest self-evaluation before handoff) and the
Evaluator (for grading). Scores feed `scores{}` and `overall_score` in
`qa_report.schema.json`. Read alongside `criteria/landing_playbook.md`, which holds the
concrete bars (Core Web Vitals, breakpoints, anti-template checklist).

## Scoring Scale

Each criterion scored **1–10**. The weighted total determines sprint approval.

| Dimension | Weight | PASS threshold |
|-----------|--------|----------------|
| Design Quality | 35% | 6 / 10 |
| Originality | 25% | 6 / 10 |
| Craft | 25% | 7 / 10 |
| Functionality | 15% | 7 / 10 |

`overall_score = 0.35·design + 0.25·originality + 0.25·craft + 0.15·functionality`

---

## 1. Design Quality (Weight: 35%)

Does the design feel like a coherent whole, not a collection of parts?

- Colors, typography, layout, and imagery combine to create a distinct mood and identity.
- The design has a recognizable visual personality, not generic.
- Spacing, density, and hierarchy feel intentional throughout.

**FAIL indicators (score ≤ 4):**

- Components feel like they're from different design systems.
- No consistent visual theme or color application.
- Generic "SaaS dashboard" look with no distinctive character.

**PASS threshold: 6/10**

---

## 2. Originality (Weight: 25%)

Is there evidence of deliberate creative decisions?

- Layout goes beyond standard landing-page template patterns (not the centered-headline +
  gradient-blob + generic-CTA stock hero).
- Color and typography choices feel specific to this product.
- No unmodified stock components or AI-slop patterns (purple gradients on white cards, etc.).
- A human designer would recognize intentional choices (see the playbook's required-qualities
  list — at least four should be evident).

**FAIL indicators (score ≤ 4):**

- Looks like it could be any generic SaaS landing page.
- Uses default Tailwind/shadcn patterns without customization.
- Telltale AI-generation aesthetics.

**PASS threshold: 6/10**

---

## 3. Craft (Weight: 25%)

Technical execution quality — for a landing page this carries extra weight because a single
marketing page must be flawless across devices and fast:

- Typography hierarchy is clear and consistent.
- Spacing is consistent (design tokens or a consistent scale; `clamp()` for fluid scaling).
- Color contrast ratios meet WCAG AA; the page is fully keyboard-operable with visible focus.
- Responsive behavior works correctly across **320 / 768 / 1024 / 1440** — no overflow,
  overlap, or clipped content at any of them.
- **Core Web Vitals targets met** (LCP < 2.5s, CLS < 0.1, INP < 200ms); images carry explicit
  dimensions (no layout shift); no render-blocking resources.
- Motion is compositor-friendly and respects `prefers-reduced-motion`.
- No broken layouts, overflow issues, or visual glitches.

**PASS threshold: 7/10** (this is a competence check — the floor is higher)

---

## 4. Functionality (Weight: 15%)

Does the page actually work and drive its one action? (Usability independent of aesthetics.)

- A visitor immediately understands what this is and what to do (value clear above the fold).
- The **primary CTA is obvious and works**; secondary CTAs/links all resolve (no dead/`#`
  links for shipped actions).
- **Forms submit and validate** — valid input succeeds, invalid input shows clear inline
  errors; success/error states are handled.
- Loading and empty states are handled where relevant.
- If — and only if — the spec named an AI/interactive element, it works **end-to-end** (NOT
  stubbed).

**FAIL indicators:**

- The primary CTA is dead or unclear.
- Sections are visually present but lorem-only or non-interactive.
- A form silently fails or accepts invalid input.
- A spec-required AI/interactive element is placeholder only.

**PASS threshold: 7/10**

---

## Sprint Approval Rule

A sprint **PASSES** only if **ALL** of the following hold:

1. Every individual dimension meets its PASS threshold.
2. `overall_score` ≥ `qa_pass_threshold` (default 6.0, see `harness_config.yaml`).
3. No **CRITICAL** bugs remain in the bug log.
4. No core feature is stubbed or non-functional.
5. No contract criterion is graded **FAIL**. PARTIAL is allowed on non-core polish criteria,
   at the Evaluator's discretion. **Grade by impact:** functional/core breaks (dead CTA, form
   failure, broken responsive layout, a11y blocker, CWV miss) are FAIL; cosmetic or
   code-discipline lapses (a hardcoded color that should be a token, missing favicon, a
   sub-millisecond reduced-motion value) are PARTIAL — real, logged as MEDIUM/LOW bugs, but
   not sprint-blocking. Reserving FAIL for what a visitor can see or do keeps the skeptical
   gate from sinking a functionally-done page over a one-line nit.

If any condition fails → verdict **FAIL**, `next_sprint_cleared: false`, and the
Generator must fix every FAIL/CRITICAL item before the next QA round.
