export const LikeErrorCode = {
  MESSAGE_NOT_FOUND: 'MESSAGE_NOT_FOUND',
  LIKE_OWN_MESSAGE: 'LIKE_OWN_MESSAGE',
  ALREADY_LIKED: 'ALREADY_LIKED',
  NOT_LIKED: 'NOT_LIKED',
} as const;

export type LikeErrorCode =
  (typeof LikeErrorCode)[keyof typeof LikeErrorCode];

export const likeErrorMessages: Record<LikeErrorCode, string> = {
  MESSAGE_NOT_FOUND: '메시지를 찾을 수 없습니다.',
  LIKE_OWN_MESSAGE: '본인 메시지에는 좋아요를 할 수 없습니다.',
  ALREADY_LIKED: '이미 좋아요한 메시지입니다.',
  NOT_LIKED: '좋아요하지 않은 메시지입니다.',
};
