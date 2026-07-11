# 심층조사: 리포트 수신 후 사용자 의사결정 워크플로우 + 피드백 루프

> **Date**: 2026-03-28
> **Status**: Research Deliverable
> **Context**: InvestScan이 주간 리포트 + 종목 워치리스트를 생성한 이후, 비코더 사용자가 실제로 무엇을 어떻게 하는지의 설계
> **User Profile**: 비코더 목사, 투자 경험 있으나 전문가 아님, 주 2-4시간 가용, 로컬 MacBook

---

## 1. 비코더 주간 루틴 타임라인

### 1.1 설계 원칙

웹 조사에서 확인된 핵심 설계 원칙 4가지를 InvestScan 사용자 맥락에 적용한다.

| # | 원칙 | 출처 | InvestScan 적용 |
|---|------|------|----------------|
| D1 | **Progressive Disclosure** | Nielsen Norman Group | 리포트를 3층 구조(30초/5분/15분)로 설계. 모든 정보를 한번에 보여주지 않는다 |
| D2 | **Time-Boxing** | FBS 30-Minute Trading Routine | 전체 주간 루틴을 30분 이내로 제한. 목사 본업에 지장 없는 수준 |
| D3 | **Decision Fatigue 방지** | The Decision Lab, Frontiers in Psychology | 한 주에 내려야 할 결정을 최대 3개로 제한. "이번 주 할 일" 체크리스트를 시스템이 제안 |
| D4 | **Habit-Forming Trigger** | Telegram push notification | 월요일 아침 자동 알림이 루틴 진입점. 사용자가 "기억해서 찾아가는" 것이 아니라 "알림이 와서 시작하는" 구조 |

### 1.2 주간 타임라인

```
일요일 밤 (자동)          월요일 아침              월요일 오전~오후           금요일 (선택)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────┐   ┌──────────────────┐   ┌────────────────────┐   ┌───────────────────┐
│ PHASE 0: 파이프라인  │   │ PHASE 1: 수신+읽기  │   │ PHASE 2: 의사결정     │   │ PHASE 3: 기록+피드백  │
│ (완전 자동)         │   │ (5분)              │   │ (10-15분)            │   │ (10분, 선택적)       │
│                   │   │                    │   │                      │   │                     │
│ ● investscan run  │──▶│ ● Telegram 알림 수신 │──▶│ ● 증권사 앱에서 확인    │──▶│ ● 이번 주 행동 기록    │
│ ● 리포트 생성       │   │ ● 핵심요약 30초 읽기  │   │ ● 매매/관망/비중조정    │   │ ● "이번 주 리포트가    │
│ ● Telegram 전송    │   │ ● 관심 섹터 상세 읽기  │   │   결정 (최대 3개)      │   │   맞았나?" 피드백     │
│ ● 저널 리마인더 전송  │   │ ● 행동 체크리스트 확인 │   │ ● 결정 근거 메모       │   │ ● 다음 주 관심사 메모   │
└─────────────────┘   └──────────────────┘   └────────────────────┘   └───────────────────┘
      (0분)                 (5분)                  (10-15분)                (10분)
                                                                     ━━━━━━━━━━━━━━━━━━
                                                                     총 소요: 25-30분/주
```

### 1.3 각 Phase 상세

#### PHASE 0: 파이프라인 실행 (일요일 밤, 완전 자동)

이미 설계 완료된 부분. `launchd` 또는 수동 `investscan run`으로 실행.
- EnvironmentScan + GlobalNews-Crawling 실행
- 시그널 정규화 + 투자 방향 합성
- 주간 리포트 Markdown 생성
- **새로운 추가**: Telegram으로 3종 메시지 자동 전송
  1. 핵심요약 (200자 이내)
  2. 행동 체크리스트 (이번 주 관찰/매매 후보)
  3. 지난주 저널 리마인더 ("지난주 결정 리뷰할 시간입니다")

#### PHASE 1: 수신 + 읽기 (월요일 아침, 5분)

**진입 트리거**: Telegram 푸시 알림 (월요일 07:00 KST)

사용자 행동 순서:
1. Telegram에서 핵심요약 메시지 읽기 (30초)
2. "이번 주 전체 방향이 뭔가?" 한 문장으로 파악
3. 관심 있는 섹터가 있으면 전체 리포트 링크 클릭 → Markdown 또는 HTML로 상세 읽기 (4분)
4. 관심 없으면 여기서 끝 — **"이번 주는 관망"도 유효한 결정**

**핵심 설계**: 리포트를 끝까지 읽을 필요가 없다. Progressive Disclosure 원칙에 따라, Telegram 요약만으로도 "이번 주 시장 분위기"를 파악할 수 있어야 한다.

#### PHASE 2: 의사결정 (월요일 오전~오후, 10-15분)

**전제**: 리포트가 "어떤 종목을 사라"고 말하지 않는다. "이 방향이 강해지고 있다"고 말한다. 최종 매매 결정은 사용자의 몫.

사용자 행동 순서:
1. 증권사 앱(키움, 한투 등) 열기
2. 리포트에서 제안된 관찰 섹터/종목 확인
3. 3가지 중 하나 결정:
   - **관망**: 현재 포트폴리오 유지 (가장 빈번한 결정이어야 함)
   - **비중 조정**: 특정 섹터 ETF 비중 증가/감소
   - **신규 진입/청산**: 새 포지션 개시 또는 기존 포지션 정리
4. 결정 이유를 한 줄로 메모 (Telegram 봇에 답장, 또는 리포트 내 체크리스트에 기록)

**Decision Fatigue 방지 규칙**:
- 한 주에 최대 3개 의사결정
- 리포트의 "행동 체크리스트"가 3개를 초과하면 시스템이 자동으로 확신도 상위 3개만 표시
- 확신도 50% 미만 시그널은 "행동 후보"에서 자동 제외

#### PHASE 3: 기록 + 피드백 (금요일, 선택적, 10분)

**진입 트리거**: 금요일 17:00 KST Telegram 리마인더

사용자 행동 순서:
1. Telegram 봇에 이번 주 행동 기록 (자연어)
   - 예: "반도체 ETF 5% 추가 매수했음. 리포트 신호 맞는 것 같아서."
   - 예: "이번 주는 아무것도 안 함. 관망."
   - 예: "리포트에서 IT 강세라고 했는데, 실제로는 조정이 왔음. 단기 예측 부정확."
2. Telegram 봇이 자연어를 구조화된 저널 엔트리로 변환 (후술)
3. 월말에 시스템이 자동 집계 → 월간 자가 평가 리포트 생성

---

## 2. 리포트 포맷 구체적 예시 (행동 지침 포함)

### 2.1 현재 설계의 문제점

기존 Branch 3.1/3.2에서 설계된 리포트 포맷은 훌륭한 분석 문서이지만, **"다 읽은 다음에 뭘 해야 하지?"** 에 대한 답이 없다. 구체적으로:

| 기존 리포트 구조 | 문제 |
|----------------|------|
| 핵심 요약 | 방향은 알려주지만, 행동은 알려주지 않는다 |
| 섹터별 투자 방향 | 14개 섹터를 다 보여주면 인지 부하 과다 |
| Top 10 시그널 | 10개를 다 읽어야 하나? |
| 증거 체인 | 신뢰를 높여주지만, 행동과 연결되지 않는다 |

### 2.2 개선된 리포트 구조: "3층 Progressive Disclosure"

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Telegram 요약 (30초)                                 │
│ ─ 1문장 시장 방향 + 확신도 게이지                                │
│ ─ 이번 주 행동 체크리스트 (최대 3개)                              │
│ ─ "자세히 보기" 링크                                           │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: 핵심 리포트 (5분)                                     │
│ ─ 경영 요약 (Executive Summary)                               │
│ ─ 행동 체크리스트 상세 (근거 포함)                                │
│ ─ 내 포트폴리오와의 관련성 (보유 섹터 하이라이트)                    │
│ ─ 위험 경고                                                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: 전체 분석 (15분, 선택)                                 │
│ ─ 14개 섹터 전체 분석                                          │
│ ─ STEEPs 히트맵                                              │
│ ─ 증거 체인                                                   │
│ ─ 약한 시그널 감시                                             │
│ ─ 지난주 대비 변화                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Layer 1: Telegram 요약 메시지 예시

```
[InvestScan 2026-03-27]

이번 주 시장: 강세(Bullish) ████░ 72%

━━ 이번 주 행동 체크리스트 ━━

1. [관찰] 반도체 섹터 강세 지속 (확신 78%)
   → 삼성전자·SK하이닉스 현재가 대비 목표가 확인

2. [관찰] 2차전지 약세 전환 신호 (확신 61%)
   → 보유 중이면 손절/비중축소 검토

3. [관망] 바이오 — 시그널 혼재, 추가 데이터 대기

━━━━━━━━━━━━━━━━━━━
📎 전체 리포트: [링크]
💬 이번 주 결정 기록: 이 메시지에 답장하세요
```

### 2.4 Layer 2: 핵심 리포트 (행동 지침 포함 버전)

기존 Branch 3.1 리포트에 **Section 0: 행동 체크리스트**를 최상단에 추가한다.

```markdown
# 주간 투자 방향 리포트
> **기간**: 2026-03-21 ~ 2026-03-27
> **생성일**: 2026-03-27 10:00 KST
> **소스**: EnvScan 42건 + GlobalNews 87건 = 총 129건 분석

---

## 0. 이번 주 행동 체크리스트

> 리포트 전체를 읽지 않아도, 이 섹션만으로 이번 주 행동을 결정할 수 있습니다.

### 행동 1: 반도체 섹터 — 관찰 (확신 78%)
- **시그널**: AI 인프라 투자 가속 (EnvScan 3건 + GlobalNews 12건 수렴)
- **STEEPs**: T(기술) + E(경제) 교차 강화
- **구체적 행동**: 삼성전자(005930), SK하이닉스(000660) 현재가 확인.
  지난 2주간 +8% 이상 상승했으면 추격 매수 자제, 조정 시 매수 기회 대기.
- **판단 기준**: "AI 투자 뉴스가 3건 이상 나왔고, 두 소스 모두 같은 방향이면 강한 시그널"
- **리스크**: 미중 반도체 규제 강화 가능성 (P(정치) 시그널 2건)

### 행동 2: 2차전지 — 비중축소 검토 (확신 61%)
- **시그널**: 유럽 EV 보조금 축소 + 중국 과잉생산 우려 (GlobalNews 8건)
- **STEEPs**: P(정치) + E(경제) 부정적 교차
- **구체적 행동**: 2차전지 ETF(305720) 보유 중이면 -5% 비중 축소 고려.
  보유하지 않으면 신규 진입 보류.
- **판단 기준**: "정치+경제 부정 시그널이 동시에 나오면 중기 약세 가능성 높음"
- **리스크**: 단기 반등 가능 (기술적 과매도 구간)

### 행동 3: 바이오 — 관망 (확신 43%)
- **시그널**: 혼재. 국내 바이오 규제 완화 (S 1건) vs 글로벌 금리 부담 (E 2건)
- **구체적 행동**: 없음. 다음 주 시그널 수렴 방향 확인 후 결정.

> **이번 주 결정 난이도**: 쉬움 (명확한 시그널 1개, 경계 시그널 1개, 관망 1개)
> **지난주 리포트 정확도**: 2/3 (반도체 강세 적중, IT 서비스 중립 적중, 방산 강세 미적중)

---

## 1. 핵심 요약 (Executive Summary)

이번 주 129개 신호를 분석한 결과, **강세(Bullish)** 방향이 우세합니다.

| 방향 | 신호 수 | 평균 확신도 |
|------|---------|------------|
| 강세(Bullish) | 52 | 68% |
| 중립(Neutral) | 48 | 45% |
| 약세(Bearish) | 29 | 57% |

**가장 강한 신호**: AI 인프라 투자 가속 (확신도 78%, 15개 소스 수렴)

---

## 2. 내 포트폴리오 관련성 (보유 섹터 하이라이트)

> 이 섹션은 사용자가 `config.yaml`에 보유 섹터/종목을 등록했을 때 자동 생성됩니다.

| 보유 섹터 | 이번 주 방향 | 지난주 대비 | 행동 제안 |
|-----------|------------|------------|----------|
| 반도체 | 강세 (78%) | ← 유지 | 보유 유지, 추가 매수 기회 대기 |
| 2차전지 | 약세 (61%) | ← 전환 (지난주 중립) | 비중 축소 검토 |
| 헬스케어 | 중립 (48%) | ← 유지 | 변동 없음 |

---

[이하 기존 리포트 섹터별 분석, 증거 체인, 위험 요인 등은 Layer 3로 유지]
```

### 2.5 행동 체크리스트의 핵심 설계 원칙

Morningstar의 "Consider Buying / Consider Selling" 패턴에서 영감을 받되, InvestScan의 특성(방향성 스캐닝, 종목 추천 아님)에 맞게 변형:

| Morningstar 패턴 | InvestScan 변형 |
|-----------------|----------------|
| "Consider Buying" (5성) | **"관찰: 강세 시그널 확인, 기회 대기"** |
| "Consider Selling" (1성) | **"비중축소 검토: 약세 전환 시그널"** |
| "Fair Value" (3성) | **"관망: 시그널 혼재, 추가 데이터 대기"** |

**절대 하지 않는 것**:
- 특정 종목 매수/매도 추천 (법적 리스크 + InvestScan의 역할이 아님)
- 목표가/손절가 제시 (가격 데이터는 Phase 2인 KRX 연동 이후)
- 4개 이상 행동 항목 제시 (Decision Fatigue 방지)

---

## 3. 피드백 루프 설계도

### 3.1 피드백 수집 채널: Telegram 답장

사용자의 진입 장벽을 최소화하기 위해, 기존 Telegram 채널을 피드백 수집 채널로 재활용한다. 별도 앱, CLI 명령어, 웹 인터페이스 없이 **Telegram 메시지 답장** 하나로 모든 피드백을 수집한다.

```
사용자가 입력하는 것 (자연어):
─────────────────────────────
"반도체 ETF 5% 추가 매수. 리포트 신호 믿고."
"이번 주 관망. 특별한 신호 없었음."
"리포트에서 IT 강세라고 했는데 실제로 하락. 단기 예측 불정확한 듯."
"2차전지 손절. 리포트 경고가 맞았음."
─────────────────────────────

시스템이 변환하는 것 (구조화 데이터):
─────────────────────────────
{
  "entry_id": "a1b2c3d4",
  "created_at": "2026-03-28",
  "action_type": "buy",           // buy | sell | hold | reduce | increase
  "sector": "반도체",
  "instrument": "반도체 ETF",
  "signal_alignment": "aligned",  // aligned | contrary | neutral
  "user_assessment": "positive",  // positive | negative | neutral
  "raw_text": "반도체 ETF 5% 추가 매수. 리포트 신호 믿고.",
  "confidence": "medium",
  "feedback_on_report": null,
  "review_date": "2026-06-28"
}
─────────────────────────────
```

### 3.2 자연어 → 구조화 변환 메커니즘

변환은 **규칙 기반 + LLM 폴백** 2단계로 처리한다.

**Stage 1: 규칙 기반 추출 (비용 0, 즉시 처리)**

```
키워드 매핑:
  매수, 샀, 추가 → action_type: "buy"
  매도, 팔았, 손절, 청산 → action_type: "sell"
  관망, 안 함, 패스 → action_type: "hold"
  축소, 줄임 → action_type: "reduce"
  늘림, 확대 → action_type: "increase"

  맞았, 적중, 정확 → user_assessment: "positive"
  틀렸, 부정확, 빗나감 → user_assessment: "negative"

  반도체, 삼성전자, SK하이닉스 → sector: "반도체"
  2차전지, 배터리, LG에너지 → sector: "2차전지"
  [etc. — 섹터 매핑 테이블]
```

**Stage 2: LLM 폴백 (규칙으로 파싱 실패 시)**

Ollama 로컬 모델(또는 Claude API)을 사용하여 자연어를 구조화. 비용이 발생하므로 규칙 기반이 실패한 경우에만 호출.

### 3.3 피드백 반영 경로

피드백이 다음 주 리포트에 실제로 영향을 미치는 3가지 경로:

```
                    ┌─────────────────────────────────────────────────┐
                    │          사용자 피드백 (Telegram 답장)              │
                    └───────────────────────┬─────────────────────────┘
                                            │
                                            ▼
                            ┌───────────────────────────────┐
                            │   자연어 → 구조화 변환           │
                            │   (규칙 기반 + LLM 폴백)        │
                            └───────────┬───────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌───────────────────┐ ┌─────────────────┐ ┌──────────────────┐
        │ 경로 A:            │ │ 경로 B:          │ │ 경로 C:           │
        │ 정확도 추적         │ │ 관심 섹터 학습    │ │ 시그널 가중치 조정  │
        │ (자동, 매주)       │ │ (자동, 매주)     │ │ (월간, 반자동)     │
        └───────┬───────────┘ └───────┬─────────┘ └────────┬─────────┘
                │                     │                     │
                ▼                     ▼                     ▼
        지난주 리포트의          사용자가 자주 언급하는    "이 유형의 시그널은
        방향 예측 정확도 계산     섹터를 "관심 섹터"로     자주 틀린다" →
        → 리포트에 표시          자동 등록 →              확신도 보정 계수 적용
        "지난주 정확도: 67%"     해당 섹터 상세 분석 강화   → 다음 리포트에 반영
```

#### 경로 A: 정확도 추적 (Accuracy Tracking)

Tetlock 슈퍼포캐스팅의 핵심 원칙인 "점수를 기록하라(Keep Score)"를 적용한다.

**메커니즘**:
1. 매주 리포트가 섹터별 방향(강세/약세/중립)과 확신도를 예측
2. 다음 주 파이프라인 실행 시, 지난주 예측 vs 실제 KOSPI/KOSDAQ 섹터 ETF 수익률 비교
3. 단순화된 Brier-like 점수 산출:
   - 예측 "강세" + 실제 +1% 이상 = **적중**
   - 예측 "약세" + 실제 -1% 이상 = **적중**
   - 예측 "강세" + 실제 -1% 이상 = **미적중**
   - 기타 = **중립** (판정 보류)
4. 리포트 Section 0에 "지난주 정확도: 2/3 (67%)"로 표시
5. 월간 누적 정확도 트렌드 그래프 (matplotlib, 텍스트 기반도 가능)

**사용자 피드백 반영**: 사용자가 "IT 예측 틀렸다"고 피드백하면, 자동 정확도 체크와 교차 검증. 자동 계산과 사용자 체감이 다르면 "사용자 체감 불일치" 플래그.

**Brier Index 간소화 버전**: 전문 Brier score(확률적 예측의 제곱 오차 평균)는 비전문가에게 이해하기 어려우므로, "N개 예측 중 M개 적중 (M/N %)" 형태의 직관적 정확도로 표현.

#### 경로 B: 관심 섹터 학습 (Interest Learning)

**메커니즘**:
1. 피드백에서 언급된 섹터를 카운트
2. 3주 연속 언급된 섹터 → `config.yaml`의 `watched_sectors`에 자동 추가 제안
3. 관심 섹터는 리포트 Layer 2의 "내 포트폴리오 관련성" 섹션에 자동 포함
4. 관심 섹터의 시그널은 Layer 1 (Telegram 요약)에서 우선 노출

**구현 방식**: 단순 빈도 카운터 + `config.yaml` 업데이트 제안 (자동 적용이 아닌 사용자 승인 후 적용)

#### 경로 C: 시그널 가중치 조정 (Confidence Calibration)

**메커니즘**:
1. 월간 집계 시, "이 STEEPs 유형의 시그널은 정확도가 낮다" 패턴 감지
2. 예: T(기술) 시그널의 3개월 적중률이 45%면, 해당 유형의 확신도에 0.85 보정 계수 적용
3. 예: 두 소스 수렴 시그널의 적중률이 75%면, 수렴 보너스를 현재 +10%에서 +15%로 상향
4. 보정 계수는 `config.yaml`에 저장, 사용자가 수동 오버라이드 가능

**주의**: 이 경로는 Phase 2 이후(M3, KRX 데이터 연동 후)에만 의미 있음. Phase 1에서는 실제 시장 수익률 데이터가 없으므로, 사용자의 정성적 피드백만으로 보정.

### 3.4 피드백 루프 전체 설계도

```
Week N                           Week N+1                        Week N+2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[리포트 N 생성]                   [리포트 N+1 생성]                  [리포트 N+2 생성]
    │                                │                                │
    ▼                                ▼                                ▼
[사용자 읽기]                      [정확도 자동 계산]                  [보정된 확신도 적용]
    │                            "Week N 예측 vs 실제"                    │
    ▼                                │                                │
[의사결정]                           ▼                                │
    │                          [리포트 N+1에                           │
    ▼                           정확도 표시]                           │
[피드백 기록]───────────────────▶[관심 섹터 업데이트]──────────────────▶│
  "반도체 맞았음"                 "반도체 → watched"                    │
  "IT 틀렸음"                    "IT 확신도 보정 -5%"                   │
                                                                      │
                                [월간 집계]──────────────────────────▶│
                                "T 시그널 적중률 45%"                "T 보정 계수 0.85"
```

### 3.5 월간 자가 평가: 6개 정성 품질 게이트

Tetlock의 자기 교정(self-correction) 원칙을 비전문가용으로 단순화한 월간 질문 세트. 매월 마지막 금요일에 Telegram으로 자동 전송.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[InvestScan 월간 자가 평가 — 2026년 3월]

이번 달 리포트 4회 수신, 결정 8건 기록.
자동 정확도: 58% (7/12 섹터 방향 적중)

아래 6개 질문에 1-5점으로 답해주세요.
(Telegram에 숫자만 답장하면 됩니다: "3 4 2 5 3 4")

Q1. 리포트가 투자 결정에 실제로 도움이 되었나?
    1=전혀 아님 ... 5=매우 도움됨

Q2. 리포트 없이 같은 결정을 내렸을 것인가?
    1=동일 결정 ... 5=완전 다른 결정

Q3. 정보량은 적절했나?
    1=너무 적음 ... 5=너무 많음 (3이 최적)

Q4. 행동 체크리스트가 명확했나?
    1=모호함 ... 5=즉시 행동 가능

Q5. 이번 달 가장 좋았던 인사이트 하나를 적어주세요.
    (자유 텍스트)

Q6. 다음 달 리포트에서 바뀌었으면 하는 점 하나를 적어주세요.
    (자유 텍스트)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Q1-Q4 점수의 용도**: 분기별 트렌드 추적. 점수가 3회 연속 하락하면 시스템 설계 재검토 트리거.

**Q5-Q6의 용도**: 사용자가 원하는 것과 시스템이 제공하는 것 사이의 간극 파악. 다음 마일스톤 우선순위에 반영.

---

## 4. 기존 설계와의 통합 포인트

### 4.1 기존 Branch 3.1 Decision Journal과의 관계

Branch 3.1에서 설계된 `journal.py`는 **CLI 기반** (`python journal.py add`)이다. 비코더 사용자에게 이것은 높은 진입 장벽.

**통합 설계**:
- `journal.py`는 그대로 유지 (데이터 저장 백엔드)
- Telegram 봇이 `journal.py`의 상위 인터페이스 역할
- 사용자는 Telegram으로만 상호작용, `journal.py`는 구조화 저장만 담당

```
[사용자] ──Telegram 답장──▶ [Telegram Bot] ──파싱──▶ [journal.py API]
                                                        │
                                                        ▼
                                                [decision_journal.jsonl]
```

### 4.2 기존 리포트 템플릿과의 관계

Branch 3.1의 `weekly-report.md.j2` 템플릿에 Section 0 (행동 체크리스트)를 추가하고, 기존 섹션 번호를 +1.

| 기존 섹션 | 변경 후 |
|----------|--------|
| (없음) | **0. 이번 주 행동 체크리스트** (신규) |
| 1. 핵심 요약 | 1. 핵심 요약 (유지) |
| 2. 섹터별 투자 방향 | 1.5 내 포트폴리오 관련성 (신규, 조건부) |
| 2. 섹터별 투자 방향 | 2. 섹터별 투자 방향 (유지) |
| 3. 주요 신호 Top 10 | 3. 주요 신호 Top 10 (유지) |
| 4. 증거 체인 | 4. 증거 체인 (유지) |
| 5. 주의 사항 | 5. 주의 사항 (유지) |

### 4.3 기존 Notification 설계와의 관계

Branch 3.1-3.2의 Telegram 알림 설계를 확장:

| 기존 설계 | 확장 |
|----------|------|
| 리포트 요약 전송 | + 행동 체크리스트 포함 |
| 단방향 (시스템→사용자) | **양방향** (사용자→시스템 피드백) |
| (없음) | + 금요일 저널 리마인더 |
| (없음) | + 월말 자가 평가 전송 |

### 4.4 config.yaml 확장

```yaml
# ~/.investscan/config.yaml (추가 필드)

# 기존 필드 유지...

user_profile:
  watched_sectors:           # 관심 섹터 (자동 학습 + 수동 추가)
    - 반도체
    - 2차전지
    - 헬스케어
  held_sectors:              # 실제 보유 섹터 (수동 입력)
    - 반도체
    - 2차전지

feedback:
  telegram_enabled: true
  weekly_reminder_day: friday    # 금요일 저널 리마인더
  weekly_reminder_time: "17:00"
  monthly_eval_enabled: true

calibration:
  steeps_correction:         # STEEPs 유형별 보정 계수 (월간 자동 갱신)
    T: 1.0
    E_economic: 0.95
    S: 0.90
    P: 0.85
    E_env: 1.0
    s_security: 1.0
  convergence_bonus: 0.10    # 두 소스 수렴 시 확신도 보너스
  min_action_confidence: 0.50  # 행동 체크리스트 최소 확신도
  max_actions_per_week: 3      # 주간 최대 행동 항목 수
```

---

## 5. 구현 우선순위 제안

이 조사 결과를 기존 Balanced Scenario의 마일스톤에 매핑:

| 항목 | 마일스톤 | LOC 추가 | 난이도 |
|------|---------|---------|-------|
| 리포트 Section 0 (행동 체크리스트) | **M1** (필수) | ~80 (템플릿 + 빌더) | 낮음 |
| Telegram 요약에 행동 체크리스트 포함 | **M1** (필수) | ~30 (기존 notify_telegram.py 수정) | 낮음 |
| Telegram 양방향 피드백 수신 | **M1** (필수) | ~120 (봇 polling + 파서) | 중간 |
| 자연어→저널 변환 (규칙 기반) | **M1** (필수) | ~80 (키워드 매핑) | 낮음 |
| 정확도 자동 추적 | **M2** (KRX 연동 후) | ~150 | 중간 |
| 관심 섹터 자동 학습 | **M2** | ~60 | 낮음 |
| 내 포트폴리오 관련성 섹션 | **M2** | ~50 (config 읽기 + 필터링) | 낮음 |
| 시그널 가중치 보정 | **M3** | ~100 | 중간 |
| 월간 자가 평가 | **M2** | ~80 (Telegram 전송 + 집계) | 낮음 |
| **합계** | | **~750 LOC** | |

기존 Balanced Scenario 총 LOC (~3,200)에 ~750 LOC 추가 → **~3,950 LOC**.
개발 시간 추가: ~20-25시간 (6개월 중 분산).

---

## 6. 핵심 통찰 요약

### 리포트에서 행동까지의 간극이 InvestScan의 가장 큰 위험

현재까지의 설계는 "훌륭한 분석 → 사용자에게 전달"에 집중했다. 그러나 **사용자가 리포트를 받은 후 실제로 행동으로 이어지지 않으면**, InvestScan은 매주 생성되지만 아무도 읽지 않는 PDF 리포트와 같아진다.

### "관망"도 행동이다

행동 체크리스트에 "관망" 항목을 명시적으로 포함하는 것이 중요하다. "이번 주는 아무것도 하지 않는다"는 의식적 결정이어야 하며, "리포트를 무시했다"와 구별되어야 한다.

### 피드백 루프의 핵심은 마찰 최소화

비코더 사용자에게 CLI 명령어, 스프레드시트 기록, 별도 앱 설치를 요구하면 피드백 루프는 2주 안에 죽는다. Telegram 답장 하나로 모든 피드백을 처리하는 것이 생존의 열쇠.

### Tetlock 원칙의 단순화

슈퍼포캐스팅의 핵심(점수 기록, 확률적 사고, 자기 교정)은 강력하지만, 원형 그대로 적용하면 비전문가에게 부담. "N개 중 M개 적중"이라는 직관적 지표로 단순화하되, 누적 데이터가 쌓이면 더 정교한 분석(Brier Index 등)으로 확장 가능.

---

## Sources

- [Dealing with Information Overload: a comprehensive review (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10322198/)
- [Information Overload, Decision Paralysis, And Herding (Weingarten Associates)](https://www.weingartenassociates.com/blog-01/information-overload-decision-paralysis-and-herding)
- [Progressive Disclosure (NN/g)](https://www.nngroup.com/articles/progressive-disclosure/)
- [Progressive Disclosure (IxDF)](https://ixdf.org/literature/topics/progressive-disclosure)
- [Dashboard Design Principles (UXPin)](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
- [The 30-Minute Trading Routine For Busy People (FBS)](https://fbs.com/fbs-academy/traders-blog/the-30-minute-trading-routine-for-busy-people)
- [Morningstar Rating for Stocks](https://www.morningstar.com/investing-terms/morningstar-rating-for-stocks)
- [Superforecasting: How to Upgrade Your Company's Judgment (HBR)](https://hbr.org/2016/05/superforecasting-how-to-upgrade-your-companys-judgment)
- [Making Forecasting Scores Easier to Interpret: Introducing the Brier Index](https://forecastingresearch.substack.com/p/introducing-the-brier-index)
- [What is a Brier Score (Cultivate Labs)](https://www.cultivatelabs.com/crowdsourced-forecasting-guide/what-is-a-brier-score-and-how-is-it-calculated)
- [Good Judgment Open (Forecasting Platform)](https://www.gjopen.com/faq)
- [Free Trading Journal Template (StockBrokers.com)](https://www.stockbrokers.com/education/trading-journal-excel-spreadsheet)
- [Portfolio Performance Review Template (WealthBee)](https://wealthbee.io/learn/portfolio-performance-review-template/)
- [Bloomberg Portfolio Analytics](https://www.bloomberg.com/professional/products/bloomberg-terminal/portfolio-analytics/)
- [AlphaSquare (알파스퀘어) Platform](https://alphasquare.co.kr/)
- [월급 흐름으로 만드는 개인 투자 운영체계 (Moments Log)](https://www.momentslog.com/investment/%EC%9B%94%EA%B8%89-%ED%9D%90%EB%A6%84%EC%9C%BC%EB%A1%9C-%EB%A7%8C%EB%93%9C%EB%8A%94-%EA%B0%9C%EC%9D%B8-%ED%88%AC%EC%9E%90-%EC%9A%B4%EC%98%81%EC%B2%B4%EA%B3%84-%EB%B3%80%EB%8F%99%EC%9E%A5%EC%97%90)
- [Analysis Paralysis for Self-Directed Investors (Unleashed Financial)](https://www.unleashedfinancial.com/blog/analysis-paralysis-in-investing/)
- [Telegram Bot for Trading Signals (Medium)](https://nigelthornton1.medium.com/telegram-bot-for-trading-signals-a-comprehensive-guide-to-automated-market-alerts-in-2025-7de07778fe36)
- [Build A Real-Time Stock Alert Telegram Bot (InsightBig)](https://www.insightbig.com/post/build-a-real-time-stock-alert-telegram-bot-with-python)
