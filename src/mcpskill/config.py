"""Configuration loading and validation."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .types import Config


class ConfigError(Exception):
    """Configuration error."""
    pass


def load_config(config_path: str | Path) -> Config:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Validated Config object

    Raises:
        ConfigError: If configuration is invalid or file not found
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML: {e}")

    # Expand environment variables in the config
    data = _expand_env_vars(data)

    try:
        return Config(**data)
    except ValidationError as e:
        raise ConfigError(f"Invalid configuration: {e}")


def _expand_env_vars(data: Any) -> Any:
    """Recursively expand environment variables in config data.

    Supports ${VAR_NAME} syntax.
    """
    if isinstance(data, dict):
        return {k: _expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Replace ${VAR} with environment variable value
        if data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            value = os.getenv(var_name)
            if value is None:
                raise ConfigError(f"Environment variable not set: {var_name}")
            return value
        return data
    else:
        return data
