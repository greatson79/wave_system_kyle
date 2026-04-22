#!/usr/bin/env python3
"""
디딤수요기도회 기도제목 생성 파이프라인 통합 실행
CSV → 데이터 추출 → HTML 생성 → PNG 캡처까지 한 번에 실행한다.

Usage:
  python run_pipeline.py <csv_path> <month> <week> [--base-dir <path>]
  
Examples:
  python run_pipeline.py data.csv 3 2
  python run_pipeline.py data.csv 8 1 --base-dir "/Users/me/Desktop/ai works/claude skills/수요기도회"
"""

import sys
import json
import subprocess
import os
from pathlib import Path

# 같은 scripts 폴더의 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_prayer_data import extract_prayer_data
from generate_html import generate_prayer_html, get_output_path


def run_pipeline(csv_path: str, month: int, week: int, base_dir: str = None, format: str = 'a4'):
    """전체 파이프라인을 실행한다."""
    
    # 기본 경로 설정
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    if base_dir:
        project_dir = Path(base_dir).resolve()
    else:
        # 스크립트 위치에서 프로젝트 루트 추정
        # .claude/skills/prayer-doc/scripts/ → 4단계 상위
        project_dir = script_dir.parent.parent.parent.parent
    
    logo_path = str(project_dir / "src" / "assets" / "logos" / "prayer-logo.png")

    if not Path(logo_path).exists():
        # fallback: 디딤 메인 로고
        logo_path = str(project_dir / "src" / "assets" / "logos" / "didim-logo.png")
    
    format_label = "4:5 카드뉴스" if format == 'card' else "A4"
    print(f"=" * 50)
    print(f"  디딤수요기도회 기도제목 생성 [{format_label}]")
    print(f"  {month}월 {week}주차")
    print(f"=" * 50)
    
    # 1단계: 데이터 추출
    print(f"\n[1/3] 데이터 추출 중... ({csv_path})")
    data = extract_prayer_data(csv_path, month, week)
    
    if data["error"]:
        print(f"❌ 오류: {data['error']}")
        return None
    
    print(f"  ✅ 분기 주제: {data['quarter_theme']}")
    print(f"  ✅ 예배 제목: {data['worship_title']}")
    print(f"  ✅ 본문: {data['scripture']}")
    print(f"  ✅ 공동체 기도제목: {len(data['community_prayers'])}개")
    print(f"  ✅ 개인 기도제목: {len(data['personal_prayers'])}개")
    
    # 2단계: HTML 생성
    html_path = get_output_path(str(project_dir), month, week, "html", format)
    print(f"\n[2/3] HTML 생성 중... → {html_path}")

    generate_prayer_html(data, logo_path, html_path, format=format)
    print(f"  ✅ HTML 생성 완료")

    # 3단계: PNG 캡처
    png_path = get_output_path(str(project_dir), month, week, "png", format)
    print(f"\n[3/3] PNG 캡처 중... → {png_path}")

    # 캡처 사이즈 결정
    cap_width = "1080" if format == 'card' else "794"
    cap_height = "1350" if format == 'card' else "1123"

    # wkhtmltoimage 시도
    try:
        result = subprocess.run(
            [
                "wkhtmltoimage",
                "--width", cap_width,
                "--height", cap_height,
                "--quality", "100",
                "--enable-local-file-access",
                "--load-error-handling", "ignore",
                html_path,
                png_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  ✅ PNG 캡처 완료 (wkhtmltoimage)")
        else:
            print(f"  ⚠️ wkhtmltoimage 경고: {result.stderr[:200]}")
            # Puppeteer fallback 시도
            _try_puppeteer(html_path, png_path, script_dir, format)
    except FileNotFoundError:
        print(f"  ⚠️ wkhtmltoimage 미설치, Puppeteer로 시도...")
        _try_puppeteer(html_path, png_path, script_dir, format)
    except subprocess.TimeoutExpired:
        print(f"  ❌ PNG 캡처 타임아웃")
    
    # 결과 요약
    print(f"\n{'=' * 50}")
    print(f"  ✅ 생성 완료!")
    print(f"  HTML: {html_path}")
    print(f"  PNG:  {png_path}")
    print(f"{'=' * 50}")
    
    return {"html": html_path, "png": png_path}


def _try_puppeteer(html_path: str, png_path: str, script_dir: Path, format: str = 'a4'):
    """Puppeteer를 사용하여 PNG 캡처를 시도한다."""
    capture_js = str(script_dir / "capture_png.js")
    cmd = ["node", capture_js, html_path, png_path, "--format", format]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  ✅ PNG 캡처 완료 (Puppeteer)")
        else:
            print(f"  ❌ Puppeteer 실패: {result.stderr[:200]}")
    except Exception as e:
        print(f"  ❌ Puppeteer 실행 불가: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="디딤수요기도회 기도제목 생성")
    parser.add_argument("csv_path", help="CSV 파일 경로")
    parser.add_argument("month", type=int, help="월 (1-12)")
    parser.add_argument("week", type=int, help="주차 (1-5)")
    parser.add_argument("--base-dir", help="스킬 기본 경로 (기본: 스크립트 상위 폴더)")
    parser.add_argument("--format", choices=["a4", "card"], default="a4",
                        help="출력 형식: a4 (기본, 인쇄용) 또는 card (4:5 카드뉴스, 1080×1350px)")

    args = parser.parse_args()
    run_pipeline(args.csv_path, args.month, args.week, args.base_dir, args.format)


if __name__ == "__main__":
    main()
