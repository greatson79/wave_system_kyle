# Step 12: Final PRD Review & Approval — Human Checkpoint

This is the final human review checkpoint. The complete PRD document is ready for approval.

## What to Present

Read and summarize:

1. **Step 10 — Cross-Validated PRD**: `prompt/implementation/prd-validated.md`
   - Structural validation results from `scripts/validate_prd_structure.py`

2. **Step 11 — Adversarial Review**: `prompt/review/prd-adversarial-review.md`
   - @reviewer findings: Critical issues, Warnings, Suggestions
   - @fact-checker findings: Claim verification results
   - Review report: `review-logs/step-11-review.md`

3. **Quality Metrics Summary**:
   - Read `.claude/state.yaml` pacs.history for all step scores
   - Calculate average pACS across all steps
   - Identify weakest dimension (F/C/L)

## Review Format

Present:
- PRD document statistics (sections, lines, code blocks, diagrams)
- Structural validation results (all 16 sections present, no placeholders)
- Adversarial review summary (critical issues count, resolution status)
- pACS score summary (per-step and average)
- Final recommendation

## User Actions

Ask the user:
1. **Approve** — Finalize PRD, trigger @translator for final .ko.md
2. **Request revisions** — Specify changes, trigger re-generation cycle
3. **Reject** — Document issues and pause workflow

After approval:
1. Copy validated PRD to final location:
   - EN: `prompt/PRD-SaaS-AutoBuilder.md`
   - KO: (produced by @translator) `prompt/PRD-SaaS-AutoBuilder.ko.md`
2. Update SOT:
   ```
   python3 .claude/hooks/scripts/sot_manager.py --project-dir . --update-step 12 --output "prompt/PRD-SaaS-AutoBuilder.md"
   python3 .claude/hooks/scripts/sot_manager.py --project-dir . --add-translation 12 --ko-path "prompt/PRD-SaaS-AutoBuilder.ko.md"
   python3 .claude/hooks/scripts/sot_manager.py --project-dir . --set-status completed
   ```
