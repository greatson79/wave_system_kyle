"""
approve_hitl.py — HITL-3 simplified approval helper.

Shows a 3-line report summary then prompts for Y/N Telegram dispatch approval.
On approval, updates state.yaml hitl_3 via atomic write.

Usage:
    python3 -m investscan.approve_hitl          # interactive
    python3 -m investscan.approve_hitl --yes    # auto-approve (CI / autopilot mode)
"""
import argparse
import glob
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# ── helpers ───────────────────────────────────────────────────────────────────

def get_latest_report(reports_dir: str = "output/reports") -> str | None:
    reports = sorted(
        r for r in glob.glob(f"{reports_dir}/weekly-report-*.md")
        if not r.endswith(".ko.md")
    )
    return reports[-1] if reports else None


def parse_summary(path: str) -> dict:
    with open(path) as f:
        content = f.read()

    stock_m = re.search(r"\*\*(.+?)\s+\((\d{6})\)\*\*", content)
    stock = f"{stock_m.group(1)} ({stock_m.group(2)})" if stock_m else "N/A"

    week_m = re.search(r"Week:\s*([\w-]+)", content)
    week = week_m.group(1) if week_m else "N/A"

    cat_m = re.search(r"Category:\s*([AB])", content)
    category = "재무 실적 기반" if (cat_m and cat_m.group(1) == "A") else "테마 기반"

    dir_m = re.search(r"> \*\*(.+?)\*\*", content)
    direction = dir_m.group(1) if dir_m else "N/A"

    # Downside risk (first occurrence, truncated to 60 chars)
    risk_m = re.search(r"\*\*Downside Risk\*\*[:\s]+([^\n]+)", content)
    risk = risk_m.group(1).strip() if risk_m else "N/A"
    if len(risk) > 60:
        # truncate at last word boundary before limit
        truncated = risk[:60]
        last_space = truncated.rfind(" ")
        risk = (truncated[:last_space] if last_space > 0 else truncated[:57]) + "…"

    # YoY growth for quick context
    yoy_m = re.search(r"\*\*YoY Growth\*\*[:\s]+(.+?)(?=\n|-)", content)
    yoy = yoy_m.group(1).strip() if yoy_m else "N/A"

    return {
        "stock": stock,
        "week": week,
        "category": category,
        "direction": direction,
        "risk": risk,
        "yoy": yoy,
    }


def atomic_sot_update(sot_path: str = ".claude/state.yaml") -> bool:
    """Update hitl_3 in state.yaml using atomic temp→rename write."""
    try:
        import yaml  # type: ignore
    except ImportError:
        print("⚠️  PyYAML not found. Install with: pip install pyyaml")
        return False

    p = Path(sot_path)
    if not p.exists():
        print(f"⚠️  SOT not found: {sot_path}")
        return False

    try:
        with open(p) as f:
            sot = yaml.safe_load(f) or {}

        sot.setdefault("hitl_3", {})
        sot["hitl_3"].update(
            {
                "completed": True,
                "report_approved": True,
                "approved_at": datetime.now().isoformat(),
            }
        )

        tmp = str(p) + ".tmp"
        with open(tmp, "w") as f:
            yaml.dump(sot, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        os.replace(tmp, str(p))
        return True

    except Exception as exc:
        print(f"⚠️  SOT 업데이트 실패: {exc}")
        return False


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="HITL-3 Telegram dispatch approval")
    parser.add_argument("--yes", action="store_true", help="Auto-approve (autopilot / CI)")
    args = parser.parse_args()

    report = get_latest_report()
    if not report:
        print("⚠️  리포트 없음 — 먼저 주간 리포트를 생성하세요 (/weekly-report).")
        return 1

    info = parse_summary(report)
    date_str = os.path.basename(report).replace("weekly-report-", "").replace(".md", "")

    # Direction badge
    d = info["direction"].lower()
    badge = "📈" if ("positive" in d or "bullish" in d or "maintained" in d) else (
        "📉" if ("negative" in d or "bearish" in d or "risk" in d) else "➡️ "
    )

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋  HITL-3 최종 검토 — {date_str}  ({info["week"]})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  종목    {info["stock"]}  ({info["category"]})
  신호    {badge} {info["direction"]}
  실적    {info["yoy"]}
  리스크   {info["risk"]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    if args.yes:
        answer = "y"
        print("  Telegram 발송하시겠습니까? [Y/N]: Y  ← 자동 승인")
    else:
        try:
            answer = input("  Telegram 발송하시겠습니까? [Y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n⏸️  취소됨.")
            return 0

    print()

    if answer == "y":
        if not atomic_sot_update():
            return 1
        print("""✅  승인 완료 — state.yaml hitl_3 갱신
📱  Telegram 발송:
    python3 -m investscan.weekly_orchestrator --mode telegram-dispatch
""")
        return 0
    else:
        print("⏸️  취소됨 — 리포트를 다시 검토하세요.")
        print(f"    전체 리포트: {report}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
