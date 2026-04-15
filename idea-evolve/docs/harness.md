# Harness Layer

Agent sessions are launched through a `HarnessAdapter` abstraction in
`orchestrator_harness.py`. This decouples the orchestrator from any specific CLI.

## Adapters

### ClaudeCodeAdapter (`claude-code`)

```
Binary:   npx @anthropic-ai/claude-code
Launch:   --print --model <model> --max-turns <N> --session-id <uuid> [--allowedTools ...]
Resume:   --print --resume <uuid> --model <model> --max-turns <N>
```

- Session ids are **caller-assigned UUIDs** generated before launch.
- Wrap-up/debrief uses `--resume <same-uuid>` — session is already in memory.
- Models from `CLAUDE_CODE_MODEL_MAP`: `opus` → `claude-opus-4-6`, `sonnet` → `claude-sonnet-4-6`, `haiku` → `claude-haiku-4-5-20251001`.

### OpenCodeAdapter (`opencode`)

```
Binary:   $OPENCODE_BIN (default: "opencode", override via OPENCODE_BIN env var)
Launch:   run --format json -m <provider/model> --dangerously-skip-permissions
Resume:   run --format json -s <ses_id> -m <provider/model> --dangerously-skip-permissions
```

- Session ids are **server-assigned** (`ses_<26chars>`), emitted in the first JSON event on stdout.
- The adapter streams stdout in a reader thread to capture the id before any potential timeout-kill.
- `SessionTimeout` is raised with `session_id` attached so wrap-up can resume with `-s <ses_id>`.
- Sessions persist in opencode's SQLite DB even after SIGKILL.
- **No `--max-turns` equivalent** — wall-clock timeout is the only ceiling (one-time warning logged per run).
- Tool allowlist is translated into `OPENCODE_PERMISSION` env JSON: `edit`/`bash`/`webfetch`.

## Contract

Both adapters expose the same interface:

```python
adapter.launch(
    project_root: Path,
    prompt_text: str,
    model: str,          # "opus" | "sonnet" | "haiku" — translated via model map
    timeout: int,        # seconds
    max_turns: int,
    allowed_tools: list[str] | None,
    session_id: str | None,
    run_root: Path | None,
) -> tuple[str, str, int]   # (stdout, session_id, pid)

adapter.resume(
    project_root: Path,
    session_id: str,
    prompt_text: str,
    model: str,
    timeout: int,
    max_turns: int,
    allowed_tools: list[str] | None,
    run_root: Path | None,
) -> str                    # stdout
```

## Configuration (`user/config.yaml`)

```yaml
harnesses:
  default: claude-code   # or: opencode
  per_agent: {}          # override by role — only list EXCEPTIONS to default
                         # (listing a role whose harness == default is a no-op)

models:
  opencode:              # opencode alias → provider/model
    opus:   modelgate/claude-sonnet-4-5
    sonnet: modelgate/minimax-m2.7
    haiku:  modelgate/minimax-m2.7
```

**Resolution order** at every launch: `per_agent[agent_role]` → `default` → `claude-code` (fallback with warning on unknown names).

**Per-agent role keys:** `architect`, `explore`, `exploit`, `genetic`, `full`, `research`,
`experimentator`, `evaluator`, `system_critic`, `consistency_reviewer`, `wrap_up`, `debrief_recovery`.

## Currently Wired Call Sites

Only the architect currently passes `agent_role=` explicitly:

```python
# orchestrator.py ~line 2309
launch_claude_session(..., agent_role="architect")
resume_claude_session(..., agent_role="architect")   # architect wrap-up
```

All other call sites (agents, evaluator, critic, consistency reviewer) rely on
`harnesses.default`. To route them individually, thread `agent_role=<role>` into
`run_single_agent()` and `run_analysis()` launch sites.

## Process Management

Both adapters use `start_new_session=True` when spawning subprocesses. On timeout:

1. `os.killpg(proc.pid, SIGTERM)` — terminate process group
2. Wait up to 5 seconds
3. `os.killpg(proc.pid, SIGKILL)` if still alive

This prevents orphan `node` (claude-code) or `bun` (opencode) grandchildren after timeout.

## Exceptions

```python
SessionTimeout(msg, session_id=..., pid=...)  # wall-clock timeout exceeded
SessionError(msg, session_id=..., pid=...)    # non-zero exit code
```

`SessionTimeout` always carries the `session_id` so the wrap-up/debrief state machine
can resume the same session.

## Pre-flight Requirement for OpenCode

OpenCode reads its API key from the shell environment. Before running any opencode-routed
session, load `.env`:

```bash
set -a; source .env; set +a
```

Without this, opencode exits with empty stdout and the adapter raises:
`SessionError: opencode launch produced no sessionID in stdout`

Also ensure `OPENCODE_BIN` points to the actual binary if `opencode` is not on `$PATH`:
```
OPENCODE_BIN=/home/sasha/.opencode/bin/opencode
```

## Tests

```bash
cd idea-evolve
python3 -m pytest tests/test_adapters.py -v
```

7 unit tests always run. 3 integration tests auto-skip if `opencode` binary or
`MODELGATE_API_KEY` is absent.
