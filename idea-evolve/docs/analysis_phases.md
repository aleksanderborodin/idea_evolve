# Analysis Phases

Three analysis phases run after agents finish each generation: Evaluator, System Critic,
and Consistency Reviewer.

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
