#!/usr/bin/env python3
"""
Merge PRD Sections — Step 10 Pre-Processing Script

Merges the 4 section documents produced by prd-generation-team (Step 9)
into a single draft PRD document.

Usage:
    python3 scripts/merge_prd_sections.py \
        --input-dir prompt/implementation/ \
        --output prompt/implementation/prd-merged-draft.md

Input files expected:
    - prd-sections-1-5.md   (Sections 1-5: Foundation & Users)
    - prd-sections-6-8.md   (Sections 6-8: Technical Core)
    - prd-sections-9-12.md  (Sections 9-12: Systems & Quality)
    - prd-sections-13-16.md (Sections 13-16: Business & Appendix)

Output (JSON stdout):
    {
        "output_path": "prompt/implementation/prd-merged-draft.md",
        "total_lines": 2500,
        "total_bytes": 85000,
        "sections_merged": 4,
        "missing_inputs": []
    }

Exit codes:
    0 — success
    1 — one or more input files missing
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Expected input files in order
INPUT_FILES = [
    "prd-sections-1-5.md",
    "prd-sections-6-8.md",
    "prd-sections-9-12.md",
    "prd-sections-13-16.md",
]


def main():
    parser = argparse.ArgumentParser(
        description="Merge PRD section files into a single draft"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing section files",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output merged PRD file path",
    )

    args = parser.parse_args()

    # Check for missing inputs
    missing = []
    found_files = []
    for filename in INPUT_FILES:
        filepath = os.path.join(args.input_dir, filename)
        if not os.path.exists(filepath):
            missing.append(filename)
        else:
            found_files.append(filepath)

    if missing:
        result = {
            "output_path": args.output,
            "total_lines": 0,
            "total_bytes": 0,
            "sections_merged": len(found_files),
            "missing_inputs": missing,
            "error": f"Missing {len(missing)} input files",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Merge files
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    merged_parts = [
        "# Product Requirements Document (PRD)",
        f"# AI Agentic Workflow Automation System — \"SaaS Auto-Builder\"",
        "",
        f"**Merged**: {now}",
        f"**Source**: {len(found_files)} section documents from prd-generation-team",
        "",
        "---",
        "",
    ]

    for filepath in found_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        merged_parts.append(content)
        merged_parts.append("")
        merged_parts.append("---")
        merged_parts.append("")

    merged_content = "\n".join(merged_parts)

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(merged_content)

    total_lines = merged_content.count("\n") + 1
    total_bytes = len(merged_content.encode("utf-8"))

    result = {
        "output_path": args.output,
        "total_lines": total_lines,
        "total_bytes": total_bytes,
        "sections_merged": len(found_files),
        "missing_inputs": [],
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
