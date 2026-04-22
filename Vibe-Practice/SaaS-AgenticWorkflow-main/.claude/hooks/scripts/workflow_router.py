#!/usr/bin/env python3
"""
Workflow Router — workflow_router.py

Determines the next executable step(s) based on DAG dependencies and SOT state.
Given the current step, checks which successor steps have all dependencies satisfied
(i.e., all prerequisite step outputs exist in SOT).

Usage:
    python3 workflow_router.py --current-step N --project-dir .

Output (JSON stdout):
    {"next_steps": [5, 6], "human_checkpoint": false, "reason": "deps satisfied"}
    {"next_steps": [4], "human_checkpoint": true, "reason": "human review required"}
    {"next_steps": [], "reason": "workflow complete"}

Exit codes:
    0 — success
    1 — argument error or invalid step

P1 Compliance: Deterministic — DAG lookup + SOT output existence check.
SOT Compliance: Read-only access via _read_sot_outputs().
"""

import argparse
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE
from _context_lib import _read_sot_outputs, sot_paths


def _get_completed_steps(project_dir):
    """Get set of step numbers that have outputs in SOT.

    Returns set of ints for steps whose output files are registered in SOT.
    Human steps (4, 8) are considered "complete" if their predecessors'
    outputs exist AND the step number <= current_step in SOT.
    """
    outputs = _read_sot_outputs(project_dir)
    completed = set()
    for key in outputs:
        # Parse "step-N" keys (ignore "step-N-ko" translation keys)
        if key.startswith("step-") and not key.endswith("-ko"):
            try:
                step_num = int(key.split("-")[1])
                completed.add(step_num)
            except (IndexError, ValueError):
                continue
    return completed


def _get_current_step(project_dir):
    """Read current_step from SOT. Returns int or 0."""
    import yaml

    for sot_path in sot_paths(project_dir):
        if os.path.exists(sot_path):
            try:
                with open(sot_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    wf = data.get("workflow", {})
                    return int(wf.get("current_step", 0))
            except Exception:
                continue
    return 0


def find_next_steps(completed_step, project_dir, wf=None):
    """Find all steps that become executable after completed_step.

    Args:
        completed_step: The step number just completed (or 0 for initial).
        project_dir: Project root directory.
        wf: Workflow module (None → Phase 1 default for backwards compat).

    Returns:
        dict with keys: next_steps (list[int]), human_checkpoint (bool), reason (str)
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)

    dag = wf.DAG
    total_steps = wf.TOTAL_STEPS

    if completed_step < 0 or completed_step > total_steps:
        return {
            "next_steps": [],
            "human_checkpoint": False,
            "reason": f"Invalid step {completed_step}. Must be 0-{total_steps}.",
        }

    # Step 0 = workflow not started, step 1 is always first
    if completed_step == 0:
        step_info = dag[1]
        return {
            "next_steps": [1],
            "human_checkpoint": step_info["human"],
            "reason": "Workflow start — step 1 has no dependencies.",
        }

    # Check if workflow is complete
    if completed_step >= total_steps:
        return {
            "next_steps": [],
            "human_checkpoint": False,
            "reason": f"Workflow complete — all {total_steps} steps done.",
        }

    # Get completed steps from SOT
    completed = _get_completed_steps(project_dir)
    # Add the just-completed step (it may not be in SOT yet)
    completed.add(completed_step)
    # Human steps count as "complete" if current_step has passed them
    sot_current = _get_current_step(project_dir)
    for s in dag:
        if dag[s]["human"] and s <= sot_current:
            completed.add(s)

    # Find successor steps whose ALL deps are satisfied
    next_steps = []
    for step_num, step_info in dag.items():
        if step_num in completed:
            continue  # Already done
        deps = step_info["deps"]
        if not deps:
            continue  # Step 1 has no deps, handled above
        if all(d in completed for d in deps):
            next_steps.append(step_num)

    next_steps.sort()

    if not next_steps:
        return {
            "next_steps": [],
            "human_checkpoint": False,
            "reason": "No steps with satisfied dependencies found.",
        }

    # Check if any next step is a human checkpoint
    is_human = any(dag[s]["human"] for s in next_steps)

    return {
        "next_steps": next_steps,
        "human_checkpoint": is_human,
        "reason": "Dependencies satisfied."
        + (" Human checkpoint required." if is_human else ""),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Workflow Router — DAG-based step routing"
    )
    parser.add_argument(
        "--current-step",
        type=int,
        required=True,
        help="The step number just completed (0 = not started)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--workflow",
        type=str,
        default=DEFAULT_PHASE,
        choices=sorted(VALID_PHASES),
        help=f"Workflow phase (default: {DEFAULT_PHASE})",
    )

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)
    wf = get_workflow(args.workflow)

    result = find_next_steps(args.current_step, project_dir, wf=wf)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
