"""
Agent harness adapters.

Two CLI harnesses launch Claude Code-compatible agent sessions in idea-evolve:

- `ClaudeCodeAdapter` — `npx @anthropic-ai/claude-code --print ...` (default).
  Session ids are caller-assigned UUIDs. Wrap-up/debrief resumes via `--resume`.

- `OpenCodeAdapter` — `opencode run --format json ...`.
  Session ids are SERVER-assigned (`ses_<26chars>`) and emitted in the first
  JSON event on stdout. Adapter streams stdout line-buffered to capture the
  id before any potential timeout-kill, then waits for completion or timeout.
  Resume uses `-s <ses_id>`. Sessions persist in opencode's SQLite DB even
  after SIGKILL, so the wrap-up/debrief state machine works unchanged.

Both adapters return identical `(stdout, session_id, pid)` / `(stdout, session_id)`
shapes so callers can swap between them by one line.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import uuid
from pathlib import Path


# ---------------------------------------------------------------------------
# Exceptions — shared by all adapters
# ---------------------------------------------------------------------------

class SessionTimeout(Exception):
    """Raised when a harness session exceeds its timeout."""
    def __init__(self, msg, session_id=None, pid=None):
        super().__init__(msg)
        self.session_id = session_id
        self.pid = pid


class SessionError(Exception):
    """Raised when a harness session exits with a non-zero return code."""
    def __init__(self, msg, session_id=None, pid=None):
        super().__init__(msg)
        self.session_id = session_id
        self.pid = pid


# ---------------------------------------------------------------------------
# Model maps — per-harness translation from idea-evolve aliases to provider ids
# ---------------------------------------------------------------------------

CLAUDE_CODE_MODEL_MAP = {
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

# Default opencode model map. Can be overridden via user/config.yaml
# `models.opencode:` block (merged at load time in orchestrator.py).
OPENCODE_MODEL_MAP_DEFAULT = {
    "opus": "modelgate/claude-sonnet-4-5",
    "sonnet": "modelgate/minimax-m2.7",
    "haiku": "modelgate/minimax-m2.7",
}


def _build_env(run_root: Path | None) -> dict:
    env = os.environ.copy()
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = "16000"
    if run_root is not None:
        env["IDEA_EVOLVE_RUN_ROOT"] = str(run_root)
    return env


def _kill_group(proc: subprocess.Popen) -> None:
    """Kill the entire process group, SIGTERM first then SIGKILL fallback."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


# ---------------------------------------------------------------------------
# ClaudeCodeAdapter
# ---------------------------------------------------------------------------

class ClaudeCodeAdapter:
    name = "claude-code"

    def __init__(self, model_map: dict | None = None):
        self.model_map = model_map or CLAUDE_CODE_MODEL_MAP

    def _run(self, cmd, prompt_text, project_root, timeout, session_id):
        env = _build_env(getattr(self, "_run_root", None))
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(project_root),
                env=env,
                start_new_session=True,
            )
        except FileNotFoundError:
            print("  ERROR: Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
            sys.exit(1)

        pid = proc.pid
        try:
            stdout, stderr = proc.communicate(input=prompt_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            raise SessionTimeout(f"Timed out after {timeout}s", session_id=session_id, pid=pid)

        if proc.returncode != 0:
            if stderr:
                print(f"  STDERR: {stderr[:500]}")
            raise SessionError(
                f"Exited with code {proc.returncode}: {stderr[:200] if stderr else 'no stderr'}",
                session_id=session_id,
            )
        return stdout, pid

    def launch(
        self,
        project_root: Path,
        prompt_text: str,
        model: str = "sonnet",
        timeout: int = 300,
        max_turns: int = 50,
        allowed_tools: list[str] | None = None,
        session_id: str | None = None,
        run_root: Path | None = None,
    ) -> tuple[str, str, int]:
        self._run_root = run_root
        model_id = self.model_map.get(model, model)
        if session_id is None:
            session_id = str(uuid.uuid4())

        cmd = [
            "taskset", "-c", "2-7",
            "npx", "@anthropic-ai/claude-code",
            "--print",
            "--model", model_id,
            "--max-turns", str(max_turns),
            "--session-id", session_id,
        ]
        if allowed_tools:
            for tool in allowed_tools:
                cmd.extend(["--allowedTools", tool])

        stdout, pid = self._run(cmd, prompt_text, project_root, timeout, session_id)
        return stdout, session_id, pid

    def resume(
        self,
        project_root: Path,
        session_id: str,
        prompt_text: str,
        model: str = "sonnet",
        timeout: int = 300,
        max_turns: int = 50,
        allowed_tools: list[str] | None = None,
        run_root: Path | None = None,
    ) -> str:
        self._run_root = run_root
        model_id = self.model_map.get(model, model)
        cmd = [
            "taskset", "-c", "2-7",
            "npx", "@anthropic-ai/claude-code",
            "--print",
            "--resume", session_id,
            "--model", model_id,
            "--max-turns", str(max_turns),
        ]
        if allowed_tools:
            for tool in allowed_tools:
                cmd.extend(["--allowedTools", tool])

        stdout, _pid = self._run(cmd, prompt_text, project_root, timeout, session_id)
        return stdout


# ---------------------------------------------------------------------------
# OpenCodeAdapter
# ---------------------------------------------------------------------------

OPENCODE_BIN = os.environ.get("OPENCODE_BIN", "opencode")


class OpenCodeAdapter:
    name = "opencode"

    def __init__(self, model_map: dict | None = None):
        self.model_map = model_map or OPENCODE_MODEL_MAP_DEFAULT
        self._warned_max_turns = False

    def _allowed_tools_env(self, allowed_tools: list[str] | None) -> dict:
        # Translate claude-code tool names to opencode's OPENCODE_PERMISSION JSON.
        # Fine-grained per-tool gating; pass-through of the caller's allowlist.
        if not allowed_tools:
            return {}
        # Opencode permission keys: edit/bash/webfetch. Map conservatively.
        perm = {
            "edit": "ask",
            "bash": "ask",
            "webfetch": "ask",
        }
        names = {t.lower() for t in allowed_tools}
        if "write" in names or "edit" in names:
            perm["edit"] = "allow"
        if "bash" in names:
            perm["bash"] = "allow"
        if "webfetch" in names:
            perm["webfetch"] = "allow"
        return {"OPENCODE_PERMISSION": json.dumps(perm)}

    def _launch_streaming(self, cmd, prompt_text, project_root, timeout, run_root, extra_env):
        """Launch opencode with --format json; stream stdout to capture sessionID
        from the first event. Returns (stdout_text, session_id, pid).
        Raises SessionTimeout with captured session_id attached on timeout.
        """
        env = _build_env(run_root)
        env.update(extra_env)

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(project_root),
                env=env,
                start_new_session=True,
                bufsize=1,
            )
        except FileNotFoundError:
            print(f"  ERROR: opencode binary not found at '{OPENCODE_BIN}'. Install: https://opencode.ai")
            sys.exit(1)

        pid = proc.pid
        session_id_box = {"id": None}
        lines_box = {"buf": []}

        def reader():
            try:
                for line in proc.stdout:
                    lines_box["buf"].append(line)
                    if session_id_box["id"] is None:
                        try:
                            ev = json.loads(line)
                            sid = ev.get("sessionID")
                            if sid:
                                session_id_box["id"] = sid
                        except Exception:
                            pass
            except Exception:
                pass

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        try:
            proc.stdin.write(prompt_text)
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Give the reader a brief moment to flush any buffered session id
            t.join(timeout=0.5)
            _kill_group(proc)
            t.join(timeout=2.0)
            raise SessionTimeout(
                f"Timed out after {timeout}s",
                session_id=session_id_box["id"],
                pid=pid,
            )

        t.join(timeout=5.0)
        stderr = proc.stderr.read() if proc.stderr else ""
        stdout = "".join(lines_box["buf"])

        if proc.returncode != 0:
            if stderr:
                print(f"  STDERR: {stderr[:500]}")
            raise SessionError(
                f"Exited with code {proc.returncode}: {stderr[:200] if stderr else 'no stderr'}",
                session_id=session_id_box["id"],
            )
        return stdout, session_id_box["id"], pid

    def launch(
        self,
        project_root: Path,
        prompt_text: str,
        model: str = "sonnet",
        timeout: int = 300,
        max_turns: int = 50,
        allowed_tools: list[str] | None = None,
        session_id: str | None = None,
        run_root: Path | None = None,
    ) -> tuple[str, str, int]:
        if not self._warned_max_turns:
            print(f"  NOTE: opencode has no --max-turns equivalent (requested {max_turns}); wall-clock timeout {timeout}s is the only ceiling.")
            self._warned_max_turns = True

        model_id = self.model_map.get(model, model)
        cmd = [OPENCODE_BIN, "run", "--format", "json", "-m", model_id,
               "--dangerously-skip-permissions"]

        extra_env = self._allowed_tools_env(allowed_tools)
        stdout, sid, pid = self._launch_streaming(
            cmd, prompt_text, project_root, timeout, run_root, extra_env,
        )
        if sid is None:
            raise SessionError(
                "opencode launch produced no sessionID in stdout",
                session_id=None,
            )
        return stdout, sid, pid

    def resume(
        self,
        project_root: Path,
        session_id: str,
        prompt_text: str,
        model: str = "sonnet",
        timeout: int = 300,
        max_turns: int = 50,
        allowed_tools: list[str] | None = None,
        run_root: Path | None = None,
    ) -> str:
        model_id = self.model_map.get(model, model)
        cmd = [OPENCODE_BIN, "run", "--format", "json", "-s", session_id,
               "-m", model_id, "--dangerously-skip-permissions"]
        extra_env = self._allowed_tools_env(allowed_tools)
        stdout, _sid, _pid = self._launch_streaming(
            cmd, prompt_text, project_root, timeout, run_root, extra_env,
        )
        return stdout


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_ADAPTERS: dict[str, object] = {}


def get_adapter(name: str, opencode_model_map: dict | None = None):
    """Return a cached adapter instance by name. Unknown names fall back to
    claude-code with a one-time warning."""
    key = (name or "claude-code").strip().lower()
    if key not in ("claude-code", "opencode"):
        print(f"  WARNING: unknown harness '{name}', falling back to claude-code")
        key = "claude-code"
    if key in _ADAPTERS:
        return _ADAPTERS[key]
    if key == "opencode":
        adapter = OpenCodeAdapter(model_map=opencode_model_map)
    else:
        adapter = ClaudeCodeAdapter()
    _ADAPTERS[key] = adapter
    return adapter
