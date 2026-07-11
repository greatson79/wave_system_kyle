# InvestScan PRD 최종 심층조사 통합 문서

> **생성일**: 2026-03-28 | **최종 갱신**: 2026-03-28 (Round 6 반영)
> **소스**: `/prompt/prd-research/` 39개 파일 (27,195줄) 전수 분석 + Round 6 추가 심층조사 5건
> **목적**: PRD.md 작성을 위한 **단일 참조 문서** (Single Source of Truth)
> **라운드**: R1(소스 시스템) + R2(경쟁우위) + R3(기술이론) + R4(구현) + R5(외부연동) + R6(성찰 — 종목추천·비코더UX·규제·검증·자동구현) + **R7(2차 성찰 — 업스트림부트스트랩·스키마검증·모놀리식통합)**

---

## Table of Contents

- [Part I: 제품 정체성](#part-i-제품-정체성)
- [Part II: 경쟁 환경 분석](#part-ii-경쟁-환경-분석)
- [Part III: 사용자 분석](#part-iii-사용자-분석)
- [Part IV: 기술 아키텍처 결정](#part-iv-기술-아키텍처-결정)
- [Part V: 이론적 기반](#part-v-이론적-기반)
- [Part VI: 구현 계획](#part-vi-구현-계획)
- [Part VII: 외부 연동 계획](#part-vii-외부-연동-계획)
- [Part VIII: 리스크 레지스터](#part-viii-리스크-레지스터)
- [Part IX: 교차 라운드 긴장 해소](#part-ix-교차-라운드-긴장-해소)
- [Part X: 미해결 질문과 추가 조사 영역](#part-x-미해결-질문과-추가-조사-영역)
- [Part XI: PRD 작성 권고사항](#part-xi-prd-작성-권고사항)
- [Part XII: 종목 추천 Bridge 방법론 (R6)](#part-xii-종목-추천-bridge-방법론-r6)
- [Part XIII: 비코더 자동구현 사용자 경험 설계 (R6)](#part-xiii-비코더-자동구현-사용자-경험-설계-r6)
- [Part XIV: 한국 법적 규제 분석 (R6)](#part-xiv-한국-법적-규제-분석-r6)
- [Part XV: 검증 방법론 — 백테스팅 없는 정확도 측정 (R6)](#part-xv-검증-방법론--백테스팅-없는-정확도-측정-r6)
- [Part XVI: workflow.md 자동구현 설계 패턴 (R6)](#part-xvi-workflowmd-자동구현-설계-패턴-r6)
- [Part XVII: 모놀리식 아키텍처 — 업스트림 통합 설계 (R7)](#part-xvii-모놀리식-아키텍처--업스트림-통합-설계-r7)
- [Part XVIII: 업스트림 시스템 현황 + 비코더 부트스트래핑 (R7)](#part-xviii-업스트림-시스템-현황--비코더-부트스트래핑-r7)
- [Part XIX: 스키마 검증 — 실측 수정 사항 (R7)](#part-xix-스키마-검증--실측-수정-사항-r7)
- [Part XXIV: PRD.md 범위 한정 지침 — 불필요 항목 성찰 (R8)](#part-xxiv-prdmd-범위-한정-지침--불필요-항목-성찰-r8)
- [Part XXV: 적대적 성찰 — 공격·방어·개선안 (R9)](#part-xxv-적대적-성찰--공격방어개선안-r9)
- [Part XXVI: 최종 성찰 — 6가지 필살기 (R10)](#part-xxvi-최종-성찰--6가지-필살기-r10)

---

# Part I: 제품 정체성

## 1.1 제품 개요

| 항목 | 내용 |
|------|------|
| **제품명** | InvestScan — 한국시장 투자방향 + 종목 관찰 AI 매크로 인텔리전스 |
| **핵심 자산** | EnvironmentScan (v2.5.0, 4 WF, 37 agents) + GlobalNews-Crawling (116 sites, 8-stage NLP) |
| **실행 환경** | 100% 로컬 (MacBook M5 Max 64GB), **SaaS 절대 아님** |
| **최종 산출물** | Claude Code workflow.md → 자동화된 주간 투자방향 리포트 + 섹터별 종목 워치리스트 |
| **개발자 프로필** | 비코더 (코드 구현 불가), 솔로, 파트타임 (주 2-4시간), 목사, 주 업무 별도 |
| **구현 방식** | Claude Code가 workflow.md를 읽고 **전체 시스템을 자동 구현** — 사용자는 코딩 불필요 |

## 1.2 포지셔닝: 카테고리 창조자

> **확정 포지셔닝**: AlphaSquare 경쟁자가 **아니다**. "로컬 매크로 투자 인텔리전스"라는 **새 카테고리를 정의**하는 도구.

| 프레임 | 설명 |
|--------|------|
| **망원경 vs 현미경** | AlphaSquare = 현미경 (개별 종목 상세 분석). InvestScan = 망원경 (거시적 방향성) |
| **"월등히 뛰어난"의 재정의** | 남들이 하는 것을 더 잘해서가 아니라, **아무도 하지 않는 것을 하기 때문에** 월등하다 |
| **핵심 비유** | "AlphaSquare는 물고기를 준다. InvestScan은 바다를 읽는 법을 주고 + 잡을 물고기까지 알려준다" |
| **경쟁 비교 금지** | AlphaSquare와 같은 차원(17개)에서 비교하지 말 것 — 11차원에서 패배 |
| **R6 확장** | 망원경(매크로 방향) **+** 종목 워치리스트(팩터 기반) = 양방향 가치 제공. 단, "추천" 표현 금지 → "데이터 기반 관찰 목록" |

**PRD 권장**: "AlphaSquare 대비 월등" 프레임 **삭제** → "AlphaSquare가 답하지 못하는 질문에 답하고, 그 답에 기반한 종목 관찰 목록까지 제공하는 도구"로 리포지셔닝.

> 소스: `phase2-consolidated-discussion.md`, `biz-sustainable-analysis.md`, `cautious-superiority-challenge.md`

## 1.3 시장 기회의 빈 사분면

**아무도 차지하지 않은 교차점**:
- 매크로 스캐닝 + 로컬 실행 + 증거 체인 + 교차 도메인 분석

**8대 시장 공백** (경쟁 지도 분석):

1. Explainable AI (최우선) — 현재 WHY 설명하는 한국 앱 **없음**
2. 멀티타임프레임 방향 — 단기신호 vs 장기ETF 사이의 공백
3. 투명한 정확도 추적
4. 비용 효율 AI 분석 (한국 3-10배 비쌈)
5. 한국+미국 통합 커버리지
6. 진정한 개인화
7. 대안 데이터 통합
8. 프로세스 지향 AI (종목 추천이 아닌 사고 과정 재설계)

**InvestScan이 유일하게 점유하는 공백**: 투자를 위한 환경 스캐닝 = **아무도 하지 않는 영역**

> 소스: `competitive-landscape-map.md`, `overwhelmingly-superior-investment-app.md`

## 1.4 소스 시스템 역량 (기존 자산)

### EnvironmentScan v2.5.0

| 항목 | 수치 |
|------|------|
| 코어 LOC | ~25,528 (40 모듈) |
| 스캐너 | 1,837 LOC (arXiv, RSS, Federal Register, LLM classifier) |
| 워크플로우 | 4개 독립 WF (General/arXiv/Naver/MultiGlobal) |
| 에이전트 | Master Orchestrator + 37개 worker agents |
| 분석 프레임워크 | STEEPs 6분류, FSSF 8타입, Three Horizons, Tipping Point Detection |
| 신뢰도 | pSST 점수 (0-100), 4단계 품질 방어 |
| 산출물 | Markdown + JSON 신호 DB, 이중언어 EN/KR |
| 총 신호 | **509개** (17개 소스), T=400, P=225, E=76, S=63, E_env=25, s=7 |
| 실행 시간 | ~120분 (Claude API 의존) |
| 모듈 구성 | 36개 Python 모듈, 22개 검증 스크립트, 12개 YAML 설정 |

### GlobalNews-Crawling

| 항목 | 수치 |
|------|------|
| 분석 LOC | 15,772 (8 stage + 파이프라인) |
| 크롤링 LOC | 15,699 (22 모듈, 스텔스 브라우저, UA manager) |
| 유틸리티 | 32개 스크립트 |
| 소스 | **116개 뉴스사이트**, 10개 지역 그룹, **14+ 언어** |
| NLP 기법 | **56개** (BERTopic, Prophet, PCMCI, SBERT, Burst Detection 등) |
| 신호 분류 | 5-Layer (L1_fad → L5_singularity), 7-state lifecycle |
| 산출물 | Parquet (ZSTD) + SQLite (FTS5+vec) + DuckDB |
| 실행 시간 | ~53분 크롤링 + ~45분 분석 |
| API 비용 | **$0** |
| 총 모듈 | **171개 Python 모듈 (~48,800 LOC)** |

### 두 시스템 합계

| 항목 | 수치 |
|------|------|
| 총 LOC | **~50,900-59,000** (측정 방법에 따라 차이) |
| 총 소스 | **150+** (116 뉴스 + 32+ 글로벌 + arXiv + 특허 + 정책) |
| 총 언어 | **14+** |
| NLP 기법 | **56종** |
| 상태 | **Production-ready**, 변경 없이 사용 가능 |

### 핵심 통합 과제

**Schema 불일치**: EnvScan JSON (STEEPs + pSST 0-100) ↔ GlobalNews Parquet (5-Layer + confidence 0-1)

**발견된 데이터 포맷**: Round 3에서 2가지로 추정했으나, Round 4에서 **6가지 포맷** 확인:

| 소스 | pSST 스케일 | STEEPs 코드 형식 |
|------|-----------|-----------------|
| WF1 database.json | 정수 0-100 | 단축 ("T", "E") |
| WF1 output JSON | 정수 0-100 | 장형 ("T_Technological") |
| WF4 database.json | 정수 0-100 | 단축 ("T") |
| WF4 priority-ranked | **부동소수점 0-10** | 장형 |
| WF4 evolution-map | 없음 | — |
| GlobalNews Parquet | **부동소수점 0-1** | signal_layer L1-L5 |

> 소스: `investscan-superiority-architecture.md`, `round1-synthesis.md`, `coding-normalization-sector-mapping.md`

---

# Part II: 경쟁 환경 분석

## 2.1 AlphaSquare 상세 분석

### 기업 정보

| 항목 | 수치 |
|------|------|
| 설립 | 2017-11-06 / CEO 송동환 / 임직원 11-15명 / UNIST 연구자 10명 창업 |
| 총 누적 투자 | **~41억 원 (~$310만)** |
| 투자 이력 | Seed(2020): 3억 / TIPS: 5억 / Pre-A(2021): 13억 / Series A(2025.03): 20억 |
| 사용자 | 누적 가입 **22만 명**, MAU ~12만 (2024), Google Play 5만+ |
| 평점 | App Store/Google Play **4.6/5** |
| 매출 | 2023 H1: 1,063만 → H2: 8,416만 (**692% 성장**), 2024 목표: 연 10억, 2025 목표: 손익분기 |

### 가격표

| 플랜 | 월정액 |
|------|--------|
| Standard | 19,800원 |
| Pro | 39,900원 |
| Premium | 69,900원 |
| Premium 연간 | 670,000원 |
| **5년 TCO** | **419만 원 (~$3,050)** |

### AlphaSquare가 **없는** 기능

- 매크로/환경 스캐닝 없음
- 신호 진화 추적 없음
- 다국어 글로벌 뉴스 없음
- 감성 분석(NLP) 없음
- Python/스크립팅 커스텀 전략 없음
- 포트폴리오 최적화 없음
- ESG 점수 없음

### 사용자 불만

1. 해외 주식 실시간 데이터 제한 (CEO: 데이터 라이센싱 비용 문제)
2. 달러 기준 차트 없음 (원화 기준만)
3. 공급/수요 매매자에게 불리한 구조
4. AI 신뢰성 위험: 예측 정확도 공개 지표 없음

### 비교 스코어카드 (정직한 평가)

| 차원 | 승자 |
|------|------|
| **분석적 차원 6개** (데이터 소스, 언어, 프레임워크, 프라이버시, 비용, 투명성) | **InvestScan** |
| **제품/경험 차원 11개** (설치, 모바일, UX, 속도, 백테스팅, 커뮤니티, 브랜드 등) | **AlphaSquare** |
| **총계 17차원** | AlphaSquare 11 vs InvestScan 6 |

> 소스: `alphasquare-competitive-analysis.md`, `cautious-superiority-challenge.md`

## 2.2 경쟁 지도 (4계층)

### 국내

| 계층 | 주요 앱 | 핵심 수치 |
|------|---------|----------|
| 메가플랫폼 | Toss(MAU 384만), Mirae(MAU 360만), Kiwoom(MAU 343만), Samsung(MAU 284만), Korea Investment(MAU 265만) | AI는 부가 기능 |
| AI 네이티브 | Thinkpool/Rassi(회원 11만, 월 11-22만 원), AlphaSquare(22만), ChoiceStock | AI 핵심이나 정확도 미검증 |
| 로보어드바이저 | Fint(AUM 312억, 105만 회원), Fount(AUM **8,074억 1위**, 58만 회원), AIM(AUM 4,097억, 64만 회원) | ETF 배분 자동화 |
| 퀀트/DIY | Genport/Newsystock(전략 380만개, 월 거래 ~6,500억) | 고기술 장벽 |

### 글로벌

| 앱 | 핵심 수치 |
|-----|----------|
| AlphaSense | 기업 6,000+, S&P 100의 85% 사용, 연 $12K-$51K |
| TradingView | 가입자 **9,000만+**, 스크립트 10만+ |
| Bloomberg Terminal | 연 $22,000-$50,000+, 구독 35만+ |
| Kensho (S&P Global) | **정확히 InvestScan이 주장하는 거시→시장 신호 매핑 수행** |

### 오픈소스 (가장 직접적 경쟁자)

| 앱 | 핵심 수치 |
|----|----------|
| **PRISM-INSIGHT** | GitHub **512스타**, 182포크, 1,008커밋, AGPL-3.0, AI 에이전트 **13개+**, 시즌2 한국 **+244.63% 누적 수익**(시뮬레이션), 승률 45.35%, Telegram 550+, **GeekNews 피처** |
| OpenBB | **25,000+ GitHub 스타**, 50+ 데이터 소스, SOC 2 Type II |
| FinGPT | Llama2/ChatGLM 기반, 훈련 비용 < $300 |
| FinRobot | 4계층 멀티에이전트 |

**PRISM-INSIGHT 위협 평가**:

| 차원 | InvestScan (계획) | PRISM-INSIGHT (기존) |
|------|------------------|---------------------|
| AI 에이전트 | 5-6 (계획) | **13+ (배포됨)** |
| 시뮬레이션 수익 | 없음 | **+244.63%** |
| 거래 실행 | 없음 | KIS API 통합 |
| 커뮤니티 | 없음 | Telegram 550+, GeekNews |
| **환경 스캐닝 추가 시** | — | **InvestScan 마지막 차별점 소멸** |

> 소스: `competitive-landscape-map.md`, `cautious-market-analysis.md`, `cautious-superiority-challenge.md`

## 2.3 구조적 해자 (5가지 복제 불가 요소)

1. **로컬퍼스트**: 클라우드 경쟁사 구독 수익 70-80% 소멸 없이 복제 불가
2. **크로스도메인 합성**: 금융 데이터 파이프라인의 근본 재아키텍처 필요
3. **증거 축적**: 전환 비용은 데이터 잠금이 아닌 **추론 맥락 축적**
4. **멀티에이전트 오케스트레이션**: 기술적 복잡도 장벽
5. **투명성 통한 신뢰**: 신뢰 하락 시장에서 블랙박스 경쟁자가 따를 수 없음

### 시간에 따른 복합 우위 (소급 복제 불가)

- 매주 **600-1,200개 고유 신호** 축적
- 의사결정 일지 = 개인 투자 추론 코퍼스
- 신호 정확도 교정 데이터베이스
- **Month 24 = 추격 불가능**

### 상류 시스템 복제 비용

| 시스템 | LOC | 복제 비용 |
|--------|-----|----------|
| EnvironmentScan v4 | ~23,400 | 3인팀 6-9개월 |
| GlobalNews-Crawling | ~25,400 | 3-4인팀 9-12개월 |
| **합계** | **~48,800** | **6인+ 12-18개월, $500,000+** |

> 소스: `long-term-superiority-architecture.md`, `overwhelmingly-superior-investment-app.md`

## 2.4 시장 데이터

### 한국 투자자 모수

| 항목 | 수치 |
|------|------|
| 증권 계좌 총수 | 7,000만-8,000만 (1인 4-5계좌) |
| 고유 개인 투자자 | ~1,400만 명 |
| 분기 1회+ 거래 활성 | ~500-700만 명 |
| 소매 거래 비중 | ~64% (Korea Times, 2023) |

### MZ세대 이탈

- 20대 투자자: 2021년 204만 → 2022년 180만 → 2023년 25만 추가 이탈
- 이탈 목적지: **미국 주식, 암호화폐** (더 나은 분석 도구로 이동하지 않음)

### 2025-2026 시장 맥락

- KOSPI: 2025년 **+76%** (세계 1위), 2026년 YTD +25%, **6,000 돌파**
- 소매 투자자 2025년 국내 주식 **32% 수익률**
- **역설**: 기존 단순 도구로 수익 → 복잡한 로컬 AI 필요성 감소

### 시장 규모 퍼널 (현실적 추정)

| 단계 | 인구 |
|------|------|
| 한국 주식 투자자 | ~1,400만 |
| 활성 거래자 | ~500-700만 |
| 분석 도구 사용자 | ~100-200만 |
| 로컬 Python/AI 실행 가능자 | ~10-30만 |
| 로컬 AI 시스템 설치 및 유지 **의향** | **~2-5만 (TAM)** |
| 비용 지불 의향 | ~5,000-15,000 (SAM) |
| **Year 1-2 SOM** | **500-2,000명** |

### AI 투자 시장 트렌드

- AI 도구 사용 소매 투자자: **19%** (전년 대비 46% 상승)
- AI 도입 의향: **39%**
- 한국 로보어드바이저 AUM: 3조 4,830억 원 (3배 증가)
- AI 자율 에이전트 신뢰도: **43% → 22%** (급락)
- 소프트웨어 기능 복제 시간: 18개월 → **9-12개월** (피처 차별화 사망)
- 헤지펀드 대안 데이터 지출 2026년 **100억 달러+**
- 멀티에이전트 시스템 문의: Q1 2024→Q2 2025 **1,445% 급증**

> 소스: `cautious-market-analysis.md`, `optimistic-market-analysis.md`, `overwhelmingly-superior-investment-app.md`

---

# Part III: 사용자 분석

## 3.1 핵심 타겟 (Edge Case 페르소나)

### Persona 1: 전업투자자 김재현 (47세)

| 항목 | 상세 |
|------|------|
| 운용자산 | **15억 원** |
| 월 도구 비용 | ~50만 원 (AlphaSquare Pro + 연합인포맥스 + WSJ/FT) |
| 핵심 Pain | 매크로 맥락 없이 종목 추천만 받음 |
| 포기 가능 | 실시간 자동매매, 예쁜 UI, 백테스팅 |
| 가치 기준 | **판단의 질 > 실행 속도** |
| 성공 지표 | STEEPs 분석으로 2주 전 미중 규제 신호 포착 → 3천만 원 손실 회피 |

### Persona 2: 투자 콘텐츠 크리에이터 박서연 (32세)

| 항목 | 상세 |
|------|------|
| 유튜브 구독자 | **8만 명** |
| 유료 멤버십 | 2,000명 (월 9,900원) |
| 핵심 Pain | 모든 크리에이터 동일 AlphaSquare 신호 → **콘텐츠 동질화** |
| 가치 기준 | **분석 깊이 > 편의성** |
| 성공 지표 | 영상 기획 6시간→2시간, 멤버십 75% 증가 |

### Persona 3: 체계적 투자자 이동현 (38세, 네이버 개발자)

| 항목 | 상세 |
|------|------|
| 투자자산 | **5억 원** |
| 월 도구 비용 | AlphaSquare API 39,800원 + QuantConnect |
| 핵심 Pain | AI Score 87 → **"왜 87인지" 블랙박스** |
| 가치 기준 | **투명성 > 편의성** |
| 성공 지표 | 증거 체인 신뢰도 0.8+ 결정 승률 72% vs 감 기반 51% |

### Core 7 Features (3 페르소나 공통)

1. F1: 매크로→투자 시사점 연쇄 분석
2. F2: 116 sites 14개 언어 글로벌 뉴스
3. F3: 신호 진화 타임라인
4. F4: 증거 체인+투명 추론
5. F5: 반론 자동 생성
6. F6: 의사결정 이력+사후 복기
7. F7: 100% 로컬+오픈+$0

> 소스: `user-edge-case-analysis.md`

## 3.2 메인스트림 전환 불가 분석

### 대표 비타겟: 김민수 (35세, IT 대리)

- 투자 3년차, 삼성전자+ETF 3,000만 원, 일일 **30분**
- Python 없음, CLI 없음, 100% 모바일
- **전환 가능성: 99% NO**

### 한국 투자자 니즈 분포

| 유형 | 비율 | InvestScan 관련성 |
|------|------|------------------|
| 단기 종목 추구 | 45-50% | 없음 |
| 종목 확인형 | 30-35% | 거의 없음 |
| **시장 방향성** | **12-15%** | **핵심 타겟** |
| **자산배분 체계적** | **3-5%** | **핵심 타겟** |

**InvestScan 자연 도달 시장: 전체의 1-2%**

### Layer별 도달 범위

| Layer | 도달 가능 % | "월등" 주장? |
|-------|-----------|------------|
| Layer 0: CLI 전용 | 0.5-1% | 해당 그룹 내 YES |
| Layer 1: 주간 리포트 | 5-8% | 부분적 |
| **Layer 1+2: 리포트+웹 대시보드** | **15-20%** | **비로소 비교 가능** |
| Layer 3: 모바일/카카오톡 | 30-40% | Toss/Kakao 정면 경쟁 |

### 메인스트림 채택 최소 조건

1. 주간 한국어 리포트 자동 생성 (읽을 수 있는 형태)
2. "그래서 뭘 하라고?" 답변 (섹터 비중, 관심 종목 등 구체적 액션)
3. 접근 장벽 제거 (최소 웹에서 결과 열람)

> 소스: `user-mainstream-analysis.md`

## 3.3 사용자 세그먼트 적합도

| 세그먼트 | 규모 | InvestScan 적합도 |
|---------|------|------------------|
| 캐주얼 투자자 (Toss/Kakao) | ~500-700만 MAU | 0/10 |
| 액티브 트레이더 (Kiwoom/Mirae) | ~100-200만 | 1/10 |
| 정보 추구자 (Naver Finance) | ~300-500만 | 2/10 |
| AI 신호 구독자 (AlphaSquare/Thinkpool) | ~30-50만 | 4/10 |
| **퀀트 호기심층** (Genport/개발자 투자자) | **5-10만** | **8/10** |
| **정교한 매크로 사고자** | **5,000-2만** | **10/10** |

> 소스: `aggressive-competitive-strategy.md`

## 3.4 총소유비용 (숨겨진 비용) — 현실적 평가

| 비용 유형 | AlphaSquare Premium | InvestScan |
|---------|---------------------|-----------|
| 월정액 | 69,900원 | 0 |
| 필수 하드웨어 | 스마트폰 | MacBook 32GB+ ($2,000+) |
| 설정 시간 | 2분 | 2-4시간 |
| 월 유지보수 | 0 | 2-5시간 |
| 전기세 | N/A | 월 ~5-10달러 |
| Claude API 비용 | N/A | 가변, 월 10-50달러+ |
| 학습 곡선 | 10분 | 20시간+ |

**한국 중위 시급(~18,000원) 기준**: InvestScan 시간 비용만 월 18-36만 원 = AlphaSquare Premium의 **2.5-5배**

> 소스: `cautious-superiority-challenge.md`

---

# Part IV: 기술 아키텍처 결정

## 4.1 권장 시나리오: Balanced (5라운드 최종 합의)

### 3개 시나리오 비교

| 차원 | Conservative | **Balanced (권장)** | Aggressive |
|------|-------------|---------------------|-----------|
| 총 LOC | ~1,500 | **~2,710-3,600** | ~4,850 |
| Dev hours | 30-43 | **60-80** | 75-80 |
| 시간/주 | ~2시간 | **~3시간** | 4+시간 |
| 첫 산출물 | Week 4 | **Week 6** | Week 6 |
| 성공 확률 (M6) | 90%+ | **70-80%** | 40-50% |
| "월등" 신뢰성 | **NO** | **Month 4+ 이후 YES** | YES (도메인 한정) |
| 포기 리스크 | LOW | LOW-MEDIUM | MEDIUM-HIGH |
| 의존성 수 | 3개 | ~8개 | ~15+ |
| STEEPs 포함 | 연기 | **M1 포함** | M1 포함 |

### Balanced 선택 근거 6가지

1. **개발자가 목사로 주 업무 별도** — Aggressive 4+시간/주 보장 불가, Balanced ~3시간/주 지속 가능
2. **"월등"은 STEEPs 필요, STEEPs는 정규화 레이어 필요** — Conservative는 STEEPs 연기, Balanced는 M1 포함 (최소 실행 가능 차별화)
3. **조건부 기능 = 솔로 개발자의 올바른 모델** — "예상되는 필요 ≠ 입증된 필요"
4. **업그레이드 경로 보존** — Conservative→Balanced 쉬움, 반대는 기술 부채 유발
5. **"자신을 위해 구축, 부산물로 공유"** — Month 4 오픈소스 (8+주 검증 후)
6. **Kill switch** — Month 2 후 유용한 리포트 없으면 중단 → 하방 ~30시간 제한

> 소스: `final-three-scenarios-prd.md`, `balanced-scenario-prd.md`

## 4.2 기술 스택 (GREEN/YELLOW/RED Zone)

### GREEN ZONE — Day 1 채택 (전 관점 합의)

| 계층 | 기술 | 근거 |
|------|------|------|
| **임베딩** | sentence-transformers + **BGE-M3** | **유일한 Aggressive bet** — 한 줄 교체, MTEB +12.5% (56→63), 8192 토큰, 2.2GB RAM |
| **한국어 NLP** | Kiwi (kiwipiepy >=0.18) | 8년+ 검증, ~200K 토큰/초, ~95% 정확도 |
| **토픽 모델링** | BERTopic + HDBSCAN | SOTA, Top2Vec 대비 34.2% 우수, GlobalNews 이미 사용 |
| **분류** | 규칙 기반 (keyword dict) | 3-4시간 구축, 70-80% 정확도면 충분 |
| **저장소** | SQLite + Parquet (PyArrow) | 양 소스 시스템 이미 사용, 추가 의존성 0 |
| **리포트 생성** | Jinja2 Markdown templates | 결정론적, 18년+ 안정, 0 ML 의존성 |
| **오케스트레이션** | Python subprocess + launchd/cron | 수십 년 검증, 5단계 선형 파이프라인에 DAG 불필요 |
| **스키마** | @dataclass(frozen=True) | Pydantic보다 가볍고 충분, 데이터 변이 버그 방지 |
| **테스트** | pytest (25개 표적 테스트만) | Schema 파싱 10개 + 섹터 매핑 15개 |
| **파이프라인 IPC** | 파일 기반 (JSON/Parquet) | Unix 철학 57년 검증 |
| **Enum** | StrEnum | 매직 스트링 버그 방지 |
| **Health check** | 소스 검증 ~50 LOC | 파이프라인 디버깅 시간 절약 |

### YELLOW ZONE — 트리거 기반 채택 (Month 3+)

| 기술 | 트리거 조건 |
|------|-----------|
| DuckDB (SQLite 대체) | SQLite 쿼리 >1초 |
| SetFit (규칙 기반 대체) | 규칙 기반 정확도 <70% |
| NetworkX (교차 분석) | 다중 홉 관계 쿼리 필요 시 |
| Ollama + Qwen3-32B (리포트 서술) | Jinja2 내러티브 품질 부족 시 |
| Snakemake (오케스트레이션) | 파이프라인 10단계+ 초과 시 |
| eKoNLPy (금융 사전) | 금융 용어 반복 오류 시 |
| pykrx (KRX 섹터) | M2: FDR 부족 시 |
| fredapi (매크로) | M2: 매크로 맥락 부족 시 |

### RED ZONE — 채택 불가 (전 관점 합의)

| 기술 | 거부 이유 |
|------|---------|
| Neo4j | <1,000 노드에 서버 DB 과잉 |
| InfluxDB / TimescaleDB | 200개/주 신호에 시계열 서버 과잉 |
| Airflow / Prefect | 5단계 선형 파이프라인에 엔터프라이즈 도구 |
| E5-Mistral-7B | 임베딩에만 14GB RAM |
| KR-FinBERT / KcELECTRA 감성 | 감성-수익 상관관계 **90-95% 허위** (교란 변수 통제 후 0.034-0.048) |
| Ollama 핵심 경로 | 비결정론, 30GB RAM, 환각 위험 → 서술 보충 용도만 |
| 멀티 에이전트 토론(MAD) | ICLR 2025에서 **실패 증명** |
| 전체 파인튜닝 | 1,000+ 레이블 필요 |

> 소스: `tech-stack-aggressive-vs-conservative.md`, `phase2-3-4-technology-deep-dive.md`, `theory-foundation-analysis.md`

## 4.3 아키텍처 결정

### 선택: Monolithic Sequential Pipeline + File-Based IPC

| 결정 | 근거 |
|------|------|
| 순차 실행 | 네트워크 I/O 병목, 병렬 크롤링은 anti-bot 유발 |
| 파일 기반 IPC | Upstream 시스템과 제로 결합, 일별 배치에 적합 |
| 규칙 기반 분류 | v1에 80% 정확도, ML 훈련 데이터 없음 |
| JSON 중간 데이터 | `jq` 조회 가능, 디버깅 용이 |
| 한국어 전용 리포트 | 개인 도구, 한국 시장용 |
| Python orchestrator | 4시간 파이프라인은 프로그래밍식 checkpoint 필요 |

### Evolutionary + Big Bang 하이브리드

- **Big Bang CLI**: Day 1부터 Click CLI + checkpoint/resume (3.5시간 재실행 방지)
- **Evolutionary 구현**: Step 클래스는 점진적 추가

### Spine+Rib 플러그인 아키텍처: 거부

- Round 1의 Long-Term Architect가 제안했으나, 다른 모든 관점이 "단일 사용자 CLI에 플러그인 추상화 = 과잉"으로 거부
- **예외**: 데이터 계약(frozen dataclass)은 채택 — 인터페이스 복잡도 없이 타입 안전성 확보

## 4.4 6가지 비타협 설계 원칙 (고전 이론 기반)

1. **멱등성** (ETL 30년+): 동일 입력 → 동일 출력. 항상. `synthesize_investment.py`는 순수 함수
2. **관심사 분리** (Dijkstra 1974): 수집/분석/표현 아키텍처적 분리. InvestScan은 소스 시스템을 **절대 수정하지 않음**
3. **증거 추적성**: 모든 방향성 판단에 소스→추론→결론 체인. `InvestmentDirection.signal_ids: list[str]`
4. **결정 저널** (Tetlock 2015): 체계적 예측 기록·채점 = 장기 가치 창출의 **주요 메커니즘**. Brier 점수 자동 계산
5. **파일 기반 파이프라인** (Unix 57년): 모든 스테이지 간 아티팩트 = 읽기 가능한 파일
6. **스키마 검증** (ETL Schema-on-Write): 정규화 경계에서 `@dataclass(frozen=True)` + `__post_init__` 검증. 검증 실패 → SchemaValidationError. **무음 통과 절대 금지**

> 소스: `classical-foundational-theory.md`, `06_long_term_scalability_architecture.md`

## 4.5 데이터 계약 (Frozen Dataclasses)

### UnifiedSignal (핵심 스키마)

```python
@dataclass(frozen=True, slots=True)
class UnifiedSignal:
    signal_id: str              # IS-{date}-{seq}
    source_system: str          # Literal["envscan", "gnews"]
    source_file: str
    title: str
    abstract: str
    steeps_category: SteepsCategory  # StrEnum
    sector_tags: tuple[str, ...]
    confidence: float               # 0.0-1.0 (정규화 후)
    psst_score: float               # 0.0-1.0 (정규화 후)
    burst_score: float              # 0.0-1.0
    novelty_score: float            # 0.0-1.0
    detected_at: datetime
    content_hash: str               # SHA-256[:16]
    source_format: str              # 6가지 중 하나
    raw_psst_scale: int             # 원본 스케일 보존 (감사용)
    schema_version: str             # "1.0.0"
```

### Enum 정의

```python
class SteepsCategory(StrEnum):
    S_Social = "S"
    T_Technological = "T"
    E_Economic = "E_Economic"
    E_Environmental = "E_Environmental"
    P_Political = "P"
    s_Security = "s"
    UNKNOWN = "UNKNOWN"

class SignalLayer(StrEnum):
    L1_FAD = "L1_fad"
    L2_SHORT = "L2_short"
    L3_MID = "L3_mid"
    L4_LONG = "L4_long"
    L5_SINGULARITY = "L5_singularity"

class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
```

### 데이터 흐름

```
EnvScan JSON (6 format) ─→ normalizers.py ─→ UnifiedSignal ─→ synthesize.py ─→ report.py ─→ weekly-report.md
GlobalNews Parquet      ─↗    ↑ schema.py      ↑ dedup.py       ↑ steeps_classifier
                              ↑ health_check    ↑ sector_mapper
```

> 소스: `coding-normalization-sector-mapping.md`, `technical-debt-strategy.md`

---

# Part V: 이론적 기반

## 5.1 마스터 프레이밍

> **InvestScan은 문서화된 시장 처리 지연(Fama/Lo)을 활용하여 교차 도메인 거시 신호(Meadows/STEEPs)를 방향성 투자 인텔리전스로 합성하는 한정 합리성 확장 장치(Simon 1956)이며, 경험적 보정(Tetlock/SDT)을 통해 검증된다.**

## 5.2 검증된 이론 (PROVEN)

| 이론 | 신뢰도 | InvestScan 활용 |
|------|--------|---------------|
| **BERTopic 금융 토픽** | 90%+ | FinTextSim 연구 — 도메인 임베딩과 함께할 때만 유효 |
| **KR-FinBERT** | 95%+ | SNU NLP Lab, 13.22GB 코퍼스, 정확도 **0.963** |
| **Apple Silicon LLM** | 98%+ | M5 Max 64GB: 32B 모델 15-22 tok/s, MLX prefix caching 5.8x |
| **STEEPs 투자 적용** | 85%+ | 소매 투자 앱에서 **완전히 부재** → 카테고리 창조 |
| **신호 수명 주기** | 85% | WISDOM 프레임워크: TEM 4분면 분류 |

## 5.3 이론적 위치

| 이론 | InvestScan 위치 |
|------|---------------|
| **EMH** (Fama 1970) | "시장이 틀리다"가 아닌 **"시장이 느리다"** — 처리 지연(주-월), 주의력 희소성, 지리적 분산 |
| **MPT** (Markowitz 1952) | InvestScan = "pre-MPT 입력 생성기" — 방향성 출력이 정밀 가중치보다 추정 오류에 견고 |
| **반사성** (Soros 1987) | 뉴스 신호는 시장을 반영하는 것이 아니라 **시장을 창조** — 수렴 다중 도메인 = 초선형 가중 |
| **Simon 한정 합리성** (1956) | InvestScan = **인지 보조 장치** — 개인 10-20소스 vs InvestScan 133+소스, 7±2 작업 기억 한계 |
| **Tetlock 슈퍼포캐스팅** (2015) | 결정 저널 = nice-to-have가 아닌 **가치 생성의 주요 메커니즘** |
| **SDT 신호 탐지** (1966) | Month 7+: ROC 분석 가능 (11 GICS × 52주 = 572 데이터 포인트) |
| **Shannon 정보** (1948) | 중복 제거의 이론적 근거 — 소스별 SNR 차등 |

## 5.4 이론적 경고 (절대 무시 불가)

| 경고 | 데이터 |
|------|--------|
| **감성-수익 상관관계 허위** | 원시 0.45-0.73 → 교란 변수 통제 후 **0.034-0.048** (90-95% 허위) |
| **Granger 인과성 허위 양성** | Raw 30-40%, 다중 검정 보정 후 10-15%, PCMCI 5-8% |
| **MAD 실패** | ICLR 2025: 14가지 실패 모드, 약한 에이전트가 정답 오염 |
| **InvestScan 실패 시점** | Soros 이론: **붐-버스트 변곡점**에서 최악의 방향성 콜 |
| **방향성 정확도 한계** | SDT 기준 AUC 0.6-0.7이 현실적, AUC >0.7은 낙관적 |
| **행동금융학 반박** | Barber & Odean(2000): 더 많은 정보 소비 → 수익 하락. SPIVA: 15년간 88% 액티브 펀드 언더퍼폼 |

> **핵심 결론: STEEPs-first, NOT sentiment-first. 감성은 선택적 보완이지 주요 신호가 아니다.**

> 소스: `theory-foundation-analysis.md`, `classical-foundational-theory.md`

---

# Part VI: 구현 계획

## 6.1 최종 구현 계획: Balanced 확장판 (~5,330 LOC)

> **R6 갱신**: Round 6 성찰 결과 종목 추천 Bridge 모듈(~1,800 LOC) + 검증 파이프라인(~400 LOC) 추가. 기존 핵심 파이프라인 ~2,710 LOC는 그대로 유지.

### 완전 모듈 목록

```
investscan/
  # ── 핵심 파이프라인 (기존 R4, ~2,710 LOC) ──
  __init__.py:           10 LOC
  schema.py:            110 LOC    ← frozen dataclass + StrEnum
  normalizers.py:       350 LOC    ← THE critical module (6-format parser)
  dedup.py:              80 LOC    ← content-hash + TF-IDF cosine 0.85
  steeps_classifier.py: 120 LOC    ← 규칙 기반 키워드 매칭
  sector_mapper.py:     160 LOC    ← STEEPs → GICS 11 섹터
  synthesize.py:        250 LOC    ← 확신도 가중 방향 계산
  generate_report.py:   180 LOC    ← Jinja2 한국어 Markdown
  journal.py:           150 LOC    ← JSONL decision journal
  health_check.py:      100 LOC    ← 소스 시스템 검증
  orchestrator.py:      280 LOC    ← Big Bang CLI + checkpoint/resume
  cli.py:               160 LOC    ← Click CLI
  config.py:             60 LOC
  utils.py:              80 LOC
  templates/
    weekly-report.md.j2: 110 LOC

  # ── 종목 추천 Bridge (R6 신규, ~1,800 LOC) ──
  universe_builder.py:  200 LOC    ← WICS JSON API + pykrx 유니버스 구성
  stock_sector_mapper.py: 150 LOC  ← WICS G10~G55 → 종목 매핑
  factor_engine.py:     350 LOC    ← Value(35%) + Momentum 12-1(40%) + Quality ROE(25%)
  signal_sector_bridge.py: 250 LOC ← STEEPs 신호 → 섹터 방향 조정 룰 엔진
  stock_screener.py:    300 LOC    ← 멀티팩터 스크리닝, 순위 산정
  evidence_chain.py:    200 LOC    ← 매크로→섹터→종목 증거 체인 JSON 직렬화
  recommendation_fmt.py: 200 LOC   ← 워치리스트/배분 출력 포맷
  data_cache.py:        150 LOC    ← SQLite 기반 데이터 캐싱

  # ── 검증 파이프라인 (R6 신규, ~400 LOC) ──
  validation/
    predictions_db.py:  120 LOC    ← 예측 기록 SQLite 관리
    accuracy_eval.py:   180 LOC    ← Brier Score + 이항검정 + 캘리브레이션
    quality_gate.py:    100 LOC    ← 월간 품질 게이트 + Kill Switch

config/
  investscan.yaml:       30 LOC
tests/
  conftest.py:           60 LOC
  test_normalizers.py:  160 LOC    ← 10개 계약 테스트
  test_sector_mapper.py: 120 LOC   ← 15개 매핑 테스트
run.sh:                 140 LOC    ← Phase A 임시 실행 스크립트
────────────────────────────────────
핵심 파이프라인:  ~2,710 LOC
종목 추천 Bridge: ~1,800 LOC (R6)
검증 파이프라인:  ~  400 LOC (R6)
외부 연동:        ~  420 LOC
────────────────────────────────────
TOTAL: ~5,330 LOC
```

### THE ONE THING

> **`normalizers.py` — 6-format 파싱 모듈을 먼저 만들고, 실제 데이터로 테스트하고, 모든 필드 매핑을 수동 검증하라.** 이것이 틀리면 모든 하류 모듈이 잘못된 투자 방향을 생산한다.

## 6.2 단계별 일정

### PHASE A: 데이터 기반 구축 (Week 1-3, ~22hr)

| 주차 | 작업 | 시간 |
|-----|------|------|
| W1 | 프로젝트 스캐폴딩: 패키지 구조, config.py, schema.py, CLI | 4h |
| W2 | normalizers.py: EnvScan JSON → UnifiedSignal (WF4 database.json 먼저) | 5h |
| W3 | normalizers.py: GlobalNews Parquet + 기본 dedup | 5h |
| 추가 | steeps_classifier.py + sector_mapper.py | 8h |

### PHASE B: 첫 리포트 (Week 4-6, ~13hr)

| 주차 | 작업 | 시간 |
|-----|------|------|
| W4 | orchestrator.py: 순차 실행 + checkpointing | 4h |
| W5 | synthesize.py: 규칙 기반 섹터 매핑 + 방향 점수 | 6h |
| W6 | generate_report.py + Jinja2 템플릿 → **첫 유용한 리포트** | 3h |

### PHASE C: CLI 및 인프라 (Week 7-10, ~18hr)

| 주차 | 작업 | 시간 |
|-----|------|------|
| W7-8 | Click CLI 마이그레이션 (checkpoint/resume) | 8h |
| W9-10 | health_check + journal + run.sh 폐기 | 10h |

### PHASE D: 테스트 (Week 9-12, ~8hr)

- conftest.py + test_normalizers.py (10개 계약 테스트)
- test_sector_mapper.py (15개 매핑 테스트)

### PHASE E: 운영 강화 (Week 13-24, ~8-15hr)

- 주간 실행 + 리포트 개선 + 임계값 조정
- 조건부 기능 (트리거 충족 시)

## 6.3 조건부 기능 (트리거 기반)

| 기능 | 트리거 | 추가 LOC | 추가 시간 |
|------|--------|---------|---------|
| Signal Evolution Tracker | 4주+ 동일 신호 수동 추적 | +350 | 10hr |
| Decision Journal (확장) | 2개월 내 3건+ 투자 결정 | +150 | 5hr |
| Scheduled Execution | 4주간 3회/주+ 수동 실행 | +200 | 5hr |
| HTML Interactive Report | 외부 공유 필요 | +400 | 12hr |
| KRX Market Data | 6개월+ 저널 축적 | +300 | 8hr |

## 6.4 테스트 전략

### 반드시 테스트 (비타협) — 25개

**10개 계약 테스트 (스키마 파싱)**:
- EnvScan: 완전 신호, 최소 신호, 필수 필드 누락 시 크래시, "T_Technological" → SteepsCategory.T
- GlobalNews: 완전 신호, null→기본값, 잘못된 layer→크래시
- pSST: 기본 변환, 범위 초과 크래시, `None→0.5`

**15개 섹터 매핑 테스트**:
- 6개 파라미터화 (S→소비재, T→IT, E_eco→금융, P→방산, E_env→에너지, s→방산+IT)
- UNKNOWN → 모든 섹터 (>=11개)
- IT/금융/크로스도메인 시그널
- STEEPs 분류 3개 ("NVIDIA 실적" → T, "CPI 물가" → E, "삼성 반도체" → T)
- 빈 summary / 한국어 텍스트 edge case

### crash-loud vs graceful

| 유형 | 동작 |
|------|------|
| **crash-loud** | 스키마 검증 실패, 점수 범위 초과, 인프라 문제 |
| **graceful** | 한 소스 미사용 → 부분 리포트, 20% 미만 파싱 실패 → 건너뜀 후 계속 |
| **20% 임계값** | 전체 신호의 20% 이상 정규화 실패 시 파이프라인 중단 |

## 6.5 Round 3→4 핵심 수정 사항

| 항목 | Round 3 추정 | Round 4 실제 |
|------|------------|------------|
| 소스 데이터 포맷 | 2가지 | **6가지** |
| 오케스트레이션 | Evolutionary | **Big Bang CLI** (checkpoint 필수) |
| 저널 저장소 | SQLite | **JSONL** (500개 미만) |
| 총 LOC | ~2,470 | **~2,710** |
| 가장 중요한 코드 | Schema normalization | **normalizers.py (6-format parser)** |

## 6.6 7가지 핵심 코드 패턴

1. `frozen dataclass(slots=True)` — 모든 데이터 객체 (PipelineState만 mutable)
2. `StrEnum` — 모든 카테고리 값
3. 명시적 scale 파라미터 — auto-detection **절대 금지**
4. 방어적 `.get()` + 문서화된 기본값 (0.5, NOT 0.0)
5. Crash-loud on contract violations / graceful on operational issues
6. JSON checkpoint for pipeline state
7. Direction with explicit uncertainty (source_count + uncertainty_reason)

## 6.7 6가지 안티패턴 (절대 금지)

1. Dict 기반 신호 전달 — frozen dataclass 사용
2. 가중치 없는 신뢰도 점수 평균 — 가중 중앙값 사용
3. 핵심 파이프라인의 ML 의존성 (transformers 등)
4. Month 1의 리포트 형식 조기 최적화 (Plotly/PDF/HTML)
5. 주간 리포트 작동 전 신호 진화 추적 구현
6. 업스트림 시스템 (EnvScan/GlobalNews) 수정

> 소스: `phase2-3-4-implementation-guide.md`, `coding-normalization-sector-mapping.md`, `orchestration-implementation-analysis.md`, `branch-3-output-implementation.md`, `testing-error-handling-implementation.md`, `branch-5-workflow-integration-analysis.md`

---

# Part VII: 외부 연동 계획

## 7.1 권장 시나리오: 3.B 균형 통합 (~420 LOC)

| 지표 | 값 |
|------|---|
| 외부 통합 LOC | ~420 |
| 핵심 파이프라인 LOC 잔여 | ~2,290 (85%) |
| 설정 시간 | ~2.5시간 |
| 월간 유지보수 | ~15분 |
| 실패 모드 | 6개 |
| 인증 자격증명 | 3개 (Gmail App Password, Telegram Bot Token + Chat ID) |

## 7.2 M1 포함 통합 (Green Zone)

| 연동 | 라이브러리 | 인증 | LOC | 장애 시 |
|------|----------|------|-----|--------|
| KOSPI/글로벌 지수/FX/원자재 | **FinanceDataReader** | 없음 | ~90 | 캐시 사용, "stale" 표시 |
| AI 모델 | Claude Code (네이티브) | 구독 | 0 | 전체 중단 |
| Telegram 알림 | requests | Bot token | ~85 | 알림 실패, 리포트 정상 |
| Gmail 아카이브 | smtplib | App Password | ~55 | 아카이브 없음, 기능 정상 |
| 자동 스케줄링 | launchd | 없음 | ~40(plist) | 수동 실행 대체 |
| 로그 관리 | RotatingFileHandler | 없음 | ~30 | 로그 없이 작동 |
| 결정 저널 DB | SQLite (WAL) | 없음 | ~40 | 새 DB 생성 |
| 백업 | 실행 전 파일 복사 | 없음 | ~20 | 백업 없이 진행 |
| JSONL 아카이브 | 신호 내보내기 | 없음 | ~15 | 미래 분석 불가 |

## 7.3 멀티모델 AI 통합

**핵심 발견**: 3개 AI CLI 모두 **기존 구독**으로 인증, 추가 비용 $0, API 키 불필요

| CLI | 인증 방식 | 호출 방법 |
|-----|---------|---------|
| Claude Code | Claude Max 구독 | 네이티브 |
| Gemini CLI | Google OAuth (기존) | `subprocess.run()` |
| Codex CLI | ChatGPT 구독 (기존) | `subprocess.run()` |

**Gemini MCP 제약**: 구독 인증으로 작동하는 Gemini MCP 서버 없음. subprocess가 유일한 방법.

**전략**: M1 스캐폴딩(코드 있으나 비활성) → M3에 설정 토글로 활성화
```yaml
multi_model:
  enabled: false  # M3+에서 true 전환
```

## 7.4 Yellow Zone 연동 (M2-M4)

| 연동 | 트리거 | LOC |
|------|--------|-----|
| pykrx (KRX 22개 섹터) | M2: FDR 섹터 데이터 부족 시 | ~110 |
| fredapi (매크로) | M2: 매크로 맥락 부족 시 | ~110 |
| Gemini CLI (장문맥) | M3: >200K 토큰 문서 분석 시 | ~120 |
| Codex CLI (구조화) | M3: JSON 출력 + 웹 검색 시 | ~120 |
| Streamlit 대시보드 | M4: 시각적 탐색 시 | ~300 |
| WeasyPrint PDF | M4: 외부 공유 시 | ~110 |

## 7.5 명시적 제외

| 제외 | 이유 |
|------|------|
| **KakaoTalk** | 200자 제한 + 30일 토큰 만료 + 복잡 OAuth. **마이너스 ROI** |
| **pytrends** | Google 자동 차단. 비신뢰 |

## 7.6 Telegram > KakaoTalk 판정 근거

| 항목 | Telegram | KakaoTalk |
|------|---------|-----------|
| 메시지 제한 | **4,096자** | 200자 |
| 토큰 만료 | **영구** | 30일 |
| 설정 시간 | **5분** | 30분+ |
| 파일 첨부 | **가능** | 불가 |
| 유지보수 | **없음** | 30일마다 토큰 갱신 |

## 7.7 성능저하 원칙

> **파이프라인은 항상 보고서를 생성해야 한다** (성능 저하라도). 스탈 경고 보고서가 아예 없는 것보다 유용하다. 유일한 전체 중단: Claude Code 자체가 다운.

## 7.8 Medallion Architecture 매핑

| 계층 | 해당 단계 |
|------|---------|
| **Bronze** | EnvScan JSON + GlobalNews Parquet (원시 수집) |
| **Silver** | unified_signals.json (정규화 + 중복 제거) |
| **Gold** | 투자_synthesis.json + weekly-report.md (분석 + 리포트) |

> 소스: `external-data-source-integration.md`, `branch-2-multi-model-integration-analysis.md`, `branch-3.1-3.2-output-notification-integration.md`, `branch-4-external-toolchain-integration.md`, `branch-5-documentation-references.md`, `phase2-3-4-external-integration-guide.md`

---

# Part VIII: 리스크 레지스터

## 8.1 기술 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 신호 품질 = 노이즈 | 40-50% | 실존적 | "116소스 집계자"로 피벗 |
| 소스 시스템 스키마 변경 | 30% | 파이프라인 파손 | 방어적 파싱 + 6포맷 명시적 감지 |
| pSST 스케일 불일치 | 높음 | 재정적 | 자동 감지 금지, 명시적 scale 파라미터 |
| STEEPs 코드 불일치 | 높음 | 신호 소멸 | StrEnum + 양 형식 파서 처리 |
| 과잉 엔지니어링 | 25% | 중간 | 3,000 LOC 복잡성 예산 (소스 시스템의 ~40%) |

## 8.2 시장 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| PRISM-INSIGHT 환경 스캐닝 추가 | 20-30% | 차별화 소멸 | 먼저 출시 + 사상 리더십 |
| 브로커 앱 "충분히 좋은" AI 임베딩 | 높음 | 가치 급락 | 브로커 복제 불가 깊이/방법론 |
| 아무도 매크로 방향에 관심 없음 | 40-50% | 중간 | 니치 수용, 200명 열성 사용자도 성공 |
| 기술 유지 부담 사용자 이탈 | 매우 높음 | 높음 | Docker, graceful degradation |

## 8.3 개발 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 솔로 개발자 번아웃 | 35% | M2-M3 중단 | 주 3시간 지속가능 페이스 |
| 일정 초과 | 60-70% | 2-4주 지연 | 33% 버퍼 (64/96hr) |
| 유지 부담 → 포기 | 40% | 치명적 | Month 2 kill switch |

## 8.4 재정 안전 임계 경로 3가지

1. **pSST Score Normalization**: 3개 스케일 혼용 (0-100, 0-10, 0-1) → 자동 감지 **절대 금지**
2. **Cross-Source Dedup Threshold**: 0.85 권고값, 모든 dedup 결정 로그 필수
3. **Direction Conviction Scoring**: **가중 중앙값** 사용, naive 평균 금지

## 8.5 "우리가 틀릴 경우" 시나리오

| 시나리오 | 확률 | 대응 |
|---------|------|------|
| 환경 스캐닝이 노이즈만 생성 | 30-40% | "116소스 집계자"로 피벗 |
| PRISM-INSIGHT가 환경 스캐닝 추가 | 20-30% | 먼저 출시, 사상 리더십 |
| AlphaSquare가 정확도 공개 | 10-20% | 시장 개선 기여, 깊이 우위 유지 |
| 로컬 실행이 너무 큰 장벽 | 50-60% | Docker 우선, 비디오 튜토리얼 |

> 소스: `aggressive-scenario-prd.md`, `aggressive-competitive-strategy.md`, `cautious-market-analysis.md`

---

# Part IX: 교차 라운드 긴장 해소

## 9.1 해소된 긴장

### T1: "월등히 뛰어남" 주장

| 관점 | 주장 |
|------|------|
| 낙관론 | InvestScan이 AlphaSquare를 진정으로 압도 (14언어, 6도메인, $0) |
| 신중론 | 분석적 깊이 ≠ 제품 우월성, AlphaSquare 11차원 우위 |
| 지속가능 | "열망적이되 망상에 가까움" |

**해소**: "카테고리 창조자" 포지셔닝으로 **합의**. "월등 = 남들이 하는 것을 더 잘해서가 아니라, 아무도 하지 않는 것을 하기 때문"

### T2: STEEPs 우선순위

| 관점 | 주장 |
|------|------|
| Conservative PRD | Phase 2로 연기 |
| Balanced/Aggressive | M1 필수 |
| Final 3-Scenario | STEEPs 없으면 "월등" 불가 |

**해소**: Balanced 채택 → **M1에 규칙 기반 STEEPs 포함** (최소 실행 가능 차별화)

### T3: 오케스트레이션

| 관점 | 주장 |
|------|------|
| Round 3 Tech Architect | Evolutionary (shell 우선) |
| Round 4 Implementation | Big Bang CLI 권장 |

**해소**: **Big Bang CLI** 채택 — checkpoint/resume으로 3.5시간 재실행 방지. Step 클래스는 점진적 추가.

### T4: 저널 저장소

| 관점 | 주장 |
|------|------|
| Round 3 | SQLite 고려 |
| Round 4 | JSONL 확정 |

**해소**: **JSONL** (500개 미만 항목). 500개 초과 시 SQLite 마이그레이션.

### T5: STEEPs-first vs Sentiment-first

**해소**: **STEEPs-first 확정**. 감성-수익 상관관계 90-95% 허위 (메타 분석 증거). 감성은 선택적 보완.

## 9.2 부분 해소된 긴장

### T6: Decision Journal 우선순위

| 관점 | 주장 |
|------|------|
| Phase 2 Discussion | GREEN ZONE (4/4 합의) |
| Balanced PRD | **CONDITIONAL** (2개월 내 3건+ 결정 시) |
| Biz-Sustainable | 250 LOC가 48,800 LOC보다 투자 가치 높음 |

**부분 해소**: GREEN ZONE 합의이나 Balanced에서 조건부 분류. PRD에서 **P0-elevated** (M2 시작, 조건부 아닌 필수)로 명확화 권장.

### T7: PRISM-INSIGHT 전략

| 관점 | 주장 |
|------|------|
| 경쟁 지도 | 긍정적 소개 (512스타, +244.63%) |
| 신중론 | 환경 스캐닝 추가 시 InvestScan 차별점 소멸 **경고** |
| 공격 전략 | 경쟁 아닌 모듈 통합 가능 |

**부분 해소**: "먼저 출시" 합의. 그러나 **협력 vs 경쟁** 최종 방향 미결정.

### T8: Balanced PRD 시간 예산 불일치

- Phase 2 Discussion: 전체 **60-80시간**
- Balanced PRD: M1만 **84시간** (예산 초과)

**부분 해소**: Round 4 최종 가이드에서 **~64시간** (33% 버퍼 포함 96시간 내)으로 재추정. PRD에서 64시간 기준 채택.

## 9.3 미해소된 긴장

### T9: 소스 시스템 LOC 불일치

| 측정 | EnvScan | GlobalNews | 합계 |
|------|---------|-----------|------|
| Round 1 | ~23,400 | ~48,800 | ~72,200 |
| Final 3-Scenario | ~25,500 | ~25,400 | ~50,900 |
| Phase 2 Discussion | — | — | ~59,000 |

**원인 추정**: 48,800은 전체(스크립트 포함), 25,400은 코어만. PRD에서 "~50,000-59,000 LOC (코어+유틸리티)" 표기 권장.

### T10: 프라이버시가 실제 구매 동기인지

- 낙관론: 로컬 = 구조적 해자
- 신중론: "사용자들이 편의성 대신 프라이버시를 선택하는 경우는 드물다"
- **검증 미실시**: 사용자 인터뷰 필요

---

# Part X: 미해결 질문과 추가 조사 영역

## 10.1 즉시 결정 필요

1. **Decision Journal P0 여부**: GREEN ZONE 합의인데 Balanced에서 조건부 — PRD에서 명확화
2. **PRISM-INSIGHT 전략**: 협력(통합 제안) vs 경쟁(속도 승부) 최종 결정
3. **배포 방식**: CLI 전용 vs Docker 제공 여부
4. **BGE-M3 차원**: 1024 전체(권장) vs 768 축소
5. **보고서 깊이**: 경영 요약 500단어 + 전체 부록 3,000단어 (권장)
6. **신호 진화 윈도우**: 12주 롤링 (권장, 1분기 정렬)

## 10.2 검증이 필요한 핵심 가설

7. STEEPs 기반 섹터 방향이 **55% 이상 정확도** 달성 가능한가? (6개월 전향 데이터 필요)
8. 프라이버시(로컬 실행)가 실제 구매/채택 동기인가? (사용자 인터뷰 필요)
9. 환경 스캐닝이 노이즈인가 신호인가? (3-6개월 실행 후 판단)
10. GlobalNews Parquet 실제 컬럼명/스키마 확인 (signals.parquet 실제 검사 필요)
11. EnvScan WF4 priority-ranked pSST 스케일 0-10 최종 확인 (실제 파일 검사)

## 10.3 추가 심층조사 가능 영역

| 영역 | 현 상태 | 필요성 |
|------|---------|--------|
| **주간 리포트 UX 리서치** | 미조사 | 투자 리포트 모범 사례 참조 |
| **PRISM-INSIGHT 코드 수준 비교** | Phase 0 수준 | 실제 아키텍처 분석 |
| **규제 리스크** | 미조사 | 한국 투자자문업법 적용 여부 |
| **백테스팅 없는 검증** | 미조사 | 매크로 방향성 정확도 측정 방법론 |
| **사용자 인터뷰 시뮬레이션** | 3 Edge Case만 | 심화 페르소나 |
| **STEEPs 분류기 v1 정확도** | 70-80% 주장, 근거 없음 | 실측 필요 |
| **섹터 전파 행렬 타당성** | 규칙 기반 v1, 검증 없음 | 금융 전문가 리뷰 |
| **수익화 장기 전략** | "필요 없음"으로 처리 | 지속가능성 논리 |
| **규제 리스크** | 미검토 | 투자 방향 제시 = 자문업? |

---

# Part XI: PRD 작성 권고사항

## 11.1 PRD 핵심 포함 사항

### 절대 포함

1. **제품 정체성**: 카테고리 창조자, 망원경 비유, "아무도 하지 않는 것"
2. **소스 시스템 역량**: ~50,000+ LOC, 150+ 소스, 14+ 언어, 56 NLP 기법
3. **Balanced 시나리오**: ~2,710 LOC, ~64hr, 주 3시간, Week 6 첫 리포트
4. **기술 스택**: Conservative Core + BGE-M3 유일한 Aggressive bet
5. **6가지 비타협 원칙**: 멱등성, 관심사 분리, 증거 추적, 결정 저널, 파일 파이프라인, 스키마 검증
6. **Green Zone 6기능**: One-command, 주간 리포트, 다중 소스 통합, 결정 저널, STEEPs, 증거 체인
7. **외부 연동**: FDR + Telegram + Gmail + launchd (420 LOC)
8. **Kill switch**: Month 2 후 유용한 리포트 없으면 중단

### 절대 포함 금지

1. "AlphaSquare 대비 월등" 프레임
2. 구체적 수익률 약속
3. SaaS 관련 아키텍처
4. 메인스트림 사용자 타겟팅
5. 감성 기반 트레이딩 신호 (허위 상관관계)

## 11.2 PRD 구조 권장

> **R6 갱신**: 기존 구조에 종목 추천 Bridge, 비코더 사용자 여정, 규제 준수, 검증 프레임워크, workflow.md 변환 가이드 추가.
> PRD의 독자는 **2명**: (1) 사용자(비코더 목사님) — 비전·여정·성공 지표, (2) Claude Code(workflow.md 경유) — 스키마·모듈·검증 기준

```
1. Executive Summary (카테고리 창조자 + 종목 관찰 + Balanced 확장 시나리오)
2. Problem Statement (거시 분석의 빈 사분면 + 종목 추천까지 포함한 완전한 비전)
3. User Journey (비코더 관점: Day 0 → 설치 → 첫 리포트 → 주간 운영) [R6 신규]
4. User Personas (3 Edge Case + 1 Non-Target)
5. Product Requirements
   5.1 Green Zone Features (6개 기존 + 종목 워치리스트)
   5.2 Yellow Zone Features (조건부)
   5.3 Red Zone Features (영구 보류)
6. Data Schema & Contracts
   6.1 UnifiedSignal schema (기존)
   6.2 StockRecommendation schema [R6 신규]
   6.3 Prediction/Validation schema [R6 신규]
   6.4 6가지 비타협 원칙
7. Technical Architecture
   7.1 기술 스택 (Green/Yellow/Red) — 확장 의존성 포함
   7.2 모듈 목록 (~5,330 LOC) [R6 갱신]
   7.3 의존성 순서 그래프
8. Implementation Architecture (for Claude Code) [R6 신규]
   8.1 세션 간 상태 유지 전략
   8.2 Done Gate 정의 (모듈별)
   8.3 에러 복구 패턴
9. External Integration
   9.1 Green Zone (FDR, Telegram, Gmail, launchd)
   9.2 Yellow Zone (pykrx, fredapi, multi-model)
10. Validation Framework [R6 신규]
    10.1 Brier Score + 이항검정 + 캘리브레이션
    10.2 Kill Switch 체크리스트
    10.3 월별 품질 게이트
11. Legal & Compliance [R6 신규]
    11.1 투자자문업법 비해당 근거
    11.2 면책 조항
    11.3 금지 용어 / 안전 대안 표현
12. Success Metrics (정량 + 정성 이중 구조)
13. Risk Register (기존 + 규모 확대 리스크)
14. Open Questions (PRD 작성 전 반드시 결정할 사항만)
15. Workflow.md 변환 가이드 [R6 신규]
    15.1 PRD→workflow.md 변환 규칙
    15.2 Phase 분해 기준
    15.3 Claude Code 실행 지시 형식
```

## 11.3 성공 지표

> **R6 갱신**: 정량(Brier Score) + 정성(품질 게이트) 이중 검증 구조 도입. 상세는 Part XV 참조.

### 핵심 이중 지표

> **정량**: Month 6 기준 3방향 Hit Rate ≥ 55% (이항검정 p < 0.10)
> **정성**: 12주 연속 주간 사용 (실행 + 읽기 + 저널 작성)

### Month 2 Kill Switch 체크리스트 [R6 신규]

5개 중 **3개 이상 실패 시 즉시 중단**:
1. 이항검정 p-value < 0.10 (단측)인가?
2. Brier Score < 0.30인가?
3. 월간 정성 평균 ≥ 2.5인가?
4. 최소 1개 섹터에서 명확한 유용성을 경험했는가?
5. 지속 의향 점수 ≥ 3인가?

### 월별 품질 게이트 (정량 + 정성)

| 월 | 정량 게이트 | 정성 게이트 |
|----|-----------|-----------|
| M1 | unified_signals.json STEEPs 분포 합리적인가? | "시스템이 데이터를 정상 수집하는가?" |
| M2 | **Brier Score < 0.30**, Hit Rate > 45% | **"다음 주에도 실행하겠는가?" (Kill Switch)** |
| M3 | Brier Score < 0.25, Hit Rate > 50% | "어느 리포트가 투자 포지션 생각을 바꿨는가?" |
| M6 | **Brier Score ≤ 0.22, Hit Rate ≥ 55%** | **"InvestScan이 작동을 멈추면 그리울 것인가?"** |

### 6개월 KPI

| 카테고리 | M3 목표 | M6 목표 |
|---------|--------|--------|
| 소스 스캔 수/리포트 | 80+ | 100+ |
| 언어 커버리지 | 10+ | 14 |
| 섹터 방향 정확도 | 미측정 | 55%+ |
| 주간 리포트 연속 | 12건 | 24건 |
| 결정 저널 | 5건+ | 15건+ |
| GitHub 스타 | 50+ | 200+ |
| 활성 주간 사용자 | 10-20 | 50-100 |

## 11.4 가장 중요한 인용구

> **"가장 적은 코드가 가장 큰 투자 가치를 창출한다."**
> — 결정 저널(~250 LOC)이 NLP 파이프라인(48,800 LOC)보다 투자 성과에 더 큰 영향을 미칠 수 있다.

> **"정보 수집에 가장 많은 엔지니어링이 투자되었지만, 투자 가치 창출은 가장 얇은 의사결정 레이어에서 발생한다."**

> **"최고의 망원경을 만들어라, 더 나은 현미경이라 주장하지 마라."**
> **R6 추가**: "그리고 망원경이 가리키는 곳의 물고기까지 보여줘라 — 단, '추천'이라 부르지 말고 '관찰 목록'이라 부르라."

---

# Part XII: 종목 추천 Bridge 방법론 (R6)

> **소스**: Round 6 추가 심층조사 — 한국 시장 팩터 투자, WICS/GICS 매핑, pykrx/FDR 데이터 파이프라인

## 12.1 왜 종목 추천 Bridge가 필요한가

사용자는 명시적으로 **"투자방향 및 종목 추천 앱"**을 원했다. 기존 R1-R5의 "카테고리 창조자 = 망원경" 포지셔닝은 전략적으로 옳지만, **종목 레벨 액션 없이는 사용자의 핵심 의도가 미충족**된다.

**해결 방향**: 매크로 방향성(망원경) + 팩터 기반 종목 워치리스트(물고기) = **둘 다 제공**

> ⚠️ 규제 안전: "추천" 표현 절대 금지 → "데이터 기반 관찰 목록" (Part XIV 참조)

## 12.2 한국 주식 유니버스 정의

### 투자 가능 유니버스

| 유니버스 | 종목 수 | 특성 |
|---------|--------|------|
| KOSPI 200 | 200개 | 시가총액 상위, 유동성 최우수 |
| KOSDAQ 150 | 150개 | KOSDAQ 대형주, 기술 섹터 집중 |
| **권장: KOSPI 200 + KOSDAQ 150** | **350개** | **유동성·데이터 품질·처리 속도 균형** |

### 데이터 취득 (완전 로컬, API Key 불필요)

| 방법 | 라이브러리 | 주요 데이터 | API Key |
|------|----------|----------|---------|
| 종목 리스트/OHLCV | `pykrx` | 전체 티커, 일/주/월봉, 수정주가 | 불필요 |
| 펀더멘털(PER/PBR/DIV) | `pykrx` `get_market_fundamental()` | 밸류에이션 지표 일괄 | 불필요 |
| 재무제표(ROE 등) | `FinanceDataReader` `'NAVER/FINSTATE-Y/{ticker}'` | 연/분기 재무 | 불필요 |
| **WICS 섹터 분류** | WiseIndex JSON API | **GICS 동형 10개 대분류, 무료** | **불필요** |
| 외국인/기관 수급 | `pykrx` `get_market_trading_value_by_date()` | 투자자 유형별 거래대금 | 불필요 |
| DART 공시(심화) | `OpenDartReader` | IFRS 재무제표, 정기보고서 | 무료 발급 필요 |

## 12.3 섹터 분류: WICS 사용 (GICS 대체)

**핵심 결정**: GICS는 S&P/MSCI 독점 지재권 → 직접 API 없음. **WICS(FnGuide)는 GICS 동형 구조이며 무료 JSON API 제공**.

| GICS 섹터 | WICS 코드 | 주요 한국 종목 |
|-----------|----------|-------------|
| Energy | G10 | SK이노베이션, S-Oil, GS |
| Materials | G15 | POSCO홀딩스, LG화학 |
| Industrials | G20 | 현대차, 삼성물산 |
| Consumer Disc. | G25 | 현대차, 기아, 아모레퍼시픽 |
| Consumer Staples | G30 | KT&G, 오리온, 농심 |
| Healthcare | G35 | 삼성바이오로직스, 셀트리온 |
| Financials | G40 | KB금융, 신한지주, 하나금융 |
| **IT** | **G45** | **삼성전자, SK하이닉스, LG전자** |
| Comm. Services | G50 | SK텔레콤, NAVER, 카카오 |
| Utilities | G55 | 한국전력, 한국가스공사 |

## 12.4 팩터 전략 (한국 시장 학술적 근거)

### 팩터별 유효성

| 팩터 | 한국 시장 유효성 | 핵심 근거 |
|------|-------------|---------|
| **사이즈 (Size)** | ★★★★★ | 1983-2023 장기 데이터: 가장 큰 프리미엄 |
| **가치 (Value/PBR)** | ★★★★ | Fama-French 3팩터와 일치, KOSPI 구조적 저평가 |
| **수익성 (Profitability/ROE)** | ★★★★ | MGMT·PERF 팩터 "highly significant positive return" (2024 APJFS) |
| **모멘텀 (Momentum)** | ★★★ (조건부) | 한국 개별 종목은 **단기 역전 효과** → **12-1 전략**(최근 1개월 제외) 필수 |
| **저변동성 (Low Vol)** | ★★★★ | 리스크 대비 수익률 안정적 |

### 권장 멀티팩터 가중치

```
한국 KOSPI/KOSDAQ 최적 팩터 배분:
  Value (PBR/PER):     35%  ← KOSPI 저평가 구조적 특성
  Momentum (12-1):     40%  ← 섹터 방향 신호와 동기화
  Quality (ROE/수익성): 25%  ← 실적 확인 요소
```

## 12.5 신호 → 종목 파이프라인 (6계층)

```
LAYER 0: STEEPs 신호 입력 (509+ 신호, 14개 언어)
    │ sector_direction_score[11]
    ▼
LAYER 1: 섹터 방향 필터
    │ Bullish: score > 0.6 / Neutral: 0.4-0.6 / Bearish: < 0.4
    ▼
LAYER 2: 종목 풀 구성
    │ WICS API → 해당 섹터 구성종목 → 우선주/스팩 제거
    ▼
LAYER 3: 팩터 스코어 계산
    │ pykrx PBR/PER/수익률 → FDR ROE → 멀티팩터 Z-score
    ▼
LAYER 4: 종목 순위 & 필터링
    │ 섹터 내 상위 5개 선별, 시가총액 > 500억, 이상값 제거
    ▼
LAYER 5: 에비던스 체인 생성
    │ 매크로 신호 → 섹터 방향 → 팩터 점수 → 종목 추적성 기록
    ▼
LAYER 6: 출력 포맷 (워치리스트 / 섹터 배분 참고 / 위험 등급)
```

## 12.6 Conviction Level 정의

| Level | 조건 | 표현 (규제 안전) | 비중 참고 |
|-------|------|----------------|---------|
| **STRONG_WATCH** | 섹터 score > 0.75 AND 종목 Z > 1.0 | "강한 관찰 대상" | +5~10% overweight |
| **WATCH** | 섹터 score > 0.6 AND 종목 Z > 0.5 | "관찰 대상" | +2~5% overweight |
| **MONITOR** | 섹터 score 0.4~0.6 OR 종목 Z 0~0.5 | "모니터링 대상" | 기존 비중 유지 |
| **CAUTION** | 섹터 score < 0.4 AND 종목 Z < 0 | "주의 대상" | -2~5% underweight |
| **AVOID** | 섹터 score < 0.25 | "회피 대상" | 보유 시 점검 |

## 12.7 에비던스 체인 예시

```
[관찰 근거 체인]
① 매크로 신호 (Political, confidence=0.85)
   "미국 BIS, 반도체 장비 대중 수출 추가 제한 발표"
   출처: Reuters (2026-03-12), Financial Times (2026-03-13)

② 섹터 방향 판단
   IT 섹터 방향: NEUTRAL (score=0.42)
   → Bullish 신호 3개 vs Bearish 신호 4개
   → AI 수요 강세(+) vs 지정학 리스크(-) 상쇄

③ 종목 팩터 분석 (SK하이닉스 000660)
   섹터 내 순위: 2위 / 23개 종목
   - Value Z-score: +0.72 (PBR 1.8, 섹터 평균 대비 저평가)
   - Momentum Z-score: +0.55 (12-1 수익률 +23%)
   - Quality Z-score: +0.81 (ROE 14.2%, 섹터 최상위)
   - 복합 스코어: +0.68

④ Conviction: MONITOR
   이유: 섹터 방향 Neutral → 소규모 관찰 유지
```

## 12.8 성능 예상 (MacBook M5 Max 64GB)

| 작업 | 예상 처리 시간 |
|------|-------------|
| 유니버스 구성 (350종목) | ~3-5초 |
| 팩터 계산 전체 | ~10-15초 |
| 스크리닝 + 순위 | ~2-3초 |
| 에비던스 체인 생성 | ~1초 |
| **전체 종목 Bridge 1회** | **~20-25초** |
| SQLite 캐싱 후 재실행 | ~3-5초 |

## 12.9 데이터 갱신 제약사항

| 데이터 | 갱신 주기 | 주의 |
|--------|----------|------|
| 주가 OHLCV | 영업일 장 마감 후 (16:30+) | pykrx = KRX 스크래핑 → 구조 변경 시 임시 오류 |
| PER/PBR | 영업일 장 마감 후 | 동일 |
| WICS 섹터 구성 | 월 1회 (분기 리밸런싱) | 공식 API 아닌 웹 엔드포인트 → 모니터링 필요 |
| 재무제표 | 분기 실적 발표 후 | **3-6개월 지연 반영 필수** (look-ahead bias 방지) |

---

# Part XIII: 비코더 자동구현 사용자 경험 설계 (R6)

> **소스**: Round 6 추가 심층조사 — Claude Code 자율 구현 역량, 원커맨드 설치, 무코드 유지보수

## 13.1 핵심 전제: 사용자는 코드를 전혀 모른다

| 항목 | 사실 |
|------|------|
| Python 경험 | 없음 |
| CLI 경험 | 최소 (터미널 열기 수준) |
| 주 업무 | 목사 (비IT) |
| 가용 시간 | 주 2-4시간 |
| **구현 방식** | **Claude Code가 workflow.md를 읽고 전체 자동 구현** |

## 13.2 Claude Code 자율 구현 역량

### 할 수 있는 것

- 프로젝트 디렉토리 전체 읽기·쓰기·생성·구조 재편
- `pip install`, `python script.py`, `git commit` 등 터미널 커맨드 자율 실행
- 코드 작성 → 테스트 → 에러 진단 → 수정 → 재테스트 반복 루프
- `--permission-mode auto` 플래그로 **무인 실행 가능** (Claude Team+ 구독)
- 서브에이전트 병렬 작업 (프론트엔드/백엔드 동시)
- **실증: 30시간+ 자율 동작 사례** 문서화됨

### 한계

| 한계 | 대응 전략 |
|------|----------|
| 컨텍스트 윈도우 소진 → 초기 지시 망각 | CLAUDE.md + Auto Memory + Phase 분리 |
| 기본 모드에서 매번 사용자 승인 요구 | `--permission-mode auto` 또는 auto-accept |
| API 500 에러 시 자동 재시도 없음 | 사용자에게 Telegram 알림 + 재실행 안내 |
| 각 세션 독립 컨텍스트 | `claude-progress.txt` + git log + state.yaml |

## 13.3 비코더 사용자 여정

### Day 0: 최초 설치 (한 번만)

**사전 조건 3가지**:
1. Claude Pro+ 구독 ($20+/월)
2. MacBook에서 터미널 실행 가능
3. Anthropic 계정

**설치 (1개 명령어)**:
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
→ Node.js 불필요, Python 불필요, PATH 자동 설정, 자동 업데이트 포함

**나머지는 Claude Code가 자동 처리**: Python, uv(패키지 관리자), 모든 라이브러리 설치

### Step 1: workflow.md 전달

```bash
cd ~/invest-system
claude
```
터미널 입력:
```
@workflow.md 를 읽고 Phase 1부터 순서대로 전부 구현해줘.
```

### Step 2-3: Claude Code 자율 구현 + 에러 처리

Claude Code는 **Gather Context → Take Action → Verify Results** 루프를 수백 회 반복:
1. workflow.md Phase 1 요구사항 파싱
2. 필요 파일 목록 생성 + pip 설치
3. 코드 작성
4. 테스트 → 에러 시 자동 진단·수정·재검증
5. Phase 완료 표시 → Phase 2 이동

**에러 에스컬레이션**: 3회 자동 수정 실패 → Telegram으로 사용자에게 비기술적 언어로 알림

### Step 4: 완료 확인

workflow.md에 포함:
```markdown
## Completion Criteria
구현 완료 시:
1. `python test_all.py` 모든 테스트 통과
2. `implementation_report.md` 자동 생성
3. Mac 알림: "투자 시스템 구현 완료"
```

### Step 5: 주간 운영 (완전 자동)

**권장 옵션 A: Mac launchd** (Claude Code가 자동 설치)
- `~/Library/LaunchAgents/com.invest.weekly.plist` 자동 생성
- 매주 월요일 오전 7시 실행
- 결과는 Telegram으로 수신

**에러 알림 (비기술적)**:
```
"인터넷 연결을 확인해주세요. 데이터 수집에 실패했습니다."
"일부 종목 데이터를 가져오지 못했습니다. 나머지 분석은 완료되었습니다."
```

## 13.4 구독 플랜 권고

| 시나리오 | 권고 플랜 | 월비용 |
|---------|---------|------|
| 초기 구현 (1-2주) | Claude Max | $100 |
| 주간 운영 | Claude Pro | $20 |
| Auto 모드 필요 시 | Claude Team | $30/인 |

## 13.5 Self-Healing 패턴

| 실패 유형 | 자동 처리 |
|---------|---------|
| API 타임아웃 | 3회 재시도(지수 백오프) 후 이전 캐시 사용 |
| 모듈 누락 | `pip install` 자동 실행 |
| 데이터 형식 오류 | 오류 종목 건너뛰고 나머지 처리 |
| 디스크 공간 부족 | 30일+ 캐시 자동 삭제 후 재시도 |

---

# Part XIV: 한국 법적 규제 분석 (R6)

> **소스**: Round 6 추가 심층조사 — 자본시장법, 투자자문업법, AI 기본법, 금융위원회 비조치의견서

## 14.1 핵심 결론

**InvestScan의 현재 설계(로컬 개인 도구 + 섹터 방향성 + 종목 관찰 목록)는 한국 자본시장법상 투자자문업에 해당하지 않는다.**

투자자문업 3요건 (자본시장법 제6조 제7항):

| 요건 | 내용 | InvestScan 해당 여부 |
|------|------|---------------------|
| ① 투자판단 | 종목·수량·가격·시기 판단 | 섹터 방향 + 워치리스트 = **해당 가능성 낮음** |
| ② 영업성 | 이익 목적, 대가 수취 | 무료 개인 사용 = **해당 없음** |
| ③ 자문에 응함 | 특정인 대상 개별 응답 | 자동 생성 리포트 = **해당 없음** |

**결정적 포인트**: 3요건이 **동시 충족**되어야 투자자문업. 영업성(②)과 개별성(③)이 부재하므로 규제 대상 아님.

## 14.2 시나리오별 법적 위험

| 시나리오 | 위험도 | 근거 |
|---------|--------|------|
| 현재 설계 (로컬 개인 도구) | **매우 낮음** | 영업성·대가·개별성 모두 없음 |
| 종목 워치리스트 추가 | **낮음** | 개인 사용 + 무료 = 투자자문 미해당 |
| GitHub 오픈소스 공개 | **중간** | AI 기본법(2026.1.22 시행) 검토 필요. 투자 분석 AI는 "고영향 AI" 미해당 가능성 높음 |
| 유료화 | **높음** | 즉시 유사투자자문업 신고 또는 투자자문업 등록 필요 |

## 14.3 금지 표현 vs 안전 대안

| 금지 표현 | 이유 | 안전 대안 |
|---------|------|---------|
| "매수 추천" / "BUY" | 투자 권유 해석 | "관찰 목록에 추가됨" |
| "이 종목을 사야 합니다" | 명백한 투자 자문 | "뉴스 빈도 증가 감지됨" |
| "수익률 보장" | 금융소비자보호법 위반 | **사용 금지** |
| "매수 신호" / "Buy Signal" | 투자판단 제공 | "상향 모멘텀 지표 감지" |
| "추천 섹터" | 자문성 표현 | "모멘텀 우위 섹터" / "데이터 기반 섹터 스코어" |
| "포트폴리오 최적화" | 투자일임업 연상 | "섹터 배분 참고 데이터" |

> "Bullish/Bearish/Neutral" 자체는 시장 분석 용어로 법적 문제 없음. 단, "추천"과 결합하지 말 것.

## 14.4 필수 면책 조항

```
[법적 고지사항]
InvestScan은 개인 투자자의 정보 수집·정리를 자동화하는 로컬 소프트웨어 도구입니다.
1. 본 소프트웨어의 모든 산출물은 공개 데이터 자동 집계 결과이며,
   「자본시장과 금융투자업에 관한 법률」 제6조 제7항의 투자자문이 아닙니다.
2. 특정인 대상 개별 투자판단을 제공하지 않으며, 금융투자상품의
   취득·처분에 관한 구체적 권유를 목적으로 하지 않습니다.
3. 모든 투자 결정과 손익은 전적으로 사용자 본인의 책임입니다.
4. 본 소프트웨어는 금융위원회 등록 투자자문업자가 아닙니다.
```

## 14.5 2026년 규제 동향

- **AI 기본법 (2026.1.22 시행)**: 오픈소스 배포 시 규제 대상 가능성. 다만 투자 분석 AI는 "고영향 AI" 10개 영역에 **미포함** → 고영향 AI 아닐 가능성 높음. 계도 기간으로 과태료는 2027년 이후.
- **금융위 AI 가이드라인 (2025.12)**: "보조수단성" 원칙 — AI는 인간 의사결정 지원, 최종 책임은 인간. InvestScan 설계에 부합.

---

# Part XV: 검증 방법론 — 백테스팅 없는 정확도 측정 (R6)

> **소스**: Round 6 추가 심층조사 — Tetlock 슈퍼포캐스팅, Brier Score, SDT, 캘리브레이션

## 15.1 왜 전통적 백테스팅이 불가능한가

InvestScan은 **매크로 환경 스캐닝 → 섹터 방향성** 시스템이다. 전통적 백테스팅(과거 데이터로 전략 검증)이 불가능한 이유:
- 과거 509개 신호의 역사적 데이터가 없음 (forward-only)
- 매크로 신호는 비반복적 (전향 편향 불가)
- 이것은 결함이 아니라 **매크로 인텔리전스의 본질적 속성**

## 15.2 Brier Score — 핵심 정량 지표

### 3방향 Brier Score

$$BS_{multi} = \frac{1}{N} \sum_{t=1}^{N} \sum_{i=1}^{3} (f_{ti} - o_{ti})^2$$

| 요소 | 의미 |
|------|------|
| $f_{ti}$ | 예측 확률 (강세 0.65, 중립 0.25, 약세 0.10) |
| $o_{ti}$ | 실제 결과 (해당 방향 = 1, 나머지 = 0) |
| 범위 | 0 (완벽) ~ 2 (최악) |
| 랜덤 기준선 | 0.444 (3분류) |

### Brier Skill Score (BSS)

$$BSS = 1 - \frac{BS_{system}}{BS_{reference}}$$

- BSS > 0: 랜덤보다 우수
- **InvestScan 목표: BSS ≥ 0.10 (Month 6)**

### 목표값

| 단계 | 기간 | Brier Score 목표 | Hit Rate 등가 |
|-----|------|-----------------|-------------|
| Kill switch 직전 | Month 2 (22 예측) | BS ≤ 0.30 | ~45%+ |
| 유용성 확인 | Month 6 (66 예측) | BS ≤ 0.22 | ~55% |
| 고품질 | Month 12 (132 예측) | BS ≤ 0.18 | ~58% |

### 벤치마크 (Good Judgment Project)

| 예측자 유형 | Brier Score |
|-----------|------------|
| 훈련받지 않은 예측자 | 0.22~0.28 |
| 도메인 전문가 | 0.18~0.22 |
| 슈퍼포캐스터 | 0.14~0.18 |
| 랜덤 예측 | 0.25 (이진) |

## 15.3 "강세가 맞았다"의 정의

| 결과 분류 | 기준 | 근거 |
|----------|------|------|
| 강세 확인 | 4주 수익률 > +1.5% | 거래비용·노이즈 제거 |
| 약세 확인 | 4주 수익률 < -1.5% | 대칭 적용 |
| 중립 확인 | -1.5% ≤ 수익률 ≤ +1.5% | 노이즈 범위 |

> 섹터별 변동성에 따라 임계값 조정 가능: 에너지(±2.5%), 유틸리티(±0.8%)

### KRX 섹터 지수 코드 (FinanceDataReader 호환)

| GICS 섹터 | KRX 코드 | 지수명 |
|-----------|---------|--------|
| Energy | 5048 | KRX 에너지화학 |
| Healthcare | 5045 | KRX 헬스케어 |
| Financials | 5046 | KRX 은행 |
| **IT** | **5064** | **KRX 정보기술** |
| Comm. Services | 5051 | KRX 방송통신 |
| Utilities | 5065 | KRX 유틸리티 |

## 15.4 통계적 유의성 — 이항검정

### 표본 크기별 유의성 임계값 (단측, α=0.05)

| 예측 수 (n) | 유의적 히트 수 | 필요 히트율 |
|------------|-------------|------------|
| 22 (Month 2) | 15/22 이상 | 68.2% |
| 66 (Month 6) | 40/66 이상 | 60.6% |
| 132 (Month 12) | 76/132 이상 | 57.6% |

> Month 2에 55% 히트율은 통계적으로 유의하지 않을 수 있음. Kill switch 발동 기준은 **통계적 유의성보다 주관적 가치 결여**를 우선시해야 한다.

## 15.5 캘리브레이션 곡선

InvestScan이 "강세 70%"라고 했을 때, **실제로 70%의 빈도로 강세 발생**해야 완벽한 캘리브레이션.

- 점이 대각선 위: 과소신뢰 (보수적)
- 점이 대각선 아래: 과잉신뢰 (무모)
- **목표**: 대각선 ±10% 이내

## 15.6 월간 정성 품질 게이트 (6개 질문, 1-5점)

1. **정보 신선도**: "기존에 몰랐던 정보를 몇 개 발견했는가?"
2. **의사결정 영향**: "실제 투자/관망 결정을 변경하게 했는가?"
3. **프레임 변경**: "특정 섹터에 대한 시각이 바뀌었는가?"
4. **실행 유발**: "보고서를 읽은 직후 어떤 행동을 취했는가?"
5. **시간 가치**: "보고서 읽는 시간이 가치 있었는가?"
6. **지속 의향**: "다음 달도 계속 운영할 의향이 있는가?"

**Kill Switch**: 월간 평균 < 2.5 또는 Q6 = 1 → 즉시 중단 검토

## 15.7 자동 검증 파이프라인 설계

```
[주간 보고서 발행] → [predictions.db에 예측 저장]
        ↓ (4주 후 자동)
[FinanceDataReader로 섹터 수익률 조회]
        ↓
[방향성 분류 + Brier Score 계산]
        ↓
[월간 정확도 보고서 자동 생성]
  ├─ Brier Score 추이 차트
  ├─ Hit Rate + 이항검정 p-value
  ├─ 섹터별 성과 분석
  └─ 캘리브레이션 곡선
```

## 15.8 검증의 3대 원칙

1. **예측은 확률로 기록하라**: "IT 강세"가 아니라 "강세 65%, 중립 25%, 약세 10%"
2. **작은 표본에서 신중하게 해석하라**: Month 2의 22개 예측으로 "효과 없다"는 판단은 통계적으로 불충분
3. **정량 + 정성 이중 검증**: Brier Score 0.22여도 주관적 가치 없으면 무의미. 반대로 정성 4.0이어도 정확도 40%면 자기기만.

---

# Part XVI: workflow.md 자동구현 설계 패턴 (R6)

> **소스**: Round 6 추가 심층조사 — Anthropic C 컴파일러 사례, 장기 에이전트 하네스, spec-driven 개발

## 16.1 핵심 실증 사례

### Anthropic C 컴파일러 사례

- 16개 Claude Code 에이전트 → **~100,000 LOC Rust 컴파일러** 구현
- ~2,000 Claude Code 세션 소요
- 핵심 교훈: **"테스트 검증기가 거의 완벽해야 Claude의 자율 작업이 가능하다"**

### InvestScan 예상 규모

- ~5,330 LOC → **~50-60 Claude Code 세션** 예상 (14모듈 × 평균 2세션 + 통합테스트 10세션)
- 각 모듈당 1-3 세션

## 16.2 세션 간 상태 유지 — 3대 아티팩트

| 아티팩트 | 목적 | 갱신 시점 |
|---------|------|----------|
| `claude-progress.txt` | 현재 세션 진행상황, 결정사항, 다음 세션 우선순위 | 모든 모듈 완료 후 |
| git commits | 실제 코드 상태 (체크포인트) | 모든 모듈 완료 후 즉시 |
| `.claude/state.yaml` | 워크플로우 메타 상태 (Orchestrator만 쓰기) | Phase 전환 시 |

**매 세션 시작 프로토콜 (필수)**:
1. `claude-progress.txt` 읽기
2. `.claude/state.yaml` 현재 단계 확인
3. `git log --oneline -10` 최근 커밋 확인
4. 현재 단계 Done Gate 실행 (이미 완료됐는지 확인)
5. 미완료 확인 후 구현 시작

## 16.3 workflow.md 7대 설계 원칙

### 원칙 1: 단계의 크기 = 서브에이전트 컨텍스트 1회분

각 구현 단계는 **단일 서브에이전트가 하나의 격리된 컨텍스트에서 완료 가능**해야 한다.
InvestScan: 14개 모듈 → 14개 서브에이전트 태스크로 분해.

### 원칙 2: Spec-First, Code-Second

구현 전 3개 문서 선행:
1. `specs/investscan/requirements.md` — 인수 기준
2. `specs/investscan/design.md` — 인터페이스 계약
3. `specs/investscan/tasks.md` — 커밋 가능 단위 태스크

### 원칙 3: Foundation First (의존성 순서)

```
schema.py → normalizers.py → dedup.py → steeps_classifier.py
                                              ↓
                                        sector_mapper.py
                                              ↓
                                        synthesize.py → generate_report.py
                                              ↓
                                   (종목 Bridge 모듈 추가)
                                   universe_builder.py → factor_engine.py
                                              ↓
                                        stock_screener.py → evidence_chain.py
```

### 원칙 4: 측정 가능한 Done Gate

모호한 기준 금지. 각 단계마다 **실행 가능한 단일 명령**으로 완료 확인:

| 모듈 | Done Gate |
|------|-----------|
| schema.py | `python -c "from investscan.schema import UnifiedSignal; print('OK')"` |
| normalizers.py | `python -c "from investscan.normalizers import parse_all; s=parse_all('...'); assert len(s)>100"` |
| generate_report.py | 보고서 파일 존재 + 내용 비어있지 않음 + 3개+ 섹터 방향 포함 |

### 원칙 5: 수직 슬라이스 (Vertical Slice) 전략

레이어별이 아닌 **"첫 유용한 보고서"에 집중**:
- Phase A (W1-3): schema + normalizers + run.sh
- Phase B (W4-6): synthesize + report → **첫 보고서 산출**
- Phase C (W7-10): CLI + 종목 Bridge
- Phase D (W11-14): 검증 파이프라인 + 테스트
- Phase E (W15+): 운영 강화

### 원칙 6: 즉시 커밋 (체크포인트)

각 모듈 완료 후 즉시 `git commit`. 컨텍스트 소진 시에도 코드 보존.

### 원칙 7: 에러 복구는 결정론적으로

```yaml
error_handling:
  on_module_failure: "에러 분석 → 수정 → 3회 실패 시 다른 접근법 → 10회 실패 시 사용자 에스컬레이션"
  on_context_overflow: "claude-progress.txt 즉시 갱신 → 새 세션에서 progress 읽고 재개"
  on_dependency_failure: "pip install --user 시도 → 실패 시 사용자에게 수동 설치 요청"
```

## 16.4 구현 단계 표준 형식

```markdown
### N. (implementation) [모듈명] 구현
- **Context**: [이전 단계 산출물 경로 — 없으면 에이전트가 상태 파악 불가]
- **Agent**: `@implementer` (sonnet)
- **Files to Create**: `investscan/[파일명].py` (~[LOC] LOC)
- **Implementation Spec**: `specs/investscan/design.md#[섹션]`
- **Verification**:
  - [ ] 파일 존재 + LOC > [N]
  - [ ] [실행 가능한 기능적 검증]
  - [ ] [파이프라인 연결: 다음 단계 입력으로 사용 가능]
- **Done Gate**: [단일 실행 명령]
- **Post-action**: git commit + claude-progress.txt 갱신
```

## 16.5 금융 안전 검증 (InvestScan 특화)

pSST 점수 정규화 오류 = 잘못된 투자 방향 → 반드시 계약 테스트:

```python
# 필수 계약 테스트 (workflow.md에 명시)
def test_psst_scale_explicit():
    """자동 감지 아닌 명시적 스케일 파라미터 확인"""
    signal = parse_wf4_database(sample)
    assert 0.0 <= signal.confidence_score <= 1.0

def test_direction_weighted_median():
    """단순 평균 아닌 가중 중위값 사용 확인"""
    direction = score_direction(20 * low_conf + [high_conf])
    assert direction.method == "weighted_median"
```

## 16.6 컨텍스트 소진 대비 Handoff Capsule

컨텍스트 90%+ 소비 시 자동 생성:

```markdown
# Handoff Capsule — [timestamp]
## 완료 모듈: [x] schema, [x] normalizers, [x] dedup
## 현재 작업: steeps_classifier — 70% 완료
## 알려진 이슈: WF1 parser summary 필드 없을 때 빈 string (TODO: 0.5 기본값)
## 다음 세션: steeps_classifier 완료 → sector_mapper 시작
```

## 16.7 AgenticWorkflow 기존 인프라 활용

| 기존 인프라 | workflow.md에서의 활용 |
|-----------|---------------------|
| Context Preservation System | 세션 간 자동 스냅샷·복원 |
| `block_destructive_commands.py` | `rm -rf`, `git reset --hard` 차단 |
| `validate_verification.py` | 각 구현 단계 Verification Gate 검증 |
| `@reviewer` 에이전트 | Phase D에서 구현된 코드 적대적 리뷰 |

---

## 부록 A: 전체 파일 참조 목록

### Round 1: 소스 시스템 분석
- `round1-synthesis.md` — Round 1 통합 요약

### Round 2: 경쟁우위 심층조사 (Phase 0-3)
- `alphasquare-competitive-analysis.md` — AlphaSquare 기능·가격·사용자·한계
- `competitive-landscape-map.md` — 한국+글로벌 4 Tier 경쟁 지도
- `overwhelmingly-superior-investment-app.md` — "월등한 우위" 7차원 정의
- `optimistic-market-analysis.md` — Market-Optimistic Branch
- `cautious-superiority-challenge.md` — Market-Cautious Branch
- `user-edge-case-analysis.md` — User-EdgeCase Branch (3 페르소나)
- `user-mainstream-analysis.md` — User-Mainstream Branch
- `investscan-superiority-architecture.md` — Tech-Fast Branch
- `long-term-superiority-architecture.md` — Tech-Scalable Branch
- `aggressive-competitive-strategy.md` — Biz-Aggressive Branch
- `biz-sustainable-analysis.md` — Biz-Sustainable Branch
- `phase2-consolidated-discussion.md` — Phase 2 통합 토론
- `aggressive-scenario-prd.md` — Aggressive 시나리오
- `balanced-scenario-prd.md` — Balanced 시나리오
- `prd-conservative-scenario.md` — Conservative 시나리오
- `final-three-scenarios-prd.md` — 3시나리오 비교 + 최종 권장
- `06_long_term_scalability_architecture.md` — Spine+Rib 아키텍처
- `cautious-market-analysis.md` — PRISM-INSIGHT 분석 포함

### Round 3: 기술·이론 심층 조사
- `tech-stack-aggressive-vs-conservative.md` — 기술 스택 Aggressive vs Conservative
- `tech-architecture-analysis.md` — Evolutionary vs Big Bang
- `tech-dev-workflow-analysis.md` — Rapid vs Robust 개발 워크플로우
- `tech-debt-strategy-analysis.md` — 기술 부채 전략
- `technical-debt-strategy.md` — 기술 부채 상세 (UnifiedSignal 스키마)
- `theory-foundation-analysis.md` — 현대/첨단 이론
- `classical-foundational-theory.md` — 고전/기초 이론
- `phase2-3-4-technology-deep-dive.md` — Round 3 통합 가이드

### Round 4: 코딩·구현 심층 조사
- `coding-normalization-sector-mapping.md` — 정규화+섹터 매핑 코딩
- `orchestration-implementation-analysis.md` — 오케스트레이션 구현
- `branch-3-output-implementation.md` — 출력/리포트 구현
- `testing-error-handling-implementation.md` — 테스트/에러 처리
- `branch-5-workflow-integration-analysis.md` — workflow.md 통합
- `phase2-3-4-implementation-guide.md` — Round 4 통합 가이드

### Round 5: 외부 연동 심층 조사
- `external-data-source-integration.md` — 금융 데이터소스
- `branch-2-multi-model-integration-analysis.md` — AI 모델 CLI
- `branch-3.1-3.2-output-notification-integration.md` — 출력/알림
- `branch-4-external-toolchain-integration.md` — 도구체인
- `branch-5-documentation-references.md` — 문서/참조
- `phase2-3-4-external-integration-guide.md` — Round 5 통합 가이드

### Round 6: 성찰 심층조사 (Part XII-XVI)
- **종목 추천 Bridge** — 한국 팩터 투자 학술 근거, WICS/GICS 매핑, pykrx/FDR 데이터 파이프라인
- **비코더 자동구현 UX** — Claude Code 자율 구현 역량, 원커맨드 설치, Self-Healing 패턴
- **한국 규제 분석** — 자본시장법 제6조/제7조, 금융위 비조치의견서, AI 기본법 2026
- **검증 방법론** — Tetlock 슈퍼포캐스팅, Brier Score, SDT/AUC, 캘리브레이션
- **workflow.md 자동구현** — Anthropic C 컴파일러 사례, spec-driven 개발, 세션 간 상태 유지

> R6 소스: 웹 리서치 5건 병렬 수행 (2026-03-28). 상세 출처는 각 Part 내 참조.

### 인덱스
- `INDEX.md` — 전체 리서치 인덱스

---

## 부록 B: Cross-Domain 전파 행렬 (규칙 기반 v1)

```
              IT   Health  Financials  Materials  Energy  Consumer  Utilities  Telecom
Political    0.7   0.3     0.6         0.4        0.8     0.3       0.5        0.3
Technologic  0.9   0.6     0.4         0.3        0.4     0.5       0.3        0.7
Economic     0.6   0.3     0.9         0.7        0.6     0.8       0.4        0.3
Environment  0.3   0.2     0.3         0.6        0.9     0.4       0.8        0.2
Social       0.4   0.7     0.3         0.2        0.2     0.9       0.3        0.3
Geopolitical 0.5   0.2     0.7         0.5        0.8     0.4       0.3        0.4
```

> ⚠️ 검증 미실시 — 금융 전문가 리뷰 필요

---

## 부록 C: 의존성 목록

### 활성 (M1) — R6 갱신

```
# requirements.txt

# 핵심 파이프라인 (기존 R4)
sentence-transformers>=3.0.0    # BGE-M3
pyarrow>=17.0.0                 # Parquet R/W
Jinja2>=3.1.4                   # 리포트 템플릿
PyYAML>=6.0.2                   # 설정
kiwipiepy>=0.18.0               # 한국어 NLP
click>=8.0                      # CLI
finance-datareader>=0.9.85      # 시장 데이터 + 섹터 지수
requests>=2.31                  # Telegram API + WICS JSON API
python-dotenv>=1.0              # .env 로딩
rich>=13.0                      # CLI 진행 표시

# 종목 추천 Bridge (R6 신규)
pykrx>=1.0.40                   # KRX 주가/펀더멘털/수급 (API Key 불필요)
numpy>=1.24.0                   # Z-score, 팩터 계산
scipy>=1.11.0                   # zscore, 이항검정, 통계 함수

# 소스 시스템에서 상속
bertopic>=0.16.4
hdbscan>=0.8.38
umap-learn>=0.5.7
scikit-learn>=1.5.0             # 캘리브레이션 곡선, 표준화
pandas>=2.2.0

# 개발
pytest>=8.3.0
```

### 스캐폴딩 (비활성, M2+)

```
# fredapi>=0.5        # M2: FRED 매크로
# opendartreader>=0.7.9  # M2: DART 공시 (무료 API Key 필요)
# duckdb>=1.2.0       # M3: 분석 쿼리
# setfit>=1.0.0       # M3: ML 분류
# networkx>=3.4       # M3: 그래프 분석
# matplotlib>=3.7.0   # M3: 캘리브레이션 차트
# streamlit>=1.35     # M4: 대시보드
# plotly>=5.18        # M4: 차트
# weasyprint>=62      # M4: PDF
```

---

## 부록 D: 커뮤니티 전략 (공개 시점: Month 4)

### 채널 (우선순위)

| 채널 | 유형 | 이유 |
|------|------|------|
| GeekNews (긱뉴스) | 주요 | PRISM-INSIGHT 피처 실적 |
| Clien 주식 게시판 | 주요 | 한국 투자 커뮤니티 |
| Korean Python/ML Slack | 보조 | 기술 커뮤니티 |
| Reddit r/korea | 보조 | 영어권 한국 투자자 |
| 한국 알고매매 Telegram | 보조 | 퀀트 커뮤니티 |

### 파트너십

- **미디어**: GeekNews, Startup Alliance, Platum
- **교육**: 한국금융투자협회, Fastcampus
- **오픈소스**: PRISM-INSIGHT, FinGPT, OpenBB
- **학술**: KAIST 핀테크 랩, SNU 계량금융
- **퀀트**: Newsystock/Genport, 퀀트 Telegram

---

*이 문서는 `/prompt/prd-research/` 폴더의 39개 파일 (27,195줄)을 5개 라운드에 걸쳐 전수 분석하여 생성된 최종 통합 문서입니다. PRD.md 작성 시 이 문서만 참조하면 됩니다.*

---

# Part XVII: 모놀리식 아키텍처 — 업스트림 통합 설계 (R7)

> **소스**: `analysis-monolithic-architecture.md` (2026-03-27) — InvestScan Fast-Ship Architect 분석
> **역할**: PRD Section 7(Technical Architecture) + Section 8(Implementation Architecture) 핵심 참조

## 17.1 실제 파일 경로 (config.py 기준)

```python
ENVSCAN_ROOT = Path("../EnvironmentScan-system-main-v4-main")
GNEWS_ROOT = Path("../GlobalNews-Crawling-AgenticWorkflow")

ENVSCAN_SIGNALS = ENVSCAN_ROOT / "env-scanning/signals/database.json"
ENVSCAN_DAILY_OUTPUT = ENVSCAN_ROOT / "output/"
ENVSCAN_INTEGRATED = ENVSCAN_ROOT / "env-scanning/integrated/"

GNEWS_SIGNALS = GNEWS_ROOT / "data/output/signals.parquet"
GNEWS_ANALYSIS = GNEWS_ROOT / "data/output/analysis.parquet"
GNEWS_TOPICS = GNEWS_ROOT / "data/output/topics.parquet"
```

**원칙**: 양 소스 시스템 변경 없이 파일 읽기만으로 통합 (Zero changes to source systems).

## 17.2 전체 파이프라인 타임라인 (MacBook M5 Max 64GB)

| Phase | Duration | Dependency | Notes |
|-------|----------|------------|-------|
| EnvScan WF1-WF4 | ~120 min | Claude API + Web | HITL 9개 체크포인트 포함 시 2-4시간 |
| GlobalNews Crawl | ~53 min | 116 sites, rate-limited | |
| GlobalNews Analyze (8 stages) | ~45 min | CPU-bound, local ML | |
| Signal Normalization (NEW) | ~2 min | JSON/Parquet reads | |
| Investment Synthesis (NEW) | ~5-10 min | Rule-based | |
| Report Generation (NEW) | ~3-5 min | Template fill | |
| **Total** | **~230-240 min (~4시간)** | | 06:00 시작 → 10:00 완료 |

**네트워크 병목**: 두 시스템 모두 대규모 웹 스크래핑 → 순차 실행이 anti-bot 대응상 최적.

## 17.3 하드웨어 자원 분석

| 자원 | EnvScan | GlobalNews | 동시 최대치 | 가용 | 판정 |
|------|---------|-----------|-----------|------|------|
| RAM | ~4-6 GB | ~10 GB peak | ~16 GB | 64 GB | **여유 충분** |
| CPU | 중간 (4 병렬 에이전트) | 높음 (SBERT+BERTopic) | 12-14코어 | 18코어 | **여유 충분** |
| GPU (MPS) | 미사용 | PyTorch MPS | 공유 | M5 Max | **문제없음** |
| Network | 높음 (스크래핑+API) | 높음 (116 사이트) | 병목 | 가정용 인터넷 | **순차 권장** |

## 17.4 workflow.md 오케스트레이션 흐름

```
Step 1: Run GlobalNews (독립 실행)
  (bash) cd ../GlobalNews-Crawling-AgenticWorkflow
         .venv/bin/python main.py --mode full --date {today}
  Wait: data/output/{date}/signals.parquet 존재 확인

Step 2: Run EnvironmentScan (독립 실행 — 이미 운영 중)
  (claude-slash) /env-scan:run (quad WF)
  Wait: env-scanning/signals/database.json updated today

Step 3: Run InvestScan Normalization + Synthesis + Report
  (bash) python -m investscan.run --date {today}
```

**핵심 제약**: EnvScan은 Claude Code 슬래시 명령 시스템 → InvestScan 세션에서 subprocess 직접 호출 불가.
**해결책**: 산출물 의존 방식 — 각 시스템 별도 세션 실행 후, InvestScan은 결과 파일만 읽음.

## 17.5 Medallion Architecture (확정)

| 계층 | 파일 | 설명 |
|------|------|------|
| **Bronze** | `signals/database.json` + `data/output/signals.parquet` | 원시 수집 |
| **Silver** | `investscan/output/unified_signals.json` | 정규화 + 중복 제거 |
| **Gold** | `investscan/output/weekly-report.md` + `synthesis.json` | 분석 + 리포트 |

---

# Part XVIII: 업스트림 시스템 현황 + 비코더 부트스트래핑 (R7)

> **소스**: `upstream-bootstrap-analysis.md` (2026-03-28) — 실제 파일 시스템 직접 확인
> **역할**: PRD Section 3(User Journey - Day 0) 핵심 참조

## 18.1 업스트림 시스템 현재 상태 (실측)

| 시스템 | 상태 | 근거 |
|--------|------|------|
| **EnvScan** | ✅ 완전 운영 중 | `wf3-naver/reports/report-statistics-2026-03-20.json` 존재, `output/scan-report-2026-03-20.html` 존재 |
| **GlobalNews 크롤러** | ✅ 운영 중 | `data/raw/2026-03-18/all_articles.jsonl` (1.9MB, 402건) |
| **GlobalNews NLP 분석** | ❌ 미완료 | `.venv` 없음 → PyTorch/spaCy/sentence-transformers 미설치, `data/output/`에 Parquet 없음 |

**결론**: PRD Day 0 작업은 **GlobalNews ML 환경 설치 1회**만 필요. EnvScan은 이미 준비됨.

## 18.2 Day 0 GlobalNews 환경 설치 (Claude Code 자동화 가능 — 95%)

```bash
# Claude Code가 자동 실행하는 절차
cd GlobalNews-Crawling-AgenticWorkflow
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt    # 44+ 패키지, 2-5GB, 30-60분
.venv/bin/python -m spacy download en_core_web_sm
.venv/bin/playwright install chromium
.venv/bin/python scripts/preflight_check.py --project-dir . --mode full
```

**소요 시간**: 30-60분 (네트워크 속도에 따라)
**API 키**: 불필요 (완전 로컬, 무료)
**디스크**: 최소 5GB 필요

## 18.3 비코더 Day 0 전체 시나리오

```
Day 0 (최초 1회):
  Step 1: Claude Code 설치 (curl 1줄)
  Step 2: InvestScan workflow.md 실행 → Claude Code가 자동으로:
    - GlobalNews 가상환경 생성
    - 44+ 패키지 설치 (30-60분 자동 대기)
    - GlobalNews 테스트 실행 (dry-run)
    - InvestScan 패키지 설치
  Step 3: Telegram Bot 토큰 입력 (유일한 수동 작업)

완료 후:
  매주 launchd 자동 실행 → 리포트를 Telegram으로 수신
```

## 18.4 EnvScan 실행 제약 — PRD 필수 반영

**EnvScan은 Claude Code 에이전트 시스템**이므로:
- InvestScan workflow.md에서 subprocess로 직접 호출 **불가**
- **해결책**: 2-세션 방식
  - Session A: `cd EnvironmentScan && claude` → `/env-scan:run`
  - Session B: `cd InvestScan && claude` → `@workflow.md 실행`
  - InvestScan은 EnvScan 출력 파일 존재 여부만 확인 후 진행

**Fallback**: EnvScan 출력이 없으면 GlobalNews 데이터만으로 부분 리포트 생성 (성능 저하 원칙).

## 18.5 PRD Section 3 User Journey 보완 항목

현재 Part XIII(비코더 UX)에서 누락된 내용:

| 누락 항목 | 보완 내용 |
|---------|---------|
| Day 0 GlobalNews 설치 | 30-60분 자동 설치, API 키 불필요 |
| EnvScan 2-세션 방식 | 사용자가 2개 터미널 창을 쓰는 이유 설명 |
| 디스크 공간 요건 | 5GB+ 필요 |
| 첫 완전 리포트 도달 시간 | Day 0 설치(1시간) + EnvScan 실행(2-4시간) + GlobalNews 실행(1.5시간) + InvestScan(10분) = **약 5-6시간** |

---

# Part XIX: 스키마 검증 — 실측 수정 사항 (R7)

> **소스**: `schema-verification-actual.md` (2026-03-28) — 코드 직접 분석
> **역할**: PRD Section 6(Data Schema & Contracts) 정확성 보정

## 19.1 final-research.md 오류 수정

### 수정 1: WF4 priority-ranked pSST 스케일

| 항목 | 기존 서술 (Part I.1.4) | 실제 확인값 |
|------|----------------------|-----------|
| WF4 priority-ranked pSST | "부동소수점 0-10" | **공식 Python 엔진 = 0-100 float** (LLM 직접 생성 = 0-10, 비공식) |

**감지 방법**: `ranking_metadata.engine == "priority_score_calculator.py"` → 0-100 적용. engine 필드 없으면 0-10으로 처리.

### 수정 2: STEEPs 코드 변이 수

| 항목 | 기존 | 실제 |
|------|------|------|
| STEEPs 변이 수 | 명시 없음 | **17가지** (소문자 `"s"`, 장형, 전체 영문자 혼재) |

### 수정 3: GlobalNews signal_layer 구체 값

| 항목 | 기존 | 실제 코드 확인 |
|------|------|-------------|
| signal_layer | "L1-L5" | `L1_fad`, `L2_short`, `L3_mid`, `L4_long`, `L5_singularity` |

### 수정 4: burst_score 범위

| 항목 | 기존 | 실제 |
|------|------|------|
| burst_score 범위 | 미명시 | 0.0+ 무제한 (z-score 기반, 정규화 불필요) |

## 19.2 normalizers.py 핵심 구현 지침

```python
# pSST 스케일 명시적 감지 (auto-detection 금지)
def get_psst_scale(ranking_metadata: dict) -> tuple[float, float]:
    engine = ranking_metadata.get("engine", "")
    if engine == "priority_score_calculator.py":
        return (0.0, 100.0)   # 공식 Python 엔진
    else:
        # LLM 직접 생성 — 실측값 범위로 판단
        psst_val = ranking_metadata.get("psst_score", 0)
        return (0.0, 10.0) if psst_val <= 10 else (0.0, 100.0)

# GlobalNews importance_score 정규화 (0-100 → 0-1)
importance_normalized = importance_score / 100.0
```

## 19.3 PRD Data Schema 최종 상태

| 항목 | 상태 |
|------|------|
| EnvScan database.json 스키마 | ✅ 실데이터 검증됨 |
| EnvScan priority-ranked pSST | ✅ 코드 검증됨 (공식/비공식 구분) |
| STEEPs 17가지 변이 | ✅ 실데이터 검증됨 |
| GlobalNews signals.parquet 12컬럼 | ✅ 코드 검증됨 (실파일 없음) |
| GlobalNews analysis.parquet | ✅ 코드 검증됨 |
| GlobalNews 실제 Parquet 파일 | ⚠️ 미실행 — 첫 실행 후 재검증 필요 |

---

---

# Part XX: 주간 운영 E2E 타임라인 + 비용 구조 (R7)

> **소스**: `research/investscan-weekly-operation-e2e-cost-analysis.md` (2026-03-28, 397줄)
> **역할**: PRD Section 3(User Journey 시간 기대치) + Section 12(비용 구조) 핵심 참조

## 20.1 전체 파이프라인 타임라인

### 순차 실행 (MVP 기본 — 네트워크 병목 대응)

```
07:00  ── EnvironmentScan ─────────────────────────────
07:00  │ WF1 General Scan                    [~30 min]
07:30  │ WF2 arXiv Scan                      [~30 min]
08:00  │ WF3 Naver News Scan                 [~30 min]
08:30  │ WF4 Multi&Global News Scan          [~30 min]
09:00  ── EnvironmentScan Complete ──────────────────
09:00  ── GlobalNews-Crawling ──────────────────────
09:00  │ Crawl 116 sites                     [~53 min]
09:53  │ Analyze (8-stage NLP pipeline)      [~45 min]
10:38  ── GlobalNews Complete ──────────────────────
10:38  ── InvestScan Bridge ─────────────────────────
10:38  │ Signal Normalization                [~2 min]
10:40  │ Investment Synthesis                [~10 min]
10:50  │ Report Generation + Translation     [~10 min]
11:00  ── Pipeline Complete ─────────────────────────
Total: ~4시간 | 월요일 7시 실행 → 11시 완료
```

### 병렬 실행 (M4+, 안정화 후)

EnvScan과 GlobalNews는 데이터 독립 → 이론적 병렬 가능. **그러나 네트워크 경합 + 안티봇 차단 확률 급증으로 MVP에서는 순차 권장.**
병렬 시 총 시간: ~2시간 25분 (09:25 완료 → 주식 장 시작 전 가능).

## 20.2 EnvScan HITL 체크포인트 자동화

EnvScan 마스터 오케스트레이터는 **9개 HITL 체크포인트** 보유 (WF당 3개 × 4WF + 통합 1개).
**해결책**: `AGENTS.md §5.1 Autopilot Mode` 활성화 → 자동 승인 + 로깅. 4계층 품질 보장(L0→L1→L1.5→L2) 자동 실행으로 품질 유지.

## 20.3 Claude API 비용 구조

### EnvironmentScan 1회 실행 비용 (Sonnet 4.6)

| 구성 | Input | Output | 합계 |
|------|-------|--------|------|
| 4개 WF + Integration (총 ~1.84M / ~840K tokens) | $5.52 | $12.60 | **~$18.12** |

### InvestScan Bridge 1회 비용 (Sonnet 4.6)

| 구성 | Input | Output | 합계 |
|------|-------|--------|------|
| Synthesis + Report + Translation + Review (~270K / ~130K) | $0.81 | $1.95 | **~$2.76** |

### 주간 총 운영 비용 시나리오

| 모델 | 주간 | 월간 | 비고 |
|------|------|------|------|
| **Max 20x 구독 ($200/월)** | $0 | **$200** | EnvScan·InvestScan 구독 한도 내 포함 |
| **API Sonnet 4.6** | ~$20.88 | **~$84** | + Claude Pro $20 = ~$104 |
| **API Haiku 4.5** | ~$6.96 | **~$28** | + Claude Pro $20 = ~$48 |
| **API + Prompt Cache** | ~$2.37-4.73 | **~$9-19** | + Pro $20 = ~$29-39 |

**SerpAPI**: $0 (Google Scholar `enabled: false`, arXiv 무료 API 직접 사용).

**권장**: MVP(M1-M3) = Max 20x 구독 ($200), 안정화 후 API 전환 검토.

## 20.4 실패 시나리오 + 재실행 전략

### 시스템별 체크포인트 & 재실행

| 시스템 | 체크포인트 | 재실행 | Graceful Degradation |
|--------|-----------|--------|---------------------|
| EnvScan | WF별 + Context Preservation Hooks | `/env-scan:run --resume` | WF 단위 독립 재실행 가능 |
| GlobalNews | Stage별 | `python main.py --mode analyze --stage N` | 부분 크롤링도 분석 가능 |
| InvestScan | `pipeline_state.json` | `investscan run --resume --date {date}` | 마지막 완료 step부터 |

### 단일 소스 성능 저하 정책

| 가용 데이터 | 리포트 품질 | 동작 |
|-----------|-----------|------|
| EnvScan + GlobalNews | Full quality | 정상 |
| EnvScan only | Degraded | GlobalNews 부재 경고 포함 |
| GlobalNews only | Degraded | EnvScan 부재 경고 포함 |
| 둘 다 없음 | **중단** | 데이터 없이 생성 불가 |

### launchd 스케줄 권장 설정

```bash
# Sunday 19:50 자동 wake → 20:00 launchd 트리거
sudo pmset repeat wake SU 19:50:00
```
plist: `StartCalendarInterval` Weekday=0, Hour=20, Minute=0.

## 20.5 자동 재시도 예산 (Bounded Retry)

| 컴포넌트 | Max 재시도 | 간격 | 에스컬레이션 |
|---------|-----------|------|------------|
| EnvScan 개별 WF | 2회 | 5분 | Telegram 알림 |
| GlobalNews Crawl | 1회 | 10분 | 가용 데이터로 계속 |
| GlobalNews Analyze Stage | 2회 | 1분 | 해당 stage 스킵, 저하 출력 |
| InvestScan Normalize | 3회 | 즉시 | Abort (파서 버그 의심) |
| InvestScan Report | 2회 | 1분 | Raw data dump 제공 |

---

# Part XXI: 비코더 설정 개인화 메커니즘 (R7)

> **소스**: `research/non-coder-personalization-mechanisms.md` (2026-03-28, 715줄)
> **역할**: PRD Section 3(User Journey) + Section 5.1(Green Zone Features) 핵심 참조

## 21.1 핵심 결론: Claude Code = 최적 설정 인터페이스

| Tier | 방법 | LOC | 추천 |
|------|------|-----|------|
| **Tier 1** | Claude Code 자연어 대화 → YAML 자동 수정 | **0 LOC** | **기본** |
| Tier 2 | InquirerPy CLI Wizard | 200-400 LOC | Fallback |
| Tier 3 | Streamlit Web GUI | 300+ LOC | 과잉 |

InvestScan은 Claude Code 위에서 실행되므로, 별도 설정 도구 없이 자연어 대화만으로 모든 개인화 가능. Home Assistant Configuration Agent(2025)가 동일 패턴 검증.

## 21.2 자격증명 보안 (macOS Keychain)

| 방법 | 보안 | 비코더 친화 | 결정 |
|------|------|-----------|------|
| **macOS Keychain (keyring 라이브러리)** | Best (OS 암호화, Touch ID) | 중간 | **권장** |
| .env 파일 | Low (plaintext) | 중간 | Fallback |
| investscan.yaml 직접 | **Worst** (git 유출) | 최고 | **절대 금지** |

```python
# 저장 (1줄)
keyring.set_password("investscan", "telegram_bot_token", token)
# 런타임 조회
keyring.get_password("investscan", "telegram_bot_token")
```
investscan.yaml에는 `credentials.source: keychain`만 기록 — 토큰 자체 없음.

## 21.3 초기 설정 UX: Zero-Decision Onboarding (GPT4All 패턴)

```
사용자: "InvestScan 처음 설정해야 해"
Claude Code: 3가지만 여쭤볼게요.
  1. 분석 섹터: a) 전체 10개 [추천]  b) IT 중심  c) 직접 선택
  2. 투자 성향: a) 보수적 [추천]  b) 공격적
  3. 알림:      a) 화면 출력 [추천]  b) Telegram  c) Gmail
→ 3개 질문, 추천 선택지 표시, 고급 설정은 나중에
```

**핵심 원칙 6가지** (PRD 포함 필수):
1. Claude Code = Primary Interface (YAML은 내부 표현)
2. 기본값 우선 (Sensible Defaults First)
3. 자격증명은 Keychain만 (YAML 직접 저장 절대 금지)
4. 변경 전 항상 Diff 확인 + 승인 요청
5. Hot reload 불필요 (다음 실행 시 자동 적용)
6. 이력 관리 = Git (별도 시스템 불필요)

## 21.4 설정 변경 자연어 패턴 예시

```
"IT랑 헬스케어만 봐줘"     → sectors 변경 + diff 표시 + 확인
"삼성전자 특별히 주목해줘"   → watch_tickers 추가
"설정 원래대로 돌려줘"      → git log 이력 조회 → 선택 → 복원
"이번 달만 공격적으로"      → style 변경 + 4주 후 리마인더 자동 설정
```

## 21.5 investscan.yaml 권장 구조

```yaml
# 사용자가 직접 편집할 필요 없음 — Claude Code가 자동 관리
sectors: [IT, Healthcare, Energy, Finance, Materials,
          Industrials, Consumer, Utilities, Real_Estate, Communication]
investment_style: conservative    # conservative | aggressive
watch_tickers: []
exclude_tickers: []

report:
  language: ko
  length: standard                # brief | standard | detailed

notifications:
  telegram:
    enabled: false
    chat_id: ""                   # token은 Keychain에 저장
  email:
    enabled: false
    sender: ""
    recipient: ""                 # app_password는 Keychain에 저장

schedule:
  enabled: false
  cron: "0 20 * * 0"             # 매주 일요일 20:00

credentials:
  source: keychain                # keychain | env
```

## 21.6 구현 우선순위 + LOC

| 우선순위 | 기능 | LOC | 마일스톤 |
|---------|------|-----|---------|
| P0 | investscan.yaml 기본 구조 + 기본값 프리셋 | 50 | M1 |
| P0 | Claude Code 대화형 초기 설정 흐름 | 0 (패턴만) | M1 |
| P1 | keyring 통합 (Telegram + Gmail) | 30 | M1 |
| P1 | Config validation | 80 | M2 |
| P2 | CLI wizard fallback (`investscan setup`) | 200 | M3 |
| P3 | Config history snapshots | 50 | M3 |
| **합계** | | **~410 LOC** | |

---

# Part XXII: 리포트 수신 → 의사결정 → 피드백 루프 (R7)

> **소스**: `research/post-report-decision-workflow.md` (2026-03-28, 579줄)
> **역할**: PRD Section 3(User Journey - Phase 1-3) + Section 5.1(Green Zone: 결정 저널) 핵심 참조

## 22.1 주간 루틴 타임라인 (총 25-30분/주)

```
일요일 밤 (자동)       월요일 아침         월요일 오전        금요일 (선택)
─────────────────────────────────────────────────────────────────────
[PHASE 0: 파이프라인]  [PHASE 1: 읽기]    [PHASE 2: 결정]   [PHASE 3: 기록]
완전 자동             5분                10-15분           10분
- investscan run     - Telegram 알림     - 증권사 앱 확인   - 이번 주 행동 기록
- 리포트 생성          - 핵심요약 30초      - 최대 3개 결정    - Telegram 답장
- Telegram 전송      - 관심 섹터 상세     - 결정 근거 메모   - 시스템이 구조화
- 저널 리마인더        - 행동 체크리스트    (관망도 유효)      - 다음 주 관심 메모
```

**4가지 설계 원칙**: Progressive Disclosure(3층), Time-Boxing(30분), Decision Fatigue 방지(최대 3결정/주), Habit-Forming Trigger(Telegram 알림)

## 22.2 3층 Progressive Disclosure 리포트 구조

```
Layer 1: Telegram 요약 (30초)
  - 1문장 시장 방향 + 확신도 게이지
  - 이번 주 행동 체크리스트 (최대 3개)
  - "자세히 보기" 링크

Layer 2: 핵심 리포트 (5분)
  - [Section 0 신규] 이번 주 행동 체크리스트 (최상단)
  - Executive Summary
  - 내 포트폴리오 관련성 (보유 섹터 하이라이트, 조건부)
  - 위험 경고

Layer 3: 전체 분석 (15분, 선택)
  - 14개 섹터 전체 + STEEPs 히트맵 + 증거 체인
```

**Section 0 행동 체크리스트 (Morningstar 패턴 적용)**:

| 항목 | 확신도 | 구체적 행동 |
|------|--------|----------|
| [관찰] 반도체 강세 지속 | 78% | 삼성전자·SK하이닉스 현재가 대비 목표가 확인 |
| [비중축소 검토] 2차전지 약세 | 61% | 2차전지 ETF 보유 중이면 -5% 비중 축소 고려 |
| [관망] 바이오 — 시그널 혼재 | 43% | 없음. 다음 주 확인 |

**규제 안전**: "매수 추천" 절대 금지 → "관찰", "비중축소 검토", "관망"으로 대체.

## 22.3 Telegram 양방향 피드백 루프

### 피드백 수집 (답장 1줄)

```
사용자 입력 (자연어):
"반도체 ETF 5% 추가 매수. 리포트 신호 믿고."
"이번 주 관망. 특별한 신호 없었음."
"IT 예측 틀렸음. 단기 예측 부정확."

시스템 변환 (구조화):
{ action_type: "buy", sector: "반도체",
  signal_alignment: "aligned", user_assessment: "positive" }
```

**변환 메커니즘**: 규칙 기반 키워드 매핑(비용 $0) → 실패 시 LLM 폴백.

### 피드백 → 리포트 개선 3가지 경로

```
피드백 (Telegram 답장)
    │
    ├─▶ 경로 A: 정확도 추적 (자동, 매주)
    │   "지난주 3방향 예측 vs 실제 섹터 수익률 → 정확도 표시"
    │
    ├─▶ 경로 B: 관심 섹터 학습 (자동, 매주)
    │   "3주 연속 언급 섹터 → watched_sectors 자동 추가 제안"
    │
    └─▶ 경로 C: 확신도 보정 (월간, 반자동)
        "특정 STEEPs 유형 적중률 낮으면 보정 계수 적용"
```

## 22.4 결정 저널 Telegram 인터페이스

기존 `journal.py` (CLI 기반)의 상위 인터페이스로 Telegram Bot 사용:

```
[사용자] ─Telegram 답장─▶ [Bot] ─파싱─▶ [journal.py API] ─▶ decision_journal.jsonl
```

비코더는 CLI 명령어 없이 Telegram 답장만으로 저널 기록. `journal.py`는 백엔드 저장만 담당.

## 22.5 config.yaml 추가 필드

```yaml
user_profile:
  watched_sectors: [반도체, 2차전지]   # 자동 학습 + 수동 추가
  held_sectors: [반도체, 2차전지]      # 실제 보유 (수동 입력)

feedback:
  telegram_enabled: true
  weekly_reminder_day: friday
  weekly_reminder_time: "17:00"
  monthly_eval_enabled: true

calibration:
  steeps_correction:                   # STEEPs 유형별 확신도 보정 계수 (월간 갱신)
    T: 1.0
    E_economic: 0.95
    P: 0.85
  convergence_bonus: 0.10              # 두 소스 수렴 시 확신도 보너스
  min_action_confidence: 0.50          # 행동 체크리스트 최소 확신도
  max_actions_per_week: 3              # Decision Fatigue 방지
```

## 22.6 구현 우선순위 + LOC

| 기능 | LOC | 마일스톤 |
|------|-----|---------|
| 리포트 Section 0 (행동 체크리스트) | ~80 | **M1 필수** |
| Telegram 요약에 체크리스트 포함 | ~30 | **M1 필수** |
| Telegram 양방향 피드백 수신 | ~120 | **M1 필수** |
| 자연어→저널 변환 (규칙 기반) | ~80 | **M1 필수** |
| 정확도 자동 추적 (KRX 연동 후) | ~150 | M2 |
| 관심 섹터 자동 학습 | ~60 | M2 |
| 내 포트폴리오 관련성 섹션 | ~50 | M2 |
| 시그널 가중치 보정 | ~100 | M3 |
| 월간 자가 평가 전송 | ~80 | M2 |
| **합계** | **~750 LOC** | |

**Balanced Scenario 총 LOC 재추정**: ~2,710 (기존) + ~410 (Part XXI) + ~750 (Part XXII) = **~3,870 LOC**

---

# Part XXIII: PRD 작성을 위한 최종 통합 지침 (R7)

> **소스**: R7 성찰 전체 — 두 독자 분리, LOC 재추정, 수정 사항 통합

## 23.1 PRD의 두 독자 — 각자에게 필요한 것

| 독자 | 필요 | PRD 섹션 |
|------|------|---------|
| **사용자 (비코더 목사)** | 비전, 여정, 성공 기준, 시간/비용 기대치 | Executive Summary, Problem Statement, User Journey, Success Metrics |
| **Claude Code (workflow.md 경유)** | 스키마, 모듈 명세, Done Gate, 에러 복구 패턴 | Data Schema & Contracts, Technical Architecture, Implementation Architecture |

**핵심**: 같은 문서에서 두 독자를 모두 만족시켜야 함. 사용자 섹션은 기술 용어 최소화, Claude Code 섹션은 모호함 0.

## 23.2 R7 반영 후 최종 LOC 추정

| 컴포넌트 | LOC |
|---------|-----|
| 기존 InvestScan Bridge (Rounds 1-6) | ~2,710 |
| Part XXI: 개인화 메커니즘 | +~410 |
| Part XXII: 피드백 루프 | +~750 |
| **총 추정** | **~3,870 LOC** |
| 33% 버퍼 포함 | **~5,150 LOC 이내** |

## 23.3 R7 수정 사항 요약 (PRD Data Schema 반영 필수)

1. **pSST 스케일**: 공식 Python 엔진 = 0-100 (engine 필드 존재 시). LLM 직접 생성 = 0-10 (비공식). `ranking_metadata.engine` 필드로 구분.
2. **STEEPs 17가지 변이**: 소문자 `"s"`, 장형 `"T_Technological"`, 전체 영문 `"Economic"` 포함 — 완전 매핑 테이블 필수.
3. **GlobalNews signal_layer 구체 값**: `L1_fad`, `L2_short`, `L3_mid`, `L4_long`, `L5_singularity`.
4. **burst_score 무제한**: 정규화 불필요, 백분위 기반 상대 비교.
5. **importance_score**: analysis.parquet 전용, 0-100 → /100 변환 필요.
6. **GlobalNews 실제 파일 없음**: 첫 실행 후 실제 Parquet 재검증 필요.

## 23.4 갱신된 PRD 구조 권장 (Part XI.2 대체)

```
1. Executive Summary (카테고리 창조자 + 종목 관찰 + Balanced 확장 시나리오)
2. Problem Statement (빈 사분면 + 완전한 비전)
3. User Journey (비코더 관점: Day 0 → Week 1 → Monthly Routine)
   3.1 Day 0: GlobalNews 환경 설치 (30-60분, Claude Code 자동) [Part XVIII]
   3.2 첫 주: EnvScan 2-세션 방식 + InvestScan 첫 실행 [Part XVIII]
   3.3 주간 루틴: 25-30분/주 (Phase 0-3) [Part XXII]
   3.4 설정 변경: Claude Code 자연어 대화 [Part XXI]
4. User Personas (3 Edge Case + 1 Non-Target)
5. Product Requirements
   5.1 Green Zone (6기능 + 종목 워치리스트 + 행동 체크리스트)
   5.2 Yellow Zone
   5.3 Red Zone
6. Data Schema & Contracts
   6.1 UnifiedSignal schema (검증됨) [Part XIX]
   6.2 STEEPs 17-변이 정규화 테이블 [Part XIX]
   6.3 GlobalNews signals.parquet 12컬럼 (코드 검증) [Part XIX]
   6.4 6가지 비타협 원칙
7. Technical Architecture
   7.1 기술 스택 (Green/Yellow/Red)
   7.2 모듈 목록 (~3,870 LOC) [Part XXIII 갱신]
   7.3 의존성 순서 그래프
   7.4 실제 파일 경로 + config.py [Part XVII]
8. Implementation Architecture (for Claude Code)
   8.1 세션 간 상태 유지 전략
   8.2 Done Gate 정의 (모듈별)
   8.3 에러 복구 패턴
   8.4 workflow.md 오케스트레이션 흐름 [Part XVII]
9. External Integration
   9.1 Green Zone (FDR, Telegram 양방향, Gmail, launchd)
   9.2 Yellow Zone
10. Validation Framework [Part XV]
11. Legal & Compliance [Part XIV]
12. Cost & Operations [Part XX]
    12.1 주간 타임라인 (순차 4시간 / 병렬 2.5시간)
    12.2 비용 구조 (Max 20x $200/월 권장)
    12.3 실패 복구 + Graceful Degradation
13. Personalization UX [Part XXI]
    13.1 Claude Code 대화형 설정
    13.2 자격증명 Keychain 관리
    13.3 investscan.yaml 구조
14. Post-Report Decision Workflow [Part XXII]
    14.1 3층 Progressive Disclosure
    14.2 Telegram 피드백 루프
    14.3 결정 저널 통합
15. Success Metrics (정량 + 정성)
16. Risk Register
17. Open Questions (결정 필요 사항만)
18. Workflow.md 변환 가이드 [Part XVI]
```

---

---

# Part XXIV: PRD.md 범위 한정 지침 — 불필요 항목 성찰 (R8)

> **성찰 방법**: 3개 병렬 teammate 에이전트 투입 (Part I-VIII / Part IX-XVI / Part XVII-XXIII 분담)
> **성찰 기준**: "비코더 목사가 로컬 MacBook에서 실행하는 투자방향+종목추천 시스템의 Claude Code workflow.md 사전 작업으로서 PRD.md 작성"에 **불필요한 것**을 찾는다
> **발견**: 총 50+ 불필요 항목, 5개 카테고리로 분류

---

## 24.1 핵심 발견: 5가지 불필요 카테고리

### 카테고리 A — 연구 과정 아티팩트 (Research Process Artifacts)
> PRD는 **결정된 사항**만 담는다. 결정 과정·긴장·미해결 질문은 연구 문서용이다.

| 위치 | 항목 | PRD 처리 |
|------|------|---------|
| Part IX 전체 | 교차 라운드 긴장 해소 (T1-T10) | **완전 제거** |
| Part X 전체 | 미해결 질문 + 추가 조사 영역 | **완전 제거** (10.1 "즉시 결정 필요" 6항목만 Risk Register 각주로) |
| Part VI.5 | Round 3→4 수정 비교표 | **완전 제거** (이미 최신 버전으로 대체됨) |
| Part IV.1 | 3-시나리오 선택 근거 6가지 | **1줄 요약**: "Balanced 선택: ~3,870 LOC, 주 3시간, 성공률 70-80%" |
| Part IV.3 | 거부된 Spine+Rib 아키텍처 | **완전 제거** |
| Part XI Section 15 | "Workflow.md 변환 가이드" | **별도 파일로 분리** (PRD 외부) |
| Part XVI.4 | 구현 단계 마크다운 템플릿 | **별도 파일로 분리** (workflow.md 작성 가이드) |
| Part XVI.6 | Handoff Capsule 템플릿 | **완전 제거** (workflow.md 영역) |
| Part XXIII.4 | PRD 구조 권장 Section 12-14 | **완전 제거** (PRD 작성 가이드이지 PRD 내용이 아님) |

---

### 카테고리 B — 이론적/학문적 배경 (Theoretical/Academic Background)
> PRD는 "**무엇을** 구현하라"는 명세다. **왜 그 이론이 맞는지**는 Claude Code 구현에 불필요하다.

| 위치 | 항목 | PRD 처리 |
|------|------|---------|
| **Part V 전체** (~400줄) | 이론적 기반 전체 (Fama/Lo, Meadows, Simon 1956, Tetlock, BERTopic, KR-FinBERT, EMH, MPT, Soros) | **완전 제거** → 각 구현 모듈 주석으로 결론만 이동 (예: "감성 제외 — 상관관계 95% 허위") |
| Part XII.4 | 팩터 전략 학술 배경 (Fama-French ★등급, MGMT·PERF) | **완전 제거** → "팩터 가중치: 35% Value + 40% Momentum + 25% Quality" 숫자만 유지 |
| Part XV.1 서두 | 왜 백테스팅이 불가능한가 | **완전 제거** → "Brier Score 기반 전향적 검증 사용" 1줄만 |
| Part XV.4 | 이항검정 통계적 유의성 표 | **완전 제거** → "Month 2 Kill Switch: Brier Score ≥ 0.30" 만 유지 |
| Part XVI.1 | Anthropic C 컴파일러 사례 (실증 근거) | **1줄 요약**: "실증: 30시간+ 자율 구현 사례 존재" |
| Part XVII.3 | 하드웨어 자원 상세 분석 (MPS, 병렬 코어) | **1줄 요구사항**: "MacBook M3 이상, 16GB+ RAM 필요" |
| Part XXI.1 | Claude Code vs Tier 2/3 비교표 | **1줄 결론**: "설정은 Claude Code 자연어 대화로만 수정" |

> ⚠️ **가장 큰 제거 대상**: Part V 전체는 약 400줄이며 학술 논문 수준의 이론 서술이다. PRD.md에서 이 내용이 없어도 Claude Code는 구현에 전혀 지장이 없다. **결론만 각 모듈 명세에 1-2줄로 이동하면 충분하다.**

---

### 카테고리 C — SaaS·마케팅 관점 (SaaS/Marketing Perspective)
> 이 시스템은 **100% 로컬**이다. SaaS 제품 비교·시장 규모·포지셔닝은 구현 명세와 무관하다.

| 위치 | 항목 | PRD 처리 |
|------|------|---------|
| Part I.2 | "카테고리 창조자" 포지셔닝 | **완전 제거** → Part I.1 제품 개요 표로 흡수 |
| Part II.1 | AlphaSquare 상세 분석 (CEO, 설립일, 투자규모, 앱 평점, 불만 상세) | **1줄 요약**: "AlphaSquare: 월 70K원 종목 AI 분석, 매크로 환경 스캐닝 부재" |
| Part II.4 | 시장 데이터 (TAM 2-5만, MZ세대 이탈, KOSPI 수익률) | **완전 제거** |
| Part III.2 | 메인스트림 전환 불가 분석 (김민수 대리 페르소나) | **완전 제거** |
| Part III.4 | 총소유비용(TCO) 비교 (학습 곡선 20시간+, 월비용 비교) | **완전 제거** |
| Part XVII.5 | Medallion Architecture 이름·계층 설명 | **완전 제거** → "Bronze→Silver→Gold 파이프라인" 다이어그램 흐름만 1줄로 |
| Part VIII.5 | "우리가 틀릴 경우" 피벗 시나리오 | **완전 제거** (연구용 대비책, PRD 아님) |

---

### 카테고리 D — M2/M3 미래 기능 (Future Features Beyond MVP)
> PRD.md는 **M1 MVP만** 다룬다. M2/M3 확장 계획은 PRD를 복잡하게 만들고 Claude Code를 혼란스럽게 한다.

| 위치 | 항목 | 현재 Phase | PRD 처리 |
|------|------|----------|---------|
| Part VII.3 | Gemini CLI / 멀티모델 AI 통합 | M3 | **완전 제거** |
| Part VII.4 | Yellow Zone 연동 전체 | M2+ | **1줄 각주**: "M2+ 조건부 기능 목록" |
| Part XX.1 | 병렬 실행 최적화 (~2.5시간) | M4+ | **완전 제거** |
| Part XX.5 | 컴포넌트별 재시도 예산 상세표 | M2+ | **1줄**: "실패 시 1-2회 자동 재시도 후 사용자 알림" |
| Part XI.3 | 6개월 KPI 테이블 (GitHub 스타, 활성 사용자 등) | M4+ | **각주로 이동** |
| Part XII.6-7 | Conviction 5단계 (STRONG_WATCH~AVOID) + Evidence Chain 예시 | M2 | **3단계로 단순화**: "Bullish / Neutral / Bearish" |
| Part XIII.4-5 | 구독 플랜 비교표 + Self-Healing 패턴 | M2 | **1줄**: "Claude Pro(또는 Max) 구독 필수" |
| Part XXI.3 | Zero-Decision Onboarding 3-질문 상세 UX flow | M2 | **1줄**: "초기 설정 3-4가지 Claude Code 대화로 수행" |
| Part XXI.4 | "이번 달만 공격적으로" 리마인더 자연어 패턴 | M3 | **제거**: 단순 sector/style 변경 예시만 유지 |
| Part XXI.6 | P2/P3 개인화 항목 (CLI wizard ~200 LOC, Config history ~50 LOC) | M3 | **백로그 이동** → P0/P1 ~440 LOC만 M1 PRD에 포함 |
| Part XXII.2 | 내 포트폴리오 관련성 레이어 | M2 | **백로그 이동** |
| Part XXII.3 | 피드백 경로 B (관심 섹터 자동 학습) + C (확신도 보정) | M2+ | **백로그 이동** → 경로 A(정확도 추적)만 M1 |
| Part XXII.6 | M2/M3 구현 항목 (자동 검증, 시그널 보정 등) | M2/M3 | **백로그 이동** |

> ⚠️ **MVP LOC 재계산**: M2/M3 항목 제거 후 M1 MVP 실제 범위는 **~1,800-2,000 LOC** (기존 ~3,870 LOC에서 대폭 축소). PRD.md는 M1 기준으로 작성하고 "M2/M3 백로그" 섹션을 별도로 명시해야 한다.

---

### 카테고리 E — 구현 코드·템플릿 (Implementation Code/Templates)
> PRD는 **"무엇을" 원하는지** 명세다. **"어떻게" 코딩하는지**는 workflow.md와 Claude Code의 영역이다.

| 위치 | 항목 | PRD 처리 |
|------|------|---------|
| Part VI.7 | 6가지 안티패턴 (Dict 기반 신호 전달 금지, 평균 금지 등) | **workflow.md 주석으로 이동** → PRD에서는 "가중 중위값 사용" 원칙만 1줄 |
| Part XV.7 | 자동 검증 파이프라인 흐름도 (predictions.db → FinanceDataReader → 월간 보고서) | **1줄 요구사항**: "예측 자동 저장 + 월간 정확도 보고서 자동 생성" |
| Part XVI.5 | pytest 스타일 금융 안전 검증 코드 예시 | **1줄**: "pSST 정규화 오류 방지: 명시적 스케일 파라미터 + 가중 중위값 필수" |
| Part XIX.2 | `get_psst_scale()` Python 함수 코드 블록 | **완전 제거** → "engine 필드 기반 0-100 vs 0-10 판별" 원칙만 유지 |
| Part XVIII.2 | Day 0 GlobalNews bash 스크립트 6줄 | **1줄**: "Day 0: Claude Code와 함께 GlobalNews 환경 설치 (30-60분)" |
| Part VI.1 | 이미 구현된 EnvironmentScan/GlobalNews 모듈 상세 목록 | **1줄**: "상류 시스템(EnvironmentScan v2.5.0 + GlobalNews-Crawling): 변경 없이 사용" |

---

## 24.2 PRD.md 포함 vs 제외 결정 매트릭스

> 이 매트릭스를 기준으로 PRD.md를 작성한다. "포함" 열이 PRD.md의 실제 내용 범위다.

| final-research.md Part | PRD 포함 여부 | 포함 시 처리 방식 |
|----------------------|------------|----------------|
| Part I.1 (제품 개요) | ✅ 포함 | 그대로 |
| Part I.2 (포지셔닝) | ❌ 제외 | 제거 |
| Part II.1-3 (경쟁 분석 핵심) | ✅ 1줄 | "AlphaSquare 1줄 + 구조적 해자 3가지"만 |
| Part II.4 (시장 데이터) | ❌ 제외 | 제거 |
| Part III.1 (타겟 3 페르소나) | ✅ 포함 | 그대로 |
| Part III.2-4 (메인스트림, TCO) | ❌ 제외 | 제거 |
| Part IV.1 시나리오 선택 | ✅ 1줄 | "Balanced 선택" 결론만 |
| Part IV.2 GREEN Zone | ✅ 포함 | 그대로 |
| Part IV.2 YELLOW/RED Zone | ✅ 목록만 | 상세 트리거 조건 제거 |
| Part IV.3 (거부 아키텍처) | ❌ 제외 | 제거 |
| **Part V 전체** | ❌ 제외 | **완전 제거** |
| Part VI (모듈 목록) | ✅ M1만 | M2/M3 모듈 제거, 신규 모듈만 |
| Part VI.5 (R3→R4 비교) | ❌ 제외 | 제거 |
| Part VI.7 (안티패턴) | ✅ 원칙만 | 코드 제거, 1줄 원칙만 |
| Part VII Green Zone | ✅ 포함 | 그대로 |
| Part VII Yellow/Red | ✅ 각주 | "M2+ 조건부" 각주만 |
| Part VIII (리스크) | ✅ 기술 리스크만 | 피벗 시나리오 제거 |
| **Part IX 전체** | ❌ 제외 | **완전 제거** |
| **Part X 전체** | ❌ 제외 | **완전 제거** (10.1만 각주) |
| Part XI (PRD 권고) | ✅ 원칙만 | 6개월 KPI 각주, Section 15 제거 |
| Part XII (종목 Bridge) | ✅ 단순화 | 5단계→3단계, 학술 WHY 제거 |
| Part XIII (비코더 UX) | ✅ 단순화 | 구독 플랜 1줄, Self-Healing 제거 |
| Part XIV (규제) | ✅ 핵심만 | 2026 규제 동향 각주, 3요건만 유지 |
| Part XV (검증) | ✅ 결론만 | 이론 서두 제거, 코드 제거 |
| Part XVI (workflow 패턴) | ✅ 원칙만 | 코드 제거, 템플릿 제거 |
| Part XVII (아키텍처) | ✅ 경로+흐름만 | Medallion 이름 제거, 하드웨어 1줄 |
| Part XVIII (부트스트래핑) | ✅ 지침만 | bash 제거, 2-세션 1줄 |
| Part XIX (스키마) | ✅ 스펙만 | Python 코드 제거, ⚠️ 표 단순화 |
| Part XX (운영+비용) | ✅ M1만 | 병렬 제거, 재시도 1줄 |
| Part XXI (개인화) | ✅ M1 P0/P1만 | P2/P3 백로그 이동 |
| Part XXII (피드백 루프) | ✅ 경로 A만 | 경로 B/C 백로그 이동 |
| Part XXIII (최종 지침) | ✅ M1 범위만 | LOC M1 기준 재계산 |

---

## 24.3 PRD.md의 두 독자 원칙 — R8 보정

> R7에서 "두 독자 원칙(비코더 목사 + Claude Code)"을 정의했다. R8 성찰을 통해 이 원칙을 더 엄격히 적용한다.

### 독자 1: 비코더 목사 (사용자)
- **필요한 것**: 무엇이 만들어지는지, 어떻게 사용하는지, 비용은 얼마인지
- **불필요한 것**: 이론적 근거, 기술 아키텍처 세부 사항, 학술 참고문헌
- **PRD 처리**: 섹션 1-3 (정체성, 사용자 여정, 비용)에 집중. 기술 섹션은 "Claude Code가 참조하는 섹션"임을 명시

### 독자 2: Claude Code (구현자)
- **필요한 것**: 무엇을 만들어야 하는지, 어떤 파일 경로/스키마/원칙을 따라야 하는지, 완료 기준
- **불필요한 것**: 결정 과정, 경쟁사 분석, 이론 배경, M2/M3 기능
- **PRD 처리**: 섹션 5-14에 구현 명세, Done Gate, 에러 복구 패턴 집중

### 구분선 원칙
> PRD.md의 모든 문장에 다음 질문을 적용한다:
> **"이 문장이 없으면 Claude Code가 틀리게 구현하거나, 사용자가 서비스를 이해 못하는가?"**
> → "아니오"이면 제거한다.

---

## 24.4 MVP M1 범위 확정 (R8 정제)

> M2/M3 항목을 제거한 후 M1 MVP 실제 범위:

| 모듈 | LOC (M1) | 비고 |
|------|---------|------|
| config.py + 경로 관리 | ~100 | 실제 경로 하드코딩 |
| normalizers.py (6-포맷 파서) | ~300 | **최중요 모듈** |
| dedup.py (중복 제거) | ~150 | |
| steeps_classifier.py (리분류) | ~200 | |
| signal_bridge.py (GICS 매핑) | ~200 | |
| synthesize.py (방향성 합성) | ~200 | |
| report_generator.py (리포트) | ~200 | |
| weekly_orchestrator.py | ~150 | |
| telegram_notifier.py | ~100 | 단방향 M1 |
| personalizer.py (P0/P1) | ~200 | investscan.yaml + Keychain |
| accuracy_tracker.py | ~150 | 경로 A만 |
| **합계 (버퍼 20% 포함)** | **~2,100 LOC** | |

> ⚠️ **기존 ~3,870 LOC → M1 실제 ~2,100 LOC**: 약 46% 감소. 차이는 M2/M3 기능(피드백 경로 B/C, 개인화 P2/P3, 병렬 실행, 검증 파이프라인 완전체 등)이 차지한다.

---

## 24.5 PRD.md 작성 시 절대 포함하지 말 것 (금지 목록)

> 아래 항목은 PRD.md 어디에도 등장해서는 안 된다.

1. **이론 인용** — Fama/Lo/Tetlock/BERTopic/EMH/MPT 등 학술 근거
2. **경쟁사 상세** — AlphaSquare CEO/투자규모/앱평점/사용자 불만 세부
3. **시장 규모 수치** — TAM, SAM, MZ세대 비율, KOSPI 수익률
4. **결정 과정** — "Round 3에서 Round 4로 바뀐 이유", "T1~T10 긴장"
5. **미해결 질문** — "사용자 인터뷰 필요", "6개월 전향 데이터 필요"
6. **M2/M3 기능 상세** — 포트폴리오 연동, 피드백 경로 B/C, 멀티모델 AI
7. **Python/bash 코드 블록** — 구현은 Claude Code의 영역
8. **피벗 시나리오** — "틀릴 경우 116소스 집계자로 전환"
9. **하드웨어 상세 분석** — GPU MPS, 병렬 코어 수 계산
10. **마케팅 포지셔닝** — "카테고리 창조자", "11차원 비교에서 패배"

---

## 24.6 R8 성찰 핵심 요약

> **성찰의 핵심 발견**: `final-research.md`는 PRD.md를 만들기 위한 **연구 자료**로서 탁월하게 완성되었다. 그러나 이 연구 자료를 그대로 PRD.md로 변환하면 실패한다. 연구 자료는 **"왜?"를 설득하는 문서**이고, PRD는 **"무엇을 만들어라"는 명세서**다.

**세 가지 성찰 결론:**

1. **Part V 전체 제거**: ~400줄의 학문적 이론 기반은 연구 정당화에는 탁월하지만 PRD 구현 지침으로는 제로 가치. 각 결론만 1줄씩 해당 모듈 명세에 이동.

2. **M1 울타리 엄격화**: PRD.md는 M1 MVP (~2,100 LOC)만 다룬다. M2/M3는 별도 "Future Backlog" 섹션에 목록만 유지. 현재 final-research.md에는 M1/M2/M3가 혼재되어 Claude Code가 무엇을 먼저 만들어야 하는지 불분명.

3. **두 독자 구분선**: 모든 문장에 "이게 없으면 Claude Code가 틀리게 구현하거나 사용자가 이해 못하는가?"를 적용. 아니오이면 무조건 제거. 이 필터 하나로 PRD.md 분량이 40-50% 감소하고 명확도가 2-3배 향상된다.

---

*R8 (2026-03-28): Part XXIV 추가 — 3개 병렬 teammate 에이전트의 "불필요 항목 성찰" 결과 통합. 총 50+ 불필요 항목을 5개 카테고리로 분류, PRD.md 포함/제외 결정 매트릭스 확정, MVP M1 LOC 재계산 (~3,870 → ~2,100), 금지 목록 10개 확정.*

---

# Part XXV: 적대적 성찰 — 공격·방어·개선안 (R9)

> **성찰 방법**: 4개 적대적 에이전트 병렬 투입 — 각 에이전트는 다른 각도에서 시스템 설계를 공격
> - **Agent 1**: 회의론자 (ROI·시간비용·경쟁 현실)
> - **Agent 2**: 비코더 UX 현실 검증 (실제 설치·운영·피드백 마찰)
> - **Agent 3**: 기술 현실주의자 (기술 가정·구현 취약점·유지보수)
> - **Agent 4**: 투자 논리 비판자 (신호 품질·검증 지표·한국 시장 특수성)

---

## 25.1 공격 1: ROI·시간비용 현실화 (회의론자)

### 공격 요지
> "Year 1 총비용이 AlphaSquare 5년치 구독료이고, '주 2-4시간'은 실제로 4-7시간이다."

| 항목 | 문서 주장 | 실제 추정 | 차이 |
|------|---------|---------|------|
| 개발 기간 | 월 2-4시간 × 6개월 | 주 4-7시간 × Phase 1-4 (실질 50-80시간) | 3-4배 |
| Year 1 비용 | 미명시 | Claude Max $200/월 × 6-12개월 = $1,200-2,400 | 미반영 |
| 월간 유지보수 | 미명시 | 실제 3-4시간/월 (API 변경, 스키마 변화, 버그) | 과소평가 |
| AlphaSquare 연비 | $840/년 | Year 1 InvestScan $1,800-3,600 | 2-4배 비쌈 |

### 방어
이 공격은 타당하지만 전제가 틀렸다. InvestScan은 **AlphaSquare의 대체재가 아니라 보완재**다. AlphaSquare가 제공하지 못하는 것(거시환경 스캐닝 + 신호 추적 + 나만의 결정 저널)을 구축하는 비용이다. 단, 비용 투명성이 PRD에서 명시적으로 빠져 있었던 것은 인정한다.

### 수용된 개선 사항

**[개선 A-1] AlphaSquare 보완재 포지셔닝 명시 (PRD Section 2 반영)**
- "AlphaSquare 경쟁자"가 아닌 "AlphaSquare 사용자를 위한 거시 컨텍스트 레이어"
- 타겟: AlphaSquare 이미 사용 중인 사용자 중 "왜 그 종목인지 맥락이 필요한 20%"
- 리포트 섹션에 "AlphaSquare 신호와의 일치/불일치" 비교 항목 추가

**[개선 A-2] 실제 시간·비용 투명하게 PRD에 기재**
```
Day 0 설치:      2-4시간 (GlobalNews 환경 포함)
M1 개발:         주 3-5시간 × 6-8주 = 약 30-40시간 총합
M1 이후 운영:    월 2-3시간 (유지보수 + 리포트 확인)
Claude Max 비용: $200/월 (MVP 운영 권장)
```

**[개선 A-3] "동전 던지기 6개월" 문제 해결**
- Month 1-2: 시스템이 안정화되는 기간. 리포트를 **수익 기반으로 즉시 판단하지 않을 것**을 명시
- Month 1-2는 "내 매크로 판단을 외재화하는 도구 구축 기간"으로 프레임
- Month 3+부터 정확도 추적 시작

---

## 25.2 공격 2: 비코더 UX 실제 마찰 (UX 현실 검증)

### 공격 요지
> "Day 0이 30-60분이 아니라 2-4시간이고, '자연어 설정 변경'은 세션 간 동기화가 깨질 수 있으며, '주 25-30분 루틴'은 에러 발생 시 주 2-5시간으로 폭증한다."

구체적 실패 시나리오:
1. Python venv 설치 중 Permission denied 에러 → 비코더는 해결 불가
2. Claude Code 새 세션에서 이전 `investscan.yaml` 경로를 잊음
3. launchd가 실패해도 4주 후에야 "리포트가 없네?"로 발견
4. Telegram 피드백 타임스탬프 미정 → "어느 주 리포트에 대한 피드백인지" 불분명

### 방어
UX 마찰 공격 대부분이 타당하다. 특히 "launchd 실패를 4주 후에 발견"과 "피드백 타임스탬프 부재"는 실제 사용성을 치명적으로 해친다. Part XIII, XXI, XXII에서 이 사항들을 과소평가했다.

### 수용된 개선 사항

**[개선 B-1] 자동화 헬스체크 대시보드 (신규 필수 기능)**
```
weekly_dashboard.html (매 실행 후 자동 생성):
├── 마지막 성공 실행: [날짜/시각] ✅
├── 이번 주 실행 상태: [진행률 30%] 🔄
├── 실패 에러 로그: [가장 최근 에러 1건, 한국어 설명]
└── 섹터별 데이터 완전성: 반도체 ✅ / IT ⚠️ (부분) / 바이오 ❌
```
→ ~50 LOC 추가. M1 필수 포함.

**[개선 B-2] 파이프라인 데드라인 알림**
```python
# launchd 일요일 20:00 시작 → 월요일 08:00 deadline
if not pipeline_completed_by(monday_08_00):
    telegram_send("⚠️ 이번 주 리포트가 아직 생성 중입니다.\n에러: [한국어 설명]\n다음 단계: [1가지 행동 지침]")
```
→ "4주 후 발견" 문제 완전 해결. ~30 LOC.

**[개선 B-3] 피드백 자동 타임스탬프 연결**
```
사용자: Telegram에서 "반도체 맞았어요" 전송
시스템: "가장 최근 리포트(W3, 3/24) 기준으로 기록할까요?"
        → 사용자 확인 또는 5분 내 무응답 시 자동 W3로 기록
```
→ 피드백 루프 혼선 해결. Part XXII 경로 A 신뢰도 향상.

**[개선 B-4] 설정 이력 자동 저장 (1줄 추가)**
```yaml
# investscan.yaml에 자동 추가
_config_history:
  - "2026-03-28: investment_style=conservative (초기값)"
  - "2026-04-05: investment_style=aggressive (사용자 변경)"
```
→ "이전 설정으로 돌아가줘" 자연어 명령 구현 가능. ~20 LOC.

**[개선 B-5] 에러 메시지 한국어화 필수 요구사항**
- 모든 에러 알림은 **영어 기술 메시지 없이** 한국어 설명 + 행동 지침만 표시
- 예: `"KeyError: 'preliminary_category'"` → `"신호 분류 정보를 읽지 못했습니다. EnvironmentScan을 다시 실행해주세요."`

---

## 25.3 공격 3: 기술 취약점 (기술 현실주의자)

### 공격 요지
> "File-based IPC는 스키마 변경 시 무음 실패하고, STEEPs→GICS 매핑 70-80% 오류가 종목 추천에 연쇄 오류를 낸다. GlobalNews Parquet을 한 번도 실행해본 적 없으므로 4시간 파이프라인 시간 추정은 근거 없다."

핵심 취약점:
1. **스키마 시한폭탄**: EnvironmentScan 업데이트 → `preliminary_category` 18번째 변이 생성 → normalizers.py 무음 UNKNOWN 처리
2. **STEEPs→GICS 정밀도 부족**: "T" 신호가 의료AI인지 반도체AI인지 키워드만으로 구분 불가
3. **database.json 파일 누적**: 1년 후 509×52 = 26,500 신호 → 50MB JSON → 성능 저하
4. **normalizers.py 과소평가**: 10시간 추정 → 실제 40시간 (엣지케이스 × 15)

### 방어
기술 취약점 공격 중 **스키마 시한폭탄**과 **파일 크기 누적** 문제는 설계에서 누락되었다. 나머지는 이미 설계에 반영되어 있지만 PRD에서 명시적으로 언급되지 않아 "없는 것처럼" 보였다.

### 수용된 개선 사항

**[개선 C-1] 스키마 버전 관리 (신규 필수 요구사항)**
```python
# normalizers.py에 추가
SUPPORTED_SCHEMA_VERSIONS = {
    "envscan-wf1-v1": {"required_fields": {"id", "title", "source", "preliminary_category"}},
    "envscan-wf4-v1": {"required_fields": {"id", "steeps", "psst_score"}},
    "gnews-signals-v1": {"required_cols": {"signal_id", "signal_layer", "confidence"}},
}

def detect_schema_version(data) -> str:
    """알려진 버전만 처리. 미알려진 변이 발견 시 명시적 에러 + Telegram 알림"""
    ...
    raise UnknownSchemaVersion(f"새로운 스키마 변이 발견: {field_keys}")
    # 자동 처리 절대 금지 — PRD 원칙
```
→ 무음 오류 완전 차단. ~40 LOC.

**[개선 C-2] 파일 크기 모니터링 + 자동 아카이브**
```python
# orchestrator.py에 추가 (M1)
MAX_SIGNALS_FILE_SIZE_MB = 10
if database_json_size_mb > MAX_SIGNALS_FILE_SIZE_MB:
    archive_old_signals(keep_weeks=4)  # 최근 4주만 유지
    telegram_send("📦 오래된 신호 데이터를 아카이브했습니다.")
```
→ 1년 후 50MB → 항상 4주치 ~4MB 유지. ~30 LOC.

**[개선 C-3] STEEPs→GICS 매핑에 신뢰도 점수 추가**
```python
# signal_bridge.py 반환값 변경
@dataclass
class SectorMapping:
    gics_sector: str           # "Information Technology"
    confidence: float          # 0.0-1.0
    korean_sector: str         # "반도체/전자"
    reasoning: str             # "T신호 + 'semiconductor' 키워드"

# confidence < 0.7이면 리포트에 ⚠️ 표시 + 여러 가능성 제시
```
→ 오분류 투명화. 사용자가 낮은 신뢰도 추천을 구분 가능. ~50 LOC.

**[개선 C-4] normalizers.py 포맷 점진적 지원 (M1 범위 조정)**
- **M1 (Phase 1-2)**: WF1 database.json + GlobalNews signals.parquet **2개 포맷만**
- **M1 (Phase 3-4)**: WF4 priority-ranked 추가 (3번째 포맷)
- **M2**: 나머지 3개 포맷 추가
- → 10시간 → 실질 15-20시간 (2개 포맷 안정화 후 확장)

**[개선 C-5] 파이프라인 최초 실행 시간 현실화**
```
GlobalNews 첫 실행 (모델 다운로드 포함):
- SBERT 모델 다운로드: ~15분 (2.2GB)
- 첫 NLP 분석 실행: ~60-90분 (추정, 실제 검증 필요)
- 총 Day 0: 3-5시간 (기존 5-6시간 추정과 일치)

Month 2+: 모델 캐시 후 ~45-60분/주 (기존 추정 유지)
```

---

## 25.4 공격 4: 투자 논리 결함 (투자 논리 비판자)

### 공격 요지
> "감성 분석이 90-95% 허위 상관관계임을 인정하면서 감성 데이터를 사용하는 것은 모순이다. Brier Score 0.22는 '훈련받지 않은 예측자' 수준이고, '워치리스트'는 실제 행동 지침이 없다. 한국 시장의 핵심 드라이버(외국인 수급, 원화 환율, 정책 변화)를 글로벌 뉴스 스캐닝으로는 잡을 수 없다."

핵심 공격 포인트:
1. **감성 역설**: 90-95% 허위를 인정하면서 GlobalNews 48K LOC 감성 파이프라인 유지
2. **Brier Score 0.22 무의미**: 66개 예측에서 55% hit rate는 통계적 유의성 없음 (p95 기준 60.6% 필요)
3. **워치리스트 → 행동 공백**: "SK하이닉스 WATCH, 비중 +2~5%"는 진입점/청산점/타이밍이 없어 실제 행동 불가
4. **한국 시장 미스매치**: TSMC 강세 신호 = 삼성전자 약세 (경쟁 관계). 글로벌 반도체 Bullish ≠ 한국 반도체 Bullish

### 방어

**감성 역설에 대한 방어**: 타당하다. 다만 GlobalNews의 가치는 감성이 아닌 **토픽 트렌드와 이벤트 추출**에 있다. "Fed 금리 인상 신호"는 감성이 아닌 사실 기반 이벤트다. 설계 문서에서 "감성은 secondary"라고 했지만 이를 더 명확히 할 필요가 있다.

**Brier Score 방어**: 0.22 목표는 "투자 수익" 기준이 아니라 "예측 능력" 기준이다. 하지만 사용자(비코더 목사)에게 Brier Score는 무의미한 지표임을 인정한다. 더 직관적인 검증 지표가 필요하다.

**워치리스트 방어**: 법적 이유로 "행동 지침"을 직접 제공할 수 없다. 하지만 "틀 제시"는 가능하다. "SK하이닉스 WATCH + 현재 52주 신고가 기준 -15% 구간"처럼 참고 정보를 추가할 수 있다.

**한국 시장 미스매치**: 이것이 가장 심각한 공격이다. **글로벌 신호의 한국 시장 전이 효과가 비선형적**이라는 것은 맞다. 특히 TSMC-삼성전자 경쟁 관계처럼 글로벌 강세 = 한국 약세인 케이스를 현재 설계로는 구분할 수 없다.

### 수용된 개선 사항

**[개선 D-1] 감성 분석 가중치 0%로 명시적 제외 (설계 원칙 변경)**

현재: GlobalNews 감성 출력 → InvestScan 통합 신호
변경: GlobalNews에서 InvestScan으로 가져오는 신호 = **사실 기반 이벤트 + 토픽 트렌드만**

```python
# synthesize.py 통합 신호 원칙 (PRD 명시 필요)
SIGNAL_WEIGHT_POLICY = {
    "steeps_event": 0.70,      # STEEPs 사실 기반 이벤트 (최우선)
    "topic_trend": 0.20,       # 뉴스 토픽 빈도 트렌드
    "sentiment": 0.00,         # 감성 분석 완전 제외 (90-95% 허위 상관)
    "factor_score": 0.10,      # 팩터 스코어 (pykrx 기반)
}
```
→ 설계 일관성 확보. 기존 LOC 감소 효과(GlobalNews 감성 파이프라인 미사용).

**[개선 D-2] 검증 지표: Brier Score → "섹터 방향 적중률 + 주관적 유용성"**

| 기존 지표 | 문제점 | 개선 지표 |
|---------|------|---------|
| Brier Score ≤ 0.22 (Month 6) | 비코더에게 무의미, 투자 수익과 무관 | **섹터 방향 적중률 ≥ 55% (Month 4)** |
| 통계적 유의성 66개 필요 | Month 2에는 22개로 불가 | **"이번 주 리포트가 내 판단에 도움이 됐나?" 0-5점 주관 평가** |
| 수익률과 직결 없음 | 맞췄어도 돈 못 벌 수 있음 | **Month 6: Kill Switch = 주관 평점 < 3.0 (3회 연속)** |

→ Kill Switch 기준을 정량(Brier Score)에서 **정성+정량 혼합**으로 변경.

**[개선 D-3] 워치리스트 → 실행 참고 체크리스트 (법적 안전 유지)**
```
[SK하이닉스 000660 — 관찰 대상]
근거 신호:
  • STEEPs-T: AI 반도체 수요 증가 신호 3건 (신뢰도 0.82)
  • STEEPs-P: 한미 반도체 협력 강화 신호 (신뢰도 0.75)

참고 정보: (투자 조언 아님)
  • 섹터 방향: 기술 섹터 Bullish (합성 점수 0.71/1.0)
  • 4주 방향 신뢰도: 65%
  • 본인 포트폴리오 내 비중 확인 권장

⚠️ 위 정보는 매크로 신호 기반 참고 자료입니다.
   실제 투자 결정은 본인 판단으로 하세요.
```
→ 법적 안전 유지하면서 행동 맥락 제공. ~30 LOC 추가.

**[개선 D-4] 한국 독립 신호 영역 추가 (신규 모듈: korea_signal_layer.py)**

이것이 R9 성찰의 가장 중요한 신규 발견이다.

```python
# korea_signal_layer.py (~150 LOC) — M1 포함 필수
"""
한국 시장은 글로벌 신호에 비선형 응답한다.
다음 3가지 한국 독립 신호를 별도 레이어로 추적.
"""

class KoreaSignalLayer:
    def get_policy_signals(self) -> list[Signal]:
        """대한민국 정부 정책 신호 (기재부/금융위 보도자료 RSS)"""
        # 세금, 공매도, 규제 변화 — 글로벌 뉴스보다 선행

    def get_currency_signal(self) -> Signal:
        """원화/달러 강약 신호 (pykrx or FDR에서 USD/KRW)"""
        # 원화 약세 → 수출 섹터 유리 / 원화 강세 → 내수 섹터 유리

    def get_foreign_flow_proxy(self) -> Signal:
        """외국인 수급 프록시 (FDR에서 KOSPI 외국인 순매수 일간)"""
        # 외국인 연속 순매도 3일+ → Bearish 신호
```

**한국 시장 비선형 매핑 규칙 (signal_bridge.py 추가):**
```python
KOREA_NONLINEAR_RULES = {
    # 글로벌 Bullish이지만 한국은 반대 케이스
    "TSMC_강세 + 삼성전자_경쟁": "BEARISH_override(삼성전자)",
    "달러강세 + 수출섹터": "BULLISH_override(반도체, 자동차)",
    "Fed금리인하 + 원화강세": "주의(수출섹터 약화 가능성)",
}
```
→ 한국 시장 특수성 반영. 기존 설계의 가장 큰 blind spot 해소. ~150 LOC.

---

## 25.5 공격을 통해 발견된 신규 설계 원칙 5가지

> 4개 적대적 에이전트의 공격을 방어하면서 발견한 **PRD.md에 반드시 포함해야 할 새로운 설계 원칙**

### 원칙 N-1: 감성 제로 (Sentiment-Zero) 원칙
> GlobalNews에서 가져오는 신호는 **사실 기반 이벤트와 토픽 트렌드만**. 감성 점수는 절대 InvestScan의 합성 계산에 포함하지 않는다.
>
> 근거: 감성-수익 상관관계 교란변수 제거 후 실효 상관 0.034-0.048 (90-95% 허위, arXiv:2603.21473)

### 원칙 N-2: 한국 독립 레이어 원칙
> 글로벌 신호와 한국 독립 신호(정책·환율·외국인수급)는 **별도 레이어**로 처리한다. 글로벌 Bullish가 한국 시장에서는 Bearish일 수 있다. 두 레이어가 충돌할 때는 한국 독립 신호가 우선한다.
>
> 근거: TSMC 강세 = 삼성전자 점유율 잠식 가능성. 달러 강세 = 한국 수출 우호적.

### 원칙 N-3: 스키마 버전 명시 원칙
> 상류 시스템(EnvScan, GlobalNews)에서 파일을 읽을 때 **첫 번째 작업은 스키마 버전 확인**이다. 알려진 버전만 처리하고, 미알려진 변이는 즉시 Telegram 알림 + 파이프라인 중단.
>
> 근거: 자동 감지(auto-detection)는 스키마 변화를 무음으로 통과시켜 다운스트림 오류를 유발한다.

### 원칙 N-4: 자동화 투명성 원칙
> 시스템은 매 실행 후 결과를 사용자에게 **한국어**로 보고한다. 성공, 부분성공, 실패 모두 Telegram으로 알린다. 사용자가 "잘 돌고 있겠지"라고 가정하게 두지 않는다.
>
> 근거: launchd 실패를 4주 후에 발견하는 시나리오는 사용자 신뢰를 파괴한다.

### 원칙 N-5: 행동 맥락 제공 원칙
> 워치리스트는 종목 이름과 신호 등급만 제공하지 않는다. 반드시 **신호 근거 체인(어떤 매크로 신호가 이 종목을 지목했는지) + 섹터 방향 신뢰도**를 함께 제공한다. "왜 이 종목인지"를 설명해야 사용자가 자신의 판단으로 결정할 수 있다.

---

## 25.6 R9 성찰 결과: PRD.md 반영 확정 사항

### 신규 추가 (PRD.md에 없던 것)

| 항목 | LOC | PRD 섹션 |
|------|-----|---------|
| `korea_signal_layer.py` (정책·환율·외국인수급) | ~150 | Section 5 (Product Requirements) |
| `weekly_dashboard.html` 자동 생성 | ~50 | Section 8 (Implementation Architecture) |
| 파이프라인 데드라인 알림 (월요일 08:00) | ~30 | Section 8 |
| 피드백 타임스탬프 자동 연결 | ~30 | Section 14 (Post-Report Workflow) |
| 스키마 버전 감지 모듈 | ~40 | Section 6 (Data Schema) |
| 파일 크기 모니터링 + 자동 아카이브 | ~30 | Section 8 |
| 설정 이력 자동 저장 (`_config_history`) | ~20 | Section 13 (Personalization) |
| 에러 메시지 한국어화 (모든 모듈 적용) | ~30 | Section 5 |
| STEEPs→GICS 신뢰도 점수 추가 | ~50 | Section 6 |
| **소계** | **~430 LOC** | |

### 수정 (기존 설계 변경)

| 항목 | 변경 전 | 변경 후 |
|------|--------|--------|
| 감성 신호 가중치 | 미명시 (암묵적 포함) | **0%** (명시적 제외, N-1 원칙) |
| 검증 지표 | Brier Score ≤ 0.22 | 섹터 방향 적중률 ≥ 55% + 주관 평점 병행 |
| Kill Switch 기준 Month 2 | BS ≤ 0.30 (표본 22개) | 주관 평점 < 3.0 (3회 연속) OR 적중률 < 40% |
| 워치리스트 형식 | 종목명 + 등급만 | 근거 체인 + 신뢰도 + 참고 정보 추가 |
| Day 0 시간 | 30-60분 | **2-4시간** (현실화) |
| AlphaSquare 관계 | 경쟁자 | **보완재** (AlphaSquare 사용자를 위한 맥락 레이어) |
| normalizers.py 포맷 지원 | M1에 6가지 | **M1: 2가지** (WF1 + GlobalNews), M1.5: 3번째 |

### M1 MVP LOC 재계산 (R9 반영 후)

| 모듈 | 기존 LOC | R9 조정 LOC | 비고 |
|------|---------|-----------|------|
| config.py | ~100 | ~100 | 동일 |
| normalizers.py (2개 포맷) | ~300 | **~200** | M1 포맷 2개로 축소 |
| dedup.py | ~150 | ~150 | 동일 |
| steeps_classifier.py | ~200 | ~200 | 동일 |
| signal_bridge.py (한국 비선형 규칙 포함) | ~200 | **~280** | 한국 규칙 +80 LOC |
| **korea_signal_layer.py** | 없음 | **+150** | 신규 |
| synthesize.py (감성 제거) | ~200 | **~180** | 감성 가중치 코드 제거 |
| report_generator.py (근거 체인 포함) | ~200 | **~250** | 워치리스트 형식 개선 |
| weekly_orchestrator.py | ~150 | ~150 | 동일 |
| telegram_notifier.py (헬스체크 포함) | ~100 | **~150** | 데드라인 알림 추가 |
| personalizer.py | ~200 | **~220** | 설정 이력 추가 |
| accuracy_tracker.py (지표 변경) | ~150 | **~130** | Brier Score 제거 |
| **소계** | ~1,950 | **~2,160** | 신규 기능 +~430, 최적화 -~220 |
| **버퍼 20%** | | **~2,600** | |

---

## 25.7 R9 성찰 핵심 요약

> **적대적 성찰의 핵심 발견**: 4개 공격 중 가장 타당하고 치명적인 것은 **공격 4 (투자 논리)**였다. 특히:
>
> 1. **한국 독립 신호 부재**: 글로벌 신호의 한국 시장 비선형 전이 효과를 설계에서 완전히 무시했다. `korea_signal_layer.py`는 선택 사항이 아니라 **M1 필수**다.
>
> 2. **감성 역설**: 90-95% 허위를 인정하면서 감성 데이터를 암묵적으로 포함한 것은 설계 불일관성이다. Sentiment-Zero 원칙을 PRD에 명시해야 한다.
>
> 3. **자동화 투명성 부재**: "잘 돌고 있겠지" 가정은 비코더 사용자에게 가장 위험하다. 헬스체크 대시보드와 데드라인 알림은 M1 필수다.

**방어를 통해 강화된 확신:**
- File-based IPC는 여전히 올바른 선택 (단, 스키마 버전 관리 추가로 취약점 보완)
- 로컬 실행은 여전히 올바른 선택 (단, 설정 이력 + 헬스체크로 유지보수성 강화)
- AlphaSquare 보완재 포지셔닝이 더 정직하고 지속가능하다

---

*R9 (2026-03-28): Part XXV 추가 — 4개 적대적 에이전트 공격·방어·개선안 통합. 신규 설계 원칙 5가지 확정 (감성제로·한국독립레이어·스키마버전·자동화투명성·행동맥락). 신규 모듈 korea_signal_layer.py (+150 LOC) M1 필수 추가. M1 LOC 재계산 ~2,100 → ~2,600 (버퍼 포함). 검증 지표 Brier Score → 섹터 적중률+주관평점으로 변경. AlphaSquare 포지셔닝 "경쟁자"→"보완재"로 확정.*

---

# Part XXVI: 최종 성찰 — 6가지 필살기 (R10)

> **성찰 방법**: 순수 내면 성찰. 6가지 독창적 기법 적용.
> **목적**: 모든 이전 성찰(R1-R9)을 꿰뚫는 **하나의 진실**을 찾는다.

---

## 26.1 필살기 1 — One-Sentence Test (한 문장 진실 테스트)

> **기법**: PRD 전체를 한 문장으로 압축한다. 압축이 안 되면 핵심이 없는 것이다.

### 시스템 관점 한 문장
> "InvestScan은 EnvironmentScan + GlobalNews를 통합하여 STEEPs 신호를 정규화하고 한국 시장 섹터 방향성과 종목 관찰 워치리스트를 주간 Markdown 리포트로 자동 생성하는 로컬 Python 시스템이다."

→ 기술적으로 정확하다. **하지만 사용자(목사님)에게 의미 없다.**

### 사용자 관점 한 문장
> "목사님이 매주 월요일 아침, 커피 한 잔을 들고 Telegram을 열면 '이번 주 반도체 긍정, IT 중립, SK하이닉스 주목' 한 줄이 와 있고, 5분 안에 이번 주 투자 방향을 결정할 수 있다."

→ **이것이 진짜 PRD의 한 문장이다.**

### 성찰 결론

3,194줄짜리 문서 전체가 이 **한 문장**을 뒷받침하는가?

검증 결과:
- Part V (이론적 배경 ~400줄): ❌ 이 한 문장에 기여하지 않음
- Part IX (교차 라운드 긴장): ❌ 기여 없음
- Part X (미해결 질문): ❌ 기여 없음
- Part XII.4 (팩터 학술 배경): ❌ 기여 없음
- **Part XVII 실제 경로**: ✅ 직접 기여
- **Part XIX 스키마 검증**: ✅ 직접 기여
- **Part XXV D-4 한국 독립 신호**: ✅ 핵심 기여

> **PRD.md 작성 황금 원칙 #1**: 모든 섹션에 "이것이 없으면 목사님이 월요일 Telegram 메시지를 받을 수 없는가?"를 적용한다. 아니오이면 제거한다.

---

## 26.2 필살기 2 — 침묵 지도 (Silence Map)

> **기법**: 문서가 말하는 것이 아니라 **말하지 않는 것**을 찾는다. 문서가 가장 조용해지는 곳이 가장 위험한 맹점이다.

### 침묵 1: "첫 리포트를 받았을 때 목사님은 실제로 무엇을 하는가?"

문서는 리포트 구조(3층 Progressive Disclosure), 섹터 방향, 워치리스트를 상세히 설명한다. 하지만 **"리포트를 읽고 나서 다음 5분 동안 목사님이 무슨 행동을 하는가?"** 에 대해 문서는 조용하다.

→ 이것은 **전체 시스템의 존재 이유**인데 명시되지 않았다.

**PRD에 추가 필요**: "리포트 → 행동 전환 흐름" (5분 행동 프로토콜)
```
1. Telegram 핵심 요약 읽기 (30초)
2. 상향된 섹터 1개 클릭 → 상세 리포트 확인 (2분)
3. "이번 주 행동 체크리스트" 확인 (1분)
4. 내 포트폴리오와 대조하여 1가지 결정 (1분)
5. 결정 근거 Telegram 답장 (30초)
```

### 침묵 2: "시스템이 완전히 틀렸을 때 어떻게 말하는가?"

문서는 "Graceful Degradation"을 말한다. 하지만 **"이번 주 예측이 완전히 틀렸습니다. 왜 틀렸는지 분석합니다."** 라는 자기 성찰 메시지를 시스템이 생성하는지에 대해 문서는 조용하다.

→ 이것이 신뢰 구축의 핵심인데 없다.

**PRD에 추가 필요**: "정확도 피드백 메시지" 설계
```
월간 리포트 마지막 섹션:
"지난달 예측 검토:
 • 반도체 Bullish → 실제 +3.2% ✅ (맞음)
 • IT Bearish → 실제 +0.8% ❌ (틀림 — IT 섹터 상향 요인 과소평가)
 • 이번 달 신뢰도 조정: IT 신호 가중치 -5%"
```

### 침묵 3: "EnvironmentScan은 정확히 언제, 누가 실행하는가?"

문서는 "2-세션 방식"을 말하지만, **"목사님이 일요일 저녁에 EnvironmentScan을 실행하는 정확한 절차 5단계"** 가 없다. 비코더가 "이걸 어떻게 실행하지?"라고 물을 때 답이 없다.

→ InvestScan의 입력 데이터가 어떻게 만들어지는지 PRD에서 명시 필요.

### 침묵 4: "3개월 후 시스템이 구식이 되면?"

EnvironmentScan이 업데이트되거나, GlobalNews 사이트가 바뀌거나, Claude API 가격이 바뀔 때 **어떻게 시스템을 유지하는가?** 에 대해 문서는 조용하다.

→ "연간 유지보수 체크리스트" (Claude Code와 함께 연 1회 점검)를 PRD에 포함해야 한다.

### 침묵 5: "처음 리포트가 나왔을 때 '이게 맞는지' 어떻게 아는가?"

Week 6, 첫 리포트 수신. "반도체 Bullish" 라고 나왔다. 목사님이 "이게 맞나?"라고 생각할 때 **무엇을 보고 검증하는가?** 에 대해 문서는 조용하다. Brier Score? 히트율? 아니면 그냥 직관?

→ "신호 자가 검증 가이드" — 첫 리포트를 받은 사용자가 스스로 신호를 점검하는 2분 가이드가 PRD에 필요하다.

> **PRD.md 황금 원칙 #2**: PRD는 침묵 지도의 5가지 빈칸을 모두 채워야 한다. 특히 "리포트 → 5분 행동"과 "처음 검증하는 법"은 PRD 전면에 배치한다.

---

## 26.3 필살기 3 — 내부 모순 사냥 (Contradiction Hunt)

> **기법**: 같은 문서 안에서 서로 충돌하는 주장 3가지를 찾는다. 모순은 설계 미성숙의 표시다.

### 모순 1: LOC 추정의 3중 충돌

| 위치 | LOC 추정 | 범위 |
|------|---------|------|
| Part XXIII.2 (R7) | ~3,870 LOC (버퍼 포함 ~5,150) | 전체 시스템 |
| Part XXIV (R8) | ~2,100 LOC | M1 MVP만 |
| Part XXV.6 (R9) | ~2,600 LOC (버퍼 20% 포함) | M1 MVP |

→ Claude Code가 workflow.md를 읽을 때 어떤 숫자를 믿어야 하는가?

**해결**: PRD.md에서 단 하나의 LOC 추정만 사용한다.
> **확정**: M1 MVP = **~2,200 LOC** (버퍼 15% 포함). 전체 로드맵(M1-M3) = ~4,000 LOC. 두 숫자를 명확히 분리.

### 모순 2: Kill Switch 기준의 2중 충돌

| 위치 | Kill Switch 기준 |
|------|----------------|
| Part XI.3, Part XV (R6) | Month 2: Brier Score ≤ 0.30 |
| Part XXV.6 (R9) | 주관 평점 < 3.0 (3회 연속) OR 적중률 < 40% |

→ 어느 기준으로 Month 2에 중단을 결정하는가?

**해결**:
```
Kill Switch 기준 (확정, PRD Section 10):
Month 2 체크포인트:
  - 정량: 섹터 방향 적중률 < 40% (누적 10회 이상)
  - 정성: "이 리포트가 내 판단에 도움이 됐나?" 평균 < 2.5/5 (4주 연속)
  - 기술: 파이프라인 완전 실패 3회 연속
  → 3가지 중 1가지 충족 시 중단 검토
```

### 모순 3: AlphaSquare 관계 정의의 충돌

| 위치 | 정의 |
|------|------|
| Part I.2 (R1-R7) | "카테고리 창조자 — AlphaSquare 경쟁자가 아님" |
| Part II.1-4 (R1-R7) | AlphaSquare 상세 분석, 경쟁 비교 40줄 |
| Part XXV.1 (R9) | "보완재 — AlphaSquare 사용자를 위한 맥락 레이어" |

→ 경쟁자도 아니고, 카테고리 창조자도 아니고, 보완재?

**해결**: 하나의 명확한 포지셔닝으로 수렴.
> **확정 포지셔닝**: "AlphaSquare 사용자를 위한 '왜 그 종목인가?' 맥락 제공 레이어."
> AlphaSquare는 **무엇을(What)** 사야 하는지 말한다. InvestScan은 **왜(Why) 그 섹터가 지금 움직이는지** 말한다. 두 도구는 협력한다.

> **PRD.md 황금 원칙 #3**: PRD에는 LOC 추정 1개, Kill Switch 기준 1세트, AlphaSquare 관계 정의 1개만 존재한다. 중복·충돌 제거.

---

## 26.4 필살기 4 — 역전 사고 (Inversion: 실패 시나리오)

> **기법**: "어떻게 성공하는가?"가 아니라 "어떻게 실패하는가?"를 먼저 생각한다. 실패 경로를 막으면 성공이 남는다.

### 실패 시나리오 A: "만들었지만 안 쓴다"

**시나리오**: Claude Code가 성공적으로 M1을 구현. Week 6, 첫 리포트 생성. 목사님이 읽는다. "흥미롭네."라고 생각한다. 다음 주에 바빠서 리포트를 안 본다. 2주 후 Telegram 메시지를 스크롤해서 넘긴다. 4주 후 시스템은 돌고 있지만 아무도 안 읽는다.

**근본 원인**: 리포트가 "결정과 연결되지 않는다." 읽어도 행동이 달라지지 않는다.

**PRD 대응**: 리포트 맨 위에 반드시 "이번 주 행동 체크리스트 1가지"를 배치한다. (이미 Part XXII에 있지만 **리포트 Section 0으로 확정 명시**)

### 실패 시나리오 B: "4주 후 무음 실패"

**시나리오**: launchd가 macOS 업데이트 후 조용히 실패한다. 시스템은 매주 실행하려 하지만 파이프라인이 에러로 중단된다. Telegram 메시지가 오지 않는다. 목사님은 "바빠서 못 봤나?"라고 생각한다. 4주 후 "리포트가 왜 없지?"라고 발견한다.

**근본 원인**: 시스템 상태를 사용자가 모른다.

**PRD 대응**: [개선 B-2] 월요일 08:00 데드라인 알림은 **M1 필수**다. 리포트가 없을 때도 알림이 와야 한다: "이번 주 리포트 생성에 실패했습니다. [원인 1줄] [해결 방법 1가지]"

### 실패 시나리오 C: "6개월 후 신뢰 붕괴"

**시나리오**: 시스템이 잘 돌아간다. 목사님이 매주 읽는다. 3개월 후 반도체 Bullish 신호 4주 연속. 하지만 KOSPI 반도체 지수는 3주 연속 하락. 목사님: "이 시스템 맞는 거야?" Kill Switch 체크 — 아직 Month 2도 안 됐다. 포기?

**근본 원인**: 단기 편차(4주 하락)와 구조적 추세(3개월 방향)를 구분하지 못한다.

**PRD 대응**: 리포트에 **타임프레임 명시** 필수. "이 신호는 4-12주 방향성입니다. 2-4주 단기 변동과 다를 수 있습니다." → 사용자 기대치 교정. ~10 LOC 추가.

> **PRD.md 황금 원칙 #4**: PRD는 3가지 실패 시나리오를 명시하고, 각각의 예방 메커니즘을 Implementation Architecture에 포함한다.

---

## 26.5 필살기 5 — 월요일 아침 시뮬레이션 (Monday Morning Test)

> **기법**: 가장 구체적인 시뮬레이션. M1 구현 완료 후 첫 번째 월요일 아침을 분 단위로 상상한다.

**배경**: 2026년 5월 18일(월) 오전 10:45. 주일 예배를 마친 목사님이 서재에서 커피를 마시며 Telegram을 연다.

---

**10:45** — Telegram 알림:

```
📊 InvestScan 주간 리포트 (5/18)
신뢰도: 78% | 데이터: EnvScan✅ GlobalNews✅

이번 주 행동 1가지:
→ 반도체 ETF 비중 점검 (현재 비중 vs 권장 8-10%)

방향 요약:
• 반도체: 🟢 긍정 (72%)
• IT서비스: ⚪ 중립 (58%)
• 바이오: 🔴 주의 (34%)

상세 보고서: [링크]
```

**10:46** — 목사님 반응:
- "반도체 ETF 비중 점검이라고? 내 포트폴리오에 TIGER 반도체 ETF 5% 있는데..."
- 링크를 클릭한다.

**10:48** — 상세 리포트 열람:
```
[반도체 섹터 긍정 근거]
신호 3건:
1. TSMC 2분기 가이던스 상향 (글로벌 반도체 수요 회복)
2. 산업부: 반도체 장비 보조금 확대 발표
3. 외국인 수급: KOSPI 반도체 3일 연속 순매수

주의: 신호 2번은 한국 정책 신호 (높은 신뢰도 85%)
      신호 1번은 글로벌 → 한국 전이 예상 (4-8주 지연 가능성)

참고 종목:
• SK하이닉스 (000660) — 관찰 대상
  근거: 신호 1, 3 직접 관련 | 신뢰도: 68%
```

**10:50** — 목사님 결정:
- "TIGER 반도체 5% → 7%로 올려볼까? 아니면 일단 지켜볼까?"
- Telegram 답장: "반도체 ETF 2% 추가 매수 결정. 신호 1, 3 참고."

**10:51** — 시스템 피드백 저장:
```
[자동 저장]
W7 리포트 → 사용자 결정: "반도체 ETF 2% 추가 매수"
4주 후 정확도 추적 예약
```

**총 소요 시간: 6분**

---

### 시뮬레이션이 드러낸 PRD 수정 사항

1. **Telegram 메시지 형식이 PRD에 명세되어야 한다** (현재 없음)
   - 신뢰도 % 표시 방식
   - 이모지 신호등 (🟢⚪🔴)
   - "행동 1가지" 최상단 배치

2. **"신호 지연 가능성" 표시가 리포트에 있어야 한다** (현재 없음)
   - "글로벌 신호는 4-8주 한국 전이 지연이 있을 수 있습니다"
   - 타임프레임 투명화

3. **사용자 결정 자연어 → 구조화 저장 흐름이 PRD에 명세되어야 한다**
   - Telegram 답장 → 자동 파싱 → predictions.json 저장
   - 이 흐름이 Part XXII에 있지만 Telegram 메시지 예시가 없음

> **PRD.md 황금 원칙 #5**: PRD에는 "첫 번째 월요일 아침 6분 시뮬레이션"을 User Journey 섹션에 포함한다. 이것이 모든 기술 명세보다 더 강력한 요구사항 정의다.

---

## 26.6 필살기 6 — 최소 탈출 속도 (Minimum Escape Velocity)

> **기법**: "이 시스템이 주간 루틴으로 정착하는 가장 작은 버전은 무엇인가?" 복잡한 시스템은 처음엔 아무도 쓰지 않는다. 사용자가 매주 반드시 쓰게 되는 최소 버전을 찾는다.

### 현재 M1 설계의 문제

M1 MVP에도 다음이 필요하다:
- GlobalNews 환경 설치 (2-4시간)
- EnvScan 2-세션 실행 (별도 세션)
- 4시간 파이프라인 (일요일 밤)
- normalizers.py 2포맷 지원
- korea_signal_layer.py

이것이 **진짜 탈출 속도인가?** 아니다. 너무 무겁다.

### 최소 탈출 속도 버전: "M0.5"

```python
# 이것만으로 '매주 쓰게 되는' 버전 가능

# 입력: EnvironmentScan database.json (이미 존재)
# 처리: STEEPs 신호 집계 → 섹터 방향 합성 (normalizers.py WF1만)
# 출력: Telegram 메시지 5줄

"""
이 버전의 LOC: ~400 LOC
구현 시간: 1-2주 (Claude Code)
파이프라인 시간: 10-15분
결과: 매주 Telegram 메시지 → 즉시 가치 제공
"""
```

**M0.5가 먼저 필요한 이유**:
1. 사용자가 **즉시 가치를 경험**한다 (Week 2에 첫 Telegram 메시지)
2. GlobalNews 없이도 EnvScan만으로 작동 (이미 운영 중인 자산 활용)
3. "이게 실제로 내 투자에 도움이 되는가?"를 **Month 2 이전에 검증**
4. 이후 GlobalNews, korea_signal_layer 를 추가하면서 점진적 확장

### M0.5 → M1 → M2 점진적 확장

```
M0.5 (Week 1-2, ~400 LOC):
  • EnvScan database.json → STEEPs 집계 → 섹터 방향 → Telegram
  • "이게 유용한가?" 검증

M1 (Week 3-8, ~2,200 LOC):
  • GlobalNews 통합 추가
  • korea_signal_layer 추가
  • 종목 워치리스트 추가
  • 상세 리포트 + 행동 체크리스트

M2 (Month 3-4, +~800 LOC):
  • 정확도 추적 자동화
  • 개인화 P2 기능
  • 피드백 경로 B (관심 섹터 학습)
```

> **핵심 통찰**: 현재 PRD는 M0.5를 건너뛰고 바로 M1을 구현하려 한다. 이것이 "만들었지만 안 쓴다"(실패 시나리오 A)의 근본 원인이다. M0.5가 "탈출 속도"다.

> **PRD.md 황금 원칙 #6**: PRD의 첫 번째 구현 단계는 **M0.5 (~400 LOC, 1-2주)**이다. "Week 2에 첫 Telegram 메시지를 받는다"가 Phase 1의 Done Gate다.

---

## 26.7 최종 종합: PRD.md 황금 원칙 6가지

> R1-R10, 모든 성찰을 거친 후 도달한 **PRD.md 작성의 6가지 불변 원칙**

| 번호 | 황금 원칙 | 근거 |
|------|---------|------|
| **#1** | 모든 섹션에 "목사님 Telegram 메시지 수신에 기여하는가?" 필터 적용 | 26.1 One-Sentence Test |
| **#2** | 침묵 지도의 5가지 빈칸 채우기: 리포트→행동 5분, 첫 검증법, EnvScan 실행 절차, 유지보수 체크리스트, 시스템 틀렸을 때 메시지 | 26.2 침묵 지도 |
| **#3** | LOC 1개, Kill Switch 1세트, AlphaSquare 관계 1개만. 중복·충돌 제거 | 26.3 내부 모순 |
| **#4** | 3가지 실패 시나리오와 예방 메커니즘을 Implementation Architecture에 명시 | 26.4 역전 사고 |
| **#5** | User Journey에 "첫 번째 월요일 아침 6분 시뮬레이션" 포함. 기술 명세보다 강력한 요구사항 정의 | 26.5 월요일 시뮬레이션 |
| **#6** | 첫 구현 단계는 **M0.5 (~400 LOC, Week 2 Telegram 메시지)**. 탈출 속도 먼저. | 26.6 최소 탈출 속도 |

---

## 26.8 PRD.md 최종 구조 확정 (R10)

> R1-R10 성찰을 모두 반영한 PRD.md의 최종 구조. 이것이 실제 PRD.md 작성 기준이다.

```
[사용자가 읽는 섹션 — 기술 용어 최소화]
Section 1: 이 시스템이 무엇인가 (한 문장 + 월요일 아침 시나리오)
Section 2: 왜 만드는가 (AlphaSquare 보완, 한국 시장 맥락)
Section 3: 어떻게 사용하는가 (Day 0 → Week 2 첫 메시지 → 주간 루틴 6분)
Section 4: 성공 기준 (Month 2 Kill Switch + Month 6 목표)
Section 5: 비용과 시간 (Day 0 2-4시간, 월 Claude Max $200, 주간 6분)

[Claude Code가 읽는 섹션 — 모호함 0]
Section 6: M0.5 구현 명세 (~400 LOC, Done Gate: Week 2 Telegram 발송)
Section 7: M1 구현 명세 (~2,200 LOC, Done Gate: 종목 워치리스트 포함 리포트)
Section 8: 데이터 스키마 계약 (UnifiedSignal + STEEPs 17변이 + 한국 독립 신호)
Section 9: 기술 아키텍처 (실제 파일 경로 + 모듈 의존성 순서)
Section 10: 구현 원칙 (감성제로, 스키마버전, 자동화투명성 등 7원칙)
Section 11: 에러 복구 + 한국어 알림 명세
Section 12: 외부 연동 (FDR, Telegram, launchd, macOS Keychain)
Section 13: 검증 프레임워크 (적중률 + 주관평점 Kill Switch)
Section 14: M2 백로그 (PRD 범위 밖, 참고용)

[두 독자 공통]
Section 15: 한국 법적 컴플라이언스 (3요건 비해당 근거 + 금지 표현)
```

---

## 26.9 R10 최종 성찰 요약

> **10라운드 성찰(R1-R10)을 통해 도달한 하나의 진실**:
>
> 이 문서는 "훌륭한 연구 자료"로서는 완성되었다. 이제 "탁월한 PRD.md"가 될 조건도 모두 밝혀졌다.
>
> **차이는 딱 하나다**: 연구 자료는 설계자의 사고 과정을 담고, PRD는 **목사님의 월요일 아침을 설계**한다.
>
> PRD.md의 첫 문장은 기술 스택이 아니라 이 장면이어야 한다:
> > "2026년 5월 18일(월) 오전 10:45. 주일 예배를 마친 목사님이 Telegram을 열었다. 메시지가 와 있다. '이번 주 반도체 긍정, 행동 1가지: ETF 비중 점검.' 6분 후 목사님은 결정을 내렸다. 시스템은 이 6분을 위해 존재한다."

---

*R10 (2026-03-28): Part XXVI 추가 — 6가지 성찰 필살기 적용 최종 성찰. One-Sentence Test(한 문장 진실), 침묵 지도(5가지 빈칸), 내부 모순 사냥(LOC·KillSwitch·AlphaSquare 3중 충돌 해소), 역전 사고(3가지 실패 시나리오), 월요일 아침 6분 시뮬레이션, 최소 탈출 속도(M0.5 ~400 LOC Week2 도입) 확정. PRD.md 황금 원칙 6가지 + 최종 15-Section 구조 확정.*

---

*R7 최종 (2026-03-28): Part XVII-XXIII 추가. 총 2,162줄 → 현재 버전. 연구 소스: upstream-bootstrap-analysis.md, schema-verification-actual.md, analysis-monolithic-architecture.md, investscan-weekly-operation-e2e-cost-analysis.md, non-coder-personalization-mechanisms.md, post-report-decision-workflow.md (총 6개 파일 통합).*
