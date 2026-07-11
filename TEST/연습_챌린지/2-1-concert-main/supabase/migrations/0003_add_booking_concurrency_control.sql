-- Migration: Add Booking Concurrency Control
-- Description: Creates PostgreSQL RPC function for atomic booking with row-level locking
-- Version: 1.0
-- Date: 2025-10-13

-- =============================================================================
-- FUNCTION: create_booking_with_lock
-- Description: Creates a booking with row-level locking to prevent concurrent reservations
-- Parameters:
--   - p_concert_id: Concert UUID
--   - p_seat_ids: Array of seat UUIDs
--   - p_name: Customer name
--   - p_phone: Customer phone number
--   - p_password_hash: Hashed password (bcrypt)
-- Returns: JSON with booking_id and success status
-- =============================================================================

CREATE OR REPLACE FUNCTION create_booking_with_lock(
  p_concert_id UUID,
  p_seat_ids UUID[],
  p_name VARCHAR,
  p_phone VARCHAR,
  p_password_hash VARCHAR
) RETURNS JSON AS $$
DECLARE
  v_booking_id UUID;
  v_seat_record RECORD;
  v_concert_record RECORD;
  v_event_date TIMESTAMPTZ;
  v_booking_deadline TIMESTAMPTZ;
BEGIN
  -- 1. Validate concert exists and lock it
  SELECT id, title, event_date INTO v_concert_record
  FROM concerts
  WHERE id = p_concert_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Concert not found';
  END IF;

  -- 2. Check booking period (must be before event date - 1 day)
  v_event_date := v_concert_record.event_date;
  v_booking_deadline := v_event_date - INTERVAL '1 day';

  IF NOW() >= v_booking_deadline THEN
    RAISE EXCEPTION 'Booking period has ended';
  END IF;

  -- 3. Lock seats in order (by id) to prevent deadlock
  FOR v_seat_record IN
    SELECT id, is_reserved, section, row, seat_column
    FROM seats
    WHERE id = ANY(p_seat_ids)
      AND concert_id = p_concert_id
    ORDER BY id
    FOR UPDATE
  LOOP
    -- Check if seat is already reserved
    IF v_seat_record.is_reserved THEN
      RAISE EXCEPTION 'Seat already reserved: % section % row % column %',
        v_seat_record.id,
        v_seat_record.section,
        v_seat_record.row,
        v_seat_record.seat_column;
    END IF;
  END LOOP;

  -- 4. Validate seat count matches
  IF (SELECT COUNT(*) FROM seats WHERE id = ANY(p_seat_ids) AND concert_id = p_concert_id) != array_length(p_seat_ids, 1) THEN
    RAISE EXCEPTION 'One or more seat IDs are invalid';
  END IF;

  -- 5. Create booking
  INSERT INTO bookings (concert_id, name, phone, password_hash, status)
  VALUES (p_concert_id, p_name, p_phone, p_password_hash, 'confirmed')
  RETURNING id INTO v_booking_id;

  -- 6. Create booking-seat connections
  INSERT INTO booking_seats (booking_id, seat_id)
  SELECT v_booking_id, unnest(p_seat_ids);

  -- 7. Update seats to reserved
  UPDATE seats
  SET is_reserved = true, updated_at = NOW()
  WHERE id = ANY(p_seat_ids);

  -- 8. Return success response
  RETURN json_build_object(
    'booking_id', v_booking_id,
    'success', true,
    'message', 'Booking created successfully'
  );

EXCEPTION
  WHEN OTHERS THEN
    -- Re-raise the exception to trigger rollback
    RAISE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_booking_with_lock(UUID, UUID[], VARCHAR, VARCHAR, VARCHAR) IS 'Creates a booking with row-level locking to prevent concurrent reservations';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION create_booking_with_lock(UUID, UUID[], VARCHAR, VARCHAR, VARCHAR) TO anon, authenticated;

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Created function:';
    RAISE NOTICE '  - create_booking_with_lock(UUID, UUID[], VARCHAR, VARCHAR, VARCHAR)';
    RAISE NOTICE '';
    RAISE NOTICE 'Features:';
    RAISE NOTICE '  - Row-level locking (SELECT ... FOR UPDATE)';
    RAISE NOTICE '  - Deadlock prevention (ORDER BY id)';
    RAISE NOTICE '  - Atomic transaction (all or nothing)';
    RAISE NOTICE '  - Booking period validation';
    RAISE NOTICE '  - Seat availability validation';
    RAISE NOTICE '=================================================================';
END $$;
