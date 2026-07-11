#!/bin/bash
sleep 15
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
cmux read-screen --workspace workspace:1 --surface surface:54 > "$OUT/health3-s54.txt" 2>&1
cmux read-screen --workspace workspace:1 --surface surface:1 > "$OUT/health3-s1.txt" 2>&1
touch "$OUT/health3-done"
