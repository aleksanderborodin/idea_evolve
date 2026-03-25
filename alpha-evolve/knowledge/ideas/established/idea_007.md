---
type: idea
id: idea_007
name: "Basin hopping"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol11, gen001_explore_1_sol12]
contradicted_by: []
related_ideas: [idea_004, idea_001, idea_012]
cluster: cluster_001
tags: [basin-hopping, global-optimization, perturbation]
---

After reaching a local minimum via gradient descent, perturb the solution with random noise
and re-optimize. Repeat for multiple rounds, keeping the global best. This is a standard
global optimization technique applied to the function optimization landscape.

Gen 1 evidence: Basin hopping produced the two best solutions in the entire generation:
- explore_1/sol12 (10 rounds, aggressive): C = 1.5168 (BEST IN GEN 1)
- explore_1/sol11 (5 rounds, medium): C = 1.5168

Both start from a multi-scale Adam solution (N=600->2000), then apply multiple rounds of
noise + re-optimization. The noise levels vary (0.05-0.10 scale) and decrease across rounds.

Improvement over vanilla multi-scale: ~0.001 (from 1.5178 to 1.5168). This is meaningful
given the target gap of 0.013 below baseline. Basin hopping helps escape the local minimum
that standard gradient descent converges to.

The diminishing returns between 5 rounds (sol11) and 10 rounds (sol12) suggest the technique
is near its ceiling with current perturbation strategies.
