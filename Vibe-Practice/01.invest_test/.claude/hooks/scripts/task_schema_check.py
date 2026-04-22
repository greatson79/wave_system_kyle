"""
PostToolUse(TaskCreate) Hook — implementation Tasks require test_spec.
v3.1 CR-1: TaskCreated(nonexistent) → PostToolUse(TaskCreate) replacement.
           Extract task data from hook_input.tool_input.
Translation Tasks (task_type == "translation") are exempt from test_spec requirement.

InvestScan Infrastructure — Phase B
"""
import json
import sys
import re

IMPL_KEYWORDS = re.compile(
    r"\b(implement|build|create module|write module|code)\b", re.IGNORECASE
)

if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())

    # InvestScan-specific guard: only enforce test_spec if tdd_status exists in state
    import os
    _state_path = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude/state.yaml")
    if not os.path.exists(_state_path):
        sys.exit(0)
    try:
        import yaml as _yaml
        _st = _yaml.safe_load(open(_state_path).read()) or {}
        if not _st.get("tdd_status"):
            sys.exit(0)
    except Exception:
        sys.exit(0)

    # v3.1 CR-1: PostToolUse(TaskCreate) → extract task data from tool_input
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskCreate":
        sys.exit(0)

    task = hook_input.get("tool_input", {})
    name = task.get("name", "")
    desc = task.get("description", "")
    metadata = task.get("metadata", {})

    # D7: Translation Tasks are exempt from test_spec requirement
    if metadata.get("task_type") == "translation":
        sys.exit(0)

    is_impl = bool(IMPL_KEYWORDS.search(name) or IMPL_KEYWORDS.search(desc))
    has_test_spec = bool(metadata.get("test_spec") or "test_spec" in desc)

    if is_impl and not has_test_spec:
        print(
            f"TDD GATE: Implementation task '{name}' requires 'test_spec'.\n"
            f"Add test_spec to metadata before creating this task.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)
