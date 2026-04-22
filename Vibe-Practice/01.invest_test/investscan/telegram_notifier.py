"""
investscan/telegram_notifier.py — Telegram delivery for InvestScan reports.
User-facing messages in Korean (P5 exception: Telegram is user delivery channel).
Supports --dry-run mode (print to stdout, no real API call).
DG-06: --dry-run mode must work without real bot token.
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TelegramConfig:
    """Telegram connection configuration."""
    bot_token: str
    chat_id: str
    dry_run: bool = False


def build_5line_summary(
    stock_name: str,
    stock_code: str,
    category: str,
    narrative_text: str,
    direction: str,
    downside_risk: str = "",
    dissolution_risk: str = "",
    catalyst: str = "",
    yoy_growth: str = "",
    market_size: str = "",
) -> str:
    """
    Build 5-line Telegram summary in Korean (v3.2 Q7 format).
    Bear Case NOT included (brevity — v3.6 I-12).

    Line 1: Stock + Category
    Line 2: Key metric (financial or theme)
    Line 3: Signal direction
    Line 4: Key risk
    Line 5: Next check date
    """
    lines = []

    # Line 1: Stock identification
    lines.append(f"📊 {stock_name}({stock_code}) — Category {category}")

    # Line 2: Key metric by category
    if category == "A" and yoy_growth:
        lines.append(f"💹 {yoy_growth}")
    elif category == "B" and market_size:
        lines.append(f"🌐 {market_size}")
    else:
        lines.append("💹 (재무 데이터 업데이트 중)")

    # Line 3: Signal direction
    direction_map = {
        "Positive momentum maintained": "🎯 긍정적 모멘텀 유지",
        "Neutral — monitor and wait": "🎯 중립 — 관망 권장",
        "Risk zone": "🎯 위험 구간 진입",
    }
    lines.append(direction_map.get(direction, f"🎯 {direction}"))

    # Line 4: Key risk
    risk_text = downside_risk or dissolution_risk or "(리스크 정보 없음)"
    # Truncate risk to 50 chars for Telegram brevity
    if len(risk_text) > 50:
        risk_text = risk_text[:47] + "..."
    lines.append(f"⚠️ 핵심 리스크: {risk_text}")

    # Line 5: Next check
    if catalyst:
        catalyst_short = catalyst[:40] + "..." if len(catalyst) > 40 else catalyst
        lines.append(f"📅 주목할 이벤트: {catalyst_short}")
    else:
        lines.append("📅 다음 주간 리포트에서 확인")

    return "\n".join(lines)


def send_message(
    text: str,
    config: TelegramConfig,
) -> bool:
    """
    Send text message via Telegram Bot API.
    Dry-run mode: prints to stdout, returns True.

    Returns:
        True on success (including dry-run), False on failure.
    """
    if config.dry_run:
        print(f"\n[DRY-RUN] Telegram message would be sent to chat_id={config.chat_id}:")
        print("─" * 50)
        print(text)
        print("─" * 50)
        return True

    try:
        import httpx

        url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
        response = httpx.post(
            url,
            json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"},
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info("Telegram message sent successfully")
        return True
    except Exception as e:
        logger.error("Telegram send failed: %s", e)
        # Log to telegram_err.log
        try:
            with open("logs/telegram_err.log", "a") as f:
                f.write(f"ERROR: {e}\n")
        except OSError:
            pass
        return False


def send_report(
    stock_name: str,
    stock_code: str,
    category: str,
    direction: str,
    narrative_fields: dict,
    config: TelegramConfig,
) -> bool:
    """
    Build and send 5-line summary for weekly report completion.

    Args:
        narrative_fields: dict with keys from NarrativeOutput schema
        config: Telegram connection config

    Returns:
        True on success.
    """
    summary = build_5line_summary(
        stock_name=stock_name,
        stock_code=stock_code,
        category=category,
        narrative_text=narrative_fields.get("text", ""),
        direction=direction,
        downside_risk=narrative_fields.get("downside_risk", ""),
        dissolution_risk=narrative_fields.get("dissolution_risk", ""),
        catalyst=narrative_fields.get("catalyst", ""),
        yoy_growth=narrative_fields.get("yoy_growth", ""),
        market_size=narrative_fields.get("market_size", ""),
    )
    return send_message(summary, config)


def hello_test(config: TelegramConfig) -> bool:
    """
    DG-00: Send installation hello message to verify Telegram connectivity.
    Message is in Korean (user-facing delivery channel).
    """
    message = (
        "✅ InvestScan 설치 완료!\n\n"
        "주간 투자 인사이트 시스템이 정상 연결되었습니다.\n"
        "매주 리포트를 이 채널로 받으실 수 있습니다.\n\n"
        "— InvestScan v1.0.0"
    )
    return send_message(message, config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="InvestScan Telegram Notifier")
    parser.add_argument("--hello-test", action="store_true", help="Send DG-00 hello message")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode")
    args = parser.parse_args()

    cfg = TelegramConfig(
        bot_token="MOCK_TOKEN",
        chat_id="MOCK_CHAT_ID",
        dry_run=args.dry_run,
    )

    if args.hello_test:
        success = hello_test(cfg)
        sys.exit(0 if success else 1)
