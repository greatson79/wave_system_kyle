# Step 8: Planning Review & Approval — Human Checkpoint

This is a human review checkpoint at the end of the Planning phase (Steps 5-7).

## What to Present

Read and summarize the following outputs for user review:

1. **Step 5 — PRD Document Architecture**: `prompt/planning/prd-architecture.md`
   - Document structure, section hierarchy, cross-reference map

2. **Step 6 — Intent Capture & Question Flow Spec**: `prompt/planning/intent-capture-spec.md`
   - 7-state FSM design, question flow (5-7 questions), branching logic
   - Review report: `review-logs/step-6-review.md` (L2 adversarial review results)

3. **Step 7 — Engine Pipeline & Quality Framework**: `prompt/planning/engine-quality-specs.md`
   - E1-E8 pipeline quality specifications, acceptance criteria
   - Review report: `review-logs/step-7-review.md` (L2 adversarial review results)

## Review Format

Present a concise summary with:
- Document architecture overview (section count, estimated total size)
- Intent capture FSM summary (states, transitions, key questions)
- Engine pipeline quality criteria highlights
- L2 review findings (any Critical or Warning issues from @reviewer)
- Recommendation: proceed to Implementation or revise

## User Actions

Ask the user:
1. **Approve** — Proceed to Implementation phase (Steps 9-12)
2. **Request changes** — Specify revisions needed
3. **Pause** — Save current state and pause workflow

After approval, update SOT:
```
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step 8 --output "approved-by-user"
```
