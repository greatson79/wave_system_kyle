#!/usr/bin/env bash
# 스킬 레지스트리 빌더 — 루트 .claude/skills/ 에 절대경로 디렉토리 심링크 생성
# 재실행 안전(idempotent). 폴더정리 후 경로만 갱신해 재실행하면 레지스트리 재생성됨.
# 규칙: frontmatter name이 같은 스킬은 정본 1개만 등록(이름충돌 방지).
set -u
BASE="/Users/kylechoi/Desktop/Ai_works"
REG="$BASE/.claude/skills"
mkdir -p "$REG"

# 매니페스트: "레지스트리명|타겟 디렉토리(BASE 기준 상대)"
# 타겟은 SKILL.md(또는 별칭)를 가진 실제 스킬 디렉토리.
MANIFEST=(
# ── 인프라/메타 (정본 1개씩) ──
"workflow-generator|Vibe-Practice/AgenticWorkflow-main/.claude/skills/workflow-generator"
"doctoral-writing|Vibe-Practice/AgenticWorkflow-main/.claude/skills/doctoral-writing"
"skill-creator|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/skill-creator"
"subagent-creator|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/subagent-creator"
"slash-command-creator|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/slash-command-creator"
"hook-creator|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/hook-creator"
# ── 교회 주간사역 (weekly-works) ──
"sermon|Claude_skills/weekly-works/.claude/skills/sermon"
"weekly-devotion|Claude_skills/weekly-works/.claude/skills/weekly-devotion"
"prayer-doc|Claude_skills/weekly-works/.claude/skills/prayer-doc"
"insert-images|Claude_skills/weekly-works/.claude/skills/insert-images"
"design-template-scout|Claude_skills/weekly-works/.claude/skills/design-template-scout"
"bulletin|Claude_skills/weekly-works/.claude/skills/bulletin"
"shorts|Claude_skills/weekly-works/.claude/skills/shorts"
"small-group|Claude_skills/weekly-works/.claude/skills/small-group"
"sns-cardnews|Claude_skills/weekly-works/.claude/skills/sns-cardnews"
"team-leader|Claude_skills/weekly-works/.claude/skills/team-leader"
"brand-guidelines|Claude_skills/weekly-works/.agents/skills/brand-guidelines"
"canvas-design|Claude_skills/weekly-works/.agents/skills/canvas-design"
# ── 연구·콘텐츠·강의 ──
"research|Claude_skills/.claude/skills/research"
"nlm-skill|.agents/skills/nlm-skill"
"writing-workflow|Claude_skills/Writingskills/writing-workflow"
"course-design|opencode/course-design"
"gpt-codex-intro|opencode/gpt-codex-intro"
"lecture-design|Claude_skills/lecture_skill_build/skill"
"youth-life-planner|Claude_skills/youth_life_plan"
"brunch-writing-workflow|Claude_skills/Writingskills/brunch-writing-workflow"
# ── 교회 행정 ──
"church-admin|Claude_skills/Church-Admin-AgenticWorkflow-main/church-admin/.claude/skills/church-admin"
# ── Wave-AI (오케스트레이터 정본) ──
"wave-orchestrator|Claude_skills/Wave-AI"
# ── 프로젝트 결합형: 환경스캐닝 ──
"env-scanner|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/env-scanner"
"youtube-collector|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/youtube-collector"
"longform-journalism|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/longform-journalism"
"translator|Vibe-Practice/EnvironmentScan-system-main-v4-main/.claude/skills/translator"
# ── 프로젝트 결합형: 투자분석 (translator는 위 env 정본과 이름충돌→제외) ──
"data-collector|Vibe-Practice/01.invest_scan/.claude/skills/data-collector"
"module-builder|Vibe-Practice/01.invest_scan/.claude/skills/module-builder"
"sot-inspector|Vibe-Practice/01.invest_scan/.claude/skills/sot-inspector"
"tdd-runner|Vibe-Practice/01.invest_scan/.claude/skills/tdd-runner"
# ── 프로젝트 결합형: 교회행정·뉴스크롤링 ──
"health-dashboard|Claude_skills/AI_churchteam/.claude/skills/health-dashboard"
"theological-reasoning|Claude_skills/AI_churchteam/.claude/skills/theological-reasoning"
"crawl-master|Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow/.claude/skills/crawl-master"
"insight-report|Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow/.claude/skills/insight-report"
# ── 하네스 템플릿 제작 4단계 ──
"harness-init|Vibe-Practice/harness-template/.claude/skills/harness-init"
"skill-build|Vibe-Practice/harness-template/.claude/skills/skill-build"
"skill-design|Vibe-Practice/harness-template/.claude/skills/skill-design"
"skill-plan|Vibe-Practice/harness-template/.claude/skills/skill-plan"
"skill-review|Vibe-Practice/harness-template/.claude/skills/skill-review"
)

ok=0; skip=0; nofm=0
echo "레지스트리: $REG"
echo "─────────────────────────────────────────────"
for entry in "${MANIFEST[@]}"; do
  name="${entry%%|*}"; rel="${entry##*|}"; tgt="$BASE/$rel"
  if [ ! -e "$tgt" ]; then echo "❌ SKIP  $name  (타겟없음: $rel)"; skip=$((skip+1)); continue; fi
  if [ ! -f "$tgt/SKILL.md" ]; then echo "⚠️  SKIP  $name  (SKILL.md 없음)"; skip=$((skip+1)); continue; fi
  fm=$(grep -m1 "^name:" "$tgt/SKILL.md" 2>/dev/null | sed 's/^name:[[:space:]]*//' | tr -d '"')
  if [ -z "$fm" ]; then echo "⚠️  $name  (frontmatter name 없음 — 등록하나 발견 불확실)"; nofm=$((nofm+1)); fi
  ln -sfn "$tgt" "$REG/$name"
  ok=$((ok+1))
  printf "✅ %-24s → %s\n" "$name" "$rel"
done
# ── 외부 스킬 레포 자동편입 (주인님 결정 2026-06-23: 전부 통합) ──
# external-skills/<repo> 하위의 모든 SKILL.md를 재귀 탐색해 디렉토리명으로 레지스트리 심링크.
# 중첩 카테고리(marketing skills/<cat>/<skill>) 대응. 디렉토리명 충돌 시 기존(정본1개) 우선 보존.
EXT_WHITELIST=(cys-claude-sermon-skills cys-claude-vision-coaching-skills marketing-skills skills gstack)
# deprecated 경로 필터: 이 패턴을 포함하는 경로는 레지스트리에서 제외 (원본 파일은 보존됨)
DEPRECATED_FILTER="/deprecated/"
for repo in "${EXT_WHITELIST[@]}"; do
  [ -d "$BASE/external-skills/$repo" ] || continue
  while IFS= read -r sk; do
    # deprecated 경로 필터링 (idempotent — 재실행 시에도 deprecated 스킬 자동 제외)
    case "$sk" in *"$DEPRECATED_FILTER"*) skip=$((skip+1)); continue;; esac
    skdir=$(dirname "$sk")
    # ★심링크명 = frontmatter name (Anthropic 스킬 스펙: 디렉토리명 == name 필수)
    nm=$(grep -m1 '^name:' "$sk" 2>/dev/null | sed 's/^name:[[:space:]]*//' | tr -d '"' | tr -d "\r" | xargs)
    [ -z "$nm" ] && nm=$(basename "$skdir")
    case "$nm" in *" "*|"") skip=$((skip+1)); continue;; esac   # 공백·빈 name 무효 차단
    if [ -e "$REG/$nm" ]; then skip=$((skip+1)); continue; fi    # 정본1개 보존
    ln -sfn "$skdir" "$REG/$nm"; ok=$((ok+1))
  done < <(find "$BASE/external-skills/$repo" -name SKILL.md -type f 2>/dev/null)
  echo "  ✅ $repo 편입 완료"
done
echo "─────────────────────────────────────────────"
echo "등록 $ok / 스킵 $skip / frontmatter결함 $nofm"
