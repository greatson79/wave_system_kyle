#!/bin/bash
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
cmux tree --all > "$OUT/es-tree.txt" 2>&1
for s in 10 71 72; do
  cmux read-screen --workspace workspace:6 --surface surface:$s > "$OUT/es-s$s.txt" 2>&1
done
touch "$OUT/es-done"
