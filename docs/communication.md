# Engine ↔ Dashboard Communication

The orchestrator and dashboard are **decoupled**: the engine writes files, the dashboard
reads them. There is no live API, no socket, no shared database between them. Both can
run simultaneously without coordination.

```
orchestrator.py  ──writes──▶  runs/{problem}/{attempt}/  ◀──reads──  dashboard/app.py
```

## Protocol: file-based, one-way

- **Engine** (orchestrator): writes state to `runs/{problem}/{attempt}/history/`,
  `briefs/`, `population/`, `knowledge/`, `reports/`, `feedback/`.
- **Dashboard** (Flask): polls the filesystem. Never writes back to the run directory.
- **Refresh cadence**: dashboard reads `run_state.json` on every request to check
  orchestrator liveness; tabs auto-refresh every 10s when orchestrator is running,
  every 60s when idle.

## Files the Engine Writes / Dashboard Reads

### Live status (real-time)

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `history/run_state.json` | `_write_run_state()` at every phase + agent transition | Every dashboard tab's beacon; Pipeline tab agent cards | `status`, `current_gen`, `current_phase`, `pid`, `last_updated`, `agents` dict |

`run_state.json` is the **heartbeat**. The dashboard checks PID liveness and timestamp
freshness (`last_updated`) to determine the beacon color:

| Beacon | Condition |
|--------|-----------|
| Green | `status: "running"`, PID alive, `last_updated` < 2 min ago |
| Amber | `status: "running"`, but `last_updated` > 2 min ago |
| Red | `status: "running"`, but PID does not exist in `/proc` |
| Gray | `status: "stopped"` or file missing |

### Per-generation progress (durable)

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `briefs/gen{NNN}/gen_progress.json` | `run_single_agent()` per status change | Pipeline tab agent cards | Per-agent status, PIDs, session ids, output-move flag |
| `briefs/gen{NNN}/manifest.yaml` | Architect phase | Pipeline tab agent grid, phase_status() | Planned agents, parallel groups, per-agent config |

`gen_progress.json` is the **durable** status store. Unlike `run_state.json` (overwritten
wholesale at each phase), `gen_progress.json` accumulates individual agent completions and
survives orchestrator restarts. Dashboard reads it to show per-agent cards.

### Scores and solutions

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `population/gen*/*/sol*.py` | Agent sessions | Solutions tab | Solution source code |
| `population/gen*/*/sol*.score` | `evaluate.py` | Solutions tab, Overview progression | JSON: `fitness`, `is_valid`, `eval_time_s`, `hash` |
| `history/all_scores.json` | `update_rankings()` | Overview chart | `[[score, path], ...]` all-time list |
| `history/eval_cache.json` | `evaluate.py` | Solutions tab (fallback) | SHA-256 → score cache |
| `history/score_progression.md` | `_update_score_progression()` | (human-readable only) | Markdown table |
| `population/best.py` | `update_rankings()` | Solutions tab highlight | Symlink to top solution |
| `population/summary.md` | `update_rankings()` | (human-readable only) | Population stats |

### Timing and history

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `history/timing.json` | `_record_timing()` at every phase | Overview tab, Pipeline timing labels | `{generations: {gen{NNN}: {phase: seconds}}}` |
| `history/generations/gen{NNN}.md` | Evaluator / `_finalize_generation()` | Overview timeline, Architecture tab | Generation snapshot with scores + timing |
| `history/coverage_matrix.md` | Evaluator | Knowledge tab coverage | Idea × solution sparse matrix |
| `history/solution_idea_map.md` | Evaluator | Knowledge tab coverage | Per-solution idea list |

### Knowledge

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `knowledge/state_of_affairs.md` | Consistency Reviewer | Overview staleness badge, Knowledge tab | Strategic summary with generation frontmatter |
| `knowledge/ideas/{lifecycle}/idea_*.md` | Evaluator, Consistency Reviewer | Knowledge tab hierarchy, lifecycle counts | Idea frontmatter + evidence body |
| `knowledge/clusters/cluster_*.md` | Evaluator, Consistency Reviewer | Knowledge tab | Cluster frontmatter + rationale |
| `knowledge/patterns/{lifecycle}/pattern_*.md` | Evaluator | Knowledge tab | Pattern frontmatter + body |
| `knowledge/facts/fact_*.md` | Evaluator | Knowledge tab | Fact frontmatter + body |
| `knowledge/research/gen{NNN}/research_N/` | Research agent via `move_research_outputs()` | Knowledge tab | findings.md, sources.md |
| `knowledge/experiments/gen{NNN}/experimentator_N/` | Experimentator via `move_experiment_outputs()` | Knowledge tab | Experiment results |

### Reports and feedback

| File | Written by | Read by | Content |
|------|-----------|---------|---------|
| `reports/gen{NNN}/*.md` | Each phase (architect, agents, evaluator, critic) | Reports tab | Debrief markdown, one file per agent/phase |
| `feedback/system_recommendations.md` | System Critic | (human-readable; architect reads it too) | Latest recommendations |
| `feedback/system_analysis/gen{NNN}.md` | System Critic | Reports tab | Detailed critic analysis |
| `feedback/consistency_reviews/gen{NNN}.md` | Consistency Reviewer | Reports tab | Consistency review notes |

### Config (read-only at runtime)

| File | Read by engine | Read by dashboard | Content |
|------|---------------|------------------|---------|
| `idea-evolve/user/config.yaml` | Orchestrator throughout | Overview tab (target score) | All evolution params, harness config, model aliases |
| `idea-evolve/problems/{id}/metrics.yaml` | `evaluate.py`, `validate.py` | Solutions tab (score direction + decimals) | `higher_is_better`, `target`, `decimals`, `sentinel_value` |
| `idea-evolve/problems/{id}/description.md` | Agent briefs | (not currently shown) | Problem statement |

## Multi-Problem Discovery

Dashboard discovers all problems via `GET /api/problems`, which scans:

```
runs/*/attempt_*/history/run_state.json   → status + gen
runs/*/attempt_*/population/              → solution count
```

No index file. Discovery is purely filesystem-based.

## What the Dashboard Never Does

- Never writes to `runs/` or any engine directory
- Never signals the orchestrator (no kill, no pause, no resume)
- Never calls `evaluate.py` or any Python engine code
- No shared in-process state (they are separate processes)

To interact with a running orchestrator, use the CLI directly — the dashboard is read-only.
