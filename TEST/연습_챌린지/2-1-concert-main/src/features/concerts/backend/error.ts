export const concertErrorCodes = {
  fetchError: 'CONCERT_FETCH_ERROR',
  validationError: 'CONCERT_VALIDATION_ERROR',
  notFound: 'CONCERT_NOT_FOUND',
  invalidId: 'INVALID_CONCERT_ID',
} as const;

export type ConcertServiceError =
  | typeof concertErrorCodes.fetchError
  | typeof concertErrorCodes.validationError
  | typeof concertErrorCodes.notFound
  | typeof concertErrorCodes.invalidId;
