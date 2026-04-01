# Idea Evolve

Evolutionary code optimization through collaborative AI agent work sessions. Multiple specialized Claude agents (architects, explorers, exploiters, researchers) work in parallel to evolve increasingly better solutions to hard optimization problems.

## Prerequisites

| Requirement | How to install | Purpose |
|------------|---------------|---------|
| **Python 3.12+** | `sudo apt install python3 python3-venv` | Orchestrator, dashboard, evaluation |
| **Node.js 18+** | `sudo apt install nodejs npm` | Claude Code CLI runtime |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | AI agent sessions |
| **Anthropic API key** | [console.anthropic.com](https://console.anthropic.com) | Set `ANTHROPIC_API_KEY` env var |
| **g++ 11+** | `sudo apt install g++` | GEMM problem: compiling C++ solutions |
| **Google Benchmark** | `sudo apt install libgoogle-benchmark-dev` | GEMM problem: benchmarking |
| **cgroup tools** | `sudo apt install cgroup-tools` | GEMM problem: CPU pinning (optional) |

## Setup (from scratch)

```bash
# 1. Clone
git clone <repo-url> && cd project_alpha

# 2. Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt      # PyYAML + Flask (minimal)

# 3. API key
export ANTHROPIC_API_KEY="sk-ant-..."  # add to ~/.bashrc for persistence

# 4. Verify Claude Code works
npx @anthropic-ai/claude-code --version
```

## Running the Orchestrator

The orchestrator is the main loop. It launches AI agents, collects results, and evolves solutions.

```bash
source venv/bin/activate
cd idea-evolve

# Start a new attempt on the GEMM problem (creates runs/gemm/attempt_001/)
python3 orchestrator.py . --problem gemm --new-attempt --single

# Continue an existing attempt
python3 orchestrator.py . --problem gemm --single          # latest attempt, 1 gen
python3 orchestrator.py . --problem gemm                    # full run (30 gens)
python3 orchestrator.py . --problem gemm --start-gen 5      # resume from gen 5

# Use a specific attempt
python3 orchestrator.py . --problem gemm --attempt attempt_002

# Preview without launching agents
python3 orchestrator.py . --problem gemm --dry-run

# Background with logging
python3 orchestrator.py . --problem gemm --single >> /tmp/run.log 2>&1 &
tail -f /tmp/run.log
```

On first run with `--new-attempt`, the orchestrator:
1. Creates the run directory skeleton (`runs/gemm/attempt_001/`)
2. Creates symlinks at `idea-evolve/` root (`population/`, `knowledge/`, etc.) pointing into the run
3. Bootstraps initial knowledge from `user/initial_ideas.md` and `user/initial_facts.md`
4. Runs the first generation

On subsequent runs, it detects where the previous run left off and resumes. If it crashed, completed agents are skipped automatically.

## Running the Dashboard

```bash
source venv/bin/activate
python dashboard/app.py              # http://localhost:5000
python dashboard/app.py --port 8080  # custom port
python dashboard/app.py --debug      # hot reload for development
```

The dashboard reads directly from the filesystem -- no database. It auto-detects problems and attempts from the `problems/` and `runs/` directories.

## How a Generation Works

Each generation goes through 6 phases:

```
Architect  ->  Agent Work  ->  Evaluator  ->  System Critic  ->  Consistency  ->  Finalize
 (plan)      (parallel AI)    (score +       (diagnose         (audit            (rank +
              agents write     extract        pipeline          knowledge         update
              solutions)       knowledge)     issues)           base)             scores)
```

1. **Architect** (opus) -- reads current knowledge, scores, and reports. Writes a manifest (`manifest.yaml`) specifying which agents to launch with what goals.
2. **Agent Work** -- 3-8 specialized agents run in parallel. Each reads its brief, writes solutions (`sol*.py`), runs `evaluate.py`, iterates, and writes a debrief report.
3. **Evaluator** (opus) -- reviews all new solutions, extracts ideas/patterns/facts, updates clusters, writes coverage matrix and solution-idea map.
4. **System Critic** (sonnet) -- reads agent reports, identifies pipeline problems, writes recommendations.
5. **Consistency Review** (opus, every N gens) -- audits the entire knowledge base, rewrites State of Affairs.
6. **Finalize** -- updates rankings (`population/best.py`), score progression, generation snapshot.

### Agent Types

| Agent | Model | Purpose |
|-------|-------|---------|
| `explore` | sonnet | Novel approaches -- structurally different from existing solutions |
| `exploit` | sonnet | Refine top solutions with targeted improvements |
| `genetic` | sonnet | Crossover: combine strengths from two parent solutions |
| `full` | sonnet | Full autonomy -- read everything, try anything |
| `research` | sonnet | Mathematical research -- read papers, derive new approaches |
| `experimentator` | opus | Create shared helper utilities for all agents |

## Dashboard Guide

### Problem/Attempt Selector

Click the breadcrumb in the header (e.g., `gemm / attempt_001`) to open the flyout panel. Shows all problems with their attempts, status indicators (running/idle/crashed), generation count, solution count, and best score. Click an attempt to switch context -- all tabs update.

### Overview Tab

![Dashboard Overview](images/score_progression.png)

The overview shows at a glance:
- **Best Fitness Score** with a gauge showing progress toward target (respects lower-is-better for GEMM)
- **Generation count**, solution count, idea count, knowledge stats
- **Current Phase** strip -- which phase the current generation is in
- **Score Progression Chart** -- interactive canvas chart with:
  - Gray dots: all evaluated solutions
  - Blue circles: per-generation best
  - Green stars: new all-time records
  - Green fill: running best (record line)
  - Dashed lines: baseline and target
  - **Frontier toggle**: click "Frontier" to overlay annotated callouts on record-breaking solutions showing agent name, score improvement %, and which ideas drove the breakthrough
  - Scroll to zoom, double-click to reset, hover for tooltips
- **Generation Timeline** -- cards for each completed generation with best score and solution count

### Pipeline Tab

![Pipeline View](images/pipeline_tab.png)

Shows the current generation's pipeline state:
- Per-agent cards with status (waiting/running/done/failed), solution count, best score
- Agent briefs showing what the Architect assigned
- Reads from durable `gen_progress.json` -- survives orchestrator crashes

### Solutions Tab

![Solutions Table](images/solutions_tab.png)

Sortable, filterable table of every solution:
- Sorted best-first (lower is better for GEMM)
- Filter by generation, agent type, or status
- Color-coded: green (valid), red (invalid), orange (error), gray (pending)
- Click error rows to expand and see the error message

### Knowledge Tab

Three-layer knowledge hierarchy:
- **State of Affairs** (L0) -- strategic overview with staleness indicator
- **Clusters** (L1) -- groups of related ideas
- **Ideas** (L2) -- individual optimization concepts with lifecycle (active/established/disputed/debunked)
- Also: facts, patterns, and research findings
- Click any item for a detail modal with full body, metadata, and relationships

### Reports Tab

Agent debrief reports grouped by generation. Each agent writes a report summarizing what it tried, what worked, what failed, and insights for future agents.

## Project Structure

```
project_alpha/
├── idea-evolve/
│   ├── orchestrator.py          # Main loop (~3200 lines)
│   ├── migrate_to_multi.py      # Migration tool
│   │
│   ├── agents/                  # Prompt templates (10 agent types)
│   │   ├── architect.md         #   Plans each generation
│   │   ├── explore.md           #   Novel approaches
│   │   ├── exploit.md           #   Refine existing solutions
│   │   ├── genetic.md           #   Crossover parents
│   │   ├── full.md              #   Full autonomy
│   │   ├── research.md          #   Math/paper research
│   │   ├── experimentator.md    #   Build shared helpers
│   │   ├── evaluator.md         #   Score + extract knowledge
│   │   ├── system_critic.md     #   Diagnose pipeline issues
│   │   └── consistency_review.md #  Audit knowledge base
│   │
│   ├── prompts/                 # Shared prompt fragments
│   │   ├── debrief_instructions.md
│   │   ├── analysis_debrief.md
│   │   └── debrief_recovery.md
│   │
│   ├── user/                    # User configuration
│   │   ├── config.yaml          #   Turn limits, timeouts, agent config
│   │   ├── initial_ideas.md     #   Seed ideas for gen 1
│   │   ├── initial_facts.md     #   Seed facts for gen 1
│   │   └── interventions.md     #   Manual guidance for the Architect
│   │
│   ├── problems/                # Problem definitions (read-only at runtime)
│   │   ├── gemm/                #   Binary-ternary GEMM optimization
│   │   │   ├── description.md   #     Problem statement
│   │   │   ├── constraints.md   #     Hard constraints
│   │   │   ├── evaluate.py      #     Evaluation harness (caches results)
│   │   │   ├── validate.py      #     Compile, correctness check, benchmark
│   │   │   ├── metrics.yaml     #     Fitness direction, target, sentinel values
│   │   │   ├── helpers/         #     Shared utilities (core.py + agent-created)
│   │   │   └── initial_programs/#     Baseline solutions
│   │   └── permcodes/           #   Permutation codes (archived)
│   │
│   └── runs/                    # Evolution data (per problem + attempt)
│       └── gemm/
│           └── attempt_001/     # One self-contained run
│               ├── population/  #   genNNN/{agent}/sol*.py + .score
│               ├── knowledge/   #   state_of_affairs.md, ideas/, clusters/
│               ├── history/     #   all_scores.json, eval_cache.json, run_state.json
│               ├── briefs/      #   genNNN/manifest.yaml + agent briefs + gen_progress.json
│               ├── reports/     #   genNNN/{agent}.md debrief reports
│               ├── feedback/    #   system_recommendations.md, analyses
│               └── workspace/   #   ephemeral agent workspaces
│
├── dashboard/                   # Flask web UI
│   ├── app.py                   # Entry point
│   ├── data/                    # Filesystem scanning (no database)
│   │   ├── config.py            #   Problem/attempt discovery
│   │   ├── helpers.py           #   Score extraction, frontmatter parsing
│   │   └── scanner.py           #   All data scanning functions
│   ├── routes/
│   │   ├── api.py               #   /api/* JSON endpoints
│   │   └── pages.py             #   HTML routes
│   ├── templates/               # Jinja2 (base.html + tab partials)
│   └── static/                  # CSS + vanilla JS (no build step)
│
├── fast-conv/                   # C++ reference implementations + benchmark harness
├── images/                      # Dashboard screenshots
├── requirements.txt             # PyYAML + Flask
└── CLAUDE.md                    # Operational reference + all known issues
```

When the orchestrator runs with `--problem gemm`, it creates **symlinks** at `idea-evolve/` root pointing into the active run directory:

```
idea-evolve/population -> runs/gemm/attempt_001/population
idea-evolve/knowledge  -> runs/gemm/attempt_001/knowledge
idea-evolve/problem    -> problems/gemm
...etc
```

This means all code works with simple relative paths. The symlinks are updated automatically when you switch problems or attempts.

## Error Recovery

If the orchestrator crashes mid-generation, just restart with the same command:

```bash
python3 orchestrator.py . --problem gemm --single
```

What happens:
- **Completed agents are skipped** (tracked in `gen_progress.json`)
- **Orphaned agent processes are killed** (verified via `/proc/{pid}/cmdline`)
- **Interrupted output moves are retried** before re-running
- **Each phase checks completion** before re-running

No manual cleanup needed.

## Current Problem: Binary-Ternary GEMM

Optimizing C++ matrix multiplication kernels for Intel Tiger Lake (AVX-512). Solutions are Python files whose `entrypoint()` returns a C++ source code string defining `gemmCandidate()`. The evaluator compiles, checks correctness against a reference implementation, and benchmarks across 3 matrix sizes.

- **Baseline:** ~770 us (V14opt implementation)
- **Target:** 24 us (~32x speedup)
- **Metric:** Geometric median time in us (lower is better)
- **Sentinel value:** 100,000 us (used for failed evaluations)

## Documentation

- **[CLAUDE.md](CLAUDE.md)** -- Operational reference, all 45 bug fixes, scaling improvements, known issues. Updated with every change.
- **[IDEA_EVOLVE_COMPLETE_V4.md](IDEA_EVOLVE_COMPLETE_V4.md)** -- Full system specification (architecture, agent roles, knowledge model, file formats).
- **[dashboard/README.md](dashboard/README.md)** -- Dashboard architecture, API endpoints, chart internals.
