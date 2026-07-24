"""
tests/test_compliance_filter.py — Tests for investscan/compliance_filter.py
P1 Critical 95% coverage. English-First (P5-A).
H-1: verifies all 10 PROHIBITION_PATTERNS and sentinel enforcement.
"""
import pytest

from investscan.compliance_filter import (
    PROHIBITION_PATTERNS,
    filter_report,
    scan,
)


# ---------------------------------------------------------------------------
# Pattern count (H-1)
# ---------------------------------------------------------------------------

def test_prohibition_patterns_count():
    """PROHIBITION_PATTERNS must contain exactly 10 entries (H-1)."""
    assert len(PROHIBITION_PATTERNS) == 10


# ---------------------------------------------------------------------------
# scan() — individual pattern tests
# ---------------------------------------------------------------------------

def test_scan_buy_recommendation_korean():
    """'매수 추천합니다' must trigger the buy recommendation violation."""
    violations = scan("매수 추천합니다")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("buy recommendation" in d for d in descriptions)


def test_scan_price_target():
    """'목표가 50000원' must trigger the price target violation."""
    violations = scan("목표가 50000원")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("price target" in d for d in descriptions)


def test_scan_guaranteed_rise():
    """'확실한 상승이 예상됩니다' must trigger the guaranteed rise violation."""
    violations = scan("확실한 상승이 예상됩니다")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("guaranteed rise" in d for d in descriptions)


def test_scan_sell_recommendation():
    """'매도 권고합니다' must trigger the sell recommendation violation."""
    violations = scan("매도 권고합니다")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("sell recommendation" in d for d in descriptions)


def test_scan_strong_buy():
    """'강력 매수 신호' must trigger the strong buy violation."""
    violations = scan("강력 매수 신호")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("strong buy" in d for d in descriptions)


def test_scan_stop_loss():
    """'손절 라인 설정' must trigger the stop-loss line advisory violation."""
    violations = scan("손절 라인 설정")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("stop-loss" in d for d in descriptions)


def test_scan_expected_surge():
    """'급등 예상 종목' must trigger the expected surge violation."""
    violations = scan("급등 예상 종목")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("expected surge" in d for d in descriptions)


def test_scan_guaranteed_return_pct():
    """'30% 수익 보장' must trigger the guaranteed return percentage violation."""
    violations = scan("30% 수익 보장")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("guaranteed return percentage" in d for d in descriptions)


def test_scan_must_buy_english():
    """'must buy now' must trigger the English must buy violation."""
    violations = scan("must buy now")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("must buy" in d for d in descriptions)


def test_scan_guaranteed_return_english():
    """'guaranteed return on investment' must trigger the English guaranteed return violation."""
    violations = scan("guaranteed return on investment")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("guaranteed return" in d for d in descriptions)


# ---------------------------------------------------------------------------
# scan() — negative and edge cases
# ---------------------------------------------------------------------------

def test_scan_clean_text_no_violations():
    """Neutral analysis text must return no violations."""
    violations = scan("현재 기술주 환경을 분석합니다")
    assert violations == []


def test_scan_empty_text():
    """Empty string must return empty list without error."""
    violations = scan("")
    assert violations == []


def test_scan_case_insensitive():
    """'MUST BUY' in uppercase must trigger the must buy violation."""
    violations = scan("MUST BUY this stock immediately")
    assert len(violations) >= 1
    descriptions = [v[1] for v in violations]
    assert any("must buy" in d for d in descriptions)


def test_scan_returns_matched_text():
    """Each violation tuple must include the actual matched text as first element."""
    violations = scan("강력 매수 추천합니다")
    assert len(violations) >= 1
    matched_texts = [v[0] for v in violations]
    # At least one matched text should be a non-empty string
    assert all(isinstance(t, str) and len(t) > 0 for t in matched_texts)


def test_scan_multiple_violations_in_one_text():
    """Text with multiple prohibited patterns must report all violations."""
    text = "매수 추천합니다. 목표가 50000원. 확실한 상승이 예상됩니다."
    violations = scan(text)
    assert len(violations) >= 3


# ---------------------------------------------------------------------------
# filter_report()
# ---------------------------------------------------------------------------

def test_filter_report_compliant():
    """Clean text must return (True, []) indicating full compliance."""
    is_compliant, violations = filter_report("현재 기술주 환경을 분석합니다", sentiment_weight=0.0)
    assert is_compliant is True
    assert violations == []


def test_filter_report_violation():
    """Prohibited text must return (False, [violation, ...])."""
    is_compliant, violations = filter_report("매수 추천합니다", sentiment_weight=0.0)
    assert is_compliant is False
    assert len(violations) >= 1


def test_filter_sentiment_weight_ignored():
    """sentiment_weight=0.5 must produce the same result as sentiment_weight=0.0."""
    text = "매수 추천합니다"
    result_with_weight = filter_report(text, sentiment_weight=0.5)
    result_zero_weight = filter_report(text, sentiment_weight=0.0)
    assert result_with_weight == result_zero_weight


def test_filter_report_returns_tuple():
    """filter_report must always return a 2-tuple (bool, list)."""
    result = filter_report("Some neutral market analysis.", sentiment_weight=0.0)
    assert isinstance(result, tuple)
    assert len(result) == 2
    is_compliant, violations = result
    assert isinstance(is_compliant, bool)
    assert isinstance(violations, list)


def test_filter_report_empty_text():
    """Empty text must be considered compliant (no patterns found)."""
    is_compliant, violations = filter_report("", sentiment_weight=0.0)
    assert is_compliant is True
    assert violations == []
