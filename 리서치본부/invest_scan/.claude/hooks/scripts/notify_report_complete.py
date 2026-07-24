#!/usr/bin/env python3
"""
notify_report_complete.py — PostToolUse hook (Bash matcher).

Fires a completion notification (Telegram + macOS banner) when the weekly
investment report PDF has just been generated.

Trigger logic (defensive — must never block the pipeline):
  1. Read the hook payload from stdin (JSON with tool_input.command).
  2. Only act if the command that just ran invoked `export_report`.
  3. Confirm today's PDF actually exists on disk.
  4. De-duplicate: skip if already notified for this date (marker file).
  5. Send Telegram message (+ PDF attachment) and a macOS banner.

This hook ALWAYS exits 0 — a notification failure must not break the run.
Telegram token/chat_id come from investscan.yaml (api_keys); if absent or
MOCK, the Telegram step is skipped (macOS banner still fires).
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[3]
PDF_DIR = Path.home() / "Desktop" / "Ai_works" / "output" / "투자분석제안"
TEMP_DIR = PROJECT_DIR / "output" / "temp"
MARKER_DIR = PROJECT_DIR / "output" / "temp"


def _read_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _command_from_payload(payload: dict) -> str:
    ti = payload.get("tool_input", {})
    if isinstance(ti, dict):
        return str(ti.get("command", ""))
    return ""


def _load_telegram_config():
    """Return (bot_token, chat_id) from investscan.yaml, or (None, None)."""
    try:
        import yaml
        cfg = yaml.safe_load((PROJECT_DIR / "investscan.yaml").read_text())
        ak = (cfg or {}).get("api_keys", {})
        bot = ak.get("telegram_bot_token")
        chat = ak.get("telegram_chat_id")
        if not bot or not chat or bot == "MOCK_TOKEN" or chat == "MOCK_CHAT_ID":
            return None, None
        return bot, chat
    except Exception:
        return None, None


def _code_name_map() -> dict[str, str]:
    """Map stock code → display name from sector_stock_map.yaml (best-effort)."""
    try:
        import yaml
        data = yaml.safe_load(
            (PROJECT_DIR / "config" / "sector_stock_map.yaml").read_text(encoding="utf-8")
        )
        out: dict[str, str] = {}
        for sec in (data or {}).get("sectors", {}).values():
            for s in sec.get("sample_stocks", []):
                out[str(s.get("code", "")).strip()] = str(s.get("name", "")).strip()
        return out
    except Exception:
        return {}


def _fmt_codes(codes: list[str], names: dict[str, str]) -> str:
    if not codes:
        return "없음"
    return ", ".join(f"{names.get(c, c)}({c})" if names.get(c) else c for c in codes)


def _build_summary(run_date: str) -> str:
    """Compose the notification text from the confirmed watchlist."""
    wl_path = TEMP_DIR / f"confirmed_watchlist_{run_date}.json"
    lines = [f"📊 InvestScan 주간 리포트 완료 — {run_date}"]
    try:
        wl = json.loads(wl_path.read_text(encoding="utf-8"))
        names = _code_name_map()
        regime = wl.get("market_regime", "n/a")
        cat_a = wl.get("cat_a", [])
        cat_b = wl.get("cat_b", [])
        quorum = wl.get("quorum", {})
        lines.append(f"레짐: {regime}")
        lines.append(f"Cat A ({len(cat_a)}): {_fmt_codes(cat_a, names)}")
        lines.append(f"Cat B ({len(cat_b)}): {_fmt_codes(cat_b, names)}")
        if quorum and not quorum.get("quorum_ok", True):
            lines.append(
                f"⚠️ 정족수 미달 — {quorum.get('loaded')}/{quorum.get('total')} 에이전트"
            )
    except Exception:
        lines.append("(watchlist 요약 불가 — PDF 참조)")
    return "\n".join(lines)


def _send_macos_banner(title: str, message: str) -> None:
    """Best-effort macOS notification banner + sound."""
    try:
        safe_title = title.replace('"', "'")
        safe_msg = message.replace('"', "'")
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{safe_msg}" with title "{safe_title}" sound name "Glass"'],
            check=False, timeout=10,
        )
    except Exception:
        pass


def main() -> int:
    payload = _read_payload()
    command = _command_from_payload(payload)

    # Only react to the report-export command.
    if "export_report" not in command:
        return 0

    run_date = date.today().isoformat()
    pdf_path = PDF_DIR / f"{run_date}_주간투자분석.pdf"
    if not pdf_path.exists():
        # Report not actually produced (e.g. export failed) — nothing to notify.
        return 0

    # De-duplicate: one notification per date.
    marker = MARKER_DIR / f".notified_{run_date}"
    if marker.exists():
        return 0

    summary = _build_summary(run_date)

    # macOS banner (always attempted).
    first_line = summary.splitlines()[0] if summary else "리포트 완료"
    rest = "\n".join(summary.splitlines()[1:]) or "PDF 생성됨"
    _send_macos_banner(first_line, rest)

    # Telegram (message + PDF) — only if token configured.
    bot, chat = _load_telegram_config()
    if bot and chat:
        try:
            sys.path.insert(0, str(PROJECT_DIR))
            from investscan.telegram_notifier import (
                TelegramConfig, send_message, send_document,
            )
            cfg = TelegramConfig(bot_token=bot, chat_id=chat, dry_run=False)
            send_message(summary, cfg)
            send_document(str(pdf_path), cfg, caption=f"{run_date} 주간투자분석")
        except Exception:
            pass  # never break the pipeline on notification failure

    try:
        marker.write_text(run_date, encoding="utf-8")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Absolutely never block on notification errors.
        sys.exit(0)
