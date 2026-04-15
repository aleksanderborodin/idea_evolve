# Knowledge Base

All knowledge lives under `runs/{problem}/{attempt}/knowledge/`. It is cumulative —
updated by the evaluator and consistency reviewer each generation, read by every agent
and the architect.

## Directory Structure

```
knowledge/
├── state_of_affairs.md        # Strategic overview (Layer 0) — written by consistency reviewer
├── ideas/                     # Ideas (Layer 1) — organized by lifecycle
│   ├── active/                # Currently relevant ideas
│   ├── established/           # Proven ideas from past gens (high confidence)
│   ├── disputed/              # Ideas with conflicting evidence
│   ├── debunked/              # Disproven ideas (kept for reference)
│   └── archived/              # Obsolete ideas
├── patterns/                  # Recurring patterns (observational, less formal than ideas)
│   ├── active/
│   └── confirmed/
├── clusters/                  # Groupings of related ideas (no lifecycle)
├── facts/                     # Ground-truth facts (problem constants, verified results)
├── research/                  # Research agent outputs, archived by generation
│   └── gen{NNN}/research_{instance}/
└── experiments/               # Experimentator outputs, archived by generation
    └── gen{NNN}/experimentator_{instance}/
```

## File Schemas

### Idea (`ideas/{lifecycle}/idea_NNN.md`)

```yaml
---
id: idea_001
type: idea
name: "Human-readable name"
lifecycle: active | established | disputed | debunked | archived
confidence: 0.85          # 0.0–1.0
first_seen: generation_1
last_updated: generation_4
last_confirmed_gen: 4     # staleness tracking — flag if current_gen - last_confirmed_gen > threshold
cluster: cluster_003      # or: unclustered
supported_by:
  - gen003_explore_1_sol02
  - gen004_exploit_1_sol01
contradicted_by: []
related_ideas:
  - idea_005
  - idea_012
tags: [algebraic, construction, sidon]
---

Markdown body: description of the idea and evidence.
```

### Cluster (`clusters/cluster_NNN.md`)

```yaml
---
type: cluster
id: cluster_003
name: "Algebraic constructions"
member_ideas: [idea_001, idea_004, idea_009]
best_score: 89
best_solution: gen007_exploit_1_sol02
status: active
last_updated: generation_7
---

Markdown body: rationale for the grouping, shared strategy, open questions.
```

### Fact (`facts/fact_NNN.md`)

```yaml
---
id: fact_001
type: fact
name: "AGL(1,8) construction gives 73 elements"
confidence: 1.0
first_seen: generation_0
verified: true
source: user-provided | generated
tags: [baseline, algebraic]
---

Markdown body: derivation or source reference.
```

### Pattern (`patterns/{lifecycle}/pattern_NNN.md`)

```yaml
---
type: pattern
id: pattern_001
name: "Local search improves algebraic constructions"
lifecycle: active | confirmed
confidence: 0.75
first_seen: generation_3
last_updated: generation_6
evidence:
  - gen003_exploit_1_sol01
  - gen006_full_1_sol02
related_ideas: [idea_001, idea_003]
tags: [local-search, optimization]
---

Markdown body: description of when and how this pattern appears.
```

### State of Affairs (`state_of_affairs.md`)

```yaml
---
generation: 7
best_score: 89
trajectory: improving | plateaued | declining
last_updated_gen: 7
---

# Strategic Summary

Markdown body: current problem state, frontier approaches, exhausted directions,
open questions, recommended next steps.
```

## Lifecycle Transitions

Ideas move between lifecycle directories when the evaluator or consistency reviewer
updates them. The orchestrator reads the `lifecycle:` field from the updated frontmatter
and routes the file to the correct directory. Ghost files in the old directory are
deleted by `_remove_from_other_lifecycles()`.

```
active ──evidence grows──> established
active ──contradiction──> disputed ──confirmed false──> debunked
active ──no longer relevant──> archived
```

## Staleness

`config.staleness_threshold` (default 5) defines how many generations without a
`last_confirmed_gen` update before an idea is flagged as stale. The consistency reviewer
receives this threshold as guidance and should archive or demote stale ideas.

## Cluster Management

- Max clusters: `config.knowledge_hierarchy.max_clusters` (default 20, advisory).
- When the consistency reviewer removes or merges a cluster, `_fix_orphaned_cluster_refs()`
  scans all idea files and sets `cluster: unclustered` for ideas that referenced the removed cluster.

## Pre-concatenation for Agents

Before the evaluator runs, `_preconcat_knowledge()` merges all idea, cluster, pattern,
and fact files into a single `knowledge_dump.md` in the evaluator workspace. Total capped
at 80 KB; truncated entries include `[TRUNCATED — read full file for details]` markers.

This avoids the evaluator spending many turns reading dozens of individual files (SCALE-1).
Regular agents read files directly via their briefs.
