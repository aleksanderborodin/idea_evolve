---
type: idea
id: idea_007
name: "Graduated smooth-max (log-sum-exp temperature annealing)"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_9
last_confirmed_gen: 6
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol02, gen002_exploit_1_sol01, gen003_explore_2_sol01, gen003_exploit_1_sol01, gen003_exploit_1_sol02]
contradicted_by: [gen006_exploit_2_sol01]
related_ideas: [idea_001, idea_005, idea_004]
cluster: cluster_001
tags: [smooth-max, log-sum-exp, temperature, annealing, gradient]
---

Replace jnp.max in the objective with a log-sum-exp soft maximum, annealing
the temperature from warm (T=0.05) to cold (T=0.0003) over training.

**Status:** Most impactful technique for gradient descent from random init. Confidence 0.95.
No solution has broken below 1.5155 without smooth-max. With it, 1.5090.

**Temperature schedule finalized:** 5-phase [0.05, 0.01, 0.003, 0.001, 0.0003]
with 15k steps per phase is the proven optimum. Extended phases provide negligible benefit.

**Gen 6 confirmation of limitations (exploit_2):**
- Smooth-max Adam tested on AlphaEvolve Cell 49 (N=600, C=1.5040) with float64 accept/reject.
- ALL 6 temperature phases rejected. T=0.005: C→1.5414. T=0.0001: C→1.5057.
- Even the coldest temperature makes things worse by +1.72e-03.
- The smooth-max approximation error at ANY useful temperature pushes the optimizer
  away from the true minimum of well-optimized solutions.
- This confirms pattern_007 with float64 rigor: smooth-max Adam is fundamentally unable
  to improve published solutions, regardless of precision.

**Gen 9 consistency review:** Updated last_confirmed_gen from 3 to 6. Gen 6 exploit_2
tested this idea with float64 rigor, confirming both its effectiveness for random init
and its limitations for published solutions.

**Important:** This technique remains essential for gradient descent from random init
(the ONLY way to reach C~1.509 basin) but is useless for optimization below C~1.505.
