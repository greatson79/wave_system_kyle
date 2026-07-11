#!/bin/sh
# Codex(코드검수) 화면 현재 상태 확인
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/done/codex_screen_latest.txt"
cmux read-screen --workspace workspace:1 --surface surface:1 > "$OUT" 2>&1
echo "[049] Codex 화면 캡처 완료"
cat "$OUT"
