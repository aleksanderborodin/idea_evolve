---
type: idea
id: idea_008
name: "Multi-seed restart with diverse initializations"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_explore_1_sol07, gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_2_sol09, gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_001, idea_013]
cluster: cluster_001
tags: [multi-seed, restart, diversity, initialization]
---

Run multiple optimization trajectories from different random seeds and/or
different initialization shapes, then keep the best result. The problem
landscape has many local minima with meaningfully different C values.

**Evidence (gens 1-3):**
- Gen 1: 8 seeds is the sweet spot. 32 seeds didn't beat 8 seeds. Diversity
  of initialization shape matters more than count.
- Gen 2: 12 restarts at coarse scale (N=80) + warm fine → 1.5091 (best at time).
- Gen 3: 25-seed funnel showed arcsine inits dominate all top-5 coarse slots.
  exploit_1 found only 25% of seeds (1 of 4) reach the ~1.509 basin — more
  seeds increase reliability of finding this basin, not finding better ones.

**Key findings:**
- 4-8 seeds is the sweet spot for cost/benefit.
- Diversity of initialization shape matters more than number of seeds.
- Multi-seed combines multiplicatively with smooth-max.
- The ~1.509 basin is hard to find (25% hit rate) but once found, inescapable.
