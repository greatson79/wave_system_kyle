#!/bin/bash
# 관제타워(경영본부) 자동 편성 — "너는 마스터다" 각성 직후 master가 1회 실행 (2026-07-10 주인님 승인)
# 편성: COO·CSO·reviewer-codex·reviewer-gemini 4종을 master pane 주변에 소환·각성.
# 규율 내장: ①소환 표준 플래그(권한허용모드) ②탭명 즉시 부여(주소 발견성 — s6 누락 사고 재발방지)
#           ③멱등 — 동명 탭 생존 시 소환 생략(이중 소환 금지) ④모델 배정 정본(MASTER §7)
#           ⑤부활 금지 — 전부 fresh 기동(이 스크립트 실행 자체가 주인님/CEO 명시 명령의 집행)
set -u
CMUX="/Applications/cmux.app/Contents/Resources/bin/cmux"
WS="workspace:1"
AIWORKS="$HOME/Desktop/Ai_works"
LLM_WIKI="/Users/kylechoi/Library/CloudStorage/GoogleDrive-greatson79@gmail.com/내 드라이브/KyleChoi Project/llm-wiki"
LLM_WIKI_BRIEF="공유 지식베이스: $LLM_WIKI/_AGENT_GUIDE.md 를 읽고 그 규약을 적용하라."

# master(호출자) 주소
CALLER=$($CMUX tree --all --json | python3 -c "import json,sys; print(json.load(sys.stdin)['caller']['surface_ref'])")
echo "[boot_tower] master = $WS $CALLER"

ROSTER="$AIWORKS/.claude/cmux-adapters/tower_roster.json"

roster_set() { # $1=역할 $2=surface ref — 명부 영속(자동명명으로 탭명이 바뀌어도 역할→주소 유지)
  python3 - "$1" "$2" <<'PYEOF'
import json, pathlib, sys
p = pathlib.Path("HOME_AIWORKS/.claude/cmux-adapters/tower_roster.json".replace("HOME_AIWORKS", __import__("os").path.expanduser("~/Desktop/Ai_works")))
d = json.loads(p.read_text()) if p.exists() else {}
d[sys.argv[1]] = sys.argv[2]
p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
PYEOF
}

tab_exists() { # $1=역할/탭명 → 생존 surface ref 출력(없으면 빈). ①명부 ref 생존+탭명 일치 확인 ②탭명 매칭 폴백
  # ★탭명 일치 검증(2026-07-14): surface 번호는 재시작마다 회전 — stale 명부 ref가 타 역할 pane을
  # 가리키면 소환이 오생략된다(실사고: COO→s1(CEO)·gemini→s3(codex) 오멱등). ref 생존만으로 부족.
  $CMUX tree --all --json | python3 -c "
import json,sys,pathlib
d=json.load(sys.stdin)
title={s['ref']:(s.get('title') or '') for w in d['windows'] for ws in w['workspaces'] for p in ws['panes'] for s in p['surfaces']}
rp=pathlib.Path('$ROSTER')
if rp.exists():
    ref=json.loads(rp.read_text()).get('$1')
    if ref in title and '$1'.lower() in title[ref].lower(): print(ref); raise SystemExit
q='$1'.lower()
for w in d['windows']:
  for ws in w['workspaces']:
    for p in ws['panes']:
      for s in p['surfaces']:
        if q in (s.get('title') or '').lower(): print(s['ref']); raise SystemExit
"
}

wait_boot() { # $1=surface $2=마커 정규식 $3=타임아웃초
  local n=0
  until $CMUX read-screen --workspace $WS --surface "$1" 2>/dev/null | grep -qE "$2"; do
    sleep 5; n=$((n+5)); [ $n -ge "$3" ] && { echo "[boot_tower] WARN: $1 부팅 마커 미확인(${3}s)"; return 1; }
  done
}

send_line() { # $1=surface $2=텍스트
  $CMUX send --workspace $WS --surface "$1" -- "$2" && $CMUX send-key --workspace $WS --surface "$1" enter
}

nick_of() { # 역할명 → 애칭 병기 탭 타이틀(주인님 확정 애칭 2026-07-31·표시 표준 2026-08-02)
  case "$1" in
    COO) echo "COO·벤" ;;
    CSO) echo "CSO·리오" ;;
    reviewer-codex) echo "reviewer-codex·리프" ;;
    reviewer-gemini) echo "reviewer-gemini·젠" ;;
    *) echo "$1" ;;
  esac
}

summon() { # $1=탭명 $2=기동명령 $3=부팅마커 $4=각성문 [$5=후속명령]
  local exist; exist=$(tab_exists "$1")
  if [ -n "$exist" ]; then echo "[boot_tower] $1: 기존 생존($exist) — 소환 생략(멱등)"; return 0; fi
  local out sf
  out=$($CMUX new-split "${SPLIT_DIR:-down}" --workspace $WS --surface "${SPLIT_FROM:-$CALLER}")
  sf=$(echo "$out" | grep -o "surface:[0-9]*" | head -1)
  [ -z "$sf" ] && { echo "[boot_tower] FAIL: $1 pane 생성 실패"; return 1; }
  $CMUX rename-tab --workspace $WS --surface "$sf" -- "$(nick_of "$1")"
  roster_set "$1" "$sf"
  send_line "$sf" "cd $AIWORKS && $2"
  wait_boot "$sf" "$3" 90 || true
  send_line "$sf" "$4 $LLM_WIKI_BRIEF"
  [ -n "${5:-}" ] && { sleep 3; send_line "$sf" "$5"; }
  echo "[boot_tower] $1: 소환 완료($sf)"
}

# --- 편성 (모델 배정 정본: MASTER §7 — 7/12 이후 기준. Fable 가용기에는 CEO만 상위 유지) ---
SPLIT_DIR=right SPLIT_FROM=$CALLER summon "COO" \
  "claude --dangerously-skip-permissions --model claude-opus-4-8" \
  "bypass permissions" \
  "[COO 각성 - master 주입] 너는 Wave AI Networks의 COO(운영총괄)다. 헌장 .claude/COO_DIRECTIVE.md(자동 로드)의 기동 방식 절대로 각성하라 - 엔진 계약 계승(.claude/_engine-snapshot/WORKER_DIRECTIVE.md 1회 필독) 포함. 복원: output/WaveAI/경영본부/_round/ 최신 COO 핸드오프 + _round/SESSION_STATE.md 재독. 보고 채널 = master pane(탭명 'CEO 관제타워' - cmux_addr.py로 해소). 각성 완료를 push 보고하라." \
  "/fast"

COO_SF=$(tab_exists "COO")
SPLIT_DIR=down SPLIT_FROM=${COO_SF:-$CALLER} summon "CSO" \
  "claude --dangerously-skip-permissions --model claude-sonnet-5" \
  "bypass permissions" \
  "[CSO 각성 - master 주입] 너는 Wave AI Networks의 CSO(최고 시스템 운영자)다. 헌장 .claude/CSO_DIRECTIVE.md(자동 로드 - §0-b 정본보호·부활차단 점검 포함) + .claude/_engine-snapshot/CSO_DIRECTIVE.md 1회 필독. 각성 직후 점검: PHOENIX_FORBID_LIVE 플래그·launchd 프리플라이트 로그·dataless 잔여. 복원: _round/SESSION_STATE.md. 보고 채널 = master pane(탭명 'CEO 관제타워'). 각성 완료를 push 보고하라."

summon "reviewer-codex" \
  "codex --dangerously-bypass-approvals-and-sandbox" \
  "codex|gpt-" \
  "[리뷰어 각성] 너는 reviewer-codex(검증·반박 리뷰어)다. 계약: 지정 파일만 검토·수정 금지·verdict(ACCEPT|REVISE|BLOCK)+파일:라인 근거·score 금지·결함 발굴이 직무. 전문: .claude/_engine-snapshot/REVIEWER_DIRECTIVE.md (cys 명령은 cmux로 치환). 회신: cmux send --workspace workspace:1 --surface <master> + send-key enter. 각성 완료를 회신하라."

CODEX_SF=$(tab_exists "reviewer-codex")
SPLIT_DIR=down SPLIT_FROM=${CODEX_SF:-$CALLER} summon "reviewer-gemini" \
  "agy --dangerously-skip-permissions" \
  "Antigravity|Gemini" \
  "[리뷰어 각성] 너는 reviewer-gemini(적대적 반박 리뷰어 - 전략·UX·콘텐츠·사실성)다. 계약: 지정 파일만·수정 금지·verdict+근거·score 금지·ASCII '->' 표기. 회신: cmux send --workspace workspace:1 --surface <master> + send-key enter. 계정 정본 = greatson79@gmail.com(2026-07-27 개정 — dia-io.com은 소멸계정·재인증 금지). 계정이 그 gmail 계정이 아니면 즉시 보고하라. 각성 완료를 회신하라."

echo "[boot_tower] 편성 결과:"
$CMUX tree --all | grep -E "surface:"
echo "[boot_tower] 완료 — 각 노드의 각성 회신을 master가 수신·확인하라. agy 계정/모델·COO fast 적용은 회신으로 검증."
