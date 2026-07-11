"""
PostToolUse(TaskUpdate) Hook — completed Task TDD and translation pACS verification.
v3.1 CR-1: TaskCompleted(nonexistent) → PostToolUse(TaskUpdate) replacement.
           Only process TaskUpdate where status == "completed".
v3.1 CR-2: validate_translation.py does not return pacs_score field.
           → Direct parse from pacs-logs/step-N-translation-pacs.md.
Implementation Task: block if coverage below threshold.
Translation Task: block if pACS RED.

InvestScan Infrastructure — Phase B
"""
import json
import sys
import subprocess
import re
import yaml
from pathlib import Path

# D4 differential coverage thresholds (v3.5 CR-5-1: steeps/stock/validate/citation added)
COVERAGE_TIERS = {
    "p1_critical": {
        # v3.4 H-2/H-3: steeps_classifier + stock_selector promoted (hallucination high-risk)
        "modules": [
            "compliance_filter",
            "synthesize_macro",
            "steeps_classifier",
            "stock_selector",
        ],
        "min_coverage": 95,
    },
    "core_pipeline": {
        # v3.4 H-4/H-5: validate_report_quality + citation_validator promoted
        "modules": [
            "normalizers",
            "intelligence_engine",
            "report_generator",
            "weekly_orchestrator",
            "validate_report_quality",
            "citation_validator",
        ],
        "min_coverage": 90,
    },
    "infrastructure": {
        "modules": [
            "quality_gate_check",
            "tdd_verify",
            "task_schema_check",
            "sot_write_guard",
            "translation_trigger",
        ],
        "min_coverage": 75,
    },
    "standard": {"modules": [], "min_coverage": 85},  # v3.2 Q3: 80→85 (quality absolutism)
}


def get_required_coverage(module: str) -> int:
    """Return required coverage % for the given module."""
    for tier_name, tier in COVERAGE_TIERS.items():
        if tier_name == "standard":
            continue  # standard is the catch-all, skip explicit search
        if module in tier["modules"]:
            return tier["min_coverage"]
    # v3.3 CR-4-2: standard tier is the catch-all default
    return COVERAGE_TIERS["standard"]["min_coverage"]  # 85 (v3.2 Q3)


def extract_module_name(task_data: dict) -> str | None:
    name = task_data.get("name", "").lower()
    m = re.search(r"implement[:\s]+(\w+)(?:\.py)?", name)
    return m.group(1) if m else None


def run_coverage(module: str) -> tuple[bool, int]:
    r = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            f"tests/test_{module}.py",
            f"--cov={module}",
            "--cov-report=term-missing",
            "-q",
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", r.stdout)
    coverage = int(m.group(1)) if m else 0
    required = get_required_coverage(module)
    return r.returncode == 0 and coverage >= required, coverage


# v3.1 CR-2: Parse pACS score directly from pacs-logs file
def get_pacs_score_from_log(step: int) -> int | None:
    """
    Parse pACS score directly from pacs-logs/step-N-translation-pacs.md.
    CR-2: validate_translation.py output has no pacs_score field → direct file parse.
    translator.md §4 format: "Translation pACS = 85 → GREEN"
    """
    log_path = Path(f"pacs-logs/step-{step}-translation-pacs.md")
    if not log_path.exists():
        return None
    content = log_path.read_text()
    m = re.search(r"Translation\s+pACS\s*=\s*(\d+)", content)
    if m:
        return int(m.group(1))
    m = re.search(r"\bpACS\s*=\s*(\d+)", content)
    return int(m.group(1)) if m else None


def handle_translation_task(task_data: dict) -> tuple[bool, str]:
    """Translation Task pACS verification — direct pacs-logs parse (CR-2)."""
    step = task_data.get("metadata", {}).get("step")
    if step is None:
        return False, "Translation task missing 'step' in metadata"

    pacs = get_pacs_score_from_log(step)

    if pacs is None:
        # No pacs-logs file → fallback to validate_translation.py T1-T7 checks
        r = subprocess.run(
            [
                "python3",
                ".claude/hooks/scripts/validate_translation.py",
                "--step",
                str(step),
                "--check-pacs",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            data = json.loads(r.stdout)
            if not data.get("pacs_arithmetic_valid", True):
                return False, f"pACS arithmetic invalid at step {step}"
            return True, f"Step {step}: pACS log not found — T1-T7 only"
        except json.JSONDecodeError:
            return False, "validate_translation.py returned invalid JSON"

    grade = "GREEN" if pacs >= 70 else ("YELLOW" if pacs >= 50 else "RED")
    _update_translation_workspace(step, pacs, grade)

    if pacs < 50:
        return False, f"Translation pACS {pacs} = RED. Re-translate step {step}."
    return True, f"Translation pACS {pacs} = {grade}"


def _update_translation_workspace(step: int, pacs: int, grade: str) -> None:
    ws = Path(".claude/agent-workspace/translator.yaml")
    if ws.exists():
        data = yaml.safe_load(ws.read_text()) or {}
        for t in data.get("translations", []):
            if t.get("step") == step:
                t.update({"pacs_score": pacs, "pacs_grade": grade})
        ws.write_text(yaml.dump(data))


if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())

    # InvestScan-specific guard: only run if tdd_status exists in state
    _state_path = Path(".claude/state.yaml")
    if _state_path.exists():
        import yaml as _yaml
        _st = _yaml.safe_load(_state_path.read_text()) or {}
        if not _st.get("tdd_status"):
            sys.exit(0)
    else:
        sys.exit(0)

    # v3.1 CR-1: PostToolUse(TaskUpdate) → process only status == "completed"
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskUpdate":
        sys.exit(0)

    tool_result = hook_input.get("tool_result", {})
    result_str = (
        json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
    )
    if (
        '"status": "completed"' not in result_str
        and "status: completed" not in result_str
    ):
        sys.exit(0)

    task_data = hook_input.get("tool_input", {})

    # Translation Task branch (D7)
    if task_data.get("metadata", {}).get("task_type") == "translation":
        passed, msg = handle_translation_task(task_data)
        if not passed:
            print(f"TRANSLATION BLOCKED: {msg}", file=sys.stderr)
            sys.exit(2)
        print(f"TRANSLATION VERIFIED: {msg}")
        sys.exit(0)

    # Implementation Task branch
    module = extract_module_name(task_data)
    if not module:
        sys.exit(0)

    test_file = Path(f"tests/test_{module}.py")
    if not test_file.exists():
        print(
            f"TDD BLOCKED: tests/test_{module}.py not found. Write tests first.",
            file=sys.stderr,
        )
        sys.exit(2)

    passed, coverage = run_coverage(module)
    if not passed:
        required = get_required_coverage(module)
        print(
            f"TDD BLOCKED: {module}.py coverage {coverage}% < required {required}%.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)
