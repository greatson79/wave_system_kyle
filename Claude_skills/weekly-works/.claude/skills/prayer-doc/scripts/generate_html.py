#!/usr/bin/env python3
"""
디딤수요기도회 기도제목 A4 HTML 문서 생성 모듈
추출된 기도제목 데이터를 교회 로고가 포함된 A4 레이아웃 HTML로 변환한다.
"""

import base64
import json
import sys
from pathlib import Path


def load_logo_base64(logo_path: str) -> str | None:
    """로고 이미지를 base64로 인코딩한다."""
    p = Path(logo_path)
    if not p.exists():
        return None
    with open(p, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = p.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"


def estimate_font_size(total_items: int) -> dict:
    """기도제목 개수에 따라 폰트 크기와 간격을 동적으로 조절한다 (A4 기준)."""
    if total_items <= 6:
        return {"title_size": "20px", "item_size": "15px", "line_height": "2.0", "item_gap": "12px"}
    elif total_items <= 8:
        return {"title_size": "18px", "item_size": "14px", "line_height": "1.85", "item_gap": "10px"}
    elif total_items <= 10:
        return {"title_size": "17px", "item_size": "13px", "line_height": "1.75", "item_gap": "8px"}
    else:
        return {"title_size": "16px", "item_size": "12px", "line_height": "1.65", "item_gap": "6px"}


def estimate_font_size_card(total_items: int) -> dict:
    """기도제목 개수에 따라 폰트 크기와 간격을 동적으로 조절한다 (4:5 카드 기준, 1080px 너비)."""
    if total_items <= 6:
        return {"title_size": "38px", "item_size": "30px", "line_height": "2.1", "item_gap": "18px"}
    elif total_items <= 8:
        return {"title_size": "34px", "item_size": "27px", "line_height": "2.0", "item_gap": "15px"}
    elif total_items <= 10:
        return {"title_size": "30px", "item_size": "24px", "line_height": "1.85", "item_gap": "12px"}
    else:
        return {"title_size": "27px", "item_size": "21px", "line_height": "1.75", "item_gap": "9px"}


def generate_prayer_html(data: dict, logo_path: str, output_path: str, format: str = 'a4') -> str:
    """
    기도제목 데이터를 HTML 문서로 생성한다.

    Args:
        data: extract_prayer_data()의 반환값
        logo_path: 교회 로고 이미지 경로
        output_path: HTML 출력 경로
        format: 출력 형식 ('a4' 또는 'card')

    Returns:
        생성된 HTML 파일 경로
    """
    month = data["month"]
    week = data["week"]
    quarter_theme = data["quarter_theme"]
    worship_title = data["worship_title"]
    scripture = data["scripture"]
    community = data["community_prayers"]
    personal = data["personal_prayers"]
    
    # 로고 로드
    logo_b64 = load_logo_base64(logo_path)
    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="{logo_b64}" alt="디딤교회 로고" class="logo">'
    else:
        logo_html = '<div class="logo-text">DiDIM CHURCH 디딤교회</div>'
    
    # 폰트 사이즈 동적 조절
    total_items = len(community) + len(personal)
    sizes = estimate_font_size_card(total_items) if format == 'card' else estimate_font_size(total_items)
    
    # 기도제목 HTML 생성
    def render_items(items: list[str]) -> str:
        html = ""
        for i, item in enumerate(items, 1):
            html += f'<div class="prayer-item"><span class="item-num">{i}.</span> {item}</div>\n'
        return html
    
    community_html = render_items(community)
    personal_html = render_items(personal)
    
    # 주차 한국어 표기
    week_kr = {1: "첫째 주", 2: "둘째 주", 3: "셋째 주", 4: "넷째 주", 5: "다섯째 주"}
    week_text = week_kr.get(week, f"{week}주차")
    
    if format == 'card':
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>디딤수요기도회 기도제목 - {month}월 {week_text}</title>
<style>
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Noto Sans CJK KR', 'Noto Sans KR', 'NanumGothic', 'Malgun Gothic', '맑은 고딕', 'Apple SD Gothic Neo', sans-serif;
    background: #ffffff;
    color: #333333;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page {{
    width: 1080px;
    height: 1350px;
    margin: 0 auto;
    padding: 70px 80px 60px 80px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }}

  /* 헤더: 로고 영역 */
  .header {{
    text-align: center;
    margin-bottom: 18px;
    padding-bottom: 18px;
    border-bottom: 3px solid #4a6741;
  }}

  .logo {{
    height: 110px;
    margin-bottom: 6px;
  }}

  .logo-text {{
    font-size: 36px;
    font-weight: 700;
    color: #4a6741;
    letter-spacing: 3px;
  }}

  /* 타이틀 영역 */
  .title-section {{
    text-align: center;
    margin-bottom: 22px;
  }}

  .main-title {{
    font-size: 44px;
    font-weight: 700;
    color: #4a6741;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }}

  .sub-info {{
    font-size: 22px;
    color: #666666;
    margin-bottom: 4px;
  }}

  .quarter-theme {{
    display: inline-block;
    background: #f0f5ed;
    color: #4a6741;
    font-size: 19px;
    font-weight: 500;
    padding: 6px 22px;
    border-radius: 18px;
    margin-top: 6px;
  }}

  /* 기도제목 영역 */
  .prayer-section {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 10px;
  }}

  .prayer-block {{
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fafcf9;
    border-left: 6px solid #4a6741;
    border-radius: 0 12px 12px 0;
    padding: 20px 26px;
  }}

  .prayer-block.personal {{
    border-left-color: #8b9a2b;
  }}

  .prayer-items {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
  }}

  .section-title {{
    font-size: {sizes['title_size']};
    font-weight: 700;
    color: #4a6741;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .section-title.personal {{
    color: #6b7a1b;
  }}

  .section-icon {{
    font-size: 32px;
  }}

  .prayer-item {{
    font-size: {sizes['item_size']};
    line-height: {sizes['line_height']};
    color: #444444;
    padding-left: 4px;
  }}

  .item-num {{
    font-weight: 700;
    color: #4a6741;
    margin-right: 2px;
  }}

  .prayer-block.personal .item-num {{
    color: #6b7a1b;
  }}

  /* 푸터 */
  .footer {{
    margin-top: auto;
    padding-top: 14px;
    border-top: 1px solid #dde5d9;
    text-align: center;
  }}

  .footer-text {{
    font-size: 18px;
    color: #999999;
  }}

  .scripture-badge {{
    display: inline-block;
    background: #4a6741;
    color: #ffffff;
    font-size: 18px;
    font-weight: 500;
    padding: 6px 20px;
    border-radius: 16px;
    margin-bottom: 6px;
  }}
</style>
</head>
<body>
<div class="page">

  <!-- 헤더 -->
  <div class="header">
    {logo_html}
  </div>

  <!-- 타이틀 -->
  <div class="title-section">
    <div class="main-title">2026 디딤수요기도회 기도제목</div>
    <div class="sub-info">{month}월 {week_text}</div>
    <div class="sub-info">
      <span class="scripture-badge">📖 {scripture}</span>
    </div>
    <div class="quarter-theme">✦ {quarter_theme} — {worship_title}</div>
  </div>

  <!-- 기도제목 -->
  <div class="prayer-section">

    <div class="prayer-block community">
      <div class="section-title">
        <span class="section-icon">🙏</span> 공동체를 위한 기도
      </div>
      <div class="prayer-items">
        {community_html}
      </div>
    </div>

    <div class="prayer-block personal">
      <div class="section-title personal">
        <span class="section-icon">💛</span> 개인을 위한 기도
      </div>
      <div class="prayer-items">
        {personal_html}
      </div>
    </div>

  </div>

  <!-- 푸터 -->
  <div class="footer">
    <div class="footer-text">디딤교회 DiDIM CHURCH | 수요기도회</div>
  </div>

</div>
</body>
</html>"""
    else:
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>디딤수요기도회 기도제목 - {month}월 {week_text}</title>
<style>
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  @page {{
    size: A4;
    margin: 0;
  }}

  body {{
    font-family: 'Noto Sans CJK KR', 'Noto Sans KR', 'NanumGothic', 'Malgun Gothic', '맑은 고딕', 'Apple SD Gothic Neo', sans-serif;
    background: #ffffff;
    color: #333333;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page {{
    width: 210mm;
    height: 297mm;
    margin: 0 auto;
    padding: 18mm 20mm 15mm 20mm;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }}

  /* 헤더: 로고 영역 */
  .header {{
    text-align: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 2px solid #4a6741;
  }}

  .logo {{
    height: 70px;
    margin-bottom: 4px;
  }}

  .logo-text {{
    font-size: 22px;
    font-weight: 700;
    color: #4a6741;
    letter-spacing: 3px;
  }}

  /* 타이틀 영역 */
  .title-section {{
    text-align: center;
    margin-bottom: 16px;
  }}

  .main-title {{
    font-size: 22px;
    font-weight: 700;
    color: #4a6741;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }}

  .sub-info {{
    font-size: 13px;
    color: #666666;
    margin-bottom: 3px;
  }}

  .quarter-theme {{
    display: inline-block;
    background: #f0f5ed;
    color: #4a6741;
    font-size: 12px;
    font-weight: 500;
    padding: 3px 14px;
    border-radius: 12px;
    margin-top: 4px;
  }}

  /* 기도제목 영역 */
  .prayer-section {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-top: 8px;
  }}

  .prayer-block {{
    background: #fafcf9;
    border-left: 4px solid #4a6741;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
  }}

  .prayer-block.personal {{
    border-left-color: #8b9a2b;
  }}

  .section-title {{
    font-size: {sizes['title_size']};
    font-weight: 700;
    color: #4a6741;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .section-title.personal {{
    color: #6b7a1b;
  }}

  .section-icon {{
    font-size: 18px;
  }}

  .prayer-item {{
    font-size: {sizes['item_size']};
    line-height: {sizes['line_height']};
    color: #444444;
    margin-bottom: {sizes['item_gap']};
    padding-left: 4px;
  }}

  .item-num {{
    font-weight: 700;
    color: #4a6741;
    margin-right: 2px;
  }}

  .prayer-block.personal .item-num {{
    color: #6b7a1b;
  }}

  /* 푸터 */
  .footer {{
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px solid #dde5d9;
    text-align: center;
  }}

  .footer-text {{
    font-size: 11px;
    color: #999999;
  }}

  .scripture-badge {{
    display: inline-block;
    background: #4a6741;
    color: #ffffff;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 12px;
    border-radius: 10px;
    margin-bottom: 4px;
  }}

  @media print {{
    body {{ background: white; }}
    .page {{
      margin: 0;
      padding: 18mm 20mm 15mm 20mm;
      page-break-after: avoid;
    }}
  }}
</style>
</head>
<body>
<div class="page">

  <!-- 헤더 -->
  <div class="header">
    {logo_html}
  </div>

  <!-- 타이틀 -->
  <div class="title-section">
    <div class="main-title">2026 디딤수요기도회 기도제목</div>
    <div class="sub-info">{month}월 {week_text}</div>
    <div class="sub-info">
      <span class="scripture-badge">📖 {scripture}</span>
    </div>
    <div class="quarter-theme">✦ {quarter_theme} — {worship_title}</div>
  </div>

  <!-- 기도제목 -->
  <div class="prayer-section">

    <div class="prayer-block community">
      <div class="section-title">
        <span class="section-icon">🙏</span> 공동체를 위한 기도
      </div>
      {community_html}
    </div>

    <div class="prayer-block personal">
      <div class="section-title personal">
        <span class="section-icon">💛</span> 개인을 위한 기도
      </div>
      {personal_html}
    </div>

  </div>

  <!-- 푸터 -->
  <div class="footer">
    <div class="footer-text">디딤교회 DiDIM CHURCH | 수요기도회</div>
  </div>

</div>
</body>
</html>"""
    
    # 파일 저장
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    
    return str(out)


def get_output_path(base_dir: str, month: int, week: int, ext: str = "html", format: str = "a4") -> str:
    """
    월/주차별 출력 경로를 생성한다.
    예: base_dir/output/3월/2주차/기도제목_3월_2주차.html
        base_dir/output/3월/2주차/기도제목_3월_2주차_카드.html
    """
    output_dir = Path(base_dir) / "output" / f"{month}월" / f"{week}주차"
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_카드" if format == "card" else ""
    filename = f"기도제목_{month}월_{week}주차{suffix}.{ext}"
    return str(output_dir / filename)


def main():
    """CLI: python generate_html.py <data_json> <logo_path> <output_html>"""
    if len(sys.argv) != 4:
        print("Usage: python generate_html.py <data_json_path> <logo_path> <output_html>")
        sys.exit(1)
    
    data_path = sys.argv[1]
    logo_path = sys.argv[2]
    output_path = sys.argv[3]
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result = generate_prayer_html(data, logo_path, output_path)
    print(f"HTML 생성 완료: {result}")


if __name__ == "__main__":
    main()
