"""Shared helpers used by every `problems/<id>/evaluate.py`.

Each problem still owns the solution-loading and scoring logic — this module
just consolidates the boring, identical-across-problems parts:

- `write_score_sidecar` — atomic `.score` sidecar write next to the solution.
- `build_error_result` — uniform error dict populated with sentinel values
  from `metrics.yaml`, including `error` / `traceback` / `eval_time_s` /
  `eval_started_at` / `eval_ended_at`.
- `try_kill_stale_same_agent` — peer-mediated kill of the agent's own prior
  eval before starting a new one, using the per-problem `eval_hooks.py` if
  present (falls back to the default SIGTERM→SIGKILL hook).
- `try_diagnose_failure` — embed a problem-specific "what to try next"
  markdown hint in the proc_log / sidecar if `eval_hooks.diagnose_failure`
  exists. Returns None when no hook is defined.

Never import this from a solution module — it's eval-side only.
"""

from __future__ import annotations

import importlib.util
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import eval_queue
from .constants import ENV_AGENT_NAME


def write_score_sidecar(solution_path: str | os.PathLike, result: dict) -> None:
    """Atomic write of the `.score` sidecar alongside the solution.

    Never raises — a sidecar that can't be written should not break the
    eval. The cache fallback covers score loss in that case.
    """
    try:
        score_path = Path(solution_path).with_suffix(".score")
        tmp_path = score_path.with_suffix(".score.tmp")
        tmp_path.write_text(json.dumps(result, indent=2))
        tmp_path.rename(score_path)
    except Exception:
        pass


def _load_sentinel_values(problem_root: Path) -> dict[str, Any]:
    """Return {metric_name: sentinel_value} from metrics.yaml, or empty."""
    metrics_path = Path(problem_root) / "metrics.yaml"
    if not metrics_path.exists():
        return {}
    try:
        import yaml  # noqa: PLC0415 — lazy; not every caller has PyYAML on sys.path warm
        data = yaml.safe_load(metrics_path.read_text()) or {}
        return {
            name: spec.get("sentinel_value", 0)
            for name, spec in (data.get("specs", {}) or {}).items()
            if isinstance(spec, dict)
        }
    except Exception:
        return {}


def build_error_result(
    problem_root: Path,
    exc: BaseException,
    t0: Optional[float] = None,
    started_at: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    """Construct a sentinel-filled error result for a failed eval.

    Uses sentinel values from `metrics.yaml:specs` so every declared metric
    has a defined value in the `.score` sidecar and eval cache. Always
    includes `error` (truncated) and `traceback` (truncated). Attaches
    timing fields when measurement had started.

    `extra` lets the caller override or add problem-specific fields
    (e.g. `avg_path_length`, `per_class`) that aren't in metrics.yaml.
    """
    sentinels = _load_sentinel_values(problem_root)
    result: dict[str, Any] = dict(sentinels)
    # Fallback: if metrics.yaml is unreadable, at least fitness + is_valid.
    result.setdefault("fitness", 0)
    result.setdefault("is_valid", 0)
    result["error"] = str(exc)[:500]
    result["traceback"] = traceback.format_exc()[:4000]
    if t0 is not None:
        result["eval_time_s"] = round(time.perf_counter() - t0, 4)
        result["eval_started_at"] = started_at
        result["eval_ended_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if extra:
        result.update(extra)
    return result


def _import_problem_eval_hooks(problem_root: Path):
    """Load `problem_root/eval_hooks.py` as a module if it exists, else None."""
    hooks_path = Path(problem_root) / "eval_hooks.py"
    if not hooks_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            f"_eval_hooks_{problem_root.name}", hooks_path
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def try_kill_stale_same_agent(problem_root: Path) -> list[dict]:
    """Invoke `eval_queue.kill_stale_same_agent` with the problem's hook.

    Reads agent name from env (set by orchestrator). If there's no
    per-problem `eval_hooks.py`, the default kill hook is used. Fails
    open — never raises.
    """
    agent = os.environ.get(ENV_AGENT_NAME, "").strip()
    if not agent or agent == "unknown":
        return []
    hook = None
    mod = _import_problem_eval_hooks(problem_root)
    if mod is not None and hasattr(mod, "kill_eval"):
        hook = mod.kill_eval
    try:
        return eval_queue.kill_stale_same_agent(agent, kill_hook=hook)
    except Exception:
        return []


def try_diagnose_failure(
    problem_root: Path,
    error_class: str,
    error_message: str,
    context: Optional[dict] = None,
) -> Optional[str]:
    """Return the per-problem diagnose_failure() markdown, or None.

    Uses the problem's `eval_hooks.diagnose_failure` if defined.
    """
    mod = _import_problem_eval_hooks(problem_root)
    if mod is None or not hasattr(mod, "diagnose_failure"):
        return None
    try:
        out = mod.diagnose_failure(error_class, error_message, context or {})
        return out if isinstance(out, str) and out.strip() else None
    except Exception:
        return None
