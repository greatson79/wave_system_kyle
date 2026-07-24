# InvestScan workflow.md 설계 아이디어 회의록 (성찰 반영 v4)

> **작성일**: 2026-03-28
> **버전**: v4 — 4차 적대적 검토 반영 (공격/방어/신규 아이디어 10개 조치)
> **주의**: 이 문서는 확정안이 아닌 아이디어 풀이다. workflow.md 작성 전 참조용.
> **다음 단계**: 사용자 승인 후 workflow.md 초안 작성

---

## 절대 목표 (모든 판단의 유일한 기준)

> 사용자의 최소 입력을 받아, 글로벌 경제 흐름과 매크로 맥락을 반영한 날카로운 통찰로 —
> **수치·근거·리스크·투자의견을 갖춘** — **전문 애널리스트급 종목 투자 원고**를 자동 생성한다.
> 안정적 현재 종목과 미래 성장 테마를 구분하여 제공하며,
> **편집 없이 즉시 투자 판단과 콘텐츠 게시에 활용할 수 있는 완성본**을 출력한다.

---

## ⚠️ 로컬 실행 절대 원칙 (SaaS 방지 조항)

> 이 시스템은 사용자의 **로컬 맥북에서만 실행**된다. 아래 항목을 위반하면 즉시 중단한다.

| 금지 항목 | 허용 대안 |
|---------|---------|
| 클라우드 서버 배포 | 로컬 launchd만 사용 |
| 외부 서버에 리포트/예측 기록 저장 | 로컬 파일시스템만 사용 |
| AWS Lambda / cron.job.io 등 외부 스케줄러 | 로컬 launchd만 사용 |
| API 키를 원격 환경변수 서비스에 저장 | macOS Keychain만 사용 |
| 여러 사용자를 위한 공유 엔드포인트 구성 | 단일 사용자 로컬만 |

**허용되는 외부 연결 (로컬 오케스트레이션이지만 분석에 외부 API 활용):**
Claude API, Telegram Bot API, FRED API, DART OpenAPI, pykrx, FinanceDataReader (FDR)

---

## ⚠️ v2 → v3 핵심 수정 요약 (3차 전수조사 결과)

| 구분 | 발견된 문제 | v3 조치 |
|------|---------|--------|
| **[치명]** | Claude API 비용이 PRD "$200 전부" 주장과 충돌 | Claude Code 에이전트 방식으로 재설계 (옵션 A 채택) |
| **[치명]** | intelligence_engine.py 장애 시 fallback 없음 | v1 파이프라인 fallback + 에러 처리 명세 추가 |
| **[치명]** | Category A/B 단일 프롬프트 — 구분 미달 | 프롬프트 분리 설계 (A용/B용) |
| **[치명]** | InvestmentMeta 등 핵심 dataclass 스키마 미정의 | 인터페이스 계약 섹션 신설 |
| **[중요]** | HITL-1에 Claude API Key 입력 누락 | HITL-1에 추가 |
| **[중요]** | validate_report_quality.py 7항목 vs 11항목 불일치 | 7항목으로 통일, 헬퍼 함수 구현 전략 명시 |
| **[중요]** | HITL-3 실패 후 재조정 루프 Phase 구조에 없음 | Step 10-R (재조정 루프) 추가 |
| **[중요]** | Jinja2 변수 목록 미정의 | 템플릿 변수 매핑 추가 |
| **[중요]** | v2 신설 모듈 네트워크 장애 대응 없음 | 네트워크 매트릭스 확장 |
| **[중요]** | 게시 플랫폼 미정의 | 미결 질문 추가 |
| **[보완]** | 글로벌 경제 지표 미국+한국 편중 | 1단계 한계 인정 + M2 보완 계획 추가 |
| **[보완]** | few-shot 예시 불완전 | 완전한 예시 (입력+출력 JSON) 추가 |

---

## ⚠️ v3 → v4 핵심 수정 요약 (4차 적대적 검토 결과)

| 구분 | 발견된 문제 | v4 조치 |
|------|---------|--------|
| **[치명]** | 종목 자동 선정 로직 완전 누락 — "어떤 종목을 분석할지" 결정 로직 없음 | `stock_selector.py` 신설 + 자동 선정 기준 설계 |
| **[치명]** | Option A 기술적 불가 — launchd headless에서 Claude Code CLI 실행 불가 (OAuth·TTY·환경변수) | Hybrid 구조 재설계: Stage 1(데이터 자동화) + Stage 2(사용자 트리거 리포트) |
| **[중요]** | validate_report_quality.py가 PRD "감산 후 발송" 모델과 충돌 + 수치 정확성 검증 부재 | 8항목 확장, 감산 모델 통합, `_verify_metrics_consistency()` 추가 |
| **[중요]** | accuracy_tracker.py 상세 설계 전무 — PRD 6가지 명세 모두 누락 | 상세 설계 섹션 신설 (스키마·벤치마크·Naive Baseline·월간 리포트 형식) |
| **[중요]** | watchdog.py 상세 설계 전무 — 성공/실패 메시지·지연 감지 로직 미설계 | 상세 설계 섹션 신설 (메시지 형식·failure_guide·지연 감지 pseudo-code) |
| **[중요]** | HITL-3 1~5점 평가 = 비코더에게 무의미 | 체크리스트 방식으로 변경 (5개 예/아니오 질문) |
| **[중요]** | state.yaml에 hitl_2.choice_date 필드 없음 — "2주 M0.5 사용" 후 재개 타이머 불가 | state.yaml 업데이트 (choice_date, data freshness 필드 추가) |
| **[보완]** | compliance_filter.py "10개 샘플" 목록 실체 없음 (PRD 6개 쌍 미반영) | 금지 표현 6+4개 목록 명시 |
| **[보완]** | 에러 메시지 비코더 행동 불가 — 기술 메시지를 Telegram으로 전달 | 한국어 평문 에러 가이드 매핑 추가 (watchdog.py) |
| **[보완]** | signals.parquet 신선도 검증 부재 — 오래된 파일로 최신 리포트 생성 위험 | state.yaml에 `data_freshness` 섹션 추가 |

---

## ✅ 최종 확정 결정 사항 (v4 Final — 사용자 승인 완료)

> 아이디어 회의에서 열린 채로 남아있던 6가지 트레이드오프를 모두 확정.
> 이 결정들이 workflow.md의 구조와 구현 방식을 직접 결정한다.

| # | 결정 사항 | 확정 내용 | 적용 위치 |
|---|---------|---------|---------|
| **D1** | 자동화 방식 | **단계적 전환**: M0.5 = Hybrid(사용자 /weekly-report 트리거), M1 = 완전 자동(Anthropic API 직접 호출) | 핵심 수정 10, 핵심 수정 15 |
| **D2** | 전제 조건 상태 | Step 1에 EnvironmentScan/GlobalNews **자동 감지** + 없을 경우 **독립 실행 모드** fallback 설계 | 아이디어 1 Step 1 |
| **D3** | 구현 시작 방식 | **M0.5 먼저 2주** — HITL-2에서 M1 전환 승인 후 완전 자동으로 업그레이드 | HITL-2 |
| **D4** | 게시 플랫폼 | **[A] 개인 투자 판단용** 기본값 확정 (HITL-1에서 변경 가능) | HITL-1, Jinja2 |
| **D5** | 초기 관심 섹터 | **반도체·IT서비스·바이오** 기본값 확정 (HITL-1에서 변경 가능) | HITL-1 |
| **D6** | 리포트 활용 범위 | **외부 게시 기준** 법적 면책 조항 강화 설계 — 내부 사용에도 더 안전 | compliance, Jinja2 |

---

## 핵심 수정 1: Claude API 비용 충돌 해결 — 옵션 A 채택 ⚠️ v4에서 Hybrid로 진화

> **[v4 업데이트]** 아래 내용은 v3 시점의 "옵션 A" 설계다.
> v4에서 옵션 A의 **기술적 한계(launchd headless에서 Claude Code CLI 실행 불가)** 가 발견되어
> **Hybrid 구조(Stage 1 + Stage 2)로 재설계**됨. → **핵심 수정 10** 참조.
> 비용 원칙(Claude Max 범위 내, 추가 비용 없음)은 v4에서도 동일하게 유지됨.

### 문제 (v3 시점)

PRD Section 5.1: "Claude Max $200/월이 전부다. 추가 숨은 비용 없음."
v2 아이디어: `intelligence_engine.py`가 `anthropic` 라이브러리로 Claude API를 직접 호출.
→ Claude API 직접 호출은 별도 종량제 과금 발생 — PRD 비용 원칙과 충돌.

### v3 채택 (참고용) → v4에서 Hybrid로 재설계됨

```
[v2 방식 — 폐기]
python intelligence_engine.py → anthropic.Client().messages.create() → 종량제 청구

[v3 방식 — v4에서 Hybrid로 발전]
weekly_orchestrator.py 실행 중 → Claude Code 에이전트 자체를 활용 → 원고를 파일로 저장

[v4 방식 — 현행]
Stage 1: launchd가 순수 Python으로 데이터만 수집 (Claude Code 없음)
Stage 2: 사용자가 /weekly-report 실행 → Claude Code 인터랙티브 세션 → 원고 생성
```

**비용:** 추가 없음. Claude Max $200/월 범위 내 완전 포함. (v3, v4 동일)

---

## 핵심 수정 2: Category A/B 프롬프트 분리 설계

### 문제

절대 목표 [F]: "안정적 현재 종목과 미래 성장 테마를 **구분하여** 제공"
v2의 단일 프롬프트로는 두 카테고리가 동일한 분석 틀로 생성된다.

Category A와 B는 서술 방식 자체가 달라야 한다:

| 항목 | Category A (안정적 관찰) | Category B (미래 성장 테마) |
|------|----------------------|--------------------------|
| 분석 기반 | 현재 실적·밸류에이션 | TAM(전체 어드레서블 마켓)·성장 경로 |
| 수치 중심 | PER, 실적 YoY, 외국인 수급 | 테마 시장 규모, 성장률, 진입 타이밍 |
| 리스크 | 실적 하향, 밸류에이션 부담 | 테마 지속성, 경쟁 진입, 타이밍 오판 |
| 서술 톤 | "현재 상태 + 방향성" | "미래 가능성 + 불확실성" |

### v3 설계: 두 개의 독립 프롬프트

**Category A 프롬프트 (Step 5에서 설계):**

```python
CATEGORY_A_SYSTEM_PROMPT = """
당신은 한국 주식 시장 전문 퀀트 애널리스트입니다.
현재 섹터 모멘텀이 확인된 종목에 대해 실적·밸류에이션 기반 분석 원고를 작성합니다.

반드시 포함할 것:
- 최근 2분기 YoY 매출·영업이익 성장률 (수치 포함)
- 현재 PER vs 섹터 평균 비교 ("X배, 섹터 평균 대비 Y% 할인/프리미엄")
- 외국인 수급 방향 (4주 누적 순매수/순매도)
- 하방 리스크 1개 이상 (정량적 영향 서술)
- 방향성 의견: "긍정적 모멘텀 유지", "중립 관망", "리스크 구간" 중 택1

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

---

## 핵심 수정 3: 모듈 간 인터페이스 계약 (dataclass 스키마)

> Claude Code가 여러 Step에서 모듈을 구현할 때 필드명 불일치를 방지하기 위한 사전 계약.
> **Step 5 (Implementation Blueprint)에서 반드시 아래 스키마를 먼저 확정**하고,
> 모든 구현 모듈(Step 6~10)은 이 스키마를 준수한다.

### InvestmentMeta (synthesize_macro.py 출력)

```python
@dataclass(frozen=True, slots=True)
class SectorDirection:
    sector_name: str                  # 예: "반도체"
    direction: str                    # "Bullish" | "Neutral" | "Bearish"
    confidence: float                 # 0.0~1.0
    signal_count: int                 # 사용된 신호 수
    signal_ids: list[str]             # 근거 신호 ID 목록

@dataclass(frozen=True, slots=True)
class InvestmentMeta:
    report_date: str                  # "YYYY-MM-DD"
    sectors: list[SectorDirection]
    top_signals: list[UnifiedSignal]  # 상위 10개 신호
    macro_summary: str                # FRED 지표 요약 (텍스트)
    schema_version: str               # "investmeta-v1"
```

### StockAnalysisContext (synthesize_stock.py 출력)

```python
@dataclass(frozen=True, slots=True)
class DartFinancials:
    ticker: str                       # 예: "000660"
    name: str                         # 예: "SK하이닉스"
    revenue_yoy: float | None         # YoY 매출 성장률 (0.15 = +15%)
    op_income_yoy: float | None       # YoY 영업이익 성장률
    quarter: str                      # 예: "2025Q3"

@dataclass(frozen=True, slots=True)
class ValuationContext:
    ticker: str
    per: float | None                 # Price-Earnings Ratio
    pbr: float | None                 # Price-Book Ratio
    roe: float | None                 # Return on Equity
    sector_avg_per: float | None      # 섹터 평균 PER
    per_discount_pct: float | None    # (per - sector_avg_per) / sector_avg_per

@dataclass(frozen=True, slots=True)
class StockAnalysisContext:
    ticker: str
    name: str
    category: str                     # "A" | "B"
    sector: str
    foreign_flow_4w: float | None     # 4주 외국인 순매수 (억원)
    financials: DartFinancials | None
    valuation: ValuationContext | None
    theme_name: str | None            # Category B용 테마명
    theme_signals: list[str] | None   # Category B용 신호 ID
```

### NarrativeOutput (intelligence_engine.py 출력)

```python
# intelligence_engine.py가 output/temp/narrative_[날짜].json에 저장하는 스키마
{
  "report_date": "2026-03-31",
  "sector_narrative": "반도체 섹터는 이번 주 글로벌 AI 투자 확대...(3~5문단)",
  "causal_chains": [
    {"from": "CHIPS Act 예산 집행", "via": "TSMC 수주 +18%", "to": "SK하이닉스 HBM 계약 증가"}
  ],
  "stock_analyses": [
    {
      "ticker": "000660",
      "name": "SK하이닉스",
      "category": "A",
      "narrative": "SK하이닉스는 HBM4 공급 계약 3건 확보로...(2~3문단)",
      "key_metrics": [
        {"name": "Forward PER", "value": "12x", "context": "섹터 평균 대비 20% 할인"},
        {"name": "YoY 매출 성장률", "value": "+18%", "context": "2025Q3 기준"}
      ],
      "risks": ["HBM 공급 과잉 시 단가 하락 리스크 (영업이익 -10% 추정)"],
      "momentum_opinion": "긍정적 모멘텀 유지 중"
    }
  ],
  "category_b_analyses": [
    {
      "ticker": "247540",
      "name": "에코프로비엠",
      "category": "B",
      "theme": "유럽 배터리 공급망 재편",
      "narrative": "EU 핵심원자재법 시행으로 국내 배터리 소재 업체가...",
      "growth_drivers": ["EU 정책 강제화", "국내 소재 점유율 상승 가능성"],
      "risks": ["중국 LFP 경쟁 심화", "테마 소멸 가능성 (정책 지연)"],
      "theme_duration_estimate": "12~24주"
    }
  ],
  "bear_case": "반도체 섹터 방향 반전 시나리오: 미-중 반도체 제재 확대 시..."
}
```

---

## 핵심 수정 4: validate_report_quality.py — 7항목 통일 ⚠️ v4에서 8항목으로 확장

> **[v4 업데이트]** 이 섹션(v3 시점)은 7항목 기준이었으나, **핵심 수정 11**에서 8항목 + PRD 감산 모델로 재설계됨.
> 아래 코드는 **역사적 참고용**. 실제 구현 기준은 **핵심 수정 11** 참조.
>
> ~~v2의 "7항목 vs 11항목" 불일치를 해소. **7항목으로 통일.**~~

```python
def validate_report_quality(report_md: str, narrative_json: dict) -> dict:
    """PRD 핵심 목적 7개 항목 자동 검증"""
    checks = {
        # 1. 독립 소스 신호 ≥ 3개
        "independent_signals_3plus": _count_sources(report_md) >= 3,
        # 2. 각 신호에 출처 명시
        "each_signal_has_source": _all_have_source(report_md),
        # 3. 하방 리스크 신호 포함
        "downside_risk_exists": bool(re.search(r'하방 리스크|리스크|Bear Case', report_md)),
        # 4. 타임프레임 명시
        "timeframe_stated": bool(re.search(r'4.{0,3}12주|4주|12주', report_md)),
        # 5. 이번 주 행동 포함
        "action_item_exists": "이번 주 행동" in report_md,
        # 6. 인과 논리 체인 2단계 이상
        "causal_chain_exists": _has_causal_chain(narrative_json),
        # 7. Bear Case 포함
        "bear_case_exists": bool(narrative_json.get("bear_case", "")),
    }
    score = sum(checks.values()) / 7
    passed = score >= (5/7)  # 5/7 이상 통과 (첫 2회 평균 기준, PRD Section 13.7)
    return {"score": score, "passed": passed, "details": checks}
```

### 헬퍼 함수 구현 전략 (정규식 기반)

```python
def _count_sources(report_md: str) -> int:
    """출처 패턴 카운트: (출처: X) 또는 #숫자 형식"""
    patterns = [r'\(출처:', r'출처:', r'신호 #\d+', r'\[신호']
    found = set()
    for p in patterns:
        found.update(re.findall(p, report_md))
    return len(found)

def _all_have_source(report_md: str) -> bool:
    """신호 언급이 있으면 출처도 있는지 확인"""
    signal_blocks = re.findall(r'신호.*?\n', report_md)
    if not signal_blocks:
        return True
    return all(re.search(r'출처|DigiTimes|전자신문|DART|FDR', b) for b in signal_blocks)

def _has_causal_chain(narrative_json: dict) -> bool:
    """NarrativeOutput의 causal_chains 필드 확인 (Claude Code 생성 결과)"""
    chains = narrative_json.get("causal_chains", [])
    return len(chains) >= 1 and all(c.get("from") and c.get("to") for c in chains)
```

**판정:** `causal_chains`는 정규식이 아닌 **NarrativeOutput JSON에서 직접 확인**한다. intelligence_engine.py(Claude Code)가 생성한 JSON에 `causal_chains` 배열이 있으면 통과. 텍스트 패턴 의존 없음.

---

## 핵심 수정 5: intelligence_engine.py 장애 처리

### 장애 유형별 처리 전략

```python
# intelligence_engine.py (옵션 A 방식 재정의)
# Claude Code 에이전트 방식이므로 실제 API 호출 실패는 세션 레벨에서 처리됨.
# 하지만 원고 생성 결과 파일 누락/빈 파일 상황은 별도 처리 필요.

def check_narrative_output(narrative_path: Path) -> str:
    """원고 파일 존재 + 유효성 확인"""
    if not narrative_path.exists():
        return "missing"
    try:
        data = json.loads(narrative_path.read_text())
        if not data.get("sector_narrative") or not data.get("stock_analyses"):
            return "empty"
        return "ok"
    except json.JSONDecodeError:
        return "invalid"

# weekly_orchestrator.py에서 처리
status = check_narrative_output(narrative_path)
if status == "ok":
    # 정상 경로: intelligence_engine 원고 사용
    pass
elif status in ("missing", "empty", "invalid"):
    # Fallback: v1 파이프라인 (Jinja2 + 수치 조합만, 원고 없음)
    logger.warning(f"Intelligence engine 원고 없음 ({status}). v1 fallback 실행.")
    send_telegram("⚠️ 이번 주 리포트는 분석 원고 없이 기본 형식으로 발송됩니다. 수치 데이터는 정상 포함.")
    use_fallback_template = True
```

**Fallback 파이프라인 (원고 생성 실패 시):**
intelligence_engine.py 원고 없이도 리포트를 생성한다. 품질은 낮지만 침묵 실패 방지.
- 섹터 방향 + 신뢰도 수치 → 표 형식으로 출력
- 워치리스트 종목 + 수치 → 리스트 형식으로 출력
- "이번 주 분석 원고 생성에 문제가 있었습니다. 다음 주 정상화 예정." 문구 포함

---

## 핵심 수정 6: Jinja2 템플릿 변수 매핑 (명시적 계약)

> intelligence_engine.py(Claude Code)가 생성한 `NarrativeOutput JSON` 키와
> Jinja2 템플릿 변수가 1:1 대응되어야 한다.

```jinja2
{# templates/weekly-report.md.j2 #}

## 분석 타임프레임 안내
이 신호는 **4–12주 방향성**입니다. 단기 등락 예측 아님.

## 이번 주 행동 1가지
→ {{ action_item }}

## 섹터 방향 요약
{% for s in sectors %}
• {{ s.sector_name }}: {{ s.direction_icon }} {{ s.direction_ko }} ({{ s.confidence_pct }}%)
{% endfor %}

## 섹터별 상세 분석
{{ sector_narrative }}  {# NarrativeOutput.sector_narrative #}

## 인과 논리 체인
{% for chain in causal_chains %}  {# NarrativeOutput.causal_chains #}
{{ chain.from }} → {{ chain.via }} → {{ chain.to }}
{% endfor %}

## Bear Case
{{ bear_case }}  {# NarrativeOutput.bear_case #}

## 종목 관찰 워치리스트 — Category A (안정적 관찰)
{% for stock in category_a_stocks %}
[{{ stock.name }} {{ stock.ticker }}]
{{ stock.narrative }}  {# NarrativeOutput.stock_analyses[i].narrative #}
{% for m in stock.key_metrics %}
  • {{ m.name }}: {{ m.value }} ({{ m.context }})
{% endfor %}
  하방 리스크: {% for r in stock.risks %}{{ r }}{% endfor %}
  방향성: {{ stock.momentum_opinion }}
  ⚠️ 이 목록은 투자 권고가 아닌 데이터 기반 관찰 목록입니다.
{% endfor %}

## 종목 관찰 워치리스트 — Category B (미래 성장 테마)
{% for stock in category_b_stocks %}
[{{ stock.name }} {{ stock.ticker }} — 테마: {{ stock.theme }}]
{{ stock.narrative }}  {# NarrativeOutput.category_b_analyses[i].narrative #}
  테마 지속 예상: {{ stock.theme_duration_estimate }}
  하방 리스크: {% for r in stock.risks %}{{ r }}{% endfor %}
  ⚠️ 이 목록은 투자 권고가 아닌 데이터 기반 관찰 목록입니다.
{% endfor %}

## 이번 주 행동 체크리스트
{% for item in action_checklist %}
  ☐ {{ item }}
{% endfor %}

{% if all_bullish_3weeks %}
⚠️ 3주 연속 전 섹터 긍정 감지. 하방 리스크를 재검토하세요.
{% endif %}

---
{% if publish_platform == "blog" or publish_platform == "external" %}
⚠️ **[외부 게시용 강화 면책 조항]**
이 리포트는 공개된 데이터 소스(DART, FRED, FinanceDataReader, EnvironmentScan)를
AI가 자동 분석한 **정보 제공용** 자료이며, 「자본시장과 금융투자업에 관한 법률」상
투자자문업 등록을 하지 않은 개인이 작성한 비전문가 의견입니다.
특정 종목의 **매수·매도·보유를 권고하지 않으며**, 본 자료를 근거로 한
모든 투자 결정과 그에 따른 손익에 대해 작성자는 법적 책임을 지지 않습니다.
투자 결정 전 **공인 금융투자전문가 상담**을 권장합니다.
{% else %}
⚠️ **[개인 투자 참고용]**
이 리포트는 데이터 분석 정보이며 투자 권유가 아닙니다.
최종 투자 결정은 본인 책임입니다.
{% endif %}
```

**Jinja2 → NarrativeOutput 변수 매핑 테이블:**

| Jinja2 변수 | NarrativeOutput JSON 키 | 소스 모듈 |
|-----------|------------------------|---------|
| `sector_narrative` | `sector_narrative` | intelligence_engine |
| `causal_chains` | `causal_chains` | intelligence_engine |
| `bear_case` | `bear_case` | intelligence_engine |
| `category_a_stocks[i].narrative` | `stock_analyses[i].narrative` | intelligence_engine |
| `category_b_stocks[i].narrative` | `category_b_analyses[i].narrative` | intelligence_engine |
| `sectors` | InvestmentMeta.sectors | synthesize_macro |
| `action_item` | 규칙 기반 생성 | synthesize_macro |

---

## 핵심 수정 7: HITL-1 수정 — Claude API Key 입력 추가

HITL-1에 Claude API Key 조달 절차가 반드시 포함되어야 한다.
(옵션 A 채택으로 Claude Code 에이전트 방식이지만, Claude Max 로그인 상태 확인이 필요)

### HITL-1 (Planning 완료 후) — v4 수정

> **비코더 안내 원칙**: Claude Code가 각 항목을 **대화형으로 단계별 안내**한다.
> 사용자가 한 번에 모든 것을 입력할 필요 없음. 항목마다 설명 + 예시 제공.

```
[Claude Code 안내 방식]
"지금부터 InvestScan 설정을 단계별로 도와드리겠습니다.
 각 단계마다 제가 무엇을 해야 하는지 안내해 드릴게요. 준비되셨으면 시작할게요!"

확인 항목:

1. Claude Max 로그인 확인
   → Claude Code가 현재 실행 중이면 OK (이미 완료된 상태입니다)

2. EnvironmentScan 경로: [자동 탐색 결과]
   → "이 경로가 맞으면 '네', 다르면 폴더를 Finder에서 드래그하여 경로를 알려주세요."

3. Telegram 봇 토큰 입력
   → "텔레그램 앱에서 @BotFather를 찾아 /newbot을 입력하세요.
      발급받은 토큰(예: 123456789:ABC-DEF...)을 여기에 붙여넣어 주세요."
   → Claude Code가 자동으로 Keychain에 안전하게 저장 처리

4. 관심 섹터 (기본값: 반도체·IT서비스·바이오)
   → "변경하고 싶은 섹터가 있으면 말씀해주세요. 없으면 기본값으로 진행합니다."

5. 완성본 활용 방식
   [A] 개인 투자 판단용 (내부 보관) ← 기본값
   [B] 블로그/브런치 게시용 (Markdown → HTML 변환)
   [C] Obsidian / Notion 노트 앱 연동
   → 선택에 따라 출력 형식 자동 최적화

6. (선택) 매주 특별히 포함하고 싶은 종목이 있으신가요?
   → "없으면 그냥 Enter 누르세요. 시스템이 자동으로 선정합니다."
```

---

## 핵심 수정 8: HITL-3 실패 후 재조정 루프 — Step 구조에 반영

### 수정된 Implementation Phase 구조

```
Step 9:  Phase 4 — Intelligence Engine
Step 10: Phase 5 — Report & Watchlist + validate_report_quality.py
         ↓ validate_report_quality.py 자동 검증 (7항목)
         → 5/7 미만: Step 10-R로 이동 (재조정 루프)
         → 5/7 이상: HITL-3 진행
         ↓ (human) HITL-3 — 완성본 평점 (1~5점)
         → 3점 미만: Step 10-R로 이동
         → 3점 이상: Step 11 진행

[Step 10-R: 원고 재조정 루프 — 최대 2회]
Step 10-R: Prompt Refinement + Regeneration
  입력: validate_report_quality.py 미충족 항목 목록 + 사용자 피드백
  처리: Category A/B 프롬프트 조정 → intelligence_engine.py 재실행 → 재검증
  제한: 최대 2회 (2회 후에도 3점 미만 시 Claude Code가 사용자와 개선 세션 진행)
  state.yaml: refinement_count 기록
```

---

## 핵심 수정 9: 종목 자동 선정 로직 — stock_selector.py 신설

> 4차 적대적 검토 발견: "어떤 종목을 분석할 것인가" 결정 로직이 완전 누락.
> 사용자가 매주 종목을 직접 지정해야 한다면 "최소 입력" 약속 위반.

### 설계: stock_selector.py (~150 LOC)

```python
# stock_selector.py — synthesize_macro.py 결과를 받아 분석 대상 종목 자동 선정

# Category A: 섹터 방향 Bullish & confidence >= 0.65인 섹터에서
#              FDR 외국인 순매수 상위 3개 종목 선정 (KOSPI200 + KOSDAQ150 유니버스)
# Category B: Bullish 섹터 테마 신호 중 score 상위 3개 신호의 주요 수혜 종목
#              (signal_bridge.py GICS 매핑 결과 기반)
# 최대 선정: Category A 5개 + Category B 3개 (총 8개)
# 동일 종목 중복 방지: Category A에 있으면 B에서 제외

def select_stocks(
    investment_meta: InvestmentMeta,
    watchlist_override: list[str] | None = None  # HITL-1에서 사용자 수동 지정 옵션
) -> tuple[list[str], list[str]]:
    """
    Returns: (category_a_tickers, category_b_tickers)
    watchlist_override: 사용자가 특정 종목을 강제 포함할 때 사용 (HITL-1 선택 항목)
    """
    bullish_sectors = [s for s in investment_meta.sectors if s.direction == "Bullish" and s.confidence >= 0.65]
    # Category A: 외국인 수급 기반 자동 선정
    cat_a = _get_top_foreign_flow_tickers(bullish_sectors, top_n=5)
    # Category B: 테마 신호 기반 자동 선정
    cat_b = _get_theme_tickers(investment_meta.top_signals, exclude=cat_a, top_n=3)
    # 수동 지정 종목 우선 삽입
    if watchlist_override:
        cat_a = watchlist_override[:5] + [t for t in cat_a if t not in watchlist_override][:max(0, 5-len(watchlist_override))]
    return cat_a[:5], cat_b[:3]
```

### state.yaml 추가 필드 (stock_selection 섹션)
```yaml
stock_selection:
  category_a: []       # ["000660", "005930", ...]  — 자동 선정 결과
  category_b: []       # ["247540", "373220", ...]
  selected_at: ""      # ISO 8601
  manual_override: false
  watchlist_override: []  # HITL-1에서 사용자 수동 추가 종목
```

### HITL-1 추가 항목
```
5. (선택) 특별히 분석하고 싶은 종목이 있으신가요?
   → 종목명 또는 코드 입력 (없으면 Enter — 자동 선정 사용)
```

---

## 핵심 수정 10: Option A 재설계 — Hybrid 자동화 구조 (M0.5 적용)

> **[v4 D1 적용]** 이 섹션은 **M0.5 Hybrid 구조** 설계다. M1 완전 자동화는 → **핵심 수정 15** 참조.
>
> 4차 적대적 검토 발견: Claude Code CLI를 launchd headless subprocess로 실행하는 것은 기술적으로 불안정.
> OAuth 인증 갱신 불가, TTY 없음, 환경변수 격리, Hook 스크립트 충돌 가능성.

### 문제

v3 Option A 방식: `launchd → weekly_orchestrator.py → subprocess("claude") → intelligence_engine 호출`
→ headless 환경에서 Claude Code CLI는 인증 필요, TTY 의존, 환경변수 격리로 실질 작동 불가.

### 채택: Hybrid 방식 (2단계 자동화 구조)

```
[Stage 1: 데이터 수집 자동화 — launchd, 순수 Python, Claude Code 없음]
─────────────────────────────────────────────────────────────────
일요일 20:00 launchd 실행: weekly_orchestrator.py --mode data-only
  ├── EnvironmentScan 결과 읽기 (database.json — 이미 별도 생성됨)
  ├── GlobalNews 결과 읽기 (signals.parquet — 이미 별도 생성됨)
  ├── FRED API 호출 (순수 Python requests)
  ├── DART + pykrx + FDR 호출 (순수 Python)
  ├── synthesize_macro.py 실행 (순수 Python, LLM 없음, 감성 0%)
  ├── stock_selector.py 실행 (종목 자동 선정)
  ├── synthesize_stock.py + valuation_comparator.py (순수 Python)
  ├── 모든 컨텍스트를 output/context/context_[날짜].json에 저장
  └── Telegram 알림:
      "📊 InvestScan 데이터 수집 완료!
       분석 섹터: 반도체(Bullish) / IT서비스(Neutral)
       선정 종목: A등급 5개, B등급 3개
       ✅ Claude Code에서 /weekly-report 실행하세요. (~10분 소요)"

[Stage 2: 리포트 생성 — 사용자 트리거, Claude Code 인터랙티브 세션]
─────────────────────────────────────────────────────────────────
사용자: Claude Code 열기 → /weekly-report 실행 (단 1회 명령, ~10분 대기)
  intelligence_engine.py (Claude Code 에이전트 자체):
  ├── output/context/context_[날짜].json 읽기
  ├── Category A/B 분리 프롬프트로 원고 생성
  ├── narrative_[날짜].json 저장
  ├── validate_report_quality.py 자동 검증 (8항목)
  └── report_generator.py → Jinja2 조립 → HITL-3 체크리스트 제시
```

### Hybrid 방식 근거
| 기준 | 이유 |
|------|------|
| **Stage 1 headless 작동** | 순수 Python (requests, pandas, pykrx, FDR)만 사용. Claude Code 없음. launchd에서 완전 작동. |
| **Stage 2 Claude Code 활용** | 인터랙티브 세션 → OAuth 인증 유지, TTY 정상, 파라미터 제어 가능. |
| **비용 없음** | Stage 2가 Claude Max 범위 내. 추가 API 비용 없음. |
| **사용자 입력 최소** | Telegram 알림 수신 → Claude Code 열기 → /weekly-report 입력 (30초 작업). |

### Stage 1 launchd plist 보안 설계
```xml
<!-- API 키: plist 평문 저장 금지. Python 코드에서 Keychain 동적 로드. -->
<key>WorkingDirectory</key>
<string>/Users/[username]/investscan</string>
<key>StandardOutPath</key>
<string>/Users/[username]/investscan/logs/orchestrator.log</string>
<key>StandardErrorPath</key>
<string>/Users/[username]/investscan/logs/orchestrator_err.log</string>
```
`config.py`가 실행 시 `security find-generic-password -a investscan -s [키이름] -w`로 Keychain에서 직접 로드.

---

## 핵심 수정 11: validate_report_quality.py 개선 (8항목 + PRD 감산 모델)

> 4차 적대적 검토 발견: (1) 모든 항목이 형식 검증 — 수치 정확성 검증 없음
> (2) PRD "미충족 항목당 신뢰도 -5% 감산 후 발송" 모델을 이진 판정으로 변경 → PRD 충돌

### 수정된 validate_report_quality.py (7항목 → 8항목)

```python
def validate_report_quality(
    report_md: str,
    narrative_json: dict,
    context_data: dict  # Stage 1에서 생성된 context_[날짜].json
) -> dict:
    """PRD 핵심 목적 + 수치 정확성 검증 (8항목)"""
    checks = {
        "independent_signals_3plus":  _count_sources(report_md) >= 3,
        "each_signal_has_source":      _all_have_source(report_md),
        "downside_risk_exists":        bool(re.search(r'하방 리스크|리스크|Bear Case', report_md)),
        "timeframe_stated":            bool(re.search(r'4.{0,3}12주|4주|12주', report_md)),
        "action_item_exists":          "이번 주 행동" in report_md,
        "causal_chain_exists":         _has_causal_chain(narrative_json),
        "bear_case_exists":            bool(narrative_json.get("bear_case", "")),
        "key_metrics_consistent":      _verify_metrics_consistency(report_md, context_data),  # v4 신규
    }
    # PRD 모델: 미충족 항목당 신뢰도 -5% 감산 후 발송 (이진 pass/fail 아님)
    score = sum(checks.values()) / 8
    confidence_penalty = sum(1 for v in checks.values() if not v) * 0.05
    adjusted_confidence = max(0.0, 1.0 - confidence_penalty)
    passed = score >= (5/8)

    return {
        "score": score,
        "passed": passed,
        "adjusted_confidence": adjusted_confidence,
        "confidence_penalty": confidence_penalty,
        "details": checks,
        "delivery_mode": "normal" if score >= (7/8) else ("with_warning" if passed else "reloop"),
    }

def _verify_metrics_consistency(report_md: str, context_data: dict) -> bool:
    """원고의 주요 수치가 context_data와 일치하는지 샘플 검증 (최대 3개 종목, ±20% 허용)"""
    stock_contexts = context_data.get("stock_contexts", [])[:3]
    for stock in stock_contexts:
        ticker = stock.get("ticker", "")
        per = stock.get("valuation", {}).get("per")
        if per and ticker:
            match = re.search(rf'{ticker}.*?PER.*?(\d+\.?\d*)', report_md)
            if match:
                reported_per = float(match.group(1))
                if abs(reported_per - per) / per > 0.20:
                    return False
    return True
```

### 발송 모드 3단계
| 조건 | delivery_mode | 동작 |
|------|--------------|------|
| 8/8 또는 7/8 통과 | `"normal"` | 신뢰도 100% 표기로 정상 발송 |
| 5~6/8 통과 | `"with_warning"` | Jinja2에서 `⚠️ 품질 경고` 배너 포함 발송 |
| 5/8 미만 | `"reloop"` | Step 10-R 재조정 루프 진입 |

---

## 핵심 수정 12: accuracy_tracker.py 상세 설계

> 4차 적대적 검토 발견: PRD의 6가지 상세 명세 전면 누락
> (predictions.jsonl 스키마, 벤치마크 ETF, Naive Baseline, 가중치 조정 알고리즘)

### PredictionRecord 스키마

```python
@dataclass(frozen=True, slots=True)
class PredictionRecord:
    report_week: str           # "2026-W13"
    sector: str                # "반도체"
    direction: str             # "Bullish" | "Neutral" | "Bearish"
    confidence: float          # 0.0~1.0
    signal_ids: list[str]      # 근거 신호 ID 목록
    created_at: str            # ISO 8601
    # 4주 후 FDR 조회 후 채워짐:
    actual_etf_return: float | None   # 4주 후 벤치마크 ETF 수익률 (0.05 = +5%)
    hit: bool | None           # True: 방향 일치 (실제 수익률이 +2% 이상이면 Bullish 적중)
    evaluated_at: str | None
```

저장 경로: `data/accuracy/predictions.jsonl` (줄당 1개 JSON 레코드)

### 벤치마크 ETF (PRD 13.3.1 기반)
| 섹터 | ETF 이름 | 코드 |
|------|---------|------|
| 반도체 | KODEX 반도체 | 091160 |
| IT서비스 | KODEX IT | 098560 |
| 헬스케어 | KODEX 헬스케어 | 266410 |
| 2차전지 | KODEX 2차전지산업 | 305720 |

### Naive Baseline 비교 (PRD 13.1)
```python
def calculate_naive_baseline(records: list[PredictionRecord]) -> float:
    """Always-Bullish 가상 전략 적중률 — InvestScan 예측과 비교하는 기준선"""
    hits = sum(1 for r in records if r.actual_etf_return and r.actual_etf_return >= 0.02)
    return hits / len(records) if records else 0.0
```

### 월간 정확도 리포트 형식 (Telegram 발송)
```
📈 InvestScan 월간 정확도 리포트 (2026년 3월)
───────────────────────────────────
반도체: 3/4 예측 적중 (75%) | Always-Bullish: 50%
IT서비스: 2/4 (50%) | Always-Bullish: 50%
바이오: 1/4 (25%) | Always-Bullish: 50%
───────────────────────────────────
전체 적중률: 55% | Always-Bullish 대비: +5%
⚠️ 바이오 섹터 신호 품질 재검토 권장
다음 가중치 자동 조정 제안 확인하시겠습니까? [Y/N]
```

---

## 핵심 수정 13: watchdog.py 상세 설계

> 4차 적대적 검토 발견: PRD의 성공/실패 메시지 분기, 지연 감지 pseudo-code 전무.
> 비코더에게 기술 에러 메시지는 행동 불가 → 한국어 평문 가이드 필수.

### 성공/실패 Telegram 메시지 형식

```python
# 성공 시 (월요일 08:00 고정 발송)
SUCCESS_MSG = """✅ InvestScan 데이터 수집 완료
──────────────────────────────
수집 완료: {data_date} {data_time}
선정 종목: A등급 {cat_a_count}개, B등급 {cat_b_count}개
분석 섹터: {sector_summary}
──────────────────────────────
📌 Claude Code를 열고 /weekly-report를 실행하세요. (약 10분 소요)"""

# 실패 시 (월요일 08:00 고정 발송)
FAILURE_MSG = """⚠️ InvestScan 데이터 수집 실패
──────────────────────────────
{action_guide}
──────────────────────────────
더 도움이 필요하면: Claude Code를 열고 상황을 말씀해주세요."""

# 기술 에러 → 한국어 평문 행동 가이드 매핑
FAILURE_GUIDE = {
    "DART_API_ERROR":   "주식 실적 데이터 수집에 실패했습니다. 이번 주는 수익성 수치 없이 리포트가 생성됩니다.",
    "PYKRX_ERROR":      "주가 데이터 수집에 실패했습니다. 다음 주에 자동으로 다시 시도합니다.",
    "ENVSCAN_STALE":    "분석 신호 데이터가 3일 이상 오래됩니다. EnvironmentScan을 먼저 실행해주세요.",
    "DISK_SPACE":       "저장 공간이 부족합니다. 오래된 리포트(~/investscan/output/reports/) 몇 개를 삭제해주세요.",
    "NETWORK_ERROR":    "인터넷 연결이 불안정했습니다. 연결 확인 후 Claude Code에서 /weekly-report를 실행하세요.",
    "GNEWS_MISSING":    "글로벌 뉴스 파일이 없습니다. 국내 데이터만으로 분석이 진행됩니다.",
}
```

### 지연 실행 감지 로직 (PRD 11.6)
```python
LAST_RUN_FILE = Path("logs/last_successful_run.txt")
STALE_THRESHOLD_DAYS = 8  # 8일 이상 미실행 시 경고

def check_staleness() -> None:
    """매주 월요일 08:00 실행 — 마지막 성공 실행으로부터 경과일 확인"""
    if not LAST_RUN_FILE.exists():
        send_telegram("⚠️ InvestScan이 아직 한 번도 실행되지 않았습니다. Claude Code에서 /weekly-report 실행을 시작해주세요.")
        return
    last_run = datetime.fromisoformat(LAST_RUN_FILE.read_text().strip())
    days_since = (datetime.now() - last_run).days
    if days_since >= STALE_THRESHOLD_DAYS:
        send_telegram(f"⚠️ {days_since}일 동안 InvestScan이 실행되지 않았습니다. 확인이 필요합니다.")
```

### Stage 1 완료 시 last_successful_run.txt 업데이트
```python
# weekly_orchestrator.py Stage 1 완료 후
LAST_RUN_FILE.write_text(datetime.now().isoformat())
```

---

## 핵심 수정 14: HITL-3 체크리스트 방식으로 변경

> 4차 적대적 검토 발견: 비코더 목사님이 투자 분석 품질을 1~5점으로 평가하는 것은
> 실질적 판단 불가. 전문 지식 없이 "3점인지 4점인지"는 형식 승인일 뿐.

### 수정된 HITL-3 (점수 → 체크리스트)

```
[HITL-3] 완성본 검수 체크리스트

아래 5가지를 확인해주세요:

[ ] 1. 내가 관심 있는 섹터(반도체/IT 등)가 포함되어 있나요?
[ ] 2. "이번 주 행동" 항목이 명확하게 나와 있나요?
[ ] 3. 각 종목에 위험(리스크) 설명이 있나요?
[ ] 4. 숫자들이 대략 맞아 보이나요? (크게 이상한 수치가 없나요?)
[ ] 5. 전반적으로 읽기 편하게 작성되었나요?

→ 4개 이상 "예": 정상 발송 ✅
→ 3개 이하 "예": 가장 어색한 부분을 말씀해주세요 → Step 10-R 개선
```

**체크리스트 설계 원칙**:
- 비코더도 "예/아니오"로 답할 수 있는 질문만
- 투자 전문 지식 불필요
- 5개 질문이 실제 품질 측면 커버: 커버리지, 행동가능성, 위험인식, 수치신뢰, 가독성

---

## 핵심 수정 15: M1 완전 자동화 설계 (D1 확정 — Anthropic API 직접 호출)

> **D1 확정**: M0.5 = Hybrid(사용자 /weekly-report 트리거), M1 = 완전 자동(Anthropic API 직접 호출).
> M1에서는 `intelligence_engine.py`가 `anthropic` 라이브러리로 Claude API를 직접 호출하여
> launchd 일정에서 원고 생성·발송까지 사용자 개입 없이 완전 자동 실행된다.

### M1 intelligence_engine.py — Anthropic API 직접 호출

```python
# intelligence_engine.py (M1 버전 — Anthropic API 직접 호출)
import anthropic
from pathlib import Path
import json

def generate_narrative(context_json_path: Path) -> dict:
    """
    Stage 1 context JSON을 읽고 Claude API로 원고 생성 (M1 완전 자동 모드).
    모델 고정: claude-opus-4-6 (결과 일관성 보장)
    temperature: 0.3 (창의성↓ 정확성↑)
    """
    context = json.loads(context_json_path.read_text())

    client = anthropic.Anthropic()  # API 키: macOS Keychain에서 동적 로드

    # Category A 원고 생성
    cat_a_response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        temperature=0.3,
        system=CATEGORY_A_SYSTEM_PROMPT,  # 핵심 수정 2 참조
        messages=[{
            "role": "user",
            "content": f"Context:\n{json.dumps(context['cat_a_contexts'], ensure_ascii=False, indent=2)}"
        }]
    )

    # Category B 원고 생성
    cat_b_response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        temperature=0.3,
        system=CATEGORY_B_SYSTEM_PROMPT,  # 핵심 수정 2 참조
        messages=[{
            "role": "user",
            "content": f"Context:\n{json.dumps(context['cat_b_contexts'], ensure_ascii=False, indent=2)}"
        }]
    )

    narrative = _parse_and_assemble(cat_a_response, cat_b_response, context)
    return narrative
```

### M0.5 vs M1 자동화 비교

| 항목 | M0.5 (Hybrid) | M1 (완전 자동) |
|------|-------------|--------------|
| Stage 1 데이터 수집 | launchd 자동 (순수 Python) | launchd 자동 (순수 Python) |
| Stage 2 원고 생성 | 사용자 `/weekly-report` 트리거 | launchd 자동 (Anthropic API) |
| 사용자 개입 | Telegram 수신 후 Claude Code 실행 (~30초) | 없음 (완전 자동) |
| 추가 비용 | 없음 (Claude Max 범위 내) | ~$0.06~0.15/회, ~$1~3/월 |
| 구현 시기 | 먼저 2주 운용 | HITL-2 승인 후 전환 |
| HITL-3 | 인터랙티브 세션에서 직접 | Telegram 기반 비동기 (선택) |

### 비용 투명성

| 항목 | 수치 |
|------|------|
| claude-opus-4-6 입력 토큰 단가 | $15 / 1M tokens |
| claude-opus-4-6 출력 토큰 단가 | $75 / 1M tokens |
| 예상 입력 (context JSON ~8K tokens/회) | ~$0.12/회 |
| 예상 출력 (원고 A+B ~4K tokens/회) | ~$0.30/회 |
| **예상 비용/회 (합계)** | **~$0.06~0.15** |
| **예상 비용/월 (4회 실행)** | **~$1~3** |

> ⚠️ M0.5는 추가 비용 없음(Claude Max 포함). M1 전환 시 위 비용 발생.
> **HITL-2에서 M1 전환 전 사용자에게 비용 고지 및 동의 확인 필수.**

### M0.5 → M1 전환 절차

```
HITL-2 선택 후:

  [A] "M1 계속 진행" 선택 시:
    → Step 7+ 구현 중 intelligence_engine.py M1 버전으로 교체
    → launchd plist에 --mode full-auto 파라미터 설정
    → weekly_orchestrator.py에 generate_narrative() 직접 호출 통합
    → Anthropic API 키를 macOS Keychain에 등록
        security add-generic-password -a investscan -s anthropic_api_key -w [KEY]

  [B] "2주 M0.5 사용 후 M1" 선택 시:
    → state.yaml hitl_2.choice_date 기록
    → watchdog.py가 14일 경과 시 Telegram 알림:
        "M1 전환 준비됐습니다. Claude Code에서 /weekly-report 실행하세요."
    → 사용자 확인 후 M1 전환 실행
```

### launchd plist 업데이트 (M1 전환 시)

```xml
<!-- M0.5: --mode data-only  →  M1: --mode full-auto -->
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/[username]/investscan/weekly_orchestrator.py</string>
    <string>--mode</string>
    <string>full-auto</string>
</array>
```

`weekly_orchestrator.py --mode full-auto` 실행 흐름:
1. Stage 1: 순수 Python 데이터 수집 → context_[날짜].json
2. Stage 2: `generate_narrative(context_path)` 호출 → narrative_[날짜].json
3. `validate_report_quality.py` 8항목 검증
4. `report_generator.py` → Jinja2 → 완성본 Markdown
5. Telegram 발송 + HITL-3 체크리스트 옵션 포함 (비동기)
6. `accuracy_tracker.py` PredictionRecord 저장

---

## 전체 Phase 구조 (v4 최종)

```
Research Phase (3 Step)
  Step 1:  Environment Pre-flight       — 자동 환경 점검
  Step 2:  Schema Analysis + 조정       — 실제 스키마 파악 + PRD-vs-실제 결정 → state.yaml
  Step 3:  Dependency Validation        — 패키지 설치 + make_fixtures.py 생성

Planning Phase (2 Step)
  Step 4:  Path & Config + 완성본 정의  — investscan.yaml + 게시 플랫폼 확인
  Step 5:  Blueprint + 프롬프트 설계    — 모듈 설계도 + Category A/B 프롬프트 확정
                                          + dataclass 스키마 확정 + few-shot 작성
           ↓ (human) HITL-1            — Claude Max 확인 + 경로 + Telegram 토큰 + 섹터 + 게시처
                                          + 종목 수동 추가 여부 (선택사항)

Implementation Phase (10 Step)
  Step 6:  Phase 1 — M0.5 Core         — 5개 모듈 + compliance_filter.py
           ↓ (human) HITL-2            — Telegram 수신 확인 + M1 계속 / 2주 사용 선택
  Step 7:  Phase 2 — GlobalNews        — normalizers 확장, dedup, steeps_classifier
  Step 8:  Phase 3 — Korea Signal      — korea_signal_layer, signal_bridge, synthesize_macro,
                                          stock_selector.py (종목 자동 선정)
  Step 9:  Phase 4 — Intelligence      — synthesize_stock.py, valuation_comparator.py,
                                          intelligence_engine.py
                                          (M0.5: Claude Code 인터랙티브 / M1: Anthropic API 직접 호출)
  Step 10: Phase 5 — Report + Validate — report_generator, Jinja2, validate_report_quality(8항목),
                                          accuracy_tracker (상세 설계), watchdog (상세 설계)
  Step 10-R: [조건부] Prompt Refinement — 자동 검증 미달(5/8 미만) 또는 HITL-3 체크리스트 3개 미만 시만 실행
           ↓ (human) HITL-3            — validate 통과 후 완성본 체크리스트 (5개 예/아니오 질문)
  Step 11: Phase 6 — Automation        — Stage 1(launchd, Python-only 자동화) +
                                          Stage 2(/weekly-report Claude Code 명령) +
                                          health_dashboard
  Step 12: M1 Final Validation         — 완성본 체크리스트 + M1 최종 인수 기준
  Step 13: Handoff                     — 실행방법.txt + weekly-run.md 자동 생성

[자동화 구조 요약 — M0.5 vs M1]
  ─────────────────────────────────────────────────────
  M0.5 (Hybrid — HITL-2 이전까지):
    Stage 1 (launchd 일요일 20:00): 데이터 수집 전용 (순수 Python, Claude Code 없음)
      → 완료 후 Telegram 알림 "데이터 수집 완료, /weekly-report 실행하세요"
    Stage 2 (사용자 트리거): Claude Code 인터랙티브 세션
      → /weekly-report 실행 → 원고 생성 → HITL-3 → 발송
  ─────────────────────────────────────────────────────
  M1 (완전 자동 — HITL-2 승인 후, 핵심 수정 15 참조):
    Stage 1 (launchd 일요일 20:00): 데이터 수집 (동일)
    Stage 2 (launchd 연속 실행): Anthropic API 직접 호출 → 원고 생성 → 발송
      → 사용자 개입 없음 (HITL-3는 Telegram 비동기 옵션)
      → 추가 비용: ~$1~3/월
```

---

## 아이디어 1: Research Phase 설계 (v4 — D2 Step 1 자동 감지 추가)

### Step 1 — Environment Pre-flight (D2: 전제 조건 자동 감지)

> **D2 확정**: EnvironmentScan/GlobalNews 존재 여부를 **자동 감지**하고,
> 없을 경우 **독립 실행 모드(fallback)**로 자동 전환한다. 사용자가 경로를 수동 확인할 필요 없음.

```python
# Step 1 환경 점검 pseudo-code
def environment_preflight(config: Config) -> PreflightResult:
    """
    전제 조건 자동 감지 → 3가지 실행 모드 중 하나 선택.
    """
    envscan_found = _detect_envscan(config.envscan_search_paths)
    gnews_found = _detect_gnews(config.gnews_search_paths)

    if envscan_found and gnews_found:
        mode = "full"           # 전체 신호 파이프라인
    elif envscan_found and not gnews_found:
        mode = "envscan_only"   # EnvironmentScan만 사용 (GlobalNews 없음)
    else:
        mode = "independent"    # 두 소스 모두 없음 → FRED + DART + pykrx만으로 실행

    state_yaml_write({
        "discovered_paths": {
            "envscan_wf1_output": envscan_found or "",
            "gnews_signals": gnews_found or "",
        },
        "runtime_mode": mode,    # state.yaml에 기록
    })

    # 독립 실행 모드 fallback 알림
    if mode == "independent":
        send_telegram(
            "⚠️ EnvironmentScan·GlobalNews 파일을 찾지 못했습니다.\n"
            "FRED + DART + pykrx 데이터만으로 매크로 분석을 진행합니다.\n"
            "신호 품질은 평소보다 낮을 수 있습니다."
        )

    return PreflightResult(mode=mode, envscan_path=envscan_found, gnews_path=gnews_found)
```

**3가지 실행 모드**:

| 모드 | 조건 | 동작 |
|------|------|------|
| `full` | EnvironmentScan + GlobalNews 모두 있음 | 전체 21모듈 파이프라인 |
| `envscan_only` | EnvironmentScan만 있음 | GlobalNews 단계 스킵, 나머지 정상 |
| `independent` | 둘 다 없음 | FRED + DART + pykrx만으로 실행, Telegram 경고 포함 |

**탐색 경로 전략 (`envscan_search_paths`)**:
```python
DEFAULT_SEARCH_PATHS = [
    "~/Documents/EnvironmentScan/",
    "~/Desktop/Ai_works/",           # 현재 프로젝트 부모 경로 탐색
    "~/",
    Path.cwd().parent,               # 현재 작업 디렉터리 상위
]
```
→ 발견 즉시 `state.yaml`에 경로 기록. HITL-1에서 사용자가 경로 확인·수정 가능.

---

### Step 2 — Schema Analysis + PRD-vs-실제 조정

#### schema-mapping.md 필수 포함 섹션

```markdown
### 1. EnvScan WF1 필드 매핑
| PRD 기대 필드 | 실제 필드 | 처리 방법 |
|-------------|---------|---------|
| steeps_category | preliminary_category | 직접 사용 |
| psst_score | (없음) | analysis.priority_score/5 |
| summary | (없음) | content.abstract[:200] |

### 2. pSST 스케일 현황 (auto-detection 절대 금지)
| 출처 | 스케일 | 정규화 | engine 필드 값 |
|------|--------|--------|--------------|
| EnvScan WF1 | 0-100 (정수) | /100 | "envscan-wf1" |
| EnvScan WF4 | 0-10 (부동) | /10 | "envscan-wf4" |
| GlobalNews | 0-1 (부동) | 그대로 | "gnews" |

### 3. 선택적 필드 처리 결정
- classification (52% 존재): graceful skip
- analysis (22% 존재): graceful skip, psst 대체값 0.5 사용
- PRD P5(crash-loud) vs P6(graceful): 필드 누락 = graceful (운영 이슈)

### 4. GlobalNews 파일 현황
- signals.parquet 실제 존재 여부: [확인 필요]
- 없을 경우: graceful fallback — EnvScan만으로 파이프라인 계속
```

#### state.yaml discovered_schema 기록

```yaml
discovered_schema:
  envscan_wf1:
    steeps_field: "preliminary_category"
    psst_field: null
    psst_substitute: "analysis.priority_score / 5"
    score_scale: "0-100"
    summary_field: null
    summary_substitute: "content.abstract[:200]"
    preliminary_category_values: ["T", "E", "P", "S", "s", "E_Environmental"]
    classification_optional_ratio: 0.52
    analysis_optional_ratio: 0.22
  gnews:
    file_exists: false
    confidence_field: "confidence"
    confidence_scale: "0-1"
  schema_decisions_recorded_at: ""
  overt_correction_needed: false  # true이면 HITL-1에서 사용자에게 알림
```

---

## 아이디어 2: 전체 모듈 목록 (v4 최종)

| 모듈 | LOC | 역할 | 단계 |
|------|-----|------|------|
| `config.py` | ~100 | YAML 로드 + 경로 관리 + Keychain 동적 로드 | M0.5 |
| `schema.py` | ~250 | frozen dataclass 전체 (InvestmentMeta, StockAnalysisContext, DartFinancials, ValuationContext, NarrativeOutput, PredictionRecord) | M0.5 |
| `normalizers.py` | ~300 | 6포맷 파서 (실제 필드명) | M0.5→M1 |
| `synthesize_macro.py` | ~200 | STEEPs → 섹터 방향 (감성 0%) | M0.5→M1 |
| `telegram_notifier.py` | ~100 | Telegram 발송 | M0.5→M1 |
| `compliance_filter.py` | ~80 | 금지 언어 감지·대체 (10개 패턴 목록 명시) | M0.5 |
| `dedup.py` | ~150 | content-hash 중복 제거 | M1 Phase 2 |
| `steeps_classifier.py` | ~200 | STEEPs 재분류 | M1 Phase 2 |
| `signal_bridge.py` | ~200 | STEEPs → GICS 섹터 | M1 Phase 2 |
| `korea_signal_layer.py` | ~150 | 외국인 수급·환율·정책 | M1 Phase 3 |
| **`stock_selector.py`** | **~150** | **종목 자동 선정 (Cat A/B, 수급 기반, v4 신설)** | **M1 Phase 3** |
| `synthesize_stock.py` | ~200 | DART+pykrx+FRED → StockAnalysisContext | M1 Phase 4 |
| `valuation_comparator.py` | ~120 | 섹터 PER 비교 | M1 Phase 4 |
| `intelligence_engine.py` | ~150 | Claude Code 인터랙티브 세션 원고 생성 인터페이스 (Stage 2) | M1 Phase 4 |
| `report_generator.py` | ~200 | Jinja2 조립 (NarrativeOutput JSON 변수 삽입) | M1 Phase 5 |
| `validate_report_quality.py` | ~120 | 완성본 8항목 자동 검증 + PRD 감산 모델 | M1 Phase 5 |
| `weekly_orchestrator.py` | ~250 | Stage 1(데이터 전용) + Stage 2(리포트) 파이프라인 제어 | M1 Phase 5 |
| `accuracy_tracker.py` | ~200 | 예측 기록 + 벤치마크 ETF 비교 + Naive Baseline + 월간 리포트 | M1 Phase 5 |
| `watchdog.py` | ~120 | 월요일 08:00 강제 알림 + 지연 감지 + 한국어 에러 가이드 | M1 Phase 5 |
| `health_dashboard.py` | ~80 | HTML 대시보드 (5가지 필수 표시 항목, PRD 11.3 형식) | M1 Phase 6 |
| `personalizer.py` | ~150 | Keychain 읽기·쓰기 + 섹터/플랫폼 설정 (config.py와 역할 분리: personalizer = 사용자 입력, config = 런타임 로드) | M1 Phase 6 |
| **합계** | **~3,430** | | |

> **v4 변경**: `stock_selector.py` 신설(+150), `accuracy_tracker.py`·`watchdog.py` 상세 구현으로 LOC 증가, `schema.py`에 `PredictionRecord` 추가

---

## 아이디어 3: State.yaml 구조 (v4 최종)

```yaml
# .claude/state.yaml — InvestScan Workflow SOT
workflow:
  current_phase: "research"
  current_step: 1
  refinement_count: 0          # Step 10-R 실행 횟수 (최대 2)

discovered_paths:
  envscan_wf1_output: ""
  gnews_signals: ""
  investscan_root: ""
  config_file: ""

discovered_schema:              # Step 2에서 Claude Code가 결정·기록
  envscan_wf1:
    steeps_field: ""
    psst_field: null
    psst_substitute: ""
    score_scale: ""
    classification_optional_ratio: 0.0
  gnews:
    file_exists: false
  schema_decisions_recorded_at: ""
  overt_correction_needed: false

data_freshness:                   # v4 추가: 데이터 신선도 추적
  signals_parquet_generated_at: ""  # GlobalNews signals.parquet 생성 시각
  envscan_db_generated_at: ""       # EnvironmentScan database.json 생성 시각
  context_file_generated_at: ""     # Stage 1 완료 시 context_[날짜].json 생성 시각
  stale_warning: false              # true이면 Telegram에 신선도 경고 포함

hitl_gates:
  hitl_1:
    passed: false
    claude_max_confirmed: false
    telegram_configured: false
    sectors_confirmed: []
    publish_platform: ""            # "personal" | "blog" | "obsidian"
    watchlist_override: []          # v4 추가: 사용자 수동 종목 추가
  hitl_2:
    passed: false
    telegram_received: false
    choice: ""                      # "continue" | "pause_2weeks"
    choice_date: ""                 # v4 추가: "pause_2weeks" 선택 시 날짜 기록 (타이머용)
  hitl_3:
    passed: false
    validate_score: 0.0
    validate_delivery_mode: ""      # "normal" | "with_warning" | "reloop"
    checklist_score: null           # v4: 1~5 (체크리스트 통과 개수)
    refinement_triggered: false

milestones:
  m05:
    done: false
    dg_01_to_08_passed: false
  m1:
    phase_2_done: false
    phase_3_done: false
    phase_4_intelligence_done: false
    phase_5_done: false
    validate_8_passed: false        # v4: 7항목→8항목으로 확장
    phase_6_done: false
    launchd_activated: false
    final_acceptance_passed: false

packages:
  m05_ready: false
  m1_ready: false
  fixtures_generated: false
  failed_packages: []

errors: []
```

---

## 아이디어 4: 네트워크 의존성 매트릭스 (v3 확장)

> PRD Section 9.6 기반 + v3 신설 모듈 추가

| 모듈 | 인터넷 필요 | 외부 서비스 | 장애 시 동작 |
|------|-----------|----------|------------|
| `config.py` | ❌ | 없음 | 완전 로컬 |
| `schema.py` | ❌ | 없음 | 완전 로컬 |
| `normalizers.py` | ❌ | 없음 | 완전 로컬 |
| `dedup.py` | ❌ | 없음 | 완전 로컬 |
| `steeps_classifier.py` | ❌ | 없음 | 완전 로컬 |
| `signal_bridge.py` | ❌ | 없음 | 완전 로컬 |
| `synthesize_macro.py` | ❌ | 없음 | 완전 로컬 |
| `report_generator.py` | ❌ | 없음 | 완전 로컬 |
| `compliance_filter.py` | ❌ | 없음 | 완전 로컬 |
| `validate_report_quality.py` | ❌ | 없음 | 완전 로컬 |
| `personalizer.py` | ❌ | macOS Keychain | 완전 로컬 |
| `health_dashboard.py` | ❌ | 없음 | 완전 로컬 |
| `korea_signal_layer.py` | ✅ | FDR (KRX) | graceful 스킵 — 글로벌 신호만 사용 |
| **`stock_selector.py`** | ✅ | FDR (수급) | **graceful fallback — 외국인 수급 없을 시 신호 점수 순위로 대체** |
| `accuracy_tracker.py` | ✅ (4주 후) | FDR 가격 | 조회 실패 시 대기 |
| **`synthesize_stock.py`** | ✅ | DART OpenAPI | **graceful 스킵 — 실적 수치 없이 방향성 원고만** |
| **`synthesize_stock.py`** | ✅ | pykrx | **graceful 스킵 — valuation 섹션 생략** |
| **`synthesize_stock.py`** | ✅ | FRED API | **graceful 스킵 — 매크로 섹션 생략** |
| **`valuation_comparator.py`** | ✅ | pykrx | **graceful — ValuationComparison 빈 배열 반환** |
| **`intelligence_engine.py`** | ✅ (Claude Max) | Claude Code 에이전트 | **fallback: v1 템플릿 (원고 없이 수치만)** |
| `telegram_notifier.py` | ✅ | Telegram Bot API | 3회 재시도 후 로컬 에러 로그 |
| `watchdog.py` | ✅ | Telegram Bot API | 실패 시 로컬 에러 로그만 |

**Telegram 장애 시 로컬 접근:**
리포트는 항상 `~/investscan/output/reports/YYYY-WW.md`에 로컬 저장된다.
Telegram 미수신 시: `실행방법.txt`에 "Finder에서 ~/investscan/output/reports/ 열기" 안내 포함.

---

## 아이디어 5: 글로벌 경제 지표 커버리지 (한계 인정 + M2 계획)

### M1 커버리지 (현실적 범위)

| 지역 | 포함 방식 | 비고 |
|------|---------|------|
| 미국 | FRED API 10개 지표 | 금리, CPI, GDP, VIX 등 |
| 한국 | DART, pykrx, FDR, korea_signal_layer | 기업 실적 + 수급 |
| 글로벌 뉴스 | EnvironmentScan 116개 사이트 14개 언어 | 유럽/중국/일본 뉴스 텍스트로 커버 |

### M1 한계 (명시적 인정)

유럽(ECB), 중국(PMI), 일본(BOJ) 정량 경제 지표는 M1에 포함되지 않는다.
이 데이터는 뉴스 텍스트에서 intelligence_engine.py(Claude Code)가 추론한다.
**"뉴스 기반 추론"이지 "정량 데이터 기반 분석"이 아님을 리포트에 명시한다.**

### M2 보완 계획 (PRD 범위 밖, 참고)

| 추가 소스 | 역할 |
|---------|------|
| ECB API (무료) | 유로존 기준금리, 인플레이션 |
| 中 PMI (csv 수동 업로드) | 중국 제조업 경기 |
| 야후 파이낸스 글로벌 | 글로벌 ETF 가격 비교 |

---

## 아이디어 6: Few-shot 예시 완성본 (Step 5에서 사용)

```python
FEW_SHOT_EXAMPLE = {
    "input_context": {
        "sector": "반도체",
        "direction": "Bullish",
        "confidence": 0.72,
        "top_signals": [
            {"id": "sig-014", "title": "TSMC 2026 Q2 수주량 전분기 대비 +18% 확인",
             "source": "DigiTimes", "date": "2026-05-15", "steeps": "T"},
            {"id": "sig-027", "title": "미국 CHIPS Act 2차 보조금 집행 확정",
             "source": "Commerce Dept", "date": "2026-05-14", "steeps": "P"},
            {"id": "sig-031", "title": "SK하이닉스 HBM4 공급 계약 3건 추가 확인",
             "source": "전자신문", "date": "2026-05-16", "steeps": "T"},
        ],
        "stock_context": {
            "ticker": "000660", "name": "SK하이닉스",
            "per": 12.3, "sector_avg_per": 15.4,
            "revenue_yoy": 0.18, "op_income_yoy": 0.32,
            "foreign_flow_4w": 4200
        }
    },
    "expected_output": {
        "sector_narrative": "반도체 섹터는 2026년 5월 현재 강한 상승 모멘텀을 유지하고 있다. "
            "미국 CHIPS Act 2차 자금 집행 확정(신호 #27)이 국내 반도체 밸류체인에 순풍으로 작용하고 있으며, "
            "TSMC의 분기 수주량 18% 증가(신호 #14)는 전방 수요 회복을 수치로 확인시켜준다. "
            "이 두 신호의 연쇄 효과로 HBM 메모리 수요가 구조적으로 확대되고 있어 "
            "SK하이닉스 등 국내 HBM 공급사의 수혜가 예상된다.",
        "causal_chains": [
            {
                "from": "CHIPS Act 2차 예산 집행 확정",
                "via": "TSMC 미국 공장 수주 확대(+18%)",
                "to": "SK하이닉스 HBM4 공급 계약 3건 추가"
            }
        ],
        "stock_analyses": [
            {
                "ticker": "000660", "name": "SK하이닉스", "category": "A",
                "narrative": "SK하이닉스는 HBM4 공급 계약 3건 확보(신호 #31)로 2026 하반기 "
                    "수익성 개선이 예상된다. 현재 Forward PER 12.3배는 섹터 평균(15.4배) "
                    "대비 약 20% 할인 구간으로, 실적 개선 모멘텀이 주가에 충분히 반영되지 않은 상태다. "
                    "최근 4주 외국인 순매수 4,200억원은 글로벌 투자자들의 관심 증가를 시사한다.",
                "key_metrics": [
                    {"name": "Forward PER", "value": "12.3x", "context": "섹터 평균 15.4x 대비 20% 할인"},
                    {"name": "YoY 매출 성장률", "value": "+18%", "context": "2025Q3 기준"},
                    {"name": "외국인 순매수 4주", "value": "+4,200억원", "context": "최근 4주 누적"}
                ],
                "risks": ["HBM 공급 과잉 진입 시 단가 하락 — 영업이익 10~15% 감소 우려"],
                "momentum_opinion": "긍정적 모멘텀 유지 중"
            }
        ],
        "category_b_analyses": [],
        "bear_case": "반도체 섹터 방향 반전 시나리오: 미-중 반도체 제재가 HBM 수출 제한으로 "
            "확대될 경우 삼성·SK의 중국 매출(전체 약 35%)이 급감할 수 있다(신호 #22). "
            "또한 글로벌 AI 투자 사이클이 예상보다 일찍 종료될 경우 HBM 수요 자체가 급감할 수 있다."
    }
}
```

---

## 아이디어 7: M0.5 Done Gate — 8항목 (변경 없음)

| ID | 검증 내용 |
|----|---------|
| DG-01 | `synthesize_macro()` null-safe 실행 |
| DG-02 | WF1 normalizer 실제 필드명 파싱 성공 |
| DG-03 | schema 검증 함수 존재 |
| DG-04 | Telegram notifier dry-run |
| DG-05 | `weekly_orchestrator --offline --dry-run` |
| DG-06 | `investscan.yaml envscan_db_path` 설정 확인 |
| DG-07 | `sentiment_weight == 0.0` (P1 절대 원칙) |
| DG-08 | `compliance_filter.py` 금지 언어 10개 샘플 통과 |

---

## 아이디어 8: 비코더 UX 언어 규칙 (v3)

| 기술 용어 | workflow 표기 |
|-----------|--------------|
| `intelligence_engine.py` | 분석 원고 작성기 (Claude AI가 원고 작성) |
| `synthesize_macro.py` | 신호 합산기 — 섹터 방향 판단 |
| `synthesize_stock.py` | 종목 수치 분석기 |
| `valuation_comparator.py` | 가격 비교기 |
| `compliance_filter.py` | 법적 표현 안전망 |
| `validate_report_quality.py` | 완성본 자동 품질 검사기 (8항목) |
| `schema.py` | 데이터 설계도 (모든 모듈이 공유하는 계약) |
| `NarrativeOutput JSON` | Claude 원고 파일 |

---

## 아이디어 9: 법적 컴플라이언스 (v4 — 금지 표현 목록 추가)

### 투자의견 조작적 재정의

| 절대 목표 | 조작적 정의 | 허용 표현 | 금지 표현 |
|---------|----------|---------|---------|
| "투자의견을 갖춘" | 방향성 모멘텀 평가 | "긍정적 모멘텀 유지 중" | "매수 추천" |
| "수치를 갖춘" | 정량 데이터 포함 | "PER 12.3x (섹터 -20%)" | "목표주가" |
| "리스크를 갖춘" | 하방 시나리오 서술 | "공급 과잉 시 -15% 우려" | "손실 없음" |

### compliance_filter.py 금지 표현 → 대체 매핑 (PRD 15.2 기반 + v4 추가)

```python
COMPLIANCE_RULES = [
    # PRD 15.2 기본 6개
    ("매수 추천합니다",   "관찰 대상으로 분류되었습니다"),
    (r"\d+% 수익 예상",  "4-12주 방향성: 긍정 신호"),
    ("지금 사세요",       "이번 주 행동 참고 사항"),
    ("투자 조언",         "데이터 기반 관찰 목록"),
    ("종목 추천",         "종목 관찰 워치리스트"),
    ("확실한 상승",       "신호 강도: High (불확실성 포함)"),
    # v4 추가 4개
    ("손실 없음",         "리스크 시나리오 포함"),
    ("목표주가",          "참고 수준 벨류에이션"),
    ("무조건",            "데이터 기반 판단"),
    (r"반드시 .{0,10}(오른다|상승한다|이익)", "긍정적 신호 감지 (불확실성 포함)"),
]
```

> **P1 원칙 적용 범위 명시 (v4)**: `sentiment_weight = 0.0`은 `synthesize_macro.py`의 **수치 합산 단계**에만 적용됨. intelligence_engine.py(Claude Code 원고 생성)의 톤은 Category A/B 프롬프트의 "절대 포함하지 말 것" 지시와 compliance_filter.py로 통제.

> **D6 외부 게시 기준 면책 조항 강화 (v4)**:
> - Jinja2 템플릿에 `publish_platform` 조건부 면책 조항 분기 추가 (핵심 수정 6 참조)
>   - `personal`: 개인 투자 참고용 간략 면책 조항
>   - `blog` / `external`: 「자본시장법」 명시 + 비전문가 의견 고지 + 상담 권장 강화 문구
> - `validate_report_quality.py`에 **면책 조항 존재 여부 검증 항목** 추가 가능 (M1 Phase 5에서 결정)
> - 외부 게시 선택 시(`publish_platform == "blog"`): compliance_filter.py의 10개 규칙 외에
>   Jinja2 강화 면책 조항이 최후 안전망으로 작동.

---

## 미결 질문 (v4 — 일부 해결)

| # | 질문 | 상태 | 해결/기본값 |
|---|------|------|------------|
| 1 | 완성본 게시 플랫폼은? (HITL-1에서 확인) | ✅ HITL-1에서 결정 | 개인 투자 판단용 (기본) |
| 2 | intelligence_engine.py fallback 시 알림 방식? | ✅ 해결 | watchdog.py FAILURE_GUIDE 한국어 평문 Telegram 발송 |
| 3 | "2주 M0.5 사용" 선택 후 M1 재개 메커니즘? | ✅ 해결 | state.yaml `hitl_2.choice_date` 기록 → watchdog.py가 14일 경과 시 Telegram으로 "M1 재개 준비됐습니다. /weekly-report 실행하세요" 발송 |
| 4 | validate_report_quality.py 통과 기준? | ✅ 해결 | 8항목 중 5개 이상 통과 시 발송 (delivery_mode에 따라 정상/경고 배너 분기) |
| 5 | 주간 자동화 전체 vs 부분 자동화? | ✅ 해결 | Hybrid: Stage 1(데이터 launchd 자동화) + Stage 2(/weekly-report 사용자 트리거) |

---

## 핵심 결정 사항 최종 요약 (v4)

| # | 결정 | 근거 |
|---|------|------|
| 1 | **Hybrid 자동화 구조 채택**: Stage 1(데이터 launchd 자동화) + Stage 2(/weekly-report 사용자 트리거) | Option A headless 기술적 불가 → Hybrid로 재설계. 비용 없음, 사용자 입력 최소 |
| 2 | **stock_selector.py 신설**: 종목 자동 선정 (Cat A = 외국인 수급 Top 5, Cat B = 테마 신호 Top 3) | "최소 입력" 약속 — 매주 종목 수동 지정 없음 |
| 3 | **Category A/B 프롬프트 분리** | 절대 목표 [F] 실질 달성 |
| 4 | **dataclass 스키마를 schema.py에서 사전 확정** (PredictionRecord 추가) | 모듈 간 인터페이스 충돌 방지 |
| 5 | **validate_report_quality.py 8항목 + PRD 감산 모델** | 수치 정확성 검증 추가, 이진 판정 → 3단계 delivery_mode |
| 6 | **Step 10-R 재조정 루프 (최대 2회)** | HITL-3 체크리스트 3개 미만 시 처리 경로 확보 |
| 7 | **HITL-3 체크리스트 방식** (1~5점 → 5개 예/아니오) | 비코더 목사님이 실질 판단 가능한 형식 |
| 8 | **accuracy_tracker.py 상세 설계** (PredictionRecord 스키마, 벤치마크 ETF 4개, Naive Baseline, 월간 리포트) | PRD 13.1~13.4 완전 반영 |
| 9 | **watchdog.py 상세 설계** (한국어 평문 에러 가이드, 지연 감지 pseudo-code) | PRD 11.6 반영 + 비코더 에러 대응 가능화 |
| 10 | **compliance_filter.py 금지 표현 10개 목록 명시** | PRD 15.2 6개 + v4 추가 4개 |
| 11 | **state.yaml 업데이트**: hitl_2.choice_date, data_freshness 섹션 추가 | "2주 M0.5" 타이머 + signals.parquet 신선도 검증 |
| 12 | **P1 원칙 적용 범위 명시**: synthesize_macro.py 수치 합산에만 적용 | LLM 원고 톤과 분리 명확화 |
| 13 | **HITL-1에 게시 플랫폼 + 종목 수동 추가 옵션** | "편집 없이 즉시 게시" 보장 |
| 14 | **M1 글로벌 지표 한계 명시** + M2 보완 계획 | 과도한 기대 방지 |
| 15 | **Jinja2 변수 매핑 테이블 확정** | 모듈 간 연결 계약 |
| **16** | **[D1] 단계적 자동화 전환**: M0.5 = Hybrid(/weekly-report 트리거), M1 = 완전 자동(Anthropic API, ~$1~3/월) | 기술적 실현 가능성(M0.5) + 장기 완전 자동화(M1) 양립 |
| **17** | **[D2] 전제 조건 자동 감지**: Step 1에서 EnvironmentScan/GlobalNews 자동 탐색 + 3가지 실행 모드 fallback (`full` / `envscan_only` / `independent`) | 사용자 수동 경로 입력 불필요 — "최소 입력" 약속 이행 |
| **18** | **[D3] M0.5 먼저 2주 운용**: HITL-2에서 2주 사용 후 M1 전환 승인 → watchdog.py 14일 타이머 기반 재개 알림 | 미검증 완전 자동화 바로 적용 위험 방지 |
| **19** | **[D4] 기본 게시 플랫폼 = 개인 투자 판단용**: `publish_platform = "personal"` 기본값, HITL-1에서 변경 가능 | 외부 게시 강화 면책 조항을 선택적으로 적용 |
| **20** | **[D5] 초기 관심 섹터 = 반도체·IT서비스·바이오**: HITL-1 기본값 확정, 변경 가능 | 설치 직후 즉시 동작하는 합리적 기본값 |
| **21** | **[D6] 외부 게시 기준 강화 면책 조항**: Jinja2 조건부 분기(`publish_platform == "blog"`시 「자본시장법」 명시) + compliance_filter.py 10개 규칙 이중 안전망 | 블로그·브런치 게시 시 법적 리스크 최소화 |

---

*InvestScan workflow.md 아이디어 v4 Final — 4차 적대적 검토 10개 조치 + D1-D6 사용자 확정 결정 완전 반영*
*다음 단계: 사용자 승인 후 workflow.md 초안 작성*
