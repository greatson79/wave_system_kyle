# 홈 페이지 및 역할 기반 리다이렉트 구현 계획

## 개요

### 모듈 목록

| 모듈 | 위치 | 설명 |
|------|------|------|
| **LandingPage** | `src/features/landing/components/LandingPage.tsx` | 비로그인 사용자용 랜딩페이지 컴포넌트 |
| **RootPage** | `src/app/page.tsx` | 루트 경로에서 인증 상태 및 역할에 따른 리다이렉트 처리 |
| **OnboardingPage** | `src/app/onboarding/page.tsx` | 프로필 정보 입력 페이지 (이름, 휴대폰, 약관동의) |
| **RoleSelectPage** | `src/app/onboarding/role-select/page.tsx` | 역할 선택 페이지 (Learner/Instructor) |
| **ProfileService** | `src/features/profile/backend/service.ts` | 프로필 CRUD 서비스 로직 |
| **ProfileRoute** | `src/features/profile/backend/route.ts` | 프로필 관련 API 라우트 |
| **ProfileSchema** | `src/features/profile/backend/schema.ts` | 프로필 요청/응답 스키마 |
| **useProfile** | `src/features/profile/hooks/useProfile.ts` | 프로필 조회 React Query 훅 |
| **useUpdateProfile** | `src/features/profile/hooks/useUpdateProfile.ts` | 프로필 수정 React Query 훅 |

---

## Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[/ 루트 접근]
        B[LandingPage<br/>비로그인 UI]
        C[OnboardingPage<br/>프로필 입력]
        D[RoleSelectPage<br/>역할 선택]
        E[/courses<br/>Learner용]
        F[/instructor/dashboard<br/>Instructor용]
    end

    subgraph "Server Components"
        G[RootPage<br/>Server Component]
        H[인증 상태 확인<br/>getSession]
        I[프로필 조회<br/>profiles 테이블]
    end

    subgraph "Backend API"
        J[ProfileRoute<br/>POST /api/profile<br/>PUT /api/profile]
        K[ProfileService<br/>createProfile<br/>updateProfile]
        L[(Supabase<br/>profiles 테이블)]
    end

    subgraph "React Query Hooks"
        M[useProfile<br/>프로필 조회]
        N[useUpdateProfile<br/>프로필 수정]
    end

    A --> G
    G --> H
    H -->|비인증| B
    H -->|인증| I
    I -->|프로필 없음| C
    I -->|역할 없음| D
    I -->|Learner| E
    I -->|Instructor| F

    C --> N
    D --> N
    N --> J
    J --> K
    K --> L

    M --> J
    J --> K
    K --> L
```

---

## Implementation Plan

### 1. Landing Page Component

**파일**: `src/features/landing/components/LandingPage.tsx`

**목적**: 비로그인 사용자에게 서비스 소개 및 CTA 제공

**구현 내용**:
- Hero Section: 서비스 타이틀, 설명, CTA 버튼
- Features Section: 주요 기능 3가지 (코스, 과제 관리, 피드백)
- CTA Section: 회원가입 유도

**Dependencies**:
- `lucide-react`: 아이콘 (BookOpen, ClipboardList, Award)
- `@/components/ui/button`: shadcn-ui Button 컴포넌트
- `next/link`: 페이지 링크

**QA Sheet**:

| 테스트 항목 | 예상 결과 |
|------------|----------|
| 페이지 렌더링 | Hero, Features, CTA 섹션이 모두 표시됨 |
| "시작하기" 버튼 클릭 | `/signup` 으로 이동 |
| "로그인" 버튼 클릭 | `/login` 으로 이동 |
| "무료로 가입하기" 버튼 클릭 | `/signup` 으로 이동 |
| 반응형 디자인 | 모바일/태블릿/데스크톱에서 정상 표시 |

---

### 2. Root Page (Server Component)

**파일**: `src/app/page.tsx`

**목적**: 인증 상태 및 역할에 따라 적절한 페이지로 리다이렉트 또는 랜딩페이지 표시

**구현 내용**:
```typescript
export const dynamic = 'force-dynamic'
export const revalidate = 0

export default async function RootPage() {
  // 1. 인증 확인
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()

  // 비로그인: 랜딩페이지 렌더링
  if (!session) {
    return <LandingPage />
  }

  // 2. 프로필 확인
  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', session.user.id)
    .maybeSingle()

  // 프로필 없음: 온보딩
  if (!profile) {
    redirect('/onboarding')
  }

  // 역할 없음: 역할 선택
  if (!profile.role) {
    redirect('/onboarding/role-select')
  }

  // 3. 역할 기반 리다이렉트
  if (profile.role === 'learner') {
    redirect('/courses')
  }

  if (profile.role === 'instructor') {
    redirect('/instructor/dashboard')
  }

  // Fallback
  redirect('/login')
}
```

**Dependencies**:
- `next/navigation`: redirect 함수
- `@/lib/supabase/server-client`: createSupabaseServerClient
- `@/features/landing/components/LandingPage`: 랜딩페이지 컴포넌트

**Unit Tests**:

| 시나리오 | 입력 | 예상 출력 |
|---------|------|----------|
| 비로그인 사용자 | session = null | LandingPage 렌더링 |
| 로그인 + 프로필 없음 | session 있음, profile = null | redirect('/onboarding') |
| 로그인 + 역할 없음 | session 있음, profile.role = null | redirect('/onboarding/role-select') |
| Learner 사용자 | session 있음, profile.role = 'learner' | redirect('/courses') |
| Instructor 사용자 | session 있음, profile.role = 'instructor' | redirect('/instructor/dashboard') |
| Operator 사용자 | session 있음, profile.role = 'operator' | redirect('/login') (fallback) |

---

### 3. Onboarding Page

**파일**: `src/app/onboarding/page.tsx`

**목적**: 신규 사용자의 프로필 정보 수집 (이름, 휴대폰번호, 약관동의)

**구현 내용**:
- 서버 컴포넌트로 인증 확인 (비로그인 시 `/login` 리다이렉트)
- 프로필이 이미 있으면 `/onboarding/role-select`로 리다이렉트
- 클라이언트 컴포넌트: `OnboardingForm` 렌더링

**Dependencies**:
- `next/navigation`: redirect
- `@/lib/supabase/server-client`: 인증 확인
- `@/features/onboarding/components/OnboardingForm`: 온보딩 폼

**QA Sheet**:

| 테스트 항목 | 예상 결과 |
|------------|----------|
| 비로그인 접근 | `/login`으로 리다이렉트 |
| 프로필 이미 존재 | `/onboarding/role-select`로 리다이렉트 |
| 정상 접근 | 온보딩 폼 표시 |
| 필수 입력값 누락 | 제출 버튼 비활성화 |
| 약관 미동의 | 제출 버튼 비활성화 |
| 정상 제출 | 프로필 생성 후 `/onboarding/role-select`로 이동 |

---

### 4. Role Select Page

**파일**: `src/app/onboarding/role-select/page.tsx`

**목적**: 사용자 역할 선택 (Learner/Instructor)

**구현 내용**:
- 서버 컴포넌트로 인증 및 프로필 확인
- 프로필 없으면 `/onboarding`으로 리다이렉트
- 역할이 이미 설정되어 있으면 역할에 따라 리다이렉트
- 클라이언트 컴포넌트: `RoleSelectForm` 렌더링

**Dependencies**:
- `next/navigation`: redirect
- `@/lib/supabase/server-client`: 인증 확인
- `@/features/onboarding/components/RoleSelectForm`: 역할 선택 폼

**QA Sheet**:

| 테스트 항목 | 예상 결과 |
|------------|----------|
| 비로그인 접근 | `/login`으로 리다이렉트 |
| 프로필 없음 | `/onboarding`으로 리다이렉트 |
| 역할 이미 설정됨 | 역할에 따라 메인 페이지로 리다이렉트 |
| Learner 선택 | role='learner' 저장 후 `/courses`로 이동 |
| Instructor 선택 | role='instructor' 저장 후 `/instructor/dashboard`로 이동 |

---

### 5. OnboardingForm Component

**파일**: `src/features/onboarding/components/OnboardingForm.tsx`

**목적**: 프로필 정보 입력 폼

**구현 내용**:
- react-hook-form + zod 사용
- 필드: name (이름), phone (휴대폰번호), termsAgreed (약관동의)
- useCreateProfile 훅으로 API 호출
- 성공 시 `/onboarding/role-select`로 이동

**Schema**:
```typescript
const onboardingSchema = z.object({
  name: z.string().min(1, '이름을 입력해주세요'),
  phone: z.string().regex(/^[0-9]{10,11}$/, '올바른 휴대폰번호를 입력해주세요'),
  termsAgreed: z.boolean().refine(val => val === true, '약관에 동의해주세요'),
})
```

**Dependencies**:
- `react-hook-form`: 폼 상태 관리
- `zod`: 스키마 검증
- `@/features/profile/hooks/useCreateProfile`: 프로필 생성 훅
- `@/components/ui/button`, `@/components/ui/input`, etc.

**QA Sheet**:

| 테스트 항목 | 예상 결과 |
|------------|----------|
| 이름 미입력 | 에러 메시지 표시 |
| 전화번호 형식 오류 | 에러 메시지 표시 |
| 약관 미동의 | 제출 버튼 비활성화 |
| 정상 입력 + 제출 | API 호출 후 role-select로 이동 |
| API 에러 | 에러 토스트 표시 |

---

### 6. RoleSelectForm Component

**파일**: `src/features/onboarding/components/RoleSelectForm.tsx`

**목적**: 역할 선택 폼

**구현 내용**:
- Learner/Instructor 카드 UI
- 각 카드 클릭 시 역할 선택
- useUpdateProfile 훅으로 역할 업데이트
- 성공 시 역할에 따라 리다이렉트

**Dependencies**:
- `@/features/profile/hooks/useUpdateProfile`: 프로필 수정 훅
- `@/components/ui/button`, `@/components/ui/card`
- `lucide-react`: 아이콘

**QA Sheet**:

| 테스트 항목 | 예상 결과 |
|------------|----------|
| Learner 카드 클릭 | role='learner' 저장 후 `/courses`로 이동 |
| Instructor 카드 클릭 | role='instructor' 저장 후 `/instructor/dashboard`로 이동 |
| API 에러 | 에러 토스트 표시 |
| 로딩 중 | 버튼 비활성화 |

---

### 7. Profile Backend Service

**파일**: `src/features/profile/backend/service.ts`

**목적**: 프로필 CRUD 비즈니스 로직

**구현 내용**:
```typescript
// 프로필 조회
export const getProfile = async (supabase, userId: string) => {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .maybeSingle()

  if (error) return { success: false, error }
  if (!data) return { success: false, error: { message: 'Profile not found' } }

  return { success: true, data }
}

// 프로필 생성
export const createProfile = async (supabase, payload) => {
  const { data, error } = await supabase
    .from('profiles')
    .insert({
      id: payload.userId,
      name: payload.name,
      phone: payload.phone,
      role: payload.role || null,
      terms_agreed_at: new Date().toISOString(),
    })
    .select()
    .single()

  if (error) return { success: false, error }
  return { success: true, data }
}

// 프로필 수정 (역할 포함)
export const updateProfile = async (supabase, userId: string, payload) => {
  const { data, error } = await supabase
    .from('profiles')
    .update(payload)
    .eq('id', userId)
    .select()
    .single()

  if (error) return { success: false, error }
  return { success: true, data }
}
```

**Unit Tests**:

| 함수 | 입력 | 예상 출력 |
|------|------|----------|
| `getProfile` | 존재하는 userId | `{ success: true, data: profile }` |
| `getProfile` | 존재하지 않는 userId | `{ success: false, error: ... }` |
| `createProfile` | 유효한 payload | `{ success: true, data: newProfile }` |
| `createProfile` | 중복 userId | `{ success: false, error: ... }` |
| `updateProfile` | 유효한 userId + payload | `{ success: true, data: updatedProfile }` |
| `updateProfile` | 존재하지 않는 userId | `{ success: false, error: ... }` |

---

### 8. Profile Backend Route

**파일**: `src/features/profile/backend/route.ts`

**목적**: 프로필 관련 HTTP API 엔드포인트

**구현 내용**:
```typescript
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { createProfileSchema, updateProfileSchema } from './schema'
import { createProfile, updateProfile, getProfile } from './service'

export const profileRoutes = new Hono()

// GET /api/profile - 현재 사용자 프로필 조회
profileRoutes.get('/api/profile', async (c) => {
  const supabase = c.get('supabase')
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  const result = await getProfile(supabase, user.id)
  return respond(c, result)
})

// POST /api/profile - 프로필 생성
profileRoutes.post('/api/profile', zValidator('json', createProfileSchema), async (c) => {
  const supabase = c.get('supabase')
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  const body = c.req.valid('json')
  const result = await createProfile(supabase, { ...body, userId: user.id })
  return respond(c, result)
})

// PUT /api/profile - 프로필 수정
profileRoutes.put('/api/profile', zValidator('json', updateProfileSchema), async (c) => {
  const supabase = c.get('supabase')
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  const body = c.req.valid('json')
  const result = await updateProfile(supabase, user.id, body)
  return respond(c, result)
})
```

**Unit Tests**:

| 엔드포인트 | 상태 | 예상 응답 |
|-----------|------|----------|
| `GET /api/profile` | 비인증 | 401 Unauthorized |
| `GET /api/profile` | 인증 + 프로필 있음 | 200 + profile data |
| `GET /api/profile` | 인증 + 프로필 없음 | 404 Not Found |
| `POST /api/profile` | 비인증 | 401 Unauthorized |
| `POST /api/profile` | 유효한 body | 201 + created profile |
| `POST /api/profile` | 잘못된 body | 400 Bad Request |
| `PUT /api/profile` | 비인증 | 401 Unauthorized |
| `PUT /api/profile` | 유효한 body | 200 + updated profile |

---

### 9. Profile Schema

**파일**: `src/features/profile/backend/schema.ts`

**목적**: 프로필 요청/응답 스키마 정의

**구현 내용**:
```typescript
import { z } from 'zod'

export const createProfileSchema = z.object({
  name: z.string().min(1),
  phone: z.string().regex(/^[0-9]{10,11}$/),
})

export const updateProfileSchema = z.object({
  name: z.string().min(1).optional(),
  phone: z.string().regex(/^[0-9]{10,11}$/).optional(),
  role: z.enum(['learner', 'instructor', 'operator']).optional(),
})

export const profileResponseSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(['learner', 'instructor', 'operator']).nullable(),
  name: z.string(),
  phone: z.string(),
  terms_agreed_at: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})

export type CreateProfileInput = z.infer<typeof createProfileSchema>
export type UpdateProfileInput = z.infer<typeof updateProfileSchema>
export type ProfileResponse = z.infer<typeof profileResponseSchema>
```

---

### 10. Profile Hooks

**파일**: `src/features/profile/hooks/useProfile.ts`

**목적**: 프로필 조회 React Query 훅

**구현 내용**:
```typescript
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/remote/api-client'
import type { ProfileResponse } from '../lib/dto'

export const useProfile = () => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await apiClient.get('/api/profile')
      return response.data as ProfileResponse
    },
    retry: false,
  })
}
```

**파일**: `src/features/profile/hooks/useCreateProfile.ts`

**목적**: 프로필 생성 React Query 훅

**구현 내용**:
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/remote/api-client'
import type { CreateProfileInput, ProfileResponse } from '../lib/dto'

export const useCreateProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: CreateProfileInput) => {
      const response = await apiClient.post('/api/profile', input)
      return response.data as ProfileResponse
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}
```

**파일**: `src/features/profile/hooks/useUpdateProfile.ts`

**목적**: 프로필 수정 React Query 훅

**구현 내용**:
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/remote/api-client'
import type { UpdateProfileInput, ProfileResponse } from '../lib/dto'

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: UpdateProfileInput) => {
      const response = await apiClient.put('/api/profile', input)
      return response.data as ProfileResponse
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}
```

---

### 11. Profile DTO

**파일**: `src/features/profile/lib/dto.ts`

**목적**: 프런트엔드에서 사용할 타입 재노출

**구현 내용**:
```typescript
export {
  createProfileSchema,
  updateProfileSchema,
  profileResponseSchema,
  type CreateProfileInput,
  type UpdateProfileInput,
  type ProfileResponse,
} from '../backend/schema'
```

---

### 12. Hono App 라우터 등록

**파일**: `src/backend/hono/app.ts`

**목적**: profileRoutes를 Hono 앱에 등록

**구현 내용**:
```typescript
import { profileRoutes } from '@/features/profile/backend/route'

export const createHonoApp = () => {
  const app = new Hono<AppEnv>()

  app.use('*', errorBoundary())
  app.use('*', withAppContext())
  app.use('*', withSupabase())

  // 기존 라우트들...
  app.route('/', profileRoutes)

  return app
}
```

---

## 구현 순서

1. **Profile Backend** (서비스 → 스키마 → 라우트)
   - `src/features/profile/backend/schema.ts`
   - `src/features/profile/backend/service.ts`
   - `src/features/profile/backend/route.ts`
   - `src/backend/hono/app.ts` 수정 (라우터 등록)

2. **Profile Hooks & DTO**
   - `src/features/profile/lib/dto.ts`
   - `src/features/profile/hooks/useProfile.ts`
   - `src/features/profile/hooks/useCreateProfile.ts`
   - `src/features/profile/hooks/useUpdateProfile.ts`

3. **Onboarding Components**
   - `src/features/onboarding/components/OnboardingForm.tsx`
   - `src/features/onboarding/components/RoleSelectForm.tsx`

4. **Onboarding Pages**
   - `src/app/onboarding/page.tsx`
   - `src/app/onboarding/role-select/page.tsx`

5. **Landing Page**
   - `src/features/landing/components/LandingPage.tsx`

6. **Root Page**
   - `src/app/page.tsx` (전면 수정)

---

## 테스트 플로우

### Flow 1: 신규 사용자 회원가입

1. `/` 접근 → 랜딩페이지 표시
2. "시작하기" 클릭 → `/signup` 이동
3. 회원가입 완료 → `/` 리다이렉트
4. 프로필 없음 감지 → `/onboarding` 리다이렉트
5. 이름, 전화번호, 약관동의 입력 → 제출
6. 프로필 생성 완료 → `/onboarding/role-select` 이동
7. Learner 선택 → role 업데이트 → `/courses` 이동

### Flow 2: 기존 사용자 로그인

1. `/` 접근 → 랜딩페이지 표시
2. "로그인" 클릭 → `/login` 이동
3. 로그인 완료 → `/` 리다이렉트
4. 프로필 있음 + 역할 있음 감지
5. Learner → `/courses` 리다이렉트
6. Instructor → `/instructor/dashboard` 리다이렉트

### Flow 3: 인증된 사용자가 루트 접근

1. 로그인 상태에서 `/` 접근
2. 역할에 따라 즉시 리다이렉트
   - Learner → `/courses`
   - Instructor → `/instructor/dashboard`

---

## 의존성 체크

### shadcn-ui 컴포넌트
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add checkbox
npx shadcn@latest add label
```

### 기존 의존성 확인
- `@tanstack/react-query`: ✓ (프로젝트에 이미 설치됨)
- `react-hook-form`: ✓
- `zod`: ✓
- `lucide-react`: ✓
- `hono`: ✓

---

## 주의사항

1. **프로필 테이블 role 필드**: 현재 `NOT NULL` 제약이 있어 역할 선택을 나중에 하려면 마이그레이션 수정 필요
   - Option A: role 필드를 nullable로 변경
   - Option B: 회원가입 시 role을 필수로 받음

2. **인증 쿠키 처리**: Server Component에서 쿠키는 읽기만 가능하므로 `createSupabaseServerClient` 사용 시 주의

3. **HMR 고려**: development 환경에서 Hono 앱 싱글턴 캐싱 해제

4. **타입 안전성**: Supabase 쿼리 결과는 `as unknown as TargetType`로 캐스팅 필요 시 적용
