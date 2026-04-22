#!/usr/bin/env python3
"""
pACS Log P1 Validation — validate_pacs.py

Standalone script called by Orchestrator after pACS scoring completes.
NOT a Hook — manually invoked during workflow execution.

Usage:
    python3 .claude/hooks/scripts/validate_pacs.py --step 3 --project-dir .
    python3 .claude/hooks/scripts/validate_pacs.py --step 3 --type translation --project-dir .
    python3 .claude/hooks/scripts/validate_pacs.py --step 3 --check-l0 --project-dir .

Output: JSON to stdout
    {"valid": true, "warnings": [], ...}

Exit codes:
    0 — validation completed (check "valid" field for result)
    1 — argument error or fatal failure

Checks (PA1-PA4 + T9 + PA7):
    PA1: pACS log file exists
    PA2: Minimum file size (≥ 50 bytes)
    PA3: Dimension scores present (≥ 3 dimensions, each 0-100)
    PA4: Pre-mortem section present (mandatory before scoring)
    PA5/T9: pACS = min(dimensions) arithmetic correctness
           (delegates to verify_pacs_arithmetic → emits "T9 FAIL:" prefix)

Optional:
    PA6: Color zone validation (score vs declared RED/YELLOW/GREEN)
    --check-l0: Also validate step output (L0 Anti-Skip Guard)

P1 Compliance: All validation is deterministic (delegates to _context_lib).
SOT Compliance: Read-only — no file writes.
"""

import argparse
import json
import os
import re
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _context_lib import (
    extract_remediations,
    validate_pacs_output,
    validate_step_output,
)


def _compute_python_pacs(source_path: str, target_path: str, project_dir: str) -> dict | None:
    """
    PA8: Python-First pACS measurement via pacs_calculator.py.
    Imports pacs_calculator directly (no subprocess) — deterministic, zero LLM.

    Returns pACS result dict or None if pacs_calculator unavailable / files missing.
    """
    investscan_dir = os.path.join(project_dir, "investscan")
    if not os.path.isdir(investscan_dir):
        return None

    # Resolve to absolute paths
    src = source_path if os.path.isabs(source_path) else os.path.join(project_dir, source_path)
    tgt = target_path if os.path.isabs(target_path) else os.path.join(project_dir, target_path)
    if not os.path.exists(src) or not os.path.exists(tgt):
        return None

    glossary = os.path.join(project_dir, "translations/glossary.yaml")
    sys.path.insert(0, investscan_dir)
    try:
        import pacs_calculator
        return pacs_calculator.score_from_files(src, tgt, glossary if os.path.exists(glossary) else None)
    except Exception as exc:
        return {"error": str(exc), "pACS": None, "grade": "UNKNOWN"}
    finally:
        # Use remove() instead of pop(0) — safe even if sys.path was modified between insert/finally
        try:
            sys.path.remove(investscan_dir)
        except ValueError:
            pass


def _extract_ai_pacs_from_log(pacs_log_path: str) -> int | None:
    """Extract AI self-reported pACS score from pacs log file."""
    if not os.path.exists(pacs_log_path):
        return None
    content = open(pacs_log_path).read()
    # Matches: "Translation pACS = 82", "pACS = 75", "Reviewer pACS = min(F,C,L) = 80"
    m = re.search(r"pACS\s*(?:=\s*min\([^)]+\))?\s*=\s*(\d+)", content)
    return int(m.group(1)) if m else None


def main():
    parser = argparse.ArgumentParser(
        description="P1 Validation for pACS scoring outputs"
    )
    parser.add_argument(
        "--step", type=int, required=True,
        help="Step number to validate"
    )
    parser.add_argument(
        "--project-dir", type=str, default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--type", type=str, default="general",
        choices=["general", "translation", "review"],
        help="pACS log type (default: general)"
    )
    parser.add_argument(
        "--check-l0", action="store_true",
        help="Also validate step output via L0 Anti-Skip Guard"
    )
    parser.add_argument(
        "--source", type=str, default=None,
        help="(translation only) English source file path — enables PA8 Python pACS verification"
    )
    parser.add_argument(
        "--target", type=str, default=None,
        help="(translation only) Korean translation file path — enables PA8 Python pACS verification"
    )
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    step = args.step

    # Core validation: PA1-PA6
    is_valid, warnings = validate_pacs_output(project_dir, step, pacs_type=args.type)

    # Remediation mapping — OpenAI harness pattern: inject fix instructions
    _REMEDIATIONS = {
        "PA1": f"Generate pACS log: run Pre-mortem Protocol → F/C/L scoring → save to pacs-logs/step-{step}-pacs.md",
        "PA2": "pACS log is too small — include Pre-mortem 3 questions + all dimension scores + pACS = min(F,C,L)",
        "PA3": "Add dimension scores: F (Faithfulness), C (Completeness), L (Lucidity) each 0-100",
        "PA4": "Add Pre-mortem section before scores — answer 3 questions per AGENTS.md §5.4",
        "T9": "Fix pACS arithmetic: pACS must equal min(F, C, L). Recalculate and correct",
        "PA7": f"pACS is RED (< 50) — rework required. Run: python3 .claude/hooks/scripts/validate_retry_budget.py --step {step} --gate pacs --project-dir . --check-and-increment",
        "PA8": f"Python pACS (deterministic) conflicts with AI self-report — re-translate step {step}. Run: python3 investscan/pacs_calculator.py --source <src> --target <tgt>",
        # L0 Anti-Skip Guard remediations (used when --check-l0 is active)
        "L0a": f"Step {step} output file missing — ensure SOT outputs.step-{step} points to an existing file",
        "L0b": f"Step {step} output file too small (< 100 bytes) — produce complete output before advancing",
        "L0c": f"Step {step} output file is empty/whitespace-only — generate substantive content",
    }

    # Build output
    output = {
        "valid": is_valid,
        "step": step,
        "pacs_type": args.type,
        "warnings": list(warnings),
    }

    # PA8: Python-First pACS verification (translation type + source/target provided)
    if args.type == "translation" and args.source and args.target:
        py_result = _compute_python_pacs(args.source, args.target, project_dir)
        if py_result and "error" not in py_result:
            output["python_pacs"] = py_result
            py_score = py_result["pACS"]
            py_grade = py_result["grade"]

            dim_str = f"Ft={py_result['Ft']}, Ct={py_result['Ct']}, Nt={py_result['Nt']}"
            pacs_log = os.path.join(
                project_dir, f"pacs-logs/step-{step}-translation-pacs.md"
            )
            ai_score = _extract_ai_pacs_from_log(pacs_log)

            if py_score < 50:
                # Tier 1 — Hard block: system RED threshold (< 50)
                output["warnings"].append(
                    f"PA8 FAIL: Python pACS = {py_score} (RED, {dim_str}) — "
                    f"translation quality insufficient, re-translate required"
                )
                output["valid"] = False
            elif py_grade == "RED":
                # Tier 2 — Quality RED (50-69): above system block but below pacs_calculator standard
                # Always warn regardless of AI delta — Python confirms quality concern
                output["warnings"].append(
                    f"PA8 WARN: Python pACS = {py_score} (quality RED by pacs_calculator, {dim_str}) — "
                    f"translation below production standard (GREEN requires ≥ 85, YELLOW ≥ 70)"
                )
                # Also check divergence from AI self-report
                if ai_score is not None and abs(py_score - ai_score) > 15:
                    output["warnings"].append(
                        f"PA8 WARN: AI self-report {ai_score} vs Python {py_score} — "
                        f"delta={abs(py_score - ai_score)} suggests inflated self-scoring"
                    )
            else:
                # Tier 3 — YELLOW or GREEN: check divergence only
                if ai_score is not None:
                    delta = abs(py_score - ai_score)
                    if delta > 15:
                        output["warnings"].append(
                            f"PA8 WARN: Python pACS {py_score} ({py_grade}) vs "
                            f"AI self-report {ai_score} — delta={delta} "
                            f"(> 15 threshold) suggests inflated self-scoring"
                        )
        elif py_result and "error" in py_result:
            output["python_pacs_error"] = py_result["error"]

    # Extract remediation for failed checks (P1-B: central function + P1-F: self-check)
    remediations = extract_remediations(output["warnings"], _REMEDIATIONS)
    if remediations:
        output["remediations"] = remediations

    # Optional: L0 Anti-Skip Guard
    if args.check_l0:
        l0_valid, l0_warnings = validate_step_output(project_dir, step)
        output["l0_valid"] = l0_valid
        output["l0_warnings"] = list(l0_warnings)
        if not l0_valid:
            output["valid"] = False
        # L0 remediation extraction (L0a/L0b/L0c keys in _REMEDIATIONS)
        l0_remediations = extract_remediations(l0_warnings, _REMEDIATIONS)
        if l0_remediations:
            existing = output.get("remediations", {})
            existing.update(l0_remediations)
            output["remediations"] = existing

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_output = {
            "valid": False,
            "error": str(e),
            "warnings": [f"Fatal error: {e}"],
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False))
        sys.exit(1)
