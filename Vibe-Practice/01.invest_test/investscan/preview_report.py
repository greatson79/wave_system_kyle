"""
preview_report.py — Inline report preview for CLI.

Extracts Executive Summary + Financial Snapshot + Signal Direction
from the latest weekly report and prints a formatted inline preview.

Usage:
    python3 -m investscan.preview_report
    python3 -m investscan.preview_report --path output/reports/weekly-report-2026-03-29.md
"""
import argparse
import glob
import os
import re
import textwrap
from pathlib import Path


def get_latest_report(reports_dir: str = "output/reports") -> str | None:
    reports = sorted(
        r for r in glob.glob(f"{reports_dir}/weekly-report-*.md")
        if not r.endswith(".ko.md")
    )
    return reports[-1] if reports else None


def parse_report(path: str) -> dict:
    with open(path) as f:
        content = f.read()

    # Header
    stock_m = re.search(r"\*\*(.+?)\s+\((\d{6})\)\*\*", content)
    stock_name = stock_m.group(1) if stock_m else "N/A"
    stock_code = stock_m.group(2) if stock_m else "N/A"

    week_m = re.search(r"Week:\s*([\w-]+)", content)
    week = week_m.group(1) if week_m else "N/A"

    cat_m = re.search(r"Category:\s*([AB])", content)
    category = cat_m.group(1) if cat_m else "N/A"

    # Executive Summary (between header and first ---)
    exec_m = re.search(
        r"## Executive Summary\s*\n\n(.+?)\n\n---",
        content,
        re.DOTALL,
    )
    exec_summary = exec_m.group(1).strip() if exec_m else "N/A"

    # Signal Direction
    dir_m = re.search(r"> \*\*(.+?)\*\*", content)
    direction = dir_m.group(1) if dir_m else "N/A"

    # Financial Snapshot bullets
    fin_m = re.search(
        r"## Financial Snapshot\s*\n\n(.+?)\n\n##",
        content,
        re.DOTALL,
    )
    financials = fin_m.group(1).strip() if fin_m else ""

    # Macro table (just the 4 rows)
    macro_m = re.search(
        r"\| Fed Rate Direction \| (.+?) \|\s*\n"
        r"\| Inflation Trend \| (.+?) \|\s*\n"
        r"\| Risk Appetite \| (.+?) \|\s*\n"
        r"\| USD Strength \| (.+?) \|",
        content,
    )
    macro = {}
    if macro_m:
        macro = {
            "Fed": macro_m.group(1).strip(),
            "Inflation": macro_m.group(2).strip(),
            "Risk": macro_m.group(3).strip(),
            "USD": macro_m.group(4).strip(),
        }

    return {
        "stock_name": stock_name,
        "stock_code": stock_code,
        "week": week,
        "category": category,
        "exec_summary": exec_summary,
        "direction": direction,
        "financials": financials,
        "macro": macro,
    }


def _indent(text: str, prefix: str = "  ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def print_preview(report_path: str) -> None:
    info = parse_report(report_path)
    date_str = os.path.basename(report_path).replace("weekly-report-", "").replace(".md", "")
    cat_label = "재무 실적 기반 (Category A)" if info["category"] == "A" else "테마 기반 (Category B)"

    # Wrap executive summary at 70 chars
    wrapped_exec = textwrap.fill(info["exec_summary"], width=70)
    indented_exec = _indent(wrapped_exec)

    # Financials — indent each bullet
    fin_lines = [ln for ln in info["financials"].splitlines() if ln.strip()]
    indented_fin = "\n".join("  " + ln for ln in fin_lines)

    # Macro one-liner
    macro = info["macro"]
    if macro:
        macro_str = (
            f"  Fed: {macro['Fed']}  |  인플레이션: {macro['Inflation']}  "
            f"|  위험선호: {macro['Risk']}  |  USD: {macro['USD']}"
        )
    else:
        macro_str = "  (macro data unavailable)"

    # Direction badge
    dir_lower = info["direction"].lower()
    if "positive" in dir_lower or "bullish" in dir_lower or "maintained" in dir_lower:
        dir_badge = f"📈 {info['direction']}"
    elif "negative" in dir_lower or "bearish" in dir_lower or "risk" in dir_lower:
        dir_badge = f"📉 {info['direction']}"
    else:
        dir_badge = f"➡️  {info['direction']}"

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊  리포트 미리보기 — {date_str}  ({info["week"]})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {info["stock_name"]} ({info["stock_code"]})  |  {cat_label}

  신호 방향: {dir_badge}

  ── Executive Summary ──────────────────────────────
{indented_exec}

  ── Financial Snapshot ─────────────────────────────
{indented_fin}

  ── Macro Environment ──────────────────────────────
{macro_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  전체 리포트: {report_path}
""")


def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan report inline preview")
    parser.add_argument("--path", help="Report path (default: latest)")
    args = parser.parse_args()

    report = args.path or get_latest_report()
    if not report:
        print("⚠️  리포트 없음 — 파이프라인을 먼저 실행하세요.")
        return 1
    if not Path(report).exists():
        print(f"⚠️  파일 없음: {report}")
        return 1

    print_preview(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
