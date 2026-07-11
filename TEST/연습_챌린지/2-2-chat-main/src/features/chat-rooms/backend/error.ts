export const ChatRoomErrorCode = {
  INVALID_NAME: 'CHAT_ROOM_INVALID_NAME',
  NAME_TOO_LONG: 'CHAT_ROOM_NAME_TOO_LONG',
  CREATE_FAILED: 'CHAT_ROOM_CREATE_FAILED',
  NOT_FOUND: 'CHAT_ROOM_NOT_FOUND',
} as const;

export type ChatRoomErrorCode =
  (typeof ChatRoomErrorCode)[keyof typeof ChatRoomErrorCode];

export const chatRoomErrorMessages: Record<ChatRoomErrorCode, string> = {
  CHAT_ROOM_INVALID_NAME: '채팅방 이름을 입력해주세요.',
  CHAT_ROOM_NAME_TOO_LONG: '채팅방 이름은 최대 50자입니다.',
  CHAT_ROOM_CREATE_FAILED: '채팅방 생성에 실패했습니다. 다시 시도해주세요.',
  CHAT_ROOM_NOT_FOUND: '채팅방을 찾을 수 없습니다.',
};
