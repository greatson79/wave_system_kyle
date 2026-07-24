# Evaluation Criteria — Harness Grading Rubric

Used by **both** the Generator (for honest self-evaluation before handoff) and the
Evaluator (for grading). Scores feed `scores{}` and `overall_score` in
`qa_report.schema.json`.

## Scoring Scale

Each criterion scored **1–10**. The weighted total determines sprint approval.

| Dimension | Weight | PASS threshold |
|-----------|--------|----------------|
| Design Quality | 35% | 6 / 10 |
| Originality | 30% | 6 / 10 |
| Craft | 20% | 7 / 10 |
| Functionality | 15% | 7 / 10 |

`overall_score = 0.35·design + 0.30·originality + 0.20·craft + 0.15·functionality`

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

## 2. Originality (Weight: 30%)

Is there evidence of deliberate creative decisions?

- Layout goes beyond standard template patterns.
- Color and typography choices feel specific to this product.
- No unmodified stock components or AI-slop patterns (purple gradients on white cards, etc.).
- A human designer would recognize intentional choices.

**FAIL indicators (score ≤ 4):**

- Looks like it could be any generic web app.
- Uses default Tailwind component patterns without customization.
- Telltale AI-generation aesthetics.

**PASS threshold: 6/10**

---

## 3. Craft (Weight: 20%)

Technical design execution quality:

- Typography hierarchy is clear and consistent.
- Spacing is consistent (design tokens or a consistent scale).
- Color contrast ratios meet WCAG AA.
- Responsive behavior works correctly across 320 / 768 / 1024 / 1440.
- No broken layouts, overflow issues, or visual glitches.

**PASS threshold: 7/10** (this is a competence check — the floor is higher)

---

## 4. Functionality (Weight: 15%)

Usability independent of aesthetics:

- Users can understand what the interface does.
- Primary actions are discoverable.
- Core workflows complete without guessing or errors.
- Error states and loading states are handled.
- AI features work end-to-end (NOT stubbed).

**FAIL indicators:**

- Core feature of the product doesn't work.
- Features are visually present but not interactive.
- AI integration is placeholder only.

**PASS threshold: 7/10**

---

## Sprint Approval Rule

A sprint **PASSES** only if **ALL** of the following hold:

1. Every individual dimension meets its PASS threshold.
2. `overall_score` ≥ `qa_pass_threshold` (default 6.0, see `harness_config.yaml`).
3. No **CRITICAL** bugs remain in the bug log.
4. No core feature is stubbed or non-functional.
5. No contract criterion is graded **FAIL** (PARTIAL is allowed only on non-core polish criteria, at the Evaluator's discretion).

If any condition fails → verdict **FAIL**, `next_sprint_cleared: false`, and the
Generator must fix every FAIL/CRITICAL item before the next QA round.
