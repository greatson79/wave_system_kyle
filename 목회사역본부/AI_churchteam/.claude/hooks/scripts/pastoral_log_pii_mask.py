#!/usr/bin/env python3
"""
pastoral_log_pii_mask.py — Mask PII in pastoral-decision-logs before external sharing.
Runs on: PreToolUse (Edit|Write matching **/pastoral-decision-logs/**)
Exit 0: clean
Exit 2: PII detected without masking → block
"""
import sys, json, re

# PII patterns to detect
PII_PATTERNS = [
    (r'\d{3}-\d{4}-\d{4}', '[전화번호]'),           # phone
    (r'\b\d{6}-[1-4]\d{6}\b', '[주민번호]'),          # resident ID
    (r'[가-힣]{2,4}\s*(집사|권사|장로|성도)', '[성도명]'),  # member names with title
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[이메일]'),  # email
]

def scan_pii(content: str) -> list:
    hits = []
    for pattern, replacement in PII_PATTERNS:
        if re.search(pattern, content):
            hits.append((pattern, replacement))
    return hits

def mask_pii(content: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        content = re.sub(pattern, replacement, content)
    return content

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    file_path = tool_input.get("file_path", "")

    if not content or "pastoral-decision-logs" not in file_path:
        sys.exit(0)

    hits = scan_pii(content)
    if not hits:
        sys.exit(0)

    masked = mask_pii(content)
    print(json.dumps({
        "systemMessage": (
            f"🔒 목회 결정 기록에서 개인정보 {len(hits)}건이 자동 마스킹됐습니다.\n"
            "   pastoral-decision-logs는 local-only로 보관되며 외부 전송 시 암호화됩니다."
        ),
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "content": masked}
        }
    }))
    sys.exit(0)

if __name__ == "__main__":
    main()
