<p align="center">
  <h1 align="center">Idea Evolve</h1>
  <p align="center">
    <strong>Evolutionary code optimization through collaborative AI agent work sessions</strong>
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+"></a>
    <a href="https://github.com/aleksanderborodin/idea_evolve/stargazers"><img src="https://img.shields.io/github/stars/aleksanderborodin/idea_evolve?style=social" alt="GitHub Stars"></a>
  </p>
</p>

Multiple specialized Claude agents — architects, explorers, exploiters, researchers — work in parallel across generations to evolve increasingly better solutions to hard optimization problems. No human in the loop. The system builds a shared knowledge base that gets smarter every generation.

> **Example result:** Sidon set problem (find largest B2 sequence in {0..10000}).
> Greedy baseline: **66 elements**. After 7 generations of autonomous agent work: **89 elements** (+35%). Theoretical target: ~100.

![Dashboard Overview](images/overview.png)

## How It Works

A stateless orchestrator runs generations of AI agents. Each generation:

```
Architect  ->  Agent Work  ->  Evaluator  ->  System Critic  ->  Consistency  ->  Finalize
 (plan)       (parallel AI      (score +       (diagnose         (audit           (rank +
               agents write      extract        pipeline          knowledge        update
               solutions)        knowledge)     issues)           base)            scores)
```

1. An **Architect** agent plans the strategy and assigns specialized agents
2. **3-8 agents** work in parallel — writing solutions, evaluating them, iterating (40+ cycles each)
3. An **Evaluator** extracts knowledge (ideas, patterns, facts) into a shared knowledge base
4. A **System Critic** diagnoses pipeline issues and recommends improvements
5. A **Consistency Reviewer** audits the knowledge base periodically
6. **Finalize** updates rankings, scores, and detects any manual interventions

All state lives in files. If the orchestrator crashes, it resumes from exactly where it left off.

## Agent Types

| Agent | Role |
|-------|------|
| **Explore** | Novel approaches — structurally different from existing solutions |
| **Exploit** | Refine top solutions with targeted improvements |
| **Genetic** | Crossover: combine strengths from two parent solutions |
| **Full** | Full autonomy — read everything, try anything |
| **Research** | Mathematical research — read papers, derive new approaches |
| **Experimentator** | Create shared helper utilities for all agents |

## Quick Start

### Prerequisites

- **Python 3.12+** — orchestrator, dashboard, evaluation
- **Node.js 22+** — Claude Code CLI runtime (default harness)
- **Anthropic API key** — [console.anthropic.com](https://console.anthropic.com)
- *(optional)* **[OpenCode](https://opencode.ai)** — alternative harness for routing individual agents through non-Anthropic providers (e.g. via ModelGate)

### Install

```bash
git clone https://github.com/aleksanderborodin/idea_evolve.git
cd idea_evolve

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Claude Code CLI (default harness)
npm install -g @anthropic-ai/claude-code

# (optional) OpenCode — only needed if you route any agent to the opencode harness
curl -fsSL https://opencode.ai/install | bash

# Secrets: store in .env at the repo root (gitignored)
cat > .env <<'EOF'
ANTHROPIC_API_KEY=sk-ant-...
# Only needed for the opencode harness via ModelGate:
MODELGATE_API_KEY=rp_...
MODELGATE_BASE_URL=https://api.modelgate.ru/v1
EOF

# Load secrets before running
set -a; source .env; set +a
```

### Run

```bash
source venv/bin/activate
cd idea-evolve

# Start a new run on a problem
python3 orchestrator.py . --problem sidon --new-attempt --single

# Continue latest attempt (1 generation)
python3 orchestrator.py . --problem sidon --single

# Full run (all generations)
python3 orchestrator.py . --problem sidon

# Preview without launching agents
python3 orchestrator.py . --problem sidon --dry-run
```

Two orchestrators can run simultaneously on different problems — each works in its own isolated directory.

## Harnesses: routing agents to different CLIs

Every agent session is launched through a **harness adapter**. Two are built-in:

| Harness | Binary | Provider reach |
|---|---|---|
| `claude-code` *(default)* | `npx @anthropic-ai/claude-code` | Anthropic (Claude) |
| `opencode` | `opencode run` | Anything opencode supports — Anthropic, OpenAI, Gemini, local, or routed via ModelGate |

Both adapters expose the same `launch()` / `resume()` contract, so wrap-up and debrief recovery after a timeout work identically. OpenCode's session ids are assigned by the server and captured from the first streamed JSON event; Claude Code accepts caller-assigned UUIDs. Details and contract tests: [idea-evolve/orchestrator_harness.py](idea-evolve/orchestrator_harness.py), [idea-evolve/tests/test_adapters.py](idea-evolve/tests/test_adapters.py).

### Selecting a harness per agent

Edit [idea-evolve/user/config.yaml](idea-evolve/user/config.yaml):

```yaml
harnesses:
  default: claude-code        # harness used when no per_agent override matches
  per_agent: {}               # override by role — only list the EXCEPTIONS
                              # (listing a role whose harness == default is a no-op)

models:
  opencode:                   # alias → provider/model (only consulted by the opencode harness)
    opus:   modelgate/claude-sonnet-4-5
    sonnet: modelgate/minimax-m2.7
    haiku:  modelgate/minimax-m2.7
```

Resolution order at every launch site: `per_agent[role]` → `default` → `claude-code` (with warning on unknown names). Only list roles in `per_agent` whose harness differs from `default`.

**Example A — keep everything on Claude, route explorers through opencode only:**

```yaml
harnesses:
  default: claude-code
  per_agent:
    explore: opencode
```

**Example B — flip the default to opencode, keep only the architect on claude-code:**

```yaml
harnesses:
  default: opencode
  per_agent:
    architect: claude-code
```

**Fidelity notes.** OpenCode has no `--max-turns` equivalent; wall-clock timeout is the only ceiling (a one-time warning is logged per run). Agent prompt templates are Claude-tuned, so routing `architect` or `evaluator` to a non-Claude model may degrade reasoning quality — keep those on `claude-code` unless you specifically want to validate otherwise.

## Defining Your Own Problem

Create a directory in `problems/{your-problem}/` with:

| File | Purpose |
|------|---------|
| `description.md` | Problem statement and context |
| `constraints.md` | Hard constraints solutions must satisfy |
| `evaluate.py` | Evaluation harness (caches results by content hash) |
| `validate.py` | Correctness check — invalid solutions get sentinel score (0) |
| `metrics.yaml` | Fitness direction (`higher_is_better` / `lower_is_better`), target, decimals |
| `helpers/` | Shared utility functions available to all agents |
| `initial_programs/` | Baseline solutions to seed generation 0 |

See existing problems (`gemm`, `permcodes`, `sidon`) for examples.

## Dashboard

```bash
source venv/bin/activate
python dashboard/app.py        # http://localhost:5000
```

The dashboard reads directly from the filesystem — no database. It auto-detects all problems and attempts.

| Tab | What it shows |
|-----|---------------|
| **Overview** | Score progression, generation timeline, key metrics, live status beacon |
| **Pipeline** | Per-agent status (waiting/running/done/failed), data flow between phases |
| **Architecture** | Run directory structure, knowledge hierarchy, idea lifecycle |
| **Solutions** | Sortable table of every evaluated solution, color-coded by validity |
| **Knowledge** | Three-layer hierarchy: State of Affairs -> Clusters -> Ideas/Patterns/Facts |
| **Reports** | Agent debrief reports and system feedback by generation |

### Pipeline
![Pipeline](images/pipeline.png)

### Architecture
![Architecture](images/architecture.png)

### Solutions
![Solutions](images/solutions.png)

### Knowledge
![Knowledge](images/knowledge.png)

### Reports
![Reports](images/reports.png)

## Project Structure

```
idea-evolve/
├── orchestrator.py          # Stateless main loop (~3200 lines)
├── agents/                  # Prompt templates (10 agent types)
├── prompts/                 # Shared prompt fragments
├── user/                    # config.yaml, initial_ideas.md
├── problems/                # Problem definitions (read-only at runtime)
│   ├── gemm/                #   Binary-ternary GEMM optimization
│   ├── permcodes/           #   Permutation codes M(n,d)
│   └── sidon/               #   Sidon sets (B2 sequences)
└── runs/                    # All evolution data, per problem + attempt
    └── {problem}/{attempt}/ #   population/, knowledge/, history/, reports/, ...

dashboard/                   # Flask web UI (reads filesystem, no database)
```

## Error Recovery

If the orchestrator crashes, just restart with the same command. Completed agents are skipped, orphaned processes are killed, and each phase checks completion before re-running. No manual cleanup needed.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to add problems, extend agent types, and submit changes.

## License

[MIT](LICENSE)

## Documentation

- [CLAUDE.md](CLAUDE.md) — Operational reference, all known issues, architectural decisions
- [IDEA_EVOLVE_COMPLETE_V4.md](IDEA_EVOLVE_COMPLETE_V4.md) — Full system specification
- [dashboard/README.md](dashboard/README.md) — Dashboard architecture and API endpoints
