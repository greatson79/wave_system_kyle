import type { Hono } from 'hono';
import { failure, respond, type ErrorResult } from '@/backend/http/response';
import { getLogger, getSupabase, type AppEnv } from '@/backend/hono/context';
import { getConcertSeats, createBooking, getBookingDetail, lookupBookings, cancelBooking } from './service';
import { CreateBookingRequestSchema, LookupBookingsRequestSchema, CancelBookingRequestSchema } from './schema';
import { bookingErrorCodes, type BookingServiceError } from './error';

export const registerBookingRoutes = (app: Hono<AppEnv>) => {
  /**
   * GET /api/concerts/:concertId/seats
   * 콘서트 좌석 배치도 조회
   */
  app.get('/api/concerts/:concertId/seats', async (c) => {
    const concertId = c.req.param('concertId');
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    const result = await getConcertSeats(supabase, concertId);

    if (!result.ok) {
      const errorResult = result as ErrorResult<BookingServiceError, unknown>;

      if (errorResult.error.code === bookingErrorCodes.concertNotFound) {
        logger.warn('Concert not found for seat map', { concertId });
      } else {
        logger.error('Failed to fetch seat map', errorResult.error.message);
      }

      return respond(c, result);
    }

    return respond(c, result);
  });

  /**
   * POST /api/bookings
   * 예약 생성
   */
  app.post('/api/bookings', async (c) => {
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    // 1. Request Body 파싱
    const body = await c.req.json();

    // 2. 스키마 검증
    const parsed = CreateBookingRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          bookingErrorCodes.validationError,
          'Invalid booking request data.',
          parsed.error.format(),
        ),
      );
    }

    // 3. 서비스 호출
    const result = await createBooking(supabase, parsed.data);

    // 4. 에러 핸들링
    if (!result.ok) {
      const errorResult = result as ErrorResult<BookingServiceError, unknown>;

      if (errorResult.error.code === bookingErrorCodes.seatAlreadyReserved) {
        logger.warn('Seat already reserved', {
          concertId: parsed.data.concertId,
          seatIds: parsed.data.seatIds,
        });
      } else if (errorResult.error.code === bookingErrorCodes.deadlockDetected) {
        logger.error('Deadlock detected during booking creation');
      } else if (errorResult.error.code === bookingErrorCodes.transactionError) {
        logger.error('Transaction error during booking creation', errorResult.error.message);
      }

      return respond(c, result);
    }

    // 5. 성공 응답
    logger.info('Booking created successfully', {
      bookingId: result.data.bookingId,
      concertId: result.data.concertId,
    });

    return respond(c, result);
  });

  /**
   * GET /api/bookings/:bookingId
   * 예약 상세 정보 조회
   */
  app.get('/api/bookings/:bookingId', async (c) => {
    const bookingId = c.req.param('bookingId');
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    const result = await getBookingDetail(supabase, bookingId);

    if (!result.ok) {
      const errorResult = result as ErrorResult<BookingServiceError, unknown>;

      if (errorResult.error.code === bookingErrorCodes.bookingNotFound) {
        logger.warn('Booking not found', { bookingId });
      } else {
        logger.error('Failed to fetch booking detail', errorResult.error.message);
      }

      return respond(c, result);
    }

    return respond(c, result);
  });

  /**
   * POST /api/bookings/lookup
   * 예약 조회 (휴대폰번호 + 비밀번호)
   */
  app.post('/api/bookings/lookup', async (c) => {
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    // 1. Request Body 파싱
    const body = await c.req.json();

    // 2. 스키마 검증
    const parsed = LookupBookingsRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          bookingErrorCodes.validationError,
          'Invalid lookup request data.',
          parsed.error.format(),
        ),
      );
    }

    const { phone, password } = parsed.data;

    // 3. 서비스 호출
    const result = await lookupBookings(supabase, phone, password);

    // 4. 에러 핸들링
    if (!result.ok) {
      const errorResult = result as ErrorResult<BookingServiceError, unknown>;

      if (errorResult.error.code === bookingErrorCodes.authenticationFailed) {
        logger.warn('Booking lookup authentication failed', { phone });
      } else {
        logger.error('Failed to lookup bookings', errorResult.error.message);
      }

      return respond(c, result);
    }

    // 5. 성공 응답
    logger.info('Bookings lookup successful', {
      phone,
      total: result.data.total,
    });

    return respond(c, result);
  });

  /**
   * PATCH /api/bookings/:bookingId/cancel
   * 예약 취소 (예약 조회 페이지에서)
   */
  app.patch('/api/bookings/:bookingId/cancel', async (c) => {
    const bookingId = c.req.param('bookingId');
    const supabase = getSupabase(c);
    const logger = getLogger(c);

    // 1. Request Body 파싱
    const body = await c.req.json();

    // 2. 스키마 검증
    const parsed = CancelBookingRequestSchema.safeParse(body);

    if (!parsed.success) {
      return respond(
        c,
        failure(
          400,
          bookingErrorCodes.validationError,
          'Invalid cancel request data.',
          parsed.error.format(),
        ),
      );
    }

    const { phone, password } = parsed.data;

    // 3. 서비스 호출
    const result = await cancelBooking(supabase, bookingId, phone, password);

    // 4. 에러 핸들링
    if (!result.ok) {
      const errorResult = result as ErrorResult<BookingServiceError, unknown>;

      if (errorResult.error.code === bookingErrorCodes.authenticationFailed) {
        logger.warn('Booking cancellation authentication failed', { bookingId, phone });
      } else if (errorResult.error.code === bookingErrorCodes.alreadyCancelled) {
        logger.warn('Booking is already cancelled', { bookingId });
      } else if (errorResult.error.code === bookingErrorCodes.cancellationNotAllowed) {
        logger.warn('Booking cancellation not allowed', { bookingId });
      } else {
        logger.error('Failed to cancel booking', errorResult.error.message);
      }

      return respond(c, result);
    }

    // 5. 성공 응답
    logger.info('Booking cancelled successfully', {
      bookingId,
    });

    return respond(c, result);
  });
};
