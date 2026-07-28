#!/usr/bin/env bash
# html2pdf.sh — HTML을 PDF로 렌더한다 (Chrome 헤드리스 · ★키체인 무접촉 · 프로세스 잔존 없음)
#
# 사용: bash .claude/bin/html2pdf.sh <input.html> <output.pdf>
#
# ★왜 이 래퍼를 쓰나 (2026-07-28 주인님 지시 — 실사고 2건에서 나온 규율)
#  1) 키체인 무접촉: `Chrome --headless`를 그냥 부르면 **기본 사용자 프로필**을 열어 macOS
#     키체인(Chrome Safe Storage)을 참조한다. 응답할 사람이 없는 승인 창이 떠서 방치되고,
#     hang되면 SIGTERM도 안 먹는다(2026-07-28 SecurityAgent kill -9로 정리).
#     ⇒ 매 실행마다 **임시 격리 프로필** + `--password-store=basic`.
#  2) 프로세스 잔존 방지: 새 프로필로 띄우면 Chrome **업데이터가 뒤에서 계속 돌아
#     프로세스가 자연 종료하지 않는다**(실측: 렌더는 끝났는데 45초+ 생존).
#     ⇒ "프로세스 종료"를 기다리지 않고 **산출 파일이 안정됐는지**로 판정한 뒤,
#        우리가 **프로세스 그룹째** 정리한다.
#  3) 프로세스 그룹 격리: macOS엔 `setsid`가 없다. python3 `start_new_session=True`로
#     새 세션을 열어, 종료 시 **이 pane의 동료 프로세스를 말려들게 하지 않는다**
#     (`kill 0`·`pkill` 금지 — CSO 헌장 §3).
#
# 계약: stdout = 출력 경로 1줄 / 실패 시 비영 exit (fail-closed)
#   exit 1 = 인자 오류 · 2 = 입력 없음 · 3 = Chrome 없음 · 4 = 렌더 실패(산출물 없음/과소/미안정)

set -euo pipefail

IN="${1:-}"
OUT="${2:-}"
MIN_BYTES="${MIN_PDF_BYTES:-4096}"     # 이보다 작으면 렌더 실패로 본다
TIMEOUT_S="${PDF_TIMEOUT_S:-90}"       # 산출물 안정까지 최대 대기

if [ -z "$IN" ] || [ -z "$OUT" ]; then
  echo "usage: html2pdf.sh <input.html> <output.pdf>" >&2
  exit 1
fi
[ -f "$IN" ] || { echo "입력 파일 없음: $IN" >&2; exit 2; }

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome을 찾을 수 없다: $CHROME" >&2; exit 3; }

ABS_IN="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"                            # 이전 산출물을 지워 "갱신됐는가"를 결정론으로 본다

CHROME="$CHROME" ABS_IN="$ABS_IN" OUT="$OUT" MIN_BYTES="$MIN_BYTES" TIMEOUT_S="$TIMEOUT_S" \
python3 <<'PY'
import os, sys, time, shutil, signal, subprocess, tempfile

chrome  = os.environ["CHROME"]
src     = os.environ["ABS_IN"]
out     = os.environ["OUT"]
min_b   = int(os.environ["MIN_BYTES"])
limit   = int(os.environ["TIMEOUT_S"])

profile = tempfile.mkdtemp(prefix="chrome-pdf-")
args = [
    chrome,
    "--headless=new", "--disable-gpu",
    f"--user-data-dir={profile}",
    "--password-store=basic",          # ★키체인 대신 평문 백엔드 — 임시 프로필이라 저장물 없음
    "--no-first-run", "--no-default-browser-check",
    "--disable-extensions", "--disable-sync",
    "--disable-background-networking",  # 업데이터·핑 억제(그래도 남는 잔존은 아래서 정리)
    "--disable-component-update", "--disable-default-apps",
    "--metrics-recording-only", "--no-service-autorun",
    "--no-pdf-header-footer",
    f"--print-to-pdf={out}",
    f"file://{src}",
]

# ★새 세션으로 띄운다 — 종료 시 부모 pane의 동료 프로세스를 말려들게 하지 않는다
proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        start_new_session=True)

def finish(code, msg=None):
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)   # 기록된 그룹만 종료
        time.sleep(0.6)
        if proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    shutil.rmtree(profile, ignore_errors=True)
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(code)

# 판정 기준 = 프로세스 종료가 아니라 **산출 파일이 생기고 크기가 안정됐는가**
stable_since, last = None, -1
deadline = time.time() + limit
while time.time() < deadline:
    time.sleep(0.5)
    if not os.path.exists(out):
        continue
    size = os.path.getsize(out)
    if size == last and size > 0:
        if stable_since is None:
            stable_since = time.time()
        elif time.time() - stable_since >= 1.5:      # 1.5초간 크기 불변 = 쓰기 완료
            break
    else:
        stable_since, last = None, size

if not os.path.exists(out):
    finish(4, f"렌더 실패: 산출물이 생성되지 않았다 ({out})")
size = os.path.getsize(out)
if size < min_b:
    finish(4, f"렌더 실패 의심: 산출물이 과소하다 ({size} bytes < {min_b})")

print(out)
finish(0)
PY
