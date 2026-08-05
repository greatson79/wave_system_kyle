#!/bin/bash
# 관제타워(경영본부) 자동 편성 — "너는 마스터다" 각성 직후 master가 1회 실행 (2026-07-10 주인님 승인)
# 편성: COO·CSO·reviewer-codex·reviewer-gemini 4종을 master pane 주변에 소환·각성.
# 규율 내장: ①소환 표준 플래그(권한허용모드) ②탭명 즉시 부여(주소 발견성 — s6 누락 사고 재발방지)
#           ③멱등 — 동명 탭 생존 시 소환 생략(이중 소환 금지). ★탭명만으론 부족(2026-08-04 실사고:
#             exit 후 빈 zsh만 남았는데 탭명이 잔존해 '기존 생존'으로 오판·gemini 무음 미소환) —
#             ★★2차 교정: 1차 수정(read-screen 문자열 마커)은 리프 REVISE로 폐기됨 — 마커가
#             "종료 후 화면에 남은 기동명령 문자열"과 자기매칭돼(예: codex|gpt- 가 "codex
#             --dangerously-..." 명령줄 자체에 일치) 죽은 pane일수록 오히려 걸렸다. tty도 CEO
#             실측상 5건중2건 오귀속+1쌍 중복이라 cmux 자기보고 단독 결속 금지. 채택안 = 소환
#             시점에 실제 프로세스의 **pid+start-time+command+surface**를 tower_roster.json._pidbind에
#             기록해두고(capture_tty로 맨 셸에서 진짜 tty 취득→bind_process가 그 tty로 pid 결속),
#             이후 판정(is_bound_alive)은 그 4종이 동시일치하는지만 ps 재조회로 본다(화면 텍스트도
#             cmux 자기보고 tty도 재사용 안 함). 기록이 없거나 불일치=fail-closed(죽음 취급→재소환.
#             이중소환>미소환 — 전자는 보고로 회수 가능, 후자는 무음 결손).
#             ★★3차 교정(CEO_판정_boot_tower_멱등_2026-08-04.md §5 — 리프 2차 REVISE): (a) surface
#             미결속 — 역할 단위로만 pid 대조하면 동일제목 stale/중복 surface가 "다른 살아있는
#             결속 PID"를 빌려 통과할 수 있었다 → _pidbind에 surface 추가, is_bound_alive(role,ref)가
#             surface 일치까지 확인. (b) 실패 전파 누락 — wait_boot·bind_process 실패를 `|| true`로
#             삼키고 무조건 "소환 완료"를 echo하던 것이 젠 사건과 동일 결함의 재발이었다(판정 로직만
#             고치고 보고 경로엔 fail-open을 남김) → summon()이 실패를 exit code로 전파, 스크립트
#             말미에서 FAILED_ROLES를 집계해 CEO 화면에 명시 노출하고 exit 1. ★한계(정직 명시):
#             소환경로 밖에서 수동 기동된 노드는 pid기록이 없어 항상 재소환 판정된다(예: 오늘 CEO가
#             수동 재기동한 gemini).
#             ★★4차 교정(§7 — 리프 3차 REVISE 독립수렴 + CEO §6-3 철회): "생존"만으로 멱등 스킵을
#             허용하면 그 사고(생존하되 각성문 미주입)가 신규소환 경로만 고쳐도 **기존생존 스킵
#             경로**에서 그대로 재발한다(CEO 실증: 오늘 COO·reviewer-codex가 이 경로로 지나갔다).
#             수정: `_pidbind`에 `awakened` 플래그 추가 — 각성문(+후속명령)까지 전달 성공해야
#             true로 기록되고, `is_bound_alive()`(멱등 스킵 판정)는 fingerprint 생존만이 아니라
#             이 플래그까지 확인한다. fingerprint가 그대로면 awakened도 그대로 남으므로 이미
#             각성해 작업 중인 노드(compact 등)에 불필요한 재전송은 하지 않는다 — fingerprint가
#             바뀌었을 때만(재기동 등) 무효화→재소환 경로를 탄다. ④모델 배정 정본(MASTER §7)
#           ⑤부활 금지 — 전부 fresh 기동(이 스크립트 실행 자체가 주인님/CEO 명시 명령의 집행)
set -u
# H-01 귀속 근거 부재로 CEO 결재 2026-08-05 비활성 — 정식 수정은 통합 처방
# (CSO_통합처방_노아교차반영_v1.2_2026-08-05.md §2 D — 최신판 참조 필수). 코드는 남기고 호출만 차단, 값을
# 1로 되돌리면 즉시 복구된다. 비활성 시 대가=이중소환(회수 가능·오늘 s49로 실증) —
# 오귀속(무음 오류)보다 안전하다는 것이 CEO 판단.
ADOPT_EXISTING_ENABLED=0
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

tab_exists() { # $1=역할/탭명 → 생존 surface ref 출력(없으면 빈)
  # ①명부 ref 생존+탭명 일치 확인 ②탭명 매칭 폴백 ③pid+start+command+surface 4종 결속 대조(is_bound_alive)
  # ★탭명 일치 검증(2026-07-14): surface 번호는 재시작마다 회전 — stale 명부 ref가 타 역할 pane을
  # 가리키면 소환이 오생략된다(실사고: COO→s1(CEO)·gemini→s3(codex) 오멱등). ref 생존만으로 부족.
  # ★프로세스 실재 검증(2026-08-04 CEO 판정 2차): 탭명은 rename-tab이 붙인 값이라 그 아래 프로세스가
  # exit해도 지워지지 않는다(실사고: reviewer-gemini exit 후 빈 zsh만 남았는데 탭명이 잔존 → 위 두
  # 확인을 모두 통과해 '기존 생존'으로 오판·무음 미소환). 1차 수정(read-screen 마커)은 리프 REVISE로
  # 폐기(마커가 죽은 화면에 남은 기동명령 문자열과 자기매칭). tty도 CEO 실측상 신뢰 불가(오귀속·
  # 중복 실증). 채택 = is_bound_alive()의 pid+start+command 3종 결속 대조.
  # ★리프 2차 REVISE(surface 미결속): 역할 단위로만 pid를 대조하면, 동일 제목의 stale/중복 surface가
  # "다른 살아있는 결속 PID"를 빌려 통과할 수 있다(귀속 증명 불가). 수정: _pidbind에 surface도
  # 기록하고, is_bound_alive(role, ref)가 그 surface 일치까지 확인한다 — 지금 대조하려는 ref와
  # 결속 당시의 surface가 다르면 fail-closed(죽음 취급).
  local ref
  ref=$($CMUX tree --all --json | python3 -c "
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
")
  [ -z "$ref" ] && return 0
  is_bound_alive "$1" "$ref" && { echo "$ref"; return 0; }
  # ★2026-08-05 데릭 수정(CEO 승인 — 오늘 아침 CSO 이중소환 실사고 원인분석): 여기까지 왔다는
  # 것은 "제목은 일치하는데 _pidbind가 없거나 어긋난다"는 뜻이다 — 신규소환 경로(bind_process)를
  # 거치지 않고 생존한 노드(예: 어제 세션이 오늘 아침까지 그대로 살아있는 경우)가 정확히 이
  # 상태였다. 관측(제목일치=생존 정황)은 했으나 그 관측을 _pidbind에 기록하지 않으면 다음
  # 판정(is_bound_alive)에서 "결속 기록 없음→fail-closed"로 처음부터 다시 물어 이중소환을
  # 낳는다(오늘 실사고: CSO s7). 여기서 그 관측을 편입(adopt)한다 — 단 재실측값만 쓴다(기존
  # roster 값을 그대로 되쓰면 stale이 영속화된다는 것이 CEO 제약 ①).
  # ★2026-08-05 CEO 승인 — D 근본조치(H-01) 배선 변경: 편입(adopt)된 노드는 "생존"과
  # "각성"을 같은 것으로 취급하지 않는다 — summon()이 무조건 스킵하는 대신 각성문을
  # 재전송하도록 신호를 분리한다.
  # ★2026-08-05 노아 REVISE(HIGH-2) 재수정: 이전엔 이 신호를 "$ref ADOPTED" 복합 문자열로
  # stdout에 섞어 반환했다 — tab_exists는 순수 surface ref 전용 계약이었는데(주석 상단),
  # COO_SF·CODEX_SF 같은 일반 소비자가 이 오염된 문자열을 그대로 SPLIT_FROM에 넣어
  # new-split --surface 인자를 깨뜨릴 수 있었다. 수정: stdout에는 항상 순수 ref만 쓰고,
  # "방금 편입했다"는 신호는 **exit code 2**로만 전달한다(exit 0=이미 존재/생존, exit 2=
  # 방금 편입·각성 미검증). `$(...)` 명령치환도 그 서브셸의 exit code는 그대로 `$?`에
  # 남기므로(변수 대입 직후 한정 — 다른 명령이 끼면 덮인다) 호출부는 대입 직후 즉시
  # `$?`를 캡처해 분기한다. ★HIGH-1(귀속 근거)은 이 변경의 대상이 아니다 — 별개 축(CEO
  # 판정) — 그래서 ADOPT_EXISTING_ENABLED는 여전히 0으로 묶어둔다.
  if [ "$ADOPT_EXISTING_ENABLED" = "1" ] && _adopt_existing "$1" "$ref"; then
    echo "$ref"
    return 2
  fi
  return 0
}

_expected_bin_of() { # $1=역할 → 그 역할이 기동될 때 쓰는 실행파일명 부분일치 패턴(_adopt_existing 전용)
  case "$1" in
    reviewer-codex) echo "codex" ;;
    reviewer-gemini) echo "agy" ;;
    *) echo "claude" ;;  # CEO·COO·CSO 전부 claude
  esac
}

_adopt_existing() { # $1=역할 $2=surface ref(title-match로 찾았으나 is_bound_alive 실패한 후보)
                     # → exit0=재실측 지문을 _pidbind에 편입 성공 / exit1=편입 실패(호출부가 정상 재소환 경로로 폴백 — 실패를 성공으로 삼키지 않는다, CEO 제약②)
  # ★정직한 한계: cmux 자기보고 tty는 capture_tty의 코멘트가 실측으로 밝힌 대로 신뢰도가 낮다
  # (5건중2건 오귀속 전례). 이 함수는 신규소환 시의 capture_tty(맨 셸 상태에서 "tty" 명령 직접
  # 실행)를 쓸 수 없다 — 이미 에이전트가 화면을 장악한 기존 pane에 "tty"를 보내면 그 세션의
  # 실제 작업(예: 진행 중인 turn)에 임의 텍스트를 주입하는 부작용이 있다. 따라서 cmux 자기보고
  # tty에 의존하되, ①역할에 맞는 바이너리인지 ②bare shell이 아닌지 이중 확인해 오귀속 위험을
  # 낮춘다(완전 제거는 아님 — 노아 코드리뷰에서 이 한계를 특히 검토해달라).
  local role="$1" ref="$2"
  local tty
  tty=$($CMUX tree --all --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
for w in d['windows']:
  for ws in w['workspaces']:
    for p in ws['panes']:
      for s in p['surfaces']:
        if s['ref']=='$ref': print(s.get('tty') or ''); raise SystemExit
")
  [ -z "$tty" ] && return 1
  local binpat; binpat=$(_expected_bin_of "$role")
  local pid
  pid=$(ps -t "$tty" -o pid=,command= 2>/dev/null | grep -F "$binpat" | grep -vE '/bin/(z|ba)?sh( -l)?$' | awk '{print $1}' | head -1)
  [ -z "$pid" ] && return 1
  local lstart cmdline
  lstart=$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^ *//;s/ *$//')
  cmdline=$(ps -p "$pid" -o command= 2>/dev/null | sed 's/^ *//;s/ *$//')
  [ -z "$lstart" ] && return 1
  [ -z "$cmdline" ] && return 1
  # ★2026-08-05 CEO 안전조치 지시(HIGH-1·HIGH-2 — 노아 REVISE 대응, 재설계는 아니고 밤새
  # 버티는 최소조치. 근본 재설계는 CSO 시스템 전수점검 Phase3로 이관) — 단일 원자 쓰기로
  # pidbind+roster_set을 함께 기록한다(HIGH-4/원자성). 기록 전 두 가지를 거부(fail-closed)한다:
  # ①HIGH-1(tty 오귀속): 이 pid가 이미 *다른* 역할의 _pidbind에 결속돼 있으면 귀속 근거가
  #   불충분한 것으로 보고 편입을 포기한다(로직을 강화해 더 확신하려 하지 않는다 — 약한 근거면
  #   그냥 포기). ②HIGH-2(미검증 각성): 여기서 각성 여부를 검증할 수단이 없으므로 awakened를
  #   True로 쓰지 않는다 — False로 정직하게 남겨 is_bound_alive()의 멱등스킵 판정이 이 필드에
  #   의존하지 못하게 한다(검증 못 하면 참으로 기록하지 않는다 — 오늘의 원칙 그대로).
  python3 - "$role" "$pid" "$lstart" "$cmdline" "$ref" <<'PYEOF'
import json, os, pathlib, sys, tempfile
role, pid, lstart, cmdline, ref = sys.argv[1:6]
p = pathlib.Path(os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
d = json.loads(p.read_text()) if p.exists() else {}
pidbind = d.setdefault("_pidbind", {})
for other_role, b in pidbind.items():
    if other_role != role and isinstance(b, dict) and b.get("pid") == pid:
        print(f"[boot_tower] REFUSE adopt {role}: pid={pid}는 이미 역할 '{other_role}'에 결속됨(귀속 불충분·fail-closed)", file=sys.stderr)
        sys.exit(1)  # HIGH-1: 약한 근거 → 편입 포기
pidbind[role] = {
    "pid": pid, "start": lstart, "command": cmdline, "surface": ref,
    "awakened": False, "adopted": True,  # HIGH-2: 미검증은 거짓 True로 기록하지 않는다
}
d[role] = ref  # roster_set과 동일한 단순 키도 같은 원자 쓰기에 포함(HIGH-4)
fd, tmp_path = tempfile.mkstemp(dir=str(p.parent), prefix=".tower_roster.", suffix=".tmp")
try:
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))
    os.replace(tmp_path, p)  # 원자 교체 — 중간 상태 노출 없음
except BaseException:
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
    raise
print(f"[boot_tower] {role}: 기존생존 노드 편입(adopt) 완료(pid={pid}, surface={ref}, awakened=False·미검증) — 재실측 지문 원자기록", file=sys.stderr)
PYEOF
}

_fingerprint_alive() { # $1=역할 $2=대조할 surface ref → exit0(pid+start+command+surface 4종 동시일치=그 프로세스가 여전히 생존) / exit1(그 외=fail-closed)
  # ★순수 프로세스 생존 판정만 한다(각성 여부는 안 봄) — bind_process의 TOCTOU 재확인(§6-2)이
  # "지금 막 결속한 프로세스가 여전히 살아있나"만 물을 때 쓰기 위해 is_bound_alive와 분리했다
  # (그 시점엔 아직 각성문을 안 보냈으니 awakened=false가 정상이라, 그걸 같이 물으면 항상 실패한다).
  python3 - "$1" "$2" <<'PYEOF'
import json, pathlib, os, sys, subprocess
role, ref = sys.argv[1], sys.argv[2]
p = pathlib.Path(os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
d = json.loads(p.read_text()) if p.exists() else {}
b = (d.get("_pidbind") or {}).get(role)
if not b or not b.get("pid"):
    sys.exit(1)  # 결속 기록 없음(예: 소환경로 밖 수동기동) → fail-closed
if b.get("surface") != ref:
    sys.exit(1)  # 결속된 surface != 지금 대조 중인 surface → 살아있는 타 surface의 pid를 빌려온 오귀속 방지
try:
    lstart = subprocess.run(["ps", "-p", b["pid"], "-o", "lstart="], capture_output=True, text=True, timeout=5).stdout.strip()
    cmdline = subprocess.run(["ps", "-p", b["pid"], "-o", "command="], capture_output=True, text=True, timeout=5).stdout.strip()
except Exception:
    sys.exit(1)
if not lstart or not cmdline:
    sys.exit(1)  # pid 부재(이미 exit) → fail-closed
if lstart == (b.get("start") or "").strip() and cmdline == (b.get("command") or "").strip():
    sys.exit(0)  # 동일 surface+동일 pid+동일 start-time+동일 command = 결속 당시 그 프로세스가 여전히 생존
sys.exit(1)  # start-time 또는 command 불일치 = pid 재사용(다른 프로세스로 교체) → fail-closed
PYEOF
}

is_bound_alive() { # $1=역할 $2=대조할 surface ref → exit0(단일 스냅샷에서 fingerprint 생존 AND 각성완료) / exit1(그 외=fail-closed→(재)소환)
  # ★4차 REVISE 반영(§7 — 리프 독립수렴 + CEO §6-3 철회): "생존"만으로 멱등 스킵을 허용하면, 오늘
  # 실제로 벌어진 사고(COO·reviewer-codex가 살아있으나 각성문을 못 받은 채 "기존 생존 — 소환
  # 생략"으로 넘어간 것)가 재발한다. fingerprint(프로세스 신원)가 살아있어도 그 fingerprint에
  # 결속된 awakened 플래그가 true가 아니면 스킵 대상이 아니다 — summon()이 그 역할을 다시 처리해
  # 최소한 각성문 재전송을 시도한다. ★설계 의도(CEO 채택 — 리프 안1, 안2 "기존생존이면 무조건
  # 재전송"은 미채택): fingerprint가 그대로면 awakened 플래그도 그대로 남아있으므로, 이미 각성해서
  # 작업 중인 노드(예: compact 진행 중)에 불필요한 재전송으로 컨텍스트를 태우지 않는다.
  # ★5차 REVISE 반영(§②): fingerprint 판정과 awakened 판정을 `_fingerprint_alive`+별도 python
  # 호출 2회로 나누면, 그 사이 레코드가 교체될 경우 "fingerprint A 생존 + record B의 awakened"를
  # 잘못 조합할 수 있다(두 번의 파일 읽기 = 그 자체로 경합 창). 그래서 여기서는 `_fingerprint_alive`를
  # 호출하지 않고, **단일 python 프로세스의 단일 파일읽기(1회 `b`)**로 pid+start+command+surface
  # 생존판정과 awakened 판정을 모두 수행한다(read-verify는 그 1회 호출 안에서 원자적).
  python3 - "$1" "$2" <<'PYEOF'
import json, pathlib, os, sys, subprocess
role, ref = sys.argv[1], sys.argv[2]
p = pathlib.Path(os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
d = json.loads(p.read_text()) if p.exists() else {}
b = (d.get("_pidbind") or {}).get(role)   # ★단일 스냅샷 — 이 b 하나로 아래 두 판정을 전부 한다
if not b or not b.get("pid"):
    sys.exit(1)
if b.get("surface") != ref:
    sys.exit(1)
try:
    lstart = subprocess.run(["ps", "-p", b["pid"], "-o", "lstart="], capture_output=True, text=True, timeout=5).stdout.strip()
    cmdline = subprocess.run(["ps", "-p", b["pid"], "-o", "command="], capture_output=True, text=True, timeout=5).stdout.strip()
except Exception:
    sys.exit(1)
if not lstart or not cmdline:
    sys.exit(1)
if not (lstart == (b.get("start") or "").strip() and cmdline == (b.get("command") or "").strip()):
    sys.exit(1)
sys.exit(0 if b.get("awakened") else 1)
PYEOF
}

mark_awakened() { # $1=역할 $2=surface $3=pid $4=start $5=command → 그 정확한 4종 지문과 exact-match할 때만 awakened=true 기록(불일치=exit1, no-op 아님)
  # ★5차 REVISE 반영(§①): surface만 비교하면 그 사이 같은 surface가 *다른* pid/start/command로
  # 재결속됐을 때도 awakened를 붙여버릴 수 있다(no-op을 성공으로 오판하는 것과 동급 위험). 소환
  # 시점에 실제 결속한 pid+start+command까지 함께 넘겨받아 **4종 전건 exact-match**할 때만
  # 기록한다 — 하나라도 다르면(레코드가 그 사이 교체됨) 기록하지 않고 exit1로 호출부에 알린다.
  python3 - "$1" "$2" "$3" "$4" "$5" <<'PYEOF'
import json, pathlib, os, sys
p = pathlib.Path(os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
d = json.loads(p.read_text()) if p.exists() else {}
b = (d.get("_pidbind") or {}).get(sys.argv[1])
if (b and b.get("surface") == sys.argv[2] and b.get("pid") == sys.argv[3]
        and b.get("start") == sys.argv[4] and b.get("command") == sys.argv[5]):
    b["awakened"] = True
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    sys.exit(0)  # exact-match 기록 성공
sys.exit(1)  # 레코드 없음/불일치(그 사이 재결속됨) → no-op을 성공으로 위장하지 않고 명시 실패
PYEOF
}

bind_process() { # $1=역할 $2=surface $3=기동명령 $4=capture_tty로 사전취득한 tty → pid+start+command+surface 결속(bounded retry 3회)
  # ★리프 2차 REVISE(실패 무시): one-shot 스크립트라 실패를 삼키면 다음 실행까지 결속이 영구
  # 미기록으로 남는다 — 소환 직후 타이밍 편차(프로세스가 아직 완전히 뜨지 않음 등)에 대비해
  # 최대 3회(2초 간격) 재시도하고, 그래도 실패하면 nonzero를 그대로 호출부(summon)에 전파한다.
  local attempt
  for attempt in 1 2 3; do
    _bind_process_once "$1" "$2" "$3" "$4" && return 0
    [ "$attempt" -lt 3 ] && sleep 2
  done
  echo "[boot_tower] WARN: $1 pid결속 실패(3회 재시도 소진) — 결속 미기록(다음 사이클 fail-closed 재소환 대상)"
  return 1
}

capture_tty() { # $1=surface(★생성 직후·아직 bare shell일 때만 호출) → 그 pane의 진짜 tty 출력(예: ttys017)
  # ★CEO 힌트(CEO_판정_boot_tower_멱등_2026-08-04.md §5) 채택: cmux tree JSON이 자체 보고하는
  # tty 필드를 믿는 대신, 그 surface에 아직 아무 에이전트도 올라가지 않은 "맨 셸" 상태에서
  # 셸 내장명령 `tty`를 직접 실행시켜 커널이 실제로 배정한 tty를 셸 스스로 출력하게 한다 —
  # cmux의 자기보고를 거치지 않는 1차 소스. ★이 read-screen 사용은 리프의 원래 지적(생존판정에
  # 화면 텍스트를 쓰지 말라)과 충돌하지 않는다 — 여기서는 "생존 여부 판정"이 아니라 "식별자(진짜
  # tty) 취득"에만 쓴다(용도가 다르다). 반드시 send_line으로 부팅명령을 보내기 전, 맨 셸 상태에서
  # 1회만 호출한다 — 에이전트가 이미 화면을 장악한 뒤에는 이 텍스트가 프롬프트로 오인돼 무의미.
  send_line "$1" "tty" >/dev/null   # ★$CMUX send/send-key가 "OK ..."를 stdout에 찍는다 — 호출부가
                                     # $(capture_tty ...)로 결과를 캡처하므로 이 노이즈를 반드시 버려야
                                     # tty 값만 순수하게 반환된다(오늘 자체 테스트에서 실제로 걸린 결함).
  local out="" n=0
  until [ -n "$out" ] || [ "$n" -ge 10 ]; do
    out=$($CMUX read-screen --workspace $WS --surface "$1" 2>/dev/null | grep -oE '/dev/tty[A-Za-z0-9]+' | tail -1)
    [ -z "$out" ] && { sleep 1; n=$((n+1)); }
  done
  echo "$out" | sed 's#/dev/##'
}

_bind_process_once() { # $1=역할 $2=surface $3=기동명령 $4=capture_tty로 사전취득한 진짜 tty — bind_process의 1회분 실제 로직
  # tty는 소환 직후(같은 세션 내 새 pane — 앱 재기동/auto-resume 이력 없음) capture_tty()가 셸
  # 내장명령으로 직접 취득한 값을 그대로 받는다(cmux 자기보고 tty 재조회 안 함 — CEO 실측상
  # cmux 자기보고는 5건중2건 오귀속이었다). 이후의 생존판정(is_bound_alive)은 이 시점에 결속한
  # pid만으로 ps 재조회한다 — tty 신뢰 구간을 "capture_tty 실행 그 1회"로 좁힌 것이 핵심.
  local tty="$4"
  [ -z "$tty" ] && return 1
  local binname pid
  binname=$(echo "$3" | awk '{print $1}')
  pid=$(ps -t "$tty" -o pid=,command= 2>/dev/null | grep -F "$binname" | grep -vE '/bin/(z|ba)?sh( -l)?$' | awk '{print $1}' | head -1)
  [ -z "$pid" ] && return 1
  local lstart cmdline
  lstart=$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^ *//;s/ *$//')
  cmdline=$(ps -p "$pid" -o command= 2>/dev/null | sed 's/^ *//;s/ *$//')
  [ -z "$lstart" ] && return 1
  # ★리프 3차 REVISE(§6-2 TOCTOU): lstart만 비어있지 않은지 검사하고 cmdline 공백은 검사하지
  # 않으면, 두 ps 호출 사이에 프로세스가 exit한 경우 빈 command를 "결속 성공"으로 기록해버린다.
  [ -z "$cmdline" ] && return 1
  python3 - "$1" "$pid" "$lstart" "$cmdline" "$2" <<'PYEOF'
import json, pathlib, os, sys
p = pathlib.Path(os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault("_pidbind", {})[sys.argv[1]] = {"pid": sys.argv[2], "start": sys.argv[3], "command": sys.argv[4], "surface": sys.argv[5], "awakened": False}
p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
PYEOF
  # ★리프 3차 REVISE(§6-2): 기록 직후 _fingerprint_alive로 재확인해 "기록 시점 프로세스가 실제로
  # 아직 살아있었는지"를 한 번 더 좁힌다(is_bound_alive가 아니라 순수 fingerprint 판정을 쓴다 —
  # 이 시점엔 각성문을 아직 안 보냈으니 awakened=false가 정상이고, 그걸 같이 물으면 항상 실패한다).
  # ★정직한 한계: 이 재확인은 기록-확인 사이의 경합 창을 *축소*할 뿐 원리상 *제거*하지 못한다
  # (관측과 관측 사이엔 항상 간극이 남는다) — 남은 창은 "제거"가 아니라 다음 is_bound_alive
  # 호출의 fail-closed가 실질 방어선이다.
  _fingerprint_alive "$1" "$2" || return 1
  # ★5차 REVISE(§①) 대응: mark_awakened가 exact-match를 하려면 방금 결속한 정확한 pid/lstart/
  # cmdline이 필요한데, 그 값들은 이 함수의 local 변수라 함수를 벗어나면 사라진다 — non-local
  # 전역변수로 노출해 summon()이 mark_awakened 호출 시 그대로 넘기게 한다(단일 스크립트·순차
  # 실행이라 동시 호출 경합 없음 — 병렬 호출로 바뀌면 이 방식은 재검토 필요).
  BOUND_PID="$pid"; BOUND_START="$lstart"; BOUND_CMD="$cmdline"
  echo "[boot_tower] $1: pid결속 완료(pid=$pid, surface=$2, 각성 대기)"
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
  # ★2026-08-05 개명 반영: 리오→데릭(Derek·주인님 둘째 아드님 성함·히브리어 데레크=길) / 리프→노아(Noah).
  #   ★어제 개명 전파에서 이 파일이 누락돼 있었다(그대로 부팅하면 옛 이름으로 되돌아간다).
  case "$1" in
    COO) echo "COO·벤" ;;
    CSO) echo "CSO·데릭" ;;
    reviewer-codex) echo "reviewer-codex·노아" ;;
    reviewer-gemini) echo "reviewer-gemini·젠" ;;
    *) echo "$1" ;;
  esac
}

summon() { # $1=탭명 $2=기동명령 $3=부팅마커 $4=각성문 [$5=후속명령] → exit0=완전성공 exit1=degraded(수동확인필요)
  local exist exist_rc
  exist=$(tab_exists "$1"); exist_rc=$?
  if [ -n "$exist" ]; then
    if [ "$exist_rc" -eq 2 ]; then
      # ★D 근본조치(H-01) 재수정: 편입된 노드는 "생존"만 확인됐지 "각성"은 검증 안 됐으므로
      # (§0 — awakened=False로 정직 기록) 무조건 스킵하지 않고 각성문을 재전송한다. 노아
      # REVISE(HIGH-1·HIGH-3) 반영 — send_line 실패를 삼키지 않고 전파하며(HIGH-1),
      # 후속명령($5)까지 성공해야 mark_awakened로 exact-match 기록한다(HIGH-3 — 편입 직후
      # 기록된 정확한 pid/start/command 지문을 재조회해 넘긴다). 넷 다 성공해야 exit0.
      local adopted_ref="$exist"
      echo "[boot_tower] $1: 기존생존 편입 노드($adopted_ref) — 각성문 재전송(재소환은 생략)"
      local awk_wake_ok=0 awk_post_ok=1 awk_mark_ok=0
      send_line "$adopted_ref" "$4 $LLM_WIKI_BRIEF" && awk_wake_ok=1
      if [ "$awk_wake_ok" -eq 1 ] && [ -n "${5:-}" ]; then
        awk_post_ok=0
        sleep 3
        send_line "$adopted_ref" "$5" && awk_post_ok=1
      fi
      if [ "$awk_wake_ok" -eq 1 ] && [ "$awk_post_ok" -eq 1 ]; then
        local ap_pid ap_start ap_cmd
        IFS=$'\t' read -r ap_pid ap_start ap_cmd < <(python3 - "$1" <<'PYEOF'
import json, os, sys
p = os.path.expanduser("~/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json")
d = json.loads(open(p).read()) if os.path.exists(p) else {}
b = (d.get("_pidbind") or {}).get(sys.argv[1]) or {}
print(f"{b.get('pid','')}\t{b.get('start','')}\t{b.get('command','')}")
PYEOF
)
        mark_awakened "$1" "$adopted_ref" "$ap_pid" "$ap_start" "$ap_cmd" && awk_mark_ok=1
      fi
      if [ "$awk_wake_ok" -eq 1 ] && [ "$awk_post_ok" -eq 1 ] && [ "$awk_mark_ok" -eq 1 ]; then
        echo "[boot_tower] $1: 편입 각성 완료($adopted_ref, 각성문전송 성공, 각성기록 성공)"
        return 0
      fi
      echo "[boot_tower] ⚠ FAIL(degraded): $1 편입 노드 — 각성문전송=${awk_wake_ok}·후속명령=${awk_post_ok}·각성기록=${awk_mark_ok}. 이 노드는 다음 멱등판정에서 죽음으로 오판돼 재소환(이중화)될 수 있다 — master 수동 확인 필요($adopted_ref)."
      return 1
    fi
    echo "[boot_tower] $1: 기존 생존($exist, pid결속 확인) — 소환 생략(멱등)"
    return 0
  fi
  local out sf
  out=$($CMUX new-split "${SPLIT_DIR:-down}" --workspace $WS --surface "${SPLIT_FROM:-$CALLER}")
  sf=$(echo "$out" | grep -o "surface:[0-9]*" | head -1)
  [ -z "$sf" ] && { echo "[boot_tower] FAIL: $1 pane 생성 실패"; return 1; }
  $CMUX rename-tab --workspace $WS --surface "$sf" -- "$(nick_of "$1")"
  roster_set "$1" "$sf"
  local sf_tty; sf_tty=$(capture_tty "$sf")   # ★맨 셸 상태에서만 유효 — 반드시 부팅명령 전송 전에 호출
  send_line "$sf" "cd $AIWORKS && $2"
  local boot_ok=0 bind_ok=0 wake_ok=0 post_ok=1 mark_ok=0
  BOUND_PID=""; BOUND_START=""; BOUND_CMD=""
  wait_boot "$sf" "$3" 90 && boot_ok=1
  bind_process "$1" "$sf" "$2" "$sf_tty" && bind_ok=1
  # ★리프 3차 REVISE(§6-1 — CEO 실증: 오늘 아침 boot_tower 실행 시 COO·reviewer-codex가 "생존은
  # 하되 각성문 미주입" 상태였는데 스크립트는 그 반환값을 버려 감지하지 못했다. 생존≠각성 —
  # send_line("$4 $LLM_WIKI_BRIEF")의 성공까지 확인해야 "각성 완료"라 부를 수 있다.
  send_line "$sf" "$4 $LLM_WIKI_BRIEF" && wake_ok=1
  if [ -n "${5:-}" ]; then
    post_ok=0
    sleep 3
    send_line "$sf" "$5" && post_ok=1
  fi
  # ★4차 REVISE(§7 — 리프 독립수렴): 각성문(+후속명령)까지 전달 성공한 결속에만 awakened=true를
  # 기록한다 — is_bound_alive()가 이 플래그까지 확인해야 다음 실행에서 "생존하지만 미각성"인
  # 노드를 멱등 스킵하지 않고 다시 처리한다(오늘 실사고 재발 방지).
  # ★5차 REVISE(§①): mark_awakened에 방금 bind_process가 결속한 정확한 pid/start/command를
  # 함께 넘겨 exact-match를 강제하고, 그 반환값(mark_ok)을 최종 성공게이트에 포함한다.
  # ★6차 REVISE(단일 잔존): 이 조건에 boot_ok가 빠져 있었다 — boot_ok=0(부팅마커 미확인)인데
  # bind/wake/post가 우연히 1이면 awakened=true가 영속 기록되고, 이번 실행은 summon() 최종
  # 게이트가 exit1로 잡아도 **다음 실행**의 is_bound_alive는 이 영속기록만 보고 true를 반환해
  # 기존생존(멱등 스킵) 경로로 exit0 — "부팅확인 실패가 한 사이클 뒤 정상으로 승격"되는 fail-open.
  # boot_ok를 조건에 추가해 애초에 기록 자체가 안 되게 막는다.
  if [ "$boot_ok" -eq 1 ] && [ "$bind_ok" -eq 1 ] && [ "$wake_ok" -eq 1 ] && [ "$post_ok" -eq 1 ]; then
    mark_awakened "$1" "$sf" "$BOUND_PID" "$BOUND_START" "$BOUND_CMD" && mark_ok=1
  fi
  # ★리프 2차 REVISE(실패 무시): wait_boot·bind_process·각성문 전송·각성기록 실패를 삼키고 무조건
  # "소환 완료"로 종료하면(기존 `|| true`) 오늘 젠 사건과 동일한 결함(판정은 맞았는데 보고가 조용히
  # 성공을 주장)이 보고 경로에 재발한다. one-shot 스크립트라 "다음 사이클이 고쳐줄 것"이란 가정이
  # 성립하지 않으므로 여기서 exit code로 CEO 화면까지 명시 전파한다.
  if [ "$boot_ok" -eq 1 ] && [ "$bind_ok" -eq 1 ] && [ "$wake_ok" -eq 1 ] && [ "$post_ok" -eq 1 ] && [ "$mark_ok" -eq 1 ]; then
    echo "[boot_tower] $1: 소환 완료($sf, pid결속 성공, 각성문 전송 성공, 각성기록 성공)"
    return 0
  fi
  echo "[boot_tower] ⚠ FAIL(degraded): $1 — pane은 생성됐으나 부팅확인=${boot_ok}·pid결속=${bind_ok}·각성문전송=${wake_ok}·후속명령=${post_ok}·각성기록=${mark_ok}. 이 노드는 다음 멱등판정에서 죽음으로 오판돼 재소환(이중화)될 수 있고, 특히 각성문전송=0이면 프로세스는 살아있으나 자기 역할을 모르는 상태(오늘 실사고 사례)다 — master 수동 확인 필요($sf)."
  return 1
}

claude_division_head_model() { # → 엔진배정표.md의 "최신 엔진 자동 승계" 실행앵커에서 Claude 상위티어 모델 CLI 슬러그를 읽음
  # ★별건 수정(2026-08-04 CEO 지시 — 오늘 실사고 근거): 이 자리가 `claude-opus-4-8`로
  # 하드코딩돼 있었다. `.claude/org/엔진배정표.md`가 2026-08-03 "최신 엔진 자동 승계 원칙"으로
  # Claude 본부장·COO 티어를 Opus 4.8→Opus 5로 이미 승계했는데, 이 스크립트는 그 문서를 안
  # 읽고 구 세대 문자열을 계속 써왔다. ★오늘 그 하드코딩을 CEO 자신이 그대로 따라 써서
  # 리서치본부장을 구 세대(Opus 4.8)로 잘못 띄웠고, 주인님이 직접 지적해 정정한 실사고가 있었다
  # (boot_tower와 무관한 수동 소환에서도 같은 문자열이 퍼져 있었다는 뜻 — 정본을 스크립트에
  # 박아두는 방식 자체가 이 부류 사고의 근본원인). 그래서 하드코딩 대신 정본 문서에서 읽는다.
  # ★정직한 한계: 엔진배정표.md는 자유서식 마크다운이라 범용 파서를 만드는 건 이 스크립트
  # 규모에 과잉설계(YAGNI) — 문서가 스스로 "실행 앵커"로 못박아둔 `Claude=`/model
  # claude-opus-5`` 표기 1줄만을 대상으로 하는 최소 grep이다. 문서 형식이 바뀌어 추출에
  # 실패하면 **무음 실패하지 않고** WARN을 찍은 뒤 하드코딩 폴백으로 안전하게 떨어진다(그
  # 폴백값도 실측 갱신 대상 — 정본과 다시 어긋나면 이 WARN이 다음 드리프트를 잡아준다).
  local table="$AIWORKS/.claude/org/엔진배정표.md"
  local model
  model=$(grep -oE 'Claude=`/model [a-z0-9-]+`' "$table" 2>/dev/null | grep -oE 'claude-[a-z0-9-]+' | head -1)
  if [ -z "$model" ]; then
    echo "[boot_tower] WARN: 엔진배정표(.claude/org/엔진배정표.md)에서 Claude 상위티어 모델 추출 실패 — 하드코딩 폴백(claude-opus-5) 사용. 문서 형식이 바뀌었을 수 있으니 CEO 확인 권고." >&2
    model="claude-opus-5"
  fi
  echo "$model"
}

# --- 편성 (모델 배정 정본: .claude/org/엔진배정표.md — COO는 claude_division_head_model()로 동적
#     조회. Fable 가용기에는 CEO만 상위 유지) ---
FAILED_ROLES=""
COO_MODEL=$(claude_division_head_model)
SPLIT_DIR=right SPLIT_FROM=$CALLER summon "COO" \
  "claude --dangerously-skip-permissions --model $COO_MODEL" \
  "bypass permissions" \
  "[COO 각성 - master 주입] 너는 Wave AI Networks의 COO(운영총괄)다. 헌장 .claude/COO_DIRECTIVE.md(자동 로드)의 기동 방식 절대로 각성하라 - 엔진 계약 계승(.claude/_engine-snapshot/WORKER_DIRECTIVE.md 1회 필독) 포함. 복원: output/WaveAI/경영본부/_round/ 최신 COO 핸드오프 + _round/SESSION_STATE.md 재독. 보고 채널 = master pane(탭명 'CEO 관제타워' - cmux_addr.py로 해소). 각성 완료를 push 보고하라." \
  "/fast" || FAILED_ROLES="$FAILED_ROLES COO"

COO_SF=$(tab_exists "COO")
SPLIT_DIR=down SPLIT_FROM=${COO_SF:-$CALLER} summon "CSO" \
  "claude --dangerously-skip-permissions --model claude-sonnet-5" \
  "bypass permissions" \
  "[CSO 각성 - master 주입] 너는 Wave AI Networks의 CSO(최고 시스템 운영자)다. 헌장 .claude/CSO_DIRECTIVE.md(자동 로드 - §0-b 정본보호·부활차단 점검 포함) + .claude/_engine-snapshot/CSO_DIRECTIVE.md 1회 필독. 각성 직후 점검: PHOENIX_FORBID_LIVE 플래그·launchd 프리플라이트 로그·dataless 잔여. 복원: _round/SESSION_STATE.md. 보고 채널 = master pane(탭명 'CEO 관제타워'). 각성 완료를 push 보고하라." \
  || FAILED_ROLES="$FAILED_ROLES CSO"

summon "reviewer-codex" \
  "codex --dangerously-bypass-approvals-and-sandbox" \
  "codex|gpt-" \
  "[리뷰어 각성] 너는 reviewer-codex(검증·반박 리뷰어)다. 계약: 지정 파일만 검토·수정 금지·verdict(ACCEPT|REVISE|BLOCK)+파일:라인 근거·score 금지·결함 발굴이 직무. 전문: .claude/_engine-snapshot/REVIEWER_DIRECTIVE.md (cys 명령은 cmux로 치환). 회신: cmux send --workspace workspace:1 --surface <master> + send-key enter. 각성 완료를 회신하라." \
  || FAILED_ROLES="$FAILED_ROLES reviewer-codex"

CODEX_SF=$(tab_exists "reviewer-codex")
SPLIT_DIR=down SPLIT_FROM=${CODEX_SF:-$CALLER} summon "reviewer-gemini" \
  "agy --dangerously-skip-permissions" \
  "Antigravity|Gemini" \
  "[리뷰어 각성] 너는 reviewer-gemini(적대적 반박 리뷰어 - 전략·UX·콘텐츠·사실성)다. 계약: 지정 파일만·수정 금지·verdict+근거·score 금지·ASCII '->' 표기. 회신: cmux send --workspace workspace:1 --surface <master> + send-key enter. 계정 정본 = greatson79@gmail.com(2026-07-27 개정 — dia-io.com은 소멸계정·재인증 금지). 계정이 그 gmail 계정이 아니면 즉시 보고하라. 각성 완료를 회신하라." \
  || FAILED_ROLES="$FAILED_ROLES reviewer-gemini"

echo "[boot_tower] 편성 결과:"
$CMUX tree --all | grep -E "surface:"
if [ -n "$FAILED_ROLES" ]; then
  echo "[boot_tower] ⚠⚠ FAIL — 결속/부팅 확인 실패 역할:$FAILED_ROLES — master가 반드시 수동 확인할 것(다음 재실행 시 이 노드가 오탐 이중소환될 위험이 있다)."
  exit 1
fi
echo "[boot_tower] 완료 — 각 노드의 각성 회신을 master가 수신·확인하라. agy 계정/모델·COO fast 적용은 회신으로 검증."
