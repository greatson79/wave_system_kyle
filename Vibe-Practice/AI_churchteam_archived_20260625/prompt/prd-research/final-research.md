# Final Research — churchTeam PRD 통합 조사 결과

> **이 문서의 성격**: PRD 본문이 아니다. round-01·02·03 의 **모든** 심층조사 산출물(30개 파일)을 무손실·추적 가능하게 통합한 **PRD 입력 문서**다. 결론은 단정하지 않고 "선택지 + 근거 + 트레이드오프 + 반증"을 보존한다.
>
> **로컬 실행 불변**: 모든 선택지에 `[LOCAL-OK | LOCAL-PARTIAL | LOCAL-BLOCKED]` 태그를 유지한다. 클라우드·SaaS 전제 항목은 자동으로 LOCAL-BLOCKED로 분리된다.

---

## 0. 메타

### 0.1 통합 범위

| 차수 | 축 | Teammate 수 | Branch 수 | 결과 파일 수 |
|---|---|---|---|---|
| Round-01 | 일반(가정 분기) | 4 | — | 4 raw + 4 summary + 4 cross-analysis = 12 |
| Round-02 | 기술·이론 | 5 | 10 | 5 raw + 5 summary + 4 cross-analysis = 14 |
| Round-03 | 코딩·구현 | 5 | 10 + 4토론 + 3시나리오 | 5 raw + 5 summary + 4 cross-analysis = 14 |

> **차수 정의 권위 (P1-3 / S7 해소)**: 위 표는 *조사 차수*만 정의한다. 본 통합본 §6.4의 "4차 역방향(2026-04-29)"은 *성찰 차수*이지 조사 차수가 아니다. 각 조사 차수의 식별자 권위는 해당 `_round-meta.md`(§0.3.bis 선례). round-04 *조사*가 향후 추가될 경우 본 표를 갱신해야 한다.

### 0.2 작성 시점·작성자
- 작성일: 2026-04-29
- 작성 단계: 종합(synthesis) — round-01~03 사후, PRD 본문 작성 전 단계
- 입력 SOT: `prompt/prd-research/_index.md` + 각 round의 `_round-meta.md` + 모든 `summary.md` + 모든 `cross-analysis/*.md`. raw.md 는 출처 링크로만 보존(분량상 무손실 인용은 비현실 → 핵심은 summary·cross-analysis가 담당).
- **갱신 이력 (P0-3 자기 SOT 적용)**:
  - 2026-04-29 (초판): round-01~03 통합 + 4차 역방향(2026-04-29) 반영.
  - 2026-04-29 (자기 적용 성찰 P0/P1 패치): P0-1(§6.1), P0-2(§0.6 권위 위임), P0-3(§0.3.bis 자기 SOT), P1-1(§1.1 표기 일관성), P1-2(§3 라벨 정의), P1-3(§0.1 차수 권위), P1-4(§5.1 #12 일정 분리), P1-5(§0.6 읽기 동선) 반영. P2(S6·S8) 미반영(보류).

### 0.3 원본 파일 인덱스 (출처 링크용)

| ID | 경로 |
|---|---|
| R0-IDX | `prompt/prd-research/_index.md` |
| R1-META | `round-01/_round-meta.md` |
| R1-T1-R / R1-T1-S | `round-01/t1-workflow-architect/{raw,summary}.md` |
| R1-T2-R / R1-T2-S | `round-01/t2-scenario-explorer/{raw,summary}.md` |
| R1-T3-R / R1-T3-S | `round-01/t3-operator-analyst/{raw,summary}.md` |
| R1-T4-R / R1-T4-S | `round-01/t4-sustainability-strategist/{raw,summary}.md` |
| R1-X-INT / R1-X-CFL / R1-X-PRK / R1-X-ADV | `round-01/cross-analysis/{intersections,conflicts,parking-lot,prd-direction-advice}.md` |
| R2-META | `round-02/_round-meta.md` |
| R2-T1-R / R2-T1-S | `round-02/t1-platform-capability/{raw,summary}.md` |
| R2-T2-R / R2-T2-S | `round-02/t2-configuration-architect/{raw,summary}.md` |
| R2-T3-R / R2-T3-S | `round-02/t3-orchestration-engineer/{raw,summary}.md` |
| R2-T4-R / R2-T4-S | `round-02/t4-integration-specialist/{raw,summary}.md` |
| R2-T5-R / R2-T5-S | `round-02/t5-theory-foundation/{raw,summary}.md` |
| R2-X-INT / R2-X-CFL / R2-X-PRK / R2-X-ADV | `round-02/cross-analysis/{intersections,conflicts,parking-lot,prd-direction-advice}.md` |
| R3-META | `round-03/_round-meta.md` |
| R3-T1-R / R3-T1-S | `round-03/t1-workflow-script-architect/{raw,summary}.md` |
| R3-T2-R / R3-T2-S | `round-03/t2-agent-orchestration-coder/{raw,summary}.md` |
| R3-T3-R / R3-T3-S | `round-03/t3-skills-hooks-developer/{raw,summary}.md` |
| R3-T4-R / R3-T4-S | `round-03/t4-verification-quality-coder/{raw,summary}.md` |
| R3-T5-R / R3-T5-S | `round-03/t5-state-recovery-coder/{raw,summary}.md` |
| R3-X-INT / R3-X-CFL / R3-X-PRK / R3-X-ADV | `round-03/cross-analysis/{intersections,conflicts,parking-lot,prd-direction-advice}.md` |

### 0.3.bis 출처 ID 정책 (round-04 대비) + 본 문서 자체의 SOT 규칙
- 본 통합본의 R1/R2/R3 ID는 round-01~03 시점 권위. **round-04 이상이 추가되면 각 차수 `_round-meta.md`가 식별자 권위**(R3-X-CFL §3 선례 적용). 본 문서는 추가 차수 발생 시 §0.3 인덱스를 갱신해야 하며, 충돌 시 `_round-meta` 우선.
- **본 문서 자체의 SOT 규칙 (P0-3 / S5 해소 — 자기 적용)**: final-research.md 자체에도 시스템 절대 기준의 SOT 원칙을 자기 적용한다.
  - **단일 쓰기자**: PRD 작성자(또는 사용자가 위임한 1인). 동시 다중 편집 금지.
  - **갱신 트리거**: ① round-N+1 *조사* 완료 직후 / ② 적대적·자기 적용 성찰의 P0 패치 승인 직후 / ③ PRD 본문이 §4.2 미해결 충돌을 확정하여 본 문서가 단정 보류한 항목이 닫힐 때.
  - **원자 쓰기**: 패치 단위 커밋 + diff 보고(본 문서 §0.6 또는 별도 CHANGELOG 항)로 흔적 보존. 갱신일·갱신 사유·반영 항목 ID(P0-*, P1-*)를 명시.
  - **버전 추적**: 본 문서를 인용하는 PRD·자식 문서는 인용 시점의 갱신일을 함께 표기해야 한다(SOT 두 버전 병존 시 추적 가능성 보장).

### 0.4 SOT 규칙 파일 검토
- `prompt/mandatory-decision-rules-sot.md` — **부재**. 본 통합에서는 적용 불가(세션 지시: 부재 시 무시).

### 0.5 로컬 실행 불변 위반 사전 점검
- LOCAL-BLOCKED 사례: **Logos / Accordance** (R2-T4-S, R2-X-ADV) — SaaS 구독 전제. 본 통합은 이를 §3 매트릭스에서 별도 행으로 격리 보존.
- 클라우드 전용 SDK·서버형 큐(Redis/Celery)·외부 DB·원격 워크플로우 엔진 — Non-Goal 후보(R3-X-ADV §Goals/Non-Goals).
- LOCAL-PARTIAL 항목: NotebookLM MCP, Telegram MCP, Gamma/Canva MCP, 분산 오케스트레이션 후보 — §3 매트릭스에 태그 보존.

### 0.6 Executive Digest (사용자용 1페이지 요약 자리 — 단정 금지)

> 본 절은 가독성 보강. 본문 §1~§6의 *결정 압력이 가장 큰 항목*만 압축한다. 결론은 PRD가 확정.
>
> **읽기 동선 (P1-5 / S10 해소)**: 부분 독해 시 §0.6(이 절) → §4.2(미해결 충돌) → §6.4(역방향 4차 미수행 축) → 부록 B(단정 보류 항목) 4구간을 순독하라. 본문 §1~§3 매트릭스는 결정 시 근거 재참조용으로 후속 열람.
>
> **권위 위임 (P0-2 / S2 해소)**: 본 절의 "BLOCKER 5선"은 *목적 ①(영적 사역 본질) 직격* 항목 5선이다. **P0(Phase 0 진입 전 결정 필수) 전체 카운트의 권위는 §4.2 표**(C-시리즈 + 격상된 U1·U2·OQ#4 포함, 총 8개)에 있다.

- **BLOCKER 5선** (목적 ① 직격, Phase 0 진입 전 사용자 결정 필수): C-A(didim 경계) · C-D(부교역자팀 정체성) · C-E(사고/전략/실행 분해) · C-F(Bootstrap·DNA 상속) · C-H(자동화율 신학 기준선). *나머지 P0 항목은 §4.2 권위.*
- **운영 SPOF 4선** (Phase 0 산출물로 격상): A1 단일 쓰기자 사망 시 lock breaking + resume / U1 4.5 잠금 후 재계획 / U2·OQ#1 외부 인증 fallback 매트릭스 / OQ#4 PreCompact↔status.md 동시성.
- **LOCAL-BLOCKED 영구 후보**: Logos / Accordance / 멀티 LLM(GPT/Gemini) / 분산 합의 알고리즘.
- **Non-Goal (Phase 2까지)**: 클라우드 SDK · 서버형 큐(Redis/Celery) · 외부 DB · 다중 사용자 동시 편집 · 원격 워크플로우 엔진.
- **합의 좌표 6선**: 혼합 DAG / Centralized + readonly fanout / 레이어 분리 skill / 2중 Theology Filter / L0 전면+L1 형식+L2 핀포인트 / File-state + phase enum.

---

## 1. 시스템 개요 (조사 기반 — 결론 아님)

### 1.1 대상 시스템
- **이름**: AI 교역자팀 (churchTeam)
- **사용자**: 담임목사 1인(비개발자) — Phase 1 가정 (R1-T3-S, R2-X-INT §3, R1-X-ADV §4)
- **실행 환경**: 로컬 macOS, Claude Code Max 단독 (R2-T1-S)
- **목적(조사 시점 인지)**: 목회 보조(설교·묵상·양육·행정 등) + 신학 필터링 + 로컬 자동화. **에이전트 수("12개")는 round-01~03이 가정으로 사용한 숫자일 뿐 근거 단정이 아님** — Phase 1 합의 우세는 핵심 3~5(§3.8), 12개 전체는 Phase 2~3 후보 범위. PRD 본문에서 최종 정의될 절대 목표·정확한 에이전트 셋은 본 문서가 단정하지 않는다.
- **본문 표기 일관성 (P1-1 / S3 해소)**: 본 문서 §1.1.ter / §3.7 / §3.8 / §6.4 / 부록 B 등에서 "12 에이전트" 표기가 등장하나 모두 *위 면책*을 상속한다. 즉 "12"는 *조사 가정*이며 PRD가 핵심 3~5로 확정하면 본문 단정 표기는 모두 "(가정 12, Phase 1 핵심 3~5 미정 — C-C)"로 읽혀야 한다. PRD 작성 시 인용 위치마다 이 면책을 함께 노출할 것.

### 1.1.bis 절대 목표 정합성 — 사고/전략/실행 3축 (조사 누락 자인)
> Round-01~03이 *실행 보조* 편중으로 진행되어 사용자 절대 목표(사고·전략·실행 보조)의 *사고·전략* 축이 본문에 충분히 반영되지 못했다. 본 절은 그 사실 자체를 시스템 전제 1장에 노출하기 위한 자리이며, 매핑은 PRD가 확정한다(C-E / G15 직결).

### 1.1.ter 부교역자팀 정체성 (조사 누락 자인)
> 12 에이전트의 *목회 직무 매핑·권한 위계*(목사 ↔ 부교역자 시뮬레이션)는 round-01~03에서 *기술 메타*(agent-registry)만 다뤄져, *정체성*은 미조사. 사용자 절대 목표 ①(영적 사역 본질) 직격 공백이며 PRD §Pastoral Team Identity & Role Model로 분리 결정 대기(C-D / G14).

### 1.2 조사가 식별한 시스템 전제(보존)
| 전제 | 출처 | 태그 |
|---|---|---|
| Claude Code 단독 자동 트리거 불가, 사용자 슬래시 커맨드 개시 필수 | R2-T1-S, R2-X-ADV §T-1 | LOCAL-BLOCKED(자동 트리거) |
| state.yaml(또는 `_state.json`) 기반 상태 머신이 세션 간 유일한 SOT 유지 수단 | R2-X-INT §1, R3-T5-S | LOCAL-OK |
| 신학 검증의 최종 판단은 목회자 — 자동화로 대체 불가 | R2-T5-S, R2-X-INT §4 | LOCAL-OK |
| 부모 게놈(`weekly-works/.claude/skills/team-leader/rules/*`, 11 validator) 와의 정합 유지 | R3-META, R3-X-INT | LOCAL-OK |
| `weekly-works`(didim) 와의 역할 경계 미정의 = **선결 과제** | R1-T2-S, R1-X-CFL §2 | LOCAL-OK(가정) |

---

## 2. 축별 종합

각 축은 (a) 핵심 선택지, (b) 근거, (c) 트레이드오프, (d) 반증/한계, (e) LOCAL 태그, (f) 출처 순으로 보존한다.

### 2.1 일반 축 (Round-01) — Claude Code 단독 vs 외부 도구 연동

#### 2.1.1 t1 Workflow Architect — 혼합 구조
- (a) 선택지: **Claude Code 에이전트 뼈대 + Theology Filter(Python Hook) + 원어 로컬 DB** 혼합 (R1-T1-S)
- (b) 근거: Orchestrator 라우팅 + state.yaml SOT + Hook 기반 신학 검증이 품질·운용성 균형
- (c) 트레이드오프: Hook 도입 시 비개발자 진입장벽 (vs t3)
- (d) 반증/한계: 에이전트가 state.yaml 직접 수정하면 SOT 충돌; 컨텍스트 격리 없으면 소진
- (e) **[LOCAL-OK]** (Hook·로컬 DB 모두 로컬)
- (f) R1-T1-S, R1-T1-R

#### 2.1.2 t2 Scenario Explorer — 차별점·범위
- (a) 선택지 우선순위: **설교 파이프라인 > 행정 자동화 > 양육 (Phase 2)** (R1-T2-S)
- (b) 근거: 빈도·가치 분석. 행정은 didim 미구현 → 차별점.
- (c) 트레이드오프: 설교만 = didim과 중복 위험 / 전체 = 토큰·복잡도 폭증
- (d) 반증: didim과의 1:1 기능 비교 미수행 → PRD 작성 전 선결 과제
- (e) **[LOCAL-OK]**
- (f) R1-T2-S, R1-T2-R

#### 2.1.3 t3 Operator Analyst — 운용성 조건
- (a) 선택지: **`/install` 자동화 + 슬래시 커맨드 인터페이스 + 한국어 출력 + Filter FAIL 시 HITL** (R1-T3-S)
- (b) 근거: 비개발자 1인 운용 가정에서 진입 마찰이 가장 큰 이탈 위험
- (c) 트레이드오프: `/install` 자동화 범위가 넓을수록 구현 복잡도 ↑
- (d) 반증/한계: `/install`이 Python 환경까지 자동 구성 가능한지 미검증 → 기술 검증 필요
- (e) **[LOCAL-OK]**
- (f) R1-T3-S, R1-T3-R

#### 2.1.4 t4 Sustainability Strategist — 지속 가능성
- (a) 선택지: **Theology Filter 프롬프트 버전 관리 + state.yaml 스키마 버전 관리 + Agent() 호출 변경 모니터링** (R1-T4-S)
- (b) 근거: 6개월 후 신뢰도 저하 시나리오. 토큰 추정(설교 1회 6~8K, 월 50~80K)
- (c) 트레이드오프: 버전 관리 도입 = 설치/유지 추가 부담
- (d) 반증/한계: 회귀 테스트 자동화 방법 미정 (P2)
- (e) **[LOCAL-OK]**
- (f) R1-T4-S, R1-T4-R

#### 2.1.5 R1 Cross — 합의·불일치·파킹
- **Green Zone (4/4 합의)**: Orchestrator, 슬래시 커맨드, state.yaml SOT, Theology Filter, HITL 지점 명시, 한국어 출력 — `[LOCAL-OK]` 전부 (R1-X-INT)
- **Yellow Zone (조건부)**: Python Hook(환경 확인 시), 원어 DB(품질 요건 후), 양육 파이프라인(Phase 2), 스태프 멀티유저(Phase 2)
- **Red Zone (현재 제외)**: Strategy Intelligence, Scenario Agent, 멀티 LLM(GPT/Gemini) — 마지막 항목은 *영구 제외 후보*
- **충돌 1 (가장 심각)**: Theology Filter 구현 — Python Hook(t1·t4 품질) vs 진입장벽(t3) → "두 선택지 트레이드오프 PRD 명시 + `/install` 검증" (R1-X-CFL)
- **충돌 2**: didim 관계 — t2 중복 위험 vs 나머지 차별점 인정 → 1:1 비교 표 후 사용자 결정 필수
- **충돌 3**: Phase 1 범위 — 12 전체 vs 핵심 3~5
- **R1 파킹 P0**: didim 비교, Phase 1 범위 확정 (R1-X-PRK)

#### 2.1.6 R1 PRD 방향 조언 (보존 — 단정 금지)
- 선결 질문 2개를 PRD 첫 섹션에 명시 (didim 관계 / Filter 구현 방식)
- Phase 1/2/3 구조 분리
- 신학 제약을 ABSOLUTE ANCHOR로 격상
- 사용자 모델 = 담임목사 1인 고정 (Phase 1)
- 에이전트별 로컬 실행 가능성 명시란 (R1-X-ADV)

---

### 2.2 기술·이론 축 (Round-02)

#### 2.2.1 t1 Platform Capability
- (a) 선택지: **state.yaml SOT + 단계별 세션 분할 + 2중 Theology Filter(프롬프트 1차 + Hook 2차)** (R2-T1-S)
- (b) 근거: Claude Code Max 컨텍스트 소진·자동 트리거 불가의 구조적 제약
- (c) 트레이드오프: 단계 분할 = 인간 개시 횟수 ↑, 단순성 ↓
- (d) 반증: SaaS-AgenticWorkflow 사례에서 3 병렬 Task 중 2개 rate limit 중단 (RATELIMIT_FAILURE_ANALYSIS.md 인용)
- (e) 설교·묵상·행정 파이프라인·2중 Filter **[LOCAL-OK]**, 자동 트리거 **[LOCAL-BLOCKED]**, cron 연동 **[LOCAL-OK]**
- (f) R2-T1-S, R2-T1-R

#### 2.2.2 t2 Configuration Architect
- (a) 선택지: **CLAUDE.md 200라인 이하 경량 TOC + `.claude/skills/` 분산 + `theology_guard.py` Hook (PostToolUse)** (R2-T2-S)
- (b) 근거: 12 에이전트·신학 필터·3 파이프라인 복잡도에서 컨텍스트 절약
- (c) 트레이드오프: 분산 구조 = 파일 수 ↑, 탐색 비용 ↑
- (d) 반증/한계: CLAUDE.md 컨텍스트 실제 측정 미실시 (R2-X-PRK §2)
- (e) **[LOCAL-OK]**
- (f) R2-T2-S, R2-T2-R

#### 2.2.3 t3 Orchestration Engineer (이론 레벨)
- (a) 선택지: **Phase 1 = 경량 순차, Phase 2 = 3 파이프라인 병렬** (R2-T3-S)
- (b) 근거: 안정성 우선 + Task 격리 + 체크포인트
- (c) 트레이드오프: 순차만 = 실행 시간, 병렬 즉시 = rate limit 위험
- (d) 반증: SaaS-AgenticWorkflow rate limit 중단
- (e) 경량 순차·세션 분할 **[LOCAL-OK]**, 병렬 Task **[LOCAL-OK + 모니터링 필요]**
- (f) R2-T3-S, R2-T3-R

#### 2.2.4 t4 Integration Specialist
- (a) 선택지 분류 (R2-T4-S):
  - 필수: state.yaml, `.claude/` 구조 — **[LOCAL-OK]**
  - 권장: OSIS XML 원어 DB, Playwright — **[LOCAL-OK (설치)]**
  - 선택: cron, pandoc, yt-dlp — **[LOCAL-OK]**
  - 선택·주의: NotebookLM MCP, Telegram — **[LOCAL-PARTIAL]**
  - 제외: Logos, Accordance — **[LOCAL-BLOCKED]**
- (b) 근거: 로컬 실행 불변 + 인증/외부 SaaS 의존도
- (c) 트레이드오프: 적극 연동 = 자동화 가치 ↑ / 인증 만료 시 파이프라인 차단
- (d) 반증: NotebookLM 인증 갱신 실패 시 워크플로우 차단(R3-X-PRK §A2)
- (f) R2-T4-S, R2-T4-R

#### 2.2.5 t5 Theory Foundation
- (a) 핵심 이론 매트릭스 (R2-T5-S, 모두 **[LOCAL-OK]**):
  | 이론 | 적용 |
  |---|---|
  | ReAct (Yao 2023) | Orchestrator 루프 |
  | Multi-Agent (Li/Park 2023) | 12 에이전트 역할 분화 |
  | Reflexion (Shinn 2023) | Theology Filter 자기 검토 |
  | Unix 철학 (1978~) | 에이전트 단일 책임 |
  | 상태 머신 | state.yaml SOT |
  | 실패 격리 (Bulkhead) | Task 격리 |
- (b) 근거: 이론(설계 언어) ↔ 검증 원칙(구현 신뢰성) 상보
- (c) 트레이드오프: 이론 충실 = 추상도 ↑ / 원칙 충실 = 표현력 ↓
- (d) 핵심 갭 3개:
  1. ReAct 완전 자동 루프 → Claude Code는 사용자 개시 필수
  2. Multi-Agent 실시간 공유 → 파일 기반 비동기만 가능
  3. 멱등성 → LLM 비결정성으로 부분만 가능
- **이론 우선 원칙**: "목회자 검토 단계는 이론적 자동화 설계보다 우선"

#### 2.2.6 R2 Cross — 합의·불일치·파킹
- **4/4 합의 (R2-X-INT)**: state.yaml 상태 머신, 슬래시 커맨드 표준화, Phase 분리 MVP 우선, 목회자 최종 검토, CLAUDE.md 경량 TOC + skills 분산
- **3.5/4 합의**: 2중 Theology Filter(프롬프트+Hook), 병렬 Task = Phase 2 이후
- **불일치 #1 (R2-X-CFL)**: Filter 구현 — t1(프롬프트 위임) vs t2(Hook 격리) → **2중 방어**로 해결(프롬프트=복잡 신학, Hook=금지 키워드 regex)
- **불일치 #2**: 병렬 도입 시점 — 고도(t3.2) vs 경량(t3.1) vs 미명시 위험(t1.2) → Phase 1 순차 / Phase 2 병렬, 단 설정 아키텍처는 Phase 1부터 병렬 지원
- **불일치 #3**: NotebookLM MCP 포함 — 적극(t4.2) vs 최소(t4.1) → MVP 제외, 인증 재시도 로직 후 Phase 2 선택 추가
- **불일치 #4**: 이론 vs 검증 원칙 → 충돌 아님, 상보(설계 언어 ↔ 구현 신뢰성)
- **파킹 P1 (Round-03 필수)**: Theology Filter 회귀 테스트 방법론 (R2-X-PRK §P1)
- **파킹 P2/P3**: 원어 DB 옵션 비교, 토큰 실측

#### 2.2.7 R2 PRD 방향 조언 (보존)
- T-1: PRD 앞에 **기술 전제 섹션** 추가 (자동 트리거 LOCAL-BLOCKED 등)
- T-2: `.claude/` 디렉터리 구조 다이어그램 (CLAUDE.md, skills/, hooks/scripts/, commands/)
- T-3: Theology Filter 독립 설계 항목 (1차 프롬프트 + 2차 Hook + 회귀 케이스 20개 + 목회자 승인)
- T-4: 에이전트별 로컬 실행 가능성 표 (ExegesisAgent LOCAL-PARTIAL, 나머지 LOCAL-OK 등)
- T-5: Phase별 기술 복잡도 연동 (Phase 1: 4~5개/순차/낮음 → Phase 3: 12개/완전/높음)
- T-6: Round-03 우선 조사 3개 지정

---

### 2.3 코딩·구현 축 (Round-03)

#### 2.3.1 t1 Workflow Script Architect
- (a) 선택지: **상위 절차적 + 노드 내부 선언적 혼합 DAG** (R3-T1-S)
- 단독 후보(선언적 단독·절차적 단독)는 모두 기각
- (b) 근거: 4.5 게이트 D·E fanout 등 하드 게이트는 선언적이 강제 가능, 인간 분기는 절차적이 흡수
- (c) 트레이드오프: 혼합 = 학습 곡선 ↑
- (d) 반증: "4.5 후 D·E 동시 소환"이 *피드백 메모리*로 박혀야 했던 기존 운영 사실 = 선언적 단독 약점 증거
- (e) **[LOCAL-OK]** (1.1, 1.2 모두)
- (f) R3-T1-S, R3-T1-R
- 부록 의무 스키마: `id, phase, agent, skill, inputs[], outputs[], validators[], retry_budget, depends_on, exit_criteria`

#### 2.3.2 t2 Agent Orchestration Coder (코드 레벨)
- (a) 선택지: **Centralized + readonly fanout** — team-leader만 status.md/`_state.json` write, sub-skill은 자기 출력 폴더만 write (R3-T2-S)
- (b) 근거: SOT 단일 쓰기를 **PreToolUse hook으로 권한 코드 강제**
- (c) 트레이드오프: 분산 = 자율성 ↑ / 분산 트랜잭션 부재로 race
- (d) 반증: insert-images가 이미 부분 자율 → "절대 중앙"은 비현실
- (e) 2.1 **[LOCAL-OK]**, 2.2 분산 **[LOCAL-PARTIAL]** (분산 트랜잭션 부재)
- (f) R3-T2-S, R3-T2-R

#### 2.3.3 t3 Skills & Hooks Developer
- (a) 선택지: **레이어 분리 — General(`val/*`, 부모 11 validator) + Specific(`skill/*`, churchTeam 특화)** (R3-T3-S)
- 단독 후보(General 단독·Specific 단독)는 기각
- (b) 근거: 이름공간 prefix로 충돌 방지, 부모 게놈 재사용
- (c) 위치 결정: 신학·SOT-pin checker(sermon-plan-2026.json JSONPath)는 `skill/sermon` 안
- (d) 파킹: skill 패키징·버전 관리 (R3-X-PRK §A3)
- (e) 3.1 **[LOCAL-OK]**, 3.2 **[LOCAL-OK]**

#### 2.3.4 t4 Verification & Quality Coder
- (a) 선택지: **L0(빈 산출 차단) 전면 + L1(형식) 전면 + L2(핀포인트 — 4.5/신학/번역/SOT-pin)** (R3-T4-S)
- (b) 근거: 부모 게놈 quality-gates와 정합. SOT-pin checker는 모든 설교 노드 의무.
- (c) 트레이드오프: Strict 단독 = 토큰·UX 비용 폭발 → 기각 / 검증 생략 = 무의미 → 기각
- (d) 반증: "주간현황 텍스트 출력 금지" 메모리 → 검증 결과의 UX 비용도 품질 일부
- (e) 4.1, 4.2 **[LOCAL-OK]**
- 파킹: 비결정 산출(카드뉴스 PNG) 회귀 검출 — hash 비교 부적합 (R3-X-PRK §A6)

#### 2.3.5 t5 State & Recovery Coder
- (a) 선택지: **File-Based(`_state.json` 진실, status.md 파생) + 얇은 phase enum guard** (R3-T5-S)
- 풀 HSM은 churchTeam 규모에 과도 → 기각
- (b) 원자 쓰기 규칙: tmp write → fsync+rename → status.md 재생성 → git add (단일 쓰기자=team-leader 전제)
- (b.bis) **단일 쓰기자 사망 시 복구 (Phase 0 필수 산출물 — BLOCKER)**: team-leader 세션이 컨텍스트 소진/중단으로 stale lock 남길 가능성은 SPOF. 다음 항목은 *Open Question이 아닌* Phase 0 산출물로 격상한다 — ① lock TTL + heartbeat ② 외부 lock breaker 슬래시 커맨드(예: `/recover --lock-break`) ③ resume 절차(`_state.json` 마지막 phase에서 재진입) ④ 보호: lock break 전 status.md+`_state.json` 백업 사본. **[LOCAL-OK]**
- (c) 4.5 게이트 코드: `transition("P1_5_TITLE_LOCKED")` 후 sermon-context.md immutable lock
- (d) 파킹: PreCompact ↔ status.md 동시성 (R3-X-PRK §A4)
- (e) 5.1, 5.2 **[LOCAL-OK]**

#### 2.3.6 R3 Cross — 합의·불일치·파킹
- **5/5 합의 (R3-X-INT)**: 위 5축 합의 좌표 모두 LOCAL-OK
- **운영 불변 5개**: ① team-leader 단독 SOT write ② 4.5 = phase enum hard gate ③ SOT-pin checker 의무 ④ L0 전면 ⑤ workflow.md 부록 스키마
- **내부 불일치 (R3-X-CFL §1)**: 모두 5팀 다수결로 단독 기각, 혼합/계층 채택
  - C1 선언적·절차적 → 혼합
  - C2 중앙·분산 → Centralized + readonly fanout (분산 단독은 절대 기준 2 위반 위험 → **[LOCAL-PARTIAL]**)
  - C3 범용·특화 → 레이어 분리
  - C4 Strict·Selective → L0/L1 전면 + L2 핀포인트
  - C5 파일·HSM → File-state + phase enum
- **차수 간 경계 중복 (R3-X-CFL §2)**:
  - 오케스트레이션: 2차(이론) ↔ 3차(코드) = **수직 관계, 충돌 아님** — PRD §System Architecture 두 층위 모두 반영
  - 검증: 2차 t1·t5 원칙 ↔ 3차 t4 코드 매핑 = 인용 관계
  - 상태: 2차 t2(설정) vs 3차 t5(워크플로우 상태) = 영역 분리
- **식별자 정책 (R3-X-CFL §3)**: round-02부터 차수별 5팀 재구성 선례. `_index.md`의 4축 표는 round-01 기준으로 보존, 차수별 정의는 `_round-meta.md`가 권위.
- **미해결 충돌 → PRD 이관 (R3-X-CFL §4)**:
  - **U1**: 4.5 잠금 후 4단계 추가 갱신 시도 시 정책 (재계획 메커니즘 미정)
  - **U2**: NotebookLM MCP 인증 갱신 실패 시 차단/우회 정책

#### 2.3.7 R3 PRD 방향 조언 (보존)
- §Goals/Non-Goals: 클라우드 전용 SDK / 원격 워크플로우 엔진 / 서버형 큐 / 외부 DB / 다중 사용자 동시 편집(Phase 2까지) **Non-Goal**
- §System Architecture: 3 레이어(Workflow DAG / Orchestration / State & Validation), 노드 4-tuple(입력 SOT·출력 경로·검증자·재시도 예산)
- §Workflow Specification: 부록 스키마, 4.5 hard gate, D·E `depends_on: [sermon-4_5]` 동일
- §Agents & Skills Catalog: agent-registry.md 의무 필드 — `type=interactive|auto`, `writes`, `reads`, `mcp_required`, `local_tag`
- §Quality Gates: L0/L1/L2 매트릭스
- §State & Recovery: `_state.json` + status.md 페어, 원자 쓰기 규칙, PreCompact 상호작용
- §Local Constraint Compliance: 외부 의존 표 (아래 §3)
- §Phased Delivery: Phase 0(1주, Rapid-Prototype) → Phase 1(+2주) → Phase 2(Hardening)
- §What PRD Must NOT Do: skill 내부 프롬프트 전문 / SDK 이름 박지 말 것 — 경로·책임 경계까지만

---

### 2.4 외부 연동 축 (Round-02 t4 + Round-03 cross 통합)

조사 자체는 외부 연동을 별도 축으로 두지 않았으나, 통합 단계에서 LOCAL 태그 보존을 위해 별도 시각화한다.

| 연동 대상 | 분류 | LOCAL 태그 | 미해결 |
|---|---|---|---|
| state.yaml / `.claude/` 구조 | 필수 | LOCAL-OK | — |
| OSIS XML 원어 DB | 권장(설치) | LOCAL-OK | 옵션 비교(BibleOL/Unbound/Sword) 미수행 (R1-X-PRK, R2-X-PRK §P2) |
| Playwright (A4 캡처) | 권장(설치) | LOCAL-OK | — |
| cron / pandoc / yt-dlp | 선택 | LOCAL-OK | cron 슬래시 자동 호출 패턴 미정 (R2-X-PRK §7) |
| Telegram MCP | 선택·주의 | LOCAL-OK (인증 경계 미정의) | Open Question #1 (R3-X-PRK §A1) |
| NotebookLM MCP | 선택·주의 | LOCAL-PARTIAL | `refresh_auth` 실패 시 정책 — Open Question #2 (R3-X-PRK §A2, U2) |
| Gamma / Canva MCP | 출력 | LOCAL-PARTIAL (입력 송신 없음) | — |
| Anthropic API (Claude Code 내부) | 필수 | LOCAL-OK | — |
| **Logos / Accordance** | **제외** | **LOCAL-BLOCKED** | 영구 제외 후보 |

#### 2.4.bis 외부 인증 fallback 매트릭스 (Phase 0 필수 산출물 자리)
> U2·OQ#1 통합. 결정은 PRD가 확정. 본 표는 *선택지 자리*만 보존.

| 외부 의존 | 차단(Block) | 스킵(Skip) | 수동(Manual) | 캐시(Cache) |
|---|---|---|---|---|
| NotebookLM MCP `refresh_auth` 실패 | 파이프라인 중단 + 한국어 에러 | 해당 노드만 건너뜀(L0 회피) | 사용자에게 재인증 요청 + resume | 직전 결과 재사용(staleness 표시) |
| Telegram MCP 권한 만료/인젝션 | Telegram 채널 입력 차단 | 채널 메시지 무시 | 수동 paste 경로 | 해당 없음 |
| Gamma/Canva MCP | 출력 단계 중단 | 로컬 PNG 대체 | 사용자 export | 해당 없음 |
| Anthropic API rate limit | 백오프+재시도 | 해당 Task 스킵 | 사용자 재시도 | 부분 결과 보존 |

#### 2.4.ter LOCAL-PARTIAL 기능 단위 분해 (자리 — 단정 금지)
> "항목 수준" 태그가 *어떤 기능*에서 PARTIAL인지 미세 분해. 본 표는 PRD에서 채워질 자리.

| 항목 | OK 기능 | PARTIAL 기능 | BLOCKED 기능 |
|---|---|---|---|
| ExegesisAgent / 원어 DB | 검색·조회 | 자동 동기화·라이선스 갱신 | (해당 시) 외부 SaaS 연계 |
| NotebookLM MCP | 단발 질의 | 인증 갱신 자동화 | (인증 실패 시) 워크플로우 진행 |
| Telegram MCP | 메시지 수신 표시 | 권한·인젝션 게이트 | 자동 권한 부여 |
| Gamma/Canva MCP | 출력 송신 | 입력 회수·버전 관리 | 양방향 동기화 |

---

## 3. 선택지 매트릭스 (LOCAL-* 태그 포함)

> **읽는 법**: 각 행은 *조사가 식별한 선택지*다. PRD가 어느 행을 채택할지는 본 문서가 단정하지 않는다.
>
> **라벨 정의 (P1-2 / S4 해소 — 과정 인용)**: 본 §3 매트릭스의 "상태" 컬럼 라벨은 *결과 단정*이 아니라 *조사 과정 인용*이다.
> - **기각** = 해당 차수 cross-analysis에서 *5팀 다수결 단독 기각* 또는 *명시적 트레이드오프 비교 후 단독 약점 확정*된 항목 (예: §3.1 선언적 단독 = R3-T1-S에서 하드 게이트 한계 확정).
> - **합의 좌표** = 4축(R1) / 4축(R2) / 5축(R3) 합의 또는 3.5/4 이상 합의가 cross-analysis intersections에 명시된 항목.
> - **의무·단계적 합의·격상** = 운영 불변·Phase 분리·적대적 성찰을 통한 격상이 본문 §2 또는 §4에 인용된 항목.
> - PRD가 매트릭스를 인용할 때 라벨만 떼어 인용 금지. *과정 출처(R\*-X-INT/CFL/PRK)와 함께* 인용해야 사용자 결정 자유가 보존된다.

### 3.1 Workflow 표현
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| 선언적 단독 | LOCAL-OK | R3-T1-S | **기각**(하드 게이트 강제 한계) |
| 절차적 단독 | LOCAL-OK | R3-T1-S | **기각**(인간 분기 흡수 한계) |
| 상위 절차적 + 노드 선언적 혼합 | LOCAL-OK | R3-T1-S, R3-X-INT | **합의 좌표** |

### 3.2 Orchestration
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| Centralized + readonly fanout (단일 쓰기자) | LOCAL-OK | R3-T2-S, R3-X-INT | **합의 좌표** |
| Skill Swarm (분산 쓰기) | LOCAL-PARTIAL | R3-T2-S, R3-X-CFL §C2 | **기각**(race·일관성) |
| 경량 순차(Phase 1) → 병렬(Phase 2) | LOCAL-OK | R2-T3-S, R2-X-CFL §2 | **단계적 합의** |
| 즉시 병렬 Task | LOCAL-OK + rate limit 모니터링 | R2-T3-S | Phase 2 이후 |

### 3.3 Skills & Hooks
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| General 단독(`val/*`만) | LOCAL-OK | R3-T3-S | **기각** |
| Specific 단독(`skill/*`만) | LOCAL-OK | R3-T3-S | **기각** |
| 레이어 분리(General + Specific) | LOCAL-OK | R3-T3-S, R3-X-INT | **합의 좌표** |

### 3.4 Theology Filter
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| 프롬프트(LLM 판단) 단독 | LOCAL-OK | R1-X-CFL §1, R2-X-CFL §1 | 단독 채택 시 일관성 위험 |
| Python Hook 단독 | LOCAL-OK (환경 확인 시) | R1-T1-S, R1-X-CFL §1 | 비개발자 진입장벽(R1-T3-S) |
| **2중 방어 (프롬프트 1차 + Hook 2차)** | LOCAL-OK | R2-T1-S, R2-T2-S, R2-X-INT §6 | **3.5/4 합의** |
| 자동화 단독(목회자 검토 생략) | LOCAL-OK | — | **기각**(R2-X-INT §4) |

### 3.5 Verification
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| Strict 전면 | LOCAL-OK | R3-T4-S | **기각**(토큰·UX 비용) |
| 검증 생략 | LOCAL-OK | R3-T4-S | **기각** |
| L0 전면 + L1 형식 전면 + L2 핀포인트 | LOCAL-OK | R3-T4-S, R3-X-INT | **합의 좌표** |
| SOT-pin checker(설교 모든 노드) | LOCAL-OK | R3-T4-S, R3-X-INT §3 | **의무** |

### 3.6 State & Recovery
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| File-state (`_state.json` 진실 + status.md 파생) + phase enum guard | LOCAL-OK | R3-T5-S | **합의 좌표** |
| 풀 HSM (계층적 상태 머신) | LOCAL-OK | R3-T5-S | **기각**(과도) |
| 단일 enum 단독 | LOCAL-OK | R3-T5-S | **기각** |
| **Lock breaking + resume (단일 쓰기자 사망 대비)** | LOCAL-OK | §2.3.5 (b.bis) | **Phase 0 필수 산출물 (격상)** |

### 3.7 Configuration
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| 단일 CLAUDE.md에 12 에이전트 지시 전체 | LOCAL-OK | R2-T2-S | **기각**(컨텍스트 폭증) |
| CLAUDE.md 200라인 TOC + `.claude/skills/` 분산 | LOCAL-OK | R2-T2-S, R2-X-INT §5 | **합의 좌표** |

### 3.8 Phase 1 범위
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| 12 에이전트 전체 즉시 | LOCAL-OK | R1-X-CFL §3 | 토큰·복잡도 위험 |
| 핵심 3~5(Orchestrator + Sermon + Filter) | LOCAL-OK | R1-T1-S, R2-X-INT §3 | **합의 우세** |
| 4~5 에이전트 + 경량 순차 (R2 명시) | LOCAL-OK | R2-X-INT §3, R2-X-ADV §T-5 | **합의 좌표** |

### 3.9 자동 트리거
| 옵션 | 태그 | 출처 | 상태 |
|---|---|---|---|
| Claude Code 단독 자동 트리거 | LOCAL-BLOCKED | R2-T1-S | 구조적 불가 |
| 슬래시 커맨드 (사용자 개시) | LOCAL-OK | R2-X-INT §2 | **합의 좌표** |
| OS cron + 슬래시 호출 | LOCAL-OK | R2-T1-S | 구현 패턴 미정 (R2-X-PRK §7) |

### 3.10 외부 연동 (§2.4 표 참조)

---

## 4. 축 간 상충·미해결 지점

본 절은 "해결된 척" 금지 원칙에 따라 *현재 미해결*인 항목만 기록한다.

### 4.1 차수 간 (수직) — 해결됨, 다만 PRD에 두 층위 명시 필요
- **R2 t3(이론 — 고도 오케스트레이션 우위) ↔ R3 t2(코드 — Centralized + readonly fanout)**: 충돌 아님(층위 차이). PRD §System Architecture에 두 층위 모두 반영. 출처: R3-X-CFL §2.
- **R2 t1·t5(검증 원칙) ↔ R3 t4(L0/L1/L2 코드)**: 인용 관계.
- **R2 t2(설정) ↔ R3 t5(워크플로우 상태)**: 영역 분리.

### 4.2 미해결 충돌 (PRD 결정 대기)

> **우선순위 컬럼 추가**: P0 = Phase 0 진입 전 사용자 결정 필수 / P1 = Phase 1 진입 전 / P2 = Phase 2 이후. *우선순위 자체는 조사가 단정한 합의가 아니라 본 통합본의 적대적 성찰 기반 권고이며, PRD가 최종 확정한다.*

| ID | 우선 | 항목 | 출처 | 영향 |
|---|---|---|---|---|
| **C-A** | P0 | didim(weekly-works) vs churchTeam 역할 경계 | R1-T2-S, R1-X-CFL §2 | 설교 파이프라인 범위 전체 — **PRD 작성 전 선결** |
| **C-B** | **P0 (BLOCKER)** | Theology Filter 구현 = 2중 방어로 합의되었으나, **Hook이 비개발자 환경에서 자동 설치 가능한지 미검증** — `/install` 진입 자체가 차단되면 사용자(코드 무능 전제) 진입 불가 | R1-X-CFL §1 ↔ R2-X-INT §6, 적대적 성찰 A6 | `/install` 자동화 범위 + Bootstrap |
| **C-C** | P0 | Phase 1 범위 — "핵심 3~5" 합의는 있으나 정확한 에이전트 셋 미확정 | R1-X-CFL §3, R2-X-ADV §T-5 | 구현 복잡도 섹션 |
| **C-D** | **P0 (BLOCKER)** | 부교역자팀 역할 모델·권한 위계 — 12 에이전트가 목회 직무(설교/교육/심방/행정/예배/전도)와 매핑되는 *정체성*과 승인 위계가 부재. agent-registry 의무 필드는 기술 메타만 담음 | 4차 역방향(2026-04-29) | §Agents & Skills Catalog 정체성 — 사용자 결정 대기 |
| **C-E** | **P0 (BLOCKER)** | "사고·전략·실행 보조" 3차원 분해 부재 — 절대 목표 정의문의 세 축이 기능 카탈로그에 매핑되지 않음. 조사가 "실행" 편중 | 4차 역방향 | §Goals / §Solution — 사용자 결정 대기 |
| **C-F** | **P0 (BLOCKER)** | Bootstrap·자기 구현 워크플로우 부재 — soul.md DNA 상속 원칙은 R3-META에 단어로만, *PRD → churchTeam 자동 빌드* 시퀀스 미정 | 4차 역방향 + AgenticWorkflow-Template/soul.md(인용) | §Bootstrap & Installation — 사용자 결정 대기 |
| **C-G** | P1 | 한국어 자연어 에러·자가진단 UX 표준 부재 — 코드 무능 사용자의 traceback·MCP 만료·SOT 락 표현 표준 부재 (`feedback_weekly_dashboard.md` 같은 산발 메모리만 존재) | 4차 역방향 | §Operations / §Error UX — 사용자 결정 대기 |
| **C-H** | **P0 (BLOCKER)** | 자동화율 신학 기준선 부재 — "어디까지 자동이면 영적 사역 본질이 훼손되는가"의 기준선 미정. R2-X-INT §4 "목회자 검토 우선" 원칙만 존재 | 4차 역방향 | §ABSOLUTE ANCHOR / §Automation Threshold — 사용자 결정 대기 |
| **C-I** | P1 | Theology Filter 회귀 케이스 작성 주체·생성 방식 미정 — `회귀 ≥ 20개` 권고만 있고 작성자(자동 생성·부모 게놈 상속·목회자 수동) 미결 | R2-X-PRK §P1 + 4차 역방향 | §Theology Filter — 사용자 결정 대기 |
| **C-J** | P1 | 의도 해석 레이어(자연어 → dispatch) 부재 — 슬래시 커맨드/한국어 출력 외 *모호 요청 분해* 메커니즘 미조사 | 4차 역방향 | §Workflow Specification — 사용자 결정 대기 |
| **C-K** | P2 | 에이전트 간 토론·반박·합의 메커니즘 표면적 — Reflexion·Multi-Agent 이론(R2-T5)이 추상 인용에 머무름, 실제 debate/critique 구현 매핑 부재 | 4차 역방향 | §System Architecture (Phase 2 후보) — 사용자 결정 대기 |
| **U1** | **P0 격상** | 4.5 잠금 후 본문 갱신 시 재계획 메커니즘 — *운영 빈발 분기*. PRD까지 미루는 것 자체가 위험(적대적 성찰 A2) | R3-X-CFL §4, 적대적 성찰 A2 | §Workflow Specification — Phase 0 결정 필수 |
| **U2** | **P0 격상** | NotebookLM MCP `refresh_auth` 실패 시 차단/우회 — §2.4.bis fallback 매트릭스로 흡수 | R2-X-CFL §3, R3-X-CFL §4, 적대적 성찰 A3 | §Risks, §Integration — Phase 0 결정 필수 |
| **OQ#1** | **P0 격상** | Telegram MCP 권한·인젝션 모델 (`<channel source="telegram">` 게이트) — §2.4.bis fallback 매트릭스로 흡수 | R3-X-PRK §A1, 적대적 성찰 A3 | §Risks, §Integration |
| **OQ#3** | P1 | Skill 패키징·버전 관리 정책 | R3-X-PRK §A3 | §Skills Catalog |
| **OQ#4** | **P0 격상** | PreCompact ↔ status.md 동시성 — 단일 쓰기자라도 Hook은 별도 프로세스. SOT 손상 위험(적대적 성찰 A5) | R3-X-PRK §A4, 적대적 성찰 A5 | §State & Recovery — Phase 0 검증 필수 |
| **OQ#5** | P1 | workflow.md DAG 외부 dry-run 테스트 부재 | R3-X-PRK §A5 | §Testing |
| **OQ#6** | P2 | 비결정 산출(PNG/슬라이드) 회귀 검출 | R3-X-PRK §A6 | §Quality Gates |
| **OQ#7** | P2 | 다중 사용자 동시 편집 시 단일 쓰기자 가정 붕괴 | R3-X-PRK §A7 | §Operations(Phase 2) |

### 4.3 영구 제외 후보 (조사 단계 제안 — 단정 아님)
- 멀티 LLM 지원(GPT/Gemini) — 로컬 실행 복잡도 과도(R1-X-INT Red Zone)
- Logos/Accordance — SaaS 전제(LOCAL-BLOCKED)
- 분산 채택 시 합의 알고리즘(Paxos lite) — over-engineering(R3-X-PRK §B)

---

## 5. PRD 방향 조언 (골격 수준 — 단정 금지)

> 본 절은 R1-X-ADV / R2-X-ADV / R3-X-ADV의 *조언* 을 통합한다. 결정은 PRD 본문에서 사용자 승인 후 확정한다.

### 5.1 PRD 권장 골격 섹션 (조사가 누적 추천)
1. **Preamble — 선결 질문 2개** (didim 관계, Filter 구현) — *답을 PRD가 명시*
2. **Goals / Non-Goals** — Non-Goal에 클라우드 SDK·서버형 큐·외부 DB·다중 사용자(Phase 2까지)
3. **Technical Constraints / 기술 전제** — 자동 트리거 LOCAL-BLOCKED, 병렬 Phase 2 이후, state SOT, 2중 Filter
4. **System Architecture** — `.claude/` 구조 다이어그램 + 3 레이어(DAG·Orchestration·State&Validation), 노드 4-tuple
5. **Workflow Specification** — 부록 스키마(`id, phase, agent, skill, inputs[], outputs[], validators[], retry_budget, depends_on, exit_criteria`), 4.5 hard gate, D·E `depends_on` 동일
6. **Agents & Skills Catalog** — agent-registry 의무 필드(`type, writes, reads, mcp_required, local_tag`), 에이전트별 LOCAL 표
7. **Theology Filter** — 1차 프롬프트 + 2차 Hook + 회귀 케이스 ≥ 20 + 목회자 승인 필수
8. **Quality Gates** — L0/L1/L2 매트릭스 + SOT-pin checker 의무
9. **State & Recovery** — `_state.json` 스키마, status.md 페어, 원자 쓰기 규칙, PreCompact 상호작용
10. **Local Constraint Compliance** — §2.4 표 + LOCAL-BLOCKED 항목
11. **Risks & Open Questions** — §4.2 11개 항목 그대로
12. **Phased Delivery** — Phase 0(1주, Rapid-Prototype) / Phase 1(+2주, Balanced) / Phase 2(Hardening). **Phase 0 면제 의무필드 컬럼 자리**: agent-registry 5필드(`type, writes, reads, mcp_required, local_tag`)·노드 4-tuple·L0/L1/L2·SOT-pin checker 중 *Phase 0에서 면제·연기되는 항목 표*를 PRD가 결정해 추가. 적대적 성찰 B5(1주 일정과 의무필드 양립 불가) 해소 자리. **(P1-4 / S9 해소)** Phase 0의 "1주" 라벨은 *구현 일정*이며 *결정 일정*은 별도다. §4.2의 P0 BLOCKER 8개 사용자 결정은 Phase 0 진입 *이전*의 결정 세션(Pre-Phase 0)에서 닫혀야 한다. PRD는 두 일정을 분리해 명시할 것.
13. **What PRD Must NOT Do** — skill 내부 프롬프트 전문 / SDK 이름 박지 말 것

### 5.1.bis 4차 역방향(2026-04-29) — 추가 권고 섹션

> Round-01~03 조언이 누락한 섹션. round-04 미수행 상태이므로 *섹션 자리*만 권고하고 *내용*은 단정하지 않는다.

- **3a. Intent Resolution Layer** (C-J) — 자연어 모호 요청을 슬래시 커맨드 외 경로로 분해·dispatch하는 인터페이스 정의 자리. 본 통합본에는 근거 부재.
- **5a. Three-Axis Functional Decomposition** (C-E) — *사고 / 전략 / 실행* 보조 축에 12 에이전트와 파이프라인이 어느 축에 귀속되는지 매핑표. 절대 목표 정의문 직결.
- **6a. Pastoral Team Identity & Role Model** (C-D) — 12 에이전트의 목회 직무 매핑 + 권한 위계(목사 ↔ 부교역자 시뮬레이션). agent-registry 기술 메타와 분리하여 *정체성*만 다루는 별도 섹션.
- **7a. Theology Filter Regression Authoring** (C-I) — 회귀 ≥ 20개의 작성 주체·생성 절차·승인 흐름.
- **7b. Automation Threshold (신학 기준선)** (C-H) — ABSOLUTE ANCHOR 격상 후보. "자동화로 대체 불가" 단계의 식별 기준.
- **9a. Bootstrap & Self-Implementation** (C-F) — `/install` 단일 경로 + DNA 상속 시퀀스(parent-genome → churchTeam 인스턴시에이션) 명세 자리. 사용자 목적 ②(코드 무능 전제)의 직격 섹션.
- **10a. Error UX & Self-Diagnosis** (C-G) — 한국어 자연어 에러·MCP 만료·SOT 락 충돌의 표준 표현. 사용자 이탈 직격.
- **11+. Multi-Agent Debate (Phase 2)** (C-K) — Reflexion/critique를 이론 인용에서 구현 매핑으로 전환하는 자리. Phase 2 후보.

### 5.2 설계 원칙(조사 누적 — 보존)
- 신학 제약 = ABSOLUTE ANCHOR 격상 (R1-X-ADV §3)
- 사용자 = 담임목사 1인 고정 (Phase 1) (R1-X-ADV §4)
- 목회자 검토 단계 > 이론적 자동화 (R2-X-INT §4, R2-T5-S)
- team-leader 단독 SOT write (R3-X-INT §1)
- 4.5 = phase enum hard gate (R3-X-INT §2)
- SOT-pin checker = 모든 설교 노드 의무 (R3-X-INT §3)
- L0 = 모든 노드 (R3-X-INT §4)
- **DNA 상속 시퀀스 명세 = PRD 필수 산출물** — soul.md(부모 게놈 헌법·구조·검증·안전·기억·비판·투명) → churchTeam 인스턴시에이션 시퀀스를 *코드/슬래시 커맨드 레벨*까지 명세하지 않으면 PRD가 의미 상실. 적대적 성찰 C3 해소 자리(C-F / G17 직결)

---

## 6. 남은 공백 — 조사 자체가 다루지 않은/부족한 영역

> "있는 것을 확인"이 아니라 "없는 것을 찾는" 점검.

### 6.1 사실 확인(1층위) — 본 통합에 *반영되지 않은* 원본 파일
- **요약·교차분석·메타 30개**: 모두 §0.3 인덱스 + §2~§5에 출처로 인용 — *누락 없음*.
- **raw.md 14개**: 분량상 직접 인용은 수행하지 않음(§0.2 자인). 모든 summary가 raw 기반이며 출처 링크로 추적 가능하나, *미세 트레이드오프 단위*에서는 압축 손실이 존재(§6.2 #4 참조). PRD 작성 중 raw 재참조가 필요한 시점이 발생하면 출처 ID(R\*-T\*-R)로 즉시 복귀 가능. **(P0-1 / S1 해소)** 이전 표기 "**없음**"은 §0.2·§6.2 #4와 충돌하여 본 갱신에서 제거.

### 6.2 구조 분석(2층위) — PRD 입력으로 쓸 때 먼저 무너지는 지점
1. **C-A(didim 경계)** 미해결 → §System Scope 전체 재작성 위험
2. **C-B(Hook 자동 설치)** 미검증 → §`/install` 사양 공백 → 운용성 위험
3. **C-C(Phase 1 셋 미확정)** → §Phased Delivery 구체화 시 흔들림
4. raw.md의 *세부 트레이드오프*가 본 통합에서 요약본 + cross-analysis 수준으로 압축됨 → PRD 작성 시 raw 재참조 필요한 항목이 발생하면 출처 ID(R\*-T\*-R)로 즉시 복귀 가능하나, 본 문서만으로는 일부 미세 근거가 압축 손실됨

### 6.3 역방향(3층위) — 조사 자체가 빠뜨린 축
| # | 미조사 축 | 사용자 목적 영향 | 권고 |
|---|---|---|---|
| G1 | **사용자(목사) 실제 운영 시나리오 검증 (UX 마찰 실측)** | Phase 1 채택 위험 | R2-X-PRK §8 — 별도 사용자 리서치 |
| G2 | **didim vs churchTeam 1:1 기능 비교 표** | 범위 미확정 | R1-X-PRK §P0 — PRD 작성 전 필수 |
| G3 | **설교 파이프라인 토큰 실측** | Phase 1 범위 결정 근거 | R2-X-PRK §P3 |
| G4 | **Theology Filter 회귀 테스트 케이스 ≥ 20개** | 신학 품질 보증 | R2-X-PRK §P1 |
| G5 | **원어 DB 옵션 실제 비교(설치·라이선스·완전성)** | ExegesisAgent 설계 | R1-X-PRK, R2-X-PRK §P2 |
| G6 | **한국어 신학 용어 임베딩 특성** | 프롬프트 언어 전략 | R2-X-PRK §5 |
| G7 | **4차 차수(예: 운영·보안·재해 복구 축)** 부재 | 세션 헤더 "1~4차"와 실제 3차 불일치 | 추가 차수 필요 여부를 사용자에게 확인 |
| G8 | **다중 사용자 시나리오** (단일 쓰기자 가정 붕괴) | OQ#7 / Phase 2 | 본 PRD는 Phase 2까지 Non-Goal로 두거나 별도 차수 필요 |
| G9 | **데이터 백업·재해 복구 전략** | 산출물 손실 위험 | 미조사 — 추가 검토 필요 |
| G10 | **개인정보·교인 데이터 처리 윤리/법적 경계** (행정 자동화 시) | 법·윤리 리스크 | 미조사 — 별도 축 필요 |
| G11 | **비용·리소스 모델**(Claude Code Max 토큰 한도 vs 월 사용량) | 운영 지속성 | R1-T4-S 추정치만, 실측·예산화 미수행 |
| G12 | **출력 산출물 형식 결정**(md / HTML / docx / PNG) | didim 중복·운영자 워크플로우 | R1-X-PRK — 미해결 |

### 6.4 역방향 4차 (2026-04-29) — 미수행 축 / Round-04 권고

> 직전 성찰 보고서가 식별한 추가 공백. **Round-04 조사는 미수행 — 사용자 승인 대기**. 본 절은 등록만 수행하며 결론은 단정하지 않는다.

| # | 미조사 축 | 사용자 목적 영향 | 판정 | Round-04 권고 묶음 | PRD 결정 ID |
|---|---|---|---|---|---|
| G13 | 의도 해석 레이어(자연어 → dispatch) | 목적 ② (코드 무능 전제) | 부분 blocker | 묶음-γ | C-J |
| G14 | 부교역자팀 역할 모델·권한 위계 | 목적 ① (영적 사역 본질) | **BLOCKER** | 묶음-α | C-D |
| G15 | "사고/전략/실행" 3차원 분해 | 목적 ① (절대 목표 정의문 직결) | **BLOCKER** | 묶음-α | C-E |
| G16 | 에이전트 간 토론·반박·합의 메커니즘 | 목적 ① ("팀" 본질) | 부분 blocker | 묶음-α (Phase 2) | C-K |
| G17 | Bootstrap·자기 구현 워크플로우 (PRD → churchTeam 자동 빌드) | 목적 ② 직격 | **BLOCKER (최상위)** | 묶음-β | C-F |
| G18 | 한국어 자연어 에러·자가진단 UX | 목적 ② (사용자 이탈) | **BLOCKER** | 묶음-β | C-G |
| G19 | 자동화율 신학 기준선 (어디까지 자동인가) | 목적 ① (영적 사역 본질) | **BLOCKER** | 묶음-δ (신학 + fact-checker) | C-H |
| G20 | Theology Filter 회귀 작성 주체·생성 방식 | 목적 ①·② 동시 | **BLOCKER** | 묶음-γ | C-I |

### 6.4.bis 적대적 성찰 반영 메모 (2026-04-29)
> 적대적 에이전트 A/B/C 기반 성찰에서 *방어 불가*로 확정된 14개 항목을 본 통합본에 반영. 반영 위치 매핑:
> - **A1·OQ#4(A5)** → §2.3.5 (b.bis), §3.6 신규 행, §4.2 P0 격상
> - **A2(U1)·A3(U2/OQ#1)** → §4.2 P0 격상, §2.4.bis fallback 매트릭스
> - **A6(C-B)** → §4.2 P0 BLOCKER 격상, §6.4 묶음-β 흡수
> - **B1** → §1.1 "12개" 단정 삭제 + 조건부 표기
> - **B4** → §0.6 Executive Digest 신규
> - **B5** → §5.1 #12 Phase 0 면제 의무필드 컬럼 자리
> - **C2** → §4.2 P0/P1/P2 컬럼
> - **C3** → §5.2 DNA 상속 시퀀스 명세 한 줄
> - **C4** → 부록 A ★ 결정적 인용 표지
> - **C5** → §2.4.ter LOCAL-PARTIAL 기능 단위 분해 표
> - **C6** → §1.1.bis(3축)·§1.1.ter(부교역자팀 정체성) 격상
> - **C1** → §0.3.bis 출처 ID 정책

**Round-04 묶음 안 (보존 — 단정 아님)**:
- 묶음-α: G14·G15·G16 — 부교역자팀 정체성 축
- 묶음-β: G17·G18 — Bootstrap·UX 축
- 묶음-γ: G13·G20 — 의도 해석·Theology 회귀 축
- 묶음-δ: G19 — 자동화율 신학 기준선 (신학 도메인 fact-checker 필수)

**Round-04 미수행 사유**: 사용자 승인 대기. 동시 dispatch 시 rate limit 위험(R2-T1 SaaS 사례 인용) → 묶음 분할·순차 dispatch 또는 동시 dispatch는 사용자 결정.

**묶음-β 추가 흡수 (적대적 성찰 A6 / C-B)**: `/install` Hook 자동 설치(Python·uv·NotebookLM CLI·yt-dlp·Playwright) 비개발자 환경 검증을 묶음-β(Bootstrap·UX 축)에 추가. 검증 미수행 시 사용자 진입 자체 차단(목적 ② 직접 훼손).

---

## 부록 A — 통합 출처 매핑(요약본 → 본 문서 위치)

> **★ 표지** = *결정적 인용*(해당 결정의 핵심 근거). 무표지 = 보조 인용. 적대적 성찰 C4 해소.

| 출처 ID | 본 문서 반영 위치 |
|---|---|
| R1-T1-S/R ★ | §2.1.1, §3.1, §3.4, §3.8 |
| R1-T2-S/R ★ | §2.1.2, §4.2 C-A, §6.3 G2 |
| R1-T3-S/R | §2.1.3, §3.4 |
| R1-T4-S/R | §2.1.4, §6.3 G11 |
| R1-X-INT ★ | §2.1.5 (Green/Yellow/Red Zone) |
| R1-X-CFL ★ | §2.1.5 (충돌 1·2·3), §4.2 C-A·C-B·C-C |
| R1-X-PRK | §2.1.5 P0/P1/P2, §4.2, §6.3 |
| R1-X-ADV | §2.1.6, §5.1, §5.2 |
| R2-T1-S/R ★ | §2.2.1, §3.4, §3.9 |
| R2-T2-S/R ★ | §2.2.2, §3.7 |
| R2-T3-S/R | §2.2.3, §3.2, §4.1 |
| R2-T4-S/R ★ | §2.2.4, §2.4, §3.10 |
| R2-T5-S/R ★ | §2.2.5, §5.2 |
| R2-X-INT ★ | §2.2.6 (4/4·3.5/4 합의), §3.4, §3.7, §3.8 |
| R2-X-CFL ★ | §2.2.6 (불일치 1~4), §3.4, §4.2 U2 |
| R2-X-PRK | §2.2.6 파킹, §6.3 G3·G4·G5·G6 |
| R2-X-ADV | §2.2.7, §5.1 (T-1~T-6) |
| R3-T1-S/R ★ | §2.3.1, §3.1 |
| R3-T2-S/R ★ | §2.3.2, §3.2 |
| R3-T3-S/R | §2.3.3, §3.3 |
| R3-T4-S/R ★ | §2.3.4, §3.5 |
| R3-T5-S/R ★ | §2.3.5, §3.6 |
| R3-X-INT ★ | §2.3.6 (5/5 합의 + 운영 불변 5개) |
| R3-X-CFL ★ | §2.3.6 (C1~C5, 차수간 경계, 식별자 정책, U1·U2) |
| R3-X-PRK ★ | §2.3.6 파킹, §4.2 OQ#1·#3~#7 |
| R3-X-ADV | §2.3.7, §5.1 |
| R0-IDX | §0.2, §0.3 |
| R1-META / R2-META / R3-META | §0.1, §0.5 |

---

## 부록 B — 본 문서가 단정하지 않은 것

다음은 PRD가 결정해야 할 항목으로 *명시적으로* 보존된다.

1. didim ↔ churchTeam 경계 (C-A)
2. Theology Filter Hook 비개발자 자동 설치 가능 여부 (C-B)
3. Phase 1 정확한 에이전트 셋 (C-C)
4. 4.5 잠금 후 재계획 정책 (U1)
5. NotebookLM 인증 실패 정책 (U2)
6. Telegram 권한 모델, Skill 버전 관리, PreCompact 동시성, DAG 테스트, 비결정 회귀, 다중 사용자(OQ#1·#3~#7)
7. 외부 연동 채택 범위(LOCAL-PARTIAL 항목들의 실제 도입 여부)
8. 출력 산출물 형식(md/HTML/docx)
9. 비용 모델, 백업 정책, 개인정보 처리 경계 (G9·G10·G11·G12)
10. 4차 차수(운영·보안·재해 복구) 추가 수행 여부 (G7)
11. **부교역자팀 역할 모델·권한 위계** (C-D / G14) — 4차 역방향 식별, round-04 미수행
12. **"사고/전략/실행" 3차원 분해** (C-E / G15) — 4차 역방향 식별, round-04 미수행
13. **Bootstrap·자기 구현 워크플로우** (C-F / G17) — 4차 역방향 식별, round-04 미수행
14. **한국어 자연어 에러·자가진단 UX 표준** (C-G / G18) — 4차 역방향 식별, round-04 미수행
15. **자동화율 신학 기준선** (C-H / G19) — 4차 역방향 식별, round-04 미수행
16. **Theology Filter 회귀 케이스 작성 주체·생성 방식** (C-I / G20) — round-04 미수행
17. **의도 해석 레이어**(자연어 → dispatch) (C-J / G13) — 4차 역방향 식별, round-04 미수행
18. **에이전트 간 토론·반박·합의 메커니즘 구체화** (C-K / G16) — Phase 2 후보, round-04 미수행
19. Round-04 dispatch 묶음(α·β·γ·δ) 채택·동시/순차 결정 — 사용자 승인 대기

— end of final-research.md —
