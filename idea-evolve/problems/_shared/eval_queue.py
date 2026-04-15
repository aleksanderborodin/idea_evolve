"""Universal evaluation queue + same-agent kill-on-new-solution contract.

Single JSON file at constants.EVAL_QUEUE_PATH lists every active evaluate.py
invocation across all problems and attempts. Used for:

  1. Dashboard visibility (who's running, who's waiting).
  2. The "new solution kills old" contract: when an evaluate.py starts, it
     kills any still-running evaluation owned by the same agent_name (peer-
     mediated, no orchestrator coordination required).

Safety: every kill goes through 8 invariant checks (see _is_safe_to_kill)
before any signal is sent. If any check fails, we fail OPEN (skip the kill,
queue normally) — never kill the wrong process.

Concurrency: per-agent fcntl lock prevents two new evals from racing to
kill each other. Queue file writes use exclusive flock.
"""

from __future__ import annotations

import atexit
import errno
import fcntl
import json
import os
import signal
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Optional

from .constants import (
    AGENT_KILL_LOCK_TEMPLATE,
    EVAL_QUEUE_PATH,
    KILL_DEADLINE_SECONDS,
    KILL_GRACE_SECONDS,
)


# ============================================================================
# Queue file primitives
# ============================================================================

@contextmanager
def _queue_lock():
    """Exclusive lock around the queue file. Creates the file if missing."""
    Path(EVAL_QUEUE_PATH).touch(exist_ok=True)
    fd = os.open(EVAL_QUEUE_PATH, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield fd
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(fd)


def _read_queue(fd: int) -> list[dict]:
    os.lseek(fd, 0, os.SEEK_SET)
    raw = os.read(fd, 1 << 24).decode("utf-8") or "[]"
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        # Corrupt queue file: treat as empty (fail-open). Caller should log.
        return []


def _write_queue(fd: int, entries: list[dict]) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    payload = json.dumps(entries, indent=2).encode("utf-8")
    os.write(fd, payload)
    os.fsync(fd)


def current_queue() -> list[dict]:
    """Read the queue (no lock — eventually consistent)."""
    p = Path(EVAL_QUEUE_PATH)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text() or "[]")
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


# ============================================================================
# Enqueue / dequeue
# ============================================================================

def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists but owned by other user


def gc_stale_entries() -> int:
    """Remove queue entries whose pid is no longer alive. Returns count removed."""
    removed = 0
    with _queue_lock() as fd:
        entries = _read_queue(fd)
        live = [e for e in entries if _alive(int(e.get("pid", 0)))]
        removed = len(entries) - len(live)
        if removed:
            _write_queue(fd, live)
    return removed


def enqueue(
    agent_name: str,
    problem: str,
    attempt: str,
    solution_path: str,
    status: str = "waiting",
) -> str:
    """Append a queue entry for this process. Returns queue_id."""
    queue_id = uuid.uuid4().hex[:12]
    pid = os.getpid()
    try:
        pgid = os.getpgid(pid)
    except OSError:
        pgid = pid
    entry = {
        "queue_id": queue_id,
        "pid": pid,
        "pgid": pgid,
        "agent_name": agent_name or "unknown",
        "problem": problem,
        "attempt": attempt,
        "solution_path": str(solution_path),
        "started_at": time.time(),
        "status": status,
    }
    with _queue_lock() as fd:
        entries = _read_queue(fd)
        # GC stale on every enqueue (cheap).
        entries = [e for e in entries if _alive(int(e.get("pid", 0)))]
        entries.append(entry)
        _write_queue(fd, entries)
    atexit.register(_dequeue_safe, queue_id)
    return queue_id


def mark_running(queue_id: str) -> None:
    with _queue_lock() as fd:
        entries = _read_queue(fd)
        for e in entries:
            if e.get("queue_id") == queue_id:
                e["status"] = "running"
                e["running_at"] = time.time()
        _write_queue(fd, entries)


def dequeue(queue_id: str) -> None:
    with _queue_lock() as fd:
        entries = _read_queue(fd)
        entries = [e for e in entries if e.get("queue_id") != queue_id]
        _write_queue(fd, entries)


def _dequeue_safe(queue_id: str) -> None:
    try:
        dequeue(queue_id)
    except Exception:
        pass


# ============================================================================
# Same-agent kill contract — DEFENSIVE
# ============================================================================

@contextmanager
def _agent_kill_lock(agent_name: str):
    """Per-agent mutex around the kill-then-enqueue sequence."""
    path = AGENT_KILL_LOCK_TEMPLATE.format(name=agent_name or "unknown")
    Path(path).touch(exist_ok=True)
    fd = os.open(path, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(fd)


def _read_proc_cmdline(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().decode("utf-8", errors="replace").replace("\0", " ")
    except (OSError, ValueError):
        return ""


def _read_proc_environ(pid: int) -> dict[str, str]:
    try:
        with open(f"/proc/{pid}/environ", "rb") as f:
            raw = f.read().decode("utf-8", errors="replace")
        env = {}
        for kv in raw.split("\0"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                env[k] = v
        return env
    except (OSError, ValueError):
        return {}


def _is_safe_to_kill(entry: dict, my_pid: int, my_agent: str) -> tuple[bool, str]:
    """8-check invariant gate. Returns (ok, reason_if_not)."""
    target_pid = int(entry.get("pid", 0))
    target_pgid = int(entry.get("pgid", 0))
    target_agent = entry.get("agent_name", "")

    if target_agent != my_agent:
        return False, f"agent mismatch ({target_agent} != {my_agent})"
    if target_pid == my_pid:
        return False, "target is self"
    if target_pid <= 0:
        return False, f"invalid pid {target_pid}"
    if not _alive(target_pid):
        return False, "target already dead"
    try:
        actual_pgid = os.getpgid(target_pid)
    except OSError:
        return False, "cannot read pgid (process gone)"
    if actual_pgid != target_pgid:
        return False, f"pgid drift ({actual_pgid} != {target_pgid}) — pid reused"
    cmdline = _read_proc_cmdline(target_pid)
    if "evaluate.py" not in cmdline:
        return False, f"cmdline lacks evaluate.py ({cmdline!r})"
    env = _read_proc_environ(target_pid)
    from .constants import ENV_AGENT_NAME
    if env.get(ENV_AGENT_NAME) != my_agent:
        return False, f"target env {ENV_AGENT_NAME} != my agent ({env.get(ENV_AGENT_NAME)!r})"
    return True, "ok"


def kill_stale_same_agent(
    agent_name: str,
    kill_hook: Optional[Callable[[int, int, str], None]] = None,
    log_event: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    """Kill any still-running evals owned by `agent_name` (other than self).

    Returns a list of records describing what happened (killed / skipped + reason).
    Always fails OPEN on any error — never raises into the caller.
    """
    if not agent_name or agent_name == "unknown":
        return []
    if kill_hook is None:
        from .eval_hooks_default import kill_eval as kill_hook  # type: ignore
    my_pid = os.getpid()
    log = log_event or (lambda s: None)
    actions: list[dict] = []
    try:
        with _agent_kill_lock(agent_name):
            with _queue_lock() as fd:
                entries = _read_queue(fd)
            for entry in list(entries):
                if entry.get("agent_name") != agent_name:
                    continue
                if int(entry.get("pid", 0)) == my_pid:
                    continue
                ok, reason = _is_safe_to_kill(entry, my_pid, agent_name)
                if not ok:
                    actions.append({"queue_id": entry.get("queue_id"), "action": "skipped", "reason": reason})
                    log(f"skipped kill of pid {entry.get('pid')}: {reason}")
                    # Garbage-collect the stale entry if its process is dead.
                    if reason == "target already dead":
                        try:
                            dequeue(entry["queue_id"])
                        except Exception:
                            pass
                    continue
                target_pid = int(entry["pid"])
                target_pgid = int(entry["pgid"])
                target_path = entry.get("solution_path", "")
                log(f"killing stale eval pid={target_pid} pgid={target_pgid} path={target_path}")
                try:
                    kill_hook(target_pid, target_pgid, target_path)
                except Exception as exc:
                    actions.append({"queue_id": entry.get("queue_id"), "action": "kill_hook_error", "reason": str(exc)})
                    log(f"kill hook raised: {exc!r}")
                    continue
                deadline = time.time() + KILL_DEADLINE_SECONDS
                while time.time() < deadline and _alive(target_pid):
                    time.sleep(0.1)
                if _alive(target_pid):
                    actions.append({"queue_id": entry.get("queue_id"), "action": "kill_timeout", "pid": target_pid})
                    log(f"target pid {target_pid} survived {KILL_DEADLINE_SECONDS}s")
                else:
                    actions.append({"queue_id": entry.get("queue_id"), "action": "killed", "pid": target_pid})
                    log(f"target pid {target_pid} terminated cleanly")
                # Clean up queue entry regardless (process is dead or unreachable).
                try:
                    dequeue(entry["queue_id"])
                except Exception:
                    pass
    except Exception as exc:
        # Total fail-open: log and continue.
        log(f"kill_stale_same_agent fatal: {exc!r}")
    return actions


def verify_lock_released(lock_path: str, deadline_s: float = 5.0) -> bool:
    """Try to acquire `lock_path` non-blocking; return True if we got it.

    Use this after a kill to verify the killed process actually released
    its hardware/lock. This is more reliable than lsof.
    """
    p = Path(lock_path)
    if not p.exists():
        return True  # nothing to release
    deadline = time.time() + deadline_s
    while time.time() < deadline:
        try:
            fd = os.open(lock_path, os.O_RDWR)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                return True
            except BlockingIOError:
                os.close(fd)
        except OSError:
            return True
        time.sleep(0.1)
    return False
