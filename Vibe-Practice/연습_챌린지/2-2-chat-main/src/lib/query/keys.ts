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
