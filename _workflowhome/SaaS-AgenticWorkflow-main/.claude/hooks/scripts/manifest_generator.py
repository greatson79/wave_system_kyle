#!/usr/bin/env python3
"""
Manifest Generator — manifest_generator.py

Generates a manifest.md file for team steps (2, 9) that lists all sub-outputs.
The manifest file becomes the single SOT entry for the team step, avoiding
SOT list/sub-key incompatibility.

Usage:
    python3 manifest_generator.py --step N --project-dir . --files "path1,path2,path3"

Output (JSON stdout):
    {
        "manifest_path": "prompt/research/step-2-manifest.md",
        "valid": true,
        "files_verified": 3,
        "total_bytes": 15432
    }

Exit codes:
    0 — success (manifest created, all files verified)
    1 — one or more files missing/empty or argument error

P1 Compliance: Deterministic — file stat + template generation.
SOT Compliance: Does NOT write to SOT. Writes manifest file only.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Add script directory to path for shared library import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _workflow_registry import get_workflow, VALID_PHASES, DEFAULT_PHASE
from _context_lib import atomic_write


def generate_manifest(step_num, project_dir, file_paths, wf=None):
    """Generate manifest.md for a team step.

    Args:
        step_num: Step number (typically 2 or 9 for Phase 1, various for Phase 2)
        project_dir: Project root directory
        file_paths: List of sub-output file paths (relative to project_dir)
        wf: Workflow module (None → Phase 1 default for backwards compat).

    Returns:
        dict with manifest_path, valid, files_verified, total_bytes
    """
    if wf is None:
        wf = get_workflow(DEFAULT_PHASE)

    dag = wf.DAG
    step_output_dirs = wf.STEP_OUTPUT_DIRS

    if step_num not in dag:
        return {
            "manifest_path": "",
            "valid": False,
            "files_verified": 0,
            "total_bytes": 0,
            "errors": [f"Step {step_num} not found in DAG"],
        }

    step_info = dag[step_num]
    output_dir = step_output_dirs.get(step_num, "prompt")
    manifest_filename = f"step-{step_num}-manifest.md"
    manifest_rel_path = os.path.join(output_dir, manifest_filename)
    manifest_abs_path = os.path.join(project_dir, manifest_rel_path)

    # Verify each file
    verified_files = []
    errors = []
    total_bytes = 0

    for fpath in file_paths:
        abs_path = (
            os.path.join(project_dir, fpath)
            if not os.path.isabs(fpath)
            else fpath
        )
        if not os.path.exists(abs_path):
            errors.append(f"File not found: {fpath}")
            continue

        size = os.path.getsize(abs_path)
        if size < 100:
            errors.append(f"File too small ({size} bytes): {fpath}")
            continue

        mtime = os.path.getmtime(abs_path)
        created = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
        verified_files.append({
            "path": fpath,
            "size": size,
            "created": created,
        })
        total_bytes += size

    if errors:
        return {
            "manifest_path": manifest_rel_path,
            "valid": False,
            "files_verified": len(verified_files),
            "total_bytes": total_bytes,
            "errors": errors,
        }

    # Generate manifest content
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        f"# Step {step_num} Manifest — {step_info['name']}",
        "",
        f"Generated: {now}",
        f"Team: {step_info.get('team', 'N/A')}",
        "",
        "## Sub-outputs",
        "",
    ]

    for vf in verified_files:
        lines.append(
            f"- `{vf['path']}` (size: {vf['size']:,} bytes, modified: {vf['created']})"
        )

    lines.extend([
        "",
        "## Summary",
        "",
        f"Total: {len(verified_files)} files, {total_bytes:,} total bytes",
        "",
    ])

    content = "\n".join(lines)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(manifest_abs_path), exist_ok=True)

    # Write manifest file (NOT SOT — just a regular file)
    atomic_write(manifest_abs_path, content)

    return {
        "manifest_path": manifest_rel_path,
        "valid": True,
        "files_verified": len(verified_files),
        "total_bytes": total_bytes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Manifest Generator — team step sub-output manifest"
    )
    parser.add_argument(
        "--step",
        type=int,
        required=True,
        help="Step number (typically 2 or 9)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--files",
        type=str,
        required=True,
        help="Comma-separated list of sub-output file paths",
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
    file_paths = [f.strip() for f in args.files.split(",") if f.strip()]
    wf = get_workflow(args.workflow)

    if not file_paths:
        result = {
            "manifest_path": "",
            "valid": False,
            "files_verified": 0,
            "total_bytes": 0,
            "errors": ["No files specified"],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = generate_manifest(args.step, project_dir, file_paths, wf=wf)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
