# Idea Evolve Agent Guide

`AGENTS.md` is a symlink to this file. Treat this document as the shared
operating guide for any coding agent working in this repository: Claude Code,
OpenCode, Codex, or a human-driven shell session. The older long-form operational
tracker was moved to `docs/operational_history.md`; use it for archaeology, not
as the primary instruction source.

The full system specification is `IDEA_EVOLVE_COMPLETE_V4.md`. The technical
deep dives live in `docs/`. The implementation lives in `idea-evolve/`.

## Non-Negotiable Rules

When you change system behavior, update the docs in the same pass. This includes
code, config, architecture, bug fixes, prompts, metrics fields, helper APIs,
queue/lock paths, env-var names, file schemas, and evaluation data flow.

Cross-cutting changes usually require updates in all relevant places:
`CLAUDE.md`, `docs/problem_design_guide.md`, the specific `docs/*.md` deep dive,
affected problem `description.md` / `helpers/README.md`, and any agent prompt
that mentions the behavior. Run `python3 scripts/check_docs_consistency.py`
from `idea-evolve/` before considering the change complete.

`docs/problem_design_guide.md` is a living contract for problem authors. If you
discover a problem-design failure mode, an evaluation footgun, a helper API
confusion, a lost artifact, or a metric that should have existed from day one,
add the lesson there while fixing the issue.

Every behavior described in `docs/problem_design_guide.md` must have a reference
implementation in one of the real `problems/*` directories. Do not document a
pattern that no problem uses.

Cross-cutting constants live in `idea-evolve/problems/_shared/constants.py`.
Import or reference those constants instead of duplicating literal paths,
env-var names, or timeout values.

Never commit `.env`, downloaded datasets, generated checkpoints, or run outputs
that are intentionally gitignored.

## Working Model

Idea Evolve is an evolutionary optimization system. The orchestrator launches
specialized agent sessions, agents write and evaluate candidate solutions, and
analysis phases extract knowledge back into the run directory. The orchestrator
is intentionally file-driven: run state, population, reports, briefs, feedback,
and knowledge all live under `idea-evolve/runs/{problem}/{attempt}/`.

The supported harnesses are a system feature, not separate project modes:
`claude-code`, `opencode`, and `codex` are all implemented through
`idea-evolve/orchestrator_harness.py`. Current local config routes normal work
through OpenCode and high-reasoning `opus` tier work through Codex. Claude Code
remains supported by the adapter but requires the Claude Code CLI/auth to be
available in the shell.

All agents share the same filesystem contract:

- Read global resources from `idea-evolve/agents/`, `idea-evolve/prompts/`,
  `idea-evolve/user/`, and `idea-evolve/problems/{problem}/`.
- Work inside the assigned run root under `idea-evolve/runs/{problem}/{attempt}/`.
- Write agent scratch/output only in the workspace assigned by the orchestrator.
- Preserve user changes and unrelated dirty files.
- Prefer small, targeted edits over broad refactors.

## Repository Layout

Important paths from the repo root:

- `CLAUDE.md` / `AGENTS.md` - this guide.
- `IDEA_EVOLVE_COMPLETE_V4.md` - standalone full specification.
- `docs/` - technical documentation and historical notes.
- `idea-evolve/orchestrator.py` - generation loop and phase orchestration.
- `idea-evolve/orchestrator_harness.py` - Claude Code, OpenCode, and Codex adapters.
- `idea-evolve/agents/` - prompt templates for architect, solution agents, and analysis agents.
- `idea-evolve/prompts/` - shared prompt fragments.
- `idea-evolve/user/config.yaml` - active harness/model/timeouts/agent configuration.
- `idea-evolve/problems/` - problem definitions, evaluators, validators, helpers, metrics.
- `idea-evolve/problems/_shared/constants.py` - shared constants and env-var names.
- `idea-evolve/runs/` - generated run state, populations, reports, knowledge, workspaces.
- `dashboard/` - Flask dashboard for browsing runs.

## Environment

Use the project virtualenv from the repository root:

```bash
source venv/bin/activate
```

Most orchestrator commands run from `idea-evolve/`, so activate the same venv
there as `source ../venv/bin/activate` if needed.

Secrets live in repo-root `.env` and are loaded explicitly:

```bash
set -a; source .env; set +a
```

From inside `idea-evolve/`, use:

```bash
set -a; source ../.env; set +a
```

The current `.env` is expected to provide provider keys for OpenCode routes and
Kaggle access. Do not print secret values. It is fine to check whether a key is
present with `${VAR:+present}`.

## Running The System

Always `cd idea-evolve` before running the orchestrator. The orchestrator expects
`.` to be the project root inside the implementation directory.

Common commands:

```bash
cd idea-evolve
../venv/bin/python orchestrator.py . --problem sidon --single
../venv/bin/python orchestrator.py . --problem sidon --new-attempt
../venv/bin/python orchestrator.py . --problem megaminx --new-attempt
../venv/bin/python orchestrator.py . --problem strawberry --new-attempt
../venv/bin/python orchestrator.py . --problem gemm --dry-run
../venv/bin/python orchestrator.py . --problem gemm --start-gen 5
```

For long runs, use `nohup` and unbuffered stdout so the process survives terminal
or agent-session disconnects:

```bash
cd idea-evolve
nohup ../venv/bin/python -u orchestrator.py . --problem strawberry --new-attempt --single \
    > /tmp/run.log 2>&1 & disown
tail -F /tmp/run.log
```

If an orchestrator was killed mid-run, inspect active processes and clear stale
queue/lock state only when you are sure no live evaluation still owns it.

Run the dashboard from the repository root:

```bash
source venv/bin/activate
python dashboard/app.py
```

The default dashboard URL is `http://localhost:5000`.

## Evaluation Workflow

Solution agents must use the evaluate-immediately loop:

1. Write one candidate solution.
2. Run the problem's `evaluate.py` on that exact file.
3. Confirm the `.score` sidecar exists.
4. Only then write or modify the next solution.

`.score` files and the eval cache are the authoritative score sources. Do not
use header comments as scores. Invalid solutions must receive the problem's
sentinel score from `metrics.yaml`; do not award partial credit unless the
problem explicitly defines that as valid behavior.

When changing an evaluator, validator, helper, metrics field, or problem data
flow, update `docs/problem_design_guide.md` and the problem's own docs in the
same edit pass.

## Active Problems

Use `metrics.yaml` for fitness direction, target, precision, concurrency, and
problem-specific toggles.

Current problem focus is usually `sidon`: largest Sidon set in `{0, ..., 10000}`;
higher score is better; invalid solutions receive sentinel score `0`.

Also available:

- `megaminx` - Kaggle CayleyPy Megaminx path-length minimization; GPU-capable;
  proxy evaluation by default and full evaluation by explicit override.
- `strawberry` - YOLO11 strawberry disease instance segmentation; GPU evaluation
  with serialized access.
- `gemm` - binary-ternary GEMM optimization.
- `permcodes` - permutation code search.

Problem-specific truth belongs in each problem directory and run knowledge base,
not in this guide. If the current target or best-known result changes, update the
problem docs and relevant run knowledge.

## Development Practice

Read local code before changing it. Follow existing patterns in the surrounding
module. Use `rg` / `rg --files` for search. Keep changes scoped to the request.

Use `apply_patch` for manual edits. Do not revert user changes or unrelated dirty
work. Avoid destructive git commands unless explicitly requested.

For Python verification, prefer the project venv:

```bash
cd idea-evolve
../venv/bin/python -m pytest tests/test_adapters.py -v
../venv/bin/python scripts/check_docs_consistency.py
```

Run narrower tests first when possible, then broaden when the change affects
shared behavior.

## Harness Notes

Harness behavior is documented in `docs/harness.md`; implementation is in
`idea-evolve/orchestrator_harness.py`.

OpenCode uses provider config from `~/.config/opencode/opencode.json` and keys
from the loaded environment. If OpenCode exits with no session id, first check
that `.env` was loaded into the shell that launched the orchestrator.

Codex uses the installed Codex CLI and its normal auth/config. The adapter runs
with workspace-write sandboxing and noninteractive approval policy. Codex has no
`--max-turns` equivalent, so wall-clock timeout is the real ceiling.

Claude Code uses `npx @anthropic-ai/claude-code` and Claude auth. The adapter
supports caller-assigned session ids and resume. Use Claude-specific wording only
when discussing that adapter; otherwise say "agent session".

## Documentation Map

- `docs/problem_design_guide.md` - problem authoring contract, evaluation rules,
  metrics, concurrency, queues, GPU pitfalls, Kaggle scaffolding.
- `docs/architect.md` - architect phase inputs, outputs, and manifest rules.
- `docs/agents.md` - agent workspace contract and output movement.
- `docs/analysis_phases.md` - evaluator, system critic, consistency reviewer.
- `docs/knowledge_base.md` - knowledge directory schemas and lifecycle.
- `docs/file_layout.md` - full run directory tree.
- `docs/harness.md` - harness adapter contract.
- `docs/dashboard.md` - dashboard tabs, API endpoints, scanner behavior.
- `docs/communication.md` - engine/dashboard file interface.
- `docs/operational_history.md` - archived issue tracker and historical notes.

## Editing This Guide

Edit `CLAUDE.md`; `AGENTS.md` should remain a symlink to it. Do not create
separate divergent copies.

Keep this file short and operational. Move historical notes, resolved issue
details, and long design rationale into `docs/operational_history.md` or a
specific `docs/*.md` file. This guide should tell the next agent how to work,
not preserve the full project diary.
