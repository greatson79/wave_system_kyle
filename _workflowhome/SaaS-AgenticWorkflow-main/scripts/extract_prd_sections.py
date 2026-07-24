#!/usr/bin/env python3
"""
Extract PRD Sections — Step 1 Pre-Processing Script

Parses coding-resource/PRD.md and extracts each top-level section (## N.)
into separate files for parallel agent analysis.

Also extracts:
  - Code examples (TypeScript/JavaScript blocks)
  - Mermaid diagrams
  - Tables

Usage:
    python3 scripts/extract_prd_sections.py \
        --input coding-resource/PRD.md \
        --output-dir prompt/research/sections/

Output (JSON stdout):
    {
        "sections": [
            {"number": 1, "title": "Executive Summary", "path": "...", "lines": 42},
            ...
        ],
        "code_blocks": 15,
        "mermaid_diagrams": 3,
        "tables": 8,
        "total_sections": 16
    }

Exit codes:
    0 — success
    1 — input file not found or parse error
"""

import argparse
import json
import os
import re
import sys


def extract_sections(content):
    """Parse markdown content into sections by ## N. headings.

    Returns list of dicts: [{number, title, content, lines}, ...]
    """
    sections = []
    # Match ## N. or ## N  patterns (with or without period)
    section_pattern = re.compile(r"^##\s+(\d+)\.\s+(.+)$", re.MULTILINE)

    matches = list(section_pattern.finditer(content))

    for i, match in enumerate(matches):
        section_num = int(match.group(1))
        section_title = match.group(2).strip()
        start = match.start()

        # End at next section or end of file
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)

        section_content = content[start:end].strip()
        line_count = section_content.count("\n") + 1

        sections.append({
            "number": section_num,
            "title": section_title,
            "content": section_content,
            "lines": line_count,
        })

    return sections


def count_elements(content):
    """Count code blocks, mermaid diagrams, and tables in content."""
    code_blocks = len(re.findall(r"```(?:typescript|javascript|tsx?|jsx?)", content, re.IGNORECASE))
    mermaid_diagrams = len(re.findall(r"```mermaid", content, re.IGNORECASE))
    # Count tables by looking for | header | rows followed by | --- | separator
    tables = len(re.findall(r"^\|.+\|$\n^\|[\s\-:]+\|", content, re.MULTILINE))

    return code_blocks, mermaid_diagrams, tables


def main():
    parser = argparse.ArgumentParser(
        description="Extract PRD sections into separate files"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to PRD.md input file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to write extracted section files",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(json.dumps({
            "error": f"Input file not found: {args.input}",
            "sections": [],
            "total_sections": 0,
        }))
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract sections
    sections = extract_sections(content)

    if not sections:
        print(json.dumps({
            "error": "No sections found in input file",
            "sections": [],
            "total_sections": 0,
        }))
        sys.exit(1)

    # Count elements
    code_blocks, mermaid_diagrams, tables = count_elements(content)

    # Write section files
    os.makedirs(args.output_dir, exist_ok=True)
    output_sections = []

    for section in sections:
        filename = f"section-{section['number']:02d}-{_slugify(section['title'])}.md"
        filepath = os.path.join(args.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(section["content"])

        output_sections.append({
            "number": section["number"],
            "title": section["title"],
            "path": filepath,
            "lines": section["lines"],
        })

    # Write full content as reference
    full_path = os.path.join(args.output_dir, "prd-full-reference.md")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    result = {
        "sections": output_sections,
        "code_blocks": code_blocks,
        "mermaid_diagrams": mermaid_diagrams,
        "tables": tables,
        "total_sections": len(sections),
        "full_reference": full_path,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


def _slugify(title):
    """Convert title to filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s]+", "-", slug)
    return slug[:50]  # limit length


if __name__ == "__main__":
    main()
