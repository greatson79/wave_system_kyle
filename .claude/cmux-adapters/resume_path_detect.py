#!/usr/bin/env python3
"""resume_path_detect.py — cmux auto-resume 부활경로 결정론 탐지 (읽기전용·조치無)

배경(2026-07-27 CEO 하달): CSO_DIRECTIVE 0-b "부활 차단 플래그 점검"은 PHOENIX_FORBID_LIVE
(cys 데몬 계열)만 봤다 — 그러나 실측(13:51 기동) 결과 cmux 런타임 자체에 별도의 자동부활 경로가
있음이 드러났다: cmux.app이 quit 후 재기동될 때, 앱이 자체 보관하는 세션 복원 파일
(~/Library/Application Support/cmux/session-com.cmuxterm.app.json)의 각 터미널 패널에 기록된
resumeBinding(approvalPolicy="auto", autoResume=true)을 사람 확인 없이 그대로 재실행한다
(`claude --resume <sessionid> --dangerously-skip-permissions` 등). 이 경로는 PHOENIX_FORBID_LIVE
플래그의 보호범위 밖이다(그 플래그는 cys 데몬의 phoenix 저널만 막는다) — 부활금지 원칙의 별도
사각지대.

이 도구는 그 사각지대를 결정론으로 검출한다. 조치(설정변경·kill·앱재시작)는 하지 않는다 — 발견만.

탐지 2축
  A) 예측적(predictive) — session-com.cmuxterm.app.json을 파싱해 autoResume=true인 패널을
     열거한다. 다음 cmux 재기동 시 자동 재실행될 후보 목록이다.
  B) 소급적(retrospective) — 현재 살아있는 프로세스의 argv에서 --resume/--resume-id 플래그
     또는 `codex resume <id>` 서브커맨드 패턴을 스캔한다. 지금 떠 있는 어떤 노드가 resume
     경로로 기동됐는지(=오늘 그 노드가 auto-resume을 탔을 가능성)를 사후 확인한다.

사용
  resume_path_detect.py            사람이 읽는 리포트 출력, 발견 0건이면 exit 0 / 1건+면 exit 1
  resume_path_detect.py --json     기계가 읽는 JSON 출력(세션시작 점검 자동화용)
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

SESSION_JSON_CANDIDATES = [
    os.path.expanduser(
        "~/Library/Application Support/cmux/session-com.cmuxterm.app.json"
    ),
]

RESUME_ARGV_PATTERNS = [
    re.compile(r"(?:^|\s)--resume(?:=|\s|$)"),
    re.compile(r"(?:^|\s)--resume-id(?:=|\s|$)"),
    re.compile(r"(?:^|/)codex(?:\s+.*)?\s+resume\s+\S+"),
]


def find_session_json():
    for p in SESSION_JSON_CANDIDATES:
        if os.path.isfile(p):
            return p
    return None


def scan_predictive(session_json_path):
    """session 복원 파일에서 autoResume=true 패널 열거."""
    findings = []
    if not session_json_path:
        return findings, "session-com.cmuxterm.app.json 미발견(경로 후보 전부 부재)"
    try:
        with open(session_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return findings, f"파싱 실패: {e}"

    for wi, window in enumerate(data.get("windows", [])):
        for wsi, ws in enumerate(
            window.get("tabManager", {}).get("workspaces", [])
        ):
            for pi, panel in enumerate(ws.get("panels", [])):
                term = panel.get("terminal", {})
                rb = term.get("resumeBinding")
                if not rb:
                    continue
                if rb.get("autoResume") and rb.get("approvalPolicy") == "auto":
                    findings.append(
                        {
                            "window": wi,
                            "workspace": wsi,
                            "panel": pi,
                            "title": panel.get("customTitle") or panel.get("title"),
                            "checkpointId": rb.get("checkpointId"),
                            "cwd": rb.get("cwd"),
                            "kind": rb.get("kind", "claude/terminal"),
                        }
                    )
    return findings, None


def scan_retrospective():
    """현재 살아있는 프로세스 argv에서 resume 플래그/서브커맨드 검출."""
    findings = []
    try:
        out = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,command="],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except Exception as e:
        return findings, f"ps 실행 실패: {e}"

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, ppid, cmd = parts[0], parts[1], parts[2]
        for pat in RESUME_ARGV_PATTERNS:
            if pat.search(cmd):
                findings.append({"pid": pid, "ppid": ppid, "command": cmd[:300]})
                break
    return findings, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    session_json_path = find_session_json()
    predictive, perr = scan_predictive(session_json_path)
    retrospective, rerr = scan_retrospective()

    total = len(predictive) + len(retrospective)
    result = {
        "session_json_path": session_json_path,
        "predictive_autoresume_panels": predictive,
        "predictive_error": perr,
        "retrospective_live_resume_processes": retrospective,
        "retrospective_error": rerr,
        "total_findings": total,
        "verdict": "ANOMALY_FOUND" if total > 0 else "CLEAR",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== cmux 부활경로 결정론 탐지 (읽기전용) ===")
        print(f"session 복원 파일: {session_json_path or '미발견'}")
        if perr:
            print(f"  [예측축 오류] {perr}")
        print(f"\n[A. 예측적] 다음 cmux 재기동 시 자동 resume될 패널: {len(predictive)}건")
        for f in predictive:
            print(
                f"  - {f['title']} (checkpoint={f['checkpointId']}, "
                f"ws{f['workspace']}/panel{f['panel']}, cwd={f['cwd']})"
            )
        if rerr:
            print(f"  [소급축 오류] {rerr}")
        print(f"\n[B. 소급적] 현재 --resume 플래그로 살아있는 프로세스: {len(retrospective)}건")
        for f in retrospective:
            print(f"  - pid={f['pid']} ppid={f['ppid']}: {f['command']}")
        print(f"\nverdict: {result['verdict']} (총 {total}건)")
        print(
            "\n※ 이 도구는 탐지만 한다 — 설정 변경·프로세스 종료·앱 재시작은 하지 않는다."
            " ANOMALY_FOUND면 CEO 보고 대상(조치안은 별도 상신)."
        )

    sys.exit(1 if total > 0 else 0)


if __name__ == "__main__":
    main()
