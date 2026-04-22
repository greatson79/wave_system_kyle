"""
investscan/config.py — Configuration loader for InvestScan pipeline.
Supports dry-run mode (no real API keys) and live mode (keyring).
English-First (P5-A): all keys, log messages, error messages in English.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Required top-level fields that must exist in a valid config
_REQUIRED_FIELDS = ("mode", "version", "paths")


class ConfigError(Exception):
    """Raised when the configuration is missing required fields or is otherwise invalid."""


def load_config(config_path: str = "investscan.yaml") -> dict:
    """
    Load YAML config from *config_path* and merge environment variable overrides.

    Environment variable overrides:
        INVESTSCAN_MODE  — overrides config["mode"]

    Returns the merged config dict.
    Raises ConfigError if the file is missing or required fields are absent.
    """
    if not os.path.exists(config_path):
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config: dict[str, Any] = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse config file '{config_path}': {exc}") from exc

    # Validate required fields
    for field in _REQUIRED_FIELDS:
        if field not in config:
            raise ConfigError(f"Missing required config field: '{field}'")

    # Merge environment variable overrides
    env_mode = os.environ.get("INVESTSCAN_MODE")
    if env_mode is not None:
        logger.debug("INVESTSCAN_MODE env var overrides config mode: %s → %s", config.get("mode"), env_mode)
        config["mode"] = env_mode

    logger.debug("Config loaded from '%s' — mode=%s", config_path, config.get("mode"))
    return config


def is_dry_run(config: dict) -> bool:
    """Return True when the pipeline is operating in dry-run mode."""
    return str(config.get("mode", "dry-run")).strip().lower() == "dry-run"


def get_api_key(key_name: str, config: dict) -> str:
    """
    Return the API key identified by *key_name*.

    Dry-run mode  — returns the mock value stored in config["api_keys"][key_name].
    Live mode     — reads the secret from the system keyring (service="investscan").

    Raises ConfigError if the key cannot be resolved.
    """
    if is_dry_run(config):
        mock_keys: dict = config.get("api_keys", {})
        if key_name not in mock_keys:
            raise ConfigError(f"Dry-run: api_keys.{key_name} not found in config")
        value = mock_keys[key_name]
        logger.debug("Dry-run: returning mock API key for '%s'", key_name)
        return str(value)

    # Live mode — use keyring
    try:
        import keyring  # type: ignore[import]
    except ImportError as exc:
        raise ConfigError(
            "keyring package is required for live mode. Install with: pip install keyring"
        ) from exc

    value = keyring.get_password("investscan", key_name)
    if value is None:
        raise ConfigError(
            f"Live mode: keyring has no entry for service='investscan', username='{key_name}'. "
            "Set it with: keyring set investscan <key_name>"
        )
    logger.debug("Live mode: resolved keyring entry for '%s'", key_name)
    return value


def get_envscan_path(config: dict) -> str:
    """
    Return the EnvironmentScan output file path.

    Dry-run — returns the fixture path from config["paths"]["envscan_output"].
    Live    — returns the real envscan output path (same config key, different value in live config).
    """
    paths: dict = config.get("paths", {})
    envscan_path = paths.get("envscan_output")
    if not envscan_path:
        raise ConfigError("Missing required config field: 'paths.envscan_output'")
    logger.debug("envscan_path resolved: '%s' (dry_run=%s)", envscan_path, is_dry_run(config))
    return str(envscan_path)
