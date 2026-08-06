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
"workflow-generator|_workflowhome/AgenticWorkflow-main/.claude/skills/workflow-generator"
"doctoral-writing|_workflowhome/AgenticWorkflow-main/.claude/skills/doctoral-writing"
"skill-creator|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/skill-creator"
"subagent-creator|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/subagent-creator"
"slash-command-creator|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/slash-command-creator"
"hook-creator|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/hook-creator"
# ── 교회 주간사역 (weekly-works) ──
"sermon|목회사역본부/weekly-works/.claude/skills/sermon"
"weekly-devotion|목회사역본부/weekly-works/.claude/skills/weekly-devotion"
"prayer-doc|목회사역본부/weekly-works/.claude/skills/prayer-doc"
"insert-images|목회사역본부/weekly-works/.claude/skills/insert-images"
"design-template-scout|목회사역본부/weekly-works/.claude/skills/design-template-scout"
"bulletin|목회사역본부/weekly-works/.claude/skills/bulletin"
"shorts|목회사역본부/weekly-works/.claude/skills/shorts"
"small-group|목회사역본부/weekly-works/.claude/skills/small-group"
"sns-cardnews|목회사역본부/weekly-works/.claude/skills/sns-cardnews"
"team-leader|목회사역본부/weekly-works/.claude/skills/team-leader"
"brand-guidelines|목회사역본부/weekly-works/.agents/skills/brand-guidelines"
"canvas-design|목회사역본부/weekly-works/.agents/skills/canvas-design"
# ── T&T 내러티브 설교 (제작 최종학 목사·원저 임도균 교수·2026-08-06 이론병합 완료) ──
"tnt-step00-context|목회사역본부/tnt-narrative-sermon/skills/tnt-step00-context"
"tnt-sermon-coach|목회사역본부/tnt-narrative-sermon/skills/tnt-sermon-coach"
"tnt-step01-select|목회사역본부/tnt-narrative-sermon/skills/tnt-step01-select"
"tnt-step02-read|목회사역본부/tnt-narrative-sermon/skills/tnt-step02-read"
"tnt-step03-retell|목회사역본부/tnt-narrative-sermon/skills/tnt-step03-retell"
"tnt-step04-compress|목회사역본부/tnt-narrative-sermon/skills/tnt-step04-compress"
"tnt-step05-connect|목회사역본부/tnt-narrative-sermon/skills/tnt-step05-connect"
"tnt-step06-path|목회사역본부/tnt-narrative-sermon/skills/tnt-step06-path"
"tnt-step07-draft|목회사역본부/tnt-narrative-sermon/skills/tnt-step07-draft"
"tnt-step08-polish|목회사역본부/tnt-narrative-sermon/skills/tnt-step08-polish"
"tnt-step09-resolve|목회사역본부/tnt-narrative-sermon/skills/tnt-step09-resolve"
"tnt-step10-deliver|목회사역본부/tnt-narrative-sermon/skills/tnt-step10-deliver"
"tnt-greek-grammar|목회사역본부/tnt-narrative-sermon/skills/tnt-greek-grammar"
"tnt-bible-dictionary|목회사역본부/tnt-narrative-sermon/skills/tnt-bible-dictionary"
"tnt-textual-criticism|목회사역본부/tnt-narrative-sermon/skills/tnt-textual-criticism"
"tnt-emotive-coach|목회사역본부/tnt-narrative-sermon/skills/tnt-emotive-coach"
"tnt-audience-persona|목회사역본부/tnt-narrative-sermon/skills/tnt-audience-persona"
# ── 연구·콘텐츠·강의 ──
"research|목회사역본부/.claude/skills/research"
"nlm-skill|.agents/skills/nlm-skill"
"writing-workflow|크리에이티브본부/Writingskills/writing-workflow"
"course-design|개발본부/플랫폼·릴리즈팀/opencode/course-design"
"gpt-codex-intro|개발본부/플랫폼·릴리즈팀/opencode/gpt-codex-intro"
"lecture-design|Edu본부/lecture_skill_build/skill"
"youth-life-planner|Edu본부/youth_life_plan"
"brunch-writing-workflow|크리에이티브본부/Writingskills/brunch-writing-workflow"
"aitoon-page-director|크리에이티브본부/aitoon-page-director"
# ── 교회 행정 ──
"church-admin|목회사역본부/church-admin/church-admin/.claude/skills/church-admin"
# ── Wave-AI (오케스트레이터 정본) ──
"wave-orchestrator|크리에이티브본부/Wave-AI"
# ── 프로젝트 결합형: wave-homepage (RSI ⑤ 도구화, 2026-07-13) ──
"deterministic-motion-capture|wave-homepage/.claude/skills/deterministic-motion-capture"
# ── 프로젝트 결합형: 환경스캐닝 ──
"env-scanner|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/env-scanner"
"youtube-collector|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/youtube-collector"
"longform-journalism|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/longform-journalism"
"translator|_workflowhome/EnvironmentScan-system-main-v4-main/.claude/skills/translator"
# ── 프로젝트 결합형: 투자분석 (translator는 위 env 정본과 이름충돌→제외) ──
"data-collector|리서치본부/invest_scan/.claude/skills/data-collector"
"module-builder|리서치본부/invest_scan/.claude/skills/module-builder"
"sot-inspector|리서치본부/invest_scan/.claude/skills/sot-inspector"
"tdd-runner|리서치본부/invest_scan/.claude/skills/tdd-runner"
# ── 프로젝트 결합형: 교회행정·뉴스크롤링 ──
"ai-churchteam|목회사역본부/AI_churchteam/.claude/skills/ai-churchteam"
"health-dashboard|목회사역본부/AI_churchteam/.claude/skills/health-dashboard"
"theological-reasoning|목회사역본부/AI_churchteam/.claude/skills/theological-reasoning"
"crawl-master|_workflowhome/GlobalNews-Crawling-AgenticWorkflow/.claude/skills/crawl-master"
"insight-report|_workflowhome/GlobalNews-Crawling-AgenticWorkflow/.claude/skills/insight-report"
# ── 하네스 템플릿 제작 4단계 ──
"harness-init|_workflowhome/harness-template/.claude/skills/harness-init"
"skill-build|_workflowhome/harness-template/.claude/skills/skill-build"
"skill-design|_workflowhome/harness-template/.claude/skills/skill-design"
"skill-plan|_workflowhome/harness-template/.claude/skills/skill-plan"
"skill-review|_workflowhome/harness-template/.claude/skills/skill-review"
# ── _skills/standalone 정식 등록 (2026-07-24·.skill zip 압축해제) ──
"blog-thumbnail-prompt|_skills/standalone/blog-thumbnail-prompt"
"pastor-life-planner|_skills/standalone/pastor-life-planner"
"prompt-polish-lite|_skills/standalone/prompt-polish-lite"
"suno-music-workflow|_skills/standalone/suno-music-workflow"
"write-content|_skills/standalone/write-content"
"write-question|_skills/standalone/write-question"
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
# ── 코드·앱빌드·미디어 스킬 편입 (2026-07-17 CSO — 스킬베이스 감사 근인A 복구·COO/CEO 요청) ──
# 레지스트리 발견성 밖이던 코드리뷰/이미지생성/신규웹앱 스킬군을 프로젝트 레지스트리에 편입.
# 소스: 전역 ~/.claude/skills · 엔진 팩 ~/.cys/pack/skills · Codex .agents. 정본1개 보존(기존 우선).
# ⚠ 엔진 팩 경로(appbuild/media-gen)는 pack-update 시 이동 가능 — idempotent 재실행으로 복구.
ABS_MANIFEST=(
  "code-review|$BASE/개발본부/AI제품개발팀/Codex/.agents/skills/code-review"
  "codebase-review|/Users/kylechoi/.claude/skills/codebase-review"
  "security-review|/Users/kylechoi/.claude/skills/security-review"
  "tdd-workflow|/Users/kylechoi/.claude/skills/tdd-workflow"
  "deployment-patterns|/Users/kylechoi/.claude/skills/deployment-patterns"
  # ── 리서치 도메인 (2026-07-17 CEO — 감사 근인A 재발분) ──
  "insane-search|/Users/kylechoi/.cys/pack/skills/insane-search"
  "agent-reach|/Users/kylechoi/.claude/skills/agent-reach"
  "search-first|/Users/kylechoi/.claude/skills/search-first"
  "exa-search|/Users/kylechoi/.claude/skills/exa-search"
  "deep-research|/Users/kylechoi/.claude/skills/deep-research"
  "iterative-retrieval|/Users/kylechoi/.claude/skills/iterative-retrieval"
)
for entry in "${ABS_MANIFEST[@]}"; do
  name="${entry%%|*}"; tgt="${entry##*|}"
  [ -f "$tgt/SKILL.md" ] || { echo "❌ SKIP  $name  (SKILL.md 없음: $tgt)"; skip=$((skip+1)); continue; }
  if [ -e "$REG/$name" ]; then skip=$((skip+1)); continue; fi   # 정본1개 보존
  ln -sfn "$tgt" "$REG/$name"; ok=$((ok+1)); printf "✅ %-24s → %s\n" "$name" "$tgt"
done
# appbuild·media-gen 패밀리 전체 (엔진 팩 정본 — 신규웹앱·이미지생성 오케스트레이션)
PACK_SKILLS="/Users/kylechoi/.cys/pack/skills"
for d in "$PACK_SKILLS"/appbuild "$PACK_SKILLS"/appbuild-* "$PACK_SKILLS"/media-gen "$PACK_SKILLS"/media-gen-*; do
  { [ -d "$d" ] && [ -f "$d/SKILL.md" ]; } || continue
  name="$(basename "$d")"
  if [ -e "$REG/$name" ]; then skip=$((skip+1)); continue; fi
  ln -sfn "$d" "$REG/$name"; ok=$((ok+1)); printf "✅ %-24s → %s\n" "$name" "$d"
done

# ── 외부 스킬 레포 자동편입 (주인님 결정 2026-06-23: 전부 통합) ──
# _skills/external/<repo> 하위의 모든 SKILL.md를 재귀 탐색해 디렉토리명으로 레지스트리 심링크.
# 중첩 카테고리(marketing skills/<cat>/<skill>) 대응. 디렉토리명 충돌 시 기존(정본1개) 우선 보존.
EXT_WHITELIST=(cys-claude-sermon-skills cys-claude-vision-coaching-skills marketing-skills skills gstack)
# deprecated 경로 필터: 이 패턴을 포함하는 경로는 레지스트리에서 제외 (원본 파일은 보존됨)
DEPRECATED_FILTER="/deprecated/"
for repo in "${EXT_WHITELIST[@]}"; do
  [ -d "$BASE/_skills/external/$repo" ] || continue
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
  done < <(find "$BASE/_skills/external/$repo" -name SKILL.md -type f 2>/dev/null)
  echo "  ✅ $repo 편입 완료"
done
echo "─────────────────────────────────────────────"
echo "등록 $ok / 스킵 $skip / frontmatter결함 $nofm"
