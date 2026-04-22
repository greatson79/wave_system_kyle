# Research Bridge — Sermon-Assistant 연구 에이전트 통합 프로토콜

## 개요

`/설교` 5단계 대화 프로세스의 2단계(본문 분석) 진입 시,
Sermon-Assistant-AgenticWorkflow의 11개 PhD급 전문 연구 에이전트를 **병렬 서브에이전트로 소환**하여
심층 연구 결과를 `/설교` 대화에 투입하는 통합 패턴이다.

### 설계 원칙

- **대화 주도권은 목사에게**: 연구 결과는 참고 자료이지, 설교 방향을 결정하지 않는다
- **병렬 실행으로 시간 절약**: 각 `/설교` 하위 단계 진입 전 관련 에이전트를 동시 소환
- **기본 활성화**: Research Bridge는 항상 자동 실행된다. "빠르게"를 명시할 때만 생략한다
- **에이전트 정의 직접 참조**: Sermon-Assistant 프로젝트의 `.md` 파일을 런타임에 읽어 프롬프트로 사용

---

## 에이전트 소스 경로

> 에이전트 목록과 소스 경로는 **`team-leader/rules/agent-registry.md`** (Sermon-Assistant 섹션)에서 관리한다.
> 기본 경로: `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/.claude/agents/`
> 이 경로의 에이전트 정의 파일(`.md`)을 Read tool로 읽어 프롬프트를 구성한다.
> 에이전트 정의가 변경되면 다음 소환 시 자동으로 최신 버전이 반영된다.

---

## 매핑 테이블: `/설교` 단계 ↔ 연구 에이전트

### 2-1 원어분석 ← Wave 1 + Wave 2 언어 전문가

| 에이전트 | 파일명 | 전문 영역 | 실행 |
|---------|--------|----------|------|
| **@original-text-analyst** | `original-text-analyst.md` | 히/헬 파싱, 형태론, 구문론, 담화분석, 사본비평 | 병렬 |
| **@manuscript-comparator** | `manuscript-comparator.md` | 번역본 비교, 사본 전통, 비평 장치 | 병렬 |
| **@keyword-expert** | `keyword-expert.md` | 핵심 단어 3-5개 심층 연구 (어원, 용례, 신학적 함의) | 병렬 |

> **통합 포인트**: 세 에이전트의 결과를 종합하여 "원어 통찰 목록"으로 정리한 후 목사에게 제시.
> 목사의 피드백을 반영하여 2-1 산출물 확정.

### 2-2 배경분석 ← Wave 1 + Wave 3 역사/문화 전문가

| 에이전트 | 파일명 | 전문 영역 | 실행 |
|---------|--------|----------|------|
| **@biblical-geography-expert** | `biblical-geography-expert.md` | 지리, 지형, 고고학, 기후/거리 | 병렬 |
| **@historical-cultural-expert** | `historical-cultural-expert.md` | 관습, 물질문화, 사회구조, 일상생활 복원 | 병렬 |
| **@historical-context-analyst** | `historical-context-analyst.md` | 저작 연대, Sitz im Leben, 고대 근동/헬레니즘 비교문헌 | 병렬 |

> **통합 포인트**: 세 에이전트의 결과를 종합하여 "배경 분석 요약"으로 정리한 후 목사에게 제시.
> 특히 "현대 독자가 놓치는 문화적 전제"를 강조.

### 2-3 우상분석 ← Wave 3 신학/문학 전문가

| 에이전트 | 파일명 | 전문 영역 | 실행 |
|---------|--------|----------|------|
| **@theological-analyst** | `theological-analyst.md` | 조직신학, 성경신학, 구속사, 언약신학 | 병렬 |
| **@literary-analyst** | `literary-analyst.md` | 장르, 문학 장치, 서사기법, 시적 기법, 저자 문체 | 병렬 |

> **통합 포인트**: 신학적 주제 + 문학적 장치를 종합한 후,
> `/설교` 고유의 **Tim Keller 우상 분석 프레임워크**(권력/승인/안전/쾌락)를 대화에서 적용.
> 에이전트 연구는 배경 자료이고, 우상 식별은 목사와의 대화에서 도출.

### 2-4 종합통찰 ← Wave 2 + Wave 4 구조/수사학 전문가

| 에이전트 | 파일명 | 전문 영역 | 실행 |
|---------|--------|----------|------|
| **@structure-analyst** | `structure-analyst.md` | 문단 구분, 교차대구, 포용구조, 논증/서사 흐름 | 병렬 |
| **@parallel-passage-analyst** | `parallel-passage-analyst.md` | 정경 내 상호텍스트, 공관 비교, 구약→신약 인용 | 병렬 |
| **@rhetorical-analyst** | `rhetorical-analyst.md` | 수사학적 구조, 설득 전략, 청중 반응 재구성 | 순차 (문학분석 후) |

> **통합 포인트**: 구조·평행본문·수사학 분석을 종합하여 CMT·FCF·HP 도출의 증거 기반을 제공.
> 최종 CMT·FCF·HP는 목사와의 대화에서 확정. 에이전트는 "제안"만 한다.

---

## 지능적 에이전트 선택 (Context-Aware Selection)

"분석에 필요한 내용만 불러온다" — 11개를 항상 전부 실행하지 않는다.
Sermon Agent는 본문 특성과 목사의 필요를 판단하여 **최소 유효 에이전트**를 선택한다.

### 판단 기준

| 본문 특성 | 핵심 에이전트 | 간소화 가능 |
|---------|-----------|------------|
| **서사 본문** (창세기, 복음서 사건, 사도행전) | literary-analyst, structure-analyst, historical-cultural-expert | keyword-expert 1-2개로 축소 |
| **교훈 서신** (로마서, 빌립보서, 에베소서) | keyword-expert, theological-analyst, rhetorical-analyst | biblical-geography 최소화 |
| **예언서** (이사야, 예레미야, 소선지서) | original-text-analyst, historical-context-analyst, theological-analyst | structure-analyst 선택적 |
| **시편/지혜서** | literary-analyst, keyword-expert, rhetorical-analyst | historical-context 선택적 |
| **짧은 단락** (3절 이하) | original-text-analyst, keyword-expert | structure-analyst 불필요 |
| **배경이 핵심인 본문** (사회적 갈등, 절기, 지명) | biblical-geography-expert, historical-cultural-expert, historical-context-analyst | - |
| **절기 설교** (부활절, 성탄절, 성령강림절) | theological-analyst, parallel-passage-analyst | 원어 분석 간소화 가능 |

### 자동 판단 절차

```
1단계 상황파악 완료 후:
  [장르 감지] → 위 테이블에서 "핵심 에이전트" 세트 결정
  [목사에게 제안] →
    "이 본문은 {장르}입니다.
     연구 브릿지를 사용하신다면 다음 에이전트를 추천드립니다:
     - {추천 에이전트 목록}
     (전체 11개 / 추천 세트 / 직접 선택 / 생략)"
  [목사 선택 대로 실행]
```

### 필요 시 추가 호출 (On-Demand)

대화 중 목사가 더 깊은 분석이 필요하다고 판단되면, 해당 에이전트를 **즉시 추가 소환**할 수 있다:
- "원어를 좀 더 봐야 할 것 같은데요" → `@keyword-expert` 추가 소환
- "이 본문의 문화 배경이 중요할 것 같아요" → `@historical-cultural-expert` 추가 소환
- 어느 단계에서든 필요한 에이전트를 그 자리에서 호출하는 것이 허용된다

---

## 확장 에이전트 (설교 준비 전 단계 지원)

2단계 연구 에이전트(SA-1~11) 외에, **3~4단계 설교 작업**에도 협업 가능한 에이전트가 있다.
필요 여부는 대화 흐름을 보고 Sermon Agent가 판단하여 제안한다.

| ID | 에이전트 | 파일명 | 협업 시점 | 역할 |
|----|---------|--------|----------|------|
| SA-12 | **@message-synthesizer** | `message-synthesizer.md` | 2-4 종합통찰 이후 | 연구 결과 → Big Idea / CMT 종합 보조 |
| SA-13 | **@outline-architect** | `outline-architect.md` | 4단계 구조설계 진입 시 | 설교 아웃라인 초안 제안 |
| SA-14 | **@research-synthesizer** | `research-synthesizer.md` | 연구 결과 전체 수신 후 | 11개 연구 결과를 2000자로 압축 |

### 확장 에이전트 활성화 조건

```
SA-12 (@message-synthesizer):
  - 2-4 단계 종합 시 CMT/FCF/HP 도출에 막히거나
  - 목사가 "Big Idea를 정리해달라"고 요청할 때
  - 연구 결과가 많아 핵심 추출이 필요할 때

SA-13 (@outline-architect):
  - 4단계 구조설계 진입 시 목사 요청 있을 때
  - "아웃라인 초안을 먼저 보여줘" 요청 시
  - Mode A/B/C 결정 후 구체적 뼈대 설계 지원

SA-14 (@research-synthesizer):
  - 전체 11개 에이전트 결과 수신 후
  - 연구 결과가 너무 많아 핵심 요약이 필요할 때
  - "이어서" 재개 시 이전 연구 컨텍스트 복원용
```

> **주의**: SA-12~14는 `목사와의 대화 주도권`을 빼앗지 않는다.
> 항상 "초안 제안"이며, 최종 결정은 목사가 한다.

---

## 실행 프로토콜

### 활성화 조건

> ⭐ **기본값 변경**: Research Bridge는 항상 자동 활성화된다. 생략을 원할 경우에만 명시적으로 요청한다.

```
/설교 [본문]           → 1단계 상황파악 완료 즉시 Research Bridge 자동 활성화 (기본값)
/설교 [본문] 빠르게    → 연구 브릿지 없이 직접 분석 (예외적 생략)
/설교 [본문] 이어서    → 기존 연구 결과 파일 존재 시 자동 로드
```

### 단계별 실행 흐름

```
1단계 상황파악 (대화)
  ↓
  ┌─ 연구 브릿지 활성화 여부 확인 ─┐
  │  "심층 연구를 함께 진행할까요?" │
  │  [예 / 아니오 / 선택적]        │
  └────────────────────────────────┘
  ↓ (예)
  === 2-1 연구 에이전트 소환 ===
  Agent(@original-text-analyst) ─┐
  Agent(@manuscript-comparator)  ├→ 병렬 실행 (background)
  Agent(@keyword-expert)        ─┘
  ↓ 결과 수신
  목사에게 연구 결과 요약 제시
  ↓
  2-1 원어분석 대화 (연구 결과 + 목사 통찰)
  → 산출물: 2-1_원어분석.md

  === 2-2 연구 에이전트 소환 ===
  Agent(@biblical-geography-expert)  ─┐
  Agent(@historical-cultural-expert)  ├→ 병렬 실행
  Agent(@historical-context-analyst) ─┘
  ↓ 결과 수신
  2-2 배경분석 대화
  → 산출물: 2-2_배경분석.md

  === 2-3 연구 에이전트 소환 ===
  Agent(@theological-analyst) ─┐
  Agent(@literary-analyst)    ─┘→ 병렬 실행
  ↓ 결과 수신
  2-3 우상분석 대화 (+ Keller 프레임워크)
  → 산출물: 2-3_우상분석.md

  === 2-4 연구 에이전트 소환 ===
  Agent(@structure-analyst)          ─┐
  Agent(@parallel-passage-analyst)   ─┘→ 병렬 실행
  ↓ 결과 수신
  Agent(@rhetorical-analyst)          → 순차 실행 (문학분석 결과 의존)
  ↓ 결과 수신
  2-4 종합통찰 대화 (CMT · FCF · HP 도출)
  → 산출물: 2-4_종합통찰.md

  3~5단계: 축적된 연구 기반으로 정상 대화 진행
```

### 에이전트 소환 프롬프트 구성법

> 상세 프롬프트 구성 패턴: **`team-leader/rules/agent-protocol.md`** 참조
> - 패턴 B (크로스 폴더 연구 에이전트): 병렬 소환 시 사용
> - 패턴 C (의존성 있는 순차 에이전트): SA-11 수사학분석 소환 시 사용

각 서브에이전트 소환 시, 다음 3요소를 결합하여 Agent 도구 프롬프트를 구성한다:

```
1. 에이전트 정의 (Read → agent-registry.md 소스 경로의 .md 파일 전문)
2. GRA-Lite 자기검증 규칙 (아래 §GRA-Lite 참조)
3. 본문 지정 + 출력 경로

Agent(
  prompt = "[에이전트 정의] + [GRA-Lite] + [본문·출력 지시]",
  run_in_background = true,  # 병렬 소환
  description = "@{에이전트명} {본문} 분석"
)
```

---

## GRA-Lite: 간소화된 환각 방지 규칙

Sermon-Assistant의 전체 GRA(3계층 방화벽 + SRCS 4축 + GroundedClaim YAML)는
코드 인프라(`_sermon_lib.py`) 없이 사용할 수 없다.
대신 **에이전트 자기검증 + 목사 검토**의 2계층으로 대체한다.

### 계층 1: 에이전트 자기검증 (프롬프트에 포함)

| 규칙 | 설명 |
|------|------|
| **출처 필수** | 사실적/언어적 주장은 반드시 출처 명시 (BDB, BDAG, TDNT 등) |
| **절대 표현 금지** | "모든 학자가 동의", "100% 확실" 등 BLOCK |
| **헤지 표현 필수** | 확신도 낮으면 "likely", "arguably", "일부 학자들은" 사용 |
| **시대/지역 명시** | 문화적 주장은 시대와 지역을 특정 |
| **미검증 표시** | 직접 확인 불가한 인용은 [미검증] 태그 |

### 계층 2: 목사 검토 (대화에서 수행)

| 검토 항목 | 대화 시점 |
|----------|----------|
| 연구 결과가 본문 원의와 부합하는가 | 각 2-N 단계 대화 시작 시 |
| 신학적으로 문제되는 주장이 있는가 | 목사가 직접 판단 |
| 출처가 신뢰할 만한가 | 필요 시 확인 요청 |

> **GRA-Lite의 한계 인정**: 코드 기반 자동 검증(SRCS 점수화, Cross-Validation Gate)이 없으므로,
> 에이전트가 자신감 있게 틀린 주장을 할 수 있다.
> 이 한계는 **목사의 신학적 판단력**으로 보완된다 — 이것이 "대화형"의 강점이다.

---

## 산출물 저장 구조

연구 브릿지 사용 시, 연구 결과를 별도 폴더에 보존한다:

```
output/{월}/{주차}주차/{날짜}_{절기}_{본문}/
├── research/                          ← 연구 브릿지 결과 (NEW)
│   ├── 01-원어분석-original-text.md    ← @original-text-analyst
│   ├── 02-번역사본비교.md              ← @manuscript-comparator
│   ├── 03-핵심단어연구.md              ← @keyword-expert
│   ├── 04-성경지리.md                  ← @biblical-geography-expert
│   ├── 05-역사문화배경.md              ← @historical-cultural-expert
│   ├── 06-역사적맥락.md                ← @historical-context-analyst
│   ├── 07-신학분석.md                  ← @theological-analyst
│   ├── 08-문학분석.md                  ← @literary-analyst
│   ├── 09-구조분석.md                  ← @structure-analyst
│   ├── 10-평행본문.md                  ← @parallel-passage-analyst
│   └── 11-수사학분석.md                ← @rhetorical-analyst
├── 1_상황파악.md
├── 2-1_원어분석.md                     ← 연구 + 대화 종합
├── 2-2_배경분석.md
├── 2-3_우상분석.md
├── 2-4_종합통찰.md
├── 3_내용전개.md
├── 4_구조설계.md
└── 5_원고.md
```

> `research/` 폴더는 에이전트 원본 결과를 보존한다.
> `2-N_*.md` 파일은 연구 결과 + 목사 대화를 종합한 최종 산출물이다.

---

## 이어서 작업 (`/설교 [본문] 이어서`) 호환

연구 브릿지는 기존 이어서 메커니즘과 호환된다:

1. `research/` 폴더 존재 시 → "이전 심층 연구가 있습니다" 안내
2. 해당 단계의 연구 파일을 자동 로드
3. 연구를 다시 실행하지 않고 기존 결과를 대화에 사용

---

## 선택적 실행

목사가 모든 에이전트를 원하지 않을 수 있다. 선택 옵션:

| 옵션 | 설명 |
|------|------|
| `/설교 [본문] 심층` | 전체 11개 에이전트 |
| `/설교 [본문] 심층 원어만` | 2-1 에이전트만 (3개) |
| `/설교 [본문] 심층 배경만` | 2-2 에이전트만 (3개) |
| `/설교 [본문] 심층 신학만` | 2-3 에이전트만 (2개) |
| `/설교 [본문] 심층 구조만` | 2-4 에이전트만 (3개) |
| `/설교 [본문]` | 연구 브릿지 없이 기존 방식 |

---

## 실행 시간 예상

| 단계 | 에이전트 수 | 예상 시간 | 비고 |
|------|-----------|----------|------|
| 2-1 연구 | 3개 병렬 | 2-4분 | WebSearch 포함 |
| 2-2 연구 | 3개 병렬 | 2-4분 | WebSearch 포함 |
| 2-3 연구 | 2개 병렬 | 2-3분 | |
| 2-4 연구 | 2개 병렬 + 1개 순차 | 3-5분 | 수사학은 문학 후 |
| **전체** | **11개** | **약 10-15분** | 대화 시간 별도 |

---

## 목사에게 연구 결과 제시 형식

각 하위 단계 진입 시 연구 결과를 다음 형식으로 제시한다:

```
📖 [Research Bridge] 2-1 원어분석 심층 연구 완료

3개 전문 에이전트가 분석한 결과를 요약합니다:

━━━ @original-text-analyst ━━━
[요약 3-5문장]
• 핵심 발견 1
• 핵심 발견 2

━━━ @manuscript-comparator ━━━
[요약 3-5문장]
• 핵심 발견 1
• 핵심 발견 2

━━━ @keyword-expert ━━━
[요약 3-5문장]
• 핵심 발견 1
• 핵심 발견 2

━━━━━━━━━━━━━━━━━━━━━━━━━
전체 연구 원문: research/ 폴더에 저장됨

이 연구 결과를 바탕으로 2-1 원어분석 대화를 시작하겠습니다.
특별히 더 깊이 다루고 싶은 부분이 있으신가요?
```

---

## 제한사항

| 항목 | Sermon-Assistant 전체 | Research Bridge |
|------|---------------------|-----------------|
| GRA 3계층 방화벽 | 코드 검증 (`_sermon_lib.py`) | **에이전트 자기검증 + 목사 검토** |
| SRCS 4축 평가 | 자동 점수화 (CS/GS/US/VS) | **없음** |
| Cross-Validation Gate | 에이전트 간 모순 자동 감지 | **없음** (목사가 판단) |
| GroundedClaim YAML | 구조화된 주장 스키마 | **비구조화 마크다운** |
| 환각 방지 강도 | 높음 (3계층 자동화) | **중간** (1계층 자기검증) |

> 이 한계는 의도적이다. 완전한 GRA를 원하면 Sermon-Assistant 프로젝트에서 직접 실행해야 한다.
> Research Bridge의 가치는 **깊이 있는 연구 + 대화형 설교 준비의 결합**에 있다.
