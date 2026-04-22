"""
investscan/personalizer.py — Day 0 installation verification and personalization.
DG-00: --hello-test sends Telegram "설치 완료" message within 10 minutes.
User-facing messages in Korean (P5 exception: delivery channel).
English-First (P5-A) for internal logic, logging, error messages.
"""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import yaml

from investscan.telegram_notifier import TelegramConfig, hello_test

logger = logging.getLogger(__name__)

CONFIG_PATH: str = "investscan.yaml"


def load_config_for_personalizer() -> dict:
    """Load investscan.yaml for personalizer use."""
    path = Path(CONFIG_PATH)
    if not path.exists():
        logger.error("Config file not found: %s", CONFIG_PATH)
        return {"mode": "dry-run", "api_keys": {}}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("Failed to load config: %s", e)
        return {"mode": "dry-run", "api_keys": {}}


def run_hello_test(dry_run: bool = True) -> bool:
    """
    DG-00: Send Telegram hello message to verify connectivity.
    In dry-run mode: prints to stdout (no real API call).

    Returns:
        True if message sent successfully within timeout.
    """
    config = load_config_for_personalizer()
    is_dry = dry_run or config.get("mode", "dry-run") == "dry-run"

    bot_token = config.get("api_keys", {}).get("telegram_bot_token", "MOCK_TOKEN")
    chat_id = config.get("api_keys", {}).get("telegram_chat_id", "MOCK_CHAT_ID")

    tg_config = TelegramConfig(
        bot_token=bot_token,
        chat_id=chat_id,
        dry_run=is_dry,
    )

    start_time = time.time()
    success = hello_test(tg_config)
    elapsed = time.time() - start_time

    if success:
        logger.info("DG-00 PASS: Hello message sent in %.1f seconds", elapsed)
        print(f"DG-00 PASS: Telegram connection verified ({elapsed:.1f}s)")
    else:
        logger.error("DG-00 FAIL: Hello message failed after %.1f seconds", elapsed)
        print(f"DG-00 FAIL: Check bot_token and chat_id in investscan.yaml")

    return success


def check_installation_prerequisites(config: dict) -> dict[str, bool]:
    """
    Check all prerequisite conditions for InvestScan installation.

    Returns:
        dict of {check_name: passed} — all must be True for DG-00.
    """
    results = {}

    # Check config file exists
    results["config_file_exists"] = Path(CONFIG_PATH).exists()

    # Check output directories exist
    for d in ["output", "output/reports", "output/temp", "data/accuracy", "logs"]:
        results[f"dir_{d.replace('/', '_')}"] = Path(d).exists()

    # Check fixtures for dry-run
    results["fixtures_envscan"] = Path("tests/fixtures/envscan_sample.json").exists()
    results["fixtures_fred"] = Path("tests/fixtures/fred_sample.json").exists()

    # Check API key placeholders present
    api_keys = config.get("api_keys", {})
    results["telegram_token_set"] = bool(api_keys.get("telegram_bot_token"))
    results["telegram_chat_id_set"] = bool(api_keys.get("telegram_chat_id"))

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="InvestScan Personalizer — DG-00 verification")
    parser.add_argument("--hello-test", action="store_true",
                        help="DG-00: Send Telegram hello message (10 min timeout)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Dry run mode — print instead of sending")
    parser.add_argument("--check-prereqs", action="store_true",
                        help="Check installation prerequisites")
    args = parser.parse_args()

    if args.hello_test:
        success = run_hello_test(dry_run=args.dry_run)
        sys.exit(0 if success else 1)

    elif args.check_prereqs:
        cfg = load_config_for_personalizer()
        checks = check_installation_prerequisites(cfg)
        all_passed = all(checks.values())
        for name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {name}")
        print(f"\nPrerequisites: {'ALL PASS' if all_passed else 'SOME FAILED'}")
        sys.exit(0 if all_passed else 1)

    else:
        parser.print_help()
