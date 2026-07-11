#!/bin/bash
sleep 40
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
for s in 54 3 2 22 1; do
  cmux read-screen --workspace workspace:1 --surface surface:$s > "$OUT/health2-s$s.txt" 2>&1
done
touch "$OUT/health2-done"
