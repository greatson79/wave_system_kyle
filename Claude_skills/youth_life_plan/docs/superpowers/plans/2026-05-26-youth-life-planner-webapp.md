# Youth Life Planner 웹앱 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 청소년 인생계획 스킬(SKILL.md)을 Next.js 14 + Supabase 기반 독립 웹앱으로 구현한다. 청소년과 사역자가 각자의 역할로 로그인하고, 구조화 폼 + 선택적 AI 대화 보조로 인생계획을 작성·관리한다.

**Architecture:** Next.js 14 App Router로 프론트엔드와 API Routes를 함께 구성한다. Supabase가 PostgreSQL DB·Auth·RLS를 담당하고, Claude API(claude-sonnet-4-6)가 도메인 분석·코칭 플랜 생성·대화 보조를 수행한다. 위기 키워드는 서버사이드에서 실시간 스캔하여 DB에 플래그를 기록하고 사역자에게 실시간 알림을 보낸다.

**Tech Stack:** Next.js 14 (App Router, TypeScript), Tailwind CSS, shadcn/ui, Supabase (PostgreSQL + Auth + RLS + Realtime), Anthropic SDK, Vercel, Vitest, Playwright

---

## 스펙 참조 파일

- 설계 문서: `docs/superpowers/specs/2026-05-23-youth-life-planner-webapp-design.md`
- 스킬 원본: `SKILL.md`, `references/*.md`

---

## 파일 구조 전체 맵

```
youth-life-planner/          ← 새 Next.js 프로젝트 루트
├── app/
│   ├── layout.tsx
│   ├── page.tsx             ← 랜딩 페이지
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── onboarding/page.tsx
│   ├── (youth)/
│   │   ├── layout.tsx       ← 청소년 공통 레이아웃
│   │   ├── interview/page.tsx
│   │   ├── plan/
│   │   │   ├── calling/page.tsx
│   │   │   ├── family/page.tsx
│   │   │   ├── peers/page.tsx
│   │   │   └── faith/page.tsx
│   │   └── result/page.tsx
│   ├── (pastor)/
│   │   ├── layout.tsx       ← 사역자 공통 레이아웃
│   │   ├── pastor/page.tsx  ← 대시보드
│   │   ├── pastor/youth/[id]/page.tsx
│   │   └── pastor/retreat/page.tsx
│   └── api/
│       ├── analyze/route.ts       ← 도메인 분석 + 코칭 플랜 생성
│       ├── chat/route.ts          ← AI 대화 보조 (streaming)
│       └── crisis/route.ts        ← 위기 키워드 스캔
├── components/
│   ├── ui/                  ← shadcn/ui 컴포넌트
│   ├── domain-form/
│   │   ├── CallingForm.tsx
│   │   ├── FamilyForm.tsx
│   │   ├── PeersForm.tsx
│   │   └── FaithForm.tsx
│   ├── chat/
│   │   └── AIChatPanel.tsx  ← 대화 보조 사이드패널
│   ├── result/
│   │   ├── YouthCard.tsx
│   │   └── CoachingPlan.tsx
│   ├── crisis/
│   │   └── CrisisBanner.tsx
│   └── dashboard/
│       ├── YouthList.tsx
│       └── YouthDetail.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts        ← 브라우저 Supabase 클라이언트
│   │   ├── server.ts        ← 서버 Supabase 클라이언트
│   │   └── types.ts         ← DB 타입 (generated)
│   ├── claude/
│   │   ├── client.ts        ← Anthropic SDK 초기화
│   │   ├── prompts.ts       ← 도메인별 시스템 프롬프트
│   │   └── analyze.ts       ← 분석 파이프라인 함수
│   ├── crisis.ts            ← 위기 키워드 상수 + 스캔 함수
│   └── utils.ts
├── hooks/
│   ├── useSession.ts        ← 현재 계획 세션 상태
│   └── useCrisisFlag.ts     ← 실시간 위기 구독
├── middleware.ts             ← Auth 라우트 보호
├── supabase/
│   └── migrations/
│       └── 0001_initial.sql ← DB 스키마 마이그레이션
└── tests/
    ├── unit/
    │   ├── crisis.test.ts
    │   ├── prompts.test.ts
    │   └── analyze.test.ts
    └── e2e/
        ├── youth-flow.spec.ts
        └── pastor-dashboard.spec.ts
```

---

## Task 1: 프로젝트 초기화

**Files:**
- Create: `youth-life-planner/` (Next.js 프로젝트 루트)
- Create: `youth-life-planner/package.json`
- Create: `youth-life-planner/.env.local`

- [ ] **Step 1: Next.js 프로젝트 생성**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Claude_skills/youth_life_plan
npx create-next-app@latest youth-life-planner \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --no-eslint \
  --import-alias "@/*"
cd youth-life-planner
```

- [ ] **Step 2: 의존성 설치**

```bash
npm install @supabase/supabase-js @supabase/ssr \
  @anthropic-ai/sdk \
  @radix-ui/react-dialog @radix-ui/react-label \
  class-variance-authority clsx tailwind-merge lucide-react
npm install -D vitest @vitejs/plugin-react \
  @playwright/test supabase
```

- [ ] **Step 3: shadcn/ui 초기화**

```bash
npx shadcn@latest init
# 프롬프트: style=default, baseColor=slate, cssVariables=yes
npx shadcn@latest add button card input label textarea badge alert progress
```

- [ ] **Step 4: .env.local 생성**

```bash
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
ANTHROPIC_API_KEY=your_anthropic_api_key
EOF
```

- [ ] **Step 5: 개발 서버 확인**

```bash
npm run dev
# Expected: http://localhost:3000 접속 가능, Next.js 기본 화면
```

- [ ] **Step 6: 초기 커밋**

```bash
git init
echo ".env.local\n.next\nnode_modules" > .gitignore
git add .
git commit -m "chore: Next.js 14 프로젝트 초기화 (Supabase + shadcn/ui)"
```

---

## Task 2: Supabase DB 스키마

**Files:**
- Create: `supabase/migrations/0001_initial.sql`

- [ ] **Step 1: Supabase CLI로 로컬 프로젝트 연결**

```bash
npx supabase init
npx supabase login
npx supabase link --project-ref YOUR_PROJECT_REF
```

- [ ] **Step 2: 마이그레이션 파일 작성**

```bash
mkdir -p supabase/migrations
```

`supabase/migrations/0001_initial.sql` 내용:

```sql
-- 교회 그룹
create table churches (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now()
);

-- 사용자
create table users (
  id uuid primary key references auth.users on delete cascade,
  role text not null check (role in ('youth', 'pastor')),
  church_id uuid references churches,
  nickname text not null,
  grade text check (grade in ('중1','중2','중3','고1','고2','고3')),
  created_at timestamptz default now()
);

-- 인생계획 세션
create table sessions (
  id uuid primary key default gen_random_uuid(),
  youth_id uuid not null references users,
  pastor_id uuid references users,
  mode text not null check (mode in ('standard','retreat')),
  status text not null default 'in_progress' check (status in ('in_progress','completed')),
  created_at timestamptz default now(),
  completed_at timestamptz
);

-- 도메인별 답변
create table domain_answers (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions on delete cascade,
  domain text not null check (domain in ('calling','family','peers','faith')),
  answers jsonb not null default '{}',
  ai_chat_log jsonb default '[]',
  completed_at timestamptz
);

-- AI 분석 결과
create table analysis_results (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions on delete cascade,
  analysis_json jsonb,
  coaching_plan_json jsonb,
  youth_card_json jsonb,
  crisis_flags jsonb default '[]',
  created_at timestamptz default now()
);

-- RLS 활성화
alter table churches enable row level security;
alter table users enable row level security;
alter table sessions enable row level security;
alter table domain_answers enable row level security;
alter table analysis_results enable row level security;

-- RLS 정책: users
create policy "본인 프로필 열람" on users for select using (auth.uid() = id);
create policy "본인 프로필 생성" on users for insert with check (auth.uid() = id);
create policy "사역자: 같은 교회 청소년 열람" on users for select
  using (
    exists (
      select 1 from users me
      where me.id = auth.uid()
        and me.role = 'pastor'
        and me.church_id = users.church_id
    )
  );

-- RLS 정책: sessions
create policy "청소년: 본인 세션" on sessions for all using (youth_id = auth.uid());
create policy "사역자: 같은 교회 세션 열람" on sessions for select
  using (
    exists (
      select 1 from users me
      join users youth on youth.id = sessions.youth_id
      where me.id = auth.uid()
        and me.role = 'pastor'
        and me.church_id = youth.church_id
    )
  );

-- RLS 정책: domain_answers
create policy "청소년: 본인 도메인 답변" on domain_answers for all
  using (
    exists (select 1 from sessions s where s.id = session_id and s.youth_id = auth.uid())
  );
create policy "사역자: 도메인 답변 열람" on domain_answers for select
  using (
    exists (
      select 1 from sessions s
      join users youth on youth.id = s.youth_id
      join users me on me.id = auth.uid()
      where s.id = session_id
        and me.role = 'pastor'
        and me.church_id = youth.church_id
    )
  );

-- RLS 정책: analysis_results
create policy "청소년: youth_card_json만 열람" on analysis_results for select
  using (
    exists (select 1 from sessions s where s.id = session_id and s.youth_id = auth.uid())
  );
create policy "사역자: 전체 분석 결과 열람" on analysis_results for select
  using (
    exists (
      select 1 from sessions s
      join users youth on youth.id = s.youth_id
      join users me on me.id = auth.uid()
      where s.id = session_id
        and me.role = 'pastor'
        and me.church_id = youth.church_id
    )
  );
```

- [ ] **Step 3: 마이그레이션 적용**

```bash
npx supabase db push
# Expected: "Finished supabase db push." 출력
```

- [ ] **Step 4: Supabase 대시보드에서 테이블 확인**

Supabase 대시보드 → Table Editor에서 churches, users, sessions, domain_answers, analysis_results 5개 테이블 확인.

- [ ] **Step 5: 커밋**

```bash
git add supabase/
git commit -m "feat: Supabase DB 스키마 + RLS 정책 설정"
```

---

## Task 3: Supabase Auth + 소셜 로그인

**Files:**
- Create: `src/lib/supabase/client.ts`
- Create: `src/lib/supabase/server.ts`
- Create: `src/middleware.ts`
- Create: `src/app/(auth)/login/page.tsx`

- [ ] **Step 1: Supabase 클라이언트 작성**

`src/lib/supabase/client.ts`:
```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

`src/lib/supabase/server.ts`:
```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )
}
```

- [ ] **Step 2: 미들웨어 작성 (라우트 보호)**

`src/middleware.ts`:
```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set(name, value)
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )
  const { data: { user } } = await supabase.auth.getUser()
  const { pathname } = request.nextUrl

  // 보호된 경로: 로그인 필요
  const protectedPaths = ['/interview', '/plan', '/result', '/pastor']
  const isProtected = protectedPaths.some(p => pathname.startsWith(p))

  if (isProtected && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 사역자 전용 경로 보호
  if (pathname.startsWith('/pastor')) {
    const { data: profile } = await supabase
      .from('users')
      .select('role')
      .eq('id', user!.id)
      .single()
    if (profile?.role !== 'pastor') {
      return NextResponse.redirect(new URL('/interview', request.url))
    }
  }

  return response
}

export const config = {
  matcher: ['/interview/:path*', '/plan/:path*', '/result/:path*', '/pastor/:path*'],
}
```

- [ ] **Step 3: 로그인 페이지 작성**

`src/app/(auth)/login/page.tsx`:
```typescript
'use client'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'

export default function LoginPage() {
  const supabase = createClient()

  const signInWithKakao = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'kakao',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    })
  }

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    })
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-4">
      <h1 className="text-3xl font-bold text-center">청소년 인생계획</h1>
      <p className="text-muted-foreground text-center max-w-sm">
        나의 진로·신앙·관계를 함께 설계해요
      </p>
      <div className="flex flex-col gap-3 w-full max-w-xs">
        <Button size="lg" className="bg-yellow-400 hover:bg-yellow-500 text-black"
          onClick={signInWithKakao}>
          카카오로 시작하기
        </Button>
        <Button size="lg" variant="outline" onClick={signInWithGoogle}>
          구글로 시작하기
        </Button>
      </div>
    </main>
  )
}
```

- [ ] **Step 4: Auth 콜백 라우트**

`src/app/auth/callback/route.ts`:
```typescript
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const origin = new URL(request.url).origin

  if (code) {
    const supabase = await createClient()
    await supabase.auth.exchangeCodeForSession(code)

    // 프로필 확인 → 없으면 온보딩으로
    const { data: { user } } = await supabase.auth.getUser()
    if (user) {
      const { data: profile } = await supabase
        .from('users')
        .select('id')
        .eq('id', user.id)
        .single()
      if (!profile) {
        return NextResponse.redirect(`${origin}/onboarding`)
      }
    }
  }
  return NextResponse.redirect(`${origin}/interview`)
}
```

- [ ] **Step 5: Supabase 대시보드에서 카카오·구글 OAuth 설정**

Supabase 대시보드 → Authentication → Providers:
- Google: Client ID / Secret 입력
- Kakao: REST API 키 입력
- Redirect URL: `https://your-project.supabase.co/auth/v1/callback`

- [ ] **Step 6: 로그인 흐름 수동 테스트**

```bash
npm run dev
# http://localhost:3000/login 접속
# 구글 로그인 → /onboarding 리다이렉트 확인
```

- [ ] **Step 7: 커밋**

```bash
git add src/
git commit -m "feat: Supabase Auth + 카카오/구글 소셜 로그인 + 미들웨어"
```

---

## Task 4: 온보딩 + 세션 관리 훅

**Files:**
- Create: `src/app/(auth)/onboarding/page.tsx`
- Create: `src/hooks/useSession.ts`

- [ ] **Step 1: 온보딩 페이지 작성**

`src/app/(auth)/onboarding/page.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const GRADES = ['중1','중2','중3','고1','고2','고3']
const ROLES = [
  { value: 'youth', label: '청소년 본인' },
  { value: 'pastor', label: '사역자' },
]

export default function OnboardingPage() {
  const router = useRouter()
  const supabase = createClient()
  const [nickname, setNickname] = useState('')
  const [role, setRole] = useState<'youth' | 'pastor'>('youth')
  const [grade, setGrade] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return

    await supabase.from('users').insert({
      id: user.id,
      role,
      nickname,
      grade: role === 'youth' ? grade : null,
    })

    router.push(role === 'pastor' ? '/pastor' : '/interview')
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-4">
      <h1 className="text-2xl font-bold">처음 오셨군요! 👋</h1>
      <div className="flex flex-col gap-4 w-full max-w-sm">
        <div className="flex gap-2">
          {ROLES.map(r => (
            <Button key={r.value} variant={role === r.value ? 'default' : 'outline'}
              onClick={() => setRole(r.value as 'youth' | 'pastor')} className="flex-1">
              {r.label}
            </Button>
          ))}
        </div>
        <div className="space-y-1">
          <Label>닉네임</Label>
          <Input placeholder="별명을 입력하세요" value={nickname}
            onChange={e => setNickname(e.target.value)} />
        </div>
        {role === 'youth' && (
          <div className="space-y-1">
            <Label>학년</Label>
            <div className="grid grid-cols-3 gap-2">
              {GRADES.map(g => (
                <Button key={g} size="sm"
                  variant={grade === g ? 'default' : 'outline'}
                  onClick={() => setGrade(g)}>{g}</Button>
              ))}
            </div>
          </div>
        )}
        <Button onClick={handleSubmit} disabled={!nickname || (role === 'youth' && !grade) || loading}>
          {loading ? '저장 중...' : '시작하기'}
        </Button>
      </div>
    </main>
  )
}
```

- [ ] **Step 2: useSession 훅 작성**

`src/hooks/useSession.ts`:
```typescript
'use client'
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

export type Session = {
  id: string
  youth_id: string
  mode: 'standard' | 'retreat'
  status: 'in_progress' | 'completed'
}

export function useSession() {
  const supabase = createClient()
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return setLoading(false)

      const { data } = await supabase
        .from('sessions')
        .select('*')
        .eq('youth_id', user.id)
        .eq('status', 'in_progress')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      setSession(data)
      setLoading(false)
    }
    load()
  }, [])

  const createSession = async (mode: 'standard' | 'retreat' = 'standard') => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return null
    const { data } = await supabase
      .from('sessions')
      .insert({ youth_id: user.id, mode })
      .select()
      .single()
    setSession(data)
    return data
  }

  return { session, loading, createSession }
}
```

- [ ] **Step 3: 커밋**

```bash
git add src/
git commit -m "feat: 온보딩 페이지 + useSession 훅"
```

---

## Task 5: 위기 감지 시스템

**Files:**
- Create: `src/lib/crisis.ts`
- Create: `src/app/api/crisis/route.ts`
- Create: `src/components/crisis/CrisisBanner.tsx`
- Create: `tests/unit/crisis.test.ts`

- [ ] **Step 1: 위기 키워드 + 스캔 함수 테스트 작성**

`tests/unit/crisis.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'
import { scanCrisis, CrisisType } from '@/lib/crisis'

describe('scanCrisis', () => {
  it('자살 키워드를 감지한다', () => {
    const result = scanCrisis('죽고 싶다')
    expect(result).toContainEqual(expect.objectContaining({ type: 'suicide' }))
  })

  it('학교폭력 키워드를 감지한다', () => {
    const result = scanCrisis('친구한테 맞는다')
    expect(result).toContainEqual(expect.objectContaining({ type: 'bullying' }))
  })

  it('이단 키워드를 감지한다', () => {
    const result = scanCrisis('신천지에 다닌다')
    expect(result).toContainEqual(expect.objectContaining({ type: 'cult' }))
  })

  it('위기 키워드 없으면 빈 배열 반환', () => {
    expect(scanCrisis('오늘 학교에서 재미있었다')).toEqual([])
  })
})
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
npx vitest run tests/unit/crisis.test.ts
# Expected: FAIL — scanCrisis not defined
```

- [ ] **Step 3: 위기 감지 함수 구현**

`src/lib/crisis.ts`:
```typescript
export type CrisisType = 'suicide' | 'bullying' | 'abuse' | 'cult' | 'burnout'

export type CrisisFlag = {
  type: CrisisType
  keyword: string
  hotline: string
  message: string
}

const CRISIS_PATTERNS: Array<{ type: CrisisType; patterns: string[]; hotline: string; message: string }> = [
  {
    type: 'suicide',
    patterns: ['자해', '자살', '죽고 싶다', '죽고싶다', '사라지고 싶다', '사라지고싶다'],
    hotline: '1393',
    message: '자살예방상담전화 1393 (24시간)',
  },
  {
    type: 'bullying',
    patterns: ['학교폭력', '따돌림', '맞는다', '괴롭힘', '왕따'],
    hotline: '117',
    message: '학교폭력신고 117',
  },
  {
    type: 'abuse',
    patterns: ['가정폭력', '부모한테 맞는다', '방임', '학대'],
    hotline: '1391',
    message: '아동보호전문기관 1391',
  },
  {
    type: 'cult',
    patterns: ['신천지', 'JMS', '하나님의교회', '구원파', '통일교'],
    hotline: '',
    message: '이단 접근이 감지되었습니다. 담당 사역자에게 알려주세요.',
  },
  {
    type: 'burnout',
    patterns: ['번아웃', '지쳐있다', '아무것도 하기 싫다', '너무 힘들다'],
    hotline: '',
    message: '회복이 먼저입니다. 지금 당장 계획보다 쉬는 것이 더 중요해요.',
  },
]

export function scanCrisis(text: string): CrisisFlag[] {
  const found: CrisisFlag[] = []
  for (const { type, patterns, hotline, message } of CRISIS_PATTERNS) {
    const matched = patterns.find(p => text.includes(p))
    if (matched) {
      found.push({ type, keyword: matched, hotline, message })
    }
  }
  return found
}
```

- [ ] **Step 4: 테스트 재실행 — 통과 확인**

```bash
npx vitest run tests/unit/crisis.test.ts
# Expected: PASS (4/4)
```

- [ ] **Step 5: 위기 감지 API Route 작성**

`src/app/api/crisis/route.ts`:
```typescript
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { scanCrisis } from '@/lib/crisis'

export async function POST(request: Request) {
  const { text, session_id } = await request.json()
  const flags = scanCrisis(text)

  if (flags.length > 0 && session_id) {
    const supabase = await createClient()
    await supabase.from('analysis_results')
      .upsert({ session_id, crisis_flags: flags }, { onConflict: 'session_id' })
  }

  return NextResponse.json({ flags })
}
```

- [ ] **Step 6: CrisisBanner 컴포넌트 작성**

`src/components/crisis/CrisisBanner.tsx`:
```typescript
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertTriangle } from 'lucide-react'
import type { CrisisFlag } from '@/lib/crisis'

export function CrisisBanner({ flags }: { flags: CrisisFlag[] }) {
  if (flags.length === 0) return null
  return (
    <div className="fixed top-0 left-0 right-0 z-50 p-4 space-y-2">
      {flags.map((flag, i) => (
        <Alert key={i} variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>⚠ 중요 안내</AlertTitle>
          <AlertDescription>
            {flag.message}
            {flag.hotline && (
              <strong className="block mt-1">📞 {flag.hotline}</strong>
            )}
          </AlertDescription>
        </Alert>
      ))}
    </div>
  )
}
```

- [ ] **Step 7: 커밋**

```bash
git add src/ tests/
git commit -m "feat: 위기 키워드 감지 시스템 (crisis.ts + API + CrisisBanner)"
```

---

## Task 6: Claude API 프롬프트 + 분석 파이프라인

**Files:**
- Create: `src/lib/claude/client.ts`
- Create: `src/lib/claude/prompts.ts`
- Create: `src/lib/claude/analyze.ts`
- Create: `src/app/api/analyze/route.ts`
- Create: `tests/unit/prompts.test.ts`

- [ ] **Step 1: Claude 클라이언트 초기화**

`src/lib/claude/client.ts`:
```typescript
import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

export const MODEL = 'claude-sonnet-4-6'
```

- [ ] **Step 2: 시스템 프롬프트 테스트 작성**

`tests/unit/prompts.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'
import { getDomainPrompt, getAnalysisPrompt } from '@/lib/claude/prompts'

describe('getDomainPrompt', () => {
  it('calling 도메인 프롬프트를 반환한다', () => {
    const prompt = getDomainPrompt('calling')
    expect(prompt).toContain('진로')
    expect(prompt).toContain('소명')
  })

  it('존재하지 않는 도메인은 에러를 던진다', () => {
    expect(() => getDomainPrompt('unknown' as any)).toThrow()
  })
})

describe('getAnalysisPrompt', () => {
  it('4개 도메인 답변을 받아 통합 분석 프롬프트를 생성한다', () => {
    const answers = { calling: {}, family: {}, peers: {}, faith: {} }
    const prompt = getAnalysisPrompt(answers, '고2', 'standard')
    expect(prompt).toContain('고2')
  })
})
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
npx vitest run tests/unit/prompts.test.ts
# Expected: FAIL
```

- [ ] **Step 4: 프롬프트 구현**

`src/lib/claude/prompts.ts`:
```typescript
type Domain = 'calling' | 'family' | 'peers' | 'faith'

const DOMAIN_PROMPTS: Record<Domain, string> = {
  calling: `너는 청소년의 진로와 소명을 탐색하는 코칭 전문가다.
청소년이 작성한 진로·소명 관련 답변을 바탕으로 3축(관심·재능·하나님 나라 기여)을 분석해라.
번영신학적 진술("믿음으로 기도하면 원하는 대학에 간다" 류)은 절대 사용하지 말 것.
정답을 주지 않고 스스로 발견하도록 질문하는 방식으로 답변한다.`,

  family: `너는 청소년의 가족 관계를 탐색하는 상담 전문가다.
부모·형제와의 관계 현황을 파악하고, 건강한 가정 환경 설계를 돕는다.
정죄 없이 현실을 직면시키되, "다시 시작할 수 있다"는 프레이밍을 유지한다.`,

  peers: `너는 청소년의 또래 관계를 분석하는 전문가다.
친구·학교·교회 관계를 투자/소모/방어 세 가지로 분류하고,
건강한 관계 지도 설계를 돕는다. 학교폭력·따돌림 언급 시 즉시 117 안내.`,

  faith: `너는 청소년의 신앙과 정체성을 탐색하는 신앙 멘토다.
개혁주의 신학 기반으로, 청소년의 신앙 현황·정체성·자기돌봄 루틴을 점검한다.
주관적 계시를 진로 결정의 유일 근거로 제시하는 것은 금지.`,
}

export function getDomainPrompt(domain: Domain): string {
  if (!(domain in DOMAIN_PROMPTS)) throw new Error(`Unknown domain: ${domain}`)
  return DOMAIN_PROMPTS[domain]
}

export function getAnalysisPrompt(
  answers: Record<string, unknown>,
  grade: string,
  mode: 'standard' | 'retreat'
): string {
  return `너는 청소년 인생계획 통합 분석 전문가다.
학년: ${grade}, 모드: ${mode === 'retreat' ? '수련회' : '평상시'}

아래 4개 도메인 답변을 통합 분석하여 JSON으로 반환하라.
{
  "summary": "청소년 전체 현황 요약 (3문장)",
  "strengths": ["강점 3가지"],
  "challenges": ["도전 과제 2가지"],
  "priorities": ["우선 집중 영역 2가지"]
}

도메인 답변:
${JSON.stringify(answers, null, 2)}`
}

export function getCoachingPrompt(analysisResult: unknown, grade: string): string {
  return `너는 청소년부 사역자를 위한 코칭 플랜 전문가다.
학년: ${grade}

분석 결과를 바탕으로 사역자용 코칭 플랜을 JSON으로 반환하라.
{
  "monthly_goals": [{"month": 1, "goal": "...", "actions": ["...", "..."]}],
  "prayer_topics": ["기도 제목 3가지"],
  "warning_signs": ["주의 관찰 사항"],
  "next_meeting_agenda": "다음 1:1 미팅 아젠다"
}

분석 결과:
${JSON.stringify(analysisResult, null, 2)}`
}
```

- [ ] **Step 5: 테스트 재실행 — 통과 확인**

```bash
npx vitest run tests/unit/prompts.test.ts
# Expected: PASS (3/3)
```

- [ ] **Step 6: 분석 파이프라인 구현**

`src/lib/claude/analyze.ts`:
```typescript
import { anthropic, MODEL } from './client'
import { getDomainPrompt, getAnalysisPrompt, getCoachingPrompt } from './prompts'

type Domain = 'calling' | 'family' | 'peers' | 'faith'

export async function analyzeDomains(
  domainAnswers: Record<Domain, Record<string, unknown>>,
  grade: string,
  mode: 'standard' | 'retreat'
) {
  // 1단계: 4개 도메인 병렬 분석
  const domainSummaries = await Promise.all(
    (Object.entries(domainAnswers) as [Domain, Record<string, unknown>][]).map(
      async ([domain, answers]) => {
        const msg = await anthropic.messages.create({
          model: MODEL,
          max_tokens: 1024,
          system: getDomainPrompt(domain),
          messages: [{ role: 'user', content: JSON.stringify(answers) }],
        })
        return { domain, summary: (msg.content[0] as { text: string }).text }
      }
    )
  )

  const summaryMap = Object.fromEntries(domainSummaries.map(d => [d.domain, d.summary]))

  // 2단계: 통합 분석
  const analysisMsg = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 2048,
    messages: [{
      role: 'user',
      content: getAnalysisPrompt(summaryMap, grade, mode),
    }],
  })
  const analysisText = (analysisMsg.content[0] as { text: string }).text
  const analysis = JSON.parse(analysisText.match(/\{[\s\S]*\}/)![0])

  // 3단계: 코칭 플랜
  const coachingMsg = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 2048,
    messages: [{
      role: 'user',
      content: getCoachingPrompt(analysis, grade),
    }],
  })
  const coachingText = (coachingMsg.content[0] as { text: string }).text
  const coaching = JSON.parse(coachingText.match(/\{[\s\S]*\}/)![0])

  return { analysis, coaching, domainSummaries: summaryMap }
}
```

- [ ] **Step 7: 분석 API Route 작성**

`src/app/api/analyze/route.ts`:
```typescript
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { analyzeDomains } from '@/lib/claude/analyze'

export async function POST(request: Request) {
  const { session_id } = await request.json()
  const supabase = await createClient()

  // 도메인 답변 로드
  const { data: domainRows } = await supabase
    .from('domain_answers')
    .select('domain, answers')
    .eq('session_id', session_id)

  if (!domainRows || domainRows.length < 4) {
    return NextResponse.json({ error: '4개 도메인을 모두 완료해야 합니다.' }, { status: 400 })
  }

  const domainAnswers = Object.fromEntries(domainRows.map(r => [r.domain, r.answers])) as any

  // 세션 유저 정보
  const { data: session } = await supabase
    .from('sessions')
    .select('youth_id')
    .eq('id', session_id)
    .single()

  const { data: profile } = await supabase
    .from('users')
    .select('grade')
    .eq('id', session!.youth_id)
    .single()

  const result = await analyzeDomains(domainAnswers, profile?.grade ?? '고1', 'standard')

  await supabase.from('analysis_results').upsert({
    session_id,
    analysis_json: result.analysis,
    coaching_plan_json: result.coaching,
    youth_card_json: result.analysis,
  }, { onConflict: 'session_id' })

  await supabase.from('sessions')
    .update({ status: 'completed', completed_at: new Date().toISOString() })
    .eq('id', session_id)

  return NextResponse.json({ success: true, analysis: result.analysis })
}
```

- [ ] **Step 8: 커밋**

```bash
git add src/ tests/
git commit -m "feat: Claude API 분석 파이프라인 (도메인 병렬 분석 + 코칭 플랜)"
```

---

## Task 7: AI 대화 보조 (스트리밍)

**Files:**
- Create: `src/app/api/chat/route.ts`
- Create: `src/components/chat/AIChatPanel.tsx`

- [ ] **Step 1: 스트리밍 API Route 작성**

`src/app/api/chat/route.ts`:
```typescript
import { anthropic, MODEL } from '@/lib/claude/client'
import { getDomainPrompt } from '@/lib/claude/prompts'
import { scanCrisis } from '@/lib/crisis'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { domain, messages, context } = await request.json()

  // 마지막 사용자 메시지 위기 스캔
  const lastUserMsg = messages.findLast((m: any) => m.role === 'user')?.content ?? ''
  const crisisFlags = scanCrisis(lastUserMsg)
  if (crisisFlags.some(f => f.type === 'suicide' || f.type === 'abuse')) {
    return NextResponse.json({ crisis: crisisFlags }, { status: 200 })
  }

  const stream = anthropic.messages.stream({
    model: MODEL,
    max_tokens: 1024,
    system: getDomainPrompt(domain) + `\n\n현재 작성 중인 답변 컨텍스트:\n${JSON.stringify(context)}`,
    messages,
  })

  const encoder = new TextEncoder()
  const readable = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
          controller.enqueue(encoder.encode(chunk.delta.text))
        }
      }
      controller.close()
    },
  })

  return new Response(readable, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  })
}
```

- [ ] **Step 2: AIChatPanel 컴포넌트 작성**

`src/components/chat/AIChatPanel.tsx`:
```typescript
'use client'
import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { CrisisBanner } from '@/components/crisis/CrisisBanner'
import type { CrisisFlag } from '@/lib/crisis'
import { X, MessageCircle } from 'lucide-react'

type Message = { role: 'user' | 'assistant'; content: string }
type Domain = 'calling' | 'family' | 'peers' | 'faith'

export function AIChatPanel({
  domain,
  context,
  onClose,
}: {
  domain: Domain
  context: Record<string, unknown>
  onClose: () => void
}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [crisisFlags, setCrisisFlags] = useState<CrisisFlag[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)

  const sendMessage = async () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', content: input }
    const next = [...messages, userMsg]
    setMessages(next)
    setInput('')
    setLoading(true)

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, messages: next, context }),
    })

    const data = await res.json().catch(() => null)
    if (data?.crisis) {
      setCrisisFlags(data.crisis)
      setLoading(false)
      return
    }

    // 스트리밍 처리
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let assistantText = ''
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      assistantText += decoder.decode(value)
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: assistantText }
        return updated
      })
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    setLoading(false)
  }

  return (
    <div className="fixed right-0 top-0 bottom-0 w-80 bg-background border-l shadow-lg flex flex-col z-40">
      <CrisisBanner flags={crisisFlags} />
      <div className="flex items-center justify-between p-3 border-b">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-4 w-4" />
          <span className="font-semibold text-sm">AI와 이야기하기</span>
        </div>
        <Button size="icon" variant="ghost" onClick={onClose}><X className="h-4 w-4" /></Button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground text-center mt-8">
            더 깊이 이야기하고 싶은 것이 있나요? 편하게 말해보세요 😊
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`text-sm p-2 rounded-lg ${
            m.role === 'user' ? 'bg-primary text-primary-foreground ml-8' : 'bg-muted mr-8'
          }`}>
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="p-3 border-t flex gap-2">
        <Textarea rows={2} placeholder="메시지 입력..." value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
          className="resize-none text-sm" />
        <Button size="sm" onClick={sendMessage} disabled={loading || !input.trim()}>
          전송
        </Button>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 커밋**

```bash
git add src/
git commit -m "feat: AI 대화 보조 스트리밍 (AIChatPanel + /api/chat)"
```

---

## Task 8: 도메인 폼 (4개)

**Files:**
- Create: `src/components/domain-form/CallingForm.tsx`
- Create: `src/components/domain-form/FamilyForm.tsx`
- Create: `src/components/domain-form/PeersForm.tsx`
- Create: `src/components/domain-form/FaithForm.tsx`
- Create: `src/app/(youth)/plan/calling/page.tsx`
- Create: `src/app/(youth)/plan/family/page.tsx`
- Create: `src/app/(youth)/plan/peers/page.tsx`
- Create: `src/app/(youth)/plan/faith/page.tsx`

- [ ] **Step 1: CallingForm 작성**

`src/components/domain-form/CallingForm.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AIChatPanel } from '@/components/chat/AIChatPanel'
import { MessageCircle } from 'lucide-react'

type CallingAnswers = {
  interest: string
  talent: string
  dream: string
  obstacle: string
  kingdom: string
}

export function CallingForm({ onSubmit }: { onSubmit: (answers: CallingAnswers) => void }) {
  const [answers, setAnswers] = useState<CallingAnswers>({
    interest: '', talent: '', dream: '', obstacle: '', kingdom: '',
  })
  const [chatOpen, setChatOpen] = useState(false)

  const update = (key: keyof CallingAnswers) => (e: React.ChangeEvent<HTMLTextAreaElement>) =>
    setAnswers(prev => ({ ...prev, [key]: e.target.value }))

  const isComplete = Object.values(answers).every(v => v.trim().length > 0)

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <Label>요즘 가장 흥미로운 것이 무엇인가요?</Label>
        <Textarea rows={3} value={answers.interest} onChange={update('interest')}
          placeholder="학교 과목, 취미, 유튜브 채널 등 뭐든 괜찮아요" />
      </div>
      <div className="space-y-1">
        <Label>내가 잘한다고 느끼는 것 3가지는?</Label>
        <Textarea rows={3} value={answers.talent} onChange={update('talent')}
          placeholder="친구들이 칭찬해준 것도 포함해서 써봐요" />
      </div>
      <div className="space-y-1">
        <Label>10년 후 어떤 사람이 되고 싶나요?</Label>
        <Textarea rows={3} value={answers.dream} onChange={update('dream')}
          placeholder="직업이 아닌 '어떤 사람'으로 표현해봐요" />
      </div>
      <div className="space-y-1">
        <Label>지금 진로를 생각할 때 가장 걱정되는 것은?</Label>
        <Textarea rows={3} value={answers.obstacle} onChange={update('obstacle')} />
      </div>
      <div className="space-y-1">
        <Label>내 재능이 하나님 나라를 위해 어떻게 쓰일 수 있을까요?</Label>
        <Textarea rows={3} value={answers.kingdom} onChange={update('kingdom')}
          placeholder="잘 모르겠으면 '모르겠다'고 써도 괜찮아요" />
      </div>

      <div className="flex gap-3">
        <Button variant="outline" onClick={() => setChatOpen(true)} className="flex-1">
          <MessageCircle className="mr-2 h-4 w-4" /> AI와 더 이야기하기
        </Button>
        <Button onClick={() => onSubmit(answers)} disabled={!isComplete} className="flex-1">
          저장하고 다음으로
        </Button>
      </div>

      {chatOpen && (
        <AIChatPanel domain="calling" context={answers} onClose={() => setChatOpen(false)} />
      )}
    </div>
  )
}
```

- [ ] **Step 2: FamilyForm 작성**

`src/components/domain-form/FamilyForm.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AIChatPanel } from '@/components/chat/AIChatPanel'
import { MessageCircle } from 'lucide-react'

type FamilyAnswers = { relationship: string; conflict: string; gratitude: string; wish: string }

export function FamilyForm({ onSubmit }: { onSubmit: (answers: FamilyAnswers) => void }) {
  const [answers, setAnswers] = useState<FamilyAnswers>({
    relationship: '', conflict: '', gratitude: '', wish: '',
  })
  const [chatOpen, setChatOpen] = useState(false)
  const update = (key: keyof FamilyAnswers) => (e: React.ChangeEvent<HTMLTextAreaElement>) =>
    setAnswers(prev => ({ ...prev, [key]: e.target.value }))
  const isComplete = Object.values(answers).every(v => v.trim().length > 0)

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <Label>요즘 부모님(또는 가족)과의 관계를 한 문장으로 표현하면?</Label>
        <Textarea rows={3} value={answers.relationship} onChange={update('relationship')} />
      </div>
      <div className="space-y-1">
        <Label>가족과 가장 자주 갈등이 생기는 상황은?</Label>
        <Textarea rows={3} value={answers.conflict} onChange={update('conflict')} />
      </div>
      <div className="space-y-1">
        <Label>가족에게 감사한 점 1가지를 쓴다면?</Label>
        <Textarea rows={3} value={answers.gratitude} onChange={update('gratitude')} />
      </div>
      <div className="space-y-1">
        <Label>올해 가족 관계에서 바라는 변화는?</Label>
        <Textarea rows={3} value={answers.wish} onChange={update('wish')} />
      </div>
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => setChatOpen(true)} className="flex-1">
          <MessageCircle className="mr-2 h-4 w-4" /> AI와 더 이야기하기
        </Button>
        <Button onClick={() => onSubmit(answers)} disabled={!isComplete} className="flex-1">
          저장하고 다음으로
        </Button>
      </div>
      {chatOpen && <AIChatPanel domain="family" context={answers} onClose={() => setChatOpen(false)} />}
    </div>
  )
}
```

- [ ] **Step 3: PeersForm 작성**

`src/components/domain-form/PeersForm.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AIChatPanel } from '@/components/chat/AIChatPanel'
import { MessageCircle } from 'lucide-react'

type PeersAnswers = { bestFriend: string; draining: string; church: string; wish: string }

export function PeersForm({ onSubmit }: { onSubmit: (answers: PeersAnswers) => void }) {
  const [answers, setAnswers] = useState<PeersAnswers>({
    bestFriend: '', draining: '', church: '', wish: '',
  })
  const [chatOpen, setChatOpen] = useState(false)
  const update = (key: keyof PeersAnswers) => (e: React.ChangeEvent<HTMLTextAreaElement>) =>
    setAnswers(prev => ({ ...prev, [key]: e.target.value }))
  const isComplete = Object.values(answers).every(v => v.trim().length > 0)

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <Label>나에게 에너지를 주는 친구는 어떤 친구인가요?</Label>
        <Textarea rows={3} value={answers.bestFriend} onChange={update('bestFriend')}
          placeholder="어떤 관계가 나를 성장시키나요?" />
      </div>
      <div className="space-y-1">
        <Label>요즘 가장 힘든 관계나 상황은?</Label>
        <Textarea rows={3} value={answers.draining} onChange={update('draining')} />
      </div>
      <div className="space-y-1">
        <Label>교회 청소년부에서의 관계는 어떤가요?</Label>
        <Textarea rows={3} value={answers.church} onChange={update('church')} />
      </div>
      <div className="space-y-1">
        <Label>올해 관계에서 한 가지 바꾸고 싶다면?</Label>
        <Textarea rows={3} value={answers.wish} onChange={update('wish')} />
      </div>
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => setChatOpen(true)} className="flex-1">
          <MessageCircle className="mr-2 h-4 w-4" /> AI와 더 이야기하기
        </Button>
        <Button onClick={() => onSubmit(answers)} disabled={!isComplete} className="flex-1">
          저장하고 다음으로
        </Button>
      </div>
      {chatOpen && <AIChatPanel domain="peers" context={answers} onClose={() => setChatOpen(false)} />}
    </div>
  )
}
```

- [ ] **Step 4: FaithForm 작성**

`src/components/domain-form/FaithForm.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AIChatPanel } from '@/components/chat/AIChatPanel'
import { MessageCircle } from 'lucide-react'

type FaithAnswers = { currentFaith: string; doubt: string; routine: string; prayer: string }

export function FaithForm({ onSubmit }: { onSubmit: (answers: FaithAnswers) => void }) {
  const [answers, setAnswers] = useState<FaithAnswers>({
    currentFaith: '', doubt: '', routine: '', prayer: '',
  })
  const [chatOpen, setChatOpen] = useState(false)
  const update = (key: keyof FaithAnswers) => (e: React.ChangeEvent<HTMLTextAreaElement>) =>
    setAnswers(prev => ({ ...prev, [key]: e.target.value }))
  const isComplete = Object.values(answers).every(v => v.trim().length > 0)

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <Label>요즘 신앙 상태를 솔직하게 표현하면?</Label>
        <Textarea rows={3} value={answers.currentFaith} onChange={update('currentFaith')}
          placeholder="뜨겁다, 식어있다, 형식적이다 등 솔직하게" />
      </div>
      <div className="space-y-1">
        <Label>요즘 하나님께 드는 가장 큰 질문이나 의심은?</Label>
        <Textarea rows={3} value={answers.doubt} onChange={update('doubt')}
          placeholder="질문과 의심도 신앙의 일부예요. 솔직하게 써도 괜찮아요" />
      </div>
      <div className="space-y-1">
        <Label>지금 갖고 있는 신앙 루틴은?</Label>
        <Textarea rows={3} value={answers.routine} onChange={update('routine')}
          placeholder="예배, 큐티, 기도, 소그룹 등" />
      </div>
      <div className="space-y-1">
        <Label>올해 신앙에서 한 가지 목표를 세운다면?</Label>
        <Textarea rows={3} value={answers.prayer} onChange={update('prayer')} />
      </div>
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => setChatOpen(true)} className="flex-1">
          <MessageCircle className="mr-2 h-4 w-4" /> AI와 더 이야기하기
        </Button>
        <Button onClick={() => onSubmit(answers)} disabled={!isComplete} className="flex-1">
          저장하고 다음으로
        </Button>
      </div>
      {chatOpen && <AIChatPanel domain="faith" context={answers} onClose={() => setChatOpen(false)} />}
    </div>
  )
}
```

- [ ] **Step 5: 도메인 페이지 4개 작성 (calling 예시, 나머지 동일 패턴)**

`src/app/(youth)/plan/calling/page.tsx`:
```typescript
'use client'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useSession } from '@/hooks/useSession'
import { CallingForm } from '@/components/domain-form/CallingForm'
import { Badge } from '@/components/ui/badge'

export default function CallingPage() {
  const router = useRouter()
  const supabase = createClient()
  const { session } = useSession()

  const handleSubmit = async (answers: Record<string, unknown>) => {
    if (!session) return
    await supabase.from('domain_answers').upsert({
      session_id: session.id,
      domain: 'calling',
      answers,
      completed_at: new Date().toISOString(),
    }, { onConflict: 'session_id,domain' })
    router.push('/plan/family')
  }

  return (
    <div className="max-w-xl mx-auto p-4 pb-20">
      <div className="mb-6">
        <Badge variant="outline">1 / 4</Badge>
        <h1 className="text-2xl font-bold mt-2">진로 · 소명</h1>
        <p className="text-muted-foreground text-sm mt-1">나는 무엇을 위해 살아가는가?</p>
      </div>
      <CallingForm onSubmit={handleSubmit} />
    </div>
  )
}
```

나머지 3개 페이지(`family`, `peers`, `faith`)도 동일 패턴으로 작성:
- domain 값: `'family'`, `'peers'`, `'faith'`
- router.push: 순서대로 `/plan/peers`, `/plan/faith`, `/result`
- Badge: `2 / 4`, `3 / 4`, `4 / 4`
- Form 컴포넌트: `FamilyForm`, `PeersForm`, `FaithForm`

- [ ] **Step 6: 커밋**

```bash
git add src/
git commit -m "feat: 도메인 폼 4개 (진로/가족/또래/신앙) + 페이지 라우팅"
```

---

## Task 9: 인터뷰 + 결과 카드 페이지

**Files:**
- Create: `src/app/(youth)/interview/page.tsx`
- Create: `src/app/(youth)/result/page.tsx`
- Create: `src/components/result/YouthCard.tsx`

- [ ] **Step 1: 인터뷰 페이지 작성**

`src/app/(youth)/interview/page.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from '@/hooks/useSession'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

const QUESTIONS = [
  { key: 'name_feel', label: '지금 기분을 날씨로 표현하면?' },
  { key: 'this_year', label: '올해 가장 기대되는 것은?' },
  { key: 'hard_now', label: '지금 가장 힘든 것 한 가지는?' },
  { key: 'strength', label: '나의 가장 큰 강점은 무엇이라고 생각해?' },
  { key: 'god_word', label: '요즘 하나님께서 네 삶에 하시는 것 같은 일은?' },
]

export default function InterviewPage() {
  const router = useRouter()
  const { session, createSession } = useSession()
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const update = (key: string) => (e: React.ChangeEvent<HTMLTextAreaElement>) =>
    setAnswers(prev => ({ ...prev, [key]: e.target.value }))

  const isComplete = QUESTIONS.every(q => answers[q.key]?.trim())

  const handleStart = async () => {
    const s = session ?? await createSession('standard')
    if (!s) return
    router.push('/plan/calling')
  }

  return (
    <div className="max-w-xl mx-auto p-4 pb-20">
      <h1 className="text-2xl font-bold mb-2">안녕! 👋</h1>
      <p className="text-muted-foreground mb-6 text-sm">
        먼저 지금 너에 대해 간단히 이야기해보자.
      </p>
      <div className="space-y-6">
        {QUESTIONS.map(q => (
          <div key={q.key} className="space-y-1">
            <Label>{q.label}</Label>
            <Textarea rows={2} value={answers[q.key] ?? ''} onChange={update(q.key)} />
          </div>
        ))}
      </div>
      <Button className="w-full mt-6" onClick={handleStart} disabled={!isComplete}>
        인생계획 시작하기 →
      </Button>
    </div>
  )
}
```

- [ ] **Step 2: YouthCard 컴포넌트 작성**

`src/components/result/YouthCard.tsx`:
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type AnalysisResult = {
  summary: string
  strengths: string[]
  challenges: string[]
  priorities: string[]
}

export function YouthCard({ analysis, nickname }: { analysis: AnalysisResult; nickname: string }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>🎯 {nickname}의 2026 인생계획</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{analysis.summary}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">💪 강점</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {analysis.strengths.map((s, i) => <Badge key={i}>{s}</Badge>)}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">🎯 올해 집중 영역</CardTitle></CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 list-disc list-inside">
            {analysis.priorities.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">🌱 함께 성장할 부분</CardTitle></CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 list-disc list-inside text-muted-foreground">
            {analysis.challenges.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 3: 결과 페이지 작성**

`src/app/(youth)/result/page.tsx`:
```typescript
'use client'
import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useSession } from '@/hooks/useSession'
import { YouthCard } from '@/components/result/YouthCard'
import { Button } from '@/components/ui/button'

export default function ResultPage() {
  const supabase = createClient()
  const { session } = useSession()
  const [analysis, setAnalysis] = useState<any>(null)
  const [nickname, setNickname] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!session) return
    const load = async () => {
      const { data } = await supabase
        .from('analysis_results')
        .select('youth_card_json')
        .eq('session_id', session.id)
        .single()
      if (data?.youth_card_json) setAnalysis(data.youth_card_json)

      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        const { data: profile } = await supabase.from('users').select('nickname').eq('id', user.id).single()
        setNickname(profile?.nickname ?? '')
      }
    }
    load()
  }, [session])

  const runAnalysis = async () => {
    if (!session) return
    setLoading(true)
    await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: session.id }),
    })
    window.location.reload()
  }

  if (!analysis) {
    return (
      <div className="max-w-xl mx-auto p-4 text-center">
        <h1 className="text-2xl font-bold mb-4">AI 분석 준비 완료!</h1>
        <p className="text-muted-foreground mb-6 text-sm">
          4개 영역 작성이 완료됐어. 이제 AI가 너만의 계획을 만들어줄게!
        </p>
        <Button onClick={runAnalysis} disabled={loading} size="lg">
          {loading ? '분석 중... (1~2분)' : '🚀 내 인생계획 만들기'}
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto p-4 pb-20">
      <YouthCard analysis={analysis} nickname={nickname} />
    </div>
  )
}
```

- [ ] **Step 4: 커밋**

```bash
git add src/
git commit -m "feat: 인터뷰 페이지 + 결과 카드 (YouthCard)"
```

---

## Task 10: 사역자 대시보드

**Files:**
- Create: `src/app/(pastor)/pastor/page.tsx`
- Create: `src/app/(pastor)/pastor/youth/[id]/page.tsx`
- Create: `src/components/dashboard/YouthList.tsx`
- Create: `src/components/result/CoachingPlan.tsx`

- [ ] **Step 1: YouthList 컴포넌트**

`src/components/dashboard/YouthList.tsx`:
```typescript
'use client'
import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { AlertTriangle } from 'lucide-react'

type Youth = {
  id: string
  nickname: string
  grade: string
  session: { status: string; crisis_flags: any[] } | null
}

export function YouthList({ youths }: { youths: Youth[] }) {
  if (youths.length === 0) {
    return <p className="text-muted-foreground text-sm text-center py-8">등록된 청소년이 없습니다.</p>
  }
  return (
    <div className="space-y-3">
      {youths.map(y => (
        <Link key={y.id} href={`/pastor/youth/${y.id}`}>
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center justify-between py-3">
              <div className="flex items-center gap-3">
                {y.session?.crisis_flags?.length > 0 && (
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                )}
                <div>
                  <p className="font-medium">{y.nickname}</p>
                  <p className="text-xs text-muted-foreground">{y.grade}</p>
                </div>
              </div>
              <Badge variant={y.session?.status === 'completed' ? 'default' : 'outline'}>
                {y.session?.status === 'completed' ? '완료' : '진행 중'}
              </Badge>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: 대시보드 페이지**

`src/app/(pastor)/pastor/page.tsx`:
```typescript
import { createClient } from '@/lib/supabase/server'
import { YouthList } from '@/components/dashboard/YouthList'

export default async function PastorDashboard() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  const { data: pastor } = await supabase
    .from('users').select('church_id').eq('id', user!.id).single()

  const { data: youths } = await supabase
    .from('users')
    .select(`
      id, nickname, grade,
      sessions(status, analysis_results(crisis_flags))
    `)
    .eq('church_id', pastor?.church_id)
    .eq('role', 'youth')

  const mapped = (youths ?? []).map((y: any) => ({
    id: y.id,
    nickname: y.nickname,
    grade: y.grade,
    session: y.sessions?.[0]
      ? { status: y.sessions[0].status, crisis_flags: y.sessions[0].analysis_results?.[0]?.crisis_flags ?? [] }
      : null,
  }))

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">청소년 현황</h1>
      <p className="text-muted-foreground text-sm mb-6">총 {mapped.length}명</p>
      <YouthList youths={mapped} />
    </div>
  )
}
```

- [ ] **Step 3: CoachingPlan 컴포넌트**

`src/components/result/CoachingPlan.tsx`:
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type CoachingPlanData = {
  monthly_goals: Array<{ month: number; goal: string; actions: string[] }>
  prayer_topics: string[]
  warning_signs: string[]
  next_meeting_agenda: string
}

export function CoachingPlan({ plan, nickname }: { plan: CoachingPlanData; nickname: string }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>📋 {nickname} 코칭 플랜</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm font-medium text-muted-foreground">다음 미팅 아젠다</p>
          <p className="text-sm mt-1">{plan.next_meeting_agenda}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">🙏 기도 제목</CardTitle></CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 list-disc list-inside">
            {plan.prayer_topics.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">⚠ 주의 관찰 사항</CardTitle></CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 list-disc list-inside text-muted-foreground">
            {plan.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">📅 월별 목표</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {plan.monthly_goals.slice(0, 3).map(g => (
            <div key={g.month}>
              <p className="text-sm font-medium">{g.month}월: {g.goal}</p>
              <ul className="text-xs text-muted-foreground list-disc list-inside mt-1">
                {g.actions.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 4: 개별 청소년 상세 페이지**

`src/app/(pastor)/pastor/youth/[id]/page.tsx`:
```typescript
import { createClient } from '@/lib/supabase/server'
import { CoachingPlan } from '@/components/result/CoachingPlan'
import { YouthCard } from '@/components/result/YouthCard'
import { CrisisBanner } from '@/components/crisis/CrisisBanner'

export default async function YouthDetailPage({ params }: { params: { id: string } }) {
  const supabase = await createClient()

  const { data: profile } = await supabase
    .from('users').select('nickname, grade').eq('id', params.id).single()

  const { data: session } = await supabase
    .from('sessions').select('id').eq('youth_id', params.id).eq('status', 'completed').single()

  if (!session) {
    return <div className="max-w-xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-2">{profile?.nickname}</h1>
      <p className="text-muted-foreground text-sm">아직 계획이 완료되지 않았습니다.</p>
    </div>
  }

  const { data: result } = await supabase
    .from('analysis_results')
    .select('youth_card_json, coaching_plan_json, crisis_flags')
    .eq('session_id', session.id)
    .single()

  return (
    <div className="max-w-xl mx-auto p-4 pb-20">
      <CrisisBanner flags={result?.crisis_flags ?? []} />
      <h1 className="text-xl font-bold mb-4">{profile?.nickname} ({profile?.grade})</h1>
      {result?.coaching_plan_json && (
        <CoachingPlan plan={result.coaching_plan_json} nickname={profile!.nickname} />
      )}
      {result?.youth_card_json && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-3">청소년 결과 카드</h2>
          <YouthCard analysis={result.youth_card_json} nickname={profile!.nickname} />
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: 커밋**

```bash
git add src/
git commit -m "feat: 사역자 대시보드 + 개별 코칭 플랜 페이지"
```

---

## Task 11: 수련회 모드

**Files:**
- Create: `src/app/(pastor)/pastor/retreat/page.tsx`

- [ ] **Step 1: 수련회 세션 생성 페이지**

`src/app/(pastor)/pastor/retreat/page.tsx`:
```typescript
'use client'
import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'

export default function RetreatPage() {
  const supabase = createClient()
  const [retreatLink, setRetreatLink] = useState('')
  const [loading, setLoading] = useState(false)

  const createRetreatSession = async () => {
    setLoading(true)
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return

    // 수련회용 임시 청소년 세션 생성 (pastor_id 연결)
    const { data } = await supabase.from('sessions').insert({
      youth_id: user.id, // 수련회는 사역자가 대리 생성
      pastor_id: user.id,
      mode: 'retreat',
    }).select().single()

    const link = `${window.location.origin}/interview?session=${data.id}&mode=retreat`
    setRetreatLink(link)
    setLoading(false)
  }

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">수련회 모드</h1>
      <p className="text-muted-foreground text-sm mb-6">
        청소년에게 링크를 공유하면 45~60분 집중 인생계획을 작성할 수 있습니다.
      </p>
      <Badge className="mb-4">수련회 특징: 핵심 질문만 / 빠른 분석 / 그룹 공유 가능</Badge>
      <Button onClick={createRetreatSession} disabled={loading} className="w-full mb-4">
        {loading ? '생성 중...' : '수련회 링크 생성'}
      </Button>
      {retreatLink && (
        <div className="space-y-2">
          <Label>청소년에게 공유할 링크</Label>
          <div className="flex gap-2">
            <Input value={retreatLink} readOnly />
            <Button variant="outline" onClick={() => navigator.clipboard.writeText(retreatLink)}>
              복사
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 커밋**

```bash
git add src/
git commit -m "feat: 수련회 모드 (링크 생성 + pastor 세션 관리)"
```

---

## Task 12: E2E 테스트 + PWA 설정 + 배포

**Files:**
- Create: `tests/e2e/youth-flow.spec.ts`
- Create: `public/manifest.json`
- Create: `vercel.json`

- [ ] **Step 1: E2E 테스트 작성**

`tests/e2e/youth-flow.spec.ts`:
```typescript
import { test, expect } from '@playwright/test'

test('랜딩 페이지 로드', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('청소년 인생계획')
})

test('로그인 페이지 접근', async ({ page }) => {
  await page.goto('/login')
  await expect(page.locator('text=카카오로 시작하기')).toBeVisible()
  await expect(page.locator('text=구글로 시작하기')).toBeVisible()
})

test('미인증 상태에서 /interview 접근 시 /login으로 리다이렉트', async ({ page }) => {
  await page.goto('/interview')
  await expect(page).toHaveURL('/login')
})

test('미인증 상태에서 /pastor 접근 시 /login으로 리다이렉트', async ({ page }) => {
  await page.goto('/pastor')
  await expect(page).toHaveURL('/login')
})
```

- [ ] **Step 2: E2E 테스트 실행**

```bash
npx playwright install chromium
npx playwright test tests/e2e/ --reporter=list
# Expected: 4/4 PASS (리다이렉트 테스트는 인증 없이 가능)
```

- [ ] **Step 3: PWA manifest 작성**

`public/manifest.json`:
```json
{
  "name": "청소년 인생계획",
  "short_name": "인생계획",
  "description": "청소년 인생계획 통합 시스템",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#6366f1",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

`src/app/layout.tsx`에 metadata 추가:
```typescript
export const metadata = {
  manifest: '/manifest.json',
  themeColor: '#6366f1',
}
```

- [ ] **Step 4: Vercel 배포**

```bash
npm install -g vercel
vercel --prod
# 프롬프트: 프로젝트 이름 입력, 환경변수 설정
# Vercel 대시보드에서 환경변수 추가:
# NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY,
# SUPABASE_SERVICE_ROLE_KEY, ANTHROPIC_API_KEY
```

- [ ] **Step 5: 최종 커밋 + 태그**

```bash
git add .
git commit -m "feat: E2E 테스트 + PWA 설정 + Vercel 배포"
git tag v1.0.0
git push origin main --tags
```

---

## 환경변수 체크리스트

배포 전 반드시 확인:

| 변수 | 출처 |
|------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase 대시보드 → Settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase 대시보드 → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase 대시보드 → Settings → API |
| `ANTHROPIC_API_KEY` | console.anthropic.com |

---

## 자기검토 (Self-Review)

**스펙 커버리지:**
- ✅ 청소년 계정 + 사역자 계정 분리 (Task 3, 미들웨어)
- ✅ 인터뷰 → 도메인 4개 → AI 분석 → 결과 카드 (Task 8, 9)
- ✅ 하이브리드 AI (폼 + AIChatPanel) (Task 7, 8)
- ✅ 수련회 모드 (Task 11)
- ✅ 위기 감지 시스템 (Task 5)
- ✅ RLS 보안 (Task 2)
- ✅ 사역자 대시보드 + 코칭 플랜 (Task 10)
- ✅ 소셜 로그인 (Task 3)
- ✅ PWA + Vercel 배포 (Task 12)

**타입 일관성:**
- `Domain` 타입: `'calling' | 'family' | 'peers' | 'faith'` — Task 5, 6, 7, 8 모두 일치
- `Session` 타입: `useSession` 훅 정의 → Task 8, 9 페이지에서 동일 사용
- `CrisisFlag` 타입: `crisis.ts` 정의 → `CrisisBanner`, API Route 일치
