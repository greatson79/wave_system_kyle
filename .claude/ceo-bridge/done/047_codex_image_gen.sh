#!/bin/sh
# 인스타툰 Opus48 v2 — Codex 코드검수(workspace:1/surface:1)에 이미지 생성 지시
SCRIPT="/Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/generate_cuts.py"

echo "[047] Codex(코드검수 workspace:1/surface:1)에 전달"
cmux send --workspace workspace:1 --surface surface:1 "python3 $SCRIPT"
cmux send-key --workspace workspace:1 --surface surface:1 enter
echo "[047] 전달 완료"
