#!/bin/sh
# Codex(코드검수 ws:1/s:1)에 직접 작업 지시 프롬프트 전달
MSG="gpt-image-2로 인스타툰 5컷 이미지를 생성해줘. 스크립트: python3 /Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/generate_cuts.py — 이 스크립트를 Bash 도구로 실행해줘. 완료 후 생성된 파일 목록 확인."
cmux send --workspace workspace:1 --surface surface:1 "$MSG"
cmux send-key --workspace workspace:1 --surface surface:1 enter
echo "[048] Codex 작업 지시 전달 완료"
