import type { SupabaseClient } from '@supabase/supabase-js';
import { failure, success, type HandlerResult } from '@/backend/http/response';
import bcrypt from 'bcryptjs';
import {
  SeatsResponseSchema,
  CreateBookingResponseSchema,
  BookingDetailResponseSchema,
  LookupBookingsResponseSchema,
  CancelBookingResponseSchema,
  type SeatsResponse,
  type CreateBookingRequest,
  type CreateBookingResponse,
  type BookingDetailResponse,
  type BookingSummary,
  type LookupBookingsResponse,
  type CancelBookingResponse,
  type SeatRow,
} from './schema';
import { bookingErrorCodes, type BookingServiceError } from './error';

/**
 * 콘서트 좌석 배치도 조회
 */
export const getConcertSeats = async (
  client: SupabaseClient,
  concertId: string,
): Promise<HandlerResult<SeatsResponse, BookingServiceError, unknown>> => {
  // 1. 콘서트 정보 조회
  const { data: concert, error: concertError } = await client
    .from('concerts')
    .select('id, title, event_date')
    .eq('id', concertId)
    .single();

  if (concertError || !concert) {
    return failure(404, bookingErrorCodes.concertNotFound, 'Concert not found.');
  }

  // 2. 좌석 등급 정보 조회
  const { data: grades, error: gradesError } = await client
    .from('seat_grades')
    .select('*')
    .order('display_order');

  if (gradesError) {
    return failure(500, bookingErrorCodes.seatsFetchError, gradesError.message);
  }

  // 3. 좌석 목록 조회 (320개)
  const { data: seats, error: seatsError } = await client
    .from('seats')
    .select('id, section, row, seat_column, is_reserved')
    .eq('concert_id', concertId)
    .order('section')
    .order('row')
    .order('seat_column');

  if (seatsError) {
    return failure(500, bookingErrorCodes.seatsFetchError, seatsError.message);
  }

  if (!seats || seats.length === 0) {
    return failure(500, bookingErrorCodes.seatsFetchError, 'No seats found for this concert.');
  }

  // 4. 좌석에 등급 정보 매핑
  const seatsWithGrade = seats.map((seat) => {
    const grade = grades?.find(
      (g) => seat.row >= g.start_row && (g.end_row === null || seat.row <= g.end_row),
    );

    return {
      id: seat.id,
      section: seat.section as 'A' | 'B' | 'C' | 'D',
      row: seat.row,
      seatColumn: seat.seat_column,
      isReserved: seat.is_reserved,
      gradeCode: grade?.grade_code || 'R',
      gradeName: grade?.grade_name || 'Regular',
      price: grade?.price || 140000,
      colorCode: grade?.color_code || '#F97316',
    };
  });

  // 5. 구역별로 그룹화
  const sectionGroups: Record<string, typeof seatsWithGrade> = {
    A: [],
    B: [],
    C: [],
    D: [],
  };

  seatsWithGrade.forEach((seat) => {
    if (sectionGroups[seat.section]) {
      sectionGroups[seat.section].push(seat);
    }
  });

  // 6. 등급별 잔여 좌석 계산
  const gradeAvailability = (grades || []).map((grade) => {
    const gradeSeats = seatsWithGrade.filter((s) => s.gradeCode === grade.grade_code);
    const availableGradeSeats = gradeSeats.filter((s) => !s.isReserved);

    return {
      gradeCode: grade.grade_code,
      gradeName: grade.grade_name,
      price: grade.price,
      totalSeats: gradeSeats.length,
      availableSeats: availableGradeSeats.length,
      colorCode: grade.color_code,
    };
  });

  // 7. 응답 데이터 구성
  const availableSeats = seatsWithGrade.filter((s) => !s.isReserved).length;

  const response: SeatsResponse = {
    concertId: concert.id,
    concertTitle: concert.title,
    eventDate: concert.event_date,
    totalSeats: seatsWithGrade.length,
    availableSeats,
    sections: ['A', 'B', 'C', 'D'].map((section) => ({
      name: section as 'A' | 'B' | 'C' | 'D',
      seats: sectionGroups[section],
    })),
    grades: (grades || []).map((g) => ({
      gradeCode: g.grade_code,
      gradeName: g.grade_name,
      startRow: g.start_row,
      endRow: g.end_row,
      price: g.price,
      colorCode: g.color_code,
      displayOrder: g.display_order,
    })),
    gradeAvailability,
  };

  // 8. 스키마 검증
  const parsed = SeatsResponseSchema.safeParse(response);

  if (!parsed.success) {
    return failure(
      500,
      bookingErrorCodes.validationError,
      'Seats response validation failed.',
      parsed.error.format(),
    );
  }

  return success(parsed.data);
};

/**
 * 예약 생성 (PostgreSQL RPC 함수 사용)
 */
export const createBooking = async (
  client: SupabaseClient,
  data: CreateBookingRequest,
): Promise<HandlerResult<CreateBookingResponse, BookingServiceError, unknown>> => {
  const { concertId, seatIds, name, phone, password } = data;

  try {
    // 1. 비밀번호 해싱
    const passwordHash = await bcrypt.hash(password, 10);

    // 2. PostgreSQL RPC 함수 호출 (트랜잭션 + Row-Level Locking)
    const { data: rpcResult, error: rpcError } = await client.rpc('create_booking_with_lock', {
      p_concert_id: concertId,
      p_seat_ids: seatIds,
      p_name: name,
      p_phone: phone,
      p_password_hash: passwordHash,
    });

    if (rpcError) {
      // RPC 에러 처리
      const errorMessage = rpcError.message;

      if (errorMessage.includes('Seat already reserved')) {
        return failure(409, bookingErrorCodes.seatAlreadyReserved, errorMessage);
      } else if (errorMessage.includes('Booking period has ended')) {
        return failure(400, bookingErrorCodes.bookingClosed, errorMessage);
      } else if (errorMessage.includes('Concert not found')) {
        return failure(404, bookingErrorCodes.concertNotFound, errorMessage);
      } else if (errorMessage.includes('One or more seat IDs are invalid')) {
        return failure(400, bookingErrorCodes.invalidSeatId, errorMessage);
      } else if (errorMessage.includes('deadlock')) {
        return failure(503, bookingErrorCodes.deadlockDetected, 'Deadlock detected. Please retry.');
      } else {
        return failure(500, bookingErrorCodes.transactionError, errorMessage);
      }
    }

    if (!rpcResult || !rpcResult.booking_id) {
      return failure(500, bookingErrorCodes.transactionError, 'Failed to create booking.');
    }

    const bookingId = rpcResult.booking_id;

    // 3. 예약 완료 후 필요한 정보 조회
    const { data: concert } = await client
      .from('concerts')
      .select('id, title, event_date')
      .eq('id', concertId)
      .single();

    const { data: selectedSeats } = await client
      .from('seats')
      .select('section, row, seat_column')
      .in('id', seatIds);

    const { data: booking } = await client
      .from('bookings')
      .select('created_at')
      .eq('id', bookingId)
      .single();

    const { data: grades } = await client
      .from('seat_grades')
      .select('*')
      .order('display_order');

    if (!concert || !selectedSeats || !booking) {
      return failure(500, bookingErrorCodes.transactionError, 'Failed to fetch booking details.');
    }

    // 4. 좌석에 등급 정보 추가
    const seatsWithGrade = selectedSeats.map((seat) => {
      const grade = grades?.find(
        (g) => seat.row >= g.start_row && (g.end_row === null || seat.row <= g.end_row),
      );

      return {
        section: seat.section as 'A' | 'B' | 'C' | 'D',
        row: seat.row,
        seatColumn: seat.seat_column,
        gradeCode: grade?.grade_code || 'R',
        gradeName: grade?.grade_name || 'Regular',
        price: grade?.price || 140000,
      };
    });

    // 5. 총 금액 계산
    const totalAmount = seatsWithGrade.reduce((sum, seat) => sum + seat.price, 0);

    // 6. 응답 데이터 구성
    const response: CreateBookingResponse = {
      bookingId,
      concertId: concert.id,
      concertTitle: concert.title,
      eventDate: concert.event_date,
      seats: seatsWithGrade,
      totalAmount,
      name,
      phone,
      status: 'confirmed',
      createdAt: booking.created_at,
    };

    const parsed = CreateBookingResponseSchema.safeParse(response);

    if (!parsed.success) {
      return failure(500, bookingErrorCodes.validationError, 'Booking response validation failed.', parsed.error.format());
    }

    return success(parsed.data);
  } catch (error) {
    // 기타 예외 처리
    if (error instanceof Error) {
      if (error.message.includes('deadlock')) {
        return failure(503, bookingErrorCodes.deadlockDetected, 'Deadlock detected. Please retry.');
      }
      return failure(500, bookingErrorCodes.transactionError, error.message);
    }
    return failure(500, bookingErrorCodes.transactionError, 'Unknown error occurred.');
  }
};

/**
 * 예약 상세 정보 조회
 */
export const getBookingDetail = async (
  client: SupabaseClient,
  bookingId: string,
): Promise<HandlerResult<BookingDetailResponse, BookingServiceError, unknown>> => {
  try {
    // 1. 예약 정보 조회 (콘서트 정보 JOIN)
    const { data: booking, error: bookingError } = await client
      .from('bookings')
      .select(
        `
        id,
        name,
        phone,
        status,
        created_at,
        concerts (
          id,
          title,
          description,
          event_date,
          location,
          thumbnail_url
        )
      `,
      )
      .eq('id', bookingId)
      .single();

    if (bookingError || !booking) {
      return failure(404, bookingErrorCodes.bookingNotFound, 'Booking not found.');
    }

    // 2. 예약된 좌석 정보 조회
    const { data: bookingSeats, error: seatsError } = await client
      .from('booking_seats')
      .select(
        `
        seat_id,
        seats (
          id,
          section,
          row,
          seat_column
        )
      `,
      )
      .eq('booking_id', bookingId);

    if (seatsError || !bookingSeats || bookingSeats.length === 0) {
      return failure(500, bookingErrorCodes.seatsFetchError, 'Failed to fetch booking seats.');
    }

    // 3. 좌석 등급 정보 조회
    const { data: grades } = await client
      .from('seat_grades')
      .select('*')
      .order('display_order');

    // 4. 휴대폰번호 마스킹 처리 (010****5678)
    const maskedPhone = booking.phone.replace(/^(\d{3})(\d{4})(\d{4})$/, '$1****$3');

    // 5. 좌석에 등급 정보 추가
    const seatsWithPrice = bookingSeats.map((bs: any) => {
      const seat = bs.seats;
      const grade = grades?.find(
        (g) => seat.row >= g.start_row && (g.end_row === null || seat.row <= g.end_row),
      );

      return {
        seatId: seat.id,
        section: seat.section as 'A' | 'B' | 'C' | 'D',
        row: seat.row,
        seatColumn: seat.seat_column,
        gradeCode: grade?.grade_code || 'R',
        gradeName: grade?.grade_name || 'Regular',
        price: grade?.price || 140000,
      };
    });

    // 6. 총 금액 계산
    const totalAmount = seatsWithPrice.reduce((sum, seat) => sum + seat.price, 0);

    // 7. 응답 데이터 구성
    const concert = booking.concerts as any;
    const response: BookingDetailResponse = {
      bookingId: booking.id,
      status: booking.status as 'confirmed' | 'cancelled',
      concertId: concert.id,
      concertTitle: concert.title,
      concertDescription: concert.description,
      eventDate: concert.event_date,
      location: concert.location,
      thumbnailUrl: concert.thumbnail_url,
      seats: seatsWithPrice,
      totalAmount,
      bookingName: booking.name,
      bookingPhone: maskedPhone,
      createdAt: booking.created_at,
    };

    // 5. 스키마 검증
    const parsed = BookingDetailResponseSchema.safeParse(response);

    if (!parsed.success) {
      return failure(
        500,
        bookingErrorCodes.validationError,
        'Booking detail response validation failed.',
        parsed.error.format(),
      );
    }

    return success(parsed.data);
  } catch (error) {
    if (error instanceof Error) {
      return failure(500, bookingErrorCodes.transactionError, error.message);
    }
    return failure(500, bookingErrorCodes.transactionError, 'Unknown error occurred.');
  }
};

/**
 * 예약 조회 (휴대폰번호 + 비밀번호 인증)
 */
export const lookupBookings = async (
  client: SupabaseClient,
  phone: string,
  password: string,
): Promise<HandlerResult<LookupBookingsResponse, BookingServiceError, unknown>> => {
  try {
    // 1. 휴대폰번호로 예약 조회
    const { data: bookings, error: bookingsError } = await client
      .from('bookings')
      .select(
        `
        id,
        name,
        phone,
        password_hash,
        status,
        created_at,
        concerts (
          id,
          title,
          event_date,
          location,
          thumbnail_url
        )
      `,
      )
      .eq('phone', phone)
      .order('created_at', { ascending: false });

    if (bookingsError) {
      return failure(500, bookingErrorCodes.transactionError, bookingsError.message);
    }

    if (!bookings || bookings.length === 0) {
      return success({ bookings: [], total: 0 });
    }

    // 2. 비밀번호 검증 (각 예약에 대해)
    const validatedBookings = [];

    for (const booking of bookings) {
      const isPasswordMatch = await bcrypt.compare(password, booking.password_hash);

      if (isPasswordMatch) {
        validatedBookings.push(booking);
      }
    }

    // 3. 비밀번호 일치하는 예약이 없으면 인증 실패
    if (validatedBookings.length === 0) {
      return failure(401, bookingErrorCodes.authenticationFailed, 'Invalid credentials');
    }

    // 4. 좌석 등급 정보 조회
    const { data: grades } = await client
      .from('seat_grades')
      .select('*')
      .order('display_order');

    // 5. 각 예약의 좌석 정보 조회
    const bookingSummaries: BookingSummary[] = [];

    for (const booking of validatedBookings) {
      const { data: bookingSeats, error: seatsError } = await client
        .from('booking_seats')
        .select(
          `
          seats (
            section,
            row,
            seat_column
          )
        `,
        )
        .eq('booking_id', booking.id);

      if (seatsError) {
        continue;
      }

      // 좌석에 등급 정보 추가
      const seatsWithPrice = (bookingSeats || []).map((bs: any) => {
        const seat = bs.seats;
        const grade = grades?.find(
          (g) => seat.row >= g.start_row && (g.end_row === null || seat.row <= g.end_row),
        );

        return {
          section: seat.section as 'A' | 'B' | 'C' | 'D',
          row: seat.row,
          seatColumn: seat.seat_column,
          gradeCode: grade?.grade_code || 'R',
          gradeName: grade?.grade_name || 'Regular',
          price: grade?.price || 140000,
        };
      });

      // 총 금액 계산
      const totalAmount = seatsWithPrice.reduce((sum, seat) => sum + seat.price, 0);

      const concert = booking.concerts as any;

      bookingSummaries.push({
        bookingId: booking.id,
        status: booking.status as 'confirmed' | 'cancelled',
        concertId: concert.id,
        concertTitle: concert.title,
        eventDate: concert.event_date,
        location: concert.location,
        thumbnailUrl: concert.thumbnail_url,
        seats: seatsWithPrice,
        totalAmount,
        bookingName: booking.name,
        createdAt: booking.created_at,
      });
    }

    // 5. 응답 데이터 구성
    const response: LookupBookingsResponse = {
      bookings: bookingSummaries,
      total: bookingSummaries.length,
    };

    // 6. 스키마 검증
    const parsed = LookupBookingsResponseSchema.safeParse(response);

    if (!parsed.success) {
      return failure(
        500,
        bookingErrorCodes.validationError,
        'Lookup response validation failed.',
        parsed.error.format(),
      );
    }

    return success(parsed.data);
  } catch (error) {
    if (error instanceof Error) {
      return failure(500, bookingErrorCodes.transactionError, error.message);
    }
    return failure(500, bookingErrorCodes.transactionError, 'Unknown error occurred.');
  }
};

/**
 * 예약 취소 (예약 조회 페이지에서)
 */
export const cancelBooking = async (
  client: SupabaseClient,
  bookingId: string,
  phone: string,
  password: string,
): Promise<HandlerResult<CancelBookingResponse, BookingServiceError, unknown>> => {
  try {
    // 1. 예약 정보 조회 (콘서트 정보 포함)
    const { data: booking, error: bookingError } = await client
      .from('bookings')
      .select(
        `
        id,
        phone,
        password_hash,
        status,
        updated_at,
        concerts (
          id,
          event_date
        )
      `,
      )
      .eq('id', bookingId)
      .single();

    if (bookingError || !booking) {
      return failure(404, bookingErrorCodes.bookingNotFound, 'Booking not found.');
    }

    // 2. 인증 검증 (휴대폰번호 + 비밀번호)
    if (booking.phone !== phone) {
      return failure(401, bookingErrorCodes.authenticationFailed, 'Invalid credentials');
    }

    const isPasswordMatch = await bcrypt.compare(password, booking.password_hash);

    if (!isPasswordMatch) {
      return failure(401, bookingErrorCodes.authenticationFailed, 'Invalid credentials');
    }

    // 3. 상태 검증
    if (booking.status === 'cancelled') {
      return failure(400, bookingErrorCodes.alreadyCancelled, 'Booking is already cancelled.');
    }

    // 4. 콘서트 시작 여부 확인 (취소 가능 기간)
    const concert = booking.concerts as any;
    const now = new Date();
    const eventDate = new Date(concert.event_date);

    if (now >= eventDate) {
      return failure(
        400,
        bookingErrorCodes.cancellationNotAllowed,
        'Cannot cancel booking after concert has started.',
      );
    }

    // 5. 예약된 좌석 ID 조회
    const { data: bookingSeats, error: seatsError } = await client
      .from('booking_seats')
      .select('seat_id, seats(section, row, seat_column)')
      .eq('booking_id', bookingId);

    if (seatsError || !bookingSeats || bookingSeats.length === 0) {
      return failure(500, bookingErrorCodes.transactionError, 'Failed to fetch booking seats.');
    }

    const seatIds = bookingSeats.map((bs: any) => bs.seat_id);

    // 6. 트랜잭션 처리 (예약 상태 업데이트 + 좌석 복원)
    const { error: updateBookingError } = await client
      .from('bookings')
      .update({ status: 'cancelled', updated_at: new Date().toISOString() })
      .eq('id', bookingId);

    if (updateBookingError) {
      return failure(500, bookingErrorCodes.transactionError, updateBookingError.message);
    }

    const { error: updateSeatsError } = await client
      .from('seats')
      .update({ is_reserved: false, updated_at: new Date().toISOString() })
      .in('id', seatIds);

    if (updateSeatsError) {
      return failure(500, bookingErrorCodes.transactionError, updateSeatsError.message);
    }

    // 7. 응답 데이터 구성
    const response: CancelBookingResponse = {
      bookingId,
      status: 'cancelled',
      cancelledAt: new Date().toISOString(),
      cancelledSeats: bookingSeats.map((bs: any) => ({
        section: bs.seats.section as 'A' | 'B' | 'C' | 'D',
        row: bs.seats.row,
        seatColumn: bs.seats.seat_column,
      })),
    };

    // 8. 스키마 검증
    const parsed = CancelBookingResponseSchema.safeParse(response);

    if (!parsed.success) {
      return failure(
        500,
        bookingErrorCodes.validationError,
        'Cancel response validation failed.',
        parsed.error.format(),
      );
    }

    return success(parsed.data);
  } catch (error) {
    if (error instanceof Error) {
      return failure(500, bookingErrorCodes.transactionError, error.message);
    }
    return failure(500, bookingErrorCodes.transactionError, 'Unknown error occurred.');
  }
};
