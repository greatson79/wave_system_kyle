"""
insert-images.py
-----------------
1. 매일묵상 HTML의 이미지 플레이스홀더를 로컬 상대 경로로 교체
2. A4 HTML을 PNG로 캡처

사용법:
    python insert-images.py <주차번호> <output경로>

예시:
    python insert-images.py 15 output/4월/2주차
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

DAYS = ["mon", "tue", "wed", "thu", "fri"]


def replace_placeholders(html: str, img_url: str, orig_url: str) -> str:
    html = html.replace("[이미지_URL]", img_url)
    html = html.replace("[이미지_원본_URL]", orig_url)
    return html


def run(week: str, output_base: str):
    base_dir = Path(__file__).resolve().parents[2]
    output_dir = base_dir / output_base
    images_dir = output_dir / "매일묵상" / "images"
    html_orig = output_dir / "매일묵상" / "html-original"
    html_out = output_dir / "매일묵상" / "html-with-images"
    html_out.mkdir(parents=True, exist_ok=True)

    # ── 이미지 파일 확인
    image_files = {}
    for day in DAYS:
        for ext in ["png", "jpg", "jpeg", "webp"]:
            p = images_dir / f"{day}.{ext}"
            if p.exists():
                image_files[day] = p
                break
    print(f"✅ 이미지 {len(image_files)}/5개 확인: {list(image_files.keys())}\n")

    # ── HTML 파일 처리
    print("📝 HTML 파일 이미지 삽입 중...")
    success = 0
    for day in DAYS:
        if day not in image_files:
            print(f"  [{day.upper()}] 이미지 없음 — 건너뜀")
            continue

        local_rel = f"../images/{day}.png"
        for variant in ["adult-a4", "youth-a4", "adult-wordpress"]:
            src_file = html_orig / f"{day}-{variant}.html"
            if not src_file.exists():
                print(f"  [{day}-{variant}] 파일 없음 — 건너뜀")
                continue

            html = src_file.read_text(encoding="utf-8")
            needs_insert = "[이미지_URL]" in html or "[이미지_원본_URL]" in html
            if not needs_insert:
                # 두 플레이스홀더 모두 없음 → 완전히 삽입된 상태
                shutil.copy(src_file, html_out / src_file.name)
                print(f"  [{day}-{variant}] 이미 삽입됨 — 복사")
                success += 1
                continue

            new_html = replace_placeholders(html, local_rel, local_rel)

            out_file = html_out / src_file.name
            out_file.write_text(new_html, encoding="utf-8")
            print(f"  [{day}-{variant}] ✅ (로컬 경로)")
            success += 1

    print(f"\n✅ HTML 처리 완료 {success}/15\n")

    # ── A4 캡쳐 (Puppeteer — 인라인 스크립트)
    captured_dir = output_dir / "매일묵상" / "captured"
    captured_dir.mkdir(parents=True, exist_ok=True)
    print("📸 A4 캡쳐 시작...")

    inline_js = f"""
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE = {json.dumps(str(html_out))};
const OUT  = {json.dumps(str(captured_dir))};
const DAYS  = ['mon','tue','wed','thu','fri'];
const TYPES = ['adult-a4','youth-a4'];

(async () => {{
  const browser = await puppeteer.launch({{ headless: 'new' }});
  const page = await browser.newPage();
  await page.setViewport({{ width: 794, height: 1123, deviceScaleFactor: 2 }});
  let success = 0;
  for (const day of DAYS) {{
    for (const type of TYPES) {{
      const htmlFile = path.join(BASE, day + '-' + type + '.html');
      const pngFile  = path.join(OUT,  day + '-' + type + '.png');
      if (!fs.existsSync(htmlFile)) {{ console.log('건너뜀: ' + day + '-' + type); continue; }}
      await page.goto('file://' + htmlFile, {{ waitUntil: 'networkidle0', timeout: 15000 }});
      await page.evaluate(() => document.fonts.ready);
      await new Promise(r => setTimeout(r, 1000));
      await page.evaluate(() => {{ const el = document.querySelector('.page'); if (el) {{ el.style.height = 'auto'; el.style.minHeight = '297mm'; }} }});
      const el = await page.$('.page');
      if (el) await el.screenshot({{ path: pngFile, type: 'png' }});
      else await page.screenshot({{ path: pngFile, type: 'png' }});
      console.log('✓ ' + day + '-' + type + '.png');
      success++;
    }}
  }}
  await browser.close();
  console.log('완료: ' + success + '개');
}})();
"""
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, dir=str(base_dir)) as tmp:
        tmp.write(inline_js)
        tmp_path = tmp.name

    result = subprocess.run(
        ["node", tmp_path],
        capture_output=True, text=True, cwd=str(base_dir)
    )
    os.unlink(tmp_path)

    if result.returncode == 0:
        png_count = len(list(captured_dir.glob("*.png")))
        print(result.stdout)
        print(f"✅ PNG {png_count}개 캡쳐 완료 → {captured_dir}")
    else:
        print(f"❌ 캡쳐 실패: {result.stderr[:400]}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 이미지 삽입 완료 — {week}주차 ({output_base})
├── html-with-images/: {success}개 HTML
├── images/: {len(image_files)}개 이미지
└── 모든 HTML: 로컬 이미지 경로
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python insert-images.py <주차번호> <output경로>")
        sys.exit(1)
    run(week=sys.argv[1], output_base=sys.argv[2])
