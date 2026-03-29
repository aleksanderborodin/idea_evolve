---
type: idea
id: idea_008
name: "Multi-seed restart with diverse initializations"
lifecycle: archived
confidence: 0.8
first_seen: generation_1
last_updated: generation_10
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_explore_1_sol07, gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_2_sol09, gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_001, idea_013]
cluster: cluster_001
tags: [multi-seed, restart, diversity, initialization, archived]
---

Run multiple optimization trajectories from different random seeds and/or initialization
shapes, keep best result. 4-8 seeds is sweet spot; diversity of shape matters more than
count. ~25% of seeds find the ~1.509 basin.

**ARCHIVED (gen 10 consistency review):** Stale since gen 3 (last_confirmed_gen=3,
3+5=8 <= 10). Only relevant to gradient-descent paradigm (random init). Current frontier
uses coordinate descent on a single published solution (idea_014 + idea_019) — multi-seed
restart is inapplicable. Factually correct but superseded.
