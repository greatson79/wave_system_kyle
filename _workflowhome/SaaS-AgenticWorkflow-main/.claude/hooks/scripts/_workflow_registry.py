#!/usr/bin/env python3
"""
Workflow Registry — _workflow_registry.py

Provides polymorphic access to Phase-specific workflow DAGs.
This module decouples consumers from hardcoded Phase 1 or Phase 2 imports.

Usage:
    from _workflow_registry import get_workflow

    wf = get_workflow("phase1")  # or "phase2"
    wf.DAG, wf.TEAMS, wf.TOTAL_STEPS, wf.HUMAN_STEPS, wf.TRANSLATION_STEPS

    # Phase 2-specific attributes (AttributeError on Phase 1):
    wf.PACS_DIMENSIONS, wf.GATE_PROFILES, wf.L3_STEPS, wf.STEP_INPUTS

Architecture:
  - Lazy-imports each phase module on first access.
  - Returns the module object directly — consumers access DAG, TEAMS, etc. as attributes.
  - Default phase is "phase1" for backwards compatibility.
  - Phase detection from SOT: reads state.yaml to determine active workflow.

P1 Compliance: Pure module routing — no mutation, no side effects.
SOT Compliance: Read-only SOT access for auto-detection.
"""

import importlib
import os
import sys

# Ensure script directory is importable
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# ---------------------------------------------------------------------------
# Registry mapping: phase name → module name
# ---------------------------------------------------------------------------
_PHASE_MODULES = {
    "phase1": "_workflow_dag",
    "phase2": "_workflow_dag_phase2",
}

# Cache loaded modules
_loaded = {}

# Valid phase names (for validation)
VALID_PHASES = frozenset(_PHASE_MODULES.keys())

# Default phase (backwards compatibility)
DEFAULT_PHASE = "phase1"


def get_workflow(phase=None):
    """
    Get the workflow module for the specified phase.

    Args:
        phase: "phase1" or "phase2". If None, uses DEFAULT_PHASE.

    Returns:
        Module object with DAG, TEAMS, TOTAL_STEPS, etc. as attributes.

    Raises:
        ValueError: If phase is not in VALID_PHASES.
        ImportError: If the phase module cannot be loaded.
    """
    if phase is None:
        phase = DEFAULT_PHASE

    if phase not in VALID_PHASES:
        raise ValueError(
            f"Unknown workflow phase: {phase!r}. Valid: {sorted(VALID_PHASES)}"
        )

    if phase not in _loaded:
        module_name = _PHASE_MODULES[phase]
        _loaded[phase] = importlib.import_module(module_name)

    return _loaded[phase]


def detect_phase_from_sot(project_dir="."):
    """
    Auto-detect the active workflow phase from SOT (state.yaml).

    Reads the workflow name from state.yaml and maps it to a phase.
    Falls back to DEFAULT_PHASE if SOT doesn't exist or name is unrecognized.

    Args:
        project_dir: Project root directory.

    Returns:
        "phase1" or "phase2"
    """
    try:
        import yaml
    except ImportError:
        return DEFAULT_PHASE

    sot_path = os.path.join(project_dir, ".claude", "state.yaml")
    if not os.path.exists(sot_path):
        return DEFAULT_PHASE

    try:
        with open(sot_path, "r") as f:
            sot = yaml.safe_load(f) or {}
        wf_name = sot.get("workflow", {}).get("name", "")
        if "fullstack" in wf_name.lower() or "development" in wf_name.lower():
            return "phase2"
        return DEFAULT_PHASE
    except Exception:
        return DEFAULT_PHASE


def get_step_inputs(phase=None):
    """
    Get the STEP_INPUTS map for the specified phase.

    Phase 1: STEP_INPUTS is in orchestrator_actions.py (legacy location).
    Phase 2: STEP_INPUTS is in _workflow_dag_phase2.py (co-located with DAG).

    Args:
        phase: "phase1" or "phase2". If None, uses DEFAULT_PHASE.

    Returns:
        dict mapping step numbers/keys to input file lists.
    """
    wf = get_workflow(phase)
    return getattr(wf, "STEP_INPUTS", {})


def get_pacs_dimensions(phase=None):
    """
    Get pACS dimensions for the specified phase.

    Phase 1: ["F", "C", "L"] (3D)
    Phase 2: ["F", "C", "L", "T"] (4D — T for Testability)

    Args:
        phase: "phase1" or "phase2". If None, uses DEFAULT_PHASE.

    Returns:
        list of dimension names.
    """
    wf = get_workflow(phase)
    return getattr(wf, "PACS_DIMENSIONS", ["F", "C", "L"])


def get_gate_profile(phase=None, step=None):
    """
    Get the quality gate profile for a specific step.

    Phase 1: Always "document" (no gate_profile field).
    Phase 2: "code" (L1=tsc+eslint) or "document" (L1=D1-D5 structural) or None (human).

    Args:
        phase: "phase1" or "phase2".
        step: Step number.

    Returns:
        "code", "document", or None
    """
    wf = get_workflow(phase)
    profiles = getattr(wf, "GATE_PROFILES", {})
    if profiles:
        return profiles.get(step)
    # Phase 1 fallback: all non-human steps are "document" profile
    dag = wf.DAG
    if step in dag and dag[step].get("human"):
        return None
    return "document"
