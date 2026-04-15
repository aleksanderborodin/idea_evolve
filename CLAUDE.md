# Idea Evolve

Evolutionary code optimization through collaborative AI agent work sessions.
Full system specification: `IDEA_EVOLVE_COMPLETE_V4.md` (standalone, replicable from that doc alone).
This file is the operational quick-reference and exhaustive issue tracker.

**RULE: When you make any change to the system (code, config, architecture, bug fixes, new features,
scaling improvements, design decisions), you MUST update this file to reflect that change.
CLAUDE.md is the operational quick-reference and issue tracker. Keep it accurate.**

**RULE: `docs/problem_design_guide.md` is a living document. Every time we find a new
issue with how problems or their `evaluate.py` / `validate.py` / helpers are designed —
an error that agents couldn't diagnose, an ephemeral artifact that got lost, a footgun
in a helper, a metric we wished we had tracked from day 1 — add the lesson to that guide
in the relevant section. The guide exists so future problem authors don't rediscover
the same failure modes. If you fix a real bug caused by a design gap, update the guide
in the same edit pass as the fix.**

**RULE: Doc-sync on cross-cutting changes.** When you change ANY orchestrator flag,
`metrics.yaml` field, helper API, agent-prompt contract, queue/lock path, env-var
name, or other behavior used across files, you MUST update ALL of:
the relevant code, `docs/problem_design_guide.md` (the cross-reference table in §11
lists every behavior with its code/doc/prompt locations), `CLAUDE.md` (this file's
"What Works" or DESIGN sections), the reference problem's `description.md`, the
reference `helpers/README.md`, and every agent prompt that mentions the behavior.
Then run `python3 scripts/check_docs_consistency.py` before committing.

**RULE: Every behavior described in `docs/problem_design_guide.md` must have a reference
implementation in one of the `problems/*` directories.** If the guide describes a pattern
no problem uses, delete the guide entry or implement the pattern. The guide is the
contract problem authors read before writing a new problem.

**RULE: Single source of truth for cross-cutting constants.** Paths, env-var names, and
timeouts live in `idea-evolve/problems/_shared/constants.py`. Do not duplicate them as
string literals in evaluate.py, helpers, docs, or agent prompts. The consistency
checker fails when a constant name appears in a doc without resolving from that file.

**RULE: When you change a component's file I/O, schema, config keys, or data flow, also update
the relevant file in `docs/`. That folder is the technical deep-dive:**

| Doc | Covers | Status |
|-----|--------|--------|
| [docs/problem_design_guide.md](docs/problem_design_guide.md) | How to design new problems — required files, multi-metric support, eval-time budgets, GPU/zombie pitfalls, scheduling/kill contract, glossary, cross-ref table | EXISTS |
| [docs/architect.md](docs/architect.md) | Architect phase inputs/outputs/flow | EXISTS |
| [docs/agents.md](docs/agents.md) | Agent workspace, output movement, session flow | EXISTS |
| [docs/analysis_phases.md](docs/analysis_phases.md) | Evaluator, Critic, Consistency Reviewer | EXISTS |
| [docs/knowledge_base.md](docs/knowledge_base.md) | Knowledge directory + file schemas | EXISTS |
| [docs/file_layout.md](docs/file_layout.md) | Complete run directory tree | EXISTS |
| [docs/harness.md](docs/harness.md) | ClaudeCode/OpenCode adapter layer | EXISTS |
| [docs/dashboard.md](docs/dashboard.md) | Dashboard tabs, API endpoints, scanner functions | EXISTS |
| [docs/communication.md](docs/communication.md) | Engine ↔ Dashboard file interface | EXISTS |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

All commands below assume the venv is active. Dependencies: `requirements.txt` at project root.

### Secrets and provider credentials (`.env`)

Secrets and provider endpoints live in `/home/sasha/Desktop/idea_evolve/.env` (project root,
gitignored via `.gitignore` entry `.env`). Everything in this file is loaded into the shell
environment before running the orchestrator or any harness CLI.

Current keys:

| Variable | Purpose |
|---|---|
| `MODELGATE_API_KEY` | OpenAI-compatible API key for the ModelGate provider (format `rp_...`). Referenced from `~/.config/opencode/opencode.json` as `{env:MODELGATE_API_KEY}`. |
| `MODELGATE_BASE_URL` | ModelGate base URL (`https://api.modelgate.ru/v1`). Currently hard-coded in opencode's provider config too; duplicated in `.env` so Python clients / future harnesses can read it. |

Load pattern (bash):

```bash
set -a; source .env; set +a
```

Future additions expected (do not commit real values): `ANTHROPIC_API_KEY` (used by `claude-code`
if we ever run against a non-default provider), `OPENAI_API_KEY` (for codex when/if added).

**Never commit `.env`.** If you add a new variable, document it in the table above.

### OpenCode provider setup (ModelGate)

OpenCode is configured at `~/.config/opencode/opencode.json` with a single provider `modelgate`
using the OpenAI-compatible `@ai-sdk/openai-compatible` driver. Registered models:
`modelgate/deepseek-v3.2`, `modelgate/gpt-4o`, `modelgate/claude-sonnet-4-5`. Add new models by
editing the `provider.modelgate.models` block (model id on left is what opencode sees as
`modelgate/<id>`). The provider reads its API key from `{env:MODELGATE_API_KEY}` so the
shell must have `.env` loaded before invoking `opencode run`.

## Running

**IMPORTANT: always `cd idea-evolve` first.** The orchestrator takes `.` as the project root
argument. Running it from the repo root passes the wrong root and fails preflight checks
(all required files appear missing). Log output to a file so you can monitor without blocking:

```bash
source venv/bin/activate
cd idea-evolve
python3 orchestrator.py . --problem gemm --single         # run gemm, latest attempt
python3 orchestrator.py . --problem gemm --new-attempt    # create new attempt
python3 orchestrator.py . --problem gemm --attempt attempt_002  # specific attempt
python3 orchestrator.py . --problem permcodes --new-attempt     # different problem
python3 orchestrator.py . --problem gemm --dry-run        # preview plan
python3 orchestrator.py . --problem gemm --start-gen 5    # resume from gen 5
```

Monitor a background run: `tail -f /tmp/run.log`.

**For long runs (GPU problems, multi-gen): launch with `nohup` and unbuffered stdout** so
the orchestrator survives terminal/harness disconnects. A bare `&` job is a child of the
shell that started it — when the shell dies (terminal closed, IDE-extension session
ended, `/compact` invoked in Claude Code, etc.) the orchestrator and its eval subprocesses
get SIGHUP'd. `nohup` detaches from the controlling terminal; `python3 -u` flushes stdout
per-line so `/tmp/run.log` is readable in real time instead of appearing empty for minutes.

```bash
set -a && source .env && set +a              # required if any agent uses opencode
source venv/bin/activate
cd idea-evolve
nohup python3 -u orchestrator.py . --problem strawberry --new-attempt --single \
    > /tmp/run.log 2>&1 & disown
echo "launched pid=$!"
tail -F /tmp/run.log                         # -F (capital) survives log rotation
```

Verify it's alive: `ps -ef | grep orchestrator.py | grep -v grep`. If you killed an
orchestrator mid-run, also clear stale state before relaunching:
`rm -f /tmp/idea_evolve_eval_queue.json /tmp/idea_evolve_gpu.lock`.

Two orchestrators can run simultaneously on different problems — each works entirely
inside its own `runs/{problem}/{attempt}/` directory with no shared state.

Current problem: **Sidon Sets (B₂ Sequences)** — find the largest Sidon set in {0, ..., 10000}.
Baseline score: **66** (greedy algorithm). **Target: 100** (≈√N theoretical bound).
A Sidon set has all pairwise sums distinct. Fitness = set size (higher is better).
Invalid solutions get sentinel score (0) per the general rule below.
Problem files at `idea-evolve/problems/sidon/`. Fitness direction read from `metrics.yaml`.
Helpers: `is_sidon`, `count_violations`, `differences`, `can_add`, `is_prime` in `helpers/core.py`.
Previous problems: Binary-Ternary GEMM (`problems/gemm/`), Permutation Codes M(8,5) (`problems/permcodes/`).

**Also available: Strawberry Disease Segmentation** (`problems/strawberry/`) — fine-tune YOLO11
for instance segmentation of 7 strawberry diseases, maximize mask mAP50 on the open test split
(743 images). Solutions are **full Python training scripts** (not config dicts) — agents can do
staged training, class weighting, custom augmentation, ensembles, etc.
Evaluation starts from exp5 best.pt (val mAP50=0.945) + 20 fine-tuning epochs (~3.6 min/eval).
GPU serialized via file lock in evaluate.py — safe even with parallel agents.
Target: beat proxy mAP50 ≈ 0.94 (current exp5 proxy baseline ~0.92-0.94).
Start: `python3 orchestrator.py . --problem strawberry --new-attempt`

## Dashboard

Web UI for tracking evolution runs, browsing solutions/knowledge, and visualizing the pipeline.

```bash
source venv/bin/activate
python dashboard/app.py              # http://localhost:5000
python dashboard/app.py --port 8080  # custom port
python dashboard/app.py --debug      # hot reload
```

Lives in `dashboard/`. Modular Flask app: `data/` (filesystem scanning), `routes/` (blueprints),
`templates/` (Jinja2 with tab partials), `static/` (CSS + JS). 6 tabs: Overview, Pipeline,
Architecture, Solutions, Knowledge, Reports. Auto-refreshes every 10s on Overview.
API endpoints at `/api/*` return JSON. See `dashboard/README.md` for full structure.

Dashboard reads fitness direction and decimals from `problems/{id}/metrics.yaml`. Scores display with
proper precision (4 decimals for this problem). Solutions table sorted best-first (respects
lower-is-better). Score source priority: `.score` sidecar → eval cache (by content hash).
Header comment fallback removed — it caused stale score inconsistencies.
Progression chart shows baseline from initial programs and target line with
direction indicator ("↓ better" / "↑ better"). Agent column shows full identifier (e.g.,
`explore_1` not just `explore`).

**Eval time + Started/Ended columns (Solutions tab).** Per-solution wall-clock evaluation
time plus the evaluation's start/end timestamps, sourced from `eval_time_s`,
`eval_started_at`, and `eval_ended_at` in `.score` files (and `eval_cache.json` by content
hash). All three populated when `metrics.yaml` has `track_eval_time: true` (sidon, gemm,
permcodes, strawberry all set it). Eval time renders as `ms` under 1s, `Ns.s` under a minute,
`Nm SSs` above. Started/Ended render as local `HH:MM:SS` with the full ISO-8601 UTC value in
the `title` tooltip; `--` when absent. All three are sortable — useful for spotting
fast-but-weak solutions, GPU queue waits, and evals that straddle long gaps. Wired through
[dashboard/data/scanner.py](idea-evolve/dashboard/data/scanner.py) `get_solutions()`,
rendered by [dashboard/static/js/app.js](idea-evolve/dashboard/static/js/app.js) `fmtEvalTime`
+ `fmtEvalStamp`, columns declared in
[dashboard/templates/tabs/solutions.html](idea-evolve/dashboard/templates/tabs/solutions.html).

**Multi-problem navigation:** Dashboard has a problem/attempt selector flyout panel in the
header (between logo and nav tabs). Click the breadcrumb to open the flyout, which shows
all problems with their attempts, summary stats, and status indicators. Selection stored
in localStorage. All API endpoints accept `?problem=X&attempt=Y` query params.
API endpoint: `GET /api/problems` returns all problems with attempts and summary stats.

**Annotated frontier:** The score progression chart has a toggleable "Frontier" button that
overlays annotated callouts on record-breaking solutions, showing agent name, score delta,
central ideas, and a descriptive label. Data from `GET /api/frontier`.

**Knowledge staleness:** Overview API returns `soa_staleness` (how many generations behind
the State of Affairs is) and `lifecycle_counts` (ideas by lifecycle stage). Pipeline tab
reads from `gen_progress.json` for durable per-agent status.

Dashboard has live orchestrator visibility via `history/run_state.json`. Header beacon shows
green (running), gray (idle), amber (stale >2min), or red (crashed PID). Overview tab shows
system status bar with phase/gen/elapsed. Pipeline tab shows per-agent status from orchestrator
(waiting/running/wrapping_up/done/failed) and recent errors. Refresh rate is dynamic: 10s when
orchestrator is running, 60s when idle.

## Architecture

The orchestrator is a stateless Python loop. All state lives in files. If it crashes, it resumes
from the last completed phase by inspecting which files exist (`phase_status()`).

**Generation loop (6 phases):**
1. **Architect** — reads system state, writes `manifest.yaml` + per-agent briefs to `briefs/genNNN/`
2. **Agent work sessions** — launched in parallel per `parallel_groups` in manifest. Each agent reads files, writes code, runs evaluate.py, iterates, writes debrief report. All in one session.
3. **Evaluator** — collects scores from `.score` files, extracts knowledge (ideas/patterns/facts), updates clusters, generates coverage matrix
4. **System Critic** — reads agent reports, identifies pipeline problems, writes recommendations
5. **Consistency Review** — every 3rd gen or on strategic shift: audits knowledge base, rewrites State of Affairs
6. **Finalize** — update rankings, population summary, score progression, detect user interventions

**Agents are launched as:** `npx @anthropic-ai/claude-code --print --model <model> --max-turns <N>`
with `--allowedTools Read,Write,Bash,Glob,Grep`. Each agent gets a lean prompt with file paths to read
(not inline content), so prompts stay small regardless of knowledge base size.

### Harness layer

Agent subprocesses are launched through a `HarnessAdapter` abstraction in
`idea-evolve/orchestrator_harness.py`. Two adapters are supported:

- **`ClaudeCodeAdapter`** (default) — `npx @anthropic-ai/claude-code --print`. Session ids are
  caller-assigned UUIDs. Wrap-up/debrief resumes via `--resume <uuid>`. Models from
  `CLAUDE_CODE_MODEL_MAP` (`opus|sonnet|haiku` → Anthropic model ids).
- **`OpenCodeAdapter`** — `opencode run --format json`. Session ids are **server-assigned**
  (`ses_<26chars>`) and emitted in the first JSON event on stdout. The adapter streams stdout
  in a reader thread so the id is captured before any potential timeout-kill, then raises
  `SessionTimeout(session_id=...)` so wrap-up/debrief can resume with `-s <ses_id>`.
  No `--max-turns` equivalent — wall-clock timeout is the only ceiling (warning logged once).
  Tool allowlist is translated into `OPENCODE_PERMISSION` env JSON (edit/bash/webfetch).

Selection is per-agent via `user/config.yaml`:

```yaml
harnesses:
  default: claude-code      # or: opencode
  per_agent: {}             # e.g. {explore: opencode, architect: claude-code}

models:
  opencode:                 # opencode alias → provider/model
    opus: modelgate/claude-sonnet-4-5
    sonnet: modelgate/minimax-m2.7
    haiku: modelgate/minimax-m2.7
```

`launch_claude_session()` / `resume_claude_session()` in `orchestrator.py` are thin shims
that dispatch to the configured adapter via `_get_adapter(agent_role)`. Call-site names kept
for legacy reasons; both accept an optional `agent_role` kwarg to resolve `per_agent` overrides.

**Resolution order** (per launch): `harnesses.per_agent[agent_role]` → `harnesses.default` →
`claude-code` (with one-line warning on unknown names).

**`per_agent` keys** accept the agent role names the orchestrator passes from call sites:
`architect`, `explore`, `exploit`, `genetic`, `full`, `research`, `experimentator`,
`evaluator`, `system_critic`, `consistency_reviewer`, `wrap_up`, `debrief_recovery`.
Any call site that does NOT pass `agent_role=` falls back to `harnesses.default` — so
flipping `default: opencode` is the simplest way to route "everything except one or two
roles" to opencode.

**Currently wired call sites** (pass `agent_role=` explicitly):
- `run_architect()` launch + wrap-up resume → `agent_role="architect"`

Other call sites (agent work, wrap-up, debrief, analysis) currently rely on
`harnesses.default`. If you need finer per-role routing beyond the architect
exception, thread `agent_role=<role>` into the launch sites in `run_single_agent()`
(work/wrap-up/debrief) and `run_analysis()` (evaluator / system_critic / consistency_reviewer).

### Pre-flight for the opencode harness

OpenCode reads its API key from the shell env (`{env:MODELGATE_API_KEY}` in
`~/.config/opencode/opencode.json`). Always load `.env` before launching the orchestrator
if any agent is routed to opencode:

```bash
set -a; source .env; set +a
cd idea-evolve && python3 orchestrator.py . --problem sidon --single
```

Without this, opencode exits silently with empty stdout and the adapter raises
`SessionError: opencode launch produced no sessionID in stdout`.

### Example: architect on claude-code, everything else on opencode

```yaml
architect_model: sonnet        # architect runs Claude Sonnet via claude-code

harnesses:
  default: opencode
  per_agent:
    architect: claude-code     # keep Claude-tuned prompt on Claude

models:
  opencode:
    opus:   modelgate/claude-sonnet-4-5
    sonnet: modelgate/minimax-m2.7
    haiku:  modelgate/minimax-m2.7
```

This is the configuration validated end-to-end on the permcodes problem
(single-generation run, 2026-04-15 attempt).

Contract tests live in `idea-evolve/tests/test_adapters.py`
(`cd idea-evolve && python3 -m pytest tests/test_adapters.py -v`).
Unit tests (7) always run. Integration tests (3) auto-skip if the `opencode` binary or
`MODELGATE_API_KEY` is absent.

## File Structure

### Current Layout (multi-problem, after migration)

```
idea-evolve/
├── orchestrator.py          # Stateless loop (~3200 lines)
├── agents/                  # Prompt templates (global, 10 files)
├── prompts/                 # Shared prompt fragments (global)
├── user/                    # config.yaml, initial_ideas.md, etc. (global)
│
├── problems/                # Problem definitions (read-only at runtime)
│   ├── gemm/                # description.md, evaluate.py, validate.py, metrics.yaml, helpers/
│   └── permcodes/           # same structure
│
└── runs/                    # All evolution data, scoped per problem+attempt
    └── gemm/
        └── attempt_001/     # Self-contained run with all state:
            ├── population/  #   genNNN/{agent_name}/sol*.py + .score
            ├── knowledge/   #   state_of_affairs.md, ideas/, clusters/, facts/, etc.
            ├── history/     #   generations/, all_scores.json, eval_cache.json, run_state.json
            ├── briefs/      #   genNNN/manifest.yaml, agent briefs, gen_progress.json
            ├── reports/     #   genNNN/agent_name.md (debrief reports)
            ├── feedback/    #   system_recommendations.md, system_analysis/, consistency_reviews/
            ├── workspace/   #   ephemeral agent workspaces (cleaned after each agent)
            └── papers/      #   research paper library
```

**No symlinks, no dot files.** The orchestrator sets `project_root = ctx.run_root` so
all functions operate inside the run directory. Global resources (`agents/`, `prompts/`,
`user/`) and problem files (`problems/{id}/`) are accessed via `_global()` and `_problem()`
helpers that read from `CTX`. This means **two orchestrators can run simultaneously**
on different problems without conflicts.

**Key file: `briefs/genNNN/gen_progress.json`** — durable per-generation progress
tracker (survives orchestrator restarts, unlike ephemeral `run_state.json`). Contains
per-agent status, PIDs, session IDs, per-phase completion status. Used by `run_single_agent()`
skip logic and dashboard pipeline tab.

## What Works

- **Architect debrief and failure reporting.** After each architect session, `architect_report.md`
  is copied from `briefs/genNNN/` to `reports/genNNN/architect.md`. The System Critic reads it
  automatically as part of `reports/genNNN/`. The next Architect gets it via `prev_gen_reports.md`.
  If the architect session times out, a wrap-up resume is attempted (300s). If the architect
  crashes or produces no manifest, the orchestrator writes a structured failure report to
  `reports/genNNN/architect.md` instead.
- **Three-phase timeout with session resume.** Work session runs with timeout T1 (default 900s)
  and gets a `--session-id`. If it times out without writing `report.md`, a **wrap-up message**
  is sent to the **same session** via `--resume` (same model, 900s) — the agent retains full
  memory of its work and is told to stop creating and evaluate/report. If the wrap-up also
  fails, a **debrief recovery** message resumes the same session (sonnet, 300s). Falls back to
  a new session only if no session_id exists. Work gets completed and knowledge is never lost.
- **Mandatory evaluate-immediately workflow.** Agent prompts (explore, exploit, full, genetic)
  and the orchestrator's global prompt context enforce: write one solution → run evaluate.py →
  verify `.score` file created → then move on. Prevents agents from batch-writing unevaluated
  solutions. Header comment `# fitness:` no longer used — `.score` sidecar is the only
  authoritative score source (alongside eval_cache by content hash).
- **Turn budgets from config.** `user/config.yaml` `max_turns:` section is authoritative.
  `DEFAULT_MAX_TURNS` in orchestrator.py is just a fallback if config is missing.
- **Timing tracking.** Every phase and agent records elapsed time to `history/timing.json`.
  The Architect sees recent timing data and can set per-agent `timeout` in `manifest.yaml`.
- **Invalid solutions get sentinel score.** If `validate.py` returns `is_valid: 0`, the fitness
  MUST be the `sentinel_value` from `metrics.yaml` (typically 0). No partial credit, no subset
  extraction, no rewarding near-misses. Only fully valid solutions receive a real score.
  This is a universal rule for all problems — every `validate.py` must enforce it.
- **Evaluation caching.** `evaluate.py` caches results by file content hash in `history/eval_cache.json`.
  Thread-safe with `fcntl` file locking for parallel agent access.
- **Live run state tracking.** `history/run_state.json` is written by the orchestrator at
  every phase transition and agent status change. Contains: PID, current gen/phase, per-agent
  status (waiting/running/wrapping_up/done/failed), error log. Thread-safe with fcntl locking.
  Dashboard reads it for real-time status beacon, dynamic refresh rates (10s when running,
  60s when idle), and per-agent pipeline visualization. Crash detection via PID liveness +
  staleness check (>120s without update). NOT a replacement for phase_status() resume logic —
  additive visibility layer only.
- **Stateless crash recovery.** `phase_status()` reconstructs position from file existence,
  with `gen_progress.json` as primary source (durable, written per-phase). Falls back to
  filesystem checks for backward compatibility.
- **Durable generation progress.** `briefs/genNNN/gen_progress.json` tracks per-agent
  completion status, PIDs, session IDs, and output move status. Survives orchestrator
  restarts (unlike ephemeral `run_state.json`). Used by `run_single_agent()` to skip
  completed agents and kill orphaned processes on resume.
- **Orphan process cleanup.** On restart, `_kill_generation_orphans()` reads `gen_progress.json`
  and kills any agent processes still listed as "running" (verified via `/proc/{pid}/cmdline`).
- **Multi-problem support.** `RunContext` dataclass separates global resources, problem
  definitions, and per-attempt run state. CLI accepts `--problem`, `--attempt`, `--new-attempt`.
  Legacy single-problem mode preserved when no `--problem` given.
- **Lean prompts.** File paths, not inline content. Stable prompt size across generations.
- **In-session debrief.** Agent writes `report.md` while it still remembers everything it tried.
- **Parallel groups.** `parallel_groups` in manifest → groups sequential, agents within group parallel.
- **Research/experiment routing.** Each agent type has its own output mover to the correct directory.
- **Initial knowledge bootstrap.** `initial_ideas.md`/`initial_facts.md` → proper YAML-frontmatter files before gen 1.
- **Gen-1 Evaluator bootstrap.** Special prompt instructions to write initial State of Affairs.
- **Manifest fallback + validation.** Invalid/missing YAML → default manifest generated.
- **Agent failure logging.** Failure reports written to `reports/` so next Architect knows.
- **Idea limits + staleness.** Evaluator gets current idea count + thresholds. Consistency Reviewer gets staleness config.
- **experiment_requests collection.** Full agent requests → `feedback/experiment_requests/` → Architect prompt.
- **Unified helpers directory.** All helpers live in `problem/helpers/`. The built-in problem
  helper (`compute_c`) is in `helpers/core.py` — import as `from helpers.core import compute_c`.
  Experimentator agents write new helpers to `output/helpers/`; the orchestrator validates
  (syntax, import blocklist, no top-level side effects) and deploys to `problem/helpers/`.
  All solution agents see available helpers via `_helpers_section()` in their prompt.
  `problem/helper.py` is a backward-compat shim that re-exports `compute_c` from `helpers/core.py`
  — old solutions still work, but new solutions should use `from helpers.core import compute_c`.
  See `problem/helpers/README.md` for the full index.
- **Evaluation time tracking — always on.** Every `evaluate.py` unconditionally records
  `eval_time_s` (wall-clock seconds), `eval_started_at`, and `eval_ended_at` (ISO-8601 UTC)
  in every `.score` sidecar and eval cache entry — including error results. If an exception
  occurs before measurement starts (e.g. import failure) the three fields are omitted from
  that result. Cached results return the original measured values — not re-measured — so
  timestamps reflect the real run, not cache hits.
  LLM prompt inclusion is controlled by `show_eval_time_in_prompts: true` in `metrics.yaml`
  (default true, recommended for all problems). The dashboard always shows Eval Time /
  Started / Ended columns regardless of this flag — it reads `.score` files directly.
  Old flag `track_eval_time` is removed; if a problem yaml still has it, it is silently
  ignored (timing collection is no longer conditional).
- **Zombie-process prevention (4-layer defense).** Validated on strawberry after an orphaned
  YOLO training held the GPU post-SIGKILL.
  1. **`os.execve` re-exec for venvs.** GPU problems re-exec into the first_project venv via
     `os.execve(VENV_PYTHON, [VENV_PYTHON] + sys.argv, env)` — REPLACES the current process.
     Never `subprocess.run([VENV_PYTHON, ...])` — that forks a grandchild which survives
     `killpg` and keeps the GPU busy. See `problems/strawberry/evaluate.py`.
  2. **Process-group isolation + `killpg`.** `safe_run()` and all adapter `Popen` calls use
     `start_new_session=True`. On timeout/kill, the orchestrator calls `os.killpg(pid, SIGTERM)`
     then `SIGKILL` — the entire tree goes. Lives in `orchestrator_harness.py`.
  3. **`pdeathsig` backstop.** `_set_pdeathsig()` is a `preexec_fn` that calls
     `prctl(PR_SET_PDEATHSIG, SIGKILL)` — if the parent dies for any reason (even an unclean
     crash that bypasses `killpg`), the child receives SIGKILL from the kernel. Attached to
     both ClaudeCode and OpenCode adapter Popen calls, and to `safe_run()`.
  4. **Subreaper on orchestrator.** `set_subreaper()` called once in `main()` marks the
     orchestrator with `PR_SET_CHILD_SUBREAPER=1`. Orphaned descendants reparent to the
     orchestrator (not PID 1), so `wait()`/`killpg` can still reach them across process-tree
     gaps.

  Use `safe_run()` (exported from `orchestrator_harness`) as a drop-in replacement for
  `subprocess.run()` anywhere the orchestrator spawns a subprocess that might hold resources
  (GPU, file locks, sockets). Bootstrap baseline evaluations use `safe_run(timeout=600)` —
  60s was too short for 3.6-min YOLO trainings and caused broken-pipe failures.
- **Multi-metric support.** Problems declare a primary metric (`is_primary: true`) plus any
  number of auxiliary metrics in `metrics.yaml`. Auxiliary metrics pass through `entrypoint()`
  → evaluate.py → `.score` sidecar + `eval_cache.json` automatically — no registration step.
  Strawberry uses this for `mAP50_95`, `F1`, `precision`, `recall`, `per_class` (structured),
  `tta` (flag), `train_time_s`. Set `include_in_prompts: true` to surface a metric in agent
  prompts/summaries; omit to store silently for developer diagnostics. See
  [docs/problem_design_guide.md](docs/problem_design_guide.md) §4 for the full pattern.
- **Mid-run metric addition.** Adding a metric after a run is live does NOT require
  re-evaluating the population:
  1. Add the metric spec to `problems/<id>/metrics.yaml`.
  2. Update `entrypoint()` / `evaluate.py` to compute and return it.
  3. The orchestrator treats missing auxiliary metrics on old `.score` files as sentinel
     (renders as `—` in summaries). Primary fitness is never retroactively perturbed.
  4. To fill in the new metric for specific solutions, delete their `.score` sidecar AND
     their `eval_cache.json` entry (by content hash); the next `evaluate.py` recomputes.
  Do NOT bulk-rerun — wastes compute, perturbs rankings.
- **Architect-driven scheduling for resource-contended problems.** `metrics.yaml` declares
  `concurrency: serial|parallel` (default `parallel`). The orchestrator passes the mode to
  the architect prompt context. The architect writes `parallel_groups` (groups sequential,
  agents within parallel) — the orchestrator HONORS what it writes via
  `_normalize_parallel_groups()` and only falls back to `[[all]]` on malformed YAML.
  Single-element groups serialize, multi-element groups parallelize. Strawberry uses
  `concurrency: serial` (one solution agent per group) so GPU evals never collide.
  See [docs/problem_design_guide.md](docs/problem_design_guide.md) §9.1.
- **Universal eval queue + same-agent kill contract.** Every `evaluate.py` enqueues itself
  in `/tmp/idea_evolve_eval_queue.json` (under `fcntl.flock`) and on entry calls
  `eval_queue.kill_stale_same_agent(agent_name, kill_hook=...)`. The kill check enforces
  8 invariants (queue presence, agent name match, pid alive, pgid match,
  `/proc/<pid>/cmdline` contains `evaluate.py`, env shows the same `IDEA_EVOLVE_AGENT_NAME`,
  per-agent fcntl mutex held); on any mismatch it **fails open** — never kills the wrong
  process. Per-problem `eval_hooks.py` defines `kill_eval` (default = killpg SIGTERM →
  grace → SIGKILL); strawberry's hook waits for the GPU lock to be released and logs to
  `/tmp/idea_evolve_strawberry/kill_log.json`. Identity threaded via
  `IDEA_EVOLVE_AGENT_NAME/PROBLEM/ATTEMPT/RUN_ROOT` env vars in `orchestrator_harness._build_env`.
- **Agent-readable narrative proc_logs.** `problems/_shared/proc_log.Writer` writes
  markdown timelines under `runs/<problem>/<attempt>/proc_logs/<ts>_<agent>_<kind>_<pid>.md`
  for every non-trivial process outcome. Append-only line-buffered with `os.fsync` so they
  survive SIGKILL up to the last line. On failure, evaluate.py invokes
  `problems/<id>/eval_hooks.py:diagnose_failure(error_class, message, context)` and embeds
  the markdown hint in the log under "What to try next". The `.score` sidecar gains a
  `log_path` field on failure. Retention: 200 per attempt, `sticky: true` excluded from prune.
  Agent prompts ([agents/_shared_eval_contract.md](idea-evolve/agents/_shared_eval_contract.md))
  instruct agents to read `log_path` before retrying.
- **Checkpoint archive + reproduction.** `metrics.yaml: archive_checkpoints: true` causes
  `helpers/core.archive_checkpoint(content_hash, run_root)` to copy the trained `best.pt`
  to `runs/<problem>/<attempt>/checkpoints/<hash>.pt` (LRU-pruned to `checkpoint_retention`).
  `evaluate.py --reproduce <hash>` re-runs only the eval phase against the archived
  checkpoint via `helpers/core.evaluate_from_checkpoint`. Closes the "is this baseline
  reproducible?" question without retraining.
- **Single source of truth for constants.** All cross-cutting paths/env-vars/timeouts
  live in `problems/_shared/constants.py` (`EVAL_QUEUE_PATH`, `GPU_LOCK_PATH`,
  `KILL_GRACE_SECONDS`, `KILL_DEADLINE_SECONDS`, `DEFAULT_CHECKPOINT_RETENTION`,
  `DEFAULT_CONCURRENCY`, `ENV_AGENT_NAME`, `ENV_PROBLEM`, `ENV_ATTEMPT`). Imported by
  every evaluate.py + helper + orchestrator module. The consistency checker
  (`scripts/check_docs_consistency.py`) walks docs and asserts referenced constants resolve.
- **Agent-readable disk artifacts.** Large or noisy evaluation outputs (training logs,
  per-class breakdowns, crash traces) go to stable `/tmp/idea_evolve_<problem>/...` paths,
  not into agent prompts. Agents read them via Bash/Read only when they have a specific
  question. Strawberry writes `last_train_logs/results.csv`, `last_train_logs/args.yaml`,
  `last_train_logs/crash_tail.log`, `last_per_class.json`. The paths are documented in
  `description.md` so agents know where to look. Keeps prompts lean (mitigates SCALE-7)
  while preserving investigability.

---

# ALL KNOWN PROBLEMS

## AUDIT FINDINGS — discovered by Claude during 2026-04-15 consistency review

These are issues I (Claude) found while implementing the GPU-contention prevention plan
and auditing the system for doc/code consistency. They were NOT user-reported — they
surfaced during my own review pass and are recorded here so they don't get lost.

### [AUDIT-1] ~~CLAUDE.md doc table referenced 8 nonexistent files~~ — FIXED
All 9 docs now exist in `docs/` (repo root). `problem_design_guide.md` was moved from
`idea-evolve/docs/` to `docs/`; the other 8 (`architect.md`, `agents.md`, etc.) were
created at `docs/`. All table entries updated to `docs/` paths and marked EXISTS.

### [AUDIT-2] Architect prompt was missing the per-problem `concurrency:` mode
The orchestrator had a `concurrency_mode(project_root)` helper but never injected the
result into the architect's prompt. The architect therefore couldn't honor the
"serial-eval problem → one agent per group" rule from the plan, regardless of what
`metrics.yaml` declared. Found by grepping the architect prompt for `concurrency` and
getting zero hits. **Fixed in this session** by adding the `## Evaluation concurrency
for this problem` block to the architect prompt builder in `orchestrator.py`.

### [AUDIT-3] Solution agents were told to read `_shared_eval_contract.md` — but never received its content
The plan called for `_shared_eval_contract.md` to be referenced by `explore.md`,
`exploit.md`, `full.md`, `genetic.md`. The reference text was added — but the orchestrator
never inlined the contract content into the prompt sent to the agent. Agents would have
seen "follow the shared eval contract" with no contract attached. Found by reading
`build_agent_prompt` and confirming no read of `_shared_eval_contract.md`. **Fixed in
this session** by adding `SOLUTION_AGENTS = {...}` gating in `orchestrator.py` that
inlines the contract under a `# SHARED EVALUATION CONTRACT (mandatory rules)` header.

### [AUDIT-4] No unit tests written for new modules
The plan's verification section called for 6 test files (`test_concurrency_mode.py`,
`test_run_agents_groups.py`, `test_eval_queue.py`, `test_kill_hook_default.py`,
`test_archive_checkpoint.py`, `test_docs_consistency.py`). Zero were written. The kill
mechanism — the most dangerous new code — has no unit test exercising the 8 safety
invariants. The consistency checker is wired up and passes, but its own test would
catch regressions. **Action needed:** write at least `test_eval_queue.py` and
`test_docs_consistency.py` before the next strawberry run.

### [AUDIT-5] Kill mechanism never exercised end-to-end on real YOLO process tree
`eval_hooks.py` for strawberry was implemented and the safety invariants are coded, but
no integration test was run that:
  1. Launches `evaluate.py` on a real strawberry solution.
  2. From a second shell with the same `IDEA_EVOLVE_AGENT_NAME`, launches a second
     `evaluate.py`.
  3. Confirms the first process tree (parent + ultralytics dataloader workers) dies,
     the GPU lock is released, and the new eval succeeds.
The plan's "Kill-hook test" (verification step 4) is unverified. First real strawberry
generation will be the production test of this code. Recommendation: run with
`--single` and `--new-attempt` first.

### [AUDIT-6] Strawberry attempt_001 evidence is uncommitted but still on disk
Per `git status`, `runs/strawberry/attempt_001/` has uncommitted modifications and
deletions across knowledge, history, briefs, and workspace. It documents the
3-generation GPU contention failure that motivated this plan. Recommendation: rename
to `_attempt_001_pre_kill_contract/` (preserves the failure trail) and start
`attempt_002` for the first run with the new contracts. Do NOT delete — the gen-001
score 0.8328 is unreproducible and the proc_logs from a fresh run will be the first
real evidence the kill contract works.

## BUGS — will break things

### [BUG-1] ~~Idea lifecycle moves leave ghost files~~ — FIXED
Fixed: `_remove_from_other_lifecycles()` now deletes old copies from all other lifecycle dirs
when an idea or pattern is moved to a new lifecycle directory.

### [BUG-2] ~~Negative scores enter rankings~~ — FIXED
Fixed: `update_rankings()` now filters `score > 0`.

### [BUG-3] ~~validate.py is O(N²) with Python loops~~ — N/A
Problem changed to First Autocorrelation Inequality. New validate.py uses FFT (O(N log N)).
Also mitigated by SCALE-8 eval caching.

### [BUG-4] ~~Brief paths are relative~~ — FIXED
Fixed: `_absolutize_brief_paths()` post-processes all briefs after the Architect writes them,
converting relative paths to absolute.

### [BUG-5] ~~Partial evaluator work is lost~~ — FIXED
Fixed: `phase_status()` now checks for any meaningful output files (generation_snapshot,
new_ideas, updated_ideas), not just the final report.

### [BUG-6] ~~Workspace cleanup destroys evidence~~ — FIXED
Fixed: Cleanup only runs on full success (both session and output move). On failure,
workspace is preserved for debugging.

### [BUG-7] ~~Evaluator writes `status:` but orchestrator reads `lifecycle:`~~ — FIXED
The evaluator template documented `status: active|established|...` but `_read_frontmatter_field()`
and all orchestrator routing read the `lifecycle` field. Ideas always landed in `active/`
regardless of evaluator intent. Fixed: evaluator.md and consistency_review.md now use `lifecycle`.
Orchestrator also falls back to reading `status` if `lifecycle` is missing (belt and suspenders).

### [BUG-8] ~~explore.md shows wrong evaluate.py invocation~~ — FIXED
Template said `python evaluate.py --solution output/sol01.py` but evaluate.py takes a positional
arg. Fixed to `python3 evaluate.py output/sol01.py`.

### [BUG-9] ~~Agent templates use `# score:` but orchestrator reads `# fitness:`~~ — FIXED
explore.md and exploit.md showed `# score: 0.612` header format but `_extract_score()` searched
for the primary metric name (`fitness`). Fixed: templates now show `# fitness:` header.
Also added `score` as a fallback key in `_extract_score()` for robustness.

### [BUG-10] ~~System critic template references nonexistent files~~ — FIXED
Template referenced `generator_log.md`, `pipeline_config.yaml`, and `generation_history/`
which don't exist. Fixed to reference actual paths: `reports/genNNN/`, `user/config.yaml`,
`history/generations/`.

### [BUG-11] ~~Orphan child processes after timeout~~ — FIXED
`subprocess.run()` with timeout sent SIGKILL to `npx` but grandchild node processes survived.
Fixed: `launch_claude_session` now uses `start_new_session=True` to create a process group,
then kills the entire group (`os.killpg`) on timeout. SIGTERM first, SIGKILL fallback.

### [BUG-12] ~~launch_claude_session swallowed errors — crash debrief never triggered~~ — FIXED
The function caught all exceptions internally and returned `""`. Agent crash detection code
(`work_error`) never triggered. Fixed: function now raises `SessionTimeout` or `SessionError`.
Callers catch these explicitly.

### [BUG-13] ~~phase_status missed evaluator completion when only report.md written~~ — FIXED
If evaluator wrote `report.md` (debrief) but not `evaluator_report.md`, `phase_status()` didn't
detect completion. Fixed: now also checks for `evaluator_debrief.md` in reports/ and `report.md`
in workspace output.

### [BUG-14] ~~Evaluator snapshot blocks finalize timing data~~ — FIXED
If evaluator wrote `generation_snapshot.md`, finalize skipped its own snapshot (with timing).
Fixed: finalize now appends timing section to existing snapshot instead of skipping.

### [BUG-15] ~~`inf` written to score_progression for minimize problems~~ — FIXED
When no valid solutions exist, `best_score` was `float("inf")` for minimize problems. Written
directly to progression file. Fixed: scores of 0.0 or non-finite values display as `--`.

### [BUG-16] ~~Valid solution count used `score > 0` heuristic~~ — FIXED
Population summary counted "valid" solutions by checking `score > 0`. Fixed: now reads
`is_valid` from `.score` JSON files.

### [BUG-17] ~~Evaluator confused about report.md vs evaluator_report.md~~ — FIXED
Debrief instructions pointed to `report.md` while evaluator template said `evaluator_report.md`.
Two files with different routing. Fixed: evaluator's debrief instruction now points to
`evaluator_report.md` so there's one canonical output file.

### [BUG-18] ~~Bootstrap idea schema mismatched evaluator template schema~~ — FIXED
Bootstrap wrote `certainty`, `solutions`, `stats` (nested), `related`. Evaluator template
documents `confidence`, `supported_by`, `contradicted_by`, `related_ideas`, `cluster`.
Fixed: bootstrap now writes the same fields as the evaluator template.

### [BUG-19] ~~`debrief_max_turns` in timeouts section but is a turn count~~ — FIXED
`debrief_max_turns` was under `timeouts:` config section and retrieved via `get_timeout()`.
Moved to `max_turns:` section as `debrief_recovery: 20` and read via `get_max_turns()`.

### [BUG-20] ~~`name:` vs `title:` field inconsistency across frontmatter~~ — FIXED
Bootstrap facts used `title:`, evaluator template uses `name:`. Dashboard read `title:` only.
Fixed: all bootstrap files now use `name:` (matching evaluator template). Dashboard scanner
reads `name` with `title` as fallback for backward compat.

### [BUG-21] ~~Evaluator template describes single-solution workflow~~ — FIXED
Step 1 said "Re-run evaluate.py on the solution" (singular) but evaluator processes all
solutions in a generation. Fixed to say "each solution in this generation's population."

### [BUG-22] ~~`proc.wait()` after SIGKILL could hang without timeout~~ — FIXED
After SIGKILL to process group, `proc.wait()` had no timeout. Added `timeout=5`.

### [BUG-23] ~~`significant_change` field in metrics.yaml unused~~ — FIXED
Was defined but never read. Now used in `_update_score_progression()` to mark trivial deltas
with `~` and show improvement direction in the progression table.

### [BUG-24] ~~Agent prompt lists `best.py` at gen 1 when it doesn't exist~~ — FIXED
Agents wasted a turn trying to read nonexistent symlink. Now only listed for gen 2+.

### [BUG-25] ~~`knowledge_hierarchy` and `idea_limits` config unclear if enforced~~ — FIXED
Added comments clarifying these are advisory (passed to agents as guidance text, not enforced
programmatically by the orchestrator).

### [BUG-26] ~~`all_scores.json` written without file locking~~ — FIXED
`update_rankings()` read and wrote `all_scores.json` with plain `write_text()` while
`_record_timing()` used `fcntl.flock()`. Race possible on crash-resume.
Fixed: `all_scores.json` writes now use `fcntl.flock()` matching timing.json pattern.

### [BUG-27] ~~`_extract_score()` hardcoded `"fitness"` fallback~~ — FIXED
When `.score` JSON didn't contain `metric_name`, function fell back to hardcoded `"fitness"`
instead of trying common metric names. Fixed: now tries `["fitness", "score"]` as fallbacks.

### [BUG-28] ~~`_fix_orphaned_cluster_refs()` used fragile string replacement~~ — FIXED
`frontmatter.replace(f"cluster: {cluster_val}", ...)` could corrupt unrelated fields if
the cluster name appeared elsewhere in frontmatter. Fixed: uses `re.sub()` with `^cluster:`
anchored regex to target only the YAML field.

### [BUG-29] ~~Non-finite scores could enter rankings~~ — FIXED
`inf` and `nan` scores passed through the filter in `update_rankings()`. Fixed: added
`math.isfinite(score)` check before all other score filters.

### [BUG-30] ~~`consistency_review_interval: 0` caused `ZeroDivisionError`~~ — FIXED
`gen % interval` with interval=0 crashed. Fixed: clamp interval to minimum 3 if < 1.

### [BUG-31] ~~Duplicate agent names in `parallel_groups` launched same agent twice~~ — FIXED
If Architect wrote `["explore_1", "explore_1"]`, both launched and second overwrote first.
Fixed: agent names deduplicated within each group before launching.

### [BUG-32] ~~Empty manifest silently ran zero agents~~ — FIXED
If manifest YAML loaded as `{}`, `agents` list was empty and no agents ran with no error.
Fallback only triggered on YAML parse exceptions, not empty-but-valid YAML.
Fixed: check for empty/missing agents list and regenerate default manifest.

### [BUG-33] ~~`consistency_review.md` template listed wrong file names~~ — FIXED
Inputs section referenced `evaluator_report.md`, `system_analysis.md`, `agent_gaps.md`,
`previous_state_of_affairs.md` — none exist under those names. Fixed to actual paths.

### [BUG-34] ~~`consistency_review.md` outputs missing `output/` prefix~~ — FIXED
Output table listed `state_of_affairs.md` instead of `output/state_of_affairs.md`.
Fixed: all output paths now include `output/` prefix matching orchestrator expectations.

### [BUG-35] ~~`architect.md` contradicted itself on path format~~ — FIXED
Line 93 said relative paths, line 120 said absolute. Orchestrator post-processes
relative→absolute. Fixed: template now consistently says relative paths.

### [BUG-36] ~~`evaluator.md` missing SCALE-4 coverage matrix cap~~ — FIXED
Template showed unbounded table format without mentioning the cap-to-30 sparse format rule.
Fixed: added scale rule note directly in the template.

### [BUG-37] ~~`exploit.md` contained Cyrillic text~~ — FIXED
"Честно скажи:" in an English template. Fixed to "Be honest:".

### [BUG-38] ~~`experimentator.md` didn't document `report.md` as output~~ — FIXED
Debrief system expects `output/report.md` from all agents but template didn't mention it.
Fixed: added `report.md` to the output format section.

### [BUG-39] ~~`_extract_score()` didn't consult eval cache~~ — FIXED
Score extraction used `.score` sidecar → header comment only. If an agent forgot to save
the `.score` file but `evaluate.py` cached the result, the score was lost. Fixed: now checks
eval cache (by content hash) as second priority after `.score` sidecar.

### [BUG-40] ~~Brief path absolutization missed `papers/`, `prompts/`, `dashboard/`~~ — FIXED
`_absolutize_brief_paths()` only converted known prefixes. Paths like `papers/summaries/X.md`
passed through as relative. Fixed: added `papers/`, `prompts/`, `dashboard/` to prefix list.

### [BUG-41] ~~No startup validation of required files~~ — FIXED
Orchestrator only checked `description.md` and `evaluate.py`. Missing `validate.py` or agent
templates caused cryptic errors deep in runs. Fixed: `_preflight_check()` validates all
required files at startup. Result cached by file mtimes so re-runs are instant.

### [BUG-42] ~~`phase_status()` declared `agents_done` after any single agent output~~ — FIXED
On crash-resume, one file in `population/genNNN/` triggered `agents_done`, skipping remaining
agents. Fixed: now reads manifest to count planned agents, checks each one has output.
Returns `planned` (triggering re-run) if some agents are incomplete. Falls back to old
behavior only if manifest is missing/corrupt.

### [BUG-43] ~~`move_research_outputs()` didn't copy solutions to population~~ — FIXED
Research agents that produced solutions (`sol*.py` + `.score`) had them routed only to
`knowledge/research/` — not to `population/`. Rankings and dashboard never saw them.
Fixed: now copies all `.py`, `.score`, and `.md` files to `population/genNNN/research_N/`.

### [BUG-44] ~~`move_evaluator_outputs()` missing `mkdir` for clusters and generations dirs~~ — FIXED
On first run, `knowledge/clusters/` and `history/generations/` didn't exist. `shutil.copy2()`
to nonexistent dirs raised `FileNotFoundError`. Fixed: added `mkdir(parents=True, exist_ok=True)`
before copying to clusters dir and generations dir.

### [BUG-46] ~~`phase_status()` skips agents when evaluator workspace exists from a bad prior run~~ — FIXED
When agents fail to launch (e.g. opencode binary not on PATH) the orchestrator may still
advance to the evaluator phase and produce evaluator workspace output. On restart, even after
gen_progress.json is cleaned, `phase_status()` finds the evaluator workspace and returns
`"evaluator_done"`, skipping agents entirely. Root cause: the manifest-based agent check
fell through to legacy filesystem fallbacks when 0 agents were complete. Fixed: if the
manifest check finds fewer than all agents complete, always return `"planned"` (even for
0 completed) instead of falling through to fallbacks that can't distinguish evaluator output
from agent output.

### [BUG-45] ~~Orphaned architect writes partial manifest; restarted orchestrator uses it~~ — FIXED
If the orchestrator is killed mid-architect-session, the architect process becomes an orphan
and keeps running. It may have already written an intermediate `manifest.yaml` (e.g. with only
one agent in group 1). On restart, `phase_status()` sees the manifest and returns `"planned"`,
skipping the architect entirely. `run_agents()` then reads the partial manifest and launches
fewer agents than intended — all remaining agents in later sequential groups never run until
group 1 finishes. Meanwhile the orphaned architect may overwrite the manifest again, leaving
the on-disk version looking correct and making the bug invisible after the fact.
Fixed: `run_architect()` now touches `briefs/genNNN/.architect_done` after the session
completes and all post-processing finishes. `phase_status()` checks for this sentinel before
trusting the manifest — if manifest exists but `.architect_done` is absent, returns
`"not_started"` so the architect re-runs cleanly.

## SCALING — surfaces after gen 10-15

### [SCALE-1] ~~Evaluator turn budget exhaustion~~ — FIXED
Fixed: Default max_turns bumped to 150. Pre-concatenated knowledge dump (`knowledge_dump.md`)
written to evaluator workspace before launch — evaluator reads one file instead of dozens.

### [SCALE-2] ~~update_rankings() rescans ALL generations~~ — FIXED
Fixed: `history/all_scores.json` caches all known scores. Only the new generation is scanned.

### [SCALE-3] ~~system_recommendations.md overwritten~~ — FIXED
Fixed: Previous version archived to `feedback/system_recommendations_archive/genNNN.md` before overwriting.

### [SCALE-4] ~~Coverage matrix grows O(N²)~~ — FIXED
Fixed: Evaluator prompt now instructs to cap matrix to top 30 most-used ideas and use sparse format.

### [SCALE-5] ~~Experiment results never consolidated~~ — FIXED
Fixed: Evaluator prompt now includes guidance to consolidate experiments older than 3 gens
into patterns/facts.

### [SCALE-6] ~~Cluster merge orphans idea back-references~~ — FIXED
Fixed: `_fix_orphaned_cluster_refs()` scans all ideas when clusters are removed/merged and
updates orphaned `cluster:` frontmatter to `unclustered`.

### [SCALE-7] Agent context window fills up during long sessions
With 150 max turns, an agent's context window accumulates tool results (file reads, bash outputs).
By turn 100+, earlier work may be compressed or lost. The agent forgets approaches it tried
at turn 10. This is inherent to Claude Code sessions but worsens with more complex knowledge bases.

**No fix** — fundamental limitation. Mitigate by keeping file reads targeted.

### [SCALE-8] ~~No evaluation caching~~ — FIXED
Fixed: `evaluate.py` caches results in `history/eval_cache.json` keyed by SHA-256 of file content.
Identical solutions return cached scores instantly.

### [SCALE-9] ~~Knowledge dump truncates without marker~~ — FIXED
`_preconcat_knowledge` truncated idea/cluster/pattern content at char limits but didn't indicate
truncation. Evaluator could read half an idea body thinking it was complete. Fixed: truncated
entries now end with `[TRUNCATED — read full file for details]`.

### [SCALE-10] Eval cache grows unbounded
`history/eval_cache.json` never prunes old entries. After hundreds of evaluations, file grows
indefinitely. **Not yet fixed** — low priority, can be pruned manually.

### [SCALE-11] `all_scores.json` stat-checks every cached path each generation
`update_rankings()` calls `Path.exists()` on every cached score entry. O(N) stat calls per
generation. **Not yet fixed** — low priority until 500+ solutions.

### [SCALE-12] ~~Experiment requests accumulate across all generations~~ — FIXED
Architect prompt listed ALL experiment requests from ALL generations via `rglob`. By gen 15+,
dozens of stale requests. Fixed: now only shows last 2 generations' requests.

### [SCALE-13] ~~Architect reads all prev-gen reports unbounded~~ — FIXED
With 8 agents producing 2-5K char reports, Architect spent many turns just reading.
Fixed: `_preconcat_prev_reports()` writes a single `prev_gen_reports.md` to briefs dir
(each report capped at 3K chars, total capped at 40K). Architect reads one file.

### [SCALE-14] ~~Knowledge dump can grow unbounded~~ — FIXED
With 100+ ideas × 2000 chars each, the evaluator's `knowledge_dump.md` could reach 200K+.
Fixed: total dump capped at 80K chars with truncation marker.

### [SCALE-15] ~~`agents.*.enabled` config never enforced~~ — FIXED
Config had `enabled: true/false` per agent type but orchestrator ignored it. Fixed:
`run_agents()` now filters manifest agents against config `enabled` flag before launching.

## DESIGN — architectural gaps vs spec

### [DESIGN-1] Write isolation is advisory only
The spec says agents write ONLY to `output/`. We tell them to in the prompt but nothing
enforces it. A misbehaving agent could corrupt `knowledge/`, `population/`, or any file.

**Risk:** Medium. Claude Code agents generally follow instructions. But a confused agent
could overwrite `state_of_affairs.md` directly instead of writing to its output dir.

**Future work**: enforce write isolation technically so agents physically cannot write outside
their workspace, regardless of what the LLM decides to do. Possible approaches:

- **Linux namespaces / bind mounts** — mount the agent's `workspace/genNNN_agentname/` as
  a writable overlay; mount everything else read-only. No code changes inside agents needed.
  Cleanest option. Requires `unshare` or a small wrapper script launched before `npx`.
- **`inotifywait` watcher** — background process watches the run dir tree and immediately
  reverts (deletes) any write outside the agent's `output/` dir. Simpler to implement but
  reactive, not preventive — a fast agent could do damage before the revert lands.
- **Restricted shell wrapper** — intercept shell commands via `LD_PRELOAD` or a custom
  `bash` wrapper that filters `open()` calls with `O_WRONLY`/`O_RDWR` outside the allowed
  path. Complex and fragile across Python versions.

Recommended path: Linux bind mounts via `unshare --mount`. Launch each agent inside a
namespace where only `workspace/genNNN_agentname/` is writable. The orchestrator already
uses `start_new_session=True` when spawning agents, so adding `unshare` to the command
prefix is straightforward. Not done yet — do as a dedicated hardening pass.

### [DESIGN-2] No solution lineage tracking
When Exploit refines `gen005_explore_1/sol01.py`, it produces a new `sol01.py` with no
record of what it descended from. The solution-idea map tracks which ideas a solution uses,
but not parent→child relationships between solutions. The Architect can't distinguish
independent solutions from derivatives when planning Genetic crossovers.

### [DESIGN-3] Knowledge files have no version history
When the Evaluator updates `idea_042.md`, it overwrites the file. No diff, no changelog.
The Consistency Reviewer audits current state but can't see how knowledge evolved.
Git would solve this but the project isn't a repo.

### [DESIGN-4] Architect is a single point of failure
If the Architect writes poor briefs, all agents in that generation suffer. Debrief reports
feed back to the NEXT generation's Architect, but there's no mid-generation correction.
A bad Architect turn wastes an entire generation of compute.

### [DESIGN-5] No cost awareness or budget management
Each generation: 1 Architect (opus) + 3-8 agents (sonnet) + 1 Evaluator (opus) +
1 Critic (sonnet) + possibly 1 Consistency Reviewer (opus). Rough cost: $1-5 per generation.
30-gen run: **$30-150+**. No budget limit, no throttle, no "this gen was expensive, reduce next."

### [DESIGN-6] No semantic deduplication of solutions
Two Explore agents might independently arrive at the same approach (e.g., both use D₁₁ root system).
The system treats them as distinct. The Evaluator should catch this during idea matching, but
compute is wasted on redundant work that the coverage map was supposed to prevent.

### [DESIGN-7] "Read broadly" principle vs lean prompts tension
The spec says agents can "read the entire project file system." Our lean prompts list specific
files. An agent that follows the list strictly might miss relevant files not mentioned
(e.g., a research finding from 5 gens ago, an experiment result in a non-obvious directory).
The agent CAN read any file, but needs to know to look.

### [DESIGN-8] No rate limiting or backoff
10 parallel Claude Code sessions × 150 turns = potentially 1500 near-simultaneous API calls.
Could trigger API rate limits depending on tier, causing sessions to fail or degrade.

### [DESIGN-9] No warm-up / cold-start handling for gen 1-2
Gen 1 has no clusters, no coverage matrix, no solution-idea map, no population summary.
All agents get "no data yet" placeholders. The Evaluator must create all knowledge structures
from scratch with no examples. Gen 1-2 knowledge quality may be poor and set a bad foundation.

### [DESIGN-12] Model tier aliases are not semantically enforced across harnesses
The `opus`/`sonnet`/`haiku` aliases mean different things depending on the harness. For
`claude-code`, they map to actual Claude model tiers with meaningful capability differences
(Opus > Sonnet > Haiku). For `opencode`, the aliases currently all point to
`modelgate/minimax-m2.7` — so every agent gets the same model regardless of tier. This means
high-reasoning roles (evaluator, experimentator, architect) that are supposed to get Opus
are silently downgraded. Additionally, different providers have different strengths — a
model that works well for code generation (Minimax) may not reason as well as Claude for
knowledge synthesis (evaluator) or strategic planning (architect).

**Problem:** We have no validation, warning, or per-role model routing that accounts for the
actual capabilities of non-Claude models. The `models.opencode:` block is purely a lookup
table with no quality signal.

**Future work:**
- Distinguish "reasoning-heavy" roles (architect, evaluator, consistency_reviewer,
  experimentator) from "workhorse" roles (explore, exploit, genetic, full, research)
- Allow separate `models.opencode.high_reasoning` and `models.opencode.workhorse` keys, or
  full per-role model overrides in config
- Log a warning when a role configured for `opus` is mapped to the same model as `haiku`
- Test non-Claude models on evaluator/architect tasks to measure quality regression

**Current workaround:** Keep architect on `claude-code` (real Claude Sonnet) via
`per_agent.architect: claude-code`. All other roles use Minimax via opencode.

### [DESIGN-11] ~~Architect skips experimentator for recurring helper requests~~ — MITIGATED
When `system_recommendations.md` asks for a shared helper (e.g. SA calibration utility),
the Architect treats it as advisory and consistently deprioritizes it in favour of immediate
exploitation ROI. The helper never gets built, and agents struggle with the same utility task
generation after generation. Previously compounded by confusion between `problem/helper.py`
(backward-compat shim) and `problem/helpers/` (unified helpers directory).
Mitigated: `agents/architect.md` now has a **Recurring Helper Needs** section that makes
launching an experimentator mandatory when a helper recommendation has appeared 2+ consecutive
generations unresolved. The helper system is now unified under `problem/helpers/` (see above).

### [DESIGN-10] ~~Agents can't iterate as fast as spec envisions~~ — MITIGATED
Turn limits raised to 150 for solution agents. Agent prompts now enforce evaluate-immediately
workflow (write one → evaluate → update header → move on). With 150 turns and ~3 turns per
write-evaluate cycle plus ~15 turns reading overhead, agents can do **40+ iterations**.
Previously agents batch-wrote solutions without evaluating, wasting all their turns.

### [DESIGN-13] evaluate.py boilerplate is duplicated per-problem
Every problem has its own `evaluate.py` that re-implements the same infrastructure: content-hash
caching, `.score` sidecar writing, file locking, `eval_cache.json` path resolution. The strawberry
problem additionally has a GPU file lock and a venv re-exec helper that no other problem has.

**Future work**: extract into `problems/_shared/eval_utils.py`:
- `class EvalRunner` — handles cache, sidecar, timing, error wrapping for any problem
- `gpu_lock()` context manager — system-wide exclusive lock on `/tmp/idea_evolve_gpu.lock`
- `reexec_in_venv(venv_python)` — transparent re-exec into a different Python interpreter

Any GPU-training problem (like strawberry) would do:
```python
# evaluate.py (all problems)
from problems._shared.eval_utils import EvalRunner, gpu_lock, reexec_in_venv

reexec_in_venv("/path/to/venv/python")  # no-op if already in venv

def run(solution_path, content_hash):
    with gpu_lock():           # no-op for CPU problems (pass gpu=False)
        output = load_and_call(solution_path)
    return validate(output)

EvalRunner(PROBLEM_ROOT).main(run)
```
CPU-only problems (sidon, gemm, permcodes) pass `gpu=False` so no lock is acquired and
parallel evaluation is unaffected. GPU problems (strawberry and future ML tasks) pass
`gpu=True` and automatically serialize.

**Not done yet** — the existing evaluate.py files all work and touching them risks regressions.
Do this as a dedicated refactor pass, not alongside a problem run.

### [DESIGN-14] GPU evaluation queue is invisible
GPU-bound problems (currently strawberry, future ML tasks) serialize evaluations through
the system-wide `/tmp/idea_evolve_gpu.lock` file lock. When multiple agents call `evaluate.py`
in parallel, they silently queue at the lock — there's no visibility into who is currently
running, who is waiting, how long the current job has been running, or how many are in line.

The only signal today is the `[evaluate.py] Waiting for GPU lock...` line in stderr, which
goes to the agent's bash output and is invisible from the dashboard or orchestrator logs.

**Future work**: build a proper job-queue layer with dashboard visibility.

- **Queue file**: `/tmp/idea_evolve_gpu_queue.json` written under the same lock guard, listing
  `{pid, agent_name, solution_path, problem, started_at, status: running|waiting}` entries.
  Each `evaluate.py` invocation appends itself on entry, marks itself `running` once the lock
  is acquired, and removes itself on exit (including via `atexit` for clean removal even on
  crash).
- **Dashboard tab**: a "GPU Queue" panel on the Pipeline tab showing the currently running
  job (problem, agent, solution path, elapsed time, ETA based on epoch count if extractable)
  and the waiting list ordered by enqueue time.
- **Orchestrator awareness**: emit queue events to `history/run_state.json` so the existing
  beacon system surfaces "GPU saturated, N jobs queued" when relevant.
- **Stale entry GC**: dashboard scanner removes entries whose PID is no longer alive (handles
  the case where `atexit` didn't run after SIGKILL).

This becomes important once 2+ GPU-bound problems run in parallel, or when one problem has
many parallel agents all serializing at the lock — without visibility, debugging "why is
this so slow" requires `lsof /tmp/idea_evolve_gpu.lock` and `ps`.

### [DESIGN-14] ~~GPU evaluation queue is invisible~~ — ADDRESSED via DESIGN-15
The unified eval queue (DESIGN-15) supersedes the GPU-specific design. Strawberry's
`eval_hooks.py` participates in the same `/tmp/idea_evolve_eval_queue.json`; the dashboard
GPU panel becomes a filtered view (`gpu: true` flag) of the same data.

### [DESIGN-15] ~~General evaluation queue with dashboard visibility~~ — IMPLEMENTED
All problems (not just GPU) need a visible evaluation queue so the dashboard shows what is
currently being evaluated and what is waiting. Right now `evaluate.py` runs inline inside
each agent's bash session with no central tracking — the orchestrator and dashboard have no
idea how many evaluations are in flight, which solution is running, or how long it has been.

**Planned implementation:**

- **Queue file**: `/tmp/idea_evolve_eval_queue.json` — written under `fcntl` lock, per-entry:
  `{pid, agent_name, solution_path, problem, attempt, started_at, status: running|waiting}`.
  Each `evaluate.py` invocation appends on entry, updates `status: running` once it starts
  computing, removes itself on exit via `atexit` (safe even on SIGKILL from the orchestrator).
- **Dashboard panel**: "Eval Queue" section on the Pipeline tab showing:
  - Currently running evaluation: problem, agent, solution filename, elapsed time
  - Waiting list ordered by enqueue time
  - Empty state: "No evaluations in progress"
- **API endpoint**: `GET /api/eval_queue` reads and returns the queue JSON; dashboard polls
  it at the same cadence as run_state (10s when orchestrator running, 60s when idle).
- **Orchestrator awareness**: surface queue depth in `history/run_state.json` as
  `eval_queue_depth: N` so the header beacon can show "N evaluations queued".
- **Stale entry GC**: dashboard scanner (or the API handler) removes entries whose PID
  is no longer alive — handles crashes where `atexit` didn't fire.
- **GPU vs CPU**: GPU problems (strawberry) already have a separate lock; their entries
  should appear in this same queue with a `gpu: true` flag so the dashboard can distinguish
  serialized GPU jobs from parallel CPU jobs.

**Scope note**: DESIGN-14 describes the GPU-specific lock queue. DESIGN-15 is the
unified layer that covers all problems. Implement DESIGN-15 first; DESIGN-14's GPU panel
becomes a filtered view of the same data.

### [DESIGN-16] Problem-specific visualizations in dashboard
The Solutions tab shows scores and metadata but no visual output from evaluations. For problems
that produce visual artifacts (segmented images, plots, diagrams), there is no way to browse
results visually from the dashboard.

**Idea:** Each problem optionally declares visualization hooks in its problem definition.
The dashboard Solutions tab renders problem-specific visuals per solution (e.g. for strawberry:
sample segmented images produced by that solution's model; for other problems: custom charts,
heatmaps, or nothing if disabled). The problem construction spec (`description.md` / `metrics.yaml`)
would gain an optional `visualizations:` block describing what artifacts exist and how to render them.

**Concrete strawberry example:** evaluation saves a few sample output images (model overlay on
strawberry photo) to a stable path keyed by content hash. The dashboard Solutions tab shows
a thumbnail gallery for each solution — click to enlarge.

**Design notes:**
- Visualization is opt-in per problem; `visualizations: []` or omitting the key disables the panel.
- Artifacts saved by `evaluate.py` to a per-hash directory under `/tmp/idea_evolve_<problem>/viz/<hash>/`
  or `runs/<problem>/<attempt>/viz/<hash>/`.
- Dashboard API: `GET /api/solution_viz?problem=X&attempt=Y&hash=Z` returns artifact paths.
- Problems that produce no visual output (sidon, gemm, permcodes) simply omit the block.
- Not yet implemented.

### [DESIGN-17] Numeric concurrency limit + research-always-parallel rule

**Current state:** `concurrency:` in `metrics.yaml` is binary — `serial` (1 eval at a time)
or `parallel` (unlimited). The architect is told which mode applies and sizes `parallel_groups`
accordingly. Research and experimentator agents (which never call `evaluate.py`) have no
special treatment — the architect example showed them serialized even on serial-eval problems,
wasting wall-clock time.

**Two gaps to fix:**

1. **Numeric concurrency.** Some problems have N ≥ 2 parallel eval slots (e.g. 2 GPUs, a
   service with rate limiting, a batched evaluator). `concurrency: 2` should mean "up to 2
   solution agents per group." Today only `serial` and `parallel` are recognized; `2` or `3`
   would be ignored.

2. **Research/experimentator are always free.** These agent types never acquire the GPU lock
   or call `evaluate.py`. They consume zero eval slots regardless of the problem's concurrency
   mode. The architect should always colocate them with a running solution agent — never place
   them in a solo sequential group, as that forces all prior solution agents to finish before
   research starts. The current `architect.md` example incorrectly shows `research_1` in its
   own solo group for serial-eval problems; the text contradicts this but agents follow the
   example.

**What needs to change:**

| Layer | Change |
|---|---|
| `metrics.yaml` schema | Accept `concurrency: serial\|parallel\|N` (integer = max simultaneous evals) |
| `orchestrator.py` | Parse numeric value; pass to architect context as "max N evals in parallel" |
| `agents/architect.md` | Fix the serial-mode example to colocate `research_1` with a solution agent; add the "research/experimentator = 0 eval slots" rule explicitly; show a 3-case example (serial / parallel / N=2) |
| `docs/problem_design_guide.md` §9 | Rewrite concurrency section: binary → numeric; add research-free-slot rule |
| `scripts/check_docs_consistency.py` | Accept numeric `concurrency` value when validating |

**The research-always-parallel rule is universal** (applies regardless of concurrency mode)
and should be stated as a hard rule in `architect.md`, not a soft "MAY share a group."

**Not yet implemented.**

## SPEC DEVIATIONS — intentional differences from the design doc

| Spec says | We do | Why |
|-----------|-------|-----|
| Write isolation enforced | Advisory only | Would need sandboxing, complex |
| Solution names: `gen007_explore_2_sol03` | Raw naming `sol01.py` in `population/gen007/explore_2/` | Simpler; path provides identity |
| Debrief as follow-up to same session | Resume same session with `--resume` | Now matches spec; agent keeps full memory |
| Agents read at granular L0→L1→L2 drill-down | Agents get file path list, read what they want | Lean prompts; agents navigate autonomously |
| Knowledge files versioned | Overwritten in place | Would need git or versioning layer |
| `workspace/` archived after run | Deleted after output moved | Saves disk; prevents debugging (see BUG-6) |
| `observations/` directory used | Observations stay in `population/{gen}/{agent}/observations.md` | Simpler routing; evaluator reads from population/ |
| Consistency Reviewer debrief to `feedback/` | Debrief to `reports/` like all agents | Consistent; system critic reads from reports/ |

## UNCERTAIN — needs a real run to verify

1. ~~**Will agents actually write report.md?**~~ **MITIGATED.** Debrief recovery session now
   runs automatically if report.md is missing after timeout. Knowledge is never fully lost.

2. **Will the Architect produce valid manifest.yaml?** LLM writing YAML. Could produce invalid
   syntax, wrong brief paths, or skip agent types. Fallback manifest exists but loses strategy.
   **MITIGATED:** architect.md now shows correct manifest format with examples matching
   what the orchestrator actually parses.

3. ~~**Do 80 max turns suffice?**~~ **ADDRESSED.** Turn limits raised to 150 for solution agents.
   With mandatory evaluate-immediately workflow, agents now have room for 30+ write-evaluate cycles.

4. **Will lean prompts cause missed context?** Agents might not read all listed files, or miss
   relevant unlisted files. Monitor debrief reports for "I didn't know about X."

5. **Rate limiting with 10 parallel sessions.** May need to reduce `max_parallel_sessions`
   or add backoff logic.

6. **Will gen-1 Evaluator create clusters from scratch?** No example cluster files exist.
   Prompt describes the format but there's nothing to imitate. First clusters may be bad.

7. **Does the experiment_requests flow actually work?** Full agents → `experiment_requests.md` →
   collected to `feedback/` → listed in Architect prompt. Untested end-to-end.

8. ~~**Will agents handle absolute paths correctly?**~~ **FIXED.** `_absolutize_brief_paths()`
   post-processes all briefs to convert relative paths to absolute.

9. **Does `--allowedTools` auto-approve tools?** We assume it does. If it doesn't, agents will
   be blocked on every tool call waiting for user approval that never comes in `--print` mode.

10. **Context window pressure at high turn counts.** With 150 turns of tool results accumulating,
    does Claude Code compress/drop early context? If so, agents lose memory of early iterations.

11. **Will the Architect read and use the coverage matrix?** It's listed in "Files to Read" but
    the matrix format (N×N table) may be hard for the LLM to parse into actionable strategy.
    **MITIGATED:** Coverage matrix now capped to top 30 ideas with sparse format.

12. **Can the Evaluator reliably do idea matching?** Mapping which ideas each solution implements
    (central vs peripheral) requires understanding both the code and the idea descriptions.
    LLM judgment here could be inconsistent across generations.

## REMAINING POTENTIAL ISSUES — not bugs, monitor during runs

### Performance (negligible until proven otherwise)
- **YAML re-parsing**: `config.yaml` and `metrics.yaml` re-parsed ~30 times per generation
  across `load_config()`, `primary_metric()`, `_score_fmt()`, etc. ~50ms total. Would require
  threading config as a parameter through all functions to fix. Not worth the refactor.
- **`detect_interventions` rglob**: Scans `knowledge/`, `user/`, `agents/` trees every gen
  during finalize. ~200 stat() calls at gen 20. Non-blocking.

### Scaling (monitor after gen 15)
- **`all_scores.json` existence checks**: Every cached entry gets `Path.exists()` per gen.
  ~100 calls at gen 20. Could skip and just trust the cache, but stale entries would linger.
- **Eval cache unbounded**: `eval_cache.json` never pruned. Could add LRU or gen-based pruning
  if it grows past 10MB.
- **`.score` file reads in population summary**: Valid count reads every `.score` file.
  Could extend `all_scores.json` to cache `is_valid` alongside score.

### Advisory config not enforced
- **`max_instances` per agent type**: Architect sees the limit but orchestrator doesn't reject
  extra instances. Intentional — hard enforcement would override Architect judgment. Monitor
  if the Architect consistently exceeds limits.
- **`knowledge_hierarchy` values**: Token limits for State of Affairs, clusters, etc. are
  advisory guidance for agents. The orchestrator doesn't truncate knowledge files to fit.
  Monitor if knowledge files grow excessively large.

### Untested end-to-end flows
- **Genetic crossover**: Requires Architect to specify 2 parents by path. Never tested in a
  real run. The genetic.md template is correct but parent path resolution is untested.
- **Experimentator → knowledge pipeline**: Experiment results go to `knowledge/experiments/`,
  evaluator consolidates old ones. The full cycle is untested.
- **Consistency reviewer cluster updates**: When the reviewer writes `updated_clusters/`,
  the orchestrator diffs against existing clusters to find removed ones and fix orphaned refs.
  Untested with real cluster data.
