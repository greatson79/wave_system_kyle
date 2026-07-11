# Agent Guardrails

These guardrails prevent My GPTs imports from weakening the existing harness.

## Non-Negotiable Rules

- Preserve original My GPTs instructions under `agent-growth/gpts/raw/`.
- Do not paste raw My GPTs instructions directly into `AGENTS.md`.
- Do not publish a skill to `.agents/skills/` until it has a review note.
- Do not import secrets, credentials, private tokens, or browser session data.
- Do not convert external GPT Actions into live scripts without an explicit
  security review.
- Do not make destructive curation the default.

## Conflict Handling

When a My GPT instruction conflicts with local rules:

1. Prefer direct user instructions for this workspace.
2. Preserve the source instruction in the raw file.
3. Record the conflict in the normalized JSON.
4. Apply the safer local rule until the user decides otherwise.

## Scope Rules

- Global operating rules belong in `AGENTS.md` only if they apply to every
  task.
- Workflow sequencing belongs in `AGENT_WORKFLOWS.md`.
- Reusable specialist behavior belongs in `.agents/skills/`.
- Unreviewed drafts belong in `agent-growth/skills/`.
- Detailed source material belongs in `references/` near the skill that uses it.
