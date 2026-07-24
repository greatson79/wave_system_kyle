#!/usr/bin/env python3
"""
Task DAG Init — task_dag_init.py

Outputs the hardcoded DAG as JSON for the orchestrator to create TaskCreate calls.
The orchestrator reads this output and creates Claude Code tasks for each step.

Usage:
    python3 task_dag_init.py --project-dir .

Output (JSON stdout):
    {
        "steps": [
            {"step_number": 1, "name": "PRD Foundation Extraction", "deps": [], "type": "sub-agent", "team": null, "human": false, "translate": true},
            ...
        ],
        "teams": {
            "prd-analysis-team": {"members": [...]},
            ...
        },
        "total_steps": 12
    }

Exit codes:
    0 — success

P1 Compliance: Pure data output — no mutations, no I/O beyond stdout.
"""

import argparse
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE


def get_dag_info(wf=None):
    """Build JSON-serializable DAG info for orchestrator consumption.

    Args:
        wf: Workflow module (None → Phase 1 default for backwards compat).
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)

    dag = wf.DAG
    teams = wf.TEAMS

    steps = []
    for step_num in sorted(dag.keys()):
        info = dag[step_num]
        step_data = {
            "step_number": step_num,
            "name": info["name"],
            "deps": info["deps"],
            "type": info["type"],
            "agent": info.get("agent"),
            "team": info["team"],
            "human": info["human"],
            "pre_script": info["pre_script"],
            "review": info["review"],
            "translate": info["translate"],
            "output": info["output"],
        }
        # Phase 2 gate_profile (absent in Phase 1)
        if "gate_profile" in info:
            step_data["gate_profile"] = info["gate_profile"]
        steps.append(step_data)

    teams_out = {}
    for team_name, team_info in teams.items():
        teams_out[team_name] = {
            "members": [
                {
                    "agent": m["agent"],
                    "task": m["task"],
                    "output": m["output"],
                }
                for m in team_info["members"]
            ]
        }

    return {
        "steps": steps,
        "teams": teams_out,
        "total_steps": wf.TOTAL_STEPS,
        "translation_steps": wf.TRANSLATION_STEPS,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Task DAG Init — output hardcoded DAG as JSON"
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
    # project_dir is accepted for interface consistency but not used
    # (DAG is hardcoded, not read from files)

    wf = get_workflow(args.workflow)
    result = get_dag_info(wf=wf)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
