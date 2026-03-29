---
type: idea
id: idea_002
name: "Higher resolution discretization"
lifecycle: debunked
confidence: 0.1
first_seen: generation_0
last_updated: generation_6
last_confirmed_gen: 0
supported_by: []
contradicted_by: [gen001_full_1_sol04, gen001_explore_1_sol06, gen001_explore_1_sol01, gen004_exploit_2_sol01]
related_ideas: [idea_004]
cluster: cluster_002
tags: [resolution, discretization, N, debunked]
---

Increase the number of grid points N beyond the baseline 600 for gradient descent.

**DEBUNKED after 6 generations of negative evidence.**

**Gen 1 evidence:**
- N=800 (full_1/sol04): 1.5151 vs N=600's 1.5108.
- N=800 (explore_1/sol01): 1.5207 vs baseline 1.5185.
- N=1000 (explore_2/sol08): 1.5207.
- N=1500 upsample (explore_1/sol06): 1.5183.

**Gen 4 evidence:**
- N=2000 upsample of 1.5032 array (exploit_2/sol01): 1.5159. Cubic spline destroyed
  sparse structure.

Higher N means slower steps, fewer iterations, and worse convergence for gradient-based
methods. N=600 is optimal for gradient descent.

**Note:** Higher N IS beneficial for LP-based methods (AlphaEvolve and TTT-Discover use
N=1319-30000), but that is a different optimization paradigm covered by idea_016/idea_018.
This idea specifically about gradient descent resolution is debunked.

Stale since gen 0 (never confirmed). Confidence lowered to 0.1.
