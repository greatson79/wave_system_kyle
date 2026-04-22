# GPTs & Gems 만들기 강의 개요
> **최종 업데이트**: 2026년 3월 22일 기준 최신 모델 반영
> **강의 목적**: Agentic Workflow를 위한 기초 역량 구축
> **대상**: AI 도구 활용에 관심 있는 일반인 ~ 중급 사용자
> **NotebookLM**: [gpts&gems 만들기 강의](https://notebooklm.google.com/notebook/95cc457e-f723-402c-899c-1e30655eb447)

---

## 현재 플랫폼 최신 현황 (2026년 3월 기준)

### OpenAI ChatGPT
| 항목 | 내용 |
|------|------|
| 최신 모델 | **GPT-5.4** (Thinking/Pro), GPT-5.3 Instant |
| 소형 모델 | GPT-5.4 mini, GPT-5.4 nano |
| 모델 중단 | GPT-4o → 2026년 4월 3일 완전 퇴역 |
| GPTs 기반 모델 | GPT-5 시리즈 (Custom GPTs 내부에서 자동 적용) |

### Google Gemini
| 항목 | 내용 |
|------|------|
| 최신 모델 | **Gemini 3.1 Pro**, Gemini 3 Flash (기본 모델) |
| 심층 사고 | Gemini 3 Deep Think |
| 안정화 모델 | Gemini 2.5 Flash/Pro (GA, 프로덕션용) |
| Gems 기본 모델 | 무료: Gemini 2.5 Flash / 유료: Gemini 3 |

### 요금제 비교
| 구분 | ChatGPT | Gemini |
|------|---------|--------|
| 무료 | GPT-5.4 제한적 사용, GPTs 사용만 가능(생성 불가) | Gemini 2.5 Flash, Gems 생성 가능 |
| 기본 유료 | Go $8/월 (GPT-5.2 Instant) | - |
| 표준 유료 | **Plus $20/월** (GPTs 생성 가능) | **AI Pro $19.99/월** (Gemini 3, 1,000 AI 크레딧) |
| 프리미엄 | Pro $200/월 (무제한) | AI Ultra $124.99/3개월 (Gemini 3 Pro, 25,000 크레딧) |

---

## Part 1: Custom GPTs 만들기 (OpenAI)
> **소요시간**: 약 40분 (강의 20분 + 실습 20분)

### 1.1 GPTs란 무엇인가?
- ChatGPT를 특정 목적에 맞게 커스터마이징한 나만의 AI 비서
- 코딩 없이 대화형 인터페이스(GPT Builder)로 생성
- GPT Store를 통해 전 세계에 공유/배포 가능
- **요구 사항**: ChatGPT Plus($20/월) 이상 구독 필요 (사용만은 무료 가능)

### 1.2 GPT Builder 접근 방법 및 두 가지 제작 모드

**접근 경로:**
- `chatgpt.com/create`로 직접 접속
- 또는 좌측 사이드바 → "Explore GPTs" → "Create" 클릭

**두 가지 제작 모드:**

| 모드 | 설명 | 적합 대상 |
|------|------|-----------|
| **Create (대화형 빌더)** | 만들고 싶은 챗봇의 목적을 일상어로 설명하면 ChatGPT가 이름, 프로필 사진, 기본 지침을 자동 생성 | 초보자, 아이디어 구체화 단계 |
| **Configure (수동 설정)** | Instructions(최대 8,000자), Knowledge, Capabilities 등을 직접 세밀하게 제어 | 경험자, 전문가 수준 커스터마이징 |

> **팁**: Create로 초안을 잡고, Configure에서 세부 조정하는 것이 가장 효율적

### 1.3 GPT 구성 5대 요소 ★

#### ① Instructions (지침) — "AI의 설계도"
- GPT의 역할, 성격, 행동 방식, 제한 조건을 정의하는 **핵심 설계도**
- 최대 약 **8,000자** 작성 가능
- 모든 대화에 적용되어 GPT의 톤, 구조, 의사결정을 안내

**Instructions 작성 4대 원칙:**

| 원칙 | 설명 | 예시 |
|------|------|------|
| **긍정적 지시어** | "Y를 하지 마라" 대신 **"X를 해라"** | "항상 출처를 밝혀라" (O) vs "출처 없이 답하지 마라" (X) |
| **명시적 단계 구조** | 복잡한 워크플로우는 "X 상황 발생 → Y 수행" 형태로 | "사용자가 코드를 요청하면 → 먼저 언어를 확인하라" |
| **시각적 구분** | 헤딩(Headings)과 목록(Lists)으로 우선순위 구분 | 섹션별 구분자(Delimiters) 활용 |
| **구체적 예시 포함** | 허용/불허 출력의 짧은 예시를 지침 내에 직접 포함 | "좋은 응답 예시: ... / 나쁜 응답 예시: ..." |

**예시:**
```
# 역할
당신은 한국어 문법 교정 전문가입니다.

# 행동 규칙
- 사용자의 글을 받으면 문법 오류를 찾아 수정합니다
- 수정 이유를 간결하게 설명합니다
- 존댓말을 사용합니다

# 제한사항
- 원문의 의미를 변경하지 않습니다
- 문체나 스타일은 유지합니다

# 출력 형식
1. 원문 → 수정문 비교
2. 수정 이유 (간결하게)
```

#### ② Knowledge (지식) — "AI의 참고 자료"
- GPT가 참조할 파일 업로드 (최대 **20개** 파일)
- PDF, Word, 텍스트, CSV, 스프레드시트, 이미지 등 지원
- 업로드한 파일을 영구적인 지식 기반(Knowledge Base)으로 활용 (RAG 방식)
- **Knowledge는 나의 GPT를 다른 GPT와 차별화하는 가장 중요한 요소**
- **활용 예**: 회사 매뉴얼, 제품 카탈로그, FAQ, SOP 문서, 연구 자료

#### ③ Capabilities (기능) — "AI의 도구 상자"

| 기능 | 설명 |
|------|------|
| **Web Search** | 실시간 인터넷 검색 후 최신 정보 제공 |
| **Canvas** | 문서/코드 협업 공간에서 공동 작업 |
| **DALL·E Image Generation** | AI 이미지 생성 모델로 이미지 생성 |
| **Code Interpreter & Data Analysis** | 내장 파이썬으로 코드 실행, 데이터 분석, 차트 생성 |

> GPT별로 필요한 기능만 ON/OFF 가능

#### ④ Actions (액션) — "AI의 외부 연결 통로" ★★★

> **이것이 GPTs의 가장 강력한 기능이자, Agentic Workflow의 출발점!**

**Actions의 작동 원리 (Function Calling):**
1. 사용자가 자연어로 질문
2. GPT가 어떤 API 호출이 필요한지 **자동 판단**
3. 자연어를 API가 요구하는 **JSON 형식으로 자동 변환**
4. API 호출 실행 → 결과를 자연어로 반환

**Actions 설정 3대 핵심 요소:**

| 요소 | 설명 |
|------|------|
| **OpenAPI 스키마** | API의 Endpoint, Parameter, 작동 설명을 정의. URL 입력 시 자동 임포트 가능 |
| **인증(Authentication)** | None(없음) / API Key / OAuth 중 선택 |
| **개인정보 정책 URL** | Store 배포 시 필수. 데이터 처리 방침 문서 링크 |

**Instructions와 Actions 연동 팁:**
```
Instructions에 반드시 다음과 같이 명시:
"[상황] 발생 시, actions의 [Action Name]을 이용해 [작업 지시]를 합니다"

예: "사용자가 날씨를 물으면, actions의 WeatherAPI를 이용해 해당 도시의 현재 날씨를 조회합니다"
```

**Actions 활용 사례:**
- CRM 데이터 조회 (예: Salesforce)
- 프로젝트 관리 (예: JIRA 티켓 생성)
- 자동화 미들웨어 연결 (Zapier, Make, n8n)
- 검색 API 호출 (네이버 검색, Google 검색)
- 이메일 전송, 데이터베이스 조회

#### ⑤ Prompt Starters (대화 시작 예시)
- 사용자가 바로 클릭해서 시작할 수 있는 예시 질문
- 현실적이고 가치 있는 프롬프트로 GPT의 사용 방법을 안내
- 최대 노출: PC 4개, 모바일 2개
- 3~4개 설정 권장

### 1.4 실습: "나만의 업무 비서 GPT" 만들기
```
[실습 순서]
Step 1: chatgpt.com → Explore GPTs → Create (또는 chatgpt.com/create)
Step 2: Create 탭에서 목적을 자연어로 설명 → 자동 설정 생성
Step 3: Configure 탭으로 이동 → Instructions 직접 수정 (역할 + 톤 + 제한 + 출력 형식)
Step 4: Knowledge에 참고 파일 1~2개 업로드
Step 5: Capabilities 중 필요한 기능 ON
Step 6: Prompt Starters 3~4개 작성
Step 7: 우측 Preview 창에서 실시간 테스트 → 피드백 반영하여 Instructions 수정
Step 8: Save → 공유 설정 (Only me / Only people with a link / Public)
```

### 1.5 (심화) Actions 실습 — 외부 API 연동
```
[Actions 설정 순서]
Step 1: Configure 탭 → "Create new action" 클릭
Step 2: Authentication 방식 선택 (None / API Key / OAuth)
Step 3: OpenAPI 스키마 입력 (직접 작성 또는 URL 자동 임포트)
Step 4: Privacy Policy URL 입력
Step 5: Instructions에 Action 호출 조건 명시
Step 6: Preview에서 테스트 → 디버깅
```

---

## Part 2: Gemini Gems 만들기 (Google)
> **소요시간**: 약 35분 (강의 15분 + 실습 20분)

### 2.1 Gems란 무엇인가?
- Gemini를 특정 역할/목적에 맞게 커스터마이징한 AI 전문가
- 반복 작업 자동화, 전문 지식 활용에 최적화
- Google Workspace(Gmail, Docs, Drive 등)와 긴밀한 네이티브 통합
- **핵심 장점**: 무료 Gmail 계정으로도 Gems 생성 가능!
- 텍스트 생성기가 아닌 **"논리 엔진(Logic Engine)"** — 다음 행동을 예측하고 실행하는 미니 앱

### 2.2 Gem 생성 접근 방법

| 플랫폼 | 생성/수정/삭제 | 사용 |
|--------|:---:|:---:|
| Gemini 웹 앱 | O | O |
| Gemini 모바일 앱 | X | O |

**접근 경로:**
- gemini.google.com → 좌측 "Gem 관리자" → "+ 새 Gem 만들기"

**두 가지 제작 방법:**

| 방법 | 설명 |
|------|------|
| **Magic Wand (AI 자동 확장)** | 1~2줄 목표 입력 → 연필/별 아이콘 클릭 → Gemini가 전문가 수준 지침으로 자동 확장 |
| **수동 작성** | Instructions 박스에 직접 상세 지침 작성 |

> **Magic Wand 팁**: "프롬프트 엔지니어처럼 쓰는 법"을 배우는 교육 도구로도 활용 가능. 마음에 안 들면 되돌리기(Undo) 가능

### 2.3 사전 제작 Gems 활용 (빠른 시작!)

처음부터 새로 만드는 것이 부담스럽다면 Google 제공 템플릿을 활용:

| 기본 Gem | 용도 |
|----------|------|
| Brainstormer (브레인스토머) | 아이디어 발상 |
| Career Guide (커리어 가이드) | 진로/경력 상담 |
| Coding Partner (코딩 파트너) | 코드 작성/디버깅 |
| Learning Coach (학습 코치) | 학습 계획/교육 |
| Writing Editor (작문 에디터) | 글쓰기 교정/편집 |

**활용법:**
1. Gem 관리자에서 원하는 기본 Gem 우측 ⋮ 메뉴 → "사본 만들기(Make a copy)"
2. 복제된 Gem의 이름 변경
3. 지침에 나만의 추가 조건/역할/톤 수정
4. 저장 → 바로 사용

### 2.4 Gem 구성 핵심 요소 — PTCF 프레임워크 ★

GPTs와 달리 Gems는 **단일 "Instructions" 입력란**을 사용합니다.
고품질 결과를 위해 **PTCF 프레임워크**를 활용합니다:

| 요소 | 의미 | 작성 내용 | 예시 |
|------|------|-----------|------|
| **P** | Persona (페르소나) | AI의 역할, 톤, 전문성 | "너는 15년 차 SaaS 전문 B2B 마케팅 전략가이다" |
| **T** | Task (과제) | 수행할 주요 목적/행동 | "블로그 초안을 검토하고 명확성과 설득력을 높여라" |
| **C** | Context (맥락) | 제약 조건, 배경, 대상 | "주 독자는 바쁜 CTO이므로 전문 용어를 피해라" |
| **F** | Format (형식) | 원하는 출력 형태 | "먼저 피드백을 글머리로, 그 다음 전체 마크다운 재작성" |

**예시 (PTCF 적용):**
```
[Persona]
당신은 SNS 마케팅 전문 카피라이터입니다. 트렌디하고 친근한 톤을 사용합니다.

[Task]
인스타그램 캡션을 작성합니다.

[Context]
- 타겟: 20~30대 한국 여성
- 브랜드 톤: 밝고 긍정적
- 이모지를 적절히 활용합니다

[Format]
- 캡션 본문 (3~5문장)
- 해시태그 5개 (항상 포함)
- 한국어로 작성
```

### 2.5 지식(Knowledge) 파일 업로드

**파일 업로드 사양:**

| 파일 유형 | 지원 형식 | 제한 |
|-----------|-----------|------|
| 문서 | PDF, DOCX, TXT, HTML | 최대 100MB 또는 2,000페이지 |
| 스프레드시트 | XLSX, CSV | 최대 20MB 또는 1,000,000셀 |
| 프레젠테이션 | PPTX | 최대 35MB 또는 ~500슬라이드 |
| 오디오 | MP3, WAV | 지원 |
| Gem당 최대 | - | **10개 파일** |

> **중요 팁**: 지침이 길어지면 Gem이 파일을 무시할 수 있음 → 지침 **첫 줄**에 `"답변하기 전에 반드시 첨부된 파일을 먼저 참조하라"` 명시!

### 2.6 Google Drive 연동 — "실시간 동기화" ★★★

> **이것이 Gems의 가장 강력한 차별점!**

**정적 파일 업로드 vs Drive 동적 동기화:**

| 비교 | 일반 파일 업로드 | Google Drive 연동 |
|------|:---:|:---:|
| 업데이트 반영 | 수동 재업로드 필요 | **자동 실시간 반영** |
| 연결 대상 | 로컬 파일 | Google Docs, Sheets, Slides |
| 사용 시나리오 | 변하지 않는 참고 자료 | 자주 변경되는 문서 |

**활용 예:**
- Google Sheet에 프로젝트 마감일 저장 → Sheet 수정 시 Gem이 자동으로 새 마감일 인식
- 브랜드 가이드라인 Docs 연결 → 가이드라인 변경 시 Gem 자동 반영
- 재고 목록 Sheet 연결 → 재고 변동 실시간 반영

> **주의**: Drive 연동이 "까다로울(finicky)" 수 있음 — Gem이 연결된 파일 외의 정보를 참조하는 경우 발생 가능

### 2.7 Google Extensions 통합

| Extension | 기능 |
|-----------|------|
| Google Workspace | Gmail, Docs, Drive, Calendar, Sheets 연동 |
| YouTube | 영상 검색/요약 |
| Google Maps | 장소/경로 검색 |
| Google Flights | 항공편 검색 |
| Google Hotels | 숙소 검색 |

> ⚠️ **핵심 차이**: 이것들은 Google이 제공하는 **사전 빌트 통합**이며, 외부 API를 직접 연동하는 GPTs Actions과는 근본적으로 다름

### 2.8 Gems 공유 — 팀 자산화

| 공유 수준 | 권한 |
|-----------|------|
| **Viewer (뷰어)** | Gem 사용 + 지침/파일 열람 (수정 불가) |
| **Editor (편집자)** | 지침 수정 + 파일 추가/삭제 + Gem 삭제 가능 |

- Google Drive 파일 공유처럼 이메일로 링크 공유
- 파일이 포함된 Gem 공유 시 해당 Drive 파일 접근 권한도 함께 부여
- **팀 활용 예**: 마케팅팀 전체가 "브랜드 페르소나 Gem"을 공유 → 브랜드 일관성 유지
- 관리자가 Admin Console에서 Gems 공유 정책 제어 가능

### 2.9 실습: "나만의 전문가 Gem" 만들기
```
[실습 순서]
Step 1: gemini.google.com 접속
Step 2: 좌측 "Gem 관리자" → "+ 새 Gem 만들기"
Step 3: 이름 설정 (목적이 드러나는 이름)
Step 4-A: (초보) Magic Wand — 1~2줄 목표 입력 → 별 아이콘 클릭 → 자동 확장된 지침 검토/수정
Step 4-B: (중급) PTCF 프레임워크로 직접 작성 (Persona → Task → Context → Format)
Step 5: Knowledge에 파일 업로드 (최대 10개) 또는 Drive 문서 연결
Step 6: 우측 Preview 창에서 테스트 (자동 저장 안 됨 → 반드시 Save 클릭!)
Step 7: 수정 및 최적화 반복
Step 8: (선택) 팀원에게 공유
```

---

## Part 3: GPTs vs Gems 심화 비교 분석
> **소요시간**: 약 20분

### 3.1 핵심 비교표

| 비교 항목 | GPTs (OpenAI) | Gems (Google) |
|-----------|--------------|---------------|
| **기반 모델** | GPT-5 시리즈 (5.3/5.4) | Gemini 3 Flash / 3.1 Pro |
| **생성 비용** | Plus $20/월 이상 필요 | **무료 가능** (Gmail 계정) |
| **지식 파일** | 최대 20개 | 최대 10개 |
| **파일 동기화** | 수동 재업로드 | **Google Drive 자동 동기화** ★ |
| **외부 API 연동** | **Actions (OpenAPI 스키마)** ★ | 불가 |
| **지침 작성 보조** | Create 탭 대화형 | **Magic Wand 자동 확장** |
| **생태계 통합** | Zapier, Make, n8n 등 | Google Workspace 네이티브 |
| **마켓플레이스** | GPT Store (활성, 수천 개) | 없음 |
| **공유 방식** | 비공개 / 링크 / Store 공개 | 링크 (Viewer/Editor 권한) |
| **코드 실행** | Code Interpreter (강력) | 제한적 |
| **이미지 생성** | DALL·E 내장 | Imagen 내장 |
| **설계 철학** | **확장성(Extensibility) 중심** | **생태계 적합성(Ecosystem Fit) 중심** |

### 3.2 근본적 설계 철학의 차이

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│   GPTs = "확장성" — 외부 세계와 연결하는 열린 플랫폼    │
│   ├─ Actions로 어떤 API든 연결 가능                     │
│   ├─ Zapier/Make/n8n 으로 수백 개 서비스 연동           │
│   └─ GPT Store로 전 세계 배포                          │
│                                                        │
│   Gems = "생태계" — Google 안에서 완결되는 워크플로우    │
│   ├─ Drive 실시간 동기화로 항상 최신 데이터              │
│   ├─ Gmail/Docs/Calendar 네이티브 접근                  │
│   └─ Google Docs 사이드바에서 직접 Gem 호출             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 3.3 선택 가이드

**GPTs를 선택하세요 if:**
- 외부 API 연동이 필요한 경우 (CRM, 검색, 이메일 자동화)
- GPT Store에 공개 배포하고 싶을 때
- 복잡한 다단계 자동화 워크플로우를 구축할 때
- Code Interpreter로 데이터 분석이 핵심일 때
- 다양한 서드파티 서비스를 넘나드는 작업

**Gems를 선택하세요 if:**
- 무료로 시작하고 싶을 때
- Google Workspace 중심 업무 환경일 때
- Drive 문서가 자주 변경되어 자동 동기화가 필수일 때
- 팀 내부에서 Gem을 공유 자산으로 활용할 때
- Gmail에서 이메일 초안, Calendar에서 회의 요약 등 Google 생태계 내 작업

### 3.4 둘 다 가능한 것
- 맞춤 지침으로 역할/톤/형식 지정
- 파일 업로드를 통한 지식 제공
- 반복 업무 자동화
- 웹 검색, 이미지 생성, 문서 협업
- 미리보기(Preview)로 실시간 테스트

---

## Part 4: Agentic Workflow로의 연결 (다음 강의 예고)
> **소요시간**: 약 15분

### 4.1 GPTs/Gems의 구조 = AI Agent의 기본 구조

오늘 배운 GPTs와 Gems의 구성 요소는 AI Agent 설계의 핵심 패턴과 **1:1로 대응**됩니다:

| GPTs/Gems 요소 | AI Agent 개념 | 설명 |
|----------------|--------------|------|
| Instructions | **System Prompt** | 에이전트의 역할과 행동 규칙 |
| Knowledge | **RAG (검색 증강 생성)** | 외부 지식 기반 연동 |
| Actions / Extensions | **Tool Use (도구 사용)** | 외부 API/서비스 호출 |
| Prompt Starters | **Entry Point / Trigger** | 워크플로우 시작점 |
| Capabilities | **Agent Skills** | 에이전트의 능력 범위 |

### 4.2 GPTs Actions가 Agentic Workflow의 기초가 되는 이유

GPT Actions의 작동 방식을 다시 보면:

```
사용자 질문 (자연어)
    ↓
GPT가 "어떤 API를 호출할지" 자동 판단 (Function Calling)
    ↓
자연어 → JSON 입력 형식 자동 변환
    ↓
API 호출 실행
    ↓
결과를 자연어로 반환
```

이것은 AI를 단순한 '텍스트 생성기'가 아니라 **"다음 행동(Action)을 예측하고 실행하는 논리 엔진(Logic Engine)"**으로 활용하는 훈련입니다.

이 패턴이 바로 Agentic AI의 핵심: **Perceive(인식) → Decide(결정) → Act(행동)**

### 4.3 GPTs/Gems의 한계 → 왜 진짜 Agentic Workflow가 필요한가?

GPTs와 Gems는 결국 **사용자가 채팅을 시작해야만 작동하는 대화형 인터페이스**입니다:

| 한계 | 설명 |
|------|------|
| **대화 종속** | 인간이 프롬프트를 입력해야만 실행됨 — 백그라운드 자동 실행 불가 |
| **단일 에이전트** | 하나의 GPT/Gem이 모든 것을 처리 → 복잡한 작업에 비효율 |
| **조건부 분기 없음** | "만약 A이면 B, 아니면 C" 같은 로직 불가 |
| **루프/반복 없음** | 작업을 반복하거나 결과 확인 후 재시도 불가 |
| **장기 메모리 제한** | 대화 간 맥락 유지에 한계 |
| **에이전트 간 협업 불가** | 여러 전문가 에이전트가 협력하는 구조 불가 |
| **스케줄링 불가** | 특정 시간에 자동 실행하는 기능 없음 |

### 4.4 실전 워크플로우 예시 — GPTs/Gems의 한계를 넘어서

```
[콘텐츠 제작 자동화 파이프라인 예시]

① Intake    : 폼 제출 → 스프레드시트에 브리프 자동 저장
② Planning  : GPT가 브리프 기반 아웃라인 + 추천 작성
③ Production: 작성자가 Docs에서 초안 → Gem이 스타일/정확성 검토
④ Review    : Assistants가 체크리스트 기준으로 이슈 플래깅
⑤ Publishing: n8n/Make가 CMS에 콘텐츠 게시 + 기록 업데이트

→ 이런 다단계 파이프라인은 GPTs/Gems 단독으로는 불가!
→ 자동화 플랫폼(n8n, Make)과 결합해야 가능
```

### 4.5 다음 강의 로드맵 미리보기

```
[Agentic Workflow 강의 시리즈]

Level 1 — 자동화 워크플로우 기초
  └─ n8n / Make를 활용한 AI 워크플로우 자동화
  └─ GPTs Actions + Zapier 연동 심화

Level 2 — AI Agent 빌드
  └─ OpenAI Assistants API 활용
  └─ Google Gemini API + Function Calling
  └─ Claude MCP (Model Context Protocol) 활용

Level 3 — 멀티 에이전트 시스템
  └─ 다중 에이전트 오케스트레이션
  └─ 에이전트 간 역할 분담과 협업 설계
  └─ 실전 프로젝트: 자동 리서치 → 분석 → 보고서 생성 파이프라인
```

### 4.6 오늘 강의의 핵심 정리

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   GPTs/Gems = AI Agent의 "노코드 버전"                       │
│                                                              │
│   Instructions  →  System Prompt   (역할 설계)               │
│   Knowledge     →  RAG             (지식 연동)               │
│   Actions       →  Tool Use        (도구 호출)               │
│                                                              │
│   이 3가지 패턴만 이해하면,                                    │
│   어떤 AI Agent 프레임워크든 동일하게 적용됩니다               │
│                                                              │
│   오늘의 GPTs/Gems는 "텍스트 생성기"가 아닙니다               │
│   → "다음 행동을 예측하고 실행하는 논리 엔진"입니다            │
│   → 이것이 Agentic Workflow의 진짜 출발점입니다               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 부록: 실습 준비 체크리스트

### ChatGPT GPTs 실습을 위해
- [ ] ChatGPT Plus 구독 ($20/월) — 또는 강사 시연 관람
- [ ] chatgpt.com 로그인 확인
- [ ] 업로드할 참고 파일 1~2개 준비 (PDF, 텍스트 등)

### Gemini Gems 실습을 위해
- [ ] Google 계정 로그인 (무료 Gmail 가능)
- [ ] gemini.google.com 접속 확인
- [ ] (선택) Google Drive에 참고 문서 준비
- [ ] (선택) Google AI Pro 구독으로 Gemini 3 사용

---

## 참고 자료

### 공식 문서
- [Creating a GPT — OpenAI Help Center](https://help.openai.com/en/articles/8554397-creating-a-gpt)
- [GPT Builder — OpenAI Help Center](https://help.openai.com/en/articles/8770868-gpt-builder)
- [GPT Actions — OpenAI Developers](https://developers.openai.com/api/docs/actions/introduction)
- [맞춤 Gems 만들기 — Google Gemini 고객센터](https://support.google.com/gemini/answer/15235603?hl=ko)
- [Gem 사용 방법 — Google Gemini 고객센터](https://support.google.com/gemini/answer/15236405?hl=ko)

### 한국어 가이드
- [GPTs 사용법 — 커스텀 GPT 만들기 상세 가이드 (DeepdAive)](https://deepdaive.com/커스텀-gpt/)
- [GPTs Action 사용법 — 외부 API 연결 (프롬프트해커 대니)](https://www.magicaiprompts.com/blog/mastering-gpts-action)
- [업무 자동화의 비밀, 제미나이 Gems 프롬프트 활용법](https://sphinfo.com/blog/read/608)
- [Gems로 맞춤형 대화 시작하기 (메가존소프트)](https://www.megazonesoft.com/customize-gemini-with-gems-html/)

### 비교 분석
- [Gemini Gems vs. Custom GPTs — Launchcodex](https://launchcodex.com/blog/llms-ai-agents-tools/gemini-gems-vs-custom-gpts/)
- [Custom GPTs vs. Gemini Gems: Who Wins? — LearnPrompting](https://learnprompting.org/blog/custom-gpts-vs-gemini-gems)
- [Gemini Gems vs ChatGPT GPTs — MindStudio](https://www.mindstudio.ai/blog/gemini-gems-vs-chatgpt-gpts-comparison)
- [GPTs, Gems, Copilots, Agents 차이점](https://innovaitionpartners.com/blog/gpts-gems-copilots-agents-wth-is-the-difference)
