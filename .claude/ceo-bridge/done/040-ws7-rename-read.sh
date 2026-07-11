#!/bin/sh
OUT=/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/gemma-inspect.txt
{
  echo "=== rename 시도 ==="
  cmux rename-workspace --workspace workspace:7 "젬마" 2>&1 || cmux rename --workspace workspace:7 "젬마" 2>&1 || echo "RENAME_FAILED — help 출력:"
  cmux --help 2>&1 | head -40
  echo "=== ws7 젬마 화면 (전체 스크롤백) ==="
  cmux read-screen --workspace workspace:7 --surface surface:26 --scrollback 2>&1 || cmux read-screen --workspace workspace:7 --surface surface:26 2>&1
} > "$OUT" 2>&1
