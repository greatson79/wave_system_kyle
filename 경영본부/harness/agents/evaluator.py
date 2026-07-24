"""Evaluator agent — skeptical QA. Reviews contracts, tests the live app with Playwright.

Read-only on app source; its only writes are the QA report files. Returns a verdict
string the orchestrator acts on: "CONTRACT_APPROVED" | "PASS" | "FAIL".
"""
from __future__ import annotations

import json

from . import _context as ctxmod
from ._context import (
    CONTRACT_APPROVED,
    QA_COMPLETE,
    READY_FOR_QA,
    SPRINT_FAILED,
    SPRINT_PASSED,
    RunContext,
    append_signal,
    git_is_dirty,
    git_revert_working_tree,
    has_signal,
    validate_json_file,
)
from ._runtime import run_claude

SYSTEM_PROMPT = (ctxmod.HARNESS_DIR / "prompts" / "evaluator_system.md")

# Read-only on source (no Edit). Write is allowed for the report; the git-dirty backstop
# in the orchestrator reverts any source edits the evaluator makes anyway.
ALLOWED_TOOLS = ["Read", "Glob", "Grep", "Bash", "Write"]
DISALLOWED_TOOLS = ["Edit"]

# Playwright MCP allow-list. We list BOTH the server-level prefix (`mcp__playwright`, which
# Claude Code uses to allow a whole server) AND the explicit @playwright/mcp tool names, so
# QA works even if the prefix form isn't honored in a given CLI version. Unmatched names are
# simply inert. For fully hands-off QA, set evaluator_permission_mode: bypassPermissions.
_PLAYWRIGHT_TOOLS = ["mcp__playwright"] + [
    f"mcp__playwright__{t}" for t in (
        "browser_navigate", "browser_navigate_back", "browser_click", "browser_type",
        "browser_fill_form", "browser_hover", "browser_select_option", "browser_press_key",
        "browser_snapshot", "browser_take_screenshot", "browser_evaluate", "browser_wait_for",
        "browser_console_messages", "browser_network_requests", "browser_tabs",
        "browser_handle_dialog", "browser_file_upload", "browser_resize", "browser_close",
    )
]
QA_TOOLS = ALLOWED_TOOLS + _PLAYWRIGHT_TOOLS


def run_evaluator(ctx: RunContext, *, phase: str, sprint: int, round: int = 1) -> str:
    if phase == "review_contract":
        return _review_contract(ctx, sprint)
    if phase == "qa":
        return _qa(ctx, sprint, round)
    raise ValueError(f"Unknown evaluator phase: {phase}")


def _review_contract(ctx: RunContext, sprint: int) -> str:
    min_criteria = int(ctx.config["harness"].get("min_criteria_per_sprint", 15))
    if ctx.dry_run:
        data = validate_json_file(ctx, ctx.contract_json(sprint), "sprint_contract.schema.json")
        data["status"] = "approved"
        ctx.contract_json(sprint).write_text(json.dumps(data, indent=2), encoding="utf-8")
        append_signal(ctx.contract_md(sprint), CONTRACT_APPROVED)
        return CONTRACT_APPROVED

    task = f"""PHASE: review_contract. SPRINT {sprint}.
Read {ctx.contract_md(sprint)} + {ctx.contract_json(sprint)}. Enforce >= {min_criteria}
granular, testable criteria — rewrite vague ones, add edge/error/responsive/AI-e2e cases.
Update {ctx.contract_json(sprint)} (status "approved") and append {CONTRACT_APPROVED} as
the final line of the .md. Then stop."""
    res = run_claude(
        ctx,
        role="evaluator:review_contract",
        system_prompt=SYSTEM_PROMPT.read_text(encoding="utf-8"),
        task_prompt=task,
        model=ctx.config["models"]["evaluator"],
        cwd=ctx.workspace_dir,
        allowed_tools=ALLOWED_TOOLS,
        disallowed_tools=DISALLOWED_TOOLS,
        add_dirs=[ctx.artifacts_dir, ctx.schemas_dir, ctx.harness_dir / "criteria"],
        permission_mode=ctx.config["execution"].get("evaluator_permission_mode", "acceptEdits"),
    )
    ctx.record_cost(res.cost_usd)

    data = validate_json_file(ctx, ctx.contract_json(sprint), "sprint_contract.schema.json")
    if len(data["criteria"]) < min_criteria:
        raise ValueError(
            f"Sprint {sprint} contract has {len(data['criteria'])} criteria; "
            f"minimum is {min_criteria}."
        )
    if not has_signal(ctx.contract_md(sprint), CONTRACT_APPROVED):
        raise ValueError(f"Evaluator did not approve sprint {sprint} contract.")
    return CONTRACT_APPROVED


def _qa(ctx: RunContext, sprint: int, round: int) -> str:
    if ctx.dry_run:
        return _qa_dry_run(ctx, sprint, round)

    cfg_tools = ctx.config.get("tools", {})
    mcp_config = None
    if cfg_tools.get("evaluator_has_playwright"):
        mcp_config = ctx.harness_dir / cfg_tools.get("playwright_mcp_config", "config/playwright_mcp.json")

    task = f"""PHASE: qa. SPRINT {sprint}, round {round}. CWD is the workspace app.
Start the app (see {ctx.contract_md(sprint)} self_evaluation.app_start_command), drive it
LIVE with the Playwright MCP, test every contract criterion + edge cases, and grade it.
Write BOTH:
  - {ctx.qa_md(sprint)}
  - {ctx.qa_json(sprint)}  (validates against {ctx.schemas_dir / 'qa_report.schema.json'};
     set round={round})
Apply the verdict rule mechanically. Append {QA_COMPLETE} then SPRINT_PASSED or
SPRINT_FAILED as final lines of the .md. Do NOT edit app source."""
    res = run_claude(
        ctx,
        role=f"evaluator:qa:r{round}",
        system_prompt=SYSTEM_PROMPT.read_text(encoding="utf-8"),
        task_prompt=task,
        model=ctx.config["models"]["evaluator"],
        cwd=ctx.workspace_dir,
        allowed_tools=QA_TOOLS,
        disallowed_tools=DISALLOWED_TOOLS,
        add_dirs=[ctx.artifacts_dir, ctx.schemas_dir, ctx.harness_dir / "criteria"],
        mcp_config=mcp_config,
        permission_mode=ctx.config["execution"].get("evaluator_permission_mode", "acceptEdits"),
    )
    ctx.record_cost(res.cost_usd)

    # backstop: the evaluator is supposed to be read-only on source. If it dirtied the
    # tracked tree, revert so the next generator round starts from a clean committed state.
    if ctx.config["safety"].get("revert_evaluator_changes") and git_is_dirty(ctx):
        git_revert_working_tree(ctx)

    report = validate_json_file(ctx, ctx.qa_json(sprint), "qa_report.schema.json")
    return _finalize_verdict(ctx, sprint, report)


def _finalize_verdict(ctx: RunContext, sprint: int, report: dict) -> str:
    verdict = report["verdict"]
    threshold = float(ctx.config["harness"]["qa_pass_threshold"])
    # independent re-check: trust the structured data, not the agent's self-declared verdict
    has_critical = any(b.get("severity") == "CRITICAL" for b in report.get("bugs", []))
    has_fail = any(c["result"] == "FAIL" for c in report["criteria_results"])
    meets_score = report["overall_score"] >= threshold
    computed = "PASS" if (meets_score and not has_critical and not has_fail) else "FAIL"
    if computed != verdict:
        # the orchestrator trusts the mechanical re-check over the agent's label
        verdict = computed
    return verdict


def _qa_dry_run(ctx: RunContext, sprint: int, round: int) -> str:
    # Exercise the fix loop: sprint 1 fails round 1, passes round 2; all others pass.
    fail = sprint == 1 and round == 1
    contract = json.loads(ctx.contract_json(sprint).read_text(encoding="utf-8"))
    crit_ids = [c["id"] for c in contract["criteria"]]
    report = {
        "sprint": sprint,
        "round": round,
        "verdict": "FAIL" if fail else "PASS",
        "criteria_results": [
            {"id": cid, "result": ("FAIL" if (fail and cid == 1) else "PASS"),
             "notes": "dry-run"} for cid in crit_ids
        ],
        "bugs": (
            [{"id": "BUG-1", "severity": "HIGH", "criterion": 1,
              "observed": "criterion 1 not met (dry-run)", "expected": "criterion 1 met",
              "location": "src/App.tsx", "reproduction": "open app",
              "fix_guidance": "implement criterion 1"}]
            if fail else []
        ),
        "scores": {"design_quality": 5.0 if fail else 7.5, "originality": 5.0 if fail else 7.0,
                   "craft": 6.0 if fail else 8.0, "functionality": 6.0 if fail else 8.0},
        "overall_score": 5.2 if fail else 7.5,
        "next_sprint_cleared": not fail,
    }
    ctx.qa_json(sprint).write_text(json.dumps(report, indent=2), encoding="utf-8")
    ctx.qa_md(sprint).write_text(
        f"## Sprint {sprint} QA Report — Round {round}\n**Verdict:** "
        f"{report['verdict']}\n\nOverall: {report['overall_score']}\n",
        encoding="utf-8",
    )
    append_signal(ctx.qa_md(sprint), QA_COMPLETE)
    append_signal(ctx.qa_md(sprint), SPRINT_PASSED if not fail else SPRINT_FAILED)
    validate_json_file(ctx, ctx.qa_json(sprint), "qa_report.schema.json")
    return _finalize_verdict(ctx, sprint, report)
