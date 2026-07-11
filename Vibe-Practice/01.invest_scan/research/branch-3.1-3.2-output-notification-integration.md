# Branch 3.1 & 3.2: Output & Notification Integration Analysis

> **Two Output & Notification Integration Experts**
> **Date**: 2026-03-28
> **Context**: InvestScan generates weekly Korean investment direction reports. How should these be delivered beyond writing a `.md` file?
> **Dependency**: Builds on `branch-3-output-implementation.md` (report generation + decision journal already designed)

---

## Branch 3.1: RICH Delivery (Multiple Channels)

### Expert 1 (Multi-Channel Delivery Architect)

**Design Philosophy**: A weekly report that nobody reads is worse than no report at all. The delivery channel must match the user's actual habit -- where do they look on Monday morning? The answer for a solo user is usually: phone notification first (to know it exists), then a comfortable reading surface (browser, PDF, or editor).

---

### A. Email Delivery (Python `smtplib` + Gmail App Password)

#### Setup Prerequisites

1. **Gmail 2-Step Verification**: Must be enabled on the Google account
2. **App Password Generation**: Google Account > Security > 2-Step Verification > App passwords > Select "Other (Custom name)" > Name it "InvestScan" > Copy the 16-character password
3. **Store securely**: Save in `.env` file (gitignored), never hardcode

#### Gmail SMTP Settings

| Parameter | Value |
|-----------|-------|
| SMTP Server | `smtp.gmail.com` |
| Port (SSL) | `465` |
| Port (TLS) | `587` |
| Authentication | Gmail address + 16-char App Password |
| Encryption | SSL (port 465) recommended for simplicity |

#### Implementation: `notify_email.py` (~50 LOC)

```python
"""InvestScan Email Notification -- Send weekly report via Gmail SMTP.

Prerequisites:
    pip install python-dotenv
    .env file with GMAIL_ADDRESS and GMAIL_APP_PASSWORD
"""

from __future__ import annotations

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import date
import os

from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def send_report_email(
    report_path: Path,
    recipient: str | None = None,
    subject: str | None = None,
    attach_pdf: Path | None = None,
) -> bool:
    """Send the weekly report as an HTML email with optional PDF attachment.

    Args:
        report_path: Path to the generated .md report file.
        recipient: Email address (defaults to self = GMAIL_ADDRESS).
        subject: Email subject (auto-generated if None).
        attach_pdf: Optional PDF file to attach.

    Returns:
        True if sent successfully.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[ERROR] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
        return False

    recipient = recipient or GMAIL_ADDRESS  # Send to self by default
    subject = subject or f"[InvestScan] 주간 투자 방향 리포트 -- {date.today().isoformat()}"

    # Read report content
    report_text = report_path.read_text(encoding="utf-8")

    # Build email
    msg = MIMEMultipart("mixed")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject

    # Body: plain text (Markdown renders well enough in most clients)
    body = MIMEText(report_text, "plain", "utf-8")
    msg.attach(body)

    # Optional PDF attachment
    if attach_pdf and attach_pdf.exists():
        with open(attach_pdf, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={attach_pdf.name}",
        )
        msg.attach(part)

    # Send via Gmail SMTP (SSL)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[OK] Report emailed to {recipient}")
        return True
    except smtplib.SMTPException as e:
        print(f"[ERROR] Email failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python notify_email.py <report.md> [report.pdf]")
        sys.exit(1)
    report = Path(sys.argv[1])
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    send_report_email(report, attach_pdf=pdf)
```

**LOC**: ~55 (excluding comments/docstrings)

#### Can it attach PDF/HTML?

Yes. The implementation above supports PDF attachment via `MIMEBase`. For HTML email body, replace `MIMEText(report_text, "plain")` with `MIMEText(html_content, "html")` after converting Markdown to HTML via `markdown` library.

#### Reliability Assessment

- **Pros**: Zero cost, no API key expiration, works indefinitely once set up, no rate limits for personal use
- **Cons**: Gmail may occasionally flag as spam (solved by adding to contacts), App Password is a static credential (security risk if `.env` leaks)
- **Maintenance**: Near-zero. App passwords do not expire unless manually revoked or 2FA is disabled

---

### B. KakaoTalk Notification (나에게 보내기 API)

#### API Overview

Kakao provides a "나에게 보내기" (Send to Self) REST API that sends template messages to the user's own KakaoTalk chat. There is also a Python wrapper library: **PyKakao** (`pip install PyKakao`).

#### Free? Authentication? Rate Limits?

| Aspect | Detail |
|--------|--------|
| **Cost** | Free (personal use, no commercial messaging fees) |
| **App Registration** | Required at [Kakao Developers](https://developers.kakao.com) -- create an app, get REST API key |
| **OAuth Flow** | Required. User must authorize via browser redirect (one-time, then refresh token) |
| **Access Token Lifetime** | 12-24 hours (varies by policy) |
| **Refresh Token Lifetime** | ~30 days. Auto-renewed if used within last 7 days before expiry |
| **Rate Limit** | Undocumented for personal use, but practically unlimited for weekly sends |
| **Message Length** | Text template: max 200 characters; Feed/List templates: richer but more complex |

#### Critical Pain Point: Token Refresh

This is the **biggest maintenance burden** of all channels. The OAuth token flow requires:

1. **Initial setup**: Open browser, log in to Kakao, authorize app, extract code from redirect URL
2. **Every ~30 days**: If the refresh token expires (because you did not call the API for 30+ days), you must repeat the browser authorization manually
3. **Automation difficulty**: For a weekly pipeline, the refresh token stays alive (used every 7 days), but any pipeline interruption > 30 days requires manual re-authorization

#### Implementation: `notify_kakao.py` (~65 LOC)

```python
"""InvestScan KakaoTalk Notification -- Send summary to self via 나에게 보내기 API.

Prerequisites:
    pip install PyKakao python-dotenv
    .env file with KAKAO_REST_API_KEY
    First-run: browser-based OAuth authorization required
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_TOKEN_FILE = Path(__file__).parent / ".kakao_token.json"


def _get_message_api():
    """Initialize PyKakao Message API with stored or new token."""
    from PyKakao import Message

    api = Message(service_key=KAKAO_REST_API_KEY)

    if KAKAO_TOKEN_FILE.exists():
        token_data = json.loads(KAKAO_TOKEN_FILE.read_text())
        api.set_access_token(token_data["access_token"])
        return api

    # First run: need browser authorization
    auth_url = api.get_url_for_generating_code()
    print(f"[KAKAO] Authorize at:\n{auth_url}")
    redirected_url = input("Paste the redirected URL here: ")
    access_token = api.get_access_token_by_redirected_url(redirected_url)
    api.set_access_token(access_token)

    # Persist token
    KAKAO_TOKEN_FILE.write_text(json.dumps({
        "access_token": access_token,
    }))
    print("[OK] Kakao token saved.")
    return api


def send_kakao_summary(
    report_path: Path,
    max_chars: int = 200,
) -> bool:
    """Send a truncated summary of the weekly report to KakaoTalk.

    Args:
        report_path: Path to the generated .md report file.
        max_chars: Maximum characters for KakaoTalk text message (API limit: 200).

    Returns:
        True if sent successfully.
    """
    if not KAKAO_REST_API_KEY:
        print("[ERROR] KAKAO_REST_API_KEY not set in .env")
        return False

    # Extract executive summary from report (Section 1)
    report_text = report_path.read_text(encoding="utf-8")
    summary = _extract_executive_summary(report_text, max_chars)

    try:
        api = _get_message_api()
        result = api.send_message_to_me(
            message_type="text",
            text=summary,
            link={
                "web_url": "https://github.com",  # Placeholder; could link to local dashboard
                "mobile_web_url": "https://github.com",
            },
            button_title="리포트 보기",
        )
        print(f"[OK] KakaoTalk message sent: {result}")
        return True
    except Exception as e:
        print(f"[ERROR] KakaoTalk send failed: {e}")
        return False


def _extract_executive_summary(report_md: str, max_chars: int) -> str:
    """Extract the executive summary section and truncate to max_chars."""
    lines = report_md.split("\n")
    in_summary = False
    summary_lines = []

    for line in lines:
        if "핵심 요약" in line or "Executive Summary" in line:
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## ") or line.startswith("---"):
                break
            if line.strip():
                summary_lines.append(line.strip())

    summary = " ".join(summary_lines)
    today = date.today().isoformat()
    prefix = f"[InvestScan {today}]\n"

    available = max_chars - len(prefix)
    if len(summary) > available:
        summary = summary[:available - 3] + "..."

    return prefix + summary


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python notify_kakao.py <report.md>")
        sys.exit(1)
    send_kakao_summary(Path(sys.argv[1]))
```

**LOC**: ~65

#### Verdict on KakaoTalk

**High setup cost, moderate maintenance, fragile token lifecycle.** The 200-character limit means the message is essentially a ping ("new report ready") rather than a delivery mechanism. The OAuth token refresh is the weakest link -- if the pipeline stops running for > 30 days, manual intervention is required. For a solo user running a weekly pipeline, this works, but it is the most maintenance-heavy option.

---

### C. Telegram Bot (Most Reliable Notification)

#### Setup Steps

1. **Create bot**: Message `@BotFather` on Telegram, send `/newbot`, follow prompts, receive bot token
2. **Get your chat ID**: Message `@userinfobot` or send any message to your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` and extract the `chat.id` field
3. **Store in `.env`**: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

#### Why Telegram is the Most Reliable

| Factor | Telegram | KakaoTalk | Email |
|--------|----------|-----------|-------|
| Token expiration | **Never** (bot token is permanent) | 30 days (refresh) | N/A (app password permanent) |
| Setup complexity | 2 minutes | 15-30 minutes (OAuth flow) | 5 minutes |
| Message length | 4096 chars (plenty for summary) | 200 chars | Unlimited |
| Markdown support | Native (MarkdownV2) | None | Limited |
| Rate limit | 30 msg/sec | Undocumented | ~500/day (Gmail) |
| Requires browser | No | Yes (initial + token refresh) | No |
| Mobile push | Instant | Instant | Depends on email app |

#### Implementation: `notify_telegram.py` (~35 LOC)

```python
"""InvestScan Telegram Notification -- Send report summary via personal bot.

Prerequisites:
    pip install requests python-dotenv
    .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

Setup:
    1. Message @BotFather on Telegram -> /newbot -> save token
    2. Message @userinfobot -> save your chat_id
    3. Send any message to your new bot (activates the chat)
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_telegram_report(
    report_path: Path,
    max_chars: int = 4000,
) -> bool:
    """Send the weekly report summary to Telegram.

    Telegram supports up to 4096 characters per message with Markdown formatting.
    This sends the executive summary + sector directions -- enough for actionable info.

    Args:
        report_path: Path to the generated .md report file.
        max_chars: Maximum message length (Telegram limit: 4096).

    Returns:
        True if sent successfully.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("[ERROR] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
        return False

    report_text = report_path.read_text(encoding="utf-8")
    message = _build_telegram_message(report_text, max_chars)

    resp = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        },
        timeout=10,
    )

    if resp.status_code == 200:
        print(f"[OK] Telegram message sent (chat_id={CHAT_ID})")
        return True
    else:
        print(f"[ERROR] Telegram API returned {resp.status_code}: {resp.text}")
        return False


def _build_telegram_message(report_md: str, max_chars: int) -> str:
    """Build a Telegram-friendly summary from the full report.

    Extracts: date, dominant direction, sector summary table, top 3 signals.
    Fits within Telegram's 4096-char limit comfortably.
    """
    lines = report_md.split("\n")
    today = date.today().isoformat()

    # Extract key sections
    header = f"*[InvestScan] 주간 투자 방향 리포트*\n_{today}_\n"
    sections = []
    current_section = []
    current_title = ""

    for line in lines:
        if line.startswith("## "):
            if current_section and current_title:
                sections.append((current_title, "\n".join(current_section)))
            current_title = line.strip("# ").strip()
            current_section = []
        elif current_title:
            current_section.append(line)

    if current_section and current_title:
        sections.append((current_title, "\n".join(current_section)))

    # Build message: header + first 2 sections (summary + sectors)
    body_parts = [header]
    for title, content in sections[:2]:
        truncated = content[:1500] if len(content) > 1500 else content
        body_parts.append(f"\n*{title}*\n{truncated}")

    message = "\n".join(body_parts)
    if len(message) > max_chars:
        message = message[:max_chars - 20] + "\n\n_... (truncated)_"

    return message


def send_telegram_file(report_path: Path) -> bool:
    """Send the full report as a document attachment."""
    if not BOT_TOKEN or not CHAT_ID:
        return False

    with open(report_path, "rb") as f:
        resp = requests.post(
            f"{API_URL}/sendDocument",
            data={"chat_id": CHAT_ID, "caption": f"InvestScan Report {date.today()}"},
            files={"document": f},
            timeout=30,
        )
    return resp.status_code == 200


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python notify_telegram.py <report.md>")
        sys.exit(1)
    path = Path(sys.argv[1])
    send_telegram_report(path)
    send_telegram_file(path)  # Also send full file as attachment
```

**LOC**: ~85 (including the bonus `send_telegram_file` function)

#### Why Telegram Wins for Reliability

1. **Bot tokens never expire.** Once created, the token works forever unless manually revoked via BotFather.
2. **No OAuth dance.** No browser redirect, no refresh tokens, no re-authorization.
3. **4096-character messages** allow sending the entire executive summary + sector table -- genuinely useful content on mobile.
4. **File attachment API** means you can also send the full `.md` or `.pdf` as a document.
5. **Markdown support** means the message renders with bold, italic, and formatting on Telegram.
6. **Zero maintenance.** If the pipeline runs, the message sends. Period.

---

### D. Streamlit Local Dashboard

#### Reuse Pattern from GlobalNews-Crawling

The existing `GlobalNews-Crawling-AgenticWorkflow/dashboard.py` is a **1,089-line Streamlit app** that reads date-partitioned Parquet/JSONL/SQLite outputs and provides:
- Date discovery via directory scanning
- Multi-period aggregation (Daily/Monthly/Quarterly/Yearly)
- 6 tabs: Overview, Topics, Sentiment, Time Series, Word Cloud, Article Explorer
- `@st.cache_data(ttl=600)` for performance

**InvestScan can directly reuse this pattern**: scan `output/` for date-partitioned directories, load JSON synthesis data and rendered reports, display in Streamlit tabs.

#### InvestScan Dashboard Design: `dashboard.py`

```python
"""InvestScan -- Investment Direction Dashboard.

Launch: streamlit run dashboard.py

Reads weekly report data from output/{date}/ directories.
Provides: Report Viewer, Signal Explorer, Sector Heatmap, Decision Journal.
"""

import json
import re
from pathlib import Path
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px

# ── Config ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "output"

st.set_page_config(
    page_title="InvestScan Dashboard",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)

# ── Date Discovery (reuse GlobalNews pattern) ──────────────────────
@st.cache_data(ttl=300)
def discover_dates() -> list[str]:
    if not OUTPUT_DIR.exists():
        return []
    return sorted(
        [p.name for p in OUTPUT_DIR.iterdir()
         if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)],
        reverse=True,
    )

# ── Sidebar ─────────────────────────────────────────────────────────
st.sidebar.title("InvestScan")
dates = discover_dates()
if not dates:
    st.warning("No report data found in output/ directory.")
    st.stop()

selected_date = st.sidebar.selectbox("Report Date", dates, index=0)
data_dir = OUTPUT_DIR / selected_date

# ── Load Data ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_synthesis(date_str: str) -> dict | None:
    path = OUTPUT_DIR / date_str / "investment_synthesis.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

@st.cache_data(ttl=300)
def load_report_md(date_str: str) -> str | None:
    for name in ["weekly-report.md", f"invest-report-{date_str}.md"]:
        path = OUTPUT_DIR / date_str / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None

synthesis = load_synthesis(selected_date)
report_md = load_report_md(selected_date)

# ── Tabs ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Weekly Report", "Signal Explorer", "Sector Heatmap", "History"
])

with tab1:
    st.header(f"주간 투자 방향 리포트 -- {selected_date}")
    if report_md:
        st.markdown(report_md)
    else:
        st.info("Report not yet generated for this date.")

with tab2:
    st.header("Signal Explorer")
    if synthesis and "signals" in synthesis:
        df = pd.DataFrame(synthesis["signals"])
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            direction_filter = st.multiselect(
                "Direction", df["direction"].unique().tolist(),
                default=df["direction"].unique().tolist(),
            )
        with col2:
            min_confidence = st.slider("Min Confidence", 0.0, 1.0, 0.3)
        filtered = df[
            (df["direction"].isin(direction_filter)) &
            (df["confidence"] >= min_confidence)
        ]
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No synthesis data available.")

with tab3:
    st.header("Sector Direction Heatmap")
    if synthesis and "signals" in synthesis:
        df = pd.DataFrame(synthesis["signals"])
        if "sectors" in df.columns:
            # Explode sectors list
            sector_df = df.explode("sectors")
            sector_summary = (
                sector_df.groupby("sectors")
                .agg(
                    count=("confidence", "count"),
                    avg_confidence=("confidence", "mean"),
                )
                .reset_index()
                .sort_values("avg_confidence", ascending=False)
            )
            fig = px.bar(
                sector_summary, x="sectors", y="avg_confidence",
                color="count", title="Sector Confidence Overview",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sector data available.")

with tab4:
    st.header("Report History")
    for d in dates[:12]:  # Last 12 weeks
        with st.expander(f"Week of {d}"):
            md = load_report_md(d)
            if md:
                # Show just the executive summary
                lines = md.split("\n")
                summary = []
                in_summary = False
                for line in lines:
                    if "핵심 요약" in line:
                        in_summary = True
                        continue
                    if in_summary and (line.startswith("## ") or line.startswith("---")):
                        break
                    if in_summary:
                        summary.append(line)
                st.markdown("\n".join(summary) if summary else "No summary found.")
            else:
                st.caption("No report for this date.")
```

**LOC estimate**: ~120 for basic version (above). Full version with auto-refresh, journal tab, and trend charts: ~300-400 LOC.

#### Auto-Refresh

Use `streamlit-autorefresh` component:
```python
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=60_000, limit=None)  # Refresh every 60 seconds
```

This is useful during pipeline execution to see results appear in real time.

#### Reuse Assessment

The GlobalNews dashboard (1,089 LOC) provides a battle-tested pattern for:
- Date-partitioned directory scanning
- Cached data loading with TTL
- Multi-tab layout with filters
- Plotly chart integration

InvestScan's dashboard is structurally simpler (weekly JSON + Markdown vs. Parquet + SQLite), so ~300 LOC covers a fully functional version.

---

### E. PDF Export (Markdown to PDF)

#### Two Approaches

| Approach | Dependency | Korean Support | Quality | Complexity |
|----------|-----------|---------------|---------|-----------|
| **WeasyPrint** | `pip install weasyprint markdown` + system libs | Excellent with `@font-face` | Print-quality | Medium |
| **Pandoc** | System install `pandoc` + `pip install pypandoc` | Excellent with `--pdf-engine=xelatex` | Publication-quality | Low (CLI wrapper) |

WeasyPrint is pure Python (no LaTeX), so it integrates better into a Python pipeline.

#### Korean Font Handling

NanumGothic must be installed on the system:

```bash
# macOS
brew install font-nanum-gothic
# or download from Google Fonts and install manually

# Ubuntu/Debian
sudo apt-get install fonts-nanum

# Verify installation
fc-list | grep Nanum
```

#### Implementation: `export_pdf.py` (~60 LOC)

```python
"""InvestScan PDF Export -- Markdown to PDF with Korean font support.

Prerequisites:
    pip install weasyprint markdown
    System font: NanumGothic (see setup instructions)
"""

from __future__ import annotations

from pathlib import Path
from datetime import date

import markdown
from weasyprint import HTML

# ── CSS for Korean PDF rendering ────────────────────────────────────
PDF_CSS = """
@page {
    size: A4;
    margin: 2cm;
    @bottom-center {
        content: "InvestScan Weekly Report -- " counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #888;
    }
}

body {
    font-family: 'NanumGothic', 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 18pt;
    color: #1a1a2e;
    border-bottom: 2px solid #16213e;
    padding-bottom: 8px;
}

h2 {
    font-size: 14pt;
    color: #16213e;
    margin-top: 24px;
}

h3 {
    font-size: 12pt;
    color: #0f3460;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #ddd;
    padding: 6px 10px;
    text-align: left;
}

th {
    background-color: #f0f0f0;
    font-weight: bold;
}

blockquote {
    border-left: 4px solid #e94560;
    padding-left: 12px;
    color: #555;
    margin: 12px 0;
}

code {
    background: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 10pt;
}

pre {
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 9pt;
}
"""


def export_report_pdf(
    report_md_path: Path,
    output_pdf_path: Path | None = None,
    css: str = PDF_CSS,
) -> Path:
    """Convert a Markdown report to PDF with Korean font support.

    Args:
        report_md_path: Path to the .md report file.
        output_pdf_path: Output PDF path. Defaults to same directory as .md.
        css: CSS styling string.

    Returns:
        Path to the generated PDF file.
    """
    if output_pdf_path is None:
        output_pdf_path = report_md_path.with_suffix(".pdf")

    # Convert Markdown -> HTML
    md_text = report_md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc"],
    )

    # Wrap in full HTML document with CSS
    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Render PDF via WeasyPrint
    HTML(string=full_html).write_pdf(str(output_pdf_path))
    print(f"[OK] PDF exported: {output_pdf_path}")
    return output_pdf_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python export_pdf.py <report.md> [output.pdf]")
        sys.exit(1)
    md_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    export_report_pdf(md_path, pdf_path)
```

**LOC**: ~60 (code) + ~50 (CSS) = ~110 total

#### WeasyPrint Caveats

1. **System dependencies**: WeasyPrint requires `cairo`, `pango`, `gdk-pixbuf` system libraries. On macOS: `brew install weasyprint`. On Ubuntu: `apt-get install libpango-1.0-0 libpangocairo-1.0-0`.
2. **First run is slow**: WeasyPrint's first PDF generation takes 2-5 seconds (font discovery). Subsequent runs: ~0.5s.
3. **Mermaid diagrams**: Not supported natively. If the report contains Mermaid, pre-render to SVG and embed as `<img>`.

---

## Branch 3.2: MINIMAL Delivery (File System Only)

### Expert 2 (Minimalist Delivery Advocate)

**Design Philosophy**: For a personal tool used by one person, the simplest delivery that gets read is the best delivery. Every additional channel is a maintenance liability that compounds over time. Start minimal, add channels only when you catch yourself not reading the reports.

---

### 3.2.1 What Minimal Looks Like

The pipeline already does the hard work: it generates `output/{date}/weekly-report.md`. The "delivery" is:

```python
# At the end of the pipeline's main() function:

import subprocess
import sys
from pathlib import Path

def deliver_minimal(report_path: Path) -> None:
    """Minimal delivery: print summary to terminal + open in default viewer."""

    # 1. Terminal summary (what you see when the pipeline finishes)
    report_text = report_path.read_text(encoding="utf-8")
    lines = report_text.split("\n")

    print("\n" + "=" * 60)
    print("  InvestScan -- Pipeline Complete")
    print("=" * 60)

    # Print first ~20 lines (executive summary)
    for line in lines[:25]:
        print(f"  {line}")

    print(f"\n  Full report: {report_path}")
    print("=" * 60 + "\n")

    # 2. Open in default application
    if sys.platform == "darwin":
        subprocess.run(["open", str(report_path)], check=False)
    elif sys.platform == "linux":
        subprocess.run(["xdg-open", str(report_path)], check=False)
    # Windows: os.startfile(str(report_path))
```

**LOC**: ~20

### 3.2.2 Is This SUFFICIENT for a Personal Tool?

**Yes, with one caveat.**

**Arguments for sufficiency:**

1. **You are the only user.** There is no "notification delivery" problem when the consumer is the same person who runs the pipeline. You know the report exists because you triggered the run.
2. **Markdown renders beautifully** in VS Code, Obsidian, Typora, and even GitHub. No formatting conversion needed.
3. **File system IS the notification** if you build the habit of checking `output/` every Monday. This is no different from checking email -- it is a learned behavior.
4. **Zero maintenance.** No tokens expire. No APIs change. No rate limits. No `.env` files to manage. No `pip install` for notification libraries.
5. **Grep-able archive.** `grep -r "약세" output/` across all historical reports is something no notification channel provides.

**The caveat -- when minimal fails:**

Minimal delivery fails when the pipeline runs **automatically** (e.g., via `cron` or `launchd`) and you forget to check. If InvestScan is manual ("I run it Monday morning"), minimal is perfect. If InvestScan is automated ("cron runs it Sunday night"), you need exactly ONE push notification to say "your report is ready."

### 3.2.3 Recommended Minimal+ Approach

```
output/
  2026-03-27/
    investment_synthesis.json     ← raw data
    invest-report-2026-03-27.md   ← human-readable report
    invest-report-2026-03-27.pdf  ← optional PDF (if email/archival needed)
```

Pipeline finishes with:
1. Terminal summary printed (always)
2. `open report.md` to launch default viewer (always)
3. One-line Telegram ping (only if automated via cron)

---

## COMPARISON: All Channels Side by Side

| Channel | LOC | Setup Time | Maintenance | Reliability | Message Quality | Dependencies |
|---------|-----|-----------|-------------|-------------|-----------------|-------------|
| **File system** (minimal) | ~20 | 0 min | None | Perfect | Full report | None |
| **Email** (Gmail SMTP) | ~55 | 10 min | Near-zero | Excellent | Full report + PDF | `python-dotenv` |
| **Telegram Bot** | ~85 | 5 min | **Zero** | **Excellent** | 4096-char summary + file | `requests` |
| **KakaoTalk** (나에게 보내기) | ~65 | 30 min | **High** (token refresh) | Fragile | 200 chars only | `PyKakao` |
| **PDF Export** | ~110 | 15 min | Low | Excellent | Print-quality | `weasyprint`, `markdown`, system libs |
| **Streamlit Dashboard** | ~300 | 45 min | Low | Good (local) | Interactive, rich | `streamlit`, `plotly`, `pandas` |

### What Actually Gets READ vs "Nice to Have"

For a solo user running a weekly pipeline:

| Channel | Gets Read? | Why / Why Not |
|---------|-----------|---------------|
| **File system + terminal** | **Always** | You just ran the pipeline. You are staring at the terminal. |
| **Telegram ping** | **Always** (if automated) | Phone vibrates. You tap. You read the summary. 10 seconds. |
| **Email** | Sometimes | Buried in inbox. Unless you set a filter/label, it drowns in noise. |
| **KakaoTalk** | Sometimes | Same as email -- chat noise buries it. Plus 200-char limit means no useful content. |
| **PDF** | Rarely | PDFs are for archival or sharing with others. You will not open a PDF to read what you already have in Markdown. |
| **Streamlit** | Occasionally | Great for exploration ("show me all bearish signals in IT sector"), but you will not launch `streamlit run` every Monday morning. |

### Final Recommendation: Which ONE Additional Channel?

## **Telegram Bot -- the single best addition beyond file output.**

**Rationale:**

1. **5-minute setup, zero ongoing maintenance.** Bot token never expires. No OAuth, no refresh tokens, no browser authorization.
2. **4096-character messages** are enough to deliver the executive summary + sector direction table -- genuinely actionable content you can read on your phone in 60 seconds.
3. **File attachment API** means you can also push the full `.md` or `.pdf` as a Telegram document for later reading.
4. **Works for both manual and automated pipelines.** Whether you run InvestScan yourself or cron does it, the Telegram ping arrives on your phone.
5. **Minimal dependency**: just `requests` (which is likely already installed).
6. **Graceful degradation**: If Telegram is down (rare), the pipeline still succeeds -- the report is on disk. Notification failure is non-fatal.

**Implementation priority order:**

```
Phase 1 (Day 1):  File system output + terminal summary         [already designed]
Phase 2 (Day 1):  Telegram bot notification                     [+5 min setup, +85 LOC]
Phase 3 (Week 2): PDF export (for archival/sharing)             [+15 min setup, +110 LOC]
Phase 4 (Month 2): Streamlit dashboard (when you want to explore signals) [+45 min, +300 LOC]
Phase 5 (Never?):  Email/KakaoTalk (only if you specifically want inbox/chat delivery)
```

**What NOT to build:** Do not build KakaoTalk integration unless you have a specific reason to receive notifications there. The 200-character limit, OAuth token refresh burden, and fragile authorization flow make it the worst ROI of all channels. If you want a Korean messaging platform notification, Telegram does it better in every dimension.

---

## Sources

- [PyKakao GitHub -- 카카오 API 파이썬 라이브러리](https://github.com/WooilJeong/PyKakao)
- [PyKakao 카카오톡 메시지 보내기 Guide](https://wooiljeong.github.io/python/pykakao-message/)
- [Kakao Developers -- REST API 카카오톡 메시지](https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api)
- [Kakao Developers -- 카카오 로그인 REST API (토큰 갱신)](https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api)
- [Kakao DevTalk -- Refresh Token 유효 기간](https://devtalk.kakao.com/t/refresh-token/128850)
- [Python Send Email Gmail Tutorial (Mailtrap, 2026)](https://mailtrap.io/blog/python-send-email-gmail/)
- [Gmail SMTP with App Password (Latenode Community)](https://community.latenode.com/t/setting-up-gmail-smtp-with-app-password-for-server-side-python-scripts/12824)
- [Send Email via Gmail and SMTP (Python Assets)](https://pythonassets.com/posts/send-email-via-gmail-and-smtp/)
- [python-telegram-bot Official Site](https://python-telegram-bot.org/)
- [pyTelegramBotAPI GitHub](https://github.com/eternnoir/pyTelegramBotAPI)
- [Send Message to Telegram User Using Python (GeeksforGeeks)](https://www.geeksforgeeks.org/python/send-message-to-telegram-user-using-python/)
- [telegram-send PyPI](https://pypi.org/project/telegram-send/)
- [streamlit-autorefresh GitHub](https://github.com/kmcgrady/streamlit-autorefresh)
- [WeasyPrint -- md2pdf GitHub](https://github.com/tanyatree/md2pdf)
- [WeasyPrint Python PDF Generation (DEV Community)](https://dev.to/bowmanjd/python-pdf-generation-from-html-with-weasyprint-538h)
- [Pandoc CSS WeasyPrint Template](https://github.com/craigbass76/pandoc-css-weasyprint-template)
