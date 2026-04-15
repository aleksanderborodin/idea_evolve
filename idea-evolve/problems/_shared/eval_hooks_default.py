"""Default evaluation kill hook + failure-diagnosis hint generator.

Used by problems that don't define their own problems/<id>/eval_hooks.py.
GPU/special-resource problems should override these.
"""

from __future__ import annotations

import os
import signal
import time

from .constants import KILL_GRACE_SECONDS


def kill_eval(pid: int, pgid: int, solution_path: str) -> None:
    """Kill a stale evaluate.py process group cleanly.

    Default: SIGTERM the process group, wait KILL_GRACE_SECONDS, then SIGKILL.
    Process-group based — works because every evaluate.py is launched with
    start_new_session=True (or as the orchestrator's child with the same).
    """
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        # Fall back to per-pid signal.
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return
    time.sleep(KILL_GRACE_SECONDS)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            return


def diagnose_failure(error_class: str, error_message: str, context: dict) -> str:
    """Return markdown-formatted hints for an agent reading a failure log.

    `context` may contain: queue_at_failure (list), elapsed_s, problem, etc.
    Override per problem to give task-specific advice.
    """
    hints: list[str] = []
    msg = (error_message or "").lower()
    if "broken pipe" in msg:
        hints.append(
            "- Broken pipe usually means another process disrupted shared resources "
            "(GPU context, file handles). Check `current_queue()` for concurrent "
            "`running` entries at the time of failure. If the problem is GPU-bound, "
            "verify metrics.yaml has `concurrency: serial`."
        )
    if "out of memory" in msg or "oom" in msg or "cuda out of memory" in msg:
        hints.append(
            "- Out-of-memory: reduce batch size first (cheapest reversible knob). "
            "Reducing model size is a much bigger commitment."
        )
    if "timeout" in msg or "timed out" in msg:
        hints.append(
            "- Timeout: total epochs * time-per-epoch exceeded the session budget. "
            "Reduce epochs or pick a smaller model variant."
        )
    if error_class in ("FileNotFoundError", "ModuleNotFoundError"):
        hints.append(
            "- Missing file/module: check `problem/helpers/README.md` for the right "
            "import paths and required artifacts."
        )
    if not hints:
        hints.append(
            "- No specific hint matched. Read the timeline above and the traceback. "
            "If this is a fresh failure mode, consider extending "
            "`problems/<id>/eval_hooks.py:diagnose_failure()` so future agents get help."
        )
    return "\n".join(hints)
