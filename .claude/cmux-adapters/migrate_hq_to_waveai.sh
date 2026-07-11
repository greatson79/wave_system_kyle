#!/usr/bin/env bash
# =============================================================================
# migrate_hq_to_waveai.sh — output/DiA/경영본부 -> output/WaveAI/경영본부
# ★자기참조 마이그레이션(COO/CSO SOT가 이 경로 자체) — 최고 주의
# (CSO 설계, 2026-07-12 — 주인님 최종 확장·COO 원자순서 제안 반영)
# =============================================================================
set -euo pipefail

ROOT="/Users/kylechoi/Desktop/Ai_works"
SRC="$ROOT/output/DiA/경영본부"
DST="$ROOT/output/WaveAI/경영본부"
DRY_RUN="${DRY_RUN:-1}"

run() { echo "+ $*"; [ "$DRY_RUN" != "1" ] && "$@"; true; }

echo "=== 0. 사전 확인 ==="
[ -d "$SRC" ] || { echo "FATAL: $SRC 없음"; exit 1; }
[ -f "$HOME/Ai_works_output_REAL_20260712_0027.tar.gz" ] || { echo "FATAL: 백업 확인불가"; exit 1; }
SRC_COUNT=$(find "$SRC" -type f -not -name ".DS_Store" | wc -l | tr -d ' ')
echo "OK: 이동전 경영본부 실콘텐츠=$SRC_COUNT (DRY_RUN=$DRY_RUN)"

echo ""
echo "=== 1. 이동(rsync -a --remove-source-files, node_modules 없음 확인된 경로) ==="
run mkdir -p "$ROOT/output/WaveAI"
run rsync -a --remove-source-files --exclude=node_modules "$SRC/" "$DST/"
run find "$SRC" -type d -empty -delete

echo ""
echo "=== 2. 이동 후 count 검증 ==="
if [ "$DRY_RUN" != "1" ]; then
  DST_COUNT=$(find "$DST" -type f -not -name ".DS_Store" | wc -l | tr -d ' ')
  echo "이동후 신위치 실콘텐츠=$DST_COUNT (이동전=$SRC_COUNT)"
  [ "$DST_COUNT" -ge "$SRC_COUNT" ] || { echo "FATAL: count 불일치 — 중단"; exit 1; }
fi

echo ""
echo "=== 3. ★자기참조 경로 갱신 — 신위치 내부의 절대경로 자기참조 전체 치환 ==="
if [ "$DRY_RUN" != "1" ]; then
  run grep -rl "output/DiA/경영본부" "$DST" 2>/dev/null | while read -r f; do
    sed -i '' 's#output/DiA/경영본부#output/WaveAI/경영본부#g' "$f"
    echo "  치환: $f"
  done
else
  echo "  (dry-run) 대상 파일 목록:"
  grep -rl "output/DiA/경영본부" "$SRC" 2>/dev/null || true
fi

echo ""
echo "=== 4. 외부 참조 파일 갱신(비denylist — COO 지정 B/C/D/E 스코프) ==="
for f in \
  "$ROOT/.claude/cmux-adapters/boot_tower.sh" \
  "$ROOT/.claude/cmux-adapters/council_prompt.py" \
  "$ROOT/_round/SESSION_STATE.md" \
  "$ROOT/COO_HANDOFF.md" \
  "$HOME/Library/LaunchAgents/com.wave.aiworks.sweep-collector.plist"
do
  if [ -f "$f" ] && grep -q "output/DiA/경영본부" "$f" 2>/dev/null; then
    run sed -i '' 's#output/DiA/경영본부#output/WaveAI/경영본부#g' "$f"
    echo "  치환: $f"
  else
    echo "  스킵(참조없음/파일없음): $f"
  fi
done

echo ""
echo "=== 5. ★denylist 헌장(터치 안 함 — CEO 몫) ==="
echo "  COO_DIRECTIVE.md / CSO_DIRECTIVE.md / MASTER_DIRECTIVE.md — 이 스크립트는 건드리지 않음"

echo ""
echo "=== 6. 검증 ==="
run bash -c "echo 'DiA 잔존:'; ls -la '$ROOT/output/DiA/' 2>&1"
run bash -c "echo '경영본부 참조 grep(denylist 3파일 제외 스코프에서 0이어야 함):'; grep -rl 'output/DiA/경영본부' '$ROOT' --include='*.md' --include='*.py' --include='*.sh' 2>/dev/null | grep -v '_archive' | grep -v 'ceo-bridge/done' | grep -v 'COO_DIRECTIVE.md' | grep -v 'CSO_DIRECTIVE.md' | grep -v 'MASTER_DIRECTIVE.md' | grep -v '/output/WaveAI/' || echo '  0건(정상)'"

echo ""
echo "=== DRY_RUN=$DRY_RUN 완료 ==="
