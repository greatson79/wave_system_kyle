# churchTeam Workflow — AI 가상 부교역자팀 자동 빌드·운용·진화 설계도 (v0.5 draft)

> **v0.5 핵심 정정**: v0.4 적대적 성찰(`prompt/workflow-idea/REFLECTION-workflow-v0.4-adversarial.md`)의 P0 6건 외과적 반영. **P0-1**(C-α 결정타 — v0.4 헤더 ②③④⑤ 자체 약속 본문 누락) Step 5 Output에 `hierarchy-view.md` + BL-6 채택안 1줄 의무, Step 7 (human) Action에 BL-9 D-2 자동 끊김 사전 합의 서명(0회차 1회) 절차 명시, Step 12 Verification에 BL-11 권한 변경 결정 카드 4줄 + Slash Commands 표에 `/팀-권한변경` 등재, §18 W-11 정합성 재확인. **P0-2**(A-α/A-β/A-γ Bootstrap 미검증 가정) Step 8 Setup hook을 *SessionStart matcher + 명시 슬래시 `/팀-점검` 이중 진입*으로 재정의, Step 9 9a 셸 1줄을 *오프라인 사전 다운로드 전제*로 변경 + 9c GUI 시나리오에 오프라인 첫 진입 후보 ≥ 1 추가, Step 5.5 신설(CM-1 `claude -p` headless 실측 가능성 Phase 0 진입 전 1회 사전 확인). **P0-3**(C-β idea v0.5 §6 #26 "Phase 1 최소 셋 후속 위임" 위반) Step 10 Verification의 10+ 게이트 단정을 *BL-1 결합 후속 라운드 위임 + state.yaml `phase1_minimum_set.decided_set` 의존 분기*로 약화. **P0-4**(B-α teammate-D 산술 과부하) Step 2 BL 재균형 — BL-11을 gate-D → gate-C로 이관, turn 상한 12 → 18 상향 + BL당 최소 turn ≥ 2 명시. **P0-5**(C-ε pastoral-decision-logs 자기 모순) Runtime Directories "commit 권장" 라인 삭제 + privacy_policy 단일 출처화. **P0-6**(C-θ §1.bis ↔ Step 10 RC-β 자기 모순) §1.bis에 "RC-β 채택 시 본 미사용 default 자동 해제 — Phase 1 *내* 채택 카드 1회 통과로만" 단서 추가. v0.4 → v0.5 변경 이력은 §19 참조.

> **v0.4 핵심 정정**: 2차 반영 완결성 성찰의 부분 누락 4건 외과적 보강. ① Step 6 + Error Handling에 B-π P-β 동시 갱신 충돌 신호 명세 ② Step 5 verification에 BL-6 위계 가시화 화면 채택안 + Output `hierarchy-view.md` ③ Step 7 (human)에 BL-9 *D-2 자동 끊김 사전 합의 카드* 동봉 서명(0회차 1회) ④ Step 12에 BL-11 외부 채널 권한 변경 결정 카드 4줄 + `/팀-권한변경` 슬래시 ⑤ §18 W-11 갱신, §19 v0.4 변경 이력. v0.3 → v0.4 변경 이력은 §19 참조.

> **v0.3 핵심 정정**: workflow-idea ↔ workflow 반영 완결성 성찰의 확정 권장 조치 G1~G5 + 미반영 4건 추적성 행을 외과적으로 반영. ① Step 10 `sermon-context.md` append-only 주입을 *BL-2 = RC-β 조건부*로 약화(G1) ② §1·§18에 B-5 비채택 명시(G2) ③ Step 13 D-3 Phase 분기를 *BL-(vi) 결정 결과 반영* 표현으로 약화(G3) ④ Step 2 CP-1 *후보 ≥ 2*를 모든 P0 게이트로 확장(G4) ⑤ state.yaml `entry_gates` 스키마에 `done_criterion`/`output_artifact`/`close_signal` 3필드 추가(G5) ⑥ §18에 idea 미반영 4건(A-δ/B-α/B-ζ/C-θ) W-11 추적성 행 추가. v0.2 → v0.3 변경 이력은 §19 참조.

> **v0.2 핵심 정정**: didim은 독립 CLI가 아니라 Claude Code **슬래시 커맨드 시스템**(`/주간총괄`·`/설교` 등). 본 문서의 모든 "didim CLI 호출"은 *슬래시 커맨드 spawn 또는 산출물 파일 직접 생산*으로 재정의된다(Step 6 재설계). v0.1 → v0.2 변경 이력은 §19 참조.

> **이 문서의 성격**: `prompt/prd.md` v0.5 + `prompt/workflow-idea/workflow-idea.md` v0.5를 입력으로, Claude Code가 *로컬 macOS 위에서 처음부터 끝까지 자동 실행*할 수 있는 단일 워크플로우 설계도(blueprint). 본 문서는 *설계도*이며, 실제 코드 구현은 별도 지시로만 진행한다.
>
> **상위 SOT**: `prompt/prd.md` v0.5 (2026-05-04). 본 워크플로우의 모든 단계는 PRD §0.1 제1 핵심 목적과 1줄 연결을 보유한다.
>
> **부모 게놈**: `AgenticWorkflow-Template/AGENTS.md` + `soul.md` + `docs/protocols/*` + `Claude_skills/weekly-works/CLAUDE.md` (didim 게놈, *위임 호출 엔진*).
>
> **상태**: draft v0.5 — v0.4 적대적 성찰(`prompt/workflow-idea/REFLECTION-workflow-v0.4-adversarial.md`)의 **P0 6건 외과적 반영 완료**(P0-1 C-α 결정타 / P0-2 Bootstrap 미검증 / P0-3 idea §6 #26 / P0-4 teammate-D 과부하 / P0-5 자기 모순 / P0-6 §1.bis 자기 모순). P1 8건은 다음 라운드 위임. 사용자 승인 후 v0.6~ 진화.

---

## Overview

- **Input**: `prompt/prd.md` v0.5 + `prompt/workflow-idea/workflow-idea.md` v0.5 + 부모 게놈 + didim 게놈
- **Output**: `Claude_skills/AI_churchteam/` 자식 인스턴스(메타빌드 산출) — 단일 슬래시 진입점 `/팀` + 12직 부교역자 지연 빌드 + 신학 2중 필터 + 한국어 자가 검증 화면 + 이중 SOT 페어링 + didim 7 에이전트 위임 호출
- **Frequency**: Bootstrap(1회) + 일상 운용(주간 사역 사이클) + SPOF 자가 복구(이벤트) + 자기 진화(PRD 재입력 시) + 재해 복구(이벤트)
- **Autopilot**: **disabled** (제1 핵심 목적의 ③ "목회자 최종 검토" 절대 우선 — D-2 영적 검토 카드는 *설계상* 자동 흐름을 끊는다)
- **pACS**: **enabled** (모든 에이전트 단계에서 자체 신뢰 평가 의무)

---

## Inherited DNA (Parent Genome)

> 본 워크플로우는 AgenticWorkflow의 전체 게놈을 *상속*한다. 자식 시스템(churchTeam)도 동일 게놈을 *재상속*한다. 도메인은 다르지만 게놈은 동일하다(`soul.md §0`).

### Constitutional Principles (도메인 맥락화)

1. **Quality Absolutism (절대 기준 1)** — 본 워크플로우 도메인에서 "품질"은 *영적 사역의 강화*다. 속도·자동화율·토큰 비용·산출량은 *모두* 무시된다. 한 단계 추가로 신학 정합성·목회자 분별 여지가 늘어난다면 그 단계를 *반드시* 추가한다. PRD §0.2·§4.1·§5.2 NG-6/NG-7과 동조.
2. **Single-File SOT (절대 기준 2)** — `.claude/state.yaml` 단일 파일에 churchTeam 공유 상태 집중. 쓰기 권한은 `@team-lead` 1인. 병렬 부교역자는 *읽기 전용* + 자기 출력 폴더만 쓰기. 추가로 *이중 SOT 페어링*: didim `status.md`와 churchTeam `state.yaml`의 *직교 진실 분할* 약속(PRD §11.5) 준수. churchTeam이 didim 필드를 복제 금지(역방향 금지).
3. **Code Change Protocol (절대 기준 3)** — 구현 단계에서 코드 변경 시 의도→영향→설계 3단계. 신학 필터·sermon 함수 시그니처·SOT 단일 쓰기자 코드는 *대규모 변경* 분류 의무. CCP 위반은 D-3 자기 진화 사전 게이트(§9.4)와 충돌하므로 게이트 매처가 자동 차단.

### Inherited Patterns

| DNA Component | Inherited Form |
|---|---|
| 3-Phase Structure | Research(BLOCKER 해소·설계 결정) → Planning(설계도 확정·페어링 검증) → Implementation(Bootstrap·운용·진화·복구 5단계) |
| SOT Pattern | `.claude/state.yaml` (churchTeam) + `Claude_skills/weekly-works/output/.../status.md` (didim, 읽기 포인터만) |
| 4-Layer QA | L0(파일 존재 ≥ 100B) → L1(Verification 기준) → L1.5(pACS F/C/L 자기 채점) → L2(`@reviewer` + `@fact-checker` Enhanced) + **신학 2중 필터(D-1 LLM 1차 + 결정적 2차)는 모든 산출 노드 의무 추가 계층** |
| P1 Hallucination Prevention | `validate_*.py` + 신학 결정적 2차 필터(금칙어·인용 성구 ↔ SOT 본문 해시 일치·금지 출처 도메인 화이트리스트) |
| P2 Expert Delegation | 12직 부교역자(참모진/전략진/산출진) 각자 단일 컨텍스트 깊이 유지 + Team Lead 조율 |
| Safety Hooks | `block_destructive_commands.py`(상속) + `theology_filter_dual.py`(신규 — 외부 노출 직전 결정적 게이트) + `dual_sot_pairing_guard.py`(신규 — didim 필드 churchTeam SOT 복제 차단) |
| Adversarial Review | `@reviewer`(설계·구조) + `@fact-checker`(신학·인용) + **`@theological-reviewer`(신규 — 개혁주의 정합·이단 표현 LLM 1차 필터)** |
| Decision Log | `autopilot-logs/` 비활성(Autopilot disabled) → 대신 `pastoral-decision-logs/`(목회자 영적 검토 카드 누적) |
| Context Preservation | Snapshot + Knowledge Archive + RLM (이중 SOT 페어링 시 churchTeam SOT만 복원, didim SOT는 didim 자체 복원에 위임) |

### Domain-Specific Gene Expression

본 워크플로우에서 *특히 강하게 발현*되는 DNA:

- **HITL 유전자(D-2 영적 검토 카드)** — 4.5 제목 게이트·신학 필터 FAIL·외부 발행 직전 3개 노드에서 yes/no 클릭 대신 *분별의 형식*. 자동 흐름이 *설계상* 끊긴다(BL-9 사용자 사전 합의 약속 결합).
- **이중 SOT 페어링 유전자** — `didim`은 흡수·재작성 금지(약속 6). 위임 호출 + 단방향 포인터(B-3) + Wrapper `@didim-bridge`(B-4 / RC-α) 결합.
- **메타빌드 유전자(약속 2)** — PRD 자체를 입력으로 자기 빌드. PRD diff = 자기 진화 = Bootstrap 재진입(A-5 단일 경로) + §9.4 자율 권한 경계 사전 게이트.
- **자가 검증 유전자(약속 5)** — FR-22 6종 신호(DNA 상속·SOT 무결성·신학 필터·외부 인증·자기 진화 이력·didim 도달성)를 *한 장의 한국어 진단표*로 1초 가독.

---

## §1. 진입 게이트 — workflow.md 본문 설계 진입 차단 8종 + 부수 1종

> **워크플로우-idea §7의 8종 진입 게이트**가 *모두 해결*되기 전 본 워크플로우의 Implementation Phase는 **봉인**된다. Research Phase가 게이트 해소를 담당.
>
> 게이트 미해결 상태로 Implementation 진입 = 약속 2·3·4·5·6 + 절대 우선순위 ③ 동시 훼손.

| Gate | BL ID | 사유 | 결정 단계 |
|---|---|---|---|
| (i) | BL-1 | 3직무 워크플로우 흐름 + 3축↔3-Door 매핑 (3축 흐름 후보 ≥ 2 — idea v0.5 §0.2 ④ 후보안 슬롯 의무 + §11 BL-1 Done 기준) | Research §2 / Step 3 |
| (ii) | BL-2 | didim 주입 콘텐츠 스펙 + 읽기 채널(RC-α/β/γ 중 채택) | Research §2 / Step 4 |
| (iii) | B-1 사전 검증 | didim CLI 미지 인자 처리 결과 + 재검증 트리거 | Research §2 / Step 5 |
| (iv) | BL-7 | D-4 self-lock 회수 정책 + D-5 fallback 발행 정책 확정 | Research §2 / Step 6 |
| (v) | BL-4 | 재해 복구(SOT 손상·게놈 손상·전체 복원) 골격 | Research §2 / Step 7 |
| (vi) | D-3 Phase 분기 | 자기 진화 사전 게이트 Phase 1 vs Phase 2 + 매처 화이트리스트 초기 형태 | Research §2 / Step 8 |
| (vii) | BL-12 | didim 비커버 신규 산출진 등록 인터페이스 (약속 6 정합) | Research §2 / Step 9 |
| (viii) | BL-13 | FR-22 6종 신호 PRD ↔ C-2 매핑 검증 | Research §2 / Step 10 |
| (부수) | BL-10 | 운영 신뢰성 4종(부모 게놈 stale·최후 알림 채널·재시도 예산·CLI 재검증) | Research §2 / Step 11 |

> **B-2/B-5 미사용 default 명문 (v0.3)**: idea §7 권고 묶음에 따라 B-2(파일 드롭)·B-5(PreToolUse Hook 자동 주입)는 *Phase 1 미사용 default*. Step 10 didim 입력 주입 채널은 BL-2(RC-α/β/γ) 결정 카드 통과 후에만 활성. 사용자 명시 채택 카드 부재 시 본 두 형태는 워크플로우 어느 단계에서도 도입 금지.
>
> 추가 보류 게이트: **BL-5** (A-1 0회차 진입 행위자 + A-5 PRD 수정자 결정), **BL-8** (A-3 1동작 복구 명세), **BL-9** (D-2 자동·HITL 끊김 합의), **BL-3** (12직 명함), **BL-6** (위계 가시화 화면), **BL-11** (외부 채널 권한 변경 절차) — 이들은 Planning Phase에서 결합 결정.

> **§1.bis Phase 1 미사용 기본값 (v0.3 신설, idea §7 R-5 명문화)**: 다음 2종은 *사용자 명시 채택 결정* 전까지 Phase 1 도입 **금지 — 기본값**. Step 10 Verification 자동 차단.
> - **B-2** (didim SKILL.md 1줄 패치 — 컨텍스트 파일 드롭) — 약속 6 "보존 vs 재작성" 사용자 판정 미통과
> - **B-5** (PreToolUse Hook 자동 주입) — 비가시 결합으로 약속 5 자가 검증 가시화 위반
>
> **(v0.5, P0-6 자기 모순 해소)** **RC-β 채택 시 자동 해제 단서**: BL-2 결정 카드에서 사용자가 RC-β(B-2 한정 sermon-context.md append-only)를 명시 채택하는 *Phase 1 내 1회 통과*가 SOT(`pastoral-decision-logs/BL-2-{date}-decision.md` + `state.yaml.entry_gates.BL-2.decision = "RC-β"`)에 기록되는 순간 본 §1.bis의 *B-2 미사용 default*만 자동 해제. **B-5 미사용 default는 별도 BL 라운드 통과 전까지 해제 금지** — RC-β 채택은 B-5 채택을 함의하지 않음(채널 분리). Step 10 Verification은 RC-β 채택 SOT 기록을 *읽고 분기* — 미기록 상태에서 B-2 형태 활성화 시도는 여전히 차단. `validate_workflow.py --check-promise-6-literal`은 RC-β 채택 SOT 존재 여부를 *예외 화이트리스트*로 인식.
>
> 우발 도입 차단 매처: `validate_workflow.py --check-promise-6-literal` — `Claude_skills/weekly-works/.claude/skills/**/SKILL.md` diff 또는 `PreToolUse` matcher에 didim 슬래시·경로 등장 시 exit 2 + 한국어 4줄.

> **B-5 비채택 명문화 (v0.3, G2)**: idea §7 R-5 "B-2/B-5 Phase 1 미사용 권고"에 따라 **B-5(`PreToolUse` Hook 자동 didim 컨텍스트 주입)는 Phase 1 비채택**. 사용자 명시 채택 결정(별도 BL 라운드) 전까지 본 워크플로우의 어떤 단계도 B-5형 hook을 등록하지 않는다. didim 입력 주입은 Step 6에서 채택된 RC-α/β/γ *읽기 채널*만 사용. 본 비채택은 §18 W-12 흔들 지점에 추적성 보존.

---

## Research

> 목적: 진입 게이트 8+1종 해소 + 12직 명함·BL-5/8/9/3/6/11 결정 + PRD ↔ workflow-idea 정합성 4단계 읽기 검증.

### 1. PRD + workflow-idea 4단계 읽기 + 부모/didim 게놈 인덱싱
- **Pre-processing**: 두 입력 파일 + `AgenticWorkflow-Template/AGENTS.md` + `soul.md` + `docs/protocols/*` + `Claude_skills/weekly-works/CLAUDE.md` + didim 7 에이전트 source 경로의 메타데이터(파일 크기·최종 수정일·SHA256) 사전 계산 (Python script). 인용 시 갱신일 자동 첨부 규칙(PRD §11.1.a) 활성화.
- **Agent**: `@prd-reader` (Opus, project scope, read-only)
- **Verification**:
  - [ ] PRD §0.1 제1 핵심 목적 단일 문장 추출 + 본 workflow.md §1 게이트 표 9행과 1:1 매핑 (구조적 완전성)
  - [ ] PRD 6대 절대 약속 6항 모두 인용 + 각 약속이 본 워크플로우의 어느 단계에 *발현*되는지 표시 (교차 단계 추적성)
  - [ ] workflow-idea §6 충돌 26건 + §11 BL 13건 모두 인덱싱 (구조적 완전성)
  - [ ] didim 7 에이전트 source 경로 모두 존재 확인 + 위치 변경 가능성 ✅/⚠ 라벨 (데이터 정합성, source: PRD §11.1.a 주소 안정성 약속)
  - [ ] 4단계 읽기 결과(본질·연관 확장·중간 보충·역방향 누락) 4개 섹션으로 산출 (구조적 완전성)
  - [ ] 부모 게놈 SHA + didim 게놈 SHA를 `inheritance-manifest.draft.json` 후보로 기록 (파이프라인 연결: Step 13 Bootstrap이 사용)
- **Task**: Read both inputs in 4-pass mode (essence → expanded relations → mid-document precision → reverse-gap). Build a unified index of all 9 entry gates, 26 conflicts, 13 BLs, 12 ministerial-role candidates, and didim's 7-agent inventory. Mark every claim with `(source: PRD §X.Y)` or `(source: idea §Z)` annotations. **Do NOT decide anything** — only catalog.
- **Output**: `prompt/workflow-research/prd-idea-index.md` + `prompt/workflow-research/genome-manifest.draft.json`
- **Translation**: none (실행 산출물 — 한국어 원본 보존)
- **Post-processing**: `validate_traceability.py --check-cross-refs` 실행 → CT1-CT5 통과 강제. 누락 시 자동 재호출.
- **복구 (v0.2 신설, P0)**:
  - **PRD/idea 파일 부재**: 작업 중단 + 한국어 4줄 카드 ("입력 파일 누락. `prompt/prd.md` 또는 `prompt/workflow-idea/workflow-idea.md`을 복구한 뒤 Step 1을 재호출하세요.") — 자동 재호출 금지(파일이 없으면 무한 루프).
  - **didim 경로 이동 감지**: `DIDIM_ROOT` 환경변수 우선 → 없으면 `Claude_skills/weekly-works/`·`../*/weekly-works/` 2-hop 탐색 → 그래도 없으면 사용자 카드(경로 1줄 입력 요청).
  - **부모 게놈 SHA 계산 실패**: 손상 파일만 `sha: "UNAVAILABLE-{filename}"`로 기록 + manifest에 `degraded: true` 플래그 → Step 8 setup_init이 차단 신호로 사용.
- **제1 목적 연결**: 통찰·기획·실행 3축의 정의가 PRD에 박혀 있음을 *재독*으로 보존 — 환각 차단(약속 2 메타빌드의 첫 동작은 *생성*이 아니라 *거부*, A-2).

### 2. (team) 진입 게이트 8+1종 동시 해소 — 4 teammate 병렬 디스패치

병렬화 근거(절대 기준 2 동반 SOT 설계 명시): 9개 게이트는 *서로 다른 도메인*(메타빌드/페어링/UX/품질) → 각 teammate가 *독립 컨텍스트*에서 자기 영역 100% 집중 = 단일 에이전트 순차보다 *품질 우위*. 단, 각 teammate는 SOT 직접 쓰기 금지. Team Lead만 통합 갱신.

**컨텍스트 예산 (v0.2)**: teammate별 turn 상한 = **15 turn** (CP-1/CP-2/CP-3 각 5 turn 가이드). 중간 산출물은 즉시 외부 파일(`gate-resolutions/{A,B,C,D}.md`)에 flush — 부모 세션이 전체 turn 로그를 보지 않고 *최종 .md 파일*만 통합. teammate 간 충돌(예: gate-A의 BL-5와 gate-D의 BL-9가 HITL 자리 정의 충돌)은 Team Lead 통합 단계에서 *충돌 매트릭스*(BL × BL 교차표) 생성 → Step 3 결정 카드에 *충돌 사실 명시* + 사용자 일괄 결정.

- **Team**: `entry-gate-resolution-team`
- **Checkpoint Pattern**: dense (각 teammate가 다중 게이트 처리, 중간 산출물 검증 다중)
- **Context Budget (v0.2 신설, P1 / v0.5 P0-4 상향)**: teammate별 **turn 상한 18** (v0.4의 12 → v0.5 P0-4로 상향 — teammate-D 산술 과부하 해소). **BL당 최소 turn ≥ 2 보장**(BL × 2 ≤ 18 = BL ≤ 9 분배 안전선). 초과 시 자동 escalate 카드. 각 teammate는 *부모 세션과 분리된 sub-agent context*에서 동작 — 중간 산출물(>2KB) 즉시 외부 파일화(`gate-resolutions/{X}/scratch/`)하여 부모 컨텍스트 오염 차단. Team Lead는 통합 시 *요약본*만 수신(전문 첨부 금지).
- **Teammate 충돌 사전 탐지 매처 (v0.2 신설, P1)**: 4 teammate 산출 통합 시 Team Lead가 `validate_workflow.py --check-teammate-conflict` 실행 — gate-A의 BL-5 결정과 gate-D의 BL-9 HITL 자리, gate-B의 RC 채택과 gate-C의 3-Door 분기 등 *교차 BL* 관계를 매처로 사전 탐지. 충돌 발견 시 Step 3 사용자 결정 카드에 "교차 충돌 해소" 항목 자동 추가.
- **Tasks**:
  - `@gate-A-meta-build` (Opus): Gates (vi) D-3 Phase 분기 + BL-5 (A-1 0회차 진입 행위자 + A-5 PRD 수정자) + BL-8 (A-3 1동작 복구) + BL-10 ① 부모 게놈 stale 갱신 트리거
    - **Checkpoints (dense)**:
      - CP-1: 후보 형태 ≥ 2개씩 발산 (각 게이트별)
      - CP-2: 각 후보의 약속 1·2·3 위반 위험 표 + 트레이드오프 1줄
      - CP-3: 사용자 결정 카드(한국어 4지선다 + "이게 무슨 뜻인가요?" 펼침) draft
  - `@gate-B-pairing` (Opus): Gates (ii) BL-2 didim 주입 콘텐츠 스펙 + (iii) B-1 사전 검증 + (vii) BL-12 신규 산출진 등록 인터페이스 + BL-10 ④ B-1 재검증 트리거
    - **Checkpoints (dense)**:
      - CP-1: B-3.bis RC-α/β/γ 비교 표 + Wrapper `@didim-bridge` 형태 후보
      - CP-2: didim 슬래시 커맨드 사전 검증 *실측 결과* — **구체 명령 1건**: `/주간현황` dry-run(읽기 전용 status.md 조회) 1회 실행 후 결과 캡쳐(통과/오류/응답 형식). v0.2 정정: didim은 외부 CLI가 아니므로 "미지 인자"는 *슬래시 커맨드 옵션 플래그*(예: `--dry-run`)로 재해석.
      - CP-3: 약속 6 위반 위험 표 + 신규 산출진 카탈로그 슬롯 정의
  - `@gate-C-ux` (Opus): Gates (i) BL-1 3-Door↔3축 매핑 + (viii) BL-13 FR-22 6종 신호 + BL-3 12직 명함 후보 ≥ 2 + BL-6 위계 가시화 화면 + **BL-11 외부 채널 권한 변경 절차 (v0.5 P0-4 — gate-D → gate-C 이관, teammate-D 산술 과부하 해소)**
    - **Checkpoints (dense)**:
      - CP-1: 3-Door↔3축 매핑 후보 ≥ 2 (치환 vs 직교 6칸)
      - CP-2: FR-22 6종 신호 한국어 라벨 후보 ≥ 1 + 신호등 매핑 규칙 + "사역 가능/일부 점검/중단" 종합 산출 규칙
      - CP-3: 12직 명함 후보 ≥ 2 + 위계 가시화 화면 후보 ≥ 2 (조직도형·대화 흐름형)
  - `@gate-D-resilience` (Opus): Gates (iv) BL-7 D-4 self-lock 회수 + D-5 fallback 발행 정책 + (v) BL-4 재해 복구 + BL-9 D-2 합의 자리 + BL-10 ②③ 최후 알림·재시도 예산 (**BL-11은 v0.5 P0-4로 gate-C 이관 — 본 teammate에서 제외**)
    - **Checkpoints (dense)**:
      - CP-1: self-lock 회수 후보 ≥ 2 (pid 생존 검사·이중 heartbeat·사용자 1동작 회수·crash 마커)
      - CP-2: D-5 발행 정책(차단 ON 기본 / 캐시 노출 OFF 기본) 한국어 알림 카드 4줄 + 재시도 예산(부모 RB1-RB3 참조) 상한
      - CP-3: 재해 복구 3종(SOT 손상·게놈 손상·전체 복원) 시나리오 + 1동작 복구 한국어 문구 ≥ 1
- **Verification** (Team Lead 검증):
  - [ ] 9개 진입 게이트 + 6개 부수 BL(BL-3/5/6/8/9/11) 모두에 *후보 형태 ≥ 1*
  - [ ] **(v0.3, G4) 모든 P0 진입 게이트 9종(BL-1·BL-2·B-1·BL-7·BL-4·D-3 Phase·BL-12·BL-13·BL-10)에 후보 *≥ 2* 보존** — idea §0.2 ④ 후보안 슬롯 원칙 일관 적용. 후보 1개만 산출된 게이트는 발산 라운드 자동 재호출
  - [ ] §0.2 ④ 후보안 슬롯 원칙 적용: ⚠/🚧/🛡 표기 모든 보류 항목에 후보 ≥ 1 + 트레이드오프 1줄 (구조적 완전성). **BL-1(3축 흐름) 한정 후보 ≥ 2 의무** (idea §11 BL-1 v0.5 Done 기준 일치, v0.3 강화)
  - [ ] 모든 후보가 약속 1~6 위반 위험 표를 보유 (데이터 정합성)
  - [ ] B-1 사전 검증 결과는 *실측*(슬래시 커맨드 1회 실행 결과 — 예: `/주간현황` dry-run)이며 추정 아님 (데이터 정합성, source: idea §6 #16)
  - [ ] 각 게이트의 산출이 Step 3 사용자 결정 카드 입력 형식과 일치 (파이프라인 연결)
- **Task**: Each teammate independently resolves their assigned gates by producing candidate forms, trade-offs, and Korean decision cards. **No teammate decides** — they prepare options for human decision. SOT writes go through Team Lead only.
- **Output**: `prompt/workflow-research/gate-resolutions/{A,B,C,D}.md` + 통합 `prompt/workflow-research/gate-resolution-summary.md`
- **Translation**: `@translator` → `gate-resolution-summary.ko.md` (사용자 결정 입력용 한국어 정본)
- **Review**: `@reviewer + @fact-checker` (구조·신학·인용 모두 적대적 교차 검증)
- **Post-processing**: `validate_workflow.py --check-w1-w8` (DNA 유전 검증) + `validate_pacs.py` (PA1-PA7 + L0)
- **SOT 쓰기**: Team Lead만. 팀원은 `gate-resolutions/{A,B,C,D}.md` 산출물 파일만 생성. `state.yaml.workflow.active_team`에 4 teammate 진척 기록.
- **제1 목적 연결**: 9개 게이트 미해결 상태 = 약속 2·3·4·5·6 + 절대 우선순위 ③ 동시 훼손 → 본 단계가 그 봉인을 *해제*하는 유일한 경로.

### 3. (human) 사용자 결정 카드 — 게이트 8+1종 + 부수 BL 결정
- **Action**: Read `gate-resolution-summary.ko.md`. For each gate, select one candidate from the Korean 4-choice card, or write a custom decision in the freeform memo. **All 9 entry gates + 6 ancillary BLs must be answered**; partial decisions block Implementation Phase.
- **Command**: `/팀-결정` (재진입: `/팀-결정 --resume` v0.2 정식 등록 — W-2 처리)
- **부담 분산 정책 (v0.2 신설, P2)**: 9+6=15 카드 일괄 응답 부담 → **세션 분할 권장** (한 세션 최대 6 카드). 진입 게이트 9종 우선 → 휴식 → 부수 BL 6종 차순. 응답 도중 세션 종료 시 PreCompact/SessionEnd Hook이 자동 누적, 다음 진입 시 `--resume`이 미응답 게이트만 표시.
- **결정 카드 형식 (PRD §11.3 4줄 패턴 + 적대적 §B-α 합의)**:
  1. 무엇을 결정하나요? (게이트명 + 사유 1줄)
  2. 후보 (각 후보별 약속 위반 위험 + 트레이드오프 1줄)
  3. 영향 (이 결정이 어느 부교역자·어느 산출물에 미치는가)
  4. 자유 메모 (사용자 분별 — 카드 자체가 SOT `pastoral-decision-logs/gate-{ID}-decision.md`에 누적)
- **제1 목적 연결**: 약속 1(무코드) + 절대 우선순위 ③(목회자 최종 검토) — 결정 동선이 비개발자 UX로 흡수.

---

## Planning

> 목적: Step 3 결정 결과를 외과적으로 PRD/idea에 *반영*(혹은 별도 결정 부록으로 보존) → 12직 명함 확정 → 3축 매핑 확정 → didim 페어링 인터페이스 확정 → workflow.md *본문 설계 진입* 허가.

### 4. 결정 결과 외과적 반영 + PRD/idea 갱신 제안
- **Pre-processing**: `pastoral-decision-logs/` 누적 결정 카드 → diff 형식 변환 (PRD diff 후보안 + idea diff 후보안). PRD diff는 §9.4 자율 권한 경계 사전 게이트 통과 의무.
- **Agent**: `@meta-build-architect` (Opus, project scope)
- **Verification**:
  - [ ] PRD §0.3·§15.1 P0 BLOCKER 13건 중 본 결정 결과로 해소되는 항목을 명시 (구조적 완전성)
  - [ ] 외과적 반영 — 무관 섹션 변경 0 (CCP Step 3 변경 설계 적용, source: 절대 기준 3)
  - [ ] PRD §11.5 이중 SOT 페어링 약속과 결정 결과의 정합 검증 ✅ (데이터 정합성)
  - [ ] §9.4 사전 게이트(LLM 자기 분류 + 결정적 매처 둘 다) 통과 확인 — "자율 금지" 7행 위반 시 사용자 재승인 카드 발행 (data 정합성, source: PRD §9.4 v0.5 사전 게이트 약속)
- **Task**: Generate diff proposals for PRD v0.5 → v0.6 and workflow-idea v0.5 → v0.6 incorporating user decisions from Step 3. Surgical edits only. Auto-block any diff that mutates §9.4 "자율 금지" rows without explicit user approval card.
- **머지 주체 (v0.2 신설, P1)**: diff *적용 주체는 사용자*. 본 단계는 diff `.md` 파일만 생성 + 한국어 4줄 카드("PRD v0.5 → v0.6 변경안 N건. 검토 후 `git apply prompt/prd.v0.6.diff.md` 또는 수동 머지하세요.")로 안내. 자동 머지 금지(약속 1 무코드 + §0.1.bis 약속 1 정합). 사용자가 머지 후 `/팀-진입허가`(Step 7) 카드에서 PRD 버전 갱신 확인.
- **Output**: `prompt/prd.v0.6.diff.md` + `prompt/workflow-idea/workflow-idea.v0.6.diff.md` + `prompt/workflow-research/decision-application-report.md`
- **Translation**: `@translator` → `decision-application-report.ko.md`
- **Review**: `@reviewer` (CCP 비례성 검증) + `@fact-checker` (PRD 인용 정확성)
- **Post-processing**: `validate_traceability.py --check-decision-trace` — 모든 diff 행이 Step 3 결정 카드와 1:1 매핑

### 5. 12직 부교역자 명함 확정 + 3축 매핑 확정 (BL-1, BL-3 결합 산출)
- **Agent**: `@team-architect` (Opus)
- **Verification**:
  - [ ] 12직(±N) 각 부교역자에 직무명·1줄 사명·소속 축(통찰/기획/실행)·보고선·권한 경계 4필드 모두 포함 (구조적 완전성, source: PRD §7.1)
  - [ ] 사고 보조 축 ≥ 1, 전략 보조 축 ≥ 1, 실행 보조 축 ≥ 1 (Q3 균형 원칙)
  - [ ] 실행 보조 축의 부교역자가 didim 7 에이전트 중 하나에 *위임 호출 매핑*되어 있음 (약속 6 + PRD §6.3, 데이터 정합성)
  - [ ] 신학 결정 권한은 *0인*에게도 위임되지 않음 — 모두 "제안 → 신학 필터 → 목사 승인" 흐름 (PRD §7.3, 데이터 정합성)
  - [ ] **기획 축 작동 방식 명세 (v0.2 신설, 성찰 P2-9)**: 전략 보조 축 부교역자별로 *input → algorithm → output* 3요소 명시 의무. input 후보: 연간 사역계획·교회력·이전 주차 회의록·didim status.md 누적. algorithm: 우선순위 점수(긴급도·신학 정합·회중 영향) + 트레이드오프 표 산출. output: 결정 카드 후보 ≥ 2 (단독 결정 금지, PRD §7.3). 알고리즘 산출은 *제안*이지 *결정*이 아님.
  - [ ] **N:M 매핑 규칙 (v0.2 신설, 성찰 A-Step5)**: BL-3 결정으로 실행축 부교역자 N(가변) ↔ didim 7 매핑 시 — ① 실행축 1인 = didim 1 에이전트 *전속*(1:1) 또는 *공동*(1:M, M ≤ 2)만 허용, 1:3+ 금지(전문성 희석). ② didim 1 에이전트가 churchTeam ≥ 2인에게 분할되는 M:1 절대 금지(약속 6 didim 단일 진실 위반). ③ N < 7 시 미할당 didim은 `@didim-bridge` 직접 호출 fallback. ④ N > 7 시 초과는 *비커버 산출진*(BL-12) 슬롯으로만, didim 호출 금지. 매핑 표에 N·M·형태 명시 의무.
  - [ ] 페르소나 시뮬레이션 *대체 위험* 면책 라인 의무 동반 (C-4 🛡 안전판, source: idea §4 C-4)
  - [ ] **BL-6 위계 가시화 화면 결정 (v0.3 신설, 반영 성찰 누락 1)**: 12직 4필드 *데이터*를 사용자에게 *어느 화면*으로 노출할지 결정. 후보 ≥ 2 의무 — 예시 ① 조직도형(트리/매트릭스) ② 대화 흐름형(M3 위임·반박 시퀀스에 보고선 색조) ③ 카드형(부교역자 호출 시 직속 상관·하위 표시). 채택안 1개 + 폐기 후보 사유 1줄. 약속 4(팀 본질) 가시화 직격 (source: idea §11 BL-6 P1).
- **Task**: Finalize the 12-role pastoral team roster. Each role definition must reference both PRD §7 and the user decision from Step 3 BL-3. Map each role to one of three axes. For execution-axis roles, declare which didim agent they delegate to.
- **Output**: `Claude_skills/AI_churchteam/.claude/roster.yaml` (draft) + `Claude_skills/AI_churchteam/.claude/three-axis-mapping.md` + `Claude_skills/AI_churchteam/.claude/hierarchy-view.md` (v0.5 P0-1② — BL-6 위계 가시화 채택 화면 1종 + 폐기 후보 사유 1줄 의무)
- **Translation**: `@translator` → `three-axis-mapping.ko.md`
- **Review**: `@reviewer + @fact-checker + @theological-reviewer`

### 6. didim 페어링 인터페이스 + 이중 SOT 페어링 정책 확정 (BL-2, B-1, BL-7 결합 산출)
- **Agent**: `@didim-bridge-architect` (Opus)
- **사실 정정 (v0.2)**: didim은 *독립 CLI가 아니라 슬래시 커맨드 시스템*(`/주간총괄`·`/주간현황`·`/설교` 등). 따라서 Wrapper의 *호출 모드*는 다음 3가지 중 결정 의무: **CM-1** headless Claude 세션 spawn (`claude -p "/주간현황"`) / **CM-2** didim 산출 폴더 직접 Read·Write (`Claude_skills/weekly-works/output/{월}/{주차}/`) + status.md 포인터 갱신 / **CM-3** 사용자 본 Claude 세션에 슬래시 위임 안내(코드 미실행, 사용자가 수동 호출).
- **Verification**:
  - [ ] B-3 단방향 포인터 골격 + 채택된 읽기 채널(RC-α/β/γ 중 1) 결합 형태가 약속 6 위반 위험 ✅ (데이터 정합성)
  - [ ] **B-π P-γ(역방향 캐시) 폐기 명문화 (v0.3, idea §3 B-π)**: churchTeam SOT가 didim status.md를 *역방향 캐시*하는 안은 **채택 불가** — 약속 6·PRD §11.5 정면 충돌. `dual-sot-pairing-policy.md`에 폐기 라인 1줄 의무 기록.
  - [ ] **호출 모드 CM-1/CM-2/CM-3 중 채택안 명시** + 비채택안의 폐기 사유 1줄 (의사결정 추적성)
  - [ ] B-1 사전 검증 *실측 명령*: 채택 모드별로 — CM-1 = `claude -p "/주간현황" --dry-run` 1회 실행 / CM-2 = `Claude_skills/weekly-works/output/` 하위 status.md 기존 파일 1개 Read 후 스키마 파싱 / CM-3 = 사용자 안내 카드 렌더 1회. 결과(통과/무시/오류) → SOT 기록.
  - [ ] B-1 결과에 따른 *분기 설계* 명시 + 재검증 트리거(주기·didim 버전 변경 감지: `Claude_skills/weekly-works/CLAUDE.md` SHA 변경) 포함 (BL-10 ④)
  - [ ] D-5 fallback 발행 정책: *발행 차단 + 회복 대기 기본값 ON* / *캐시 노출 기본값 OFF* (source: idea §5 D-5 v0.3)
  - [ ] D-4 self-lock 회수 정책: 결정된 후보 ≥ 1 + crash 마커·이중 heartbeat·사용자 1동작 회수 중 결합 형태 명시
  - [ ] PRD §11.5 진실 페어링 규약(churchTeam SOT는 didim 포인터·해시만, 역방향 복제 금지) 코드 강제 가능한 형태로 명세
  - [ ] **dual_sot_pairing_guard 알고리즘 명세 (v0.2, P1)**: 결정적 복제 탐지 규칙 — ① didim status.md *예약 키 화이트리스트*(`current_phase`·`step_status`·`output_paths`·`agent_progress`·`error_state`·`next_action`) 중 어느 키든 churchTeam state.yaml에 존재하면 violation. ② 역방향 동일 검사. ③ 위반 시 `exit 2` + 한국어 4줄(어느 키·어느 파일·복원 1동작·재발 방지). ④ **B-π P-β 동시 갱신 차단 (v0.3 신설)**: 동일 사이클 ID(`weekly_cycle.current_id`)에 대해 churchTeam SOT와 didim status.md가 *60초 이내 동시 갱신* 탐지 시 → 한국어 1줄 신호 + 산출진 추가 호출 *명시 차단* (idea §3 B-π P-β). 차단 해제는 사용자 `/팀-동시갱신-회수` 카드 통과로만. 화이트리스트 키 목록 정본은 Step 6 Output `dual-sot-pairing-policy.md`에 명세.
  - [ ] **didim 입력 주입 메커니즘 명세** (약속 6 후반부): churchTeam의 통찰·기획 산출이 didim sermon 4단계 흐름에 *어떻게* 추가 입력되는가 — 구체 경로는 `Claude_skills/weekly-works/output/{월}/{주차}/설교/sermon-context.md` *사전 작성*이며, churchTeam이 이 파일을 *추가 섹션 append-only*로 갱신(기존 didim 작성 섹션 미수정).
- **Task**: Specify the exact form of: (a) `@didim-bridge` wrapper agent contract with chosen invocation mode (CM-1/2/3), (b) actual invocation command/Read pattern per chosen mode, (c) churchTeam SOT ↔ didim status.md cross-conflict signal Korean 1-line, (d) self-lock recovery policy and Korean 1-action recovery trigger, (e) D-5 fallback last-resort alert channel(s) (BL-10 ②), (f) **sermon-context.md append-only injection contract** (which sections churchTeam may add, which are reserved for didim).
- **Output**: `Claude_skills/AI_churchteam/.claude/didim-bridge-spec.md` + `Claude_skills/AI_churchteam/.claude/dual-sot-pairing-policy.md`
- **Translation**: `@translator` → both `.ko.md` 변형
- **Review**: `@reviewer` (페어링 일관성) + `@fact-checker` (didim source 정합성)

### 7. (human) 설계도 본문 진입 허가 — Implementation 봉인 해제
- **Action**: Review Steps 4-6 outputs as a unified packet. Confirm: (a) all 9 entry gates resolved, (b) all 6 ancillary BLs decided, (c) PRD/idea diffs acceptable, (d) 12-role roster + 3-axis mapping coherent with §0.1, (e) didim pairing preserves 약속 6, (f) §11.5 dual-SOT policy enforceable, **(g) (v0.5 P0-1 ③) BL-9 D-2 자동 끊김 사전 합의 카드 서명 — *0회차 1회 의무***: 본 카드는 "D-2 영적 검토 카드 3노드(4.5 제목 게이트·신학 필터 FAIL·외부 발행 직전)에서 자동 흐름이 *설계상* 끊긴다"는 사실을 사용자가 *사전에 인지·동의*한다는 한국어 4줄 합의 라인을 포함. 서명 결과는 `pastoral-decision-logs/BL-9-d2-consent-{YYYY-MM-DD}.md`에 영구 보관 + `state.yaml.ancillary_BLs.BL-9.consent_signed_at` 기록. 미서명 시 Implementation Phase 봉인 해제 차단(idea §11 BL-9 + v0.4 헤더 ③ 약속 본문 반영). Sign Korean decision card `/팀-진입허가` to unseal Implementation Phase.
- **Command**: `/팀-진입허가` (BL-9 합의 항목 통합 — 별도 슬래시 미생성, 단일 진입점 약속 4 정합)
- **Block 조건**: 어느 하나라도 ❌ → Step 2 또는 Step 3로 자동 회귀 + 사유 한국어 카드. **BL-9 합의 미서명도 ❌ 처리**.

---

## Implementation

> 목적: PRD §11.1.c "끝까지" 5단계(① 설치 ② 일상 운용 ③ SPOF 자가 복구 ④ 자기 진화 ⑤ 재해 복구)를 단일 메타빌드 경로로 실현. Phase 0 → Phase 1 → Phase 2 단계적 도입. 본 Phase는 Step 7 진입 허가 카드가 SOT에 기록된 후에만 활성.

### 7.5 (사용자 안내) Bootstrap-of-Bootstrap — Python·필수 의존성 사전 점검 (v0.2 신설)
- **사유**: Step 8 setup_init 자체가 Python 스크립트. Python 미설치 시 hook 실행 불가 → 진입 불능.
- **Action**: `which python3 && python3 -c "import sys; assert sys.version_info >= (3,12)"` 결과 한국어 카드 4줄로 표시. 미설치 시 *코드 미실행 안내*만 — "사용자가 다음 1줄을 터미널에 직접 입력해 주세요: `brew install python@3.12`" (절대 기준 1: 자동 설치는 PRD §11.4 정책 결정 후, 약속 1 무코드 — 안내선까지). Node.js·uv·nlm 도달성도 동일 패턴.
- **출력**: `pastoral-decision-logs/bootstrap-prereq-{YYYY-MM-DD}.md` (검증 결과 + 사용자 행동 기록)
- **Block**: 어느 의존성이라도 `❌` → Step 8 진입 차단.

### 8. (hook) Bootstrap 사전 인프라 검증 — `setup_init`
- **Hook 이벤트**: `Setup` (matcher: `init`)
- **검증 항목**:
  1. 부모 게놈 위치 해석 가능(`AgenticWorkflow-Template/` 경로 환경변수 단일 출처, A-3 참조-증명)
  2. didim 게놈 도달성(`Claude_skills/weekly-works/CLAUDE.md` + 7 에이전트 source 모두 존재, PRD §11.4 ⑥)
  3. macOS 로컬 환경 + Python 3.12+ + Node.js + uv tool + nlm + yt-dlp 설치 검증 (Q6 자동 설치 가능성 결정 결과 반영)
  4. `Claude_skills/AI_churchteam/.claude/state.yaml` 부트스트랩 슬롯 ≥ 100B
  5. `runtime_directories/`(verification-logs·pacs-logs·review-logs·pastoral-decision-logs·translations·inheritance-manifest·dual-sot-snapshots) 전부 mkdir -p
  6. 네트워크 연결(C-9 명시 예외 — 초기 설치 한정)
- **Exit Code 규칙**: 6항 중 1개라도 실패 → `exit 2` + 한국어 4줄 복구 안내(C-3 패턴) → Bootstrap 차단.

### 9. Phase 0 — Bootstrap (0회차 진입 + DNA 상속 + 단일 슬래시 등록)

> **v0.2 분기 설계**: BL-5 결정 결과(0회차 진입 행위자)에 따라 본 단계는 다음 3 서브 시나리오 중 *하나*로만 활성화된다. 다른 두 시나리오는 *비활성*. Step 7 진입 허가 카드가 BL-5 채택안을 명시 기록.
>
> - **9a — 셸 1줄 시나리오** (BL-5 = 사용자/Claude Code 셸): `bash <(curl -fsSL ...)` 또는 로컬 `bash bootstrap.sh` 1줄. stdout 한국어 진척 노출.
> - **9b — Claude Code 슬래시 시나리오** (BL-5 = 기존 Claude 세션 내 진입): `/팀-부트스트랩` 1회 호출. 부모 세션의 Bash·Write tool로 인스턴스 생성.
> - **9c — GUI 트리거 시나리오** (BL-5 = 비개발자 친화 GUI): macOS Automator/AppleScript 더블클릭 → 내부적으로 9a 또는 9b 호출.
>
> 모든 시나리오 공통: A-2 거부 게이트·A-3 매니페스트·A-4 단일 슬래시 등록 동일.
- **Pre-processing**: PRD `§11.1.b` 0회차 진입점 약속 + idea `A-1` (0회차 행위자 결정 결과 BL-5 반영) + A-2 PRD 스키마 검증 게이트 + A-3 참조-증명 매니페스트.
- **Agent**: `@bootstrapper` (Opus, project scope, write to `Claude_skills/AI_churchteam/`)
- **Verification**:
  - [ ] PRD 6대 절대 약속 6항 모두 인용 통과 + 누락 시 한국어 자연어 거부 메시지 출력 후 exit (A-2 거부 게이트, source: idea §2)
  - [ ] inheritance-manifest.json 생성 — 부모 게놈 SHA + 7 DNA 요소(헌법·구조·검증·안전·기억·비판·투명) 매핑 + didim 게놈 SHA 포함 (source: idea §2 A-3)
  - [ ] 단일 슬래시 `/팀` 1개 등록 (그 외 12직·DAG·hook 전체 설치 *금지* — 지연 빌드, source: idea §2 A-4)
  - [ ] FR-22 자가 검증 화면이 inheritance-manifest를 한국어로 렌더링 가능
  - [ ] 0회차 진입 *진척*이 한국어 자연어로 노출 (시나리오 9a stdout / 9b Claude 응답 / 9c GUI 모달 — PRD §11.1.b)
  - [ ] BL-5 결정된 0회차 행위자 + 채택 시나리오(9a/9b/9c)가 약속 1과 정합
- **Task**: Execute the single-shell-line bootstrap: (a) parse parent-genome path from env single-source, (b) parse PRD v0.6 (or v0.5 if user skipped Step 4 diff), (c) verify 6 mandatory metadata fields, (d) copy/reference DNA inheritance manifest into child instance SOT, (e) register single slash command `/팀`, (f) terminate. Lazy-build everything else.
- **Output**: `Claude_skills/AI_churchteam/.claude/inheritance-manifest.json` + `Claude_skills/AI_churchteam/.claude/commands/팀.md` + `Claude_skills/AI_churchteam/.claude/state.yaml` (자식 SOT 초기 슬롯 — 스키마는 §SOT *자식 스키마* 표 참조, v0.2 신설)
- **Translation**: none (실행 산출물)
- **Review**: `@reviewer` (DNA 상속 정합성)
- **Post-processing**: `validate_workflow.py --check-genome-inheritance` (W1-W8 모두 통과)
- **제1 목적 연결**: 약속 2(메타빌드) + 약속 4(팀 본질 단일 진입점) — 비개발자 담임목사가 *팀*을 처음 만나는 지점.

### 10. Phase 1 — Core 부교역자 3~5인 활성화 + 3-Door UX + 2중 신학 필터 + HITL 영적 검토 카드 + didim Wrapper
- **Pre-processing**: Step 5 roster.yaml에서 *Phase 1 핵심* 표시된 3~5직만 추출 (BL-3 결정 결과). 나머지는 `placeholder` 유지.
- **Agent**: `@phase1-builder` (Opus)
- **Verification**:
  - [ ] 3~5인 부교역자 source 파일 생성 + 각자 PRD §7.1 4필드(직무명·사명·권한·보고선) 보유 (구조적 완전성)
  - [ ] 사고·전략·실행 3축 *최소 1인씩* 매핑 충족 (PRD §6.4)
  - [ ] 신학 필터 1차(`@theological-reviewer` LLM 의미론) + 2차(`theology_filter_dual.py` 결정적: 금칙어·인용 성구 ↔ SOT 본문 해시·금지 출처 화이트리스트) 양 끝 배치 (D-1, source: idea §5)
  - [ ] **신학 시드 공급 절차 (v0.2)**: 결정적 2차 필터의 *초기 시드*(금칙어·금지 도메인 화이트리스트·회귀 케이스 ≥ 20)는 *목회자 승인 카드 통과 후* 부모 게놈 또는 외부 신학 자료에서 import. 시스템 단독 합성 절대 금지(PRD §9.1 v0.5). 시드 출처 후보: ① 개혁주의 표준문서(WCF·하이델베르크) 인용 화이트리스트 ② 한국 공교회 합의 이단 식별 자료 ③ 목회자 자유 지정. 시드 미공급 시 필터는 *통과만* + FR-22 `신학 필터` 신호 ⚠ 표시.
  - [ ] **didim 입력 주입 활성 — BL-2 채택안 의존 분기 (v0.3, P1)**: Step 6에서 채택된 읽기 채널(RC-α/β/γ) 결과에 따라 *조건부 활성*. (a) **RC-β(B-2 한정 — 파일 드롭) 채택 시**: 통찰·기획 부교역자 산출 → `Claude_skills/weekly-works/output/{월}/{주차}/설교/sermon-context.md` *append-only* 섹션(`## churchTeam 통찰`·`## churchTeam 기획`) 사전 작성, didim sermon agent가 4단계에서 본 섹션 읽기, churchTeam은 didim 작성 섹션 미수정. (b) **RC-α(Wrapper 변환) 채택 시**: `@didim-bridge`가 churchTeam SOT를 didim 입력 포맷으로 *변환만* 수행 — sermon-context.md 직접 작성 금지. (c) **RC-γ(비차단 hook) 채택 시**: PreToolUse hook이 didim 호출 직전 *입력 첨부만*, sermon-context.md 직접 작성 금지. **BL-2 미결정 또는 RC 미채택 상태에서는 Phase 1 본 단계 *기본값 = B-2/B-5 미사용*(idea §7 권고)** — 어느 채널도 활성화되지 않은 채로 Step 11 시연 진입 차단.
  - [ ] HITL 영적 검토 카드 3노드 의무 활성화 — 4.5 제목 게이트, 신학 필터 FAIL, 외부 발행 직전 (D-2)
  - [ ] 영적 검토 카드 응답이 SOT `pastoral-decision-logs/`에 누적되어 다음 주차 회귀 케이스 후보로 전환 (PRD §9.1 v0.5 회귀 케이스 작성 주체 약속 — 시스템 단독 합성 금지)
  - [ ] 3-Door 한국어 분기 (`① 팀 회의 (M1)` `② 한 사람 부르기 (M2)` `③ 위임·반박 보기 (M3)`) + BL-1 결정된 3축 매핑 결합 (치환 vs 직교 6칸)
  - [ ] **C-1 내부 ID·플래그 비노출 (v0.3 신설, 성찰 B2-부분반영-2)**: 사용자 가시 텍스트(3-Door·부교역자 호출·에러·진척 라인)에 내부 agent 이름(`phase1-builder` 등)·플래그(`--scope`·`permissionMode`)·내부 경로 노출 금지. 한국어 호칭만 허용. `output_internal_id_filter.py`(신규 PostToolUse hook)가 영문 식별자 패턴 탐지 시 한국어 호칭으로 자동 치환 또는 ⚠ 경고. idea §4 C-1 "이름표만, 내부 ID 비노출" literal 반영.
  - [ ] `@didim-bridge` wrapper 활성 — Step 6 페어링 정책 준수, didim CLI 인자 호환성 검증 결과(B-1) 반영
  - [ ] FR-22 6칸 자가 검증 카드 가시화 + 종합 한 단어("사역 가능/일부 점검/중단") 산출 (BL-13 결정 결과 반영)
  - [ ] 부교역자 첫 등장 화면 + 모든 외부 산출 푸터에 "AI 도우미 / 신학 최종 권자 = 담임목사" 면책 라인 (C-4 🛡 안전판)
  - [ ] **C-4 입장 연출 스트리밍 (v0.3 신설, idea §4 C-4)**: M1 팀 소환 시 응답 직전 부교역자별 한국어 입장 라인 순차 스트리밍 — `"{호칭}이 자리에 앉습니다…"`. M2는 호명 1인만, 나머지 `"대기 중"`. M3 위임·반박은 두 부교역자 한국어 대화 형식(이름표 부착). 첫 발화 1줄 페르소나·발언 색조. 스트리밍이라 실제 지연 0.
  - [ ] **§1.bis Phase 1 미사용 기본값 강제 (v0.3)**: B-2/B-5 도입 차단 — `validate_workflow.py --check-promise-6-literal` PASS 의무.
  - [ ] 모든 한국어 에러 메시지 = 4줄 패턴 (C-3, source: idea §4)
- **Task**: Lazy-build the Phase 1 surface: (a) 3-5 pastoral agent source files under `Claude_skills/AI_churchteam/.claude/agents/`, (b) `theology_filter_dual.py` hook with deterministic 2nd-stage rules, (c) `@theological-reviewer` LLM 1st-stage filter, (d) HITL spiritual review card UI rendering, (e) `@didim-bridge` wrapper invoking didim's 7 agents per Step 6 spec, (f) FR-22 6-card health dashboard renderer, (g) C-3 4-line Korean error envelope. **Persona theatrics (C-4 입장 연출) ARE included** but with 🛡 면책 안전판 mandatory.
- **Output**: `Claude_skills/AI_churchteam/.claude/agents/{phase1-roster}.md` × 3-5 + `Claude_skills/AI_churchteam/.claude/hooks/scripts/theology_filter_dual.py` + `Claude_skills/AI_churchteam/.claude/hooks/scripts/dual_sot_pairing_guard.py` + `Claude_skills/AI_churchteam/.claude/skills/health-dashboard/` + `Claude_skills/AI_churchteam/.claude/agents/didim-bridge.md`
- **Translation**: `@translator` → 모든 사용자 가시 텍스트 한국어 (시스템 프롬프트 영어, 사용자 인터페이스 한국어 — PRD FR-07)
- **Review**: `@reviewer + @fact-checker + @theological-reviewer` (3종 적대적)
- **Post-processing**: `validate_domain_knowledge.py --domain theology` (DK1-DK7) + `validate_pacs.py` + 신학 필터 회귀 셋 ≥ 20개 누적 확인 (PRD §9.1)
- **신학 회귀 시드 공급 절차 (v0.2 신설, P2)**:
  1. 시드 후보 출처 — 부모 게놈 `prompt/ai_pastoral_prompts/`의 *이단 표현·잘못된 인용·금지 출처* 케이스 ≥ 20건 사전 큐레이션.
  2. 목회자 1회 검토 카드 (`/팀-신학시드`) — 각 케이스 ✅(채택) / ⚠(수정) / ❌(폐기) 응답.
  3. 채택분만 `Claude_skills/AI_churchteam/.claude/skills/theology_filter_dual/regression-seed/{YYYY-MM-DD}.yaml`로 기록 + `theology_filter_dual.py` 2차 필터 금칙어·도메인 화이트리스트 초기 시드 로드.
  4. **시스템 단독 합성 금지 (PRD §9.1 v0.5)** — 본 절차 전에는 결정적 2차 단계가 *경고만 발행*, 차단 미수행. 시드 ≥ 20개 충족 후 차단 활성.
- **데이터 프라이버시 (v0.2 신설, P2)**: `pastoral-decision-logs/`는 영적 분별 포함 → ① local-only(`.gitignore`로 원격 push 금지) ② `age` 또는 macOS Keychain 암호화 후 외부 백업 ③ 회중 식별 정보 자동 마스킹 PreToolUse hook(`pastoral_log_pii_mask.py`).

### 11. Phase 1 일상 운용 — 1주 사역 사이클 시연 (PRD §6.5)
- **Pre-processing**: PRD §6.5 시간선 표(주일~토 7요일별 활성 축)를 churchTeam 사이클 ID에 매핑. didim status.md 포인터 갱신. **시연 주차 ID 사전 결정**: BL-3 결정 카드에 시연 주차 필드 추가 (`sermon-plan-2026.json`의 어느 주차) — 미결정 시 Step 11 진입 차단.
- **Agent**: `@weekly-cycle-orchestrator` (Sonnet, project scope)
- **Verification**:
  - [ ] 7요일 각 단계에서 *활성 축 부교역자가 호출*되었음을 SOT 로그가 입증 (FR-24 시연 가능)
  - [ ] 금~토 산출진 가동 구간에 didim 7 에이전트가 위임 호출되며 *churchTeam SOT가 didim 필드를 복제하지 않음* (PRD §11.5 페어링 규약, 데이터 정합성)
  - [ ] 4.5 제목 게이트 + 신학 필터 FAIL + 외부 발행 직전 3노드 모두에서 D-2 영적 검토 카드 발행
  - [ ] **M1·M2 두 모드** 1회 이상 사용 (Phase 1 도입 모드 — M3는 Step 13 Phase 2 도입 후 시연. v0.1 PRD FR-21 표현은 v0.2에서 *Phase별 점진* 해석으로 보강).
  - [ ] 토요일 종료 시 "오늘의 팀 회의록"(C-5) 자동 생성 + SOT 원본 무손상
  - [ ] **(v0.3, 잔여 G6) 회의록(meeting-minutes.md) 푸터에 C-4 🛡 면책 라인 의무 동반** — 운영진 ≥ 2인 공유 가능성 = Step 15 exposure-boundary.md *외부 노출로 간주* 안전 기본값 적용. 푸터 정본 = "저희는 부교역자가 아닌 AI 도우미입니다. 신학적 판단의 최종 권자는 담임목사님입니다." (idea §4 C-4 안전판 + Step 15 경계 모호성 해소)
- **Task**: Run one full weekly cycle as a smoke test. Korean cycle log mandatory. Each daily step writes to SOT only via Team Lead.
- **Output**: `Claude_skills/AI_churchteam/output/{사이클ID}/cycle-log.md` + `meeting-minutes.md` + didim 산출물 포인터
- **Translation**: `@translator` → 회의록 한국어 (이미 한국어이면 정합 검증만)
- **Review**: `@fact-checker` (신학 인용 정확성)

### 12. Phase 1 SPOF 자가 복구 — D-5 fallback 4선 + 한국어 4줄 회복
- **Agent**: `@spof-recovery` (Sonnet)
- **Verification**:
  - [ ] 4.5 잠금 후 재계획 정책 — 제목 변경 시 하위 산출물 자동 무효화 *마커* (자동 폐기 금지)
  - [ ] 외부 인증 fallback(NotebookLM/Telegram/Gmail) — 30s 백오프 3회 → 발행 차단 + 회복 대기 (캐시 노출 OFF 기본)
  - [ ] Telegram chat_id 화이트리스트 강제 + `<channel source="telegram">` 외 명령 토큰 무시 (idea §5 D-5)
  - [ ] **chat_id 저장 위치 명세 (v0.2 신설, 성찰 A-Step12)**: `.env`(키 `TELEGRAM_ALLOWED_CHATIDS`) 단일 출처. Bootstrap 시 `setup_init_churchteam.py`가 메모리 캐시로 1회 로드. `state.yaml`은 *SHA256 해시값만* 보존(평문 SOT 금지). `.gitignore` 강제. BL-11 추가/제거: 사용자 `.env` 수동 편집 → `/팀-건강` 카드가 갱신 해시 노출.
  - [ ] PreCompact ↔ SOT 동시성 — D-4 토큰 락 + crash 마커(BL-7 결정안)
  - [ ] **D-4 토큰 락 본문 스키마 (v0.3 신설, idea §5 D-4)**: SOT 파일별 lock 파일 `{path}.lock` = `{owner_agent, pid, started_at(ISO8601), heartbeat_at(ISO8601)}`. Orchestrator/Team Lead만 토큰 발급 — 병렬 에이전트 *읽기 전용*. heartbeat 30s 주기, 90s 초과 stale → Orchestrator 강제 회수 + `runtime_directories/lock-recovery.log` 기록. PreCompact는 lock 보유 시 30s 대기 후 강제 스냅샷. self-lock 회수는 BL-7 채택안; BL-7 미결 시 *crash 마커 자동 생성 + 다음 세션 한국어 안내* 임시 기본값.
  - [ ] 모든 SPOF 알림 = 한국어 4줄 패턴 (C-3) + 최후 알림 채널(BL-10 ②) 발행
  - [ ] 재시도 예산 상한 초과 시 자동 escalate 카드 (BL-10 ③, RB1-RB3)
- **Task**: Implement the 4-line SPOF fallback module. Wire to FR-22 health dashboard so degradation is visible.
- **Output**: `Claude_skills/AI_churchteam/.claude/skills/spof-recovery/`
- **Review**: `@reviewer`

### 13. Phase 2 — Hardening (D-3 자기 진화 사전 게이트 + 부교역자 추가 활성화 + 토론·반박 메커니즘)

> **(v0.3, G3) D-3 Phase 분기 단정 약화**: 본 Step의 D-3 활성화는 **BL-(vi) 결정 결과 = "Phase 2 도입"** 인 경우에 한해 유효. 사용자가 BL-(vi)에서 "Phase 1 필수"를 채택하면 D-3 게이트 활성 시점은 Step 10으로 이전되고, 본 Step 13은 부교역자 추가·토론·반박 메커니즘만 담당. idea v0.5 §6 #8·#26은 Phase 1 최소 게이트 셋을 *후속 라운드 위임*으로 보존하므로 본 워크플로우도 BL-(vi) 결정 SOT를 읽기 전까지 단정 금지.

- **Agent**: `@phase2-hardener` (Opus)
- **Verification**:
  - [ ] **(v0.3, G3) BL-(vi) D-3 Phase 분기 결정 SOT 기록 확인** — `state.yaml.entry_gates."D-3-phase".decision ∈ {"phase1", "phase2"}`. "phase1"이면 본 Step에서는 *추가 강화*만 수행, "phase2"이면 본 Step에서 신규 활성화.
  - [ ] D-3 자기 진화 사전 게이트 — LLM 자기 분류 + AST/import-graph 결정적 매처 *둘 다* 통과 (PRD §9.4 v0.5 사전 게이트 약속, 데이터 정합성)
  - [ ] **`.md` 변경 매처 동작 명세 (v0.2 신설, 성찰 A-Step13)**: churchTeam 자식 부교역자/스킬은 다수가 `.md` 정의(YAML 프론트매터 + 본문). 결정적 매처는 — ① 프론트매터 diff: `name`·`scope`·`tools`·`model`·`permissionMode`·`skills` 키 변경 시 자동 차단(자율 금지 7행 중 "외부 의존"·"DAG" 직격). ② 본문 diff: `## 권한 경계`·`## 보고선`·`## 신학 필터` 섹션 헤더 단위 변경 시 차단. ③ 화이트리스트 키/섹션 외 diff는 통과. AST 미적용 영역(.md)은 *섹션·키 단위 결정적 매처*로 대체.
  - [ ] §9.4 표 "자율 금지" 7행 모두 매처 화이트리스트에 포함 (신학 필터·sermon 시그니처·SOT 단일 쓰기자·DAG·외부 의존·부모 게놈 위반)
  - [ ] PRD diff = 자기 진화 = Bootstrap 재진입 단일 경로 (A-5)
  - [ ] 부교역자 12인 카탈로그 활성화 (Phase 1 외 7직 추가)
  - [ ] 부교역자 간 토론·반박 메커니즘(C-K, FR-19) — Phase 2 도입
  - [ ] 페르소나 시뮬레이션 *대체* 위험 면책 라인 모든 외부 산출에 보존
- **Task**: Activate D-3 self-evolution gate, expand roster to 12, add debate/rebuttal mechanism. Each diff to "자율 금지" rows triggers user approval card.
- **Output**: `Claude_skills/AI_churchteam/.claude/hooks/scripts/self_evolution_gate.py` + 추가 부교역자 source × 7
- **Review**: `@reviewer + @fact-checker + @theological-reviewer`

### 14. Phase 2 재해 복구 — BL-4 3종 시나리오 (SOT 손상·게놈 손상·전체 복원)
- **Agent**: `@disaster-recovery` (Opus)
- **Verification**:
  - [ ] SOT 손상 시나리오 — 1동작 한국어 복구 안내 ≥ 1 (Step 6 결정 결과 반영)
  - [ ] 게놈 손상 시나리오 — 부모 게놈 재상속 + manifest stale 갱신 트리거(BL-10 ①)
  - [ ] **부모 게놈 원격 백업 다중성 (v0.2 신설, 성찰 P3-12)**: 단일 macOS 로컬은 SPOF — 부모 게놈(`AgenticWorkflow-Template/`)을 ① Git remote(GitHub private repo, encrypted) ② 외부 저장소(사용자 지정 iCloud/외장 디스크) 중 *최소 1곳*에 주기 백업. `inheritance-manifest.json`에 백업 경로 + 마지막 sync timestamp + SHA 기록. 부모 게놈 손상 시 *원격 재획득 1동작 한국어 안내*(예: "git clone {URL} --depth=1 ~/Recovery") 포함. pastoral-decision-logs도 동일 백업 경로 적용(P2-10 데이터 프라이버시 결합 — Git remote는 private + 외부 저장소는 사용자 암호화 책임).
  - [ ] 전체 복원 시나리오 — Bootstrap 재진입 + DNA 매니페스트 재검증
  - [ ] 모든 복구 안내 = C-3 4줄 패턴 + FR-22 자가 검증 화면 동기 갱신
- **Task**: Implement the 3-scenario disaster recovery flows.
- **Output**: `Claude_skills/AI_churchteam/.claude/skills/disaster-recovery/`
- **Review**: `@reviewer`

### 15. (human) 시연 · 회중 노출 전 최종 검토
- **시연 대상·외부 노출 경계 정의 (v0.2 신설, 성찰 A-Step15)**: ① *내부 시연*(차단 OFF 가능) = 담임목사 1인 + 운영진 ≤ 3인 대상 화면/PDF/로컬 미리보기 — `Claude_skills/AI_churchteam/output/` 하위 머무름. ② *외부 노출*(D-2 영적 검토 카드 + `/팀-회중허가` 의무) = 회중 ≥ 1인에게 공개되는 모든 채널: 주보(인쇄·디지털 발행), SNS 카드뉴스 업로드, 설교 본문 단상 사용, 소그룹 나눔지 배포, Telegram 그룹 발송, Gmail 발송. ③ 경계 모호 시(예: 운영진 토론용 초안 공유) — *외부 노출로 간주* 안전 기본값. 본 정의는 `Claude_skills/AI_churchteam/.claude/exposure-boundary.md`에 정본 보존.
- **Action**: 1주 사역 사이클을 *실제 본문*으로 1회 완주. M1·M2·M3 모두 사용. 토요일 외부 발행 직전 영적 검토 카드 통과 후에만 회중 노출 허가. 면책 라인이 모든 외부 산출 푸터에 보이는지 확인.
- **Command**: `/팀-회중허가`
- **제1 목적 연결**: 절대 우선순위 ③(목회자 최종 검토) — 회중에게 *부정합 메시지*가 나가지 않도록 마지막 게이트.

---

## Claude Code Configuration

### Sub-agents (12직 부교역자 + 빌드/검토 에이전트)

```yaml
# .claude/agents/*.md frontmatter (예시 골격, Phase 1 활성 5직만 즉시 실체화)

# 빌드·아키텍트 에이전트 (Research/Planning Phase)
prd-reader:           {model: opus, scope: project, tools: [Read, Grep, Glob], permissionMode: plan}
gate-A-meta-build:    {model: opus, scope: project}
gate-B-pairing:       {model: opus, scope: project}
gate-C-ux:            {model: opus, scope: project}
gate-D-resilience:    {model: opus, scope: project}
meta-build-architect: {model: opus, scope: project}
team-architect:       {model: opus, scope: project}
didim-bridge-architect: {model: opus, scope: project}
bootstrapper:         {model: opus, scope: project, tools: [Read, Write, Edit, Bash]}
phase1-builder:       {model: opus, scope: project}
phase2-hardener:      {model: opus, scope: project}
weekly-cycle-orchestrator: {model: sonnet, scope: project}
spof-recovery:        {model: sonnet, scope: project}
disaster-recovery:    {model: opus, scope: project}

# 부교역자 12직 (Phase 1 핵심 3~5직 + Phase 2 추가 7직 — 정확한 셋은 BL-3 결정)
# 각 부교역자 프론트매터 공통:
#   model: sonnet (대부분) | opus (사고·전략 보조 중 신학 추론 깊이 필요한 직)
#   scope: project
#   skills: [theological-reasoning, korean-pastoral-style, sermon-structure, ...]
#   memory: project (RLM — SOT 읽기 전용)

# 적대적 검토 에이전트 (Enhanced L2 + 신학 추가)
reviewer:              {model: opus, scope: user, tools: [Read, Glob, Grep]}
fact-checker:          {model: opus, scope: user, tools: [Read, Glob, Grep, WebSearch, WebFetch]}
theological-reviewer:  {model: opus, scope: project, skills: [reformed-theology, biblical-hermeneutics]}

# 번역 에이전트
translator:            {model: sonnet, scope: project, tools: [Read, Write, Glob, Grep, Edit]}

# didim 페어링
didim-bridge:          {model: sonnet, scope: project, tools: [Read, Write, Bash]}
```

> **모델 선택 근거 (절대 기준 1)**: 신학 추론·메타빌드·자기 진화 게이트는 *Opus 의무*. 회기적 산출(주간 사이클·SPOF 복구)은 Sonnet으로 충분. Haiku는 본 워크플로우에서 *사용 안 함* — 영적 사역의 본질 영역에는 충분 품질 기준 미달.

### Agent Team

```markdown
### entry-gate-resolution-team (Step 2)
- Team Lead: Orchestrator (parent session)
- Teammates: @gate-A-meta-build, @gate-B-pairing, @gate-C-ux, @gate-D-resilience
- Lifecycle: Step-scoped (Step 2 시작 시 TeamCreate, 완료 시 TeamDelete)
- SOT 쓰기: Team Lead만. 각 teammate는 `gate-resolutions/{A,B,C,D}.md` 산출물만 생성.
- Checkpoint Pattern: dense (각 teammate 평균 12+ 턴 예상 — BL ≥ 4건씩 처리)
```

### SOT (상태 관리)

- **SOT 파일**: `Claude_skills/AI_churchteam/.claude/state.yaml` (workflow 자체) + `prompt/workflow-research/state.yaml` (본 설계 진행 상태)
- **쓰기 권한**: Orchestrator (본 workflow 실행자) + `@team-lead` (자식 churchTeam 운용 시)
- **에이전트 접근**: 읽기 전용 + 자기 출력 폴더만 쓰기
- **이중 SOT 페어링 (PRD §11.5)**:
  - churchTeam SOT = 통찰·전략·승인 흐름 진실
  - didim status.md = 실행 산출물 진척 진실
  - churchTeam SOT는 didim 포인터·해시만 보유. **didim 필드 churchTeam SOT 복제 절대 금지**.
  - `dual_sot_pairing_guard.py` Hook이 PostToolUse(Write|Edit, churchTeam state.yaml 매처 한정)에서 위반 자동 차단 (exit 2)
  - **복제 탐지 알고리즘 (v0.2)**: 가드는 churchTeam `state.yaml`을 파싱하여 다음 *복제 금지 키 목록*과 매칭 — `sermon.outline`·`sermon.title`·`devotion.day_N.body`·`prayer.card_text`·`small_group.questions`·`sns.cards[*].body`·`weekly_status.completed_steps`. 이들은 didim 산출 폴더의 *진실 영역*. churchTeam SOT에서 발견 시 exit 2 + 한국어 4줄. *허용 키*는 didim 포인터(`didim_pointer.path`·`didim_pointer.sha`·`didim_pointer.last_seen`)만.
- **품질 우선 조정**: Step 2 Agent Team이 진입 게이트 9종을 *서로 다른 도메인*으로 병렬 처리 — 단일 에이전트 순차 대비 품질 우위(독립 컨텍스트 100% 집중). SOT는 Team Lead 단일 쓰기로 정합성 보장.

#### state.yaml 스키마 (workflow 자체)

```yaml
workflow:
  name: "churchTeam-meta-build"
  version: "0.1"
  current_step: 1
  status: "research"  # research | planning | implementation_phase0 | implementation_phase1 | implementation_phase2 | maintenance
  parent_genome:
    source: "AgenticWorkflow-Template/"
    version: "2026-05-04"
    sha: "<computed at Step 1>"
  didim_genome:
    source: "Claude_skills/weekly-works/CLAUDE.md"
    agents: ["team-leader", "sermon", "weekly-devotion", "insert-images", "prayer-doc", "small-group", "sns-cardnews"]
    sha: "<computed at Step 1>"
    address_anchor_env: "DIDIM_ROOT"  # PRD §11.1.a 주소 안정성 약속
  outputs: {}
  active_team: null
  completed_teams: []
  entry_gates:  # v0.3 G5 — done_criterion / output_artifact / close_signal 3필드 추가 (유지보수 추적성)
    BL-1:      {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-2:      {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    B-1:       {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-7:      {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-4:      {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    D-3-phase: {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-12:     {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-13:     {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    BL-10:     {status: "pending", decision: null, done_criterion: null, output_artifact: null, close_signal: null}
    # 필드 정의: done_criterion = BL 닫힘 정의문(idea §11 v0.5 인용). output_artifact = 닫힘 산출 파일 경로.
    # close_signal = 사용자가 1초 안에 가독 가능한 한국어 신호(예: "✅ BL-1 결정 카드 통과 — 3축 매핑 확정").
  ancillary_BLs:
    BL-5: {status: "pending"}
    BL-8: {status: "pending"}
    BL-9: {status: "pending"}
    BL-3: {status: "pending"}
    BL-6: {status: "pending"}
    BL-11: {status: "pending"}
  phase1_minimum_set:  # v0.3 신설 (성찰 B2-부분반영-3, idea §6 #26)
    # D-1~D-5 중 Phase 1 시연 진입 시 *반드시* 활성화되어야 하는 최소 게이트 셋.
    # BL-3 결정 카드에서 사용자가 ≥ 1개 명시. 미결정 시 Step 10 진입 차단.
    decided_set: null    # 예: ["D-1", "D-2"] — D-3은 BL-(vi) 결정에 따라 별도
    decision_card_ref: null   # pastoral-decision-logs/{파일명}
    minimum_required: ["D-1", "D-2"]   # 신학 필터 + 영적 검토 카드는 *항상 권장 기본값*
  pacs_log_dir: "pacs-logs/"
  pastoral_decision_log_dir: "pastoral-decision-logs/"
```

#### state.yaml 스키마 (자식 churchTeam 인스턴스 — v0.2 신설, 성찰 A-Step9)

```yaml
# Claude_skills/AI_churchteam/.claude/state.yaml
churchteam:
  version: "0.1"
  inheritance:
    parent_genome_sha: "<from inheritance-manifest.json>"
    didim_genome_sha: "<from inheritance-manifest.json>"
    last_validated: "<ISO8601>"
  active_phase: "phase0"  # phase0 | phase1 | phase2
  roster:                  # Step 5 산출 — Phase 1만 active, 나머지 placeholder
    - {role_id, axis, didim_delegate, status: "active|placeholder"}
  cycle:                   # 현재 주간 사이클
    cycle_id: "<YYYY-WW>"
    current_day: "월~토 한글"
    active_axis: "통찰|기획|실행"
    didim_pointer:
      path: "Claude_skills/weekly-works/output/{월}/{주차}/"
      sha: "<status.md hash>"
      last_seen: "<ISO8601>"
  health_signals:          # FR-22 6종 — 해시·라벨만, 산출물 본문 복제 금지
    dna_inheritance: "✅|⚠|❌"
    sot_integrity: "✅|⚠|❌"
    theology_filter: "✅|⚠|❌"
    external_auth: "✅|⚠|❌"
    self_evolution_ledger: "✅|⚠|❌"
    didim_reachability: "✅|⚠|❌"
    composite: "사역 가능|일부 점검|중단"
  external_secrets:        # 평문 금지 — 해시만
    telegram_chatid_hash: "<sha256>"
  last_user_card: "<pastoral-decision-logs/ 최근 결정 파일명>"
  retry_budgets:           # BL-10 ③ RB1-RB3
    theology_filter_loop: {used: 0, max: 5}
    didim_bridge: {used: 0, max: 3}
    external_auth: {used: 0, max: 3}
```

> **자식 SOT의 *복제 금지 키*** (dual_sot_pairing_guard 매처 정본): `sermon.outline`·`sermon.title`·`devotion.day_N.body`·`prayer.card_text`·`small_group.questions`·`sns.cards[*].body`·`weekly_status.completed_steps`. 이 키들은 didim 진실 영역으로 자식 SOT에 절대 등장 금지.

#### 자식 SOT 스키마 (`Claude_skills/AI_churchteam/.claude/state.yaml`, v0.2 신설)

```yaml
churchteam:
  version: "0.1"
  bootstrap_scenario: null      # 9a | 9b | 9c (BL-5 결정 결과)
  inheritance_manifest_sha: null
  active_phase: "phase0"
  roster:
    insight: []
    strategy: []
    execution: []
  didim_pointer:
    path: "Claude_skills/weekly-works/output/{월}/{주차}/"
    status_md_sha: null
    last_seen: null
  weekly_cycle:
    current_id: null
    active_axis: null
  health_signals:
    dna_inheritance: null
    sot_integrity: null
    theology_filter: null
    external_auth: null
    self_evolution_history: null
    didim_reachability: null
    overall: null               # "사역 가능" | "일부 점검" | "중단"
  pastoral_decisions: []
```

> **복제 금지 보증**: didim 진실 영역 키(sermon body·devotion text 등) 부재. `dual_sot_pairing_guard.py`가 외부 추가 시 차단.

### Hooks

```json
{
  "hooks": {
    "Setup": [
      {"matcher": "init", "hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/setup_init_churchteam.py", "timeout": 60}]}
    ],
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/block_destructive_commands.py", "timeout": 5}]}
    ],
    "PostToolUse": [
      {"matcher": "Edit|Write(Claude_skills/AI_churchteam/.claude/state.yaml)", "hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/dual_sot_pairing_guard.py", "timeout": 10}]},
      {"matcher": "Edit|Write(Claude_skills/AI_churchteam/output/**/*.md)", "hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/theology_filter_dual.py --stage deterministic", "timeout": 30}]},
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/output_secret_filter.py", "timeout": 10}]}
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/generate_context_summary.py", "timeout": 30}]}
    ],
    "PreCompact": [
      {"hooks": [{"type": "command", "command": "python3 .claude/hooks/scripts/save_context.py --before-compact", "timeout": 30}]}
    ]
  }
}
```

> **신규 hook 3종**: `setup_init_churchteam.py`, `dual_sot_pairing_guard.py`, `theology_filter_dual.py`. 나머지는 부모 게놈 상속.

### Slash Commands

```markdown
/팀                    → 단일 진입점. 3-Door 한국어 분기 (M1 회의 / M2 부르기 / M3 위임·반박)
/팀-결정               → Step 3 사용자 결정 카드 표시 + 응답 누적
/팀-진입허가           → Step 7 Implementation 봉인 해제
/팀-회중허가           → Step 15 회중 노출 전 최종 검토
/팀-건강               → FR-22 6칸 자가 검증 카드 즉시 표시
/팀-lock-회수          → BL-7 결정 결과 반영 — self-lock 사용자 1동작 회수 (idea §5 D-4)
/팀-회복               → SPOF/재해 복구 1동작 안내 (C-3 4줄)
/팀-동시갱신-회수      → B-π P-β 동시 갱신 차단 해제 (v0.3, dual_sot_pairing_guard ④)
```

### Required Skills

- `theological-reasoning` — 개혁주의 신학 추론 (`@theological-reviewer` 주입)
- `biblical-hermeneutics` — 본문 해석 원칙
- `korean-pastoral-style` — 한국어 목회 문체 (모든 부교역자 주입)
- `sermon-structure` — 설교 구조 (실행 보조 축 부교역자)
- `health-dashboard` — FR-22 6칸 카드 렌더링
- `spof-recovery` — C-3 4줄 패턴 + D-5 fallback
- `disaster-recovery` — BL-4 3종 시나리오
- 부모 상속: `tdd-workflow`, `verification-loop`, `iterative-retrieval`, `code-tour`, `agentic-engineering`

### MCP Servers

- **NotebookLM MCP** — 리서치 단계 (PRD §6.1 사고 보조 축에서 활용 가능). Bootstrap 시점 인증 1회.
- **Telegram MCP** (`@kyle_cc_bot`) — 외부 알림 채널 (BL-10 ② 최후 알림 후보). 화이트리스트 chat_id만, `<channel source="telegram">` 태그 외 명령 토큰 무시.
- **context7 MCP** — 라이브러리·API 문서 조회 (Phase 0 Bootstrap 시점 의존성 검증).
- **Gmail MCP** (선택) — D-5 fallback 발행 채널.

### Runtime Directories

```yaml
runtime_directories:
  verification-logs/:           # L1 검증 결과 (step-N-verify.md)
  pacs-logs/:                   # pACS 자체 신뢰 평가 (step-N-pacs.md)
  review-logs/:                 # @reviewer + @fact-checker + @theological-reviewer 적대적 결과
  translations/:                # @translator 산출물 (.ko.md) + glossary.yaml
  pastoral-decision-logs/:      # D-2 영적 검토 카드 누적 (시스템 단독 합성 금지 — 회귀 케이스 후보)
  inheritance-manifest/:        # A-3 참조-증명 매니페스트 (부모 + didim SHA)
  dual-sot-snapshots/:          # PRD §11.5 페어링 검증용 스냅샷 (PreCompact + 토요일 사이클 종료)
  workflow-research/:           # Step 1·2 Research 산출물
  Claude_skills/AI_churchteam/output/{사이클ID}/:  # 주간 사역 사이클 산출물
```

> **gitignore 권장**: `verification-logs/`, `pacs-logs/`, `review-logs/`, `dual-sot-snapshots/`. `pastoral-decision-logs/`는 *commit 권장* — 회귀 케이스 진실 원천.
>
> **백업·프라이버시 (v0.2)**: `pastoral-decision-logs/`는 목회자 분별 기록 = 민감 데이터. 외부 백업 시 ① Git private remote ② 외부 스토리지(Drive/Dropbox)에 *암호화 후 업로드*(예: `age` 또는 macOS `security cms`) 권장. 평문 외부 노출 금지. 백업 정책 결정은 BL-3 결정 카드에 추가.

### Error Handling

```yaml
error_handling:
  on_agent_failure:
    action: retry_with_feedback
    max_attempts: 3
    escalation: human_korean_4line_card  # C-3 패턴
  on_validation_failure:
    action: retry_or_rollback
    retry_with_feedback: true
    rollback_after: 3
  on_theology_filter_fail:
    action: spiritual_review_card        # D-2 영적 검토 카드 즉시 발행
    auto_block_publish: true             # 외부 노출 차단
  on_dual_sot_pairing_violation:
    action: block_and_alert              # exit 2 + 한국어 4줄 + FR-22 신호 갱신
  on_didim_bridge_failure:
    action: cli_arg_recheck              # B-1 재검증 트리거 (BL-10 ④)
  on_self_lock_stale:
    action: crash_marker_then_user_recovery  # BL-7 결정안 — /팀-lock-회수
  on_external_auth_expire:
    action: block_publish_wait_recovery  # D-5 v0.3 — 발행 차단 ON, 캐시 OFF
    backoff: [30, 30, 30]                # 3회 백오프
    last_resort_alert: telegram_or_macos_notification  # BL-10 ②
  on_retry_budget_exceed:
    action: auto_escalate_card           # BL-10 ③ RB1-RB3
  on_context_overflow:
    action: save_and_recover             # 부모 Context Preservation 상속
  on_teammate_failure:
    attempt_1: retry_same_agent
    attempt_2: replace_with_upgrade      # sonnet → opus
    attempt_3: human_escalation
```

### pACS Logs

```yaml
pacs_logging:
  log_directory: "pacs-logs/"
  log_format: "step-{N}-pacs.md"
  translation_log_format: "step-{N}-translation-pacs.md"
  dimensions: [F, C, L]
  translation_dimensions: [Ft, Ct, Nt]
  scoring: "min-score"
  triggers:
    GREEN: "≥ 70 → auto-proceed (Autopilot disabled이므로 사용자 가시화만)"
    YELLOW: "50-69 → 영적 검토 카드 발행"
    RED: "< 50 → 자동 rework + escalate"
  protocol: "AGENTS.md §5.4"
```

### Pastoral Decision Logs (Autopilot disabled 대체)

```yaml
pastoral_decision_logging:
  log_directory: "pastoral-decision-logs/"
  log_format: "{게이트ID}-{YYYY-MM-DD}-decision.md"
  required_fields:
    - gate_id              # BL-1 등
    - decision_card_text   # 한국어 4지선다 + 자유 메모
    - selected_option
    - free_memo            # 목회자 분별 자유 서술
    - timestamp
    - downstream_impact    # 어느 부교역자·어느 산출물에 미치는가
  retention: permanent     # 회귀 케이스 진실 원천 — PRD §9.1 v0.5 약속
  privacy_policy:          # v0.2 신설 (P2)
    storage: local_macOS_only_by_default
    external_backup: optional_user_opt_in   # 명시 승인 카드 통과 후 활성
    encryption_at_rest: age_or_gpg_required # 외부 백업 활성 시 의무
    pii_fields: [free_memo, downstream_impact]  # 회중·개인 식별 가능
    redaction_on_share: true                # /팀-회중허가 외부 산출 자동 redact
    access_log: pastoral-decision-logs/access.log
```

---

## §17. 제1 핵심 목적 ↔ 단계 매핑 (자가 점검)

| Step | 단계 | 제1 목적 연결 1줄 | PRD/idea 출처 |
|---|---|---|---|
| 1 | PRD/idea 4단계 읽기 | 약속 2(메타빌드) 첫 동작 = *생성 아닌 거부* — 환각 차단 | idea §2 A-2, PRD §11.1.a |
| 2 | 진입 게이트 9종 병렬 해소 | 약속 2·3·4·5·6 + 절대 ③ 동시 봉인 해제 — 본 워크플로우 유일 경로 | idea §7 진입 게이트 |
| 3 | 사용자 결정 카드 | 약속 1(무코드) + 절대 ③(목회자 최종) — 결정 동선 비개발자 흡수 | PRD §0.2 ③ |
| 4 | 결정 결과 외과적 반영 | 절대 기준 3 CCP 비례성 + §9.4 사전 게이트 | PRD §9.4 v0.5 |
| 5 | 12직 명함 + 3축 매핑 | 약속 4(팀 본질) + 절대 목표 정의문 직격 | PRD §6.4, §7.1 |
| 6 | didim 페어링 인터페이스 | 약속 6(didim 보존) + §11.5 페어링 규약 | PRD §0.1.bis 6, §11.5 |
| 7 | 진입 허가 | Implementation 봉인 — 게이트 미해결 진입 차단 | idea §7 |
| 7.5 | Bootstrap-of-Bootstrap (사용자 안내) | 약속 1(무코드) — Python·의존성 미설치 시 *코드 미실행 안내선*까지 (자동 설치 금지) | PRD §11.4, idea A-1 |
| 8 | Setup Hook 인프라 검증 | 약속 5(자가 검증) + C-9 명시 예외 | PRD §11.4, §12 C-9 |
| 9 | Bootstrap 0회차 셸 1줄 | 약속 2(메타빌드) + 약속 4(단일 진입점) | PRD §11.1.b, idea §2 A-1/A-2/A-3/A-4 |
| 10 | Phase 1 Core 5직 + UX + 신학 + HITL + didim Wrapper | 절대 목표 3축 + 약속 4·5·6 + 절대 ③ 결합 발현 | PRD §6, §7, §9, §11 + idea §3·§4·§5 |
| 11 | 1주 사역 사이클 시연 | FR-24 시연 검증 + §6.5 시간선 | PRD §6.5, FR-24 |
| 12 | SPOF 자가 복구 | 약속 3 ③ + 절대 ②(로컬 자동 실행) | PRD §11.2, idea §5 D-5 |
| 13 | Phase 2 자기 진화 사전 게이트 + 추가 부교역자 | 약속 3 ④ + Q9 자기 변질 차단 | PRD §9.4 v0.5, §15.1 C-L |
| 14 | 재해 복구 3종 | 약속 3 ⑤ — *끝까지* 5단계 마지막 | PRD §11.1.c ⑤ |
| 15 | 회중 노출 전 최종 검토 | 절대 ③ 마지막 게이트 + C-4 면책 라인 | PRD §0.2 ③, idea §4 C-4 🛡 |

> **미연결 항목**: 없음. 본 자가 점검 시점(작성 직후)에서 모든 단계가 제1 핵심 목적과 1:1 연결을 보유한다. 미연결 발견 시 본 workflow.md에서 즉시 제거.

---

## §18. 흔들 지점 (Distill 검증 — 본 설계도가 자동 실행될 때 무너지는 지점)

| ID | 흔들 지점 | 처리 방안 |
|---|---|---|
| W-1 | Step 2 Agent Team이 SOT를 동시에 쓰려 시도 | Team Lead 단일 쓰기 강제 + `dual_sot_pairing_guard.py` PostToolUse 차단 |
| W-2 | Step 3 사용자 결정 카드를 비개발자가 *전부* 답하지 못함 | 부분 응답 시 `/팀-결정 --resume` 회기적 진입 + SOT가 미응답 게이트 명시 표시 |
| W-3 | Step 6 B-1 사전 검증이 *실측 불가*(didim CLI 변경 가능성) | BL-10 ④ 재검증 트리거가 주기·didim 버전 변경 감지 시 자동 재검증 |
| W-4 | Step 9 0회차 셸 1줄이 비개발자에 적합한지 | BL-5 결정 결과(GUI 트리거 vs 셸 vs 기존 Claude Code 세션 내 슬래시) 반영 |
| W-5 | Step 10 신학 필터 회귀 케이스 ≥ 20개 누적 시점이 *Phase 1 첫 실행*에는 부재 | 부모 게놈에서 *초기 시드 케이스*를 *목회자 승인 후* 시드. 시스템 단독 합성 금지(PRD §9.1 v0.5) |
| W-6 | Step 11 1주 사이클 시연 시 didim 산출물 부정합 위험 | PRD §11.5 페어링 규약 + dual_sot_pairing_guard 코드 강제 |
| W-7 | Step 13 D-3 자기 진화 게이트가 Phase 1부터 필수인지 | BL-(vi) D-3 Phase 분기 결정 결과 반영 (사용자 결정) |
| W-8 | Step 15 회중 노출 직전 영적 검토 카드를 사용자가 우회 | 코드 강제 — `/팀-회중허가` 카드 통과 SOT 기록 없으면 외부 발행 hook 자동 차단 |
| W-9 | 6개월 정지 후 재개 시 state.yaml stale + PRD 버전 격차 + didim 위치 변경 동시 발생 | (v0.2) Step 8 setup_init에 *stale 검증* 추가 — `state.yaml.last_updated` 90일 초과 시 강제 재진입 카드(Step 1 4단계 재독 + 매니페스트 재계산) + Bootstrap 재진입 자동 트리거 |
| W-10 | Step 2 teammate 충돌(BL-5↔BL-9 등 교차 게이트의 결정 충돌) | (v0.2) Team Lead 통합 단계에서 BL × BL 충돌 매트릭스 생성 → Step 3 결정 카드에 충돌 사실 명시 + 사용자 일괄 결정 |
| W-11 | idea 미반영 4건(A-δ 런타임 빌드 트랜잭션 정책·B-α 결정 동선 UX 형식·B-ζ 반복 피로 토글·C-θ 제1 목적 1줄 연결 검증 기준) | (v0.3) idea §11 백로그(BL-12+ 또는 §6 충돌 표) 보존 의무 — workflow.md는 추적성 행만 보유, 실 결정은 idea 라운드에서. Step 2 gate-C-ux teammate 산출에 4건 후보 ≥ 1 의무 |
| W-12 | B-5(`PreToolUse` Hook 자동 didim 컨텍스트 주입) Phase 1 비채택 — 미래 채택 압력 발생 시 워크플로우 흔들 가능 | (v0.3) §1.bis 미사용 기본값 명문화 + 사용자 명시 BL 라운드 통과 전 자동 hook 등록 금지. Phase 2 진화 시 D-3 사전 게이트 통과 의무 |

---

## §19. 변경 이력

- **2026-05-04 v0.3 (draft)**: 직전 감사(workflow-idea ↔ workflow 반영 완결성 성찰) 확정 권장 조치 외과적 반영. **P1**: ① Step 10 Verification — `didim 입력 주입 활성`을 BL-2 채택안(RC-α/β/γ) 의존 분기로 조건화. BL-2 미결정 시 Phase 1 진입 차단 + idea §7 R-5 "B-2/B-5 Phase 1 미사용 기본값" 권고 보존. **P2**: ② Step 6 Verification — B-π **P-γ(역방향 캐시) 폐기 명문화** 라인 추가(`dual-sot-pairing-policy.md` 의무 기록 — maintainer 추적성 앵커). **부수(병행 반영 확인)**: ③ §1.bis Phase 1 미사용 기본값(B-2/B-5) 명문화 + Step 10 자동 차단. ④ §18 W-11/W-12 흔들 지점 추가(B-2/B-5 비채택 추적성). ⑤ Step 2 Verification G4 — 9종 P0 게이트 후보 ≥ 2 의무. 헤더 v0.2 → v0.3. 무관 섹션 변경 0건. §17 매핑 무손상. ND 가드 위반 0건.
- **2026-05-04 v0.3 (draft)**: 직전 성찰 보고서(workflow-idea ↔ workflow 반영 완결성 감사)의 블로커 1건 + 약화 4건 외과적 반영. **블로커 해소**: ① Step 10 "didim 입력 주입 활성" 라인을 *BL-2 결정 후 활성*으로 보류 처리(idea §3 B-3.bis 후보안 슬롯 단정 금지 회복) — sermon-context.md append-only 형태는 RC-α/β의 *예시*로 강등. **품질 강화**: ② Step 2 Verification §0.2 ④ 후보안 슬롯 체크에 *BL-1 한정 ≥ 2 의무* 명문화 ③ §1 진입 게이트 표 preamble에 *B-2/B-5 미사용 default* 명문 추가 ④ Step 6 dual_sot_pairing_guard 알고리즘에 *B-π P-β 동시 갱신 차단 규칙* 추가(60초 윈도우 + `/팀-동시갱신-회수` 카드) ⑤ Slash Commands에 `/팀-동시갱신-회수` 추가. 무관 섹션 변경 0, §17 매핑 무손상, ND 가드 위반 0건.
- **2026-05-04 v0.2 (draft)**: 062.log 성찰 보고서 D 권고 외과적 반영. **P0**: ① Step 6 didim CLI → 슬래시 커맨드 시스템(CM-1/2/3) 재정의 + B-1 실측 명령 모드별 구체화 ② Step 10 didim 입력 주입 활성(sermon-context.md append-only) 명시 ③ Step 9 BL-5 의존성 분기 9a/9b/9c 신설. **P1**: ④ Hook 매처 좁히기(theology_filter_dual.py를 churchTeam output 한정, dual_sot_pairing_guard를 state.yaml 한정) ⑤ dual_sot_pairing_guard 화이트리스트 키 알고리즘 명세 ⑥ Step 2 teammate turn 상한 12 + 컨텍스트 외부 파일화 + 충돌 사전 탐지 매처 ⑦ Step 7.5 Bootstrap-of-Bootstrap 신설. **P2**: ⑧ 신학 시드 공급 절차 ⑨ 기획 축 작동 방식 4필드 명세 ⑩ Pastoral Decision Logs 프라이버시 정책 ⑪ Step 11 시연 주차 ID 사전 결정 + M3 Phase 분리. **P3**: ⑫ Step 14 부모 게놈 원격 백업 다중성 ⑬ §18 W-9(6개월 stale) + W-10(충돌 매트릭스). 무관 섹션 변경 0, §17 매핑 무손상.
- **2026-05-04 v0.1 (draft)**: workflow-generator 스킬로 1차 산출. PRD v0.5 + workflow-idea v0.5 4단계 읽기 후 외과적 설계. 진입 게이트 8+1종을 Research §2 Agent Team으로 병렬 해소 + Step 3 사용자 결정 카드로 봉인 해제. 5단계("끝까지") Bootstrap → 운용 → SPOF 복구 → 자기 진화 → 재해 복구 모두 단계화. 부모 게놈 + didim 게놈 모두 Inherited DNA로 명문화. ND-1~8 가드 위반 0건(스택·디렉터리 절대 경로·DAG 노드 코드·Hook 본문·Skill 프롬프트 전문 무삽입 — 책임 경계까지만 명시).
  - 자기 점검 1층위 (사실): PRD/idea 모든 게이트·BL이 본 문서 §1 표 + Step 2 표에 1:1 매핑 ✅
  - 자기 점검 2층위 (구조): 흔들 지점 8개 식별 + 처리 방안 명시 → 자동 실행 시 무너지지 않음을 입증 시도
  - 자기 점검 3층위 (철학): 모든 단계가 §17.1 매핑 표에서 제1 목적과 1:1 연결 ✅
  - 미반영(다음 turn 처리): D-3 Phase 분기 *기본값 추천*(idea §6 #8) — 사용자 결정 카드에서 채택안 제시 형태로 보존

— end of workflow.md draft v0.3 —
