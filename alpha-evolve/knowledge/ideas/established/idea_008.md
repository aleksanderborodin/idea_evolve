---
type: idea
id: idea_008
name: "Multi-seed restart with diverse initializations"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol05, gen001_explore_1_sol07, gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_003, idea_001]
cluster: cluster_001
tags: [multi-seed, restart, diversity, initialization]
---

Run multiple optimization trajectories from different random seeds and/or
different initialization shapes, then keep the best result. The problem
landscape has many local minima with meaningfully different C values.

**Evidence:**
- explore_1/sol05 (8 shifted-support seeds): C = 1.5155 vs baseline 1.5185.
  The 0.003 improvement from multi-seed alone is significant given the
  total target improvement is only 0.013.
- explore_1/sol07 (32 seeds, 16 diverse modes): C = 1.5157 — similar.
- full_1/sol03 (8 seeds with smooth-max): C = 1.5108 — best result.
- full_1/sol04 (12 seeds): C = 1.5151.
- explore_2/sol09 (4 seeds, Lion+Adam): C = 1.5182.

**Key findings:**
- 4-8 seeds is the sweet spot for cost/benefit in gen 1.
- 32 seeds (explore_1/sol07) didn't beat 8 seeds (explore_1/sol05) — diminishing
  returns; the bottleneck shifts to per-seed optimization quality.
- Diversity of initialization shape matters more than number of seeds.
  Shifted support blocks, random Gaussian bumps, and ramps all contribute.
- Multi-seed combines multiplicatively with smooth-max: sol03 (8 seeds + smooth-max)
  achieved 1.5108, while sol05 (8 seeds, no smooth-max) achieved 1.5155.
