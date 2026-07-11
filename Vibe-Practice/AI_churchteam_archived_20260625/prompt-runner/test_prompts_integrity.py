"""
Prompts integrity test — philosophy-critical.

Verifies the static contract of prompts/ that the pipeline depends on:
- Exactly 144 prompt files numbered 001..144.
- Every file is non-empty UTF-8 text.
- No unsubstituted {{placeholder}} remains (setup-prompts must have run).
- Every file carries the ABSOLUTE ANCHOR marker (workflow philosophy invariant).
- File numbering matches state.total contract (144).

Pure read-only — does NOT touch state.json or any backup. Safe in any environment.
"""

from __future__ import annotations
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
PROMPTS_DIR = ROOT / "prompts"
EXPECTED_TOTAL = 144

PLACEHOLDER_RE = re.compile(r"\{\{[A-Za-z0-9_\-./ ]+\}\}")
ANCHOR_RE = re.compile(r"\[ABSOLUTE ANCHOR\]")


@pytest.fixture(scope="module")
def prompt_files() -> list[Path]:
    files = sorted(PROMPTS_DIR.glob("*.txt"))
    return files


def test_prompt_count_matches_contract(prompt_files):
    assert len(prompt_files) == EXPECTED_TOTAL, (
        f"Expected {EXPECTED_TOTAL} prompts, found {len(prompt_files)}"
    )


def test_prompt_numbering_is_contiguous(prompt_files):
    nums = []
    for p in prompt_files:
        m = re.match(r"^(\d{3})\.txt$", p.name)
        assert m, f"Unexpected filename: {p.name}"
        nums.append(int(m.group(1)))
    assert nums == list(range(1, EXPECTED_TOTAL + 1)), (
        f"Numbering not contiguous 001..{EXPECTED_TOTAL:03d}"
    )


def test_no_unsubstituted_placeholders(prompt_files):
    offenders: list[tuple[str, str]] = []
    for p in prompt_files:
        text = p.read_text(encoding="utf-8")
        for m in PLACEHOLDER_RE.finditer(text):
            offenders.append((p.name, m.group(0)))
    assert not offenders, (
        "Unsubstituted placeholders remain (run setup-prompts):\n"
        + "\n".join(f"  {n}: {ph}" for n, ph in offenders[:20])
    )


def test_absolute_anchor_present_in_workflow_prompts(prompt_files):
    """Workflow prompts (non-/clear) must carry [ABSOLUTE ANCHOR].

    /clear-only files are session resets and legitimately have no anchor.
    """
    missing: list[str] = []
    for p in prompt_files:
        text = p.read_text(encoding="utf-8").strip()
        if text == "/clear":
            continue
        if not ANCHOR_RE.search(text):
            missing.append(p.name)
    assert not missing, f"Missing [ABSOLUTE ANCHOR] in workflow prompts: {missing[:10]}"


def test_files_nonempty_utf8(prompt_files):
    bad: list[str] = []
    for p in prompt_files:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            bad.append(f"{p.name}: not utf-8")
            continue
        if not text.strip():
            bad.append(f"{p.name}: empty")
    assert not bad, "Bad prompt files:\n" + "\n".join(bad)
