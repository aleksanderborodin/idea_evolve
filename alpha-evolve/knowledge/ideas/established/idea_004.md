---
type: idea
id: idea_004
name: "Multi-scale optimization"
lifecycle: established
confidence: 0.9
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_explore_1_sol06, gen001_explore_1_sol08, gen001_explore_1_sol09, gen001_explore_1_sol11, gen001_explore_1_sol12]
contradicted_by: []
related_ideas: [idea_001, idea_002]
cluster: cluster_001
tags: [multi-scale, coarse-to-fine, resolution]
---

Start at low resolution (N=600), optimize, upsample via linear interpolation, then refine at
higher resolution (N=2000+). This is the single most impactful technique discovered in gen 1.

All 7 best solutions (C < 1.518) use this approach. The coarse phase finds the right general
shape quickly (40k steps at N=600), and the fine phase tunes it (50-80k steps at N=2000).

The standard pipeline: N=600 (40k steps, lr=0.005) -> upsample -> N=2000 (50-80k steps, lr=0.002).
Three-phase (adding N=4000) gives marginal improvement (explore_1/sol06, 1.5176 vs sol04's 1.5178).

This technique is now the baseline approach — future solutions should use it as a foundation
and layer additional techniques (basin hopping, multi-start, etc.) on top.
