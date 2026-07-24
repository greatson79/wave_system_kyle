# Technology Deep-Dive 2차 심층조사 종합 결과

> **조사 완료일**: 2026-03-12
> **프레임워크**: Technology_Development_DeepDive_PRD_Teammate_Executable.md (4-Phase Fork-Based Sessions)
> **에이전트 총 투입**: 17개 (Phase1: 10, Phase2: 4, Phase3: 3)
> **목적**: SaaS Auto-Builder PRD.md 작성을 위한 **기술 전문** 사전 리서치
> **핵심 제약**: 로컬 CLI 실행, Solo founder, 6개월, 8기능

---

## 1. 핵심 질문 3회 정밀 독해 결과 (기술 관점)

### 1회차 — 기술 구조 읽기
핵심 질문들이 **9개 기술 엔진**을 요구:
1. NLU/Intent Engine (자연어 → 구조화된 의도)
2. Tool/Template Selection Engine (제약 기반 추천)
3. Feature Extraction Engine (도메인별 기능 분류)
4. User Research Engine (페르소나 + 기술 수준 평가)
5. Document Generation Pipeline (7문서 SOT 체인)
6. Design Generation Engine (4단계 멀티턴)
7. IA Generation Engine (정보 구조)
8. Task Generation Engine (문서 → 태스크)
9. Agent Configuration Engine (AGENTS.md/rules.md = DNA 주입)

### 2회차 — 기술 확장 읽기
- 멀티턴 대화형 AI 엔진 + 컨텍스트 관리 (LLM 호출당 수천 토큰)
- 도메인 지식 베이스 (SaaS 수직 시장별 기능 카탈로그)
- **사용자 기술 수준이 모든 하위 생성의 아키텍처를 결정**
- **문서 간 SOT 체인 + 교차검증 — 가장 어려운 기술 과제**
- 전문 에이전트 위임 (디자이너, UX 아키텍트) → 멀티에이전트 오케스트레이션
- 메타프로그래밍 — AI가 다른 AI의 규칙을 생성

### 3회차 — 중간 정밀 보충
- PRD→TRD 전환이 문서 체인의 시작점 — forward-propagation 작동 지점
- 4단계 디자인 가이드 = stateful 멀티턴 에이전트 세션 필수
- AGENTS.md 생성 = DNA 유전 (AgenticWorkflow의 soul.md 패턴)
- 핵심 기술 갭: "문서 파이프라인"(V1) vs "풀 자동 구현"(V2+)

---

## 2. Phase 1: 10개 Branch 기술 심층 조사

### 2.1 Core Tech — Aggressive (Branch 1.1)
**파일**: `prompt/tech-deep-dive-aggressive-cutting-edge.md`
- Claude Sonnet 4.5 (77.2% SWE-bench) + Structured Outputs (100% 스키마)
- Prompt Caching (90% 비용, 85% 지연 감소) + Batch API (50% 추가 절감)
- Claude Agent SDK + MCP 프로토콜 (97M+ 월간 다운로드)
- Zod → JSON Schema → Structured Outputs (단일 정의 흐름)
- Next.js 15+ Turbopack + Drizzle ORM (7KB) + shadcn/ui + Biome (56x 빠름)
- **추천도**: 8.5/10

### 2.2 Core Tech — Conservative (Branch 1.2)
**파일**: `prompt/technology-stack-conservative-analysis.md`
- Node.js LTS (15년+, 98% Fortune 500), Commander.js (13년+, 27K stars)
- 직접 REST API 호출 (SDK 의존성 없음), Handlebars/EJS (14년+)
- Ajv JSON Schema 검증 (85M 주간 다운로드)
- Next.js 14 + Supabase + Stripe (99.999% 업타임)
- **안정성**: 9/10, "Build with boring technology. Ship on time."

### 2.3 Architecture — Evolutionary (Branch 2.1)
**파일**: `prompt/tech-deep-dive-evolutionary-architecture.md`
- ~25 파일로 시작, 직접 함수 호출, 추상화 없음
- 파일 기반 상태 관리 (CLI에 DB 불필요)
- DAG 병렬 생성 (준비 시 도입)
- AgenticWorkflow 인프라 재사용: 2.5-4주 절감
- 진화 트리거: 관찰 가능한 조건 9개 정의 (달력이 아닌 신호 기반)
- **결론**: Evolutionary 확정, Big Bang 대비 2-3개 기능 더 배송

### 2.4 Architecture — Big Bang (Branch 2.2)
**파일**: `prompt/architecture-big-bang-design-report.md`
- Clean Architecture + tsyringe DI + typed event bus + plugin system
- BaseGenerator<T> 플러그인 (7문서 각각 독립 플러그인)
- Token Budget Manager (컨텍스트 윈도우 = 예산)
- 18주 소요, 점진적 출시 병행 시 "조건부 YES"
- 과잉 설계 비용: ~1,050 LOC / 3-4일 (나중 3-4주 리팩토링 보험)
- AgenticWorkflow DNA 매핑: 9개 부모 컴포넌트 → 자식 표현

### 2.5 Dev Workflow — Rapid (Branch 3.1)
**파일**: `prompt/dev-process-rapid-development.md`
- 30분 셋업, 15분 code-to-release
- tsx + tsup + Vitest + Biome 도구체인
- 3-tier LLM 모킹 (golden files → mock server → cache proxy)
- 1주 스프린트, <60초 테스트 스위트
- 사례: Sindre Sorhus 1000+ 패키지, Turborepo solo→Vercel 인수

### 2.6 Dev Workflow — Robust (Branch 3.2)
**파일**: `prompt/strategy-report-robust-development-process.md`
- 10-gate CI 파이프라인, 5-layer 테스트 피라미드
- VCR 패턴 LLM 녹화/재생, LLM-as-judge 3회 다수결
- 주간 릴리스 트레인, 80% 커버리지 바닥
- Nix Flakes 재현성, pino 구조화 로깅
- 8기능 26주 가능 (2주 선행 품질 인프라 투자)

### 2.7 Tech Debt — Minimized (Branch 4.1)
**파일**: `prompt/tech-debt-minimized-strategy.md`
- TypeScript strict + ESLint zero-warnings + 20% 스프린트 부채 할당
- 4단계 심각도 (S0-S3), 하드 캡
- 메타 품질: 부채 있는 생성기 = 부채 있는 출력
- 손익분기: Week 11 (이후 Minimized가 더 빠름)
- 22개 출처 인용 (InfoQ, MIT Sloan, Shopify Engineering, DORA)

### 2.8 Tech Debt — Practical (Branch 4.2)
**파일**: `prompt/tech-debt-pragmatic-strategy.md`
- 95/5 → 85/15 → 80/20 단계적 할당
- 월 2시간 "부채 수금" 세션
- 부채 변곡점: Month 12-14 (V1 내에서 안전)
- 사례: Instagram (3명, Django, 2B 유저, 절대 리라이트 안 함)
- 핵심: "부채는 도구. 현명하게 빌리고, 전략적으로 갚아라."

### 2.9 Theory Foundation — Modern (Branch 5.1)
**파일**: `prompt/theory-foundation-modern-2021-2026.md`
- ReAct (reasoning+acting), CoT, Constitutional AI 자기비판
- Anthropic composable agent 패턴, Claude Agent SDK 아키텍처
- MDA → AI 적응, Design by Contract → 문서 체인
- DevEx 3차원 프레임워크 (flow, feedback, cognitive load)
- **TOP 5 필수 이론**: ReAct, Composable Patterns, CoT+CAI, DbC, DevEx
- 학습 계획: 15-18일

### 2.10 Theory Foundation — Classical (Branch 5.2)
**파일**: `prompt/classical-theoretical-foundations-report.md`
- Information Hiding (Parnas 1972), Unix Philosophy (McIlroy 1978)
- GoF 패턴 (Factory, Strategy, Observer, Template Method)
- Traceability (Gotel & Finkelstein 1994) → SOT 체인 설계
- Specification Compiler (Aho 1986) → 7문서 파이프라인 = 중간 표현
- Cognitive Load (Sweller 1988) → 5-7 질문 최적화 근거
- **Oracle Problem** (Weyuker 1982) = 가장 어려운 테스트 과제
- Conway's Law → Solo founder = 자연스러운 모놀리스 (장점)

---

## 3. Phase 1 통합 (10개 Branch 교차 분석)

### 3.1 기술 선택 스펙트럼

```
Core Technology:
  Aggressive ←───[6/10]───→ Conservative
  Agent SDK+Structured Output    Direct REST+Handlebars
  → 양쪽 모두 Node.js LTS + Commander.js에 수렴

Architecture:
  Evolutionary ←───[5/10]───→ Big Bang
  ~25 파일, 필요시 추출           Clean Arch+DI+Plugin
  → Big Bang "조건부 YES", Evolutionary가 2-3 기능 더 배송

Dev Workflow:
  Rapid ←───[6/10]───→ Robust
  15분 릴리스, 스냅샷 테스트      주간 릴리스, 10-gate CI
  → AI 코드 품질 문제 감안 시 Robust가 더 안전

Tech Debt:
  Minimized ←───[4/10]───→ Practical
  20% 할당, Week 11 손익분기      5-10%, Month 12 변곡점
  → 핵심 모듈은 Minimized, 나머지 Practical

Theory:
  Modern ←───[5/10]───→ Classical
  ReAct, CoT, Agent SDK           Information Hiding, Compiler Theory
  → Classical 원칙 위에 Modern 기법 적용
```

### 3.2 절대 합의 (10/10 Branch)
1. **TypeScript + Node.js LTS**
2. **Commander.js + Inquirer.js** (CLI)
3. **JSON Schema** (문서 구조 검증)
4. **모듈러 모놀리스**
5. **파일 기반 상태 관리**
6. **Claude API (BYOK)**
7. **Next.js + Supabase + Stripe** (생성 템플릿)

### 3.3 최대 불일치 5개

| 불일치 | Branch A | Branch B |
|--------|----------|----------|
| LLM 통합 | Agent SDK + Structured Output | Direct REST + Handlebars |
| 아키텍처 투자 | 점진적 (~25 파일) | 선행 설계 (Clean Arch) |
| 릴리스 주기 | 15분 (매일) | 주간 (10-gate CI) |
| 부채 할당 | 5-10% (Practical) | 20% (Minimized) |
| 프롬프트 관리 | Zod 템플릿 Day 1 | 하드코딩 → 나중 추출 |

---

## 4. Phase 2: 4개 관점별 기술 토론

### 4.1 Discussion — Latest Tech First
- Cutting-edge 8/12 레이어 승리, Conservative 1개 (Ink), 동률 4개
- **5대 혁신 기술**: Structured Outputs, Prompt Caching, Agent SDK (선택적), Zod, Biome
- Ink V1 제외 (3/4 동의), Agent SDK 오케스트레이션만 사용
- 타임라인: Conservative 대비 +2주 (학습) but -1주 (생산성 향상)
- Solo founder 가능: YES (체계적 순서 학습 시)

### 4.2 Discussion — Stability First
- 기술별 안정성 스코어카드 (18개 기술 평가)
- **Tier S**: Node.js, TypeScript, Commander.js, Handlebars, Stripe, Ajv, ESLint+Prettier
- **Tier C (너무 새로움)**: Drizzle, Biome, Structured Outputs, Agent SDK
- Claude API = 유일한 심각한 외부 의존성 → 얇은 추상화 레이어 필수
- 3곳에서 새 기술이 오히려 안전: TypeScript strict, Structured Outputs (fallback 동반), Vitest
- "Ship boring technology. Win with product quality, not stack novelty."

### 4.3 Discussion — Speed First
- 체리피킹: Aggressive(파이프라인) + Conservative(CLI)
- **TOP 3 속도 향상**: Structured Outputs (-2~3주), Biome+tsx+Vitest (-50시간), Supabase Stripe Sync (-1~2주)
- 24/26주 가능 (2주 버퍼)
- 테스트: 40% critical-path (80테스트, <60초)
- 과잉 설계가 #1 속도 킬러 (Big Bang = 16-18주 before features)
- 1주 스프린트 (26회 course-correction vs 13회)

### 4.4 Discussion — Maintainability First
- 기술별 유지보수성 스코어카드 (20개 기술, 6차원 평가)
- **최고 유지보수성**: TypeScript strict (9.5), Zod (9.3), Vitest (8.8), pnpm (8.8)
- **최저 유지보수성**: Agent SDK (6.0), Handlebars (6.3)
- V2 준비도 매트릭스: Web GUI 차단 방지 = "Zero business logic in CLI" 절대 규칙
- LLMAdapter 인터페이스: 1-2시간 투자, Multi-LLM V2 경로 보장
- 20% 부채 할당 + import/no-restricted-paths 강제 = 2년 건강한 코드베이스

---

## 5. Phase 2 통합: 4개 관점 기술 선택 비교표

| 기술 | Latest | Stability | Speed | Maintain | 합의도 |
|------|--------|-----------|-------|----------|--------|
| TypeScript strict | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| Node.js LTS | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| Commander.js+Inquirer.js | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| Vitest | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| File-based state | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| NO Ink V1 | ✓ | ✓ | ✓ | ✓ | **4/4 ✅** |
| Structured Outputs | ✓ | △(fallback) | ✓ | ✓ | 3.5/4 |
| Prompt Caching | ✓ | △(최적화) | ✓ | ✓ | 3.5/4 |
| Zod | ✓ | — | ✓ | ✓ | 3/4 |
| Evolutionary Arch | — | ✓ | ✓ | ✓(+인터페이스) | 3/4 |
| Biome | ✓ | ✗ | ✓ | △(하이브리드) | 2.5/4 |
| Drizzle ORM | ✓ | ✗(Prisma) | ✓ | ✓ | 3/4 |
| Agent SDK | △ | ✗ | ✗ | ✗ | 0.5/4 |
| LLMAdapter 인터페이스 | — | ✓ | — | ✓ | 2/4 |

---

## 6. Phase 3: 3개 기술 시나리오 비교

### 6.1 Cutting Edge Scenario
**파일**: `prompt/technology-scenario-cutting-edge.md`
- 35+ 기술, Agent SDK 포함, 최대 역량
- 추천도: 7.5/10, **4x Challenging**
- 24주 + 2주 버퍼 (7.7%), 학습 5-6주
- API 비용: $0.17-$2.46/프로젝트, 운영 $320-$900/월
- V2 준비도: 높음 (Agent SDK + MCP 장점)
- 리스크: Agent SDK 결합(40%), 얇은 버퍼, solo burnout(35-45%)

### 6.2 Balanced-Tech Scenario ← **최종 선택**
**파일**: `prompt/technology-scenario-balanced-tech.md`
- 체리피킹: 보수적 CLI + 공격적 파이프라인
- 추천도: ~8.5/10, **4x Realistic**, 87% 신뢰도
- 23.5주 + 2.5주 버퍼 (9.6%), 학습 2-3주
- API 비용: $460-$840 총 6개월
- V2 준비도: Multi-LLM(9/10), Marketplace(8/10), Multi-Framework(7/10), Deploy(6/10), GUI(5/10)
- Day-1 인터페이스 2개: LLMAdapter, TemplateRegistry

### 6.3 Proven Stack Scenario
**파일**: `prompt/tech-scenario-proven-stack.md`
- 5년+ 검증 기술만, Structured Outputs 미사용
- 추천도: 8.5/10, **4x Realistic**, **95% 신뢰도**
- 20-22주 + 4-6주 버퍼 (15-23%), 학습 0-2주
- Private Alpha 2-6주 일찍 도달
- 11개 기술 명시적 거부 (Agent SDK, Structured Outputs, Zod, Biome 등)
- 희생: 2-5% JSON 오류율, 15-30% 높은 API 비용, 타입/스키마 이중 관리
- "Boring but alive" — Basecamp, Craigslist, Stripe, Shopify 사례

---

## 7. Phase 4: 최종 기술 로드맵 결정

### 선택: BALANCED-TECH

**선택 근거:**
- 5/5 평가 조건 충족 (Cutting Edge 3/5, Proven 4/5)
- 4x "Realistic" 팀 서명 (Cutting Edge는 4x "Challenging")
- 87% 신뢰도 + 2.5주 버퍼 (Proven의 95%보다 낮지만 충분)
- Structured Outputs + Zod의 기술적 이점이 Proven Stack의 안정성 이점을 상쇄
- Agent SDK 미사용으로 Cutting Edge의 핵심 리스크 회피

### 버린 시나리오 이유

**Cutting Edge 탈락:**
- 4x "Challenging" = solo founder에게 실패 확률 증가
- Agent SDK pre-1.0, 3/4 토론에서 거부
- 2주 버퍼(7.7%) 너무 위험
- 학습 5-6주가 첫 2개월 생산성 저해

**Proven Stack 차순위:**
- 매력적 (8.5/10, 95%, 4-6주 버퍼)
- 그러나: 2-5% JSON 오류율 × 7문서 = 누적 10-30% 파이프라인 오류
- BYOK 유저에게 4-10x 높은 비용 (Prompt Caching 미사용)
- "2026년 AI 도구에서 boring이 경쟁 우위인가?" — 불확실

---

## 8. 최종 기술 스택 상세

### CLI Tool (The Product Itself)

| 계층 | 기술 | 버전 | 선택 근거 |
|------|------|------|----------|
| Runtime | Node.js | 22 LTS | 15년+ 검증, 98% Fortune 500 |
| Language | TypeScript | 5.x (strict: true) | 12년+, 컴파일 타임 안전성 |
| CLI | Commander.js | v12+ | 13년+, 160M/주, 4/4 합의 |
| Prompts | Inquirer.js | v8 (LTS) | 12년+, 28M/주 |
| LLM | @anthropic-ai/sdk | latest | Claude API 공식 SDK |
| LLM Feature | Structured Outputs | GA | 100% 스키마 준수, Ajv fallback |
| LLM Feature | Prompt Caching | GA | 76-90% 비용 절감, 자동 |
| Schema | Zod | v3.x | 타입+검증+LLM 단일 소스 |
| Code Templates | Handlebars + EJS | stable | 14년+ 검증, 코드 스캐폴딩 |
| Build | tsup (prod) + tsx (dev) | latest | esbuild 기반, 제로 config |
| Package Mgr | pnpm | v9+ | 3x npm, strict node_modules |
| Lint | Biome (기본) + ESLint (경계 규칙) | latest | 56x 빠름 + boundary 강제 |
| Test | Vitest | v2+ | 10x Jest, TS 네이티브 |
| CI/CD | GitHub Actions + semantic-release | N/A | OSS 무료, 자동 버전관리 |
| State | File-based JSON/YAML | N/A | DB 불필요, 검사 가능 |

### Generated SaaS Template (What Users Get)

| 계층 | 기술 | 버전 | 선택 근거 |
|------|------|------|----------|
| Framework | Next.js | 15 (App Router) | 6M+/주, Vercel 레퍼런스 구현 |
| Database | Supabase | latest | Auth+DB+Realtime+Edge |
| ORM | Drizzle | latest | 7KB, SQL-native, 3/4 합의 |
| Payments | Stripe | latest | 14년+, 99.999% uptime |
| UI | shadcn/ui | latest | 65K+ stars, 코드 소유 |
| CSS | Tailwind CSS | v4 | utility-first, 5년+ 검증 |

### 아키텍처

```
saas-auto-builder/
├── src/
│   ├── cli/                    ← Thin adapter (Commander+Inquirer)
│   │   ├── commands/
│   │   └── display/
│   ├── core/
│   │   ├── conversation/       ← F1: 5-7 스마트 질문
│   │   ├── pipeline/           ← F2: 7문서 오케스트레이션
│   │   ├── propagation/        ← F4: 단방향 컨텍스트 전파
│   │   └── validation/         ← F8: 교차검증
│   ├── generators/
│   │   ├── prd/
│   │   ├── user-journey/
│   │   ├── trd/
│   │   ├── code-guidelines/
│   │   ├── ui-guidelines/
│   │   ├── information-architecture/
│   │   └── tasks/
│   ├── templates/
│   │   ├── registry.ts         ← Day-1 인터페이스
│   │   └── nextjs-supabase/    ← F3
│   ├── shared/
│   │   ├── llm-adapter/        ← Day-1 인터페이스 (LLMAdapter)
│   │   ├── schemas/            ← Zod 스키마 (7문서)
│   │   ├── config/
│   │   └── types/
│   └── licensing/              ← F6: Free/Paid
├── templates/                   ← EJS/Handlebars 코드 템플릿
├── test/
│   ├── fixtures/               ← Golden-file LLM 응답
│   └── *.test.ts
└── package.json
```

**의존 방향**: `cli → core → generators → shared` (ESLint boundary 강제)
**Day-1 인터페이스**: LLMAdapter (Multi-LLM V2), TemplateRegistry (마켓플레이스 V2)

### 개발 타임라인 (23.5주 + 2.5주 버퍼)

| 주차 | Feature/Task | 산출물 |
|------|-------------|--------|
| 1-2 | 인프라 + Zod 스키마 7개 | CLI 스켈레톤, CI/CD, 품질 게이트 |
| 3-5 | F1: 대화 엔진 | 5-7 스마트 질문 → 구조화된 의도 |
| 6-9 | F2: 7문서 파이프라인 | PRD→TRD→Tasks 순차 생성 |
| 10-12 | F3: Next.js 템플릿 | 동작하는 SaaS 스캐폴드 |
| 13-14 | F4: 컨텍스트 전파 | 단방향 문서 간 참조 |
| 15-16 | F5: 편집 가능 문서 | 수정 → 재전파 |
| 17-18 | F6: Free/Paid 경계 | 3프로젝트 제한 + 라이선스 |
| 19-20 | F7: 15분 첫 경험 | 온보딩 플로우 최적화 |
| 21-23.5 | F8: 교차검증 + 품질 강화 | 문서 간 일관성 검증 |
| 24-26 | 버퍼 + 베타 런치 | Pro $19/mo 런치 |

### 비용 분석 (6개월)

| 항목 | 비용 |
|------|------|
| Claude API (개발) | $44-$71 (Prompt Caching 적용) |
| 인프라 (GitHub, npm) | $0 (OSS) |
| 도메인 + 기타 | ~$50 |
| **총 개발 비용** | **$100-$150** |
| 유저당 API 비용 | $0.50-$2.00/세션 (BYOK) |

---

## 9. 위험 가정 TOP 5

| # | 위험 | 확률 | 영향 | 완화 |
|---|------|------|------|------|
| 1 | Claude API 가격/모델 변경 | 40% | High | LLMAdapter 추상화, 모델 버전 고정 |
| 2 | Structured Outputs 동작 변경 | 15% | Medium | Ajv fallback 경로 (Belt+Suspenders) |
| 3 | 7문서 품질이 기대 이하 | 30% | High | Constitutional AI 자기비판 + 인간 큐레이션 |
| 4 | Solo founder 번아웃 | 35% | Medium | 주 40시간 상한, F8 컷 옵션 |
| 5 | CLI 니치 너무 작음 (<200명) | 25% | Fatal | V2 Web GUI 아키텍처 Day-1 준비 |

---

## 10. 이론적 기초 요약

### 적용할 핵심 이론 (TOP 5)

| 이론 | 저자 | 적용 영역 |
|------|------|----------|
| Information Hiding | Parnas, 1972 | 모듈 경계 설계 (각 모듈이 하나의 "비밀"을 숨김) |
| Specification Compiler | Aho et al., 1986 | 7문서 파이프라인 = 중간 표현 체인 |
| Traceability | Gotel & Finkelstein, 1994 | SOT 체인 설계 (forward propagation) |
| Cognitive Load | Sweller, 1988 | 5-7 질문 최적화 (과부하 방지) |
| ReAct | Yao et al., 2022 | LLM 기반 문서 생성 (reasoning + acting) |

### 이론과 현실의 갭

- **ACID vs BASE**: 우리 문서 파이프라인은 "문서 일관성"이 필수 → ACID 원칙 적용
- **Oracle Problem**: "올바른 PRD"의 정답이 없음 → 부분 오라클 (스키마 검증 + 교차 일관성 + 인간 리뷰)
- **Conway's Law**: Solo founder → 자연스러운 모놀리스 = 장점 (의사소통 오버헤드 = 0)
- **No Silver Bullet (Brooks)**: LLM은 생산성 도구, 마법이 아님 — "문서 파이프라인"으로 포지셔닝

---

## 11. 추가 조사 필요 영역 (향후 심층조사 후보)

1. **LLM 프롬프트 엔지니어링 심층 설계**: 7개 문서 타입별 최적 프롬프트 전략
2. **Zod 스키마 상세 설계**: 7개 문서의 구체적 필드/타입 정의
3. **SOT 체인 데이터 플로우**: PRD→TRD→Tasks 간 구체적 전파 규칙
4. **경쟁사 기술 스택 분석**: Cursor, Lovable, Bolt.new의 실제 기술 선택
5. **Free/Paid 경계 최적화**: 전환 트리거 심리학 + 가격 탄력성
6. **AgenticWorkflow 인프라 재사용**: 구체적 모듈 매핑 + 절감 시간

---

## 12. 파일 인덱스

| 파일 | 유형 | 내용 |
|------|------|------|
| `prompt/Technology_Development_DeepDive_PRD_Teammate_Executable.md` | 프레임워크 | 기술 심층조사 10-Branch 프레임워크 (원본) |
| `prompt/tech-deep-dive-aggressive-cutting-edge.md` | Phase 1 | Branch 1.1: 공격적 기술 스택 |
| `prompt/technology-stack-conservative-analysis.md` | Phase 1 | Branch 1.2: 보수적 기술 스택 |
| `prompt/tech-deep-dive-evolutionary-architecture.md` | Phase 1 | Branch 2.1: 점진적 진화 아키텍처 |
| `prompt/architecture-big-bang-design-report.md` | Phase 1 | Branch 2.2: 초기 완성도 아키텍처 |
| `prompt/dev-process-rapid-development.md` | Phase 1 | Branch 3.1: 빠른 개발 프로세스 |
| `prompt/strategy-report-robust-development-process.md` | Phase 1 | Branch 3.2: 견고한 개발 프로세스 |
| `prompt/tech-debt-minimized-strategy.md` | Phase 1 | Branch 4.1: 기술 부채 최소화 |
| `prompt/tech-debt-pragmatic-strategy.md` | Phase 1 | Branch 4.2: 실용적 부채 관리 |
| `prompt/theory-foundation-modern-2021-2026.md` | Phase 1 | Branch 5.1: 최신 이론 (2021-2026) |
| `prompt/classical-theoretical-foundations-report.md` | Phase 1 | Branch 5.2: 고전 이론 (수십년) |
| `prompt/technology-scenario-cutting-edge.md` | Phase 3 | Cutting Edge 시나리오 (7.5/10) |
| `prompt/technology-scenario-balanced-tech.md` | Phase 3 | **Balanced-Tech 시나리오 (최종 선택)** |
| `prompt/tech-scenario-proven-stack.md` | Phase 3 | Proven Stack 시나리오 (8.5/10) |
| `prompt/RESEARCH-SYNTHESIS-tech-deep-dive-round2.md` | 종합 | **이 문서 — 2차 조사 전체 종합** |
