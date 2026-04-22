# InvestScan 시스템 블루프린트
**Step 5 산출물** | 생성일: 2026-03-29 | 언어: English (P5-A)

---

## 시스템 아키텍처

```
User (Korean) ←→ Claude Code Session (Orchestrator)
                        │
          ┌─────────────┼─────────────┐
          │             │             │
   Research Fork    Module Forks   Translation
   (Stage 1)        (Stage 2)      Fork (@translator)
          │             │             │
   ┌──────┼──────┐  ┌───┼───┐     Korean .ko.md
   │      │      │  │   │   │     pACS logs
 FRED  EnvScan GNews Fork Fork Fork
              │    A   B   C
              └─────────────── Fork D → Fork E
```

### 에이전트 스웜(Agent Swarm): 3+5+2+1

| 역할 | 수량 | 에이전트 |
|------|------|----------|
| 리서치 | 3 | envscan-agent, fred-agent, gnews-agent |
| 구현 | 5 | builder-a/b/c/d/e |
| 리뷰 | 2 | code-reviewer, fact-checker |
| 번역 | 1 | @translator |

---

## 데이터 흐름

```
EnvironmentScan DB → normalizers.py → UnifiedSignal[]
                                            │
FRED API ──────────→ synthesize_macro.py → InvestmentMeta
                                            │
GlobalNews Parquet → signal_bridge.py ──→ {sector: signals[]}
                           │
                     dedup.py (content-hash)
                           │
                   steeps_classifier.py (keyword lookup)
                           │
KRX/DART ──────────→ korea_signal_layer.py → KoreaSignal
                           │
                   stock_selector.py (numeric thresholds)
                    category A or B
                           │
                   synthesize_stock.py → context_data dict
                           │
                   intelligence_engine.py (LLM)
                    → NarrativeOutput (English)
                           │
              ┌────────────┼────────────┐
              │            │            │
    validate_report   compliance_   citation_
    _quality.py       filter.py     validator.py
    (Python 8-criteria) (10 patterns) (Python)
              │
    report_generator.py → weekly-report-{date}.md
              │
         @translator → weekly-report-{date}.ko.md
              │
    accuracy_tracker.py → PredictionRecord
              │
    Telegram (Korean 5-line summary)
```

---

## 모듈 책임 (P6: Python-First)

| 모듈 | 결정 유형 | LLM 사용 여부 |
|------|----------|--------------|
| steeps_classifier.py | 키워드 분류 | NO |
| compliance_filter.py | 정규식 금지 패턴 검사 | NO |
| stock_selector.py | 수치 기반 카테고리 임계값 | NO |
| synthesize_macro.py | 규칙 기반 매크로 합성 | NO |
| citation_validator.py | 수치 교차 검증 | NO |
| validate_report_quality.py | 정규식 8개 기준 (1차 패스) | 2차 패스만 |
| intelligence_engine.py | 텍스트 생성 | YES (내러티브만) |
| @translator | 한국어 번역 | YES (텍스트만) |

---

## SOT 계층 구조 (D1)

```
Tier 0: .claude/state.yaml          ← Orchestrator-only write
  └── Tier 1: .claude/state/phase-*.yaml  ← Phase Lead write
        └── Tier 2: .claude/agent-workspace/*.yaml  ← SubAgent self-write only
```

모든 쓰기 작업은 원자적 `tmp → rename` 패턴을 따른다. 모든 키/값은 영어(P5-A)로 작성한다.

---

## 드라이런 모드

`investscan.yaml`의 mode가 `dry-run`인 경우:
- API 키: MOCK_ 접두사가 붙은 더미 값 사용
- 데이터 경로: 라이브 API 대신 `tests/fixtures/` 사용
- LLM 호출: 테스트에서 monkeypatch 가능
- Telegram: 전송 대신 stdout 출력
- `run_m05.py --dry-run` 실행 시 외부 연결 없이 DG-01~08 검증 가능

이를 통해 실제 API 키 없이도 전체 파이프라인 검증이 가능하다.

---

## 정확도 추적 (v3.6 I-3)

| 기간 | 목적 | KS-1 기준 여부 |
|------|------|---------------|
| 4주 | 예비 판독 | No |
| 8주 | 최종 측정 | YES |

KS-1 레이블: "Month 3 data basis" (측정 지연 반영 — v3.6 I-5).
나이브 베이스라인: Always-Bullish + Momentum + Random (v3.6 I-13).

---

## Bear Case UX (v3.6 I-12)

Bear Case 섹션 위치: **리포트 하단** (면책 조항 바로 위).
이는 신규 사용자의 의사결정 마비를 방지하기 위함이다.
Telegram 5줄 요약에는 Bear Case를 포함하지 않는다(간결성 원칙).

---

*본 블루프린트는 시스템 설계의 정본 참조 문서다. 아키텍처 변경 시 ADR 문서화가 필요하다.*
