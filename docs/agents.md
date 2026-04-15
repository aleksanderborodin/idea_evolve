# Agent Work Phase

Agents are the second phase of every generation. They run in parallel inside isolated
workspaces, write solutions, evaluate them, and produce debrief reports.

## Agent Types

| Type | Purpose | Writes to |
|------|---------|-----------|
| `explore` | Novel approaches structurally different from existing solutions | `population/` |
| `exploit` | Refine top existing solutions with targeted improvements | `population/` |
| `genetic` | Crossover: combine two parent solutions | `population/` |
| `full` | Full autonomy — read everything, try anything | `population/` |
| `research` | Mathematical research, literature survey, no code required | `knowledge/research/` |
| `experimentator` | Build shared helper utilities for all agents | `knowledge/experiments/` + `problems/{id}/helpers/` |

## Workspace Layout

Each agent gets an isolated workspace at `workspace/gen{NNN}_{type}_{instance}/`:

```
workspace/gen001_explore_1/
├── prompt.md              # Agent role template (copy of agents/{type}.md)
├── brief.md               # Generation-specific brief (copy of briefs/gen001/explore_1.md)
└── output/                # Agent writes ALL work here
    ├── report.md          # REQUIRED — final debrief (approach, results, what worked)
    ├── sol01.py           # Solution code
    ├── sol01.score        # Sidecar JSON written by evaluate.py: {fitness, is_valid, ...}
    ├── sol02.py
    ├── sol02.score
    ├── observations.md    # Optional — agent's analysis notes
    ├── experiment_requests.md  # Optional — requests for future experiments
    └── sandbox/           # Scratch dir, deleted on output move
```

Experimentator workspace additionally has:
```
output/
├── helpers/               # Validated helper .py files (deployed to problems/{id}/helpers/)
└── ...
```

## What Agents Read

Agents are given file paths in their brief. Typically:

- `problems/{id}/description.md` and `constraints.md`
- `knowledge/state_of_affairs.md`
- `knowledge/ideas/active/` and `established/`
- `knowledge/clusters/*.md`
- `knowledge/facts/*.md`
- `population/gen{N-1}/*/sol*.py` + `.score` — previous generation solutions
- `problems/{id}/helpers/*.py` — available shared helpers
- For gen 2+: `population/best.py` — current best solution

Research agents also get `WebSearch` and `WebFetch` tools.

## Output Movement

After a successful session, outputs are moved out of the workspace:

### Regular agents (explore, exploit, full, genetic) — `move_agent_outputs()`
```
output/sol*.py + .score   →  population/gen{NNN}/{type}_{instance}/
output/observations.md    →  population/gen{NNN}/{type}_{instance}/
output/report.md          →  reports/gen{NNN}/{type}_{instance}.md
output/experiment_requests.md  →  feedback/experiment_requests/gen{NNN}/{type}_{instance}.md
```

### Research agents — `move_research_outputs()`
```
output/**                 →  knowledge/research/gen{NNN}/research_{instance}/
output/report.md          →  reports/gen{NNN}/research_{instance}.md
output/sol*.py + .score   →  population/gen{NNN}/research_{instance}/  (mirror, for rankings)
```

### Experimentator agents — `move_experiment_outputs()`
```
output/**                 →  knowledge/experiments/gen{NNN}/experimentator_{instance}/
output/helpers/*.py       →  problems/{id}/helpers/  (after validation)
output/report.md          →  reports/gen{NNN}/experimentator_{instance}.md
output/sol*.py + .score   →  population/gen{NNN}/experimentator_{instance}/  (mirror)
```

Helper validation (`_validate_helper`) checks: valid Python syntax, no banned imports
(`os.system`, `subprocess`, etc.), no top-level side effects.

## Session Flow

```
Phase 1: Main work session
    ──timeout──>  Phase 2: Wrap-up (resume same session)
                      ──fail──>  Phase 3: Debrief recovery (resume or new session)
```

### Phase 1 — Main work session
- Launched via `launch_claude_session` (dispatched to configured harness).
- Allowed tools: `Read`, `Write`, `Bash`, `Glob`, `Grep` (+ `WebSearch`, `WebFetch` for research).
- Timeout: per-agent `timeout` in manifest, or `config.timeouts.agent_default`.
- Session id saved to `gen_progress.json` immediately for crash recovery.

### Phase 2 — Wrap-up (if phase 1 timed out or errored)
- Resumes the **same session** via `resume_claude_session` — agent retains full memory.
- Message for regular agents: "Stop creating, evaluate all sol*.py you wrote, write report.md."
- Message for research agents: "Stop searching, write findings.md and report.md with what you found."
- Timeout: `config.timeouts.wrap_up`.

### Phase 3 — Debrief recovery (if no report.md after phases 1+2)
- First tries: resume same session (lightweight report-writing prompt).
- Fallback: new session with full context if no session id exists.
- Goal: produce a report.md capturing whatever was produced.
- Timeout: `config.timeouts.debrief_recovery`. Model: `sonnet`.

## Crash Recovery

On restart, `run_single_agent()` checks `gen_progress.json`:

| Agent status | Action |
|---|---|
| `complete` + `outputs_moved: true` | Skip entirely |
| `complete` + no `outputs_moved` | Re-move outputs, skip session |
| `running` | Check if PID is still alive. If dead, re-run. If alive, kill and re-run |
| `pending` | Re-run (was about to launch when orchestrator crashed) |
| absent | Run normally |

## Parallelism

Agents within a `parallel_groups` entry run concurrently via `ThreadPoolExecutor`.
Groups are executed sequentially — group 2 starts only after all agents in group 1 finish.
Max concurrent sessions: `config.max_parallel_sessions` (default 10).

## Key Functions (orchestrator.py)

| Function | Description |
|----------|-------------|
| `run_agents(project_root, gen, config)` | Top-level: reads manifest, dispatches groups |
| `_run_agent_group(...)` | Runs one parallel group via ThreadPoolExecutor |
| `run_single_agent(project_root, gen, agent_spec, config)` | Full lifecycle for one agent |
| `create_workspace(project_root, gen, atype, instance)` | Creates workspace dirs, copies prompt+brief |
| `cleanup_workspace(project_root, gen, atype, instance)` | Deletes workspace after successful move |
| `move_agent_outputs(...)` | Moves regular agent outputs |
| `move_research_outputs(...)` | Moves research agent outputs |
| `move_experiment_outputs(...)` | Moves experimentator outputs + deploys helpers |
| `_validate_helper(path)` | Syntax + safety check for helper files |
