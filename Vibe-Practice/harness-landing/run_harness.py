#!/usr/bin/env python3
"""Harness Orchestrator — three-agent (Planner/Generator/Evaluator) build loop.

Usage:
    python run_harness.py "Your 1-4 sentence app idea"
    python run_harness.py "..." --dry-run          # exercise the loop, spawn no agents
    python run_harness.py --check                   # cheap real wiring probe (~1 cent)
    python run_harness.py "..." --run-id finance    # name the workspace/run

Inter-agent communication is file-only (artifacts/). The generated app is built in an
ISOLATED workspace (harness/workspace/<run-id>/) with its own git repo — never the
parent monorepo. See HARNESS_README.md.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))

from config import load_config  # noqa: E402
from agents._context import (  # noqa: E402
    HARNESS_COMPLETE,
    RunContext,
    git_head,
    init_workspace_git,
    load_sprints,
    slugify,
)
from agents._runtime import wiring_probe, wiring_probe_full_posture  # noqa: E402
from agents.evaluator import run_evaluator  # noqa: E402
from agents.generator import run_generator  # noqa: E402
from agents.planner import run_planner  # noqa: E402


def _hr(title: str) -> None:
    print(f"\n━━━ {title} ━━━", flush=True)


def write_handoff(ctx: RunContext, *, last_sprint: int, current_sprint: int,
                  state: str, issues: str, next_steps: str, start_cmd: str) -> None:
    ctx.handoff_md.write_text(
        "## Session Handoff\n"
        f"**Run ID:** {ctx.run_id}\n"
        f"**Last Sprint Completed:** {last_sprint}\n"
        f"**Current Sprint:** {current_sprint}\n"
        f"**App State:** {state}\n"
        f"**Known Issues:** {issues}\n"
        f"**Next Steps:** {next_steps}\n"
        f"**Git Commit:** {git_head(ctx) or '(none)'}\n"
        f"**Workspace:** {ctx.workspace_dir}\n"
        f"**How to Start App:** {start_cmd}\n",
        encoding="utf-8",
    )


def run_sprint(ctx: RunContext, sprint_num: int, total: int) -> bool:
    """Run one sprint end-to-end. Returns True if it cleared QA."""
    max_rounds = int(ctx.config["harness"]["max_qa_rounds"])

    _hr(f"SPRINT {sprint_num}/{total}: contract negotiation")
    res = run_generator(ctx, phase="propose_contract", sprint=sprint_num)
    ctx.record_cost(res.cost_usd)
    run_evaluator(ctx, phase="review_contract", sprint=sprint_num)

    _hr(f"SPRINT {sprint_num}/{total}: building")
    res = run_generator(ctx, phase="build", sprint=sprint_num)
    ctx.record_cost(res.cost_usd)

    passed = False
    for qa_round in range(1, max_rounds + 1):
        print(f"  [sprint {sprint_num}] QA round {qa_round}/{max_rounds}...", flush=True)
        verdict = run_evaluator(ctx, phase="qa", sprint=sprint_num, round=qa_round)
        if verdict == "PASS":
            print(f"  [sprint {sprint_num}] ✓ PASSED QA (round {qa_round})", flush=True)
            passed = True
            break
        print(f"  [sprint {sprint_num}] ✗ FAILED QA — generator fixing bugs...", flush=True)
        res = run_generator(ctx, phase="fix_bugs", sprint=sprint_num, round=qa_round)
        ctx.record_cost(res.cost_usd)

    write_handoff(
        ctx,
        last_sprint=sprint_num if passed else sprint_num - 1,
        current_sprint=sprint_num + 1 if passed else sprint_num,
        state=f"sprint {sprint_num} {'passed' if passed else 'NOT cleared after max QA rounds'}",
        issues="see latest qa_report" if not passed else "none blocking",
        next_steps=f"start sprint {sprint_num + 1}" if passed else f"manually inspect sprint {sprint_num}",
        start_cmd="see workspace README.md",
    )
    return passed


def run_harness(user_prompt: str, *, dry_run: bool, run_id: str | None,
                config_path: str | None, start_sprint: int) -> int:
    config = load_config(config_path)
    rid = run_id or slugify(user_prompt)
    ctx = RunContext(user_prompt=user_prompt, config=config, run_id=rid, dry_run=dry_run)
    ctx.ensure_dirs()

    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Harness run '{rid}' [{mode}]  workspace={ctx.workspace_dir}")

    _hr("PHASE 1: PLANNING")
    res = run_planner(ctx, user_prompt)
    ctx.record_cost(res.cost_usd)
    init_workspace_git(ctx)

    sprints = load_sprints(ctx)
    max_sprints = int(config["harness"]["max_sprints"])
    sprints = [s for s in sprints if s["number"] <= max_sprints and s["number"] >= start_sprint]
    total = len(sprints)
    print(f"  planned {total} sprint(s): {[s['number'] for s in sprints]}")

    results: dict[int, bool] = {}
    for s in sprints:
        n = s["number"]
        try:
            results[n] = run_sprint(ctx, n, total)
        except Exception as exc:  # noqa: BLE001 — surface, don't swallow, then stop the loop
            print(f"\n‼ Sprint {n} aborted: {exc}", file=sys.stderr)
            traceback.print_exc()
            results[n] = False
            break
        if not results[n]:
            print(f"\n‼ Sprint {n} did not clear QA within "
                  f"{config['harness']['max_qa_rounds']} rounds. Stopping.", file=sys.stderr)
            break

    _hr("HARNESS COMPLETE")
    print_summary(ctx, results, total)
    ctx.handoff_md.write_text(
        ctx.handoff_md.read_text(encoding="utf-8") + f"\n{HARNESS_COMPLETE}\n"
        if ctx.handoff_md.exists() else f"{HARNESS_COMPLETE}\n",
        encoding="utf-8",
    )
    return 0 if all(results.values()) and results else 1


def print_summary(ctx: RunContext, results: dict[int, bool], total: int) -> None:
    for n in sorted(results):
        print(f"  Sprint {n}: {'✓ PASSED' if results[n] else '✗ FAILED'}")
    cleared = sum(1 for v in results.values() if v)
    print(f"  Cleared {cleared}/{total} sprints")
    if not ctx.dry_run:
        print(f"  Total agent cost: ${ctx.total_cost:.4f}")
    print(f"  Workspace: {ctx.workspace_dir}")
    print(f"  Artifacts: {ctx.artifacts_dir}")


def main() -> int:
    p = argparse.ArgumentParser(description="Three-agent harness orchestrator")
    p.add_argument("prompt", nargs="?", help="1-4 sentence app idea")
    p.add_argument("--dry-run", action="store_true",
                   help="exercise the full loop without spawning real agents")
    p.add_argument("--check", action="store_true",
                   help="cheap real wiring probe (one haiku call) then exit")
    p.add_argument("--run-id", help="name the run/workspace (default: slug of prompt)")
    p.add_argument("--config", help="path to harness_config.yaml")
    p.add_argument("--start-sprint", type=int, default=1, help="resume from sprint N")
    args = p.parse_args()

    if args.check:
        cfg = load_config(args.config)
        ctx = RunContext(user_prompt="probe", config=cfg, run_id="_probe")
        ctx.ensure_dirs()
        print("Probe 1/2: minimal call (auth + subprocess)...", flush=True)
        res1 = wiring_probe(ctx)
        ok1 = res1.ok and "WIRING_OK" in res1.text
        print(f"  rc={res1.returncode} cost=${res1.cost_usd:.4f} out={res1.text[:80]!r}")

        print("Probe 2/2: production flag stack (variadic --allowedTools, --add-dir, "
              "acceptEdits) + scoped tool fires...", flush=True)
        res2 = wiring_probe_full_posture(ctx)
        ok2 = res2.ok and "PROBE_DONE" in res2.text
        print(f"  rc={res2.returncode} cost=${res2.cost_usd:.4f} out={res2.text[:80]!r}")

        ok = ok1 and ok2
        print("✓ WIRING OK — both probes passed"
              if ok else "✗ WIRING FAILED — check `claude` auth, PATH, and flag parsing")
        return 0 if ok else 1

    if not args.prompt:
        p.error("a prompt is required (or use --check)")
    return run_harness(
        args.prompt,
        dry_run=args.dry_run,
        run_id=args.run_id,
        config_path=args.config,
        start_sprint=args.start_sprint,
    )


if __name__ == "__main__":
    raise SystemExit(main())
