"""
investscan/accuracy_tracker.py — Track and measure prediction accuracy.
v3.6 I-3: Dual measurement window — 4-week (preliminary) + 8-week (final KS-1 basis).
v3.6 I-5: KS-1 label uses "Month 3 data basis" (measurement lag accounted).
v3.6 I-13: 3 naive baseline strategies for comparison.
English-First (P5-A). Python-First (P6): all accuracy computations are Python.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from investscan.schema import PredictionRecord

logger = logging.getLogger(__name__)

# Measurement windows (v3.6 I-3)
ACCURACY_WINDOW_PRELIMINARY: int = 4   # weeks — preliminary reading
ACCURACY_WINDOW_FINAL: int = 8         # weeks — final KS-1 basis

# Bullish threshold for accuracy evaluation
BULLISH_THRESHOLD: float = 0.01        # +1% (v3.6 I-4)
NEUTRAL_BAND: float = 0.03             # ±3%

# Data directory
ACCURACY_DIR: str = "data/accuracy"


def record_prediction(
    stock_code: str,
    direction: str,
    week_label: str | None = None,
    config: dict | None = None,
) -> PredictionRecord:
    """
    Record a new weekly prediction. Appends to JSONL file.

    Args:
        stock_code: KRX stock code
        direction: Prediction direction from NarrativeOutput
        week_label: ISO week label (e.g., "2026-W13"). Auto-generated if None.
        config: Optional config dict

    Returns:
        Created PredictionRecord.
    """
    if week_label is None:
        iso_week = datetime.now().isocalendar()
        week_label = f"{iso_week[0]}-W{iso_week[1]:02d}"

    record = PredictionRecord(
        week_label=week_label,
        stock_code=stock_code,
        direction=direction,
        actual_return_4w=None,
        actual_return_8w=None,
        recorded_at=datetime.now().isoformat() + "Z",
    )

    _append_record(record, config)
    logger.info("Prediction recorded: %s %s → %s", week_label, stock_code, direction)
    return record


def update_actual_return(
    stock_code: str,
    week_label: str,
    actual_return: float,
    window: int,
    config: dict | None = None,
) -> bool:
    """
    Update actual return for a recorded prediction.

    Args:
        window: 4 (preliminary) or 8 (final KS-1)

    Returns:
        True if record was found and updated.
    """
    records = load_all_records(stock_code, config)
    updated = False

    for i, rec in enumerate(records):
        if rec["week_label"] == week_label and rec["stock_code"] == stock_code:
            if window == ACCURACY_WINDOW_PRELIMINARY:
                records[i]["actual_return_4w"] = actual_return
            elif window == ACCURACY_WINDOW_FINAL:
                records[i]["actual_return_8w"] = actual_return
            updated = True
            break

    if updated:
        _write_all_records(records, stock_code, config)
        logger.info("Updated %sw actual return for %s %s: %.3f",
                    window, week_label, stock_code, actual_return)
    return updated


def compute_accuracy(
    stock_code: str,
    window: int = ACCURACY_WINDOW_FINAL,
    config: dict | None = None,
) -> dict:
    """
    Compute prediction accuracy for a stock over the measurement window.
    Uses 8-week window as KS-1 basis (v3.6 I-3, I-5).

    Returns:
        dict with: {accuracy, total, correct, window, ks1_label, naive_baselines}
    """
    records = load_all_records(stock_code, config)
    return_field = "actual_return_8w" if window == ACCURACY_WINDOW_FINAL else "actual_return_4w"

    completed = [r for r in records if r.get(return_field) is not None]
    if not completed:
        return {
            "accuracy": None,
            "total": 0,
            "correct": 0,
            "window": window,
            "ks1_label": "Month 3 data basis",  # v3.6 I-5: NOT "Month 2"
            "naive_baselines": _compute_naive_baselines(completed, return_field),
        }

    correct = 0
    for rec in completed:
        actual_return = rec[return_field]
        predicted = rec["direction"]
        actual_direction = _return_to_direction(actual_return)
        if predicted == actual_direction:
            correct += 1

    accuracy = correct / len(completed) if completed else 0.0

    return {
        "accuracy": accuracy,
        "total": len(completed),
        "correct": correct,
        "window": window,
        "ks1_label": "Month 3 data basis",  # v3.6 I-5
        "naive_baselines": _compute_naive_baselines(completed, return_field),
    }


def _return_to_direction(actual_return: float) -> str:
    """Convert actual return to direction label using Python thresholds (P6)."""
    if actual_return > BULLISH_THRESHOLD:
        return "Positive momentum maintained"
    elif abs(actual_return) <= NEUTRAL_BAND:
        return "Neutral — monitor and wait"
    else:
        return "Risk zone"


def _compute_naive_baselines(
    completed_records: list[dict],
    return_field: str,
) -> dict:
    """
    Compute 3 naive baseline accuracies for KS-1 comparison (v3.6 I-13).
    Baselines: Always-Bullish, Momentum, Random.
    """
    if not completed_records:
        return {"always_bullish": None, "momentum": None, "random": 0.333}

    n = len(completed_records)
    always_bullish_correct = sum(
        1 for r in completed_records
        if _return_to_direction(r[return_field]) == "Positive momentum maintained"
    )

    return {
        "always_bullish": always_bullish_correct / n,
        "momentum": None,   # Requires sequential records — computed externally
        "random": 1 / 3,    # 3-class uniform random baseline
    }


def load_all_records(stock_code: str, config: dict | None = None) -> list[dict]:
    """Load all prediction records for a stock from JSONL file."""
    config = config or {}
    accuracy_dir = config.get("paths", {}).get("accuracy_data", ACCURACY_DIR)
    path = Path(accuracy_dir) / f"{stock_code}.jsonl"

    if not path.exists():
        return []

    records = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to load records for %s: %s", stock_code, e)
    return records


def _append_record(record: PredictionRecord, config: dict | None = None) -> None:
    """Append a PredictionRecord to the stock's JSONL file."""
    config = config or {}
    accuracy_dir = config.get("paths", {}).get("accuracy_data", ACCURACY_DIR)
    Path(accuracy_dir).mkdir(parents=True, exist_ok=True)
    path = Path(accuracy_dir) / f"{record.stock_code}.jsonl"

    try:
        with open(path, "a") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    except OSError as e:
        logger.error("Failed to append prediction record: %s", e)


def _write_all_records(records: list[dict], stock_code: str, config: dict | None = None) -> None:
    """Overwrite JSONL file with updated records."""
    config = config or {}
    accuracy_dir = config.get("paths", {}).get("accuracy_data", ACCURACY_DIR)
    path = Path(accuracy_dir) / f"{stock_code}.jsonl"

    try:
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tmp.rename(path)
    except OSError as e:
        logger.error("Failed to write records for %s: %s", stock_code, e)
