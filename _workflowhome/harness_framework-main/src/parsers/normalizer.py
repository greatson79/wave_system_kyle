"""불린/공백/전화번호/이메일 정규화."""

import re
from typing import Any

_BOOL_TRUE = {"예", "네", "yes", "y", "true", "1", "o", "확인", "입금완료", "완료"}
_BOOL_FALSE = {"아니오", "아니요", "no", "n", "false", "0", "x"}


def normalize_boolean(value: Any) -> bool:
    if value is None:
        return False
    s = str(value).strip().lower()
    if not s or s in ("nan", "none", ""):
        return False
    return s in _BOOL_TRUE


def normalize_phone(value: Any) -> str:
    if value is None:
        return ""
    digits = re.sub(r"[^\d]", "", str(value))
    if len(digits) == 11 and digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return str(value).strip()


def normalize_email(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    if "email" in result:
        result["email"] = normalize_email(result["email"])
    if "phone" in result:
        result["phone"] = normalize_phone(result["phone"])
    for bool_field in ("payment_status", "privacy_agreed", "course_completed"):
        if bool_field in result:
            result[bool_field] = normalize_boolean(result[bool_field])
    for field_name, val in result.items():
        if isinstance(val, str):
            result[field_name] = val.strip()
    return result
