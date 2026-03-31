# Idea Evolve Dashboard

Web-based monitoring UI for Idea Evolve evolutionary runs.

## Setup

```bash
# From project root (idea_evolve/)
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
| **Overview** | Score gauge, metrics, phase indicator, **interactive score progression chart** (see Chart section below), generation timeline. Auto-refreshes every 60s. Manual refresh button in header. Solutions data fetched eagerly for chart scatter plot. |
| **Pipeline** | Visual 6-phase generation loop (Architect > Agents > Evaluator > Critic > Consistency > Finalize). **Live agent panels** showing currently running agents with real-time status, solution counts, scores, and expandable detail tables. Auto-refreshes every 60s. Agent type cards with config. Data flow diagram. |
| **Architecture** | Collapsible file tree browser (color-coded by directory). Knowledge hierarchy diagram (L0/L1/L2). Idea lifecycle flow. |
| **Solutions** | Sortable, filterable table of all solutions with full decimal precision. Agent column shows type+instance (e.g., `explore_1`). Sorted best-first respecting fitness direction. Filter by generation or agent type. |
| **Knowledge** | State of Affairs, ideas grid with lifecycle filters, facts, patterns, clusters. **All items are clickable** — opens a detail modal with full body text, metadata, and relationship tags (supported_by, contradicted_by, related_ideas, member_ideas). Close with X, click-outside, or Escape. |
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
| `GET /api/agents/active` | Currently running/recent agents with solution counts, scores, status |
| `GET /api/knowledge/<kind>/<id>` | Full detail for a single knowledge item (idea, fact, pattern, cluster) |
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
- **Filesystem-based.** Backend scans `../idea-evolve/` on each request. No database.
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

## Score Progression Chart

Interactive canvas chart with layered rendering. Architecture in `app.js`:

**Data pipeline** (`buildChartData()`):
- Takes all solutions (from `/api/solutions`) + gen-level progression as fallback
- Filters sentinel values and invalid scores
- Computes: `allPoints` (scatter), `genBests` (per-generation best), `runningBest`
  (monotonically improving), `records` (new all-time bests)

**Render layers** (`drawChart()`), bottom to top:
1. Grid lines + axis labels
2. Baseline dashed line (right-aligned label to avoid overlap)
3. Target dashed line (left-aligned label)
4. Scatter dots — every valid solution as a small dot (grey=finalized, blue=in-progress)
5. Record line + fill — green gradient under a straight line connecting record stars
6. Gen-best dots — medium blue circles for each generation's best
7. Record stars — green star markers where a new all-time best was achieved
8. Selection ring — highlight on the clicked point

**Interactivity**:
- **Hover**: nearest point within 20px shows tooltip (score, agent, file, record/gen-best badge)
- **Click**: selects a point, draws selection ring; click empty space to deselect
- **Scroll wheel**: zoom Y-axis in/out centered on cursor position
- **Double-click**: reset zoom to auto-focus
- **Auto-focus button**: toggle between IQR-based auto-focus (excludes outliers) and full range
- Tooltip auto-positions to avoid chart edges
- Outlier indicators ("▲ N above" / "▼ N below") shown when points are clipped by zoom

**Direction-aware**: respects `higher_is_better` from metrics.yaml. For lower-is-better,
"better" arrow points down, best-so-far line trends downward, ascending sort in tables.

**Sentinel-aware**: sentinel values (e.g., 1000.0 for eval errors) are filtered at every
level — config export, scanner, API, JS chart data, and sort keys.

**Extending the chart**:
- Add a new visual layer by adding a draw section in `drawChart()` render sequence
- Add new data dimensions by extending the `buildChartData()` return object
- For new interactivity, extend `chartHitTest()` (currently point-based)
- `chartPoints[]` stores px/py screen coordinates set during render for hit testing

## Design

Light theme with clean card-based layout. Accent green (#059669) for scores/progress,
blue for generations/population, purple for briefs/planning, amber for reports/warnings.
Monospace (JetBrains Mono) for data, Outfit for headings.
