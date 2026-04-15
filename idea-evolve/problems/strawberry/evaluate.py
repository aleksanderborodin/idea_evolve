#!/usr/bin/env python3
"""
Evaluate a solution for the Strawberry Disease Segmentation problem.

Usage: python3 evaluate.py <solution_file.py>

The solution file must implement def entrypoint() which does its own YOLO training
and returns a metrics dict: {"mAP50": float, "mAP50_95": float, ...}

evaluate.py handles:
  - Caching by content hash (identical solutions return instantly)
  - GPU file lock (serializes all training — safe even with parallel agents)
  - Re-exec into the first_project venv (provides ultralytics)
  - Fitness extraction: fitness = result["mAP50"]

Prints JSON with {fitness, is_valid, mAP50, mAP50_95, F1, ...} fields.
"""

import contextlib
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
VENV_PYTHON = "/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python"

# --- Cache setup ---
_RUN_ROOT = (
    Path(os.environ["IDEA_EVOLVE_RUN_ROOT"])
    if "IDEA_EVOLVE_RUN_ROOT" in os.environ
    else None
)
CACHE_PATH = (
    (_RUN_ROOT / "history" / "eval_cache.json")
    if _RUN_ROOT
    else Path("/tmp/idea_evolve_strawberry_cache.json")
)
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")

# --- GPU lock: serializes all training jobs system-wide ---
GPU_LOCK_PATH = Path("/tmp/idea_evolve_gpu.lock")


# ── Cache helpers ──────────────────────────────────────────────────────────────

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


# ── GPU lock context manager ───────────────────────────────────────────────────

@contextlib.contextmanager
def _gpu_lock():
    """
    Exclusive file lock on /tmp/idea_evolve_gpu.lock.
    Blocks until the GPU is free. Works across all processes on this machine.
    This means parallel agents automatically queue — no orchestrator changes needed.
    """
    GPU_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_file = open(GPU_LOCK_PATH, "w")
    try:
        print("[evaluate.py] Waiting for GPU lock...", file=sys.stderr, flush=True)
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        print("[evaluate.py] GPU acquired — starting training.", file=sys.stderr, flush=True)
        yield
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        print("[evaluate.py] GPU lock released.", file=sys.stderr, flush=True)


# ── Solution loading and validation ───────────────────────────────────────────

def _load_and_validate_solution(filepath: str):
    """
    Load solution module and return (module, error_result).
    error_result is None if OK, or a dict if the module failed to load.
    """
    try:
        spec = importlib.util.spec_from_file_location("solution", filepath)
        module = importlib.util.module_from_spec(spec)
        # Add problem root and helpers to path so 'from helpers.core import ...' works
        if str(PROBLEM_ROOT) not in sys.path:
            sys.path.insert(0, str(PROBLEM_ROOT))
        spec.loader.exec_module(module)
    except SyntaxError as e:
        return None, _error_result(f"SyntaxError in solution: {e}")
    except Exception as e:
        return None, _error_result(f"Failed to load solution: {e}")

    if not hasattr(module, "entrypoint") or not callable(module.entrypoint):
        return None, _error_result("Solution must implement def entrypoint()")

    return module, None


def _error_result(msg: str) -> dict:
    return {
        "fitness": 0,
        "is_valid": 0,
        "mAP50": 0,
        "mAP50_95": 0,
        "F1": 0,
        "error": msg[:500],
    }


def _process_entrypoint_result(raw: object) -> dict:
    """
    Validate the dict returned by entrypoint() and produce the final result.
    fitness = raw["mAP50"]
    """
    if not isinstance(raw, dict):
        raise ValueError(
            f"entrypoint() must return a dict, got {type(raw).__name__}"
        )

    required_keys = ("mAP50",)
    for key in required_keys:
        if key not in raw:
            raise ValueError(f"entrypoint() result missing required key: '{key}'")

    map50 = float(raw["mAP50"])
    if not (0.0 <= map50 <= 1.0):
        raise ValueError(f"mAP50={map50} out of range [0, 1]")

    result = {
        "fitness": round(map50, 4),
        "is_valid": 1,
        "mAP50": round(map50, 4),
        "mAP50_95": round(float(raw.get("mAP50_95", 0)), 4),
        "F1": round(float(raw.get("F1", 0)), 4),
        "precision": round(float(raw.get("precision", 0)), 4),
        "recall": round(float(raw.get("recall", 0)), 4),
    }
    # Pass through auxiliary metrics (REC-2: per-class + TTA flag + train time).
    # These don't affect fitness — they're stored so agents can inspect what
    # the model is doing per-class without re-running evaluation.
    for key in ("per_class", "tta", "train_time_s"):
        if key in raw:
            result[key] = raw[key]
    return result


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py <solution_file.py>")
        sys.exit(1)

    solution_path = sys.argv[1]

    try:
        # 1. Fast-path: cache check (no GPU needed, works in any Python)
        content_hash = _file_hash(solution_path)
        cached = _cached_lookup(content_hash)
        if cached is not None:
            _write_score_sidecar(solution_path, cached)
            print(json.dumps(cached))
            return

        # 2. Re-exec in first_project venv if ultralytics is not available.
        #    Uses os.execve to REPLACE this process (not spawn a child), so the
        #    caller's process tree has no grandchild layer — timeout-kill via
        #    pgroup reliably catches the training process.
        if os.environ.get("_STRAWBERRY_IN_VENV") != "1":
            _has = False
            try:
                import importlib as _il
                _has = _il.util.find_spec("ultralytics") is not None
            except Exception:
                pass
            if not _has:
                env = os.environ.copy()
                env["_STRAWBERRY_IN_VENV"] = "1"
                os.execve(VENV_PYTHON, [VENV_PYTHON] + sys.argv, env)

        # 3. (In the right venv now) Check cache once more (race guard)
        cached = _cached_lookup(content_hash)
        if cached is not None:
            _write_score_sidecar(solution_path, cached)
            print(json.dumps(cached))
            return

        # 4. Load and validate module (syntax check, entrypoint exists)
        module, err = _load_and_validate_solution(solution_path)
        if err is not None:
            _cached_store(content_hash, err)
            _write_score_sidecar(solution_path, err)
            print(json.dumps(err))
            return

        # 5. Acquire GPU lock → call entrypoint() → release GPU lock
        t0 = time.perf_counter()
        with _gpu_lock():
            raw_result = module.entrypoint()
        elapsed = time.perf_counter() - t0

        # 6. Validate and package the result
        result = _process_entrypoint_result(raw_result)
        result["eval_time_s"] = round(elapsed, 1)

        # 7. Cache + sidecar + print
        _cached_store(content_hash, result)
        _write_score_sidecar(solution_path, result)
        print(json.dumps(result))

    except Exception as e:
        error_result = _error_result(str(e))
        _write_score_sidecar(solution_path, error_result)
        print(json.dumps(error_result))
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
