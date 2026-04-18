"""Strawberry-specific eval hooks: GPU-aware kill + failure diagnosis.

The default kill hook in problems/_shared/eval_hooks_default.py just SIGTERM/
SIGKILLs the process group. That isn't enough for a GPU-bound training:

- An ultralytics DataLoader worker can hold the GPU lock for a few seconds
  after SIGKILL while CUDA frees memory.
- A new evaluate.py launching immediately can find the GPU lock free but the
  GPU itself OOM-fragmented.

So this hook does the killpg dance, then *verifies* the gpu lock has been
released before returning, using lock-acquisition (more reliable than lsof)
via problems/_shared/eval_queue.verify_lock_released. Every step is logged
to /tmp/idea_evolve_strawberry/kill_log.json so the next failure is debuggable.
"""

from __future__ import annotations

import json
import os
import signal
import time
from pathlib import Path

from problems._shared.constants import (
    GPU_LOCK_PATH,
    KILL_DEADLINE_SECONDS,
    KILL_GRACE_SECONDS,
)
from problems._shared.eval_queue import verify_lock_released

KILL_LOG_PATH = Path("/tmp/idea_evolve_strawberry/kill_log.json")


def _log_step(record: dict) -> None:
    try:
        KILL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        record["ts"] = time.time()
        with open(KILL_LOG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def kill_eval(pid: int, pgid: int, solution_path: str) -> None:
    """Terminate a stale strawberry evaluation cleanly.

    Sequence:
      1. SIGTERM pgid (gives YOLO/ultralytics a chance to flush)
      2. wait KILL_GRACE_SECONDS
      3. SIGKILL pgid (definitive)
      4. verify GPU lock released (lock-acquisition, not lsof)
      5. log every step
    """
    _log_step({"action": "kill_start", "pid": pid, "pgid": pgid, "solution": solution_path})
    try:
        os.killpg(pgid, signal.SIGTERM)
        _log_step({"action": "sigterm_sent", "pgid": pgid})
    except ProcessLookupError:
        _log_step({"action": "already_dead", "pid": pid})
        return
    except OSError as e:
        _log_step({"action": "sigterm_failed", "pgid": pgid, "error": str(e)})
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return

    time.sleep(KILL_GRACE_SECONDS)

    try:
        os.killpg(pgid, signal.SIGKILL)
        _log_step({"action": "sigkill_sent", "pgid": pgid})
    except ProcessLookupError:
        pass
    except OSError as e:
        _log_step({"action": "sigkill_failed", "pgid": pgid, "error": str(e)})

    # Lock-acquisition verification — more reliable than lsof. If the killed
    # process actually held GPU_LOCK_PATH, we should be able to grab it now.
    released = verify_lock_released(str(GPU_LOCK_PATH), deadline_s=KILL_DEADLINE_SECONDS)
    _log_step({"action": "gpu_lock_released", "released": released, "deadline_s": KILL_DEADLINE_SECONDS})


def diagnose_failure(error_class: str, error_message: str, context: dict) -> str:
    """Return strawberry-specific markdown hints for a failed evaluation."""
    hints: list[str] = []
    msg = (error_message or "").lower()
    queue_at_failure = context.get("queue_at_failure") or []
    concurrent = [
        e for e in queue_at_failure
        if e.get("status") == "running" and e.get("problem") == "strawberry"
    ]

    if "broken pipe" in msg:
        hints.append(
            "- **Broken pipe during YOLO training is almost always concurrent GPU access.** "
            f"At failure time there were {len(concurrent)} concurrent strawberry evaluations "
            "marked `running` in the queue. The expected count is 1 (this one). "
            "Check `metrics.yaml` — `concurrency: 1` MUST be set, and the architect "
            "MUST place strawberry agents in single-element parallel_groups so they run "
            "one at a time."
        )
    if "out of memory" in msg or "cuda out of memory" in msg or "cuda oom" in msg:
        hints.append(
            "- **CUDA OOM.** Reduce `batch` first (cheapest reversible knob — try halving). "
            "Reducing `imgsz` is the next lever. Switching to a smaller model variant "
            "(e.g. yolo11s → yolo11n) is a much bigger commitment — only do it if "
            "smaller batch+imgsz still OOMs. Check `last_train_logs/args.yaml` to see "
            "what the previous run used."
        )
    if "timeout" in msg or "timed out" in msg:
        hints.append(
            "- **Eval timed out.** `epochs * time_per_epoch` exceeded the session budget. "
            "Per-epoch time is in `last_train_logs/results.csv`. Reduce epochs to fit, "
            "or pick a smaller model variant. Do NOT just raise the timeout — the budget "
            "exists so the orchestrator can keep moving."
        )
    if error_class in ("FileNotFoundError", "ModuleNotFoundError"):
        hints.append(
            "- **Missing file/module.** Likely a path that doesn't exist in first_project's "
            "venv, or an import that needs `from helpers.core import ...` but used a flat "
            "import. See `helpers/README.md` for the canonical helper layout."
        )
    if "killed" in msg or error_class == "ProcessKilled":
        hints.append(
            "- **Killed by same-agent contract.** A newer evaluate.py from the same agent "
            "started before this one finished. The kill was deliberate. Read this log's "
            "Timeline section for the exact pid that killed you. Do NOT retry sol01.py — "
            "you abandoned it on purpose by launching sol02.py. Move on to the next idea."
        )
    if not hints:
        hints.append(
            "- No strawberry-specific hint matched. Check the timeline above, then look "
            "at `/tmp/idea_evolve_strawberry/last_train_logs/` for partial training output. "
            "If this is a brand new failure mode, extend "
            "`problems/strawberry/eval_hooks.py:diagnose_failure()` so future agents get help."
        )
    return "\n".join(hints)
