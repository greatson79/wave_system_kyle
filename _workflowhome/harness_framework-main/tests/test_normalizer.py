"""normalizer 단위 테스트."""

import pytest
from src.parsers.normalizer import normalize_boolean, normalize_phone, normalize_email, normalize_row


class TestNormalizeBoolean:
    @pytest.mark.parametrize("value", ["예", "네", "Yes", "Y", "TRUE", "1", "O", "확인", "입금완료", "완료"])
    def test_true_values(self, value):
        assert normalize_boolean(value) is True

    @pytest.mark.parametrize("value", ["아니오", "아니요", "No", "N", "FALSE", "0", "X"])
    def test_false_values(self, value):
        assert normalize_boolean(value) is False

    def test_none_is_false(self):
        assert normalize_boolean(None) is False

    def test_empty_string_is_false(self):
        assert normalize_boolean("") is False

    def test_nan_like_is_false(self):
        assert normalize_boolean("nan") is False

    def test_case_insensitive(self):
        assert normalize_boolean("YES") is True
        assert normalize_boolean("yes") is True


class TestNormalizePhone:
    def test_11_digit(self):
        assert normalize_phone("01012345678") == "010-1234-5678"

    def test_hyphenated(self):
        result = normalize_phone("010-1234-5678")
        assert "010" in result

    def test_none_returns_empty(self):
        assert normalize_phone(None) == ""

    def test_short_number_passthrough(self):
        result = normalize_phone("12345")
        assert result == "12345"


class TestNormalizeEmail:
    def test_lowercase(self):
        assert normalize_email("TEST@EXAMPLE.COM") == "test@example.com"

    def test_strip_whitespace(self):
        assert normalize_email("  user@example.com  ") == "user@example.com"

    def test_none_returns_empty(self):
        assert normalize_email(None) == ""


class TestNormalizeRow:
    def test_normalizes_email_and_phone(self):
        row = {"email": "TEST@EXAMPLE.COM", "phone": "01012345678", "name": "  홍길동  "}
        result = normalize_row(row)
        assert result["email"] == "test@example.com"
        assert result["phone"] == "010-1234-5678"
        assert result["name"] == "홍길동"

    def test_normalizes_payment_status(self):
        row = {"payment_status": "예"}
        result = normalize_row(row)
        assert result["payment_status"] is True

    def test_preserves_unknown_fields(self):
        row = {"custom_field": "value"}
        result = normalize_row(row)
        assert result["custom_field"] == "value"
