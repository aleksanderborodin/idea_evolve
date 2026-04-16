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
    """List problem IDs from problems/ directory.

    Skips underscore-prefixed entries (`__pycache__`, `_shared`, `_kaggle_template`, ...)
    which are internal modules / templates, not problems. A real problem must also have a
    `description.md` to be selectable.
    """
    problems_dir = _PROJECT_ROOT / "problems"
    if not problems_dir.is_dir():
        return []
    return sorted(
        d.name
        for d in problems_dir.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and (d / "description.md").is_file()
    )


def list_attempts(problem_id: str) -> list[str]:
    """List attempt IDs for a problem from runs/{problem_id}/."""
    runs_dir = _PROJECT_ROOT / "runs" / problem_id
    if not runs_dir.is_dir():
        return []
    return sorted(d.name for d in runs_dir.iterdir() if d.is_dir())


def get_run_root(problem_id: str | None = None, attempt_id: str | None = None) -> Path | None:
    """Get the run root path for a problem/attempt.
    Returns None if no valid attempt exists."""
    if problem_id is None:
        return None
    if attempt_id is None:
        # Find latest attempt
        attempts = list_attempts(problem_id)
        if attempts:
            return _PROJECT_ROOT / "runs" / problem_id / attempts[-1]
        return None
    run_path = _PROJECT_ROOT / "runs" / problem_id / attempt_id
    if run_path.is_dir():
        return run_path
    return None


def get_problem_dir(problem_id: str | None = None) -> Path | None:
    """Get the problem definition directory. Returns None if not found."""
    if problem_id is None:
        # Return first available problem
        problems = list_problems()
        if problems:
            return _PROJECT_ROOT / "problems" / problems[0]
        return None
    prob_path = _PROJECT_ROOT / "problems" / problem_id
    if prob_path.is_dir():
        return prob_path
    return None
