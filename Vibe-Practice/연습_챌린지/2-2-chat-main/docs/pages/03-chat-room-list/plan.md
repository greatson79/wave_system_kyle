# 페이지 구현 계획: 홈 - 채팅방 목록 (`/`)

## 1. 페이지 개요

### 1.1 목적
로그인한 사용자가 모든 채팅방을 목록 형태로 조회하고, 원하는 채팅방에 빠르게 접근하거나 새로운 채팅방을 생성할 수 있는 메인 페이지입니다.

### 1.2 주요 기능
- 전체 채팅방 목록 조회 (최근 메시지 시간 기준 정렬)
- 각 채팅방의 최근 메시지 미리보기 표시
- 채팅방 클릭 시 상세 페이지로 이동
- 플로팅 '채팅방 추가' 버튼
- 빈 상태 처리 (채팅방이 없을 경우)
- 로딩 상태 표시

### 1.3 연관 유스케이스
- **UC-005**: 채팅방 목록 조회
- **UC-006**: 채팅방 생성 (채팅방 추가 버튼)

### 1.4 경로 및 레이아웃
- **경로**: `/`
- **레이아웃**: `(protected)/layout.tsx` - 인증 필수
- **접근 권한**: 로그인된 사용자만 접근 가능

---

## 2. 파일 구조

### 2.1 프론트엔드 (페이지 및 컴포넌트)

```
src/
├── app/
│   └── (protected)/
│       └── page.tsx                          # 홈 페이지 (채팅방 목록)
│
├── features/
│   └── chat-rooms/
│       ├── types.ts                          # ✅ 이미 구현됨
│       ├── components/
│       │   ├── chat-room-list.tsx            # 채팅방 목록 컨테이너
│       │   ├── chat-room-card.tsx            # 채팅방 카드 컴포넌트
│       │   └── chat-room-list-header.tsx     # 헤더 컴포넌트
│       ├── hooks/
│       │   └── useChatRoomsQuery.ts          # React Query 훅
│       ├── lib/
│       │   └── dto.ts                        # 응답 스키마 재노출
│       └── backend/
│           ├── schema.ts                     # ✅ 일부 구현됨 (추가 필요)
│           ├── route.ts                      # Hono 라우터 (GET /api/chat-rooms)
│           ├── service.ts                    # 비즈니스 로직 및 DB 조회
│           └── error.ts                      # 에러 코드 정의
│
└── components/
    └── common/
        ├── empty-state.tsx                   # ✅ 이미 구현됨
        ├── loading-spinner.tsx               # ✅ 이미 구현됨
        └── error-message.tsx                 # ✅ 이미 구현됨
```

### 2.2 주요 의존성
- **공통 타입**: `@/features/chat-rooms/types` (ChatRoom), `@/features/messages/types` (MessageType)
- **공통 유틸**: `@/lib/utils/date` (formatChatRoomTime), `@/constants/emoticons` (getEmoticonById)
- **공통 컴포넌트**: EmptyState, LoadingSpinner, ErrorMessage
- **라우트 보호**: `(protected)/layout.tsx`

---

## 3. 컴포넌트 계층 구조

```
page.tsx (/)
  └── ChatRoomList (컨테이너)
      ├── ChatRoomListHeader (헤더)
      │   ├── 서비스 로고
      │   ├── 사용자 정보 (닉네임)
      │   └── 마이페이지 링크
      │
      ├── useChatRoomsQuery (React Query 훅)
      │   ├── 로딩 상태 → LoadingSpinner
      │   ├── 에러 상태 → ErrorMessage
      │   ├── 빈 상태 → EmptyState
      │   └── 성공 → ChatRoomCard[] (목록)
      │
      └── FloatingActionButton (플로팅 버튼)
          └── 채팅방 추가 → /chat-rooms/new
```

---

## 4. 상태 관리

### 4.1 서버 상태 (React Query)

**쿼리 키**: `['chat-rooms']`

**Query Hook**: `useChatRoomsQuery`
```typescript
// src/features/chat-rooms/hooks/useChatRoomsQuery.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import type { ChatRoom } from '../types';
import { ChatRoomListResponseSchema } from '../lib/dto';

export const useChatRoomsQuery = () => {
  return useQuery({
    queryKey: ['chat-rooms'],
    queryFn: async () => {
      const response = await apiClient.get('/api/chat-rooms');
      const parsed = ChatRoomListResponseSchema.parse(response.data);
      return parsed.data;
    },
    staleTime: 1000 * 60, // 1분
    retry: 1,
  });
};
```

**상태 종류**:
- `isLoading`: 초기 로딩 중
- `isError`: 에러 발생
- `data`: ChatRoom[] (채팅방 목록)
- `error`: Error 객체

**캐싱 전략**:
- `staleTime: 1분` - 1분 동안 캐시 데이터 사용
- 페이지 재방문 시 자동 재검증
- 채팅방 생성 후 invalidate로 목록 갱신

### 4.2 클라이언트 상태

이 페이지는 **읽기 전용**이므로 별도의 로컬 상태 관리가 불필요합니다.
- 채팅방 카드 클릭 → Next.js 클라이언트 라우팅 (상태 없음)
- 플로팅 버튼 클릭 → 페이지 이동 (상태 없음)

---

## 5. API 연동

### 5.1 백엔드 엔드포인트

**경로**: `GET /api/chat-rooms`

**요청**:
- **헤더**: Supabase Auth 토큰 (자동 전송)
- **쿼리 파라미터**: 없음
- **요청 본문**: 없음

**응답**:
```typescript
// 성공 (200 OK)
{
  data: [
    {
      id: string;
      name: string;
      created_at: string;
      last_message_content: string | null;
      last_message_type: 'text' | 'emoticon' | null;
      last_message_emoticon_id: string | null;
      last_message_time: string | null;
      last_message_sender: string | null;
    }
  ]
}

// 실패 (401 Unauthorized)
{
  error: {
    code: 'UNAUTHORIZED',
    message: '인증이 필요합니다.'
  }
}

// 실패 (500 Internal Server Error)
{
  error: {
    code: 'INTERNAL_SERVER_ERROR',
    message: '일시적인 오류가 발생했습니다.'
  }
}
```

### 5.2 백엔드 스키마 정의

**파일**: `src/features/chat-rooms/backend/schema.ts`

**추가 필요**:
```typescript
import { z } from 'zod';
import { MessageTypeEnum } from '@/features/messages/backend/schema';

// 채팅방 목록 응답
export const ChatRoomListResponseSchema = z.object({
  data: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      created_at: z.string(),
      last_message_content: z.string().nullable(),
      last_message_type: MessageTypeEnum.nullable(),
      last_message_emoticon_id: z.string().nullable(),
      last_message_time: z.string().nullable(),
      last_message_sender: z.string().nullable(),
    })
  ),
});

export type ChatRoomListResponse = z.infer<typeof ChatRoomListResponseSchema>;
```

### 5.3 백엔드 라우터 구현

**파일**: `src/features/chat-rooms/backend/route.ts`

```typescript
import { Hono } from 'hono';
import type { AppEnv } from '@/backend/hono/context';
import { requireAuth } from '@/backend/middleware/auth';
import { respond } from '@/backend/http/response';
import { listChatRooms } from './service';
import { ChatRoomListResponseSchema } from './schema';

export const chatRoomsRouter = new Hono<AppEnv>();

// GET /api/chat-rooms - 채팅방 목록 조회
chatRoomsRouter.get('/', requireAuth(), async (c) => {
  const supabase = c.get('supabase');
  const logger = c.get('logger');

  try {
    const chatRooms = await listChatRooms(supabase);
    return respond(c, { data: chatRooms }, ChatRoomListResponseSchema);
  } catch (error) {
    logger.error('Failed to list chat rooms', error);
    throw error;
  }
});
```

### 5.4 백엔드 서비스 구현

**파일**: `src/features/chat-rooms/backend/service.ts`

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';
import type { ChatRoom } from '../types';

export async function listChatRooms(
  supabase: SupabaseClient
): Promise<ChatRoom[]> {
  // 채팅방 목록 + 최근 메시지 정보 조회
  const { data, error } = await supabase.rpc('get_chat_rooms_with_last_message');

  if (error) {
    throw new Error(`Failed to fetch chat rooms: ${error.message}`);
  }

  return (data || []) as ChatRoom[];
}
```

**참고**: `get_chat_rooms_with_last_message`는 Supabase 함수로 작성 필요 (또는 복잡한 조인 쿼리)

**대안 (직접 쿼리)**:
```typescript
export async function listChatRooms(
  supabase: SupabaseClient
): Promise<ChatRoom[]> {
  const { data: chatRooms, error: roomsError } = await supabase
    .from('chat_rooms')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(100);

  if (roomsError) {
    throw new Error(`Failed to fetch chat rooms: ${roomsError.message}`);
  }

  // 각 채팅방의 최근 메시지 조회
  const chatRoomsWithMessages = await Promise.all(
    chatRooms.map(async (room) => {
      const { data: messages } = await supabase
        .from('messages')
        .select('content, message_type, emoticon_id, created_at, sender:user_profiles(nickname)')
        .eq('chat_room_id', room.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      return {
        ...room,
        last_message_content: messages?.content || null,
        last_message_type: messages?.message_type || null,
        last_message_emoticon_id: messages?.emoticon_id || null,
        last_message_time: messages?.created_at || null,
        last_message_sender: messages?.sender?.nickname || null,
      };
    })
  );

  // 최근 메시지 시간 기준 재정렬
  return chatRoomsWithMessages.sort((a, b) => {
    const timeA = a.last_message_time || a.created_at;
    const timeB = b.last_message_time || b.created_at;
    return new Date(timeB).getTime() - new Date(timeA).getTime();
  });
}
```

**성능 최적화 고려사항**:
- N+1 쿼리 문제 발생 → Supabase RPC 함수로 대체 권장
- 또는 PostgreSQL LATERAL JOIN 사용

### 5.5 백엔드 에러 코드

**파일**: `src/features/chat-rooms/backend/error.ts`

```typescript
export const ChatRoomErrorCode = {
  CHAT_ROOM_NOT_FOUND: 'CHAT_ROOM_NOT_FOUND',
  INVALID_CHAT_ROOM_NAME: 'INVALID_CHAT_ROOM_NAME',
} as const;

export type ChatRoomErrorCode =
  typeof ChatRoomErrorCode[keyof typeof ChatRoomErrorCode];

export const chatRoomErrorMessages: Record<ChatRoomErrorCode, string> = {
  CHAT_ROOM_NOT_FOUND: '채팅방을 찾을 수 없습니다.',
  INVALID_CHAT_ROOM_NAME: '유효하지 않은 채팅방 이름입니다.',
};
```

---

## 6. UI/UX 상세

### 6.1 헤더 (ChatRoomListHeader)

**구성 요소**:
```
┌─────────────────────────────────────────────┐
│  🏠 채팅 서비스    사용자1님   [ 마이페이지 ] │
└─────────────────────────────────────────────┘
```

**구현**:
```typescript
// src/features/chat-rooms/components/chat-room-list-header.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser';

export const ChatRoomListHeader: React.FC = () => {
  const { user } = useCurrentUser();

  return (
    <header className="sticky top-0 z-10 bg-background border-b">
      <div className="container max-w-4xl mx-auto flex items-center justify-between h-16 px-4">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">채팅 서비스</h1>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            {user?.nickname}님
          </span>
          <Link
            href="/my-page"
            className="text-sm font-medium text-primary hover:underline"
          >
            마이페이지
          </Link>
        </div>
      </div>
    </header>
  );
};
```

### 6.2 채팅방 카드 (ChatRoomCard)

**레이아웃**:
```
┌──────────────────────────────────────────┐
│  채팅방 이름                         오후 3:24 │
│  최근 메시지 미리보기 (50자 제한)...      │
└──────────────────────────────────────────┘
```

**구현**:
```typescript
// src/features/chat-rooms/components/chat-room-card.tsx
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import type { ChatRoom } from '../types';
import { formatChatRoomTime } from '@/lib/utils/date';
import { getEmoticonById } from '@/constants/emoticons';
import { Card, CardContent } from '@/components/ui/card';

type ChatRoomCardProps = {
  chatRoom: ChatRoom;
};

export const ChatRoomCard: React.FC<ChatRoomCardProps> = ({ chatRoom }) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/chat-rooms/${chatRoom.id}`);
  };

  // 최근 메시지 표시 로직
  const getLastMessageDisplay = () => {
    if (!chatRoom.last_message_type) {
      return '메시지가 없습니다';
    }

    if (chatRoom.last_message_type === 'emoticon') {
      const emoticon = getEmoticonById(chatRoom.last_message_emoticon_id || '');
      return emoticon ? `${emoticon.label} 이모티콘` : '[이모티콘]';
    }

    // 텍스트 메시지: 최대 50자
    const content = chatRoom.last_message_content || '';
    return content.length > 50 ? `${content.slice(0, 50)}...` : content;
  };

  const lastMessageTime = chatRoom.last_message_time || chatRoom.created_at;

  return (
    <Card
      className="cursor-pointer hover:bg-accent transition-colors"
      onClick={handleClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-foreground truncate">
              {chatRoom.name}
            </h3>
            <p className="text-sm text-muted-foreground truncate mt-1">
              {getLastMessageDisplay()}
            </p>
          </div>
          <time className="text-xs text-muted-foreground whitespace-nowrap">
            {formatChatRoomTime(lastMessageTime)}
          </time>
        </div>
      </CardContent>
    </Card>
  );
};
```

### 6.3 채팅방 목록 컨테이너 (ChatRoomList)

**구현**:
```typescript
// src/features/chat-rooms/components/chat-room-list.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { useChatRoomsQuery } from '../hooks/useChatRoomsQuery';
import { ChatRoomCard } from './chat-room-card';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { ErrorMessage } from '@/components/common/error-message';
import { EmptyState } from '@/components/common/empty-state';
import { Button } from '@/components/ui/button';

export const ChatRoomList: React.FC = () => {
  const { data: chatRooms, isLoading, isError, error, refetch } = useChatRoomsQuery();

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  if (isError) {
    return (
      <ErrorMessage
        message={error?.message || '채팅방 목록을 불러올 수 없습니다.'}
        onRetry={() => refetch()}
      />
    );
  }

  if (!chatRooms || chatRooms.length === 0) {
    return (
      <EmptyState
        title="아직 채팅방이 없습니다"
        description="새로운 채팅방을 만들어보세요!"
        action={
          <Button asChild>
            <Link href="/chat-rooms/new">
              <Plus className="w-4 h-4 mr-2" />
              채팅방 추가
            </Link>
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      {chatRooms.map((chatRoom) => (
        <ChatRoomCard key={chatRoom.id} chatRoom={chatRoom} />
      ))}
    </div>
  );
};
```

### 6.4 플로팅 액션 버튼

**구현**:
```typescript
// page.tsx 내부에 포함
<Link
  href="/chat-rooms/new"
  className="fixed bottom-6 right-6 z-50"
>
  <Button size="lg" className="rounded-full shadow-lg h-14 w-14 p-0">
    <Plus className="w-6 h-6" />
    <span className="sr-only">채팅방 추가</span>
  </Button>
</Link>
```

### 6.5 페이지 레이아웃

**파일**: `src/app/(protected)/page.tsx`

```typescript
'use client';

import React from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { ChatRoomListHeader } from '@/features/chat-rooms/components/chat-room-list-header';
import { ChatRoomList } from '@/features/chat-rooms/components/chat-room-list';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <ChatRoomListHeader />

      <main className="flex-1 container max-w-4xl mx-auto py-6 px-4">
        <ChatRoomList />
      </main>

      {/* 플로팅 버튼 */}
      <Link href="/chat-rooms/new" className="fixed bottom-6 right-6 z-50">
        <Button size="lg" className="rounded-full shadow-lg h-14 w-14 p-0">
          <Plus className="w-6 h-6" />
          <span className="sr-only">채팅방 추가</span>
        </Button>
      </Link>
    </div>
  );
}
```

### 6.6 반응형 디자인

**모바일 (< 640px)**:
- 헤더 간격 축소
- 카드 패딩 축소
- 플로팅 버튼 위치 조정 (bottom-4, right-4)

**태블릿 (640px ~ 1024px)**:
- 기본 레이아웃 유지
- 최대 너비 제한 (max-w-4xl)

**데스크톱 (> 1024px)**:
- 최대 너비 제한 (max-w-4xl)
- 카드 호버 효과 강조

---

## 7. 에러 처리

### 7.1 인증 실패 (401 Unauthorized)

**처리 방법**:
1. `(protected)/layout.tsx`에서 자동 처리
2. 로그인 페이지로 리다이렉트 (`redirectedFrom=/`)
3. 로그인 성공 후 홈으로 복귀

**구현 위치**: 레이아웃 레벨 (페이지 진입 전)

### 7.2 네트워크 오류

**화면 표시**:
```typescript
<ErrorMessage
  message="채팅방 목록을 불러올 수 없습니다. 네트워크 연결을 확인해주세요."
  onRetry={() => refetch()}
/>
```

**사용자 액션**: "다시 시도" 버튼 클릭 → `refetch()` 호출

### 7.3 서버 오류 (500)

**화면 표시**:
```typescript
<ErrorMessage
  message="일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
  onRetry={() => refetch()}
/>
```

### 7.4 빈 상태 (채팅방 없음)

**화면 표시**:
```typescript
<EmptyState
  title="아직 채팅방이 없습니다"
  description="새로운 채팅방을 만들어보세요!"
  action={<Button>채팅방 추가</Button>}
/>
```

**사용자 액션**: 채팅방 추가 버튼 → `/chat-rooms/new` 이동

---

## 8. 구현 순서

### Phase 1: 백엔드 구현 (우선)
1. ✅ `schema.ts`: ChatRoomListResponseSchema 추가
2. ✅ `error.ts`: ChatRoomErrorCode 정의
3. ✅ `service.ts`: listChatRooms 함수 구현
4. ✅ `route.ts`: GET /api/chat-rooms 엔드포인트 구현
5. ✅ Hono 앱에 chatRoomsRouter 등록 (`src/backend/hono/app.ts`)

### Phase 2: 프론트엔드 기초
6. ✅ `lib/dto.ts`: ChatRoomListResponseSchema 재노출
7. ✅ `hooks/useChatRoomsQuery.ts`: React Query 훅 구현
8. ✅ `components/chat-room-card.tsx`: 카드 컴포넌트
9. ✅ `components/chat-room-list-header.tsx`: 헤더 컴포넌트

### Phase 3: 페이지 조립
10. ✅ `components/chat-room-list.tsx`: 목록 컨테이너
11. ✅ `app/(protected)/page.tsx`: 페이지 조립 및 플로팅 버튼

### Phase 4: 테스트 및 검증
12. ✅ 로딩 상태 확인
13. ✅ 에러 상태 확인 (네트워크 차단 테스트)
14. ✅ 빈 상태 확인 (DB에서 채팅방 삭제 후)
15. ✅ 채팅방 클릭 시 라우팅 확인
16. ✅ 플로팅 버튼 클릭 시 이동 확인
17. ✅ 반응형 확인 (모바일, 태블릿, 데스크톱)

---

## 9. 의존성 확인

### 9.1 구현 완료된 공통 모듈
- ✅ `EmptyState` 컴포넌트
- ✅ `LoadingSpinner` 컴포넌트
- ✅ `ErrorMessage` 컴포넌트
- ✅ `ChatRoom` 타입
- ✅ `MessageType` 타입
- ✅ `formatChatRoomTime` 함수
- ✅ `getEmoticonById` 함수
- ✅ `requireAuth` 미들웨어
- ✅ `(protected)/layout.tsx` (인증 보호)

### 9.2 구현 필요한 항목
- ⚠️ `ChatRoomListResponseSchema` (schema.ts 추가)
- ⚠️ `listChatRooms` 서비스 함수
- ⚠️ `GET /api/chat-rooms` 라우터
- ⚠️ `useChatRoomsQuery` 훅
- ⚠️ 페이지 컴포넌트 전체

---

## 10. 주의사항

### 10.1 DRY 원칙 준수
- 날짜 포맷팅: `@/lib/utils/date`의 `formatChatRoomTime` 사용
- 이모티콘 표시: `@/constants/emoticons`의 `getEmoticonById` 사용
- 공통 UI: EmptyState, LoadingSpinner, ErrorMessage 재사용

### 10.2 타입 안전성
- 모든 API 응답은 Zod 스키마로 검증
- React Query 훅의 반환 타입 명시
- 컴포넌트 Props는 명시적 타입 정의

### 10.3 성능 최적화
- React Query 캐싱 활용 (staleTime: 1분)
- 채팅방 목록은 최대 100개 제한
- 불필요한 리렌더링 방지 (React.memo 고려)

### 10.4 접근성
- 플로팅 버튼에 `sr-only` 레이블 추가
- 키보드 네비게이션 지원 (Link, Button)
- 시맨틱 HTML 사용 (header, main)

### 10.5 코드 충돌 방지
- 기존 `chat-rooms/backend/schema.ts` 수정 시 기존 코드 유지
- Hono 앱 라우터 등록 시 순서 확인
- 타입 import 경로 일관성 유지

---

## 11. 테스트 케이스

### 11.1 기능 테스트

| ID | 시나리오 | 기대 결과 |
|----|---------|----------|
| TC-01 | 로그인 후 홈 페이지 접근 | 채팅방 목록 로딩 후 표시 |
| TC-02 | 채팅방이 없는 상태 | EmptyState 표시, "채팅방 추가" 버튼 강조 |
| TC-03 | 채팅방 카드 클릭 | `/chat-rooms/:id` 로 이동 |
| TC-04 | 플로팅 버튼 클릭 | `/chat-rooms/new` 로 이동 |
| TC-05 | 마이페이지 링크 클릭 | `/my-page` 로 이동 |
| TC-06 | 네트워크 오류 발생 | ErrorMessage + "다시 시도" 버튼 |
| TC-07 | "다시 시도" 버튼 클릭 | API 재요청 |

### 11.2 UI 테스트

| ID | 시나리오 | 기대 결과 |
|----|---------|----------|
| TC-08 | 텍스트 메시지가 최근인 채팅방 | 내용 50자 제한 표시 |
| TC-09 | 이모티콘 메시지가 최근인 채팅방 | "[이모티콘]" 또는 이모지 표시 |
| TC-10 | 메시지가 없는 채팅방 | "메시지가 없습니다" 표시 |
| TC-11 | 탈퇴한 사용자가 보낸 메시지 | 발신자 "알 수 없음" 표시 (백엔드 처리) |
| TC-12 | 최근 메시지 시간 포맷 | formatChatRoomTime 결과 확인 |

### 11.3 엣지 케이스

| ID | 시나리오 | 기대 결과 |
|----|---------|----------|
| TC-13 | 채팅방 100개 이상 존재 | 최대 100개만 표시 |
| TC-14 | 채팅방 이름이 매우 긴 경우 | 카드 내에서 truncate 처리 |
| TC-15 | 로딩 중 페이지 이탈 | React Query 자동 정리 |
| TC-16 | 비로그인 상태에서 접근 | layout에서 로그인 페이지로 리다이렉트 |

---

## 12. 성능 목표

- **초기 로딩 시간**: 1.5초 이하 (First Contentful Paint)
- **API 응답 시간**: 평균 500ms 이하
- **페이지 전환 시간**: 300ms 이하 (Next.js 클라이언트 라우팅)
- **TTI (Time to Interactive)**: 2초 이하

---

## 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0  | 2025-10-20 | Claude Code | 초기 작성 |

---

## 부록

### A. 참고 문서
- PRD: `/docs/prd.md` (섹션 3.2, 5.1, 6.2)
- Userflow: `/docs/userflow.md` (섹션 2.1)
- Database: `/docs/database.md` (섹션 3.2, 6.1)
- Common Modules: `/docs/common-modules.md`
- UC-005: `/docs/usecases/5-list-chat-rooms/spec.md`
- UC-006: `/docs/usecases/6-create-chat-room/spec.md`

### B. 코드베이스 구조 참고
- 기존 example feature: `/src/features/example/*`
- 인증 보호: `/src/app/(protected)/layout.tsx`
- API 클라이언트: `/src/lib/remote/api-client.ts`

### C. Supabase RPC 함수 (성능 최적화)

채팅방 목록 조회 성능을 위해 다음 RPC 함수를 Supabase에 생성할 수 있습니다:

```sql
-- supabase/migrations/0005_create_get_chat_rooms_with_last_message.sql
CREATE OR REPLACE FUNCTION get_chat_rooms_with_last_message()
RETURNS TABLE (
  id uuid,
  name varchar,
  created_at timestamptz,
  last_message_content text,
  last_message_type message_type_enum,
  last_message_emoticon_id varchar,
  last_message_time timestamptz,
  last_message_sender varchar
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    cr.id,
    cr.name,
    cr.created_at,
    m.content AS last_message_content,
    m.message_type AS last_message_type,
    m.emoticon_id AS last_message_emoticon_id,
    m.created_at AS last_message_time,
    up.nickname AS last_message_sender
  FROM chat_rooms cr
  LEFT JOIN LATERAL (
    SELECT * FROM messages
    WHERE chat_room_id = cr.id
    ORDER BY created_at DESC
    LIMIT 1
  ) m ON true
  LEFT JOIN user_profiles up ON m.sender_id = up.id
  ORDER BY COALESCE(m.created_at, cr.created_at) DESC
  LIMIT 100;
$$;
```

**사용 시 service.ts 간소화**:
```typescript
export async function listChatRooms(supabase: SupabaseClient): Promise<ChatRoom[]> {
  const { data, error } = await supabase.rpc('get_chat_rooms_with_last_message');

  if (error) throw new Error(`Failed to fetch chat rooms: ${error.message}`);

  return (data || []) as ChatRoom[];
}
```

---

**문서 종료**
