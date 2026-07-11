"""학점/이수 계산 — Pass/Fail/진행중."""

import pandas as pd

from utils.constants import GRADE_FAIL, GRADE_IN_PROGRESS, GRADE_PASS


def calculate_grade(
    completion_rate: float,
    course_completed: bool,
    payment_status: bool,
    threshold: float = 80.0,
) -> tuple[str, str]:
    """단일 수강생 학점 계산.

    Returns:
        (grade, reason)
    """
    if not course_completed:
        return GRADE_IN_PROGRESS, "수강 미완료"

    if not payment_status:
        return GRADE_FAIL, "수강료 미입금"

    if completion_rate >= threshold:
        return GRADE_PASS, f"과제 완료율 {completion_rate:.1f}% (기준 {threshold:.1f}%)"

    return GRADE_FAIL, f"과제 완료율 {completion_rate:.1f}% < 기준 {threshold:.1f}%"


def calculate_all(master_df: pd.DataFrame, threshold: float = 80.0) -> pd.DataFrame:
    """전체 수강생 학점 일괄 계산. grade 컬럼을 업데이트한 새 DataFrame 반환."""
    if master_df.empty:
        return master_df.copy()

    df = master_df.copy()

    def _grade_row(row: pd.Series) -> str:
        completion_raw = row.get("assignment_completion_rate", 0.0)
        try:
            completion_rate = float(completion_raw) if completion_raw not in (None, "", "nan") else 0.0
        except (ValueError, TypeError):
            completion_rate = 0.0

        course_raw = row.get("course_completed", False)
        course_completed = bool(course_raw) if course_raw not in (None, "", "nan") else False

        payment_raw = row.get("payment_status", False)
        payment_status = bool(payment_raw) if payment_raw not in (None, "", "nan") else False

        grade, _ = calculate_grade(
            completion_rate=completion_rate,
            course_completed=course_completed,
            payment_status=payment_status,
            threshold=threshold,
        )
        return grade

    df["grade"] = df.apply(_grade_row, axis=1)
    return df
