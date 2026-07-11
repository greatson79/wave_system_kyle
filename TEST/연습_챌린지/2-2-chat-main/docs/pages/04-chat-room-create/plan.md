# 채팅방 추가 페이지 - 구현 계획

## 문서 개요

본 문서는 채팅방 추가 페이지(`/chat-rooms/new`)의 상세한 구현 계획을 정의합니다. PRD, Userflow, Database 설계 문서 및 UC-006 유스케이스 문서를 기반으로 작성되었습니다.

---

## 1. 페이지 개요

### 1.1 페이지 정보

- **경로**: `/chat-rooms/new`
- **목적**: 새로운 채팅방 생성
- **접근 권한**: 로그인 필수 (인증된 사용자만 접근 가능)
- **라우트 보호**: `(protected)` 레이아웃 그룹 사용

### 1.2 주요 기능

1. 채팅방 이름 입력 폼 (1~50자)
2. 실시간 유효성 검증 (React Hook Form + Zod)
3. 생성 완료 시 홈(`/`)으로 리다이렉트
4. 취소 버튼으로 홈 이동

### 1.3 관련 유스케이스

- **UC-006**: 채팅방 생성

### 1.4 관련 문서

- PRD: 섹션 3.2 (Journey 2), 6.2 (F-006)
- Userflow: 섹션 2.2 (채팅방 생성)
- Database: 섹션 3.2 (chat_rooms 테이블)
- Common Modules: 섹션 2.4 (채팅방 스키마)

---

## 2. 파일 구조

```
src/
├── app/
│   └── (protected)/
│       └── chat-rooms/
│           └── new/
│               └── page.tsx                 # 채팅방 생성 페이지
│
├── features/
│   └── chat-rooms/
│       ├── types.ts                         # ✅ 기존 파일 (ChatRoom 타입)
│       ├── backend/
│       │   ├── schema.ts                    # ✅ 기존 파일 (스키마 정의)
│       │   ├── error.ts                     # 🆕 신규 파일 (에러 코드 정의)
│       │   ├── service.ts                   # 🆕 신규 파일 (비즈니스 로직)
│       │   └── route.ts                     # 🆕 신규 파일 (Hono 라우터)
│       ├── components/
│       │   └── create-chat-room-form.tsx    # 🆕 신규 파일 (폼 컴포넌트)
│       ├── hooks/
│       │   └── useCreateChatRoom.ts         # 🆕 신규 파일 (React Query Mutation)
│       └── lib/
│           └── dto.ts                       # 🆕 신규 파일 (스키마 재노출)
│
└── backend/
    └── hono/
        └── app.ts                           # ✏️ 수정 필요 (라우터 등록)
```

### 파일별 작업 종류

- ✅ **기존 파일**: 이미 구현됨 (`types.ts`, `backend/schema.ts`)
- 🆕 **신규 파일**: 새로 생성 필요
- ✏️ **수정 파일**: 기존 파일에 코드 추가 필요

---

## 3. 컴포넌트 계층 구조

```
/chat-rooms/new (page.tsx)
└── CreateChatRoomPage
    └── CreateChatRoomForm
        ├── FormHeader
        │   └── 페이지 제목
        ├── FormBody
        │   ├── Input (채팅방 이름)
        │   ├── CharacterCounter (N/50자)
        │   └── ErrorMessage (유효성 검증 에러)
        └── FormFooter
            ├── CancelButton (취소)
            └── SubmitButton (생성)
```

### 컴포넌트 책임

| 컴포넌트 | 책임 |
|---------|------|
| `CreateChatRoomPage` | 페이지 레이아웃, React Query Provider 제공 |
| `CreateChatRoomForm` | 폼 상태 관리 (React Hook Form), API 호출, 리다이렉션 |
| `FormHeader` | 페이지 제목 표시 |
| `FormBody` | 입력 필드, 글자 수 카운터, 에러 메시지 |
| `FormFooter` | 취소/생성 버튼, 로딩 상태 표시 |

---

## 4. 상태 관리

### 4.1 폼 상태 (React Hook Form)

```typescript
type CreateChatRoomFormData = {
  name: string; // 채팅방 이름 (1~50자)
};

const form = useForm<CreateChatRoomFormData>({
  resolver: zodResolver(CreateChatRoomRequestSchema),
  defaultValues: {
    name: '',
  },
  mode: 'onChange', // 실시간 검증
});
```

**검증 규칙**:
- `name`: 1~50자 문자열
- 빈 문자열 불가
- 공백만으로 구성된 이름 허용하지 않음 (trim 후 검증)

### 4.2 서버 상태 (React Query Mutation)

```typescript
// src/features/chat-rooms/hooks/useCreateChatRoom.ts

export const useCreateChatRoom = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: CreateChatRoomRequest) =>
      apiClient.post('/api/chat-rooms', data),

    onSuccess: (response) => {
      // 채팅방 목록 캐시 무효화
      queryClient.invalidateQueries({
        queryKey: queryKeys.chatRooms.all(),
      });

      // 홈으로 리다이렉트
      router.push(response.redirectTo);
    },

    onError: (error) => {
      // 에러 처리는 컴포넌트에서 수행
      console.error('채팅방 생성 실패:', error);
    },
  });
};
```

### 4.3 관리할 상태

| 상태 | 관리 방법 | 설명 |
|------|-----------|------|
| `name` | React Hook Form | 채팅방 이름 입력값 |
| `errors` | React Hook Form | 유효성 검증 에러 |
| `isValid` | React Hook Form | 폼 유효성 여부 |
| `isDirty` | React Hook Form | 입력 변경 여부 |
| `isPending` | React Query | API 요청 진행 중 여부 |
| `error` | React Query | API 요청 실패 에러 |

---

## 5. API 연동

### 5.1 백엔드 라우터 (Hono)

**파일**: `src/features/chat-rooms/backend/route.ts`

```typescript
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { respond, success, failure } from '@/backend/http/response';
import { CreateChatRoomRequestSchema } from './schema';
import { createChatRoom } from './service';
import { ChatRoomErrorCode, chatRoomErrorMessages } from './error';

export const chatRoomRoutes = new Hono<AppEnv>();

// 채팅방 생성
chatRoomRoutes.post(
  '/api/chat-rooms',
  requireAuth(),
  zValidator('json', CreateChatRoomRequestSchema),
  async (c) => {
    const data = c.req.valid('json');
    const userId = c.get('userId');
    const supabase = c.get('supabase');
    const logger = c.get('logger');

    try {
      const chatRoom = await createChatRoom(supabase, {
        name: data.name,
        userId,
      });

      logger.info('채팅방 생성 성공', { chatRoomId: chatRoom.id });

      return c.json(
        success({
          success: true,
          data: {
            id: chatRoom.id,
            name: chatRoom.name,
            created_at: chatRoom.created_at,
          },
          redirectTo: '/',
        }),
        200
      );
    } catch (error) {
      logger.error('채팅방 생성 실패', { error });
      return respond(
        c,
        failure(ChatRoomErrorCode.CREATE_FAILED, 500)
      );
    }
  }
);
```

### 5.2 백엔드 서비스 레이어

**파일**: `src/features/chat-rooms/backend/service.ts`

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';
import type { ChatRoom } from '../types';

export type CreateChatRoomParams = {
  name: string;
  userId: string;
};

export async function createChatRoom(
  supabase: SupabaseClient,
  params: CreateChatRoomParams
): Promise<ChatRoom> {
  const { data, error } = await supabase
    .from('chat_rooms')
    .insert({
      name: params.name.trim(),
    })
    .select('id, name, created_at')
    .single();

  if (error || !data) {
    throw new Error('채팅방 생성 실패: ' + error?.message);
  }

  return data;
}
```

### 5.3 에러 코드 정의

**파일**: `src/features/chat-rooms/backend/error.ts`

```typescript
export const ChatRoomErrorCode = {
  INVALID_NAME: 'CHAT_ROOM_INVALID_NAME',
  NAME_TOO_LONG: 'CHAT_ROOM_NAME_TOO_LONG',
  CREATE_FAILED: 'CHAT_ROOM_CREATE_FAILED',
  NOT_FOUND: 'CHAT_ROOM_NOT_FOUND',
} as const;

export type ChatRoomErrorCode =
  typeof ChatRoomErrorCode[keyof typeof ChatRoomErrorCode];

export const chatRoomErrorMessages: Record<ChatRoomErrorCode, string> = {
  CHAT_ROOM_INVALID_NAME: '채팅방 이름을 입력해주세요.',
  CHAT_ROOM_NAME_TOO_LONG: '채팅방 이름은 최대 50자입니다.',
  CHAT_ROOM_CREATE_FAILED: '채팅방 생성에 실패했습니다. 다시 시도해주세요.',
  CHAT_ROOM_NOT_FOUND: '채팅방을 찾을 수 없습니다.',
};
```

### 5.4 DTO 재노출

**파일**: `src/features/chat-rooms/lib/dto.ts`

```typescript
export {
  CreateChatRoomRequestSchema,
  CreateChatRoomResponseSchema,
  type CreateChatRoomRequest,
  type CreateChatRoomResponse,
} from '../backend/schema';
```

### 5.5 Hono 앱에 라우터 등록

**파일**: `src/backend/hono/app.ts` (수정)

```typescript
import { chatRoomRoutes } from '@/features/chat-rooms/backend/route';

export function createHonoApp(): Hono<AppEnv> {
  // ... 기존 코드

  // 라우터 등록
  app.route('/', chatRoomRoutes); // 추가

  return app;
}
```

---

## 6. UI/UX 상세

### 6.1 화면 구성

```
┌──────────────────────────────────────┐
│ 채팅방 만들기                         │  ← FormHeader
├──────────────────────────────────────┤
│                                      │
│ 채팅방 이름                           │
│ ┌──────────────────────────────────┐ │
│ │ [입력창]                    10/50│ │  ← Input + Counter
│ └──────────────────────────────────┘ │
│ ⚠️ 에러 메시지 (조건부)               │  ← ErrorMessage
│                                      │
│                                      │
│                                      │
│                                      │
├──────────────────────────────────────┤
│ [취소]                        [생성] │  ← FormFooter
└──────────────────────────────────────┘
```

### 6.2 인터랙션 상세

#### 입력 중
- **실시간 글자 수 카운터 업데이트**: `N/50자` 형식
- **50자 초과 시 추가 입력 차단**: `maxLength={50}` 속성 사용
- **유효하지 않은 입력 시 즉시 에러 메시지 표시**: React Hook Form의 `mode: 'onChange'`

#### 제출 시
- **로딩 인디케이터 표시**: 생성 버튼 내부에 스피너 표시
- **제출 버튼 비활성화**: `disabled={!isValid || isPending}`
- **키보드 Enter 키로도 제출 가능**: 폼의 기본 동작 사용

#### 성공 시
- **홈 페이지로 리다이렉트**: `router.push(response.redirectTo)`
- **채팅방 목록 캐시 무효화**: `queryClient.invalidateQueries`

#### 실패 시
- **에러 메시지 표시**: 입력 필드 아래 또는 토스트
- **입력 내용 유지**: 폼 값 초기화 안 함
- **재시도 가능 상태 유지**: 버튼 다시 활성화

### 6.3 스타일링 (Tailwind CSS)

```tsx
// FormHeader
<h1 className="text-2xl font-bold px-4 py-6">채팅방 만들기</h1>

// Input
<input
  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
  placeholder="채팅방 이름을 입력하세요"
/>

// Character Counter
<span className="text-sm text-gray-500">
  {name.length}/50자
</span>

// Error Message
<p className="text-sm text-destructive mt-1">
  {errors.name?.message}
</p>

// Cancel Button
<button
  type="button"
  className="flex-1 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
>
  취소
</button>

// Submit Button
<button
  type="submit"
  className="flex-1 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
  disabled={!isValid || isPending}
>
  {isPending ? '생성 중...' : '생성'}
</button>
```

---

## 7. 에러 처리

### 7.1 클라이언트 측 검증 에러

| 조건 | 에러 메시지 | 처리 방법 |
|------|-------------|-----------|
| 빈 문자열 | "채팅방 이름을 입력해주세요" | 입력 필드 아래 표시, 제출 차단 |
| 50자 초과 | "채팅방 이름은 최대 50자입니다" | 입력 필드 아래 표시, 추가 입력 차단 |

### 7.2 서버 측 에러

| HTTP 상태 | 에러 코드 | 에러 메시지 | 처리 방법 |
|-----------|-----------|-------------|-----------|
| 400 | `INVALID_NAME` | "채팅방 이름을 입력해주세요" | 입력 필드 아래 표시 |
| 401 | `UNAUTHORIZED` | "인증이 필요합니다" | 로그인 페이지로 리다이렉트 |
| 500 | `CREATE_FAILED` | "채팅방 생성에 실패했습니다. 다시 시도해주세요" | 토스트 메시지 표시 |
| Network Error | - | "네트워크 오류가 발생했습니다. 다시 시도해주세요" | 토스트 메시지 표시 |

### 7.3 에러 처리 흐름

```typescript
const handleSubmit = form.handleSubmit(async (data) => {
  try {
    await createChatRoom.mutateAsync(data);
    // 성공 시 자동 리다이렉트 (onSuccess에서 처리)
  } catch (error) {
    // API 에러
    if (error.response?.status === 401) {
      router.push('/login?redirectedFrom=/chat-rooms/new');
    } else {
      toast.error(
        error.response?.data?.error?.message ||
        '채팅방 생성에 실패했습니다. 다시 시도해주세요'
      );
    }
  }
});
```

---

## 8. 구현 순서

### Phase 1: 백엔드 구현 (우선순위 높음)

1. ✅ **에러 코드 정의** (`backend/error.ts`)
   - 채팅방 관련 에러 코드 정의
   - 에러 메시지 매핑

2. ✅ **서비스 레이어 구현** (`backend/service.ts`)
   - `createChatRoom` 함수 구현
   - Supabase INSERT 쿼리
   - 에러 처리

3. ✅ **Hono 라우터 구현** (`backend/route.ts`)
   - `POST /api/chat-rooms` 라우트 정의
   - 인증 미들웨어 적용
   - Zod 검증
   - 서비스 레이어 호출
   - 응답 포맷팅

4. ✅ **Hono 앱에 라우터 등록** (`backend/hono/app.ts`)
   - `chatRoomRoutes` import 및 등록

5. ✅ **DTO 재노출** (`lib/dto.ts`)
   - 스키마 재노출 (프론트엔드 사용)

### Phase 2: 프론트엔드 구현

6. ⚠️ **React Query Mutation Hook** (`hooks/useCreateChatRoom.ts`)
   - `useMutation` 정의
   - API 클라이언트 호출
   - 캐시 무효화
   - 성공/실패 처리

7. ⚠️ **폼 컴포넌트** (`components/create-chat-room-form.tsx`)
   - React Hook Form 설정
   - Zod 스키마 검증
   - 입력 필드, 글자 수 카운터
   - 에러 메시지 표시
   - 취소/생성 버튼
   - 로딩 상태 표시

8. ⚠️ **페이지 컴포넌트** (`app/(protected)/chat-rooms/new/page.tsx`)
   - 페이지 레이아웃
   - 폼 컴포넌트 렌더링
   - 메타데이터 설정

### Phase 3: 테스트 및 개선

9. ✅ **API 테스트**
   - Postman/Thunder Client로 엔드포인트 테스트
   - 유효성 검증 확인
   - 에러 케이스 확인

10. ✅ **UI 테스트**
    - 폼 입력 및 제출 테스트
    - 에러 메시지 표시 확인
    - 리다이렉션 동작 확인

11. ✅ **엣지 케이스 테스트**
    - 빈 문자열 입력
    - 50자 초과 입력
    - 네트워크 오류 시뮬레이션
    - 세션 만료 시뮬레이션

---

## 9. 코드 구현 예시

### 9.1 페이지 컴포넌트

**파일**: `src/app/(protected)/chat-rooms/new/page.tsx`

```typescript
'use client';

import React from 'react';
import { CreateChatRoomForm } from '@/features/chat-rooms/components/create-chat-room-form';

export default async function CreateChatRoomPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <CreateChatRoomForm />
    </div>
  );
}
```

### 9.2 폼 컴포넌트

**파일**: `src/features/chat-rooms/components/create-chat-room-form.tsx`

```typescript
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useCreateChatRoom } from '../hooks/useCreateChatRoom';
import { CreateChatRoomRequestSchema } from '../lib/dto';
import type { CreateChatRoomRequest } from '../lib/dto';

export const CreateChatRoomForm: React.FC = () => {
  const router = useRouter();
  const createChatRoom = useCreateChatRoom();

  const form = useForm<CreateChatRoomRequest>({
    resolver: zodResolver(CreateChatRoomRequestSchema),
    defaultValues: {
      name: '',
    },
    mode: 'onChange',
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      await createChatRoom.mutateAsync(data);
      // 성공 시 자동 리다이렉트 (useCreateChatRoom onSuccess에서 처리)
    } catch (error) {
      console.error('채팅방 생성 실패:', error);
      // 에러 처리는 mutation hook에서 수행
    }
  });

  const handleCancel = () => {
    router.push('/');
  };

  const nameLength = form.watch('name')?.length || 0;
  const isValid = form.formState.isValid;
  const isPending = createChatRoom.isPending;

  return (
    <div className="max-w-lg mx-auto bg-white shadow-md rounded-lg mt-8">
      {/* Header */}
      <div className="px-6 py-4 border-b">
        <h1 className="text-2xl font-bold">채팅방 만들기</h1>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-6">
        {/* Input Field */}
        <div className="mb-6">
          <label htmlFor="name" className="block text-sm font-medium mb-2">
            채팅방 이름
          </label>
          <div className="relative">
            <input
              id="name"
              {...form.register('name')}
              type="text"
              placeholder="채팅방 이름을 입력하세요"
              maxLength={50}
              disabled={isPending}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-gray-100"
            />
            <span className="absolute right-3 top-3 text-sm text-gray-500">
              {nameLength}/50자
            </span>
          </div>

          {/* Error Message */}
          {form.formState.errors.name && (
            <p className="text-sm text-destructive mt-2">
              {form.formState.errors.name.message}
            </p>
          )}
        </div>

        {/* API Error */}
        {createChatRoom.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              {createChatRoom.error?.response?.data?.error?.message ||
                '채팅방 생성에 실패했습니다. 다시 시도해주세요.'}
            </p>
          </div>
        )}

        {/* Footer Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isPending}
            className="flex-1 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={!isValid || isPending}
            className="flex-1 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                생성 중...
              </>
            ) : (
              '생성'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
```

### 9.3 React Query Mutation Hook

**파일**: `src/features/chat-rooms/hooks/useCreateChatRoom.ts`

```typescript
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/remote/api-client';
import { queryKeys } from '@/lib/query/keys';
import type {
  CreateChatRoomRequest,
  CreateChatRoomResponse,
} from '../lib/dto';

export const useCreateChatRoom = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<CreateChatRoomResponse, Error, CreateChatRoomRequest>({
    mutationFn: async (data) => {
      const response = await apiClient.post<CreateChatRoomResponse>(
        '/api/chat-rooms',
        data
      );
      return response.data;
    },

    onSuccess: (response) => {
      // 채팅방 목록 캐시 무효화
      queryClient.invalidateQueries({
        queryKey: queryKeys.chatRooms.all(),
      });

      // 홈으로 리다이렉트
      router.push(response.redirectTo);
    },

    onError: (error) => {
      console.error('채팅방 생성 실패:', error);
      // 에러 처리는 컴포넌트에서 수행
    },
  });
};
```

---

## 10. 주의사항 및 베스트 프랙티스

### 10.1 공통 모듈 의존성

- **필수**: `CreateChatRoomRequestSchema`, `CreateChatRoomResponseSchema`는 이미 `src/features/chat-rooms/backend/schema.ts`에 정의되어 있음
- **재사용**: `lib/dto.ts`를 통해 프론트엔드에서 재노출하여 사용

### 10.2 코드 스타일 준수

- **Client Component**: 모든 컴포넌트에 `'use client'` 디렉티브 사용
- **타입 안전성**: Zod 스키마로 요청/응답 타입 보장
- **에러 처리**: try-catch 대신 React Query의 `onError` 콜백 활용
- **로딩 상태**: `isPending` 플래그로 버튼 비활성화 및 스피너 표시

### 10.3 보안

- **XSS 방지**: 입력값 HTML 이스케이프 (React의 기본 동작)
- **SQL Injection 방지**: Supabase 클라이언트의 파라미터화된 쿼리 사용
- **인증 검증**: 백엔드에서 `requireAuth()` 미들웨어로 세션 확인

### 10.4 접근성

- **Label 연결**: `<label htmlFor="name">` 와 `<input id="name">` 연결
- **에러 메시지**: `aria-describedby`로 에러 메시지 연결 (권장)
- **키보드 접근**: Enter 키로 폼 제출 가능

### 10.5 성능

- **Debounce 불필요**: 입력 필드는 검증만 수행, API 호출 없음
- **캐시 무효화**: 생성 성공 시 채팅방 목록 캐시 무효화하여 최신 데이터 반영

---

## 11. 테스트 시나리오

### 11.1 성공 케이스

| 테스트 케이스 | 입력값 | 기대 결과 |
|--------------|--------|----------|
| TC-001 | "일상 잡담" | 채팅방 생성 성공, 홈으로 리다이렉트 |
| TC-002 | "가" (1자) | 최소 길이 허용, 생성 성공 |
| TC-003 | "A".repeat(50) | 최대 길이 허용, 생성 성공 |
| TC-004 | "자유 주제 💬" (이모지 포함) | 이모지 허용, 생성 성공 |
| TC-005 | 동일 이름 2회 생성 | 중복 허용, 모두 생성 성공 |

### 11.2 실패 케이스

| 테스트 케이스 | 입력값 | 기대 결과 |
|--------------|--------|----------|
| TC-006 | "" (빈 문자열) | "채팅방 이름을 입력해주세요" 에러 |
| TC-007 | "   " (공백만) | "채팅방 이름을 입력해주세요" 에러 |
| TC-008 | "A".repeat(51) | 입력 차단 또는 검증 실패 |
| TC-009 | 세션 만료 상태 | 로그인 페이지로 리다이렉트 |
| TC-010 | 네트워크 오류 | "네트워크 오류" 메시지, 재시도 가능 |

### 11.3 UX 테스트

| 테스트 케이스 | 시나리오 | 기대 결과 |
|--------------|---------|----------|
| TC-011 | 취소 버튼 클릭 | 홈으로 이동, 입력 내용 버림 |
| TC-012 | 브라우저 뒤로가기 | 홈으로 이동, 입력 내용 유실 |
| TC-013 | 글자 수 카운터 | 입력 시 실시간 업데이트 |
| TC-014 | Enter 키 제출 | 생성 버튼 클릭과 동일 동작 |
| TC-015 | 제출 중 취소 버튼 | 버튼 비활성화 상태 |

---

## 12. 의존성 체크리스트

### 12.1 공통 모듈 (이미 구현됨)

- ✅ `CreateChatRoomRequestSchema` (`src/features/chat-rooms/backend/schema.ts`)
- ✅ `CreateChatRoomResponseSchema` (`src/features/chat-rooms/backend/schema.ts`)
- ✅ `ChatRoom` 타입 (`src/features/chat-rooms/types.ts`)
- ✅ `requireAuth` 미들웨어 (`src/backend/middleware/auth.ts`)
- ✅ `apiClient` (`src/lib/remote/api-client.ts`)
- ✅ `queryKeys` (`src/lib/query/keys.ts`)

### 12.2 라이브러리

- ✅ React Hook Form (`@hookform/resolvers`)
- ✅ Zod (`zod`)
- ✅ React Query (`@tanstack/react-query`)
- ✅ Next.js (`next/navigation`)
- ✅ Lucide React (`lucide-react`)
- ✅ Tailwind CSS

### 12.3 데이터베이스

- ✅ `chat_rooms` 테이블 마이그레이션 (`supabase/migrations/0002_create_chat_rooms.sql`)

---

## 13. 완료 조건 (Definition of Done)

- [ ] 백엔드 라우터 구현 및 테스트 (`POST /api/chat-rooms`)
- [ ] 서비스 레이어 구현 (Supabase INSERT)
- [ ] 에러 코드 정의 (`backend/error.ts`)
- [ ] DTO 재노출 (`lib/dto.ts`)
- [ ] Hono 앱에 라우터 등록
- [ ] React Query Mutation Hook 구현
- [ ] 폼 컴포넌트 구현 (React Hook Form + Zod)
- [ ] 페이지 컴포넌트 구현
- [ ] 클라이언트 측 유효성 검증 동작 확인
- [ ] 서버 측 유효성 검증 동작 확인
- [ ] 에러 처리 및 표시 확인
- [ ] 생성 성공 시 홈 리다이렉트 확인
- [ ] 취소 버튼 동작 확인
- [ ] 로딩 상태 표시 확인
- [ ] 모든 테스트 케이스 통과

---

## 14. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0 | 2025-10-20 | Claude Code | 초기 작성 |

---

**문서 종료**
