# Contributing to Idea Evolve

Thanks for your interest in contributing! This guide covers the main ways to help.

## Getting Started

```bash
git clone https://github.com/aleksanderborodin/idea_evolve.git
cd idea_evolve
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll also need Node.js 22+ and Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) if you want to run the orchestrator.

## Ways to Contribute

### Add a New Problem

This is the easiest and most impactful contribution. Create `problems/{your-problem}/` with:

1. **`description.md`** — Problem statement, context, known bounds
2. **`constraints.md`** — Hard constraints that solutions must satisfy
3. **`evaluate.py`** — Evaluation harness. Must:
   - Accept a single positional arg (path to solution file)
   - Call `validate.py` first
   - Print JSON to stdout: `{"metric_name": <float>, "is_valid": 1|0, ...}`
   - Use content-hash caching (see existing problems for the pattern)
4. **`validate.py`** — Correctness checker. Invalid solutions get sentinel score (0)
5. **`metrics.yaml`** — Fitness config:
   ```yaml
   primary_metric: your_metric
   direction: higher_is_better  # or lower_is_better
   target: 100                  # known optimal or goal
   sentinel_value: 0            # score for invalid solutions
   decimals: 0                  # display precision
   ```
6. **`helpers/`** — Optional shared utilities (with `core.py` and `__init__.py`)
7. **`initial_programs/`** — At least one baseline solution
8. **`initial_ideas.md`** and **`initial_facts.md`** — Seed knowledge for generation 1

Look at `problems/sidon/` for a complete example.

### Improve Agent Prompts

Agent templates live in `agents/`. Each one defines how a specialized agent approaches problems:

- `explore.md` — Novel solution generation
- `exploit.md` — Refinement of existing solutions
- `genetic.md` — Crossover between two parent solutions
- `research.md` — Literature research and mathematical derivation
- `experimentator.md` — Helper utility creation

If you find agents making systematic mistakes or missing opportunities, improving the prompt template is high-value work.

### Dashboard Improvements

The dashboard is a Flask app in `dashboard/`:

```bash
python dashboard/app.py --debug  # hot reload on http://localhost:5000
```

- `data/` — filesystem scanning and config
- `routes/` — API endpoints and page routes
- `templates/` — Jinja2 templates (tab partials)
- `static/` — CSS and vanilla JS

No external JS frameworks. Everything is vanilla HTML/CSS/JS.

### Bug Fixes and Improvements

Check [CLAUDE.md](CLAUDE.md) for the full list of known issues, scaling concerns, and design gaps. Items marked "Not yet fixed" are fair game.

## Submitting Changes

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Test locally:
   - For problems: run `python3 evaluate.py initial_programs/your_baseline.py` and verify JSON output
   - For dashboard: run `python dashboard/app.py --debug` and check your changes
   - For orchestrator: use `--dry-run` to verify without launching agents
4. Open a pull request with:
   - What you changed and why
   - How to test it
   - Any relevant screenshots (especially for dashboard changes)

## Code Style

- Python 3.12+ with type hints where they add clarity
- No external dependencies unless absolutely necessary (check `requirements.txt`)
- Agent templates are Markdown — keep them clear and actionable
- The orchestrator is a single file by design; don't split it into modules

## AI Agents Welcome

Contributions made with AI coding agents (Claude Code, Copilot, Cursor, etc.) are welcome — as long as they solve real issues and propose real features. We don't accept AI-generated PRs that are cosmetic busywork: reformatting code, adding unnecessary docstrings, or "improving" things that don't need improving. If an AI helped you write it, great. Just make sure the change would be worth merging if a human wrote it too.

## Questions?

Open an issue for questions, bug reports, or feature ideas. We're responsive and happy to help.
