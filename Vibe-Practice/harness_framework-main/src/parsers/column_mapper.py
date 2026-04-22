"""헤더 텍스트 기반 컬럼 매핑."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# field_name → 매칭 키워드 목록 (contains, case-insensitive)
FIELD_KEYWORDS: dict[str, list[str]] = {
    "timestamp": ["타임스탬프", "timestamp"],
    "email": ["이메일", "email"],
    "name": ["성함", "이름", "name"],
    "phone": ["연락처", "전화", "phone"],
    "church": ["교회", "기관", "church"],
    "position": ["직분", "position"],
    "class_level": ["클래스", "class", "희망"],
    "payment_status": ["입금여부", "payment"],
    "payment_name": ["입금자", "payer"],
    "privacy_agreed": ["개인정보", "privacy"],
}

_REQUIRED_FIELDS = {"email", "name"}


def build_column_map(headers: list[str]) -> dict[str, int]:
    """헤더 목록 → {field_name: column_index}."""
    result: dict[str, int] = {}
    for field_name, keywords in FIELD_KEYWORDS.items():
        for idx, header in enumerate(headers):
            h_lower = header.lower().strip()
            for kw in keywords:
                if kw.lower() in h_lower:
                    if field_name not in result:
                        result[field_name] = idx
                    break
            if field_name in result:
                break

    for req in _REQUIRED_FIELDS:
        if req not in result:
            logger.error("필수 필드 매핑 실패: %s (헤더: %s)", req, headers)

    return result


def map_row(row: list[Any], column_map: dict[str, int]) -> dict[str, Any]:
    """단일 행 데이터 → {field_name: value}."""
    result: dict[str, Any] = {}
    for field_name, idx in column_map.items():
        if idx < len(row):
            result[field_name] = row[idx]
        else:
            result[field_name] = None
    return result
