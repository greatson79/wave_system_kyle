# Workflow Status Dashboard

Display the current workflow status by reading the SOT and running diagnostics.

## Execution

Run the workflow dashboard:
```bash
python3 .claude/hooks/scripts/query_workflow.py --dashboard
```

Also show:
1. **SOT State**: Read `.claude/state.yaml` and display current_step, status, outputs count
2. **pACS History**: Show pACS scores for all completed steps
3. **Translation Status**: For each completed step with translate=true, check if .ko.md exists
4. **Active Team**: If active_team exists, show team name, completed/pending tasks

## Output Format

```
=== SaaS Auto-Builder PRD Workflow Status ===

Phase: Research / Planning / Implementation
Current Step: N/12 — "Step Name"
Status: running / completed / error / paused

Completed Steps:
  Step 1: PRD Foundation Extraction ✓ (pACS: 85, EN+KO)
  Step 2: Multi-Perspective Analysis ✓ (pACS: 78, EN+KO)
  ...

Next Steps: [5, 6] (parallel — deps satisfied)

Active Team: prd-analysis-team (2/3 tasks completed)

Average pACS: 82 (Weakest: C)
```
