# Dashboard

Web UI for tracking evolution runs. Flask app at `dashboard/app.py`.
Reads directly from the filesystem — no database.

```bash
source venv/bin/activate
python dashboard/app.py          # http://localhost:5000
python dashboard/app.py --port 8080
python dashboard/app.py --debug  # hot reload
```

## Architecture

```
dashboard/
├── app.py                  # Flask app entry point, blueprint registration
├── routes/
│   ├── api.py              # All JSON endpoints (/api/*)
│   └── pages.py            # HTML shell (single-page, tabs load via JS)
├── data/
│   ├── scanner.py          # Filesystem scanning functions
│   └── config.py           # Path helpers
├── templates/
│   ├── base.html           # Main layout
│   └── *.html              # Tab partials
└── static/
    ├── css/
    └── js/
```

## Tabs and Data Sources

### Overview Tab
**Endpoint:** `GET /api/overview?problem=X&attempt=Y`

Reads:
- `history/run_state.json` — live orchestrator status, PID, current phase/gen, agent statuses
- `history/all_scores.json` — score progression data
- `history/timing.json` — per-phase timing
- `history/generations/gen*.md` — generation snapshots
- `knowledge/state_of_affairs.md` — staleness check (how many gens since last update)
- `user/config.yaml` — target score, fitness direction

Shows: score progression chart with baseline + target lines, generation timeline, system status bar (phase/gen/elapsed), live status beacon (green=running, gray=idle, amber=stale >2min, red=crashed PID), knowledge lifecycle counts.

**Annotated Frontier:** `GET /api/frontier` — overlays callouts on record-breaking solutions showing agent name, score delta, central ideas.

### Pipeline Tab
**Endpoint:** `GET /api/generation/<gen>?problem=X&attempt=Y`

Reads:
- `briefs/gen{NNN}/gen_progress.json` — per-agent status (waiting/running/wrapping_up/done/failed)
- `briefs/gen{NNN}/manifest.yaml` — planned agents and groups
- `history/run_state.json` — current phase and agent statuses
- `history/timing.json` — phase timing

Shows: 6-phase pipeline with active phase highlighted, live agent cards with status and elapsed time, agent type grid with config (max_instances, max_turns, model, purpose).

### Architecture Tab
**Endpoint:** `GET /api/generation/<gen>?problem=X&attempt=Y`

Reads:
- `briefs/gen{NNN}/manifest.yaml` — agent plan
- `history/generations/gen{NNN}.md` — generation snapshot
- `reports/gen{NNN}/` — all reports

Shows: run directory structure, knowledge hierarchy visualization, data flow diagram.

### Solutions Tab
**Endpoint:** `GET /api/solutions?problem=X&attempt=Y`

Reads:
- `population/gen*/*/sol*.py` — all solution files
- `population/gen*/*/sol*.score` — sidecar score JSON (primary source)
- `history/eval_cache.json` — fallback score lookup by content hash

Shows: sortable table of all solutions, color-coded by validity, sorted best-first (respects `higher_is_better` / `lower_is_better` from `metrics.yaml`). Scores displayed with precision from `metrics.yaml.decimals`.

### Knowledge Tab
**Endpoint:** `GET /api/knowledge?problem=X&attempt=Y`

Reads:
- `knowledge/ideas/*/` — all lifecycle directories
- `knowledge/clusters/*.md`
- `knowledge/patterns/*/`
- `knowledge/facts/*.md`
- `knowledge/research/`
- `knowledge/experiments/`

Shows: three-layer hierarchy (State of Affairs → Clusters → Ideas/Patterns/Facts), lifecycle counts, staleness indicators.

**Single item:** `GET /api/knowledge/<kind>/<item_id>` — returns full file with frontmatter parsed + markdown body.

**Coverage:** `GET /api/knowledge/coverage` — reads `history/coverage_matrix.md` and `history/solution_idea_map.md`.

### Reports Tab
**Endpoint:** `GET /api/reports?problem=X&attempt=Y` and `GET /api/reports/<int:gen>`

Reads:
- `reports/gen{NNN}/*.md` — architect, evaluator, agent debrief, system_critic_debrief reports
- `history/generations/gen{NNN}.md` — generation snapshots

Shows: markdown-rendered agent and phase reports grouped by generation.

## Multi-Problem Navigation

Header has a problem/attempt selector flyout. All API endpoints accept `?problem=X&attempt=Y`
query params. Available problems discovered via:

**Endpoint:** `GET /api/problems`

Reads: `runs/*/attempt_*/history/run_state.json` and `runs/*/attempt_*/population/` for all
problems and attempts. Returns summary stats and status indicators.

Selection stored in `localStorage`.

## Live Orchestrator Status

The beacon in the header reads `history/run_state.json`:

| Beacon | Condition |
|--------|-----------|
| Green | `status: "running"` and PID is alive and updated <2 min ago |
| Gray | `status: "stopped"` or no run_state.json |
| Amber | `status: "running"` but `last_updated` > 2 min ago |
| Red | `status: "running"` but PID no longer exists |

**Dynamic refresh rate:** 10s when orchestrator is running, 60s when idle.

## Score Display

- Source priority: `.score` sidecar JSON → eval cache by content hash.
- Fitness direction from `problems/{id}/metrics.yaml` → `higher_is_better`.
- Decimal precision from `metrics.yaml` → `decimals`.
- Invalid solutions (`.score` has `is_valid: 0`) displayed separately / color-coded.
- Progression chart shows baseline from `population/gen000/` initial programs and target line.

## Key Scanner Functions (data/scanner.py)

| Function | Input Files |
|----------|-------------|
| `get_run_state()` | `history/run_state.json` |
| `get_solutions()` | `population/gen*/*/sol*.py`, `.score`, `eval_cache.json` |
| `get_knowledge()` | `knowledge/ideas/*/`, `clusters/`, `facts/`, `patterns/*/` |
| `get_reports(gen)` | `reports/gen{NNN}/*.md` |
| `get_manifest(gen)` | `briefs/gen{NNN}/manifest.yaml` |
| `get_timing_data()` | `history/timing.json` |
| `get_coverage_matrix()` | `history/coverage_matrix.md` |
| `get_state_of_affairs_staleness()` | `knowledge/state_of_affairs.md`, `history/generations/gen*.md` |
| `get_knowledge_lifecycle_counts()` | `knowledge/ideas/*/`, `patterns/*/` |
