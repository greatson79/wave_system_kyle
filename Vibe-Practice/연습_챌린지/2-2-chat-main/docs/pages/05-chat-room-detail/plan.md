# 채팅방 상세 페이지 - 구현 계획

## 문서 개요

본 문서는 채팅방 상세 페이지(`/chat-rooms/:id`)의 상세 구현 계획을 정의합니다. 기존 작성된 상태 관리 설계 문서(`state.md`)와 일관성을 유지하며, 모든 기능을 단계별로 구현할 수 있도록 구체적인 가이드를 제공합니다.

---

## 1. 페이지 개요

### 1.1 페이지 정보

- **경로**: `/app/(protected)/chat-rooms/[id]/page.tsx`
- **레이아웃**: 카카오톡 스타일 채팅 인터페이스
- **인증**: 로그인 필수 (protected 레이아웃 적용)
- **주요 기능**:
  - 메시지 목록 조회 (무한 스크롤)
  - 텍스트/이모티콘 메시지 전송
  - 메시지 답장
  - 메시지 좋아요/좋아요 취소
  - 메시지 삭제 (단일/일괄)

### 1.2 참조 문서

- **상태 관리 설계**: `/docs/pages/02-chat-room-detail/state.md` (필수 참조)
- **PRD**: `/docs/prd.md` - 3.2, 6.3, 6.4
- **Userflow**: `/docs/userflow.md` - 3.2 ~ 3.8
- **Database**: `/docs/database.md` - messages, message_likes 테이블
- **공통 모듈**: `/docs/common-modules.md`
- **관련 유스케이스**:
  - UC-007: 채팅방 상세 조회
  - UC-008: 메시지 목록 조회
  - UC-009: 텍스트 메시지 전송
  - UC-010: 이모티콘 메시지 전송
  - UC-011: 메시지 답장
  - UC-012: 메시지 좋아요/좋아요 취소
  - UC-013: 메시지 삭제

---

## 2. 파일 구조

```
src/
├── app/(protected)/chat-rooms/[id]/
│   └── page.tsx                          # 메인 페이지 컴포넌트
│
├── features/chat-rooms/
│   ├── components/
│   │   ├── chat-room-header.tsx          # 헤더 (뒤로가기, 채팅방 이름)
│   │   ├── message-list.tsx              # 메시지 목록 컨테이너
│   │   ├── message-item.tsx              # 개별 메시지 아이템
│   │   ├── message-input.tsx             # 텍스트 입력창
│   │   ├── reply-target-preview.tsx      # 답장 대상 미리보기
│   │   ├── delete-mode-footer.tsx        # 삭제 모드 하단 버튼
│   │   └── emoticon-picker.tsx           # 이모티콘 선택 팝업
│   │
│   ├── context/
│   │   └── chat-room-context.tsx         # Context + useReducer 상태 관리
│   │
│   ├── hooks/
│   │   ├── useChatRoom.ts                # 채팅방 정보 조회 Query
│   │   ├── useMessages.ts                # 메시지 목록 조회 InfiniteQuery
│   │   ├── useSendMessage.ts             # 메시지 전송 Mutation
│   │   ├── useToggleLike.ts              # 좋아요 토글 Mutation
│   │   └── useDeleteMessages.ts          # 메시지 일괄 삭제 Mutation
│   │
│   ├── backend/
│   │   ├── route.ts                      # Hono 라우터 등록
│   │   ├── service.ts                    # 비즈니스 로직
│   │   ├── schema.ts                     # Zod 스키마 정의
│   │   └── error.ts                      # 에러 코드 정의
│   │
│   └── types.ts                          # 타입 정의
│
└── constants/
    └── emoticons.ts                      # 이모티콘 목록 상수
```

---

## 3. 컴포넌트 계층 구조

```
ChatRoomPage
└── ChatRoomProvider (Context)
    ├── ChatRoomHeader
    │   ├── 뒤로가기 버튼
    │   └── 채팅방 이름
    │
    ├── MessageList
    │   ├── InfiniteScroll (무한 스크롤 컨테이너)
    │   └── MessageItem[] (개별 메시지)
    │       ├── 발신자 닉네임 (남의 메시지만)
    │       ├── 메시지 내용 (텍스트 또는 이모티콘)
    │       ├── ReplyTargetPreview (답장 정보)
    │       ├── LikeDisplay (하트 + 개수)
    │       ├── 메시지 시간
    │       ├── 메시지 메뉴 버튼
    │       └── 체크박스 (삭제 모드 시)
    │
    ├── MessageInput (조건부: 일반 모드)
    │   ├── ReplyTargetPreview (조건부: 답장 대상 있을 때)
    │   ├── TextInput
    │   ├── EmoticonButton
    │   └── SendButton
    │
    ├── DeleteModeFooter (조건부: 삭제 모드)
    │   ├── CancelButton
    │   └── BatchDeleteButton
    │
    └── EmoticonPicker (조건부: emoticonPickerOpen)
        ├── 이모티콘 그리드
        └── 닫기 버튼
```

---

## 4. 상태 관리 설계

> **중요**: 본 섹션은 `/docs/pages/02-chat-room-detail/state.md`를 기반으로 작성되었습니다. 상세한 내용은 해당 문서를 참조하세요.

### 4.1 서버 상태 (React Query)

#### 4.1.1 채팅방 정보 조회

**파일**: `src/features/chat-rooms/hooks/useChatRoom.ts`

```typescript
export const useChatRoom = (roomId: string) => {
  return useQuery({
    queryKey: queryKeys.chatRooms.detail(roomId),
    queryFn: () => apiClient.get(`/api/chat-rooms/${roomId}`),
    staleTime: 1000 * 60 * 5, // 5분
    gcTime: 1000 * 60 * 10, // 10분
    retry: 1,
  });
};
```

**응답 스키마**:
```typescript
{
  success: true,
  data: {
    id: string;
    name: string;
    created_at: string;
  }
}
```

**에러 처리**:
- 404: 홈으로 리다이렉트, "채팅방을 찾을 수 없습니다" 토스트
- 401: 로그인 페이지로 리다이렉트

---

#### 4.1.2 메시지 목록 조회 (무한 스크롤)

**파일**: `src/features/messages/hooks/useMessages.ts`

```typescript
export const useMessages = (roomId: string) => {
  return useInfiniteQuery({
    queryKey: queryKeys.messages.list(roomId),
    queryFn: ({ pageParam = 0 }) =>
      apiClient.get(`/api/chat-rooms/${roomId}/messages`, {
        params: { limit: 50, offset: pageParam }
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const totalFetched = allPages.length * 50;
      return lastPage.data.messages.length === 50 ? totalFetched : undefined;
    },
    staleTime: 1000 * 60, // 1분
    gcTime: 1000 * 60 * 5, // 5분
    select: (data) => ({
      pages: data.pages,
      pageParams: data.pageParams,
      messages: data.pages.flatMap((page) => page.data.messages),
    }),
  });
};
```

**Message 타입** (공통 모듈에서 재사용):
```typescript
type Message = {
  id: string;
  chat_room_id: string;
  sender_id: string;
  sender_nickname: string;
  message_type: 'text' | 'emoticon';
  content: string | null;
  emoticon_id: string | null;
  created_at: string;
  reply_to?: {
    message_id: string;
    sender_nickname: string;
    message_type: 'text' | 'emoticon';
    content: string | null;
    emoticon_id: string | null;
  };
  like_count: number;
  is_liked_by_me: boolean;
};
```

---

#### 4.1.3 메시지 전송 Mutation (Optimistic Update)

**파일**: `src/features/messages/hooks/useSendMessage.ts`

```typescript
export const useSendMessage = (roomId: string) => {
  const queryClient = useQueryClient();
  const { dispatch } = useChatRoomContext(); // Context에서 가져옴

  return useMutation({
    mutationFn: (data: SendMessageRequest) =>
      apiClient.post(`/api/chat-rooms/${roomId}/messages`, data),

    // Optimistic Update
    onMutate: async (newMessage) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      // 낙관적 업데이트: 임시 메시지 추가
      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => {
          const optimisticMessage: Message = {
            id: `temp-${Date.now()}`,
            chat_room_id: roomId,
            sender_id: 'current-user-id', // useUser에서 가져옴
            sender_nickname: 'current-user-nickname',
            message_type: newMessage.message_type,
            content: newMessage.content || null,
            emoticon_id: newMessage.emoticon_id || null,
            reply_to: undefined, // 서버 응답 후 업데이트
            like_count: 0,
            is_liked_by_me: false,
            created_at: new Date().toISOString(),
          };

          return {
            ...old,
            pages: old.pages.map((page: any, index: number) =>
              index === 0
                ? { ...page, data: { messages: [...page.data.messages, optimisticMessage] } }
                : page
            ),
          };
        }
      );

      return { previousMessages };
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.messages.list(roomId),
      });
      // 전송 후 상태 초기화
      dispatch({ type: 'RESET_AFTER_SEND' });
    },

    onError: (error, variables, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(
          queryKeys.messages.list(roomId),
          context.previousMessages
        );
      }
    },
  });
};
```

**요청 스키마**:
```typescript
type SendMessageRequest =
  | { message_type: 'text'; content: string; reply_to_message_id?: string }
  | { message_type: 'emoticon'; emoticon_id: string; reply_to_message_id?: string };
```

---

#### 4.1.4 좋아요 토글 Mutation (Optimistic Update)

**파일**: `src/features/messages/hooks/useToggleLike.ts`

```typescript
export const useToggleLike = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId, isLiked }: { messageId: string; isLiked: boolean }) => {
      if (isLiked) {
        return apiClient.delete(`/api/messages/${messageId}/likes`);
      } else {
        return apiClient.post(`/api/messages/${messageId}/likes`);
      }
    },

    onMutate: async ({ messageId, isLiked }) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      // 낙관적 업데이트
      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => ({
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            data: {
              messages: page.data.messages.map((msg: Message) =>
                msg.id === messageId
                  ? {
                      ...msg,
                      like_count: isLiked ? msg.like_count - 1 : msg.like_count + 1,
                      is_liked_by_me: !isLiked,
                    }
                  : msg
              ),
            },
          })),
        })
      );

      return { previousMessages };
    },

    onError: (error, variables, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(
          queryKeys.messages.list(roomId),
          context.previousMessages
        );
      }
    },
  });
};
```

---

#### 4.1.5 메시지 일괄 삭제 Mutation (Optimistic Update)

**파일**: `src/features/messages/hooks/useDeleteMessages.ts`

```typescript
export const useDeleteMessages = (roomId: string) => {
  const queryClient = useQueryClient();
  const { dispatch } = useChatRoomContext();

  return useMutation({
    mutationFn: (messageIds: string[]) =>
      apiClient.delete('/api/messages/batch', {
        data: { message_ids: messageIds }
      }),

    onMutate: async (messageIds) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.messages.list(roomId),
      });

      const previousMessages = queryClient.getQueryData(
        queryKeys.messages.list(roomId)
      );

      // 낙관적 업데이트: 메시지 제거
      queryClient.setQueryData(
        queryKeys.messages.list(roomId),
        (old: any) => ({
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            data: {
              messages: page.data.messages.filter(
                (msg: Message) => !messageIds.includes(msg.id)
              ),
            },
          })),
        })
      );

      return { previousMessages };
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.messages.list(roomId),
      });
      // 삭제 모드 종료
      dispatch({ type: 'EXIT_DELETE_MODE' });
    },

    onError: (error, variables, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(
          queryKeys.messages.list(roomId),
          context.previousMessages
        );
      }
    },
  });
};
```

---

### 4.2 클라이언트 상태 (Context + useReducer)

> **참조**: `/docs/pages/02-chat-room-detail/state.md` 섹션 4

**파일**: `src/features/chat-rooms/context/chat-room-context.tsx`

#### 4.2.1 State 구조

```typescript
type ChatRoomState = {
  replyTarget: Message | null;
  deleteMode: {
    isActive: boolean;
    selectedMessageIds: string[];
  };
  emoticonPickerOpen: boolean;
};

const initialState: ChatRoomState = {
  replyTarget: null,
  deleteMode: {
    isActive: false,
    selectedMessageIds: [],
  },
  emoticonPickerOpen: false,
};
```

#### 4.2.2 Actions

```typescript
type ChatRoomAction =
  | { type: 'SET_REPLY_TARGET'; payload: Message | null }
  | { type: 'ENTER_DELETE_MODE'; payload: string }
  | { type: 'EXIT_DELETE_MODE' }
  | { type: 'TOGGLE_MESSAGE_SELECTION'; payload: string }
  | { type: 'TOGGLE_EMOTICON_PICKER' }
  | { type: 'RESET_AFTER_SEND' };
```

#### 4.2.3 Reducer

```typescript
function chatRoomReducer(
  state: ChatRoomState,
  action: ChatRoomAction
): ChatRoomState {
  switch (action.type) {
    case 'SET_REPLY_TARGET':
      return {
        ...state,
        replyTarget: action.payload,
      };

    case 'ENTER_DELETE_MODE':
      return {
        ...state,
        deleteMode: {
          isActive: true,
          selectedMessageIds: [action.payload],
        },
        replyTarget: null,
        emoticonPickerOpen: false,
      };

    case 'EXIT_DELETE_MODE':
      return {
        ...state,
        deleteMode: {
          isActive: false,
          selectedMessageIds: [],
        },
      };

    case 'TOGGLE_MESSAGE_SELECTION': {
      const { selectedMessageIds } = state.deleteMode;
      const messageId = action.payload;

      return {
        ...state,
        deleteMode: {
          ...state.deleteMode,
          selectedMessageIds: selectedMessageIds.includes(messageId)
            ? selectedMessageIds.filter((id) => id !== messageId)
            : [...selectedMessageIds, messageId],
        },
      };
    }

    case 'TOGGLE_EMOTICON_PICKER':
      return {
        ...state,
        emoticonPickerOpen: !state.emoticonPickerOpen,
      };

    case 'RESET_AFTER_SEND':
      return {
        ...state,
        replyTarget: null,
        emoticonPickerOpen: false,
      };

    default:
      return state;
  }
}
```

#### 4.2.4 Context Provider

```typescript
type ChatRoomContextValue = {
  state: ChatRoomState;
  dispatch: React.Dispatch<ChatRoomAction>;
  selectedMessageCount: number;
  canDelete: boolean;
};

const ChatRoomContext = createContext<ChatRoomContextValue | undefined>(undefined);

export const ChatRoomProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatRoomReducer, initialState);

  const selectedMessageCount = state.deleteMode.selectedMessageIds.length;
  const canDelete = selectedMessageCount > 0;

  const value: ChatRoomContextValue = {
    state,
    dispatch,
    selectedMessageCount,
    canDelete,
  };

  return (
    <ChatRoomContext.Provider value={value}>
      {children}
    </ChatRoomContext.Provider>
  );
};

export const useChatRoomContext = () => {
  const context = useContext(ChatRoomContext);
  if (!context) {
    throw new Error('useChatRoomContext must be used within ChatRoomProvider');
  }
  return context;
};
```

---

### 4.3 폼 상태 (React Hook Form)

**파일**: `src/features/messages/components/message-input.tsx`

```typescript
const textMessageSchema = z.object({
  content: z.string()
    .min(1, '메시지를 입력해주세요')
    .max(1000, '메시지는 최대 1000자까지 입력할 수 있습니다')
    .trim(),
});

type TextMessageFormData = z.infer<typeof textMessageSchema>;

export const MessageInput: React.FC = () => {
  const { state, dispatch } = useChatRoomContext();
  const sendMessage = useSendMessage(roomId);

  const form = useForm<TextMessageFormData>({
    resolver: zodResolver(textMessageSchema),
    defaultValues: { content: '' },
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      await sendMessage.mutateAsync({
        message_type: 'text',
        content: data.content,
        reply_to_message_id: state.replyTarget?.id,
      });

      form.reset();
      // RESET_AFTER_SEND는 mutation onSuccess에서 호출됨
    } catch (error) {
      console.error('메시지 전송 실패:', error);
    }
  });

  // ...
};
```

---

## 5. API 연동

### 5.1 Backend 라우터 등록

**파일**: `src/features/chat-rooms/backend/route.ts`

```typescript
import { Hono } from 'hono';
import { requireAuth } from '@/backend/middleware/auth';
import * as service from './service';
import * as schema from './schema';

export function registerChatRoomRoutes(app: Hono) {
  // 채팅방 정보 조회
  app.get('/api/chat-rooms/:id', requireAuth(), async (c) => {
    const roomId = c.req.param('id');
    const result = await service.getChatRoom(c, roomId);
    return c.json(result);
  });

  // 메시지 목록 조회
  app.get('/api/chat-rooms/:roomId/messages', requireAuth(), async (c) => {
    const roomId = c.req.param('roomId');
    const limit = parseInt(c.req.query('limit') || '50');
    const offset = parseInt(c.req.query('offset') || '0');

    const result = await service.getMessages(c, roomId, limit, offset);
    return c.json(result);
  });

  // 메시지 전송
  app.post('/api/chat-rooms/:roomId/messages', requireAuth(), async (c) => {
    const roomId = c.req.param('roomId');
    const body = await c.req.json();
    const validated = schema.SendMessageRequestSchema.parse(body);

    const result = await service.sendMessage(c, roomId, validated);
    return c.json(result, 201);
  });

  // 좋아요 추가
  app.post('/api/messages/:messageId/likes', requireAuth(), async (c) => {
    const messageId = c.req.param('messageId');
    const result = await service.addLike(c, messageId);
    return c.json(result, 201);
  });

  // 좋아요 취소
  app.delete('/api/messages/:messageId/likes', requireAuth(), async (c) => {
    const messageId = c.req.param('messageId');
    const result = await service.removeLike(c, messageId);
    return c.json(result);
  });

  // 메시지 일괄 삭제
  app.delete('/api/messages/batch', requireAuth(), async (c) => {
    const body = await c.req.json();
    const validated = schema.BatchDeleteMessagesSchema.parse(body);

    const result = await service.deleteMessages(c, validated.message_ids);
    return c.json(result);
  });
}
```

---

### 5.2 Backend 서비스 로직 (예시)

**파일**: `src/features/chat-rooms/backend/service.ts`

```typescript
import type { Context } from 'hono';
import type { AppEnv } from '@/backend/hono/context';

// 채팅방 정보 조회
export async function getChatRoom(c: Context<AppEnv>, roomId: string) {
  const supabase = c.get('supabase');

  const { data, error } = await supabase
    .from('chat_rooms')
    .select('id, name, created_at')
    .eq('id', roomId)
    .single();

  if (error || !data) {
    return { success: false, error: { code: 'CHAT_ROOM_NOT_FOUND', message: '채팅방을 찾을 수 없습니다.' } };
  }

  return { success: true, data };
}

// 메시지 목록 조회
export async function getMessages(c: Context<AppEnv>, roomId: string, limit: number, offset: number) {
  const supabase = c.get('supabase');
  const userId = c.get('userId'); // requireAuth에서 주입됨

  // 메시지 + 발신자 + 답장 정보 + 좋아요 정보 JOIN
  const { data, error } = await supabase
    .from('messages')
    .select(`
      id,
      chat_room_id,
      sender_id,
      sender:user_profiles!sender_id(nickname),
      message_type,
      content,
      emoticon_id,
      created_at,
      reply_to:messages!reply_to_message_id(
        id,
        sender:user_profiles!sender_id(nickname),
        message_type,
        content,
        emoticon_id
      ),
      likes:message_likes(user_id)
    `)
    .eq('chat_room_id', roomId)
    .order('created_at', { ascending: true })
    .range(offset, offset + limit - 1);

  if (error) {
    return { success: false, error: { code: 'INTERNAL_ERROR', message: '메시지 조회 실패' } };
  }

  // 데이터 변환 (좋아요 개수 및 내 좋아요 여부 계산)
  const messages = data.map((msg: any) => ({
    id: msg.id,
    chat_room_id: msg.chat_room_id,
    sender_id: msg.sender_id,
    sender_nickname: msg.sender?.nickname || '알 수 없음',
    message_type: msg.message_type,
    content: msg.content,
    emoticon_id: msg.emoticon_id,
    created_at: msg.created_at,
    reply_to: msg.reply_to ? {
      message_id: msg.reply_to.id,
      sender_nickname: msg.reply_to.sender?.nickname || '알 수 없음',
      message_type: msg.reply_to.message_type,
      content: msg.reply_to.content,
      emoticon_id: msg.reply_to.emoticon_id,
    } : undefined,
    like_count: msg.likes?.length || 0,
    is_liked_by_me: msg.likes?.some((like: any) => like.user_id === userId) || false,
  }));

  return { success: true, data: { messages } };
}

// 메시지 전송
export async function sendMessage(c: Context<AppEnv>, roomId: string, data: any) {
  const supabase = c.get('supabase');
  const userId = c.get('userId');

  // 채팅방 존재 확인
  const { data: room } = await supabase
    .from('chat_rooms')
    .select('id')
    .eq('id', roomId)
    .single();

  if (!room) {
    return { success: false, error: { code: 'CHAT_ROOM_NOT_FOUND', message: '채팅방을 찾을 수 없습니다.' } };
  }

  // 답장 대상 메시지 확인 (선택)
  if (data.reply_to_message_id) {
    const { data: replyMsg } = await supabase
      .from('messages')
      .select('id')
      .eq('id', data.reply_to_message_id)
      .single();

    if (!replyMsg) {
      // 답장 대상 없으면 null로 처리 (일반 메시지로 저장)
      data.reply_to_message_id = null;
    }
  }

  // 메시지 삽입
  const { data: newMessage, error } = await supabase
    .from('messages')
    .insert({
      chat_room_id: roomId,
      sender_id: userId,
      message_type: data.message_type,
      content: data.content || null,
      emoticon_id: data.emoticon_id || null,
      reply_to_message_id: data.reply_to_message_id || null,
    })
    .select()
    .single();

  if (error) {
    return { success: false, error: { code: 'MESSAGE_SEND_FAILED', message: '메시지 전송에 실패했습니다.' } };
  }

  return { success: true, data: newMessage };
}

// 좋아요 추가
export async function addLike(c: Context<AppEnv>, messageId: string) {
  const supabase = c.get('supabase');
  const userId = c.get('userId');

  // 메시지 존재 및 본인 메시지 여부 확인
  const { data: message } = await supabase
    .from('messages')
    .select('sender_id')
    .eq('id', messageId)
    .single();

  if (!message) {
    return { success: false, error: { code: 'MESSAGE_NOT_FOUND', message: '메시지를 찾을 수 없습니다.' } };
  }

  if (message.sender_id === userId) {
    return { success: false, error: { code: 'LIKE_OWN_MESSAGE', message: '본인 메시지에는 좋아요를 할 수 없습니다.' } };
  }

  // 좋아요 삽입 (중복 시 UNIQUE 제약으로 에러 발생)
  const { error } = await supabase
    .from('message_likes')
    .insert({ message_id: messageId, user_id: userId });

  if (error) {
    // 중복 좋아요 시 멱등성 처리
    if (error.code === '23505') {
      return { success: true };
    }
    return { success: false, error: { code: 'LIKE_FAILED', message: '좋아요 추가에 실패했습니다.' } };
  }

  return { success: true };
}

// 좋아요 취소
export async function removeLike(c: Context<AppEnv>, messageId: string) {
  const supabase = c.get('supabase');
  const userId = c.get('userId');

  const { error } = await supabase
    .from('message_likes')
    .delete()
    .eq('message_id', messageId)
    .eq('user_id', userId);

  if (error) {
    return { success: false, error: { code: 'UNLIKE_FAILED', message: '좋아요 취소에 실패했습니다.' } };
  }

  return { success: true };
}

// 메시지 일괄 삭제
export async function deleteMessages(c: Context<AppEnv>, messageIds: string[]) {
  const supabase = c.get('supabase');
  const userId = c.get('userId');

  if (messageIds.length === 0) {
    return { success: false, error: { code: 'NO_MESSAGES_SELECTED', message: '삭제할 메시지를 선택해주세요.' } };
  }

  // 본인 메시지만 삭제
  const { data, error } = await supabase
    .from('messages')
    .delete()
    .in('id', messageIds)
    .eq('sender_id', userId)
    .select();

  if (error) {
    return { success: false, error: { code: 'DELETE_FAILED', message: '메시지 삭제에 실패했습니다.' } };
  }

  return { success: true, data: { deleted_count: data?.length || 0 } };
}
```

---

### 5.3 Zod 스키마 정의

**파일**: `src/features/chat-rooms/backend/schema.ts`

```typescript
import { z } from 'zod';

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

---

## 6. UI/UX 상세

### 6.1 레이아웃 구조

```
┌─────────────────────────────────────┐
│ ChatRoomHeader                      │
│ [←] 채팅방 이름                      │
├─────────────────────────────────────┤
│                                     │
│ MessageList (무한 스크롤)            │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ 남의 메시지 (좌측 정렬)       │   │
│ │ 닉네임                        │   │
│ │ [답장 대상: ...] (조건부)      │   │
│ │ 메시지 내용                   │   │
│ │ ❤️ 3  오후 3:24              │   │
│ └─────────────────────────────┘   │
│                                     │
│         ┌─────────────────────┐    │
│         │ 내 메시지 (우측 정렬) │    │
│         │ 메시지 내용          │    │
│         │ 오후 3:25           │    │
│         └─────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│ MessageInput (일반 모드)             │
│ [답장 대상: ...] [X] (조건부)        │
│ [😊] [텍스트 입력창] [전송]          │
└─────────────────────────────────────┘
```

---

### 6.2 메시지 아이템 디자인 (카카오톡 스타일)

#### 6.2.1 남의 메시지

```
┌─────────────────────────────────────┐
│ 사용자1                              │
│ ┌───────────────────────────┐      │
│ │ [답장: 사용자2 > 안녕하세요] │      │ (조건부)
│ │ 네, 반갑습니다!             │      │
│ └───────────────────────────┘      │
│ ❤️ 2  오후 3:24              [⋮]  │
└─────────────────────────────────────┘
```

#### 6.2.2 내 메시지

```
┌─────────────────────────────────────┐
│                      ┌─────────────┐│
│                      │ 안녕하세요!  ││
│                      └─────────────┘│
│                 [⋮]  오후 3:23      │
└─────────────────────────────────────┘
```

#### 6.2.3 이모티콘 메시지

```
┌─────────────────────────────────────┐
│ 사용자1                              │
│      😊                             │
│ (큰 이모티콘 2~3배 크기)              │
│ ❤️ 1  오후 3:26              [⋮]  │
└─────────────────────────────────────┘
```

---

### 6.3 삭제 모드 UI

```
┌─────────────────────────────────────┐
│ ChatRoomHeader                      │
│ [←] 채팅방 이름                      │
├─────────────────────────────────────┤
│                                     │
│ MessageList (삭제 모드)              │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ 남의 메시지 (변화 없음)       │   │
│ └─────────────────────────────┘   │
│                                     │
│ ☑️ ┌─────────────────────────┐    │ (파란색 체크)
│    │ 내 메시지 1 (선택됨)      │    │
│    └─────────────────────────┘    │
│                                     │
│ ☐ ┌─────────────────────────┐    │ (회색 체크)
│    │ 내 메시지 2 (선택 안 됨)  │    │
│    └─────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│ DeleteModeFooter                    │
│ [취소]              [일괄삭제(2개)] │
└─────────────────────────────────────┘
```

---

### 6.4 이모티콘 선택 팝업

```
┌───────────────────────────────┐
│ 이모티콘 선택           [X]   │
├───────────────────────────────┤
│                               │
│ 😊  ❤️  👍  😂               │
│ 😢  😠  😲  🤔               │
│ (4~6열 그리드)                │
│                               │
└───────────────────────────────┘
```

**동작**:
- 이모티콘 클릭 시 즉시 전송 (별도 전송 버튼 없음)
- 팝업 외부 클릭 시 닫기
- 답장 대상 설정된 경우 답장 정보 포함하여 전송

---

## 7. 에러 처리

### 7.1 에러 타입별 처리

| 에러 타입 | HTTP 상태 | 처리 방법 |
|-----------|-----------|-----------|
| 인증 실패 | 401 | 로그인 페이지로 리다이렉트 (`/login?redirectedFrom=/chat-rooms/:id`) |
| 채팅방 없음 | 404 | 홈 페이지로 리다이렉트, 에러 토스트 표시 ("채팅방을 찾을 수 없습니다") |
| 메시지 전송 실패 | 400 | 에러 메시지 표시, 입력값 유지, 재시도 가능 |
| 네트워크 오류 | - | 에러 토스트 표시, 재시도 버튼 제공 |
| 서버 오류 | 500 | 에러 토스트 표시, 재시도 버튼 제공 |

### 7.2 로딩 상태 표시

| 상태 | UI 표시 |
|------|---------|
| 채팅방 정보 로딩 | 헤더 스켈레톤 UI |
| 메시지 목록 로딩 | 메시지 목록 스켈레톤 UI (말풍선 모양) |
| 무한 스크롤 로딩 | 목록 상단에 작은 로딩 인디케이터 |
| 메시지 전송 중 | 전송 버튼 비활성화, 로딩 스피너 표시 |
| 메시지 삭제 중 | 일괄삭제 버튼 비활성화, 로딩 스피너 표시 |
| 좋아요 토글 중 | 낙관적 업데이트로 즉시 UI 변경 (로딩 없음) |

### 7.3 에러 복구 전략

| 에러 상황 | 복구 방법 |
|-----------|-----------|
| 메시지 전송 실패 | Rollback → 임시 메시지 제거, 입력값 유지, 재시도 가능 |
| 메시지 삭제 실패 | Rollback → 삭제된 메시지 복원, 삭제 모드 유지, 재시도 가능 |
| 좋아요 토글 실패 | Rollback → 좋아요 상태 복원, 에러 토스트 표시 |
| 채팅방 정보 로딩 실패 | 에러 메시지 표시, 재시도 버튼 제공 |
| 메시지 목록 로딩 실패 | 에러 메시지 표시, 재시도 버튼 제공 |

---

## 8. 구현 순서

### Phase 1: 기본 구조 및 조회 (우선순위 높음)

**목표**: 채팅방 진입 및 메시지 목록 조회

#### 1.1 Backend 기본 구조
- [ ] `src/features/chat-rooms/backend/route.ts` 생성
- [ ] `src/features/chat-rooms/backend/service.ts` 생성
- [ ] `src/features/chat-rooms/backend/schema.ts` 생성
- [ ] `src/features/chat-rooms/backend/error.ts` 생성
- [ ] `src/backend/hono/app.ts`에 `registerChatRoomRoutes` 등록

#### 1.2 채팅방 정보 조회 API
- [ ] `GET /api/chat-rooms/:id` 라우터 구현
- [ ] `getChatRoom` 서비스 로직 구현
- [ ] 에러 처리 (404 Not Found)

#### 1.3 메시지 목록 조회 API
- [ ] `GET /api/chat-rooms/:roomId/messages` 라우터 구현
- [ ] `getMessages` 서비스 로직 구현 (JOIN 쿼리)
- [ ] 페이지네이션 구현 (limit, offset)
- [ ] 답장 정보 및 좋아요 정보 포함

#### 1.4 Frontend 기본 구조
- [ ] `src/features/chat-rooms/types.ts` 생성 (Message, ChatRoom 타입)
- [ ] `src/lib/query/keys.ts`에 쿼리 키 추가
- [ ] `src/features/chat-rooms/hooks/useChatRoom.ts` 구현
- [ ] `src/features/chat-rooms/hooks/useMessages.ts` 구현 (InfiniteQuery)

#### 1.5 페이지 및 컴포넌트
- [ ] `src/app/(protected)/chat-rooms/[id]/page.tsx` 생성
- [ ] `src/features/chat-rooms/components/chat-room-header.tsx` 구현
- [ ] `src/features/chat-rooms/components/message-list.tsx` 구현
- [ ] `src/features/chat-rooms/components/message-item.tsx` 구현 (기본 표시)

#### 1.6 테스트
- [ ] 채팅방 진입 시 헤더 표시 확인
- [ ] 메시지 목록 조회 및 렌더링 확인
- [ ] 무한 스크롤 동작 확인
- [ ] 에러 처리 확인 (404, 401)

---

### Phase 2: 메시지 전송 (텍스트/이모티콘)

**목표**: 메시지 전송 기능 구현

#### 2.1 Backend API
- [ ] `POST /api/chat-rooms/:roomId/messages` 라우터 구현
- [ ] `sendMessage` 서비스 로직 구현
- [ ] Zod 스키마 검증 (SendMessageRequestSchema)
- [ ] 답장 대상 메시지 확인 로직

#### 2.2 이모티콘 상수
- [ ] `src/constants/emoticons.ts` 생성
- [ ] 이모티콘 목록 정의 (id, label, name)
- [ ] `getEmoticonById`, `isValidEmoticonId` 유틸 함수

#### 2.3 Context 및 상태 관리
- [ ] `src/features/chat-rooms/context/chat-room-context.tsx` 생성
- [ ] State, Actions, Reducer 구현
- [ ] ChatRoomProvider 구현
- [ ] useChatRoomContext 훅 구현

#### 2.4 Frontend Hooks
- [ ] `src/features/messages/hooks/useSendMessage.ts` 구현 (Optimistic Update)

#### 2.5 컴포넌트
- [ ] `src/features/messages/components/message-input.tsx` 구현 (텍스트)
- [ ] `src/features/messages/components/emoticon-picker.tsx` 구현
- [ ] `src/app/(protected)/chat-rooms/[id]/page.tsx`에 Context Provider 추가

#### 2.6 테스트
- [ ] 텍스트 메시지 전송 확인
- [ ] 이모티콘 메시지 전송 확인
- [ ] 전송 후 입력창 초기화 확인
- [ ] Optimistic Update 동작 확인
- [ ] 에러 처리 확인 (입력값 유지, 롤백)

---

### Phase 3: 답장 기능

**목표**: 메시지 답장 기능 구현

#### 3.1 컴포넌트
- [ ] `src/features/messages/components/reply-target-preview.tsx` 구현
- [ ] `message-item.tsx`에 메시지 메뉴 버튼 추가 (남의 메시지)
- [ ] 메시지 메뉴 팝업 구현 (답장, 좋아요)
- [ ] `message-input.tsx`에 답장 미리보기 영역 추가

#### 3.2 상태 관리
- [ ] `SET_REPLY_TARGET` 액션 처리 확인
- [ ] `RESET_AFTER_SEND` 액션 처리 확인

#### 3.3 답장 정보 표시
- [ ] `message-item.tsx`에 답장 정보 렌더링 추가
- [ ] 카카오톡 스타일 답장 UI 구현

#### 3.4 테스트
- [ ] 답장 대상 설정 확인
- [ ] 답장 미리보기 표시 확인
- [ ] 답장 메시지 전송 확인
- [ ] 답장 취소 확인 (X 버튼)
- [ ] 답장 정보 표시 확인 (메시지 목록)

---

### Phase 4: 좋아요 기능

**목표**: 메시지 좋아요/좋아요 취소 구현

#### 4.1 Backend API
- [ ] `POST /api/messages/:messageId/likes` 라우터 구현
- [ ] `DELETE /api/messages/:messageId/likes` 라우터 구현
- [ ] `addLike` 서비스 로직 구현 (본인 메시지 확인, 중복 방지)
- [ ] `removeLike` 서비스 로직 구현

#### 4.2 Frontend Hooks
- [ ] `src/features/messages/hooks/useToggleLike.ts` 구현 (Optimistic Update)

#### 4.3 컴포넌트
- [ ] `message-item.tsx`에 좋아요 표시 영역 추가
- [ ] 하트 아이콘 + 개수 표시
- [ ] 클릭 시 토글 동작 구현
- [ ] 내가 좋아요한 메시지: 핑크색 하트
- [ ] 그 외: 회색 하트

#### 4.4 테스트
- [ ] 좋아요 추가 확인
- [ ] 좋아요 취소 확인
- [ ] 좋아요 개수 표시 확인
- [ ] 하트 아이콘 색상 변경 확인
- [ ] Optimistic Update 동작 확인

---

### Phase 5: 메시지 삭제 기능

**목표**: 메시지 삭제 모드 및 일괄 삭제 구현

#### 5.1 Backend API
- [ ] `DELETE /api/messages/batch` 라우터 구현
- [ ] `deleteMessages` 서비스 로직 구현 (본인 메시지만 삭제)
- [ ] Zod 스키마 검증 (BatchDeleteMessagesSchema)

#### 5.2 Frontend Hooks
- [ ] `src/features/messages/hooks/useDeleteMessages.ts` 구현 (Optimistic Update)

#### 5.3 상태 관리
- [ ] `ENTER_DELETE_MODE` 액션 처리 확인
- [ ] `EXIT_DELETE_MODE` 액션 처리 확인
- [ ] `TOGGLE_MESSAGE_SELECTION` 액션 처리 확인

#### 5.4 컴포넌트
- [ ] `message-item.tsx`에 메시지 메뉴 추가 (내 메시지: 삭제)
- [ ] 삭제 모드 UI 구현 (체크박스)
- [ ] `src/features/messages/components/delete-mode-footer.tsx` 구현
- [ ] 취소 버튼 구현
- [ ] 일괄삭제(N개) 버튼 구현

#### 5.5 테스트
- [ ] 삭제 모드 진입 확인
- [ ] 체크박스 선택/해제 확인
- [ ] 일괄삭제 버튼 활성화/비활성화 확인
- [ ] 메시지 삭제 확인
- [ ] 삭제 모드 종료 확인
- [ ] 취소 기능 확인

---

### Phase 6: 최적화 및 개선

**목표**: 성능 최적화 및 UX 개선

#### 6.1 성능 최적화
- [ ] React.memo로 MessageItem 컴포넌트 최적화
- [ ] 무한 스크롤 Intersection Observer 최적화
- [ ] 이모티콘 이미지 lazy loading
- [ ] useMemo로 derived state 캐싱

#### 6.2 UX 개선
- [ ] 로딩 스켈레톤 UI 추가
- [ ] 에러 메시지 토스트 추가
- [ ] 자동 스크롤 하단 이동 구현
- [ ] 메시지 전송 중 입력창 비활성화
- [ ] 좋아요 애니메이션 추가 (선택 사항)

#### 6.3 접근성 개선
- [ ] 키보드 단축키 (Enter로 전송, Shift+Enter로 줄바꿈)
- [ ] 포커스 관리
- [ ] 스크린 리더 지원

#### 6.4 테스트 및 검증
- [ ] 모든 기능 통합 테스트
- [ ] 에러 상황 테스트 (네트워크 오류, 서버 오류 등)
- [ ] 동시성 테스트 (여러 사용자가 동시에 메시지 전송)
- [ ] 성능 테스트 (메시지 개수 증가 시)

---

## 9. 체크리스트

### 9.1 구현 완료 확인

- [ ] **페이지 진입**: 채팅방 상세 페이지 정상 접근
- [ ] **채팅방 정보**: 헤더에 채팅방 이름 표시
- [ ] **메시지 목록**: 메시지 목록 조회 및 표시
- [ ] **무한 스크롤**: 메시지 50개 단위로 로드
- [ ] **텍스트 메시지 전송**: 텍스트 입력 및 전송
- [ ] **이모티콘 메시지 전송**: 이모티콘 선택 및 전송
- [ ] **답장 기능**: 답장 대상 설정 및 전송
- [ ] **좋아요 기능**: 좋아요 추가/취소
- [ ] **삭제 기능**: 메시지 삭제 모드 및 일괄 삭제
- [ ] **에러 처리**: 모든 에러 상황 대응
- [ ] **로딩 상태**: 로딩 인디케이터 표시

### 9.2 코드 품질 확인

- [ ] **타입 안전성**: TypeScript 타입 정의 완료
- [ ] **상태 관리**: Context + useReducer 패턴 적용
- [ ] **React Query**: 서버 상태 관리 적용
- [ ] **에러 핸들링**: 모든 API 호출에 에러 처리
- [ ] **Optimistic Update**: 메시지 전송, 좋아요, 삭제 적용
- [ ] **DRY 원칙**: 중복 코드 제거
- [ ] **컴포넌트 분리**: 재사용 가능한 컴포넌트 구조

### 9.3 UX 확인

- [ ] **카카오톡 스타일**: 유사한 UI/UX 구현
- [ ] **반응형 디자인**: 모바일 화면 대응
- [ ] **로딩 피드백**: 명확한 로딩 인디케이터
- [ ] **에러 피드백**: 사용자 친화적 에러 메시지
- [ ] **자동 스크롤**: 메시지 전송 후 하단 이동
- [ ] **포커스 관리**: 전송 후 입력창 포커스 유지

---

## 10. 주의 사항

### 10.1 DRY 원칙 준수

- **타입 정의**: 공통 모듈(`common-modules.md`)에서 정의된 타입 재사용
- **유틸 함수**: 날짜 포맷팅, 이모티콘 관리 등 공통 함수 사용
- **에러 코드**: 공통 에러 코드 정의 재사용
- **스키마**: 공통 Zod 스키마 재사용

### 10.2 상태 관리 일관성

- **서버 상태**: React Query로만 관리
- **클라이언트 상태**: Context + useReducer로 관리
- **폼 상태**: React Hook Form으로 관리
- **상태 분리**: 서버/클라이언트/폼 상태 명확히 분리

### 10.3 코드베이스 구조 엄격 준수

- **파일 위치**: 디렉터리 구조 가이드 준수
- **명명 규칙**: 파일명, 컴포넌트명 일관성 유지
- **Client Component**: 모든 컴포넌트에 `"use client"` 추가

### 10.4 백엔드 라우팅

- **API prefix**: 모든 라우트는 `/api` prefix 포함
- **인증 미들웨어**: `requireAuth()` 적용
- **에러 응답**: 공통 응답 포맷 사용 (`src/backend/http/response.ts`)

### 10.5 데이터베이스 무결성

- **외래 키**: 데이터베이스 설계 문서 참조
- **CASCADE**: 메시지 삭제 시 좋아요도 삭제
- **SET NULL**: 답장 대상 삭제 시 NULL 처리

---

## 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0 | 2025-10-20 | Claude Code | 초기 작성 |

---

**문서 종료**
