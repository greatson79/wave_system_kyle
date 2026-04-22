"""filename_parser 단위 테스트."""

import pytest
from src.parsers.filename_parser import parse_filename, ParsedFileName


class TestPatternA:
    def test_pastor_integrated(self):
        result = parse_filename("(4월 목회자 통합신청서)(응답)")
        assert result.month == 4
        assert result.target == "목회자"
        assert result.class_levels == []
        assert result.parse_error is False

    def test_cohort(self):
        result = parse_filename("(3월 목회자 통합신청서)(응답)")
        assert result.cohort == "2026-03"


class TestPatternB:
    def test_multi_class_with_hash_space(self):
        result = parse_filename("(4월 일반 Class #1 & 3통합신청서)(응답)")
        assert result.month == 4
        assert result.target == "일반"
        assert 1 in result.class_levels
        assert 3 in result.class_levels
        assert result.parse_error is False


class TestPatternC:
    def test_church_lecture_pastor_class1(self):
        result = parse_filename("(3월 교회강의 목회자 Class#1 수강신청)(응답)")
        assert result.month == 3
        assert result.category == "교회강의"
        assert result.target == "목회자"
        assert result.class_levels == [1]
        assert result.parse_error is False


class TestPatternD:
    def test_church_lecture_general_class1(self):
        result = parse_filename("(3월 교회강의 일반 Class #1 수강신청)(응답)")
        assert result.month == 3
        assert result.category == "교회강의"
        assert result.target == "일반"
        assert result.class_levels == [1]
        assert result.parse_error is False


class TestPatternE:
    def test_region_church_lecture(self):
        result = parse_filename("(4월 꿈별 교회강의 신청서)(응답)")
        assert result.month == 4
        assert result.region == "꿈별"
        assert result.category == "교회강의"
        assert result.parse_error is False


class TestPatternF:
    def test_busan_church_lecture_class1(self):
        result = parse_filename("(4월 부산 교회강의 Class#1 수강신청서)(응답)")
        assert result.month == 4
        assert result.region == "부산"
        assert result.category == "교회강의"
        assert result.class_levels == [1]
        assert result.parse_error is False


class TestClassVariants:
    def test_class_no_hash(self):
        result = parse_filename("(3월 일반 Class1 수강신청)(응답)")
        assert 1 in result.class_levels

    def test_class_hash_space(self):
        result = parse_filename("(3월 일반 Class #1 수강신청)(응답)")
        assert 1 in result.class_levels

    def test_class_hash_nospace(self):
        result = parse_filename("(3월 일반 Class#1 수강신청)(응답)")
        assert 1 in result.class_levels


class TestMultiClass:
    def test_class_1_and_3(self):
        result = parse_filename("(4월 일반 Class #1 & 3통합신청서)(응답)")
        assert sorted(result.class_levels) == [1, 3]

    def test_class_1_and_2(self):
        result = parse_filename("(4월 일반 Class #1 & 2통합신청서)(응답)")
        assert sorted(result.class_levels) == [1, 2]


class TestParseError:
    def test_no_response_marker(self):
        result = parse_filename("GroupMailSender.gsheet")
        assert result.parse_error is True

    def test_empty_string(self):
        result = parse_filename("")
        assert result.parse_error is True

    def test_none_like_empty(self):
        result = parse_filename("")
        assert isinstance(result, ParsedFileName)
        assert result.parse_error is True

    def test_copy_suffix_removed(self):
        result = parse_filename("(4월 목회자 통합신청서의 사본)(응답)")
        assert result.parse_error is False
        assert result.month == 4

    def test_raw_preserved(self):
        fname = "(4월 목회자 통합신청서)(응답)"
        result = parse_filename(fname)
        assert result.raw == fname
