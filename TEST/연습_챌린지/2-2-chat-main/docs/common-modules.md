# 공통 모듈 작업 계획

## 문서 개요

이 문서는 페이지 단위 개발을 시작하기 전에 구현해야 할 공통 모듈 및 로직을 정의합니다. 모든 항목은 PRD, Userflow, Database 설계 문서 및 유스케이스 문서에 명시된 내용만을 기반으로 설계되었으며, 오버엔지니어링을 최소화했습니다.

**중요**: 이 문서에 정의된 공통 모듈은 **모든 페이지 단위 개발이 병렬로 진행될 수 있도록** 사전에 구현되어야 하며, 코드 충돌을 방지합니다.

---

## 1. 공통 타입 정의

### 1.1 메시지 관련 타입

**목적**: 메시지 데이터 구조를 일관되게 정의하여 프론트엔드와 백엔드에서 재사용

**구현 위치**: `src/features/messages/types.ts`

**주요 타입**:
```typescript
export type MessageType = 'text' | 'emoticon';

export type Message = {
  id: string;
  chat_room_id: string;
  sender_id: string;
  sender_nickname: string;
  message_type: MessageType;
  content: string | null;
  emoticon_id: string | null;
  reply_to_message_id: string | null;
  created_at: string;

  // 답장 정보 (있는 경우)
  reply_to?: {
    message_id: string;
    sender_nickname: string;
    message_type: MessageType;
    content: string | null;
    emoticon_id: string | null;
  };

  // 좋아요 정보
  like_count: number;
  is_liked_by_me: boolean;
};
```

**의존성**: 없음

---

### 1.2 채팅방 관련 타입

**목적**: 채팅방 데이터 구조 정의

**구현 위치**: `src/features/chat-rooms/types.ts`

**주요 타입**:
```typescript
export type ChatRoom = {
  id: string;
  name: string;
  created_at: string;

  // 최근 메시지 정보 (목록 조회 시)
  last_message_content?: string | null;
  last_message_type?: MessageType | null;
  last_message_emoticon_id?: string | null;
  last_message_time?: string | null;
  last_message_sender?: string | null;
};
```

**의존성**: `MessageType` (messages/types.ts)

---

### 1.3 사용자 프로필 타입

**목적**: 사용자 프로필 데이터 구조 정의

**구현 위치**: `src/features/users/types.ts`

**주요 타입**:
```typescript
export type UserProfile = {
  id: string;
  nickname: string;
  email: string;
};
```

**의존성**: 없음

---

## 2. 공통 검증 스키마 (Zod)

### 2.1 인증 스키마

**목적**: 회원가입/로그인 입력값 검증

**구현 위치**: `src/features/auth/backend/schema.ts`

**주요 스키마**:
```typescript
import { z } from 'zod';

// 회원가입
export const SignupRequestSchema = z.object({
  nickname: z.string()
    .min(2, '닉네임은 2~20자여야 합니다')
    .max(20, '닉네임은 2~20자여야 합니다')
    .regex(/^[가-힣a-zA-Z0-9]+$/, '특수문자는 사용할 수 없습니다'),
  email: z.string().email('유효한 이메일 주소를 입력하세요'),
  password: z.string()
    .min(8, '비밀번호는 8자 이상이어야 합니다')
    .regex(/^(?=.*[A-Za-z])(?=.*\d)/, '영문+숫자 조합이어야 합니다'),
});

export const SignupResponseSchema = z.object({
  success: z.literal(true),
  redirectTo: z.string(),
});

// 로그인
export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export const LoginResponseSchema = z.object({
  success: z.literal(true),
  user: z.object({
    id: z.string(),
    email: z.string(),
    nickname: z.string(),
  }),
  redirectTo: z.string(),
});
```

**의존성**: zod

---

### 2.2 메시지 스키마

**목적**: 메시지 전송/삭제 요청 검증

**구현 위치**: `src/features/messages/backend/schema.ts`

**주요 스키마**:
```typescript
import { z } from 'zod';

export const MessageTypeEnum = z.enum(['text', 'emoticon']);

// 텍스트 메시지 전송
export const SendTextMessageSchema = z.object({
  message_type: z.literal('text'),
  content: z.string().min(1).max(1000),
  reply_to_message_id: z.string().uuid().optional(),
});

// 이모티콘 메시지 전송
export const SendEmoticonMessageSchema = z.object({
  message_type: z.literal('emoticon'),
  emoticon_id: z.string(),
  reply_to_message_id: z.string().uuid().optional(),
});

// 메시지 전송 (Union)
export const SendMessageRequestSchema = z.discriminatedUnion('message_type', [
  SendTextMessageSchema,
  SendEmoticonMessageSchema,
]);

// 메시지 일괄 삭제
export const BatchDeleteMessagesSchema = z.object({
  message_ids: z.array(z.string().uuid()).min(1, '삭제할 메시지를 선택해주세요'),
});
```

**의존성**: zod

---

### 2.3 사용자 프로필 스키마

**목적**: 닉네임 수정 요청 검증

**구현 위치**: `src/features/users/backend/schema.ts`

**주요 스키마**:
```typescript
import { z } from 'zod';

export const UpdateNicknameRequestSchema = z.object({
  nickname: z.string()
    .min(2, '닉네임은 2~20자여야 합니다')
    .max(20, '닉네임은 2~20자여야 합니다')
    .regex(/^[가-힣a-zA-Z0-9]+$/, '특수문자는 사용할 수 없습니다'),
});

export const UpdateNicknameResponseSchema = z.object({
  success: z.literal(true),
  data: z.object({
    id: z.string(),
    nickname: z.string(),
    email: z.string(),
  }),
});
```

**의존성**: zod

---

### 2.4 채팅방 스키마

**목적**: 채팅방 생성 요청 검증

**구현 위치**: `src/features/chat-rooms/backend/schema.ts`

**주요 스키마**:
```typescript
import { z } from 'zod';

export const CreateChatRoomRequestSchema = z.object({
  name: z.string()
    .min(1, '채팅방 이름을 입력해주세요')
    .max(50, '채팅방 이름은 최대 50자입니다'),
});

export const CreateChatRoomResponseSchema = z.object({
  success: z.literal(true),
  data: z.object({
    id: z.string(),
    name: z.string(),
    created_at: z.string(),
  }),
  redirectTo: z.string(),
});
```

**의존성**: zod

---

## 3. 공통 에러 코드 정의

### 3.1 인증 에러

**구현 위치**: `src/features/auth/backend/error.ts`

**에러 코드**:
```typescript
export const AuthErrorCode = {
  EMAIL_DUPLICATE: 'AUTH_EMAIL_DUPLICATE',
  INVALID_CREDENTIALS: 'AUTH_INVALID_CREDENTIALS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',
  UNAUTHORIZED: 'UNAUTHORIZED',
} as const;

export type AuthErrorCode = typeof AuthErrorCode[keyof typeof AuthErrorCode];

export const authErrorMessages: Record<AuthErrorCode, string> = {
  AUTH_EMAIL_DUPLICATE: '이미 가입된 이메일입니다.',
  AUTH_INVALID_CREDENTIALS: '이메일 또는 비밀번호가 올바르지 않습니다.',
  SESSION_EXPIRED: '세션이 만료되었습니다. 다시 로그인해주세요.',
  UNAUTHORIZED: '인증이 필요합니다.',
};
```

**의존성**: 없음

---

### 3.2 메시지 에러

**구현 위치**: `src/features/messages/backend/error.ts`

**에러 코드**:
```typescript
export const MessageErrorCode = {
  INVALID_MESSAGE_CONTENT: 'INVALID_MESSAGE_CONTENT',
  MESSAGE_TOO_LONG: 'MESSAGE_TOO_LONG',
  MESSAGE_NOT_FOUND: 'MESSAGE_NOT_FOUND',
  CHAT_ROOM_NOT_FOUND: 'CHAT_ROOM_NOT_FOUND',
  REPLY_TARGET_NOT_FOUND: 'REPLY_TARGET_NOT_FOUND',
  NO_MESSAGES_SELECTED: 'NO_MESSAGES_SELECTED',
  FORBIDDEN: 'FORBIDDEN',
} as const;

export type MessageErrorCode = typeof MessageErrorCode[keyof typeof MessageErrorCode];

export const messageErrorMessages: Record<MessageErrorCode, string> = {
  INVALID_MESSAGE_CONTENT: '메시지를 입력해주세요.',
  MESSAGE_TOO_LONG: '메시지는 최대 1000자까지 입력할 수 있습니다.',
  MESSAGE_NOT_FOUND: '메시지를 찾을 수 없습니다.',
  CHAT_ROOM_NOT_FOUND: '채팅방을 찾을 수 없습니다.',
  REPLY_TARGET_NOT_FOUND: '답장 대상 메시지가 삭제되었습니다.',
  NO_MESSAGES_SELECTED: '삭제할 메시지를 선택해주세요.',
  FORBIDDEN: '권한이 없습니다.',
};
```

**의존성**: 없음

---

### 3.3 좋아요 에러

**구현 위치**: `src/features/likes/backend/error.ts`

**에러 코드**:
```typescript
export const LikeErrorCode = {
  MESSAGE_NOT_FOUND: 'MESSAGE_NOT_FOUND',
  LIKE_OWN_MESSAGE: 'LIKE_OWN_MESSAGE',
  ALREADY_LIKED: 'ALREADY_LIKED',
  NOT_LIKED: 'NOT_LIKED',
} as const;

export type LikeErrorCode = typeof LikeErrorCode[keyof typeof LikeErrorCode];

export const likeErrorMessages: Record<LikeErrorCode, string> = {
  MESSAGE_NOT_FOUND: '메시지를 찾을 수 없습니다.',
  LIKE_OWN_MESSAGE: '본인 메시지에는 좋아요를 할 수 없습니다.',
  ALREADY_LIKED: '이미 좋아요한 메시지입니다.',
  NOT_LIKED: '좋아요하지 않은 메시지입니다.',
};
```

**의존성**: 없음

---

## 4. 공통 백엔드 미들웨어

### 4.1 인증 미들웨어

**목적**: API 요청의 Supabase Auth 세션 검증

**구현 위치**: `src/backend/middleware/auth.ts`

**주요 기능**:
- Supabase Auth 세션 검증
- 사용자 ID 추출 및 컨텍스트에 저장
- 미인증 시 401 응답

**인터페이스**:
```typescript
import type { MiddlewareHandler } from 'hono';
import type { AppEnv } from '@/backend/hono/context';

export const requireAuth = (): MiddlewareHandler<AppEnv> => {
  return async (c, next) => {
    const supabase = c.get('supabase');
    const { data, error } = await supabase.auth.getUser();

    if (error || !data.user) {
      return c.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: '인증이 필요합니다.',
          },
        },
        401
      );
    }

    c.set('userId', data.user.id);
    await next();
  };
};
```

**의존성**: Supabase, Hono

---

## 5. 공통 유틸리티 함수

### 5.1 날짜 포맷팅

**목적**: 메시지 시간 표시 포맷팅

**구현 위치**: `src/lib/utils/date.ts`

**주요 함수**:
```typescript
import { format, isToday, isYesterday } from 'date-fns';
import { ko } from 'date-fns/locale';

/**
 * 메시지 시간을 표시용으로 포맷
 * - 오늘: "오후 3:24"
 * - 어제: "어제"
 * - 그 외: "2025.10.20"
 */
export const formatMessageTime = (dateString: string): string => {
  const date = new Date(dateString);

  if (isToday(date)) {
    return format(date, 'a h:mm', { locale: ko });
  }

  if (isYesterday(date)) {
    return '어제';
  }

  return format(date, 'yyyy.MM.dd');
};

/**
 * 채팅방 목록의 최근 메시지 시간 포맷
 * - 오늘: "오후 3:24"
 * - 어제: "어제"
 * - 7일 이내: "월요일"
 * - 그 외: "2025.10.20"
 */
export const formatChatRoomTime = (dateString: string): string => {
  const date = new Date(dateString);

  if (isToday(date)) {
    return format(date, 'a h:mm', { locale: ko });
  }

  if (isYesterday(date)) {
    return '어제';
  }

  const daysDiff = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (daysDiff < 7) {
    return format(date, 'EEEE', { locale: ko });
  }

  return format(date, 'yyyy.MM.dd');
};
```

**의존성**: date-fns

---

### 5.2 이모티콘 관리

**목적**: 고정된 이모티콘 ID 목록 관리

**구현 위치**: `src/constants/emoticons.ts`

**주요 상수**:
```typescript
export const EMOTICONS = [
  { id: 'smile', label: '😊', name: '미소' },
  { id: 'heart', label: '❤️', name: '하트' },
  { id: 'thumbsup', label: '👍', name: '좋아요' },
  { id: 'laugh', label: '😂', name: '웃음' },
  { id: 'sad', label: '😢', name: '슬픔' },
  { id: 'angry', label: '😠', name: '화남' },
  { id: 'surprised', label: '😲', name: '놀람' },
  { id: 'thinking', label: '🤔', name: '생각' },
] as const;

export type EmoticonId = typeof EMOTICONS[number]['id'];

export const getEmoticonById = (id: string) => {
  return EMOTICONS.find(e => e.id === id);
};

export const isValidEmoticonId = (id: string): id is EmoticonId => {
  return EMOTICONS.some(e => e.id === id);
};
```

**의존성**: 없음

---

### 5.3 메시지 내용 sanitization

**목적**: XSS 방지를 위한 HTML 이스케이프

**구현 위치**: `src/lib/utils/sanitize.ts`

**주요 함수**:
```typescript
/**
 * HTML 태그 이스케이프 처리
 */
export const escapeHtml = (text: string): string => {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };

  return text.replace(/[&<>"']/g, (char) => map[char]);
};
```

**의존성**: 없음

---

## 6. 공통 React Query 설정

### 6.1 QueryClient 설정

**목적**: React Query 전역 설정

**구현 위치**: `src/lib/query/client.ts`

**주요 설정**:
```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1분
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});
```

**의존성**: @tanstack/react-query

---

### 6.2 Query Key Factory

**목적**: 일관된 Query Key 관리

**구현 위치**: `src/lib/query/keys.ts`

**주요 함수**:
```typescript
export const queryKeys = {
  // 사용자
  users: {
    me: () => ['users', 'me'] as const,
  },

  // 채팅방
  chatRooms: {
    all: () => ['chat-rooms'] as const,
    detail: (id: string) => ['chat-rooms', id] as const,
  },

  // 메시지
  messages: {
    list: (chatRoomId: string) => ['messages', chatRoomId] as const,
  },
} as const;
```

**의존성**: 없음

---

## 7. 공통 UI 컴포넌트

### 7.1 에러 메시지 표시

**목적**: 일관된 에러 메시지 표시

**구현 위치**: `src/components/common/error-message.tsx`

**인터페이스**:
```typescript
'use client';

import React from 'react';

export type ErrorMessageProps = {
  message: string;
  onRetry?: () => void;
};

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-4">
      <p className="text-destructive text-sm">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="text-primary underline text-sm">
          다시 시도
        </button>
      )}
    </div>
  );
};
```

**의존성**: React

---

### 7.2 로딩 스피너

**목적**: 일관된 로딩 표시

**구현 위치**: `src/components/common/loading-spinner.tsx`

**인터페이스**:
```typescript
'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

export type LoadingSpinnerProps = {
  size?: 'sm' | 'md' | 'lg';
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md' }) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className="flex items-center justify-center py-8">
      <Loader2 className={`${sizeClass} animate-spin text-primary`} />
    </div>
  );
};
```

**의존성**: React, lucide-react

---

### 7.3 빈 상태 표시

**목적**: 데이터가 없을 때 일관된 UI

**구현 위치**: `src/components/common/empty-state.tsx`

**인터페이스**:
```typescript
'use client';

import React from 'react';

export type EmptyStateProps = {
  title: string;
  description?: string;
  action?: React.ReactNode;
};

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <h3 className="text-lg font-semibold text-muted-foreground">{title}</h3>
      {description && <p className="text-sm text-muted-foreground">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
};
```

**의존성**: React

---

## 8. 라우트 보호 로직

### 8.1 인증 필수 페이지 보호

**목적**: 비로그인 사용자의 인증 페이지 접근 차단

**구현 위치**: 기존 `src/app/(protected)/layout.tsx` 개선

**주요 기능**:
- 비로그인 사용자는 `/login`으로 리다이렉트
- `redirectedFrom` 쿼리 파라미터에 원래 경로 저장

**구현 참고**:
```typescript
// 이미 구현되어 있으므로 검토만 필요
// 필요시 리다이렉트 로직 개선
```

**의존성**: Next.js, Supabase

---

### 8.2 비인증 페이지 보호

**목적**: 로그인된 사용자의 로그인/회원가입 페이지 접근 차단

**구현 위치**: `src/app/(public)/layout.tsx` (신규 생성 필요 여부 확인)

**주요 기능**:
- 로그인된 사용자는 `/`로 리다이렉트

**구현 참고**:
```typescript
// 현재 middleware.ts에서 처리 중인지 확인
// 필요시 별도 레이아웃으로 분리
```

**의존성**: Next.js, Supabase

---

## 9. API 응답 포맷 표준화

### 9.1 성공 응답 포맷

**구현 위치**: 기존 `src/backend/http/response.ts` 사용

**포맷**:
```typescript
// 이미 구현된 success 함수 사용
{
  // 데이터만 반환 (success 플래그 없음)
  data: T
}
```

**의존성**: 기존 코드 사용

---

### 9.2 에러 응답 포맷

**구현 위치**: 기존 `src/backend/http/response.ts` 사용

**포맷**:
```typescript
// 이미 구현된 failure 함수 사용
{
  error: {
    code: string,
    message: string,
    details?: unknown
  }
}
```

**의존성**: 기존 코드 사용

---

## 10. 데이터베이스 마이그레이션 준비

### 10.1 테이블 생성 SQL

**목적**: Supabase 데이터베이스 스키마 생성

**구현 위치**: `supabase/migrations/`

**필요 마이그레이션**:
1. `0001_create_user_profiles.sql`: user_profiles 테이블
2. `0002_create_chat_rooms.sql`: chat_rooms 테이블
3. `0003_create_messages.sql`: messages 테이블, message_type_enum
4. `0004_create_message_likes.sql`: message_likes 테이블

**참고**: Database 문서의 스키마 정의에 따라 작성

**의존성**: Supabase

---

## 11. 환경 변수 설정

### 11.1 필수 환경 변수

**구현 위치**: `.env.local` (사용자 생성), `src/constants/env.ts` (검증)

**필요 변수**:
```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
NEXT_PUBLIC_API_BASE_URL=
```

**의존성**: Supabase 프로젝트 생성 필요

---

## 12. 구현 우선순위

### Phase 1: 핵심 기반 (병렬 개발 전 필수)
1. ✅ 공통 타입 정의 (messages, chat-rooms, users)
2. ✅ 공통 검증 스키마 (auth, messages, users, chat-rooms)
3. ✅ 공통 에러 코드 (auth, messages, likes)
4. ✅ 인증 미들웨어 (requireAuth)
5. ✅ 공통 유틸리티 (날짜, 이모티콘, sanitize)
6. ✅ 데이터베이스 마이그레이션 SQL 파일 작성

### Phase 2: UI 및 상태 관리 (선택적 병렬 가능)
7. ⚠️ 공통 UI 컴포넌트 (ErrorMessage, LoadingSpinner, EmptyState)
8. ⚠️ Query Key Factory
9. ⚠️ 라우트 보호 로직 검토 및 개선

### Phase 3: 검증 및 문서화
10. ✅ 환경 변수 설정 가이드
11. ✅ API 응답 포맷 문서화 (기존 사용)

**범례**:
- ✅ 필수 (Phase 1 완료 전까지 병렬 개발 불가)
- ⚠️ 권장 (병렬 개발 가능하지만 중복 구현 방지 위해 사전 구현 권장)

---

## 13. 검증 체크리스트

### 코드 충돌 방지 검증

다음 항목들이 **Phase 1 완료 후**에 각 페이지 개발이 병렬로 진행될 수 있는지 확인:

- [x] **타입 정의**: 모든 feature에서 사용할 Message, ChatRoom, UserProfile 타입이 공통 정의되었는가?
- [x] **검증 스키마**: 모든 API 엔드포인트의 요청/응답 스키마가 공통 정의되었는가?
- [x] **에러 코드**: 모든 feature의 에러 코드가 충돌 없이 정의되었는가?
- [x] **인증 미들웨어**: 모든 보호된 엔드포인트에서 사용할 인증 로직이 공통화되었는가?
- [x] **유틸리티 함수**: 날짜 포맷팅, 이모티콘 관리 등 공통 로직이 중복 구현되지 않도록 정의되었는가?
- [x] **데이터베이스 스키마**: 모든 테이블이 사전에 정의되고 마이그레이션 파일로 작성되었는가?

**검증 결과**: ✅ 모든 항목이 Phase 1에 포함되어 있으며, 병렬 개발 시 코드 충돌이 발생하지 않도록 설계되었습니다.

### 오버엔지니어링 검증

다음 항목들이 PRD/Userflow/Database 문서에 **명시된 내용만** 포함하는지 확인:

- [x] 메시지 수정 기능: 제외 (PRD에 명시: 수정 불가)
- [x] 채팅방 삭제 기능: 제외 (PRD에 명시: 삭제 기능 없음)
- [x] 사용자 차단 기능: 제외 (Phase 3로 명시)
- [x] 읽음/안읽음 표시: 제외 (Phase 3로 명시)
- [x] 파일 업로드: 제외 (PRD에 명시: 텍스트/이모티콘만)
- [x] 실시간 업데이트: 제외 (PRD에 선택 사항으로 명시, 초기 버전 미포함)

**검증 결과**: ✅ 문서에 명시되지 않은 기능은 모두 제외되었습니다.

---

## 14. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0  | 2025-10-20 | Claude Code | 초기 작성 |

---

**문서 종료**
