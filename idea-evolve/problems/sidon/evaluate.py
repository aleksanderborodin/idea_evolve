#!/usr/bin/env python3
"""
Evaluate a solution for the Sidon Sets problem.

Usage: python3 evaluate.py <solution_file.py>

The solution file must implement def entrypoint() that returns a list of integers.
Prints JSON with {fitness, is_valid, violations, raw_size} fields.
"""

import fcntl
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path

PROBLEM_ROOT = Path(__file__).parent
_IDEA_EVOLVE_ROOT = PROBLEM_ROOT.parent.parent
if str(_IDEA_EVOLVE_ROOT) not in sys.path:
    sys.path.insert(0, str(_IDEA_EVOLVE_ROOT))

from problems._shared import eval_queue  # noqa: E402
from problems._shared.constants import (  # noqa: E402
    ENV_AGENT_NAME, ENV_ATTEMPT, ENV_PROBLEM, ENV_RUN_ROOT,
)

# Cache lives in the run directory (set by orchestrator via env var).
_RUN_ROOT = Path(os.environ[ENV_RUN_ROOT]) if ENV_RUN_ROOT in os.environ else None
CACHE_PATH = (_RUN_ROOT / "history" / "eval_cache.json") if _RUN_ROOT else Path("/tmp/idea_evolve_eval_cache.json")
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")

# Load validate.py from the problem directory
_validate_spec = importlib.util.spec_from_file_location("validate", PROBLEM_ROOT / "validate.py")
_validate_mod = importlib.util.module_from_spec(_validate_spec)
_validate_spec.loader.exec_module(_validate_mod)
validate = _validate_mod.validate


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache))


def _cached_lookup(content_hash: str) -> dict | None:
    """Thread-safe cache read."""
    CACHE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_LOCK_PATH, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH)
            cache = _load_cache()
            fcntl.flock(lock, fcntl.LOCK_UN)
        return cache.get(content_hash)
    except Exception:
        return None


def _cached_store(content_hash: str, result: dict):
    """Thread-safe cache write."""
    CACHE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_LOCK_PATH, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            cache = _load_cache()
            cache[content_hash] = result
            _save_cache(cache)
            fcntl.flock(lock, fcntl.LOCK_UN)
    except Exception:
        pass


def _file_hash(filepath: str) -> str:
    return hashlib.sha256(Path(filepath).read_bytes()).hexdigest()


def load_solution(filepath: str):
    """Dynamically load a solution module and call entrypoint()."""
    spec = importlib.util.spec_from_file_location("solution", filepath)
    module = importlib.util.module_from_spec(spec)
    if str(PROBLEM_ROOT) not in sys.path:
        sys.path.insert(0, str(PROBLEM_ROOT))
    spec.loader.exec_module(module)

    if not hasattr(module, "entrypoint"):
        raise ValueError(f"Solution {filepath} must implement def entrypoint()")

    return module.entrypoint()


def _write_score_sidecar(solution_path: str, result: dict):
    """Write .score sidecar file next to the solution."""
    try:
        score_path = Path(solution_path).with_suffix(".score")
        tmp_path = score_path.with_suffix(".score.tmp")
        tmp_path.write_text(json.dumps(result, indent=2))
        tmp_path.rename(score_path)
    except Exception:
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py <solution_file.py>")
        sys.exit(1)

    solution_path = sys.argv[1]

    try:
        content_hash = _file_hash(solution_path)
        cached = _cached_lookup(content_hash)
        if cached is not None:
            _write_score_sidecar(solution_path, cached)
            print(json.dumps(cached))
            return

        track_time = False
        metrics_path = PROBLEM_ROOT / "metrics.yaml"
        if metrics_path.exists():
            try:
                import yaml
                metrics = yaml.safe_load(metrics_path.read_text())
                track_time = metrics.get("track_eval_time", False)
            except Exception:
                pass

        # Queue visibility — sidon is parallel-safe, no kill-stale needed.
        queue_id = eval_queue.enqueue(
            os.environ.get(ENV_AGENT_NAME, "unknown"),
            os.environ.get(ENV_PROBLEM, "sidon"),
            os.environ.get(ENV_ATTEMPT, "unknown"),
            solution_path,
            status="running",
        )
        try:
            t0 = time.perf_counter()
            output = load_solution(solution_path)
            result = validate(output)
            elapsed = time.perf_counter() - t0
        finally:
            try:
                eval_queue.dequeue(queue_id)
            except Exception:
                pass

        if track_time:
            result["eval_time_s"] = round(elapsed, 4)

        _cached_store(content_hash, result)
        _write_score_sidecar(solution_path, result)
        print(json.dumps(result))
    except Exception as e:
        error_result = {
            "fitness": 0,
            "is_valid": 0,
            "violations": -1,
            "raw_size": 0,
            "error": str(e)[:500],
        }
        _write_score_sidecar(solution_path, error_result)
        print(json.dumps(error_result))
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
