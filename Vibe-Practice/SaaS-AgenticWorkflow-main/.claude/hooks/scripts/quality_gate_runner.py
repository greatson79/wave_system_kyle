#!/usr/bin/env python3
"""
Quality Gate Runner — quality_gate_runner.py

Executes the quality gate sequence deterministically via subprocess calls.

Phase 1 (document): L0 → L1(D1-D5 structural) → L1.5 → L2 → Translation
Phase 2 (code):     L0 → L1(tsc+eslint)       → L1.5 → L2 → [L3] → Translation
Phase 2 (document): L0 → L1(D1-D5 structural) → L1.5 → L2 → Translation
Human steps:        Skipped entirely (human is the verifier)

The orchestrator calls this AFTER a step output is generated, BEFORE SOT update.
L1 routing is determined by gate_profile: "code" → tsc+eslint, "document" → D1-D5 structural.
L3 (Integration Gate) runs only for steps in L3_STEPS (Phase 2 Step 13).

Usage:
    python3 quality_gate_runner.py --step N --project-dir . --output-path PATH [--skip-review] [--skip-translation]
    python3 quality_gate_runner.py --step 5 --workflow phase2 --project-dir . --output-path src/registries/index.ts

The --output-path is REQUIRED and specifies the step output file to validate.
This avoids the sequencing problem where SOT is updated AFTER quality gates pass.

Output (JSON stdout):
    {
        "step": 3,
        "all_passed": true,
        "gates": {
            "L0": {"passed": true, "details": "..."},
            "L1.5": {"passed": true, "details": "..."},
            "L2": {"passed": true, "skipped": false, "details": "..."},
            "translation": {"passed": true, "skipped": false, "details": "..."}
        }
    }

Exit codes:
    0 — all gates passed (or skipped)
    1 — one or more gates failed

P1 Compliance: Deterministic subprocess invocations.
SOT Compliance: Read-only — reads SOT outputs but does not write.
"""

import argparse
import json
import os
import subprocess
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUBPROCESS_TIMEOUT = 30  # seconds per validator call
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_validator(script_name, args_list, timeout=SUBPROCESS_TIMEOUT):
    """Run a validator script as subprocess. Returns (success, output)."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return False, f"Validator not found: {script_path}"

    cmd = [sys.executable, script_path] + args_list
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=SCRIPTS_DIR,  # subprocess runs from scripts dir; paths are absolute
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s) running {script_name}"
    except Exception as e:
        return False, f"Error running {script_name}: {type(e).__name__}: {e}"


def gate_l0(output_path, project_dir):
    """L0: Anti-Skip Guard — file exists, >= 100 bytes, non-empty.

    Takes the output path directly (not from SOT) to avoid the sequencing
    problem where SOT is updated AFTER quality gates pass.

    Args:
        output_path: Relative or absolute path to the step output file.
        project_dir: Project root directory.

    Returns:
        (passed: bool, details: str)
    """
    if not output_path:
        return False, "No output path provided"

    full_path = (
        os.path.join(project_dir, output_path)
        if not os.path.isabs(output_path)
        else output_path
    )

    if not os.path.exists(full_path):
        return False, f"Output file does not exist: {full_path}"

    size = os.path.getsize(full_path)
    if size < 100:
        return False, f"Output file too small: {size} bytes (minimum 100)"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        return False, f"Cannot read output file: {e}"

    if not content:
        return False, "Output file is empty (whitespace only)"

    return True, f"L0 passed: {full_path} ({size} bytes)"


def gate_l1_code(project_dir):
    """L1 for code steps: tsc --noEmit + ESLint + test file existence.

    Phase 2 code steps use deterministic compilation and linting as L1 gate.
    Three sub-checks run in sequence; first failure stops the gate.

    Sub-checks:
      L1-C1: tsc --noEmit (TypeScript type check)
      L1-C2: eslint --max-warnings 0 (lint quality)
      L1-C3: test file existence (*.test.ts or *.spec.ts)

    Graceful degradation:
      - No tsconfig.json → skip all (project not scaffolded)
      - No eslint → skip L1-C2 (warning only)
      - No test files → warning only (does not fail gate)

    Returns:
        (passed: bool, details: str)
    """
    tsconfig = os.path.join(project_dir, "tsconfig.json")
    if not os.path.exists(tsconfig):
        return True, "L1-code skipped — tsconfig.json not found (project not yet scaffolded)"

    results = []

    # L1-C1: tsc --noEmit
    try:
        tsc = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_dir,
        )
        if tsc.returncode == 0:
            results.append("tsc(0 errors)")
        else:
            errors = tsc.stdout.strip() or tsc.stderr.strip()
            error_lines = [l for l in errors.splitlines() if "error TS" in l]
            return False, f"L1-code FAILED [tsc]: {len(error_lines)} TypeScript errors\n{errors[:500]}"
    except FileNotFoundError:
        results.append("tsc(skipped — npx not available)")
    except subprocess.TimeoutExpired:
        return False, "L1-code FAILED [tsc]: tsc --noEmit timed out (60s)"
    except Exception as e:
        return False, f"L1-code FAILED [tsc]: {type(e).__name__}: {e}"

    # L1-C2: ESLint (advisory — skip if not available)
    try:
        eslint = subprocess.run(
            ["npx", "eslint", ".", "--max-warnings", "0", "--format", "compact"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_dir,
        )
        if eslint.returncode == 0:
            results.append("eslint(0 warnings)")
        else:
            # ESLint failures are advisory — log but don't fail L1
            output = eslint.stdout.strip() or eslint.stderr.strip()
            warn_count = output.count(" Warning ")
            err_count = output.count(" Error ")
            results.append(f"eslint({err_count} errors, {warn_count} warnings)")
            # Only fail on ESLint errors (not warnings)
            if err_count > 0:
                return False, (
                    f"L1-code FAILED [eslint]: {err_count} errors, {warn_count} warnings\n"
                    f"{output[:500]}"
                )
    except FileNotFoundError:
        results.append("eslint(skipped — not installed)")
    except subprocess.TimeoutExpired:
        results.append("eslint(skipped — timeout)")
    except Exception:
        results.append("eslint(skipped — error)")

    # L1-C3: Test file existence check (advisory)
    src_dir = os.path.join(project_dir, "src")
    test_files = []
    if os.path.isdir(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if f.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
                    test_files.append(os.path.join(root, f))

    if test_files:
        results.append(f"tests({len(test_files)} files)")
    elif os.path.isdir(src_dir):
        # src/ exists but no test files — warning
        results.append("tests(0 files — WARNING: no test files in src/)")

    return True, f"L1-code passed: {', '.join(results)}"


def gate_l1_document(output_path, project_dir, step_num, wf=None):
    """L1 for document steps: structural validation (D1-D5).

    Replaces the previous auto-pass with deterministic structural checks.
    Catches empty shells, placeholder outputs, and low-effort documents.

    Returns:
        (passed: bool, details: str)
    """
    workflow_arg = []
    if wf is not None and hasattr(wf, "PHASE_NAME"):
        workflow_arg = ["--workflow", wf.PHASE_NAME]

    success, output = _run_validator(
        "validate_l1_document.py",
        ["--step", str(step_num),
         "--project-dir", project_dir,
         "--output-path", output_path] + workflow_arg,
    )

    if success:
        return True, f"L1-doc passed: structural checks D1-D5 (step {step_num})"

    # Parse JSON output for detailed failure info
    try:
        result = json.loads(output)
        failed_checks = [
            k for k, v in result.get("checks", {}).items()
            if not v.get("passed", True)
        ]
        warnings = result.get("warnings", [])
        detail = "; ".join(warnings[:3]) if warnings else f"Failed: {failed_checks}"
        return False, f"L1-doc FAILED: {detail}"
    except (json.JSONDecodeError, KeyError):
        return False, f"L1-doc FAILED: {output[:300]}"


def gate_l3(step_num, project_dir):
    """L3: Integration Gate — full build + test + E2E (Phase 2 only).

    Only runs for steps in L3_STEPS (typically Step 13: Integration & E2E Testing).
    Executes: npm run build → npm test → npm run test:e2e

    Returns:
        (passed: bool, details: str)
    """
    pkg_json = os.path.join(project_dir, "package.json")
    if not os.path.exists(pkg_json):
        return True, "L3 skipped — package.json not found (project not yet scaffolded)"

    stages = [
        ("build", ["npm", "run", "build"]),
        ("test", ["npm", "test"]),
        ("test:e2e", ["npm", "run", "test:e2e"]),
    ]

    for stage_name, cmd in stages:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_dir,
            )
            if result.returncode != 0:
                output = result.stdout.strip() or result.stderr.strip()
                return False, f"L3 FAILED at '{stage_name}': exit {result.returncode}\n{output[:500]}"
        except FileNotFoundError:
            return True, f"L3 skipped — npm not available for '{stage_name}'"
        except subprocess.TimeoutExpired:
            return False, f"L3 FAILED: '{stage_name}' timed out (120s)"
        except Exception as e:
            return False, f"L3 FAILED at '{stage_name}': {type(e).__name__}: {e}"

    return True, "L3 passed: build + test + test:e2e all succeeded"


def gate_l15(step_num, project_dir):
    """L1.5: pACS validation — checks pacs-logs/step-N-pacs.md exists and is valid."""
    success, output = _run_validator(
        "validate_pacs.py",
        ["--step", str(step_num), "--check-l0",
         "--project-dir", project_dir],
    )
    return success, output


def gate_l2(step_num, project_dir, step_info):
    """L2: Adversarial Review — only for steps with review agent assigned."""
    review_agent = step_info.get("review")
    if not review_agent:
        return True, "L2 skipped — no review agent for this step"

    success, output = _run_validator(
        "validate_review.py",
        ["--step", str(step_num),
         "--project-dir", project_dir],
    )
    return success, output


def gate_translation(step_num, project_dir, step_info):
    """Translation gate — checks translation output exists and is valid."""
    if not step_info.get("translate"):
        return True, "Translation skipped — step not marked for translation"

    success, output = _run_validator(
        "validate_translation.py",
        ["--step", str(step_num), "--check-pacs", "--check-sequence",
         "--project-dir", project_dir],
    )
    return success, output


def run_gates(step_num, project_dir, output_path, skip_review=False, skip_translation=False, wf=None):
    """Execute full gate sequence for a step.

    Gate sequence depends on gate_profile:
      - "document" steps:  L0 → L1(D1-D5 structural) → L1.5 → L2 → Translation
      - "code" steps:      L0 → L1(tsc+eslint)       → L1.5 → L2 → [L3] → Translation
      - Human steps:       Skipped entirely (early return with all_passed=True)

    Args:
        step_num: Step number
        project_dir: Project root directory
        output_path: Path to the step output file (relative or absolute).
                     Passed directly to avoid SOT sequencing issues —
                     SOT is updated AFTER quality gates pass.
        skip_review: Skip L2 adversarial review
        skip_translation: Skip translation validation
        wf: Workflow module (None → Phase 1 default)

    Returns:
        dict with all_passed (bool) and gates details
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)
    dag = wf.DAG

    if step_num not in dag:
        return {
            "step": step_num,
            "all_passed": False,
            "gates": {},
            "error": f"Step {step_num} not found in DAG",
        }

    step_info = dag[step_num]
    gates = {}
    all_passed = True

    # Human steps: skip quality gates when output is human approval marker.
    # Hybrid steps (e.g., Phase 1 Step 12) have human=True but produce real
    # output files — those must go through the full gate sequence.
    if step_info.get("human", False) and output_path == "approved-by-user":
        return {
            "step": step_num,
            "all_passed": True,
            "gates": {},
            "skipped": "Human step — no quality gates required",
        }

    # Determine gate_profile with Phase 1 fallback
    # Phase 2 DAG has explicit gate_profile; Phase 1 DAG does not (all docs)
    gate_profile = step_info.get("gate_profile")
    if gate_profile is None:
        gate_profile = "document"

    # L0: Anti-Skip Guard — uses provided output_path, NOT SOT
    passed, details = gate_l0(output_path, project_dir)
    gates["L0"] = {"passed": passed, "details": details}
    if not passed:
        all_passed = False
        # L0 failure is fatal — don't run subsequent gates
        return {
            "step": step_num,
            "all_passed": False,
            "gates": gates,
        }

    # L1: Verification Gate — route by gate_profile
    if gate_profile == "code":
        # Code steps: deterministic tsc --noEmit
        passed, details = gate_l1_code(project_dir)
        gates["L1"] = {"passed": passed, "details": details}
        if not passed:
            all_passed = False
    else:
        # Document steps: deterministic structural validation (D1-D5)
        passed, details = gate_l1_document(
            output_path, project_dir, step_num, wf
        )
        gates["L1"] = {"passed": passed, "details": details}
        if not passed:
            all_passed = False

    # L1.5: pACS Self-Rating validation
    passed, details = gate_l15(step_num, project_dir)
    gates["L1.5"] = {"passed": passed, "details": details}
    if not passed:
        all_passed = False
        # L1.5 failure: RED (<50) = fatal, YELLOW (50-69) = warning
        # Let orchestrator decide based on score

    # L2: Adversarial Review
    if skip_review:
        gates["L2"] = {"passed": True, "skipped": True, "details": "Skipped by flag"}
    else:
        passed, details = gate_l2(step_num, project_dir, step_info)
        gates["L2"] = {"passed": passed, "skipped": False, "details": details}
        if not passed and step_info.get("review"):
            all_passed = False

    # L3: Integration Gate (Phase 2 only — steps in L3_STEPS)
    l3_steps = getattr(wf, "L3_STEPS", [])
    if step_num in l3_steps:
        passed, details = gate_l3(step_num, project_dir)
        gates["L3"] = {"passed": passed, "skipped": False, "details": details}
        if not passed:
            all_passed = False
    elif l3_steps:
        # Phase 2 but not an L3 step
        gates["L3"] = {"passed": True, "skipped": True, "details": "Not an L3 step"}

    # Translation
    if skip_translation:
        gates["translation"] = {
            "passed": True,
            "skipped": True,
            "details": "Skipped by flag",
        }
    else:
        passed, details = gate_translation(step_num, project_dir, step_info)
        gates["translation"] = {
            "passed": passed,
            "skipped": False,
            "details": details,
        }
        if not passed and step_info.get("translate"):
            all_passed = False

    return {
        "step": step_num,
        "all_passed": all_passed,
        "gates": gates,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Quality Gate Runner — L0→L1→L1.5→L2→[L3]→Translation sequence"
    )
    parser.add_argument(
        "--step",
        type=int,
        required=True,
        help="Step number to validate",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path to the step output file (relative to project-dir or absolute)",
    )
    parser.add_argument(
        "--skip-review",
        action="store_true",
        help="Skip L2 adversarial review gate",
    )
    parser.add_argument(
        "--skip-translation",
        action="store_true",
        help="Skip translation validation gate",
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

    result = run_gates(
        args.step, project_dir, args.output_path,
        args.skip_review, args.skip_translation, wf=wf,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
