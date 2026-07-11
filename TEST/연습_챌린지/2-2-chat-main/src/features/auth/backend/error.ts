export const AuthErrorCode = {
  EMAIL_DUPLICATE: 'AUTH_EMAIL_DUPLICATE',
  INVALID_CREDENTIALS: 'AUTH_INVALID_CREDENTIALS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',
  UNAUTHORIZED: 'UNAUTHORIZED',
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
} as const;

export type AuthErrorCode =
  (typeof AuthErrorCode)[keyof typeof AuthErrorCode];

export const authErrorMessages: Record<AuthErrorCode, string> = {
  AUTH_EMAIL_DUPLICATE: '이미 가입된 이메일입니다.',
  AUTH_INVALID_CREDENTIALS: '이메일 또는 비밀번호가 올바르지 않습니다.',
  SESSION_EXPIRED: '세션이 만료되었습니다. 다시 로그인해주세요.',
  UNAUTHORIZED: '인증이 필요합니다.',
  INTERNAL_SERVER_ERROR: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
};
