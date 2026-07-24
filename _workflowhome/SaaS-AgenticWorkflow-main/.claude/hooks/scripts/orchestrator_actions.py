#!/usr/bin/env python3
"""
Orchestrator Actions — orchestrator_actions.py

Deterministic helper that eliminates 12 hallucination vectors (H-1 through H-12)
from the LLM orchestrator. Every subcommand returns JSON to stdout — the LLM
interprets JSON, not prose.

Architecture:
  - Phase-polymorphic via _workflow_registry.py — supports Phase 1 (PRD) and Phase 2 (dev).
  - Imports workflow DAG dynamically — NO hardcoded phase assumptions.
  - SOT read-only (SOT writes stay with sot_manager.py).
  - RLM pattern preserved. Backwards compatible (--workflow defaults to phase1).

Subcommands:
  --action step-config   --step N        → Agent name, output path, type, team (H-2)
  --action extract-pacs  --file PATH     → Regex-based pACS from output file (H-1)
  --action derive-paths  --step N        → KO path derivation + extension handling (H-3, H-5)
  --action team-files    --step N        → Team member list + file existence (H-4)
  --action pacs-decision --score S       → GREEN/YELLOW/RED branching (H-7)
  --action verify-deps   --step N        → Pre-execution dependency check (H-12)
  --action finalize-step12               → Step 12 hybrid protocol paths (H-11, Phase 1 only)
  --action agent-prompt  --step N        → Complete prompt with all paths substituted (H-3)

Global flags:
  --workflow phase1|phase2               → Select workflow phase (default: phase1)
  --project-dir PATH                     → Project root (default: .)

Usage:
    python3 orchestrator_actions.py --action step-config --step 3
    python3 orchestrator_actions.py --action step-config --step 5 --workflow phase2
    python3 orchestrator_actions.py --action extract-pacs --file prompt/research/synthesis-and-gaps.md
    python3 orchestrator_actions.py --action pacs-decision --score 65 --weak-dim C --step 3
    python3 orchestrator_actions.py --action agent-prompt --step 5 --project-dir .
    python3 orchestrator_actions.py --action team-files --step 6 --workflow phase2 --project-dir .

Exit codes:
    0 — success
    1 — error (invalid input, missing file, etc.)

P1 Compliance: Pure data transformations — no LLM interpretation, no side effects.
SOT Compliance: Read-only access via _read_sot_outputs().
"""

import argparse
import json
import os
import re
import sys

# Add script directory to path for shared library import
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE
from _context_lib import (
    _PACS_DIM_UNIVERSAL_RE,
    _PACS_WITH_MIN_RE,
    _PACS_SIMPLE_RE,
    _read_sot_outputs,
    sot_paths,
)


def _resolve_wf(wf):
    """Resolve workflow module. None → Phase 1 default (backwards compat)."""
    return wf if wf is not None else get_workflow(DEFAULT_PHASE)


# ---------------------------------------------------------------------------
# Explicit Input Map (C-1 fix: eliminates incomplete DAG-tracing)
# ---------------------------------------------------------------------------
# Derived from agent definition files' "Input Files (Quick Reference)" tables.
# This is the SINGLE source of truth for which files each agent must read.
# Key: step number (int) for sub-agent steps.
# Key: "N:agent-name" (str) for team member-specific inputs.
#
# P1 Compliance: Hardcoded from agent .md specs — no runtime derivation.
# Phase 1 STEP_INPUTS: co-located with DAG in _workflow_dag.py (same pattern as Phase 2).
# Re-exported here for backwards compatibility with existing imports.
from _workflow_dag import STEP_INPUTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ok(data):
    """Build a success JSON response."""
    return {"success": True, **data}


def _err(message):
    """Build an error JSON response."""
    return {"success": False, "error": message}


def _derive_ko_path(en_path):
    """Derive Korean translation path from English path.

    Rules (deterministic):
      - "file.md"       → "file.ko.md"
      - "file.txt"      → "file.ko.txt"
      - "file"          → "file.ko.md"
      - "file.ko.md"    → "file.ko.md" (already KO — no double suffix)

    H-5: Eliminates LLM guessing KO path derivation.
    """
    if ".ko." in en_path:
        return en_path  # Already a KO path

    base, ext = os.path.splitext(en_path)
    if ext:
        return f"{base}.ko{ext}"
    else:
        return f"{en_path}.ko.md"


def _get_step_inputs(step_num, member_agent=None, wf=None):
    """Return the explicit input file list for a step (or team member).

    Uses STEP_INPUTS — the hardcoded map derived from agent definition files.
    Both Phase 1 and Phase 2 STEP_INPUTS are co-located with their DAG modules.

    Args:
        step_num: Step number.
        member_agent: For team members, the agent name (e.g., "prd-writer-core").
        wf: Workflow module (None → Phase 1 default).

    Returns list of file path strings.

    H-3: Eliminates LLM guessing which files to read.
    """
    wf = _resolve_wf(wf)
    # Phase 2 has STEP_INPUTS co-located with DAG; Phase 1's is in this file
    step_inputs_map = getattr(wf, "STEP_INPUTS", None) or STEP_INPUTS

    # Team member-specific lookup
    if member_agent:
        key = f"{step_num}:{member_agent}"
        return list(step_inputs_map.get(key, []))

    # Step-level lookup
    return list(step_inputs_map.get(step_num, []))


# ---------------------------------------------------------------------------
# Action: step-config (H-2)
# ---------------------------------------------------------------------------
def action_step_config(step_num, wf=None):
    """Return deterministic step configuration from DAG.

    Eliminates H-2: LLM no longer interprets prose to find agent name,
    output path, step type, team info, review agent, etc.
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG
    teams = wf.TEAMS
    total = wf.TOTAL_STEPS
    trans_steps = wf.TRANSLATION_STEPS
    human_steps = wf.HUMAN_STEPS

    if step_num not in dag:
        return _err(f"Step {step_num} not found in DAG (valid: 1-{total})")

    info = dag[step_num]

    # Phase 1 Step 11 = two-phase review; Phase 2 has no special flows
    special_flow = None
    if step_num == 11 and hasattr(wf, "TOTAL_STEPS") and wf.TOTAL_STEPS == 12:
        special_flow = "two-phase"

    result = {
        "step": step_num,
        "name": info["name"],
        "type": info["type"],
        "agent": info["agent"],
        "team": info["team"],
        "output": info["output"],
        "deps": info["deps"],
        "human": info["human"],
        "pre_script": info["pre_script"],
        "review": info["review"],
        "translate": info["translate"],
        "is_translation_step": step_num in trans_steps,
        "is_human_step": step_num in human_steps,
        "special_flow": special_flow,
        # Phase 2 gate_profile (None for Phase 1 — always "document")
        "gate_profile": info.get("gate_profile"),
    }

    # Add team members if this is a team step
    if info["team"] and info["team"] in teams:
        team = teams[info["team"]]
        result["team_members"] = [
            {
                "agent": m["agent"],
                "task": m["task"],
                "output": m["output"],
            }
            for m in team["members"]
        ]

    return _ok(result)


# ---------------------------------------------------------------------------
# Action: extract-pacs (H-1)
# ---------------------------------------------------------------------------
def _cross_validate_pacs(content, dims, file_path):
    """P3: Structural cross-validation for pACS self-assessment.

    Compares agent-reported dimension scores against deterministic
    structural metrics to detect optimistic self-assessment (hallucination).

    Returns dict with warnings (list of str) and metrics (dict).
    Does NOT block — advisory only. Orchestrator/L2 reviewer use this data.

    P1 Compliance: Deterministic — regex + byte counting.
    """
    warnings = []
    metrics = {}

    # --- F (Faithfulness) cross-check: input reference density ---
    # Count distinct file references (basename patterns like "*.md")
    file_refs = set(re.findall(r'[\w-]+\.(?:md|txt|yaml|json|ts|tsx|py)', content))
    metrics["file_references"] = len(file_refs)

    f_score = dims.get("F") or dims.get("Faithfulness")
    if f_score is not None and f_score >= 80 and len(file_refs) < 3:
        warnings.append(
            f"F cross-check: Agent reports F={f_score} but only "
            f"{len(file_refs)} file references found. "
            f"High Faithfulness requires source references."
        )

    # --- C (Completeness) cross-check: section count ---
    headings = re.findall(r'^#{1,3}\s+.+', content, re.MULTILINE)
    metrics["section_count"] = len(headings)

    c_score = dims.get("C") or dims.get("Completeness")
    if c_score is not None and c_score >= 80 and len(headings) < 4:
        warnings.append(
            f"C cross-check: Agent reports C={c_score} but only "
            f"{len(headings)} sections found. "
            f"High Completeness requires comprehensive coverage."
        )

    # --- L (Lucidity) cross-check: content density ---
    # Measure average paragraph length (bytes per non-empty paragraph)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    non_heading_paras = [
        p for p in paragraphs
        if not p.startswith("#") and len(p) > 20
    ]
    avg_para_bytes = 0
    if non_heading_paras:
        avg_para_bytes = sum(len(p.encode("utf-8")) for p in non_heading_paras) // len(non_heading_paras)
    metrics["avg_paragraph_bytes"] = avg_para_bytes
    metrics["paragraph_count"] = len(non_heading_paras)

    l_score = dims.get("L") or dims.get("Lucidity")
    if l_score is not None and l_score >= 80 and avg_para_bytes < 80:
        warnings.append(
            f"L cross-check: Agent reports L={l_score} but "
            f"average paragraph is only {avg_para_bytes} bytes. "
            f"High Lucidity requires substantive exposition."
        )

    # --- T (Testability) cross-check: test-related patterns ---
    t_score = dims.get("T") or dims.get("Testability")
    if t_score is not None:
        test_patterns = len(re.findall(
            r'\b(?:test|spec|assert|expect|describe|it\(|mock|stub|fixture)\b',
            content, re.IGNORECASE
        ))
        metrics["test_pattern_count"] = test_patterns
        if t_score >= 80 and test_patterns < 3:
            warnings.append(
                f"T cross-check: Agent reports T={t_score} but only "
                f"{test_patterns} test-related patterns found. "
                f"High Testability requires explicit test considerations."
            )

    # --- File size cross-check ---
    try:
        file_size = os.path.getsize(file_path)
        metrics["file_size_bytes"] = file_size
        # If all dimensions >= 75 but file is tiny, flag it
        if dims and all(v >= 75 for v in dims.values()) and file_size < 2000:
            warnings.append(
                f"Size cross-check: All dimensions ≥75 but file is only "
                f"{file_size} bytes. High-quality output typically exceeds 2KB."
            )
    except OSError:
        pass

    return {
        "warnings": warnings,
        "metrics": metrics,
        "has_warnings": len(warnings) > 0,
    }


def action_extract_pacs(file_path, project_dir):
    """Extract pACS score from an agent output file using deterministic regex.

    Eliminates H-1: LLM no longer interprets pACS self-assessment prose.
    Uses the same regex patterns as _context_lib.py (verify_pacs_arithmetic).
    """
    full_path = (
        os.path.join(project_dir, file_path)
        if not os.path.isabs(file_path)
        else file_path
    )

    if not os.path.exists(full_path):
        return _err(f"File not found: {full_path}")

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return _err(f"Cannot read file: {e}")

    # Extract dimension scores — matches verify_pacs_arithmetic() in _context_lib.py
    # Uses raw dimension names (no canonicalization) for reference-impl alignment.
    dims = {}
    seen_dim_scores = {}  # dim → list of scores (ambiguity detection, C-3 fix)
    for match in _PACS_DIM_UNIVERSAL_RE.finditer(content):
        dim_name = match.group(1)
        dim_score = int(match.group(2))
        if 0 <= dim_score <= 100:
            seen_dim_scores.setdefault(dim_name, []).append(dim_score)
            dims[dim_name] = dim_score

    # Ambiguity guard (C-3 fix): if same dimension appears with different scores, skip it
    for dim_name, scores in seen_dim_scores.items():
        if len(set(scores)) > 1:
            del dims[dim_name]

    # Minimum dimension guard (C-3 fix): need at least 2 dimensions for meaningful min()
    calculated_score = None
    if len(dims) >= 2:
        calculated_score = min(dims.values())

    # Extract reported final score
    reported_score = None
    min_match = _PACS_WITH_MIN_RE.search(content)
    if min_match:
        reported_score = int(min_match.group(1))
    else:
        simple_matches = _PACS_SIMPLE_RE.findall(content)
        if len(simple_matches) == 1:
            reported_score = int(simple_matches[0])

    # Determine weak dimension (from raw dims)
    weak_dim = ""
    if len(dims) >= 2:
        min_val = min(dims.values())
        weak_candidates = [k for k, v in dims.items() if v == min_val]
        weak_dim = weak_candidates[0] if weak_candidates else ""

    # Arithmetic verification
    arithmetic_ok = True
    if reported_score is not None and calculated_score is not None:
        arithmetic_ok = reported_score == calculated_score

    # Use calculated score if available, otherwise reported
    final_score = calculated_score if calculated_score is not None else reported_score

    # P3: Structural cross-validation — detect optimistic self-assessment
    cross_validation = _cross_validate_pacs(content, dims, full_path)

    result = {
        "file": file_path,
        "dimensions": dims,
        "reported_score": reported_score,
        "calculated_score": calculated_score,
        "final_score": final_score,
        "weak_dim": weak_dim,
        "arithmetic_ok": arithmetic_ok,
        "found": final_score is not None,
        "cross_validation": cross_validation,
    }

    return _ok(result)


# ---------------------------------------------------------------------------
# Action: derive-paths (H-3, H-5)
# ---------------------------------------------------------------------------
def action_derive_paths(step_num, project_dir, wf=None):
    """Derive all file paths for a step: output, KO path, inputs.

    Eliminates H-3 (input file guessing) and H-5 (KO path derivation).
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG
    teams = wf.TEAMS

    if step_num not in dag:
        return _err(f"Step {step_num} not found in DAG")

    info = dag[step_num]
    en_path = info["output"]

    # KO path derivation
    ko_path = None
    if info["translate"] and en_path != "approved-by-user":
        ko_path = _derive_ko_path(en_path)

    # Input files from STEP_INPUTS (explicit map)
    inputs = _get_step_inputs(step_num, wf=wf)

    # Check file existence
    def _check(path):
        if not path or path == "approved-by-user":
            return None
        fp = os.path.join(project_dir, path) if not os.path.isabs(path) else path
        return os.path.exists(fp)

    result = {
        "step": step_num,
        "en_output": en_path,
        "ko_output": ko_path,
        "inputs": [
            {"path": path, "exists": _check(path)}
            for path in inputs
        ],
    }

    # For team steps, add member paths
    if info["team"] and info["team"] in teams:
        team = teams[info["team"]]
        result["team_member_outputs"] = [
            {
                "agent": m["agent"],
                "en_path": m["output"],
                "ko_path": _derive_ko_path(m["output"]) if info["translate"] else None,
                "en_exists": _check(m["output"]),
            }
            for m in team["members"]
        ]

    return _ok(result)


# ---------------------------------------------------------------------------
# Action: team-files (H-4)
# ---------------------------------------------------------------------------
def action_team_files(step_num, project_dir, wf=None):
    """Return team member list with file existence and CSV assembly.

    Eliminates H-4: LLM no longer assembles team member CSV manually.
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG
    teams = wf.TEAMS

    if step_num not in dag:
        return _err(f"Step {step_num} not found in DAG")

    info = dag[step_num]
    if info["type"] != "agent-team" or not info["team"]:
        return _err(f"Step {step_num} is not a team step (type: {info['type']})")

    team_name = info["team"]
    if team_name not in teams:
        return _err(f"Team '{team_name}' not found in TEAMS dict")

    team = teams[team_name]
    members = []
    all_exist = True
    files_csv = []

    for m in team["members"]:
        en_path = m["output"]
        full_path = os.path.join(project_dir, en_path) if not os.path.isabs(en_path) else en_path
        exists = os.path.exists(full_path)
        if not exists:
            all_exist = False
        files_csv.append(en_path)

        members.append({
            "agent": m["agent"],
            "task": m["task"],
            "output": en_path,
            "exists": exists,
        })

    result = {
        "step": step_num,
        "team_name": team_name,
        "member_count": len(members),
        "members": members,
        "all_outputs_exist": all_exist,
        "files_csv": ",".join(files_csv),
        "manifest_path": info["output"],
    }

    return _ok(result)


# ---------------------------------------------------------------------------
# Action: pacs-decision (H-7)
# ---------------------------------------------------------------------------
def action_pacs_decision(score, weak_dim, step_num):
    """Deterministic pACS decision: GREEN/YELLOW/RED with rework feedback.

    Eliminates H-7: LLM no longer interprets the decision matrix from prose.

    Decision Matrix:
      >= 70  → GREEN  → Proceed
      50-69  → YELLOW → Proceed with warning
      < 50   → RED    → Rework required with targeted feedback
    """
    if not (0 <= score <= 100):
        return _err(f"pACS score {score} out of range (0-100)")

    # Deterministic decision
    if score >= 70:
        color = "GREEN"
        action = "proceed"
        feedback = None
    elif score >= 50:
        color = "YELLOW"
        action = "proceed_with_warning"
        feedback = f"Warning: pACS score {score} is below GREEN threshold (70). Weak dimension: {weak_dim or 'unknown'}."
    else:
        color = "RED"
        action = "rework_required"

        # Targeted feedback based on weak dimension
        feedback_map = {
            "F": (
                "Your output deviated from the input sources. "
                "Re-read ALL inputs and ensure every claim traces back to a specific source. "
                "Cross-reference your analysis against the original PRD and research outputs."
            ),
            "C": (
                "Your output is missing required elements. "
                "Check your protocol and ensure ALL phases are executed. "
                "Verify every required sub-section, table, diagram, and code block is present."
            ),
            "L": (
                "Your output has logical inconsistencies. "
                "Review your conclusions against your analysis. "
                "Ensure internal cross-references are correct and arguments are coherent."
            ),
            "T": (
                "Your code lacks adequate testability. "
                "Ensure functions have clear inputs/outputs and dependencies are injectable. "
                "Edge cases must be explicitly handled. Add test hooks where appropriate."
            ),
        }
        feedback = feedback_map.get(
            weak_dim,
            "Your output scored below the minimum threshold. "
            "Review all protocol requirements and ensure full compliance."
        )

    result = {
        "step": step_num,
        "score": score,
        "weak_dim": weak_dim or "",
        "color": color,
        "action": action,
        "feedback": feedback,
        "rework_max": 1 if color == "RED" else 0,
    }

    return _ok(result)


# ---------------------------------------------------------------------------
# Action: verify-deps (H-12)
# ---------------------------------------------------------------------------
def action_verify_deps(step_num, project_dir, wf=None):
    """Verify all dependency outputs exist before executing a step.

    Eliminates H-12: LLM no longer skips dependency checks.
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG
    teams = wf.TEAMS

    if step_num not in dag:
        return _err(f"Step {step_num} not found in DAG")

    info = dag[step_num]
    deps = info["deps"]

    if not deps:
        return _ok({
            "step": step_num,
            "deps_satisfied": True,
            "deps": [],
            "missing": [],
        })

    dep_results = []
    missing = []

    for dep_step in deps:
        dep_info = dag.get(dep_step)
        if not dep_info:
            missing.append({"step": dep_step, "reason": "Step not found in DAG"})
            continue

        dep_output = dep_info["output"]
        if dep_output == "approved-by-user":
            # Human steps — check SOT for completion
            outputs = _read_sot_outputs(project_dir)
            sot_key = f"step-{dep_step}"
            if sot_key in outputs:
                dep_results.append({
                    "step": dep_step,
                    "output": dep_output,
                    "satisfied": True,
                    "method": "sot_check",
                })
            else:
                missing.append({
                    "step": dep_step,
                    "output": dep_output,
                    "reason": f"Human step {dep_step} not recorded in SOT",
                })
            continue

        # For team steps, check all member outputs
        if dep_info["type"] == "agent-team" and dep_info.get("team"):
            team = teams.get(dep_info["team"], {})
            team_satisfied = True
            for member in team.get("members", []):
                m_path = member["output"]
                full_path = os.path.join(project_dir, m_path) if not os.path.isabs(m_path) else m_path
                if not os.path.exists(full_path):
                    team_satisfied = False
                    missing.append({
                        "step": dep_step,
                        "output": m_path,
                        "reason": f"Team member output missing: {m_path}",
                    })
            if team_satisfied:
                dep_results.append({
                    "step": dep_step,
                    "output": dep_output,
                    "satisfied": True,
                    "method": "team_files_check",
                })
        else:
            # Regular step — check file exists
            full_path = os.path.join(project_dir, dep_output) if not os.path.isabs(dep_output) else dep_output
            if os.path.exists(full_path):
                dep_results.append({
                    "step": dep_step,
                    "output": dep_output,
                    "satisfied": True,
                    "method": "file_exists",
                })
            else:
                missing.append({
                    "step": dep_step,
                    "output": dep_output,
                    "reason": f"Output file missing: {dep_output}",
                })

    return _ok({
        "step": step_num,
        "deps_satisfied": len(missing) == 0,
        "deps": dep_results,
        "missing": missing,
    })


# ---------------------------------------------------------------------------
# Action: finalize-step12 (H-11)
# ---------------------------------------------------------------------------
def action_finalize_step12(project_dir, wf=None):
    """Return the exact sequence of commands for Step 12 hybrid protocol.

    Eliminates H-11: LLM no longer interprets the Step 12 protocol from prose.
    Returns the deterministic command list with all paths substituted.

    Phase 1 only: Step 12 is the hybrid human+production step.
    Phase 2 Step 16 is pure human approval — use standard human step protocol.
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG

    step_info = dag.get(12)
    if not step_info:
        return _err("Step 12 not found in DAG")

    # Guard: This protocol is Phase 1-specific (12-step workflow)
    if wf.TOTAL_STEPS != 12:
        return _err(
            f"finalize-step12 is Phase 1-specific. "
            f"Current workflow has {wf.TOTAL_STEPS} steps."
        )

    # Step 11 output is the input for Step 12
    step_11_output = dag.get(11, {}).get("output", "")
    final_en = step_info["output"]
    final_ko = _derive_ko_path(final_en)

    scripts_dir = ".claude/hooks/scripts"

    # W-5 fix: derive source from DAG instead of hardcoding
    validated_source = dag.get(10, {}).get("output", "prompt/implementation/prd-validated.md")

    commands = [
        {
            "order": 1,
            "description": "Copy validated+reviewed PRD to final location",
            "type": "copy",
            "source": validated_source,
            "destination": final_en,
        },
        {
            "order": 2,
            "description": "Spawn @translator for final PRD",
            "type": "agent",
            "agent": "translator",
            "input": final_en,
            "output": final_ko,
            "glossary": "translations/glossary.yaml",
        },
        {
            "order": 3,
            "description": "Validate bilingual pair",
            "type": "bash",
            "command": f"python3 {scripts_dir}/bilingual_validator.py --step 12 --project-dir .",
        },
        {
            "order": 4,
            "description": "Register translation in SOT",
            "type": "bash",
            "command": f"python3 {scripts_dir}/sot_manager.py --project-dir . --add-translation 12 --ko-path {final_ko}",
        },
        {
            "order": 5,
            "description": "Update SOT with final output",
            "type": "bash",
            "command": f"python3 {scripts_dir}/sot_manager.py --project-dir . --update-step 12 --output {final_en}",
        },
    ]

    return _ok({
        "step": 12,
        "input": step_11_output,
        "final_en": final_en,
        "final_ko": final_ko,
        "commands": commands,
    })


# ---------------------------------------------------------------------------
# Action: agent-prompt (H-3)
# ---------------------------------------------------------------------------
def action_agent_prompt(step_num, project_dir, wf=None):
    """Generate complete agent prompt with all paths substituted.

    Eliminates H-3: LLM no longer guesses input file paths from prose.
    Returns the exact prompt string with every file path filled in.
    """
    wf = _resolve_wf(wf)
    dag = wf.DAG
    teams = wf.TEAMS

    if step_num not in dag:
        return _err(f"Step {step_num} not found in DAG")

    info = dag[step_num]

    if info["type"] == "human":
        return _err(f"Step {step_num} is a human step — no agent prompt needed")

    if info["type"] == "agent-team":
        # For team steps, generate per-member prompts with concrete file paths (C-2 fix)
        team_name = info["team"]
        if team_name not in teams:
            return _err(f"Team '{team_name}' not found")

        team = teams[team_name]
        member_prompts = []
        for m in team["members"]:
            # Get per-member required inputs from STEP_INPUTS
            member_inputs = _get_step_inputs(step_num, member_agent=m["agent"], wf=wf)
            if member_inputs:
                input_lines = "\n".join(f"- {path}" for path in member_inputs)
                input_section = (
                    f"Read these REQUIRED input files before starting:\n{input_lines}\n"
                    f"Also read coding-resource/PRD.md for verification."
                )
            else:
                input_section = "Read ALL inputs listed in your agent definition before starting."

            prompt = (
                f"You are the @{m['agent']} agent. "
                f"Execute your task: {m['task']}.\n\n"
                f"{input_section}\n\n"
                f"Write output to {m['output']}. "
                f"Quality is the ONLY criterion — take as many turns as needed.\n"
                f"Include pACS self-assessment at the end of your output."
            )
            member_prompts.append({
                "agent": m["agent"],
                "task": m["task"],
                "output": m["output"],
                "inputs": member_inputs,
                "prompt": prompt,
            })

        return _ok({
            "step": step_num,
            "type": "agent-team",
            "team": team_name,
            "member_prompts": member_prompts,
        })

    # Sub-agent step — generate single agent prompt using STEP_INPUTS
    agent = info["agent"]
    output = info["output"]
    inputs = _get_step_inputs(step_num, wf=wf)

    # Build input file listing from explicit STEP_INPUTS
    if inputs:
        input_lines = "\n".join(f"- {path}" for path in inputs)
        input_section = f"Read these REQUIRED input files before starting:\n{input_lines}"
        # Add PRD if not already in the list
        if "coding-resource/PRD.md" not in inputs:
            input_section += "\nAlso read coding-resource/PRD.md for verification."
    else:
        input_section = "Read ALL inputs listed in your agent definition before starting."

    # Build prompt
    prompt = (
        f"You are the @{agent} agent. "
        f"Execute Step {step_num}: {info['name']}.\n\n"
        f"{input_section}\n\n"
        f"Write your complete output to {output}.\n"
        f"Follow your agent definition protocol exactly. "
        f"Quality is the ONLY criterion — take as many turns as needed.\n"
        f"Include pACS self-assessment at the end of your output."
    )

    # Pre-script info
    pre_script = None
    if info["pre_script"]:
        pre_script = {
            "script": info["pre_script"],
            "command": f"python3 scripts/{info['pre_script']}",
        }
        # Add script-specific args based on known scripts
        if info["pre_script"] == "extract_prd_sections.py":
            pre_script["command"] = (
                "python3 scripts/extract_prd_sections.py "
                "--input coding-resource/PRD.md "
                "--output-dir prompt/research/sections/"
            )
        elif info["pre_script"] == "merge_prd_sections.py":
            pre_script["command"] = (
                "python3 scripts/merge_prd_sections.py "
                "--input-dir prompt/implementation/ "
                "--output prompt/implementation/prd-merged.md"
            )

    # Review info
    review = None
    if info["review"]:
        review = {
            "agent": info["review"],
            "output_to_review": output,
        }

    result = {
        "step": step_num,
        "type": "sub-agent",
        "agent": agent,
        "output": output,
        "prompt": prompt,
        "pre_script": pre_script,
        "review": review,
        "translate": info["translate"],
        "ko_output": _derive_ko_path(output) if info["translate"] else None,
        "inputs": inputs,
    }

    return _ok(result)


# ---------------------------------------------------------------------------
# Step 11 special prompt (two-phase)
# ---------------------------------------------------------------------------
def _step_11_prompt(wf=None):
    """Generate Step 11 two-phase review prompts (Phase 1 only)."""
    wf = _resolve_wf(wf)
    dag = wf.DAG

    step_info = dag.get(11)
    if not step_info:
        return _err("Step 11 not found in DAG")

    validated_prd = dag.get(10, {}).get("output", "prompt/implementation/prd-validated.md")
    review_output = step_info["output"]

    phase1_prompt = (
        f"Adversarially review the validated PRD at {validated_prd}. "
        f"This is Step 11 — the last automated quality gate before human review. "
        f"Check all 16 sections, all F1-F8 features, cross-references, code blocks, diagrams. "
        f"Your review report is the primary deliverable."
    )

    phase2_prompt = (
        f"Fact-check the validated PRD at {validated_prd}. "
        f"Extract all verifiable claims (technical, statistical, comparative). "
        f"Verify against independent sources. Focus on technology choices, "
        f"performance claims, and market data."
    )

    return _ok({
        "step": 11,
        "type": "two-phase",
        "input": validated_prd,
        "output": review_output,
        "phase1": {
            "agent": "reviewer",
            "subagent_type": "reviewer",
            "prompt": phase1_prompt,
        },
        "phase2": {
            "agent": "fact-checker",
            "subagent_type": "fact-checker",
            "prompt": phase2_prompt,
        },
        "merge_instruction": f"Merge both reports into {review_output}",
    })


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------
ACTIONS = {
    "step-config": "step_config",
    "extract-pacs": "extract_pacs",
    "derive-paths": "derive_paths",
    "team-files": "team_files",
    "pacs-decision": "pacs_decision",
    "verify-deps": "verify_deps",
    "finalize-step12": "finalize_step12",
    "agent-prompt": "agent_prompt",
}


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrator Actions — deterministic helpers for workflow orchestration"
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=sorted(ACTIONS.keys()),
        help="Action to perform",
    )
    parser.add_argument(
        "--step",
        type=int,
        help="Step number (required for most actions)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File path (for extract-pacs)",
    )
    parser.add_argument(
        "--score",
        type=int,
        help="pACS score 0-100 (for pacs-decision)",
    )
    parser.add_argument(
        "--weak-dim",
        type=str,
        default="",
        help="Weak dimension F/C/L/T (for pacs-decision)",
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

    # Load workflow module for the requested phase
    wf = get_workflow(args.workflow)

    try:
        action = args.action

        if action == "step-config":
            if args.step is None:
                result = _err("--step is required for step-config")
            else:
                result = action_step_config(args.step, wf=wf)

        elif action == "extract-pacs":
            if not args.file:
                result = _err("--file is required for extract-pacs")
            else:
                result = action_extract_pacs(args.file, project_dir)

        elif action == "derive-paths":
            if args.step is None:
                result = _err("--step is required for derive-paths")
            else:
                result = action_derive_paths(args.step, project_dir, wf=wf)

        elif action == "team-files":
            if args.step is None:
                result = _err("--step is required for team-files")
            else:
                result = action_team_files(args.step, project_dir, wf=wf)

        elif action == "pacs-decision":
            if args.score is None:
                result = _err("--score is required for pacs-decision")
            else:
                result = action_pacs_decision(
                    args.score,
                    args.weak_dim,
                    args.step if args.step is not None else 0,
                )

        elif action == "verify-deps":
            if args.step is None:
                result = _err("--step is required for verify-deps")
            else:
                result = action_verify_deps(args.step, project_dir, wf=wf)

        elif action == "finalize-step12":
            result = action_finalize_step12(project_dir, wf=wf)

        elif action == "agent-prompt":
            if args.step is None:
                result = _err("--step is required for agent-prompt")
            elif args.step == 11 and wf.TOTAL_STEPS == 12:
                # Phase 1 Step 11 = two-phase review (special handling)
                result = _step_11_prompt(wf=wf)
            else:
                result = action_agent_prompt(args.step, project_dir, wf=wf)

        else:
            result = _err(f"Unknown action: {action}")

    except Exception as e:
        result = _err(f"Fatal: {type(e).__name__}: {e}")

    # Single exit point — all paths converge here
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
