# Architect Phase

The architect is the first phase of every generation. It reads the current system state and
produces a plan: a `manifest.yaml` plus individual agent briefs.

## Input Files

| File | Purpose |
|------|---------|
| `problems/{id}/description.md` | Problem definition |
| `problems/{id}/constraints.md` | Hard and soft constraints |
| `knowledge/state_of_affairs.md` | Strategic overview from the last consistency review |
| `knowledge/clusters/*.md` | All idea cluster files |
| `knowledge/facts/*.md` | All ground-truth facts |
| `history/score_progression.md` | Score history across generations |
| `population/summary.md` | Population statistics |
| `history/coverage_matrix.md` | Which solution×idea combinations have been tried |
| `history/solution_idea_map.md` | Solution-to-idea associations |
| `briefs/gen{N-1}/prev_gen_reports.md` | Pre-concatenated reports from the previous generation (one file, capped at 40 KB — SCALE-13) |
| `feedback/system_recommendations.md` | Latest system critic recommendations |
| `feedback/experiment_suggestions/gen{N-1}.md` | Experiment suggestions from the previous critic pass |
| `feedback/consistency_reviews/gen{N-1}.md` | Latest consistency review |
| `user/interventions.md` | User edits detected between generations |

## Output Files

All outputs written to `briefs/gen{NNN}/`:

| File | Purpose |
|------|---------|
| `manifest.yaml` | Execution plan: agents array, strategy_summary, parallel_groups, per-agent timeout overrides |
| `manifest_reasoning.md` | Architect's strategic rationale (not read by agents, visible in dashboard) |
| `{type}_{instance}.md` | One brief per agent (e.g. `explore_1.md`, `full_1.md`) |
| `architect_report.md` | Architect's self-analysis. Copied to `reports/gen{NNN}/architect.md` |
| `.architect_done` | Empty sentinel file. Written last. `phase_status()` will not trust the manifest unless this exists |

## manifest.yaml Format

```yaml
generation: 1
strategy_summary: "One-sentence strategy for this generation"
agents:
  - type: explore       # explore | exploit | genetic | full | research | experimentator
    instance: 1         # sequential integer per type
    model: sonnet       # opus | sonnet | haiku
    brief: "briefs/gen001/explore_1.md"
    timeout: 1200       # optional, overrides config agent_default
parallel_groups:
  - ["explore_1", "full_1"]   # agents in same list run in parallel
  - ["exploit_1"]             # this group runs after the first completes
```

## Session Flow

```
Main work session  ──timeout──>  Wrap-up resume  ──fail──>  Failure report
     (architect writes briefs and manifest.yaml)
```

1. **Main session** — `launch_claude_session` with `agent_role="architect"` (routes to claude-code even when default harness is opencode).
2. **Wrap-up** — if main session times out, `resume_claude_session` on the same session id (preserves context). Timeout: `config.timeouts.architect_wrapup`.
3. **Manifest validation** — if manifest.yaml missing or YAML-invalid after both sessions, `_create_default_manifest()` generates a safe fallback.
4. **Path absolutization** — `_absolutize_brief_paths()` converts relative paths in briefs to absolute so agents can read them regardless of cwd.
5. **Sentinel** — `.architect_done` is written. `phase_status()` returns `"not_started"` if manifest exists but this file is absent (crash-recovery guard).

## Crash Recovery

If the orchestrator is killed while the architect is running:
- The architect process may keep running as an orphan and write a partial manifest.
- On restart, `phase_status()` sees `manifest.yaml` but no `.architect_done` → returns `"not_started"` → architect re-runs cleanly.
- `_kill_generation_orphans()` reads `gen_progress.json` and kills any still-running agent PIDs before the new run starts.

## Key Functions (orchestrator.py)

| Function | Description |
|----------|-------------|
| `run_architect(project_root, gen, config)` | Full architect phase orchestration |
| `build_architect_prompt(project_root, gen, config)` | Constructs architect context prompt |
| `_preconcat_prev_reports(project_root, gen, briefs_dir)` | Concatenates gen{N-1} reports into single file |
| `_absolutize_brief_paths(project_root, briefs_dir)` | Converts relative → absolute paths in all briefs |
| `_create_default_manifest(briefs_dir, gen, config)` | Fallback manifest when architect output is missing/invalid |
| `_write_architect_failure_report(...)` | Writes structured failure report to `reports/gen{NNN}/architect.md` |
