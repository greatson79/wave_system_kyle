#!/usr/bin/env python3
"""
L1 Document Gate — validate_l1_document.py

Structural L1 verification for document-type step outputs.
Replaces the previous auto-pass ("L1 performed by orchestrator LLM") with
deterministic structural checks that catch empty shells, placeholder outputs,
and low-effort hallucinated documents.

This does NOT replace semantic judgment — it catches structural deficiencies
that a deterministic script CAN verify. Semantic quality is evaluated by
L1.5 (pACS self-assessment) and L2 (adversarial review).

Usage:
    python3 validate_l1_document.py --step N --project-dir . --output-path PATH
    python3 validate_l1_document.py --step 3 --project-dir . --output-path prompt/research/synthesis-and-gaps.md

Output (JSON stdout):
    {
        "passed": true,
        "checks": {
            "D1_sections": {"passed": true, "found": 8, "minimum": 3, "details": "..."},
            "D2_content_depth": {"passed": true, "avg_bytes": 1200, "min_threshold": 200},
            "D3_input_references": {"passed": true, "rate": 0.8, "threshold": 0.3},
            "D4_trace_markers": {"passed": true, "count": 5},
            "D5_pacs_section": {"passed": true}
        },
        "warnings": []
    }

Exit codes:
    0 — all checks passed
    1 — one or more checks failed

Checks:
    D1: Section count — document has ≥ MIN_SECTIONS headings (##/###)
    D2: Content depth — average section length ≥ MIN_AVG_SECTION_BYTES
    D3: Input reference density — fraction of input filenames referenced in output
    D4: Trace markers — [trace:step-N] markers present (if deps exist)
    D5: pACS section — pACS self-assessment block present

P1 Compliance: Deterministic — regex + byte counting + file existence.
SOT Compliance: Read-only — reads output file and DAG, never modifies.
"""

import argparse
import json
import os
import re
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE

# ---------------------------------------------------------------------------
# Thresholds — tuned for quality (절대 기준 1)
# ---------------------------------------------------------------------------
MIN_SECTIONS = 3           # D1: minimum ## or ### headings
MIN_AVG_SECTION_BYTES = 200  # D2: average bytes per section (excludes headings)
MIN_INPUT_REF_RATE = 0.3   # D3: fraction of input files referenced (0.0-1.0)
MIN_TRACE_MARKERS = 1      # D4: minimum [trace:step-N] markers (if step has deps)

# ---------------------------------------------------------------------------
# Regex patterns (pre-compiled for P1 compliance)
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r'^#{1,3}\s+.+', re.MULTILINE)
_SECTION_SPLIT_RE = re.compile(r'^#{1,3}\s+', re.MULTILINE)
_TRACE_RE = re.compile(r'\[trace:step-\d+\]', re.IGNORECASE)
_PACS_SECTION_RE = re.compile(
    r'(##\s*pACS|##\s*Self[- ]Assessment|##\s*자체\s*평가|pACS\s*=\s*min)',
    re.IGNORECASE,
)
# Match common pACS dimension patterns (F: 85, C: 70, etc.)
_PACS_DIM_RE = re.compile(r'\b[FCLT]\s*[:=]\s*\d{1,3}\b')


def validate_l1_document(output_path, project_dir, step_num, wf=None):
    """Run all D1-D5 structural checks on a document output.

    Args:
        output_path: Path to the step output file (relative or absolute).
        project_dir: Project root directory.
        step_num: Step number (for DAG lookup — deps, inputs).
        wf: Workflow module (None → Phase 1 default).

    Returns:
        dict with passed (bool), checks (dict), warnings (list).
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)

    dag = wf.DAG
    checks = {}
    warnings = []

    # Resolve full path
    full_path = (
        os.path.join(project_dir, output_path)
        if not os.path.isabs(output_path)
        else output_path
    )

    # Read the document
    if not os.path.exists(full_path):
        return {
            "passed": False,
            "checks": {},
            "warnings": [f"Output file not found: {full_path}"],
        }

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "passed": False,
            "checks": {},
            "warnings": [f"Cannot read file: {e}"],
        }

    # -----------------------------------------------------------------------
    # D1: Section count — headings (##, ###)
    # -----------------------------------------------------------------------
    headings = _HEADING_RE.findall(content)
    d1_count = len(headings)
    d1_passed = d1_count >= MIN_SECTIONS
    checks["D1_sections"] = {
        "passed": d1_passed,
        "found": d1_count,
        "minimum": MIN_SECTIONS,
        "details": f"{d1_count} headings found (minimum: {MIN_SECTIONS})",
    }
    if not d1_passed:
        warnings.append(
            f"D1 FAIL: Only {d1_count} section headings "
            f"(minimum {MIN_SECTIONS}). Document may be a stub/placeholder."
        )

    # -----------------------------------------------------------------------
    # D2: Content depth — average section length
    # -----------------------------------------------------------------------
    sections = _SECTION_SPLIT_RE.split(content)
    # Filter out empty sections and the preamble (before first heading)
    section_bodies = [s.strip() for s in sections[1:] if s.strip()]
    if section_bodies:
        avg_bytes = sum(len(s.encode("utf-8")) for s in section_bodies) // len(
            section_bodies
        )
    else:
        avg_bytes = 0

    d2_passed = avg_bytes >= MIN_AVG_SECTION_BYTES
    checks["D2_content_depth"] = {
        "passed": d2_passed,
        "avg_bytes": avg_bytes,
        "min_threshold": MIN_AVG_SECTION_BYTES,
        "section_count": len(section_bodies),
        "details": f"Average section: {avg_bytes} bytes "
                   f"(minimum: {MIN_AVG_SECTION_BYTES})",
    }
    if not d2_passed:
        warnings.append(
            f"D2 FAIL: Average section length {avg_bytes} bytes "
            f"(minimum {MIN_AVG_SECTION_BYTES}). Sections may lack substance."
        )

    # -----------------------------------------------------------------------
    # D3: Input reference density
    # -----------------------------------------------------------------------
    # STEP_INPUTS is co-located with DAG in both Phase 1 and Phase 2 modules
    step_inputs_map = getattr(wf, "STEP_INPUTS", {}) or {}

    input_files = step_inputs_map.get(step_num, [])
    if input_files:
        referenced = 0
        for inp in input_files:
            # Extract just the filename for matching
            fname = os.path.basename(inp)
            # Also try the full relative path
            if fname in content or inp in content:
                referenced += 1
        ref_rate = referenced / len(input_files)
        d3_passed = ref_rate >= MIN_INPUT_REF_RATE
        checks["D3_input_references"] = {
            "passed": d3_passed,
            "rate": round(ref_rate, 2),
            "threshold": MIN_INPUT_REF_RATE,
            "referenced": referenced,
            "total_inputs": len(input_files),
            "details": f"{referenced}/{len(input_files)} input files referenced "
                       f"(rate: {ref_rate:.0%}, threshold: {MIN_INPUT_REF_RATE:.0%})",
        }
        if not d3_passed:
            unreferenced = [
                os.path.basename(inp) for inp in input_files
                if os.path.basename(inp) not in content and inp not in content
            ]
            warnings.append(
                f"D3 FAIL: Only {ref_rate:.0%} of input files referenced "
                f"(threshold: {MIN_INPUT_REF_RATE:.0%}). "
                f"Unreferenced: {unreferenced[:3]}"
            )
    else:
        # No known inputs — skip check
        checks["D3_input_references"] = {
            "passed": True,
            "rate": None,
            "threshold": MIN_INPUT_REF_RATE,
            "details": "Skipped — no input files defined for this step",
        }

    # -----------------------------------------------------------------------
    # D4: Trace markers — [trace:step-N]
    # -----------------------------------------------------------------------
    step_info = dag.get(step_num, {})
    deps = step_info.get("deps", [])
    trace_matches = _TRACE_RE.findall(content)
    d4_count = len(trace_matches)

    if deps:
        d4_passed = d4_count >= MIN_TRACE_MARKERS
        checks["D4_trace_markers"] = {
            "passed": d4_passed,
            "count": d4_count,
            "minimum": MIN_TRACE_MARKERS,
            "deps": deps,
            "details": f"{d4_count} trace markers found "
                       f"(minimum: {MIN_TRACE_MARKERS} for step with deps {deps})",
        }
        if not d4_passed:
            warnings.append(
                f"D4 FAIL: {d4_count} trace markers "
                f"(minimum {MIN_TRACE_MARKERS}). "
                f"Step depends on {deps} but doesn't trace back to them."
            )
    else:
        # Step 1 or steps with no deps — trace check optional
        checks["D4_trace_markers"] = {
            "passed": True,
            "count": d4_count,
            "minimum": 0,
            "details": "Skipped — step has no dependencies",
        }

    # -----------------------------------------------------------------------
    # D5: pACS section presence
    # -----------------------------------------------------------------------
    has_pacs = bool(_PACS_SECTION_RE.search(content))
    has_dims = len(_PACS_DIM_RE.findall(content)) >= 2
    d5_passed = has_pacs or has_dims
    checks["D5_pacs_section"] = {
        "passed": d5_passed,
        "has_pacs_heading": has_pacs,
        "has_dimension_scores": has_dims,
        "details": "pACS self-assessment section found" if d5_passed
                   else "No pACS section or dimension scores detected",
    }
    if not d5_passed:
        warnings.append(
            "D5 FAIL: No pACS self-assessment section found. "
            "Agent must include pACS scoring (F, C, L dimensions)."
        )

    # -----------------------------------------------------------------------
    # Overall result
    # -----------------------------------------------------------------------
    all_passed = all(c["passed"] for c in checks.values())

    return {
        "passed": all_passed,
        "checks": checks,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(
        description="L1 Document Gate — structural verification for document outputs"
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
        "--workflow",
        type=str,
        default=DEFAULT_PHASE,
        choices=sorted(VALID_PHASES),
        help=f"Workflow phase (default: {DEFAULT_PHASE})",
    )

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)
    wf = get_workflow(args.workflow)

    result = validate_l1_document(
        args.output_path, project_dir, args.step, wf=wf
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
