---
type: idea
id: idea_002
name: "Higher resolution discretization"
lifecycle: disputed
confidence: 0.3
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: [gen001_full_1_sol04, gen001_explore_1_sol06, gen001_explore_1_sol01]
related_ideas: [idea_004]
cluster: cluster_002
tags: [resolution, discretization, N]
---

Increase the number of grid points N beyond the baseline 600. More points
give a finer representation of the function shape, potentially finding
better optima. Trade-off: slower computation per iteration.

**Gen 1 evidence is negative:**
- full_1/sol04 (N=800, same approach as best sol03): 1.5151 vs sol03's 1.5108 at N=600.
- explore_1/sol01 (N=800): 1.5207 vs baseline 1.5185.
- explore_1/sol06 upsampled to N=1500: 1.5183, not better.
- explore_2/sol08 (N=1000, Lion+Adam): 1.5207, same as N=800 result.

Higher N means slower steps and fewer iterations in fixed time, leading to
worse convergence. N=600 appears sufficient for the current score range.
Higher N may help when scores approach 1.503 and fine structure matters,
but it is counterproductive at the current optimization quality level.
