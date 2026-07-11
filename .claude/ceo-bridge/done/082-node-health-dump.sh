#!/bin/bash
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
cmux tree --all > "$OUT/health-tree.txt" 2>&1
echo "tree exit=$?" >> "$OUT/health-tree.txt"
