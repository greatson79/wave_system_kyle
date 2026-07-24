# churchTeam Web App — Requirements Document

> **작성일:** 2026-06-11  
> **버전:** v1.0  
> **대상:** 디딤교회 AI 부교역자 시스템 (31인 에이전트)의 웹앱 전환

---

## 배경 및 목적

현재 churchTeam은 Claude Code CLI에서만 동작한다. 담임목사님과 사역팀이 터미널 없이 브라우저에서 AI 팀을 활용할 수 있도록 웹앱화한다.

**핵심 제약:**
- 신학 필터는 모든 산출물에 반드시 통과
- 최종 결정권은 담임목사님 — AI는 보조
- SOT(`state.yaml`) 구조 유지
- 목회철학 파일(`pastor/philosophy/`)이 모든 판단의 기준

---

## 공통 요구사항 (Option A · B 공통)

### 기능 요구사항

| # | 요구사항 | 우선순위 |
|---|---------|---------|
| F-01 | Claude API를 통해 31인 에이전트 호출 | P0 |
| F-02 | 목회철학 문서 업로드 및 컨텍스트 주입 | P0 |
| F-03 | `/팀`, `/팀-전략분석`, `/팀-연간계획`, `/팀-월간`, `/팀-분기` 명령 실행 | P0 |
| F-04 | 신학 필터 통과 여부 표시 | P0 |
| F-05 | 담임목사님 최종 승인 게이트 UI | P0 |
| F-06 | 산출물 목록 및 열람 | P1 |
| F-07 | 한국어 인터페이스 | P0 |

### 비기능 요구사항

| # | 요구사항 | 기준 |
|---|---------|------|
| NF-01 | 응답 시작 시간 | 에이전트 스트리밍: 첫 토큰 < 3s |
| NF-02 | 접근 제한 | 인증된 사용자(담임목사 + 사역팀)만 접근 |
| NF-03 | 모바일 대응 | 기본 반응형 레이아웃 (최소 768px 기준) |
| NF-04 | 보안 | Claude API 키 서버사이드 전용, 클라이언트 미노출 |

---

## Option A — 경량 대시보드

### 목표

CLI 없이 브라우저에서 churchTeam 명령을 실행하고 결과를 확인하는 **최소 기능 웹앱**. 기존 에이전트 프롬프트를 API 호출로 직접 연결한다.

**개발 기간:** 2~3주  
**배포:** Vercel  
**운영 비용:** Claude API 사용량 + Vercel 무료 플랜

---

### A. 아키텍처

```
Browser (Next.js)
    │
    ├── /dashboard          — 명령 실행 패널
    ├── /reports            — 산출물 열람
    └── /upload             — 목회철학 문서 업로드

        │ API Route (서버사이드)
        │
    Anthropic Claude API
        │
    에이전트 프롬프트 (.claude/agents/*.md 내용 주입)
```

**데이터 흐름:**
1. 사용자가 브라우저에서 명령 선택
2. Next.js API Route가 `.claude/agents/` 프롬프트 + 목회철학 파일 로드
3. Claude API 호출 (streaming)
4. 결과를 화면에 스트리밍 출력
5. 산출물 파일로 저장 (`output/YYYY-MM-DD/`)

---

### A. 기술 스택

| 레이어 | 기술 | 이유 |
|--------|------|------|
| 프레임워크 | Next.js 15 (App Router) | API Routes + SSR 동시 지원 |
| 스타일 | Tailwind CSS | 빠른 개발 |
| AI | `@anthropic-ai/sdk` | Claude API 공식 SDK |
| 파일 저장 | 로컬 파일시스템 (fs) | 기존 `output/` 구조 유지 |
| 인증 | NextAuth.js (이메일 또는 패스코드) | 최소 설정 |
| 배포 | Vercel | 무료 플랜, 자동 배포 |

---

### A. 파일 구조

```
churchteam-web/                     ← 신규 프로젝트 루트
├── app/
│   ├── layout.tsx                  — 루트 레이아웃 (한국어, 폰트)
│   ├── page.tsx                    — 대시보드 메인
│   ├── dashboard/
│   │   └── page.tsx                — 명령 실행 패널
│   ├── reports/
│   │   └── page.tsx                — 산출물 목록 + 열람
│   ├── upload/
│   │   └── page.tsx                — 목회철학 문서 업로드
│   └── api/
│       ├── run-command/
│       │   └── route.ts            — 에이전트 명령 실행 (streaming)
│       ├── reports/
│       │   └── route.ts            — 산출물 파일 목록 반환
│       └── upload/
│           └── route.ts            — 목회철학 파일 저장
├── components/
│   ├── CommandPanel.tsx            — 명령 버튼 6개 + 자유입력
│   ├── StreamingOutput.tsx         — 에이전트 응답 스트리밍 표시
│   ├── TheologyBadge.tsx           — 신학 필터 통과 배지
│   ├── ApprovalGate.tsx            — 담임목사님 승인 버튼
│   └── ReportCard.tsx              — 산출물 카드
├── lib/
│   ├── claude.ts                   — Claude API 클라이언트 + 스트리밍 헬퍼
│   ├── agents.ts                   — 에이전트 프롬프트 로더 (.claude/agents/*.md)
│   └── files.ts                    — 목회철학·산출물 파일 IO
├── data/                           — churchTeam 데이터 연결 (심링크 또는 복사)
│   ├── pastor/philosophy/
│   └── output/
├── .env.local                      — ANTHROPIC_API_KEY, NEXTAUTH_SECRET
└── package.json
```

---

### A. 화면 정의

#### 1) 대시보드 (`/dashboard`)

```
┌─────────────────────────────────────────────────────────┐
│  churchTeam  —  디딤교회 AI 부교역자                      │
├─────────────────────────────────────────────────────────┤
│  [/팀]  [/팀-전략분석]  [/팀-연간계획]                    │
│  [/팀-월간]  [/팀-분기]  [/팀-건강]                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  자유 입력: "이번 주 설교 주제는 요한복음 15장..."   │  │
│  └───────────────────────────────────────────────────┘  │
│  [실행]                                                  │
│                                                         │
│  ─── 에이전트 응답 ──────────────────────────────────── │
│  [스트리밍 출력 영역]                                     │
│                                                         │
│  ✅ 신학 필터 통과     [담임목사님 승인]  [저장]           │
└─────────────────────────────────────────────────────────┘
```

#### 2) 산출물 (`/reports`)

```
┌─────────────────────────────────────────────────────────┐
│  산출물 목록                                              │
├─────────────────────────────────────────────────────────┤
│  2026-06-10 │ 전략팀 시대통찰 보고서      [열람] [다운로드]│
│  2026-06-10 │ 여름사역 기획안 Phase 1    [열람] [다운로드]│
│  2026-06-08 │ 주간 설교 준비안           [열람] [다운로드]│
└─────────────────────────────────────────────────────────┘
```

---

### A. 기능 제약 (Scope Out)

- 에이전트 간 오케스트레이션 시각화 — 단순 텍스트 출력으로 대체
- `state.yaml` 실시간 수정 — 읽기 전용 표시만
- 대화 기록 DB 저장 — 로컬 파일로만 저장
- 다중 사용자 동시 세션 — 단일 세션 기준

---

### A. 개발 태스크 분해

| 태스크 | 내용 | 예상 시간 |
|--------|------|---------|
| A-T01 | Next.js 프로젝트 초기화 + Tailwind + 인증 설정 | 0.5일 |
| A-T02 | Claude API 스트리밍 연결 (`/api/run-command`) | 1일 |
| A-T03 | 에이전트 프롬프트 로더 (`lib/agents.ts`) | 0.5일 |
| A-T04 | 대시보드 명령 패널 UI (`CommandPanel.tsx`) | 0.5일 |
| A-T05 | 스트리밍 출력 컴포넌트 (`StreamingOutput.tsx`) | 0.5일 |
| A-T06 | 신학 필터 배지 + 승인 게이트 UI | 0.5일 |
| A-T07 | 목회철학 파일 업로드 API + UI | 0.5일 |
| A-T08 | 산출물 목록 + 열람 페이지 | 0.5일 |
| A-T09 | Vercel 배포 + 환경변수 설정 | 0.5일 |
| A-T10 | QA — 전체 명령 실행 테스트 | 1일 |
| **합계** | | **6~8일** |

---

---

## Option B — 풀스택 사역 플랫폼

### 목표

churchTeam을 **독립적인 사역 관리 플랫폼**으로 구축한다. 에이전트 실행뿐 아니라 설교 계획, 주간 보고서, 카드뉴스 등 산출물을 DB에 저장하고 팀원과 공유·관리한다.

**개발 기간:** 6~8주  
**배포:** Vercel (프론트) + Supabase (DB + 스토리지)  
**운영 비용:** Claude API + Supabase 무료~Pro 플랜

---

### B. 아키텍처

```
Browser (Next.js 15)
    │
    ├── /dashboard          — 에이전트 실행 + 실시간 오케스트레이션
    ├── /sermon             — 설교 계획 관리
    ├── /weekly             — 주간 사역 보고서
    ├── /content            — 카드뉴스 · SNS 콘텐츠
    ├── /reports            — 전략 보고서 아카이브
    ├── /calendar           — 교회 절기 · 행사 캘린더
    └── /admin              — 목회철학 문서 · 팀 설정

        │ Next.js API Routes (서버사이드)
        │
    ┌───────────┬──────────────┐
    │           │              │
 Claude API  Supabase DB   Supabase Storage
    │        (산출물 메타)   (파일: PDF·이미지)
    │
 에이전트 오케스트레이터
 (31인 팀 시뮬레이션)
```

**데이터 흐름:**
1. 사용자 요청 → 오케스트레이터 API
2. Lead Orchestrator → Team Router → 해당 팀 에이전트 순차 호출
3. 신학 필터 자동 검증
4. 결과 스트리밍 + Supabase 저장
5. 담임목사님 승인 → 상태 업데이트 → 팀 공유

---

### B. 기술 스택

| 레이어 | 기술 | 이유 |
|--------|------|------|
| 프레임워크 | Next.js 15 (App Router) | 풀스택, Edge Runtime 지원 |
| 스타일 | Tailwind CSS + shadcn/ui | 디자인 시스템 일관성 |
| AI | `@anthropic-ai/sdk` | 스트리밍, 멀티-에이전트 |
| DB | Supabase (PostgreSQL) | 산출물 메타데이터, 대화 기록 |
| 스토리지 | Supabase Storage | PDF, 이미지, 문서 파일 |
| 인증 | Supabase Auth | 역할 기반 (담임목사 / 사역팀) |
| 상태관리 | Zustand | 클라이언트 에이전트 실행 상태 |
| 실시간 | Supabase Realtime | 팀원 산출물 알림 |
| 배포 | Vercel + Supabase | 각 레이어 전문 플랫폼 |

---

### B. 파일 구조

```
churchteam-platform/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                        — 메인 허브
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── layout.tsx
│   ├── dashboard/
│   │   └── page.tsx                    — 에이전트 실행 + 오케스트레이션 뷰
│   ├── sermon/
│   │   ├── page.tsx                    — 설교 계획 목록
│   │   ├── [id]/page.tsx               — 설교 계획 상세
│   │   └── new/page.tsx                — 새 설교 생성
│   ├── weekly/
│   │   ├── page.tsx                    — 주간 보고서 목록
│   │   └── [id]/page.tsx               — 주간 보고서 상세
│   ├── content/
│   │   ├── page.tsx                    — 콘텐츠 갤러리
│   │   └── [id]/page.tsx               — 카드뉴스 · SNS 콘텐츠
│   ├── reports/
│   │   └── page.tsx                    — 전략 보고서 아카이브
│   ├── calendar/
│   │   └── page.tsx                    — 교회 절기 · 행사
│   ├── admin/
│   │   ├── page.tsx                    — 설정 허브
│   │   ├── philosophy/page.tsx         — 목회철학 문서 관리
│   │   └── team/page.tsx               — 팀 멤버 설정
│   └── api/
│       ├── orchestrate/route.ts        — 에이전트 오케스트레이터 (핵심)
│       ├── theology-filter/route.ts    — 신학 필터 단독 API
│       ├── reports/route.ts            — 산출물 CRUD
│       ├── upload/route.ts             — 파일 업로드 → Supabase Storage
│       └── webhook/route.ts            — 승인 상태 변경 알림
│
├── components/
│   ├── orchestrator/
│   │   ├── TeamFlowChart.tsx           — 31인 팀 오케스트레이션 시각화
│   │   ├── AgentCard.tsx               — 개별 에이전트 상태 카드
│   │   └── StreamingConsole.tsx        — 에이전트 응답 실시간 출력
│   ├── theology/
│   │   ├── FilterBadge.tsx             — 신학 필터 통과/경고 배지
│   │   └── ApprovalGate.tsx            — 담임목사님 승인 게이트
│   ├── content/
│   │   ├── SermonCard.tsx
│   │   ├── WeeklyReportCard.tsx
│   │   └── ContentGalleryItem.tsx
│   ├── calendar/
│   │   └── ChurchCalendar.tsx          — 절기 캘린더
│   └── ui/                             — shadcn/ui 기반 공통 컴포넌트
│
├── lib/
│   ├── claude/
│   │   ├── client.ts                   — Anthropic SDK 초기화
│   │   ├── orchestrator.ts             — 31인 팀 오케스트레이션 엔진
│   │   ├── agents.ts                   — 에이전트 프롬프트 로더
│   │   └── theology-filter.ts          — 신학 필터 로직
│   ├── supabase/
│   │   ├── client.ts                   — Supabase 클라이언트
│   │   ├── reports.ts                  — 산출물 DB 쿼리
│   │   └── storage.ts                  — 파일 업로드/다운로드
│   └── utils/
│       ├── date.ts
│       └── korean.ts                   — 한국어 처리 유틸
│
├── store/
│   └── orchestratorStore.ts            — Zustand: 에이전트 실행 상태
│
├── supabase/
│   └── migrations/
│       ├── 001_reports.sql             — 산출물 테이블
│       ├── 002_sermons.sql             — 설교 계획 테이블
│       └── 003_approvals.sql           — 승인 기록 테이블
│
└── .env.local
```

---

### B. 데이터베이스 스키마

```sql
-- 산출물 (모든 에이전트 출력)
CREATE TABLE reports (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type        TEXT NOT NULL,          -- 'strategy' | 'sermon' | 'weekly' | 'content'
  title       TEXT NOT NULL,
  content     TEXT NOT NULL,
  theology_passed BOOLEAN DEFAULT false,
  approved_by TEXT,                   -- 담임목사님 승인
  approved_at TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  file_url    TEXT                    -- Supabase Storage URL
);

-- 설교 계획
CREATE TABLE sermons (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scripture   TEXT NOT NULL,          -- 본문
  title       TEXT,
  outline     TEXT,                   -- 설교 구조 (JSON)
  applications TEXT,                  -- 현대적용
  small_group TEXT,                   -- 나눔지
  status      TEXT DEFAULT 'draft',   -- 'draft' | 'approved' | 'delivered'
  sermon_date DATE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 승인 기록
CREATE TABLE approvals (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id   UUID REFERENCES reports(id),
  action      TEXT NOT NULL,          -- 'approved' | 'revision_requested'
  comment     TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

### B. 화면 정의

#### 1) 대시보드 — 에이전트 오케스트레이션

```
┌────────────────────────────────────────────────────────────────┐
│  churchTeam Platform                              [담임목사님 ▾] │
├──────────────┬─────────────────────────────────────────────────┤
│              │                                                  │
│  메뉴        │  에이전트 실행                                    │
│  ─ 대시보드  │  ┌──────────────────────────────────────────┐   │
│  ─ 설교계획  │  │ 요청 입력: "이번 주 설교 준비..."         │   │
│  ─ 주간보고  │  └──────────────────────────────────────────┘   │
│  ─ 콘텐츠   │  [/팀]  [전략분석]  [연간계획]  [월간]  [분기]  │
│  ─ 보고서   │                                                   │
│  ─ 캘린더   │  ─── 팀 오케스트레이션 ────────────────────────  │
│  ─ 설정     │  Lead Orchestrator ✅                             │
│             │    └─ 전략팀 🔄  ← 분석 중                       │
│             │    └─ 기획팀 ⏳                                   │
│             │    └─ 실행팀 ⏳                                   │
│             │                                                   │
│             │  ─── 실시간 출력 ──────────────────────────────  │
│             │  [스트리밍 텍스트...]                              │
│             │                                                   │
│             │  ✅ 신학 필터 통과       [승인] [수정요청] [저장] │
└──────────────┴─────────────────────────────────────────────────┘
```

#### 2) 설교 계획 (`/sermon`)

```
┌─────────────────────────────────────────────────────────────┐
│  설교 계획                                  [새 설교 생성 +] │
├─────────────────────────────────────────────────────────────┤
│  2026-06-15 │ 요한복음 15:1-8  │ ✅승인    [열람] [편집]    │
│  2026-06-22 │ 시편 23편        │ 🔄초안    [열람] [편집]    │
│  2026-06-29 │ 미지정           │ ⏳대기    [생성]           │
└─────────────────────────────────────────────────────────────┘
```

---

### B. 기능 제약 (MVP 기준, 이후 확장)

**MVP 포함:**
- 에이전트 오케스트레이션 (4팀 순차 실행 시각화)
- 설교 계획 DB 저장 + 담임목사님 승인 워크플로우
- 산출물 Supabase 저장 + PDF 다운로드
- 역할 기반 인증 (담임목사 / 사역팀원)

**MVP 제외 (Phase 2):**
- 모바일 앱 (React Native)
- 외부 캘린더 연동 (Google Calendar)
- 실시간 팀원 협업 편집
- 에이전트 응답 캐싱 최적화

---

### B. 개발 태스크 분해

| 태스크 | 내용 | 예상 시간 |
|--------|------|---------|
| **Phase 1 — 기반** | | **1주** |
| B-T01 | Next.js + Supabase + 인증 초기화 | 1일 |
| B-T02 | DB 마이그레이션 (3개 테이블) | 0.5일 |
| B-T03 | Supabase Storage + 파일 업로드 API | 0.5일 |
| B-T04 | 역할 기반 인증 + 보호 라우트 | 1일 |
| B-T05 | 레이아웃 + 네비게이션 (shadcn/ui) | 1일 |
| **Phase 2 — 에이전트 엔진** | | **2주** |
| B-T06 | Claude API 스트리밍 + 에이전트 프롬프트 로더 | 1일 |
| B-T07 | 오케스트레이터 엔진 (Lead → Team → Filter) | 2일 |
| B-T08 | 신학 필터 API + 배지 UI | 1일 |
| B-T09 | 팀 오케스트레이션 시각화 (TeamFlowChart) | 1.5일 |
| B-T10 | 담임목사님 승인 게이트 + 알림 | 1일 |
| **Phase 3 — 사역 기능** | | **2주** |
| B-T11 | 설교 계획 CRUD + 상태 워크플로우 | 1.5일 |
| B-T12 | 주간 보고서 목록 + 상세 | 1일 |
| B-T13 | 콘텐츠 갤러리 (카드뉴스 · SNS) | 1일 |
| B-T14 | 교회 캘린더 (절기 · 행사) | 1일 |
| B-T15 | 전략 보고서 아카이브 | 0.5일 |
| **Phase 4 — 마무리** | | **1주** |
| B-T16 | 목회철학 문서 관리 (업로드 + 컨텍스트 주입) | 1일 |
| B-T17 | PDF 다운로드 + 공유 링크 | 0.5일 |
| B-T18 | 반응형 레이아웃 QA | 0.5일 |
| B-T19 | Vercel 배포 + 환경변수 + 도메인 | 0.5일 |
| B-T20 | 전체 E2E 테스트 (주요 플로우 5개) | 1일 |
| **합계** | | **6~7주** |

---

## 비교 요약

| 항목 | Option A | Option B |
|------|---------|---------|
| 개발 기간 | 2~3주 | 6~8주 |
| 기술 복잡도 | 낮음 | 높음 |
| 에이전트 오케스트레이션 | 단순 API 호출 | 4팀 순차 시각화 |
| 산출물 저장 | 로컬 파일 | Supabase DB + Storage |
| 담임목사님 승인 | 단순 버튼 | 워크플로우 + 알림 |
| 팀 협업 | 없음 | 역할 기반 공유 |
| 확장성 | 제한적 | 높음 (Phase 2+ 가능) |
| 운영 비용 | 최소 | 중간 |
| 권장 대상 | 빠른 검증 · 1인 사용 | 장기 운영 · 팀 사용 |

---

## 권장사항

**단계적 접근 권장:**
1. **Option A 먼저 구축** (2~3주) — 실제 사용성 검증
2. A의 사용 패턴과 필요 기능 확인 후 **Option B로 점진적 전환**

Option A를 건너뛰고 바로 B를 구축하면 사용되지 않는 기능에 시간을 낭비할 위험이 있다. A를 통해 실제 목회 현장의 니즈를 파악한 후 B를 설계하는 것이 최선이다.

---

*이 문서는 churchTeam 웹앱 전환의 요구사항 기준이다. 구현 착수 전 담임목사님의 우선순위 확인이 필요하다.*
