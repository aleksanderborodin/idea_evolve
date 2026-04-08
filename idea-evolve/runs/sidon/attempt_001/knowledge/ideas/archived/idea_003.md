---
id: idea_003
type: idea
name: "Difference-Aware Construction"
lifecycle: archived
confidence: 0.2
first_seen: generation_0
last_updated: generation_6
last_confirmed_gen: 4
supported_by: [gen004_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_016, idea_015]
cluster: cluster_002
tags: [construction, difference-aware, heuristic, greedy-variant, archived]
---

Instead of checking violations after the fact, maintain the set of used differences explicitly. When choosing the next element to add, pick one that uses "rare" differences (large gaps in the difference spectrum). This leaves more room for future elements.

Used peripherally in several solutions and now centrally tested via idea_016 (min-blocking greedy). Gen 4 confirmed that the corrected min-blocking implementation achieves 69 elements — identical to the Fibonacci ordering ceiling (idea_015). The concept has practical value but does not break the non-algebraic greedy ceiling of ~69.

**Gen 6 consistency review**: Archived. Ceiling 69, 36 elements below frontier (105). 2 generations stale (last confirmed gen 4). No further value as a standalone idea. The cluster_002 (search-based methods) is exhausted.
