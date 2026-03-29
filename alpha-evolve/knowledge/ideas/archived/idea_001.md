---
type: idea
id: idea_001
name: "Gradient descent with JAX"
lifecycle: archived
confidence: 0.8
first_seen: generation_0
last_updated: generation_10
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_full_1_sol03, gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_005, idea_007]
cluster: cluster_001
tags: [optimization, gradient, adam, lion, archived]
---

Use JAX + optax for differentiable optimization of C constant. Baseline uses Adam with
cosine schedule. Gen 1 confirmed Adam as workhorse optimizer — all top-5 solutions use Adam.

**ARCHIVED (gen 10 consistency review):** Stale since gen 1 (last_confirmed_gen=1,
staleness threshold exceeded by 4 generations). Gradient descent caps at C~1.509 basin
(pattern_005). Current frontier at C~1.5029 uses coordinate descent on published solutions
(idea_019), not gradient descent. Factually correct but superseded — gradient descent is
only relevant for exploration from random initialization, which is no longer productive.
