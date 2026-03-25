# Alpha Evolve Dashboard

Web-based monitoring UI for Alpha Evolve evolutionary runs.

## Setup

```bash
# From project root (project_alpha/)
source venv/bin/activate
pip install flask pyyaml       # already in venv
python dashboard/app.py        # http://localhost:5000
```

Options:
- `--port N` — custom port (default 5000)
- `--host 0.0.0.0` — listen on all interfaces
- `--debug` — enable Flask debug mode with hot reload

## Tabs

| Tab | Purpose |
|-----|---------|
| **Overview** | Score gauge, metrics, phase indicator, score progression chart (with baseline + target lines, direction indicator), generation timeline. Auto-refreshes every 10s. |
| **Pipeline** | Visual 6-phase generation loop (Architect > Agents > Evaluator > Critic > Consistency > Finalize). Agent type cards with config. Data flow diagram. |
| **Architecture** | Collapsible file tree browser (color-coded by directory). Knowledge hierarchy diagram (L0/L1/L2). Idea lifecycle flow. |
| **Solutions** | Sortable, filterable table of all solutions with full decimal precision. Agent column shows type+instance (e.g., `explore_1`). Sorted best-first respecting fitness direction. Filter by generation or agent type. |
| **Knowledge** | State of Affairs, ideas grid with lifecycle filters, facts, patterns, clusters. |
| **Reports** | Expandable agent debrief reports grouped by generation. |

## API Endpoints

All return JSON.

| Endpoint | Description |
|----------|-------------|
| `GET /api/overview` | Config (incl. `higher_is_better`, `decimals`), stats, generations, score progression, timing data, eval cache stats, initial program scores |
| `GET /api/solutions` | All solutions with scores, sorted best-first (respects fitness direction) |
| `GET /api/knowledge` | State of affairs, ideas, facts, patterns, clusters |
| `GET /api/knowledge/coverage` | Coverage matrix + solution-idea map (raw markdown) |
| `GET /api/reports` | All agent reports |
| `GET /api/reports/<gen>` | Reports for a specific generation |
| `GET /api/files` | File tree grouped by directory |
| `GET /api/generation/<gen>` | Full detail for one generation (manifest, reports, solutions, snapshot) |

## File Structure

```
dashboard/
├── __init__.py
├── app.py                  # Entry point — create_app(), argparse
├── data/                   # Backend data layer
│   ├── __init__.py         # Re-exports all public functions
│   ├── config.py           # Project root resolution, config.yaml loading
│   ├── helpers.py          # Frontmatter parsing, score extraction (with eval cache), metrics config
│   └── scanner.py          # Filesystem scanning (generations, solutions, knowledge, etc.)
├── routes/                 # Flask blueprints
│   ├── __init__.py
│   ├── api.py              # /api/* JSON endpoints
│   └── pages.py            # HTML page routes
├── templates/
│   ├── base.html           # Shell: head, header, nav, includes tabs, loads JS
│   └── tabs/               # Per-tab HTML partials (Jinja2 includes)
│       ├── overview.html
│       ├── pipeline.html
│       ├── architecture.html
│       ├── solutions.html
│       ├── knowledge.html
│       └── reports.html
├── static/
│   ├── css/
│   │   └── style.css       # All styles (variables, components, responsive)
│   └── js/
│       └── app.js          # Client logic (tab switching, API fetch, rendering, chart)
└── README.md
```

## Design Decisions

- **No build step.** Plain CSS + vanilla JS. No npm, no bundler, no framework.
- **Filesystem-based.** Backend scans `../alpha-evolve/` on each request. No database.
- **Metrics-aware.** Reads `problem/metrics.yaml` for fitness direction (`higher_is_better`),
  decimal precision, target score. All sort orders, comparisons, and display formats respect this.
- **Multi-source score resolution.** `extract_score()` checks: `.score` sidecar file →
  eval cache (`history/eval_cache.json`) by SHA-256 content hash → `# fitness:` header comment.
  This means scores appear in the dashboard even before the orchestrator's Finalize phase creates
  `.score` files, as long as evaluate.py was run (which populates the cache).
- **Optimized overview polling.** `/api/overview` counts files via generation dirs instead of
  doing a full solution scan — fast enough for 10s polling.
- **Blueprints.** Routes split into `api` and `pages` blueprints for clean separation.
- **Data layer.** `data/` package isolates all filesystem scanning. The routes layer
  calls `data.*` functions and returns JSON — no file I/O in route handlers.

## Design

Light theme with clean card-based layout. Accent green (#059669) for scores/progress,
blue for generations/population, purple for briefs/planning, amber for reports/warnings.
Monospace (JetBrains Mono) for data, Outfit for headings.
