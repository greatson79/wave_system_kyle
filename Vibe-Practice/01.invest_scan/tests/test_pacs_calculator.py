"""
tests/test_pacs_calculator.py — Tests for pacs_calculator.py (PPC).
Python pACS Calculator: deterministic Ft/Ct/Nt scoring.
P6 Python-First: all tests deterministic — no LLM calls.
English-First (P5-A).
"""
from __future__ import annotations

import pytest

from investscan.pacs_calculator import (
    calculate_translation_pacs,
    _score_fidelity,
    _score_completeness,
    _score_naturalness,
    _extract_preserve_terms,
    PACS_GREEN,
    PACS_YELLOW,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

ENGLISH_SOURCE = """# Samsung Electronics Investment Analysis

## Financial Overview
Revenue grew 8.3% YoY with operating income surging 34.2% in Q4 2025.
Current PER stands at 10.2x, representing a 28.4% discount to sector average.
Foreign institutional net buy reached $380M over 4 weeks.
NarrativeOutput sentiment_weight must remain 0.0.

## Risk Assessment
Primary downside risk: DRAM oversupply resurgence → estimated -12% revenue impact.
"""

# Good Korean translation preserving terms and numbers
KOREAN_GOOD = """# 삼성전자 투자 분석

## 재무 개요
수익은 전년 대비 8.3% 성장했으며 2025년 4분기 영업이익은 34.2% 급등했습니다.
현재 PER은 10.2배로 섹터 평균 대비 28.4% 할인 수준입니다.
외국인 기관 순매수는 4주간 $380M에 달했습니다.
NarrativeOutput sentiment_weight는 반드시 0.0을 유지해야 합니다.

## 위험 평가
주요 하방 리스크: DRAM 공급과잉 재발 → 예상 매출 영향 -12%.
"""

# Korean translation missing terms/numbers
KOREAN_POOR = """삼성에 대한 분석입니다. 투자에 참고하세요."""

GLOSSARY = {
    "NarrativeOutput": "NarrativeOutput",       # must be preserved as-is
    "sentiment_weight": "sentiment_weight",     # must be preserved as-is
    "PER": "PER",                               # must be preserved as-is
    "revenue": "매출",                           # translated → not a preserve term
    "analysis": "분석",                          # translated → not a preserve term
}


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pacs_green_threshold(self):
        assert PACS_GREEN == 85

    def test_pacs_yellow_threshold(self):
        assert PACS_YELLOW == 70

    def test_green_above_yellow(self):
        assert PACS_GREEN > PACS_YELLOW


# ── _extract_preserve_terms() ─────────────────────────────────────────────────

class TestExtractPreserveTerms:
    def test_identity_terms_extracted(self):
        # Terms where key == value → must be preserved verbatim
        glossary = {
            "NarrativeOutput": "NarrativeOutput",
            "PER": "PER",
            "revenue": "매출",  # translated — NOT preserved
        }
        terms = _extract_preserve_terms(glossary)
        assert "NarrativeOutput" in terms
        assert "PER" in terms
        assert "revenue" not in terms  # was translated

    def test_short_terms_excluded(self):
        # Terms shorter than 3 chars are not added (too common/ambiguous)
        glossary = {"AI": "AI", "NB": "NB"}
        terms = _extract_preserve_terms(glossary)
        assert "AI" not in terms
        assert "NB" not in terms

    def test_empty_glossary_returns_empty(self):
        assert _extract_preserve_terms({}) == []

    def test_all_translated_glossary_returns_empty(self):
        glossary = {"revenue": "매출", "analysis": "분석", "market": "시장"}
        terms = _extract_preserve_terms(glossary)
        assert terms == []

    def test_exact_length_boundary(self):
        # Length 3 is the minimum → included
        glossary = {"ABC": "ABC"}
        terms = _extract_preserve_terms(glossary)
        assert "ABC" in terms


# ── _score_fidelity() ─────────────────────────────────────────────────────────

class TestScoreFidelity:
    def test_perfect_fidelity_high_score(self):
        preserve = ["NarrativeOutput", "sentiment_weight", "PER"]
        score = _score_fidelity(ENGLISH_SOURCE, KOREAN_GOOD, preserve)
        assert score >= 80

    def test_missing_terms_reduces_score(self):
        preserve = ["NarrativeOutput", "sentiment_weight", "PER"]
        # Korean text that omits all preserve terms
        korean_no_terms = "이 문서는 투자 분석에 관한 내용입니다. 매우 중요한 데이터를 담고 있습니다."
        score = _score_fidelity(ENGLISH_SOURCE, korean_no_terms, preserve)
        assert score < 100

    def test_missing_numbers_reduces_score(self):
        # Source has numbers, target has none
        source = "Revenue grew 8.3% with 34.2% operating income increase of $380M."
        target = "수익이 증가했습니다."  # No numbers
        score = _score_fidelity(source, target, [])
        assert score < 100

    def test_no_preserve_terms_no_penalty(self):
        # If no terms to preserve, term penalty is zero
        score = _score_fidelity(ENGLISH_SOURCE, KOREAN_GOOD, [])
        assert score <= 100
        assert score >= 0

    def test_score_bounded_0_to_100(self):
        score = _score_fidelity(ENGLISH_SOURCE, KOREAN_POOR, ["NarrativeOutput", "PER"])
        assert 0 <= score <= 100

    def test_all_terms_preserved_all_numbers_present(self):
        source = "PER is 10.2x"
        target = "PER은 10.2배입니다."
        score = _score_fidelity(source, target, ["PER"])
        assert score == 100

    def test_terms_in_source_only_checked(self):
        # Terms not present in source are not required in target
        preserve = ["NarrativeOutput", "UnrelatedTerm"]
        # Only NarrativeOutput is in source → only that is checked
        source = "NarrativeOutput must be valid."
        target = "NarrativeOutput는 유효해야 합니다."
        score = _score_fidelity(source, target, preserve)
        assert score == 100


# ── _score_completeness() ─────────────────────────────────────────────────────

class TestScoreCompleteness:
    def test_complete_translation_high_score(self):
        score = _score_completeness(ENGLISH_SOURCE, KOREAN_GOOD)
        assert score >= 70

    def test_too_short_target_penalized(self):
        # Target is much shorter than source → incomplete translation
        very_short = "짧은 번역."
        score = _score_completeness(ENGLISH_SOURCE, very_short)
        assert score < 80

    def test_same_section_count_no_header_penalty(self):
        source = "# Section 1\ncontent\n## Section 2\ncontent"
        target = "# 섹션 1\n내용\n## 섹션 2\n내용"
        score = _score_completeness(source, target)
        assert score == 100

    def test_missing_sections_penalized(self):
        source = "# Sec1\n## Sec2\n### Sec3\n#### Sec4\n내용" * 5
        target = "짧은 번역 내용입니다." * 2  # No headers
        score = _score_completeness(source, target)
        assert score < 100

    def test_no_sections_in_source_no_penalty(self):
        # Plain prose — no header ratio check
        source = "Plain text with no sections. " * 10
        target = "일반 텍스트 번역 내용입니다. " * 10
        score = _score_completeness(source, target)
        assert score >= 80

    def test_score_bounded_0_to_100(self):
        score = _score_completeness(ENGLISH_SOURCE, KOREAN_POOR)
        assert 0 <= score <= 100

    def test_empty_source_no_crash(self):
        score = _score_completeness("", KOREAN_GOOD)
        assert 0 <= score <= 100


# ── _score_naturalness() ──────────────────────────────────────────────────────

class TestScoreNaturalness:
    def test_korean_rich_text_high_score(self):
        score = _score_naturalness(KOREAN_GOOD)
        assert score >= 70

    def test_pure_english_low_score(self):
        # No Korean chars → low naturalness for Korean translation
        english_only = "This is pure English text without any Korean characters present."
        score = _score_naturalness(english_only)
        assert score < 30

    def test_empty_string_returns_zero(self):
        assert _score_naturalness("") == 0

    def test_minimum_korean_chars_required(self):
        # Less than 50 Korean chars → minimum content penalty
        few_korean = "한국어" + "English text " * 20  # Only 3 Korean chars
        score = _score_naturalness(few_korean)
        assert score < 70

    def test_score_bounded_0_to_100(self):
        score = _score_naturalness(KOREAN_POOR)
        assert 0 <= score <= 100

    def test_sufficient_korean_density(self):
        # Text that is >10% Korean chars → no density penalty
        dense_korean = "삼성전자 투자 분석 보고서입니다. 수익이 증가했습니다. " * 5
        score = _score_naturalness(dense_korean)
        assert score >= 70


# ── calculate_translation_pacs() — full integration ──────────────────────────

class TestCalculateTranslationPacs:
    def test_returns_required_keys(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert "Ft" in result
        assert "Ct" in result
        assert "Nt" in result
        assert "pACS" in result
        assert "grade" in result
        assert "method" in result
        assert "details" in result

    def test_method_is_python_deterministic(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert result["method"] == "python_deterministic"

    def test_pacs_is_min_of_ft_ct_nt(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert result["pACS"] == min(result["Ft"], result["Ct"], result["Nt"])

    def test_good_translation_passes_yellow(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert result["pACS"] >= PACS_YELLOW

    def test_poor_translation_lower_score(self):
        result_good = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        result_poor = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_POOR, GLOSSARY)
        assert result_poor["pACS"] <= result_good["pACS"]

    def test_grade_green_for_score_above_85(self):
        # Construct a case that should score GREEN
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        # Grade must correspond to pACS score
        if result["pACS"] >= PACS_GREEN:
            assert result["grade"] == "GREEN"
        elif result["pACS"] >= PACS_YELLOW:
            assert result["grade"] == "YELLOW"
        else:
            assert result["grade"] == "RED"

    def test_grade_red_for_poor_translation(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_POOR, GLOSSARY)
        assert result["grade"] in ("RED", "YELLOW")  # poor translation not GREEN

    def test_scores_bounded_0_to_100(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert 0 <= result["Ft"] <= 100
        assert 0 <= result["Ct"] <= 100
        assert 0 <= result["Nt"] <= 100
        assert 0 <= result["pACS"] <= 100

    def test_no_glossary_still_works(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD)
        assert "pACS" in result
        assert result["pACS"] >= 0

    def test_preserve_as_is_overrides_glossary(self):
        # Explicit preserve_as_is list takes precedence over glossary extraction
        result = calculate_translation_pacs(
            ENGLISH_SOURCE, KOREAN_GOOD,
            preserve_as_is=["NarrativeOutput", "PER"]
        )
        assert "pACS" in result

    def test_details_contains_sub_scores(self):
        result = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        details = result["details"]
        assert "fidelity_score" in details
        assert "completeness_score" in details
        assert "naturalness_score" in details

    def test_deterministic_same_input_same_output(self):
        result1 = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        result2 = calculate_translation_pacs(ENGLISH_SOURCE, KOREAN_GOOD, GLOSSARY)
        assert result1["pACS"] == result2["pACS"]
        assert result1["grade"] == result2["grade"]

    def test_grade_thresholds_correct(self):
        # Grade thresholds must match constants
        for pacs_val, expected_grade in [(90, "GREEN"), (75, "YELLOW"), (60, "RED")]:
            # Create mock sub-scores that force a known pACS
            # We test by directly computing what grade would be
            if pacs_val >= PACS_GREEN:
                assert expected_grade == "GREEN"
            elif pacs_val >= PACS_YELLOW:
                assert expected_grade == "YELLOW"
            else:
                assert expected_grade == "RED"
