"""Configuration loader for the Harness Engineering System.

Exposes ``load_config`` so the orchestrator can ``from config import load_config``.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = CONFIG_DIR / "harness_config.yaml"

# The source spec referenced fictional model IDs. Map them to real current IDs so an
# unmodified spec-config still runs. Real IDs and aliases pass through untouched.
_MODEL_ALIASES = {
    "claude-opus-4-6-20251101": "claude-opus-4-8",
    "claude-opus-4-6": "claude-opus-4-8",
    "claude-sonnet-4-20250514": "claude-sonnet-4-6",
    "claude-sonnet-4-5": "claude-sonnet-4-6",
}


def _normalize_model(model: str) -> str:
    return _MODEL_ALIASES.get(model, model)


def load_config(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load and lightly validate harness config.

    Returns a plain dict. Model IDs are normalized to real current IDs.
    """
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Harness config not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    models = cfg.setdefault("models", {})
    for role, model in list(models.items()):
        if isinstance(model, str):
            models[role] = _normalize_model(model)

    # Minimal sanity checks — fail fast with a clear message.
    harness = cfg.setdefault("harness", {})
    harness.setdefault("max_sprints", 8)
    harness.setdefault("max_qa_rounds", 3)
    harness.setdefault("qa_pass_threshold", 6.0)
    harness.setdefault("min_criteria_per_sprint", 15)

    weights = cfg.get("evaluation", {}).get("weights", {})
    if weights:
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"evaluation.weights must sum to 1.0, got {total:.3f}: {weights}"
            )

    return cfg
