#!/bin/sh
# 현재 cmux tree 갱신
cmux tree --all > /Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/done/tree-latest.txt 2>&1
echo "[046] tree 갱신 완료"
cat /Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/done/tree-latest.txt
