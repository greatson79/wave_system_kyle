#!/bin/bash
# 059 — 컷2·5 3D 재생성 (스타일 통일)
SCRIPT="/Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/regen_cut2_cut5.py"

cmux send --workspace workspace:2 --surface surface:55 "python3 '$SCRIPT'"
cmux send-key --workspace workspace:2 --surface surface:55 enter
echo "[059] s55 Codex에 컷2·5 3D 재생성 지시 전달"
