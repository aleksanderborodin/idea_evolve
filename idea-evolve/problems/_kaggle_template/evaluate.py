#!/usr/bin/env python3
"""SKELETON evaluator for a Kaggle-as-idea-evolve problem.

This is a CPU-only, parallel-safe shell. To turn it into a real evaluator:

1. Replace the `# TODO` block in main() with calls to your `helpers.core`
   loader and scorer.
2. Update the error-result dict shape to match your `metrics.yaml` schema.

Usage: python3 evaluate.py <solution_file.py> [--full]

The solution must implement `def entrypoint()` returning a dict in whatever
shape `helpers.core.score_predictions()` expects.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROBLEM_ROOT = Path(__file__).parent
_IDEA_EVOLVE_ROOT = PROBLEM_ROOT.parent.parent
if str(_IDEA_EVOLVE_ROOT) not in sys.path:
    sys.path.insert(0, str(_IDEA_EVOLVE_ROOT))
if str(PROBLEM_ROOT) not in sys.path:
    sys.path.insert(0, str(PROBLEM_ROOT))

from problems._shared import eval_queue  # noqa: E402
from problems._shared.constants import (  # noqa: E402
    ENV_AGENT_NAME, ENV_ATTEMPT, ENV_PROBLEM, ENV_RUN_ROOT,
)

_RUN_ROOT = Path(os.environ[ENV_RUN_ROOT]) if ENV_RUN_ROOT in os.environ else None
CACHE_PATH = (
    (_RUN_ROOT / "history" / "eval_cache.json")
    if _RUN_ROOT
    else Path("/tmp/idea_evolve_kaggle_template_cache.json")
)
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")


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


def _write_score_sidecar(solution_path: str, result: dict):
    try:
        score_path = Path(solution_path).with_suffix(".score")
        tmp_path = score_path.with_suffix(".score.tmp")
        tmp_path.write_text(json.dumps(result, indent=2))
        tmp_path.rename(score_path)
    except Exception:
        pass


def load_solution(filepath: str):
    spec = importlib.util.spec_from_file_location("solution", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "entrypoint"):
        raise ValueError(f"Solution {filepath} must implement def entrypoint()")
    return module.entrypoint()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("solution", help="Path to solution .py with entrypoint()")
    ap.add_argument(
        "--full",
        action="store_true",
        help="Operator-only override: re-score on the full test set (ignored by agents).",
    )
    args = ap.parse_args()

    solution_path = args.solution
    started_at = None
    t0 = None
    try:
        content_hash = _file_hash(solution_path)
        # Cache key incorporates the --full override so proxy/full results don't collide.
        cache_key = f"{content_hash}:{'full' if args.full else 'proxy'}"
        cached = _cached_lookup(cache_key)
        if cached is not None:
            _write_score_sidecar(solution_path, cached)
            print(json.dumps(cached))
            return

        queue_id = eval_queue.enqueue(
            os.environ.get(ENV_AGENT_NAME, "unknown"),
            os.environ.get(ENV_PROBLEM, "kaggle_template"),
            os.environ.get(ENV_ATTEMPT, "unknown"),
            solution_path,
            status="running",
        )
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        t0 = time.perf_counter()
        try:
            predictions = load_solution(solution_path)
            # TODO: replace with real scorer.
            # Example:
            #   from helpers.core import score_predictions
            #   fitness, is_valid, aux = score_predictions(predictions, full=args.full)
            #   result = {"fitness": fitness, "is_valid": is_valid, **aux}
            raise NotImplementedError(
                "Skeleton evaluate.py — replace this block with your scoring logic."
            )
            elapsed = time.perf_counter() - t0
            ended_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        finally:
            try:
                eval_queue.dequeue(queue_id)
            except Exception:
                pass

        result["eval_time_s"] = round(elapsed, 4)  # noqa: F821 — example block
        result["eval_started_at"] = started_at
        result["eval_ended_at"] = ended_at

        _cached_store(cache_key, result)
        _write_score_sidecar(solution_path, result)
        print(json.dumps(result))
    except Exception as e:
        ended_at_err = datetime.now(timezone.utc).isoformat(timespec="seconds")
        error_result = {
            "fitness": 0,
            "is_valid": 0,
            "error": str(e)[:500],
            "traceback": traceback.format_exc()[:4000],
        }
        if t0 is not None:
            error_result["eval_time_s"] = round(time.perf_counter() - t0, 4)
            error_result["eval_started_at"] = started_at
            error_result["eval_ended_at"] = ended_at_err
        _write_score_sidecar(solution_path, error_result)
        print(json.dumps(error_result))
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
