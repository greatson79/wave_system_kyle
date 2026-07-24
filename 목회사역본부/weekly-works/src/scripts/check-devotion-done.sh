#!/bin/bash
# check-devotion-done.sh
# captured/ 폴더에 PNG가 10개 이상이면 status.md 매일묵상 완료 처리

WEEKLY_WORKS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# 인수로 week_dir 받거나 자동 탐지
if [ -n "$1" ]; then
  WEEK_DIR="$1"
else
  WEEK_DIR=$(find "$WEEKLY_WORKS_DIR/output" -type d -name "captured" \
    -path "*/매일묵상/captured" | sort | tail -1 | sed 's|/매일묵상/captured||')
fi

CAPTURED_DIR="$WEEK_DIR/매일묵상/captured"
STATUS_FILE="$WEEK_DIR/status.md"

if [ ! -d "$CAPTURED_DIR" ]; then
  echo "captured 폴더 없음: $CAPTURED_DIR"
  exit 0
fi

COUNT=$(find "$CAPTURED_DIR" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')

if [ "$COUNT" -ge 10 ] && [ -f "$STATUS_FILE" ]; then
  NOW=$(date '+%Y-%m-%d %H:%M')
  # pending → 완료 갱신 (이미 완료면 변경 없음)
  sed -i '' "s/| B. 매일묵상 | pending | — |/| B. 매일묵상 | ✅완료 | ${NOW} |/" "$STATUS_FILE"
  echo "✅ status.md 매일묵상 완료 처리 (캡쳐 ${COUNT}개)"
else
  echo "⏳ 캡쳐 ${COUNT}개 — 아직 미완료"
fi
