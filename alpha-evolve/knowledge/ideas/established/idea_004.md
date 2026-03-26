---
type: idea
id: idea_004
name: "Multi-scale optimization (coarse-to-fine)"
lifecycle: established
confidence: 0.75
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: [gen001_explore_1_sol02, gen001_explore_2_sol05, gen002_explore_1_sol01, gen003_explore_1_sol01, gen003_explore_1_sol02, gen003_explore_1_sol03]
related_ideas: [idea_002, idea_007, idea_013]
cluster: cluster_002
tags: [multi-scale, coarse-to-fine, upsampling]
---

Start with low resolution (small N), optimize, then upsample and refine at
higher resolution. Coarse optimization finds the right general shape; fine
optimization tunes it. The WARM fine stage (re-annealing from T=0.05 after
upsample) is essential — cold fine stage is a confirmed dead end.

**Promoted to established** based on gen 2-3 evidence across multiple agents.

**Gen 3 findings:**
- 2-stage (N=80->600) continues to work: explore_2/sol01 (arcsine init): C=1.5090.
- 3-stage (N=80->200->600) does NOT improve over 2-stage (explore_2/sol03: 1.5091).
- **SA at coarse scale FAILED** (explore_1): N=40 SA (1.5148), N=80 SA (1.5155), N=30 SA (1.5169). All worse than simple multi-seed coarse-to-fine without SA.

**SA failure analysis:**
- Metropolis temperature was poorly calibrated (acceptance 60-100%, not selective enough).
- sigma grew uncontrollably with raw_params magnitude.
- Warm inner optimizer (T=0.05) defeats SA purpose — converges back to same basin.
- A cold inner optimizer might work better for SA basin-hopping, but this has not been tested.
- N=40 is confirmed too coarse for quality upsampling to N=600.

**Optimal recipe:** N=80 coarse, warm smooth-max, upsample to N=600, warm fine
stage (T=0.05). 8-12 seeds. Best: C=1.5090-1.5091.

**Temperature schedule:** 5-phase [0.05, 0.01, 0.003, 0.001, 0.0003] at both
coarse and fine stages. Extended phases (T=0.0001, T=0.00003) confirmed
negligible benefit.
