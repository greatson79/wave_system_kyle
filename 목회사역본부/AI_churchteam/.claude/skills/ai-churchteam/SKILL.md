---
name: ai-churchteam
description: Route church ministry requests through the AI Church Team. Use for `/팀` team requests, ministry strategy analysis, annual, monthly, quarterly, or health-check planning, and for requests that need pastoral safeguards, theological reasoning, weekly-works, or church-admin coordination.
---

# AI Church Team

Resolve this `SKILL.md` realpath, then resolve `../../..` from it as `<root>`. Before acting, read `<root>/CLAUDE.md` and `<root>/.claude/state.yaml`. Route the request before creating or changing any ministry artifact.

## Guardrails

- Read the relevant material in `pastor/philosophy/` first; treat it as the pastoral SOT.
- Treat `<root>/.claude/state.yaml` as the single state source. Only the 총괄팀장 may write `state.yaml`; every other Lead Orchestrator member may write only `<root>/.claude/workflow-state.yaml` for in-progress work.
- Apply the theological filter to every output. Use `theological-reasoning` for biblical interpretation, doctrinal analysis, or theological-risk checks.
- Treat the senior pastor as the final decision-maker. Request approval for decisions, publication, or any theological concern that needs pastoral judgment.
- Do not modify downstream internals. Coordinate only through the documented bridges.

## Route

| Request | Entry point or skill |
|---|---|
| General team request, team meeting, or selecting a specialist team | `/팀` |
| Cultural change, ministry direction, or scenario analysis | `/팀-전략분석` |
| Annual ministry direction or annual plan | `/팀-연간계획` |
| Monthly education, operations, or preparation | `/팀-월간` |
| Quarterly evaluation and next-quarter preparation | `/팀-분기` |
| System health or six-signal verification | `/팀-건강` and `$health-dashboard` |
| Biblical text, sermon theology, or doctrinal alignment | `$theological-reasoning` |

When the request needs sermon preparation, weekly content, or weekly progress, read `<root>/.claude/skills/weekly-works-bridge.md` and use its documented interface only. When it needs bulletins, member information, finances, or church administration, read `<root>/.claude/skills/church-admin-bridge.md` and use its documented interface only.

State the selected route, needed approvals, and the applicable safeguards before proceeding. Keep outputs aligned with the pastoral philosophy and preserve the named system boundaries.
