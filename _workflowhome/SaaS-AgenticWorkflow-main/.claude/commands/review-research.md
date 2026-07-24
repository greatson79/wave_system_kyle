# Step 4: Research Findings Review — Human Checkpoint

This is a human review checkpoint at the end of the Research phase (Steps 1-3).

## What to Present

Read and summarize the following outputs for user review:

1. **Step 1 — PRD Foundation Analysis**: `prompt/research/prd-foundation-analysis.md`
   - Key findings about PRD structure, features, architecture decisions

2. **Step 2 — Multi-Perspective Deep Analysis** (3 team outputs):
   - Architecture & Engine: `prompt/research/arch-engine-analysis.md`
   - Feature & UX: `prompt/research/feature-ux-analysis.md`
   - Business & Quality: `prompt/research/biz-quality-analysis.md`

3. **Step 3 — Research Synthesis & Gap Analysis**: `prompt/research/synthesis-and-gaps.md`
   - Cross-cutting findings, contradictions, gaps, open questions

## Review Format

Present a concise summary (not full content) with:
- Top 5 key findings across all analyses
- Identified gaps or contradictions
- Open questions that need resolution before Planning phase
- Recommendation: proceed to Planning or request additional research

## User Actions

Ask the user:
1. **Approve** — Proceed to Planning phase (Steps 5-8)
2. **Request changes** — Specify what needs additional analysis
3. **Pause** — Save current state and pause workflow

After approval, update SOT:
```
python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step 4 --output "approved-by-user"
```
