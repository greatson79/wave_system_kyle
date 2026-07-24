# 🏗️ Harness Engineering System — Landing-Page Edition

A production-grade, **three-agent harness** that autonomously builds **Next.js/React
landing pages**. GAN-style **Generator ↔ Evaluator** loop, supervised by a **Planner**,
inspired by Anthropic's harness-design research.

> This is a **dedicated copy of the generic `harness/`**, specialized for landing pages.
> The orchestration plumbing is identical; the specialization lives in the prompts, the
> bundled `criteria/landing_playbook.md` (CWV, responsive, anti-template, a11y, SEO), the
> grading rubric, and config (`max_sprints: 5`, craft weight raised). The default stack is
> Next.js (App Router) + TypeScript + Tailwind, dev server on **:3000**.

Agents never call each other directly — they communicate **only through files** in
`artifacts/`. The site being built lives in an **isolated workspace with its own git
repo**, never the parent monorepo.

> **Safety model: cooperative isolation + rollback, not a hard sandbox.** `--add-dir`
> scopes the *file* tools (Read/Write/Edit) to the workspace, and the Generator is the
> only agent that builds there. But the Generator also has `Bash`, and shell commands are
> **not** bound by `--add-dir` — a determined or confused command could still reach the
> wider filesystem. The real protections are: (1) agents are cooperative and prompted to
> stay in-workspace, (2) the workspace has its own git with per-sprint commits for
> rollback, (3) the Evaluator is read-only on source with a git-revert backstop, and
> (4) the monorepo is never `git add`ed by the harness. For a true hard sandbox, run the
> harness inside a container/VM scoped to `harness/workspace/`.

```
User Prompt (1–4 sentences)
        │
        ▼
┌──────────────┐  writes artifacts/plan/PRODUCT_SPEC.md + sprints.json
│   PLANNER    │  → page vision, design language, sections, 4–5 sprints
└──────┬───────┘
       │
       ▼  for each sprint:
┌──────────────┐   contract    ┌──────────────┐
│  GENERATOR   │◄─────────────►│  EVALUATOR   │
│              │   QA report   │ (Playwright) │
│ propose →    │               │ review →     │
│ build →      │               │ live test →  │
│ fix bugs     │               │ grade+verdict│
└──────┬───────┘               └──────────────┘
       │  (isolated git workspace, commit per sprint)
       ▼
   Final Landing Page (Next.js)
```

---

## Why this design (key decisions)

| Decision | Rationale |
|----------|-----------|
| **Backend = local `claude` CLI** (headless `-p`) | It *is* Claude Code: full file/Bash/git tools, MCP (Playwright), and your existing auth — no separate API key for OAuth/subscription users. No `pip install` of an SDK. |
| **Isolated workspace + own git** | Agents build in `workspace/<run-id>/` with a fresh `git init`. The monorepo (with its dozens of unrelated changes) is never touched or committed. Per-sprint commits give rollback. |
| **Evaluator is read-only on app source** | It runs/reads/drives the app but doesn't edit it. A git-dirty backstop reverts any stray edits. |
| **Structured `*.json` sidecars** | The orchestrator reads `sprints.json` / contract / QA JSON (schema-validated) — never regex on prose. Deterministic control flow. |
| **Mechanical verdict re-check** | The orchestrator recomputes PASS/FAIL from the structured QA data rather than trusting the agent's self-declared label. |
| **`--dry-run` mode** | Exercises the entire loop (schemas, signals, fix-loop, git) without spawning agents — free and instant. |

---

## Directory layout

```
harness-landing/
├── HARNESS_README.md          # this file
├── run_harness.py             # orchestrator entry point
├── agents/
│   ├── _context.py            # paths, signal tokens, schema validation, workspace git
│   ├── _runtime.py            # claude CLI driver + wiring probe
│   ├── planner.py / generator.py / evaluator.py   # landing-page dry-run stubs
├── prompts/                   # *_system.md — landing-page / Next.js agent system prompts
├── schemas/                   # product_spec / sprint_contract / qa_report JSON Schemas
├── criteria/
│   ├── evaluation_criteria.md # 4-dimension grading rubric (landing-page weighting)
│   └── landing_playbook.md    # bundled web standards: CWV, responsive, anti-template, a11y, SEO
├── config/
│   ├── harness_config.yaml    # all tunable parameters
│   └── playwright_mcp.json    # MCP config handed to the evaluator
├── artifacts/                 # runtime (gitignored): plan/ sprints/ session/
├── workspace/                 # isolated per-run app dirs (gitignored), each own git
└── tests/test_harness_wiring.py
```

---

## Install

This folder is a **self-contained standalone project** — it imports nothing from the
parent repo and can be lifted out and run anywhere.

```bash
cd harness-landing

# 1) Python deps — the complete set, declared in requirements.txt
pip install -r requirements.txt        # PyYAML + jsonschema

# 2) Execution backend — the Claude Code CLI (must be installed & authenticated)
claude --version                        # confirm it exists

# 3) Evaluator's browser driver — Playwright MCP, auto-fetched via npx on first use
node --version                          # needs Node.js / npx (no pip install)
```

No `ANTHROPIC_API_KEY` is required if you're signed into Claude Code (OAuth/subscription).
Set one only if you want `bare_mode` cleaner-context runs (see config).

**To publish as its own git repo later:** copy the folder out of the monorepo and
`git init` there — nothing in the code assumes the monorepo location.

---

## Usage

```bash
cd harness-landing

# 1) Verify the loop plumbing — free, instant, spawns NO agents
python run_harness.py "A launch landing page for a productivity app — hero, features, pricing, FAQ" --dry-run

# 2) Confirm the real CLI backend works — one cheap haiku call (~1 cent)
python run_harness.py --check

# 3) Run for real (spawns Planner → Generator/Evaluator per sprint)
python run_harness.py "A launch landing page for a productivity app — hero, features, pricing, FAQ"

# Name the run / workspace, resume from a sprint, use a custom config
python run_harness.py "..." --run-id coffee
python run_harness.py "..." --run-id coffee --start-sprint 3
python run_harness.py "..." --config /path/to/harness_config.yaml

# Watch progress live
tail -f artifacts/sprints/sprint_1_contract.md
tail -f artifacts/sprints/sprint_1_qa_report.md

# Run the finished site
cd workspace/<run-id> && cat README.md   # follow its start command
```

> ⚠️ **Cost & time.** A real run is a multi-hour, multi-dollar autonomous build (it spawns
> long `claude` sessions per sprint phase). Always `--dry-run` and `--check` first. The
> Section-12 validation below is a deliberate, user-triggered real run.

---

## Inter-agent protocol (file-based only)

State changes are signalled by appending **tokens** on their own final line of an artifact:

| Token | Meaning |
|-------|---------|
| `READY_FOR_CONTRACT_REVIEW` | Generator → Evaluator: review the proposed contract |
| `CONTRACT_APPROVED` | Evaluator → Generator: start building |
| `READY_FOR_QA` | Generator → Evaluator: build/fix done, test it |
| `QA_COMPLETE` | Evaluator → Generator: QA results written |
| `SPRINT_PASSED` / `SPRINT_FAILED` | Evaluator verdict |
| `HARNESS_COMPLETE` | All sprints done |

Each exchange also writes a **schema-validated JSON sidecar** that the orchestrator reads:

- `artifacts/plan/sprints.json` → `schemas/product_spec.schema.json`
- `artifacts/sprints/sprint_N_contract.json` → `schemas/sprint_contract.schema.json` (≥15 criteria)
- `artifacts/sprints/sprint_N_qa_report.json` → `schemas/qa_report.schema.json`

`artifacts/session/handoff.md` is rewritten each sprint for cross-session resume.

---

## Grading

Four weighted dimensions (`criteria/evaluation_criteria.md`):

| Dimension | Weight | Pass |
|-----------|--------|------|
| Design Quality | 35% | ≥6/10 |
| Originality | 25% | ≥6/10 |
| Craft | 25% | ≥7/10 |
| Functionality | 15% | ≥7/10 |

Craft is weighted higher than a generic app build (0.25 vs 0.20) because a landing page must
be flawless across breakpoints and meet Core Web Vitals; see `criteria/landing_playbook.md`.

A sprint clears only if **every** dimension passes, `overall_score ≥ qa_pass_threshold`,
**no CRITICAL bug** remains, and **no criterion** is graded FAIL. The Evaluator's system
prompt is explicitly tuned for **skepticism, not leniency**.

---

## Configuration (`config/harness_config.yaml`)

Key knobs:

- `harness.max_sprints` (default **5** for a single page) `/ max_qa_rounds / qa_pass_threshold / min_criteria_per_sprint`
- `models.{planner,generator,evaluator}` — real IDs. Cost-tuned default:
  planner/evaluator = `claude-opus-4-8`, generator = `claude-sonnet-4-6`. Set all to
  `claude-opus-4-8` to match the original all-opus spec.
- `context.bare_mode` = `auto|always|never` — `--bare` (clean/cheap context) auto-enables
  only when `ANTHROPIC_API_KEY` is set, so OAuth auth is never broken.
- `execution.{generator,evaluator}_permission_mode` — set evaluator to `bypassPermissions`
  for a fully hands-off Playwright run (safe because the workspace is isolated).
- `safety.*` — workspace isolation, per-sprint commits, evaluator revert backstop.

---

## Tool scoping (per agent)

| Agent | cwd | Tools | MCP |
|-------|-----|-------|-----|
| Planner | `harness-landing/` | Read, Write, Edit, Glob, Grep, Skill, WebFetch | — |
| Generator | `workspace/<run>/` | + Bash, NotebookEdit (full build) | — |
| Evaluator | `workspace/<run>/` | Read, Glob, Grep, Bash, Write (reports only); **Edit disallowed** | Playwright |

File access is further scoped with `--add-dir` (workspace + `artifacts/` + `schemas/`
+ `criteria/` only) so agents can't roam the monorepo.

---

## Validation (Section 12 — user-triggered real run)

```bash
python run_harness.py "A landing page for an indie coffee roaster — story, bestsellers, subscribe CTA"
```

Expected: a `PRODUCT_SPEC.md` with 4–5 sprints + design language; contracts with ≥15
criteria each; Evaluator QA driving the live app via Playwright; QA reports with
PASS/FAIL per criterion; at least Sprint 1 completing with a working hero + shell at :3000.

The **plumbing** for all of the above is already verified automatically:

```bash
python tests/test_harness_wiring.py   # schemas, dry-run loop, fix-loop, isolated git
python run_harness.py --check          # real CLI backend (one haiku call)
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `--check` fails | `claude` not authenticated or not on PATH. Run `claude` once interactively. |
| Planner halts with schema error | The model emitted malformed `sprints.json`. Re-run; lower scope; check the schema. |
| Evaluator can't drive the browser | Node/`npx` missing, or permission prompts blocking — set `evaluator_permission_mode: bypassPermissions`. |
| Agent times out | Raise `execution.agent_timeout_seconds` or split the sprint. |
| Want cheaper runs | Set generator/evaluator to `claude-sonnet-4-6` / `claude-haiku-4-5` in config. |
