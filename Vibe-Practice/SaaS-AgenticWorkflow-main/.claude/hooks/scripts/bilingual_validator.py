#!/usr/bin/env python3
"""
Bilingual Validator — bilingual_validator.py

Validates that EN+KO file pairs exist for a given step.
Checks SOT for step-N (English) and step-N-ko (Korean) entries,
then verifies both files exist and meet minimum size requirements.

Usage:
    python3 bilingual_validator.py --step N --project-dir .

Output (JSON stdout):
    {
        "step": 3,
        "valid": true,
        "en_path": "prompt/research/synthesis-and-gaps.md",
        "ko_path": "prompt/research/synthesis-and-gaps.ko.md",
        "en_size": 5432,
        "ko_size": 4891
    }

Exit codes:
    0 — both files exist and are valid
    1 — one or both files missing/invalid

P1 Compliance: Deterministic — file existence + size check.
SOT Compliance: Read-only access via _read_sot_outputs().
"""

import argparse
import json
import os
import sys

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _context_lib import _read_sot_outputs

# Minimum file size in bytes
MIN_FILE_SIZE = 100


def validate_bilingual(step_num, project_dir):
    """Check EN+KO pair for a step.

    Args:
        step_num: Step number (1-12)
        project_dir: Project root directory

    Returns:
        dict with valid, en_path, ko_path, en_size, ko_size, errors
    """
    outputs = _read_sot_outputs(project_dir)
    en_key = f"step-{step_num}"
    ko_key = f"step-{step_num}-ko"

    errors = []
    en_path = outputs.get(en_key, "")
    ko_path = outputs.get(ko_key, "")

    if not en_path:
        errors.append(f"No EN output in SOT for {en_key}")
    if not ko_path:
        errors.append(f"No KO output in SOT for {ko_key}")

    en_size = 0
    ko_size = 0

    if en_path:
        abs_en = (
            os.path.join(project_dir, en_path)
            if not os.path.isabs(en_path)
            else en_path
        )
        if os.path.exists(abs_en):
            en_size = os.path.getsize(abs_en)
            if en_size < MIN_FILE_SIZE:
                errors.append(
                    f"EN file too small: {en_size} bytes (min {MIN_FILE_SIZE})"
                )
        else:
            errors.append(f"EN file not found: {abs_en}")

    if ko_path:
        abs_ko = (
            os.path.join(project_dir, ko_path)
            if not os.path.isabs(ko_path)
            else ko_path
        )
        if os.path.exists(abs_ko):
            ko_size = os.path.getsize(abs_ko)
            if ko_size < MIN_FILE_SIZE:
                errors.append(
                    f"KO file too small: {ko_size} bytes (min {MIN_FILE_SIZE})"
                )
        else:
            errors.append(f"KO file not found: {abs_ko}")

    return {
        "step": step_num,
        "valid": len(errors) == 0,
        "en_path": en_path,
        "ko_path": ko_path,
        "en_size": en_size,
        "ko_size": ko_size,
        "errors": errors if errors else [],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Bilingual Validator — EN+KO pair existence check"
    )
    parser.add_argument(
        "--step",
        type=int,
        required=True,
        help="Step number to validate (1-12)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)

    result = validate_bilingual(args.step, project_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
