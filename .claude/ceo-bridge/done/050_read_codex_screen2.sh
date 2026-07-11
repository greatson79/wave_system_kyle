#!/bin/sh
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/done/codex_screen_latest.txt"
cmux read-screen --workspace workspace:1 --surface surface:1 > "$OUT" 2>&1
echo "[050] Codex 화면 재캡처"
cat "$OUT"
