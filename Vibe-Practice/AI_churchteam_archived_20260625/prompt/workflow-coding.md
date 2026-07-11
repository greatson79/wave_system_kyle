# churchTeam Infrastructure Build — Coding Blueprint (workflow-coding.md v0.8)

> **v0.8 변경 (운용 결함 반영 — R1 자동 러너 SESSION HEADER 디스크 사실 이탈)**: 본 워크플로우의 자동 프롬프트 러너가 직전 turn 산출 0건(의도된 보류)에도 다음 turn의 SESSION HEADER에 "구현 완료"를 기록하는 메타 hallucination 발견. 절대 기준 1(품질·환각 봉쇄)·I2(RLM) 직접 위협. §20 (NEW) 통합 인덱스 + `session_header_disk_audit.py` SessionStart hook 명세 + §11 새 행 #12 fallback. 인용 보고서 path: 본 세션 2026-05-05 turn 2 (코드베이스 전수조사 결과 — 구현 산출물 0건 4중 디스크 검증).

> **v0.7 변경 (PRD v0.5 적대적 A/B/C 성찰 — 방어 불가 7건 반영, P1~P7)**: 이중 SOT 직교 *런타임 검증*(P1) · 자기 진화 외부 관찰자 분리(P2) · 번역 팀 전체 실패 fallback(P3) · FR-25 메커니즘 Phase 2 강등(P4) · M2/M3 Phase 2 강등(P5) · 변경이력 성찰 보고서 포인터 의무(P6) · 게놈 핀 didim 확장(P7). 전 변경은 §19에 통합 인덱스. PRD 본문 수정은 분리 의제(§19.4). 머리 changelog 컨벤션은 P6 적용 — 인용 보고서 path + 갱신일 동반.

> **v0.6 변경 (설계 결함 보고서 반영 — D1~D12 치명·위험)**: SOT 가드 PreToolUse 이동(D1) · RLM stamp prefill 폐기(D2) · Phase 0 자기-부트스트랩 예외(D3) · invocation 영속 저널(D4) · Pre-Phase 0 RED 실행 주체 명시(D5) · 번역 재귀 트리거 차단(D6) · heartbeat hook 쌍 신설(D7) · §11 #1 단순화 + 모델 승격 ADR화(D8) · worktree 머지 충돌 검증자(D9) · RLM stamp 위치 강제(D10) · glossary_rev step-freeze(D11) · safe_mode 역방향 FSM(D12). 전 변경은 §18에 통합 인덱스.

> **이 문서의 성격**: `prompt/workflow.md` v0.5 설계도를 **실제 코드로 구현하기 위한 외과 지시서**. 본 문서가 합의·승인된 후에만 실제 코드 작성에 진입한다. 본 문서 자체는 코드가 아니며, 코드의 *형태·위치·검증 방법·실패 회복 경로*만 명시한다.
>
> **상위 SOT**: `prompt/prd.md` v0.5 + `prompt/workflow.md` v0.5.
> **상태**: draft v0.5 — v0.4 + 할루시네이션 원천 봉쇄 성찰 결과(E-1~E-10) 반영 (결정성 회로의 Python 치환 — 절대 기준 1 강화).
>
> **v0.5 changelog (요약 — Python Determinism Layer 도입)**:
> - **§17 (NEW) Python Determinism Layer**: 세 축(엄밀·반복·할루) 모두 높은 회로 10건을 LLM에서 Python으로 이동. 절대 기준 1(품질 우선) 강화 + 절대 기준 2(SOT/RLM) 보강. 도입 순서: E-4·E-7 즉시 → E-1·E-6 ADR 후 → E-2·E-3·E-5 결정 카드 후.
> - **E-1 Glossary lock-and-restore**: §6에 `glossary_placeholder_codec.py` (PreToolUse `Task(@translator-ko)` 매처) — 번역 직전 glossary 키를 `<<TERM_NN>>` 치환 → MT → 복원. *사후* 검증(`--check-glossary-rev`)이 *사전* 봉쇄로 승격.
> - **E-2 Back-translation similarity 판정자**: §10.3에 `score_translation_quality.py` — rouge-L 1차(로컬·결정적) GREEN. 임베딩 cosine 2차는 ADR `accepted` 후에만 활성 (R1 클라우드 의존 — 본 문서가 자동 허가 안 함). §4.5 0.85 임계 단일 모듈 핀.
> - **E-3 Korean 4-line card 템플릿화**: §13.1·§13.3에 `format_korean_card.py` (jinja-like 슬롯 합성) — C-3 4줄·결정 카드·면책 라인 *생성*은 슬롯 채움만 LLM, 4줄 뼈대는 `i18n/ko.yaml` 정본 인용. *생성*과 *검증*(`validate_translation.py --pattern`) 1:1 정합.
> - **E-4 RLM 5줄 stamp 자동 주입**: §6에 `rlm_stamp_prefill.py` (PreToolUse `Task` 매처 — sub-agent spawn 시 (a)(b)(c)(d) 4줄 prefill, (e) Intent만 LLM 자유 작성). §9.3 stamp 형식 위반 *원천 0*.
> - **E-5 SOT JSON-Patch 통합기**: §6·§9.2에 `merge_sot_proposals.py` — Lead가 teammate 산출 통합 시 LLM이 머지하지 않음. JSON-Schema 기반 결정성 머지 + 키 충돌 감지. Tier 0(LLM)은 "수락/거부" 결정만.
> - **E-6 ADR 스캐폴드 발번기**: §13.2에 `adr_scaffold.py` — ADR-{NNN} 자동 발번, 5섹션 빈 템플릿, Status enum FSM. LLM은 Context/Decision/Consequences 본문만.
> - **E-7 부교역자 한국어 호칭 prompt 주입**: §6에 `pastoral_honorific_inject.py` (PreToolUse `Task(<pastoral-role>)` 매처) — `roster.yaml.korean_label`을 fresh-read해 system prompt에 string-substitute. LLM lookup 부담 0 + RLM 강화.
> - **E-8 state FSM 응집**: §10.3에 `state_machine.py` — `pending → en_done → en_done_provisional? → translating → bilingual_done` + 분기 `translation_failed | failed`. v0.4까지 분산되어 있던 전이 검증 통일.
> - **E-9 pACS 버킷팅 함수**: §10.3 `validate_pacs.py`에 `bucket_score(F, C, L) -> {GREEN|YELLOW|RED}` 결정성 함수 명시 (임계 70/50, §13.3 인용).
> - **E-10 inheritance-manifest 생성기**: §14 Phase 0에 `generate_inheritance_manifest.py` 명시 — `parent_hook_pin_audit.py`(검증)와 쌍. 부모 hook 경로 walk + sha256.
> - **§15 모호 지점 갱신**: 신규 모호 지점 #15 (E-2 임베딩 2차 채택 ADR 트리거 시점) 추가. 기존 #1~#14 변동 없음.
> - **CCP 비례성**: 10건 일괄 도입 금지. ADR 단위 분리 진입(§17.3 도입 게이트 표).
>
> **v0.4 changelog (요약)**:
> - **D-1 번역 자동 트리거 hook 신설**: §6에 `translator_trigger_postwrite.py` (PostToolUse, step `en_done` 진입 감지 → Tier 0 큐에 `@translator-ko` invocation enqueue).
> - **D-2 번역 품질 team 승격**: §4에 `translation-quality-team` (Lead=Tier 0, Teammates=`@translator-ko` + `@back-translator-en` + `@glossary-validator`). 단일 sub-agent 대비 *품질 기준상* 3중 적대 검증으로 승격.
> - **D-3 `/팀-번역재시도` command 신설**: §7. `translation_failed` step 수동 회수.
> - **D-4 agent-selection 프로토콜**: §16 (NEW) `agent-selection.md` — sub-agent vs agent-team 선택 기준 = **품질 단일축**(다관점 검증 필요 시 team, 결정론적 단일 변환 시 sub-agent). 토큰·속도 기준 명시 배제.
> - **D-5 품질 게이트 L0/L1/L1.5/L2 명시 매핑**: §10.3.2 (NEW) 부모 게놈 4계층 → 본 워크플로우 validator 1:1 매핑 표.
> - **D-6 glossary.yaml 운용 경로 + 갱신 프로토콜**: §12.1 (NEW) `translations/glossary.yaml` 위치 고정 + 신규 용어는 ADR 경유 추가(자동 쓰기 금지) + `validate_translation.py --check-glossary-rev`로 SOT `invocations[].glossary_rev` 일관성 강제.
>
> **v0.3 changelog (요약)**:
> - C-1 Intent Stamp: §9.3 RLM stamp 4줄 → 5줄 (Intent 1줄 추가).
> - C-2 영향 범위 자동화: §6에 `impact_scan.py` · `parent_hook_pin_audit.py` · `validate_owner_matrix.py` 신설, §6 하단 hook 의존 매트릭스 표 추가.
> - C-3 Per-Edit Change Plan: §13.1에 마이크로 템플릿 5항 추가.
> - C-4 SOT 단일 쓰기자 강건화: §9.2에 `tier0.lock` 2nd-factor.
> - C-5 Bilingual 부분 진입: §9.1.1 `status`에 `en_done_provisional` 추가.
> - C-6 스키마 마이그레이션: §9.1.1 + §10.3에 `migrate_state_v01_to_v02.py` 명시.
> - C-7 fork_manager 정식 편입: §6 hook 표 + §10.1 매핑.
> - C-8 RLM 시간 해상도: §9.3·§6 PreToolUse(Edit\|Write\|Task) 매처 추가.
> - C-9 validator DAG: §10.3에 `validators-dag.md` 1장 신설.
> - C-10 ADR 트리거 매처 명세: §6 `adr_trigger_audit.py`.
> **로컬 실행 전제**: 모든 구성은 사용자 macOS 로컬에서 자동 실행됨. 클라우드 서비스 의존 0 (Telegram·NotebookLM·Gmail은 *선택* 외부 채널이며 fallback 의무).
> **언어 운용 (절대 원칙 강화)**:
> - **사용자가 워크플로우 실행 명령을 내리면, 모든 사고·작업·산출물은 English로 수행**한다 (AI 성능 극대화 — 절대 기준 1 근거).
> - **각 단계 영어 산출물 직후 `@translator-ko` 서브에이전트가 자동 호출**되어 한국어 쌍을 생성. SOT는 `outputs.{en,ko}` 쌍으로 저장된다 (단계별 trigger).
> - agent/skill/hook/command frontmatter·system prompt·코드·주석·테스트·내부 로그 = English (예외 없음).
> - 사용자 가시 텍스트(C-3 4줄·결정 카드·진척 라인·면책 라인) = Korean — `i18n/ko.yaml` 또는 translator 산출 `outputs.ko`에서 로드.
> - **v0.1 대비 변경**: `@translator` 호출이 "Translation: 표기 단계 한정" → "**모든 단계 종료 직후 자동 호출**"로 확장됨. 단계는 영어 산출 완료(`en_done`) → 번역(`translating`) → `bilingual_done`을 거쳐야 다음 단계 진입.

---

## §0. Reading Map

| 섹션 | 다루는 것 | 제1 목적 연결 |
|---|---|---|
| §1 | 전체 아키텍처 (3-Tier) | 약속 4 단일 진입·약속 2 메타빌드 |
| §2 | Orchestrator 계층 | 절대 기준 2 SOT 단일 쓰기 강제 |
| §3 | Sub-agents 카탈로그 | 약속 4 12직 + 적대적 검토 |
| §4 | Agent Teams (teammate 구성) | 품질 우선 — 독립 컨텍스트 100% 집중 |
| §5 | Skills 카탈로그 | 부모 게놈 상속 + 도메인 신학 발현 |
| §6 | Hooks 카탈로그 | §C.1 SOT·RLM 코드 강제·신학 결정적 게이트 |
| §7 | Slash Commands | 약속 4 단일 진입점 + 결정 동선 |
| §8 | fork (git worktree) 사용처 | 약속 2 메타빌드·약속 3 ⑤ 재해 복구 |
| §9 | SOT · RLM 강제 메커니즘 | 절대 기준 2 + Rule 4 |
| §10 | TDD Automation | 절대 기준 1 품질 + 약속 5 자가 검증 |
| §11 | Fallback 경로 (10종) | 요구사항 7 — 무응답·붕괴 회복 |
| §12 | 영어 운용 경계 | 지시 사항 5 |
| §13 | 평가 기준 3종 파일 | 절대 기준 1 보강 (정돈된 평가 기준 = 품질의 일부) |
| §14 | 빌드 순서 (Phase 0 → 1 → 2) | 약속 3 "끝까지" 5단계 + 지연 빌드 |
| §15 | 모호 지점 — 다음 라운드 결정 | 자기 점검 3층위 |
| §16 | Agent Selection Protocol | 절대 기준 1 (품질 단일축) |
| §17 | Python Determinism Layer (NEW v0.5) | 절대 기준 1 강화 (할루시네이션 원천 봉쇄) |

---

## §1. Overall Architecture (3-Tier Topology)

```
┌─ Tier 0: Parent Orchestrator (THE SINGLE SOT WRITER)
│      • Runs in the user's primary Claude Code session
│      • Owns: state.yaml writes, lifecycle of all spawns, user dialog
│      • Enforces: RLM pre-action verification, retry budget, escalation chain
│      • Cannot be parallelized — there is exactly ONE
│
├─ Tier 1: Phase Orchestrators  (sub-agents under Tier 0)
│      • @research-orchestrator   (workflow.md Step 1-2-3)
│      • @planning-orchestrator   (Step 4-5-6-7)
│      • @impl-orchestrator       (Step 7.5-15, internally splits Phase 0/1/2)
│      • Each: read SOT → dispatch Tier 2 → produce *proposal files*
│      • Never writes SOT. Returns proposed-diff to Tier 0.
│
└─ Tier 2: Workers
       • Agent Teams (parallel, isolated worktree contexts) — §4
       • Specialist sub-agents (sequential domain builders) — §3
       • @didim-bridge (sole conduit to weekly-works) — §3
       • Adversarial reviewers (3-way) — §3
       • @translator (boundary-only EN↔KO) — §3
```

**불변식 (Invariants — 코드 강제)**:
- I1: Tier 1·2의 어떤 에이전트도 SOT(state.yaml) 직접 쓰기 금지. PostToolUse hook이 매처로 차단(§6 `dual_sot_pairing_guard.py` 확장).
- I2: 모든 Tier 1·2 system prompt 첫 5줄에 RLM 체크리스트 의무 삽입(§9.3).
- I3: 모든 sub-agent invocation은 `state["steps"][step_id]["invocations"]`에 Tier 0이 기록(§9.4).
- I4: 30s 무응답 = timeout 가정 → fallback chain 진입(§11).

**제1 목적 연결**: 절대 우선순위 ③(목회자 최종 검토) 보존을 위해 자동 흐름이 *설계상* 끊기는 3 노드(4.5 제목 게이트·신학 필터 FAIL·외부 발행 직전)는 Tier 0의 사용자 대화 단계로 *반드시 회귀*한다.

---

## §2. Orchestrator Layer

### §2.1 Tier 0 — Parent Orchestrator
- 위치: 본 Claude Code 세션 자체. 별도 agent 파일 없음 (사용자가 곧 Parent의 *권한자*).
- 역할:
  1. SOT 단일 쓰기자 (`prompt/workflow-research/state.yaml` + `Claude_skills/AI_churchteam/.claude/state.yaml`)
  2. Phase Orchestrator 호출 (Task 도구로 spawn)
  3. 사용자 결정 카드 발행/수신 (Step 3·7·15)
  4. Retry budget enforcement (RB1-RB3)
  5. Escalation chain final responder (한국어 4줄 카드)
- 코드: 없음. *프로토콜*. 본 문서 §9 SOT 단일 쓰기 강제 메커니즘이 그 권한을 코드로 보장.

### §2.2 Tier 1 — Phase Orchestrators (3개)

| 이름 | 모델 | scope | tools | 책임 Step | 산출 |
|---|---|---|---|---|---|
| `@research-orchestrator` | opus | project | Read, Grep, Glob, Task | 1, 2, 3 | `prompt/workflow-research/{prd-idea-index.md, gate-resolution-summary.md}` |
| `@planning-orchestrator` | opus | project | Read, Write, Edit, Grep, Task | 4, 5, 6, 7 | `prompt/prd.v0.6.diff.md`, `Claude_skills/AI_churchteam/.claude/{roster.yaml, three-axis-mapping.md, hierarchy-view.md, didim-bridge-spec.md, dual-sot-pairing-policy.md}` (draft) |
| `@impl-orchestrator` | opus | project | Read, Write, Edit, Bash, Task | 7.5–15 | `Claude_skills/AI_churchteam/.claude/**` (lazy-built) |

- **공통 frontmatter (English)**:
  ```yaml
  ---
  name: <orchestrator-name>
  description: Phase orchestrator for workflow.md Steps <range>. Reads SOT, dispatches sub-agents, returns proposal-diffs to Parent. NEVER writes SOT directly.
  model: opus
  scope: project
  permissionMode: default
  tools: [...]
  ---
  ```
- **공통 system prompt 골격**: RLM 체크리스트 (§9.3) → Step routing table → Verification gate (validate_workflow.py invocation) → Proposal-diff format → Escalation chain.

---

## §3. Sub-agents Catalog

### §3.1 Build/Architect agents (Research·Planning Phase)
| Agent | Model | Scope | Step | Output |
|---|---|---|---|---|
| `@prd-reader` | opus | project | 1 | `prd-idea-index.md`, `genome-manifest.draft.json` |
| `@gate-A-meta-build` | opus | project | 2 | `gate-resolutions/A.md` |
| `@gate-B-pairing` | opus | project | 2 | `gate-resolutions/B.md` |
| `@gate-C-ux` | opus | project | 2 | `gate-resolutions/C.md` |
| `@gate-D-resilience` | opus | project | 2 | `gate-resolutions/D.md` |
| `@meta-build-architect` | opus | project | 4 | PRD/idea diff `.md` |
| `@team-architect` | opus | project | 5 | `roster.yaml`, `three-axis-mapping.md`, `hierarchy-view.md` |
| `@didim-bridge-architect` | opus | project | 6 | `didim-bridge-spec.md`, `dual-sot-pairing-policy.md` |

### §3.2 Implementation agents
| Agent | Model | Scope | Step | Output |
|---|---|---|---|---|
| `@bootstrapper` | opus | project | 9 | `inheritance-manifest.json`, `commands/팀.md`, child `state.yaml` |
| `@phase1-pastoral-builder` | opus | project | 10 | `agents/<3-5 pastoral>.md` |
| `@phase1-filter-builder` | opus | project | 10 | `hooks/scripts/theology_filter_dual.py`, `agents/theological-reviewer.md` |
| `@phase1-ux-builder` | sonnet | project | 10 | `skills/health-dashboard/`, 3-Door render |
| `@phase1-bridge-builder` | sonnet | project | 10 | `agents/didim-bridge.md` |
| `@weekly-cycle-orchestrator` | sonnet | project | 11 | weekly cycle log |
| `@spof-recovery` | sonnet | project | 12 | `skills/spof-recovery/` |
| `@phase2-evolution-builder` | opus | project | 13 | `hooks/scripts/self_evolution_gate.py` |
| `@phase2-roster-extender` | opus | project | 13 | additional 7 pastoral `.md` |
| `@phase2-debate-builder` | opus | project | 13 | M3 debate engine spec |
| `@disaster-recovery` | opus | project | 14 | `skills/disaster-recovery/` |

### §3.3 Bridge / Reviewer / Translator
| Agent | Model | Scope | Tools | Trigger |
|---|---|---|---|---|
| `@didim-bridge` | sonnet | project | Read, Write, Bash | Every weekly-works invocation (CM-1/2/3 modes per Step 6) |
| `@reviewer` | opus | user | Read, Glob, Grep | Post-processing of every Step output |
| `@fact-checker` | opus | user | Read, Glob, Grep, WebSearch, WebFetch (Rule 2 적용) | Same |
| `@theological-reviewer` | opus | project | Read, Grep + skills [reformed-theology, biblical-hermeneutics] | Theology filter 1st stage (D-1) |
| `@translator-ko` | sonnet | project | Read (SOT), Glob, Grep | **모든 step `status: en_done` 자동 트리거 (Tier 0 호출).** stateless·읽기 전용. SOT 직접 쓰기 금지 — 결과를 Tier 0에 리턴, Tier 0이 `outputs.ko`에 기록 |
| `@translator` (legacy) | sonnet | project | Read, Write, Glob, Grep, Edit | (deprecated for prompt-runner-scope) 부모 게놈 글로벌 번역기. 본 워크플로우에서는 `@translator-ko`로 대체 |

### §3.4 12 Pastoral Roles (지연 빌드)
- Phase 1 활성: 3–5직 (BL-3 결정 결과). Phase 2 추가: 7직.
- 공통 frontmatter:
  ```yaml
  ---
  name: <role-id>            # English snake_case
  description: <one-line mission, English>
  model: sonnet               # opus only for theology-reasoning-heavy roles
  scope: project
  permissionMode: default
  skills: [korean-pastoral-style, theological-reasoning, ...]
  axis: insight | strategy | execution
  reports_to: <role-id>
  authority_boundary: <one-line, English>
  ---
  ```
- **사용자 가시 호칭은 한국어** (system prompt 내 명시: "When addressing the user, refer to yourself by Korean honorific from `roster.yaml.korean_label`").

---

## §4. Agent Teams (Teammate 구성)

### §4.1 `entry-gate-resolution-team` (workflow.md 명시 — Step 2)
- Lead: `@research-orchestrator` (Tier 1)
- Teammates: `@gate-A-meta-build` / `@gate-B-pairing` / `@gate-C-ux` / `@gate-D-resilience`
- Lifetime: TeamCreate at Step 2 start → TeamDelete at Step 3 entry
- **Worktree isolation (fork #1, §8)**: each teammate spawned with `isolation: "worktree"` — `worktrees/gate-{A,B,C,D}/`. 산출 통합은 Lead가 4 worktree에서 `gate-resolutions/{X}.md`만 회수.
- Turn cap: 18 (P0-4) · BL ≥ 2 turn 보장
- Conflict matrix: Lead 통합 시 `validate_workflow.py --check-teammate-conflict` 실행 → BL × BL 충돌 매트릭스를 Step 3 카드에 주입.

### §4.2 `design-finalization-team` (제안 — Step 5+6)
- Lead: `@planning-orchestrator`
- Teammates: `@team-architect` (Step 5) · `@didim-bridge-architect` (Step 6)
- Lifetime: Step 5 시작 → Step 7 entry
- Parallelism: 단일 트리(worktree 미사용 — 충돌 위험 낮음). 산출 충돌 감지 시에만 fork 승격.

### §4.3 `phase1-build-team` (제안 — Step 10)
- Lead: `@impl-orchestrator`
- Teammates: `@phase1-pastoral-builder` · `@phase1-filter-builder` · `@phase1-ux-builder` · `@phase1-bridge-builder`
- Lifetime: Step 10 시작 → Step 11 entry
- Parallelism: 4축 독립 — 단일 트리 가능. 단, `agents/` 동일 디렉터리 쓰기 충돌 방지 위해 *파일별 owner 매트릭스* 사전 합의(Lead가 owner 매핑 SOT 기록).

### §4.4 `phase2-hardening-team` (제안 — Step 13)
- Lead: `@impl-orchestrator`
- Teammates: `@phase2-evolution-builder` · `@phase2-roster-extender` · `@phase2-debate-builder`
- Lifetime: Step 13 시작 → Step 14 entry
- Worktree isolation (fork #2, §8): self-evolution gate 변경은 fork에서 검증 후 머지.

### §4.5 `translation-quality-team` (D-2 v0.4 신규 — 모든 step 종료 직후 자동 승격)
- Lead: **Tier 0 (Parent Orchestrator)** — SOT 단일 쓰기자 원칙 유지.
- Teammates (3중 적대 검증):
  1. `@translator-ko` (sonnet, project) — EN→KO 1차 번역.
  2. `@back-translator-en` (sonnet, project, NEW) — KO→EN 역번역. 의미 손실 측정용.
  3. `@glossary-validator` (haiku, project, NEW) — `translations/glossary.yaml` 용어 일관성 + KI-2 식별자 영어 보존 검사.
- Lifetime: 매 step `status: en_done` 진입 시 `translator_trigger_postwrite.py`가 큐에 적재 → Tier 0이 다음 turn에 TeamCreate → 3 산출 통합 후 TeamDelete.
- Worktree isolation: **불필요** (읽기 전용·결정론적 변환). 단일 트리에서 병렬 spawn.
- 합격 기준 (모두 PASS 시 `bilingual_done`):
  - T1–T9 (translator) PASS
  - 역번역 의미 일치율 ≥ 0.85 (cosine on embeddings or rouge-L proxy)
  - glossary 용어 일관 (신규 용어 발견 시 `translation_failed` → ADR 트리거)
  - KI-1 (en/ko 키 1:1) + KI-2 (식별자/SOT 키 영어 보존)
- 실패 분기: 1회 retry (RB1) → 실패 시 `translation_failed` 상태 → `/팀-번역재시도` 카드(§7 D-3) 또는 한국어 4줄 escalate.
- **품질 우선 근거 (절대 기준 1)**: 단일 `@translator` 호출 대비 토큰 ~3x 소모. 토큰 비용은 *수용*. 품질이 절대 기준.

### §4.6 SOT 쓰기 규약 (모든 Team 공통)
- Teammate는 **자기 산출 파일만** 작성. SOT는 *제안 형식*(JSON-Patch 또는 YAML-merge)으로 Lead에 전달.
- Lead는 Tier 0(Parent)에 통합 제안 단일 호출. Tier 0이 RLM 재독 + dual_sot_pairing_guard 통과 후 SOT 갱신.

---

## §5. Skills Catalog

### §5.1 부모 게놈 상속 (재정의 금지)
- `tdd-workflow` · `verification-loop` · `iterative-retrieval` · `code-tour` · `agentic-engineering`

### §5.2 도메인 신학 발현 (신규 — Phase 1)
| Skill | 위치 | 목적 |
|---|---|---|
| `theological-reasoning` | `Claude_skills/AI_churchteam/.claude/skills/theological-reasoning/` | 개혁주의 신학 추론 (`@theological-reviewer` 주입) |
| `biblical-hermeneutics` | 동상 | 본문 해석 원칙 |
| `korean-pastoral-style` | 동상 | 모든 부교역자 한국어 문체 |
| `sermon-structure` | 동상 | 실행 보조 축 |

### §5.3 운용 발현 (신규 — Phase 1·2)
| Skill | 위치 | 목적 |
|---|---|---|
| `health-dashboard` | `skills/health-dashboard/` | FR-22 6칸 카드 렌더링 |
| `spof-recovery` | `skills/spof-recovery/` | C-3 4줄 + D-5 fallback |
| `disaster-recovery` | `skills/disaster-recovery/` | BL-4 3종 시나리오 |

### §5.4 Skill 작성 규약
- `SKILL.md` (English) — WHY/WHEN/CONTRACT
- `references/*.md` (English) — WHAT/HOW/VERIFY
- `tests/golden/*.yaml` — 결정적 입력→출력 회귀 셋
- 사용자 가시 출력 string은 `references/i18n/ko.yaml`에서 한국어 로드

---

## §6. Hooks Catalog

| Hook event | matcher | script | exit codes | TDD test file |
|---|---|---|---|---|
| Setup | `init` | `setup_init_churchteam.py` | 0 pass / 2 block | `_test_setup_init_churchteam.py` |
| Setup | `init` | `parent_hook_pin_audit.py` (NEW — C-2c) — 부모 hook 경로 존재성 + sha256 핀 검사 | 0 / 2 | `_test_parent_hook_pin_audit.py` |
| PreToolUse | `Bash` | `block_destructive_commands.py` (parent inherit) | 0 / 2 | parent already covered |
| PreToolUse | `Bash(git worktree*)` | `fork_manager_audit.py` (NEW — C-7) — fork 4종 트리거 검증 | 0 / 2 | `_test_fork_manager_audit.py` |
| PreToolUse | `Edit\|Write` | `block_test_file_edit.py` (TDD guard, parent inherit) | 0 / 2 | parent |
| PreToolUse | `Edit\|Write` | `tdd_red_first_check.py` (NEW) | 0 / 2 | `_test_tdd_red_first.py` |
| PreToolUse | `Edit\|Write` | `impact_scan.py` (NEW — C-2a) — AST 심볼·역참조·DTO co-change·테스트 매핑 4종 advisory 출력 | 0 / 1 (warn) | `_test_impact_scan.py` |
| PreToolUse | `Edit\|Write` | `bilingual_provisional_guard.py` (NEW — C-5) — 직전 step `en_done_provisional` 시 쓰기 차단 | 0 / 2 | `_test_bilingual_provisional_guard.py` |
| PreToolUse | `Edit\|Write\|Task` | `validate_rlm.py --pre` (NEW — C-8) — stamp ts 60s 초과 시 재독 강제 | 0 / 2 | `_test_validate_rlm_pre.py` |
| PreToolUse | `Task` (sub-agent spawn) | `record_subagent_invocation.py` (NEW — §9.4) | 0 (always) | `_test_record_invocation.py` |
| PostToolUse | `Edit\|Write(state.yaml)` where `status` transitions to `en_done` AND `invocations[-1].agent != 'translator-ko'` (D-6 v0.6 재귀 차단) | `translator_trigger_postwrite.py` (NEW — D-1 v0.4 / v0.6 매처 보강) — Tier 0 invocation 저널(NDJSON, §9.4)에 `@translator-ko` 적재. Tier 0이 다음 turn에 §4.5 team spawn. *기록 전용·차단 없음* | 0 (always) | `_test_translator_trigger.py` (재귀 케이스 골든 추가) |
| **PreToolUse** (v0.6 D-1 이동) | `Edit\|Write(**state.yaml)` | `dual_sot_pairing_guard.py` (C-4 2nd-factor 적용 — 쓰기 *전* 차단. PostToolUse 잔존 인스턴스는 격리망으로만 유지) | 0 / 2 | `_test_dual_sot_pairing_guard.py` (PreToolUse 시나리오 골든 추가) |
| PreToolUse | `Task` | `heartbeat_emit.py` (NEW — v0.6 D-7) — sub-agent spawn 직전 `runtime_directories/heartbeat/<task-id>.json`에 `ts`, `parent_agent`, `target_agent` 기록 | 0 (always) | `_test_heartbeat_emit.py` |
| Setup (cron 30s) | (any) | `heartbeat_check.py` (NEW — v0.6 D-7) — 활성 task의 hb ts > 30s 부재 시 §11 #1 fallback 트리거 | 0 / 1 (warn) | `_test_heartbeat_check.py` |
| PostToolUse | `Edit\|Write(Claude_skills/AI_churchteam/.claude/state.yaml)` | `validate_owner_matrix.py` (NEW — C-2d) — `state.yaml.steps.<id>.owner_matrix` 스키마 검증 | 0 / 2 | `_test_validate_owner_matrix.py` |
| PostToolUse | `Edit\|Write(state.yaml or **/phase or **/decision_card.signed)` | `adr_trigger_audit.py` (NEW — C-10) — phase 변경·결정 카드·자율 금지 7행 변경 매처에서 ADR 부재 차단 | 0 / 2 | `_test_adr_trigger_audit.py` |
| PostToolUse | `Edit\|Write(Claude_skills/AI_churchteam/output/**/*.md)` | `theology_filter_dual.py --stage deterministic` | 0 / 2 | `_test_theology_filter_dual.py` |
| PostToolUse | `Edit\|Write` | `output_secret_filter.py` (parent inherit) | 0 / 2 | parent |
| PostToolUse | `Edit\|Write` | `output_internal_id_filter.py` (NEW — C-1) | 0 / 1 (warn) | `_test_output_internal_id_filter.py` |
| PostToolUse | `Edit\|Write(pastoral-decision-logs/**)` | `pastoral_log_pii_mask.py` (NEW) | 0 / 2 | `_test_pastoral_log_pii_mask.py` |
| PostToolUse | `Edit\|Write` | `validate_convention.py --advisory` (NEW — §13.1) | 0 / 1 | `_test_validate_convention.py` |
| Stop | (any) | `generate_context_summary.py` (parent inherit) | 0 | parent |
| PreCompact | (any) | `save_context.py --before-compact` (parent inherit) | 0 | parent |
| SessionStart | (any) | `restore_context.py` (parent inherit) | 0 | parent |
| SessionEnd | (any) | `save_context.py` (parent inherit) | 0 | parent |

**신규 hook (v0.3 누계 14종)**: 모두 RED-first(테스트 먼저). 커버리지 ≥ 90%.

### §6.1 Hook 의존 매트릭스 (C-2b v0.3 신규)

> hook 간 *데이터/큐/파일* 의존을 명시. 순환 의존 금지. 자세한 실행 순서 DAG는 §10.3 `validators-dag.md` 참조.

| 스크립트 (행) | 의존 (열) | 의존 형태 |
|---|---|---|
| `validate_rlm.py` | `record_subagent_invocation.py` | RLM stamp 검증 시 invocation 큐의 마지막 ts 비교 |
| `dual_sot_pairing_guard.py` | `tier0.lock` (파일) + `CLAUDE_AGENT_ID` (env) | 2nd-factor |
| `impact_scan.py` | (없음 — 읽기 전용 advisory) | 정적 분석 |
| `validate_owner_matrix.py` | `state.yaml.steps.<id>.owner_matrix` | 스키마 |
| `adr_trigger_audit.py` | `prompt/workflow-research/standards/adr/` | 디렉터리 인덱스 |
| `bilingual_provisional_guard.py` | `state.yaml.steps.<id>.status` | RLM read |
| `fork_manager_audit.py` | `.claude/scripts/fork_manager.py` | 함수 매처 |
| `parent_hook_pin_audit.py` | 부모 게놈 hook 경로 + sha256 핀 표 | Setup-time only |
| `theology_filter_dual.py` | `@theological-reviewer` agent + `i18n/ko.yaml` | LLM + 정본 한국어 |
| `output_internal_id_filter.py` | (parent inherit 패턴) | 정적 |

**금지**: `dual_sot_pairing_guard.py` ↔ `validate_owner_matrix.py` 상호 호출 (둘 다 PostToolUse SOT 매처) — 중복 차단 방지 위해 `validate_owner_matrix.py`는 `dual_sot_pairing_guard.py` PASS 후에만 작동(exit code 전파).

---

## §7. Slash Commands

| Command | Step / Trigger | Body | TDD scenario |
|---|---|---|---|
| `/팀` | 단일 진입점 (Phase 0+) | 3-Door Korean 분기 (M1 회의 / M2 부르기 / M3 위임·반박) | `_test_command_team_root.py` |
| `/팀-결정` | Step 3 | 결정 카드 + `--resume` | `_test_command_decision.py` |
| `/팀-진입허가` | Step 7 | Implementation 봉인 해제 + BL-9 D-2 합의 서명 | `_test_command_unseal.py` |
| `/팀-회중허가` | Step 15 | 외부 노출 최종 검토 | `_test_command_publish_approval.py` |
| `/팀-건강` | 상시 | FR-22 6칸 카드 즉시 렌더 | `_test_command_health.py` |
| `/팀-lock-회수` | SPOF (D-4) | self-lock 1동작 회수 | `_test_command_lock_recovery.py` |
| `/팀-회복` | SPOF/DR | C-3 4줄 1동작 안내 | `_test_command_recover.py` |
| `/팀-동시갱신-회수` | B-π P-β 차단 해제 | 60초 윈도우 회수 | `_test_command_concurrent_recovery.py` |
| `/팀-신학시드` | Step 10 (1회) | 회귀 케이스 ≥ 20개 시드 검토 | `_test_command_theology_seed.py` |
| `/팀-권한변경` | BL-11 | 외부 채널 권한 변경 4줄 결정 카드 | `_test_command_authority_change.py` |
| `/팀-규약갱신` | code-convention 변경 | 사용자 명시 결정 카드 (§13.1) | `_test_command_convention_update.py` |
| `/팀-번역재시도` | step `translation_failed` 회수 (D-3 v0.4) | 실패한 step id 입력 → §4.5 team 재호출 + glossary 신규 용어 ADR 트리거 | `_test_command_translation_retry.py` |

- 모든 command `.md` body: English description + Korean user-facing prompt template.
- 모든 command 응답은 SOT pastoral-decision-logs/에 누적(Tier 0 단일 쓰기).

---

## §8. Fork (git worktree) Use Cases — 4종 채택

| # | Trigger | Fork target | Merge condition | Cleanup |
|---|---|---|---|---|
| 1 | Step 2 4-teammate parallel | `worktrees/gate-{A,B,C,D}/` | Lead가 산출 회수 후 자동 cleanup (no-change worktree 자동 삭제) | TeamDelete |
| 2 | Step 9 Phase 0 child instance bootstrap | `worktrees/bootstrap-{ts}/` | `validate_workflow.py --check-genome-inheritance` PASS + 사용자 `/팀-진입허가` | 본 트리 promotion 후 worktree 삭제 |
| 3 | Step 13 D-3 self-evolution diff | `worktrees/evolution-{adr-id}/` | (a) AST/section matcher PASS, (b) 3중 적대 검토 PASS, (c) 1주 사이클 시연 fork PASS | 사용자 `/팀-진입허가 --evolution` 후 머지 |
| 4 | Step 14 DR rehearsal (분기별) | `worktrees/dr-rehearsal-{ts}/` | 시뮬레이션 시나리오 3종 통과 + 회귀 케이스 추출 | 회귀 케이스만 본 트리 흡수, worktree 폐기 |

**기각된 fork 사용**: 매 step 자동 fork (Context Preservation으로 충분), 매 결정 분기 fork (pastoral-decision-logs로 충분), 모델 A/B 테스트 (v0.1 범위 외).

**Fork manager**: `.claude/scripts/fork_manager.py` (NEW) — `worktree_create / worktree_validate / worktree_promote / worktree_discard` 4 함수. 모든 호출은 Tier 0 권한.

---

## §9. SOT · RLM Enforcement

### §9.1 두 SOT 파일
- `prompt/workflow-research/state.yaml` — workflow 자체 진행 상태
- `Claude_skills/AI_churchteam/.claude/state.yaml` — child 운용 상태
- 스키마 정본: workflow.md §SOT 표 (변경 시 ADR 의무)

### §9.1.1 이중 언어 스키마 확장 (v0.2 신규 — 추가 절대 원칙 반영)
두 SOT 파일 모두 다음 필드를 *추가*. 기존 필드 변경·삭제 없음(하위 호환).
```yaml
schema_version: "0.2"           # v0.3 신규. migrate_state_v01_to_v02.py로 0.1→0.2 승급
execution_language: en          # 워크플로우 시작 시 고정. 불변
translation_policy:
  target: ko
  trigger: after_each_step      # 모든 step en_done 직후
  writer: tier0_orchestrator_only
steps:
  step-<id>:
    # status 흐름: pending → en_done → (선택)en_done_provisional → translating → bilingual_done
    #             분기: translation_failed | failed
    status: pending|en_done|en_done_provisional|translating|bilingual_done|translation_failed|failed
    outputs:
      en: { ... }               # 영어 원본 (worker/orchestrator 산출)
      ko: { ... }               # @translator-ko 산출 (Tier 0이 기록)
    invocations:
      - { agent: translator-ko, ts: <iso8601>, input_ref: outputs.en, output_ref: outputs.ko, glossary_rev: <sha> }
```
- **단계 진입 게이트**: 다음 step의 *쓰기 단계*는 직전 step `bilingual_done`일 때만 진입. *읽기 전용 계획 단계*는 `en_done_provisional`로 한정 진입 가능 (C-5). `validate_workflow.py --check-bilingual-gate` (W12)로 분기 강제.
- **`en_done_provisional` 사용 규칙**: 다음 step에서 Read·Grep·Glob만 허용. Edit·Write·Task는 PreToolUse hook에서 차단(exit 2). bilingual_done 도달 시 자동 해제.
- **번역 실패 시**: `translation_failed` 진입 → RB1–RB3 재시도 예산 → 한국어 4줄 escalate.
- **사용자 한국어 입력 처리**: 사용자 입력이 한국어인 경우 Tier 0이 즉시 영어 변환 후 `inputs.user.{ko_original, en}` 양쪽 보존(원문 손실 0).
- **스키마 마이그레이션 (C-6)**: `schema_version` 필드 부재 또는 `< 0.2` 시 `migrate_state_v01_to_v02.py` 자동 호출. 골든 픽스처 3종(`tests/migrations/{empty,mid-step,post-translate}.yaml`)로 회귀 보장. 마이그레이션은 ADR 의무.
- **Phase 0 자기-부트스트랩 예외 (v0.6 D-3)**: `translation-quality-team`(§4.5) 자체 빌드 *이전*의 Phase 0 step은 `bilingual_done` 게이트가 구조적으로 충족 불가하므로, 다음 한정 예외를 둔다.
  1. `phase: pre_phase0 | phase0` AND `step.flags.translator_team_built != true` 인 step에 한해 진입 게이트는 **`en_done` 만으로 통과 허용**.
  2. 해당 step id를 `runtime_directories/phase0_translation_debt.yaml`에 부채로 기록.
  3. `translation-quality-team` 빌드 완료 직후, Tier 0이 부채 yaml을 순차 회수하며 *소급 번역*을 수행하고 status를 `bilingual_done`으로 보정. 부채 yaml 비-empty 상태에서 Phase 1 진입 시도 시 `validate_workflow.py --check-translation-debt` 차단(W12 보강).
  4. 본 예외 자체가 ADR 의무(번호 사전 발급).

### §9.2 단일 쓰기자 강제
- **v0.6 D-1**: 가드는 **PreToolUse `Edit|Write(**state.yaml)` 매처**로 이동(쓰기 *전* 차단). PostToolUse 위치는 잔존 격리망(2차 안전망)으로만 유지하며, 1차 차단 책임은 PreToolUse가 진다. 이는 "사후 격리는 이미 오염된 SOT를 진실로 받아들이는 후속 RLM 재독을 막지 못한다"는 결함(D1)의 직접 수정이다.
- 가드 알고리즘 (C-4 강건화 — 2nd-factor):
  1. **1st-factor**: 호출자 식별(`CLAUDE_AGENT_ID` env or stack inspection).
  2. **2nd-factor (v0.3 신규)**: `runtime_directories/tier0.lock` 파일 락 존재 + `pid` 매칭 + `ts` 60초 이내. 둘 중 하나라도 부재 시 exit 2.
  3. Tier 0 외 차단(exit 2 + 한국어 4줄).
  4. 복제 금지 키 화이트리스트 검사 (workflow.md Step 6 명세).
  5. 60초 윈도우 동시 갱신 검사 (B-π P-β).
  6. 위반 시 위반 diff를 `runtime_directories/sot-violations/{ts}.md`에 격리 + Tier 0 알림.
- **락 회수 동선**: stale lock(>90s heartbeat)은 §7 `/팀-lock-회수`로 1동작 회수.

### §9.3 RLM Pre-Action Verification (코드 강제 — v0.3 5줄 stamp)
- 모든 Tier 1·2 system prompt에 의무 삽입(English):
  ```
  Before any tool call that writes a file or spawns a sub-agent, you MUST:
  (a) Re-read the SOT file fresh THIS TURN — no memory.
  (b) Output one line: "RLM verified: read <path> @ <iso8601>".
  (c) Output one line: "Target output: <relative-path-in-my-assigned-folder>".
  (d) Confirm: "I do not write to state.yaml directly."
  (e) Output one line: "Intent: <user-instruction restated in <=25 English words>".  # C-1 v0.3 신규
  Without all five lines preceding any Write/Edit/Task tool call, the harness will reject your output.
  ```
- 검증 hook: `validate_rlm.py` (NEW)
  - **Stop/PostToolUse**: 마지막 응답 첫 5줄 stamp 부재 시 차단 (5줄 모두 필수).
  - **PreToolUse(Edit\|Write\|Task) (C-8 v0.3 신규)**: 단일 turn 내 N번째 도구 호출 시, 직전 stamp의 `ts`와 SOT mtime 비교 → **60초 초과 시 재독 강제** (재 stamp 요구). 단일 stamp가 다수 도구 호출에 stale하게 재사용되는 케이스 차단.
  - **위치 무결성 (v0.6 D-10)**: stamp 5줄은 *직전 도구 호출 메시지 블록 첫머리*에 위치해야 한다. 검사 알고리즘 — turn stream을 역순으로 스캔하여 (이전 도구 결과 → 어시스턴트 텍스트 → 도구 호출) 트리플렛 안에서 "어시스턴트 텍스트의 첫 5줄"이 stamp인지 확인. 트리플렛 외부 stamp는 stale로 간주 차단(exit 2).
  - IS-1 검사: Intent 1줄의 *원문 토큰 일치율*이 0.5 미만이거나 25단어 초과 시 차단.
  - **prefill 금지 (v0.6 D-2)**: stamp 4줄(a~d)을 자동 주입하는 모듈(예: 구 E-4 prefill 안)은 폐기. §17 E-4는 "verify-only"로 재정의(§17.2 갱신 참조).

### §9.4 Sub-agent Invocation Recording
- PreToolUse `Task` matcher → `record_subagent_invocation.py`
- 동작: 호출 메타(parent agent / target agent / step id / ts / payload sha) 추출 → **append-only 영속 저널** `runtime_directories/invocation-journal.ndjson` 끝에 한 줄 NDJSON 추가 → Tier 0이 다음 turn 시작 시 미처리 줄을 흡수해 SOT `state.yaml.steps.<id>.invocations`에 단일-쓰기자 경로로 기록.
- **v0.6 D-4 영속화**: 종전 "in-memory queue → Tier 0 다음 turn 처리"는 세션 종료/압축 시 기록 유실 위험(I3 위반). 저널 파일은 fsync로 atomic append하며, `restore_context.py`(parent inherit)에 미처리 NDJSON 흡수 단계를 추가한다(SessionStart 의무 동작).
- 본 hook은 *기록 전용* — 절대 차단하지 않음 (exit 0 always).

---

## §10. TDD Automation

### §10.1 RED-first contract
- 신규 `agents/`·`hooks/scripts/`·`skills/`·`commands/` 파일 생성 시도 → `tdd_red_first_check.py`가 *대응 테스트 파일 부재 시* exit 2.
- 매핑 규칙:
  | 신규 파일 | 요구 테스트 파일 |
  |---|---|
  | `agents/<name>.md` | `tests/agents/_test_<name>.py` (golden I/O) |
  | `hooks/scripts/<name>.py` | 동일 디렉터리 `_test_<name>.py` |
  | `skills/<name>/SKILL.md` | `skills/<name>/tests/golden/*.yaml` ≥ 3 |
  | `commands/<name>.md` | `tests/commands/_test_<name>.py` |
  | `.claude/scripts/fork_manager.py` (C-7) | `.claude/scripts/_test_fork_manager.py` |
  | `.claude/scripts/migrate_state_v01_to_v02.py` (C-6) | `tests/migrations/{empty,mid-step,post-translate}.yaml` 골든 3종 |

### §10.2 Coverage thresholds
- Hooks/validators: ≥ 90%
- Sub-agents (golden I/O): ≥ 85% scenario coverage (입력 fixture 기준)
- Skills (golden output): ≥ 3 회귀 케이스 + 신학 skill은 ≥ 20 (workflow.md Step 10)
- E2E: Phase 1 1주 사이클 1회 통과 의무 (Step 11)

### §10.3 Validators (모두 신규 또는 부모 확장)
- `validate_workflow.py` — W1-W11 + **W12 (bilingual gate, v0.2)** + `--check-teammate-conflict` + `--check-genome-inheritance` + `--check-promise-6-literal` + `--check-bilingual-gate` + `--step N` + **`--check-translation-debt` (v0.6 D-3)** + **`--check-merge-conflict` (v0.6 D-9: worktree 머지 시 base/A/B 3-way state.yaml diff에서 동일 키 다중 변경 검출 → exit 2)**
- `validate_pacs.py` (parent extend) — F/C/L + Ft/Ct/Nt 번역 차원
- `validate_traceability.py` — CT1-CT5
- `validate_translation.py` — T1-T9 + **KI-1** (en/ko 키 1:1 무결성, v0.2 신규) + **KI-2** (코드/식별자/SOT 키/기술 용어 영어 보존 검사)
- `validate_verification.py` — V1a-V1c
- `validate_domain_knowledge.py --domain theology` — DK1-DK7
- `validate_retry_budget.py` — RB1-RB3
- `validate_rlm.py` (NEW) — RLM stamp **5줄** (C-1) + PreToolUse 시간 해상도 검사 (C-8) + IS-1
- `validate_convention.py` (NEW) — §13.1 규약 + `--pattern per-edit-plan` (C-3)
- `validate_quality_gate.py` (NEW) — §13.3 임계값
- `validate_adr.py` (NEW) — §13.2 ADR 부재 차단
- `validate_owner_matrix.py` (NEW — C-2d) — `state.yaml.steps.<id>.owner_matrix` 스키마 + 파일별 owner 1:1
- `migrate_state_v01_to_v02.py` (NEW — C-6) — `schema_version` 승급 + 골든 3종 회귀

### §10.3.2 Quality Gate L0/L1/L1.5/L2 매핑 (D-5 v0.4 신규 — 부모 게놈 4계층 상속)

> 부모 AgenticWorkflow의 4계층 품질 게이트(`docs/protocols/quality-gates.md`)를 본 워크플로우 validator에 1:1 매핑. 절대 기준 1(품질) 보강.

| 계층 | 부모 정의 | 본 워크플로우 매핑 validator | 발동 시점 |
|---|---|---|---|
| **L0** Anti-Skip Guard | 단계 스킵·유실 방지 | `validate_workflow.py W1-W12` + `validate_pacs.py L0` | 매 Step PostToolUse |
| **L1** Verification Gate | 산출물 검증 14항목 | `validate_traceability.py CT1-5` + `validate_translation.py T1-9 + KI-1/KI-2` + `validate_domain_knowledge.py DK1-7` + `validate_verification.py V1a-c` | 매 Step 종료 직후 (translator team 합류 직전) |
| **L1.5** pACS Self-Rating | F/C/L 자기 평정 | `validate_pacs.py F/C/L + Ft/Ct/Nt` | L1 PASS 후 자동 |
| **L2** Calibration | 적대적 재평정 | `@reviewer` + `@fact-checker` 3중 적대 (R1-R5) + `validate_review.py` | Phase 종료 / 외부 발행 직전 |

**발동 순서 (validators-dag.md §10.3.1과 정합)**: L0 → L1 → L1.5 → L2. L2 실패는 ADR + 회수 카드. L0 실패는 즉시 차단.

**번역 차원 추가**: L1 단계에서 `translation-quality-team`(§4.5) 산출 PASS가 *L1 합격 조건의 일부*. 즉 `bilingual_done` 미달 step은 L1 미통과로 간주.

### §10.3.1 Validator DAG (C-9 v0.3 신규 — `validators-dag.md`)

> 별도 파일 `prompt/workflow-research/standards/validators-dag.md`에 정본. 본 문서는 요약.

**실행 순서 (pre-commit + per-Step PostToolUse 공통)**:
```
0. parent_hook_pin_audit (Setup only)
1. validate_rlm                 ← 가장 먼저 (다른 검증의 stamp 전제)
2. dual_sot_pairing_guard       ← SOT 쓰기 매처에서만
3. validate_owner_matrix        ← 2 PASS 후에만
4. validate_workflow (W1-W12)
5. validate_traceability (CT1-5)
6. validate_translation (T1-9 + KI-1/KI-2)
7. validate_convention (advisory→strict)
8. validate_pacs / validate_domain_knowledge / validate_verification (병렬 가능)
9. validate_retry_budget
10. validate_quality_gate
11. adr_trigger_audit            ← 마지막 (선행 검증의 결정 변경 사항 기반 ADR 부재 검출)
```

**금지 의존**:
- 순환 의존 금지 (1 ↔ 2, 4 ↔ 11 등 양방향 호출 금지).
- step 7 (`validate_convention`)이 step 4·5의 산출 메타를 *수정*하는 행위 금지 (read-only).
- 실패 격리: 1·2·3 실패 시 4–11 미실행 (early-exit). 4–11 중 실패는 *해당 검증만 차단*하고 나머지 진행.

### §10.4 CI 트리거
- 로컬 pre-commit hook (Setup `init`이 설치): pytest + 모든 validate_*.py 실행. 실패 시 commit 차단.
- 로컬-only — 클라우드 CI 의존 없음 (절대 기준 3 로컬 실행 전제).

---

## §11. Fallback Paths (10종)

| # | Failure | Detection | Chain |
|---|---|---|---|
| 1 | Teammate 무응답 (>30s) | `heartbeat_check.py` (v0.6 D-7 신설 — `runtime_directories/heartbeat/<task-id>.json` ts 비교) | **(v0.6 D-8)** 동일 모델·동일 프롬프트 retry 1회 → 직렬 단일 강등 → 한국어 4줄 escalate. **모델 승격(Sonnet→Opus)은 별도 ADR 트리거 결정 카드로 분리**(§16.3 비용 무관 원칙 준수). |
| 2 | Team 조율 붕괴 (BL × BL ≥ 3건) | Lead 충돌 매트릭스 | 즉시 해체 → `@gate-resolver` 직렬 강등 + 사용자 일괄 결정 카드 |
| 3 | Orchestrator 컨텍스트 초과 | Stop hook + PreCompact | save_context → SessionStart 시 RLM + last_user_card 복원 |
| 4 | SOT 동시 쓰기 시도 | dual_sot_pairing_guard exit 2 | 위반자 격리 → Tier 0 회복 권한 |
| 5 | didim-bridge 실패 | B-1 재검증 + RB | RB1-RB3 → 발행 차단 + 캐시 OFF |
| 6 | 신학 필터 1차 FAIL | `@theological-reviewer` | 결정적 2차 분기 → FAIL 확정 시 D-2 카드 |
| 7 | Self-lock stale | heartbeat > 90s | crash 마커 → `/팀-lock-회수` |
| 8 | Fork merge 실패 (#2 #3) | git conflict OR validator FAIL | 자동 폐기 + 본 트리 무손상 + diff 보존 + "자기 진화 미적용" 카드 |
| 9 | 외부 인증 만료 | 30s × 3 백오프 | 발행 차단 + 최후 알림 (Telegram + macOS Notification 이중) |
| 10 | 모든 fallback 소진 | escalation chain 끝 | **Safe-Mode**: 외부 발행 OFF + Phase 0 강등 + `/팀-회복` 1동작 카드 + FR-22 = "중단". **(v0.6 D-12 역방향 FSM)** 회복 경로는 `safe_mode → recovery_pending → phase1_resume`로 명시. `/팀-회복` 카드 통과 시 `recovery_pending` 진입, `validate_workflow.py W1-W12 + L0` 전수 PASS 후에만 `phase1_resume`. E-8 FSM 표에 추가. |

---

## §12. 영어 운용 경계

| 영역 | 언어 | 강제 hook |
|---|---|---|
| agent/skill/hook/command frontmatter | English | `validate_convention.py` |
| system prompt body | English | 동일 |
| 코드·주석·테스트 식별자 | English | 동일 |
| 사용자 가시 한국어 라벨 (i18n yaml) | Korean | `validate_translation.py` |
| C-3 4줄 에러 카드 | Korean | `validate_translation.py --pattern c3-4line` |
| 결정 카드(C-α 4줄 + 자유 메모) | Korean | 동일 |
| 진척 라인(0회차·M1·M3 입장 연출 C-4) | Korean | 동일 |
| 면책 라인 C-4 | Korean (정본 1줄 고정) | 동일 |
| 내부 ID 노출 검사 | (영문 식별자 사용자 가시 차단) | `output_internal_id_filter.py` |
| **모든 step 산출물 (v0.2)** | English 원본 + Korean 번역 쌍 | `validate_workflow.py --check-bilingual-gate` (W12) + `validate_translation.py` (KI-1/KI-2) |

### §12.1 Glossary 운용 프로토콜 (D-6 v0.4 신규)

- **위치 (고정)**: `translations/glossary.yaml` (저장소 루트). 부모 게놈 상속.
- **읽기 권한**: `@translator-ko`, `@back-translator-en`, `@glossary-validator`, `validate_translation.py` 모두 매 호출 fresh read (RLM 적용).
- **쓰기 권한**: **Tier 0 단독**. 자동 쓰기 금지.
- **신규 용어 추가 절차**:
  1. `@glossary-validator` 또는 `@translator-ko`가 신규 용어 후보 발견 → `outputs.translation_proposals[]`에 append (제안만).
  2. Tier 0이 다음 결정 카드(한국어 4줄)에 후보 노출 → 사용자 승인 시 ADR 생성(§13.2).
  3. ADR `accepted` 후 Tier 0이 `glossary.yaml`에 추가 + `state.yaml.invocations[].glossary_rev`에 새 sha 기록.
- **검증**: `validate_translation.py --check-glossary-rev` — 모든 step의 `invocations[].glossary_rev`가 *해당 step 종료 시점의 glossary HEAD sha*와 일치하는지 검증. 불일치 시 exit 2 (오래된 glossary로 번역된 산출물 차단).
- **하위 호환**: v0.3까지의 step은 `glossary_rev: legacy` 허용. v0.4 이후 신규 step은 sha 필수.
- **v0.6 D-11 step-freeze**: 각 step 진입 시점에 Tier 0이 현재 glossary HEAD sha를 SOT `state.yaml.steps.<id>.glossary_rev_frozen`에 *고정*한다. 해당 step 진행 중 사전 갱신이 발생하면:
  1. 진행 중 step은 frozen sha를 계속 사용(encode/decode 정합 보장 — D-11 race 차단).
  2. 사전 갱신 자체는 ADR 트리거(§13.2).
  3. 신규 sha는 *다음 step 진입 시*부터 freeze 대상. 현재 step의 산출물이 신규 용어를 포함해 추가 번역 필요 시 `/팀-번역재시도`로 명시 회수.
  4. `validate_translation.py --check-glossary-rev`는 `invocations[].glossary_rev == steps.<id>.glossary_rev_frozen` 일치를 추가 검증.

**v0.2 변경 (추가 절대 원칙 반영)**:
- `@translator-ko` 호출은 **모든 step 종료 직후 자동** (Tier 0 트리거). v0.1의 "Translation: 표기 한정"은 deprecated.
- 부모 게놈 `translations/glossary.yaml` 상속. 신규 용어는 ADR 방식으로 사용자 승인 후 확정(자동 쓰기 금지 — Tier 0 경유).
- 사용자 입력이 한국어인 경우 Tier 0이 즉시 영어 변환, 내부 처리는 영어로 진행 (원문은 `inputs.user.ko_original`에 보존).

---

## §13. 평가 기준 3종 — 작성 계획

> 절대 기준 1 보강: 정돈된 평가 기준 = 품질의 일부. **작성 시점은 모두 Step 7.5 직후, Phase 0 첫 코드 한 줄 전**. 갱신은 사용자 명시 결정 카드(`/팀-규약갱신` 또는 ADR)로만.

### §13.1 `code-convention.md`
- 위치: `prompt/workflow-research/standards/code-convention.md` → 구현 시 `Claude_skills/AI_churchteam/.claude/standards/code-convention.md` 동기 복제
- 작성 시점: Step 7.5 직후 1차, Phase 1 진입 직전 사용자 승인
- 내용 (English):
  - File naming (kebab-case `.md`, snake_case `.py`, PascalCase agent IDs in their `.md` `name:` field, kebab-case Korean labels in `i18n/ko.yaml`)
  - Imports order (stdlib → 3rd-party → local)
  - Error envelope (internal logs English, user-visible Korean C-3 4-line)
  - Size limits: file ≤ 800 lines, function ≤ 50 lines, nesting ≤ 4
  - Type hints mandatory (Python 3.12+ `from __future__ import annotations`)
  - No emoji in code or comments
  - Korean only inside `i18n/*.yaml` strings
  - RLM stamp position (first 4 lines of any tool-using turn, sub-agents)
  - SOT write protocol reference (§9)
  - Hook exit code semantics (0 pass / 1 advisory / 2 block)
- 검증: `validate_convention.py --advisory` (PostToolUse) — 위반 시 exit 1(경고). Phase 1 진입 후 `--strict`로 승격 (exit 2).

#### §13.1.1 Per-Edit Change Plan (C-3 v0.3 신규 — 코드 변경 3원칙 중 "변경 설계" 마이크로 강제)

모든 Edit/Write 도구 호출 직전, agent는 영어로 다음 5항을 출력해야 한다 (RLM 5줄 stamp 다음 블록):

```
Per-Edit Change Plan:
1) Target file: <relative-path>
2) Direct callers/callees (<=5 each, from impact_scan.py output)
3) Co-change set: <DTO|schema|test|doc paths>
4) Risk: shotgun | local | additive
5) Rollback note: <one line>
```

- 검증: `validate_convention.py --pattern per-edit-plan`
  - **Phase 0**: advisory (exit 1). 누락 시 경고만.
  - **Phase 1 진입 후**: strict (exit 2). 누락 시 차단.
- `Risk: shotgun` 표시 시 자동으로 ADR 트리거 (§13.2 + C-10) — 광범위 파급 변경은 ADR 의무.
- 5항 정보는 `state.yaml.steps.<id>.edit_plans[]`에 누적 (Tier 0 단일 쓰기 경유).

### §13.2 `architectural-decision-records.md` (ADR)
- 위치: `prompt/workflow-research/standards/adr/ADR-{NNN}-{slug}.md` + 인덱스 `architectural-decision-records.md`
- 작성 시점:
  - Step 3 모든 사용자 결정 → ADR 자동 생성 (Tier 0)
  - Step 7 진입 허가 카드 → ADR
  - §9.4 자율 금지 7행 변경 시도 매번 → ADR
  - Phase 진입 매번 → ADR
- 포맷 (Michael Nygard 5-section, English):
  ```
  # ADR-{NNN}: <title>
  ## Status: proposed | accepted | superseded by ADR-NNN
  ## Context
  ## Decision
  ## Consequences
  ## References
    - PRD §X.Y, idea §Z, BL-ID, pastoral-decision-logs/<file>
  ```
- 갱신 권한: Tier 0만 작성. Supersede도 ADR로 기록.
- 검증: `validate_adr.py` — Phase 진입 직전 ADR 부재 시 exit 2.

### §13.3 `code-quality-guide.md`
- 위치: `prompt/workflow-research/standards/code-quality-guide.md`
- 작성 시점: Step 7.5 직후 (code-convention과 동시)
- 내용 (English):
  - TDD Contract (RED-first, §10)
  - Coverage thresholds (§10.2)
  - pACS dimensions F/C/L thresholds (GREEN ≥ 70 / YELLOW 50–69 / RED < 50)
  - Adversarial review pass criteria (3중 통과 의무)
  - Anti-patterns: silent failure / mutation / mock-the-database / `--no-verify` / autoinstall without user card
  - Korean error envelope schema (C-3 4-line literal template)
  - RLM stamp schema
  - SOT write protocol cross-link
- 검증: `validate_quality_gate.py` — 모든 Step Post-processing 자동 실행.

### §13.4 3종 책임 분담
```
code-convention.md   = HOW (style)
ADR                  = WHY (decision)
code-quality-guide   = WHAT (thresholds)
```

---

## §14. Build Order (Phase 0 → 1 → 2)

> "지연 빌드"가 핵심. Phase 0은 *최소 골격*만, Phase 1은 *시연 가능 표면*, Phase 2는 *경화*.

| Phase | Includes (코드 작성 대상) | TDD gate |
|---|---|---|
| **Pre-Phase 0** (Step 7.5) | §13 평가 기준 3종 + 신규 hook (v0.6 누계 16종 — D-7 heartbeat 쌍 포함) RED-only 테스트 작성 + `validators-dag.md` 정본화 + `migrate_state_v01_to_v02.py` 골든 3종. **(v0.6 D-5)** 본 단계 RED 테스트의 *실행 주체는 Tier 0(현 세션) 직접*이며, `setup_init_churchteam.py --pre-phase0-red` 단일 진입점이 pytest 일괄 실행을 책임진다. Tier 1 orchestrator 미존재 시점이므로 위임 불가. | RED 통과 (구현 0) |
| **Phase 0** (Step 8–9) | `setup_init_churchteam.py` + `bootstrap.sh` (BL-5 시나리오 9a/b/c 중 채택) + `inheritance-manifest.json` 생성 + `commands/팀.md` + child `state.yaml` + Tier 0/1 orchestrator system prompts + RLM hook + record_invocation hook | 모든 hook GREEN + `validate_workflow.py --check-genome-inheritance` PASS |
| **Phase 1** (Step 10–12) | 3–5 pastoral agents + `theology_filter_dual.py` + `@theological-reviewer` + 3-Door + FR-22 + `@didim-bridge` + spof-recovery + `output_internal_id_filter.py` + `pastoral_log_pii_mask.py` | 1주 사이클 시연 PASS + 신학 시드 ≥ 20 |
| **Phase 2** (Step 13–14) | `self_evolution_gate.py` + 7 추가 부교역자 + M3 debate + disaster-recovery (3 시나리오) | 자기 진화 fork merge PASS + DR 시뮬레이션 PASS |
| **Steady state** (Step 15+) | 회중 노출, 분기별 DR rehearsal, ADR 누적 | `/팀-회중허가` PASS |

각 Phase 진입은 ADR 의무. 각 Phase 종료 시 `/팀-진입허가 --next-phase` 사용자 카드 통과.

---

## §15. 모호 지점 (다음 라운드 결정)

> 본 문서가 *다루지 않은 것* — 코드 진입 전 합의 필수.

1. **BL-5 채택 시나리오 (9a/9b/9c)** — Phase 0 부트스트랩 진입점. 본 문서는 3 후보 모두 코드 형태 명시 안 함.
2. **BL-3 Phase 1 active roster** — 3직 vs 5직 결정 + didim 7 매핑 정확한 N:M.
3. **BL-(vi) D-3 Phase 분기** — Phase 1 도입 vs Phase 2 도입. `phase1_minimum_set.decided_set` 미결.
4. **BL-2 RC 채택** — RC-α/β/γ 중 1. didim 입력 주입 활성 분기 결정.
5. **시연 주차 ID** — `sermon-plan-2026.json`의 어느 주차로 Step 11 시연.
6. **외부 백업 채널** — pastoral-decision-logs · 부모 게놈 백업 위치(Git private vs iCloud vs 외장).
7. **Telegram chat_id 화이트리스트 초기 셋** — `.env` 입력 시점.
8. **신학 시드 출처** — 부모 게놈 `prompt/ai_pastoral_prompts/` 실재 케이스 ≥ 20 큐레이션 가능 여부.
9. ~~**`@translator` 실행 boundary**~~ — **v0.2에서 결정**: 매 step 종료 직후 자동 (`@translator-ko`). §3.3 / §9.1.1 / §12 반영 완료.
10. ~~**fork manager 구현 위치**~~ — **v0.3에서 해소 (C-7)**: §6 `fork_manager_audit.py` + §10.1 매핑 추가. 본격 함수 4종 명세는 §8 그대로 (구현 단계에서 RED-first 테스트로 확정).
11. **Safe-Mode 임계값 정확값** — §11 #10 추상.
12. **Tier 1 분리 vs 통합** — 3 Phase Orchestrator 분리 (현재) vs 단일 통합.
13. **사용자 가시 호칭 한국어 사전** — `i18n/ko.yaml`의 12직 호칭 정본 부재.
14. ~~**ADR 자동 생성 트리거 정확 매처**~~ — **v0.3에서 해소 (C-10)**: §6 `adr_trigger_audit.py` 매처 행 추가 (state.yaml + phase + decision_card.signed + 자율 금지 7행).
15. **E-2 임베딩 2차 채택 ADR 트리거 시점** (v0.5 신규) — `score_translation_quality.py`의 임베딩 cosine 2차 활성은 §27 line 27 "클라우드 의존 0" 원칙과 충돌. v0.5 기본은 rouge-L 1차만으로 GREEN. 임베딩 채택 결정 카드 발행 주차 미정.

---

## §16. Agent Selection Protocol (D-4 v0.4 신규 — `agent-selection.md`)

> 위치: `prompt/workflow-research/standards/agent-selection.md` (정본). 본 섹션은 요약.
>
> **선택 단일축 = 품질**. 토큰·속도·구현 편의는 명시적으로 *기각*.

### §16.1 결정 매트릭스

| 조건 | 선택 | 근거 |
|---|---|---|
| 다관점 검증 필요 (설계·신학·번역 품질·적대적 리뷰) | **agent-team** | 독립 컨텍스트 100% 집중 + 3중 교차 비판 → 품질 ↑ |
| 단일 책임·결정론적 변환 (데이터 정제·매처 검증·정적 분석) | **sub-agent** | team 오버헤드가 품질 향상에 기여 0 |
| 충돌 가능성 있는 병렬 쓰기 (worktree 필요) | **agent-team + worktree isolation** | 산출 격리 + 충돌 매트릭스 |
| 사용자 결정 카드 발행 / SOT 단일 쓰기 | **Tier 0 직접** (sub-agent도 team도 아님) | I1·I3 불변식 |

### §16.2 본 워크플로우 적용

| 영역 | 선택 | 이유 |
|---|---|---|
| Step 2 4 게이트 결의 | team (`entry-gate-resolution-team`) | 4 BL 다관점 + 충돌 가능 |
| Step 5+6 설계 마무리 | team (`design-finalization-team`) | 팀 구조 ↔ 브릿지 정합 교차 검토 |
| Step 10 Phase 1 빌드 | team (`phase1-build-team`) | 4축 독립 병렬 + owner 매트릭스 |
| Step 13 진화 | team (`phase2-hardening-team`) + worktree | 자기 진화 = 적대 검토 의무 |
| **모든 step 종료 후 번역 (D-2)** | team (`translation-quality-team`) | 3중 적대 = 품질 절대 |
| 신학 필터 (`@theological-reviewer`) | sub-agent | 도메인 단일 책임 + 결정론적 분기 |
| `record_subagent_invocation` | hook (sub-agent 아님) | 기록 전용 |
| `@didim-bridge` (weekly-works 다리) | sub-agent | 단일 책임 conduit |
| `@translator-ko` 단독 (deprecated) | ~~sub-agent~~ → **team으로 승격(D-2)** | 품질 기준 재평가 결과 |

### §16.3 토큰·속도 기준 명시 배제

선택 시 다음 사유는 **무효**:
- "team은 토큰 3배 든다" → 절대 기준 1에 따라 무효.
- "sub-agent가 빠르다" → 무효.
- "구현이 간단하다" → 무효.

선택 변경은 ADR(§13.2) 의무. 본 §16.2 매핑 변경 시 ADR 트리거.

---

## §17. Python Determinism Layer (E-1 ~ E-10, v0.5 신규)

> **목적**: 세 축(엄밀·반복·할루) 모두 높은 회로를 LLM에서 Python으로 이동해 할루시네이션을 *원천 봉쇄*. 절대 기준 1(품질 우선) 강화.
> **불변식 보존**: SOT 단일 쓰기자(I1)·RLM(I2)·invocation 기록(I3)은 변하지 않음. 모든 신규 모듈은 *Tier 0 권한 내부* 또는 *PreToolUse hook* 위치. Teammate 자율 SOT 쓰기 권한 부여 절대 금지.
> **선택 단일축 = 품질** (§16). 토큰·구현 편의 기각.

### §17.1 모듈 카탈로그 (10건)

| ID | 모듈 | 위치 | 트리거 | 대체 대상(LLM 회로) | TDD 골든 |
|---|---|---|---|---|---|
| **E-1** | `glossary_placeholder_codec.py` | `Claude_skills/AI_churchteam/.claude/scripts/` | PreToolUse `Task(@translator-ko)` + PostToolUse 짝 (decode) | 번역 모델의 식별자/용어 자유 변형 | ≥ 5 (encode/decode 왕복 정합) |
| **E-2** | `score_translation_quality.py` | 동상 | `translation-quality-team` Lead 호출 | 의미 유사도 LLM self-judge | ≥ 5 (rouge-L 골든) |
| **E-3** | `format_korean_card.py` | 동상 + skill `health-dashboard` 공용 | C-3 4줄·결정 카드·면책 라인 *생성* 시점 | LLM이 4줄 정본 자유 작성 | ≥ 6 (4줄 정본 × 카드 종류) |
| **E-4** | `rlm_stamp_verify.py` (v0.6 D-2 재정의 — 종전 `rlm_stamp_prefill.py` *폐기*) | `hooks/scripts/` | PreToolUse `Task` (sub-agent spawn) + PostToolUse 짝 | sub-agent의 RLM 4줄 *자기 출력*에 대한 *증거 검사*: (1) 직전 5s 이내 SOT read syscall 존재, (2) stamp `path` 인자가 실제 read 대상과 일치, (3) `ts`가 read syscall ts 이후 단조 증가, (4) (a)~(d) 텍스트는 sub-agent 출력에서만 수집(자동 주입 금지) | ≥ 5 (read syscall 검증 케이스 + 위조 stamp 차단 골든) |
| **E-5** | `merge_sot_proposals.py` | `Claude_skills/AI_churchteam/.claude/scripts/` | Tier 0이 Lead 통합 직전 호출 | LLM 머지 (필드 누락·키 변형 위험) | ≥ 5 (JSON-Patch + 충돌) |
| **E-6** | `adr_scaffold.py` | 동상 | Step 3·7·Phase 진입·자율 금지 7행 변경 시 | LLM 자유 ADR 작성 (번호 충돌·Status FSM 위반) | ≥ 4 (발번 + supersede) |
| **E-7** | `pastoral_honorific_inject.py` | `hooks/scripts/` | PreToolUse `Task(<pastoral-role>)` | LLM 호칭 메모리 의존 (RLM 위반) | ≥ 3 (12직 호칭) |
| **E-8** | `state_machine.py` | `Claude_skills/AI_churchteam/.claude/scripts/` | `validate_workflow.py W12` 내부 호출 | v0.4까지 분산된 전이 검증 | ≥ 6 (모든 전이/금지) |
| **E-9** | `validate_pacs.py::bucket_score()` | 기존 모듈 함수 추가 | `validate_pacs.py` 호출 시 | LLM 임계 해석 (70/50) | ≥ 4 (경계값) |
| **E-10** | `generate_inheritance_manifest.py` | `Claude_skills/AI_churchteam/.claude/scripts/` | Phase 0 `setup_init_churchteam.py` 내부 | LLM이 manifest 자유 생성 | ≥ 3 (sha 핀 정합) |

모두 RED-first(§10.1). coverage ≥ 90% (§10.2).

### §17.2 LLM ↔ Python 책임 경계 (보존 원칙)

| 영역 | LLM 유지 | Python 이동 |
|---|---|---|
| 번역 본문 | `@translator-ko` MT 자체 | 용어 placeholder 치환·복원 (E-1) |
| 번역 품질 | (없음 — 판정자도 Python으로) | 유사도 점수·임계 판정 (E-2) |
| RLM stamp | (a)~(e) sub-agent 자기 출력 (자동 주입 금지) | E-4는 *증거 검사 only* — read syscall 추적 + ts 단조성 + path 일치 (v0.6 D-2) |
| ADR | Context/Decision/Consequences 본문 | 발번·5섹션 빈 템플릿·Status FSM (E-6) |
| 결정 카드 | 슬롯 내용(현재상태·다음행동·위험·회수경로) | 4줄 정본 합성 (E-3) |
| SOT 머지 | 수락/거부 결정 | JSON-Patch 합성 (E-5) |
| 부교역자 호칭 | 본문 출력 | system prompt 내 호칭 substitute (E-7) |
| state 전이 | (없음 — 전이는 결정성) | FSM (E-8) |
| pACS 평정 | F/C/L 점수 산출 | 버킷팅 (E-9) |
| 부모 manifest | (없음) | 경로 walk + sha (E-10) |

**경계선 원칙**: SOT/식별자/정본 텍스트/숫자 임계/FSM = Python. 사용자 의사결정 본문/창의 추론/도메인 판단 = LLM 유지.

### §17.3 도입 게이트 (CCP 비례성 — 10건 일괄 금지)

| 그룹 | 모듈 | 도입 시점 | 게이트 |
|---|---|---|---|
| **즉시 (Tier-A)** | E-4·E-7 | 본 문서 승인 직후 | RED-first TDD 골든 PASS만 |
| **ADR 후 (Tier-B)** | E-1·E-6·E-8·E-9·E-10 | 각 모듈 ADR `accepted` 후 | ADR + RED-first |
| **결정 카드 후 (Tier-C)** | E-2·E-3·E-5 | `/팀-결정` 카드 + ADR | 결정 카드 + ADR + RED-first + 1주 advisory 운용 |

**Tier-C 추가 조건**:
- E-2: 임베딩 2차 채택 시 §27 클라우드 의존 충돌 ADR 별도 (R1).
- E-3: `i18n/ko.yaml` 정본 4줄 사용자 승인 후에만.
- E-5: `dual_sot_pairing_guard.py` 1st-factor가 Python 머지기 호출 시점에서도 동일하게 작동하는지 회귀 골든 의무.

### §17.4 SOT/RLM 보존 재확인

- **I1 (단일 쓰기자)**: E-1·E-5·E-6·E-8·E-10은 *제안만 생산* — SOT 쓰기는 Tier 0이 기존 경로로 처리. PreToolUse `Edit|Write(state.yaml)`의 `dual_sot_pairing_guard.py`(§9.2) 변동 없음.
- **I2 (RLM stamp)**: E-4(v0.6 재정의)는 sub-agent의 *자기 stamp*에 대한 *증거 검사*만 수행 — 자동 주입 금지(D-2). E-7은 호칭 substitute에 한정. `validate_rlm.py`(C-1·C-8) + 위치 무결성(D-10)이 1차 안전, E-4 evidence 검사가 2차 안전.
- **I3 (invocation 기록)**: E-4가 prefill하는 stamp는 `record_subagent_invocation.py`가 기록하는 invocation과 중복 아님. 두 hook 서로 의존 없음(§6.1 매트릭스).
- **I4 (timeout fallback)**: E-2가 외부 임베딩 호출 시 Rule 2 30s 멘탈 타임아웃 적용. rouge-L 1차는 로컬 결정성이라 timeout 무관.

### §17.5 손실 분석 (반대 의견 보존)

| 손실 | 모듈 | 평가 |
|---|---|---|
| 자연 번역 부드러움 일부 손상 | E-1 | 식별자 보존 절대 우선 — 수용 |
| 정본 4줄 표현 다양성 제거 | E-3 | 예측 가능성 ≥ 표현 다양성 — 수용 |
| sub-agent 자기 검사 효과 약간 감소 | E-4 | hook 검증 이중 안전망으로 보전 |
| 외부 임베딩 비용·클라우드 의존 | E-2 | rouge-L 1차로 회피, 임베딩은 ADR 필수 |
| Tier 0 권한 위치 한 단계 추상화 | E-5 | 1st-factor 회귀 골든 의무로 보전 |
| Python silent bug 신규 표면 | 전체 | TDD coverage ≥ 90% + 골든 픽스처로 보전 |

### §17.6 자율 금지 7행과의 정합

§17 모듈 도입 자체는 자율 금지 7행에 해당하지 않음. 그러나 다음은 ADR 의무:
- E-3 정본 4줄 *변경*: Korean 정본 텍스트 변경 = 사용자 가시 톤 변경.
- E-6 Status enum *변경*: ADR FSM 자체 변경.
- E-8 status enum 추가: workflow.md §SOT 표 변경.

위 3건은 모두 §13.2 ADR 트리거 매처에 이미 포함(C-10 `adr_trigger_audit.py`).

---

## §18. v0.6 결함 수정 통합 인덱스 (설계 결함 보고서 D1~D12 반영)

> 본 섹션은 v0.6 변경의 *단일 인덱스*다. 본문 변경 위치는 각 항목에 명시. 우선순위는 보고서의 심각도(치명/위험)와 동일.

| ID | 결함 요약 | 반영 위치 | 위반했던 불변식/원칙 | 검증 |
|---|---|---|---|---|
| **D1** 치명 | SOT 가드 사후 검증 → 사전 차단 | §6 hook 표(PreToolUse 이동) · §9.2 첫 줄 | I1 단일 쓰기자 | `_test_dual_sot_pairing_guard.py` PreToolUse 골든 |
| **D2** 치명 | RLM stamp 자동 주입 폐기 → 증거 검사 | §17.1 E-4 행 · §17.2 RLM stamp 행 · §17.4 I2 · §9.3 prefill 금지 | I2 RLM 재독 | E-4 골든 ≥5 (위조 stamp 차단) |
| **D3** 치명 | Phase 0 자기-부트스트랩 예외 + 부채 회수 | §9.1.1 끝 (4항목) · §10.3 `--check-translation-debt` | 게이트 자기-차단 / 절대 기준 1 | `validate_workflow.py --check-translation-debt` |
| **D4** 치명 | invocation in-memory queue → NDJSON 영속 저널 | §9.4 (전면 갱신) · §6 (translator_trigger 매처 갱신) | I3 invocation 기록 | restore_context 흡수 회귀 골든 |
| **D5** 위험 | Pre-Phase 0 RED 실행 주체 = Tier 0 직접 | §14 Pre-Phase 0 행 | 책임 부재 | `setup_init --pre-phase0-red` |
| **D6** 위험 | translator 재귀 트리거 차단 | §6 translator_trigger 매처 (`invocations[-1].agent != 'translator-ko'`) | 폭주 방지 | 재귀 케이스 골든 |
| **D7** 위험 | Heartbeat hook 쌍 신설 | §6 (heartbeat_emit + heartbeat_check) | §11 #1 감지 인프라 | 30s 시뮬레이션 골든 |
| **D8** 위험 | 폴백 사다리에서 모델 승격 분리 | §11 #1 행 | §16.3 비용 무관 원칙 | ADR 트리거 매처 |
| **D9** 위험 | Worktree 머지 충돌 검증자 | §10.3 `validate_workflow.py --check-merge-conflict` | §8 fork 무결성 | 3-way diff 골든 |
| **D10** 위험 | RLM stamp *위치* 무결성 | §9.3 (직전 도구 호출 트리플렛 검사) | I2 stale 재사용 차단 | turn stream 위치 골든 |
| **D11** 위험 | Glossary `step-freeze` | §12.1 끝 (4항목) | E-1 encode/decode 정합 | `--check-glossary-rev` 보강 |
| **D12** 위험 | Safe-Mode 역방향 FSM | §11 #10 행 (E-8 FSM에 `recovery_pending → phase1_resume`) | 회복 경로 부재 | E-8 골든 보강 |

**보존 재확인 (v0.6 기준)**:
- I1(단일 쓰기자): D1로 사전 차단 강화. SOT 직접 쓰기 경로는 여전히 Tier 0 단독.
- I2(RLM): D2 prefill 폐기 + D10 위치 무결성으로 *형식만 통과*하던 우회로 전부 봉쇄.
- I3(invocation 기록): D4 영속 저널로 세션 종료/압축 시 유실 0.
- 절대 기준 1(품질): D8로 비용 사유 폴백 사다리 제거. 모델 승격은 *명시적 결정*으로 격상.
- 절대 기준 3(CCP): 본 v0.6 변경 자체가 보고서 → 분석 → 외과적 수정의 절차로 산출 — 본 §18이 그 추적 인덱스다.

**파급 영역(다음 라운드 점검 필요)**:
- §6.1 hook 의존 매트릭스: D7 heartbeat 쌍의 의존 행 추가, D1 PreToolUse 이동에 따른 dual_sot_pairing_guard 행 시점 갱신이 필요 — 본 v0.6은 §18 인덱스로 의도만 명시, 표 구조 갱신은 다음 라운드.
- §13.3 quality-gate 임계값: D2/D10 강화로 RLM 위반 검출률이 변동 가능 — 캘리브레이션 표 갱신 후속.
- §16.2 매핑: D8로 모델 승격 결정이 ADR 트리거에 편입됨에 따라 `Step 13 진화` 행에 *모델 승격 ADR* 부주 추가 필요(다음 라운드).

---

## §19. v0.7 PRD 적대적 성찰 반영 통합 인덱스 (P1~P7)

> 본 섹션은 v0.7 변경의 *단일 인덱스*. PRD v0.5에 대한 적대적 A/B/C 성찰의 "방어 불가 7건"을 본 인프라 빌드 청사진에 외과적으로 반영. PRD 본문 수정은 별도 승인 의제(§19.4)이며, 본 §19는 *워크플로우 측 대응*만 다룬다.
>
> **인용 성찰 보고서 (P6 컨벤션)**: `prompt/workflow-research/reflections/2026-05-05_prd-v05-adversarial-ABC.md` (갱신일 2026-05-05). 보고서 부재 또는 path 변경 시 본 §19 무효 — `validate_convention.py --pattern changelog-pointer` 보강 검증.

| ID | PRD 결함 (출처) | 본 문서 반영 위치 | 검증 모듈 | 도입 게이트 |
|---|---|---|---|---|
| **P1** A-α | PRD §11.5 "정의상 직교" 강변 → 런타임 검증으로 격하 | §6 hook 표(`dual_sot_orthogonality_probe.py` 신설), §11.4 자가 검증 신호 ⑥ 보강 | `_test_orthogonality_probe.py` ≥ 5 | Tier-A 즉시 |
| **P2** A-γ | PRD §9.4 자기 진화 자기-감시 → 외부 관찰자(pre-commit) 분리 | §3.2 `@phase2-evolution-builder` 산출물 `self_evolution_gate.py`의 호출 위치를 git pre-commit(§10.4)에 강제, 동일 세션 내 호출 금지 | pre-commit 회귀 골든 + ADR | Tier-B (ADR 후) |
| **P3** A-δ | PRD §11.2 번역 서브에이전트 fallback 부재 | §11 새 행 #11 (translation-quality-team 전체 실패), §11.4 자가 검증 신호 ⑦ "번역 보류" 추가 | `_test_translator_team_total_failure.py` | Tier-B (ADR 후) |
| **P4** B-α | PRD FR-25 자기 진화 *메커니즘* P0 → P1 강등 (원칙은 P0 유지) | §14 Phase 표 — 사전 게이트 약속 메커니즘은 Phase 2(§14 Phase 2 행)에 명시, Phase 1은 *원칙 노출만* | `validate_workflow.py --check-fr25-phase` | Tier-C (결정 카드) |
| **P5** B-γ | PRD FR-21 M2/M3 P0 → P1 (Phase 2) | §7 `/팀` 행 분기 도입 시점 주 + §14 Phase 1 = M1 단일 / Phase 2 = M2/M3 추가 | `_test_command_team_root.py` Phase 분기 골든 | Tier-C (결정 카드) |
| **P6** C-α | 변경 이력 → 성찰 보고서 포인터 의무 | 본 문서 머리 changelog 컨벤션 강화(인용 보고서 path + 갱신일 동반). 본 v0.7 헤더가 첫 적용 사례 | `validate_convention.py --pattern changelog-pointer` | Tier-D (컨벤션, 즉시) |
| **P7** C-γ | didim 게놈 버전 pinning 부재 | §6 `parent_hook_pin_audit.py` → `genome_pin_audit.py`로 확장(parent + didim sha/태그 핀), §11.4 ⑥ 신호 = *도달성 + 버전 식별* | `_test_genome_pin_audit_didim.py` | Tier-A 즉시 |

### §19.1 신규/확장 모듈 명세 (스펙만 — 실제 코드 미구현)

- **`dual_sot_orthogonality_probe.py`** (P1): PreToolUse 매처 `Edit|Write(**state.yaml)` ∪ `Edit|Write(**status.md)`. 동일 cycle id에 대해 churchTeam SOT와 didim SOT 양측 갱신을 60s 윈도우 내 탐지 시 exit 2 + 한국어 4줄 + `runtime_directories/sot-orthogonality-violations/{ts}.md` 격리. PRD §11.5 "직교 by definition" 강변을 *런타임 검증*으로 격하. 기존 `dual_sot_pairing_guard.py`(§9.2)는 단일 SOT 단일 쓰기자 강제, 본 probe는 *교차 SOT 정합* 강제 — 두 hook은 §6.1 매트릭스에서 비순환 의존(probe → pairing).
- **`genome_pin_audit.py`** (P7, 확장): 기존 `parent_hook_pin_audit.py`를 *parent + didim* 양 게놈 sha256/태그 핀 검사로 확장. didim 게놈 위치는 `roster.yaml.didim_genome_path` 단일 출처(PRD §11.1.a 주소 안정성 약속과 일관). Setup-time + 매 weekly cycle 진입 시 재검사. 핀 불일치 시 한국어 1동작 복구 안내(새 경로/태그 입력) + 산출진(§6.3) 호출 명시 차단(무응답 무한 대기 금지).
- **`self_evolution_gate.py` 외부 강제 (P2)**: §3.2 `@phase2-evolution-builder` 산출물. 본 hook 호출은 *동일 Claude Code 세션 안*이 아니라 *git pre-commit*(§10.4)에서 강제. 자기-감시 우회 차단. ADR 의무 — `architectural-decision-records.md`에 "self-evolution은 외부 관찰자(pre-commit)에서만 강제됨" 기록.
- **§11 #11 신설 (P3)**: translation-quality-team 전체 실패(3 teammate 모두 timeout/error) → 산출 차단하지 않고 `outputs.en` 유지 + `outputs.ko = "<번역 보류 — Tier 0 한국어 1줄 요약>"` + FR-22 자가 검증 신호 ⑦ "번역 보류"로 노출. Phase 진입 게이트는 허용(품질 절대우선 — 영문 산출은 보존)하되 *외부 발행*(§7 `/팀-회중허가`) 단계에서만 차단.

### §19.2 변경이 흔드는 일관성 지점 (다음 라운드 점검)

1. **§11.4 자가 검증 신호 카운트**: v0.6까지 ⑥(didim 도달성). v0.7로 ⑦(번역 보류 신호) 추가 → §11.4 본문 행 갱신 필요.
2. **§7 `/팀`의 3-Door**: Phase 1에서 M1만 활성, M2/M3는 안내 메시지("Phase 2 도입 예정") — UX 회귀 골든 추가 필요.
3. **§14 Phase 1 build 표**: "3-Door 전체"가 "M1 단일 + M2/M3 stub"로 격하 — `phase1_minimum_set.decided_set`(BL-3)에 영향, BL-3 결정 카드에 P5 주 추가.
4. **§13.2 ADR 컨벤션**: P6 changelog 포인터 강화는 *기존 ADR* 소급 의무 아님(가독성 비용 회피). v0.7 이후 신규 항목만 적용.
5. **§6.1 hook 의존 매트릭스**: P1 probe 행 + P7 genome_pin_audit 행 추가 필요(다음 라운드).
6. **§15 모호 지점**: P4·P5는 BL-(vi)·BL-3 영역과 중첩 — 결정 카드 통합 가능성 검토.

### §19.3 SOT/RLM 보존 재확인

- **I1 단일 쓰기자**: P1 probe는 *탐지 only* (쓰기 차단은 기존 `dual_sot_pairing_guard.py` 담당). I1 변동 0.
- **I2 RLM**: P7 게놈 pinning은 RLM 재독 대상에 *버전 식별자*를 추가 — 재독 표면이 명료해짐. P2 외부 관찰자 분리는 RLM 패턴(자기 세션 회상 금지) 강화.
- **I3 invocation**: P3 fallback의 부분 산출 invocation도 NDJSON 저널에 기록(D4와 정합). translation-quality-team teammate 단위 실패 ts 모두 보존.
- **I4 timeout**: P3는 30s × 3 teammate 모두 timeout 시점에 발동 — Rule 2 정합. heartbeat(D7)과 결합.
- **CCP 비례성**: 7건 일괄 도입 금지. Tier 표(우측 컬럼) 준수.

### §19.4 PRD 본문 수정과의 분리 (CCP ③ 승인 게이트)

본 §19는 *PRD 미수정 가정* 하에 워크플로우 측 대응만 명시. PRD 본문 수정 의제(별도 승인):
- PRD §11.5: "정의상 직교" → "설계상 직교 + 런타임 검증" 어휘 교체.
- PRD §9.4: "결정적 매처 + LLM 둘 다" → "외부 관찰자(pre-commit) + LLM" 명시.
- PRD §11.2: 번역 서브에이전트 fallback 행 추가.
- PRD §8 FR-25: P0 → FR-25-원칙(P0)/FR-25-메커니즘(P1) 분할.
- PRD §8 FR-21: FR-21a(M1, P0)/FR-21b(M2/M3, P1) 분할.
- PRD §19 변경 이력: 성찰 보고서 path 동반 규약 추가.
- PRD §11.1.a: 갱신일 인용 규칙을 didim 게놈으로 확장.

PRD가 수정되지 않은 채 본 §19가 채택되면, 워크플로우는 *PRD 강변 지점을 런타임 검증으로 격하 적용*하므로 일관성은 유지된다(워크플로우가 PRD보다 보수적). 양쪽 동시 승인 권장.

---

## §20. v0.8 운용 결함 통합 인덱스 (R1 — 자동 러너 SESSION HEADER 디스크 사실 이탈)

> 본 섹션은 v0.8 변경의 *단일 인덱스*. 인용 보고서: 본 세션(2026-05-05) turn 2 — Infrastructure Build 코드베이스 전수조사 결과(`git log` 최근 10·`git status` churchTeam 영역·`find`·`ls` 4중 교차 검증) 산출물 0건 확정. 직전 turn 1 COMPLETION REPORT의 `CREATED: 없음` 라인과 일치. 그럼에도 turn 3 SESSION HEADER가 "Infrastructure Build 실구현 + 가상 데이터 시딩 완료"를 전제 → 자동 러너가 디스크 증거 없이 단계 완료를 단정하는 경로 존재.
>
> **위반 불변식**: 절대 기준 1(품질·환각 봉쇄). I2(RLM — 메모리 의존 결정 차단의 사전 봉쇄가 깨짐). 본 §20이 없으면 후속 turn이 hallucinated 전제 위에서 무한 누적될 수 있음(메타-환각 폭주).

| ID | 결함 요약 | 반영 위치 | 검증 모듈 | 도입 게이트 |
|---|---|---|---|---|
| **R1** 치명 | 자동 러너 SESSION HEADER가 디스크 산출과 무관하게 "완료" 기록 → 후속 turn이 hallucinated 전제 위에서 작동 | §6 hook 표(`session_header_disk_audit.py` 신설) · §11 새 행 #12 (헤더-디스크 이탈 fallback) · 본 §20 명세 | `_test_session_header_disk_audit.py` ≥ 5 (사실 일치/이탈/부분/키워드 부재/인용 경로 미존재) | Tier-A 즉시 (RED-first) |

### §20.1 신규 모듈 명세 — `session_header_disk_audit.py`

- **위치**: `Claude_skills/AI_churchteam/.claude/hooks/scripts/session_header_disk_audit.py` (Phase 0 setup_init이 배치)
- **트리거**: SessionStart hook, 단발 1회. churchTeam 작업 컨텍스트일 때만 활성 — 매처: `cwd ⊃ Claude_skills/AI_churchteam` ∨ `prompt/workflow-coding.md` 편집 의제 turn.
- **입력**: (a) 현 turn SESSION HEADER 텍스트, (b) 직전 turn COMPLETION REPORT의 `CREATED/MODIFIED/DELETED` 라인, (c) git 작업 트리.
- **검사 절차**:
  1. SESSION HEADER 키워드 추출: "구현 완료" · "산출 완료" · "빌드 완료" · "시딩 완료" · 동의 변형.
  2. 직전 COMPLETION REPORT의 `CREATED:` 항목이 "없음"·"0건"·부재 → **헤더-사실 이탈 1차 후보**.
  3. 헤더가 인용하는 산출 경로(예: `setup_init_churchteam.py`·`bootstrap.sh`) `os.path.exists()` 검증.
  4. 이탈 확정 시 exit 2 + 한국어 4줄 결정 카드(E-3 정본 4줄 인용) + 격리 파일 `runtime_directories/header-drift-violations/{ts}.md` 작성. Tier 0(현 세션)이 정직 보고로 응답 의무.
- **검증 골든** (≥ 5):
  1. 헤더-사실 일치 → exit 0 (PASS).
  2. "완료" 헤더 + `CREATED: 없음` → exit 2 (BLOCK). 본 §20 추가 사례가 적용 사례.
  3. 부분 산출(헤더 "완료" + 디스크 일부만 존재) → exit 1 (ADVISORY).
  4. 헤더 키워드 부재(예: "보고만") → exit 0 (PASS).
  5. 인용 경로 미존재 → exit 2 (BLOCK).
- **출력 격리 정책**: `runtime_directories/header-drift-violations/`는 SOT 아님(I1 변동 0). git 추적 외(.gitignore 의무). Phase 0 부트스트랩 시 디렉터리 생성.

### §20.2 §11 Fallback 새 행 #12 — 헤더-디스크 이탈

- **트리거**: §20.1 hook exit 2.
- **1차 회복**: Tier 0(현 세션) 즉시 정직 보고 + 사용자 결정 카드 발행. *코드 자율 생성 0*. 본 세션 turn 2·3이 첫 적용 사례 — 정직 거부 패턴이 본 fallback의 reference behavior.
- **2차 회복**: 자동 러너 일시 중단 신호 (사용자 가시 한국어 1줄: "자동 러너 헤더-디스크 이탈 감지. 사람 확인 필요."). 직전 본격 구현 세션의 산출 경로를 사용자 응답으로 수신.
- **3차 회복**: 사용자 응답 후 헤더 정정 ADR 발행(§13.2 + C-10 매처에 R1 행 추가). ADR 후에만 자동 러너 재개.
- **자율 금지 7행 정합**: 본 fallback은 *기록·중단·문의*만 — 코드 자율 생성/SOT 자율 쓰기/단계 자율 진입 0. 절대 기준 3(CCP) 보존.

### §20.3 §6 hook 의존 매트릭스 갱신 (다음 라운드 본문 갱신)

- 신규 행: `session_header_disk_audit.py`. 트리거: SessionStart. 의존: `restore_context.py`(부모 게놈 상속) 직후 실행. PreToolUse·PostToolUse 어떤 hook과도 비순환(읽기 only).
- §6.1 의존 매트릭스 표 자체의 행 추가는 다음 라운드(본 §20은 의도만 명시 — 표 구조 변경 회피).

### §20.4 SOT/RLM 보존 재확인

- **I1 단일 쓰기자**: §20 모듈은 SOT 직접 쓰기 0. 격리 파일은 `runtime_directories/` (SOT 아님). 변동 0.
- **I2 RLM**: 본 §20이 직접 강화 — RLM 메모리 의존을 *메타 수준*에서 사전 차단. 직전 turn의 사실(`CREATED: 없음`)을 디스크와 교차 검증해 후속 turn의 메모리 의존(헤더 단정)을 봉쇄.
- **I3 invocation 기록**: 본 hook은 sub-agent 호출 아님(SessionStart). NDJSON 저널(D4) 영향 없음.
- **I4 timeout**: 단발 1회 hook, 디스크 I/O만 — 30s timeout 위험 0.
- **절대 기준 1**: 본 §20 추가 자체가 본 워크플로우 hallucination 봉쇄망의 1차 격리. *워크플로우 자가 검증 시스템이 차단하려던 것을 워크플로우 자동화 자체가 발생시킴* — 이 모순의 외과적 봉쇄.
- **절대 기준 3 (CCP)**: 본 v0.8 변경 자체가 보고서 → 분석 → 외과적 수정 절차로 산출. 본 §20 인덱스가 그 추적 기록.

### §20.5 §15 모호 지점 갱신

- 신규 #16: 본 hook의 `cwd` 매처 정확값 — `Claude_skills/AI_churchteam` 외 *부모 워크플로우 turn*(예: `prompt/workflow-coding.md` 편집만 하는 turn)에서도 활성화 여부. 다음 라운드 결정.
- 기존 #1~#15 변동 없음. P4·P5 BL 중첩 결정 카드 검토(§19.2 #6)는 v0.8과 독립.

### §20.6 PRD 본문과의 분리 (CCP ③ 승인 게이트)

본 §20은 *PRD 미수정 가정* 하의 워크플로우 측 대응만 명시. PRD 본문 수정 의제(별도 승인):
- PRD §19 변경 이력 컨벤션에 "자동 러너 SESSION HEADER ↔ COMPLETION REPORT 정합" 절 추가 권장.

PRD가 수정되지 않아도 본 §20은 *워크플로우가 PRD보다 보수적*으로 작동하므로 일관성 유지.

### §20.7 본 변경의 자기 적용 (메타 검증)

본 §20 추가 자체가 R1 fallback 1차 회복의 reference behavior — *코드 자율 생성 0, SOT 직접 쓰기 0, 설계 문서 외과 수정 + 다음 라운드 표 구조 갱신 의도 명시만*. 본 turn이 §20 자체를 위반하지 않음을 디스크 증거(다음 turn `git diff` `prompt/workflow-coding.md`만 변경)로 자가 입증.

---

# Output A — 목차

§0 Reading Map · §1 Overall Architecture (3-Tier) · §2 Orchestrator Layer · §3 Sub-agents Catalog · §4 Agent Teams · §5 Skills Catalog · §6 Hooks Catalog · §7 Slash Commands · §8 Fork Use Cases · §9 SOT·RLM Enforcement · §10 TDD Automation · §11 Fallback Paths · §12 영어 운용 경계 · §13 평가 기준 3종 · §14 Build Order · §15 모호 지점 · §16 Agent Selection Protocol · §17 Python Determinism Layer (NEW v0.5) · §18 v0.6 결함 수정 통합 인덱스 (D1~D12) · §19 v0.7 PRD 적대적 성찰 반영 통합 인덱스 (P1~P7) · **§20 v0.8 운용 결함 통합 인덱스 (R1 — 자동 러너 SESSION HEADER 디스크 사실 이탈)**

# Output B — 섹션별 핵심 요약

- §1 3-Tier: Tier 0 단일 SOT writer / Tier 1 Phase Orchestrator 3개 / Tier 2 Worker (teams · specialists · bridge · reviewers · translator)
- §2 Tier 0은 본 세션 자체. Tier 1 = `@research-orchestrator`/`@planning-orchestrator`/`@impl-orchestrator`
- §3 빌드 8 + 구현 11 + 브릿지/리뷰어/번역 5 + 12 부교역자(지연 빌드)
- §4 4 teams: entry-gate(명시) · design-finalization(신설) · phase1-build(신설) · phase2-hardening(신설). Step 2는 worktree isolation
- §5 부모 5 skill 상속 + 도메인 신학 4 + 운용 3
- §6 hook 14개(신규 7개), 모두 RED-first TDD
- §7 11 slash command, 모두 SOT 기록
- §8 fork 4종 채택 (Step 2 teammate · Phase 0 bootstrap · D-3 evolution · DR rehearsal)
- §9 SOT 2 file · 단일 쓰기자 코드 강제 · RLM 4줄 stamp · invocation recording hook
- §10 RED-first hook, coverage 90%/85%, validator 11종
- §11 fallback 10종 + Safe-Mode
- §12 English 내부 / Korean 사용자 가시 / hook 강제
- §13 code-convention(HOW) · ADR(WHY) · code-quality-guide(WHAT) — Step 7.5 직후 작성
- §14 Pre-Phase 0 → Phase 0 → 1 → 2 → Steady state, 각 진입 ADR 의무
- §15 14개 모호 지점

# Output C — 모호 지점

§15 14개 그대로. 그중 **구현 차단 4건** (즉시 결정 필요): #1 BL-5 / #2 BL-3 / #3 BL-(vi) / #4 BL-2. 나머지 10건은 Phase 진입 전까지 결정 가능.

— end of workflow-coding.md draft v0.8 —
