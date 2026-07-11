#!/bin/sh
# 인스타툰 Opus48 v2 — Codex(코드검수 ws1/s1)에 정확 전달
SCRIPT="/Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/generate_cuts.py"
WS=1
SF=1

echo "[045] Codex(코드검수 ws=$WS s=$SF)에 이미지 생성 명령 전달"
cmux send --workspace "$WS" --surface "$SF" "cd /Users/kylechoi/Desktop/Ai_works && python3 $SCRIPT"
cmux send-key --workspace "$WS" --surface "$SF" enter
echo "[045] 전달 완료"
