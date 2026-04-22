#!/usr/bin/env python3
"""insight-report MD → HTML → PDF (fpdf2, 한국어 지원)"""

import re
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

BASE = Path(__file__).parent
MD_FILE = BASE / "insight-report-2026-04-08.md"
PDF_FILE = BASE / "insight-report-2026-04-08.pdf"

# ── 폰트 경로 (macOS 시스템 폰트) ──────────────────────────────────────
FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleGothic.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
]
font_path = next((p for p in FONT_PATHS if Path(p).exists()), None)
if not font_path:
    raise FileNotFoundError("한국어 폰트를 찾을 수 없습니다.")

# ── FPDF 서브클래스 ──────────────────────────────────────────────────
class InsightPDF(FPDF):
    def header(self):
        pass  # 커스텀 헤더 없음

    def footer(self):
        self.set_y(-15)
        self.set_font("korean", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "WAVE AI Networks", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(-12)
        self.cell(0, 6, str(self.page_no()), align="R")
        self.set_text_color(0, 0, 0)

def strip_inline(text):
    """마크다운 인라인 포맷 제거 (볼드, 이탤릭, 코드, 링크)"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()

def is_banner_line(line):
    return line.strip().startswith('━')

def parse_md(path):
    """마크다운을 구조화된 블록으로 파싱"""
    blocks = []
    lines = path.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        if is_banner_line(raw):
            blocks.append(('hr', ''))
            i += 1
            continue

        if raw.startswith('### '):
            blocks.append(('h3', strip_inline(raw[4:])))
        elif raw.startswith('## '):
            blocks.append(('h2', strip_inline(raw[3:])))
        elif raw.startswith('# '):
            blocks.append(('h1', strip_inline(raw[2:])))
        elif raw.startswith('---'):
            blocks.append(('hr', ''))
        elif raw.startswith('| '):
            # 테이블 수집
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            blocks.append(('table', table_lines))
            continue
        elif raw.startswith('- ') or raw.startswith('* '):
            blocks.append(('bullet', strip_inline(raw[2:])))
        elif raw == '':
            blocks.append(('blank', ''))
        else:
            blocks.append(('p', strip_inline(raw)))

        i += 1
    return blocks

def render_pdf(blocks, out_path, font_path):
    pdf = InsightPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(25, 25, 25)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # 폰트 등록
    pdf.add_font("korean", style="", fname=font_path)
    pdf.add_font("korean", style="B", fname=font_path)

    banner_area = True  # 첫 배너 영역 감지용

    for btype, content in blocks:
        if btype == 'h1':
            pdf.ln(4)
            pdf.set_font("korean", style="B", size=14)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 7, content, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)

        elif btype == 'h2':
            pdf.ln(5)
            pdf.set_font("korean", style="B", size=12)
            pdf.set_draw_color(50, 50, 50)
            pdf.multi_cell(0, 6, content, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(80, 80, 80)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 160, pdf.get_y())
            pdf.ln(2)

        elif btype == 'h3':
            pdf.ln(3)
            pdf.set_font("korean", size=10.5)
            pdf.multi_cell(0, 6, content, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)

        elif btype == 'p':
            if not content:
                continue
            # 배너 중앙 텍스트 감지
            if 'Wave AI 통찰 보고서' in content:
                pdf.ln(2)
                pdf.set_font("korean", style="B", size=16)
                pdf.cell(0, 10, "Wave AI 통찰 보고서", align="C",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
            else:
                pdf.set_font("korean", size=10)
                pdf.multi_cell(0, 5.5, content, align="L",
                               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)

        elif btype == 'bullet':
            pdf.set_font("korean", size=10)
            pdf.set_x(30)
            pdf.multi_cell(155, 5.5, f"• {content}", align="L",
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        elif btype == 'table':
            rows = content
            if len(rows) < 2:
                continue
            # 헤더행 파싱
            def parse_row(r):
                cells = [c.strip() for c in r.strip('|').split('|')]
                return [strip_inline(c) for c in cells if not re.match(r'^[-:]+$', c.strip())]

            headers = parse_row(rows[0])
            if not headers:
                continue
            data_rows = [parse_row(r) for r in rows[2:] if r.strip() and not re.match(r'^\|[-|: ]+\|$', r.strip())]

            ncols = len(headers)
            col_w = 160 / ncols

            pdf.ln(2)
            pdf.set_font("korean", style="B", size=8.5)
            pdf.set_draw_color(80, 80, 80)
            y_before = pdf.get_y()
            pdf.line(25, y_before, 185, y_before)
            pdf.ln(1)
            for h in headers:
                pdf.cell(col_w, 5, h[:25], align="L")
            pdf.ln(5)
            y_after_header = pdf.get_y()
            pdf.line(25, y_after_header, 185, y_after_header)

            pdf.set_font("korean", size=8.5)
            for row in data_rows:
                # 행 높이 계산 (긴 텍스트 대비)
                max_lines = max(
                    len(pdf.multi_cell(col_w, 4.5, (row[ci] if ci < len(row) else '')[:80],
                                       dry_run=True, output='LINES'))
                    for ci in range(ncols)
                ) if data_rows else 1
                row_h = max(4.5, max_lines * 4.5)

                for ci, h in enumerate(headers):
                    cell_text = (row[ci] if ci < len(row) else '')[:80]
                    pdf.multi_cell(col_w, 4.5, cell_text, align="L",
                                   new_x=XPos.RIGHT if ci < ncols-1 else XPos.LMARGIN,
                                   new_y=YPos.TOP if ci < ncols-1 else YPos.NEXT)

                y_row = pdf.get_y()
                pdf.set_draw_color(200, 200, 200)
                pdf.line(25, y_row, 185, y_row)

            pdf.set_draw_color(80, 80, 80)
            pdf.line(25, pdf.get_y(), 185, pdf.get_y())
            pdf.ln(3)

        elif btype == 'hr':
            pdf.ln(2)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(25, pdf.get_y(), 185, pdf.get_y())
            pdf.ln(3)

        elif btype == 'blank':
            pdf.ln(1)

    pdf.output(str(out_path))
    print(f"[OK] PDF 생성: {out_path} ({out_path.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    blocks = parse_md(MD_FILE)
    render_pdf(blocks, PDF_FILE, font_path)
