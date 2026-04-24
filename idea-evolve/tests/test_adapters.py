"""Adapter smoke tests.

These tests exercise the minimum contract all harnesses must honor:
  - `launch()` returns a non-empty session id (and finishes under timeout)
  - `resume()` with the returned id retains session memory
  - `SessionTimeout` is raised on wall-clock timeout AND carries a session id
    so the wrap-up/debrief state machine can resume the same session

Heavier tests (full-workflow, tool-permission translation, `--max-turns`
fidelity) are deliberately out of scope. These only guard the pieces
`orchestrator.py` depends on.

Running:
    cd idea-evolve
    python3 -m pytest tests/test_adapters.py -v

ClaudeCode tests skip unless `npx` and `@anthropic-ai/claude-code` resolve.
OpenCode tests skip unless the `opencode` binary is on `$PATH` and
`MODELGATE_API_KEY` is exported.
Codex coverage here is unit-only; live Codex sessions are not exercised.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator_harness import (
    ClaudeCodeAdapter,
    CodexAdapter,
    OpenCodeAdapter,
    SessionError,
    SessionTimeout,
    _find_session_id,
    get_adapter,
)


# ---------------------------------------------------------------------------
# Unit tests — no subprocess, no network
# ---------------------------------------------------------------------------

def test_registry_returns_cached_instance():
    a = get_adapter("claude-code")
    b = get_adapter("claude-code")
    assert a is b
    assert a.name == "claude-code"


def test_registry_unknown_falls_back_to_claude_code(capsys):
    adapter = get_adapter("made-up-name")
    assert adapter.name == "claude-code"
    assert "falling back" in capsys.readouterr().out


def test_opencode_adapter_takes_model_map_override():
    override = {"sonnet": "modelgate/gpt-4o"}
    adapter = OpenCodeAdapter(model_map=override)
    assert adapter.model_map["sonnet"] == "modelgate/gpt-4o"


def test_codex_adapter_takes_model_map_override():
    override = {"sonnet": "gpt-5.4"}
    adapter = CodexAdapter(model_map=override)
    assert adapter.model_map["sonnet"] == "gpt-5.4"


def test_registry_returns_codex_adapter():
    adapter = get_adapter("codex")
    assert adapter.name == "codex"


def test_codex_session_id_extraction_accepts_nested_events():
    ev = {"type": "session_configured", "payload": {"session_id": "abc-123"}}
    assert _find_session_id(ev) == "abc-123"


def test_codex_adapter_adds_reasoning_effort_config(tmp_path):
    adapter = CodexAdapter(
        model_map={"opus": "gpt-5.5"},
        reasoning_effort_map={"opus": "high"},
    )
    captured = {}

    def fake_run(cmd, prompt_text, project_root, timeout, run_root,
                 agent_name=None, problem=None, attempt=None):
        captured["cmd"] = cmd
        return "", "thread_123", 1234

    adapter._run_streaming = fake_run
    _, sid, _ = adapter.launch(
        project_root=tmp_path,
        prompt_text="ok",
        model="opus",
        timeout=1,
    )

    assert sid == "thread_123"
    assert "-c" in captured["cmd"]
    assert 'model_reasoning_effort="high"' in captured["cmd"]


def test_opencode_tool_env_mapping():
    adapter = OpenCodeAdapter()
    env = adapter._allowed_tools_env(["Read", "Write", "Bash", "Glob"])
    perm = json.loads(env["OPENCODE_PERMISSION"])
    assert perm["edit"] == "allow"   # Write listed → edit allowed
    assert perm["bash"] == "allow"   # Bash listed → bash allowed
    assert perm["webfetch"] == "ask" # webfetch not listed → defaults to ask


def test_opencode_tool_env_empty_when_no_tools():
    adapter = OpenCodeAdapter()
    assert adapter._allowed_tools_env(None) == {}
    assert adapter._allowed_tools_env([]) == {}


def test_session_timeout_carries_id():
    e = SessionTimeout("late", session_id="ses_abc", pid=1234)
    assert e.session_id == "ses_abc"
    assert e.pid == 1234


def test_claude_code_adapter_uses_default_model_map():
    adapter = ClaudeCodeAdapter()
    assert adapter.model_map["opus"] == "claude-opus-4-6"
    assert adapter.model_map["sonnet"] == "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Integration tests — real subprocess, require opencode + ModelGate
# ---------------------------------------------------------------------------

HAS_OPENCODE = shutil.which(os.environ.get("OPENCODE_BIN", "opencode")) is not None
HAS_MODELGATE = bool(os.environ.get("MODELGATE_API_KEY"))
OC_MODEL = os.environ.get("OC_TEST_MODEL", "modelgate/minimax-m2.7")


@pytest.mark.skipif(not (HAS_OPENCODE and HAS_MODELGATE),
                    reason="opencode binary or MODELGATE_API_KEY missing")
def test_opencode_launch_returns_server_session_id(tmp_path):
    adapter = OpenCodeAdapter()
    stdout, sid, pid = adapter.launch(
        project_root=tmp_path,
        prompt_text="reply with only the word 'ok'",
        model=OC_MODEL,
        timeout=60,
        max_turns=5,
    )
    assert sid and sid.startswith("ses_"), f"bad session id: {sid!r}"
    assert pid > 0
    # At least one JSON event should be in stdout and carry the same sid
    saw = False
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
            if ev.get("sessionID") == sid:
                saw = True
                break
        except Exception:
            pass
    assert saw, "no JSON event carried the returned session id"


@pytest.mark.skipif(not (HAS_OPENCODE and HAS_MODELGATE),
                    reason="opencode binary or MODELGATE_API_KEY missing")
def test_opencode_resume_retains_memory(tmp_path):
    adapter = OpenCodeAdapter()
    secret = f"zxq{uuid.uuid4().hex[:6]}"
    _, sid, _ = adapter.launch(
        project_root=tmp_path,
        prompt_text=f"remember the secret code: {secret}. reply 'ok'.",
        model=OC_MODEL,
        timeout=60,
        max_turns=5,
    )
    stdout = adapter.resume(
        project_root=tmp_path,
        session_id=sid,
        prompt_text="what was the secret code I told you? reply with only the code.",
        model=OC_MODEL,
        timeout=60,
        max_turns=5,
    )
    text = _concat_text_events(stdout).lower()
    assert secret in text, f"memory not preserved. reply: {text!r}"


@pytest.mark.skipif(not (HAS_OPENCODE and HAS_MODELGATE),
                    reason="opencode binary or MODELGATE_API_KEY missing")
def test_opencode_timeout_captures_sid_and_is_resumable(tmp_path):
    adapter = OpenCodeAdapter()
    with pytest.raises(SessionTimeout) as excinfo:
        adapter.launch(
            project_root=tmp_path,
            prompt_text="write a very long 5000-word essay about marine biology",
            model=OC_MODEL,
            timeout=7,
            max_turns=5,
        )
    sid = excinfo.value.session_id
    assert sid and sid.startswith("ses_"), f"no sid captured on timeout: {sid!r}"

    stdout = adapter.resume(
        project_root=tmp_path,
        session_id=sid,
        prompt_text="stop. in one word: what topic were you writing about?",
        model=OC_MODEL,
        timeout=60,
        max_turns=5,
    )
    text = _concat_text_events(stdout).lower()
    assert any(k in text for k in ("marine", "biology", "ocean", "sea")), \
        f"could not recall pre-timeout topic: {text!r}"


def _concat_text_events(stdout: str) -> str:
    parts = []
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
            if ev.get("type") == "text":
                parts.append(ev["part"].get("text", ""))
        except Exception:
            pass
    return " ".join(parts)
