# 마이페이지 구현 계획

## 문서 개요

**페이지명**: 마이페이지
**라우트**: `/my-page`
**인증 요구**: 필수 (비로그인 시 `/login`으로 리다이렉트)
**작성일**: 2025-10-20

---

## 1. 페이지 개요

### 1.1 페이지 목적
로그인한 사용자가 자신의 계정 정보를 확인하고 닉네임을 수정하며, 로그아웃할 수 있는 페이지입니다.

### 1.2 핵심 기능
1. **사용자 정보 조회**: 이메일과 현재 닉네임 표시
2. **닉네임 수정**: React Hook Form + Zod 검증을 통한 닉네임 변경
3. **로그아웃**: 현재 세션 종료 및 로그인 페이지로 이동

### 1.3 참고 문서
- PRD: 3.2 메인 페이지, 4.2 Journey 6, 6.1 F-003/F-004
- Userflow: 1.3 로그아웃, 1.4 닉네임 수정, 4.1 마이페이지 조회
- UC-003: 로그아웃
- UC-004: 닉네임 수정
- Database: user_profiles 테이블
- Common Modules: 공통 스키마, 에러 코드, UI 컴포넌트

---

## 2. 파일 구조

```
src/
├── app/
│   └── (protected)/
│       └── my-page/
│           └── page.tsx                    # 마이페이지 메인 (Client Component)
│
├── features/
│   ├── users/
│   │   ├── backend/
│   │   │   ├── schema.ts                   # ✅ 이미 구현됨 (UpdateNicknameRequestSchema)
│   │   │   ├── error.ts                    # 🆕 사용자 관련 에러 코드 (신규 생성 필요)
│   │   │   ├── service.ts                  # 🆕 사용자 프로필 조회/수정 서비스
│   │   │   └── route.ts                    # 🆕 사용자 관련 API 라우트
│   │   │
│   │   ├── components/
│   │   │   ├── my-page-header.tsx          # 🆕 마이페이지 헤더 (뒤로가기)
│   │   │   ├── user-info-section.tsx       # 🆕 이메일/닉네임 표시 영역
│   │   │   ├── nickname-form.tsx           # 🆕 닉네임 수정 폼
│   │   │   └── logout-button.tsx           # 🆕 로그아웃 버튼
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-user-profile.ts         # 🆕 사용자 프로필 조회 (React Query)
│   │   │   ├── use-update-nickname.ts      # 🆕 닉네임 수정 mutation
│   │   │   └── use-logout.ts               # 🆕 로그아웃 mutation
│   │   │
│   │   ├── lib/
│   │   │   └── dto.ts                      # 🆕 backend/schema 재노출
│   │   │
│   │   └── types.ts                        # ✅ 이미 구현됨 (UserProfile)
│   │
│   └── auth/
│       ├── backend/
│       │   ├── schema.ts                   # ✅ 이미 구현됨
│       │   ├── error.ts                    # ✅ 이미 구현됨
│       │   ├── service.ts                  # 🆕 로그아웃 서비스 (추가)
│       │   └── route.ts                    # 🆕 로그아웃 라우트 (추가)
│       │
│       └── hooks/
│           └── use-logout.ts               # 🆕 또는 users/hooks에 통합
│
├── components/
│   └── common/
│       ├── error-message.tsx               # ✅ 이미 구현됨
│       └── loading-spinner.tsx             # ✅ 이미 구현됨
│
└── lib/
    ├── query/
    │   └── keys.ts                         # ✅ 이미 구현됨 (queryKeys.users.me 추가 확인)
    │
    └── utils/
        └── ...                             # ✅ 이미 구현됨
```

**범례**:
- ✅ 이미 구현됨 (재사용)
- 🆕 신규 생성 필요

---

## 3. 컴포넌트 계층 구조

```
/my-page (page.tsx)
│
├── MyPageHeader
│   └── ArrowLeft (lucide-react)
│
├── UserInfoSection
│   ├── 이메일 표시 (읽기 전용)
│   └── 닉네임 표시 (읽기 전용, 폼 외부)
│
├── NicknameForm (React Hook Form)
│   ├── Form (shadcn-ui)
│   ├── FormField
│   │   ├── FormLabel
│   │   ├── FormControl
│   │   │   └── Input (닉네임 입력)
│   │   └── FormMessage (에러 메시지)
│   │
│   └── Button (저장)
│       └── LoadingSpinner (조건부)
│
└── LogoutButton
    └── Button (로그아웃)
        └── LoadingSpinner (조건부)
```

---

## 4. 상태 관리

### 4.1 서버 상태 (React Query)

#### 4.1.1 사용자 프로필 조회
```typescript
// src/features/users/hooks/use-user-profile.ts
export const useUserProfile = () => {
  return useQuery({
    queryKey: queryKeys.users.me(),
    queryFn: async () => {
      const response = await apiClient.get('/api/users/me');
      return response.data as UserProfile;
    },
    staleTime: 1000 * 60 * 5, // 5분
  });
};
```

**Query Key**: `['users', 'me']`
**Stale Time**: 5분 (프로필 정보는 자주 변경되지 않음)
**Refetch 조건**: 윈도우 포커스 시 refetch 비활성화

#### 4.1.2 닉네임 수정
```typescript
// src/features/users/hooks/use-update-nickname.ts
export const useUpdateNickname = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UpdateNicknameRequest) => {
      const response = await apiClient.patch('/api/users/me', data);
      return response.data;
    },
    onSuccess: (data) => {
      // 프로필 캐시 무효화 및 업데이트
      queryClient.setQueryData(queryKeys.users.me(), data.data);
      toast.success('닉네임이 변경되었습니다');
    },
    onError: (error: ApiError) => {
      toast.error(error.message || '닉네임 변경에 실패했습니다');
    },
  });
};
```

**낙관적 업데이트 여부**: No (서버 응답 후 캐시 업데이트)
**에러 처리**: Toast 메시지로 피드백
**성공 처리**: React Query 캐시 직접 업데이트 (refetch 불필요)

#### 4.1.3 로그아웃
```typescript
// src/features/users/hooks/use-logout.ts (또는 auth/hooks)
export const useLogout = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/auth/logout');
    },
    onSuccess: () => {
      // 모든 캐시 초기화
      queryClient.clear();
      // 로그인 페이지로 이동
      router.push('/login');
    },
    onError: () => {
      // 에러 발생 시에도 클라이언트 세션 정리
      queryClient.clear();
      router.push('/login');
    },
  });
};
```

**에러 처리**: 실패해도 로그아웃 처리 (클라이언트 세션 정리 우선)
**리다이렉트**: `/login`으로 즉시 이동
**캐시 정리**: `queryClient.clear()` 전체 삭제

### 4.2 로컬 상태 (React Hook Form)

```typescript
// NicknameForm 컴포넌트 내부
const form = useForm<UpdateNicknameFormData>({
  resolver: zodResolver(UpdateNicknameRequestSchema),
  defaultValues: {
    nickname: userProfile?.nickname || '',
  },
});
```

**검증 방식**: Zod schema (2~20자, 특수문자 제외)
**초기값**: 조회한 사용자 프로필의 닉네임
**Dirty 체크**: `form.formState.isDirty`로 변경 여부 확인
**유효성 체크**: `form.formState.isValid`

### 4.3 전역 상태 (Zustand)

**사용 여부**: No
**이유**: 마이페이지는 독립적이며 전역 상태가 필요 없음. React Query만으로 충분.

---

## 5. API 연동

### 5.1 사용자 프로필 조회

**엔드포인트**: `GET /api/users/me`
**인증**: 필수 (requireAuth 미들웨어)
**구현 위치**: `src/features/users/backend/route.ts`

**요청**:
```http
GET /api/users/me HTTP/1.1
Authorization: Bearer {token}
```

**응답 (성공)**:
```json
{
  "id": "user-uuid",
  "nickname": "홍길동",
  "email": "user@example.com"
}
```

**응답 (실패 - 인증 실패)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "인증이 필요합니다"
  }
}
```

### 5.2 닉네임 수정

**엔드포인트**: `PATCH /api/users/me`
**인증**: 필수
**구현 위치**: `src/features/users/backend/route.ts`

**요청**:
```json
{
  "nickname": "새로운닉네임"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "nickname": "새로운닉네임",
    "email": "user@example.com"
  }
}
```

**응답 (실패 - 검증 오류)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "닉네임은 2~20자여야 합니다"
  }
}
```

### 5.3 로그아웃

**엔드포인트**: `POST /api/auth/logout`
**인증**: 필수
**구현 위치**: `src/features/auth/backend/route.ts`

**요청**:
```http
POST /api/auth/logout HTTP/1.1
Authorization: Bearer {token}
```

**응답 (성공)**:
```json
{
  "success": true,
  "message": "로그아웃이 완료되었습니다"
}
```

**응답 (실패)**:
- 실패 시에도 클라이언트 세션 정리 후 로그인 페이지로 이동

---

## 6. UI/UX 상세

### 6.1 레이아웃

```
┌─────────────────────────────────────┐
│ ← 마이페이지                        │  ← Header
├─────────────────────────────────────┤
│                                     │
│  이메일                             │
│  user@example.com                   │  ← 읽기 전용
│                                     │
│  닉네임                             │
│  ┌───────────────────────────────┐ │
│  │ 홍길동                        │ │  ← 입력 필드
│  └───────────────────────────────┘ │
│                                     │
│           [저장]                    │  ← 저장 버튼
│                                     │
│                                     │
│                                     │
│          [로그아웃]                 │  ← 로그아웃 버튼
│                                     │
└─────────────────────────────────────┘
```

### 6.2 인터랙션 플로우

#### 6.2.1 페이지 진입
1. `/my-page` 접근
2. 로딩 인디케이터 표시
3. `GET /api/users/me` 자동 호출
4. 사용자 정보 렌더링

#### 6.2.2 닉네임 수정
1. 닉네임 입력 필드에 새 값 입력
2. 포커스 아웃 시 실시간 검증 (Zod)
3. 유효성 검증 실패 시 입력 필드 아래 에러 메시지 표시
4. 저장 버튼 클릭
5. 버튼에 로딩 스피너 표시, 버튼 비활성화
6. `PATCH /api/users/me` 호출
7. 성공 시:
   - React Query 캐시 업데이트
   - 토스트 메시지 표시: "닉네임이 변경되었습니다"
   - 폼 상태 리셋 (isDirty = false)
8. 실패 시:
   - 토스트 메시지 표시: 에러 메시지
   - 입력값 유지 (재입력 불필요)

#### 6.2.3 로그아웃
1. 로그아웃 버튼 클릭
2. (선택) 확인 다이얼로그 표시
3. 버튼에 로딩 스피너 표시
4. `POST /api/auth/logout` 호출
5. 성공/실패 무관:
   - React Query 캐시 전체 삭제
   - `/login` 페이지로 리다이렉트

### 6.3 스타일링 지침

#### 헤더
- 고정 높이: `h-14`
- 배경: `bg-background`
- 테두리: `border-b`
- 뒤로가기 버튼: `ArrowLeft` 아이콘, 좌측 정렬

#### 사용자 정보 섹션
- 패딩: `p-6`
- 이메일 레이블: `text-sm text-muted-foreground`
- 이메일 값: `text-base text-foreground`

#### 닉네임 폼
- 간격: `space-y-4`
- 입력 필드: shadcn-ui `Input` 컴포넌트
- 에러 상태: 빨간 테두리 (`border-destructive`)
- 에러 메시지: `text-sm text-destructive`

#### 버튼
- 저장 버튼: `variant="default"`, 전체 너비
- 로그아웃 버튼: `variant="outline"`, 전체 너비, 하단 고정

### 6.4 접근성
- 헤더 내비게이션: `<button>` 태그 사용 (키보드 접근 가능)
- 폼 레이블: 명확한 레이블 제공
- 에러 메시지: `aria-describedby`로 입력 필드와 연결
- 로딩 상태: `aria-busy` 속성 설정

---

## 7. 에러 처리

### 7.1 클라이언트 측 에러

#### 7.1.1 닉네임 검증 에러 (Zod)
```typescript
{
  "닉네임은 2~20자여야 합니다": min/max 조건 위반
  "특수문자는 사용할 수 없습니다": regex 조건 위반
  "닉네임을 입력해주세요": 필수 입력 위반
}
```

**표시 위치**: 입력 필드 아래 (`FormMessage`)
**스타일**: 빨간색 텍스트
**해제 조건**: 유효한 값 입력 시 자동 해제

#### 7.1.2 네트워크 에러
```typescript
onError: (error) => {
  if (error.code === 'NETWORK_ERROR') {
    toast.error('네트워크 연결을 확인해주세요');
  }
}
```

**재시도**: React Query 기본 재시도 1회
**사용자 피드백**: Toast 메시지

### 7.2 서버 측 에러

#### 7.2.1 인증 에러 (401)
```typescript
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "인증이 필요합니다"
  }
}
```

**처리 방법**:
1. React Query 캐시 초기화
2. `/login` 페이지로 리다이렉트
3. 세션 만료 안내 메시지 표시

#### 7.2.2 검증 에러 (400)
```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "닉네임은 2~20자여야 합니다"
  }
}
```

**처리 방법**: Toast 메시지로 에러 표시

#### 7.2.3 서버 에러 (500)
```typescript
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "일시적인 오류가 발생했습니다"
  }
}
```

**처리 방법**: Toast 메시지로 에러 표시, 재시도 안내

### 7.3 에러 코드 정의

**파일**: `src/features/users/backend/error.ts` (신규 생성)

```typescript
export const UserErrorCode = {
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  INVALID_NICKNAME: 'INVALID_NICKNAME',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
} as const;

export type UserErrorCode = typeof UserErrorCode[keyof typeof UserErrorCode];

export const userErrorMessages: Record<UserErrorCode, string> = {
  USER_NOT_FOUND: '사용자를 찾을 수 없습니다',
  INVALID_NICKNAME: '유효하지 않은 닉네임입니다',
  VALIDATION_ERROR: '입력값을 확인해주세요',
};
```

---

## 8. 백엔드 구현

### 8.1 사용자 프로필 조회 서비스

**파일**: `src/features/users/backend/service.ts`

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';
import type { UserProfile } from '../types';

export const getUserProfile = async (
  supabase: SupabaseClient,
  userId: string
): Promise<UserProfile | null> => {
  const { data: profile, error } = await supabase
    .from('user_profiles')
    .select('id, nickname')
    .eq('id', userId)
    .single();

  if (error) {
    throw error;
  }

  // 이메일은 Supabase Auth에서 가져옴
  const { data: authUser } = await supabase.auth.getUser();

  return {
    id: profile.id,
    nickname: profile.nickname,
    email: authUser.user?.email || '',
  };
};
```

### 8.2 닉네임 수정 서비스

```typescript
export const updateNickname = async (
  supabase: SupabaseClient,
  userId: string,
  nickname: string
): Promise<UserProfile> => {
  const { data: profile, error } = await supabase
    .from('user_profiles')
    .update({ nickname })
    .eq('id', userId)
    .select('id, nickname')
    .single();

  if (error) {
    throw error;
  }

  const { data: authUser } = await supabase.auth.getUser();

  return {
    id: profile.id,
    nickname: profile.nickname,
    email: authUser.user?.email || '',
  };
};
```

### 8.3 API 라우트

**파일**: `src/features/users/backend/route.ts`

```typescript
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { success, failure } from '@/backend/http/response';
import { UpdateNicknameRequestSchema } from './schema';
import { getUserProfile, updateNickname } from './service';
import { UserErrorCode, userErrorMessages } from './error';

const app = new Hono<AppEnv>();

// GET /api/users/me - 사용자 프로필 조회
app.get('/me', requireAuth(), async (c) => {
  const userId = c.get('userId');
  const supabase = c.get('supabase');

  try {
    const profile = await getUserProfile(supabase, userId);

    if (!profile) {
      return c.json(
        failure(UserErrorCode.USER_NOT_FOUND, userErrorMessages.USER_NOT_FOUND),
        404
      );
    }

    return c.json(profile);
  } catch (error) {
    c.get('logger').error('Get user profile failed', error);
    return c.json(failure('INTERNAL_ERROR', '프로필 조회에 실패했습니다'), 500);
  }
});

// PATCH /api/users/me - 닉네임 수정
app.patch(
  '/me',
  requireAuth(),
  zValidator('json', UpdateNicknameRequestSchema),
  async (c) => {
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const { nickname } = c.req.valid('json');

    try {
      const updatedProfile = await updateNickname(supabase, userId, nickname);
      return c.json(success(updatedProfile));
    } catch (error) {
      c.get('logger').error('Update nickname failed', error);
      return c.json(failure('INTERNAL_ERROR', '닉네임 변경에 실패했습니다'), 500);
    }
  }
);

export default app;
```

### 8.4 라우트 등록

**파일**: `src/backend/hono/app.ts`

```typescript
import userRoutes from '@/features/users/backend/route';

// ...

app.route('/api/users', userRoutes);
```

### 8.5 로그아웃 라우트

**파일**: `src/features/auth/backend/route.ts` (기존 파일에 추가)

```typescript
// POST /api/auth/logout
app.post('/logout', requireAuth(), async (c) => {
  const supabase = c.get('supabase');

  try {
    const { error } = await supabase.auth.signOut();

    if (error) {
      c.get('logger').error('Logout failed', error);
      return c.json(failure('LOGOUT_FAILED', '로그아웃에 실패했습니다'), 500);
    }

    return c.json({ success: true, message: '로그아웃이 완료되었습니다' });
  } catch (error) {
    c.get('logger').error('Logout exception', error);
    return c.json(failure('INTERNAL_ERROR', '서버 오류가 발생했습니다'), 500);
  }
});
```

---

## 9. 구현 순서

### Phase 1: 백엔드 구현
1. ✅ 사용자 에러 코드 정의 (`users/backend/error.ts`)
2. ✅ 사용자 서비스 레이어 (`users/backend/service.ts`)
3. ✅ 사용자 API 라우트 (`users/backend/route.ts`)
4. ✅ 로그아웃 라우트 추가 (`auth/backend/route.ts`)
5. ✅ 라우트 등록 (`backend/hono/app.ts`)
6. ✅ DTO 재노출 (`users/lib/dto.ts`)

### Phase 2: React Query 훅
1. ✅ 사용자 프로필 조회 훅 (`users/hooks/use-user-profile.ts`)
2. ✅ 닉네임 수정 훅 (`users/hooks/use-update-nickname.ts`)
3. ✅ 로그아웃 훅 (`users/hooks/use-logout.ts`)

### Phase 3: UI 컴포넌트
1. ✅ 마이페이지 헤더 (`users/components/my-page-header.tsx`)
2. ✅ 사용자 정보 섹션 (`users/components/user-info-section.tsx`)
3. ✅ 닉네임 폼 (`users/components/nickname-form.tsx`)
4. ✅ 로그아웃 버튼 (`users/components/logout-button.tsx`)

### Phase 4: 페이지 조립
1. ✅ 마이페이지 메인 (`app/(protected)/my-page/page.tsx`)
2. ✅ 로딩/에러 상태 처리
3. ✅ 통합 테스트

### Phase 5: 스타일링 및 최적화
1. ✅ Tailwind 스타일 적용
2. ✅ 반응형 레이아웃 확인
3. ✅ 접근성 검증
4. ✅ 성능 최적화 (불필요한 리렌더 방지)

---

## 10. 테스트 시나리오

### 10.1 단위 테스트

#### 10.1.1 서비스 레이어
- ✅ `getUserProfile`: 정상적인 프로필 반환
- ✅ `getUserProfile`: 존재하지 않는 사용자 (null 반환)
- ✅ `updateNickname`: 닉네임 정상 업데이트
- ✅ `updateNickname`: DB 에러 발생 시 예외 발생

#### 10.1.2 React Hook
- ✅ `useUserProfile`: 데이터 로딩 및 성공
- ✅ `useUpdateNickname`: mutation 성공 시 캐시 업데이트
- ✅ `useLogout`: 성공/실패 무관 캐시 초기화 및 리다이렉트

### 10.2 통합 테스트

#### 10.2.1 API 엔드포인트
- ✅ `GET /api/users/me`: 인증된 사용자 프로필 조회
- ✅ `GET /api/users/me`: 비인증 사용자 401 응답
- ✅ `PATCH /api/users/me`: 닉네임 정상 업데이트
- ✅ `PATCH /api/users/me`: 유효성 검증 실패 (400)
- ✅ `POST /api/auth/logout`: 로그아웃 성공

### 10.3 E2E 테스트 (선택 사항)

- ✅ 마이페이지 접근 → 사용자 정보 표시
- ✅ 닉네임 수정 → 성공 메시지 표시 → 새 닉네임 반영
- ✅ 유효하지 않은 닉네임 입력 → 에러 메시지 표시
- ✅ 로그아웃 → 로그인 페이지로 리다이렉트

---

## 11. 예상 문제 및 해결 방안

### 11.1 문제: 닉네임 변경 후 다른 페이지에서 즉시 반영 안 됨

**원인**: React Query 캐시가 독립적으로 관리됨

**해결**:
- 닉네임 수정 성공 시 `queryKeys.users.me()` 캐시 무효화
- 다른 페이지에서도 동일한 Query Key 사용

### 11.2 문제: 로그아웃 실패 시 사용자가 로그인 상태로 남음

**원인**: 네트워크 에러 또는 서버 에러

**해결**:
- `onError` 핸들러에서도 클라이언트 세션 정리 (`queryClient.clear()`)
- 실패해도 로그인 페이지로 리다이렉트

### 11.3 문제: 이메일 정보가 user_profiles 테이블에 없음

**원인**: 이메일은 Supabase Auth에서 관리

**해결**:
- 서비스 레이어에서 `supabase.auth.getUser()` 호출하여 이메일 가져옴
- 프로필 조회 시 Auth 정보와 병합

### 11.4 문제: 폼 제출 중 중복 요청 방지

**원인**: 사용자가 저장 버튼을 여러 번 클릭

**해결**:
- React Query mutation의 `isLoading` 상태로 버튼 비활성화
- 버튼에 로딩 스피너 표시

---

## 12. 성능 최적화

### 12.1 React Query 캐시 전략
- `staleTime: 5분`: 프로필 정보는 자주 변경되지 않으므로 긴 stale time 설정
- `refetchOnWindowFocus: false`: 윈도우 포커스 시 불필요한 refetch 방지

### 12.2 불필요한 리렌더 방지
- `React.memo` 사용: 자식 컴포넌트 최적화
- `useCallback`: 이벤트 핸들러 메모이제이션

### 12.3 번들 크기 최적화
- `lucide-react`: 아이콘 트리쉐이킹 (필요한 아이콘만 import)
- shadcn-ui 컴포넌트: 이미 최적화됨

---

## 13. 보안 고려사항

### 13.1 인증 검증
- 모든 API 엔드포인트에 `requireAuth()` 미들웨어 적용
- 클라이언트 측 라우트 보호: `(protected)` 레이아웃 사용

### 13.2 입력 검증
- 클라이언트: Zod 스키마로 검증
- 서버: 동일한 Zod 스키마로 재검증 (우회 방지)

### 13.3 XSS 방지
- 사용자 입력 HTML 이스케이프 (React 기본 제공)
- 서버 측 sanitization 추가 (필요 시)

### 13.4 CSRF 방지
- Supabase Auth 토큰 사용 (자동 처리)

---

## 14. 접근성 (a11y)

### 14.1 키보드 내비게이션
- 모든 인터랙티브 요소에 키보드 접근 가능
- Tab 순서: 뒤로가기 → 닉네임 입력 → 저장 버튼 → 로그아웃 버튼

### 14.2 스크린 리더 지원
- 폼 레이블: 명확한 `<label>` 제공
- 에러 메시지: `aria-describedby`로 입력 필드와 연결
- 로딩 상태: `aria-busy` 속성 설정

### 14.3 포커스 관리
- 에러 발생 시 첫 번째 에러 필드로 포커스 이동
- 폼 제출 후 성공 메시지에 포커스 (선택 사항)

---

## 15. 참고 사항

### 15.1 기존 코드 재사용
- ✅ `src/features/users/backend/schema.ts`: `UpdateNicknameRequestSchema`
- ✅ `src/features/users/types.ts`: `UserProfile`
- ✅ `src/features/auth/backend/schema.ts`: 로그인/회원가입 스키마
- ✅ `src/components/common/error-message.tsx`
- ✅ `src/components/common/loading-spinner.tsx`
- ✅ `src/lib/query/keys.ts`: `queryKeys.users.me()`

### 15.2 신규 생성 필요
- 🆕 `src/features/users/backend/error.ts`
- 🆕 `src/features/users/backend/service.ts`
- 🆕 `src/features/users/backend/route.ts`
- 🆕 `src/features/users/hooks/use-user-profile.ts`
- 🆕 `src/features/users/hooks/use-update-nickname.ts`
- 🆕 `src/features/users/hooks/use-logout.ts`
- 🆕 `src/features/users/components/*.tsx` (4개 컴포넌트)
- 🆕 `src/app/(protected)/my-page/page.tsx`
- 🆕 로그아웃 라우트 추가 (`auth/backend/route.ts`)

### 15.3 수정 필요
- 📝 `src/backend/hono/app.ts`: 사용자 라우트 등록
- 📝 `src/lib/query/keys.ts`: `queryKeys.users.me()` 추가 (이미 있는지 확인)

---

## 16. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0  | 2025-10-20 | Claude Code | 초기 작성 |

---

**문서 종료**
