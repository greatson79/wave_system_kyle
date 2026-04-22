"""
PreToolUse(Edit|Write) Hook — hierarchical SOT write permission check (D1).
v3.1 CR-3:
  (1) env-variable-based Agent ID → unreliable (CLAUDE_AGENT_ID not guaranteed).
      Primary defense: Orchestrator prompt instructs each SubAgent to write to workspace only.
      Secondary defense: this guard (block on clear env-based SubAgent detection).
  (2) Path normalization bug fix:
      lstrip("./") → .resolve() absolute path comparison (prevents path traversal bypass).

ADR-015: sot_write_guard is the secondary defense line.
  SubAgent env var not set → assume Orchestrator and allow (with warning output).
  Primary defense (prompt instruction) handles actual SOT protection.

InvestScan Infrastructure — Phase B
"""
import json
import sys
import os
from pathlib import Path

SOT_FILES = [
    ".claude/state.yaml",
    ".claude/state/phase-research.yaml",
    ".claude/state/phase-planning.yaml",
    ".claude/state/phase-impl.yaml",
]


def get_project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()


def is_sot_file(file_path: str) -> bool:
    """v3.1 CR-3: Path.resolve() absolute path comparison (removes lstrip bug)."""
    root = get_project_root()
    try:
        target = Path(file_path).resolve()
    except Exception:
        return False
    return any((root / sot).resolve() == target for sot in SOT_FILES)


def is_agent_workspace_file(file_path: str) -> bool:
    root = get_project_root()
    try:
        target = Path(file_path).resolve()
        workspace = (root / ".claude/agent-workspace").resolve()
        return str(target).startswith(str(workspace) + "/")
    except Exception:
        return False


def get_agent_id() -> str:
    """Best-effort detection — no env var is guaranteed in SubAgent environment."""
    for var in ["ANTHROPIC_SUBAGENT_ID", "CLAUDE_AGENT_ID", "AGENT_ID"]:
        val = os.environ.get(var, "")
        if val:
            return val
    return "orchestrator"


if __name__ == "__main__":
    tool_input = json.loads(sys.stdin.read())
    file_path = tool_input.get("file_path", "")
    agent_id = get_agent_id()

    # agent-workspace files → always allow
    if is_agent_workspace_file(file_path):
        sys.exit(0)

    # SOT file access detected
    if is_sot_file(file_path):
        is_subagent = any(
            os.environ.get(v, "")
            for v in ["ANTHROPIC_SUBAGENT_ID", "CLAUDE_AGENT_ID"]
        )
        if is_subagent:
            print(
                f"SOT WRITE BLOCKED (SubAgent detected):\n"
                f"  Agent: {agent_id}\n"
                f"  File:  {file_path}\n"
                f"  Fix:   Write to .claude/agent-workspace/{agent_id}.yaml\n"
                f"         Orchestrator merges workspace → SOT.",
                file=sys.stderr,
            )
            sys.exit(2)
        else:
            # No env var = assume Orchestrator → allow (warning only)
            print(
                f"SOT WRITE (Orchestrator assumed): {file_path}\n"
                f"  If this is a SubAgent, set ANTHROPIC_SUBAGENT_ID.",
                file=sys.stderr,
            )
            sys.exit(0)

    sys.exit(0)
