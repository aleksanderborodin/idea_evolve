"""Project configuration and root resolution."""

from pathlib import Path

import yaml

# Idea-evolve root (sibling of dashboard/)
_PROJECT_ROOT = Path(__file__).parent.parent.parent / "idea-evolve"


def get_project_root() -> Path:
    return _PROJECT_ROOT


def get_config() -> dict:
    config_path = _PROJECT_ROOT / "user" / "config.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text()) or {}
    return {}


# ---------------------------------------------------------------------------
# Multi-problem / multi-attempt discovery
# ---------------------------------------------------------------------------

def _is_legacy_layout() -> bool:
    """Check if we're using the legacy single-problem layout (no problems/ dir)."""
    return not (_PROJECT_ROOT / "problems").is_dir()


def list_problems() -> list[str]:
    """List problem IDs from problems/ directory. Falls back to ['default'] for legacy layout."""
    problems_dir = _PROJECT_ROOT / "problems"
    if not problems_dir.is_dir():
        return ["default"]
    ids = sorted(d.name for d in problems_dir.iterdir() if d.is_dir())
    return ids if ids else ["default"]


def list_attempts(problem_id: str) -> list[str]:
    """List attempt IDs for a problem from runs/{problem_id}/."""
    if _is_legacy_layout():
        return ["legacy"]
    runs_dir = _PROJECT_ROOT / "runs" / problem_id
    if not runs_dir.is_dir():
        return ["legacy"]
    ids = sorted(d.name for d in runs_dir.iterdir() if d.is_dir())
    return ids if ids else ["legacy"]


def get_run_root(problem_id: str | None = None, attempt_id: str | None = None) -> Path:
    """Get the run root path for a problem/attempt.

    Legacy layout: returns _PROJECT_ROOT (the idea-evolve/ dir itself).
    Multi-problem layout: returns runs/{problem_id}/{attempt_id}/.
    """
    if _is_legacy_layout() or problem_id is None or problem_id == "default":
        return _PROJECT_ROOT
    if attempt_id is None or attempt_id == "legacy":
        return _PROJECT_ROOT
    run_path = _PROJECT_ROOT / "runs" / problem_id / attempt_id
    if run_path.is_dir():
        return run_path
    # Fallback to legacy
    return _PROJECT_ROOT


def get_problem_dir(problem_id: str | None = None) -> Path:
    """Get the problem definition directory.

    Legacy layout: returns _PROJECT_ROOT / 'problem'.
    Multi-problem layout: returns problems/{problem_id}/.
    """
    if _is_legacy_layout() or problem_id is None or problem_id == "default":
        return _PROJECT_ROOT / "problem"
    prob_path = _PROJECT_ROOT / "problems" / problem_id
    if prob_path.is_dir():
        return prob_path
    # Fallback to legacy
    return _PROJECT_ROOT / "problem"
