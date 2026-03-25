---
type: idea
id: idea_001
name: "Gradient descent with JAX"
lifecycle: established
confidence: 0.8
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_full_1_sol03, gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_005, idea_007]
cluster: cluster_001
tags: [optimization, gradient, adam, lion]
---

Use JAX + optax for differentiable optimization of the C constant directly.
The baseline uses Adam with cosine schedule. Generation 1 confirmed that Adam
is the workhorse optimizer: all top-5 solutions use Adam (some with Lion warmup).

Key findings from gen 1:
- Adam alone with 40k steps converges to C ~ 1.5185 (baseline basin).
- Longer runs (80k steps) give marginal improvement (1.5182).
- Lion optimizer as warmup before Adam (explore_2/sol09) matches baseline at 1.5182.
- The real gains come from combining Adam with other ideas (smooth-max, multi-seed).
- L-BFGS-B alone performs poorly (full_1/sol02: 1.6887) due to non-smooth landscape,
  but works well as a fine-tuning step after Adam (explore_1/sol05: 1.5155).
