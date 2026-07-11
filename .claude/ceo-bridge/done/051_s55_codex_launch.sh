#!/bin/sh
# s55(크리에이티브 Ai_works 터미널)에서 Codex 소환 + 이미지 생성 지시
SCRIPT="/Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/generate_cuts.py"

echo "[051] s55 현재 상태 확인"
cmux read-screen --workspace workspace:2 --surface surface:55 > /tmp/s55_screen.txt 2>&1
cat /tmp/s55_screen.txt

echo "[051] s55에 Codex 소환"
cmux send --workspace workspace:2 --surface surface:55 "codex --dangerously-bypass-approvals-and-sandbox"
cmux send-key --workspace workspace:2 --surface surface:55 enter

sleep 5

echo "[051] Codex 기동 후 이미지 생성 지시"
cmux send --workspace workspace:2 --surface surface:55 "python3 $SCRIPT 실행해줘. gpt-image-2로 인스타툰 5컷 이미지 생성 태스크야."
cmux send-key --workspace workspace:2 --surface surface:55 enter
echo "[051] 완료"
