# InvestScan 주간 운영 End-to-End 시퀀스 + 비용 구조 심층 ��석

**Date**: 2026-03-28
**Context**: InvestScan 3-system pipeline on MacBook M5 Max 64GB
**Scope**: 실행 타임라인, API/구독 비용, 실패 시나리오 대응

---

## 1. 전체 파이프라인 타임라인

### 1.1 3개 시스템 실행 시간 상세

| System | Phase | Duration | Dependency | Notes |
|--------|-------|----------|------------|-------|
| **EnvironmentScan** | WF1 General Scan | ~30 min | Claude API + Web | Blogs, policy docs, patents |
| | WF2 arXiv Scan | ~30 min | Claude API + arXiv API | Academic papers |
| | WF3 Naver Scan | ~30 min | Claude API + Naver | Korean news crawl |
| | WF4 MultiGlobal Scan | ~30 min | Claude API + 32+ sites | Global news sites |
| | **Subtotal** | **~120 min** | | WF1-WF4 순차 실행 (4 workflows) |
| **GlobalNews-Crawling** | Stage: Crawl | ~53 min | 116 sites | Rate-limited, anti-block |
| | Stage: Analyze (8 stages) | ~45 min | CPU-bound (local ML) | SBERT, BERTopic, Prophet, PCMCI |
| | **Subtotal** | **~98 min** | | Crawl -> Analyze 순차 |
| **InvestScan (Bridge+Report)** | Signal Normalization | ~2 min | Local (JSON/Parquet I/O) | |
| | Investment Synthesis | ~5-10 min | Rule-based + Claude | Sector mapping, scoring |
| | Report Generation | ~3-5 min | Claude (report writing) | EN + KO |
| | Korean Translation | ~3-5 min | Claude (@translator) | |
| | **Subtotal** | **~15-25 min** | | |

### 1.2 순차 실행 타임라인 (현재 권장 아키텍처)

네트워크 I/O가 병목이므로 순차 실행이 기본 권장사항이다. 두 시��템이 동시에 웹 크롤링하면 가정용 인터넷 대역폭을 포화시키고, 안티봇 차단 확률이 급증한다.

```
07:00  [Start] Pipeline initiated
07:00  ── EnvironmentScan ───────────────────────────
07:00  │ WF1 General Scan                    [~30 min]
07:30  │ WF2 arXiv Scan                      [~30 min]
08:00  │ WF3 Naver News Scan                 [~30 min]
08:30  │ WF4 Multi&Global News Scan          [~30 min]
09:00  ── EnvironmentScan Complete ──────────────────
09:00  ── GlobalNews-Crawling ──────────────────────
09:00  │ Crawl 116 sites                     [~53 min]
09:53  │ Analyze (8-stage NLP pipeline)      [~45 min]
10:38  ── GlobalNews Complete ──────────────────────
10:38  ── InvestScan Bridge ─────────���──────────────
10:38  │ Signal Normalization                [~2 min]
10:40  │ Investment Synthesis                [~10 min]
10:50  │ Report Generation + Translation     [~10 min]
11:00  ── Pipeline Complete ────────────────────────

Total: ~4시간 (240분)
```

**월요일 아침 7시 실행 시 완료 시각: ~11:00 AM**

### 1.3 병렬 실행 타임라인 (64GB RAM 여유 시)

EnvScan과 GlobalNews는 데이터 독립적이므로 이론적 병렬 실행이 가능하다. 다만 네트워크 경합 리스크가 있다.

```
07:00  [Start] Pipeline initiated (parallel)
07:00  ── EnvironmentScan ──────────────────┐
07:00  │ WF1-WF4 (sequential)  [~120 min]  │
       │                                    │
07:00  ── GlobalNews-Crawling ─────────────┤ (parallel)
07:00  │ Crawl [~53 min]                   │
07:53  │ Analyze [~45 min]                 │
08:38  ── GlobalNews Complete ─────────────┘
       │                                    │
09:00  ── EnvironmentScan Complete ─────────┘
09:00  ── InvestScan Bridge ────────────────
09:00  │ Normalize + Synthesize + Report   [~25 min]
09:25  ── Pipeline Complete ────────────────

Total: ~2시간 25분 (145분)
완료 시각: ~09:25 AM (KST 장 시작 전 가능)
```

**병렬 실행의 리스크**:
- 네트워크 대역폭 포화 -> 양�� 크롤링 속도 저하
- 안티봇 차단 확률 증가 (동일 IP에서 다수 요청)
- 디버깅 어려움 (두 시스템 동시 로깅)
- `analysis-monolithic-architecture.md`에서 **순차 실행을 명시적으로 권장**

**결론**: MVP에서는 순차 실행(~4시간), 안정화 후 병렬 실행(~2.5시간) 전환 검토

### 1.4 Human Checkpoint 분석 (EnvironmentScan)

EnvironmentScan의 master-orchestrator는 총 **9회의 human checkpoint**를 갖고 있다.

각 WF당 3회 (필터링 검토, 분석 결과 검토, 보고서 승인) = WF1~WF4에 걸쳐 분포:

| Checkpoint | Step | Type | Auto-approve 조건 |
|-----------|------|------|-----------------|
| 1 | Step 1.4 (WF1 필터링) | Optional | AI confidence >= 0.9 in deduplication |
| 2 | Step 1.8 (WF1 분석) | Required | Analysis passes L2 validation |
| 3 | Step 1.12 (WF1 보고서) | Required | L2 review passes + pACS >= 70 |
| 4 | Step 2.4 (WF2 필터링) | Optional | Same as #1 |
| 5 | Step 2.8 (WF2 분석) | Required | Same as #2 |
| 6 | Step 2.12 (WF2 보고서) | Required | Same as #3 |
| 7 | Step 3.x (WF3) | Required | Same pattern |
| 8 | Step 4.x (WF4) | Required | Same pattern |
| 9 | Step 5.x (Integration) | Required | Integrated report final approval |

**자동화 가능성**:
- EnvironmentScan은 **Autopilot Mode**를 지원한다 (AGENTS.md 5.1).
- Autopilot 활성화 시, (human) 단계를 자동 승인하되 rationale을 로깅한다.
- 4계층 품질 보장(L0->L1->L1.5->L2)이 자동 실행되므로, autopilot으로도 품질이 보장된다.
- **결론**: Autopilot ��드를 활성화하면 human intervention 없이 120분 완주 가능. 사후에 보고서를 인간이 검��하는 패턴으로 전환.

---

## 2. Claude API 비용 구조

### 2.1 현재 Anthropic Claude API 가격 (2026년 3월 기준)

| Model | Input (per MTok) | Output (per MTok) | Context Window | 특징 |
|-------|------------------|--------------------|----------------|------|
| Claude Haiku 4.5 | $1.00 | $5.00 | 1M tokens | Fastest, cheapest |
| **Claude Sonnet 4.6** | **$3.00** | **$15.00** | 1M tokens | Balanced (코딩 권장) |
| Claude Opus 4.6 | $5.00 | $25.00 | 1M tokens | Most capable |
| (Legacy) Claude 3.5 Sonnet | $3.00 | $15.00 | 200K | Deprecated |

**비용 절감 옵션**:
- Prompt Caching: 90% 입력 비용 절감
- Batch API: 50% 할인 (비동기 처리)
- 두 가지 결합 시 최��� 95% 절감 가능

### 2.2 EnvironmentScan 토큰 사용량 추정

EnvironmentScan은 37개 에이전트가 4개 워크플로우를 실행하는 LLM-driven 시스템이다. 각 에이전트는 Claude API를 호출하여 추론한다.

**WF 1개당 추정 토��� 사용량**:

| Step | Agent 수 | 평균 입력 토큰 | 평균 출력 토큰 | ��계 |
|------|---------|--------------|--------------|------|
| 데이터 수집 & 파싱 | 2-3 | ~15K | ~5K | ~60K in / ~15K out |
| 중복 필터링 | 1-2 | ~20K | ~3K | ~40K in / ~6K out |
| 분류 & 구조화 | 3-4 | ~25K | ~15K | ~100K in / ~60K out |
| 영향도 분석 | 2-3 | ~20K | ~10K | ~60K in / ~30K out |
| 우선순위 결정 | 1-2 | ~15K | ~5K | ~30K in / ~10K out |
| 보고서 생성 | 1-2 | ~30K | ~20K | ~60K in / ~40K out |
| 품질 검증 (L2/L3) | 2-3 | ~20K | ~8K | ~60K in / ~24K out |
| **WF 1개 소계** | | | | **~410K in / ~185K out** |

**4개 WF + Integration 합산**:

| Component | Input Tokens | Output Tokens |
|-----------|-------------|--------------|
| WF1 (General) | ~410K | ~185K |
| WF2 (arXiv) | ~410K | ~185K |
| WF3 (Naver) | ~410K | ~185K |
| WF4 (MultiGlobal) | ~410K | ~185K |
| Integration (merge) | ~200K | ~100K |
| **합계** | **~1.84M** | **~840K** |

**EnvironmentScan 1회 실행 API 비용** (Sonnet 4.6 기준):
- Input: 1.84M tokens x $3.00/MTok = **$5.52**
- Output: 0.84M tokens x $15.00/MTok = **$12.60**
- **총: ~$18.12 / 1회 실행**

### 2.3 InvestScan Bridge API 비용 추정

InvestScan 자체 파이프라인(Normalization -> Synthesis -> Report)도 Claude를 사용한다.

| Step | Input Tokens | Output Tokens | Notes |
|------|-------------|--------------|-------|
| Signal Normalization | ~0 (Python only) | ~0 | 순수 Python 처리 |
| Investment Synthesis | ~100K | ~50K | Claude reasoning for sector mapping |
| Report Generation | ~80K | ~30K | Template + Claude 서술 |
| Korean Translation | ~40K | ~35K | @translator 서브에이전트 |
| Review (L2) | ~50K | ~15K | @reviewer |
| **합계** | **~270K** | **~130K** |

**InvestScan Bridge 1회 비용** (Sonnet 4.6):
- Input: 0.27M x $3.00 = $0.81
- Output: 0.13M x $15.00 = $1.95
- **총: ~$2.76 / 1회 실행**

### 2.4 Claude Code 구독 vs API 비용 ��교

**핵심 질문**: Claude Code 구독($20-200/월)으로 API 비용이 포함되는가?

| 구독 Plan | 월 비용 | Claude Code 사용 | API 포함 여부 | 비고 |
|-----------|--------|-----------------|-------------|------|
| **Pro** | $20/월 | 포함 (기본 한도) | 구독 한도 내 포함 | ~44K tokens/5hr window |
| **Max 5x** | $100/월 | 포함 (5x Pro) | 구독 한도 내 포함 | ~88K tokens/5hr window |
| **Max 20x** | $200/월 | 포함 (20x Pro) | 구독 한도 내 포함 | ~220K tokens/5hr window |
| **API (별도)** | 종량제 | 미포함 | 순수 API ���금 | Per-token billing |

**중요 구분**:
- **Claude Code를 구독(Pro/Max)으로 사��할 경���**: EnvironmentScan이 Claude Code 내에서 에이전트로 실행되므로, **구독 한도 내에서 토큰을 소비**한다. 별�� API 비용이 발생하지 않는다.
- **Claude Code를 API key로 사용할 경우**: 토큰당 과금이 발생한다.

**EnvironmentScan은 Claude Code의 에이전트 시스템으로 실행된다** (slash command `/env-scan:run`). 따라서:
- Pro($20/월) 구독 시: 5시간 윈도우 44K 토큰 ���도로 **EnvironmentScan 1회 실행(~2.7M tokens) 불가능**
- Max 5x($100/월) 구독 시: 88K/5hr로도 부족
- Max 20x($200/월) 구독 시: 220K/5hr로도 부족 (2.7M tokens 필요)
- **실질적으로 Max 20x에서도 rate limit에 걸릴 수 있다**

**현실적 시나리오**:
1. **구��(Max 20x)으로 실행**: 220K/5hr window이지만 rolling reset이므로, 4시간 파이프라인 동안 점진적으로 소비. 주간 1�� 실행이면 주간 cap에 여유 있을 가능성 높음. 단, Opus 모델 별도 weekly cap 존재.
2. **API key로 실행**: 토큰당 ~$18-21 비용. Rate limit은 API tier에 따라 유연.

### 2.5 주간 1회 실행 총 API 비용 요약

| Scenario | EnvironmentScan | GlobalNews | InvestScan Bridge | 주간 합계 | 월간 합계 |
|----------|----------------|------------|------------------|---------|---------|
| **Max 20x 구독** | 구독 포함 | $0 (local ML) | 구독 포함 | **$0** (월 $200 고정) | **$200** |
| **API key (Sonnet 4.6)** | ~$18.12 | $0 | ~$2.76 | **~$20.88** | **~$83.52** |
| **API key (Haiku 4.5)** | ~$6.04 | $0 | ~$0.92 | **~$6.96** | **~$27.84** |
| **API + Prompt Cache** | ~$2.09-4.18 | $0 | ~$0.28-0.55 | **~$2.37-4.73** | **~$9.48-18.92** |

---

## 3. 월간 총 운영 비용 추정

### 3.1 필수 비용

| 항목 | 월 비용 | 비고 |
|------|--------|------|
| **Claude 구독 (Max 20x)** | $200.00 | EnvironmentScan + InvestScan 포함 |
| **SerpAPI** | $0.00 | Google Scholar는 현재 disabled. arXiv는 무료 API ��용 |
| **전기세** | ~$1-2 | M5 Max ~40W x 4hr/week = 0.64 kWh/week = 2.56 kWh/month |
| **인터넷** | 기존 비용 | 추가 비용 없음 |
| **합계 (구독 모델)** | **~$201-202/월** | |

### 3.2 대안: API key 모델

| 항목 | 월 비용 | 비고 |
|------|--------|------|
| **Claude API (Sonnet 4.6)** | ~$83.52 | 주간 1회, 4주 |
| **Claude Pro 구독** (일상 사용) | $20.00 | 일상 코딩/대화용 |
| **SerpAPI** | $0.00 | 미사용 |
| **전기세** | ~$1-2 | |
| **합계 (API 모델)** | **~$104-106/월** | |

### 3.3 최소 비용 모델 (Haiku + Prompt Caching)

| 항목 | 월 비용 | 비고 |
|------|--------|------|
| **Claude API (Haiku 4.5 + Cache)** | ~$9.48-18.92 | 최대 절감 |
| **Claude Pro 구독** | $20.00 | 일상 사용 |
| **합계** | **~$30-40/월** | 품질 트레이드오프 있음 |

### 3.4 SerpAPI 상세

| Plan | 월 비용 | 검색 횟수/월 | InvestScan 사용 여부 |
|------|--------|------------|-------------------|
| Free | $0 | 100회 | Google Scholar disabled 상태이므로 불필요 |
| Developer | $75 | 5,000회 | Google Scholar 활성화 시에만 필요 |
| Small Business | $150 | 15,000회 | 과도 |

**현재 상태**: EnvironmentScan의 `sources.yaml`에서 Google Scholar는 `enabled: false`로 설정되어 있다. arXiv는 무료 API를 직접 호출한다. **따라서 SerpAPI 비용은 $0이다.**

Google Scholar를 활성화하려면 SerpAPI Developer plan ($75/월) 필요. 그러나 arXiv WF2가 이미 학술 논문 영역을 커버하므로 우선순위 낮음.

### 3.5 비용 비교표

| Model | 월 비용 | 장점 | 단점 |
|-------|--------|------|------|
| **Max 20x 구독** | $200 | 고정비, 일상 사용 겸용, rate limit 최대 | 비용 고정 (미사용시 손해) |
| **API + Pro 구독** | $104 | 사용량 비례 과금, 유연 | Rate limit 관리 필요 |
| **Haiku API + Pro** | $30-40 | 최저 비용 | 품질 저하 가능 (Haiku < Sonnet) |
| **API + Prompt Cache** | $30-40 | 좋은 균형 | 캐시 설정 복잡도 |

**권장**: 초기 MVP는 **Max 20x ($200/월)** 구독으로 시작. 안정화 후 실제 사용 패턴을 보고 API 모델로 전환 검토.

---

## 4. 실패 시나리오별 재실행 전략

### 4.1 launchd 실행 시 Mac이 꺼져있으면?

| 상태 | launchd 동작 | 대응 |
|------|-------------|------|
| **Mac이 Sleep 상태** | `StartCalendarInterval` 사용 시, **wake 후 누적된 미실행 작업을 1회로 합쳐서 실행**한다 | 정상 동작. Mac이 결국 깨어나면 파이프라인 시작됨 |
| **Mac이 완전 Shutdown** | **실행하지 않는다.** 다음 예정 시각까지 대기 | 매주 같은 시간�� Mac이 ���져 있도록 해야 함 |
| **Mac이 Lid Closed (Sleep)** | Sleep 중에는 실행 불가. Lid open 시 즉시 실행 | macOS의 Power Nap은 launchd를 지원하지 않음 |

**대응 전략**:
1. macOS의 "자동 시작" 설정: System Settings > Energy > Schedule > "Start up or wake" on Sunday 7:50 PM
2. 또는 `pmset` 명령으로 스케줄 wake: `sudo pmset repeat wake SU 19:50:00`
3. launchd plist의 `StartCalendarInterval`가 Sunday 20:00으로 설정되면, 7:50 PM��� 자동 wake -> 20:00에 launchd 트리거

**권장 plist 설정** (이미 `phase2-3-4-external-integration-guide.md`에 정의됨):
- `StartCalendarInterval`: Weekday=0 (Sunday), Hour=20, Minute=0
- `KeepAlive`: false (1회 실행 후 종료)
- `Nice`: 10 (낮은 우선순위)

### 4.2 네트워크 단절 시

| System | Checkpoint 유무 | 네트워��� 단절 시 동작 | 재실행 전략 |
|--------|---------------|-------------------|-----------|
| **EnvironmentScan** | **있음** (WF별 checkpoint, Context Preservation System) | WF 중간에 실패 -> 해당 WF만 재실행 가능. 다만 Claude Code 세션이 끊기면 context loss | `--resume` 플래그로 완료된 WF 건너뛰기. Context Preservation hooks가 자동 복원 |
| **GlobalNews-Crawling** | **있음** (stage별 checkpoint) | Crawl 단계에서 실패 시 부분 크롤링 결과 보존. `--mode analyze --stage N`으로 특정 stage부터 재시작 가능 | `--mode full --date {date}`로 전체 재실행 또는 `--stage N`으로 부분 재실행 |
| **InvestScan Bridge** | **있음** (Pipeline State JSON) | Python 스크립트이므로 네트워크 불필요 (로컬 파일 I/O). Claude API 호출 단계만 실패 가능 | `--resume` 모드로 마지막 완료 step부터 재시작 |

**재실행 시나리오 상세**:

```
Scenario A: EnvironmentScan WF2 도중 네트워크 단절
  -> WF1 output은 보존됨 (파일 기반)
  -> WF2 부분 결과 존재할 수 있음
  -> 재실행: /env-scan:run --resume (WF1 skip, WF2부터)
  -> 또는: /env-scan:run-arxiv (WF2만 단독 실행)

Scenario B: GlobalNews crawl 50번째 사이트에서 네트워크 단절
  -> data/raw/{date}/all_articles.jsonl에 50개 사이트 결과 보존
  -> main.py는 error handling으로 실패 사이트 skip + 로깅
  -> 재실행: python main.py --mode crawl --date {date}
  -> 이미 크롤링된 사이트는 dedup으로 건너뛸 수 있음

Scenario C: InvestScan report generation 중 Claude API 실패
  -> pipeline_state.json에 normalize/synthesize 완료 기록됨
  -> 재실행: python -m investscan run --resume --date {date}
  -> Report generation step만 재실행
```

### 4.3 부분 실패 시 전체 재실행 vs 부분 재실행

| 실패 지점 | 권장 전략 | 이유 |
|----------|---------|------|
| **EnvScan WF1 실패** | WF1만 재실행 (`/env-scan:run-general`) | WF2-4는 독립적 |
| **EnvScan WF3 실패** | WF3만 재실행 (`/env-scan:run-naver`) | 네이버 전용 워크플로우 |
| **EnvScan Integration 실패** | Integration만 재실행 | WF1-4 output 보존됨 |
| **GlobalNews Crawl 실패** | 전체 재실행 (`--mode full`) | 부분 크롤링은 분석 품질 저하 |
| **GlobalNews Analyze Stage 4 실패** | `--mode analyze --stage 4`부터 | 이전 stage output 보존 |
| **InvestScan Normalize 실패** | Normalize부터 재실행 (`--resume`) | Source data 변경 없음 |
| **InvestScan Report 실패** | Report만 재실행 (`--step report`) | Synthesis output 보존 |

### 4.4 Graceful Degradation (부분 데이터로 실행)

InvestScan은 **단일 소스만으로도 보고서 생성 가능**하도록 ���계해야 한다:

| Available Data | Report Quality | 동작 |
|---------------|---------------|------|
| EnvScan + GlobalNews (정상) | Full quality | 양쪽 시그널 교차 검증 |
| EnvScan only | Degraded (diverse but no mass-market coverage) | GlobalNews 부재 경고 포함 |
| GlobalNews only | Degraded (mass-market but no specialized sources) | EnvScan 부재 경고 포함 |
| Neither | **Abort** | 데이터 없이 보고서 생성 불가 |

`analysis-monolithic-architecture.md` Risk 1에서 이미 이 설계를 명시:
> "Build the synthesis layer to produce useful output even with only one source system's data."

### 4.5 자동 재시도 예산 (Bounded Retry)

| Component | Max Retry | Retry 간격 | Escalation |
|-----------|----------|-----------|-----------|
| EnvScan 개별 WF | 2회 | 5분 대기 | Human notification |
| GlobalNews Crawl | 1회 (전��) | 10분 대기 | Skip and use available data |
| GlobalNews Analyze Stage | 2회 | 1분 대기 | Skip stage, degraded output |
| InvestScan Normalize | 3회 | 즉시 | Abort (parser bug 의심) |
| InvestScan Synthesis | 2회 | 1분 대기 | Degraded report (fewer sectors) |
| InvestScan Report | 2회 | 1분 대기 | Raw data dump 대신 제공 |

---

## 5. 종합 의사결정 매트릭스

### 5.1 실행 빈도별 비용 비교

| 실행 빈도 | 월간 API 비용 (Sonnet) | 월간 API 비용 (Haiku) | Max 20x 구독 대비 | 권장 |
|----------|---------------------|---------------------|----------------|------|
| 주 1회 | ~$83.52 | ~$27.84 | 구독이 $117 비쌈 | API (비용 우선) 또는 구독 (편의 우선) |
| 주 2회 | ~$167.04 | ~$55.68 | 구독이 $33 비쌈 | 구독 권장 (편의 + 일상 사용) |
| 주 3회+ | ~$250+ | ~$83+ | **구독이 저렴** | 구독 필수 |

### 5.2 최종 권장 운영 모델

**Phase 1 (Month 1-3, MVP)**:
- Claude Max 20x 구독 ($200/월)
- 주 1회 일요일 저녁 실행 (launchd, Sunday 20:00)
- SerpAPI 불필요 ($0)
- 순차 실행 (~4시간)
- 총 월간 비용: **~$202**

**Phase 2 (Month 4+, 안정화 후)**:
- 실제 토큰 사용량 측정 후 API 전환 검토
- Prompt Caching 도입으로 비용 절감
- 병렬 실행 테스트 (안정적이면 ~2.5시간으로 단축)
- 총 월간 비용: **$30-104** (최적화 수준에 따라)

---

## Sources

- [Anthropic API Pricing (Official)](https://platform.claude.com/docs/en/about-claude/pricing)
- [Claude Plans & Pricing](https://claude.com/pricing)
- [Claude Code Pricing 2026 (SSD Nodes)](https://www.ssdnodes.com/blog/claude-code-pricing-in-2026-every-plan-explained-pro-max-api-teams/)
- [Claude API Pricing Breakdown (Metacto)](https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration)
- [Claude Code Rate Limits (Sitepoint)](https://www.sitepoint.com/claude-code-rate-limits-explained/)
- [Using Claude Code with Pro/Max (Anthropic Help)](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [SerpAPI Pricing](https://serpapi.com/pricing)
- [launchd Tutorial](https://launchd.info/)
- [Apple Developer: Scheduling Timed Jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)
- [macOS launchd sleep/wake behavior (Apple Forums)](https://developer.apple.com/forums/thread/52369)
