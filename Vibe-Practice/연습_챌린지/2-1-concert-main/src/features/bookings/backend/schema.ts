import { z } from 'zod';

// ===== 좌석 등급 스키마 =====

export const SeatGradeSchema = z.object({
  gradeCode: z.string(),
  gradeName: z.string(),
  startRow: z.number().int(),
  endRow: z.number().int().nullable(),
  price: z.number().int().positive(),
  colorCode: z.string(),
  displayOrder: z.number().int(),
});

export type SeatGrade = z.infer<typeof SeatGradeSchema>;

// ===== 좌석 조회 API =====

export const SeatSchema = z.object({
  id: z.string().uuid(),
  section: z.enum(['A', 'B', 'C', 'D']),
  row: z.number().int().min(1).max(20),
  seatColumn: z.number().int().min(1).max(4),
  isReserved: z.boolean(),
  gradeCode: z.string(),
  gradeName: z.string(),
  price: z.number().int(),
  colorCode: z.string(),
});

export const GradeAvailabilitySchema = z.object({
  gradeCode: z.string(),
  gradeName: z.string(),
  price: z.number().int(),
  totalSeats: z.number().int(),
  availableSeats: z.number().int(),
  colorCode: z.string(),
});

export const SeatsResponseSchema = z.object({
  concertId: z.string().uuid(),
  concertTitle: z.string(),
  eventDate: z.string(), // ISO 8601
  totalSeats: z.number().int().min(0),
  availableSeats: z.number().int().min(0),
  sections: z.array(
    z.object({
      name: z.enum(['A', 'B', 'C', 'D']),
      seats: z.array(SeatSchema),
    }),
  ),
  grades: z.array(SeatGradeSchema),
  gradeAvailability: z.array(GradeAvailabilitySchema),
});

export type Seat = z.infer<typeof SeatSchema>;
export type GradeAvailability = z.infer<typeof GradeAvailabilitySchema>;
export type SeatsResponse = z.infer<typeof SeatsResponseSchema>;

// ===== 예약 생성 API =====

export const CreateBookingRequestSchema = z.object({
  concertId: z.string().uuid(),
  seatIds: z.array(z.string().uuid()).min(1).max(4),
  name: z.string().min(2).max(50).trim(),
  phone: z.string().regex(/^01[0-9]{8,9}$/, 'Invalid phone number format'), // 01012345678
  password: z.string().regex(/^[0-9]{4}$/, 'Password must be exactly 4 digits'),
});

export const CreateBookingResponseSchema = z.object({
  bookingId: z.string().uuid(),
  concertId: z.string().uuid(),
  concertTitle: z.string(),
  eventDate: z.string(),
  seats: z.array(
    z.object({
      section: z.enum(['A', 'B', 'C', 'D']),
      row: z.number().int(),
      seatColumn: z.number().int(),
      gradeCode: z.string(),
      gradeName: z.string(),
      price: z.number().int(),
    }),
  ),
  totalAmount: z.number().int(),
  name: z.string(),
  phone: z.string(),
  status: z.enum(['confirmed', 'cancelled']),
  createdAt: z.string(),
});

export type CreateBookingRequest = z.infer<typeof CreateBookingRequestSchema>;
export type CreateBookingResponse = z.infer<typeof CreateBookingResponseSchema>;

// ===== DB 테이블 스키마 =====

export const SeatRowSchema = z.object({
  id: z.string().uuid(),
  concert_id: z.string().uuid(),
  section: z.string(),
  row: z.number(),
  seat_column: z.number(),
  is_reserved: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const BookingRowSchema = z.object({
  id: z.string().uuid(),
  concert_id: z.string().uuid(),
  name: z.string(),
  phone: z.string(),
  password_hash: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type SeatRow = z.infer<typeof SeatRowSchema>;
export type BookingRow = z.infer<typeof BookingRowSchema>;

// ===== 예약 상세 조회 API =====

export const BookingDetailResponseSchema = z.object({
  bookingId: z.string().uuid(),
  status: z.enum(['confirmed', 'cancelled']),
  concertId: z.string().uuid(),
  concertTitle: z.string(),
  concertDescription: z.string().nullable(),
  eventDate: z.string(), // ISO 8601
  location: z.string(),
  thumbnailUrl: z.string().nullable(),
  seats: z.array(
    z.object({
      seatId: z.string().uuid(),
      section: z.enum(['A', 'B', 'C', 'D']),
      row: z.number().int(),
      seatColumn: z.number().int(),
      gradeCode: z.string(),
      gradeName: z.string(),
      price: z.number().int(),
    }),
  ),
  totalAmount: z.number().int(),
  bookingName: z.string(),
  bookingPhone: z.string(), // 조회 시 마스킹 처리
  createdAt: z.string(), // ISO 8601
});

export type BookingDetailResponse = z.infer<typeof BookingDetailResponseSchema>;

// ===== 예약 조회 API =====

export const LookupBookingsRequestSchema = z.object({
  phone: z.string().regex(/^01[0-9]{8,9}$/, 'Invalid phone number format'),
  password: z.string().regex(/^[0-9]{4}$/, 'Password must be exactly 4 digits'),
});

export const BookingSummarySchema = z.object({
  bookingId: z.string().uuid(),
  status: z.enum(['confirmed', 'cancelled']),
  concertId: z.string().uuid(),
  concertTitle: z.string(),
  eventDate: z.string(), // ISO 8601
  location: z.string(),
  thumbnailUrl: z.string().nullable(),
  seats: z.array(
    z.object({
      section: z.enum(['A', 'B', 'C', 'D']),
      row: z.number().int(),
      seatColumn: z.number().int(),
      gradeCode: z.string(),
      gradeName: z.string(),
      price: z.number().int(),
    }),
  ),
  totalAmount: z.number().int(),
  bookingName: z.string(),
  createdAt: z.string(), // ISO 8601
});

export const LookupBookingsResponseSchema = z.object({
  bookings: z.array(BookingSummarySchema),
  total: z.number().int().min(0),
});

export type LookupBookingsRequest = z.infer<typeof LookupBookingsRequestSchema>;
export type BookingSummary = z.infer<typeof BookingSummarySchema>;
export type LookupBookingsResponse = z.infer<typeof LookupBookingsResponseSchema>;

// ===== 예약 취소 API =====

export const CancelBookingRequestSchema = z.object({
  phone: z.string().regex(/^01[0-9]{8,9}$/, 'Invalid phone number format'),
  password: z.string().regex(/^[0-9]{4}$/, 'Password must be exactly 4 digits'),
});

export const CancelBookingResponseSchema = z.object({
  bookingId: z.string().uuid(),
  status: z.literal('cancelled'),
  cancelledAt: z.string(), // ISO 8601
  cancelledSeats: z.array(
    z.object({
      section: z.enum(['A', 'B', 'C', 'D']),
      row: z.number().int(),
      seatColumn: z.number().int(),
    }),
  ),
});

export type CancelBookingRequest = z.infer<typeof CancelBookingRequestSchema>;
export type CancelBookingResponse = z.infer<typeof CancelBookingResponseSchema>;
