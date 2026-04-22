import type { SupabaseClient } from '@supabase/supabase-js';
import { failure, success, type HandlerResult } from '@/backend/http/response';
import {
  ConcertListResponseSchema,
  ConcertDetailResponseSchema,
  type ConcertListResponse,
  type ConcertDetailResponse,
} from './schema';
import { concertErrorCodes, type ConcertServiceError } from './error';

/**
 * 예약 가능한 콘서트 목록 조회
 * - 진행일이 현재 시간 + 1일보다 큰 콘서트만 조회
 * - 각 콘서트별 좌석 예약 현황 집계
 */
export const getConcertList = async (
  client: SupabaseClient,
): Promise<HandlerResult<ConcertListResponse, ConcertServiceError, unknown>> => {
  // 쿼리 실행: 콘서트 목록 + 좌석 집계
  const { data, error } = await client
    .from('concerts')
    .select(`
      id,
      title,
      description,
      event_date,
      location,
      thumbnail_url,
      seats (
        id,
        is_reserved
      )
    `)
    .gt('event_date', new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString())
    .order('event_date', { ascending: true });

  if (error) {
    return failure(500, concertErrorCodes.fetchError, error.message);
  }

  if (!data) {
    // 빈 배열도 정상 응답
    return success([]);
  }

  // 데이터 변환: DB 형식 -> API 형식
  const concerts = data.map((concert) => {
    const totalSeats = concert.seats?.length ?? 0;
    const reservedSeats = concert.seats?.filter((s) => s.is_reserved).length ?? 0;
    const availableSeats = totalSeats - reservedSeats;

    return {
      id: concert.id,
      title: concert.title,
      description: concert.description,
      eventDate: concert.event_date,
      location: concert.location,
      thumbnailUrl: concert.thumbnail_url,
      totalSeats,
      reservedSeats,
      availableSeats,
      isSoldOut: availableSeats === 0,
    };
  });

  // 응답 스키마 검증
  const parsed = ConcertListResponseSchema.safeParse(concerts);

  if (!parsed.success) {
    return failure(
      500,
      concertErrorCodes.validationError,
      'Concert list response validation failed.',
      parsed.error.format(),
    );
  }

  return success(parsed.data);
};

/**
 * 콘서트 상세 정보 조회
 * @param client - Supabase 클라이언트
 * @param concertId - 콘서트 UUID
 * @returns 콘서트 상세 정보 또는 에러
 */
export const getConcertDetail = async (
  client: SupabaseClient,
  concertId: string,
): Promise<HandlerResult<ConcertDetailResponse, ConcertServiceError, unknown>> => {
  // 1. 콘서트 정보 + 좌석 정보 조회
  const { data, error } = await client
    .from('concerts')
    .select(`
      id,
      title,
      description,
      event_date,
      location,
      thumbnail_url,
      created_at,
      seats (
        id,
        is_reserved
      )
    `)
    .eq('id', concertId)
    .single();

  if (error) {
    // Postgres 에러 코드 'PGRST116'은 단일 행이 없음을 의미
    if (error.code === 'PGRST116') {
      return failure(404, concertErrorCodes.notFound, 'Concert not found.');
    }
    return failure(500, concertErrorCodes.fetchError, error.message);
  }

  if (!data) {
    return failure(404, concertErrorCodes.notFound, 'Concert not found.');
  }

  // 2. 예약 가능 여부 계산
  const now = new Date();
  const eventDate = new Date(data.event_date);
  const bookingDeadline = new Date(eventDate);
  bookingDeadline.setDate(bookingDeadline.getDate() - 1);
  bookingDeadline.setHours(23, 59, 59, 999);

  const isBookable = now < bookingDeadline;

  // 3. 좌석 현황 집계
  const totalSeats = data.seats?.length ?? 0;
  const reservedSeats = data.seats?.filter((s) => s.is_reserved).length ?? 0;
  const availableSeats = totalSeats - reservedSeats;
  const isSoldOut = availableSeats === 0;

  // 4. 좌석 등급 정보 조회
  const { data: grades } = await client
    .from('seat_grades')
    .select('*')
    .order('display_order');

  // 5. 좌석 상세 정보 조회 (등급별 잔여 좌석 계산용)
  const { data: seats } = await client
    .from('seats')
    .select('id, row, is_reserved')
    .eq('concert_id', concertId);

  // 6. 등급별 잔여 좌석 계산
  const gradeAvailability = (grades || []).map((grade) => {
    const gradeSeats = (seats || []).filter(
      (s) => s.row >= grade.start_row && (grade.end_row === null || s.row <= grade.end_row),
    );
    const availableGradeSeats = gradeSeats.filter((s) => !s.is_reserved);

    return {
      gradeCode: grade.grade_code,
      gradeName: grade.grade_name,
      price: grade.price,
      totalSeats: gradeSeats.length,
      availableSeats: availableGradeSeats.length,
      colorCode: grade.color_code,
    };
  });

  // 7. 응답 데이터 생성
  const response: ConcertDetailResponse = {
    id: data.id,
    title: data.title,
    description: data.description,
    eventDate: data.event_date,
    location: data.location,
    thumbnailUrl: data.thumbnail_url,
    performers: null, // 향후 구현
    totalSeats,
    reservedSeats,
    availableSeats,
    isSoldOut,
    isBookable,
    bookingDeadline: bookingDeadline.toISOString(),
    createdAt: data.created_at,
    gradeAvailability,
  };

  // 5. 응답 스키마 검증
  const parsed = ConcertDetailResponseSchema.safeParse(response);

  if (!parsed.success) {
    return failure(
      500,
      concertErrorCodes.validationError,
      'Concert detail response validation failed.',
      parsed.error.format(),
    );
  }

  return success(parsed.data);
};
