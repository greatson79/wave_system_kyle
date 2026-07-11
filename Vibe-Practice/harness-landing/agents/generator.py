"""Generator agent — proposes contracts, builds sprints, fixes QA bugs.

Communicates only via files in artifacts/sprints/. Builds inside the isolated workspace.
"""
from __future__ import annotations

import json

from . import _context as ctxmod
from ._context import (
    READY_FOR_CONTRACT_REVIEW,
    READY_FOR_QA,
    RunContext,
    append_signal,
    git_commit,
    git_head,
    validate_json_file,
)
from ._runtime import AgentResult, ensure_ok, run_claude

SYSTEM_PROMPT = (ctxmod.HARNESS_DIR / "prompts" / "generator_system.md")

ALLOWED_TOOLS = [
    "Read", "Write", "Edit", "Glob", "Grep", "Bash", "Skill",
    "WebFetch", "TodoWrite", "NotebookEdit",
]


def run_generator(ctx: RunContext, *, phase: str, sprint: int, round: int = 1) -> AgentResult:
    if ctx.dry_run:
        return _dry_run(ctx, phase=phase, sprint=sprint, round=round)

    builders = {
        "propose_contract": _task_propose,
        "build": _task_build,
        "fix_bugs": _task_fix,
    }
    if phase not in builders:
        raise ValueError(f"Unknown generator phase: {phase}")
    task = builders[phase](ctx, sprint, round)

    # Capture HEAD before the build/fix round so we can tell whether the workspace actually
    # advanced. The generator commits its OWN work (per its prompt), so the orchestrator's
    # safety git_commit below is normally a no-op — we must NOT treat that as failure.
    head_before = git_head(ctx)

    result = run_claude(
        ctx,
        role=f"generator:{phase}",
        system_prompt=SYSTEM_PROMPT.read_text(encoding="utf-8"),
        task_prompt=task,
        model=ctx.config["models"]["generator"],
        cwd=ctx.workspace_dir,
        allowed_tools=ALLOWED_TOOLS,
        add_dirs=[ctx.artifacts_dir, ctx.schemas_dir, ctx.harness_dir / "criteria"],
        permission_mode=ctx.config["execution"].get("generator_permission_mode", "acceptEdits"),
    )

    ensure_ok(result, f"generator:{phase}")

    # gate per phase
    if phase == "propose_contract":
        validate_json_file(ctx, ctx.contract_json(sprint), "sprint_contract.schema.json")
    elif phase in ("build", "fix_bugs"):
        # Safety net: commit any leftovers the agent forgot to commit (usually nothing —
        # the agent commits itself). Then verify the workspace ADVANCED: HEAD must have moved
        # (via the agent's commit or ours). If HEAD is unchanged, the round did real nothing —
        # stop loudly instead of looping over unchanged code (re-QA would just re-fail).
        git_commit(ctx, f"sprint {sprint}: {phase} (round {round}) [harness safety commit]")
        if git_head(ctx) == head_before:
            raise RuntimeError(
                f"[generator:{phase} sprint {sprint} round {round}] workspace did not advance "
                f"(no new commit) — the round was a real no-op. Likely the agent failed to "
                f"apply changes or hit a limit. Stopping instead of looping. "
                f"Agent output head: {result.text[:300]!r}"
            )
    return result


# ── real-mode task prompts ──────────────────────────────────────────────────────
def _task_propose(ctx: RunContext, sprint: int, round: int) -> str:
    return f"""PHASE: propose_contract. Target SPRINT {sprint}.

Read {ctx.product_spec_md} and {ctx.sprints_json}.
Write the proposed contract to BOTH:
  - {ctx.contract_md(sprint)}
  - {ctx.contract_json(sprint)}  (validates against
     {ctx.schemas_dir / 'sprint_contract.schema.json'}; >=15 testable criteria)
Set JSON status "proposed", append the token {READY_FOR_CONTRACT_REVIEW} as the final
line of the .md, then STOP. Do not build."""


def _task_build(ctx: RunContext, sprint: int, round: int) -> str:
    return f"""PHASE: build. SPRINT {sprint}. Your CWD is the isolated workspace — build here.

Read the APPROVED contract {ctx.contract_md(sprint)} + {ctx.contract_json(sprint)}.
Implement every criterion fully (no stubs). Self-evaluate against
{ctx.harness_dir / 'criteria' / 'evaluation_criteria.md'} and fill the JSON
self_evaluation (criteria_self_passed, known_gaps, app_start_command, app_url).
Set JSON status "ready_for_qa", append {READY_FOR_QA} as the final line of the contract
.md, update the workspace README, commit with git, then STOP."""


def _task_fix(ctx: RunContext, sprint: int, round: int) -> str:
    return f"""PHASE: fix_bugs. SPRINT {sprint}, QA round {round}. CWD is the workspace.

Read {ctx.qa_md(sprint)} + {ctx.qa_json(sprint)}. Fix EVERY criterion graded FAIL and
every CRITICAL/HIGH bug; address PARTIAL/MEDIUM/LOW where practical. Re-check the fixes,
update self_evaluation, append {READY_FOR_QA} to {ctx.contract_md(sprint)}, commit, STOP."""


# ── dry-run stubs (schema-valid) ────────────────────────────────────────────────
def _dry_run(ctx: RunContext, *, phase: str, sprint: int, round: int) -> AgentResult:
    if phase == "propose_contract":
        contract = {
            "sprint": sprint,
            "name": f"Sprint {sprint}",
            "features": [f"section-{sprint}-a", f"section-{sprint}-b"],
            "tech_decisions": ["Next.js App Router + TS", "Tailwind (customized)", "static export"],
            "criteria": [
                {"id": i, "description": f"Criterion {i} for sprint {sprint} is verifiable.",
                 "testable_via": ["playwright", "http", "db", "bash", "visual"][i % 5]}
                for i in range(1, 16)
            ],
            "definition_of_done": "All criteria pass and the app runs.",
            "status": "proposed",
        }
        ctx.contract_json(sprint).write_text(json.dumps(contract, indent=2), encoding="utf-8")
        ctx.contract_md(sprint).write_text(
            f"## Sprint {sprint} Contract (dry-run)\n\n15 testable criteria proposed.\n",
            encoding="utf-8",
        )
        append_signal(ctx.contract_md(sprint), READY_FOR_CONTRACT_REVIEW)
        validate_json_file(ctx, ctx.contract_json(sprint), "sprint_contract.schema.json")
        return _ok("[dry-run] contract proposed")

    if phase in ("build", "fix_bugs"):
        data = json.loads(ctx.contract_json(sprint).read_text(encoding="utf-8"))
        data["status"] = "ready_for_qa"
        data["self_evaluation"] = {
            "criteria_self_passed": 15,
            "known_gaps": [] if phase == "build" else ["fixed prior round"],
            "app_start_command": "npm run dev",
            "app_url": "http://localhost:3000",
        }
        ctx.contract_json(sprint).write_text(json.dumps(data, indent=2), encoding="utf-8")
        # make a real file change so the isolated git has something to commit
        marker = ctx.workspace_dir / f"sprint_{sprint}_build.txt"
        marker.write_text(f"sprint {sprint} {phase} round {round}\n", encoding="utf-8")
        (ctx.workspace_dir / "README.md").write_text(
            f"# Dry-run app\nLast: sprint {sprint} {phase}\nStart: npm run dev\n", encoding="utf-8"
        )
        append_signal(ctx.contract_md(sprint), READY_FOR_QA)
        git_commit(ctx, f"sprint {sprint}: {phase} (round {round}) [dry-run]")
        return _ok(f"[dry-run] {phase} done")

    raise ValueError(f"Unknown generator phase: {phase}")


def _ok(msg: str) -> AgentResult:
    return AgentResult(ok=True, text=msg, cost_usd=0.0, num_turns=0, returncode=0, raw="")
