---
id: idea_011
type: idea
name: "Erdos-Turan Extension with Local Search"
lifecycle: active
confidence: 0.35
first_seen: generation_2
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_002
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol04, gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_009, idea_002, idea_022]
tags: [erdos-turan, local-search, extension, non-algebraic]
---

Combines Erdos-Turan construction (p=71) with greedy extension and 1-opt local search.
Best result: 75 elements (gen 2, confirmed gen 6).

**Gen 6 results (explore_1):**
- ET(71) + 1-opt + 2-opt + LNS: 75 (sol02)
- ET(71) + aggressive LNS (k=2-15): 75 (sol03)
- Randomized greedy + 1-opt restarts: 75 (sol04)
- 30+ restarts across all three solutions, all converge to exactly 75

The 75 ceiling is extremely robust. LNS with up to 15-element perturbations, 2-opt,
and diverse initial constructions all converge to the same local optimum. This is now
confirmed as a hard structural ceiling, not just a weak local minimum.

**Confidence reduced to 0.35** — superseded by algebraic constructions (105) with a
30-element gap. No further investment recommended unless combined with fundamentally
new ideas (e.g., SA from 75-element seed with longer time budget, or C implementation
for 2-opt).
