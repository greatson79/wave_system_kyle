"""column_mapper 단위 테스트."""

import pytest
from src.parsers.column_mapper import build_column_map, map_row


class TestBuildColumnMap:
    def test_basic_mapping(self):
        headers = ["타임스탬프", "이메일 주소", "성함", "연락처", "교회/기관명"]
        col_map = build_column_map(headers)
        assert col_map["email"] == 1
        assert col_map["name"] == 2
        assert col_map["phone"] == 3
        assert col_map["church"] == 4

    def test_english_headers(self):
        headers = ["timestamp", "email", "name", "phone"]
        col_map = build_column_map(headers)
        assert col_map["timestamp"] == 0
        assert col_map["email"] == 1
        assert col_map["name"] == 2

    def test_unknown_headers_ignored(self):
        headers = ["unknown_col", "random_col"]
        col_map = build_column_map(headers)
        assert "email" not in col_map
        assert "name" not in col_map

    def test_partial_match(self):
        headers = ["수강 희망 클래스 선택", "입금여부 확인"]
        col_map = build_column_map(headers)
        assert col_map["class_level"] == 0
        assert col_map["payment_status"] == 1

    def test_required_fields_missing_returns_empty(self):
        # 필수 필드 누락 시 에러 로그만 (예외 없음)
        headers = ["소속", "직분"]
        col_map = build_column_map(headers)
        assert "email" not in col_map
        assert "name" not in col_map


class TestMapRow:
    def test_basic_row(self):
        col_map = {"email": 1, "name": 2}
        row = ["2026-04-01", "test@example.com", "홍길동"]
        result = map_row(row, col_map)
        assert result["email"] == "test@example.com"
        assert result["name"] == "홍길동"

    def test_row_shorter_than_expected(self):
        col_map = {"email": 5, "name": 1}
        row = ["a", "홍길동"]
        result = map_row(row, col_map)
        assert result["name"] == "홍길동"
        assert result["email"] is None

    def test_empty_row(self):
        col_map = {"email": 0}
        result = map_row([], col_map)
        assert result["email"] is None
