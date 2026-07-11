#!/usr/bin/env python3
"""
output_internal_id_filter.py — Strip internal agent IDs from user-visible output.
Runs on: PostToolUse (Edit|Write matching AI_churchteam/output/**)
Exit 0: clean or filtered
Exit 2: unfixable violation
"""
import sys, json, re

# Internal identifiers that must not appear in user-visible text
INTERNAL_PATTERNS = [
    # --- 구 에이전트명 (레거시) ---
    (r'\bphase[12]?-builder\b', '부교역자'),
    (r'\b@?bootstrapper\b', '시스템'),
    (r'\b@?impl-orchestrator\b', '진행자'),
    (r'\b@?planning-orchestrator\b', '기획자'),
    (r'\b@?research-orchestrator\b', '연구자'),
    (r'\b@?weekly-cycle-orchestrator\b', '진행자'),
    (r'\b@?spof-recovery\b', '복구 모듈'),
    (r'\b@?disaster-recovery\b', '복구 모듈'),
    # --- 신규 에이전트명 (1단계 구현) ---
    (r'\b@?intent-interpreter\b', '분석 담당'),
    (r'\b@?task-planner\b', '기획 담당'),
    (r'\b@?team-router\b', '배분 담당'),
    (r'\b@?response-synthesizer\b', '통합 담당'),
    (r'\b@?theology-alignment\b', '신학 검증 담당'),
    (r'\b@?kingdom-vision\b', '비전 담당'),
    (r'\b@?culture-generation-analyst\b', '시대분석 담당'),
    (r'\b@?ai-ministry-innovation\b', '혁신 담당'),
    (r'\b@?scenario-planner\b', '시나리오 담당'),
    (r'\b@?strategy-synthesizer\b', '전략팀장'),
    # --- 사역기획팀 (2단계) ---
    (r'\b@?기획팀장\b', '기획 담당'),
    (r'\b@?주간사역설계관\b', '일정 담당'),
    (r'\b@?메시지정렬관\b', '메시지 담당'),
    # --- 사역실행팀 (3단계) ---
    (r'\b@?실행팀장\b', '실행 총괄'),
    (r'\b@?말씀팀장\b', '말씀 담당'),
    (r'\b@?sermon-structure\b', '설교구조 담당'),
    (r'\b@?gospel-application\b', '적용 담당'),
    (r'\b@?small-group-builder\b', '나눔지 담당'),
    (r'\b@?교육팀장\b', '교육 담당'),
    (r'\b@?student-coaching\b', '청소년 담당'),
    (r'\b@?parent-education\b', '부모교육 담당'),
    (r'\b@?spiritual-growth-tracker\b', '성장 담당'),
    (r'\b@?콘텐츠팀장\b', '콘텐츠 담당'),
    (r'\b@?sns-optimization\b', 'SNS 담당'),
    (r'\b@?storytelling\b', '스토리 담당'),
    (r'\b@?visual-prompt\b', '비주얼 담당'),
    (r'\b@?운영팀장\b', '운영 담당'),
    (r'\b@?document-generator\b', '문서 담당'),
    (r'\b@?data-tracker\b', '데이터 담당'),
    (r'\b@?event-planner\b', '행사 담당'),
    # --- 시스템 메타 정보 ---
    (r'--scope\s+\S+', ''),
    (r'permissionMode:\s*\S+', ''),
    (r'\bsession_id:\s*[\w-]+', ''),
    (r'Tier\s+[012]\b', ''),
]

def filter_content(content: str) -> tuple[str, list]:
    warnings = []
    filtered = content
    for pattern, replacement in INTERNAL_PATTERNS:
        if re.search(pattern, filtered, re.IGNORECASE):
            warnings.append(f"내부 식별자 감지: {pattern}")
            filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)
    return filtered, warnings

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    file_path = tool_input.get("file_path", "")

    if not content or "AI_churchteam/output" not in file_path:
        sys.exit(0)

    filtered, warnings = filter_content(content)

    if warnings:
        print(json.dumps({
            "systemMessage": (
                f"⚠️ 내부 식별자 {len(warnings)}건이 한국어 호칭으로 자동 치환됐습니다.\n"
                + "\n".join(f"   - {w}" for w in warnings[:3])
            ),
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "updatedInput": {**tool_input, "content": filtered}
            }
        }))

    sys.exit(0)

if __name__ == "__main__":
    main()
