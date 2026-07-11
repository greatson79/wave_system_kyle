#!/usr/bin/env python3
"""Run one local, file-based growth-loop tick for this workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONFIG_FILE = "agent-growth/config.json"
STATE_FILE = "agent-growth/state/state.json"

REQUIRED_FILES = [
    "AGENTS.md",
    "AGENT_WORKFLOWS.md",
    "AGENT_SKILL_INDEX.md",
    "AGENT_GUARDRAILS.md",
    "ARCHITECTURE.md",
    ".codex/harness/safe-development-protocol.md",
    "agent-growth/README.md",
    "agent-growth/loop-spec.md",
    "agent-growth/config.json",
    "agent-growth/state/state.json",
    "agent-growth/memory/MEMORY.md",
    "agent-growth/templates/skill/SKILL.md",
    "agent-growth/gpts/AGENTS.md",
    ".agents/AGENTS.md",
    "templates/gpt-normalization.template.json",
    "templates/skill-publication-review.template.md",
    "agent-growth/skills/harness-first-development/SKILL.md",
]

REQUIRED_DIRS = [
    "agent-growth/inbox",
    "agent-growth/memory",
    "agent-growth/reports",
    "agent-growth/runs",
    "agent-growth/skills",
    "agent-growth/state",
    "agent-growth/templates/skill",
    "agent-growth/gpts/raw",
    "agent-growth/gpts/normalized",
    "agent-growth/gpts/reviews",
    "agent-growth/gpts/publication-queue",
    ".agents/skills",
    "templates",
]

REQUIRED_PATH_KEYS = ("inbox", "memory", "reports", "runs", "skills", "state")
MEMORY_PREFIXES = ("memory", "lesson", "preference", "convention", "workaround")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "unnamed-skill"


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def safe_join(root: Path, value: str) -> Path:
    raw_path = Path(value)
    if raw_path.is_absolute():
        raise ValueError("path must be relative to the workspace root")
    resolved = (root / raw_path).resolve()
    resolved.relative_to(root.resolve())
    return resolved


def config_path(root: Path, config: dict[str, Any], key: str) -> Path:
    paths = config.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("config.paths must be an object")
    value = paths.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"config.paths.{key} must be a non-empty string")
    return safe_join(root, value)


def read_json_for_validation(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        errors.append(f"invalid json: {label}: {exc}")
        return None


def validate_config(root: Path, config: dict[str, Any] | None, errors: list[str]) -> None:
    if config is None:
        return
    if config.get("schema") != "codex-growth-config.v1":
        errors.append("config.schema must be codex-growth-config.v1")

    paths = config.get("paths")
    if not isinstance(paths, dict):
        errors.append("config.paths must be an object")
    else:
        for key in REQUIRED_PATH_KEYS:
            value = paths.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"config.paths.{key} must be a non-empty string")
                continue
            try:
                safe_join(root, value)
            except ValueError as exc:
                errors.append(f"config.paths.{key} is unsafe: {exc}")

    tick = config.get("tick")
    if not isinstance(tick, dict):
        errors.append("config.tick must be an object")
    else:
        for key in ("delete_inbox_after_processing", "write_report", "write_ledger"):
            if not isinstance(tick.get(key), bool):
                errors.append(f"config.tick.{key} must be a boolean")

    curator = config.get("curator")
    if not isinstance(curator, dict):
        errors.append("config.curator must be an object")
    else:
        for key in ("enabled", "archive_enabled"):
            if not isinstance(curator.get(key), bool):
                errors.append(f"config.curator.{key} must be a boolean")
        for key in ("stale_after_days", "archive_after_days"):
            value = curator.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"config.curator.{key} must be a non-negative integer")


def validate_state(state: dict[str, Any] | None, errors: list[str]) -> None:
    if state is None:
        return
    if state.get("schema") != "codex-growth-state.v1":
        errors.append("state.schema must be codex-growth-state.v1")
    if not isinstance(state.get("tick_count"), int) or state.get("tick_count") < 0:
        errors.append("state.tick_count must be a non-negative integer")
    if not isinstance(state.get("processed_notes"), dict):
        errors.append("state.processed_notes must be an object")
    for key in ("last_tick_at", "last_report"):
        value = state.get(key)
        if value is not None and not isinstance(value, str):
            errors.append(f"state.{key} must be null or a string")


def read_frontmatter(skill_file: Path) -> dict[str, str]:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def unique_report_path(reports_dir: Path, timestamp: str) -> Path:
    stem = f"tick-{timestamp.replace(':', '').replace('-', '')}"
    candidate = reports_dir / f"{stem}.md"
    counter = 2
    while candidate.exists():
        candidate = reports_dir / f"{stem}-{counter}.md"
        counter += 1
    return candidate


def parse_note(text: str) -> tuple[list[str], list[str]]:
    memory_items: list[str] = []
    skill_names: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        prefix, value = stripped.split(":", 1)
        key = prefix.strip().lower()
        value = value.strip()
        if not value:
            continue
        if key in MEMORY_PREFIXES:
            memory_items.append(f"{prefix.strip()}: {value}")
        elif key == "skill":
            skill_names.append(value)
    return memory_items, skill_names


def load_config(root: Path) -> dict[str, Any]:
    return read_json(root / CONFIG_FILE)


def load_state(root: Path) -> dict[str, Any]:
    return read_json(root / STATE_FILE)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for item in REQUIRED_FILES:
        if not (root / item).is_file():
            errors.append(f"missing required file: {item}")
    for item in REQUIRED_DIRS:
        if not (root / item).is_dir():
            errors.append(f"missing required directory: {item}")

    config = read_json_for_validation(root / CONFIG_FILE, CONFIG_FILE, errors)
    state = read_json_for_validation(root / STATE_FILE, STATE_FILE, errors)
    validate_config(root, config, errors)
    validate_state(state, errors)

    skills_root = root / "agent-growth/skills"
    if skills_root.exists():
        usage_path = skills_root / ".usage.json"
        read_json_for_validation(usage_path, "agent-growth/skills/.usage.json", errors)
        for skill_file in sorted(skills_root.glob("*/SKILL.md")):
            frontmatter = read_frontmatter(skill_file)
            if not frontmatter:
                errors.append(f"skill missing frontmatter: {rel(skill_file, root)}")
            if not frontmatter.get("name"):
                errors.append(f"skill missing name: {rel(skill_file, root)}")
            if not frontmatter.get("description"):
                errors.append(f"skill missing description: {rel(skill_file, root)}")
    return errors


def create_skill(skills_root: Path, name: str, source: str) -> tuple[str, bool]:
    slug = slugify(name)
    skill_dir = skills_root / slug
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        return slug, False

    title = " ".join(part.capitalize() for part in slug.split("-"))
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        "\n".join(
            [
                "---",
                f"name: {slug}",
                f"description: Agent-created skill draft from {source}.",
                "---",
                "",
                f"# {title}",
                "",
                "## When to Use",
                "",
                "Use this when a future task matches the source note.",
                "",
                "## Procedure",
                "",
                "1. Read the source note and nearby project context.",
                "2. Apply the smallest safe repeatable procedure.",
                "3. Verify the result.",
                "4. Record any refinement in `agent-growth/inbox/`.",
                "",
                "## Verification",
                "",
                "Add concrete verification steps before relying on this skill for production work.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return slug, True


def refresh_usage(root: Path, skills_root: Path, timestamp: str) -> dict[str, Any]:
    usage_path = skills_root / ".usage.json"
    usage: dict[str, Any] = {}
    if usage_path.exists():
        usage = read_json(usage_path)

    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        slug = skill_file.parent.name
        entry = usage.setdefault(slug, {})
        entry.setdefault("created_at", timestamp)
        entry.setdefault("state", "active")
        entry.setdefault("pinned", False)
        entry.setdefault("use_count", 0)
        entry.setdefault("patch_count", 0)
        entry["last_reviewed_at"] = timestamp
        entry["review_count"] = int(entry.get("review_count", 0)) + 1
        entry["path"] = rel(skill_file, root)

    write_json(usage_path, usage)
    return usage


def run_tick(root: Path) -> int:
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"growth-tick: {error}", file=sys.stderr)
        return 1

    config = load_config(root)
    state = load_state(root)
    timestamp = utc_now()
    processed_notes = dict(state.get("processed_notes", {}))

    inbox_dir = config_path(root, config, "inbox")
    memory_path = config_path(root, config, "memory")
    reports_dir = config_path(root, config, "reports")
    runs_dir = config_path(root, config, "runs")
    skills_root = config_path(root, config, "skills")
    state_path = config_path(root, config, "state")

    new_memory: list[tuple[str, str]] = []
    skills_created: list[str] = []
    skills_seen: list[str] = []
    notes_processed: list[str] = []
    notes_skipped: list[str] = []

    for note_path in sorted(inbox_dir.glob("*.md")):
        note_rel = rel(note_path, root)
        digest = file_hash(note_path)
        if processed_notes.get(note_rel) == digest:
            notes_skipped.append(note_rel)
            continue

        text = note_path.read_text(encoding="utf-8")
        memory_items, skill_names = parse_note(text)
        for item in memory_items:
            new_memory.append((note_rel, item))
        for skill_name in skill_names:
            slug, created = create_skill(skills_root, skill_name, note_rel)
            skills_seen.append(slug)
            if created:
                skills_created.append(slug)
        processed_notes[note_rel] = digest
        notes_processed.append(note_rel)

    if new_memory:
        lines = [f"\n## Tick {timestamp}\n"]
        for source, item in new_memory:
            lines.append(f"- {item} (source: {source})\n")
        append_text(memory_path, "".join(lines))

    usage = refresh_usage(root, skills_root, timestamp)

    report_path = unique_report_path(reports_dir, timestamp)
    report = [
        f"# Growth Tick {timestamp}",
        "",
        "## Summary",
        "",
        f"- Notes processed: {len(notes_processed)}",
        f"- Notes skipped as already processed: {len(notes_skipped)}",
        f"- Memory entries added: {len(new_memory)}",
        f"- Skills created: {len(skills_created)}",
        f"- Skills reviewed: {len(usage)}",
        "",
        "## Processed Notes",
        "",
    ]
    report.extend(f"- {item}" for item in notes_processed)
    if not notes_processed:
        report.append("- None")
    report.extend(["", "## Memory Additions", ""])
    report.extend(f"- {item} ({source})" for source, item in new_memory)
    if not new_memory:
        report.append("- None")
    report.extend(["", "## Skill Changes", ""])
    report.extend(f"- Created `{item}`" for item in skills_created)
    existing_seen = [item for item in skills_seen if item not in skills_created]
    report.extend(f"- Preserved existing `{item}`" for item in existing_seen)
    if not skills_created and not existing_seen:
        report.append("- None")
    report.extend(["", "## Curation", ""])
    if config.get("curator", {}).get("archive_enabled"):
        report.append("- Archive mode is enabled. Review `.usage.json` before trusting changes.")
    else:
        report.append("- Archive mode is disabled. No skills were deleted or moved.")
    report.append("")
    report_path.write_text("\n".join(report), encoding="utf-8")

    ledger_entry = {
        "timestamp": timestamp,
        "notes_processed": notes_processed,
        "notes_skipped": notes_skipped,
        "memory_entries_added": len(new_memory),
        "skills_created": skills_created,
        "skills_reviewed": sorted(usage.keys()),
        "report": rel(report_path, root),
    }
    append_text(runs_dir / "ledger.jsonl", json.dumps(ledger_entry, sort_keys=True) + "\n")

    state["tick_count"] = int(state.get("tick_count", 0)) + 1
    state["last_tick_at"] = timestamp
    state["processed_notes"] = processed_notes
    state["last_report"] = rel(report_path, root)
    write_json(state_path, state)

    print(f"growth-tick: ok ({rel(report_path, root)})")
    return 0


def run_check(root: Path) -> int:
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"growth-tick: {error}", file=sys.stderr)
        return 1
    print("growth-tick: check ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="workspace root")
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.check:
        return run_check(root)
    return run_tick(root)


if __name__ == "__main__":
    raise SystemExit(main())
