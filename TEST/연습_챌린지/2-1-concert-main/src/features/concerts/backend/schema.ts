import { z } from 'zod';

// 콘서트 목록 응답 스키마
export const ConcertListItemSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string().nullable(),
  eventDate: z.string(), // ISO 8601 형식
  location: z.string(),
  thumbnailUrl: z.string().nullable(),
  totalSeats: z.number().int().min(0),
  reservedSeats: z.number().int().min(0),
  availableSeats: z.number().int().min(0),
  isSoldOut: z.boolean(),
});

export const ConcertListResponseSchema = z.array(ConcertListItemSchema);

// 데이터베이스 테이블 스키마
export const ConcertTableRowSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string().nullable(),
  event_date: z.string(),
  location: z.string(),
  thumbnail_url: z.string().nullable(),
  available_seats: z.number().nullable(),
  reserved_seats: z.number().nullable(),
  total_seats: z.number().nullable(),
});

export type ConcertListItem = z.infer<typeof ConcertListItemSchema>;
export type ConcertListResponse = z.infer<typeof ConcertListResponseSchema>;
export type ConcertRow = z.infer<typeof ConcertTableRowSchema>;

// 좌석 등급별 잔여 좌석 스키마
export const GradeAvailabilitySchema = z.object({
  gradeCode: z.string(),
  gradeName: z.string(),
  price: z.number().int(),
  totalSeats: z.number().int(),
  availableSeats: z.number().int(),
  colorCode: z.string(),
});

export type GradeAvailability = z.infer<typeof GradeAvailabilitySchema>;

// 콘서트 상세 응답 스키마
export const ConcertDetailResponseSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string().nullable(),
  eventDate: z.string(), // ISO 8601
  location: z.string(),
  thumbnailUrl: z.string().nullable(),
  performers: z.array(z.string()).nullable(), // 향후 추가 고려
  totalSeats: z.number().int().min(0),
  reservedSeats: z.number().int().min(0),
  availableSeats: z.number().int().min(0),
  isSoldOut: z.boolean(),
  isBookable: z.boolean(),
  bookingDeadline: z.string(), // ISO 8601
  createdAt: z.string(),
  gradeAvailability: z.array(GradeAvailabilitySchema),
});

export type ConcertDetailResponse = z.infer<typeof ConcertDetailResponseSchema>;

// Path Parameter 검증 스키마
export const ConcertIdParamSchema = z.object({
  concertId: z.string().uuid(),
});

export type ConcertIdParam = z.infer<typeof ConcertIdParamSchema>;
