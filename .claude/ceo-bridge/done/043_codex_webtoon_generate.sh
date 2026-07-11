#!/bin/sh
# 인스타툰 Opus48 v2 이미지 생성 — Codex에 전달
# bridge.sh가 cmux 내부에서 실행해야 작동
SCRIPT="/Users/kylechoi/Desktop/Ai_works/output/DiA/크리에이티브본부/AI트렌드/인스타툰_Opus48_v2_0702/generate_cuts.py"

# Codex pane 동적 탐색 (tab 이름 기반)
CODEX_INFO=$(cmux tree --all 2>/dev/null | grep -i "codex" | head -1)
echo "[043] Codex 탐색: $CODEX_INFO"

# workspace와 surface 추출
WS=$(echo "$CODEX_INFO" | grep -oE 'workspace:[0-9]+' | grep -oE '[0-9]+' | head -1)
SF=$(echo "$CODEX_INFO" | grep -oE 'surface:[0-9]+' | grep -oE '[0-9]+' | head -1)

if [ -z "$WS" ] || [ -z "$SF" ]; then
  echo "[043] WARN: Codex pane 미탐지. 직접 python3 실행 시도."
  python3 "$SCRIPT"
else
  echo "[043] Codex → ws=$WS surface=$SF"
  CMD="python3 $SCRIPT"
  cmux send --workspace "$WS" --surface "$SF" "$CMD"
  cmux send-key --workspace "$WS" --surface "$SF" enter
  echo "[043] Codex에 생성 명령 전달 완료"
fi
