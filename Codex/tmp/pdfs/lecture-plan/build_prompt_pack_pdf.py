#!/usr/bin/env python3
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path("/Users/kylechoi/Desktop/Ai_works/Codex")
MD_PATH = ROOT / "output/lecture-plan/Codex_자료정리자동화_수강생_상세프롬프트팩_2026-07-06.md"
PDF_PATH = ROOT / "output/lecture-plan/Codex_자료정리자동화_수강생_상세프롬프트팩_2026-07-06.pdf"


def register_fonts():
    font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    pdfmetrics.registerFont(TTFont("Korean", font_path))
    pdfmetrics.registerFont(TTFont("Korean-Bold", font_path))
    pdfmetrics.registerFontFamily("Korean", normal="Korean", bold="Korean-Bold")


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleKo", parent=base["Title"], fontName="Korean-Bold", fontSize=21, leading=29, alignment=TA_LEFT, textColor=colors.HexColor("#1F2430"), spaceAfter=14),
        "h1": ParagraphStyle("H1Ko", parent=base["Heading1"], fontName="Korean-Bold", fontSize=15, leading=21, textColor=colors.HexColor("#2E4780"), spaceBefore=14, spaceAfter=7),
        "h2": ParagraphStyle("H2Ko", parent=base["Heading2"], fontName="Korean-Bold", fontSize=12.5, leading=18, textColor=colors.HexColor("#1F2430"), spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("BodyKo", parent=base["BodyText"], fontName="Korean", fontSize=9.5, leading=14.6, textColor=colors.HexColor("#1F2430"), spaceAfter=5),
        "small": ParagraphStyle("SmallKo", parent=base["BodyText"], fontName="Korean", fontSize=8.2, leading=11.5, textColor=colors.HexColor("#464C55")),
        "bullet": ParagraphStyle("BulletKo", parent=base["BodyText"], fontName="Korean", fontSize=9.4, leading=14.3, leftIndent=12, firstLineIndent=-8, spaceAfter=3),
        "code": ParagraphStyle("CodeKo", parent=base["Code"], fontName="Korean", fontSize=8.1, leading=11.4, textColor=colors.HexColor("#1F2430")),
    }


def clean_inline(text):
    text = text.strip()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font name='Korean'>\1</font>", text)
    return text


def is_separator_row(line):
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return all(cell and set(cell) <= {"-", ":", " "} for cell in cells)


def parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        if not is_separator_row(lines[i]):
            rows.append([cell.strip() for cell in lines[i].strip().strip("|").split("|")])
        i += 1
    return rows, i


def table_flow(rows, styles, width):
    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    col_widths = [width / max_cols] * max_cols
    data = [[Paragraph(clean_inline(cell), styles["small"]) for cell in row] for row in normalized]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF1FE")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DBE7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def code_flow(text, styles, width):
    block = Preformatted(text.strip("\n"), styles["code"], maxLineLength=88)
    table = Table([[block]], colWidths=[width])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F5F7")),
        ("BOX", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DBE7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def markdown_to_flowables(markdown, styles, width):
    flow = []
    lines = markdown.splitlines()
    i = 0
    in_code = False
    code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                flow.append(code_flow("\n".join(code_lines), styles, width))
                flow.append(Spacer(1, 7))
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            flow.append(Spacer(1, 3))
            i += 1
            continue

        if stripped.startswith("|"):
            rows, next_i = parse_table(lines, i)
            if rows:
                flow.append(table_flow(rows, styles, width))
                flow.append(Spacer(1, 7))
            i = next_i
            continue

        if stripped.startswith("# "):
            flow.append(Paragraph(clean_inline(stripped[2:]), styles["title"]))
        elif stripped.startswith("## "):
            flow.append(Paragraph(clean_inline(stripped[3:]), styles["h1"]))
        elif stripped.startswith("### "):
            flow.append(Paragraph(clean_inline(stripped[4:]), styles["h2"]))
        elif stripped.startswith("- "):
            flow.append(Paragraph("• " + clean_inline(stripped[2:]), styles["bullet"]))
        elif re.match(r"^\d+\.\s+", stripped):
            flow.append(Paragraph(clean_inline(stripped), styles["bullet"]))
        else:
            flow.append(Paragraph(clean_inline(stripped), styles["body"]))
        i += 1
    return flow


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Korean", 8)
    canvas.setFillColor(colors.HexColor("#6F768A"))
    canvas.drawString(18 * mm, 12 * mm, "Codex 자료정리 자동화 수강생 프롬프트 팩")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, str(doc.page))
    canvas.restoreState()


def main():
    register_fonts()
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="Codex 자료정리 자동화 수강생 상세 프롬프트 팩",
        author="WAVE AI Networks",
    )
    width = A4[0] - doc.leftMargin - doc.rightMargin
    flow = markdown_to_flowables(MD_PATH.read_text(encoding="utf-8"), styles, width)
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
