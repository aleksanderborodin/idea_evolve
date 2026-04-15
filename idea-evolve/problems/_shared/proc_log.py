"""Agent-readable narrative process logs.

Every long-running process (evaluations, training, kills, agent sessions) writes
a markdown log to runs/<problem>/<attempt>/proc_logs/<ts>_<agent>_<kind>_<pid>.md
that an agent can read to understand WHY a process failed/was killed and WHAT
to try next — not just a fitness number.

Format is markdown so agents reading via Read tool see structure naturally.
Append-only line-buffered I/O with fsync after every line keeps logs durable
under SIGKILL (final partial line may be lost; everything before is safe).

The same Writer class is used by evaluate.py, kill hooks, and (eventually) the
orchestrator harness — one class, one format, zero drift.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import signal
import sys
import traceback
from pathlib import Path
from typing import Optional

from .constants import DEFAULT_PROC_LOG_RETENTION, PROC_LOGS_SUBDIR


def _ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


class Writer:
    """Append-only durable log writer with SIGTERM-aware finalization."""

    def __init__(
        self,
        run_root: Path,
        agent_name: str,
        kind: str,
        pid: Optional[int] = None,
        sticky: bool = False,
    ):
        self.run_root = Path(run_root)
        self.agent_name = agent_name or "unknown"
        self.kind = kind
        self.pid = pid or os.getpid()
        self.sticky = sticky
        log_dir = self.run_root / PROC_LOGS_SUBDIR
        log_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{_ts()}_{self.agent_name}_{self.kind}_{self.pid}.md"
        self.path = log_dir / fname
        self._fp = open(self.path, "a", buffering=1)  # line-buffered
        self._closed = False
        self._outcome: Optional[str] = None
        self.write_header()
        if sticky:
            sticky_marker = self.path.with_suffix(".md.sticky")
            sticky_marker.write_text("1")
        # Best-effort SIGTERM handler to record a final line before exit.
        try:
            signal.signal(signal.SIGTERM, self._on_sigterm)
        except (ValueError, OSError):
            pass  # not main thread, etc.

    def write_header(self) -> None:
        self._line(f"# Process Log — {self.agent_name} / {self.kind} / pid {self.pid}")
        self._line("")
        self._line("## Summary")
        self._line(f"- **Started:** {_now_iso()}")
        self._line(f"- **Outcome:** (in progress)")
        self._line("")
        self._line("## Timeline")

    def event(self, message: str) -> None:
        """Append a timestamped event line to the timeline."""
        self._line(f"- {_now_iso()} — {message}")

    def section(self, title: str, body: str) -> None:
        self._line("")
        self._line(f"## {title}")
        self._line(body)
        self._line("")

    def kv(self, **fields) -> None:
        self._line("")
        for k, v in fields.items():
            self._line(f"- **{k}:** {v}")

    def traceback(self, exc: BaseException) -> None:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self.section("Traceback", f"```\n{tb}\n```")

    def hints(self, hints_text: str) -> None:
        if hints_text:
            self.section("What agents should try next", hints_text)

    def finalize(self, outcome: str, mark_sticky: bool = False) -> None:
        """Mark process outcome and close the log."""
        if self._closed:
            return
        self._outcome = outcome
        self._line("")
        self._line("---")
        self._line(f"_Finalized at {_now_iso()} — outcome: **{outcome}**_")
        try:
            self._fp.flush()
            os.fsync(self._fp.fileno())
        except OSError:
            pass
        self._fp.close()
        self._closed = True
        if mark_sticky or self.sticky:
            sticky_marker = self.path.with_suffix(".md.sticky")
            sticky_marker.write_text("1")

    def _on_sigterm(self, signum, frame) -> None:
        if self._closed:
            return
        try:
            self._line("")
            self._line(f"- {_now_iso()} — SIGTERM received, finalizing log")
            self._fp.flush()
            os.fsync(self._fp.fileno())
        except Exception:
            pass
        # Re-raise default behavior so process actually exits.
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGTERM)

    def _line(self, s: str) -> None:
        try:
            self._fp.write(s + "\n")
            self._fp.flush()
            os.fsync(self._fp.fileno())
        except (OSError, ValueError):
            pass

    @property
    def log_path(self) -> str:
        return str(self.path)


def prune_old_logs(run_root: Path, keep: int = DEFAULT_PROC_LOG_RETENTION) -> int:
    """LRU-prune proc_logs, never deleting sticky-marked logs.

    Returns number of files removed.
    """
    log_dir = Path(run_root) / PROC_LOGS_SUBDIR
    if not log_dir.exists():
        return 0
    md_files = sorted(log_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    non_sticky = [p for p in md_files if not p.with_suffix(".md.sticky").exists()]
    excess = len(non_sticky) - keep
    if excess <= 0:
        return 0
    removed = 0
    for p in non_sticky[:excess]:
        try:
            p.unlink()
            removed += 1
        except OSError:
            pass
    return removed
