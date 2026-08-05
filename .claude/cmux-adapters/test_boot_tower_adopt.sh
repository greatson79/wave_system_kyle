#!/bin/bash
# D 근본조치(H-01) 재수정 격리 회귀시험 — 노아 REVISE(REVIEWER_CODEX_VERDICT_boot_tower_D근본조치_2026-08-05.json)
# 의 "missing" 5번째 항목("네 실패 모드가 가드를 제거하거나 실패를 주입했을 때 RED가 되는
# mutation/격리 회귀시험") 이행. boot_tower.sh를 그대로 실행하지 않는다(실제 COO/CSO/리뷰어를
# 소환해버리므로) — 함수 정의부만 source하고 $CMUX를 진짜 프로세스를 상대하는 페이크로 바꿔
# tab_exists()/summon()의 편입(adopt) 경로를 격리 실행한다.
#
# 검증 대상:
#   T1: tab_exists()의 반환 stdout이 편입 시에도 순수 ref다("ADOPTED" 접미 없음) — HIGH-2
#   T2: 편입 후 각성문 전송 성공 시 summon()이 exit0 + roster._pidbind.awakened=true 기록 — HIGH-3
#   T3(RED 유도): 각성문 전송이 실패하면 summon()이 exit0을 반환하지 않는다(무음성공 금지) — HIGH-1
#       ★이 스크립트를 원래 결함 버전(HIGH-1 미수정)에 돌리면 T3가 FAIL로 뒤집힌다 — 그것이
#       "가드를 제거했을 때 RED" 조건이다. 직접 확인하려면 boot_tower.sh.bak-cso-D근본조치재수정-
#       20260805_1820(수정 전 백업)에 대해 이 스크립트의 SOURCE_TARGET을 바꿔 재실행해보라.
set -u
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_TARGET="${SOURCE_TARGET:-$SCRIPT_DIR/boot_tower.sh}"

TMPDIR_T=$(mktemp -d)
trap 'kill %1 2>/dev/null; rm -rf "$TMPDIR_T"' EXIT

# --- 페이크 cmux: tree --all --json / send / send-key만 필요한 만큼 흉내낸다 ---
# ★노아 REVISE(v1.1) 반영 — send마다 전송 텍스트를 SEND_LOG에 순서대로 남기고(WAKE/POST 순서·
# 횟수 반증 가능), SEND_FAIL_FLAG(전체 실패)와 별개로 SEND_FAIL_MATCH(부분일치 문자열만 실패)를
# 둬서 "각성문은 성공·후속명령만 실패" 케이스를 독립적으로 주입할 수 있게 한다.
FAKE_CMUX="$TMPDIR_T/cmux"
SEND_FAIL_FLAG="$TMPDIR_T/send_should_fail"
SEND_FAIL_MATCH="$TMPDIR_T/send_fail_match"
SEND_LOG="$TMPDIR_T/send.log"
cat > "$FAKE_CMUX" <<'FAKEEOF'
#!/bin/bash
case "$1" in
  tree)
    cat "$FAKE_TREE_JSON"
    ;;
  send)
    text="${@: -1}"
    echo "$text" >> "$SEND_LOG"
    if [ -f "$SEND_FAIL_FLAG" ]; then echo "FAKE send FAIL(all)" >&2; exit 1; fi
    if [ -f "$SEND_FAIL_MATCH" ]; then
      pattern=$(cat "$SEND_FAIL_MATCH")
      case "$text" in *"$pattern"*) echo "FAKE send FAIL(match:$pattern)" >&2; exit 1 ;; esac
    fi
    exit 0
    ;;
  send-key)
    if [ -f "$SEND_FAIL_FLAG" ]; then exit 1; fi
    exit 0
    ;;
  rename-tab) exit 0 ;;
  *) echo "FAKE cmux: unhandled subcommand $1" >&2; exit 1 ;;
esac
FAKEEOF
chmod +x "$FAKE_CMUX"

# --- 진짜 프로세스 하나를 띄워 pid/lstart/command를 실측 가능하게 한다(과도한 mock 지양) ---
sleep 100 &
REAL_PID=$!
sleep 0.3
REAL_LSTART=$(ps -p "$REAL_PID" -o lstart= | sed 's/^ *//;s/ *$//')
REAL_CMD=$(ps -p "$REAL_PID" -o command= | sed 's/^ *//;s/ *$//')

# ★boot_tower.sh의 is_bound_alive/_fingerprint_alive/mark_awakened와 이번에 추가한 편입-지문
# 재조회 블록은 전부 `~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json`을 python
# heredoc 안에서 하드코딩 참조한다(quoted heredoc이라 bash $ROSTER를 못 넘겨받는 기존 관례 —
# 이 시험에서 새로 만든 패턴 아님). 격리시험이 진짜 운영 roster를 건드리지 않게 HOME을
# temp 디렉터리로 바꿔 그 하드코딩 경로 자체를 온전히 temp 쪽으로 돌린다(코드 수정 없이 격리).
export HOME="$TMPDIR_T"
mkdir -p "$HOME/Desktop/Ai_works/.claude/cmux-adapters"
ROSTER="$HOME/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"
FAKE_TREE_JSON="$TMPDIR_T/tree.json"
cat > "$FAKE_TREE_JSON" <<JSONEOF
{"caller":{"surface_ref":"surface:1"},"windows":[{"workspaces":[{"panes":[{"surfaces":[{"ref":"surface:99","title":"testrole·기존세션","tty":"$(ps -p "$REAL_PID" -o tty= | tr -d ' ')"}]}]}]}]}
JSONEOF
python3 -c "
import json
d = {'_pidbind': {'testrole': {'pid': '$REAL_PID', 'start': '''$REAL_LSTART''', 'command': '''$REAL_CMD''', 'surface': 'surface:99', 'awakened': False, 'adopted': True}}, 'testrole': 'surface:99'}
open('$ROSTER','w').write(json.dumps(d, ensure_ascii=False, indent=1))
"

# --- boot_tower.sh 함수 정의부만 source (top-level 실행부는 제외 — 진짜 COO/CSO 소환 방지) ---
FUNC_END_LINE=$(grep -n '^claude_division_head_model' "$SOURCE_TARGET" | head -1 | cut -d: -f1)
FUNC_SRC=$(sed -n "52,$((FUNC_END_LINE - 1))p" "$SOURCE_TARGET")
eval "$FUNC_SRC"

# ★_adopt_existing()는 tty로 프로세스를 재발견하는데, 이 격리시험 환경(백그라운드 sleep)은
# 실제 pty가 없어 ps -t 조회가 항상 빈다(샌드박스 제약 — 실사고 아님). _adopt_existing 자체의
# pid오귀속 방어(HIGH-1/HIGH-2, 이전 라운드 REVIEWER_CODEX_VERDICT_boot_tower_adopt_2026-08-05.json
# 에서 이미 별도 검수)는 이 시험 범위 밖이다 — 여기서 재수정 중인 것은 tab_exists()의 반환계약과
# summon()의 편입 분기(HIGH-1/2/3, D근본조치 라운드)이므로, _adopt_existing은 "이미 알고 있는 진짜
# pid/lstart/cmd로 pidbind를 원자기록한다"는 자신의 핵심 계약만 정직한 스텁으로 재현한다.
_adopt_existing() {
  python3 -c "
import json
d = json.load(open('$ROSTER'))
d.setdefault('_pidbind', {})['$1'] = {'pid': '$REAL_PID', 'start': '''$REAL_LSTART''', 'command': '''$REAL_CMD''', 'surface': '$2', 'awakened': False, 'adopted': True}
d['$1'] = '$2'
open('$ROSTER','w').write(json.dumps(d, ensure_ascii=False, indent=1))
"
  return 0
}

CMUX="$FAKE_CMUX"
export FAKE_TREE_JSON SEND_FAIL_FLAG SEND_FAIL_MATCH SEND_LOG
WS="workspace:test"
CALLER="surface:1"
AIWORKS="$TMPDIR_T"
LLM_WIKI_BRIEF=""
ADOPT_EXISTING_ENABLED=1

PASS_N=0; TOTAL_N=0
assert() { # $1=조건bool문자열(0/1) $2=설명
  TOTAL_N=$((TOTAL_N+1))
  if [ "$1" = "1" ]; then echo "  [PASS] $2"; PASS_N=$((PASS_N+1)); else echo "  [FAIL] $2"; FAIL=1; fi
}

reset_awakened_false() { # 각 시험 전 "방금 편입됨(미각성)" 상태로 되돌린다
  python3 -c "
import json
d=json.load(open('$ROSTER'))
d['_pidbind']['testrole']['awakened']=False
open('$ROSTER','w').write(json.dumps(d))
"
}
get_awakened() { python3 -c "import json;print(json.load(open('$ROSTER'))['_pidbind']['testrole']['awakened'])"; }

echo "=== T1: tab_exists 순수성(HIGH-2) — 편입 시에도 stdout에 ADOPTED 접미 없음 ==="
out=$(tab_exists "testrole"); rc=$?
[ "$out" = "surface:99" ] && p1=1 || p1=0
[ "$rc" -eq 2 ] && p2=1 || p2=0
assert "$p1" "stdout이 순수 ref('surface:99')다 (실제: '$out')"
assert "$p2" "exit code가 2(편입 신호)다 (실제: $rc)"

echo "=== T2: 편입 각성+후속명령 둘 다 성공 시 summon() exit0 + WAKE/POST 순서·횟수 + awakened=true(HIGH-3) ==="
# ★노아 REVISE(v1.1) 반영 — $5(COO /fast 상당 후속명령)를 실제로 공급해 그 경로도 실행시킨다.
rm -f "$SEND_FAIL_FLAG" "$SEND_FAIL_MATCH"; : > "$SEND_LOG"
reset_awakened_false
summon "testrole" "true" "marker" "WAKE_MSG" "POST_MSG" >/dev/null 2>&1
sc=$?
[ "$sc" -eq 0 ] && p3=1 || p3=0
awakened=$(get_awakened)
[ "$awakened" = "True" ] && p4=1 || p4=0
nlines=$(wc -l < "$SEND_LOG" | tr -d ' ')
line1=$(sed -n '1p' "$SEND_LOG"); line2=$(sed -n '2p' "$SEND_LOG")
case "$line1" in *WAKE_MSG*) o1=1 ;; *) o1=0 ;; esac
case "$line2" in *POST_MSG*) o2=1 ;; *) o2=0 ;; esac
assert "$p3" "WAKE+POST 둘 다 성공 시 summon()이 exit0이다 (실제: $sc)"
assert "$p4" "roster._pidbind.testrole.awakened가 true로 기록됐다 (실제: $awakened)"
assert "$([ "$nlines" = 2 ] && echo 1 || echo 0)" "send가 정확히 2회(WAKE 1회+POST 1회)만 일어났다 (실제: ${nlines}회)"
assert "$o1" "1번째 send가 WAKE_MSG다 (실제: '$line1')"
assert "$o2" "2번째 send가 POST_MSG다(순서=WAKE먼저·POST나중) (실제: '$line2')"

echo "=== T3(RED 유도): 각성문(WAKE) 전송 실패 시 summon()이 무음 exit0을 반환하지 않는다(HIGH-1) ==="
reset_awakened_false
rm -f "$SEND_FAIL_MATCH"; : > "$SEND_LOG"
touch "$SEND_FAIL_FLAG"
summon "testrole" "true" "marker" "WAKE_MSG" "POST_MSG" >/dev/null 2>&1
sc=$?
rm -f "$SEND_FAIL_FLAG"
[ "$sc" -ne 0 ] && p5=1 || p5=0
awakened2=$(get_awakened)
[ "$awakened2" = "False" ] && p6=1 || p6=0
assert "$p5" "각성문 전송 실패 시 summon()이 exit0을 반환하지 않는다(무음성공 금지) (실제: $sc)"
assert "$p6" "전송 실패 시 awakened가 false로 남는다(거짓 True 금지) (실제: $awakened2)"

echo "=== T4(RED 유도·노아 REVISE v1.2 지적①): WAKE는 성공·POST(후속명령)만 실패해도 summon()이 exit0을 반환하지 않는다 ==="
reset_awakened_false
: > "$SEND_LOG"
echo "POST_MSG" > "$SEND_FAIL_MATCH"   # POST_MSG를 담은 send만 실패, WAKE_MSG는 통과
summon "testrole" "true" "marker" "WAKE_MSG" "POST_MSG" >/dev/null 2>&1
sc=$?
rm -f "$SEND_FAIL_MATCH"
# ★도달층 검증(노아 v1.2 지적①) — 선행 WAKE 실패로 우연히 GREEN이 되는 오탐을 막기 위해,
# 최종 결과를 보기 전에 "WAKE는 실제로 성공해 로그에 남았고 POST 표적실패 지점까지 실제
# 도달했는가"부터 증명한다. SEND_LOG는 실패한 send도 텍스트를 먼저 기록하므로(FAKE_CMUX
# 구현상 로그 기록이 실패판정보다 앞선다) 2줄(WAKE_MSG, POST_MSG)이 남아 있어야 두 번째
# send까지 실제로 시도됐다는 뜻이다.
t4_line1=$(sed -n '1p' "$SEND_LOG"); t4_line2=$(sed -n '2p' "$SEND_LOG")
case "$t4_line1" in *WAKE_MSG*) t4_reach1=1 ;; *) t4_reach1=0 ;; esac
case "$t4_line2" in *POST_MSG*) t4_reach2=1 ;; *) t4_reach2=0 ;; esac
assert "$t4_reach1" "[도달] WAKE_MSG가 실제로 1번째 send로 로그됐다(WAKE 성공 확인) (실제: '$t4_line1')"
assert "$t4_reach2" "[도달] POST_MSG가 실제로 2번째 send로 로그됐다(POST 표적실패 지점 도달 확인) (실제: '$t4_line2')"
[ "$sc" -ne 0 ] && p7=1 || p7=0
awakened3=$(get_awakened)
[ "$awakened3" = "False" ] && p8=1 || p8=0
assert "$p7" "후속명령(POST)만 실패해도 summon()이 exit0을 반환하지 않는다 (실제: $sc)"
assert "$p8" "후속명령 실패 시에도 awakened가 false로 남는다 (실제: $awakened3)"

echo "=== T5(RED 유도·노아 REVISE 지적②): WAKE+POST 성공해도 mark_awakened가 실패하면 summon()이 exit0을 반환하지 않는다 ==="
# ★mark_awakened() 자체의 exact-match 로직(pre-existing, 별개 라운드에서 이미 검수)은 다시
# 검증하지 않는다 — "mark_awakened가 실패를 반환하면 summon()이 그것을 삼키지 않고 그대로
# 전파하는가"라는 summon()의 계약만 격리해서 묻기 위해, 실패를 반환하는 스텁으로 의도적으로
# 교체한다(고전적 mutation 기법 — 실제 결함 재현이 목적).
# ★노아 REVISE(v1.3) 반영 — 스텁이 "실제로 호출됐다"는 표식(MARK_CALLED)을 남긴다. 이게 없으면
# mark_awakened 호출 자체가 코드에서 사라지고 다른 이유로 nonzero가 나도 T5가 우연히 GREEN일
# 수 있다(도달층 미검증 오탐 — T4와 같은 층의 문제).
MARK_CALLED=0
mark_awakened() { MARK_CALLED=1; return 1; }
reset_awakened_false
: > "$SEND_LOG"; rm -f "$SEND_FAIL_FLAG" "$SEND_FAIL_MATCH"
summon "testrole" "true" "marker" "WAKE_MSG" "POST_MSG" >/dev/null 2>&1
sc=$?
# ★도달층 검증(노아 v1.2 지적②) — WAKE·POST가 둘 다 실제 성공(로그 2줄 전부, SEND_FAIL 계열
# 미설정이므로 진짜 성공)해서 mark 단계까지 도달했는지부터 확인한다. 이게 없으면 T3/T4처럼
# 앞단에서 실패해도 우연히 nonzero+false가 나와 GREEN이 되는 오탐을 배제할 수 없다.
t5_line1=$(sed -n '1p' "$SEND_LOG"); t5_line2=$(sed -n '2p' "$SEND_LOG")
case "$t5_line1" in *WAKE_MSG*) t5_reach1=1 ;; *) t5_reach1=0 ;; esac
case "$t5_line2" in *POST_MSG*) t5_reach2=1 ;; *) t5_reach2=0 ;; esac
assert "$t5_reach1" "[도달] WAKE_MSG가 실제로 1번째 send로 성공 로그됐다(mark 단계 도달 전제①) (실제: '$t5_line1')"
assert "$t5_reach2" "[도달] POST_MSG가 실제로 2번째 send로 성공 로그됐다(mark 단계 도달 전제②) (실제: '$t5_line2')"
assert "$([ "$MARK_CALLED" = 1 ] && echo 1 || echo 0)" "[도달] mark_awakened 스텁이 실제로 호출됐다(mark 단계 도달 전제③ — 호출 자체 삭제 mutation과 구분) (실제: MARK_CALLED=$MARK_CALLED)"
[ "$sc" -ne 0 ] && p9=1 || p9=0
awakened4=$(get_awakened)
[ "$awakened4" = "False" ] && p10=1 || p10=0
assert "$p9" "mark_awakened 실패 시 summon()이 exit0을 반환하지 않는다 (실제: $sc)"
assert "$p10" "mark_awakened 실패 시 awakened가 false로 남는다(거짓 True 미기록) (실제: $awakened4)"

echo ""
echo "=== 집계(assert() 호출 자동계수 — 눈대중 수기집계 금지, 노아 REVISE v1.2 지적② 반영) ==="
echo "PASS ${PASS_N}/${TOTAL_N}"
if [ "$FAIL" -eq 0 ]; then
  echo "ALL PASS"
  exit 0
else
  echo "REGRESSION DETECTED — 위 [FAIL] 항목이 있는 HIGH 재발"
  exit 1
fi
