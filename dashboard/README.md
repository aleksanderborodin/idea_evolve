# Idea Evolve Dashboard

Web-based monitoring UI for Idea Evolve evolutionary runs. Supports multiple problems and attempts.

## Setup

```bash
# From project root
source venv/bin/activate
pip install -r requirements.txt    # Flask + PyYAML
python dashboard/app.py            # http://localhost:5000
```

Options:
- `--port N` — custom port (default 5000)
- `--host 0.0.0.0` — listen on all interfaces
- `--debug` — enable Flask debug mode with hot reload

## Tabs

| Tab | Purpose |
|-----|---------|
| **Overview** | Score gauge, metrics, phase indicator, **interactive score progression chart** with toggleable annotated frontier, generation timeline. Knowledge staleness and lifecycle counts. Auto-refreshes every 10s when running, 60s when idle. |
| **Pipeline** | Visual 6-phase generation loop. **Live agent panels** with real-time status from durable `gen_progress.json`. Agent type cards with config. Data flow diagram. |
| **Architecture** | Collapsible file tree browser. Knowledge hierarchy diagram (L0/L1/L2). Idea lifecycle flow. |
| **Solutions** | Sortable, filterable table of all solutions. Sorted best-first respecting fitness direction. Filter by generation or agent type. Shows **Eval time** per solution when `metrics.yaml` sets `track_eval_time: true` (sourced from `eval_time_s` in each `.score` file); rendered as `ms` / `s` / `m:ss` and `--` when unavailable. |
| **Knowledge** | State of Affairs (with staleness indicator), ideas grid with lifecycle filters, facts, patterns, clusters. Clickable items open detail modal. |
| **Reports** | Expandable agent debrief reports grouped by generation. |

## Problem/Attempt Navigation

The header contains a **context selector** (breadcrumb between logo and nav tabs) that opens a flyout panel showing all problems and their attempts with summary stats (generations, solutions, best score, run status). Selection persists in localStorage.

All API endpoints accept `?problem=X&attempt=Y` query params. Default: auto-detect first available problem/attempt.

## API Endpoints

All return JSON. All accept optional `?problem=X&attempt=Y` query params.

| Endpoint | Description |
|----------|-------------|
| `GET /api/problems` | List all problems with attempts, summary stats, and status |
| `GET /api/overview` | Config, stats, generations, score progression, timing, eval cache, initial scores, staleness, lifecycle counts |
| `GET /api/solutions` | All solutions with scores, sorted best-first |
| `GET /api/knowledge` | State of affairs, ideas, facts, patterns, clusters |
| `GET /api/knowledge/coverage` | Coverage matrix + solution-idea map (raw markdown) |
| `GET /api/reports` | All agent reports |
| `GET /api/reports/<gen>` | Reports for a specific generation |
| `GET /api/files` | File tree grouped by directory |
| `GET /api/agents/active` | Currently running/recent agents with solution counts, scores, status |
| `GET /api/knowledge/<kind>/<id>` | Full detail for a single knowledge item |
| `GET /api/generation/<gen>` | Full detail for one generation (manifest, reports, solutions, snapshot) |
| `GET /api/generation/<gen>/progress` | Durable per-agent progress from `gen_progress.json` |
| `GET /api/frontier` | Record-breaking solutions annotated with central ideas |
| `GET /api/feedback` | System critic analysis and consistency reviews |

## File Structure

```
dashboard/
├── __init__.py
├── app.py                  # Entry point — create_app(), argparse
├── data/                   # Backend data layer
│   ├── __init__.py         # Re-exports all public functions
│   ├── config.py           # Project root, multi-problem discovery (list_problems, etc.)
│   ├── helpers.py          # Frontmatter parsing, score extraction, metrics config
│   └── scanner.py          # Filesystem scanning (generations, solutions, knowledge, etc.)
├── routes/                 # Flask blueprints
│   ├── __init__.py
│   ├── api.py              # /api/* JSON endpoints
│   └── pages.py            # HTML page routes
├── templates/
│   ├── base.html           # Shell: header with context selector, nav, flyout panel
│   └── tabs/               # Per-tab HTML partials (Jinja2 includes)
│       ├── overview.html
│       ├── pipeline.html
│       ├── architecture.html
│       ├── solutions.html
│       ├── knowledge.html
│       └── reports.html
├── static/
│   ├── css/
│   │   └── style.css       # All styles (variables, components, flyout, responsive)
│   └── js/
│       └── app.js          # Client logic (context management, tabs, API, chart, flyout)
└── README.md
```

## Design Decisions

- **No build step.** Plain CSS + vanilla JS. No npm, no bundler, no framework.
- **Filesystem-based.** Backend scans the idea-evolve directory on each request. No database.
- **Multi-problem aware.** Auto-detects `problems/` + `runs/` layout. Falls back to legacy single-problem.
- **Metrics-aware.** Reads `metrics.yaml` for fitness direction, decimal precision, target score.
- **Score source priority.** `.score` sidecar file → eval cache by content hash. Header comment fallback removed (caused stale inconsistencies).
- **Durable progress.** Pipeline tab reads from `gen_progress.json` (survives crashes) not just ephemeral `run_state.json`.
- **Blueprints.** Routes split into `api` and `pages` for clean separation.
- **Data layer.** `data/` package isolates all filesystem scanning. Routes call `data.*` functions.

## Score Progression Chart

Interactive canvas chart with layered rendering. Architecture in `app.js`:

**Data pipeline** (`buildChartData()`):
- Takes all solutions (from `/api/solutions`) + gen-level progression as fallback
- Filters sentinel values and invalid scores
- Computes: `allPoints` (scatter), `genBests` (per-generation best), `runningBest`
  (monotonically improving), `records` (new all-time bests)

**Render layers** (`drawChart()`), bottom to top:
1. Grid lines + axis labels
2. Baseline dashed line
3. Target dashed line
4. Scatter dots (grey=finalized, blue=in-progress)
5. Record line + fill (green gradient under record stars)
6. Gen-best dots (blue circles)
7. Record stars (green stars)
8. Selection ring (highlighted point)
9. **Frontier annotations** (toggle) -- callout boxes on record points showing agent, score delta, central ideas, and label

**Interactivity**:
- **Hover**: nearest point tooltip (score, agent, file, badges)
- **Click**: select point; click empty to deselect
- **Scroll wheel**: zoom Y-axis centered on cursor
- **Double-click**: reset zoom
- **Auto-focus**: IQR-based zoom excluding outliers
- **Frontier toggle**: fetch `/api/frontier`, overlay annotated callouts on record stars

## Theme

Dark theme. Background `#0f172a`, surface `#1e293b`, accent green `#059669`.
Monospace (JetBrains Mono) for data, Outfit for headings.
