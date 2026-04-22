-- Migration: Add Seat Grades (Pricing Tiers)
-- Description: Creates seat_grades table and adds seat grade information
-- Version: 1.0
-- Date: 2025-10-13

-- =============================================================================
-- TABLE: seat_grades
-- Description: Stores seat grade information (pricing tiers based on row number)
-- =============================================================================

CREATE TABLE seat_grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grade_code VARCHAR(10) NOT NULL UNIQUE,
    grade_name VARCHAR(50) NOT NULL,
    start_row INTEGER NOT NULL,
    end_row INTEGER,  -- NULL means "to the end"
    price INTEGER NOT NULL,  -- Price in Korean Won
    color_code VARCHAR(10) NOT NULL,  -- Hex color code for UI
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
CREATE INDEX idx_seat_grades_row_range ON seat_grades(start_row, end_row);

-- Add comment
COMMENT ON TABLE seat_grades IS 'Seat grade pricing tiers (S, P, A, R)';
COMMENT ON COLUMN seat_grades.grade_code IS 'Grade code (S, P, A, R)';
COMMENT ON COLUMN seat_grades.grade_name IS 'Grade display name (Special, Premium, Advanced, Regular)';
COMMENT ON COLUMN seat_grades.start_row IS 'Starting row number for this grade';
COMMENT ON COLUMN seat_grades.end_row IS 'Ending row number (NULL means to the last row)';
COMMENT ON COLUMN seat_grades.price IS 'Price in Korean Won (e.g., 250000)';
COMMENT ON COLUMN seat_grades.color_code IS 'Hex color code for UI (e.g., #9333EA)';
COMMENT ON COLUMN seat_grades.display_order IS 'Display order (1 = highest grade)';

-- Add trigger for updated_at
CREATE TRIGGER update_seat_grades_updated_at
    BEFORE UPDATE ON seat_grades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

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

    RETURN COALESCE(v_grade_code, 'R');  -- Default to 'R' if not found
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION get_seat_grade(INTEGER) IS 'Returns seat grade code based on row number';

-- =============================================================================
-- INSERT SEED DATA
-- Description: Insert seat grade pricing tiers
-- =============================================================================

INSERT INTO seat_grades (grade_code, grade_name, start_row, end_row, price, color_code, display_order)
VALUES
    ('S', 'Special', 1, 3, 250000, '#9333EA', 1),    -- 보라색 (purple-600)
    ('P', 'Premium', 4, 7, 190000, '#0EA5E9', 2),    -- 하늘색 (sky-500)
    ('A', 'Advanced', 8, 15, 170000, '#10B981', 3),  -- 초록색 (emerald-500)
    ('R', 'Regular', 16, NULL, 140000, '#F97316', 4); -- 주황색 (orange-500), NULL means to row 20

-- =============================================================================
-- HELPER VIEW: seat_grade_statistics
-- Description: View for monitoring seat grade availability per concert
-- =============================================================================

CREATE OR REPLACE VIEW seat_grade_statistics AS
SELECT
    c.id as concert_id,
    c.title as concert_title,
    sg.grade_code,
    sg.grade_name,
    sg.price,
    COUNT(s.id) as total_seats,
    COUNT(s.id) FILTER (WHERE s.is_reserved = true) as reserved_seats,
    COUNT(s.id) FILTER (WHERE s.is_reserved = false) as available_seats,
    ROUND(
        (COUNT(s.id) FILTER (WHERE s.is_reserved = true)::NUMERIC /
         NULLIF(COUNT(s.id), 0)) * 100,
        2
    ) as occupancy_rate
FROM concerts c
CROSS JOIN seat_grades sg
LEFT JOIN seats s ON s.concert_id = c.id
    AND s.row >= sg.start_row
    AND (sg.end_row IS NULL OR s.row <= sg.end_row)
GROUP BY c.id, c.title, sg.grade_code, sg.grade_name, sg.price, sg.display_order
ORDER BY c.event_date, sg.display_order;

COMMENT ON VIEW seat_grade_statistics IS 'Seat grade availability statistics per concert';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

GRANT SELECT ON seat_grades TO anon, authenticated;
GRANT SELECT ON seat_grade_statistics TO anon, authenticated;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify seat_grades table creation
DO $$
DECLARE
    grade_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO grade_count FROM seat_grades;

    IF grade_count = 4 THEN
        RAISE NOTICE 'SUCCESS: 4 seat grades inserted (S, P, A, R)';
    ELSE
        RAISE EXCEPTION 'ERROR: Expected 4 seat grades but found %', grade_count;
    END IF;
END $$;

-- Verify get_seat_grade function
DO $$
DECLARE
    grade_s VARCHAR(10);
    grade_p VARCHAR(10);
    grade_a VARCHAR(10);
    grade_r VARCHAR(10);
BEGIN
    SELECT get_seat_grade(1) INTO grade_s;
    SELECT get_seat_grade(5) INTO grade_p;
    SELECT get_seat_grade(10) INTO grade_a;
    SELECT get_seat_grade(18) INTO grade_r;

    IF grade_s = 'S' AND grade_p = 'P' AND grade_a = 'A' AND grade_r = 'R' THEN
        RAISE NOTICE 'SUCCESS: get_seat_grade() function working correctly';
        RAISE NOTICE '  Row 1 -> %, Row 5 -> %, Row 10 -> %, Row 18 -> %', grade_s, grade_p, grade_a, grade_r;
    ELSE
        RAISE EXCEPTION 'ERROR: get_seat_grade() function returned unexpected values';
    END IF;
END $$;

-- Display seat grade pricing information
DO $$
DECLARE
    grade_record RECORD;
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Seat Grade Pricing Information:';
    RAISE NOTICE '=================================================================';

    FOR grade_record IN
        SELECT grade_code, grade_name, start_row, end_row, price, color_code
        FROM seat_grades
        ORDER BY display_order
    LOOP
        RAISE NOTICE '  % (%) | Rows %-% | ₩% | Color: %',
            grade_record.grade_code,
            grade_record.grade_name,
            grade_record.start_row,
            COALESCE(grade_record.end_row::TEXT, '20'),
            grade_record.price,
            grade_record.color_code;
    END LOOP;

    RAISE NOTICE '=================================================================';
END $$;

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Migration 0004 completed successfully!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - seat_grades table (4 grades: S, P, A, R)';
    RAISE NOTICE '  - get_seat_grade(row) function';
    RAISE NOTICE '  - seat_grade_statistics view';
    RAISE NOTICE '';
    RAISE NOTICE 'Seat Grade Tiers:';
    RAISE NOTICE '  S (Special)  : Rows 1-3    | 250,000 KRW';
    RAISE NOTICE '  P (Premium)  : Rows 4-7    | 190,000 KRW';
    RAISE NOTICE '  A (Advanced) : Rows 8-15   | 170,000 KRW';
    RAISE NOTICE '  R (Regular)  : Rows 16-20  | 140,000 KRW';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Update backend API to include grade information';
    RAISE NOTICE '  2. Update frontend components to display grade colors';
    RAISE NOTICE '  3. Update booking flow to calculate total amount';
    RAISE NOTICE '=================================================================';
END $$;
