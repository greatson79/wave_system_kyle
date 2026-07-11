#!/bin/sh
# CEO outbox 파일 브리지 — 반드시 cmux 내부 pane에서 실행 (cmux 소켓 접근 필요)
# 목적: background CEO 세션(cmux 외부·소켓 차단)이 outbox에 떨군 명령 파일을
#       cmux 내부에서 대신 실행해 CEO의 실질 outbound(cmux send 등)를 확보한다.
# 종료: 이 pane에서 Ctrl+C 또는 pane 종료. STOP 파일( $BASE/STOP ) 생성 시 자율 종료.
BASE="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
mkdir -p "$BASE/outbox" "$BASE/done"
echo "[bridge] started $(date '+%F %T') pid=$$ (cmux inside=$([ -n "$CMUX_SURFACE_ID" ] && echo yes || echo NO — 소켓 접근 불가, cmux pane에서 실행하라))"
while :; do
  [ -e "$BASE/STOP" ] && { echo "[bridge] STOP file detected — exiting $(date '+%F %T')"; rm -f "$BASE/STOP"; exit 0; }
  for f in "$BASE"/outbox/*.sh; do
    [ -e "$f" ] || continue
    name=$(basename "$f")
    echo "[bridge] $(date '+%T') exec $name"
    sh "$f" > "$BASE/done/$name.log" 2>&1
    echo "exit=$?" >> "$BASE/done/$name.log"
    mv "$f" "$BASE/done/$name"
  done
  sleep 2
done
