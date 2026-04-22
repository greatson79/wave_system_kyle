# 로그인 페이지 구현 계획 (`/login`)

## 문서 개요

이 문서는 로그인 페이지(`/login`)의 상세한 구현 계획을 정의합니다. PRD, Userflow, Database 설계, 그리고 유스케이스 문서(UC-002)에 명시된 내용을 기반으로 작성되었습니다.

**페이지 경로**: `/login`
**기능 ID**: F-002 (로그인)
**유스케이스**: UC-002 (사용자 로그인)

---

## 1. 페이지 개요

### 1.1 목적

등록된 사용자가 이메일과 비밀번호를 입력하여 채팅 서비스에 로그인하고, 인증된 상태로 서비스를 이용할 수 있도록 한다.

### 1.2 주요 기능

1. **이메일 + 비밀번호 입력 폼**
   - React Hook Form + Zod 검증
   - 클라이언트 측 기본 검증 (비어있지 않은지)

2. **Supabase Auth 연동**
   - `supabase.auth.signInWithPassword()` 사용
   - 세션 토큰 자동 관리

3. **로그인 성공 시 리다이렉트**
   - 기본: 홈 페이지(`/`)로 이동
   - `redirectedFrom` 파라미터가 있는 경우: 해당 경로로 이동

4. **회원가입 페이지로 이동 링크**
   - `/signup` 페이지로 이동

5. **에러 처리**
   - 클라이언트 검증 에러: 즉시 표시
   - 서버 에러: API 응답 후 표시
   - 네트워크 에러 처리

### 1.3 제외 사항

- 소셜 로그인 (향후 확장)
- 자동 로그인 (Remember Me)
- 비밀번호 재설정
- 이중 인증 (2FA)

---

## 2. 파일 구조

### 2.1 프론트엔드

```
src/
├── app/
│   └── login/
│       └── page.tsx                    # 로그인 페이지 (기존 파일, 개선 필요)
│
├── features/
│   └── auth/
│       ├── backend/
│       │   ├── schema.ts               # ✅ 이미 구현됨 (LoginRequestSchema, LoginResponseSchema)
│       │   ├── error.ts                # ✅ 이미 구현됨 (AuthErrorCode, authErrorMessages)
│       │   ├── route.ts                # 🆕 신규 생성 필요 (Hono 라우터)
│       │   └── service.ts              # 🆕 신규 생성 필요 (로그인 비즈니스 로직)
│       │
│       ├── components/
│       │   ├── login-form.tsx          # 🆕 신규 생성 (로그인 폼 컴포넌트)
│       │   └── login-error.tsx         # 🆕 신규 생성 (에러 메시지 컴포넌트)
│       │
│       ├── hooks/
│       │   ├── useLogin.ts             # 🆕 신규 생성 (로그인 React Query 훅)
│       │   └── useCurrentUser.ts       # ✅ 이미 구현됨 (현재 사용자 정보 조회)
│       │
│       └── lib/
│           └── dto.ts                  # 🆕 신규 생성 (schema 재노출)
│
└── lib/
    ├── query/
    │   └── keys.ts                     # ✅ 이미 구현됨 (Query Key Factory)
    │
    └── remote/
        └── api-client.ts               # ✅ 이미 구현됨 (HTTP 클라이언트)
```

### 2.2 백엔드

```
src/
├── backend/
│   ├── hono/
│   │   └── app.ts                      # ✅ 기존 파일 (registerAuthRoutes 추가 필요)
│   │
│   └── middleware/
│       └── auth.ts                     # ✅ 이미 구현됨 (requireAuth 미들웨어)
│
└── features/
    └── auth/
        └── backend/
            ├── route.ts                # 🆕 POST /api/auth/login 라우터
            └── service.ts              # 🆕 로그인 비즈니스 로직
```

**범례**:
- ✅ 이미 구현됨
- 🆕 신규 생성 필요
- 📝 개선 필요

---

## 3. 컴포넌트 계층 구조

```
LoginPage (src/app/login/page.tsx)
│
├── useCurrentUser()                     # 인증 상태 확인
│   └── 로그인된 경우 → 자동 리다이렉트
│
├── LoginForm (src/features/auth/components/login-form.tsx)
│   ├── useForm (React Hook Form)
│   │   └── zodResolver(LoginFormSchema)
│   │
│   ├── useLogin()                       # React Query 훅
│   │   └── apiClient.post('/api/auth/login', data)
│   │
│   ├── 이메일 입력 필드
│   │   └── Input (shadcn-ui)
│   │
│   ├── 비밀번호 입력 필드
│   │   └── Input (shadcn-ui)
│   │
│   ├── LoginError                       # 에러 메시지 표시
│   │   └── Alert (shadcn-ui)
│   │
│   ├── 로그인 버튼
│   │   └── Button (shadcn-ui)
│   │
│   └── 회원가입 링크
│       └── Link (Next.js)
│
└── 플레이스홀더 이미지 (선택 사항)
    └── Image (Next.js)
```

---

## 4. 상태 관리

### 4.1 폼 상태 (React Hook Form)

```typescript
type LoginFormValues = {
  email: string;
  password: string;
};

const form = useForm<LoginFormValues>({
  resolver: zodResolver(LoginFormSchema),
  defaultValues: {
    email: '',
    password: '',
  },
});
```

### 4.2 로딩 상태 (React Query)

```typescript
const { mutate: login, isPending, error } = useLogin();
```

### 4.3 인증 상태 (useCurrentUser)

```typescript
const { isAuthenticated, refresh } = useCurrentUser();
```

### 4.4 에러 상태

- **클라이언트 검증 에러**: React Hook Form의 `formState.errors`
- **서버 에러**: React Query의 `error` 객체
- **네트워크 에러**: React Query의 `error` 객체

---

## 5. API 연동

### 5.1 Hono 라우트 (`POST /api/auth/login`)

**파일**: `src/features/auth/backend/route.ts`

**요청**:
```typescript
// POST /api/auth/login
{
  email: string,      // 이메일
  password: string    // 비밀번호
}
```

**응답 (성공 200)**:
```typescript
{
  success: true,
  user: {
    id: string,
    email: string,
    nickname: string
  },
  redirectTo: string  // '/' 또는 redirectedFrom 파라미터 값
}
```

**응답 (실패 401)**:
```typescript
{
  error: {
    code: 'AUTH_INVALID_CREDENTIALS',
    message: '이메일 또는 비밀번호가 올바르지 않습니다.'
  }
}
```

**응답 (실패 500)**:
```typescript
{
  error: {
    code: 'INTERNAL_SERVER_ERROR',
    message: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
  }
}
```

### 5.2 백엔드 비즈니스 로직

**파일**: `src/features/auth/backend/service.ts`

**주요 로직**:
1. Supabase Auth `signInWithPassword` 호출
2. 인증 성공 시 `user_profiles` 테이블에서 닉네임 조회
3. 응답 데이터 구성
4. 에러 발생 시 에러 코드 반환

**의사 코드**:
```typescript
export async function login(
  supabase: SupabaseClient,
  email: string,
  password: string,
  redirectedFrom?: string
): Promise<LoginResponse | ErrorResponse> {
  // 1. Supabase Auth 로그인
  const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (authError || !authData.user) {
    return {
      error: {
        code: 'AUTH_INVALID_CREDENTIALS',
        message: authErrorMessages.AUTH_INVALID_CREDENTIALS,
      }
    };
  }

  // 2. 사용자 프로필 조회
  const { data: profile, error: profileError } = await supabase
    .from('user_profiles')
    .select('nickname')
    .eq('id', authData.user.id)
    .single();

  if (profileError || !profile) {
    return {
      error: {
        code: 'INTERNAL_SERVER_ERROR',
        message: '사용자 정보를 불러올 수 없습니다.',
      }
    };
  }

  // 3. 응답 반환
  return {
    success: true,
    user: {
      id: authData.user.id,
      email: authData.user.email!,
      nickname: profile.nickname,
    },
    redirectTo: redirectedFrom || '/',
  };
}
```

### 5.3 React Query 훅

**파일**: `src/features/auth/hooks/useLogin.ts`

```typescript
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/remote/api-client';
import type { LoginRequest, LoginResponse } from '@/features/auth/lib/dto';

export function useLogin() {
  const router = useRouter();

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await apiClient.post<LoginResponse>(
        '/api/auth/login',
        data
      );
      return response.data;
    },
    onSuccess: (data) => {
      // 로그인 성공 시 리다이렉트
      router.replace(data.redirectTo);
    },
    onError: (error) => {
      console.error('Login failed:', error);
    },
  });
}
```

---

## 6. UI/UX 상세

### 6.1 레이아웃

**데스크톱 (PC)**:
```
┌─────────────────────────────────────────────────┐
│                   로그인 페이지                  │
│                                                  │
│  ┌──────────────────────┐  ┌─────────────────┐ │
│  │   로그인 폼          │  │   이미지        │ │
│  │                      │  │                 │ │
│  │  이메일: [        ] │  │   [Placeholder] │ │
│  │  비밀번호: [      ] │  │                 │ │
│  │                      │  │                 │ │
│  │  [에러 메시지]       │  │                 │ │
│  │                      │  │                 │ │
│  │  [ 로그인 ]          │  │                 │ │
│  │                      │  │                 │ │
│  │  계정이 없으신가요?   │  └─────────────────┘ │
│  │  회원가입            │                      │
│  └──────────────────────┘                      │
└─────────────────────────────────────────────────┘
```

**모바일**:
```
┌─────────────────┐
│   로그인 페이지 │
│                  │
│  이메일: [    ] │
│  비밀번호: [  ] │
│                  │
│  [에러 메시지]   │
│                  │
│  [ 로그인 ]      │
│                  │
│  계정이 없으신가요?│
│  회원가입        │
│                  │
│  [이미지 생략]   │
└─────────────────┘
```

### 6.2 스타일 가이드

**색상**:
- 배경: `bg-background` (white)
- 입력 필드: `border-input`, `focus:border-primary`
- 버튼: `bg-primary text-primary-foreground hover:bg-primary/90`
- 에러: `text-destructive`

**간격**:
- 폼 내부 요소 간격: `gap-4`
- 페이지 패딩: `px-6 py-16`
- 최대 너비: `max-w-4xl`

**반응형**:
- 데스크톱 (768px 이상): 2열 그리드 (`md:grid-cols-2`)
- 모바일: 1열 (`flex-col`)

### 6.3 접근성

- **키보드 탐색**: Tab 키로 모든 요소 접근 가능
- **Enter 키**: 폼 제출
- **ARIA 레이블**: `aria-label`, `aria-describedby` 적용
- **에러 메시지**: 스크린 리더에서 읽을 수 있도록 `role="alert"`

---

## 7. 에러 처리

### 7.1 클라이언트 검증 에러

**발생 시점**: 폼 제출 시 Zod 검증 실패

**에러 메시지**:
- 이메일 비어있음: "이메일을 입력해주세요."
- 비밀번호 비어있음: "비밀번호를 입력해주세요."

**표시 위치**: 해당 입력 필드 아래

**처리 방법**:
```typescript
{formState.errors.email && (
  <p className="text-sm text-destructive">
    {formState.errors.email.message}
  </p>
)}
```

### 7.2 서버 에러

**에러 코드별 메시지**:

| 에러 코드 | HTTP 상태 | 메시지 |
|----------|----------|--------|
| `AUTH_INVALID_CREDENTIALS` | 401 | "이메일 또는 비밀번호가 올바르지 않습니다." |
| `INTERNAL_SERVER_ERROR` | 500 | "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요." |

**표시 위치**: 폼 상단 또는 버튼 위

**처리 방법**:
```typescript
{error && (
  <Alert variant="destructive">
    <AlertDescription>
      {error.message || '로그인에 실패했습니다.'}
    </AlertDescription>
  </Alert>
)}
```

### 7.3 네트워크 에러

**발생 시점**: API 요청 실패 (네트워크 연결 끊김)

**메시지**: "네트워크 연결을 확인해주세요."

**처리 방법**:
```typescript
if (error?.message?.includes('Network')) {
  return '네트워크 연결을 확인해주세요.';
}
```

### 7.4 에러 발생 시 UI 상태

- 비밀번호 필드 초기화 (보안)
- 이메일 필드에 포커스
- 로딩 상태 해제
- 버튼 활성화

---

## 8. 구현 순서

### Phase 1: 백엔드 구현

#### Step 1: 서비스 로직 구현
**파일**: `src/features/auth/backend/service.ts`

**작업**:
1. `login` 함수 구현
   - Supabase Auth `signInWithPassword` 호출
   - 사용자 프로필 조회 (`user_profiles` 테이블)
   - 에러 처리 및 응답 생성

**의존성**:
- Supabase Client
- 기존 스키마 (`LoginRequestSchema`, `LoginResponseSchema`)
- 기존 에러 코드 (`AuthErrorCode`, `authErrorMessages`)

**검증**:
- 올바른 이메일/비밀번호 입력 시 세션 생성
- 잘못된 이메일/비밀번호 입력 시 에러 반환
- 사용자 프로필 조회 실패 시 에러 반환

#### Step 2: Hono 라우터 구현
**파일**: `src/features/auth/backend/route.ts`

**작업**:
1. `POST /api/auth/login` 라우터 정의
2. 요청 검증 (`LoginRequestSchema`)
3. 서비스 로직 호출
4. 응답 반환 (`respond` 헬퍼 사용)

**코드 예시**:
```typescript
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { respond } from '@/backend/http/response';
import { LoginRequestSchema } from './schema';
import { login } from './service';

export const authRoutes = new Hono<AppEnv>();

authRoutes.post(
  '/api/auth/login',
  zValidator('json', LoginRequestSchema),
  async (c) => {
    const { email, password } = c.req.valid('json');
    const supabase = c.get('supabase');
    const redirectedFrom = c.req.query('redirectedFrom');

    const result = await login(supabase, email, password, redirectedFrom);
    return respond(c, result);
  }
);
```

**검증**:
- 요청 스키마 검증
- 서비스 로직 호출
- 올바른 HTTP 상태 코드 반환

#### Step 3: Hono 앱에 라우터 등록
**파일**: `src/backend/hono/app.ts`

**작업**:
1. `authRoutes` import
2. `app.route('/', authRoutes)` 추가

**검증**:
- `POST /api/auth/login` 엔드포인트 접근 가능
- 요청/응답 정상 작동

---

### Phase 2: 프론트엔드 구현

#### Step 4: DTO 재노출
**파일**: `src/features/auth/lib/dto.ts`

**작업**:
```typescript
export type {
  LoginRequest,
  LoginResponse,
} from '../backend/schema';

export {
  LoginRequestSchema,
  LoginResponseSchema,
} from '../backend/schema';
```

#### Step 5: React Query 훅 구현
**파일**: `src/features/auth/hooks/useLogin.ts`

**작업**:
1. `useMutation` 훅 정의
2. API 호출 (`apiClient.post`)
3. 성공 시 리다이렉트 처리
4. 에러 처리

**검증**:
- 로그인 API 호출 성공
- 성공 시 홈 또는 `redirectedFrom` 페이지로 이동
- 에러 시 에러 객체 반환

#### Step 6: 로그인 폼 컴포넌트 구현
**파일**: `src/features/auth/components/login-form.tsx`

**작업**:
1. React Hook Form + Zod 검증 설정
2. `useLogin` 훅 사용
3. 입력 필드 렌더링 (shadcn-ui Input)
4. 에러 메시지 표시
5. 로그인 버튼 (로딩 상태 표시)
6. 회원가입 링크

**검증**:
- 폼 검증 작동 (빈 값 입력 시 에러)
- 로그인 버튼 클릭 시 API 호출
- 로딩 상태 UI 표시
- 에러 메시지 표시

#### Step 7: 로그인 페이지 개선
**파일**: `src/app/login/page.tsx`

**작업**:
1. 기존 코드 제거 (현재는 Supabase 클라이언트 직접 호출)
2. `LoginForm` 컴포넌트 사용
3. 인증 상태 확인 (`useCurrentUser`)
4. 로그인된 경우 자동 리다이렉트

**검증**:
- 로그인된 사용자 접근 시 홈으로 리다이렉트
- 비로그인 사용자 접근 시 로그인 폼 표시

---

### Phase 3: 테스트 및 검증

#### Step 8: 수동 테스트

**테스트 케이스**:
1. 올바른 이메일/비밀번호 입력 → 로그인 성공, 홈으로 이동
2. 잘못된 이메일/비밀번호 입력 → 에러 메시지 표시
3. 빈 이메일 입력 → 클라이언트 검증 에러
4. 빈 비밀번호 입력 → 클라이언트 검증 에러
5. `redirectedFrom` 파라미터 포함 → 해당 경로로 이동
6. 로그인된 상태에서 로그인 페이지 접근 → 자동 리다이렉트
7. 네트워크 연결 끊김 → 네트워크 에러 메시지

#### Step 9: UI/UX 검증

**체크리스트**:
- [ ] 반응형 레이아웃 (모바일/데스크톱)
- [ ] 키보드 탐색 (Tab, Enter)
- [ ] 접근성 (ARIA 레이블, 스크린 리더)
- [ ] 로딩 상태 표시
- [ ] 에러 메시지 표시
- [ ] 회원가입 링크 작동

---

## 9. 기존 코드와의 충돌 방지

### 9.1 이미 구현된 파일

**사용 가능한 파일**:
- ✅ `src/features/auth/backend/schema.ts`: LoginRequestSchema, LoginResponseSchema
- ✅ `src/features/auth/backend/error.ts`: AuthErrorCode, authErrorMessages
- ✅ `src/backend/middleware/auth.ts`: requireAuth 미들웨어 (이 페이지에서는 미사용)
- ✅ `src/lib/query/keys.ts`: Query Key Factory
- ✅ `src/lib/remote/api-client.ts`: HTTP 클라이언트

**수정 필요한 파일**:
- 📝 `src/app/login/page.tsx`: 기존 로직 제거, 새 컴포넌트 사용
- 📝 `src/backend/hono/app.ts`: authRoutes 등록

### 9.2 신규 생성 파일

**충돌 없는 파일**:
- 🆕 `src/features/auth/backend/route.ts`
- 🆕 `src/features/auth/backend/service.ts`
- 🆕 `src/features/auth/components/login-form.tsx`
- 🆕 `src/features/auth/components/login-error.tsx` (선택 사항)
- 🆕 `src/features/auth/hooks/useLogin.ts`
- 🆕 `src/features/auth/lib/dto.ts`

### 9.3 코드 중복 방지

**중복 가능성**:
- Supabase Auth 호출 로직 (기존 `page.tsx`와 새 서비스 로직)
- 에러 메시지 정의 (기존 `error.ts` 사용)

**해결 방법**:
- 기존 `error.ts`의 에러 코드 재사용
- 기존 `schema.ts`의 스키마 재사용
- 새 서비스 로직에서 중앙화된 로직 구현

---

## 10. 의존성

### 10.1 필수 의존성

**이미 설치된 라이브러리**:
- Next.js 15
- React 19
- React Hook Form
- Zod
- @tanstack/react-query
- Hono
- Supabase
- shadcn-ui

**추가 설치 필요** (있는 경우):
```bash
# shadcn-ui 컴포넌트 (필요 시)
npx shadcn@latest add input
npx shadcn@latest add button
npx shadcn@latest add alert
npx shadcn@latest add label
```

### 10.2 환경 변수

**필요한 환경 변수**:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (백엔드 전용)

---

## 11. 성능 최적화

### 11.1 코드 분할

- 로그인 페이지는 별도 청크로 분리 (Next.js 자동 처리)
- 이미지는 레이지 로딩 (`priority={false}`)

### 11.2 캐싱

- React Query 캐싱 (기본 설정 사용)
- 로그인 성공 시 사용자 정보 캐시

### 11.3 로딩 최적화

- Suspense 경계 설정 (선택 사항)
- 로딩 스피너 표시

---

## 12. 보안 고려사항

### 12.1 입력 검증

- **클라이언트 측**: Zod 스키마 검증
- **서버 측**: Zod 스키마 검증 (중복 검증)

### 12.2 에러 메시지

- 이메일 존재 여부 노출 금지 (동일한 에러 메시지 사용)
- 상세 에러 정보 노출 금지 (일반 에러 메시지)

### 12.3 세션 관리

- Supabase Auth 자동 세션 관리
- HttpOnly 쿠키 사용 (XSS 방지)

### 12.4 HTTPS

- 프로덕션 환경에서 HTTPS 강제 (Next.js 설정)

---

## 13. 테스트 계획

### 13.1 단위 테스트 (선택 사항)

- `login` 서비스 로직 테스트
- `useLogin` 훅 테스트
- 폼 검증 테스트

### 13.2 통합 테스트

- API 엔드포인트 테스트 (Postman/curl)
- 로그인 플로우 E2E 테스트

### 13.3 수동 테스트

- 브라우저에서 실제 로그인 시도
- 다양한 에러 케이스 테스트

---

## 14. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0  | 2025-10-20 | Claude Code | 초기 작성 |

---

## 15. 참고 자료

- **PRD**: `/docs/prd.md` (섹션 3.1, 4.1, 6.1)
- **Userflow**: `/docs/userflow.md` (섹션 1.2)
- **Database**: `/docs/database.md`
- **유스케이스**: `/docs/usecases/2-login/spec.md` (UC-002)
- **공통 모듈**: `/docs/common-modules.md`

---

**문서 종료**
