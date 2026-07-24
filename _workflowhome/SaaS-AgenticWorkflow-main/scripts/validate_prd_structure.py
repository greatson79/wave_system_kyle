#!/usr/bin/env python3
"""
Validate PRD Structure — Step 10 Post-Processing Script

Validates the merged PRD document for structural completeness:
  - All 16 ## N. headings present
  - TypeScript/JavaScript code blocks with valid syntax markers
  - Mermaid diagram tokens present
  - No TODO/TBD/PLACEHOLDER markers
  - Minimum document size (2500 lines)

Usage:
    python3 scripts/validate_prd_structure.py \
        --input prompt/implementation/prd-validated.md

Output (JSON stdout):
    {
        "valid": true,
        "checks": {
            "headings": {"passed": true, "found": 16, "expected": 16, "missing": []},
            "code_blocks": {"passed": true, "count": 15},
            "mermaid": {"passed": true, "count": 3},
            "no_placeholders": {"passed": true, "found": []},
            "min_lines": {"passed": true, "lines": 2800, "minimum": 2500}
        }
    }

Exit codes:
    0 — all checks pass
    1 — one or more checks fail
"""

import argparse
import json
import os
import re
import sys


EXPECTED_SECTIONS = list(range(1, 17))  # 1-16
MIN_LINES = 2500
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\[INSERT\b", re.IGNORECASE),
]


def validate(content):
    """Run all structural checks on PRD content.

    Returns dict with valid (bool) and checks details.
    """
    checks = {}
    all_passed = True

    # 1. Check for all 16 ## N. headings
    heading_pattern = re.compile(r"^##\s+(\d+)\.\s+", re.MULTILINE)
    found_nums = sorted(set(int(m.group(1)) for m in heading_pattern.finditer(content)))
    missing = [n for n in EXPECTED_SECTIONS if n not in found_nums]
    heading_pass = len(missing) == 0
    checks["headings"] = {
        "passed": heading_pass,
        "found": len(found_nums),
        "expected": len(EXPECTED_SECTIONS),
        "missing": missing,
    }
    if not heading_pass:
        all_passed = False

    # 2. TypeScript/JavaScript code blocks
    code_block_count = len(re.findall(
        r"```(?:typescript|javascript|tsx?|jsx?)\b", content, re.IGNORECASE
    ))
    code_pass = code_block_count > 0
    checks["code_blocks"] = {
        "passed": code_pass,
        "count": code_block_count,
    }
    if not code_pass:
        all_passed = False

    # 3. Mermaid diagrams
    mermaid_count = len(re.findall(r"```mermaid", content, re.IGNORECASE))
    mermaid_pass = mermaid_count > 0
    checks["mermaid"] = {
        "passed": mermaid_pass,
        "count": mermaid_count,
    }
    if not mermaid_pass:
        all_passed = False

    # 4. No placeholder markers
    found_placeholders = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            found_placeholders.append({
                "marker": match.group(),
                "line": line_num,
            })
    placeholder_pass = len(found_placeholders) == 0
    checks["no_placeholders"] = {
        "passed": placeholder_pass,
        "found": found_placeholders[:10],  # limit output
    }
    if not placeholder_pass:
        all_passed = False

    # 5. Minimum lines
    line_count = content.count("\n") + 1
    lines_pass = line_count >= MIN_LINES
    checks["min_lines"] = {
        "passed": lines_pass,
        "lines": line_count,
        "minimum": MIN_LINES,
    }
    if not lines_pass:
        all_passed = False

    return {"valid": all_passed, "checks": checks}


def main():
    parser = argparse.ArgumentParser(
        description="Validate PRD document structural completeness"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to PRD document to validate",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        result = {
            "valid": False,
            "checks": {},
            "error": f"Input file not found: {args.input}",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    result = validate(content)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
