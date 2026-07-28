#!/usr/bin/env bash
# newout.sh — 산출물 폴더를 표준 구조로 만든다
#   output/WaveAI/{본부}/{카테고리}/{MMDD}_{제목}/
#
# 사용: bash .claude/bin/newout.sh <본부> <카테고리> <제목>
# 예:   bash .claude/bin/newout.sh 크리에이티브본부 AI트렌드실전팁 에이전트에게_일을_맡기는_법
#
# 규약 정본: .claude/org/산출물_저장구조_규약.md
# 계약: stdout = 생성된 절대경로 1줄 / 실패 시 비영 exit

set -euo pipefail

DIV="${1:-}"; CAT="${2:-}"; TITLE="${3:-}"
if [ -z "$DIV" ] || [ -z "$CAT" ] || [ -z "$TITLE" ]; then
  echo "usage: newout.sh <본부> <카테고리> <제목>" >&2
  echo "  예: newout.sh 크리에이티브본부 AI트렌드실전팁 에이전트에게_일을_맡기는_법" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/Desktop/Ai_works")"
BASE="$ROOT/output/WaveAI"

# 본부 실재 확인 — 오타로 새 본부 폴더가 생기는 것을 막는다
if [ ! -d "$BASE/$DIV" ]; then
  echo "본부 폴더가 없다: $BASE/$DIV" >&2
  echo "실재하는 본부: $(ls -1 "$BASE" | grep -v '^_' | tr '\n' ' ')" >&2
  exit 2
fi

# 날짜는 실행 시각에서 자동 — 수기 입력 금지(오기재 방지)
MMDD="$(date +%m%d)"
# 제목의 공백은 _로
TITLE_SAFE="$(echo "$TITLE" | tr ' ' '_')"
DEST="$BASE/$DIV/$CAT/${MMDD}_${TITLE_SAFE}"

if [ -d "$DEST" ]; then
  echo "이미 존재한다(덮어쓰지 않음): $DEST" >&2
  echo "$DEST"
  exit 0
fi

mkdir -p "$DEST"
echo "$DEST"
