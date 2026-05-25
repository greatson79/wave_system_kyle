# 청소년 인생계획 웹앱 설계 문서

**날짜:** 2026-05-23  
**상태:** 승인됨  
**범위:** youth_life_plan 스킬 → 독립 웹앱 전환

---

## 1. 개요

`Claude_skills/youth_life_plan/SKILL.md`에 정의된 9개 에이전트 청소년 인생계획 시스템을 독립형 웹앱으로 구현한다. 청소년 본인과 사역자가 각자의 역할로 사용하는 이중 역할 구조이며, 구조화 폼과 선택적 AI 대화 보조를 결합한 하이브리드 방식으로 동작한다.

---

## 2. 확정 결정 사항

| 항목 | 결정 |
|------|------|
| 플랫폼 | 웹앱 (모바일 반응형 PWA) — 독립 단독 배포 |
| 사용자 구조 | 청소년 계정 + 사역자 계정 (역할 분리) |
| MVP 범위 | 표준 — 인터뷰→도메인→분석→코칭+수련회 모드 포함 |
| AI 방식 | 하이브리드 (구조화 폼 + 선택적 AI 대화 보조) |
| 백엔드 | Next.js 14 + Supabase (PostgreSQL + Auth) |
| 배포 | Vercel |
| AI 모델 | claude-sonnet-4-6 (Anthropic API) |

---

## 3. 기술 스택

### 프론트엔드
- **Next.js 14** — App Router, Server Components
- **Tailwind CSS + shadcn/ui** — UI 컴포넌트
- **PWA** — 모바일 홈화면 추가, 오프라인 기본 지원

### 백엔드
- **Next.js API Routes** — Claude API 프록시, 비즈니스 로직
- **Supabase** — PostgreSQL DB, Row Level Security (RLS), 실시간 구독
- **Supabase Auth** — 카카오 / 구글 소셜 로그인

### AI
- **Anthropic Claude API** (`claude-sonnet-4-6`)
  - 도메인 분석 (4개 동시 병렬 호출)
  - 코칭 플랜 생성
  - 대화 보조 (선택 활성화 시)
  - 위기 키워드 감지

### 배포
- **Vercel** — 자동 배포, Edge Functions
- **Supabase** — 별도 독립 프로젝트 (church-accounting과 완전 분리)

---

## 4. 사용자 역할 및 흐름

### 4.1 청소년 (Youth)

```
로그인 (카카오/구글)
  ↓
인터뷰 — 5문 기본 질문 (학년, 관심사, 현재 상태 등)
  ↓
도메인 4개 (병렬 진행 가능, 저장 후 이어서 가능)
  ├── 진로·소명  (calling_direction_mode)
  ├── 가족관계   (family_mode)
  ├── 또래관계   (peers_mode)
  └── 나의삶·신앙 (faith_life_mode)
  ↓ (4개 완료 시)
AI 분석 실행 (AnalysisAgent → CoachingAgent 순차)
  ↓
결과 카드 (청소년용) — 저장 및 공유 가능
```

**하이브리드 AI 동작:**
- 각 도메인 폼 하단에 **"AI와 더 이야기하기 💬"** 버튼 배치
- 버튼 클릭 시 해당 도메인 컨텍스트를 가진 채팅 사이드패널 오픈
- 채팅 내용은 도메인 답변에 자동 보강되어 분석에 반영

### 4.2 사역자 (Pastor)

```
로그인 (카카오/구글)
  ↓
대시보드 — 소속 교회 청소년 목록, 완료 현황
  ↓
개별 청소년 선택
  ├── 코칭 플랜 (PastorPlanAgent 결과)
  ├── 도메인별 원본 답변 열람
  └── 위기 플래그 확인
  ↓
수련회 모드 — 그룹 세션 생성, 45~60분 집중 플로우 진행
```

**위기 감지:**
- 자살·자해 → 1393 즉시 배너 + 사역자 대시보드 빨간 플래그
- 학교폭력 → 117 안내 + 플래그
- 가정폭력 → 1391 안내 + 플래그
- 이단 키워드 → 경고 플래그

---

## 5. 데이터 모델

```sql
-- 교회 그룹
churches (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz
)

-- 사용자 (청소년 + 사역자 공통)
users (
  id uuid PRIMARY KEY REFERENCES auth.users,
  role text CHECK (role IN ('youth', 'pastor')),
  church_id uuid REFERENCES churches,
  nickname text NOT NULL,       -- 미성년자 보호: 실명 대신 닉네임
  grade text,                   -- 청소년 전용: 중1~고3
  created_at timestamptz
)

-- 인생계획 세션
sessions (
  id uuid PRIMARY KEY,
  youth_id uuid REFERENCES users,
  pastor_id uuid REFERENCES users,
  mode text CHECK (mode IN ('standard', 'retreat')),
  status text CHECK (status IN ('in_progress', 'completed')),
  created_at timestamptz,
  completed_at timestamptz
)

-- 도메인별 답변
domain_answers (
  id uuid PRIMARY KEY,
  session_id uuid REFERENCES sessions,
  domain text CHECK (domain IN ('calling', 'family', 'peers', 'faith')),
  answers jsonb NOT NULL,       -- 폼 답변 구조화 저장
  ai_chat_log jsonb,            -- 선택적 대화 보조 기록
  completed_at timestamptz
)

-- AI 분석 결과
analysis_results (
  id uuid PRIMARY KEY,
  session_id uuid REFERENCES sessions,
  analysis_json jsonb,          -- AnalysisAgent 출력
  coaching_plan_json jsonb,     -- CoachingAgent 출력 (사역자용)
  youth_card_json jsonb,        -- YouthCardAgent 출력 (청소년용)
  crisis_flags jsonb,           -- 위기 키워드 감지 결과
  created_at timestamptz
)
```

**보안:**
- Supabase RLS 적용 — 청소년은 자신의 세션만 읽기/쓰기
- 사역자는 소속 church_id 내 youth만 열람 가능
- `coaching_plan_json`은 사역자만 접근 가능 (RLS 정책)

---

## 6. 주요 화면 구성

### 청소년 화면
| 화면 | 설명 |
|------|------|
| `/` | 랜딩 — 소개 + 로그인 |
| `/onboarding` | 최초 1회: 학년·닉네임 설정 |
| `/interview` | 5문 기본 인터뷰 |
| `/plan/calling` | 진로·소명 도메인 폼 |
| `/plan/family` | 가족관계 도메인 폼 |
| `/plan/peers` | 또래관계 도메인 폼 |
| `/plan/faith` | 나의삶·신앙 도메인 폼 |
| `/result` | 결과 카드 (AI 분석 완료 후) |

### 사역자 화면
| 화면 | 설명 |
|------|------|
| `/pastor` | 대시보드 — 청소년 목록·현황 |
| `/pastor/youth/[id]` | 개별 코칭 플랜 + 도메인 답변 |
| `/pastor/retreat` | 수련회 모드 — 그룹 세션 관리 |

---

## 7. AI 통합 설계

### 호출 구조
```
도메인 폼 완료 (4개)
  → POST /api/analyze
    → Claude API 병렬 4호출 (도메인별 분석)
    → Claude API 순차 1호출 (통합 분석 → 코칭 플랜)
    → DB 저장 (analysis_results)
  → 결과 카드 렌더링
```

### 대화 보조 (하이브리드)
```
사용자가 "AI와 더 이야기하기" 클릭
  → POST /api/chat (streaming)
    → 해당 도메인 컨텍스트 + SKILL.md 페르소나 주입
    → Claude API streaming response
  → 사이드패널에 실시간 출력
  → 대화 종료 시 domain_answers.ai_chat_log에 저장
```

### 위기 감지
- 모든 텍스트 입력 저장 전 서버사이드 키워드 스캔
- 감지 시: 즉시 UI 경고 배너 + `crisis_flags` DB 저장 + 사역자 실시간 알림

---

## 8. 개발 단계 (예상 6~8주)

| 주차 | 작업 |
|------|------|
| 1~2주 | 프로젝트 셋업, Supabase 스키마, Auth (소셜 로그인), 기본 라우팅 |
| 3~4주 | 청소년 플로우: 인터뷰 → 도메인 4개 폼 → AI 분석 → 결과 카드 |
| 5주 | 하이브리드 AI 대화 보조 + 위기 감지 |
| 6주 | 사역자 대시보드 + 코칭 플랜 뷰 |
| 7주 | 수련회 모드 + PWA 설정 |
| 8주 | QA, 성능 최적화, 배포 |

---

## 9. 미포함 항목 (v2 이후)

- 반기회고 모드 (`/반기회고`)
- 구글 캘린더 연동
- PWA 푸시 알림
- 다국어 지원
- 부모 계정 역할

---

## 10. 신학·윤리 안전 원칙 (SKILL.md 유지)

- 번영신학, 개인 주관적 계시를 진로의 유일 근거로 제시 금지
- 이단·사이비 관련 방향 제시 금지
- 미성년자 보호: 닉네임 사용, 민감 정보 사역자 플랜에만 기록
- 정죄 없는 언어: "잘못했다" 아닌 "다시 시작할 수 있다" 프레이밍
