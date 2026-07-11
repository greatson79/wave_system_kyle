#!/bin/bash
# Watchdog: 러너가 죽으면 자동 재개. 110 완료 또는 명시적 stop 파일 생성 시 종료.
set -u
cd "$(dirname "$0")"

TITLE="AI 가상 부교역자팀 (churchTeam)"
GOAL="담임목사가 목회적 통찰·사역 기획·다매체 실행을 할 수 있도록 돕는 단일 가상 AI 교역자팀 (통찰진/기획진/실행진 3직무, 로컬 실행, 비개발자 운용, didim 유지·확장)"
PROJECT_DIR="$HOME/ax_church"
STOP_FILE=".watchdog_stop"
WATCH_LOG="watchdog.log"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $*" | tee -a "$WATCH_LOG"; }

log "=== Watchdog 시작 ==="
log "정지하려면: touch $(pwd)/$STOP_FILE"

while true; do
  if [ -f "$STOP_FILE" ]; then
    log "STOP 파일 감지 → 워치독 종료"
    rm -f "$STOP_FILE"
    exit 0
  fi

  # 종료 조건: state.json status==completed 또는 current_step>110
  STATUS=$(python3 -c "import json; s=json.load(open('state.json')); print(s.get('status','?'), s.get('current_step',0))" 2>/dev/null)
  STAT_NAME=$(echo "$STATUS" | awk '{print $1}')
  CUR_STEP=$(echo "$STATUS" | awk '{print $2}')
  if [ "$STAT_NAME" = "completed" ] || [ "${CUR_STEP:-0}" -gt 110 ]; then
    log "🎉 전체 완료 — status=$STAT_NAME step=$CUR_STEP"
    exit 0
  fi

  # 러너 살아있나?
  if pgrep -f "run.py --from\|run.py --resume" > /dev/null; then
    sleep 60
    continue
  fi

  # 러너 죽음 → 재개
  log "러너 부재 감지 (last step=$CUR_STEP) — 30초 후 재개 시도"
  sleep 30

  # rate_limit_state 있으면 --resume 우선 (러너가 남은 대기 자동 처리)
  HAS_RL=$(python3 -c "import json; s=json.load(open('state.json')); print('1' if s.get('rate_limit_state') else '0')" 2>/dev/null)

  if [ "$HAS_RL" = "1" ]; then
    log "rate_limit_state 감지 → --resume 사용"
    nohup python3 run.py --resume \
      --title "$TITLE" --goal "$GOAL" \
      --project-dir "$PROJECT_DIR" \
      >> execution.log 2>&1 &
  else
    # state.json의 current_step부터
    NEXT="${CUR_STEP:-62}"
    log "정상 종료 추정 → --from $NEXT"
    nohup python3 run.py --from "$NEXT" \
      --title "$TITLE" --goal "$GOAL" \
      --project-dir "$PROJECT_DIR" \
      >> execution.log 2>&1 &
  fi

  sleep 10
  if pgrep -f "run.py" > /dev/null; then
    log "✅ 러너 재시작 성공 (PID $(pgrep -f 'run.py' | head -1))"
  else
    log "⚠ 재시작 실패 — 5분 후 재시도"
    sleep 300
  fi
done
