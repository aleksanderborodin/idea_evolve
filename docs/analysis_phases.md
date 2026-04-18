# Analysis Phases

Four analysis passes run during a generation:
a per-group **Light Evaluator** (phase 2.5, after each parallel group in multi-group
manifests) and three end-of-generation passes — **Heavy Evaluator**, **System Critic**,
**Consistency Reviewer**.

---

## Light Evaluator (Phase 2.5 — per parallel group)

Fast, surgical pass that runs **after each agent group** in a multi-group manifest
(except the final group — the heavy evaluator runs right after it anyway). Its job
is to unblock the NEXT group's agents by publishing any new ideas/patterns THIS
group produced, before the next group starts.

### When it runs / when it skips

Runs when ALL of:
- Manifest has more than one group in `parallel_groups`
- The current group is not the final group
- The group produced at least one artifact (solution, report, research finding, or experiment)
- The problem opts in (see "Enable/disable" below)

Skipped otherwise (including on single-group manifests — the heavy evaluator is next anyway).

### Enable/disable — resolved by `orchestrator.evaluator_light_enabled()`

First match wins:

1. `problems/<id>/metrics.yaml` → `evaluator_light_enabled: true|false` (per-problem override)
2. `user/config.yaml` → `analysis.evaluator_light.enabled` (global default)
3. `problems/_shared/constants.py` → `DEFAULT_EVALUATOR_LIGHT_ENABLED = True` (hardcoded default)

Strawberry ships with `evaluator_light_enabled: false` because `concurrency: 1`
makes every parallel_group a single solution agent — a light eval would run
between every agent with no multi-agent findings to consolidate. Parallel-eval
problems (megaminx, gemm, sidon, permcodes) leave it at default `true`.
See [docs/problem_design_guide.md §9.5](problem_design_guide.md).

### Input files

| File | Purpose |
|------|---------|
| `population/gen{NNN}/{agent}/` | Solutions + .score + observations for THIS group only |
| `reports/gen{NNN}/{agent}.md` | Agent debrief for THIS group only |
| `knowledge/research/gen{NNN}/{agent}/` | Research findings from this group's research agents |
| `knowledge/experiments/gen{NNN}/{agent}/` | Experiments from this group's experimentator agents |
| `knowledge/ideas/active/` + `knowledge/ideas/established/` | Existing ideas — for dedup checks before creating new |
| `knowledge/state_of_affairs.md` | Current Layer 0 — context only, not modified |
| `knowledge/group_notes/gen{NNN}/group*.md` | Prior groups' notes from EARLIER in this generation |

### Workspace

`workspace/gen{NNN}_evaluator_light_group{K}/output/`

```
output/
├── new_ideas/*.md        # ONLY genuinely new ideas (strict dedup rules)
├── new_patterns/*.md     # ONLY genuinely new patterns
├── group_notes.md        # 200-400 word summary for NEXT group's agents
└── report.md             # Debrief read by Heavy Evaluator at end of gen
```

**Explicitly NOT produced:** state_of_affairs.md, coverage_matrix.md,
solution_idea_map.md, updated_ideas/, updated_clusters/, generation_snapshot.md,
agent_gaps.md, evaluator_report.md. Those belong to the Heavy Evaluator.

### Output movement — `move_light_evaluator_outputs()`

```
new_ideas/*.md    → knowledge/ideas/{lifecycle}/     (same lifecycle routing as heavy)
new_patterns/*.md → knowledge/patterns/{lifecycle}/
group_notes.md    → knowledge/group_notes/gen{NNN}/group{K}.md
report.md         → reports/gen{NNN}/evaluator_group{K}.md
```

### Progress tracking

`briefs/gen{NNN}/gen_progress.json` gains a `light_evaluators` block:

```json
{
  "light_evaluators": {
    "group0": {
      "status": "complete",
      "agents": ["explore_1", "explore_2"],
      "started_at": "...",
      "completed_at": "..."
    },
    "group1": { "status": "skipped", "reason": "no_output" }
  }
}
```

Possible statuses: `running`, `complete`, `skipped`, `failed`.

### Key functions

| Function | Description |
|----------|-------------|
| `run_light_evaluator(project_root, gen, group_idx, names, config)` | Runs one light evaluator |
| `build_light_evaluator_prompt(...)` | Scoped prompt — only this group's agent outputs |
| `move_light_evaluator_outputs(project_root, gen, group_idx)` | Routes outputs |
| `_light_evaluator_name(group_idx)` | Workspace / gen_progress key: `evaluator_light_group{K}` |

### Defaults

| Setting | Default | Per-problem | Global config |
|---------|---------|-------------|---------------|
| Enabled | `true` | `metrics.yaml: evaluator_light_enabled` | `analysis.evaluator_light.enabled` |
| Model | `sonnet` | — | `analysis.evaluator_light.model` |
| Timeout | 900s | — | `timeouts.evaluator_light` |
| Max turns | 400 | — | `max_turns.evaluator_light` |

Only the enable flag supports per-problem override; model/timeout/max_turns
are global so tuning is centralized.

### Dashboard surface

- Sub-phase pipeline node (`pn-lighteval`) on the Pipeline tab — dashed border, per-group tag
- API: `GET /api/generation/<gen>/light_evaluators` → list of group status entries
- Scanner: `get_light_evaluator_summary(gen)` + phase value `light_evaluator_running`

---

## Evaluator (Phase 3)

Reads all agent outputs, scores solutions, extracts knowledge (ideas/patterns/facts) into
the shared knowledge base.

### Input Files

| File | Purpose |
|------|---------|
| `population/gen{NNN}/*/sol*.py` | All solutions from this generation |
| `population/gen{NNN}/*/sol*.score` | Sidecar score files |
| `reports/gen{NNN}/*.md` | All agent debrief reports |
| `knowledge/` (full tree) | Pre-concatenated by orchestrator into single `knowledge_dump.md` in workspace (SCALE-1 optimization — avoids 100+ individual file reads) |

### Workspace

`workspace/gen{NNN}_evaluator/output/`

```
output/
├── evaluator_report.md        # Evaluation summary + recommendations
├── generation_snapshot.md     # Generation summary (copied to reports/gen{NNN}/evaluator.md)
├── solution_idea_map.md       # Which ideas each solution implements (→ history/)
├── coverage_matrix.md         # Idea×solution coverage (→ history/, capped to 30 ideas)
├── new_ideas/                 # New idea .md files (YAML frontmatter + body)
│   └── idea_042.md
├── updated_ideas/             # Updated versions of existing ideas
├── new_patterns/              # New pattern .md files
└── updated_clusters/          # Updated cluster .md files
```

### Output Movement — `move_evaluator_outputs()`

```
new_ideas/*.md         →  knowledge/ideas/{lifecycle}/      (reads lifecycle: field in frontmatter)
updated_ideas/*.md     →  knowledge/ideas/{lifecycle}/      (removes from old lifecycle dir)
new_patterns/*.md      →  knowledge/patterns/{lifecycle}/
updated_clusters/*.md  →  knowledge/clusters/               (fixes orphaned cluster refs)
generation_snapshot.md →  reports/gen{NNN}/evaluator.md
solution_idea_map.md   →  history/solution_idea_map.md      (overwrites)
coverage_matrix.md     →  history/coverage_matrix.md        (overwrites)
```

### Key Functions

| Function | Description |
|----------|-------------|
| `run_evaluator(project_root, gen, config)` | Full evaluator phase |
| `build_evaluator_prompt(project_root, gen, config)` | Constructs prompt with knowledge dump path |
| `_preconcat_knowledge(project_root, ws)` | Pre-concatenates all knowledge into one file (SCALE-1) |
| `move_evaluator_outputs(project_root, gen)` | Moves all evaluator outputs |
| `_remove_from_other_lifecycles(project_root, filename, lifecycle)` | Cleans up ghost files when idea moves lifecycle |
| `_fix_orphaned_cluster_refs(project_root, removed_clusters)` | Updates ideas whose cluster was deleted |

---

## System Critic (Phase 4)

Diagnoses pipeline problems, identifies what's working and what isn't, writes recommendations
for the next architect.

### Input Files

| File | Purpose |
|------|---------|
| `reports/gen{NNN}/*.md` | All agent reports and architect report from this generation |
| `history/generations/` | Past generation snapshots |
| `knowledge/` | Current knowledge state |
| `feedback/system_recommendations.md` | Previous generation's recommendations |
| `user/config.yaml` | Current configuration |

### Workspace

`workspace/gen{NNN}_system_critic/output/`

```
output/
├── system_analysis.md          # Detailed analysis of what happened this generation
├── system_recommendations.md   # Actionable recommendations for next architect
├── experiment_suggestions.md   # Specific experiments to try
└── report.md                   # Debrief summary
```

### Output Movement — `move_critic_outputs()`

```
system_analysis.md        →  feedback/system_analysis/gen{NNN}.md
system_recommendations.md →  feedback/system_recommendations.md  (current, archives previous)
                           →  feedback/system_recommendations_archive/gen{NNN}.md  (archive)
experiment_suggestions.md →  feedback/experiment_suggestions/gen{NNN}.md
report.md                 →  reports/gen{NNN}/system_critic_debrief.md
```

### Model

Uses `config.analysis.system_critic.model` (default `sonnet` — lighter-weight than evaluator).

---

## Consistency Reviewer (Phase 5)

Audits the knowledge base for coherence, staleness, and contradictions. Rewrites the
State of Affairs strategic summary.

### When It Runs

- Every `config.consistency_review_interval` generations (default every generation; clamped minimum 3 in code).
- Immediately if the evaluator flags a `strategic_shift` in its report and `config.emergency_review_on_strategic_shift: true`.

### Input Files

| File | Purpose |
|------|---------|
| `knowledge/state_of_affairs.md` | Current strategic summary |
| `knowledge/ideas/*/` | All ideas across all lifecycle stages |
| `knowledge/clusters/*.md` | Cluster definitions |
| `knowledge/patterns/*/` | All patterns |
| `reports/gen{NNN}/evaluator.md` | This generation's evaluator findings |

### Workspace

`workspace/gen{NNN}_consistency_reviewer/output/`

```
output/
├── state_of_affairs.md      # Updated strategic overview (replaces knowledge/state_of_affairs.md)
├── consistency_review.md    # Detailed review notes
├── updated_ideas/           # Coherence-corrected idea files
└── updated_clusters/        # Coherence-corrected cluster files
```

### Output Movement — `move_consistency_outputs()`

```
state_of_affairs.md    →  knowledge/state_of_affairs.md     (overwrites)
updated_ideas/*.md     →  knowledge/ideas/{lifecycle}/       (lifecycle-aware routing)
updated_clusters/*.md  →  knowledge/clusters/                (fixes orphaned refs)
consistency_review.md  →  feedback/consistency_reviews/gen{NNN}.md
```

### Model

Uses `config.analysis.evaluator.model` setting (same as evaluator, defaults to `opus` — needs high reasoning for knowledge coherence work).

---

## Shared Session Flow (all analysis phases)

All three phases use `_run_analysis_with_debrief()`:

```
Main session  ──timeout──>  Wrap-up resume  ──fail──>  Debrief recovery
```

The same three-phase timeout pattern as agent work sessions. The analysis phase is identified
by a role string (`"evaluator"`, `"system_critic"`, `"consistency_reviewer"`) which is logged
to `gen_progress.json`.

## Tool Permissions

Analysis phases use: `Read`, `Write`, `Glob`, `Grep` — no `Bash` (they don't run code).
