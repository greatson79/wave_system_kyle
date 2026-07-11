export const bookingErrorCodes = {
  // 좌석 조회 관련
  concertNotFound: 'CONCERT_NOT_FOUND',
  seatsFetchError: 'SEATS_FETCH_ERROR',

  // 예약 생성 관련
  validationError: 'BOOKING_VALIDATION_ERROR',
  bookingClosed: 'BOOKING_CLOSED',
  seatAlreadyReserved: 'SEAT_ALREADY_RESERVED',
  invalidSeatId: 'INVALID_SEAT_ID',
  seatCountExceeded: 'SEAT_COUNT_EXCEEDED',
  transactionError: 'TRANSACTION_ERROR',
  deadlockDetected: 'DEADLOCK_DETECTED',

  // 예약 조회 관련
  bookingNotFound: 'BOOKING_NOT_FOUND',
  authenticationFailed: 'AUTHENTICATION_FAILED',

  // 예약 취소 관련
  alreadyCancelled: 'ALREADY_CANCELLED',
  cancellationNotAllowed: 'CANCELLATION_NOT_ALLOWED',
} as const;

export type BookingServiceError =
  | typeof bookingErrorCodes.concertNotFound
  | typeof bookingErrorCodes.seatsFetchError
  | typeof bookingErrorCodes.validationError
  | typeof bookingErrorCodes.bookingClosed
  | typeof bookingErrorCodes.seatAlreadyReserved
  | typeof bookingErrorCodes.invalidSeatId
  | typeof bookingErrorCodes.seatCountExceeded
  | typeof bookingErrorCodes.transactionError
  | typeof bookingErrorCodes.deadlockDetected
  | typeof bookingErrorCodes.bookingNotFound
  | typeof bookingErrorCodes.authenticationFailed
  | typeof bookingErrorCodes.alreadyCancelled
  | typeof bookingErrorCodes.cancellationNotAllowed;
