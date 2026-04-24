#!/usr/bin/env python3
"""Evaluate a Megaminx solution.

Usage:
    python3 evaluate.py <solution_file.py>            # default: proxy (100 puzzles)
    python3 evaluate.py --full <solution_file.py>     # operator override: full 1001

The solution must implement `def entrypoint() -> dict[int, str]` returning
`{initial_state_id: dot_joined_path}`. A path of "" or a missing key counts as
unsolved (per-row sentinel).

Prints JSON with: fitness, is_valid, avg_path_length, solved_count,
expected_count, invalid_count, eval_time_s, eval_started_at, eval_ended_at.

Class A: local score == Kaggle score (no leaderboard submission needed).
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

from problems._shared import eval_queue, proc_log  # noqa: E402
from problems._shared.constants import (  # noqa: E402
    ENV_AGENT_NAME, ENV_ATTEMPT, ENV_PROBLEM, ENV_RUN_ROOT,
)
from problems._shared.eval_boilerplate import (  # noqa: E402
    try_diagnose_failure,
    try_kill_stale_same_agent,
)

_RUN_ROOT = Path(os.environ[ENV_RUN_ROOT]) if ENV_RUN_ROOT in os.environ else None
CACHE_PATH = (
    (_RUN_ROOT / "history" / "eval_cache.json")
    if _RUN_ROOT
    else Path("/tmp/idea_evolve_megaminx_cache.json")
)
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")

# Load validate.py from the problem dir
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


def _cached_lookup(key: str) -> dict | None:
    CACHE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_LOCK_PATH, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH)
            cache = _load_cache()
            fcntl.flock(lock, fcntl.LOCK_UN)
        return cache.get(key)
    except Exception:
        return None


def _cached_store(key: str, result: dict):
    CACHE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_LOCK_PATH, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            cache = _load_cache()
            cache[key] = result
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


def _load_solution(filepath: str):
    spec = importlib.util.spec_from_file_location("solution", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "entrypoint"):
        raise ValueError(f"Solution {filepath} must implement def entrypoint()")
    return module.entrypoint()


def _error_result(err: Exception, t0: float | None, started_at: str | None) -> dict:
    ended_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = {
        "fitness": 1_000_000_000,
        "is_valid": 0,
        "avg_path_length": 1_000_000,
        "solved_count": 0,
        "expected_count": 0,
        "invalid_count": 0,
        "error": str(err)[:500],
        "traceback": traceback.format_exc()[:4000],
    }
    if t0 is not None:
        out["eval_time_s"] = round(time.perf_counter() - t0, 4)
        out["eval_started_at"] = started_at
        out["eval_ended_at"] = ended_at
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("solution", help="Path to solution .py with entrypoint()")
    ap.add_argument(
        "--full",
        action="store_true",
        help="Operator override: score on the full 1001-puzzle test set (default: proxy 100).",
    )
    args = ap.parse_args()

    solution_path = args.solution
    started_at = None
    t0 = None
    queue_id = None

    try:
        # Pre-flight syntax check (cheap)
        v = validate(solution_path)
        if not v.get("is_valid"):
            v["fitness"] = 1_000_000_000
            v["is_valid"] = 0
            _write_score_sidecar(solution_path, v)
            print(json.dumps(v))
            return 1

        content_hash = _file_hash(solution_path)
        # Cache key includes mode so proxy/full results don't collide.
        # "proxy_strat" tag disambiguates from the old first-100 proxy in
        # case an older eval_cache.json is around.
        cache_key = f"{content_hash}:{'full' if args.full else 'proxy_strat'}"
        cached = _cached_lookup(cache_key)
        if cached is not None:
            _write_score_sidecar(solution_path, cached)
            print(json.dumps(cached))
            return 0

        # Same-agent kill contract: terminate any stale evaluate.py owned by
        # me before enqueueing. Megaminx runs parallel under MPS
        # (concurrency: 3); fails open if no matching process exists.
        try_kill_stale_same_agent(PROBLEM_ROOT)

        queue_id = eval_queue.enqueue(
            os.environ.get(ENV_AGENT_NAME, "unknown"),
            os.environ.get(ENV_PROBLEM, "megaminx"),
            os.environ.get(ENV_ATTEMPT, "unknown"),
            solution_path,
            status="running",
        )
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        t0 = time.perf_counter()

        predictions = _load_solution(solution_path)
        if not isinstance(predictions, dict):
            raise TypeError(
                f"entrypoint() must return dict[int, str], got {type(predictions).__name__}"
            )

        # Lazy-import scorer to keep the cache-hit path free of heavy imports.
        from helpers.core import score_predictions  # noqa: PLC0415

        fitness, is_valid, aux = score_predictions(predictions, proxy=not args.full)
        elapsed = time.perf_counter() - t0
        ended_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        result = {
            "fitness": fitness,
            "is_valid": is_valid,
            **aux,
            "eval_time_s": round(elapsed, 4),
            "eval_started_at": started_at,
            "eval_ended_at": ended_at,
        }

        _cached_store(cache_key, result)
        _write_score_sidecar(solution_path, result)
        print(json.dumps(result))
        return 0
    except Exception as e:
        result = _error_result(e, t0, started_at)
        # Agent-readable narrative failure log + problem-specific hint.
        if _RUN_ROOT is not None:
            try:
                fail_log = proc_log.Writer(
                    _RUN_ROOT,
                    os.environ.get(ENV_AGENT_NAME, "unknown"),
                    "eval_fail",
                    sticky=True,
                )
                fail_log.event(f"crashed on {Path(solution_path).name}")
                fail_log.kv(error_class=type(e).__name__, error_message=str(e)[:200])
                fail_log.traceback(e)
                hint = try_diagnose_failure(
                    PROBLEM_ROOT, type(e).__name__, str(e),
                    {"queue_at_failure": eval_queue.current_queue()},
                )
                if hint:
                    fail_log.hints(hint)
                fail_log.finalize("CRASHED", mark_sticky=True)
                result["log_path"] = fail_log.log_path
            except Exception:
                pass
        _write_score_sidecar(solution_path, result)
        print(json.dumps(result))
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    finally:
        if queue_id is not None:
            try:
                eval_queue.dequeue(queue_id)
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
