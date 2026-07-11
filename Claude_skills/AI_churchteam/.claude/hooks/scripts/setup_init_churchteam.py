#!/usr/bin/env python3
"""
setup_init_churchteam.py — churchTeam Bootstrap infrastructure health check.
Runs on: Setup hook (matcher: init)
Exit 0: all checks pass
Exit 2: any check fails → blocks Bootstrap
"""
import sys, os, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PARENT_ROOT = os.path.expanduser("~/Desktop/Ai_works/AgenticWorkflow-Template")
ENVSCAN_ROOT = os.path.expanduser(
    "~/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main")

def check(label, ok, fix=None):
    status = "✅" if ok else "❌"
    print(f"{status} {label}")
    if not ok and fix:
        print(f"   → {fix}")
    return ok

def main():
    print("=" * 55)
    print("  churchTeam Bootstrap — 인프라 사전 검증")
    print("=" * 55)
    results = []

    # 1. Python 3.12+
    ver = sys.version_info
    results.append(check(
        f"Python {ver.major}.{ver.minor}.{ver.micro}",
        ver >= (3, 12),
        "brew install python@3.12 을 터미널에 입력하세요."
    ))

    # 2. 부모 게놈 도달성
    agents_md = os.path.join(PARENT_ROOT, "AGENTS.md")
    results.append(check(
        f"부모 게놈 AGENTS.md",
        os.path.exists(agents_md),
        "AgenticWorkflow-Template/ 경로를 확인하세요."
    ))

    # 3. Lead Orchestrator 팀 5인 존재
    lo_agents = [
        "lead-orchestrator/총괄팀장.md",
        "lead-orchestrator/intent-interpreter.md",
        "lead-orchestrator/task-planner.md",
        "lead-orchestrator/team-router.md",
        "lead-orchestrator/response-synthesizer.md",
    ]
    agents_base = os.path.join(BASE, ".claude", "agents")
    lo_ok = all(os.path.exists(os.path.join(agents_base, a)) for a in lo_agents)
    results.append(check(
        "Lead Orchestrator 팀 5인 존재",
        lo_ok,
        f"{agents_base}/lead-orchestrator/ 폴더를 확인하세요."
    ))

    # 4. 미래목회전략팀 6인 존재
    st_agents = [
        "strategy-team/theology-alignment.md",
        "strategy-team/kingdom-vision.md",
        "strategy-team/culture-generation-analyst.md",
        "strategy-team/ai-ministry-innovation.md",
        "strategy-team/scenario-planner.md",
        "strategy-team/strategy-synthesizer.md",
    ]
    st_ok = all(os.path.exists(os.path.join(agents_base, a)) for a in st_agents)
    results.append(check(
        "미래목회전략팀 6인 존재",
        st_ok,
        f"{agents_base}/strategy-team/ 폴더를 확인하세요."
    ))

    # 4-2. 사역기획팀 3인 존재
    pt_agents = [
        "planning-team/기획팀장.md",
        "planning-team/주간사역설계관.md",
        "planning-team/메시지정렬관.md",
    ]
    pt_ok = all(os.path.exists(os.path.join(agents_base, a)) for a in pt_agents)
    results.append(check(
        "사역기획팀 3인 존재",
        pt_ok,
        f"{agents_base}/planning-team/ 폴더를 확인하세요."
    ))

    # 4-2-2. 사역실행팀 17인 존재
    et_agents = [
        "execution-team/실행팀장.md",
        "execution-team/word-team/말씀팀장.md",
        "execution-team/word-team/sermon-structure.md",
        "execution-team/word-team/gospel-application.md",
        "execution-team/word-team/small-group-builder.md",
        "execution-team/education-team/교육팀장.md",
        "execution-team/education-team/student-coaching.md",
        "execution-team/education-team/parent-education.md",
        "execution-team/education-team/spiritual-growth-tracker.md",
        "execution-team/content-team/콘텐츠팀장.md",
        "execution-team/content-team/sns-optimization.md",
        "execution-team/content-team/storytelling.md",
        "execution-team/content-team/visual-prompt.md",
        "execution-team/operations-team/운영팀장.md",
        "execution-team/operations-team/document-generator.md",
        "execution-team/operations-team/data-tracker.md",
        "execution-team/operations-team/event-planner.md",
    ]
    et_ok = all(os.path.exists(os.path.join(agents_base, a)) for a in et_agents)
    results.append(check(
        "사역실행팀 17인 존재",
        et_ok,
        f"{agents_base}/execution-team/ 폴더를 확인하세요."
    ))

    # 4-3. data 폴더 존재
    data_files = ["data/church-calendar.md", "data/sermon-data.md"]
    data_ok = all(os.path.exists(os.path.join(BASE, f)) for f in data_files)
    results.append(check(
        "data 폴더 기본 파일 존재",
        data_ok,
        "data/ 폴더를 확인하세요."
    ))

    # 4-4. reports 폴더 3종 존재 (비어있어도 폴더 자체는 있어야 함)
    report_dirs = ["reports/strategy", "reports/planning", "reports/alignment-check"]
    for d in report_dirs:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    reports_ok = all(os.path.isdir(os.path.join(BASE, d)) for d in report_dirs)
    results.append(check(
        "reports 폴더 3종 존재 (strategy/planning/alignment-check)",
        reports_ok,
        "reports/ 폴더를 확인하세요."
    ))

    # 5. state.yaml + workflow-state.yaml 존재
    state_path = os.path.join(BASE, ".claude", "state.yaml")
    wf_state_path = os.path.join(BASE, ".claude", "workflow-state.yaml")
    results.append(check(
        "state.yaml ≥ 100B",
        os.path.exists(state_path) and os.path.getsize(state_path) >= 100,
        "state.yaml 을 재생성하세요."
    ))
    results.append(check(
        "workflow-state.yaml 존재",
        os.path.exists(wf_state_path),
        "workflow-state.yaml 을 재생성하세요."
    ))

    # 6. pastor 폴더 3종 존재
    pastor_dirs = ["pastor/philosophy", "pastor/annual-plans", "pastor/reference"]
    pastor_ok = all(os.path.isdir(os.path.join(BASE, d)) for d in pastor_dirs)
    results.append(check(
        "pastor 데이터 폴더 3종 존재",
        pastor_ok,
        "pastor/ 폴더가 없습니다. 구현을 재실행하세요."
    ))

    # 7. 환경스캐닝 도달성
    envscan_ok = os.path.isdir(ENVSCAN_ROOT)
    results.append(check(
        "환경스캐닝 시스템 도달성",
        envscan_ok,
        f"{ENVSCAN_ROOT} 경로를 확인하세요."
    ))

    # 8. runtime 디렉토리 생성
    runtime_dirs = [
        "runtime/verification-logs", "runtime/pacs-logs",
        "runtime/review-logs", "runtime/pastoral-decision-logs",
        "runtime/translations", "runtime/inheritance-manifest",
        "output"
    ]
    for d in runtime_dirs:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    results.append(check("runtime + output 디렉토리 생성", True))

    # 9. Node.js
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        results.append(check(f"Node.js {r.stdout.strip()}", r.returncode == 0,
                             "brew install node 을 입력하세요."))
    except Exception:
        results.append(check("Node.js", False, "brew install node 을 입력하세요."))

    print("=" * 55)
    fails = sum(1 for r in results if not r)
    if fails:
        print(f"\n❌ {fails}개 항목 실패 — Bootstrap 차단")
        print("위 안내에 따라 조치 후 /init 을 다시 실행하세요.")
        sys.exit(2)
    else:
        print(f"\n✅ 전체 {len(results)}개 검증 통과 — Bootstrap 진행 가능")
        sys.exit(0)

if __name__ == "__main__":
    main()
