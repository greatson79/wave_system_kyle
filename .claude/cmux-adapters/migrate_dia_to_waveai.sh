#!/usr/bin/env bash
# =============================================================================
# migrate_dia_to_waveai.sh — output/DiA/ -> output/WaveAI/ 원자적 마이그레이션
# (CSO 설계, 2026-07-12 — P5(4) 주인님 전건승인·COO 협조요청 대응)
#
# ★실행 전 필수 확인(스크립트 자체는 안전장치를 걸지만 운영자 재확인 권장):
#   - COO의 "(3) 완료·(4) 착수 승인" 신호 수신 후에만 실행할 것(race 방지)
#   - git 백업(4a9af96)·tar 백업(~/Ai_works_premigration_backup_20260711.tar.gz) 존재 확인됨
#   - 인텔리전스 폴더·loose 핸드오프 파일 처리는 COO 확인 후 아래 변수로 반영
#
# 원칙: set -euo pipefail로 중단 시 즉시 정지(부분 이동 방지). 각 단계 후 검증.
#       Dry-run 모드(DRY_RUN=1)로 먼저 실행해 계획만 출력 가능.
# =============================================================================
set -euo pipefail

ROOT="/Users/kylechoi/Desktop/Ai_works"
SRC="$ROOT/output/DiA"
DST="$ROOT/output/WaveAI"
DRY_RUN="${DRY_RUN:-1}"   # 기본값=dry-run(안전). 실집행 시 DRY_RUN=0 명시 필요.

# ★v2(2026-07-12 00:3x, COO 지시): node_modules 전량 제외 — dataless 정체 유발 확인
# (크리에이티브본부 rsync가 유독 느렸던 원인 = node_modules 3개 트리·5655개 파일 실측).
# 재생성 가능(신위치 npm install) — 구 node_modules는 후속 별도 정리 대상, 이 스크립트가
# 안 건드린다. ★기존 중단 시점에 WaveAI쪽에 이미 일부 복사된 node_modules 잔여물이 있을 수
# 있음(이번 실행에서 제외 대상이라 추가되진 않으나 기존 잔여물은 그대로 남음 — 후속 정리에서 처리).

# ★COO 확정 지시(2026-07-12) — 둘 다 이동으로 확정. 필요 시 no로 override 가능.
MOVE_INTELLIGENCE="${MOVE_INTELLIGENCE:-yes}"   # ask|yes|no — COO 확정: yes(정본명 한글 유지)
MOVE_LOOSE_HANDOFF="${MOVE_LOOSE_HANDOFF:-yes}" # ask|yes|no — COO 확정: yes(같은 상대위치)

run() {
  echo "+ $*"
  if [ "$DRY_RUN" != "1" ]; then
    "$@"
  fi
}

echo "=== 0. 사전 확인 ==="
[ -d "$SRC" ] || { echo "FATAL: $SRC 없음"; exit 1; }
git -C "$ROOT" rev-parse --verify 4a9af96 >/dev/null 2>&1 || { echo "FATAL: 백업 커밋 4a9af96 확인 불가"; exit 1; }
[ -f "$HOME/Ai_works_premigration_backup_20260711.tar.gz" ] || { echo "FATAL: tar 백업 확인 불가"; exit 1; }
git -C "$ROOT" status --porcelain -- output/DiA/ | grep -q . && { echo "FATAL: output/DiA/ 내부에 미커밋 변경 있음 — race 위험, 먼저 정리할 것"; exit 1; } || true
echo "  (참고: 레포 전체가 아니라 output/DiA/ 스코프만 검사 — 무관 서브모듈 드리프트는 차단 대상 아님)"
echo "OK: 백업·워크트리 확인 통과 (DRY_RUN=$DRY_RUN)"

echo ""
echo "=== 1. 타겟 루트 생성 ==="
run mkdir -p "$DST"

echo ""
echo "=== 2. 단순 이동(병합 없음) ==="
for d in 리서치본부 마케팅본부 크리에이티브본부; do
  if [ -d "$SRC/$d" ]; then
    run rsync -a --remove-source-files --exclude=node_modules "$SRC/$d/" "$DST/$d/"
    run find "$SRC/$d" -type d -empty -delete
  fi
done

if [ "$MOVE_INTELLIGENCE" = "yes" ]; then
  run rsync -a --remove-source-files --exclude=node_modules "$SRC/인텔리전스/" "$DST/인텔리전스/"
  run find "$SRC/인텔리전스" -type d -empty -delete
elif [ "$MOVE_INTELLIGENCE" = "ask" ]; then
  echo "SKIP(확인대기): 인텔리전스 — COO 지시 없음, MOVE_INTELLIGENCE=yes|no로 재실행 필요"
fi

echo ""
echo "=== 3. 병합 A: AI-Tech본부(+개발본부+AI_Tech본부 stub) -> AI-Tech본부 (정본명 유지) ==="
run mkdir -p "$DST/AI-Tech본부"
[ -d "$SRC/AI-Tech본부" ] && run rsync -a --remove-source-files --exclude=node_modules "$SRC/AI-Tech본부/" "$DST/AI-Tech본부/"
[ -d "$SRC/개발본부" ] && run rsync -a --remove-source-files --exclude=node_modules "$SRC/개발본부/" "$DST/AI-Tech본부/"
[ -d "$SRC/AI_Tech본부" ] && run rsync -a --remove-source-files --exclude=node_modules "$SRC/AI_Tech본부/" "$DST/AI-Tech본부/"
run find "$SRC/AI-Tech본부" "$SRC/개발본부" "$SRC/AI_Tech본부" -type d -empty -delete 2>/dev/null || true

echo ""
echo "=== 4. 병합 B: 목회사역-디딤 + 목회사역본부 -> 목회사역 (정본명) ==="
run mkdir -p "$DST/목회사역"
[ -d "$SRC/목회사역-디딤" ] && run rsync -a --remove-source-files --exclude=node_modules "$SRC/목회사역-디딤/" "$DST/목회사역/"
[ -d "$SRC/목회사역본부" ] && run rsync -a --remove-source-files --exclude=node_modules "$SRC/목회사역본부/" "$DST/목회사역/"
run find "$SRC/목회사역-디딤" "$SRC/목회사역본부" -type d -empty -delete 2>/dev/null || true

echo ""
echo "=== 5. .DS_Store 정리(이관 대상 아님) ==="
run find "$SRC" -name ".DS_Store" -delete
run find "$DST" -name ".DS_Store" -delete

echo ""
echo "=== 6. loose 파일(agy2_작업인계_핸드오프_0704.md) ==="
if [ "$MOVE_LOOSE_HANDOFF" = "yes" ]; then
  [ -f "$SRC/agy2_작업인계_핸드오프_0704.md" ] && run mv "$SRC/agy2_작업인계_핸드오프_0704.md" "$DST/"
elif [ "$MOVE_LOOSE_HANDOFF" = "ask" ]; then
  echo "SKIP(확인대기): loose 핸드오프 파일 — MOVE_LOOSE_HANDOFF=yes|no로 재실행 필요"
fi

echo ""
echo "=== 7. 경로 참조 갱신(스코프 확정분 — 경영본부 참조는 불변이므로 미포함) ==="
# 7-a. 대시보드 커맨드
if [ -f "$ROOT/.claude/commands/대시보드.md" ]; then
  run sed -i '' 's#output/DiA/AI-Tech본부#output/WaveAI/AI-Tech본부#g' "$ROOT/.claude/commands/대시보드.md"
fi
# 7-b. 루트 COO_HANDOFF.md (목회사역-디딤 -> 목회사역 정본명 반영 포함)
if [ -f "$ROOT/COO_HANDOFF.md" ]; then
  run sed -i '' \
    -e 's#output/DiA/리서치본부#output/WaveAI/리서치본부#g' \
    -e 's#output/DiA/목회사역-디딤#output/WaveAI/목회사역#g' \
    -e 's#output/DiA/크리에이티브본부#output/WaveAI/크리에이티브본부#g' \
    "$ROOT/COO_HANDOFF.md"
fi
# 7-c. REVIEWER_VERDICT_CONTRACT.md (마케팅본부 예시 경로)
if [ -f "$ROOT/_round/REVIEWER_VERDICT_CONTRACT.md" ]; then
  run sed -i '' 's#output/DiA/마케팅본부#output/WaveAI/마케팅본부#g' "$ROOT/_round/REVIEWER_VERDICT_CONTRACT.md"
fi
# 7-d. 일반 패턴 문서 3건 — 경영본부 예외를 명시하는 문구로 교체(단순 치환 아님, 수동 대조 필요)
echo "  ★수동확인 필요(일반 패턴 문서 — 자동치환 보류): MASTER_DIRECTIVE.md L28/L92, CLAUDE.md L145, HQ_SUMMON_STANDARD.md L27"
echo "    (경영본부만 output/DiA/ 유지 + 나머지 output/WaveAI/ 인 '이원화 규칙'으로 문구 수정 필요 — 단순 sed 치환 위험)"

echo ""
echo "=== 8. 확인 불요 판정(변경 없음 — 전부 경영본부 스코프 확인됨) ==="
echo "  COO_DIRECTIVE.md / CSO_DIRECTIVE.md / boot_tower.sh / council_prompt.py: DiA참조 전량 경영본부 스코프 — 변경 불요"

echo ""
echo "=== 9. 최종 상태 ==="
run bash -c "ls -la '$SRC'"
run bash -c "ls -la '$DST'"

echo ""
echo "=== DRY_RUN=$DRY_RUN 완료. 실집행은 DRY_RUN=0 MOVE_INTELLIGENCE=yes|no MOVE_LOOSE_HANDOFF=yes|no bash $0 ==="
