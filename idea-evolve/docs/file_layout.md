# File Layout Reference

Complete directory tree for a run at `runs/{problem_id}/{attempt_id}/`.
Directories marked **(INPUT)** are read by agents/phases; **(OUTPUT)** are written;
**(STATE)** are orchestrator bookkeeping.

```
runs/{problem_id}/{attempt_id}/
│
├── briefs/                             (STATE + INPUT to agents)
│   └── gen{NNN}/
│       ├── manifest.yaml               Execution plan: agents, groups, per-agent timeouts
│       ├── manifest_reasoning.md       Architect's strategic rationale
│       ├── {type}_{instance}.md        Per-agent brief (e.g. explore_1.md)
│       ├── architect_report.md         Architect's self-analysis
│       ├── prev_gen_reports.md         Pre-concat of gen{N-1} reports (SCALE-13)
│       ├── .architect_done             Empty sentinel: architect phase complete
│       ├── gen_progress.json           Per-agent status: pending/running/complete/failed
│       └── gen_progress.lock
│
├── population/                         (OUTPUT of agent work, INPUT to evaluator)
│   ├── best.py                         Symlink to highest-scoring solution overall
│   ├── summary.md                      Population statistics
│   ├── top/                            Top N solutions (convenience links)
│   └── gen{NNN}/
│       └── {type}_{instance}/          e.g. explore_1/, research_1/
│           ├── sol01.py                Solution code
│           ├── sol01.score             Sidecar JSON: {fitness, is_valid, eval_time_s, ...}
│           ├── sol02.py
│           ├── sol02.score
│           └── observations.md         Agent's analysis notes
│
├── knowledge/                          (INPUT + OUTPUT across all phases)
│   ├── state_of_affairs.md             Strategic overview (Layer 0) — written by consistency reviewer
│   ├── ideas/
│   │   ├── active/idea_NNN.md
│   │   ├── established/idea_NNN.md
│   │   ├── disputed/idea_NNN.md
│   │   ├── debunked/idea_NNN.md
│   │   └── archived/idea_NNN.md
│   ├── patterns/
│   │   ├── active/pattern_NNN.md
│   │   └── confirmed/pattern_NNN.md
│   ├── clusters/cluster_NNN.md
│   ├── facts/fact_NNN.md
│   ├── research/
│   │   └── gen{NNN}/research_{N}/      Research agent archives
│   │       ├── findings.md
│   │       └── sources.md
│   └── experiments/
│       └── gen{NNN}/experimentator_{N}/ Experimentator archives
│           ├── helpers/                Validated helper code deployed to problems/
│           └── sol*.py
│
├── reports/                            (OUTPUT — debrief reports from all phases)
│   └── gen{NNN}/
│       ├── architect.md                From briefs/gen{NNN}/architect_report.md
│       ├── {type}_{instance}.md        From workspace output/report.md (e.g. explore_1.md)
│       ├── evaluator.md                From evaluator workspace generation_snapshot.md
│       ├── evaluator_debrief.md        Evaluator debrief if separate from main report
│       └── system_critic_debrief.md    System critic debrief
│
├── feedback/                           (OUTPUT of analysis phases, INPUT to architect)
│   ├── system_recommendations.md       Latest critic recommendations (overwritten each gen)
│   ├── system_recommendations_archive/
│   │   └── gen{NNN}.md                 Archived previous recommendations
│   ├── system_analysis/
│   │   └── gen{NNN}.md                 Detailed critic analysis
│   ├── consistency_reviews/
│   │   └── gen{NNN}.md                 Consistency review notes
│   ├── experiment_suggestions/
│   │   └── gen{NNN}.md                 Suggested experiments from critic
│   └── experiment_requests/            Agent-requested experiments (INPUT to architect)
│       └── gen{NNN}/
│           └── {type}_{instance}.md
│
├── history/                            (STATE — cross-generation bookkeeping)
│   ├── run_state.json                  Live orchestrator state: PID, phase, agent statuses
│   ├── run_state.json.lock
│   ├── all_scores.json                 All evaluated scores: [[score, path], ...]
│   ├── all_scores.json.lock
│   ├── eval_cache.json                 Content-hash → score cache (never pruned)
│   ├── eval_cache.json.lock
│   ├── score_progression.md            Human-readable score history table
│   ├── solution_idea_map.md            Solution → idea mapping (written by evaluator)
│   ├── coverage_matrix.md              Idea × solution coverage (sparse, top 30 ideas)
│   ├── timing.json                     Per-phase timing: {generations: {gen{NNN}: {architect: Ns, ...}}}
│   ├── timing.json.lock
│   └── generations/
│       └── gen{NNN}.md                 Generation snapshot with timing (INPUT to architect/dashboard)
│
└── workspace/                          (INTERMEDIATE — deleted after successful output move)
    ├── gen{NNN}_{type}_{instance}/     Per-agent workspace
    │   ├── prompt.md                   Copy of agents/{type}.md
    │   ├── brief.md                    Copy of briefs/gen{NNN}/{type}_{instance}.md
    │   └── output/                     Agent writes all work here
    │       ├── report.md               REQUIRED final debrief
    │       ├── sol*.py
    │       ├── sol*.score
    │       ├── observations.md
    │       ├── experiment_requests.md
    │       └── sandbox/                Scratch (deleted on move)
    ├── gen{NNN}_evaluator/
    │   └── output/
    │       ├── evaluator_report.md
    │       ├── generation_snapshot.md
    │       ├── solution_idea_map.md
    │       ├── coverage_matrix.md
    │       ├── new_ideas/
    │       ├── updated_ideas/
    │       ├── new_patterns/
    │       └── updated_clusters/
    ├── gen{NNN}_system_critic/
    │   └── output/
    │       ├── system_analysis.md
    │       ├── system_recommendations.md
    │       ├── experiment_suggestions.md
    │       └── report.md
    └── gen{NNN}_consistency_reviewer/
        └── output/
            ├── state_of_affairs.md
            ├── consistency_review.md
            ├── updated_ideas/
            └── updated_clusters/
```

## Global Resources (outside runs/)

These live at the `idea-evolve/` root and are shared across all problems and attempts:

```
idea-evolve/
├── orchestrator.py          Main loop (~3200 lines)
├── orchestrator_harness.py  Harness adapters (ClaudeCodeAdapter, OpenCodeAdapter)
├── agents/                  Prompt templates — one .md per agent type
│   ├── architect.md
│   ├── explore.md
│   ├── exploit.md
│   ├── full.md
│   ├── genetic.md
│   ├── research.md
│   ├── experimentator.md
│   ├── evaluator.md
│   ├── system_critic.md
│   └── consistency_review.md
├── prompts/                 Shared prompt fragments
├── user/
│   ├── config.yaml          All evolution parameters, harness config, model aliases
│   └── initial_ideas.md     Bootstrap ideas seeded before gen 1
├── problems/                Problem definitions (read-only at runtime)
│   └── {problem_id}/
│       ├── description.md
│       ├── constraints.md
│       ├── metrics.yaml     Fitness direction, target, decimals, sentinel_value
│       ├── evaluate.py      Evaluation harness (caches by content hash)
│       ├── validate.py      Correctness check
│       ├── helpers/         Shared helper code (core.py + experimentator-deployed)
│       └── initial_programs/ Baseline solutions seeded as gen 0
├── docs/                    Technical documentation (this folder)
└── tests/
    └── test_adapters.py     Adapter contract tests
```

## Score Sidecar Format (`.score` files)

```json
{
  "fitness": 89,
  "is_valid": 1,
  "eval_time_s": 0.042,
  "metric_name": "fitness",
  "hash": "sha256:..."
}
```

`is_valid: 0` means `validate.py` rejected the solution. Score is the `sentinel_value`
from `metrics.yaml` (typically 0). Invalid solutions are excluded from rankings.

## File Locking Conventions

Files written by multiple threads or processes use `.lock` sidecar files with `fcntl.flock`:
- `run_state.json.lock`
- `all_scores.json.lock`
- `eval_cache.json.lock`
- `timing.json.lock`
- `gen_progress.lock`
