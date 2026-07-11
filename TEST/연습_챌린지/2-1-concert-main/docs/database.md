# 데이터베이스 설계

## 개요
콘서트 예약 플랫폼의 PostgreSQL 데이터베이스 스키마 및 데이터 플로우 설계서입니다.
유저플로우에 명시된 데이터만 포함하여 최소 스펙으로 구성되었습니다.

---

## 데이터 플로우 요약

### 1. 콘서트 목록 조회
```
READ: concerts → 진행일 필터링 → 좌석 집계 (seats) → 응답
```

### 2. 콘서트 상세 조회
```
READ: concerts (by id) → 좌석 현황 집계 (seats) → 응답
```

### 3. 좌석 배치도 조회
```
READ: seats (by concert_id) → JOIN: seat_grades (등급 정보) → 상태별 필터링 → 응답
```

### 4. 예약 생성
```
BEGIN TRANSACTION
  READ: concerts (검증)
  READ: seats FOR UPDATE (Lock)
  JOIN: seat_grades (가격 계산)
  CHECK: 좌석 상태 검증
  INSERT: bookings
  INSERT: booking_seats (N개)
  UPDATE: seats.is_reserved = true (N개)
COMMIT
```

### 5. 예약 조회
```
READ: bookings (by phone) → 비밀번호 검증 →
JOIN: concerts, booking_seats, seats, seat_grades → 응답
```

### 6. 예약 취소
```
BEGIN TRANSACTION
  READ: bookings (by id) → 상태 검증
  UPDATE: bookings.status = 'cancelled'
  UPDATE: seats.is_reserved = false (해당 예약의 좌석들)
  DELETE: booking_seats (선택사항)
COMMIT
```

---

## 엔티티 관계 다이어그램 (ERD)

```
┌─────────────────┐
│   concerts      │
│─────────────────│
│ id (PK)         │
│ title           │
│ description     │
│ event_date      │
│ location        │
│ thumbnail_url   │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   seats         │
│─────────────────│
│ id (PK)         │
│ concert_id (FK) │◄──────┐
│ section         │        │
│ row             │        │ (row → get_seat_grade() → grade_code)
│ seat_column     │        │
│ is_reserved     │        │
│ created_at      │        │
│ updated_at      │        │
└─────────────────┘        │
         │                 │
         │ N:M             │
         │ (through)       │
         ▼                 │
┌─────────────────┐        │
│ booking_seats   │        │
│─────────────────│        │
│ id (PK)         │        │
│ booking_id (FK) │        │
│ seat_id (FK)    │────────┘
│ created_at      │
└─────────────────┘
         ▲
         │ N:1
         │
┌─────────────────┐
│   bookings      │
│─────────────────│
│ id (PK)         │
│ concert_id (FK) │
│ name            │
│ phone           │
│ password_hash   │
│ status          │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌─────────────────────┐
│   seat_grades       │
│─────────────────────│
│ id (PK)             │
│ grade_code (UQ)     │ (S, P, A, R)
│ grade_name          │
│ start_row           │
│ end_row             │
│ price               │
│ color_code          │
│ display_order       │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

---

## 테이블 스키마 상세

### 1. concerts (콘서트)

콘서트 기본 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 콘서트 고유 ID |
| title | VARCHAR(255) | NOT NULL | 콘서트 제목 |
| description | TEXT | NULL | 콘서트 상세 설명 |
| event_date | TIMESTAMPTZ | NOT NULL | 콘서트 진행 일시 |
| location | VARCHAR(255) | NOT NULL | 공연 장소 |
| thumbnail_url | TEXT | NULL | 썸네일 이미지 URL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성 일시 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 수정 일시 |

**인덱스:**
- `idx_concerts_event_date`: `(event_date)` - 날짜 기반 필터링 성능 향상

**비즈니스 룰:**
- 예약 가능 기간: `event_date - 1 day 23:59:59` 까지
- 총 좌석 수: 320석 (고정, seats 테이블에서 집계)

---

### 2. seats (좌석)

각 콘서트의 개별 좌석 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 좌석 고유 ID |
| concert_id | UUID | NOT NULL, FOREIGN KEY → concerts(id) ON DELETE CASCADE | 콘서트 ID |
| section | CHAR(1) | NOT NULL, CHECK (section IN ('A', 'B', 'C', 'D')) | 구역 (A, B, C, D) |
| row | INTEGER | NOT NULL, CHECK (row >= 1 AND row <= 20) | 행 (1-20) |
| seat_column | INTEGER | NOT NULL, CHECK (seat_column >= 1 AND seat_column <= 4) | 열 (1-4) |
| is_reserved | BOOLEAN | NOT NULL, DEFAULT FALSE | 예약 여부 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성 일시 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 수정 일시 |

**인덱스:**
- `idx_seats_concert_id`: `(concert_id)` - 콘서트별 좌석 조회
- `idx_seats_concert_reserved`: `(concert_id, is_reserved)` - 예약 가능 좌석 필터링
- `idx_seats_unique_position`: UNIQUE `(concert_id, section, row, seat_column)` - 좌석 위치 중복 방지

**비즈니스 룰:**
- 각 콘서트당 320석: 4개 구역(A,B,C,D) × 20행 × 4열
- `is_reserved = false`: 예약 가능
- `is_reserved = true`: 예약됨
- 좌석 등급은 `get_seat_grade(row)` 함수를 통해 계산됨

---

### 3. bookings (예약)

예약 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 예약 고유 ID |
| concert_id | UUID | NOT NULL, FOREIGN KEY → concerts(id) ON DELETE RESTRICT | 콘서트 ID |
| name | VARCHAR(100) | NOT NULL | 예약자명 |
| phone | VARCHAR(20) | NOT NULL | 휴대폰번호 (암호화 가능) |
| password_hash | VARCHAR(255) | NOT NULL | 비밀번호 해시 (bcrypt) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'confirmed', CHECK (status IN ('confirmed', 'cancelled')) | 예약 상태 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 예약 생성 일시 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 수정 일시 |

**인덱스:**
- `idx_bookings_phone`: `(phone)` - 휴대폰번호 기반 조회
- `idx_bookings_concert_id`: `(concert_id)` - 콘서트별 예약 조회
- `idx_bookings_status`: `(status)` - 상태별 필터링
- `idx_bookings_phone_status`: `(phone, status)` - 예약 조회 시 성능 최적화

**비즈니스 룰:**
- 비밀번호는 4자리 숫자이지만 bcrypt 해싱 저장
- status: `confirmed` (확정), `cancelled` (취소)
- 한 예약당 최대 4개 좌석

---

### 4. booking_seats (예약-좌석 연결)

예약과 좌석의 다대다 관계를 나타내는 중간 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 레코드 고유 ID |
| booking_id | UUID | NOT NULL, FOREIGN KEY → bookings(id) ON DELETE CASCADE | 예약 ID |
| seat_id | UUID | NOT NULL, FOREIGN KEY → seats(id) ON DELETE RESTRICT | 좌석 ID |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성 일시 |

**인덱스:**
- `idx_booking_seats_booking_id`: `(booking_id)` - 예약별 좌석 조회
- `idx_booking_seats_seat_id`: `(seat_id)` - 좌석별 예약 조회
- `idx_booking_seats_unique`: UNIQUE `(booking_id, seat_id)` - 중복 연결 방지

**비즈니스 룰:**
- 하나의 booking은 1-4개의 seat와 연결
- 예약 취소 시 CASCADE로 자동 삭제 (또는 유지하고 booking.status로 관리)

---

### 5. seat_grades (좌석 등급)

좌석 등급별 가격 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약조건 | 설명 |
|--------|------------|---------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 레코드 고유 ID |
| grade_code | VARCHAR(10) | NOT NULL, UNIQUE | 등급 코드 (S, P, A, R) |
| grade_name | VARCHAR(50) | NOT NULL | 등급 이름 (Special, Premium, Advanced, Regular) |
| start_row | INTEGER | NOT NULL, CHECK (start_row >= 1 AND start_row <= 20) | 시작 행 번호 |
| end_row | INTEGER | NULL, CHECK (end_row IS NULL OR (end_row >= start_row AND end_row <= 20)) | 종료 행 번호 (NULL = 마지막 행까지) |
| price | INTEGER | NOT NULL, CHECK (price > 0) | 가격 (원) |
| color_code | VARCHAR(10) | NOT NULL | UI 표시용 컬러 코드 (Hex) |
| display_order | INTEGER | NOT NULL, CHECK (display_order > 0) | 표시 순서 (1 = 최고 등급) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성 일시 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 수정 일시 |

**인덱스:**
- `idx_seat_grades_display_order`: `(display_order)` - 정렬 최적화
- `idx_seat_grades_row_range`: `(start_row, end_row)` - 행 범위 검색 최적화

**비즈니스 룰:**
- S (Special): 1-3행, 250,000원, 보라색 (#9333EA)
- P (Premium): 4-7행, 190,000원, 하늘색 (#0EA5E9)
- A (Advanced): 8-15행, 170,000원, 초록색 (#10B981)
- R (Regular): 16-20행, 140,000원, 주황색 (#F97316)

---

## 데이터베이스 함수

### 1. get_seat_grade(row)

좌석 행 번호를 받아 해당 등급 코드를 반환하는 함수입니다.

**시그니처:**
```sql
get_seat_grade(p_row INTEGER) RETURNS VARCHAR(10)
```

**동작:**
- 입력된 행 번호가 어느 등급 범위에 속하는지 확인
- 해당 등급 코드(S, P, A, R) 반환
- 매칭되지 않으면 기본값 'R' 반환

**사용 예시:**
```sql
SELECT get_seat_grade(1);   -- 'S'
SELECT get_seat_grade(5);   -- 'P'
SELECT get_seat_grade(10);  -- 'A'
SELECT get_seat_grade(18);  -- 'R'
```

---

## 뷰 (Views)

### 1. seat_grade_statistics

콘서트별 좌석 등급 통계를 제공하는 뷰입니다.

**컬럼:**
- `concert_id`: 콘서트 ID
- `concert_title`: 콘서트 제목
- `grade_code`: 등급 코드
- `grade_name`: 등급 이름
- `price`: 등급 가격
- `total_seats`: 해당 등급 전체 좌석 수
- `reserved_seats`: 예약된 좌석 수
- `available_seats`: 예약 가능한 좌석 수
- `occupancy_rate`: 예약률 (%)

**사용 예시:**
```sql
-- 특정 콘서트의 등급별 예약 현황 조회
SELECT * FROM seat_grade_statistics
WHERE concert_id = 'xxx-xxx-xxx'
ORDER BY display_order;
```

---

## 데이터 플로우 상세

### DF-001: 콘서트 목록 조회

**요청 데이터:** 없음

**처리 흐름:**
```sql
-- 1. 현재 날짜 기준 예약 가능한 콘서트 조회
SELECT
  c.id,
  c.title,
  c.event_date,
  c.location,
  c.thumbnail_url,
  COUNT(s.id) FILTER (WHERE s.is_reserved = false) as available_seats,
  COUNT(s.id) FILTER (WHERE s.is_reserved = true) as reserved_seats,
  COUNT(s.id) as total_seats
FROM concerts c
LEFT JOIN seats s ON c.id = s.concert_id
WHERE c.event_date > (NOW() + INTERVAL '1 day')
GROUP BY c.id
ORDER BY c.event_date ASC;
```

**응답 데이터:**
- 콘서트 목록 (id, title, event_date, location, thumbnail_url)
- 각 콘서트별: total_seats, reserved_seats, available_seats

---

### DF-002: 콘서트 상세 조회

**요청 데이터:** `concert_id`

**처리 흐름:**
```sql
-- 1. 콘서트 기본 정보 조회
SELECT
  c.*,
  COUNT(s.id) FILTER (WHERE s.is_reserved = false) as available_seats,
  COUNT(s.id) as total_seats
FROM concerts c
LEFT JOIN seats s ON c.id = s.concert_id
WHERE c.id = :concert_id
GROUP BY c.id;
```

**응답 데이터:**
- 콘서트 상세 정보 (title, description, event_date, location)
- available_seats, total_seats

---

### DF-003: 좌석 배치도 조회

**요청 데이터:** `concert_id`

**처리 흐름:**
```sql
-- 1. 해당 콘서트의 모든 좌석 조회 (등급 정보 포함)
SELECT
  s.id,
  s.section,
  s.row,
  s.seat_column,
  s.is_reserved,
  get_seat_grade(s.row) as grade_code,
  sg.grade_name,
  sg.price,
  sg.color_code
FROM seats s
LEFT JOIN seat_grades sg ON get_seat_grade(s.row) = sg.grade_code
WHERE s.concert_id = :concert_id
ORDER BY s.section, s.row, s.seat_column;
```

**응답 데이터:**
- 320개 좌석 정보 배열
- 각 좌석: id, section, row, seat_column, is_reserved, grade_code, grade_name, price, color_code

---

### DF-004: 예약 생성 (트랜잭션)

**요청 데이터:**
- `concert_id`
- `seat_ids[]` (1-4개)
- `name`
- `phone`
- `password` (해싱 전)

**처리 흐름:**
```sql
BEGIN;

-- 1. 콘서트 존재 및 예약 가능 여부 확인
SELECT id, event_date
FROM concerts
WHERE id = :concert_id
  AND event_date > (NOW() + INTERVAL '1 day')
FOR UPDATE;
-- 결과 없으면 ROLLBACK (예약 마감)

-- 2. 좌석 상태 확인 및 Lock (등급 정보 포함)
SELECT
  s.id,
  s.is_reserved,
  sg.price
FROM seats s
LEFT JOIN seat_grades sg ON get_seat_grade(s.row) = sg.grade_code
WHERE s.id = ANY(:seat_ids)
  AND s.concert_id = :concert_id
FOR UPDATE;
-- Row Lock 획득

-- 3. 좌석 예약 가능 여부 검증
-- 모든 is_reserved가 false여야 함
-- 하나라도 true면 ROLLBACK (중복 예약)

-- 4. 예약 레코드 생성
INSERT INTO bookings (concert_id, name, phone, password_hash, status)
VALUES (:concert_id, :name, :phone, :password_hash, 'confirmed')
RETURNING id;
-- booking_id 반환

-- 5. 예약-좌석 연결 생성
INSERT INTO booking_seats (booking_id, seat_id)
SELECT :booking_id, unnest(:seat_ids);

-- 6. 좌석 상태 업데이트
UPDATE seats
SET is_reserved = true, updated_at = NOW()
WHERE id = ANY(:seat_ids);

COMMIT;
```

**응답 데이터:**
- `booking_id`
- `total_amount` (선택된 좌석의 가격 합계)
- 성공 여부

**에러 케이스:**
- 콘서트 없음: 404
- 예약 마감: 400
- 좌석 중복 예약: 409
- 트랜잭션 실패: 500

---

### DF-005: 예약 조회

**요청 데이터:**
- `phone`
- `password` (해싱 전)

**처리 흐름:**
```sql
-- 1. 휴대폰번호로 예약 조회 및 비밀번호 검증
SELECT
  b.id,
  b.concert_id,
  b.name,
  b.status,
  b.created_at,
  c.title as concert_title,
  c.event_date,
  c.location
FROM bookings b
JOIN concerts c ON b.concert_id = c.id
WHERE b.phone = :phone
ORDER BY b.created_at DESC;

-- 2. 각 예약에 대해 비밀번호 검증 (애플리케이션 레벨)
-- bcrypt.compare(password, booking.password_hash)

-- 3. 비밀번호 일치하는 예약의 좌석 정보 조회 (가격 포함)
SELECT
  s.section,
  s.row,
  s.seat_column,
  sg.grade_code,
  sg.grade_name,
  sg.price
FROM booking_seats bs
JOIN seats s ON bs.seat_id = s.id
LEFT JOIN seat_grades sg ON get_seat_grade(s.row) = sg.grade_code
WHERE bs.booking_id = :booking_id
ORDER BY s.section, s.row, s.seat_column;
```

**응답 데이터:**
- 예약 목록 (booking_id, concert 정보, 예약자명, 예약 일시, 상태)
- 각 예약별 좌석 목록 (section, row, seat_column, grade_code, grade_name, price)
- 각 예약별 총 금액 (좌석 가격 합계)

---

### DF-006: 예약 취소 (트랜잭션)

**요청 데이터:**
- `booking_id`
- (선택) `phone`, `password` (재인증)

**처리 흐름:**
```sql
BEGIN;

-- 1. 예약 정보 조회 및 Lock
SELECT
  b.id,
  b.status,
  c.event_date
FROM bookings b
JOIN concerts c ON b.concert_id = c.id
WHERE b.id = :booking_id
FOR UPDATE;
-- 예약 없음: ROLLBACK (404)
-- 이미 취소됨: ROLLBACK (400)
-- 콘서트 시작됨: ROLLBACK (400)

-- 2. 예약 상태 업데이트
UPDATE bookings
SET status = 'cancelled', updated_at = NOW()
WHERE id = :booking_id;

-- 3. 해당 예약의 좌석 ID 조회
SELECT seat_id
FROM booking_seats
WHERE booking_id = :booking_id;

-- 4. 좌석 상태 복원
UPDATE seats
SET is_reserved = false, updated_at = NOW()
WHERE id IN (
  SELECT seat_id
  FROM booking_seats
  WHERE booking_id = :booking_id
);

-- 5. (선택사항) 예약-좌석 연결 삭제
-- DELETE FROM booking_seats WHERE booking_id = :booking_id;

COMMIT;
```

**응답 데이터:**
- 성공 여부

**에러 케이스:**
- 예약 없음: 404
- 이미 취소됨: 400
- 취소 불가 기간: 400
- 트랜잭션 실패: 500

---

## 동시성 제어

### Row-Level Locking

예약 생성 시 `SELECT ... FOR UPDATE`를 사용하여 동시성 문제를 방지합니다.

```sql
-- 좌석 Lock 획득
SELECT id, is_reserved
FROM seats
WHERE id = ANY(:seat_ids)
FOR UPDATE;
```

**동작 방식:**
1. 첫 번째 트랜잭션이 좌석에 Lock을 획득
2. 두 번째 트랜잭션은 Lock이 해제될 때까지 대기
3. Lock 해제 후 좌석 상태 재확인
4. 이미 예약된 경우 트랜잭션 롤백

### 트랜잭션 격리 수준

**권장:** `READ COMMITTED` (PostgreSQL 기본값)
- Dirty Read 방지
- Non-Repeatable Read 허용 (재검증으로 해결)
- FOR UPDATE로 충분한 동시성 제어 가능

---

## 인덱스 전략

### 성능 최적화 인덱스

```sql
-- 1. 콘서트 날짜 기반 필터링
CREATE INDEX idx_concerts_event_date ON concerts(event_date);

-- 2. 콘서트별 좌석 조회
CREATE INDEX idx_seats_concert_id ON seats(concert_id);

-- 3. 예약 가능 좌석 필터링
CREATE INDEX idx_seats_concert_reserved ON seats(concert_id, is_reserved);

-- 4. 예약 조회 (휴대폰번호)
CREATE INDEX idx_bookings_phone ON bookings(phone);

-- 5. 예약 조회 최적화
CREATE INDEX idx_bookings_phone_status ON bookings(phone, status);

-- 6. 예약별 좌석 조회
CREATE INDEX idx_booking_seats_booking_id ON booking_seats(booking_id);

-- 7. 좌석 등급 표시 순서
CREATE INDEX idx_seat_grades_display_order ON seat_grades(display_order);

-- 8. 좌석 등급 행 범위 검색
CREATE INDEX idx_seat_grades_row_range ON seat_grades(start_row, end_row);
```

### Unique 제약 인덱스

```sql
-- 좌석 위치 중복 방지
CREATE UNIQUE INDEX idx_seats_unique_position
ON seats(concert_id, section, row, seat_column);

-- 예약-좌석 중복 연결 방지
CREATE UNIQUE INDEX idx_booking_seats_unique
ON booking_seats(booking_id, seat_id);

-- 좌석 등급 코드 중복 방지
CREATE UNIQUE INDEX idx_seat_grades_grade_code
ON seat_grades(grade_code);
```

---

## 데이터 초기화

### 콘서트 생성 시 좌석 자동 생성

```sql
-- 콘서트 생성
INSERT INTO concerts (title, description, event_date, location)
VALUES ('BTS 콘서트', '방탄소년단 월드투어', '2025-12-25 19:00:00+09', '서울 올림픽 공원');

-- 320개 좌석 자동 생성 (트리거 또는 애플리케이션 로직)
INSERT INTO seats (concert_id, section, row, seat_column)
SELECT
  :concert_id,
  section,
  row,
  seat_column
FROM (
  SELECT
    unnest(ARRAY['A', 'B', 'C', 'D']) as section,
    generate_series(1, 20) as row,
    generate_series(1, 4) as seat_column
) AS seat_positions;
```

### 좌석 등급 시드 데이터

```sql
-- 좌석 등급 초기 데이터 (마이그레이션에 포함됨)
INSERT INTO seat_grades (grade_code, grade_name, start_row, end_row, price, color_code, display_order)
VALUES
    ('S', 'Special', 1, 3, 250000, '#9333EA', 1),
    ('P', 'Premium', 4, 7, 190000, '#0EA5E9', 2),
    ('A', 'Advanced', 8, 15, 170000, '#10B981', 3),
    ('R', 'Regular', 16, NULL, 140000, '#F97316', 4);
```

---

## 데이터 무결성

### Foreign Key 제약

```sql
-- seats → concerts
ALTER TABLE seats
ADD CONSTRAINT fk_seats_concert
FOREIGN KEY (concert_id) REFERENCES concerts(id)
ON DELETE CASCADE;  -- 콘서트 삭제 시 좌석도 삭제

-- bookings → concerts
ALTER TABLE bookings
ADD CONSTRAINT fk_bookings_concert
FOREIGN KEY (concert_id) REFERENCES concerts(id)
ON DELETE RESTRICT;  -- 예약이 있으면 콘서트 삭제 불가

-- booking_seats → bookings
ALTER TABLE booking_seats
ADD CONSTRAINT fk_booking_seats_booking
FOREIGN KEY (booking_id) REFERENCES bookings(id)
ON DELETE CASCADE;  -- 예약 삭제 시 연결도 삭제

-- booking_seats → seats
ALTER TABLE booking_seats
ADD CONSTRAINT fk_booking_seats_seat
FOREIGN KEY (seat_id) REFERENCES seats(id)
ON DELETE RESTRICT;  -- 좌석 삭제 방지
```

### Check 제약

```sql
-- 좌석 구역 제약
ALTER TABLE seats
ADD CONSTRAINT chk_seats_section
CHECK (section IN ('A', 'B', 'C', 'D'));

-- 좌석 행 제약
ALTER TABLE seats
ADD CONSTRAINT chk_seats_row
CHECK (row >= 1 AND row <= 20);

-- 좌석 열 제약
ALTER TABLE seats
ADD CONSTRAINT chk_seats_column
CHECK (seat_column >= 1 AND seat_column <= 4);

-- 예약 상태 제약
ALTER TABLE bookings
ADD CONSTRAINT chk_bookings_status
CHECK (status IN ('confirmed', 'cancelled'));

-- 좌석 등급 행 번호 제약
ALTER TABLE seat_grades
ADD CONSTRAINT chk_seat_grades_start_row
CHECK (start_row >= 1 AND start_row <= 20);

ALTER TABLE seat_grades
ADD CONSTRAINT chk_seat_grades_end_row
CHECK (end_row IS NULL OR (end_row >= start_row AND end_row <= 20));

-- 좌석 등급 가격 제약
ALTER TABLE seat_grades
ADD CONSTRAINT chk_seat_grades_price
CHECK (price > 0);
```

---

## 쿼리 성능 최적화

### 1. 콘서트 목록 조회 (집계 최적화)

```sql
-- 좋은 예: 필터링된 집계
SELECT
  c.id,
  c.title,
  c.event_date,
  c.location,
  COUNT(s.id) FILTER (WHERE s.is_reserved = false) as available_seats
FROM concerts c
LEFT JOIN seats s ON c.id = s.concert_id
WHERE c.event_date > (NOW() + INTERVAL '1 day')
GROUP BY c.id;
```

### 2. 예약 조회 (JOIN 최적화)

```sql
-- 좋은 예: 필요한 데이터만 JOIN (등급 정보 포함)
SELECT
  b.id,
  b.name,
  b.status,
  b.created_at,
  json_agg(
    json_build_object(
      'section', s.section,
      'row', s.row,
      'seat_column', s.seat_column,
      'grade_code', sg.grade_code,
      'grade_name', sg.grade_name,
      'price', sg.price
    )
  ) as seats
FROM bookings b
JOIN booking_seats bs ON b.id = bs.booking_id
JOIN seats s ON bs.seat_id = s.id
LEFT JOIN seat_grades sg ON get_seat_grade(s.row) = sg.grade_code
WHERE b.phone = :phone
GROUP BY b.id;
```

---

## 백업 및 복구 전략

### 정기 백업
```bash
# 전체 데이터베이스 백업
pg_dump -U postgres -d concert_booking > backup_$(date +%Y%m%d).sql

# 특정 테이블만 백업
pg_dump -U postgres -d concert_booking -t bookings -t booking_seats > bookings_backup.sql
```

### Point-in-Time Recovery
```sql
-- WAL 아카이빙 활성화 (postgresql.conf)
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

---

## 모니터링 쿼리

### 1. 예약 현황 집계
```sql
SELECT
  c.title,
  c.event_date,
  COUNT(DISTINCT b.id) as total_bookings,
  COUNT(bs.id) as reserved_seats,
  320 - COUNT(bs.id) as available_seats
FROM concerts c
LEFT JOIN bookings b ON c.id = b.concert_id AND b.status = 'confirmed'
LEFT JOIN booking_seats bs ON b.id = bs.booking_id
GROUP BY c.id
ORDER BY c.event_date;
```

### 2. 좌석 등급별 예약 현황
```sql
SELECT * FROM seat_grade_statistics
ORDER BY concert_id, display_order;
```

### 3. 활성 Lock 확인
```sql
SELECT
  pid,
  locktype,
  relation::regclass,
  mode,
  granted
FROM pg_locks
WHERE NOT granted;
```

### 4. 슬로우 쿼리 분석
```sql
-- postgresql.conf 설정
log_min_duration_statement = 1000  -- 1초 이상 쿼리 로깅

-- 실행 계획 확인
EXPLAIN ANALYZE
SELECT * FROM seats WHERE concert_id = 'xxx' AND is_reserved = false;
```

---

## 확장 고려사항 (향후)

### 1. 예약 만료 시간
```sql
ALTER TABLE bookings
ADD COLUMN expires_at TIMESTAMPTZ;
```

### 2. 결제 정보
```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id UUID NOT NULL REFERENCES bookings(id),
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) NOT NULL,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3. 동적 가격 조정
```sql
-- 콘서트별로 다른 가격 적용
CREATE TABLE concert_seat_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  concert_id UUID NOT NULL REFERENCES concerts(id),
  grade_code VARCHAR(10) NOT NULL REFERENCES seat_grades(grade_code),
  price INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(concert_id, grade_code)
);
```

---

**문서 버전**: 2.0
**최종 수정일**: 2025-10-13
**작성자**: Database Team
**DBMS**: PostgreSQL 14+
**변경사항**: 좌석 등급 시스템 추가 (seat_grades 테이블, get_seat_grade 함수, seat_grade_statistics 뷰)
