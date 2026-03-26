---
type: idea
id: idea_007
name: "Graduated smooth-max (log-sum-exp temperature annealing)"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol02, gen002_exploit_1_sol01, gen003_explore_2_sol01, gen003_exploit_1_sol01, gen003_exploit_1_sol02]
contradicted_by: []
related_ideas: [idea_001, idea_005, idea_004]
cluster: cluster_001
tags: [smooth-max, log-sum-exp, temperature, annealing, gradient]
---

Replace jnp.max in the objective with a log-sum-exp soft maximum, annealing
the temperature from warm (T=0.05) to cold (T=0.0003) over training.

**Status:** Most impactful technique across all 3 generations. Confidence 0.95.
No solution has broken below 1.5155 without smooth-max. With it, 1.5090.

**Gen 3 confirmation:**
- exploit_1/sol01 (extended to T=0.00003): C improved from 1.5094 to 1.5093 — only 0.000025.
- exploit_1/sol02 (DCT perturbation + re-optimization): All 10 seeds converge to 1.5091.
- explore_2/sol01 (arcsine init + smooth-max): C=1.5090 — the technique remains essential.

**Temperature schedule finalized:** 5-phase [0.05, 0.01, 0.003, 0.001, 0.0003]
with 15k steps per phase is the proven optimum. Extended phases (T=0.0001,
T=0.00003) provide negligible benefit (gen 2 + gen 3 confirmation). Ultra-low
temperature polish is now a confirmed dead end.

**Important limitation:** Smooth-max + Adam can reach C~1.509 but appears to
have a hard floor there. The AlphaEvolve solution (C=1.5032) uses a fundamentally
different algorithm (LP-guided memetic), suggesting smooth-max gradient descent
cannot break below ~1.509 from random initialization.
