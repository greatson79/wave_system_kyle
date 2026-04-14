"""
export_report.py — Multi-format report exporter: Markdown → TXT + PDF.

Korean font: Apple SD 산돌고딕 Neo (extracted from system .ttc via fontTools)
PDF layout : structured sections, Korean tables, balanced pages

Saves to:
  ~/Desktop/Ai_works/output/투자분석제안/{DATE}_주간투자분석.txt
  ~/Desktop/Ai_works/output/투자분석제안/{DATE}_주간투자분석.pdf

Usage:
    python3 -m investscan.export_report                         # latest report
    python3 -m investscan.export_report --date 2026-03-30
    python3 -m investscan.export_report --path /path/to/file.md
    python3 -m investscan.export_report --formats txt,pdf
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
from pathlib import Path

from investscan import export_dashboard as _dashboard

# ── constants ─────────────────────────────────────────────────────────────────

OUTPUT_DIR  = Path.home() / "Desktop" / "Ai_works" / "output" / "투자분석제안"
REPORTS_DIR = Path("output/reports")

_FONT_CACHE = Path.home() / ".cache" / "investscan" / "fonts"

# NanumGothic TTC candidates (macOS system asset paths — Naver open-source Korean font)
_NANUM_CANDIDATES: list[Path] = [
    Path("/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs"
         "/com_apple_MobileAsset_Font7"
         "/ffdc761fe47bbaccf326d21ef8ea29d0b576d632.asset/AssetData/NanumGothic.ttc"),
    Path("/System/Library/AssetsV2/com_apple_MobileAsset_Font8"
         "/7a0b5c0f3c1d41c4c52a33343496c9c65ad52c50.asset/AssetData/NanumGothic.ttc"),
]
_NANUM_IDX = {"": 0, "B": 1}   # 0=Regular, 1=Bold

# Fallback: AppleSDGothicNeo
_APPLE_TTC  = Path("/System/Library/Fonts/AppleSDGothicNeo.ttc")
_APPLE_IDX  = {"": 0, "B": 6}

# ── Typography & colors ───────────────────────────────────────────────────────

FS = {"h1": 16, "h2": 13, "h3": 10.5, "h4": 9.5,
      "body": 9.5, "small": 8, "table": 8.5, "code": 8.5}

LH = {"h1": 7.5, "h2": 6, "h3": 5, "h4": 4.5,
      "body": 4.5, "table": 4.2, "code": 4.0}

C = {
    "h1":          (26,  54, 108),
    "h2":          (36,  78, 160),
    "h3":          (60, 100, 175),
    "body":        (30,  30,  30),
    "gray":        (100, 100, 100),
    "light_gray":  (160, 160, 160),
    "hr":          (205, 210, 220),
    "quote_bar":   (90,  140, 210),
    "quote_bg":    (242, 246, 255),
    "quote_text":  (40,  60, 130),
    "code_bg":     (246, 246, 246),
    "code_border": (215, 215, 215),
    "code_text":   (50,  50,  50),
    "th_bg":       (26,  54, 108),
    "th_fg":       (255, 255, 255),
    "td_alt":      (244, 248, 255),
    "td_bg":       (255, 255, 255),
    "td_border":   (200, 210, 228),
}

PDF_MARGIN     = 15   # mm
PDF_MARGIN_TOP = 22   # mm (space for header line)


# ── font helpers ──────────────────────────────────────────────────────────────

def _ensure_fonts() -> dict[str, Path]:
    """
    Extract NanumGothic TTF variants from system .ttc and cache locally.
    Falls back to AppleSDGothicNeo if NanumGothic is not found.
    """
    _FONT_CACHE.mkdir(parents=True, exist_ok=True)
    from fontTools.ttLib import TTCollection

    # Try NanumGothic first (cleaner Korean rendering in PDF)
    ttc_path: Path | None = None
    idx_map = _NANUM_IDX
    prefix = "NanumGothic"
    for candidate in _NANUM_CANDIDATES:
        if candidate.exists():
            ttc_path = candidate
            break

    # Fallback to AppleSDGothicNeo
    if ttc_path is None:
        if _APPLE_TTC.exists():
            ttc_path = _APPLE_TTC
            idx_map = _APPLE_IDX
            prefix = "AppleSDGothicNeo"

    if ttc_path is None:
        raise FileNotFoundError("한국어 폰트를 찾을 수 없습니다. NanumGothic 또는 AppleSDGothicNeo가 필요합니다.")

    paths: dict[str, Path] = {}
    for style, idx in idx_map.items():
        label = "regular" if style == "" else "bold"
        out = _FONT_CACHE / f"{prefix}_{label}.ttf"
        if not out.exists():
            ttc = TTCollection(str(ttc_path))
            ttc[idx].save(str(out))
        paths[style] = out
    return paths


# ── markdown parser ───────────────────────────────────────────────────────────

def _strip_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",        r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    # Remove emoji / special Unicode symbols (keep basic CJK + Hangul)
    # NOTE: no r-prefix so \uXXXX escapes are interpreted as Unicode code points
    text = re.sub("[\U00010000-\U0010ffff]", "", text)          # supplementary planes (emoji etc.)
    text = re.sub("[\u2600-\u27BF\ufe00-\ufe0f]", "", text)     # misc symbols + variation selectors
    text = re.sub("[\u2300-\u23FF\u2B00-\u2BFF]", "", text)     # misc technical + arrows
    return text.strip()


def _parse_table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        if re.match(r"^\|[-\s|:]+\|$", line.strip()):
            continue
        cells = line.split("|")
        cells = [_strip_inline(c.strip()) for c in cells]
        cells = cells[1:-1] if len(cells) > 2 else cells
        if any(c for c in cells):
            rows.append(cells)
    return rows


def parse_md(md: str) -> list[dict]:
    elements: list[dict] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # H1-H4
        for lvl in range(4, 0, -1):
            prefix = "#" * lvl + " "
            if line.startswith(prefix):
                elements.append({"type": f"h{lvl}", "text": _strip_inline(line[len(prefix):])})
                i += 1
                break
        else:
            # Code block
            if stripped.startswith("```"):
                code: list[str] = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code.append(lines[i])
                    i += 1
                i += 1
                elements.append({"type": "code", "text": "\n".join(code)})
                continue

            # Table
            if stripped.startswith("|"):
                tbl: list[str] = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    tbl.append(lines[i])
                    i += 1
                rows = _parse_table_rows(tbl)
                if rows:
                    elements.append({"type": "table", "rows": rows})
                continue

            # HR
            if re.match(r"^-{3,}$", stripped) or re.match(r"^\*{3,}$", stripped):
                elements.append({"type": "hr"})
                i += 1
                continue

            # Blockquote
            if stripped.startswith(">"):
                qlines: list[str] = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    raw = lines[i].strip().lstrip(">").strip()
                    qlines.append(_strip_inline(raw))
                    i += 1
                elements.append({"type": "quote", "text": " ".join(qlines)})
                continue

            # Ordered / unordered bullet
            m = re.match(r"^(\s*)([-*•]|\d+\.)\s+(.+)$", line)
            if m:
                level = len(m.group(1)) // 2
                marker = m.group(2)
                text = _strip_inline(m.group(3))
                is_num = bool(re.match(r"\d+\.", marker))
                elements.append({"type": "bullet", "text": text,
                                  "level": level, "marker": marker, "numbered": is_num})
                i += 1
                continue

            # Blank
            if not stripped:
                elements.append({"type": "blank"})
                i += 1
                continue

            # Paragraph
            elements.append({"type": "para", "text": _strip_inline(stripped)})
            i += 1

    return elements


# ── PDF renderer ──────────────────────────────────────────────────────────────

def _make_pdf(report_date: str):
    from fpdf import FPDF

    class InvestPDF(FPDF):
        def header(self):
            self.set_font("KR", "B", 8)
            self.set_text_color(*C["gray"])
            self.cell(0, 5, f"InvestScan 주간 투자 분석  |  {report_date}", align="R")
            self.ln(2)
            self.set_draw_color(*C["hr"])
            self.set_line_width(0.2)
            self.line(PDF_MARGIN, self.get_y(), self.w - PDF_MARGIN, self.get_y())
            self.ln(4)
            self.set_text_color(*C["body"])

        def footer(self):
            self.set_y(-15)
            self.set_font("KR", "", 8)
            self.set_text_color(*C["light_gray"])
            self.cell(0, 5, f"— {self.page_no()} —", align="C")
            self.ln(4)
            self.set_font("KR", "", 7.5)
            self.cell(0, 4, "본 리포트는 AI 자동 생성 참고 자료이며 투자 권유가 아닙니다.", align="C")

    pdf = InvestPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(PDF_MARGIN, PDF_MARGIN_TOP, PDF_MARGIN)
    pdf.set_auto_page_break(auto=True, margin=28)
    return pdf


def _render_h1(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 50:
        pdf.add_page()
    pdf.ln(2)
    pdf.set_font("KR", "B", FS["h1"])
    pdf.set_text_color(*C["h1"])
    pdf.multi_cell(pdf.epw, LH["h1"], text)
    y = pdf.get_y()
    pdf.set_draw_color(*C["h2"])
    pdf.set_line_width(0.7)
    pdf.line(PDF_MARGIN, y + 1, pdf.w - PDF_MARGIN, y + 1)
    pdf.ln(3)
    pdf.set_text_color(*C["body"])


def _render_h2(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 65:
        pdf.add_page()
    pdf.ln(3)
    y = pdf.get_y()
    # Left accent bar
    pdf.set_fill_color(*C["h2"])
    pdf.rect(PDF_MARGIN - 1, y, 3, 7, "F")
    pdf.set_x(PDF_MARGIN + 3)
    pdf.set_font("KR", "B", FS["h2"])
    pdf.set_text_color(*C["h2"])
    pdf.multi_cell(pdf.epw - 4, LH["h2"], text)
    pdf.ln(1.5)
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*C["body"])


def _render_h3(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 70:
        pdf.add_page()
    pdf.ln(2)
    pdf.set_font("KR", "B", FS["h3"])
    pdf.set_text_color(*C["h3"])
    pdf.multi_cell(pdf.epw, LH["h3"], text)
    pdf.ln(0.5)
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*C["body"])


def _render_h4(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 50:
        pdf.add_page()
    pdf.ln(1)
    pdf.set_font("KR", "B", FS["h4"])
    pdf.set_text_color(*C["h3"])
    pdf.multi_cell(pdf.epw, 4.5, text)
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*C["body"])


def _render_para(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 28:
        pdf.add_page()
    pdf.set_font("KR", "", FS["body"])
    pdf.set_text_color(*C["body"])
    pdf.multi_cell(pdf.epw, LH["body"], text)
    pdf.set_x(pdf.l_margin)


def _render_bullet(pdf, el: dict) -> None:
    indent = 3 + el.get("level", 0) * 5
    marker = "•" if not el["numbered"] else el["marker"]
    pdf.set_font("KR", "", FS["body"])
    pdf.set_text_color(*C["body"])
    if pdf.get_y() > pdf.h - 26:
        pdf.add_page()
    x0 = PDF_MARGIN + indent
    # marker
    pdf.set_x(x0)
    pdf.cell(5, LH["body"], marker)
    # text — use full remaining width from current x; reset to l_margin after
    pdf.set_x(x0 + 5)
    pdf.multi_cell(pdf.epw - indent - 5, LH["body"], el["text"])
    pdf.set_x(pdf.l_margin)


def _render_quote(pdf, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    if pdf.get_y() > pdf.h - 50:
        pdf.add_page()
    pdf.ln(0.5)
    y = pdf.get_y()
    pdf.set_fill_color(*C["quote_bar"])
    pdf.rect(PDF_MARGIN, y, 2.5, 7, "F")
    pdf.set_fill_color(*C["quote_bg"])
    pdf.set_x(PDF_MARGIN + 4)
    pdf.set_font("KR", "", FS["body"])
    pdf.set_text_color(*C["quote_text"])
    pdf.multi_cell(pdf.epw - 5, LH["body"], text, fill=True)
    pdf.ln(0.5)
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*C["body"])


def _render_code(pdf, text: str) -> None:
    pdf.ln(1.5)
    lines = text.strip().split("\n")
    row_h = LH["code"]
    box_h = len(lines) * row_h + 4
    y0 = pdf.get_y()

    if y0 + box_h > pdf.h - 26:
        pdf.add_page()
        y0 = pdf.get_y()

    pdf.set_fill_color(*C["code_bg"])
    pdf.set_draw_color(*C["code_border"])
    pdf.set_line_width(0.2)
    pdf.rect(PDF_MARGIN, y0, pdf.epw, min(box_h, 80), "FD")

    pdf.set_font("KR", "", FS["code"])
    pdf.set_text_color(*C["code_text"])
    for line in lines:
        pdf.set_x(PDF_MARGIN + 3)
        pdf.multi_cell(pdf.epw - 6, row_h, line if line.strip() else " ")
    pdf.ln(1.5)
    pdf.set_text_color(*C["body"])


def _render_table(pdf, rows: list[list[str]]) -> None:
    if not rows:
        return
    pdf.ln(1.5)

    header = rows[0]
    data   = rows[1:]
    ncols  = len(header)
    if ncols == 0:
        return

    epw = pdf.epw
    cw  = epw / ncols          # equal column width
    lh  = LH["table"]
    pad = 1.5                  # cell padding mm
    font_sz = FS["table"]

    def _cell_lines(text: str) -> int:
        """Estimate line count for a cell given column width.
        Uses math.ceil with a 20% safety factor for Korean text."""
        pdf.set_font("KR", "", font_sz)
        sw = pdf.get_string_width(text or " ") * 1.2  # 20% safety for CJK metrics
        available = cw - 2 * pad
        lines = math.ceil(sw / max(available, 1))
        return max(1, lines + 1)  # +1 safety margin

    def _row_height(cells: list[str]) -> float:
        max_lines = max((_cell_lines(c) for c in cells), default=1)
        return max_lines * lh + 2 * pad

    def _draw_row(cells: list[str], is_header: bool, alt: bool = False) -> None:
        rh = _row_height(cells)
        y0 = pdf.get_y()

        # Page overflow — ensure entire row fits before starting
        if y0 + rh > pdf.h - 26:
            pdf.add_page()
            y0 = pdf.get_y()

        x0 = pdf.l_margin
        pdf.set_draw_color(*C["td_border"])
        pdf.set_line_width(0.15)

        max_y_after = y0 + rh  # Track actual bottom; start with estimated

        for j, cell in enumerate(cells[:ncols]):
            xj = x0 + j * cw
            if is_header:
                pdf.set_fill_color(*C["th_bg"])
            else:
                pdf.set_fill_color(*(C["td_alt"] if alt else C["td_bg"]))
            pdf.rect(xj, y0, cw, rh, "FD")

            pdf.set_xy(xj + pad, y0 + pad)
            if is_header:
                pdf.set_font("KR", "B", font_sz)
                pdf.set_text_color(*C["th_fg"])
            else:
                pdf.set_font("KR", "", font_sz)
                pdf.set_text_color(*C["body"])
            pdf.multi_cell(cw - 2 * pad, lh, cell or "")
            # Track maximum y reached after each cell
            max_y_after = max(max_y_after, pdf.get_y())

        # Use actual bottom (not just estimated) so next content doesn't overlap overflow
        pdf.set_xy(x0, max_y_after)

    _draw_row(header, is_header=True)
    for i, row in enumerate(data):
        cells = (row + [""] * ncols)[:ncols]
        _draw_row(cells, is_header=False, alt=(i % 2 == 0))

    pdf.ln(1.5)


def _render_hr(pdf) -> None:
    pdf.ln(1.5)
    pdf.set_draw_color(*C["hr"])
    pdf.set_line_width(0.3)
    pdf.line(PDF_MARGIN, pdf.get_y(), pdf.w - PDF_MARGIN, pdf.get_y())
    pdf.ln(2)


def _render_elements(pdf, elements: list[dict]) -> None:
    blank_streak = 0
    for el in elements:
        t = el["type"]
        if t == "blank":
            blank_streak += 1
            if blank_streak == 1:
                pdf.ln(1.5)
            continue
        blank_streak = 0

        if   t == "h1":     _render_h1(pdf, el["text"])
        elif t == "h2":     _render_h2(pdf, el["text"])
        elif t == "h3":     _render_h3(pdf, el["text"])
        elif t == "h4":     _render_h4(pdf, el["text"])
        elif t == "para":   _render_para(pdf, el["text"])
        elif t == "bullet": _render_bullet(pdf, el)
        elif t == "quote":  _render_quote(pdf, el["text"])
        elif t == "code":   _render_code(pdf, el["text"])
        elif t == "table":  _render_table(pdf, el["rows"])
        elif t == "hr":     _render_hr(pdf)


def embed_chart(pdf, chart_path: Path, caption: str = "") -> None:
    """Embed a chart PNG into the current PDF page."""
    if not chart_path.exists():
        return
    # Available width
    avail_w = pdf.epw
    img_h = avail_w * 0.55      # maintain ~16:9-ish aspect ratio
    y0 = pdf.get_y()
    if y0 + img_h + 10 > pdf.h - 25:
        pdf.add_page()
        y0 = pdf.get_y()

    pdf.image(str(chart_path), x=PDF_MARGIN, y=y0, w=avail_w)
    pdf.set_y(y0 + img_h + 2)
    if caption:
        pdf.set_font("KR", "", 8)
        pdf.set_text_color(*C["gray"])
        pdf.cell(0, 5, caption, align="C")
        pdf.ln(3)
    pdf.set_text_color(*C["body"])


# ── text exporter ─────────────────────────────────────────────────────────────

def md_to_plain_text(md: str) -> str:
    text = md
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#{1,4}\s+(.+)$",
                  lambda m: "\n" + m.group(1).upper() + "\n" + "─" * len(m.group(1)),
                  text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",        r"\1", text)
    text = re.sub(r"^>\s+(.+)$",    r"  ▶ \1", text, flags=re.MULTILINE)
    text = re.sub(r"^\|[-\s|:]+\|$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\|", "  ", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_txt(content: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def write_pdf(md_content: str, out_path: Path, report_date: str) -> None:
    """Render markdown as a Korean-friendly, balanced-layout PDF."""
    font_paths = _ensure_fonts()

    pdf = _make_pdf(report_date)
    pdf.add_font("KR", "",  str(font_paths[""]))
    pdf.add_font("KR", "B", str(font_paths["B"]))
    pdf.add_page()

    elements = parse_md(md_content)
    _render_elements(pdf, elements)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))


# ── export orchestrator ───────────────────────────────────────────────────────

def _build_dca_section(stock_data: dict, report_date: str = "") -> str:
    """
    Generate a DCA (분할매수) buy price table from dynamically fetched stock data.
    Applies generic Korean market DCA parameters — no hardcoded per-ticker config.
    """
    # Generic DCA parameters applied uniformly to all dynamically selected stocks
    _DIFFS  = [-0.015, -0.035, -0.055]  # 1차 -1.5%, 2차 -3.5%, 3차 -5.5%
    _TARGET = +0.10                      # +10% target from current price
    _STOP   = -0.07                      # -7% stop loss from current price

    def _rnd(n: float) -> str:
        """Round to nearest 1,000 for large prices, 500 for mid, 100 for small."""
        if n >= 500_000:
            unit = 1_000
        elif n >= 100_000:
            unit = 500
        else:
            unit = 100
        return f"{round(n / unit) * unit:,.0f}원"

    header = "| 종목 | 현재가 | 1차 (30%) | 2차 (40%) | 3차 (30%) | 목표가 | 손절가 |"
    sep    = "|------|--------|-----------|-----------|-----------|--------|--------|"
    rows   = [header, sep]

    for ticker, info in stock_data.items():
        name    = info.get("name", ticker)
        cur_raw = str(info.get("current_price", "")).replace(",", "").strip()
        try:
            price = float(cur_raw)
        except ValueError:
            price = 0.0

        cur_str = (info.get("current_price", "N/A") + "원") if info.get("current_price") else "N/A"

        if price <= 0:
            rows.append(f"| {name} ({ticker}) | {cur_str} | — | — | — | — | — |")
        else:
            b1  = _rnd(price * (1 + _DIFFS[0]))
            b2  = _rnd(price * (1 + _DIFFS[1]))
            b3  = _rnd(price * (1 + _DIFFS[2]))
            tgt = _rnd(price * (1 + _TARGET))
            stp = _rnd(price * (1 + _STOP))
            rows.append(f"| {name} ({ticker}) | {cur_str} | {b1} | {b2} | {b3} | {tgt} | {stp} |")

    return "\n".join([
        "## 분할매수 진입 가격대 제안",
        "",
        "> **분할매수 원칙**: 투자금을 3회 분할 진입 (1차 30% / 2차 40% / 3차 30%)."
        " 손절선 이탈 시 전량 정리."
        " 목표가·손절가는 현재가 기준 일반 파라미터 적용 (+10% / -7%)."
        " 종목별 세부 분석 및 투자의견은 본문 에이전트 토론 섹션 참조.",
        "",
        *rows,
        "",
    ])


def _enrich_markdown(
    md_content: str,
    report_date: str,
    dry_run: bool = False,
) -> tuple[str, dict[str, Path]]:
    """
    Inject real-time stock data + DCA buy levels into report markdown.
    Charts removed — replaced by structured DCA price table.
    Returns (enriched_markdown, {}).
    """
    extra_sections: list[str] = []

    # 1. Naver Finance real-time prices — tickers loaded from agent context (dynamic)
    stock_data: dict = {}
    try:
        from investscan.naver_finance import fetch_stocks, format_stock_table, _mock_data

        # Load dynamic watchlist from agent context file
        dyn_tickers: dict[str, str] | None = None
        try:
            import json as _json
            ctx_path = Path(f"output/temp/agent_context_{report_date}.json")
            if ctx_path.exists():
                ctx = _json.loads(ctx_path.read_text(encoding="utf-8"))
                wl = ctx.get("watchlist", {})
                if isinstance(wl, dict) and wl:
                    dyn_tickers = wl
                    print(f"  📋 동적 watchlist 로드: {list(dyn_tickers.values())}")
        except Exception:
            pass  # fallback to naver_finance.DEFAULT_TICKERS

        print("  📊 네이버 증권 실시간 데이터 수집 중...")
        stock_data = _mock_data() if dry_run else fetch_stocks(tickers=dyn_tickers)
        if stock_data:
            extra_sections.append(format_stock_table(stock_data))
            print(f"     └ {len(stock_data)}개 종목 수집 완료")
    except Exception as e:
        print(f"  ⚠  네이버 증권 수집 실패: {e}")

    # 2. DCA buy price recommendation table (replaces charts)
    if stock_data:
        dca_section = _build_dca_section(stock_data, report_date=report_date)
        if dca_section:
            extra_sections.append(dca_section)
            print("  ✅ 분할매수 진입 가격대 생성 완료")

    # 3. Inject enriched sections AFTER the stock analysis section (before agent debate section)
    #    Markers tried in order: "## Ⅶ", "## VII", "## 에이전트", "## 7."
    #    Fallback: append at end (before disclaimer) or at very end.
    if extra_sections:
        injection = "\n\n".join(extra_sections)
        _markers = ["\n## Ⅶ", "\n## VII", "\n## 에이전트 토론", "\n## 7.", "\n## Ⅹ", "\n## X.", "\n## 면책"]
        injected = False
        for marker in _markers:
            if marker in md_content:
                idx = md_content.index(marker)
                md_content = md_content[:idx] + "\n\n" + injection + md_content[idx:]
                injected = True
                break
        if not injected:
            md_content = md_content + "\n\n" + injection

    return md_content, {}


def export(
    md_path: Path,
    report_date: str,
    formats: list[str],
    out_dir: Path = OUTPUT_DIR,
    enrich: bool = False,
    dry_run: bool = False,
    no_live: bool = False,
) -> dict[str, Path]:
    md_path = md_path.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(md_path, encoding="utf-8") as f:
        md_content = f.read()

    # Optionally inject live data + DCA section
    if enrich:
        md_content, _ = _enrich_markdown(md_content, report_date, dry_run)

    stem    = f"{report_date}_주간투자분석"
    results: dict[str, Path] = {}

    if "txt" in formats:
        txt_path = out_dir / f"{stem}.txt"
        write_txt(md_to_plain_text(md_content), txt_path)
        results["txt"] = txt_path
        print(f"  ✅ TXT  → {txt_path}")

    if "pdf" in formats:
        pdf_path = out_dir / f"{stem}.pdf"
        write_pdf(md_content, pdf_path, report_date)
        results["pdf"] = pdf_path
        print(f"  ✅ PDF  → {pdf_path}")

    # MD copy
    md_dest = out_dir / f"{stem}.md"
    if md_path.resolve() != md_dest.resolve():
        shutil.copy2(md_path, md_dest)
    results["md"] = md_dest
    print(f"  ✅ MD   → {md_dest}")

    if "html" in formats:
        try:
            html_path = _dashboard.generate(
                report_date,
                out_dir=out_dir,
                live=not (dry_run or no_live),
            )
            results["html"] = html_path
            print(f"  ✅ HTML → {html_path}")
        except FileNotFoundError as e:
            print(f"  ⚠️  HTML 생략 — {e}")
        except Exception as e:
            print(f"  ⚠️  HTML 생성 실패 — {e}")

    return results


# ── CLI entry point ───────────────────────────────────────────────────────────

def get_latest_report(reports_dir: Path = REPORTS_DIR) -> Path | None:
    files = sorted(p for p in reports_dir.glob("weekly-report-*.md")
                   if not p.name.endswith(".ko.md"))
    return files[-1] if files else None


def get_report_by_date(report_date: str, reports_dir: Path = REPORTS_DIR) -> Path | None:
    p = reports_dir / f"weekly-report-{report_date}.md"
    return p if p.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan 리포트 내보내기")
    parser.add_argument("--date",    help="리포트 날짜 YYYY-MM-DD")
    parser.add_argument("--path",    help=".md 파일 경로 직접 지정")
    parser.add_argument("--formats", default="txt,pdf",
                        help="형식 선택: txt,pdf,md,html (기본: txt,pdf)")
    parser.add_argument("--no-live", action="store_true",
                        help="실시간 주가 조회 생략 (HTML 대시보드 오프라인 테스트용)")
    parser.add_argument("--out-dir", default=str(OUTPUT_DIR),
                        help="출력 디렉터리")
    parser.add_argument("--enrich",  action="store_true",
                        help="실시간 주가 + 분할매수 진입 가격대 자동 삽입")
    parser.add_argument("--dry-run", action="store_true",
                        help="네트워크 없이 mock 데이터로 enrich 테스트")
    args = parser.parse_args()

    formats = [f.strip().lower() for f in args.formats.split(",")]
    out_dir = Path(args.out_dir)

    # Resolve source
    if args.path:
        md_path = Path(args.path)
        if not md_path.exists():
            print(f"⚠️  파일 없음: {args.path}")
            return 1
        m = re.search(r"(\d{4}-\d{2}-\d{2})", md_path.stem)
        report_date = m.group(1) if m else md_path.stem
    elif args.date:
        md_path = get_report_by_date(args.date)
        if not md_path:
            print(f"⚠️  {args.date} 리포트 없음")
            return 1
        report_date = args.date
    else:
        md_path = get_latest_report()
        if not md_path:
            print("⚠️  리포트 없음 — 파이프라인을 먼저 실행하세요.")
            return 1
        m = re.search(r"(\d{4}-\d{2}-\d{2})", md_path.stem)
        report_date = m.group(1) if m else md_path.stem.replace("weekly-report-", "")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
리포트 내보내기 — {report_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  원본: {md_path}
  출력: {out_dir}
  형식: {', '.join(f.upper() for f in formats)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    results = export(md_path, report_date, formats, out_dir,
                     enrich=args.enrich, dry_run=args.dry_run,
                     no_live=args.no_live)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
내보내기 완료 — {len(results)}개 파일 저장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
