#!/bin/bash
# watch-devotion-images.sh
# images/ 폴더에 mon~fri 이미지 5장이 모이면 insert-images.py + capture-a4.js 자동 실행

WEEKLY_WORKS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="$WEEKLY_WORKS_DIR/src/scripts/watcher.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 현재 주차 output 경로 자동 탐지 (가장 최근 수정된 주차 폴더)
find_current_week() {
  find "$WEEKLY_WORKS_DIR/output" -type d -name "images" \
    -path "*/매일묵상/images" | sort | tail -1 | sed 's|/매일묵상/images||'
}

# images/ 폴더에 mon~fri 이미지가 모두 있는지 확인
check_images_ready() {
  local images_dir="$1"
  local count=0
  for day in mon tue wed thu fri; do
    for ext in jpg jpeg png webp JPG JPEG PNG WEBP; do
      if [ -f "$images_dir/${day}.${ext}" ]; then
        count=$((count + 1))
        break
      fi
    done
  done
  [ "$count" -ge 5 ]
}

# insert-images 파이프라인 실행
run_insert_pipeline() {
  local week_dir="$1"
  local week_num="$2"
  local output_rel

  # output/ 기준 상대 경로 추출
  output_rel=$(echo "$week_dir" | sed "s|$WEEKLY_WORKS_DIR/||")

  log "▶ insert-images 파이프라인 시작: $output_rel"

  cd "$WEEKLY_WORKS_DIR" || exit 1

  # 1단계: insert-images.py (이미지 교체; 모든 HTML에 로컬 상대 경로 사용)
  log "  1단계: 이미지 삽입 중..."
  python3 src/scripts/insert-images.py "$week_num" "$output_rel" >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    log "  ❌ insert-images.py 실패"
    return 1
  fi

  # 2단계: capture-a4.js (Puppeteer A4 캡쳐)
  log "  2단계: A4 캡쳐 중..."
  node src/scripts/capture-a4.js "$output_rel/매일묵상" >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    log "  ❌ capture-a4.js 실패"
    return 1
  fi

  # 3단계: status.md 완료 처리
  log "  3단계: status.md 갱신..."
  bash "$(dirname "$0")/check-devotion-done.sh" "$week_dir" >> "$LOG_FILE" 2>&1

  log "✅ 파이프라인 완료: $output_rel"
}

# 주차 번호 추출 (output/5월/5주차 → 22 또는 폴더명 기반)
extract_week_num() {
  local week_dir="$1"
  # data/sermon-plan-2026.json에서 주차 번호 매핑 대신
  # 폴더명 기반으로 추출 시도: "5주차" → 22 (근사)
  # insert-images.py는 output 경로를 직접 받으므로 week_num 불필요
  echo "auto"
}

# --single 모드: Claude 훅에서 호출 시 지정 폴더를 즉시 1회 처리
if [ "$1" = "--single" ]; then
  images_dir="$2/매일묵상/images"
  week_dir="$2"
  if check_images_ready "$images_dir"; then
    run_insert_pipeline "$week_dir" "auto"
    lock_file="$images_dir/.pipeline_running"
    rm -f "$lock_file"
  else
    log "⏳ --single: 이미지 미완성 ($(ls "$images_dir" 2>/dev/null | wc -l | tr -d ' ')장)"
  fi
  exit 0
fi

# fswatch 설치 확인
if ! command -v fswatch &>/dev/null; then
  echo "❌ fswatch 미설치. 설치 후 재실행:"
  echo "   brew install fswatch"
  exit 1
fi

log "🔍 이미지 감시 시작 (weekly-works)"
log "   대상: output/**/매일묵상/images/"

# output 폴더 전체를 감시
fswatch -0 -e ".*" -i "\.(jpg|jpeg|png|webp|JPG|JPEG|PNG|WEBP)$" \
  "$WEEKLY_WORKS_DIR/output" | \
while IFS= read -r -d '' changed_file; do
  # images/ 폴더 내 파일인지 확인
  if echo "$changed_file" | grep -q "/매일묵상/images/"; then
    images_dir=$(dirname "$changed_file")
    week_dir=$(echo "$images_dir" | sed 's|/매일묵상/images||')

    log "📥 이미지 감지: $changed_file"

    # 5장 모두 있는지 확인 (디바운스: 2초 대기)
    sleep 2
    if check_images_ready "$images_dir"; then
      # 이미 파이프라인 실행 중인지 확인 (락 파일)
      lock_file="$images_dir/.pipeline_running"
      if [ ! -f "$lock_file" ]; then
        touch "$lock_file"
        run_insert_pipeline "$week_dir" "auto"
        rm -f "$lock_file"
      else
        log "⏭ 이미 파이프라인 실행 중 — 건너뜀"
      fi
    else
      log "⏳ 이미지 대기 중 ($(ls "$images_dir" 2>/dev/null | wc -l | tr -d ' ')장)"
    fi
  fi
done
