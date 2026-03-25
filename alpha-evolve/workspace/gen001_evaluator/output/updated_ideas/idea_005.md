---
type: idea
id: idea_005
name: "Regularization approaches"
lifecycle: disputed
confidence: 0.3
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: [gen001_explore_2_sol10, gen001_explore_1_sol13]
related_ideas: []
cluster: null
tags: [regularization, smoothness]
---

Add regularization terms (smoothness penalties, sparsity, symmetry enforcement) to the objective.

Gen 1 evidence is negative:
- TV regularization annealing (explore_2/sol10, C=1.5354) performed significantly worse than
  unregularized approaches (~1.517). The smoothness penalty appears to prevent the optimizer
  from finding the right function shape.
- L1-normalized optimization (explore_1/sol13, C=1.5203) also underperformed vanilla Adam.

The optimization landscape may not benefit from explicit regularization — the objective itself
(minimizing C) seems to provide sufficient implicit regularization toward smooth functions.
However, symmetry enforcement (a specific form of regularization) has theoretical support
(see idea_009) but was not properly tested in gen 1.
