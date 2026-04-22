# InvestScan — 아키텍처 및 설계 철학

> **문서 범위**: InvestScan 자식 시스템의 도메인 고유 아키텍처
> **부모 프레임워크**: [AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md)
> **설계 결정 이력**: [DECISION-LOG.md](DECISION-LOG.md)

---

## 1. 시스템 존재 이유

InvestScan은 단 하나의 문제를 해결한다:

> **글로벌 경제 신호 → 수치·근거·리스크를 갖춘 한국어 투자 관찰 리포트 → Telegram 자동 발송**

사람이 매주 수십 개의 경제 지표를 분석하고, 섹터 방향을 판단하고, 종목 내러티브를 작성하는 작업을 **완전 자동화**한다.
이 시스템은 **투자 조언이 아니다.** 공개 정보 기반의 거시 신호 관찰 리포트다.

### 1.1 핵심 철학: "Python is the judge, LLM is the narrator"

```
데이터 수집 → [Python 검증 Gate] → LLM 내러티브 → [Python 품질 Gate] → 리포트
```

LLM은 텍스트를 **쓰는** 역할만 한다. 분류·검증·임계값 판단은 **모두 Python 코드**가 한다.
이것이 P6 (Python-First) 원칙이다. LLM 환각(hallucination)이 리포트 품질에 영향을 주지 않도록
Python Gate가 앞과 뒤에서 통제한다.

### 1.2 절대 불변 상수

이 두 상수는 어떤 상황에서도 변경하지 않는다:

```python
sentiment_weight = 0.0          # 감정 편향 제거 — 비감정 분석 보장
                                 # 변경 시: 파이프라인 즉시 중단 (validate_report_quality.py 검증)

BULLISH_THRESHOLD = 0.01         # 매수 판정 임계값: +1%
                                 # 근거: ADR-048 — +2%→+1% 완화 (v3.6 I-4)
```

---

## 2. 설계 원칙 (P1–P6)

모든 구현 결정은 이 6개 원칙의 우선순위에 따라 판단한다.

| 원칙 | 이름 | 내용 | 적용 예시 |
|------|------|------|-----------|
| **P1** | 데이터 정제 우선 | AI 전달 전 Python으로 노이즈 제거 | `normalizers.py`가 EnvScan 신호를 `NormalizedSignal`로 변환한 후 LLM에 전달 |
| **P2** | 전문성 기반 위임 | Orchestrator는 조율만, 전문 에이전트에 위임 | `intelligence_engine.py`는 내러티브만, `stock_selector.py`는 선택만 |
| **P3** | 리소스 정확성 | 정확한 경로 명시, placeholder 불가 | `discovered_paths.envscan_wf1_output` = 절대 경로 |
| **P4** | 질문 최소화 | 최대 4개 질문, 각 3개 선택지 | HITL 게이트는 명확한 선택지만 제시 |
| **P5** | English-First 실행 | 내부 에이전트 로직은 영어 | 모든 Python 모듈, 에이전트 지시서 영어 작성 |
| **P6** | Python-First 판단 | 분류·임계값·검증은 Python, LLM은 서사만 | `steeps_classifier.py`, `stock_selector.py`, `compliance_filter.py` |

### 절대 기준 (상위 3개 — P1-P6보다 상위)

```
절대 기준 1: 품질 최우선 (속도·비용·작업량 완전 무시)
절대 기준 2: 단일 파일 SOT (state.yaml이 유일한 진실 소스)
절대 기준 3: 코드 변경 프로토콜 (의도 파악 → 영향 분석 → 변경 설계)
```

---

## 3. 시스템 아키텍처

### 3.1 전체 조감도

```
┌─────────────────────────────────────────────────────────────────┐
│                    InvestScan 시스템 경계                         │
│                                                                   │
│  ┌─────────────┐    ┌──────────────────────────────────────────┐ │
│  │  외부 데이터  │    │             AI 파이프라인                 │ │
│  │             │    │                                           │ │
│  │ FRED API    │───▶│  Stage 1: 설정 로드                       │ │
│  │ (금리·인플)  │    │  Stage 2: 신호 정규화 (Python P1)         │ │
│  │             │    │  Stage 3: 매크로 합성 (Python P6)         │ │
│  │ EnvScan DB  │───▶│  Stage 4: 종목 재무 합성 (Python P6)      │ │
│  │ (STEEPS 신호)│    │  Stage 5: 카테고리 선택 (Python P6)       │ │
│  │             │    │  Stage 6: 내러티브 생성 (LLM + 재시도 3회) │ │
│  │ DART API    │───▶│  Stage 7: 인용 검증 (Python)              │ │
│  │ (재무 데이터) │    │  Stage 8: 리포트 생성 (Jinja2)            │ │
│  └─────────────┘    │  Stage 9: 원자적 저장                     │ │
│                      │  Stage 10: Telegram 발송 + SOT 갱신      │ │
│  ┌─────────────┐    └──────────────────────────────────────────┘ │
│  │  사람 개입   │                      │                          │
│  │  (HITL)     │◀─────────── HITL-3 검토 요청                   │ │
│  │             │                      │                          │ │
│  └──────┬──────┘    ┌────────────────▼────────────────────────┐ │
│         │           │           최종 출력                       │ │
│         │           │  • 영어 리포트 (output/reports/*.md)      │ │
│         └──────────▶│  • 한국어 번역 (*.ko.md)                  │ │
│                      │  • TXT + PDF + MD (투자분석제안/)         │ │
│                      │  • Telegram 5줄 요약                     │ │
│                      └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 10단계 파이프라인 상세

| 단계 | 모듈 | 입력 | 출력 | Gate |
|------|------|------|------|------|
| **Stage 1** | `config.py` | `investscan.yaml` | Config 객체 | BULLISH_THRESHOLD=0.01 검증 |
| **Stage 2** | `normalizers.py` | EnvScan JSON | `NormalizedSignal[]` | P1: 빈 필드·형식 오류 제거 |
| **Stage 3** | `synthesize_macro.py` | FRED fixture | `InvestmentMeta` | P6: 4개 레이블 결정론적 산출 |
| **Stage 4** | `synthesize_stock.py` | DART/pykrx | `StockFinancials` | FDR→pykrx→DART fallback chain |
| **Stage 5** | `stock_selector.py` | `InvestmentMeta` | Category A/B | P6: BULLISH_THRESHOLD 비교 |
| **Stage 6** | `intelligence_engine.py` | Context JSON | `NarrativeOutput` | Reflect-Revise 최대 3회 |
| **Stage 7** | `citation_validator.py` | `NarrativeOutput` | 인용 오류 경고 | 비차단 (경고만) |
| **Stage 8** | `report_generator.py` | `NarrativeOutput` | 마크다운 리포트 | Jinja2 템플릿 렌더링 |
| **Stage 9** | `weekly_orchestrator.py` | 마크다운 | 저장된 파일 | 원자적 쓰기 (tmp→rename) |
| **Stage 9.5** | `export_report.py` | `.md` 리포트 | TXT + PDF + MD | `~/Desktop/Ai_works/output/투자분석제안/` |
| **Stage 10** | `telegram_notifier.py` | 리포트 | Telegram 메시지 | Dry-run(M0.5) / 실발송(M1) |

### 3.3 Stage 6 상세: 내러티브 생성 Reflect-Revise 루프

```
intelligence_engine.py (LLM 호출)
         ↓
python_validate_first()          ← P6 Gate: 입력 데이터 완전성 검증
         ↓ PASS
validate_report_quality.py       ← Category A: 5필드 / Category B: 6필드 검증
         ↓ PASS
compliance_filter.py             ← 10패턴 법적 표현 검사
         ↓ PASS
content_gate()                   ← 8기준 구조 검증
         ↓ PASS
산출물 확정                         ← sentiment_weight == 0.0 최종 확인

실패 시: 최대 3회 재시도 → 3회 초과 시 HITL 에스컬레이션
```

---

## 4. 모듈 맵 (27개 Python 모듈)

### 4.1 데이터 수집 계층

| 모듈 | 역할 | 핵심 기능 |
|------|------|-----------|
| `normalizers.py` | EnvScan 신호 정규화 | P1 Gate: `NormalizedSignal` 스키마 변환 |
| `signal_bridge.py` | 신호 브리지 | EnvScan → `UnifiedSignal` 변환 |
| `korea_signal_layer.py` | 한국 시장 신호 | KOSPI, 외국인 순매수 데이터 |
| `dedup.py` | 신호 중복 제거 | 동일 신호 필터링 |

### 4.2 합성 계층 (P6 Python-First)

| 모듈 | 역할 | 핵심 기능 |
|------|------|-----------|
| `synthesize_macro.py` | FRED 매크로 합성 | `InvestmentMeta` 생성: rate_direction, inflation_trend, risk_appetite, usd_strength |
| `synthesize_stock.py` | 종목 재무 합성 | DART+pykrx fallback chain → `StockFinancials` |
| `steeps_classifier.py` | STEEPs 분류 | 키워드 룩업 테이블 (95% TDD) |
| `stock_selector.py` | 카테고리 선택 | Category A/B 결정 (BULLISH_THRESHOLD 기반) |

### 4.3 내러티브 및 검증 계층

| 모듈 | 역할 | 핵심 기능 |
|------|------|-----------|
| `intelligence_engine.py` | LLM 내러티브 생성 | CATEGORY_A/B_SYSTEM_PROMPT, English-First |
| `validate_report_quality.py` | 리포트 품질 검증 | 8기준 Python 검증 (L1 Gate) |
| `compliance_filter.py` | 컴플라이언스 필터 | 10패턴 법적 표현 검사 (P1 Critical) |
| `citation_validator.py` | 인용 정확성 검증 | 정량 데이터 인용 일관성 확인 |
| `valuation_comparator.py` | 밸류에이션 비교 | PER/PBR vs 섹터 평균 비교 |
| `narrative_cross_check.py` | 내러티브 교차 검증 | 신호-내러티브 일관성 |

### 4.4 리포트 및 전달 계층

| 모듈 | 역할 | 핵심 기능 |
|------|------|-----------|
| `report_generator.py` | 리포트 생성 | Jinja2 템플릿 → 마크다운 |
| `telegram_notifier.py` | Telegram 발송 | `build_5line_summary()` + httpx API |
| `health_dashboard.py` | 상태 대시보드 | HTML 상태 페이지 생성 |

### 4.5 추적 및 인프라 계층

| 모듈 | 역할 | 핵심 기능 |
|------|------|-----------|
| `accuracy_tracker.py` | 정확도 추적 | KS-1 이중 윈도우 (4주+8주) |
| `watchdog.py` | 이상 탐지 | 파이프라인 이상 감지 |
| `personalizer.py` | 개인화 | 사용자 포트폴리오 맥락 |
| `schema.py` | 데이터 스키마 SOT | 불변 dataclass 정의 |
| `config.py` | 설정 로더 | YAML 설정 파일 로드 |
| `weekly_orchestrator.py` | 메인 오케스트레이터 | 10단계 파이프라인 조율 |
| `pacs_calculator.py` | 번역 품질 산출 | pACS 결정론적 산출 (P6) |

### 4.6 CLI 지원 모듈

| 모듈 | 역할 |
|------|------|
| `run_summary.py` | 파이프라인 완료 후 3줄 요약 출력 |
| `preview_report.py` | 리포트 인라인 미리보기 |
| `approve_hitl.py` | HITL-3 간소화 승인 (Y/N) |
| `export_report.py` | 리포트 TXT + PDF + MD 내보내기 — `~/Desktop/Ai_works/output/투자분석제안/` |

---

## 5. 데이터 스키마 (schema.py — SOT)

`schema.py`는 모든 데이터 계약의 단일 진실 소스다. 변경 시 전체 파이프라인 영향.

```python
@dataclass(frozen=True)
class NarrativeOutput:
    stock_name: str
    stock_code: str
    category: str               # "A" | "B"
    direction: SectorDirection  # BULLISH | BEARISH | NEUTRAL
    sentiment_weight: float     # 절대 불변: 항상 0.0
    narrative_text: str
    # ... 추가 필드

@dataclass(frozen=True)
class InvestmentMeta:
    rate_direction: str         # RISING | FALLING | HOLD
    inflation_trend: str        # RISING | COOLING | STABLE
    risk_appetite: str          # HIGH | MODERATE | LOW
    usd_strength: str           # STRONG | WEAK | NEUTRAL

class SteepsCategory(StrEnum):
    T = "T"          # Technology
    E = "E"          # Economy
    P = "P"          # Political
    S = "S"          # Social
    E_ENV = "E_Environmental"

class SectorDirection(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
```

---

## 6. SOT 계층 구조

단일 파일 SOT 원칙: **모든 공유 상태는 `.claude/state.yaml`에 집중**.
Orchestrator만 쓰기 권한을 가진다.

```yaml
# .claude/state.yaml 구조
packages:
  m05_ready: true          # M0.5 마일스톤 완료 여부

milestones:
  m1: {}                   # M1 Done Gate 상태

hitl_1:                    # HITL-1 완료 상태 (API 키 등록)
  completed: false
  fred_api_key_registered: false
  dart_api_key_registered: false
  telegram_bot_token_registered: false

hitl_2:                    # HITL-2 완료 상태 (런타임 모드 선택)
  completed: true
  choice: envscan_only     # full | envscan_only | independent

hitl_3:                    # HITL-3 완료 상태 (리포트 승인)
  completed: false
  report_approved: false

workflow:
  current_step: 0
  runtime_mode: envscan_only

errors: []
```

**원자적 쓰기 패턴** (모든 state.yaml 쓰기):
```python
tmp = ".claude/state.yaml.tmp"
# 1. tmp 파일에 쓰기
# 2. os.replace(tmp, ".claude/state.yaml")  ← 원자적 교체
```

---

## 7. 품질 보장 4계층

| 계층 | 이름 | 담당 | 임계값 |
|------|------|------|--------|
| **L0** | Anti-Skip Guard | Hook (결정론적) | 파일 존재 + ≥100 bytes |
| **L1** | Verification Gate | 에이전트 자기검증 | 기능 목표 100% 달성 |
| **L1.5** | pACS Self-Rating | Pre-mortem 채점 | GREEN ≥70, YELLOW 50-69, RED <50 |
| **L2** | Adversarial Review | `@reviewer` + `@fact-checker` | R1-R5 5항목 검증 |

### 번역 품질 (pACS)

번역 결과의 품질은 Python이 결정론적으로 산출한다 (P6 원칙):

```
pACS = min(Ft, Ct, Nt)
  Ft: Fidelity (충실도)
  Ct: Completeness (완전성)
  Nt: Naturalness (자연스러움)

GREEN ≥ 85  → 자동 진행
YELLOW 70-84 → 플래그 후 진행
RED < 70    → 재번역 필요
```

---

## 8. 마일스톤 게이트 (16개 Done Gate)

### M0.5 — 파이프라인 기반 구축 (✅ 달성)

| DG | 검증 내용 | 상태 |
|----|-----------|------|
| DG-01 | 설정 로드, `BULLISH_THRESHOLD=0.01` 확인 | ✅ PASS |
| DG-02 | `normalize_envscan()` → `NormalizedSignal` 생성 | ✅ PASS |
| DG-03 | `synthesize_macro()` → 유효 레이블 4개 반환 | ✅ PASS |
| DG-04 | `NarrativeOutput`: `sentiment_weight=0.0`, `text≥1000B` | ✅ PASS |
| DG-05 | `compliance_filter()` 10패턴: PASS+BLOCKED 구분 | ✅ PASS |
| DG-06 | `build_5line_summary()` dry-run 성공 | ✅ PASS |
| DG-07 | `run_full_pipeline()` dry-run 전체 성공 | ✅ PASS |
| DG-08 | `state.yaml` 원자적 쓰기, `m05_ready=True` | ✅ PASS |

### M1 — 실제 API 통합 (🎯 다음 목표)

| DG | 검증 내용 | 상태 |
|----|-----------|------|
| DG-09 | HITL-1 완료 (API 키 전체 등록) | 대기 |
| DG-10 | 실제 FRED API 연결 + 데이터 수신 | 대기 |
| DG-11 | 실제 DART API 연결 + 재무 데이터 수신 | 대기 |
| DG-12 | 실제 Telegram 발송 성공 | 대기 |
| DG-13 | 4주 정확도 추적 초기화 | 대기 |
| DG-14 | HITL-3 전체 흐름 완주 | 대기 |
| DG-15 | 에이전트 팀 병렬 실행 검증 | 대기 |
| DG-16 | 전체 파이프라인 실환경 1회 완주 | 대기 |

---

## 9. 자동 실행 스케줄

```xml
<!-- com.investscan.weekly.plist — macOS launchd 설정 -->
<key>StartCalendarInterval</key>
<dict>
  <key>Weekday</key><integer>0</integer>  <!-- 일요일 -->
  <key>Hour</key><integer>20</integer>    <!-- 20시 -->
  <key>Minute</key><integer>0</integer>
</dict>
```

**실행 순서:**
1. 일요일 20:00: `weekly_orchestrator --mode data-only` (데이터 수집 + 컨텍스트 저장)
2. 월요일: 사용자가 `/start` → `[1] 주간 리포트 생성` → 내러티브 생성
3. 완료 후: `run_summary.py` → 결과 요약 → `approve_hitl.py` → Telegram 발송

---

## 10. Context Preservation System

세션 경계에서 작업 맥락을 잃지 않도록 하는 Hook 기반 자동 저장·복원 시스템.

| Hook 이벤트 | 스크립트 | 동작 |
|------------|---------|------|
| SessionStart | `restore_context.py` | 이전 스냅샷 복원 + Predictive Debugging |
| PostToolUse | `update_work_log.py` | 작업 로그 누적 |
| Stop | `generate_context_summary.py` | 증분 스냅샷 저장 |
| PreCompact | `save_context.py` | 압축 전 전체 스냅샷 |
| PreToolUse | `block_destructive_commands.py` | 위험 명령 차단 |
| PostToolUse | `output_secret_filter.py` | API 키 등 시크릿 탐지 |

---

## 11. 에이전트 팀 (12개)

| 에이전트 | 역할 |
|----------|------|
| `investscan-orchestrator` | 마스터 오케스트레이터 — SOT 가드, 단계 조율 |
| `p1-critical-builder` | P1 Critical 모듈 빌더 (Opus, 95% TDD) |
| `module-builder` | 표준 TDD-first 모듈 빌더 |
| `tdd-runner` | 전체 테스트 스위트 실행 |
| `data-collector` | FRED/EnvScan 데이터 수집 |
| `fred-subagent` | FRED API 전용 |
| `envscan-subagent` | EnvironmentScan WF1 통합 |
| `gnews-subagent` | 글로벌 뉴스 신호 수집 |
| `report-reviewer` | 리포트 품질 리뷰 |
| `translator` | 영어→한국어 번역 (glossary 기반) |
| `reviewer` | 적대적 코드/산출물 리뷰 |
| `fact-checker` | 외부 사실 검증 |

---

## 12. 리포트 출력 형식 및 저장 경로

### 12.1 출력 형식 (3종)

| 형식 | 파일 | 용도 |
|------|------|------|
| **TXT** | `{DATE}_주간투자분석.txt` | 평문 텍스트 — 터미널·메모장 직독 |
| **PDF** | `{DATE}_주간투자분석.pdf` | 인쇄·공유용 — fpdf2 Helvetica 렌더링 |
| **MD** | `{DATE}_주간투자분석.md` | 원본 마크다운 참조용 |

### 12.2 저장 경로

```
~/Desktop/Ai_works/output/투자분석제안/
├── 2026-03-30_주간투자분석.txt
├── 2026-03-30_주간투자분석.pdf
└── 2026-03-30_주간투자분석.md
```

### 12.3 내보내기 CLI

```bash
# 최신 리포트 자동 탐지 후 내보내기
python3 -m investscan.export_report

# 날짜 지정
python3 -m investscan.export_report --date 2026-03-30

# 경로 직접 지정
python3 -m investscan.export_report --path /path/to/report.md

# 형식 선택
python3 -m investscan.export_report --formats txt,pdf
```

### 12.4 설계 결정 (ADR-056 요약)

- **fpdf2 선택**: 순수 Python, 외부 바이너리 불필요 → 설치·배포 단순화
- **latin-1 인코딩**: Helvetica 폰트는 latin-1만 지원 → `_safe()` 함수로 Unicode→ASCII 변환
- **경로 분리**: 파이프라인 중간 산출물(`output/reports/`)과 사용자 산출물(`투자분석제안/`) 역할 구분

---

## 13. 이론적 기반

**Recursive Language Models (RLM)** — MIT CSAIL
- 장기기억 구현의 이론적 기반
- Context Preservation System의 설계 원리
- 세션 경계를 넘는 인지 연속성 보장

**참조**: `coding-resource/recursive language models.pdf`

---

*이 문서는 InvestScan 자식 시스템 전용입니다.*
*부모 프레임워크(AgenticWorkflow) 설계 철학: [AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md)*
