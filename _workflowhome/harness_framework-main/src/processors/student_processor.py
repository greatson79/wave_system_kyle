"""수강생 데이터 통합 — 중복 제거, upsert."""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import openpyxl
import pandas as pd

from parsers.column_mapper import build_column_map, map_row
from parsers.filename_parser import ParsedFileName
from parsers.normalizer import normalize_row
from utils.constants import GRADE_IN_PROGRESS, SHEET_MASTER
from utils.error_handler import Severity, log_error

logger = logging.getLogger(__name__)

_MASTER_COLUMNS = [
    "id", "timestamp", "email", "name", "phone", "church", "position",
    "category", "class_level", "target", "region", "cohort",
    "payment_status", "course_completed", "grade",
    "assignment_completion_rate", "source_file", "is_active",
    "created_at", "updated_at",
]

_UPSERT_KEY = ["email", "class_level", "cohort"]


class StudentProcessor:
    def __init__(self) -> None:
        self._master: pd.DataFrame = pd.DataFrame(columns=_MASTER_COLUMNS)
        self._stats: dict[str, int] = {"total": 0, "new": 0, "updated": 0, "skipped": 0, "errors": 0}

    def load_existing(self, master_path: Path | None) -> None:
        """기존 마스터 Excel이 있으면 로드."""
        if master_path is None or not master_path.exists():
            return
        try:
            df = pd.read_excel(master_path, sheet_name=SHEET_MASTER)
            self._master = df
            logger.info("기존 마스터 로드: %d 행", len(df))
        except Exception as exc:
            log_error(Severity.HIGH, "StudentProcessor", "마스터 Excel 로드 실패", exc=exc)

    def process_file(self, local_path: Path, parsed_filename: ParsedFileName) -> int:
        """단일 Excel 파일을 처리하여 마스터에 upsert. 처리된 행 수 반환."""
        try:
            wb = openpyxl.load_workbook(local_path, read_only=True, data_only=True)
            ws = wb.worksheets[0]
            rows = list(ws.iter_rows(values_only=True))
            wb.close()
        except Exception as exc:
            log_error(Severity.HIGH, "StudentProcessor", f"파일 읽기 실패: {local_path}", exc=exc)
            self._stats["errors"] += 1
            return 0

        if len(rows) < 2:
            logger.info("빈 시트 스킵: %s", local_path.name)
            return 0

        headers = [str(h) if h is not None else "" for h in rows[0]]
        col_map = build_column_map(headers)

        if "email" not in col_map:
            log_error(Severity.MEDIUM, "StudentProcessor", f"이메일 컬럼 없음: {local_path.name}")
            self._stats["errors"] += 1
            return 0

        processed = 0
        for raw_row in rows[1:]:
            if all(v is None for v in raw_row):
                continue
            try:
                row_list: list[Any] = list(raw_row)
                mapped = map_row(row_list, col_map)
                normalized = normalize_row(mapped)
                self._upsert(normalized, parsed_filename, local_path.name)
                processed += 1
            except Exception as exc:
                log_error(Severity.MEDIUM, "StudentProcessor", "행 처리 실패", exc=exc)
                self._stats["errors"] += 1

        self._stats["total"] += processed
        return processed

    def _upsert(
        self,
        row: dict[str, Any],
        pf: ParsedFileName,
        source_file: str,
    ) -> None:
        email = str(row.get("email") or "").strip().lower()
        if not email:
            self._stats["skipped"] += 1
            return

        # class_level from filename (first class) or row
        class_level: str | None = None
        if pf.class_levels:
            class_level = f"Class #{pf.class_levels[0]}"
        elif row.get("class_level"):
            class_level = str(row["class_level"]).strip()

        cohort = pf.cohort

        now = datetime.now(timezone.utc).isoformat()

        # Find existing record
        mask = (
            (self._master["email"] == email)
            & (self._master["class_level"] == class_level)
            & (self._master["cohort"] == cohort)
        )
        existing = self._master[mask]

        if not existing.empty:
            idx = existing.index[0]
            updates: dict[str, Any] = {
                "updated_at": now,
                "source_file": source_file,
            }
            for field in ("name", "phone", "church", "position", "payment_status", "privacy_agreed"):
                if field in row and row[field] is not None:
                    updates[field] = row[field]
            if pf.category:
                updates["category"] = pf.category
            if pf.target:
                updates["target"] = pf.target
            if pf.region:
                updates["region"] = pf.region

            new_master = self._master.copy()
            for col, val in updates.items():
                if col in new_master.columns:
                    new_master.at[idx, col] = val
            self._master = new_master
            self._stats["updated"] += 1
        else:
            new_record: dict[str, Any] = {
                "id": str(uuid.uuid4()),
                "timestamp": row.get("timestamp"),
                "email": email,
                "name": row.get("name", ""),
                "phone": row.get("phone", ""),
                "church": row.get("church", ""),
                "position": row.get("position", ""),
                "category": pf.category or "",
                "class_level": class_level or "",
                "target": pf.target or "",
                "region": pf.region or "",
                "cohort": cohort or "",
                "payment_status": row.get("payment_status", False),
                "course_completed": row.get("course_completed", False),
                "grade": GRADE_IN_PROGRESS,
                "assignment_completion_rate": 0.0,
                "source_file": source_file,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
            new_row_df = pd.DataFrame([new_record])
            self._master = pd.concat([self._master, new_row_df], ignore_index=True)
            self._stats["new"] += 1

    def get_master(self) -> pd.DataFrame:
        return self._master.copy()

    def get_stats(self) -> dict[str, int]:
        return dict(self._stats)
