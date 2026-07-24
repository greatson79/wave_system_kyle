#!/usr/bin/env python3
"""
SOT Manager — sot_manager.py

The ONLY authorized write path for the workflow SOT file (state.yaml).
All other write paths are blocked by:
  - validate_sot_write.py (PreToolUse Write → exit 2)
  - block_destructive_commands.py (Bash redirect patterns)
  - Architectural invariant (Hooks = SOT read-only)

Architecture:
  - Reads current SOT via PyYAML
  - Modifies in-memory dict
  - Validates via validate_sot_schema() BEFORE writing
  - Writes via atomic_write() (temp file → rename)
  - JSON output to stdout for orchestrator consumption

Usage:
    python3 sot_manager.py --project-dir . --init
    python3 sot_manager.py --project-dir . --update-step 3 --output path/to/file.md
    python3 sot_manager.py --project-dir . --set-status running
    python3 sot_manager.py --project-dir . --add-translation 3 path/to/file.ko.md
    python3 sot_manager.py --project-dir . --set-team prd-analysis-team --team-status partial
    python3 sot_manager.py --project-dir . --add-team-result task-id path/to/output.md
    python3 sot_manager.py --project-dir . --finalize-team
    python3 sot_manager.py --project-dir . --update-pacs 3 --pacs-score 85 --weak-dim F

Exit codes:
    0 — success
    1 — validation failure or argument error
    2 — file I/O error

P1 Compliance: All mutations are deterministic (dict update + schema validation).
SOT Compliance: This is the SINGLE authorized SOT writer.
"""

import argparse
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _context_lib import (
    SOT_FILENAMES,
    sot_paths,
    validate_sot_schema,
    atomic_write,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_STATUSES = {"running", "completed", "error", "paused"}
VALID_TEAM_STATUSES = {"partial", "all_completed"}
VALID_WEAK_DIMS = {"F", "C", "L", "T"}  # T = Testability (Phase 2 code steps)

# Initial SOT templates — created by --init, selected by --workflow flag
_INITIAL_SOT_PHASE1 = {
    "workflow": {
        "name": "SaaS Auto-Builder PRD Generation",
        "current_step": 0,
        "status": "running",
        "total_steps": 12,
        "autopilot": {
            "enabled": False,
            "activated_at": "",
            "auto_approved_steps": [],
        },
        "outputs": {},
        "pacs": {
            "dimensions": {"F": 0, "C": 0, "L": 0},
            "current_step_score": 0,
            "weak_dimension": "",
            "history": {},
            "pre_mortem_flag": "",
        },
        "parent_genome": {
            "source": "AgenticWorkflow",
            "version": "2026-03-13",
        },
    }
}

_INITIAL_SOT_PHASE2 = {
    "workflow": {
        "name": "Full-Stack SaaS Auto-Builder Development",
        "current_step": 0,
        "status": "running",
        "total_steps": 16,
        "autopilot": {
            "enabled": False,
            "activated_at": "",
            "auto_approved_steps": [],
        },
        "outputs": {},
        "pacs": {
            "dimensions": {"F": 0, "C": 0, "L": 0, "T": 0},
            "current_step_score": 0,
            "weak_dimension": "",
            "history": {},
            "pre_mortem_flag": "",
        },
        "parent_genome": {
            "source": "AgenticWorkflow",
            "version": "2026-03-13",
            "inherited_dna": [
                "absolute-criteria", "sot-pattern", "4-phase-structure",
                "5-layer-qa", "safety-hooks", "adversarial-review",
                "decision-log", "context-preservation", "ccp-strong",
                "pacs-code-4d",
            ],
        },
    }
}

# Default for backwards compatibility
INITIAL_SOT = _INITIAL_SOT_PHASE1

def _get_initial_sot(workflow_phase=None):
    """Get the initial SOT template for the specified workflow phase."""
    if workflow_phase == "phase2":
        import copy
        return copy.deepcopy(_INITIAL_SOT_PHASE2)
    import copy
    return copy.deepcopy(_INITIAL_SOT_PHASE1)


# ---------------------------------------------------------------------------
# SOT I/O
# ---------------------------------------------------------------------------
def _find_sot(project_dir):
    """Find and parse the SOT file. Returns (data, path) or raises."""
    import yaml

    for sot_path in sot_paths(project_dir):
        if os.path.exists(sot_path):
            with open(sot_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data is None:
                data = {}
            if not isinstance(data, dict):
                raise ValueError(f"SOT {sot_path} is not a dict")
            return data, sot_path

    raise FileNotFoundError(
        f"No SOT file found. Expected one of: "
        f"{', '.join(SOT_FILENAMES)} in {project_dir}/.claude/"
    )


def _get_workflow(data):
    """Extract the workflow section from SOT data. Creates if missing."""
    if "workflow" not in data:
        data["workflow"] = {}
    wf = data["workflow"]
    if not isinstance(wf, dict):
        data["workflow"] = {}
        wf = data["workflow"]
    return wf


def _write_sot(data, sot_path):
    """Validate schema and write SOT atomically.

    Converts SOT data to the flat format expected by validate_sot_schema()
    (read_autopilot_state() output shape), validates, then writes YAML.
    """
    import yaml

    wf = data.get("workflow", {})

    # Build the flat dict that validate_sot_schema() expects
    ap_state = {
        "enabled": wf.get("autopilot", {}).get("enabled", False),
        "current_step": wf.get("current_step", 0),
        "workflow_status": wf.get("status", ""),
        "outputs": wf.get("outputs", {}),
        "auto_approved_steps": wf.get("autopilot", {}).get(
            "auto_approved_steps", []
        ),
        "pacs": wf.get("pacs"),
    }

    # Include active_team if present
    if "active_team" in wf:
        ap_state["active_team"] = wf["active_team"]

    # Validate before writing — all schema warnings are fatal.
    # validate_sot_schema() only reports structural violations (S1-S7),
    # so every warning indicates a write that would corrupt the SOT.
    warnings = validate_sot_schema(ap_state)
    if warnings:
        return False, warnings

    # Write atomically
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    atomic_write(sot_path, content)

    return True, warnings


def _result(success, warnings=None, extra=None):
    """Build JSON result dict."""
    out = {"success": success, "warnings": warnings or []}
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_init(project_dir, workflow_phase=None):
    """Create initial SOT file.

    Args:
        project_dir: Project root directory.
        workflow_phase: "phase1" (default) or "phase2".
    """
    import yaml

    sot_path = os.path.join(project_dir, ".claude", "state.yaml")

    if os.path.exists(sot_path):
        return _result(False, ["SOT file already exists: " + sot_path])

    initial = _get_initial_sot(workflow_phase)

    os.makedirs(os.path.dirname(sot_path), exist_ok=True)
    content = yaml.dump(
        initial, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    atomic_write(sot_path, content)
    return _result(True, extra={
        "action": "init",
        "path": sot_path,
        "workflow": workflow_phase or "phase1",
    })


def cmd_update_step(project_dir, step, output_path):
    """Record step output and advance current_step atomically (S4 compliance)."""
    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    # Ensure outputs dict exists
    if "outputs" not in wf or not isinstance(wf.get("outputs"), dict):
        wf["outputs"] = {}

    step_key = f"step-{step}"
    wf["outputs"][step_key] = output_path
    wf["current_step"] = step  # S4 atomicity: output + current_step in same write

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "update_step", "step": step, "output": output_path})


def cmd_set_status(project_dir, status):
    """Set workflow status."""
    if status not in VALID_STATUSES:
        return _result(False, [
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        ])

    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)
    wf["status"] = status

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "set_status", "status": status})


def cmd_add_translation(project_dir, step, ko_path):
    """Record translation output path for a step."""
    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    if "outputs" not in wf or not isinstance(wf.get("outputs"), dict):
        wf["outputs"] = {}

    ko_key = f"step-{step}-ko"
    wf["outputs"][ko_key] = ko_path

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "add_translation", "step": step, "ko_path": ko_path})


def cmd_set_team(project_dir, team_name, team_status):
    """Set or update active_team in SOT."""
    if team_status not in VALID_TEAM_STATUSES:
        return _result(False, [
            f"Invalid team status '{team_status}'. "
            f"Must be one of: {', '.join(sorted(VALID_TEAM_STATUSES))}"
        ])

    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    if "active_team" not in wf:
        wf["active_team"] = {
            "name": team_name,
            "status": team_status,
            "tasks_completed": [],
            "tasks_pending": [],
            "completed_summaries": {},
        }
    else:
        wf["active_team"]["name"] = team_name
        wf["active_team"]["status"] = team_status

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "set_team", "team": team_name, "status": team_status})


def cmd_add_team_result(project_dir, task_id, output_path):
    """Record a completed team task result."""
    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    at = wf.get("active_team")
    if not at or not isinstance(at, dict):
        return _result(False, ["No active_team in SOT — call --set-team first"])

    # Move from pending to completed
    pending = at.get("tasks_pending", [])
    completed = at.get("tasks_completed", [])
    if task_id in pending:
        pending.remove(task_id)
    if task_id not in completed:
        completed.append(task_id)
    at["tasks_pending"] = pending
    at["tasks_completed"] = completed

    # Record summary
    if "completed_summaries" not in at:
        at["completed_summaries"] = {}
    at["completed_summaries"][task_id] = {
        "output_path": output_path,
    }

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "add_team_result", "task_id": task_id})


def cmd_finalize_team(project_dir):
    """Move active_team to completed_teams and remove active_team."""
    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    at = wf.get("active_team")
    if not at or not isinstance(at, dict):
        return _result(False, ["No active_team in SOT to finalize"])

    at["status"] = "all_completed"

    # Move to completed_teams list
    if "completed_teams" not in wf:
        wf["completed_teams"] = []
    wf["completed_teams"].append(at.copy())

    # Remove active_team
    del wf["active_team"]

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "finalize_team", "team": at.get("name", "unknown")})


def cmd_update_pacs(project_dir, step, score, weak_dim):
    """Update pACS score for a step."""
    if not (0 <= score <= 100):
        return _result(False, [f"pACS score {score} out of range (0-100)"])
    if weak_dim and weak_dim not in VALID_WEAK_DIMS:
        return _result(False, [
            f"Invalid weak_dimension '{weak_dim}'. Must be one of: {', '.join(sorted(VALID_WEAK_DIMS))}"
        ])

    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    if "pacs" not in wf:
        wf["pacs"] = {
            "dimensions": {"F": 0, "C": 0, "L": 0},
            "current_step_score": 0,
            "weak_dimension": "",
            "history": {},
            "pre_mortem_flag": "",
        }

    pacs = wf["pacs"]
    pacs["current_step_score"] = score
    if weak_dim:
        pacs["weak_dimension"] = weak_dim

    # Record in history
    if "history" not in pacs:
        pacs["history"] = {}
    step_key = f"step-{step}"
    pacs["history"][step_key] = {"score": score, "weak": weak_dim or ""}

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "update_pacs", "step": step, "score": score})


def cmd_set_autopilot(project_dir, enabled):
    """Set workflow.autopilot.enabled in SOT.

    Args:
        project_dir: Project root directory.
        enabled: True to enable autopilot, False to disable.
    """
    data, sot_path = _find_sot(project_dir)
    wf = _get_workflow(data)

    if "autopilot" not in wf or not isinstance(wf.get("autopilot"), dict):
        wf["autopilot"] = {
            "enabled": False,
            "activated_at": "",
            "auto_approved_steps": [],
        }

    wf["autopilot"]["enabled"] = enabled
    if enabled:
        from datetime import datetime
        wf["autopilot"]["activated_at"] = datetime.now().isoformat()

    ok, warnings = _write_sot(data, sot_path)
    return _result(ok, warnings, {"action": "set_autopilot", "enabled": enabled})


def cmd_reset(project_dir, workflow_phase=None):
    """Backup existing SOT and create a fresh one.

    Safe alternative to `rm .claude/state.yaml` — maintains the single-write-path
    principle (절대 기준 2). Existing SOT is preserved as .bak for recovery.

    Args:
        project_dir: Project root directory.
        workflow_phase: "phase1" (default) or "phase2".
    """
    import yaml
    import shutil

    sot_path = os.path.join(project_dir, ".claude", "state.yaml")

    backup_path = None
    if os.path.exists(sot_path):
        backup_path = sot_path + ".bak"
        try:
            shutil.copy2(sot_path, backup_path)
        except Exception as e:
            return _result(False, [f"Cannot backup SOT: {e}"])

        # Remove existing SOT so cmd_init can create fresh
        try:
            os.remove(sot_path)
        except Exception as e:
            return _result(False, [f"Cannot remove old SOT: {e}"])

    # Create fresh SOT
    init_result = cmd_init(project_dir, workflow_phase=workflow_phase)
    if not init_result["success"]:
        # Restore backup if init failed
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, sot_path)
        return init_result

    init_result["action"] = "reset"
    if backup_path:
        init_result["backup"] = backup_path

    return init_result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="SOT Manager — single authorized write path for state.yaml"
    )
    parser.add_argument(
        "--project-dir", type=str, default=".",
        help="Project root directory (default: current directory)"
    )

    # Mutually exclusive commands
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Create initial SOT file")
    group.add_argument("--update-step", type=int, metavar="N", help="Record step output and advance current_step")
    group.add_argument("--set-status", type=str, metavar="STATUS", help="Set workflow status")
    group.add_argument("--add-translation", type=int, metavar="STEP", help="Record translation output")
    group.add_argument("--set-team", type=str, metavar="TEAM_NAME", help="Set or update active_team")
    group.add_argument("--add-team-result", type=str, metavar="TASK_ID", help="Record completed team task")
    group.add_argument("--finalize-team", action="store_true", help="Move active_team to completed_teams")
    group.add_argument("--update-pacs", type=int, metavar="STEP", help="Update pACS score for a step")
    group.add_argument("--set-autopilot", type=str, metavar="BOOL",
                        help="Set autopilot mode (true/false)")
    group.add_argument("--reset", action="store_true",
                        help="Backup existing SOT and create fresh (safe restart)")

    # Command-specific arguments
    parser.add_argument("--output", type=str, help="Output file path (for --update-step, --add-team-result)")
    parser.add_argument("--ko-path", type=str, help="Korean translation file path (for --add-translation)")
    parser.add_argument("--team-status", type=str, default="partial", help="Team status (for --set-team)")
    parser.add_argument("--pacs-score", type=int, help="pACS score 0-100 (for --update-pacs)")
    parser.add_argument("--weak-dim", type=str, default="", help="Weak dimension F/C/L/T (for --update-pacs)")
    parser.add_argument("--workflow", type=str, default=None, choices=["phase1", "phase2"],
                        help="Workflow phase (for --init). Default: phase1")

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)

    try:
        if args.init:
            result = cmd_init(project_dir, workflow_phase=args.workflow)
        elif args.update_step is not None:
            if not args.output:
                result = _result(False, ["--output is required with --update-step"])
            else:
                result = cmd_update_step(project_dir, args.update_step, args.output)
        elif args.set_status:
            result = cmd_set_status(project_dir, args.set_status)
        elif args.add_translation is not None:
            ko = args.ko_path or args.output
            if not ko:
                result = _result(False, ["--ko-path or --output is required with --add-translation"])
            else:
                result = cmd_add_translation(project_dir, args.add_translation, ko)
        elif args.set_team:
            result = cmd_set_team(project_dir, args.set_team, args.team_status)
        elif args.add_team_result:
            if not args.output:
                result = _result(False, ["--output is required with --add-team-result"])
            else:
                result = cmd_add_team_result(project_dir, args.add_team_result, args.output)
        elif args.finalize_team:
            result = cmd_finalize_team(project_dir)
        elif args.update_pacs is not None:
            if args.pacs_score is None:
                result = _result(False, ["--pacs-score is required with --update-pacs"])
            else:
                result = cmd_update_pacs(project_dir, args.update_pacs, args.pacs_score, args.weak_dim)
        elif args.set_autopilot is not None:
            enabled = args.set_autopilot.lower() in ("true", "1", "yes", "on")
            result = cmd_set_autopilot(project_dir, enabled)
        elif args.reset:
            result = cmd_reset(project_dir, workflow_phase=args.workflow)
        else:
            result = _result(False, ["No command specified"])

    except FileNotFoundError as e:
        result = _result(False, [str(e)])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(2)
    except Exception as e:
        result = _result(False, [f"Fatal error: {type(e).__name__}: {e}"])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
