#!/bin/bash
# 숏츠 렌더링 스크립트
# 사용법: bash render.sh <output_mp4_path>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_PATH="${1:-$PROJECT_DIR/out/shorts.mp4}"

echo "렌더링 시작..."
echo "출력: $OUTPUT_PATH"

mkdir -p "$(dirname "$OUTPUT_PATH")"

cd "$PROJECT_DIR"
npx remotion render src/index.ts SermonShorts "$OUTPUT_PATH" \
  --overwrite \
  --log=verbose 2>&1

echo "✅ 렌더링 완료: $OUTPUT_PATH"
