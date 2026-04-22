"""
tests/test_config.py — Unit tests for investscan.config module.
Standard coverage target: 85%.
All test code and messages in English (P5-A).
"""
from __future__ import annotations

import os
import textwrap

import pytest

from investscan.config import ConfigError, get_api_key, get_envscan_path, is_dry_run, load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Path to the real project-root config (dry-run fixture)
_REAL_CONFIG = os.path.join(os.path.dirname(__file__), "..", "investscan.yaml")


# ---------------------------------------------------------------------------
# test_load_config_dry_run
# ---------------------------------------------------------------------------

def test_load_config_dry_run():
    """load_config() on the real investscan.yaml must return mode == 'dry-run'."""
    config = load_config(_REAL_CONFIG)
    assert config["mode"] == "dry-run"


# ---------------------------------------------------------------------------
# test_is_dry_run_true
# ---------------------------------------------------------------------------

def test_is_dry_run_true():
    """is_dry_run() returns True when config['mode'] == 'dry-run'."""
    config = {"mode": "dry-run", "version": "1.0.0", "paths": {}}
    assert is_dry_run(config) is True


def test_is_dry_run_false():
    """is_dry_run() returns False when config['mode'] == 'live'."""
    config = {"mode": "live", "version": "1.0.0", "paths": {}}
    assert is_dry_run(config) is False


# ---------------------------------------------------------------------------
# test_get_api_key_dry_run_returns_mock
# ---------------------------------------------------------------------------

def test_get_api_key_dry_run_returns_mock():
    """In dry-run mode, get_api_key() must return a MOCK_-prefixed value from config."""
    config = load_config(_REAL_CONFIG)
    key = get_api_key("fred_api_key", config)
    assert key.startswith("MOCK_"), f"Expected MOCK_ prefix, got: {key!r}"


def test_get_api_key_dry_run_all_keys():
    """All four mock API keys must be resolvable in dry-run mode."""
    config = load_config(_REAL_CONFIG)
    for key_name in ("fred_api_key", "dart_api_key", "telegram_bot_token", "telegram_chat_id"):
        value = get_api_key(key_name, config)
        assert isinstance(value, str) and len(value) > 0, f"Empty value for '{key_name}'"


def test_get_api_key_missing_key_raises():
    """get_api_key() with an unknown key name must raise ConfigError in dry-run."""
    config = {"mode": "dry-run", "version": "1.0.0", "paths": {}, "api_keys": {}}
    with pytest.raises(ConfigError, match="api_keys.nonexistent_key"):
        get_api_key("nonexistent_key", config)


# ---------------------------------------------------------------------------
# test_get_envscan_path_dry_run
# ---------------------------------------------------------------------------

def test_get_envscan_path_dry_run():
    """get_envscan_path() in dry-run must return a path that includes 'fixtures'."""
    config = load_config(_REAL_CONFIG)
    path = get_envscan_path(config)
    assert "fixture" in path.lower() or "tests" in path.lower(), (
        f"Expected fixture-like path, got: {path!r}"
    )


def test_get_envscan_path_missing_raises():
    """get_envscan_path() raises ConfigError when paths.envscan_output is absent."""
    config = {"mode": "dry-run", "version": "1.0.0", "paths": {}}
    with pytest.raises(ConfigError, match="envscan_output"):
        get_envscan_path(config)


# ---------------------------------------------------------------------------
# test_config_error_on_missing_file
# ---------------------------------------------------------------------------

def test_config_error_on_missing_file():
    """load_config() must raise ConfigError when the YAML file does not exist."""
    with pytest.raises(ConfigError, match="not found"):
        load_config("/nonexistent/path/investscan.yaml")


# ---------------------------------------------------------------------------
# test_load_config_merges_env_var
# ---------------------------------------------------------------------------

def test_load_config_merges_env_var(monkeypatch):
    """INVESTSCAN_MODE env var must override the mode field in the loaded config."""
    monkeypatch.setenv("INVESTSCAN_MODE", "live")
    config = load_config(_REAL_CONFIG)
    assert config["mode"] == "live", (
        f"Expected mode='live' after env override, got {config['mode']!r}"
    )


def test_load_config_no_env_var_uses_file_mode(monkeypatch):
    """Without INVESTSCAN_MODE env var, mode comes from the YAML file."""
    monkeypatch.delenv("INVESTSCAN_MODE", raising=False)
    config = load_config(_REAL_CONFIG)
    assert config["mode"] == "dry-run"


# ---------------------------------------------------------------------------
# test_load_config_raises_on_missing_required_fields
# ---------------------------------------------------------------------------

def test_load_config_raises_on_missing_required_fields(tmp_path):
    """load_config() raises ConfigError when a required field ('paths') is missing."""
    minimal_yaml = tmp_path / "bad.yaml"
    minimal_yaml.write_text("mode: dry-run\nversion: '1.0.0'\n")
    with pytest.raises(ConfigError, match="paths"):
        load_config(str(minimal_yaml))


def test_load_config_raises_on_missing_mode(tmp_path):
    """load_config() raises ConfigError when 'mode' field is absent."""
    minimal_yaml = tmp_path / "no_mode.yaml"
    minimal_yaml.write_text("version: '1.0.0'\npaths: {}\n")
    with pytest.raises(ConfigError, match="mode"):
        load_config(str(minimal_yaml))
