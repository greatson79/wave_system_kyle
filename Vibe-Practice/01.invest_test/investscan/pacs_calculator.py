"""
investscan/pacs_calculator.py — Python pACS Calculator (PPC).
Replaces LLM self-reported pACS scores with deterministic Python measurement.

P6 Python-First: all 3 dimensions computed from text analysis — zero LLM calls.
English-First (P5-A).

pACS = min(Ft, Ct, Nt)  (same formula as translator/reviewer self-report)
  Ft — Fidelity:     technical term preservation + numeric preservation
  Ct — Completeness: structural preservation + size ratio
  Nt — Naturalness:  Korean character density + minimum Korean content

GREEN  ≥ 85   (production quality)
YELLOW 70-84  (acceptable, reviewer flags)
RED    < 70   (retranslate required)
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Korean Hangul syllables (Unicode range)
_KOREAN_PATTERN: re.Pattern = re.compile(r"[\uAC00-\uD7A3]")

# Markdown section headers
_HEADER_PATTERN: re.Pattern = re.compile(r"^#{1,4}\s+.+", re.MULTILINE)

# Numeric values (integers and decimals)
_NUMBER_PATTERN: re.Pattern = re.compile(r"\d+(?:\.\d+)?")

# Green/Yellow/Red thresholds
PACS_GREEN: int = 85
PACS_YELLOW: int = 70


def calculate_translation_pacs(
    source_text: str,
    target_text: str,
    glossary: dict | None = None,
    preserve_as_is: list[str] | None = None,
) -> dict:
    """
    Compute translation pACS deterministically from text analysis.

    Args:
        source_text:    English source document (full text)
        target_text:    Korean translation (full text)
        glossary:       dict loaded from translations/glossary.yaml
        preserve_as_is: list of technical terms that must appear verbatim in target

    Returns:
        dict with Ft, Ct, Nt, pACS, grade, method, details
    """
    glossary = glossary or {}
    preserve_as_is = preserve_as_is or _extract_preserve_terms(glossary)

    ft = _score_fidelity(source_text, target_text, preserve_as_is)
    ct = _score_completeness(source_text, target_text)
    nt = _score_naturalness(target_text)

    pacs = min(ft, ct, nt)
    grade = "GREEN" if pacs >= PACS_GREEN else ("YELLOW" if pacs >= PACS_YELLOW else "RED")

    result = {
        "Ft": ft,
        "Ct": ct,
        "Nt": nt,
        "pACS": pacs,
        "grade": grade,
        "method": "python_deterministic",
        "details": {
            "fidelity_score": ft,
            "completeness_score": ct,
            "naturalness_score": nt,
        },
    }

    logger.info(
        "PPC: Ft=%d, Ct=%d, Nt=%d → pACS=%d (%s)",
        ft, ct, nt, pacs, grade,
    )
    return result


def _score_fidelity(source: str, target: str, preserve_terms: list[str]) -> int:
    """
    Fidelity (Ft): how accurately source content is represented in target.

    Components:
      - Term preservation (60 pts): technical identifiers that must survive translation
      - Number preservation (40 pts): key numeric values must appear in translation

    Returns:
        Score 0-100.
    """
    score = 100

    # Component 1: Technical term preservation (max penalty -60)
    # Terms that must appear verbatim (identifiers, code names, etc.)
    terms_in_source = [t for t in preserve_terms if t and t in source]
    if terms_in_source:
        missed = [t for t in terms_in_source if t not in target]
        miss_rate = len(missed) / len(terms_in_source)
        penalty = int(miss_rate * 60)
        if penalty > 0:
            logger.debug("Ft: missed terms = %s", missed[:5])
        score -= penalty

    # Component 2: Number preservation (max penalty -40)
    # Key numbers from source should appear in translation
    source_numbers = set(_NUMBER_PATTERN.findall(source))
    # Filter to "meaningful" numbers (not just 1, 2, 3 that appear everywhere)
    significant_numbers = {n for n in source_numbers if float(n) >= 4.0 and n != "100"}
    if significant_numbers:
        target_numbers = set(_NUMBER_PATTERN.findall(target))
        missed_numbers = significant_numbers - target_numbers
        miss_rate = len(missed_numbers) / len(significant_numbers)
        penalty = int(miss_rate * 40)
        score -= penalty

    return max(0, score)


def _score_completeness(source: str, target: str) -> int:
    """
    Completeness (Ct): how completely the source structure is preserved.

    Components:
      - Section count ratio (50 pts): target should have ≥ source section count
      - Size ratio (50 pts): target bytes should be 50%-300% of source bytes

    Returns:
        Score 0-100.
    """
    score = 100

    # Component 1: Section header preservation (max penalty -50)
    source_headers = _HEADER_PATTERN.findall(source)
    target_headers = _HEADER_PATTERN.findall(target)

    if source_headers:
        # Target should have at least as many headers as source
        ratio = len(target_headers) / len(source_headers)
        if ratio < 0.7:
            # < 70% of source headers present → significant penalty
            penalty = int((1 - ratio) * 50)
            score -= min(50, penalty)

    # Component 2: Size ratio (max penalty -50)
    source_bytes = len(source.encode("utf-8"))
    target_bytes = len(target.encode("utf-8"))

    if source_bytes > 0:
        ratio = target_bytes / source_bytes
        if ratio < 0.5:
            # Too short — likely incomplete translation
            penalty = int((0.5 - ratio) * 100)
            score -= min(50, penalty)
        elif ratio > 3.0:
            # Too long — likely spurious content added
            penalty = int((ratio - 3.0) * 10)
            score -= min(30, penalty)

    return max(0, score)


def _score_naturalness(target: str) -> int:
    """
    Naturalness (Nt): quality of Korean content in target.

    Components:
      - Korean density (70 pts): Korean chars / total chars should be ≥ 10%
      - Minimum Korean content (30 pts): at least 50 Korean chars required

    Returns:
        Score 0-100.
    """
    if not target:
        return 0

    total_chars = len(target)
    korean_chars = len(_KOREAN_PATTERN.findall(target))

    # Component 1: Korean density (max penalty -70)
    density = korean_chars / total_chars if total_chars > 0 else 0
    if density < 0.10:
        # Below 10% density — possible untranslated content
        density_score = int(density * 700)  # 0.10 → 70, 0.05 → 35
    else:
        density_score = 70

    # Component 2: Minimum Korean content (max penalty -30)
    if korean_chars < 50:
        min_score = int(korean_chars * 30 / 50)  # linear scale to 30
    else:
        min_score = 30

    score = density_score + min_score
    return max(0, min(100, score))


def _extract_preserve_terms(glossary: dict) -> list[str]:
    """
    Extract terms that must be preserved verbatim from glossary.
    Terms where value == key (i.e., kept in English) must appear unchanged.

    Example:
        "NarrativeOutput": "NarrativeOutput"  → must appear in translation
        "BULLISH_THRESHOLD": "BULLISH_THRESHOLD"  → must appear in translation
    """
    preserve = []
    for key, value in glossary.items():
        if isinstance(key, str) and isinstance(value, str):
            # If the translation is identical to source → must be preserved as-is
            if key == value and len(key) >= 3:
                preserve.append(key)
    return preserve


def score_from_files(source_path: str, target_path: str, glossary_path: str | None = None) -> dict:
    """
    Convenience function: calculate pACS from file paths.

    Args:
        source_path:   path to English source .md file
        target_path:   path to Korean translation .md file
        glossary_path: path to translations/glossary.yaml (optional)

    Returns:
        pACS result dict (same as calculate_translation_pacs)
    """
    from pathlib import Path
    import yaml

    source_text = Path(source_path).read_text(encoding="utf-8")
    target_text = Path(target_path).read_text(encoding="utf-8")

    glossary: dict = {}
    if glossary_path and Path(glossary_path).exists():
        glossary = yaml.safe_load(Path(glossary_path).read_text(encoding="utf-8")) or {}

    return calculate_translation_pacs(source_text, target_text, glossary)


if __name__ == "__main__":
    """
    CLI entry point — P6 Python-First authoritative pACS measurement.

    Usage:
        python3 investscan/pacs_calculator.py --source report.md --target report.ko.md
        python3 investscan/pacs_calculator.py --source report.md --target report.ko.md --glossary translations/glossary.yaml

    Exit codes:
        0 — GREEN (pACS >= 85) or YELLOW (70-84): acceptable quality
        1 — RED (pACS < 70): translation quality insufficient, re-translate required
    """
    import argparse
    import json as _json
    import sys as _sys

    _parser = argparse.ArgumentParser(
        description=(
            "Python pACS Calculator — deterministic translation quality measurement.\n"
            "P6 Python-First: authoritative score via text analysis, zero LLM calls."
        ),
    )
    _parser.add_argument("--source", required=True, help="Path to English source file")
    _parser.add_argument("--target", required=True, help="Path to Korean translation file")
    _parser.add_argument(
        "--glossary",
        default="translations/glossary.yaml",
        help="Path to glossary YAML (default: translations/glossary.yaml)",
    )
    _args = _parser.parse_args()

    _result = score_from_files(_args.source, _args.target, _args.glossary)
    print(_json.dumps(_result, indent=2, ensure_ascii=False))

    # Exit 1 if RED (grade == "RED", pACS < 70) — aligned with pacs_calculator grade definition
    _sys.exit(1 if _result["grade"] == "RED" else 0)
