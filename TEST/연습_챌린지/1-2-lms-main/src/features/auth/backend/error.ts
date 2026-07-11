export const authErrorCodes = {
  invalidRequest: 'AUTH_INVALID_REQUEST',
  emailAlreadyExists: 'AUTH_EMAIL_ALREADY_EXISTS',
  weakPassword: 'AUTH_WEAK_PASSWORD',
  invalidPhone: 'AUTH_INVALID_PHONE',
  termsNotAgreed: 'AUTH_TERMS_NOT_AGREED',
  authCreationFailed: 'AUTH_CREATION_FAILED',
  profileCreationFailed: 'AUTH_PROFILE_CREATION_FAILED',
  termsRecordFailed: 'AUTH_TERMS_RECORD_FAILED',
  validationError: 'AUTH_VALIDATION_ERROR',
} as const;

type AuthErrorValue =
  (typeof authErrorCodes)[keyof typeof authErrorCodes];

export type AuthServiceError = AuthErrorValue;
