"""grade_calculator 단위 테스트."""

import pandas as pd
import pytest

from processors.grade_calculator import calculate_all, calculate_grade
from utils.constants import GRADE_FAIL, GRADE_IN_PROGRESS, GRADE_PASS


def test_pass():
    grade, reason = calculate_grade(90.0, True, True)
    assert grade == GRADE_PASS
    assert "90.0%" in reason


def test_fail_low_rate():
    grade, reason = calculate_grade(50.0, True, True)
    assert grade == GRADE_FAIL
    assert "50.0%" in reason


def test_in_progress():
    grade, _ = calculate_grade(100.0, False, True)
    assert grade == GRADE_IN_PROGRESS


def test_fail_no_payment():
    grade, reason = calculate_grade(90.0, True, False)
    assert grade == GRADE_FAIL
    assert "미입금" in reason


def test_boundary_exactly_threshold():
    grade, _ = calculate_grade(80.0, True, True, threshold=80.0)
    assert grade == GRADE_PASS


def test_boundary_just_below_threshold():
    grade, _ = calculate_grade(79.9, True, True, threshold=80.0)
    assert grade == GRADE_FAIL


def test_calculate_all_updates_grade_column():
    df = pd.DataFrame([
        {"email": "a@a.com", "course_completed": True, "payment_status": True, "assignment_completion_rate": 90.0},
        {"email": "b@b.com", "course_completed": False, "payment_status": True, "assignment_completion_rate": 90.0},
    ])
    result = calculate_all(df)
    assert result.loc[0, "grade"] == GRADE_PASS
    assert result.loc[1, "grade"] == GRADE_IN_PROGRESS


def test_calculate_all_does_not_mutate_original():
    df = pd.DataFrame([
        {"email": "a@a.com", "course_completed": True, "payment_status": True, "assignment_completion_rate": 90.0},
    ])
    _ = calculate_all(df)
    assert "grade" not in df.columns


def test_calculate_all_empty():
    df = pd.DataFrame()
    result = calculate_all(df)
    assert result.empty
