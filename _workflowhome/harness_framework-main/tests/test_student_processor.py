"""student_processor 단위 테스트."""

import io
from pathlib import Path

import openpyxl
import pytest

from parsers.filename_parser import ParsedFileName
from processors.student_processor import StudentProcessor


def _make_xlsx(rows: list[list]) -> Path:
    """메모리 내 xlsx 파일을 tmp_path에 저장."""
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    tmp = Path("/tmp/test_wave_proc.xlsx")
    wb.save(tmp)
    return tmp


def _parsed(month: int = 4, class_levels: list[int] | None = None) -> ParsedFileName:
    return ParsedFileName(
        month=month,
        category="Wave Academy",
        target="일반",
        class_levels=class_levels or [1],
        region=None,
        raw="(4월 일반 Class#1 수강신청)(응답)",
        parse_error=False,
    )


def test_new_student_added():
    proc = StudentProcessor()
    path = _make_xlsx([
        ["타임스탬프", "이메일", "성함", "연락처", "교회", "직분", "입금여부"],
        ["2026-04-01", "test@a.com", "홍길동", "010-1234-5678", "OO교회", "목사", "예"],
    ])
    count = proc.process_file(path, _parsed())
    assert count == 1
    master = proc.get_master()
    assert len(master) == 1
    assert master.iloc[0]["email"] == "test@a.com"
    assert master.iloc[0]["is_active"] is True
    stats = proc.get_stats()
    assert stats["new"] == 1


def test_duplicate_skipped_and_updated():
    proc = StudentProcessor()
    path = _make_xlsx([
        ["타임스탬프", "이메일", "성함", "연락처", "교회", "직분", "입금여부"],
        ["2026-04-01", "dup@a.com", "김철수", "010-0000-0000", "A교회", "목사", "예"],
        ["2026-04-01", "dup@a.com", "김철수", "010-0000-0000", "A교회", "목사", "예"],
    ])
    proc.process_file(path, _parsed())
    master = proc.get_master()
    assert len(master) == 1
    stats = proc.get_stats()
    assert stats["new"] == 1
    assert stats["updated"] == 1


def test_empty_file_returns_zero():
    proc = StudentProcessor()
    path = _make_xlsx([["이메일", "성함"]])
    count = proc.process_file(path, _parsed())
    assert count == 0
    assert len(proc.get_master()) == 0


def test_missing_email_row_skipped():
    proc = StudentProcessor()
    path = _make_xlsx([
        ["타임스탬프", "이메일", "성함"],
        ["2026-04-01", "", "이름없음"],
    ])
    proc.process_file(path, _parsed())
    assert len(proc.get_master()) == 0
    assert proc.get_stats()["skipped"] == 1


def test_load_existing_none_does_not_crash():
    proc = StudentProcessor()
    proc.load_existing(None)
    assert proc.get_master().empty


def test_get_master_returns_copy():
    proc = StudentProcessor()
    path = _make_xlsx([
        ["이메일", "성함"],
        ["x@x.com", "X"],
    ])
    proc.process_file(path, _parsed())
    m1 = proc.get_master()
    m1["email"] = "mutated"
    m2 = proc.get_master()
    assert m2.iloc[0]["email"] != "mutated"
