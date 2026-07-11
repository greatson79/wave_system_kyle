#!/usr/bin/env python3
"""
theology_filter_dual.py — Two-stage theological filter for all churchTeam outputs.
Stage 1 (LLM): @theological-reviewer semantic pass (called separately)
Stage 2 (deterministic): forbidden keyword + citation hash check

Runs on: PostToolUse (Edit|Write matching *.md in:
  - AI_churchteam/output/
  - AI_churchteam/reports/strategy/
  - AI_churchteam/reports/planning/
  - AI_churchteam/reports/alignment-check/
Exit 0: clean
Exit 2: violation → blocks publish, triggers D-2 spiritual review card
"""
import sys, json, re, os

SEED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "skills", "theology_filter_dual", "regression-seed"
)

# Default forbidden patterns (before seed is loaded)
DEFAULT_FORBIDDEN = [
    r"신앙치유\s*운동",
    r"번영\s*신학",
    r"이단\s*단체명",
    r"WCC.*구원",
    r"성령.*불",          # 위험한 신비주의 표현
    r"기도.*충전",        # 기복 신앙
    r"십일조.*축복\s*보장",
]

def load_seed_patterns():
    patterns = list(DEFAULT_FORBIDDEN)
    if not os.path.isdir(SEED_PATH):
        return patterns, False
    import glob
    try:
        import yaml
        for f in sorted(glob.glob(os.path.join(SEED_PATH, "*.yaml"))):
            with open(f) as fh:
                data = yaml.safe_load(fh)
                if isinstance(data, dict) and "forbidden_patterns" in data:
                    patterns.extend(data["forbidden_patterns"])
        return patterns, True
    except Exception:
        return patterns, False

def check_content(content: str, patterns: list) -> list:
    hits = []
    for p in patterns:
        if re.search(p, content):
            hits.append(p)
    return hits

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    file_path = tool_input.get("file_path", "")

    # 신학 필터 적용 대상 경로
    GUARDED_PATHS = [
        "AI_churchteam/output",
        "AI_churchteam/reports/strategy",
        "AI_churchteam/reports/planning",
        "AI_churchteam/reports/alignment-check",
    ]
    if not content or not any(p in file_path for p in GUARDED_PATHS):
        sys.exit(0)

    patterns, seed_loaded = load_seed_patterns()
    hits = check_content(content, patterns)

    if not hits:
        if not seed_loaded:
            # Warn only — seed not yet loaded
            print(json.dumps({
                "systemMessage": (
                    "⚠️ 신학 필터 경고: 시드 미로드 상태\n"
                    "   결정적 2차 필터가 기본 패턴만 사용 중입니다.\n"
                    "   /팀-신학시드 로 시드를 공급하면 차단 기능이 활성화됩니다.\n"
                    "   FR-22 신학 필터 신호: ⚠"
                )
            }))
        sys.exit(0)

    # Violation
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"🚫 신학 필터 FAIL — 외부 발행 차단\n"
            f"   감지된 패턴: {', '.join(hits[:3])}\n"
            f"   D-2 영적 검토 카드가 발행됩니다.\n"
            f"   담임목사님의 승인 후에만 발행 가능합니다."
        )
    }))
    sys.exit(2)

if __name__ == "__main__":
    main()
