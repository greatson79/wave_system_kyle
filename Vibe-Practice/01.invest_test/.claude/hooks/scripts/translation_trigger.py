"""
PostToolUse(TaskUpdate) Hook — emit translation signal when a target Step completes.
v3.1 CR-1: TaskCompleted(nonexistent) → PostToolUse(TaskUpdate) replacement.
v3.1 HR-4: Direct use of task metadata.step (eliminates state.yaml read timing race condition).
No blocking (exit 0). Only outputs translation pending signal.
Orchestrator reads pending file to spawn @translator SubAgent.

InvestScan Infrastructure — Phase B (D7: English-First + Korean Pair)
"""
import json
import sys
import yaml
from pathlib import Path

# Translation target Steps and their source file mappings
TRANSLATION_TARGETS = {
    2: "output/schema-mapping.md",
    4: "output/completion-definition.md",
    5: "output/blueprint.md",
    11: "output/temp/narrative_{date}.json",
    12: "output/reports/weekly-report-{date}.md",
    15: "output/watchlist-{date}.md",          # v3.2 Q5: Watchlist final output
}


def source_file_exists(source: str) -> bool:
    """Check if source file exists. Handles {date} placeholder paths."""
    if "{" not in source:
        return Path(source).exists()
    # {date}-containing path: check via stem prefix matching
    base = source.split("{")[0]
    parent = Path(base).parent
    stem = Path(base).stem
    return parent.exists() and any(
        f.name.startswith(stem) for f in parent.glob("*")
    )


def write_translation_pending(step: int, source: str) -> None:
    """Write translation pending signal to agent-workspace for Orchestrator to detect."""
    pending_file = Path(".claude/agent-workspace/translation-pending.yaml")
    data = {"step": step, "source": source, "action": "create_translation_task"}
    pending_file.write_text(yaml.dump(data))


def run_hook(hook_input: dict) -> int:
    """
    Main hook logic — extracted for testability (coverage tracking).
    Returns exit code: 0 (allow) or 2 (block — not used in this hook).
    Called by __main__ and importable for unit tests.
    """
    # v3.1 CR-1: PostToolUse(TaskUpdate) → verify completed status
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskUpdate":
        return 0

    tool_result = hook_input.get("tool_result", {})
    result_str = (
        json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
    )
    if (
        '"status": "completed"' not in result_str
        and "status: completed" not in result_str
    ):
        return 0

    task_data = hook_input.get("tool_input", {})

    # Skip trigger when the translation Task itself completes (prevent infinite loop)
    if task_data.get("metadata", {}).get("task_type") == "translation":
        return 0

    # v3.1 HR-4: Use metadata.step directly (no state.yaml read)
    # Orchestrator MUST include metadata.step when calling TaskUpdate
    step = task_data.get("metadata", {}).get("step")
    if step is None or step not in TRANSLATION_TARGETS:
        return 0

    source = TRANSLATION_TARGETS[step]
    if not source_file_exists(source):
        return 0

    write_translation_pending(step, source)
    print(
        f"TRANSLATION SIGNAL: Step {step} output ready for translation.\n"
        f"Source: {source}\n"
        f"Action: Orchestrator should spawn @translator SubAgent.\n"
        f"Pending: .claude/agent-workspace/translation-pending.yaml"
    )
    return 0


if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())
    sys.exit(run_hook(hook_input))
