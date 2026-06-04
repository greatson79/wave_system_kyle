"""Wiring tests — exercise the full orchestration loop in dry-run (no agents spawned).

Run directly:   python tests/test_harness_wiring.py
Or with pytest: pytest tests/

These validate the plumbing the advisor flagged as load-bearing: schema validity,
the dry-run loop, the QA fix-loop branch, signal tokens, and isolated-workspace git.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

import jsonschema  # noqa: E402

from config import load_config  # noqa: E402
from agents import _context as ctxmod  # noqa: E402
from agents._context import (  # noqa: E402
    READY_FOR_QA,
    SPRINT_PASSED,
    RunContext,
    has_signal,
)

RUN_ID = "_wiring_test"


def _clean(ctx: RunContext) -> None:
    if ctx.workspace_dir.exists():
        shutil.rmtree(ctx.workspace_dir, ignore_errors=True)
    for d in (ctx.plan_dir, ctx.sprints_dir, ctx.session_dir):
        for f in d.glob("*"):
            if f.name != ".gitkeep":
                f.unlink()


def test_schemas_are_valid_jsonschema() -> None:
    for name in ("product_spec", "sprint_contract", "qa_report"):
        schema = json.loads((HARNESS_DIR / "schemas" / f"{name}.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
    print("✓ all three schemas are valid JSON Schema")


def test_config_loads_and_weights_sum_to_one() -> None:
    cfg = load_config()
    weights = cfg["evaluation"]["weights"]
    assert abs(sum(weights.values()) - 1.0) < 0.01
    # fictional spec model IDs must be normalized to real ones
    assert cfg["models"]["planner"].startswith("claude-")
    print("✓ config loads, weights sum to 1.0, models normalized")


def test_dry_run_full_loop() -> None:
    import run_harness

    cfg = load_config()
    ctx = RunContext(user_prompt="x", config=cfg, run_id=RUN_ID, dry_run=True)
    ctx.ensure_dirs()
    _clean(ctx)
    try:
        rc = run_harness.run_harness(
            "A finance tracker with AI insights",
            dry_run=True, run_id=RUN_ID, config_path=None, start_sprint=1,
        )
        assert rc == 0, f"dry-run returned {rc}, expected 0 (all sprints cleared)"

        # spec produced and schema-valid
        assert ctx.sprints_json.exists()
        sprints = json.loads(ctx.sprints_json.read_text())["sprints"]
        assert 4 <= len(sprints) <= 8

        # every sprint produced a valid contract + qa report
        for s in sprints:
            n = s["number"]
            jsonschema.validate(
                json.loads(ctx.contract_json(n).read_text()),
                json.loads((HARNESS_DIR / "schemas" / "sprint_contract.schema.json").read_text()),
            )
            jsonschema.validate(
                json.loads(ctx.qa_json(n).read_text()),
                json.loads((HARNESS_DIR / "schemas" / "qa_report.schema.json").read_text()),
            )
            assert len(json.loads(ctx.contract_json(n).read_text())["criteria"]) >= 15
            assert has_signal(ctx.contract_md(n), READY_FOR_QA)
            assert has_signal(ctx.qa_md(n), SPRINT_PASSED)

        # the QA fix-loop branch was exercised: sprint 1 failed round 1, passed round 2
        sprint1_qa = json.loads(ctx.qa_json(1).read_text())
        assert sprint1_qa["round"] == 2, "sprint 1 should have needed a 2nd QA round"

        # isolated workspace got its own git repo with commits
        assert (ctx.workspace_dir / ".git").exists(), "workspace must have its own git repo"
        head = ctxmod.git_head(ctx)
        assert head, "workspace git should have commits"
        print(f"✓ dry-run loop: {len(sprints)} sprints, fix-loop exercised, isolated git @ {head}")
    finally:
        _clean(ctx)


def _main() -> int:
    failed = 0
    for fn in (test_schemas_are_valid_jsonschema, test_config_loads_and_weights_sum_to_one,
               test_dry_run_full_loop):
        try:
            fn()
        except AssertionError as exc:
            print(f"✗ {fn.__name__}: {exc}")
            failed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"✗ {fn.__name__} ERROR: {exc}")
            failed += 1
    print("\nALL WIRING TESTS PASSED" if not failed else f"\n{failed} TEST(S) FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
