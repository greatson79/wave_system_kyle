"""파일명 패턴 파싱 — 6가지 패턴 A-F."""

import re
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CURRENT_YEAR


@dataclass(frozen=True)
class ParsedFileName:
    month: int | None
    category: str | None
    target: str | None
    class_levels: list[int]
    region: str | None
    raw: str
    parse_error: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "class_levels", list(self.class_levels))

    @property
    def cohort(self) -> str | None:
        if self.month is None:
            return None
        return f"{CURRENT_YEAR}-{self.month:02d}"


_MONTH_RE = re.compile(r"(\d{1,2})월")
_CLASS_RE = re.compile(r"[Cc]lass\s*#?\s*(\d)")
_MULTI_CLASS_RE = re.compile(r"[Cc]lass\s*#?\s*(\d)(?:\s*[&＆]\s*(\d))+")

_TARGET_KEYWORDS: dict[str, str] = {
    "목회자": "목회자",
    "목클": "목회자",
    "일반인": "일반",
    "일반": "일반",
    "교회": "교회",
}

_REGION_KEYWORDS: list[str] = ["부산", "충남", "꿈별", "대전", "인천", "광주", "대구"]

_CATEGORY_KEYWORDS: dict[str, str] = {
    "교회강의": "교회강의",
    "wave academy": "Wave Academy",
    "자격증": "자격증과정",
    "외부강의": "외부강의",
}


def _extract_month(text: str) -> int | None:
    m = _MONTH_RE.search(text)
    if m:
        val = int(m.group(1))
        return val if 1 <= val <= 12 else None
    return None


def _extract_class_levels(text: str) -> list[int]:
    # multi-class: Class #1 & 3
    nums: list[int] = []
    for m in re.finditer(r"[Cc]lass\s*#?\s*(\d)", text):
        val = int(m.group(1))
        if val not in nums:
            nums.append(val)
    # also catch bare digits after &
    for m in re.finditer(r"[&＆]\s*(\d)", text):
        val = int(m.group(1))
        if val not in nums:
            nums.append(val)
    return sorted(nums)


def _extract_target(text: str) -> str | None:
    lower = text.lower()
    for kw, val in _TARGET_KEYWORDS.items():
        if kw in lower or kw in text:
            return val
    return None


def _extract_region(text: str) -> str | None:
    for kw in _REGION_KEYWORDS:
        if kw in text:
            return kw
    return None


def _extract_category(text: str) -> str | None:
    lower = text.lower()
    for kw, val in _CATEGORY_KEYWORDS.items():
        if kw in lower:
            return val
    return None


def _strip_outer_parens(filename: str) -> str:
    """파일명에서 (응답) 제거 후 첫 번째 괄호 내용 추출."""
    # Remove trailing (응답) or (응답) variants
    cleaned = re.sub(r"\(응답\)", "", filename).strip()
    # Remove 의 사본
    cleaned = re.sub(r"의\s*사본", "", cleaned).strip()
    # Extract content inside first (...)
    m = re.search(r"\((.+?)\)", cleaned)
    if m:
        return m.group(1)
    return cleaned


def parse_filename(filename: str) -> ParsedFileName:
    """파일명을 파싱하여 ParsedFileName 반환. 실패 시 parse_error=True."""
    if not filename:
        return ParsedFileName(
            month=None,
            category=None,
            target=None,
            class_levels=[],
            region=None,
            raw=filename or "",
            parse_error=True,
        )

    inner = _strip_outer_parens(filename)
    inner_norm = re.sub(r"\s+", " ", inner).strip()

    month = _extract_month(inner_norm)
    category = _extract_category(inner_norm)
    target = _extract_target(inner_norm)
    class_levels = _extract_class_levels(inner_norm)
    region = _extract_region(inner_norm)

    # (응답) 없는 파일 → parse_error
    has_response_marker = "(응답)" in filename
    parse_error = not has_response_marker

    return ParsedFileName(
        month=month,
        category=category,
        target=target,
        class_levels=class_levels,
        region=region,
        raw=filename,
        parse_error=parse_error,
    )
