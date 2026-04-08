---
name: "Erdos-Turan Extension with Local Search"
type: idea
lifecycle: archived
confidence: 0.2
first_seen: generation_2
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_002
supported_by:
  - gen002_explore_1_sol03
  - gen002_explore_1_sol04
  - gen006_explore_1_sol02
  - gen006_explore_1_sol03
  - gen006_explore_1_sol04
  - gen007_explore_1_sol03
contradicted_by: []
related_ideas:
  - idea_009
  - idea_002
  - idea_022
  - idea_025
tags:
  - erdos-turan
  - local-search
  - extension
  - non-algebraic
  - archived
---

Combines Erdos-Turan (p=71) with greedy extension and local search (1-opt, 2-opt, LNS, VLNS).

**Best result:** 75 elements (gen 2, confirmed gens 6-7 with 30+ independent trials).

**Gen 7 update:** Ruzsa-Lindstrom primitive root p=71 + VLNS also converges to 75 ceiling (pattern_018). Multiple algebraic seed types (quadratic ET, exponential Ruzsa) converge to identical 75-element basin. 2-opt, LNS k=2-15, randomized restarts all fail to escape.

**Archived gen 7:** 75-ceiling confirmed as hard structural barrier (pattern_015). 30-element gap to frontier (105). Cluster_002 exhausted. Same evidence threshold as idea_003, idea_015, idea_016, idea_021 (all archived gen 6). No further investment warranted.
