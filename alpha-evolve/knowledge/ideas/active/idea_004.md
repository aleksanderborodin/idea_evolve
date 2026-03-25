---
type: idea
id: idea_004
name: "Multi-scale optimization (coarse-to-fine)"
lifecycle: active
confidence: 0.65
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol02]
contradicted_by: [gen001_explore_1_sol02, gen001_explore_2_sol05, gen002_explore_1_sol01]
related_ideas: [idea_002, idea_007]
cluster: cluster_002
tags: [multi-scale, coarse-to-fine, upsampling]
---

Start with low resolution (small N), optimize, then upsample and refine at
higher resolution. Coarse optimization finds the right general shape;
fine optimization tunes it.

**Gen 1 evidence was strongly negative** (all cold fine stage):
- explore_1/sol02 (Hann init, N=200->600->1200): 1.5270.
- explore_2/sol05 (N=100->600->1200): 1.5730.
- explore_1/sol06 (16 seeds refined, upsample to N=1500): 1.5183.

**Gen 2 reversed the verdict** — the critical missing ingredient was a WARM
fine stage (restarting smooth-max at T=0.05 after upsampling):
- explore_1/sol03 (N=80→600, warm fine, 12 restarts): **C=1.5091** — NEW BEST.
- explore_1/sol02 (N=80→600, warm fine, 8 restarts): C=1.5093.
- explore_1/sol01 (N=40→150→600, COLD fine T=0.001): C=1.5188 — no improvement.

**Key insight:** Cold fine stage negates the coarse benefit entirely. The warm
fine stage re-anneals from the coarse basin, allowing further optimization.
N=80 is the minimum useful coarse resolution (N=40 was too small).

Promoted from disputed to active. Needs more evidence before established
(e.g., different coarse strategies, SA at coarse scale).
