---
name: reformed-sermon-workflow
description: Orchestrate the full Reformed gospel-centered sermon preparation workflow. Use for Korean or English requests involving 개혁주의 복음 중심 설교, sermon preparation, CMT/FCF/HP workflow, Christ-centered sermon outlines, sermon manuscripts, gospel application, or theology review across the full sermon process.
---

# Reformed Sermon Workflow

Use this as the coordinator for full sermon-preparation requests. If the user asks for only CMT, FCF, HP,본문 연구, 설교문, or review, call the narrower skill instead of forcing the full workflow.

## Required References

Read these shared references before full workflow work:

- `references/theological-guardrails.md`
- `references/translation-policy.md`
- `references/sermon-framework.md`
- `references/output-formats.md`
- `references/quality-checklist.md`

Read `references/cmt-fcf-hp-rules.md` before any CMT, FCF, or HP output.

## Procedure

1. Identify the requested passage, audience, output type, and scope.
2. If passage, audience, or output type is unclear, ask one or two clarifying questions.
3. Keep the requested scope. Do not generate a full sermon when the user asks for one stage.
4. Route the task:
   - 본문 연구: use `biblical-text-research`.
   - CMT/FCF/HP: use `cmt-fcf-hp-builder`.
   - 설교 흐름: use `christ-centered-sermon-arc`.
   - 설교문 or outline: use `sermon-manuscript-builder`.
   - 신학/품질 검토: use `sermon-theology-reviewer`.
5. Assemble outputs in the format requested by the user.
6. Mark uncertain historical, linguistic, or source claims as `확인 필요`.
7. Run the quality checklist before finalizing.

## Output Rule

Keep output structured and concise unless the user asks for a full manuscript.
