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
from datetime import datetime, timezone
from pathlib import Path

PROBLEM_ROOT = Path(__file__).parent
VENV_PYTHON = "/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python"

# Make `from problems._shared.X import Y` importable from this script
# regardless of cwd. PROBLEM_ROOT.parent == problems/, .parent.parent == idea-evolve/.
_IDEA_EVOLVE_ROOT = PROBLEM_ROOT.parent.parent
if str(_IDEA_EVOLVE_ROOT) not in sys.path:
    sys.path.insert(0, str(_IDEA_EVOLVE_ROOT))

from problems._shared import eval_queue, proc_log
from problems._shared.constants import (
    ENV_AGENT_NAME,
    ENV_ATTEMPT,
    ENV_PROBLEM,
    ENV_RUN_ROOT,
    GPU_LOCK_PATH as _GPU_LOCK_PATH_CONST,
)
from problems.strawberry import eval_hooks as _strawberry_hooks

# --- Cache setup ---
_RUN_ROOT = (
    Path(os.environ[ENV_RUN_ROOT])
    if ENV_RUN_ROOT in os.environ
    else None
)
CACHE_PATH = (
    (_RUN_ROOT / "history" / "eval_cache.json")
    if _RUN_ROOT
    else Path("/tmp/idea_evolve_strawberry_cache.json")
)
CACHE_LOCK_PATH = CACHE_PATH.with_suffix(".lock")

# --- GPU lock: serializes all training jobs system-wide.
#     Path is the canonical constant from problems/_shared/constants.py — never
#     hardcode the string elsewhere. ---
GPU_LOCK_PATH = Path(_GPU_LOCK_PATH_CONST)


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
    Exclusive file lock on GPU_LOCK_PATH (see problems/_shared/constants.py).
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


def _error_result(msg: str, tb: str | None = None) -> dict:
    return {
        "fitness": 0,
        "is_valid": 0,
        "mAP50": 0,
        "mAP50_95": 0,
        "F1": 0,
        "error": msg[:500],
        "traceback": (tb or "")[:4000],
    }


# Well-known training artifact dir written by train_and_eval (helpers.core).
# Overwritten every eval — we snapshot it next to the failing solution on error.
TRAIN_LOG_DIR = Path("/tmp/idea_evolve_strawberry/last_train_logs")


def _snapshot_crash_artifacts(solution_path: str):
    """
    On error, copy /tmp/.../last_train_logs/* next to the solution file as
    <solution_stem>_crash_logs/. Persists per-solution so future agents can
    read WHY their ancestor failed — the /tmp dir gets overwritten by the
    next training run otherwise.
    """
    import shutil
    try:
        if not TRAIN_LOG_DIR.exists():
            return
        sol = Path(solution_path)
        dest = sol.parent / f"{sol.stem}_crash_logs"
        dest.mkdir(parents=True, exist_ok=True)
        for src in TRAIN_LOG_DIR.iterdir():
            if src.is_file():
                try:
                    shutil.copy2(src, dest / src.name)
                except Exception:
                    pass
    except Exception:
        pass


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

_METRICS_PATH = PROBLEM_ROOT / "metrics.yaml"


def _read_metrics_field(key: str, default):
    """Tiny YAML reader — top-level scalar fields only. Avoids a yaml dep."""
    try:
        for line in _METRICS_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{key}:"):
                _, _, val = line.partition(":")
                val = val.strip().split("#", 1)[0].strip()
                if val.lower() in ("true", "false"):
                    return val.lower() == "true"
                try:
                    return int(val)
                except ValueError:
                    return val
    except OSError:
        pass
    return default


def _archive_enabled() -> bool:
    return bool(_read_metrics_field("archive_checkpoints", False))


def _checkpoint_retention() -> int:
    return int(_read_metrics_field("checkpoint_retention", 50))


def _agent_identity() -> tuple[str, str, str]:
    """Read identity env vars injected by the orchestrator harness."""
    return (
        os.environ.get(ENV_AGENT_NAME, "unknown"),
        os.environ.get(ENV_PROBLEM, "strawberry"),
        os.environ.get(ENV_ATTEMPT, "unknown"),
    )


def _reproduce_mode(content_hash: str) -> int:
    """Replay `evaluate_from_checkpoint` for an archived best.pt."""
    if _RUN_ROOT is None:
        print(f"ERROR: --reproduce requires {ENV_RUN_ROOT} to be set", file=sys.stderr)
        return 1
    # Re-exec into the venv if needed so ultralytics is importable.
    if os.environ.get("_STRAWBERRY_IN_VENV") != "1":
        try:
            import importlib as _il
            _has = _il.util.find_spec("ultralytics") is not None
        except Exception:
            _has = False
        if not _has:
            env = os.environ.copy()
            env["_STRAWBERRY_IN_VENV"] = "1"
            os.execve(VENV_PYTHON, [VENV_PYTHON] + sys.argv, env)
    if str(PROBLEM_ROOT) not in sys.path:
        sys.path.insert(0, str(PROBLEM_ROOT))
    from helpers.core import evaluate_from_checkpoint  # type: ignore
    metrics = evaluate_from_checkpoint(content_hash, _RUN_ROOT)
    print(json.dumps(metrics, indent=2))
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py <solution_file.py>")
        print("       python3 evaluate.py --reproduce <content_hash>")
        sys.exit(1)

    if sys.argv[1] == "--reproduce" and len(sys.argv) >= 3:
        sys.exit(_reproduce_mode(sys.argv[2]))

    solution_path = sys.argv[1]
    agent_name, problem, attempt = _agent_identity()

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
        #    pgroup reliably catches the training process. The IDEA_EVOLVE_*
        #    identity env vars are preserved through execve so the queue/kill
        #    contract survives the re-exec.
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

        # 4. Same-agent kill contract: terminate any stale evaluate.py owned by
        #    me before I take the GPU. Defensive — never raises into the caller.
        kill_actions = eval_queue.kill_stale_same_agent(
            agent_name,
            kill_hook=_strawberry_hooks.kill_eval,
            log_event=lambda s: print(f"[evaluate.py][kill] {s}", file=sys.stderr, flush=True),
        )

        # 5. Set up narrative log + queue entry. Both are best-effort; if RUN_ROOT
        #    is missing (manual invocation) we just skip the log.
        log_writer = None
        if _RUN_ROOT is not None:
            try:
                log_writer = proc_log.Writer(_RUN_ROOT, agent_name, "eval", sticky=False)
                log_writer.event(f"started for {Path(solution_path).name} (hash {content_hash[:12]})")
                if kill_actions:
                    log_writer.section(
                        "Predecessor kill",
                        "\n".join(f"- {a}" for a in kill_actions),
                    )
            except Exception as exc:
                print(f"[evaluate.py] proc_log init failed: {exc!r}", file=sys.stderr)

        queue_id = eval_queue.enqueue(
            agent_name, problem, attempt, solution_path, status="waiting",
        )
        try:
            # 6. Load and validate module (syntax check, entrypoint exists)
            module, err = _load_and_validate_solution(solution_path)
            if err is not None:
                _cached_store(content_hash, err)
                _write_score_sidecar(solution_path, err)
                print(json.dumps(err))
                if log_writer is not None:
                    log_writer.section("Error", err.get("error", "load failed"))
                    log_writer.hints(_strawberry_hooks.diagnose_failure(
                        "ImportError", err.get("error", ""),
                        {"queue_at_failure": eval_queue.current_queue()},
                    ))
                    log_writer.finalize("LOAD_FAILED", mark_sticky=True)
                return

            # 7. Acquire GPU lock → mark running → call entrypoint() → release GPU lock
            t0 = time.perf_counter()
            started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with _gpu_lock():
                eval_queue.mark_running(queue_id)
                if log_writer is not None:
                    log_writer.event("GPU lock acquired, training starting")
                raw_result = module.entrypoint()
            elapsed = time.perf_counter() - t0
            ended_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

            # 8. Validate and package the result
            result = _process_entrypoint_result(raw_result)
            result["eval_time_s"] = round(elapsed, 1)
            result["eval_started_at"] = started_at
            result["eval_ended_at"] = ended_at
            if log_writer is not None:
                result["log_path"] = log_writer.log_path

            # 8a. Archive best.pt for `--reproduce <hash>` if metrics.yaml says to.
            #     Driven by the archive_checkpoints flag — read fresh each call so
            #     a config change takes effect without restarting the orchestrator.
            try:
                if _RUN_ROOT is not None and _archive_enabled():
                    if str(PROBLEM_ROOT) not in sys.path:
                        sys.path.insert(0, str(PROBLEM_ROOT))
                    from helpers.core import archive_checkpoint  # type: ignore
                    archived = archive_checkpoint(
                        content_hash, _RUN_ROOT,
                        retention=_checkpoint_retention(),
                    )
                    if archived and log_writer is not None:
                        log_writer.event(f"archived checkpoint to {archived}")
            except Exception as exc:
                if log_writer is not None:
                    log_writer.event(f"checkpoint archive failed: {exc!r}")

            # 9. Cache + sidecar + print
            _cached_store(content_hash, result)
            _write_score_sidecar(solution_path, result)
            print(json.dumps(result))

            if log_writer is not None:
                log_writer.event(f"completed: fitness={result['fitness']}")
                log_writer.finalize("OK")
        finally:
            try:
                eval_queue.dequeue(queue_id)
            except Exception:
                pass

    except Exception as e:
        tb = traceback.format_exc()
        ended_at_err = datetime.now(timezone.utc).isoformat(timespec="seconds")
        error_result = _error_result(str(e), tb=tb)
        try:
            error_result["eval_time_s"] = round(time.perf_counter() - t0, 1)
            error_result["eval_started_at"] = started_at
            error_result["eval_ended_at"] = ended_at_err
        except NameError:
            pass  # error before GPU lock / measurement began
        _snapshot_crash_artifacts(solution_path)
        # Failure log — diagnose with strawberry-specific hints, mark sticky.
        try:
            if _RUN_ROOT is not None:
                fail_log = proc_log.Writer(_RUN_ROOT, agent_name, "eval_fail", sticky=True)
                fail_log.event(f"crashed on {Path(solution_path).name}")
                fail_log.kv(error_class=type(e).__name__, error_message=str(e)[:200])
                fail_log.traceback(e)
                fail_log.hints(_strawberry_hooks.diagnose_failure(
                    type(e).__name__, str(e),
                    {"queue_at_failure": eval_queue.current_queue()},
                ))
                fail_log.finalize("CRASHED", mark_sticky=True)
                error_result["log_path"] = fail_log.log_path
        except Exception:
            pass
        _write_score_sidecar(solution_path, error_result)
        print(json.dumps(error_result))
        print(f"ERROR: {e}", file=sys.stderr)
        print(tb, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
