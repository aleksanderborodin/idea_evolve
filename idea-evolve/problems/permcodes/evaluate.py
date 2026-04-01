#!/usr/bin/env python3
"""
Evaluate a solution for the current problem.

Usage: python3 evaluate.py <solution_file.py>

The solution file must implement def entrypoint() that returns the expected output.
Prints JSON with at minimum {fitness, is_valid} fields.

Problem-agnostic: reads validate.py from the same directory as this script.
Caches results by file content hash for speed.
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

# Cache lives in the run directory (set by orchestrator via env var).
_RUN_ROOT = Path(os.environ["IDEA_EVOLVE_RUN_ROOT"]) if "IDEA_EVOLVE_RUN_ROOT" in os.environ else None
CACHE_PATH = (_RUN_ROOT / "history" / "eval_cache.json") if _RUN_ROOT else Path("/tmp/idea_evolve_eval_cache.json")
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")

# Load validate.py from the problem directory (problem-agnostic)
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
    # Add problem dir to sys.path so solutions can import from helpers/ (e.g. helpers.core)
    if str(PROBLEM_ROOT) not in sys.path:
        sys.path.insert(0, str(PROBLEM_ROOT))
    spec.loader.exec_module(module)

    if not hasattr(module, "entrypoint"):
        raise ValueError(f"Solution {filepath} must implement def entrypoint()")

    return module.entrypoint()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py <solution_file.py>")
        sys.exit(1)

    solution_path = sys.argv[1]

    try:
        # Check cache first (thread-safe)
        content_hash = _file_hash(solution_path)
        cached = _cached_lookup(content_hash)
        if cached is not None:
            print(json.dumps(cached))
            return

        # Check if time tracking is enabled
        track_time = False
        metrics_path = PROBLEM_ROOT / "metrics.yaml"
        if metrics_path.exists():
            try:
                import yaml
                metrics = yaml.safe_load(metrics_path.read_text())
                track_time = metrics.get("track_eval_time", False)
            except Exception:
                pass

        t0 = time.perf_counter()
        output = load_solution(solution_path)
        result = validate(output)
        elapsed = time.perf_counter() - t0

        if track_time:
            result["eval_time_s"] = round(elapsed, 4)

        # Cache the result (thread-safe) — stores eval_time_s too
        _cached_store(content_hash, result)

        print(json.dumps(result))
    except Exception as e:
        # Build error result with sentinel values for all metrics
        error_result = {"error": str(e)}
        metrics_path = PROBLEM_ROOT / "metrics.yaml"
        if metrics_path.exists():
            try:
                import yaml
                data = yaml.safe_load(metrics_path.read_text())
                for name, spec in data.get("specs", {}).items():
                    error_result[name] = spec.get("sentinel_value", 0)
            except Exception:
                error_result["fitness"] = 1e9
                error_result["is_valid"] = 0
        else:
            error_result["fitness"] = 1e9
            error_result["is_valid"] = 0
        print(json.dumps(error_result))
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
