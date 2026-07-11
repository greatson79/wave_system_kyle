# Wave Academy Donation Landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a Vercel-ready landing page for the Wave Academy donation lecture, using `/donation` as the canonical route, `/donationd` as a compatibility redirect, and a connected donation account flow for KakaoBank.

**Architecture:** Create a small static site in `wave-academy-donation/` so it can be deployed directly by Vercel without a build framework or dependency install. The page will use the supplied card-news PNG files as source-backed visual assets, native HTML/CSS/JS for the landing experience, and generated QR assets for the final donation page URL. The donation account connection is an explicit copy-and-confirm flow, not an automatic bank transfer or hidden payment flow.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, local Python verification scripts, local Python QR generation with existing `qrcode` and Pillow packages, Vercel static deployment.

---

## Scope And Risk Note

- Change class: `feature` plus `infra`.
- Public deployment risk: Vercel deployment requires network access and user approval.
- Payment-adjacent risk: The page displays donation account details and copy buttons only. It does not initiate a transfer, store payment information, or call banking/payment APIs.
- Third-party avoidance: The canonical page and new page QR should not depend on `free4qr.com`. Existing bank-select QR files may remain in `output/qr/`, but this landing page should point users to the owned Vercel page and show the KakaoBank account directly.
- Canonical route: `/donation`.
- Compatibility route: `/donationd` redirects to `/donation`.
- Account details:
  - Bank: `카카오뱅크`
  - Account: `79422890725`
  - Holder: `최종학`
  - Store/program name: `Wave academy`

## File Structure

- Create `wave-academy-donation/package.json`
  - Records static project scripts: `verify`, `generate:qr`.
- Create `wave-academy-donation/vercel.json`
  - Configures static Vercel routing and clean headers.
- Create `wave-academy-donation/index.html`
  - Redirects root traffic to `/donation/`.
- Create `wave-academy-donation/donation/index.html`
  - Canonical landing page.
- Create `wave-academy-donation/donationd/index.html`
  - Compatibility redirect page from `/donationd` to `/donation`.
- Create `wave-academy-donation/styles.css`
  - Complete responsive visual system based on the supplied card-news palette.
- Create `wave-academy-donation/app.js`
  - Copy buttons, share button, card-news lightbox, and progressive enhancement.
- Create `wave-academy-donation/scripts/verify_static.py`
  - Local static checks for required copy, account data, routes, images, and third-party QR dependency avoidance.
- Create `wave-academy-donation/scripts/generate_page_qr.py`
  - Generates QR assets that point to the final `/donation` page URL.
- Create `wave-academy-donation/assets/cardnews/card-01.png` through `card-10.png`
  - Copied from the KakaoTalk card-news files in `/Users/kylechoi/Downloads`.
- Create `wave-academy-donation/assets/qr/wave-academy-donation-page-qr.png`
  - Generated after final URL is known.
- Create `wave-academy-donation/assets/qr/wave-academy-donation-page-card.png`
  - Printable/shareable QR card generated after final URL is known.

## Content Inventory

Hero copy:

```text
Wave always be with you
5인5색 Ai collaboration summer class 2026
AI, 이제 혼자 쓰지 마세요
무료 Zoom 강의 · 자율 후원
7.14 - 8.18 · 화요일 저녁 8:00-10:00
```

Lecture schedule:

```text
7/14 Codex로 시작하는 AI 에이전트 워크플로우 — 최종학 대표
7/21 Suno로 만드는 AI 음악 콘텐츠 — 이지철 강사
7/28 이미지 & 영상 생성형 AI 콘텐츠 — 이신혜 이사
8/11 목회 Wiki, 사역 지식창고 — 이진민 이사
8/18 GPT와 함께 만드는 SNS 브랜딩 & 카드뉴스 — 김제준 강사
```

Participation and donation copy:

```text
이번 여름 강의는 후원강의로 진행합니다. 후원과 후원금은 자율입니다.
Zoom 강의: 7.14 - 8.18 화요일 저녁 8:00-10:00
후기 작성자: 강의 자료를 배포합니다.
후원자: 강의 녹화영상을 제공합니다.
카카오뱅크 79422890725 예금주 최종학
```

## Task 1: Create Static Project Shell

**Files:**
- Create: `wave-academy-donation/package.json`
- Create: `wave-academy-donation/vercel.json`
- Create: `wave-academy-donation/index.html`
- Create: `wave-academy-donation/donationd/index.html`

- [ ] **Step 1: Create the project folders**

Run:

```bash
mkdir -p wave-academy-donation/donation wave-academy-donation/donationd wave-academy-donation/assets/cardnews wave-academy-donation/assets/qr wave-academy-donation/scripts
```

Expected: command exits `0` and the directories exist.

- [ ] **Step 2: Add `package.json`**

Create `wave-academy-donation/package.json` with:

```json
{
  "name": "wave-academy-donation",
  "version": "1.0.0",
  "private": true,
  "description": "Wave Academy donation lecture landing page",
  "scripts": {
    "verify": "python3 scripts/verify_static.py",
    "generate:qr": "python3 scripts/generate_page_qr.py"
  }
}
```

- [ ] **Step 3: Add `vercel.json`**

Create `wave-academy-donation/vercel.json` with:

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/donationd",
      "destination": "/donation"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

- [ ] **Step 4: Add root redirect page**

Create `wave-academy-donation/index.html` with:

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="0; url=/donation/">
    <link rel="canonical" href="/donation/">
    <title>Wave Academy 후원강의</title>
  </head>
  <body>
    <a href="/donation/">Wave Academy 후원강의 페이지로 이동</a>
  </body>
</html>
```

- [ ] **Step 5: Add `/donationd` compatibility redirect page**

Create `wave-academy-donation/donationd/index.html` with:

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="0; url=/donation/">
    <link rel="canonical" href="/donation/">
    <title>Wave Academy 후원강의</title>
  </head>
  <body>
    <a href="/donation/">Wave Academy 후원강의 페이지로 이동</a>
  </body>
</html>
```

## Task 2: Copy Card-News Source Assets

**Files:**
- Create: `wave-academy-donation/assets/cardnews/card-01.png`
- Create: `wave-academy-donation/assets/cardnews/card-02.png`
- Create: `wave-academy-donation/assets/cardnews/card-03.png`
- Create: `wave-academy-donation/assets/cardnews/card-04.png`
- Create: `wave-academy-donation/assets/cardnews/card-05.png`
- Create: `wave-academy-donation/assets/cardnews/card-06.png`
- Create: `wave-academy-donation/assets/cardnews/card-07.png`
- Create: `wave-academy-donation/assets/cardnews/card-08.png`
- Create: `wave-academy-donation/assets/cardnews/card-09.png`
- Create: `wave-academy-donation/assets/cardnews/card-10.png`

- [ ] **Step 1: Copy the supplied images into stable asset names**

Run:

```bash
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 001.png" wave-academy-donation/assets/cardnews/card-01.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 002.png" wave-academy-donation/assets/cardnews/card-02.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 003.png" wave-academy-donation/assets/cardnews/card-03.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 004.png" wave-academy-donation/assets/cardnews/card-04.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 005.png" wave-academy-donation/assets/cardnews/card-05.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 006.png" wave-academy-donation/assets/cardnews/card-06.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 007.png" wave-academy-donation/assets/cardnews/card-07.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 008.png" wave-academy-donation/assets/cardnews/card-08.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 009.png" wave-academy-donation/assets/cardnews/card-09.png
cp "/Users/kylechoi/Downloads/KakaoTalk_Photo_2026-07-04-20-44-31 010.png" wave-academy-donation/assets/cardnews/card-10.png
```

Expected: all commands exit `0`.

- [ ] **Step 2: Verify dimensions**

Run:

```bash
sips -g pixelWidth -g pixelHeight wave-academy-donation/assets/cardnews/card-01.png
```

Expected: `pixelWidth: 960` and `pixelHeight: 1200`.

Run:

```bash
find wave-academy-donation/assets/cardnews -name "card-*.png" -maxdepth 1 | wc -l
```

Expected: `10`.

## Task 3: Build Canonical `/donation` Page

**Files:**
- Create: `wave-academy-donation/donation/index.html`
- Create: `wave-academy-donation/styles.css`
- Create: `wave-academy-donation/app.js`

- [ ] **Step 1: Add canonical landing page markup**

Create `wave-academy-donation/donation/index.html` with sections in this order:

```text
1. Fixed/simple header with brand and CTA anchors
2. Full first viewport hero
3. Quick facts band
4. Five lecture schedule
5. Participation guide
6. Donation account module
7. Card-news gallery
8. Final CTA
```

The page must include these exact account strings once in visible text:

```text
카카오뱅크
79422890725
최종학
```

The primary account copy button must use:

```html
<button class="copy-button" type="button" data-copy="79422890725">계좌번호 복사</button>
```

The full account copy button must use:

```html
<button class="copy-button secondary" type="button" data-copy="카카오뱅크 79422890725 최종학">계좌 정보 복사</button>
```

- [ ] **Step 2: Add visual system CSS**

Create `wave-academy-donation/styles.css` with these design tokens at the top:

```css
:root {
  --navy: #063f78;
  --navy-dark: #073565;
  --pink: #f23868;
  --teal: #0d9ba8;
  --orange: #ff7a17;
  --yellow: #ffc20e;
  --cream: #fff2d6;
  --paper: #fff8eb;
  --ink: #073565;
  --muted: #55708a;
  --line: rgba(7, 53, 101, 0.16);
  --shadow: 0 18px 48px rgba(7, 53, 101, 0.18);
  --radius: 8px;
}
```

Responsive requirements:

```text
Desktop: content max-width 1120px, hero fills first viewport with next section hinted below.
Tablet: schedule cards become two-column where space allows.
Mobile: all sections stack, CTA buttons fit within parent width, card-news images use full width.
```

- [ ] **Step 3: Add interaction script**

Create `wave-academy-donation/app.js` with:

```javascript
const copyButtons = document.querySelectorAll("[data-copy]");
const statusNode = document.querySelector("[data-copy-status]");

function setStatus(message) {
  if (!statusNode) return;
  statusNode.textContent = message;
  window.setTimeout(() => {
    statusNode.textContent = "";
  }, 2200);
}

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.top = "-999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

copyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const value = button.getAttribute("data-copy") || "";
    try {
      await copyText(value);
      setStatus("복사되었습니다.");
    } catch (error) {
      setStatus("복사에 실패했습니다. 계좌번호를 직접 선택해 주세요.");
    }
  });
});
```

- [ ] **Step 4: Keep bank transfer behavior explicit**

Do not add app deep links or automatic transfer links. The donation module should say:

```text
계좌번호를 복사한 뒤 사용하시는 은행 앱에서 예금주 최종학을 확인하고 이체해 주세요.
```

## Task 4: Add Static Verification

**Files:**
- Create: `wave-academy-donation/scripts/verify_static.py`

- [ ] **Step 1: Add verification script**

Create `wave-academy-donation/scripts/verify_static.py` with:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONATION = ROOT / "donation" / "index.html"
DONATIOND = ROOT / "donationd" / "index.html"
STYLE = ROOT / "styles.css"
APP = ROOT / "app.js"
CARDS = ROOT / "assets" / "cardnews"

required_files = [
    DONATION,
    DONATIOND,
    STYLE,
    APP,
    ROOT / "index.html",
    ROOT / "vercel.json",
]

for path in required_files:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

html = DONATION.read_text(encoding="utf-8")
redirect = DONATIOND.read_text(encoding="utf-8")
css = STYLE.read_text(encoding="utf-8")
js = APP.read_text(encoding="utf-8")

required_copy = [
    "Wave always be with you",
    "5인5색 Ai collaboration summer class 2026",
    "7.14 - 8.18",
    "화요일 저녁 8:00-10:00",
    "카카오뱅크",
    "79422890725",
    "최종학",
    "계좌번호 복사",
    "계좌 정보 복사",
]

for text in required_copy:
    if text not in html:
        raise SystemExit(f"Missing required copy: {text}")

for card_number in range(1, 11):
    path = CARDS / f"card-{card_number:02d}.png"
    if not path.exists():
        raise SystemExit(f"Missing card image: {path}")
    if f"assets/cardnews/card-{card_number:02d}.png" not in html:
        raise SystemExit(f"Card image not referenced: card-{card_number:02d}.png")

blocked_strings = [
    "free4qr.com",
    "tel:",
    "kakaobank://",
]

for blocked in blocked_strings:
    if blocked in html or blocked in js:
        raise SystemExit(f"Blocked dependency or unsafe link found: {blocked}")

if "/donation/" not in redirect:
    raise SystemExit("donationd redirect does not point to /donation/")

for token in ["--navy", "--pink", "--teal", "--yellow"]:
    if token not in css:
        raise SystemExit(f"Missing CSS token: {token}")

for snippet in ["navigator.clipboard", "data-copy", "복사되었습니다."]:
    if snippet not in js:
        raise SystemExit(f"Missing JS behavior: {snippet}")

print("Static verification passed.")
```

- [ ] **Step 2: Run static verification and confirm it fails before implementation is complete**

Run after creating the script but before finishing page markup:

```bash
cd wave-academy-donation && npm run verify
```

Expected: FAIL with a message naming the first missing file, missing copy, or missing card reference.

- [ ] **Step 3: Run static verification after implementation**

Run:

```bash
cd wave-academy-donation && npm run verify
```

Expected:

```text
Static verification passed.
```

## Task 5: Generate Donation Page QR Assets

**Files:**
- Create: `wave-academy-donation/scripts/generate_page_qr.py`
- Create: `wave-academy-donation/assets/qr/wave-academy-donation-page-qr.png`
- Create: `wave-academy-donation/assets/qr/wave-academy-donation-page-card.png`
- Modify: `wave-academy-donation/donation/index.html`

- [ ] **Step 1: Add QR generation script**

Create `wave-academy-donation/scripts/generate_page_qr.py` with:

```python
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H

ROOT = Path(__file__).resolve().parents[1]
QR_DIR = ROOT / "assets" / "qr"
QR_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_URL = "https://wave-academy-donation.vercel.app/donation"
url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

if not url.startswith("https://"):
    raise SystemExit("Donation QR URL must start with https://")

qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=24, border=4)
qr.add_data(url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#111111", back_color="white").convert("RGB")
qr_path = QR_DIR / "wave-academy-donation-page-qr.png"
qr_img.save(qr_path)

font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
title_font = ImageFont.truetype(font_path, 72)
body_font = ImageFont.truetype(font_path, 34)

W, H = 1400, 1800
card = Image.new("RGB", (W, H), "#fff8eb")
draw = ImageDraw.Draw(card)
draw.rectangle((0, 0, W, 280), fill="#073565")
draw.text((90, 86), "Wave Academy", font=title_font, fill="white")
draw.text((94, 178), "후원강의 안내 QR", font=body_font, fill="#ffc20e")

qr_size = 1000
qr_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.NEAREST)
qr_x = (W - qr_size) // 2
qr_y = 380
draw.rounded_rectangle((qr_x - 34, qr_y - 34, qr_x + qr_size + 34, qr_y + qr_size + 34), radius=8, fill="white", outline="#d8e0e8", width=4)
card.paste(qr_resized, (qr_x, qr_y))

caption = "스캔하면 후원강의 안내와 계좌정보를 확인할 수 있습니다."
bbox = draw.textbbox((0, 0), caption, font=body_font)
draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 210), caption, font=body_font, fill="#073565")

card_path = QR_DIR / "wave-academy-donation-page-card.png"
card.save(card_path, quality=95)

print(url)
print(qr_path.resolve())
print(card_path.resolve())
```

- [ ] **Step 2: Generate provisional QR assets**

Run:

```bash
cd wave-academy-donation && python3 scripts/generate_page_qr.py
```

Expected: command prints the default Vercel URL plus two PNG paths.

- [ ] **Step 3: Reference QR assets in the page**

Add this image in the donation account module:

```html
<img src="../assets/qr/wave-academy-donation-page-qr.png" alt="Wave Academy 후원강의 안내 QR">
```

- [ ] **Step 4: Regenerate QR with the final deployed URL after Vercel deployment**

After Vercel prints the production URL, run this command with that exact URL plus `/donation`:

```bash
cd wave-academy-donation && python3 scripts/generate_page_qr.py "https://wave-academy-donation.vercel.app/donation"
```

Expected: the QR payload points to the production `/donation` page.

If Vercel prints a different production host, replace only the host in the command and keep `/donation` as the path.

## Task 6: Local Browser And File Verification

**Files:**
- Verify: `wave-academy-donation/donation/index.html`
- Verify: `wave-academy-donation/styles.css`
- Verify: `wave-academy-donation/app.js`
- Verify: `wave-academy-donation/assets/qr/wave-academy-donation-page-qr.png`

- [ ] **Step 1: Run static verification**

Run:

```bash
cd wave-academy-donation && npm run verify
```

Expected:

```text
Static verification passed.
```

- [ ] **Step 2: Start a local static server for visual QA**

Run:

```bash
cd wave-academy-donation && python3 -m http.server 4173
```

Expected: terminal prints `Serving HTTP on :: port 4173` or `Serving HTTP on 0.0.0.0 port 4173`.

- [ ] **Step 3: Inspect local routes**

Open:

```text
http://localhost:4173/donation/
http://localhost:4173/donationd/
```

Expected:

```text
/donation/ shows the landing page.
/donationd/ redirects or links immediately to /donation/.
```

- [ ] **Step 4: Test account copy interaction**

Click:

```text
계좌번호 복사
계좌 정보 복사
```

Expected visible status:

```text
복사되었습니다.
```

- [ ] **Step 5: Visual QA checkpoints**

Check desktop and mobile widths:

```text
Desktop: hero has Wave title, subtitle, schedule, CTA, and next-section hint.
Mobile: no horizontal overflow; CTA buttons wrap cleanly; account number remains readable.
Card gallery: all 10 cards load in sequence.
Donation module: bank, account number, holder, copy buttons, and QR image are visible.
No free4qr logo or external free4qr dependency appears.
```

- [ ] **Step 6: Stop local server**

Use `Ctrl-C` in the server terminal.

Expected: no local server remains running for this task.

## Task 7: Vercel Deployment

**Files:**
- Deploy root: `wave-academy-donation/`
- May modify after deploy: `wave-academy-donation/assets/qr/wave-academy-donation-page-qr.png`
- May modify after deploy: `wave-academy-donation/assets/qr/wave-academy-donation-page-card.png`

- [ ] **Step 1: Check whether Vercel CLI is available**

Run:

```bash
vercel --version
```

Expected: prints a Vercel CLI version.

If command is not found, request approval to run:

```bash
npx vercel@latest --version
```

- [ ] **Step 2: Deploy preview**

Run from the static site folder:

```bash
cd wave-academy-donation && vercel
```

Expected:

```text
Vercel prints a preview deployment URL.
```

If Vercel prompts for project setup:

```text
Set up and deploy: Yes
Which scope: use the user's selected account
Link to existing project: No
Project name: wave-academy-donation
Directory: ./
Override settings: No
```

- [ ] **Step 3: Deploy production**

Run:

```bash
cd wave-academy-donation && vercel --prod
```

Expected:

```text
Vercel prints a production URL.
```

- [ ] **Step 4: Regenerate QR using production URL**

Run with the production URL printed by Vercel:

```bash
cd wave-academy-donation && python3 scripts/generate_page_qr.py "https://wave-academy-donation.vercel.app/donation"
```

Expected: QR PNG and QR card PNG are regenerated.

- [ ] **Step 5: Redeploy production with final QR assets**

Run:

```bash
cd wave-academy-donation && vercel --prod
```

Expected:

```text
The same production project is updated with final QR assets.
```

- [ ] **Step 6: Verify deployed URLs**

Open:

```text
https://wave-academy-donation.vercel.app/donation
https://wave-academy-donation.vercel.app/donationd
```

Expected:

```text
/donation displays the full landing page.
/donationd reaches the same canonical donation page.
The account copy buttons work in the deployed HTTPS context.
The QR image points back to the production /donation URL.
```

If Vercel prints a different host, use that host in the verification URLs.

## Task 8: Completion Report

**Files:**
- Report: final assistant response

- [ ] **Step 1: Summarize changed files**

Include:

```text
wave-academy-donation/
wave-academy-donation/donation/index.html
wave-academy-donation/donationd/index.html
wave-academy-donation/styles.css
wave-academy-donation/app.js
wave-academy-donation/assets/cardnews/
wave-academy-donation/assets/qr/
wave-academy-donation/scripts/
```

- [ ] **Step 2: Summarize verification**

Include exact results for:

```text
npm run verify
local desktop visual QA
local mobile visual QA
QR payload verification
Vercel preview URL
Vercel production URL
```

- [ ] **Step 3: State limitations**

Use this wording if no custom domain is connected:

```text
Custom domain connection is not included yet. Current production URL is the Vercel URL; QR assets can be regenerated after waveacademy.kr is connected.
```

- [ ] **Step 4: State donation safety**

Use this wording:

```text
The page does not initiate a transfer automatically. It shows the KakaoBank account and provides copy buttons so the donor can confirm the 예금주 before sending.
```

## Self-Review Checklist

- [ ] `/donation` is canonical.
- [ ] `/donationd` redirects to `/donation`.
- [ ] All 10 user-provided card-news images are copied and referenced.
- [ ] The page includes the user-provided title and subtitle.
- [ ] The five lecture dates and instructors match the card news.
- [ ] Donation account details match the user-provided account.
- [ ] The account flow avoids automatic bank transfer behavior.
- [ ] The new donation page QR does not depend on `free4qr.com`.
- [ ] Static verification checks for required copy, assets, unsafe strings, and copy behavior.
- [ ] Vercel deployment is gated behind explicit network approval.
- [ ] Final production URL is used to regenerate QR assets before final handoff.
