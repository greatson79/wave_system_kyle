"""
Stop Hook — Claude Code 응답 종료 전 품질 상태 검증.
v3.1 CR-1: TeammateIdle(nonexistent) → Stop event replacement.
v3.1 HR-2: Full tests/ run → passing modules only (prevent ImportError for unimplemented modules).
TDD failing or translation RED state → exit 2 to block response.

InvestScan Infrastructure — Phase B (D4 TDD gates + D7 translation gates)
"""
import json
import sys
import subprocess
import yaml
from pathlib import Path


def load_state() -> dict:
    p = Path(".claude/state.yaml")
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def get_failing_modules(state: dict) -> list:
    return [m for m, s in state.get("tdd_status", {}).items() if s == "failing"]


def get_red_translations(state: dict) -> list:
    """Return step keys where pacs_grade == RED."""
    return [
        step
        for step, data in state.get("translations", {}).items()
        if data.get("pacs_grade") == "RED"
    ]


def get_passing_modules(state: dict) -> list:
    """v3.1 HR-2: Return only passing modules to prevent ImportError for unimplemented ones."""
    return [m for m, s in state.get("tdd_status", {}).items() if s == "passing"]


def run_quick_tests(passing_modules: list) -> tuple[bool, str]:
    """Run only passing module test files — avoid Phase C early conflicts."""
    if not passing_modules:
        return True, "No modules passing yet — skip test run"
    test_files = [
        f"tests/test_{m}.py"
        for m in passing_modules
        if Path(f"tests/test_{m}.py").exists()
    ]
    if not test_files:
        return True, "No test files found for passing modules"
    r = subprocess.run(
        [sys.executable, "-m", "pytest"] + test_files + ["-q", "--tb=no", "--no-header"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return r.returncode == 0, r.stdout.strip()[-500:]


if __name__ == "__main__":
    # Stop Hook: session data may arrive via stdin (safe to ignore)
    state = load_state()
    # InvestScan-specific guard: only run if this is an InvestScan project (tdd_status key present)
    if not state.get("tdd_status"):
        sys.exit(0)
    failing = get_failing_modules(state)
    red_translations = get_red_translations(state)

    if failing:
        print(f"QUALITY GATE: TDD failing — {failing}", file=sys.stderr)
        sys.exit(2)

    if red_translations:
        print(
            f"QUALITY GATE: Translation RED (pACS < 50) — {red_translations}\n"
            f"Re-translate before proceeding.",
            file=sys.stderr,
        )
        sys.exit(2)

    passing = get_passing_modules(state)
    ok, output = run_quick_tests(passing)
    if not ok:
        print(f"QUALITY GATE: Tests failing.\n{output}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)
