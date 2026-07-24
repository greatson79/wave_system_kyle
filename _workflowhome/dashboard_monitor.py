#!/usr/bin/env python3
"""
Master Workflow Dashboard Monitor
3개 워크플로우 실시간 상태 모니터링 + 승인 필요 시 알림
"""

import subprocess, json, time, os, sys
from datetime import datetime

CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"
WF_BASE = "/Users/kylechoi/Desktop/ai_works/Vibe-Practice"

WORKFLOWS = {
    "surface:2": {
        "name": "🌍 환경스캐닝",
        "short": "EnvScan",
        "dir": f"{WF_BASE}/EnvironmentScan-system-main-v4-main",
        "approve_cmd": "/env-scan:approve",
        "status_cmd": "/env-scan:status",
    },
    "surface:3": {
        "name": "📰 글로벌뉴스 크롤링",
        "short": "GlobalNews",
        "dir": f"{WF_BASE}/GlobalNews-Crawling-AgenticWorkflow",
        "approve_cmd": "승인",
        "status_cmd": "현재 상태를 알려줘",
    },
    "surface:4": {
        "name": "📈 투자분석",
        "short": "InvestScan",
        "dir": f"{WF_BASE}/01.invest_test",
        "approve_cmd": "승인",
        "status_cmd": "현재 상태를 알려줘",
    },
}

# pane title 기반 상태 추론
STATUS_MAP = {
    "✳": ("🟢 실행 중", False),
    "⠂": ("🟡 처리 중", False),
    "⠐": ("🟡 처리 중", False),
    "⠁": ("🟡 처리 중", False),
    "⣿": ("🟡 처리 중", False),
    "⠿": ("🟡 처리 중", False),
}

# 승인 필요 키워드 (pane title에서 감지)
APPROVAL_KEYWORDS = [
    "approve", "승인", "review", "checkpoint",
    "human", "waiting", "approval", "confirm",
    "검토", "확인", "대기", "인터랙티브"
]

# 완료 키워드
DONE_KEYWORDS = ["complete", "완료", "done", "finished", "generated"]

def get_tree():
    try:
        result = subprocess.run(
            [CMUX, "tree", "--all"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except Exception:
        return ""

def parse_pane_titles(tree_output):
    titles = {}
    for line in tree_output.splitlines():
        for surface_id in WORKFLOWS:
            if surface_id in line:
                # title 추출: "surface:X [terminal] "TITLE"" 패턴
                if '"' in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        titles[surface_id] = parts[1]
    return titles

def infer_status(title: str, surface_id: str):
    title_lower = title.lower()

    # 완료 감지
    for kw in DONE_KEYWORDS:
        if kw in title_lower:
            return "✅ 완료", False

    # 승인 필요 감지
    for kw in APPROVAL_KEYWORDS:
        if kw in title_lower:
            return "🔴 승인 필요", True

    # spinner로 상태 감지
    for spinner, (status, needs_approval) in STATUS_MAP.items():
        if title.startswith(spinner):
            return status, needs_approval

    # 기본
    if title.strip():
        return "🟡 처리 중", False
    return "⚪ 대기", False

def notify_mac(title, message):
    """macOS 알림 전송"""
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(["osascript", "-e", script], timeout=3)
    except Exception:
        pass

def clear():
    os.system("clear")

def render_dashboard(titles, prev_approval_state):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    needs_approval_any = False
    approval_surfaces = []

    clear()
    print("=" * 60)
    print("  🎛️  MASTER WORKFLOW DASHBOARD")
    print(f"  업데이트: {now}")
    print("=" * 60)

    for surface_id, wf in WORKFLOWS.items():
        title = titles.get(surface_id, "(연결 없음)")
        status, needs_approval = infer_status(title, surface_id)

        print(f"\n  {wf['name']}")
        print(f"  {'─' * 50}")
        print(f"  상태: {status}")
        print(f"  진행: {title[:50]}")

        if needs_approval:
            print(f"  ⚠️  → 승인 대기 중! 승인하려면: [{surface_id}] 입력")
            needs_approval_any = True
            approval_surfaces.append(surface_id)

    print("\n" + "=" * 60)

    if needs_approval_any:
        print("\n  🔔 승인이 필요한 워크플로우:")
        for s in approval_surfaces:
            print(f"     • {WORKFLOWS[s]['name']} [{s}]")
        print("\n  명령: 'approve <surface_id>' 또는 'a<숫자>' 입력")
        print("  예시: 'a2' → surface:2 승인")

        # 처음 승인 상태 진입 시 macOS 알림
        for s in approval_surfaces:
            if not prev_approval_state.get(s):
                notify_mac(
                    "승인 필요",
                    f"{WORKFLOWS[s]['name']} 워크플로우가 승인을 기다리고 있습니다."
                )
                prev_approval_state[s] = True
    else:
        # 승인 상태 해제
        for s in list(prev_approval_state.keys()):
            prev_approval_state[s] = False

    print("\n  [q] 종료  [r] 새로고침  [a2/a3/a4] 해당 워크플로우 승인")
    print("=" * 60)

    return prev_approval_state, needs_approval_any

def send_approval(surface_id):
    wf = WORKFLOWS.get(surface_id)
    if not wf:
        print(f"  ❌ 알 수 없는 surface: {surface_id}")
        return
    cmd = wf["approve_cmd"]
    result = subprocess.run(
        [CMUX, "send", "--surface", surface_id, f"{cmd}\n"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        print(f"  ✅ {wf['name']} 승인 전송 완료")
    else:
        print(f"  ❌ 승인 전송 실패: {result.stderr}")

def main():
    import select

    prev_approval_state = {}
    interval = 10  # 10초마다 갱신

    print("대시보드 시작 중...")

    # stdin non-blocking 설정
    import termios, tty
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        tty.setcbreak(sys.stdin.fileno())
        input_buf = ""
        last_render = 0

        while True:
            now = time.time()

            # 주기적 렌더링
            if now - last_render >= interval:
                tree = get_tree()
                titles = parse_pane_titles(tree)
                prev_approval_state, _ = render_dashboard(titles, prev_approval_state)
                last_render = now

            # 키 입력 체크 (non-blocking)
            if select.select([sys.stdin], [], [], 0.5)[0]:
                ch = sys.stdin.read(1)

                if ch == 'q':
                    clear()
                    print("대시보드 종료.")
                    break
                elif ch == 'r':
                    last_render = 0  # 즉시 새로고침
                elif ch in ('a', 'A'):
                    input_buf = ch
                elif ch.isdigit() and input_buf.startswith('a'):
                    num = ch
                    surface_id = f"surface:{num}"
                    if surface_id in WORKFLOWS:
                        send_approval(surface_id)
                        time.sleep(1)
                        last_render = 0
                    input_buf = ""
                else:
                    input_buf = ""

    except KeyboardInterrupt:
        clear()
        print("대시보드 종료.")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
