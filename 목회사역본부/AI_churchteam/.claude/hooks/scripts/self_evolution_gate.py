#!/usr/bin/env python3
"""
self_evolution_gate.py — Phase 2 self-evolution gate.
Blocks unauthorized modifications to agent definitions and SOT structure.
Runs on: PreToolUse (Edit|Write matching .claude/agents/** or .claude/skills/**)
Exit 0: allowed
Exit 2: blocked — requires user approval card
"""
import sys, json, re, os

# Frontmatter keys that cannot be changed without ADR
PROTECTED_FRONTMATTER = ["name", "model", "scope", "tools", "permissionMode", "skills"]

# Section headers in agent .md files that cannot be changed without ADR
PROTECTED_SECTIONS = [
    "## 권한 경계", "## 보고선", "## 신학 필터",
    "## RLM Pre-action", "## 운용 원칙"
]

# The 7 "자율 금지" rows from workflow.md §9.4
AUTONOMY_FORBIDDEN = [
    r"theology_filter",
    r"sermon.*signature",
    r"SOT.*단일.*쓰기",
    r"DAG.*변경",
    r"외부.*의존.*추가",
    r"부모.*게놈.*위반",
    r"신학.*필터.*비활성",
]

def check_frontmatter_change(old_content: str, new_content: str) -> list:
    violations = []
    for key in PROTECTED_FRONTMATTER:
        old_val = re.search(rf'^{key}:\s*(.+)$', old_content, re.MULTILINE)
        new_val = re.search(rf'^{key}:\s*(.+)$', new_content, re.MULTILINE)
        if old_val and new_val and old_val.group(1) != new_val.group(1):
            violations.append(f"프론트매터 키 변경: {key}")
    return violations

def check_section_change(new_content: str) -> list:
    violations = []
    for section in PROTECTED_SECTIONS:
        if section in new_content:
            violations.append(f"보호 섹션 포함: {section}")
    return violations

def check_autonomy_forbidden(new_content: str) -> list:
    violations = []
    for pattern in AUTONOMY_FORBIDDEN:
        if re.search(pattern, new_content, re.IGNORECASE):
            violations.append(f"자율 금지 영역: {pattern}")
    return violations

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    new_content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # Only guard agent/skill files in AI_churchteam
    if "AI_churchteam" not in file_path:
        sys.exit(0)
    if not (".claude/agents/" in file_path or ".claude/skills/" in file_path):
        sys.exit(0)

    violations = []

    # Check autonomy forbidden patterns
    violations += check_autonomy_forbidden(new_content)

    if not violations:
        sys.exit(0)

    print(json.dumps({
        "decision": "block",
        "reason": (
            f"🚫 자기 진화 게이트 차단\n"
            f"   위반 항목: {', '.join(violations[:3])}\n"
            f"   변경하려면 ADR 승인 카드를 통과해야 합니다.\n"
            f"   `/팀-결정` 으로 사용자 승인 카드를 발행하세요."
        )
    }))
    sys.exit(2)

if __name__ == "__main__":
    main()
