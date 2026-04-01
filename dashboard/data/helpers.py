"""Shared helpers for parsing Idea Evolve files."""

import hashlib
import json
from pathlib import Path

import yaml


def _auto_run_root() -> Path:
    """Auto-detect the run root for multi-problem layout.
    Returns ie_root as fallback if no attempts exist."""
    ie_root = Path(__file__).resolve().parent.parent.parent / "idea-evolve"
    problems_dir = ie_root / "problems"
    if problems_dir.is_dir():
        for pdir in sorted(problems_dir.iterdir()):
            if pdir.is_dir():
                runs_dir = ie_root / "runs" / pdir.name
                if runs_dir.is_dir():
                    attempts = sorted(d for d in runs_dir.iterdir() if d.is_dir())
                    if attempts:
                        return attempts[-1]
    return ie_root


def _eval_cache(run_root: Path | None = None) -> dict:
    """Load the evaluation cache (content-hash -> result).

    If run_root is given, look for the cache there instead of the default path.
    """
    if run_root is not None:
        cache_path = run_root / "history" / "eval_cache.json"
    else:
        root = _auto_run_root()
        cache_path = root / "history" / "eval_cache.json"
    try:
        return json.loads(cache_path.read_text()) if cache_path.exists() else {}
    except Exception:
        return {}


def read_frontmatter(filepath: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    try:
        text = filepath.read_text()
        if not text.startswith("---"):
            return {}
        end = text.index("---", 3)
        fm = yaml.safe_load(text[3:end])
        return fm if isinstance(fm, dict) else {}
    except Exception:
        return {}


def read_body(filepath: Path) -> str:
    """Read content after YAML frontmatter."""
    try:
        text = filepath.read_text()
        if text.startswith("---"):
            end = text.index("---", 3)
            return text[end + 3:].strip()
        return text.strip()
    except Exception:
        return ""


def extract_score(sol_path: Path) -> dict | None:
    """Extract fitness score from a solution file (mirrors orchestrator logic).

    Checks .score sidecar file first, then parses header comments.
    Returns dict with at least 'fitness' key, or None.
    """
    score_file = sol_path.with_suffix(".score")
    if score_file.exists():
        try:
            data = json.loads(score_file.read_text())
            if isinstance(data, dict) and "fitness" in data:
                return data
        except Exception:
            pass

    # Fallback: check eval cache by file content hash
    try:
        content = sol_path.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        cache = _eval_cache()
        if sha in cache:
            return cache[sha]
    except Exception:
        pass

    # Header comment fallback removed — stale headers caused score inconsistencies.
    # Only .score sidecar and eval_cache are authoritative sources.
    return None


def get_metrics_config(problem_dir: Path | None = None) -> dict:
    """Read problem/metrics.yaml and return primary metric config.

    If problem_dir is given, look for metrics.yaml there instead of the default path.
    """
    if problem_dir is not None:
        metrics_path = problem_dir / "metrics.yaml"
    else:
        ie_root = Path(__file__).resolve().parent.parent.parent / "idea-evolve"
        # Try legacy path first, then auto-detect from problems/
        metrics_path = ie_root / "problem" / "metrics.yaml"
        if not metrics_path.exists():
            problems_dir = ie_root / "problems"
            if problems_dir.is_dir():
                for pdir in sorted(problems_dir.iterdir()):
                    candidate = pdir / "metrics.yaml"
                    if candidate.exists():
                        metrics_path = candidate
                        break
    try:
        data = yaml.safe_load(metrics_path.read_text())
        specs = data.get("specs", {})
        for name, spec in specs.items():
            if spec.get("is_primary"):
                return {
                    "name": name,
                    "higher_is_better": spec.get("higher_is_better", True),
                    "target_score": data.get("target_score"),
                    "decimals": spec.get("decimals", 4),
                    "lower_bound": spec.get("lower_bound"),
                    "upper_bound": spec.get("upper_bound"),
                    "sentinel_value": spec.get("sentinel_value"),
                }
        return {}
    except Exception:
        return {}


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    if size_bytes > 1048576:
        return f"{size_bytes / 1048576:.1f}M"
    if size_bytes > 1024:
        return f"{size_bytes / 1024:.1f}K"
    return f"{size_bytes}B"
