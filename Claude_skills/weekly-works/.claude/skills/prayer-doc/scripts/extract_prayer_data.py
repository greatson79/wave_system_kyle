#!/usr/bin/env python3
"""
디딤수요기도회 기도제목 데이터 추출 모듈
CSV 파일에서 특정 월/주차의 기도제목 데이터를 추출한다.
"""

import csv
import sys
import json
import re
from pathlib import Path


# 주차별 열 인덱스 매핑 (0-based)
# E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11, M=12, N=13
WEEK_COLUMN_MAP = {
    1: {"community": 4, "personal": 5},
    2: {"community": 6, "personal": 7},
    3: {"community": 8, "personal": 9},
    4: {"community": 10, "personal": 11},
    5: {"community": 12, "personal": 13},
}

# 한국어 서수 → 숫자 매핑
KOREAN_ORDINAL = {
    "첫째": 1, "첫번째": 1, "첫": 1,
    "둘째": 2, "두번째": 2,
    "셋째": 3, "세번째": 3,
    "넷째": 4, "네번째": 4,
    "다섯째": 5, "다섯번째": 5,
}

# 월 이름 매핑
MONTH_MAP = {
    "1월": 1, "2월": 2, "3월": 3, "4월": 4,
    "5월": 5, "6월": 6, "7월": 7, "8월": 8,
    "9월": 9, "10월": 10, "11월": 11, "12월": 12,
}


def parse_month(text: str) -> int | None:
    """텍스트에서 월 정보를 추출한다."""
    # "8월", "8" 등
    for key, val in MONTH_MAP.items():
        if key in text:
            return val
    match = re.search(r'(\d{1,2})월?', text)
    if match:
        m = int(match.group(1))
        if 1 <= m <= 12:
            return m
    return None


def parse_week(text: str) -> int | None:
    """텍스트에서 주차 정보를 추출한다."""
    # 한국어 서수
    for key, val in KOREAN_ORDINAL.items():
        if key in text:
            return val
    # "2주차", "2주", "둘째 주" 등
    match = re.search(r'(\d)주', text)
    if match:
        w = int(match.group(1))
        if 1 <= w <= 5:
            return w
    return None


def parse_prayer_items(raw_text: str) -> list[str]:
    """
    기도제목 텍스트를 개별 항목 리스트로 파싱한다.
    입력 형태: "1. 기도제목1\n2. 기도제목2\n3. 기도제목3\n4. 기도제목4"
    """
    if not raw_text or raw_text.strip() == "":
        return []
    
    items = []
    # 번호 패턴으로 분리 (1. 2. 3. 4.)
    parts = re.split(r'\n?\d+\.\s*', raw_text.strip())
    for part in parts:
        cleaned = part.strip().rstrip('.')
        if cleaned:
            items.append(cleaned)
    
    return items


def extract_prayer_data(csv_path: str, month: int, week: int) -> dict:
    """
    CSV에서 특정 월/주차의 기도제목 데이터를 추출한다.
    
    Returns:
        {
            "month": 8,
            "week": 2,
            "quarter_theme": "섬김의 확장",
            "worship_title": "추수할 일꾼을 보내소서",
            "scripture": "마 9:35-38",
            "community_prayers": ["기도1", "기도2", ...],
            "personal_prayers": ["기도1", "기도2", ...],
            "error": null
        }
    """
    result = {
        "month": month,
        "week": week,
        "quarter_theme": "",
        "worship_title": "",
        "scripture": "",
        "community_prayers": [],
        "personal_prayers": [],
        "error": None,
    }
    
    csv_file = Path(csv_path)
    if not csv_file.exists():
        result["error"] = f"CSV 파일을 찾을 수 없습니다: {csv_path}"
        return result
    
    # CSV 읽기
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if len(rows) < 3:
        result["error"] = "CSV 파일에 데이터가 부족합니다."
        return result
    
    # 데이터 행 찾기 (1행=제목, 2행=헤더, 3행~=데이터)
    target_row = None
    month_str = f"{month}월"
    
    for row in rows[2:]:  # 헤더 2줄 건너뜀
        if len(row) > 0 and row[0].strip() == month_str:
            target_row = row
            break
    
    if target_row is None:
        result["error"] = f"{month_str} 데이터를 찾을 수 없습니다."
        return result
    
    # 기본 정보 추출
    result["quarter_theme"] = target_row[1].strip() if len(target_row) > 1 else ""
    result["worship_title"] = target_row[2].strip() if len(target_row) > 2 else ""
    result["scripture"] = target_row[3].strip() if len(target_row) > 3 else ""
    
    # 주차별 기도제목 추출
    if week not in WEEK_COLUMN_MAP:
        result["error"] = f"유효하지 않은 주차입니다: {week}주차 (1~5주차만 가능)"
        return result
    
    col_map = WEEK_COLUMN_MAP[week]
    comm_idx = col_map["community"]
    pers_idx = col_map["personal"]
    
    comm_text = target_row[comm_idx].strip() if len(target_row) > comm_idx else ""
    pers_text = target_row[pers_idx].strip() if len(target_row) > pers_idx else ""
    
    if not comm_text and not pers_text:
        result["error"] = f"{month_str} {week}주차 기도제목이 비어있습니다."
        return result
    
    result["community_prayers"] = parse_prayer_items(comm_text)
    result["personal_prayers"] = parse_prayer_items(pers_text)
    
    return result


def main():
    """CLI 실행: python extract_prayer_data.py <csv_path> <month> <week>"""
    if len(sys.argv) != 4:
        print("Usage: python extract_prayer_data.py <csv_path> <month> <week>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    month = int(sys.argv[2])
    week = int(sys.argv[3])
    
    data = extract_prayer_data(csv_path, month, week)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
