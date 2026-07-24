# PRD Teammate 1차 심층조사 종합 결과

> **조사 완료일**: 2026-03-12
> **프레임워크**: prd_teammate_executable.md (4-Phase Fork-Based Sessions)
> **에이전트 총 투입**: 15개 (Phase1: 8, Phase2: 4, Phase3: 3)
> **목적**: SaaS 자동 구현 AI agentic workflow automation system의 PRD.md 작성을 위한 사전 리서치
> **핵심 제약**: 이 시스템은 SaaS가 아님 — 사용자의 로컬 컴퓨터(Claude Code CLI)에서 작동

---

## 1. 핵심 질문 3회 정밀 독해 결과

### 1회차 — 구조적 읽기
핵심 질문들이 **5개 계층**으로 분류됨:
- **Input**: 아이디어 입력, 개발도구/템플릿 선택 (시스템 초기 설정)
- **Feature**: 핵심 기능, 추가 기능 (범위 정의)
- **User**: 사용자, 사용 사례, 문제, 목표, 기술 수준 (사용자 연구)
- **Specification**: PRD, User Journey, TRD, Code Guidelines, Design Guide, IA (문서 생성 파이프라인)
- **Implementation**: Tasks 생성, AGENTS.md, rules.md (실행 인프라)

### 2회차 — 확장 읽기
- Input→Feature→User는 **대화형 수집 파이프라인** (점진적 구체화)
- DB/Auth/고급기능 질문은 **TRD 복잡도 분기점**
- 디자인 가이드 → IA는 **전문 에이전트 위임 구조** (시니어 디자이너, UX 아키텍트)
- AGENTS.md + rules.md 생성은 **자식 시스템의 DNA를 주입**하는 구조 (soul.md 패턴 동일)

### 3회차 — 중간 정밀 보충
- "사용자 기술 수준"이 **아키텍처 전체를 결정** (비개발자 = no-code, 개발자 = CLI)
- PRD → TRD 순서는 **의도적** (사용자 중심 설계 후 기술 구체화)
- 디자인 가이드의 "4단계 과정"은 **멀티턴 대화** 능력 필수를 의미
- 모든 문서가 **상호 참조(SOT 원칙)** 해야 하므로 문서 간 일관성 보장 메커니즘이 핵심

**결론**: "AI PM + AI Architect + AI Designer + AI Developer"를 **로컬 CLI 환경에서 순차-병렬 오케스트레이션**하는 워크플로우 자동화 시스템

---

## 2. Phase 1: 8개 Branch 조사 결과

### 2.1 Market Researcher — Optimistic (기회주의)
**파일**: `prompt/market-research-optimistic.md`

- AI 개발도구 시장: $7.37B (2025) → $23.97B (2030), CAGR 26.6%
- AI 앱 빌더 시장: $4.7B (2026) → $12.3B (2027), ~162% YoY
- Low-Code/No-Code: $26.3B-$37.4B (2025) → $67B-$187B (2030)
- **경쟁사 실적**: Cursor $2B+ ARR, Lovable $300M ARR (8개월만에 $100M), Bolt.new $40M+ ARR
- 대상: Indie hackers (+340% YoY), 스타트업 팀 (63% daily AI 사용), Side project 개발자 (72% daily AI)
- **낙관적 TAM**: $1.2B-$3.0B (30M 개발자 중 5M SaaS 빌더, $20-50/mo)
- "Vibe Coding"이 2025년 올해의 단어 선정

### 2.2 Market Researcher — Cautious (보수주의)
**파일**: `prompt/market-research-cautious-report.md`

- AI 코드 수용률 겨우 30% (46% 제안 중 30%만 accept)
- AI 생성 코드 1.7x 더 많은 이슈, 45% 보안 테스트 실패
- 변경 실패율 ~30% 증가, 경험 많은 개발자가 오히려 19% 느림 (METR RCT)
- 대다수 AI 생성 "앱"은 프로덕션에 도달하지 못함
- **보수적 TAM**: 90K-115K 유저, $22M-$69M ARR 상한
- **경쟁사 강점**: Cursor ($29.3B, $2.3B 펀딩), Lovable ($6.6B, $653M), Replit ($9B, $400M+)
- 합산 $4B+ 펀딩으로 진입장벽 극도로 높음

### 2.3 User Researcher — Edge Case (극단적 니치 사용자)
- 페르소나: Solo Founder, Serial Hacker (10+ years 경험)
- P0 = 문서 생성 파이프라인 (PRD→TRD→Tasks)
- 이 사용자들은 CLI 장벽 없음, 높은 의도, 빠른 평가
- 핵심: "문서 연결이 곧 제품" — 추적성이 차별화

### 2.4 User Researcher — Mainstream (평균적 대중)
- 페르소나: Junior Dev, PM, Hobbyist
- CLI 장벽 존재, 15+ 질문 시 이탈 위험 (67%)
- Quick Mode + Web GUI 없이는 이 시장 접근 불가
- **합의**: V1 = 파워유저, V2 = Mainstream 확장

### 2.5 Tech Architect — Monolithic (빠른 출시)
- 14주 MVP 가능
- 단일 context window 불가 (500K+ 토큰)
- 빠른 출시 우선, 나중에 리팩토링

### 2.6 Tech Architect — Microservices (장기 확장성)
- 모듈러 모놀리스 (두 Branch 모두 여기로 수렴)
- 7-9개월 손익분기
- Agent SDK + 스키마 기반 접근

### 2.7 Business Strategist — Aggressive (공격적)
- $29K MRR / 6개월, 12K 유저 목표
- Open-Core + Marketplace 모델

### 2.8 Business Strategist — Sustainable (안정적)
**파일**: `prompt/strategy-report-sustainable-growth.md`

- $1.5-3K MRR / 6개월, 250-350 유저
- Open-Core + Templates 모델
- Community (Free) → Pro ($19/mo) → Team ($49/mo) → Enterprise ($2K-$10K)
- BYOK (Bring Your Own Key) — 마진 비용 ≈ $0
- 손익분기: Month 8-10 (~80 Pro 구독자)
- Comparable: Supabase ($70M ARR), Vercel ($9.3B, Next.js 소유)

---

## 3. Phase 1 통합 (8개 Branch 교차 분석)

### 3.1 스펙트럼 매핑

```
Market:   기회주의 ←──[6/10]──→ 보수주의
          $40B+ 시장, 폭발적 수요    $22M-$69M 현실적 TAM
          → 시장은 존재하나 진입장벽 높음

User:     극단적 ←──[4/10]──→ 평균적
          Solo Founder/Serial Hacker   Junior Dev/PM
          → V1은 파워유저 집중이 합의

Tech:     모놀리식 ←──[5/10]──→ 마이크로서비스
          빠른 출시, 14주 MVP          모듈러 모놀리스
          → 두 Branch 모두 "모듈러 모놀리스"에 수렴

Business: 공격적 ←──[6/10]──→ 안정적
          $29K MRR/6개월              $1.5-3K MRR/6개월
          → 두 Branch 모두 Open-Core 모델에 합의
```

### 3.2 절대적 합의 (8/8 Branch 동의)

1. **대화형 Q→문서 파이프라인** = 핵심 차별화
2. **로컬 실행 (CLI-first)** = 경쟁사와의 유일한 구조적 차별점
3. **SOT 기반 문서 체인** (PRD→TRD→Code Guidelines→Tasks) = 가치의 핵심
4. **Open-Core 수익 모델** (무료 코어 + 프리미엄 지식 레이어)

### 3.3 절대적 회피 (8/8 Branch 동의)

1. "프로덕션 레디" 코드라고 약속하지 말 것 — AI 코드 버그 1.7x, 보안 취약점 45%
2. 단일 context window에서 전체 워크플로우 실행 — 500K+ 토큰으로 불가
3. Mainstream 사용자를 V1에서 타겟팅 — CLI 장벽 + 15+ 질문 이탈 위험
4. $4B+ 펀딩된 경쟁사와 정면 승부하지 말 것

### 3.4 최대 불일치

| 불일치 | Branch A | Branch B | 해결 필요 데이터 |
|--------|----------|----------|----------------|
| 시장 크기 | $40B+ (Optimistic) | $22M-$69M (Cautious) | 실제 CLI 도구 사용자 수 |
| 6개월 MRR | $29K (Aggressive) | $1.5-3K (Sustainable) | 초기 100명 유저 전환율 |
| 코드 생성 범위 | 풀 구현 (Monolithic) | 스캐폴딩+스텁 (Micro) | 실제 생성 코드 품질 테스트 |
| 질문 수 | 15+ 딥 (EdgeCase) | 3-5 퀵 (Mainstream) | A/B 테스트 완료율 |

---

## 4. Phase 2: 4개 관점별 토론 결과

### 4.1 Discussion-Market (시장 기회 우선)
- **현실 TAM**: $50M-$150M (3년), Year 1 SOM: $22M-$69M
- **포지셔닝**: "Lovable gives you a prototype. We give you a production architecture."
- **5 MUST HAVEs**: 대화→문서 파이프라인, 7문서 풀체인, 교차검증, 편집가능 중간문서, Next.js+Supabase+Stripe 템플릿 1개
- **가격**: $19/mo (not $29 — 인디 개발자 가격 민감)
- **14주가 시장 한계선** — 이후 경쟁사가 유사 기능 추가 가능

### 4.2 Discussion-User (사용자 만족 우선)
- **"A mediocre PRD generator with beautiful web GUI will lose to an excellent PRD generator with bare CLI."**
- V1 = 파워유저 집중, V2 = Quick Mode + Web GUI로 Mainstream 확장
- **3-7개 스마트 질문** (15+가 아님) — 스마트 기본값으로 67% 이탈 방지
- **5 MUST HAVEs**: 대화형 PRD, TRD+코드가이드(PRD에서 파생), 태스크 생성, 컨텍스트 전파, 완전한 사용자 소유
- **"문서 간 연결이 곧 제품"** — PRD→TRD→Tasks의 추적성이 유일한 차별화
- 시간 목표: 아이디어→7질문→6문서 10분→구현 시작 30분

### 4.3 Discussion-Tech (기술 실현성 우선)
- **"The 6-month product is a 'structured document pipeline' — not an 'auto-builder'."**
- **모듈러 모놀리스** 확정 — 두 Tech Branch 모두 수렴
- 6개월(26 생산주) = **극도로 타이트** — 슬랙 제로
- **Green Zone** (확실히 구현 가능):
  1. 대화 엔진 (멀티턴 Q&A)
  2. 7문서 파이프라인 (PRD, User Journey, TRD, Code Guidelines, UI Guidelines, IA, Tasks)
  3. JSON Schema 검증
  4. Next.js+Supabase+Stripe 템플릿 1개
  5. AI 작업 규칙 (AGENTS.md, rules.md 생성)
  6. 문서 교차검증
  7. 문서 내보내기 (Markdown)
- **Red Zone** (6개월 불가):
  - 풀 SaaS 자동구현, 원클릭 배포, Quick Mode, Multi-LLM, 마켓플레이스, GUI
- 기존 AgenticWorkflow 인프라로 **7-11주 절감**
- **핵심 결정**: 문서 파이프라인 먼저, 코드 생성은 V2

### 4.4 Discussion-Business (비즈니스 지속성 우선)
**파일**: `prompt/discussion-business-sustainability.md`

- **성장 모델: SUSTAINABLE** — Aggressive ($29K MRR, 12K 유저)는 역사적 선례 없음
- **Open-Core + BYOK** 모델 — 마진 비용 ≈ $0, ~80 Pro 구독자에서 손익분기
- **현실적 Year 1 수입**: $18K-$45K (80-200 Pro 구독자)
- **LTV:CAC = 2.5-10x** — 유기적 배포(GitHub/CLI)가 CAC을 $30-80으로 유지
- **전환율 벤치마크**: CLI 도구 1.5-3% (일반 dev tools 2-5%, 오픈소스 <1%)
- **최종 판정: CONDITIONALLY VIABLE** — 3가지 취약 조건 (2%+ 전환율, $19/mo 가치 입증, 6개월 500+ 유저)

#### 비즈니스 기능 우선순위 분석

| 기능 | 수익 드라이버? | 리텐션 드라이버? | 전환 드라이버? |
|------|-------------|----------------|--------------|
| 대화형 PRD | No (무료) | HIGH (aha moment) | HIGH (입소문) |
| 7문서 파이프라인 | YES (프리미엄 템플릿) | HIGH (완결성) | MEDIUM |
| 교차검증 | No | HIGH (신뢰 구축) | LOW (보이지 않는 품질) |
| 편집 가능 문서 | No | HIGH (자율성) | MEDIUM |
| Next.js 템플릿 | YES (수익화 핵심) | MEDIUM | HIGH ("작동하는 코드!") |
| 컨텍스트 전파 | No | HIGH ("문서 연결 = 제품") | LOW |
| 태스크 생성 | Weak | MEDIUM | MEDIUM |

#### GO/NO-GO KPI (6개월)

| KPI | GO | NO-GO |
|-----|----|-------|
| Free→Paid 전환율 | ≥2.0% | <0.8% |
| 30일 리텐션 | ≥40% | <20% |
| MRR | ≥$1,500 | <$500 |
| 대화 완료율 | ≥70% | <40% |
| NPS | ≥+40 | <+10 |

---

## 5. Phase 2 통합: 4개 Perspective PRD 비교

| 기능 | Market | User | Tech | Business | 합의도 |
|------|--------|------|------|----------|--------|
| 대화형 PRD 생성 | ✓ 필수 | ✓ 필수 | ✓ Green | ✓ 필수(hook) | **4/4 ✅** |
| 7문서 파이프라인 | ✓ 필수 | ✓ 필수 | ✓ Green | ✓ 필수 | **4/4 ✅** |
| 문서 간 교차검증 | ✓ 필수 | △ Nice | ✓ Green | △ Nice | 3/4 |
| 편집 가능 중간 문서 | ✓ 필수 | ✓ 필수 | ✓ Green | △ Nice | 3.5/4 |
| Next.js 템플릿 | ✓ 필수 | △ Nice | ✓ Green | ✓ 필수(proof) | 3.5/4 |
| 컨텍스트 전파 | △ Nice | ✓ 필수 | ✓ Green | ✓ 필수(차별화) | 3.5/4 |
| 태스크 생성 | △ Nice | ✓ 필수 | ✓ Green | △ Nice | 2.5/4 |
| Free/Paid 경계 | — | — | — | ✓ 필수 | Business only |
| 15분 이내 첫 경험 | △ Nice | ✓ 필수 | △ 가능 | ✓ 필수 | 3/4 |

**Green Zone (4/4)**: 대화형 PRD, 7문서 파이프라인
**Yellow Zone (3+)**: 교차검증, 편집가능 문서, 템플릿, 컨텍스트 전파, 첫 경험
**Red Zone (<3)**: 풀 자동구현, 배포, GUI, 마켓플레이스, Multi-LLM

---

## 6. Phase 3: 3개 시나리오 비교

### 6.1 Aggressive Scenario
**파일**: `prompt/prd-aggressive-scenario.md`

- **10개 기능**, 24.5/26주, 버퍼 1.5주 (5.8%)
- MRR 목표: $10,750 at Month 6 ($29/mo Pro, 2,500 유저, 4% 전환)
- 기술 부채: **매우 높음**, Month 7-8 필수 리팩토링
- 실패 확률: **25-35%**
- Month 4 Hard Go/No-Go Gate — 조기 경보 3+ 시 Conservative로 전환
- **서명**: Market AGREE, User ACCEPT(우려), Tech ACCEPT(우려), Business ACCEPT(강한 우려)
- **핵심 논거**: 14주 spec-driven development 공백, 경쟁사 신뢰 결함 (Lovable 18,000유저 데이터 노출, Bolt.new $1,000+ 토큰비, Replit DB 삭제), Solo founder +340% YoY

### 6.2 Balanced Scenario ← **최종 선택**
**파일**: `prompt/prd-balanced-scenario.md`

- **8개 기능**, 24/26주, 버퍼 3주 (11.5%)
- MRR 목표: $1,260-$2,520 at Month 6 ($19/mo, 220-350 유저, 2-3% 전환)
- 기술 부채: **중간**
- 실패 확률: **10-15%**
- **서명**: Market ACCEPT, User AGREE, Tech ACCEPT, Business AGREE (2 AGREE, 2 ACCEPT)

#### 8개 기능 상세

| # | 기능 | P | 주수 | 역할 |
|---|------|---|------|------|
| F1 | 대화형 SaaS 정의 엔진 (5-7 스마트 질문) | P0 | 3 | The Hook |
| F2 | 7문서 파이프라인 | P0 | 5 | The Differentiator |
| F3 | Next.js+Supabase+Stripe 템플릿 | P0 | 4 | The Proof |
| F4 | 문서 간 컨텍스트 전파 (V1=단방향) | P1 | 3 | The Magic |
| F5 | 편집 가능 중간 문서 + 재전파 | P1 | 2 | The Trust |
| F6 | Free/Paid 경계 (3프로젝트 제한) | P1 | 2 | The Business |
| F7 | 15분 이내 첫 경험 | P2 | 2 | The Retention |
| F8 | 기본 교차검증 엔진 | P2 | 3 | The Quality |

#### 아키텍처: 모듈러 모놀리스

```
saas-auto-builder/
├── core/
│   ├── conversation-engine/     ← F1
│   ├── document-pipeline/       ← F2
│   ├── context-propagation/     ← F4
│   └── cross-validation/        ← F8
├── generators/
│   ├── prd/, user-journey/, trd/, code-guidelines/
│   ├── ui-guidelines/, information-architecture/, tasks/
├── templates/
│   ├── nextjs-supabase-stripe/  ← F3
│   └── template-engine/
├── licensing/tier-manager/      ← F6
├── cli/
│   ├── onboarding/              ← F7
│   ├── commands/
│   └── editor-integration/      ← F5
└── shared/
    ├── llm-adapter/             ← V2 Multi-LLM 대비
    ├── config/
    └── types/
```

#### 마일스톤

| 마일스톤 | 기간 | 산출물 |
|---------|------|--------|
| M1 | Month 1-2 (W1-8) | 대화 엔진 + 7문서 파이프라인 → Private Alpha (10-15명) |
| M2 | Month 3-4 (W9-18) | 템플릿 + 전파 + 편집 + Free/Paid → Public Beta + ProductHunt |
| M3 | Month 5-6 (W19-26) | 교차검증 + 품질 강화 + Pro 런치 → $1,260-$2,520 MRR |

#### 수익 전망

| Month | 누적 무료 유저 | 유료 구독 | MRR |
|-------|-------------|----------|-----|
| 1-2 | 25-40 | 0 | $0 |
| 3 | 60-90 | 2-5 | $38-$95 |
| 4 | 100-150 | 8-15 | $152-$285 |
| 5 | 150-220 | 20-40 | $380-$760 |
| 6 | 220-350 | 40-80 | $760-$1,520 |

#### V2 로드맵 (Month 7-12)

| 기능 | V2 시기 | 진입 조건 |
|------|---------|----------|
| 템플릿 마켓플레이스 | Month 7-8 | 500+ 유저 + 커뮤니티 수요 |
| 멀티프레임워크 (Svelte, Nuxt) | Month 8-9 | Next.js 만족도 >85% |
| Web GUI | Month 9-12 | CLI 유저 <500 at Month 6 |
| 원클릭 배포 | Month 10-12 | 200+ 유료 구독 + 50%+ 요청 |
| Multi-LLM | Month 11-12 | Anthropic 가격 변동 |

### 6.3 Conservative Scenario
**파일**: `prompt/prd-conservative-scenario.md`

- **4개 기능**, ~18/26주, 버퍼 30%+
- MRR 목표: $285-$760 at Month 6 (1-1.5% 전환)
- 기술 부채: **거의 없음**, 85%+ 테스트 커버리지
- 실패 확률: **5%**
- **서명**: Market CONCERN, User ACCEPT, Tech AGREE, Business ACCEPT
- **"Boring but alive" 논거**: 200명의 행복한 유저가 2,000명의 좌절한 유저보다 낫다
- **Worst case**: $9K-$11.4K 총 비용 + OSS 프로젝트 + 전문성 자산 → 커리어 우회, 파탄 아님

---

## 7. Phase 4: 최종 의사결정

### 선택: BALANCED SCENARIO

**선택 근거 (prd_teammate_executable.md 체크리스트)**:
- Balanced 4/4 조건 충족 (시장 긴급성 중간, 균형잡힌 팀, 단기+장기 중요, 현실적 접근)
- Aggressive 2/4 (탈락), Conservative 3/4 (차순위)

**버린 시나리오 이유**:
- Aggressive: 1.5주 버퍼로 Solo founder 비현실적, 4% 전환율에 선례 없음
- Conservative: "Boring but alive" 매력적이나 14주 창에서 4기능만으론 카테고리 피탈

### 위험 가정 TOP 5

| # | 가정 | 확률 | 영향 | 완화 |
|---|------|------|------|------|
| 1 | Free 티어 충분 → 전환 없음 | 45% | Fatal | 3프로젝트 제한 + 산업 템플릿 페이월 |
| 2 | 경쟁사 문서 파이프라인 추가 | 60-70% | High | 깊이(교차검증, 전파) 구축 |
| 3 | CLI 너무 니치 (<200명) | 25-35% | Fatal | V2 GUI 아키텍처 Day 1 준비 |
| 4 | 템플릿 코드 품질 부족 | 30-40% | High | 인간 큐레이션 + 자동 테스트 |
| 5 | Solo founder 번아웃 | 35-45% | Medium | 주 50시간 상한 + F8 컷 옵션 |

---

## 8. 핵심 데이터 포인트 (빠른 참조)

### 시장 데이터
- AI 코딩 도구 시장: $7.37B (2025), CAGR 26.6%
- 현실적 TAM: $22M-$69M (CLI 로컬 도구 니치)
- 3년 TAM: $50M-$150M
- 경쟁사 합산 펀딩: $4B+

### 경쟁사 핵심 지표
| 경쟁사 | 밸류에이션 | ARR | 유저 | 약점 |
|--------|----------|-----|------|------|
| Cursor | $29.3B | $2B+ | 50K+ 팀 | IDE 종속, 문서 파이프라인 없음 |
| Lovable | $6.6B | $300M | 25M+ 프로젝트 | 18K 유저 데이터 노출, 프로토타입 수준 |
| Bolt.new | $700M | $40M+ | 비공개 | $1K+ 토큰 비용, 15-20컴포넌트서 붕괴 |
| Replit | $9B | $265M | 40M+ | 라이브 DB 삭제 사고, 성능 이슈 |
| Devin | $10.2B | ~$150M | 엔터프라이즈 | 20개 중 3개만 완료 |

### AI 코드 품질 데이터
- AI 생성 코드 이슈 1.7x (CodeRabbit, Dec 2025, 470 PRs)
- 45% 보안 테스트 실패 (Veracode 2025)
- 변경 실패율 ~30% 증가 (Cortex)
- 5개 중 1개 조직에서 심각한 보안 사고 (AI 코드 기인)
- 경험 많은 개발자 19% 느림 (METR RCT, Jul 2025)

### 비즈니스 벤치마크
- 인디 프로젝트 중간값: $500/mo (IndieMarkerAnalytics, 326개)
- 오픈소스 SaaS 전환율: 0.3-3% (Monetizely)
- 개발자 도구 전환율: ~5% 중간값 (GUI 포함, Lenny's Newsletter)
- CLI 도구 전환율: 1-3% (추정)
- SaaS SMB 월간 이탈: 3-5%
- 개발자 도구 CAC: $480-$942 (B2B SaaS 평균), CLI/GitHub 유기적 $30-$80

### 수익 모델
- Community (Free): 코어 파이프라인 + 기본 템플릿 + 3프로젝트 제한
- Pro ($19/mo): 산업 템플릿 + 고급 가이드라인 + 무제한 프로젝트
- Team ($49/mo): 공유 라이브러리 + 커스텀 템플릿 + PM 연동
- Enterprise ($2K-$10K): 커스텀 워크플로우 + 교육

---

## 9. 추가 조사 필요 영역 (향후 심층조사 후보)

1. **기술 심층조사** (`Technology_Development_DeepDive_PRD_Teammate_Executable.md` 프레임워크 활용)
   - 10개 Branch: Core Tech, Architecture, Dev Workflow, Tech Debt Manager, Theory Foundation
   - 현재 PRD teammate은 시장/사용자/기술/비즈니스 4관점이었으나 기술 구체화 필요

2. **경쟁사 실제 사용 경험 분석**
   - Cursor, Lovable, Bolt.new 실사용 리뷰 전수조사
   - 실패 사례 패턴 분류 (어디서 실패하는가?)

3. **대화형 Q&A 엔진 설계**
   - 5-7개 스마트 질문의 구체적 설계
   - 도메인별 질문 분기 (e-commerce vs marketplace vs dashboard)
   - 질문 순서와 의존 관계

4. **문서 간 SOT 체인 설계**
   - PRD→TRD→Code Guidelines→Tasks의 구체적 데이터 플로우
   - JSON Schema 정의
   - 전파 규칙 (변경 시 어디까지 cascade)

5. **Free/Paid 경계 최적화**
   - 3프로젝트 제한의 타당성 검증
   - 산업 템플릿의 구체적 가치 제안
   - 전환 트리거 심리학

6. **기존 AgenticWorkflow 인프라 활용 전략**
   - 7-11주 절감 추정의 구체화
   - 어떤 모듈을 재사용할 수 있는가?
   - 새로 만들어야 하는 부분은?

---

## 10. 파일 인덱스

| 파일 | 유형 | 내용 |
|------|------|------|
| `prompt/prd_teammate_executable.md` | 프레임워크 | 4-Phase teammate 실행 지침 (원본) |
| `prompt/Technology_Development_DeepDive_PRD_Teammate_Executable.md` | 프레임워크 | 기술 심층조사 10-Branch 프레임워크 (미실행) |
| `prompt/market-research-optimistic.md` | Phase 1 | 기회주의 시장 분석 |
| `prompt/market-research-cautious-report.md` | Phase 1 | 보수주의 시장 분석 |
| `prompt/strategy-report-sustainable-growth.md` | Phase 1 | 안정적 성장 전략 |
| `prompt/discussion-business-sustainability.md` | Phase 2 | 비즈니스 지속성 토론 (462줄, 출처 포함) |
| `prompt/prd-aggressive-scenario.md` | Phase 3 | 공격적 시나리오 PRD |
| `prompt/prd-balanced-scenario.md` | Phase 3 | **균형 시나리오 PRD (최종 선택)** |
| `prompt/prd-conservative-scenario.md` | Phase 3 | 보수적 시나리오 PRD |
| `prompt/RESEARCH-SYNTHESIS-prd-teammate-round1.md` | 종합 | **이 문서 — 1차 조사 전체 종합** |
