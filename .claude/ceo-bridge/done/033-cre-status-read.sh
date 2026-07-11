#!/bin/sh
OUT=/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/cre-screen.txt
cmux read-screen --workspace workspace:2 --surface surface:6 > "$OUT" 2>&1
