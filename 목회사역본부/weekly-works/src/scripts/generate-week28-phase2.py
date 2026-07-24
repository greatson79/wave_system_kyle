from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/7월/2주차"
SG_OUT = OUT / "소그룹나눔지"
CN_OUT = OUT / "카드뉴스"
SERMON = OUT / "설교" / "sermon-context.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def html_wrap(title: str, body: str, extra_css: str = "") -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #f7f6f1;
      color: #223033;
      font-family: -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;
    }}
    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto;
      padding: 18mm 16mm 16mm;
      background: #fbfaf5;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    a {{ color: inherit; }}
    {extra_css}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def make_small_group(context: dict[str, str]) -> None:
    title = context["title"]
    scripture = context["scripture"]
    month = "7월"
    week_label = "2주차"

    adult_html = html_wrap(
        "장년 소그룹 나눔지",
        f"""
<main class="page">
  <section style="border-bottom:2px solid #4f6b4a;padding-bottom:12px;margin-bottom:18px;">
    <div style="font-size:12px;color:#6d7b72;letter-spacing:.08em;">DI D IM CHURCH · SMALL GROUP</div>
    <h1 style="font-size:28px;line-height:1.25;color:#32453a;margin-top:8px;">{title}</h1>
    <p style="margin-top:8px;font-size:14px;color:#5d6a61;">로마서 15:1-7 · {month} {week_label}</p>
  </section>

  <section style="margin-bottom:18px;">
    <h2 style="font-size:18px;color:#32453a;margin-bottom:8px;">이번 주 말씀 요약</h2>
    <p style="font-size:13.5px;line-height:1.8;">강한 사람은 자기 편함과 권리를 앞세우기보다 연약한 이의 짐을 함께 짊어질 때 복음의 길을 따르게 됩니다. 예수님은 자기 기쁨을 붙잡지 않으시고 우리를 받아 주셨고, 그 환대가 공동체의 기준이 됩니다. 이번 주 말씀은 남을 품는 것이 손해가 아니라 주님을 닮는 예배라는 사실을 보여 줍니다. 그리스도 안에서 우리는 서로를 판단하는 자리에서 함께 짐지는 자리로 부름받습니다.</p>
  </section>

  <section style="margin-bottom:18px;">
    <h2 style="font-size:18px;color:#32453a;margin-bottom:8px;">팀장 서론 이야기</h2>
    <p style="font-size:13.5px;line-height:1.8;">스페인의 화가 벨라스케스는 궁정화가로 이름을 얻었지만, 그의 대표작인 &lt;시녀들&gt;은 왕이 아니라 뒤편의 사람들, 공간의 긴장, 시선의 방향을 함께 그려 냅니다. 그림의 중심에 서지 않아도 전체를 살리는 존재가 있다는 뜻입니다. 우리 공동체도 누가 중심이 되느냐보다 누가 누군가의 짐을 함께 지느냐로 성격이 드러납니다.</p>
    <p style="font-size:13.5px;line-height:1.8;margin-top:8px;color:#4f6b4a;">연결: 이번 주 본문은 공동체의 중심을 '내 자유'가 아니라 '형제의 짐을 함께 지는 사랑'으로 옮겨 놓습니다.</p>
  </section>

  <section style="margin-bottom:18px;">
    <h2 style="font-size:18px;color:#32453a;margin-bottom:8px;">말씀 나누기</h2>
    <ol style="padding-left:20px;font-size:13.5px;line-height:1.9;margin:0;">
      <li>최근 누군가의 도움을 받아 마음이 놓였던 순간이 있으셨나요?</li>
      <li>본문에서 "자기를 기쁘게 하지 아니하셨나니"라는 말이 왜 반복되는지 어떻게 느껴지십니까?</li>
      <li>내가 누군가에게 짐이 되어 버린 적, 또는 다른 이의 짐을 지나친 적이 있나요?</li>
      <li>그리스도께서 나를 있는 그대로 받아 주셨다는 사실은 이번 주 관계를 어떻게 바꾸어 줍니까?</li>
      <li>이번 주에 한 사람의 짐을 함께 지기 위해 구체적으로 무엇을 할 수 있을까요?</li>
    </ol>
  </section>

  <section style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px;">
    <div style="background:#f4f6f0;border-left:4px solid #7d9b75;padding:14px;border-radius:6px;">
      <h2 style="font-size:17px;color:#32453a;margin-bottom:8px;">함께 기도</h2>
      <p style="font-size:13px;line-height:1.8;">우리 공동체가 강한 말보다 따뜻한 책임을 선택하게 해 달라고 기도합시다. 서로의 연약함을 품는 마음, 판단보다 환대를 먼저 하는 태도를 위해 함께 기도해주세요.</p>
    </div>
    <div style="background:#f4f2ea;border-left:4px solid #b59b63;padding:14px;border-radius:6px;">
      <h2 style="font-size:17px;color:#32453a;margin-bottom:8px;">이번 주 실천</h2>
      <p style="font-size:13px;line-height:1.8;">이번 주 한 사람에게 먼저 안부를 묻고, 실제 필요한 것을 하나 들어 주기. 말로만 돕지 말고 한 번의 행동으로 짐을 함께 지어 보기.</p>
    </div>
  </section>

  <footer style="border-top:1px solid #d8d2c0;padding-top:10px;font-size:12px;color:#7a7a73;">로마서 15:1-7 · 서로의 짐을 지라</footer>
</main>
""",
        extra_css="ol li { margin-bottom: 8px; }",
    )

    youth_html = html_wrap(
        "청소년 소그룹 나눔지",
        f"""
<main class="page" style="background:#f7fbf5;">
  <section style="border-bottom:2px solid #6aa56b;padding-bottom:12px;margin-bottom:18px;">
    <div style="font-size:12px;color:#5f7c61;letter-spacing:.08em;">DI DIM CHURCH · YOUTH GROUP</div>
    <h1 style="font-size:28px;line-height:1.25;color:#214d2e;margin-top:8px;">내 자유가 남에게는 상처가 될 때</h1>
    <p style="margin-top:8px;font-size:14px;color:#4c6651;">롬 15:1-7 · {month} {week_label}</p>
  </section>

  <section style="margin-bottom:18px;">
    <h2 style="font-size:18px;color:#214d2e;margin-bottom:8px;">이번 주 핵심은 이거야</h2>
    <p style="font-size:13.5px;line-height:1.8;">예수님은 자기 편한 길만 고르지 않으시고 우리를 받아 주셨어요. 그래서 우리도 친구를 볼 때 "내가 옳다"보다 "상대가 지금 어떤 짐을 지고 있지?"를 먼저 생각할 수 있어요. 자유는 남을 무시하는 힘이 아니라, 누군가를 살리는 선택으로 드러나요.</p>
  </section>

  <section style="margin-bottom:18px;">
    <h2 style="font-size:18px;color:#214d2e;margin-bottom:8px;">Talk About It</h2>
    <ol style="padding-left:20px;font-size:13.5px;line-height:1.9;margin:0;">
      <li>학교나 반에서 "나만 생각하는 분위기"를 느낀 적 있어?</li>
      <li>친구가 약해 보일 때, 나도 모르게 무시하거나 피한 적은 없었어?</li>
      <li>예수님이 나를 먼저 받아 주셨다는 사실이 오늘 관계에 어떤 의미가 있을까?</li>
      <li>이번 주에 친구 한 명에게 해 볼 수 있는 작은 배려는 뭐가 있을까?</li>
    </ol>
  </section>

  <section style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px;">
    <div style="background:#fff;border:1px solid #d7e7cf;padding:14px;border-radius:8px;">
      <h2 style="font-size:17px;color:#214d2e;margin-bottom:8px;">이번 주 챌린지</h2>
      <p style="font-size:13px;line-height:1.8;">먼저 말 걸기 1회. 먼저 안부 묻고, 먼저 도와주고, 먼저 손 내밀기.</p>
    </div>
    <div style="background:#eaf6ea;border:1px solid #c9e0c1;padding:14px;border-radius:8px;">
      <h2 style="font-size:17px;color:#214d2e;margin-bottom:8px;">기도</h2>
      <p style="font-size:13px;line-height:1.9;">하나님, 이번 주 제가 <strong>친구의 짐을 같이 들어 주는 사람</strong>이 될 수 있게 도와주세요.<br>제 마음에 <strong>예수님처럼 받아 주는 마음</strong>을 채워주세요.<br>예수님의 이름으로 기도합니다. 아멘.</p>
    </div>
  </section>

  <footer style="border-top:1px solid #d8d2c0;padding-top:10px;font-size:12px;color:#6b7b6d;">롬 15:1-7 · 이번 주, 누군가의 짐을 조금 덜어 주기</footer>
</main>
""",
        extra_css="ol li { margin-bottom: 8px; }",
    )

    SG_OUT.mkdir(parents=True, exist_ok=True)
    write(SG_OUT / "장년-나눔지.html", adult_html)
    write(SG_OUT / "청소년-나눔지.html", youth_html)


def make_cardnews(context: dict[str, str]) -> None:
    CN_OUT.mkdir(parents=True, exist_ok=True)
    slides = [
        {
            "n": 1,
            "title": "내 자유가\n남에게는\n폭력이 될 때",
            "body": "롬 15:1-7\n서로의 짐을 지라",
            "design": "짙은 올리브 배경, 큰 제목, 여백 넓게. 로고 하단 배치.",
        },
        {
            "n": 2,
            "title": "혹시\n내가 맞는지\n증명하느라",
            "body": "옆 사람의 짐을\n못 보고 있진 않나요?",
            "design": "밝은 배경, 공감형 질문. 대각선으로 작은 사람 실루엣.",
        },
        {
            "n": 3,
            "title": "강한 자는\n약한 자를\n담당하라",
            "body": "복음은\n내 편함보다\n형제의 짐을 먼저 봅니다.",
            "design": "본문 인용 중심. 중앙 정렬, 한 줄씩 짧게.",
        },
        {
            "n": 4,
            "title": "그리스도는\n자기를\n기쁘게 하지\n않으셨습니다",
            "body": "그분의 환대가\n우리의 기준이 됩니다.",
            "design": "복음 전환 슬라이드. 빛이 번지는 질감, 절제된 톤.",
        },
        {
            "n": 5,
            "title": "이번 주\n한 사람의 짐을\n함께 들어보세요",
            "body": "안부 한 번,\n도움 한 번,\n배려 한 번.",
            "design": "실천 CTA. 체크리스트 느낌, 초록 포인트.",
        },
        {
            "n": 6,
            "title": "\"그리스도께서\n우리로\n하나 되게 하셨습니다\"",
            "body": "함께 짐을 지는 교회가\n복음의 모습입니다.",
            "design": "인용 슬라이드. 큰 따옴표, 여백 충분히.",
        },
        {
            "n": 7,
            "title": "이번 주일\n함께 예배해요",
            "body": "디딤교회\n롬 15:1-7",
            "design": "마무리/초대. 로고, 예배 초대 문구, 깔끔한 종료.",
        },
    ]

    slides_md = ["# Week 28 카드뉴스", "", "본문: 롬 15:1-7", "콘텐츠용 제목: 내 자유가 남에게는 폭력이 될 때", ""]
    for s in slides:
        slides_md.extend(
            [
                f"## 슬라이드 {s['n']}",
                "**텍스트:**",
                s["title"],
                s["body"],
                "",
                "**디자인 지시:**",
                s["design"],
                "",
            ]
        )
    write(CN_OUT / "slides.md", "\n".join(slides_md).strip() + "\n")

    preview_parts = [
        "<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>Week 28 Card News</title>",
        "<style>body{margin:0;background:#111;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;color:#fff}.slide{width:1080px;height:1080px;margin:24px auto;padding:84px 88px;display:flex;flex-direction:column;justify-content:space-between;border-radius:0;box-sizing:border-box}.num{font-size:20px;letter-spacing:.16em;opacity:.8}.title{font-size:78px;line-height:1.08;font-weight:800;white-space:pre-line}.body{font-size:36px;line-height:1.35;white-space:pre-line;opacity:.95}.dark{background:#294233}.light{background:#f7f1e7;color:#21302b}.cream{background:#f2ede3;color:#253028}.olive{background:#5e6f47}.gold{background:#736245}.footer{font-size:24px;opacity:.88;display:flex;justify-content:space-between;align-items:center}.logo{font-weight:700;letter-spacing:.1em}</style></head><body>",
    ]
    theme_classes = ["dark", "light", "cream", "olive", "gold", "light", "dark"]
    for s, cls in zip(slides, theme_classes):
        preview_parts.append(
            f"<section class='slide {cls}'><div class='num'>SLIDE {s['n']:02d}</div><div class='title'>{s['title']}</div><div class='body'>{s['body']}</div><div class='footer'><div class='logo'>DIDIM CHURCH</div><div>Week 28 · Romans 15:1-7</div></div></section>"
        )
    preview_parts.append("</body></html>")
    write(CN_OUT / "slide-preview.html", "".join(preview_parts))

    caption = (
        "내 자유가 누군가에겐 상처가 될 수 있습니다.\n"
        "롬 15:1-7은 강한 사람이 약한 이를 무시하지 말고 함께 짐을 지라고 말합니다.\n"
        "이번 주, 옆 사람을 살리는 선택을 해보세요.\n"
        "#디딤교회 #주일설교 #말씀카드 #롬15장 #공동체 #환대 #서로의짐"
    )
    message = (
        "내 자유가 남에게는 폭력이 될 때,\n"
        "롬 15:1-7의 답은 분명합니다.\n"
        "이번 주일 함께 예배해요 🙏"
    )
    write(CN_OUT / "caption-instagram.txt", caption.strip() + "\n")
    write(CN_OUT / "message-kakao.txt", message.strip() + "\n")

    for s, cls in zip(slides, theme_classes):
        html = (
            "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>slide-{s['n']}</title><style>body{{margin:0;background:#111;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif}}"
            f".slide{{width:1080px;height:1080px;padding:84px 88px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;color:{'#fff' if cls in {'dark','olive','gold'} else '#21302b'};background:{ {'dark':'#294233','light':'#f7f1e7','cream':'#f2ede3','olive':'#5e6f47','gold':'#736245'}[cls] }}}"
            ".num{font-size:20px;letter-spacing:.16em;opacity:.8}.title{font-size:78px;line-height:1.08;font-weight:800;white-space:pre-line}.body{font-size:36px;line-height:1.35;white-space:pre-line;opacity:.95}.footer{font-size:24px;opacity:.88;display:flex;justify-content:space-between;align-items:center}.logo{font-weight:700;letter-spacing:.1em}</style></head><body>"
            f"<section class='slide'><div class='num'>SLIDE {s['n']:02d}</div><div class='title'>{s['title']}</div><div class='body'>{s['body']}</div><div class='footer'><div class='logo'>DIDIM CHURCH</div><div>Week 28 · Romans 15:1-7</div></div></section></body></html>"
        )
        write(CN_OUT / f"slide-{s['n']}.html", html)


def capture_pngs() -> None:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    for i in range(1, 8):
        html = CN_OUT / f"slide-{i}.html"
        png = CN_OUT / f"slide-{i}.png"
        subprocess.run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--allow-file-access-from-files",
                f"--screenshot={png}",
                "--window-size=1080,1080",
                f"file://{html}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


def main() -> None:
    sermon_text = read(SERMON)
    context = {"title": "서로의 짐을 지라", "scripture": "롬 15:1-7", "raw": sermon_text}
    make_small_group(context)
    make_cardnews(context)
    capture_pngs()


if __name__ == "__main__":
    main()
