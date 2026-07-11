export const UserErrorCode = {
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  INVALID_NICKNAME: 'INVALID_NICKNAME',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
} as const;

export type UserErrorCode = (typeof UserErrorCode)[keyof typeof UserErrorCode];

export const userErrorMessages: Record<UserErrorCode, string> = {
  USER_NOT_FOUND: '사용자를 찾을 수 없습니다',
  INVALID_NICKNAME: '유효하지 않은 닉네임입니다',
  VALIDATION_ERROR: '입력값을 확인해주세요',
};
