# My GPTs Import Staging

This directory stages My GPTs instructions before they become Codex workflows
or skills.

## Rules

- `raw/` stores untouched source text.
- `normalized/` stores structured extraction JSON.
- `reviews/` stores promotion and safety review notes.
- `publication-queue/` stores reviewed items ready to publish.
- Do not delete or rewrite raw imports.
- Do not publish directly from raw text.
- Redact secrets before creating references, skills, or scripts.
