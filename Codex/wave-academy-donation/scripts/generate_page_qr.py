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
draw.rounded_rectangle(
    (qr_x - 34, qr_y - 34, qr_x + qr_size + 34, qr_y + qr_size + 34),
    radius=8,
    fill="white",
    outline="#d8e0e8",
    width=4,
)
card.paste(qr_resized, (qr_x, qr_y))

caption = "스캔하면 후원강의 안내와 계좌정보를 확인할 수 있습니다."
bbox = draw.textbbox((0, 0), caption, font=body_font)
draw.text(((W - (bbox[2] - bbox[0])) // 2, H - 210), caption, font=body_font, fill="#073565")

card_path = QR_DIR / "wave-academy-donation-page-card.png"
card.save(card_path, quality=95)

print(url)
print(qr_path.resolve())
print(card_path.resolve())
