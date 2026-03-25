"""Project configuration and root resolution."""

from pathlib import Path

import yaml

# Alpha-evolve root (sibling of dashboard/)
_PROJECT_ROOT = Path(__file__).parent.parent.parent / "alpha-evolve"


def get_project_root() -> Path:
    return _PROJECT_ROOT


def get_config() -> dict:
    config_path = _PROJECT_ROOT / "user" / "config.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text()) or {}
    return {}
