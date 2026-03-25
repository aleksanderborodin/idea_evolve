---
type: idea
id: idea_002
name: "Higher resolution discretization"
lifecycle: established
confidence: 0.7
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol04, gen001_explore_1_sol06]
contradicted_by: []
related_ideas: [idea_004]
cluster: cluster_001
tags: [resolution, discretization]
---

Higher resolution (N=2000-4000) improves scores vs N=600, but ONLY when combined with
multi-scale optimization (idea_004). Simply starting at high resolution doesn't help because
the optimizer has more parameters to navigate.

Evidence: explore_1/sol04 (N=600->2000, C=1.5178) beats explore_1/sol03 (N=600 only, C=1.5257).
explore_1/sol06 goes to N=4000 and gets C=1.5176, a marginal further improvement.
explore_2/sol08-09 used N=1000-1200 without multi-scale upsampling and scored 1.5179-1.5207,
comparable to but not better than multi-scale approaches.

The sweet spot appears to be N=2000 for the fine phase. N=4000 provides diminishing returns
(~0.0002 improvement) at significantly higher computation cost.
