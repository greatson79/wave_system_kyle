# InvestScan PRD 사전 리서치 인덱스

> 생성일: 2026-03-27
> 목적: PRD.md 작성을 위한 심층 조사 결과 총 정리
> 상태: **Round 1-6 완료. 최종 통합 문서 갱신 완료.**
>
> ## **최종 통합 문서**
> **[final-research.md](final-research.md)** — PRD.md 작성을 위한 단일 참조 문서 (**1,947줄**). 39개 파일 + Round 6 추가 심층조사 5건의 모든 발견·권고·리스크·긴장 해소를 통합.
> - R6 추가: Part XII(종목 추천 Bridge), Part XIII(비코더 UX), Part XIV(규제), Part XV(검증), Part XVI(workflow.md 패턴)

---

## 리서치 개요

| 구분 | 내용 |
|------|------|
| **제품명** | InvestScan — 한국시장 투자방향 AI 매크로 인텔리전스 |
| **핵심 자산** | EnvironmentScan (v2.5.0, 4 WF, 37 agents) + GlobalNews-Crawling (116 sites, 8-stage NLP) |
| **실행 환경** | 100% 로컬 (MacBook M5 Max 64GB), SaaS 아님 |
| **최종 산출물** | Claude Code workflow.md |
| **경쟁 기준** | 알파스퀘어를 포함한 모든 투자방향 앱 대비 "월등한 우위" |

---

## Round 1: 소스 시스템 분석 + 4-Phase Teammate (투자방향 스캐닝 시스템)

기존 두 시스템의 기술적 역량 분석 + PRD 방향 설정을 위한 8조사→4토론→3시나리오→최종통합

### 핵심 결론
- **권장 시나리오**: Balanced (~3,000 LOC, 주 3시간, 6개월)
- **Green Zone**: One-command, 주간 리포트, 다중 소스 통합, STEEPs 분류, 결정 저널
- **포지셔닝**: "망원경 vs 현미경" — 카테고리 창조, AlphaSquare 대체 아님

> Round 1 결과는 이 폴더의 시나리오 문서들에 내포되어 있음 (Round 2에서 통합 발전)

---

## Round 2: 경쟁우위 심층조사 + 4-Phase Teammate ("월등한 앱")

### Phase 0: 경쟁사 웹 리서치 (3건)

| 파일 | 내용 | 핵심 발견 |
|------|------|----------|
| [alphasquare-competitive-analysis.md](alphasquare-competitive-analysis.md) | 알파스퀘어 기능·가격·사용자·한계 심층 분석 | 220K 사용자, 19,800-69,900원/월, AI 시그널 340K sim/10min. **매크로 스캐닝 없음, 신호 진화 없음, 다국어 없음, 클라우드 전용** |
| [competitive-landscape-map.md](competitive-landscape-map.md) | 한국+글로벌 투자앱 경쟁 지도 | 4 Tier 분류. 8대 시장 공백 발견. PRISM-INSIGHT(512 stars)가 가장 직접적 오픈소스 경쟁자 |
| [overwhelmingly-superior-investment-app.md](overwhelmingly-superior-investment-app.md) | "월등한 우위"의 7가지 차원 정의 | 빈 사분면: 매크로 스캐닝 + 로컬 + 증거체인 + 교차 도메인. **아무도 차지하지 않은 교차점** |

### Phase 1: 8개 조사 Branch

| 파일 | Branch | 핵심 발견 |
|------|--------|----------|
| [optimistic-market-analysis.md](optimistic-market-analysis.md) | Market-Optimistic | 7차원 우위 (데이터 7.5x, 언어 14x, 프레임워크·프라이버시·비용·커스텀·투명성 = 카테고리 격차). "Hedge fund in a box" |
| [cautious-superiority-challenge.md](cautious-superiority-challenge.md) | Market-Cautious | AlphaSquare 제품 11차원 승리, InvestScan 분석 6차원 승리. **"다르게 유능한 것이지 월등한 것이 아니다"**. PRISM-INSIGHT 위협 |
| *(대화 내 인라인)* | User-EdgeCase | 3 페르소나 (전업투자자/크리에이터/체계적투자자). Core 7 Features. **"AlphaSquare는 물고기를 준다. InvestScan은 바다를 읽는 법을 준다"** |
| *(대화 내 인라인)* | User-Mainstream | 메인스트림 99% 전환 불가. 자연 도달 1-2%. Layer 1+2 최소 필요. "엔진은 우수하나 차체가 없는 자동차" |
| [investscan-superiority-architecture.md](investscan-superiority-architecture.md) | Tech-Fast | ~5,300 LOC, 3 구조적 우위 (다중시간축, 증거체인, 신호수명). 정확도 M7+ 검증 필요 |
| [long-term-superiority-architecture.md](long-term-superiority-architecture.md) | Tech-Scalable | 3 복제불가 장벽 (비즈니스 모델 비호환, 아키텍처 불가, 시간 의존 복리). **Month 24 = 추격 불가능** |
| [aggressive-competitive-strategy.md](aggressive-competitive-strategy.md) | Biz-Aggressive | 카테고리 창조 포지셔닝. 오픈소스 = 무기. 55%+ 섹터 방향 정확도 목표 |
| *(대화 내 인라인)* | Biz-Sustainable | **"열망적이되 망상에 가까움"**. "최고의 망원경을 만들어라, 더 나은 현미경이라 주장하지 마라". 결정 저널 = THE 핵심 기능 |

### Phase 2: 4개 관점 통합 토론

| 파일 | 내용 | 핵심 발견 |
|------|------|----------|
| [phase2-consolidated-discussion.md](phase2-consolidated-discussion.md) | Market/User/Tech/Biz 4관점 통합 | **Green Zone 6개**: One-command, 주간 리포트, 신호 통합, 결정 저널, STEEPs, 증거체인. **"월등 = 남들이 하는 것을 더 잘해서가 아니라, 아무도 하지 않는 것을 하기 때문"** |

### Phase 3: 3개 시나리오 수렴

| 파일 | 시나리오 | 핵심 수치 |
|------|---------|----------|
| [aggressive-scenario-prd.md](aggressive-scenario-prd.md) | Aggressive | ~4,850 LOC, 75-80hr, 출시확률 40-50% |
| [balanced-scenario-prd.md](balanced-scenario-prd.md) | **Balanced (권장)** | **~3,050-3,600 LOC, 60-80hr, 출시확률 70-80%** |
| [prd-conservative-scenario.md](prd-conservative-scenario.md) | Conservative | ~1,500 LOC, 30-43hr, 출시확률 90%+ |
| [final-three-scenarios-prd.md](final-three-scenarios-prd.md) | 3개 비교 + 최종 권장 | Balanced 선택 근거 6가지 |

### 기타 참조

| 파일 | 내용 |
|------|------|
| [06_long_term_scalability_architecture.md](06_long_term_scalability_architecture.md) | Round 1 Tech-Scalable 상세 (Spine+Rib 아키텍처) |
| [cautious-market-analysis.md](cautious-market-analysis.md) | Round 1 Market-Cautious (PRISM-INSIGHT 분석 포함) |

---

## 현재 합의 사항 (추가 조사로 변경 가능)

### 1. 포지셔닝
> **카테고리 창조자** — "로컬 매크로 투자 인텔리전스"라는 새 카테고리 정의
> AlphaSquare 대체품이 아닌, AlphaSquare가 답하지 못하는 질문에 답하는 도구

### 2. "월등히 뛰어난"의 정의
> 남들이 하는 것을 더 잘해서가 아니라, **아무도 하지 않는 것을 하기 때문에** 월등하다

### 3. Green Zone Features (4/4 합의)
1. One-command execution (`investscan run`)
2. 주간 한국어 종합 리포트
3. 다중 소스 신호 통합 (Schema normalization)
4. 결정 저널 (Decision Journal)
5. STEEPs 투자 분류
6. 증거 체인 (Evidence chains)

### 4. 권장 시나리오
**Balanced** — ~3,000 LOC, 주 3시간, Month 2 kill switch

### 5. 핵심 대립축 (미해결 — 추가 조사 필요 가능)
- "카테고리 창조" vs "직접 경쟁" 포지셔닝 최종 결정
- Layer 2 (웹 대시보드) 포함 시기
- 오픈소스 공개 시기와 전략
- 신호 정확도 검증 방법론

---

## Round 3: 기술·이론 심층 조사 (Technology Deep-Dive, 10 Branch + Phase 2-4)

### Phase 1: 10개 조사 Branch

| 파일 | Branch | 핵심 결론 |
|------|--------|----------|
| [tech-stack-aggressive-vs-conservative.md](tech-stack-aggressive-vs-conservative.md) | 1.1 Aggressive + 1.2 Conservative | **"Conservative Core + 1 Aggressive Bet (BGE-M3)"** — 나머지 전부 기존 스택, 트리거 기반 업그레이드 |
| [tech-architecture-analysis.md](tech-architecture-analysis.md) | 2.1 Evolutionary + 2.2 Big Bang | Evolutionary + Big Bang 2요소 (frozen dataclass, health check). **6개월 ~2,600 LOC, ~55-70hr** |
| [tech-dev-workflow-analysis.md](tech-dev-workflow-analysis.md) | 3.1 Rapid + 3.2 Robust | 표적 하이브리드: Schema 파싱 10개 + 섹터 매핑 15개 테스트만. **나머지 수동 검증** |
| [tech-debt-strategy-analysis.md](tech-debt-strategy-analysis.md) | 4.1 Debt-Minimized + 4.2 Practical | 표적 하이브리드: 재정 위험 부채만 예방 (+18hr). **2년 총 300-370hr (최저)** |
| [theory-foundation-analysis.md](theory-foundation-analysis.md) | 5.1 Modern/Cutting-Edge Theory | **STEEPs-first (NOT sentiment-first)**. KR-FinBERT 96.3%. 다중에이전트 토론 = HYPE |
| [classical-foundational-theory.md](classical-foundational-theory.md) | 5.2 Classical/Foundational Theory | **6 비타협 원칙** (멱등성, 관심사분리, 증거추적, 결정저널, 파일파이프라인, 스키마검증). 핵심: 제한된 합리성(Simon) |

### Phase 2-3-4: 통합 토론 → 시나리오 → 최종 권장

| 파일 | 내용 | 핵심 결론 |
|------|------|----------|
| [phase2-3-4-technology-deep-dive.md](phase2-3-4-technology-deep-dive.md) | 4관점 토론 + 3시나리오 + 최종 권장 | **Balanced-Tech 선택**: Conservative Core + BGE-M3 + 트리거 기반 업그레이드. ~2,470 LOC, ~70hr |

### 기술 Green Zone (4/4 합의)

| 계층 | 기술 | 근거 |
|------|------|------|
| Embedding | sentence-transformers + **BGE-M3** | 유일한 Aggressive bet (12.5% 품질↑, one-line swap) |
| Korean NLP | Kiwi (kiwipiepy) | 5년+ 검증, 싱글턴+배치 최적화 |
| Topic Modeling | BERTopic + HDBSCAN | 시간적 토픽 추적 내장, GlobalNews 이미 사용 |
| Classification | Rule-based (keyword dict) | Solo dev 유지보수성, 70-80% 정확도면 충분 |
| Storage | SQLite + Parquet (PyArrow) | 양 소스 시스템이 이미 사용, 추가 의존성 0 |
| Report Gen | Jinja2 Markdown templates | 0 ML 의존성, 즉시 편집 가능 |
| Orchestration | Python subprocess + launchd/cron | 수십 년 검증, 디버깅 용이 |
| Schema | @dataclass(frozen=True) | Pydantic보다 가볍고 충분 |
| Testing | pytest (25개 표적 테스트만) | Schema 파싱 + 섹터 매핑 경로만 |

### 기술 Yellow Zone (3/4, 트리거 기반)

| 기술 | 트리거 조건 |
|------|-----------|
| DuckDB (SQLite 대체) | SQLite 쿼리 >1초 |
| SetFit (rule-based 대체) | 규칙 기반 정확도 <70% |
| NetworkX (교차 분석) | 신호 간 관계 탐색 필요 시 |
| Ollama + Qwen3-32B (리포트) | Jinja2 템플릿 내러티브 품질 부족 시 |
| Snakemake (오케스트레이션) | 파이프라인 10단계+ 초과 시 |

### 6 비타협 설계 원칙 (고전 이론 기반)

1. **멱등성**: 동일 입력 → 동일 출력 (재실행 안전)
2. **관심사 분리**: 수집(EnvScan+GlobalNews) / 분석(InvestScan) / 표현(Report) 완전 분리
3. **증거 추적성**: 모든 방향성 판단에 소스→추론→결론 체인
4. **결정 저널**: Tetlock 초예측 원칙 — 가장 전략적으로 중요한 기능
5. **파일 기반 파이프라인**: Unix 철학 — 소스 시스템과 파일로만 통신
6. **스키마 검증**: 경계에서 타입 검증 (frozen dataclass)

### 이론적 프레임워크 (PRD용)

> **"제한된 합리성의 인지 보철물(cognitive prosthesis)로서, EMH 처리 지연을 교차 도메인 STEEPs 합성으로 활용하며, 경험적 보정(Decision Journal)으로 검증하는 시스템"**

---

## Round 4: 코딩·구현 심층 조사 (Implementation Deep-Dive, 10 Branch + Phase 2-4)

> Round 3 = 무엇을 쓸 것인가 (기술 선택) / Round 4 = **어떻게 만들 것인가** (실제 코드)

### Phase 1: 10개 구현 Branch

| 파일 | Branch | 핵심 결론 |
|------|--------|----------|
| [coding-normalization-sector-mapping.md](coding-normalization-sector-mapping.md) | 1.1 Aggressive + 1.2 Conservative 코딩 | **Aggressive schema + Conservative parser** = ~640 LOC. 소스 데이터 **6가지 포맷** 발견 (Round 3 추정 2가지보다 복잡) |
| [orchestration-implementation-analysis.md](orchestration-implementation-analysis.md) | 2.1 Evolutionary + 2.2 Big Bang 오케스트레이션 | **Big Bang CLI 권장** (Evolutionary 아님). Checkpoint/resume = 3.5hr 재실행 방지. ~880 LOC |
| [branch-3-output-implementation.md](branch-3-output-implementation.md) | 3.1 Minimal + 3.2 Rich 출력 | **Minimal + surgical 추가** (heatmap + retrospective) = ~575 LOC. JSONL 저널 |
| [testing-error-handling-implementation.md](testing-error-handling-implementation.md) | 4.1 Minimal + 4.2 Comprehensive 테스트 | **25 test + crash-loud (8hr)**. Month 4-6: +5 demand-driven. 총 14-15hr |
| [branch-5-workflow-integration-analysis.md](branch-5-workflow-integration-analysis.md) | 5.1 Deep + 5.2 Simple workflow.md | **Simple first** (shell 180 LOC). Python 파이프라인(~2,330 LOC) 동일 |

### Phase 2-3-4: 통합 토론 → 시나리오 → 최종 구현 가이드

| 파일 | 내용 | 핵심 결론 |
|------|------|----------|
| [phase2-3-4-implementation-guide.md](phase2-3-4-implementation-guide.md) | 4관점 토론 + 3시나리오 + 최종 코딩 가이드 | **Balanced Implementation**: ~2,710 LOC, ~64hr, 첫 리포트 Week 6 |

### Round 3→4 핵심 수정 사항

| 항목 | Round 3 추정 | Round 4 실제 |
|------|------------|------------|
| 소스 데이터 포맷 | 2가지 | **6가지** |
| 오케스트레이션 | Evolutionary | **Big Bang CLI** (checkpoint 필수) |
| 저널 저장소 | SQLite | **JSONL** |
| 총 LOC | ~2,470 | **~2,710** |
| 가장 중요한 코드 | Schema normalization | **normalizers.py (6-format parser)** |

### 최종 구현 계획 (Balanced, ~2,710 LOC, ~64hr)

```
Week 1:    schema.py + run.sh bootstrap
Week 2-3:  normalizers.py (6-format parser — THE critical code)
Week 3-4:  dedup + steeps_classifier + sector_mapper
Week 5:    synthesize_investment.py
Week 6:    report generator → 첫 유용한 리포트 생성
Week 7-8:  Click CLI 마이그레이션 (checkpoint/resume)
Week 9-10: decision journal + 25 targeted tests
Week 11-24: 유지보수 + conditional features (트리거 기반)
```

### THE ONE THING — 가장 중요한 구현 결정

> **`normalizers.py` — 6-format 파싱 모듈을 먼저 만들고, 실제 데이터로 테스트하고, 모든 필드 매핑을 수동 검증하라.** 이것이 틀리면 모든 하류 모듈이 잘못된 투자 방향을 생산한다.

---

## 추가 심층조사 가능 영역

아래 영역은 아직 조사되지 않았거나 깊이가 부족합니다:

## Round 5: 외부 연동 심층 조사 (External Integration Deep-Dive, 10 Branch + Phase 2-4)

> Round 3 = 무엇을 / Round 4 = 어떻게 / Round 5 = **무엇과 연결하여**

### Phase 1: 10개 외부연동 Branch

| 파일 | Branch | 핵심 결론 |
|------|--------|----------|
| [external-data-source-integration.md](external-data-source-integration.md) | 1.1+1.2 금융 데이터소스 | **FinanceDataReader + pykrx + fredapi** = 310 LOC, 5분. pykrx(22 KRX 섹터)가 핵심 |
| [branch-2-multi-model-integration-analysis.md](branch-2-multi-model-integration-analysis.md) | 2.1+2.2 AI 모델 CLI | **3 CLI 모두 설치+인증 완료**. subprocess.run() 호출 확인. 추가 비용 $0. Gemini MCP는 API 키 필요 → subprocess가 유일한 방법 |
| [branch-3.1-3.2-output-notification-integration.md](branch-3.1-3.2-output-notification-integration.md) | 3.1+3.2 출력/알림 | **Telegram Bot = 유일한 추가 채널** (5분, 만료 없음, 4096자). 카카오톡 ROI 최악 → SKIP |
| [branch-4-external-toolchain-integration.md](branch-4-external-toolchain-integration.md) | 4.1+4.2 도구체인 | **Hybrid**: launchd + RotatingFileHandler + WAL + JSONL export + pre-run copy. 추가 ~2.5hr |
| [branch-5-documentation-references.md](branch-5-documentation-references.md) | 5.1+5.2 문서/참조 | PRD 명시 인용 8개 + 암묵 준수 10개. Medallion Architecture(Bronze/Silver/Gold) 매핑 |

### Phase 2-3-4: 통합 → 시나리오 → 최종 가이드

| 파일 | 핵심 결론 |
|------|----------|
| [phase2-3-4-external-integration-guide.md](phase2-3-4-external-integration-guide.md) | **Balanced Integration**: 420 LOC, 2.5hr 세팅, 6 failure modes, 15분/월 유지. 멀티모델은 config flag 뒤에 scaffold |

### Round 5 핵심 발견 3가지

**1. AI 모델 구독 연동 = 해결됨**
> Gemini CLI (OAuth), Codex CLI (ChatGPT subscription), Claude Code — 모두 subprocess.run()으로 호출 가능. API 키 불필요. 비용 $0.

**2. Telegram Bot > 카카오톡**
> 카카오톡: 200자 제한 + 30일 토큰 만료 + 복잡한 OAuth. Telegram: 4096자 + 영구 토큰 + 5분 세팅.

**3. 금융 데이터 = pykrx가 핵심**
> 22개 KOSPI 섹터 OHLCV 데이터를 무료로 제공하는 유일한 라이브러리. STEEPs → 섹터 방향 검증에 필수.

### 외부 연동 Green Zone (M1 포함)

| 연동 | 라이브러리 | 인증 | LOC | 장애 시 |
|------|----------|------|-----|--------|
| KOSPI 섹터 데이터 | pykrx | 없음 | ~110 | 이전 주 캐시 사용 |
| 글로벌 지수/환율 | FinanceDataReader | 없음 | ~90 | 리포트에서 해당 섹션 생략 |
| Claude Code | 내장 | 구독 | 0 | 전체 파이프라인 중단 |
| Telegram 알림 | requests | Bot token | ~45 | 알림 실패, 리포트는 정상 |
| 자동 스케줄링 | launchd | 없음 | ~30(plist) | 수동 실행으로 대체 |
| 로그 관리 | logging | 없음 | ~15 | 로그 없이도 작동 |

### 외부 연동 Yellow Zone (M2-M4, 트리거 기반)

| 연동 | 트리거 | LOC |
|------|--------|-----|
| fredapi (매크로) | M2: 첫 리포트에서 매크로 맥락 부족 시 | ~110 |
| Gemini CLI | M3: 장문 문서 분석 필요 시 (>200K 토큰) | ~120 |
| Codex CLI | M3: JSON 구조화 출력 + 웹 검색 필요 시 | ~120 |
| Email (Gmail) | M4: 자동화 실행 시 알림 이중화 | ~55 |
| Streamlit 대시보드 | M4: 시각적 탐색 필요 시 | ~300 |
| PDF 내보내기 | M4: 외부 공유 필요 시 | ~110 |

---

## 추가 심층조사 가능 영역

1. ~~Schema 매핑 실증 분석~~ → Round 4 해결
2. **주간 리포트 UX 리서치** — 투자 리포트 모범 사례
3. ~~STEEPs → 투자 섹터 매핑~~ → Round 4+5 해결
4. ~~결정 저널 설계~~ → Round 4 해결
5. **PRISM-INSIGHT 상세 분석** — 코드 수준 비교
6. ~~규제 리스크~~ → **Round 6 해결** (Part XIV: 자본시장법 비해당, 면책 조항 설계)
7. ~~백테스팅 없는 검증~~ → **Round 6 해결** (Part XV: Brier Score + 이항검정 + 캘리브레이션)
8. **사용자 인터뷰 시뮬레이션** — 3 Edge Case 페르소나 심화
9. ~~종목 추천 방법론~~ → **Round 6 해결** (Part XII: WICS + 멀티팩터 + 에비던스 체인)
10. ~~비코더 자동구현 UX~~ → **Round 6 해결** (Part XIII: Claude Code 자율 구현 + 원커맨드)
11. ~~workflow.md 설계 패턴~~ → **Round 6 해결** (Part XVI: Anthropic 사례 + 7대 원칙)
