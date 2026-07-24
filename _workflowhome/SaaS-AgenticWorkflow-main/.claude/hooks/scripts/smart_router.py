#!/usr/bin/env python3
"""
Smart Router — smart_router.py

Detects project state and determines available execution modes.
Called by the /start slash command to present options to the user.

Usage:
    python3 .claude/hooks/scripts/smart_router.py --project-dir .

Output (JSON stdout):
    {
        "project_state": "fresh|running|paused|error|completed",
        "active_phase": null|"phase1"|"phase2",
        "current_step": 0,
        "total_steps": 12,
        "workflow_name": "...",
        "available_modes": [
            {
                "id": "phase1-fresh",
                "label": "Phase 1: PRD 생성 (12-step)",
                "description": "...",
                "command": "/run-workflow",
                "enabled": true
            }
        ],
        "settings": {
            "autopilot": false,
            "ulw": false
        },
        "prerequisites": {
            "python_ok": true,
            "python_version": "3.11",
            "pyyaml_ok": true
        },
        "resume_info": null|{
            "phase": "phase1",
            "step": 5,
            "step_name": "PRD Document Architecture Design",
            "status": "running",
            "pacs_avg": 82,
            "completed_count": 4
        }
    }

Exit codes:
    0 — success (always — errors are reported in JSON)

P1 Compliance: Deterministic — file existence + YAML parsing + set logic.
SOT Compliance: Read-only — never modifies SOT.
"""

import argparse
import importlib.util
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _context_lib import SOT_FILENAMES, sot_paths


# ---------------------------------------------------------------------------
# Prerequisites Check
# ---------------------------------------------------------------------------
def _check_prerequisites():
    """Check Python version and PyYAML availability."""
    major, minor = sys.version_info[:2]
    python_ok = major >= 3 and minor >= 9

    pyyaml_spec = importlib.util.find_spec("yaml")
    pyyaml_ok = pyyaml_spec is not None

    return {
        "python_ok": python_ok,
        "python_version": f"{major}.{minor}",
        "pyyaml_ok": pyyaml_ok,
    }


# ---------------------------------------------------------------------------
# SOT State Detection (Read-Only)
# Uses _context_lib.py:SOT_FILENAMES + sot_paths() — single definition (A-3).
# ---------------------------------------------------------------------------


def _find_sot(project_dir):
    """Find and parse SOT file. Returns (data, path) or (None, None).

    SOT Compliance: Read-only access.
    Uses sot_paths() from _context_lib.py for path consistency (A-3).
    """
    for sot_path in sot_paths(project_dir):
        if os.path.exists(sot_path):
            try:
                import yaml

                with open(sot_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data, sot_path
            except ImportError:
                # PyYAML not available — try regex fallback for basic fields
                return _parse_sot_regex(sot_path)
            except Exception:
                continue
    return None, None


def _parse_sot_regex(sot_path):
    """Minimal regex fallback when PyYAML is unavailable.

    Extracts only essential fields for routing decisions.
    """
    import re

    try:
        with open(sot_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None, None

    data = {"workflow": {}}
    wf = data["workflow"]

    # Extract workflow name
    m = re.search(r"name:\s*(.+)", content)
    if m:
        wf["name"] = m.group(1).strip().strip("'\"")

    # Extract current_step
    m = re.search(r"current_step:\s*(\d+)", content)
    if m:
        wf["current_step"] = int(m.group(1))

    # Extract status
    m = re.search(r"status:\s*(\w+)", content)
    if m:
        wf["status"] = m.group(1)

    # Extract total_steps
    m = re.search(r"total_steps:\s*(\d+)", content)
    if m:
        wf["total_steps"] = int(m.group(1))

    # Extract autopilot enabled
    m = re.search(r"enabled:\s*(true|false)", content, re.IGNORECASE)
    if m:
        wf["autopilot"] = {"enabled": m.group(1).lower() == "true"}

    return data, sot_path


def _detect_phase(wf_data):
    """Detect active phase from SOT workflow data.

    Returns "phase1", "phase2", or None.

    D-7: Must stay consistent with _workflow_registry.detect_phase_from_sot().
    This function operates on an already-parsed dict (avoids re-reading the file),
    while detect_phase_from_sot() reads the file itself. Same heuristic logic,
    plus total_steps as an additional signal.
    """
    wf_name = wf_data.get("name", "")
    total = wf_data.get("total_steps", 0)

    # Phase 2 detection: name contains "fullstack" or "development", or total_steps=16
    if total == 16:
        return "phase2"
    name_lower = wf_name.lower()
    if "fullstack" in name_lower or "development" in name_lower:
        return "phase2"

    # Phase 1 detection: name contains "PRD" or total_steps=12
    if total == 12:
        return "phase1"
    if "prd" in name_lower:
        return "phase1"

    return None


def _build_resume_info(wf_data, phase):
    """Build resume information from SOT data."""
    current_step = wf_data.get("current_step", 0)
    status = wf_data.get("status", "unknown")
    total_steps = wf_data.get("total_steps", 0)

    # Count completed steps from outputs
    outputs = wf_data.get("outputs", {})
    completed_count = sum(
        1
        for k in outputs
        if k.startswith("step-") and not k.endswith("-ko")
    )

    # Get step name from DAG
    step_name = ""
    try:
        from _workflow_registry import get_workflow

        wf_module = get_workflow(phase)
        dag = wf_module.DAG
        next_step = current_step + 1
        if next_step in dag:
            step_name = dag[next_step].get("name", "")
        elif current_step in dag:
            step_name = dag[current_step].get("name", "")
    except Exception:
        pass

    # Calculate average pACS from history
    pacs = wf_data.get("pacs", {})
    history = pacs.get("history", {})
    pacs_avg = 0
    if history:
        scores = [
            v.get("score", 0) for v in history.values() if isinstance(v, dict)
        ]
        if scores:
            pacs_avg = sum(scores) // len(scores)

    # Active team info
    active_team = wf_data.get("active_team")
    team_info = None
    if active_team and isinstance(active_team, dict):
        team_info = {
            "name": active_team.get("name", ""),
            "status": active_team.get("status", ""),
            "completed": len(active_team.get("tasks_completed", [])),
            "pending": len(active_team.get("tasks_pending", [])),
        }

    return {
        "phase": phase,
        "step": current_step,
        "next_step": min(current_step + 1, total_steps),
        "next_step_name": step_name,
        "status": status,
        "total_steps": total_steps,
        "completed_count": completed_count,
        "pacs_avg": pacs_avg,
        "active_team": team_info,
    }


# ---------------------------------------------------------------------------
# Mode Determination
# ---------------------------------------------------------------------------

# Mode definitions — the complete catalog of execution modes
_MODE_PHASE1_FRESH = {
    "id": "phase1-fresh",
    "label": "Phase 1: PRD 생성 — 새로 시작",
    "label_en": "Phase 1: PRD Generation — Fresh Start",
    "description": "12단계 워크플로우로 SaaS Auto-Builder PRD 문서를 생성합니다. "
    "Research → Planning → Implementation 3단계 구조.",
    "command": "/run-workflow",
    "init_command": "python3 .claude/hooks/scripts/sot_manager.py --project-dir . --init --workflow phase1",
    "phase": "phase1",
    "enabled": True,
}

_MODE_PHASE1_RESUME = {
    "id": "phase1-resume",
    "label": "Phase 1: PRD 생성 — 이어서 진행",
    "label_en": "Phase 1: PRD Generation — Resume",
    "description": "이전에 중단된 Phase 1 워크플로우를 이어서 진행합니다.",
    "command": "/run-workflow",
    "phase": "phase1",
    "enabled": True,
}

_MODE_PHASE2_FRESH = {
    "id": "phase2-fresh",
    "label": "Phase 2: 풀스택 개발 — 새로 시작",
    "label_en": "Phase 2: Full-Stack Development — Fresh Start",
    "description": "16단계 워크플로우로 SaaS Auto-Builder를 풀스택 구현합니다. "
    "Phase 1 PRD를 기반으로 실제 동작하는 코드를 생성.",
    "command": "/run-workflow-phase2",
    "init_command": "python3 .claude/hooks/scripts/sot_manager.py --project-dir . --init --workflow phase2",
    "phase": "phase2",
    "enabled": True,
}

_MODE_PHASE2_RESUME = {
    "id": "phase2-resume",
    "label": "Phase 2: 풀스택 개발 — 이어서 진행",
    "label_en": "Phase 2: Full-Stack Development — Resume",
    "description": "이전에 중단된 Phase 2 워크플로우를 이어서 진행합니다.",
    "command": "/run-workflow-phase2",
    "phase": "phase2",
    "enabled": True,
}

_MODE_PHASE1_RESTART = {
    "id": "phase1-restart",
    "label": "Phase 1: PRD 생성 — 처음부터 다시",
    "label_en": "Phase 1: PRD Generation — Restart",
    "description": "기존 진행 상황을 초기화하고 Phase 1을 처음부터 다시 시작합니다. "
    "주의: 기존 SOT와 산출물이 초기화됩니다.",
    "command": "/run-workflow",
    "phase": "phase1",
    "destructive": True,
    "enabled": True,
}


def _check_command_exists(command_name, project_dir):
    """Check if a slash command file exists (.claude/commands/{name}.md).

    Args:
        command_name: Slash command name (e.g., "/run-workflow-phase2" → "run-workflow-phase2")
        project_dir: Project root directory.

    Returns:
        True if command file exists, False otherwise.
    """
    # Strip leading slash
    name = command_name.lstrip("/")
    cmd_path = os.path.join(project_dir, ".claude", "commands", f"{name}.md")
    return os.path.exists(cmd_path)


def _apply_availability_guards(modes, project_dir):
    """Apply runtime availability checks to mode list.

    Phase 2 modes are disabled if their command file doesn't exist yet.
    Returns a new list with guarded copies (original dicts are not mutated).
    """
    guarded = []
    for mode in modes:
        m = dict(mode)  # Shallow copy — don't mutate module-level constants
        command = m.get("command", "")
        if not _check_command_exists(command, project_dir):
            m["enabled"] = False
            m["unavailable_reason"] = f"Command {command} not yet implemented"
        guarded.append(m)
    return guarded


def _determine_modes(project_state, active_phase, wf_data, project_dir):
    """Determine available execution modes based on project state.

    Returns list of mode dicts, ordered by recommendation priority.
    Modes whose command files don't exist are marked enabled=false.
    """
    modes = []

    if project_state == "fresh":
        # No SOT — fresh start options
        modes.append(_MODE_PHASE1_FRESH)

        # Phase 2 available only if Phase 1 deliverable exists
        prd_path = os.path.join(project_dir, "prompt", "PRD-SaaS-AutoBuilder.md")
        if os.path.exists(prd_path):
            modes.append(_MODE_PHASE2_FRESH)

    elif project_state == "running":
        # Active workflow — resume is primary
        if active_phase == "phase1":
            modes.append(_MODE_PHASE1_RESUME)
            modes.append(_MODE_PHASE1_RESTART)
        elif active_phase == "phase2":
            modes.append(_MODE_PHASE2_RESUME)

    elif project_state == "paused" or project_state == "error":
        # Paused/Error — resume or restart
        if active_phase == "phase1":
            modes.append(_MODE_PHASE1_RESUME)
            modes.append(_MODE_PHASE1_RESTART)
        elif active_phase == "phase2":
            modes.append(_MODE_PHASE2_RESUME)

    elif project_state == "completed":
        # Phase completed — check which phase
        if active_phase == "phase1":
            # Phase 1 done → Phase 2 becomes primary
            modes.append(_MODE_PHASE2_FRESH)
            modes.append(_MODE_PHASE1_RESTART)
        elif active_phase == "phase2":
            # Both phases done — restart options
            modes.append(_MODE_PHASE1_RESTART)

    # Apply runtime availability guards (S-5: R-4 fix)
    return _apply_availability_guards(modes, project_dir)


# ---------------------------------------------------------------------------
# Main Logic
# ---------------------------------------------------------------------------
def detect_state(project_dir):
    """Main entry: detect project state and compute available modes.

    Returns a dict suitable for JSON output.
    """
    prereqs = _check_prerequisites()

    # Find and parse SOT
    sot_data, sot_path = _find_sot(project_dir)

    if sot_data is None:
        # No SOT — fresh project
        modes = _determine_modes("fresh", None, None, project_dir)
        return {
            "project_state": "fresh",
            "active_phase": None,
            "current_step": 0,
            "total_steps": 0,
            "workflow_name": None,
            "available_modes": modes,
            "settings": {"autopilot": False, "ulw": False},
            "prerequisites": prereqs,
            "resume_info": None,
        }

    # Parse SOT workflow data
    wf_data = sot_data.get("workflow", {})
    if not isinstance(wf_data, dict):
        wf_data = {}

    status = wf_data.get("status", "unknown")
    current_step = wf_data.get("current_step", 0)
    total_steps = wf_data.get("total_steps", 0)
    workflow_name = wf_data.get("name", "Unknown Workflow")

    # Detect phase
    active_phase = _detect_phase(wf_data)

    # Map SOT status to project_state
    state_map = {
        "running": "running",
        "completed": "completed",
        "error": "error",
        "paused": "paused",
    }
    project_state = state_map.get(status, "running")

    # Autopilot setting
    ap = wf_data.get("autopilot", {})
    autopilot_enabled = ap.get("enabled", False) if isinstance(ap, dict) else False

    # Build resume info
    resume_info = _build_resume_info(wf_data, active_phase)

    # Determine available modes
    modes = _determine_modes(project_state, active_phase, wf_data, project_dir)

    return {
        "project_state": project_state,
        "active_phase": active_phase,
        "current_step": current_step,
        "total_steps": total_steps,
        "workflow_name": workflow_name,
        "available_modes": modes,
        "settings": {
            "autopilot": autopilot_enabled,
            "ulw": False,  # ULW is a session-level flag, not persisted in SOT
        },
        "prerequisites": prereqs,
        "resume_info": resume_info,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Smart Router — detect project state and available execution modes"
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)

    result = detect_state(project_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
