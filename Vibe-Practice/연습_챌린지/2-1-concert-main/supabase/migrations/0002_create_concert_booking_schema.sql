-- Migration: Create Concert Booking Schema
-- Description: Creates tables for concert booking platform with seats, bookings, and related entities
-- Version: 1.0
-- Date: 2025-10-13

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLE: concerts
-- Description: Stores concert information
-- =============================================================================

CREATE TABLE concerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date TIMESTAMPTZ NOT NULL,
    location VARCHAR(255) NOT NULL,
    thumbnail_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for date-based filtering
CREATE INDEX idx_concerts_event_date ON concerts(event_date);

-- Add comment
COMMENT ON TABLE concerts IS 'Concert information';
COMMENT ON COLUMN concerts.event_date IS 'Concert event date and time';

-- =============================================================================
-- TABLE: seats
-- Description: Stores individual seat information for each concert
-- =============================================================================

CREATE TABLE seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concert_id UUID NOT NULL,
    section CHAR(1) NOT NULL,
    row INTEGER NOT NULL,
    seat_column INTEGER NOT NULL,
    is_reserved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_seats_concert
        FOREIGN KEY (concert_id)
        REFERENCES concerts(id)
        ON DELETE CASCADE,

    -- Check constraints
    CONSTRAINT chk_seats_section
        CHECK (section IN ('A', 'B', 'C', 'D')),
    CONSTRAINT chk_seats_row
        CHECK (row >= 1 AND row <= 20),
    CONSTRAINT chk_seats_column
        CHECK (seat_column >= 1 AND seat_column <= 4)
);

-- Indexes for performance optimization
CREATE INDEX idx_seats_concert_id ON seats(concert_id);
CREATE INDEX idx_seats_concert_reserved ON seats(concert_id, is_reserved);

-- Unique constraint to prevent duplicate seat positions
CREATE UNIQUE INDEX idx_seats_unique_position
    ON seats(concert_id, section, row, seat_column);

-- Add comments
COMMENT ON TABLE seats IS 'Individual seats for each concert (320 seats per concert)';
COMMENT ON COLUMN seats.section IS 'Seat section: A, B, C, or D';
COMMENT ON COLUMN seats.row IS 'Seat row: 1-20';
COMMENT ON COLUMN seats.seat_column IS 'Seat column: 1-4';
COMMENT ON COLUMN seats.is_reserved IS 'Whether the seat is reserved';

-- =============================================================================
-- TABLE: bookings
-- Description: Stores booking information
-- =============================================================================

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concert_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_bookings_concert
        FOREIGN KEY (concert_id)
        REFERENCES concerts(id)
        ON DELETE RESTRICT,

    -- Check constraint for status
    CONSTRAINT chk_bookings_status
        CHECK (status IN ('confirmed', 'cancelled'))
);

-- Indexes for query optimization
CREATE INDEX idx_bookings_phone ON bookings(phone);
CREATE INDEX idx_bookings_concert_id ON bookings(concert_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_phone_status ON bookings(phone, status);

-- Add comments
COMMENT ON TABLE bookings IS 'Booking information';
COMMENT ON COLUMN bookings.phone IS 'Customer phone number (may be encrypted)';
COMMENT ON COLUMN bookings.password_hash IS 'Hashed 4-digit password (bcrypt)';
COMMENT ON COLUMN bookings.status IS 'Booking status: confirmed or cancelled';

-- =============================================================================
-- TABLE: booking_seats
-- Description: Junction table connecting bookings and seats (many-to-many)
-- =============================================================================

CREATE TABLE booking_seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL,
    seat_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key constraints
    CONSTRAINT fk_booking_seats_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_booking_seats_seat
        FOREIGN KEY (seat_id)
        REFERENCES seats(id)
        ON DELETE RESTRICT
);

-- Indexes for join performance
CREATE INDEX idx_booking_seats_booking_id ON booking_seats(booking_id);
CREATE INDEX idx_booking_seats_seat_id ON booking_seats(seat_id);

-- Unique constraint to prevent duplicate booking-seat connections
CREATE UNIQUE INDEX idx_booking_seats_unique
    ON booking_seats(booking_id, seat_id);

-- Add comment
COMMENT ON TABLE booking_seats IS 'Junction table connecting bookings and seats';

-- =============================================================================
-- FUNCTION: update_updated_at_column
-- Description: Automatically updates updated_at timestamp
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS: Auto-update updated_at timestamps
-- =============================================================================

CREATE TRIGGER update_concerts_updated_at
    BEFORE UPDATE ON concerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_seats_updated_at
    BEFORE UPDATE ON seats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- FUNCTION: generate_seats_for_concert
-- Description: Generates 320 seats (4 sections × 20 rows × 4 columns) for a concert
-- =============================================================================

CREATE OR REPLACE FUNCTION generate_seats_for_concert(p_concert_id UUID)
RETURNS void AS $$
BEGIN
    INSERT INTO seats (concert_id, section, row, seat_column)
    SELECT
        p_concert_id,
        section_letter,
        row_number,
        column_number
    FROM
        (SELECT unnest(ARRAY['A', 'B', 'C', 'D']) AS section_letter) AS sections,
        generate_series(1, 20) AS row_number,
        generate_series(1, 4) AS column_number;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_seats_for_concert(UUID) IS 'Generates 320 seats for a given concert';

-- =============================================================================
-- SAMPLE DATA (Optional - for development/testing)
-- =============================================================================

-- Insert sample concerts
INSERT INTO concerts (title, description, event_date, location, thumbnail_url)
VALUES
    (
        'BTS World Tour 2025',
        '방탄소년단 월드투어 서울 공연',
        '2025-12-25 19:00:00+09',
        '서울 올림픽공원 체조경기장',
        'https://example.com/bts-thumbnail.jpg'
    ),
    (
        'Blackpink Concert',
        '블랙핑크 Born Pink Tour',
        '2025-11-15 18:00:00+09',
        '고척 스카이돔',
        'https://example.com/blackpink-thumbnail.jpg'
    ),
    (
        'IU Concert 2025',
        'IU The Golden Hour',
        '2025-10-20 19:00:00+09',
        'KSPO DOME',
        'https://example.com/iu-thumbnail.jpg'
    );

-- Generate seats for each concert
DO $$
DECLARE
    concert_record RECORD;
BEGIN
    FOR concert_record IN SELECT id FROM concerts LOOP
        PERFORM generate_seats_for_concert(concert_record.id);
    END LOOP;
END $$;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify table creation
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('concerts', 'seats', 'bookings', 'booking_seats');

    IF table_count = 4 THEN
        RAISE NOTICE 'SUCCESS: All 4 tables created successfully';
    ELSE
        RAISE EXCEPTION 'ERROR: Expected 4 tables but found %', table_count;
    END IF;
END $$;

-- Verify seat count
DO $$
DECLARE
    total_seats INTEGER;
    expected_seats INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_seats FROM seats;
    SELECT COUNT(*) * 320 INTO expected_seats FROM concerts;

    IF total_seats = expected_seats THEN
        RAISE NOTICE 'SUCCESS: Generated % seats (% per concert)', total_seats, 320;
    ELSE
        RAISE EXCEPTION 'ERROR: Expected % seats but found %', expected_seats, total_seats;
    END IF;
END $$;

-- =============================================================================
-- GRANT PERMISSIONS (Supabase RLS will be configured separately)
-- =============================================================================

-- Grant basic permissions (adjust based on your security requirements)
-- These will be overridden by Row Level Security policies

GRANT SELECT ON concerts TO anon, authenticated;
GRANT SELECT ON seats TO anon, authenticated;
GRANT SELECT, INSERT ON bookings TO anon, authenticated;
GRANT SELECT, INSERT ON booking_seats TO anon, authenticated;

-- =============================================================================
-- HELPFUL QUERIES FOR MONITORING
-- =============================================================================

-- Query to check booking statistics
CREATE OR REPLACE VIEW booking_statistics AS
SELECT
    c.id as concert_id,
    c.title,
    c.event_date,
    COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'confirmed') as total_bookings,
    COUNT(bs.id) FILTER (WHERE b.status = 'confirmed') as reserved_seats,
    320 - COUNT(bs.id) FILTER (WHERE b.status = 'confirmed') as available_seats,
    ROUND(
        (COUNT(bs.id) FILTER (WHERE b.status = 'confirmed')::NUMERIC / 320) * 100,
        2
    ) as occupancy_rate
FROM concerts c
LEFT JOIN bookings b ON c.id = b.concert_id
LEFT JOIN booking_seats bs ON b.id = bs.booking_id
GROUP BY c.id, c.title, c.event_date
ORDER BY c.event_date;

COMMENT ON VIEW booking_statistics IS 'Overview of booking statistics per concert';

-- =============================================================================
-- INDEXES FOR ANALYTICS (Optional)
-- =============================================================================

-- Index for created_at based queries
CREATE INDEX idx_bookings_created_at ON bookings(created_at DESC);
CREATE INDEX idx_concerts_created_at ON concerts(created_at DESC);

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Created tables:';
    RAISE NOTICE '  - concerts';
    RAISE NOTICE '  - seats';
    RAISE NOTICE '  - bookings';
    RAISE NOTICE '  - booking_seats';
    RAISE NOTICE '';
    RAISE NOTICE 'Created functions:';
    RAISE NOTICE '  - update_updated_at_column()';
    RAISE NOTICE '  - generate_seats_for_concert(UUID)';
    RAISE NOTICE '';
    RAISE NOTICE 'Created views:';
    RAISE NOTICE '  - booking_statistics';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Configure Row Level Security (RLS) policies';
    RAISE NOTICE '  2. Set up proper authentication';
    RAISE NOTICE '  3. Review and adjust permissions';
    RAISE NOTICE '=================================================================';
END $$;
