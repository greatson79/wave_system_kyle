# 좌석 등급별 가격 차등 기능 추가 구현 계획

**작성일**: 2025-10-13
**버전**: 1.0
**상태**: 구현 대기

---

## 📋 개요

### 추가 요구사항
좌석 등급별 가격 차등 시스템을 도입하여, 행 번호에 따라 좌석 가격을 4개 등급(S, P, A, R)으로 나누고, 예약 시 등급별 가격을 반영합니다.

### 등급 정의
| 등급 | 등급명 | 시작 행 | 종료 행 | 가격 | 색상 코드 | 색상 |
|------|--------|---------|---------|------|-----------|------|
| S | Special | 1 | 3 | 250,000원 | `#9333EA` | 보라색 (purple-600) |
| P | Premium | 4 | 7 | 190,000원 | `#0EA5E9` | 하늘색 (sky-500) |
| A | Advanced | 8 | 15 | 170,000원 | `#10B981` | 초록색 (emerald-500) |
| R | Regular | 16 | 20 | 140,000원 | `#F97316` | 주황색 (orange-500) |

### 주요 변경 사항
1. **데이터베이스**: 좌석 등급 테이블 (`seat_grades`) 추가
2. **백엔드 API**: 등급 정보 포함한 응답 스키마 수정
3. **프론트엔드 UI**:
   - 좌석 선택 페이지: 등급별 색상 표시, 가격 정보 표시, 선택 좌석 금액 합계
   - 콘서트 상세 페이지: 등급별 잔여 좌석 표시
   - 예약 완료/조회 페이지: 좌석별 등급 및 금액 표시

---

## 🗄️ 1. 데이터베이스 변경사항

### 1.1 새로운 테이블: `seat_grades`

```sql
-- =============================================================================
-- TABLE: seat_grades
-- Description: Stores seat grade information (pricing tiers)
-- =============================================================================

CREATE TABLE seat_grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grade_code VARCHAR(10) NOT NULL UNIQUE,
    grade_name VARCHAR(50) NOT NULL,
    start_row INTEGER NOT NULL,
    end_row INTEGER,  -- NULL means "to the end"
    price INTEGER NOT NULL,  -- Price in Korean Won
    color_code VARCHAR(10) NOT NULL,  -- Hex color code
    display_order INTEGER NOT NULL,  -- Display order (1, 2, 3, 4)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Check constraints
    CONSTRAINT chk_seat_grades_start_row
        CHECK (start_row >= 1 AND start_row <= 20),
    CONSTRAINT chk_seat_grades_end_row
        CHECK (end_row IS NULL OR (end_row >= start_row AND end_row <= 20)),
    CONSTRAINT chk_seat_grades_price
        CHECK (price > 0),
    CONSTRAINT chk_seat_grades_display_order
        CHECK (display_order > 0)
);

-- Index for performance
CREATE INDEX idx_seat_grades_display_order ON seat_grades(display_order);

-- Add trigger for updated_at
CREATE TRIGGER update_seat_grades_updated_at
    BEFORE UPDATE ON seat_grades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE seat_grades IS 'Seat grade pricing tiers';
COMMENT ON COLUMN seat_grades.grade_code IS 'Grade code (S, P, A, R)';
COMMENT ON COLUMN seat_grades.end_row IS 'End row (NULL means to the last row)';
COMMENT ON COLUMN seat_grades.price IS 'Price in Korean Won';
COMMENT ON COLUMN seat_grades.color_code IS 'Hex color code for UI';
```

### 1.2 시드 데이터 삽입

```sql
-- Insert seat grade data
INSERT INTO seat_grades (grade_code, grade_name, start_row, end_row, price, color_code, display_order)
VALUES
    ('S', 'Special', 1, 3, 250000, '#9333EA', 1),
    ('P', 'Premium', 4, 7, 190000, '#0EA5E9', 2),
    ('A', 'Advanced', 8, 15, 170000, '#10B981', 3),
    ('R', 'Regular', 16, 20, 140000, '#F97316', 4);
```

### 1.3 좌석 등급 계산 함수

```sql
-- =============================================================================
-- FUNCTION: get_seat_grade
-- Description: Returns seat grade code based on row number
-- =============================================================================

CREATE OR REPLACE FUNCTION get_seat_grade(p_row INTEGER)
RETURNS VARCHAR(10) AS $$
DECLARE
    v_grade_code VARCHAR(10);
BEGIN
    SELECT grade_code INTO v_grade_code
    FROM seat_grades
    WHERE p_row >= start_row
      AND (end_row IS NULL OR p_row <= end_row)
    ORDER BY start_row DESC
    LIMIT 1;

    RETURN v_grade_code;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION get_seat_grade(INTEGER) IS 'Returns seat grade code based on row number';
```

### 1.4 마이그레이션 파일

**파일 경로**: `supabase/migrations/0004_add_seat_grades.sql`

위의 모든 SQL을 하나의 마이그레이션 파일로 작성합니다.

---

## 🔧 2. 백엔드 변경사항

### 2.1 Schema 수정 (`src/features/bookings/backend/schema.ts`)

#### 2.1.1 SeatGrade 스키마 추가

```typescript
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
```

#### 2.1.2 기존 Seat 스키마 수정

```typescript
export const SeatSchema = z.object({
  id: z.string().uuid(),
  section: z.enum(['A', 'B', 'C', 'D']),
  row: z.number().int().min(1).max(20),
  seatColumn: z.number().int().min(1).max(4),
  isReserved: z.boolean(),
  gradeCode: z.string(),      // 추가
  gradeName: z.string(),       // 추가
  price: z.number().int(),     // 추가
  colorCode: z.string(),       // 추가
});
```

#### 2.1.3 SeatsResponse 스키마 수정

```typescript
export const SeatsResponseSchema = z.object({
  concertId: z.string().uuid(),
  concertTitle: z.string(),
  eventDate: z.string(),
  totalSeats: z.number().int().min(0),
  availableSeats: z.number().int().min(0),
  sections: z.array(
    z.object({
      name: z.enum(['A', 'B', 'C', 'D']),
      seats: z.array(SeatSchema),
    }),
  ),
  grades: z.array(SeatGradeSchema),  // 추가: 등급 정보
  gradeAvailability: z.array(         // 추가: 등급별 잔여 좌석
    z.object({
      gradeCode: z.string(),
      gradeName: z.string(),
      price: z.number().int(),
      totalSeats: z.number().int(),
      availableSeats: z.number().int(),
      colorCode: z.string(),
    }),
  ),
});
```

#### 2.1.4 BookingSummary 스키마 수정 (예약 조회/완료)

```typescript
export const BookingSummarySchema = z.object({
  // ... 기존 필드 ...
  seats: z.array(
    z.object({
      section: z.enum(['A', 'B', 'C', 'D']),
      row: z.number().int(),
      seatColumn: z.number().int(),
      gradeCode: z.string(),      // 추가
      gradeName: z.string(),       // 추가
      price: z.number().int(),     // 추가
    }),
  ),
  totalAmount: z.number().int(),   // 추가: 총 금액
  // ... 기존 필드 ...
});
```

### 2.2 Service 수정 (`src/features/bookings/backend/service.ts`)

#### 2.2.1 getConcertSeats 함수 수정

```typescript
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

  // 2. 좌석 등급 정보 조회 (새로 추가)
  const { data: grades, error: gradesError } = await client
    .from('seat_grades')
    .select('*')
    .order('display_order');

  if (gradesError) {
    return failure(500, bookingErrorCodes.seatsFetchError, gradesError.message);
  }

  // 3. 좌석 목록 조회 (등급 정보 JOIN)
  const { data: seats, error: seatsError } = await client
    .from('seats')
    .select(`
      id,
      section,
      row,
      seat_column,
      is_reserved
    `)
    .eq('concert_id', concertId)
    .order('section')
    .order('row')
    .order('seat_column');

  if (seatsError || !seats || seats.length === 0) {
    return failure(500, bookingErrorCodes.seatsFetchError, 'No seats found.');
  }

  // 4. 좌석에 등급 정보 매핑
  const seatsWithGrade = seats.map((seat) => {
    const grade = grades.find(
      (g) =>
        seat.row >= g.start_row &&
        (g.end_row === null || seat.row <= g.end_row),
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

  // 6. 등급별 잔여 좌석 계산 (새로 추가)
  const gradeAvailability = grades.map((grade) => {
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
    grades: grades.map((g) => ({
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
```

#### 2.2.2 getBookingDetail 함수 수정 (예약 완료 페이지)

좌석 정보 조회 시 등급 및 가격 정보를 포함하도록 수정:

```typescript
// 좌석 정보 조회 부분 수정
const { data: bookingSeats, error: seatsError } = await client
  .from('booking_seats')
  .select(`
    seats (
      section,
      row,
      seat_column
    )
  `)
  .eq('booking_id', bookingId);

// 좌석에 등급 정보 추가
const { data: grades } = await client
  .from('seat_grades')
  .select('*')
  .order('display_order');

const seatsWithPrice = (bookingSeats || []).map((bs: any) => {
  const seat = bs.seats;
  const grade = grades?.find(
    (g) =>
      seat.row >= g.start_row &&
      (g.end_row === null || seat.row <= g.end_row),
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

// response 객체에 추가
const response: BookingDetailResponse = {
  // ... 기존 필드 ...
  seats: seatsWithPrice,
  totalAmount,
  // ... 기존 필드 ...
};
```

#### 2.2.3 lookupBookings 함수 수정 (예약 조회 페이지)

동일하게 좌석 정보에 등급 및 가격 정보를 포함하도록 수정합니다.

### 2.3 콘서트 상세 조회 수정 (`src/features/concerts/backend/service.ts`)

#### getConcertDetail 함수 수정

등급별 잔여 좌석 정보를 포함하도록 수정:

```typescript
export const getConcertDetail = async (
  client: SupabaseClient,
  concertId: string,
): Promise<HandlerResult<ConcertDetailResponse, ConcertServiceError, unknown>> => {
  // ... 기존 콘서트 조회 로직 ...

  // 좌석 등급 정보 조회
  const { data: grades } = await client
    .from('seat_grades')
    .select('*')
    .order('display_order');

  // 좌석 정보 조회
  const { data: seats } = await client
    .from('seats')
    .select('id, row, is_reserved')
    .eq('concert_id', concertId);

  // 등급별 잔여 좌석 계산
  const gradeAvailability = (grades || []).map((grade) => {
    const gradeSeats = (seats || []).filter(
      (s) =>
        s.row >= grade.start_row &&
        (grade.end_row === null || s.row <= grade.end_row),
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

  const response: ConcertDetailResponse = {
    // ... 기존 필드 ...
    gradeAvailability,  // 추가
  };

  return success(response);
};
```

### 2.4 Schema 수정 (`src/features/concerts/backend/schema.ts`)

```typescript
export const ConcertDetailResponseSchema = z.object({
  // ... 기존 필드 ...
  gradeAvailability: z.array(
    z.object({
      gradeCode: z.string(),
      gradeName: z.string(),
      price: z.number().int(),
      totalSeats: z.number().int(),
      availableSeats: z.number().int(),
      colorCode: z.string(),
    }),
  ),  // 추가
});
```

---

## 🎨 3. 프론트엔드 변경사항

### 3.1 좌석 선택 페이지

#### 3.1.1 SeatCard 컴포넌트 수정

**파일**: `src/features/bookings/components/SeatCard.tsx`

```typescript
'use client';

import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import type { Seat } from '../backend/schema';
import { cn } from '@/lib/utils';

interface SeatCardProps {
  seat: Seat;
}

export const SeatCard = ({ seat }: SeatCardProps) => {
  const { addSeat, removeSeat, isSeatSelected, canSelectMore } = useSeatSelectionStore();

  const isSelected = isSeatSelected(seat.id);
  const isReserved = seat.isReserved;
  const isClickable = !isReserved;

  const handleClick = () => {
    if (isReserved) return;

    if (isSelected) {
      removeSeat(seat.id);
    } else {
      if (canSelectMore()) {
        addSeat(seat);
      } else {
        alert('최대 4석까지만 선택할 수 있습니다.');
      }
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={!isClickable}
      className={cn(
        'aspect-square rounded text-xs font-medium transition-all',
        'border-2',
        isReserved && 'bg-gray-400 border-gray-500 cursor-not-allowed',
        !isReserved &&
          !isSelected &&
          'bg-white cursor-pointer hover:shadow-md',
        isSelected && 'bg-blue-500 text-white cursor-pointer',
      )}
      style={{
        // 등급별 색상을 border에 적용 (예약되지 않은 경우)
        borderColor: !isReserved && !isSelected ? seat.colorCode : undefined,
        borderWidth: !isReserved && !isSelected ? '3px' : undefined,
      }}
      aria-label={`${seat.section}구역 ${seat.row}행 ${seat.seatColumn}열 ${seat.gradeName} ${
        isReserved ? '예약됨' : isSelected ? '선택됨' : '예약 가능'
      }`}
    >
      {seat.row}-{seat.seatColumn}
    </button>
  );
};
```

#### 3.1.2 등급 정보 표시 컴포넌트 추가

**파일**: `src/features/bookings/components/SeatGradeLegend.tsx`

```typescript
'use client';

import type { SeatGrade } from '../backend/schema';

interface SeatGradeLegendProps {
  grades: SeatGrade[];
  gradeAvailability: Array<{
    gradeCode: string;
    gradeName: string;
    price: number;
    totalSeats: number;
    availableSeats: number;
    colorCode: string;
  }>;
}

export const SeatGradeLegend = ({ grades, gradeAvailability }: SeatGradeLegendProps) => {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm mb-4">
      <h3 className="font-bold text-sm mb-3">등급별 가격 안내</h3>
      <div className="space-y-2">
        {gradeAvailability.map((availability) => {
          const grade = grades.find((g) => g.gradeCode === availability.gradeCode);
          if (!grade) return null;

          return (
            <div
              key={availability.gradeCode}
              className="flex items-center justify-between text-sm"
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded border-2"
                  style={{ borderColor: availability.colorCode }}
                />
                <span className="font-medium">{availability.gradeName}</span>
                <span className="text-gray-500 text-xs">
                  ({grade.startRow}~{grade.endRow || 20}행)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold">
                  {availability.price.toLocaleString()}원
                </span>
                <span className="text-gray-600 text-xs">
                  {availability.availableSeats}/{availability.totalSeats}석
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
```

#### 3.1.3 선택 좌석 사이드바 수정

**파일**: `src/features/bookings/components/SeatSelectionSidebar.tsx`

```typescript
'use client';

import { X } from 'lucide-react';
import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';
import type { Seat } from '../backend/schema';

interface SeatSelectionSidebarProps {
  selectedSeats: Seat[];
  availableSeats: number;
  totalSeats: number;
}

export const SeatSelectionSidebar = ({
  selectedSeats,
  availableSeats,
  totalSeats,
}: SeatSelectionSidebarProps) => {
  const { removeSeat } = useSeatSelectionStore();

  // 선택된 좌석의 총 금액 계산
  const totalAmount = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm sticky top-4">
      <h3 className="font-bold text-lg mb-2">선택된 좌석</h3>
      <p className="text-sm text-gray-600 mb-4">
        남은 좌석: {availableSeats}/{totalSeats}석
      </p>

      {selectedSeats.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <p>좌석을 선택해주세요</p>
          <p className="text-xs mt-1">최대 4석까지 선택 가능</p>
        </div>
      )}

      {selectedSeats.length > 0 && (
        <>
          <ul className="space-y-2 mb-4">
            {selectedSeats.map((seat) => (
              <li
                key={seat.id}
                className="flex items-center justify-between bg-gray-50 rounded px-3 py-2"
              >
                <div className="flex flex-col">
                  <span className="text-sm font-medium">
                    {seat.section}구역 {seat.row}행 {seat.seatColumn}열
                  </span>
                  <span className="text-xs text-gray-600">
                    {seat.gradeName} - {seat.price.toLocaleString()}원
                  </span>
                </div>
                <button
                  onClick={() => removeSeat(seat.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                  aria-label={`${seat.section}구역 ${seat.row}행 ${seat.seatColumn}열 선택 해제`}
                >
                  <X className="w-4 h-4" />
                </button>
              </li>
            ))}
          </ul>

          {/* 총 금액 표시 */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <span className="font-bold text-lg">총 금액</span>
              <span className="font-bold text-xl text-blue-600">
                {totalAmount.toLocaleString()}원
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
```

#### 3.1.4 좌석 선택 단계 컴포넌트 수정

**파일**: `src/features/bookings/components/SeatSelectionStep.tsx`

```typescript
// ... 기존 imports ...
import { SeatGradeLegend } from './SeatGradeLegend';

export const SeatSelectionStep = ({ concertId, onProceed }: SeatSelectionStepProps) => {
  const { data, isLoading, isError, error } = useConcertSeats(concertId);
  const { selectedSeats } = useSeatSelectionStore();

  // ... 로딩/에러 처리 ...

  if (!data) return null;

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">{data.concertTitle} - 좌석 선택</h1>
        <p className="text-sm text-gray-600 mt-1">
          남은 좌석: {data.availableSeats}/{data.totalSeats}석
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 좌석 배치도 */}
        <div className="lg:col-span-2">
          {/* 등급 범례 추가 */}
          <SeatGradeLegend
            grades={data.grades}
            gradeAvailability={data.gradeAvailability}
          />

          <SeatMap sections={data.sections} />
        </div>

        {/* 사이드바 */}
        <div className="lg:col-span-1">
          <SeatSelectionSidebar
            selectedSeats={selectedSeats}
            availableSeats={data.availableSeats}
            totalSeats={data.totalSeats}
          />

          <Button
            className="w-full mt-4"
            disabled={selectedSeats.length === 0}
            onClick={onProceed}
            size="lg"
          >
            예약하기 ({selectedSeats.length}석 선택)
          </Button>
        </div>
      </div>
    </div>
  );
};
```

### 3.2 콘서트 상세 페이지

#### 3.2.1 등급별 잔여 좌석 표시 컴포넌트 추가

**파일**: `src/features/concerts/components/concert-grade-availability.tsx`

```typescript
'use client';

interface GradeAvailability {
  gradeCode: string;
  gradeName: string;
  price: number;
  totalSeats: number;
  availableSeats: number;
  colorCode: string;
}

interface ConcertGradeAvailabilityProps {
  gradeAvailability: GradeAvailability[];
}

export const ConcertGradeAvailability = ({
  gradeAvailability,
}: ConcertGradeAvailabilityProps) => {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-bold mb-4">등급별 잔여 좌석</h3>
      <div className="space-y-3">
        {gradeAvailability.map((grade) => {
          const occupancyRate =
            (grade.totalSeats - grade.availableSeats) / grade.totalSeats;
          const isSoldOut = grade.availableSeats === 0;

          return (
            <div key={grade.gradeCode} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: grade.colorCode }}
                  />
                  <span className="font-medium">{grade.gradeName}</span>
                  <span className="text-sm text-gray-600">
                    {grade.price.toLocaleString()}원
                  </span>
                </div>
                <div className="text-sm">
                  {isSoldOut ? (
                    <span className="text-red-600 font-semibold">매진</span>
                  ) : (
                    <span className="text-gray-700">
                      {grade.availableSeats}/{grade.totalSeats}석
                    </span>
                  )}
                </div>
              </div>
              {/* 진행률 바 */}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${occupancyRate * 100}%`,
                    backgroundColor: grade.colorCode,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
```

#### 3.2.2 콘서트 상세 뷰 수정

**파일**: `src/features/concerts/components/concert-detail-view.tsx`

```typescript
// ... 기존 imports ...
import { ConcertGradeAvailability } from './concert-grade-availability';

export const ConcertDetailView = ({ concertId }: ConcertDetailViewProps) => {
  // ... 기존 로직 ...

  if (!data) return null;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* ... 기존 콘서트 정보 ... */}

      {/* 등급별 잔여 좌석 추가 */}
      <ConcertGradeAvailability gradeAvailability={data.gradeAvailability} />

      {/* ... 나머지 컴포넌트 ... */}
    </div>
  );
};
```

### 3.3 예약 완료 페이지

#### 3.3.1 좌석 목록 컴포넌트 수정

**파일**: `src/features/bookings/components/BookingSeatsList.tsx`

```typescript
'use client';

import { Armchair } from 'lucide-react';

interface Seat {
  section: 'A' | 'B' | 'C' | 'D';
  row: number;
  seatColumn: number;
  gradeCode: string;
  gradeName: string;
  price: number;
}

interface BookingSeatsListProps {
  seats: Seat[];
  totalAmount: number;
}

export const BookingSeatsList = ({ seats, totalAmount }: BookingSeatsListProps) => {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Armchair className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">예약된 좌석 ({seats.length}석)</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        {seats.map((seat, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-4 py-3"
          >
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-gray-900">
                {seat.section}구역 {seat.row}행 {seat.seatColumn}열
              </span>
              <span className="text-xs text-gray-600">{seat.gradeName}</span>
            </div>
            <span className="text-sm font-medium text-blue-700">
              {seat.price.toLocaleString()}원
            </span>
          </div>
        ))}
      </div>

      {/* 총 금액 */}
      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold">총 결제 금액</span>
          <span className="text-2xl font-bold text-blue-600">
            {totalAmount.toLocaleString()}원
          </span>
        </div>
      </div>
    </div>
  );
};
```

#### 3.3.2 예약 완료 컨테이너 수정

**파일**: `src/features/bookings/components/BookingCompleteContainer.tsx`

좌석 데이터에 등급 정보가 포함되므로 `totalAmount`를 props로 전달하도록 수정합니다.

### 3.4 예약 조회 페이지

#### 3.4.1 예약 카드 컴포넌트 수정

**파일**: `src/features/bookings/components/BookingCard.tsx`

예약 완료 페이지와 동일하게 좌석별 등급 및 가격 정보를 표시하도록 수정합니다.

```typescript
// seats 섹션 수정
<div className="mt-4 pt-4 border-t border-gray-200">
  <h4 className="text-sm font-semibold text-gray-700 mb-2">
    예약된 좌석 ({booking.seats.length}석)
  </h4>
  <div className="space-y-2">
    {booking.seats.map((seat, index) => (
      <div
        key={index}
        className="flex items-center justify-between bg-gray-50 rounded px-3 py-2"
      >
        <span className="text-sm">
          {seat.section}구역 {seat.row}행 {seat.seatColumn}열
          <span className="text-xs text-gray-600 ml-2">({seat.gradeName})</span>
        </span>
        <span className="text-sm font-medium">
          {seat.price.toLocaleString()}원
        </span>
      </div>
    ))}
  </div>

  {/* 총 금액 */}
  <div className="mt-3 pt-3 border-t flex items-center justify-between">
    <span className="font-semibold">총 금액</span>
    <span className="text-lg font-bold text-blue-600">
      {booking.totalAmount.toLocaleString()}원
    </span>
  </div>
</div>
```

---

## 📝 4. 문서 업데이트

### 4.1 업데이트할 문서 목록

1. **PRD** (`docs/prd.md`)
   - 좌석 등급 시스템 추가
   - 가격 정보 명시

2. **Database 설계** (`docs/database.md`)
   - `seat_grades` 테이블 추가

3. **유스케이스** (`docs/usecases/`)
   - UF-001: 콘서트 목록 조회 (등급별 가격 정보)
   - UF-002: 콘서트 상세 조회 (등급별 잔여 좌석)
   - UF-003: 좌석 선택 (등급 색상 표시, 가격 정보)
   - UF-005: 예약 정보 입력 및 제출 (총 금액 계산)
   - UF-006: 예약 조회 (좌석별 가격 표시)

4. **페이지 계획 문서** (`docs/pages/`)
   - `concert-detail/plan.md`
   - `concert-booking/plan.md`
   - `booking-complete/plan.md`
   - `booking-lookup/plan.md`

5. **검증 보고서** (`usecase-checker.md`)
   - 좌석 등급 기능 추가 반영

---

## 🔍 5. 구현 우선순위 및 단계

### Phase 1: 데이터베이스 (최우선)
- [ ] 마이그레이션 파일 작성 (`0004_add_seat_grades.sql`)
- [ ] Supabase에 마이그레이션 적용
- [ ] 시드 데이터 확인

### Phase 2: 백엔드 API (우선순위: 높음)
- [ ] Schema 수정 (SeatGrade, Seat, SeatsResponse, BookingSummary 등)
- [ ] Service 함수 수정 (getConcertSeats, getBookingDetail, lookupBookings, getConcertDetail)
- [ ] Route Handler 테스트

### Phase 3: 프론트엔드 컴포넌트 (우선순위: 중간)
- [ ] 좌석 선택 페이지
  - [ ] SeatCard 수정 (등급별 색상 border)
  - [ ] SeatGradeLegend 컴포넌트 추가
  - [ ] SeatSelectionSidebar 수정 (총 금액 표시)
  - [ ] SeatSelectionStep 수정
- [ ] 콘서트 상세 페이지
  - [ ] ConcertGradeAvailability 컴포넌트 추가
  - [ ] concert-detail-view 수정
- [ ] 예약 완료 페이지
  - [ ] BookingSeatsList 수정 (등급 및 가격 표시)
- [ ] 예약 조회 페이지
  - [ ] BookingCard 수정 (등급 및 가격 표시)

### Phase 4: 테스트 (우선순위: 높음)
- [ ] 백엔드 Unit Tests
  - [ ] Schema 테스트 (SeatGradeSchema)
  - [ ] Service 테스트 (등급 정보 포함 여부)
- [ ] 프론트엔드 Component Tests
  - [ ] SeatCard 테스트 (등급 색상 표시)
  - [ ] SeatGradeLegend 테스트
  - [ ] 총 금액 계산 테스트
- [ ] E2E Tests (Playwright)
  - [ ] 좌석 선택 시 등급 색상 확인
  - [ ] 선택 좌석 총 금액 계산 확인
  - [ ] 예약 완료 후 금액 표시 확인

### Phase 5: 문서화 (우선순위: 낮음)
- [ ] PRD 업데이트
- [ ] 유스케이스 업데이트
- [ ] 페이지 계획 문서 업데이트
- [ ] 검증 보고서 업데이트

---

## ⚠️ 주의사항

### 1. 데이터 일관성
- 기존 좌석 데이터는 row 번호를 기준으로 등급이 자동 결정됩니다.
- `get_seat_grade(row)` 함수를 사용하여 동적으로 등급을 계산합니다.

### 2. 가격 변경 유연성
- 좌석 등급 가격은 `seat_grades` 테이블에서 관리되므로, 향후 가격 변경 시 테이블만 업데이트하면 됩니다.
- 단, 이미 완료된 예약의 가격은 변경되지 않도록 주의해야 합니다 (필요 시 booking_seats 테이블에 price 컬럼 추가 고려).

### 3. 성능 최적화
- 좌석 조회 시 등급 정보 JOIN이 추가되므로, 적절한 인덱싱이 필요합니다.
- 캐싱 전략 고려 (등급 정보는 자주 변하지 않으므로 캐싱 가능).

### 4. 백워드 호환성
- 기존 API 응답에 등급 정보가 추가되므로, 프론트엔드 업데이트 전까지 optional 처리 필요.
- Zod 스키마에서 `.optional()` 또는 `.nullable()`로 처리할 수 있습니다.

### 5. 총 금액 계산
- 예약 생성 시 총 금액을 저장할지, 조회 시 계산할지 결정 필요.
- **권장**: 예약 시점의 가격을 `booking_seats` 테이블에 저장하여 향후 가격 변경 시에도 과거 예약 금액이 변하지 않도록 합니다.

---

## 📊 예상 구현 시간

| 작업 | 예상 시간 |
|------|----------|
| 데이터베이스 마이그레이션 | 1시간 |
| 백엔드 API 수정 | 4시간 |
| 백엔드 Unit Tests | 2시간 |
| 프론트엔드 컴포넌트 수정 | 6시간 |
| 프론트엔드 Component Tests | 2시간 |
| E2E Tests | 2시간 |
| 문서 업데이트 | 2시간 |
| QA & Bug Fix | 3시간 |
| **총계** | **22시간** |

---

## ✅ 완료 체크리스트

### 데이터베이스
- [ ] `seat_grades` 테이블 생성
- [ ] 시드 데이터 삽입 (S, P, A, R)
- [ ] `get_seat_grade()` 함수 생성
- [ ] 마이그레이션 Supabase 적용

### 백엔드
- [ ] SeatGrade 스키마 추가
- [ ] Seat 스키마 수정 (gradeCode, price 등 추가)
- [ ] SeatsResponse 스키마 수정 (grades, gradeAvailability 추가)
- [ ] BookingSummary 스키마 수정 (totalAmount 추가)
- [ ] ConcertDetailResponse 스키마 수정 (gradeAvailability 추가)
- [ ] getConcertSeats 함수 수정
- [ ] getBookingDetail 함수 수정
- [ ] lookupBookings 함수 수정
- [ ] getConcertDetail 함수 수정
- [ ] 백엔드 Unit Tests 작성

### 프론트엔드
- [ ] SeatCard 수정 (등급별 색상 border)
- [ ] SeatGradeLegend 컴포넌트 추가
- [ ] SeatSelectionSidebar 수정 (총 금액 표시)
- [ ] SeatSelectionStep 수정
- [ ] ConcertGradeAvailability 컴포넌트 추가
- [ ] concert-detail-view 수정
- [ ] BookingSeatsList 수정 (등급 및 가격 표시)
- [ ] BookingCard 수정 (예약 조회)
- [ ] 프론트엔드 Component Tests 작성

### 테스트
- [ ] E2E Tests 실행 및 수정
- [ ] 통합 테스트 (전체 예약 플로우)
- [ ] 금액 계산 정확성 검증

### 문서
- [ ] PRD 업데이트
- [ ] 유스케이스 업데이트
- [ ] 페이지 계획 문서 업데이트
- [ ] usecase-checker.md 업데이트

---

## 🚀 배포 전 확인사항

1. ✅ Supabase 마이그레이션 적용 완료
2. ✅ 시드 데이터 (좌석 등급) 삽입 완료
3. ✅ 백엔드 API 테스트 통과
4. ✅ 프론트엔드 UI 테스트 통과
5. ✅ E2E 테스트 통과 (좌석 선택 → 예약 → 완료)
6. ✅ 금액 계산 정확성 검증
7. ✅ 반응형 디자인 확인 (모바일/데스크톱)
8. ✅ 접근성 확인 (색상 대비, 스크린 리더)

---

**문서 버전**: 1.0
**최종 수정일**: 2025-10-13
**작성자**: Development Team
**검토 필요**: 좌석 등급 가격 정책, 총 금액 저장 방식
