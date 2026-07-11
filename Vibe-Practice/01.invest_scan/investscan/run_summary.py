"""
run_summary.py — Pipeline execution result summary.

Prints a 3-line summary after weekly_orchestrator completes:
  - Stock name + week
  - Signal direction
  - YoY growth + pACS quality score

Usage:
    python3 -m investscan.run_summary
    python3 investscan/run_summary.py
"""
import glob
import os
import re
from pathlib import Path


def get_latest_report(reports_dir: str = "output/reports") -> str | None:
    reports = sorted(
        r for r in glob.glob(f"{reports_dir}/weekly-report-*.md")
        if not r.endswith(".ko.md")
    )
    return reports[-1] if reports else None


def get_latest_pacs(pacs_dir: str = "pacs-logs") -> int | None:
    files = sorted(glob.glob(f"{pacs_dir}/*.md"))
    if not files:
        return None
    with open(files[-1]) as f:
        content = f.read()
    m = re.search(r"pACS\s*=\s*(\d+)", content)
    return int(m.group(1)) if m else None


def parse_report(path: str) -> dict:
    with open(path) as f:
        content = f.read()

    stock_m = re.search(r"\*\*(.+?)\s+\((\d{6})\)\*\*", content)
    stock = f"{stock_m.group(1)} ({stock_m.group(2)})" if stock_m else "N/A"

    week_m = re.search(r"Week:\s*([\w-]+)", content)
    week = week_m.group(1) if week_m else "N/A"

    cat_m = re.search(r"Category:\s*([AB])", content)
    category = cat_m.group(1) if cat_m else "N/A"

    dir_m = re.search(r"> \*\*(.+?)\*\*", content)
    direction = dir_m.group(1) if dir_m else "N/A"

    yoy_m = re.search(r"\*\*YoY Growth\*\*[:\s]+([^\n]+)", content)
    yoy = yoy_m.group(1).strip() if yoy_m else "N/A"

    return {
        "stock": stock,
        "week": week,
        "category": category,
        "direction": direction,
        "yoy": yoy,
    }


def pacs_badge(score: int) -> str:
    if score >= 85:
        return f"🟢 {score} GREEN"
    elif score >= 70:
        return f"🟡 {score} YELLOW"
    else:
        return f"🔴 {score} RED"


def print_summary(report_path: str) -> None:
    info = parse_report(report_path)
    pacs = get_latest_pacs()
    date_str = os.path.basename(report_path).replace("weekly-report-", "").replace(".md", "")
    cat_label = "재무 실적 기반" if info["category"] == "A" else "테마 기반"
    pacs_str = pacs_badge(pacs) if pacs is not None else "N/A"

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  파이프라인 완료 — {date_str}  ({info["week"]})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  종목   {info["stock"]}  |  카테고리 {info["category"]} ({cat_label})
  신호   {info["direction"]}
  실적   {info["yoy"]}
  품질   pACS {pacs_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋  리포트: {report_path}
    검토 후 /approve-hitl 3 으로 Telegram 발송 승인
""")


def main() -> int:
    report = get_latest_report()
    if not report:
        print("⚠️  리포트 없음 — 파이프라인을 먼저 실행하세요.")
        return 1
    print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
