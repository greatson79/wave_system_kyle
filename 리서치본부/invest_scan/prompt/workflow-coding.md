# InvestScan — Infrastructure Build 구현 설계서 v3.6

> **목적**: `workflow.md` Step 1-15의 철학·목적·핵심 기능을 완벽히 보존하면서, Claude Code Orchestrator + Agent Swarm + TDD + 계층적 SOT + English-First + 한국어 번역 쌍 체계로 완전 자동 실행하는 기반 구조를 구축한다.
>
> **참조 문서**: `workflow.md` (실행 대상 Step 1-15), `prd.md` (요구사항 SOT), `CLAUDE.md` (프로젝트 헌법)
>
> **v3.0 변경**: P5(English-First + Korean Pair) 원칙 추가 및 전 섹션 반영
>
> **v3.1 변경**: 심층 성찰(Critical Reflection) 반영 — CR-1(Hook 이벤트 실제 API 정렬), CR-2(pacs_score 인터페이스 수정), CR-3(sot_write_guard 경로 수정), HR-1~5(Agent 정의·Fork 동기화·Gate 수정·번역 트리거·date 플레이스홀더), MR-1~3(Hook 순서·픽스처·RLM 호환성), ADR-015, §18 Agent 정의 전문 추가
>
> **v3.2 변경**: 품질 절대주의(P4) + English-First(P5) 완전성 성찰 반영 — Q1(P1 Critical Opus 빌더), Q2(Intelligence Engine Reflect-Revise 루프), Q3(TDD 표준 85%), Q4(D3 품질 근거 재술), Q5(Step 15 Watchlist 번역), Q6(Fd 금융 도메인 pACS 차원), Q7(Telegram 요약 설계), Q8(NarrativeOutput 번역 전 게이트)
>
> **v3.3 변경**: 3차 성찰(Critical Reflection) 반영 — CR-4-1(제목 v3.2), CR-4-2(get_required_coverage 기본값 80→85 로직 버그 수정), CR-4-3(SubAgent 예시 coverage 80%→85%), CR-4-4(ADR-014 Step 수 5→6), IR-1(TDG 범위), IR-2(Phase E TDG), IR-3(§14 누락 파일), IR-4(/translate step15), IR-5(Translator Skill Fd), IR-6(SOT Inspector 완전 표시), IR-7(Translation Fork Step15), IR-8(Phase B p1-critical-builder), IR-9(§4-4 template 일관성), IR-10(Phase D Step15), MR-1(tdd_status 주석), MR-2(이중구분선), MR-3(Fork B/C p1-critical-builder 흐름), MR-4(NarrativeOutput JSON 스키마 정의)
>
> **v3.4 변경**: 할루시네이션 원천봉쇄 성찰 반영 — P6(Python-First 의사결정 원칙 신규), H-1(compliance_filter.py 10개 금지 패턴 Python regex 상수 명세), H-2(steeps_classifier.py STEEPs 키워드 룩업 테이블 — lowercase s/uppercase S 구분 포함), H-3(stock_selector.py Category A/B 결정론적 임계값 + classify_category() 명세), H-4(validate_report_quality.py Python regex 1차 검증 8기준 명세), H-5(citation_validator.py 신규 모듈 — NarrativeOutput 수치 인용 검증), builder-a steeps_classifier 85%→95%(P1 Critical), builder-c stock_selector 85%→95%(P1 Critical), builder-e validate_report_quality 85%→90%(Core Pipeline) + citation_validator.py 추가, §6-1 TDD 등급표 4개 모듈 승격, ADR-016(Python-First Decision Architecture), §19 신규(할루시네이션 원천봉쇄 — Python-First 결정론 명세 전문)
>
> **v3.5 변경**: 설계 결함(Design Gap) 성찰 반영 — CR-5-1(tdd_verify.py COVERAGE_TIERS 갱신 — steeps_classifier·stock_selector P1 Critical 95%, validate_report_quality·citation_validator Core Pipeline 90% 추가), CR-5-2(p1-critical-builder workspace 모듈별 4개 분리 — SOT 쓰기 충돌 해소), CR-5-3(citation_validator 파이프라인 연결 — §9-7-2 content_gate 직후 호출 + §2·§11 흐름 반영), CR-5-4(Reflect-Revise 루프 build_narrative_with_retry() 명세 — 카운터·catch·3회 초과 fallback), IR-11(§5 Fork A·C·E v3.4 승격 반영), IR-12(§2 Stage 2 흐름에 python_validate_first() 단계 추가), IR-13(STEEPs E2→E_env 표기 전체 통일), IR-14(§5 Fork 동기화 코드 실행 컨텍스트 분리 레이블), DG-9(§18-6 steeps/stock 테스트 지침 추가), DG-10(run_m05.py 명세 신규), DG-11(citation_validator context_data 출처 명시), DG-12(Agent Teams 품질 기준 활성화 조건 명세)
>
> **v3.6 변경**: 적대적 성찰(Adversarial Reflection) 반영 — I-1(M0.0 마일스톤: Day 0 즉시 Telegram Hello + DG-00), I-2(Day 0 설치 시간 현실적 범위 명세), I-3(accuracy_tracker.py 이중 측정 윈도우 4주+8주 — 타임프레임 중앙값 반영), I-4(Bullish 판정 임계값 +2%→+1% 완화), I-5(KS-1 타이밍 라벨 "Month 2"→"Month 3" 수정 — 측정 지연 현실 반영), I-6(FDR/pykrx/dart-fss 가용률 추적 + 명시적 fallback chain §12 Level 4 확장), I-7(Category B 신흥 테마 알고리즘 `or 1` 제로가드 버그 수정 + MIN_ABS_COUNT 안전망 §20-1), I-8(envscan_bridge.sh 최소 데이터 검증 로직 §20-2), I-9(Section 15.1 법적 근거 재정렬 §20-3), I-10(계속적 관계 가드레일 §20-3), I-11(portfolio 컨텍스트 기능: state.yaml portfolio 섹션 + DG-17 §20-4), I-12(Bear Case UX 개선 — 위치 하단 이동 + onboarding 설명 §18-5·§20-5), I-13(Naive Baseline 3가지 비교 전략 §20-6), ADR-017(Adversarial Reflection Architecture Decisions)

---

## 절대 기준 (5개 — 모든 구현 결정의 상위 규칙)

| # | 기준 | 내용 |
|---|------|------|
| **P1** | 워크플로우 보존 | `workflow.md` Step 1-15의 철학·목적·핵심은 일체 변경하지 않는다. 바꾸는 것은 **실행 Infrastructure**뿐이다. |
| **P2** | SOT 일관성 | 단일 파일 SOT + 계층적 메모리 구조 아래서 수십 개 에이전트가 동시에 작동해도 데이터 불일치가 발생하지 않는다. |
| **P3** | RLM 보존 | RLM(Recursive Language Model) 패턴은 어떤 경우에도 훼손되지 않는다. |
| **P4** | 품질 절대주의 | 속도·토큰 비용 완전 무시. 유일한 기준은 **최종 결과물의 품질**이다. |
| **P5** | English-First + Korean Pair | 워크플로우 실행 시 모든 에이전트의 사고·계획·중간 산출물을 영어로 수행한다. 이후 @translator SubAgent가 각 단계 산출물을 한국어로 번역하여 쌍(pair)으로 제공한다. |
| **P6** | Python-First 의사결정 | 모든 분류·검증·결정은 Python 코드로 구현한다. LLM은 NarrativeOutput 텍스트 생성만 담당한다. **"Python이 판사, LLM은 내레이터"** — 할루시네이션 원천봉쇄. |

---

## 확정 설계 결정 요약 (D1–D7)

| # | 결정 영역 | 선택 | 근거 |
|---|---------|------|------|
| D1 | SOT 일관성 | **계층적 소유권 구조** | 수십 에이전트 동시 작동 + 불일치 없음 유일한 충족 방법 |
| D2 | RLM 패턴 | **중앙집중 RLM (Lead 단일 체인)** | /resume 지원 + 기존 save/restore_context.py 수정 최소화 |
| D3 | Agent 실행 | **SubAgents 우선, Agent Teams 선택적** | **(품질 1차)** 각 SubAgent가 전문 데이터 소스·모듈에 단독 집중 → 전문 깊이 우위. Agent Teams 활성화 기준: ①Research 신호 상충, ②fact-checker CRITICAL 발견 (v3.5 DG-12 명세) |
| D4 | TDD 강도 | **차등 기준** (P1: 95% / 핵심: 90% / **표준: 85%** / 인프라: 75%) | v3.2 Q3: 비용 무관 원칙 → 표준 80%는 속도 타협선. 품질 절대주의 = 최소 85%. 인프라(Hook) 75% 유지 (코드 로직 단순) |
| D5 | Swarm 크기 | **3+5+2+1** (Research+Impl+Review+Translation) | 데이터소스·Fork·역할·번역에 정확히 매핑 |
| D6 | Phase 순서 | **B → A → C → D → E** | SOT 보호 인프라 없이 에이전트 실행 = SOT 오염 위험 |
| D7 | 언어 정책 | **English-First 실행 + @translator 한국어 쌍** | AI 영어 추론 품질 최대화(P4) + 한국어 최종 결과물 제공 |

---

## 목차

1. [전체 아키텍처 개요](#1-전체-아키텍처-개요)
2. [3계층 실행 모델](#2-3계층-실행-모델)
3. [Agent 실행 모델 — SubAgents 우선 + 영어 실행 강제](#3-agent-실행-모델)
4. [Agent Swarm 구성 (3+5+2+1)](#4-agent-swarm-구성)
5. [Fork 전략](#5-fork-전략)
6. [TDD 통합 — 차등 기준](#6-tdd-통합)
7. [계층적 SOT 설계 (D1)](#7-계층적-sot-설계)
8. [중앙집중 RLM 통합 (D2·D3)](#8-중앙집중-rlm-통합)
9. [Hooks 설계](#9-hooks-설계)
10. [Skills 설계](#10-skills-설계)
11. [Commands 설계](#11-commands-설계)
12. [Fallback 경로](#12-fallback-경로)
13. [품질 기준 파일](#13-품질-기준-파일)
14. [전체 파일 구조](#14-전체-파일-구조)
15. [구현 Phase 계획 (B→A→C→D→E)](#15-구현-phase-계획)
16. [settings.json 변경 사항](#16-settingsjson-변경-사항)
17. [P5 원칙 전문 — English-First + Korean Pair](#17-p5-원칙-전문)
18. [Agent 정의 파일 전문 (5개 신규)](#18-agent-정의-파일-전문)
19. [할루시네이션 원천봉쇄 — Python-First 결정론 명세](#19-할루시네이션-원천봉쇄)
20. [적대적 성찰 개선 명세 (v3.6 — I-2~I-13)](#20-적대적-성찰-개선-명세)

---

## 1. 전체 아키텍처 개요

```
┌──────────────────────────────────────────────────────────────────────────────┐
│               CLAUDE CODE SESSION — Team Lead / Orchestrator                 │
│                                                                              │
│  Global SOT:  .claude/state.yaml          ← Orchestrator 전용 쓰기           │
│  RLM Chain:   .claude/context-snapshots/  ← 중앙집중 (Lead 단일 체인)          │
│  Task List:   ~/.claude/tasks/investscan/ ← 모든 에이전트 읽기·Lead 쓰기       │
│  Language:    English-First (P5-A)        ← 모든 에이전트 영어 실행            │
└──────────────┬──────────────────────────────────────┬────────────────────────┘
               │ spawn SubAgent (영어 프롬프트)         │ spawn SubAgent
   ┌───────────▼───────────┐          ┌───────────────▼───────────────────────┐
   │   Research SubAgents  │          │      Implementation SubAgents          │
   │   (3명 — D5)           │          │      (5명 — D5)                        │
   │                       │          │                                        │
   │ ① envscan-subagent    │          │ ④ builder-a  (Fork A)                 │
   │ ② fred-subagent       │          │ ⑤ builder-b  (Fork B)                 │
   │ ③ gnews-subagent      │          │ ⑥ builder-c  (Fork C)                 │
   └───────────┬───────────┘          │ ⑦ builder-d  (Fork D)                 │
               │                      │ ⑧ builder-e  (Fork E)                 │
               │                      └───────────────┬───────────────────────┘
               │ English results                      │ English modules
   ┌───────────▼──────────────────────────────────────▼──────────────────────┐
   │               Review SubAgents (2명 — D5)                                │
   │   ⑨  @reviewer     — 코드 품질 + 아키텍처 준수 (L2)                        │
   │   ⑩  @fact-checker — 수치·필드명·신호 정합성 검증                           │
   └─────────────────────────────────────────────────────────────────────────┘
               │ English outputs (review passed)
   ┌───────────▼─────────────────────────────────────────────────────────────┐
   │               Translation SubAgent (1명 — D7)                            │
   │   ⑪  @translator  — 영어 원본 → 한국어 번역 쌍 생성                         │
   │       trigger: 각 Step 완료 후 자동 (translation_trigger.py)               │
   │       output: [file].ko.md + pACS log + glossary 업데이트                 │
   └─────────────────────────────────────────────────────────────────────────┘

※ Agent Teams (선택적 — D3, v3.5 DG-12: 품질 기준 활성화 조건 명세):
   활성화 조건 (품질 기준 — 속도 무관):
   ① Research Phase에서 SubAgent 3개가 서로 상충하는 매크로 신호를 반환할 때
      (예: FRED는 금리 인하 신호, EnvScan은 스태그플레이션 신호)
      → Agent Teams로 경쟁 가설 토론 → 팀 합의 우선 (단일 SubAgent 보다 품질↑)
   ② fact-checker가 1개 이상의 CRITICAL 불일치(FRED series_id 오류, STEEPs 오분류)를 발견 시
      → Agent Teams로 교차 검증 (독립적 다중 관점 > 단일 에이전트 재검토)
   비활성화 기준: 3개 SubAgent 신호 방향 일치 시 → SubAgents 충분 (Teams 불필요)

계층적 SOT (D1):
   .claude/state.yaml                    ← Global (Orchestrator 최종 Merge)
   .claude/state/phase-research.yaml     ← Research Lead
   .claude/state/phase-planning.yaml     ← Planning Lead
   .claude/state/phase-impl.yaml         ← Impl Lead
   .claude/agent-workspace/[id].yaml     ← 각 SubAgent 전용
```

---

## 2. 3계층 실행 모델

### Layer 1 — Stage 1: Headless Data Collection (launchd)

| 구성요소 | 역할 | 실행 시점 |
|---------|------|---------|
| `weekly_orchestrator.py` | 데이터 수집 총괄 | 일요일 20:00 launchd |
| ProcessPoolExecutor Fork | FRED/EnvScan/GlobalNews/Korea 병렬 수집 | subprocess fork ×4 |
| Global SOT 업데이트 | `state.yaml` 최종 Merge 기록 | Orchestrator 단독 |
| Telegram 알림 | 수집 완료·오류 알림 (한국어 — HITL 채널) | 각 단계 완료 후 |

**Stage 1 실행 흐름** (모든 내부 처리 영어):
```
[M0.0 — v3.6 I-1: Day 0 설치 완료 즉시 1회 실행]
personalizer.py --hello-test
  → Telegram: "✅ InvestScan 설치 완료. Claude Code가 코드를 완성하는 중입니다.
               Week 2에 첫 리포트가 도착합니다. 이 메시지가 오면 연결 성공입니다."
  → 10분 이내 Telegram 수신 확인 → 침묵 불안 제거
  ↑ 설치 직후 1회 전송. 이후 매주 Stage 1이 대신함.

launchd (일요일 20:00)
  → weekly_orchestrator.py --mode data-collection  [English execution]
  → Fork A: FRED API (10개 series_id)
  → Fork B: EnvScan database.json + normalizers
  → Fork C: GlobalNews signals.parquet
  → Fork D: Korea 시장 데이터 (FDR + pykrx)
  → Merge → state.yaml 업데이트 (English keys/values)
  → context_[날짜].json 생성 (English field names, English content)
  → Telegram: "데이터 수집 완료. /weekly-report로 리포트 생성하세요."
    ↑ 이 메시지만 한국어 (사용자 직접 수신 채널)
```

### Layer 2 — Stage 2: Interactive Report Generation (Claude Code)

**Stage 2 실행 흐름** (P5-A: 영어 실행, P5-B: 한국어 번역 쌍):
```
사용자: /weekly-report
  → Orchestrator: context_[날짜].json 검증 [English]
  → Orchestrator: context_data 로드 (context_[날짜].json → dict)  ← citation_validator 입력 준비
  → intelligence_engine.build_prompt()   [English prompt]
  ↓ [v3.5 CR-5-4: build_narrative_with_retry(max_retries=3)]
  LOOP START (retry_count = 0, max = 3):
    → Claude Code LLM → NarrativeOutput   [English narrative — M0.5]
    → [v3.5 IR-12: P6 Python 1차 검증 단계]
    → validate_report_quality.python_validate_first(narrative)
      → FAIL → retry_count += 1 → LOOP (실패 기준 컨텍스트 첨부)
      → PASS → 다음 단계
    → compliance_filter 10개 패턴 적용     [English patterns — H-1]
    → [v3.2 Q2: Reflect-Revise 루프]
    → @reviewer: 8개 기준 체크 (LLM — Python 통과 후 2차)
      → FAIL → retry_count += 1 → LOOP (실패 기준 컨텍스트 첨부)
      → PASS → 다음 단계
  LOOP END (3회 초과 시 → best_attempt 저장 + HITL 에스컬레이션)
  ↓ [v3.4 H-5: citation_validator 수치 인용 검증]
  → citation_validator.validate_citations(narrative.text, context_data)
    → validated=False → log warning + @reviewer에 flag (파이프라인 계속)
    → validated=True  → 정상 진행
  ↓ [v3.2 Q8: 번역 전 NarrativeOutput 내용 게이트]
  → content_gate: NarrativeOutput 8기준 최종 확인
  → report_generator Jinja2 렌더링       [English template → English report]
  ↓ [P5-B 트리거: translation_trigger.py]
  → @translator SubAgent spawn
  → weekly-report-[date].ko.md 생성      [Korean translation]
  → pACS 검증 (GREEN ≥ 70)
  → HITL-3: 사용자에게 한국어 번역본 확인 요청
  → 승인: Telegram 발송 (한국어 버전) + output/reports/ 양본 저장
```

### Layer 3 — Monitoring (Continuous)

| 구성요소 | 역할 | 언어 |
|---------|------|------|
| `watchdog.py` | 상태 모니터링 + 재시도 | English (내부) |
| `health_dashboard.py` | 시스템 상태 시각화 | English (내부) |
| `accuracy_tracker.py` | 예측 정확도 추적 | English (데이터) |
| Telegram notifier | 사용자 알림 | Korean (사용자 채널) |

---

## 3. Agent 실행 모델

### D3 + D7: SubAgents 우선 + English-First 강제

```
모든 SubAgent 프롬프트 작성 원칙 (P5-A):

  ✅ 영어로 작성:
     - SubAgent 목적 설명
     - 수행할 태스크 지시
     - 기대 출력 형식
     - 오류 처리 지침
     - agent-workspace 기록 형식

  ✅ 영어로 생성:
     - 중간 산출물 (schema-mapping.md, blueprint.md)
     - NarrativeOutput JSON
     - 코드 파일 (변수명·주석·docstring)
     - 로그 파일
     - state.yaml 모든 값

  ✅ 한국어 허용 (사용자 직접 수신):
     - HITL 안내 메시지 (Step 6, 8)
     - Telegram 알림 메시지
     - 최종 주간 리포트 (.ko.md — @translator 생성)
```

### English SubAgent 프롬프트 패턴

```python
# Orchestrator가 SubAgent 호출하는 방식 (모두 영어)

# Research SubAgent
result = Agent(
    subagent_type="general-purpose",
    prompt="""
    Perform EnvironmentScan database.json discovery for InvestScan.

    Tasks:
    1. Search paths: ~/Documents/EnvironmentScan/, ~/Desktop/Ai_works/, ~/
    2. Extract actual field names (STEEPs category, pSST score, summary fields)
    3. Determine pSST normalization scale (0-100 | 0-10 | 0-1)
    4. Write ALL findings to .claude/agent-workspace/envscan-agent.yaml
    5. Return JSON: {"found": bool, "path": str, "schema": {field_mappings}}

    Write only English to workspace files. Do not write to state.yaml directly.
    """,
    run_in_background=True
)

# Implementation SubAgent
result = Agent(
    subagent_type="general-purpose",
    prompt="""
    Implement config.py for InvestScan per docs/code-convention.md.

    English-first requirements:
    - Write all code, comments, and docstrings in English
    - Variable names: English snake_case
    - Log messages: English

    TDD protocol:
    1. Write tests/test_config.py first (test_spec below)
    2. Run pytest → confirm FAIL (red)
    3. Implement config.py
    4. Run pytest → achieve PASS (green, coverage ≥ 85%)  # v3.3 CR-4-3: standard tier = 85%

    test_spec: Keychain loading success/failure, YAML parsing, singleton pattern,
               sentiment_weight==0.0 assertion
    Write progress to .claude/agent-workspace/builder-a.yaml.
    Return: {"module": "config.py", "coverage": float, "tests_passed": bool}
    """
)

# Translation SubAgent — 번역만 한국어로
result = Agent(
    subagent_type="translator",
    prompt="""
    Translate the English output from Step N to Korean.

    Source: output/schema-mapping.md
    Target: output/schema-mapping.ko.md
    Glossary: translations/glossary.yaml (load first, update after)

    Protocol: Follow translator.md 7-step protocol exactly.
    pACS minimum: 70 (GREEN). Re-translate if RED (<50).
    Write pACS log to pacs-logs/step-2-translation-pacs.md.
    Update glossary with new InvestScan terms found.
    Return: {"pacs_score": int, "grade": str, "new_terms": int}
    """
)
```

---

## 4. Agent Swarm 구성 (3+5+2+1)

### 4-1. Research SubAgents (3명)

```yaml
research_agents:
  - id: envscan-agent
    type: general-purpose
    prompt_language: English
    scope: "EnvironmentScan database.json discovery + schema analysis"
    workspace: .claude/agent-workspace/envscan-agent.yaml
    returns: discovered_paths + discovered_schema (English values)

  - id: fred-agent
    type: general-purpose
    prompt_language: English
    scope: "FRED API connectivity + 10 series_id availability check"
    workspace: .claude/agent-workspace/fred-agent.yaml
    returns: packages.fred_ready + connectivity status

  - id: gnews-agent
    type: general-purpose
    prompt_language: English
    scope: "GlobalNews signals.parquet discovery + pyarrow parse check"
    workspace: .claude/agent-workspace/gnews-agent.yaml
    returns: discovered_paths.gnews_signals + file_exists

completion_trigger: phase-research.yaml merge_ready: true
translation_trigger: none (technical discovery — no translation needed)
```

### 4-2. Implementation SubAgents (5명)

```yaml
impl_agents:
  - id: builder-a
    fork: A
    modules: [config.py, normalizers.py, steeps_classifier.py]
    tdd_coverage: [85%, 90%, 95%]       # steeps_classifier = P1 Critical (95%) — v3.4 H-2: 할루시네이션 6단계 체인 방어
    prompt_language: English
    workspace: .claude/agent-workspace/builder-a.yaml
    # v3.5 CR-5-2: 모듈별 전용 workspace — SOT 쓰기 충돌 방지 (Fork A/B/C 동시 실행)
    agent_for_p1: p1-critical-builder
    p1_workspace: .claude/agent-workspace/p1-cb-steeps.yaml   # steeps_classifier 전용

  - id: builder-b
    fork: B
    modules: [signal_bridge.py, dedup.py, compliance_filter.py]
    tdd_coverage: [85%, 85%, 95%]       # compliance_filter = P1 Critical (95%)
    prompt_language: English
    workspace: .claude/agent-workspace/builder-b.yaml
    # v3.2 Q1: compliance_filter는 p1-critical-builder (Opus) 사용
    # v3.5 CR-5-2: 전용 workspace — Fork A와 파일 충돌 없음
    agent_for_p1: p1-critical-builder
    p1_workspace: .claude/agent-workspace/p1-cb-compliance.yaml  # compliance_filter 전용

  - id: builder-c
    fork: C
    modules: [synthesize_macro.py, korea_signal_layer.py, stock_selector.py]
    tdd_coverage: [95%, 85%, 95%]       # synthesize_macro + stock_selector = P1 Critical (95%) — v3.4 H-3: Category A/B 결정론적 분류
    prompt_language: English
    workspace: .claude/agent-workspace/builder-c.yaml
    # v3.2 Q1: synthesize_macro는 p1-critical-builder (Opus) 사용
    # v3.4 H-3: stock_selector도 p1-critical-builder — classify_category() Python 임계값 강제
    # v3.5 CR-5-2: 2개 P1 모듈 각각 전용 workspace (순차 실행 — macro 완료 후 stock)
    agent_for_p1: p1-critical-builder
    p1_workspace:
      synthesize_macro: .claude/agent-workspace/p1-cb-macro.yaml     # synthesize_macro 전용
      stock_selector:   .claude/agent-workspace/p1-cb-stock.yaml      # stock_selector 전용
    p1_sequence: [synthesize_macro, stock_selector]  # Fork C 내 P1 모듈 순차 처리

  - id: builder-d
    fork: D
    modules: [synthesize_stock.py, valuation_comparator.py]
    tdd_coverage: [85%, 85%]            # v3.2 Q3: 표준 85%
    depends_on: [builder-a, builder-b, builder-c]
    prompt_language: English
    workspace: .claude/agent-workspace/builder-d.yaml

  - id: builder-e
    fork: E
    modules: [intelligence_engine.py, report_generator.py, validate_report_quality.py, citation_validator.py]
    tdd_coverage: [90%, 90%, 90%, 90%]  # validate_report_quality + citation_validator = 핵심 파이프라인 (90%) — v3.4 H-4/H-5
    depends_on: [builder-d]
    prompt_language: English
    workspace: .claude/agent-workspace/builder-e.yaml
    # v3.4 H-5: citation_validator.py 신규 — NarrativeOutput 수치 인용 검증 (Python only)

# intelligence_engine.py 특이사항 (P5-A 적용):
#   CATEGORY_A/B_SYSTEM_PROMPT → 영어로 구현
#   내용 요구사항(5개 필수 항목, 금지 항목)은 workflow.md Step 5 기준 100% 보존
#   English prompt → English NarrativeOutput → @translator → Korean report
```

### 4-3. Review SubAgents (2명)

```yaml
review_agents:
  - id: code-reviewer
    type: reviewer
    trigger: 각 builder module 완료 반환 시
    scope: "L2 quality + ADR compliance + sentiment_weight==0.0"
    prompt_language: English
    workspace: .claude/agent-workspace/reviewer.yaml

  - id: fact-checker
    type: fact-checker
    trigger: Step 2, Step 5, Step 11 완료 시
    scope: "FRED series_id + SteepsCategory 6가지(S/T/E/E_env/P/s) + compliance 10 patterns"  # v3.5 IR-13
    prompt_language: English
    workspace: .claude/agent-workspace/fact-checker.yaml
```

### 4-4. Translation SubAgent (1명 — D7 신규)

```yaml
translation_agent:
  - id: translator
    type: translator                     # .claude/agents/translator.md 정의
    model: opus                          # 번역 품질 최대화 (P4)
    trigger: translation_trigger.py Hook (PostToolUse(TaskUpdate) — status=completed 감지)
    prompt_language: English instruction → Korean output
    workspace: .claude/agent-workspace/translator.yaml

    translation_targets:                 # 번역 대상 Step + 파일
      step_2:
        source: output/schema-mapping.md
        target: output/schema-mapping.ko.md
        pacs_log: pacs-logs/step-2-translation-pacs.md

      step_4:
        source: output/completion-definition.md
        target: output/completion-definition.ko.md
        pacs_log: pacs-logs/step-4-translation-pacs.md

      step_5:
        source: output/blueprint.md
        target: output/blueprint.ko.md
        pacs_log: pacs-logs/step-5-translation-pacs.md

      step_11:                           # v3.3 IR-9: template 패턴으로 통일
        source_template: "output/temp/narrative_{date}.json"  # 텍스트 필드만 번역
        source: ""                       # 런타임에 Orchestrator가 채움
        target_template: "output/temp/narrative_{date}.ko.json"
        target: ""
        pacs_log: pacs-logs/step-11-translation-pacs.md

      step_12:                           # 핵심 산출물 — v3.3 IR-9: template 패턴으로 통일
        source_template: "output/reports/weekly-report-{date}.md"
        source: ""                       # 런타임에 Orchestrator가 채움
        target_template: "output/reports/weekly-report-{date}.ko.md"
        target: ""
        pacs_log: pacs-logs/step-12-translation-pacs.md
        telegram_send: true             # 한국어 버전으로 Telegram 발송
        pacs_dimensions: [Ft, Ct, Nt, Fd]  # v3.2 Q6: Fd(Financial Domain accuracy) 추가

      step_15:                           # v3.2 Q5: Watchlist 산출물
        source_template: "output/watchlist-{date}.md"
        source: ""                       # 런타임에 Orchestrator가 채움
        target_template: "output/watchlist-{date}.ko.md"
        target: ""
        pacs_log: pacs-logs/step-15-translation-pacs.md

    not_translated:                      # 번역 제외 목록
      - "*.py"                           # 코드 파일
      - "*.yaml, *.json, *.txt"          # 설정·데이터 파일
      - "state.yaml, phase-*.yaml"       # SOT 파일
      - "agent-workspace/*.yaml"         # workspace 파일
      - "logs/*.log"                     # 로그 파일
      - "tests/"                         # 테스트 파일

    quality_gate:
      pacs_green: 70                     # GREEN 기준 (통과)
      pacs_yellow: 50                    # YELLOW (경고 + 통과)
      pacs_red: 49                       # RED (재번역 필요)
```

---

## 5. Fork 전략

### Fork 유형 1: 데이터 수집 Fork (Stage 1)

```python
# weekly_orchestrator.py — 영어 로그, 영어 결과 키
from concurrent.futures import ProcessPoolExecutor, as_completed

FORK_TIMEOUT = 120

def run_data_collection():
    forks = {
        "fred":    collect_fred_data,     # FRED 10 series_ids
        "envscan": collect_envscan_data,  # database.json + normalizers
        "gnews":   collect_gnews_data,    # signals.parquet (graceful if absent)
        "korea":   collect_korea_data,    # FDR foreign flow + pykrx
    }
    results = {}
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fn): name for name, fn in forks.items()}
        for future in as_completed(futures, timeout=FORK_TIMEOUT * 2):
            name = futures[future]
            try:
                results[name] = future.result(timeout=FORK_TIMEOUT)
            except Exception as e:
                results[name] = None
                write_agent_workspace(f"fork-{name}", {
                    "error": str(e), "status": "failed"  # English values
                })
    return merge_fork_results(results)
```

### Fork 유형 2: 모듈 구현 Fork (Stage 2)

```
독립 실행 (동시 spawn):
  Fork A: config.py → normalizers.py → steeps_classifier.py
          [config·normalizers: module-builder (Sonnet)]
          [steeps_classifier.py: p1-critical-builder (Opus) — P1 Critical, 95% TDD]  # v3.5 IR-11
          [p1 workspace: p1-cb-steeps.yaml — CR-5-2]

  Fork B: signal_bridge.py → dedup.py → compliance_filter.py
          [signal_bridge·dedup: module-builder (Sonnet)]
          [compliance_filter.py: p1-critical-builder (Opus) — P1 Critical, 95% TDD]
          [p1 workspace: p1-cb-compliance.yaml — CR-5-2]

  Fork C: synthesize_macro.py → korea_signal_layer.py → stock_selector.py
          [synthesize_macro.py: p1-critical-builder (Opus) — P1 Critical, 95% TDD]
          [p1 workspace: p1-cb-macro.yaml — CR-5-2]
          [korea_signal_layer: module-builder (Sonnet)]
          [stock_selector.py: p1-critical-builder (Opus) — P1 Critical, 95% TDD]     # v3.5 IR-11
          [p1 workspace: p1-cb-stock.yaml — CR-5-2]
          [Fork C P1 순서: synthesize_macro → stock_selector (순차) — p1-cb-macro 완료 후]

순차 의존:
  Fork D: Fork A,B,C 완료 후 → synthesize_stock.py → valuation_comparator.py
          [agent: module-builder (Sonnet)]

  Fork E: Fork D 완료 후 → intelligence_engine.py → report_generator.py
          → validate_report_quality.py → citation_validator.py                        # v3.5 IR-11
          [intelligence_engine: module-builder (Sonnet), Core Pipeline 90%]
          [report_generator: module-builder (Sonnet), Core Pipeline 90%]
          [validate_report_quality: module-builder (Sonnet), Core Pipeline 90%]       # v3.4 H-4 승격
          [citation_validator: module-builder (Sonnet), Core Pipeline 90%]            # v3.4 H-5 신규

Translation Fork (각 Step 완료 후):
  Step 2  완료 → Translation Task → schema-mapping.ko.md
  Step 4  완료 → Translation Task → completion-definition.ko.md
  Step 5  완료 → Translation Task → blueprint.ko.md
  Step 11 완료 → Translation Task → narrative_{date}.ko.json
  Step 12 완료 → Translation Task → weekly-report-{date}.ko.md (핵심)
  Step 15 완료 → Translation Task → watchlist-{date}.ko.md      (v3.3 IR-7)
```

### Fork 유형 3: TDD Fork (각 모듈 내부)

```
각 builder SubAgent 내부:
  tdd-phase-1: tests/test_{module}.py 작성 (영어) → pytest FAIL (Red)
  tdd-phase-2: {module}.py 구현 (영어) → pytest PASS (Green)
  tdd-phase-3: coverage ≥ 모듈 등급 기준 → TaskUpdate(status=completed, metadata.step=N)
  → tdd_verify.py Hook 자동 실행 → 통과 시 완료 확정
```

### Fork 의존성 동기화 메커니즘 (HR-3 신규)

> **문제**: `depends_on` YAML 선언만으로는 대기 로직 없음. builder-d가 builder-a/b/c 미완 상태에서 시작 가능.
> **해결**: Orchestrator가 Fork 완료를 workspace 파일로 폴링 후 다음 Fork 스폰.

```python
# ── Claude Code Orchestrator 지시 패턴 (Stage 2 — 구현 Phase) ──────────────
# v3.5 IR-14: 이 코드는 weekly_orchestrator.py(Stage 1 Python 스크립트)가 아님.
# 이것은 Claude Code 인터랙티브 세션의 Orchestrator가 SubAgent를 spawn하는 방식의 명세.
# weekly_orchestrator.py는 ProcessPoolExecutor로 데이터 수집(Stage 1)만 담당.
# SubAgent workspace 폴링은 오직 Claude Code Orchestrator 세션에서만 실행됨.
import time, yaml
from pathlib import Path

def wait_for_forks(fork_ids: list[str], timeout: int = 600) -> bool:
    """
    지정 Fork들의 agent-workspace 파일에서 status == "completed" 대기.
    timeout 초 초과 시 False 반환 (Orchestrator가 에러 처리).
    """
    start = time.time()
    while time.time() - start < timeout:
        all_done = True
        for fid in fork_ids:
            ws = Path(f".claude/agent-workspace/{fid}.yaml")
            if not ws.exists():
                all_done = False
                break
            data = yaml.safe_load(ws.read_text()) or {}
            if data.get("status") != "completed":
                all_done = False
                break
        if all_done:
            return True
        time.sleep(30)  # 30초 간격 폴링
    return False

# Orchestrator 실행 순서 (의존성 준수):
# Phase 1: Fork A/B/C 동시 spawn (독립)
result_a = Agent(subagent_type="general-purpose", prompt=builder_a_prompt,
                 run_in_background=True)
result_b = Agent(subagent_type="general-purpose", prompt=builder_b_prompt,
                 run_in_background=True)
result_c = Agent(subagent_type="general-purpose", prompt=builder_c_prompt,
                 run_in_background=True)

# Phase 2: A/B/C 완료 확인 후 Fork D spawn
if not wait_for_forks(["builder-a", "builder-b", "builder-c"]):
    # Fallback: 개별 완료된 것만 확인 후 부분 진행 또는 에스컬레이션
    raise RuntimeError("Fork A/B/C timeout — escalate to user")
result_d = Agent(subagent_type="general-purpose", prompt=builder_d_prompt,
                 run_in_background=True)

# Phase 3: D 완료 확인 후 Fork E spawn
if not wait_for_forks(["builder-d"]):
    raise RuntimeError("Fork D timeout — escalate to user")
result_e = Agent(subagent_type="general-purpose", prompt=builder_e_prompt,
                 run_in_background=True)
```

---

## 6. TDD 통합 — 차등 기준 (D4)

### 6-1. 모듈별 커버리지 기준표

| 등급 | 기준 | 적용 모듈 |
|-----|------|---------|
| **P1 Critical (95%+)** | P1 절대 원칙 직결 + 할루시네이션 최고위험 경로 | `compliance_filter.py`, `synthesize_macro.py`, `steeps_classifier.py` (v3.4 H-2), `stock_selector.py` (v3.4 H-3) |
| **핵심 파이프라인 (90%+)** | 리포트 품질 직결 | `normalizers.py`, `intelligence_engine.py`, `report_generator.py`, `weekly_orchestrator.py`, `validate_report_quality.py` (v3.4 H-4), `citation_validator.py` (v3.4 H-5) |
| **표준 (85%+)** | 일반 처리 모듈 — v3.2 Q3 상향 | 나머지 10개 모듈 (80%는 속도 타협선, 비용 무관 원칙으로 85% 적용) |
| **인프라 (75%+)** | Hook·Skill 스크립트 (로직 단순) | `quality_gate_check.py`, `tdd_verify.py`, `task_schema_check.py`, `sot_write_guard.py`, `translation_trigger.py` |

### 6-2. Done Gate 시스템

**M0.0 Done Gate (DG-00 — v3.6 I-1)**:
```python
DONE_GATE_M00 = [
    ("DG-00", "personalizer.py --hello-test: Telegram '설치 완료' 메시지 수신 확인 (10분 이내)"),
    # DG-00 실패 시: Telegram Bot Token + chat_id 재확인. M0.5 진행 전 반드시 통과.
]
```

**M0.5 Done Gate (DG-01~DG-08)**:
```python
DONE_GATE_M05 = [
    ("DG-01", "config.py: investscan.yaml load + Keychain dynamic load success"),
    ("DG-02", "normalizers.py: database.json → UnifiedSignal (actual field names)"),
    ("DG-03", "synthesize_macro.py: InvestmentMeta + sector directions generated"),
    ("DG-04", "sentinel: assert sentiment_weight == 0.0 passes"),
    ("DG-05", "compliance_filter.py: all 10 prohibition patterns replaced"),
    ("DG-06", "telegram_notifier.py: --dry-run mode works"),
    ("DG-07", "run_m05.py --dry-run: full pipeline completes without error"),
    ("DG-08", "state.yaml: milestones.m05.dg_01_to_08_passed recorded as true"),
]
```

**M1 Done Gate (DG-09~DG-16)**:
```python
DONE_GATE_M1 = [
    ("DG-09", "dedup.py: content-hash dedup + source field in hash"),
    ("DG-10", "steeps_classifier.py: Python keyword lookup table → all 6 STEEPs + lowercase s/uppercase S Python-based distinction (v3.4 H-2)"),
    ("DG-11", "signal_bridge.py: E_env + s routed to correct sectors"),
    ("DG-12", "synthesize_stock.py: DART financials + pykrx + graceful skip"),
    ("DG-13", "intelligence_engine.py: NarrativeOutput >= 1000 bytes (English)"),
    ("DG-14", "validate_report_quality.py: Python regex 8기준 PASS + citation_validator.py: 수치 인용 검증 PASS (v3.4 H-4/H-5)"),
    ("DG-15", "weekly_orchestrator.py --mode full-auto: end-to-end success"),
    ("DG-16", "accuracy_tracker.py: PredictionRecord recorded + state.yaml update"),
    ("DG-17", "portfolio context: state.yaml portfolio.holdings updatable via Telegram reply + report_generator auto-compare output verified"),  # v3.6 I-11
]
```

**Translation Done Gate (TDG-01~TDG-05)**:
```python
DONE_GATE_TRANSLATION = [
    ("TDG-01", "step_2 translation: schema-mapping.ko.md exists, pACS >= 70"),
    ("TDG-02", "step_4 translation: completion-definition.ko.md exists, pACS >= 70"),
    ("TDG-03", "step_5 translation: blueprint.ko.md exists, pACS >= 70"),
    ("TDG-04", "step_11 translation: narrative_{date}.ko.json exists, pACS >= 70"),
    ("TDG-05", "step_12 translation: weekly-report-{date}.ko.md exists, pACS >= 70"),
    ("TDG-06", "step_15 translation: watchlist-{date}.ko.md exists, pACS >= 70"),   # v3.2 Q5
]
```

---

## 7. 계층적 SOT 설계 (D1)

### 7-1. 계층 구조

```
Tier 0: .claude/state.yaml              ← Orchestrator 전용 (최종 권위)
Tier 1: .claude/state/phase-*.yaml     ← 해당 Phase Lead 전용
Tier 2: .claude/agent-workspace/*.yaml  ← 각 SubAgent 자신만 쓰기

원자적 쓰기: state.yaml.tmp → rename → state.yaml (손상 방지)
모든 키·값: 영어 (D7 — 코드/설정은 English-First)
```

### 7-2. state.yaml 전체 스키마 (translations 섹션 포함)

```yaml
# .claude/state.yaml — Global SOT
# Orchestrator + weekly_orchestrator.py 전용 쓰기 | 모든 에이전트 읽기 허용
# ALL KEYS AND VALUES IN ENGLISH (D7 — P5-A)

system:
  installed_at: ""
  version: "1.0.0"

workflow:
  current_step: 0
  current_phase: "research"     # research | planning | implementation | complete
  runtime_mode: ""              # full | envscan_only | independent
  language_policy: "english-first"   # D7 기록
  last_updated: ""

discovered_paths:
  envscan_wf1_output: ""
  gnews_signals: ""
  config_file: ""

discovered_schema:
  envscan_wf1:
    steeps_field: ""
    psst_field: ""
    summary_field: ""
    score_scale: ""             # "0-100" | "0-10" | "0-1"
    preliminary_category_values: []
    schema_decisions_recorded_at: ""
  gnews:
    file_exists: false
    confidence_field: ""

packages:
  m05_ready: false
  fixtures_generated: false
  failed_packages: []

hitl_1:
  completed: false
  telegram_bot_token_registered: false
  telegram_chat_id_registered: false
  dart_api_key_registered: false
  fred_api_key_registered: false
  sectors_confirmed: []
  platform: ""
  custom_watchlist: []
  completed_at: ""

hitl_2:
  completed: false
  choice: ""                    # continue | pause_2weeks
  choice_date: ""
  m1_cost_acknowledged: false

hitl_3:
  completed: false
  report_approved: false
  approved_at: ""

milestones:
  m05:
    dg_01_to_08_passed: false
    installed_at: ""
  m1:
    phase_2_done: false
    phase_3_done: false
    phase_4_done: false
    full_pipeline_ready: false

stock_selection:
  category_a: []
  category_b: []
  selected_at: ""
  manual_override: false

tdd_status:
  compliance_filter: "pending"      # P1 Critical (95%+) — H-1: PROHIBITION_PATTERNS regex
  synthesize_macro: "pending"       # P1 Critical (95%+)
  steeps_classifier: "pending"      # P1 Critical (95%+) — v3.4 H-2: keyword_lookup table
  stock_selector: "pending"         # P1 Critical (95%+) — v3.4 H-3: classify_category() thresholds
  normalizers: "pending"            # Core Pipeline (90%+)
  intelligence_engine: "pending"    # Core Pipeline (90%+)
  report_generator: "pending"       # Core Pipeline (90%+)
  weekly_orchestrator: "pending"    # Core Pipeline (90%+)
  validate_report_quality: "pending" # Core Pipeline (90%+) — v3.4 H-4: Python regex 8기준
  citation_validator: "pending"     # Core Pipeline (90%+) — v3.4 H-5 신규
  config: "pending"                 # Standard (85%+)  # v3.3 MR-1
  schema: "pending"
  dedup: "pending"
  signal_bridge: "pending"
  korea_signal_layer: "pending"
  synthesize_stock: "pending"
  valuation_comparator: "pending"
  watchdog: "pending"
  accuracy_tracker: "pending"

# ── D7 신규: 번역 상태 추적 ──────────────────────────────────────────────────
translations:
  step_2:
    source: "output/schema-mapping.md"
    target: "output/schema-mapping.ko.md"
    status: "pending"           # pending | translating | done | failed
    pacs_score: null
    pacs_grade: null            # GREEN | YELLOW | RED
    translated_at: ""
    glossary_terms_added: 0

  step_4:
    source: "output/completion-definition.md"
    target: "output/completion-definition.ko.md"
    status: "pending"
    pacs_score: null
    pacs_grade: null
    translated_at: ""

  step_5:
    source: "output/blueprint.md"
    target: "output/blueprint.ko.md"
    status: "pending"
    pacs_score: null
    pacs_grade: null
    translated_at: ""

  step_11:
    # v3.1 HR-5: {date} 플레이스홀더 → template/actual 분리
    # source는 weekly_orchestrator.py 실행 시 실제 날짜로 채워짐
    source_template: "output/temp/narrative_{date}.json"
    source: ""                  # 런타임에 weekly_orchestrator가 채움
    target_template: "output/temp/narrative_{date}.ko.json"
    target: ""
    status: "pending"
    pacs_score: null
    pacs_grade: null
    translated_at: ""

  step_12:
    # v3.1 HR-5: {date} 플레이스홀더 → template/actual 분리
    source_template: "output/reports/weekly-report-{date}.md"
    source: ""                  # 런타임에 weekly_orchestrator가 채움
    target_template: "output/reports/weekly-report-{date}.ko.md"
    target: ""
    status: "pending"
    pacs_score: null
    pacs_grade: null
    translated_at: ""
    telegram_sent: false

  step_15:                             # v3.2 Q5 신규: Watchlist 번역
    source_template: "output/watchlist-{date}.md"
    source: ""                         # 런타임에 Orchestrator가 채움
    target_template: "output/watchlist-{date}.ko.md"
    target: ""
    status: "pending"
    pacs_score: null
    pacs_grade: null
    translated_at: ""
# ────────────────────────────────────────────────────────────────────────────

# ── v3.6 I-6: 커뮤니티 라이브러리 가용률 추적 ──────────────────────────────────
library_availability:
  fdr:
    success_count: 0
    total_count: 0
    rolling_4w_rate: null     # 0.0–1.0, null=데이터 없음
    last_checked: ""
  pykrx:
    success_count: 0
    total_count: 0
    rolling_4w_rate: null
    last_checked: ""
  dart_fss:
    success_count: 0
    total_count: 0
    rolling_4w_rate: null
    last_checked: ""
# ────────────────────────────────────────────────────────────────────────────

agent_team_status:
  active: false
  research_swarm: "idle"
  impl_swarm: "idle"
  review_swarm: "idle"
  translation_subagent: "idle"  # D7 신규

# ── v3.6 I-11: Portfolio 컨텍스트 (사용자 보유 비중 — 6분 루틴 지원) ──────────
portfolio:
  # 사용자가 Telegram 답장으로 업데이트. 월 1회 갱신 권장.
  # report_generator.py가 섹터 방향과 자동 대조 → "현재 보유: 3% → 행동: 비중 확대 검토"
  holdings: {}              # {"반도체 ETF": 3, "바이오 ETF": 5} — 비중(%) 단위
  last_updated: ""          # ISO 날짜
  currency: "KRW"
  auto_compare: true        # true: 리포트에서 보유 비중과 자동 대조
# ────────────────────────────────────────────────────────────────────────────

errors: []
```

### 7-3. Translator Workspace 스키마

```yaml
# .claude/agent-workspace/translator.yaml
agent_id: translator
updated_at: ""
current_step: null
translations:
  - step: null
    source: ""
    target: ""
    pacs_score: null
    pacs_grade: ""
    glossary_terms_added: 0
    error: ""
log: []
```

---

## 8. 중앙집중 RLM 통합 (D2·D3)

### v3.1 MR-3: save_context.py 확장 전 호환성 확인 필수

> **주의**: `save_context.py`는 `_context_lib.generate_snapshot_md()`에 의존.
> `snapshot` 딕셔너리에 `agent_workspaces`, `translation_pacs_logs` 키를 추가하면
> `generate_snapshot_md()`가 이 키를 MD 출력에 포함시킬 수 있음.
> **Phase B 구현 시**: `_context_lib.py`의 `generate_snapshot_md()` 함수를
> 먼저 읽어 키 처리 로직을 확인한 후 확장 여부 결정.
> 예상치 못한 키 → MD 섹션 노이즈 발생 가능 → 필요 시 허용 키 목록(allowlist) 추가.

### RLM 체인에 번역 결과 통합

```python
# save_context.py 확장 (최소 수정 — 기존 RLM 로직 유지)

def save_agent_workspace_paths(snapshot: dict) -> dict:
    """
    agent-workspace/ + pacs-logs/ 경로를 스냅샷에 포함.
    세션 복원 시 번역 결과물 위치도 RLM 체인에 포함.
    """
    workspace_dir = Path(".claude/agent-workspace")
    pacs_dir = Path("pacs-logs")
    if workspace_dir.exists():
        snapshot["agent_workspaces"] = [
            str(p) for p in workspace_dir.glob("*.yaml")
        ]
    if pacs_dir.exists():
        snapshot["translation_pacs_logs"] = [
            str(p) for p in pacs_dir.glob("*.md")
        ]
    return snapshot

# restore_context.py 확장 (최소 수정)
def restore_agent_context_hint(snapshot: dict) -> str:
    workspaces = snapshot.get("agent_workspaces", [])
    pacs_logs = snapshot.get("translation_pacs_logs", [])
    hint = ""
    if workspaces:
        hint += "\n[SubAgent Workspace Recovery]\n"
        hint += "\n".join(f"  - {p}" for p in workspaces)
    if pacs_logs:
        hint += "\n[Translation pACS Logs]\n"
        hint += "\n".join(f"  - {p}" for p in pacs_logs)
    return hint + "\n" if hint else ""
```

---

## 9. Hooks 설계

### 9-1. 전체 Hook 목록 — 실제 Claude Code 이벤트 기반

> **v3.1 CR-1 수정**: `TeammateIdle`·`TaskCompleted`·`TaskCreated`는 표준 Claude Code Hook 이벤트가 아님.
> 실험적 Agent Teams 전용 이벤트로 일반 SubAgent 환경에서 발화 보장 없음.
> → **`PostToolUse(TaskUpdate/TaskCreate)`와 `Stop`으로 전면 대체**.

| Hook 이벤트 | 스크립트 | 목적 | 차단 조건 |
|------------|---------|------|---------|
| `Stop` | `quality_gate_check.py` | 응답 종료 전 TDD·번역 RED 검증 | exit 2 |
| `PostToolUse(TaskUpdate)` | `tdd_verify.py` | 완료 Task: TDD·번역 pACS 검증 | exit 2 |
| `PostToolUse(TaskUpdate)` | `translation_trigger.py` | 번역 대상 Step 완료 시 번역 신호 | exit 0 (신호만) |
| `PostToolUse(TaskCreate)` | `task_schema_check.py` | test_spec 없는 구현 Task 차단 | exit 2 |
| `PreToolUse(Edit\|Write)` | `sot_write_guard.py` | SOT 계층 위반 쓰기 차단 (최선 노력) | exit 2 |

**실행 순서 보장** (동일 이벤트 내, MR-1 수정):
- `PostToolUse(TaskUpdate)`: `tdd_verify.py` → `translation_trigger.py` (순서 명시 — tdd_verify exit 2 시 trigger 미실행)
- `PreToolUse(Edit|Write)`: `block_test_file_edit.py` → `predictive_debug_guard.py` → `sot_write_guard.py` (기존 2개 뒤에 추가)

### 9-2. quality_gate_check.py (Stop — v3.1 CR-1·HR-2 수정)

```python
"""
Stop Hook — Claude Code 응답 종료 전 품질 상태 검증.
v3.1 CR-1: TeammateIdle(미존재) → Stop 이벤트로 대체.
v3.1 HR-2: 전체 tests/ 실행 → passing 모듈만 실행 (미구현 모듈 ImportError 방지).
TDD failing 또는 translation RED 상태면 exit 2로 차단.
"""
import json, sys, subprocess, yaml
from pathlib import Path

def load_state() -> dict:
    p = Path(".claude/state.yaml")
    return yaml.safe_load(p.read_text()) if p.exists() else {}

def get_failing_modules(state: dict) -> list:
    return [m for m, s in state.get("tdd_status", {}).items() if s == "failing"]

def get_red_translations(state: dict) -> list:
    return [
        step for step, data in state.get("translations", {}).items()
        if data.get("pacs_grade") == "RED"
    ]

def get_passing_modules(state: dict) -> list:
    """v3.1 HR-2: passing 상태 모듈만 반환 — 미구현 모듈 ImportError 차단."""
    return [m for m, s in state.get("tdd_status", {}).items() if s == "passing"]

def run_quick_tests(passing_modules: list) -> tuple[bool, str]:
    """passing 모듈 테스트 파일만 실행 — Phase C 초기 미구현 모듈 충돌 방지."""
    if not passing_modules:
        return True, "No modules passing yet — skip test run"
    test_files = [
        f"tests/test_{m}.py" for m in passing_modules
        if Path(f"tests/test_{m}.py").exists()
    ]
    if not test_files:
        return True, "No test files found for passing modules"
    r = subprocess.run(
        ["python3", "-m", "pytest"] + test_files + ["-q", "--tb=no", "--no-header"],
        capture_output=True, text=True, timeout=60
    )
    return r.returncode == 0, r.stdout.strip()[-500:]

if __name__ == "__main__":
    # Stop Hook: stdin에 세션 데이터 포함될 수 있음 (무시해도 무방)
    state = load_state()
    failing = get_failing_modules(state)
    red_translations = get_red_translations(state)

    if failing:
        print(f"QUALITY GATE: TDD failing — {failing}", file=sys.stderr)
        sys.exit(2)
    if red_translations:
        print(f"QUALITY GATE: Translation RED (pACS < 50) — {red_translations}\n"
              f"Re-translate before proceeding.", file=sys.stderr)
        sys.exit(2)

    passing = get_passing_modules(state)
    ok, output = run_quick_tests(passing)
    if not ok:
        print(f"QUALITY GATE: Tests failing.\n{output}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)
```

### 9-3. tdd_verify.py (PostToolUse(TaskUpdate) — v3.1 CR-1·CR-2 수정)

```python
"""
PostToolUse(TaskUpdate) Hook — 완료 Task의 TDD·번역 pACS 검증.
v3.1 CR-1: TaskCompleted(미존재) → PostToolUse(TaskUpdate)로 대체.
           status == "completed"인 TaskUpdate만 처리.
v3.1 CR-2: validate_translation.py는 pacs_score 필드 미반환.
           → pacs-logs/step-N-translation-pacs.md 직접 파싱으로 수정.
구현 Task: coverage 기준 미달 시 차단.
번역 Task: pACS RED 시 차단.
"""
import json, sys, subprocess, re, yaml
from pathlib import Path

# D4 차등 커버리지 기준 (v3.5 CR-5-1: steeps/stock/validate/citation 추가)
COVERAGE_TIERS = {
    "p1_critical": {
        # v3.4 H-2/H-3: steeps_classifier·stock_selector 승격 (할루시네이션 최고위험 경로)
        "modules": ["compliance_filter", "synthesize_macro",
                    "steeps_classifier", "stock_selector"],
        "min_coverage": 95,
    },
    "core_pipeline": {
        # v3.4 H-4/H-5: validate_report_quality·citation_validator 승격
        "modules": ["normalizers", "intelligence_engine", "report_generator",
                    "weekly_orchestrator", "validate_report_quality",
                    "citation_validator"],
        "min_coverage": 90,
    },
    "infrastructure": {
        "modules": ["quality_gate_check", "tdd_verify", "task_schema_check",
                    "sot_write_guard", "translation_trigger"],
        "min_coverage": 75,
    },
    "standard": {"modules": [], "min_coverage": 85},  # v3.2 Q3: 80→85 (품질 절대주의)
}

def get_required_coverage(module: str) -> int:
    for tier_name, tier in COVERAGE_TIERS.items():
        if tier_name == "standard":
            continue  # standard is the catch-all, skip in explicit search
        if module in tier["modules"]:
            return tier["min_coverage"]
    # v3.3 CR-4-2: 표준 티어가 catch-all default — return 80이면 Q3(85%) 무력화됨.
    # standard 티어 min_coverage를 정확히 반환해야 모든 미지정 모듈이 85% 기준 적용됨.
    return COVERAGE_TIERS["standard"]["min_coverage"]  # 85 (v3.2 Q3)

def extract_module_name(task_data: dict) -> str | None:
    name = task_data.get("name", "").lower()
    m = re.search(r"implement[:\s]+(\w+)(?:\.py)?", name)
    return m.group(1) if m else None

def run_coverage(module: str) -> tuple[bool, int]:
    r = subprocess.run(
        ["python3", "-m", "pytest", f"tests/test_{module}.py",
         f"--cov={module}", "--cov-report=term-missing", "-q"],
        capture_output=True, text=True, timeout=90
    )
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", r.stdout)
    coverage = int(m.group(1)) if m else 0
    required = get_required_coverage(module)
    return r.returncode == 0 and coverage >= required, coverage

# ── v3.1 CR-2 수정: pacs_score를 pacs-logs 파일에서 직접 파싱 ──────────────
def get_pacs_score_from_log(step: int) -> int | None:
    """
    pacs-logs/step-N-translation-pacs.md에서 pACS 점수 직접 파싱.
    CR-2: validate_translation.py 출력에 pacs_score 필드 없음 → 파일 직접 파싱.
    translator.md §4 형식: "Translation pACS = 85 → GREEN"
    """
    log_path = Path(f"pacs-logs/step-{step}-translation-pacs.md")
    if not log_path.exists():
        return None
    content = log_path.read_text()
    m = re.search(r"Translation\s+pACS\s*=\s*(\d+)", content)
    if m:
        return int(m.group(1))
    m = re.search(r"\bpACS\s*=\s*(\d+)", content)
    return int(m.group(1)) if m else None

def handle_translation_task(task_data: dict) -> tuple[bool, str]:
    """번역 Task pACS 검증 — pacs-logs 직접 파싱 (CR-2 수정)."""
    step = task_data.get("metadata", {}).get("step")
    if step is None:
        return False, "Translation task missing 'step' in metadata"

    pacs = get_pacs_score_from_log(step)

    if pacs is None:
        # pacs-logs 파일 없음 → validate_translation.py T1-T7 검증으로 폴백
        r = subprocess.run(
            ["python3", ".claude/hooks/scripts/validate_translation.py",
             "--step", str(step), "--check-pacs"],
            capture_output=True, text=True, timeout=60
        )
        try:
            data = json.loads(r.stdout)
            if not data.get("pacs_arithmetic_valid", True):
                return False, f"pACS arithmetic invalid at step {step}"
            return True, f"Step {step}: pACS log not found — T1-T7 only"
        except json.JSONDecodeError:
            return False, "validate_translation.py returned invalid JSON"

    grade = "GREEN" if pacs >= 70 else ("YELLOW" if pacs >= 50 else "RED")
    _update_translation_workspace(step, pacs, grade)

    if pacs < 50:
        return False, f"Translation pACS {pacs} = RED. Re-translate step {step}."
    return True, f"Translation pACS {pacs} = {grade}"

def _update_translation_workspace(step: int, pacs: int, grade: str):
    ws = Path(".claude/agent-workspace/translator.yaml")
    if ws.exists():
        data = yaml.safe_load(ws.read_text()) or {}
        for t in data.get("translations", []):
            if t.get("step") == step:
                t.update({"pacs_score": pacs, "pacs_grade": grade})
        ws.write_text(yaml.dump(data))
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())

    # v3.1 CR-1: PostToolUse(TaskUpdate) → status == "completed"만 처리
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskUpdate":
        sys.exit(0)

    tool_result = hook_input.get("tool_result", {})
    result_str = (json.dumps(tool_result)
                  if isinstance(tool_result, dict) else str(tool_result))
    if ('"status": "completed"' not in result_str
            and "status: completed" not in result_str):
        sys.exit(0)

    task_data = hook_input.get("tool_input", {})

    # 번역 Task 분기 (D7)
    if task_data.get("metadata", {}).get("task_type") == "translation":
        passed, msg = handle_translation_task(task_data)
        if not passed:
            print(f"TRANSLATION BLOCKED: {msg}", file=sys.stderr)
            sys.exit(2)
        print(f"TRANSLATION VERIFIED: {msg}")
        sys.exit(0)

    # 구현 Task 분기
    module = extract_module_name(task_data)
    if not module:
        sys.exit(0)

    test_file = Path(f"tests/test_{module}.py")
    if not test_file.exists():
        print(
            f"TDD BLOCKED: tests/test_{module}.py not found. Write tests first.",
            file=sys.stderr
        )
        sys.exit(2)

    passed, coverage = run_coverage(module)
    if not passed:
        required = get_required_coverage(module)
        print(
            f"TDD BLOCKED: {module}.py coverage {coverage}% < required {required}%.",
            file=sys.stderr
        )
        sys.exit(2)
    sys.exit(0)
```

### 9-4. task_schema_check.py (PostToolUse(TaskCreate) — v3.1 CR-1 수정)

```python
"""
PostToolUse(TaskCreate) Hook — 구현 Task에 test_spec 필수.
v3.1 CR-1: TaskCreated(미존재) → PostToolUse(TaskCreate)로 대체.
           hook_input.tool_input에서 task 데이터 추출.
번역 Task (task_type == "translation")는 test_spec 면제.
"""
import json, sys, re

IMPL_KEYWORDS = re.compile(
    r"\b(implement|build|create module|write module|code)\b", re.IGNORECASE
)

if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())

    # v3.1 CR-1: PostToolUse(TaskCreate) → tool_input에서 task 데이터 추출
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskCreate":
        sys.exit(0)

    task = hook_input.get("tool_input", {})
    name = task.get("name", "")
    desc = task.get("description", "")
    metadata = task.get("metadata", {})

    # D7: 번역 Task는 test_spec 면제
    if metadata.get("task_type") == "translation":
        sys.exit(0)

    is_impl = bool(IMPL_KEYWORDS.search(name) or IMPL_KEYWORDS.search(desc))
    has_test_spec = bool(metadata.get("test_spec") or "test_spec" in desc)

    if is_impl and not has_test_spec:
        print(
            f"TDD GATE: Implementation task '{name}' requires 'test_spec'.\n"
            f"Add test_spec to metadata before creating this task.",
            file=sys.stderr
        )
        sys.exit(2)
    sys.exit(0)
```

### 9-5. sot_write_guard.py (PreToolUse(Edit|Write) — v3.1 CR-3 수정)

```python
"""
PreToolUse(Edit|Write) Hook — 계층적 SOT 쓰기 권한 검증 (D1).
v3.1 CR-3:
  (1) env 변수 기반 Agent ID → 신뢰 불가 (CLAUDE_AGENT_ID 미보장).
      1차 방어: Orchestrator 프롬프트가 각 SubAgent에 workspace 쓰기 명시.
      2차 방어: 이 guard (명백한 env 기반 SubAgent 탐지 시 차단).
  (2) 경로 정규화 버그 수정:
      lstrip("./") → .resolve() 절대경로 비교 (경로 우회 차단).

ADR-015: sot_write_guard는 2차 방어선.
  SubAgent env var 미설정 → Orchestrator로 가정하여 허용 (경고 출력).
  1차 방어(프롬프트 지시)가 실질적 SOT 보호 담당.
"""
import json, sys, os
from pathlib import Path

SOT_FILES = [
    ".claude/state.yaml",
    ".claude/state/phase-research.yaml",
    ".claude/state/phase-planning.yaml",
    ".claude/state/phase-impl.yaml",
]

def get_project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

def is_sot_file(file_path: str) -> bool:
    """v3.1 CR-3: Path.resolve() 절대경로 비교 (lstrip 버그 제거)."""
    root = get_project_root()
    try:
        target = Path(file_path).resolve()
    except Exception:
        return False
    return any((root / sot).resolve() == target for sot in SOT_FILES)

def is_agent_workspace_file(file_path: str) -> bool:
    root = get_project_root()
    try:
        target = Path(file_path).resolve()
        workspace = (root / ".claude/agent-workspace").resolve()
        return str(target).startswith(str(workspace) + "/")
    except Exception:
        return False

def get_agent_id() -> str:
    """best-effort 탐지 — 어떤 env 변수도 SubAgent 환경에서 보장 안 됨."""
    for var in ["ANTHROPIC_SUBAGENT_ID", "CLAUDE_AGENT_ID", "AGENT_ID"]:
        val = os.environ.get(var, "")
        if val:
            return val
    return "orchestrator"

if __name__ == "__main__":
    tool_input = json.loads(sys.stdin.read())
    file_path = tool_input.get("file_path", "")
    agent_id = get_agent_id()

    # agent-workspace 파일 → 항상 허용
    if is_agent_workspace_file(file_path):
        sys.exit(0)

    # SOT 파일 접근 감지
    if is_sot_file(file_path):
        is_subagent = any(
            os.environ.get(v, "")
            for v in ["ANTHROPIC_SUBAGENT_ID", "CLAUDE_AGENT_ID"]
        )
        if is_subagent:
            print(
                f"SOT WRITE BLOCKED (SubAgent detected):\n"
                f"  Agent: {agent_id}\n"
                f"  File:  {file_path}\n"
                f"  Fix:   Write to .claude/agent-workspace/{agent_id}.yaml\n"
                f"         Orchestrator merges workspace → SOT.",
                file=sys.stderr
            )
            sys.exit(2)
        else:
            # env var 없음 = Orchestrator로 가정 → 허용 (경고만 출력)
            print(
                f"SOT WRITE (Orchestrator assumed): {file_path}\n"
                f"  SubAgent라면 ANTHROPIC_SUBAGENT_ID 설정 필요.",
                file=sys.stderr
            )
            sys.exit(0)

    sys.exit(0)
```

### 9-6. translation_trigger.py (PostToolUse(TaskUpdate) — v3.1 CR-1·HR-4 수정)

```python
"""
PostToolUse(TaskUpdate) Hook — 번역 대상 Step 완료 시 번역 Task 생성 신호.
v3.1 CR-1: TaskCompleted(미존재) → PostToolUse(TaskUpdate)로 대체.
v3.1 HR-4: state.yaml current_step 읽기 → task metadata.step 직접 사용.
           (타이밍 경쟁 조건 제거: state.yaml 업데이트 전 Hook 발화 문제 해결)
차단 없음 (exit 0). 번역 Task 생성 안내만 출력.
Orchestrator가 pending 파일을 읽어 @translator SubAgent를 spawn.
"""
import json, sys, yaml
from pathlib import Path

# 번역 대상 Step과 소스 파일 매핑
TRANSLATION_TARGETS = {
    2:  "output/schema-mapping.md",
    4:  "output/completion-definition.md",
    5:  "output/blueprint.md",
    11: "output/temp/narrative_{date}.json",
    12: "output/reports/weekly-report-{date}.md",
    15: "output/watchlist-{date}.md",          # v3.2 Q5: Watchlist 최종 산출물
}

def source_file_exists(source: str) -> bool:
    if "{" not in source:
        return Path(source).exists()
    # {date} 포함 경로: 날짜 패턴 매칭으로 존재 확인
    base = source.split("{")[0]
    parent = Path(base).parent
    stem = Path(base).stem
    return parent.exists() and any(
        f.name.startswith(stem) for f in parent.glob("*")
    )

def write_translation_pending(step: int, source: str):
    """Orchestrator에게 번역 Task 생성 신호 전송 (파일 기반)."""
    pending_file = Path(".claude/agent-workspace/translation-pending.yaml")
    data = {"step": step, "source": source, "action": "create_translation_task"}
    pending_file.write_text(yaml.dump(data))

if __name__ == "__main__":
    hook_input = json.loads(sys.stdin.read())

    # v3.1 CR-1: PostToolUse(TaskUpdate) → 완료 상태 확인
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "TaskUpdate":
        sys.exit(0)

    tool_result = hook_input.get("tool_result", {})
    result_str = (json.dumps(tool_result)
                  if isinstance(tool_result, dict) else str(tool_result))
    if ('"status": "completed"' not in result_str
            and "status: completed" not in result_str):
        sys.exit(0)

    task_data = hook_input.get("tool_input", {})

    # 번역 Task 자체 완료 시 트리거 불필요
    if task_data.get("metadata", {}).get("task_type") == "translation":
        sys.exit(0)

    # v3.1 HR-4: state.yaml 읽기 제거 → metadata.step 직접 사용
    # Orchestrator가 TaskUpdate 호출 시 metadata에 step을 명시해야 함
    step = task_data.get("metadata", {}).get("step")
    if step is None or step not in TRANSLATION_TARGETS:
        sys.exit(0)

    source = TRANSLATION_TARGETS[step]
    if not source_file_exists(source):
        sys.exit(0)

    write_translation_pending(step, source)
    print(
        f"TRANSLATION SIGNAL: Step {step} output ready for translation.\n"
        f"Source: {source}\n"
        f"Action: Orchestrator should spawn @translator SubAgent.\n"
        f"Pending: .claude/agent-workspace/translation-pending.yaml"
    )
    sys.exit(0)
```

---

### 9-7. content_gate (weekly_orchestrator.py 내 — v3.2 Q8)

> **Q8 수정**: `@translator`를 spawn하기 전에 영어 NarrativeOutput이 실제로 8기준을 충족하는지 최종 확인하는 게이트. Reflect-Revise 루프(Q2)가 PASS를 리턴했어도, Orchestrator가 번역을 시작하기 전에 한 번 더 검증한다.

#### 9-7-1. NarrativeOutput JSON 스키마 (v3.3 MR-4 신규)

> **MR-4**: `content_gate()`가 사용하는 필드명이 `schema.py`에 정의되어 있지 않으면 `intelligence_engine.py` 구현자가 필드명을 알 수 없어 content_gate는 항상 FAIL. 아래 스키마가 단일 진실 출처(SOT).

```python
# investscan/schema.py — NarrativeOutput 데이터 클래스 (공식 스키마 SOT)
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class NarrativeOutput:
    """
    intelligence_engine.py가 생성하는 영어 원본 JSON 산출물.
    content_gate(), report_generator.py, @translator가 이 필드명을 직접 참조.
    All fields in English (P5-A). sentiment_weight == 0.0 is an absolute sentinel.
    """
    # 공통 필드 (Category A·B 모두 필수)
    category: Literal["A", "B"]
    text: str                          # 완성된 narrative 전문 (UTF-8 ≥1000 bytes)
    sentiment_weight: float = 0.0      # 절대 불변 sentinel — assert == 0.0

    # Category A 전용 (5개 필수)
    yoy_growth: str = ""               # "Revenue +12.3% YoY, Op.Income +8.7% (2025Q3)"
    per_vs_sector: str = ""            # "12.3x, 15.2% discount vs. sector avg 14.5x"
    foreign_flow_direction: str = ""   # "4-week net buy: +$42M (cumulative)"
    downside_risk: str = ""            # "Supply chain disruption → est. -8% revenue"
    direction: Literal[
        "Positive momentum maintained",
        "Neutral — monitor and wait",
        "Risk zone",
        ""
    ] = ""

    # Category B 전용 (6개 필수)
    market_size: str = ""              # "Global AI infra market: $180bn, CAGR 28%"
    stock_positioning: str = ""        # "Tier-1 DRAM supplier for LLM training clusters"
    catalyst: str = ""                 # "Q2 2026 hyperscaler datacenter capex cycle"
    theme_duration: str = ""           # "12-24 week momentum expected"
    dissolution_risk: str = ""         # "Chinese DRAM entry by 2027H1"
    disclaimer: str = ""               # "This analysis is based on future growth..."
```

> **intelligence_engine.py 구현 시**: `NarrativeOutput` 인스턴스를 `from investscan.schema import NarrativeOutput`으로 생성. `pre_translation_gate(dataclasses.asdict(output))`으로 게이트 통과 확인.

#### 9-7-2. content_gate 구현 (v3.2 Q8)

```python
# weekly_orchestrator.py 내 content_gate 함수 (v3.2 Q8)
# NarrativeOutput 필드명은 schema.py §9-7-1 참조
def content_gate(narrative_output: dict) -> tuple[bool, list[str]]:
    """
    Pre-translation gate: verify NarrativeOutput meets all 8 criteria
    before spawning @translator. Called after Reflect-Revise loop PASS.
    Input: dataclasses.asdict(NarrativeOutput) — field names from schema.py
    Returns: (passed: bool, failures: list[str])
    """
    failures = []
    category = narrative_output.get("category", "A")

    if category == "A":
        # Category A: 5 mandatory elements (schema.py field names)
        if not narrative_output.get("yoy_growth"):
            failures.append("A1: Missing YoY revenue + operating income growth")
        if not narrative_output.get("per_vs_sector"):
            failures.append("A2: Missing PER vs sector average")
        if not narrative_output.get("foreign_flow_direction"):
            failures.append("A3: Missing foreign investor 4-week flow direction")
        if not narrative_output.get("downside_risk"):
            failures.append("A4: Missing quantified downside risk")
        if narrative_output.get("direction") not in (
            "Positive momentum maintained",
            "Neutral — monitor and wait",
            "Risk zone",
        ):
            failures.append("A5: Missing/invalid directional opinion")

    elif category == "B":
        # Category B: 6 mandatory elements (schema.py field names)
        if not narrative_output.get("market_size"):
            failures.append("B1: Missing global market size + growth rate")
        if not narrative_output.get("stock_positioning"):
            failures.append("B2: Missing stock positioning within theme")
        if not narrative_output.get("catalyst"):
            failures.append("B3: Missing catalyst event with timeline")
        if not narrative_output.get("theme_duration"):
            failures.append("B4: Missing theme duration estimate")
        if not narrative_output.get("dissolution_risk"):
            failures.append("B5: Missing theme dissolution risk")
        if not narrative_output.get("disclaimer"):
            failures.append("B6: Missing required disclaimer text")

    # Common checks (both categories)
    text = narrative_output.get("text", "")
    if len(text.encode("utf-8")) < 1000:
        failures.append(
            f"C1: NarrativeOutput too short ({len(text.encode())} bytes, min 1000)"
        )
    if narrative_output.get("sentiment_weight", 0.0) != 0.0:
        failures.append("C2: Sentinel violation — sentiment_weight != 0.0")

    return len(failures) == 0, failures


def pre_translation_gate(narrative_output: dict, context_data: dict,
                          retry_count: int) -> None:
    """
    Called inside build_narrative_with_retry() BEFORE spawning @translator.
    v3.5 CR-5-3: Now accepts context_data for citation_validator integration.
    v3.5 CR-5-4: retry_count passed in — raises RetryableError (not generic ValueError).

    Raises:
        RetryableError: if content_gate fails AND retry_count < max_retries
        FinalFailureError: if content_gate fails AND retry_count >= max_retries
    """
    # Step 1: content gate (8 structural criteria)
    passed, failures = content_gate(narrative_output)
    if not passed:
        msg = (f"Content gate FAIL — {len(failures)} criteria unmet:\n"
               + "\n".join(f"  - {f}" for f in failures))
        if retry_count < 3:
            raise RetryableError(msg)
        raise FinalFailureError(msg)

    # Step 2: citation validation (non-blocking — flag only) — v3.5 CR-5-3
    from investscan.citation_validator import validate_citations
    cite_result = validate_citations(narrative_output.get("text", ""), context_data)
    if not cite_result.validated:
        # Log warning but do NOT block translation — semantic check follows by @reviewer
        print(
            f"CITATION WARNING: {len(cite_result.unmatched_numbers)} unmatched numbers "
            f"({cite_result.unmatched_numbers[:5]}). @reviewer will verify semantics.",
            file=sys.stderr
        )

class RetryableError(Exception):
    """Signals build_narrative_with_retry() to retry with failure context."""

class FinalFailureError(Exception):
    """Signals max retries exhausted — trigger HITL escalation."""
```

---

### 9-8. build_narrative_with_retry() — Reflect-Revise 루프 명세 (v3.5 CR-5-4)

> **DG-4 수정**: 기존 Reflect-Revise "최대 3회" 는 카운터·catch·fallback이 없었음.
> 이 함수가 weekly_orchestrator.py 내 Reflect-Revise 루프의 유일한 구현 진실 출처(SOT).

```python
# weekly_orchestrator.py 내 — Reflect-Revise 루프 공식 구현 (v3.5 CR-5-4)
import dataclasses, sys
from investscan.schema import NarrativeOutput
from investscan.validate_report_quality import python_validate_first
from investscan.compliance_filter import filter_report
from investscan.citation_validator import validate_citations

MAX_RETRIES: int = 3  # 품질 절대주의: 3회 시도 후 HITL 에스컬레이션 (무한 루프 방지)

def build_narrative_with_retry(
    context_data: dict,
    intelligence_engine,
    reviewer_agent_fn,
) -> NarrativeOutput:
    """
    Full Reflect-Revise loop with bounded retry counter.

    Sequence per attempt:
      1. intelligence_engine → NarrativeOutput (LLM generation)
      2. python_validate_first(narrative)      ← H-4: Python 1차 구조 검증
      3. filter_report(narrative.text, 0.0)    ← H-1: compliance 10 patterns
      4. reviewer_agent_fn(narrative)          ← @reviewer LLM 2차 (Python PASS 후에만)
      5. pre_translation_gate(narrative, context_data, retry_count)  ← 최종 gate

    Returns:
        NarrativeOutput on success.

    Raises:
        FinalFailureError: after MAX_RETRIES exhausted → caller must HITL escalate.

    P6: Steps 2 and 3 are Python-only. Step 4 (LLM) only runs if Steps 2+3 pass.
    """
    failure_context: list[str] = []   # 이전 실패 기준 누적 (다음 LLM 호출에 첨부)
    best_attempt: NarrativeOutput | None = None

    for retry_count in range(MAX_RETRIES):
        # Step 1: LLM generation (failure_context를 prompt에 첨부)
        narrative: NarrativeOutput = intelligence_engine.generate(
            context_data=context_data,
            failure_context=failure_context,   # 빈 리스트 → 최초 호출
        )
        best_attempt = narrative

        # Step 2: Python 1차 검증 (H-4 — self-evaluation loop 방지)
        py_result = python_validate_first(narrative)
        if not py_result.passed:
            failure_context = [f"Python validation failed: {py_result.details}"]
            continue  # retry — LLM 재호출 (LLM @reviewer 호출 없음 → 토큰 절약)

        # Step 3: compliance_filter (H-1 — Python regex)
        compliant, violations = filter_report(narrative.text, narrative.sentiment_weight)
        if not compliant:
            failure_context = [f"Compliance failed: {[(v[0], v[1]) for v in violations]}"]
            continue

        # Step 4: @reviewer LLM 2차 (논리 일관성·한국 투자자 맥락 — Python 불가 영역)
        review_passed, review_failures = reviewer_agent_fn(narrative)
        if not review_passed:
            failure_context = review_failures
            continue

        # Step 5: citation_validator (H-5 — non-blocking flag)
        cite_result = validate_citations(narrative.text, context_data)
        if not cite_result.validated:
            # citation 불일치는 경고만 — review_failures에 추가하여 다음 LLM에 전달
            failure_context = [
                f"Citation warning (non-blocking): {cite_result.unmatched_numbers[:5]}"
            ]
            # NOTE: continue하지 않음 — citation 불일치는 blocking이 아님 (§19-5 설계 원칙)

        # Step 6: pre_translation_gate
        try:
            pre_translation_gate(
                dataclasses.asdict(narrative), context_data, retry_count
            )
        except RetryableError as e:
            failure_context = [str(e)]
            continue

        return narrative  # ✅ 모든 gate 통과

    # MAX_RETRIES 초과 → best_attempt 저장 + HITL 에스컬레이션
    _save_best_attempt(best_attempt)
    raise FinalFailureError(
        f"Narrative quality gate failed after {MAX_RETRIES} attempts. "
        f"Best attempt saved to output/temp/narrative_failed_[date].json. "
        f"Human review required (/approve-hitl to proceed with best attempt)."
    )

def _save_best_attempt(narrative: NarrativeOutput | None) -> None:
    """3회 실패 시 최선의 결과를 저장 — 사용자가 수동 검토 후 /approve-hitl로 진행 가능."""
    import json, dataclasses
    from pathlib import Path
    from datetime import date
    if narrative is None:
        return
    path = Path(f"output/temp/narrative_failed_{date.today()}.json")
    path.write_text(json.dumps(dataclasses.asdict(narrative), ensure_ascii=False, indent=2))
```

---

## 10. Skills 설계

### 10-1. module-builder Skill

```markdown
# Module Builder Skill
위치: .claude/skills/module-builder/SKILL.md
언어: English-First (P5-A)

Protocol:
1. Load context (English): state.yaml discovered_schema, docs/code-convention.md
2. Write tests/test_{module}.py in English → pytest FAIL (Red)
3. Implement {module}.py in English (code + comments + docstrings)
4. pytest PASS → TaskComplete → tdd_verify.py auto-runs
5. Report to Lead in English: {module, coverage, tests_passed, loc}
```

### 10-2. data-collector Skill

```markdown
# Data Collector Skill
위치: .claude/skills/data-collector/SKILL.md
언어: English-First (P5-A)

Protocol:
1. Keychain check (English commands)
2. Fetch with timeout=30s, retry=3x (English log messages)
3. Normalize to UnifiedSignal (English field names from discovered_schema)
4. Fallback hierarchy: DART → pykrx → FDR → None
5. All results: English keys, English log, English error messages
```

### 10-3. tdd-runner Skill

```markdown
# TDD Runner Skill
위치: .claude/skills/tdd-runner/SKILL.md
언어: English-First (P5-A)

Phase A: Write tests/test_{module}.py in English
  - Happy path, edge cases, sentinel (sentiment_weight==0.0)
  - pytest → FAIL confirmation

Phase B: Validate implementation
  - Run pytest --cov, parse coverage
  - PASS: report to Lead | FAIL: detail to builder

Phase C: Update state
  - tdd_status.{module}: "passing" (via Orchestrator)
```

### 10-4. translator Skill (신규 — D7)

```markdown
# Translator Skill
위치: .claude/skills/translator/SKILL.md
참조: .claude/agents/translator.md (전체 7단계 프로토콜)
모델: opus (번역 품질 최대화)
언어: English instruction → Korean output

## Trigger
- translation_trigger.py가 pending 신호를 발생시킨 경우
- /translate [step|all] 커맨드 수동 호출

## Protocol (translator.md 7단계 준수)
1. Load translations/glossary.yaml (InvestScan 전용 용어 포함)
2. Read English source file completely
3. Translate to Korean (natural, not translationese)
4. Self-Review + pACS scoring
   - Step 2,4,5,11,15: Ft·Ct·Nt (표준 3개 차원)
   - Step 12 전용: Ft·Ct·Nt·Fd — Fd=Financial Domain accuracy  # v3.3 IR-5
5. Update glossary with new InvestScan terms
6. Write [filename].ko.md
7. Write pacs-logs/step-{N}-translation-pacs.md
8. Update .claude/agent-workspace/translator.yaml
9. Return: {pacs_score, pacs_grade, new_terms_added}

## Quality Gates
- GREEN (≥70): 정상 완료 → TaskComplete
- YELLOW (50-69): 경고 + 완료 허용 → 다음 실행 시 개선 목표
- RED (<50): 재번역 필수 → tdd_verify.py가 TaskComplete 차단

## CATEGORY_A/B_SYSTEM_PROMPT 번역 주의
intelligence_engine.py의 영어 프롬프트는 번역 대상이 아님 (코드 파일).
NarrativeOutput JSON의 텍스트 필드만 번역.
```

### 10-5. sot-inspector Skill

```markdown
# SOT Inspector Skill
위치: .claude/skills/sot-inspector/SKILL.md
출력 언어: Korean (사용자 직접 조회 결과)

출력 형식:
InvestScan 상태 — [datetime]
━━━━━━━━━━━━━━━━━━━━━━━━
Phase: [phase] | Step: [N]/15 | Mode: [runtime_mode]
언어 정책: English-First (P5) | HITL: H1=[✓/✗] H2=[✓/✗] H3=[✓/✗]

TDD (P1 Critical 95%+): [✓/✗/○] compliance_filter [✓/✗/○] synthesize_macro
TDD (핵심 90%+):         [✓/✗/○] normalizers [✓/✗/○] intelligence_engine
번역 상태:                                                   # v3.3 IR-6: 전체 Step 표시
  [✓/✗/○] Step 2  (schema-mapping.ko.md)           pACS=[N]
  [✓/✗/○] Step 4  (completion-definition.ko.md)    pACS=[N]
  [✓/✗/○] Step 5  (blueprint.ko.md)                pACS=[N]
  [✓/✗/○] Step 11 (narrative_{date}.ko.json)       pACS=[N]
  [✓/✗/○] Step 12 (weekly-report-{date}.ko.md)     pACS=[N] Fd=[N]
  [✓/✗/○] Step 15 (watchlist-{date}.ko.md)         pACS=[N]
Errors: [count]개
```

---

## 11. Commands 설계

### /run-investscan

```markdown
파일: .claude/commands/run-investscan.md
동작: Research SubAgents 3개 spawn (English prompts) → 결과 수집
      → phase-research.yaml merge → state.yaml 업데이트
Fallback: 타임아웃 5분 → 재spawn → Sequential 모드
```

### /weekly-report

```markdown
파일: .claude/commands/weekly-report.md
동작:
  1. context_[날짜].json 검증 (English fields) + context_data 로드 → dict
  2. intelligence_engine.build_prompt() → English prompt
  3. build_narrative_with_retry(max_retries=3):  ← v3.5 CR-5-4
     3a. LLM → English NarrativeOutput (M0.5)
     3b. validate_report_quality.python_validate_first() → FAIL: retry  ← v3.5 IR-12
     3c. compliance_filter (10 patterns) → FAIL: retry
     3d. @reviewer 8기준 LLM 체크 → FAIL: retry
     3e. 3회 초과 → best_attempt 저장 + HITL 에스컬레이션
  4. citation_validator.validate_citations(narrative.text, context_data)  ← v3.5 CR-5-3
     → False: @reviewer에 flag + log (non-blocking)
  5. content_gate: NarrativeOutput 최종 8기준 확인
  6. report_generator → English weekly-report-[date].md
  7. [P5-B] @translator → weekly-report-[date].ko.md
  8. pACS 검증 (GREEN ≥ 70)
  9. HITL-3: 사용자에게 한국어 번역본 확인
  10. Telegram 발송: 한국어 버전 5줄 요약 (v3.2 Q7)
     Line 1: 📊 [종목명]([종목코드]) — Category [A|B]
     Line 2: 💹 YoY 매출 +X% / 영업이익 +X% (최신 분기)   ← A only
             또는: [테마명] 시장 규모 $Xbn, CAGR X%        ← B only
     Line 3: 🎯 [Positive momentum maintained | Neutral — monitor | Risk zone]
     Line 4: ⚠️ 핵심 리스크: [downside_risk 또는 dissolution_risk 요약 1문장]
     Line 5: 📅 다음 확인: [catalyst 일정 또는 다음 주간 리포트 예정일]
```

### /check-sot

```markdown
파일: .claude/commands/check-sot.md
동작: sot-inspector SubAgent → 계층적 SOT + 번역 상태 리포트 (한국어 출력)
```

### /approve-hitl

```markdown
파일: .claude/commands/approve-hitl.md
/approve-hitl 1 → hitl_1.completed: true → Step 7 시작
/approve-hitl 2 → hitl_2.completed: true → Step 9 시작
/approve-hitl 3 → hitl_3.completed: true → 한국어 리포트 Telegram 발송
```

### /run-tdd

```markdown
파일: .claude/commands/run-tdd.md
/run-tdd [module] → 단일 모듈 TDD 재실행
/run-tdd all      → 전체 모듈 TDD
/run-tdd m05      → DG-01~DG-08
/run-tdd m1       → DG-09~DG-16
/run-tdd translation → TDG-01~TDG-06 번역 Done Gate  # v3.3 IR-1: Step 15 포함
```

### /translate (신규 — D7)

```markdown
파일: .claude/commands/translate.md
목적: 번역 수동 트리거 (자동 트리거 실패 시 또는 재번역 시 사용)

사용법:
  /translate 2    → Step 2 output 번역 (schema-mapping.md)
  /translate 4    → Step 4 output 번역
  /translate 5    → Step 5 output 번역
  /translate 11   → Step 11 output 번역
  /translate 12   → Step 12 output 번역 (최종 리포트)
  /translate 15   → Step 15 output 번역 (watchlist-{date}.md)  # v3.3 IR-4
  /translate all  → 모든 번역 대상 순차 실행 (Step 2,4,5,11,12,15)

동작:
  1. state.yaml translations.step_N.status 확인
  2. source 파일 존재 확인
  3. @translator SubAgent spawn
  4. 번역 완료 → tdd_verify.py (pACS 검증)
  5. state.yaml translations.step_N 업데이트

재번역: /translate 12 (이전 번역 덮어쓰기)
```

---

## 12. Fallback 경로

### Level 1-3: Swarm 장애 (기존 — 변경 없음)

```
L1: Teammate 단일 실패 → 5분 타임아웃 → 재할당
L2: Fork 전체 실패 → Sequential 처리
L3: Swarm 전체 실패 → 단일 에이전트 순차 모드
```

### Level 4: 데이터 API Fallback (v3.6 I-6 확장)

| API | 1차 | 2차 | 최종 |
|----|-----|-----|------|
| FRED | 캐시 7일 | 최소 5개 지표 | independent 모드 |
| DART | pykrx | 수치 없이 방향성만 | `data_freshness_note` |
| pykrx | FDR | sector_avg_per=None | 부분 생성 |
| FDR | pykrx (외국인 수급) | 직전 주 캐시 | 한국 신호 없이 글로벌만 |
| EnvScan | — | — | independent + ⚠️ 경고 |

**커뮤니티 라이브러리 가용률 추적 (v3.6 I-6 신규)**:
```python
# health_dashboard.py 내 — 매 파이프라인 실행 시 자동 기록
# FDR, pykrx, dart-fss: 비공식 KRX 의존 커뮤니티 라이브러리 → 주기적 장애 위험
LIBRARY_AVAILABILITY_TRACKING = {
    "fdr":      {"call": "fdr.DataReader('USD/KRW', start)", "timeout_sec": 10},
    "pykrx":    {"call": "stock.get_market_ohlcv('005930')", "timeout_sec": 10},
    "dart_fss": {"call": "dart.get_corp_code('005930')",    "timeout_sec": 10},
}

def record_library_availability(lib_name: str, success: bool) -> None:
    """
    매 파이프라인 실행 시 각 라이브러리 호출 성공 여부를 기록.
    state.yaml library_availability.<lib>에 4주 이동 평균 가용률 유지.
    """
    ...

# 임계값: 4주 가용률 < 80%이면 Telegram 경고
# "⚠️ {lib_name} 라이브러리가 불안정합니다 (최근 4주 가용률 {rate}%).
#    Claude Code에게 대체 라이브러리 확인을 요청하세요."
LIBRARY_AVAILABILITY_THRESHOLD = 0.80

# state.yaml 확장 — library_availability 섹션 (v3.6)
# library_availability:
#   fdr:      {success_count: 0, total_count: 0, rolling_4w_rate: null}
#   pykrx:    {success_count: 0, total_count: 0, rolling_4w_rate: null}
#   dart_fss: {success_count: 0, total_count: 0, rolling_4w_rate: null}
```

**버전 고정 원칙 (v3.6 I-6)**:
- `requirements.txt`에서 `>=` 대신 `==` 사용: `pykrx==1.0.35`, `dart-fss==0.4.0`
- 업그레이드는 Claude Code와 검토 후 수동 적용 (자동 업그레이드 금지)

### Level 5: TDD Fallback (기존)

```
1회: 자동 수정 | 2회: 상세 분석 | 3회: Orchestrator 에스컬레이션
```

### Level 6: Translation Fallback (신규 — D7)

```
@translator YELLOW (pACS 50-69):
  → 경고 로그 기록 + 번역 완료 허용
  → 다음 /translate 실행 시 개선 목표 명시

@translator RED (pACS < 50):
  → tdd_verify.py가 TaskComplete 차단
  → @translator 재번역 1회 자동 시도
  → 2회 연속 RED → /translate [N] 수동 재번역 요청 + Telegram 알림
  → 재번역 거부 시: YELLOW 기준으로 완료 허용 (품질 경고 포함)

번역 소스 파일 없음:
  → translation_trigger.py: 스킵 (exit 0)
  → state.yaml translations.step_N.status: "skipped"
  → /translate [N] 수동 실행으로 나중에 처리 가능

Orchestrator @translator 연결 실패:
  → state.yaml translations.step_N.status: "failed"
  → quality_gate_check.py는 "failed" 상태를 경고로만 처리 (차단 안 함)
  → 워크플로우 계속 진행 (번역은 blocking이 아닌 enrichment)
```

### Level 7: RLM 복원 Fallback (기존 + 번역 포함)

```
restore_context.py 실패 →
  agent-workspace/*.yaml + pacs-logs/ 읽기로 이전 작업 재구성
  translations 섹션에서 완료된 번역 확인 → 중복 번역 방지
```

---

## 13. 품질 기준 파일

### 13-1. docs/code-convention.md (P5 추가)

```markdown
# InvestScan Code Convention

## P5: English-First 코드 작성 원칙
- 변수명·함수명·클래스명: 영어 (snake_case, PascalCase)
- 주석·docstring: 영어
- 로그 메시지: 영어
- 예외 메시지: 영어
- 설정 파일 키·값: 영어
- 단, 사용자 직접 수신 메시지 (Telegram, HITL 안내): 한국어 허용

## CATEGORY_A/B_SYSTEM_PROMPT 언어 원칙
- intelligence_engine.py에서 영어로 구현 (P5-A)
- 내용 요구사항(5개 필수 항목, 금지 항목): workflow.md Step 5 명세 100% 보존
- 생성되는 NarrativeOutput: 영어
- 최종 한국어 리포트: @translator가 생성

## 기본 규칙 (기존)
- Python 3.11+ | 타입 힌트 필수 | PEP 8 + Black | Line length: 100
- frozen=True + slots=True (공유 dataclass)
- sentiment_weight: 0.0 불변
```

### 13-2. docs/architectural-decision-records.md (ADR-013·014·016 추가)

```markdown
# ADR-013: English-First Execution (P5-A)
Status: Accepted
Context: AI는 영어에서 최고 추론 품질 발휘 → 품질 절대주의(P4)의 직접 구현
Decision: 모든 에이전트 프롬프트·중간 산출물·코드를 영어로 작성
Consequence: CATEGORY_A/B_SYSTEM_PROMPT 영어화 필요 (내용 요구사항 100% 보존)
NOT affected: HITL 안내 메시지, Telegram 알림 (사용자 직접 수신 채널)

# ADR-014: @translator Korean Pair (P5-B)
Status: Accepted
Context: 영어 원본 생성 후 한국어 번역 쌍 제공 → 사용자 경험 완전성
Decision: 6개 Step (2,4,5,11,12,15) 완료 후 @translator SubAgent 자동 spawn  # v3.3 CR-4-4
Mechanism: translation_trigger.py (PostToolUse(TaskUpdate) Hook) → pending signal
           → Orchestrator spawns @translator → tdd_verify.py pACS 검증
Fallback: translation은 blocking이 아닌 enrichment — 실패 시 영어 원본 사용 가능
SOT: state.yaml translations 섹션이 번역 상태 단일 진실 출처

# ADR-015: sot_write_guard 2차 방어선 원칙 (v3.1 CR-3)
Status: Accepted
Context: Claude Code SubAgent 실행 환경에서 CLAUDE_AGENT_ID 등 env 변수 보장 안 됨.
         env 기반 Agent ID 탐지는 신뢰 불가 → SOT 보호를 이것에만 의존 불가.
Decision:
  1차 방어: Orchestrator 프롬프트가 각 SubAgent에 "자신의 workspace만 쓰기" 명시
  2차 방어: sot_write_guard.py — SubAgent env var 탐지 시 차단, 미탐지 시 허용+경고
  경로 비교: Path.resolve() 절대경로 (lstrip 버그 제거)
Consequence: env var 미설정 SubAgent가 SOT를 직접 쓰면 탐지 불가 → 1차 방어 중요.
             프롬프트 지시가 실질적 보호 담당.

# ADR-016: Python-First Decision Architecture (v3.4 P6)
Status: Accepted
Context: LLM은 동일 입력에 대해 다른 분류를 낼 수 있음 (비결정론적).
         steeps_classifier / stock_selector / compliance_filter 등 분류·검증 함수에
         LLM 판단을 허용하면 6단계 할루시네이션 체인이 발생.
Decision:
  - 모든 분류·검증·임계값 판단 = Python 코드 (결정론적)
  - LLM 역할 = NarrativeOutput.text 텍스트 생성만
  - 원칙: "Python이 판사, LLM은 내레이터"
Consequence:
  - steeps_classifier: keyword_lookup 테이블 + Python classify() 함수
  - stock_selector: 수치 임계값 상수 + Python classify_category() 함수
  - compliance_filter: PROHIBITION_PATTERNS regex 상수 배열 + Python scan() 함수
  - validate_report_quality: 8기준 Python regex 1차 검증 후 LLM 평가 호출
  - citation_validator: NarrativeOutput 수치 vs context_data Python 교차검증
NOT affected: NarrativeOutput.text 생성 (여전히 LLM), @translator 번역 (LLM 유지)

# ADR-017: Adversarial Reflection Architecture Decisions (v3.6)
Status: Accepted
Context: 5명 적대적 에이전트(회의론자·통계학자·기술비평가·법률감시자·UX심문관)가
         prd.md를 공격·방어 → 13개 설계 결함·버그·측정 오류 발견.
Decisions:
  I-7: Category B `or 1` 제로가드 → 삼중 안전망(MIN_WEEKS_TRACKED/ABS_COUNT/AVG_COUNT)
  I-3: accuracy_tracker 이중 윈도우 4주(예비) + 8주(최종 KS-1 기준)
  I-4: 판정 임계값 완화 → Bullish +1%, Neutral ±3%
  I-5: KS-1 라벨 "Month 2" → "Month 3 데이터 기반" (측정 지연 반영)
  I-13: Naive Baseline 3가지 (Always-Bullish + Momentum + Random)
  I-11: Portfolio 컨텍스트 state.yaml 섹션 신규
  I-12: Bear Case 섹션 위치 하단 이동 (결정 마비 방지)
  I-9: 법적 비해당 근거 재정렬 (계약 없음 → 보수 없음 → 자기 결정)
  I-1: M0.0 마일스톤 — Day 0 즉시 Telegram Hello
  I-6: FDR/pykrx/dart-fss 가용률 추적 + 버전 고정
Consequence: §20 신규 섹션에 전체 Python 명세 포함. ADR-001~016 모두 유효.

# ADR-001~ADR-012: (기존 — 변경 없음)
```

### 13-3. docs/code-quality-guide.md (@reviewer 체크리스트 업데이트)

```markdown
## @reviewer 체크리스트 (L2) — P5 항목 추가

### P5 English-First 준수
  - [ ] 모든 변수명·함수명·클래스명이 영어
  - [ ] docstring이 영어로 작성됨
  - [ ] 로그·예외 메시지가 영어
  - [ ] CATEGORY_A/B_SYSTEM_PROMPT가 영어로 구현됨
  - [ ] 내용 요구사항 5개 항목이 workflow.md Step 5와 동일 (언어만 영어)

### 번역 관련
  - [ ] intelligence_engine.py: NarrativeOutput JSON 필드명 영어
  - [ ] report_generator.py: 영어 템플릿 사용 (weekly-report.md.j2)
  - [ ] translation 결과(.ko.md)가 영어 원본과 쌍으로 존재 (해당 Step)

### 법적 컴플라이언스 (v3.6 I-9/I-10 신규)
  - [ ] 금지 표현 없음: "매수 추천", "목표가", "확실한 상승", "매도 권고"
  - [ ] 면책 조항 포함 (Section 15.3 문구 그대로)
  - [ ] 가중치 조정 이력에 HITL 필수 여부 명시 (자동 적용 코드 라인 없음)
  - [ ] 리포트를 타인과 공유하는 행위에 대한 법적 경고 문구 없음 (리포트 자체에 포함 불필요)

### Bear Case UX 위치 (v3.6 I-12 신규)
  - [ ] Bear Case 섹션이 리포트 하단(면책 조항 바로 위)에 위치
  - [ ] Bear Case 섹션 제목: "⚠️ 이 방향이 틀릴 수 있는 상황 (참고용)"
  - [ ] onboarding_mode=true 시 Bear Case 앞 설명 문구 포함:
        "이 섹션은 예측이 틀렸을 때의 시나리오입니다. 결정에 반드시 고려할 필요는 없습니다."
  - [ ] Telegram 5줄 요약에는 Bear Case 미포함 (간결성 유지)

### 기존 체크리스트 (변경 없음)
  - [ ] 타입 힌트 모든 함수 | frozen dataclass | sentiment_weight==0.0
  - [ ] API 키 plain text 없음 | ADR-001~016 준수
```

---

## 14. 전체 파일 구조

```
InvestScan/
├── CLAUDE.md
├── docs/
│   ├── code-convention.md              ← [Phase A] P5 항목 포함
│   ├── architectural-decision-records.md ← [Phase A] ADR-001~014, ADR-016 (v3.4), ADR-017 (v3.6)
│   └── code-quality-guide.md           ← [Phase A] P5 체크리스트 포함
│
├── translations/
│   └── glossary.yaml                   ← [Phase B] InvestScan 용어 확장 (+25개)
│
├── pacs-logs/                          ← [Runtime] 번역 pACS 로그
│   ├── step-2-translation-pacs.md
│   ├── step-4-translation-pacs.md
│   ├── step-5-translation-pacs.md
│   ├── step-11-translation-pacs.md
│   ├── step-12-translation-pacs.md    ← Fd 차원 포함
│   └── step-15-translation-pacs.md   ← v3.3 IR-3 신규 (v3.2 Q5)
│
├── .claude/
│   ├── settings.json                   ← [Phase B] 신규 5개 Hook 등록
│   ├── state.yaml                      ← [Phase B] translations 섹션 포함
│   ├── state/
│   │   ├── phase-research.yaml
│   │   ├── phase-planning.yaml
│   │   └── phase-impl.yaml
│   ├── agent-workspace/
│   │   ├── envscan-agent.yaml
│   │   ├── fred-agent.yaml
│   │   ├── gnews-agent.yaml
│   │   ├── builder-a.yaml ~ builder-e.yaml
│   │   ├── reviewer.yaml
│   │   ├── fact-checker.yaml
│   │   ├── translator.yaml             ← [Phase B] 신규
│   │   ├── p1-cb-steeps.yaml          ← [Phase C Runtime] steeps_classifier 전용 — v3.5 CR-5-2
│   │   ├── p1-cb-compliance.yaml      ← [Phase C Runtime] compliance_filter 전용 — v3.5 CR-5-2
│   │   ├── p1-cb-macro.yaml           ← [Phase C Runtime] synthesize_macro 전용 — v3.5 CR-5-2
│   │   ├── p1-cb-stock.yaml           ← [Phase C Runtime] stock_selector 전용 — v3.5 CR-5-2
│   │   └── translation-pending.yaml   ← [Runtime] trigger 신호
│   ├── agents/
│   │   ├── translator.md               ← ✅ 기존 완비 (수정 없음)
│   │   ├── investscan-orchestrator.md  ← [Phase B] §18-1
│   │   ├── data-collector.md           ← [Phase B] §18-2
│   │   ├── module-builder.md           ← [Phase B] §18-3
│   │   ├── tdd-runner.md               ← [Phase B] §18-4
│   │   ├── report-reviewer.md          ← [Phase B] §18-5
│   │   └── p1-critical-builder.md      ← [Phase B] §18-6 v3.3 IR-3 신규 (Opus)
│   ├── commands/
│   │   ├── run-investscan.md
│   │   ├── weekly-report.md            ← [Phase B] @translator 흐름 포함
│   │   ├── check-sot.md
│   │   ├── approve-hitl.md
│   │   ├── run-tdd.md                  ← [Phase B] /run-tdd translation 추가
│   │   └── translate.md                ← [Phase B] 신규
│   ├── hooks/scripts/
│   │   ├── quality_gate_check.py       ← [Phase B] RED translation 체크 추가
│   │   ├── tdd_verify.py               ← [Phase B] 번역 Task 분기 추가
│   │   ├── task_schema_check.py        ← [Phase B] 번역 Task 면제 추가
│   │   ├── sot_write_guard.py          ← [Phase B] 기존 유지
│   │   └── translation_trigger.py      ← [Phase B] 신규
│   └── skills/
│       ├── module-builder/SKILL.md
│       ├── data-collector/SKILL.md
│       ├── tdd-runner/SKILL.md
│       ├── translator/SKILL.md          ← [Phase B] 신규
│       └── sot-inspector/SKILL.md
│
├── investscan/
│   ├── schema.py                       ← NarrativeOutput 데이터 클래스 SOT (§9-7-1)
│   ├── config.py
│   ├── normalizers.py
│   ├── synthesize_macro.py
│   ├── telegram_notifier.py
│   ├── compliance_filter.py
│   ├── dedup.py
│   ├── steeps_classifier.py
│   ├── signal_bridge.py
│   ├── korea_signal_layer.py
│   ├── stock_selector.py
│   ├── synthesize_stock.py
│   ├── valuation_comparator.py
│   ├── intelligence_engine.py          ← CATEGORY_A/B_SYSTEM_PROMPT 영어화
│   ├── report_generator.py
│   ├── validate_report_quality.py
│   ├── citation_validator.py           ← [Phase E] v3.4 H-5 신규 — NarrativeOutput 수치 인용 검증
│   ├── weekly_orchestrator.py
│   ├── accuracy_tracker.py
│   ├── watchdog.py
│   ├── health_dashboard.py
│   └── personalizer.py
│
├── run_m05.py           ← [Phase C] builder-d 담당 — M0.5 통합 테스트 러너 (v3.5 DG-10 명세)
├── make_fixtures.py
├── requirements.txt
│
├── tests/
│   ├── fixtures/envscan_sample.json
│   ├── test_config.py                  ← 영어 테스트 코드
│   ├── test_normalizers.py
│   ├── test_synthesize_macro.py
│   ├── test_compliance_filter.py
│   ├── test_dedup.py
│   ├── test_steeps_classifier.py
│   ├── test_signal_bridge.py
│   ├── test_korea_signal_layer.py
│   ├── test_stock_selector.py
│   ├── test_synthesize_stock.py
│   ├── test_valuation_comparator.py
│   ├── test_intelligence_engine.py
│   ├── test_report_generator.py
│   ├── test_validate_report_quality.py
│   ├── test_citation_validator.py      ← [Phase E] v3.4 H-5 신규 — 90%+ 핵심 파이프라인
│   ├── test_weekly_orchestrator.py
│   ├── test_translation_trigger.py     ← [Phase B] TDD 75%+ (인프라 티어) — v3.3 IR-3
│   ├── test_m05_done_gate.py           ← DG-01~08
│   ├── test_m1_done_gate.py            ← DG-09~16
│   └── test_translation_done_gate.py   ← TDG-01~06 (신규 — v3.3 IR-3)
│
├── config/
│   ├── sector_stock_map.yaml
│   └── few_shot.json
│
├── templates/
│   └── weekly-report.md.j2             ← 영어 템플릿
│
├── output/
│   ├── schema-mapping.md               ← 영어 원본
│   ├── schema-mapping.ko.md            ← 한국어 번역 (@translator)
│   ├── completion-definition.md
│   ├── completion-definition.ko.md
│   ├── blueprint.md
│   ├── blueprint.ko.md
│   ├── context/
│   ├── temp/
│   │   ├── narrative_{date}.json       ← 영어 NarrativeOutput
│   │   └── narrative_{date}.ko.json   ← 한국어 번역
│   ├── watchlist-{date}.md             ← [Step 15] 영어 watchlist 요약 — v3.3 IR-3
│   ├── watchlist-{date}.ko.md         ← [Step 15] 한국어 번역 (@translator)
│   └── reports/
│       ├── weekly-report-{date}.md     ← 영어 원본 리포트
│       └── weekly-report-{date}.ko.md ← 한국어 최종 리포트 (Telegram 발송)
│
├── data/
│   ├── accuracy/
│   ├── journal/
│   └── watchlist_candidates.jsonl
│
├── logs/
│   ├── compliance.log
│   └── telegram_err.log
│
└── ~/.investscan/investscan.yaml
```

---

## 15. 구현 Phase 계획 (B→A→C→D→E)

### Phase B — Infrastructure 구축 (선행 필수 — D6)

```
기존 산출물 + D7 신규 산출물:

기존:
  .claude/settings.json (Hook 등록)
  .claude/state.yaml (초기 구조)
  .claude/state/phase-*.yaml (3개)
  .claude/agent-workspace/ (디렉터리)
  .claude/hooks/scripts/quality_gate_check.py
  .claude/hooks/scripts/tdd_verify.py
  .claude/hooks/scripts/task_schema_check.py
  .claude/hooks/scripts/sot_write_guard.py
  .claude/agents/*.md (5개)
  .claude/commands/*.md (5개)
  .claude/skills/*.md (4개)

D7 신규:
  .claude/hooks/scripts/translation_trigger.py
  .claude/agent-workspace/translator.yaml
  .claude/commands/translate.md
  .claude/skills/translator/SKILL.md
  translations/glossary.yaml (InvestScan 용어 +25개)
  pacs-logs/ (디렉터리 생성)
  .claude/state.yaml translations 섹션 포함

기존 수정 (최소):
  tdd_verify.py → 번역 Task 분기 추가
  task_schema_check.py → 번역 Task 면제 추가
  quality_gate_check.py → RED translation 체크 추가
  .claude/commands/run-tdd.md → translation Done Gate 추가
  .claude/commands/weekly-report.md → @translator 흐름 포함
  save_context.py → pacs-logs/ 경로 추가
  restore_context.py → translation 복원 힌트 추가

D7 신규 + v3.1 HR-1 추가 + v3.3 IR-8 추가:
  .claude/agents/investscan-orchestrator.md  ← 신규 (§18-1 스펙 기반)
  .claude/agents/data-collector.md           ← 신규 (§18-2 스펙 기반)
  .claude/agents/module-builder.md           ← 신규 (§18-3 스펙 기반)
  .claude/agents/tdd-runner.md               ← 신규 (§18-4 스펙 기반)
  .claude/agents/report-reviewer.md          ← 신규 (§18-5 스펙 기반)
  .claude/agents/p1-critical-builder.md      ← v3.3 IR-8 신규 (§18-6 스펙 기반 — Opus)
                                               Phase C에서 Fork B(compliance_filter)·Fork C(synthesize_macro) 빌드 시 사용

v3.1 MR-2 추가:
  make_fixtures.py                           ← TDD 픽스처 생성 스크립트
  tests/fixtures/envscan_sample.json         ← normalizers TDD 필수 픽스처
  tests/fixtures/fred_sample.json            ← synthesize_macro TDD 픽스처
  tests/fixtures/gnews_sample.parquet        ← signal_bridge TDD 픽스처
  (Phase C TDD 시작 전 픽스처 없으면 test_normalizers.py 실행 불가)

완료 기준:
  translation_trigger.py 단위 테스트 통과 (75%+ 기준)
  5개 Agent 정의 파일 생성 완료 (§18 스펙 준수)
  make_fixtures.py 실행 → tests/fixtures/ 3개 파일 생성 확인
  /translate 2 실행 → @translator spawn → .ko.md 생성 확인
```

### Phase A — 품질 기준 파일 (P5 포함)

```
docs/code-convention.md      (P5 English-First 항목 포함)
docs/architectural-decision-records.md  (ADR-013, ADR-014 포함)
docs/code-quality-guide.md   (P5 @reviewer 체크리스트 포함)
```

### Phase C — Stage 1 구현 (Steps 1-7 + HITL-1/2)

```
모든 코드: English-First (P5-A)
번역 트리거: Step 2·4·5 완료 시 @translator 자동 실행
번역 검증: pACS ≥ 70 (GREEN)

Day 0 설치 시작 전 — 인터넷 속도 기반 시간 안내 (v3.6 I-2):
  빠른 인터넷 (100Mbps+): 약 2시간
  보통 인터넷 (50Mbps):   약 3-4시간
  느린 인터넷 (10Mbps-):  5시간 이상 (다음날 분할 설치 권장)
  → Claude Code가 curl 속도 측정 후 현실적 시간 안내 (§20-6 참조)

M0.0 완료 기준 (DG-00 — v3.6 I-1):
  personalizer.py --hello-test 실행 → Telegram 설치 완료 메시지 수신 (10분 이내)
  → 성공 시 Phase C 계속 진행 / 실패 시 Telegram Bot Token 재확인
```

#### run_m05.py 명세 (v3.5 DG-10 — Phase C builder-d 담당)

```python
# run_m05.py — M0.5 통합 테스트 러너
# 담당 builder: builder-d (Fork D) — synthesize_stock.py 완료 후 생성
# TDD: test_m05_done_gate.py → DG-01~DG-08 검증 (Standard 85%+ 기준)
# 목적: M0.5 Done Gate 일괄 실행 — 단위 테스트가 아닌 통합 연기 테스트

"""
Usage:
    python run_m05.py --dry-run     # 실제 API 호출 없이 파이프라인 검증
    python run_m05.py --validate    # DG-01~DG-08 순차 검증 후 결과 출력
"""
import argparse, sys, yaml
from pathlib import Path

# M0.5 Done Gate 항목 (DG-01~08 순서 보장)
M05_GATES = [
    ("DG-01", lambda: _check_config()),           # config.py: yaml + Keychain
    ("DG-02", lambda: _check_normalizers()),      # database.json → UnifiedSignal
    ("DG-03", lambda: _check_synthesize_macro()), # InvestmentMeta + directions
    ("DG-04", lambda: _check_sentinel()),         # sentiment_weight == 0.0
    ("DG-05", lambda: _check_compliance()),       # 10 prohibition patterns
    ("DG-06", lambda: _check_telegram_dry()),     # telegram --dry-run
    ("DG-07", lambda: _check_pipeline_dry()),     # full pipeline dry-run
    ("DG-08", lambda: _check_state_written()),    # state.yaml milestone 기록
]

def run_all_gates(dry_run: bool = True) -> bool:
    """
    DG-01~DG-08 순차 실행. 하나라도 실패 시 중단 후 False 반환.
    --dry-run: 실제 API 호출 없이 mock 데이터로 실행 (기본값).
    Returns True if all gates pass.
    """
    results = {}
    for gate_id, gate_fn in M05_GATES:
        try:
            passed = gate_fn()
            results[gate_id] = "PASS" if passed else "FAIL"
            if not passed:
                print(f"GATE FAILED: {gate_id}", file=sys.stderr)
                return False
        except Exception as e:
            results[gate_id] = f"ERROR: {e}"
            return False

    # DG-08: state.yaml에 milestone 기록
    _write_milestone(results)
    print("M0.5 Done Gates: ALL PASS ✅")
    return True

def _write_milestone(results: dict) -> None:
    """DG-08: state.yaml에 milestones.m05.dg_01_to_08_passed: true 기록 (Orchestrator 위임)."""
    state_path = Path(".claude/state.yaml")
    if state_path.exists():
        state = yaml.safe_load(state_path.read_text()) or {}
        state.setdefault("milestones", {}).setdefault("m05", {})
        state["milestones"]["m05"]["dg_01_to_08_passed"] = all(
            v == "PASS" for v in results.values()
        )
        state["milestones"]["m05"]["gate_results"] = results
        # 원자적 쓰기 (tmp → rename)
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(yaml.dump(state))
        tmp.rename(state_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    success = run_all_gates(dry_run=args.dry_run)
    sys.exit(0 if success else 1)
```

### Phase D — Stage 2 구현 (Steps 9-15)

```
intelligence_engine.py:
  CATEGORY_A_SYSTEM_PROMPT → English (내용 요구사항 100% 보존)
  CATEGORY_B_SYSTEM_PROMPT → English (내용 요구사항 100% 보존)
  NarrativeOutput → English JSON (NarrativeOutput 스키마 §9-7-1 준수)

Step 11 완료: narrative_{date}.ko.json 번역
Step 12 완료: weekly-report-{date}.ko.md 번역 (핵심 산출물, Fd pACS 포함)
Step 15 완료: watchlist-{date}.ko.md 번역 (v3.3 IR-10 — watchlist 생성 후 즉시 번역)
  → weekly_orchestrator.py가 watchlist-{date}.md 생성 후 TaskUpdate(step=15) 호출
  → translation_trigger.py 자동 감지 → @translator spawn
```

### Phase E — Integration + 운영 설정

```
End-to-end 테스트:
  /weekly-report → English report → @translator → .ko.md
  → pACS 검증 → HITL-3 → Telegram 한국어 발송

Translation Done Gate (TDG-01~06) 전체 통과  # v3.3 IR-2: Step 15 포함
```

---

## 16. settings.json 변경 사항

> **v3.1 CR-1 수정**: `TeammateIdle`·`TaskCompleted`·`TaskCreated` 제거.
> → `Stop`·`PostToolUse(TaskUpdate/TaskCreate)`로 대체.
> 기존 설정에 **추가**하는 항목만 표시. 기존 Stop/PostToolUse/PreToolUse 항목은 유지.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/quality_gate_check.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/quality_gate_check.py; fi",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "TaskUpdate",
        "hooks": [
          {
            "type": "command",
            "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/tdd_verify.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/tdd_verify.py; fi",
            "timeout": 120
          },
          {
            "type": "command",
            "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/translation_trigger.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/translation_trigger.py; fi",
            "timeout": 15
          }
        ]
      },
      {
        "matcher": "TaskCreate",
        "hooks": [
          {
            "type": "command",
            "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/task_schema_check.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/task_schema_check.py; fi",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "if test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/sot_write_guard.py; then python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/sot_write_guard.py; fi",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Hook 실행 순서 (MR-1 명시)**:
- `PostToolUse(TaskUpdate)`: `tdd_verify.py` (timeout 120s) → `translation_trigger.py` (timeout 15s) — 순서 보장
  - `tdd_verify.py`가 exit 2 차단 시 `translation_trigger.py` 미실행
- `PreToolUse(Edit|Write)` 전체 순서 (기존 + 신규):
  1. `block_test_file_edit.py` (기존)
  2. `predictive_debug_guard.py` (기존)
  3. `sot_write_guard.py` (신규 — 마지막에 추가)
- `Stop` 기존 Hook (`context_guard.py --mode=stop`) 뒤에 `quality_gate_check.py` 추가

---

## 17. P5 원칙 전문 — English-First + Korean Pair

### P5-A: English-First Execution

```
적용 대상 (항상 영어):
  ✅ 모든 SubAgent 프롬프트
  ✅ 모든 Task 설명 (TaskCreate description, test_spec)
  ✅ 모든 agent-workspace/*.yaml (키·값)
  ✅ 모든 Phase SOT (state/phase-*.yaml)
  ✅ Global SOT state.yaml
  ✅ 코드 파일 (변수명·주석·docstring·에러 메시지)
  ✅ 중간 기술 문서 (schema-mapping.md, blueprint.md 등)
  ✅ NarrativeOutput JSON (영어 원본)
  ✅ 로그 파일 (compliance.log, telegram_err.log)
  ✅ CATEGORY_A/B_SYSTEM_PROMPT (intelligence_engine.py 구현 시)

번역 불필요 (영어 고정):
  ❌ .py 코드 파일
  ❌ .yaml/.json 설정·데이터 파일
  ❌ state.yaml, phase-*.yaml, agent-workspace/*.yaml
  ❌ requirements.txt, 테스트 파일

한국어 허용 (사용자 직접 수신):
  🇰🇷 HITL 안내 메시지 (Step 6, 8)
  🇰🇷 Telegram 알림 메시지
  🇰🇷 최종 주간 리포트 (.ko.md — @translator 생성)
```

### P5-B: Korean Pair

```
번역 대상 Step과 파일:
  Step 2  → output/schema-mapping.ko.md
  Step 4  → output/completion-definition.ko.md
  Step 5  → output/blueprint.ko.md
  Step 11 → output/temp/narrative_{date}.ko.json
  Step 12 → output/reports/weekly-report-{date}.ko.md  ← 핵심 산출물 (Fd pACS 추가)
  Step 15 → output/watchlist-{date}.ko.md              ← v3.2 Q5 신규 (관찰 목록)

번역 품질 기준:
  GREEN (pACS ≥ 70): 정상 완료
  YELLOW (pACS 50-69): 완료 허용 + 경고
  RED (pACS < 50): 재번역 필수

Telegram 발송: 한국어 번역본 기준 (weekly-report-{date}.ko.md)
```

### 전체 번역 흐름

```
Step N 실행 (영어 에이전트 — P5-A)
  │
  ▼
영어 출력물 생성 (schema-mapping.md / blueprint.md / NarrativeOutput 등)
  │
  ▼ Orchestrator: TaskUpdate(status="completed", metadata={step: N}) 호출
  │
  ▼ PostToolUse(TaskUpdate) → tdd_verify.py → 완료 확인 (v3.1 CR-1)
  │
  ▼ PostToolUse(TaskUpdate) → translation_trigger.py → pending 신호 (v3.1 CR-1·HR-4)
  │
  ▼ Orchestrator: @translator SubAgent spawn
  │
  ▼ @translator (translator.md 7단계 프로토콜)
  ├── glossary.yaml 로드 (InvestScan 전용 용어 포함)
  ├── 영어 원본 완독
  ├── 한국어 번역 (자연스러운 한국어, translationese 금지)
  ├── Self-Review + pACS 채점
  │   ├── Ft·Ct·Nt (모든 Step 공통)
  │   └── Fd (Financial Domain accuracy — Step 12 전용, v3.2 Q6)
  │       검증 항목: PER/YoY/CAGR 등 금융 전문 용어 정확성,
  │                 수치·단위 보존 (억→억, % 기호 등), 금감원·DART 표준 표기
  │       Translation pACS (Step 12) = min(Ft, Ct, Nt, Fd)
  ├── pacs-logs/step-N-translation-pacs.md 기록
  ├── glossary.yaml 신규 InvestScan 용어 추가
  └── [filename].ko.md 생성
  │
  ▼ tdd_verify.py: task_type=="translation" → pACS 검증
  ├── RED (<50) → TaskComplete 차단 → 재번역
  ├── YELLOW (50-69) → 완료 + 경고
  └── GREEN (≥70) → 정상 완료
  │
  ▼ state.yaml translations.step_N 업데이트
  │
  ▼ 영어 원본 + 한국어 번역본 쌍 완성
```

### CATEGORY_A/B_SYSTEM_PROMPT 영어화 명세

```python
# intelligence_engine.py 구현 시 사용할 영어 버전
# 내용 요구사항: workflow.md Step 5 한국어 명세와 100% 동일, 언어만 영어

CATEGORY_A_SYSTEM_PROMPT = """
You are an expert quantitative analyst specializing in the Korean stock market.
Generate a professional analyst-grade investment narrative for a stock with
confirmed sector momentum, based on financial performance and valuation data.

MUST INCLUDE (all 5 elements required):
1. YoY revenue and operating income growth for the last 2 quarters (with figures)
   — specify the latest DART-reported quarter (e.g., "As of 2025Q4")
2. Current PER vs. sector average
   — format: "X times, Y% discount/premium vs. sector average"
3. Foreign investor flow direction (4-week cumulative net buy/sell)
4. At least 1 quantified downside risk (describe quantitative impact)
5. Directional opinion — choose exactly one:
   "Positive momentum maintained" | "Neutral — monitor and wait" | "Risk zone"

DATA CITATION RULE (P13 — factual accuracy):
- Cite ONLY actual values from the provided context_data
- Do NOT generate or estimate figures not present in context_data
- If DART quarterly data is unavailable:
  state "Data not collected" or "Pre-quarterly report disclosure"

ABSOLUTE PROHIBITIONS:
buy/sell recommendations, target prices, guaranteed returns
"""

CATEGORY_B_SYSTEM_PROMPT = """
You are an expert analyst specializing in thematic and growth stocks in the
Korean equity market. Generate a growth-oriented investment narrative for
a stock expected to benefit from an emerging global theme.

MUST INCLUDE (all 6 elements required):
1. Global market size and growth rate of the theme (with figures)
2. This stock's positioning within the theme
3. At least 1 key catalyst event (specific timeline or condition)
4. Estimated theme duration (e.g., "12-24 week momentum expected")
5. Theme dissolution risk (competitive entry, policy changes, etc.)
6. Disclaimer: "This analysis is based on future growth potential,
   not current earnings performance"

ABSOLUTE PROHIBITIONS:
buy/sell recommendations, target prices, short-term price predictions
"""
```

### InvestScan 전용 glossary.yaml 확장 (25개 신규 용어)

```yaml
# translations/glossary.yaml 추가 항목 (기존 27개에 추가)

# InvestScan 핵심 개념
"Category A": "Category A"
"Category B": "Category B"
"EnvironmentScan": "EnvironmentScan"
"GlobalNews": "GlobalNews"
"InvestScan": "InvestScan"

# 금융 데이터 소스
"FRED API": "FRED API"
"DART OpenAPI": "DART OpenAPI"
"pykrx": "pykrx"
"FinanceDataReader": "FinanceDataReader"

# 분석 방법론
"STEEPs": "STEEPs"
"pSST score": "pSST 점수"
"UnifiedSignal": "UnifiedSignal"
"InvestmentMeta": "InvestmentMeta"
"NarrativeOutput": "NarrativeOutput"
"sentiment_weight": "sentiment_weight"
"sector confidence": "섹터 신뢰도"

# 리포트 관련
"watchlist": "관찰 목록(watchlist)"
"Bullish": "긍정적(Bullish)"
"Bearish": "부정적(Bearish)"
"Neutral": "중립(Neutral)"
"compliance filter": "컴플라이언스 필터"
"weekly report": "주간 리포트"
"done gate": "완료 게이트"

# 번역 관련 (D7 신규)
"English-First": "English-First"
"Korean Pair": "한국어 쌍"
"Translation pACS": "번역 pACS"
```

---

## 18. Agent 정의 파일 전문 (6개 — v3.1 HR-1 + v3.3 IR-8)

> **HR-1 수정**: Phase B에서 생성할 5개 Agent 정의 파일의 내용 스펙.
> Phase C 실행 전 이 파일들이 존재해야 Orchestrator가 SubAgent를 정확히 spawn 가능.

### 18-1. .claude/agents/investscan-orchestrator.md

```markdown
---
name: investscan-orchestrator
description: InvestScan main orchestrator — coordinates all SubAgents, manages SOT, controls workflow phases
model: opus
tools: Read, Write, Edit, Bash, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet
maxTurns: 50
---

# InvestScan Orchestrator Agent

You are the sole coordinator for InvestScan workflow execution.
You NEVER do implementation work directly — you spawn specialized SubAgents and integrate their results.

## Absolute Rules
1. You are the ONLY agent that writes to .claude/state.yaml (SOT — D1).
2. All SubAgent results must be merged to state.yaml via atomic write (tmp → rename).
3. All reasoning, task descriptions, and intermediate outputs in English (P5-A).
4. On session start: read state.yaml → resume from current_step/current_phase.
5. Before spawning any SubAgent, call wait_for_forks() for dependent Forks (§5).

## SOT Write Protocol (Mandatory Atomic Pattern)
```python
import yaml, pathlib, tempfile, os
def atomic_sot_write(data: dict, target: str = ".claude/state.yaml"):
    p = pathlib.Path(target)
    with tempfile.NamedTemporaryFile("w", dir=p.parent,
                                     suffix=".tmp", delete=False) as f:
        yaml.dump(data, f, allow_unicode=True)
        tmp = pathlib.Path(f.name)
    tmp.rename(p)
```

## Translation Trigger Protocol
After each Step N completion that has task metadata.step set:
1. Call TaskUpdate with status="completed", metadata={"step": N, "task_type": "implementation"}
2. Check .claude/agent-workspace/translation-pending.yaml
3. If pending.step == N and N in [2,4,5,11,12]: spawn @translator SubAgent

## HITL Gate Protocol
- HITL-1 (Step 6): Send Korean Telegram message → wait for /approve-hitl 1
- HITL-2 (Step 8): Send Korean Telegram message → wait for /approve-hitl 2
- HITL-3 (Step 12): Present Korean .ko.md → wait for /approve-hitl 3
```

### 18-2. .claude/agents/data-collector.md

```markdown
---
name: data-collector
description: InvestScan data collection SubAgent — FRED API, EnvironmentScan, GlobalNews, Korea market data
model: sonnet
tools: Read, Write, Bash
maxTurns: 20
---

# Data Collector SubAgent

Collect data from assigned source. Write ALL results to .claude/agent-workspace/[assigned-id].yaml ONLY.
Do NOT write to state.yaml or any phase-*.yaml (D1 — SOT protection).

## English-First (P5-A)
All workspace file keys, values, and log messages must be in English.

## Protocol
1. Read .claude/agent-workspace/[id].yaml — check if already completed (resume guard)
2. Collect data with timeout=30s, retry=3x
3. Validate data completeness (minimum required fields)
4. Write result: {"status": "completed", "data": {...}, "error": null, "collected_at": "ISO8601"}
5. Return summary JSON to Orchestrator

## Fallback Hierarchy
- FRED: cache (7 days) → minimum 5 series → runtime_mode = "independent"
- DART: pykrx → FDR → None (with data_freshness_note in result)
- EnvScan: not found → {"found": false, "path": null} → Orchestrator sets runtime_mode
- GlobalNews: not found → {"found": false} → graceful skip (not blocking)
```

### 18-3. .claude/agents/module-builder.md

```markdown
---
name: module-builder
description: InvestScan TDD-first module builder SubAgent
model: sonnet
tools: Read, Write, Edit, Bash
maxTurns: 30
---

# Module Builder SubAgent

Build assigned modules using strict TDD (Red → Green cycle).
Write all progress to .claude/agent-workspace/[fork-id].yaml ONLY.

## English-First (P5-A — Mandatory)
- Variable names, function names, class names: English snake_case / PascalCase
- All comments and docstrings: English
- Log messages and error messages: English
- Test descriptions (pytest): English

## TDD Protocol (mandatory order)
Phase 1 (Red):
  - Write tests/test_{module}.py first
  - Run: pytest tests/test_{module}.py → MUST see FAILED output
  - If no failures: tests are trivial → strengthen test cases

Phase 2 (Green):
  - Implement {module}.py
  - Run: pytest tests/test_{module}.py → MUST see PASSED output

Phase 3 (Verify Coverage):
  - Run: pytest tests/test_{module}.py --cov={module} --cov-report=term-missing
  - Coverage must meet tier requirement (P1 Critical: 95%, Core: 90%, Standard: 85%, Infra: 75%)

Phase 4 (Report):
  - Write to workspace: {"status": "completed", "module": str, "coverage": float, "tests_passed": bool}
  - Call TaskUpdate: status="completed", metadata={"step": N, "module": module}

## Dependency Check (before starting)
Read .claude/agent-workspace/[dependency-id].yaml for each depends_on id.
Only start if all dependencies have status == "completed".
```

### 18-4. .claude/agents/tdd-runner.md

```markdown
---
name: tdd-runner
description: InvestScan TDD verification SubAgent — runs tests and reports coverage only
model: sonnet
tools: Read, Write, Bash
maxTurns: 15
---

# TDD Runner SubAgent

Validate test coverage for assigned module. TESTING ONLY — do NOT modify production code.

## Protocol
1. Run: pytest tests/test_{module}.py --cov={module} --cov-report=term-missing -v
2. Parse coverage % from "TOTAL" line
3. Compare against tier requirement
4. Write to .claude/agent-workspace/tdd-runner.yaml:
   {"module": str, "coverage": float, "passed": bool, "required": int, "failures": list}
5. Return summary to Orchestrator

## Coverage Tier Reference
- P1 Critical (95%+): compliance_filter, synthesize_macro
- Core Pipeline (90%+): normalizers, intelligence_engine, report_generator, weekly_orchestrator
- Infrastructure (75%+): Hook scripts
- Standard (80%+): all others

## On Failure
Report exact failing test names and uncovered lines to Orchestrator.
Do NOT auto-fix implementation — builder SubAgent is responsible for fixes.
```

### 18-5. .claude/agents/report-reviewer.md

```markdown
---
name: report-reviewer
description: InvestScan adversarial report reviewer — validates against 8 quality criteria
model: opus
tools: Read, Write, Bash
maxTurns: 20
---

# Report Reviewer SubAgent (Adversarial — L2)

Review InvestScan report outputs. Your role is adversarial — look for failures, not confirmations.
Apply validate_report_quality.py criteria systematically.

## 8-Criteria Review Checklist
1. Category A: All 5 elements present
   - [ ] YoY revenue + operating income growth (last 2 quarters, with figures)
   - [ ] PER vs sector average (format: "X times, Y% discount/premium")
   - [ ] Foreign investor 4-week cumulative flow direction
   - [ ] At least 1 quantified downside risk
   - [ ] Directional opinion (exactly one: Positive/Neutral/Risk zone)
2. Category B: All 6 elements present
   - [ ] Global market size + growth rate (with figures)
   - [ ] Stock's positioning in the theme
   - [ ] At least 1 catalyst event (specific timeline/condition)
   - [ ] Theme duration estimate
   - [ ] Theme dissolution risk
   - [ ] Required disclaimer text
3. [ ] No prohibited content (buy/sell recommendations, target prices, guaranteed returns)
4. [ ] All figures traceable to context_data (no hallucinated numbers)
5. [ ] NarrativeOutput >= 1000 bytes
6. [ ] sentiment_weight == 0.0 (check config.py sentinel)
7. [ ] compliance_filter: all 10 prohibition patterns replaced
8. [ ] Step 12: weekly-report.ko.md exists + pACS grade not RED
9. Bear Case UX compliance (v3.6 I-12):
   - [ ] Bear Case section positioned AFTER watchlist, BEFORE disclaimer (bottom of report)
   - [ ] Bear Case title is "⚠️ 이 방향이 틀릴 수 있는 상황 (참고용)"
   - [ ] Bear Case NOT included in Telegram 5-line summary
   - [ ] onboarding_mode=true: pre-text before Bear Case exists
10. Disclaimer (legal — v3.6 I-9):
   - [ ] Full disclaimer text present (Section 15.3 exact wording)
   - [ ] Telegram summary includes short disclaimer variant

## Output Format
Write verdict to review-logs/step-{N}-review.md:
VERDICT: PASS | FAIL
FAILING_CRITERIA: [list of failed items with evidence]
EVIDENCE: [specific text quotes from report showing issues]

Return: {"verdict": "PASS"|"FAIL", "failing_criteria": list, "step": int}
```

### 18-6. .claude/agents/p1-critical-builder.md (v3.2 Q1 신규)

```markdown
---
name: p1-critical-builder
description: InvestScan P1 Critical module builder — Opus-class quality for compliance_filter, synthesize_macro, steeps_classifier, stock_selector
model: opus
tools: Read, Write, Edit, Bash
maxTurns: 40
---

# P1 Critical Builder SubAgent

You build P1 Critical modules for InvestScan.
P1 Critical = compliance_filter.py + synthesize_macro.py + steeps_classifier.py + stock_selector.py (v3.5 DG-9)

You are invoked with a SINGLE module assignment per invocation. Check your assignment:
- Assigned module: [set by Orchestrator in prompt]
- Workspace file: [set by Orchestrator — p1-cb-{module-short}.yaml]

These modules are the core safety net of InvestScan. Failure here means:
- compliance_filter: regulatory violations published to users
- synthesize_macro: corrupted macro scores → wrong Category A/B signals
- steeps_classifier: hallucination 6-chain start (wrong STEEPs routing)
- stock_selector: wrong Category A/B → wrong intelligence_engine prompt → wrong narrative

## Why Opus (v3.2 Q1 + v3.5 DG-9)

Quality absolutism (P4) prohibits using speed as a criterion. These modules require:
- compliance_filter.py: 10 prohibition patterns must catch 100% of violations — no false negatives
- synthesize_macro.py: macro synthesis drives all Category A/B decisions — logical flaws = wrong investment signals
- steeps_classifier.py: Python keyword lookup correctness — lowercase 's' vs uppercase 'T' routing
- stock_selector.py: deterministic A/B threshold enforcement — classify_category() must never invoke LLM

Sonnet is insufficient for formal verification of sentinel conditions. Opus is mandatory.

## P1 Critical Protocol

### Phase 1: Specification Analysis (MANDATORY before writing any code)
1. Read workflow.md §Step 12 and §Step 5 (Category A/B logic) completely
2. Read prd.md for compliance requirements
3. Read docs/code-convention.md for coding standards
4. Read workflow-coding.md §19 (Python-First spec for your assigned module)
5. Identify ALL sentinel conditions for your assigned module:
   - sentiment_weight == 0.0 (absolute — all modules)
   - compliance_filter: PROHIBITION_PATTERNS[0..9] regex list (§19-1)
   - synthesize_macro: macro_score bounds [0.0, 1.0] (§19-2 연관)
   - steeps_classifier: KEYWORD_LOOKUP dict + SteepsCategory["S","T","E","E_env","P","s"] (§19-2)
   - stock_selector: CATEGORY_A_THRESHOLDS dict + classify_category() no-LLM invariant (§19-3)

### Phase 2: Adversarial Test-First (95% coverage required)
Write tests BEFORE implementation. Use the test guidance for your assigned module:

**compliance_filter.py tests (tests/test_compliance_filter.py)**:
```python
# Required test classes:
# TestProhibitionPatterns: all 10 patterns individually (양성/음성 쌍)
# TestEdgeCases: substring match, case sensitivity, Unicode variants
# TestNoFalseNegatives: real-world violation examples from analyst reports
# TestSentinelPreservation: sentiment_weight == 0.0 after filter
# TestScanReturnFormat: (idx, name, match) 튜플 구조 검증
# TestPerformance: 1000 reports processed in < 5s
```

**synthesize_macro.py tests (tests/test_synthesize_macro.py)**:
```python
# Required test classes:
# TestNormalization: output bounds [0.0, 1.0] for all inputs
# TestCategoryClassification: A/B boundary conditions
# TestMissingData: graceful handling of None/empty FRED/EnvScan fields
# TestSentinelIntegrity: sentiment_weight never modified
# TestDeterminism: same inputs always produce same output
```

**steeps_classifier.py tests (tests/test_steeps_classifier.py)** — v3.5 DG-9 신규:
```python
# Required test classes:
# TestAllSixCategories: S/T/E/E_env/P/s 각각 최소 3개 키워드 매칭 테스트
# TestLowercaseS: "tech sector", "업황" → 's' (소문자) NOT 'T'
# TestUppercaseT: "semiconductor", "반도체" → 'T' (대문자) NOT 's'
# TestCompoundKeyword: "반도체 업황" → 's' (더 구체적인 복합 키워드 우선)
# TestUnknownCategory: 매칭 없는 텍스트 → None 반환
# TestConfidenceRange: confidence ∈ [0.0, 1.0]
# TestDeterminism: 동일 입력 100회 → 동일 결과 (Python lookup 결정론성)
# TestCaseNormalization: 대소문자 혼합 입력 → 동일 결과
# TestEEnvCategory: "climate change", "탄소중립" → 'E_env' NOT 'E'
```

**stock_selector.py tests (tests/test_stock_selector.py)** — v3.5 DG-9 신규:
```python
# Required test classes:
# TestCategoryAAllPass: 3개 임계값 모두 충족 → "A"
# TestCategoryAPartialFail: sector_confidence만 미달 → "B"
# TestCategoryAMacroFail: macro_score만 미달 → "B"
# TestCategoryAFinancialFail: financial_completeness만 미달 → "B"
# TestCategoryBAll: 3개 모두 미달 → "B"
# TestBoundaryExact: threshold 정확값 입력 → "A" (≥ 조건)
# TestBoundaryJustBelow: threshold - 0.001 입력 → "B"
# TestReasonString: reason 문자열에 실제 입력값 포함 확인
# TestDeterminism: 동일 입력 100회 → 동일 결과
# TestFrozenInput: ClassificationInput 수정 시 FrozenInstanceError
# TestNoLLMCall: classify_category() 내부에 LLM 호출 없음 확인 (mock 없이 실행)
```

pytest must report FAIL before proceeding to implementation.

### Phase 3: Implementation with Formal Verification
For each sentinel condition, write an assertion that fires at runtime:
```python
# compliance_filter.py
assert sentiment_weight == 0.0, "Sentinel violation: sentiment_weight modified by compliance_filter"

# synthesize_macro.py
assert 0.0 <= macro_score <= 1.0, f"Normalization violation: macro_score={macro_score}"
```

### Phase 4: Adversarial Self-Review (pre-commit)
Before writing to workspace, conduct adversarial review:
1. "What input could bypass prohibition pattern #N?" (check all 10) — compliance_filter only
2. "What edge case could push macro_score outside [0,1]?" — synthesize_macro only
3. "What keyword could be misrouted between uppercase T and lowercase s?" — steeps_classifier only (v3.4 H-2)
4. "What boundary input could flip Category A to B or vice versa?" — stock_selector only (v3.4 H-3)
5. "What None/empty value could cause a silent wrong result?" — all modules
6. Fix all identified vulnerabilities.

### Phase 5: Coverage Verification
Run: pytest tests/test_{module}.py --cov={module} --cov-report=term-missing -v
Requirement: 95% line coverage minimum. If < 95%, add missing test cases and re-run.

### Phase 6: Report to Orchestrator
Write to the module-specific workspace file (v3.5 CR-5-2 — NO shared file):
```
compliance_filter → .claude/agent-workspace/p1-cb-compliance.yaml
synthesize_macro  → .claude/agent-workspace/p1-cb-macro.yaml
steeps_classifier → .claude/agent-workspace/p1-cb-steeps.yaml
stock_selector    → .claude/agent-workspace/p1-cb-stock.yaml
```

Schema (모든 파일 공통):
```yaml
module: str   # e.g. "compliance_filter"
status: "completed" | "failed"
coverage: float
tests_total: int
tests_passed: int
sentinel_assertions: int  # count of runtime assertion guards added
adversarial_review_issues_found: int
adversarial_review_issues_fixed: int
p1_passed: bool  # coverage >= 95% AND all sentinels present
# 모듈별 추가 필드:
keyword_lookup_entries: int | null  # steeps_classifier: KEYWORD_LOOKUP 항목 수
category_thresholds_verified: bool | null  # stock_selector: A/B 임계값 상수 검증
```

> **v3.5 CR-5-2**: 과거 단일 `p1-critical-builder.yaml`을 4개로 분리.
> Fork A·B·C가 동시 실행될 때 각 p1-critical-builder 인스턴스가 서로 다른 파일에 쓰므로
> P2 SOT 쓰기 충돌이 원천 차단됨.

## English-First (P5-A)
All code, comments, docstrings, test names, error messages: English only.
Write NO Korean in any file you produce.
```

---

## 19. 할루시네이션 원천봉쇄 — Python-First 결정론 명세

> **P6 원칙 구현**: "Python이 판사, LLM은 내레이터" — 모든 분류·검증·임계값 판단은 Python 코드가 담당한다. LLM은 오직 NarrativeOutput.text 텍스트 생성만 수행한다.
>
> **§19 구성**: H-1(compliance_filter) → H-2(steeps_classifier) → H-3(stock_selector) → H-4(validate_report_quality) → H-5(citation_validator)

---

### 19-1. H-1 — compliance_filter.py: 10개 금지 패턴 Python regex 상수

> **문제**: compliance_filter.py 명세에 "10개 금지 패턴"이 선언되어 있으나 구체적 패턴이 미정의 → 구현자가 패턴을 스스로 추론 or LLM에게 위임 → 할루시네이션 누출.
>
> **해결**: 10개 패턴을 Python regex 상수 배열로 명세에 고정. 이 상수가 SOT.

```python
# investscan/compliance_filter.py — PROHIBITION_PATTERNS (SOT)
# P6: LLM이 패턴을 생성하거나 수정해서는 안 됨. 이 배열이 유일한 진실 출처.
import re
from dataclasses import dataclass
from typing import Final

# 10개 금지 패턴 — 각 패턴은 독립적으로 적용 (OR 조건)
PROHIBITION_PATTERNS: Final[list[re.Pattern]] = [
    # P-01: 확정적 미래 수익/가격 예측 (법적 금지 사항)
    re.compile(
        r"(반드시|certainly|guaranteed?|definitely)\s+(오를|상승할|gain|rise|reach)\b",
        re.IGNORECASE
    ),
    # P-02: 매수/매도 직접 권유
    re.compile(
        r"\b(지금\s*바로\s*매수|buy\s*now|지금\s*팔아라|sell\s*immediately)\b",
        re.IGNORECASE
    ),
    # P-03: 원금 보장 표현
    re.compile(
        r"(원금\s*보장|원금이\s*보전|principal\s*guarantee[d]?|no[\s-]risk\s*investment)",
        re.IGNORECASE
    ),
    # P-04: 특정 수익률 확정 표현 (예: "연 20% 보장")
    re.compile(
        r"(연\s*\d+\s*%\s*(수익|보장|확정)|annual\s*(return|yield)\s*of\s*\d+\s*%\s*(guaranteed|certain))",
        re.IGNORECASE
    ),
    # P-05: sentiment_weight 비제로 표현 (감성 점수 조작 감지)
    re.compile(
        r"sentiment_weight\s*[=:]\s*(?!0\.0\b)[\d]",
        re.IGNORECASE
    ),
    # P-06: 내부 정보 암시
    re.compile(
        r"(내부\s*정보|insider\s*(information|tip)|비공개\s*정보|non[\s-]public\s*information)",
        re.IGNORECASE
    ),
    # P-07: 과거 수익률을 미래 보장으로 표현
    re.compile(
        r"(과거\s*수익률이?\s*(보장|확정|반복)|past\s*(performance|returns?)\s*(guarantee[sd]?|ensure[sd]?|repeat[s]?))",
        re.IGNORECASE
    ),
    # P-08: 투자 자문 자격 없는 개인화 추천
    re.compile(
        r"(당신에게\s*추천|귀하에게\s*추천|I\s*recommend\s+you\s+buy|personally\s+recommend\s+purchasing)",
        re.IGNORECASE
    ),
    # P-09: 손실 가능성 완전 부인
    re.compile(
        r"(손실이?\s*(없습니다|불가|발생하지\s*않[습])|no\s*(risk|loss|downside)\s*(of|to)\s*(losing|investment))",
        re.IGNORECASE
    ),
    # P-10: 특정 목표 주가 단정 (애널리스트 공식 발표 제외)
    re.compile(
        r"(목표주가\s*는?\s*반드시|target\s*price\s*(will\s*be|is\s*definitely|guaranteed\s*to\s*reach))",
        re.IGNORECASE
    ),
]

def scan_for_violations(text: str) -> list[tuple[int, str, re.Match]]:
    """
    Apply all 10 prohibition patterns and return list of violations.

    Returns:
        list of (pattern_idx, pattern_name, match_object) — empty if compliant.

    P6: This function is Python-only. Never invoke LLM for compliance judgment.
    """
    PATTERN_NAMES = [
        "P-01:확정적수익예측", "P-02:매수매도직접권유", "P-03:원금보장",
        "P-04:수익률확정", "P-05:sentiment_weight비제로", "P-06:내부정보암시",
        "P-07:과거수익률미래보장", "P-08:개인화추천", "P-09:손실가능성부인",
        "P-10:목표주가단정",
    ]
    violations = []
    for idx, pattern in enumerate(PROHIBITION_PATTERNS):
        match = pattern.search(text)
        if match:
            violations.append((idx + 1, PATTERN_NAMES[idx], match))
    return violations

def filter_report(narrative_text: str, sentiment_weight: float) -> tuple[bool, list]:
    """
    Gate function: checks compliance then verifies sentinel.

    Returns:
        (is_compliant: bool, violations: list[tuple])

    sentinel_weight must always be 0.0 — verified here as final guard.
    """
    assert sentiment_weight == 0.0, (
        f"Sentinel violation: sentiment_weight={sentiment_weight} (must be 0.0)"
    )
    violations = scan_for_violations(narrative_text)
    return len(violations) == 0, violations
```

**TDD 요구사항 (95% — P1 Critical)**:
```python
# tests/test_compliance_filter.py
# TestProhibitionPatterns: 10개 패턴 각각 독립 테스트 (양성/음성 쌍)
# TestEdgeCases: 유니코드 변형, 공백 변형, 대소문자
# TestNoFalseNegatives: 실제 애널리스트 리포트 위반 예시
# TestSentinelPreservation: assert sentiment_weight == 0.0 검증
# TestScanReturnFormat: (idx, name, match) 튜플 구조 검증
# TestPerformance: 1000개 리포트 < 5s
```

---

### 19-2. H-2 — steeps_classifier.py: STEEPs 키워드 룩업 테이블

> **문제**: LLM이 "Technology sector 뉴스"를 STEEPs 대문자 'T'(Technological)로 분류할 때 vs 소문자 't'(tech sector)로 처리할 때가 혼재 → signal_bridge 라우팅 오류 → 할루시네이션 6단계 체인.
>
> **해결**: 키워드 룩업 테이블을 Python 상수로 정의. `classify()` 함수가 테이블 조회만 수행.

```python
# investscan/steeps_classifier.py — KEYWORD_LOOKUP (SOT)
# P6: classify() 함수는 Python dict 조회만 수행. LLM 분류 금지.
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Final, Literal

# STEEPs 범주 정의
# 대문자 = 거시 카테고리 (macro signal → InvestmentMeta)
# 소문자 s = 섹터별 신호 (sector signal → SectorSignal)
SteepsCategory = Literal["S", "T", "E", "E_env", "P", "s"]
# S     = Social (사회/인구 변화 — 대문자)
# T     = Technological (기술 혁신/AI/반도체 — 대문자)
# E     = Economic (경제/금리/환율 — 대문자)
# E_env = Environmental (환경/기후 — 대문자) — 'E' 충돌 방지 (v3.5 IR-13: E2→E_env 통일)
# P     = Political (정치/규제 — 대문자)
# s     = sector-specific (섹터별 업황 — 소문자, signal_bridge 별도 라우팅)

# 키워드 룩업 테이블 — 각 키워드는 소문자로 정규화 후 비교
KEYWORD_LOOKUP: Final[dict[str, SteepsCategory]] = {
    # ── Social (S) ──────────────────────────────────────────────────────────
    "aging population": "S", "고령화": "S", "저출산": "S", "인구감소": "S",
    "demographic": "S", "인구구조": "S", "출생률": "S", "노동인구": "S",
    "workforce aging": "S", "pension reform": "S", "연금개혁": "S",
    # ── Technological (T) ────────────────────────────────────────────────────
    "artificial intelligence": "T", "ai regulation": "T", "반도체": "T",
    "semiconductor": "T", "chip": "T", "hbm": "T", "llm": "T",
    "quantum computing": "T", "양자컴퓨팅": "T", "robotics": "T",
    "autonomous": "T", "자율주행": "T", "5g": "T", "6g": "T",
    # ── Economic (E) ─────────────────────────────────────────────────────────
    "federal reserve": "E", "기준금리": "E", "interest rate": "E",
    "환율": "E", "exchange rate": "E", "gdp": "E", "inflation": "E",
    "인플레이션": "E", "cpi": "E", "ppi": "E", "경기침체": "E",
    "recession": "E", "무역수지": "E", "trade balance": "E",
    "경상수지": "E", "current account": "E",
    # ── Environmental (E_env) — v3.5 IR-13: E2→E_env 통일 ──────────────────
    "climate change": "E_env", "탄소중립": "E_env", "carbon neutral": "E_env",
    "esg": "E_env", "renewable energy": "E_env", "재생에너지": "E_env",
    "carbon tax": "E_env", "탄소세": "E_env", "green deal": "E_env",
    # ── Political (P) ────────────────────────────────────────────────────────
    "regulation": "P", "규제": "P", "tariff": "P", "관세": "P",
    "geopolitical": "P", "지정학": "P", "sanctions": "P", "제재": "P",
    "trade war": "P", "무역전쟁": "P", "election": "P", "선거": "P",
    # ── sector-specific (s — 소문자) ─────────────────────────────────────────
    "sector rotation": "s", "업황": "s", "섹터": "s",
    "healthcare sector": "s", "tech sector": "s", "energy sector": "s",
    "financial sector": "s", "consumer sector": "s", "industrial sector": "s",
    "반도체 업황": "s", "배터리 업황": "s", "조선 업황": "s",
    "바이오 업황": "s", "게임 업황": "s",
}

# 키워드 우선순위 정렬 (길이 내림차순 — 더 구체적인 키워드가 먼저 매칭)
_SORTED_KEYWORDS: Final[list[tuple[str, SteepsCategory]]] = sorted(
    KEYWORD_LOOKUP.items(), key=lambda x: len(x[0]), reverse=True
)

def classify(text: str) -> SteepsCategory | None:
    """
    Classify news text into STEEPs category using keyword lookup only.

    Returns:
        SteepsCategory if matched, None if no keyword matched.

    P6: Pure Python lookup — NO LLM involvement.
    Lowercase 's' = sector-specific → routed to SectorSignal by signal_bridge.
    Uppercase letters = macro signal → routed to InvestmentMeta.
    """
    normalized = text.lower()
    for keyword, category in _SORTED_KEYWORDS:
        if keyword in normalized:
            return category
    return None

def classify_with_confidence(text: str) -> tuple[SteepsCategory | None, float]:
    """
    Returns (category, confidence).
    Confidence = number of matching keywords / total keywords (capped at 1.0).
    Used by signal_bridge for routing weight.
    """
    normalized = text.lower()
    matches = [(kw, cat) for kw, cat in _SORTED_KEYWORDS if kw in normalized]
    if not matches:
        return None, 0.0
    # Use first (longest/most specific) match as primary category
    primary_category = matches[0][1]
    confidence = min(len(matches) / 3.0, 1.0)  # 3+ matches = 100% confidence
    return primary_category, round(confidence, 3)
```

**TDD 요구사항 (95% — P1 Critical)**:
```python
# tests/test_steeps_classifier.py
# TestAllSixCategories: S/T/E/E_env/P/s 각각 최소 3개 키워드 매칭 테스트
# TestLowercaseS: "tech sector", "업황" → 's' (소문자), NOT 'T'
# TestUppercaseT: "semiconductor", "반도체" → 'T' (대문자), NOT 's'
# TestLongestMatch: "반도체 업황" → 's' 아닌 'T'? → 우선순위 규칙 명확화
# TestUnknownCategory: 매칭 없는 텍스트 → None 반환
# TestConfidenceRange: confidence ∈ [0.0, 1.0]
# TestDeterminism: 동일 입력 100회 → 동일 결과
# TestCaseNormalization: 대소문자 혼합 입력 → 동일 결과
```

> **구현 주의**: `"반도체 업황"` 키워드는 `"반도체"`(T)와 `"업황"`(s) 두 키워드를 포함.
> 길이 우선순위에 의해 `"반도체 업황"` → `'s'`로 분류 (섹터별 업황 신호).
> `"반도체"` 단독 → `'T'` (거시 기술 신호). 이 구분이 signal_bridge 라우팅의 핵심.

---

### 19-3. H-3 — stock_selector.py: Category A/B 결정론적 임계값

> **문제**: stock_selector.py에서 Category A/B 분류를 LLM 판단에 의존하면 동일 종목이 매주 다른 카테고리로 분류될 수 있음 → intelligence_engine이 다른 프롬프트 사용 → 리포트 구조 불일치.
>
> **해결**: 수치 임계값 상수를 Python으로 정의. `classify_category()` 함수가 임계값 비교만 수행.

```python
# investscan/stock_selector.py — Category A/B 결정론적 분류 (SOT)
# P6: classify_category()는 수치 비교만 수행. LLM 판단 절대 금지.
from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Literal

CategoryLabel = Literal["A", "B"]

# ── Category 분류 임계값 상수 ─────────────────────────────────────────────────
# Category A: 개별 종목 펀더멘털 분석 (재무 + 밸류에이션 기반)
CATEGORY_A_THRESHOLDS: Final[dict[str, float]] = {
    "sector_confidence_min": 0.65,   # steeps_classifier sector 확신도 (s 카테고리)
    "macro_score_min": 0.60,         # synthesize_macro macro_score 최솟값
    "financial_data_completeness": 0.70,  # DART 재무 데이터 완전성 (0~1)
}

# Category B: 테마/섹터 거시 분석 (InvestmentMeta 기반)
CATEGORY_B_THRESHOLDS: Final[dict[str, float]] = {
    "theme_strength_min": 0.70,      # 테마 신호 강도 (InvestmentMeta.theme_score)
    "macro_score_max": 0.59,         # macro_score가 낮을 때 B 선호 (A 조건 미충족)
    "steeps_macro_count_min": 2,     # 거시 STEEPs 신호 수 (S/T/E/E2/P) 최소값
}

@dataclass(frozen=True)
class ClassificationInput:
    """Input bundle for classify_category() — all fields required."""
    sector_confidence: float      # from steeps_classifier.classify_with_confidence()
    macro_score: float            # from synthesize_macro.compute_macro_score()
    financial_data_completeness: float  # from normalizers.compute_completeness()
    theme_strength: float         # from synthesize_macro.compute_theme_strength()
    steeps_macro_count: int       # count of macro STEEPs signals (S/T/E/E2/P)

def classify_category(inp: ClassificationInput) -> tuple[CategoryLabel, str]:
    """
    Deterministic Category A/B classification using threshold constants only.

    Decision logic (Python only — NO LLM):
    - Category A if ALL conditions met:
        1. sector_confidence >= CATEGORY_A_THRESHOLDS["sector_confidence_min"]
        2. macro_score >= CATEGORY_A_THRESHOLDS["macro_score_min"]
        3. financial_data_completeness >= CATEGORY_A_THRESHOLDS["financial_data_completeness"]
    - Category B otherwise (including partial A condition failures)

    Returns:
        (CategoryLabel, reason_string) — reason explains which threshold triggered.

    P6: Never call LLM inside this function. Thresholds are SOT constants.
    """
    a_conditions = {
        "sector_confidence": inp.sector_confidence >= CATEGORY_A_THRESHOLDS["sector_confidence_min"],
        "macro_score": inp.macro_score >= CATEGORY_A_THRESHOLDS["macro_score_min"],
        "financial_completeness": inp.financial_data_completeness >= CATEGORY_A_THRESHOLDS["financial_data_completeness"],
    }

    if all(a_conditions.values()):
        reason = (
            f"A: sector_conf={inp.sector_confidence:.2f}≥{CATEGORY_A_THRESHOLDS['sector_confidence_min']}, "
            f"macro={inp.macro_score:.2f}≥{CATEGORY_A_THRESHOLDS['macro_score_min']}, "
            f"fin_completeness={inp.financial_data_completeness:.2f}≥{CATEGORY_A_THRESHOLDS['financial_data_completeness']}"
        )
        return "A", reason

    failed = [k for k, v in a_conditions.items() if not v]
    reason = (
        f"B: A conditions failed={failed}, "
        f"theme_strength={inp.theme_strength:.2f}, "
        f"steeps_macro_count={inp.steeps_macro_count}"
    )
    return "B", reason
```

**TDD 요구사항 (95% — P1 Critical)**:
```python
# tests/test_stock_selector.py
# TestCategoryAAllPass: 3개 임계값 모두 충족 → "A"
# TestCategoryAPartialFail: sector_confidence만 미달 → "B"
# TestCategoryAMacroFail: macro_score만 미달 → "B"
# TestCategoryAFinancialFail: financial_completeness만 미달 → "B"
# TestCategoryBAll: 3개 모두 미달 → "B"
# TestBoundaryExact: threshold 정확값 입력 → A (≥ 조건 확인)
# TestBoundaryJustBelow: threshold - 0.001 → B
# TestReasonString: reason 문자열에 실제 값 포함 확인
# TestDeterminism: 동일 입력 100회 → 동일 결과
# TestFrozenInput: ClassificationInput 수정 시 FrozenInstanceError
```

---

### 19-4. H-4 — validate_report_quality.py: Python regex 8기준 1차 검증

> **문제**: validate_report_quality.py가 LLM에게 "8기준을 평가하라"고 위임하면 자기평가 루프(self-evaluation loop) 발생 — LLM이 자신이 생성한 텍스트를 자신이 평가 → 할루시네이션 인식 불가.
>
> **해결**: 객관적으로 Python regex로 검증 가능한 기준은 Python이 1차 검증. LLM은 Python이 통과시킨 텍스트만 2차 평가.

```python
# investscan/validate_report_quality.py — Python 1차 검증 (SOT)
# P6: python_validate_first() 함수는 LLM 호출 없음. 8기준 중 Python 검증 가능 항목만.
import re
from dataclasses import dataclass
from typing import Final

# ── 8기준 Python 검증 가능 항목 ───────────────────────────────────────────────
# 기준 1: UTF-8 바이트 길이 ≥ 1000
# 기준 2: Category A → direction 필드 3개 값 중 하나 포함
# 기준 3: Category B → disclaimer 필드 비어 있지 않음
# 기준 4: sentiment_weight == 0.0 (sentinel)
# 기준 5: 금지 패턴 없음 (compliance_filter 결과 재확인)
# 기준 6: Category A → yoy_growth, per_vs_sector, foreign_flow_direction, downside_risk 비어 있지 않음
# 기준 7: Category B → market_size, stock_positioning, catalyst, theme_duration, dissolution_risk 비어 있지 않음
# 기준 8: ★ LLM 평가 항목 — 논리적 일관성, 한국 투자자 맥락 적합성 (Python 불가 → LLM 2차)

DIRECTION_VALID_VALUES: Final[set[str]] = {
    "Positive momentum maintained",
    "Neutral — monitor and wait",
    "Risk zone",
}

CATEGORY_A_REQUIRED_FIELDS: Final[list[str]] = [
    "yoy_growth", "per_vs_sector", "foreign_flow_direction", "downside_risk", "direction"
]
CATEGORY_B_REQUIRED_FIELDS: Final[list[str]] = [
    "market_size", "stock_positioning", "catalyst", "theme_duration",
    "dissolution_risk", "disclaimer"
]

@dataclass
class ValidationResult:
    passed: bool
    failed_criteria: list[str]   # criteria IDs that failed
    details: dict[str, str]      # criterion_id → detail message

def python_validate_first(narrative: "NarrativeOutput") -> ValidationResult:
    """
    Python-only validation of criteria 1-7.
    Criteria 8 (logical consistency) is delegated to LLM reviewer.

    P6: This function must NOT call LLM. It validates structure and sentinel only.
    Returns ValidationResult — proceed to LLM review only if passed=True.
    """
    from investscan.compliance_filter import scan_for_violations

    failed: list[str] = []
    details: dict[str, str] = {}

    # 기준 1: UTF-8 길이
    byte_len = len(narrative.text.encode("utf-8"))
    if byte_len < 1000:
        failed.append("C1")
        details["C1"] = f"text={byte_len} bytes < 1000"

    # 기준 2: direction 유효값 (Category A only)
    if narrative.category == "A":
        if narrative.direction not in DIRECTION_VALID_VALUES:
            failed.append("C2")
            details["C2"] = f"direction='{narrative.direction}' not in valid set"

    # 기준 3: disclaimer 비어 있지 않음 (Category B only)
    if narrative.category == "B":
        if not narrative.disclaimer.strip():
            failed.append("C3")
            details["C3"] = "disclaimer is empty for Category B"

    # 기준 4: sentinel
    if narrative.sentiment_weight != 0.0:
        failed.append("C4")
        details["C4"] = f"sentiment_weight={narrative.sentiment_weight} (must be 0.0)"

    # 기준 5: compliance re-check
    violations = scan_for_violations(narrative.text)
    if violations:
        failed.append("C5")
        details["C5"] = f"compliance violations={[(v[0], v[1]) for v in violations]}"

    # 기준 6: Category A 필수 필드
    if narrative.category == "A":
        missing = [f for f in CATEGORY_A_REQUIRED_FIELDS if not getattr(narrative, f, "").strip()]
        if missing:
            failed.append("C6")
            details["C6"] = f"missing fields={missing}"

    # 기준 7: Category B 필수 필드
    if narrative.category == "B":
        missing = [f for f in CATEGORY_B_REQUIRED_FIELDS if not getattr(narrative, f, "").strip()]
        if missing:
            failed.append("C7")
            details["C7"] = f"missing fields={missing}"

    return ValidationResult(
        passed=len(failed) == 0,
        failed_criteria=failed,
        details=details,
    )
```

**TDD 요구사항 (90% — 핵심 파이프라인)**:
```python
# tests/test_validate_report_quality.py
# TestC1ByteLength: 999 bytes → FAIL C1, 1000 bytes → PASS
# TestC2DirectionValid: 3개 유효값 → PASS; 임의 문자열 → FAIL C2
# TestC2CategoryBSkip: Category B는 direction 체크 건너뜀
# TestC3DisclaimerEmpty: Category B, disclaimer="" → FAIL C3
# TestC4SentinelViolation: sentiment_weight=0.1 → FAIL C4
# TestC5ComplianceViolation: P-01 패턴 포함 텍스트 → FAIL C5
# TestC6CategoryAMissingFields: yoy_growth="" → FAIL C6
# TestC7CategoryBMissingFields: market_size="" → FAIL C7
# TestAllPassCategoryA: 모든 기준 충족 → passed=True, failed_criteria=[]
# TestAllPassCategoryB: 모든 기준 충족 → passed=True
# TestMultipleFailures: C1+C4 동시 실패 → failed_criteria=['C1','C4']
```

---

### 19-5. H-5 — citation_validator.py: NarrativeOutput 수치 인용 검증 (신규 모듈)

> **문제**: intelligence_engine이 생성한 NarrativeOutput.text에 "YoY +23.5%" 같은 구체적 수치가 포함될 때, 이 수치가 context_data(실제 FRED/DART 데이터)에 실제로 존재하는지 검증하지 않음 → 할루시네이션 수치 리포트 발송 위험.
>
> **해결**: citation_validator.py가 NarrativeOutput의 모든 수치를 추출하여 context_data와 Python으로 교차검증.

```python
# investscan/citation_validator.py — 수치 인용 교차검증 (신규 v3.4 H-5)
# P6: 모든 수치 추출·비교는 Python regex/수치 연산. LLM 판단 없음.
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Final

# 수치 추출 패턴 — NarrativeOutput.text에서 % 및 절대값 추출
NUMERIC_PATTERN: Final[re.Pattern] = re.compile(
    r"([+-]?\d+\.?\d*)\s*(%|억|조|billion|million|bn|mn|배|x)"
    r"|"
    r"([+-]?\d+\.?\d+)"  # 소수점 포함 수치 (정수 제외 — 노이즈 방지)
)

# 허용 오차 — 반올림 차이 허용 (예: 23.5% vs 23.47%)
TOLERANCE_PERCENT: Final[float] = 0.5   # ±0.5% 포인트
TOLERANCE_ABSOLUTE: Final[float] = 0.05  # ±5% 상대 오차

@dataclass
class CitationResult:
    validated: bool
    unmatched_numbers: list[str]    # context_data에서 찾지 못한 수치
    matched_numbers: list[str]      # 검증된 수치
    warning_count: int              # matched but near boundary

def extract_numbers_from_text(text: str) -> list[str]:
    """Extract all numeric references from NarrativeOutput text."""
    return [m.group(0).strip() for m in NUMERIC_PATTERN.finditer(text)]

def flatten_context_values(context_data: dict) -> list[float]:
    """
    Recursively extract all float/int values from context_data dict.
    Used as the pool of "known numbers" to validate citations against.
    """
    values = []
    def _recurse(obj):
        if isinstance(obj, (int, float)):
            values.append(float(obj))
        elif isinstance(obj, dict):
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
    _recurse(context_data)
    return values

def _parse_numeric_value(raw: str) -> float | None:
    """Parse raw string like '+23.5%' → 23.5, '1.2조' → 1.2, etc."""
    cleaned = re.sub(r"[+억조billion|million|bn|mn|배|x%\s]", "", raw, flags=re.IGNORECASE)
    try:
        return float(cleaned)
    except ValueError:
        return None

def validate_citations(
    narrative_text: str,
    context_data: dict,
) -> CitationResult:
    """
    Cross-validate all numbers in narrative_text against context_data values.

    Algorithm (Python-only — NO LLM):
    1. Extract all numeric references from narrative_text
    2. Flatten context_data to pool of known float values
    3. For each extracted number, check if ≥1 context value matches within tolerance
    4. Return CitationResult with matched/unmatched split

    P6: This function is deterministic Python. Never invoke LLM for number validation.

    Note: citation_validator validates *existence* not *semantics*.
          Semantic accuracy (correct metric name) is validated by @reviewer (L2).
    """
    context_pool = flatten_context_values(context_data)
    raw_numbers = extract_numbers_from_text(narrative_text)

    matched: list[str] = []
    unmatched: list[str] = []
    warnings = 0

    for raw in raw_numbers:
        num = _parse_numeric_value(raw)
        if num is None:
            unmatched.append(raw)
            continue

        found = False
        for ctx_val in context_pool:
            # Tolerance check: within TOLERANCE_PERCENT of the value
            if abs(ctx_val - num) <= TOLERANCE_PERCENT:
                found = True
                break
            # Relative tolerance for larger numbers
            if ctx_val != 0 and abs((ctx_val - num) / ctx_val) <= TOLERANCE_ABSOLUTE:
                found = True
                warnings += 1
                break

        if found:
            matched.append(raw)
        else:
            unmatched.append(raw)

    # Gate: if > 30% of numbers are unmatched → validation fails
    total = len(raw_numbers)
    if total == 0:
        return CitationResult(validated=True, unmatched_numbers=[], matched_numbers=[], warning_count=0)

    unmatched_ratio = len(unmatched) / total
    validated = unmatched_ratio <= 0.30  # ≤30% unmatched is acceptable

    return CitationResult(
        validated=validated,
        unmatched_numbers=unmatched,
        matched_numbers=matched,
        warning_count=warnings,
    )
```

**TDD 요구사항 (90% — 핵심 파이프라인)**:
```python
# tests/test_citation_validator.py
# TestExtractNumbers: "+23.5%", "1.2조", "3.5x" → 올바른 추출
# TestFlattenContext: 중첩 dict → flat float list
# TestParseNumeric: "+23.5%" → 23.5, "1.2" → 1.2, "abc" → None
# TestExactMatch: narrative "23.5%" + context {revenue_yoy: 23.5} → matched
# TestToleranceMatch: narrative "23.5%" + context {yoy: 23.4} → matched (within 0.5)
# TestUnmatchedNumber: narrative "99.9%" + context has no near value → unmatched
# TestValidatedTrue: unmatched_ratio <= 30% → validated=True
# TestValidatedFalse: >30% unmatched → validated=False
# TestEmptyText: no numbers in text → validated=True (nothing to validate)
# TestEmptyContext: numbers in text but empty context → all unmatched → likely False
# TestDeterminism: 동일 입력 → 동일 결과 항상
```

**context_data 출처 명세 (v3.5 DG-11)**:
```python
# context_data는 context_[날짜].json을 로드한 Python dict — weekly_orchestrator.py에서 관리
# 로드 시점: build_narrative_with_retry() 호출 직전 (§9-8 참조)
# 구조: {"fred": {...}, "envscan": {...}, "gnews": {...}, "korea": {...}}
#       normalizers.py → UnifiedSignal 변환 후 context_[날짜].json에 저장된 실제 데이터
# citation_validator는 이 dict을 flatten해 수치 pool을 구성 (§19-5 flatten_context_values)
import json
from pathlib import Path
from datetime import date

def load_context_data() -> dict:
    """
    Load context_[date].json → dict for citation_validator and intelligence_engine.
    Called ONCE in weekly_orchestrator.py before build_narrative_with_retry().
    Returns empty dict if file not found (build_narrative_with_retry handles gracefully).
    """
    path = Path(f"output/context/context_{date.today()}.json")
    if not path.exists():
        # Fallback: find latest context file
        candidates = sorted(Path("output/context").glob("context_*.json"))
        if not candidates:
            return {}
        path = candidates[-1]
    return json.loads(path.read_text())
```

**통합 실행 흐름 (v3.5 CR-5-3 + DG-11 업데이트)**:
```python
# weekly_orchestrator.py (공식 통합 흐름 — §9-8 build_narrative_with_retry 기반)
context_data = load_context_data()          # DG-11: context_[날짜].json → dict
narrative = build_narrative_with_retry(     # CR-5-4: 최대 3회 Reflect-Revise
    context_data=context_data,              # citation_validator + intelligence_engine 공유
    intelligence_engine=intelligence_engine,
    reviewer_agent_fn=reviewer_agent_fn,
)
# citation_validator는 build_narrative_with_retry() 내부 Step 5에서 자동 호출 (§9-8)
# content_gate는 build_narrative_with_retry() 내부 Step 6에서 자동 호출 (§9-7-2)
# @translator spawn은 build_narrative_with_retry() 반환 후 Orchestrator가 트리거
```

---

## 20. 적대적 성찰 개선 명세 (v3.6 — I-2~I-13)

> **배경**: v3.6에서 5명의 적대적 에이전트(회의론자·통계학자·기술 비평가·법률 감시자·UX 심문관)가 prd.md를 공격하고 방어하는 과정에서 발견된 설계 결함·알고리즘 버그·측정 오류를 이 섹션에 명세한다.
> **참조**: PRD v1.3 기준. 각 개선점은 prd.md의 대응 섹션을 명시.

---

### 20-1. I-7 — Category B 신흥 테마 알고리즘 버그 수정 (synthesize_macro.py)

> **버그**: prd.md §7.6 pseudo-code `avg_4week_count = topic.avg_signal_count_past_4_weeks or 1`
> 이 `or 1` 제로가드는 이력이 없는 완전히 새로운 토픽에 2건 언급만으로 "200% 급증 + 신흥 테마" 판정을 허용한다.
> 새 토픽 2개 언급 → avg=0 → or 1 → 2/1=200% → theme_confidence=0.67 → Category B 진입 → **허위 신흥 테마**.

```python
# investscan/synthesize_macro.py — Category B 신흥 테마 식별 (v3.6 I-7 수정)
# P6: 모든 임계값 상수로 정의. LLM 판단 금지.

from dataclasses import dataclass
from typing import Final

# ── 신흥 테마 식별 안전망 상수 ─────────────────────────────────────────────────
THEME_SURGE_RATIO: Final[float] = 2.0        # 4주 평균 대비 최소 2배 급증
THEME_MIN_ABS_COUNT: Final[int]  = 5         # 이번 주 절대 신호 수 최소값 (허위 신호 차단)
THEME_MIN_WEEKS_TRACKED: Final[int] = 2      # 최소 2주 이상 추적된 토픽만 대상
THEME_MIN_AVG_COUNT: Final[float] = 1.0      # avg_4week_count가 1.0 미만이면 이력 부족 → 제외
THEME_CONFIDENCE_THRESHOLD: Final[float] = 0.55
THEME_GROWTH_CATEGORIES: Final[frozenset] = frozenset(["T", "E_env", "P"])

@dataclass(frozen=True)
class TopicSignal:
    """신흥 테마 후보 토픽 데이터."""
    topic_name: str
    steeps_category: str
    signal_count_this_week: int
    avg_signal_count_past_4_weeks: float   # 0.0 허용 (새 토픽)
    weeks_tracked: int                     # 추적 주 수
    weeks_in_category_b: int               # Category B 유지 주 수
    consecutive_below_55: int              # 55% 미만 연속 주 수

def identify_emerging_themes(topic_signals: list[TopicSignal]) -> list[tuple[str, float]]:
    """
    신흥 성장 테마 식별 — Category B 후보 반환.
    Returns: list of (topic_name, theme_confidence)

    Bug fix (v3.6 I-7):
    - 기존 `or 1` 제로가드 완전 제거
    - MIN_WEEKS_TRACKED: 새 토픽(이력 없음) 제외
    - MIN_ABS_COUNT: 절대 신호 수 최소값으로 허위 급증 차단
    - MIN_AVG_COUNT: 이력 평균이 1.0 미만이면 제외 (희소 토픽 제외)

    P6: NO LLM calls. Pure Python threshold comparison.
    """
    emerging = []

    for topic in topic_signals:
        # 안전망 1: 최소 추적 주 수 미달 → 제외 (완전 새 토픽 차단)
        if topic.weeks_tracked < THEME_MIN_WEEKS_TRACKED:
            continue

        # 안전망 2: 4주 평균 절대값 부족 → 제외 (희소 토픽 차단)
        if topic.avg_signal_count_past_4_weeks < THEME_MIN_AVG_COUNT:
            continue

        # 안전망 3: 이번 주 절대 신호 수 미달 → 제외 (단발 언급 차단)
        if topic.signal_count_this_week < THEME_MIN_ABS_COUNT:
            continue

        # 신흥 테마 식별: 급증 비율 계산 (or 1 제거 — avg >= 1.0 보장됨)
        surge_ratio = topic.signal_count_this_week / topic.avg_signal_count_past_4_weeks
        if surge_ratio < THEME_SURGE_RATIO:
            continue

        # 성장 테마 카테고리 필터
        if topic.steeps_category not in THEME_GROWTH_CATEGORIES:
            continue

        # 테마 신뢰도 계산
        theme_confidence = min(
            topic.signal_count_this_week / (topic.avg_signal_count_past_4_weeks * 3.0),
            1.0
        )
        if theme_confidence >= THEME_CONFIDENCE_THRESHOLD:
            emerging.append((topic.topic_name, theme_confidence))

    return emerging


def apply_category_b_lifecycle(themes: list[TopicSignal]) -> list[TopicSignal]:
    """
    Category B 유지·제거 정책:
    - 4주 연속 55% 미만 → 자동 제거
    - 24주 최대 유지 → M2 아카이브
    """
    active = []
    for theme in themes:
        if theme.consecutive_below_55 >= 4:
            continue   # 제거
        if theme.weeks_in_category_b >= 24:
            continue   # M2 아카이브
        active.append(theme)
    return active
```

**TDD 요구사항 (95% — P1 Critical)**:
```python
# tests/test_synthesize_macro_theme.py
# TestNewTopicExcluded: weeks_tracked=1 → 제외 (핵심 버그 수정 검증)
# TestSparseAvgExcluded: avg=0.5 → 제외 (MIN_AVG_COUNT 안전망)
# TestLowAbsCountExcluded: signal_count_this_week=3 → 제외 (MIN_ABS_COUNT 안전망)
# TestSurgeRatioMet: avg=5, current=10 → 200% 충족 → 후보
# TestSurgeRatioNotMet: avg=5, current=9 → 180% 미달 → 제외
# TestCategoryFilter: steeps_category="E" → 성장 카테고리 아님 → 제외
# TestConfidenceThreshold: theme_confidence=0.54 → 55% 미달 → 제외
# TestConfidencePass: theme_confidence=0.67 → Category B 진입
# TestDeterminism: 동일 입력 100회 → 동일 결과
# TestLifecycle4Weeks: consecutive_below_55=4 → 제거
# TestLifecycle24Weeks: weeks_in_category_b=24 → 아카이브
```

---

### 20-2. I-3/I-4/I-13 — accuracy_tracker.py 정확도 측정 명세 (v3.6)

> **I-3 문제**: 기존 28일(4주) 1회 스냅샷은 "4-12주 방향성" 타임프레임 시작점에서만 측정. 6주째 맞는 예측이 4주에 틀렸다고 KS-1 트리거 가능.
> **I-4 문제**: Bullish → +2% 초과 기준은 약세장(0~2% 상승)에서 모든 Bullish 예측을 WRONG으로 집계. 구조적 불이익.
> **I-13 문제**: "항상 Bullish" 단일 Naive Baseline은 횡보장에서 오히려 불리 → 시스템 가치 과소평가. 3가지 비교 전략 필요.

```python
# investscan/accuracy_tracker.py — 정확도 측정 명세 (v3.6 I-3/I-4/I-13)
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from typing import Final, Literal

# ── 측정 윈도우 상수 (I-3) ─────────────────────────────────────────────────────
MEASUREMENT_WINDOW_4W: Final[int]  = 28   # 4주 예비 측정 (days)
MEASUREMENT_WINDOW_8W: Final[int]  = 56   # 8주 최종 측정 — 타임프레임 중앙값 (days)
KS1_TRIGGER_AFTER_RUNS: Final[int] = 8    # KS-1은 최종 측정(8주) 기준 8회 누적 후 평가
# ⚠️ KS-1 실제 가능 시점: 8주 × 8회 = 16주 이후 = Month 3-4 (prd.md "Month 3 데이터 기반 Kill Switch")

# ── 정확도 판정 임계값 (I-4) ───────────────────────────────────────────────────
BULLISH_CORRECT_THRESHOLD: Final[float] = 0.01   # +1% 초과 (기존 +2% → 완화)
BEARISH_CORRECT_THRESHOLD: Final[float] = -0.01  # -1% 미만 (기존 -2% → 완화)
NEUTRAL_BAND: Final[float] = 0.03               # ±3% 이내 (기존 ±2% → 완화)
# 근거 I-4: 섹터 방향 예측 목적은 "정확한 수익률 예측"이 아닌 "방향 판단"
#   → 방향 일치 여부가 더 적절한 기준. ±2%는 약세장에서 Bullish를 구조적으로 불이익.

class Direction(StrEnum):
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"

@dataclass(frozen=True)
class PredictionRecord:
    """예측 기록 — prediction 시점에 저장."""
    run_id: str               # "2026-05-18" (발행 날짜)
    sector: str               # "반도체"
    predicted_direction: Direction
    confidence: float         # 0.0–1.0
    signal_ids: list[str]     # 근거 신호 ID 목록
    benchmark_etf: str        # "091160" (KODEX 반도체)
    predicted_at: date

@dataclass
class AccuracyResult:
    """정확도 평가 결과 — 측정 시점에 기록."""
    run_id: str
    sector: str
    predicted_direction: Direction
    actual_return_4w: float | None = None   # 4주 예비 측정
    actual_return_8w: float | None = None   # 8주 최종 측정
    verdict_4w: Literal["CORRECT", "WRONG", "PENDING"] = "PENDING"
    verdict_8w: Literal["CORRECT", "WRONG", "PENDING"] = "PENDING"
    # KS-1은 verdict_8w 기준으로만 집계

def evaluate_verdict(direction: Direction, actual_return: float) -> Literal["CORRECT", "WRONG"]:
    """
    방향 예측 정확도 판정 (v3.6 I-4 임계값 완화).
    Bullish → +1% 초과 ✅ | Bearish → -1% 미만 ✅ | Neutral → ±3% 이내 ✅
    """
    if direction == Direction.BULLISH:
        return "CORRECT" if actual_return > BULLISH_CORRECT_THRESHOLD else "WRONG"
    elif direction == Direction.BEARISH:
        return "CORRECT" if actual_return < BEARISH_CORRECT_THRESHOLD else "WRONG"
    else:  # NEUTRAL
        return "CORRECT" if abs(actual_return) <= NEUTRAL_BAND else "WRONG"


# ── Naive Baseline 3가지 비교 전략 (I-13) ─────────────────────────────────────
class NaiveStrategy(StrEnum):
    ALWAYS_BULLISH = "always_bullish"    # 모든 섹터 항상 긍정
    MOMENTUM      = "momentum"           # 전주와 동일 방향 유지
    RANDOM_50     = "random_50"          # 50% 확률 랜덤 (이론값 50%)

def compute_naive_baselines(
    history: list[AccuracyResult],
    prev_directions: dict[str, Direction],    # {sector: prev_direction} for Momentum
) -> dict[NaiveStrategy, float]:
    """
    3가지 Naive 전략의 월간 적중률 계산 (v3.6 I-13).
    InvestScan이 3가지 모두를 초과해야 의미 있는 시스템.

    Returns:
        {NaiveStrategy: accuracy_rate}  # 0.0–1.0
    """
    results: dict[NaiveStrategy, list[bool]] = {s: [] for s in NaiveStrategy}

    for record in history:
        if record.verdict_8w != "PENDING" and record.actual_return_8w is not None:
            ret = record.actual_return_8w

            # Always Bullish
            results[NaiveStrategy.ALWAYS_BULLISH].append(
                ret > BULLISH_CORRECT_THRESHOLD
            )
            # Momentum: 전주와 동일 방향으로 예측했을 때
            prev = prev_directions.get(record.sector, Direction.NEUTRAL)
            momentum_verdict = evaluate_verdict(prev, ret)
            results[NaiveStrategy.MOMENTUM].append(momentum_verdict == "CORRECT")

            # Random 50%: 이론값 고정 0.5 (실제 랜덤 시뮬레이션 대신)
            results[NaiveStrategy.RANDOM_50].append(True)  # placeholder (0.5 이론값)

    rates = {}
    for strategy, verdicts in results.items():
        if strategy == NaiveStrategy.RANDOM_50:
            rates[strategy] = 0.50   # 이론값
        elif verdicts:
            rates[strategy] = sum(verdicts) / len(verdicts)
        else:
            rates[strategy] = 0.0

    return rates

# ── 월간 정확도 리포트 출력 (Telegram) ────────────────────────────────────────
# "📊 이번 달 정확도:
#    InvestScan: 62% | Always-Bullish: 44% | Momentum: 55% | Random: 50%
#    InvestScan이 모든 Naive 전략을 초과 ✅"
# KS-1 평가 기준: verdict_8w 기준 누적 8회 이상 집계 후 <35% 시 발동
#   ("Month 3 데이터 기반 Kill Switch" — prd.md §4.2 라벨 수정 v3.6 I-5)
KS1_ACCURACY_THRESHOLD: Final[float] = 0.35   # 8주 측정 기준 (기존 40% → 조정)
```

**TDD 요구사항 (90% — 핵심 파이프라인)**:
```python
# tests/test_accuracy_tracker.py
# TestVerdictBullishCorrect: actual=+1.1% → CORRECT (임계값 +1% 완화 확인)
# TestVerdictBullishWrong: actual=+0.9% → WRONG (기존 +2% 기준이면 CORRECT였을 것)
# TestVerdictBearishCorrect: actual=-1.1% → CORRECT
# TestVerdictNeutralBand: actual=+2.9% → CORRECT (±3% 이내)
# TestDualWindowPending: 4주 미경과 → verdict_4w/8w=PENDING
# TestDualWindow4W: 28일 경과 → verdict_4w 갱신
# TestDualWindow8W: 56일 경과 → verdict_8w 갱신 (KS-1 기준)
# TestNaiveAlwaysBullish: bullish_threshold 기준 적중률 계산
# TestNaiveMomentum: 전주 방향 유지 전략 계산
# TestNaiveRandom: 항상 0.50
# TestKS1NotTriggered: 8회 미만 → KS-1 평가 없음
# TestKS1Triggered: 8회 이상 + accuracy < 0.35 → KS-1 flag
```

---

### 20-3. I-9/I-10 — 법적 컴플라이언스 강화 명세

> **I-9 문제**: prd.md §15.1 법적 비해당 근거 1순위가 "특정인 대상 아님"인데, 단일 사용자 로컬 도구는 오히려 "더 특정인 대상"으로 해석될 수 있음. 논리 순서 역전.
> **I-10 문제**: onboarding_mode 4주 기억 + 가중치 자동 조정 제안이 "계속적 관계" 증거로 사용될 수 있음.

```python
# investscan/compliance_filter.py — 법적 근거 강화 (v3.6 I-9/I-10)
# 기존 10개 금지 패턴(H-1)은 유지. 추가 강화 사항:

# ── 투자자문업 비해당 3대 근거 (재정렬 — I-9) ───────────────────────────────────
# 1순위: 계속적 계약 없음 (단발 설치, 서비스 계약 없음)
# 2순위: 보수 수취 없음 (InvestScan 리포트에 대한 유료 청구 없음)
# 3순위: 자기 결정 도구 (사용자 본인의 투자 판단 보조, 제3자 권고 아님)
# → "특정인 대상 아님" 논거는 보조적 위치로 이동 (법적 주력 근거 아님)
LEGAL_NON_ADVISORY_BASIS = [
    "no_continuous_contract",    # 1순위
    "no_compensation",           # 2순위
    "self_decision_tool",        # 3순위
]

# ── 계속적 관계 방지 가드레일 (I-10) ─────────────────────────────────────────
# 가중치 조정 이력 저장 시 법적 고지 주석 필수 포함:
WEIGHT_ADJUSTMENT_LEGAL_NOTE = (
    "이 조정은 알고리즘 성능 개선 목적이며, "
    "귀하의 개인 투자 성향을 학습하는 것이 아닙니다."
)

# investscan.yaml _config_history 기록 형식 (법적 고지 포함):
# _config_history:
#   - "2026-03-28: signal_policy.topic_trend_weight 0.20→0.15
#      [사용자 승인: 예] [목적: 알고리즘 성능 개선, 개인화 아님]"

# ── 리포트 공유 경고 (I-10 신규) ──────────────────────────────────────────────
# Day 0 설치 완료 시 실행방법.txt에 자동 포함:
SHARING_WARNING = (
    "📌 법적 안내: 이 리포트는 귀하의 개인 로컬 도구가 생성한 것입니다. "
    "제3자에게 제공하거나 공개 게시하는 경우 법적 상황이 달라질 수 있습니다."
)
```

---

### 20-4. I-11 — Portfolio 컨텍스트 기능 명세

> **I-11 문제**: 6분 루틴 "1분 — 포트폴리오 대조"에서 사용자가 본인 ETF 비중을 즉시 알고 있다고 가정. 비코더 사용자에게 비현실적.

```python
# investscan/personalizer.py — portfolio 컨텍스트 기능 (v3.6 I-11)
from typing import Optional

def update_portfolio_holdings(sector: str, allocation_pct: float) -> None:
    """
    Telegram 답장으로 보유 비중 업데이트.
    파싱 패턴: "반도체 ETF 3%", "바이오 5%", "포트폴리오: 반도체 3, IT 7"
    → state.yaml portfolio.holdings 갱신 (월 1회 권장)
    """
    ...

def generate_portfolio_comparison(
    sector: str,
    direction: str,            # "Bullish" / "Neutral" / "Bearish"
    confidence: float,
    holdings: dict[str, float], # state.yaml portfolio.holdings
) -> Optional[str]:
    """
    섹터 방향과 현재 보유 비중 자동 대조 문구 생성.
    holdings에 해당 섹터 없으면 None 반환 (출력 생략).

    Returns:
        "반도체 🟢 긍정 (72%) — 현재 보유: 3% → 행동: 비중 확대 검토"
        "바이오 🔴 주의 (34%) — 현재 보유: 5% → 행동: 비중 점검 권장"
    """
    ...

# report_generator.py 통합 포인트:
# - 섹터 방향 블록 렌더링 시 generate_portfolio_comparison() 호출
# - 반환값이 None이면 기존 출력 (비중 정보 없음)
# - auto_compare: false이면 호출 생략

# Telegram 피드백 파싱 패턴:
PORTFOLIO_UPDATE_PATTERNS = [
    r"반도체\s*ETF?\s*(\d+(?:\.\d+)?)%?",
    r"포트폴리오[:\s]+(.+)",
    r"(\w+)\s+(\d+(?:\.\d+)?)%",
]
```

---

### 20-5. I-12 — Bear Case UX 구현 명세

> **I-12 문제**: Bear Case가 섹터 상세 분석(4번 섹션) 직후에 위치하면, 긍정 방향 직후 부정 시나리오를 읽게 되어 결정 마비 유발. 전문가용 섹션이 비코더 사용자 결정 흐름을 방해.

```python
# investscan/report_generator.py — Bear Case 섹션 순서 (v3.6 I-12)
# prd.md §7.8 리포트 섹션 고정 순서 → Bear Case 위치 변경:

REPORT_SECTION_ORDER = [
    "1_timeframe_notice",          # [필수] 분석 타임프레임 안내
    "2_action_of_week",            # [필수] 이번 주 행동 1가지 (최우선 노출)
    "3_sector_summary",            # [필수] 섹터 방향 요약
    "4_sector_detail",             # [필수] 섹터별 상세 분석 (인과 논리 체인)
    "5_watchlist_a",               # [필수] Category A 워치리스트 (최대 5종목)
    "6_watchlist_b",               # [필수] Category B 워치리스트 (최대 3종목)
    "7_action_checklist",          # [필수] 이번 주 행동 체크리스트
    "8_portfolio_comparison",      # [조건부] portfolio.auto_compare=true 시만
    "9_all_bullish_warning",       # [조건부] 전 섹터 동일 방향 3주 연속 시만
    "10_bear_case",                # [필수] ← v3.6 I-12: 워치리스트 이후로 이동
    "11_disclaimer",               # [필수] 면책 조항 (항상 최하단)
]
# 변경 전: Bear Case가 5번 위치 (섹터 상세 직후)
# 변경 후: Bear Case가 10번 위치 (워치리스트 후, 면책 조항 전)

# Bear Case Jinja2 템플릿 (weekly-report.md.j2 내):
BEAR_CASE_TEMPLATE = """
{%- if onboarding_mode %}
> **참고**: 이 섹션은 예측이 틀렸을 때의 시나리오입니다. 결정에 반드시 고려할 필요는 없습니다.
{%- endif %}

## ⚠️ 이 방향이 틀릴 수 있는 상황 (참고용)

현재 방향({{ direction }} {{ confidence }}%)이 틀렸을 때 가장 가능성 높은 시나리오:
{% for scenario in bear_cases %}
→ {{ scenario.description }} (신호 #{{ scenario.signal_id }})
{% endfor %}

⚠️ 이 시나리오는 현재 방향의 반대 가능성입니다. 투자 결정 전 확인하세요.
"""

# Telegram 5줄 요약: Bear Case 미포함 (간결성 유지)
# → report_generator.telegram_summary()에서 "10_bear_case" 섹션 제외
```

---

### 20-6. I-2/I-5 — 설치 타임라인 + KS-1 라벨 수정

> **I-2**: Day 0 "30-60분" 설치 추정은 인터넷 속도 미고려. 과소평가 위험.
> **I-5**: KS-1 "Month 2 Kill Switch" 라벨은 28일 × 8회 측정 지연으로 실제 Month 3-4에야 평가 가능. 라벨 오류.

```python
# investscan/config.py — Day 0 설치 타임라인 명세 (v3.6 I-2)
INSTALLATION_TIME_GUIDE = {
    "fast_internet_100mbps_plus": "약 2시간",
    "normal_internet_50mbps":     "약 3-4시간",
    "slow_internet_10mbps_minus": "5시간 이상 (다음날 분할 설치 권장)",
}
# Day 0 시작 전 Claude Code가 인터넷 속도 측정 후 현실적 시간 안내:
# `curl -s -w '%{time_total}' -o /dev/null https://speed.cloudflare.com/__down?bytes=10000000`
# → 10MB 다운로드 시간으로 대역폭 추정 → INSTALLATION_TIME_GUIDE 분기 안내

# KS-1 라벨 수정 (I-5):
# - prd.md §4.2·§13.3 라벨: "Month 2 Kill Switch" → "Month 3 데이터 기반 Kill Switch"
# - 근거: 8주 최종 측정(MEASUREMENT_WINDOW_8W=56일) × 8회 = 16주 후에야 KS-1 평가 가능
# - accuracy_tracker.py 로그/알림에서 이 라벨 사용:
KS1_LABEL = "Month 3+ 데이터 기반 Kill Switch"  # v3.6 I-5
KS1_EXPLANATION = (
    "KS-1은 8주 최종 측정 기준 8회 누적 후 평가됩니다. "
    "실제 평가 가능 시점은 Month 3-4입니다 (8주 × 8회 = 16주+)."
)
```

---

### 20-7. ADR-017: Adversarial Reflection Architecture Decisions

```markdown
## ADR-017: Adversarial Reflection — prd.md 공격·방어·개선 (v3.6)

**날짜**: 2026-03-29
**상태**: 승인됨 (v3.6 반영 완료)
**배경**: 5명 적대적 에이전트가 prd.md를 공격·방어. 13개 개선점 도출.

### 핵심 결정

**결정 1 (I-7)**: Category B 신흥 테마 알고리즘에서 `or 1` 제로가드 제거.
- 대안 유지: MIN_WEEKS_TRACKED=2 + MIN_ABS_COUNT=5 + MIN_AVG_COUNT=1.0 삼중 안전망.
- 이유: 신규 토픽 2건 언급 = 신흥 테마 허위 판정 차단 필수.

**결정 2 (I-3/I-4)**: 정확도 측정 이중 윈도우 (4주 예비 + 8주 최종).
- 대안 거부: 단일 8주 측정 → 리포트 피드백 지연 너무 큼.
- 선택: 4주 예비(사용자 참고) + 8주 최종(KS-1 트리거 유일 기준).

**결정 3 (I-13)**: Naive Baseline을 3가지로 확장 (Always-Bullish + Momentum + Random).
- 이유: Momentum 전략은 자기상관을 자동 반영 → 더 공정한 비교 기준.
- InvestScan이 3가지 모두 초과해야 의미 있는 시스템으로 인정.

**결정 4 (I-11)**: Portfolio 컨텍스트 기능 추가 (state.yaml portfolio 섹션).
- 이유: 6분 루틴 "1분 포트폴리오 대조"는 비코더 사용자가 즉시 비중을 알 수 없음.
- 설계: 월 1회 Telegram 답장으로 업데이트. 자동 대조 문구 생성.

**결정 5 (I-9)**: 법적 비해당 근거 재정렬.
- 1순위: 계속적 계약 없음 / 2순위: 보수 없음 / 3순위: 자기 결정 도구.
- "특정인 대상 아님" 논거 → 보조적 위치 (1순위에서 제거).

**결정 6 (I-12)**: Bear Case 위치 이동 (섹터 분석 직후 → 워치리스트 후).
- 이유: 비코더 사용자의 결정 마비 방지. 전문가용 시나리오는 참고용으로.
- Telegram 5줄 요약에서는 계속 제외.
```

---

## 참조 문서

| 문서 | 목적 |
|-----|------|
| `workflow.md` | 실행 대상 Step 1-15 (변경 없음) |
| `prd.md` | 제품 요구사항 SOT |
| `CLAUDE.md` | 프로젝트 헌법 + 절대 기준 |
| `AGENTS.md` | 에이전트 공통 지시서 |
| `.claude/agents/translator.md` | @translator 7단계 프로토콜 (완비 — 수정 없음) |
| `translations/glossary.yaml` | 번역 용어 사전 (InvestScan 확장) |
| `docs/protocols/quality-gates.md` | L0-L2 4계층 품질 보장 |
| `docs/protocols/code-change-protocol.md` | CCP 3단계 + CAP |
| `docs/protocols/context-preservation-detail.md` | RLM + Hook 내부 메커니즘 |
