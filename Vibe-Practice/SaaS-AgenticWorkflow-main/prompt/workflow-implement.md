# SaaS PRD Workflow — Claude Code Implementation Final Design

> **이 문서의 목적**: (1) 구현 체크리스트 (2) 컨텍스트 상실 시 복구 기준점
> **워크플로우 원본**: `prompt/saas-autobuilder-prd-workflow.md`
> **설계 완료일**: 2026-03-13
> **상태**: 4차 성찰 완료, 사용자 구현 승인 대기

---

## 0. 절대 기준 (Non-Negotiable)

1. **절대 기준 1 — 품질**: 속도, 토큰 비용, 작업량 무시. 품질만 기준.
2. **절대 기준 2 — SOT**: `.claude/state.yaml` 단일 파일. Orchestrator/Team Lead만 쓰기. 병렬 에이전트 동시 수정 금지.
3. **절대 기준 3 — CCP**: 코드 변경 전 의도→영향→설계 3단계. CAP-1~4.
4. **절대 기준 4 — English-First**: 모든 에이전트 사고·산출물 영어. @translator만 한국어 생성. 모든 output-producing step에서 영어 원본 + 한국어 번역 쌍 생성.

---

## 1. 아키텍처 개요

```
Main Session (Orchestrator)
├── Step 1:  @prd-analyst (sub-agent)
├── Step 2:  prd-analysis-team (Agent Team — 3 members)
├── Step 3:  @research-synthesizer (sub-agent)
├── Step 4:  (human) /review-research
├── Step 5:  @prd-architect (sub-agent)
├── Step 6:  @intent-designer (sub-agent)
├── Step 7:  @engine-planner (sub-agent)
├── Step 8:  (human) /review-planning
├── Step 9:  prd-generation-team (Agent Team — 4 members)
├── Step 10: @cross-validator (sub-agent)
├── Step 11: @reviewer + @fact-checker (sub-agents, sequential)
└── Step 12: (human) /review-final-prd
```

- **Orchestrator**: Main Claude Code session. SOT 쓰기는 sot_manager.py 통해서만.
- **Agent Teams**: Steps 2, 9. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 필요. 미설정 시 sequential sub-agent fallback.
- **Sub-agents**: 나머지 steps. Agent tool로 spawn, 결과 보고.
- **Translation**: 모든 output step 완료 후 @translator sub-agent 순차 호출 (glossary 일관성).

### 핵심 설계 원칙

- **LLM as Coordinator, Python as Enforcer**: 창의적/분석적 작업은 LLM, 결정론적 작업(SOT 쓰기, step routing, gate sequencing)은 Python
- **Hook = Read-Only for SOT**: 모든 Hook script는 SOT를 읽기만 함. 쓰기는 Orchestrator → sot_manager.py 경로만.
- **Manifest File Pattern**: Team steps(2, 9)의 복수 sub-output은 manifest.md 1개로 SOT 등록. SOT list/sub-key 비호환 우회.
- **Sequential Translation**: glossary.yaml 일관성 보장을 위해 15개 번역 job을 순차 실행.

---

## 2. SOT 스키마 (state.yaml)

```yaml
workflow:
  name: "SaaS Auto-Builder PRD Generation"
  current_step: 1          # int >= 0
  status: "running"        # S5: running | completed | error | paused
  total_steps: 12

  autopilot:
    enabled: false
    activated_at: ""
    auto_approved_steps: []

  outputs:                 # S3: step-N 또는 step-N-ko 형식만 허용
    # step-1: "prompt/research/prd-foundation-analysis.md"
    # step-1-ko: "prompt/research/prd-foundation-analysis.ko.md"
    # step-2: "prompt/research/step-2-manifest.md"     ← manifest 패턴
    # step-2-ko: "prompt/research/step-2-manifest.ko.md"
    # step-3: "prompt/research/synthesis-and-gaps.md"
    # step-3-ko: "prompt/research/synthesis-and-gaps.ko.md"
    # step-5: "prompt/planning/prd-architecture.md"
    # step-5-ko: "prompt/planning/prd-architecture.ko.md"
    # step-6: "prompt/planning/intent-capture-spec.md"
    # step-6-ko: "prompt/planning/intent-capture-spec.ko.md"
    # step-7: "prompt/planning/engine-quality-specs.md"
    # step-7-ko: "prompt/planning/engine-quality-specs.ko.md"
    # step-9: "prompt/implementation/step-9-manifest.md"  ← manifest 패턴
    # step-9-ko: "prompt/implementation/step-9-manifest.ko.md"
    # step-10: "prompt/implementation/prd-validated.md"
    # step-10-ko: (없음 — Step 12에서 최종본 번역)
    # step-11: "prompt/review/prd-adversarial-review.md"
    # step-11-ko: "prompt/review/prd-adversarial-review.ko.md"
    # step-12: "prompt/PRD-SaaS-AutoBuilder.md"
    # step-12-ko: "prompt/PRD-SaaS-AutoBuilder.ko.md"

  pacs:
    dimensions: {F: 0, C: 0, L: 0}
    current_step_score: 0
    weak_dimension: ""
    history: {}
    pre_mortem_flag: ""

  # active_team:           # Step 2, 9 실행 중에만 존재
  #   name: "prd-analysis-team"
  #   status: "partial"    # partial | all_completed
  #   tasks_completed: []
  #   tasks_pending: []
  #   completed_summaries: {}
  # completed_teams: []

  parent_genome:
    source: "AgenticWorkflow"
    version: "2026-03-13"
```

### SOT 핵심 규칙

| 규칙 | 상세 |
|------|------|
| S3 키 형식 | `step-N` 또는 `step-N-ko` (N은 숫자) |
| S4 미래 단계 금지 | output key의 step number ≤ current_step |
| S5 status 값 | `running`, `completed`, `error`, `paused` 만 허용 |
| S8 active_team | `partial` 또는 `all_completed` |
| Manifest 패턴 | Team steps (2, 9)는 manifest.md 파일 1개 → SOT에는 `step-N: manifest_path` |
| 쓰기 경로 | Orchestrator → `sot_manager.py` → `atomic_write()` → state.yaml |
| 쓰기 금지 경로 | 1) Claude Write tool 직접 → `validate_sot_write.py`가 exit 2로 차단 2) Bash redirect → `block_destructive_commands.py`가 차단 3) Hook script → 아키텍처 불변식 (Hook = SOT read-only) |

---

## 3. DAG (Step Dependency Graph)

```python
# task_dag_init.py에 하드코딩. workflow.md 런타임 파싱 안 함.
DAG = {
    1:  {"name": "PRD Foundation Extraction",            "deps": [],     "type": "sub-agent",   "team": None,                  "human": False, "pre_script": "extract_prd_sections.py", "review": None,           "translate": True},
    2:  {"name": "Multi-Perspective Deep Analysis",      "deps": [1],    "type": "agent-team",  "team": "prd-analysis-team",    "human": False, "pre_script": None,                      "review": None,           "translate": True},
    3:  {"name": "Research Synthesis & Gap Analysis",    "deps": [1,2],  "type": "sub-agent",   "team": None,                  "human": False, "pre_script": None,                      "review": "fact-checker", "translate": True},
    4:  {"name": "Research Findings Review",             "deps": [3],    "type": "human",       "team": None,                  "human": True,  "pre_script": None,                      "review": None,           "translate": False},
    5:  {"name": "PRD Document Architecture Design",    "deps": [4],    "type": "sub-agent",   "team": None,                  "human": False, "pre_script": None,                      "review": None,           "translate": True},
    6:  {"name": "Intent Capture & Question Flow Spec", "deps": [4],    "type": "sub-agent",   "team": None,                  "human": False, "pre_script": None,                      "review": "reviewer",     "translate": True},
    7:  {"name": "Engine Pipeline & Quality Framework",  "deps": [5,6],  "type": "sub-agent",   "team": None,                  "human": False, "pre_script": None,                      "review": "reviewer",     "translate": True},
    8:  {"name": "Planning Review & Approval",           "deps": [7],    "type": "human",       "team": None,                  "human": True,  "pre_script": None,                      "review": None,           "translate": False},
    9:  {"name": "PRD Document Generation",              "deps": [8],    "type": "agent-team",  "team": "prd-generation-team", "human": False, "pre_script": None,                      "review": None,           "translate": True},
    10: {"name": "Cross-Validation & Integration",       "deps": [9],    "type": "sub-agent",   "team": None,                  "human": False, "pre_script": "merge_prd_sections.py",   "review": None,           "translate": False},
    11: {"name": "Adversarial Review",                   "deps": [10],   "type": "sub-agent",   "team": None,                  "human": False, "pre_script": None,                      "review": None,           "translate": True},
    12: {"name": "Final PRD Review & Approval",          "deps": [11],   "type": "human",       "team": None,                  "human": True,  "pre_script": None,                      "review": None,           "translate": True},
}
# 15 translation jobs: steps 1,2,3,5,6,7,9,11,12 (EN+KO pairs)
# Steps 4,8: human checkpoint — no output
# Step 10: intermediate — translated at step 12 as final version
```

### Team Members

```python
TEAMS = {
    "prd-analysis-team": {
        "members": [
            {"agent": "arch-engine-specialist", "task": "Architecture & Engine Pipeline Analysis", "output": "prompt/research/arch-engine-analysis.md"},
            {"agent": "feature-ux-specialist",  "task": "Feature & Intent Capture Analysis",      "output": "prompt/research/feature-ux-analysis.md"},
            {"agent": "biz-quality-specialist",  "task": "Business Model & Quality Framework Analysis", "output": "prompt/research/biz-quality-analysis.md"},
        ],
    },
    "prd-generation-team": {
        "members": [
            {"agent": "prd-writer-core",        "task": "Sections 1-5: Foundation & Users",      "output": "prompt/implementation/prd-sections-1-5.md"},
            {"agent": "prd-writer-tech",        "task": "Sections 6-8: Technical Core",          "output": "prompt/implementation/prd-sections-6-8.md"},
            {"agent": "prd-writer-integration", "task": "Sections 9-12: Systems & Quality",      "output": "prompt/implementation/prd-sections-9-12.md"},
            {"agent": "prd-writer-business",    "task": "Sections 13-16: Business & Appendix",   "output": "prompt/implementation/prd-sections-13-16.md"},
        ],
    },
}
```

---

## 4. Quality Gate Flow (Per Step)

```
Step Output 생성
    ↓
[L0] validate_step_output() — 파일 존재 + ≥100 bytes + 비-공백
    ↓
[L1] Verification Gate — step의 Verification 체크리스트 against output
    ↓ (verification-logs/step-N-verify.md)
[L1.5] pACS Self-Rating — Pre-mortem → F/C/L 채점 → min() = pACS
    ↓ (pacs-logs/step-N-pacs.md)
    ↓ RED(<50) → 재작업 | YELLOW(50-69) → 진행+경고 | GREEN(≥70) → 진행
[L2] Adversarial Review (해당 step만) — @reviewer/@fact-checker
    ↓ (review-logs/step-N-review.md)
    ↓ PASS → 진행 | FAIL → Abductive Diagnosis → 재작업
[Translation] @translator → .ko.md + glossary update
    ↓ (pacs-logs/step-N-translation-pacs.md)
[SOT Update] sot_manager.py — outputs.step-N, outputs.step-N-ko, current_step++
```

**Quality Gate Runner (quality_gate_runner.py)**: 위 시퀀스를 Python subprocess로 결정론적 실행.
```
python3 quality_gate_runner.py --step N --project-dir . [--skip-review] [--skip-translation]
```
- L0: `validate_step_output()` from `_context_lib.py`
- L1: LLM (Orchestrator) 수행, 로그 write
- L1.5: LLM (Orchestrator) 수행, 로그 write → `validate_pacs.py --step N` 검증
- L2: `validate_review.py --step N` 검증
- Translation: `validate_translation.py --step N --check-pacs --check-sequence` 검증

### L2 Review 대상 Steps

| Step | Review Agent | 근거 |
|------|-------------|------|
| 3 | @fact-checker | gap claims가 실제 PRD 내용에 근거하는지 검증 |
| 6 | @reviewer | FSM 완전성, guard condition, rollback semantics 검증 |
| 7 | @reviewer | 기술적 타당성, 사양 완전성, acceptance criteria 검증 |
| 11 | @reviewer + @fact-checker | 최종 PRD 전체 적대적 리뷰 |

---

## 5. 파일 생성/수정 전체 목록

### Phase 1: P1 Hallucination Prevention Scripts (6 new + 6 tests)

| # | 파일 | 역할 | 위치 |
|---|------|------|------|
| 1 | `sot_manager.py` | SOT 유일 쓰기 경로. atomic_write + validate_sot_schema 내장. CLI: `--init`, `--update-step N --output path`, `--set-status STATUS`, `--add-team-result TASK OUTPUT_PATH`, `--finalize-team`, `--add-translation STEP KO_PATH` | `.claude/hooks/scripts/` |
| 2 | `workflow_router.py` | Step N → 다음 실행 가능 step 결정 (DAG deps 충족 + output 존재 확인). `--current-step N --project-dir .` → JSON stdout `{"next_steps": [5,6], "reason": "..."}` | `.claude/hooks/scripts/` |
| 3 | `quality_gate_runner.py` | L0→L1.5 게이트 시퀀스 결정론적 실행. 각 validator를 subprocess로 호출. `--step N --project-dir . [--skip-review] [--skip-translation]` → JSON stdout `{"all_passed": true, "gates": {...}}` | `.claude/hooks/scripts/` |
| 4 | `task_dag_init.py` | DAG 하드코딩 + DAG 정보 JSON 출력. Orchestrator가 TaskCreate 호출. `--project-dir .` → JSON stdout `{"steps": [...]}` | `.claude/hooks/scripts/` |
| 5 | `manifest_generator.py` | Team step 완료 후 manifest.md 생성. `--step N --project-dir . --files "path1,path2,..."` → manifest file write + JSON stdout | `.claude/hooks/scripts/` |
| 6 | `bilingual_validator.py` | EN+KO 쌍 존재 확인. `--step N --project-dir .` → JSON stdout `{"valid": true, "en_path": "...", "ko_path": "..."}` | `.claude/hooks/scripts/` |
| 7-12 | `_test_sot_manager.py`, `_test_workflow_router.py`, `_test_quality_gate_runner.py`, `_test_task_dag_init.py`, `_test_manifest_generator.py`, `_test_bilingual_validator.py` | TDD 테스트 | `.claude/hooks/scripts/` |

**공통 패턴**: 모든 P1 스크립트는 `_context_lib.py`에서 import (`SOT_FILENAMES`, `sot_paths`, `validate_sot_schema`, `atomic_write` 등). 순방향 import만 — 순환 의존성 없음.

### Phase 2: 기존 파일 수정 (6 files)

| # | 파일 | 변경 내용 |
|---|------|----------|
| 13 | `_context_lib.py` (line ~4063) | `validate_translation_output(project_dir, step_number, source_path=None)` — source_path 파라미터 추가. source_path 제공 시 SOT 조회 대신 직접 사용. T3 체크에서 분기. |
| 14 | `_context_lib.py` (line ~600) | Regex fallback에서 `step-\d+` → `step-\d+(?:-ko)?` 패턴 수정 (outer + inner). GAP-H1 대응. |
| 15 | `setup_init.py` (REQUIRED_SCRIPTS, line 43-66) | 8개 스크립트 추가: `sot_manager.py`, `workflow_router.py`, `quality_gate_runner.py`, `task_dag_init.py`, `manifest_generator.py`, `bilingual_validator.py`, `validate_task_completion.py`, `validate_sot_write.py` |
| 16 | `setup_maintenance.py` (REQUIRED_SCRIPTS, line 46-69) | 동일 8개 스크립트 추가 (D-7 dual update) |
| 17 | `CLAUDE.md` (Hook event table) | 2개 Hook 항목 추가 (DC-6 sync): `PreToolUse(Write)` → `validate_sot_write.py`, `PostToolUse(TaskUpdate)` → `validate_task_completion.py` |
| 18 | `block_destructive_commands.py` | SOT 직접 쓰기 Bash 패턴 추가: `> .claude/state.yaml` 등 (GAP-C3) |

### Phase 3: Workflow Scripts (3 new + 3 tests)

| # | 파일 | 역할 |
|---|------|------|
| 19 | `scripts/extract_prd_sections.py` | Step 1 pre-processing. `coding-resource/PRD.md` → 16 section files + code-examples + diagrams + tables. `--input coding-resource/PRD.md --output-dir prompt/research/sections/` |
| 20 | `scripts/merge_prd_sections.py` | Step 10 pre-processing. 4 section documents → merged draft. `--input-dir prompt/implementation/ --output prompt/implementation/prd-merged-draft.md` |
| 21 | `scripts/validate_prd_structure.py` | Step 10 post-processing. 16 `## N.` headings, TypeScript syntax, Mermaid tokens, no TODO/TBD, ≥2500 lines. `--input prompt/implementation/prd-validated.md` |
| 22-24 | `scripts/_test_extract.py`, `scripts/_test_merge.py`, `scripts/_test_validate_prd.py` | TDD 테스트 |

### Phase 4: Hook Scripts (2 new + 2 tests)

| # | 파일 | Hook 이벤트 | 역할 |
|---|------|------------|------|
| 25 | `validate_task_completion.py` | PostToolUse(TaskUpdate) | TaskUpdate 호출 시 stdin JSON에서 task status 확인. status="completed"면 output 파일 존재+크기 검증. exit 0 (경고만, 차단 안 함). |
| 26 | `validate_sot_write.py` | PreToolUse(Write) | Write tool의 file_path가 `.claude/state.yaml\|yml\|json`이면 exit 2 차단 + "sot_manager.py를 사용하세요" 메시지. |
| 27-28 | `_test_validate_task_completion.py`, `_test_validate_sot_write.py` | TDD 테스트 |

### Phase 5: Agent Definitions (13 files) + Commands (5 files)

| # | 파일 | 모델 | maxTurns |
|---|------|------|----------|
| 29 | `.claude/agents/prd-analyst.md` | opus | 50 |
| 30 | `.claude/agents/arch-engine-specialist.md` | opus | 40 |
| 31 | `.claude/agents/feature-ux-specialist.md` | opus | 40 |
| 32 | `.claude/agents/biz-quality-specialist.md` | opus | 40 |
| 33 | `.claude/agents/research-synthesizer.md` | opus | 40 |
| 34 | `.claude/agents/prd-architect.md` | opus | 40 |
| 35 | `.claude/agents/intent-designer.md` | opus | 50 |
| 36 | `.claude/agents/engine-planner.md` | opus | 50 |
| 37 | `.claude/agents/prd-writer-core.md` | opus | 60 |
| 38 | `.claude/agents/prd-writer-tech.md` | opus | 80 |
| 39 | `.claude/agents/prd-writer-integration.md` | opus | 60 |
| 40 | `.claude/agents/prd-writer-business.md` | opus | 60 |
| 41 | `.claude/agents/cross-validator.md` | sonnet | 40 |

기존 에이전트 수정 없음: `translator.md`, `reviewer.md`, `fact-checker.md` 그대로 사용.

| # | 파일 | 역할 |
|---|------|------|
| 42 | `.claude/commands/run-workflow.md` | 전체 워크플로우 실행 orchestrator command |
| 43 | `.claude/commands/review-research.md` | Step 4 human checkpoint |
| 44 | `.claude/commands/review-planning.md` | Step 8 human checkpoint |
| 45 | `.claude/commands/review-final-prd.md` | Step 12 human checkpoint |
| 46 | `.claude/commands/workflow-status.md` | `query_workflow.py --dashboard` wrapper |

### Phase 6: settings.json + state.yaml + Integration Test

| # | 파일 | 변경 |
|---|------|------|
| 47 | `.claude/settings.json` | 2개 Hook 항목 추가: PreToolUse(Write) → validate_sot_write.py, PostToolUse(TaskUpdate) → validate_task_completion.py |
| 48 | `.claude/state.yaml` | 초기 SOT 파일 생성 (sot_manager.py --init) |

### Phase 7: Full 12-Step Workflow Execution

사용자 승인 후 `/run-workflow` 실행.

**총 파일 수**: 신규 43개 + 기존 수정 6개 = 49개 변경

---

## 6. CRITICAL Gaps & Resolutions (1-4차 성찰)

### From Reflection 1-3:

| ID | Gap | Resolution | Status |
|----|-----|-----------|--------|
| CRITICAL-1 | SOT nested schema `{en:..., ko:...}` breaks `_read_sot_outputs()` regex | Flat `step-N` / `step-N-ko` 패턴 사용 (S3 호환) | **RESOLVED** |
| CRITICAL-2 | Team sub-output keys `step-2a` rejected by S3 validator | Manifest file 패턴: `step-2: manifest.md` | **RESOLVED** |
| CRITICAL-3 | REQUIRED_SCRIPTS D-7 sync | setup_init.py + setup_maintenance.py 양쪽 동시 추가 | **RESOLVED** |
| CRITICAL-4 | DC-6 doc-code sync | settings.json 변경 시 CLAUDE.md hook table 동시 갱신 | **RESOLVED** |
| CRITICAL-5 | validate_translation.py team sub-output 미지원 | `validate_translation_output()` `source_path=None` 파라미터 추가 | **RESOLVED** |
| CRITICAL-6 | enforce_bilingual_output.py false positive | Hook 삭제. Orchestrator step-completion 로직으로 이동 | **RESOLVED** |
| CRITICAL-7 | validate_english_output.py fragile heuristic | Hook 삭제. Agent 지시문으로 English-first 강제 | **RESOLVED** |
| CRITICAL-8 | SOT status mismatch ("in_progress" vs "running") | S5 허용값 사용: running/completed/error/paused | **RESOLVED** |
| CRITICAL-9 | Team step SOT에 output list 불가 | Manifest file 패턴 (CRITICAL-2와 동일 해결) | **RESOLVED** |

### From Reflection 4:

| ID | Gap | Resolution | Status |
|----|-----|-----------|--------|
| GAP-C1 | TeammateIdle/TaskCompleted hook 이벤트 미존재 | 2개 hook 삭제. Orchestrator TaskList polling으로 대체 | **RESOLVED** |
| GAP-C2 | task_completed_gate.py SOT 쓰기 = Hook read-only 위반 | GAP-C1에 의해 hook 자체 삭제 | **RESOLVED** |
| GAP-C3 | validate_sot_write.py가 Bash redirect 미감지 | `block_destructive_commands.py`에 SOT 직접 쓰기 패턴 추가 | **RESOLVED** |
| GAP-H1 | `read_autopilot_state()` regex가 `step-N-ko` 키 미파싱 | regex `step-\d+` → `step-\d+(?:-ko)?` 수정 | **RESOLVED** |
| GAP-H2 | workflow.md 런타임 파싱 취약 | Hardcoded DAG + W9 divergence check | **RESOLVED** |
| GAP-H3 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 미관리 | setup_init.py 검증 + sequential fallback | **RESOLVED** |
| GAP-M1 | Team 실행 중 session compaction | SOT active_team.name 보존 + run-workflow.md 복구 지시 | **RESOLVED** |
| GAP-M2 | S4 validator + sot_manager.py 원자성 | atomic_write()로 output+current_step 동시 갱신 | **RESOLVED** |
| GAP-M3 | query_workflow.py dashboard 번역 상태 미표시 | `_dashboard()`에 translation_status 섹션 추가 | **DEFERRED** (Phase 2) |

---

## 7. 구현 순서 체크리스트

### Phase 1: P1 Hallucination Prevention Scripts

- [ ] 1-1. `sot_manager.py` 구현
  - `from _context_lib import SOT_FILENAMES, sot_paths, validate_sot_schema, atomic_write`
  - CLI: `--init`, `--update-step N --output PATH`, `--set-status STATUS`, `--add-team-result TASK_ID OUTPUT_PATH`, `--finalize-team`, `--add-translation STEP KO_PATH`
  - 내부: PyYAML `yaml.safe_load()` → dict 수정 → `validate_sot_schema()` → `atomic_write()`
  - `--update-step`는 반드시 output + current_step을 같은 write에서 갱신 (S4 원자성)
  - Exit codes: 0=success, 1=validation failure, 2=file error
  - JSON stdout: `{"success": true, "warnings": []}`

- [ ] 1-2. `_test_sot_manager.py` TDD 작성 + 통과

- [ ] 1-3. `workflow_router.py` 구현
  - DAG dict 하드코딩 (Section 3 참조)
  - `--current-step N` → 모든 successor의 deps 확인 → `_read_sot_outputs()`로 output 존재 검증
  - Parallel successor 반환 (e.g., Step 4 완료 → [5, 6] 반환)
  - Human step 감지: `"type": "human"` → `{"next_steps": [4], "human_checkpoint": true}`

- [ ] 1-4. `_test_workflow_router.py` TDD 작성 + 통과

- [ ] 1-5. `quality_gate_runner.py` 구현
  - `--step N --project-dir . [--skip-review] [--skip-translation]`
  - Subprocess calls: `validate_pacs.py --step N --check-l0`, `validate_review.py --step N`, `validate_translation.py --step N --check-pacs --check-sequence`
  - Timeout: 30s per subprocess (Bash tool 120s 내)
  - Gate sequence: L0 → L1(skip — LLM does this) → L1.5 → L2 → Translation
  - JSON output: `{"all_passed": true, "gates": {"L0": {...}, "L1.5": {...}, ...}}`

- [ ] 1-6. `_test_quality_gate_runner.py` TDD 작성 + 통과

- [ ] 1-7. `task_dag_init.py` 구현
  - DAG dict (workflow_router.py와 동일 — import 공유)
  - DAG 정보를 JSON으로 출력, orchestrator가 TaskCreate 호출
  - JSON output: `{"steps": [{step_number, name, deps, type}, ...]}`

- [ ] 1-8. `_test_task_dag_init.py` TDD 작성 + 통과

- [ ] 1-9. `manifest_generator.py` 구현
  - `--step N --project-dir . --files "path1,path2,path3"`
  - Manifest format:
    ```markdown
    # Step N Manifest — {step_name}
    ## Sub-outputs
    - path1 (size: X bytes, created: timestamp)
    - path2 (size: Y bytes, created: timestamp)
    ## Summary
    Total: N files, M total bytes
    ```
  - 각 파일 존재 + 크기 검증
  - `atomic_write()`로 manifest 파일 생성
  - JSON output: `{"manifest_path": "...", "valid": true, "files_verified": N}`

- [ ] 1-10. `_test_manifest_generator.py` TDD 작성 + 통과

- [ ] 1-11. `bilingual_validator.py` 구현
  - `--step N --project-dir .`
  - SOT에서 `step-N` (EN) + `step-N-ko` (KO) 경로 읽기
  - 양쪽 파일 존재 + 크기 ≥ 100 bytes 확인
  - JSON output: `{"valid": true, "en_path": "...", "ko_path": "...", "en_size": X, "ko_size": Y}`

- [ ] 1-12. `_test_bilingual_validator.py` TDD 작성 + 통과

### Phase 2: Existing File Modifications

- [ ] 2-1. `_context_lib.py` — `validate_translation_output()` 시그니처 수정
  - Line ~4063: `def validate_translation_output(project_dir, step_number, source_path=None):`
  - `source_path` 제공 시 T3 체크에서 SOT 대신 source_path 직접 사용
  - 3-tier fallback은 `source_path=None`일 때만 동작 (기존 호환)

- [ ] 2-2. `_context_lib.py` — Regex fallback 패턴 수정
  - Line ~601 (outer): `r'outputs\s*:\s*\n((?:\s+step-\d+(?:-ko)?\s*:.+\n?)*)'`
  - Line ~605 (inner): `r'(step-\d+(?:-ko)?)\s*:\s*["\']?(.+?)["\']?\s*$'`

- [ ] 2-3. `setup_init.py` — REQUIRED_SCRIPTS 8개 추가
  - 기존 20개 → 28개
  - 추가: sot_manager.py, workflow_router.py, quality_gate_runner.py, task_dag_init.py, manifest_generator.py, bilingual_validator.py, validate_task_completion.py, validate_sot_write.py

- [ ] 2-4. `setup_maintenance.py` — REQUIRED_SCRIPTS 8개 추가 (D-7)

- [ ] 2-5. `CLAUDE.md` — Hook event table에 2개 항목 추가 (DC-6)
  - `| PreToolUse (Write) | validate_sot_write.py | SOT 직접 Write 차단 (exit 2) |`
  - `| PostToolUse (TaskUpdate) | validate_task_completion.py | Task 완료 시 output 검증 |`

- [ ] 2-6. `block_destructive_commands.py` — SOT 직접 쓰기 패턴 추가 (GAP-C3)
  - `> .claude/state.yaml`, `> .claude/state.yml`, `> .claude/state.json`
  - `tee .claude/state.*`, `$CLAUDE_PROJECT_DIR/.claude/state.*`

### Phase 3: Workflow Scripts

- [ ] 3-1. `scripts/extract_prd_sections.py` 구현
- [ ] 3-2. `scripts/_test_extract.py` TDD 작성 + 통과
- [ ] 3-3. `scripts/merge_prd_sections.py` 구현
- [ ] 3-4. `scripts/_test_merge.py` TDD 작성 + 통과
- [ ] 3-5. `scripts/validate_prd_structure.py` 구현
- [ ] 3-6. `scripts/_test_validate_prd.py` TDD 작성 + 통과

### Phase 4: Hook Scripts

- [ ] 4-1. `validate_task_completion.py` 구현
- [ ] 4-2. `_test_validate_task_completion.py` TDD 작성 + 통과
- [ ] 4-3. `validate_sot_write.py` 구현
- [ ] 4-4. `_test_validate_sot_write.py` TDD 작성 + 통과

### Phase 5: Agent Definitions + Commands

- [ ] 5-1. 13개 agent .md 파일 생성
- [ ] 5-2. `run-workflow.md` 작성 — 핵심 orchestrator command
- [ ] 5-3. `review-research.md`, `review-planning.md`, `review-final-prd.md` 작성
- [ ] 5-4. `workflow-status.md` 작성

### Phase 6: settings.json + state.yaml + Integration Test

- [ ] 6-1. `settings.json` — 2개 Hook 추가
  - PreToolUse 배열:
    ```json
    {"matcher": "Write", "hooks": [{"type": "command", "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/validate_sot_write.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/validate_sot_write.py; fi", "timeout": 10}]}
    ```
  - PostToolUse 배열:
    ```json
    {"matcher": "TaskUpdate", "hooks": [{"type": "command", "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/validate_task_completion.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/validate_task_completion.py; fi", "timeout": 10}]}
    ```

- [ ] 6-2. `sot_manager.py --init` → `.claude/state.yaml` 초기 파일 생성
- [ ] 6-3. Integration Test: Step 1 dry-run
- [ ] 6-4. `setup_init.py` 실행하여 인프라 검증 (REQUIRED_SCRIPTS 28개)

### Phase 7: Full Workflow Execution

- [ ] 7-1. `/run-workflow` 실행
- [ ] 7-2. Phase별 모니터링 (Research → Planning → Implementation)
- [ ] 7-3. 3개 human checkpoint에서 사용자 리뷰
- [ ] 7-4. 최종 PRD-SaaS-AutoBuilder.md + .ko.md 생성 확인

---

## 8. Agent Teams 실행 흐름 (Steps 2, 9)

### 사전 조건
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수 설정됨
- 미설정 시: Sequential sub-agent fallback

### 실행 순서

```
1. Orchestrator: sot_manager.py --set-team "prd-analysis-team" --status partial
2. Orchestrator: TeamCreate (team_name)
3. 각 teammate에게 TaskCreate (subject, description, output path)
4. Orchestrator: TaskList polling loop
   - 모든 task status == "completed" 될 때까지 반복
   - 각 완료된 task의 output 파일 존재 확인
5. Orchestrator: manifest_generator.py --step N --files "path1,path2,..."
6. Orchestrator: sot_manager.py --finalize-team
7. Orchestrator: sot_manager.py --update-step N --output manifest_path
8. Quality gates (L0 → L1.5)
9. Translation (개별 sub-output을 각각 순차 번역)
10. Orchestrator: TeamDelete (cleanup)
```

### Sequential Fallback (Agent Teams 미가용 시)

```
1. for member in team_members:
2.   Agent(name=member.agent, prompt=member.task)
3.   결과를 member.output_path에 저장
4. manifest_generator.py --step N --files "path1,path2,..."
5. sot_manager.py --update-step N --output manifest_path
```

---

## 9. Translation 흐름 (15 jobs)

### 대상 Steps: 1, 2, 3, 5, 6, 7, 9, 11, 12

| Step | EN Output | KO Output |
|------|-----------|-----------|
| 1 | prompt/research/prd-foundation-analysis.md | .ko.md |
| 2 | 3개 sub-output 개별 번역 | .ko.md × 3 |
| 3 | prompt/research/synthesis-and-gaps.md | .ko.md |
| 5 | prompt/planning/prd-architecture.md | .ko.md |
| 6 | prompt/planning/intent-capture-spec.md | .ko.md |
| 7 | prompt/planning/engine-quality-specs.md | .ko.md |
| 9 | 4개 sub-output 개별 번역 | .ko.md × 4 |
| 11 | prompt/review/prd-adversarial-review.md | .ko.md |
| 12 | prompt/PRD-SaaS-AutoBuilder.md | .ko.md |

### 번역 순서 규칙

1. **순차 실행**: glossary.yaml 일관성을 위해 병렬 번역 금지
2. **Step 순서**: 1 → 2(sub1→sub2→sub3) → 3 → 5 → 6 → 7 → 9(sub1→sub2→sub3→sub4) → 11 → 12
3. **Review PASS 후**: Review가 있는 step (3, 6, 7, 11)은 @reviewer PASS 후 번역 시작
4. **검증**: 각 번역 후 `validate_translation.py --step N --check-pacs --check-sequence`

---

## 10. run-workflow.md Orchestrator Pseudocode

```
1. Read state.yaml → current_step, status
2. If status == "completed": 이미 완료. 종료.
3. If status == "error" or "paused": 사용자에게 상태 보고 후 재개 여부 질문.

4. LOOP (current_step → 12):
   a. workflow_router.py --current-step N → next_steps[]
   b. For each next_step in next_steps:
      - If human: /review-* command 호출. 사용자 승인 대기.
      - If sub-agent:
        i.  Pre-script 실행 (있으면)
        ii. Agent(name=agent_name, prompt=task_description) spawn
        iii. 결과 파일 저장
        iv. Review agent 실행 (있으면) → review-logs/
        v.  quality_gate_runner.py --step N 실행
        vi. @translator 호출 (translate=True인 step)
        vii. bilingual_validator.py --step N 실행
        viii. sot_manager.py --update-step N --output PATH
      - If agent-team:
        i.  Pre-script 실행 (있으면)
        ii. TeamCreate 또는 sequential fallback
        iii. TaskList polling → 전체 완료 대기
        iv. manifest_generator.py → manifest 생성
        v.  quality_gate_runner.py --step N
        vi. 개별 sub-output 각각 @translator 호출
        vii. sot_manager.py --update-step N --output manifest_path
   c. workflow_router.py → 다음 step 결정

5. All 12 steps 완료: sot_manager.py --set-status completed
```

### Compaction 복구 지시 (run-workflow.md 내장)

> "If current_step N has no output in SOT and active_team exists, check TaskList for team status. If all tasks completed, run manifest_generator and continue. If tasks still running, resume polling."

---

## 11. 환경 필수 요건

| 요건 | 확인 방법 | 대체 |
|------|----------|------|
| Python 3.9+ | `python3 --version` | — |
| PyYAML | `python3 -c "import yaml"` | `pip install pyyaml` |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Sequential sub-agent fallback |
| Opus model access | Claude Code 설정 | — |

---

## 12. 위험 관리

| 위험 | 확률 | 완화 |
|------|------|------|
| Agent Teams 실험적 기능 안정성 | 높음 | Sequential fallback 구현 |
| Session compaction 중 팀 상태 유실 | 중간 | SOT active_team + RLM 복구 |
| 15 translations 누적 시간 | 중간 | 품질 우선 (절대 기준 1) |
| PRD.md 2,667줄 파싱 에러 | 낮음 | extract_prd_sections.py 테스트 |
| Hook 간 stdin 경합 | 낮음 | Claude Code가 독립 stdin 제공 |
| sot_manager.py 버그로 SOT 손상 | 낮음 | validate_sot_schema() + atomic_write |

---

## 13. 기존 코드베이스 핵심 참조 (컨텍스트 복구용)

구현 중 참조해야 할 기존 코드의 정확한 위치:

| 함수/상수 | 파일 | 라인 | 용도 |
|----------|------|------|------|
| `SOT_FILENAMES` | `_context_lib.py` | 103 | SOT 파일명 상수 |
| `sot_paths()` | `_context_lib.py` | 469 | SOT 경로 목록 |
| `read_autopilot_state()` | `_context_lib.py` | 501 | SOT 읽기 (YAML+regex) |
| `validate_sot_schema()` | `_context_lib.py` | 613 | S1-S8 스키마 검증 |
| `_read_sot_outputs()` | `_context_lib.py` | 3836 | SOT outputs dict 읽기 |
| `validate_translation_output()` | `_context_lib.py` | 4063 | T1-T7 번역 검증 |
| `validate_step_output()` | `_context_lib.py` | 4556 | L0 Anti-Skip Guard |
| `validate_pacs_output()` | `_context_lib.py` | 4439 | PA1-PA7 pACS 검증 |
| `atomic_write()` | `_context_lib.py` | 2257 | 원자적 파일 쓰기 |
| `REQUIRED_SCRIPTS` | `setup_init.py` | 43-66 | 필수 스크립트 목록 |
| `REQUIRED_SCRIPTS` | `setup_maintenance.py` | 46-69 | D-7 복제 |
| `DISPATCH` | `context_guard.py` | 28-33 | Hook 디스패치 테이블 |
| Hook event table | `CLAUDE.md` | Hook section | DC-6 동기화 대상 |
| `_SOT_FILENAMES` | `query_workflow.py` | 44 | DC-5 동기화 대상 |

---

## 14. 사용자 결정 사항 (PENDING)

1. **구현 승인**: Phase 1-7 순차 구현 진행 여부
2. **Agent Teams**: 실험적 기능 사용 vs. sequential only
3. **추가 성찰**: 5차 성찰 필요 여부
