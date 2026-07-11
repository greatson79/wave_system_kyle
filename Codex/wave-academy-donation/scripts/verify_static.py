import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONATION = ROOT / "donation" / "index.html"
SHARE = ROOT / "donation-20260706" / "index.html"
DONATIOND = ROOT / "donationd" / "index.html"
HOME = ROOT / "index.html"
STYLE = ROOT / "styles.css"
APP = ROOT / "app.js"
QR = ROOT / "assets" / "qr" / "wave-academy-donation-page-qr.png"
PROVIDED_QR = ROOT / "assets" / "qr" / "wave-academy-provided-donation-qr.png"
KAKAO_PREVIEW = ROOT / "assets" / "og" / "wave-academy-kakao-preview-20260706.png"

required_files = [
    DONATION,
    SHARE,
    DONATIOND,
    STYLE,
    APP,
    HOME,
    ROOT / "vercel.json",
    QR,
    PROVIDED_QR,
    KAKAO_PREVIEW,
]

for path in required_files:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

html = DONATION.read_text(encoding="utf-8")
share_html = SHARE.read_text(encoding="utf-8")
home_html = HOME.read_text(encoding="utf-8")
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
    "자율 후원하기",
    "랜딩페이지 QR",
    "제공 QR",
    "후원 계좌 QR",
    "은행 선택 화면",
    "후원자는 강의 녹화영상을 받아볼 수 있습니다.",
    "후기 작성 링크",
    "후기 링크 준비중",
    "Codex로 시작하는 AI 에이전트 워크플로우",
    "Suno로 만드는 AI 음악 콘텐츠",
    "이미지 & 영상 생성형 AI 콘텐츠",
    "목회 Wiki, 사역 지식창고",
    "GPT와 함께 만드는 SNS 브랜딩 & 카드뉴스",
    "최종학 대표",
    "이지철 강사",
    "이신혜 강사",
    "이진민 강사",
    "김제준 강사",
    "Wave AI Networks",
    "연락처",
    "010.3094.8899",
    "이메일",
    "waveainetworks@gmail.com",
    "대표",
    "개인정보 관련 문의와 요청은 이메일로 접수합니다.",
    "맨 위",
]

for text in required_copy:
    if text not in html:
        raise SystemExit(f"Missing required copy: {text}")

review_match = re.search(r"<a[^>]*data-review-link[^>]*>", html)
if not review_match:
    raise SystemExit("Missing review link placeholder")

review_tag = review_match.group(0)
for snippet in ['class="review-link is-disabled"', 'data-review-url=""', 'aria-disabled="true"', 'tabindex="-1"']:
    if snippet not in review_tag:
        raise SystemExit(f"Review link placeholder is missing: {snippet}")

if "href=" in review_tag:
    raise SystemExit("Review link placeholder must not include href before a real URL is configured")

for snippet in ['class="footer-nav"', 'href="#top"', 'href="#schedule"', 'href="#donation"', 'mailto:waveainetworks@gmail.com']:
    if snippet not in html:
        raise SystemExit(f"Missing footer navigation or contact link: {snippet}")

for snippet in ["qr-grid", "wave-academy-donation-page-qr.png", "wave-academy-provided-donation-qr.png"]:
    if snippet not in html:
        raise SystemExit(f"Missing QR layout or asset reference: {snippet}")

for snippet in [
    '<meta property="og:image" content="https://wave-academy-donation.vercel.app/assets/og/wave-academy-kakao-preview-20260706.png">',
    '<meta property="og:image:width" content="727">',
    '<meta property="og:image:height" content="413">',
    '<meta property="og:image:alt" content="Wave Academy Summer Open Lecture 대표 이미지">',
    '<meta name="twitter:card" content="summary_large_image">',
    '<meta name="twitter:image" content="https://wave-academy-donation.vercel.app/assets/og/wave-academy-kakao-preview-20260706.png">',
]:
    if snippet not in html:
        raise SystemExit(f"Missing social preview meta: {snippet}")

for snippet in [
    '<meta property="og:image" content="https://wave-academy-donation.vercel.app/assets/og/wave-academy-kakao-preview-20260706.png">',
    '<meta property="og:image:width" content="727">',
    '<meta property="og:image:height" content="413">',
]:
    if snippet not in home_html:
        raise SystemExit(f"Missing home social preview meta: {snippet}")

for snippet in [
    '<meta property="og:url" content="https://wave-academy-donation.vercel.app/donation-20260706/">',
    '<meta property="og:image" content="https://wave-academy-donation.vercel.app/assets/og/wave-academy-kakao-preview-20260706.png">',
    "Wave always be with you",
    "자율 후원하기",
]:
    if snippet not in share_html:
        raise SystemExit(f"Missing share route content or meta: {snippet}")

blocked_strings = [
    "free4qr.com",
    "tel:",
    "kakaobank://",
    "후원 계좌 보기",
    "이사",
    "카드뉴스 요약",
    "Card news digest",
    "cardnews-section",
    "digest-grid",
    'href="#"',
    "example.com",
    "javascript:",
    "고유번호",
    "216-82-70640",
    '<meta property="og:image" content="../assets/qr/',
]

for blocked in blocked_strings:
    if blocked in html or blocked in share_html or blocked in home_html or blocked in js:
        raise SystemExit(f"Blocked dependency or unsafe link found: {blocked}")

for blocked in ["cardnews-section", "digest-grid"]:
    if blocked in css:
        raise SystemExit(f"Unused cardnews CSS found: {blocked}")

if "/donation/" not in redirect:
    raise SystemExit("donationd redirect does not point to /donation/")

for token in ["--navy", "--pink", "--teal", "--yellow"]:
    if token not in css:
        raise SystemExit(f"Missing CSS token: {token}")

for snippet in [
    "navigator.clipboard",
    "data-copy",
    "복사되었습니다.",
    "data-review-link",
    "data-review-url",
    "setupReviewLink",
    "reviewLink.href = parsedUrl.href;",
    'reviewLink.textContent = "후기 작성하기";',
]:
    if snippet not in js:
        raise SystemExit(f"Missing JS behavior: {snippet}")

print("Static verification passed.")
