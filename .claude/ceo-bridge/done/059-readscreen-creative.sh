#!/bin/sh
# 059: 크리에이티브 ws2 화면 실측 (인스타툰 v2 이미지 생성 오류 진단)
D=/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/done
cmux read-screen --workspace workspace:2 --surface surface:6 > "$D/screen-cri-s6.txt" 2>&1
cmux read-screen --workspace workspace:2 --surface surface:55 > "$D/screen-cri-s55.txt" 2>&1
cmux tree --all > "$D/tree-latest.txt" 2>&1
