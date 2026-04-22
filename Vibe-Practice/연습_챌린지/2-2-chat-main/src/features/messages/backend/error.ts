export const MessageErrorCode = {
  INVALID_MESSAGE_CONTENT: 'INVALID_MESSAGE_CONTENT',
  MESSAGE_TOO_LONG: 'MESSAGE_TOO_LONG',
  MESSAGE_NOT_FOUND: 'MESSAGE_NOT_FOUND',
  CHAT_ROOM_NOT_FOUND: 'CHAT_ROOM_NOT_FOUND',
  REPLY_TARGET_NOT_FOUND: 'REPLY_TARGET_NOT_FOUND',
  NO_MESSAGES_SELECTED: 'NO_MESSAGES_SELECTED',
  FORBIDDEN: 'FORBIDDEN',
} as const;

export type MessageErrorCode =
  (typeof MessageErrorCode)[keyof typeof MessageErrorCode];

export const messageErrorMessages: Record<MessageErrorCode, string> = {
  INVALID_MESSAGE_CONTENT: '메시지를 입력해주세요.',
  MESSAGE_TOO_LONG: '메시지는 최대 1000자까지 입력할 수 있습니다.',
  MESSAGE_NOT_FOUND: '메시지를 찾을 수 없습니다.',
  CHAT_ROOM_NOT_FOUND: '채팅방을 찾을 수 없습니다.',
  REPLY_TARGET_NOT_FOUND: '답장 대상 메시지가 삭제되었습니다.',
  NO_MESSAGES_SELECTED: '삭제할 메시지를 선택해주세요.',
  FORBIDDEN: '권한이 없습니다.',
};
