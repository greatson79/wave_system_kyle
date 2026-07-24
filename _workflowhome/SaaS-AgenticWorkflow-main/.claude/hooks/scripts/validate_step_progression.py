#!/usr/bin/env python3
"""
Step Progression Guard — validate_step_progression.py

Validates that ALL obligations for the current step are fulfilled before
allowing progression to the next step. This deterministic script prevents
the orchestrator LLM from accidentally skipping SOT updates, translations,
reviews, or ignoring pACS rework decisions.

Called by the orchestrator BEFORE advancing current_step.
Can also be integrated into workflow_router.py as a pre-check.

Usage:
    python3 validate_step_progression.py --step N --project-dir .
    python3 validate_step_progression.py --step 5 --workflow phase2 --project-dir .

Output (JSON stdout):
    {
        "step": 5,
        "can_progress": true,
        "checks": {
            "SP1_sot_output": {"passed": true, "details": "..."},
            "SP2_pacs_recorded": {"passed": true, "score": 75, "color": "GREEN"},
            "SP3_pacs_decision_compliance": {"passed": true, "details": "..."},
            "SP4_translation_complete": {"passed": true, "details": "..."},
            "SP5_review_complete": {"passed": true, "details": "..."},
            "SP6_output_file_exists": {"passed": true, "details": "..."}
        },
        "blockers": []
    }

Exit codes:
    0 — all checks passed, step can progress
    1 — one or more checks failed, progression blocked

Checks:
    SP1: SOT has output registered for this step
    SP2: pACS score recorded in SOT pacs.history
    SP3: pACS decision compliance — if decision was "rework_required",
         verify rework was actually performed (score improved or action_taken logged)
    SP4: If translate=true, .ko output exists and is registered in SOT
    SP5: If review agent assigned, review log exists
    SP6: Output file exists on disk and meets L0 criteria

P1 Compliance: Deterministic — YAML parsing + file existence + arithmetic.
SOT Compliance: Read-only — reads state.yaml, never modifies.
"""

import argparse
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE

# Minimum file size for valid output (matches L0)
MIN_OUTPUT_SIZE = 100


def _read_sot(project_dir):
    """Read and parse state.yaml. Returns dict or None."""
    try:
        import yaml
    except ImportError:
        return None

    sot_candidates = [
        os.path.join(project_dir, ".claude", "state.yaml"),
        os.path.join(project_dir, "state.yaml"),
    ]
    for sot_path in sot_candidates:
        if os.path.exists(sot_path):
            try:
                with open(sot_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
            except Exception:
                continue
    return None


def validate_progression(step_num, project_dir, wf=None):
    """Validate all obligations for step_num are fulfilled.

    Args:
        step_num: Step number to validate for progression.
        project_dir: Project root directory.
        wf: Workflow module (None → Phase 1 default).

    Returns:
        dict with can_progress (bool), checks (dict), blockers (list).
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)

    dag = wf.DAG
    checks = {}
    blockers = []

    if step_num not in dag:
        return {
            "step": step_num,
            "can_progress": False,
            "checks": {},
            "blockers": [f"Step {step_num} not found in DAG"],
        }

    step_info = dag[step_num]

    # Human steps have different obligations
    is_human = step_info.get("human", False)
    if is_human:
        # Human steps only need SOT acknowledgement
        sot = _read_sot(project_dir)
        if sot:
            wf_data = sot.get("workflow", {})
            outputs = wf_data.get("outputs", {})
            step_key = f"step-{step_num}"
            has_output = step_key in outputs
            checks["SP1_sot_output"] = {
                "passed": has_output,
                "details": f"SOT output for {step_key}: "
                           + ("registered" if has_output else "NOT FOUND"),
            }
            if not has_output:
                blockers.append(
                    f"SP1: SOT output not registered for human step {step_num}"
                )
        else:
            checks["SP1_sot_output"] = {
                "passed": False,
                "details": "SOT file not found",
            }
            blockers.append("SP1: SOT file not found")

        return {
            "step": step_num,
            "can_progress": len(blockers) == 0,
            "checks": checks,
            "blockers": blockers,
        }

    # -----------------------------------------------------------------------
    # SP1: SOT has output registered
    # -----------------------------------------------------------------------
    sot = _read_sot(project_dir)
    if not sot:
        checks["SP1_sot_output"] = {
            "passed": False,
            "details": "SOT file not found",
        }
        blockers.append("SP1: SOT file not found — cannot verify progression")
        # Return early — all other checks depend on SOT
        return {
            "step": step_num,
            "can_progress": False,
            "checks": checks,
            "blockers": blockers,
        }

    wf_data = sot.get("workflow", {})
    outputs = wf_data.get("outputs", {})
    step_key = f"step-{step_num}"
    output_path = outputs.get(step_key)

    sp1_passed = bool(output_path)
    checks["SP1_sot_output"] = {
        "passed": sp1_passed,
        "details": f"SOT {step_key}: {output_path}" if sp1_passed
                   else f"SOT {step_key}: NOT REGISTERED",
    }
    if not sp1_passed:
        blockers.append(
            f"SP1: Output not registered in SOT for step {step_num}. "
            f"Run: sot_manager.py --update-step {step_num} --output <path>"
        )

    # -----------------------------------------------------------------------
    # SP2: pACS score recorded in SOT
    # -----------------------------------------------------------------------
    pacs_data = wf_data.get("pacs", {})
    pacs_history = pacs_data.get("history", {})
    pacs_entry = pacs_history.get(f"step-{step_num}", {})
    pacs_score = pacs_entry.get("score")

    sp2_passed = pacs_score is not None
    pacs_color = "UNKNOWN"
    if pacs_score is not None:
        if pacs_score >= 70:
            pacs_color = "GREEN"
        elif pacs_score >= 50:
            pacs_color = "YELLOW"
        else:
            pacs_color = "RED"

    checks["SP2_pacs_recorded"] = {
        "passed": sp2_passed,
        "score": pacs_score,
        "color": pacs_color,
        "details": f"pACS score: {pacs_score} ({pacs_color})" if sp2_passed
                   else "pACS score NOT recorded in SOT",
    }
    if not sp2_passed:
        blockers.append(
            f"SP2: pACS score not recorded for step {step_num}. "
            f"Run: sot_manager.py --update-pacs {step_num} --pacs-score <N>"
        )

    # -----------------------------------------------------------------------
    # SP3: pACS decision compliance
    # -----------------------------------------------------------------------
    action_taken = pacs_entry.get("action_taken")
    decision_action = pacs_entry.get("decision_action")

    if pacs_score is not None and pacs_score < 50:
        # RED score — rework was required
        if decision_action == "rework_required" and action_taken == "proceed":
            # Orchestrator ignored rework requirement — BLOCK
            sp3_passed = False
            checks["SP3_pacs_decision_compliance"] = {
                "passed": False,
                "decision": "rework_required",
                "action_taken": "proceed",
                "details": "VIOLATION: pACS RED + rework_required, "
                           "but action_taken=proceed. "
                           "Orchestrator must rework before progressing.",
            }
            blockers.append(
                f"SP3: pACS decision violation — step {step_num} "
                f"scored RED ({pacs_score}) with rework_required, "
                f"but orchestrator proceeded without rework."
            )
        elif pacs_score < 50 and action_taken not in ("rework", "escalated"):
            # RED but no compliant action recorded
            sp3_passed = False
            checks["SP3_pacs_decision_compliance"] = {
                "passed": False,
                "score": pacs_score,
                "action_taken": action_taken,
                "details": f"RED score ({pacs_score}) requires rework or escalation. "
                           f"action_taken: {action_taken}",
            }
            blockers.append(
                f"SP3: RED pACS ({pacs_score}) for step {step_num} — "
                f"action_taken must be 'rework' or 'escalated', got: {action_taken}"
            )
        else:
            sp3_passed = True
            checks["SP3_pacs_decision_compliance"] = {
                "passed": True,
                "details": f"RED score handled: action_taken={action_taken}",
            }
    else:
        # GREEN or YELLOW — no compliance issue
        sp3_passed = True
        checks["SP3_pacs_decision_compliance"] = {
            "passed": True,
            "details": "Non-RED score — no rework compliance required"
                       if pacs_score is not None
                       else "Skipped — no pACS score available",
        }

    # -----------------------------------------------------------------------
    # SP4: Translation complete (if translate=true)
    # -----------------------------------------------------------------------
    should_translate = step_info.get("translate", False)
    if should_translate:
        ko_key = f"step-{step_num}-ko"
        ko_path = outputs.get(ko_key)
        sp4_passed = bool(ko_path)

        if sp4_passed:
            # Also verify file exists on disk
            ko_full = (
                os.path.join(project_dir, ko_path)
                if not os.path.isabs(ko_path)
                else ko_path
            )
            if not os.path.exists(ko_full):
                sp4_passed = False
                checks["SP4_translation_complete"] = {
                    "passed": False,
                    "details": f"KO path registered ({ko_path}) but file not found on disk",
                }
                blockers.append(
                    f"SP4: Translation registered in SOT ({ko_path}) "
                    f"but file does not exist"
                )
            else:
                checks["SP4_translation_complete"] = {
                    "passed": True,
                    "ko_path": ko_path,
                    "details": f"Translation registered and file exists: {ko_path}",
                }
        else:
            checks["SP4_translation_complete"] = {
                "passed": False,
                "details": f"Step {step_num} has translate=true but "
                           f"no {ko_key} registered in SOT",
            }
            blockers.append(
                f"SP4: Step {step_num} requires translation but "
                f"{ko_key} not in SOT outputs"
            )
    else:
        checks["SP4_translation_complete"] = {
            "passed": True,
            "details": "Step does not require translation",
        }

    # -----------------------------------------------------------------------
    # SP5: Review complete (if review agent assigned)
    # -----------------------------------------------------------------------
    review_agent = step_info.get("review")
    if review_agent:
        review_path = os.path.join(
            project_dir, "review-logs", f"step-{step_num}-review.md"
        )
        sp5_passed = os.path.exists(review_path)
        if sp5_passed:
            size = os.path.getsize(review_path)
            sp5_passed = size >= MIN_OUTPUT_SIZE
            checks["SP5_review_complete"] = {
                "passed": sp5_passed,
                "review_agent": review_agent,
                "details": f"Review log exists ({size} bytes)"
                           if sp5_passed
                           else f"Review log too small ({size} bytes)",
            }
        else:
            checks["SP5_review_complete"] = {
                "passed": False,
                "review_agent": review_agent,
                "details": f"Review log not found: {review_path}",
            }

        if not sp5_passed:
            blockers.append(
                f"SP5: Review by {review_agent} not complete for step {step_num}. "
                f"Expected: review-logs/step-{step_num}-review.md"
            )
    else:
        checks["SP5_review_complete"] = {
            "passed": True,
            "details": "No review agent assigned for this step",
        }

    # -----------------------------------------------------------------------
    # SP6: Output file exists on disk
    # -----------------------------------------------------------------------
    if output_path and output_path != "approved-by-user":
        full_path = (
            os.path.join(project_dir, output_path)
            if not os.path.isabs(output_path)
            else output_path
        )
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            sp6_passed = size >= MIN_OUTPUT_SIZE
            checks["SP6_output_file_exists"] = {
                "passed": sp6_passed,
                "size": size,
                "details": f"Output file exists ({size} bytes)"
                           if sp6_passed
                           else f"Output file too small ({size} bytes, min: {MIN_OUTPUT_SIZE})",
            }
            if not sp6_passed:
                blockers.append(
                    f"SP6: Output file too small: {output_path} ({size} bytes)"
                )
        else:
            checks["SP6_output_file_exists"] = {
                "passed": False,
                "details": f"Output file not found: {full_path}",
            }
            blockers.append(
                f"SP6: Output file not found on disk: {output_path}"
            )
    else:
        checks["SP6_output_file_exists"] = {
            "passed": True,
            "details": "Skipped — output is human approval or not yet registered",
        }

    # -----------------------------------------------------------------------
    # Overall
    # -----------------------------------------------------------------------
    can_progress = len(blockers) == 0

    return {
        "step": step_num,
        "can_progress": can_progress,
        "checks": checks,
        "blockers": blockers,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Step Progression Guard — validates all step obligations before advancing"
    )
    parser.add_argument(
        "--step",
        type=int,
        required=True,
        help="Step number to validate for progression",
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

    result = validate_progression(args.step, project_dir, wf=wf)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["can_progress"] else 1)


if __name__ == "__main__":
    main()
