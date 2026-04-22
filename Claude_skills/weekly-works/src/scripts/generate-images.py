"""
generate-images.py
------------------
image-prompts.txt를 읽어 Google Imagen 3 API로 이미지를 생성하고
output/{월}/{주차}/매일묵상/images/ 폴더에 저장합니다.

사용법:
    python generate-images.py <주차번호> <output경로>

예시:
    python generate-images.py 15 output/4월/2주차
"""

import os
import re
import sys
from pathlib import Path

from google import genai
from google.genai import types


DAYS = ["mon", "tue", "wed", "thu", "fri"]
DAY_MAP = {"MON": "mon", "TUE": "tue", "WED": "wed", "THU": "thu", "FRI": "fri"}


def parse_prompts(prompts_file: Path) -> dict:
    """image-prompts.txt에서 요일별 영어 프롬프트 추출 (Midjourney 플래그 제거)"""
    content = prompts_file.read_text(encoding="utf-8")
    sections = re.split(r'━+', content)

    prompts = {}
    for section in sections:
        lines = [l.strip() for l in section.strip().splitlines() if l.strip()]
        current_day = None
        for i, line in enumerate(lines):
            # [MON], [TUE] ... 헤더 감지
            m = re.match(r'\[(\w+)\]', line)
            if m and m.group(1).upper() in DAY_MAP:
                current_day = DAY_MAP[m.group(1).upper()]
                continue

            # 영어로 시작하는 프롬프트 라인 (제목: / # 제외)
            if current_day and re.match(r'^[A-Z]', line) and not line.startswith('#'):
                # Midjourney 전용 플래그 제거 (--ar, --v, --style 등)
                clean = re.sub(r'\s*--\w+\s*[\w.:]*', '', line).strip()
                prompts[current_day] = clean
                current_day = None  # 한 섹션에 프롬프트 1개

    return prompts


def generate(week: str, output_base: str):
    output_dir = Path(output_base)
    prompts_file = output_dir / "매일묵상" / "image-prompts.txt"
    images_dir   = output_dir / "매일묵상" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # ── 파일 확인
    if not prompts_file.exists():
        print(f"❌ image-prompts.txt 없음: {prompts_file}")
        sys.exit(1)

    # ── 프롬프트 파싱
    prompts = parse_prompts(prompts_file)
    if not prompts:
        print("❌ 프롬프트 파싱 실패 — image-prompts.txt 형식을 확인하세요")
        sys.exit(1)
    print(f"✅ 프롬프트 {len(prompts)}개 파싱 완료\n")

    # ── API 키 확인
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # ── 이미지 생성
    success = 0
    for day in DAYS:
        prompt = prompts.get(day)
        if not prompt:
            print(f"[{day.upper()}] ⚠️  프롬프트 없음 — 건너뜀")
            continue

        print(f"[{day.upper()}] 생성 중... ", end="", flush=True)
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )
            img_path = images_dir / f"{day}.png"
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img_path.write_bytes(part.inline_data.data)
                    print(f"✅ {img_path.name}")
                    success += 1
                    break

        except Exception as e:
            print(f"❌ 실패: {e}")

    print(f"\n{'✅' if success == len(prompts) else '⚠️ '} {success}/{len(prompts)}개 완료 → {images_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python generate-images.py <주차번호> <output경로>")
        print("예시:   python generate-images.py 15 output/4월/2주차")
        sys.exit(1)

    generate(week=sys.argv[1], output_base=sys.argv[2])
