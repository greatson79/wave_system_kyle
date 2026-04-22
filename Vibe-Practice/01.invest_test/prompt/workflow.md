# InvestScan — 로컬 AI 투자 인텔리전스 자동화 시스템

> 사용자의 최소 입력을 받아, 미국 FRED 매크로 지표 + 글로벌 뉴스 신호를 반영한 날카로운 통찰로 —
> **수치·근거·리스크·방향성 의견을 갖춘** — **전문 애널리스트급 분석 형식·엄밀성의 종목 투자 원고**를 자동 생성한다.
> *(법적 이유로 매수/매도 추천·목표주가 제외 — 방향성 참고 자료로 활용)*
> 안정적 현재 종목(Category A)과 미래 성장 테마(Category B)를 구분하여 제공하며,
> **편집 없이 즉시 투자 판단과 콘텐츠 게시에 활용할 수 있는 완성본**을 출력한다.

---

## Overview

- **Input**: EnvironmentScan `database.json` + GlobalNews `signals.parquet` (선택) + FRED / DART / pykrx / FDR API
- **Output**: Telegram 5줄 요약 + Markdown 상세 리포트 + 종목 관찰 워치리스트 (Category A/B)
- **Frequency**: Weekly — Stage 1(일요일 20:00 launchd 자동 데이터 수집) + Stage 2(월요일 사용자 `/weekly-report` 트리거)
- **Autopilot**: disabled — 3개 HITL 게이트 필수 (HITL-1 설정, HITL-2 M1 전환, HITL-3 리포트 검수)
- **pACS**: enabled
- **Absolute Goal** (모든 단계·모든 판단의 유일한 기준):
  > "사용자의 최소 입력 → 전문 애널리스트급 분석 형식·엄밀성의 방향성 참고 원고 → 편집 없이 즉시 사용 가능한 완성본"
- **참조 문서**:
  - PRD: `/prompt/prd.md` (v1.3)
  - 아이디어 회의록: `/prompt/workflow-idea/workflow-idea.md` (v4 Final)
- **Local-Only 원칙**: 클라우드 배포 절대 금지. launchd + macOS Keychain + 로컬 파일시스템만 사용.
- **DKS 평가**: InvestScan은 **금융 분석** 자체가 아닌 **코드 자동 구현**이 목적. 도메인 지식(금융법, 컴플라이언스)은 `compliance_filter.py`에 내장되어 DKS 역할을 대신함. → **Research 단계 별도 DKS 구축 불필요** (compliance_filter가 대신함).
- **EnvironmentScan 운영 가이드** (InvestScan의 1차 신호 소스):
  - **목적**: 글로벌·국내 뉴스에서 STEEPs(T/E/P/S/E_env/s) 신호를 추출하는 **별도 독립 시스템** (InvestScan과 분리 설치·실행)
  - **실행 빈도**: 주 1~2회 권장 (주말 실행 → 일요일 20:00 launchd 자동 수집 시 사용)
  - **산출물**: `database.json` — Step 1에서 자동 탐색 (경로는 사용자 환경마다 다름)
  - **없으면**: Step 1이 `runtime_mode = "independent"` 자동 설정 → FRED 데이터만으로 제한된 분석 진행 (⚠️ 신뢰도 제한)
  - **설치**: EnvironmentScan 프로젝트 자체 문서 참조 (InvestScan 범위 외)

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.
> Purpose varies by domain; the genome is identical. See `soul.md §0`.

**Constitutional Principles** (InvestScan 도메인에서의 발현):

1. **Quality Absolutism** — 최종 리포트가 "편집 없이 즉시 투자 판단과 콘텐츠 게시에 활용"되는 수준이어야 함. 속도·토큰 비용 완전 무시. 미충족 항목 있으면 Step 10-R 재조정 루프 실행.
2. **Single-File SOT** — `.claude/state.yaml`이 모든 공유 상태의 유일한 진실 출처. `weekly_orchestrator.py`(Stage 1 완료 시)와 Claude Code 세션(Stage 2)만 SOT 쓰기 권한 보유. 모듈들은 SOT를 읽기 전용으로 참조.
3. **Code Change Protocol** — 모든 모듈 구현 전: (1) 의도 파악 → (2) 영향 범위 분석 → (3) 변경 설계 3단계 수행. **CAP 4원칙 내면화**: CAP-1(구현 전 사고), CAP-2(단순성 우선 — 과도한 추상화 금지), CAP-3(목표 기반 실행 — PRD 기능 요구에만 집중), CAP-4(외과적 변경 — 기존 동작 최소 침범).

**Inherited Patterns**:

| DNA Component | Inherited Form (InvestScan) |
|--------------|----------------------------|
| 3-Phase Structure | Research(환경 분석) → Planning(설계 확정) → Implementation(단계별 구현) |
| SOT Pattern | `.claude/state.yaml` — Orchestrator/Claude Code 단일 쓰기 |
| 4-Layer QA | L0 Anti-Skip → L1 Verification(8항목 validate) → L1.5 pACS → L2 Review |
| P1 Hallucination Prevention | `sentiment_weight: 0.0` 결정론적 강제 (변경 불가 원칙) |
| P2 Expert Delegation | `@reviewer`: 코드 품질 검증, `@fact-checker`: 신호·수치 정합성 |
| Safety Hooks | `block_destructive_commands.py` 기존 가동 |
| Adversarial Review | Step 7/11/12/14/15에서 `@reviewer` + Step 2/12에서 `@fact-checker` 적용 |
| Decision Log | `autopilot-logs/` 패턴 — HITL 결정 기록 |
| Context Preservation | 세션 간 state.yaml SOT + context_[날짜].json 지속 |

**Domain-Specific Gene Expression** (InvestScan에서 강하게 발현되는 DNA):
- **P1(데이터 정제)**: `sentiment_weight: 0.0` 절대 원칙 + STEEPs 사실 기반 신호만 사용 → 허위 상관 차단
- **P2(전문성 위임)**: 21개 모듈이 각 전문 영역에 집중. `intelligence_engine.py`가 원고 생성에만 집중.
- **SOT 보호**: Stage 1(launchd headless) ↔ Stage 2(Claude Code 인터랙티브) 분리 → SOT 충돌 방지

---

## ⚠️ 로컬 실행 절대 원칙 (SaaS 방지)

| 금지 항목 | 허용 대안 |
|---------|---------|
| 클라우드 서버 배포 | 로컬 launchd만 사용 |
| 외부 서버에 리포트/예측 기록 저장 | 로컬 파일시스템만 사용 |
| AWS Lambda / 외부 스케줄러 | 로컬 launchd만 사용 |
| API 키를 원격 환경변수 서비스에 저장 | macOS Keychain만 사용 |

**허용되는 외부 연결**: Claude API (M1 Stage 2), Telegram Bot API, FRED API, DART OpenAPI, pykrx, FinanceDataReader

---

## Research

### Step 1: Environment Pre-flight

- **Pre-processing**: `python3 -c "import sys; print(sys.version)"` 실행하여 Python 3.11+ 확인 후 실패 시 즉시 중단
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] Python 3.11.0 이상 확인 (`python3 --version` 결과 기록)
  - [ ] EnvironmentScan `database.json` 탐색 결과가 state.yaml `discovered_paths.envscan_wf1_output`에 기록됨
  - [ ] GlobalNews `signals.parquet` 탐색 결과가 state.yaml `discovered_paths.gnews_signals`에 기록됨 (없으면 `""` 기록 — graceful)
  - [ ] `runtime_mode`가 3가지 중 하나로 state.yaml에 기록됨: `"full"` / `"envscan_only"` / `"independent"`
  - [ ] `independent` 모드 시 Telegram 경고 메시지 초안이 준비됨
- **Task**: |
    Perform complete environment pre-flight check for InvestScan system.

    1. Verify prerequisites: Python 3.11+, pip3, internet connectivity (curl Telegram API).
    2. Auto-detect EnvironmentScan `database.json` by scanning paths in this order:
       - `~/Documents/EnvironmentScan/`
       - `~/Desktop/Ai_works/`
       - `~/`
       - Current working directory parent
    3. Auto-detect GlobalNews `signals.parquet` with similar path scanning.
    4. Determine runtime_mode: `full` (both found) / `envscan_only` (EnvScan only) / `independent` (neither found).
    5. Write ALL discovered paths and runtime_mode to `.claude/state.yaml` `discovered_paths` + `workflow.current_step: 1`.
    6. If `independent` mode: prepare Korean Telegram warning message (see PRD §11).
    7. Report findings to user with clear status for each dependency.

    Reference: `workflow-idea.md` 아이디어 1 Step 1 (D2), PRD §0.2
- **Output**: `.claude/state.yaml` (`discovered_paths` + `runtime_mode` 기록) + 콘솔 환경 점검 리포트
- **Review**: `none`
- **Translation**: `none`
- **Post-processing**: state.yaml `workflow.current_step` → 2 업데이트

---

### Step 2: Schema Analysis + PRD-vs-실제 조정

- **Pre-processing**: |
    ```bash
    python3 -c "
    import json, pathlib
    path = pathlib.Path('$(grep envscan_wf1_output .claude/state.yaml | cut -d: -f2 | tr -d " \"")').expanduser()
    if path.exists():
        data = json.loads(path.read_text())
        record = data[0] if isinstance(data, list) else list(data.values())[0]
        print('FIELDS:', list(record.keys()))
        print('SAMPLE:', str(record)[:500])
    else:
        print('FILE_NOT_FOUND')
    "
    ```
    출력 결과를 분석 입력으로 사용. FILE_NOT_FOUND이면 `independent` 모드로 스키마 기본값 적용.
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] `discovered_schema.envscan_wf1.steeps_field` 가 실제 필드명으로 기록됨 (예: `"preliminary_category"`)
  - [ ] `discovered_schema.envscan_wf1.psst_field` 또는 `psst_substitute` 중 하나 이상 기록됨
  - [ ] `discovered_schema.envscan_wf1.summary_field` 또는 `summary_substitute` 중 하나 이상 기록됨
  - [ ] `discovered_schema.envscan_wf1.score_scale` 기록됨 (`"0-100"` / `"0-10"` / `"0-1"`)
  - [ ] `discovered_schema.envscan_wf1.preliminary_category_values` 기록됨 — 실제 EnvScan에서 추출한 STEEPs 값 목록 (예: `["T","E","P","S","s","E_Environmental"]`). steeps_classifier.py가 이 값을 분기 기준으로 사용.
  - [ ] GlobalNews: `gnews.file_exists` 기록됨 (true/false)
  - [ ] `schema-mapping.md` 파일 생성됨 — PRD 기대 필드 vs 실제 필드 매핑 테이블 포함
  - [ ] `schema_decisions_recorded_at` 타임스탬프 기록됨 (source: Step 1 발견 경로)
- **Task**: |
    Analyze actual EnvironmentScan database.json schema and resolve PRD vs. reality gaps.

    1. Parse the actual database.json using pre-processing output. Extract real field names for:
       - STEEPs category field (PRD expects `steeps_category`, actual may be `preliminary_category`)
       - pSST score field (PRD expects `psst_score`, actual may be nested or absent → use `analysis.priority_score/5`)
       - Summary field (actual may be `content.abstract[:200]`)
    2. Determine pSST normalization scale:
       - EnvScan WF1: 0-100 int → divide by 100
       - EnvScan WF4: 0-10 float → divide by 10
       - GlobalNews: 0-1 float → use as-is
    3. Check GlobalNews signals.parquet existence; record `gnews.file_exists`.
    4. Record ALL schema decisions in `.claude/state.yaml` `discovered_schema` section.
    5. Create `output/schema-mapping.md` with: PRD expected field | Actual field | Handling method table.
    6. Note `overt_correction_needed: true` if any critical field is completely absent with no substitute.

    CRITICAL: Never auto-detect pSST scale — always record explicit decision.
    Reference: workflow-idea.md 아이디어 1 Step 2, PRD §0.4, §8.1
- **Output**: `.claude/state.yaml` `discovered_schema` 섹션 완성 + `output/schema-mapping.md`
- **Review**: `@fact-checker` — schema-mapping.md의 필드 매핑 정확성 검증
- **Translation**: `none`
- **Post-processing**: `overt_correction_needed: true` 이면 HITL-1 안건 목록에 추가. state.yaml `workflow.current_step` → 3 업데이트.

---

### Step 3: Dependency Validation + Fixtures

- **Pre-processing**: `cat .claude/state.yaml | grep runtime_mode` — 실행 모드 확인 후 필요 패키지 범위 결정
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] M0.5 최소 패키지 6개 설치 성공 (`finance-datareader`, `pandas`, `pyarrow`, `jinja2`, `requests`, `keyring`)
  - [ ] M1 패키지 추가 설치 성공 (`fredapi`, `dart-fss`, `pykrx`, `anthropic`)
  - [ ] `make_fixtures.py` 파일 생성됨 — 실제 database.json 샘플 3건으로 `UnifiedSignal` 테스트 픽스처 생성
  - [ ] `test_fixtures.py` 실행 성공 — 픽스처 로딩 및 기본 파싱 검증
  - [ ] `state.yaml packages.m05_ready: true` 기록됨
  - [ ] `failed_packages` 배열이 비어있거나 대안 설치 방법이 기록됨
- **Task**: |
    Install all required Python packages and generate test fixtures.

    1. Create `requirements.txt` with two sections (M0.5 minimum + M1 full) per PRD §0.3.
    2. Install M0.5 packages: `pip3 install finance-datareader pandas pyarrow jinja2 requests keyring`
    3. Install M1 packages: `pip3 install fredapi dart-fss pykrx anthropic`
    4. Record any failed packages in state.yaml `packages.failed_packages` with fallback note.
    5. Create `make_fixtures.py`: reads actual database.json, extracts 3 representative records,
       saves to `tests/fixtures/envscan_sample.json`. Include edge cases: missing fields, null values.
    6. Create `tests/test_fixtures.py` with basic loading assertions. Run it. Assert pass.
    7. Create `investscan/` project directory structure:
       ```
       investscan/
       ├── config.py, schema.py, normalizers.py, synthesize_macro.py, telegram_notifier.py
       ├── compliance_filter.py, dedup.py, steeps_classifier.py, signal_bridge.py
       ├── korea_signal_layer.py, stock_selector.py, synthesize_stock.py
       ├── valuation_comparator.py, intelligence_engine.py, report_generator.py
       ├── validate_report_quality.py, weekly_orchestrator.py, accuracy_tracker.py
       ├── watchdog.py, health_dashboard.py, personalizer.py
       ├── templates/weekly-report.md.j2
       ├── config/sector_stock_map.yaml
       ├── tests/
       ├── output/reports/, output/temp/, output/context/
       ├── data/accuracy/, data/journal/
       └── logs/
       ```
    8. Update state.yaml: `packages.m05_ready: true`, `packages.fixtures_generated: true`.

    Reference: PRD §0.3, workflow-idea.md 아이디어 2
- **Output**: `requirements.txt` + `investscan/` 디렉터리 구조 + `tests/fixtures/` + state.yaml 업데이트
- **Review**: `none`
- **Translation**: `none`
- **Post-processing**: state.yaml `workflow.current_phase: "planning"`, `workflow.current_step: 4` 업데이트

---

## Planning

### Step 4: Config & Path Setup + 완성본 정의

- **Pre-processing**: state.yaml `discovered_paths` 섹션 읽기 → `investscan.yaml` 초기값 자동 채움
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] `~/.investscan/investscan.yaml` 파일 생성됨 — PRD §7.12 전체 스키마 포함
  - [ ] `paths.envscan_wf1_output`이 Step 1에서 발견된 실제 경로로 설정됨 (source: Step 1)
  - [ ] `signal_policy.sentiment_weight: 0.0` 값이 설정됨 (P1 절대 원칙 — 변경 불가)
  - [ ] `user.sectors_of_interest: ["반도체", "IT서비스", "바이오"]` 기본값 설정됨 (D5 결정)
  - [ ] `onboarding_mode: true` 설정됨 (비코더 초기 진입 배려)
  - [ ] `output/completion-definition.md` 생성됨 — "완성본이란 무엇인가" 기준 문서 포함
- **Task**: |
    Generate investscan.yaml configuration file and define final deliverable standard.

    1. Create `~/.investscan/investscan.yaml` with complete schema (PRD §7.12):
       - Fill `paths.envscan_wf1_output` with value from state.yaml `discovered_paths.envscan_wf1_output`
       - Set `signal_policy.sentiment_weight: 0.0` — IMMUTABLE (P1 absolute principle)
       - Set `user.sectors_of_interest: ["반도체", "IT서비스", "바이오"]` as default (D5)
       - Set `onboarding_mode: true` for non-coder user experience
       - Leave `telegram.chat_id: ""` (filled in HITL-1)
       - Add `_config_history: []` for change tracking
    2. Create `config/sector_stock_map.yaml` with default sector → stock mappings:
       - 반도체: [삼성전자(005930), SK하이닉스(000660), 한미반도체(042700)]
       - IT서비스: [카카오(035720), NAVER(035420), 카카오페이(377300)]
       - 바이오: [셀트리온(068270), 삼성바이오로직스(207940), 한미약품(128940)]
    3. Create `output/completion-definition.md`:
       - Telegram 5-line summary format example (per PRD §3.2)
       - Report 10-section fixed order (per PRD §7.8)
       - Category A/B watchlist format (per PRD §7.6)
       - 8-item quality gate criteria (per PRD §핵심목적)
    4. Update state.yaml `workflow.current_step: 4` and record `discovered_paths.config_file`.

    Reference: PRD §7.12, §3.2, workflow-idea.md 핵심수정 7
- **Output**: `~/.investscan/investscan.yaml` + `config/sector_stock_map.yaml` + `output/completion-definition.md`
- **Review**: `none`
- **Translation**: `none`
- **Post-processing**: state.yaml `workflow.current_step` → 5 업데이트

---

### Step 5: Blueprint + Prompt Design + Dataclass Schema

- **Pre-processing**: `output/schema-mapping.md` + `output/completion-definition.md` 읽기 (source: Steps 2, 4)
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] `output/blueprint.md` 생성됨 — 21개 모듈 구현 순서, 의존성 다이어그램 포함
  - [ ] `schema.py` 작성됨 — 6개 frozen dataclass 모두 포함: `UnifiedSignal`, `InvestmentMeta`, `SectorDirection`, `StockAnalysisContext`, `DartFinancials`, `ValuationContext`, `PredictionRecord`, `NarrativeOutput` (7개 + SteepsCategory StrEnum)
  - [ ] `schema.py` — `SteepsCategory` StrEnum이 소문자 `s` 포함 6가지로 선언됨
  - [ ] Category A 시스템 프롬프트와 Category B 시스템 프롬프트가 각각 독립 상수로 정의됨
  - [ ] Few-shot 예시 **4쌍** (Category A Bullish·Bearish, Category B, Neutral)이 `config/few_shot.json`에 저장됨
  - [ ] Jinja2 변수 매핑 테이블이 `output/blueprint.md`에 포함됨 (NarrativeOutput JSON 키 ↔ Jinja2 변수)
  - [ ] `output/blueprint.md`가 Step 4 `completion-definition.md`의 기준을 참조함 (source: Step 4)
- **Task**: |
    Write complete implementation blueprint, dataclass schema, and Category A/B prompts.

    1. Create `schema.py` with ALL frozen dataclasses (P1: define before coding, not after):
       - `SteepsCategory(StrEnum)`: T, E, P, S, E_env, s (lowercase s is MANDATORY)
       - `UnifiedSignal(frozen=True, slots=True)`: id, title, summary, source, steeps_category,
         steeps_tags, psst_score, signal_date, schema_version
       - `SectorDirection(frozen=True, slots=True)`: sector_name, direction, confidence, signal_count, signal_ids
       - `InvestmentMeta(frozen=True, slots=True)`: report_date, sectors: list[SectorDirection], top_signals: list[UnifiedSignal], macro_summary: str, action_item: str, action_checklist: list[str], schema_version: str
       - `DartFinancials`, `ValuationContext`
       - `StockAnalysisContext(frozen=True, slots=True)`: ticker, name, category("A"|"B"),
         sector, foreign_flow_4w, financials, valuation, theme_name, theme_signals
       - `NarrativeOutput`: report_date, sector_narrative, causal_chains, stock_analyses,
         category_b_analyses, bear_case
       - `PredictionRecord(frozen=True, slots=True)`: report_week, sector, direction, confidence,
         signal_ids, created_at, actual_etf_return, hit, evaluated_at

    2. Define Category A and Category B system prompts as constants in `intelligence_engine.py`.
       Use the EXACT text below — do NOT paraphrase or simplify:

       ```python
       CATEGORY_A_SYSTEM_PROMPT = """
       당신은 한국 주식 시장 전문 퀀트 애널리스트입니다.
       현재 섹터 모멘텀이 확인된 종목에 대해 실적·밸류에이션 기반 분석 원고를 작성합니다.

       반드시 포함할 것:
       - 최근 2분기 YoY 매출·영업이익 성장률 (수치 포함) — DART 공시 기준 최신 분기 명시 (예: "2025Q4 기준")
       - 현재 PER vs 섹터 평균 비교 ("X배, 섹터 평균 대비 Y% 할인/프리미엄")
       - 외국인 수급 방향 (4주 누적 순매수/순매도)
       - 하방 리스크 1개 이상 (정량적 영향 서술)
       - 방향성 의견: "긍정적 모멘텀 유지", "중립 관망", "리스크 구간" 중 택1

       수치 인용 원칙 (P13 — 사실 검증 보장):
       - 모든 수치는 반드시 제공된 context_data의 실제 값만 인용할 것
       - context_data에 없는 수치를 임의로 생성하거나 추정하지 말 것
       - 해당 분기 DART 데이터가 없는 경우: "데이터 미수집" 또는 "분기보고서 공시 전"으로 표기

       절대 포함하지 말 것: 매수/매도 추천, 목표주가, 수익 보장
       """

       CATEGORY_B_SYSTEM_PROMPT = """
       당신은 한국 주식 시장 테마/성장주 전문 애널리스트입니다.
       신흥 글로벌 테마에서 수혜가 예상되는 종목에 대해 성장성 중심 분석 원고를 작성합니다.

       반드시 포함할 것:
       - 테마의 글로벌 시장 규모 및 성장률 (수치 포함)
       - 이 종목이 해당 테마에서 차지하는 포지셔닝 설명
       - 핵심 촉매 이벤트 1개 이상 (구체적 일정/조건)
       - 테마 지속 기간 추정 (예: "12~24주 모멘텀 예상")
       - 테마 소멸 리스크 (경쟁 진입, 정책 변화 등)
       - 주의사항: "현재 실적보다 미래 성장성에 근거한 분석"임을 명시

       절대 포함하지 말 것: 매수/매도 추천, 목표주가, 단기 등락 예측
       """
       ```

    3. Create `config/few_shot.json` with **4 representative examples** covering all critical dimensions:
       - **Example 1** (Category A · Bullish · 반도체): SK하이닉스 — HBM 수요 급증 + 외국인 순매수
         (input_context + expected_output per workflow-idea.md 아이디어 6)
       - **Example 2** (Category A · Bearish · 바이오): 삼성바이오로직스 — FDA 임상 지연 + 고밸류 부담
         (Bearish 방향 + 리스크 중심 서술 패턴 학습)
       - **Example 3** (Category B · Bullish · 신테마): AI 에이전트 수혜주 — 테마 초기 형성 + 4~12주 전망
         (Category B 테마 지속기간 추정 + 불확실성 명시 패턴 학습)
       - **Example 4** (Category A · Neutral · IT서비스): NAVER — 섹터 Neutral + 개별 모멘텀 혼재
         (Neutral 방향에서 투자의견 미제시 + 관찰 유지 서술 패턴 학습)
       각 예시는 `{"example_id": N, "category": "A"|"B", "direction": "Bullish"|"Bearish"|"Neutral", "sector": "...", "input_context": {...}, "expected_output": "..."}` 구조로 저장.

    4. Create `output/blueprint.md`:
       - Module implementation order: config → schema → normalizers → synthesize_macro →
         telegram_notifier → compliance_filter → (HITL-2) → dedup → steeps_classifier →
         signal_bridge → korea_signal_layer → stock_selector → synthesize_stock →
         valuation_comparator → intelligence_engine → report_generator →
         validate_report_quality → weekly_orchestrator → accuracy_tracker → watchdog →
         health_dashboard → personalizer
       - Jinja2 variable mapping table (NarrativeOutput JSON key ↔ template variable)
       - M0.5 vs M1 module boundary diagram

    Reference: workflow-idea.md 핵심수정 2, 3, 6, 아이디어 6, PRD §8.1, §8.2
- **Output**: `schema.py` (완성) + `output/blueprint.md` + `config/few_shot.json` + `intelligence_engine.py` (프롬프트 상수 포함 초안)
- **Review**: `@reviewer` — schema.py dataclass 설계 완전성 + 프롬프트 법적 컴플라이언스 (매수/매도 추천 부재 확인)
- **Translation**: `none`
- **Post-processing**: state.yaml `workflow.current_step: 5` 기록. Review FAIL 시 schema/프롬프트 수정 후 재검증.

---

### Step 6: (human) HITL-1 — 설정 확인 및 Telegram 연동

> **비코더 안내 원칙**: Claude Code가 각 항목을 **대화형으로 단계별 안내**한다. 사용자가 한 번에 모든 것을 입력할 필요 없음.

- **Action**: |
    Claude Code가 아래 순서로 사용자를 안내합니다:

    **[안내 시작 메시지]**
    "지금부터 InvestScan 설정을 단계별로 도와드리겠습니다.
     각 단계마다 무엇을 해야 하는지 안내해 드릴게요. 준비되셨으면 시작할게요!"

    **확인 항목 (순서대로):**

    1. **Claude Max 로그인 확인**
       → "Claude Code가 현재 실행 중이면 OK입니다 (이미 완료된 상태)."

    2. **EnvironmentScan 경로 확인**
       → "자동 탐색 결과: [발견된 경로]"
       → "이 경로가 맞으면 '네', 다르면 Finder에서 드래그하여 알려주세요."

    3. **Telegram 봇 토큰 입력**
       → "텔레그램 앱에서 @BotFather를 찾아 /newbot을 입력하세요.
          발급받은 토큰(예: 123456789:ABC-DEF...)을 여기에 붙여넣어 주세요."
       → Claude Code가 `keyring.set_password("investscan", "telegram_bot_token", token)` 자동 실행

    3b. **Telegram Chat ID 획득** (bot_token 등록 직후 — 메시지 발송에 **필수**)
       → "이제 텔레그램 앱에서 방금 만든 봇에게 '/start'를 보내주세요."
       → 사용자 전송 확인 후, Claude Code가 getUpdates API를 호출하여 chat_id 자동 추출:
          ```python
          import requests, keyring
          token = keyring.get_password("investscan", "telegram_bot_token")
          resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
          chat_id = str(resp["result"][0]["message"]["chat"]["id"])
          keyring.set_password("investscan", "telegram_chat_id", chat_id)
          ```
       → 성공 시 state.yaml `hitl_1.telegram_chat_id_registered: true` 업데이트
       → 실패 시 (result 비어있음): "봇에게 '/start'를 보내셨나요? 전송 후 다시 시도하겠습니다."
       ⚠️ **chat_id 없이는 Telegram 알림이 전혀 발송되지 않습니다.** bot_token만으로는 부족합니다.

       > **Telegram 아키텍처 원칙**: InvestScan의 Telegram은 **단방향 알림 채널**입니다.
       > 사용자 응답(답장)을 수신하는 폴링 메커니즘이 없습니다.
       > 인터랙션이 필요한 피드백·설정 변경은 반드시 Claude Code 세션에서 처리합니다.

    4. **DART OpenAPI 키 등록** (재무 수치 필수 — 생략 시 종목 실적 데이터 없음)
       → "DART(금융감독원 공시 시스템) API 키가 필요합니다.
          1) opendart.fss.or.kr 접속 → 회원가입 → API 키 신청 (무료, 정부 서비스)
          2) 발급된 키를 여기에 붙여넣어 주세요."
       → Claude Code가 `security add-generic-password -a investscan -s dart_api_key -w [KEY]` 자동 실행
       → 등록 실패 시 안내: "나중에 등록하셔도 됩니다. 등록 전까지는 재무 수치 없이 방향성만 분석됩니다."

    5. **FRED API 키 등록** (미국 매크로 지표 필수 — 생략 시 금리·CPI·VIX 데이터 없음)
       → "FRED(미국 연방준비제도 경제 데이터) API 키가 필요합니다.
          1) fred.stlouisfed.org/docs/api/api_key.html 접속 → 무료 계정 생성 → API 키 발급
          2) 발급된 키를 여기에 붙여넣어 주세요."
       → Claude Code가 `security add-generic-password -a investscan -s fred_api_key -w [KEY]` 자동 실행
       → 등록 실패 시 안내: "나중에 등록하셔도 됩니다. 등록 전까지는 미국 매크로 데이터 없이 국내 신호만 사용됩니다."

    6. **관심 섹터 확인** (기본값: 반도체·IT서비스·바이오)
       → "변경하고 싶은 섹터가 있으면 말씀해주세요. 없으면 기본값으로 진행합니다."

    7. **완성본 활용 방식 선택**
       - [A] 개인 투자 판단용 (내부 보관) ← 기본값 (D4 결정)
       - [B] 블로그/브런치 게시용 (강화 면책 조항 자동 포함)
       - [C] Obsidian/Notion 연동

    8. **특별 관심 종목** (선택)
       → "없으면 그냥 Enter 누르세요. 시스템이 자동 선정합니다."

    **완료 후**: state.yaml HITL-1 섹션 전체 업데이트 + investscan.yaml 설정 반영

    **overt_correction_needed 처리**: Step 2에서 발견된 경우 이 시점에 사용자에게 알림.
- **Command**: `/hitl-1-setup`
- **Autopilot Default**: 기본값 사용 (관심 섹터: 반도체·IT서비스·바이오, 플랫폼: 개인용)

---

## Implementation

### Step 7: M0.5 Core — 핵심 5개 모듈 + compliance_filter

- **Checkpoint Pattern**: `dense` (예상 15~20턴 — 5개 모듈 + 테스트 + DG 검증)
- **Pre-processing**: state.yaml `discovered_schema` + investscan.yaml 로드하여 모듈 구현 시 실제 필드명 사용
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`config.py`** (~100 LOC): `investscan.yaml` 로드 + Keychain 동적 로드 (`security find-generic-password` 사용) + 실제 파일 경로 관리
  - [ ] **`normalizers.py`** (~150 LOC, WF1 only): 실제 필드명(`preliminary_category` 등)으로 `database.json` → `UnifiedSignal` 변환 성공. psst 대체값 로직 포함.
  - [ ] **`synthesize_macro.py`** (~200 LOC): `sentiment_weight == 0.0` 검증 라인 포함. STEEPs 집계 → Bullish/Neutral/Bearish 판정 (≥65%/45-65%/<45%) 로직 구현.
  - [ ] **`telegram_notifier.py`** (~40 LOC): dry-run 모드 지원 (`--dry-run` 플래그) + Keychain에서 토큰 로드
  - [ ] **`compliance_filter.py`** (~80 LOC): 10개 금지 표현 패턴 모두 포함 (PRD 15.2 6개 + v4 추가 4개)
  - [ ] M0.5 Done Gate 8항목 (DG-01~DG-08) 모두 통과 (`python3 -m pytest tests/test_m05_done_gate.py`)
  - [ ] `python3 run_m05.py --input [경로] --dry-run` 성공 — Telegram 발송 직전 단계까지 확인
  - [ ] `sentiment_weight == 0.0` 자동 검증: `python3 -c "from config import load_config; c=load_config(); assert c.signal_policy.sentiment_weight == 0.0"`
- **Task**: |
    Implement InvestScan M0.5 core — 5 modules + compliance filter.

    CRITICAL CONSTRAINT: `sentiment_weight` MUST equal 0.0 at all times. This is P1 absolute principle.
    Any code path that could modify this value is a P1 violation.

    1. **config.py**: Load investscan.yaml + dynamically load secrets from macOS Keychain using
       `subprocess.run(["security", "find-generic-password", "-a", "investscan", "-s", key, "-w"])`.
       Never store API keys in plain text. Cache loaded config as singleton.

    2. **normalizers.py** (WF1 only at M0.5):
       - Use ACTUAL field names from `state.yaml discovered_schema` (NOT PRD assumed names)
       - Map `preliminary_category` → `steeps_category` with SteepsCategory enum
       - Handle psst substitute: `analysis.priority_score / 5` when psst_field is null
       - Handle summary substitute: `content.abstract[:200]` when summary_field is null
       - Graceful handling for missing `classification` (52% absent) and `analysis` (22% absent)

    3. **synthesize_macro.py**: Implement STEEPs aggregation algorithm:
       ```python
       # Step 1: Per-signal weighted score
       weighted_score = (
           steeps_event_score * config.signal_policy.steeps_event_weight +  # 0.70
           topic_trend_score  * config.signal_policy.topic_trend_weight +   # 0.20
           factor_score       * config.signal_policy.factor_score_weight    # 0.10
           # sentiment_weight: 0.0 — NEVER added here
       )

       # Step 2: Sector direction determination (P12 명확화)
       # sector_confidence = mean(weighted_score) of all UnifiedSignals mapped to that sector
       # via signal_bridge.py. Thresholds:
       #   Bullish:  sector_confidence >= 0.65
       #   Neutral:  0.45 <= sector_confidence < 0.65
       #   Bearish:  sector_confidence < 0.45
       # Edge case: signal_count < 2 → direction = "Neutral" (데이터 불충분)
       # Store as: SectorDirection(sector_name, direction, confidence=sector_confidence, signal_count=n, signal_ids)
       ```
       Output `InvestmentMeta` with sector directions + confidence + signal_ids.
       Generate BOTH of the following via rule-based logic (PRD §7.9 pseudo-code):
       - `action_item` (str): "이번 주 행동 1가지" — 단일 핵심 행동 문장 (Jinja2 `{{ action_item }}`)
       - `action_checklist` (list[str]): "이번 주 행동 체크리스트" — 복수 체크 항목 (Jinja2 `{% for item in action_checklist %}`)
       Both fields saved in InvestmentMeta and forwarded to report_generator.py.

    4. **telegram_notifier.py**: Send 5-line summary via Telegram Bot API.
       Support `--dry-run` flag that prints message without sending.
       3 retries on failure. Log failure to `logs/telegram_err.log`.

    5. **compliance_filter.py**: Implement the EXACT 10 prohibition rules below — do NOT reduce or modify:
       ```python
       COMPLIANCE_RULES = [
           # PRD 15.2 기본 6개
           ("매수 추천합니다",         "관찰 대상으로 분류되었습니다"),
           (r"\d+% 수익 예상",         "4-12주 방향성: 긍정 신호"),
           ("지금 사세요",             "이번 주 행동 참고 사항"),
           ("투자 조언",               "데이터 기반 관찰 목록"),
           ("종목 추천",               "종목 관찰 워치리스트"),
           ("확실한 상승",             "신호 강도: High (불확실성 포함)"),
           # v4 추가 4개
           ("손실 없음",               "리스크 시나리오 포함"),
           ("목표주가",                "참고 수준 벨류에이션"),
           ("무조건",                  "데이터 기반 판단"),
           (r"반드시 .{0,10}(오른다|상승한다|이익)", "긍정적 신호 감지 (불확실성 포함)"),
       ]
       ```
       Use regex-based find-and-replace. Log each substitution to `logs/compliance.log`.
       Raise `ComplianceViolationError` if prohibited pattern persists after substitution attempt.

    6. **run_m05.py**: Orchestrate M0.5 pipeline: config → normalizers → synthesize → compliance → telegram.
       Run M0.5 Done Gate validation (DG-01~DG-08) before Telegram send.

    7. Create `tests/test_m05_done_gate.py` implementing all 8 DG checks.

    8. **`independent` mode normalizer** (runtime_mode == "independent"):
       When both EnvScan and GlobalNews are absent, generate pseudo-UnifiedSignals from
       structured APIs only (no text parsing needed):
       ```python
       def normalize_fred_to_signal(fred_key: str, value: float, date: str) -> UnifiedSignal:
           """Convert FRED indicator to UnifiedSignal for independent mode."""
           return UnifiedSignal(
               id=f"fred-{fred_key[:8]}-{date}",
               title=FRED_SIGNAL_TITLES.get(fred_key, fred_key),
               summary=f"{fred_key}: {value:.2f} ({date})",
               source="fred",
               steeps_category=FRED_TO_STEEPS[fred_key],  # E for rates/CPI, T for tech indicators
               steeps_tags=[],
               psst_score=_fred_to_psst_score(fred_key, value),  # normalized 0-1
               signal_date=date,
               schema_version="investmeta-v1"
           )
       ```
       Use the EXACT 10 FRED series_id list below (PRD §0.5) — do NOT use partial names:
       ```python
       FRED_SERIES_IDS = [
           "DGS10",     # 미국 10년 국채수익률 → E (금리·통화정책 방향)
           "CPIAUCSL",  # 소비자물가지수 → E (인플레이션)
           "VIXCLS",    # VIX 공포지수 → E (시장 변동성)
           "UNRATE",    # 실업률 → S (고용 시장)
           "FEDFUNDS",  # 연방기금금리 → E (통화정책 현재 수준)
           "GDP",       # 미국 실질 GDP → E (경기 사이클)
           "DCOILWTICO",# WTI 원유 가격 → E (원자재·에너지)
           "DEXKOUS",   # 달러/원 환율 → E (한국 수출 경쟁력)
           "INDPRO",    # 산업생산지수 → E (제조업 경기)
           "UMCSENT",   # 미시간대 소비자심리지수 → S (소비 심리)
       ]
       FRED_TO_STEEPS = {
           "DGS10": SteepsCategory.E, "CPIAUCSL": SteepsCategory.E,
           "VIXCLS": SteepsCategory.E, "UNRATE": SteepsCategory.S,
           "FEDFUNDS": SteepsCategory.E, "GDP": SteepsCategory.E,
           "DCOILWTICO": SteepsCategory.E, "DEXKOUS": SteepsCategory.E,
           "INDPRO": SteepsCategory.E, "UMCSENT": SteepsCategory.S,
       }

       # Min-max normalization — per-series historical range (P7 정규화 알고리즘)
       FRED_HISTORICAL_RANGES = {
           "DGS10":      (0.5, 8.0),    # % — 2000~현재 역사적 범위
           "CPIAUCSL":   (250, 320),    # 지수값 — 2015~현재 절대 범위
           "VIXCLS":     (10.0, 80.0),  # 정상~위기 수준
           "UNRATE":     (3.0, 15.0),   # % — 저실업~위기 범위
           "FEDFUNDS":   (0.0, 8.0),    # % — 2000~현재 범위
           "GDP":        (18000, 30000),# 십억달러
           "DCOILWTICO": (20.0, 140.0), # 배럴당 달러
           "DEXKOUS":    (1000, 1500),  # 원/달러
           "INDPRO":     (90, 115),     # 2017=100 기준 지수
           "UMCSENT":    (50, 110),     # 소비자심리 지수
       }

       def _fred_to_psst_score(fred_key: str, value: float) -> float:
           """Min-max normalize FRED indicator → 0-1 psst_score.
           HIGH score = BULLISH condition. Bearish indicators (VIX, UNRATE) are inverted."""
           lo, hi = FRED_HISTORICAL_RANGES.get(fred_key, (0, 100))
           normalized = max(0.0, min(1.0, (value - lo) / (hi - lo)))
           # Invert: high VIX/UNRATE = bearish = low psst_score
           return (1.0 - normalized) if fred_key in ("VIXCLS", "UNRATE") else normalized
       ```
       Minimum viable (FRED API 부분 장애 시): DGS10, CPIAUCSL, VIXCLS, UNRATE, FEDFUNDS.
       This ensures independent mode produces ≥ 5 UnifiedSignals for synthesize_macro.

       ⚠️ **independent 모드 품질 경고**: FRED 지표는 미국 시장 신호만을 나타냅니다.
       한국 개별 종목 분석에 직접 적용 시 신뢰도가 크게 제한됩니다.
       independent 모드에서 생성된 리포트는 `delivery_mode = "with_warning"` **강제 적용**
       (validate_report_quality.py에 구현 — 아래 Step 12 참조).
       리포트 상단 고정 경고문:
       ```
       ⚠️ 이번 리포트는 미국 매크로 데이터(FRED 10개 지표)만을 기반으로 생성되었습니다.
       EnvironmentScan 신호가 없어 한국 시장 분석의 신뢰도가 제한됩니다.
       EnvironmentScan 실행 후 /weekly-report를 다시 실행하시면 더 정확한 분석이 제공됩니다.
       ```

    Reference: PRD §6, workflow-idea.md 아이디어 2, 9, 핵심수정 4
- **Output**: `config.py` + `normalizers.py` + `synthesize_macro.py` + `telegram_notifier.py` + `compliance_filter.py` + `run_m05.py` + `tests/test_m05_done_gate.py`
- **Review**: `@reviewer` — M0.5 코드 품질 + DG-07 (sentiment_weight==0.0) 특별 검증
- **Translation**: `none`
- **Post-processing**: |
    테스트 통과 후: state.yaml `milestones.m05.dg_01_to_08_passed: true` 업데이트.
    **최초 1회**: `state.yaml system.installed_at`에 현재 ISO 8601 타임스탬프 기록
    (watchdog.py의 weeks_since_install 계산 기준점 — 이후 수정 불가).
    실패 항목은 state.yaml `errors` 배열에 기록 후 CCP Step 1→2→3 재진단.

---

### Step 8: (human) HITL-2 — Telegram 수신 확인 + M1 전환 결정

- **Action**: |
    **[Claude Code 안내]**

    1. `python3 run_m05.py --input [실제 경로]` 실행 지시 (Telegram 실제 발송)
    2. 사용자의 Telegram 수신 확인 대기
    3. 수신 확인 후 M1 전환 방식 선택 안내:

    **[A] 지금 M1 구현 계속 진행**
       → 바로 Step 9부터 M1 구현 시작

    **[B] 2주간 M0.5로 먼저 사용해보기 (권장)**
       → state.yaml `hitl_2.choice: "pause_2weeks"` + `hitl_2.choice_date: [오늘날짜]` 기록
       → 14일 후 watchdog.py가 "M1 재개 준비됐습니다" Telegram 알림 발송
       → 사용자 확인 후 Step 9부터 재개

    **M1 비용 고지** (사전 동의 필수):
    M1에서 Anthropic API 직접 호출 시 추가 비용 발생:
    - claude-opus-4-6: ~$0.06~0.15/회, ~$1~3/월 (입력 ~8K + 출력 ~4K 토큰)
    - M0.5(Claude Max 포함)는 추가 비용 없음

    **Telegram 수신 실패 시**: PRD §6.4a 실패 복구 프로토콜 참조하여 진단 안내
- **Command**: `/hitl-2-m1-decision`
- **Autopilot Default**: [B] 2주 M0.5 사용 후 M1 전환

---

### Step 9: GlobalNews Integration — dedup + steeps_classifier + signal_bridge

- **Pre-processing**: |
    If `discovered_paths.gnews_signals` is empty or file does not exist:
    - Set `discovered_schema.gnews.file_exists: false` in state.yaml
    - Skip this step's GlobalNews parsing — proceed with EnvScan-only mode
    - Log: "GlobalNews skipped — envscan_only mode"
    Otherwise proceed with parquet loading.
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`dedup.py`** (~150 LOC): content-hash 기반 중복 제거. 동일 content_hash 신호 중 최신 1개만 유지.
  - [ ] **`steeps_classifier.py`** (~200 LOC): `SteepsCategory` StrEnum 6가지 분류 정확성. `s`(소문자) 구분 보장.
  - [ ] **`signal_bridge.py`** (~200 LOC): STEEPs **6가지** → GICS 섹터 매핑 테이블 포함 (T/E/P/S/E_env/s 모두 매핑). `config/sector_stock_map.yaml` 참조.
  - [ ] `signal_bridge.py` — `E_env` 신호가 친환경에너지·소재 섹터로 라우팅됨 (환경규제 신호 누락 없음)
  - [ ] `signal_bridge.py` — `s` 신호가 방산·바이오·금융 섹터로 라우팅됨 (법적 리스크 신호 누락 없음)
  - [ ] **`normalizers.py` 확장**: GlobalNews `signals.parquet` → `UnifiedSignal` 변환 추가 (Parquet 로딩, confidence 0-1 정규화)
  - [ ] GlobalNews 없을 때 graceful skip 동작 확인 (`gnews_signals: ""` 상태에서 파이프라인 계속 진행)
  - [ ] `steeps_tags` 다중 레이블 처리: 분할 가중치 `1/len(tags)` 적용 검증
  - [ ] dedup hash에 `source` 포함 확인 — EnvScan과 GlobalNews 동일 이슈 신호가 각각 보존됨
  - [ ] 통합 파이프라인 테스트: WF1 + GlobalNews → `UnifiedSignal` 리스트 → dedup → classify → bridge → `InvestmentMeta` 흐름 성공 (source: Step 7 normalizers 기반 확장)
- **Task**: |
    Implement GlobalNews integration layer with signal deduplication, STEEPs classification,
    and sector bridging.

    1. **Extend normalizers.py** to support GlobalNews `signals.parquet`:
       - Load with pyarrow: `pa.parquet.read_table(path).to_pandas()`
       - Map `confidence` field (0-1 scale) → `psst_score`
       - Assign `source: "gnews"` in each UnifiedSignal

    2. **dedup.py**: Remove duplicate signals across sources using content-hash:
       ```python
       def compute_content_hash(signal: UnifiedSignal) -> str:
           # source 포함: 동일 제목·날짜라도 출처(envscan vs gnews)가 다르면 독립 신호로 보존
           content = f"{signal.source}:{signal.title}:{signal.signal_date}"
           return hashlib.md5(content.encode()).hexdigest()[:12]
       ```
       Keep newest signal when hash collision detected. Log dedup count.
       RATIONALE: `source` 포함으로 EnvScan vs GlobalNews 동일 이슈의 다관점 신호가 보존됨.
       hash 길이 12 hex chars (48 bits) — 주당 1000+ 신호에서도 충돌 확률 무시 가능 수준.

    3. **steeps_classifier.py**: Rule-based STEEPs classification for signals with
       ambiguous or missing category. Priority order: explicit field > keyword rules.
       Handle `s` (lowercase security/legal) vs `S` (society) with explicit str comparison.
       Implement `steeps_tags` multi-label: if signal matches multiple categories,
       populate `steeps_tags` list; apply split weight `1/len(tags)` in synthesis.

    4. **signal_bridge.py**: Map ALL 6 STEEPs categories → GICS Korean market sectors:
       - T → 반도체, IT서비스, 통신
       - E → 금융, 에너지, 산업재
       - P → 방산, 규제관련
       - S → 소비재, 헬스케어
       - E_env → 친환경에너지, 소재, 산업재 (환경규제·탄소 신호 — 섹터 방향에 중요)
       - s → 방산, 바이오(규제), 금융(컴플라이언스) (보안·법적 리스크 신호)
       - CRITICAL: `E_env`와 `s` 누락 시 환경규제 이슈·법적 리스크가 섹터 분석에 반영되지 않음
       - Load extended mapping from `config/sector_stock_map.yaml`

    5. Update `synthesize_macro.py` to consume merged signal list (WF1 + GlobalNews).

    Reference: PRD §7.3, §7.4, §8.1, §8.2, workflow-idea.md 아이디어 4
- **Output**: `dedup.py` + `steeps_classifier.py` + `signal_bridge.py` + `normalizers.py` (확장) + 통합 테스트 통과
- **Review**: `none`
- **Translation**: `none`
- **Post-processing**: state.yaml `milestones.m1.phase_2_done: true` 업데이트

---

### Step 10: Korea Signal Layer + Stock Selector

- **Pre-processing**: `InvestmentMeta` 출력 (Step 9 결과) 로드 — synthesize_macro.py 결과가 있어야 종목 선정 가능
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`korea_signal_layer.py`** (~150 LOC): FDR에서 외국인 수급 + 환율 조회 성공. 장애 시 graceful skip (글로벌 신호만 사용).
  - [ ] **`stock_selector.py`** (~150 LOC): Category A (Bullish + confidence≥0.65 섹터의 외국인 수급 Top 5) + Category B (테마 신호 상위 3개 수혜 종목) 자동 선정 로직 구현.
  - [ ] `stock_selector.py` — `watchlist_override` 파라미터 지원 (HITL-1 수동 종목 우선 삽입)
  - [ ] Category A 최대 5종목, Category B 최대 3종목 — 초과 종목은 `data/watchlist_candidates.jsonl`에 저장됨
  - [ ] FDR 장애 시: 외국인 수급 없이 신호 점수 순위로 대체 (graceful fallback)
  - [ ] state.yaml `stock_selection` 섹션 업데이트됨 — category_a, category_b, selected_at, manual_override 포함
  - [ ] 종목 선정 결과가 `InvestmentMeta`에 포함되어 다음 단계 입력으로 사용 가능 (source: Step 9 InvestmentMeta)
- **Task**: |
    Implement Korea signal layer (domestic market data) and automatic stock selector.

    1. **korea_signal_layer.py**: Fetch Korean market signals:
       - Foreign flow: `fdr.DataReader('KRX/ETF', start=four_weeks_ago)` — KOSPI200 + KOSDAQ150
       - USD/KRW, JPY/KRW rates: `fdr.DataReader('USD/KRW', start=two_weeks_ago)`
       - Policy signals: filter EnvironmentScan `P` + `s` categories from database.json
       - ALL network calls wrapped in try/except → graceful skip on failure, log to state.yaml errors

    2. **stock_selector.py**: Implement automatic stock selection:
       ```python
       def select_stocks(investment_meta, watchlist_override=None):
           bullish_sectors = [s for s in investment_meta.sectors
                              if s.direction == "Bullish" and s.confidence >= 0.65]
           cat_a = _get_top_foreign_flow_tickers(bullish_sectors, top_n=5)
           cat_b = _get_theme_tickers(investment_meta.top_signals, exclude=cat_a, top_n=3)
           if watchlist_override:
               cat_a = watchlist_override[:5] + [t for t in cat_a
                       if t not in watchlist_override][:max(0, 5-len(watchlist_override))]
           return cat_a[:5], cat_b[:3]
       ```
       Save overflow candidates to `data/watchlist_candidates.jsonl`.
       FDR fallback: if FDR unavailable, rank by signal psst_score instead.

    3. Category B "emerging theme" detection algorithm in `steeps_classifier.py`:
       - Identify topics where current_week_count >= avg_4week_count * 2.0
       - Theme confidence = min(current_week_count / (avg_4week_count * 3.0), 1.0)
       - Include in Category B if theme_confidence >= 0.55
       - Auto-remove after 4 consecutive weeks below 0.55 threshold

    4. Update state.yaml `stock_selection` section with results.

    Reference: PRD §7.6, §7.10, workflow-idea.md 핵심수정 9, 아이디어 2
- **Output**: `korea_signal_layer.py` + `stock_selector.py` + state.yaml 업데이트
- **Review**: `none`
- **Translation**: `none`
- **Post-processing**: state.yaml `milestones.m1.phase_3_done: true` 업데이트

---

### Step 11: Intelligence Engine — 종목 수치 분석 + 원고 생성

- **Checkpoint Pattern**: `dense` (예상 12~18턴 — DART/pykrx/FRED 3개 API + 2개 카테고리 원고 생성 + NarrativeOutput 검증)
- **Pre-processing**: |
    Load context from state.yaml:
    - `stock_selection.category_a` + `category_b` (from Step 10)
    - `discovered_schema.envscan_wf1` (for DART field mapping)
    Run: `python3 -c "from synthesize_macro import load_investment_meta; m=load_investment_meta(); print(len(m.sectors), 'sectors loaded')"` — Must succeed.
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`synthesize_stock.py`** (~200 LOC): `DartFinancials` (revenue_yoy, op_income_yoy) + `ValuationContext` (per, pbr, roe, sector_avg_per) 생성. 각 API 장애 시 graceful skip 동작 확인.
  - [ ] **`valuation_comparator.py`** (~120 LOC): 섹터 평균 PER 계산 + per_discount_pct 생성
  - [ ] **`intelligence_engine.py`** (~150 LOC): `StockAnalysisContext` → `NarrativeOutput` JSON 생성. Category A/B 프롬프트 분리 적용.
  - [ ] `NarrativeOutput` 구조 검증: `sector_narrative`, `causal_chains` (≥1개), `stock_analyses`, `category_b_analyses`, `bear_case` 필드 모두 존재
  - [ ] M0.5 모드: `intelligence_engine.py`가 `output/temp/context_[날짜].json`을 읽고 원고 생성 (Claude Code 인터랙티브 세션 방식)
  - [ ] fallback 동작 확인: narrative 파일 없을 시 v1 템플릿(수치만 표) 생성 + Telegram 경고 발송
  - [ ] `output/temp/narrative_[날짜].json` 파일 크기 ≥ 1000 bytes (빈 파일 방지 — Anti-Skip Guard)
- **Task**: |
    Implement stock data synthesis and intelligence engine for report narrative generation.

    1. **synthesize_stock.py**: Fetch financial data for selected tickers:
       - **DART OpenAPI** (dart-fss library) — 핵심 호출 흐름 (P6):
         ```python
         import dart_fss as dart, keyring
         dart.set_api_key(keyring.get_password("investscan", "dart_api_key"))
         corp_list = dart.get_corp_list()
         corp = corp_list.find_by_stock_code(ticker)[0]  # corp_code 자동 조회
         fs = corp.extract_fs(bgn_de="20240101")         # 최근 4분기 재무제표

         # 분기 자동 결정 (P13 — 공시 지연 45일 고려):
         year, quarter = _determine_latest_available_quarter()
         # 공시 분기 판정 규칙:
         #   Q1(Mar31 종료) → ~May15 공시 → 5월 15일 이후 사용 가능
         #   Q2(Jun30 종료) → ~Aug14 공시
         #   Q3(Sep30 종료) → ~Nov14 공시
         #   Q4(Dec31 종료) → ~Feb14(다음해) 공시
         revenue_yoy = _calc_yoy(fs, "매출액", year, quarter)
         op_income_yoy = _calc_yoy(fs, "영업이익", year, quarter)
         dart_financials = DartFinancials(
             ticker=ticker, quarter=f"{year}Q{quarter}",
             revenue_yoy=revenue_yoy, op_income_yoy=op_income_yoy,
             data_freshness_note=f"{year}Q{quarter} 기준 (DART 공시 기준 최신 분기)"
         )
         ```
         API 키 없음/만료/서버 오류: graceful skip → FAILURE_GUIDE["DART_API_ERROR"] 발송.
         공시 미완료 분기 조회 시: `revenue_yoy = None` + `data_freshness_note = "분기보고서 공시 전"`.

       - **pykrx**: PER, PBR, ROE for each ticker and sector averages
       - **FRED API**: 10개 series_id (Step 7 FRED_SERIES_IDS 목록) — US macro context
       - ALL wrapped in try/except → graceful skip on failure (partial data is better than no data)
       - Output: `ContextContract` (아래 #4 참조) saved to `output/context/context_[date].json`

    2. **valuation_comparator.py**: Compute sector average PER from pykrx data (P8 명세 추가).
       ```python
       # pykrx 섹터 평균 PER 계산 방법:
       # 1. 섹터 분류: sector_stock_map.yaml의 종목 목록 사용 (WICS 기준 3개 대표 종목)
       # 2. 호출: pykrx.stock.get_market_fundamental_by_ticker(date, market="KOSPI")
       #    KOSDAQ 종목은 market="KOSDAQ"으로 별도 호출
       # 3. 평균: 단순 산술평균 (적자 종목 PER < 0 또는 이상값 > 200은 제외)
       # 4. fallback: pykrx 장애 시 sector_avg_per = None → ValuationContext.per_discount_pct = None
       ```
       Calculate `per_discount_pct = (per - sector_avg_per) / sector_avg_per * 100`.
       Return empty ValuationComparison list if pykrx unavailable (graceful).

    3. **intelligence_engine.py** — M0.5 vs M1 실행 모델 (P5 명확화):

       ⚠️ **M0.5 실행 모델**: `intelligence_engine.py`는 M0.5에서 독립 실행 Python 모듈이 아닙니다.
       `/weekly-report` 슬래시 커맨드가 Claude Code 자신(LLM)에게 컨텍스트를 준비·전달하여
       Claude Code가 직접 NarrativeOutput을 생성합니다. Anthropic API 별도 호출 없음.

       ```
       [M0.5 실행 흐름]
       사용자: /weekly-report 실행
       → intelligence_engine.load_context(date): output/context/context_[date].json 로드 + 검증
       → intelligence_engine.build_prompt(context): CATEGORY_A/B_SYSTEM_PROMPT + context_data 조합
       → Claude Code (LLM 내부): NarrativeOutput 추론 및 생성 (Python 코드가 아닌 LLM 자체)
       → intelligence_engine.save_narrative(result): output/temp/narrative_[date].json 저장

       [M1 실행 흐름 — launchd headless]
       weekly_orchestrator.py --mode full-auto
       → intelligence_engine.generate_narrative_via_api(context): Anthropic API 직접 호출
         (claude-opus-4-6, temperature=0.3, system=CATEGORY_A/B_SYSTEM_PROMPT)
       → intelligence_engine.save_narrative(result): 동일 경로 저장
       ```

       **M0.5 Python 모듈 (~150 LOC) 구현 범위**:
       - `load_context(date: str) -> ContextContract`: JSON 로드 + schema_version 검증
       - `build_prompt(context: ContextContract) -> dict`: system_prompt + user_message 딕셔너리 반환
       - `save_narrative(narrative: dict, date: str)`: output/temp/narrative_[date].json 저장
       - `generate_narrative_via_api(context: ContextContract) -> dict`: M1 전용 Anthropic API 호출
       - FALLBACK: narrative 파일 없음/손상 → v1 템플릿(수치 표만) 생성 + Telegram 경고

    4. Create `output/context/context_[date].json` as **Stage 1 output contract** (P4 — 스키마 정의):
       이 파일은 Stage 1(launchd headless)이 생성하고 Stage 2(Claude Code interactive / M1 API)가 소비하는
       **핵심 인터페이스 파일**입니다. 스키마 불일치 시 Stage 2 실패.

       ```python
       # ContextContract — Stage 1 → Stage 2 계약 파일 스키마 (완전 정의)
       @dataclass
       class ContextContract:
           report_date: str          # ISO date "YYYY-MM-DD"
           runtime_mode: str         # "full" | "envscan_only" | "independent"
           meta: dict                # InvestmentMeta 직렬화 (sectors, macro_summary, action_item, action_checklist)
           cat_a_contexts: list      # List[StockAnalysisContext] — Category A 종목 (DART+pykrx+FRED 데이터 포함)
           cat_b_contexts: list      # List[StockAnalysisContext] — Category B 종목
           stock_contexts: list      # cat_a + cat_b 합쳐진 목록 (_verify_metrics_consistency 입력)
           signals_summary: list     # 상위 5개 UnifiedSignal 요약 (id, title, psst_score, steeps_category)
           fred_snapshot: dict       # {series_id: {"value": float, "date": str}} — 10개 FRED 지표
           created_at: str           # ISO datetime — /weekly-report 신선도 체크용
           schema_version: str       # "context-v1" — 버전 불일치 시 경고 출력
       ```
       저장: `output/context/context_{date}.json` (date = YYYY-MM-DD).
       저장 전 검증: `cat_a_contexts` 또는 `cat_b_contexts` 비어있으면 Telegram 경고 발송 + 계속 진행.

    5. **KS-2 weekly feedback** (Telegram 단방향 아키텍처 적용):
       ⚠️ Telegram은 단방향 채널 — 응답 수신 불가. 피드백 수집은 Claude Code 세션에서 처리.

       Telegram으로는 **안내 메시지만** 발송 (응답 요청 없음):
       ```
       "📋 리포트 생성 완료! Claude Code에서 /weekly-report를 완료하셨으면,
        만족도를 Claude Code 채팅에 알려주세요 (예: '이번 리포트 4점')."
       ```
       실제 피드백 수집: HITL-3 체크리스트 완료 후 Claude Code가 만족도 질문:
       "이번 리포트 만족도를 1~5점으로 말씀해주세요." → `accuracy_tracker.record_ks2(rating)` 기록.
       KS-2 trigger: if 4-week average < 2.5 → watchdog가 Telegram으로 경고 발송 (단방향 알림).
       **권장안**: KS-2 피드백 = Claude Code 대화로 수집, Telegram = 수집 안내만 (단방향).

    Reference: PRD §7.6, §7.11, §4.2, workflow-idea.md 핵심수정 2, 5, 15, 아이디어 2
- **Output**: `synthesize_stock.py` + `valuation_comparator.py` + `intelligence_engine.py` (완성) + `output/context/context_[날짜].json` (Stage 1 계약 파일)
- **Review**: `@reviewer` — intelligence_engine 프롬프트 컴플라이언스 + NarrativeOutput 스키마 일치성
- **Translation**: `none`
- **Post-processing**: state.yaml `milestones.m1.phase_4_intelligence_done: true` 업데이트

---

### Step 12: Report Generator + Quality Validation + Monitoring

- **Pre-processing**: |
    Verify narrative file exists and is valid:
    ```python
    status = check_narrative_output(Path(f"output/temp/narrative_{date}.json"))
    assert status == "ok", f"Narrative not ready: {status}"
    ```
    Load `output/completion-definition.md` (from Step 4) as quality baseline reference.
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`report_generator.py`** (~200 LOC): Jinja2 템플릿(`templates/weekly-report.md.j2`)으로 10개 섹션 고정 순서 리포트 생성됨 (PRD §7.8)
  - [ ] **`validate_report_quality.py`** (~120 LOC): 8항목 검증 + PRD 감산 모델 구현. `delivery_mode` 3단계 분기: `normal` / `with_warning` / `reloop`
  - [ ] **`accuracy_tracker.py`** (~200 LOC): `PredictionRecord` 저장 + 벤치마크 ETF 4개 (KODEX 반도체 091160, IT 098560, 헬스케어 266410, 2차전지 305720) + Naive Baseline + 월간 리포트 형식
  - [ ] **`watchdog.py`** (~120 LOC): 월요일 08:00 강제 알림 + 지연 감지(8일 이상 미실행) + `FAILURE_GUIDE` 한국어 평문 7개 에러 유형 매핑
  - [ ] 생성된 리포트 파일 `output/reports/YYYY-WW.md` 크기 ≥ 2000 bytes
  - [ ] `onboarding_mode: true` 시 전문 용어에 괄호 설명이 삽입됨
  - [ ] Bear Case 섹션이 리포트에 존재하고 신호 ID를 포함함 (source: Step 11 NarrativeOutput.bear_case)
  - [ ] 면책 조항이 `publish_platform` 값에 따라 조건부 분기됨 (personal vs blog)
- **Task**: |
    Implement report generation, 8-item quality validation, accuracy tracking, and watchdog.

    1. **report_generator.py**: Assemble final report using Jinja2:
       - Load `templates/weekly-report.md.j2` (create template with 10-section fixed order per PRD §7.8)
       - Map NarrativeOutput JSON keys → Jinja2 variables (per workflow-idea.md 핵심수정 6 mapping table)
       - Apply onboarding_mode: insert term explanations when `onboarding_mode: true`
       - Apply conditional disclaimer based on `publish_platform`:
         * "personal": short disclaimer
         * "blog" / "external": 「자본시장법」 full disclaimer + non-expert advisory warning
       - Save to `output/reports/[YYYY]-W[WW].md` (ISO week number)

    2. **validate_report_quality.py**: Implement 8-item PRD quality gate:
       ```python
       checks = {
           "independent_signals_3plus":  _count_sources(report_md) >= 3,
           "each_signal_has_source":      _all_have_source(report_md),
           "downside_risk_exists":        bool(re.search(r'하방 리스크|리스크|Bear Case', report_md)),
           "timeframe_stated":            bool(re.search(r'4.{0,3}12주|4주|12주', report_md)),
           "action_item_exists":          "이번 주 행동" in report_md,
           "causal_chain_exists":         _has_causal_chain(narrative_json),
           "bear_case_exists":            bool(narrative_json.get("bear_case", "")),
           "key_metrics_consistent":      _verify_metrics_consistency(report_md, context_data),
       }
       # PRD model: -5% confidence per failed item (NOT binary pass/fail)
       confidence_penalty = sum(1 for v in checks.values() if not v) * 0.05
       delivery_mode = "normal" if score >= 7/8 else ("with_warning" if score >= 5/8 else "reloop")

       # P8: independent 모드 강제 downgrade
       if context_data.get("runtime_mode") == "independent":
           # FRED 5개 지표만 기반 분석 — 신뢰도 제한 강제 표시
           delivery_mode = "with_warning"  # normal도 with_warning으로 강제
           # 리포트 상단에 고정 경고문 삽입 (report_generator.py가 처리)
           context_data["independent_mode_warning"] = True
       ```
       Include `_verify_metrics_consistency()`: sample 3 stocks, check PER within ±20% of context_data.

    3. **accuracy_tracker.py**: Record PredictionRecord per sector per week.
       4 weeks later: fetch actual ETF returns via FDR, evaluate hit (Bullish = actual ≥ +2%).
       Monthly report: accuracy by sector + Naive Baseline comparison + weight adjustment suggestions.
       Use the EXACT Telegram monthly report format below:
       ```
       📈 InvestScan 월간 정확도 리포트 ({YYYY}년 {M}월)
       ───────────────────────────────────
       반도체: {n}/{total} 예측 적중 ({pct}%) | Always-Bullish: {baseline}%
       IT서비스: {n}/{total} ({pct}%) | Always-Bullish: {baseline}%
       바이오: {n}/{total} ({pct}%) | Always-Bullish: {baseline}%
       ───────────────────────────────────
       전체 적중률: {overall}% | Always-Bullish 대비: {diff:+.0f}%
       ⚠️ {lowest_sector} 섹터 신호 품질 재검토 권장
       가중치 조정이 필요하면 Claude Code에서 '가중치 조정해줘'라고 말씀해주세요.
       ```
       > 참고: Telegram은 단방향 채널입니다. [Y/N] 응답은 수신되지 않습니다.

    4. **watchdog.py**:
       - Monday 08:00 forced Telegram alert (report present = SUCCESS_MSG, absent = FAILURE_MSG)
       - **즉시 감지 (P10)**: 일요일 Stage 1 미실행 → 월요일 08:00에 즉각 경고 (8일 대기 없음):
         ```python
         def monday_morning_check(state: dict):
             last_run_file = Path("logs/last_successful_run.txt")
             if not last_run_file.exists():
                 send_telegram(FAILURE_GUIDE["NETWORK_ERROR"]); return
             last_run = datetime.fromisoformat(last_run_file.read_text().strip())
             # 지난 일요일 날짜 계산
             today = datetime.now()
             last_sunday = today - timedelta(days=today.weekday() + 1)
             if last_run.date() < last_sunday.date():
                 # Stage 1이 이번 주 일요일에 실행되지 않음 → 즉시 경고
                 send_telegram(
                     f"⚠️ 이번 주 데이터 수집이 실행되지 않았습니다.\n"
                     f"마지막 수집: {last_run.strftime('%Y-%m-%d')}\n"
                     f"확인: 일요일 20:00에 MacBook이 켜져 있었나요?\n"
                     f"수동 실행: python3 ~/investscan/weekly_orchestrator.py --mode data-only\n"
                     f"그 후 Claude Code에서 /weekly-report를 실행하세요."
                 )
             elif last_run.date() >= last_sunday.date():
                 send_telegram(SUCCESS_MSG.format(...))  # 정상 수집 완료
         ```
       - Stale detection: if days_since_last_run >= 8 (위 즉시 감지가 선행되므로 2차 안전망)
       - Implement EXACT SUCCESS_MSG and FAILURE_GUIDE below — do NOT summarize or simplify:
       ```python
       SUCCESS_MSG = """✅ InvestScan 데이터 수집 완료
       ──────────────────────────────
       수집 완료: {data_date} {data_time}
       선정 종목: A등급 {cat_a_count}개, B등급 {cat_b_count}개
       분석 섹터: {sector_summary}
       ──────────────────────────────
       📌 Claude Code를 열고 /weekly-report를 실행하세요. (약 10분 소요)"""

       FAILURE_GUIDE = {
           "DART_API_ERROR":   "주식 실적 데이터 수집에 실패했습니다. 이번 주는 수익성 수치 없이 리포트가 생성됩니다.",
           "PYKRX_ERROR":      "주가 데이터 수집에 실패했습니다. 다음 주에 자동으로 다시 시도합니다.",
           "ENVSCAN_STALE":    "분석 신호 데이터가 3일 이상 오래됩니다. EnvironmentScan을 먼저 실행해주세요.",
           "DISK_SPACE":       "저장 공간이 부족합니다. 오래된 리포트(~/investscan/output/reports/) 몇 개를 삭제해주세요.",
           "NETWORK_ERROR":    "인터넷 연결이 불안정했습니다. 연결 확인 후 Claude Code에서 /weekly-report를 실행하세요.",
           "GNEWS_MISSING":    "글로벌 뉴스 파일이 없습니다. 국내 데이터만으로 분석이 진행됩니다.",
           "FRED_API_ERROR":   "미국 경제 지표 수집에 실패했습니다. 이번 주는 국내 데이터만으로 분석합니다.",
       }
       ```

    5. Create `templates/weekly-report.md.j2` implementing all 10 fixed sections.
       Include the following Jinja2 variables (complete list — do NOT omit any):
       | Jinja2 변수 | 소스 | 설명 |
       |------------|------|------|
       | `sector_narrative` | NarrativeOutput.sector_narrative | 섹터 상세 분석 본문 |
       | `causal_chains` | NarrativeOutput.causal_chains | 인과 논리 체인 (from→via→to) |
       | `bear_case` | NarrativeOutput.bear_case | 하방 시나리오 |
       | `category_a_stocks` | NarrativeOutput.stock_analyses | Category A 종목 분석 |
       | `category_b_stocks` | NarrativeOutput.category_b_analyses | Category B 테마주 분석 |
       | `sectors` | InvestmentMeta.sectors | 섹터 방향 요약 (direction + confidence) |
       | `action_item` | synthesize_macro (규칙 기반) | "이번 주 행동 1가지" 단일 문장 |
       | `action_checklist` | synthesize_macro (규칙 기반) | "이번 주 행동 체크리스트" 복수 항목 리스트 |
       | `all_bullish_3weeks` | weekly_orchestrator 플래그 | 3주 연속 전섹터 Bullish 경고 배너 |
       | `publish_platform` | investscan.yaml | 면책 조항 조건부 분기 ("personal" vs "blog") |
       | `onboarding_mode` | investscan.yaml | 용어 괄호 설명 삽입 여부 |
       | `data_source_note` | 고정 텍스트 | **M1 글로벌 지표 한계 고지 (필수)** |
       | `independent_mode_warning` | validate_report_quality.py | independent 모드 경고 배너 (True일 때만 표시) |

       `data_source_note` 고정 텍스트 (EXACT — 수정 금지):
       ```
       ※ 분석 주석: 유럽(ECB)·중국(PMI)·일본(BOJ) 정량 경제 지표는 본 시스템에 직접 수집되지 않습니다.
       해당 지역 매크로 흐름은 EnvironmentScan 뉴스 신호에서 추론된 것으로,
       '뉴스 기반 추론'이지 '정량 데이터 기반 분석'이 아님을 참고하시기 바랍니다.
       ```

    Reference: PRD §7.8, §7.9, 핵심목적 7항목, workflow-idea.md 핵심수정 6, 11, 12, 13, 아이디어 5
- **Output**: `report_generator.py` + `validate_report_quality.py` + `accuracy_tracker.py` + `watchdog.py` + `templates/weekly-report.md.j2` + `output/reports/[첫 리포트].md`
- **Review**: `@reviewer` + `@fact-checker` — 리포트 품질(8항목) + 수치 정합성 + 컴플라이언스 최종 확인
- **Translation**: `none`
- **Post-processing**: |
    validate_report_quality.py 결과 확인:
    - `delivery_mode: "normal"` or `"with_warning"` → HITL-3 진행
    - `delivery_mode: "reloop"` → Step 12-R (Prompt Refinement) 진입
    state.yaml `milestones.m1.validate_8_passed` 업데이트

---

### Step 12-R: (조건부) Prompt Refinement — 재조정 루프

> **실행 조건**: `validate_report_quality.py` 결과 `delivery_mode: "reloop"` (5/8 미만) 또는 HITL-3 체크리스트 3개 미만 통과 시만 실행. 최대 2회 제한.

- **Pre-processing**: validate_report_quality.py 결과에서 실패 항목 목록 추출 + HITL-3 피드백(있는 경우) 로드
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] `state.yaml workflow.refinement_count` ≤ 2 (3회 초과 시 Claude Code가 사용자와 개선 세션 직접 진행)
  - [ ] 실패 항목별 프롬프트 수정 근거가 기록됨 (`autopilot-logs/refinement-[N].md`)
  - [ ] 재실행 후 `validate_report_quality.py` 결과가 이전보다 개선됨
  - [ ] `delivery_mode`가 `"normal"` 또는 `"with_warning"`으로 변경됨
- **Task**: |
    Diagnose quality failures and refine Category A/B prompts or data context, then regenerate report.

    1. Identify root cause of each failed quality check:
       - `independent_signals_3plus` FAIL → add signal source diversity instruction to prompts
       - `causal_chain_exists` FAIL → strengthen causal chain requirement in A/B prompts
       - `bear_case_exists` FAIL → add explicit bear case generation to prompts
       - `key_metrics_consistent` FAIL → check if context_data metrics are correctly formatted

    2. Record refinement decision in `autopilot-logs/refinement-[N].md`
    3. Adjust CATEGORY_A/B_SYSTEM_PROMPT constants in intelligence_engine.py
    4. Re-run intelligence_engine.py → validate_report_quality.py
    5. Increment state.yaml `workflow.refinement_count`
    6. If refinement_count >= 2 and still failing — **권장안 적용: 자동 에스컬레이션**:
       a. Save failure report to `autopilot-logs/refinement-escalation.md`:
          - Failed quality checks (which of the 8 items)
          - Both refinement attempts and what was changed
          - Suggested manual fix direction
       b. Send Telegram message:
          "⚠️ 리포트 품질 자동 개선이 2회 시도 후 기준 미달입니다.
           Claude Code에서 'InvestScan 리포트 품질 점검해줘'라고 말씀해주세요.
           파일: autopilot-logs/refinement-escalation.md"
       c. Proceed with v1 fallback template (data table only) for this week's report.
          Do NOT block the pipeline — partial report is better than no report.

    Reference: workflow-idea.md 핵심수정 8, PRD §핵심목적
- **Output**: 수정된 `intelligence_engine.py` (프롬프트 상수) + 새 `narrative_[날짜].json` + 새 리포트 + `autopilot-logs/refinement-[N].md`
- **Review**: `none` (신속 재처리 우선)
- **Translation**: `none`
- **Post-processing**: state.yaml `hitl_3.refinement_triggered: true` 기록

---

### Step 13: (human) HITL-3 — 완성본 체크리스트 검수

- **Action**: |
    **[완성본 검수 체크리스트]**

    아래 5가지를 확인해주세요:

    [ ] 1. 내가 관심 있는 섹터(반도체/IT 등)가 포함되어 있나요?
    [ ] 2. "이번 주 행동" 항목이 명확하게 나와 있나요?
    [ ] 3. 각 종목에 위험(리스크) 설명이 있나요?
    [ ] 4. 숫자들이 대략 맞아 보이나요? (크게 이상한 수치가 없나요?)
    [ ] 5. 전반적으로 읽기 편하게 작성되었나요?

    → **4개 이상 "예"**: 정상 발송 ✅ → Step 14(Automation) 진행
    → **3개 이하 "예"**: 가장 어색한 부분을 말씀해주세요 → Step 12-R 재개선

    **리포트 파일 위치**: `output/reports/[날짜].md` — Finder에서 확인 가능
- **Command**: `/hitl-3-report-review`
- **Autopilot Default**: 4개 이상 체크 시 자동 승인

---

### Step 14: Automation — launchd + weekly_orchestrator + health_dashboard

- **Pre-processing**: HITL-3 통과 확인. state.yaml `hitl_3.passed: true` 검증 후 진행.
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] **`weekly_orchestrator.py`** (~250 LOC): `--mode data-only` (Stage 1) + `--mode full-auto` (M1) 두 모드 구현
  - [ ] **launchd plist 파일** 생성됨: `~/Library/LaunchAgents/com.investscan.weekly.plist`
  - [ ] launchd plist: `StartCalendarInterval` 일요일 20:00 설정, API 키는 plist 평문 저장 금지 (Keychain 동적 로드)
  - [ ] `launchctl load [plist]` 실행 성공 + `launchctl list | grep investscan` 확인
  - [ ] `weekly_orchestrator.py --mode data-only --dry-run` 성공 (실제 발송 없이 파이프라인 검증)
  - [ ] **`health_dashboard.py`** (~80 LOC): `output/dashboard/weekly_dashboard.html` 생성 (5가지 필수 표시: 마지막 실행 시각, 섹터 방향, 신뢰도, 데이터 신선도, 오류 로그)
  - [ ] **`personalizer.py`** (~150 LOC): Keychain 읽기·쓰기 + 섹터/플랫폼 설정 변경 대화형 인터페이스
  - [ ] `logs/last_successful_run.txt` 파일 생성됨 (watchdog.py 지연 감지용)
- **Task**: |
    Implement complete automation pipeline: weekly_orchestrator, launchd, health dashboard, personalizer.

    1. **weekly_orchestrator.py**: Pipeline controller for both modes:
       ```
       --mode data-only (M0.5 Stage 1):
         1. environment_preflight()
         2. load_signals() [normalizers + dedup + classify + bridge]
         3. synthesize_macro()
         4. korea_signal_layer()
         5. stock_selector()
         6. synthesize_stock() + valuation_comparator()
         7. Save context_[date].json
         8. Update last_successful_run.txt
         9. Telegram: "데이터 수집 완료, /weekly-report 실행하세요"

       --mode full-auto (M1):
         [Stage 1 same as above]
         + intelligence_engine.generate_narrative() [Anthropic API direct call]
         + report_generator() + validate_report_quality()
         + compliance_filter()
         + Telegram send (with delivery_mode handling)
         + accuracy_tracker.record()
       ```
       Include checkpoint: save `data_freshness` timestamps to state.yaml after each data fetch.

    2. **launchd plist** (`com.investscan.weekly.plist`) — 완전한 XML (P14):
       USERNAME을 `os.environ.get("USER")`로 자동 치환 후 저장.
       Apple Silicon Mac: `/opt/homebrew/bin/python3` / Intel Mac: `/usr/local/bin/python3`
       (설치 경로 확인: terminal에서 `which python3`)
       ```xml
       <?xml version="1.0" encoding="UTF-8"?>
       <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
         "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
       <plist version="1.0">
       <dict>
           <key>Label</key>
           <string>com.investscan.weekly</string>

           <key>ProgramArguments</key>
           <array>
               <string>/opt/homebrew/bin/python3</string>
               <!-- Intel Mac: /usr/local/bin/python3 으로 변경 -->
               <string>/Users/USERNAME/investscan/weekly_orchestrator.py</string>
               <string>--mode</string>
               <string>data-only</string>
           </array>

           <key>WorkingDirectory</key>
           <string>/Users/USERNAME/investscan</string>

           <key>StartCalendarInterval</key>
           <dict>
               <key>Weekday</key>
               <integer>0</integer>
               <!-- 0 = Sunday (macOS launchd 기준 확인됨) -->
               <key>Hour</key>
               <integer>20</integer>
               <key>Minute</key>
               <integer>0</integer>
           </dict>

           <key>StandardOutPath</key>
           <string>/Users/USERNAME/investscan/logs/orchestrator.log</string>

           <key>StandardErrorPath</key>
           <string>/Users/USERNAME/investscan/logs/orchestrator_err.log</string>

           <key>EnvironmentVariables</key>
           <dict>
               <key>PATH</key>
               <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
               <!-- Homebrew Python을 launchd 환경의 제한된 PATH에서 찾을 수 있도록 설정 -->
           </dict>

           <key>RunAtLoad</key>
           <false/>
           <!-- 시스템 시작 시 즉시 실행 안함 — 일요일 20:00에만 실행 -->

           <key>KeepAlive</key>
           <false/>
           <!-- 실패 시 자동 재시작 안함 — 주 1회 스케줄 실행 -->
       </dict>
       </plist>
       ```
       저장: `~/Library/LaunchAgents/com.investscan.weekly.plist`
       등록: `launchctl load ~/Library/LaunchAgents/com.investscan.weekly.plist`
       확인: `launchctl list | grep investscan` → 목록에 표시되면 정상

    3. **health_dashboard.py**: Generate `output/dashboard/weekly_dashboard.html` with:
       - Last run timestamp
       - Sector directions + confidence chart
       - Data freshness status (envscan age, gnews age)
       - 5 recent error log entries
       - Kill Switch status (KS-1, KS-2, KS-3)

    4. **personalizer.py**: Role = user input handling (separate from config.py = runtime loading)
       - Interactive prompts for sector addition/removal
       - Keychain write: `keyring.set_password("investscan", key, value)`
       - Update investscan.yaml sections via YAML safe_load/dump

    5. Register launchd: `launchctl load ~/Library/LaunchAgents/com.investscan.weekly.plist`

    6. **`/weekly-report` slash command file** — create `.claude/commands/weekly-report.md`:
       ```markdown
       # /weekly-report

       Stage 2 트리거 — InvestScan 주간 리포트 생성

       ## 실행 전 확인
       1. Check state.yaml `data_freshness.context_file_generated_at` — must be today or yesterday
       2. If stale: warn user "데이터 파일이 오래됐습니다. launchd가 실행됐는지 확인하세요."

       ## 실행
       Load `output/context/context_[latest_date].json` and run intelligence_engine.py
       in Claude Code interactive session. Apply Category A/B prompts. Generate NarrativeOutput.
       Then run validate_report_quality.py (8-item check). Then run report_generator.py.
       Present HITL-3 checklist when report is ready.

       ## 완료 메시지
       "✅ 리포트 생성 완료: output/reports/[날짜].md
        발송 전 5가지를 확인해주세요: [HITL-3 체크리스트]"
       ```

    7. **`pause_weeks` handling** — add to `watchdog.py`:
       ```python
       def is_paused_week(config: Config) -> bool:
           today = datetime.now().strftime("%Y-%m-%d")
           return today in config.pause_weeks
       # In Monday 08:00 job:
       if is_paused_week(config):
           logger.info(f"Pause week: {today}. Skipping report. KS-3 counter not incremented.")
           return  # Silent skip — no Telegram needed (user intentionally paused)
       ```
       **권장안 적용**: pause_weeks 주에는 KS-3 연속 실패 카운터를 증가시키지 않음.

    8. **`onboarding_mode` auto-transition** — add to `watchdog.py`:
       ```python
       def check_onboarding_transition(config: Config, state: dict):
           """Calculate weeks_since_install from state.yaml system.installed_at."""
           installed_at_str = state.get("system", {}).get("installed_at", "")
           if not installed_at_str:
               return  # installed_at not set yet — skip
           installed_at = datetime.fromisoformat(installed_at_str)
           weeks_since_install = (datetime.now() - installed_at).days // 7
           if config.onboarding_mode and weeks_since_install >= 4:
               send_telegram(
                   "처음 4주가 지났습니다. "
                   "간결한 리포트로 전환하려면 Claude Code에서 '용어 설명 없애줘'라고 말씀해주세요."
               )
               # User action in Claude Code → personalizer.py sets onboarding_mode: false
               # (Telegram은 단방향 채널 — 응답 수신 불가. Claude Code 세션에서 처리)
       ```
       **권장안 적용**: `state.yaml system.installed_at`에서 설치 날짜를 읽어 weeks_since_install 계산.
       `system.installed_at`는 Step 7 M0.5 완료 시 weekly_orchestrator.py가 최초 1회 기록.

    9. **`all_bullish_3weeks` flag** — add to `weekly_orchestrator.py`:
       ```python
       def check_all_bullish_3weeks(state: dict) -> bool:
           """Check last 3 weeks in predictions.jsonl — all sectors Bullish."""
           recent = load_last_n_predictions(n=3)
           return all(p.direction == "Bullish" for p in recent) and len(recent) >= 3
       # In report generation flow (before Telegram send):
       if check_all_bullish_3weeks(state):
           state["all_bullish_3weeks"] = True  # Jinja2 template renders warning banner
       ```
       **권장안 적용**: weekly_orchestrator.py가 관리, Jinja2 템플릿에서 조건부 경고 출력.

    Reference: PRD §3.5, §4.2, §9, workflow-idea.md 핵심수정 10, 15, 아이디어 2
- **Output**: `weekly_orchestrator.py` + `health_dashboard.py` + `personalizer.py` + `com.investscan.weekly.plist` + launchd 등록 완료
- **Review**: `@reviewer` — launchd 보안 설계 (평문 API 키 부재 확인) + orchestrator 파이프라인 완전성
- **Translation**: `none`
- **Post-processing**: state.yaml `milestones.m1.phase_6_done: true` + `milestones.m1.launchd_activated: true` 업데이트

---

### Step 15: M1 Final Validation — 완전 자동화 인수 테스트

- **Pre-processing**: |
    M1 전환 전 비용 재고지 (HITL-2에서 이미 동의했으나 최종 확인):
    - claude-opus-4-6 예상 비용: ~$0.06~0.15/회, ~$1~3/월
    state.yaml `hitl_2.choice` 확인 — "continue"이면 즉시 진행, "pause_2weeks"이면 watchdog 타이머 확인
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] M1 `intelligence_engine.py` Anthropic API 버전 작동 확인: `generate_narrative(context_path)` 호출 성공
  - [ ] `weekly_orchestrator.py --mode full-auto --dry-run` 성공 (Stage 1 + Stage 2 전 구간 검증)
  - [ ] Telegram 실제 메시지 수신 확인 (8항목 자동 검증 통과 버전)
  - [ ] `accuracy_tracker.py` PredictionRecord 저장 확인 (`data/accuracy/predictions.jsonl` 존재)
  - [ ] Kill Switch 모니터링 체계 작동: KS-1(적중률<40%), KS-2(유용성<2.5점), KS-3(3연속 실패) 감지 로직 테스트
  - [ ] 3주 연속 전 섹터 Bullish 경고 자동 발송 로직 확인 (`all_bullish_3weeks` 플래그)
  - [ ] `실행방법.txt` 파일 생성됨 — 수동 실행 명령, Telegram 확인법, 오류 대응 3가지 포함
  - [ ] state.yaml `milestones.m1.final_acceptance_passed: true` 기록됨
- **Task**: |
    Perform M1 full system acceptance test — verify complete automation works end-to-end.

    1. **M1 intelligence_engine.py** (Anthropic API version):
       Register Anthropic API key in Keychain:
       `security add-generic-password -a investscan -s anthropic_api_key -w [KEY]`
       Verify `generate_narrative()` uses `claude-opus-4-6` with `temperature=0.3`.

    2. Update launchd plist: `--mode data-only` → `--mode full-auto`
       `launchctl unload [plist] && launchctl load [plist]`

    3. Run full dry-run: `python3 weekly_orchestrator.py --mode full-auto --dry-run`
       Verify all stages pass without actual API calls or Telegram sends.

    4. Run actual test (once, with real API):
       `python3 weekly_orchestrator.py --mode full-auto`
       Verify Telegram reception + report file in `output/reports/` ≥ 2000 bytes.

    5. Verify Kill Switch monitoring:
       - Test KS-1: `accuracy_tracker.evaluate_kill_switch()` with mocked <40% accuracy data
       - Test KS-2: Telegram feedback loop (send feedback prompt, mock <2.5 response)
       - Test KS-3: Mock 3 consecutive failures in state.yaml, verify alert

    6. Create `실행방법.txt` (Korean plain text):
       - Line 1: Manual run command
       - Line 2: How to check Telegram bot connection
       - Line 3: What to do if no message received Monday morning

    Reference: PRD §4.2, §5.1, workflow-idea.md 핵심수정 15
- **Output**: M1 작동 확인 + `실행방법.txt` + state.yaml final acceptance 기록
- **Review**: `@reviewer` — 최종 시스템 완전성 검증 (21개 모듈 모두 구현됨 확인)
- **Translation**: `none`
- **Post-processing**: state.yaml 전체 milestones 최종 확인

---

### Step 16: Handoff — 사용자 인계

- **Pre-processing**: state.yaml `milestones.m1.final_acceptance_passed: true` 확인
- **Agent**: `@general-purpose`
- **Verification**:
  - [ ] `실행방법.txt` 존재 + 3개 항목 완비
  - [ ] `output/docs/weekly-run.md` 생성됨 — 주간 루틴 6분 가이드 + 첫 4주 20분 안내
  - [ ] `output/docs/annual-maintenance.md` 생성됨 — 연 1회 점검 체크리스트 4항목
  - [ ] `output/dashboard/weekly_dashboard.html` 최신 상태로 생성됨
  - [ ] 최종 Telegram 완료 메시지 발송됨: "InvestScan M1 설정 완료! 이번 주 일요일 저녁부터 자동 실행됩니다."
  - [ ] state.yaml 전체 필드가 정상 상태로 기록됨 (no errors, all milestones done)
- **Task**: |
    Generate all user-facing handoff documents and deliver final completion notification.

    1. Verify `실행방법.txt` is complete with 3 items (manual run, Telegram check, Monday failure action).

    2. Create `output/docs/weekly-run.md` (Korean, non-coder friendly):
       - Monday 6-minute routine steps (per PRD §3.3)
       - First 4 weeks: 20 minutes guidance + what to expect
       - Self-verification guide for first report (per PRD §4.5)
       - What to do when system is wrong (per PRD §4.6)

    3. Create `output/docs/annual-maintenance.md`:
       - 4 annual checks: EnvScan schema changes, GlobalNews site changes,
         Claude API price review, investscan.yaml settings refresh
       - Trigger: "Claude Code에게 'InvestScan 연간 점검해줘'라고 말하면 됩니다."

    4. Update health_dashboard.html with final system status.

    5. Send Telegram completion message:
       "🎉 InvestScan M1 설치 완료!
        다음 주 월요일 08:00에 첫 리포트가 도착합니다.
        일요일 저녁에 MacBook 전원 연결 + 덮개 열어두기를 잊지 마세요."

    Reference: PRD §3.6, §4.5, workflow-idea.md 아이디어 8
- **Output**: `output/docs/weekly-run.md` + `output/docs/annual-maintenance.md` + 완료 Telegram 발송
- **Review**: `none`
- **Translation**: `@translator` → `output/docs/weekly-run.ko.md` (사용자 대면 문서 한국어 확인)
- **Post-processing**: 워크플로우 완료. state.yaml `workflow.current_phase: "completed"` 기록.

---

## Claude Code Configuration

### Sub-agents

```yaml
# .claude/agents/investscan-implementer.md (옵션 — 복잡한 모듈 구현 위임용)
---
name: investscan-implementer
description: "InvestScan 모듈 구현 전문가. schema.py, normalizers.py 등 복잡한 Python 모듈 작성 시 위임."
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep
permissionMode: default
maxTurns: 30
memory: project
---
Implement InvestScan Python modules following PRD specifications exactly.
Always check .claude/state.yaml for current discovered_schema before writing field access code.
IMMUTABLE: sentiment_weight must always be 0.0. Never modify this value.
```

```yaml
# .claude/agents/reviewer.md (기존 에이전트 — 이미 구성됨)
# 사용 시점: Step 7(M0.5 코드), Step 11(intelligence_engine), Step 12(리포트+validate), Step 14(launchd 보안), Step 15(최종 인수)
```

```yaml
# .claude/agents/fact-checker.md (기존 에이전트 — 이미 구성됨)
# 사용 시점: Step 2(schema mapping 정확성), Step 12(리포트 수치 정합성)
```

**모델 선택 근거**:
- `opus` — 21개 모듈 구현 (복잡한 코드 생성, 절대 기준 1: 품질 우선)
- `sonnet` — 리뷰·팩트체킹 (안정적 검증 작업)
- `haiku` — 단순 파일 생성·포맷팅 (health_dashboard HTML 등)

---

### SOT (상태 관리)

- **SOT 파일**: `.claude/state.yaml`
- **쓰기 권한**: `weekly_orchestrator.py` (Stage 1 완료 시 자동) + Claude Code 인터랙티브 세션 (HITL 게이트 후)
- **에이전트 접근**: 읽기 전용 — 모든 모듈은 state.yaml을 read-only로 참조, 직접 수정 금지
- **품질 우선 조정**: 기본 패턴 적용. Stage 1(headless) ↔ Stage 2(interactive) 분리로 동시 쓰기 충돌 구조적 방지.

```yaml
# .claude/state.yaml 초기 부트스트랩 구조
workflow:
  name: "InvestScan"
  current_phase: "research"   # research | planning | implementation | completed
  current_step: 1
  refinement_count: 0          # Step 12-R 실행 횟수 (최대 2)
  parent_genome:
    version: "2026-03-28"
    source: "AgenticWorkflow"
    principles: ["quality-absolutism", "single-file-sot", "code-change-protocol"]

discovered_paths:
  envscan_wf1_output: ""
  gnews_signals: ""
  investscan_root: ""
  config_file: ""
  runtime_mode: ""             # "full" | "envscan_only" | "independent"

discovered_schema:
  envscan_wf1:
    steeps_field: ""
    psst_field: null
    psst_substitute: ""
    score_scale: ""
    summary_field: null
    summary_substitute: ""
    classification_optional_ratio: 0.0
    analysis_optional_ratio: 0.0
    preliminary_category_values: []  # Step 2에서 실제 EnvScan 값 기록 — e.g. ["T","E","P","S","s","E_Environmental"]
  gnews:
    file_exists: false
    confidence_field: "confidence"
    confidence_scale: "0-1"
  schema_decisions_recorded_at: ""
  overt_correction_needed: false

data_freshness:
  signals_parquet_generated_at: ""
  envscan_db_generated_at: ""
  context_file_generated_at: ""
  stale_warning: false

hitl_gates:
  hitl_1:
    passed: false
    claude_max_confirmed: false
    telegram_configured: false
    telegram_chat_id_registered: false # true = Keychain에 telegram_chat_id 등록됨 (알림 발송 활성화) — Step 6 item 3b
    dart_api_key_registered: false    # true = Keychain에 dart_api_key 등록됨 (재무수치 활성화)
    fred_api_key_registered: false    # true = Keychain에 fred_api_key 등록됨 (미국 매크로 활성화)
    sectors_confirmed: []
    publish_platform: "personal"
    watchlist_override: []
  hitl_2:
    passed: false
    telegram_received: false
    choice: ""                   # "continue" | "pause_2weeks"
    choice_date: ""
  hitl_3:
    passed: false
    validate_score: 0.0
    validate_delivery_mode: ""
    checklist_score: null
    refinement_triggered: false

stock_selection:
  category_a: []
  category_b: []
  selected_at: ""
  manual_override: false
  watchlist_override: []

milestones:
  m05:
    done: false
    dg_01_to_08_passed: false
  m1:
    phase_2_done: false
    phase_3_done: false
    phase_4_intelligence_done: false
    phase_5_done: false
    validate_8_passed: false
    phase_6_done: false
    launchd_activated: false
    final_acceptance_passed: false

packages:
  m05_ready: false
  m1_ready: false
  fixtures_generated: false
  failed_packages: []

system:
  installed_at: ""              # ISO 8601 — Step 7 최초 M0.5 완료 시 기록. watchdog.py가 weeks_since_install 계산에 사용.
  version: "1.0.0"

errors: []
```

---

### Hooks (기존 시스템 활용)

| Hook 이벤트 | 스크립트 | InvestScan 적용 |
|------------|---------|---------------|
| PreToolUse (Bash) | `block_destructive_commands.py` | `rm -rf` 등 위험 명령 차단 |
| PreToolUse (Edit\|Write) | `predictive_debug_guard.py` | 에러 이력 있는 파일 수정 시 경고 |
| PostToolUse (Edit\|Write) | `security_sensitive_file_guard.py` | `investscan.yaml`, Keychain 관련 파일 수정 시 경고 |
| Stop | `generate_context_summary.py` | 세션 종료 시 구현 진행 상황 스냅샷 |

---

### Slash Commands

| 커맨드 | 파일 | 역할 |
|--------|------|------|
| `/weekly-report` | `.claude/commands/weekly-report.md` | Stage 2 트리거 — `intelligence_engine.py` 실행 → HITL-3 |
| `/hitl-1-setup` | `.claude/commands/hitl-1-setup.md` | HITL-1 대화형 설정 안내 |
| `/hitl-2-m1-decision` | `.claude/commands/hitl-2-m1-decision.md` | HITL-2 M1 전환 결정 |
| `/hitl-3-report-review` | `.claude/commands/hitl-3-report-review.md` | HITL-3 리포트 체크리스트 |

---

### Context Injection Patterns

| 단계 | 입력 크기 | 패턴 선택 |
|------|---------|---------|
| Step 2 (Schema Analysis) | database.json 샘플 < 50KB | **Pattern A** — 파일 경로 직접 전달 |
| Step 7 (M0.5 구현) | PRD + schema-mapping < 50KB | **Pattern A** — 참조 파일 경로 전달 |
| Step 11 (Intelligence Engine) | context_[날짜].json ~8K tokens | **Pattern A** — 전체 위임 |
| Step 12 (Report Generation) | NarrativeOutput JSON | **Pattern A** — JSON 경로 전달 |

---

### M0.5 → M1 전환 결정 트리

```
HITL-2 선택에 따른 분기:

[A] "M1 계속 진행" 선택:
  → Step 9부터 바로 M1 구현 진행
  → intelligence_engine.py M1 버전(Anthropic API 직접 호출) 구현
  → launchd plist: --mode full-auto 설정
  → Anthropic API 키 Keychain 등록

[B] "2주 M0.5 사용" 선택:
  → state.yaml hitl_2.choice_date 기록
  → watchdog.py가 14일 경과 시 Telegram:
    "M1 전환 준비됐습니다. Claude Code에서 /weekly-report 실행하세요."
  → 사용자 확인 후 Step 9 재개

M1 intelligence_engine.py 핵심 코드:
  client = anthropic.Anthropic()  # API 키: macOS Keychain에서 동적 로드
  response = client.messages.create(
      model="claude-opus-4-6",    # 결과 일관성 보장을 위해 모델 고정
      temperature=0.3,             # 창의성↓ 정확성↑
      max_tokens=4096,
      system=CATEGORY_A_SYSTEM_PROMPT,
      messages=[{"role": "user", "content": f"Context:\n{context_json}"}]
  )
```

---

### 21개 모듈 구현 현황 추적

| # | 모듈 | LOC | 단계 | 의존성 |
|---|------|-----|------|--------|
| 1 | `config.py` | ~100 | Step 7 | investscan.yaml, Keychain |
| 2 | `schema.py` | ~250 | Step 5 | Python stdlib |
| 3 | `normalizers.py` | ~300 | Step 7→9 | schema.py, state.yaml |
| 4 | `synthesize_macro.py` | ~200 | Step 7→9 | schema.py, signal_policy |
| 5 | `telegram_notifier.py` | ~100 | Step 7 | Keychain, requests |
| 6 | `compliance_filter.py` | ~80 | Step 7 | COMPLIANCE_RULES |
| 7 | `dedup.py` | ~150 | Step 9 | schema.py, hashlib |
| 8 | `steeps_classifier.py` | ~200 | Step 9 | SteepsCategory StrEnum |
| 9 | `signal_bridge.py` | ~200 | Step 9 | sector_stock_map.yaml |
| 10 | `korea_signal_layer.py` | ~150 | Step 10 | FDR, EnvironmentScan |
| 11 | `stock_selector.py` | ~150 | Step 10 | InvestmentMeta, FDR |
| 12 | `synthesize_stock.py` | ~200 | Step 11 | DART, pykrx, FRED |
| 13 | `valuation_comparator.py` | ~120 | Step 11 | pykrx |
| 14 | `intelligence_engine.py` | ~150 | Step 11 | schema.py, Anthropic API |
| 15 | `report_generator.py` | ~200 | Step 12 | Jinja2, NarrativeOutput |
| 16 | `validate_report_quality.py` | ~120 | Step 12 | report_md, narrative_json |
| 17 | `weekly_orchestrator.py` | ~250 | Step 14 | All modules |
| 18 | `accuracy_tracker.py` | ~200 | Step 12 | PredictionRecord, FDR |
| 19 | `watchdog.py` | ~120 | Step 12 | FAILURE_GUIDE, launchd |
| 20 | `health_dashboard.py` | ~80 | Step 14 | state.yaml, logs |
| 21 | `personalizer.py` | ~150 | Step 14 | Keychain, investscan.yaml |
| **합계** | | **~3,430** | | |

---

### 네트워크 장애 대응 매트릭스

| 모듈 | 외부 의존성 | 장애 시 동작 |
|------|-----------|------------|
| `korea_signal_layer.py` | FDR (KRX) | graceful skip — 글로벌 신호만 사용 |
| `stock_selector.py` | FDR (수급) | fallback — 신호 점수 순위로 대체 |
| `synthesize_stock.py` | DART OpenAPI | graceful skip — 실적 수치 없이 방향성만 |
| `synthesize_stock.py` | pykrx | graceful skip — valuation 섹션 생략 |
| `synthesize_stock.py` | FRED API | graceful skip — 매크로 섹션 생략 |
| `intelligence_engine.py` | Claude API | fallback — v1 템플릿(수치 표만) 발송 |
| `telegram_notifier.py` | Telegram Bot API | 3회 재시도 → 로컬 로그 저장 |
| `accuracy_tracker.py` | FDR (가격 조회) | 4주 후 재시도 대기 |

**Telegram 장애 시**: 리포트는 항상 `~/investscan/output/reports/YYYY-WW.md`에 로컬 저장됨.

---

*InvestScan workflow.md v1.0 — workflow-idea.md v4 Final + PRD v1.3 완전 통합*
*생성일: 2026-03-28 | 저장 위치: /prompt/workflow.md*
