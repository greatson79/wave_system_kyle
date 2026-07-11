#!/bin/sh
OUT=/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/ws7-probe.txt
{
  echo "=== cmux tree --all (ws7 부분) ==="
  cmux tree --all
} > "$OUT" 2>&1
