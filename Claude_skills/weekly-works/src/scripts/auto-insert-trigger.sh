#!/bin/bash
# auto-insert-trigger.sh
# Claude PostToolUse 훅에서 호출 — Write/Bash 후 images/ 폴더 상태 확인
# 환경변수 CLAUDE_TOOL_INPUT_FILE_PATH 로 작성된 파일 경로 수신

WEEKLY_WORKS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# 작성된 파일이 매일묵상 images/ 폴더인지 확인
FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

if [ -z "$FILE_PATH" ]; then
  # 표준 입력에서 JSON 읽기 (Claude hook 전달 방식)
  INPUT=$(cat)
  FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
fi

# images/ 폴더 파일인지 확인
if ! echo "$FILE_PATH" | grep -q "/매일묵상/images/"; then
  exit 0
fi

images_dir=$(dirname "$FILE_PATH")

# 5장 확인
count=0
for day in mon tue wed thu fri; do
  for ext in jpg jpeg png webp JPG JPEG PNG WEBP; do
    if [ -f "$images_dir/${day}.${ext}" ]; then
      count=$((count + 1))
      break
    fi
  done
done

if [ "$count" -ge 5 ]; then
  lock_file="$images_dir/.pipeline_running"
  if [ ! -f "$lock_file" ]; then
    touch "$lock_file"
    # 백그라운드 실행 (훅 블로킹 방지)
    bash "$WEEKLY_WORKS_DIR/src/scripts/watch-devotion-images.sh" --single "$images_dir" &
    echo "[auto-insert] 파이프라인 백그라운드 시작 (이미지 ${count}장 감지)"
  fi
fi

exit 0
