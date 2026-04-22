"""과제 정의 및 현황 관리."""

import logging
from pathlib import Path

import pandas as pd

from utils.constants import SHEET_ASSIGNMENT_DEF, SHEET_ASSIGNMENT_STATUS

logger = logging.getLogger(__name__)

_DEF_COLUMNS = ["id", "category", "class_level", "week", "title", "weight", "is_active"]
_STATUS_COLUMNS = ["student_id", "assignment_id", "status", "submitted_at"]


class AssignmentManager:
    def __init__(self) -> None:
        self._definitions: pd.DataFrame = pd.DataFrame(columns=_DEF_COLUMNS)
        self._status: pd.DataFrame = pd.DataFrame(columns=_STATUS_COLUMNS)

    def load_definitions(self, master_path: Path | None) -> None:
        """기존 마스터 Excel의 과제_정의 시트에서 로드."""
        if master_path is None or not master_path.exists():
            return
        try:
            df = pd.read_excel(master_path, sheet_name=SHEET_ASSIGNMENT_DEF)
            self._definitions = df
        except Exception as exc:
            logger.warning("과제_정의 시트 로드 실패 (빈 DataFrame 사용): %s", exc)

    def load_status(self, master_path: Path | None) -> None:
        """기존 마스터 Excel의 과제_현황 시트에서 로드."""
        if master_path is None or not master_path.exists():
            return
        try:
            df = pd.read_excel(master_path, sheet_name=SHEET_ASSIGNMENT_STATUS)
            self._status = df
        except Exception as exc:
            logger.warning("과제_현황 시트 로드 실패 (빈 DataFrame 사용): %s", exc)

    def get_completion_rate(self, student_id: str) -> float:
        """weight 기반 가중 완료율 계산 (0.0~100.0)."""
        if self._definitions.empty or self._status.empty:
            return 0.0

        active_defs = self._definitions[self._definitions.get("is_active", True) == True]
        if active_defs.empty:
            return 0.0

        student_status = self._status[self._status["student_id"] == student_id]
        completed_ids = set(
            student_status[student_status["status"] == "완료"]["assignment_id"].tolist()
        )

        total_weight = active_defs["weight"].sum()
        if total_weight == 0:
            return 0.0

        completed_weight = active_defs[active_defs["id"].isin(completed_ids)]["weight"].sum()
        return float(completed_weight / total_weight * 100)

    def get_definitions(self) -> pd.DataFrame:
        return self._definitions.copy()

    def get_status(self) -> pd.DataFrame:
        return self._status.copy()
